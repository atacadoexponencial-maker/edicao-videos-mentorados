"""Funções compartilhadas da skill editar-video.

Onde ficam as coisas:
  PASTA DO ALUNO (no Google Drive dele, sincronizada no computador, ou na Área de Trabalho):
    Edição de Vídeos IA/
      1. Para editar/<Nome do vídeo>/   brutos que a pessoa sobe (hook, conteúdo, CTA, takes)
      2. Concluídos/<Nome do vídeo>/    vídeos prontos (entregar.py coloca aqui)
  PASTA DE TRABALHO (no computador, fora do Drive): ~/EditorDeVideosIA/projetos/<Nome do vídeo>/
    brutos/   cópia dos vídeos originais (nomes sem acento)
    edit/     reels.json, transcrições, caches, conferências
    final/    vídeos prontos antes de entregar
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

VIDEO_EXT = (".mov", ".mp4", ".m4v", ".mkv", ".webm")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # acentos no terminal do Windows

TRABALHO = Path(os.getenv("EDITOR_VIDEOS_TRABALHO") or Path.home() / "EditorDeVideosIA")
CONFIG = TRABALHO / "config.json"
NOME_RAIZ = "Edição de Vídeos IA"
PARA_EDITAR, CONCLUIDOS = "1. Para editar", "2. Concluídos"


# ---------- ffmpeg: o do sistema ou o que vem pelo pip (static-ffmpeg) ----------
def _garantir_ffmpeg():
    if shutil.which("ffmpeg") and shutil.which("ffprobe"):
        return
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths(weak=True)        # baixa ffmpeg e ffprobe na primeira vez e põe no PATH
    except Exception as e:
        print(f"AVISO: ffmpeg não encontrado ({type(e).__name__}). Rode o instalar.py.", file=sys.stderr)


_garantir_ffmpeg()


def ler_config():
    return json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else {}


def salvar_config(**kw):
    TRABALHO.mkdir(parents=True, exist_ok=True)
    c = ler_config(); c.update(kw)
    CONFIG.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")


def projeto(arg):
    """Nome simples ("Lousa 3") vira ~/EditorDeVideosIA/projetos/Lousa 3; caminho é usado como está."""
    p = Path(arg)
    if not p.is_absolute() and len(p.parts) == 1:
        p = TRABALHO / "projetos" / arg
    p = p.resolve()
    for d in ("brutos", "edit", "final"):
        (p / d).mkdir(parents=True, exist_ok=True)
    return p


def env(nome, obrigatoria=False):
    """Lê variável do ambiente ou do arquivo ~/EditorDeVideosIA/.env. Nunca imprimir o valor."""
    if os.getenv(nome):
        return os.getenv(nome)
    f = TRABALHO / ".env"
    if f.exists():
        for linha in f.read_text(encoding="utf-8").splitlines():
            if linha.strip().startswith(nome + "="):
                v = linha.split("=", 1)[1].strip().strip('"').strip("'")
                if v:
                    return v
    if obrigatoria:
        sys.exit(f"Chave {nome} não encontrada.")
    return None


def fonte(proj, stem):
    """Caminho do bruto pelo nome sem extensão."""
    for ext in VIDEO_EXT:
        f = proj / "brutos" / f"{stem}{ext}"
        if f.exists():
            return f
    sys.exit(f"Bruto não encontrado: {stem}")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-2000:]); sys.exit(1)
    return r


def duracao(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).stdout)


# ---------- Transcrição palavra a palavra ----------
# Padrão: Whisper no próprio computador (grátis, sem chave). Se existir a chave ELEVENLABS, usa a ElevenLabs
# Scribe v2 (paga, transcreve gagueira e repetição com mais fidelidade). WHISPER_MODELO muda o modelo
# (small = padrão, rápido; medium = mais preciso e ~3x mais lento).
DICA_FALA = ("Transcrição literal, com repetições, hesitações e frases recomeçadas: então, é, é, tipo, eu, eu acho que... "
             "né? Ãh, peraí, de novo. Vou de novo. Pode ser?")


def _audio_16k(midia, destino):
    run(["ffmpeg", "-v", "error", "-y", "-i", str(midia), "-vn", "-ac", "1", "-ar", "16000", str(destino)])


def _whisper(midia, saida_json):
    from faster_whisper import WhisperModel
    modelo = env("WHISPER_MODELO") or "small"
    audio = saida_json.with_suffix(".tmp.wav")
    _audio_16k(midia, audio)
    global _MODELO
    if "_MODELO" not in globals() or _MODELO[0] != modelo:
        print(f"  carregando o Whisper ({modelo}); na primeira vez ele é baixado", flush=True)
        _MODELO = (modelo, WhisperModel(modelo, device="cpu", compute_type="int8"))
    segs, _ = _MODELO[1].transcribe(str(audio), language="pt", word_timestamps=True, beam_size=5,
                                    condition_on_previous_text=False, initial_prompt=DICA_FALA)
    words = []
    for s in segs:
        for w in s.words or []:
            t = w.word.strip()
            if t:
                words.append({"type": "word", "text": t, "start": round(w.start, 3), "end": round(w.end, 3)})
    audio.unlink(missing_ok=True)
    return {"words": words, "eventos": [], "servico": f"whisper {modelo}"}


def _elevenlabs(midia, saida_json, key):
    import requests
    audio = saida_json.with_suffix(".tmp.mp3")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(midia), "-vn", "-ac", "1", "-ar", "16000", "-b:a", "64k", str(audio)])
    for tentativa in range(3):
        try:
            with open(audio, "rb") as f:
                r = requests.post("https://api.elevenlabs.io/v1/speech-to-text", headers={"xi-api-key": key}, timeout=1800,
                                  data={"model_id": "scribe_v2", "language_code": "por", "tag_audio_events": "true",
                                        "timestamps_granularity": "word", "diarize": "false"},
                                  files={"file": (audio.name, f, "audio/mpeg")})
            if r.status_code in (401, 402, 403) or "quota" in r.text[:500].lower():
                audio.unlink(missing_ok=True)
                print(f"  ElevenLabs recusou ({r.status_code}); sigo com o Whisper grátis", flush=True)
                return None
            r.raise_for_status()
            d = r.json()
            break
        except requests.RequestException as e:
            if tentativa == 2:
                audio.unlink(missing_ok=True)
                print(f"  ElevenLabs sem resposta ({type(e).__name__}); sigo com o Whisper grátis", flush=True)
                return None
            time.sleep(5)
    audio.unlink(missing_ok=True)
    words = [{"type": "word", "text": w["text"], "start": w["start"], "end": w["end"]}
             for w in d.get("words") or [] if w.get("type") == "word" and (w.get("text") or "").strip()]
    eventos = [{"text": w["text"], "start": w["start"], "end": w["end"]} for w in d.get("words") or [] if w.get("type") == "audio_event"]
    return {"words": words, "eventos": eventos, "servico": "elevenlabs scribe_v2"}


def transcrever(midia, saida_json, idioma="pt"):
    """Transcreve áudio/vídeo e salva {"words": [{type,text,start,end}], "eventos": [...]} (segundos). Com cache."""
    saida_json = Path(saida_json)
    if saida_json.exists():
        return json.loads(saida_json.read_text(encoding="utf-8"))
    saida_json.parent.mkdir(parents=True, exist_ok=True)
    key = env("ELEVENLABS")
    out = (_elevenlabs(midia, saida_json, key) if key else None) or _whisper(midia, saida_json)
    saida_json.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def palavras(proj, stem):
    d = json.loads((proj / "edit" / "transcripts" / f"{stem}.json").read_text(encoding="utf-8"))
    return [w for w in d["words"] if w.get("type", "word") == "word"]


# ---------- Silêncios ----------
def silencios(proj, stem, db=-38, minimo=0.30):
    cache = proj / "edit" / "silences" / f"{stem}_{db}_{minimo}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    cache.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", str(fonte(proj, stem)), "-vn", "-ac", "1",
                        "-af", f"silencedetect=noise={db}dB:d={minimo}", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    s = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)],
                 [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]))
    cache.write_text(json.dumps(s))
    return s


def deriva(proj, stem, posicao=0.8):
    """Confere se os tempos da transcrição continuam certos no fim de um arquivo longo (> 5 min): retranscreve
    30 s isolados a `posicao` do arquivo (80% por padrão; trecho curto sai fiel) e compara com a transcrição inteira.
    Devolve (início do trecho, diferença mediana em s, palavras comparadas) ou None.
    |diferença| > 0,3 s = tempos deslocados ali (caso Recompra, 09/10/2026: 0,8 a 1,7 s depois dos 14 min)."""
    ws = palavras(proj, stem)
    dur = duracao(fonte(proj, stem))
    if not ws or dur < 300:
        return None                                  # arquivo curto: atraso acumulado não chega a aparecer
    t0 = round(min(dur * posicao, dur - 32), 1)
    snip = proj / "edit" / "snip"; snip.mkdir(parents=True, exist_ok=True)
    trecho = snip / f"{stem}_deriva_{t0}.mp4"
    if not trecho.exists():
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0}", "-t", "30", "-i", str(fonte(proj, stem)), "-vn", "-c:a", "aac", str(trecho)])
    ref = transcrever(trecho, snip / "transcripts" / f"{trecho.stem}.json")["words"]
    norm = lambda t: re.sub(r"\W", "", t.lower())
    import difflib
    alvo = [w for w in ws if t0 - 2 <= w["start"] <= t0 + 32]
    sm = difflib.SequenceMatcher(None, [norm(w["text"]) for w in ref], [norm(w["text"]) for w in alvo], autojunk=False)
    d = sorted(alvo[b.b + k]["start"] - (t0 + ref[b.a + k]["start"]) for b in sm.get_matching_blocks() for k in range(b.size))
    return (t0, round(d[len(d) // 2], 2), len(d)) if len(d) >= 5 else None


def config(proj):
    return json.loads((proj / "edit" / "reels.json").read_text(encoding="utf-8"))


def conteudos(cfg, nomes):
    return nomes or [k for k in cfg if not k.startswith("_")]


def nome_final(nome, hook, cfg_conteudo):
    return f"{nome} - {hook}" if len(cfg_conteudo["hooks"]) > 1 else nome


def nome_saida(nome, hook, cfg_conteudo, nome_cta, n_ctas):
    """Nome do vídeo final: a versão com CTA de conteúdo (orgânica) fica com o nome-base; a de anúncio recebe "- Ad"."""
    base = nome_final(nome, hook, cfg_conteudo)
    if nome_cta and nome_cta != "Conteúdo":
        base += f" - {nome_cta}"
    return base
