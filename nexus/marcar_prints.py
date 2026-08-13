# -*- coding: utf-8 -*-
"""Prepara os prints do jogo para o Nexus.

Faz duas coisas:

1. Cobre o overlay da NVIDIA (microfone e mira, no canto inferior direito,
   em x 2528-2545 e y 1369-1426) com uma marca da traducao. Em vez de uma
   placa de borda dura, que parece adesivo colado, usa um escurecimento em
   degrade que fecha 100% no canto e some para dentro da imagem.

2. Sai em JPEG de qualidade alta: os PNG originais tem ate' 4,6 MB e o
   limite do Nexus e' 8 MB por imagem. JPEG a 93 fica visualmente igual em
   cena fotografica e sobe muito mais rapido.

Uso: python marcar_prints.py
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
ENTRADA = os.path.join(AQUI, "Screenshots")
SAIDA = os.path.join(AQUI, "prints-prontos")
os.makedirs(SAIDA, exist_ok=True)


def fonte(nomes, tam):
    for n in nomes:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            continue
    return ImageFont.load_default()


def suave(t):
    """Curva S: transicao sem emenda visivel nas pontas."""
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def marcar(caminho, destino):
    im = Image.open(caminho).convert("RGB")
    W, H = im.size

    # --- escurecimento em degrade, cravado no canto inferior direito ------
    # Chega a opacidade total antes de alcancar os icones da NVIDIA, entao
    # eles somem por completo em vez de ficar um fantasma visivel.
    x0, x1 = W - 760, W - 165
    y0, y1 = H - 330, H - 130
    gx = suave((np.arange(W) - x0) / (x1 - x0))
    gy = suave((np.arange(H) - y0) / (y1 - y0))
    # 255, nao 232: a 91% sobrava 9% do icone, o suficiente para aparecer
    # de leve sobre fundo preto.
    alpha = (gy[:, None] * gx[None, :] * 255).astype(np.uint8)

    base = np.array(im)
    escuro = np.zeros_like(base)
    a = alpha[:, :, None] / 255.0
    im = Image.fromarray((base * (1 - a) + escuro * a).astype(np.uint8))

    # --- a marca ----------------------------------------------------------
    d = ImageDraw.Draw(im)
    f_olho = fonte(["seguisb.ttf", "segoeui.ttf"], 25)
    f_tit = fonte(["georgiab.ttf", "timesbd.ttf"], 44)

    margem_x, margem_y = W - 52, H - 46
    tit = "TRADUÇÃO PT-BR"
    olho = "PATHOLOGIC 3"

    lt = d.textlength(tit, font=f_tit)
    lo = d.textlength(olho, font=f_olho)
    d.text((margem_x - lo, margem_y - 88), olho, font=f_olho, fill=(178, 126, 96))
    d.text((margem_x - lt, margem_y - 56), tit, font=f_tit, fill=(238, 230, 218))
    d.line([(margem_x - lt, margem_y - 4), (margem_x, margem_y - 4)],
           fill=(150, 110, 88), width=2)

    im.save(destino, "JPEG", quality=93, subsampling=0)
    return im


def sobrou_overlay(im):
    """Confere que nenhum pixel claro sobrou onde ficavam os icones."""
    a = np.array(im.convert("L"))
    # limiar baixo: o icone precisa sumir, nao so ficar mais escuro.
    # Comeca em 2512 porque a linha da propria marca termina em 2508 e
    # estava sendo contada como se fosse residuo do overlay.
    return int((a[1355:1440, 2512:2560] > 32).sum())


arquivos = sorted(f for f in os.listdir(ENTRADA) if f.lower().endswith(".png")
                  and not f.startswith("_"))
print(f"{len(arquivos)} prints\n")
for f in arquivos:
    dst = os.path.join(SAIDA, os.path.splitext(f)[0] + ".jpg")
    im = marcar(os.path.join(ENTRADA, f), dst)
    resto = sobrou_overlay(im)
    kb_antes = os.path.getsize(os.path.join(ENTRADA, f)) / 1024
    kb = os.path.getsize(dst) / 1024
    marca = "ok" if resto == 0 else f"ATENCAO: {resto} px claros restantes"
    print(f"  {f} -> {os.path.basename(dst)}   {kb_antes:6.0f} KB -> {kb:5.0f} KB   {marca}")

print(f"\ngravados em {SAIDA}")
