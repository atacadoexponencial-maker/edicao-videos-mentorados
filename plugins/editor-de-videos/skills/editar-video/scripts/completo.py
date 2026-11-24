"""Reels COMPLETO (padrão de Reels que mais performam), feito em cima do simples já aprovado:
1,15x, zoom alternado só na troca de trecho (tomada), caixa branca no topo nos primeiros segundos, legenda branca
minúscula de 2 a 4 palavras no peito, imagens de prova e CTA em caixa quando configurados. Spec em
references/formato-completo.md.

A legenda vem da retranscrição do vídeo simples (edit/check/transcripts, criada pelo conferir.py): é o áudio real.

Uso:
  python completo.py <projeto> "<Conteúdo>" "<Hook>" [cta=Ad] --previa   -> legenda e topo para aprovar
  python completo.py <projeto> "<Conteúdo>" "<Hook>" [cta=Ad]            -> final/<nome> - completo.mp4

Campos no reels.json (no conteúdo):
  "topo": ["linha 1", "linha 2"]                 obrigatório (aprovado pela pessoa)
  "topo_seg": 4                                  opcional, segundos na tela (4 a 8)
  "legenda_corrige": {"palavra errada": "palavra certa"}   opcional, correções da legenda (minúsculas)
  "provas": [{"arquivo": "provas/nota.png", "de": 1.0, "ate": 5.5}]  opcional, tempos do vídeo SIMPLES
  "cta_caixa": "ESCREVA ANÁLISE NOS COMENTÁRIOS"  opcional, aparece durante a CTA
"""
import hashlib, json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from comum import projeto, fonte, run, config, nome_saida, duracao
from cortes import linha_do_tempo
from takes import aplicar_takes

VEL = 1.15                      # 1,25x ficou "rápido demais"
W, H = 1080, 1920
ZOOMS = [1.0, 1.12]
TOPO_Y, TOPO_PX = 345, 46
LEG_Y, LEG_Y_PROVA, LEG_PX = 1490, 1150, 66
CTA_Y, CTA_PX = 1180, 44
PROVA_LARG, PROVA_BASE = 640, 1860
ASSETS = Path(__file__).resolve().parents[1] / "assets"
F700 = str(ASSETS / "intertight700.ttf")

args = [a for a in sys.argv[1:] if not a.startswith("--")]
proj, CONTEUDO, HOOK = projeto(args[0]), args[1], args[2]
CTA = next((a[4:] for a in args[3:] if a.startswith("cta=")), "Conteúdo")
PREVIA = "--previa" in sys.argv
c = config(proj)[CONTEUDO]
if not c.get("topo"):
    sys.exit('Falta "topo" no reels.json (frase da caixa branca, 2 linhas). Proponha 2 ou 3 frases e peça a escolha.')
ctas = c.get("ctas") or {None: []}
if CTA not in ctas and None not in ctas:
    sys.exit(f"CTA '{CTA}' não existe neste conteúdo: {list(ctas)}")
nome = nome_saida(CONTEUDO, HOOK, c, CTA if CTA in ctas else None, len(ctas))
WORK = proj / "edit" / "completo"; WORK.mkdir(parents=True, exist_ok=True)
tag = re.sub(r"\W+", "_", nome)


# ---------- vídeo base: mesmos cortes do simples, 1,15x, zoom alternado por trecho ----------
def peca(src, a, b, z):
    out = WORK / (hashlib.md5(f"{src}|{a:.3f}|{b:.3f}|{z}|{VEL}".encode()).hexdigest()[:12] + ".mp4")
    if out.exists(): return out
    sw, sh = int(W * z) // 2 * 2, int(H * z) // 2 * 2
    x, y = (sw - W) // 2, int((sh - H) * 0.35)
    d = (b - a) / VEL
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", str(fonte(proj, src)),
         "-vf", f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={W}:{H}:{x}:{y},setsar=1,setpts=(PTS-STARTPTS)/{VEL},fps=30",
         "-af", f"asetpts=PTS-STARTPTS,atempo={VEL},afade=t=in:st=0:d=0.03,afade=t=out:st={max(0, d - 0.03):.3f}:d=0.03,aresample=48000",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", str(out.with_suffix(".tmp.mp4"))])
    out.with_suffix(".tmp.mp4").replace(out)   # render interrompido não deixa trecho quebrado no cache
    return out


pecas = linha_do_tempo(proj, c, HOOK, ctas.get(CTA, []) if CTA in ctas else [])
t_simples, ini_cta, zi, chave_ant = 0.0, None, -1, None   # tempos do vídeo simples (com a velocidade dele)
for idx, papel, s, x, y, v in pecas:
    if (papel, idx) != chave_ant: zi += 1; chave_ant = (papel, idx)
    if papel == "cta" and ini_cta is None: ini_cta = t_simples
    t_simples += (y - x) / v
fator = sum((y - x) / v for *_, x, y, v in pecas) / sum((y - x) / VEL for *_, x, y, v in pecas)   # simples -> completo


