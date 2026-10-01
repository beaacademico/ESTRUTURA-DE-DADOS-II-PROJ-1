# Guia de Transição para a Equipe — Preditor de Redes (Grupo 5)

Este documento foi criado para explicar **exatamente o que mudou, o porquê de cada mudança e como o trabalho de cada um dos 6 integrantes foi adaptado** para atender às exigências do RFC da Profa. Andrea para as Tarefas 2 a 5.

---

## 1. O Problema Central: Por que mudamos a base do projeto?

A professora Andrea deu uma boa nota (3,15) para a **qualidade do código** de ingestão de vocês. No entanto, a estratégia de dados que vocês escolheram (`ID 1001`, `2 horas de coleta`) gerou um beco sem saída matemático para a Tarefa 2. 

**Por que não dava para continuar como estava:**
1. **Medição 1001 (K-Root) é Anycast:** O IP de destino responde de servidores físicos diferentes dependendo de onde o ping sai. É impossível criar um *baseline* estatístico de um caminho se o destino físico muda. O RFC exige o **Anchoring Mesh** (ping entre servidores "Anchors" estáticos da RIPE).
2. **Janela de 2 Horas:** Gerou apenas ~30 pings por sonda. A Tarefa 2 exige um **piso de 1.500 pings válidos** por fluxo para calcular a Mediana e o MAD (Median Absolute Deviation). Sem 1.500 pings, o fluxo é descartado. Por isso, mudamos para o padrão de **14 dias** (7 dias Período A + 7 dias Período B).

---

## 2. O Que Mudou no Trabalho de Cada Integrante?

O trabalho de vocês não foi perdido. Ele foi **reaproveitado, expandido e modularizado**. Veja o impacto individual:

### 👩‍💻 Beatriz Gonçalves (Parâmetros da Consulta)
- **O que você fez:** Definiu no notebook os parâmetros `ID 1001`, `2h`, `CSV` e `timeout 60s`.
- **Como ficou agora:** Seus parâmetros foram promovidos! Em vez de ficarem perdidos no meio do código Python, eles agora vivem no arquivo **`config/config.yaml`**. 
- **O que mudou:** O ID 1001 foi retirado. As 2 horas viraram duas janelas de datas UTC precisas (06/09 a 13/09 para o Período A, e 13/09 a 20/09 para o B). O timeout subiu para 120s por segurança, e o formato CSV foi mantido.

### 👨‍💻 Breno Brasil (Você — Mount do Drive e Pasta Raw)
- **O que você fez:** Montou o Google Drive e criou uma pasta `raw` única.
- **Como ficou agora:** O RFC exige uma estrutura profissional de Git. A sua pasta `raw` evoluiu para uma árvore completa de diretórios local: `data/raw/periodo_a/`, `data/raw/periodo_b/`, `data/interim/` e `data/processed/`. 
- **O que mudou:** Você ainda pode (e deve) usar o Google Drive no Colab, mas agora o código salva os arquivos distribuídos nessas subpastas para não misturar os JSONs do Baseline (Período A) com os da Rotulagem (Período B). E os metadados agora devem subir para o GitHub.

### 👨‍💻 Enzo Moraes (Checklist e Nome do Grupo)
- **O que você fez:** Cuidou da identificação e das seções de validação (checklist) no notebook.
- **Como ficou agora:** A responsabilidade de validação cresceu. Os checklists agora residem nos arquivos Markdown oficiais da professora dentro da pasta **`tarefas/`** (ex: `Tarefa1_Coleta_Bruta.md` e `Tarefa2_Baseline_e_Rotulagem.md`).
- **O que mudou:** Você (e o grupo) precisarão preencher esses diários no formato Scrum (Product Owner, Scrum Master, board, etc.). O notebook em si ficou mais limpo, focado só no código.

### 👩‍💻 Natsumi Goto (Consulta à API e Inspeção)
- **O que você fez:** Escreveu a lógica genial do `requests.get`, `raise_for_status()`, lidando com recusa de lista vazia.
- **Como ficou agora:** Sua lógica era muito boa e foi **100% mantida** no `01_coleta_bruta.ipynb`! 
- **O que mudou:** Como agora baixamos 14 dias de dados, a API da RIPE daria erro de "Query too large". A sua função de coleta foi colocada dentro de um loop (`for`) que baixa os dados fatiados, garantindo que o download gigantesco não quebre.

### 👨‍💻 Pedro Viana (DataFrame e Salvamento JSON/CSV)
- **O que você fez:** Converteu os resultados da API em linhas de um DataFrame do Pandas e salvou em CSV.
- **Como ficou agora:** O seu parser de DataFrame ficou muito mais inteligente. 
- **O que mudou:** No momento da conversão, o novo script (`processar_resultados`) já cria o `fluxo_id` (concatenando probe_id + dst_addr) e faz as matemáticas que o RFC exige já na extração: calcula a porcentagem de perda (`perda_pct`), calcula o desvio padrão da rajada (`jitter_ms`) e marca se houve timeout (`timeout_atual`). O CSV gerado em `data/interim/` agora tem todas as colunas que a Tarefa 2 exige.

