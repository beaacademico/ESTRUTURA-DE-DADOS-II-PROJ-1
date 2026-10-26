import os
import time
import hashlib
import requests
import numpy as np
import pandas as pd
import joblib
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Diretórios e caminhos relativos à raiz do repositório
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCAO_DIR = os.path.dirname(APP_DIR)
REPO_ROOT = os.path.dirname(PRODUCAO_DIR)

BASELINE_PATH = os.path.join(REPO_ROOT, "data", "processed", "baseline_por_fluxo.csv")
MODEL_PATH = os.path.join(PRODUCAO_DIR, "modelo", "modelo_final.joblib")

print("=" * 60)
print(" INICIALIZANDO SERVIDOR DE MONITORAMENTO DE REDES (NOC MLOps)")
print("=" * 60)

# 1. Rastreabilidade Criptográfica (SHA-256)
print(f"1. Calculando SHA-256 do modelo serializado em: {MODEL_PATH}")
sha256_hash = hashlib.sha256()
with open(MODEL_PATH, "rb") as f:
    for byte_block in iter(lambda: f.read(4096), b""):
        sha256_hash.update(byte_block)
MODELO_SHA256 = sha256_hash.hexdigest()
print(f"   -> SHA-256: {MODELO_SHA256}")

# 2. Carga do Modelo e Baseline
print(f"2. Carregando baseline histórica de: {BASELINE_PATH}")
df_baseline = pd.read_csv(BASELINE_PATH)
baselines = df_baseline.set_index('fluxo_id').to_dict('index')

print("3. Carregando modelo campeão XGBoost...")
modelo = joblib.load(MODEL_PATH)
classes_map = {0: "OK", 1: "RISCO", 2: "FALHA"}
features_order = ['z_robusto', 'aumento_pct', 'jitter_relativo', 'perda_pct', 
                  'timeout_atual', 'n5_timeout', 'n5_aumento80', 'n5_risco']

# Buffer em memória para janelas móveis (últimos 5 pings por fluxo)
historico_fluxos = {}
START_TIME = time.time()

def diagnosticar_medicao(probe_id, dst_addr, rtt_ms, perda_pct, jitter_ms, ruido_pct=0.0):
    fluxo_id = f"{int(probe_id)}|{dst_addr}"
    if fluxo_id not in baselines:
        return {"erro": f"Fluxo {fluxo_id} não possui baseline histórica cadastrada."}
    
    base = baselines[fluxo_id]
    mediana = float(base['mediana'])
    mad = float(base['MAD']) if float(base['MAD']) > 0 else 1.0
    jitter_tipico = float(base['jitter_tipico']) if float(base['jitter_tipico']) > 0 else 0.5

    # Injeção opcional de ruído estocástico (teste de drift)
    if ruido_pct > 0.0 and rtt_ms is not None:
        ruido = np.random.normal(0, (ruido_pct / 100.0) * mad)
        rtt_ms = max(0.1, rtt_ms + ruido)
        jitter_ms = max(0.1, jitter_ms + np.random.normal(0, (ruido_pct / 100.0) * jitter_tipico))

    timeout_atual = 1.0 if perda_pct >= 100.0 or rtt_ms is None else 0.0
    rtt_val = mediana if timeout_atual else float(rtt_ms)
    
    z_robusto = max(0.0, (rtt_val - mediana) / mad)
    aumento_pct = max(0.0, ((rtt_val - mediana) / mediana) * 100.0) if mediana > 0 else 0.0
    jitter_relativo = max(0.0, float(jitter_ms) / jitter_tipico)

    # Atualiza janela móvel dos últimos 5 eventos
    if fluxo_id not in historico_fluxos:
        historico_fluxos[fluxo_id] = []
    
    hist = historico_fluxos[fluxo_id]
    is_risco = (z_robusto > 1.5) or (aumento_pct > 30.0)
    hist.append({"timeout": timeout_atual, "aumento80": 1.0 if aumento_pct > 80.0 else 0.0, "risco": 1.0 if is_risco else 0.0})
    if len(hist) > 5:
        hist.pop(0)

    n5_timeout = sum(h["timeout"] for h in hist)
    n5_aumento80 = sum(h["aumento80"] for h in hist)
    n5_risco = sum(h["risco"] for h in hist)

    vetor = pd.DataFrame([{
        'z_robusto': z_robusto,
        'aumento_pct': aumento_pct,
        'jitter_relativo': jitter_relativo,
        'perda_pct': float(perda_pct),
        'timeout_atual': timeout_atual,
        'n5_timeout': n5_timeout,
        'n5_aumento80': n5_aumento80,
        'n5_risco': n5_risco
    }])[features_order]

    # Inferência com medição de microssegundos
    t0 = time.perf_counter()
    probs = modelo.predict_proba(vetor)[0]
    latencia_inferencia_ms = (time.perf_counter() - t0) * 1000.0
    
    pred_idx = int(np.argmax(probs))
    classe_pred = classes_map[pred_idx]
    
    return {
        "fluxo_id": fluxo_id,
        "probe_id": int(probe_id),
        "dst_addr": dst_addr,
        "rtt_ms": round(rtt_val, 2),
        "mediana": round(mediana, 2),
        "mad": round(mad, 2),
        "z_robusto": round(z_robusto, 2),
        "aumento_pct": round(aumento_pct, 1),
        "jitter_relativo": round(jitter_relativo, 2),
        "perda_pct": round(float(perda_pct), 1),
        "timeout_atual": int(timeout_atual),
        "n5_risco": int(n5_risco),
        "n5_aumento80": int(n5_aumento80),
        "classe": classe_pred,
        "confianca_pct": round(float(probs[pred_idx]) * 100.0, 1),
        "probabilidades": {
            "OK": round(float(probs[0]) * 100.0, 1),
            "RISCO": round(float(probs[1]) * 100.0, 1),
            "FALHA": round(float(probs[2]) * 100.0, 1)
        },
        "modelo_sha256": MODELO_SHA256,
        "latencia_ms": round(latencia_inferencia_ms, 3)
    }

