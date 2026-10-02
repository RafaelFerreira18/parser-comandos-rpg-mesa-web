# Parser de Comandos de RPG de Mesa (Web)

Aplicação didática de Linguagens Formais e Autômatos: cinco expressões regulares reconhecem comandos completos, extraem parâmetros e executam ações de RPG. Interface web em JavaScript, backend e menu CLI em Python 3.10+ (recomendado 3.11+), exclusivamente com biblioteca padrão.

## Executar

Na pasta do projeto, com Python instalado e disponível no terminal:

```powershell
python -m rpg.server
```

Abra http://127.0.0.1:8000. Para outra porta: `python -m rpg.server --port 8080`. Ctrl+C encerra o servidor. Não abra `web/index.html` diretamente: ele depende da API local.

Menu CLI:

```powershell
python -m rpg.cli
```

Não é necessário instalar pacotes com pip. `requirements.txt` registra a ausência de dependências da aplicação. O servidor padrão atende somente à máquina local. É um servidor de demonstração, sem autenticação ou recursos de produção.

## Comandos

| Ação | Exemplo | Resultado |
|---|---|---|
| Dados | `/rolar 2d6+3` | Valores individuais, modificador e total |
| Ataque | `/atacar goblin bonus=5 ca=14 dano=1d8+2` | d20 + bônus ≥ CA: acerto e dano; caso contrário, dano zero |
| Magia | `/magia fogo alvo=goblin cd=12 bonus=3 dano=2d6` | Alvo faz d20 + bônus; resistência ≥ CD reduz dano à metade |
| Cura | `/curar ana 2d8+3` | Pontos de vida recuperados |
| Atributo | `/teste forca bonus=-2 cd=15` | d20 + bônus ≥ CD: sucesso |

Sintaxe estrita: minúsculas, um espaço ASCII entre campos, sem espaços externos, campos na ordem dos exemplos. Nomes: uma letra a-z seguida de letras a-z, números ou `_`. Atributos: forca, destreza, constituicao, inteligencia, sabedoria, carisma.

Dados: quantidade 1 a 20, faces 4/6/8/10/12/20/100. Modificador opcional com sinal e um ou dois dígitos. Bônus: sinal opcional e um ou dois dígitos (inclui 00, +05 e -00). CA/CD: 1 a 99, sem zero inicial. Quantidade também não admite zero inicial.

Rolagens podem ter total negativo. Dano e cura têm piso zero. Não há críticos ou regras oficiais de D&D: este é um sistema didático independente. Em magia, `sucesso` indica que o alvo falhou na resistência; `resistencia_sucesso` informa o resultado da resistência. Nomes de magias não são consultados em catálogo. Não há fichas, consumo de recursos ou alteração persistente de PV.

A validação ocorre 300 ms após parar de digitar e não consome aleatoriedade. O botão Executar faz uma rolagem. O histórico mantém até 30 ações enquanto a página permanece aberta. O limite de entrada do serviço é 512 caracteres; a linguagem regular permite nomes de comprimento arbitrário. Essa restrição operacional é separada da sintaxe.

## Testes

```powershell
python -m unittest discover -v
```

14 métodos de teste cobrem 60 cadeias obrigatórias (6 aceitas e 6 rejeitadas por ER), 1.500 mutações com semente fixa comparando regex/AFNε, simulação dos `.jff` exportados, regras determinísticas de jogo, limites e HTTP. Os testes geram um servidor temporário em porta livre e o encerram.

## Materiais da entrega

O relatório também está disponível como `docs/relatorio-tecnico.tex`, um documento LaTeX independente com diagramas vetoriais leves e tabelas completas de transições. Para Overleaf, importe `docs/relatorio-overleaf.zip` em **New Project > Upload Project**, mantenha `main.tex` como arquivo principal e use **pdfLaTeX**. Os desenhos não dependem de TikZ durante a compilação e cada faixa processa somente os caminhos visíveis. Consulte `docs/LEIA-ME-OVERLEAF.txt`. A compilação integrada não pôde ser confirmada por uma falha de inicialização do ambiente; o PDF anterior foi preservado.

