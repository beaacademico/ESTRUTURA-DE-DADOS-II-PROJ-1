# 🎙️ Roteiro da Apresentação na Feira — Dividido em 6 Partes (Grupo 05)

Roteiro sincronizado com os slides [`apresentacao_feira.html`](apresentacao_feira.html) para apresentação em grupo (aprox. **3 a 4 minutos no total**, ~30–40 segundos por integrante), equilibrando linguagem clara para **visitantes externos** e rigor técnico para **professores e alunos**.

---

## 🧩 Visão Rápida da Divisão

| Parte | Tema | Slides | Integrante |
| :---: | :--- | :---: | :--- |
| **Parte 1** | Abertura e o Problema (*Gray Failures* & Limite Fixo) | Slides 1 e 2 | _________________ |
| **Parte 2** | A Solução CypherNet e os Dados Reais (RIPE Atlas) | Slides 3 e 4 | _________________ |
| **Parte 3** | Baseline Robusta, Features e Tratamento de `NaN` | Slide 5 | _________________ |
| **Parte 4** | Modelo Escolhido (Árvore `max_depth=7`) e Comparação | Slide 6 | _________________ |
| **Parte 5** | Resultados ($T=0$ vs. Previsão Proativa $T+1$) | Slide 7 | _________________ |
| **Parte 6** | Arquitetura MLOps, Demo ao Vivo e QR Code | Slides 8, 9 e 10 | Breno |

---

## 🔹 Parte 1 — Abertura e o Problema Real (Slides 1 e 2)

**Na tela:** Slide 1 (Capa) &rarr; avançar para o Slide 2 (*Por que a Internet trava antes de cair?*).

**Fala sugerida:**
> *"Olá, pessoal! Nós somos o Grupo 05 e criamos o **CypherNet: Vigia de Redes**.*
> *Sabe quando você está numa chamada de vídeo ou jogando e a Internet começa a travar do nada, mas quando você liga no suporte eles dizem que 'o sinal está normal'? Na engenharia de redes, isso tem nome: **Gray Failure** — uma falha cinzenta, onde a conexão ainda não caiu de vez, mas já está degradando aos poucos.*
> *Os sistemas tradicionais falham nisso porque usam um **limite fixo** igual para tudo, tipo 'acima de 100 ms é ruim'. Só que 40 ms é ótimo para um servidor na Europa, mas é péssimo para uma rota local que normalmente responde em 2 ms. É igual à pressão arterial: o que é normal varia de pessoa para pessoa — e, na rede, varia de rota para rota."*

**Gancho de transição:** *"Para resolver isso sem limite fixo, a [Nome da Parte 2] vai explicar como o CypherNet classifica as conexões e de onde tiramos os dados reais."*

---

## 🔹 Parte 2 — A Solução CypherNet e Dados Reais (Slides 3 e 4)

**Na tela:** Slide 3 (*3 Estados Operacionais*) &rarr; avançar para o Slide 4 (*Telemetria Global RIPE Atlas*).

**Fala sugerida:**
> *"O CypherNet observa cada rota individualmente e traduz o comportamento dela em três estados claros: **OK** (operação normal), **RISCO** (degradação moderada persistente, hora de agir antes de cair) e **FALHA** (perda crítica de pacotes ou indisponibilidade).*
> *E o mais importante: nós não usamos dados inventados. Coletamos telemetria real da Internet pelo projeto **RIPE Atlas** (`msm_id = 9333345`), monitorando **69 rotas globais** com disparos de ping a cada **4 minutos**.*
> *Ao todo, trabalhamos com **173.674 medições reais**, divididas em ordem estritamente cronológica: **50% para treino, 20% para validação e 30% finais para teste**, evitando qualquer vazamento de dados do futuro para o passado."*

**Gancho de transição:** *"Agora o [Nome da Parte 3] vai mostrar como transformamos esses pings brutos em inteligência para o modelo."*

---

## 🔹 Parte 3 — Baseline Robusta, Features e Tratamento de `NaN` (Slide 5)

**Na tela:** Slide 5 (*Baseline Robusta & Engenharia de Atributos*).