### 👩‍💻 Vitória Alessandra (Tabela de Decisões e Testes de ID)
- **O que você fez:** Registrou todo o histórico técnico (ID 1007, 2000000) e os imports.
- **Como ficou agora:** O seu trabalho de documentação de decisões foi vital. O histórico de por que vocês testaram o 2000000 (one-off) e foram pro 1001 deve ir para o **Diário de Bordo** da Tarefa 1.
- **O que mudou:** O código ganhou novos imports (ex: `yaml` e `numpy`). Agora você pode adicionar à tabela de decisões o motivo da mudança atual: "Migramos da 1001 para a malha Anchoring Mesh para atender à restrição de estabilidade física do alvo, e estendemos de 2h para 14 dias para bater o piso de 1.500 amostras do Baseline".

---

## 3. Explicação Profunda: O Que os Novos Notebooks Fazem?

Criei dois notebooks novos na pasta `notebooks/`. O código foi totalmente refatorado, mas comentamos passo a passo.

### 📗 `01_coleta_bruta.ipynb` (Responsável pela Tarefa 1)
Ele lê o arquivo de configuração `config.yaml`. Depois, ele vai até a API da RIPE e baixa os dados separando estritamente em **Período A** e **Período B** (para que não haja contaminação dos dados de teste no treino).
* **O segredo:** Ele não salva só RTT. Ele cria as colunas brutas fundamentais como `perda_pct` (já lidando com divisão por zero) e `jitter_ms`.

### 📙 `02_baseline_rotulagem.ipynb` (Responsável pela Tarefa 2)
Este é o "Cérebro" do projeto até agora. Ele é dividido em 4 etapas cruciais:
1. **O Baseline Robusto:** Ele lê *apenas* os dados do Período A. Para cada `fluxo_id`, ele descarta se tiver menos de 1.500 linhas. Depois, calcula a **Mediana** e o **MAD (Median Absolute Deviation)**. 
   * *Por que Mediana/MAD e não Média/Desvio Padrão?* Como a Profa. Andrea ensinou, RTT na internet sofre picos malucos. A média seria corrompida por esses picos (outliers). A Mediana e o MAD ignoram os picos e encontram o valor "normal" verdadeiro.
2. **Métricas Relativas:** Ele pega os dados do Período B e calcula o `z_robusto` (quantos MADs de distância o RTT atual está da Mediana).
3. **Rotulagem em Cascata:** Ele passa linha por linha no Período B aplicando 6 regras "If/Else" ordenadas. Se a perda > 10% = FALHA. Se o Z-Robusto > 3.5 = FALHA. E assim por diante, até sobrar o OK.
4. **Split Temporal:** Em vez de embaralhar os dados (o que seria "espiar o futuro"), ele corta os dados no tempo: os primeiros 50% viram Treino, os próximos 20% Validação, e os últimos 30% Teste.

---

## 4. O Que Vocês Devem Fazer a Partir de Agora

O código está ~90% pronto para gerar o dataset da Árvore de Decisão. O que falta é a inteligência humana de redes de vocês:

1. **Achar as Medições Reais (Ação Técnica Principal):**
   * No `01_coleta_bruta.ipynb`, existe uma variável chamada `MSM_IDS_TESTE`. 
   * Vocês precisam entrar no portal do **RIPE Atlas**, ir na aba de *Measurements*, filtrar por "Ping", "Anchoring Mesh" e pegar os IDs das medições reais (que rodam o tempo todo) referentes às 12 rotas que a professora pede (ex: BR->BR, BR->JP, DE->DE).
   * Coloquem esses IDs no script ou no `config.yaml` e rodem a coleta de verdade.

2. **Rodar os Pipelines:**
   * Rodem o Notebook 01 inteiro. Ele vai popular as pastas `data/raw/` com arquivos grandes e gerar a `tabela_bruta_completa.csv`.
   * Depois rodem o Notebook 02. Ele vai consumir essa tabela, gerar os cálculos avançados e cuspir o `dataset_rotulado_B_split.csv`.
   * *Pronto! Vocês terão finalizado a Tarefa 2 de forma perfeita.*

3. **Preencher a Burocracia:**
   * Abram a pasta `tarefas/`. Lá dentro estão os templates `Tarefa1_...` e `Tarefa2_...`.
   * Peguem os relatórios de qualidade gerados no final dos notebooks (contagem de OK, RISCO, FALHA, quantidade de fluxos) e preencham nos documentos. Registrem os diários de bordo individuais de vocês lá.
