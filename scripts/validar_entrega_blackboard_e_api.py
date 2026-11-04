# -*- coding: utf-8 -*-
"""
Validador End-to-End do Pacote Canônico Blackboard (Grupo05.zip) e da API REST (server.py).

Executa:
1. Refinamento leve do pacote (removendo ensembles pesados de dentro de modelo.joblib para
   deixá-lo enxuto com as Árvores de Decisão T=0, T+1 e H3, e ajustando o período exato da
   janela de baseline 06/09/2026 a 13/09/2026).
2. Teste de descompactação isolada de Grupo05.zip (verifica modelo.joblib, metadados.json e baseline.csv).
3. Teste automatizado de todos os endpoints da API Flask via test_client():
   - GET /
   - GET /api/saude
   - GET /api/modelo
   - GET /api/fluxos
   - POST /api/diagnosticar (Cenários: OK, RISCO persistente e FALHA por Timeout 100% com preservação de NaN)
   - POST /api/previsoes (Contrato OpenAPI do Edital — individual e em lote)
   - GET /api/previsoes (Histórico de predições)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile

import joblib
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def calcular_sha256(caminho: str) -> str:
    sha = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            sha.update(bloco)
    return sha.hexdigest()


def main():
    print("=" * 78)
    print(" AUDITORIA E VALIDAÇÃO END-TO-END: PACOTE BLACKBOARD + API CYPHERNET")
    print("=" * 78)

    dist_dir = os.path.join(REPO_ROOT, "dist", "Grupo05")
    prod_model_dir = os.path.join(REPO_ROOT, "producao", "modelo")
    caminho_modelo_dist = os.path.join(dist_dir, "modelo.joblib")
    caminho_modelo_prod = os.path.join(prod_model_dir, "modelo_final.joblib")
    caminho_meta_dist = os.path.join(dist_dir, "metadados.json")
    caminho_meta_prod = os.path.join(prod_model_dir, "metadados.json")
    caminho_base_dist = os.path.join(dist_dir, "baseline.csv")
    caminho_base_prod = os.path.join(prod_model_dir, "baseline.csv")

    # 1. Deixar modelo.joblib enxuto (apenas Árvores de Decisão T=0, T+1 e H3)
    pacote = joblib.load(caminho_modelo_dist)
    chaves_manter = [
        "modelo",
        "features",
        "familia",
        "params",
        "classes",
        "classes_map",
        "horizonte_principal",
        "modelo_proativo_t1",
        "modelo_proativo_h3",
        "features_proativas",
    ]
    pacote_enxuto = {k: pacote[k] for k in chaves_manter if k in pacote}
    joblib.dump(pacote_enxuto, caminho_modelo_dist)
    joblib.dump(pacote_enxuto, caminho_modelo_prod)

    # Ajustar datas da janela de baseline (primeiros 7 dias: 06/09/2026 a 13/09/2026)
    df_base = pd.read_csv(caminho_base_dist)
    df_base["periodo_calculo_inicio"] = "2026-09-06T07:32:31Z"
    df_base["periodo_calculo_fim"] = "2026-09-13T07:32:31Z"
    df_base["amostras_janela_baseline"] = (df_base["prop_resposta"] * 2520).round().astype(int)
    df_base["baseline_valida"] = (
        (df_base["amostras_janela_baseline"] >= 1500)
        & (df_base["prop_resposta"] >= 0.70)
        & (df_base["mediana"] > 0)
    )
    df_base.to_csv(caminho_base_dist, index=False, encoding="utf-8")
    df_base.to_csv(caminho_base_prod, index=False, encoding="utf-8")

    sha_modelo = calcular_sha256(caminho_modelo_dist)
    sha_base = calcular_sha256(caminho_base_dist)

    with open(caminho_meta_dist, "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["1_identificacao_modelo"]["sha256_modelo_joblib"] = sha_modelo
    meta["1_identificacao_modelo"]["sha256_baseline_csv"] = sha_base
    meta["9_regras_uso_baseline"]["periodo_referencia_calculo"] = {
        "inicio_utc": "2026-09-06T07:32:31Z",
        "fim_utc": "2026-09-13T07:32:31Z",
        "duracao_dias": 7,
    }
    meta["9_regras_uso_baseline"]["criterios_validade_fluxo"]["fluxos_validos_no_arquivo"] = int(
        df_base["baseline_valida"].sum()
    )

    with open(caminho_meta_dist, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    with open(caminho_meta_prod, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # Recriar Grupo05.zip
    zip_path_dist = os.path.join(REPO_ROOT, "dist", "Grupo05.zip")
    zip_path_downloads = os.path.join(os.path.dirname(os.path.dirname(REPO_ROOT)), "Grupo05.zip")
    with zipfile.ZipFile(zip_path_dist, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ["modelo.joblib", "metadados.json", "baseline.csv"]:
            zf.write(os.path.join(dist_dir, fname), arcname=fname)
    shutil.copy2(zip_path_dist, zip_path_downloads)

    tam_modelo_kb = os.path.getsize(caminho_modelo_dist) / 1024.0
    tam_zip_kb = os.path.getsize(zip_path_dist) / 1024.0
    print(f"[1/3] Pacote enxuto atualizado:")
    print(f"      - modelo.joblib: {tam_modelo_kb:.1f} KB (SHA-256: {sha_modelo[:16]}...)")
    print(f"      - Grupo05.zip  : {tam_zip_kb:.1f} KB (copiado para {zip_path_downloads})")

    # 2. Testar descompactação e carga isolada do ZIP
    print("\n[2/3] Testando descompactação e inferência standalone a partir de Grupo05.zip...")
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path_dist, "r") as zf:
            nomes = zf.namelist()
            assert set(nomes) == {"modelo.joblib", "metadados.json", "baseline.csv"}, f"Arquivos inesperados: {nomes}"
            zf.extractall(tmpdir)

        pkg = joblib.load(os.path.join(tmpdir, "modelo.joblib"))
        assert isinstance(pkg, dict), "modelo.joblib deve ser um dict"
        for k_req in ["modelo", "features", "familia", "params"]:
            assert k_req in pkg, f"Chave obrigatória '{k_req}' ausente em modelo.joblib"

        with open(os.path.join(tmpdir, "metadados.json"), "r", encoding="utf-8") as fm:
            meta_loaded = json.load(fm)
        df_b_loaded = pd.read_csv(os.path.join(tmpdir, "baseline.csv"))
        assert len(df_b_loaded) == 69, "baseline.csv deve conter 69 fluxos"

        # Testar predição com NaN nativo (simulando timeout ICMP)
        X_nan = pd.DataFrame([{
            "z_robusto": np.nan,
            "aumento_pct": np.nan,
            "jitter_relativo": np.nan,
            "perda_pct": 100.0,
            "timeout_atual": 1.0,
            "n5_timeout": 3.0,
            "n5_aumento80": 0.0,
            "n5_risco": 0.0,
        }])[pkg["features"]]
        pred_nan = int(pkg["modelo"].predict(X_nan)[0])
        assert pred_nan == 2, f"Timeout severo deve ser classificado como FALHA (2), obtido: {pred_nan}"
        print("      -> [OK] Extração isolada e predição standalone (incluindo NaN nativo) validadas!")

    # 3. Testar todos os endpoints da API Flask
    print("\n[3/3] Testando endpoints REST da API Flask (producao/app/server.py)...")
    from producao.app.server import app

    client = app.test_client()

    r_root = client.get("/")
    assert r_root.status_code == 200, "GET / falhou"

    r_saude = client.get("/api/saude")
    assert r_saude.status_code == 200
    js_saude = r_saude.get_json()
    assert js_saude["status"] == "ok" and js_saude["total_fluxos_cadastrados"] == 69
    print(f"      -> [OK] GET /api/saude: status={js_saude['status']} | fluxos={js_saude['total_fluxos_cadastrados']}")

    r_mod = client.get("/api/modelo")
    assert r_mod.status_code == 200
    js_mod = r_mod.get_json()
    assert js_mod["familia"] == "arvore_decisao" and js_mod["suporte_proativo_t1"] is True
    print(f"      -> [OK] GET /api/modelo: {js_mod['nome']} ({js_mod['tamanho_disco_kb']} KB)")

    r_flx = client.get("/api/fluxos")
    assert r_flx.status_code == 200
    js_flx = r_flx.get_json()
    assert len(js_flx) == 69
    print(f"      -> [OK] GET /api/fluxos: {len(js_flx)} fluxos retornados")

    # Teste de diagnóstico normal (OK)
    r_diag_ok = client.post(
        "/api/diagnosticar",
        json={"probe_id": 6251, "dst_addr": "193.0.0.164", "rtt_ms": 28.25, "perda_pct": 0.0, "jitter_ms": 0.18},
    )
    assert r_diag_ok.status_code == 200
    js_ok = r_diag_ok.get_json()
    assert js_ok["classe"] == "OK"
    print(
        f"      -> [OK] POST /api/diagnosticar (Normal): T=0={js_ok['classe']} | "
        f"T+1={js_ok['predicao_proativa_t1']['classe']} ({js_ok['latencia_ms']} ms)"
    )

    # Teste de diagnóstico de RISCO persistente (2 medições com 2.0 <= z_robusto < 3.5)
    for _ in range(2):
        r_diag_risco = client.post(
            "/api/diagnosticar",
            json={"probe_id": 6251, "dst_addr": "193.0.0.164", "rtt_ms": 28.85, "perda_pct": 0.0, "jitter_ms": 0.30},
        )
    js_risco = r_diag_risco.get_json()
    assert js_risco["classe"] == "RISCO", f"Esperado RISCO, obtido: {js_risco}"
    print(
        f"      -> [OK] POST /api/diagnosticar (Degradação Persistente): T=0={js_risco['classe']} | "
        f"T+1={js_risco['predicao_proativa_t1']['classe']} | z_robusto={js_risco['z_robusto']}"
    )

    # Teste de Timeout (100% perda) verificando preservação de NaN
    r_diag_to = client.post(
        "/api/diagnosticar",
        json={"probe_id": 6251, "dst_addr": "193.0.0.164", "rtt_ms": None, "perda_pct": 100.0, "jitter_ms": None},
    )
    js_to = r_diag_to.get_json()
    assert js_to["classe"] == "FALHA" and js_to["z_robusto"] == "NaN" and js_to["timeout_atual"] == 1
    print(
        f"      -> [OK] POST /api/diagnosticar (Timeout 100%): T=0={js_to['classe']} | "
        f"z_robusto={js_to['z_robusto']} | timeout_atual={js_to['timeout_atual']}"
    )

    # Teste do endpoint canônico do Edital: POST /api/previsoes e GET /api/previsoes
    r_prev_post = client.post(
        "/api/previsoes",
        json={
            "medicoes": [
                {"fluxo_id": "6313|193.0.0.164", "avg": 6.55, "min": 6.50, "max": 6.60, "sent": 3, "rcvd": 3},
                {"fluxo_id": "6313|193.0.0.164", "avg": 18.0, "min": 15.0, "max": 22.0, "sent": 3, "rcvd": 2},
            ]
        },
    )
    assert r_prev_post.status_code == 200
    js_prev_post = r_prev_post.get_json()
    assert js_prev_post["total_processado"] == 2
    print(f"      -> [OK] POST /api/previsoes (Lote RIPE bruto): {js_prev_post['total_processado']} medições processadas")

    r_prev_get = client.get("/api/previsoes?limit=5")
    assert r_prev_get.status_code == 200
    js_prev_get = r_prev_get.get_json()
    assert len(js_prev_get["previsoes"]) == 5
    print(f"      -> [OK] GET /api/previsoes: {js_prev_get['total_historico']} registros no histórico da API")

    print("=" * 78)
    print(" TODOS OS TESTES PASSARAM COM 100% DE CONFORMIDADE!")
    print("=" * 78)


if __name__ == "__main__":
    main()
