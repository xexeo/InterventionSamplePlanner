<!-- File version: 2.2; date: 2026-05-17 -->

# Changelog

## 2.2 - 2026-05-17

### Adicionado

- Análise reversa apenas com tamanho da amostra para fluxos de estudo realizado.
- Linhas de capacidade que relatam efeitos mínimos detectáveis para combinações comuns de `p`/alpha e poder.
- Linhas reversas que relatam poder aproximado para tamanhos de efeito comuns e limiares aproximados de alpha necessários para alvos comuns de efeito/poder.
- Tabelas de cenários de alocação quando estudos realizados de dois grupos informam apenas a amostra total.

### Alterado

- O modo de estudo realizado não exige mais efeito observado quando o usuário quer avaliar apenas o que o tamanho da amostra alcançada consegue sustentar.
- As tabelas de resultado Tkinter e web agora exibem linhas de capacidade da amostra na aba `Plano / Benchmarks`.
- O executável Windows foi regerado com `explanations.json` e `web_static` empacotados.

## 2.1 - 2026-05-12

### Adicionado

- Tabela própria `Plano / Benchmarks` para avaliação de estudo realizado.
- Exportação de relatório em HTML e PDF diretamente pelo aplicativo Tkinter.
- Avaliação exata de McNemar para resultados binários pareados antes/depois em um grupo.
- Valores-p exatos de Fisher para resultados binários de dois grupos quando as contagens de eventos são informadas.
- Capturas de tela em `docs/screenshots`.
- Arquivo de checksum SHA256 para o executável Windows gerado para release.
- Helper para capturar telas usadas na documentação de release.
- API REST em Flask e cliente web estático como segunda interface.
- Blueprint do Render e workflow do GitHub Actions disparado por tag.
- Guia detalhado de deploy no Render.
- Salvamento e carregamento de JSON no navegador para arquivos locais de estudo, sem banco de dados.

### Alterado

- Metadados de versão agora informam `ISP v2.1`.
- Sugestões de estudo realizado agora explicam melhor valores-p exatos, resultados com pouco poder, lacunas contra plano anterior e lacunas contra benchmarks.
- Pré-teste/pós-teste com controle agora explica melhor a aproximação em estilo ANCOVA.
- Desenhos com clusters agora recebem alertas mais fortes sobre planejamento e análise no nível do cluster.
- Documentação, schema JSON, cobertura de exemplos, READMEs e notas de desenvolvimento/build foram atualizados para v2.1.
- O projeto agora documenta duas interfaces suportadas: desktop Tkinter e web Flask.
- O cliente web agora espelha o fluxo de liberação de faixas recomendadas usado pelo aplicativo desktop.

### Corrigido

- Resultados binários de dois grupos com amostra pequena ou células esparsas agora usam o valor-p exato de Fisher como valor-p reportado.
- Resultados binários pareados em um grupo não exigem mais um tamanho de efeito observado contínuo.
