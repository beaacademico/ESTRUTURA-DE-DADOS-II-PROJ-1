# 📄 Rascunho Oficial do Artigo - Fase 3
> **Objetivo:** Produzir o artigo técnico comparativo (Árvore de Decisão vs. Random Forest vs. XGBoost) e estruturar a apresentação de 5 minutos do grupo.

---

## 👥 Quadro de Alocação do Grupo (Escolha Livre)

| Parte | Módulo / Seção | Responsável | Status |
| :---: | :--- | :--- | :---: |
| **Parte 1** | Introdução, Cenário de Redes e Autoria/LGPD | `[A definir]` | ⏳ Pendente |
| **Parte 2** | Teoria I: Árvore de Decisão (Conceitos Básicos) | **Vitória Alessandra** | ✅ Concluído (Integrado no HTML) |
| **Parte 3** | Teoria II: Random Forest vs. XGBoost (Ensembles) | **Natsumi Goto** | ✅ Concluído (Integrado no HTML) |
| **Parte 4** | O Experimento Justo (GridSearch e Código Python) | **Breno Brasil** | ✅ Concluído (Integrado no HTML) |
| **Parte 5** | Resultados, Métricas e Matrizes de Confusão | `[A definir]` | ⏳ Pendente |
| **Parte 6** | Veredito, MLOps (Data Drift) e Quadro de Observações | `[A definir]` | ⏳ Pendente |

---

## 📌 Detalhamento das 6 Partes

### 👤 Parte 1: Introdução, Cenário de Redes e Autoria
* **Responsável:** `[A definir]`
* **Tempo na Apresentação:** ~50 segundos (Abertura e Contextualização).
* **O que deve redigir:**
  1. **Cartões de Autoria (LGPD):** Coletar e estruturar os dados de cada um dos 6 membros (Nome completo, mini-bio acadêmica, links públicos do GitHub e LinkedIn, foto). *Atenção:* Não expor e-mails pessoais ou telefones.
  2. **O Problema de Redes:** Explicar didaticamente por que monitorar redes por "latência fixa" (ex: ping > 200ms) é ineficiente em uma infraestrutura global (200ms em uma rota curta é falha crítica, mas em um cabo submarino intercontinental é o estado normal).
  3. **A Proposta do Grupo:** Apresentar a abordagem do projeto utilizando desvio relativo (*Z-Robusto*) e histórico recente com dados reais da rede RIPE Atlas (69 fluxos).

---

### 👤 Parte 2: Teoria Didática I – Árvore de Decisão
* **Responsável:** `[A definir]`
* **Tempo na Apresentação:** ~50 segundos (Conceito base).
* **O que deve redigir:**
  1. **Intuição:** Explicar a tomada de decisão sequencial por perguntas condicionais simples (*"O Z-Robusto é > 3.5?"*).
  2. **Conceitos Fundamentais:** Definir nó raiz, nós internos, ramos, folhas, critério de divisão (Índice Gini / Entropia), profundidade máxima e poda (*pruning*).
  3. **Vantagens e Limitações:** Alta interpretabilidade humana versus alta propensão a *overfitting* (decorar os dados de treino) e sensibilidade a variações nos dados (alta variância).
  4. **Visual:** Incluir uma figura ilustrativa simples de árvore de decisão para tráfego de rede com legenda e texto alternativo acessível.

---

### 👤 Parte 3: Teoria Didática II – Random Forest vs. XGBoost
* **Responsável:** `[A definir]`
* **Tempo na Apresentação:** ~50 segundos (Confronto dos Ensembles).
* **O que deve redigir:**
  1. **Random Forest (Bagging):** Construção de múltiplas árvores paralelas com amostragem *Bootstrap* e seleção aleatória de atributos. Explicar como a votação por maioria reduz a **variância**.
  2. **XGBoost (Boosting):** Construção de árvores em sequência, onde cada nova árvore foca em corrigir os resíduos (erros) das árvores anteriores. Explicar taxa de aprendizado (*learning rate*), regularização e como isso reduz o **viés**.
  3. **Visual:** Diagrama comparativo esquemático: árvores paralelas com votação (Floresta) versus árvores sequenciais somatórias (XGBoost).

---

