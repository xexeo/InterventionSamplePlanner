<!-- File version: 2.4; date: 2026-05-30 -->

# Resumo Operacional da Teoria para o ISP v2.4

## Fluxos atuais do wizard

O primeiro passo do wizard agora pergunta a tarefa pratica:

- `Planejar um estudo`: estima a amostra necessaria antes da coleta.
- `Analisar um estudo realizado`: calcula valor-p aproximado, poder alcancado e lacunas de benchmark quando há efeito observado, ou uma tabela de capacidade quando só há tamanho da amostra.
- `Comparar estudo realizado com o plano`: faz a analise do resultado observado e compara a amostra valida alcancada com um plano anterior. O plano pode ser digitado manualmente ou carregado de um JSON salvo.

Na comparacao com plano, o app usa os campos `planned_control_n`, `planned_intervention_n`, `planned_total_n`, `planned_effect_size`, `planned_alpha` e `planned_power`. Para desfechos binarios, pode usar `observed_control_events` e `observed_intervention_events` para calcular as taxas observadas.

Este manual operacional explica como usar o `ISP v2.4` de forma prática. Ele é mais curto que o manual educacional em LaTeX, mas foi escrito para apoiar decisões reais dentro do aplicativo.

## 1. Capacidades atuais na versão 2.4

O `ISP v2.4` suporta o fluxo original de planejamento com dois grupos, os fluxos de estudo realizado e os fluxos de questionário de opinião pós-intervenção:

- `Dois grupos independentes`
- `Pré-teste/pós-teste com grupo de controle`
- `Pré-teste/pós-teste com um grupo`
- `Questionário pós-intervenção com um grupo`
- `Questionário pós-intervenção estratificado`
- `Planejar amostra necessária`
- `Avaliar resultado alcançado`
- `Comparar estudo realizado com o plano`
- faixas recomendadas com liberação explícita
- explicações em `intervention_sample_planner/explanations.json`
- uma aba dedicada de `Sugestões`
- análise reversa de capacidade quando apenas o tamanho da amostra alcançada está disponível
- planejamento de precisão e avaliação de questionários realizados para escalas Likert, estrelas e notas numéricas limitadas
- planejamento e avaliação de questionários estratificados para representação demográfica

## 2. Comece escolhendo o caminho de pesquisa

A primeira decisão do wizard não é mais o tipo de desfecho. Agora é o caminho de pesquisa.

### Caminho A. Dois grupos independentes

Use quando pessoas diferentes pertencem à intervenção e ao controle, e a afirmação principal é sobre uma diferença entre grupos.

Exemplo em jogos educacionais:
Um pesquisador da área de jogos educacionais pretende verificar se o uso do jogo Uno ajuda as crianças a compreender os conceitos de maior e menor. Um grupo joga Uno com mediação e depois recebe uma aula curta. Outro grupo recebe apenas a aula. Os dois grupos fazem um teste final, e a comparação principal é entre os grupos.

### Caminho B. Pré-teste/pós-teste com grupo de controle

Use quando os dois grupos são medidos antes e depois.

Exemplo em jogos educacionais:
Um pesquisador deseja examinar se o Uno altera os conceitos de comparação matemática além da instrução comum. As crianças dos dois grupos fazem um pré-teste. O grupo de intervenção joga Uno e recebe uma aula curta. O grupo de controle recebe apenas a aula. Os dois grupos fazem o mesmo pós-teste. Neste caminho, o pré-teste ajuda a controlar diferenças iniciais e melhora a precisão.

### Caminho C. Pré-teste/pós-teste com um grupo

Use quando não existe grupo de controle e os mesmos participantes são medidos antes e depois.

Exemplo em jogos educacionais:
Um pesquisador quer uma primeira estimativa de se jogar Uno entre duas medições melhora a compreensão de maior e menor. As mesmas crianças fazem um pré-teste, jogam Uno em uma sessão guiada e depois fazem um pós-teste. Esse desenho pode ser útil como piloto, mas é mais fraco para inferência causal porque a mudança ao longo do tempo pode vir de fatores diferentes do jogo.

### Caminho D. Questionário pós-intervenção com um grupo

Use quando os participantes respondem apenas a um questionário de opinião, experiência, usabilidade ou aprendizagem percebida depois da intervenção. Isso é comum em avaliações de jogos educacionais no estilo MEEGA+, questionários Likert, avaliações por estrelas e formulários de usabilidade pós-uso.

