"""Troca interjeicao inglesa que vazou do texto-fonte por equivalente pt-BR.

Nao e' troca em bloco: cada uma vem de uma interjeicao russa diferente e
pede resposta diferente.

  «тьфу»  cuspe de desprezo      -> bah
  «бр-р»  arrepio                -> brr   (existe igual em pt-BR)
  «Н-да»  resmungo resignado     -> Pois é
  «Ну-ну» ceticismo              -> Sei, sei
  sem russo, nojo de gosto       -> eca

Linha cuja origem nao casa nenhuma regra fica intacta e e' relatada: sem
saber o que o russo diz, trocar seria chute.

Uso:
    python fix_interjeicoes.py            # dry-run
    python fix_interjeicoes.py --apply
"""
import json, os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APLICAR = "--apply" in sys.argv
CREDITOS = ("Other_00b", "Other_00c", "Other_05a")

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
byid = {e["id"]: e for e in wb}

REGRAS = [
    ("тьфу", "bah"),
    ("бр-р", "brr"),
    ("н-да", "pois é"),
    ("ну-ну", "sei, sei"),
    ("ух,", "ui"),
    ("ба!", "ora"),
]
ANGL = re.compile(r"\b(pah|huh|ugh|whoa|yeah|okay)\b", re.I)
UH_HUH = re.compile(r"\bUh-huh\b", re.I)

trocas, sem_regra = [], []
for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))):
    nome = os.path.basename(path)
    if nome == "reviews.tsv" or any(nome.startswith(c) for c in CREDITOS):
        continue
    linhas = open(path, encoding="utf-8").read().split("\n")
    out, dirty = [], False
    for ln in linhas:
        wid, sep, pt = ln.partition("\t")
        m = ANGL.search(pt) if sep else None
        if m:
            e = byid.get(wid.strip())
            ru = (e.get("ru") or "").lower() if e else ""
            alvo = None
            for chave, subst in REGRAS:
                if chave in ru:
                    alvo = subst
                    break
            if alvo is None and not ru.strip():
                alvo = "eca"          # nojo puro, sem origem russa
            if alvo:
                # "Uh-huh" e' uma unidade; troca inteira
                # preserva a caixa: "Ugh!" no inicio da frase vira "Bah!"
                def com_caixa(mm):
                    orig = mm.group(0)
                    return alvo[:1].upper() + alvo[1:] if orig[:1].isupper() else alvo
                novo = UH_HUH.sub(com_caixa, pt)
                if novo == pt:
                    novo = ANGL.sub(com_caixa, pt, count=1)
                if novo != pt:
                    trocas.append((nome, wid.strip(), m.group(0), alvo, novo[:70]))
                    pt, dirty = novo, True
                    ln = wid + sep + pt
            else:
                sem_regra.append((nome, wid.strip(), m.group(0), ru[:60]))
        out.append(ln)
    if dirty and APLICAR:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print(f"trocas: {len(trocas)}")
for nome, wid, de, para, amostra in trocas[:15]:
    print(f"   {wid:<11} {de} -> {para}   {amostra}")
print(f"\nsem regra (origem nao identificada, intactas): {len(sem_regra)}")
for nome, wid, de, ru in sem_regra[:10]:
    print(f"   {wid:<11} {de}   RU: {ru}")
print("\nGRAVADO." if APLICAR else "\n(dry-run — use --apply)")
