# Edição de vídeos (versão de teste)

Você ajuda uma pessoa leiga a editar vídeos. Fale simples, em português, sem termos técnicos.

## Antes de tudo
Se `python3 -c "import faster_whisper"` falhar, rode `bash instalar.sh` e espere terminar.

## Quando pedirem para editar um vídeo
1. Peça o link do vídeo, se ainda não veio. Pode ser Google Drive (compartilhado como "qualquer pessoa com o link"), YouTube ou link direto de .mp4.
2. Rode `python3 editar.py "<link>"`.
   - Se a pessoa disser que configurou a ElevenLabs, use `--motor elevenlabs`.
3. Mostre o resultado em poucas linhas: duração antes e depois, quanto tempo levou e o link para baixar.
4. Se não saiu link ("SEM LINK"):
   - faça `git add` do arquivo em `saida/` e de `saida/relatorio.json`, commit e push;
   - explique como baixar: abrir o repositório no GitHub, trocar para a branch que você enviou, abrir a pasta `saida`, clicar no vídeo e no botão de download.

## Se algo falhar
Rode `python3 checar.py`, mostre o resultado inteiro e diga em uma frase o que está bloqueado.
Não tente outro caminho por conta própria: este repositório é um teste e o relatório é o que importa.
