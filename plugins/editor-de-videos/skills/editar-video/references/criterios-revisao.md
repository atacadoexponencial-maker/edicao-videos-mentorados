# Critérios de revisão (erros reais já cometidos e como evitar)

> A transcrição padrão é o Whisper, que roda grátis no computador. Ele às vezes junta repetições numa palavra só, esconde gagueira e erra o fim da palavra em alguns décimos de segundo. Por isso as verificações abaixo (repetições, quadros, conferir) são parte do trabalho, não um extra.

Cada item: o que aconteceu, por que aconteceu e como evitar. Acrescente aqui quando surgir um novo.

## 1. Frase repetida no meio do vídeo
**Caso:** caixinha "como se destacar" — "esse tipo de, esse tipo de, esse tipo de conteúdo" saiu inteiro no vídeo.
**Por quê:** a transcrição pode juntar repetições ditas em sequência numa palavra esticada (um "conteúdo" de 1,5 s). A transcrição do vídeo final também esconde, então comparar texto não pega.
**Evitar:** `repeticoes.py` em todo conteúdo; palavra `<LONGA>` no `palavras.py` é sinal de alerta. Começar o trecho na última tomada.
Outro caso igual: "Verdade 1: comercial" dito duas vezes com pausa no meio, a transcrição registrou uma vez só.

## 2. Pessoa lendo o roteiro
**Caso:** vídeo do casal — em "processo comercial é o que separa...", "não é um diferencial" e "toda marca que trava nos 30, 40, 50 mil" os dois olham para o papel.
**Por quê:** só aparece na imagem; o áudio é normal.
**Evitar:** `quadros.py` e olhar as grades. Trocar pela tomada olhando para a câmera (quase sempre existe, porque eles repetem).

## 3. Última palavra cortada
**Caso:** "consultiva" saiu "consulta"; CTA "me segue para mais respostas assim" soou cortado.
**Por quê:** a transcrição marca o fim da palavra até 0,4 s antes do som acabar; e vídeo que termina colado na última palavra perde os últimos milissegundos no player do Drive/Instagram.
**Evitar:** o `montar.py` estende até o silêncio real e deixa 0,6 s de respiro no fim. `conferir.py` avisa folga < 0,4 s.

## 4. Palavra duplicada na emenda hook → corpo
**Caso:** caixinha "estagnado" começava "não sei o que fazer. Bom, bom...".
**Por quê:** ele emendou "fazer" e "Bom" sem pausa; o fim do hook e o início do corpo pegaram o mesmo "Bom".
**Evitar:** em emenda colada, olhar `energia.py` e colocar o limite no vale entre as palavras (aqui: hook até 3,66 s, corpo a partir de 3,80 s).

## 5. Hook mais rápido que o corpo
**Caso:** Ad3 hook B parecia acelerado.
**Por quê:** hooks são gravados mais rápido (5,2 a 5,9 palavras/s x 3,75 do corpo); com 1,3x nos dois, a diferença cresce.
**Evitar:** o `montar.py` iguala o ritmo sozinho (entre 1x e a velocidade do vídeo). Se mesmo em 1x o hook ficar rápido, avisar — abaixo de 1x a voz arrasta. Dica para quem grava: gravar o hook no ritmo do conteúdo.

## 6. Vídeo rápido demais (o simples é 1x e o completo 1,15x; `speed` só se a pessoa pedir)
**Caso:** "achei que ficou muito rápido em 1,3x" (caixinha), mas "nem todas achei rápidas".
**Por quê:** cortar as pausas já acelera; quem fala pausado fica corrido com 1,3x por cima.
**Evitar:** velocidade por conteúdo (`speed`); 1,15x para falas pausadas.

## 7. Vídeo sem CTA
**Caso:** duas caixinhas foram gravadas sem CTA.
**Evitar:** todo vídeo termina com CTA. Sem CTA gravado, emprestar um genérico ("Me segue para mais respostas assim") de outro bruto do mesmo dia, com mesma roupa, cenário e ângulo (conferir nos quadros), e avisar.

## 8. Palavra sumida no começo do trecho (transcrição atrasada)
**Caso:** vídeo do ovo — "Sabe o que esse ovo tem a ver com o seu tráfego pago? *Nada!* Mas aproveita..." saiu sem o "Nada!", que é a resposta da piada.
**Por quê:** a transcrição marcou "Nada!" em 6,47 s; no áudio ele está em 5,25–5,85 s. O trecho começou em 6,47 e o snap só olha 0,5 s para trás.
**Evitar:** o `conferir.py` marca "PALAVRA FALTANDO" — tratar como bloqueio. `energia.py` entre o fim da palavra anterior e o início do trecho; se houver fala, começar o trecho nela.
**Lição:** o aviso apareceu e mesmo assim o relatório disse "não há palavra sendo cortada". Relatório tem que listar cada aviso e o que foi feito com ele.

