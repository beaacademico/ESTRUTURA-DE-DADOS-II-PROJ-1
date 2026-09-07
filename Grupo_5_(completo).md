# Memorando de Decisão — Fonte de Dados do Projeto


| Campo | Informação |
|-------|------------|
| Curso / Disciplina | `[Ciencias da Computação]` |
| Projeto integrador | `[API RIPE e database real]` |
| Orientador(a) | `[Andrea Ono Sakai]` |
| Data de entrega desta etapa | `[08/09]` |
| Integrantes do grupo | `[Enzo, Beatriz, Natsumi,  Breno e Pedro]` |

---

## 1. Situação


É preciso a analisar e documentar as diferenças entre a utilização de um dataset real já coletado e a API do RIPE Atlas como fontes de dados para o projeto de monitoramento de rede. A comparação considera aspectos como controle sobre a coleta, diversidade geográfica, custo e complexidade de implementação, disponibilidade dos dados, além das vantagens, limitações e riscos de cada abordagem.
Temos como objetivo compreender as características de cada alternativa e como elas afetam a obtenção dos dados utilizados pelo projeto.

## 2. Opção A — Dataset real

- **Origem / link:** [Network Anomaly Dataset (Alberto del Rio) — arquivo network_dataset_labeled.csv](https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset?select=network_dataset_labeled.csv)

- **Formato:** [ CSV, 98.3 kB, 21 colunas ]

- **Período coberto:** [ medições contínuas em 11/05/2024, coletadas a cada ~28 segundos (1001 registros) ]

- **Campos disponíveis:** [ timestamp, bandwidth, throughput, congestion, packet_loss, latency, jitter, Routers, Planned route, Network measure, Network target, Video target, Percentage video occupancy, Bitrate video, Number videos, além de flags binárias de rótulo (anomaly_throughput, anomaly_congestion, anomaly_packet_loss, anomaly_latency, anomaly_jitter, anomaly) ]

- **Licença de uso:** [ Apache 2.0 ]

**Resumo do que foi encontrado:**

Pesquisamos em 8 fontes diferentes (Kaggle, Zenodo, IEEE DataPort, Mendeley Data, CAIDA, UCI Machine Learning Repository, GitHub e figshare), avaliando um total de 16 datasets candidatos contra o contrato de dados do projeto (timestamp, ip, latencia_ms, perda_pacotes_pct, jitter_ms, status_real).

O dataset network_dataset_labeled.csv, do Kaggle (autor Alberto del Rio), foi o único que reuniu simultaneamente os três campos numéricos centrais do contrato — latência, perda de pacotes e jitter — em colunas nomeadas e prontas para uso, junto com algum rótulo de status. Os demais candidatos avaliados sempre falharam em pelo menos um desses pontos:

LAN Network Stability (Gary Stafford, Kaggle, CC0) — tem latência real de ping ICMP a cada 10s, mas não tem perda de pacotes nem jitter como colunas diretas.
Cloud Interdatacenter Network Performance Dataset (Persico et al., Mendeley Data, CC BY 4.0, publicado em Computer Networks 2017) — tem os 4 campos de métrica (throughput, latência, jitter, perda), mas está em formato JSON (exigiria conversão) e não possui IP nem rótulo de status.
Network Traffic Dataset via Wireshark (Kaggle, MIT) — tem IP de origem real, latência e jitter, e um rótulo binário de anomalia, mas não tem % de perda de pacotes explícita (só um indicador de retransmissão).
Datasets como 5G Network data e Network Traffic Anomaly Detection Dataset foram descartados por serem sintéticos ("simulates" na própria descrição) ou não medirem os campos de rede necessários.
CAIDA, UCI e figshare não retornaram datasets prontos com os campos exigidos — CAIDA exige acesso restrito a capturas .pcap brutas de backbone, sem latência/jitter/perda como colunas.

Limitação central identificada: o rótulo de status do dataset é binário (0/1 por métrica, mais um flag geral `anomaly`), não as 3 classes exigidas pelo contrato de dados (OK/RISCO/FALHA).

Ambiente de coleta: a coluna `Routers` traz valores como `up xrv6` e `up xrv1,2,3` — nomes de roteadores virtuais Cisco IOS-XRv. Isso indica que os dados foram medidos em um testbed/laboratório com equipamento virtualizado, não em uma rede de produção real com tráfego de usuários. Ou seja, são medições reais (não geradas por fórmula/sintéticas), mas coletadas em ambiente controlado — diferente da rede de produção real que o grupo vai monitorar no projeto.


## 3. Opção B — API do RIPE Atlas

- **Documentação consultada (link):** [
https://atlas.ripe.net/docs/apis/rest-api-manual/introduction/
https://atlas.ripe.net/docs/apis/rest-api-reference/
https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/
https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/
]

- **Autenticação exigida:** [ API Key e autenticação baseada em sessão. Grande parte das consultas públicas pode ser realizada anonimamente. A API Key é necessária para operações que exigem permissões específicas, como criar medições, interromper medições, acessar determinados dados privados e gerenciar probes. ]

