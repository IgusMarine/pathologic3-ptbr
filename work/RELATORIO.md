# Relatório de trabalho — localização pt-BR de Pathologic 3

> Arquivo atualizado a cada etapa. Se você acabou de acordar, é o único
> que precisa abrir.

## Status

| | |
|---|---|
| Traduzido | **61.242 / 61.242 (100%)** |
| Em inglês na tela | 0 |
| Em russo na tela | 0 |
| Portão | limpo |

## Plano

1. ✅ Diálogo restante — 4.834 linhas
2. ✅ Interface — 1.008 linhas
3. ✅ Auditoria de alinhamento — **4 cenas embaralhadas encontradas e reparadas**
4. ✅ Auditoria de nomes — 7 nomes partidos, unificados
5. ✅ Interjeições inglesas — 34 trocadas por equivalente pt-BR
6. ⏸ Verificação dos 492 achados pendentes da revisão do Hospital
7. ⏸ Itálicos restantes (118, quase todos sem portador natural em pt-BR)

## Interjeições inglesas trocadas

Vazaram do texto-fonte. A troca foi por **origem russa**, não em bloco —
cada uma pede coisa diferente:

| russo | era | ficou |
|---|---|---|
| «тьфу» (cuspe de desprezo) | ugh / pah | **bah** |
| «бр-р» (arrepio) | ugh | **brr** |
| «н-да» (resmungo) | huh | **pois é** |
| «ну-ну» (ceticismo) | huh | **sei, sei** |
| «ух,» | Ugh | **ui** |
| «ба!» | Ugh | **ora** |

6 linhas ficaram intactas: o russo não traz interjeição identificável, e
trocar seria chute. Estão listadas pelo `qa_check`.

## ACHADO GRAVE — traduções presas ao id errado

Quatro cenas tinham o texto português **preso aos ids errados**: o personagem
diria a fala de outro momento da conversa. Defeito herdado, anterior a esta
sessão.

| cena | linhas | deslocamento |
|---|---|---|
| Day8_Q17.1_Caretaker_StillStillwater | 66 | 19 linhas |
| Eva_Evening_02 | 55 | 2 |
| Day3_Q10_Andrey_WhereIsBrother | 52 | 1 |
| SuicideMP_Test_2 | 12 | 5 |

Encontrado assim: uma linha cujo russo era latim («Voluntas est superior
intellectu») tinha português que não era latim. Isso levou ao detector
estatístico em `tools/auditar_desalinhamento.py`, que compara o comprimento
das falas — numa cena alinhada, fala curta vira fala curta.

As 224 linhas foram retraduzidas do russo. Reauditoria: **zero cenas
desalinhadas** em 894 analisadas.

## Outro achado: placeholders do jogo traduzidos

`62137.5` e `62137.6` tinham `<day>.<month>.<year>` traduzido para
`<dia>.<mês>.<ano>`. São variáveis que o jogo substitui em execução —
traduzidas, ele mostraria `<dia>` literal na tela. Corrigido, e o portão
agora bloqueia isso.

## O que NÃO farei sem autorização

- `tools/inject_pt.py` — escreve dentro da instalação do jogo no Steam.
  Único passo irreversível e voltado para fora.

## Decisões tomadas sem consulta (regras já fixadas pelo usuário)

- Nome vindo da versão inglesa → transliteração, sempre
- Apelido descritivo → tradução que soe brasileira
- Deriva de glossário, aspas, campo extra → correção automática
- Itálico → colocado onde a ênfase do inglês manda
- Tratamento oscilando na mesma cena → conferido no russo, unificado pela maioria

## Decisões deixadas para o usuário

*(nenhuma pendente no momento)*

## Histórico de correções desta sessão

### Terminologia unificada