Exemplo em jogos educacionais:
Depois de uma sessão guiada com Uno, um pesquisador pergunta aos estudantes se a atividade foi fácil de aprender, divertida, útil e se ajudou a entender maior e menor. Não existe pré-teste nem grupo de controle nesse caminho. O resultado pode sustentar uma afirmação descritiva como "com 95% de confiança, pelo menos cerca de 70% dos respondentes válidos deram uma resposta favorável", mas não prova que o Uno causou aprendizagem.

### Caminho E. Questionário pós-intervenção estratificado

Use quando o mesmo questionário de opinião pós-intervenção deve representar classes demográficas. Um estrato é uma classe planejada, como faixa etária, tipo de escola, região, experiência anterior ou gênero. O objetivo não é provar causalidade; é evitar que uma afirmação descritiva seja dominada pelos respondentes mais fáceis de recrutar.

Exemplo em jogos educacionais:
Depois de uma sessão guiada com Uno, um pesquisador quer que o questionário de opinião represente crianças de `8-10`, `11-13` e `14-16` anos. Se a população tem 30%, 40% e 30% nessas faixas, a alocação proporcional segue essas participações. Se o pesquisador também quer que cada faixa seja visível, a opção de mínimo por estrato pode exigir pelo menos 30 respostas válidas por faixa. No fluxo de estudo realizado, o aplicativo verifica se cada faixa ficou abaixo da meta, sub-representada ou super-representada.

## 3. Depois escolha o tipo de execução

### Planejar amostra necessária

Use quando o estudo ainda não foi executado e você quer estimar:

- participantes válidos analisáveis necessários
- participantes que precisam iniciar
- participantes que precisam ser convidados

### Avaliar resultado alcançado

Use quando o estudo ou piloto já existe e você quer estimar o que a amostra alcançada e o efeito observado implicam.

Esse fluxo inverso ajuda a responder:

- O estudo teve pouco poder?
- Que valor-p aproximado corresponde ao efeito observado?
- Se o efeito desejado não apareceu, que efeito foi realmente observado?

## 4. Faixas recomendadas e por que elas existem

O aplicativo agora verifica faixas recomendadas ou típicas. Você pode explicitamente permitir um valor fora da faixa, mas o aplicativo registrará isso e mostrará novamente na aba `Sugestões`.

| Variável | Faixa recomendada ou típica | Valores tradicionais comuns | Por que essa faixa é usada |
|---|---|---|---|
| `alpha` | `0.01` a `0.10` | `0.05`, `0.01` | Fora dessa faixa, o padrão de evidência se torna incomum e deve ser justificado. |
| `power` | `0.80` a `0.95` | `0.80`, `0.90` | Abaixo de `0.80` costuma ser fraco para trabalho confirmatório; acima de `0.95` pode ficar impraticável. |
| `primary_comparisons` | `1` a `10` | `1`, `2`, `3` | Muitas comparações primárias geralmente indicam que a pergunta de pesquisa precisa ser estreitada. |
| `allocation_ratio` | `0.5` a `2.0` | `1.0` | Forte desbalanceamento costuma desperdiçar informação, salvo justificativa operacional. |
| `effect_size_d` | `0.10` a `1.20` | `0.20`, `0.50`, `0.80` | Efeitos muito pequenos podem exigir amostras enormes; efeitos muito grandes não devem ser assumidos sem evidência. |
| `pre_post_correlation` | `0.30` a `0.80` | `0.50`, `0.60` | É uma faixa comum para muitas medidas educacionais e de usabilidade. |
| `response_rate` | `0.40` a `1.00` | `0.60`, `0.80`, `0.90` | Valores baixos tornam o recrutamento frágil. |
| `completion_rate` | `0.70` a `1.00` | `0.85`, `0.90`, `0.95` | Valores menores sinalizam risco de atrito. Em medidas repetidas, conclusão significa completar ambas as medições. |
| `usable_data_rate` | `0.80` a `1.00` | `0.90`, `0.95`, `0.98` | Valores baixos geralmente indicam problema na coleta, não apenas de tamanho amostral. |
| `extra_buffer_rate` | `0.00` a `0.20` | `0.00`, `0.05`, `0.10` | Reservas pequenas são comuns; reservas grandes podem indicar suposições fracas. |
| `cluster_average_size` | `1` a `50` | `1`, `20`, `30` | Clusters maiores tornam o ICC muito mais importante. |
| `intraclass_correlation` | `0.00` a `0.20` | `0.01`, `0.05`, `0.10` | ICCs pequenos são comuns, mas mesmo `0.05` pode inflar muito a amostra necessária. |
| `survey_expected_proportion` | `0.30` a `0.90` | `0.50`, `0.70`, `0.80` | `0.50` é conservador para planejamento por margem de erro; valores maiores devem vir de piloto ou evidência anterior. |
| `survey_margin_of_error` | `0.03` a `0.15` | `0.05`, `0.10` | Questionários de opinião muitas vezes relatam precisão em pontos percentuais. Margens menores exigem muito mais respondentes. |
| `survey_favorable_threshold` | dentro da escala | `4` em escala de 1 a 5 | O limiar deve corresponder ao significado verbal da escala, como "concordo" ou melhor. |
| `survey_mean_margin_of_error` | `0.05` a `1.00` ponto da escala | `0.20`, `0.30`, `0.50` | A precisão da média deve ser pequena o bastante para importar na escala, mas viável para a amostra esperada. |
| `stratified_min_per_stratum` | `10` a `100` | `20`, `30`, `50` | Estratos muito pequenos geram porcentagens instáveis; mínimos grandes podem inviabilizar a coleta. |
| `stratified_target_total` | em branco ou total viável | em branco, `100`, `200`, `400` | Deixe em branco quando a precisão deve determinar o total; informe um valor quando a amostra viável já está fixada. |

