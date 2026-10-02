from dataclasses import dataclass
import re
import string
from .patterns import PATTERNS


@dataclass(frozen=True)
class Expr:
    kind: str
    value: str = ""
    children: tuple = ()

    def pattern(self):
        if self.kind == "literal":
            return re.escape(self.value)
        if self.kind == "set":
            return "[" + "".join(re.escape(c) for c in self.value) + "]"
        if self.kind == "epsilon":
            return ""
        if self.kind == "seq":
            return "".join(c.pattern() for c in self.children)
        if self.kind == "alt":
            return "(?:" + "|".join(c.pattern() for c in self.children) + ")"
        if self.kind == "star":
            return "(?:" + self.children[0].pattern() + ")*"
        if self.kind == "capture":
            return "(?P<" + self.value + ">" + self.children[0].pattern() + ")"
        raise ValueError(self.kind)

    def formal(self):
        if self.kind == "literal":
            return "".join("␠" if c == " " else "'" + c + "'" for c in self.value)
        if self.kind == "set":
            return "(" + " ∪ ".join("'" + c + "'" for c in self.value) + ")"
        if self.kind == "epsilon":
            return "ε"
        if self.kind == "seq":
            return " ".join(c.formal() for c in self.children)
        if self.kind == "alt":
            return "(" + " ∪ ".join(c.formal() for c in self.children) + ")"
        if self.kind == "star":
            return "(" + self.children[0].formal() + ")*"
        return self.children[0].formal()

    def alphabet(self):
        return set(self.value) if self.kind in ("literal", "set") else set().union(*(c.alphabet() for c in self.children))


def lit(s): return Expr("literal", s)
def chars(s): return Expr("set", s)
def seq(*xs): return Expr("seq", children=xs)
def alt(*xs): return Expr("alt", children=xs)
def star(x): return Expr("star", children=(x,))
def cap(name, x): return Expr("capture", name, (x,))
EPS = Expr("epsilon")
def optional(x): return alt(EPS, x)

D = chars(string.digits)
L = chars(string.ascii_lowercase)
NAME = seq(L, star(chars(string.ascii_lowercase + string.digits + "_")))
NUMBER = seq(chars("123456789"), optional(D))  # 1 a 99
BONUS = seq(optional(chars("+-")), D, optional(D))  # 0 a 99, sinal opcional
QUANTITY = alt(chars("123456789"), seq(lit("1"), D), lit("20"))
FACES = alt(*(lit(s) for s in ("4", "6", "8", "10", "12", "20", "100")))
DICE = seq(QUANTITY, lit("d"), FACES, optional(seq(chars("+-"), D, optional(D))))
ATTRIBUTE = alt(*(lit(s) for s in ("forca", "destreza", "constituicao", "inteligencia", "sabedoria", "carisma")))


@dataclass(frozen=True)
class Rule:
    key: str
    title: str
    purpose: str
    syntax: str
    expr: Expr

    @property
    def pattern(self): return PATTERNS[self.key]

    def match(self, text): return re.fullmatch(self.pattern, text)


RULES = (
    Rule("rolar", "Rolagem de dados", "Extrair quantidade, faces e modificador de uma rolagem.", "/rolar 2d6+3", seq(lit("/rolar "), cap("dados", DICE))),
    Rule("atacar", "Ataque", "Extrair alvo, bônus de acerto, classe de armadura e dano.", "/atacar goblin bonus=5 ca=14 dano=1d8+2", seq(lit("/atacar "), cap("alvo", NAME), lit(" bonus="), cap("bonus", BONUS), lit(" ca="), cap("ca", NUMBER), lit(" dano="), cap("dados", DICE))),
    Rule("magia", "Magia ofensiva", "Extrair magia, alvo, dificuldade, bônus de resistência e dano.", "/magia fogo alvo=goblin cd=12 bonus=3 dano=2d6", seq(lit("/magia "), cap("magia", NAME), lit(" alvo="), cap("alvo", NAME), lit(" cd="), cap("cd", NUMBER), lit(" bonus="), cap("bonus", BONUS), lit(" dano="), cap("dados", DICE))),
    Rule("curar", "Cura", "Extrair alvo e dados dos pontos de vida recuperados.", "/curar ana 2d8+3", seq(lit("/curar "), cap("alvo", NAME), lit(" "), cap("dados", DICE))),
    Rule("teste", "Teste de atributo", "Extrair atributo, bônus e classe de dificuldade.", "/teste forca bonus=-2 cd=15", seq(lit("/teste "), cap("atributo", ATTRIBUTE), lit(" bonus="), cap("bonus", BONUS), lit(" cd="), cap("cd", NUMBER))),
)
