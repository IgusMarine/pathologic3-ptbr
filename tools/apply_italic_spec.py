"""Converte work/italicos_spec.tsv (revisao manual) em work/italicos_revisados.tsv.

A spec diz, por id, QUAL trecho da PT carrega a enfase do original. Este
script so envolve esse trecho em <i>...</i> — nunca reescreve texto. Se o
trecho nao existir, ou existir menos vezes que a ocorrencia pedida, falha
alto em vez de adivinhar.

Uso: python apply_italic_spec.py
Depois: python fix_italics.py --apply
"""
import os, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "work", "italicos_spec.tsv")
OUT = os.path.join(ROOT, "work", "italicos_revisados.tsv")
TRANS = os.path.join(ROOT, "translated", "pt")

# PT atual, por id
cur = {}
for path in sorted(glob.glob(os.path.join(TRANS, "*.tsv"))):
    if os.path.basename(path) == "reviews.tsv":
        continue
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip():
            continue
        wid, _, pt = ln.partition("\t")
        cur[wid.strip()] = pt

spec = collections.defaultdict(list)
for ln in open(SPEC, encoding="utf-8"):
    ln = ln.rstrip("\n")
    if not ln.strip() or ln.lstrip().startswith("#"):
        continue
    parts = ln.split("\t")
    wid = parts[0].strip()
    target = parts[1] if len(parts) > 1 else ""
    occ = int(parts[2]) if len(parts) > 2 and parts[2].strip() else 1
    spec[wid].append((target, occ))

ok, fail = {}, []
for wid, items in spec.items():
    if wid not in cur:
        fail.append((wid, "<id inexistente>", ""))
        continue
    text = cur[wid]
    for target, occ in items:
        # posicao da occ-esima ocorrencia, ignorando o que ja foi marcado
        idx, start, found = -1, 0, 0
        while True:
            p = text.find(target, start)
            if p < 0:
                break
            found += 1
            if found == occ:
                idx = p
                break
            start = p + 1
        if idx < 0:
            fail.append((wid, target, f"achado {found}x, pedido #{occ}"))
            continue
        text = text[:idx] + "<i>" + target + "</i>" + text[idx + len(target):]
    if text != cur[wid]:
        ok[wid] = text

with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
    fh.write("# gerado por apply_italic_spec.py — nao editar a mao\n")
    for wid, text in ok.items():
        fh.write(f"{wid}\t{text}\n")

print(f"linhas marcadas: {len(ok)}")
print(f"falhas: {len(fail)}")
for wid, target, why in fail:
    print(f"  FALHOU {wid}: '{target}' {why}")
    if wid in cur:
        print(f"     PT: {cur[wid][:160]}")