### 👤 Parte 4: O Experimento Justo e Código Python
* **Responsável:** **Breno Brasil**
* **Tempo na Apresentação:** ~50 segundos (Rigor metodológico e Engenharia de Software).
* **O que foi redigido e implementado no HTML:**
  1. **Metodologia sem Vazamento (Data Leakage):** Explicar a divisão temporal estrita do Período B (Treino 50% / Validação 20% / Teste 30%), garantindo que os dados do Período A foram usados apenas como baseline e a fixação da semente (`random_state=42`).
  2. **Ajuste Honesto (GridSearchCV):** Explicar que nenhum hiperparâmetro foi chutado; foi usada busca exaustiva em grade para calibrar profundidade, estimadores e taxas nos três modelos com scoring `f1_macro`.
  3. **Show me the Code:** Apresentação modular do código em 3 passos: mapeamento numérico das classes, execução do GridSearch com medição de tempo e persistência do artefato `.joblib`.
* **Roteiro de Fala para a Apresentação (~50 segundos):**
  > *"Olá a todos! Eu sou o Breno, atuei como Scrum Master e Arquiteto de Dados do grupo, e fiquei responsável por estruturar o experimento e a esteira de código.*
  > 
  > *Em Machine Learning para redes, o maior perigo é o vazamento de dados — o famoso Data Leakage. Por isso, blindamos o pipeline: congelamos o Período A exclusivamente para o cálculo do baseline, dividimos o Período B em ordem cronológica estrita em 50% treino, 20% validação e 30% teste lacrado, e fixamos a semente em 42.*
  > 
  > *Para garantir uma disputa justa entre os três modelos, não chutamos parâmetros. Implementamos o GridSearchCV do Scikit-Learn avaliando os modelos pelo F1-Score Macro em três partições. E para fechar o ciclo de engenharia de software, empacotamos o modelo vencedor em um artefato `.joblib` de apenas 372 KB, deixando a IA pronta para rodar em produção com inferência em tempo real."*

---

### 👤 Parte 5: Resultados, Métricas e Matrizes de Confusão
* **Responsável:** `[A definir]`
* **Tempo na Apresentação:** ~50 segundos (Análise dos dados).
* **O que deve redigir:**
  1. **Tabela Comparativa de Métricas:** Preencher e comentar a tabela com Precisão, Recall, F1-Score (macro), tempo de treinamento e tempo de inferência para os 3 modelos.
  2. **Matriz de Confusão:** Explicar a matriz do modelo campeão (usar o arquivo [matriz_xgboost.png](matriz_xgboost.png)).
  3. **Custo dos Erros em Operação de Redes:** Avaliar o impacto de um Falso Positivo (alarme falso que acorda o plantonista de SRE) versus um Falso Negativo (degradação não detectada que afeta os usuários).
  4. **Importância dos Atributos:** Comentar o peso das features extraídas do nosso modelo final:
     * `z_robusto`: **36.37%**
     * `n5_risco`: **27.67%**
     * `jitter_relativo`: **20.30%**
     * Outros atributos (aumento, perda): **~15.66%**

---

### 👤 Parte 6: Recomendação Final, MLOps (Data Drift) e Quadro de Observações
* **Responsável:** `[A definir]`
* **Tempo na Apresentação:** ~50 segundos (Conclusão, produção e deploy).
* **O que deve redigir:**
  1. **Recomendação Justificada:** Defender a escolha do modelo campeão (**XGBoost**) combinando alta acurácia com leveza operacional (arquivo gerado de apenas **372 KB** em `producao/modelo/modelo_final.joblib`, ideal para baixa latência em tempo real).
  2. **Limitações e Data Drift:** Explicar o fenômeno do desvio de conceito/dados na física da rede (rompimentos de rota, mudança de operadora) que demanda monitoramento contínuo e rotinas de retreino.
  3. **Quadro de Observação (Exigência do Projeto):**
     * *Duas referências analisadas:* (ex: documentação oficial do XGBoost e artigo Chen & Guestrin).
     * *Três decisões do grupo:* (ex: adoção do Z-Robusto relativo, uso de GridSearchCV honesto e estruturação MLOps com `.joblib`).
     * *Uma coisa que o grupo decidiu NÃO fazer:* (ex: não utilizar limiares fixos de RTT em milissegundos).
  4. **Deploy e Acesso:** Validar e disponibilizar a URL pública da página funcionando no GitHub Pages.

---

## 🚀 Como Proceder
1. Cada integrante escolhe uma das partes acima e preenche seu nome na tabela inicial.
2. Cada responsável redige o texto do seu bloco neste arquivo `.md` ou diretamente na seção correspondente do [index.html](index.html).
3. Após revisão geral do grupo, atualizamos a página estática e sincronizamos no GitHub.
