# -*- coding: utf-8 -*-
"""Prepara a capa do jogo para o painel esquerdo do instalador.

A capa e' 2:3 (1440x2160) e o painel e' 600x820, mais largo em proporcao.
Escala para cobrir e corta o TOPO: assim o rosto e o titulo, que estao na
metade de baixo, ficam inteiros — cortar embaixo decapitaria o logo.

Uso: python gerar_arte.py
"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from PIL import Image, ImageDraw

AQUI = os.path.dirname(os.path.abspath(__file__))
L, A = 600, 820

orig = Image.open(os.path.join(AQUI, "capa_original.png")).convert("RGB")
lo, ao = orig.size

# escala para COBRIR o painel inteiro
f = max(L / lo, A / ao)
novo = orig.resize((round(lo * f), round(ao * f)), Image.LANCZOS)
ln, an = novo.size

# corta o excedente do topo (o titulo fica embaixo e precisa sobreviver)
esq = (ln - L) // 2
topo = an - A
img = novo.crop((esq, topo, esq + L, topo + A))

# leve escurecimento na borda direita, para o texto do painel ao lado
# nao competir com a arte
sombra = Image.new("L", (L, A), 0)
d = ImageDraw.Draw(sombra)
for x in range(L - 90, L):
    d.line([(x, 0), (x, A)], fill=int(90 * (x - (L - 90)) / 90))
img = Image.composite(Image.new("RGB", (L, A), (10, 6, 7)), img, sombra)

img.save(os.path.join(AQUI, "arte.png"), "PNG")
print(f"arte.png: {img.size}  ({os.path.getsize(os.path.join(AQUI,'arte.png'))/1024:.0f} KB)")

# icone: recorta a mascara, que e' o simbolo mais reconhecivel da capa
cx, cy = round(1000 * f) - esq, round(950 * f) - topo
lado = round(430 * f)
cai = img.crop((max(0, cx - lado // 2), max(0, cy - lado // 2),
                min(L, cx + lado // 2), min(A, cy + lado // 2)))
cai = cai.resize((256, 256), Image.LANCZOS)
cai.save(os.path.join(AQUI, "icone.ico"),
         sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icone.ico gravado")
