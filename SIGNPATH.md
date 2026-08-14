# Assinatura digital gratuita via SignPath

O único build que nunca levou acusação de antivírus foi o assinado. A
SignPath Foundation assina projetos de código aberto de graça, e este
projeto cumpre os requisitos: repositório público, release publicada, e o
autor do pedido é o mantenedor.

O que muda para o jogador: o instalador com o ícone do jogo passa a ter
assinatura digital válida. O Windows mostra **"SignPath Foundation"** como
editor (não o nome do autor — para o certificado sair no seu nome, o caminho
é o pago, Certum, ~50 dólares/ano).

A esteira técnica já está pronta neste repositório: o workflow
`build-installer` compila o instalador a partir do código público, que é
exatamente o que o SignPath exige. Falta só a parte burocrática, que é
pessoal e intransferível.

## O que só o autor pode fazer

**1. Candidatar o projeto** em <https://signpath.org> (About → Apply).
No formulário:

- Projeto: `https://github.com/IgusMarine/pathologic3-ptbr`
- Releases: `https://github.com/IgusMarine/pathologic3-ptbr/releases`
- Descrição sugerida: *Brazilian Portuguese translation for the game
  Pathologic 3, with a GUI installer built with cx_Freeze. The installer is
  built by GitHub Actions from this public repository.*

A análise é humana e leva de dias a semanas.

**2. Depois de aprovado**, no painel do SignPath:

- ativar o Trusted Build System **GitHub.com** e vinculá-lo ao projeto;
- instalar o **SignPath GitHub App** neste repositório;
- criar o projeto (anotar o *project slug*) com uma *artifact
  configuration* apontando para o `Instalar-Traducao-PTBR.exe` dentro do
  artefato;
- criar uma *signing policy* de release (anotar o *slug*; ela pede a sua
  aprovação manual a cada assinatura — é o desenho correto);
- gerar um **API token** de submissão.

**3. No GitHub** (Settings do repositório):

| onde | nome | valor |
|---|---|---|
| Secrets → Actions | `SIGNPATH_API_TOKEN` | o token gerado |
| Variables → Actions | `SIGNPATH_ENABLED` | `true` |
| Variables → Actions | `SIGNPATH_ORGANIZATION_ID` | do painel do SignPath |
| Variables → Actions | `SIGNPATH_PROJECT_SLUG` | do painel |
| Variables → Actions | `SIGNPATH_POLICY_SLUG` | do painel |

**4. Rodar** Actions → `build-installer` → *Run workflow*, aprovar o pedido
de assinatura no painel do SignPath, e baixar o artefato
`instalador-assinado`.

## Obrigação de atribuição

O SignPath Foundation pede crédito no projeto. Quando a assinatura estiver
ativa, acrescentar ao README:

> Free code signing provided by [SignPath.io](https://signpath.io),
> certificate by [SignPath Foundation](https://signpath.org).

## Enquanto isso

Sem a conta, o workflow roda só o build (a etapa de assinatura fica
desligada pela variável `SIGNPATH_ENABLED`). O artefato
`instalador-nao-assinado` já sai reproduzível a partir do código público —
o que, por si, é um argumento de confiança.
