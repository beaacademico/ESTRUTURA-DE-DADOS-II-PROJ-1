import os
from PIL import Image, ImageDraw, ImageFont

print("=" * 60)
print(" GERADOR DO KIT DE INSCRIÇÃO NA MOSTRA DE TECNOLOGIA (02/11)")
print("=" * 60)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

OUTPUT_LOGO = os.path.join(DOCS_DIR, "logo_nomedoprojeto.png")

# Dimensões exatas exigidas pelo edital: 500 x 500 px
W, H = 500, 500
img = Image.new("RGBA", (W, H), (7, 13, 24, 255))
draw = ImageDraw.Draw(img)

# 1. Fundo com gradiente sutil simulado e linhas de rede cibernética
for y in range(H):
    r = int(7 + (y / H) * 8)
    g = int(13 + (y / H) * 15)
    b = int(24 + (y / H) * 26)
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# Grade de nós de rede (grid de pontos tecnológicos)
for x in range(30, W - 20, 44):
    for y in range(30, H - 20, 44):
        draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(97, 228, 239, 35))

# Conexões de rede (linhas em ciano/azul neon)
network_lines = [
    ((150, 200), (250, 130)),
    ((250, 130), (350, 200)),
    ((250, 130), (250, 260)),
    ((150, 200), (250, 260)),
    ((350, 200), (250, 260)),
    ((150, 200), (180, 290)),
    ((350, 200), (320, 290)),
    ((250, 260), (250, 320)),
    ((180, 290), (250, 320)),
    ((320, 290), (250, 320)),
]

for p1, p2 in network_lines:
    draw.line([p1, p2], fill=(0, 242, 254, 90), width=3)

# Nós de destaque
nodes = [
    ((250, 130), 16, (0, 242, 254, 255)),   # Top (Origem)
    ((150, 200), 12, (79, 172, 254, 255)),  # Esquerda
    ((350, 200), 12, (79, 172, 254, 255)),  # Direita
    ((250, 260), 14, (16, 185, 129, 255)),  # Centro (OK/Verde)
    ((180, 290), 10, (245, 158, 11, 255)),  # Risco (Amarelo)
    ((320, 290), 10, (239, 68, 68, 255)),   # Falha (Vermelho)
    ((250, 320), 12, (0, 242, 254, 255)),   # Destino
]

for (x, y), radius, color in nodes:
    # Halo externo
    draw.ellipse([x - radius - 6, y - radius - 6, x + radius + 6, y + radius + 6], fill=(color[0], color[1], color[2], 40))
    # Núcleo do nó
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color)

# 2. Tipografia e Textos
try:
    font_title = ImageFont.truetype("arialbd.ttf", 30)
    font_sub = ImageFont.truetype("arial.ttf", 16)
    font_badge = ImageFont.truetype("arialbd.ttf", 14)
except Exception:
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_badge = ImageFont.load_default()

# Badge superior "IA & REDES"
draw.rounded_rectangle([190, 48, 310, 78], radius=8, fill=(0, 242, 254, 30), outline=(0, 242, 254, 180), width=1)
draw.text((208, 54), "IA & REDES", fill=(0, 242, 254, 255), font=font_badge)

# Título Principal
title_text = "PREDITOR DE REDES"
bbox = draw.textbbox((0, 0), title_text, font=font_title)
t_w = bbox[2] - bbox[0]
draw.text(((W - t_w) / 2, 372), title_text, fill=(240, 246, 252, 255), font=font_title)

# Subtítulo com Status OK · RISCO · FALHA
sub_text = "OK  ·  RISCO  ·  FALHA"
bbox_sub = draw.textbbox((0, 0), sub_text, font=font_sub)
s_w = bbox_sub[2] - bbox_sub[0]
draw.text(((W - s_w) / 2, 418), sub_text, fill=(139, 155, 180, 255), font=font_sub)

# Barra de status colorida inferior
draw.rounded_rectangle([150, 452, 230, 456], radius=2, fill=(16, 185, 129, 255))
draw.rounded_rectangle([235, 452, 265, 456], radius=2, fill=(245, 158, 11, 255))
draw.rounded_rectangle([270, 452, 350, 456], radius=2, fill=(239, 68, 68, 255))

# Salva a imagem
img.save(OUTPUT_LOGO, format="PNG")
print(f"\n[OK] Logotipo gerado com sucesso em: {OUTPUT_LOGO}")
print(f"     Dimensões: {img.size[0]} x {img.size[1]} pixels (PNG RGB/RGBA)\n")

# Textos formatados rigorosamente dentro das regras do edital
nome_projeto = "Preditor de Falhas em Redes"
descritivo = "Monitor de redes com IA que prevê anomalias e degradação em caminhos de rede usando RTT relativo, jitter e perda sobre o RIPE Atlas."
tags = "Machine Learning, Redes de Computadores, Árvore de Decisão, RIPE Atlas, MLOps, Python, ICMP"

print("=" * 60)
print(" TEXTOS OFICIAIS PARA O FORMULÁRIO DO BLACKBOARD (HOJE - 02/11)")
print("=" * 60)
print(f"1. ARQUIVO DO LOGO:\n   -> docs/logo_nomedoprojeto.png (500x500 px)\n")
print(f"2. NOME DO PROJETO ({len(nome_projeto)}/30 caracteres):\n   {nome_projeto}\n")
print(f"3. DESCRITIVO DO PROJETO ({len(descritivo)}/200 caracteres):\n   {descritivo}\n")
print(f"4. TAGS DO PROJETO:\n   {tags}\n")
print("=" * 60)
