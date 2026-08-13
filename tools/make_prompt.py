"""Monta o pacote que vai para o modelo tradutor: instrucoes + glossario + lote.

O glossario e' gerado a partir de research/glossario.lock.tsv, entao nunca
dessincroniza. O contexto do modelo zera a cada lote — se o glossario nao
viajar junto, a terminologia deriva (foi o que aconteceu do Day07 em diante).

Um lote de 900 linhas nao cabe numa colada so. Por isso o lote sai fatiado
em pedacos de 200, com a letra batendo com o nome do arquivo de saida:

    python make_prompt.py Day13_00 a   -> grava work/prompt_Day13_00a.txt
                                          (traduzir e salvar a resposta em
                                           translated/pt/Day13_00a.tsv)

Sem letra, gera TODAS as fatias do lote de uma vez.

O arquivo e' gravado pelo proprio script, em UTF-8. Nao use "> arquivo.txt":
no Windows o redirecionamento do console estraga os acentos e o cirilico.
"""
import os, sys, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(ROOT, "research", "glossario.lock.tsv")
BATCH = os.path.join(ROOT, "work", "batches")
INSTR = os.path.join(ROOT, "research", "INSTRUCOES_TRADUTOR.md")


def glossario():
    """Lista enxuta: RU -> PT. Sem as notas, que so gastariam contexto.

    A forma russa vem da coluna ru_display (nominativo, escrita a mao).
    Derivar do regex do gatilho nao funciona: classes de caractere viram
    lixo ("эмш[еэи]н" -> "эмшеэин") e alternativas viram forma flexionada.
    """
    linhas = []
    for ln in open(LOCK, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        p = ln.split("\t")
        if p[0] == "canonico":
            continue
        while len(p) < 6:
            p.append("")
        ru = p[5].strip()
        if not ru:
            continue  # sem forma legivel declarada: fora da lista, nao chuta
        proib = [v.split(":")[0].strip() for v in p[3].split(";") if v.strip()]
        linha = f"  {ru:<20} -> {p[0]}"
        if proib:
            linha += f"   (NUNCA: {', '.join(proib)})"
        linhas.append(linha)
    return "\n".join(linhas)


FATIA = 200
WORK = os.path.join(ROOT, "work")


def texto_prompt(linhas, rodape=""):
    """Monta o texto completo do prompt. Usado tanto para colar a mao
    quanto por traduzir_auto.py."""
    return "\n".join([
        open(INSTR, encoding="utf-8").read(),
        "\n## GLOSSÁRIO OBRIGATÓRIO (russo -> pt-BR)\n",
        glossario(),
        "\n## LOTE A TRADUZIR\n",
        "Formato de entrada:  id ⇥ cena ⇥ russo ⇥ inglês",
        "Formato de saída:    id ⇥ português    (só isso, uma linha por id)",
        f"São {len(linhas)} linhas. Devolva as {len(linhas)}, na mesma ordem.\n",
        "\n".join(linhas),
        rodape,
    ])


def montar(nome, letra, linhas):
    saida_tsv = f"translated/pt/{nome}{letra}.tsv"
    destino = os.path.join(WORK, f"prompt_{nome}{letra}.txt")
    with open(destino, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto_prompt(linhas, f"\n<!-- salvar a resposta em {saida_tsv} -->"))
    return destino, saida_tsv


def main():
    if len(sys.argv) < 2:
        print("uso: python tools/make_prompt.py <lote> [letra]")
        print("  ex: python tools/make_prompt.py Day00_00 a")
        print("      python tools/make_prompt.py Day00_00     (gera todas as fatias)")
        sys.exit(2)
    nome = sys.argv[1]
    if nome.endswith(".txt"):
        nome = nome[:-4]
    letra = sys.argv[2].strip().lower() if len(sys.argv) > 2 else None
    caminho = os.path.join(BATCH, nome + ".txt")
    if not os.path.exists(caminho):
        print(f"lote nao encontrado: {caminho}")
        print("gere primeiro com: python tools/export_batch.py <grupo> 0 900")
        sys.exit(1)

    todas = [l for l in open(caminho, encoding="utf-8").read().split("\n") if l.strip()]
    n_fatias = (len(todas) + FATIA - 1) // FATIA
    ultima = chr(ord("a") + n_fatias - 1)

    if letra:
        i = ord(letra) - ord("a")
        if not (0 <= i < n_fatias):
            print(f"a letra '{letra}' nao existe neste lote: vai de a ate {ultima}")
            sys.exit(1)
        alvos = [(letra, todas[i * FATIA:(i + 1) * FATIA])]
    else:
        alvos = [(chr(ord("a") + i), todas[i * FATIA:(i + 1) * FATIA])
                 for i in range(n_fatias)]

    print(f"lote {nome}: {len(todas)} linhas em {n_fatias} fatia(s) (a..{ultima})\n")
    for ltr, linhas in alvos:
        destino, saida_tsv = montar(nome, ltr, linhas)
        print(f"  [{ltr}] {len(linhas):>3} linhas")
        print(f"      colar : {destino}")
        print(f"      salvar: {saida_tsv}")
    print("\nAbra o arquivo 'colar', copie TUDO (Ctrl+A, Ctrl+C) e cole no DeepSeek.")


if __name__ == "__main__":
    main()
