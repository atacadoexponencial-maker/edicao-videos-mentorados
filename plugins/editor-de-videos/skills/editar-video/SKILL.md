---
name: editar-video
description: Edita vídeos falados (Reels, Shorts, TikTok, aulas, lousas) a partir dos brutos gravados no celular. Corta pausas, erros e repetições palavra por palavra, escolhe a melhor tomada de cada frase, monta um vídeo por hook, coloca takes de apoio por cima da fala com a voz de fundo, confere e entrega na pasta "2. Concluídos". Use quando pedirem para editar um vídeo, ver o que tem para editar, instalar ou configurar a edição, fazer a versão com legenda, aplicar ajustes ("0:23 cortar...") ou quando reclamarem de um vídeo editado (frase repetida, fala cortada, rápido demais).
---

# Editar vídeo

Você edita vídeos para uma pessoa **leiga**. Fale simples, em português, frases curtas, sem termos técnicos (nada de "script", "JSON", "ffmpeg", "render"; diga "estou montando o vídeo"). Nunca mostre comandos nem saídas longas para ela: mostre o resultado.

O que faz um vídeo bom aqui é parecer que a pessoa falou de primeira: nenhuma frase dita duas vezes, nenhuma palavra comida na emenda, ninguém olhando o papel, ritmo parecido do começo ao fim. Quase todo erro já cometido veio de confiar demais na transcrição; por isso a conferência (passos 5 a 7) é parte do trabalho, não um extra. Leia também `references/criterios-revisao.md` antes da primeira edição.

## Ferramentas

`S` = a pasta `scripts` ao lado deste SKILL.md (use o caminho completo). `PY` = `python` no Windows (ou `py` se `python` não existir), `python3` no Mac e no Linux. `<projeto>` = nome do vídeo (vira `~/EditorDeVideosIA/projetos/<nome>/`, com `brutos/`, `edit/`, `final/`).

```bash
$PY $S/checar_ambiente.py                           # uma vez por conversa; saída 1 = rodar instalar.py
$PY $S/instalar.py                                  # primeira vez no computador (alguns minutos)
$PY $S/pasta.py [--definir <caminho>]               # onde fica a pasta "Edição de Vídeos IA"
$PY $S/pendentes.py                                 # vídeos esperando edição
$PY $S/baixar.py <projeto> <nome-da-pasta|caminho|link>   # copia os brutos (duração/resolução)
$PY $S/transcrever.py <projeto>                     # transcrição palavra a palavra + edit/takes.md + aviso de deriva
$PY $S/palavras.py <projeto> <bruto> [ini] [fim]    # palavra a palavra com pausas; marca <LONGA>
$PY $S/energia.py <projeto> <bruto> <ini> <dur>     # volume a cada 25 ms: onde a palavra acaba de verdade
$PY $S/quadros_take.py <projeto> <bruto-do-take>    # quadros de um take de apoio (abrir com Read)
$PY $S/checar.py <projeto> ["Conteúdo" ...]         # TRAVA antes de montar
$PY $S/montar.py <projeto> ["Conteúdo" ...]         # vídeo simples (+ takes de apoio), um conteúdo por vez
$PY $S/repeticoes.py <projeto> ["Conteúdo" ...]     # repetições escondidas
$PY $S/quadros.py <projeto> "Conteúdo"              # grade de quadros dos trechos (abrir com Read)
$PY $S/conferir.py <projeto> ["Conteúdo" ...]       # retranscreve o final e compara
$PY $S/completo.py <projeto> "Conteúdo" "Hook X" [cta=Ad] [--previa]
$PY $S/mapa.py <projeto> "Conteúdo" "Hook X" [cta=Ad] [--completo] 0:23 0:41
$PY $S/entregar.py <projeto> ["Vídeo final" ...]    # copia para "2. Concluídos/<projeto>/"
$PY $S/limpar.py <projeto>                          # depois de entregar: apaga cópias e caches
```

Transcrever e montar levam alguns minutos: rode em segundo plano e avise ("estou transcrevendo, leva uns 3 minutos").

## Primeira vez (instalação)
1. `checar_ambiente.py`. Se faltar algo, `instalar.py` e espere terminar. Se o Python não existir: no Windows rode você mesmo `winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements` e use `py` em seguida; no Mac rode `xcode-select --install` (abre uma janela: peça para a pessoa clicar em "Instalar" e avisar quando terminar). Se não der, peça para instalar pelo site python.org (Windows: marcar "Add python.exe to PATH") e voltar.
2. `pasta.py`. Diga onde a pasta ficou e se está no Google Drive. Se não estiver, sugira instalar o **Google Drive para computador** (assim a pasta aparece no celular e os vídeos sobem do celular), ou pergunte se a pessoa quer usar outra pasta (`--definir`).
3. Explique o uso em 3 linhas: criar uma pasta com o nome do vídeo dentro de "1. Para editar", colocar os vídeos dentro, e pedir "edita o vídeo <nome>". O pronto aparece em "2. Concluídos".

