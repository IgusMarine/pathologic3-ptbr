# -*- coding: utf-8 -*-
"""Empacota o instalador grafico com cx_Freeze.

Por que cx_Freeze e nao PyInstaller: o PyInstaller monta um executavel que se
autoextrai em tempo de execucao, e esse comportamento e' assinatura conhecida
de packer — heuristicas de antivirus marcam por principio. O cx_Freeze gera um
lancador pequeno com o Python e as bibliotecas soltos em lib/, nada embutido,
nada autoextraido.

Pos-build obrigatorio: rodar ci_pos_build.py para desfazer o lib/library.zip
(arquivo compactado dentro de arquivo compactado e' quarentena automatica no
Nexus Mods).

Uso:  python setup_build.py build
"""
from cx_Freeze import setup, Executable

opcoes_build = {
    # Pacotes copiados inteiros, com os arquivos de dados de cada um.
    "packages": [
        "customtkinter",   # o tema .json e os assets ficam junto
        "PIL",
        "UnityPy",
        "tkinter",
        "json",
    ],
    # Imports que a analise estatica nao enxerga.
    "includes": [
        "PIL._tkinter_finder",
        "tkinter.filedialog",
        "tkinter.messagebox",
    ],
    # Dados ao lado do .exe. O recurso() do instalador procura na pasta do
    # executavel quando esta congelado. Estes tres arquivos NAO vivem no
    # repositorio (arte do jogo e traducao compilada): o CI os extrai da
    # Release publicada antes de compilar — ver ci_extrair_dados.py.
    "include_files": [
        ("arte.png", "arte.png"),
        ("icone.ico", "icone.ico"),
        ("ptbr_final.json", "ptbr_final.json"),
    ],
    # Peso morto.
    "excludes": [
        "test", "unittest", "pydoc_data", "lib2to3", "idlelib",
        "pip", "setuptools", "wheel", "distutils",
        "matplotlib", "scipy", "pandas", "IPython", "pytest",
    ],
    # Tudo em forma de arquivo dentro de lib/, nada zipado: menos parecido
    # com um packer, mais parecido com um programa comum.
    "zip_include_packages": [],
    "zip_exclude_packages": ["*"],
    "build_exe": "build/instalador",
    "include_msvcr": True,
    "optimize": 0,
    "silent_level": 1,
}

setup(
    name="Instalar-Traducao-PTBR",
    version="1.0.0",
    description="Instalador da traducao PT-BR de Pathologic 3",
    author="Igor",
    options={"build_exe": opcoes_build},
    executables=[Executable(
        script="instalador.py",
        base="gui",                       # sem janela de console
        target_name="Instalar-Traducao-PTBR.exe",
        icon="icone.ico",
        copyright="Traducao feita por fa. Sem fins lucrativos.",
        trademarks="Pathologic 3 (c) Ice-Pick Lodge",
    )],
)