## 5. A variável difícil: tamanho de efeito

Tamanho de efeito não é um número decorativo. É o menor efeito que importaria o bastante para justificar a intervenção.

### 5.1 Em dois grupos independentes

Para desfechos contínuos, `effect_size_d` é a diferença padronizada entre grupos. Uma interpretação tradicional é:

- `0.2`: pequeno
- `0.5`: médio
- `0.8`: grande

Esses valores são apenas âncoras aproximadas. Se um teste de aprendizagem tem desvio padrão combinado de `10` pontos e uma melhora de `5` pontos já justificaria usar a intervenção, então:

`d = 5 / 10 = 0.5`

### 5.2 Em pré-teste/pós-teste com controle

Aqui a pergunta costuma ser sobre a diferença de ganho. O grupo de intervenção pode melhorar mais do que o grupo de controle entre o pré-teste e o pós-teste.

No exemplo do Uno:
- os dois grupos começam com pré-testes parecidos
- o grupo de intervenção joga Uno e depois recebe uma aula curta
- o grupo de controle recebe apenas a aula curta
- o efeito de interesse é o quanto o grupo de intervenção melhora a mais

Na prática, `effect_size_d` deve representar a menor diferença padronizada de ganho que importaria.

### 5.3 Em pré-teste/pós-teste com um grupo

Não há grupo de controle, então o efeito é a mudança padronizada nos mesmos participantes.

Isso é útil para pilotos, aprendizado em usabilidade ou inovação inicial em sala de aula. Mas a interpretação é mais fraca porque a melhora pode refletir prática, familiaridade com o teste, maturação ou ensino comum.

### 5.4 Em pesquisa de opinião ou usabilidade apenas depois

Às vezes existe apenas um questionário após exposição a um sistema, jogo ou aula. Em `one_group_post_survey`, o aplicativo não pede `effect_size_d`, porque a saída principal não é uma comparação causal. A decisão prática normalmente é a precisão desejada para uma afirmação descritiva.

Por exemplo:
- se concordância é medida em uma escala Likert de 1 a 5
- e os escores `4` e `5` significam respostas favoráveis
- e o pesquisador quer uma margem de erro de cerca de `0.10`

então a pergunta de planejamento é quantos respondentes válidos são necessários para que o intervalo de confiança ao redor da proporção favorável seja estreito o suficiente. Se o pesquisador preferir relatar uma média, o aplicativo usa o desvio padrão esperado e a margem de erro desejada para a média.

Esse caminho não deve ser interpretado como "a intervenção funcionou". Ele sustenta afirmações sobre o que os respondentes relataram depois da intervenção.

## 6. Números tradicionais e por que aparecem tanto

Esses valores aparecem no software porque são comuns em pesquisa real:

- `alpha = 0.05`
- `power = 0.80`
- `power = 0.90`
- `effect_size_d = 0.20, 0.50, 0.80`
- `completion_rate = 0.85` ou `0.90`
- `usable_data_rate = 0.95`
- `ICC = 0.05`
- `survey_margin_of_error = 0.05` ou `0.10`
- `survey_expected_proportion = 0.50` quando não houver uma estimativa anterior melhor

Eles são comuns porque muitas vezes são práticos, não porque sejam obrigatórios.

## 7. Exemplos operacionais

### Exemplo 1. Uno com grupo de controle e comparação no pós-teste

