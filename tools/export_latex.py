"""Gera um relatório LaTeX independente, com desenhos TikZ e ZIP para Overleaf.

Usa a definição regular e os layouts Graphviz já gerados no projeto.
Não exige bibliotecas Python externas. Compilar o .tex exige LaTeX/TikZ.
"""
from pathlib import Path
from collections import defaultdict
from zipfile import ZipFile, ZIP_DEFLATED
import json
import math
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from rpg.language import RULES
from rpg.automata import compile_nfa


def esc(text):
    mapping = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
               "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
               "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(mapping.get(char, char) for char in text)


def coord(point):
    return "(" + ",".join(f"{value:.2f}" for value in point) + ")"


def diagram_ops(ops):
    lines = []
    size = 10
    for op in ops:
        kind = op["op"]
        if kind == "F":
            size = op["size"]
        elif kind in ("e", "E"):
            x, y, rx, ry = op["rect"]
            command = "filldraw" if kind == "E" else "draw"
            lines.append("\\" + command + " " + coord((x, y)) + f" ellipse [x radius={rx:.2f}bp,y radius={ry:.2f}bp];")
        elif kind in ("b", "B"):
            points = op["points"]
            line = r"\draw " + coord(points[0])
            for i in range(1, len(points), 3):
                line += " .. controls " + coord(points[i]) + " and " + coord(points[i+1]) + " .. " + coord(points[i+2])
            lines.append(line + ";")
        elif kind in ("P", "p", "L"):
            lines.append((r"\filldraw " if kind == "P" else r"\draw ") + " -- ".join(coord(p) for p in op["points"]) + (" -- cycle;" if kind != "L" else ";"))
        elif kind == "T":
            text = op["text"]
            if text.startswith("q") and text[1:].isdigit(): text = "$q_{" + text[1:] + "}$"
            elif text == "ε": text = r"$\varepsilon$"
            else: text = esc(text.replace("␠", "SP"))
            anchor = {"c": "base", "l": "base west", "r": "base east"}[op["align"]]
            lines.append(r"\node[anchor=" + anchor + r",inner sep=0pt,font=\fontsize{" + str(size) + "}{" + str(size+2) + r"}\selectfont] at " + coord(op["pt"]) + " {" + text + "};")
    return lines


PREAMBLE = r"""% Relatório independente: abrir este arquivo e compilar com pdfLaTeX.
% Compatível com Overleaf, sem shell-escape ou arquivos externos.
\documentclass[12pt,a4paper]{article}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage[brazil]{babel}
\usepackage{lmodern}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{amsmath,amssymb}
\usepackage{graphicx,tikz}
\usepackage{pdflscape}
\usepackage{booktabs,longtable,array}
\usepackage{xcolor,listings}
\usepackage{microtype}
\usepackage{hyperref}
\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue,pdftitle={Parser de Comandos de RPG de Mesa (Web)},pdfauthor={Rafael Batista Ferreria e Paulo Ricardo da Rocha}}
\setlength{\parindent}{1.25cm}
\setlength{\parskip}{0.35em}
\renewcommand{\arraystretch}{1.15}
\emergencystretch=2em
\lstdefinestyle{codigo}{basicstyle=\ttfamily\footnotesize,breaklines=true,breakatwhitespace=false,columns=fullflexible,keepspaces=true,showstringspaces=false,frame=single,rulecolor=\color{gray},xleftmargin=0pt,xrightmargin=0pt,aboveskip=0.6em,belowskip=0.6em}
\lstset{style=codigo}
\newcommand{\lit}[1]{\texttt{#1}}
\newcommand{\SP}{\mathrm{SP}}
\newcommand{\eps}{\varepsilon}
\newcommand{\cadeia}[1]{{\ttfamily\footnotesize\detokenize{#1}}}
"""

