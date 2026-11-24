"""Volume do áudio a cada 25 ms num intervalo do bruto. Mostra onde uma palavra termina de verdade
(a transcrição erra até ~0,4 s). Valores perto de 0 = silêncio.

Uso: python energia.py <projeto> <bruto> <inicio> <duracao>
"""
import struct, subprocess, sys
from comum import projeto, fonte

proj, stem, t0, dur = projeto(sys.argv[1]), sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t0}", "-t", f"{dur}", "-i", str(fonte(proj, stem)),
                      "-vn", "-ac", "1", "-ar", "1000", "-f", "s16le", "-"], capture_output=True).stdout
a = struct.unpack(f"<{len(raw) // 2}h", raw)
print(" ".join(f"{t0 + i / 1000:.2f}:{max(abs(x) for x in a[i:i + 25]) // 100}" for i in range(0, len(a), 25)))
