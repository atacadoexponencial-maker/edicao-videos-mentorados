"""Depois da entrega: apaga o que pesa no projeto (brutos, pedaços renderizados, cortes de áudio, quadros) e
mantém reels.json, transcrições, notas e os finais. Na nuvem o disco é pequeno (~30 GB): rodar sempre.

Uso: python limpar.py <projeto> [--tudo]   (--tudo apaga também os vídeos finais)
"""
import shutil, sys
from comum import projeto

proj = projeto(sys.argv[1])
alvos = [proj / "brutos", proj / "edit" / "segs", proj / "edit" / "snip", proj / "edit" / "verify" / "tmp_quadros", proj / "edit" / "work"]
if "--tudo" in sys.argv:
    alvos.append(proj / "final")
livre = 0
for a in alvos:
    if a.exists():
        livre += sum(f.stat().st_size for f in a.rglob("*") if f.is_file())
        shutil.rmtree(a)
print(f"liberado {livre / 1e6:.0f} MB em {proj.name}")
