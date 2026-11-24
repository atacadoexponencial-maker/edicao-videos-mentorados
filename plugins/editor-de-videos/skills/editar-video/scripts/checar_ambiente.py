"""Confere se o computador tem tudo para editar. Não mostra o valor de nenhuma chave.

Uso: python checar_ambiente.py      (saída 1 = falta algo: rode instalar.py)
"""
import importlib, os, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
falhou = False


def linha(ok, nome, detalhe=""):
    global falhou
    falhou |= not ok
    print(f"[{'OK' if ok else 'FALTA'}] {nome}" + (f": {detalhe}" if detalhe else ""))


linha(sys.version_info >= (3, 9), "Python", sys.version.split()[0])
for mod, nome in [("faster_whisper", "Whisper (transcrição)"), ("PIL", "Pillow (imagens)"), ("requests", "requests"),
                  ("gdown", "gdown (links do Drive)"), ("static_ffmpeg", "static-ffmpeg")]:
    try:
        importlib.import_module(mod); linha(True, nome)
    except Exception as e:
        linha(False, nome, f"{type(e).__name__}; rode instalar.py")
try:
    import av
    linha(int(av.__version__.split(".")[0]) < 19, "PyAV", av.__version__ + ("" if int(av.__version__.split(".")[0]) < 19 else " (versão nova quebra o Whisper; rode instalar.py)"))
except Exception:
    linha(False, "PyAV", "rode instalar.py")
try:
    import comum
    linha(bool(shutil.which("ffmpeg") and shutil.which("ffprobe")), "ffmpeg e ffprobe", shutil.which("ffmpeg") or "")
    from pasta import pasta_do_aluno, drives_do_google
    raiz = pasta_do_aluno(criar=False)
    if raiz:
        no_drive = any(str(raiz).startswith(str(d)) for d in drives_do_google())
        linha(True, "pasta dos vídeos", f"{raiz}" + ("" if no_drive else " (fora do Google Drive)"))
    else:
        linha(False, "pasta dos vídeos", "ainda não criada; rode pasta.py")
    print(f"[INFO] transcrição: {'ElevenLabs (chave encontrada)' if comum.env('ELEVENLABS') else 'Whisper grátis, modelo ' + (comum.env('WHISPER_MODELO') or 'small')}")
    livre = shutil.disk_usage(comum.TRABALHO.parent).free / 1e9
    linha(livre > 5, "espaço livre", f"{livre:.0f} GB")
except Exception as e:
    linha(False, "scripts", f"{type(e).__name__}: {e}")
sys.exit(1 if falhou else 0)
