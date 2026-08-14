# Publicar no Nexus Mods

Página do jogo: **https://www.nexusmods.com/games/pathologic3**
Botão `Upload a mod` no topo.

Já existe uma tradução PT-BR lá (mod 16), com 70% da interface e 95% dos
diálogos. A sua está em 100%, então o número é o argumento. Não vale atacar
a outra: quem compara decide sozinho.

---

## O que está pronto nesta pasta

| arquivo | para onde vai |
|---|---|
| `DESCRICAO.bbcode.txt` | copiar e colar no campo **Description** |
| `imagem-principal.jpg` | a imagem principal do mod (1920x1080) |
| `captura-instalador.png` | screenshot da aba **Images** |
| `../Pathologic3-Traducao-PTBR-Instalador.zip` | o arquivo do mod |

---

## Preenchendo o formulário

**Mod name**
```
Traducao PT-BR completa (Complete Brazilian Portuguese)
```

Atenção: o campo só aceita letras sem acento, números, espaço e `_ ' ( ) . -`
Por isso "Traducao" vai sem cedilha. É a convenção no Nexus, e brasileiro lê
sem estranhar (o outro mod PT-BR de lá se chama "Tradutor" justamente porque
essa palavra não tem acento).

`completa` é o que diferencia do mod que já existe. O trecho em inglês faz
aparecer para quem busca sem falar português.

Se preferir não mutilar a palavra, esta alternativa é toda sem acento e não
parece errada:
```
Complete Brazilian Portuguese Translation (PT-BR)
```

**Summary** (aparece na listagem, é o que decide o clique)
```
Tradução completa para português brasileiro: 63.703 falas, o jogo inteiro.
Feita a partir do russo original, com instalador de um clique e reversível
a qualquer momento.
```

**Category**
`Translations` se existir. Se não, `Miscellaneous`.

**Version**
```
1.0
```

**Description**
Cole o conteúdo de `DESCRICAO.bbcode.txt`. Já está em BBCode, que é o formato
que o Nexus usa. Não é Markdown, então não converta nada.

---

## A marcação de IA é obrigatória

O Nexus exige que mod feito com ajuda de inteligência artificial seja marcado,
e quem não marca sofre moderação. Na hora do upload existe uma seção sobre
conteúdo gerado por IA. Marque, e escolha a opção que descreve **texto ou
tradução**, não voz nem imagem.

Se a interface pedir uma explicação, esta serve:

```
Tradução de texto feita com auxílio de IA, a partir do roteiro em russo do
próprio jogo. Nenhum asset do jogo foi gerado: não há voz sintetizada, arte
gerada nem modelo novo. O texto passou por glossário fixo de 105 termos e
por várias passagens de revisão.
```

Isso é verdade e evita o mal-entendido mais comum, que é achar que houve
dublagem ou arte de IA.

---

## Tags sugeridas

```
Translation, Portuguese, Brazilian Portuguese, Localization, Text, PT-BR
```

---

## Requirements

Nenhum mod exigido. Vale registrar no campo de requisitos, ou deixar claro na
descrição, que é preciso ter o jogo instalado e fechado durante a instalação.

---

## Permissions

Decisão sua. O mais comum em tradução de fã:

- **Redistribuir sem autorização:** não
- **Usar como base para outro mod:** perguntar antes
- **Conversão para outro jogo:** não
- **Uso comercial:** não

O motivo de não liberar redistribuição não é ciúme do trabalho: é que versão
antiga circulando por aí gera relato de erro que você já corrigiu.

---

## Antes de clicar em publicar

- [ ] O arquivo enviado é o `.zip`, não o `.exe` solto
- [ ] A marcação de IA está preenchida
- [ ] A imagem principal subiu e aparece na prévia
- [ ] A descrição não ficou com BBCode quebrado (confira a prévia)
- [ ] O aviso do SmartScreen está mencionado, para não virar dez comentários
      perguntando se é vírus

---

## Depois de publicar

**Tire screenshots do jogo traduzido e suba na aba Images.** É o que mais
convence, e é o que falta aqui: eu só consegui gerar a imagem de divulgação e
a captura do instalador. Uma tela de diálogo e uma do prontuário do hospital
já mudam muito a impressão de quem chega.

**A primeira semana traz os relatos que importam.** Texto estourando caixa,
botão que não cabe, nome trocado. Anote tudo e mande para cá que a gente
corrige e sobe a 1.1.

---

## Arquivo opcional: o arquivo pronto (copiar e substituir)

Sobe na aba **Files** do mod já publicado, como arquivo adicional — o script
continua sendo o principal.

| campo | valor |
|---|---|
| File name | `Arquivo pronto - copiar e substituir (13-08-2026)` |
| File version | `1.0` |
| Category | **Optional files** |
| Arquivo | `Pathologic3-Traducao-PTBR-Arquivo-Pronto.zip` (396 MB) |

**File description** (o campo aceita 255 caracteres; este tem 254):

```
Para quem não quer usar Python: o arquivo de textos do jogo já traduzido, só copiar e substituir (instruções no LEIA-ME). Vale para a versão do jogo de 13/08/2026. Se o jogo atualizou depois, não use — baixe o script, que confere a versão antes de mexer.
```

**Changelog** (se o formulário pedir):

```
Primeira versão do arquivo pronto. Mesma tradução 1.0 do script, já aplicada; corresponde ao jogo de 13/08/2026.
```

**Marque "Remove the 'Download with manager' button"**: este arquivo é para
colocar na pasta na mão; o Vortex não saberia onde pôr e instalaria errado.

**Depois do upload, atualize o campo Description da página** com o
`DESCRICAO.bbcode.txt` desta pasta — ele já apresenta os dois jeitos de
instalar e explica por que um download é pequeno e o outro é grande.

**A cada atualização do jogo**: gerar o arquivo de novo (`tools/apply_pt.py`
+ `tools/inject_pt.py`), zipar com o LEIA-ME atualizado, subir como novo
arquivo opcional com a data nova no nome e mandar o antigo para
**Old files**. A data no nome é o que evita usuário aplicando arquivo velho
em jogo novo.
