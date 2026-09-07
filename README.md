# 🌐 Projeto de Monitoramento de Redes

Projeto desenvolvido para analisar e comparar duas fontes de dados para monitoramento de redes:

* 📊 **Dataset Real — Network Anomaly Dataset**
* 🌍 **API RIPE Atlas**

## 🎯 Objetivo

Avaliar as vantagens, limitações e possibilidades de utilização de um dataset real e da API RIPE Atlas para a coleta e análise de dados de redes.

## 📊 Dataset Real

**Network Anomaly Dataset — Alberto del Rio**

* Formato: CSV
* 1.001 registros
* 21 colunas
* Contém **latência, perda de pacotes e jitter**
* Possui indicadores de anomalias
* Licença: Apache 2.0
* Dados coletados em ambiente controlado com roteadores virtuais Cisco IOS-XRv

🔗 [Dataset no Kaggle](https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset)

> ⚠️ O dataset utiliza classificação binária de anomalias, enquanto o projeto prevê os estados **OK, RISCO e FALHA**.

## 🌍 API RIPE Atlas

O **RIPE Atlas** permite realizar medições reais de rede utilizando probes distribuídos geograficamente.

Possibilita:

* 📡 Criar novas medições
* 🌎 Coletar dados de diferentes regiões
* 🔄 Realizar medições recorrentes
* 📈 Obter dados atualizados
* ⚙️ Configurar diferentes parâmetros de coleta

🔗 [Documentação da API RIPE Atlas](https://atlas.ripe.net/docs/apis/rest-api-manual/introduction/)

## ⚖️ Comparação

| Critério             | Dataset Real | RIPE Atlas    |
| -------------------- | ------------ | ------------- |
| Controle da coleta   | Baixo        | Alto          |
| Cobertura geográfica | Baixa        | Alta          |
| Complexidade         | Baixa        | Média/Alta    |
| Dados disponíveis    | Imediatos    | Após medições |

### ✅ Recomendação

Para as próximas etapas, a **API RIPE Atlas** foi escolhida como a alternativa mais adequada por permitir **medições atuais, configuráveis e distribuídas geograficamente**.

---

## 👥 Integrantes e contribuições

| Integrante                     | Contribuição                                           |
| ------------------------------ | ------------------------------------------------------ |
| **Enzo Moraes Sousa**          | Seção 4 e organização/junção das etapas                |
| **Beatriz Gonçalves da Silva** | Seção 7 e repositório/commit do GitHub                 |
| **Breno Brasil de Souza**      | Pesquisa e desenvolvimento da Seção 2 — Dataset Real   |
| **Natsumi Goto**               | Seções 1, 5 e 6                                        |
| **Pedro Viana da Silva**       | Pesquisa e desenvolvimento da Seção 3 — API RIPE Atlas |

---

## 📚 Fontes

* [Network Anomaly Dataset — Kaggle](https://www.kaggle.com/datasets/kaiser14/network-anomaly-dataset)
* [RIPE Atlas — Documentação](https://atlas.ripe.net/docs/apis/rest-api-manual/introduction/)
* [RIPE Atlas — Creating Measurements](https://atlas.ripe.net/docs/apis/rest-api-manual/measurements/creating-measurements/)
* [RIPE Atlas — Authentication](https://atlas.ripe.net/docs/apis/rest-api-manual/authentication/)
