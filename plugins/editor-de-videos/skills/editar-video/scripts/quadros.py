"""Grade de quadros a cada 0,8 s de todos os trechos escolhidos de um conteúdo, com o número do trecho e o tempo.
Serve para achar o que só aparece na imagem: pessoa lendo o roteiro (olhar para baixo), saindo do quadro,
câmera mexendo, roupa/cenário diferente entre tomadas.

Uso: python quadros.py <projeto> "Nome do conteúdo"   -> edit/verify/quadros_<nome>_<n>.jpg (abrir com Read)
"""
import subprocess, sys
from PIL import Image, ImageDraw
from comum import projeto, fonte, config

proj = projeto(sys.argv[1]); nome = sys.argv[2]; c = config(proj)[nome]
tmp = proj / "edit" / "verify" / "tmp_quadros"; tmp.mkdir(parents=True, exist_ok=True)
for f in tmp.glob("*.jpg"): f.unlink()
itens = []
ranges = [(f"H:{h}", r) for h, rs in c["hooks"].items() for r in rs] + [(f"C{i}", r) for i, r in enumerate(c["body"])]     + [(f"CTA:{k}", r) for k, rs in (c.get("ctas") or {}).items() for r in rs]
for rot, (src, a, b) in ranges:
    t = a + 0.2
    while t < b:
        out = tmp / f"{len(itens):04d}.jpg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(fonte(proj, src)), "-frames:v", "1",
                        "-vf", "scale=120:-1", str(out)])
        if out.exists(): itens.append((out, f"{rot} {t:.1f}"))
        t += 0.8
cols, por_folha = 14, 112
for n in range(0, len(itens), por_folha):
    lote = itens[n:n + por_folha]
    w, h = Image.open(lote[0][0]).size
    g = Image.new("RGB", (w * cols, h * ((len(lote) + cols - 1) // cols)), "white")
    for k, (f, rot) in enumerate(lote):
        im = Image.open(f); ImageDraw.Draw(im).text((3, 3), rot, fill="yellow"); g.paste(im, ((k % cols) * w, (k // cols) * h))
    out = proj / "edit" / "verify" / f"quadros_{nome.replace(' ', '_')}_{n // por_folha}.jpg"
    g.save(out); print(out)
