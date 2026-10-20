# Dicionário de Dados v0.4 (Modelo Final — Tarefa 5)

Este dicionário consolida o esquema final utilizado na Tarefa 5 (`dataset_rotulado_B_split.csv`), detalhando o papel de cada variável e destacando explicitamente as **8 features relativas** permitidas na Árvore de Decisão Final.

## 1. Variáveis de Identificação e Telemetria Bruta (Fora do Modelo)
*(Utilizadas apenas para rastreamento, auditoria de casos e cálculo prévio do baseline — proibidas como entrada da árvore).*

| Coluna | Tipo | Unidade | Papel no Pipeline |
|---|---|---|---|
| `timestamp` | Inteiro | Epoch (UTC) | Instante da medição; define a ordenação cronológica do split 50/20/30. |
| `measurement_id` | Inteiro | ID | Identificador da campanha de medição no RIPE Atlas (Anchoring Mesh). |
| `probe_id` | Inteiro | ID | Identificador da sonda de origem. |
| `dst_addr` | Texto | IPv4 | Endereço IP do Anchor de destino. |
| `avg`, `min`, `max` | Float | ms | RTT médio, mínimo e máximo da rajada (nulos em caso de timeout). |
| `sent`, `rcvd` | Inteiro | pacotes | Pacotes enviados e recebidos na rajada ICMP. |
| `jitter_ms` | Float | ms | Oscilação bruta da rajada (desvio-padrão amostral). |
| `periodo` | Texto | `A` ou `B` | Separa o bloco de Baseline congelado (`A`) do bloco de avaliação (`B`). |
| `mediana`, `MAD` | Float | ms | Estatísticas robustas do fluxo calculadas exclusivamente no Período A. |
| `jitter_tipico`, `perda_tipica` | Float | ms / % | Comportamento basal de oscilação e perda do fluxo no Período A. |
| `prop_resposta` | Float | proporção | Taxa histórica de resposta válida do fluxo no Período A. |

---

## 2. Colunas Oficiais de Entrada do Modelo (8 Features Relativas)
*(Únicas variáveis autorizadas no treinamento e inferência da Árvore Final — invariantes à distância física).*

| Feature | Tipo | Unidade / Escala | Fórmula / Definição Operacional |
|---|---|---|---|
| `z_robusto` | Float | desvios MAD | `(avg - mediana) / (1.4826 * MAD)` — Desvio relativo robusto da latência. |
| `aumento_pct` | Float | % | `((avg - mediana) / mediana) * 100` — Aumento percentual frente à mediana do fluxo. |
| `jitter_relativo` | Float | razão | `jitter_ms / max(jitter_tipico, 0.01)` — Oscilação normalizada pelo padrão da rota. |
| `perda_pct` | Float | % | `((sent - rcvd) / sent) * 100` — Fração de perda de pacotes na rajada atual. |
| `timeout_atual` | Inteiro | binário (0/1) | `1` se `rcvd == 0` ou `perda_pct == 100%`; `0` caso contrário. |
| `n5_timeout` | Inteiro | contagem (0 a 5) | Quantidade de medições com `timeout_atual == 1` na janela móvel das últimas 5 coletas do fluxo. |
| `n5_aumento80` | Inteiro | contagem (0 a 5) | Quantidade de medições com `aumento_pct > 80%` na janela móvel das últimas 5 coletas do fluxo. |
| `n5_risco` | Inteiro | contagem (0 a 5) | Quantidade de medições com condição pontual de anomalia na janela móvel das últimas 5 coletas. |

---

## 3. Variáveis de Controle e Alvo Supervisionado

| Coluna | Tipo | Valores | Descrição |
|---|---|---|---|
| `classe` | Categórica | `OK`, `RISCO`, `FALHA` | Variável-alvo (*target*) determinada pela política de rotulagem da Tarefa 2. |
| `split` | Texto | `treino`, `validacao`, `teste` | Partição temporal estrita dentro do Período B (50% / 20% / 30%). |
