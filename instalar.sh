#!/bin/bash
# Instala o que a edição precisa. Roda sozinho quando a sessão abre (Claude Code)
# ou pelo campo "Setup script" do ambiente (Codex). Pode rodar de novo sem problema.
cd "$(dirname "$0")"

if [ -f .instalado ] && python3 -c "import faster_whisper, imageio_ffmpeg, requests" 2>/dev/null; then
  echo "Ambiente já pronto."
  exit 0
fi

echo "Instalando dependências (só na primeira vez)..."

# ffmpeg do sistema, se der; senão o Python usa o ffmpeg que vem no pacote imageio-ffmpeg
if ! command -v ffmpeg >/dev/null 2>&1; then
  if [ "$(id -u)" = "0" ] && command -v apt-get >/dev/null 2>&1; then
    (apt-get update -qq && apt-get install -y -qq ffmpeg >/dev/null) || echo "apt falhou, sigo com o ffmpeg do pip"
  fi
fi

python3 -m pip install -q -r requirements.txt 2>/dev/null \
  || python3 -m pip install -q --break-system-packages -r requirements.txt

touch .instalado
python3 checar.py
