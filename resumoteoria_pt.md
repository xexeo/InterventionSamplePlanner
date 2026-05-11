<!-- File version: 2.0; date: 2026-05-11 -->

# Resumo Operacional da Teoria para o ISP v2.0

Este manual operacional explica como usar o `ISP v2.0` de forma prática. Ele é mais curto que o manual educacional em LaTeX, mas foi escrito para apoiar decisões reais dentro do aplicativo.

## 1. O que mudou na versão 2.0

O `ISP v1.0` focava em um desenho: dois grupos independentes. O `ISP v2.0` acrescenta:

- `Dois grupos independentes`
- `Pré-teste/pós-teste com grupo de controle`
- `Pré-teste/pós-teste com um grupo`
- `Planejar amostra necessária`
- `Avaliar resultado alcançado`
- faixas recomendadas com liberação explícita
- explicações em `intervention_sample_planner/explanations.json`
- uma aba dedicada de `Sugestões`

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

Às vezes existe apenas um questionário após exposição a um sistema, jogo ou aula. Nesse caso, o tamanho de efeito continua precisando vir de uma diferença significativa na prática, mas a interpretação costuma ser mais difícil porque não existe medida de linha de base.

Por exemplo:
- se satisfação é medida em uma escala de 1 a 5
- e uma diferença de `0.4` ponto justificaria mudar a interface
- e o desvio padrão combinado esperado é `0.8`

então:

`d = 0.4 / 0.8 = 0.5`

## 6. Números tradicionais e por que aparecem tanto

Esses valores aparecem no software porque são comuns em pesquisa real:

- `alpha = 0.05`
- `power = 0.80`
- `power = 0.90`
- `effect_size_d = 0.20, 0.50, 0.80`
- `completion_rate = 0.85` ou `0.90`
- `usable_data_rate = 0.95`
- `ICC = 0.05`

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
- valores aceitos fora das faixas recomendadas

O objetivo não é bloquear o estudo, mas tornar explícitos os trade-offs.
