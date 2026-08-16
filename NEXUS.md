# Publicar no Nexus — Pathologic 3

Este é o único dos três que **já está no ar**:
[nexusmods.com/pathologic3/mods/28](https://www.nexusmods.com/pathologic3/mods/28).

Então aqui o assunto é outro: manter a página viva, subir versão nova sem
quebrar quem já baixou, e ter um texto de descrição que envelheça bem.

---

## Parte 1 — o texto da página

O `README.md` deste repositório já tem a explicação boa de como a tradução foi
feita, e ela foi escrita para pessoa, não para programador. **Use ele como base.**
O que muda entre o README e a página do Nexus é só o começo e o fim.

O que a página precisa ter, na ordem:

**1. A frase de abertura.** Diga o tamanho antes de qualquer outra coisa. Quem
chega quer saber se é completo.

> Tradução completa de Pathologic 3 para português do Brasil. São 63.703 falas:
> cada diálogo, cada anotação, cada tela de menu.

**2. Como instalar.** Antes de qualquer explicação de processo. Quem já decidiu
baixar não quer ler filosofia primeiro. Copie a seção "Como instalar" do README.

**3. A seção "Sim, foi feita com inteligência artificial".** Essa é a parte mais
importante da página, e ela já está escrita no README. Não corte, não encolha, e
não esconda no fim.

O motivo é prático: a pergunta vai ser feita nos comentários de qualquer jeito.
Respondê-la antes, com detalhe e sem defensiva, muda completamente o tom da
conversa — a diferença entre "usou IA?" como acusação e como curiosidade é
quem falou primeiro.

E a resposta é forte porque é verdadeira: a pesquisa veio antes da primeira
linha traduzida, o glossário de 105 termos é verificado automaticamente a cada
versão, e a base é o **russo**, não o inglês.

**4. O que guiou as escolhas.** Também já no README. É o que separa esta
tradução de uma passada de tradutor automático, e é a parte que os jogadores que
se importam vão ler inteira.

**5. Créditos e permissões**, no fim.

---

## Parte 2 — subir uma versão nova

**Antes**

1. Rode a verificação do glossário. Ela existe justamente para isto: recusa o
   resultado se algum dos 105 termos escapou.
2. Instale numa cópia limpa e jogue os primeiros minutos. Não confie só no
   verificador.
3. Anote o que mudou em linguagem de jogador, não de commit. "Corrigidas 40
   falas em que o nome do Bacharel aparecia trocado" é útil; "fix typos" não é.

**Subindo**

4. Sempre **arquivo novo**, nunca substituir o existente. Quem já baixou recebe
   notificação de update, e o histórico fica visível.
5. Numere de verdade: `1.1`, `1.2`. Se o número não subir, o Nexus não avisa
   ninguém.
6. Preencha o **changelog** da versão. É o campo que mais gente lê e o que menos
   gente preenche.
7. Se a versão anterior tinha um problema conhecido, diga na descrição da nova
   que ele foi resolvido. As pessoas voltam à página justamente para isso.

**Os pacotes deste repositório**

| arquivo | quando usar |
|---|---|
| `Pathologic3-Traducao-PTBR-ASSINADO.zip` | o principal, executável assinado |
| `Pathologic3-Traducao-PTBR-Arquivo-Pronto.zip` | para quem não quer executável |
| `Pathologic3-Traducao-PTBR-SEM-EXECUTAVEL.zip` | versão em script |

Se subir mais de um, deixe claro **em uma linha na descrição de cada arquivo**
qual é a diferença. Ninguém abre três zips para descobrir.

**Depois**

8. Responda os comentários dos primeiros dias. É quando aparecem os erros que
   nenhuma verificação pega — piada que não funcionou, personagem que soou
   errado — e é a informação mais valiosa que você vai receber.
9. Print de jogador vale mais que qualquer relatório automático. Peça.

---

## Se o jogo atualizar

A tradução reescreve um arquivo grande do jogo, então uma atualização
provavelmente desfaz tudo.

Quando acontecer: **avise na página antes de consertar**. Um aviso rápido
("atualização do dia X desfez a tradução, estou vendo isso") evita uma
enxurrada de comentários dizendo que quebrou, e as pessoas esperam sem
reclamar quando sabem que alguém está olhando.