## A pasta da pessoa

```
Edição de Vídeos IA/
  1. Para editar/
    <Nome do vídeo>/        uma pasta por vídeo
      HOOK A, HOOK B ...    começos diferentes (um vídeo final por hook)
      CONTEUDO              o meio, igual para todos (ou CONTEUDO 1, CONTEUDO 2, em ordem)
      CTA                   o fim (chamada para ação); com CTA CONTEUDO e CTA ANUNCIO sai também a versão "- Ad"
      TAKE ...              imagens de apoio, sem fala importante
  2. Concluídos/
    <Nome do vídeo>/        vídeos prontos
```

Os nomes ajudam mas não são obrigatórios: um arquivo só com tudo junto também serve. Sem padrão, decida pelo texto da transcrição e diga o que entendeu. Pasta em "Para editar" sem par em "Concluídos" = pendente. Se a pessoa mandar um link (Drive, YouTube, .mp4) em vez de usar a pasta, `baixar.py` aceita o link.

## Passo a passo

### 1. Perguntar o tipo de edição (antes de tudo)
Depois de `baixar.py` e `transcrever.py` (para já ter o que sugerir), faça **as 3 perguntas numa mensagem só**, com opções numeradas e a sua sugestão marcada pelo que viu na transcrição e nos nomes dos arquivos:

1. **Como foi gravado?**
   a) Fala corrida, uma vez só: só limpar pausas, erros e repetições.
   b) Vários takes da mesma fala: escolher a melhor tomada de cada frase.
   c) Hooks diferentes + conteúdo + CTA: um vídeo pronto por hook.
2. **Tem imagens de apoio (takes) para entrar por cima da fala?** Se sim, quais arquivos, e se a pessoa tem preferência de momento ("quando eu falar da palestra").
3. **Como quer o resultado?** Só cortes (simples) ou com legenda e frase no topo (completo).

Se a pessoa disser "não sei" ou "você decide", siga a sua sugestão e diga qual foi. Registre as respostas em `edit/project.md`.

### 2. Entender o material
Ler `edit/takes.md` inteiro. Agrupar por conteúdo pelo texto (hook e conteúdo no mesmo arquivo, dois hooks num arquivo, outra tomada do conteúdo com nome errado). Separar os takes de apoio (arquivos TAKE ou sem fala). Se o `transcrever.py` avisar deriva, retranscrever isolado cada trecho usado daquela parte antes de cortar.

### 3. Escolher os trechos (o trabalho de editor)
Montar `hooks`, `body` e `ctas` no `edit/reels.json` (formato em `references/reels-json.md`; editar por Python, não por `sed`), com `palavras.py` para os tempos.

- **Melhor tomada de cada frase**: normalmente a última completa. Sem autocorreção no meio, sem "de novo", "pode ser?", "peraí", "mais uma", "não tô feliz", sem conversa com quem grava. A transcrição pode registrar a gagueira ("No dia-- o dia do vendedor"): começar o trecho depois dela.
- **Fala corrida (tipo a)**: um hook só com o começo, `body` com o resto em ordem; corte só erros, repetições e frases recomeçadas.
- **Corte entre palavras, nunca dentro**. Emenda colada: `energia.py` para achar o vale; vale especialmente na troca hook → corpo.
- **Raciocínio inteiro**: o corpo faz sentido sozinho depois de qualquer hook. Não pule partes da explicação.
- **CTA**: com as duas gravadas, `ctas` com "Conteúdo" e "Ad". Só uma: monte essa. Sem CTA: avise que o vídeo vai terminar sem chamada e pergunte se a pessoa quer gravar uma.
- **Lousa/quadro**: o corpo segue a ordem em que a pessoa escreveu, e cada ponto aparece explicado. Liste os pontos antes de montar.

**Takes de apoio** (se a pessoa quis): `quadros_take.py` para ver cada take e escolher trechos bonitos (sem tremida, sem gente passando na frente). Coloque 1 take a cada 15 a 30 s de vídeo, de 2 a 4 s cada, em momentos em que a imagem combina com a fala, nunca nos primeiros 3 s do hook nem na CTA, e varie os trechos do take. Use `em: [bruto da fala, segundo da palavra]` (vale para todos os hooks). Formato no `scripts/takes.py`.

**Trava:** `checar.py`. REPROVADO (saída 1) = não monta. Se der erro, pare e relate.

