# Formato COMPLETO

Estilo de Reels que costuma performar melhor: falado direto para a câmera, com corte seco, legenda curta e uma frase de impacto no topo nos primeiros segundos.

O completo é feito **em cima do simples já aprovado** (mesmos cortes), pelo `completo.py`.

| Elemento | Como é |
|---|---|
| Velocidade | 1,15x (1,25x ficou "rápido demais") |
| Cortes | os do simples; nenhuma pausa audível |
| Zoom | alterna normal x 1,12 **só quando muda o trecho/tomada**; zoom em toda emenda parece erro de corte |
| Topo | caixa branca arredondada, texto preto negrito, 2 linhas, por 4 a 8 s e some (padrão do script: 4 s) |
| Legenda | branca, negrito (Inter Tight 700), minúscula, 2 a 4 palavras por vez, no meio da tela na altura do peito, contorno escuro fino; sem cor, sem emoji |
| Imagens de prova | quando a pessoa mandar (print, documento, conversa): imagem por cima, na parte de baixo; a legenda sobe enquanto ela aparece |
| CTA em caixa | quando a CTA pede palavra no comentário: caixa branca com o pedido ("ESCREVA ... NOS COMENTÁRIOS") durante a CTA |
| Takes de apoio | os mesmos do simples (campo `takes`), aplicados no final |
| Áudio | normalizado (-14 LUFS), sem trilha |

## Aprovações antes do render
1. **Frase do topo** (campo `topo` no reels.json): propor 2 ou 3 opções curtas, que falem com o público da pessoa e deem vontade de assistir, sem travessão (—), sem entregar a virada do vídeo. Esperar a escolha.
2. **Texto da legenda**: `completo.py ... --previa` gera `final/<nome> - legenda.txt`. Conferir nomes próprios, marcas e termos do nicho (a transcrição erra). Correções no campo `legenda_corrige`.
