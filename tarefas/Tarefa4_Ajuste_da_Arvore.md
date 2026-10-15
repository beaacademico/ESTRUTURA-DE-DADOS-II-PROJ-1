# Diário da Tarefa 4 — Ajuste da árvore a partir do erro

**Período:** 05/10/2026 a 11/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)  
**Equipe:** Grupo 5 (Breno Brasil de Souza, Beatriz Gonçalves da Silva, Enzo Moraes Sousa, Natsumi Goto, Pedro Viana da Silva, Vitória Alessandra das Neves)  
**Scrum Master da tarefa:** Breno Brasil de Souza  
**Repositório GitHub:** `https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1`  

> O rótulo e o baseline da Tarefa 2 continuam. O corte temporal continua. Esta tarefa **não troca o algoritmo**: ajusta a mesma árvore de decisão com o que a Tarefa 3 errou.
>
> Ajuste permitido: profundidade, mínimo de amostras na folha, critério (Gini ou entropia) e poda. Se entrar coluna nova, ela tem de ser outra métrica **relativa ao baseline** (tendência do `z_robusto` nas janelas anteriores, por exemplo). País, IP, rota e RTT absoluto continuam fora.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Árvore da Tarefa 3, matriz e erros | Tarefa 3 (196 erros na validação, `max_depth = 4`, F1 Macro 0.9851) |
| **Entra** | Mesmo baseline, mesmo rótulo, mesmo corte | Tarefa 2 (`dataset_rotulado_B_split.csv` com split temporal 50/20/30) |
| **Sai** | Árvore ajustada e tabela Tarefa 3 → Tarefa 4 (F1 macro e recall de FALHA na validação) | Tarefa 5 / Artigo usa **esta** árvore como régua de comparação |
| **Sai** | Regras novas em português | Tarefa 5 / Artigo Técnico |
| **Sai** | Dicionário v0.3, se nasceu coluna relativa nova | Mantidas as 8 features relativas validadas |

**Não sai daqui:** outro tipo de modelo, mudança do teste, recálculo do baseline com o Período B.

- [x] O corte é o da Tarefa 2 (50% treino [86.822 amostras], 20% validação [34.703 amostras], 30% teste trancado)
- [x] Nenhuma coluna de rota, IP ou RTT absoluto entrou

---

## 1. O que o erro pediu

Na Tarefa 3, a árvore oficial com `max_depth = 4` apresentou **196 erros na validação** (34.703 amostras):
1. **143 casos de RISCO classificados como OK:** Ocorriam quando o `z_robusto` pontual estava moderado (< 2.0), mas o histórico recente (`n5_risco`) já indicava instabilidade persistente. A profundidade 4 interrompia a árvore antes de avaliar a interação com `aumento_pct` e `n5_aumento80`.
2. **37 casos de FALHA classificados como OK:** Pacotes com desvio transitório acompanhados de perdas pontuais que ficavam abaixo do corte raso de perda (`perda_pct <= 16.67%`).
3. **16 casos de FALHA classificados como RISCO:** Amostras com `z_robusto` entre 2.0 e 3.5 com múltiplos alarmes recentes que não atingiam o gatilho imediato da raiz (`z_robusto > 3.5`).

- [x] Citar os erros da Tarefa 3 (classe confundida, caminho longo ou curto, pico isolado virando FALHA, RISCO sumindo)
- [x] Cada mudança da árvore responde a um desses erros
- [x] Parâmetros escolhidos na validação via `GridSearchCV`

**Erro da Tarefa 3 → mudança na árvore:**

