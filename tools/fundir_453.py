# -*- coding: utf-8 -*-
"""Funde os 453 assets perdidos no workbook principal.

Depois disso, todo o pipeline existente (export_batch, traduzir_auto,
enforce_glossary, qa_check, apply_pt) passa a enxergar esses 2488 registros
sem precisar de ferramenta separada.

PRE-REQUISITO: tools/apply_pt.py precisa agrupar por PATH_ID, nao por nome
de asset. Com a fusao passam a existir nomes repetidos no workbook (dois
Day1_Q0_Interrogation, dois Labels...), e agrupar por nome fundiria assets
distintos, escrevendo tudo num path_id so'. Este script confere isso antes
de mexer em qualquer coisa e aborta se a correcao nao estiver la'.

Guarda extracted/workbook.pre453.json antes de gravar.

Uso: python fundir_453.py [--desfazer]
"""
import os, sys, json, shutil, collections

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB = os.path.join(ROOT, "extracted", "workbook.json")
W453 = os.path.join(ROOT, "extracted", "workbook_453.json")
BACKUP = os.path.join(ROOT, "extracted", "workbook.pre453.json")

if "--desfazer" in sys.argv:
    if not os.path.exists(BACKUP):
        sys.exit("nao ha backup workbook.pre453.json")
    shutil.copy2(BACKUP, WB)
    print("workbook.json restaurado do backup pre-fusao")
    sys.exit(0)

# 1. a correcao de agrupamento esta aplicada?
fonte = open(os.path.join(ROOT, "tools", "apply_pt.py"), encoding="utf-8").read()
if "by_pid[e[\"id\"].split(\".\")[0]]" not in fonte:
    sys.exit("ABORTADO: tools/apply_pt.py ainda agrupa por nome de asset.\n"
             "Corrija para agrupar por path_id antes de fundir, ou os assets\n"
             "de nome repetido vao se sobrescrever.")
print("ok: apply_pt.py agrupa por path_id")

wb = json.load(open(WB, encoding="utf-8"))
extra = json.load(open(W453, encoding="utf-8"))
print(f"workbook principal : {len(wb)} registros")
print(f"lote dos 453       : {len(extra)} registros")

# 2. nenhum id pode colidir
ids_wb = {e["id"] for e in wb}
colisao = [e["id"] for e in extra if e["id"] in ids_wb]
if colisao:
    sys.exit(f"ABORTADO: {len(colisao)} ids colidem, ex.: {colisao[:5]}")
print("ok: nenhum id colide")

# 3. path_ids tambem tem que ser disjuntos (um asset nao pode ficar partido
#    entre os dois arquivos, senao o apply_pt monta o texto pela metade)
pid_wb = {e["id"].split(".")[0] for e in wb}
pid_ex = {e["id"].split(".")[0] for e in extra}
if pid_wb & pid_ex:
    sys.exit(f"ABORTADO: {len(pid_wb & pid_ex)} path_id aparecem nos dois")
print("ok: path_ids disjuntos")

if not os.path.exists(BACKUP):
    shutil.copy2(WB, BACKUP)
    print(f"backup gravado: {os.path.basename(BACKUP)}")

junto = wb + extra
with open(WB, "w", encoding="utf-8") as fh:
    json.dump(junto, fh, ensure_ascii=False, indent=0)

nomes = collections.Counter(e["text"] for e in junto)
rep = sum(1 for n, c in nomes.items() if c > len([1]) and False)  # placeholder
por_nome = collections.defaultdict(set)
for e in junto:
    por_nome[e["text"]].add(e["id"].split(".")[0])
repetidos = {n: p for n, p in por_nome.items() if len(p) > 1}

print(f"\nworkbook.json agora: {len(junto)} registros")
print(f"   assets (path_id) : {len(pid_wb | pid_ex)}")
print(f"   nomes repetidos  : {len(repetidos)}  <- por isso o agrupamento por path_id importa")
print(f"   a traduzir       : {sum(1 for e in extra if e['pt'].strip())}")
