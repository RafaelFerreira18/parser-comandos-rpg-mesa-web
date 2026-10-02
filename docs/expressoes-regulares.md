# Fichas das cinco expressões regulares
Geradas de `rpg/language.py`. Cada padrão usa `re.fullmatch`, sem flags e sem normalização.
## Convenções

Σ é declarado individualmente. ␠ representa exatamente U+0020. Literais estão entre aspas simples. União ∪, concatenação por justaposição, estrela * e ε têm o significado do guia. Aspas e ␠ são metanotação, não caracteres extras.
As classes do padrão Python expandem conjuntos finitos. `(?:...)` agrupa sem capturar; `(?P<nome>...)` captura parâmetros sem mudar a linguagem. Não há lookaround, retroreferências, recursão, `\w`, `\d`, `\s` ou âncoras ambíguas.
Quantidade: 1 a 20, sem zero inicial. Faces: 4, 6, 8, 10, 12, 20, 100. Modificador dos dados: sinal obrigatório se presente, seguido de um ou dois dígitos. Bônus: sinal opcional, um ou dois dígitos (00 e +05 aceitos). CA/CD: 1 a 99 sem zero inicial. Nomes: [a-z][a-z0-9_]*.
A linguagem regular admite nomes de qualquer comprimento. O serviço impõe separadamente 512 caracteres por comando e 4096 bytes por requisição. Esses limites operacionais não são parte das cinco ER.

## ER-01: Rolagem de dados

Extrair quantidade, faces e modificador de uma rolagem.

**Alfabeto Σ:** ␠, '+', '-', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'd', 'l', 'o', 'r'

**Linguagem:** comandos completos no formato `/rolar 2d6+3`, com parâmetros nos domínios das convenções acima. A ordem e os espaços são obrigatórios.

**ER formal expandida:**

'/''r''o''l''a''r'␠ (('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '1' ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '2''0') 'd' ('4' ∪ '6' ∪ '8' ∪ '1''0' ∪ '1''2' ∪ '2''0' ∪ '1''0''0') (ε ∪ ('+' ∪ '-') ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')))

**Sintaxe exata em `rpg/patterns.py`, utilizada por Rule.pattern:**

```python
r"/rolar\ (?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))"
# re.fullmatch(rule.pattern, texto)
```

**AFNε:** início q0, final q1; 49 estados e 94 transições elementares. Arquivos `automata/rolar.dot`, `.svg`, `.jff`. O SVG agrupa transições paralelas de um caractere; no JFLAP cada símbolo tem sua própria transição. `<read />` é movimento vazio.

| Cadeia | Esperado |
|---|---|
| `/rolar 1d4` | Aceita |
| `/rolar 20d100+99` | Aceita |
| `/rolar 2d6-3` | Aceita |
| `/rolar 10d10+0` | Aceita |
| `/rolar 1d20-99` | Aceita |
| `/rolar 3d12+05` | Aceita |
| `` | Rejeitada |
| `/rolar 0d6` | Rejeitada |
| `/rolar 21d6` | Rejeitada |
| `/rolar 1d7` | Rejeitada |
| `/rolar 1d6+100` | Rejeitada |
| `/rolar 1d6\n` | Rejeitada |

Caso-limite: primeira cadeia aceita usa os mínimos; a segunda ou terceira explora limites superiores. A cadeia vazia é rejeitada.

**Transições completas:**

| Origem | Símbolo | Destino |
|---|---|---|
| q0 | / | q3 |
| q3 | r | q4 |
| q4 | o | q5 |
| q5 | l | q6 |
| q6 | a | q7 |
| q7 | r | q8 |
| q8 | ␠ | q2 |
| q2 | ε | q10 |
| q11 | ε | q9 |
| q10 | 1 | q11 |
| q10 | 2 | q11 |
| q10 | 3 | q11 |
| q10 | 4 | q11 |
| q10 | 5 | q11 |
| q10 | 6 | q11 |
| q10 | 7 | q11 |
| q10 | 8 | q11 |
| q10 | 9 | q11 |
| q2 | ε | q12 |
| q13 | ε | q9 |
| q12 | 1 | q14 |
| q14 | 0 | q13 |
| q14 | 1 | q13 |
| q14 | 2 | q13 |
| q14 | 3 | q13 |
| q14 | 4 | q13 |
| q14 | 5 | q13 |
| q14 | 6 | q13 |
| q14 | 7 | q13 |
| q14 | 8 | q13 |
| q14 | 9 | q13 |
| q2 | ε | q15 |
| q16 | ε | q9 |
| q15 | 2 | q17 |
| q17 | 0 | q16 |
| q9 | d | q18 |
| q18 | ε | q20 |
| q21 | ε | q19 |
| q20 | 4 | q21 |
| q18 | ε | q22 |
| q23 | ε | q19 |
| q22 | 6 | q23 |
| q18 | ε | q24 |
| q25 | ε | q19 |
| q24 | 8 | q25 |
| q18 | ε | q26 |
| q27 | ε | q19 |
| q26 | 1 | q28 |
| q28 | 0 | q27 |
| q18 | ε | q29 |
| q30 | ε | q19 |
| q29 | 1 | q31 |
| q31 | 2 | q30 |
| q18 | ε | q32 |
| q33 | ε | q19 |
| q32 | 2 | q34 |
| q34 | 0 | q33 |
| q18 | ε | q35 |
| q36 | ε | q19 |
| q35 | 1 | q37 |
| q37 | 0 | q38 |
| q38 | 0 | q36 |
| q19 | ε | q39 |
| q40 | ε | q1 |
| q39 | ε | q40 |
| q19 | ε | q41 |
| q42 | ε | q1 |
| q41 | + | q43 |
| q41 | - | q43 |
| q43 | 0 | q44 |
| q43 | 1 | q44 |
| q43 | 2 | q44 |
| q43 | 3 | q44 |
| q43 | 4 | q44 |
| q43 | 5 | q44 |
| q43 | 6 | q44 |
| q43 | 7 | q44 |
| q43 | 8 | q44 |
| q43 | 9 | q44 |
| q44 | ε | q45 |
| q46 | ε | q42 |
| q45 | ε | q46 |
| q44 | ε | q47 |
| q48 | ε | q42 |
| q47 | 0 | q48 |
| q47 | 1 | q48 |
| q47 | 2 | q48 |
| q47 | 3 | q48 |
| q47 | 4 | q48 |
| q47 | 5 | q48 |
| q47 | 6 | q48 |
| q47 | 7 | q48 |
| q47 | 8 | q48 |
| q47 | 9 | q48 |

