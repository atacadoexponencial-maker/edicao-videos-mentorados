"""Retranscreve cada vídeo final e compara com o texto esperado dos trechos escolhidos.
Acusa palavra cortada, sobrando ou repetida na emenda. Diferenças do tipo "para"/"pra", "construtora"/"consultora"
são ruído da transcrição (Whisper ou ElevenLabs); olhe as que envolvem começo/fim de trecho ou palavra a mais.
Também confere o fim pelo áudio: depois da última fala precisa haver pelo menos ~0,35 s.
"PALAVRA FALTANDO" bloqueia a entrega até ser explicada: a transcrição pode marcar uma palavra mais de 1 s depois
do som real (caso "Nada!") e o trecho começa tarde demais. Olhe o bruto com energia.py antes do início do trecho.

Uso: python conferir.py <projeto> ["Nome do conteúdo" ...]
"""
import difflib, re, struct, subprocess, sys, unicodedata
from comum import projeto, palavras, transcrever, config, conteudos, nome_saida, run


def folga_audio(f, dur):
    """Tempo entre o fim da última fala e o fim do arquivo, medido no áudio (a transcrição estica a última
    palavra até o fim quando há ruído de sala, e acusava folga curta à toa)."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-sseof", "-4", "-i", str(f), "-vn", "-ac", "1", "-ar", "1000",
                          "-f", "s16le", "-"], capture_output=True).stdout
    a = struct.unpack(f"<{len(raw) // 2}h", raw)
    blocos = [max((abs(x) for x in a[i:i + 50]), default=0) for i in range(0, len(a), 50)]   # 50 ms
    if not blocos:
        return 0.0
    ordem = sorted(blocos)
    voz, piso = ordem[int(len(ordem) * 0.9)], ordem[int(len(ordem) * 0.1)]
    limite = max(voz * 0.3, piso * 2.5)          # acima do ruído da sala
    ult = max((i for i, v in enumerate(blocos) if v > limite), default=len(blocos) - 1)
    return round((len(blocos) - 1 - ult) * 0.05, 2)


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", t).split()


proj = projeto(sys.argv[1]); cfg = config(proj)
chk = proj / "edit" / "check"
for nome in conteudos(cfg, sys.argv[2:]):
    c = cfg[nome]
    ctas = c.get("ctas") or {None: []}
    for hook, ranges in c["hooks"].items():
        for nome_cta, ranges_cta in ctas.items():
            fn = nome_saida(nome, hook, c, nome_cta, len(ctas))
            f = proj / "final" / f"{fn}.mp4"
            if not f.exists(): print(f"== {fn}: não renderizado"); continue
            j = chk / "transcripts" / f"{fn}.json"
            if j.exists() and j.stat().st_mtime < f.stat().st_mtime: j.unlink()      # vídeo mudou: retranscreve
            t = transcrever(f, j)
            got_w = t["words"]
            got = norm(" ".join(w["text"] for w in got_w))
            exp = norm(" ".join(w["text"] for s, a, b in ranges + c["body"] + ranges_cta
                                for w in palavras(proj, s) if a - 0.02 <= w["start"] < b))
            sm = difflib.SequenceMatcher(None, exp, got, autojunk=False)
            dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).stdout)
            folga = folga_audio(f, dur)
            print(f"== {fn}: semelhança {sm.ratio():.3f}, {dur:.1f}s, folga no fim {folga:.2f}s (pelo áudio){'  <-- CURTA' if folga < 0.35 else ''}")
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal":
                    continue
                falta = [w for w in exp[i1:i2] if w not in got[max(0, j1 - 3):j2 + 3]] if op in ("delete", "replace") else []
                alerta = "  <-- PALAVRA FALTANDO: investigar com energia.py antes de subir" if op == "delete" or (op == "replace" and len(falta) > len(got[j1:j2])) else ""
                print(f"   {op}: esperado [{' '.join(exp[i1:i2])}] -> saiu [{' '.join(got[j1:j2])}]{alerta}")
