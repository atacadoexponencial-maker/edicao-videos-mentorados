"""Onde cada trecho do reels.json começa e termina de verdade no bruto. Usado por montar.py, completo.py e mapa.py,
para os três cortarem exatamente igual.

- snap: a transcrição pode errar o fim/início das palavras; cada corte vai até o silêncio real, sem entrar na
  palavra vizinha;
- pausas >= 0,15 s dentro dos trechos são cortadas (fica 0,05 s de cada lado): frase emenda na outra, sem respiro
  (pedido do time, 26/10 e 09/11/2026). Silêncio medido a -35 dB: a -32 dB a fala baixa era comida (Depoimento, 26/10);
- dois trechos seguidos do mesmo bruto nunca se sobrepõem (o corte justo duplicou um "tá?" em 09/11);
- respiro de 0,6 s depois da última palavra do vídeo (terminar colado soa cortado nos players).
"""
from comum import palavras, silencios

PAD_IN, PAD_OUT = 0.05, 0.07
SIL_DB, SIL_MIN, KEEP, TAIL = -35, 0.15, 0.05, 0.6


def snap(proj, src, a, b):
    ws, sil = palavras(proj, src), silencios(proj, src, db=SIL_DB, minimo=SIL_MIN)
    nxt = min((w["start"] for w in ws if w["start"] >= b - 0.01), default=1e9)
    prv = max((w["end"] for w in ws if w["end"] <= a + 0.01), default=-1e9)
    s_after = [s for s, e in sil if b - 0.10 <= s <= b + 0.50 and s < nxt + 0.10]
    end = s_after[0] + KEEP if s_after else b + PAD_OUT
    e_before = [e for s, e in sil if a - 0.50 <= e <= a + 0.10 and e > prv - 0.10]
    start = e_before[-1] - KEEP if e_before else a - PAD_IN
    # nunca entrar na palavra vizinha (fala colada: o "F" de "Fato" vazou num corte, vídeo 6 momentos, 10/10/2026)
    end = min(end, max(b, nxt - 0.03))
    start = max(start, min(a, prv + 0.03))
    return max(0, start), end


def sem_pausas(proj, src, a, b):
    parts, cur = [], a
    for s, e in silencios(proj, src, db=SIL_DB, minimo=SIL_MIN):
        if e <= cur or s >= b: continue
        s2, e2 = max(s, cur), min(e, b)
        if e2 - s2 < SIL_MIN: continue
        if s2 + KEEP > cur: parts.append((cur, s2 + KEEP))
        cur = max(cur, e2 - KEEP)
    if b > cur: parts.append((cur, b))
    return [(x, y) for x, y in parts if y - x >= 0.10]


def trechos(proj, src, a, b, respiro=False):
    a, b = snap(proj, src, a, b)
    parts = sem_pausas(proj, src, a, b)
    if respiro:
        nxt = min((w["start"] for w in palavras(proj, src) if w["start"] >= b - 0.05), default=1e9)
        end = min(b + TAIL, nxt - 0.05)
        parts = parts[:-1] + [(parts[-1][0], max(parts[-1][1], end))] if parts else [(a, end)]
    return parts


def _quieto(sil, t, lado):
    """Quanto silêncio encosta no ponto t, para trás (lado=-1) ou para frente (+1). Junta só runs colados
    (< 0,02 s): juntar buracos maiores atravessa consoante e fala baixa."""
    fim = t
    for s, e in (reversed(sil) if lado < 0 else sil):
        if lado < 0 and s <= fim + 0.01 and e >= fim - 0.02:
            fim = min(fim, s)
        elif lado > 0 and s <= fim + 0.02 and e >= fim - 0.01:
            fim = max(fim, e)
    return abs(fim - t)


