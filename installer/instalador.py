# -*- coding: utf-8 -*-
"""Instalador da traducao pt-BR de Pathologic 3.

Faz o mesmo que o aplicar_traducao.py de linha de comando, mas com janela:
acha o jogo sozinho, mostra o que esta fazendo, e da' progresso de verdade —
a operacao reescreve um arquivo de 780 MB e leva minutos, e ficar em silencio
esse tempo todo parece travamento.

Uso em desenvolvimento:  python instalador.py
Empacotado:              Instalar-Traducao-PTBR.exe
"""
import os, sys, json, shutil, threading, subprocess, traceback
import customtkinter as ctk
from PIL import Image

# ---------------------------------------------------------------- recursos --
def recurso(nome):
    """Caminho de um arquivo empacotado — funciona solto e dentro do .exe."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, nome)


COR_FUNDO = "#141112"
COR_PAINEL = "#1b1719"
COR_TEXTO = "#e8e0d4"
COR_FRACO = "#9d9088"
COR_ACAO = "#8c3a24"
COR_ACAO_HOVER = "#a5462c"
COR_OK = "#4e7a4a"
COR_ERRO = "#a33b3b"

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
    tentativas = ([manual] if manual else []) + list(CAMINHOS)
    vdf = r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
    if os.path.exists(vdf):
        try:
            for linha in open(vdf, encoding="utf-8", errors="ignore"):
                if '"path"' in linha:
                    base = linha.split('"')[3].replace("\\\\", "\\")
                    tentativas.append(os.path.join(base, "steamapps", "common", "Pathologic 3"))
        except Exception:
            pass
    for base in tentativas:
        if not base:
            continue
        for alvo in (os.path.join(base, "Pathologic3_Data", "resources.assets"),
                     os.path.join(base, "resources.assets")):
            if os.path.exists(alvo):
                return alvo
    return None


# ------------------------------------------------------------------ janela --
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pathologic 3 — Instalar Tradução")
        self.geometry("1180x820")
        self.resizable(False, False)
        self.configure(fg_color=COR_FUNDO)
        try:
            self.iconbitmap(recurso("icone.ico"))
        except Exception:
            pass

        self.asset = achar_jogo()
        self.trabalhando = False

        # -------- painel esquerdo: a arte
        try:
            arte = Image.open(recurso("arte.png"))
            self.img = ctk.CTkImage(light_image=arte, dark_image=arte, size=(600, 820))
            ctk.CTkLabel(self, image=self.img, text="").place(x=0, y=0)
        except Exception:
            ctk.CTkFrame(self, width=600, height=820, fg_color="#241a18").place(x=0, y=0)

        # -------- painel direito
        p = ctk.CTkFrame(self, width=580, height=820, fg_color=COR_PAINEL, corner_radius=0)
        p.place(x=600, y=0)
        p.pack_propagate(False)

        ctk.CTkLabel(p, text="Pathologic 3", font=("Georgia", 42, "bold"),
                     text_color=COR_TEXTO).pack(anchor="w", padx=46, pady=(78, 0))
        ctk.CTkLabel(p, text="em português brasileiro", font=("Georgia", 30, "italic"),
                     text_color="#c9865f").pack(anchor="w", padx=46, pady=(2, 30))

        abre = ctk.CTkFrame(p, fg_color="transparent")
        abre.pack(anchor="w", padx=44, fill="x", pady=(0, 20))
        # Nada de "do prologo ao decimo segundo dia": os arquivos do dia 12
        # sao Final e VillainSpeech — dizer onde a historia termina e' spoiler,
        # e o primeiro item da lista ja' garante que esta completo.
        ctk.CTkLabel(abre, width=490, justify="left", wraplength=490, anchor="w",
                     font=("Segoe UI", 16), text_color="#b9aca2",
                     text="A cidade inteira em português — cada fala, cada "
                          "anotação, cada tela.").pack(anchor="w")

        for forte, resto in [
            ("63.703 falas",        "o jogo todo, sem sobra em inglês"),
            ("Traduzida do russo",  "direto do original, sem intermediário"),
            ("Nomes em português",  "nada de apelido deixado em inglês"),
            ("«o senhor» e «você»", "seguem a distinção do original"),
            ("105 termos travados", "o mesmo nome do começo ao fim"),
        ]:
            li = ctk.CTkFrame(p, fg_color="transparent")
            li.pack(anchor="w", padx=44, fill="x", pady=4)
            ctk.CTkLabel(li, text="✓", font=("Segoe UI", 17, "bold"),
                         text_color="#c9865f", width=26, anchor="w").pack(side="left")
            ctk.CTkLabel(li, text=forte, font=("Segoe UI", 15, "bold"),
                         text_color=COR_TEXTO, anchor="w").pack(side="left")
            ctk.CTkLabel(li, text=f"  ·  {resto}", font=("Segoe UI", 15),
                         text_color=COR_FRACO, anchor="w").pack(side="left")

        seg = ctk.CTkFrame(p, fg_color="transparent")
        seg.pack(anchor="w", padx=44, fill="x", pady=(22, 0))
        ctk.CTkLabel(seg, text="↺", font=("Segoe UI Symbol", 21),
                     text_color="#87977f", width=26, anchor="w").pack(side="left", anchor="n")
        ctk.CTkLabel(seg, width=448, justify="left", wraplength=448, anchor="w",
                     font=("Segoe UI", 14), text_color="#8b8078",
                     text="Guarda uma cópia de segurança antes de mexer em nada. "
                          "Dá para desfazer a qualquer momento.").pack(side="left")

        # -------- onde esta o jogo
        ctk.CTkLabel(p, text="PASTA DO JOGO", font=("Segoe UI", 13, "bold"),
                     text_color="#6f645e").pack(anchor="w", padx=46, pady=(34, 8))
        cx = ctk.CTkFrame(p, fg_color="#221d1f", corner_radius=8)
        cx.pack(padx=46, fill="x")
        self.lbl_path = ctk.CTkLabel(
            cx, width=360, justify="left", anchor="w", font=("Consolas", 12),
            text_color=COR_TEXTO if self.asset else "#c98a6a",
            text=self._texto_caminho())
        self.lbl_path.pack(side="left", padx=13, pady=13)
        ctk.CTkButton(cx, text="Procurar", width=100, height=33, corner_radius=6,
                      fg_color="#332b2d", hover_color="#41373a",
                      font=("Segoe UI", 14), command=self.procurar).pack(side="right", padx=10)

        # -------- progresso
        self.barra = ctk.CTkProgressBar(p, width=488, height=8, corner_radius=4,
                                        progress_color=COR_ACAO, fg_color="#2a2325")
        self.barra.set(0)
        self.lbl_status = ctk.CTkLabel(p, text="", font=("Segoe UI", 15),
                                       text_color=COR_FRACO, wraplength=490, justify="left")

        # -------- acoes
        self.btn = ctk.CTkButton(
            p, text="Instalar tradução", width=488, height=58, corner_radius=10,
            font=("Segoe UI", 20, "bold"), fg_color=COR_ACAO, hover_color=COR_ACAO_HOVER,
            command=self.instalar)
        self.btn.pack(side="bottom", padx=46, pady=(0, 30))
        self.btn_restaurar = ctk.CTkButton(
            p, text="Restaurar o original", width=488, height=42, corner_radius=8,
            font=("Segoe UI", 15), fg_color="transparent", border_width=1,
            border_color="#3d3336", text_color=COR_FRACO, hover_color="#262022",
            command=self.restaurar)
        self.btn_restaurar.pack(side="bottom", padx=46, pady=(0, 10))
        self.lbl_status.pack(side="bottom", padx=46, pady=(0, 12), anchor="w")
        self.barra.pack(side="bottom", padx=46, pady=(0, 10))
        self.barra.pack_forget()

        if not self.asset:
            self.btn.configure(state="disabled", fg_color="#3a3033")
            self.status("Não encontrei o jogo. Use «Procurar» e aponte a pasta "
                        "que contém Pathologic3_Data.", COR_FRACO)

    # ------------------------------------------------------------- auxiliar --
    def _texto_caminho(self):
        if not self.asset:
            return "não encontrado"
        p = os.path.dirname(os.path.dirname(self.asset))
        return p if len(p) <= 52 else "…" + p[-51:]

    def status(self, txt, cor=COR_FRACO):
        self.lbl_status.configure(text=txt, text_color=cor)
        self.update_idletasks()

    def procurar(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(title="Onde o Pathologic 3 está instalado?")
        if not d:
            return
        a = achar_jogo(d)
        if a:
            self.asset = a
            self.lbl_path.configure(text=self._texto_caminho(), text_color=COR_TEXTO)
            self.btn.configure(state="normal", fg_color=COR_ACAO)
            self.status("Jogo encontrado.", COR_OK)
        else:
            self.status("Não achei resources.assets aí. A pasta certa é a que "
                        "contém Pathologic3_Data.", COR_ERRO)

    def travar(self, travado):
        self.trabalhando = travado
        e = "disabled" if travado else "normal"
        self.btn.configure(state=e)
        self.btn_restaurar.configure(state=e)

    # ------------------------------------------------------------- acoes -----
    def instalar(self):
        if self.trabalhando or not self.asset:
            return
        self.travar(True)
        self.barra.pack(side="bottom", padx=46, pady=(0, 10), before=self.lbl_status)
        self.barra.set(0)
        threading.Thread(target=self._trabalho, daemon=True).start()

    def restaurar(self):
        if self.trabalhando or not self.asset:
            return
        bak = self.asset + ".bak"
        if not os.path.exists(bak):
            self.status("Não há cópia de segurança. Use «Verificar integridade "
                        "dos arquivos» no Steam para voltar ao original.", COR_ERRO)
            return
        self.travar(True)
        self.status("Restaurando o original…")
        try:
            shutil.copy2(bak, self.asset)
            self.status("Original restaurado. O jogo voltou ao idioma de antes.", COR_OK)
        except Exception as e:
            self.status(f"Não consegui restaurar: {e}", COR_ERRO)
        self.travar(False)

    def _trabalho(self):
        try:
            self._aplicar()
        except PermissionError:
            self.status("Sem permissão para escrever na pasta do jogo. Feche o "
                        "jogo e o Steam, ou rode este instalador como "
                        "administrador.", COR_ERRO)
        except Exception as e:
            traceback.print_exc()
            self.status(f"Deu errado: {e}", COR_ERRO)
        finally:
            self.travar(False)

    def _aplicar(self):
        import UnityPy
        bak = self.asset + ".bak"

        if not os.path.exists(bak):
            self.status("Fazendo cópia de segurança (780 MB)…")
            self.barra.set(0.05)
            shutil.copy2(self.asset, bak)
        else:
            self.status("Cópia de segurança já existe — preservada.")
        self.barra.set(0.15)

        self.status("Lendo os arquivos do jogo… (demora um pouco)")
        textos = json.load(open(recurso("ptbr_final.json"), encoding="utf-8"))
        por_pid = {int(pid): rec for pid, rec in textos.items()}
        env = UnityPy.load(self.asset)
        self.barra.set(0.35)

        trocados = 0
        alvo = len(por_pid)
        for obj in env.objects:
            if obj.type.name != "TextAsset":
                continue
            rec = por_pid.get(obj.path_id)
            if not rec:
                continue
            dados = obj.read()
            if getattr(dados, "m_Name", None) != rec["name"]:
                continue
            dados.m_Script = "\ufeff" + rec["text"]   # o BOM precisa voltar
            dados.save()
            trocados += 1
            if trocados % 400 == 0:
                self.barra.set(0.35 + 0.30 * trocados / alvo)
                self.status(f"Aplicando os textos…  {trocados} de {alvo}")

        if trocados == 0:
            self.status("Nenhum texto foi trocado — esta versão do jogo é "
                        "diferente da que a tradução usa. Nada foi alterado.",
                        COR_ERRO)
            self.barra.pack_forget()
            return

        self.barra.set(0.68)
        self.status(f"{trocados} textos aplicados. Gravando os 780 MB — "
                    "esta é a parte demorada, pode levar alguns minutos.")
        tmp = self.asset + ".novo"
        with open(tmp, "wb") as fh:
            fh.write(env.file.save())
        self.barra.set(0.94)
        self.status("Finalizando…")
        shutil.move(tmp, self.asset)

        self.barra.set(1.0)
        self.status(f"Pronto. {trocados} textos traduzidos — pode abrir o jogo.\n"
                    "Se algo der errado, use «Restaurar o original».", COR_OK)
        self.btn.configure(text="Instalado ✓", fg_color=COR_OK)


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    App().mainloop()
