"""Gera dumps RU/EN/PT de um bloco, fatiados para revisao humana ou por agente.

Uso:
    python dump_revisao.py Hosp          # todos os translated/pt/Hosp*.tsv
    python dump_revisao.py Hosp 120      # 120 falas por arquivo de revisao

Escreve em work/revisao/<prefixo>_NN.txt. So' entram linhas com texto de
verdade (>=40 caracteres): rotulo de UI e interjeicao curta nao rendem
revisao literaria e so' diluiriam a leitura.
"""
import json, os, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "revisao")

prefixo = sys.argv[1] if len(sys.argv) > 1 else "Hosp"
por_arquivo = int(sys.argv[2]) if len(sys.argv) > 2 else 120

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
byid = {e["id"]: e for e in wb}

falas = []
for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", prefixo + "*.tsv"))):
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip():
            continue
        wid, _, pt = ln.partition("\t")
        wid = wid.strip()
        e = byid.get(wid)
        if not e or len(pt.strip()) < 40:
            continue
        falas.append((wid, e["text"].replace("_Portuguese_Br", ""),
                      e.get("ru") or "", e.get("en") or "", pt))

os.makedirs(OUT, exist_ok=True)
for velho in glob.glob(os.path.join(OUT, prefixo + "_*.txt")):
    os.remove(velho)

n = 0
for i in range(0, len(falas), por_arquivo):
    bloco = falas[i:i + por_arquivo]
    destino = os.path.join(OUT, f"{prefixo}_{i // por_arquivo:02d}.txt")
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        for wid, cena, ru, en, pt in bloco:
            fh.write(f"### {wid}  [{cena}]\nRU: {ru}\nEN: {en}\nPT: {pt}\n\n")
    n += 1

print(f"falas com texto: {len(falas)}")
print(f"arquivos de revisao: {n}  (em work/revisao/)")
