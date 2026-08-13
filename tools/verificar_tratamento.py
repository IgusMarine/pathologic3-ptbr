"""Verifica achados de tratamento (o senhor / voce) contra o russo.

O russo distingue «вы» (formal) de «ты» (intimo). Esse e' o criterio
objetivo — nao opiniao. Mas ele NAO decide sozinho, por dois motivos que
ja produziram falso positivo nesta revisao:

  1. pt-BR usa "o senhor" com pai, mae e idoso onde o russo usa «ты».
     Filho falando com pai: «ты» no russo, "o senhor" em portugues, CERTO.
  2. Assimetria e' legitima: o paciente trata o medico por "o senhor" e
     ele o trata por "voce", mesmo o russo usando «вы» nos dois sentidos.

Entao aqui so' se procura UMA coisa: o MESMO falante oscilando dentro da
MESMA cena. Para isso, agrupa por cena e compara as linhas que tem a mesma
direcao de fala (aproximada pela forma verbal e pelo vocativo).

Uso: python verificar_tratamento.py work/ids_tratamento.txt
"""
import json, os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VY = re.compile(r"\b(вы|вас|вам|вами|ваш\w*)\b", re.I)
TY = re.compile(r"\b(ты|тебя|тебе|тобой|тво\w+)\b", re.I)
VY_VERBO = re.compile(r"\b\w+(?:ете|ите|йте)\b")
SENHOR = re.compile(r"\bo senhor\b|\ba senhora\b|\blhe\b", re.I)
VOCE = re.compile(r"\bvocê\b", re.I)

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

alvos = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]

# agrupa TODAS as linhas por cena, nao so' as apontadas: para julgar
# oscilacao e' preciso ver a cena inteira
cenas = collections.defaultdict(list)
for wid, (pt, arq) in tr.items():
    e = byid.get(wid)
    if not e:
        continue
    cenas[e["text"]].append((wid, pt, e.get("ru") or ""))

suspeitas, descartados = [], []
for wid in alvos:
    e = byid.get(wid)
    if not e or wid not in tr:
        descartados.append((wid, "id sem traducao"))
        continue
    pt, arq = tr[wid]
    ru = e.get("ru") or ""
    formal_ru = bool(VY.search(ru) or VY_VERBO.search(ru))
    intimo_ru = bool(TY.search(ru))
    pt_senhor = bool(SENHOR.search(pt))
    pt_voce = bool(VOCE.search(pt))

    if not (pt_senhor or pt_voce):
        descartados.append((wid, "linha sem tratamento marcado"))
        continue
    # russo intimo + pt formal: quase sempre e' pai/mae/idoso — legitimo
    if intimo_ru and not formal_ru and pt_senhor:
        descartados.append((wid, "«ты» + «o senhor»: deferencia por idade/parentesco, normal em pt-BR"))
        continue
    # a cena inteira usa a mesma forma? entao nao ha oscilacao
    irmas = cenas.get(e["text"], [])
    n_s = sum(1 for _, p2, _ in irmas if SENHOR.search(p2))
    n_v = sum(1 for _, p2, _ in irmas if VOCE.search(p2))
    if n_s == 0 or n_v == 0:
        descartados.append((wid, f"cena uniforme ({n_s} senhor / {n_v} voce)"))
        continue
    suspeitas.append((wid, arq, e["text"], n_s, n_v, pt[:90]))

print(f"apontados: {len(alvos)}")
print(f"descartados pelo criterio objetivo: {len(descartados)}")
print(f"restam para leitura humana: {len(suspeitas)}\n")

motivos = collections.Counter(m for _, m in descartados)
for m, n in motivos.most_common():
    print(f"   {n:>3}  {m}")

print("\n--- suspeitas (cena mista) ---")
for wid, arq, cena, n_s, n_v, amostra in suspeitas:
    print(f"  {wid:<11} {arq:<16} {cena.replace('_Portuguese_Br','')[:34]:<36} "
          f"senhor={n_s} voce={n_v}")
    print(f"      {amostra}")