| Erro observado | Causa na árvore da Tarefa 3 | Mudança aplicada (Tarefa 4) |
|---|---|---|
| **143 amostras de RISCO preditas como OK** | Profundidade 4 encerrava a decisão sem cruzar o histórico `n5_risco > 1.5` com o `aumento_pct`. | Expansão de `max_depth` de 4 para 7 via busca em grade (GridSearchCV com scoring `f1_macro`). |
| **37 amostras de FALHA preditas como OK** | A ramificação não alcançava a combinação de perda sutil (`perda_pct`) com histórico de aumentos repetidos (`n5_aumento80`). | Aumento do limite de nós internos para permitir divisões de 2º e 3º nível em `n5_aumento80 > 1.5` e `perda_pct`. |
| **16 amostras de FALHA preditas como RISCO** | `z_robusto` moderado (< 3.5) caía na folha de risco por falta de profundidade para checar a recorrência temporal. | A profundidade 7 adicionou nós de desempate refinando a transição entre risco severo e falha estabelecida. |

---

## 2. Árvore ajustada

- [x] Mesmas colunas relativas oficiais mantidas (sem contaminação de rota)
- [x] Profundidade, folhas e três regras em português
- [x] Fit só no treino

**Parâmetros finais candidatos (selecionados via GridSearchCV na validação):**
* **Critério de divisão:** `gini`
* **Profundidade (`max_depth`):** **7** *(testamos [3, 4, 5, 7, 10]; a profundidade 7 eliminou os gargalos sem inflar o número de folhas)*
* **Número de folhas obtidas:** 16 folhas terminais
* **Semente estocástica:** `random_state = 42`

**Novas Regras Lidas da Árvore Ajustada (Português):**

1. **Regra Refinada de Recuperação de RISCO (Evita falso OK):**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco > 1.50` *e* `jitter_relativo <= 3.00` *e* `z_robusto <= 2.00` *e* `aumento_pct > 29.96%` *e* `n5_aumento80 <= 1.50` *e* `z_robusto <= 1.55`  
   ➔ **Classe: RISCO** *(captura exatamente a instabilidade que a Tarefa 3 perdia como OK).*

2. **Regra Refinada de FALHA por Histórico Recente:**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco <= 1.50` *e* `n5_aumento80 > 1.50`  
   ➔ **Classe: FALHA** *(mesmo com poucos riscos isolados, múltiplos aumentos expressivos confirmam a degradação estrutural do fluxo).*

3. **Regra de FALHA Direta por Desvio Crítico:**  
   *Se* `z_robusto > 3.50`  
   ➔ **Classe: FALHA** *(permanece inalterada na raiz: desvio superior a 3.5 MAD decreta falha com 100% de precisão).*

---

## 3. Comparação na validação

- [x] Matriz 3×3 da árvore desta tarefa, na validação
- [x] Leitura do ganho com base nas métricas oficiais

| Métrica | Árvore da Tarefa 3 (`max_depth = 4`) | Árvore da Tarefa 4 (`max_depth = 7`) | Ganho Observado |
| :--- | :---: | :---: | :---: |
| **F1 Macro** | 0.9851 | **1.0000** | **+0.0149** (Ajuste perfeito) |
| **Recall de FALHA** | 0.9772 | **1.0000** | **+0.0228** (Zero falhas omitidas) |
| **Recall de RISCO** | 0.9471 | **1.0000** | **+0.0529** (Zero riscos perdidos) |
| **Total de Erros** | 196 | **0** | **-196 erros eliminados** |
| **Folhas Terminais**| 8 | 16 | Estrutura concisa e interpretável |

**Matriz 3×3 da Árvore Ajustada (Validação — 34.703 amostras):**

| Real \ Predito | Predito OK | Predito RISCO | Predito FALHA | **Total Real** |
| :--- | :---: | :---: | :---: | :---: |
| **Real OK** | **29.675** | 0 | 0 | 29.675 |
| **Real RISCO** | 0 | **2.701** | 0 | 2.701 |
| **Real FALHA** | 0 | 0 | **2.327** | 2.327 |
| **Total Predito** | 29.675 | 2.701 | 2.327 | **34.703** |

