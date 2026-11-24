"""Traduz tempos do vídeo EDITADO (o que o time vê) para o bruto, para aplicar uma lista de ajustes de uma vez.
Para cada tempo mostra: qual trecho do reels.json (papel e posição), o tempo no bruto e as palavras em volta.

Uso: python mapa.py <projeto> "<Conteúdo>" "<Hook>" [cta=Ad] [--completo] 0:23 41.5 1:02
     --completo: os tempos são do vídeo completo (1,15x), não do simples.

Depois: editar os trechos no reels.json (por Python), montar.py uma vez só, conferir.py, e o completo se for o caso.
"""
import sys
from comum import projeto, config, palavras
from cortes import linha_do_tempo

VEL_COMPLETO = 1.15


def segundos(t):
    if ":" in t:
        m, s = t.split(":"); return int(m) * 60 + float(s)
    return float(t)


args = [a for a in sys.argv[1:] if not a.startswith("--")]
proj, nome, hook = projeto(args[0]), args[1], args[2]
cta = next((a[4:] for a in args[3:] if a.startswith("cta=")), "Conteúdo")
tempos = [segundos(a) for a in args[3:] if not a.startswith("cta=")]
c = config(proj)[nome]
ctas = c.get("ctas") or {}
pecas = linha_do_tempo(proj, c, hook, ctas.get(cta, []))
completo = "--completo" in sys.argv
print(f"Mapa de '{nome} - {hook}' (CTA {cta}{', tempos do completo' if completo else ''}); reflete o reels.json atual.")

for alvo in tempos:
    t, achou = 0.0, False
    for idx, papel, s, x, y, v in pecas:
        d = (y - x) / (VEL_COMPLETO if completo else v)
        if t <= alvo < t + d:
            no_bruto = x + (alvo - t) * (y - x) / d
            ws = palavras(proj, s)
            perto = [w for w in ws if no_bruto - 2.5 <= w["start"] <= no_bruto + 2.5]
            marca = next((w for w in perto if w["end"] > no_bruto), None)      # palavra que está tocando naquele instante
            txt = " ".join(("»" if w is marca else "") + f"{w['text']}[{w['start']:.2f}]" for w in perto)
            print(f"\n{int(alvo // 60)}:{alvo % 60:05.2f} -> {papel} nº {idx + 1} do reels.json, bruto {s} em {no_bruto:.2f}s "
                  f"(pedaço {x:.2f}-{y:.2f})\n   {txt}")
            achou = True
            break
        t += d
    if not achou:
        print(f"\n{int(alvo // 60)}:{alvo % 60:05.2f} -> depois do fim do vídeo ({t:.1f}s)")
