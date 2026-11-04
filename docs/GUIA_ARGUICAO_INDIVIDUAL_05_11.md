# 🎓 Guia Completo para a Arguição Individual (05/11/2026) — CypherNet: Vigia de Redes (Grupo 05)

Este documento prepara cada integrante do **Grupo 05** para a **Avaliação Individual do dia 05/11/2026**, cobrindo de forma direta, técnica e objetiva os **4 tópicos obrigatórios da página 9 do Edital de Entrega Final**.

---

## 📌 Resumo Executivo (Números-Chave para ter na ponta da língua)

* **Nome Oficial na Mostra:** **CypherNet: Vigia de Redes** (*Grupo 05*)
* **Fonte de Dados Reais:** Medição pública `msm_id = 9333345` do **RIPE Atlas (Anchoring Mesh)** — pacotes ICMP (`ping`) a cada **4 minutos** ($\Delta t = 240\text{ s}$).
* **Volume do Dataset Supervisionado:** **173.674 registros** distribuídos em **69 fluxos** (`probe_id|dst_addr`), após separação estrita dos **primeiros 7 dias** (`06/09/2026` a `13/09/2026`) exclusivamente para o cálculo da **baseline histórica**.
* **Divisão Temporal (Sem Vazamento / No Data Leakage):**
  * **Treino (50%):** 86.813 amostras
  * **Validação (20%):** 34.712 amostras
  * **Teste (30%):** 52.149 amostras
* **Modelo Principal Recomendado (`modelo.joblib`):** **Árvore de Decisão (`DecisionTreeClassifier`)** com `max_depth = 7` (16 folhas no modo diagnóstico $T=0$ e `max_depth = 8` sensível ao custo no modo proativo $T+1$).
* **Duplo Horizonte Operacional:**
  1. **Diagnóstico Instantâneo ($T=0$, 8 features base):** **F1 Macro = 1,0000** no teste (reconstrução exata das regras operacionais sem usar o rótulo como entrada).
  2. **Previsão Proativa do Próximo Ciclo ($T+1 = +4\text{ min}$, 11 features expandidas, sem `classe_atual` em $X$):** **F1 Macro = 0,5699** (Árvore) e **0,5824** (Random Forest), antecipando **31,9% a 33,9% das falhas futuras** 4 minutos antes de ocorrerem!

---

## 1️⃣ Tópico 1 do Edital: O Problema e os Dados

### P1.1: Qual problema real o CypherNet resolve e por que limiares fixos de RTT não funcionam?
* **Resposta:** Em redes geograficamente distribuídas (WAN/Internet), uma latência de `35 ms` pode ser excelente para um enlace transatlântico, mas representar uma degradação severa para uma rota metropolitana cujo normal é `2 ms`. Além disso, muitas degradações ocorrem como **Gray Failures** (oscilação de jitter ou elevação moderada e persistente de RTT sem queda total do link).
* **Nossa solução:** Em vez de usar RTT bruto ou identificadores de topologia (como IP ou país, que fariam o modelo decorar rotas específicas), normalizamos cada medição contra a **baseline histórica individual do próprio fluxo** (`fluxo_id = probe_id|dst_addr`).

### P1.2: Como a Baseline (`baseline.csv`) foi calculada e como evitamos vazamento de dados (*Data Leakage*)?
* **Resposta:** Separamos os primeiros **7 dias** da coleta (`2026-09-06` a `2026-09-13`, ~2.520 medições por fluxo) exclusivamente para calcular estatísticas robustas a *outliers*:
  * **Mediana ($\text{mediana}$)** da latência `avg` (em vez da média aritmética, que é distorcida por picos).
  * **MAD ($\text{Median Absolute Deviation}$):** $\text{mediana}(|x - \text{mediana}|)$, multiplicado pelo fator de consistência normal **$1,4826$**.
  * **Jitter Típico ($\text{jitter\_tipico}$):** mediana de $(\text{max} - \text{min})$ no período basal.
* Esses 7 dias iniciais **não entram** no dataset supervisionado (`dataset_rotulado_B_split.csv`), e o dataset supervisionado é dividido **cronologicamente** (50% treino $\rightarrow$ 20% validação $\rightarrow$ 30% teste), garantindo que o modelo nunca treine com dados do futuro para prever o passado.

