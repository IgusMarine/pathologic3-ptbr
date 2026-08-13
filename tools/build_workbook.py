"""Build the translation workbook: one entry per localized string.

For every TextAsset that exists in the pt-BR set, split its lines into
{key} text entries, then join with the Russian and English versions of the
same key. Output: extracted/workbook.json
  [ { "id": "5655.1", "text": "Day2_...", "key": "...40211", "scene": "...",
      "ru": "...", "en": "...", "pt": "...", "status": "todo"|"done" }, ... ]

Also splits workbook into per-group files (Prologue, Day1..Day12, Other) for
batched translation work.
"""
import json, os, re, collections

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extracted")

def parse_lines(text):
    """Parse '{key} content' lines, preserving empty lines as None."""
    out = []
    for line in text.split("\n"):
        line = line.strip("\r")
        m = re.match(r"^\{([^}]*)\}\s?(.*)$", line, re.S)
        if m:
            out.append({"key": m.group(1), "text": m.group(2)})
        else:
            out.append({"key": None, "text": line})
    return out

def load_texts(fname):
    recs = json.load(open(os.path.join(OUT, fname), encoding="utf-8"))
    by_name = {}
    for r in recs:
        if r["text"] or r["name"]:
            by_name.setdefault(r["name"], r)
    return by_name

en = load_texts("texts_en.json")
ru = load_texts("texts_ru.json")
pt = load_texts("texts_ptbr.json")

def strip_lang(name, lang):
    return name[: -len("_" + lang)]

def is_pt(t):
    if not t or not t.strip():
        return False
    if any('Ѐ' <= c <= 'ӿ' for c in t):
        return False
    # latin-only content: is it Portuguese-ish? count common words
    low = (" " + t.lower() + " ")
    words = ("de ", "que ", "em ", "o ", "a ", "para ", "com ", "não ", "não", "por ", "um ", "uma ", "você ", "isso ", "muito ", "bem ", "ser ", "foi ", "tudo ", "mas ")
    hits = sum(1 for w in words if (" " + w.strip() + " ") in low)
    return hits >= 2

workbook = []
for name, ptrec in pt.items():
    base = strip_lang(name, "Portuguese_Br")
    enrec = en.get(base + "_English")
    rurec = ru.get(base + "_Russian")
    ptlines = parse_lines(ptrec["text"])
    enlines = parse_lines(enrec["text"]) if enrec else []
    rulines = parse_lines(rurec["text"]) if rurec else []
    def by_key(lines):
        d = {}
        for l in lines:
            if l["key"]:
                d.setdefault(l["key"], l["text"])
        return d
    enk, ruk = by_key(enlines), by_key(rulines)
    for i, pl in enumerate(ptlines):
        if pl["key"] is None:
            # line without key: only translate if it carries prose
            if not pl["text"].strip():
                continue
        wid = f"{ptrec['path_id']}.{i}"
        entry = {
            "id": wid,
            "text": name,
            "key": pl["key"],
            "en": enk.get(pl["key"]) if pl["key"] else None,
            "ru": ruk.get(pl["key"]) if pl["key"] else None,
            "pt": pl["text"],
            "status": "review" if pl["text"] and is_pt(pl["text"]) else "todo",
        }
        workbook.append(entry)

# group by narrative block for batching
def group_of(text_name):
    for g in ("Prologue", "Epilogue"):
        if text_name.startswith(g):
            return g
    m = re.match(r"Day(\d+)", text_name)
    if m:
        return f"Day{int(m.group(1)):02d}"
    return "Other"

for e in workbook:
    e["group"] = group_of(e["text"])

with open(os.path.join(OUT, "workbook.json"), "w", encoding="utf-8") as f:
    json.dump(workbook, f, ensure_ascii=False, indent=0)

# per-group slices + stats
stats = collections.Counter()
todo_by_group = collections.Counter()
for e in workbook:
    stats[e["status"]] += 1
    if e["status"] != "done":
        todo_by_group[e["group"]] += 1
print("TOTAL:", len(workbook), dict(stats))
print("TODO por grupo:", dict(sorted(todo_by_group.items())))
print("saved extracted/workbook.json")
