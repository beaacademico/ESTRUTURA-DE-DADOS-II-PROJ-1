# -*- coding: utf-8 -*-
"""
Servidor de Monitoramento e Predição de Degradação de Redes — CypherNet: Vigia de Redes (Grupo 05).

Integra:
- Módulo único de engenharia de atributos (src.cyphernet.features) com paridade de 100% com o treino
- Modelo Principal: Árvore de Decisão (Profundidade 7) empacotada em modelo_final.joblib
- Duplo Horizonte de Inferência:
    * T=0 (Diagnóstico Instantâneo em Tempo Real — 8 features base)
    * T+1 (Previsão Proativa +4 min à frente — 11 features expandidas)
    * H3  (Alerta Antecipado +12 min à frente — 11 features expandidas)
- Endpoints compatíveis com o Dashboard NOC (/api/diagnosticar, /api/fluxos, /api/coletar_ripe_ao_vivo),
  com a página da Mostra (/feira/index.html) e com o Contrato OpenAPI do Edital
  (GET /api/saude, GET /api/modelo, POST /api/previsoes, GET /api/previsoes).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from collections import deque
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
import requests
from flask import Flask, jsonify, render_template, request

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCAO_DIR = os.path.dirname(APP_DIR)
REPO_ROOT = os.path.dirname(PRODUCAO_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.cyphernet.features import (
    CLASSES,
    FEATURES,
    FEATURES_BASE,
    JanelaFluxo,
    ausente,
    processar_medicao,
    vetor,
)

app = Flask(__name__)


@app.after_request
def adicionar_cabecalhos_cors(response):
    """Permite integração direta com a página estática feira/index.html."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response


BASELINE_PATH = os.path.join(PRODUCAO_DIR, "modelo", "baseline.csv")
if not os.path.exists(BASELINE_PATH):
    BASELINE_PATH = os.path.join(REPO_ROOT, "data", "processed", "baseline_por_fluxo.csv")

MODEL_PATH = os.path.join(PRODUCAO_DIR, "modelo", "modelo_final.joblib")
METADATA_PATH = os.path.join(PRODUCAO_DIR, "modelo", "metadados.json")

print("=" * 72)
print(" CYPHERNET: VIGIA DE REDES — INICIALIZANDO SERVIDOR NOC MLOps")
print("=" * 72)

# 1. Rastreabilidade Criptográfica (SHA-256)
print(f"1. Calculando SHA-256 do pacote serializado em: {MODEL_PATH}")
sha256_hash = hashlib.sha256()
with open(MODEL_PATH, "rb") as f:
    for byte_block in iter(lambda: f.read(65536), b""):
        sha256_hash.update(byte_block)
MODELO_SHA256 = sha256_hash.hexdigest()
print(f"   -> SHA-256: {MODELO_SHA256}")

# 2. Carga da Baseline Histórica
print(f"2. Carregando baseline histórica de: {BASELINE_PATH}")
df_baseline = pd.read_csv(BASELINE_PATH)
baselines = df_baseline.set_index("fluxo_id").to_dict("index")

# 3. Carga do Pacote de Modelos (Árvore de Decisão T=0 + Proativos T+1 e H3)
print("3. Carregando pacote modelo_final.joblib (Árvore de Decisão Canônica)...")
pacote_carregado = joblib.load(MODEL_PATH)

if isinstance(pacote_carregado, dict) and "modelo" in pacote_carregado:
    modelo_t0 = pacote_carregado["modelo"]
    features_t0 = list(pacote_carregado.get("features", FEATURES_BASE))
    familia_modelo = pacote_carregado.get("familia", "arvore_decisao")
    params_modelo = pacote_carregado.get("params", {})
    modelo_t1 = pacote_carregado.get("modelo_proativo_t1")
    modelo_h3 = pacote_carregado.get("modelo_proativo_h3")
    features_proativas = list(pacote_carregado.get("features_proativas", FEATURES))
