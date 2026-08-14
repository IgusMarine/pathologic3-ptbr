# -*- coding: utf-8 -*-
"""Gera o header do topo da pagina no Nexus (1300x372).

Restricoes aprendidas com a pagina publicada:

1. O container do Nexus e' mais alto que 3,5:1, e a sobra vira faixa preta
   acima da imagem. Correcao: o TOPO da imagem escurece ate' o preto puro,
   e a faixa se funde com ela.
2. O Nexus sobrepoe a miniatura do mod (esquerda) e o nome + navegacao
   (canto inferior esquerdo) sobre o banner. Entao: nenhum texto proprio,
   base escurecida, e o elemento focal fica a DIREITA, fora da area deles.

Composicao: textura do relogio da capa ao fundo, e a mascara — o objeto
mais iconico do jogo — em foco suave a direita.

Uso: python gerar_banner.py
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

AQUI = os.path.dirname(os.path.abspath(__file__))
CAPA = os.path.join(os.path.dirname(AQUI), "installer", "capa_original.png")
L, A = 1300, 372
E = 2                       # desenha em dobro e reduz: texto/bordas lisas
LL, AA = L * E, A * E

capa = Image.open(CAPA).convert("RGB")

# ---- fundo: o relogio vira textura -----------------------------------------
f = max(LL / capa.width, AA / capa.height) * 1.15
g = capa.resize((round(capa.width * f), round(capa.height * f)), Image.LANCZOS)
cx, cy = int(g.width * 0.5), int(g.height * 0.17)
img = g.crop((cx - LL // 2, max(0, cy - AA // 2),
              cx + LL // 2, max(0, cy - AA // 2) + AA))
img = img.filter(ImageFilter.GaussianBlur(5 * E))
img = Image.blend(img, Image.new("RGB", (LL, AA), (14, 6, 7)), 0.34)

# ---- topo escurece ate' o preto: a faixa do Nexus se funde ------------------
mk = Image.new("L", (LL, AA), 0)
d = ImageDraw.Draw(mk)
lim = int(AA * 0.44)
for y in range(AA):
    d.line([(0, y), (LL, y)],
           fill=int(255 * ((lim - y) / lim) ** 0.85) if y < lim else 0)
img = Image.composite(Image.new("RGB", (LL, AA), (0, 0, 0)), img, mk)

# ---- a mascara, emergindo do escuro, a direita ------------------------------
# Colada DEPOIS do degrade do topo, de proposito: em vez de ser engolida por
# ele, ela surge do preto. O recorte e' centrado na mascara inteira, com os
# furos dos olhos — e' isso que a torna reconhecivel e nao um ovo branco.
elem = capa.crop((930, 850, 1430, 1350))
tam = int(AA * 0.80)
elem = elem.resize((tam, tam), Image.LANCZOS)
yy, xx = np.mgrid[0:tam, 0:tam]
r = np.sqrt((xx - tam / 2) ** 2 + (yy - tam / 2) ** 2) / (tam / 2)
alfa = np.clip((0.97 - r) / 0.40, 0, 1)          # some nas bordas, sem recorte duro
m = Image.fromarray((alfa * 255).astype("uint8"))
px, py = int(LL * 0.76) - tam // 2, int(AA * 0.42) - tam // 2
img.paste(elem, (px, py), m)

# ---- base escurece: e' onde o Nexus escreve o nome do mod -------------------
# mais forte a esquerda (onde o texto fica), mais leve a direita (a mascara)
gy = np.zeros((AA, LL), dtype=float)
ini = int(AA * 0.46)
for y in range(ini, AA):
    gy[y, :] = ((y - ini) / (AA - ini)) ** 1.15
gx = np.linspace(1.0, 0.62, LL)[None, :]         # atenua o fade no lado direito
alpha = (gy * gx * 235).astype("uint8")
base = np.array(img).astype(float)
img = Image.fromarray((base * (1 - alpha[:, :, None] / 255.0)).astype("uint8"))

final = img.resize((L, A), Image.LANCZOS)
saida = os.path.join(AQUI, "banner-1300x372.jpg")
final.save(saida, "JPEG", quality=93)
print(f"banner-1300x372.jpg  {final.size}  ({os.path.getsize(saida)/1024:.0f} KB)")

# ---- previa de como a pagina mostra ----------------------------------------
prev = Image.new("RGB", (L, 560), (0, 0, 0))
prev.paste(final, (0, 560 - A))
cap = capa.resize((133, 200), Image.LANCZOS)
prev.paste(cap, (45, 300))
d3 = ImageDraw.Draw(prev)
d3.text((190, 505), "Games / Pathologic 3 / Mods / Miscellaneous /", fill=(205, 145, 95))
d3.text((190, 528), "Traducao PT-BR completa (Brazilian Portuguese)", fill=(245, 245, 245))
prev.save(os.path.join(AQUI, "_previa_nexus.png"))
print("_previa_nexus.png    simulacao com a faixa e o titulo do Nexus")
