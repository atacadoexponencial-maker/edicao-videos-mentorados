"""Mostra palavra a palavra com tempos e as pausas (|0.50|) de um trecho do bruto. Base para escolher cortes.

Uso: python palavras.py <projeto> <bruto> [inicio] [fim]
"""
import sys
from comum import projeto, palavras

proj, stem = projeto(sys.argv[1]), sys.argv[2]
a = float(sys.argv[3]) if len(sys.argv) > 3 else 0
b = float(sys.argv[4]) if len(sys.argv) > 4 else 1e9
out, prev = [], None
for w in palavras(proj, stem):
    if not a <= w["start"] <= b: continue
    if prev is not None and w["start"] - prev > 0.35:
        out.append(f"|{w['start'] - prev:.2f}|")
    longa = " <LONGA>" if w["end"] - w["start"] > 1.0 else ""
    out.append(f"{w['text']}[{w['start']:.2f}-{w['end']:.2f}]{longa}")
    prev = w["end"]
print(" ".join(out))
