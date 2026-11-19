# 🎤 Roteiro de Apresentação e Estande — CypherNet: Vigia de Redes (Feira 2026)

Este roteiro foi desenhado para funcionar tanto com **visitantes gerais** (pessoas de fora da faculdade e outros cursos) quanto com **professores e alunos da área técnica**.

---

## 🖥️ 1. Como abrir os slides no dia da Feira

1. **Pelo navegador local (funciona mesmo sem internet):**
   * Abra o arquivo [`docs/apresentacao_feira.html`](apresentacao_feira.html) no Chrome/Edge.
   * Aperte **`F`** (ou **`F11`**) para colocar em **Tela Cheia**.
   * Navegue com as setas **`←`** e **`→`** (ou `Espaço`).
   * Se quiser exportar para PDF, clique no botão **`⎙ PDF`** na barra inferior (já está configurado em modo paisagem).
2. **Pelo link online no GitHub Pages:**
   * `https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/apresentacao_feira.html`

---

## 🗣️ 2. Pitch de 30 Segundos (Para Visitante Geral / Público Externo)

> *"Sabe quando a internet não caiu de vez, mas fica travando em chamadas de vídeo ou jogos e o provedor diz que 'está tudo normal'? Isso acontece porque os sistemas antigos só olham um limite fixo de velocidade.*
> *O **CypherNet** é um vigia inteligente de redes: ele aprende qual é o comportamento normal de **cada rota** usando dados reais da Internet e, com uma **Árvore de Decisão**, consegue classificar na hora se a conexão está **OK**, em **RISCO** (degradando antes de cair) ou em **FALHA** — e ainda tenta antecipar falhas graduais 4 minutos antes."*

---

## 🎓 3. Pitch Técnico de 2 Minutos (Para Professores e Alunos de TI)

Use a sequência dos **10 slides**:
* **Slides 1 a 3 (Problema e Ideia):** Explique *Gray Failures* e por que latência absoluta (`avg`) não funciona em redes globais. Mostre as 3 classes (**OK, RISCO, FALHA**).
* **Slides 4 e 5 (Dados e Features):** Cite os dados reais do **RIPE Atlas (`msm_id = 9333345`)**, **69 fluxos**, **173.674 medições**, split temporal **50/20/30** (sem *data leakage*) e a baseline de 7 dias com **Mediana + `1,4826 × MAD`**. Destaque o tratamento nativo de `NaN` em timeouts (nunca zerado nem substituído pela mediana).
* **Slides 6 e 7 (Modelo e Resultados):** Explique a escolha da **Árvore de Decisão (`max_depth=7`, 16 folhas)**: empate técnico com Random Forest/XGBoost no $T=0$ (**F1 Macro = `1,0000`**), resposta em **`~0,2 ms`**, apenas **`45,6 KB`**, e transparência de **caixa-branca**. No modo proativo (**$T+1 = +4\text{ min}$**, com `z_max5` e `z_tendencia5`), atinge **F1 Macro = `0,5699`** e antecipa **~1 em cada 3 falhas futuras (`31,86%` Recall)**.
* **Slides 8 e 9 (API + Demo ao Vivo):** Mostre o fluxo Flask (`/api/saude`, `/api/modelo`, `/api/previsoes`) e pule para o Dashboard ao vivo!

---

## ⚡ 4. Demonstração Ao Vivo no Estande (3 Cliques)

Antes do público chegar, abra um terminal na pasta `ESTRUTURA-DE-DADOS-II-PROJ-1` e rode:

```bash
python producao/app/server.py
```

Depois abra **`http://127.0.0.1:5000`** em outra aba do navegador (ao lado dos slides):
1. **Teste 1 (Operação Normal):** Deixe o RTT na mediana da rota selecionada e perda `0%` &rarr; mostra **OK (~100%)**.
2. **Teste 2 (Degradação / Gray Failure):** Arraste o RTT para ~40% acima da mediana e mova o slider algumas vezes (para encher a janela de 5 medições `n5_risco`) &rarr; mostra a transição para **RISCO** e atualiza a previsão futura **T+1**.
3. **Teste 3 (Timeout / RIPE Atlas ao Vivo):** Coloque perda em `100%` (mostra **FALHA** com `z_robusto = NaN` preservado!) ou clique em **"Consultar API RIPE Atlas ao Vivo"** para classificar pings reais da Internet coletados na última hora.

---

## ✅ 5. Checklist do Estande

* [ ] Servidor Flask rodando em `http://127.0.0.1:5000` (aba 1)
* [ ] Slides [`docs/apresentacao_feira.html`](apresentacao_feira.html) abertos em tela cheia (aba 2)
* [ ] Quando ninguém estiver apresentando, deixar no **Slide 10** (com o QR Code grande na tela para os visitantes escanearem!)
* [ ] Imprimir ou deixar visível o card [`docs/qrcode_cyphernet_card_mostra.png`](qrcode_cyphernet_card_mostra.png) na mesa do estande.