| russo | ficou | linhas | era |
|---|---|---|---|
| Пётр | **Pyotr** | 272 | Peter (forma inglesa) |
| Точечка | **Pontinho** | 20 | Tochinha / "Little" |
| Бурдук | **Burduk** | 6 | Burdock (inglês) |
| Ципух | **Tsipukh** | 15 | Tsipuch |
| Черняк | **Chernyak** | 5 | "Corvo" (invenção) |
| Щур | **o Tentilhão** | 8 | Finch / Shchur |
| Воронок | **o Corvinho** | 5 | Martin (inglês) |
| Мандаринка | **a Mandarina** | 3 | Clementine (inglês) |
| Тяжёлый Влад | **Vladão** | 12 | "Vlad, o Gordo" |
| Ласка | **Grace** | 14 | Graça |
| Стержень | **o Eixo** | 8 | Cetro |
| Короб | **o Cortiço** | 6 | Covil / Caixa |
| Гора | **Rocha** | 5 | Boulder |
| эчеленца | **eccellenza** | 39 | excelência |
| Луток | **Lutok** | 2 | Luntok |

### Outras

- 253 itálicos recolocados à mão
- 422 + 199 linhas com o nome da cena vazando, reparadas
- Tratamento do Inspetor unificado em "o senhor" (40 linhas)
- 11 formas de português de Portugal corrigidas
- Aspas normalizadas para `«»`

## Bugs corrigidos nas ferramentas

Registrados porque afetam a confiabilidade do que já rodou:

- `--simular` gravava arquivos falsos no corpus
- Regex de troca casava dentro de palavra ("para o Baço" → "parao Rim")
- Tab real gravado no lugar do escape `\t` (quebra o TSV)
- Soma de tokens estourava com campo aninhado
- Validador não conferia contagem de campos (422 linhas passaram)
- Nomeador de arquivo travava em 26 fatias
- Portão acusava citação aninhada `«… „x“ …»`, que é correta

## Barra superior e apelidos infantis

**A sobreposição do relógio.** A barra de abas foi desenhada para caber o
russo. Medindo: RU 55 caracteres, EN 56, PT **68** — treze a mais, e por
isso o relógio era empurrado para cima do botão. Dois cortes:

| aba | antes | agora | motivo |
|---|---|---|---|
| МЫСЛИ | PENSAMENTOS (11) | **MENTE** (5) | a aba abre o mapa mental; o russo tem 5 letras |
| ПЛАНШЕТ | PRONTUÁRIO (10) | **FICHÁRIO** (8) | mantém o tom médico, cabe melhor |
| ЗАПИСКИ | ANOTAÇÕES (9) | **NOTAS** (5) | feito antes |

Total agora: **60**, contra 56 do inglês. As duas que ainda passam
(PESSOAS +3, COISAS +2) esbarram em palavras russas curtíssimas
(ЛЮДИ, ВЕЩИ) e não têm forma menor decente em português.

**«Карта мыслей»** aparecia como *Mapa de pensamentos* em três lugares e
*Mapa Mental* num quarto. Unificado em **Mapa mental** — é o termo
corrente em pt-BR e ainda economiza 8 caracteres na notificação.

**Duas crianças fora do sistema de apelidos.** O glossário já mandava
traduzir apelido de bicho (a Mandarina, o Corvinho, o Tentilhão, a
Gralha, o Andorinhão). Faltavam duas:

- **Спичка** estava como *"Sticky"* em 31 linhas, forma da versão inglesa.
  Agora **o Fósforo**, que é o que a palavra quer dizer e o que outras
  linhas já usavam. O item "caixa de fósforos" usa a mesma palavra no
  russo de propósito: o menino tem o nome do objeto, e isso se preserva.
- **Белка** (esquilo) oscilava entre *"Belka"* e *"Musaranho"*. O inglês
  usa *shrew*; com o esquilo a piada da noz fecha. Agora **Serelepe**
  — nome brasileiro do esquilo, e também criança inquieta.

Ambos travados no glossário, com varredura de duas chaves.

**Dois erros de conteúdo achados no caminho:**

- `6191.54` — o russo pergunta «А Спичка где?» (*cadê o Spichka?*). A
  linha dizia **"E a Grace, cadê?"**: personagem errada.
- `60282.1` — «Не давай белке орехов», гласит пословица é um provérbio.
  Tinha virado a pergunta *"Musaranho come noz, é?"*, com o bicho que não
  come noz. Agora: *«Não dê nozes a serelepe», diz o ditado.*

## Auditoria de colisao de nomes (workflow com 6 agentes)

