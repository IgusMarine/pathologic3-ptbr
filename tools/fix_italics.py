"""Restaura o <i>...</i> perdido na traducao.

Dois regimes, porque o risco e' diferente:

  AUTO   — o EN envolve a string INTEIRA (^<i>tudo</i>$). Envolver a PT
           inteira e' equivalente e nao exige alinhamento. Aplicado direto.

  FILA   — enfase interna (quase sempre 1 palavra). Aqui a colocacao e'
           decisao de tradutor: italico na palavra errada muda o sentido
           da fala e soa pior que italico nenhum. Exportado para
           work/italicos_pendentes.tsv para revisao humana, e reimportado
           de work/italicos_revisados.tsv.

Uso:
    python fix_italics.py            # dry-run + gera a fila
    python fix_italics.py --apply    # aplica AUTO + o que estiver revisado
"""
import json, os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS = os.path.join(ROOT, "translated", "pt")
WORK = os.path.join(ROOT, "work")
QUEUE = os.path.join(WORK, "italicos_pendentes.tsv")
REVIEWED = os.path.join(WORK, "italicos_revisados.tsv")
APPLY = "--apply" in sys.argv

TAG = re.compile(r"</?[a-zA-Z][^>]*>")
WHOLE = re.compile(r"^\s*<i>(?P<inner>.*)</i>\s*$", re.S)


def load_reviewed():
    """id -> PT ja corrigida a mao. Valida que so mudou marcacao."""
    out = {}
    if not os.path.exists(REVIEWED):
        return out
    for ln in open(REVIEWED, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.startswith("#"):
            continue
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        out[parts[0].strip()] = parts[1]
    return out


def main():
    wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
    byid = {e["id"]: e for e in wb}
    reviewed = load_reviewed()

    auto, queue, applied_rev = [], [], []
    files = {}

    for path in sorted(glob.glob(os.path.join(TRANS, "*.tsv"))):
        if os.path.basename(path) == "reviews.tsv":
            continue
        out, dirty = [], False
        for ln in open(path, encoding="utf-8"):
            raw = ln.rstrip("\n")
            if not raw.strip():
                out.append(raw)
                continue
            wid, _, pt = raw.partition("\t")
            wid = wid.strip()
            e = byid.get(wid)
            new = pt
            if e:
                en = e["en"] or ""
                if TAG.findall(en) and not TAG.findall(pt) and pt.strip():
                    if wid in reviewed:
                        new = reviewed[wid]
                        # a revisao so pode acrescentar marcacao, nao reescrever texto
                        if TAG.sub("", new).strip() != pt.strip():
                            print(f"  ! {wid}: revisao alterou o TEXTO, nao so a marcacao — ignorada")
                            new = pt
                        else:
                            applied_rev.append((wid, new))
                    else:
                        m = WHOLE.match(en)
                        if m and "<i>" not in m.group("inner"):
                            new = "<i>" + pt.strip() + "</i>"
                            auto.append((os.path.basename(path), wid, en[:60], new[:60]))
                        else:
                            queue.append((wid, os.path.basename(path), en, pt))
            if new != pt:
                dirty = True
            out.append(wid + "\t" + new if e or pt else raw)
        files[path] = (out, dirty)

    print(f"AUTO  (wrap integral)      : {len(auto)}")
    print(f"REVISADAS aplicadas        : {len(applied_rev)}")
    print(f"FILA  (enfase interna)     : {len(queue)}")

    os.makedirs(WORK, exist_ok=True)
    with open(QUEUE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# id\tarquivo\tEN (com <i>)\tPT (sem marcacao)\n")
        fh.write("# Copie para italicos_revisados.tsv como:  id<TAB>PT com <i> no lugar certo\n")
        for wid, f, en, pt in queue:
            fh.write(f"{wid}\t{f}\t{en}\t{pt}\n")
    print(f"\nfila gravada em {os.path.relpath(QUEUE, ROOT)}")

    if APPLY:
        n = 0
        for path, (out, dirty) in files.items():
            if dirty:
                open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
                n += 1
        print(f"GRAVADO em {n} arquivo(s).")
    else:
        for f, wid, en, new in auto[:5]:
            print(f"  {f} {wid}\n    EN: {en}\n    PT: {new}")
        print("\n(dry-run — nada gravado. use --apply)")


if __name__ == "__main__":
    main()