- **Como se cria uma medição:** [ Uma medição pode ser criada através de uma requisição POST para `/api/v2/measurements/`. O pedido deve conter a definição da medição, informando o tipo de teste, o destino e a versão do protocolo IP utilizada. Também deve ser definida a seleção dos probes que realizarão a medição. É possível configurar horário de início e término, intervalo entre medições e se o teste será único ou recorrente. Para criar uma medição é necessária uma API Key com permissão de criação. ]

- **Como se consultam os resultados:** [ Os resultados podem ser consultados através de um `GET /api/v2/measurements/{msm}/results/`, em que   `{msm}` corresponde ao identificador da medição. A API permite filtros como ID dos probes e período de tempo. Também existe o endpoint `/latest/`, que permite obter os resultados mais recentes de uma medição. ]

**Resumo do que foi encontrado:**

A API do RIPE Atlas é uma interface que permite que programas e aplicações tenham acesso aos dados e recursos da plataforma RIPE Atlas.
A plataforma utiliza uma rede distribuída de probes e anchors para realizar medições da Internet a partir de diferentes pontos do mundo. Essas medições podem analisar diferentes aspectos da conectividade, como ping, traceroute, DNS, TLS/SSL, NTP e HTTP.
A API utiliza como endereço-base `https://atlas.ripe.net/api/v2/` e permite requisições HTTP, como GET para consultar informações e POST para criar medições. Os dados podem ser retornados em formatos como JSON, adequado para processamento automático por programas.

Na criação de uma medição, o usuário define o tipo de teste, o alvo, a família de endereços (IPv4 ou IPv6) e os probes que irão realizar o teste. Por exemplo, uma medição do tipo ping pode verificar o tempo de resposta entre vários probes e um determinado servidor.
Depois da execução, os resultados podem ser obtidos pela API utilizando o ID da medição. Os resultados são disponibilizados em JSON e podem conter informações específicas de cada tipo de teste, como dados de latência e tempo de ida e volta round-trip time em medições de ping.
Outro recurso importante é a Streaming API, que permite receber resultados de medições à medida que eles são produzidos, sendo útil para aplicações que precisam acompanhar medições praticamente em tempo real.

Em resumo, a API do RIPE Atlas é uma ferramenta importante para automação de medições e coleta de dados de redes. Ela permite que pesquisadores e desenvolvedores criem testes, selecionem diferentes pontos de medição, coletem resultados e posteriormente processem esses dados em ferramentas como Python e outras linguagens de programação.

## 4. Comparação

|          Critério            | Opção A — Dataset real | Opção B — API RIPE Atlas |
|------------------------------|------------------------|--------------------------|
| Controle sobre a coleta      > Limitado               | Alto                     |
| Diversidade geográfica       > Baixa                  | Alta                     |
| Custo / complexidade         > Baixo                  | Médio/Alto               |
| Tempo até os primeiros dados > Imediato               | Depende da medição       |

justificativas das minhas escolhas:

- Controle sobre a coleta > o dataset já está pronto, enquanto o outro permite configurar novas medições

- Diversidade geográfica > o dataset foi coletado em um ambiente controlado, enquanto o RIPE Atlas utiliza probes distribuídos mundialmente

- Custo / complexidade > utilizar um CSV pronto é mais simples. A API exige configuração e conhecimento de requisições

- Tempo até os primeiros dados > o dataset já possui dados disponíveis. No RIPE Atlas, é necessário realizar uma medição antes de obter os resultados

## 5. Recomendação

Para a continuidade do projeto, recomenda-se a utilização da API do RIPE Atlas como fonte de dados para as próximas etapas.
A recomendação considera as características levantadas durante a pesquisa, principalmente a possibilidade de realizar novas medições, configurar diferentes parâmetros de coleta e utilizar probes distribuídos geograficamente. Isso não significa que a utilização de datasets reais seja inadequada, mas que as duas alternativas atendem a necessidades diferentes dentro de um projeto de monitoramento de redes.

## 6. Justificativa

Os resultados da pesquisa mostram que as duas alternativas apresentam vantagens e limitações próprias.
O dataset analisado apresenta como principal vantagem a disponibilidade imediata dos dados, permitindo iniciar a análise sem a necessidade de configurar ou aguardar uma nova coleta. Por outro lado, sua utilização fica restrita às condições em que os dados foram originalmente obtidos, incluindo período, ambiente, métricas e características da coleta.
A API do RIPE Atlas, por outro lado, permite realizar novas medições e definir parâmetros como o tipo de teste, o destino, a família de endereços IP e os probes utilizados. A infraestrutura distribuída do RIPE Atlas possibilita obter medições a partir de diferentes pontos geográficos e permite realizar coletas recorrentes e atualizadas.
Como desvantagens, a utilização da API exige maior esforço de implementação e tratamento dos resultados, além de depender da disponibilidade do serviço, da configuração das medições e das limitações impostas pela própria plataforma.
Assim, para as próximas etapas deste projeto, a API do RIPE Atlas se mostra mais adequada por permitir uma coleta atual e configurável.

