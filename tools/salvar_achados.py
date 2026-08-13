"""Extrai os achados brutos do journal de um workflow de revisao.

A revisao roda em duas fases: buscar e verificar. Se a verificacao morre no
meio (limite de sessao, por exemplo), os achados da busca ficam so' no
journal. Este script os recupera para work/achados_brutos.json, para a
verificacao poder ser retomada depois sem refazer a busca.

Uso: python salvar_achados.py <caminho_do_journal.jsonl>
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "work", "achados_brutos.json")

if len(sys.argv) < 2:
    print("uso: python salvar_achados.py <journal.jsonl>")
    sys.exit(2)

achados, resultados = [], 0
for ln in open(sys.argv[1], encoding="utf-8"):
    try:
        d = json.loads(ln)
    except Exception:
        continue
    if d.get("type") != "result":
        continue
    resultados += 1
    v = d.get("result")
    if isinstance(v, dict) and isinstance(v.get("achados"), list):
        achados.extend(v["achados"])

# dedup por id + trecho: lentes diferentes acham a mesma coisa
vistos, unicos = set(), []
for a in achados:
    if not isinstance(a, dict):
        continue
    chave = str(a.get("id")) + "|" + str(a.get("pt_atual", ""))[:40]
    if chave in vistos:
        continue
    vistos.add(chave)
    unicos.append(a)

json.dump(unicos, open(DEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(f"registros de resultado: {resultados}")
print(f"achados brutos: {len(achados)} | unicos: {len(unicos)}")
print(f"gravado em {os.path.relpath(DEST, ROOT)}")
print()
print("por gravidade:", dict(collections.Counter(a.get("gravidade", "?") for a in unicos)))
print("por categoria:")
for k, c in collections.Counter(a.get("categoria", "?") for a in unicos).most_common(10):
    print(f"   {c:>4}  {k}")