**Fala sugerida:**
> *"Separamos os primeiros **7 dias** de coleta exclusivamente para criar a **baseline histórica** de cada uma das 69 rotas. Em vez de média e desvio padrão — que são facilmente distorcidos por um único pico — usamos **Mediana e MAD** (Desvio Absoluto Mediano) com o fator `1,4826`, calculando o `z_robusto`.*
> *O modelo não recebe IP nem país, para não decorar endereços; ele recebe **8 métricas relativas** (como variação percentual, jitter relativo, perda e contagem de alertas nas últimas 5 medições) mais **3 métricas de tendência**.*
> *E um detalhe técnico fundamental: quando dá **timeout** (100% de perda), a latência não existe (`NaN`). Nós **nunca** substituímos `NaN` por zero nem pela mediana, porque isso mascararia um apagão total como latência normal."*

**Gancho de transição:** *"Com esses dados tratados, o [Nome da Parte 4] vai explicar qual algoritmo de Inteligência Artificial escolhemos e por quê."*

---

## 🔹 Parte 4 — Escolha do Modelo: Árvore de Decisão vs. Ensembles (Slide 6)

**Na tela:** Slide 6 (*Por que escolhemos a Árvore de Decisão?*).

**Fala sugerida:**
> *"Comparamos três algoritmos clássicos: **Árvore de Decisão**, **Random Forest** (várias árvores votando em paralelo) e **XGBoost** (árvores em sequência corrigindo erros anteriores).*
> *Nós escolhemos a **Árvore de Decisão com profundidade máxima 7** como nosso modelo principal. Primeiro, porque ela empatou em desempenho com os ensembles mais pesados. Segundo, porque num Centro de Operações de Rede (NOC), o engenheiro precisa de **transparência (caixa-branca)**: nossa árvore gera apenas **16 folhas** com regras `SE ... ENTÃO` claras, pesa só **45,6 KB** e responde em **0,2 milissegundo**."*

**Gancho de transição:** *"E quais foram os números reais que esses modelos alcançaram no teste? A [Nome da Parte 5] vai mostrar."*

---

## 🔹 Parte 5 — Resultados: Diagnóstico Atual ($T=0$) vs. Previsão Proativa ($T+1$) (Slide 7)

**Na tela:** Slide 7 (*Resultados Experimentais*).

**Fala sugerida:**
> *"Avaliamos nosso sistema em dois horizontes sobre as **52.149 amostras de teste**.*
> *No **Diagnóstico Instantâneo (`T=0`)**, que classifica o estado da rede no momento em que a medição chega, a Árvore de Decisão atingiu **F1-Macro de 1,0000** — reconstruindo com precisão os critérios operacionais.*
> *Já na **Previsão Proativa (`T+1`)**, onde escondemos o estado atual e desafiamos o modelo a prever como a rede vai estar **daqui a 4 minutos**, aplicamos pesos maiores para erros em risco e falha e alcançamos **F1-Macro de 0,5699** na Árvore (e **0,5824** no Random Forest), antecipando cerca de **1 em cada 3 falhas futuras** (31,86% de Recall). Isso acontece porque quedas físicas súbitas não dão aviso prévio, mas falhas graduais geram sinais de tendência capturados pelo `z_max5` e `z_tendencia5`."*

**Gancho de transição:** *"Por fim, o [Nome da Parte 6] vai mostrar como tudo isso roda em produção e fazer uma demonstração ao vivo."*

---

## 🔹 Parte 6 — Arquitetura MLOps, Demonstração ao Vivo e QR Code (Slides 8, 9 e 10)

**Na tela:** Slide 8 (*Arquitetura MLOps*) &rarr; Slide 9 (*Demo ao Vivo*) &rarr; alternar para o Dashboard Flask (`http://127.0.0.1:5000`) &rarr; finalizar no Slide 10 (*QR Code*).

**Fala sugerida:**
> *"Para tirar o modelo do papel, empacotamos o artefato canônico em `Grupo05.zip` (`modelo.joblib`, `baseline.csv` e `metadados.json`) com verificação criptográfica **SHA-256** e subimos uma **API REST em Flask**.*
> *Quando chega uma medição em `POST /api/previsoes`, a API consulta a baseline da rota, atualiza a fila circular das últimas 5 medições e devolve o diagnóstico `T=0` e a previsão `T+1` em menos de 1 milissegundo.*
> *(Mostrar rapidamente na tela do Dashboard `http://127.0.0.1:5000`: rota normal `OK` &rarr; degradação gradual `RISCO` &rarr; timeout `FALHA` ou botão RIPE Atlas ao vivo).*
> *Quem quiser testar no próprio celular, pode apontar a câmera para este **QR Code** para abrir a página interativa da feira e assistir ao nosso vídeo pitch de 90 segundos. Muito obrigado!"*