## 7. Riscos e limitações

| Aspecto          | Dataset Real                                      | API RIPE Atlas                                      |
|------------------|---------------------------------------------------|-----------------------------------------------------|
| Prós             | Dados já coletados e prontos para análise;        | Dados reais e atualizados; permite obter medições   |
|                  | permite trabalhar com grandes volumes; resultados | de rede diretamente; grande cobertura geográfica;   |
|                  | reproduzíveis; não depende da API estar           | possibilita análises em diferentes momentos.        |
|                  | disponível.                                       |                                                     |
|------------------|---------------------------------------------------|-----------------------------------------------------|
| Contras          | Pode estar desatualizado; pode conter dados       | Depende da disponibilidade da API; exige            |
|                  | incompletos ou inconsistentes; nem sempre é       | conhecimento técnico; pode haver limites de         |
|                  | possível conhecer todos os detalhes da coleta.    | requisições; o tratamento dos dados pode ser        |
|                  |                                                   | mais trabalhoso.                                    |
|------------------|---------------------------------------------------|-----------------------------------------------------|
| Riscos           | Os dados podem não representar a situação atual   | Instabilidade ou indisponibilidade da API;          |
|                  | da rede; podem existir vieses na coleta; erros ou | mudanças no serviço podem afetar o projeto;         |
|                  | valores ausentes podem afetar os resultados.      | resultados podem variar conforme o momento da       |
|                  |                                                   | coleta.                                             |
|------------------|---------------------------------------------------|-----------------------------------------------------|
| Limitações       | Fica limitado ao período, locais e métricas       | Limitada às medições e informações disponibilizadas |
|                  | presentes no dataset; não permite realizar novas  | pelo RIPE Atlas; depende das sondas e medições      |
|                  | coletas.                                          | disponíveis.                                        |
|------------------|---------------------------------------------------|-----------------------------------------------------|
| Custo / esforço  | Menor esforço inicial, pois os dados já estão     | Maior esforço de implementação e tratamento, mas    |
|                  | disponíveis.                                      | permite automatizar a coleta.                       |

**Conclusão:**

O Dataset Real é mais adequado quando o objetivo é utilizar uma base estável e reproduzível para análise. Já a API RIPE Atlas é mais interessante quando o objetivo é obter medições de rede reais e atualizadas, oferecendo maior flexibilidade e cobertura. As duas abordagens também podem ser utilizadas de forma complementar.


## 8. Contribuição Individual dos Integrantes

### Integrante 1 — `[Enzo Moraes Sousa]`
- **O que fez nesta etapa:** `[seção numero 4 e junção das etapas restantes]`
- **Tempo dedicado (aprox.):** `[01:15]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[tranformei as tabelas para ficarem mais entendiveis, incluindo o da sessão 4]` 

### Integrante 2 — `[ Beatriz Gonçalves da Silva ]`
- **O que fez nesta etapa:** `[seção 7 e repositorio/commit do github]`
- **Tempo dedicado (aprox.):** `[01:40]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*:
`[Documento no Word]`

### Integrante 3 — `[ Breno Brasil de Souza ]`
- **O que fez nesta etapa:** `[seção 2]`
- **Tempo dedicado (aprox.):** `[02:00]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[links de pesquisa na seção 2 e network dataset completo]` 

### Integrante 4 — `[ Natsumi Goto ]`
- **O que fez nesta etapa:** `[seção 1, 5 e 6]`
- **Tempo dedicado (aprox.):** `[01:15]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[links de pesquisa abaixo]`

### Integrante 5 — `[ Pedro Viana da Silva ]`
- **O que fez nesta etapa:** `[seção 3]`
- **Tempo dedicado (aprox.):** `[1:00]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[links de pesquisa na seção 3]` 

### Integrante 6 — `[Vago]`
- **O que fez nesta etapa:** `[X]`
- **Tempo dedicado (aprox.):** `[X]`
- **Evidência da contribuição** *(print de conversa, rascunho, e-mail, documento compartilhado etc.)*: 
`[X]` 
`[X]`

---

## Fontes consultadas

1. DEL RIO, Alberto; SCHUMMER, Pilar. Network anomaly dataset. Kaggle, 2024. Disponível em: https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset. 

2. RIPE NCC. RIPE Atlas REST API: introduction. [S. l.]: RIPE NCC, [s. d.]. Disponível em: https://atlas.ripe.net/docs/apis/rest-api-manual/introduction/. 

3. RIPE NCC. Creating measurements. RIPE Atlas Documentation. [S. l.]: RIPE NCC, [s. d.]. Disponível em: https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/. 

4. RIPE NCC. Authentication. RIPE Atlas Documentation. [S. l.]: RIPE NCC, [s. d.]. Disponível em: https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/. 

5. RIPE NCC. Creating and managing API keys. RIPE Atlas Documentation. [S. l.]: RIPE NCC, [s. d.]. Disponível em: https://atlas.ripe.net/docs/howtos/keys. 