Depois de achar a corrupcao dos caracteres ⇥ e o erro da Grace, a pergunta
"sera' que nao temos mais problemas graves como esse" levou a uma varredura
sistematica: comparamos, para cada nome russo curto e solto (placa, ficha,
retrato, apelido), quantas formas distintas em portugues ele tinha. Achamos
153 grupos com mais de uma forma — a maioria rotulo de sistema (19), o
resto nome de lugar/comodo/cargo (136). Rodamos um workflow de 6 agentes:
4 investigando em paralelo, 1 revisando o lote inteiro contra o estado real
dos arquivos antes de aprovar, 1 aplicando e rodando o portao de qualidade.

**Resultado: 267 patches manuais + 50 capturados pela varredura automatica
do glossario apos travar os termos novos = 317 linhas corrigidas em 143
arquivos.** Zero pulados por desatualizacao (o revisor conferiu byte a byte
antes de aprovar).

### Colisao de apelido de crianca/paciente (quatro personagens viravam "Gralha")

Quatro palavras russas diferentes — Сойка, Галка, Лунь, Грач — estavam
todas traduzidas para o mesmo "Gralha". A Галка sempre esteve certa (e' o
par pretendido, documentado numa nota do proprio glossario); as outras tres
atropelavam essa decisao por cima. Nomes novos, verificados contra contexto
narrativo (quem fala, que dia, que sintoma):

- **Сойка** (menina do bando Alma-e-Meia, expulsa do Poliedro) -> **a Saíra**
- **Лунь** (paciente do hospital, come argila, trabalha pro Stamatin — a
  auditoria confirmou que "Lunin"/"Lun"/"Gralha"/"Grouse" eram a MESMA
  pessoa em 5 grafias diferentes) -> **a Perdiz**
