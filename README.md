# 👁️‍🗨️ CypherNet: Vigia de Redes — Diagnóstico e Predição Proativa de Degradação com RIPE Atlas

[![Status: Em Produção](https://img.shields.io/badge/Status-Mostra%20de%20Tecnologia%202026-10b981.svg)](#)
[![Modelo Principal: Árvore de Decisão](https://img.shields.io/badge/Modelo%20Canônico-Árvore%20de%20Decisão%20(Prof.%207)-00f2fe.svg)](#)
[![Artigo Técnico](https://img.shields.io/badge/Artigo-GitHub%20Pages-blue.svg)](https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/)
[![Página da Mostra](https://img.shields.io/badge/Feira-CypherNet%20Showcase-0f766e.svg)](https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/feira/)
[![Disciplina](https://img.shields.io/badge/Disciplina-Estruturas%20de%20Dados%20II%20(Grupo%2005)-orange.svg)](#)

**CypherNet: Vigia de Redes** é um sistema de observabilidade e aprendizado de máquina para detecção em tempo real ($T=0$) e predição proativa ($T+1 = +4\text{ min}$ e $H3 = +12\text{ min}$) de degradação e falhas em enlaces de Internet geograficamente distribuídos, utilizando telemetria ativa do **RIPE Atlas (Anchoring Mesh, `msm_id=9333345`)** e normalização estatística robusta por fluxo (`Mediana` e `1.4826 * MAD`).

---

## 🎯 Objetivo do Projeto

Classificar e antecipar o estado operacional de rotas de rede em **OK, RISCO e FALHA** sem depender de limiares fixos de RTT em milissegundos e sem vazar variáveis de identidade topológica (como IP, ASN ou país).

Cada fluxo (`probe_id|dst_addr`) é avaliado contra a sua própria **baseline histórica de 7 dias** (`06/09/2026` a `13/09/2026`), permitindo isolar tanto *blackouts* severos quanto degradações progressivas (*Gray Failures*) em **173.674 medições reais** de **69 rotas globais**.

---

## 🏗️ Arquitetura do Repositório

```text
ESTRUTURA-DE-DADOS-II-PROJ-1/
├── src/cyphernet/               # Fonte única da verdade (Engenharia de Features e Janela Móvel)
│   ├── __init__.py
│   └── features.py              # Fórmulas exatas (1.4826*MAD, preservação de NaN, JanelaFluxo)
├── dist/                        # Pacote Canônico para submissão no Blackboard
│   ├── Grupo05/                 # modelo.joblib, metadados.json e baseline.csv
│   └── Grupo05.zip              # Arquivo ZIP validado pronto para entrega (27.9 KB)
├── producao/                    # Microsserviço REST & Dashboard Operacional NOC
│   ├── modelo/                  # Artefatos ativos em produção (modelo_final.joblib, metadados.json, baseline.csv)
│   └── app/
│       ├── server.py            # API Flask (/api/saude, /api/modelo, /api/previsoes, /api/diagnosticar)
│       └── templates/index.html # Painel interativo com simulador T=0 / T+1 e stream RIPE Atlas ao vivo
├── feira/                       # Página oficial da Mostra de Tecnologia (CypherNet Showcase)
│   └── index.html               # Relatório interativo e simulador publicado no GitHub Pages
├── docs/                        # Documentação técnica, artigo web e guias de defesa
│   ├── index.html               # Artigo Técnico completo
│   ├── logo_nomedoprojeto.png   # Logotipo oficial 500x500 px (CypherNet: Vigia de Redes)
│   ├── INSTRUCOES_INSCRICAO_BLACKBOARD.md # Textos oficiais de inscrição na Mostra
│   └── GUIA_ARGUICAO_INDIVIDUAL_05_11.md  # Guia completo para a arguição individual (05/11)
├── scripts/                     # Automação de treino, auditoria de paridade e testes de estresse
│   ├── validar_paridade_features.py       # Verifica 0 divergências nas 173.674 linhas do dataset
│   ├── treinar_e_empacotar_blackboard.py  # Treina modelos T=0, T+1 e H3 e gera dist/Grupo05.zip
│   ├── validar_entrega_blackboard_e_api.py# Suite de testes end-to-end do ZIP e das rotas Flask
│   ├── 01_teste_estresse_ruido.py         # Simulação de Data Drift (ruído estocástico)
│   ├── 02_simulador_producao_tempo_real.py# Streaming com buffer circular de janelas
│   └── 03_teste_dados_reais_hoje.py       # Consulta ao vivo à API global do RIPE Atlas
├── notebooks/                   # Notebooks do pipeline (Coleta, Baseline, Árvore e Comparativo)
├── data/processed/              # Dataset rotulado com split temporal 50/20/30 e baseline por fluxo
└── requirements.txt             # Dependências padronizadas do projeto
```

---

## 📊 Resultados Experimentais: Diagnóstico ($T=0$) vs. Horizonte Proativo ($T+1$ e $H3$)

Avaliação sobre o conjunto de **Teste Temporal (52.149 medições)**, comparando a **Árvore de Decisão** (modelo principal recomendado pela transparência de suas regras `SE-ENTÃO`) com **Random Forest** e **XGBoost**:

| Modo Operacional | Modelo | Accuracy (Teste) | F1 Macro (Validação) | F1 Macro (Teste) | Recall `FALHA` (Teste) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **$T=0$ (Diagnóstico Instantâneo — 8 features)** | **Árvore de Decisão (`d=7`, 16 folhas)** | **100,00%** | **0,9999** | **1,0000** | **100,00%** |
| $T=0$ (Diagnóstico Instantâneo — 8 features) | Random Forest (`100` árvores, `d=7`) | 99,99% | 0,9996 | 0,9997 | 99,93% |
| $T=0$ (Diagnóstico Instantâneo — 8 features) | XGBoost (`100` árvores, `d=4`) | 99,90% | 0,9954 | 0,9956 | 99,87% |
| **$T+1$ (Previsão Proativa +4 min — 11 features)** | **Árvore Proativa (`d=8`, pesos `1:2:3`)** | **88,38%** | **0,5782** | **0,5699** | **31,86%** |
| $T+1$ (Previsão Proativa +4 min — 11 features) | Random Forest Proativo (`d=10`, pesos `1:2:3`) | 88,80% | 0,5873 | 0,5824 | 33,85% |
| $T+1$ (Previsão Proativa +4 min — 11 features) | XGBoost Proativo (`d=5`, `lr=0.05`) | 89,14% | 0,5788 | 0,5748 | 28,48% |
| **$H3$ (Alerta Antecipado +12 min — 11 features)** | **Árvore Alerta (`d=7`, pesos `1:1.5:2`)** | **72,80%** | **0,5243** | **0,5113** | **21,92%** |

---

## ⚡ Como Executar e Validar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Servidor Flask e Dashboard Operacional NOC
```bash
python producao/app/server.py
```
Acesse no navegador: **`http://127.0.0.1:5000`**
* Endpoints REST disponíveis:
  * `GET /api/saude` — *Healthcheck* e verificação SHA-256 do modelo
  * `GET /api/modelo` — Metadados de governança e atributos do pacote `modelo.joblib`
  * `GET /api/fluxos` — Catálogo das 69 rotas e baselines históricas
  * `POST /api/diagnosticar` — Diagnóstico instantâneo ($T=0$) + previsão proativa ($T+1$ e $H3$)
  * `POST /api/previsoes` e `GET /api/previsoes` — Contrato OpenAPI canônico do Edital Final (suporta envio unitário ou em lote e consulta ao histórico de previsões)
  * `POST /api/coletar_ripe_ao_vivo` — Coleta e classificação ao vivo da API do RIPE Atlas

### 3. Executar a Suite de Auditoria e Validação Automatizada
```bash
# Verifica 100% de paridade matemática das features nas 173.674 linhas do dataset
python scripts/validar_paridade_features.py

# Valida o pacote dist/Grupo05.zip (descompactação isolada + NaN nativo) e todos os endpoints da API
python scripts/validar_entrega_blackboard_e_api.py
```

---

## 👥 Equipe — Grupo 05

| Integrante | RA | Papel Técnico no Projeto |
| :--- | :---: | :--- |
| **Beatriz Gonçalves da Silva** | 2400909 | Parametrização de janelas, documentação científica e publicação GitHub Pages. |
| **Breno Brasil de Souza** | 2401483 | **Scrum Master**: Modelagem preditiva, engenharia MLOps, API Flask e empacotamento Blackboard. |
| **Enzo Moraes Sousa** | 2401685 | **QA**: Auditoria estatística do dataset, validação de paridade e métricas comparativas. |
| **Natsumi Goto** | 2401999 | Coleta fatiada RIPE Atlas, análise de árvore de decisão e desenvolvimento da página da Mostra (`feira/`). |
| **Pedro Viana da Silva** | 2400956 | Engenharia de atributos relativos, cálculo de jitter/perda e estruturação dos DataFrames. |
| **Vitória Alessandra das Neves** | 2401781 | Mapeamento da Anchoring Mesh, análise de rotas e construção da baseline histórica. |

---

📖 **Preparação para a Arguição Individual (05/11):** consulte [`docs/GUIA_ARGUICAO_INDIVIDUAL_05_11.md`](docs/GUIA_ARGUICAO_INDIVIDUAL_05_11.md).
