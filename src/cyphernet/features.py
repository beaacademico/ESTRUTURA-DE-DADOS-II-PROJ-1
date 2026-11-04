"""Calculo das features do CypherNet: fonte unica da verdade.

As formulas aqui reproduzem EXATAMENTE as do notebook 02 (baseline e rotulagem),
para que treino, API, scripts e pacote do Blackboard usem a mesma conta.
O teste de paridade (scripts/validar_paridade_features.py) confere isso contra
o dataset `dataset_rotulado_B_split.csv`.

Convencao: valor ausente e sempre float('nan'), nunca zero.
"""
from __future__ import annotations

import math
from collections import deque
from typing import Iterable, Optional

import numpy as np
import pandas as pd

JANELA = 5                       # medicoes na janela movel (inclui a atual)
INTERVALO_AMOSTRAGEM_S = 240     # as ancoras do RIPE Atlas medem a cada 4 min
CLASSES = ("OK", "RISCO", "FALHA")

FEATURES_BASE = [
    "z_robusto", "aumento_pct", "jitter_relativo", "perda_pct",
    "timeout_atual", "n5_timeout", "n5_aumento80", "n5_risco",
]
FEATURES_TENDENCIA = ["z_max5", "z_tendencia5", "perda_media5"]
FEATURES = FEATURES_BASE + FEATURES_TENDENCIA

NAN = float("nan")


def ausente(x) -> bool:
    """True para None ou NaN."""
    return x is None or x != x


def como_float(x) -> float:
    return NAN if ausente(x) else float(x)


def metricas_pontuais(avg, jitter_ms, mediana, mad, jitter_tipico):
    """z_robusto, aumento_pct e jitter_relativo de UMA medicao (notebook 02, celula 8)."""
    avg, jitter_ms = como_float(avg), como_float(jitter_ms)
    z = aumento = jr = NAN
    if not ausente(avg) and avg > 0:
        if mad > 0:
            z = (avg - mediana) / (1.4826 * mad)
        elif avg == mediana:
            z = 0.0
        else:
            z = (avg - mediana) / 1.0          # fallback do notebook quando MAD == 0
        aumento = ((avg - mediana) / mediana) * 100.0
    if not ausente(jitter_ms) and jitter_ms > 0:
        jr = jitter_ms / jitter_tipico if jitter_tipico > 0 else 3.0
    elif not ausente(jitter_ms) and jitter_ms == 0 and jitter_tipico == 0:
        jr = 1.0
    return z, aumento, jr


def timeout_atual(perda_pct: float) -> float:
    return 1.0 if perda_pct >= 100.0 else 0.0


def cond_risco_pontual(z: float, aumento: float, jr: float) -> float:
    """Condicao pontual de risco (NaN compara como falso, igual ao pandas)."""
    return 1.0 if ((2 <= z < 3.5) or (30 <= aumento <= 80) or (jr >= 3)) else 0.0


def rotular_regra(perda_pct, n5_timeout, z, n5_aumento80, cond_risco, n5_risco) -> str:
    """Regra fixa de rotulagem da Tarefa 2: define a classe do instante ATUAL."""
    if perda_pct >= 10:
        return "FALHA"
    if n5_timeout >= 3:
        return "FALHA"
    if not ausente(z) and z >= 3.5:
        return "FALHA"
    if n5_aumento80 >= 2:
        return "FALHA"
    if cond_risco == 1 and n5_risco >= 2:
        return "RISCO"
    return "OK"


def inclinacao(valores) -> float:
    """Inclinacao (minimos quadrados) de z ao longo da janela; NaN com menos de 3 pontos validos."""
    v = np.asarray(valores, dtype=float)
    ok = ~np.isnan(v)
    if ok.sum() < 3:
        return NAN
    x = np.arange(len(v), dtype=float)[ok]
    y = v[ok]
    xm = x.mean()
    return float(((x - xm) * (y - y.mean())).sum() / ((x - xm) ** 2).sum())


class JanelaFluxo:
    """Memoria curta de UM fluxo: as ultimas JANELA medicoes."""

    def __init__(self, tamanho: int = JANELA):
        self._h: deque = deque(maxlen=tamanho)

    def __len__(self):
        return len(self._h)

    def adicionar(self, z, aumento, perda_pct, timeout, cond):
        self._h.append({
            "timeout": timeout,
            "aum80": 1.0 if (not ausente(aumento) and aumento > 80) else 0.0,
            "cond": cond, "z": z, "perda": perda_pct,
        })

    def agregados(self) -> dict:
        zs = [h["z"] for h in self._h]
        validos = [z for z in zs if not ausente(z)]
        return {
            "n5_timeout": float(sum(h["timeout"] for h in self._h)),
            "n5_aumento80": float(sum(h["aum80"] for h in self._h)),
            "n5_risco": float(sum(h["cond"] for h in self._h)),
            "z_max5": max(validos) if validos else NAN,
            "z_tendencia5": inclinacao(zs),
            "perda_media5": float(np.mean([h["perda"] for h in self._h])),
        }


def processar_medicao(medicao: dict, baseline: dict, janela: JanelaFluxo) -> dict:
    """Atualiza a janela do fluxo com a medicao e devolve todas as features.

    medicao  : {"rtt_ms": float|None, "perda_pct": float, "jitter_ms": float|None}
    baseline : {"mediana": float, "MAD": float, "jitter_tipico": float}
    """
    perda = float(medicao.get("perda_pct", 0.0))
    z, aumento, jr = metricas_pontuais(
        medicao.get("rtt_ms"), medicao.get("jitter_ms"),
        float(baseline["mediana"]), float(baseline["MAD"]), float(baseline["jitter_tipico"]),
    )
    to = timeout_atual(perda)
    cond = cond_risco_pontual(z, aumento, jr)
    janela.adicionar(z, aumento, perda, to, cond)
    agg = janela.agregados()
    feats = {
        "z_robusto": z, "aumento_pct": aumento, "jitter_relativo": jr,
        "perda_pct": perda, "timeout_atual": to, **agg,
    }
    feats["classe_atual_regra"] = rotular_regra(
        perda, agg["n5_timeout"], z, agg["n5_aumento80"], cond, agg["n5_risco"])
    return feats


def vetor(feats: dict, ordem: Iterable[str] = FEATURES) -> pd.DataFrame:
    """DataFrame de 1 linha na ORDEM de treino (a ordem importa para o modelo)."""
    return pd.DataFrame([{k: feats[k] for k in ordem}])[list(ordem)]


def adicionar_tendencias(df: pd.DataFrame) -> pd.DataFrame:
    """Versao vetorizada das features de tendencia. df: ordenado por fluxo_id, timestamp."""
    df = df.reset_index(drop=True)
    g = df.groupby("fluxo_id", sort=False)

    def _roll(col, metodo, **kw):
        r = g[col].rolling(JANELA, min_periods=1)
        out = getattr(r, metodo)(**kw)
        return out.reset_index(level=0, drop=True)

    df["z_max5"] = _roll("z_robusto", "max")
    df["perda_media5"] = _roll("perda_pct", "mean")
    df["z_tendencia5"] = _roll("z_robusto", "apply", func=inclinacao, raw=True)
    return df
