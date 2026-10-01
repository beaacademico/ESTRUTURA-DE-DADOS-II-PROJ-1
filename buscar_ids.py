import requests

print("Buscando medições Anchoring Mesh ativas...\n")

# Endpoint específico para medições de Anchors
url = "https://atlas.ripe.net/api/v2/anchor-measurements/?limit=100"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()['results']
    # Filtramos medições ativas de ping (o RIPE usa IPv4 como padrão para ping no Mesh)
    ping_active = [m for m in data if m.get('type') == 'ping' and m.get('is_active') == True]
    
    print(f"Foram encontradas {len(ping_active)} medições de Ping em Anchors nesta página.")
    print("Aqui estão algumas IDs válidas para você testar no Notebook 1:\\n")
    
    for m in ping_active[:10]:
        # O campo measurement vem como URL, ex: https://atlas.ripe.net/api/v2/measurements/215593100/
        msm_url = m['measurement']
        msm_id = msm_url.strip('/').split('/')[-1]
        print(f"- Measurement ID: {msm_id} | Tipo: {m['type']} | Mesh: {m['is_mesh']}")
else:
    print("Erro ao consultar a API da RIPE.")
