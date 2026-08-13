"""Uniformiza o tratamento no interrogatorio: Inspetor <-> Dankovsky = "o senhor".

O criterio nao e' chute: o russo distingue «вы» (formal) de «ты» (intimo).
So' troca linhas de cena de interrogatorio cujo original esta na forma
formal. Linhas com «ты» ficam como estao — sao outros falantes (a Serafima
chamando o Daniil, por exemplo).

Protecao importante: nao mexe em «você» dentro de aspas «...», porque ai
costuma ser ditado citado, nao tratamento (ex.: 14917.21, onde o provérbio
do pardal usa «ты» de proposito).

Uso:
    python fix_tratamento_inspetor.py            # dry-run
    python fix_tratamento_inspetor.py --apply
"""
import json, os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS = os.path.join(ROOT, "translated", "pt")
APPLY = "--apply" in sys.argv

VY = re.compile(r"\b(вы|вас|вам|вами|ваш\w*)\b", re.I)
TY = re.compile(r"\b(ты|тебя|тебе|тобой|тво\w+)\b", re.I)
# desinencias verbais de 2a pessoa do plural (forma formal): -ете/-ите/-йте
VY_VERBO = re.compile(r"\b\w+(?:ете|ите|йте)\b")

# "de/em/a/por + voce" -> contracao com "o senhor"
CONTR = {"de": "do", "em": "no", "a": "ao", "por": "pelo"}

# Onde a troca mecanica fica dura, a forma vai escrita a mao.
EXCECOES = {
    # «Вам никогда не доводилось САМОМУ вести разбирательства» — "самому" e'
    # "pessoalmente"; "um interrogatorio o senhor mesmo" empilha tratamento.
    "61626.0": ("Você nunca conduziu um interrogatório você mesmo",
                "O senhor nunca conduziu um interrogatório pessoalmente"),
    # "feche a porta atras do senhor" soa estranho; o reflexivo natural e' "de si".
    "61626.7": ("feche a porta atrás de você", "feche a porta atrás de si"),
}


def manter_caixa(modelo, novo):
    return novo[:1].upper() + novo[1:] if modelo[:1].isupper() else novo


def trocar(texto):
    """Troca voce -> o senhor fora de trechos entre « »."""
    partes = re.split(r"(«[^»]*»)", texto)
    for i, parte in enumerate(partes):
        if parte.startswith("«"):
            continue  # citacao: nao e' tratamento
        parte = re.sub(
            r"(?<![\wÀ-ſ])(?:(?P<prep>[Dd]e|[Ee]m|[Aa]|[Pp]or)\s+)?(?P<v>[Vv]ocê)\b",
            lambda m: (manter_caixa(m.group("prep"), CONTR[m.group("prep").lower()]) + " senhor")
            if m.group("prep") else manter_caixa(m.group("v"), "o senhor"),
            parte,
        )
        partes[i] = parte
    return "".join(partes)


def main():
    wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
    byid = {e["id"]: e for e in wb}
    mudancas, arquivos = [], {}

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
            novo = pt
            if e and ("Inspector" in e["text"] or "Interrogation" in e["text"]):
                ru = e.get("ru") or ""
                formal = (VY.search(ru) or VY_VERBO.search(ru)) and not TY.search(ru)
                if formal and re.search(r"\bvocê\b", pt, re.I):
                    if wid in EXCECOES:
                        velho, mao = EXCECOES[wid]
                        if velho not in pt:
                            print(f"  ! excecao {wid}: trecho mudou, revisar a mao")
                            cand = pt
                        else:
                            cand = trocar(pt.replace(velho, mao))
                    else:
                        cand = trocar(pt)
                    if cand != pt:
                        novo = cand
                        mudancas.append((os.path.basename(path), wid, pt, novo))
            if novo != pt:
                dirty = True
            out.append(wid + "\t" + novo if e or pt else raw)
        arquivos[path] = (out, dirty)

    print(f"linhas a trocar: {len(mudancas)}\n")
    for f, wid, velho, novo in mudancas:
        print(f"--- {f} {wid}")
        print(f"  ANTES : {velho[:140]}")
        print(f"  DEPOIS: {novo[:140]}")

    if APPLY:
        n = sum(1 for _, (o, d) in arquivos.items() if d)
        for path, (o, d) in arquivos.items():
            if d:
                open(path, "w", encoding="utf-8", newline="\n").write("\n".join(o) + "\n")
        print(f"\nGRAVADO em {n} arquivo(s).")
    else:
        print("\n(dry-run — nada gravado. use --apply)")


if __name__ == "__main__":
    main()