BODY = r"""
\begin{document}
\begin{titlepage}
\centering
{\large Linguagens Formais e Autômatos\par}
\vspace{2.5cm}
{\LARGE\bfseries Parser de Comandos de RPG de Mesa (Web)\par}
\vspace{1cm}
{\Large Relatório técnico\par}
\vspace{2cm}
{\large Rafael Batista Ferreria\par Paulo Ricardo da Rocha\par}
\vfill
\begin{minipage}{0.9\textwidth}
\centering
Projeto de aplicação de expressões regulares, com interface web e CLI, cinco linguagens regulares, AFN$\varepsilon$, testes e documentação.\\[1em]
\url{https://github.com/RafaelFerreira18/parser-comandos-rpg-mesa-web}
\end{minipage}
\vspace{1.5cm}
{\large Outubro de 2026\par}
\end{titlepage}

\begin{abstract}
Este trabalho apresenta uma aplicação que interpreta comandos textuais de RPG de mesa. Cinco expressões regulares reconhecem rolagens de dados, ataques, magias ofensivas, curas e testes de atributo. O programa valida a entrada completa, extrai parâmetros com grupos nomeados e calcula os resultados. A implementação usa Python com biblioteca padrão no backend e JavaScript na interface web, além de um menu CLI. Uma representação estrutural das expressões gera os padrões Python e os autômatos finitos não determinísticos com movimentos vazios. Os testes confrontam as regex, a simulação dos AFN$\varepsilon$ e os arquivos JFLAP exportados. O relatório documenta as linguagens, os operadores, os testes, as regras de execução e as limitações do sistema.
\end{abstract}
\noindent\textbf{Palavras-chave:} expressões regulares; linguagens regulares; autômatos finitos; parser; RPG de mesa.
\tableofcontents
\clearpage

\section{Introdução e problema}
Em partidas de RPG de mesa, comandos de texto podem representar ações como lançar dados, atacar uma criatura ou recuperar pontos de vida. Antes de executar uma ação, é necessário reconhecer seu tipo e verificar se os parâmetros seguem uma sintaxe definida. O projeto relaciona a fundamentação de Linguagens Formais e Autômatos a uma aplicação funcional de validação e interpretação de comandos.

A entrada é uma cadeia digitada no navegador ou no menu CLI. O processamento aplica correspondência completa, captura os parâmetros e executa regras didáticas de rolagem. A saída apresenta mensagens, valores individuais, total, sucesso ou falha, dano ou cura. Uma falha da ação no jogo é diferente de uma entrada com sintaxe inválida.

\section{Objetivos e requisitos}
O objetivo geral é implementar um interpretador de comandos cuja validação se apoie em cinco expressões regulares distintas e relevantes. Os objetivos específicos são:
\begin{itemize}
\item reconhecer rolagem, ataque, magia, cura e teste de atributo;
\item tratar entradas vazias, inválidas ou acima dos limites operacionais;
\item oferecer interface web com atualização sem recarregar a página e CLI com menu;
\item documentar alfabeto, linguagem, formal, padrão implementado e operadores de cada ER;
\item fornecer AFN$\varepsilon$, arquivos Graphviz e JFLAP e testes com seis aceitas e seis rejeitadas por ER;
\item verificar as regras de execução e registrar resultados e limitações.
\end{itemize}

\section{Arquitetura e tecnologias}
A aplicação usa Python 3.10 ou superior, com recomendação de Python 3.11 ou superior. O backend e os testes dependem somente da biblioteca padrão: \lit{re}, \lit{dataclasses}, \lit{random}, \lit{http.server}, \lit{json}, \lit{argparse} e \lit{unittest}. O frontend usa HTML, CSS e JavaScript com \lit{fetch}. Graphviz e JFLAP são ferramentas de documentação, e não dependências da execução do aplicativo.

\begin{center}
\begin{tabular}{p{0.33\textwidth}p{0.57\textwidth}}
\toprule
\textbf{Arquivo ou diretório} & \textbf{Responsabilidade}\\
\midrule
\lit{rpg/language.py} & Definição estrutural das linguagens regulares.\\
\lit{rpg/patterns.py} & Padrões Python literais gerados e usados no parser.\\
\lit{rpg/engine.py} & Validação, extração e regras do jogo.\\
\lit{rpg/automata.py} & Construção e simulação dos AFN$\varepsilon$.\\
\lit{rpg/server.py} & Servidor HTTP e API local.\\
\lit{rpg/cli.py} & Menu interativo.\\
\lit{web/} & Interface de navegador.\\
\lit{tests/}, \lit{examples/} & Testes automatizados e cadeias de exemplo.\\
\lit{automata/}, \lit{docs/} & Diagramas, arquivos JFLAP e documentação.\\
\bottomrule
\end{tabular}
\end{center}

O fluxo é entrada textual, chamada HTTP, correspondência com \lit{re.fullmatch}, captura dos parâmetros, execução e retorno JSON. A interface consulta \lit{/api/validar} após 300~ms sem alterações na entrada. Essa consulta não lança dados. O envio explícito usa \lit{/api/executar}. O histórico no navegador mantém até 30 ações durante a sessão da página.

\section{Contrato de entrada e regras de execução}
\subsection{Sintaxe e domínios}
Os comandos são sensíveis à caixa: somente letras minúsculas ASCII são aceitas. Cada separador corresponde exatamente ao espaço U+0020. Não se removem espaços externos nem se reordena a entrada. Identificadores começam com uma letra de \lit{a} a \lit{z} e continuam com letras, dígitos ou sublinhado.

A quantidade de dados vai de 1 a 20, sem zero inicial. As faces permitidas são 4, 6, 8, 10, 12, 20 e 100. O modificador de dados é opcional e, quando presente, contém sinal e um ou dois dígitos. O bônus admite sinal opcional e um ou dois dígitos, inclusive \lit{00}, \lit{+05} e \lit{-00}. CA e CD vão de 1 a 99 e não admitem zero inicial.

\subsection{Regras didáticas}
Uma rolagem simples soma os valores individuais e o modificador; seu total pode ser negativo. Um ataque acerta quando $d20+\text{bônus}\geq\text{CA}$. Se acertar, causa o dano rolado, com piso zero. Se falhar, não lança os dados de dano e causa zero. Um teste de atributo tem sucesso quando $d20+\text{bônus}\geq\text{CD}$.

Na magia ofensiva, o alvo faz uma resistência de $d20+\text{bônus}$ contra a CD. Resistência bem-sucedida reduz o dano à metade, arredondada para baixo. O campo \lit{sucesso} indica que a magia superou a resistência, enquanto \lit{resistencia\_sucesso} indica o resultado do alvo. A cura informa pontos de vida recuperados, com piso zero. O programa não altera fichas persistentes.

\subsection{Limites operacionais}
O serviço aceita até 512 caracteres por comando e até 4096 bytes no corpo HTTP. A leitura possui timeout. Esses limites são separados das cinco expressões regulares: a linguagem formal admite identificadores de comprimento arbitrário. A rejeição operacional de uma cadeia longa não é uma mudança no AFN$\varepsilon$ ou na ER.

\section{Fundamentação formal e equivalência}
\subsection{Convenções}
União é representada por $\cup$, concatenação por justaposição e fecho de Kleene por $*$. A palavra vazia é $\eps$. Classes finitas representam união de símbolos. Opcionalidade equivale à união com $\eps$. Literais de várias letras são a concatenação de seus caracteres; a fonte monoespaçada apenas os distingue da metanotação.

As abreviações abaixo são expressões formais, e não padrões adicionais independentes. Seja $D$ o conjunto dos dez dígitos, $U$ o conjunto dos nove dígitos diferentes de zero e $L$ o conjunto das 26 letras minúsculas ASCII. Quando um conjunto aparece em uma ER, representa a união de seus símbolos.
\begin{align*}
D &= \{0,1,2,3,4,5,6,7,8,9\},\\
U &= \{1,2,3,4,5,6,7,8,9\},\\
L &= \{a,b,c,\ldots,z\},\\
\SP &= \text{espaço U+0020},\\
I &= L(L\cup D\cup\{\lit{\_}\})^*,\\
N &= U(\eps\cup D),\\
B &= (\eps\cup\lit{+}\cup\lit{-})D(\eps\cup D),\\
Q &= U\cup\lit{1}D\cup\lit{20},\\
F &= \lit{4}\cup\lit{6}\cup\lit{8}\cup\lit{10}\cup\lit{12}\cup\lit{20}\cup\lit{100},\\
R &= Q\lit{d}F\bigl(\eps\cup(\lit{+}\cup\lit{-})D(\eps\cup D)\bigr).
\end{align*}
Para os atributos:
\[
\begin{aligned}
A={}&\lit{forca}\cup\lit{destreza}\cup\lit{constituicao}\\
&\cup\lit{inteligencia}\cup\lit{sabedoria}\cup\lit{carisma}.
\end{aligned}
\]

\subsection{Correspondência com Python}
Alternância \lit{|} implementa união; sequência de padrões implementa concatenação; \lit{*} implementa fecho. Grupos \lit{(?:...)} organizam sem capturar. Grupos \lit{(?P<nome>...)} capturam parâmetros sem alterar a linguagem aceita. Uma alternativa vazia, como \lit{(?:|r)}, corresponde a $\eps\cup r$. O escape \lit{\textbackslash{} } representa um espaço literal no padrão. A validação usa \lit{re.fullmatch}, sem flags; portanto, não depende da interpretação de âncoras de fim de linha.

\subsection{Construção e equivalência dos AFN\texorpdfstring{$\varepsilon$}{epsilon}}
O autômato é construído por tradução estrutural. Um literal usa uma transição por caractere. Uma classe finita usa transições paralelas. A concatenação compartilha fronteiras de fragmentos. A união acrescenta caminhos alternativos com movimentos vazios. O fecho acrescenta o caminho vazio e o retorno que permite repetição. Capturas são ignoradas na construção porque não alteram a linguagem.

Por indução sobre a árvore de expressão, cada operador conserva a linguagem descrita. Essa construção fundamenta a equivalência entre formal, padrão e AFN$\varepsilon$. Os testes verificam se a implementação e as exportações apresentam divergências, sem substituir a argumentação estrutural por uma amostragem.

Os diagramas do apêndice preservam as posições e curvas calculadas pelo Graphviz. Rótulos com classes agrupam transições paralelas de um único símbolo. Os arquivos JFLAP expandem cada classe; a marca \lit{<read />} representa movimento vazio. Todos os autômatos começam em $q_0$ e têm $q_1$ como único estado final.
"""

