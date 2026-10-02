import json
from .engine import execute, CommandError
from .language import RULES


def main():
    while True:
        print("\nRPG de Mesa\n1. Executar comando\n2. Exemplos e sintaxe\n0. Sair")
        try:
            option = input("Escolha: ")
            if option == "0":
                return
            if option == "2":
                for rule in RULES:
                    print(rule.syntax)
            elif option == "1":
                try:
                    result = execute(input("Comando: "))
                    print(result["mensagem"])
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                except CommandError as exc:
                    print(f"Erro: {exc}")
            else:
                print("Opção inválida. Escolha 0, 1 ou 2.")
        except (EOFError, KeyboardInterrupt):
            print("\nAté a próxima aventura!")
            return


if __name__ == "__main__":
    main()
