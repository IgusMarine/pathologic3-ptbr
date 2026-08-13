"""Detecta cena inteira com traducao presa aos ids errados.

O detector por latim/numero e' fraco: so' pega onde ha ancora, e ancora e'
rara. Este usa correlacao de COMPRIMENTO.

Ideia: numa cena bem alinhada, fala curta em russo vira fala curta em
portugues, e longa vira longa. A correlacao entre os comprimentos e' alta.
Se a traducao escorregou de lugar, essa relacao se desfaz.

Reforco: tambem testa se a cena casaria melhor com um DESLOCAMENTO (a PT
da linha N correspondendo ao RU da linha N-k). Se casar muito melhor com
k != 0, e' desalinhamento — e o k encontrado diz o tamanho do escorregao.

Nao corrige nada. Cena apontada precisa de conferencia manual.

Uso: python auditar_desalinhamento.py [minimo_de_linhas]
"""
import json, os, glob, sys, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Abaixo de ~20 linhas a correlacao e' ruido: cenas de 8 linhas foram
# apontadas e estavam perfeitamente alinhadas. 20 e' o piso confiavel.
MIN_LINHAS = int(sys.argv[1]) if len(sys.argv) > 1 else 20

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
byid = {e["id"]: e for e in wb}
tr = {}
for p in glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv")):
    if os.path.basename(p) == "reviews.tsv":
        continue
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.strip():
            w, _, t = ln.partition("\t")
            tr[w.strip()] = (t, os.path.basename(p))


def corr(a, b):
    if len(a) < 4:
        return 0.0
    try:
        return statistics.correlation(a, b)
    except Exception:
        return 0.0


cenas = {}
for wid, (pt, arq) in tr.items():
    e = byid.get(wid)
    if not e:
        continue
    cenas.setdefault(e["text"], []).append((wid, e.get("ru") or "", pt, arq))

suspeitas = []
for cena, its in cenas.items():
    its.sort(key=lambda x: (int(x[0].split(".")[0]), int(x[0].split(".")[1])))
    its = [x for x in its if len(x[1]) > 12 and len(x[2]) > 12]
    if len(its) < MIN_LINHAS:
        continue
    ru = [len(x[1]) for x in its]
    pt = [len(x[2]) for x in its]
    base = corr(ru, pt)

    # testa deslocamentos: a PT casaria melhor deslocada?
    melhor_k, melhor_c = 0, base
    for k in range(1, min(25, len(its) // 2)):
        c1 = corr(ru[:-k], pt[k:])   # pt atrasada
        c2 = corr(ru[k:], pt[:-k])   # pt adiantada
        if c1 > melhor_c + 0.15:
            melhor_k, melhor_c = k, c1
        if c2 > melhor_c + 0.15:
            melhor_k, melhor_c = -k, c2

    if base < 0.45 or melhor_k != 0:
        suspeitas.append((cena, its[0][3], len(its), round(base, 2),
                          melhor_k, round(melhor_c, 2)))

suspeitas.sort(key=lambda x: x[3])
print(f"cenas analisadas: {sum(1 for c in cenas.values() if len(c) >= MIN_LINHAS)}")
print(f"cenas suspeitas: {len(suspeitas)}\n")
print(f"{'cena':<52}{'arq':<16}{'n':>4}{'corr':>7}{'desloc':>8}{'corr2':>7}")
for cena, arq, n, base, k, c2 in suspeitas[:30]:
    marca = "  <<<" if k != 0 or base < 0.25 else ""
    print(f"{cena.replace('_Portuguese_Br','')[:50]:<52}{arq:<16}{n:>4}{base:>7}{k:>8}{c2:>7}{marca}")
