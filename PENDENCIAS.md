# Pendências

Falas que exigem decisão do dono. **Não chute: deposite aqui.**

Existe porque o qa_check e o enforce_glossary pegam a maior parte dos defeitos sozinhos, e os outros ~6% são
justamente os que um modelo não deve resolver por conta própria — voz de personagem,
idiomatismo, escolha de tratamento, termo novo que ainda não está no glossário.

Chutar e seguir em frente é o que produz erro que passa em todas as checagens.

Formato:

```
### <chave>  (ex.: a110_0247)
- EN: <o original>
- RU: <o russo, que é a autoridade>
- Dúvida: <qual é a dúvida, em uma frase>
- Opções: <a> / <b>
- Inclinação: <qual você escolheria e por quê, se tivesse de escolher>
```

Quando o dono decidir: a decisão vai para o `GLOSSARIO.tsv` (se for termo) ou para a
`BIBLIA.md` (se for regra de voz), e a entrada sai daqui.

---

_(vazio)_
