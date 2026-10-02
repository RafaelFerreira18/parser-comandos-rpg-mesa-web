"""Gera relatório e apresentação PDF com dados reais das fichas e dos testes.

Ferramenta de documentação: requer reportlab e pypdf. A aplicação é stdlib.
Antes: export_materials.py, render_graphs.mjs e testes com saída registrada.
"""
from pathlib import Path
import json
import textwrap
from html import escape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parent.parent
TMP = ROOT / "tmp/pdfs"
TMP.mkdir(parents=True, exist_ok=True)
FONT = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Body", str(FONT / "seguisym.ttf")))
pdfmetrics.registerFont(TTFont("Bold", str(FONT / "segoeuib.ttf")))
pdfmetrics.registerFont(TTFont("Code", str(FONT / "consola.ttf")))
DATA = json.loads((ROOT / "docs/manifest.json").read_text(encoding="utf-8"))
FORMAL = ["'/rolar' SP R", "'/atacar' SP I SP 'bonus=' B SP 'ca=' N SP 'dano=' R",
          "'/magia' SP I SP 'alvo=' I SP 'cd=' N SP 'bonus=' B SP 'dano=' R",
          "'/curar' SP I SP R", "'/teste' SP A SP 'bonus=' B SP 'cd=' N"]
MACROS = ["D = (0 ∪ 1 ∪ 2 ∪ 3 ∪ 4 ∪ 5 ∪ 6 ∪ 7 ∪ 8 ∪ 9)",
          "U = (1 ∪ 2 ∪ 3 ∪ 4 ∪ 5 ∪ 6 ∪ 7 ∪ 8 ∪ 9)",
          "L = (a ∪ b ∪ c ∪ ... ∪ z), somente as 26 letras ASCII",
          "I = L (L ∪ D ∪ '_')*; N = U (ε ∪ D)",
          "B = (ε ∪ '+' ∪ '-') D (ε ∪ D)",
          "Q = (U ∪ '1' D ∪ '20')",
          "F = ('4' ∪ '6' ∪ '8' ∪ '10' ∪ '12' ∪ '20' ∪ '100')",
          "R = Q 'd' F (ε ∪ ('+' ∪ '-') D (ε ∪ D))",
          "A = ('forca' ∪ 'destreza' ∪ 'constituicao' ∪ 'inteligencia' ∪ 'sabedoria' ∪ 'carisma')",
          "SP = espaço U+0020. Aspas delimitam literais, não pertencem à entrada."]


def draw_ops(c, ops):
    size = 10
    for op in ops:
        kind = op["op"]
        if kind == "F": size = op["size"]
        elif kind in ("c", "C"):
            color = op["color"]
            if color.startswith("#"):
                value = HexColor(color[:7])
                (c.setStrokeColor if kind == "c" else c.setFillColor)(value)
        elif kind in ("e", "E"):
            x, y, rx, ry = op["rect"]
            c.ellipse(x-rx, y-ry, x+rx, y+ry, stroke=1, fill=int(kind == "E"))
        elif kind in ("b", "B"):
            points = op["points"]
            p = c.beginPath(); p.moveTo(*points[0])
            for i in range(1, len(points), 3):
                p.curveTo(*points[i], *points[i+1], *points[i+2])
            c.drawPath(p, stroke=1, fill=int(kind == "B"))
        elif kind in ("p", "P", "L"):
            points = op["points"]
            p = c.beginPath(); p.moveTo(*points[0])
            for point in points[1:]: p.lineTo(*point)
            if kind != "L": p.close()
            c.drawPath(p, stroke=1, fill=int(kind == "P"))
        elif kind == "T":
            x, y = op["pt"]
            # SP mantém visível o símbolo de espaço em fontes do PDF.
            text = op["text"].replace("␠", "SP")
            c.setFont("Body", size)
            if op["align"] == "c": c.drawCentredString(x, y, text)
            elif op["align"] == "r": c.drawRightString(x, y, text)
            else: c.drawString(x, y, text)


