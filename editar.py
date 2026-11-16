"""Edição de teste: baixa o vídeo, transcreve, corta as pausas longas e devolve o link.

Uso:
  python3 editar.py <link-ou-arquivo> [--motor auto|whisper|elevenlabs] [--modelo small] [--pausa 0.6] [--sem-link]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
TRABALHO = RAIZ / "trabalho"
SAIDA = RAIZ / "saida"
FOLGA = 0.15  # respiro antes e depois de cada trecho, em segundos


def caminho_ffmpeg():
    sistema = shutil.which("ffmpeg")
    if sistema:
        return sistema
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def rodar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"Erro rodando {cmd[0]}:\n{r.stderr[-2000:]}")
    return r


def duracao(video):
    r = subprocess.run([caminho_ffmpeg(), "-i", str(video)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    if not m:
        sys.exit("Não consegui ler a duração do vídeo.")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


def baixar(fonte):
    if Path(fonte).exists():
        return Path(fonte)
    destino = TRABALHO / "bruto.mp4"
    if "drive.google.com" in fonte:
        import gdown
        if not gdown.download(fonte, output=str(destino), fuzzy=True, quiet=True):
            sys.exit("Não consegui baixar do Drive. O link precisa estar como 'qualquer pessoa com o link'.")
        return destino
    if re.search(r"\.(mp4|mov|m4v|webm)(\?|$)", fonte, re.I):
        import requests
        with requests.get(fonte, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(destino, "wb") as f:
                for bloco in r.iter_content(1 << 20):
                    f.write(bloco)
        return destino
    rodar([sys.executable, "-m", "yt_dlp", "-q", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
           "--ffmpeg-location", caminho_ffmpeg(), "-o", str(destino), fonte])
    return destino


def extrair_audio(video):
    audio = TRABALHO / "audio.wav"
    rodar([caminho_ffmpeg(), "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(audio)])
    return audio


def transcrever_whisper(audio, modelo, idioma):
    from faster_whisper import WhisperModel
    try:
        m = WhisperModel(modelo, device="cpu", compute_type="int8")
    except Exception as e:
        sys.exit(f"Não consegui baixar o modelo do Whisper ({type(e).__name__}). "
                 "Libere huggingface.co e *.huggingface.co em 'Allowed domains' do ambiente.")
    segmentos, _ = m.transcribe(str(audio), language=idioma, word_timestamps=True)
    return [{"texto": w.word.strip(), "inicio": w.start, "fim": w.end}
            for s in segmentos for w in (s.words or [])]


def transcrever_elevenlabs(audio, idioma):
    import requests
    cabecalhos = {}
    chave = os.environ.get("ELEVENLABS_API_KEY")
    if chave:
        cabecalhos["xi-api-key"] = chave  # sem a variável, conta com o "network secret" do ambiente
    idiomas = {"pt": "por", "en": "eng", "es": "spa"}
    with open(audio, "rb") as f:
        r = requests.post("https://api.elevenlabs.io/v1/speech-to-text", headers=cabecalhos,
                          data={"model_id": "scribe_v2", "language_code": idiomas.get(idioma, idioma),
                                "timestamps_granularity": "word"},
                          files={"file": f}, timeout=600)
    if r.status_code != 200:
        sys.exit(f"ElevenLabs respondeu {r.status_code}: {r.text[:300]}")
    return [{"texto": w["text"], "inicio": w["start"], "fim": w["end"]}
            for w in r.json().get("words", []) if w.get("type") == "word"]


def montar_trechos(palavras, pausa_max, total):
    if not palavras:
        sys.exit("A transcrição não achou fala no vídeo.")
    trechos = []
    inicio = palavras[0]["inicio"]
    for atual, proxima in zip(palavras, palavras[1:]):
        if proxima["inicio"] - atual["fim"] > pausa_max:
            trechos.append([inicio, atual["fim"]])
            inicio = proxima["inicio"]
    trechos.append([inicio, palavras[-1]["fim"]])
    com_folga = [[max(0.0, a - FOLGA), min(total, b + FOLGA)] for a, b in trechos]
    unidos = [com_folga[0]]
    for a, b in com_folga[1:]:
        if a <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], b)
        else:
            unidos.append([a, b])
    return unidos


def renderizar(video, trechos, destino):
    partes, rotulos = [], ""
    for i, (a, b) in enumerate(trechos):
        partes.append(f"[0:v]trim=start={a:.3f}:end={b:.3f},setpts=PTS-STARTPTS[v{i}]")
        partes.append(f"[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS[a{i}]")
        rotulos += f"[v{i}][a{i}]"
    partes.append(f"{rotulos}concat=n={len(trechos)}:v=1:a=1[v][a]")
    roteiro = TRABALHO / "filtro.txt"
    roteiro.write_text(";\n".join(partes), encoding="utf-8")
    rodar([caminho_ffmpeg(), "-y", "-i", str(video), "-filter_complex_script", str(roteiro),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
           "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(destino)])


def enviar_link(arquivo):
    try:
        import requests
        with open(arquivo, "rb") as f:
            r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                              data={"reqtype": "fileupload", "time": "72h"},
                              files={"fileToUpload": f}, timeout=600)
        if r.status_code == 200 and r.text.startswith("http"):
            return r.text.strip()
        return None
    except Exception:
        return None


def main():
    p = argparse.ArgumentParser()
    p.add_argument("fonte")
    p.add_argument("--motor", default="auto", choices=["auto", "whisper", "elevenlabs"])
    p.add_argument("--modelo", default="small")
    p.add_argument("--idioma", default="pt")
    p.add_argument("--pausa", type=float, default=0.6)
    p.add_argument("--sem-link", action="store_true")
    args = p.parse_args()

    TRABALHO.mkdir(exist_ok=True)
    SAIDA.mkdir(exist_ok=True)
    relatorio = {}

    t = time.time()
    video = baixar(args.fonte)
    total = duracao(video)
    relatorio["download_s"] = round(time.time() - t, 1)
    relatorio["duracao_bruto_s"] = round(total, 1)

    motor = args.motor
    if motor == "auto":
        motor = "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "whisper"
    t = time.time()
    audio = extrair_audio(video)
    if motor == "elevenlabs":
        palavras = transcrever_elevenlabs(audio, args.idioma)
    else:
        palavras = transcrever_whisper(audio, args.modelo, args.idioma)
    tempo_transcricao = time.time() - t
    relatorio["motor"] = motor if motor == "elevenlabs" else f"whisper-{args.modelo}"
    relatorio["transcricao_s"] = round(tempo_transcricao, 1)
    relatorio["transcricao_x_tempo_real"] = round(tempo_transcricao / total, 2)
    (TRABALHO / "transcricao.json").write_text(json.dumps(palavras, ensure_ascii=False, indent=1),
                                              encoding="utf-8")

    t = time.time()
    trechos = montar_trechos(palavras, args.pausa, total)
    destino = SAIDA / f"{Path(video).stem}_editado.mp4"
    renderizar(video, trechos, destino)
    relatorio["render_s"] = round(time.time() - t, 1)
    relatorio["duracao_editado_s"] = round(sum(b - a for a, b in trechos), 1)
    relatorio["arquivo"] = str(destino.relative_to(RAIZ))
    relatorio["tamanho_mb"] = round(destino.stat().st_size / 1e6, 1)

    link = None if args.sem_link else enviar_link(destino)
    relatorio["link"] = link or "não gerado"

    (SAIDA / "relatorio.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=1),
                                          encoding="utf-8")
    print(json.dumps(relatorio, ensure_ascii=False, indent=1))
    if not link:
        print("SEM LINK: o arquivo ficou em", relatorio["arquivo"])


if __name__ == "__main__":
    main()
