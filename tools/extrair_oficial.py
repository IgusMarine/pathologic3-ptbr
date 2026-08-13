"""Extrai a localizacao pt-BR OFICIAL que sobrou nos arquivos do jogo.

O arquivo «..._Portuguese_Br» que os desenvolvedores enviaram tem 61.242
entradas, mas so' ~1.800 estao em portugues: a localizacao oficial comecou,
cobriu uma fracao e parou. O resto ficou em ingles ou russo.

Serve como REFERENCIA de terminologia, nao como fonte a copiar: a versao
oficial traduziu a partir do ingles, e herdou os erros dele (por exemplo
«Почка» = rim virou "Baco", seguindo o "Spleen" ingles).

Gera:
  work/oficial_ptbr.tsv    id, cena, russo, oficial, nossa
  work/oficial_diff.tsv    so' as linhas onde discordamos

Uso: python extrair_oficial.py
"""
import json, os, re, glob, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIR = re.compile(r"[А-Яа-яЁё]")
ACC = re.compile(r"[ãõçáéíóúâêôàÃÕÇÁÉÍÓÚÂÊÔÀ]")
FUNC = re.compile(r"\b(não|você|senhor|está|então|também|nós|para|com|uma|que|dos|das|pelo|isso)\b", re.I)

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
nossa = {}
for p in glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv")):
    if os.path.basename(p) == "reviews.tsv":
        continue
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.strip():
            w, _, t = ln.partition("\t")
            nossa[w.strip()] = t


def e_portugues(s):
    """Heuristica: acento tipico do pt, ou duas palavras funcionais."""
    if not s or CIR.search(s):
        return False
    return bool(ACC.search(s)) or len(FUNC.findall(s)) >= 2


linhas, difs = [], []
for e in wb:
    of = (e.get("pt") or "").strip()
    if not e_portugues(of):
        continue
    nos = nossa.get(e["id"], "").strip()
    ru = (e.get("ru") or "").strip()
    linhas.append((e["id"], e["text"].replace("_Portuguese_Br", ""), ru, of, nos))
    if nos:
        r = difflib.SequenceMatcher(None, of.lower(), nos.lower()).ratio()
        if r < 0.75:
            difs.append((round(r, 2), e["id"], e["text"].replace("_Portuguese_Br", ""), ru, of, nos))

os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
with open(os.path.join(ROOT, "work", "oficial_ptbr.tsv"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("id\tcena\trusso\toficial\tnossa\n")
    for it in linhas:
        fh.write("\t".join(x.replace("\t", " ") for x in it) + "\n")

difs.sort()
with open(os.path.join(ROOT, "work", "oficial_diff.tsv"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write("similaridade\tid\tcena\trusso\toficial\tnossa\n")
    for r, *it in difs:
        fh.write(str(r) + "\t" + "\t".join(x.replace("\t", " ") for x in it) + "\n")

print(f"linhas em portugues oficial: {len(linhas)}")
print(f"  destas, com traducao nossa: {sum(1 for x in linhas if x[4])}")
print(f"  onde discordamos bastante : {len(difs)}")
print()
print("gravado: work/oficial_ptbr.tsv  e  work/oficial_diff.tsv")