Cenário:
Um pesquisador da área de jogos educacionais pretende verificar se o uso do Uno ajuda as crianças a compreenderem maior e menor. O grupo de intervenção joga Uno com mediação e depois recebe uma aula curta. O grupo de controle recebe apenas a aula. Os dois grupos fazem um teste final. O pesquisador espera que uma diferença padronizada relevante seja `0.5`.

Escolhas no wizard:

- caminho: `Dois grupos independentes`
- tipo de execução: `Planejar amostra necessária`
- desfecho: `Contínuo`
- tamanho de efeito: `0.5`
- alpha: `0.05`
- power: `0.80`
- razão de alocação: `1`
- completion rate: `0.90`
- usable data rate: `0.95`

Por que esse wizard:
A afirmação principal é uma diferença entre grupos depois da intervenção.

### Exemplo 2. Uno com pré-teste/pós-teste e controle

Cenário:
Um pesquisador quer um desenho de aprendizagem mais forte. Os dois grupos fazem um pré-teste. O grupo de intervenção depois joga Uno e participa de uma aula curta. O grupo de controle participa apenas da aula curta. Os dois grupos fazem o mesmo pós-teste. O pesquisador espera correlação pré/pós de aproximadamente `0.60` e quer detectar uma diferença padronizada de ganho de `0.4`.

Escolhas no wizard:

- caminho: `Pré-teste/pós-teste com grupo de controle`
- tipo de execução: `Planejar amostra necessária`
- desfecho: `Contínuo`
- tamanho de efeito: `0.4`
- correlação pré/pós: `0.60`
- alpha: `0.05`
- power: `0.80`
- completion rate: `0.85`

Por que esse wizard:
As mesmas crianças são medidas duas vezes, mas ainda existe grupo de controle.

### Exemplo 3. Uno com apenas um grupo

Cenário:
Um pesquisador ainda não consegue recrutar um grupo de comparação e quer um piloto. As mesmas crianças fazem um pré-teste, participam de uma sessão guiada de Uno e depois fazem um pós-teste. A adesão final é definida como completar os dois testes. O pesquisador quer detectar uma mudança média padronizada de `0.5`.

Escolhas no wizard:

- caminho: `Pré-teste/pós-teste com um grupo`
- tipo de execução: `Planejar amostra necessária`
- desfecho: `Contínuo`
- tamanho de efeito: `0.5`
- alpha: `0.05`
- power: `0.80`
- completion rate: `0.85`

Por que esse wizard:
Não existe grupo de controle e o desfecho é a mudança nas mesmas pessoas.

### Exemplo 4. Questionário de opinião pós-intervenção com Uno

Cenário:
Depois de uma atividade em sala usando Uno, o pesquisador pede que as crianças respondam a um questionário curto sobre o jogo. Um item diz: "O jogo me ajudou a entender maior e menor." A escala vai de 1 a 5, em que `1` significa discordo totalmente, `3` significa nem concordo nem discordo, `4` significa concordo e `5` significa concordo totalmente. O pesquisador quer planejar respondentes válidos suficientes para descrever a proporção favorável com intervalo de confiança de 95% e cerca de 10 pontos percentuais de margem de erro.

Escolhas no wizard:

- caminho: `Questionário pós-intervenção com um grupo`
- tipo de execução: `Planejar amostra necessária`
- objetivo da análise do questionário: `Proporção de respostas favoráveis`
- alpha: `0.05`
- mínimo da escala: `1`
- máximo da escala: `5`
- pontos da escala: `5`
- limiar favorável: `4`
- proporção favorável esperada: `0.50` se não houver piloto
- margem de erro: `0.10`
- completion rate: `0.90`
- usable data rate: `0.95`

Por que esse wizard:
Não há grupo de controle nem medida antes/depois. A afirmação é sobre a precisão das opiniões relatadas depois da atividade.

### Exemplo 5. Questionário de opinião pós-intervenção estratificado com Uno

Cenário:
A mesma atividade com Uno será usada em um programa escolar misto. O pesquisador sabe que a população pretendida tem cerca de 30% de crianças de `8-10` anos, 40% de `11-13` e 30% de `14-16`. Um questionário simples poderia superamostrar crianças mais velhas se elas responderem mais rápido. Por isso, o pesquisador quer que a afirmação de opinião seja verificada por faixa etária.

Escolhas no wizard:

