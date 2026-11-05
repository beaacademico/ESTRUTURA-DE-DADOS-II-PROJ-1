# -*- coding: utf-8 -*-
"""
Gerador Oficial de QR Codes — CypherNet: Vigia de Redes (Grupo 05).

Gera:
1. QR Code limpo de alta resolução (1024x1024 px) para a Página da Mostra (/feira/)
2. Card QR Code estilizado (1200x1500 px) com identidade visual CypherNet + Logo central
3. QR Code limpo de alta resolução (1024x1024 px) para a raiz do GitHub Pages (/)
4. Espelha feira/index.html em docs/feira/index.html para garantir que o GitHub Pages
   (configurado na pasta /docs) sirva a URL /feira/ sem erro 404.
"""

from __future__ import annotations

import os
import shutil
import sys

import qrcode
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(REPO_ROOT, "docs")
FEIRA_DIR = os.path.join(REPO_ROOT, "feira")
DOWNLOADS_DIR = os.path.dirname(os.path.dirname(REPO_ROOT))
ARTIFACT_DIR = r"C:\Users\BrenoBrasildeSouza\.gemini\antigravity\brain\495869da-d820-42a4-9072-71b4bfbd61f9"

URL_FEIRA = "https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/feira/"
URL_RAIZ = "https://beaacademico.github.io/ESTRUTURA-DE-DADOS-II-PROJ-1/"


def carregar_fonte(tamanho: int, negrito: bool = False):
    candidatas = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/calibrib.ttf"]
        if negrito
        else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/calibri.ttf"]
    )
    for caminho in candidatas:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()