FORMALS = [r"\lit{/rolar}\,\SP\,R",
            r"\lit{/atacar}\,\SP\,I\,\SP\,\lit{bonus=}\,B\,\SP\,\lit{ca=}\,N\,\SP\,\lit{dano=}\,R",
            r"\lit{/magia}\,\SP\,I\,\SP\,\lit{alvo=}\,I\,\SP\,\lit{cd=}\,N\,\SP\,\lit{bonus=}\,B\,\SP\,\lit{dano=}\,R",
            r"\lit{/curar}\,\SP\,I\,\SP\,R",
            r"\lit{/teste}\,\SP\,A\,\SP\,\lit{bonus=}\,B\,\SP\,\lit{cd=}\,N"]


def case_tex(text):
    if not text: return r"$\eps$ (entrada vazia)"
    # Escapes visíveis identificam caracteres que não poderiam aparecer na tabela.
    return r'\cadeia{"' + text.replace("\n", r"\n").replace("\t", r"\t") + '"}'


def alphabet_tex(rule):
    values = sorted(rule.expr.alphabet())
    if set("abcdefghijklmnopqrstuvwxyz").issubset(values):
        values = [x for x in values if x not in "abcdefghijklmnopqrstuvwxyz0123456789"]
        prefix = r"L\cup D\cup"
    else:
        prefix = ""
        if set("0123456789").issubset(values):
            values = [x for x in values if x not in "0123456789"]
            prefix = r"D\cup"
    symbols = [r"\SP" if c == " " else r"\lit{" + esc(c) + "}" for c in values]
    return prefix + r"\{" + ",".join(symbols) + r"\}"


