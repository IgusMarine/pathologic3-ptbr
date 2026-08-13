"""Traduz lotes pendentes chamando a API do DeepSeek, com validacao antes de gravar.

A chave vem da variavel de ambiente DEEPSEEK_API_KEY. Ela nunca e' impressa,
gravada em arquivo nem incluida em mensagem de erro.

O que este script NAO faz: confiar na resposta. Antes de salvar qualquer .tsv
ele confere que voltaram exatamente os ids pedidos, na mesma ordem, sem
duplicata e sem conteudo engolido. Se a resposta vier truncada ou torta, ele
reduz a fatia pela metade e tenta de novo. So' grava o que passou.

CUSTO: cada fatia gasta tokens da sua conta. Por isso o padrao e' UMA fatia.
Use --n N ou --tudo conscientemente.

Uso:
    python tools/traduzir_auto.py Day00_00              # 1 fatia pendente
    python tools/traduzir_auto.py Day00_00 --n 3        # 3 fatias
    python tools/traduzir_auto.py Day00_00 --tudo       # todas as pendentes
    python tools/traduzir_auto.py Day00_00 --simular    # nao chama a API
"""
import json, os, re, sys, glob, time, subprocess

# nome de cena do jogo: termina sempre em _Portuguese_Br
FORMA_CENA = re.compile(r"^[\w ()\-.]+_Portuguese_Br$")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_prompt as MP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRANS = os.path.join(ROOT, "translated", "pt")
BATCH = os.path.join(ROOT, "work", "batches")

URL = "https://api.deepseek.com/chat/completions"
MODELO = "deepseek-chat"
TEMPERATURA = 1.0      # traducao literaria: nem travado nem solto demais
MAX_TOKENS = 8000
TENTATIVAS = 3
FATIA_INICIAL = int(os.environ.get("FATIA","100"))    # prosa longa (Hospital) estourava a saida com 150


def chave():
    k = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not k:
        print("DEEPSEEK_API_KEY nao esta no ambiente.")
        print("Defina a variavel e rode de novo (nao passe a chave por argumento).")
        sys.exit(2)
    return k


def limpar(resposta):
    """Tira cerca de markdown e preambulo, se o modelo tiver posto."""
    t = resposta.strip()
    if t.startswith("```"):
        linhas = t.split("\n")
        linhas = linhas[1:]
        if linhas and linhas[-1].strip().startswith("```"):
            linhas = linhas[:-1]
        t = "\n".join(linhas)
    # descarta linhas antes do primeiro id valido
    out, comecou = [], False
    for ln in t.split("\n"):
        if not comecou:
            cabeca = ln.split("\t", 1)[0].strip()
            if cabeca and cabeca.replace(".", "").isdigit():
                comecou = True
            else:
                continue
        out.append(ln)
    return "\n".join(out)


_CENA = None


def cena_de(wid):
    """Nome da cena de um id, do workbook (carregado uma vez)."""
    global _CENA
    if _CENA is None:
        wb = json.load(open(os.path.join(ROOT, "extracted", "workbook.json"),
                            encoding="utf-8"))
        _CENA = {e["id"]: e["text"] for e in wb}
    return _CENA.get(wid)


def reparar_cena_ecoada(linhas):
    """Remove a coluna da cena quando o modelo a ecoa.

    O modelo as vezes trava nesse padrao e repete o erro ate' em fatias de
    12 linhas — recusar sozinho gera impasse. Reparar e' seguro porque so'
    remove o campo do meio quando ele bate EXATAMENTE com o nome da cena
    daquele id. Um TAB legitimo dentro da fala nunca casa, e fica intacto.
    """
    out, reparadas = [], 0
    for l in linhas:
        p = l.split("\t")
        if len(p) > 2:
            meio = p[1].strip()
            # bate com a cena daquele id, OU tem a forma de nome de cena.
            # A segunda regra cobre quando o modelo ecoa a cena de outra
            # linha; texto em portugues jamais casa esse padrao.
            if meio == cena_de(p[0].strip()) or FORMA_CENA.match(meio):
                l = p[0] + "\t" + "\t".join(p[2:])
                reparadas += 1
        out.append(l)
    return out, reparadas