# =================== ROTAS DA APLICAÇÃO ===================

@app.route("/")
def index():
    return render_template("index.html", 
                           total_fluxos=len(baselines),
                           modelo_sha256=MODELO_SHA256)

@app.route("/api/saude")
def api_saude():
    """Liveness probe / Healthcheck padrão Cloud Native"""
    return jsonify({
        "status": "ok",
        "api": "ok",
        "modelo": "ok",
        "modelo_sha256": MODELO_SHA256,
        "uptime_segundos": round(time.time() - START_TIME, 1),
        "total_fluxos_cadastrados": len(baselines)
    })

@app.route("/api/modelo")
def api_modelo():
    """Metadados de auditoria e governança do modelo"""
    params = modelo.get_params() if hasattr(modelo, 'get_params') else {}
    return jsonify({
        "nome": "XGBoost Classifier (Campeão Produção)",
        "formato": "joblib",
        "sha256": MODELO_SHA256,
        "tamanho_disco_kb": round(os.path.getsize(MODEL_PATH) / 1024, 1),
        "classes": ["OK", "RISCO", "FALHA"],
        "atributos_entrada": features_order,
        "parametros": {
            "n_estimators": params.get("n_estimators", 100),
            "max_depth": params.get("max_depth", 4),
            "learning_rate": params.get("learning_rate", 0.05),
            "random_state": params.get("random_state", 42)
        }
    })

@app.route("/api/fluxos")
def get_fluxos():
    lista = []
    for f_id, data in baselines.items():
        parts = f_id.split("|")
        lista.append({
            "fluxo_id": f_id,
            "probe_id": parts[0],
            "dst_addr": parts[1],
            "mediana": round(float(data['mediana']), 2),
            "mad": round(float(data['MAD']), 2)
        })
    return jsonify(lista)

@app.route("/api/diagnosticar", methods=["POST"])
def api_diagnosticar():
    dados = request.json or {}
    probe_id = dados.get("probe_id")
    dst_addr = dados.get("dst_addr")
    rtt_ms = float(dados.get("rtt_ms", 30.0))
    perda_pct = float(dados.get("perda_pct", 0.0))
    jitter_ms = float(dados.get("jitter_ms", 1.0))
    ruido_pct = float(dados.get("ruido_pct", 0.0))
    
    resultado = diagnosticar_medicao(probe_id, dst_addr, rtt_ms, perda_pct, jitter_ms, ruido_pct)
    return jsonify(resultado)

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
            diag = diagnosticar_medicao(prb_id, dst_addr, rtt, perda, 1.0)
            if diag and "erro" not in diag:
                resultados.append(diag)

    return jsonify({
        "total_recebido": len(raw_data),
        "total_mapeado": len(resultados),
        "diagnosticos": resultados
    })

if __name__ == "__main__":
    print(f"Servidor NOC MLOps rodando em http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=False)
