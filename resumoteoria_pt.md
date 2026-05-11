# Resumo Operacional da Teoria de Amostra

<!-- File version: 1.0; date: 2026-05-11 -->

Este arquivo é um guia operacional curto para planejar tamanho de amostra em estudos de intervenção com dois grupos: um grupo recebe a intervenção e o outro não recebe. Ele ajuda usuários a aplicar o app, escolher entradas e escrever uma justificativa amostral defensável.

Política de documentação: `resumoteoria.md` é o original canônico em inglês. Este arquivo é sua tradução em português.

Ele não é um livro de estatística. É um checklist prático para transformar uma pergunta de pesquisa em um plano de amostra.

## Ideia Central

Tamanho de amostra não é apenas uma conta. É uma decisão sobre a força da evidência que o estudo precisa produzir.

A pergunta útil não é só:

```text
Quantas pessoas eu preciso?
```

É:

```text
Que conclusão quero sustentar, com que risco de erro, usando quais dados, em qual população ou contexto?
```

Uma amostra é suficiente quando consegue responder à pergunta do estudo sem afirmar mais do que a evidência permite.

## Quatro Perguntas Antes de Qualquer Fórmula

Antes de calcular, defina:

1. Qual é a unidade da inferência?
   Exemplos: estudante, jogador, turma, sessão, resposta, documento, execução computacional.

2. Que tipo de resultado será analisado?
   Exemplos: média de aprendizagem, taxa de conclusão, proporção de erro, correlação, entrevista, log, caso.

3. Que efeito seria grande o bastante para importar?
   Exemplos: ganho de 0,5 ponto em uma escala, aumento de 45% para 60% de conclusão, redução relevante de erros.

4. Quanta incerteza é aceitável?
   Exemplos: alfa 0,05, poder 80%, margem de erro 5%, saturação documentada.

## Quando o Estudo Compara Dois Grupos

Para validar uma intervenção, o desenho comum é:

```text
Grupo intervenção vs grupo controle
```

Esse desenho deve declarar:

- hipótese principal;
- desfecho principal;
- nível de significância, ou alfa;
- poder desejado;
- menor tamanho de efeito relevante;
- razão de alocação entre os grupos;
- perdas, desistência, não resposta e dados inválidos esperados.

## Erro Tipo I, Erro Tipo II e Poder

Erro Tipo I significa concluir que existe efeito quando não existe efeito real.

```text
P(erro Tipo I) = alfa
```

Erro Tipo II significa não detectar um efeito real relevante.

```text
P(erro Tipo II) = beta
```

Poder é a chance de detectar o efeito planejado se ele realmente existir.

```text
poder = 1 - beta
```

Valores comuns:

| Decisão | Valor comum |
| --- | --- |
| Alfa | 0,05 |
| Poder | 0,80 |
| Alfa mais rigoroso | 0,01 |
| Poder mais rigoroso | 0,90 ou 0,95 |

Esses valores são convenções, não leis. Escolhas diferentes devem ser justificadas quando o custo prático, ético ou científico do erro for diferente.

## Comparando Duas Médias

Use quando o desfecho principal é uma média:

- escore de aprendizagem;
- escore de engajamento;
- escala de usabilidade;
- tempo médio;
- pontuação de desempenho.

O efeito é o `d` de Cohen:

```text
d = (média_intervenção - média_controle) / desvio_padrão_combinado
```

Para grupos de mesmo tamanho:

```text
n_por_grupo = 2 * (z_alfa + z_poder)^2 / d^2
```

Exemplo:

- alfa = 0,05, bilateral;
- poder = 0,80;
- d = 0,5.

Resultado aproximado:

```text
63 participantes por grupo
126 participantes no total
```

Interpretação: o estudo foi planejado para detectar uma diferença média padronizada de 0,5 entre intervenção e controle.

## Comparando Duas Proporções

Use quando o desfecho principal é uma taxa:

- concluiu ou não concluiu;
- teve sucesso ou falhou;
- retornou ou não retornou;
- abandonou ou permaneceu;
- escolheu ou não escolheu uma opção.

