import json
import random
import threading
import unittest
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from http.server import ThreadingHTTPServer
from rpg.language import RULES
from rpg.automata import compile_nfa, NFA
from rpg.engine import execute, parse, CommandError
from rpg.server import Handler

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / "examples/cases.json").read_text(encoding="utf-8"))


class FixedRng:
    def __init__(self, *values): self.values = iter(values)
    def randint(self, a, b):
        value = next(self.values)
        assert a <= value <= b
        return value


class LanguageTests(unittest.TestCase):
    def test_required_cases_regex_and_nfa(self):
        for rule in RULES:
            self.assertEqual(rule.pattern, rule.expr.pattern())
            nfa = compile_nfa(rule.expr)
            for category, expected in (("accepted", True), ("rejected", False)):
                self.assertGreaterEqual(len(CASES[rule.key][category]), 6)
                for text in CASES[rule.key][category]:
                    with self.subTest(action=rule.key, text=text):
                        self.assertEqual(bool(rule.match(text)), expected)
                        self.assertEqual(nfa.accepts(text), expected)

    def test_equivalence_mutations(self):
        rng = random.Random(42)
        for rule in RULES:
            nfa = compile_nfa(rule.expr)
            samples = CASES[rule.key]["accepted"]
            for i in range(300):
                text = rng.choice(samples)
                index = rng.randrange(len(text) + 1)
                symbol = rng.choice("abcXYZ0129_ +-=/d\n\tá")
                changed = (text[:index] + symbol + text[index:] if i % 3 == 0 else
                           text[:index] + text[index+1:] if i % 3 == 1 else
                           text[:index] + symbol + text[index+1:])
                self.assertEqual(bool(rule.match(changed)), nfa.accepts(changed), changed)

    def test_exports_jflap(self):
        for rule in RULES:
            root = ET.parse(ROOT / "automata" / f"{rule.key}.jff").getroot()
            states = root.findall("automaton/state")
            nfa = NFA(states=len(states))
            nfa.initial = int(next(s for s in states if s.find("initial") is not None).get("id"))
            nfa.final = int(next(s for s in states if s.find("final") is not None).get("id"))
            nfa.edges = [(int(t.findtext("from")), int(t.findtext("to")), t.findtext("read") or "") for t in root.findall("automaton/transition")]
            self.assertEqual(nfa.edges, compile_nfa(rule.expr).edges)
            for category, expected in (("accepted", True), ("rejected", False)):
                for text in CASES[rule.key][category]: self.assertEqual(nfa.accepts(text), expected)

    def test_no_normalization_and_input_limits(self):
        for text in (None, 4, "", "  ", "/ROLAR 1d6", " /rolar 1d6", "/rolar 1d6\n", "/curar " + "a"*513 + " 1d6"):
            with self.assertRaises(CommandError): parse(text)


class EngineTests(unittest.TestCase):
    def test_dice_and_negative_total(self):
        self.assertEqual(execute("/rolar 2d6+3", FixedRng(2, 6))["rolagens"][0]["total"], 11)
        self.assertEqual(execute("/rolar 1d4-99", FixedRng(1))["rolagens"][0]["total"], -98)

    def test_attack_equal_threshold(self):
        result = execute("/atacar orc bonus=5 ca=14 dano=1d8+2", FixedRng(9, 4))
        self.assertTrue(result["sucesso"])
        self.assertEqual(result["dano"], 6)

    def test_failed_attack_does_not_roll_damage(self):
        result = execute("/atacar orc bonus=0 ca=20 dano=1d8", FixedRng(1))
        self.assertFalse(result["sucesso"])
        self.assertEqual(len(result["rolagens"]), 1)

    def test_magic_resistance_half_and_full(self):
        command = "/magia fogo alvo=orc cd=12 bonus=2 dano=1d6"
        result = execute(command, FixedRng(10, 5))
        self.assertFalse(result["sucesso"])
        self.assertTrue(result["resistencia_sucesso"])
        self.assertEqual(result["dano"], 2)
        self.assertEqual(execute(command, FixedRng(1, 5))["dano"], 5)

    def test_heal_and_damage_floor(self):
        self.assertEqual(execute("/curar ana 1d4-99", FixedRng(1))["cura"], 0)
        self.assertEqual(execute("/atacar orc bonus=0 ca=1 dano=1d4-99", FixedRng(2, 1))["dano"], 0)

    def test_attribute(self):
        self.assertFalse(execute("/teste forca bonus=-2 cd=15", FixedRng(16))["sucesso"])
        self.assertTrue(execute("/teste forca bonus=-2 cd=15", FixedRng(17))["sucesso"])

    def test_all_faces_and_max_quantity(self):
        for face in (4, 6, 8, 10, 12, 20, 100):
            roll = execute(f"/rolar 20d{face}", random.Random(12))["rolagens"][0]
            self.assertEqual(len(roll["valores"]), 20)
            self.assertTrue(all(1 <= v <= face for v in roll["valores"]))


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def call(self, path, data):
        request = urllib.request.Request(self.url + path, data=data, headers={"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(request) as response: return response.status, json.load(response)
        except urllib.error.HTTPError as response:
            return response.code, json.load(response)

    def test_static_and_rules(self):
        for path in ("/", "/style.css", "/app.js", "/api/regras"):
            with urllib.request.urlopen(self.url + path) as response: self.assertEqual(response.status, 200)

    def test_validation_has_no_rolls(self):
        status, body = self.call("/api/validar", b'{"comando":"/rolar 1d6"}')
        self.assertEqual(status, 200)
        self.assertNotIn("rolagens", body)

    def test_execution_and_errors(self):
        status, body = self.call("/api/executar", b'{"comando":"/rolar 1d6"}')
        self.assertEqual(status, 200)
        self.assertEqual(body["acao"], "rolar")
        for data in (b'{', b'[]', b'{}', b'{"comando":null}', b'{"comando":""}'):
            self.assertEqual(self.call("/api/executar", data)[0], 400)
        self.assertEqual(self.call("/api/executar", b'x'*4097)[0], 413)
        self.assertEqual(self.call("/api/unknown", b'{}')[0], 404)