### P1.3: Quais são as features de entrada e como tratamos valores ausentes (`NaN`) e divisão por zero?
* **As 8 Features Base (Modo Diagnóstico $T=0$):**
  1. `z_robusto` $= \frac{\text{avg} - \text{mediana}}{1,4826 \times \text{MAD}}$ *(desvio padronizado robusto)*
  2. `aumento_pct` $= \frac{\text{avg} - \text{mediana}}{\text{mediana}} \times 100$ *(variação percentual sobre a mediana)*
  3. `jitter_relativo` $= \frac{\text{max} - \text{min}}{\text{jitter\_tipico}}$ *(amplificação da instabilidade de fila)*
  4. `perda_pct` $= \frac{\text{sent} - \text{rcvd}}{\text{sent}} \times 100$ *(perda de pacotes ICMP)*
  5. `timeout_atual` $\in \{0, 1\}$ *(vale `1` se `rcvd == 0` / perda de 100%)*
  6. `n5_timeout` $\in [0, 5]$ *(soma de timeouts nas últimas 5 medições do fluxo, ~20 min)*
  7. `n5_aumento80` $\in [0, 5]$ *(quantas das últimas 5 medições tiveram `aumento_pct >= 80%`)*
  8. `n5_risco` $\in [0, 5]$ *(quantas das últimas 5 medições apresentaram risco pontual: $2 \le z < 3,5$ ou $30\% \le \text{aumento} \le 80\%$ ou $\text{jitter\_relativo} \ge 3$)*
* **As 3 Features de Tendência Adicionais (Modo Proativo $T+1$ e $H3$):**
  9. `z_max5`: pico de `z_robusto` na janela móvel de 5 medições.
  10. `z_tendencia5`: inclinação linear (*slope* por mínimos quadrados) de `z_robusto` nas últimas 5 medições (mede se a fila do roteador está acelerando).
  11. `perda_media5`: média móvel da perda de pacotes nas últimas 5 medições.
* **Tratamento de `NaN` (Ponto Crítico de Auditoria):**
  * Quando ocorre um *blackout* (`perda_pct == 100%`), não há resposta ICMP e, portanto, `avg` e `jitter` não existem (`NaN`).
  * **Nunca substituímos `NaN` por zero nem pela mediana**, pois imputar a mediana faria `z_robusto = 0`, enganando o modelo como se a latência estivesse perfeita durante uma queda total! Mantemos `float('nan')`, pois o `DecisionTreeClassifier` do `scikit-learn >= 1.4` e o `XGBoost` aprendem nativamente para qual ramo enviar valores `NaN`.

---

## 2️⃣ Tópico 2 do Edital: Conceitos sobre os Modelos

### P2.1: Como funciona a Árvore de Decisão (CART) e o critério de Gini?
* **Resposta:** A Árvore de Decisão particiona recursivamente o espaço de atributos por meio de cortes ortogonais (`feature <= limiar`), buscando em cada nó a divisão que maximiza a redução da **Impureza de Gini**:
  $$G = 1 - \sum_{k=1}^{3} p_k^2$$
  onde $p_k$ é a proporção de amostras da classe $k \in \{\text{OK}, \text{RISCO}, \text{FALHA}\}$ no nó. Um nó puro (100% de uma única classe) tem $G = 0$.

### P2.2: Qual a diferença conceitual entre Árvore de Decisão, Random Forest (Bagging) e XGBoost (Boosting)?
* **Árvore de Decisão Única:** Treina uma única hierarquia de regras. Vantagens: **100% interpretável (caixa-branca)**, auditável por engenheiros de NOC e ultra-rápida. Risco se não podada: *overfitting* (controlado no nosso projeto limitando `max_depth=7` e `min_samples_leaf`).
* **Random Forest (*Bagging*):** Treina dezenas/centenas de árvores **em paralelo** sobre amostras *bootstrap* com sorteio aleatório de subconjuntos de features em cada nó, combinando-as por votação majoritária. Reduz a **variância** de árvores individuais.
* **XGBoost (*Gradient Boosting*):** Treina árvores **sequencialmente**, onde cada nova árvore é ajustada para corrigir os resíduos (erros do gradiente da função de perda *log-loss*) deixados pelas árvores anteriores, somando regularização $L_1/L_2$. Reduz tanto **viés** quanto **variância**.

