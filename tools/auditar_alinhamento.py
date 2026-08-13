"""Procura traducao presa ao id ERRADO (desalinhamento).

Sintoma real encontrado em Day08_01a/b: a partir de certa linha, o texto
portugues passa a pertencer a outro trecho da conversa. No jogo isso faz
o personagem dizer a fala de outro momento.

Metodo: usa ancoras que precisam aparecer IGUAIS nos tres idiomas.

  1. Latim — «Voluntas est superior intellectu» e' identico em RU, EN e PT.
     Se a origem e' latim e a traducao nao repete esse latim, ha suspeita.
  2. Numeros — se a origem tem "27" e a traducao nao tem nenhum numero,
     idem.

Nenhuma ancora sozinha prova; por isso o script agrupa por ARQUIVO e por
faixa de id: desalinhamento e' contiguo, entao varias suspeitas seguidas
no mesmo bloco e' o sinal forte.

Uso: python auditar_alinhamento.py
"""
import json, os, re, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

CIR = re.compile(r"[А-Яа-яЁё]")
LAT_PAL = re.compile(r"\b[a-zA-Z]{3,}\b")
NUM = re.compile(r"\d+")

suspeitas = []
for wid, (pt, arq) in tr.items():
    e = byid.get(wid)
    if not e:
        continue
    ru = (e.get("ru") or "").strip()
    if not ru or not pt.strip():
        continue

    # ancora 1: origem em latim (sem cirilico, com palavras latinas)
    sem_tag = re.sub(r"</?i>", "", ru).strip()
    if not CIR.search(sem_tag) and len(LAT_PAL.findall(sem_tag)) >= 2:
        palavras = set(w.lower() for w in LAT_PAL.findall(sem_tag))
        pt_pal = set(w.lower() for w in LAT_PAL.findall(pt))
        if palavras and len(palavras & pt_pal) < max(1, len(palavras) // 2):
            suspeitas.append((arq, wid, "latim nao repetido", sem_tag[:60], pt[:60]))
            continue

    # ancora 2: numeros na origem que sumiram na traducao
    n_ru = set(NUM.findall(ru))
    if n_ru and not NUM.search(pt) and len(ru) > 25:
        suspeitas.append((arq, wid, "numero sumiu", ru[:60], pt[:60]))

print(f"linhas suspeitas: {len(suspeitas)}\n")

# desalinhamento e' CONTIGUO: agrupa por arquivo e conta
por_arq = collections.Counter(s[0] for s in suspeitas)
print("por arquivo (3+ suspeitas = provavel desalinhamento de bloco):")
for arq, n in por_arq.most_common(20):
    marca = "  <<< INVESTIGAR" if n >= 3 else ""
    print(f"   {n:>3}  {arq}{marca}")

print("\nprimeiras suspeitas:")
for arq, wid, motivo, orig, pt in suspeitas[:15]:
    print(f"  {arq} {wid} [{motivo}]")
    print(f"      origem: {orig}")
    print(f"      pt    : {pt}")
