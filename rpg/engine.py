from dataclasses import dataclass
import random
from .language import RULES

MAX_INPUT = 512


class CommandError(ValueError):
    pass


@dataclass(frozen=True)
class Command:
    action: str
    parameters: dict
    text: str


def parse(text):
    if not isinstance(text, str):
        raise CommandError("O comando deve ser um texto.")
    if not text or not text.strip():
        raise CommandError("Digite um comando antes de executar.")
    if len(text) > MAX_INPUT:
        raise CommandError("O comando excede o limite operacional de 512 caracteres.")
    for rule in RULES:
        match = rule.match(text)
        if match:
            return Command(rule.key, match.groupdict(), text)
    raise CommandError("Sintaxe inválida. Use letras minúsculas, um espaço entre campos e a ordem indicada nos exemplos.")


def roll_dice(spec, rng):
    quantity, tail = spec.split("d")
    sign_index = next((i for i, c in enumerate(tail) if c in "+-"), len(tail))
    faces = int(tail[:sign_index])
    modifier = int(tail[sign_index:]) if sign_index < len(tail) else 0
    rolls = [rng.randint(1, faces) for _ in range(int(quantity))]
    return {"expressao": spec, "valores": rolls, "faces": faces,
            "modificador": modifier, "total": sum(rolls) + modifier}


def execute(text, rng=None):
    command = parse(text)
    rng = rng if rng is not None else random.SystemRandom()
    p = command.parameters
    result = {"ok": True, "acao": command.action, "comando": text, "parametros": p,
              "sucesso": None, "dano": 0, "cura": 0, "rolagens": []}
    if command.action in ("rolar", "curar"):
        dice = roll_dice(p["dados"], rng)
        result["rolagens"].append(dice)
        if command.action == "curar":
            result["cura"] = max(0, dice["total"])
            result["mensagem"] = f'{p["alvo"]} recupera {result["cura"]} PV.'
        else:
            result["mensagem"] = f'Rolagem {p["dados"]}: total {dice["total"]}.'
    elif command.action in ("atacar", "teste"):
        d20 = roll_dice("1d20", rng)
        d20["modificador"] = int(p["bonus"])
        d20["total"] += int(p["bonus"])
        result["rolagens"].append(d20)
        target = int(p.get("ca", p.get("cd")))
        result["sucesso"] = d20["total"] >= target
        if command.action == "atacar":
            if result["sucesso"]:
                damage = roll_dice(p["dados"], rng)
                result["rolagens"].append(damage)
                result["dano"] = max(0, damage["total"])
            result["mensagem"] = f'Ataque em {p["alvo"]}: {"sucesso" if result["sucesso"] else "falha"}. Dano: {result["dano"]}.'
        else:
            result["mensagem"] = f'Teste de {p["atributo"]}: {"sucesso" if result["sucesso"] else "falha"} ({d20["total"]} contra CD {target}).'
    else:
        resistance = roll_dice("1d20", rng)
        resistance["modificador"] = int(p["bonus"])
        resistance["total"] += int(p["bonus"])
        damage = roll_dice(p["dados"], rng)
        result["rolagens"] += [resistance, damage]
        resisted = resistance["total"] >= int(p["cd"])
        result["sucesso"] = not resisted
        result["resistencia_sucesso"] = resisted
        result["dano"] = max(0, damage["total"]) // (2 if resisted else 1)
        result["mensagem"] = f'{p["magia"]} em {p["alvo"]}: {"resistiu" if resisted else "não resistiu"}. Dano: {result["dano"]}.'
    return result
