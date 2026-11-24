"""Copia os vídeos prontos de <projeto>/final para "2. Concluídos/<Nome do vídeo>/" na pasta do aluno.
Se o arquivo já existe lá, substitui (no Drive, o link continua o mesmo).

Uso: python entregar.py <projeto> ["Nome do vídeo final sem .mp4" ...]   (sem nomes = todos os .mp4 de final/)
"""
import shutil, sys
from comum import projeto, CONCLUIDOS
from pasta import pasta_do_aluno

proj = projeto(sys.argv[1])
destino = pasta_do_aluno() / CONCLUIDOS / proj.name
destino.mkdir(parents=True, exist_ok=True)
arquivos = [proj / "final" / f"{n}.mp4" for n in sys.argv[2:]] or sorted(
    f for f in (proj / "final").glob("*.mp4") if not f.stem.endswith((".montado", ".base")))
for f in arquivos:
    if not f.exists():
        sys.exit(f"Não existe: {f}")
    shutil.copy2(f, destino / f.name)
    print("entregue", f.name, flush=True)
print(f"Pasta: {destino}")
