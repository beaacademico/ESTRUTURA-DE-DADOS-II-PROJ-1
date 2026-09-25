# Diário da Tarefa 1 — Problema e coleta bruta (sem rótulo)

**Período:** 17/08/2026 a 17/09/2026  
**Projeto:** Preditor de degradação de rede com RTT normalizado (independente da rota)  
**Modelo desta disciplina:** árvore de decisão. Nesta tarefa não se treina árvore.

**Equipe: Grupo 5**  
**Integrantes:Beatriz, Breno, Enzo, Natsumi, Pedro, Vitória**  
**Scrum Master da tarefa: Breno**  
**Repositório GitHub:https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1**

> Esta tarefa entrega o problema e o **dado cru**. Não há classe OK, RISCO ou FALHA. Não há baseline, não há mediana e não há árvore. Quem rotular aqui mistura a coleta com a decisão da Tarefa 2.
>
> A rota entra na coleta só para haver caminhos curtos e longos no mesmo arquivo. RTT alto **não** é falha. País, IP e nome da rota **não** serão coluna da árvore.

### Contrato desta tarefa

| | Artefato | Quem usa depois |
|---|---|---|
| **Entra** | RFC do projeto | — |
| **Sai** | RFC preenchido pelo grupo (problema, horizonte, custo de errar FALHA, fora de escopo) | Tarefas 2 e 5 |
| **Sai** | Dicionário v0.1 só com colunas **brutas** da medição | Tarefa 2 |
| **Sai** | `data/raw/` + `config/` + `requirements.txt` | Tarefa 2 **é obrigada a usar este bruto** |
| **Sai** | Este diário | Tarefas seguintes |

**Não sai daqui:** baseline, rótulo, `z_robusto`, split, árvore, métrica de modelo.

---

## 1. Definição do problema

Responder no diário. A resposta tem de bater com o RFC.

| Pergunta | Resposta do grupo |
|---|---|
| Qual evento a árvore vai classificar? | Degradação do fluxo em relação ao **próprio** normal: OK, RISCO ou FALHA. Não é “rota longa” nem “RTT acima de 100 ms”. |
| O que é um fluxo? | `fluxo_id = probe_id \| dst_addr` (origem, destino e, se existir, `measurement_id`). |
| O que é cada linha do bruto? | Uma medição ICMP desse fluxo, com timestamp. Ainda **sem** classe. |
| Qual horizonte fica para depois? | Detector: estado da medição atual. Preditor: estado 12 minutos à frente. A árvore só entra na Tarefa 3. |
| Quem usa o alerta? | Quem opera o enlace: investigar (FALHA), observar (RISCO) ou não agir (OK). |
| O que está proibido como definição de falha? | Limiar global de RTT, país, continente ou nome da rota. |

- [x] RFC do grupo preenchido a partir desta tabela
- [x] Dicionário v0.1 só com variáveis brutas

## 2. O que coletar (e o que não criar)

Fonte: medições públicas já existentes de ping IPv4 (mesh de Anchors do RIPE Atlas, somente `GET`). Não criar medição própria e não gastar crédito.

Cada registro bruto guarda, quando a API trouxer:

| Campo | Unidade | Papel agora |
|---|---|---|
| `timestamp` | UTC | Ordenar o fluxo |
| `measurement_id` | — | Identidade da medição |
| `probe_id` | — | Origem |
| `dst_addr` | — | Destino |
| `fluxo_id` | texto estável | `probe_id\|dst_addr` |
| RTT da rajada (médio; mín/máx se existirem) | ms | Medição. Vazio se não houver resposta. **Nunca 0** |
| enviados, recebidos | contagem | |
| `perda_pct` | % | `(enviados − recebidos) / enviados × 100` |
| `jitter_ms` | ms | Desvio-padrão dos RTT da rajada **somente** com 2 ou mais respostas. Senão, vazio. **Nunca 0 fingindo estabilidade** |
| `timeout_atual` | 0 ou 1 | 1 se não há RTT ou perda = 100% |
| país ou rota | texto | Só auditoria de diversidade. **Fora da futura árvore** |

Regras da coleta:

- [x] Vários fluxos, com pelo menos um caminho curto e um caminho longo no mesmo período
- [x] A diversidade geográfica está documentada e **não** virou classe
- [x] Dois blocos de tempo contíguos, sem amostra nos dois: Período A (só para o baseline da Tarefa 2) e Período B (medições que serão rotuladas). Referência do projeto: 7 dias + 7 dias a partir de 06/09/2026 04:32 UTC. Outro recorte só vale se os dois blocos continuarem sem sobreposição e o A tiver volume para o mínimo da Tarefa 2
- [x] Timeout permanece no arquivo
- [x] JSON bruto preservado; a tabela tratada não apaga o bruto
- [x] Parâmetros (período, probes, destinos) em `config/`, não espalhados no código
- [x] HTTP com timeout, releitura em erro transitório e coleta idempotente (rodar de novo não duplica)
- [x] `requirements.txt` da coleta

**Evidências (notebook, commit, trecho do config):Os parâmetros de tempo e timeout estão isolados no arquivo config/config.yaml. O loop de download fatiado e tratamento idempotente está no notebooks/01_coleta_bruta.ipynb.**

## 3. Relatório de qualidade — ainda sem classe

