# Guia de Apresentação e Domínio Técnico: Parte do Breno

**Aluno / Scrum Master:** Breno Brasil de Souza  
**Projeto:** Preditor de Degradação de Rede com RTT Normalizado  
**Escopo Principal:** **Seção 03 (Metodologia)** & **Seção 04 (Reprodutibilidade e Pipeline em Python)** / **Tarefas 2 e 4**  
**Disciplina:** Estruturas de Dados II — Grupo 5  

---

## 1. Resumo Executivo e Posicionamento

Na apresentação do Artigo Técnico publicado, a sua atuação cobre **o coração do método científico do projeto**:

* **Seção 03 · Metodologia:** O desenho do experimento com dados reais do RIPE Atlas (Anchoring Mesh). O congelamento do Período A (14 dias) com Mediana e MAD, a criação das 8 variáveis relativas adimensionais, o expurgo absoluto de dados de IP/país/RTT bruto e a divisão estritamente temporal em 50% Treino (86.822), 20% Validação (34.703) e 30% Teste (52.149).
* **Seção 04 · Reprodutibilidade:** A execução prática em Python desse protocolo metodológico. A ordenação cronológica contínua, a resolução dos 196 erros da árvore inicial via `GridSearchCV` (profundidade 4 ➔ 7 com 16 folhas), a validação temporal com `TimeSeriesSplit` e a instrumentação de alta precisão via `time.perf_counter()` para medir tempos de treino (3,69s) e inferência (0,012s).

---

## 2. Roteiro Unificado de Apresentação (Pitch de ~1m40s a 2min)

### 2.1 Abertura e Transição
> *"Perfeito. Agora entrando no cerne experimental do nosso trabalho, eu vou apresentar as **Seções 03 e 04 do Artigo: a nossa Metodologia e o Pipeline de Reprodutibilidade em Python**."*

### 2.2 Seção 03 · Metodologia: O Desenho Experimental (~45s)
> *"Para que a comparação entre Árvore de Decisão, Random Forest e XGBoost fosse cientificamente justa, estabelecemos um protocolo rígido em 4 etapas:*
>
> 1. ***Primeiro — Baseline Histórico Robusto:** Utilizamos os 14 dias de referência do Período A para calcular a **Mediana** e o **MAD** (*Median Absolute Deviation*) específicos de cada uma das 69 rotas. O Período A foi 100% congelado para impedir vazamento de dados.
> 2. ***Segundo — Atributos Relativos e Adimensionais:** Transformamos as medições do Período B em **8 variáveis relativas** — como `z_robusto`, `jitter_relativo` e contadores de janelas móveis. **Excluímos deliberadamente IP, ASN, país e RTT absoluto em milissegundos**, forçando o modelo a aprender a física do desvio e não a geografia das sondas.
> 3. ***Terceiro — Separação Estritamente Temporal:** Das 173.674 amostras do Período B, dividimos em ordem cronológica: **50% para Treino (86.822)**, **20% para Validação (34.703)** e **30% para Teste Trancado (52.149)**.
> 4. ***Quarto — Métrica Decisiva:** Definimos o **F1-Score Macro** com semente fixa 42, garantindo que as classes críticas de degradação — **RISCO e FALHA** — tivessem o mesmo peso que a classe majoritária OK."*

### 2.3 Seção 04 · Reprodutibilidade: O Pipeline em Python (~55s)
> *"Na Seção 04, materializamos essa metodologia em código aberto e reprodutível, estruturado em dois blocos:*
>
> * **No primeiro bloco de código**, demonstramos o pipeline de treino. Garantimos a ordenação cronológica com `.sort_values('timestamp')` e aplicamos o `TimeSeriesSplit` dentro do `GridSearchCV`. 
>   * *Foi através desse código que solucionamos os **196 erros de validação da árvore rasa inicial (Tarefa 3)**: a busca em grade nos mostrou que a **profundidade 7** era o ponto ótimo, eliminando 100% dos erros e mantendo apenas **16 folhas auditáveis**.*
>
> * **No segundo bloco**, desenvolvemos a função `avaliar_modelo`. Para medir a latência real sem distorções do sistema operacional, utilizamos o `perf_counter` de alta resolução de CPU.
>   * *Medimos separadamente o tempo de treino e o tempo de predição, provando que a Árvore de Decisão realiza a inferência em apenas **12 milissegundos**, enquanto treina em **3,69 segundos**.*
>
> *Com esse pipeline validado e instrumentado, geramos a régua de benchmark que alimenta a tabela de resultados. Passo agora a palavra para o colega que vai detalhar os **Resultados Reportados na Seção 05**."*

---

