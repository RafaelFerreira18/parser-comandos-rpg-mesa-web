"""Construção composicional de AFNε e simulação sem usar re."""
from dataclasses import dataclass, field
from collections import defaultdict
import json
import xml.etree.ElementTree as ET


@dataclass
class NFA:
    initial: int = 0
    final: int = 1
    states: int = 2
    edges: list = field(default_factory=list)

    def new(self):
        state = self.states
        self.states += 1
        return state

    def build(self, expr, start, end):
        kind = expr.kind
        if kind == "capture":
            self.build(expr.children[0], start, end)
        elif kind == "epsilon":
            self.edges.append((start, end, ""))
        elif kind == "set":
            for symbol in expr.value:
                self.edges.append((start, end, symbol))
        elif kind == "literal":
            current = start
            for index, symbol in enumerate(expr.value):
                nxt = end if index == len(expr.value) - 1 else self.new()
                self.edges.append((current, nxt, symbol))
                current = nxt
            if not expr.value:
                self.edges.append((start, end, ""))
        elif kind == "seq":
            current = start
            for index, child in enumerate(expr.children):
                nxt = end if index == len(expr.children) - 1 else self.new()
                self.build(child, current, nxt)
                current = nxt
        elif kind == "alt":
            for child in expr.children:
                a, b = self.new(), self.new()
                self.edges.extend(((start, a, ""), (b, end, "")))
                self.build(child, a, b)
        elif kind == "star":
            a, b = self.new(), self.new()
            self.edges.extend(((start, end, ""), (start, a, ""), (b, a, ""), (b, end, "")))
            self.build(expr.children[0], a, b)
        else:
            raise ValueError(kind)

    def accepts(self, text):
        transitions = defaultdict(set)
        for a, b, symbol in self.edges:
            transitions[a, symbol].add(b)
        def closure(states):
            seen, todo = set(states), list(states)
            while todo:
                for nxt in transitions[todo.pop(), ""]:
                    if nxt not in seen:
                        seen.add(nxt)
                        todo.append(nxt)
            return seen
        states = closure({self.initial})
        for symbol in text:
            states = closure(set().union(*(transitions[s, symbol] for s in states)))
            if not states:
                return False
        return self.final in states

    def dot(self, title):
        grouped = defaultdict(list)
        for a, b, symbol in self.edges:
            grouped[a, b].append(symbol)
        lines = ['digraph NFA {', 'rankdir=LR; bgcolor="#ffffff";',
                 'graph [fontname="Arial", label=' + json.dumps(title, ensure_ascii=False) + ', labelloc=t];',
                 'node [shape=circle, fontsize=10, width=.32, fontname="Arial"];',
                 'edge [fontsize=9, fontname="Arial"];', 'start [shape=point];',
                 f'start -> q{self.initial};', f'q{self.final} [shape=doublecircle];']
        for (a, b), symbols in grouped.items():
            symbols = sorted(symbols)
            label = ("[a-z0-9_]" if set(symbols) == set("abcdefghijklmnopqrstuvwxyz0123456789_") else
                     "[a-z]" if set(symbols) == set("abcdefghijklmnopqrstuvwxyz") else
                     "[0-9]" if set(symbols) == set("0123456789") else
                     "[1-9]" if set(symbols) == set("123456789") else
                     ", ".join("ε" if s == "" else "␠" if s == " " else s for s in symbols))
            lines.append(f'q{a} -> q{b} [label={json.dumps(label, ensure_ascii=False)}];')
        return "\n".join(lines + ['}'])

    def jff(self):
        root = ET.Element("structure")
        ET.SubElement(root, "type").text = "fa"
        automaton = ET.SubElement(root, "automaton")
        for state in range(self.states):
            item = ET.SubElement(automaton, "state", id=str(state), name=f"q{state}")
            ET.SubElement(item, "x").text = str(80 + (state % 12) * 100)
            ET.SubElement(item, "y").text = str(80 + (state // 12) * 100)
            if state == self.initial: ET.SubElement(item, "initial")
            if state == self.final: ET.SubElement(item, "final")
        for a, b, symbol in self.edges:
            edge = ET.SubElement(automaton, "transition")
            ET.SubElement(edge, "from").text = str(a)
            ET.SubElement(edge, "to").text = str(b)
            ET.SubElement(edge, "read").text = symbol or None
        ET.indent(root)
        return ET.tostring(root, encoding="unicode", xml_declaration=True)


def compile_nfa(expr):
    nfa = NFA()
    nfa.build(expr, nfa.initial, nfa.final)
    return nfa
