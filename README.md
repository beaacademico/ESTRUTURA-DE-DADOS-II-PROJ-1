# 🌐 Projeto de Monitoramento de Redes

Projeto desenvolvido para analisar e comparar duas fontes de dados para monitoramento de redes, e agora implementando um preditor ativo de degradação:

* 📊 **Dataset Real — Network Anomaly Dataset** (Análise Histórica)
* 🌍 **API RIPE Atlas** (Pipeline Oficial Escolhido)

## 🎯 Objetivo

Avaliar as vantagens, limitações e possibilidades de utilização de um dataset real e da API RIPE Atlas para a coleta e análise de dados de redes, culminando na construção de uma Árvore de Decisão para classificar rotas em **OK, RISCO e FALHA**.

---

## 🚀 Arquitetura e Pipeline Atual (Fase 2)

Após a definição pela **API RIPE Atlas**, o repositório foi reestruturado sob uma metodologia Ágil (Scrum) para comportar o pipeline profissional de dados:

* 📁 **`config/`**: Arquivos de parametrização (janelas de tempo, ids de medição e timeouts).
* 📁 **`data/`**: Separação estrita entre dados brutos (`raw/`), transformados (`interim/`) e rotulados (`processed/`).
* 📁 **`notebooks/`**: 
  * `01_coleta_bruta`: Loop de requisição HTTP e extração de *jitter* e *perda_pct*.
  * `02_baseline_rotulagem`: Motor matemático que usa **Mediana e MAD** (Median Absolute Deviation) para calcular a normalidade de uma rota e aplicar a rotulagem em cascata baseada no `z_robusto`.
* 📁 **`tarefas/`**: Diários de bordo e relatórios de qualidade em Markdown.
* 📁 **`legado/`**: Arquivos e pesquisas da Fase 1 do projeto.

---

## 📊 Pesquisa Inicial: Dataset Real

**Network Anomaly Dataset — Alberto del Rio**

* Formato: CSV
* 1.001 registros | 21 colunas
* Contém **latência, perda de pacotes e jitter**
* Possui indicadores de anomalias
* Licença: Apache 2.0
* Dados coletados em ambiente controlado com roteadores virtuais Cisco IOS-XRv

🔗 [Dataset no Kaggle](https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset)

> ⚠️ O dataset utiliza classificação binária de anomalias, enquanto o projeto final prevê os estados **OK, RISCO e FALHA**.

## 🌍 Pesquisa Inicial: API RIPE Atlas

O **RIPE Atlas** permite realizar medições reais de rede utilizando probes distribuídos geograficamente.

Possibilita:
* 📡 Criar novas medições
* 🌎 Coletar dados de diferentes regiões
* 🔄 Realizar medições recorrentes
* 📈 Obter dados atualizados
* ⚙️ Configurar diferentes parâmetros de coleta

🔗 [Documentação da API RIPE Atlas](https://atlas.ripe.net/docs/apis/rest-api-manual/introduction/)

## ⚖️ Comparação da Fase 1

| Critério             | Dataset Real | RIPE Atlas    |
| -------------------- | ------------ | ------------- |
| Controle da coleta   | Baixo        | Alto          |
| Cobertura geográfica | Baixa        | Alta          |
| Complexidade         | Baixa        | Média/Alta    |
| Dados disponíveis    | Imediatos    | Após medições |

### ✅ Recomendação

Para o desenvolvimento prático das Tarefas de 1 a 5, a **API RIPE Atlas (Anchoring Mesh)** foi escolhida por permitir **medições atuais, configuráveis e distribuídas geograficamente**.

---

## 👥 Integrantes e Contribuições

| Integrante                     | Contribuição Original | Contribuição Fase Atual (Scrum) |
| ------------------------------ | --------------------- | ------------------------------- |
| **Breno Brasil de Souza**      | Pesquisa Seção 2 (Dataset) | **Scrum Master**: Organização do pipeline Git, pastas `raw/interim` e execução. |
| **Beatriz Gonçalves da Silva** | Seção 7 e Commits Iniciais | **Analista**: Parametrização de janelas (14 dias) no arquivo `config.yaml`. |
| **Enzo Moraes Sousa**          | Seção 4 e Junção das etapas | **QA**: Validação do dataset final e relatórios de qualidade. |
| **Natsumi Goto**               | Seções 1, 5 e 6 | **Dev**: Requisições HTTP fatiadas para a API do RIPE (Períodos A e B). |
| **Pedro Viana da Silva**       | Pesquisa Seção 3 (RIPE) | **Eng. Dados**: Criação do DataFrame, `fluxos_id` e extração de `jitter/perda`. |
| **Vitória Alessandra das Neves**| Tabela de Decisões e IDs | **Analista Redes**: Pesquisa de Rotas do Anchoring Mesh (Caminhos curtos e longos). |

---

## 📚 Fontes

* [Network Anomaly Dataset — Kaggle](https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset)
* [RIPE Atlas — Documentação](https://atlas.ripe.net/docs/apis/rest-api-manual/introduction/)
* [RIPE Atlas — Creating Measurements](https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/)
* [RIPE Atlas — Authentication](https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/)
