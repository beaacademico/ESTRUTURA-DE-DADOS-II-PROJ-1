import os
import time
import requests
import numpy as np
import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier

print("=" * 70)
print(" EXPERIMENTO 3: TESTE COM DADOS REAIS COLETADOS HOJE DA API RIPE ATLAS")
print("=" * 70)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR

BASELINE_PATH = os.path.join(REPO_ROOT, "data", "processed", "baseline_por_fluxo.csv")
MODEL_PATH = os.path.join(REPO_ROOT, "producao", "modelo", "modelo_final.joblib")
TRAIN_DATA_PATH = os.path.join(REPO_ROOT, "data", "processed", "dataset_rotulado_B_split.csv")

# 1. Carrega Baselines e Modelos
print("1. Carregando Baselines históricas...")
df_baseline = pd.read_csv(BASELINE_PATH)
baselines = df_baseline.set_index('fluxo_id').to_dict('index')

print("2. Carregando XGBoost e treinando Árvore de Decisão...")
xgb = joblib.load(MODEL_PATH)

df_train = pd.read_csv(TRAIN_DATA_PATH)
features = ['z_robusto', 'aumento_pct', 'jitter_relativo', 'perda_pct', 'timeout_atual', 'n5_timeout', 'n5_aumento80', 'n5_risco']
mapping = {'OK': 0, 'RISCO': 1, 'FALHA': 2}
df_train['label'] = df_train['classe'].map(mapping)
sub_train = df_train[df_train['split'] == 'treino']

dt = DecisionTreeClassifier(max_depth=7, criterion='gini', random_state=42)
dt.fit(sub_train[features], sub_train['label'])

# 3. Consulta API do RIPE Atlas ao vivo
msm_id = 9333345
now = int(time.time())
start = now - 3600  # última 1 hora

print(f"\n3. Consultando API RIPE Atlas ao vivo (Measurement {msm_id})...")
url = f"https://atlas.ripe.net/api/v2/measurements/{msm_id}/results/?start={start}&stop={now}&format=json"

try:
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        print(f"Erro na API RIPE: Status {r.status_code}")
        exit()
    raw_data = r.json()
    print(f"   -> {len(raw_data)} medições em tempo real recebidas da última hora!")
except Exception as e:
    print(f"Falha de conexão com a API: {e}")
    exit()

# 4. Processamento dos pacotes ao vivo
registros = []
historico = {}

print("\n4. Processando medições ao vivo contra as baselines históricas...")

for item in raw_data:
    prb_id = item.get('prb_id')
    dst_addr = item.get('dst_addr')
    fluxo_id = f"{prb_id}|{dst_addr}"
    
    if fluxo_id not in baselines:
        continue
    
    base = baselines[fluxo_id]
    mediana = base['mediana']
    mad = base['MAD'] if base['MAD'] > 0 else 1.0
    jitter_tipico = base['jitter_tipico'] if base['jitter_tipico'] > 0 else 0.5
    
    rtt_ms = item.get('avg')
    sent = item.get('sent', 3)
    rcvd = item.get('rcvd', 0)
    perda_pct = ((sent - rcvd) / sent) * 100.0 if sent > 0 else 100.0
    
    results_list = item.get('result', [])
    rtts = [p.get('rtt') for p in results_list if isinstance(p, dict) and p.get('rtt') is not None]
    jitter_ms = float(np.std(rtts)) if len(rtts) > 1 else 0.5
    
    timeout_atual = 1.0 if perda_pct >= 100.0 or rtt_ms is None else 0.0
    rtt_val = mediana if timeout_atual else float(rtt_ms)
    
    z_robusto = max(0.0, (rtt_val - mediana) / mad)
    aumento_pct = max(0.0, ((rtt_val - mediana) / mediana) * 100.0) if mediana > 0 else 0.0
    jitter_relativo = max(0.0, jitter_ms / jitter_tipico)
    
    if fluxo_id not in historico:
        historico[fluxo_id] = []
    hist = historico[fluxo_id]
    is_risco = (z_robusto > 1.5) or (aumento_pct > 30.0)
    hist.append({"timeout": timeout_atual, "aumento80": 1.0 if aumento_pct > 80.0 else 0.0, "risco": 1.0 if is_risco else 0.0})
    if len(hist) > 5:
        hist.pop(0)
        
    registros.append({
        'fluxo_id': fluxo_id,
        'rtt_ms': rtt_val,
        'mediana': mediana,
        'z_robusto': z_robusto,
        'aumento_pct': aumento_pct,
        'jitter_relativo': jitter_relativo,
        'perda_pct': perda_pct,
        'timeout_atual': timeout_atual,
        'n5_timeout': sum(h['timeout'] for h in hist),
        'n5_aumento80': sum(h['aumento80'] for h in hist),
        'n5_risco': sum(h['risco'] for h in hist)
    })

df_live = pd.DataFrame(registros)
print(f"   -> {len(df_live)} medições mapeadas com sucesso para os 69 fluxos históricos!")

if len(df_live) > 0:
    X_live = df_live[features]
    pred_dt = dt.predict(X_live)
    pred_xgb = xgb.predict(X_live)
    probs_xgb = xgb.predict_proba(X_live)

    classes_inv = {0: 'OK', 1: 'RISCO', 2: 'FALHA'}
    df_live['pred_arvore'] = [classes_inv[p] for p in pred_dt]
    df_live['pred_xgboost'] = [classes_inv[p] for p in pred_xgb]
    df_live['confianca_xgboost'] = [probs_xgb[i][pred_xgb[i]] * 100.0 for i in range(len(df_live))]

    print("\n" + "=" * 70)
    print(" DISTRIBUIÇÃO DAS CLASSIFICAÇÕES EM DADOS VIVOS DE HOJE")
    print("=" * 70)
    print("Árvore de Decisão:")
    print(df_live['pred_arvore'].value_counts())
    print("\nXGBoost Campeão:")
    print(df_live['pred_xgboost'].value_counts())

    concordancia = (df_live['pred_arvore'] == df_live['pred_xgboost']).mean() * 100.0
    print(f"\nConcordância entre os dois modelos nos dados ao vivo: {concordancia:.2f}%")

print("=" * 70)
print("Experimento concluído!")
