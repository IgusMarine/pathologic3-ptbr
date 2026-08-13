"""Analyze Pathologic 3 Unity assets: count object types per file, dump samples of text-bearing objects.

Usage:
  python analyze_assets.py <path_to_assets_file> [--samples N] [--dump-json PREFIX]
"""
import sys, os
import UnityPy

def analyze(path, samples=5, dump_prefix=None):
    env = UnityPy.load(path)
    counts = {}
    total = 0
    text_samples = []
    print(f"=== {os.path.basename(path)} ===")
    for obj in env.objects:
        total += 1
        t = obj.type.name
        counts[t] = counts.get(t, 0) + 1
        if t in ("TextAsset", "MonoBehaviour") and len(text_samples) < samples:
            try:
                data = obj.read()
                if t == "TextAsset":
                    script = data.m_Script
                    preview = script[:300]
                    if any(chr(b) >= ' ' for b in preview[:100]):
                        text_samples.append((t, obj.path_id, preview))
                else:
                    # MonoBehaviour: dump raw serialized bytes; look for readable text
                    raw = data.raw_data[:400]
                    text_samples.append((t, obj.path_id, raw))
            except Exception as e:
                text_samples.append((t, obj.path_id, f"<ERR {e}>"))
    for t, c in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")
    print(f"  TOTAL objects: {total}")
    if dump_prefix:
        os.makedirs(os.path.dirname(dump_prefix), exist_ok=True) if os.path.dirname(dump_prefix) else None
        with open(f"{dump_prefix}_{os.path.basename(path)}.txt", "w", encoding="utf-8") as f:
            for t, pid, sample in text_samples:
                f.write(f"--- {t} path_id={pid} ---\n")
                f.write(repr(sample) + "\n\n")
        print(f"  samples -> {dump_prefix}_{os.path.basename(path)}.txt")
    else:
        for t, pid, sample in text_samples:
            print(f"--- {t} path_id={pid} ---")
            print(repr(sample[:300]))
            print()

if __name__ == "__main__":
    path = sys.argv[1]
    samples = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    dump = sys.argv[3] if len(sys.argv) > 3 else None
    analyze(path, samples, dump)
