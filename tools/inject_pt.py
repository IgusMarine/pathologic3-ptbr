"""Inject translated PT-BR texts back into resources.assets.

Reads translated/ptbr_final.json ({path_id: {name, text}}) and overwrites
the m_Script of matching TextAssets (names ending in _Portuguese_Br).

Safety: creates resources.assets.bak on first run. Run from an elevated
shell if the game dir is write-protected.

Usage: python inject_pt.py [--restore]
"""
import sys, os, shutil, json
import UnityPy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Pathologic 3\Pathologic3_Data"
ASSET = os.path.join(GAME, "resources.assets")
BACKUP = ASSET + ".bak"
FINAL = os.path.join(ROOT, "translated", "ptbr_final.json")

if "--restore" in sys.argv:
    if os.path.exists(BACKUP):
        shutil.copy2(BACKUP, ASSET)
        print("restored resources.assets from backup")
    else:
        print("no backup found")
    sys.exit(0)

if not os.path.exists(BACKUP):
    print(f"backing up -> {BACKUP}")
    shutil.copy2(ASSET, BACKUP)
else:
    print("backup already exists, skipping")

final = json.load(open(FINAL, encoding="utf-8"))
by_pid = {int(pid): rec for pid, rec in final.items()}

print("loading assets...")
env = UnityPy.load(ASSET)
changed = 0
missing = 0
for obj in env.objects:
    if obj.type.name != "TextAsset":
        continue
    pid = obj.path_id
    rec = by_pid.get(pid)
    if not rec:
        continue
    try:
        data = obj.read()
        name = (getattr(data, "m_Name", "") or "")
        if not name.endswith("_Portuguese_Br"):
            missing += 1
            continue
        data.m_Script = "\ufeff" + rec["text"]  # restore BOM like originals
        data.save()
        changed += 1
    except Exception as e:
        print(f"  ERR pid={pid}: {e}")

print(f"changed TextAssets: {changed}, skipped (name mismatch): {missing}")
print("saving assets (this rewrites the 784MB file, may take a while)...")
out_dir = os.path.join(ROOT, "patched")
os.makedirs(out_dir, exist_ok=True)
env.save(out_path=out_dir)
patched = os.path.join(out_dir, "resources.assets")
shutil.copy2(patched, ASSET)
print(f"copied patched file over original ({patched})")
print("DONE. If the game breaks, run: python inject_pt.py --restore")