### P2.3: Por que escolhemos a Árvore de Decisão (`max_depth=7`) como modelo principal no pacote do Blackboard?
* **Resposta:** Seguindo a recomendação metodológica da disciplina:
  1. **Paridade de Desempenho:** No modo diagnóstico ($T=0$), a Árvore de profundidade 7 atinge `F1 Macro = 1,0000` (com apenas 16 folhas!), empatando com Random Forest (`0,9997`) e superando ligeiramente o XGBoost (`0,9956`). No modo proativo ($T+1$), fica a apenas `~0,01` de F1 Macro do Random Forest (`0,5699` vs `0,5824`).
  2. **Interpretabilidade Operacional:** Cada folha da árvore pode ser lida diretamente como uma regra `SE ... ENTÃO` pela equipe de redes, enquanto 150 árvores de um ensemble funcionam como caixa-preta.
  3. **Eficiência e Pegada Mínima:** O pacote completo com as árvores serializadas tem apenas **45,6 KB** (`Grupo05.zip` tem **27,9 KB**) e executa inferências em **~0,15 a 0,70 ms**.

---

## 3️⃣ Tópico 3 do Edital: Resultados da Predição ($T=0$ vs. Horizonte Proativo $T+1$ e $H3$)

### P3.1: Por que o modelo $T=0$ obteve `F1 = 1,0000` e por que adicionamos a avaliação proativa em $T+1$ (+4 min)?
* **Resposta:**
  * No modo **Diagnóstico Instantâneo ($T=0$)**, o objetivo é classificar o estado operacional atual $y_t$ a partir das 8 métricas observadas até o próprio instante $t$. Como os rótulos de referência foram construídos a partir de limiares determinísticos sobre essas mesmas grandezas (sem ruído externo), uma Árvore de Decisão de profundidade 7 reconstrói perfeitamente os cortes ortogonais (`F1 Macro = 1,0000` no teste).
  * Contudo, na prática de um NOC, também queremos **prever o estado futuro antes que a falha ocorra**. Por isso, implementamos o **Modo Previsão Proativa ($T+1$, 4 minutos à frente)** e o **Modo Alerta Antecipado ($H3$, próximos 12 minutos)**, onde o alvo é o estado futuro ($y_{t+1}$) e a classe atual **não está presente** entre as variáveis explicativas.

### P3.2: Quais são os resultados comparativos no Conjunto de Teste (52.149 amostras)?

| Horizonte / Modo | Modelo | Accuracy (Teste) | F1 Macro (Validação) | F1 Macro (Teste) | Recall `FALHA` (Teste) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **$T=0$ (Diagnóstico Instantâneo)** | **Árvore de Decisão (`d=7`, 16 folhas)** | **100,00%** | **0,9999** | **1,0000** | **100,00%** |
| $T=0$ (Diagnóstico Instantâneo) | Random Forest (`100` árvores, `d=7`) | 99,99% | 0,9996 | 0,9997 | 99,93% |
| $T=0$ (Diagnóstico Instantâneo) | XGBoost (`100` árvores, `d=4`) | 99,90% | 0,9954 | 0,9956 | 99,87% |
| **$T+1$ (Proativo +4 min à frente)** | **Árvore Proativa (`d=8`, pesos `1:2:3`)** | **88,38%** | **0,5782** | **0,5699** | **31,86%** |
| $T+1$ (Proativo +4 min à frente) | Random Forest Proativo (`d=10`, pesos `1:2:3`) | 88,80% | 0,5873 | 0,5824 | 33,85% |
| $T+1$ (Proativo +4 min à frente) | XGBoost Proativo (`d=5`, `lr=0.05`) | 89,14% | 0,5788 | 0,5748 | 28,48% |
| **$H3$ (Alerta Antecipado +12 min)** | **Árvore Alerta (`d=7`, pesos `1:1.5:2`)** | **72,80%** | **0,5243** | **0,5113** | **21,92%** |

### P3.3: Como interpretar o `F1 Macro = 0,57–0,58` e o `Recall FALHA = 32%–34%` no horizonte futuro $T+1$?
* **Resposta:** Em telemetria de rede amostrada a cada 4 minutos, existem dois tipos de falhas:
  1. **Falhas Abruptas / Estocásticas (~66%):** Quedas súbitas de pacote (`perda_pct >= 10%`) ou cortes instantâneos de rota sem elevação prévia de RTT. Nenhum modelo baseado apenas em ping passado consegue adivinhar um corte físico súbito 4 minutos antes.
  2. **Degradações Progressivas / *Congestion Build-up* (~34%):** Enlaces onde a fila do roteador começa a encher gradualmente (`aumento_pct`, `n5_risco`, `z_max5` e `z_tendencia5` subindo). **O nosso modelo proativo captura ~1 em cada 3 falhas futuras com 4 minutos de antecedência** (e 62,2% de precisão quando emite alerta de falha!), sendo que as duas novas variáveis de tendência (`z_max5` com 13,1% e `z_tendencia5` com 10,6%) respondem por **23,7% da importância total da árvore proativa**.

