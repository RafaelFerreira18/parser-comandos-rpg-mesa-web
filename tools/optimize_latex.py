"""Otimiza o .tex existente sem regenerar seu texto ou perder edições.

Converte os caminhos Graphviz/TikZ em caminhos PDF vetoriais (pdfLaTeX)
e desenha apenas primitivas que intersectam cada faixa do diagrama.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs/relatorio-tecnico.tex"
MACRO = re.compile(r"\\newcommand\{\\NFA([a-z]+)\}\{%\n(.*?)\n\}\n", re.S)
POINT = re.compile(r"\((-?[\d.]+),(-?[\d.]+)\)")
PANEL = re.compile(
    r"\\begin\{tikzpicture\}\[x=1bp,y=1bp,line width=0\.6bp\]\s*"
    r"\\path\[use as bounding box\] \(0,0\) rectangle \(([\d.]+),([\d.]+)\);\s*"
    r"\\clip \(0,0\) rectangle \([\d.]+,[\d.]+\);\s*"
    r"\\begin\{scope\}\[xshift=(-?[\d.]+)bp\]\s*"
    r"\\NFA([a-z]+)\s*\\end\{scope\}\\end\{tikzpicture\}")
NODE = re.compile(
    r"\\node\[anchor=([^,]+),inner sep=0pt,font=\\fontsize\{([\d.]+)\}\{([\d.]+)\}\\selectfont\] at \((-?[\d.]+),(-?[\d.]+)\) \{(.*)\};")


def number(value): return f"{value:.3f}".rstrip("0").rstrip(".") or "0"
def pair(point, shift=0): return number(point[0]+shift) + " " + number(point[1])


def ellipse(x, y, rx, ry, shift):
    # A mesma elipse, em quatro curvas cúbicas padrão de PDF.
    k = 0.552284749831
    x += shift
    segments = [((x+rx, y+k*ry), (x+k*rx, y+ry), (x, y+ry)),
                ((x-k*rx, y+ry), (x-rx, y+k*ry), (x-rx, y)),
                ((x-rx, y-k*ry), (x-k*rx, y-ry), (x, y-ry)),
                ((x+k*rx, y-ry), (x+rx, y-k*ry), (x+rx, y))]
    return [pair((x+rx, y)) + " m"] + [" ".join(pair(p) for p in triplet) + " c" for triplet in segments]


def convert(lines, shift, width):
    paths, labels = [], []
    selected = set()
    for index, line in enumerate(lines):
        points = [(float(x), float(y)) for x, y in POINT.findall(line)]
        if not points: raise ValueError("Comando sem coordenadas: " + line)
        if line.startswith(r"\node"):
            match = NODE.fullmatch(line)
            if not match: raise ValueError("Nó desconhecido: " + line)
            anchor, size, leading, x, y, label = match.groups()
            x, y = float(x), float(y)
            # Margem conservadora para texto/subscritos nas bordas do recorte.
            low, high = x + shift - 160, x + shift + 160
            if high < 0 or low > width: continue
            aligned = {"base": "b", "base west": "lb", "base east": "rb"}[anchor]
            labels.append(r"\put(" + number(x+shift) + "," + number(y) + r"){\makebox(0,0)[" + aligned + r"]{\fontsize{" + size + "}{" + leading + r"}\selectfont " + label + "}}")
        else:
            radius = re.search(r"x radius=([\d.]+)bp,y radius=([\d.]+)bp", line)
            low, high = min(p[0] for p in points)+shift, max(p[0] for p in points)+shift
            if radius:
                rx, ry = map(float, radius.groups())
                low -= rx; high += rx
            if high < 0 or low > width: continue
            if radius:
                paths.extend(ellipse(*points[0], rx, ry, shift))
                paths.append("B" if line.startswith(r"\filldraw") else "S")
            elif "controls" in line:
                paths.append(pair(points[0], shift) + " m")
                for i in range(1, len(points), 3):
                    paths.append(" ".join(pair(p, shift) for p in points[i:i+3]) + " c")
                paths.append("S")
            else:
                paths.append(pair(points[0], shift) + " m")
                paths.extend(pair(p, shift)+" l" for p in points[1:])
                if "cycle" in line: paths.append("h")
                paths.append("B" if line.startswith(r"\filldraw") else "S")
        selected.add(index)
    return paths, labels, selected


def main():
    source = SOURCE.read_text(encoding="utf-8")
    definitions = {name: body.splitlines() for name, body in MACRO.findall(source)}
    if not definitions:
        if "% Diagramas vetoriais leves" in source:
            refresh_zip()
            print("Fonte já otimizada; ZIP sincronizado.")
            return
        raise RuntimeError("Não foi encontrado o formato esperado. Fonte preservada.")
    assert len(definitions) == 5
    covered = {name: set() for name in definitions}
    old_operations = new_operations = panels = 0
    def replace_panel(match):
        nonlocal old_operations, new_operations, panels
        width, height, shift = map(float, match.groups()[:3])
        name = match.group(4)
        paths, labels, selected = convert(definitions[name], shift, width)
        covered[name].update(selected)
        old_operations += len(definitions[name])
        new_operations += len(selected)
        panels += 1
        literal = "\n".join(["q", f"0 0 {number(width)} {number(height)} re W n", "0.6 w 0 G 0 g"] + paths + ["Q"])
        return (r"\clipbox{0pt 0pt 0pt 0pt}{\setlength{\unitlength}{1bp}" + "\n" +
                r"\begin{picture}(" + number(width) + "," + number(height) + ")\n" +
                r"\put(0,0){\pdfliteral{" + literal + "}}\n" +
                "\n".join(labels) + "\n" + r"\end{picture}}")
    revised, count = PANEL.subn(replace_panel, source)
    assert count == 27, f"Número de faixas inesperado: {count}"
    for name, lines in definitions.items():
        assert covered[name] == set(range(len(lines))), f"Primitivas ausentes: {name}"
    revised = MACRO.sub("", revised)
    revised = revised.replace(r"\usepackage{graphicx,tikz}", r"\usepackage{graphicx,adjustbox}")
    revised = revised.replace("% Compatível com Overleaf, sem shell-escape ou arquivos externos.",
                              "% Compatível com Overleaf/pdfLaTeX, sem shell-escape ou arquivos externos.\n% Diagramas vetoriais leves: somente os caminhos visíveis de cada faixa.\n% Não usa TikZ na compilação; primitivas PDF preservam o layout Graphviz.")
    assert "tikzpicture" not in revised and r"\NFA" not in revised
    tmp = ROOT / "tmp"
    tmp.mkdir(exist_ok=True)
    (tmp / "relatorio-antes-otimizacao.tex").write_text(source, encoding="utf-8")
    SOURCE.write_text(revised, encoding="utf-8")
    refresh_zip()
    print(f"Faixas preservadas: {panels}. Primitivas desenhadas: {old_operations} -> {new_operations}.")
    print("Cobertura verificada: todos os caminhos e rótulos dos cinco autômatos.")


def refresh_zip():
    with ZipFile(ROOT / "docs/relatorio-overleaf.zip", "w", ZIP_DEFLATED) as archive:
        archive.write(SOURCE, "main.tex")


if __name__ == "__main__": main()
