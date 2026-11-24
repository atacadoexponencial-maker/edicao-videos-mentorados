"""Traz os brutos de um vídeo para <projeto>/brutos (nome sem acento; pula o que já existe).

A origem pode ser:
- o nome da pasta dentro de "1. Para editar" (ex.: "Lousa 1");
- o caminho de uma pasta ou de um arquivo no computador;
- um link do Google Drive (pasta ou arquivo compartilhado como "qualquer pessoa com o link"), YouTube ou .mp4.

Uso: python baixar.py <projeto> <origem>
Imprime a lista de arquivos com duração e resolução.
"""
import re, shutil, subprocess, sys, tempfile, unicodedata
from pathlib import Path
from comum import projeto, run, VIDEO_EXT, PARA_EDITAR
from pasta import pasta_do_aluno


def limpo(nome):
    n = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "_", n).strip("_") or "video"


def info(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data:format=duration", "-of", "json", str(f)],
                       capture_output=True, text=True)
    import json
    try:
        d = json.loads(r.stdout); s = d["streams"][0]
        w, h = s["width"], s["height"]
        rot = abs(int(float(next((x["rotation"] for x in s.get("side_data_list", []) if "rotation" in x), 0))))
        if rot in (90, 270): w, h = h, w
        return f"{w}x{h} {float(d['format']['duration']):.0f}s"
    except Exception:
        return "(não consegui ler o vídeo)"


def de_link(link, destino):
    destino.mkdir(parents=True, exist_ok=True)
    if "drive.google.com" in link:
        import gdown
        if "/folders/" in link:
            ok = gdown.download_folder(link, output=str(destino), quiet=True)
        else:
            ok = gdown.download(link, output=str(destino) + "/", fuzzy=True, quiet=True)
        if not ok:
            sys.exit("Não consegui baixar do Drive. O link precisa estar como 'qualquer pessoa com o link'.")
    elif re.search(r"\.(mp4|mov|m4v|webm)(\?|$)", link, re.I):
        import requests
        nome = limpo(Path(link.split("?")[0]).stem) + Path(link.split("?")[0]).suffix
        with requests.get(link, stream=True, timeout=60) as r, open(destino / nome, "wb") as fh:
            r.raise_for_status()
            for bloco in r.iter_content(1 << 20): fh.write(bloco)
    else:
        run([sys.executable, "-m", "yt_dlp", "-q", "-f", "bv*+ba/b", "--merge-output-format", "mp4",
             "-o", str(destino / "%(title).60s.%(ext)s"), link])
    return destino


proj, origem = projeto(sys.argv[1]), sys.argv[2]
if origem.startswith("http"):
    pasta = de_link(origem, Path(tempfile.mkdtemp(prefix="brutos_")))
else:
    pasta = Path(origem).expanduser()
    if not pasta.exists():
        pasta = pasta_do_aluno() / PARA_EDITAR / origem
    if not pasta.exists():
        sys.exit(f"Não achei '{origem}' em {pasta_do_aluno() / PARA_EDITAR}")
arquivos = [pasta] if pasta.is_file() else sorted(f for f in pasta.rglob("*") if f.suffix.lower() in VIDEO_EXT)
if not arquivos:
    sys.exit(f"Nenhum vídeo em {pasta} (se acabou de subir no Drive, espere sincronizar)")
for f in arquivos:
    dst = proj / "brutos" / f"{limpo(f.stem)}{f.suffix.lower()}"
    if dst.exists() and dst.stat().st_size == f.stat().st_size:
        print("já copiado", dst.name, info(dst)); continue
    shutil.copy2(f, dst)
    print("copiado", dst.name, info(dst), flush=True)
(proj / "edit" / "origem.txt").write_text(str(pasta), encoding="utf-8")
