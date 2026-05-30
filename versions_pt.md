<!-- File version: 2.4; date: 2026-05-30 -->

# Histórico de Versões

## 2.4

- adiciona `Questionario pos-intervencao estratificado` para pesquisas de opiniao com metas de representacao demografica
- adiciona planejamento estratificado por participacao populacional, alocacao igual, minimo por estrato ou metas manuais por estrato
- adiciona avaliacao estratificada de estudo realizado com participacoes observadas, razoes de representacao, pesos opcionais, proporcoes favoraveis e status
- atualiza Tkinter, web, REST, schema, testes, textos de ajuda, READMEs, changelogs e resumo teorico operacional para o caminho de survey estratificado
- atualiza os metadados do aplicativo para `ISP v2.4`

## 2.3

- adiciona `Questionário pós-intervenção com um grupo` para estudos apenas de opinião depois de uma intervenção
- adiciona planejamento por proporção de respostas favoráveis com nível de confiança e margem de erro
- adiciona planejamento por média do questionário com desvio padrão esperado e margem de erro da média
- adiciona avaliação de questionário realizado a partir de histogramas de respostas, contagens favoráveis ou resumos de média/desvio padrão
- adiciona intervalos de confiança de Wilson para proporções favoráveis e intervalos de confiança para médias de escores de questionário
- atualiza Tkinter, web, REST, schema, testes, textos de ajuda, READMEs e manual educacional para o caminho de questionário
- atualiza os metadados do aplicativo para `ISP v2.3`

## 2.2

- adiciona análise reversa apenas com tamanho da amostra para fluxos de estudo realizado
- adiciona tabelas de capacidade que relatam efeitos mínimos detectáveis para padrões comuns de valor-p e poder
- adiciona linhas reversas para poder sob tamanhos de efeito comuns e limiares aproximados de alpha sob alvos comuns de efeito/poder
- adiciona tabelas de cenários de alocação quando um estudo realizado de dois grupos informa apenas a amostra total
- atualiza as tabelas de resultado Tkinter e web para mostrar linhas de capacidade da amostra em `Plano / Benchmarks`
- recompila o executável Windows com explicações JSON e arquivos estáticos web empacotados

## 2.1

- adiciona uma tabela própria `Plano / Benchmarks` para comparação com plano anterior e limiares comuns
- adiciona exportação direta de relatório pelo aplicativo desktop em HTML e PDF, além do relatório de texto
- adiciona avaliação exata de McNemar para resultados binários pareados em um grupo
- adiciona valores-p exatos de Fisher para resultados binários de dois grupos com amostras pequenas ou células esparsas
- esclarece a interpretação em estilo ANCOVA para pré-teste/pós-teste com grupo de controle
- amplia orientações sobre estudos com clusters e ajuste dos benchmarks quando suposições de cluster são informadas
- atualiza `explanations.json`, o schema JSON, testes, capturas de tela, READMEs e documentação de build/desenvolvimento
- adiciona capturas de tela de release em `docs/screenshots`
- adiciona suporte a checksum SHA256 para o executável Windows gerado para release
- adiciona interface web Flask e API REST como segunda interface sobre o mesmo motor de cálculo
- adiciona configuração de deploy no Render e workflow do GitHub Actions que publica commits taggeados
- adiciona documentação detalhada de deploy no Render
- adiciona salvamento/carregamento local de JSON no navegador e verificação de liberação de faixas recomendadas no cliente web

## 2.0

- adiciona tres escolhas explicitas de fluxo: planejar um estudo, analisar um estudo realizado e comparar um estudo realizado com um plano anterior
- adiciona carregamento de planos salvos em JSON para a comparacao com o plano
- adiciona contagens binarias de eventos, taxas observadas, lacunas de benchmark e estimativas de amostra faltante para limiares comuns de valor-p e poder

- adiciona a escolha do caminho de pesquisa no início do wizard
- adiciona `Pré-teste/pós-teste com grupo de controle`
- adiciona `Pré-teste/pós-teste com um grupo`
- adiciona o fluxo inverso `Avaliar resultado alcançado`
- adiciona faixas recomendadas com liberação explícita
- move explicações longas das variáveis para `intervention_sample_planner/explanations.json`
- adiciona a aba `Sugestões`
- expande a API, o schema, os testes e a documentação operacional
- atualiza o manual educacional e os scripts de build do manual para limpeza com LuaLaTeX

## 1.0

- API local inicial e aplicativo Tkinter inicial
- suporte a dois grupos independentes
- suporte a desfechos contínuos e binários
- suporte a correções por atrito, resposta, população finita e cluster
- suporte a análise de sensibilidade e configuração em JSON