# ---------- legenda ----------
def espalha(ws):
    """A transcrição às vezes espreme várias palavras (< 0,06 s cada) e deixa um buraco até a próxima.
    O áudio é contínuo: redistribui o grupo até a próxima palavra, proporcional ao tamanho de cada uma."""
    ws = list(ws); i = 0
    while i < len(ws):
        j = i
        while j < len(ws) and ws[j][2] - ws[j][1] < 0.06: j += 1
        if j - i >= 3 and j < len(ws):
            i0 = i
            while i > max(0, i0 - 3) and ws[i][1] - ws[i - 1][1] < 0.35: i -= 1
            a, b = ws[i][1], ws[j][1] - 0.08
            pesos = [len(w[0]) + 1 for w in ws[i:j]]; t = a
            for k, p in zip(range(i, j), pesos):
                d = (b - a) * p / sum(pesos); ws[k] = (ws[k][0], t, t + d); t += d
        i = max(j, i + 1)
    return ws


def corrige(ws):
    """Tira palavra repetida colada (ruído) e aplica legenda_corrige (trechos em minúsculas)."""
    ws = espalha(ws)
    limpa = lambda t: t.lower().strip(".,?!:;")
    out = []
    for t, s, e in ws:
        if out and limpa(t) == limpa(out[-1][0]) and limpa(t) not in ("a", "o"):
            continue
        out.append((t, s, e))
    for errado, certo in (c.get("legenda_corrige") or {}).items():
        de, para = errado.lower().split(), certo.split()
        i = 0
        while i <= len(out) - len(de):
            if [limpa(w[0]) for w in out[i:i + len(de)]] == de:
                s, e = out[i][1], out[i + len(de) - 1][2]; passo = (e - s) / len(para)
                pont = re.search(r"[.,?!:;]+$", out[i + len(de) - 1][0])
                novo = [(p, s + k * passo, s + (k + 1) * passo) for k, p in enumerate(para)]
                if pont: novo[-1] = (novo[-1][0] + pont.group(), *novo[-1][1:])
                out[i:i + len(de)] = novo; i += len(para)
            else:
                i += 1
    return out


def grupos(ws, max_words=4, max_chars=22):
    out, cur = [], []
    for w in ws:
        if cur and len(" ".join(x[0] for x in cur + [w])) > max_chars:
            out.append(cur); cur = []
        cur.append(w)
        if w[0][-1] in ".,?!:" or len(cur) >= max_words:
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out


def png_legenda(txt, y, arq):
    f = ImageFont.truetype(F700, LEG_PX)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.text(((W - d.textlength(txt, font=f)) / 2, y - LEG_PX // 2), txt, font=f, fill="white", stroke_width=3, stroke_fill=(0, 0, 0, 170))
    sh = img.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.55))
    bg = Image.new("RGBA", img.size, (0, 0, 0, 0)); bg.putalpha(sh)
    Image.alpha_composite(bg, img).save(arq)


def png_caixa(linhas, px, arq):
    """Caixa branca arredondada com texto preto negrito centralizado (topo e CTA)."""
    f = ImageFont.truetype(F700, px)
    lh, padx, pady = int(px * 1.2), 28, 16
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    bw = int(max(tmp.textlength(l, font=f) for l in linhas)) + 2 * padx
    bh = lh * len(linhas) + 2 * pady
    img = Image.new("RGBA", (W, bh + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x0 = (W - bw) // 2
    d.rounded_rectangle((x0, 20, x0 + bw, 20 + bh), radius=18, fill="white")
    for i, l in enumerate(linhas):
        d.text(((W - d.textlength(l, font=f)) / 2, 20 + pady + i * lh), l, font=f, fill="black")
    img.save(arq)
    return bh + 40


def quebra(txt, px, larg=900):
    f = ImageFont.truetype(F700, px); d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    linhas, cur = [], ""
    for p in txt.split():
        if cur and d.textlength(cur + " " + p, font=f) > larg:
            linhas.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    return linhas + ([cur] if cur else [])


chk = proj / "edit" / "check" / "transcripts" / f"{nome}.json"
simples = proj / "final" / f"{nome}.mp4"
if not chk.exists() or (simples.exists() and chk.stat().st_mtime < simples.stat().st_mtime):
    sys.exit(f"Falta a retranscrição do vídeo simples '{nome}'. Rode conferir.py no projeto antes do completo.")
tr = json.loads(chk.read_text(encoding="utf-8"))["words"]
u = 1000 if tr and tr[-1]["end"] > 5000 else 1                                  # transcrições antigas em ms
tr = [dict(w, start=w["start"] / u, end=w["end"] / u) for w in tr]
ws = corrige([(w["text"], w["start"] / fator, w["end"] / fator) for w in tr])   # tempos do completo
provas = [dict(p, de_c=p["de"] / fator, ate_c=p["ate"] / fator) for p in c.get("provas") or []]
gs = grupos(ws)
textos = [(re.sub(r"[.,!?:;]+$", "", " ".join(x[0] for x in g)).lower(), g[0][1], g[-1][2]) for g in gs]

topo_seg = float(c.get("topo_seg", 4))
topo_png = WORK / "topo.png"; png_caixa(c["topo"], TOPO_PX, topo_png)
if PREVIA:
    leg = proj / "final" / f"{nome} - legenda.txt"
    leg.write_text("\n".join(f"{s:6.2f}  {t}" for t, s, e in textos), encoding="utf-8")
    print(f"Topo ({topo_seg:.0f}s): {' / '.join(c['topo'])}  -> imagem {topo_png}")
    print(f"Legenda para aprovar: {leg} ({len(textos)} blocos). Correções vão em \"legenda_corrige\" no reels.json.")
    sys.exit(0)

# ---------- render ----------
clips, zi, chave_ant, dur = [], -1, None, 0.0
for idx, papel, s, x, y, v in pecas:
    if (papel, idx) != chave_ant: zi += 1; chave_ant = (papel, idx)
    clips.append(peca(s, x, y, ZOOMS[zi % 2])); dur += (y - x) / VEL
(WORK / f"{tag}_list.txt").write_text("".join(f"file '{p.as_posix()}'\n" for p in clips), encoding="utf-8")
base = WORK / f"{tag}_base.mp4"
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(WORK / f"{tag}_list.txt"), "-c", "copy", str(base)])
if c.get("takes"):                       # takes de apoio por cima, antes de topo e legenda
    aplicar_takes(proj, c, [(i, p, src, x, y, VEL) for i, p, src, x, y, _ in pecas], base)