### 4. Montar
`montar.py`. Ele já faz snap no silêncio, corte de pausas, velocidade do hook, respiro no fim, fades e os takes de apoio (ver `cortes.py` e `takes.py`); não compensar nos tempos.

### 5. Caçar repetições escondidas
`repeticoes.py`; para cada ponto, ler o "real" e, se repetir, mover o trecho para a última tomada e remontar. O Whisper esconde mais repetição que transcrições pagas: não pule.

### 6. Olhar os quadros
`quadros.py` e **abrir as imagens**. Procurar: leitura de roteiro (olhar para baixo), saída do quadro, conversa de bastidor, roupa/cenário diferente. Trecho lido: trocar por tomada olhando para a câmera. Conferir também 1 quadro de cada take de apoio no vídeo final.

### 7. Conferir
`conferir.py`. Ruído normal: "para/pra", "está/tá", nomes parecidos. **"PALAVRA FALTANDO" bloqueia a entrega**: `energia.py` no bruto entre a palavra anterior e o início do trecho; se houver fala, mover o início e remontar. Se for só diferença de transcrição (a palavra está no áudio do final), dizer isso no relatório.

Checklist, um por um:
- [ ] Nenhuma frase ou palavra repetida (incluindo emenda hook → corpo)
- [ ] Nenhuma palavra cortada no começo ou no fim de trecho
- [ ] Ninguém lendo roteiro nem saindo do quadro
- [ ] Termina com CTA (se houver) e com respiro depois da última palavra
- [ ] Hook no mesmo ritmo do corpo
- [ ] Takes de apoio nos momentos certos, sem tarja preta
- [ ] Um arquivo por hook e por CTA

### 8. Mostrar, entregar e limpar
Relatório curto para a pessoa: nome do vídeo, duração antes e depois, e as decisões que ela pode querer mudar (tomada escolhida, trecho tirado, onde entraram os takes). Todo aviso dos scripts aparece no relatório com o que foi feito; nunca diga "nenhuma palavra cortada" se o conferir mostrou pendência. Peça para ela assistir o arquivo em `final/` (dê o caminho) e **espere o OK**. Com OK: `entregar.py`, diga em qual pasta ficou, registre as decisões em `edit/project.md` e rode `limpar.py`.

**Um vídeo por vez**: monte, confira, entregue e pare para a avaliação antes do próximo.

## Formato completo (com legenda)
1. Só depois do simples aprovado e conferido (o `completo.py` usa a retranscrição do `conferir.py`).
2. Propor 2 ou 3 frases para o topo (regras em `references/formato-completo.md`) e gravar a escolhida em `topo`.
3. `completo.py ... --previa` e mostrar a legenda (`final/<nome> - legenda.txt`). Correções em `legenda_corrige`.
4. Imagens de prova (opcional): salvar em `<projeto>/provas/` e listar em `provas` com os tempos do vídeo simples. CTA em caixa: `cta_caixa`.
5. `completo.py ...` (sem `--previa`), conferir alguns quadros (topo, legenda, takes, fim) e a duração, mostrar e esperar o OK.

## Ajustes por lista
Quando mandarem ajustes pelo tempo do vídeo editado ("0:12 começar meio segundo antes; 0:31 cortar a frase repetida"):
1. `mapa.py <projeto> "Conteúdo" "Hook X" [cta=Ad] [--completo] 0:12 0:31` mostra, para cada tempo, o trecho do reels.json, o tempo no bruto e as palavras em volta.
2. Aplicar **todos** os ajustes no `reels.json` (por Python), conferindo cada um com `palavras.py`/`energia.py`.
3. `montar.py` uma vez, `conferir.py`, e o `completo.py` se o ajuste era no completo.
4. Entregar o vídeo novo com a lista do que foi feito em cada tempo.

## Quando apontam um problema num vídeo editado
Achar a causa no bruto (`energia.py`, `palavras.py`, `repeticoes.py`, `quadros.py`) antes de mexer, corrigir no `reels.json`, remontar só aquele conteúdo, conferir e entregar por cima (com OK). Se a causa pode existir em outros vídeos, verificar todos.

## Se algo der errado
- Erro de instalação ou de pacote: `checar_ambiente.py`, depois `instalar.py`. Diga em uma frase o que faltou.
- Vídeo não aparece na pasta: o Google Drive ainda está sincronizando; peça para esperar o upload terminar.
- Transcrição muito errada (sotaque, barulho): rodar de novo com `WHISPER_MODELO=medium` (mais lento, mais preciso), apagando `edit/transcripts/`.
- Pouco espaço no disco: `limpar.py` nos projetos já entregues.
