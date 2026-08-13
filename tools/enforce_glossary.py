"""Aplica research/glossario.lock.tsv retroativamente as traducoes.

O gatilho e' sempre o RUSSO de origem — nunca o portugues. Isso evita
corromper homografos: «железные коробки» sao caixas literais, nao o Короб.

Substitui a variante proibida pelo canonico ajustando artigo, preposicao
contraida e concordancia de genero/numero.

Uso:
    python enforce_glossary.py            # dry-run: so relata
    python enforce_glossary.py --apply    # grava os .tsv
"""
import json, os, re, glob, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(ROOT, "research", "glossario.lock.tsv")
TRANS = os.path.join(ROOT, "translated", "pt")
APPLY = "--apply" in sys.argv

# artigo definido por genero/numero
ART = {"ms": "o", "fs": "a", "mp": "os", "fp": "as"}
# preposicao + artigo -> forma contraida, por genero/numero do termo
CONTR = {
    "de": {"ms": "do", "fs": "da", "mp": "dos", "fp": "das"},
    "em": {"ms": "no", "fs": "na", "mp": "nos", "fp": "nas"},
    "a":  {"ms": "ao", "fs": "à",  "mp": "aos", "fp": "às"},
    "por": {"ms": "pelo", "fs": "pela", "mp": "pelos", "fp": "pelas"},
}
# formas contraidas -> (preposicao, gen_num de origem), para reconhecer o que esta escrito
CONTR_REV = {}
for prep, m in CONTR.items():
    for gn, form in m.items():
        CONTR_REV[form] = prep

# No corpus a quebra de paragrafo e' o escape LITERAL de dois caracteres
# (barra invertida + "n"; a tabulacao decorativa usa "t"), nunca um \n de
# verdade. Como "n"/"t" sao caractere de palavra, um termo colado nesse escape
# («...\nGannet») nao tem fronteira de palavra a esquerda e escapava da
# varredura. Este lookbehind reconhece exatamente o fim do escape: exige uma
# barra invertida REAL antes do "n"/"t", sequencia que nao existe dentro de
# palavra nenhuma — por isso ele nao afrouxa a protecao contra casar no meio
# de palavra.
# NAO estender isto ao gatilho RUSSO: ver a justificativa do descarte do
# FERRAMENTA_2 (creditos/apoiadores).
ESC_BEHIND = r"(?<=\\[nt])"