Entradas principais:

```text
proporção_controle
proporção_intervenção
alfa
poder
razão_de_alocação
```

Exemplo:

- 45% concluem no grupo controle;
- 60% concluem no grupo intervenção;
- alfa = 0,05, bilateral;
- poder = 0,80.

Resultado aproximado:

```text
173 participantes por grupo
346 participantes no total
```

Interpretação: comparar proporções frequentemente exige amostras maiores do que pesquisadores esperam, especialmente quando a diferença esperada é moderada.

## Grupos Desiguais

Se os grupos têm tamanhos desiguais, defina a razão:

```text
k = n_intervenção / n_controle
```

Exemplo:

```text
k = 2
```

significa que o grupo intervenção foi planejado para ter o dobro do tamanho do grupo controle.

Grupos desiguais podem ser necessários por acesso ou logística, mas normalmente aumentam o total necessário para a mesma força estatística.

## Amostra Inicial, Amostra Válida e Convites

O número produzido pela fórmula principal geralmente é o número de casos válidos analisáveis, não o número de convites.

Separe estas etapas:

| Etapa | Significado |
| --- | --- |
| Alvo inicial válido | Casos analisáveis necessários se todos fornecerem dados utilizáveis |
| Alvo válido corrigido | Casos válidos após correção de população finita, cluster ou múltiplas comparações |
| Participantes a iniciar | Pessoas que devem começar após considerar desistência e dados inválidos |
| Pessoas a convidar/contatar | Pessoas que devem ser contatadas após considerar a taxa de resposta/início |

Correção simples por perda:

```text
n_recrutado = n_necessário / (1 - taxa_de_perda)
```

Exemplo:

```text
63 / 0,85 = 74,12
```

Arredonde para cima:

```text
75 participantes por grupo
```

## Taxa de Resposta e Dados Inválidos

Quando nem todas as pessoas convidadas participam:

```text
convites = n_válido / taxa_de_resposta
```

Quando parte dos dados completos é inválida:

```text
taxa_efetiva = taxa_resposta * taxa_conclusão * taxa_dados_utilizáveis
```

Então:

```text
convites = n_válido / taxa_efetiva
```

Exemplo:

- 292 respostas válidas necessárias;
- taxa de resposta = 40%;
- perda por resposta inválida ou incompleta = 10%.

Taxa efetiva:

```text
0,40 * 0,90 = 0,36
```

Convites:

```text
292 / 0,36 = 812 convites
```

## População Finita

Use correção para população finita apenas quando a conclusão estiver restrita a uma população pequena e conhecida.

Exemplos:

- todos os estudantes de uma disciplina;
- todos os participantes de uma oficina;
- todos os jogadores de um teste fechado.

Fórmula:

```text
n = (N * n0) / (N + n0 - 1)
```

Onde:

- `N` é o tamanho da população finita;
- `n0` é a amostra sem correção;
- `n` é a amostra corrigida.

Não use essa correção quando a conclusão pretendida for sobre uma população ampla.

## Turmas, Grupos e Clusters

Quando participantes estão agrupados, eles não são totalmente independentes.

Exemplos:

- estudantes dentro da mesma turma;
- jogadores dentro da mesma equipe;
- participantes dentro da mesma oficina;
- pacientes dentro do mesmo serviço.

Correção por efeito de desenho:

```text
DEFF = 1 + (m - 1) * ICC
```

Onde:

- `m` é o tamanho médio do cluster;
- `ICC` é a correlação intraclasse.

Amostra ajustada:

```text
n_ajustado = n_independente * DEFF
```

Exemplo:

- amostra independente = 126;
- tamanho médio da turma = 25;
- ICC = 0,05.

```text
DEFF = 1 + 24 * 0,05 = 2,2
126 * 2,2 = 278
```

Resultado:

```text
278 estudantes
```

## Múltiplas Comparações

Se o estudo testa vários desfechos primários, o risco de falso positivo aumenta.

