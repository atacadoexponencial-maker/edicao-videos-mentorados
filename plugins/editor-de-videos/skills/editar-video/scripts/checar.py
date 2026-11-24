"""Trava ANTES de renderizar: confere as escolhas do edit/reels.json contra o próprio bruto.
Nasceu de uma edição de lousas que ficou péssima:

- tomada descartada: logo depois do trecho a pessoa diz "de novo", "mais uma", "não tô feliz"... = ele mesmo
  jogou fora aquela tomada (Hook B usava "A sua revendedora compra uma vez e some" seguido de "De novo, de novo").
- tomada antiga: a mesma frase aparece de novo mais adiante no bruto. A certa costuma ser a última completa
  (corpo usava "Transacional, a venda é oi tchau" dos 144 s, refeita 3 vezes depois).
- hook de outro conteúdo: o arquivo do hook é de outro tema/lousa (LOUSA_2 num corpo da LOUSA_1): a lousa, o
  cenário e o assunto mudam. Só vale se as duas estiverem em "_mesmo_conteudo" no conteúdo (depois de ver os quadros).
- corpo curto demais (só ATENÇÃO, não reprova): menos de 25% da fala do bruto principal. Uma edição ruim montou 47 s de um
  bruto de 8 min e pulou metade da explicação (tirador x guia de pedido, ticket baixo x alto).

Saída 1 = REPROVADO: corrigir o reels.json antes de montar. Se uma escolha for proposital, explicar no
"_nota" do conteúdo e no relatório.

Uso: python checar.py <projeto> ["Nome do conteúdo" ...]
"""
import difflib, re, sys, unicodedata
from comum import projeto, palavras, config, conteudos

DESCARTE = re.compile(r"\b(de novo|mais uma|nao (to|estou|tô) feliz|vou repetir|repete|regrava|porcaria|peraí|perai|errei)\b")


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", t).split()


def tema(stem):
    """LOUSA_1_HOOK_A_Conteudo -> lousa 1. Tudo antes de HOOK/CONTEUDO/CTA."""
    s = norm(stem.replace("_", " "))
    out = []
    for w in s:
        if w in ("hook", "conteudo", "cta", "criativo"):
            break
        out.append(w)
    return " ".join(out)


proj = projeto(sys.argv[1]); cfg = config(proj)
reprovado = False
for nome in conteudos(cfg, sys.argv[2:]):
    c = cfg[nome]; avisos = []
    trechos = [("hook " + h, r) for h, rs in c["hooks"].items() for r in rs] + [("corpo", r) for r in c["body"]] \
        + [("cta " + k, r) for k, rs in (c.get("ctas") or {}).items() for r in rs]
    for papel, (stem, a, b) in trechos:
        ws = palavras(proj, stem)
        dentro = [w for w in ws if a - 0.02 <= w["start"] < b]
        depois = " ".join(norm(" ".join(w["text"] for w in ws if b <= w["start"] < b + 4))[:5])   # só o que vem logo em seguida
        if DESCARTE.search(depois):
            avisos.append(f"{papel} {stem} {a}-{b}: logo depois ele diz '{depois[:60]}' -> tomada descartada, usar a seguinte")
        txt = norm(" ".join(w["text"] for w in dentro))
        if len(txt) >= 5:
            resto = [w for w in ws if w["start"] >= b + 1]
            for i in range(0, max(0, len(resto) - len(txt)) + 1, 2):
                cand = norm(" ".join(w["text"] for w in resto[i:i + len(txt)]))
                if difflib.SequenceMatcher(None, txt, cand).ratio() >= 0.75:
                    avisos.append(f"{papel} {stem} {a}-{b}: '{' '.join(txt[:8])}...' é refeita em {resto[i]['start']:.1f}s -> usar a última tomada completa")
                    break
    temas_corpo = {tema(s) for s, _, _ in c["body"]}
    ok = {tema(s) for s in c.get("_mesmo_conteudo", [])}
    for h, rs in c["hooks"].items():
        for s, _, _ in rs:
            if tema(s) not in temas_corpo and not ({tema(s)} | temas_corpo) <= ok:
                avisos.append(f"hook {h} vem de '{s}' (tema '{tema(s)}'), corpo é de {sorted(temas_corpo)} -> outro conteúdo; conferir quadros e marcar '_mesmo_conteudo' se for a mesma lousa")
    principal = max({s for s, _, _ in c["body"]}, key=lambda s: sum(b - a for x, a, b in c["body"] if x == s))
    fala = sum(w["end"] - w["start"] for w in palavras(proj, principal))
    usado = sum(b - a for x, a, b in c["body"] if x == principal)
    print(f"== {nome}" + ("  OK" if not avisos else "  REPROVADO"))
    if fala > 60 and usado / fala < 0.25:   # não reprova (gravação com muita repetição usa pouco), mas obriga a conferir
        print(f"   ATENÇÃO: corpo usa {usado:.0f}s de {fala:.0f}s de fala de {principal} ({usado / fala:.0%}). Liste os pontos do bruto (o que ele escreve na lousa) e confira que cada um está no corpo.")
    for a in avisos: print("   - " + a)
    reprovado = reprovado or bool(avisos)
sys.exit(1 if reprovado else 0)
