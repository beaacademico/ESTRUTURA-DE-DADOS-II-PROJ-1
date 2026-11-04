"""Teste de paridade: a conta de features do CypherNet reproduz o dataset de treino?

Reprocessa cada medicao do Periodo B EM STREAMING (uma por vez, com a janela
movel por fluxo, exatamente como a API faz) e compara com as colunas ja
gravadas em data/processed/dataset_rotulado_B_split.csv.

Uso:  python scripts/validar_paridade_features.py
Saida: codigo 0 se tudo bate, 1 se houver divergencia.
"""
import os
import sys

import numpy as np
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
from cyphernet import features as F  # noqa: E402

DATASET = os.path.join(RAIZ, "data", "processed", "dataset_rotulado_B_split.csv")
BASELINE = os.path.join(RAIZ, "data", "processed", "baseline_por_fluxo.csv")
TOL = 1e-9


def carregar():
    df = pd.read_csv(DATASET)
    df["fluxo_id"] = df["probe_id"].astype(int).astype(str) + "|" + df["dst_addr"]
    df = df.sort_values(["fluxo_id", "timestamp"]).reset_index(drop=True)
    base = pd.read_csv(BASELINE).set_index("fluxo_id").to_dict("index")
    return df, base


def reprocessar(df, base):
    janelas = {}
    saida = []
    for r in df[["fluxo_id", "avg", "perda_pct", "jitter_ms"]].itertuples(index=False):
        j = janelas.setdefault(r.fluxo_id, F.JanelaFluxo())
        medicao = {"rtt_ms": r.avg, "perda_pct": r.perda_pct, "jitter_ms": r.jitter_ms}
        saida.append(F.processar_medicao(medicao, base[r.fluxo_id], j))
    return pd.DataFrame(saida)


def comparar(nome, esperado, obtido):
    esperado = esperado.to_numpy(dtype=float)
    obtido = obtido.to_numpy(dtype=float)
    ambos_nan = np.isnan(esperado) & np.isnan(obtido)
    um_nan = np.isnan(esperado) ^ np.isnan(obtido)
    dif = np.where(ambos_nan | um_nan, 0.0, np.abs(esperado - obtido))
    ruins = int(um_nan.sum() + (dif > TOL).sum())
    print(f"  {nome:<16} divergencias: {ruins:>6} / {len(esperado)}")
    return ruins


def main():
    df, base = carregar()
    print(f"Medicoes: {len(df)} | fluxos: {df['fluxo_id'].nunique()}")
    novo = reprocessar(df, base)

    total = 0
    print("\nFeatures base (streaming vs colunas do dataset):")
    for col in F.FEATURES_BASE:
        total += comparar(col, df[col], novo[col])

    print("\nClasse atual (regra da Tarefa 2):")
    erros_classe = int((df["classe"].to_numpy() != novo["classe_atual_regra"].to_numpy()).sum())
    print(f"  {'classe':<16} divergencias: {erros_classe:>6} / {len(df)}")
    total += erros_classe

    print("\nFeatures de tendencia (streaming vs versao vetorizada do treino):")
    vet = F.adicionar_tendencias(df.copy())
    for col in F.FEATURES_TENDENCIA:
        total += comparar(col, vet[col], novo[col])

    print()
    if total == 0:
        print("PARIDADE OK: a API e o treino calculam exatamente as mesmas features.")
        return 0
    print(f"FALHA: {total} divergencias.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
