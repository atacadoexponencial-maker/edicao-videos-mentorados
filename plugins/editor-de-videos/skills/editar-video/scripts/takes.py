"""Takes de apoio (B-roll): imagens que entram por cima da fala, com a voz continuando por baixo.

No reels.json, dentro do conteúdo:
  "takes": [
    {"take": "TAKE_palestra", "de": 4.5, "dur": 3.0, "em": ["LOUSA_1", 95.2]},
    {"take": "TAKE_palestra", "de": 9.0, "dur": 2.5, "no_video": 41.0}
  ]
- take: o bruto do take (nome sem extensão, em brutos/);
- de: segundo do take onde a imagem começa (escolha um trecho bonito, sem tremida; veja com quadros_take.py);
- dur: quanto tempo fica na tela (2 a 4 s funciona bem);
- em: [bruto da fala, segundo no bruto] = entra quando aquela palavra é dita (preferível: vale para todos os hooks);
  ou no_video: segundo do vídeo final (vale só se houver um hook).
O som do take é ignorado. O take é recortado para 9:16 preenchendo a tela (sem tarja preta).
Escolha momentos em que a fala combina com a imagem e evite cobrir o hook (primeiros segundos) e a CTA.

Usado pelo montar.py; não precisa rodar sozinho.
"""
from comum import fonte, run


def tempo_no_final(pecas, src, t):
    """Converte um tempo do bruto da fala para o tempo no vídeo final, pela linha do tempo do montar.py."""
    acc = 0.0
    for _, _, s, x, y, v in pecas:
        if s == src and x - 0.05 <= t <= y + 0.05:
            return acc + max(0.0, t - x) / v
        acc += (y - x) / v
    return None


def aplicar_takes(proj, c, pecas, final):
    janelas = []
    for k in c["takes"]:
        t = k["no_video"] if "no_video" in k else tempo_no_final(pecas, *k["em"])
        if t is None:
            print(f"  AVISO take {k['take']} @ {k.get('em')}: esse momento foi cortado do vídeo; take ignorado", flush=True)
            continue
        janelas.append((round(t, 3), k))
    if not janelas:
        return
    entradas, filtros, ultimo = ["-i", str(final)], [], "0:v"
    for i, (t, k) in enumerate(janelas, start=1):
        entradas += ["-ss", f"{k.get('de', 0):.3f}", "-t", f"{k.get('dur', 3):.3f}", "-i", str(fonte(proj, k["take"]))]
        filtros.append(f"[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
                       f"format=yuv420p,setpts=PTS-STARTPTS+{t}/TB[t{i}]")
        filtros.append(f"[{ultimo}][t{i}]overlay=0:0:eof_action=pass:enable='between(t,{t},{t + k.get('dur', 3):.3f})'[v{i}]")
        ultimo = f"v{i}"
    tmp = final.with_name(final.stem + ".takes.mp4")
    run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", f"[{ultimo}]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy",
         "-movflags", "+faststart", str(tmp)])
    tmp.replace(final)
    print(f"  {len(janelas)} take(s) de apoio em " + ", ".join(f"{t:.1f}s" for t, _ in janelas), flush=True)