def symbol_tex(symbols):
    values = set(symbols)
    if values == {""}: return r"$\eps$"
    if values == set("abcdefghijklmnopqrstuvwxyz"): return "$L$"
    if values == set("abcdefghijklmnopqrstuvwxyz0123456789_"): return r"$L\cup D\cup\{\lit{\_}\}$"
    if values == set("0123456789"): return "$D$"
    if values == set("123456789"): return "$U$"
    return ", ".join(r"$\SP$" if c == " " else r"$\eps$" if not c else r"\lit{" + esc(c) + "}" for c in sorted(values))


def main():
    cases = json.loads((ROOT / "examples/cases.json").read_text(encoding="utf-8"))
    data = []
    macros = []
    for rule in RULES:
        nfa = compile_nfa(rule.expr)
        assert rule.pattern == rule.expr.pattern(), "Regenerar padrões antes do relatório"
        graph = json.loads((ROOT / "tmp/graphs" / (rule.key + ".json")).read_text(encoding="utf-8"))
        draw = []
        for edge in graph["edges"]:
            for key in ("_draw_", "_hdraw_", "_ldraw_"): draw += diagram_ops(edge.get(key, []))
        for obj in graph["objects"]:
            for key in ("_draw_", "_ldraw_"): draw += diagram_ops(obj.get(key, []))
        macros.append(r"\newcommand{\NFA" + rule.key + "}{%\n" + "\n".join(draw) + "\n}\n")
        data.append((rule, nfa, graph))
    parts = [PREAMBLE, "\n".join(macros), BODY, r"\clearpage\section{Fichas das expressões regulares}" + "\n"]
    for i, (rule, nfa, graph) in enumerate(data):
        parts.append(r"\subsection{ER-" + f"{i+1:02}" + ": " + esc(rule.title) + "}\n")
        parts.append(r"\textbf{Finalidade:} " + esc(rule.purpose) + "\n\n")
        parts.append(r"\textbf{Linguagem:} comandos completos no formato \cadeia{" + rule.syntax + "}, com os domínios definidos na seção 4, na ordem indicada e com espaços exatos.\n\n")
        parts.append(r"\textbf{Alfabeto:} $\Sigma=" + alphabet_tex(rule) + "$.\n\n")
        parts.append(r"\textbf{Expressão formal:}\par\smallskip\noindent\sbox0{$" + FORMALS[i] + r"$}\ifdim\wd0>\linewidth\resizebox{\linewidth}{!}{\usebox0}\else\usebox0\fi\par\smallskip" + "\n")
        parts.append(r"\textbf{Sintaxe exata em \lit{rpg/patterns.py}:}" + "\n\\begin{lstlisting}\nr\"" + rule.pattern + '"\n\\end{lstlisting}\n')
        parts.append(r"\textbf{Operadores:} concatenação de campos, união nas alternativas e opcionais, classes finitas e capturas nomeadas. " + ("Há fecho de Kleene na continuação dos identificadores. " if rule.key in ("atacar", "magia", "curar") else "Não há fecho de Kleene nesta ER completa. ") + r"Alternativas vazias implementam $\eps$. Quebras visuais no padrão não são caracteres adicionais.\par" + "\n")
        parts.append(r"\textbf{AFN$\varepsilon$:} inicial $q_0$, final $q_1$, " + str(nfa.states) + " estados e " + str(len(nfa.edges)) + r" transições elementares. O diagrama completo, dividido em faixas com sobreposição, está no apêndice~\ref{ap:diagramas}. As transições estão no apêndice~\ref{ap:transicoes}.\par" + "\n")
        parts.append(r"\begin{longtable}{p{0.11\linewidth}p{0.67\linewidth}p{0.13\linewidth}}\toprule Caso & Cadeia & Resultado\\\midrule\endhead" + "\n")
        for category, label, prefix in (("accepted", "Aceita", "A"), ("rejected", "Rejeitada", "R")):
            for index, text in enumerate(cases[rule.key][category], 1):
                parts.append(f"{prefix}{index} & " + case_tex(text) + " & " + label + r"\\" + "\n")
        parts.append(r"\bottomrule\end{longtable}" + "\n")
        parts.append(r"\textbf{Casos-limite e análise:} A1 usa os mínimos da linguagem. As demais aceitas incluem limites superiores, sinais e zeros iniciais permitidos nos bônus ou modificadores. R1 verifica a palavra vazia. Todas as cadeias tiveram os resultados esperados nas regex, no simulador e nos arquivos JFLAP. Nas tabelas, \cadeia{\n} representa uma quebra de linha e espaços finais entre a última letra e o delimitador devem ser preservados ao reproduzir a entrada.\par" + "\n\\clearpage\n")
    parts.append(r"""
\section{Testes e análise dos resultados}
A execução registrada em \lit{docs/resultados-testes.txt} concluiu 14 métodos de teste com \lit{OK}. Os testes verificam 60 cadeias obrigatórias, seis aceitas e seis rejeitadas por ER, tanto nas regex quanto nos AFN$\varepsilon$. Os mesmos casos são executados sobre as transições lidas dos arquivos \lit{.jff}, cuja estrutura é comparada à do autômato original.

Há também 1.500 mutações com semente 42, geradas por inserção, exclusão ou substituição de caracteres. Nenhuma divergência entre regex e simulador foi encontrada nessa amostra. Amostragem não é prova exaustiva de equivalência. A fundamentação formal decorre da tradução estrutural dos operadores.

Os testes determinísticos verificam acerto exatamente no limiar, falha sem rolagem de dano, resistência com metade do dano, cura e dano com piso zero, totais negativos, todas as faces permitidas e a quantidade máxima. Os testes HTTP usam um servidor temporário em porta livre e verificam arquivos estáticos, validação sem rolagem, execução, JSON malformado, tipos incorretos, corpo grande e rotas desconhecidas.

Os arquivos JFLAP foram verificados por leitura e simulação do XML. A interface gráfica do JFLAP 7 não foi executada nesta validação; a equipe deve conferir a abertura dos arquivos e a função Multiple Run na máquina da apresentação. A implementação inicial foi verificada com Python 3.12.14; versões 3.10 e 3.11 não foram executadas nesta sessão.

\section{Instalação, execução e demonstração}
Não é necessário instalar pacotes Python para a aplicação e os testes. Na pasta do projeto:
\begin{lstlisting}
python -m rpg.server
python -m rpg.cli
python -m unittest discover -v
\end{lstlisting}
O primeiro comando inicia o servidor; os demais são alternativas independentes para CLI e testes. Abra \url{http://127.0.0.1:8000}. Para outra porta, use \lit{python -m rpg.server --port 8080}. O servidor atende à máquina local por padrão e é encerrado com Ctrl+C.

Uma demonstração pode executar \cadeia{/rolar 2d6+3}, exibir os dados e o modificador, e depois rejeitar \cadeia{/rolar 21d6}. Um ataque demonstra comparação com CA e dano condicionado ao acerto. A execução no CLI utiliza o mesmo parser. Os valores aleatórios variam entre execuções; os testes injetam resultados controlados.

\section{Limitações e possíveis melhorias}
O projeto implementa um sistema didático independente, sem reproduzir integralmente regras oficiais de RPG. Não há críticos, vantagem, cadastro de personagens, consumo de recursos, catálogo de magias, persistência de PV ou autenticação. O servidor é destinado à demonstração local. Melhorias possíveis incluem fichas persistentes, histórico salvo e novas ações, acompanhadas de novas ER, autômatos e testes equivalentes.

\section{Contribuições e uso de inteligência artificial}
As contribuições abaixo reproduzem o registro fornecido pela equipe em \lit{docs/contribuicoes.md}.
\begin{longtable}{p{0.25\linewidth}p{0.42\linewidth}p{0.23\linewidth}}
\toprule Integrante & Contribuição registrada & Parte da apresentação\\\midrule\endhead
Rafael Batista Ferreria & Idealização da ideia do projeto, criação dos slides e criação das expressões regulares 1 a 3. & Introdução até a expressão regular 3.\\
Paulo Ricardo da Rocha & Criação das expressões regulares 4 e 5, testes e interface web. & Expressão regular 4 até a conclusão.\\
\bottomrule\end{longtable}
O registro da equipe informa apoio do OpenAI Codex na criação dos autômatos e na documentação. Durante a elaboração inicial nesta sessão, a ferramenta também apoiou a estruturação da implementação, dos testes e dos materiais. A equipe é responsável por revisar, compreender, explicar e conseguir modificar o conteúdo produzido.

\section{Conclusão}
A aplicação integra reconhecimento de cinco linguagens regulares a ações concretas de RPG. A representação estrutural relaciona as expressões implementadas à notação formal e aos AFN$\varepsilon$. As interfaces web e CLI reutilizam o motor, e os testes verificam tanto o reconhecimento quanto as regras de execução. As limitações operacionais e de regras do jogo são explícitas e separadas da definição das linguagens.

\begin{thebibliography}{9}
\bibitem{lauda} MATERIAL DO PROFESSOR. \textit{Lauda do trabalho de Linguagens Formais e Autômatos}. Documento fornecido pela equipe, 2026.
\bibitem{guia} MATERIAL DO PROFESSOR. \textit{Guia de Sintaxe para Apresentação das Expressões Regulares}. Arquivo GUIA\_SINTAXE\_EXPRESSOES\_REGULARES\_TRABALHO\_LFA - FINAL.pdf, 2026.
\bibitem{python} PYTHON SOFTWARE FOUNDATION. \textit{Python 3: documentação da biblioteca padrão}. Módulos re, dataclasses, unittest, random e http.server. Disponível em: \url{https://docs.python.org/3/library/}.
\bibitem{graphviz} GRAPHVIZ. \textit{Graphviz: Graph Visualization Software}. Disponível em: \url{https://graphviz.org/}. Layouts deste relatório gerados com Graphviz via \lit{@viz-js/viz}.
\bibitem{jflap} JFLAP. \textit{JFLAP: Software for Experimenting with Formal Languages and Automata}. Disponível em: \url{https://www.jflap.org/}.
\end{thebibliography}

\appendix
\clearpage
\begin{landscape}
\section{Diagramas completos dos AFN\texorpdfstring{$\varepsilon$}{epsilon}}\label{ap:diagramas}
Cada diagrama foi dividido em faixas horizontais de coordenadas, com sobreposição. Os trechos repetidos nas faixas adjacentes pertencem ao mesmo autômato. Uma transição cortada pela borda continua na próxima faixa; ela não termina na borda. Essa divisão mantém os rótulos legíveis sem reduzir um autômato extenso à largura de uma página.

Todas as faixas de cada ER, consideradas em conjunto, cobrem o diagrama completo. $q_0$ é inicial e $q_1$ é final. SP é espaço U+0020; $\eps$ é movimento vazio. Classes entre colchetes são uniões de transições de um caractere. A tabela do próximo apêndice especifica todas as transições sem cortes.
\clearpage
""")
    for i, (rule, nfa, graph) in enumerate(data):
        _, _, width, height = map(float, graph["bb"].split(","))
        window, step = 900, 800
        total = max(1, math.ceil(max(0, width-window)/step)+1)
        for part in range(total):
            start = min(part*step, max(0, width-window))
            parts.append(r"\subsection*{ER-" + f"{i+1:02}" + ": " + esc(rule.title) + f" --- faixa {part+1} de {total}" + "}\n")
            parts.append(r"\noindent\textbf{Coordenadas horizontais:} " + f"{start:.0f} a {start+window:.0f}" + r". A numeração dos estados é preservada.\par\smallskip" + "\n")
            parts.append(r"\begin{center}\resizebox{0.98\linewidth}{!}{\begin{tikzpicture}[x=1bp,y=1bp,line width=0.6bp]" + "\n")
            parts.append(r"\path[use as bounding box] (0,0) rectangle " + coord((window, height+5)) + ";\n")
            parts.append(r"\clip (0,0) rectangle " + coord((window, height+5)) + ";\n")
            parts.append(r"\begin{scope}[xshift=" + f"{-start:.2f}" + "bp]\n" + r"\NFA" + rule.key + "\n" + r"\end{scope}\end{tikzpicture}}\end{center}" + "\n\\clearpage\n")
    parts.append(r"\end{landscape}\section{Transições completas dos autômatos}\label{ap:transicoes}" + "\n")
    parts.append(r"As linhas agrupam apenas transições paralelas com a mesma origem e destino. Cada símbolo de uma célula representa uma transição independente. Os conjuntos $L$, $D$ e $U$ são definidos na seção 5. Um símbolo $\eps$ é movimento vazio. Não há outras transições além das listadas.\par" + "\n")
    for i, (rule, nfa, graph) in enumerate(data):
        parts.append(r"\subsection{ER-" + f"{i+1:02}" + ": " + esc(rule.title) + "}\n")
        parts.append(r"$Q=\{q_0,q_1,\ldots,q_{" + str(nfa.states-1) + r"}\}$, estado inicial $q_0$, conjunto de finais $\{q_1\}$.\par" + "\n")
        parts.append(r"\begin{longtable}{p{0.2\linewidth}p{0.48\linewidth}p{0.2\linewidth}}\toprule Origem & Símbolo(s) & Destino\\\midrule\endhead" + "\n")
        groups = defaultdict(list)
        for a, b, symbol in nfa.edges: groups[a, b].append(symbol)
        for (a, b), symbols in groups.items():
            parts.append(f"$q_{{{a}}}$ & " + symbol_tex(symbols) + f" & $q_{{{b}}}$" + r"\\" + "\n")
        parts.append(r"\bottomrule\end{longtable}" + "\n")
    parts.append(r"\end{document}" + "\n")
    out = ROOT / "docs/relatorio-tecnico.tex"
    out.write_text("".join(parts), encoding="utf-8")
    zip_path = ROOT / "docs/relatorio-overleaf.zip"
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        archive.write(out, "main.tex")
    print(f"LaTeX independente: {out.name} ({out.stat().st_size} bytes)")
    print(f"ZIP Overleaf: {zip_path.name}; arquivo principal main.tex; compilador pdfLaTeX")
    from optimize_latex import main as optimize_document
    optimize_document()


if __name__ == "__main__": main()
