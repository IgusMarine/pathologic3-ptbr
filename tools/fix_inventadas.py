"""Esvazia linhas cuja ORIGEM esta vazia mas ganharam texto inventado.

Defeito mais grave da auditoria: quando o russo E o ingles estao vazios,
nao ha o que traduzir — a linha deve ficar vazia. Em 190 linhas o modelo
inventou conteudo, e num bloco de 35 linhas inventou uma cena inteira, com
narracao e dialogo citando Pasteur e Koch, figuras que nao existem no
universo do jogo.

Nao e' traducao ruim: e' texto que nao existe entrando no jogo.

Seguranca: so' esvazia quando RU e EN estao AMBOS vazios. Se qualquer um
dos dois tem conteudo, a linha e' traducao legitima e fica intacta.

Uso:
    python fix_inventadas.py            # dry-run
    python fix_inventadas.py --apply
"""
import json, os, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APLICAR = "--apply" in sys.argv

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
byid = {e["id"]: e for e in wb}

esvaziadas, por_arq = [], collections.Counter()
for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))):
    if os.path.basename(path) == "reviews.tsv":
        continue
    linhas = open(path, encoding="utf-8").read().split("\n")
    out, dirty = [], False
    for ln in linhas:
        wid, sep, pt = ln.partition("\t")
        if sep and pt.strip():
            e = byid.get(wid.strip())
            # so' e inventado quando NAO HA FONTE EM LUGAR NENHUM. O campo
            # "pt" do workbook guarda o arquivo original do jogo, e nele o
            # texto-fonte as vezes esta em russo — 264 linhas dependiam disso.
            sem_fonte = e is not None and (
                not (e.get("ru") or "").strip()
                and not (e.get("en") or "").strip()
                and not (e.get("pt") or "").strip())
            if sem_fonte:
                esvaziadas.append((os.path.basename(path), wid.strip(), pt[:70]))
                por_arq[os.path.basename(path)] += 1
                ln = wid + sep
                dirty = True
        out.append(ln)
    if dirty and APLICAR:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print(f"linhas com texto inventado (origem vazia): {len(esvaziadas)}\n")
for arq, n in por_arq.most_common():
    print(f"   {n:>4}  {arq}")
print("\namostra do que sai:")
for arq, wid, t in esvaziadas[:8]:
    print(f"   {wid:<11} {t}")
print("\nGRAVADO." if APLICAR else "\n(dry-run — use --apply)")
