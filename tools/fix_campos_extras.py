"""Repara linhas em que o modelo ecoou a coluna da cena junto com a traducao.

O prompt manda "id TAB portugues", mas as vezes vem "id TAB cena TAB portugues".
Como apply_pt.py corta no primeiro TAB, o nome da cena entraria no jogo.

Seguranca: so' remove o campo do meio quando ele bate EXATAMENTE com o nome
da cena daquele id no workbook. Qualquer outra coisa fica intacta e e' relatada
para revisao a mao — um TAB legitimo dentro da fala nao pode ser engolido.

Uso:
    python fix_campos_extras.py            # dry-run
    python fix_campos_extras.py --apply
"""
import json, os, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APPLY = "--apply" in sys.argv
TAB = "\t"

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
cena = {e["id"]: e["text"] for e in wb}

corrigidas, suspeitas = 0, []
for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))):
    if os.path.basename(path) == "reviews.tsv":
        continue
    linhas = open(path, encoding="utf-8").read().split("\n")
    out, dirty = [], False
    for ln in linhas:
        p = ln.split(TAB)
        if len(p) > 2:
            wid = p[0].strip()
            if p[1].strip() == cena.get(wid, "\0"):
                ln = wid + TAB + TAB.join(p[2:])
                corrigidas += 1
                dirty = True
            else:
                suspeitas.append((os.path.basename(path), wid, ln[:110]))
        out.append(ln)
    if dirty and APPLY:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print(f"linhas com a cena ecoada (removivel com seguranca): {corrigidas}")
print(f"linhas com TAB extra NAO identificado (revisar a mao): {len(suspeitas)}")
for f, wid, l in suspeitas[:10]:
    print(f"   {f} {wid}: {l}")
print("\nGRAVADO." if APPLY else "\n(dry-run — use --apply)")
