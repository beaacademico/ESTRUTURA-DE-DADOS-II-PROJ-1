# Diário da Tarefa 5 — Árvore final e teste único

**Período:** 12/10/2026 a 25/10/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)  
**Equipe:** Grupo 5 (Breno Brasil de Souza, Beatriz Gonçalves da Silva, Enzo Moraes Sousa, Natsumi Goto, Pedro Viana da Silva, Vitória Alessandra das Neves)  
**Scrum Master da tarefa:** Breno Brasil de Souza  
**Repositório GitHub:** `https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1`  

> A árvore que entra aqui é a da Tarefa 4. O baseline e o rótulo são os da Tarefa 2. O teste, guardado desde a Tarefa 2, é medido **uma vez**.
>
> Continua sendo uma árvore de decisão. O grupo entrega as regras, a matriz e o que a árvore faz num fluxo que ela não viu — desde que esse fluxo tenha a própria ficha de baseline, calculada só no período inicial dele.

### Contrato desta tarefa

| | Artefato | Origem / destino |
|---|---|---|
| **Entra** | Corte da Tarefa 2 e ficha de baseline | Tarefa 2 (`dataset_rotulado_B_split.csv`, 52.149 amostras no bloco `teste`) |
| **Entra** | Árvore ajustada e regras | Tarefa 4 (`DecisionTreeClassifier`, `criterion='gini'`, `max_depth=7`, 16 folhas) |
| **Sai** | Teste único: matriz 3×3, F1 por classe, F1 macro | Entrega |
| **Sai** | Checagem de fluxo não visto, com baseline próprio | Entrega (Experimento *Leave-Flows-Out* em rota curta e rota intercontinental) |
| **Sai** | Ficha da árvore (abaixo) e dicionário v0.4 igual às colunas usadas | Entrega (`docs/dicionario_dados_v0.4.md`) |

Não há tarefa seguinte.

- [x] A profundidade não foi escolhida de novo olhando o teste (mantida a configuração congelada na Tarefa 4: `max_depth = 7`)
- [x] O baseline do teste não usou medição do próprio teste (calculado exclusivamente sobre o Período A congelado)

---

## 1. Árvore que será medida

- [x] Critério, profundidade, mínimo de amostras na folha, colunas
- [x] Três regras em português, as mesmas da Tarefa 4 ou as revistas **antes** de abrir o teste
- [x] Confirmação de que país, IP, rota e RTT absoluto não estão na árvore

**Parâmetros:**
* **Algoritmo:** `DecisionTreeClassifier` (Scikit-Learn)
* **Critério:** `gini`
* **Profundidade máxima (`max_depth`):** `7` (profundidade obtida: `7`, número de folhas terminais: `16`)
* **Mínimo de amostras na folha (`min_samples_leaf`):** `1` (padrão validado na Tarefa 4)
* **Semente (`random_state`):** `42`

**Colunas (8 features exclusivamente relativas ao baseline):**
```python
features = [
    'z_robusto', 'aumento_pct', 'jitter_relativo', 'perda_pct',
    'timeout_atual', 'n5_timeout', 'n5_aumento80', 'n5_risco'
]
```
*(Confirmamos formalmente que país, endereço IP, `probe_id`, `measurement_id` e RTT absoluto em milissegundos estão 100% fora do modelo).*

**Regras (congeladas na Tarefa 4 antes de abrir o conjunto de teste):**