## 2.4 Versão Express (Caso o tempo do grupo aperte — 1 minuto)
> *"Assumindo a **Metodologia e Reprodutibilidade (Seções 03 e 04)**, o nosso objetivo foi criar uma comparação 100% justa e sem atalhos geográficos. 
> Usamos 14 dias de histórico para congelar o baseline (mediana e MAD) de 69 fluxos globais e geramos 8 variáveis relativas adimensionais — banindo IPs e RTT em milissegundos. Dividimos o Período B temporalmente em 50% treino (86.822), 20% validação (34.703) e 30% teste (52.149).
> Na Seção 04, implementamos o pipeline em Python com `TimeSeriesSplit` e `GridSearchCV`. Foi esse código que nos permitiu diagnosticar os 196 erros da árvore inicial e encontrar a **profundidade 7**, zerando os erros na validação com F1 Macro de 1,0000 em apenas 16 folhas auditáveis. 
> Instrumentamos a medição com `perf_counter` de CPU, registrando 3,69s de treino e 12 milissegundos de inferência, estabelecendo a régua para os resultados da Seção 05."*

---

## 3. Dissecando a Patologia dos 196 Erros da Tarefa 3

| Erro da Tarefa 3 | Quantidade | O que acontecia na rede? | Por que a profundidade 4 falhava? | Como a profundidade 7 corrigiu? |
| :--- | :---: | :--- | :--- | :--- |
| **RISCO predito como OK** | **143** | O desvio pontual (`z_robusto`) ainda era moderado (< 2.0), mas o link já sofria há várias janelas (`n5_risco > 1.5`) com aumento de latência > 29%. | A profundidade 4 encerrava a árvore antes de avaliar a interação entre o histórico móvel e o aumento percentual. | Criou ramificações de 5º e 6º níveis que cruzam `n5_risco` e `aumento_pct`, recuperando a detecção de risco precoce. |
| **FALHA predita como OK** | **37** | Perda sutil de pacotes (10% a 16%) acompanhada de aumentos severos recorrentes (`n5_aumento80 > 1.5`). | O corte de perda era raso e isolado (`perda_pct > 16.67%`). Se ficasse abaixo, o modelo ignorava o histórico e dizia OK. | Nós secundários passaram a combinar perda moderada com reincidência de picos no histórico para decretar falha. |
| **FALHA predita como RISCO** | **16** | Desvio na faixa intermediária (entre 2.0 e 3.5 MAD) com múltiplos timeouts recentes. | Só existia um atalho para falha na raiz (`z_robusto > 3.5`). Valores intermediários caíam direto na folha de risco. | Adicionou nós de desempate refinando a fronteira entre degradação moderada e falha estrutural estabelecida. |

---

## 4. O Código da Seção 04 Explicado Linha por Linha

No Artigo Web, há dois blocos de código com botão de cópia. Veja o papel exato de cada um:

### Bloco 4.1: Pipeline de Treinamento e Validação Temporal
```python
import pandas as pd
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score

# 1. Ordenação cronológica obrigatória para séries temporais
df = pd.read_csv("data/processed/dataset_rotulado.csv")
df = df.sort_values("timestamp").reset_index(drop=True)

# 2. Expurgo ético: impede atalhos espúrios e vazamento do futuro
colunas_excluidas = ["timestamp", "label", "pais", "ip", "rota"]
X = df.drop(columns=[c for c in colunas_excluidas if c in df.columns])
y = df["label"]

# 3. Divisão estrita no tempo (passado no treino, futuro no teste)
corte = int(len(df) * 0.70)
X_treino, X_teste = X.iloc[:corte], X.iloc[corte:]
y_treino, y_teste = y.iloc[:corte], y.iloc[corte:]

# 4. Busca em grade temporal focada no F1 Macro
modelo = DecisionTreeClassifier(random_state=42)
grade = {"max_depth": [3, 5, 7, 10], "min_samples_leaf": [1, 5, 10]}
cv_temporal = TimeSeriesSplit(n_splits=3)
busca = GridSearchCV(modelo, grade, cv=cv_temporal, scoring="f1_macro", n_jobs=-1)
busca.fit(X_treino, y_treino)

# 5. Avaliação no conjunto cego de teste
pred = busca.best_estimator_.predict(X_teste)
```

* **`df.sort_values("timestamp").reset_index(drop=True)`**: Garante a sequência temporal contínua e recria o índice de `0` a `N-1` para que os cortes com `.iloc` sejam exatos.
* **`colunas_excluidas`**: Garante que o modelo não aprenda que "o IP X sempre falha" ou que "a rota intercontinental tem RTT alto". O modelo só recebe índices relativos ao baseline da própria rota.
* **`TimeSeriesSplit(n_splits=3)`**: Divisão em janelas deslizantes/acumulativas. Nunca usa dados futuros para validar hipóteses passadas.
* **`scoring="f1_macro"`**: Força a grade a ponderar com o mesmo peso as classes minoritárias (FALHA e RISCO), impedindo que a classe majoritária (OK) domine a escolha.

---

