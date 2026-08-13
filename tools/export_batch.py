"""Export workbook entries as readable batch files for translation.

Input:  extracted/workbook.json
Output: work/batches/<group>_<n>.txt  (id TAB scene TAB ru TAB en)
And translated files go to: translated/pt/<batch>.tsv  (id TAB pt)

Usage: python export_batch.py <group> [start] [count]
"""
import json, os, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "extracted")
BATCH_DIR = os.path.join(ROOT, "work", "batches")
TRANS_DIR = os.path.join(ROOT, "translated", "pt")
os.makedirs(BATCH_DIR, exist_ok=True)
os.makedirs(TRANS_DIR, exist_ok=True)

wb = json.load(open(os.path.join(OUT, "workbook.json"), encoding="utf-8"))
group = sys.argv[1] if len(sys.argv) > 1 else "Prologue"
start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
count = int(sys.argv[3]) if len(sys.argv) > 3 else 900

# O campo "status" do workbook e' estatico — nunca foi reescrito depois que a
# traducao comecou, entao TODAS as linhas continuam "todo", inclusive as ja
# traduzidas. Filtrar so' por status reexportaria trabalho pronto e geraria
# traducoes divergentes para o mesmo id. A verdade sobre o que falta esta em
# translated/pt/.
ja_feito = set()
for _p in glob.glob(os.path.join(TRANS_DIR, "*.tsv")):
    if os.path.basename(_p) == "reviews.tsv":
        continue
    for _ln in open(_p, encoding="utf-8"):
        if _ln.strip():
            ja_feito.add(_ln.split("\t", 1)[0].strip())

entries = [e for e in wb if e["group"] == group and e["id"] not in ja_feito]

# Filtro opcional por prefixo de cena: permite atacar um bloco coerente
# (ex.: so' o Hospital, ou so' a interface) em vez da ordem alfabetica.
#   python export_batch.py Other 0 900 Hospital
prefixo = sys.argv[4] if len(sys.argv) > 4 else None
if prefixo:
    entries = [e for e in entries if e["text"].startswith(prefixo)]
    print(f"filtrando por cena começando com '{prefixo}': {len(entries)} linhas")
entries.sort(key=lambda e: (e["text"], int(e["id"].split(".")[0]), int(e["id"].split(".")[1])))
chunk = entries[start:start + count]

fname = f"{group}_{start//count:02d}.txt"
with open(os.path.join(BATCH_DIR, fname), "w", encoding="utf-8") as f:
    for e in chunk:
        ru = (e["ru"] or "").replace("\t", " ").replace("\n", "\\n")
        en = (e["en"] or "").replace("\t", " ").replace("\n", "\\n")
        # Quando ru E en estao vazios, a fonte real pode estar no campo "pt"
        # (o arquivo original do jogo, que as vezes traz russo, as vezes
        # ingles). Sem isso o modelo recebe uma linha VAZIA e inventa texto —
        # foi o que produziu 41 linhas de prosa inventada no bloco Hospital.
        if not ru and not en:
            fonte = (e.get("pt") or "").replace("\t", " ").replace("\n", "\\n")
            if fonte:
                ru = fonte
        f.write(f"{e['id']}\t{e['text']}\t{ru}\t{en}\n")
print(f"wrote {BATCH_DIR}/{fname} with {len(chunk)} entries")
print(f"remaining todo in {group}: {len(entries) - start - len(chunk)}")
