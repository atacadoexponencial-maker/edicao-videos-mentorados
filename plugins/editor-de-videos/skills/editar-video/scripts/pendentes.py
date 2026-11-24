"""Lista os vídeos esperando edição em "1. Para editar" (pasta sem par em "2. Concluídos" = pendente).

Cada vídeo é uma pasta com os arquivos daquele vídeo. Nomes recomendados (não obrigatórios; sem padrão a IA
decide pelo que foi falado):
  HOOK A, HOOK B ...   começos diferentes (um vídeo final por hook)
  CONTEUDO             o meio, igual para todos os hooks (pode ser CONTEUDO 1, CONTEUDO 2)
  CTA                  o fim (chamada para ação)
  TAKE ...             imagens de apoio sem fala importante (entram por cima, com a voz por baixo)
Um arquivo só, com tudo junto, também serve.

Uso: python pendentes.py
"""
import re
from comum import VIDEO_EXT, PARA_EDITAR, CONCLUIDOS, duracao
from pasta import pasta_do_aluno

raiz = pasta_do_aluno()
entrada, saida = raiz / PARA_EDITAR, raiz / CONCLUIDOS
feitos = {p.name for p in saida.iterdir() if p.is_dir()}
pastas = sorted(p for p in entrada.iterdir() if p.is_dir())
for p in pastas:
    status = "CONCLUÍDO" if p.name in feitos else "PENDENTE"
    print(f"[{status}] {p.name}  -> {p}")
    for a in sorted(f for f in p.iterdir() if f.suffix.lower() in VIDEO_EXT):
        try:
            dur = f" {duracao(a):.0f}s"
        except SystemExit:
            dur = " (ainda sincronizando ou arquivo com problema)"
        tipo = re.search(r"\b(HOOK|CONTE[UÚ]DO|CTA|TAKE)", a.stem.upper())
        print(f"     {a.name}{dur}{'' if tipo else '   (sem HOOK/CONTEUDO/CTA/TAKE no nome: decido pela fala)'}")
soltos = sorted(f for f in entrada.iterdir() if f.suffix.lower() in VIDEO_EXT)
for s in soltos:
    print(f"[FORA DE PASTA] {s.name}  <-- crie uma pasta com o nome do vídeo e coloque o arquivo dentro")
if not pastas and not soltos:
    print(f"Nada para editar em {entrada}")
