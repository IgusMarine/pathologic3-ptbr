"""Extract the full text corpus from Pathologic 3 resources.assets.

Produces extracted/texts_en.json and extracted/texts_ptbr.json:
  [ { "path_id": 5655, "name": "Day2_...", "lang": "Portuguese_Br", "text": "...", "words": N }, ... ]

Also writes extracted/corpus_stats.json with volume metrics:
  - per-language counts
  - placeholder check: how many PT-BR texts are byte-identical to EN
  - EN word counts (per-text and total)
  - texts without language suffix (shared corpus)
"""
import sys, os, json, collections, re
import UnityPy

DATA_DIR = sys.argv[1] if len(sys.argv) > 1 else r"C:\Program Files (x86)\Steam\steamapps\common\Pathologic 3\Pathologic3_Data"
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extracted")
os.makedirs(OUT_DIR, exist_ok=True)

LANGS = ("English", "Russian", "Portuguese_Br", "Italian", "German", "Chinese_Simplified",
         "Spanish", "French", "Japanese", "Korean", "Polish", "Turkish", "Ukrainian")

def clean(s):
    """Replace lone surrogates (bad decodes) so JSON utf-8 export works."""
    return re.sub(r"[\ud800-\udfff]", "�", s)

def lang_of(name):
    for lang in LANGS:
        if name.endswith("_" + lang):
            return lang
    return None

env = UnityPy.load(os.path.join(DATA_DIR, "resources.assets"))

by_lang = collections.defaultdict(list)
shared = []          # no language suffix
placeholder_ptbr = 0
en_by_key = {}

print("reading objects...", flush=True)
seen = set()
for obj in env.objects:
    if obj.type.name != "TextAsset" or obj.path_id in seen:
        continue
    seen.add(obj.path_id)
    try:
        d = obj.read()
        name = (getattr(d, "m_Name", "") or "").strip()
        txt = d.m_Script or ""
    except Exception:
        continue
    if not name:
        continue
    txt = clean(txt.lstrip("\ufeff"))  # BOM + sanitize surrogates
    lang = lang_of(name)
    rec = {"path_id": obj.path_id, "name": name, "text": txt, "words": len(txt.split())}
    if lang:
        by_lang[lang].append(rec)
        if lang == "English":
            # key = text up to first '}' of the localization key, or the name
            en_by_key[obj.path_id] = txt
    else:
        shared.append(rec)

print("computing stats...", flush=True)
stats = {"per_lang": {k: len(v) for k, v in by_lang.items()},
         "shared_no_lang": len(shared),
         "total_unique": len(seen)}

# placeholder check: PT-BR texts that equal EN texts with same name-base
en_by_base = {}
for rec in by_lang.get("English", []):
    base = rec["name"][:-len("_English")]
    en_by_base[base] = rec["text"]
ident = 0
diff = 0
for rec in by_lang.get("Portuguese_Br", []):
    base = rec["name"][:-len("_Portuguese_Br")]
    en = en_by_base.get(base)
    if en is not None and en == rec["text"]:
        ident += 1
    else:
        diff += 1
stats["ptbr_identical_to_en"] = ident
stats["ptbr_different_from_en"] = diff

en_words = sum(r["words"] for r in by_lang.get("English", []))
shared_words = sum(r["words"] for r in shared)
stats["en_words_total"] = en_words
stats["shared_words_total"] = shared_words

print("writing...", flush=True)
with open(os.path.join(OUT_DIR, "texts_en.json"), "w", encoding="utf-8") as f:
    json.dump(by_lang.get("English", []) + shared, f, ensure_ascii=False)
with open(os.path.join(OUT_DIR, "texts_ru.json"), "w", encoding="utf-8") as f:
    json.dump(by_lang.get("Russian", []), f, ensure_ascii=False)
with open(os.path.join(OUT_DIR, "texts_ptbr.json"), "w", encoding="utf-8") as f:
    json.dump(by_lang.get("Portuguese_Br", []), f, ensure_ascii=False)
with open(os.path.join(OUT_DIR, "corpus_stats.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=1, ensure_ascii=False)

print(json.dumps(stats, indent=1, ensure_ascii=False))
print("DONE")