def load_lock():
    rules = []
    for ln in open(LOCK, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        parts = ln.split("\t")
        if parts[0] == "canonico":
            continue
        while len(parts) < 5:
            parts.append("")
        canon, gen_num, ru, proib, nota = parts[:5]
        if not proib.strip():
            continue  # sem variantes a corrigir: so serve para o qa_check
        bare = re.sub(r"^(?:o|a|os|as)\s+", "", canon)
        variants = []
        for v in proib.split(";"):
            v = v.strip()
            if not v:
                continue
            name, _, vgn = v.partition(":")
            variants.append((name.strip(), (vgn.strip() or "inv")))
        rules.append({
            "canon": canon, "bare": bare, "gn": gen_num.strip(),
            "ru": re.compile(ru.strip()), "variants": variants, "nota": nota,
        })
    return rules


def keep_case(model, word):
    """Aplica a capitalizacao de `model` (ex.: 'No') a `word` (ex.: 'no')."""
    return word[:1].upper() + word[1:] if model[:1].isupper() else word


def build_pattern(variant, vgn):
    """Casa a variante com artigo/preposicao opcionais que a precedam.

    (?<![\\w\\u00c0-\\u017f]) impede casar dentro de palavra — sem isso o 'a'
    final de "para" era lido como preposicao ("para o Baco" -> "parao Rim").
    A alternativa ESC_BEHIND cobre o termo colado num escape literal
    ("\\n\\nGannet"), onde o "n" do escape mata a fronteira.
    """
    arts = "|".join(sorted(set(ART.values()), key=len, reverse=True))
    contrs = "|".join(sorted(CONTR_REV, key=len, reverse=True))
    return re.compile(
        r"(?:(?<![\wÀ-ſ])|" + ESC_BEHIND + r")"
        r"(?:(?P<contr>" + contrs + r")\s+|(?P<prep>de|em|a|por)\s+(?P<art2>" + arts + r")\s+|(?P<art>" + arts + r")\s+)?"
        # o termo casa case-SENSITIVE (e' nome proprio); so os artigos/preposicoes
        # que o antecedem e' que sao case-insensitive ("No Cetro" no inicio da frase)
        r"(?P<term>(?-i:" + re.escape(variant) + r"))\b"
        # Variante com virgula e' aposto ("Vlad, o Gordo, precisa..."). Ao
        # trocar por um apelido de uma palavra, a virgula de fechamento do
        # aposto fica orfa — entao ela e' consumida junto.
        + (r"(?P<aposto>,)?" if "," in variant else ""),
        re.IGNORECASE,
    )


def replace_one(m, rule):
    """Reescreve o trecho casado com o canonico e a concordancia certa.

    gen_num 'inv' (nome proprio): troca so a palavra e preserva intacto o que
    vier antes. Quem traduziu ja decidiu por contexto se cabia artigo — em
    pt-BR "a Grace disse" e "Grace disse" sao ambos naturais, e nao e' papel
    deste script arbitrar isso.
    """
    gn = rule["gn"]
    bare = rule["bare"]
    if gn == "inv":
        return m.group(0)[: m.start("term") - m.start(0)] + bare
    if m.group("contr"):
        prep = CONTR_REV[m.group("contr").lower()]
        return keep_case(m.group("contr"), CONTR[prep][gn]) + " " + bare
    if m.group("prep"):
        prep = m.group("prep").lower()
        new = CONTR[prep][gn] if prep in CONTR else prep + " " + ART[gn]
        return keep_case(m.group("prep"), new) + " " + bare
    if m.group("art"):
        return keep_case(m.group("art"), ART[gn]) + " " + bare
    return bare


def main():
    wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
    byid = {e["id"]: e for e in wb}
    rules = load_lock()
    for r in rules:
        r["pats"] = [(v, build_pattern(v, vgn)) for v, vgn in r["variants"]]

    changes = []
    per_file = collections.defaultdict(list)

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
            # Creditos NUNCA passam pelo glossario: sao nomes de pessoas
            # reais. O russo dos creditos lista «Пётр Потапов», o gatilho de
            # Pyotr casa, e a varredura renomearia um colaborador de verdade
            # para "Pyotr Potapov". O mesmo vale para a lista de apoiadores.
            if e and (e.get("key", "").startswith("UI.Credits")
                      or "redit" in e.get("text", "")):
                out.append(wid + "\t" + new)
                continue
            if e:
                # A quebra de paragrafo vem como escape literal de dois
                # caracteres. Colada num nome ("...hospital.\n\nОлуша"), o "n"
                # do escape e a letra seguinte sao ambos caractere de palavra
                # para o regex, entao a fronteira \b nao existe e o gatilho
                # NUNCA dispara. Foi assim que o "Gannet" escapou da varredura
                # mesmo com "Atoba" travado.
                # Normalizar o texto de BUSCA resolve sem afrouxar a fronteira:
                # tentar relaxar o proprio padrao fazia a varredura invadir os
                # creditos e trocar nome de pessoa real.
                ru = (e.get("ru") or "").replace("\\n", " ").replace("\\t", " ")
                for r in rules:
                    if not r["ru"].search(ru):
                        continue  # gatilho russo ausente: nao mexe
                    for variant, pat in r["pats"]:
                        if variant not in new:
                            continue
                        rep = pat.sub(lambda m: replace_one(m, r), new)
                        if rep != new:
                            changes.append((os.path.basename(path), wid, variant,
                                            r["canon"], new, rep))
                            new = rep
            if new != pt:
                dirty = True
            out.append(wid + "\t" + new if e or pt else raw)
        per_file[path] = (out, dirty)

    print(f"linhas alteradas: {len(changes)}")
    by_term = collections.Counter(c[3] for c in changes)
    for term, n in by_term.most_common():
        print(f"  {n:4d}  -> {term}")
    print()
    for f, wid, var, canon, old, new in changes:
        print(f"--- {f} {wid}   [{var} -> {canon}]")
        print(f"  ANTES: {old[:150]}")
        print(f"  DEPOIS: {new[:150]}")

    if APPLY:
        n = 0
        for path, (out, dirty) in per_file.items():
            if dirty:
                open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
                n += 1
        print(f"\nGRAVADO em {n} arquivo(s).")
    else:
        print("\n(dry-run — nada gravado. use --apply)")


if __name__ == "__main__":
    main()
