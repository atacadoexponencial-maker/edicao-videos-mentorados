# Edição de vídeos para mentorados (teste)

Repositório de teste. Serve para descobrir se a edição roda na nuvem do Claude Code e do Codex sem configuração. A edição aqui é simples: corta as pausas longas da fala. O método completo entra depois do teste.

## O que o teste responde
1. A instalação roda sozinha?
2. A transcrição gratuita (Whisper) funciona na nuvem, e em quanto tempo?
3. A ElevenLabs funciona com a chave?
4. O vídeo pronto sai por link de download?

## Teste no Claude Code (claude.ai/code)
1. Escolha este repositório e use o ambiente padrão, sem mudar nada.
2. Mande: `Roda python3 checar.py e me mostra o resultado.`
3. Mande: `Edita esse vídeo: <link de um Reels curto no Drive, compartilhado como "qualquer pessoa com o link">`
4. Anote o que o Claude devolveu: tempos, link ou "SEM LINK".
5. Opcional (ElevenLabs): no ambiente, em **Network secrets**, adicione `api.elevenlabs.io` com o header `xi-api-key` e a chave. Abra uma sessão nova e mande: `Configurei a ElevenLabs. Edita esse vídeo: <link>`

## Teste no Codex (chatgpt.com/codex)
1. Crie um ambiente com este repositório.
2. No campo de **setup script**, cole: `bash instalar.sh`
3. Rode as mesmas mensagens dos passos 2 e 3 acima.
4. Se o download falhar, ative o acesso à internet do agente nas configurações do ambiente e repita.

## Arquivos
- `instalar.sh`: instala ffmpeg, Whisper e o resto. No Claude Code roda sozinho quando a sessão abre.
- `checar.py`: mostra o que está instalado e quais sites a sessão consegue acessar.
- `editar.py`: baixa, transcreve, corta as pausas, gera o vídeo e tenta criar o link.
- `CLAUDE.md` / `AGENTS.md`: instruções para o Claude Code e o Codex (mesmo conteúdo).
