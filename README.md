# Editor de vídeos com IA (mentorados)

Plugin que transforma a sua IA (Claude ou Codex) numa editora de vídeos. Você grava no celular, coloca os vídeos numa pasta do Google Drive e pede "edita o vídeo". A IA tira pausas, erros e frases repetidas palavra por palavra, escolhe a melhor tomada de cada frase, coloca imagens de apoio por cima da sua fala e devolve o vídeo pronto na pasta "Concluídos".

Tudo roda no seu computador. O vídeo não sobe para nenhum site, e a transcrição é grátis.

## Do que você precisa
- Um computador Windows ou Mac (com pelo menos 10 GB livres).
- **Claude** (plano Pro ou acima) **ou** **ChatGPT/Codex** (plano Plus ou acima).
- **Google Drive para computador** (grátis): é o que faz a pasta do Drive aparecer no computador. Baixe em google.com/drive/download.

## Instalação no Claude (uma vez, uns 10 minutos)
1. Entre em **claude.ai/customize/plugins** com a sua conta.
2. Clique para **adicionar uma loja (marketplace)** e cole: `atacadoexponencial-maker/edicao-videos-mentorados`. Depois ative o plugin **editor-de-videos**.
   Assim ele se atualiza sozinho sempre que sair uma versão nova.
3. Baixe e instale o app do Claude em claude.ai/download, entre na mesma conta e abra a aba **Code**. Escolha qualquer pasta do computador (pode ser a Área de Trabalho).
4. Escreva: **"Instala o editor de vídeos."** A IA instala o que falta e cria a pasta **Edição de Vídeos IA** no seu Google Drive. Se ela pedir permissão para rodar comandos, clique em permitir.

Alternativa pelo próprio app (sem atualização automática): na aba Code, cole
`/plugin install editor-de-videos --marketplace atacadoexponencial-maker/edicao-videos-mentorados`.

## Instalação no Codex (uma vez, uns 10 minutos)
1. Instale o app do Codex (chatgpt.com/codex) e entre com a sua conta do ChatGPT.
2. Abra **Plugins**, adicione a loja `atacadoexponencial-maker/edicao-videos-mentorados` e instale **editor-de-videos**.
   Pelo terminal, o mesmo é:
   ```
   codex plugin marketplace add atacadoexponencial-maker/edicao-videos-mentorados
   codex plugin add editor-de-videos@edicao-videos-mentorados
   ```
3. Abra uma conversa nova e escreva: **"Instala o editor de vídeos."**

## Como usar no dia a dia
1. No Google Drive (pode ser pelo celular), abra **Edição de Vídeos IA → 1. Para editar** e crie uma pasta com o nome do vídeo (ex.: "Lousa vendas").
2. Coloque os vídeos dentro. Nomes que ajudam a IA (não são obrigatórios):
   - `HOOK A`, `HOOK B`: começos diferentes (sai um vídeo pronto para cada um)
   - `CONTEUDO`: o meio
   - `CTA`: a chamada do final
   - `TAKE palestra`, `TAKE loja`: imagens de apoio, para entrar por cima da sua fala
3. No app do Claude **no computador, aba Code** (ou no app do Codex), escreva: **"Edita o vídeo Lousa vendas."** No chat do site ou do celular não funciona, porque a edição roda no seu computador.
4. A IA faz 3 perguntas rápidas (como foi gravado, se tem takes de apoio, se quer legenda). Responda com o número da opção ou "você decide".
5. Assista o resultado. Se estiver bom, diga **"Aprovado"** e ele aparece em **2. Concluídos**. Se não, diga o que mudar com o tempo do vídeo: "0:12 começar meio segundo antes; 0:31 cortar a frase repetida".

## Pedidos que funcionam
- `O que tem para editar?`
- `Edita o vídeo <nome da pasta>.`
- `Faz a versão com legenda do <nome>.`
- `Ajustes no <nome>: 0:12 ...; 0:31 ...`
- `Aprovado.`
- `Confere se está tudo instalado.`

## Para quem mantém o plugin
- O plugin fica em `plugins/editor-de-videos/` e a skill em `skills/editar-video/` (SKILL.md + scripts Python).
- `.claude-plugin/marketplace.json` é a loja do Claude; `.agents/plugins/marketplace.json` é a do Codex. As duas apontam para a mesma pasta.
- Transcrição: Whisper no computador (grátis). Se existir a variável `ELEVENLABS` (ou a linha `ELEVENLABS=...` em `~/EditorDeVideosIA/.env`), usa a ElevenLabs. `WHISPER_MODELO=medium` deixa o Whisper mais preciso e mais lento.
- Arquivos de trabalho ficam em `~/EditorDeVideosIA/projetos/`, fora do Drive.
