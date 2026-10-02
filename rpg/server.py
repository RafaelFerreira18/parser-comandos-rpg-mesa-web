"""Servidor HTTP local usando exclusivamente a biblioteca padrão."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from .engine import execute, parse, CommandError
from .language import RULES

WEB = Path(__file__).resolve().parent.parent / "web"
FILES = {"/": ("index.html", "text/html"), "/app.js": ("app.js", "text/javascript"),
         "/style.css": ("style.css", "text/css")}


class Handler(BaseHTTPRequestHandler):
    def respond(self, status, body, content_type="application/json"):
        if isinstance(body, dict):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/regras":
            self.respond(200, {"regras": [{"acao": r.key, "nome": r.title, "exemplo": r.syntax} for r in RULES]})
        elif path in FILES:
            filename, mime = FILES[path]
            self.respond(200, (WEB / filename).read_bytes(), mime)
        else:
            self.respond(404, {"ok": False, "erro": "Recurso não encontrado."})

    def do_POST(self):
        if self.path not in ("/api/executar", "/api/validar"):
            self.respond(404, {"ok": False, "erro": "Rota não encontrada."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 4096:
                self.close_connection = True
                self.respond(413, {"ok": False, "erro": "Envie um corpo JSON de até 4096 bytes."})
                return
            self.connection.settimeout(5)
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            if not isinstance(payload, dict):
                raise CommandError("Envie um objeto JSON com o campo comando.")
            text = payload.get("comando")
            if self.path == "/api/validar":
                command = parse(text)
                self.respond(200, {"ok": True, "acao": command.action, "parametros": command.parameters})
            else:
                self.respond(200, execute(text))
        except (ValueError, UnicodeError, CommandError) as exc:
            self.respond(400, {"ok": False, "erro": str(exc)})
        except (TimeoutError, OSError):
            self.close_connection = True


def main():
    parser = argparse.ArgumentParser(description="Parser de comandos de RPG de mesa")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Abra http://{args.host}:{args.port} (Ctrl+C para encerrar)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