def validar(resposta, esperados):
    """Devolve (ok, motivo, linhas). Nao grava nada — so' julga (e repara
    o que da' para reparar com seguranca)."""
    linhas = [l.rstrip("\r") for l in limpar(resposta).split("\n") if l.strip()]
    linhas, reparadas = reparar_cena_ecoada(linhas)
    if reparadas:
        print(f"      (reparadas {reparadas} linha(s) com a cena ecoada)")
    ids = [l.split("\t", 1)[0].strip() for l in linhas]
    if len(ids) != len(esperados):
        return False, f"vieram {len(ids)} linhas, esperava {len(esperados)}", None
    if ids != esperados:
        faltam = [i for i in esperados if i not in set(ids)]
        return False, f"ids fora de ordem ou trocados (faltam {len(faltam)})", None
    if len(set(ids)) != len(ids):
        return False, "ids repetidos", None
    # O modelo as vezes ecoa a coluna da cena: "id TAB cena TAB portugues".
    # Como apply_pt.py corta no primeiro TAB, isso colocaria o nome da cena
    # dentro do jogo. Ja aconteceu em 422 linhas do Hospital.
    extras = [l for l in linhas if l.count("\t") > 1]
    if extras:
        return False, f"{len(extras)} linha(s) com campo extra (cena ecoada)", None
    return True, "", linhas


def chamar(prompt, key):
    import requests
    r = requests.post(
        URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": MODELO,
              "messages": [{"role": "user", "content": prompt}],
              "temperature": TEMPERATURA,
              "max_tokens": MAX_TOKENS},
        timeout=600,
    )
    if r.status_code != 200:
        # nunca ecoar o corpo inteiro: pode devolver cabecalhos com a chave
        raise RuntimeError(f"HTTP {r.status_code} da API")
    d = r.json()
    esc = d["choices"][0]
    return esc["message"]["content"], esc.get("finish_reason"), d.get("usage", {})


def ja_traduzidos():
    feito = set()
    for p in glob.glob(os.path.join(TRANS, "*.tsv")):
        if os.path.basename(p) == "reviews.tsv":
            continue
        for ln in open(p, encoding="utf-8"):
            if ln.strip():
                feito.add(ln.split("\t", 1)[0].strip())
    return feito


def proximo_nome(nome):
    """Primeiro sufixo livre para o arquivo de saida.

    Uma letra da' conta de 26 fatias; lotes grandes passam disso (o Oth_A
    tem mais), entao depois de 'z' segue com 'aa', 'ab', ...
    """
    for i in range(26):
        ltr = chr(ord("a") + i)
        if not os.path.exists(os.path.join(TRANS, f"{nome}{ltr}.tsv")):
            return ltr
    for i in range(26):
        for j in range(26):
            ltr = chr(ord("a") + i) + chr(ord("a") + j)
            if not os.path.exists(os.path.join(TRANS, f"{nome}{ltr}.tsv")):
                return ltr
    raise RuntimeError("acabaram os sufixos para " + nome)


