<!-- File version: 2.4; date: 2026-05-30 -->

# Changelog

## 2.4 - 2026-05-30

### Adicionado

- Tipo de estudo de questionario pos-intervencao estratificado para pesquisas de opiniao que precisam de representacao demografica.
- Caminho no wizard, campos de configuracao, saida REST, schema, textos de ajuda e testes para survey estratificado.
- Linhas de planejamento por estrato com participacao populacional, alvo valido, participantes para iniciar, convites e pesos opcionais.
- Avaliacao de resultado por estrato com participacao observada, razao de representacao, proporcao favoravel e status.

### Alterado

- Metadados de versao agora informam `ISP v2.4`.
- Interfaces Tkinter e web agora expõem as mesmas variaveis de survey estratificado e mostram linhas estratificadas nas tabelas de resultado.
- Sugestoes agora alertam sobre estratos pequenos, sub-representacao e pesos instaveis.

## 2.3 - 2026-05-18

### Adicionado

- Tipo de estudo de questionário pós-intervenção com um grupo para pesquisas de opinião no estilo MEEGA+, Likert, estrelas e escalas numéricas limitadas.
- Planejamento de questionário por proporção de respostas favoráveis usando nível de confiança e margem de erro.
- Planejamento de questionário por média da escala usando nível de confiança, desvio padrão esperado e margem de erro da média.
- Avaliação de questionário realizado a partir de histogramas JSON, contagens favoráveis ou média mais desvio padrão.
- Intervalos de confiança de Wilson para proporções favoráveis e intervalos descritivos para médias de escores de questionário.
- Orientação específica de questionários no Tkinter, interface web, saída REST, schema, explicações, testes, READMEs e manual educacional.

### Alterado

- Metadados de versão agora informam `ISP v2.3`.
- Fluxos de questionário escondem entradas de valor-p/poder quando a tarefa relevante é estimação descritiva, não teste causal de hipótese.
- Sugestões agora alertam quando um questionário pós-intervenção está sendo usado como evidência de opinião dos usuários, não como evidência de efeito da intervenção.

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
