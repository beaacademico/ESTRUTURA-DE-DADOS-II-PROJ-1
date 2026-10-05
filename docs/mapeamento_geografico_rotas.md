# Mapeamento Geográfico da Coleta (Anchoring Mesh)

Este documento mapeia a localização física das Sondas (Origens) e das Medições (Destinos) utilizadas na Fase 2 do projeto para geração dos 69 fluxos (pares) do dataset rotulado.

## 🎯 Destinos (Measurement IDs)
Os destinos são os servidores "Âncoras" do RIPE Atlas. Nós selecionamos 8 medições ativas distribuídas no norte europeu.

| Measurement ID | País de Destino | Servidor Alvo (Anchor) |
| :--- | :--- | :--- |
| **7714918** | 🇫🇮 Finlândia (FI) | `fi-tmp-as719.anchors.atlas.ripe.net` |
| **7714921** | 🇫🇮 Finlândia (FI) | `fi-tmp-as719.anchors.atlas.ripe.net` |
| **9181148** | 🇫🇮 Finlândia (FI) | `fi-tmp-as719.anchors.atlas.ripe.net` |
| **9181151** | 🇫🇮 Finlândia (FI) | `fi-tmp-as719.anchors.atlas.ripe.net` |
| **8937123** | 🇳🇴 Noruega (NO) | `no-osl-as39029.anchors.atlas.ripe.net` |
| **8937126** | 🇳🇴 Noruega (NO) | `no-osl-as39029.anchors.atlas.ripe.net` |
| **9333345** | 🇳🇱 Holanda (NL) | `nl-ams-as3333-3.anchors.atlas.ripe.net` |
| **9333348** | 🇳🇱 Holanda (NL) | `nl-ams-as3333-3.anchors.atlas.ripe.net` |

---

## 📡 Origens (Probes)
Para garantir a diversidade geográfica exigida no projeto (caminhos curtos e longos), selecionamos 12 sondas (Probes) espalhadas por diferentes continentes.

| Probe ID | País de Origem | Continente |
| :--- | :--- | :--- |
| **6349** | 🇧🇷 Brasil (BR) | América do Sul |
| **6379** | 🇺🇸 Estados Unidos (US) | América do Norte |
| **6393** | 🇹🇹 Trinidad e Tobago (TT) | América Central / Caribe |
| **6380** | 🇬🇭 Gana (GH) | África |
| **6251** | 🇫🇮 Finlândia (FI) | Europa |
| **6313** | 🇩🇪 Alemanha (DE) | Europa |
| **6346** | 🇩🇪 Alemanha (DE) | Europa |
| **6316** | 🇮🇹 Itália (IT) | Europa |
| **6424** | 🇮🇹 Itália (IT) | Europa |
| **6342** | 🇳🇱 Holanda (NL) | Europa |
| **6451** | 🇬🇧 Reino Unido (GB) | Europa |
| **6490** | 🇨🇭 Suíça (CH) | Europa |

---

## 🌍 Matriz de Tráfego (De Onde para Onde?)

O cruzamento das origens com os destinos gerou **69 pares (fluxos)** válidos, cobrindo os três cenários vitais para validar que a Inteligência Artificial julga pelo "desvio padrão" relativo e não pelo ping absoluto:

1. **Caminhos Curtos (Intra-país):**
   * *Exemplo:* Sonda `6251` (FI) ➔ Medição `7714918` (FI). Tráfego doméstico, RTT natural baixíssimo (geralmente < 10ms).
   * *Exemplo:* Sonda `6342` (NL) ➔ Medição `9333345` (NL).
2. **Caminhos Regionais (Intra-continente):**
   * *Exemplo:* Sonda `6316` (IT) ➔ Medição `8937123` (NO). Cruzando a Europa de sul a norte. RTT médio.
   * *Exemplo:* Sonda `6451` (GB) ➔ Medição `9181148` (FI).
3. **Caminhos Longos (Intercontinentais):**
   * *Exemplo:* Sonda `6349` (BR) ➔ Medição `8937123` (NO). Cruzando o oceano Atlântico a partir do Brasil. RTT natural altíssimo (frequentemente > 200ms).
   * *Exemplo:* Sonda `6380` (GH) ➔ Medição `9333345` (NL). Rota África-Europa.
   * *Exemplo:* Sonda `6379` (US) ➔ Medição `7714918` (FI). Rota América do Norte-Europa.
