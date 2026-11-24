"""Grade de quadros de um take de apoio (um quadro a cada segundo, com o tempo), para escolher o trecho bonito.

Uso: python quadros_take.py <projeto> <bruto do take>   -> edit/verify/take_<nome>.jpg (abrir com Read)
"""
import subprocess, sys
from PIL import Image, ImageDraw
from comum import projeto, fonte, duracao

proj, stem = projeto(sys.argv[1]), sys.argv[2]
src = fonte(proj, stem); dur = duracao(src)
tmp = proj / "edit" / "verify" / "tmp_take"; tmp.mkdir(parents=True, exist_ok=True)
quadros, t = [], 0.3
while t < dur and len(quadros) < 40:
    out = tmp / f"{len(quadros):03d}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(src), "-frames:v", "1",
                    "-vf", "scale=-2:320", str(out)])
    if out.exists():
        im = Image.open(out).convert("RGB"); ImageDraw.Draw(im).text((6, 6), f"{t:.1f}s", fill="yellow")
        quadros.append(im)
    t += max(1.0, dur / 40)
if not quadros:
    sys.exit("Não consegui tirar quadros do take")
w, h = quadros[0].size; cols = 8
grade = Image.new("RGB", (w * cols, h * ((len(quadros) + cols - 1) // cols)))
for i, im in enumerate(quadros):
    grade.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
dst = proj / "edit" / "verify" / f"take_{stem}.jpg"; grade.save(dst, quality=80)
print(dst)
