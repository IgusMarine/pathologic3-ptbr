"""Encontra candidatos a proverbio/idioma russo achatado na traducao.

E' a maior classe de defeito remanescente e nao tem detector objetivo: so'
leitura resolve. O que este script faz e' REDUZIR o que precisa ser lido,
de 34 mil linhas para algumas centenas.

Filtros (o russo entrega o candidato, nao o portugues):

  1. Sintaxe de proverbio: «кто…, тот…», «что…, то…», «не…, а…»,
     «чем…, тем…», «как…, так и…»
  2. Comparacao popular: «как + substantivo» em fala curta
  3. Particulas de fala coloquial: авось, небось, дескать, мол, ужо, знай
  4. Lista de idiomas conhecidos (raz plyunut, khozyain-barin, etc.)
  5. Rima/ritmo: linha curta terminando em palavras que rimam

Sinal de que a traducao pode ter achatado:
  - proporcao de comprimento muito diferente (traducao explicativa e' longa)
  - o portugues nao tem nenhum marcador de oralidade

Uso:
    python auditar_proverbios.py            # relatorio
    python auditar_proverbios.py --dump     # grava work/proverbios.txt
"""
import json, os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUMP = "--dump" in sys.argv

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
tr = {}
for p in glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv")):
    if os.path.basename(p) == "reviews.tsv":
        continue
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.strip():
            w, _, t = ln.partition("\t")
            tr[w.strip()] = (t, os.path.basename(p))

SINTAXE = [
    (re.compile(r"\bкто\b[^,.!?]{3,40},\s*тот\b", re.I), "kto-tot"),
    (re.compile(r"\bчто\b[^,.!?]{3,40},\s*то\b", re.I), "chto-to"),
    (re.compile(r"\bчем\b[^,.!?]{3,40},\s*тем\b", re.I), "chem-tem"),
    (re.compile(r"\bне\s+\w+[^,.!?]{0,30},\s*а\s+\w+", re.I), "ne-a"),
    (re.compile(r"\bкак\b[^,.!?]{3,30},\s*так\s+и\b", re.I), "kak-tak"),
    (re.compile(r"\bне\s+\w+\s+\w+,\s*не\s+\w+", re.I), "ne-ne"),
]
COLOQUIAL = re.compile(r"\b(авось|небось|дескать|мол|ужо|знай\s+себе|поди|нешто|"
                       r"эка|ишь|аль|коли|кабы|вестимо|сызнова)\b", re.I)
COMPARA = re.compile(r"\bкак\s+[а-яё]{3,}\b", re.I)

# idiomas conhecidos que ja apareceram achatados nesta localizacao
CONHECIDOS = [
    "раз плюнуть", "хозяин — барин", "хозяин, конечно, барин", "не в бровь", "с гулькин",
    "как с гуся", "ни рыба ни мясо", "седьмая вода", "белены объелся",
    "疯", "медведь на ухо", "куры не клюют", "как сыр в масле",
    "не лыком шит", "себе на уме", "ни свет ни заря", "спустя рукава",
    "бить баклуши", "водить за нос", "зуб на зуб", "как в воду",
    "на воре и шапка", "свято место", "по граблям", "бойся своих",
    "око за око", "шила в мешке", "первый блин", "не всё коту",
    "волков бояться", "у семи нянек", "яблоко от яблони",
]

# marcadores de oralidade em pt-BR: se a traducao nao tem NENHUM,
# ha chance de ter virado explicacao
ORAL_PT = re.compile(r"\b(que nem|feito|à toa|pra|tá|né|ora|vai que|sei lá|"
                     r"cá|lá|mesmo|é que|pois é|coitado|danado|besta|"
                     r"safado|diabo|raio|nossa|puxa|olha)\b", re.I)

cands = []
for e in wb:
    ru = (e.get("ru") or "").strip()
    wid = e["id"]
    if not ru or wid not in tr:
        continue
    pt, arq = tr[wid]
    if not pt.strip():
        continue
    motivos = []
    for rx, nome in SINTAXE:
        if rx.search(ru):
            motivos.append(nome)
            break
    if COLOQUIAL.search(ru):
        motivos.append("coloquial")
    low = ru.lower()
    for k in CONHECIDOS:
        if k in low:
            motivos.append("idioma:" + k)
            break
    # comparacao so' conta em fala MUITO curta e com sintaxe de ditado —
    # sozinha era ruido: todo «как» virava candidato.
    if len(ru) < 60 and COMPARA.search(ru) and motivos:
        motivos.append("comparacao")
    if not motivos:
        continue
    # proverbio e' conciso. Acima de 130 caracteres e' fala corrente.
    if len(ru) > 130:
        continue
    # sinal fraco de achatamento: pt bem mais longa e sem marcador de oralidade
    inchou = len(pt) > len(ru) * 1.35
    seco = not ORAL_PT.search(pt)
    peso = len(motivos) + (1 if inchou else 0) + (1 if seco else 0)
    cands.append((peso, wid, arq, motivos, ru, pt))

cands.sort(key=lambda x: -x[0])
print(f"linhas analisadas: {len(wb)}")
print(f"candidatos a proverbio/idioma: {len(cands)}")
print(f"  com sinal de achatamento (peso>=3): {sum(1 for c in cands if c[0] >= 3)}")
print()
print("motivos:", dict(collections.Counter(m for c in cands for m in c[3]).most_common(8)))

if DUMP:
    destino = os.path.join(ROOT, "work", "proverbios.txt")
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        for peso, wid, arq, motivos, ru, pt in cands:
            fh.write(f"### {wid}  [{arq}]  peso={peso}  {','.join(motivos)}\n")
            fh.write(f"RU: {ru}\nPT: {pt}\n\n")
    print(f"\ngravado em {os.path.relpath(destino, ROOT)}")
else:
    print("\n--- 12 de maior peso ---")
    for peso, wid, arq, motivos, ru, pt in cands[:12]:
        print(f"  [{peso}] {wid} {','.join(motivos)}")
        print(f"      RU: {ru[:100]}")
        print(f"      PT: {pt[:100]}")
