# Dicionário de Dados v0.1 (Coleta Bruta)

Este dicionário descreve as variáveis presentes no arquivo `tabela_bruta_completa.csv` gerado na Tarefa 1, antes de qualquer cálculo de baseline ou rotulagem.

| Coluna | Tipo | Unidade | Descrição |
|---|---|---|---|
| `timestamp` | Inteiro | Epoch (UTC) | Instante de tempo em que a medição foi realizada. |
| `measurement_id` | Inteiro | - | ID da campanha de medição no RIPE Atlas. |
| `probe_id` | Inteiro | - | ID da sonda de origem (quem dispara o ping). |
| `dst_addr` | Texto | IPv4 | Endereço IP do Anchor alvo (destino). |
| `fluxo_id` | Texto | - | Chave composta (`probe_id\|dst_addr`) que identifica a rota única. |
| `avg` | Float | ms | RTT médio da rajada. Fica em branco (nulo) em caso de timeout. Nunca zero. |
| `min` | Float | ms | RTT mínimo da rajada. |
| `max` | Float | ms | RTT máximo da rajada. |
| `sent` | Inteiro | pacotes | Quantidade de pacotes enviados na rajada (geralmente 3). |
| `rcvd` | Inteiro | pacotes | Quantidade de pacotes respondidos. |
| `perda_pct` | Float | % | Porcentagem de pacotes perdidos na rajada `((sent-rcvd)/sent)*100`. |
| `jitter_ms` | Float | ms | Desvio-padrão amostral dos RTTs de resposta (requer 2+ respostas). |
| `timeout_atual`| Inteiro | booleano (0/1) | Flag que marca `1` se não houve resposta ou se a perda foi de 100%. |
| `periodo` | Texto | A ou B | Indica se a medição pertence ao bloco de Baseline (A) ou Teste/Rotulagem (B). |