def graph_appendix():
    path = TMP / "automatos.pdf"
    c = canvas.Canvas(str(path))
    for rule in DATA:
        graph = json.loads((ROOT / "tmp/graphs" / (rule["acao"] + ".json")).read_text(encoding="utf-8"))
        _, _, w, h = map(float, graph["bb"].split(","))
        c.setPageSize((w+80, h+120))
        c.setFont("Bold", 18)
        c.drawString(30, h+86, rule["id"] + " - " + rule["nome"] + " - AFNε completo")
        c.setFont("Body", 11)
        c.drawString(30, h+65, "Página de grande formato para zoom. Inicial q0, final q1. Classes = transições paralelas. SP = espaço. ε = movimento vazio.")
        c.saveState(); c.translate(40, 30)
        draw_ops(c, graph.get("_draw_", []))
        for edge in graph["edges"]:
            for key in ("_draw_", "_hdraw_", "_tdraw_", "_ldraw_"): draw_ops(c, edge.get(key, []))
        for obj in graph["objects"]:
            for key in ("_draw_", "_ldraw_"): draw_ops(c, obj.get(key, []))
        c.restoreState(); c.showPage()
    c.save()
    return path


def merge(base, appendix, output):
    writer = PdfWriter()
    writer.append(str(base)); writer.append(str(appendix))
    writer.add_metadata({"/Title": output.stem, "/Author": "Equipe - identificação a preencher"})
    with output.open("wb") as stream: writer.write(stream)