Uma correção simples é Bonferroni:

```text
alfa_ajustado = alfa / número_de_comparações
```

Exemplo:

```text
0,05 / 5 = 0,01
```

Isso reduz falsos positivos, mas aumenta a amostra necessária. Defina antes quais comparações são primárias e quais são exploratórias.

## Estudos Pequenos

Uma amostra pequena não é automaticamente uma amostra ruim.

Ela pode ser adequada quando o objetivo é:

- teste piloto;
- teste de instrumento;
- avaliação formativa;
- diagnóstico de problemas;
- refinamento de protótipo;
- entrevista em profundidade;
- estudo de caso;
- geração de hipóteses.

Ela é insuficiente quando o texto promete:

- eficácia geral;
- superioridade definitiva;
- impacto populacional;
- validação conclusiva;
- ausência de problemas raros;
- generalização ampla sem desenho compatível.

## Se a Amostra Disponível For Pequena

Reformule a pergunta para que ela corresponda à evidência que você realmente pode coletar.

Evite:

```text
A intervenção melhora a aprendizagem dos estudantes.
```

Prefira, quando o desenho for pequeno ou exploratório:

```text
Neste contexto observado, a intervenção produziu indícios preliminares de melhora e identificou condições para uma avaliação futura com maior poder estatístico.
```

Isso não enfraquece o estudo. Torna a conclusão proporcional à evidência.

## Checklist de Planejamento

Antes da coleta:

- Defini a população ou o contexto?
- Defini a unidade de análise?
- Defini a unidade de observação?
- Escolhi o desfecho principal?
- Decidi se o desfecho é média ou proporção?
- Justifiquei o tamanho de efeito relevante?
- Escolhi alfa e poder?
- Decidi se o teste é bilateral ou unilateral?
- Defini a razão de alocação intervenção/controle?
- Considerei perdas, desistência e dados inválidos?
- Considerei taxa de resposta?
- Considerei população finita, se aplicável?
- Considerei clusters, se aplicável?
- Considerei múltiplas comparações?
- Escrevi o limite real da conclusão?

## Como Escrever a Justificativa da Amostra

Modelo para duas médias:

```text
O experimento comparou dois grupos independentes: intervenção e controle. O tamanho amostral foi planejado para detectar uma diferença média padronizada de d = [valor] no desfecho principal, com alfa = [valor], teste [bilateral/unilateral] e poder de [valor]. A razão de alocação planejada foi [razão]. O cálculo indicou [n] participantes válidos por grupo. Considerando [taxa] de perdas, desistência ou dados inválidos, o estudo deve iniciar aproximadamente [n_corrigido] participantes por grupo. As conclusões serão limitadas à população, ao contexto e à medida definidos no desenho.
```

Modelo para duas proporções:

```text
O experimento comparou a proporção de [evento] entre o grupo intervenção e o grupo controle. O planejamento assumiu proporção esperada de [p_controle] no controle e [p_intervenção] na intervenção, com alfa = [valor], teste [bilateral/unilateral] e poder de [valor]. O cálculo indicou [n] participantes válidos por grupo. Após correções para resposta, conclusão e dados utilizáveis, o estudo deve convidar aproximadamente [convites] pessoas. Os resultados serão interpretados de forma proporcional ao desenho e às perdas observadas.
```

Modelo para estudo pequeno ou formativo:

```text
Dadas as restrições de tempo, acesso e maturidade da intervenção, este estudo foi planejado como avaliação exploratória e formativa. O objetivo não é estimar um efeito populacional definitivo, mas identificar indícios, problemas de uso, compreensão, aceitabilidade e condições para uma avaliação posterior. Os resultados quantitativos serão tratados de forma descritiva, e os dados qualitativos serão usados para interpretar os padrões observados.
```

## Regra Final

Toda pesquisa deve coletar evidência suficiente para responder à pergunta que faz.

E toda pesquisa deve formular uma pergunta que possa ser respondida pela evidência que consegue coletar.
