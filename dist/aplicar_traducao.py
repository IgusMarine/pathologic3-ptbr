"""Aplica a traducao pt-BR de Pathologic 3.

Este script NAO contem o jogo. Ele altera a sua propria copia instalada,
aplicando o arquivo de textos traduzidos que acompanha o pacote.

Antes de alterar qualquer coisa ele faz uma copia de seguranca
(resources.assets.bak). Para voltar ao original, rode:

    python aplicar_traducao.py --restaurar

Uso:
    python aplicar_traducao.py                      # procura o jogo sozinho
    python aplicar_traducao.py "D:\\Jogos\\Pathologic 3"   # caminho manual
"""
import sys, os, shutil, json, glob

AQUI = os.path.dirname(os.path.abspath(__file__))
TEXTOS = os.path.join(AQUI, "ptbr_final.json")

CAMINHOS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\Pathologic 3",
    r"C:\Program Files\Steam\steamapps\common\Pathologic 3",
    r"C:\SteamLibrary\steamapps\common\Pathologic 3",
    r"D:\SteamLibrary\steamapps\common\Pathologic 3",
    r"D:\Steam\steamapps\common\Pathologic 3",
    r"E:\SteamLibrary\steamapps\common\Pathologic 3",
    r"C:\Program Files (x86)\GOG Galaxy\Games\Pathologic 3",
]


def achar_jogo(manual=None):
    """Devolve o caminho de resources.assets, ou None."""
    tentativas = []
    if manual:
        tentativas.append(manual)
    tentativas += CAMINHOS
    # tambem le as bibliotecas extras que o Steam registra
    vdf = r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
    if os.path.exists(vdf):
        try:
            for linha in open(vdf, encoding="utf-8", errors="ignore"):
                if '"path"' in linha:
                    base = linha.split('"')[3].replace("\\\\", "\\")
                    tentativas.append(os.path.join(
                        base, "steamapps", "common", "Pathologic 3"))
        except Exception:
            pass

    for base in tentativas:
        alvo = os.path.join(base, "Pathologic3_Data", "resources.assets")
        if os.path.exists(alvo):
            return alvo
        # caso o caminho ja aponte para a pasta _Data
        alvo2 = os.path.join(base, "resources.assets")
        if os.path.exists(alvo2):
            return alvo2
    return None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    manual = args[0] if args else None
    asset = achar_jogo(manual)

    if not asset:
        print("Nao encontrei a instalacao do Pathologic 3.")
        print()
        print("Passe o caminho da pasta do jogo como argumento. Exemplo:")
        print('   python aplicar_traducao.py "D:\\SteamLibrary\\steamapps\\common\\Pathologic 3"')
        print()
        print("A pasta certa e a que contem 'Pathologic3_Data'.")
        sys.exit(1)

    backup = asset + ".bak"
    print(f"jogo encontrado em:\n   {asset}\n")

    if "--restaurar" in sys.argv or "--restore" in sys.argv:
        if os.path.exists(backup):
            shutil.copy2(backup, asset)
            print("Original restaurado. O jogo voltou ao idioma de antes.")
        else:
            print("Nao ha copia de seguranca — nada a restaurar.")
            print("Se precisar, use 'Verificar integridade dos arquivos' no Steam.")
        return

    if not os.path.exists(TEXTOS):
        print(f"Faltando o arquivo de textos: {TEXTOS}")
        print("Ele deve estar na mesma pasta que este script.")
        sys.exit(1)

    try:
        import UnityPy
    except ImportError:
        print("Falta a biblioteca UnityPy. Instale com:")
        print("   pip install UnityPy")
        sys.exit(1)

    if not os.path.exists(backup):
        print("fazendo copia de seguranca (pode demorar, sao ~780 MB)...")
        shutil.copy2(asset, backup)
        print(f"   guardada em {os.path.basename(backup)}")
    else:
        print("copia de seguranca ja existe — preservada")

    textos = json.load(open(TEXTOS, encoding="utf-8"))
    por_pid = {int(pid): rec for pid, rec in textos.items()}

    print("\nlendo os arquivos do jogo...")
    env = UnityPy.load(asset)
    trocados = 0
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        rec = por_pid.get(obj.path_id)
        if not rec:
            continue
        dados = obj.read()
        if getattr(dados, "m_Name", None) != rec["name"]:
            continue
        # O BOM precisa voltar: TODOS os arquivos de texto do jogo comecam
        # com ele, e o leitor do jogo conta com isso para a primeira chave.
        dados.m_Script = "﻿" + rec["text"]
        dados.save()
        trocados += 1

    if trocados == 0:
        print("\nNenhum texto foi trocado. Provavelmente esta e uma versao do")
        print("jogo diferente da que a traducao usa. Nada foi alterado.")
        sys.exit(1)

    print(f"textos traduzidos: {trocados}")
    print("\ngravando (reescreve ~780 MB, leva um tempo)...")
    temporario = asset + ".novo"
    with open(temporario, "wb") as fh:
        fh.write(env.file.save())
    shutil.move(temporario, asset)

    print("\nPRONTO. Abra o jogo — ele deve estar em portugues.")
    print("Para desfazer:  python aplicar_traducao.py --restaurar")


if __name__ == "__main__":
    main()
