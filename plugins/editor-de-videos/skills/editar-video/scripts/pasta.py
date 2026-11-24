"""Acha (ou cria) a pasta "Edição de Vídeos IA" do aluno, com "1. Para editar" e "2. Concluídos".

Procura primeiro no Google Drive sincronizado no computador (Google Drive para computador), depois na Área de
Trabalho. Guarda o caminho escolhido em ~/EditorDeVideosIA/config.json para as próximas vezes.

Uso:
  python pasta.py                  mostra a pasta (cria se não existir)
  python pasta.py --definir <caminho>   usa esta pasta (ex.: a pasta que a pessoa arrastou para o chat)
"""
import string, sys
from pathlib import Path
from comum import ler_config, salvar_config, NOME_RAIZ, PARA_EDITAR, CONCLUIDOS


def drives_do_google():
    """Pastas "Meu Drive"/"My Drive" do Google Drive para computador (Windows, Mac)."""
    casa = Path.home()
    candidatos = []
    if sys.platform.startswith("win"):
        for letra in string.ascii_uppercase[3:]:            # D: em diante (G: é o padrão do Drive)
            candidatos += [Path(f"{letra}:/Meu Drive"), Path(f"{letra}:/My Drive")]
        candidatos += [casa / "Google Drive", casa / "Meu Drive"]
    else:
        nuvem = casa / "Library" / "CloudStorage"
        if nuvem.exists():
            for d in sorted(nuvem.glob("GoogleDrive-*")):
                candidatos += [d / "Meu Drive", d / "My Drive"]
        candidatos += [casa / "Google Drive" / "Meu Drive", casa / "Google Drive" / "My Drive", casa / "Google Drive"]
    return [c for c in candidatos if c.exists()]


def area_de_trabalho():
    casa = Path.home()
    for d in ("Desktop", "Área de Trabalho", "Escritorio", "OneDrive/Desktop", "OneDrive/Área de Trabalho"):
        if (casa / d).exists():
            return casa / d
    return casa


def preparar(raiz):
    raiz = Path(raiz)
    (raiz / PARA_EDITAR).mkdir(parents=True, exist_ok=True)
    (raiz / CONCLUIDOS).mkdir(parents=True, exist_ok=True)
    salvar_config(pasta=str(raiz))
    return raiz


def pasta_do_aluno(criar=True):
    c = ler_config().get("pasta")
    if c and Path(c).exists():
        return Path(c)
    for d in drives_do_google():
        if (d / NOME_RAIZ).exists():
            return preparar(d / NOME_RAIZ)
    if not criar:
        return None
    base = (drives_do_google() or [area_de_trabalho()])[0]
    return preparar(base / NOME_RAIZ)


if __name__ == "__main__":
    if "--definir" in sys.argv:
        alvo = Path(sys.argv[sys.argv.index("--definir") + 1]).expanduser()
        if alvo.name in (PARA_EDITAR, CONCLUIDOS):
            alvo = alvo.parent
        raiz = preparar(alvo)
    else:
        raiz = pasta_do_aluno()
    no_drive = any(str(raiz).startswith(str(d)) for d in drives_do_google())
    print(f"Pasta: {raiz}")
    print(f"  Para editar: {raiz / PARA_EDITAR}")
    print(f"  Concluídos:  {raiz / CONCLUIDOS}")
    print("  Está no Google Drive: sim" if no_drive else
          "  Está no Google Drive: NÃO (Google Drive para computador não encontrado; a pasta ficou no computador)")