- [ ] Registros por `fluxo_id`
- [ ] Início e fim de cada fluxo
- [ ] Campos ausentes (RTT vazio é ausência, não zero)
- [ ] Duplicatas
- [ ] Quantidade de timeouts
- [ ] RTT e perda descritos (mínimo, mediana, máximo) **sem** dizer OK, RISCO ou FALHA

**N de registros brutos:30227**  
**N de fluxos:6**  
**Caminho curto e caminho longo presentes (quais):Sim, garantimos a diversidade geográfica. Temos caminhos curtos (ex: Sonda 6251 na Finlândia pingando o destino da medição 7714918, também na Finlândia) e caminhos longos/regionais (ex: Sonda 6316 na Itália pingando o destino 8937123 na Noruega). Isso prova que o dataset engloba baselines fisicamente muito diferentes, o que será vital para o cálculo relativo do Z-Robusto na Tarefa 2**

## 4. Scrum

- [ ] Product Owner = docente; Scrum Master da tarefa; time de desenvolvimento
- [ ] Board com To do / Doing / Done
- [ ] Pelo menos 3 histórias: coletar fluxos diversos; preservar o bruto com timeout; separar Período A e Período B sem rotular

**Histórias:**  
1.  Como Scrum Master, quero estruturar o repositório Git em pastas padronizadas (config, raw, interim) e orquestrar o time para garantir que o projeto não dependa apenas do Google Drive.
2.  Como desenvolvedora, quero implementar as requisições HTTP fatiadas para a API do RIPE Atlas, garantindo o download seguro de 14 dias de dados para os Períodos A e B.
3.  Como engenheiro de dados, quero converter o JSON bruto em DataFrame, criando os fluxos_id e calculando perda_pct e jitter no momento da extração.
4.  Como analista, quero externalizar as configurações de timeout e as datas dos períodos de coleta em um arquivo config.yaml para manter o código isolado.
5.  Como analista de redes, quero investigar e selecionar IDs reais do Anchoring Mesh que garantam a presença de rotas curtas e longas na amostra.
6.  Como analista de qualidade (QA), quero auditar a contagem de registros e timeouts para gerar o relatório de qualidade, garantindo que não haja rotulagem prematura na Tarefa 1.

**Link do board:https://trello.com/invite/b/6ab6af6de8c4ab5ad844fc44/ATTI26425ccc82efa9e355bd029ba936768820A59FB6/projeto-redes-grupo-5**

## 5. Diário de bordo

| Integrante | O que fiz nesta tarefa | Dificuldades | O que pretendo manter/ajustar |
| Breno (Scrum Master)| Montei a estrutura local do projeto (Git) saindo da dependência do Drive, criei as pastas raw e interim e organizei os relatórios.| Entender a melhor forma de separar os dados brutos sem estourar o limite do GitHub.| Manter a execução dos notebooks localmente antes de subir para a nuvem.|
| Beatriz | Configurei o arquivo config.yaml, ajustando as janelas de 14 dias (Períodos A e B) conforme exigido no RFC. | Entender o formato de data UTC Epoch exigido pela API da RIPE. | Manter a separação de parâmetros fora do código. |
| Enzo | Fui responsável por checar as métricas finais geradas pelo código, validar a presença de caminhos curtos/longos e documentar o Scrum. | Preencher os artefatos com a formatação Markdown correta e unir o trabalho do time. | Acompanhar mais de perto os logs de erro da API. |
| Natsumi | Refatorei meu código original de requisição (requests.get) colocando-o num loop para lidar com o volume massivo de 14 dias. | A API da RIPE demorou muito para responder o bloco grande, precisei adaptar para downloads diários. | Manter os tratamentos de erro (raise_for_status) sempre ativos. |
| Pedro | Construí o script processar_resultados gerando o DataFrame final com as colunas de perda_pct e desvio-padrão da rajada (jitter). | Lidar com a divisão por zero quando o pacote dava 100% de perda. | Garantir que RTT vazio não seja mascarado como zero. |
| Vitória | Evoluí os testes das antigas medições (1001 e 2000000) buscando IDs novos no Anchoring Mesh para adequar à restrição do RFC. | Foi difícil achar uma medição que trouxesse probes ativos de rotas intercontinentais. | Continuar documentando as decisões e IDs descartados no histórico. |

## 6. Evidências gerais

- Link do RFC: https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1/blob/main/docs/RFC_Preditor_Degradacao_Rede.md
- Link do dicionário v0.1: https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1/blob/main/docs/dicionario_dados_v0.1.md
- Link dos commits: https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1/commits/main
- Link de `data/raw/` e do `config/`:
    -   RAW: https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1/tree/main/data/raw
    -   CONFIG: https://github.com/beaacademico/ESTRUTURA-DE-DADOS-II-PROJ-1/tree/main/config

---

## Rubrica — Tarefa 1 (0 a 4,0)

| Critério | Peso | Nota máxima | Nota | Observações |
|---|---|---|---|---|
| Problema | 0,5 | Fluxo, unidade de análise e proibição de RTT absoluto como falha estão explícitos | | |
| Coleta bruta | 1,5 | Vários fluxos (curto e longo), timeout preservado, RTT vazio ≠ 0, config externa, bruto intocável | | |
| Período A e Período B sem rótulo | 1,0 | Dois blocos sem sobreposição; relatório de qualidade **sem** classe | | |
| Scrum + diário | 1,0 | Papéis, board, histórias e diário de todos | | |
| **Total** | **4,0** | | **___ / 4,0** | |
