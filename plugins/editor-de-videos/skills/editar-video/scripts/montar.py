"""Monta os vídeos simples do edit/reels.json: um vídeo por hook (hook + corpo + CTA), 9:16 1080x1920, sem legenda.
Se o conteúdo tiver "takes", as imagens de apoio entram por cima da fala (a voz continua por baixo), ver takes.py.

Uso: python montar.py <projeto> ["Nome do conteúdo" ...]   (sem nomes = todos)

O que já é resolvido sozinho (não compensar nos tempos do reels.json), ver cortes.py:
- snap no silêncio real, pausas >= 0,15 s cortadas (cortes justos, sem respiro entre frases), respiro de 0,6 s no fim;
- dois trechos seguidos do mesmo bruto não se sobrepõem (sem palavra duplicada na emenda);
- velocidade do hook igualada ao ritmo do corpo, entre 1x e a velocidade do vídeo;
- fade de 30 ms em cada emenda (sem estalo).
"""
import hashlib, sys
from comum import projeto, fonte, run, config, conteudos, nome_saida, duracao
from cortes import linha_do_tempo
from takes import aplicar_takes

VELOCIDADE = 1.0                  # padrão 1x (não acelerar hook, corpo nem CTA); "speed" no conteúdo sobrescreve

proj = projeto(sys.argv[1])
SEG = proj / "edit" / "segs"; SEG.mkdir(exist_ok=True)


def render(src, a, b, vel):
    out = SEG / (hashlib.md5(f"{src}|{a:.3f}|{b:.3f}|{vel}".encode()).hexdigest()[:12] + ".mp4")
    if out.exists(): return out
    d = (b - a) / vel
    tmp = out.with_suffix(".tmp.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(fonte(proj, src)),
         "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,setpts=(PTS-STARTPTS)/{vel},fps=30",
         "-af", f"asetpts=PTS-STARTPTS,atempo={vel},afade=t=in:st=0:d=0.03,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03,aresample=48000",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart", str(tmp)])
    tmp.replace(out)              # render interrompido não deixa pedaço quebrado no cache
    return out


cfg = config(proj)
for nome in conteudos(cfg, sys.argv[2:]):
    c = cfg[nome]
    ctas = c.get("ctas") or {None: []}
    for hook in c["hooks"]:
        for nome_cta, ranges_cta in ctas.items():
            pecas = linha_do_tempo(proj, c, hook, ranges_cta, VELOCIDADE)
            segs = [render(s, x, y, v) for _, _, s, x, y, v in pecas]
            lst = SEG / "list.txt"
            lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in segs), encoding="utf-8")
            final = proj / "final" / f"{nome_saida(nome, hook, c, nome_cta, len(ctas))}.mp4"
            montado = final.with_name(final.stem + ".montado.mp4")
            run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", "-movflags", "+faststart", str(montado)])
            # O bruto pode emendar a CTA seguinte sem silêncio. Fecha com 0,6 s de quadro congelado e áudio mudo.
            run(["ffmpeg", "-v", "error", "-y", "-i", str(montado), "-filter_complex",
                 "[0:v]tpad=stop_mode=clone:stop_duration=0.6[v];[0:a]apad=pad_dur=0.6[a]",
                 "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])
            montado.unlink(missing_ok=True)
            if c.get("takes"):
                aplicar_takes(proj, c, pecas, final)
            hv = next((v for _, p, *_, v in pecas if p == "hook"), 1.0)
            print(f"{final.name}: {duracao(final):.1f}s (hook {hv}x, corpo {c.get('speed', VELOCIDADE)}x)", flush=True)
