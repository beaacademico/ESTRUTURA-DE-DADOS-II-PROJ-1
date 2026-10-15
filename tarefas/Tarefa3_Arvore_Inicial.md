# Diário da Tarefa 3 — Primeira árvore de decisão

**Período:** 28/09/2026 a 04/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)  
**Equipe:** Grupo 5 (Breno Brasil de Souza, Beatriz Gonçalves da Silva, Enzo Moraes Sousa, Natsumi Goto, Pedro Viana da Silva, Vitória Alessandra das Neves)  
**Scrum Master da tarefa:** Breno Brasil de Souza  
**Repositório GitHub:** `https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1`  

> Tarefa 1 coletou. Tarefa 2 fez o baseline e o rótulo. Esta tarefa **não refaz** a ficha nem a tabela de classes.
>
> O modelo é uma **árvore de decisão**. O entregável é a árvore: atributos de cada divisão, profundidade, folhas e as regras lidas em português. Não é um desfile de algoritmos.
>
> A árvore oficial usa só métricas relativas ao baseline do fluxo. Uma segunda árvore, de contraste, pode ver a rota ou o RTT absoluto — só para mostrar que ela aprende distância. Essa árvore de contraste **não** é o modelo do projeto.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Ficha de baseline, dataset rotulado, corte temporal | Tarefa 2 — **os mesmos** (`dataset_rotulado_B_split.csv`) |
| **Sai** | Árvore treinada só no treino, com profundidade e critério registrados | Tarefa 4 mexe nesta árvore, não no rótulo |
| **Sai** | Regras da árvore em texto e matriz 3×3 (OK, RISCO, FALHA) | Tarefa 4, para atacar o erro |
| **Sai** | Árvore de contraste (com rota ou RTT absoluto) e a frase do que ela aprendeu | Prova de que o modelo oficial não segue esse atalho |

**Não sai daqui:** troca de algoritmo (floresta, boosting, redes), limiar fino, model card.

- [x] Treino, validação e teste são os da Tarefa 2 (Split temporal: 50% treino [86.822 linhas], 20% validação [34.703 linhas], 30% teste [52.149 linhas])
- [x] A ficha de baseline não foi recalculada com o Período B (o baseline é estritamente o do Período A para evitar *data leakage*)

---

## 1. Colunas que a árvore oficial pode usar

Entram: `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco`.

Não entram: país, IP, `rota_id`, `fluxo_id`, nome do destino, RTT em milissegundos no lugar das métricas relativas.

- [x] Lista de colunas do treino colada no diário
- [x] Conferido que a classe (`OK` / `RISCO` / `FALHA`) é o alvo, não uma feature

**Colunas usadas:**
```python
features = [
    'z_robusto', 'aumento_pct', 'jitter_relativo', 'perda_pct',
    'timeout_atual', 'n5_timeout', 'n5_aumento80', 'n5_risco'
]
target = 'classe'
```

---

## 2. A árvore

- [x] Uma árvore de decisão (CART: Critério **Gini**)
- [x] `max_depth` e `min_samples_leaf` escolhidos olhando **só a validação**, não o teste
- [x] Semente registrada se o treino for estocástico (`random_state=42`)
- [x] Ajuste (`fit`) só no conjunto de treino (`df['split'] == 'treino'`)
- [x] Profundidade real, número de folhas e as primeiras divisões descritas
- [x] Pelo menos três regras no formato “se métrica ≤ limiar e … então classe”, copiadas da árvore (não inventadas)

**Critério, profundidade máxima pedida, profundidade obtida, folhas:**  
* **Algoritmo:** `DecisionTreeClassifier` (Scikit-Learn)
* **Critério de divisão:** `gini`
* **Profundidade máxima solicitada:** `max_depth = 4`
* **Profundidade obtida:** 4
* **Número total de folhas:** 8 folhas terminais
* **Divisão inicial (Nó Raiz):** `z_robusto <= 3.50` (comprova que a anomalia normalizada é a feature de maior ganho de informação)

**Regras lidas diretamente da árvore (extraídas via `export_text`):**

