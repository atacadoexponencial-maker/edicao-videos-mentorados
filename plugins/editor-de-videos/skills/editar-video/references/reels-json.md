# Formato do edit/reels.json

Um objeto por conteúdo. Chaves começando com `_` são comentários (ignoradas pelos scripts).

```json
{
  "_nota": "qualquer observação",
  "Ad3 teto do faturamento": {
    "hooks": {
      "Hook A": [["Ad3_HOOK_A_CONTEUDO", 0.04, 2.97], ["Ad3_HOOK_A_CONTEUDO", 13.62, 16.58]],
      "Hook B": [["Ad3_HOOK_B_HOOK_C", 0.00, 4.01]]
    },
    "body": [
      ["Ad3_HOOK_A_CONTEUDO", 28.83, 33.38],
      ["Ad3_HOOK_A_CONTEUDO", 38.17, 42.47]
    ]
  },
  "Caixinha como se destacar": {
    "speed": 1.15,
    "hooks": {"Hook": [["Caixinha_como_se_destacar_Hook_Conteudo", 0.65, 6.59]]},
    "body": [["Caixinha_como_se_destacar_Hook_Conteudo", 18.16, 24.86]]
  }
}
```

- Cada trecho é `[bruto sem extensão, início, fim]` em segundos do bruto, com início = começo da primeira palavra e fim = fim da última palavra (tempos da transcrição). O `montar.py` ajusta para o silêncio real.
- Trechos do corpo podem vir de brutos diferentes (ex.: CTA emprestado de outro vídeo do mesmo dia).
- Um hook só → arquivo final com o nome do conteúdo. Vários → "Conteúdo - Hook X.mp4".
- `speed` opcional (padrão 1x; só mudar se a pessoa pedir). A velocidade do hook é calculada sozinha.
- `ctas` opcional: `{"Conteúdo": [[bruto, ini, fim]], "Ad": [[...]]}`. "Conteúdo" gera o nome-base; "Ad" gera "... - Ad".
- `_mesmo_conteudo` opcional: lista de brutos de temas diferentes que são a mesma lousa/conteúdo (libera o `checar.py`).
- `takes` opcional: imagens de apoio por cima da fala, com a voz por baixo. Formato no cabeçalho do `scripts/takes.py`:
  `"takes": [{"take": "TAKE_palestra", "de": 4.5, "dur": 3.0, "em": ["LOUSA_1", 95.2]}]`.
- Campos do formato completo (`topo`, `topo_seg`, `legenda_corrige`, `provas`, `cta_caixa`): ver o cabeçalho do `completo.py` e `formato-completo.md`.
- Editar o arquivo por Python (`json.load`/`json.dump`), não por `sed`: a formatação muda e a substituição falha em silêncio.
