# Plano de Melhorias e Evolução do Preditor de Redes

**Projeto:** Preditor de Degradação de Redes com RTT Normalizado  
**Equipe:** Grupo 5 (Breno Brasil de Souza, Beatriz Gonçalves da Silva, Enzo Moraes Sousa, Natsumi Goto, Pedro Viana da Silva, Vitória Alessandra das Neves)  
**Disciplina:** Estruturas de Dados II / Redes de Computadores  
**Status do Repositório:** Planejamento de Evolução Pós-Apresentação  

---

## 1. Contexto e Diagnóstico Pós-Apresentação

Na primeira apresentação do Artigo Técnico, o projeto obteve uma avaliação mediana (~3/5). A principal ressalva levantada pela banca foi a obtenção de métricas perfeitas (**F1-Score Macro = 1,0000**), enquanto os projetos de maior destaque da turma (como o Grupo 16) atingiram métricas na faixa de **0,78 a 0,82**.

Após análise forense dos dados e estudo comparativo do projeto referência compartilhado pela turma, diagnosticamos as causas fundamentais e desenhamos este plano de melhorias:

### O Diagnóstico Técnico da Discrepância de Métricas:
1. **Classificação de Estado Presente ($T=0$) vs Predição Antecipada ($T+\Delta t$):**
   * O nosso modelo atual foi treinado para **classificar a condição no instante exato da medição** com base em uma política de rotulagem determinística. A árvore de decisão simplesmente aprendeu a fronteira matemática exata do algoritmo de rotulagem, atingindo 1,0000 no laboratório.
   * O projeto de destaque formulou o problema como **Predição Antecipada (Forecasting com horizonte de 12 minutos à frente)**. Prever a falha antes que ela aconteça em uma rede real envolve incerteza estocástica, onde um F1 de **~0,80 é um resultado realista, robusto e de alto valor prático**.
2. **Fragilidade a Ruído Estocástico (Data Drift):**
   * Nossos testes de estresse provaram que ao injetar apenas 5% de ruído gaussiano (oscilação real de jitter e latência), o F1 da nossa árvore despenca de 1,0000 para **0,7466**, provando que o modelo de laboratório sofria de extrema rigidez nas fronteiras de decisão.
3. **Maturidade de Engenharia e MLOps:**
   * O projeto destaque implementou deploy em nuvem com API REST documentada via **Swagger/OpenAPI**, rastreabilidade criptográfica por **SHA-256** do modelo e embasamento na literatura seminal de **Gray Failure** (falhas cinzentas/parciais).

---

## 2. Eixo 1: Evolução da Modelagem e Ciência de Dados

### 2.1 Transição de Classificação Pontual para Predição Antecipada (*Lead Time*)
* **Objetivo:** Mudar o objetivo do modelo de *"o que a rota está sentindo agora?"* para *"esta rota vai degradar nos próximos 10 a 15 minutos?"*.
* **Ação Técnica:**
  * Criar no pipeline de rotulagem uma janela de avanço temporal ($\text{offset} = +15\text{ minutos}$): o vetor de features no tempo $t$ passa a ter como alvo o pior estado da rede observado entre $t+5\text{m}$ e $t+15\text{m}$.
  * Com isso, o F1 esperado convergirá naturalmente para **0,78 ~ 0,85**, refletindo um verdadeiro sistema de **Alerta Prévio (*Early Warning System*)** aceito pela comunidade científica.

### 2.2 Aprendizado Sensível a Custo (*Cost-Sensitive Learning*)
* **Objetivo:** Alinhar as penalidades do algoritmo com a realidade dos centros de operações de rede (NOC).
* **Ação Técnica:**
  * Na operação de telecomunicações, um **Falso Negativo de FALHA** (a rede caiu e o modelo não avisou) custa dezenas de vezes mais que um **Falso Positivo de RISCO** (o modelo alertou preventivamente e o tráfego normalizou).
  * Configurar a matriz de custos no XGBoost e Random Forest via parâmetro de pesos de classe (`class_weight` / `scale_pos_weight`), forçando os estimadores a priorizar o Recall de Falha.

### 2.3 Engenharia de Atributos de Telecomunicações (Inédita)
* **Objetivo:** Adicionar atributos dinâmicos de tendência sem copiar os métodos de outros grupos.
* **Novas Features Planejadas:**
  1. `derivada_rtt_5`: A inclinação linear (taxa de variação $d(RTT)/dt$) nas últimas 5 amostras, diferenciando se a latência está estável ou acelerando em rampa de saturação;
  2. `razao_p95_mediana`: A razão entre o percentil 95 da janela recente e a mediana histórica do Período A, capturando caudas longas de perda e jitter;
  3. `volatilidade_mad`: Desvio absoluto móvel das últimas 5 janelas normalizado pelo MAD histórico.

