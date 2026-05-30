<!-- File version: 2.4; date: 2026-05-30 -->

# Intervention Sample Planner

O Intervention Sample Planner, ou `ISP`, é uma API local em Python com duas interfaces: um aplicativo desktop em Tkinter e um aplicativo web em Flask para planejar ou avaliar estudos de intervenção em processos humanos, como aprendizagem, treinamento, usabilidade e melhoria de fluxos de trabalho.

A versão `2.4` oferece:

- `Dois grupos independentes`
- `Pré-teste/pós-teste com grupo de controle`
- `Pré-teste/pós-teste com um grupo`
- `Questionário pós-intervenção com um grupo`
- `Questionário pós-intervenção estratificado`
- `Planejar amostra necessária`
- `Avaliar resultado alcançado`
- três escolhas logo no início: planejar um estudo, analisar um estudo realizado ou comparar um estudo realizado com um plano anterior
- carregamento de um plano JSON salvo no fluxo de comparação com estudo realizado
- faixas recomendadas com liberação explícita
- explicações carregadas de um arquivo JSON separado
- uma aba de sugestões com orientações metodológicas e alertas
- uma tabela própria `Plano / Benchmarks` para verificações de estudo realizado
- análise reversa apenas com tamanho da amostra para estudos realizados, com tabelas de capacidade quando não há efeito observado
- planejamento e avaliação de questionários de opinião com escalas Likert, estrelas e notas numéricas limitadas
- planejamento e avaliação de questionários de opinião estratificados para representação demográfica
- exportação direta de relatório em texto, HTML ou PDF pelo aplicativo
- avaliação exata de McNemar para desfechos binários pareados em um grupo
- valores-p exatos de Fisher para resultados binários de dois grupos com amostras pequenas ou células esparsas
- notas mais claras sobre aproximação no espírito de ANCOVA em pré-teste/pós-teste com controle e sobre desenho com clusters
- endpoints REST para cálculo e exportação de relatórios
- uma interface no navegador preparada para deploy no Render sem banco de dados e sem etapa de build com Node.js

## Capturas de tela

![Início do wizard](docs/screenshots/wizard.png)

![Tabela de plano e benchmarks](docs/screenshots/plan_benchmarks.png)

## O que ele faz

O aplicativo ajuda a responder perguntas como:

- Quantos participantes válidos são necessários para comparar intervenção e controle?
- Quantas pessoas precisam completar tanto o pré-teste quanto o pós-teste?
- Quantas pessoas devem ser convidadas se parte delas não iniciar ou não terminar?
- Se um estudo já foi executado, que valor-p aproximado e que poder alcançado correspondem ao resultado observado?
- Se apenas o tamanho da amostra alcançada é conhecido, que efeitos essa amostra conseguiria detectar sob padrões comuns de valor-p e poder?
- Para um questionário de opinião pós-intervenção, quantos respondentes válidos são necessários para dizer algo como "com 95% de confiança, pelo menos X% dos usuários deram uma resposta favorável"?
- Para um questionário de opinião estratificado, quantas respostas válidas são necessárias em cada classe demográfica para que o resultado não seja dominado por um só tipo de respondente?

A implementação atual é mais forte para planejamento transparente e interpretação educativa. O planejamento binário é suportado em `Dois grupos independentes`; a avaliação binária de estudo realizado é suportada em `Dois grupos independentes` e em casos pareados de pré/pós com um grupo. Questionários pós-intervenção, inclusive estratificados, são tratados como problemas de estimação descritiva, não como testes causais.

## Caminhos de pesquisa típicos

### 1. Dois grupos independentes

Use quando um grupo recebe a intervenção e outro grupo não recebe. Exemplo: um pesquisador da área de jogos educacionais quer testar se usar Uno junto com uma aula melhora o entendimento de maior e menor em um pós-teste, comparado com apenas aula.

### 2. Pré-teste/pós-teste com grupo de controle

Use quando os dois grupos são medidos antes e depois. Exemplo: um grupo faz um pré-teste, joga Uno, recebe uma aula curta e faz um pós-teste; o grupo controle faz o mesmo pré-teste e pós-teste, mas recebe apenas a aula.

### 3. Pré-teste/pós-teste com um grupo

Use quando os mesmos participantes são medidos antes e depois e não existe grupo de controle. Exemplo: um pesquisador quer uma primeira estimativa do efeito de aprendizagem de jogar Uno entre um pré-teste e um pós-teste antes de executar um ensaio controlado.

### 4. Questionário pós-intervenção com um grupo

Use quando os participantes respondem apenas a um questionário de opinião ou experiência após usar a intervenção. Exemplo: depois de uma sessão com um jogo de aprendizagem, os alunos respondem a um questionário Likert no estilo MEEGA+ sobre usabilidade, confiança, diversão e aprendizagem percebida. O `ISP` pode planejar o número de respondentes válidos necessário para um intervalo de confiança da proporção de respostas favoráveis ou da média da escala, e pode avaliar um histograma realizado como `{"1": 2, "2": 4, "3": 10, "4": 18, "5": 26, "NA": 3}`.