---

## 4️⃣ Tópico 4 do Edital: O Uso da API e Empacotamento MLOps

### P4.1: O que há dentro do pacote canônico `Grupo05.zip` entregue no Blackboard?
1. **`modelo.joblib` (45,6 KB):** Dicionário Python serializado via `joblib` contendo:
   * `"modelo"`: objeto `DecisionTreeClassifier` principal ($T=0$, profundidade 7, 16 folhas).
   * `"features"`: lista ordenada das 8 features base (`FEATURES_BASE`).
   * `"familia"`: `"arvore_decisao"`.
   * `"params"`: hiperparâmetros do modelo.
   * `"modelo_proativo_t1"` e `"modelo_proativo_h3"`: árvores treinadas para +4 min e +12 min com as 11 features (`features_proativas`).
2. **`metadados.json`:** Especificação completa com os 11 itens exigidos pelo edital (versões de Python/bibliotecas, fórmulas exatas, regras de `NaN` e divisão por zero, mapeamento `["OK", "RISCO", "FALHA"]`, horizontes, exemplo real de entrada/saída e matrizes de confusão).
3. **`baseline.csv`:** As 69 rotas com `mediana`, `MAD`, `jitter_tipico`, `perda_tipica`, `prop_resposta`, janela de cálculo (`2026-09-06` a `2026-09-13`), critério de validade (`amostras >= 1500` e `prop_resposta >= 0.70`) e recomendação de uso.

### P4.2: Como a API Flask (`producao/app/server.py`) funciona da entrada à saída?
1. **Inicialização Segura:** No boot, o servidor calcula o hash **SHA-256** de `modelo_final.joblib`, carrega `baseline.csv` em memória (`dict` indexado por `fluxo_id`) e inicializa um dicionário de buffers circulares `JanelaFluxo(tamanho=5)` para manter as últimas 5 medições de cada rota.
2. **Fluxo de uma Requisição (`POST /api/diagnosticar` ou `POST /api/previsoes`):**
   * Recebe `probe_id`, `dst_addr` (ou `fluxo_id`), `rtt_ms` (`avg`), `perda_pct` (ou `sent`/`rcvd`) e `jitter_ms` (ou `min`/`max`).
   * Consulta a `mediana`, `MAD` e `jitter_tipico` do fluxo em `baselines`.
   * Chama `processar_medicao()` do módulo único [`src/cyphernet/features.py`](../src/cyphernet/features.py), que calcula `z_robusto` (com fator `1.4826 * MAD`), preserva `NaN` em caso de timeout (`perda_pct >= 100%`) e atualiza a janela móvel `JanelaFluxo` de 5 medições.
   * Executa a inferência na Árvore de Decisão $T=0$ (`modelo_t0.predict_proba`) e nas Árvores Proativas $T+1$ (+4 min) e $H3$ (+12 min).
   * Registra o resultado no histórico em memória (`historico_previsoes`) e devolve JSON estruturado com a classe predita, probabilidades por classe, métricas calculadas, tempo de inferência em milissegundos e hash SHA-256.
3. **Endpoints Disponíveis:**
   * `GET /api/saude`: *Healthcheck* com status da API, modelo carregado, uptime e SHA-256.
   * `GET /api/modelo`: Metadados de governança, hiperparâmetros e lista ordenada de atributos.
   * `GET /api/fluxos`: Catálogo das 69 rotas monitoradas e suas baselines.
   * `POST /api/diagnosticar`: Diagnóstico interativo instantâneo ($T=0$) + previsão proativa ($T+1$ e $H3$).
   * `POST /api/previsoes` e `GET /api/previsoes`: Contrato canônico do edital para predição individual/em lote e consulta do histórico recente de previsões.
   * `POST /api/coletar_ripe_ao_vivo`: Consulta ao vivo a API global do RIPE Atlas (`msm_id = 9333345`) nos últimos 60 minutos e classifica os enlaces em tempo real.
