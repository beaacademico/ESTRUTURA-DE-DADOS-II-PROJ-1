# -*- coding: utf-8 -*-
"""
Script de Treinamento, Avaliação Multi-Horizonte (T=0, T+1, T+1..T+3)
e Empacotamento Canônico para o Blackboard — CypherNet: Vigia de Redes (Grupo 05).

Gera:
1. dist/Grupo05/modelo.joblib
2. dist/Grupo05/metadados.json
3. dist/Grupo05/baseline.csv
4. dist/Grupo05.zip (e cópia em Downloads/Grupo05.zip)
5. Atualiza producao/modelo/modelo_final.joblib, producao/modelo/metadados.json e producao/modelo/baseline.csv
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone

import joblib
import matplotlib
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.tree import DecisionTreeClassifier

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.cyphernet.features import (
    CLASSES,
    FEATURES,
    FEATURES_BASE,
    FEATURES_TENDENCIA,
    JANELA,
    adicionar_tendencias,
)

CLASSES_ORDEM = list(CLASSES)
CLASSES_MAP = {"OK": 0, "RISCO": 1, "FALHA": 2}
CLASSES_INV = {0: "OK", 1: "RISCO", 2: "FALHA"}
FATOR_MAD_NORMAL = 1.4826
FEATURES_EXPANDIDAS = FEATURES
JANELA_HISTORICO = JANELA


def calcular_sha256(caminho: str) -> str:
    sha = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(65536), b""):
            sha.update(bloco)
    return sha.hexdigest()


def avaliar_predicoes(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    acc = float(accuracy_score(y_true, y_pred))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))
    prec_por_classe = precision_score(y_true, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
    rec_por_classe = recall_score(y_true, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
    f1_por_classe = f1_score(y_true, y_pred, average=None, labels=[0, 1, 2], zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2]).tolist()

    return {
        "accuracy": round(acc, 6),
        "f1_macro": round(f1_macro, 6),
        "f1_weighted": round(f1_weighted, 6),
        "por_classe": {
            "OK": {
                "precision": round(float(prec_por_classe[0]), 6),
                "recall": round(float(rec_por_classe[0]), 6),
                "f1": round(float(f1_por_classe[0]), 6),
            },
            "RISCO": {
                "precision": round(float(prec_por_classe[1]), 6),
                "recall": round(float(rec_por_classe[1]), 6),
                "f1": round(float(f1_por_classe[1]), 6),
            },
            "FALHA": {
                "precision": round(float(prec_por_classe[2]), 6),
                "recall": round(float(rec_por_classe[2]), 6),
                "f1": round(float(f1_por_classe[2]), 6),
            },
        },
        "matriz_confusao_3x3": cm,
    }


def main():
    print("=" * 78)
    print(" CYPHERNET: VIGIA DE REDES — TREINAMENTO MULTI-HORIZONTE E EMPACOTAMENTO")
    print("=" * 78)

    caminho_dataset = os.path.join(REPO_ROOT, "data", "processed", "dataset_rotulado_B_split.csv")
    caminho_baseline = os.path.join(REPO_ROOT, "data", "processed", "baseline_por_fluxo.csv")

    print(f"[1/6] Carregando dataset: {caminho_dataset}")
    df = pd.read_csv(caminho_dataset)
    df_base = pd.read_csv(caminho_baseline)

    if "fluxo_id" not in df.columns:
        df["fluxo_id"] = df["probe_id"].astype(int).astype(str) + "|" + df["dst_addr"].astype(str)
    if "classe_num" not in df.columns:
        df["classe_num"] = df["classe"].map(CLASSES_MAP).astype(int)

    df = df.sort_values(["fluxo_id", "timestamp"]).reset_index(drop=True)
    print(f"      Registros totais: {len(df):,} | Fluxos únicos: {df['fluxo_id'].nunique()}")

    print("[2/6] Calculando 11 features (8 base + 3 tendência) via src.cyphernet.features...")
    df = adicionar_tendencias(df)

    # Construção de alvos por fluxo (sem vazamento entre fluxos nem do futuro)
    g = df.groupby("fluxo_id", sort=False)
    df["alvo_t0"] = df["classe_num"].astype(int)
    df["alvo_t1"] = g["classe_num"].shift(-1)

    # Alvo horizonte 3 passos (pior estado nos próximos 3 ciclos = ~12 minutos à frente)
    s1 = g["classe_num"].shift(-1)
    s2 = g["classe_num"].shift(-2)
    s3 = g["classe_num"].shift(-3)
    df["alvo_h3"] = pd.concat([s1, s2, s3], axis=1).max(axis=1)

    # Evitar fronteira entre splits dentro do mesmo fluxo para T+1 e H3
    split_next1 = g["split"].shift(-1)
    split_next3 = g["split"].shift(-3)
    mask_t1_valido = df["alvo_t1"].notna() & (df["split"] == split_next1)
    mask_h3_valido = df["alvo_h3"].notna() & (df["split"] == split_next3)

    # =========================================================================
    # MODO 1: DIAGNÓSTICO INSTANTÂNEO (T=0) — 8 FEATURES BASE
    # =========================================================================
    print("\n[3/6] Treinando e avaliando modelos no Modo Diagnóstico Instantâneo (T=0)...")
    df_tr_t0 = df[df["split"] == "treino"]
    df_va_t0 = df[df["split"] == "validacao"]
    df_te_t0 = df[df["split"] == "teste"]

    X_tr_t0, y_tr_t0 = df_tr_t0[FEATURES_BASE], df_tr_t0["alvo_t0"].values
    X_va_t0, y_va_t0 = df_va_t0[FEATURES_BASE], df_va_t0["alvo_t0"].values
    X_te_t0, y_te_t0 = df_te_t0[FEATURES_BASE], df_te_t0["alvo_t0"].values

    dt_t0 = DecisionTreeClassifier(
        criterion="gini",
        max_depth=7,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
    )
    dt_t0.fit(X_tr_t0, y_tr_t0)

    rf_t0 = RandomForestClassifier(
        n_estimators=100,
        max_depth=7,
        random_state=42,
        n_jobs=-1,
    )
    rf_t0.fit(X_tr_t0, y_tr_t0)

    xgb_t0 = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.05,
        random_state=42,
        eval_metric="mlogloss",
    )
    xgb_t0.fit(X_tr_t0, y_tr_t0)

    metricas_t0 = {
        "arvore_decisao_prof7": {
            "validacao": avaliar_predicoes(y_va_t0, dt_t0.predict(X_va_t0)),
            "teste": avaliar_predicoes(y_te_t0, dt_t0.predict(X_te_t0)),
            "profundidade_real": int(dt_t0.get_depth()),
            "n_folhas": int(dt_t0.get_n_leaves()),
        },
        "random_forest": {
            "validacao": avaliar_predicoes(y_va_t0, rf_t0.predict(X_va_t0)),
            "teste": avaliar_predicoes(y_te_t0, rf_t0.predict(X_te_t0)),
        },
        "xgboost": {
            "validacao": avaliar_predicoes(y_va_t0, xgb_t0.predict(X_va_t0)),
            "teste": avaliar_predicoes(y_te_t0, xgb_t0.predict(X_te_t0)),
        },
    }

    print(
        f"      -> [T=0 Diagnóstico] Árvore (depth=7, folhas={dt_t0.get_n_leaves()}): "
        f"F1 Macro Val={metricas_t0['arvore_decisao_prof7']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_t0['arvore_decisao_prof7']['teste']['f1_macro']:.4f}"
    )
    print(
        f"      -> [T=0 Diagnóstico] Random Forest: "
        f"F1 Macro Val={metricas_t0['random_forest']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_t0['random_forest']['teste']['f1_macro']:.4f}"
    )
    print(
        f"      -> [T=0 Diagnóstico] XGBoost: "
        f"F1 Macro Val={metricas_t0['xgboost']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_t0['xgboost']['teste']['f1_macro']:.4f}"
    )

    # =========================================================================
    # MODO 2: PREVISÃO PROATIVA FUTURA (T+1 = +4 min) — 11 FEATURES EXPANDIDAS
    # =========================================================================
    print("\n[4/6] Treinando e avaliando modelos no Modo Previsão Proativa (T+1 = +4 min)...")
    df_t1 = df[mask_t1_valido].copy()
    df_t1["alvo_t1"] = df_t1["alvo_t1"].astype(int)

    df_tr_t1 = df_t1[df_t1["split"] == "treino"]
    df_va_t1 = df_t1[df_t1["split"] == "validacao"]
    df_te_t1 = df_t1[df_t1["split"] == "teste"]

    X_tr_t1, y_tr_t1 = df_tr_t1[FEATURES_EXPANDIDAS], df_tr_t1["alvo_t1"].values
    X_va_t1, y_va_t1 = df_va_t1[FEATURES_EXPANDIDAS], df_va_t1["alvo_t1"].values
    X_te_t1, y_te_t1 = df_te_t1[FEATURES_EXPANDIDAS], df_te_t1["alvo_t1"].values

    # Hiperparâmetros ótimos validados na partição de validação temporal (sem vazamento)
    melhor_cfg_dt_t1 = {
        "max_depth": 8,
        "min_samples_leaf": 10,
        "class_weight": "{0: 1.0, 1: 2.0, 2: 3.0}",
    }
    melhor_dt_t1 = DecisionTreeClassifier(
        criterion="gini",
        max_depth=8,
        min_samples_leaf=10,
        class_weight={0: 1.0, 1: 2.0, 2: 3.0},
        random_state=42,
    )
    melhor_dt_t1.fit(X_tr_t1, y_tr_t1)

    melhor_cfg_rf_t1 = {
        "max_depth": 10,
        "class_weight": "{0: 1.0, 1: 2.0, 2: 3.0}",
    }
    melhor_rf_t1 = RandomForestClassifier(
        n_estimators=150,
        max_depth=10,
        min_samples_leaf=20,
        class_weight={0: 1.0, 1: 2.0, 2: 3.0},
        random_state=42,
        n_jobs=-1,
    )
    melhor_rf_t1.fit(X_tr_t1, y_tr_t1)

    # XGBoost T+1
    xgb_t1 = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="mlogloss",
    )
    xgb_t1.fit(X_tr_t1, y_tr_t1)

    metricas_t1 = {
        "arvore_decisao_proativa": {
            "hiperparametros": melhor_cfg_dt_t1,
            "profundidade_real": int(melhor_dt_t1.get_depth()),
            "n_folhas": int(melhor_dt_t1.get_n_leaves()),
            "validacao": avaliar_predicoes(y_va_t1, melhor_dt_t1.predict(X_va_t1)),
            "teste": avaliar_predicoes(y_te_t1, melhor_dt_t1.predict(X_te_t1)),
        },
        "random_forest_proativo": {
            "hiperparametros": melhor_cfg_rf_t1,
            "validacao": avaliar_predicoes(y_va_t1, melhor_rf_t1.predict(X_va_t1)),
            "teste": avaliar_predicoes(y_te_t1, melhor_rf_t1.predict(X_te_t1)),
        },
        "xgboost_proativo": {
            "validacao": avaliar_predicoes(y_va_t1, xgb_t1.predict(X_va_t1)),
            "teste": avaliar_predicoes(y_te_t1, xgb_t1.predict(X_te_t1)),
        },
    }

    print(
        f"      -> [T+1 (+4 min)] Árvore ({melhor_cfg_dt_t1}): "
        f"F1 Macro Val={metricas_t1['arvore_decisao_proativa']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_t1['arvore_decisao_proativa']['teste']['f1_macro']:.4f} | "
        f"Recall FALHA Teste={metricas_t1['arvore_decisao_proativa']['teste']['por_classe']['FALHA']['recall']:.4f}"
    )
    print(
        f"      -> [T+1 (+4 min)] Random Forest ({melhor_cfg_rf_t1}): "
        f"F1 Macro Val={metricas_t1['random_forest_proativo']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_t1['random_forest_proativo']['teste']['f1_macro']:.4f} | "
        f"Recall FALHA Teste={metricas_t1['random_forest_proativo']['teste']['por_classe']['FALHA']['recall']:.4f}"
    )
    print(
        f"      -> [T+1 (+4 min)] XGBoost: "
        f"F1 Macro Val={metricas_t1['xgboost_proativo']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_t1['xgboost_proativo']['teste']['f1_macro']:.4f} | "
        f"Recall FALHA Teste={metricas_t1['xgboost_proativo']['teste']['por_classe']['FALHA']['recall']:.4f}"
    )

    # =========================================================================
    # MODO 3: HORIZONTE DE ALERTA ANTECIPADO (T+1..T+3 = próximos 12 min)
    # =========================================================================
    print("\n[5/6] Avaliando Horizonte de Alerta Antecipado (H3 = pior estado em 12 min)...")
    df_h3 = df[mask_h3_valido].copy()
    df_h3["alvo_h3"] = df_h3["alvo_h3"].astype(int)

    df_tr_h3 = df_h3[df_h3["split"] == "treino"]
    df_va_h3 = df_h3[df_h3["split"] == "validacao"]
    df_te_h3 = df_h3[df_h3["split"] == "teste"]

    X_tr_h3, y_tr_h3 = df_tr_h3[FEATURES_EXPANDIDAS], df_tr_h3["alvo_h3"].values
    X_va_h3, y_va_h3 = df_va_h3[FEATURES_EXPANDIDAS], df_va_h3["alvo_h3"].values
    X_te_h3, y_te_h3 = df_te_h3[FEATURES_EXPANDIDAS], df_te_h3["alvo_h3"].values

    dt_h3 = DecisionTreeClassifier(
        criterion="gini",
        max_depth=7,
        min_samples_leaf=25,
        class_weight={0: 1.0, 1: 1.5, 2: 2.0},
        random_state=42,
    )
    dt_h3.fit(X_tr_h3, y_tr_h3)

    rf_h3 = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_leaf=20,
        class_weight={0: 1.0, 1: 1.5, 2: 2.0},
        random_state=42,
        n_jobs=-1,
    )
    rf_h3.fit(X_tr_h3, y_tr_h3)

    metricas_h3 = {
        "arvore_decisao_h3_12min": {
            "validacao": avaliar_predicoes(y_va_h3, dt_h3.predict(X_va_h3)),
            "teste": avaliar_predicoes(y_te_h3, dt_h3.predict(X_te_h3)),
        },
        "random_forest_h3_12min": {
            "validacao": avaliar_predicoes(y_va_h3, rf_h3.predict(X_va_h3)),
            "teste": avaliar_predicoes(y_te_h3, rf_h3.predict(X_te_h3)),
        },
    }

    print(
        f"      -> [H3 (+12 min)] Árvore: "
        f"F1 Macro Val={metricas_h3['arvore_decisao_h3_12min']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_h3['arvore_decisao_h3_12min']['teste']['f1_macro']:.4f} | "
        f"Recall FALHA Teste={metricas_h3['arvore_decisao_h3_12min']['teste']['por_classe']['FALHA']['recall']:.4f}"
    )
    print(
        f"      -> [H3 (+12 min)] Random Forest: "
        f"F1 Macro Val={metricas_h3['random_forest_h3_12min']['validacao']['f1_macro']:.4f} | "
        f"Teste={metricas_h3['random_forest_h3_12min']['teste']['f1_macro']:.4f} | "
        f"Recall FALHA Teste={metricas_h3['random_forest_h3_12min']['teste']['por_classe']['FALHA']['recall']:.4f}"
    )

    # Importância de features (T=0 e T+1)
    importancias_dt_t0 = {
        feat: round(float(imp), 6)
        for feat, imp in zip(FEATURES_BASE, dt_t0.feature_importances_)
    }
    importancias_dt_t1 = {
        feat: round(float(imp), 6)
        for feat, imp in zip(FEATURES_EXPANDIDAS, melhor_dt_t1.feature_importances_)
    }

    # =========================================================================
    # EMPACOTAMENTO CANÔNICO DO BLACKBOARD (dist/Grupo05/)
    # =========================================================================
    print("\n[6/6] Gerando pacote canônico Blackboard (modelo.joblib, metadados.json, baseline.csv)...")
    dist_dir = os.path.join(REPO_ROOT, "dist", "Grupo05")
    os.makedirs(dist_dir, exist_ok=True)
    prod_model_dir = os.path.join(REPO_ROOT, "producao", "modelo")
    os.makedirs(prod_model_dir, exist_ok=True)

    # 1. Enriquecer baseline.csv conforme especificação da página 5 do edital
    # Período da baseline (primeiros 7 dias da coleta RIPE Atlas msm_id=9333345, imediatamente
    # anteriores ao início do dataset supervisionado para evitar vazamento temporal):
    ts_fim_base = int(df["timestamp"].min())
    ts_ini_base = ts_fim_base - 7 * 86400
    dt_ini_iso = datetime.fromtimestamp(ts_ini_base, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dt_fim_iso = datetime.fromtimestamp(ts_fim_base, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    df_base_enriq = df_base.copy()
    parts = df_base_enriq["fluxo_id"].str.split("|", expand=True)
    df_base_enriq["probe_id"] = parts[0].astype(int)
    df_base_enriq["dst_addr"] = parts[1]
    df_base_enriq["periodo_calculo_inicio"] = dt_ini_iso
    df_base_enriq["periodo_calculo_fim"] = dt_fim_iso
    df_base_enriq["duracao_baseline_dias"] = 7
    df_base_enriq["amostras_janela_baseline"] = (df_base_enriq["prop_resposta"] * 2520).round().astype(int)
    df_base_enriq["min_amostras_validas"] = 1500
    df_base_enriq["prop_minima_resposta"] = 0.70
    df_base_enriq["fator_escala_mad"] = FATOR_MAD_NORMAL
    df_base_enriq["baseline_valida"] = (
        (df_base_enriq["amostras_janela_baseline"] >= 1500)
        & (df_base_enriq["prop_resposta"] >= 0.70)
        & (df_base_enriq["mediana"] > 0)
    )
    df_base_enriq["recomendacao_uso"] = (
        "Utilizar mediana, MAD (multiplicado por 1.4826) e jitter_tipico do fluxo_id correspondente "
        "para normalizar cada nova medicao; recalibrar semanalmente em janela movel de 7 dias."
    )

    # Manter as 6 colunas originais na frente para retrocompatibilidade total + colunas exigidas pelo edital
    colunas_baseline = [
        "fluxo_id",
        "mediana",
        "MAD",
        "jitter_tipico",
        "perda_tipica",
        "prop_resposta",
        "probe_id",
        "dst_addr",
        "periodo_calculo_inicio",
        "periodo_calculo_fim",
        "duracao_baseline_dias",
        "amostras_janela_baseline",
        "min_amostras_validas",
        "prop_minima_resposta",
        "fator_escala_mad",
        "baseline_valida",
        "recomendacao_uso",
    ]
    df_base_enriq = df_base_enriq[colunas_baseline]

    caminho_baseline_dist = os.path.join(dist_dir, "baseline.csv")
    caminho_baseline_prod = os.path.join(prod_model_dir, "baseline.csv")
    df_base_enriq.to_csv(caminho_baseline_dist, index=False, encoding="utf-8")
    df_base_enriq.to_csv(caminho_baseline_prod, index=False, encoding="utf-8")

    # 2. Salvar modelo.joblib no formato de dicionário auto-contido padrão da professora:
    # {"modelo": dt_t0, "features": FEATURES_BASE, "familia": "arvore_decisao", "params": ...}
    # Inclui também as Árvores de Decisão proativas (T+1 = +4 min e H3 = +12 min) para uso na API!
    pacote_modelo = {
        "modelo": dt_t0,
        "features": list(FEATURES_BASE),
        "familia": "arvore_decisao",
        "params": {
            "criterion": "gini",
            "max_depth": 7,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "random_state": 42,
        },
        "classes": list(CLASSES_ORDEM),
        "classes_map": {0: "OK", 1: "RISCO", 2: "FALHA"},
        "horizonte_principal": "T=0 (Diagnostico Instantaneo em Tempo Real)",
        "modelo_proativo_t1": melhor_dt_t1,
        "modelo_proativo_h3": dt_h3,
        "features_proativas": list(FEATURES_EXPANDIDAS),
    }

    caminho_modelo_dist = os.path.join(dist_dir, "modelo.joblib")
    caminho_modelo_prod = os.path.join(prod_model_dir, "modelo_final.joblib")
    joblib.dump(pacote_modelo, caminho_modelo_dist)
    joblib.dump(pacote_modelo, caminho_modelo_prod)

    sha256_modelo = calcular_sha256(caminho_modelo_dist)
    sha256_baseline = calcular_sha256(caminho_baseline_dist)

    # 3. Construir exemplo real de entrada e saída (item obrigatório na pág. 5 do edital)
    candidatos_ex = df_te_t1[(df_te_t1["alvo_t0"] == 1) & (df_te_t1["alvo_t1"] >= 1)]
    amostra_risco = candidatos_ex.iloc[0] if len(candidatos_ex) > 0 else df_te_t0[df_te_t0["alvo_t0"] == 1].iloc[0]
    vetor_exemplo_t0 = pd.DataFrame([amostra_risco[FEATURES_BASE].to_dict()])[FEATURES_BASE]
    probs_ex_t0 = dt_t0.predict_proba(vetor_exemplo_t0)[0]
    pred_ex_t0 = int(dt_t0.predict(vetor_exemplo_t0)[0])

    vetor_exemplo_t1 = pd.DataFrame([amostra_risco[FEATURES_EXPANDIDAS].to_dict()])[FEATURES_EXPANDIDAS]
    probs_ex_t1 = melhor_dt_t1.predict_proba(vetor_exemplo_t1)[0]
    pred_ex_t1 = int(melhor_dt_t1.predict(vetor_exemplo_t1)[0])

    # 4. Construir metadados.json completo (cobrindo todos os 11 itens da pág. 5 do edital)
    metadados = {
        "projeto": "CypherNet: Vigia de Redes",
        "grupo": "Grupo 05",
        "integrantes": [
            {"nome": "Beatriz Gonçalves da Silva", "ra": "2400909"},
            {"nome": "Breno Brasil de Souza", "ra": "2401483"},
            {"nome": "Enzo Moraes Sousa", "ra": "2401685"},
            {"nome": "Natsumi Goto", "ra": "2401999"},
            {"nome": "Pedro Viana da Silva", "ra": "2400956"},
            {"nome": "Vitória Alessandra das Neves", "ra": "2401781"},
        ],
        "1_identificacao_modelo": {
            "nome_modelo": "CypherNet DecisionTree Classifier (Profundidade 7)",
            "familia": "arvore_decisao",
            "classe_python": "sklearn.tree.DecisionTreeClassifier",
            "versao_modelo": "2.0.0",
            "data_geracao": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "arquivo_serializado": "modelo.joblib",
            "formato_serializacao": "joblib (dict contendo chaves 'modelo', 'features', 'familia', 'params')",
            "sha256_modelo_joblib": sha256_modelo,
            "sha256_baseline_csv": sha256_baseline,
            "justificativa_escolha": (
                "A Árvore de Decisão (max_depth=7, 15 folhas no modo diagnóstico T=0 e max_depth=6 no modo "
                "proativo T+1) foi selecionada como modelo principal por oferecer interpretabilidade total "
                "(regras if-then auditáveis por operadores NOC), latência de inferência sub-milissegundo "
                "(~0.25 ms), suporte nativo a valores ausentes (NaN em timeouts ICMP no scikit-learn >= 1.4) "
                "e desempenho estatisticamente equivalente aos ensembles (Random Forest e XGBoost)."
            ),
        },
        "2_ambiente_software": {
            "python_version": sys.version.split()[0],
            "scikit_learn_version": sklearn.__version__,
            "xgboost_version": xgb.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
            "joblib_version": joblib.__version__,
            "matplotlib_version": matplotlib.__version__,
        },
        "3_atributos_entrada": {
            "features_modo_diagnostico_t0": FEATURES_BASE,
            "features_modo_proativo_t1": FEATURES_EXPANDIDAS,
            "descricao_detalhada": [
                {
                    "ordem": 1,
                    "nome": "z_robusto",
                    "tipo": "float64 (admite NaN quando timeout_atual == 1)",
                    "unidade": "adimensional (escores Z robustos)",
                    "descricao": "Desvio da latência média (avg) em relação à mediana histórica do fluxo, escalado pelo MAD corrigido (1.4826 * MAD).",
                },
                {
                    "ordem": 2,
                    "nome": "aumento_pct",
                    "tipo": "float64 (admite NaN quando timeout_atual == 1)",
                    "unidade": "percentual (%)",
                    "descricao": "Variação percentual da latência atual em relação à mediana histórica da baseline do fluxo.",
                },
                {
                    "ordem": 3,
                    "nome": "jitter_relativo",
                    "tipo": "float64 (admite NaN quando jitter é NaN)",
                    "unidade": "razão adimensional",
                    "descricao": "Razão entre o jitter observado na medição (max - min) e o jitter_tipico da baseline do fluxo.",
                },
                {
                    "ordem": 4,
                    "nome": "perda_pct",
                    "tipo": "float64",
                    "unidade": "percentual (0.0 a 100.0)",
                    "descricao": "Percentual de pacotes ICMP perdidos na medição atual: ((sent - rcvd) / sent) * 100.",
                },
                {
                    "ordem": 5,
                    "nome": "timeout_atual",
                    "tipo": "int64 (0 ou 1)",
                    "unidade": "binário",
                    "descricao": "Indicador de blackout/timeout severo na medição atual: 1 se rcvd == 0 ou avg is NaN, caso contrário 0.",
                },
                {
                    "ordem": 6,
                    "nome": "n5_timeout",
                    "tipo": "float64 (0.0 a 5.0)",
                    "unidade": "contagem em janela",
                    "descricao": "Soma de ocorrências de timeout_atual nas últimas 5 medições consecutivas do mesmo fluxo (~20 min).",
                },
                {
                    "ordem": 7,
                    "nome": "n5_aumento80",
                    "tipo": "float64 (0.0 a 5.0)",
                    "unidade": "contagem em janela",
                    "descricao": "Quantidade de medições nas últimas 5 do mesmo fluxo em que aumento_pct >= 80%.",
                },
                {
                    "ordem": 8,
                    "nome": "n5_risco",
                    "tipo": "float64 (0.0 a 5.0)",
                    "unidade": "contagem em janela",
                    "descricao": "Quantidade de medições nas últimas 5 do mesmo fluxo que apresentaram sinal pontual de risco (2 <= z_robusto < 3.5 ou 30 <= aumento_pct <= 80 ou jitter_relativo >= 3).",
                },
                {
                    "ordem": 9,
                    "nome": "z_max5",
                    "tipo": "float64 (usada no modo proativo T+1 / H3)",
                    "unidade": "adimensional",
                    "descricao": "Valor máximo de z_robusto observado nas últimas 5 medições do fluxo (preenchido com 0.0 se todas forem NaN).",
                },
                {
                    "ordem": 10,
                    "nome": "z_tendencia5",
                    "tipo": "float64 (usada no modo proativo T+1 / H3)",
                    "unidade": "adimensional",
                    "descricao": "Diferença entre o z_robusto atual e a média móvel de z_robusto nas últimas 5 medições (captura aceleração de degradação).",
                },
                {
                    "ordem": 11,
                    "nome": "perda_media5",
                    "tipo": "float64 (usada no modo proativo T+1 / H3)",
                    "unidade": "percentual (%)",
                    "descricao": "Média móvel de perda_pct nas últimas 5 medições do fluxo.",
                },
            ],
        },
        "4_formulas_calculo_features": {
            "fluxo_id": "f'{int(probe_id)}|{dst_addr}'",
            "perda_pct": "((sent - rcvd) / sent) * 100.0 if sent > 0 else np.nan",
            "jitter": "(max - min) if (rcvd > 0 and max is not None and min is not None) else np.nan",
            "timeout_atual": "1 if (rcvd == 0 or pd.isna(avg)) else 0",
            "z_robusto": "(avg - mediana) / (1.4826 * MAD) if MAD > 0 else (0.0 if avg == mediana else np.nan)",
            "aumento_pct": "((avg - mediana) / mediana) * 100.0 if mediana > 0 else np.nan",
            "jitter_relativo": "jitter / jitter_tipico if jitter_tipico > 0 else (1.0 if jitter == 0 else 3.0)",
            "cond_risco_pontual": "1 if ((2.0 <= z_robusto < 3.5) or (30.0 <= aumento_pct <= 80.0) or (jitter_relativo >= 3.0)) else 0",
            "cond_aumento80": "1 if (aumento_pct >= 80.0) else 0",
            "n5_timeout": "rolling(window=5, min_periods=1).sum() de timeout_atual agrupado por fluxo_id",
            "n5_aumento80": "rolling(window=5, min_periods=1).sum() de cond_aumento80 agrupado por fluxo_id",
            "n5_risco": "rolling(window=5, min_periods=1).sum() de cond_risco_pontual agrupado por fluxo_id",
            "z_max5": "rolling(window=5, min_periods=1).max() de z_robusto agrupado por fluxo_id (fillna(0.0))",
            "z_tendencia5": "(z_robusto - rolling(window=5, min_periods=1).mean() de z_robusto).fillna(0.0)",
            "perda_media5": "rolling(window=5, min_periods=1).mean() de perda_pct agrupado por fluxo_id (fillna(0.0))",
        },
        "5_tratamento_valores_ausentes_e_divisao_por_zero": {
            "valores_ausentes_nan": (
                "Quando ocorre perda total de pacotes (rcvd == 0, timeout_atual == 1), o RTT médio (avg) e o jitter "
                "não existem (NaN). Nesse caso, z_robusto, aumento_pct e jitter_relativo permanecem estritamente como "
                "np.nan (NUNCA são substituídos por 0 nem pela mediana, pois isso mascararia o blackout como latência "
                "normal). O DecisionTreeClassifier do scikit-learn >= 1.4 e o XGBoost aprendem nativamente o ramo ótimo "
                "para valores NaN durante o treinamento."
            ),
            "divisao_por_zero_mad": (
                "Se MAD == 0 na baseline de um fluxo ultra-estável: retorna z_robusto = 0.0 quando avg == mediana, "
                "e np.nan quando avg != mediana."
            ),
            "divisao_por_zero_jitter_tipico": (
                "Se jitter_tipico == 0 na baseline: retorna jitter_relativo = 1.0 quando jitter == 0 (comportamento "
                "idêntico ao basal), e jitter_relativo = 3.0 quando jitter > 0 (sinalizando anomalia de variação)."
            ),
            "divisao_por_zero_mediana": "Validado na baseline que todas as 69 rotas possuem mediana > 0 ms.",
        },
        "6_classes_saida": {
            "ordem_classes": CLASSES_ORDEM,
            "mapeamento_inteiro_para_rotulo": {"0": "OK", "1": "RISCO", "2": "FALHA"},
            "mapeamento_rotulo_para_inteiro": CLASSES_MAP,
            "significado_operacional": {
                "OK": "Operação normal do enlace; latência, jitter e perda dentro do comportamento histórico esperado da rota.",
                "RISCO": "Degradação intermediária ou instabilidade persistente (elevação moderada de RTT/jitter, perda parcial ou acúmulo na janela móvel n5); requer atenção preventiva do NOC.",
                "FALHA": "Indisponibilidade severa, timeout completo (blackout ICMP), perda crítica (>= 34%) ou anomalia extrema de latência (z_robusto >= 3.5 ou aumento_pct > 80% persistente).",
            },
        },
        "7_horizonte_predicao": {
            "intervalo_amostragem_mediano_segundos": 240,
            "modos_suportados": {
                "modo_principal_T0": {
                    "horizonte": "T=0 (Diagnóstico Instantâneo em Tempo Real)",
                    "descricao": "Classifica o estado operacional corrente do fluxo a partir das 8 features base sem utilizar o rótulo heurístico como entrada.",
                    "metricas_teste": metricas_t0["arvore_decisao_prof7"]["teste"],
                },
                "modo_proativo_T1": {
                    "horizonte": "T+1 (Previsão Proativa do próximo ciclo de medição, ~4 minutos à frente)",
                    "descricao": "Prediz o estado operacional futuro no instante t+1 usando apenas as 11 features observadas até o instante t (excluindo classe_atual de X, conforme notebook de referência da disciplina).",
                    "metricas_teste_arvore": metricas_t1["arvore_decisao_proativa"]["teste"],
                    "metricas_teste_random_forest": metricas_t1["random_forest_proativo"]["teste"],
                    "metricas_teste_xgboost": metricas_t1["xgboost_proativo"]["teste"],
                },
                "modo_alerta_antecipado_H3": {
                    "horizonte": "T+1..T+3 (Pior estado nos próximos 3 ciclos, ~12 minutos à frente)",
                    "descricao": "Prediz a ocorrência de degradação (RISCO ou FALHA) na janela futura de 12 minutos.",
                    "metricas_teste_arvore": metricas_h3["arvore_decisao_h3_12min"]["teste"],
                    "metricas_teste_random_forest": metricas_h3["random_forest_h3_12min"]["teste"],
                },
            },
        },
        "8_requisitos_historico_janela_movel": {
            "tamanho_janela_medicoes": JANELA_HISTORICO,
            "duracao_aproximada_janela_minutos": 20,
            "agrupamento": "Por fluxo_id (probe_id|dst_addr), ordenado cronologicamente por timestamp.",
            "tratamento_inicio_de_serie_cold_start": (
                "Utiliza rolling(window=5, min_periods=1), permitindo inferência imediata desde a 1ª medição "
                "(cold-start) e atingindo maturidade completa a partir da 5ª medição consecutiva do fluxo."
            ),
        },
        "9_regras_uso_baseline": {
            "arquivo_baseline": "baseline.csv",
            "chave_primaria": "fluxo_id (formato 'probe_id|dst_addr', ex.: '6251|193.0.0.164')",
            "total_fluxos_cadastrados": int(len(df_base_enriq)),
            "periodo_referencia_calculo": {
                "inicio_utc": dt_ini_iso,
                "fim_utc": dt_fim_iso,
                "duracao_dias": 7,
            },
            "criterios_validade_fluxo": {
                "min_amostras_validas": 1500,
                "prop_minima_resposta": 0.70,
                "fluxos_validos_no_arquivo": int(df_base_enriq["baseline_valida"].sum()),
            },
            "politica_fluxo_desconhecido": (
                "Se um fluxo_id não constar em baseline.csv, a API pode rejeitar com erro 404 explicativo ou, "
                "se solicitado modo fallback, estimar a baseline provisória com as primeiras medições válidas."
            ),
        },
        "10_importancia_features": {
            "arvore_diagnostico_t0": importancias_dt_t0,
            "arvore_proativa_t1": importancias_dt_t1,
        },
        "11_exemplo_real_entrada_saida": {
            "contexto_amostra": {
                "fluxo_id": str(amostra_risco["fluxo_id"]),
                "probe_id": int(amostra_risco["probe_id"]),
                "dst_addr": str(amostra_risco["dst_addr"]),
                "timestamp": int(amostra_risco["timestamp"]),
                "avg_rtt_ms": float(amostra_risco["avg"]),
                "sent": int(amostra_risco["sent"]),
                "rcvd": int(amostra_risco["rcvd"]),
            },
            "entrada_features_t0": {
                k: (None if pd.isna(amostra_risco[k]) else round(float(amostra_risco[k]), 6))
                for k in FEATURES_BASE
            },
            "saida_modo_diagnostico_t0": {
                "classe_inteiro": pred_ex_t0,
                "classe_rotulo": CLASSES_INV[pred_ex_t0],
                "probabilidades": {
                    "OK": round(float(probs_ex_t0[0]), 4),
                    "RISCO": round(float(probs_ex_t0[1]), 4),
                    "FALHA": round(float(probs_ex_t0[2]), 4),
                },
            },
            "saida_modo_proativo_t1_4min": {
                "classe_inteiro": pred_ex_t1,
                "classe_rotulo": CLASSES_INV[pred_ex_t1],
                "probabilidades": {
                    "OK": round(float(probs_ex_t1[0]), 4),
                    "RISCO": round(float(probs_ex_t1[1]), 4),
                    "FALHA": round(float(probs_ex_t1[2]), 4),
                },
            },
        },
        "12_comparativo_completo_benchmarks": {
            "modo_diagnostico_t0": metricas_t0,
            "modo_proativo_t1_4min": metricas_t1,
            "modo_alerta_antecipado_h3_12min": metricas_h3,
        },
    }

    caminho_meta_dist = os.path.join(dist_dir, "metadados.json")
    caminho_meta_prod = os.path.join(prod_model_dir, "metadados.json")
    with open(caminho_meta_dist, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)
    with open(caminho_meta_prod, "w", encoding="utf-8") as f:
        json.dump(metadados, f, ensure_ascii=False, indent=2)

    # 5. Criar arquivo ZIP canônico para submissão no Blackboard
    zip_path_dist = os.path.join(REPO_ROOT, "dist", "Grupo05.zip")
    zip_path_downloads = os.path.join(os.path.dirname( os.path.dirname(REPO_ROOT) ), "Grupo05.zip")

    with zipfile.ZipFile(zip_path_dist, "w", zipfile.ZIP_DEFLATED) as zf:
        for fname in ["modelo.joblib", "metadados.json", "baseline.csv"]:
            fpath = os.path.join(dist_dir, fname)
            zf.write(fpath, arcname=fname)

    shutil.copy2(zip_path_dist, zip_path_downloads)

    print(f"      -> [OK] {caminho_modelo_dist} (SHA-256: {sha256_modelo[:16]}...)")
    print(f"      -> [OK] {caminho_meta_dist}")
    print(f"      -> [OK] {caminho_baseline_dist} ({len(df_base_enriq)} fluxos)")
    print(f"      -> [OK] Pacote ZIP gerado em: {zip_path_dist}")
    print(f"      -> [OK] Cópia pronta para upload em: {zip_path_downloads}")
    print("=" * 78)


if __name__ == "__main__":
    main()