- `docs/relatorio-tecnico.pdf`: relatório e fichas das cinco ER, com apêndice de AFNε em páginas largas para zoom.
- `docs/apresentacao.pdf`: apresentação, incluindo fichas e apêndice de autômatos.
- `docs/expressoes-regulares.md`: padrões exatos, formal expandida, alfabetos, exemplos e todas as transições.
- `docs/manifest.json`: dados das fichas gerados da mesma definição do código.
- `docs/roteiro-apresentacao.md`: roteiro para 10-12 minutos, com demonstração.
- `docs/contribuicoes.md`: registro a completar com nomes e contribuições reais.
- `docs/checklist-entrega.md`: correspondência dos requisitos e pendências administrativas.
- `docs/resultados-testes.txt`: execução registrada dos testes.
- `examples/cases.json`: entradas aceitas/rejeitadas para estudo e demonstração.
- `automata/`: 5 `.dot`, 5 `.svg`, 5 `.jff` compatíveis com o formato de autômatos finitos JFLAP 7.

## Organização e equivalência

`rpg/language.py` define uma árvore com literais, classes finitas, união, concatenação e fecho. Dela derivam os padrões literais em `rpg/patterns.py`, usados por `re.fullmatch`, a notação formal e os AFNε de `rpg/automata.py`. A construção composicional usa ramificações ε na união e laços ε no fecho. Capturas nomeadas identificam parâmetros e não alteram a linguagem. Não há recursos de regex não regulares.

`rpg/engine.py` interpreta e executa; `rpg/server.py` fornece HTTP; `rpg/cli.py` fornece o menu; `web/` contém a interface. As fichas exibem exatamente o padrão calculado por `Rule.pattern`. Os testes por amostragem detectam divergências, mas não constituem prova exaustiva de equivalência; a equivalência estrutural segue da tradução de cada operador.

## Regenerar materiais

```powershell
python tools/export_materials.py
```

Se tiver Graphviz instalado, execute para cada comando:

```powershell
dot -Tsvg automata/rolar.dot -o automata/rolar.svg
```

Os SVG entregues já foram gerados com Graphviz via @viz-js/viz (WebAssembly). Opcionalmente, Node.js com `@viz-js/viz` pode executar `node tools/render_graphs.mjs`. Isso é ferramenta de documentação, não dependência da aplicação. Para os PDFs, `tools/build_pdfs.py` requer ReportLab, pypdf, fontes do Windows e os layouts Graphviz produzidos pelo renderizador. Os PDFs prontos não exigem essas ferramentas para leitura.

No JFLAP 7: File > Open > escolha `.jff`; Input > Multiple Run para testar cadeias. Para a cadeia vazia, deixe a entrada em branco. `<read />` representa ε. A compatibilidade foi verificada lendo o XML e simulando suas transições; a GUI do JFLAP não foi executada neste ambiente.

## VS Code e Git/GitHub

Abra esta pasta no VS Code, selecione um interpretador Python 3.10+ e use o terminal integrado. O repositório local já está configurado para [RafaelFerreira18/parser-comandos-rpg-mesa-web](https://github.com/RafaelFerreira18/parser-comandos-rpg-mesa-web). A implementação desta entrega está local; após revisar e preencher a identificação, publique as alterações, mantenha o repositório acessível e envie o link definitivo no Classroom. Consulte o checklist.

## Autoria e uso de IA

OpenAI Codex foi utilizado como apoio na estruturação, implementação inicial, geração de documentação/autômatos, elaboração de testes e materiais de apresentação. A equipe deve revisar o conteúdo, registrar suas contribuições reais, compreender as expressões e conseguir modificar o programa. Os nomes e contribuições dos integrantes estão pendentes de preenchimento; a publicação no GitHub precisa ser concluída.

Fontes: lauda fornecida pelo professor; `GUIA_SINTAXE_EXPRESSOES_REGULARES_TRABALHO_LFA - FINAL.pdf`; documentação da biblioteca padrão Python (`re`, `unittest`, `http.server`, `random`); Graphviz e JFLAP. A lauda informa 02/10/2026 no cabeçalho e 30/09/2026 em uma etapa; o guia informa 30/09/2026. Confirme com o professor qual prazo prevalece.
