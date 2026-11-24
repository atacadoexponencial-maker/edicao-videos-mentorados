"""Instala o que a edição precisa (uma vez por computador). Pode rodar de novo sem problema.

- pacotes Python: Whisper (transcrição grátis), ffmpeg (via static-ffmpeg), Pillow, gdown, yt-dlp;
- baixa o ffmpeg e o modelo do Whisper, para a primeira edição não demorar;
- cria a pasta "Edição de Vídeos IA" (no Google Drive do computador, se tiver; senão na Área de Trabalho).

Uso: python instalar.py
"""
import subprocess, sys
from pathlib import Path

REQ = Path(__file__).resolve().parents[1] / "requirements.txt"
if sys.version_info < (3, 9):
    sys.exit(f"Python {sys.version.split()[0]} é antigo demais. Instale o Python 3.12 (python.org) e rode de novo.")

print("1/3 Instalando os pacotes (alguns minutos na primeira vez)...", flush=True)
base = [sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check", "-r", str(REQ)]
r = subprocess.run(base + ["--user"]) if subprocess.run(base).returncode else None
if r is not None and r.returncode:
    r = subprocess.run(base + ["--break-system-packages", "--user"])
    if r.returncode:
        sys.exit("Não consegui instalar os pacotes. Mostre esta mensagem para quem te ajuda.")

print("2/3 Baixando o ffmpeg e o Whisper...", flush=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum  # noqa: E402  (garante o ffmpeg no PATH)
comum.run(["ffmpeg", "-version"])
from faster_whisper import WhisperModel  # noqa: E402
WhisperModel(comum.env("WHISPER_MODELO") or "small", device="cpu", compute_type="int8")

print("3/3 Preparando a pasta dos vídeos...", flush=True)
from pasta import pasta_do_aluno  # noqa: E402
raiz = pasta_do_aluno()
print(f"\nTudo pronto. Pasta dos vídeos: {raiz}")