## 9. Falso alarme de fim curto
**Caso:** vídeos 2 e 3 da mesma leva acusaram folga negativa, mas tinham 0,6 a 1,1 s de respiro.
**Por quê:** com ruído de sala, a transcrição estica a última palavra até o fim do arquivo.
**Evitar:** o `conferir.py` mede a folga pelo áudio, comparando com o ruído da própria gravação.

## 10. Lousa picotada, tomada descartada e hook de outra lousa
**Caso:** uma edição de lousas foi chamada de "péssima". Lousa 1: corpo de 47 s com 8 pedaços de um bruto de 8 min, sem "tirador x guia de pedido" nem "ticket baixo x alto"; Hook B era a tomada que a pessoa descartou ("De novo, de novo" logo depois); frase do transacional pegou a tomada dos 144 s, seguida de "Mais uma desse aí"; o hook da LOUSA 2 (outra lousa, outro assunto) virou Hook C da Lousa 1.
**Evitar:** `checar.py` antes de montar (reprova os três) e conferir ponto a ponto da lousa no corpo.

## 11. Tomada colada na outra e hesitação sem palavra
**Caso:** "a revendedora, a revendedora" (trecho de uma tomada abandonada antes da tomada certa, que já começava com a mesma frase); "mas vale ressaltar" duas vezes (dividi o trecho numa pausa e o primeiro pedaço era a tomada abandonada); "ela ã" (hesitação que a transcrição nem registra).
**Por quê:** a transcrição esticou "revendedora" e "gente" por 2 s e escondeu a repetição; o "ã" só aparece como um pico no `energia.py`, sem palavra.
**Evitar:** antes de usar dois trechos seguidos da mesma frase, retranscrever o intervalo isolado (como o `repeticoes.py` faz) e ver se a tomada seguinte já começa com o mesmo texto. Ao dividir um trecho numa pausa, conferir que a pausa não separa duas tomadas. Quando o snap puxa a palavra vizinha (vale menor que 0,3 s), recortar o pedaço do bruto num arquivo próprio em `brutos/` (com `edit/transcripts/<nome>.json` deslocado) e usar no `reels.json`.

## 12. Tempos deslocados no fim de arquivo longo
**Caso:** vídeo de 18 min: a transcrição antiga estava 0,8 a 1,7 s fora do som depois dos 14 min; corte e painel saíram no lugar errado.
**Evitar:** o `transcrever.py` retranscreve 30 s isolados a 80% de todo bruto com mais de 5 min e avisa se a diferença passa de 0,3 s. Com aviso, retranscrever isolado cada trecho usado daquela parte.

## 13. Respiro entre as frases (corte frouxo)
**Caso:** depoimento: "ele terminou a frase, já vem o começo da outra, sem muitos espaços e respiros, bem juntinho". Outro pedido: "sem respiros, cuidado com duplicação de palavras, frases bem conectadas, assim que uma acaba a outra já começa, mas sem atropelar".
**Por quê:** o corte antigo só tirava pausas acima de 0,3 s e deixava 0,07 s de cada lado; as respirações (acima de -38 dB) contavam como fala.
**Evitar:** o `cortes.py` agora corta pausas a partir de 0,15 s, deixa 0,05 s de cada lado e mede o silêncio a -35 dB (a -32 dB comeu o fim de "isso" falado baixo no Depoimento). Cuidados que continuam valendo: trechos contíguos do mesmo bruto vão num trecho só (dois trechos colados se sobrepuseram e duplicaram um "tá?"; o `cortes.py` agora impede a sobreposição) e o `conferir.py` roda em todo vídeo para pegar palavra comida em fala baixa.

## Dicas de gravação (passar para a pessoa quando fizer sentido)
- Um arquivo por parte, com nome "HOOK A", "CONTEUDO", "CTA", "TAKE ..." (não é obrigatório).
- Mandar o roteiro junto: ajuda a escolher a tomada certa.
- Definir antes de gravar se a peça é orgânica ou anúncio (qual CTA).
- Gravar o hook no mesmo ritmo do conteúdo.
