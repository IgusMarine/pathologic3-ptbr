# Pathologic 3 — Tradução PT-BR

Tradução e localização completas de **Pathologic 3** (Мор) para português
brasileiro. Feita por fã, sem vínculo com a Ice-Pick Lodge ou a Hypetrain
Digital.

**63.703 falas — o jogo inteiro**, incluindo os interrogatórios que
emolduram a história e as entrevistas de paciente do hospital.

---

## Instalação

Baixe o instalador na [aba Releases](../../releases) e dê dois cliques.
Não precisa de Python nem de nada instalado — está tudo dentro do programa.

Ele acha o jogo sozinho, guarda uma cópia de segurança antes de mexer em
qualquer coisa, e tem um botão para desfazer.

A instalação leva alguns minutos: ela reescreve um arquivo de 780 MB do
jogo. A barra fica um bom tempo na última etapa — é normal.

### Se o antivírus reclamar

Acontece: executável feito com PyInstaller dispara falso positivo com
frequência. O pacote traz uma pasta `modo-manual` com um script de linha de
comando que faz exatamente a mesma coisa:

```bash
pip install UnityPy
python aplicar_traducao.py
```

Para desfazer, `python aplicar_traducao.py --restaurar`.

---

## O que esta tradução tem de diferente

O critério foi que ninguém devesse perceber que passou por máquina. Isso
significou algumas decisões que valem explicar:

**O russo é a fonte, não o inglês.** A localização inglesa toma liberdades e
às vezes erra — ela traduz «Почка» (rim) como *Spleen* (baço), e troca o
esquilo «Белка» por *shrew*, o que quebra uma piada sobre nozes. Onde o
inglês e o russo discordam, vale o russo.

**Nome inglês não passa.** Apelido de bicho ou descritivo vira nome
brasileiro, nunca transliteração crua nem o nome que o inglês inventou:

| russo | significa | inglês fez | aqui |
|---|---|---|---|
| `Гриф` | abutre | Bad Grief | **o Abutre** |
| `Уклад` | ordem, modo de vida | the Kin | **a Estirpe** |
| `Ласка` | carinho, doninha | Grace | **Graça** |
| `Гаруспик` | adivinho de vísceras | Haruspex | **o Arúspice** |
| `Спичка` | fósforo | Sticky | **o Fósforo** |
| `Белка` | esquilo | Shrew | **Serelepe** |

**O tratamento segue o russo.** O original distingue `ты` de `вы`, e isso
decide entre "você" e "o senhor" — critério objetivo, não gosto.

**Português brasileiro de verdade.** Sem "tu" nem mesóclise; interjeição
inglesa vira equivalente daqui (`тьфу` → *credo*, `Бр-р` → *brr*, não *ugh*).
Onde o registro é elevado de propósito — uma citação de Hamlet, uma carta
formal, uma reza — a forma arcaica fica.

---

## Como o projeto funciona

O texto do jogo vive dentro de `resources.assets`, num formato próprio:
cada arquivo é uma lista de `{Chave} valor`, um registro por linha. Quebra
de linha real separa registros; quebra de parágrafo dentro de um valor é o
escape literal `\n`. Confundir os dois quebra o jogo — foi o que apagou a
legenda da cutscene de abertura até descobrirmos.

```
tools/extract_texts.py    tira os textos do jogo (precisa do jogo instalado)
tools/build_workbook.py   monta extracted/workbook.json com ru + en + pt
tools/export_batch.py     gera lotes para traduzir
tools/enforce_glossary.py aplica o glossário sobre o corpus
tools/qa_check.py         portão de qualidade — roda sozinho no build
tools/apply_pt.py         compila translated/pt/*.tsv no pacote final
tools/inject_pt.py        injeta no jogo
```

O único formato que importa saber: `translated/pt/*.tsv` é `id` + uma
tabulação + o texto em português. `\n` e `\t` dentro do texto são os dois
caracteres literais, nunca quebra de linha de verdade.

### O glossário manda

`research/glossario.lock.tsv` é normativo, com 105 termos. Cada linha tem o
termo obrigatório, o gênero, um **regex do russo de origem**, e a lista de
formas proibidas.

O gatilho é o russo, nunca o português — isso evita corromper substantivo
comum homógrafo. E a troca só acontece se as **duas** chaves baterem: o
russo casa o gatilho **e** a forma proibida está no português. Assim um
gatilho errado não estraga nada, só deixa de agir.

`tools/qa_check.py` roda no build e barra: desvio de glossário, aspas retas,
escape `\t` divergente, campo extra, placeholder de jogo alterado, id
duplicado com traduções diferentes, e pacote compilado desatualizado.

---

## O que NÃO está aqui

Este repositório tem só o que é nosso. Não há nenhum arquivo do jogo.

- `extracted/` — o roteiro original nos três idiomas (~200 MB). Regenere com
  `tools/extract_texts.py`, a partir da sua cópia do jogo.
- a arte de capa do instalador — é da Ice-Pick Lodge. Ponha a sua em
  `installer/capa_original.png` e rode `installer/gerar_arte.py`.
- `translated/ptbr_final.json` — o pacote compilado. Sai de `apply_pt.py`, e
  vai como anexo de Release.

---

## Contribuir

Achou algo? O que mais ajuda não é erro de português, é o que a tela mostra:
texto estourando a caixa, botão que não cabe, fala fora de lugar na
conversa, nome que muda de uma cena para outra.

Anote **dia do jogo, personagem e cena** — com isso dá para achar a linha
exata. Abra uma issue.

---

## Créditos

Tradução e localização: **Igor**
Jogo: **Ice-Pick Lodge** / **Hypetrain Digital**

Tradução feita por fã, sem fins lucrativos e sem vínculo com os
desenvolvedores ou a distribuidora. Distribua apenas o pacote de tradução —
nunca os arquivos do jogo.