---

## 3. Eixo 2: MLOps, Engenharia de Software e Deploy em Produção

### 3.1 Rastreabilidade Criptográfica com Hash SHA-256
* **Objetivo:** Garantir integridade e governança de auditoria sobre o artefato serializado em produção.
* **Ação Técnica:**
  * Ao inicializar a aplicação, o backend calcula automaticamente o hash criptográfico `SHA-256` do arquivo `.joblib` carregado na memória RAM.
  * O hash é retornado em todos os diagnósticos e nas respostas dos endpoints de status, assegurando que o modelo que está servindo inferências é matematicamente idêntico ao modelo avaliado no notebook.

### 3.2 Padronização da API REST com Documentação OpenAPI / Swagger
* **Objetivo:** Disponibilizar contratos de interface claros e interativos para integração com ferramentas de monitoramento (Zabbix, Grafana, Datadog).
* **Endpoints a Implementar:**
  * `GET /api/saude`: Healthcheck da aplicação, retornando status dos buffers, memória e o SHA-256 do modelo;
  * `GET /api/modelo`: Metadados completos do modelo (hiperparâmetros, classes, data de treinamento, versão do Scikit-Learn/XGBoost);
  * `POST /api/previsoes`: Recebe métricas de um fluxo, valida tipos, imputa nulos de forma segura e retorna predição com probabilidades de cada classe;
  * `GET /api/previsoes`: Histórico das últimas $N$ inferências registradas para auditoria;
  * `GET /swagger`: Interface gráfica interativa para teste manual dos endpoints.

### 3.3 Integração do Dashboard de NOC (Frontend)
* **Objetivo:** Transformar a interface que já construímos no protótipo Flask em parte oficial da suíte de produção do projeto.
* **Funcionalidades Centrais:**
  * Painel operacional em tempo real dos 69 fluxos mundiais;
  * Playground interativo de injeção de parâmetros com sliders de RTT, perda e jitter;
  * Simulador de Data Drift com injeção de ruído paramétrico;
  * Conector com a API do RIPE Atlas para demonstração de predição ao vivo.

---

## 4. Eixo 3: Enriquecimento Acadêmico e Metodológico do Artigo

### 4.1 Incorporação Formal da Literatura de *Gray Failure*
* **Embasamento:** Citar os trabalhos seminais de **Huang et al. (HotOS 2017 - Microsoft Research)** e **Guo et al. (Pingmesh - SIGCOMM 2015)**.
* **Narrativa do Artigo:** 
  * Reenquadrar o problema explicando que quedas totais (*fail-stop*) são fáceis de detectar por qualquer ping simples;
  * O verdadeiro desafio técnico que justifica o uso de Machine Learning são as **Falhas Cinzentas (*Gray Failures*)**: degradações sutis e intermitentes onde o enlace continua formalmente "ativo", mas o desvio relativo de latência e perda quebra o SLA das aplicações distribuídas.

### 4.2 Transparência Metodológica sobre o Comportamento sob Ruído
* Documentar abertamente a tabela de estresse (0% a 50% de ruído) gerada nos nossos experimentos:
  * Mostrar com honestidade científica que o F1 de 1,0000 do laboratório cai para ~0,78 sob 5% de perturbação real;
  * Defender que o XGBoost se destaca em relação à Árvore de Decisão simples exatamente pela capacidade de preservar a separabilidade de classes através de árvores aditivas e regularização L1/L2.

---

## 5. Backlog de Execução e Próximos Passos (Scrum)

| Sprint / Etapa | Entregável / Ação | Responsável Sugerido |
| :--- | :--- | :--- |
| **Sprint 1 (Backend & MLOps)** | Implementar hash SHA-256, endpoints `/api/saude`, `/api/modelo` e Swagger no servidor Flask. | Breno (Scrum Master / Dev) |
| **Sprint 2 (Engenharia de Dados)** | Construir o script de rotulagem antecipada ($T+15\text{m}$) e gerar os novos atributos de aceleração ($d(RTT)/dt$). | Pedro / Vitória |
| **Sprint 3 (Treinamento & Benchmark)**| Re-treinar o XGBoost com matriz de custo (*Cost-Sensitive*) e gerar nova matriz de confusão sob horizonte preditivo. | Breno / Enzo |
| **Sprint 4 (Artigo & Publicação)** | Atualizar o artigo em `docs/index.html` incorporando a literatura de *Gray Failure* e o link do novo Swagger/NOC. | Beatriz / Natsumi |

---

*Documento elaborado com base na auditoria experimental e nos padrões de referência da disciplina.*
