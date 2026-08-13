"""Classify each text by the LANGUAGE ACTUALLY SPOKEN in its content.

Checks the content characters: Cyrillic script ratio -> Russian; else -> English.
For PT-BR texts, also detect if content is really Portuguese (looks at common PT words).

Output: extracted/lang_stats.json + extracted/classification.json
"""
import json, os, re, collections

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extracted")

def script_stats(text):
    cyr = sum(1 for c in text if 'Ѐ' <= c <= 'ӿ')
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    return cyr, latin

def classify(text, n=4000):
    sample = text[:n]
    cyr, latin = script_stats(sample)
    if cyr > latin and cyr > 5:
        return "russian"
    if latin > 5:
        return "latin"
    return "empty_or_short"

PT_WORDS = ("o ", "a ", "os ", "as ", "de ", "do ", "da ", "dos ", "das ", "que ", "em ", "para ",
            "por ", "com ", "não ", "não ", "uma ", "um ", "você ", "isso ", "isso ", "eu ", "ele ")
def is_portuguese(text):
    low = (" " + text.lower() + " ")
    hits = sum(1 for w in PT_WORDS if (" " + w.strip() + " ") in low)
    return hits >= 3

en_recs = json.load(open(os.path.join(OUT, "texts_en.json"), encoding="utf-8"))
pt_recs = json.load(open(os.path.join(OUT, "texts_ptbr.json"), encoding="utf-8"))

en_by_name = {r["name"]: r for r in en_recs}
shared_recs = [r for r in en_recs if not r["name"].endswith("_English")]

# --- English texts: what language is really inside? ---
en_langs = collections.Counter()
russian_en = []
for r in en_recs:
    if r["name"].endswith("_English"):
        l = classify(r["text"])
        en_langs[l] += 1
        if l == "russian":
            russian_en.append(r)

# --- PT-BR texts: what language is really inside? ---
pt_langs = collections.Counter()
pt_real_pt = 0
pt_english = 0
pt_russian = 0
pt_missing = 0
pt_examples = collections.defaultdict(list)
for r in pt_recs:
    l = classify(r["text"])
    if l == "russian":
        pt_russian += 1
    elif l == "latin":
        if is_portuguese(r["text"]):
            pt_real_pt += 1
        else:
            pt_english += 1
    else:
        pt_missing += 1
    if len(pt_examples[l]) < 3:
        pt_examples[l].append(r["name"])

# --- shared: how many contain real translatable prose vs binary/XML? ---
shared_kinds = collections.Counter()
for r in shared_recs:
    txt = r["text"]
    if txt.startswith("<Data type="):
        shared_kinds["xml_definition"] += 1
    elif "\x00" in txt[:200] or txt.count("�") > 50:
        shared_kinds["binary"] += 1
    elif classify(txt) == "latin" and len(txt.split()) > 20:
        shared_kinds["english_prose"] += 1
    else:
        shared_kinds["other"] += 1

stats = {
    "en_texts_by_content": dict(en_langs),
    "en_texts_in_russian_count": len(russian_en),
    "en_russian_words_total": sum(r["words"] for r in russian_en),
    "ptbr_by_content": {
        "real_portuguese": pt_real_pt,
        "english_placeholder": pt_english,
        "russian": pt_russian,
        "empty_short": pt_missing,
    },
    "ptbr_examples": {k: v for k, v in pt_examples.items()},
    "shared_by_kind": dict(shared_kinds),
}
print(json.dumps(stats, indent=1, ensure_ascii=False))

with open(os.path.join(OUT, "lang_stats.json"), "w", encoding="utf-8") as f:
    json.dump(stats, f, indent=1, ensure_ascii=False)

# dump list of English texts that are actually Russian (they are the ORIGINAL source)
with open(os.path.join(OUT, "en_texts_actually_russian.json"), "w", encoding="utf-8") as f:
    json.dump([{"name": r["name"], "text": r["text"]} for r in russian_en], f, ensure_ascii=False)
print("saved en_texts_actually_russian.json with", len(russian_en), "entries")