def report(appendix):
    styles = getSampleStyleSheet()
    for name in styles.byName:
        styles[name].fontName = "Body"
    styles["Normal"].fontSize = 10; styles["Normal"].leading = 15
    styles["Title"].fontName = "Bold"; styles["Title"].fontSize = 25; styles["Title"].leading = 32
    styles["Heading1"].fontName = "Bold"; styles["Heading1"].fontSize = 17
    styles.add(ParagraphStyle("Mono", fontName="Code", fontSize=8, leading=12))
    story = []
    def p(text, style="Normal"):
        story.append(Paragraph(escape(text), styles[style])); story.append(Spacer(1, 9))
    def code(text): story.append(Preformatted("\n".join(textwrap.wrap(text, 93, replace_whitespace=False, drop_whitespace=False)), styles["Mono"]))
    p("Parser de Comandos de RPG de Mesa (Web)", "Title")
    p("Relatório técnico - Linguagens Formais e Autômatos")
    p("Integrantes: preencher os nomes completos em docs/contribuicoes.md. Repositório configurado: https://github.com/RafaelFerreira18/parser-comandos-rpg-mesa-web. A implementação está local e a publicação ainda precisa ser concluída.")
    p("1. Problema e solução", "Heading1")
    p("Comandos de RPG digitados em texto exigem reconhecer a ação, validar os parâmetros e calcular resultados. O projeto oferece interface web com atualização sem recarregar a página e menu CLI. Cinco expressões regulares relevantes reconhecem rolagem, ataque, magia, cura e teste de atributo.")
    p("Entrada: texto do comando. Processamento: re.fullmatch, captura nomeada, conversão de valores e regras de rolagem. Saída: mensagem clara, parâmetros, valores individuais, total, sucesso/falha, dano ou cura. A interface distingue erros de sintaxe de falhas da ação no jogo.")
    p("2. Implementação e arquitetura", "Heading1")
    p("Python 3.10+ (recomendado 3.11+) com re, dataclasses, random, http.server, json, argparse e unittest. JavaScript usa fetch para consultar o backend. A aplicação não depende de frameworks nem APIs externas. Graphviz e JFLAP são ferramentas de documentação dos autômatos.")
    p("Módulos: language.py define as ER; engine.py valida e executa; automata.py constrói e simula AFNε; server.py expõe HTTP; cli.py apresenta o menu. web/ contém HTML, CSS e JavaScript. tools/ gera as fichas, diagramas e PDFs. Testes usam a mesma API pública que as interfaces.")
    p("3. Contrato de entrada e regras de jogo", "Heading1")
    p("Espaços U+0020 e minúsculas são obrigatórios. A validação não aplica strip, flags de Unicode abreviadas ou conversão de caixa. Quantidade 1-20; faces 4, 6, 8, 10, 12, 20, 100; modificador opcional -99 a +99; CA/CD 1-99 sem zero inicial; bônus com sinal opcional e um ou dois dígitos. Nomes seguem [a-z][a-z0-9_]*. Bônus e modificadores permitem zeros iniciais com até dois dígitos.")
    p("Ataque: d20 + bônus ≥ CA causa o dano rolado; falha causa zero. Teste: d20 + bônus ≥ CD produz sucesso. Magia: o alvo faz resistência d20 + bônus contra CD; se resistir, recebe metade do dano, arredondada para baixo. Sucesso da magia significa falha da resistência. Cura e dano têm piso zero, mas o total de uma rolagem simples pode ser negativo. Não há críticos ou fichas persistentes.")
    p("Limites operacionais: comandos até 512 caracteres, corpo HTTP até 4096 bytes e leitura com timeout. A regex e o AFNε admitem nomes de comprimento arbitrário. O serviço aplica seus limites separadamente, sem redefinir as cinco linguagens regulares.")
    p("4. Notação formal e equivalência", "Heading1")
    p("As macros abaixo são abreviações de expressões regulares formais. Literais de várias letras significam concatenação de cada símbolo. O alfabeto de cada ficha lista somente os símbolos efetivamente usados. A ficha Markdown inclui a expansão completa, sem macros.")
    for macro in MACROS: p(macro)
    p("União ∪ gera alternância (?:...|...). Justaposição gera concatenação. Fecho * gera zero ou mais repetições. Opcionalidade corresponde a união com ε. Classes finitas expandem união de símbolos. Grupos (?P<nome>...) só capturam parâmetros. re.fullmatch exige a cadeia inteira, sem incluir âncoras no alfabeto. Não se usam retroreferências, lookaround, condicionais ou recursão.")
    p("Construção do AFNε: um literal usa uma transição por símbolo; uma classe usa transições paralelas; concatenação compartilha fronteiras; união acrescenta ramificações ε; fecho acrescenta passagem vazia e retorno ε. Por indução sobre a árvore de operadores, cada transformação preserva a linguagem. A simulação fecha movimentos ε antes e depois de cada símbolo.")
    for index, rule in enumerate(DATA):
        story.append(PageBreak())
        p(rule["id"] + " - " + rule["nome"], "Heading1")
        p("Finalidade: " + rule["finalidade"])
        p("Linguagem: comandos completos conforme o exemplo " + rule["exemplo"] + ", com domínios e ordem dos campos definidos na seção 3.")
        p("Σ = {" + ", ".join("SP" if s == " " else s for s in rule["alfabeto"]) + "}")
        p("ER formal (macros da seção 4): " + FORMAL[index])
        p("Padrão exato gerado e utilizado por Rule.pattern:")
        code(rule["regex"])
        p("A quebra de linha visual do padrão não insere caracteres na expressão.")
        p(f'AFNε: início q0, final q1, {rule["estados"]} estados, {rule["transicoes"]} transições elementares. Diagrama integral no apêndice e em automata/{rule["acao"]}.svg. XML JFLAP e tabela de transições acompanham o repositório.')
        p("Operadores: união nas alternativas e opcionais; concatenação dos campos; fecho no nome quando há identificador. A captura nomeada extrai valores sem alterar aceitação.")
        p("Seis cadeias aceitas:")
        for text in rule["casos"]["accepted"]: code(text)
        p("Seis cadeias rejeitadas:")
        for text in rule["casos"]["rejected"]: code("ε (entrada vazia)" if text == "" else repr(text))
        p("Casos-limite: mínimos na primeira aceita, máximos entre as demais, vazio e valores fora do domínio nas rejeitadas. Todas produziram o resultado esperado nas regex, no simulador AFNε e nos XML exportados.")
    story.append(PageBreak())
    p("5. Testes e análise dos resultados", "Heading1")
    test_output = (ROOT / "docs/resultados-testes.txt").read_text(encoding="utf-8")
    if "Ran 14 tests" not in test_output or "\nOK" not in test_output: raise RuntimeError("Teste registrado sem sucesso")
    p("A execução registrada em docs/resultados-testes.txt concluiu 14 métodos de teste com OK. A suíte verifica 60 cadeias obrigatórias, cada uma nas regex e no AFNε, e repete os casos nos .jff exportados. Mais 1.500 mutações com semente 42 confrontam a regex e a simulação independente. Nenhuma divergência foi encontrada nessa amostra.")
    p("Os testes determinísticos verificam igualdade no limiar, ataque falho sem rolar dano, resistência à magia com metade do dano, piso zero, totais negativos, todos os dados e quantidade máxima. Testes HTTP reais verificam arquivos estáticos, validação sem rolagem, execução, JSON malformado, tipo incorreto, corpo grande e rota inexistente. Testes por amostragem não provam equivalência exaustiva.")
    p("A leitura e simulação dos arquivos JFLAP confirmaram estados, início, final, transições e cadeias. A interface gráfica JFLAP 7 não foi executada neste ambiente; a equipe deve conferir abertura e Multiple Run na máquina de apresentação.")
    p("6. Execução e demonstração", "Heading1")
    for text in ("python -m rpg.server", "python -m rpg.cli", "python -m unittest discover -v"): code(text)
    p("Acesse http://127.0.0.1:8000. Digite /rolar 2d6+3 e execute. Depois mostre a rejeição de /rolar 21d6. A digitação consulta /api/validar após 300 ms; /api/executar lança os dados ao enviar. O menu CLI possui executar, exemplos e sair. Ctrl+C encerra a aplicação. A apresentação usa o roteiro de 10-12 minutos do repositório.")
    p("7. Limitações e melhorias", "Heading1")
    p("Este sistema não reproduz um regulamento oficial. Não há críticos, vantagem, cadastro de personagens, persistência de PV, catálogo de magias ou autenticação. A aleatoriedade de produção usa SystemRandom; testes injetam resultados controlados. O servidor local é destinado à demonstração. Melhorias possíveis: fichas, histórico persistente e regras adicionais, com novas ER e autômatos equivalentes.")
    p("8. Contribuições, IA e entrega", "Heading1")
    p("Identificação e tarefas reais de 1 a 4 integrantes devem ser preenchidas em docs/contribuicoes.md antes do envio. OpenAI Codex apoiou implementação inicial, documentação, autômatos, testes e apresentação. A equipe deve compreender e revisar o conteúdo, assumir autoria e conseguir alterá-lo. O endereço do repositório provém da configuração Git existente; a implementação desta entrega permanece local até a publicação.")
    p("A entrega exige link definitivo GitHub, relatório, apresentação e nomes no Classroom. Os documentos divergem quanto ao prazo: lauda traz 02/10/2026 no cabeçalho e 30/09/2026 em uma etapa; guia traz 30/09/2026. Confirmar o prazo com o professor.")
    p("9. Referências", "Heading1")
    for text in ("Lauda do trabalho de Linguagens Formais e Autômatos fornecida pela equipe.", "GUIA_SINTAXE_EXPRESSOES_REGULARES_TRABALHO_LFA - FINAL.pdf, material do professor.", "Python: https://docs.python.org/3/library/re.html; unittest.html; http.server.html; random.html.", "Graphviz: https://graphviz.org/. SVGs gerados pelo Graphviz via @viz-js/viz.", "JFLAP: https://www.jflap.org/. Formato XML de autômatos finitos."):
        p(text)
    p("Apêndice: cinco AFNε completos", "Heading1")
    p("As páginas seguintes usam tamanho ampliado para manter estados e rótulos legíveis com zoom. SVGs são a opção indicada para projeção por trechos. As tabelas completas estão em docs/expressoes-regulares.md.")
    def footer(c, doc):
        c.setFont("Body", 8); c.setFillColor(HexColor("#626979"))
        c.drawString(42, 24, "Parser de Comandos de RPG de Mesa - Relatório técnico")
        c.drawRightString(550, 24, str(doc.page))
    base = TMP / "report.pdf"
    SimpleDocTemplate(str(base), rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42).build(story, onFirstPage=footer, onLaterPages=footer)
    merge(base, appendix, ROOT / "docs/relatorio-tecnico.pdf")


