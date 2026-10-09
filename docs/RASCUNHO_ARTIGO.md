# Rascunho Oficial do Artigo - Fase 3
*(Use este documento para dividir as tarefas de redação entre o grupo. Quando estiver pronto, passaremos o conteúdo para o HTML).*

---

## 0. Cabeçalho e Autoria
* **Título:** Árvore, Floresta ou Boosting?
* **Subtítulo:** A busca pelo modelo ideal para previsão de falhas em redes geograficamente distribuídas usando Desvio Relativo.
* **Autores:** 
  * *(Adicionar para cada membro: Nome, Mini-bio [ex: Estudante de TI, 4º Semestre], Link do GitHub e LinkedIn. Atenção à LGPD: Não coloquem e-mails pessoais ou telefones).*

---

## 1. Introdução (O Problema)
* **Objetivo da seção:** Explicar para um aluno de TI qual é o problema de redes que estamos resolvendo.
* **Tópicos para escrever:**
  * O monitoramento clássico usa latência absoluta (Ex: Alarme se RTT > 200ms).
  * Por que isso falha numa rede global? (200ms no Brasil é falha, mas Brasil-Europa é normal).
  * O que o leitor vai aprender? (Como usamos Inteligência Artificial e a métrica de *Z-Robusto* para julgar a rede pelo "desvio" e não pelo tempo bruto, e qual algoritmo é melhor para isso).

---

## 2. Conceitos: Os Três Modelos (O Core do Artigo)
* **Objetivo da seção:** Explicar didaticamente (com exemplos) como cada modelo funciona antes de jogar a matemática pesada.

### 2.1 Árvore de Decisão
* **O que é:** Um modelo simples de perguntas e respostas.
* **Para escrever:** Dar um exemplo prático ("O pacote excedeu o Z-Robusto de 3? Se sim, é risco..."). Citar que é muito rápido e interpretável, mas sofre de *overfitting* (decora os dados).

### 2.2 Random Forest (O conceito de Bagging)
* **O que é:** Várias árvores treinadas em paralelo com amostras diferentes, decidindo por votação.
* **Para escrever:** Explicar o que é *Bagging* de forma simples. Reduz a variância, mas perde um pouco da interpretabilidade (é uma "caixa preta" parcial).

### 2.3 XGBoost (O conceito de Boosting)
* **O que é:** Árvores treinadas em sequência, onde a Árvore 2 tenta consertar os erros cometidos pela Árvore 1.
* **Para escrever:** Explicar a sacada do *Boosting*. Ele não vota igual a floresta, ele evolui. Citar o ajuste de taxa de aprendizado (*learning rate*).

---

## 3. O Experimento e Ajuste Honesto
* **Objetivo da seção:** Provar que a competição foi justa (Regra da Professora).
* **Dados para usar no texto:**
  * Usamos o dataset do RIPE Atlas com **69 fluxos** (173.674 pacotes).
  * Dividimos temporalmente: Treino (50%), Validação (20%), Teste (30%).
  * Usamos o **GridSearchCV** do `scikit-learn` para ajuste hiperparâmetros (Não chutamos nada, o computador testou todas as combinações).

---

## 4. Resultados (Os Números do Nosso Projeto)
*(Aqui estão os números reais que eu extraí do nosso `.joblib` e do `Notebook 04`. Basta vocês formatarem em texto).*

* **O Campeão Absoluto:** XGBoost.
* **Hiperparâmetros Vencedores:** 100 Árvores, Profundidade 4, Learning Rate 0.05.
* **O que a IA achou mais importante?**
  1. `z_robusto` (36.37%)
  2. `n5_risco` (27.67%)
  3. `jitter_relativo` (20.30%)
* **Latência (Tempo de Predição):** O XGBoost julgou milhares de pacotes da validação em poucos milissegundos. Arquivo final pesa apenas `372 KB`.
* **Imagens a incluir:** (As imagens já foram geradas na pasta `docs/`).
  1. Desenho de uma Árvore Simples.
  2. Esquema de Bagging vs Boosting (O grupo precisa desenhar/buscar).
  3. Matriz de Confusão do XGBoost (`matriz_xgboost.png`).

---

## 5. Recomendação e Limitações (Data Drift)
* **Recomendação:** Nós recomendamos o **XGBoost** porque ele combinou um F1-Score altíssimo com um arquivo extremamente leve (372 KB), ideal para rodar em tempo real em servidores de monitoramento de redes sem gargalos de CPU.
* **Limitações (Data Drift):** Explicar que a rede física muda (cabos rompem, roteadores pifam). O que é normal hoje, pode não ser mês que vem. O modelo não duraria para sempre; precisaria ser re-treinado periodicamente.

---

## 6. Referências
* Listar entre 3 a 7 links bons (Documentação oficial do XGBoost, Scikit-learn, Artigo NSL-KDD, etc).
