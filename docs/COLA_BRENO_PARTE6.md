# 🎯 Cola Rápida do Breno — Parte 6 (Slides 8, 9 e 10 + Demo NOC)

Guia enxuto de bolso com **palavras-chave, números exatos e gatilhos** para a sua fala na Feira.

---

## 🔑 1. Palavras-Chave da Sua Fala (Ordem Lógica)

1. **Tirar do notebook e levar para produção:** API REST em **Flask** escutando em tempo real (`http://127.0.0.1:5000`).
2. **Pacote canônico (`Grupo05.zip` — `27,9 KB`):** `modelo.joblib` (`45,6 KB`), `baseline.csv` (`69 fluxos`) e `metadados.json`.
3. **Sem *training-serving skew* (paridade 100%):** Mesma conta no treino e na API via módulo único `src/cyphernet/features.py` (**0 divergências em 173.674 linhas**).
4. **Governança MLOps:** Hash criptográfico **SHA-256** verificado no boot da API.
5. **Memória curta em $O(1)$:** Fila circular (`JanelaFluxo` / `deque(maxlen=5)`) independente por `fluxo_id` (~20 min).
6. **Duplo horizonte em `< 1 ms`:** Diagnóstico de agora (**`T=0`**) + Previsão proativa (**`T+1` = +4 min** e **`H3` = +12 min**).

---

## 📊 2. Os 4 Blocos do Topo do Painel NOC (Para Apontar com o Mouse)

| Bloco no Painel | O que significa | Frase curta na hora |
| :--- | :--- | :--- |
| **`69` Fluxos Catalogados** | Rotas reais (`probe\|destino`) com baseline própria | *"69 caminhos reais da Internet com régua própria."* |
| **`Árvore (d=7)` Modelo Canônico** | `16` folhas, caixa-branca, roda `T=0` e `T+1` | *"16 regras claras rodando presente e futuro juntos."* |
| **`~1 ms` Latência de Inferência** | Medido em tempo real com `time.perf_counter()` | *"A IA pensa e responde em ~1 milissegundo."* |
| **`8 + 3` Features** | 8 base + 3 tendência, `1,4826·MAD` e janela `n5` | *"Métricas relativas + tendência das últimas 5 medições."* |

---

## 🧾 3. Os 3 Botões JSON no Cabeçalho (Se Perguntarem da API)

* **`[Healthcheck]` (`GET /api/saude`):** Sinal de vida da API, status do modelo, uptime e **SHA-256**.
* **`[Metadados API]` (`GET /api/modelo`):** Ficha técnica — família (`arvore_decisao`), `max_depth=7`, tamanho (`45,6 KB`) e ordem exata das features.
* **`[Histórico Previsões]` (`GET /api/previsoes`):** Log das últimas **500** predições com features calculadas, `T=0`, `T+1` e `H3`.
* **Entrada da API (`POST /api/previsoes`):** Recebe só `probe_id`, `dst_addr`, `rtt_ms`, `perda_pct` e `jitter_ms` — a API busca a baseline e calcula tudo sozinha.

---

## ⚡ 4. Coreografia da Demo Ao Vivo (4 Passos no Painel)

*(Deixe selecionado o fluxo **`6251|193.0.0.164`** — mediana `28,25 ms`, MAD `0,164 ms`)*

1. **Normal (`OK`):** RTT ~`28 ms`, perda `0%` &rarr; Z perto de 0, confiança ~100% em **OK**.
2. **Gray Failure (`RISCO`):** Suba o RTT levemente (`~28,8 ms`) / jitter e faça 2 cliques/movimentos &rarr; `n5_risco >= 2` dispara **RISCO** sem ter perda de pacotes.
3. **Blackout (`FALHA` + `NaN`):** Puxe Perda para `100%` &rarr; `z_robusto = NaN` (não mascarado com 0 ou mediana!) e a árvore aciona **FALHA**.
4. **RIPE Atlas Ao Vivo:** Clique em **"Consultar API RIPE Atlas ao Vivo"** &rarr; puxa pings reais da última hora na Europa.
   * **Se aparecerem rotas em `FALHA` no ao vivo:** *"Isso é **Data Drift** real! A baseline é de setembro (2 meses atrás); uma mudança de `1,9 ms` na rota já dispara o alerta, por isso prevemos recalibração semanal."*
   * **Plano B (se o Wi-Fi da feira falhar):** Mostrar que o simulador e os JSONs (`/api/saude`, `/api/previsoes`) rodam **100% locais** em `127.0.0.1:5000`.

---

## 🛡️ 5. Respostas-Relâmpago para Perguntas Difíceis

* **Reiniciou o servidor, perde a janela de 5?** &rarr; *"Sim, hoje fica em RAM (`deque`) com `min_periods=1` (funciona desde a 1ª medição); em escala distribuída iria para **Redis**."*
* **Chegou rota fora das 69?** &rarr; *"Retorna **HTTP 404** explícito para não usar régua errada; evolução futura é warm-up automático."*
* **Por que o site da feira (GitHub Pages) também funciona?** &rarr; *"O GitHub Pages roda modo demonstrativo em JS, e nossa API Flask tem **CORS** liberado para conectar direto nele quando hospedada."*
* **Fechamento (Slide 10):** *"Apontem a câmera para o **QR Code** para testar no celular e ver o vídeo pitch de 90s!"*