1. **Regra de Operação Normal (OK):**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco <= 1.50` *e* `n5_aumento80 <= 1.50` *e* `perda_pct <= 16.67%`  
   ➔ **Então Classe = OK** *(rota operando dentro do envelope estatístico esperado de seu baseline).*

2. **Regra de Captura de Risco Persistente (RISCO):**  
   *Se* `z_robusto <= 3.50` *e* `n5_risco > 1.50` *e* `jitter_relativo <= 3.00` *e* `z_robusto <= 2.00` *e* `aumento_pct > 29.96%` *e* `n5_aumento80 <= 1.50` *e* `z_robusto <= 1.55`  
   ➔ **Então Classe = RISCO** *(oscilação moderada recorrente na janela recente sem atingir o limiar de falha severa).*

3. **Regra de Degradação Severa / Queda (FALHA):**  
   *Se* `z_robusto > 3.50` **OU** (*se* `z_robusto <= 3.50` *e* `n5_risco <= 1.50` *e* `n5_aumento80 > 1.50`) **OU** (*se* `perda_pct > 16.67%`)  
   ➔ **Então Classe = FALHA** *(desvio agudo de latência, perda de pacotes na rajada ou múltiplos saltos severos consecutivos).*

---

## 2. Teste temporal (uma vez)

Avaliação executada uma única vez sobre os **52.149 registros** mais recentes do Período B (`df['split'] == 'teste'`), cobrindo os 69 fluxos monitorados.

- [x] Matriz 3×3 com contagem, não só porcentagem
- [x] Precisão, recall e F1 de OK, RISCO e FALHA
- [x] F1 macro
- [x] Recall de FALHA e a troca RISCO ↔ FALHA comentados
- [x] Dois casos concretos documentados com fluxo e timestamp

**Matriz 3×3 no Conjunto de Teste (52.149 medições):**

| Real \ Predito | Predito OK | Predito RISCO | Predito FALHA | **Total Real** |
| :--- | :---: | :---: | :---: | :---: |
| **Real OK** | **44.916** | 0 | 0 | 44.916 |
| **Real RISCO** | 0 | **4.261** | 0 | 4.261 |
| **Real FALHA** | 0 | 0 | **2.972** | 2.972 |
| **Total Predito** | 44.916 | 4.261 | 2.972 | **52.149** |

**Métricas por Classe no Teste:**

| Classe | Precisão | Recall | F1-Score | Suporte (Contagem) |
| :--- | :---: | :---: | :---: | :---: |
| **OK** | 1.0000 | 1.0000 | 1.0000 | 44.916 |
| **RISCO** | 1.0000 | 1.0000 | 1.0000 | 4.261 |
| **FALHA** | 1.0000 | 1.0000 | 1.0000 | 2.972 |
| **F1 Macro no Teste** | **1.0000** | **1.0000** | **1.0000** | **52.149** |

**Comentário sobre Recall de FALHA e fronteira RISCO ↔ FALHA:**  
O **Recall de FALHA atingiu 1.0000 (2.972 de 2.972)** e não houve trocas entre `RISCO` e `FALHA` no teste temporal dos fluxos conhecidos. Conforme detalhado na Seção 4 ("O que declarar"), esse resultado ocorre porque a árvore de profundidade 7 possui capacidade representacional suficiente para reconstruir exatamente os cortes ortogonais da política de rotulagem determinística definida na Tarefa 2.

**Casos concretos auditados no Teste:**

1. **Caso 1 — Acerto em Caminho Longo Estável (Classe OK):**
   * **Fluxo:** `measurement_id = 9333345`, `probe_id = 6349` (Rota intercontinental longa com **Mediana histórica = 185,09 ms**).
   * **Timestamp:** `1789708000`
   * **Medição:** `avg = 184,72 ms`, `z_robusto = -0,1724`, `perda_pct = 0%`, `n5_risco = 0`.
   * **Comportamento da Árvore:** Apesar de o RTT absoluto estar próximo de 185 ms (o que dispararia falso positivo em ferramentas de limiar fixo de 150 ms), o `z_robusto` de `-0,17` informou à árvore que a rota operava perfeitamente em sua linha de base, classificando como **OK**.

2. **Caso 2 — Detecção Crítica em Rota Regional / Limiar de Fronteira (Classe FALHA):**
   * **Fluxo:** `measurement_id = 9333345`, `probe_id = 6251` (Rota com **Mediana histórica = 28,25 ms** e baixíssima variabilidade `MAD`).
   * **Timestamp:** `1789720000`
   * **Medição:** `avg = 29,33 ms`, `z_robusto = 4,4552`, `perda_pct = 0%`.
   * **Comportamento da Árvore:** Embora o RTT bruto fosse baixo (29,33 ms), para aquela rota extremamente estável o salto ultrapassou `4,45` desvios MAD (`z_robusto > 3.50`), levando a árvore a acionar imediatamente a folha **FALHA**.

---

## 3. Fluxo que a árvore não viu

Para testar rigorosamente a generalização espacial da árvore em rotas inéditas (*Leave-Flows-Out*), removemos **dois fluxos completos** de todo o conjunto de treino (1 rota intercontinental longa e 1 rota local ultracurta), retreinamos a árvore com os mesmos hiperparâmetros (`max_depth = 7`, `random_state = 42`) apenas nos 67 fluxos restantes e avaliamos o modelo nas **5.036 medições** dos fluxos inéditos — utilizando exclusivamente o baseline calculado no Período A de cada fluxo separado.

- [x] O fluxo novo não aparece no treino
- [x] A mediana e o MAD não usam o trecho avaliado (vêm apenas do Período A de cada fluxo, ambos com >1.500 RTTs válidos)
- [x] Verificado que o caminho longo estável permaneceu OK e que degradações foram marcadas como RISCO ou FALHA

**Fluxos separados (100% fora do treino):**
1. **Fluxo Longo (Intercontinental):** `measurement_id = 7714918 | probe_id = 6349` — **Mediana no Período A = 252,82 ms** (> 1.500 medições válidas).
2. **Fluxo Curto (Local/IXP):** `measurement_id = 7714918 | probe_id = 6251` — **Mediana no Período A = 0,32 ms** (> 1.500 medições válidas).

**Resultado nos Fluxos Não Vistos (5.036 medições avaliadas):**

| Real \ Predito | Predito OK | Predito RISCO | Predito FALHA | **Total Real** |
| :--- | :---: | :---: | :---: | :---: |
| **Real OK** | **3.695** | 1 | 0 | 3.696 |
| **Real RISCO** | 0 | **736** | 0 | 736 |
| **Real FALHA** | 0 | 0 | **604** | 604 |
| **Total Predito** | 3.695 | 737 | 604 | **5.036** |

* **F1 Macro nos Fluxos Inéditos:** **0.9997** (Acurácia: 99,98% — 5.035 acertos em 5.036 pacotes).
* **Análise do Caminho Longo Estável (`252,82 ms`):** Permaneceu **100% em classe OK** durante todo o período saudável, provando que a árvore jamais confunde distância geográfica com falha.
* **Análise do Único Erro Observado no Fluxo Inédito (`timestamp = 1789621000`, fluxo `7714918 | 6251`):**  
  Uma medição com `avg = 0,579 ms` (frente à mediana sub-milissegundo de `0,321 ms`) gerou `aumento_pct = 80,40%`, `n5_risco = 2` e `z_robusto = 1,5557`. Como o corte interno aprendido sem esse fluxo ficou em `z_robusto <= 1,55`, a amostra por 0,0057 caiu no ramo de **RISCO** em vez de **OK**. Todas as **604 falhas reais** e **736 riscos reais** foram detectados sem omissão.

---

## 4. O que declarar

- [x] **Sobre a repetição da política de rótulo:** Declaramos com transparência científica que, como os rótulos da Tarefa 2 foram construídos a partir de regras sobre as mesmas métricas relativas (`z_robusto`, `aumento_pct`, `perda_pct` e janelas `n5_*`), a árvore de decisão de profundidade 7 aprendeu a **reproduzir a política de rotulagem com fidelidade matemática**, e não um evento externo independente (como um ticket de queda de BGP aberto por um operador humano).
- [x] **Detector de Estado vs. Preditor Futuro:** Como o alvo supervisionado deste pipeline é a classe da medição corrente $t$ (apoiada pela memória curta das últimas 5 medições) e não o estado da rede 12 minutos no futuro ($t+3$), o artefato entregue atua estritamente como um **detector/classificador automatizado de estado atual invariantemente à rota**, e não como um preditor de séries temporais futuras.
- [x] **Limitações operacionais identificadas:**
  1. **Baseline estático (*Data Drift*):** O baseline congelado no Período A não acompanha mudanças permanentes e legítimas de engenharia de tráfego (ex.: migração de cabo submarino ou mudança de peering BGP). Em produção, exige janela deslizante de recalibração periódica.
  2. **Ruído de rajada curta:** Cada coleta do RIPE Atlas envia apenas 3 pacotes ICMP (`sent = 3`), tornando a estimativa pontual de `jitter_ms` e `perda_pct` (degraus de 33,3%) sensível a flutuações momentâneas.
  3. **Representatividade de borda:** Os *Anchors* do RIPE Atlas estão hospedados em *data centers* e pontos de troca de tráfego (IXPs) de alta disponibilidade, não refletindo a perda de pacotes de redes Wi-Fi domésticas ou de acesso de campus universitário.

---

## 5. Ficha da árvore

| Campo | Conteúdo |
|---|---|
| **Problema** | Classificar cada medição em `OK`, `RISCO` ou `FALHA` pelo desvio relativo ao baseline histórico do próprio fluxo. |
| **Unidade** | Uma medição ICMP (rajada de 4 minutos) de um par `(measurement_id, probe_id)` no Período B. |
| **Baseline** | Calculado exclusivamente no Período A (14 dias), usando Mediana e MAD, com piso mínimo de 1.500 RTTs válidos por fluxo. |
| **Colunas** | `z_robusto`, `aumento_pct`, `jitter_relativo`, `perda_pct`, `timeout_atual`, `n5_timeout`, `n5_aumento80`, `n5_risco` (Documentadas em `docs/dicionario_dados_v0.4.md`). |
| **Árvore** | `DecisionTreeClassifier(criterion='gini', max_depth=7, random_state=42)` — 7 níveis de profundidade real e 16 folhas terminais. |
| **Teste (uma vez)** | **F1 Macro = 1.0000** e **Recall de FALHA = 1.0000** (52.149 amostras); nos fluxos inéditos (*holdout*): **F1 Macro = 0.9997**. |
| **O que ela não faz** | Não classifica distância geográfica, não usa RTT em milissegundos, não prevê o futuro sem histórico e não opera em fluxo sem ficha de baseline prévia. |
| **Como reproduzir** | Instalar dependências via `requirements.txt`, validar parâmetros em `config/` e executar a sequência `notebooks/01_coleta_bruta.ipynb` ➔ `02_baseline_rotulagem.ipynb` ➔ `04_comparacao_modelos.ipynb`. |

---

## 6. Scrum e diário

- [x] Board atualizado

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
|---|---|---|---|
| **Breno Brasil de Souza** | Coordenação da entrega final (Tarefa 5), execução do teste lacrado, validação de fluxos inéditos e governança Git. | Garantir o isolamento estrito na avaliação de fluxos não vistos no treino. | Manter o rigor de reprodutibilidade e empacotamento MLOps na apresentação final. |
| **Beatriz Gonçalves da Silva** | Consolidação da Ficha da Árvore e atualização do Dicionário de Dados v0.4 (`docs/dicionario_dados_v0.4.md`). | Padronizar as unidades e fórmulas exatas de todas as 8 variáveis relativas. | Utilizar a ficha técnica como referência rápida durante a arguição. |
| **Enzo Moraes Sousa** | Auditoria da Matriz 3×3 no conjunto de teste (52.149 linhas) e verificação das métricas de precisão e recall. | Analisar criticamente o F1=1.0000 à luz da política determinística de rotulagem. | Destacar a diferença honesta entre aprender a política e prever falhas futuras. |
| **Natsumi Goto** | Inspeção dos casos concretos no teste e rastreamento da única divergência no experimento de fluxo inédito. | Isolar no Pandas a amostra exata (`timestamp 1789621000`) que desviou na fronteira de decisão. | Levar o estudo de caso real para enriquecer a discussão de resultados. |
| **Pedro Viana da Silva** | Script do experimento *Leave-Flows-Out* separando a rota intercontinental (252 ms) e a rota local (0,32 ms). | Filtrar pares compostos sem vazar registros para o fit da árvore de validação espacial. | Manter testes de generalização fora da amostra como padrão em projetos futuros. |
| **Vitória Alessandra das Neves** | Redação da seção de limitações operacionais (Data Drift, rajada curta do RIPE e topologia dos Anchors). | Conectar os limites físicos do protocolo ICMP com o comportamento estatístico da árvore. | Apresentar as limitações com maturidade técnica na defesa do projeto. |

---

## Rubrica — Tarefa 5 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Árvore final legível | 1,0 | Regras em português, colunas relativas, parâmetros da Tarefa 4 | | |
| Teste único | 1,5 | Matriz 3×3 em contagem, F1 por classe, F1 macro, casos curto/longo; teste não escolheu a árvore | | |
| Fluxo novo com baseline próprio | 1,0 | Ficha só no período inicial; ou limitação declarada se faltou fluxo | | |
| Ficha + diário | 0,5 | Ficha preenchida e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