def deck(appendix):
    base = TMP / "slides.pdf"
    c = canvas.Canvas(str(base), pagesize=(1280, 720))
    slide_num = 0
    def page(title, subtitle=""):
        nonlocal slide_num
        slide_num += 1
        c.setFillColor(HexColor("#111722")); c.rect(0, 0, 1280, 720, fill=1, stroke=0)
        c.setFillColor(HexColor("#e1bb79")); c.setFont("Bold", 17); c.drawString(64, 671, "PARSER DE COMANDOS DE RPG DE MESA")
        c.setFillColor(HexColor("#f2f0e8")); c.setFont("Bold", 34); c.drawString(64, 602, title)
        if subtitle: c.setFont("Body", 17); c.drawString(64, 566, subtitle)
        c.setFillColor(HexColor("#aab1bf")); c.setFont("Body", 13); c.drawString(64, 28, "Linguagens Formais e Autômatos"); c.drawRightString(1216, 28, str(slide_num))
    def lines(items, y=520, size=23, step=45, font="Body"):
        c.setFillColor(HexColor("#f2f0e8")); c.setFont(font, size)
        for text in items:
            for line in textwrap.wrap(text, width=int(1120/(size*.52)), replace_whitespace=False, drop_whitespace=False) or [""]:
                if y < 64: raise RuntimeError(f"Overflow slide {slide_num}")
                c.drawString(64, y, line); y -= step
        return y
    page("Parser de Comandos", "RPG de Mesa (Web)")
    lines(["Um comando de texto reconhecido por uma linguagem regular.", "Python 3.10+ e JavaScript. Web com resultado dinâmico e menu CLI.", "Integrantes: preencher nomes e contribuições reais antes da entrega."], y=440, size=26, step=58)
    c.showPage()
    page("Problema e solução")
    lines(["Jogadores digitam comandos de dados, ataque, magia, cura e atributos.", "Cinco regex validam a entrada inteira e capturam os parâmetros.", "O motor lança os dados e retorna total, sucesso/falha, dano ou cura.", "A interface mostra a resposta sem recarregar a página."])
    c.showPage()
    page("Entrada, processamento e saída")
    lines(["Entrada: /atacar goblin bonus=5 ca=14 dano=1d8+2", "Validação: re.fullmatch sobre o comando completo.", "Extração: alvo=goblin, bonus=5, ca=14, dados=1d8+2.", "Execução: d20 + 5 ≥ 14 acerta. Dano é o total de 1d8+2.", "Ao digitar: validação após 300 ms, sem rolagem. Ao executar: rolagem.", "Backend, CLI e interface web compartilham o mesmo motor."], size=21, step=43)
    c.showPage()
    page("Convenções da notação formal", "As cinco fichas usam estas macros. A expansão integral acompanha o relatório em Markdown.")
    lines(MACROS, y=520, size=18, step=34)
    c.showPage()
    page("Equivalência dos operadores")
    lines(["União ∪ corresponde a alternância. Justaposição é concatenação.", "r* aceita zero ou mais repetições. Opcionalidade equivale a (ε ∪ r).", "Classes finitas representam união de símbolos do alfabeto.", "Grupos nomeados capturam valores sem mudar a linguagem.", "fullmatch exige a cadeia inteira. Espaço ASCII e caixa são estritos.", "Sem retroreferências, recursão, condicionais ou lookaround."], size=22, step=48)
    c.showPage()
    for index, rule in enumerate(DATA):
        page(rule["id"] + " - " + rule["nome"], rule["finalidade"])
        y = lines(["Linguagem: formato " + rule["exemplo"], "ER formal: " + FORMAL[index]], y=510, size=20, step=36)
        y -= 10
        y = lines(["Sintaxe Python exata (quebras de linha apenas visuais):"], y=y, size=18, step=32)
        y = lines([rule["regex"]], y=y, size=17, step=25, font="Code")
        y -= 16
        lines([f'AFNε: q0 inicial, q1 final; {rule["estados"]} estados e {rule["transicoes"]} transições.', "Diagrama completo no apêndice, SVG e arquivo .jff."], y=y, size=18, step=30)
        c.showPage()
        page(rule["id"] + " - alfabeto e testes", "Seis cadeias aceitas e seis rejeitadas. Resultados confirmados nos testes automatizados.")
        y = lines(["Σ = {" + ", ".join("SP" if s == " " else s for s in rule["alfabeto"]) + "}"], y=515, size=17, step=24)
        y -= 16
        for category, label in (("accepted", "ACEITA"), ("rejected", "REJEITA")):
            for text in rule["casos"][category]:
                text = "ε (entrada vazia)" if not text else repr(text)
                y = lines([label + "  " + text], y=y, size=17, step=25, font="Code")
            y -= 10
        lines(["Caso-limite: mínimos, máximos e rejeição da entrada vazia."], y=y, size=17, step=25)
        c.showPage()
    page("AFNε e equivalência estrutural")
    lines(["Literais: uma transição por símbolo. Classes: transições paralelas.", "Concatenação: fronteiras compartilhadas entre fragmentos.", "União: caminhos alternativos com ramificações ε.", "Fecho: caminho vazio e retorno ε para repetir o fragmento.", "A mesma árvore gera regex, formal e autômatos.", "Demonstração: ampliar automata/rolar.svg e abrir rolar.jff no JFLAP."], size=22, step=47)
    c.showPage()
    page("Demonstração ao vivo")
    lines(["Aceita: /rolar 2d6+3", "Rejeita: /rolar 21d6 (quantidade acima de 20)", "Aceita: /teste forca bonus=-2 cd=15", "Rejeita: /curar Ana 1d4 (maiúscula no nome)", "Mostrar parâmetros, dados individuais e mensagem de resultado.", "No CLI: python -m rpg.cli"], size=23, step=49)
    c.showPage()
    page("Testes e limites")
    lines(["14 métodos de teste concluídos com OK.", "60 cadeias obrigatórias, verificadas por regex, AFNε e XML JFLAP.", "1.500 mutações com semente fixa: nenhuma divergência na amostra.", "Testes determinísticos verificam dano, cura e limiares de sucesso.", "Testes HTTP verificam execução, validação e entradas malformadas.", "Amostragem não substitui a construção formal da equivalência.", "Limites: 512 caracteres no serviço, sem críticos ou PV persistentes."], size=21, step=42)
    c.showPage()
    page("Autoria, contribuições e entrega")
    lines(["Cada integrante deve registrar seu nome e as contribuições reais.", "Codex auxiliou implementação inicial, testes, autômatos e materiais.", "A equipe deve revisar, explicar e conseguir modificar o conteúdo.", "Entregar GitHub, relatório PDF, apresentação PDF e nomes no Classroom.", "Confirmar com o professor a divergência de prazo nos documentos.", "Referências: lauda, guia de sintaxe, Python, Graphviz e JFLAP."], size=22, step=48)
    c.showPage(); c.save()
    merge(base, appendix, ROOT / "docs/apresentacao.pdf")


if __name__ == "__main__":
    appendix = graph_appendix()
    report(appendix)
    deck(appendix)
    for name in ("relatorio-tecnico.pdf", "apresentacao.pdf"):
        print(name, len(PdfReader(ROOT / "docs" / name).pages), "páginas")
