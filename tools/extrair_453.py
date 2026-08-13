# -*- coding: utf-8 -*-
"""Extrai os 453 assets de texto que a extracao original perdeu.

POR QUE ELES SUMIRAM
O jogo tem 9345 TextAssets por idioma. Varios sao arquivos DIFERENTES, em
pastas diferentes, com o mesmo nome de arquivo — por exemplo dois Labels,
um em ui/microscope/ e outro em ui/demowindow/. A extracao original indexou
por m_Name, entao cada par desses perdeu uma das copias: sobrou uma, a
outra nunca entrou no workbook. Sao 453 assets, 2488 chaves.

Investigacao anterior confirmou que o jogo CARREGA as duas copias (cada uma
tem caminho Resources.Load proprio no globalgamemanagers, e as chaves de
uma nao existem na outra). Ou seja: e' texto vivo, sem traducao.

COMO PAREIA PT COM RU/EN
Nao da' para parear por nome (e' justamente o que colide). Pareia pelo
CONJUNTO DE CHAVES: a copia portuguesa de um asset tem exatamente as mesmas
chaves da copia russa correspondente. Isso identifica o par sem ambiguidade.

SAIDA
  extracted/workbook_453.json   mesmo formato do workbook.json principal
  work/453_resumo.tsv           o que tem em cada asset, para triagem

Uso: python extrair_453.py
"""
import os, sys, json, re, collections

sys.stdout.reconfigure(encoding="utf-8")
import UnityPy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOM = "\ufeff"
CIR = re.compile(r"[А-Яа-яЁё]")

CANDS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Pathologic 3",
    r"D:\SteamLibrary\steamapps\common\Pathologic 3",
]
vdf = r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
if os.path.exists(vdf):
    for linha in open(vdf, encoding="utf-8", errors="ignore"):
        if '"path"' in linha:
            base = linha.split('"')[3].replace(chr(92) + chr(92), chr(92))
            CANDS.append(os.path.join(base, "steamapps", "common", "Pathologic 3"))

asset = None
for b in CANDS:
    a = os.path.join(b, "Pathologic3_Data", "resources.assets")
    if os.path.exists(a):
        asset = a
        break
if not asset:
    sys.exit("nao achei a instalacao do jogo")

# Le sempre do BACKUP: e' o original intocado, e o resources.assets pode
# estar sendo reescrito por uma injecao em andamento.
fonte = asset + ".bak"
if not os.path.exists(fonte):
    sys.exit("resources.assets.bak nao existe — rode a injecao uma vez antes")

IDIOMAS = ("_Portuguese_Br", "_Russian", "_English")


def registros(texto):
    """Quebra o asset em (chave, valor). Uma quebra de linha REAL separa um
    registro do proximo; a quebra de paragrafo dentro de um valor fica como
    escape literal e nao deve ser tocada aqui."""
    out = []
    for linha in texto.replace("\r\n", "\n").split("\n"):
        linha = linha.lstrip(BOM)
        if linha.startswith("{") and "}" in linha:
            i = linha.index("}")
            out.append((linha[1:i], linha[i + 1:].lstrip(" ")))
    return out


print(f"lendo {fonte} ...")
env = UnityPy.load(fonte)
porIdioma = {lang: {} for lang in IDIOMAS}
for obj in env.objects:
    if obj.type.name != "TextAsset":
        continue
    d = obj.read()
    nome = getattr(d, "m_Name", "") or ""
    for lang in IDIOMAS:
        if nome.endswith(lang):
            s = d.m_Script
            if isinstance(s, (bytes, bytearray)):
                s = s.decode("utf-8", "replace")
            porIdioma[lang][obj.path_id] = (nome, registros(s))
            break
for lang in IDIOMAS:
    print(f"   {lang:<16} {len(porIdioma[lang])} assets")

# path_ids que o workbook principal ja cobre
wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
cobertos = {e["id"].split(".")[0] for e in wb}
print(f"\njá cobertos pelo workbook principal: {len(cobertos)}")

# indices por conjunto de chaves, para parear PT com RU/EN
def indice(lang):
    idx = {}
    for pid, (nome, regs) in porIdioma[lang].items():
        idx.setdefault(frozenset(k for k, _ in regs), []).append(pid)
    return idx


idx_ru, idx_en = indice("_Russian"), indice("_English")

novo, resumo = [], []
sem_par = 0
for pid, (nome, regs) in sorted(porIdioma["_Portuguese_Br"].items()):
    if str(pid) in cobertos:
        continue
    chaves = frozenset(k for k, _ in regs)
    ru_pid = (idx_ru.get(chaves) or [None])[0]
    en_pid = (idx_en.get(chaves) or [None])[0]
    if ru_pid is None and en_pid is None and chaves:
        sem_par += 1
    ru_map = dict(porIdioma["_Russian"][ru_pid][1]) if ru_pid else {}
    en_map = dict(porIdioma["_English"][en_pid][1]) if en_pid else {}

    com_texto = sum(1 for _, v in regs if v.strip())
    cirilico = sum(1 for _, v in regs if CIR.search(v))
    chars = sum(len(v) for _, v in regs)
    resumo.append((nome, pid, len(regs), com_texto, cirilico, chars,
                   (regs[0][1][:70] if regs else "")))

    for i, (k, v) in enumerate(regs):
        novo.append({
            "id": f"{pid}.{i}",
            "text": nome,
            "key": k,
            "en": en_map.get(k, ""),
            "ru": ru_map.get(k, ""),
            "pt": v,
            "status": "todo",
            "group": "extra453",
        })

os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
with open(os.path.join(ROOT, "extracted", "workbook_453.json"), "w", encoding="utf-8") as fh:
    json.dump(novo, fh, ensure_ascii=False, indent=0)

resumo.sort(key=lambda r: -r[5])
TAB = chr(9)
with open(os.path.join(ROOT, "work", "453_resumo.tsv"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(TAB.join(["asset", "path_id", "registros", "com_texto", "com_cirilico",
                       "caracteres", "amostra"]) + "\n")
    for r in resumo:
        fh.write(TAB.join(str(x).replace(TAB, " ") for x in r) + "\n")

vivos = [r for r in resumo if r[3] > 0]
print(f"\nassets extraidos            : {len(resumo)}")
print(f"   com algum texto          : {len(vivos)}")
print(f"   sem par ru/en encontrado : {sem_par}")
print(f"registros (chaves) no total : {len(novo)}")
print(f"   com texto de verdade     : {sum(1 for e in novo if e['pt'].strip())}")
print(f"   com cirilico no pt       : {sum(1 for e in novo if CIR.search(e['pt']))}")
print(f"   com russo de origem      : {sum(1 for e in novo if e['ru'].strip())}")
print(f"   com ingles de origem     : {sum(1 for e in novo if e['en'].strip())}")
print(f"caracteres a traduzir       : {sum(len(e['pt']) for e in novo)}")
print("\ngravado: extracted/workbook_453.json  e  work/453_resumo.tsv")
