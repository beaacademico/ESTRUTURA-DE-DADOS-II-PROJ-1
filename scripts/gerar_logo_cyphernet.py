import os
import math
from PIL import Image, ImageDraw, ImageFont

print("=" * 60)
print(" GERANDO LOGOTIPO: CypherNet: Vigia de Redes (500x500 px)")
print("=" * 60)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

OUTPUT_LOGO = os.path.join(DOCS_DIR, "logo_nomedoprojeto.png")

# Dimensões exatas: 500 x 500 px
W, H = 500, 500
img = Image.new("RGBA", (W, H), (6, 11, 20, 255))
draw = ImageDraw.Draw(img)

# 1. Fundo com gradiente tecnológico profundo (paleta Cypher: ciano elétrico, azul escuro e toques de âmbar)
for y in range(H):
    r = int(6 + (y / H) * 10)
    g = int(11 + (y / H) * 18)
    b = int(20 + (y / H) * 30)
    draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

# Grade sutil de radar / mira de câmera (estilo Spycam)
center_x, center_y = 250, 190
for radius in [140, 100, 60]:
    draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], 
                 outline=(0, 242, 254, 30), width=1)

# Linhas cruzadas de mira (crosshair de vigilância)
draw.line([(center_x - 150, center_y), (center_x - 70, center_y)], fill=(0, 242, 254, 50), width=1)
draw.line([(center_x + 70, center_y), (center_x + 150, center_y)], fill=(0, 242, 254, 50), width=1)
draw.line([(center_x, center_y - 150), (center_x, center_y - 70)], fill=(0, 242, 254, 50), width=1)
draw.line([(center_x, center_y + 70), (center_x, center_y + 150)], fill=(0, 242, 254, 50), width=1)

# Cantos de interface de câmera HUD (retângulos nos 4 cantos da lente)
hud_corners = [
    # Top-Left
    [(center_x - 85, center_y - 85), (center_x - 65, center_y - 85)],
    [(center_x - 85, center_y - 85), (center_x - 85, center_y - 65)],
    # Top-Right
    [(center_x + 85, center_y - 85), (center_x + 65, center_y - 85)],
    [(center_x + 85, center_y - 85), (center_x + 85, center_y - 65)],
    # Bottom-Left
    [(center_x - 85, center_y + 85), (center_x - 65, center_y + 85)],
    [(center_x - 85, center_y + 85), (center_x - 85, center_y + 65)],
    # Bottom-Right
    [(center_x + 85, center_y + 85), (center_x + 65, center_y + 85)],
    [(center_x + 85, center_y + 85), (center_x + 85, center_y + 65)],
]
for p1, p2 in hud_corners:
    draw.line([p1, p2], fill=(0, 242, 254, 180), width=2)

# Teia de nós de rede / Trapwires conectados
nodes = [
    ((center_x, center_y - 75), 10, (0, 242, 254, 255)),     # Topo
    ((center_x - 70, center_y), 9, (79, 172, 254, 255)),     # Esquerda
    ((center_x + 70, center_y), 9, (79, 172, 254, 255)),     # Direita
    ((center_x - 45, center_y + 65), 10, (16, 185, 129, 255)),# OK (Verde)
    ((center_x + 45, center_y + 65), 10, (239, 68, 68, 255)), # Falha (Vermelho)
]

# Desenha os fios de conexão (trapwires)
for i in range(len(nodes)):
    for j in range(i + 1, len(nodes)):
        draw.line([nodes[i][0], nodes[j][0]], fill=(0, 242, 254, 70), width=2)

# Desenha os nós periféricos
for (nx, ny), r, col in nodes:
    draw.ellipse([nx - r - 4, ny - r - 4, nx + r + 4, ny + r + 4], fill=(col[0], col[1], col[2], 50))
    draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=col)

# O Olho Central do Cypher (A Câmera Espiã - Spycam Eye)
eye_r = 26
# Halo de brilho do olho
draw.ellipse([center_x - eye_r - 12, center_y - eye_r - 12, center_x + eye_r + 12, center_y + eye_r + 12], 
             fill=(0, 242, 254, 35))
draw.ellipse([center_x - eye_r - 6, center_y - eye_r - 6, center_x + eye_r + 6, center_y + eye_r + 6], 
             fill=(0, 242, 254, 70))
# Lente escura externa
draw.ellipse([center_x - eye_r, center_y - eye_r, center_x + eye_r, center_y + eye_r], 
             fill=(9, 22, 38, 255), outline=(0, 242, 254, 255), width=3)
# Íris tecnológica ciano brilhante
draw.ellipse([center_x - 13, center_y - 13, center_x + 13, center_y + 13], 
             fill=(0, 242, 254, 255))
# Pupila da câmera
draw.ellipse([center_x - 6, center_y - 6, center_x + 6, center_y + 6], 
             fill=(4, 9, 16, 255))
# Ponto de reflexo da lente
draw.ellipse([center_x + 3, center_y - 5, center_x + 7, center_y - 1], 
             fill=(255, 255, 255, 240))

# 2. Textos e Identidade Visual
try:
    font_badge = ImageFont.truetype("arialbd.ttf", 13)
    font_main = ImageFont.truetype("arialbd.ttf", 34)
    font_sub = ImageFont.truetype("arial.ttf", 18)
except Exception:
    font_badge = ImageFont.load_default()
    font_main = ImageFont.load_default()
    font_sub = ImageFont.load_default()

# Badge de topo "VIGILÂNCIA & PREDIÇÃO"
draw.rounded_rectangle([170, 32, 330, 60], radius=6, fill=(0, 242, 254, 25), outline=(0, 242, 254, 160), width=1)
draw.text((188, 38), "VIGIA DE REDES · IA", fill=(0, 242, 254, 255), font=font_badge)

# Nome Principal: CYPHERNET
title_text = "CYPHERNET"
bbox_t = draw.textbbox((0, 0), title_text, font=font_main)
tw = bbox_t[2] - bbox_t[0]
draw.text(((W - tw) / 2, 350), title_text, fill=(240, 246, 252, 255), font=font_main)

# Subtítulo: VIGIA DE REDES
sub_text = "VIGIA DE REDES"
bbox_s = draw.textbbox((0, 0), sub_text, font=font_sub)
sw = bbox_s[2] - bbox_s[0]
draw.text(((W - sw) / 2, 400), sub_text, fill=(0, 242, 254, 220), font=font_sub)

# Barra de status com as 3 cores das classes (OK, RISCO, FALHA)
draw.rounded_rectangle([140, 442, 220, 446], radius=2, fill=(16, 185, 129, 255)) # Verde OK
draw.rounded_rectangle([226, 442, 274, 446], radius=2, fill=(245, 158, 11, 255))  # Amarelo RISCO
draw.rounded_rectangle([280, 442, 360, 446], radius=2, fill=(239, 68, 68, 255))  # Vermelho FALHA

img.save(OUTPUT_LOGO, format="PNG")
print(f"[OK] Logo salvo em: {OUTPUT_LOGO}")
