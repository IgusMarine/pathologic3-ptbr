# -*- coding: utf-8 -*-
"""Gera as imagens do anuncio no Nexus.

A imagem principal aparece pequena na listagem (cerca de 250 px de largura),
entao o texto precisa ser legivel nesse tamanho: pouca palavra, corpo grande.
Sai em 1920x1080 para nao borrar quando o Nexus reduz.

Uso: python gerar_imagens.py
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
CAPA = os.path.join(os.path.dirname(AQUI), "installer", "capa_original.png")
L, A = 1920, 1080


def fonte(nomes, tam):
    for n in nomes:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            continue
    return ImageFont.load_default()


# ---- fundo: a capa desfocada, para nao competir com o texto ----------------
capa = Image.open(CAPA).convert("RGB")
f = max(L / capa.width, A / capa.height)
fundo = capa.resize((round(capa.width * f), round(capa.height * f)), Image.LANCZOS)
x = (fundo.width - L) // 2
fundo = fundo.crop((x, 0, x + L, A)).filter(ImageFilter.GaussianBlur(26))
fundo = Image.blend(fundo, Image.new("RGB", (L, A), (16, 9, 10)), 0.55)

# ---- a capa inteira, nitida, na esquerda -----------------------------------
alt = 980
lar = round(capa.width * alt / capa.height)
nitida = capa.resize((lar, alt), Image.LANCZOS)
px, py = 96, (A - alt) // 2
sombra = Image.new("RGBA", (lar + 60, alt + 60), (0, 0, 0, 0))
ImageDraw.Draw(sombra).rectangle([30, 30, lar + 30, alt + 30], fill=(0, 0, 0, 190))
sombra = sombra.filter(ImageFilter.GaussianBlur(22))
fundo.paste(sombra, (px - 30, py - 30), sombra)
fundo.paste(nitida, (px, py))

d = ImageDraw.Draw(fundo)
tx = px + lar + 92

f_bandeira = fonte(["seguisb.ttf", "segoeui.ttf"], 34)
f_tit = fonte(["georgiab.ttf", "timesbd.ttf"], 108)
f_sub = fonte(["georgiai.ttf", "timesi.ttf"], 60)
f_item = fonte(["segoeui.ttf", "arial.ttf"], 40)
f_chk = fonte(["seguisym.ttf", "segoeui.ttf"], 40)

y = py + 66
d.text((tx, y), "TRADUÇÃO PARA O PORTUGUÊS", font=f_bandeira, fill=(201, 134, 95))
y += 74
d.text((tx, y), "Pathologic 3", font=f_tit, fill=(240, 232, 220))
y += 128
d.text((tx, y), "em português brasileiro", font=f_sub, fill=(201, 134, 95))
y += 118

d.line([(tx, y), (tx + 300, y)], fill=(120, 96, 82), width=2)
y += 54

for txt in ["63.703 falas, o jogo inteiro",
            "Feita a partir do russo original",
            "Instalador com um clique",
            "Reversível a qualquer momento"]:
    d.text((tx, y), "✓", font=f_chk, fill=(201, 134, 95))
    d.text((tx + 56, y), txt, font=f_item, fill=(214, 204, 192))
    y += 62

saida = os.path.join(AQUI, "imagem-principal.jpg")
fundo.save(saida, "JPEG", quality=92)
print(f"imagem-principal.jpg  {fundo.size}  ({os.path.getsize(saida)/1024:.0f} KB)")

# ---- versao reduzida, para conferir a legibilidade na listagem -------------
prev = fundo.resize((300, 169), Image.LANCZOS)
prev.save(os.path.join(AQUI, "teste-miniatura.png"))
print("teste-miniatura.png   300x169  (como aparece na listagem do Nexus)")