### Bloco 4.2: Benchmark de Custo Computacional com `perf_counter`
```python
from time import perf_counter
from sklearn.metrics import f1_score, precision_score, recall_score

def avaliar_modelo(nome, modelo, X_treino, y_treino, X_avaliacao, y_avaliacao):
    inicio = perf_counter()
    modelo.fit(X_treino, y_treino)
    tempo_treino = perf_counter() - inicio

    inicio = perf_counter()
    previsoes = modelo.predict(X_avaliacao)
    tempo_predicao = perf_counter() - inicio

    return {
        "modelo": nome,
        "precision_macro": precision_score(y_avaliacao, previsoes, average="macro", zero_division=0),
        "recall_macro": recall_score(y_avaliacao, previsoes, average="macro", zero_division=0),
        "f1_macro": f1_score(y_avaliacao, previsoes, average="macro", zero_division=0),
        "tempo_treino_s": round(tempo_treino, 4),
        "tempo_predicao_s": round(tempo_predicao, 4),
    }
```

* **Por que `perf_counter()` em vez de `time.time()`?** O `time.time()` é o relógio do sistema, impreciso para durações de frações de milissegundo. O `perf_counter()` acessa o contador de ciclos de hardware da CPU com a resolução mais alta do sistema, registrando a inferência da árvore em **0,012 segundos** sem ruído.
* **Isolamento de tempos:** Mede separadamente o custo de treinar (`modelo.fit`) e o custo operacional de servir predições em produção (`modelo.predict`).

---

## 5. Tabela de Bolso: Métricas Decisivas para Citar

### Evolução Tarefa 3 ➔ Tarefa 4 (Na Validação - 34.703 amostras):
* **F1-Score Macro:** de `0,9851` ➔ **`1,0000`** (+0,0149)
* **Recall de FALHA:** de `0,9772` ➔ **`1,0000`** (100% das falhas capturadas)
* **Recall de RISCO:** de `0,9471` ➔ **`1,0000`** (100% dos riscos detectados)
* **Total de Erros Eliminados:** **196 erros zerados**
* **Arquitetura da Árvore:** Profundidade expandida de 4 para **7**, gerando **16 folhas terminais** (estrutura concisa, sem sobreajuste descontrolado).

### Benchmark Comparativo no Artigo (Seção 05):
| Modelo | Hiperparâmetro | F1 Macro | Tempo Treino | Tempo Predição | Conclusão Técnica |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Árvore de Decisão (Tarefa 4)** | Profundidade 7 | **1,0000** | **3,69 s** | **0,012 s** | **Mais rápida e interpretável** |
| **Random Forest** | 50 estimadores | 0,9996 | 22,29 s | 0,145 s | Custo 6x maior no treino e 12x na inferência |
| **XGBoost** | 100 estimadores | **1,0000** | 9,58 s | 0,076 s | Custo intermediário, campeão para MLOps |

---

## 6. FAQ da Banca: Respostas Rápidas para Pegadinhas da Professora

### 1. *"F1 de 1,0000 não é sinal de vazamento de dados (data leakage)?"*
> **Sua Resposta:** *"Não é vazamento, professora. O F1 perfeito ocorreu porque a rotulagem da Tarefa 2 decorreu de uma política matemática determinística de regras claras com janelas móveis e MAD histórico. A árvore com profundidade 7 conseguiu reproduzir essa lógica sem ruído artificial. Além disso, auditamos a esteira: o Período A foi 100% congelado para calcular o baseline e o split seguiu a ordem cronológica estrita (50/20/30). Não houve contaminação temporal."*

### 2. *"Por que no Artigo a Árvore de Decisão é citada como recomendação preliminar, mas na Tarefa 6 o XGBoost foi o escolhido?"*
> **Sua Resposta:** *"Essa é uma virtude analítica do projeto, professora:*
> * *Sob a ótica do Artigo Técnico e do princípio da parcimônia (Navalha de Occam), a Árvore é imbatível em simplicidade e velocidade (0,012s de inferência).*
> * *Já na ótica de Engenharia e MLOps (Parte 6), redes reais enfrentam **Data Drift** (mudanças de tráfego e rotas não vistas no treino). A árvore simples tende a ser rígida demais perante ruídos inéditos. O XGBoost foi o campeão de produção por sua **regularização L1 e L2**, capacidade de generalização e artefato serializado superleve de apenas **372 KB**."*

### 3. *"Como você garante que o modelo funciona em qualquer lugar do mundo?"*
> **Sua Resposta:** *"Porque todas as variáveis são adimensionais. Não olhamos RTT bruto em ms, nem IP, nem país. Trabalhamos com o `z_robusto` (quantos desvios absolutos a medição se afastou da mediana histórica daquela rota). Uma rota intercontinental que opera normalmente a 150 ms tem z-score zero, da mesma forma que uma rede metropolitana a 5 ms tem z-score zero. O modelo aprendeu apenas o desvio relativo."*
