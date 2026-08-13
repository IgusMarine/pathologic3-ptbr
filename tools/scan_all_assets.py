"""Scan all Unity asset files in Pathologic 3 for text-bearing objects.

For each file: count TextAssets (with size), MonoBehaviour (with raw_data size).
Dump samples of TextAsset content to extracted/samples/<file>.txt.

Usage: python scan_all_assets.py <game_data_dir> [--limit N]
"""
import sys, os, json
import UnityPy

GAME_DATA = sys.argv[1]
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 0

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extracted", "scan_report.json")
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extracted", "samples")
os.makedirs(SAMPLE_DIR, exist_ok=True)

files = sorted(f for f in os.listdir(GAME_DATA)
               if f.endswith(".assets") or f.startswith("level") or f in ("globalgamemanagers",))
if LIMIT:
    files = files[:LIMIT]

report = {}
for fname in files:
    path = os.path.join(GAME_DATA, fname)
    try:
        env = UnityPy.load(path)
    except Exception as e:
        report[fname] = {"error": str(e)}
        print(f"{fname}: ERROR {e}", flush=True)
        continue
    counts = {}
    textassets = []
    big_monos = 0
    for obj in env.objects:
        t = obj.type.name
        counts[t] = counts.get(t, 0) + 1
        if t == "TextAsset":
            try:
                data = obj.read()
                size = len(data.m_Script) if data.m_Script else 0
                textassets.append((obj.path_id, size))
                if size > 200:
                    with open(os.path.join(SAMPLE_DIR, f"{fname}__{obj.path_id}.txt"), "w", encoding="utf-8", errors="replace") as f:
                        f.write(data.m_Script.decode("utf-8", errors="replace")[:2000])
            except Exception as e:
                textassets.append((obj.path_id, -1))
        elif t == "MonoBehaviour":
            try:
                data = obj.read()
                raw = data.raw_data
                if raw and len(raw) > 4000:
                    big_monos += 1
            except Exception:
                pass
    report[fname] = {
        "types": counts,
        "textassets": textassets[:50],
        "textasset_count": len(textassets),
        "big_monos": big_monos,
    }
    print(f"{fname}: TextAssets={len(textassets)} bigMonos={big_monos}", flush=True)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=1, ensure_ascii=False)
print(f"\nreport -> {OUT}")
