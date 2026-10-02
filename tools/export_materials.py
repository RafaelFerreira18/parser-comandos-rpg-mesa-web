"""Atualiza autômatos e fichas a partir da definição usada pela aplicação."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rpg.language import RULES
from rpg.automata import compile_nfa

ROOT = Path(__file__).resolve().parent.parent


def main():
    (ROOT / "automata").mkdir(exist_ok=True)
    (ROOT / "docs").mkdir(exist_ok=True)
    cases = json.loads((ROOT / "examples/cases.json").read_text(encoding="utf-8"))
    (ROOT / "rpg/patterns.py").write_text(
        '# Gerado por tools/export_materials.py. Nao editar manualmente.\nPATTERNS = {\n' +
        ''.join('    ' + repr(rule.key) + ': r"' + rule.expr.pattern() + '",\n' for rule in RULES) + '}\n',
        encoding="utf-8")
    parts = ["# Fichas das cinco expressões regulares\n", "Geradas de `rpg/language.py`. Cada padrão usa `re.fullmatch`, sem flags e sem normalização.\n",
             "## Convenções\n\nΣ é declarado individualmente. ␠ representa exatamente U+0020. Literais estão entre aspas simples. União ∪, concatenação por justaposição, estrela * e ε têm o significado do guia. Aspas e ␠ são metanotação, não caracteres extras.\n",
             "As classes do padrão Python expandem conjuntos finitos. `(?:...)` agrupa sem capturar; `(?P<nome>...)` captura parâmetros sem mudar a linguagem. Não há lookaround, retroreferências, recursão, `\\w`, `\\d`, `\\s` ou âncoras ambíguas.\n",
             "Quantidade: 1 a 20, sem zero inicial. Faces: 4, 6, 8, 10, 12, 20, 100. Modificador dos dados: sinal obrigatório se presente, seguido de um ou dois dígitos. Bônus: sinal opcional, um ou dois dígitos (00 e +05 aceitos). CA/CD: 1 a 99 sem zero inicial. Nomes: [a-z][a-z0-9_]*.\n",
             "A linguagem regular admite nomes de qualquer comprimento. O serviço impõe separadamente 512 caracteres por comando e 4096 bytes por requisição. Esses limites operacionais não são parte das cinco ER.\n"]
    manifest = []
    for index, rule in enumerate(RULES, 1):
        pattern = rule.expr.pattern()
        nfa = compile_nfa(rule.expr)
        (ROOT / "automata" / f"{rule.key}.dot").write_text(nfa.dot(rule.title), encoding="utf-8")
        (ROOT / "automata" / f"{rule.key}.jff").write_text(nfa.jff(), encoding="utf-8")
        manifest.append({"id": f"ER-{index:02}", "acao": rule.key, "nome": rule.title, "finalidade": rule.purpose,
                         "exemplo": rule.syntax, "regex": pattern, "formal": rule.expr.formal(),
                         "alfabeto": sorted(rule.expr.alphabet()), "estados": nfa.states, "transicoes": len(nfa.edges),
                         "inicial": nfa.initial, "finais": [nfa.final], "casos": cases[rule.key]})
        parts += [f"\n## ER-{index:02}: {rule.title}\n\n{rule.purpose}\n\n",
                  "**Alfabeto Σ:** " + ", ".join("␠" if c == " " else repr(c) for c in sorted(rule.expr.alphabet())) + "\n\n",
                  f"**Linguagem:** comandos completos no formato `{rule.syntax}`, com parâmetros nos domínios das convenções acima. A ordem e os espaços são obrigatórios.\n\n",
                  "**ER formal expandida:**\n\n" + rule.expr.formal() + "\n\n",
                  "**Sintaxe exata em `rpg/patterns.py`, utilizada por Rule.pattern:**\n\n```python\nr\"" + pattern + "\"\n# re.fullmatch(rule.pattern, texto)\n```\n\n",
                  f"**AFNε:** início q{nfa.initial}, final q{nfa.final}; {nfa.states} estados e {len(nfa.edges)} transições elementares. Arquivos `automata/{rule.key}.dot`, `.svg`, `.jff`. O SVG agrupa transições paralelas de um caractere; no JFLAP cada símbolo tem sua própria transição. `<read />` é movimento vazio.\n\n",
                  "| Cadeia | Esperado |\n|---|---|\n"]
        for category, label in (("accepted", "Aceita"), ("rejected", "Rejeitada")):
            for text in cases[rule.key][category]:
                parts.append("| `" + text.replace("\n", "\\n").replace("\t", "\\t") + "` | " + label + " |\n")
        parts.append("\nCaso-limite: primeira cadeia aceita usa os mínimos; a segunda ou terceira explora limites superiores. A cadeia vazia é rejeitada.\n\n**Transições completas:**\n\n| Origem | Símbolo | Destino |\n|---|---|---|\n")
        for a, b, symbol in nfa.edges:
            parts.append(f"| q{a} | {'ε' if not symbol else '␠' if symbol == ' ' else symbol} | q{b} |\n")
    (ROOT / "docs/expressoes-regulares.md").write_text("".join(parts), encoding="utf-8")
    (ROOT / "docs/manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Cinco AFNε (.dot/.jff), fichas e manifesto gerados.")


if __name__ == "__main__": main()