else:
    modelo_t0 = pacote_carregado
    features_t0 = list(FEATURES_BASE)
    familia_modelo = "arvore_decisao"
    params_modelo = modelo_t0.get_params() if hasattr(modelo_t0, "get_params") else {}
    modelo_t1 = None
    modelo_h3 = None
    features_proativas = list(FEATURES)

metadados_arquivo = {}
if os.path.exists(METADATA_PATH):
    with open(METADATA_PATH, "r", encoding="utf-8") as fm:
        metadados_arquivo = json.load(fm)

classes_map = {0: "OK", 1: "RISCO", 2: "FALHA"}

# Memória curta por fluxo (JanelaFluxo de 5 medições) e histórico de predições da API
janelas_por_fluxo: dict[str, JanelaFluxo] = {}
historico_previsoes: deque = deque(maxlen=500)
START_TIME = time.time()


def _fmt_json_num(val, casas: int = 2):
    """Formata float para exibição segura em JSON sem mascarar NaN como zero."""
    if ausente(val):
        return "NaN"
    return round(float(val), casas)


def _fmt_nullable_float(val, casas: int = 4):
    """Retorna None se NaN, ou float arredondado."""
    if ausente(val):
        return None
    return round(float(val), casas)


def diagnosticar_medicao(
    probe_id,
    dst_addr: str,
    rtt_ms,
    perda_pct: float,
    jitter_ms,
    ruido_pct: float = 0.0,
    timestamp_medicao: int | None = None,
) -> dict:
    fluxo_id = f"{int(probe_id)}|{dst_addr}"
    if fluxo_id not in baselines:
        return {"erro": f"Fluxo {fluxo_id} não possui baseline histórica cadastrada."}

    base = baselines[fluxo_id]
    mediana = float(base["mediana"])
    mad = float(base["MAD"])
    jitter_tipico = float(base["jitter_tipico"])

    perda_val = float(perda_pct) if not ausente(perda_pct) else 0.0
    is_timeout = perda_val >= 100.0 or ausente(rtt_ms)

    rtt_efetivo = None if is_timeout else float(rtt_ms)
    jitter_efetivo = None if (is_timeout or ausente(jitter_ms)) else float(jitter_ms)

    # Injeção opcional de ruído estocástico (simulador de Data Drift no painel)
    if ruido_pct > 0.0 and rtt_efetivo is not None:
        escala_mad = mad if mad > 0 else 1.0
        escala_jit = jitter_tipico if jitter_tipico > 0 else 0.5
        rtt_efetivo = max(0.1, rtt_efetivo + float(np.random.normal(0, (ruido_pct / 100.0) * escala_mad)))
        if jitter_efetivo is not None:
            jitter_efetivo = max(0.0, jitter_efetivo + float(np.random.normal(0, (ruido_pct / 100.0) * escala_jit)))

    if fluxo_id not in janelas_por_fluxo:
        janelas_por_fluxo[fluxo_id] = JanelaFluxo()

    janela = janelas_por_fluxo[fluxo_id]
    feats = processar_medicao(
        {"rtt_ms": rtt_efetivo, "perda_pct": perda_val, "jitter_ms": jitter_efetivo},
        base,
        janela,
    )

    # 1. Inferência Principal T=0 (Diagnóstico Instantâneo)
    X_t0 = vetor(feats, ordem=features_t0)
    t0_clock = time.perf_counter()
    probs_t0 = modelo_t0.predict_proba(X_t0)[0]
    latencia_inferencia_ms = (time.perf_counter() - t0_clock) * 1000.0

    pred_idx_t0 = int(np.argmax(probs_t0))
    classe_pred_t0 = classes_map[pred_idx_t0]

    # 2. Inferência Proativa T+1 (+4 min) e H3 (+12 min)
    predicao_proativa_t1 = None
    if modelo_t1 is not None:
        X_t1 = vetor(feats, ordem=features_proativas)
        probs_t1 = modelo_t1.predict_proba(X_t1)[0]
        idx_t1 = int(np.argmax(probs_t1))
        predicao_proativa_t1 = {
            "horizonte": "T+1 (+4 min)",
            "classe": classes_map[idx_t1],
            "confianca_pct": round(float(probs_t1[idx_t1]) * 100.0, 1),
            "probabilidades": {
                "OK": round(float(probs_t1[0]) * 100.0, 1),
                "RISCO": round(float(probs_t1[1]) * 100.0, 1),
                "FALHA": round(float(probs_t1[2]) * 100.0, 1),
            },
        }

    predicao_alerta_h3 = None
    if modelo_h3 is not None:
        X_h3 = vetor(feats, ordem=features_proativas)
        probs_h3 = modelo_h3.predict_proba(X_h3)[0]
        idx_h3 = int(np.argmax(probs_h3))
        predicao_alerta_h3 = {
            "horizonte": "T+1..T+3 (+12 min)",
            "classe": classes_map[idx_h3],
            "confianca_pct": round(float(probs_h3[idx_h3]) * 100.0, 1),
            "probabilidades": {
                "OK": round(float(probs_h3[0]) * 100.0, 1),
                "RISCO": round(float(probs_h3[1]) * 100.0, 1),
                "FALHA": round(float(probs_h3[2]) * 100.0, 1),
            },
        }

    ts_iso = (
        datetime.fromtimestamp(timestamp_medicao, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if timestamp_medicao
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    resposta = {
        "timestamp_utc": ts_iso,
        "fluxo_id": fluxo_id,
        "probe_id": int(probe_id),
        "dst_addr": dst_addr,
        "rtt_ms": "TIMEOUT" if rtt_efetivo is None else round(rtt_efetivo, 2),
        "mediana": round(mediana, 2),
        "mad": round(mad, 4),
        "z_robusto": _fmt_json_num(feats["z_robusto"], 2),
        "aumento_pct": _fmt_json_num(feats["aumento_pct"], 1),
        "jitter_relativo": _fmt_json_num(feats["jitter_relativo"], 2),
        "perda_pct": round(perda_val, 1),
        "timeout_atual": int(feats["timeout_atual"]),
        "n5_timeout": int(feats["n5_timeout"]),
        "n5_risco": int(feats["n5_risco"]),
        "n5_aumento80": int(feats["n5_aumento80"]),
        "z_max5": _fmt_nullable_float(feats["z_max5"], 3),
        "z_tendencia5": _fmt_nullable_float(feats["z_tendencia5"], 3),
        "perda_media5": _fmt_nullable_float(feats["perda_media5"], 2),
        "amostras_na_janela": len(janela),
        "classe": classe_pred_t0,
        "classe_regra_heuristica": feats["classe_atual_regra"],
        "confianca_pct": round(float(probs_t0[pred_idx_t0]) * 100.0, 1),
        "probabilidades": {
            "OK": round(float(probs_t0[0]) * 100.0, 1),
            "RISCO": round(float(probs_t0[1]) * 100.0, 1),
            "FALHA": round(float(probs_t0[2]) * 100.0, 1),
        },
        "predicao_proativa_t1": predicao_proativa_t1,
        "predicao_alerta_h3": predicao_alerta_h3,
        "familia_modelo": familia_modelo,
        "modelo_sha256": MODELO_SHA256,
        "latencia_ms": round(latencia_inferencia_ms, 3),
    }

    historico_previsoes.appendleft(resposta)
    return resposta


# =================== ROTAS DA APLICAÇÃO ===================


@app.route("/")
def index():
    return render_template(
        "index.html",
        total_fluxos=len(baselines),
        modelo_sha256=MODELO_SHA256,
    )


@app.route("/api/saude", methods=["GET"])
def api_saude():
    """Liveness probe / Healthcheck padrão Cloud Native e especificação OpenAPI."""
    return jsonify(
        {
            "status": "ok",
            "api": "ok",
            "modelo": "ok",
            "projeto": "CypherNet: Vigia de Redes",
            "grupo": "Grupo 05",
            "familia_modelo": familia_modelo,
            "modelo_sha256": MODELO_SHA256,
            "uptime_segundos": round(time.time() - START_TIME, 1),
            "total_fluxos_cadastrados": len(baselines),
            "historico_previsoes_em_memoria": len(historico_previsoes),
        }
    )


@app.route("/api/modelo", methods=["GET"])
def api_modelo():
    """Metadados de auditoria, governança e métricas do modelo carregado."""
    return jsonify(
        {
            "projeto": "CypherNet: Vigia de Redes",
            "nome": "CypherNet DecisionTree Classifier (Profundidade 7)",
            "familia": familia_modelo,
            "formato": "joblib (dicionário canônico)",
            "sha256": MODELO_SHA256,
            "tamanho_disco_kb": round(os.path.getsize(MODEL_PATH) / 1024, 1),
            "classes": list(CLASSES),
            "atributos_entrada_t0": features_t0,
            "atributos_entrada_proativo_t1": features_proativas,
            "parametros": params_modelo,
            "suporte_proativo_t1": modelo_t1 is not None,
            "suporte_alerta_h3": modelo_h3 is not None,
            "metadados_completos": metadados_arquivo.get("1_identificacao_modelo", {}),
        }
    )


@app.route("/api/fluxos", methods=["GET"])
def get_fluxos():
    lista = []
    for f_id, data in baselines.items():
        parts = f_id.split("|")
        lista.append(
            {
                "fluxo_id": f_id,
                "probe_id": parts[0],
                "dst_addr": parts[1],
                "mediana": round(float(data["mediana"]), 2),
                "mad": round(float(data["MAD"]), 4),
                "jitter_tipico": round(float(data.get("jitter_tipico", 0.1)), 4),
                "prop_resposta": round(float(data.get("prop_resposta", 1.0)), 4),
                "baseline_valida": bool(data.get("baseline_valida", True)),
            }
        )
    return jsonify(lista)


@app.route("/api/diagnosticar", methods=["POST"])
def api_diagnosticar():
    dados = request.get_json(silent=True) or {}
    probe_id = dados.get("probe_id")
    dst_addr = dados.get("dst_addr")
    if probe_id is None or not dst_addr:
        return jsonify({"erro": "Campos 'probe_id' e 'dst_addr' são obrigatórios."}), 400

    rtt_raw = dados.get("rtt_ms", 30.0)
    rtt_ms = None if rtt_raw is None else float(rtt_raw)
    perda_pct = float(dados.get("perda_pct", 0.0))
    jitter_raw = dados.get("jitter_ms", 1.0)
    jitter_ms = None if jitter_raw is None else float(jitter_raw)
    ruido_pct = float(dados.get("ruido_pct", 0.0))

    resultado = diagnosticar_medicao(probe_id, dst_addr, rtt_ms, perda_pct, jitter_ms, ruido_pct)
    if "erro" in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)


@app.route("/api/previsoes", methods=["POST", "GET"])
def api_previsoes():
    """
    Endpoint canônico exigido pelo contrato OpenAPI do Edital Final:
    - POST /api/previsoes: recebe uma medição (ou lista de medições em 'medicoes') e retorna a predição.
    - GET /api/previsoes: retorna o histórico recente de previsões realizadas pela API.
    """
    if request.method == "GET":
        fluxo_filtro = request.args.get("fluxo_id")
        limite = int(request.args.get("limit", 50))
        itens = list(historico_previsoes)
        if fluxo_filtro:
            itens = [x for x in itens if x.get("fluxo_id") == fluxo_filtro]
        return jsonify(
            {
                "total_historico": len(itens),
                "limite_aplicado": limite,
                "previsoes": itens[:limite],
            }
        )

    dados = request.get_json(silent=True) or {}
    lista_entrada = dados.get("medicoes") if isinstance(dados.get("medicoes"), list) else [dados]

    resultados = []
    for item in lista_entrada:
        fluxo_id = item.get("fluxo_id")
        probe_id = item.get("probe_id") or item.get("prb_id")
        dst_addr = item.get("dst_addr")
        if fluxo_id and (probe_id is None or not dst_addr) and "|" in str(fluxo_id):
            p_str, d_str = str(fluxo_id).split("|", 1)
            probe_id = int(p_str)
            dst_addr = d_str

        if probe_id is None or not dst_addr:
            return jsonify({"erro": "Informe 'fluxo_id' (probe|dst) ou 'probe_id' + 'dst_addr'."}), 400

        # Aceita tanto rtt_ms/perda_pct/jitter_ms quanto formato bruto RIPE Atlas (avg, min, max, sent, rcvd)
        sent = item.get("sent")
        rcvd = item.get("rcvd")
        if "perda_pct" in item and item["perda_pct"] is not None:
            perda_pct = float(item["perda_pct"])
        elif sent is not None and rcvd is not None and float(sent) > 0:
            perda_pct = ((float(sent) - float(rcvd)) / float(sent)) * 100.0
        else:
            perda_pct = 0.0

        rtt_raw = item.get("rtt_ms", item.get("avg"))
        rtt_ms = None if rtt_raw is None else float(rtt_raw)

        if "jitter_ms" in item and item["jitter_ms"] is not None:
            jitter_ms = float(item["jitter_ms"])
        elif item.get("max") is not None and item.get("min") is not None:
            jitter_ms = max(0.0, float(item["max"]) - float(item["min"]))
        else:
            jitter_ms = None if rtt_ms is None else 0.1

        diag = diagnosticar_medicao(
            probe_id,
            dst_addr,
            rtt_ms,
            perda_pct,
            jitter_ms,
            timestamp_medicao=item.get("timestamp"),
        )
        if "erro" in diag:
            return jsonify(diag), 404
        resultados.append(diag)

    if len(resultados) == 1 and "medicoes" not in dados:
        return jsonify(resultados[0]), 200
    return jsonify({"total_processado": len(resultados), "previsoes": resultados}), 200


@app.route("/api/coletar_ripe_ao_vivo", methods=["POST"])
def api_coletar_ripe():
    msm_id = 9333345
    now = int(time.time())
    start = now - 3600
    url = f"https://atlas.ripe.net/api/v2/measurements/{msm_id}/results/?start={start}&stop={now}&format=json"

    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            return jsonify({"erro": f"RIPE API retornou código {r.status_code}"}), 502
        raw_data = r.json()
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

    resultados = []
    for item in raw_data:
        prb_id = item.get("prb_id")
        dst_addr = item.get("dst_addr")
        fluxo_id = f"{prb_id}|{dst_addr}"
        if fluxo_id in baselines and len(resultados) < 25:
            sent = item.get("sent", 3)
            rcvd = item.get("rcvd", 0)
            perda = ((sent - rcvd) / sent) * 100.0 if sent > 0 else 100.0
            rtt = item.get("avg")
            rtt_min = item.get("min")
            rtt_max = item.get("max")
            jitter = (
                max(0.0, float(rtt_max) - float(rtt_min))
                if (rcvd > 0 and rtt_max is not None and rtt_min is not None)
                else None
            )
            diag = diagnosticar_medicao(
                prb_id,
                dst_addr,
                rtt,
                perda,
                jitter,
                timestamp_medicao=item.get("timestamp"),
            )
            if diag and "erro" not in diag:
                resultados.append(diag)

    return jsonify(
        {
            "total_recebido": len(raw_data),
            "total_mapeado": len(resultados),
            "diagnosticos": resultados,
        }
    )


if __name__ == "__main__":
    print("Servidor CypherNet NOC MLOps rodando em http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False)
