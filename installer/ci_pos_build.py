# -*- coding: utf-8 -*-
"""Pos-processamento do build do cx_Freeze.

1. Extrai lib/library.zip e o remove: compactado dentro de compactado e'
   quarentena automatica no Nexus, e o scanner de la nao abre aninhamento.
2. Confere que nao sobrou nenhum arquivo compactado e que o executavel
   existe.

Uso: python ci_pos_build.py <pasta_do_build>
"""
import zipfile, sys, os

pasta = sys.argv[1]
lz = os.path.join(pasta, "lib", "library.zip")
if os.path.exists(lz):
    with zipfile.ZipFile(lz) as z:
        n = len(z.namelist())
        z.extractall(os.path.join(pasta, "lib"))
    os.remove(lz)
    print(f"library.zip desfeito: {n} modulos soltos em lib/")

COMP = (".zip", ".whl", ".egg", ".7z", ".rar", ".tar", ".gz", ".cab")
sobras = [os.path.join(r, f) for r, _, fs in os.walk(pasta)
          for f in fs if f.lower().endswith(COMP)]
exe = os.path.join(pasta, "Instalar-Traducao-PTBR.exe")
total = sum(len(fs) for _, _, fs in os.walk(pasta))

print(f"arquivos no build : {total}")
print(f"compactados dentro: {len(sobras)}")
print(f"executavel        : {'ok' if os.path.exists(exe) else 'FALTANDO'}")
if sobras or not os.path.exists(exe):
    sys.exit("build reprovado")
print("build aprovado")
