"""Acha repetições que a transcrição escondeu. A AssemblyAI (usada até 10/10/2026) juntava falas repetidas numa
palavra só, esticada no tempo ("esse tipo de, esse tipo de, esse tipo de conteúdo" virava um "conteúdo" de 1,5 s).
O Whisper também pode esconder repetição: esta busca é a rede de segurança.
Sinal: palavra com silêncio dentro ou com mais de 1,1 s. Cada ponto suspeito é retranscrito isolado
(trecho curto sai fiel) e o texto real é impresso para decidir o corte.

Uso: python repeticoes.py <projeto> ["Nome do conteúdo" ...]
"""
import subprocess, sys
from comum import projeto, fonte, palavras, silencios, transcrever, config, conteudos

proj = projeto(sys.argv[1]); cfg = config(proj)
snip = proj / "edit" / "snip"
for nome in conteudos(cfg, sys.argv[2:]):
    c = cfg[nome]
    for src, a, b in [r for h in c["hooks"].values() for r in h] + c["body"] + [r for rs in (c.get("ctas") or {}).values() for r in rs]:
        sil = silencios(proj, src, minimo=0.2)
        for w in [w for w in palavras(proj, src) if a - 0.02 <= w["start"] < b]:
            dentro = [s for s in sil if s[0] > w["start"] + 0.05 and s[1] < w["end"] - 0.05]
            if not dentro and w["end"] - w["start"] < 1.1: continue
            x0, x1 = max(0, w["start"] - 1.5), w["end"] + 1.5
            wav = snip / f"{src}_{x0:.1f}.wav"; snip.mkdir(exist_ok=True)
            if not wav.exists():
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{x0:.2f}", "-t", f"{x1 - x0:.2f}", "-i",
                                str(fonte(proj, src)), "-vn", "-ac", "1", "-ar", "16000", str(wav)])
            t = transcrever(wav, snip / "transcripts" / f"{wav.stem}.json")
            real = " ".join(f"{v['text']}[{x0 + v['start']:.2f}]" for v in t["words"])
            print(f"{nome} | {src} | '{w['text']}' {w['start']:.2f}-{w['end']:.2f} (trecho {a}-{b})\n   real: {real}", flush=True)
print("fim da busca")