### 5. Questionário pós-intervenção estratificado

Use quando o questionário de opinião deve representar classes demográficas, não apenas as pessoas que responderam primeiro. Exemplo: depois de um jogo de aprendizagem, o pesquisador quer respostas de crianças nas faixas `8-10`, `11-13` e `14-16`, com alvos baseados na composição populacional ou com um mínimo por faixa. O `ISP` planeja respostas válidas, participantes iniciados e convites por estrato, e avalia JSON realizado como `{"idade_8_10": {"counts": {"4": 12, "5": 18, "NA": 2}}, "idade_11_13": {"valid_n": 40, "favorable": 31}}`.

## Fluxos de estudo realizado e problema inverso

`Analisar um estudo realizado` e `Comparar estudo realizado com o plano` são os fluxos inversos. Em vez de perguntar apenas quantos participantes são necessários, eles perguntam o que a amostra alcançada, a alocação, o efeito observado e os benchmarks implicam.

Quando há efeito observado ou contagens binárias de eventos, eles relatam quantidades aproximadas como:

- efeito observado informado
- taxas binárias observadas quando as contagens de eventos são informadas
- estatística z aproximada
- valor-p aproximado
- poder alcançado aproximado
- lacunas para benchmarks convencionais como `p < 0.05`, `p < 0.10`, `power >= 80%` e `power >= 90%`

Quando apenas o tamanho da amostra alcançada está disponível, a resposta não é única. O `ISP` passa a retornar uma tabela de capacidade da amostra. Ela mostra efeitos mínimos detectáveis para combinações comuns, como `p < 0.05` com `80%` de poder, poder para tamanhos de efeito tradicionais como `d = 0.20`, `0.50` e `0.80`, e o limiar aproximado de valor-p que seria necessário para alvos comuns de efeito e poder. Em estudos de dois grupos com apenas amostra total, a tabela também avalia alocações comuns como `1:1`, `2:1` e `1:2`.

Se existir um plano anterior, use `Comparar estudo realizado com o plano`. Você pode digitar a amostra planejada manualmente ou clicar em `Carregar plano anterior` e escolher um JSON salvo de uma execução de planejamento. O relatório então informa se a amostra válida alcançada atingiu o plano e quantos participantes válidos ficaram faltando.

## Tamanho de efeito em linguagem simples

Tamanho de efeito é a entrada mais difícil para muitos usuários, então o `ISP v2.4` trata esse ponto explicitamente.

- Em `Dois grupos independentes`, o tamanho de efeito contínuo é a diferença padronizada entre grupos.
- Em `Pré-teste/pós-teste com grupo de controle`, ele é a diferença padronizada de ganho, ou o efeito no pós-teste depois de considerar a linha de base.
- Em `Pré-teste/pós-teste com um grupo`, ele é a mudança média padronizada nos mesmos participantes.
- Em `Questionário pós-intervenção com um grupo`, o alvo principal de planejamento normalmente não é tamanho de efeito. É o nível de confiança e a margem de erro desejada para uma proporção de respostas favoráveis ou para a média do escore.
- Em `Questionário pós-intervenção estratificado`, o mesmo alvo de precisão do questionário é dividido entre estratos, e a qualidade da representação é verificada com participações observadas, metas por estrato e pesos opcionais.

Valores tradicionais como `0,2`, `0,5` e `0,8` podem servir como orientação, mas o melhor tamanho de efeito é o menor efeito que realmente seria significativo no estudo real.

## Explicações e recomendações

O aplicativo lê explicações longas das variáveis e faixas recomendadas a partir de:

[explanations.json](intervention_sample_planner/explanations.json)

Esse JSON foi pensado para permanecer alinhado ao manual operacional e ao manual educacional.

## Execução local

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Execução local da interface web

```powershell
python -m pip install -r requirements.txt
python -m flask --app intervention_sample_planner.web_app run
```

Depois abra `http://127.0.0.1:5000`.

## Construção do executável

Veja:

- [build_pt.md](build_pt.md)
- [developers_pt.md](developers_pt.md)
- [versions_pt.md](versions_pt.md)
- [docs/render_deploy_pt.md](docs/render_deploy_pt.md)

O checksum SHA256 do executável de release fica em `release/checksums.sha256`. Executável Windows atual:

```text
6018D9075B643C9706A11B83FF1B66CD5CE28CECF394E887AD7185D80EC1FA7D  dist/InterventionSamplePlanner.exe
```

## Documentação principal

- [theoryintroduction_pt.md](theoryintroduction_pt.md)
- [manual.tex](docs/educational_manual/manual.tex)
- [useofAI_pt.md](useofAI_pt.md)
- [disclaimer_pt.md](disclaimer_pt.md)
