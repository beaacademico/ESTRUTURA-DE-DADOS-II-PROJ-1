import os
import time
import pandas as pd
import numpy as np
import joblib

print("=" * 70)
print(" EXPERIMENTO 2: SIMULADOR DE INFERÊNCIA OPERACIONAL (MLOps / NOC)")
print("=" * 70)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR

BASELINE_PATH = os.path.join(REPO_ROOT, "data", "processed", "baseline_por_fluxo.csv")
MODEL_PATH = os.path.join(REPO_ROOT, "producao", "modelo", "modelo_final.joblib")
TEST_DATA_PATH = os.path.join(REPO_ROOT, "data", "processed", "dataset_rotulado_B_split.csv")

print(f"1. Carregando Baseline Histórica de {BASELINE_PATH}...")
df_baseline = pd.read_csv(BASELINE_PATH)
baselines = df_baseline.set_index('fluxo_id').to_dict('index')
print(f"   -> {len(baselines)} fluxos catalogados.")

print(f"\n2. Carregando Modelo Campeão XGBoost de {MODEL_PATH}...")
modelo = joblib.load(MODEL_PATH)
classes_map = {0: "OK", 1: "RISCO", 2: "FALHA"}

class MonitorDeRedeEmTempoReal:
    def __init__(self, modelo, baselines):
        self.modelo = modelo
        self.baselines = baselines
        self.historico = {}
        self.features_order = ['z_robusto', 'aumento_pct', 'jitter_relativo', 'perda_pct', 
                               'timeout_atual', 'n5_timeout', 'n5_aumento80', 'n5_risco']

    def processar_medicao(self, probe_id, dst_addr, rtt_ms, perda_pct, jitter_ms):
        fluxo_id = f"{int(probe_id)}|{dst_addr}"
        if fluxo_id not in self.baselines:
            return None, "Fluxo sem baseline cadastrada."
        
        base = self.baselines[fluxo_id]
        mediana = base['mediana']
        mad = base['MAD'] if base['MAD'] > 0 else 1.0
        jitter_tipico = base['jitter_tipico'] if base['jitter_tipico'] > 0 else 0.5

        timeout_atual = 1.0 if perda_pct >= 100.0 or pd.isna(rtt_ms) else 0.0
        rtt_val = mediana if timeout_atual else rtt_ms
        z_robusto = max(0.0, (rtt_val - mediana) / mad)
        aumento_pct = max(0.0, ((rtt_val - mediana) / mediana) * 100.0) if mediana > 0 else 0.0
        jitter_relativo = max(0.0, jitter_ms / jitter_tipico)

        if fluxo_id not in self.historico:
            self.historico[fluxo_id] = []
        
        hist = self.historico[fluxo_id]
        is_risco_pontual = (z_robusto > 1.5) or (aumento_pct > 30.0)
        hist.append({
            "timeout": timeout_atual,
            "aumento80": 1.0 if aumento_pct > 80.0 else 0.0,
            "risco": 1.0 if is_risco_pontual else 0.0
        })
        if len(hist) > 5:
            hist.pop(0)

        n5_timeout = sum(h["timeout"] for h in hist)
        n5_aumento80 = sum(h["aumento80"] for h in hist)
        n5_risco = sum(h["risco"] for h in hist)

        vetor = pd.DataFrame([{
            'z_robusto': z_robusto,
            'aumento_pct': aumento_pct,
            'jitter_relativo': jitter_relativo,
            'perda_pct': perda_pct,
            'timeout_atual': timeout_atual,
            'n5_timeout': n5_timeout,
            'n5_aumento80': n5_aumento80,
            'n5_risco': n5_risco
        }])[self.features_order]

        probs = self.modelo.predict_proba(vetor)[0]
        pred_idx = np.argmax(probs)
        classe_pred = classes_map[pred_idx]
        confianca = probs[pred_idx] * 100.0

        return {
            "fluxo": fluxo_id,
            "rtt_ms": rtt_val,
            "mediana": mediana,
            "z_robusto": z_robusto,
            "classe": classe_pred,
            "confianca": confianca,
            "probs": probs
        }

print("\n3. Inicializando Monitor de Rede...")
monitor = MonitorDeRedeEmTempoReal(modelo, baselines)

df_test = pd.read_csv(TEST_DATA_PATH)
df_test = df_test[df_test['split'] == 'teste'].sample(n=15, random_state=42)

print("\n" + "=" * 70)
print(" SIMULAÇÃO DE INFERÊNCIA EM TEMPO REAL (STREAMING DE MEDIÇÕES)")
print("=" * 70)

for idx, row in df_test.iterrows():
    probe_id = row['probe_id']
    dst_addr = row['dst_addr']
    rtt_ms = row['avg']
    perda = row['perda_pct']
    jitter = row['jitter_ms']
    classe_real = row['classe']

    resultado = monitor.processar_medicao(probe_id, dst_addr, rtt_ms, perda, jitter)
    if resultado:
        c = resultado["classe"]
        tag = "[OK]    " if c == "OK" else ("[RISCO] " if c == "RISCO" else "[FALHA] ")
        correta = "[ACERTO]" if c == classe_real else f"[ERRO (Real: {classe_real})]"
        print(f"{tag} Fluxo {resultado['fluxo'][:22]}... | RTT: {resultado['rtt_ms']:6.2f}ms (Mediana: {resultado['mediana']:6.2f}ms | z: {resultado['z_robusto']:4.1f}) -> Predição: {c:5s} ({resultado['confianca']:5.1f}%) | {correta}")
    time.sleep(0.05)

print("=" * 70)
print("Simulação concluída com sucesso! O modelo responde em tempo de microsserviço.")