- **Грач** (funcionario grisalho da Prefeitura) -> **o Anu**
- **Клёст** (visitante avulso, so' uma linha) -> **o Curió** (confianca
  baixa, personagem aparece uma vez so')

E o Тентильан (Клёст) estava roubando o nome do Щур, que ja' era
"Tentilhão" havia tempo — esse ficou intocado.

### Seis erros de conteudo confirmados (dos 52 candidatos revisados)

1. `55804.0` — "Grace" inventado onde o russo so' diz "irmazinha" generica
2. `52987.52` — Notkin fundido com Pochinka, um garoto morto diferente
3. `57704.2` — o caso que puxou a investigacao: "Pontinho convenceu voce a
   partir" era invencao, o russo e' so' surpresa com a partida
4. `29591.71` — "Vladão" (o pai) usado onde o contexto e' "Vlad" (o filho)
5. `31489.0` — "Taya Pontinho": personagem errado por completo, ela e' Taya
   Tycheek, uma crianca sagrada do Kin sem relacao com o assistente Yakov
6. `71903.0` — a colisao Curió/Tentilhão acima

### Rotulos de sistema e nomes de lugar

19 rotulos que apareciam na ficha de todo paciente (ex: "Diagnostico
Estabelecido" com 10 formas em 26 usos) foram unificados — 3 ja' tinham se
resolvido sozinhos com a limpeza do caractere ⇥. Entre os 136 grupos de
nome de lugar/cargo, dois achados de peso: a faccao "os Duas-Almas" tinha
quatro grafias (uma delas, "Alma e Meia", diverge do russo: o termo
quer dizer "duas almas", nao "uma alma e meia"); e "Concept Artist" nos
creditos vazava ingles cru, agora "Artista Conceitual". Tambem corrigido:
"Changeling" chegando ate' a Impostora, duas salas do Rubin que estavam
sendo confundidas uma com a outra (Sala de Autopsias x Esconderijo).

### Achado extra na conferencia manual: um sistema inteiro de 29 nomes de ave

Fora do escopo do workflow, uma varredura propria achou `проситель X` — um
padrao de 29 NPCs "suplicantes/peticionarios", cada um batizado com uma
especie de ave russa diferente. **23 das 29 estao intactas em russo
transliterado ou ingles cru** (Zimnyak, Varakusha, Sych, Spiza, Dubrovnik,
Piskulka, Popolzen, Sarych, Gagara, Drofa, Splyushka, Zuyok, Neyasyt,
Cheglok, Korostel, Kopyto, Vyp, Pogonysh, Burevestnik — e mais). So' seis
foram traduzidas (Marreco, Narceja, Pica-pau, Beco sem Saída — este ultimo
errado, colide com o rotulo de sistema "Beco Sem Saída" ja' unificado
acima). Corrigimos so' os dois com resposta ja' estabelecida no resto do
corpus (Gannet e Swift -> Atoba e Andorinhao). Os outros 21 ficam para uma
proxima rodada dedicada — cada um exige identificar a especie e escolher um
nome brasileiro, o mesmo trabalho que o workflow fez para os quatro
personagens principais.

### Tambem achado: bug de fronteira de palavra no enforce_glossary.py

Quando um termo travado aparece logo depois da sequencia decorativa
"

" (quebra de paragrafo), a fronteira de palavra do regex falha — o
"n" literal e a letra cirilica seguinte contam como um so' "caractere de
palavra" pro Python, entao  nunca dispara ali. Foi assim que o "Gannet"
de 54648.11 escapou da varredura automatica mesmo com "Atoba" ja' travado
no glossario. Vale um ajuste no proprio tools/enforce_glossary.py depois.

## A legenda que nao aparecia — era nossa

O diagnostico anterior ("so' 4 de 20 cutscenes tem legenda, deve ser bug do
jogo") estava errado. Comparando byte a byte o asset injetado contra o
backup original, o defeito ficou obvio:

| idioma | quebras reais | escapes literais |
|---|---|---|
| ingles | 2 | 100 |
| russo | 2 | 100 |
| alemao | 2 | 74 |
| pt-BR dos devs | 2 | 68 |
| **nosso (antes)** | **100** | **0** |

O jogo guarda cada asset assim: `{Chave} valor`, um registro por linha.
A quebra de linha REAL separa um registro do proximo; a quebra de paragrafo
DENTRO de um valor fica como o escape literal de dois caracteres. O SRT
inteiro da cutscene e' UM valor so'.

O `tools/apply_pt.py` expandia o escape em quebra real antes de gravar
(linha 73). Isso transformava conteudo em estrutura: o SRT de 100 linhas
virava 100 registros orfaos, e o parser nao achava legenda nenhuma.

### O que foi corrigido

Descobri o formato exato por round-trip: remontar os assets a partir do
campo `pt` do workbook, com separador CRLF + BOM + separador final,
reproduz **8471 dos 8892** assets originais byte a byte (os 421 restantes
diferem so' no caminho da chave, artefato de extracao antigo).

Duas mudancas no `apply_pt.py`:

1. nao expandir mais `\\n` e `\\t` — ficam como escape literal, igual ao original
2. juntar os registros com CRLF e fechar com CRLF, em vez de LF sem fecho

Conferencia depois da correcao, pareando por `path_id` (o jogo tem 421
nomes de asset repetidos, entao parear por nome engana): **8892 de 8892
com a mesma contagem de registros do original, zero divergencia.** BOM e
separador final em 8892/8892.

Isso nao consertou so' a cutscene: 738 assets estavam com quebras reais a
mais que o original, sendo 656 onde o escape virou quebra. Toda quebra de
paragrafo do jogo estava sendo gravada como limite de registro.

## Achado: 453 assets em portugues que a extracao nunca pegou

Ao parear por `path_id` apareceu que o jogo tem **9345** TextAssets
`_Portuguese_Br`, e o nosso pacote cobre **8892**. Os 453 restantes sao as
"gemeas" dos nomes repetidos — mesmo nome, path_id diferente, conteudo
diferente (o `Labels` do analisador e o `Labels` da janela de demo nao tem
uma chave em comum).

Desses 453: 297 estao vazios (so' chave sem valor) e **156 tem texto de
verdade, 156.766 caracteres — 48 deles ainda em russo cru**, o resto em
ingles. Exemplos: `Hospital_Sukhonos_Interview`, `Day5_Visitors_Secretary
Decision` (66 valores), `Hospital_Burakh_TakeBlood`.

Nao sei ainda se o jogo carrega essas copias ou se sao sobra morta de
versao antiga — o jogador nao relatou dialogo em russo no hospital, o que
sugere que a maioria nao e' usada. Precisa de uma passada dedicada: extrair
esses 453 por path_id, ver quais tem texto vivo e traduzir.

## Os 453 assets SAO usados — a hipotese de "sobra morta" estava errada

Investigacao com evidencia, nao palpite. A premissa de "gemeas duplicadas"
era falsa: nao existem copias do mesmo asset. Sao **453 arquivos
diferentes, em pastas diferentes**, que por coincidencia tem o mesmo nome
de arquivo. A extracao original indexou por `m_Name` e sobrescreveu um com
o outro.

**Evidencia 1 — o ResourceManager.** Ele nao esta em resources.assets (por
isso a primeira sondagem deu zero); esta em `globalgamemanagers`, com
28.041 entradas de localizacao. Todos os 9345 assets aparecem la', cobertos
e nao cobertos, cada um com um caminho `Resources.Load` proprio e coerente
com o namespace das suas chaves:

    pid 22577  clouds2/characters/block_portuguese_br
    pid 12779  npcs/block_portuguese_br

O jogo carrega por CAMINHO, nao por nome. Os dois sao carregaveis.

**Evidencia 2 — intersecao zero.** As 2488 chaves das 453 copias nao tem
uma unica chave em comum com as 61.242 que traduzimos. Se o jogo pedir
qualquer uma delas, so' esse asset pode servir — nao ha fonte alternativa.

**Evidencia 3 — estao amarradas ao jogo.** Contagem de ocorrencias de 30
chaves nao cobertas contra 30 de controle (que o jogador ve traduzidas
hoje): perfil identico, 7 ocorrencias em ambas (6 sao os TextAssets de
idioma, a 7a e' o objeto do jogo que nomeia a chave).

**Evidencia 4 — espelhamento nos 6 idiomas.** Exatamente 9345 TextAssets em
cada idioma, com a mesma assinatura de contagem por nome-base. Um build que
carregasse so' uma copia por nome teria metade do conteudo morto ate no
russo dos proprios devs.

**Evidencia 5 — nao e' versao antiga.** A hipotese "ArchiveDialogs e' pasta
velha, Dialogs2 e' a atual" nao se sustenta: nos pares, ora o lado coberto
e' Dialogs2 e o nao coberto ArchiveDialogs (13 pares), ora o inverso (10),
ora os dois sao ArchiveDialogs em subpastas diferentes (18). Qual copia caiu
no nosso pacote foi acaso da ordem de extracao.

### O que isso significa

**2112 chaves com texto real, cerca de 157 mil caracteres, que o jogador
pode encontrar sem traducao — 48 assets ainda em russo cru.** E' a maior
pendencia do projeto. Exige reextrair indexando por `path_id` (nao por
nome), gerar o lote e traduzir.

## Suplicantes: 21 aves batizadas

O sistema de NPCs «проситель X» tinha 36 fichas; 32 sao apelido de ave.
Sete ja estavam certas. Batizamos 21, mais tres achados:

- **Тупик** dizia "Beco sem Saída" — a palavra russa e' ambigua (beco sem
  saida E o passaro papagaio-do-mar). O proprio ingles dos devs diz
  "visitor Puffin". Alem de errado, colidia com o rotulo de interface ja
  unificado. Virou **Araçari** (o bico enorme e colorido e' a mesma graca).
- **id 31940.0** tinha russo VAZIO e o ingles traz "visitor Auk", que passou cru
  como "visitante Auk" — a varredura pelo russo nunca acharia. Virou
  **Biguá**.
- **Копыто** e **Коростель** ja tinham forma consolidada no dialogo (Casco,
  Codorniz) mas a ficha divergia. Alinhados.

Onde havia equivalente brasileiro direto, usamos (Socó, Batuíra, Tico-tico,
Corujinha). Onde a especie nao existe no Brasil, escolhemos a ave que ocupa
o mesmo nicho ou carrega a mesma motivacao: Mergulhão pela mobelha, Irerê
pela pisculka (ambos batizados pelo assobio), Acauã pelo burevestnik (ambos
arautos de catastrofe).

Tres candidatos foram descartados por colisao que so' apareceu na conferencia:
"Quero-quero" ja era o nome de DOIS outros NPCs; "Petrel" colidia com o
paciente Петрель; "Canário" e' metafora recorrente do texto em cinco ids.

A palavra «проситель» tinha cinco formas nossas (suplicante, o suplicante,
peticionário, visitante, solicitante). Fixada em **"suplicante <Nome>"**,
sem artigo: e' comum de dois generos, entao cobre проситель e
просительница sem inventar marca de genero num rotulo.

## O bug de fronteira: corrigido pela metade, de proposito

A correcao proposta era aplicar o relaxamento nos tres pontos onde a
ferramenta monta fronteira. O revisor simulou e **achou regressao**: aplicar
no gatilho RUSSO fazia a varredura passar a mexer nos creditos e na lista de
apoiadores, trocando nome de pessoas reais. Esse trecho foi descartado; ficou
so' o lado portugues, que era o que resolvia o caso do "Gannet".

Depois do conserto a varredura acha 4 linhas que antes escapavam — o corpus
ja estava limpo pelo scanner antigo, entao essas 4 sao exatamente o que o
bug escondia.

## Os 453 assets perdidos: traduzidos

### A causa raiz

O `tools/apply_pt.py` agrupava os registros por NOME de asset. O jogo tem 453
arquivos diferentes, em pastas diferentes, que compartilham o nome do
arquivo (dois `Labels`, dois `Day1_Q0_Interrogation`...). Agrupar por nome
fundia assets distintos num so' e escrevia tudo num path_id, deixando o
outro intocado. Foi literalmente assim que 453 assets nunca entraram na
traducao. Agora agrupa por `path_id`, e o `tools/fundir_453.py` ABORTA se
detectar que essa correcao nao esta aplicada.

### O que estava perdido

Nao era periferia. Traduzimos a copia `ArchiveDialogs` (arquivo/legado) e
deixamos a `Dialogs2` (viva) em ingles:

| cena | copia que cobrimos | copia que faltava |
|---|---|---|
| Day1_Q0_Interrogation | 2 registros | **33 registros** |
| Hospital_Vasiliy_Interview | 9 registros | **56 registros** |

Sao os interrogatorios que emolduram o jogo inteiro e as entrevistas de
paciente — o laco central de jogabilidade.

### Como foi feito

`tools/extrair_453.py` pareia PT com RU/EN pelo CONJUNTO DE CHAVES, nao pelo
nome (que e' justamente o que colide). Resultado: 0 assets sem par.

Dois workflows: 12 agentes para os 2091 registros com texto, depois 4 para
343 registros que a primeira instrucao deixou escapar (o `pt` de origem vinha
vazio, mas havia russo ou ingles disponivel — eu tinha mandado gravar vazio
sem prever esse caso).

Duas coisas que os agentes fizeram sem ser mandado, e que melhoraram o
resultado:

- **Reaproveitaram traducao ja aprovada dos assets gemeos.** Um lote achou
  que 130 das suas 181 linhas ja existiam traduzidas na copia `ArchiveDialogs`
  da mesma cena; cruzou por campo russo identico e por chave, conferiu cena a
  cena, e reusou verbatim. Garante que o jogador nunca veja a mesma fala
  escrita de dois jeitos.
- **Ancoraram vocabulario no corpus em vez de inventar.** `«Медики»` estava
  como "Ordeiros", calcado em *Orderlies*, e virou "Enfermeiros", a
  forma que o resto da UI ja usava. `«побычики»`, palavra inventada por um
  personagem louco, virou "embovinos" porque o corpus ja usava isso em 8
  linhas, inclusive numa fala que se refere de volta a esse mesmo paciente.

Casos de localizacao que valem registro: `Житочник` (ingles: "Hardman")
virou **Valentão**; `Аристарх` (ingles: "Swangoose" (forma da versao inglesa)) ficou **Aristarkh**,
como manda o glossario — o apelido ingles nao passou.

### Resultado

Cobertura foi de **61242/61242 (que era falso — o portao nao sabia que os
453 existiam)** para **63703/63730, 100%**. As 27 restantes sao registros
genuinamente vazios, sem russo nem ingles.

Na tela: **817 linhas em russo -> 0. 1472 em ingles -> 0.**

Verificacao independente: 0 erro de formato, 0 id duplicado, 0 cirilico
indevido. As 11 linhas com cirilico que sobram sao legitimas (lixo de teclado
dos proprios devs em cenas de teste, o «Русский» do seletor de idiomas, e um
easter egg nos creditos).

Tambem removido: `Day06_01c.tsv` era subconjunto exato de `Day06_01b.tsv`
(300 ids, todos identicos, nenhum exclusivo) — a duplicata podia divergir se
alguem editasse so' um dos dois.

## Alinhamento com o Pathologic 2 pt-BR

Fonte: a traducao de fa do Yuri Beira (Pathologic 2 & Marble Nest), que o
usuario forneceu. NAO e' a localizacao oficial — sao as escolhas de um
tradutor. Entrou como REFERENCIA, nao como autoridade: mesmo tratamento que
demos ao pt-BR oficial abandonado do proprio 3.

Comparados 27 conceitos que os dois jogos compartilham (mesma cidade, mesmo
elenco). Batem em 6, divergem em 12.

### O achado que doeu: quatro anglicismos nossos

As quatro divergencias mais importantes eram todas o MESMO erro nosso — o
russo tem palavra comum, o portugues tem equivalente exato, e nos ficamos
com o nome INGLES. Em dois deles o erro estava TRAVADO no glossario como se
fosse decisao (a linha "Grace" chegava a proibir a forma portuguesa "Graça").

| russo | significa | ingles fez | P2 | nos (antes) | agora |
|---|---|---|---|---|---|
| Гриф | abutre | "Bad Grief" | Abutre | Grief | **o Abutre** |
| Ласка | carinho/doninha | "Grace" | Graça | Grace | **Graça** |
| Уклад | ordem, modo de vida | "the Kin" | Estirpe | o Kin | **a Estirpe** |
| Гаруспик | adivinho de visceras | "Haruspex" | Arúspice | Haruspex | **o Arúspice** |

`Уклад` mudou de genero (ms -> fs). A ferramenta reescreve as contracoes
sozinha: "do Kin" -> "da Estirpe".

### Empates de gosto: o usuario escolheu seguir o 2

Бойня -> **o Abatedouro** (era Matadouro). Песчанка -> **a Peste Arenosa**
(era Peste de Areia; o P2 usa a forma 159 vezes e nunca a nossa). Тяжёлый
Влад -> **Grande Vlad** (era Vladão — custou uma escolha que o usuario tinha
elogiado, e ele decidiu assim mesmo, ciente).

### Duas adocoes do P2 RECUSADAS, com motivo

- **Termiteiro**: o nosso lock separa «Термиты» (o povo) = os Termiteiros de
  «Термитник» (o predio) = o Termitario. O P2 tem ZERO ocorrencia do povo —
  ele nunca precisou resolver essa distincao. Adotar deixaria as duas coisas
  com o mesmo nome. Mantido **o Termitário**.
- **Palito**: era falso positivo do meu comparativo. As 4 ocorrencias no P2
  sao "Palito de fosforo", o ITEM. Ele nunca chama o menino «Спичка» assim.
  Mantido **o Fósforo**.

### Uma linha que precisou de reescrita

`47918.29` era trocadilho com o nome INGLES: "Não é à toa que me chamam de
Grief: deixo todos os meus enlutados para trás" (grief = luto). O russo nao
tem isso — diz «мама, роди меня обратно» (mae, me poe de volta pra dentro),
expressao de dor extrema. Com "Abutre" o trocadilho ingles morreria de
qualquer jeito, entao a linha voltou ao que o russo diz.

### Numeros

1053 linhas alteradas ao todo. Formas antigas restantes: Grief 0, Kin 0,
Grace 0, Haruspex 0, Vladão 0, Matadouro 0, Peste de Areia 0.

O trabalho revelou tambem varias declinacoes russas que os gatilhos do
glossario nao cobriam e que estavam falhando em silencio: «Боен» e «Бойнях»
(genitivo e prepositivo plural de Бойня), «Грифов» e «грифовский»
(possessivo e adjetivo), «укладский» (adjetivo de Уклад), «Большому Владу»
(uma terceira forma do nome do Vlad pai), e «песчанка» em minuscula. Todos
ampliados.

## Fechamento das pendencias

### Colisao medica: resolvida por evidencia, sem precisar da tela

Os caminhos de chave separam tres objetos que a traducao vinha fundindo:

| russo | ingles | o que e' | agora |
|---|---|---|---|
| Врачебный планшет | Casebook | o aparelho | **o Fichário** |
| Личное дело | Medical Chart | a ficha de um paciente | **o prontuário** |
| Карты пациентов | Patients' files | o conjunto | **os prontuários** |

"Fichário" ja' era a aba (ПЛАНШЕТ), entao a hierarquia fecha. As linhas em
que «Личное дело» e' a expressao idiomatica "assunto pessoal" ja' estavam
certas e nao foram tocadas.

### O bug de fronteira: corrigido de verdade

A tentativa anterior (relaxar a fronteira do regex) causava regressao nos
creditos. Reproduzi: a varredura queria renomear **Peter Potapov**, pessoa
real, para "Pyotr Potapov" — o russo dos creditos tem «Пётр Потапов», o
gatilho casa, e o portugues tem "Peter". As duas chaves disparavam.

Duas correcoes, e a segunda e' a que faltava:

1. **Normalizar o texto de busca**, nao o padrao: o campo russo passa por
   uma troca dos escapes literais por espaco antes do casamento. Isso da'
   fronteira correta sem afrouxar o que conta como fronteira.
2. **Excluir os creditos da varredura.** Nome de pessoa real nunca deve
   passar por glossario. 404 registros protegidos.

Testado: o gatilho que falhava (o caso «

Олуша» que deixou "Gannet"
passar) agora dispara, e o Peter Potapov segue intacto.

### Interjeicoes: 7 -> 0

O detector acusava 28, mas 11 eram falso positivo do MESMO tipo de bug de
fronteira: `nAh` e' o "n" do escape colado em "Ah" — e "Ah" e' portugues
perfeito. Das 17 reais, cada escolha veio do que o russo faz:

тьфу (cuspir de nojo) -> Credo | Бр-р (tremor) -> Brr | У-у-у -> Ui |
Угмм (resmungo) -> Hum | ugh de gosto ruim -> Eca | ugh de exasperacao ->
Aff | ugh de desprezo -> Bah | Hmph -> Hunf

### Formas pt-PT: 37 -> 30

As 30 que ficaram sao registro elevado DELIBERADO e nao devem mudar: a
citacao de Hamlet ("sonha a tua filosofia"), a carta formal ("conforme
vossas instrucoes"), a reza ("vosso Criador"), o cantico da Agua. Tres eram
falso positivo: latim («Timere desideria tua»), poema citado, e cantico.

O defeito real era outro — 11 falas MISTURAVAM tu e voce na mesma frase
("Como tua mulher te aguenta... como voce pega os turnos"). Em pt-BR o "te"
convive com "voce" sem problema; o que soa errado e' tua/teu/ti/contigo ao
lado de voce. Uma delas tinha ainda conjugacao portuguesa ("nao te fazes",
"quanto tempo aguentas").

### Italicos: 16 -> 10

Achado no meio: `22322.38` tinha **`< i>` com espaco** — tag quebrada, que
apareceria literal na tela como "< i>Pensa,". Corrigida.

Recuperadas 6 enfases que o ingles marca e o portugues tinha perdido, onde o
mapeamento era inequivoco. Os 10 que ficam sao enfase que so' o ingles tem —
o russo, nossa fonte de verdade, nao marca. Dois sao intraduziveis por
natureza: o russo italiza a vogal em «б<i>о</i>льшую» para marcar acento
tonico e desfazer ambiguidade, coisa que "maior" em portugues nao tem.

### Rotulos de UI: medidos, nada a fazer

41 rotulos de controle passam do original, mas dica de controle tem folga —
nao e' o caso da barra de abas. Dois que pareciam problema nao sao:
«Упасть в омут с головой» e' trocadilho (cair de cabeca no remanso E
mergulhar na Stillwater) e o nosso preserva os dois sentidos; e os quatro
"Coletar amostra" vem de acoes que o proprio ingles tambem funde em "Take
Sample" — um prompt consistente e' melhor que quatro sinonimos.

