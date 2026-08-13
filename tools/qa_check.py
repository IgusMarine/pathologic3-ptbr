"""Portao de qualidade. Roda antes de compilar; falha o build se a deriva voltar.

Verifica:
  1. deriva de terminologia contra research/glossario.lock.tsv
  2. marcacao <i> perdida em relacao ao original
  3. \\n / \\t divergentes (quebra o layout das caixas de dialogo)
  4. ids duplicados com traducoes DIFERENTES
  5. quanto do jogo cai em ingles/russo se compilar agora

Uso:
    python qa_check.py            # relatorio
    python qa_check.py --strict   # sai com codigo 1 se houver erro bloqueante
"""
import json, os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(ROOT, "research", "glossario.lock.tsv")
STRICT = "--strict" in sys.argv

# «Бакалавр» -> "Bacharel em Medicina" nestes dois documentos e' correto:
# e' o grau academico num papel timbrado, nao o titulo-persona.
ISENTOS = {"57700.1", "8827.61"}

TAG = re.compile(r"</?[a-zA-Z][^>]*>")
CYR = re.compile(r"[А-Яа-яЁё]")


def load_rows():
    wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
    byid = {e["id"]: e for e in wb}
    rows, seen = [], collections.defaultdict(list)
    for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))):
        if os.path.basename(path) == "reviews.tsv":
            continue
        for ln in open(path, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if not ln.strip():
                continue
            wid, _, pt = ln.partition("\t")
            wid = wid.strip()
            rows.append((wid, pt, os.path.basename(path)))
            seen[wid].append(pt)
    return wb, byid, rows, seen


def load_lock():
    rules = []
    for ln in open(LOCK, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        p = ln.split("\t")
        if p[0] == "canonico":
            continue
        while len(p) < 5:
            p.append("")
        if not p[3].strip():
            continue
        rules.append({
            "canon": p[0], "ru": re.compile(p[2].strip()),
            "variants": [v.split(":")[0].strip() for v in p[3].split(";") if v.strip()],
        })
    return rules


def main():
    wb, byid, rows, seen = load_rows()
    rules = load_lock()
    erros, avisos = [], []

    # 1. deriva de terminologia
    drift = []
    for wid, pt, f in rows:
        if wid in ISENTOS:
            continue
        e = byid.get(wid)
        if not e:
            continue
        ru = e.get("ru") or ""
        for r in rules:
            if not r["ru"].search(ru):
                continue
            for v in r["variants"]:
                if re.search(r"(?<![\wÀ-ſ])" + re.escape(v) + r"\b", pt):
                    drift.append((f, wid, v, r["canon"]))
    if drift:
        erros.append(f"deriva de terminologia: {len(drift)} linha(s)")
        for f, wid, v, canon in drift[:10]:
            erros.append(f"    {f} {wid}: '{v}' deveria ser '{canon}'")

    # 2. marcacao perdida
    lost = [(f, wid) for wid, pt, f in rows
            if (e := byid.get(wid)) and TAG.findall(e.get("en") or "")
            and not TAG.findall(pt) and pt.strip()]
    if lost:
        avisos.append(f"marcacao <i> perdida: {len(lost)} linha(s) "
                      f"(ver work/italicos_pendentes.tsv)")

    # 3. \n e \t divergentes — quebram o layout da caixa de dialogo.
    #    RU e EN paragrafam DIFERENTE (o EN costuma abrir \n\n onde o RU nao
    #    abre), entao bater com qualquer um dos dois e' aceitavel. So e' erro
    #    quando a PT nao bate com nenhum: ai a quebra foi inventada ou perdida.
    esc = []
    for wid, pt, f in rows:
        e = byid.get(wid)
        if not e:
            continue
        en, ru = e.get("en") or "", e.get("ru") or ""
        if not en.strip() and not ru.strip():
            continue
        for token in ("\\n", "\\t"):
            n = pt.count(token)
            if n != en.count(token) and n != ru.count(token):
                esc.append((f, wid, token, ru.count(token), en.count(token), n))
    # \t divergente e' bloqueante (corrompe o TSV); \n so' muda espacamento
    # na caixa de dialogo — cosmetico, e o proprio EN reparagrafa em relacao
    # ao RU, entao pode ter sido escolha de legibilidade. Fica como aviso.
    esc_t = [x for x in esc if x[2] == "\\t"]
    esc_n = [x for x in esc if x[2] == "\\n"]
    if esc_t:
        erros.append(f"escapes \\t divergentes: {len(esc_t)} linha(s)")
        for f, wid, t, a, b, c in esc_t[:10]:
            erros.append(f"    {f} {wid}: RU={a} EN={b} PT={c}")
    if esc_n:
        avisos.append(f"quebras de paragrafo \\n que nao batem nem com RU nem "
                      f"com EN: {len(esc_n)} linha(s) — cosmetico, decidir o padrao")

    # 3b. tipografia e residuo do ingles — poucos casos, mas destoam.
    #     Creditos ficam de fora: la' as aspas cercam apelidos de pessoas
    #     reais, escritos assim pelos proprios desenvolvedores.
    CREDITOS = ("Other_00b", "Other_00c", "Other_05a")
    aspas, interj = [], []
    ANGL = re.compile(r"\b(pah|huh|ugh|whoa|yeah|okay)\b", re.I)
    for wid, pt, f in rows:
        if any(f.startswith(c) for c in CREDITOS):
            continue
        # „texto“ dentro de «...» e' citacao aninhada — convencao que o
        # proprio russo usa («Дом „Дом“»). Nao e' erro: so' se acusa o „“
        # quando nao ha o par de abertura baixo na linha.
        aninhada = "„" in pt
        if '"' in pt or ("“" in pt and not aninhada):
            aspas.append((f, wid, pt[:70]))
        if ANGL.search(pt):
            interj.append((f, wid, pt[:70]))
    if aspas:
        erros.append(f"aspas fora do padrao «»: {len(aspas)} linha(s)")
        for f, wid, t in aspas[:6]:
            erros.append(f"    {f} {wid}: {t}")
    if interj:
        avisos.append(f"interjeicoes inglesas (pah/huh/ugh...): {len(interj)} linha(s)"
                      f" — conferir se cabe equivalente em pt-BR")

    # 3c. formas de pt-PT. AVISO, nunca erro: em registro elevado (sermao,
    #     poema, carta pomposa, provérbio biblico) o tu/vos e' correto em
    #     pt-BR tambem. Serve como lista para revisar, nao para corrigir.
    PTPT = re.compile(r"(?<![\wÀ-ſ])(?:[Tt]u|[Tt]eu|[Tt]ua|[Tt]eus|[Tt]uas|"
                      r"[Cc]ontigo|[Vv]ós|[Cc]onvosco)(?![\wÀ-ſ])")
    ptpt = [(f, wid) for wid, pt, f in rows if PTPT.search(pt)]
    if ptpt:
        avisos.append(f"formas de pt-PT (tu/teu/vós): {len(ptpt)} linha(s)"
                      f" — muitas sao registro elevado legitimo; revisar, nao trocar em bloco")

    # 3d. campo extra na linha. apply_pt.py corta no primeiro TAB, entao um
    #     "id TAB cena TAB texto" faria o nome da cena aparecer no jogo.
    extras = []
    for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))):
        if os.path.basename(path) == "reviews.tsv":
            continue
        for ln in open(path, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if ln.strip() and ln.count("\t") > 1:
                extras.append((os.path.basename(path), ln.split("\t")[0], ln[:70]))
    if extras:
        erros.append(f"linhas com campo extra (vazaria para o jogo): {len(extras)}")
        for f, wid, t in extras[:6]:
            erros.append(f"    {f} {wid}: {t}")

    # 3e. placeholder do jogo traduzido. <day>, <month>, <hour> sao
    #     variaveis que o jogo substitui em execucao. Traduzidas, ele nao
    #     as encontra e mostra "<dia>" literal na tela.
    PH = re.compile(r"<([a-zA-Zа-яА-Я_]+)>")
    IGNORAR = {"i", "b", "I", "B"}
    ph_ruins = []
    for wid, pt, f in rows:
        e = byid.get(wid)
        if not e:
            continue
        src = {s for s in PH.findall(e.get("ru") or "") + PH.findall(e.get("en") or "")
               if s not in IGNORAR}
        if not src:
            continue
        achado = {s for s in PH.findall(pt) if s not in IGNORAR}
        if achado != src:
            ph_ruins.append((f, wid, sorted(src), sorted(achado)))
    if ph_ruins:
        erros.append(f"placeholders do jogo alterados: {len(ph_ruins)} linha(s)")
        for f, wid, a, b in ph_ruins[:6]:
            erros.append(f"    {f} {wid}: origem={a} pt={b}")

    # 3f. pacote compilado atrasado em relacao aos .tsv.
    #     Furo encontrado JOGANDO: o qa_check dizia "limpo" e o menu do jogo
    #     mostrava ingles, porque o ptbr_final.json era mais velho que as
    #     traducoes. Medir o corpus nao basta: o que chega na tela e' o pacote.
    final = os.path.join(ROOT, "translated", "ptbr_final.json")
    if not os.path.exists(final):
        erros.append("translated/ptbr_final.json nao existe — rode tools/apply_pt.py")
    else:
        t_pac = os.path.getmtime(final)
        recentes = [(os.path.basename(p), os.path.getmtime(p))
                    for p in glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))
                    if os.path.getmtime(p) > t_pac]
        if recentes:
            erros.append(f"pacote compilado DESATUALIZADO: {len(recentes)} arquivo(s) "
                         f"mais novos que ptbr_final.json — rode tools/apply_pt.py")
            for nome, _ in sorted(recentes)[:5]:
                erros.append(f"    {nome}")

    # 4. duplicatas divergentes
    dup = {k: v for k, v in seen.items() if len(set(v)) > 1}
    if dup:
        erros.append(f"ids duplicados com traducoes DIFERENTES: {len(dup)}")
        for k in list(dup)[:10]:
            erros.append(f"    {k}")

    # 5. cobertura
    done = {wid for wid, _, _ in rows}
    falta = [e for e in wb if e["id"] not in done]
    fb = collections.Counter()
    for e in falta:
        src = (e.get("pt") or "").strip() or (e.get("en") or "").strip()
        fb["vazio" if not src else ("russo" if CYR.search(src) else "ingles")] += 1

    print("=" * 62)
    print(f"  traduzidas : {len(done):>6} / {len(wb)}  ({100*len(done)/len(wb):.1f}%)")
    print(f"  faltam     : {len(falta):>6}  -> na tela: "
          f"{fb['ingles']} em ingles, {fb['russo']} em russo, {fb['vazio']} vazias")
    print("=" * 62)
    for a in avisos:
        print("AVISO  " + a)
    for e in erros:
        print("ERRO   " + e)
    if not erros:
        print("OK — nenhum erro bloqueante.")
    if STRICT and erros:
        sys.exit(1)


if __name__ == "__main__":
    main()