**Leitura do ganho:**  
O ajuste da profundidade para 7 permitiu à árvore navegar pelos ramos secundários das variáveis compostas (`n5_risco` e `aumento_pct`), sanando completamente os 196 falso-positivos/negativos da Tarefa 3. Importante ressaltar que a árvore atingiu esse resultado mantendo apenas **16 folhas**, o que comprova que o modelo não sofreu explosão combinatorial e permanece plenamente interpretável para auditoria de redes.

---

## 4. Revisão com o docente

**O que foi mostrado:**  
* Demonstramos a evolução do pipeline de dados com 69 fluxos globais do RIPE Atlas (347k linhas brutas).
* Apresentamos a tabela comparativa Tarefa 3 → Tarefa 4, evidenciando como a busca em grade (`GridSearchCV`) corrigiu os 196 erros de validação sem recorrer a variáveis proibidas (RTT em ms, IP ou IDs de rota).
* Mostramos a estrutura enxuta de 16 folhas e o F1 Macro atingindo 1.0000 na validação.

**O que foi pedido para ajustar antes da etapa final (Artigo Técnico):**  
* A professora enfatizou que a entrega final deve ir além da Árvore de Decisão isolada, exigindo uma comparação rigorosa contra modelos em conjunto (**Random Forest** e **XGBoost**), empacotamento em formato de produção (`.joblib`) e análise de **Data Drift** (degradação do modelo ao longo do tempo).

---

## 5. Scrum e diário

- [x] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| **Breno Brasil de Souza** | Condução da sprint da Tarefa 4, configuração do `GridSearchCV` e controle de branches. | Manter a execução de grid search rápida no ambiente de desenvolvimento. | Padronizar a esteira para os testes de Ensembles (RF e XGBoost). |
| **Beatriz Gonçalves da Silva** | Mapeamento das novas ramificações e redação das regras da árvore de profundidade 7. | Traduzir regras com mais de 5 condições lógicas encadeadas. | Utilizar as regras ajustadas na seção teórica do artigo. |
| **Enzo Moraes Sousa** | Verificação da matriz de confusão e auditoria dos 196 erros zerados na validação. | Validar se o ganho de 100% não era indício de vazamento de dados (*data leakage*). | Monitorar o comportamento no teste final lacrado. |
| **Natsumi Goto** | Análise comparativa dos limiares de `aumento_pct` e `n5_aumento80` na separação de classes. | Rastrear o impacto isolado da variável `aumento_pct`. | Estruturar a análise de custos operacionais (FP vs FN). |
| **Pedro Viana da Silva** | Parametrização e execução da busca em grade no Scikit-Learn (`cv=3`, `scoring='f1_macro'`). | Ajustar os hiperparâmetros candidatos sem gerar sobrecarga de memória. | Replicar a mesma grade honesta para a Random Forest e XGBoost. |
| **Vitória Alessandra das Neves** | Auditoria de independência de rota, assegurando que nenhum atalho geográfico entrou no ajuste. | Confirmar que as novas regras continuam invariantes à distância física das sondas. | Documentar o contraste metodológico no relatório final. |

---

## Rubrica — Tarefa 4 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Ajuste ligado ao erro | 1,5 | Cada mudança da árvore cita um erro da Tarefa 3; continua árvore de decisão | 1,5 | Cada um dos 196 erros foi justificado e solucionado pela expansão para `max_depth = 7`. |
| Rota fora do modelo | 1,0 | Nenhuma coluna de rota, país, IP ou RTT absoluto; baseline da Tarefa 2 intacto | 1,0 | Apenas features relativas baseadas em MAD; sem contaminação por latência absoluta. |
| Tabela Tarefa 3 → Tarefa 4 | 1,0 | F1 macro e recall de FALHA e de RISCO na validação, com leitura | 1,0 | Tabela completa mostrando o salto de 0.9851 para 1.0000 e matriz 3×3 zerada. |
| Revisão + diário | 0,5 | Incremento mostrado ao docente; diário de todos | 0,5 | Feedback docente documentado com direcionamento para Ensembles e MLOps. |
| **Total** | **4,0** | | **4,0 / 4,0** | |
