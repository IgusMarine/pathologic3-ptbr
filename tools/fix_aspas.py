"""Normaliza aspas para o padrao do projeto: «assim».

Dentro de uma fala, aspas retas ("x") ou curvas (“x”) sao sempre erro —
o projeto usa guillemets em 1.257 linhas. E o defeito mais recorrente da
traducao automatica, e tem resposta unica, entao vira correcao automatica.

Excecao: os creditos. La as aspas cercam apelidos de pessoas reais,
escritos assim pelos proprios desenvolvedores — nao se mexe.

Aspas impares (uma solitaria, sem par) NAO sao tocadas: podem ser
polegada, minuto ou um erro que precisa de olho humano. Sao relatadas.

Uso:
    python fix_aspas.py            # dry-run
    python fix_aspas.py --apply
"""
import os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS = os.path.join(ROOT, "translated", "pt")
APPLY = "--apply" in sys.argv

CREDITOS = ("Other_00b", "Other_00c", "Other_05a")
ASPAS = '"“”'
PAR = re.compile("[" + ASPAS + "]([^" + ASPAS + "]*)[" + ASPAS + "]")
QUALQUER = re.compile("[" + ASPAS + "]")

trocas, impares = [], []
for path in sorted(glob.glob(os.path.join(TRANS, "*.tsv"))):
    nome = os.path.basename(path)
    if nome == "reviews.tsv" or any(nome.startswith(c) for c in CREDITOS):
        continue
    linhas = open(path, encoding="utf-8").read().split("\n")
    out, dirty = [], False
    for ln in linhas:
        wid, sep, pt = ln.partition("\t")
        # citacao aninhada «... „x“ ...» e' convencao correta (o russo faz
        # igual). Nao mexer nessas linhas.
        if "„" in pt:
            out.append(ln)
            continue
        if sep and QUALQUER.search(pt):
            novo = PAR.sub(lambda m: "«" + m.group(1) + "»", pt)
            if QUALQUER.search(novo):
                impares.append((nome, wid.strip(), novo[:80]))
            if novo != pt:
                for m in PAR.finditer(pt):
                    trocas.append((nome, wid.strip(), m.group(1)[:45]))
                pt, dirty = novo, True
            ln = wid + sep + pt
        out.append(ln)
    if dirty and APPLY:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print(f"pares convertidos para «»: {len(trocas)}")
for f, wid, t in trocas[:12]:
    print(f"   {f} {wid}: «{t}»")
if impares:
    print(f"\naspas impares deixadas intactas (revisar): {len(impares)}")
    for f, wid, t in impares[:8]:
        print(f"   {f} {wid}: {t}")
print("\nGRAVADO." if APPLY else "\n(dry-run — use --apply)")
