"""Apply translated TSV batches to the workbook and rebuild final TextAssets.

Reads translated/pt/*.tsv (id TAB pt, \\n escaped as literal backslash-n),
joins with extracted/workbook.json, reconstructs each TextAsset's text,
and writes:
  - translated/ptbr_final.json : { path_id: {"name": ..., "text": ...} }
  - translated/progress.json   : stats

Usage: python apply_pt.py
"""
import json, os, glob, re, collections, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "extracted")
TRANS = os.path.join(ROOT, "translated", "pt")

wb = json.load(open(os.path.join(OUT, "workbook.json"), encoding="utf-8"))

# load translations
tr = {}  # id -> pt
for f in sorted(glob.glob(os.path.join(TRANS, "*.tsv"))):
    for line in open(f, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        wid = parts[0].strip()
        pt = parts[1] if len(parts) > 1 else ""
        if wid in tr:
            print(f"WARN: duplicate id {wid} ({f})")
        tr[wid] = pt

print(f"translations loaded: {len(tr)}")

# sanity checks
missing = [e for e in wb if e["status"] == "todo" and e["id"] not in tr]
print(f"todo entries still untranslated: {len(missing)}")
unused = [wid for wid in tr if wid not in {e['id'] for e in wb}]
if unused:
    print(f"WARN: {len(unused)} translation ids not in workbook: {unused[:5]}")

tag_re = re.compile(r"<[^>]+>")
bad_tags = []
for e in wb:
    if e["id"] in tr:
        pt = tr[e["id"]]
        en_tags = set(tag_re.findall(e["en"] or ""))
        pt_tags = set(tag_re.findall(pt))
        if not pt_tags.issubset(en_tags):
            bad_tags.append((e["id"], en_tags, pt_tags))
if bad_tags:
    print(f"WARN: {len(bad_tags)} entries with tags not present in source:")
    for wid, en, pt in bad_tags[:10]:
        print(f"   {wid}: en={en} pt={pt}")

# rebuild per-TextAsset
# Agrupa por PATH_ID, nunca por nome de asset. O jogo tem 453 arquivos
# diferentes, em pastas diferentes, que compartilham o nome do arquivo (ha'
# dois Labels, dois Day1_Q0_Interrogation, etc.). Agrupar por nome fundia
# assets distintos num so' e mandava tudo para um path_id, deixando o outro
# intocado — foi exatamente assim que 453 assets ficaram sem traducao.
by_pid = collections.defaultdict(list)
for e in wb:
    by_pid[e["id"].split(".")[0]].append(e)

final = {}
done = 0
for pid, entries in by_pid.items():
    name = entries[0]["text"]
    lines = []
    for e in sorted(entries, key=lambda x: int(x["id"].split(".")[1])):
        pt = tr.get(e["id"])
        if pt is None:
            # fall back to existing PT, then EN text (avoids leaking "{key}" literals
            # when the PT line has a key with empty payload), then empty
            pt = e.get("pt", "") or ""
            if not pt.strip() and (e.get("en") or "").strip():
                pt = e["en"]
        # NAO expandir \n e \t aqui. No formato do jogo, a quebra de linha
        # REAL separa um registro do proximo ({Chave} valor), e a quebra de
        # paragrafo DENTRO de um valor fica como o escape literal de dois
        # caracteres. Expandir transformava conteudo em estrutura: o parser
        # via limites de registro onde era so' paragrafo. Foi isso que
        # apagou a legenda da cutscene de abertura — o SRT inteiro e' um
        # valor so', e virava 100 registros orfaos.
        if e["key"]:
            lines.append("{" + e["key"] + "} " + pt)
        else:
            lines.append(pt)
    # Separador CRLF e um separador final tambem, como os assets originais.
    # Verificado por round-trip: montar assim a partir do campo pt do
    # workbook reproduz 8471 dos 8892 assets originais byte a byte (os 421
    # restantes diferem so' no caminho da chave, artefato de extracao
    # anterior e alheio a isto).
    text = "\r\n".join(lines) + "\r\n"
    final[pid] = {"name": name, "text": text}
    done += len(entries)

with open(os.path.join(ROOT, "translated", "ptbr_final.json"), "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=0)

stats = {
    "total_strings": len(wb),
    "translated_strings": len(tr),
    "textassets_rebuilt": len(final),
    "untranslated_todo": len(missing),
}
with open(os.path.join(ROOT, "translated", "progress.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=1, ensure_ascii=False)

print(json.dumps(stats, indent=1, ensure_ascii=False))
print("saved translated/ptbr_final.json")

# --- portao de qualidade -----------------------------------------------
# A traducao roda em lotes ao longo de dias, e a deriva de terminologia
# reaparece sempre que um lote novo perde o glossario de vista. Rodar aqui
# garante que nenhum build sai sem a checagem.
print()
rc = subprocess.call([sys.executable, os.path.join(ROOT, "tools", "qa_check.py")])
if rc != 0:
    print("\nqa_check apontou erro bloqueante — corrija antes de injetar no jogo.")
    print("  terminologia:  python tools/enforce_glossary.py --apply")
    sys.exit(rc)
