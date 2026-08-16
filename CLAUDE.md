# Instruções do projeto — Pathologic 3

Tradução completa, **já publicada** no Nexus. Não é projeto novo: qualquer mudança aqui
mexe em algo que gente está usando. Versão nova, nunca troca de arquivo.

## A base é o russo

O jogo foi escrito em russo, e é de lá que a tradução sai. O inglês fica por perto para
desambiguar, mas partir dele seria herdar as escolhas da localização inglesa em vez de
decidir as nossas.

## Os dois portões

```
python tools/enforce_glossary.py   # aplica o lock retroativamente
python tools/qa_check.py           # falha o build se a deriva voltar
```

O `qa_check.py` verifica deriva de terminologia contra `research/glossario.lock.tsv`,
marcação `<i>` perdida e `\n`/`\t` divergentes, que quebram o layout das caixas.

O `research/glossario.lock.tsv` é **normativo**, com 127 linhas e uma coluna de
`proibidos`. Ele não é sugestão: `enforce_glossary.py` sobrescreve o que contraria. Antes
de propor termo novo, leia o lock — várias decisões estão marcadas "ALINHADO AO PATHOLOGIC
2 pt-BR", ou seja, casadas de propósito com a tradução publicada do jogo anterior.

**O gatilho do enforce é sempre o russo de origem, nunca o português.** Isso evita
corromper homógrafos: «железные коробки» são caixas literais, não o Короб.

## O que não é mecânico

Ver [`../AGENTS.md`](../AGENTS.md). Os canais de dúvida são `PENDENCIAS.md` e
`DIVERGENCIAS.md` — aqui a divergência que importa é russo × inglês.

## Regras deste projeto

- `extracted/` é o roteiro deles, ~200 MB. **Nunca** versionar.
- `resources.assets` e derivados são arquivo do jogo. Nunca versionar.
- A arte de capa pertence à Ice-Pick Lodge. Há imagens dela ainda no histórico público —
  o `.gitignore` de hoje já as proíbe, mas a regra não alcança o passado.
- A tradução do Pathologic 2 do Yuri Beira é trabalho de outra pessoa, usado só como
  referência de terminologia. Nunca redistribuir.