## ER-02: Ataque

Extrair alvo, bônus de acerto, classe de armadura e dano.

**Alfabeto Σ:** ␠, '+', '-', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'

**Linguagem:** comandos completos no formato `/atacar goblin bonus=5 ca=14 dano=1d8+2`, com parâmetros nos domínios das convenções acima. A ordem e os espaços são obrigatórios.

**ER formal expandida:**

'/''a''t''a''c''a''r'␠ ('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z') (('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z' ∪ '0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9' ∪ '_'))* ␠'b''o''n''u''s''=' (ε ∪ ('+' ∪ '-')) ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')) ␠'c''a''=' ('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')) ␠'d''a''n''o''=' (('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '1' ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '2''0') 'd' ('4' ∪ '6' ∪ '8' ∪ '1''0' ∪ '1''2' ∪ '2''0' ∪ '1''0''0') (ε ∪ ('+' ∪ '-') ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')))

**Sintaxe exata em `rpg/patterns.py`, utilizada por Rule.pattern:**

```python
r"/atacar\ (?P<alvo>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ bonus=(?P<bonus>(?:|[\+\-])[0123456789](?:|[0123456789]))\ ca=(?P<ca>[123456789](?:|[0123456789]))\ dano=(?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))"
# re.fullmatch(rule.pattern, texto)
```

**AFNε:** início q0, final q1; 88 estados e 235 transições elementares. Arquivos `automata/atacar.dot`, `.svg`, `.jff`. O SVG agrupa transições paralelas de um caractere; no JFLAP cada símbolo tem sua própria transição. `<read />` é movimento vazio.

| Cadeia | Esperado |
|---|---|
| `/atacar a bonus=0 ca=1 dano=1d4` | Aceita |
| `/atacar goblin bonus=5 ca=14 dano=1d8+2` | Aceita |
| `/atacar orc_2 bonus=-99 ca=99 dano=20d100+99` | Aceita |
| `/atacar dragao bonus=+9 ca=20 dano=2d12` | Aceita |
| `/atacar x1 bonus=00 ca=2 dano=1d6-99` | Aceita |
| `/atacar lobo bonus=-1 ca=12 dano=3d10+05` | Aceita |
| `` | Rejeitada |
| `/atacar 1orc bonus=0 ca=1 dano=1d4` | Rejeitada |
| `/atacar orc bonus=100 ca=10 dano=1d6` | Rejeitada |
| `/atacar orc bonus=0 ca=0 dano=1d6` | Rejeitada |
| `/atacar orc ca=10 bonus=0 dano=1d6` | Rejeitada |
| `/atacar orc bonus=0 ca=10 dano=0d6` | Rejeitada |

Caso-limite: primeira cadeia aceita usa os mínimos; a segunda ou terceira explora limites superiores. A cadeia vazia é rejeitada.

**Transições completas:**

| Origem | Símbolo | Destino |
|---|---|---|
| q0 | / | q3 |
| q3 | a | q4 |
| q4 | t | q5 |
| q5 | a | q6 |
| q6 | c | q7 |
| q7 | a | q8 |
| q8 | r | q9 |
| q9 | ␠ | q2 |
| q2 | a | q11 |
| q2 | b | q11 |
| q2 | c | q11 |
| q2 | d | q11 |
| q2 | e | q11 |
| q2 | f | q11 |
| q2 | g | q11 |
| q2 | h | q11 |
| q2 | i | q11 |
| q2 | j | q11 |
| q2 | k | q11 |
| q2 | l | q11 |
| q2 | m | q11 |
| q2 | n | q11 |
| q2 | o | q11 |
| q2 | p | q11 |
| q2 | q | q11 |
| q2 | r | q11 |
| q2 | s | q11 |
| q2 | t | q11 |
| q2 | u | q11 |
| q2 | v | q11 |
| q2 | w | q11 |
| q2 | x | q11 |
| q2 | y | q11 |
| q2 | z | q11 |
| q11 | ε | q10 |
| q11 | ε | q12 |
| q13 | ε | q12 |
| q13 | ε | q10 |
| q12 | a | q13 |
| q12 | b | q13 |
| q12 | c | q13 |
| q12 | d | q13 |
| q12 | e | q13 |
| q12 | f | q13 |
| q12 | g | q13 |
| q12 | h | q13 |
| q12 | i | q13 |
| q12 | j | q13 |
| q12 | k | q13 |
| q12 | l | q13 |
| q12 | m | q13 |
| q12 | n | q13 |
| q12 | o | q13 |
| q12 | p | q13 |
| q12 | q | q13 |
| q12 | r | q13 |
| q12 | s | q13 |
| q12 | t | q13 |
| q12 | u | q13 |
| q12 | v | q13 |
| q12 | w | q13 |
| q12 | x | q13 |
| q12 | y | q13 |
| q12 | z | q13 |
| q12 | 0 | q13 |
| q12 | 1 | q13 |
| q12 | 2 | q13 |
| q12 | 3 | q13 |
| q12 | 4 | q13 |
| q12 | 5 | q13 |
| q12 | 6 | q13 |
| q12 | 7 | q13 |
| q12 | 8 | q13 |
| q12 | 9 | q13 |
| q12 | _ | q13 |
| q10 | ␠ | q15 |
| q15 | b | q16 |
| q16 | o | q17 |
| q17 | n | q18 |
| q18 | u | q19 |
| q19 | s | q20 |
| q20 | = | q14 |
| q14 | ε | q23 |
| q24 | ε | q22 |
| q23 | ε | q24 |
| q14 | ε | q25 |
| q26 | ε | q22 |
| q25 | + | q26 |
| q25 | - | q26 |
| q22 | 0 | q27 |
| q22 | 1 | q27 |
| q22 | 2 | q27 |
| q22 | 3 | q27 |
| q22 | 4 | q27 |
| q22 | 5 | q27 |
| q22 | 6 | q27 |
| q22 | 7 | q27 |
| q22 | 8 | q27 |
| q22 | 9 | q27 |
| q27 | ε | q28 |
| q29 | ε | q21 |
| q28 | ε | q29 |
| q27 | ε | q30 |
| q31 | ε | q21 |
| q30 | 0 | q31 |
| q30 | 1 | q31 |
| q30 | 2 | q31 |
| q30 | 3 | q31 |
| q30 | 4 | q31 |
| q30 | 5 | q31 |
| q30 | 6 | q31 |
| q30 | 7 | q31 |
| q30 | 8 | q31 |
| q30 | 9 | q31 |
| q21 | ␠ | q33 |
| q33 | c | q34 |
| q34 | a | q35 |
| q35 | = | q32 |
| q32 | 1 | q37 |
| q32 | 2 | q37 |
| q32 | 3 | q37 |
| q32 | 4 | q37 |
| q32 | 5 | q37 |
| q32 | 6 | q37 |
| q32 | 7 | q37 |
| q32 | 8 | q37 |
| q32 | 9 | q37 |
| q37 | ε | q38 |
| q39 | ε | q36 |
| q38 | ε | q39 |
| q37 | ε | q40 |
| q41 | ε | q36 |
| q40 | 0 | q41 |
| q40 | 1 | q41 |
| q40 | 2 | q41 |
| q40 | 3 | q41 |
| q40 | 4 | q41 |
| q40 | 5 | q41 |
| q40 | 6 | q41 |
| q40 | 7 | q41 |
| q40 | 8 | q41 |
| q40 | 9 | q41 |
| q36 | ␠ | q43 |
| q43 | d | q44 |
| q44 | a | q45 |
| q45 | n | q46 |
| q46 | o | q47 |
| q47 | = | q42 |
| q42 | ε | q49 |
| q50 | ε | q48 |
| q49 | 1 | q50 |
| q49 | 2 | q50 |
| q49 | 3 | q50 |
| q49 | 4 | q50 |
| q49 | 5 | q50 |
| q49 | 6 | q50 |
| q49 | 7 | q50 |
| q49 | 8 | q50 |
| q49 | 9 | q50 |
| q42 | ε | q51 |
| q52 | ε | q48 |
| q51 | 1 | q53 |
| q53 | 0 | q52 |
| q53 | 1 | q52 |
| q53 | 2 | q52 |
| q53 | 3 | q52 |
| q53 | 4 | q52 |
| q53 | 5 | q52 |
| q53 | 6 | q52 |
| q53 | 7 | q52 |
| q53 | 8 | q52 |
| q53 | 9 | q52 |
| q42 | ε | q54 |
| q55 | ε | q48 |
| q54 | 2 | q56 |
| q56 | 0 | q55 |
| q48 | d | q57 |
| q57 | ε | q59 |
| q60 | ε | q58 |
| q59 | 4 | q60 |
| q57 | ε | q61 |
| q62 | ε | q58 |
| q61 | 6 | q62 |
| q57 | ε | q63 |
| q64 | ε | q58 |
| q63 | 8 | q64 |
| q57 | ε | q65 |
| q66 | ε | q58 |
| q65 | 1 | q67 |
| q67 | 0 | q66 |
| q57 | ε | q68 |
| q69 | ε | q58 |
| q68 | 1 | q70 |
| q70 | 2 | q69 |
| q57 | ε | q71 |
| q72 | ε | q58 |
| q71 | 2 | q73 |
| q73 | 0 | q72 |
| q57 | ε | q74 |
| q75 | ε | q58 |
| q74 | 1 | q76 |
| q76 | 0 | q77 |
| q77 | 0 | q75 |
| q58 | ε | q78 |
| q79 | ε | q1 |
| q78 | ε | q79 |
| q58 | ε | q80 |
| q81 | ε | q1 |
| q80 | + | q82 |
| q80 | - | q82 |
| q82 | 0 | q83 |
| q82 | 1 | q83 |
| q82 | 2 | q83 |
| q82 | 3 | q83 |
| q82 | 4 | q83 |
| q82 | 5 | q83 |
| q82 | 6 | q83 |
| q82 | 7 | q83 |
| q82 | 8 | q83 |
| q82 | 9 | q83 |
| q83 | ε | q84 |
| q85 | ε | q81 |
| q84 | ε | q85 |
| q83 | ε | q86 |
| q87 | ε | q81 |
| q86 | 0 | q87 |
| q86 | 1 | q87 |
| q86 | 2 | q87 |
| q86 | 3 | q87 |
| q86 | 4 | q87 |
| q86 | 5 | q87 |
| q86 | 6 | q87 |
| q86 | 7 | q87 |
| q86 | 8 | q87 |
| q86 | 9 | q87 |

## ER-03: Magia ofensiva

Extrair magia, alvo, dificuldade, bônus de resistência e dano.

**Alfabeto Σ:** ␠, '+', '-', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'

**Linguagem:** comandos completos no formato `/magia fogo alvo=goblin cd=12 bonus=3 dano=2d6`, com parâmetros nos domínios das convenções acima. A ordem e os espaços são obrigatórios.

**ER formal expandida:**

'/''m''a''g''i''a'␠ ('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z') (('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z' ∪ '0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9' ∪ '_'))* ␠'a''l''v''o''=' ('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z') (('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z' ∪ '0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9' ∪ '_'))* ␠'c''d''=' ('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')) ␠'b''o''n''u''s''=' (ε ∪ ('+' ∪ '-')) ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')) ␠'d''a''n''o''=' (('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '1' ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '2''0') 'd' ('4' ∪ '6' ∪ '8' ∪ '1''0' ∪ '1''2' ∪ '2''0' ∪ '1''0''0') (ε ∪ ('+' ∪ '-') ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')))

**Sintaxe exata em `rpg/patterns.py`, utilizada por Rule.pattern:**

```python
r"/magia\ (?P<magia>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ alvo=(?P<alvo>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ cd=(?P<cd>[123456789](?:|[0123456789]))\ bonus=(?P<bonus>(?:|[\+\-])[0123456789](?:|[0123456789]))\ dano=(?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))"
# re.fullmatch(rule.pattern, texto)
```

**AFNε:** início q0, final q1; 97 estados e 307 transições elementares. Arquivos `automata/magia.dot`, `.svg`, `.jff`. O SVG agrupa transições paralelas de um caractere; no JFLAP cada símbolo tem sua própria transição. `<read />` é movimento vazio.

| Cadeia | Esperado |
|---|---|
| `/magia a alvo=b cd=1 bonus=0 dano=1d4` | Aceita |
| `/magia fogo alvo=goblin cd=12 bonus=3 dano=2d6` | Aceita |
| `/magia gelo_2 alvo=orc_1 cd=99 bonus=-99 dano=20d100+99` | Aceita |
| `/magia raio alvo=a1 cd=20 bonus=+5 dano=1d20-99` | Aceita |
| `/magia fogo alvo=ana cd=2 bonus=00 dano=3d8` | Aceita |
| `/magia luz alvo=elfo cd=15 bonus=-1 dano=2d12+05` | Aceita |
| `` | Rejeitada |
| `/magia 2fogo alvo=b cd=1 bonus=0 dano=1d4` | Rejeitada |
| `/magia fogo alvo=_a cd=1 bonus=0 dano=1d4` | Rejeitada |
| `/magia fogo alvo=b cd=00 bonus=0 dano=1d4` | Rejeitada |
| `/magia fogo alvo=b cd=1 bonus=0 dano=1d7` | Rejeitada |
| `/magia fogo alvo=b bonus=0 cd=1 dano=1d4` | Rejeitada |

Caso-limite: primeira cadeia aceita usa os mínimos; a segunda ou terceira explora limites superiores. A cadeia vazia é rejeitada.

**Transições completas:**

| Origem | Símbolo | Destino |
|---|---|---|
| q0 | / | q3 |
| q3 | m | q4 |
| q4 | a | q5 |
| q5 | g | q6 |
| q6 | i | q7 |
| q7 | a | q8 |
| q8 | ␠ | q2 |
| q2 | a | q10 |
| q2 | b | q10 |
| q2 | c | q10 |
| q2 | d | q10 |
| q2 | e | q10 |
| q2 | f | q10 |
| q2 | g | q10 |
| q2 | h | q10 |
| q2 | i | q10 |
| q2 | j | q10 |
| q2 | k | q10 |
| q2 | l | q10 |
| q2 | m | q10 |
| q2 | n | q10 |
| q2 | o | q10 |
| q2 | p | q10 |
| q2 | q | q10 |
| q2 | r | q10 |
| q2 | s | q10 |
| q2 | t | q10 |
| q2 | u | q10 |
| q2 | v | q10 |
| q2 | w | q10 |
| q2 | x | q10 |
| q2 | y | q10 |
| q2 | z | q10 |
| q10 | ε | q9 |
| q10 | ε | q11 |
| q12 | ε | q11 |
| q12 | ε | q9 |
| q11 | a | q12 |
| q11 | b | q12 |
| q11 | c | q12 |
| q11 | d | q12 |
| q11 | e | q12 |
| q11 | f | q12 |
| q11 | g | q12 |
| q11 | h | q12 |
| q11 | i | q12 |
| q11 | j | q12 |
| q11 | k | q12 |
| q11 | l | q12 |
| q11 | m | q12 |
| q11 | n | q12 |
| q11 | o | q12 |
| q11 | p | q12 |
| q11 | q | q12 |
| q11 | r | q12 |
| q11 | s | q12 |
| q11 | t | q12 |
| q11 | u | q12 |
| q11 | v | q12 |
| q11 | w | q12 |
| q11 | x | q12 |
| q11 | y | q12 |
| q11 | z | q12 |
| q11 | 0 | q12 |
| q11 | 1 | q12 |
| q11 | 2 | q12 |
| q11 | 3 | q12 |
| q11 | 4 | q12 |
| q11 | 5 | q12 |
| q11 | 6 | q12 |
| q11 | 7 | q12 |
| q11 | 8 | q12 |
| q11 | 9 | q12 |
| q11 | _ | q12 |
| q9 | ␠ | q14 |
| q14 | a | q15 |
| q15 | l | q16 |
| q16 | v | q17 |
| q17 | o | q18 |
| q18 | = | q13 |
| q13 | a | q20 |
| q13 | b | q20 |
| q13 | c | q20 |
| q13 | d | q20 |
| q13 | e | q20 |
| q13 | f | q20 |
| q13 | g | q20 |
| q13 | h | q20 |
| q13 | i | q20 |
| q13 | j | q20 |
| q13 | k | q20 |
| q13 | l | q20 |
| q13 | m | q20 |
| q13 | n | q20 |
| q13 | o | q20 |
| q13 | p | q20 |
| q13 | q | q20 |
| q13 | r | q20 |
| q13 | s | q20 |
| q13 | t | q20 |
| q13 | u | q20 |
| q13 | v | q20 |
| q13 | w | q20 |
| q13 | x | q20 |
| q13 | y | q20 |
| q13 | z | q20 |
| q20 | ε | q19 |
| q20 | ε | q21 |
| q22 | ε | q21 |
| q22 | ε | q19 |
| q21 | a | q22 |
| q21 | b | q22 |
| q21 | c | q22 |
| q21 | d | q22 |
| q21 | e | q22 |
| q21 | f | q22 |
| q21 | g | q22 |
| q21 | h | q22 |
| q21 | i | q22 |
| q21 | j | q22 |
| q21 | k | q22 |
| q21 | l | q22 |
| q21 | m | q22 |
| q21 | n | q22 |
| q21 | o | q22 |
| q21 | p | q22 |
| q21 | q | q22 |
| q21 | r | q22 |
| q21 | s | q22 |
| q21 | t | q22 |
| q21 | u | q22 |
| q21 | v | q22 |
| q21 | w | q22 |
| q21 | x | q22 |
| q21 | y | q22 |
| q21 | z | q22 |
| q21 | 0 | q22 |
| q21 | 1 | q22 |
| q21 | 2 | q22 |
| q21 | 3 | q22 |
| q21 | 4 | q22 |
| q21 | 5 | q22 |
| q21 | 6 | q22 |
| q21 | 7 | q22 |
| q21 | 8 | q22 |
| q21 | 9 | q22 |
| q21 | _ | q22 |
| q19 | ␠ | q24 |
| q24 | c | q25 |
| q25 | d | q26 |
| q26 | = | q23 |
| q23 | 1 | q28 |
| q23 | 2 | q28 |
| q23 | 3 | q28 |
| q23 | 4 | q28 |
| q23 | 5 | q28 |
| q23 | 6 | q28 |
| q23 | 7 | q28 |
| q23 | 8 | q28 |
| q23 | 9 | q28 |
| q28 | ε | q29 |
| q30 | ε | q27 |
| q29 | ε | q30 |
| q28 | ε | q31 |
| q32 | ε | q27 |
| q31 | 0 | q32 |
| q31 | 1 | q32 |
| q31 | 2 | q32 |
| q31 | 3 | q32 |
| q31 | 4 | q32 |
| q31 | 5 | q32 |
| q31 | 6 | q32 |
| q31 | 7 | q32 |
| q31 | 8 | q32 |
| q31 | 9 | q32 |
| q27 | ␠ | q34 |
| q34 | b | q35 |
| q35 | o | q36 |
| q36 | n | q37 |
| q37 | u | q38 |
| q38 | s | q39 |
| q39 | = | q33 |
| q33 | ε | q42 |
| q43 | ε | q41 |
| q42 | ε | q43 |
| q33 | ε | q44 |
| q45 | ε | q41 |
| q44 | + | q45 |
| q44 | - | q45 |
| q41 | 0 | q46 |
| q41 | 1 | q46 |
| q41 | 2 | q46 |
| q41 | 3 | q46 |
| q41 | 4 | q46 |
| q41 | 5 | q46 |
| q41 | 6 | q46 |
| q41 | 7 | q46 |
| q41 | 8 | q46 |
| q41 | 9 | q46 |
| q46 | ε | q47 |
| q48 | ε | q40 |
| q47 | ε | q48 |
| q46 | ε | q49 |
| q50 | ε | q40 |
| q49 | 0 | q50 |
| q49 | 1 | q50 |
| q49 | 2 | q50 |
| q49 | 3 | q50 |
| q49 | 4 | q50 |
| q49 | 5 | q50 |
| q49 | 6 | q50 |
| q49 | 7 | q50 |
| q49 | 8 | q50 |
| q49 | 9 | q50 |
| q40 | ␠ | q52 |
| q52 | d | q53 |
| q53 | a | q54 |
| q54 | n | q55 |
| q55 | o | q56 |
| q56 | = | q51 |
| q51 | ε | q58 |
| q59 | ε | q57 |
| q58 | 1 | q59 |
| q58 | 2 | q59 |
| q58 | 3 | q59 |
| q58 | 4 | q59 |
| q58 | 5 | q59 |
| q58 | 6 | q59 |
| q58 | 7 | q59 |
| q58 | 8 | q59 |
| q58 | 9 | q59 |
| q51 | ε | q60 |
| q61 | ε | q57 |
| q60 | 1 | q62 |
| q62 | 0 | q61 |
| q62 | 1 | q61 |
| q62 | 2 | q61 |
| q62 | 3 | q61 |
| q62 | 4 | q61 |
| q62 | 5 | q61 |
| q62 | 6 | q61 |
| q62 | 7 | q61 |
| q62 | 8 | q61 |
| q62 | 9 | q61 |
| q51 | ε | q63 |
| q64 | ε | q57 |
| q63 | 2 | q65 |
| q65 | 0 | q64 |
| q57 | d | q66 |
| q66 | ε | q68 |
| q69 | ε | q67 |
| q68 | 4 | q69 |
| q66 | ε | q70 |
| q71 | ε | q67 |
| q70 | 6 | q71 |
| q66 | ε | q72 |
| q73 | ε | q67 |
| q72 | 8 | q73 |
| q66 | ε | q74 |
| q75 | ε | q67 |
| q74 | 1 | q76 |
| q76 | 0 | q75 |
| q66 | ε | q77 |
| q78 | ε | q67 |
| q77 | 1 | q79 |
| q79 | 2 | q78 |
| q66 | ε | q80 |
| q81 | ε | q67 |
| q80 | 2 | q82 |
| q82 | 0 | q81 |
| q66 | ε | q83 |
| q84 | ε | q67 |
| q83 | 1 | q85 |
| q85 | 0 | q86 |
| q86 | 0 | q84 |
| q67 | ε | q87 |
| q88 | ε | q1 |
| q87 | ε | q88 |
| q67 | ε | q89 |
| q90 | ε | q1 |
| q89 | + | q91 |
| q89 | - | q91 |
| q91 | 0 | q92 |
| q91 | 1 | q92 |
| q91 | 2 | q92 |
| q91 | 3 | q92 |
| q91 | 4 | q92 |
| q91 | 5 | q92 |
| q91 | 6 | q92 |
| q91 | 7 | q92 |
| q91 | 8 | q92 |
| q91 | 9 | q92 |
| q92 | ε | q93 |
| q94 | ε | q90 |
| q93 | ε | q94 |
| q92 | ε | q95 |
| q96 | ε | q90 |
| q95 | 0 | q96 |
| q95 | 1 | q96 |
| q95 | 2 | q96 |
| q95 | 3 | q96 |
| q95 | 4 | q96 |
| q95 | 5 | q96 |
| q95 | 6 | q96 |
| q95 | 7 | q96 |
| q95 | 8 | q96 |
| q95 | 9 | q96 |

## ER-04: Cura

Extrair alvo e dados dos pontos de vida recuperados.

**Alfabeto Σ:** ␠, '+', '-', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'

**Linguagem:** comandos completos no formato `/curar ana 2d8+3`, com parâmetros nos domínios das convenções acima. A ordem e os espaços são obrigatórios.

**ER formal expandida:**

'/''c''u''r''a''r'␠ ('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z') (('a' ∪ 'b' ∪ 'c' ∪ 'd' ∪ 'e' ∪ 'f' ∪ 'g' ∪ 'h' ∪ 'i' ∪ 'j' ∪ 'k' ∪ 'l' ∪ 'm' ∪ 'n' ∪ 'o' ∪ 'p' ∪ 'q' ∪ 'r' ∪ 's' ∪ 't' ∪ 'u' ∪ 'v' ∪ 'w' ∪ 'x' ∪ 'y' ∪ 'z' ∪ '0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9' ∪ '_'))* ␠ (('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '1' ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') ∪ '2''0') 'd' ('4' ∪ '6' ∪ '8' ∪ '1''0' ∪ '1''2' ∪ '2''0' ∪ '1''0''0') (ε ∪ ('+' ∪ '-') ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')))

**Sintaxe exata em `rpg/patterns.py`, utilizada por Rule.pattern:**

```python
r"/curar\ (?P<alvo>[abcdefghijklmnopqrstuvwxyz](?:[abcdefghijklmnopqrstuvwxyz0123456789_])*)\ (?P<dados>(?:[123456789]|1[0123456789]|20)d(?:4|6|8|10|12|20|100)(?:|[\+\-][0123456789](?:|[0123456789])))"
# re.fullmatch(rule.pattern, texto)
```

**AFNε:** início q0, final q1; 54 estados e 162 transições elementares. Arquivos `automata/curar.dot`, `.svg`, `.jff`. O SVG agrupa transições paralelas de um caractere; no JFLAP cada símbolo tem sua própria transição. `<read />` é movimento vazio.

| Cadeia | Esperado |
|---|---|
| `/curar a 1d4` | Aceita |
| `/curar ana 2d8+3` | Aceita |
| `/curar elfo_2 20d100+99` | Aceita |
| `/curar x1 1d20-99` | Aceita |
| `/curar paladino 3d12+05` | Aceita |
| `/curar clerigo 10d10+0` | Aceita |
| `` | Rejeitada |
| `/curar 1ana 1d4` | Rejeitada |
| `/curar Ana 1d4` | Rejeitada |
| `/curar ana 21d6` | Rejeitada |
| `/curar ana 1d6+100` | Rejeitada |
| `/curar ana  1d4` | Rejeitada |

Caso-limite: primeira cadeia aceita usa os mínimos; a segunda ou terceira explora limites superiores. A cadeia vazia é rejeitada.

**Transições completas:**

| Origem | Símbolo | Destino |
|---|---|---|
| q0 | / | q3 |
| q3 | c | q4 |
| q4 | u | q5 |
| q5 | r | q6 |
| q6 | a | q7 |
| q7 | r | q8 |
| q8 | ␠ | q2 |
| q2 | a | q10 |
| q2 | b | q10 |
| q2 | c | q10 |
| q2 | d | q10 |
| q2 | e | q10 |
| q2 | f | q10 |
| q2 | g | q10 |
| q2 | h | q10 |
| q2 | i | q10 |
| q2 | j | q10 |
| q2 | k | q10 |
| q2 | l | q10 |
| q2 | m | q10 |
| q2 | n | q10 |
| q2 | o | q10 |
| q2 | p | q10 |
| q2 | q | q10 |
| q2 | r | q10 |
| q2 | s | q10 |
| q2 | t | q10 |
| q2 | u | q10 |
| q2 | v | q10 |
| q2 | w | q10 |
| q2 | x | q10 |
| q2 | y | q10 |
| q2 | z | q10 |
| q10 | ε | q9 |
| q10 | ε | q11 |
| q12 | ε | q11 |
| q12 | ε | q9 |
| q11 | a | q12 |
| q11 | b | q12 |
| q11 | c | q12 |
| q11 | d | q12 |
| q11 | e | q12 |
| q11 | f | q12 |
| q11 | g | q12 |
| q11 | h | q12 |
| q11 | i | q12 |
| q11 | j | q12 |
| q11 | k | q12 |
| q11 | l | q12 |
| q11 | m | q12 |
| q11 | n | q12 |
| q11 | o | q12 |
| q11 | p | q12 |
| q11 | q | q12 |
| q11 | r | q12 |
| q11 | s | q12 |
| q11 | t | q12 |
| q11 | u | q12 |
| q11 | v | q12 |
| q11 | w | q12 |
| q11 | x | q12 |
| q11 | y | q12 |
| q11 | z | q12 |
| q11 | 0 | q12 |
| q11 | 1 | q12 |
| q11 | 2 | q12 |
| q11 | 3 | q12 |
| q11 | 4 | q12 |
| q11 | 5 | q12 |
| q11 | 6 | q12 |
| q11 | 7 | q12 |
| q11 | 8 | q12 |
| q11 | 9 | q12 |
| q11 | _ | q12 |
| q9 | ␠ | q13 |
| q13 | ε | q15 |
| q16 | ε | q14 |
| q15 | 1 | q16 |
| q15 | 2 | q16 |
| q15 | 3 | q16 |
| q15 | 4 | q16 |
| q15 | 5 | q16 |
| q15 | 6 | q16 |
| q15 | 7 | q16 |
| q15 | 8 | q16 |
| q15 | 9 | q16 |
| q13 | ε | q17 |
| q18 | ε | q14 |
| q17 | 1 | q19 |
| q19 | 0 | q18 |
| q19 | 1 | q18 |
| q19 | 2 | q18 |
| q19 | 3 | q18 |
| q19 | 4 | q18 |
| q19 | 5 | q18 |
| q19 | 6 | q18 |
| q19 | 7 | q18 |
| q19 | 8 | q18 |
| q19 | 9 | q18 |
| q13 | ε | q20 |
| q21 | ε | q14 |
| q20 | 2 | q22 |
| q22 | 0 | q21 |
| q14 | d | q23 |
| q23 | ε | q25 |
| q26 | ε | q24 |
| q25 | 4 | q26 |
| q23 | ε | q27 |
| q28 | ε | q24 |
| q27 | 6 | q28 |
| q23 | ε | q29 |
| q30 | ε | q24 |
| q29 | 8 | q30 |
| q23 | ε | q31 |
| q32 | ε | q24 |
| q31 | 1 | q33 |
| q33 | 0 | q32 |
| q23 | ε | q34 |
| q35 | ε | q24 |
| q34 | 1 | q36 |
| q36 | 2 | q35 |
| q23 | ε | q37 |
| q38 | ε | q24 |
| q37 | 2 | q39 |
| q39 | 0 | q38 |
| q23 | ε | q40 |
| q41 | ε | q24 |
| q40 | 1 | q42 |
| q42 | 0 | q43 |
| q43 | 0 | q41 |
| q24 | ε | q44 |
| q45 | ε | q1 |
| q44 | ε | q45 |
| q24 | ε | q46 |
| q47 | ε | q1 |
| q46 | + | q48 |
| q46 | - | q48 |
| q48 | 0 | q49 |
| q48 | 1 | q49 |
| q48 | 2 | q49 |
| q48 | 3 | q49 |
| q48 | 4 | q49 |
| q48 | 5 | q49 |
| q48 | 6 | q49 |
| q48 | 7 | q49 |
| q48 | 8 | q49 |
| q48 | 9 | q49 |
| q49 | ε | q50 |
| q51 | ε | q47 |
| q50 | ε | q51 |
| q49 | ε | q52 |
| q53 | ε | q47 |
| q52 | 0 | q53 |
| q52 | 1 | q53 |
| q52 | 2 | q53 |
| q52 | 3 | q53 |
| q52 | 4 | q53 |
| q52 | 5 | q53 |
| q52 | 6 | q53 |
| q52 | 7 | q53 |
| q52 | 8 | q53 |
| q52 | 9 | q53 |

## ER-05: Teste de atributo

Extrair atributo, bônus e classe de dificuldade.

**Alfabeto Σ:** ␠, '+', '-', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '=', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'i', 'l', 'm', 'n', 'o', 'r', 's', 't', 'u', 'z'

**Linguagem:** comandos completos no formato `/teste forca bonus=-2 cd=15`, com parâmetros nos domínios das convenções acima. A ordem e os espaços são obrigatórios.

**ER formal expandida:**

'/''t''e''s''t''e'␠ ('f''o''r''c''a' ∪ 'd''e''s''t''r''e''z''a' ∪ 'c''o''n''s''t''i''t''u''i''c''a''o' ∪ 'i''n''t''e''l''i''g''e''n''c''i''a' ∪ 's''a''b''e''d''o''r''i''a' ∪ 'c''a''r''i''s''m''a') ␠'b''o''n''u''s''=' (ε ∪ ('+' ∪ '-')) ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9')) ␠'c''d''=' ('1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9') (ε ∪ ('0' ∪ '1' ∪ '2' ∪ '3' ∪ '4' ∪ '5' ∪ '6' ∪ '7' ∪ '8' ∪ '9'))

**Sintaxe exata em `rpg/patterns.py`, utilizada por Rule.pattern:**

```python
r"/teste\ (?P<atributo>(?:forca|destreza|constituicao|inteligencia|sabedoria|carisma))\ bonus=(?P<bonus>(?:|[\+\-])[0123456789](?:|[0123456789]))\ cd=(?P<cd>[123456789](?:|[0123456789]))"
# re.fullmatch(rule.pattern, texto)
```

**AFNε:** início q0, final q1; 96 estados e 139 transições elementares. Arquivos `automata/teste.dot`, `.svg`, `.jff`. O SVG agrupa transições paralelas de um caractere; no JFLAP cada símbolo tem sua própria transição. `<read />` é movimento vazio.

| Cadeia | Esperado |
|---|---|
| `/teste forca bonus=0 cd=1` | Aceita |
| `/teste destreza bonus=-99 cd=99` | Aceita |
| `/teste constituicao bonus=+5 cd=12` | Aceita |
| `/teste inteligencia bonus=00 cd=20` | Aceita |
| `/teste sabedoria bonus=-1 cd=15` | Aceita |
| `/teste carisma bonus=99 cd=2` | Aceita |
| `` | Rejeitada |
| `/teste sorte bonus=0 cd=1` | Rejeitada |
| `/teste forca bonus=100 cd=1` | Rejeitada |
| `/teste forca bonus=0 cd=0` | Rejeitada |
| `/teste forca cd=1 bonus=0` | Rejeitada |
| `/teste forca bonus=0 cd=1 ` | Rejeitada |

Caso-limite: primeira cadeia aceita usa os mínimos; a segunda ou terceira explora limites superiores. A cadeia vazia é rejeitada.

**Transições completas:**

| Origem | Símbolo | Destino |
|---|---|---|
| q0 | / | q3 |
| q3 | t | q4 |
| q4 | e | q5 |
| q5 | s | q6 |
| q6 | t | q7 |
| q7 | e | q8 |
| q8 | ␠ | q2 |
| q2 | ε | q10 |
| q11 | ε | q9 |
| q10 | f | q12 |
| q12 | o | q13 |
| q13 | r | q14 |
| q14 | c | q15 |
| q15 | a | q11 |
| q2 | ε | q16 |
| q17 | ε | q9 |
| q16 | d | q18 |
| q18 | e | q19 |
| q19 | s | q20 |
| q20 | t | q21 |
| q21 | r | q22 |
| q22 | e | q23 |
| q23 | z | q24 |
| q24 | a | q17 |
| q2 | ε | q25 |
| q26 | ε | q9 |
| q25 | c | q27 |
| q27 | o | q28 |
| q28 | n | q29 |
| q29 | s | q30 |
| q30 | t | q31 |
| q31 | i | q32 |
| q32 | t | q33 |
| q33 | u | q34 |
| q34 | i | q35 |
| q35 | c | q36 |
| q36 | a | q37 |
| q37 | o | q26 |
| q2 | ε | q38 |
| q39 | ε | q9 |
| q38 | i | q40 |
| q40 | n | q41 |
| q41 | t | q42 |
| q42 | e | q43 |
| q43 | l | q44 |
| q44 | i | q45 |
| q45 | g | q46 |
| q46 | e | q47 |
| q47 | n | q48 |
| q48 | c | q49 |
| q49 | i | q50 |
| q50 | a | q39 |
| q2 | ε | q51 |
| q52 | ε | q9 |
| q51 | s | q53 |
| q53 | a | q54 |
| q54 | b | q55 |
| q55 | e | q56 |
| q56 | d | q57 |
| q57 | o | q58 |
| q58 | r | q59 |
| q59 | i | q60 |
| q60 | a | q52 |
| q2 | ε | q61 |
| q62 | ε | q9 |
| q61 | c | q63 |
| q63 | a | q64 |
| q64 | r | q65 |
| q65 | i | q66 |
| q66 | s | q67 |
| q67 | m | q68 |
| q68 | a | q62 |
| q9 | ␠ | q70 |
| q70 | b | q71 |
| q71 | o | q72 |
| q72 | n | q73 |
| q73 | u | q74 |
| q74 | s | q75 |
| q75 | = | q69 |
| q69 | ε | q78 |
| q79 | ε | q77 |
| q78 | ε | q79 |
| q69 | ε | q80 |
| q81 | ε | q77 |
| q80 | + | q81 |
| q80 | - | q81 |
| q77 | 0 | q82 |
| q77 | 1 | q82 |
| q77 | 2 | q82 |
| q77 | 3 | q82 |
| q77 | 4 | q82 |
| q77 | 5 | q82 |
| q77 | 6 | q82 |
| q77 | 7 | q82 |
| q77 | 8 | q82 |
| q77 | 9 | q82 |
| q82 | ε | q83 |
| q84 | ε | q76 |
| q83 | ε | q84 |
| q82 | ε | q85 |
| q86 | ε | q76 |
| q85 | 0 | q86 |
| q85 | 1 | q86 |
| q85 | 2 | q86 |
| q85 | 3 | q86 |
| q85 | 4 | q86 |
| q85 | 5 | q86 |
| q85 | 6 | q86 |
| q85 | 7 | q86 |
| q85 | 8 | q86 |
| q85 | 9 | q86 |
| q76 | ␠ | q88 |
| q88 | c | q89 |
| q89 | d | q90 |
| q90 | = | q87 |
| q87 | 1 | q91 |
| q87 | 2 | q91 |
| q87 | 3 | q91 |
| q87 | 4 | q91 |
| q87 | 5 | q91 |
| q87 | 6 | q91 |
| q87 | 7 | q91 |
| q87 | 8 | q91 |
| q87 | 9 | q91 |
| q91 | ε | q92 |
| q93 | ε | q1 |
| q92 | ε | q93 |
| q91 | ε | q94 |
| q95 | ε | q1 |
| q94 | 0 | q95 |
| q94 | 1 | q95 |
| q94 | 2 | q95 |
| q94 | 3 | q95 |
| q94 | 4 | q95 |
| q94 | 5 | q95 |
| q94 | 6 | q95 |
| q94 | 7 | q95 |
| q94 | 8 | q95 |
| q94 | 9 | q95 |