def gerar_qr_limpo(url: str, cor_preenchimento: str = "#16212B", cor_fundo: str = "#FFFFFF", com_logo: bool = True) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color=cor_preenchimento, back_color=cor_fundo).convert("RGBA")
    img_qr = img_qr.resize((1024, 1024), Image.Resampling.NEAREST)

    caminho_logo = os.path.join(DOCS_DIR, "logo_nomedoprojeto.png")
    if com_logo and os.path.exists(caminho_logo):
        logo = Image.open(caminho_logo).convert("RGBA")
        tam_logo = 210
        logo = logo.resize((tam_logo, tam_logo), Image.Resampling.LANCZOS)

        # Moldura branca arredondada no centro para leitura óptica perfeita
        pad = 16
        box_size = tam_logo + 2 * pad
        fundo_logo = Image.new("RGBA", (box_size, box_size), (0, 0, 0, 0))
        draw_bg = ImageDraw.Draw(fundo_logo)
        draw_bg.rounded_rectangle(
            [0, 0, box_size - 1, box_size - 1],
            radius=28,
            fill=(255, 255, 255, 255),
            outline=(15, 118, 110, 255),
            width=4,
        )
        pos_bg = ((1024 - box_size) // 2, (1024 - box_size) // 2)
        pos_logo = ((1024 - tam_logo) // 2, (1024 - tam_logo) // 2)
        img_qr.alpha_composite(fundo_logo, dest=pos_bg)
        img_qr.alpha_composite(logo, dest=pos_logo)

    return img_qr.convert("RGB")


def gerar_card_mostra(qr_img: Image.Image, url: str) -> Image.Image:
    W, H = 1200, 1520
    card = Image.new("RGB", (W, H), "#0B131E")
    draw = ImageDraw.Draw(card)

    # Moldura tática CypherNet
    draw.rounded_rectangle([28, 28, W - 28, H - 28], radius=32, fill="#111D2C", outline="#00F2FE", width=3)
    draw.rounded_rectangle([48, 48, W - 48, H - 48], radius=24, outline="#1E344B", width=2)

    f_kicker = carregar_fonte(26, negrito=True)
    f_titulo = carregar_fonte(56, negrito=True)
    f_sub = carregar_fonte(28, negrito=False)
    f_url = carregar_fonte(22, negrito=True)

    # Cabeçalho
    kicker = "MOSTRA DE TECNOLOGIA 2026 · GRUPO 05"
    bbox_k = draw.textbbox((0, 0), kicker, font=f_kicker)
    draw.text(((W - (bbox_k[2] - bbox_k[0])) // 2, 88), kicker, fill="#00F2FE", font=f_kicker)

    titulo = "CypherNet: Vigia de Redes"
    bbox_t = draw.textbbox((0, 0), titulo, font=f_titulo)
    draw.text(((W - (bbox_t[2] - bbox_t[0])) // 2, 132), titulo, fill="#F0F6FC", font=f_titulo)

    sub = "Diagnóstico e Predição de Degradação com Árvore de Decisão e RIPE Atlas"
    bbox_s = draw.textbbox((0, 0), sub, font=f_sub)
    draw.text(((W - (bbox_s[2] - bbox_s[0])) // 2, 210), sub, fill="#94A3B8", font=f_sub)

    # Quadro branco central com o QR Code
    qr_box_size = 940
    qr_resized = qr_img.resize((qr_box_size, qr_box_size), Image.Resampling.NEAREST)
    x_qr = (W - qr_box_size) // 2
    y_qr = 285
    draw.rounded_rectangle(
        [x_qr - 20, y_qr - 20, x_qr + qr_box_size + 20, y_qr + qr_box_size + 20],
        radius=28,
        fill="#FFFFFF",
        outline="#00F2FE",
        width=4,
    )
    card.paste(qr_resized, (x_qr, y_qr))

    # Rodapé com instrução e URL
    inst = "Aponte a câmera do celular para acessar a página interativa e o vídeo pitch (90s)"
    bbox_i = draw.textbbox((0, 0), inst, font=f_sub)
    draw.text(((W - (bbox_i[2] - bbox_i[0])) // 2, 1280), inst, fill="#E2E8F0", font=f_sub)

    bbox_u = draw.textbbox((0, 0), url, font=f_url)
    draw.text(((W - (bbox_u[2] - bbox_u[0])) // 2, 1335), url, fill="#00F2FE", font=f_url)

    equipe = "Beatriz · Breno · Enzo · Natsumi · Pedro · Vitória"
    bbox_e = draw.textbbox((0, 0), equipe, font=f_sub)
    draw.text(((W - (bbox_e[2] - bbox_e[0])) // 2, 1400), equipe, fill="#64748B", font=f_sub)

    return card


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    # 1. Espelhar feira/index.html em docs/feira/index.html para suporte ao GitHub Pages (/docs)
    feira_src = os.path.join(FEIRA_DIR, "index.html")
    docs_feira_dir = os.path.join(DOCS_DIR, "feira")
    os.makedirs(docs_feira_dir, exist_ok=True)
    if os.path.exists(feira_src):
        shutil.copy2(feira_src, os.path.join(docs_feira_dir, "index.html"))
        print(f"[OK] feira/index.html espelhado em docs/feira/index.html (compatível com GitHub Pages /docs)")

    # 2. Gerar QR Code principal da Feira (/feira/) com logo e sem logo
    qr_feira = gerar_qr_limpo(URL_FEIRA, com_logo=True)
    qr_feira_puro = gerar_qr_limpo(URL_FEIRA, com_logo=False)
    card_feira = gerar_card_mostra(qr_feira, URL_FEIRA)

    # 3. Gerar QR Code da raiz do GitHub Pages (/)
    qr_raiz = gerar_qr_limpo(URL_RAIZ, com_logo=True)

    arquivos = [
        ("qrcode_cyphernet_feira.png", qr_feira),
        ("qrcode_cyphernet_feira_puro.png", qr_feira_puro),
        ("qrcode_cyphernet_card_mostra.png", card_feira),
        ("qrcode_cyphernet_site_principal.png", qr_raiz),
    ]

    for nome, img in arquivos:
        p_docs = os.path.join(DOCS_DIR, nome)
        p_down = os.path.join(DOWNLOADS_DIR, nome)
        img.save(p_docs, format="PNG", optimize=True)
        shutil.copy2(p_docs, p_down)
        if os.path.exists(ARTIFACT_DIR):
            shutil.copy2(p_docs, os.path.join(ARTIFACT_DIR, nome))
        print(f"[OK] {nome} salvo em docs/ e em {p_down}")


if __name__ == "__main__":
    main()
