# Repositório do plugin "editor-de-videos"

Este repositório é a loja (marketplace) do plugin de edição de vídeos para os mentorados, no Claude e no Codex.

- Plugin: `plugins/editor-de-videos/` (manifesto do Claude em `.claude-plugin/plugin.json`, do Codex em `plugin.json`).
- Skill: `plugins/editor-de-videos/skills/editar-video/SKILL.md`, com os scripts em `scripts/` e as referências em `references/`.
- Lojas: `.claude-plugin/marketplace.json` (Claude) e `.agents/plugins/marketplace.json` (Codex).
- Ao mudar a skill, suba a `version` nos dois `plugin.json` para os mentorados receberem a atualização.
- Guia dos mentorados: `README.md`. Escrever simples, em português, sem termos técnicos.
- Nada da marca de quem mantém (nomes, clientes, regras de marca) entra no plugin.
- Para editar um vídeo aqui mesmo, siga a skill `editar-video`.