def traduzir_fatia(linhas, key, simular):
    """Tenta traduzir. Se falhar/truncar, parte no meio e tenta cada metade."""
    esperados = [l.split("\t", 1)[0].strip() for l in linhas]
    if simular:
        # devolve None de proposito: --simular NUNCA pode gravar .tsv.
        # (bug antigo: devolvia texto falso e ele ia parar no corpus)
        print(f"      [simulacao] {len(linhas)} linhas — nada enviado, nada gravado")
        return None, {}

    for tent in range(1, TENTATIVAS + 1):
        prompt = MP.texto_prompt(linhas)
        try:
            resp, fim, uso = chamar(prompt, key)
        except Exception as ex:
            print(f"      tentativa {tent}: erro na chamada — {ex}")
            time.sleep(3)
            continue
        if fim == "length":
            print(f"      tentativa {tent}: resposta truncada pelo limite de saida")
            break  # partir e' melhor que insistir
        ok, motivo, out = validar(resp, esperados)
        if ok:
            return out, uso
        print(f"      tentativa {tent}: resposta invalida — {motivo}")

    if len(linhas) <= 20:
        print(f"      DESISTINDO desta fatia de {len(linhas)} linhas")
        return None, {}
    meio = len(linhas) // 2
    print(f"      partindo {len(linhas)} em {meio} + {len(linhas)-meio}")
    a, ua = traduzir_fatia(linhas[:meio], key, simular)
    b, ub = traduzir_fatia(linhas[meio:], key, simular)
    if a is None or b is None:
        return None, {}
    # so' soma contadores inteiros: a API devolve tambem campos aninhados
    # (prompt_tokens_details), e dict+dict estoura.
    uso = {k: ua.get(k, 0) + ub.get(k, 0)
           for k in set(ua) | set(ub)
           if isinstance(ua.get(k, 0), int) and isinstance(ub.get(k, 0), int)}
    return a + b, uso


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    nome = sys.argv[1]
    simular = "--simular" in sys.argv
    if "--tudo" in sys.argv:
        limite = 10**6
    elif "--n" in sys.argv:
        limite = int(sys.argv[sys.argv.index("--n") + 1])
    else:
        limite = 1

    caminho = os.path.join(BATCH, nome + ".txt")
    if not os.path.exists(caminho):
        print(f"lote nao encontrado: {caminho}")
        print("gere com: python tools/export_batch.py <grupo> 0 900")
        sys.exit(1)

    key = "" if simular else chave()
    feito = ja_traduzidos()
    pend = [l for l in open(caminho, encoding="utf-8").read().split("\n")
            if l.strip() and l.split("\t", 1)[0].strip() not in feito]
    print(f"lote {nome}: {len(pend)} linhas pendentes")
    if not pend:
        print("nada a fazer.")
        return

    fatias = [pend[i:i + FATIA_INICIAL] for i in range(0, len(pend), FATIA_INICIAL)][:limite]
    print(f"vou processar {len(fatias)} fatia(s) de ate {FATIA_INICIAL} linhas\n")

    total_uso, gravados = {}, []
    for n, linhas in enumerate(fatias, 1):
        ltr = proximo_nome(nome)
        print(f"  [{n}/{len(fatias)}] -> {nome}{ltr}.tsv  ({len(linhas)} linhas)")
        out, uso = traduzir_fatia(linhas, key, simular)
        if out is None:
            if not simular:
                print("      FALHOU — nada gravado para esta fatia")
            print()
            continue
        destino = os.path.join(TRANS, f"{nome}{ltr}.tsv")
        with open(destino, "w", encoding="utf-8", newline="\n") as fh:
            fh.write("\n".join(out) + "\n")
        gravados.append(os.path.basename(destino))
        for k, v in uso.items():
            if isinstance(v, int):
                total_uso[k] = total_uso.get(k, 0) + v
        print(f"      gravado ({len(out)} linhas)\n")

    if total_uso:
        print("tokens:", {k: total_uso[k] for k in sorted(total_uso)})
    if gravados and not simular:
        print("\naplicando correcoes automaticas e rodando o portao...\n")
        for script in ("enforce_glossary.py", "fix_aspas.py", "fix_campos_extras.py"):
            subprocess.call([sys.executable, os.path.join(ROOT, "tools", script), "--apply"])
        subprocess.call([sys.executable, os.path.join(ROOT, "tools", "qa_check.py")])


if __name__ == "__main__":
    main()
