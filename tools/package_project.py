"""Compacta somente arquivos de entrega, excluindo Git e intermediários."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "parser-comandos-rpg-mesa-web.zip"
excluded = {".git", "tmp", "node_modules", "__pycache__", ".venv"}


def main():
    files = [p for p in ROOT.rglob("*") if p.is_file() and p != DEST
             and not excluded.intersection(p.relative_to(ROOT).parts)
             and p.suffix not in (".pyc", ".zip")]
    with ZipFile(DEST, "w", ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, str(Path(ROOT.name) / path.relative_to(ROOT)))
    print(f"Pacote gerado: {DEST.name} ({len(files)} arquivos)")


if __name__ == "__main__": main()