def apertar_emendas(proj, src, pecas, alvo=0.40, limite=0.62, secao=0.80, abre_secao=("momento",)):
    """Na emenda entre dois pedaços cada lado guarda a própria folga e a soma vira respiro sobrando (feedback do
    chefe na v2 do YouTube 6 momentos, 14/10/2026: 0,66 a 0,98 s em emendas, ele deixou ~0,35-0,40 s;
    limite 0,62 pega os 4 pontos dele e tira ~10 s em 36 min).
    Silêncio total na emenda > limite cai para alvo; se o pedaço seguinte abre seção (primeira palavra em
    abre_secao), o alvo é secao. Pausas dentro da tomada não mudam. pecas = [(i, x, y)] em ordem; devolve igual."""
    sil = silencios(proj, src, db=-30, minimo=0.05)
    ws = palavras(proj, src)
    out = [list(p) for p in pecas]
    for k in range(len(out) - 1):
        y, x2 = out[k][2], out[k + 1][1]
        cauda, cabeca = _quieto(sil, y, -1), _quieto(sil, x2, +1)
        prim = next((w for w in ws if w["start"] >= x2 - 0.02), None)
        ult = max((w["end"] for w in ws if w["end"] <= y + 0.02), default=y)
        meta = secao if prim and prim["text"].lower().strip(".,!?") in abre_secao else alvo
        if cauda + cabeca <= max(limite, meta):
            continue
        tira = cauda + cabeca - meta
        # deixa >= 0,12 s de silêncio de cada lado e nunca entra na palavra (fala baixa também passa por
        # "silêncio" a -30 dB)
        amax = max(0, min(cauda - 0.12, y - ult - 0.03))
        bmax = max(0, min(cabeca - 0.12, prim["start"] - x2 - 0.03)) if prim else max(0, cabeca - 0.12)
        a = min(amax, max(tira / 2, tira - bmax))
        b = min(bmax, tira - a)
        out[k][2] = round(y - a, 3)
        out[k + 1][1] = round(x2 + b, 3)
    return [tuple(p) for p in out]


def ritmo(proj, ranges):
    """Palavras por segundo falado (pausas longas não contam)."""
    n = t = 0
    for src, a, b in ranges:
        ws = [w for w in palavras(proj, src) if a - 0.02 <= w["start"] < b]
        n += len(ws)
        t += sum(w["end"] - w["start"] for w in ws) + sum(min(0.3, max(0, ws[i + 1]["start"] - ws[i]["end"])) for i in range(len(ws) - 1))
    return n / t if t else 0


def velocidades(proj, c, padrao=1.0):
    """(velocidade do corpo, {hook: velocidade}): o hook fica no ritmo do corpo, entre 1x e a do vídeo."""
    vel = c.get("speed", padrao)
    ritmo_corpo = ritmo(proj, c["body"]) * vel
    return vel, {h: round(min(vel, max(1.0, ritmo_corpo / (ritmo(proj, r) or 1))), 2) for h, r in c["hooks"].items()}


def linha_do_tempo(proj, c, hook, ranges_cta, padrao=1.0):
    """Lista de pedaços do vídeo final, na ordem: (índice do trecho no reels.json, papel, bruto, início, fim, velocidade).
    papel = "hook" | "corpo" | "cta". Os tempos são do bruto; a duração no vídeo é (fim - início) / velocidade."""
    vel, hv = velocidades(proj, c, padrao)
    out = []
    for i, (s, a, b) in enumerate(c["hooks"][hook]):
        out += [(i, "hook", s, x, y, hv[hook]) for x, y in trechos(proj, s, a, b)]
    corpo = [("corpo", r) for r in c["body"]] + [("cta", r) for r in ranges_cta]
    for i, (papel, (s, a, b)) in enumerate(corpo):
        out += [(i, papel, s, x, y, vel) for x, y in trechos(proj, s, a, b, respiro=(i == len(corpo) - 1))]
    limpo = []                               # trechos seguidos do mesmo bruto não podem se sobrepor (duplica palavra)
    for p in out:
        if limpo and limpo[-1][2] == p[2] and limpo[-1][3] < p[4] and p[3] < limpo[-1][4]:
            p = p[:3] + (limpo[-1][4],) + p[4:]
            if p[4] - p[3] < 0.10: continue
        limpo.append(p)
    return limpo
