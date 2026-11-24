"""Transcreve todos os brutos (Whisper grátis no computador, ou ElevenLabs se houver chave; com cache), gera edit/takes.md (frases com
[início-fim] por arquivo) e avisa quando os tempos da transcrição derivam do áudio.

Uso: python transcrever.py <projeto>
"""
import sys
from concurrent.futures import ThreadPoolExecutor
from comum import projeto, transcrever, palavras, deriva, env, VIDEO_EXT

proj = projeto(sys.argv[1])
brutos = sorted(f for f in (proj / "brutos").iterdir() if f.suffix.lower() in VIDEO_EXT)
tarefa = lambda f: (print(f"transcrevendo {f.name}...", flush=True), transcrever(f, proj / "edit" / "transcripts" / f"{f.stem}.json"))
if env("ELEVENLABS"):
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(tarefa, brutos))
else:
    for f in brutos:                      # Whisper usa o processador inteiro: um arquivo por vez
        tarefa(f)

linhas = ["# Tomadas (frases quebradas em silêncio >= 0,5 s)\n"]
for f in brutos:
    ws = palavras(proj, f.stem)
    linhas.append(f"\n## {f.stem}")
    frase = []
    for i, w in enumerate(ws):
        frase.append(w)
        fim = i == len(ws) - 1 or ws[i + 1]["start"] - w["end"] >= 0.5
        if fim:
            linhas.append(f"  [{frase[0]['start']:07.2f}-{frase[-1]['end']:07.2f}] " + " ".join(x["text"] for x in frase))
            frase = []
    d = deriva(proj, f.stem)
    if d and abs(d[1]) > 0.3:
        print(f"AVISO deriva: {f.stem}, perto de {d[0]:.0f}s os tempos estão {d[1]:+.2f}s fora do som (mediana de {d[2]} palavras). "
              "Antes de cortar na segunda metade do arquivo, retranscrever o trecho usado isolado (como o repeticoes.py faz).")
(proj / "edit" / "takes.md").write_text("\n".join(linhas), encoding="utf-8")
print(f"{len(brutos)} brutos transcritos -> {proj / 'edit' / 'takes.md'}")
