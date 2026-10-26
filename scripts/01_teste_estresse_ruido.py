import os
import numpy as np
import pandas as pd
import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score, recall_score

print("=" * 70)
print(" EXPERIMENTO 1: TESTE DE ESTRESSE E DRIFT (ÁRVORE VS XGBOOST)")
print("=" * 70)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR

DATA_PATH = os.path.join(REPO_ROOT, "data", "processed", "dataset_rotulado_B_split.csv")
MODEL_PATH = os.path.join(REPO_ROOT, "producao", "modelo", "modelo_final.joblib")

print(f"Carregando dados de: {DATA_PATH}")
df = pd.read_csv(DATA_PATH)

features = ['z_robusto', 'aumento_pct', 'jitter_relativo', 'perda_pct', 'timeout_atual', 'n5_timeout', 'n5_aumento80', 'n5_risco']
mapping = {'OK': 0, 'RISCO': 1, 'FALHA': 2}
df['label'] = df['classe'].map(mapping)

treino = df[df['split'] == 'treino']
teste = df[df['split'] == 'teste'].copy()

X_treino = treino[features]
y_treino = treino['label']
X_teste_orig = teste[features].copy()
y_teste = teste['label']

print(f"Treino: {len(X_treino)} linhas | Teste: {len(X_teste_orig)} linhas")

# 1. Treina a Árvore de Decisão oficial da Tarefa 4 (depth 7)
print("\nTreinando a Árvore de Decisão oficial (max_depth=7)...")
dt = DecisionTreeClassifier(max_depth=7, criterion='gini', random_state=42)
dt.fit(X_treino, y_treino)

# 2. Carrega o XGBoost Campeão da Tarefa 6
print(f"Carregando XGBoost Campeão de: {MODEL_PATH}...")
xgb = joblib.load(MODEL_PATH)

# Variáveis contínuas que sofrem ruído térmico/congestionamento na rede real
continuous_features = ['z_robusto', 'aumento_pct', 'jitter_relativo']
stds = X_teste_orig[continuous_features].std()

noise_levels = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
results = []

print("\nExecutando injeção progressiva de ruído gaussiano (simulando oscilação de tráfego real)...")
np.random.seed(42)

for noise in noise_levels:
    X_noisy = X_teste_orig.copy()
    if noise > 0:
        for col in continuous_features:
            sigma = noise * stds[col]
            noise_vector = np.random.normal(0, sigma, size=len(X_noisy))
            X_noisy[col] = np.maximum(0, X_noisy[col] + noise_vector)
    
    pred_dt = dt.predict(X_noisy)
    pred_xgb = xgb.predict(X_noisy)
    
    f1_dt = f1_score(y_teste, pred_dt, average='macro')
    rec_falha_dt = recall_score(y_teste, pred_dt, labels=[2], average='macro', zero_division=0)
    
    f1_xgb = f1_score(y_teste, pred_xgb, average='macro')
    rec_falha_xgb = recall_score(y_teste, pred_xgb, labels=[2], average='macro', zero_division=0)
    
    results.append({
        "Ruído": f"{int(noise*100)}%",
        "F1 Árvore": f1_dt,
        "F1 XGBoost": f1_xgb,
        "Recall FALHA Árvore": rec_falha_dt,
        "Recall FALHA XGBoost": rec_falha_xgb,
        "Vantagem XGBoost (F1)": f1_xgb - f1_dt
    })

res_df = pd.DataFrame(results)

print("\n" + "=" * 70)
print(" TABELA COMPARATIVA DE ESTRESSE: ÁRVORE VS XGBOOST SOB RUÍDO")
print("=" * 70)
print(res_df.to_string(index=False, formatters={
    'F1 Árvore': '{:.4f}'.format,
    'F1 XGBoost': '{:.4f}'.format,
    'Recall FALHA Árvore': '{:.4f}'.format,
    'Recall FALHA XGBoost': '{:.4f}'.format,
    'Vantagem XGBoost (F1)': '{:+.4f}'.format
}))
print("=" * 70)
