"""Translitera palavras da estepe que ficaram em cirilico na traducao.

O glossario manda manter as palavras da estepe como CODIGO CULTURAL, em
transliteracao latina (bayarlaa, emshen, khatanghe) — nunca em cirilico,
que o jogador brasileiro nao le.

As formas abaixo nao sao invencao: sao as que o Prologo ja estabeleceu
para as MESMAS falas, que reaparecem em outras cenas.

Nao toca em:
  - creditos (nomes de pessoas reais)
  - a lista de idiomas (o seletor mostra cada lingua no proprio alfabeto)
  - lixo de teclado do proprio original (павп, вапвап, сам пр 1)

Uso:
    python fix_cirilico.py            # dry-run
    python fix_cirilico.py --apply
"""
import os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APLICAR = "--apply" in sys.argv

# formas fixadas pelo Prologo (51432.*) para as mesmas falas
MAPA = [
    ("Сайн байна, эрдэм", "Sayn bayna, erdem"),
    ("Би харанаб, ты сердит", "Bi kharanab, você está zangado"),
    ("Ши юундэ ерээбши", "Shee yunde ereebshee"),
    ("Айдаhамни хүрэнэ", "Aydahamni hүrene"),
    ("Болииш, бүү алыш", "Boleesh, bүү alysh"),
    ("Энэ ши юун хун гээшэбши", "Ene shi yüün khün geeshebshi"),
    ("Чи болохогүй", "Chi bolokhogүi"),
    ("Би ойлгоно угыб", "Be oylgono ugyb"),
    ("Бу ногоон, бу улаан", "bu nogoon, bu ulaan"),
    ("Шпилька-дүү", "Shpilka-dүү"),
    ("Байгалдай", "Baighaldai"),
    ("Хатангэ", "Khatanghe"),
    ("Баярлаа", "Bayarlaa"),
    ("мүү юүмэн", "mүү yүүmen"),
    ("Нүхэр", "Nүkher"),
    ("нүхэр", "nүkher"),
    ("эрдэм", "erdem"),
    ("хэтэй", "khetei"),
    ("Эм...", "Em..."),
]

# lixo do proprio original: nao e' traducao pendente, e' placeholder de dev
LIXO = re.compile(r"^(павп|ав|ввв|вапвап\w*|укцукцк|пр|сам пр \d+)\s*$")
IGNORAR_ARQ = ("Other_00b", "Other_00c", "Other_05a")
IGNORAR_ID = {"39250.1"}          # «Русский» no seletor de idiomas

CIR = re.compile(r"[А-Яа-яЁё]")

trocas, restantes = [], []
for path in sorted(glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv"))):
    nome = os.path.basename(path)
    if nome == "reviews.tsv" or any(nome.startswith(x) for x in IGNORAR_ARQ):
        continue
    linhas = open(path, encoding="utf-8").read().split("\n")
    out, dirty = [], False
    for ln in linhas:
        wid, sep, pt = ln.partition("\t")
        if sep and CIR.search(pt) and wid.strip() not in IGNORAR_ID:
            if LIXO.match(pt.strip()):
                out.append(ln)
                continue
            antes = pt
            for cir, lat in MAPA:
                pt = pt.replace(cir, lat)
            if pt != antes:
                trocas.append((nome, wid.strip(), pt[:78]))
                dirty = True
            if CIR.search(pt):
                restantes.append((nome, wid.strip(), pt[:78]))
            ln = wid + sep + pt
        out.append(ln)
    if dirty and APLICAR:
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out))

print(f"linhas transliteradas: {len(trocas)}")
for nome, wid, t in trocas[:12]:
    print(f"   {wid:<11} {t}")
print(f"\nainda com cirilico apos a troca: {len(restantes)}")
for nome, wid, t in restantes[:10]:
    print(f"   {wid:<11} ({nome}) {t}")
print("\nGRAVADO." if APLICAR else "\n(dry-run — use --apply)")