blank = WORK / "vazio.png"; Image.new("RGBA", (W, H), (0, 0, 0, 0)).save(blank)
linhas, cur = ["ffconcat version 1.0"], 0.0
for n, (txt, s, e) in enumerate(textos):
    s = max(s, cur); e = max(e, s + 0.25)
    if s > cur + 0.01: linhas += [f"file '{blank.as_posix()}'", f"duration {s - cur:.3f}"]
    y = LEG_Y_PROVA if any(p["de_c"] - 0.2 <= s <= p["ate_c"] for p in provas) else LEG_Y
    p = WORK / f"{tag}_leg{n:03d}.png"; png_legenda(txt, y, p)
    linhas += [f"file '{p.as_posix()}'", f"duration {e - s:.3f}"]; cur = e
if cur < dur: linhas += [f"file '{blank.as_posix()}'", f"duration {dur - cur:.3f}"]
linhas.append(f"file '{blank.as_posix()}'")
(WORK / f"{tag}_leg.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")

entradas = ["-i", str(base), "-loop", "1", "-t", f"{dur:.3f}", "-i", str(topo_png),
            "-f", "concat", "-safe", "0", "-i", str(WORK / f"{tag}_leg.txt")]
filtro = [f"[1:v]format=rgba,fade=t=out:st={topo_seg - 0.4}:d=0.4:alpha=1[t]",
          f"[0:v][t]overlay=0:{TOPO_Y - 20}:shortest=1[v0]",
          "[2:v]fps=30,format=rgba[l]", "[v0][l]overlay=0:0:eof_action=pass[v1]"]
ult, k = "v1", 3
for p in provas:
    arq = (proj / p["arquivo"]) if not Path(p["arquivo"]).is_absolute() else Path(p["arquivo"])
    if not arq.exists(): sys.exit(f"Imagem de prova não encontrada: {arq}")
    entradas += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(arq)]
    filtro += [f"[{k}:v]scale={PROVA_LARG}:-2,format=rgba[p{k}]",
               f"[{ult}][p{k}]overlay=(W-w)/2:{PROVA_BASE}-h:enable='between(t,{p['de_c']:.2f},{p['ate_c']:.2f})'[v{k}]"]
    ult, k = f"v{k}", k + 1
if c.get("cta_caixa") and ini_cta is not None:
    cta_png = WORK / f"{tag}_cta.png"; png_caixa(quebra(c["cta_caixa"], CTA_PX), CTA_PX, cta_png)
    entradas += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(cta_png)]
    filtro += [f"[{ult}][{k}:v]overlay=0:{CTA_Y}:enable='gte(t,{ini_cta / fator:.2f})'[v{k}]"]
    ult, k = f"v{k}", k + 1
filtro += [f"[{ult}]tpad=stop_mode=clone:stop_duration=0.5,format=yuv420p[v]",
           "[0:a]apad=pad_dur=0.5,loudnorm=I=-14:TP=-1.5:LRA=11[a]"]
saida = proj / "final" / f"{nome} - completo.mp4"
run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtro),
     "-map", "[v]", "-map", "[a]", "-ar", "48000", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{dur + 0.5:.3f}", str(saida)])
print(f"pronto: {saida.name} ({duracao(saida):.1f}s, {len(clips)} cortes, {len(textos)} blocos de legenda, "
      f"{len(provas)} prova(s){', CTA em caixa' if c.get('cta_caixa') else ''})", flush=True)