1. **Regra de Operação Saudável (OK):**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco <= 1.50` *e* `n5_aumento80 <= 1.50` *e* `perda_pct <= 16.67%`  
   ➔ **Classe: OK** *(tráfego dentro da variabilidade esperada da rota).*

2. **Regra de Degradação Severa por Perda (FALHA):**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco <= 1.50` *e* `n5_aumento80 <= 1.50` *e* `perda_pct > 16.67%`  
   ➔ **Classe: FALHA** *(mesmo com RTT próximo da mediana, a perda de pacotes caracteriza falha do canal).*

3. **Regra de Degradação Crítica por Latência (FALHA):**  
   *Se* `z_robusto > 3.50`  
   ➔ **Classe: FALHA** *(imediatamente na raiz: latência desviou mais de 3.5 vezes a escala MAD histórica do fluxo).*

4. **Regra de Alerta Intermediário (RISCO):**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco > 1.50` *e* `jitter_relativo <= 3.00` *e* `z_robusto > 2.00`  
   ➔ **Classe: RISCO** *(histórico recente instável somado a um desvio moderado de RTT).*

---

## 3. Leitura do erro

No bloco de **validação** (34.703 amostras. O teste permanece lacrado até a entrega final):

- [x] Matriz 3×3 com contagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro
- [x] Acurácia sozinha não decide: com maioria OK (29.675 de 34.703 = 85.5%), ela fica alta mesmo errando FALHA
- [x] Dois erros concretos analisados com fluxo, timestamp e valores

**Matriz 3×3 de Confusão (Validação):**

| Real \ Predito | Predito OK | Predito RISCO | Predito FALHA | **Total Real** |
| :--- | :---: | :---: | :---: | :---: |
| **Real OK** | **29.675** | 0 | 0 | 29.675 |
| **Real RISCO** | 143 | **2.558** | 0 | 2.701 |
| **Real FALHA** | 37 | 16 | **2.274** | 2.327 |
| **Total Predito** | 29.855 | 2.574 | 2.274 | **34.703** |

**Desempenho por Classe e F1 Macro:**

| Classe | Precisão | Recall | F1-Score | Amostras (Support) |
| :--- | :---: | :---: | :---: | :---: |
| **OK** | 0.9940 | 1.0000 | 0.9970 | 29.675 |
| **RISCO** | 0.9938 | 0.9471 | 0.9699 | 2.701 |
| **FALHA** | 1.0000 | 0.9772 | 0.9885 | 2.327 |
| **Acurácia Global** | - | - | **0.9944** | 34.703 |
| **F1 Macro** | **0.9959** | **0.9748** | **0.9851** | 34.703 |

> **Nota sobre desbalanceamento:** A acurácia foi de 99.44%, mas o critério guia da equipe é o **F1 Macro (0.9851)** e o **Recall de FALHA (97.72%)**, garantindo que as classes minoritárias críticas não sejam mascaradas pela predominância de amostras em estado normal (`OK`).

**Erros concretos (amostras reais da validação):**

1. **Caso 1 — Real RISCO classificado como OK:**  
   * **Fluxo:** `measurement_id: 7714918`, `probe_id: 6251` (Rota curta / regional).  
   * **Timestamp:** `1789587420`  
   * **Métricas:** `z_robusto = 0.8655`, `n5_risco = 3.0`, `jitter_relativo = 1.12`, `perda_pct = 0%`, `avg = 0.465 ms`.  
   * **Diagnóstico do Erro:** O `z_robusto` pontual estava baixo (< 2.0), fazendo com que a árvore caísse na folha `OK` mesmo com `n5_risco = 3`. A profundidade 4 não teve ramificação suficiente para capturar a persistência temporal desse risco leve.

2. **Caso 2 — Real FALHA classificado como RISCO:**  
   * **Fluxo:** `measurement_id: 7714918`, `probe_id: 6251`.  
   * **Timestamp:** `1789612380`  
   * **Métricas:** `z_robusto = 2.85`, `n5_risco = 4.0`, `n5_aumento80 = 1.0`, `jitter_relativo = 3.82`, `perda_pct = 0%`.  
   * **Diagnóstico do Erro:** O limiar da raiz para `FALHA` imediata exige `z_robusto > 3.50`. Como a amostra tinha `z_robusto = 2.85` e `n5_aumento80 <= 1.5`, a árvore classificou como `RISCO`, subestimando uma falha incipiente.

---

## 4. Árvore de contraste (não é o modelo)

Treinamos uma segunda árvore com os mesmos dados de treino, porém inserindo atributos absolutos de telemetria (`avg` em milissegundos e `probe_id`).

- [x] Dizer qual divisão apareceu perto da raiz (em geral a rota ou um corte fixo de milissegundos)
- [x] Declarar que essa árvore fica fora da entrega final

**O que a árvore de contraste usou na raiz e nós superiores:**
```text
|--- jitter_ms <= 0.39
|   |--- avg <= 1.91 ms
|   |   |--- avg <= 0.42 ms -> class: OK
|   |   |--- avg >  0.42 ms -> class: RISCO
|--- jitter_ms >  0.39
|   |--- avg <= 24.54 ms -> class: FALHA
|   |--- avg >  40.80 ms -> class: RISCO
```

**Conclusão sobre a árvore de contraste:**  
A árvore de contraste criou cortes duros em milissegundos (`avg <= 1.91 ms`, `avg <= 24.54 ms`, `avg <= 40.80 ms`). Em vez de aprender degradação, ela **decorou a distância geográfica das sondas** (rotas curtas da Europa vs. rotas transatlânticas). Em um cabo submarino onde 150 ms é a latência saudável, essa árvore geraria alarmes falsos ininterruptos.  
**Declaração formal:** Essa árvore de contraste serve unicamente como contraprova metodológica e **está terminantemente descartada da entrega do projeto**.

---

## 5. Scrum e diário

- [x] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| **Breno Brasil de Souza** | Coordenação Scrum, garantia de não vazamento do Período A e revisão do split. | Garantir a consistência dos splits temporais sem leak. | Manter a governança do repositório e branches limpas. |
| **Beatriz Gonçalves da Silva** | Extração e tradução das regras lógicas da árvore para português claro. | Mapear as ramificações profundas em regras legíveis. | Manter documentação clara para o artigo técnico. |
| **Enzo Moraes Sousa** | Cálculo e validação da Matriz de Confusão 3×3 e métricas de F1 Macro. | Interpretar o impacto do desbalanceamento das classes. | Ajustar na Tarefa 4 a sensibilidade para a classe FALHA. |
| **Natsumi Goto** | Análise e rastreamento dos 196 casos de erro na validação com timestamp e fluxo. | Localizar e filtrar os registros divergentes no Pandas. | Monitorar trocas indevidas entre OK e RISCO. |
| **Pedro Viana da Silva** | Script de treinamento do Scikit-Learn com `DecisionTreeClassifier` e semente fixa. | Parametrização e extração das features relativas. | Manter o pipeline pronto para a busca em grade da Tarefa 4. |
| **Vitória Alessandra das Neves** | Construção da Árvore de Contraste com RTT absoluto e análise do atalho geográfico. | Demonstrar matematicamente a armadilha do RTT em ms. | Consolidar a defesa do `z_robusto` nas apresentações. |

---

## Rubrica — Tarefa 3 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore oficial | 1,5 | Uma árvore, critério e profundidade declarados, regras em português, fit só no treino | 1,5 | Árvore CART (Gini), profundidade 4, 8 folhas, 4 regras extraídas textualmente. |
| Métricas de três classes | 1,0 | Matriz 3×3, F1 por classe e F1 macro; acurácia não é o critério | 1,0 | Matriz 3×3 completa, F1 Macro de 0.9851 e análise de desbalanceamento. |
| Independência da rota | 1,0 | Colunas relativas apenas; árvore de contraste mostra o atalho da distância e é descartada | 1,0 | Árvore de contraste treinou com `avg`, provou o atalho em ms e foi descartada. |
| Scrum + diário | 0,5 | Board e diário de todos | 0,5 | Todos os 6 integrantes com tarefas, dificuldades e ajustes descritos. |
| **Total** | **4,0** | | **4,0 / 4,0** | |
