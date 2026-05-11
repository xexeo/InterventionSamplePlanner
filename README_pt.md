<!-- File version: 2.0; date: 2026-05-11 -->

# Intervention Sample Planner

O Intervention Sample Planner, ou `ISP`, é uma API local em Python e um aplicativo desktop em Tkinter para planejar ou avaliar estudos de intervenção em processos humanos, como aprendizagem, treinamento, usabilidade e melhoria de fluxo de trabalho.

A versão `2.0` amplia o aplicativo para além do desenho original de dois grupos. Agora ele oferece:

- `Dois grupos independentes`
- `Pré-teste/pós-teste com grupo de controle`
- `Pré-teste/pós-teste com um grupo`
- `Planejar amostra necessária`
- `Avaliar resultado alcançado`
- faixas recomendadas com liberação explícita
- explicações carregadas de um arquivo JSON separado
- uma aba de sugestões com orientações metodológicas e alertas

## O que ele faz

O aplicativo ajuda a responder perguntas como:

- Quantos participantes válidos são necessários para comparar intervenção e controle?
- Quantas pessoas precisam completar tanto o pré-teste quanto o pós-teste?
- Quantas pessoas devem ser convidadas se parte delas não iniciar ou não terminar?
- Se um estudo já foi executado, que valor-p aproximado e que poder alcançado correspondem ao resultado observado?

A implementação atual é mais forte para desfechos contínuos. Desfechos binários, no momento, são suportados no caminho `Dois grupos independentes`.

## Caminhos de pesquisa típicos

### 1. Dois grupos independentes

Use quando um grupo recebe a intervenção e outro não recebe. Exemplo: um pesquisador da área de jogos educacionais quer testar se usar Uno junto com uma aula melhora o entendimento de maior e menor em um pós-teste, comparado com apenas aula.

### 2. Pré-teste/pós-teste com grupo de controle

Use quando os dois grupos são medidos antes e depois. Exemplo: um grupo faz um pré-teste, joga Uno, recebe uma aula curta e faz um pós-teste; o grupo controle faz o mesmo pré-teste e pós-teste, mas recebe apenas a aula.

### 3. Pré-teste/pós-teste com um grupo

Use quando os mesmos participantes são medidos antes e depois e não existe grupo de controle. Exemplo: um pesquisador quer uma primeira estimativa do efeito de aprendizagem de jogar Uno entre um pré-teste e um pós-teste antes de executar um ensaio controlado.

## Modo inverso

`Avaliar resultado alcançado` é o fluxo inverso. Em vez de perguntar quantos participantes são necessários, ele pergunta o que a amostra alcançada e o efeito observado implicam. Ele informa quantidades aproximadas como:

- efeito observado informado
- estatística z aproximada
- valor-p aproximado
- poder aproximado alcançado

Esse modo é útil quando um piloto ou estudo concluído não encontrou o efeito desejado e o pesquisador quer entender o que a amostra coletada foi capaz de mostrar.

## Tamanho de efeito em linguagem simples

Tamanho de efeito é a entrada mais difícil para muitos usuários, então o `ISP v2.0` passou a tratá-la de forma mais explícita.

- Em `Dois grupos independentes`, o tamanho de efeito contínuo é a diferença padronizada entre grupos.
- Em `Pré-teste/pós-teste com grupo de controle`, ele é a diferença padronizada de ganho, ou o efeito no pós-teste depois de considerar a linha de base.
- Em `Pré-teste/pós-teste com um grupo`, ele é a mudança média padronizada nos mesmos participantes.

Valores tradicionais como `0,2`, `0,5` e `0,8` podem servir como orientação, mas o melhor tamanho de efeito é o menor efeito que realmente seria significativo no estudo real.

## Explicações e recomendações

O aplicativo agora lê explicações longas das variáveis e faixas recomendadas a partir de:

`intervention_sample_planner/explanations.json`

Esse JSON foi pensado para permanecer alinhado ao manual operacional e ao manual educacional.

## Execução local

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
python run_app.py
```

## Construção do executável

Veja:

- `build.md`
- `developers.md`
- `versions.md`

## Documentação principal

- `resumoteoria.md`
- `docs/educational_manual/manual.tex`