- caminho: `Questionário pós-intervenção estratificado`
- tipo de execução: `Planejar amostra necessária`
- objetivo da análise do questionário: `Proporção de respostas favoráveis`
- alpha: `0.05`
- margem de erro: `0.10`
- definição de estratos: `{"idade_8_10": {"label": "Idade 8-10", "population_proportion": 0.30}, "idade_11_13": {"label": "Idade 11-13", "population_proportion": 0.40}, "idade_14_16": {"label": "Idade 14-16", "population_proportion": 0.30}}`
- método de alocação: `minimum_per_stratum` quando cada faixa deve ser visível, ou `proportional` quando a estimativa geral é o objetivo principal
- mínimo por estrato: `30`
- usar pesos: `true`

Por que esse wizard:
O estudo continua sendo descritivo, mas a afirmação deve representar uma população com classes conhecidas. O aplicativo planeja respostas válidas por estrato e depois verifica se cada classe ficou abaixo da meta ou sub-representada.

## 8. O problema inverso

O app também pode fazer o cálculo inverso.

Exemplo:
Um piloto com Uno e um grupo único coletou `28` crianças que completaram os dois testes e produziu uma mudança padronizada observada de `0.35`.

Escolhas no wizard:

- caminho: `Pré-teste/pós-teste com um grupo`
- tipo de execução: `Avaliar resultado alcançado`
- alpha: `0.05`
- n total observado: `28`
- efeito observado: `0.35`

O app então estima:

- estatística z aproximada
- valor-p aproximado
- poder aproximado alcançado para o efeito observado

Se o piloto tem apenas o tamanho da amostra alcançada e ainda não tem um efeito observado defensável, o app agora gera uma tabela de capacidade em vez de fingir que existe uma resposta única. Por exemplo, com `28` pares completos em um pré/pós de um grupo, ele pode relatar o efeito mínimo detectável para `p < 0.05` com `80%` de poder, o poder para efeitos comuns como `d = 0.20`, `0.50` e `0.80`, e o limiar aproximado de alpha necessário para alvos comuns de efeito/poder. Em estudos de dois grupos com apenas `n` total, ele também compara alocações comuns como `1:1`, `2:1` e `1:2`.

Para questionário pós-intervenção, a interpretação inversa é diferente. Se o pesquisador informa apenas o número de respondentes válidos alcançados, o aplicativo estima a margem de erro atual aproximada para uma proporção favorável. Se o pesquisador informa um histograma como `{"1": 2, "2": 4, "3": 10, "4": 18, "5": 26, "NA": 3}`, o aplicativo relata denominador válido, contagem NA, contagem favorável, proporção favorável, intervalo de confiança de Wilson e média do escore. Isso sustenta uma conclusão descritiva como: "a maioria dos respondentes válidos foi favorável, mas o limite inferior do intervalo de confiança é a parte conservadora da afirmação."

Para questionário estratificado, a interpretação inversa adiciona representação. Se o pesquisador informa dados alcançados por estrato, o app relata o resultado geral do questionário e uma tabela por estrato com participação esperada, participação observada, razão de representação, peso opcional e status como `under target`, `under-represented`, `over-represented` ou `ok`. Isso ajuda a decidir se a afirmação de opinião pode ser ampla ou se precisa ser qualificada, por exemplo: "a faixa etária mais jovem ficou sub-representada, então o resultado reflete principalmente respondentes mais velhos."

Isso é útil quando o efeito desejado não foi encontrado. Um resultado não significativo pode significar:

- a intervenção realmente teve pouco ou nenhum efeito
- o estudo teve pouca precisão
- o efeito observado foi menor do que o planejado

## 9. O que fazer quando o efeito desejado não aparece

A ausência do efeito desejado não significa que não houve efeito algum.

No fim do estudo, costuma ser útil calcular e relatar:

- o efeito realmente observado
- a incerteza aproximada ao redor dele
- se a amostra coletada tinha precisão suficiente para o efeito que importava

Na prática:

- o planejamento pergunta: `Que efeito eu quero ser capaz de detectar?`
- a avaliação pergunta: `Que efeito eu observei de fato, e o que esse estudo conseguiu mostrar sobre ele?`

## 10. Aba Sugestões

A aba `Sugestões` é o lugar em que o software passa a julgar de forma útil.

Ela destaca coisas como:

- taxa de resposta baixa
- taxa de conclusão baixa
- taxa de dados utilizáveis baixa
- inflação por cluster
- limitações de desenho sem grupo de controle
- limitações de questionário pós-intervenção quando a evidência é descritiva, não causal
- valores aceitos fora das faixas recomendadas

O objetivo não é bloquear o estudo, mas tornar explícitos os trade-offs.
