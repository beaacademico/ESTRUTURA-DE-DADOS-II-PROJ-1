2. Opção A — Dataset real
Origem / link: [Network Anomaly Dataset (Alberto del Rio) — arquivo network_dataset_labeled.csv](https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset?select=network_dataset_labeled.csv)
Formato: CSV, 98.3 kB, 21 colunas
Período coberto: medições contínuas em 11/05/2024, coletadas a cada ~28 segundos (1001 registros)
Campos disponíveis: timestamp, bandwidth, throughput, congestion, packet_loss, latency, jitter, Routers, Planned route, Network measure, Network target, Video target, Percentage video occupancy, Bitrate video, Number videos, além de flags binárias de rótulo (anomaly_throughput, anomaly_congestion, anomaly_packet_loss, anomaly_latency, anomaly_jitter, anomaly)
Licença de uso: Apache 2.0

Resumo do que foi encontrado:

Pesquisamos em 8 fontes diferentes (Kaggle, Zenodo, IEEE DataPort, Mendeley Data, CAIDA, UCI Machine Learning Repository, GitHub e figshare), avaliando um total de 16 datasets candidatos contra o contrato de dados do projeto (timestamp, ip, latencia_ms, perda_pacotes_pct, jitter_ms, status_real).

O dataset network_dataset_labeled.csv, do Kaggle (autor Alberto del Rio), foi o único que reuniu simultaneamente os três campos numéricos centrais do contrato — latência, perda de pacotes e jitter — em colunas nomeadas e prontas para uso, junto com algum rótulo de status. Os demais candidatos avaliados sempre falharam em pelo menos um desses pontos:

LAN Network Stability (Gary Stafford, Kaggle, CC0) — tem latência real de ping ICMP a cada 10s, mas não tem perda de pacotes nem jitter como colunas diretas.
Cloud Interdatacenter Network Performance Dataset (Persico et al., Mendeley Data, CC BY 4.0, publicado em Computer Networks 2017) — tem os 4 campos de métrica (throughput, latência, jitter, perda), mas está em formato JSON (exigiria conversão) e não possui IP nem rótulo de status.
Network Traffic Dataset via Wireshark (Kaggle, MIT) — tem IP de origem real, latência e jitter, e um rótulo binário de anomalia, mas não tem % de perda de pacotes explícita (só um indicador de retransmissão).
Datasets como 5G Network data e Network Traffic Anomaly Detection Dataset foram descartados por serem sintéticos ("simulates" na própria descrição) ou não medirem os campos de rede necessários.
CAIDA, UCI e figshare não retornaram datasets prontos com os campos exigidos — CAIDA exige acesso restrito a capturas .pcap brutas de backbone, sem latência/jitter/perda como colunas.

Limitação central identificada: o rótulo de status do dataset é binário (0/1 por métrica, mais um flag geral `anomaly`), não as 3 classes exigidas pelo contrato de dados (OK/RISCO/FALHA).

Ambiente de coleta: a coluna `Routers` traz valores como `up xrv6` e `up xrv1,2,3` — nomes de roteadores virtuais Cisco IOS-XRv. Isso indica que os dados foram medidos em um testbed/laboratório com equipamento virtualizado, não em uma rede de produção real com tráfego de usuários. Ou seja, são medições reais (não geradas por fórmula/sintéticas), mas coletadas em ambiente controlado — diferente da rede de produção real que o grupo vai monitorar no projeto.

