# -*- coding: utf-8 -*-
"""Gera o banner do topo da pagina no Nexus (1300x372).

DUAS COISAS APRENDIDAS VENDO A PAGINA PUBLICADA:

1. O container do Nexus e' mais alto que a proporcao 3,5:1 que eles
   recomendam, entao sobra uma faixa preta acima da imagem. A solucao nao e'
   mudar o tamanho (o campo pede 1300x372): e' fazer o TOPO da imagem escurecer
   ate' o preto, para a faixa se fundir com ela e sumir.

2. O Nexus sobrepoe o nome do mod e o caminho de navegacao sobre a parte de
   baixo do banner. Colocar titulo proprio ali duplica a informacao e embola a
   leitura. Entao aqui nao vai texto nenhum: o banner e' so' atmosfera, e o
   texto e' o da plataforma.

Uso: python gerar_banner.py
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
CAPA = os.path.join(os.path.dirname(AQUI), "installer", "capa_original.png")
L, A = 1300, 372
E = 2
LL, AA = L * E, A * E

capa = Image.open(CAPA).convert("RGB")

# ---- fundo: a capa ampliada e desfocada, cobrindo a faixa ------------------
f = max(LL / capa.width, AA / capa.height) * 1.9
g = capa.resize((round(capa.width * f), round(capa.height * f)), Image.LANCZOS)
# enquadra no rosto e no relogio, que e' a parte com textura
cx, cy = int(g.width * 0.5), int(g.height * 0.42)
fundo = g.crop((cx - LL // 2, cy - AA // 2, cx + LL // 2, cy + AA // 2))
fundo = fundo.filter(ImageFilter.GaussianBlur(30 * E))
fundo = Image.blend(fundo, Image.new("RGB", (LL, AA), (20, 9, 10)), 0.45)

# ---- a capa inteira, nitida, a esquerda ------------------------------------
alt = int(AA * 0.86)
lar = round(capa.width * alt / capa.height)
px, py = int(LL * 0.06), (AA - alt) // 2
sombra = Image.new("RGBA", (lar + 44 * E, alt + 44 * E), (0, 0, 0, 0))
ImageDraw.Draw(sombra).rectangle([22 * E, 22 * E, lar + 22 * E, alt + 22 * E],
                                 fill=(0, 0, 0, 205))
sombra = sombra.filter(ImageFilter.GaussianBlur(16 * E))
fundo.paste(sombra, (px - 22 * E, py - 22 * E), sombra)
fundo.paste(capa.resize((lar, alt), Image.LANCZOS), (px, py))

# ---- o topo escurece ate' o preto, para a faixa do Nexus se fundir ---------
mask = Image.new("L", (LL, AA), 0)
d = ImageDraw.Draw(mask)
lim = int(AA * 0.42)
for y in range(AA):
    if y < lim:
        v = int(255 * ((lim - y) / lim) ** 0.75)
    else:
        v = 0
    d.line([(0, y), (LL, y)], fill=v)
fundo = Image.composite(Image.new("RGB", (LL, AA), (0, 0, 0)), fundo, mask)

# ---- a base tambem escurece: e' onde o Nexus escreve o nome do mod ---------
mask2 = Image.new("L", (LL, AA), 0)
d2 = ImageDraw.Draw(mask2)
ini = int(AA * 0.62)
for y in range(ini, AA):
    d2.line([(0, y), (LL, y)], fill=int(190 * ((y - ini) / (AA - ini)) ** 1.3))
fundo = Image.composite(Image.new("RGB", (LL, AA), (0, 0, 0)), fundo, mask2)

final = fundo.resize((L, A), Image.LANCZOS)
saida = os.path.join(AQUI, "banner-1300x372.jpg")
final.save(saida, "JPEG", quality=93)
print(f"banner-1300x372.jpg  {final.size}  ({os.path.getsize(saida)/1024:.0f} KB)")

# previa de como o Nexus mostra: faixa preta em cima e titulo sobreposto
prev = Image.new("RGB", (L, 560), (0, 0, 0))
prev.paste(final, (0, 560 - A))
d3 = ImageDraw.Draw(prev)
d3.text((16, 500), "Games / Pathologic 3 / Mods / Miscellaneous /", fill=(200, 140, 90))
d3.text((16, 524), "Traducao PT-BR completa (Brazilian Portuguese)", fill=(240, 240, 240))
prev.save(os.path.join(AQUI, "_previa_nexus.png"))
print("_previa_nexus.png  simula a faixa preta e o titulo sobreposto")
