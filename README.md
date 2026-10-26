# 🌐 Preditor de Degradação de Redes com RTT Normalizado

[![Status: Em Produção](https://img.shields.io/badge/Status-Produção%20%26%20Evolução-10b981.svg)](#)
[![Modelo: XGBoost](https://img.shields.io/badge/Campeão-XGBoost%20(372%20KB)-00f2fe.svg)](#)
[![Artigo Técnico](https://img.shields.io/badge/Artigo-GitHub%20Pages-blue.svg)](https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/)
[![Licença: Acadêmica](https://img.shields.io/badge/Disciplina-Estruturas%20de%20Dados%20II-orange.svg)](#)

Sistema de observabilidade e Inteligência Artificial para classificação e predição de degradação em caminhos de rede geograficamente distribuídos, utilizando medições ativas do **RIPE Atlas (Anchoring Mesh)** e variáveis relativas adimensionais (Mediana e MAD).

---

## 🎯 Objetivo do Projeto

Detectar e antecipar falhas de rede nos estados **OK, RISCO e FALHA** sem recorrer a limiares absolutos de latência e sem aprender atalhos geográficos (como IPs, ASNs ou países). 

O sistema avalia cada rota contra a sua própria régua de normalidade histórica (Período A - 14 dias), isolando anomalias sutis conhecidas na literatura de engenharia de redes como **Gray Failures** (*falhas cinzentas e parciais que monitoramentos tradicionais não captam*).

---

## 🏗️ Arquitetura Reorganizada do Repositório

```text
ESTRUTURA-DE-DADOS-II-PROJ-1/
├── config/                      # Configurações de coleta e parâmetros (config.yaml)
├── data/                        # Esteira de dados segregada
│   ├── raw/                     # Medições brutas JSON do RIPE Atlas (Períodos A e B)
│   ├── interim/                 # Tabelas intermediárias processadas
│   └── processed/               # Baseline histórica (Mediana/MAD) e Dataset Rotulado Split
├── notebooks/                   # Pipeline completo de Ciência de Dados
│   ├── 01_coleta_bruta.ipynb    # Ingestão via API RIPE Atlas
│   ├── 02_baseline_rotulagem.ipynb # Engenharia de features e split temporal 50/20/30
│   ├── 03_arvore_inicial.ipynb  # Árvore inicial rasa (max_depth=4)
│   └── 04_comparacao_modelos.ipynb # GridSearchCV, Random Forest vs XGBoost
├── producao/                    # Ambiente operacional de microsserviço
│   ├── modelo/                  # Artefato serializado oficial (modelo_final.joblib - 372 KB)
│   └── app/                     # Servidor de Produção REST & Dashboard NOC
│       ├── server.py            # Backend Flask com SHA-256 e endpoints /api/saude
│       └── templates/index.html # Frontend visual de monitoramento interativo
├── scripts/                     # Scripts de teste, estresse e validação ao vivo
│   ├── 01_teste_estresse_ruido.py      # Injeção de ruído e simulação de Data Drift
│   ├── 02_simulador_producao_tempo_real.py # Streaming com buffer circular de janelas
│   └── 03_teste_dados_reais_hoje.py    # Validação ao vivo consultando a API do RIPE
├── docs/                        # Documentação técnica e publicação
│   ├── index.html               # Artigo Técnico Web publicado no GitHub Pages
│   ├── PLANO_DE_MELHORIAS_PROJETO.md # Plano de evolução e auditoria pós-apresentação
│   └── GUIA_APRESENTACAO_BRENO.md    # Roteiro técnico e defesa metodológica
├── tarefas/                     # Relatórios das entregas parciais (Tarefas 1 a 6)
├── legado/                      # Histórico da Fase 1 do projeto
└── requirements.txt             # Dependências padronizadas do ecossistema
```

---

## ⚡ Como Executar em Modo Produção

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Dashboard Operacional (NOC Telecom)
Inicia o servidor de microsserviço na porta `5000` com endpoints REST, healthcheck e playground de diagnóstico:
```bash
python producao/app/server.py
```
Acesse no navegador: **`http://127.0.0.1:5000`**

### 3. Rodar os Scripts de Validação e Estresse
* **Simulação de Data Drift (Ruído de 0% a 50%):**
  ```bash
  python scripts/01_teste_estresse_ruido.py
  ```
* **Simulador de Streaming em Tempo Real (Buffer de Janelas):**
  ```bash
  python scripts/02_simulador_producao_tempo_real.py
  ```
* **Teste com Dados Vivos da API do RIPE Atlas Hoje:**
  ```bash
  python scripts/03_teste_dados_reais_hoje.py
  ```

---

## 📊 Governança e Rastreabilidade de Modelo

| Elemento | Especificação de Produção |
| :--- | :--- |
| **Algoritmo Campeão** | **XGBoost Classifier** (100 estimadores, regularizado) |
| **Tamanho em Disco** | **~372 KB** (`modelo_final.joblib`) |
| **Latência de Inferência** | **< 0,1 milissegundos** por amostra |
| **Variáveis de Entrada** | **8 métricas relativas adimensionais** (sem IP, país ou RTT absoluto) |
| **Integridade Criptográfica**| Hash SHA-256 verificado dinamicamente no boot da API |
| **Healthcheck** | Endpoint `GET /api/saude` (Liveness probe Cloud-Native) |

---

## 👥 Equipe (Grupo 5)

| Integrante | Papel Técnico no Projeto |
| :--- | :--- |
| **Breno Brasil de Souza** | **Scrum Master**: Ajuste da Árvore pelo Erro (Tarefa 4), Pipeline de Reprodutibilidade, Backend Flask e MLOps. |
| **Beatriz Gonçalves da Silva** | **Analista**: Parametrização de janelas (14 dias), Redação da Tarefa 6 e Deploy no GitHub Pages. |
| **Enzo Moraes Sousa** | **QA**: Auditoria do dataset, validação de integridade e relatórios de métricas comparativas. |
| **Natsumi Goto** | **Desenvolvedora**: Ingestão e requisições HTTP fatiadas para a API do RIPE Atlas (Períodos A e B). |
| **Pedro Viana da Silva** | **Engenheiro de Dados**: Extração de métricas relativas, cálculo de jitter e geração dos DataFrames. |
| **Vitória Alessandra das Neves** | **Analista de Redes**: Mapeamento da Anchoring Mesh (rotas curtas e longas) e Baseline (Tarefa 2). |

---

*Para consultar os planos de expansão do modelo com horizonte preditivo (Lead Time de 15 min) e aprendizado sensível a custo, veja [docs/PLANO_DE_MELHORIAS_PROJETO.md](docs/PLANO_DE_MELHORIAS_PROJETO.md).*
