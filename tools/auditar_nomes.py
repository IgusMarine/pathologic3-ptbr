"""Audita TODO o corpus atras de nome proprio partido em duas formas.

Foi assim que apareceram, um a um e por acaso, os 239 "Peter", os 17
"Yakov Little", o "Corvo" ocupando o nome do Chernyak e o Tsipuch/Tsipukh.
Este script procura o padrao inteiro de uma vez, em vez de esperar tropecar.

Metodo: para cada nome proprio RUSSO frequente, coleta as palavras
capitalizadas que aparecem nas traducoes das linhas que o contem. Se um
mesmo nome russo aparece junto de duas grafias parecidas (ou de uma
palavra inglesa), reporta.

Nao corrige nada — so' aponta. Cada caso precisa de olho humano, porque
nome de personagem diferente pode conviver na mesma linha.

Uso: python auditar_nomes.py [minimo_de_ocorrencias]
"""
import json, os, re, glob, sys, collections, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN = int(sys.argv[1]) if len(sys.argv) > 1 else 4

wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"), encoding="utf-8"))
tr = {}
for p in glob.glob(os.path.join(ROOT, "translated", "pt", "*.tsv")):
    if os.path.basename(p) == "reviews.tsv":
        continue
    for ln in open(p, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.strip():
            w, _, t = ln.partition("\t")
            tr[w.strip()] = t

# nomes proprios russos: maiuscula inicial, fora de inicio de frase
RU_NOME = re.compile(r"(?<![.!?…]\s)(?<!^)\b([А-ЯЁ][а-яё]{3,})\b")
PT_NOME = re.compile(r"\b([A-ZÀ-Ý][\wÀ-ÿ]{2,})\b")

# palavras pt que nao sao nome, so' comecam frase
RUIDO = set("""Nao Não Mas Voce Você Ele Ela Eue Que Como Sim Por Se Quando Isso Aqui
Uma Meu Minha Agora Bem Ah Oh Depois Todos Talvez Ainda Tudo Estou Vou Foi Tem Nem
Onde Quem Para Sobre Peste Cidade Doutor Deus Senhor Entao Então Pois Ora Claro Nada
Nunca Vamos Deixe Pode Preciso Sei Acho Era Sao São Esse Essa Este Esta Aquele Antes
Depressa Cuidado Escute Olha Veja Sabe Diga Fale Espere Certo Errado Muito Pouco Mais
Menos Tao Tão Assim Talvez Enfim Alias Aliás Porque Porem Porém Contudo Logo Ate Até
Desde Sem Com Dos Das Nos Nas Aos Uns Umas Seu Sua Meus Suas Dele Dela Deles Delas""".split())

ocorr = collections.defaultdict(collections.Counter)
for e in wb:
    ru, wid = e.get("ru") or "", e["id"]
    if wid not in tr:
        continue
    pt = tr[wid]
    for nome_ru in set(RU_NOME.findall(ru)):
        for nome_pt in set(PT_NOME.findall(pt)):
            if nome_pt in RUIDO:
                continue
            ocorr[nome_ru][nome_pt] += 1

suspeitos = []
for nome_ru, c in ocorr.items():
    total = sum(c.values())
    if total < MIN:
        continue
    cands = [(p, n) for p, n in c.most_common(8) if n >= 2]
    # duas grafias PARECIDAS para o mesmo nome russo = provavel split
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            a, na = cands[i]
            b, nb = cands[j]
            if a == b:
                continue
            r = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
            if r >= 0.62 and min(na, nb) >= 2:
                suspeitos.append((nome_ru, a, na, b, nb, round(r, 2)))

suspeitos.sort(key=lambda x: -(x[2] + x[4]))
print(f"nomes russos analisados: {len(ocorr)}")
print(f"suspeitas de grafia partida: {len(suspeitos)}\n")
for ru, a, na, b, nb, r in suspeitos[:40]:
    print(f"  {ru:<16} {a} ({na})  vs  {b} ({nb})   semelhanca {r}")
