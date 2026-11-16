"""Confere o ambiente e quais sites a sessão consegue acessar. Só leitura."""
import os
import shutil

OK, FALHA = "[ok]", "[FALHA]"


def ffmpeg_disponivel():
    if shutil.which("ffmpeg"):
        return "sistema"
    try:
        import imageio_ffmpeg
        imageio_ffmpeg.get_ffmpeg_exe()
        return "pip (imageio-ffmpeg)"
    except Exception:
        return None


def checar_pacote(nome):
    try:
        __import__(nome)
        return True
    except Exception:
        return False


def checar_site(url):
    try:
        import requests
        r = requests.get(url, timeout=15)
        # 401/404 também servem: o importante é o site responder, não o bloqueio do proxy
        bloqueado = r.status_code == 403 and "host_not_allowed" in r.text.lower()
        return (not bloqueado, f"HTTP {r.status_code}")
    except Exception as e:
        return (False, type(e).__name__)


def main():
    print("== Ambiente ==")
    ff = ffmpeg_disponivel()
    print(f"{OK if ff else FALHA} ffmpeg: {ff or 'não encontrado'}")
    for pacote in ["requests", "faster_whisper", "yt_dlp", "gdown"]:
        print(f"{OK if checar_pacote(pacote) else FALHA} {pacote}")
    print(f"     CPUs: {os.cpu_count()}")
    chave = bool(os.environ.get("ELEVENLABS_API_KEY"))
    print(f"     Chave ElevenLabs na variável: {'sim' if chave else 'não'}")

    print("== Acesso à internet ==")
    sites = {
        "GitHub": "https://github.com",
        "Hugging Face (modelo do Whisper)": "https://huggingface.co/api/models/Systran/faster-whisper-small",
        "ElevenLabs": "https://api.elevenlabs.io/v1/models",
        "Litterbox (link de download)": "https://litterbox.catbox.moe",
        "Google Drive": "https://drive.google.com",
        "YouTube": "https://www.youtube.com",
    }
    for nome, url in sites.items():
        ok, detalhe = checar_site(url)
        print(f"{OK if ok else FALHA} {nome}: {detalhe}")


if __name__ == "__main__":
    main()
