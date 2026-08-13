# -*- coding: utf-8 -*-
"""Gera o banner do topo da pagina no Nexus (1300x372).

A capa do jogo e' retrato 2:3 e o banner e' 3,5:1, entao nao da' para
esticar nem cortar: vira composicao horizontal, com a capa inteira a
esquerda e o texto ao lado.

Desenha em dobro e reduz no fim, para o texto sair liso.

Uso: python gerar_banner.py
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
CAPA = os.path.join(os.path.dirname(AQUI), "installer", "capa_original.png")
L, A = 1300, 372
E = 2                      # desenha em 2x
LL, AA = L * E, A * E


def fonte(nomes, tam):
    for n in nomes:
        try:
            return ImageFont.truetype(n, tam)
        except OSError:
            continue
    return ImageFont.load_default()


capa = Image.open(CAPA).convert("RGB")

# ---- fundo: a propria capa desfocada, cobrindo a faixa ---------------------
f = max(LL / capa.width, AA / capa.height)
fundo = capa.resize((round(capa.width * f), round(capa.height * f)), Image.LANCZOS)
x = (fundo.width - LL) // 2
y = int(fundo.height * 0.30)
fundo = fundo.crop((x, y, x + LL, y + AA)).filter(ImageFilter.GaussianBlur(40 * E))
fundo = Image.blend(fundo, Image.new("RGB", (LL, AA), (18, 10, 11)), 0.58)

# escurece a direita, onde vai o texto
grad = Image.new("L", (LL, AA), 0)
g = ImageDraw.Draw(grad)
ini = int(LL * 0.22)
for i in range(ini, LL):
    g.line([(i, 0), (i, AA)], fill=int(150 * (i - ini) / (LL - ini)))
fundo = Image.composite(Image.new("RGB", (LL, AA), (14, 8, 9)), fundo, grad)

# ---- a capa inteira, nitida, a esquerda ------------------------------------
alt = 300 * E
lar = round(capa.width * alt / capa.height)
px, py = 46 * E, (AA - alt) // 2
sombra = Image.new("RGBA", (lar + 40 * E, alt + 40 * E), (0, 0, 0, 0))
ImageDraw.Draw(sombra).rectangle([20 * E, 20 * E, lar + 20 * E, alt + 20 * E],
                                 fill=(0, 0, 0, 200))
sombra = sombra.filter(ImageFilter.GaussianBlur(14 * E))
fundo.paste(sombra, (px - 20 * E, py - 20 * E), sombra)
fundo.paste(capa.resize((lar, alt), Image.LANCZOS), (px, py))

# ---- texto -----------------------------------------------------------------
d = ImageDraw.Draw(fundo)
tx = px + lar + 52 * E

f_olho = fonte(["seguisb.ttf", "segoeui.ttf"], 20 * E)
f_tit = fonte(["georgiab.ttf", "timesbd.ttf"], 66 * E)
f_sub = fonte(["georgiai.ttf", "timesi.ttf"], 34 * E)
f_pe = fonte(["segoeui.ttf", "arial.ttf"], 21 * E)

yy = py + 18 * E
d.text((tx, yy), "TRADUÇÃO PARA O PORTUGUÊS", font=f_olho, fill=(196, 130, 92))
yy += 40 * E
d.text((tx, yy), "Pathologic 3", font=f_tit, fill=(242, 234, 222))
yy += 86 * E
d.text((tx, yy), "em português brasileiro", font=f_sub, fill=(201, 134, 95))
yy += 62 * E
d.line([(tx, yy), (tx + 210 * E, yy)], fill=(120, 94, 80), width=2 * E)
yy += 26 * E

# uma linha so': banner cheio de texto nao se le
partes = ["63.703 falas", "o jogo inteiro", "instalador de um clique"]
cx = tx
for i, p in enumerate(partes):
    if i:
        d.text((cx, yy), "  ·  ", font=f_pe, fill=(126, 106, 96))
        cx += d.textlength("  ·  ", font=f_pe)
    d.text((cx, yy), p, font=f_pe, fill=(206, 194, 182))
    cx += d.textlength(p, font=f_pe)

# ---- reduz e grava ---------------------------------------------------------
final = fundo.resize((L, A), Image.LANCZOS)
saida = os.path.join(AQUI, "banner-1300x372.jpg")
final.save(saida, "JPEG", quality=93)
print(f"banner-1300x372.jpg  {final.size}  ({os.path.getsize(saida)/1024:.0f} KB, limite 8 MB)")
