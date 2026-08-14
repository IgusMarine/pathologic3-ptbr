# -*- coding: utf-8 -*-
"""Extrai da Release publicada os tres arquivos que o build precisa e que
nao vivem no repositorio: a arte (da Ice-Pick Lodge, que nao versionamos de
proposito) e a traducao compilada (gerada, publicada como Release).

Uso: python ci_extrair_dados.py <release.zip>
"""
import zipfile, sys, os

AQUI = os.path.dirname(os.path.abspath(__file__))
ALVO = {"app/arte.png": "arte.png",
        "app/icone.ico": "icone.ico",
        "app/ptbr_final.json": "ptbr_final.json"}

achados = 0
with zipfile.ZipFile(sys.argv[1]) as z:
    for nome in z.namelist():
        for sufixo, destino in ALVO.items():
            if nome.endswith(sufixo):
                with open(os.path.join(AQUI, destino), "wb") as fh:
                    fh.write(z.read(nome))
                print(f"  {destino}  <-  {nome}")
                achados += 1

if achados != len(ALVO):
    sys.exit(f"esperava {len(ALVO)} arquivos, achei {achados}")
print("dados extraidos")
