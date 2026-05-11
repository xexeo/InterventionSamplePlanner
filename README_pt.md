# Planejador de Amostra para Intervenções

<!-- File version: 1.0; date: 2026-05-11 -->

O Planejador de Amostra para Intervenções é um app desktop local para planejar o tamanho da amostra de um estudo de intervenção com dois grupos.

Versão atual da aplicação: **ISP v1.0**.

Política de documentação: os arquivos Markdown em inglês são os originais canônicos. Arquivos terminados em `_pt.md` são traduções em português desses originais em inglês.

Ele foi pensado para experimentos em que um grupo recebe a intervenção e outro grupo não recebe, por exemplo:

- jogo educacional versus aula tradicional;
- tutorial novo versus tutorial atual;
- versão com feedback adaptativo versus versão com feedback fixo;
- intervenção de saúde, treinamento, usabilidade ou aprendizagem versus condição controle.

O app não responde apenas "quantas pessoas?". Ele separa etapas metodológicas que muitas vezes são misturadas:

1. Quantos casos válidos e analisáveis são necessários se todas as pessoas fornecerem dados?
2. Como esses casos devem ser divididos entre intervenção e controle?
3. O que muda quando a população é finita, os dados estão agrupados em turmas/grupos ou o alfa precisa ser ajustado por múltiplas comparações planejadas?
4. Quantas pessoas devem ser alocadas, recrutadas ou convidadas depois de considerar desistência, não resposta e dados inválidos?
5. Como a decisão amostral deve ser explicada em artigo, TCC, dissertação, tese, protocolo ou submissão ética?

## Principais Recursos

- App local em Tkinter, sem necessidade de servidor web.
- API de cálculo em Python puro, reutilizável em scripts, notebooks, testes ou interfaces futuras.
- Modo assistente com explicações para cada pergunta.
- Modo de configuração direta com todas as variáveis em um só lugar.
- Botão `?` ao lado de cada campo.
- Suporte a inglês e português na interface e no relatório.
- Abas de resultado para resumo, sensibilidade e JSON.
- Tabela de sensibilidade formatada.
- Salvar e carregar configurações do estudo em JSON.
- Exportar o relatório de planejamento como texto.
- Exemplos baseados em fontes externas e testes unitários.

## O Que Ele Calcula

Versão atual:

- Duas médias independentes usando `d` de Cohen.
- Duas proporções independentes, como conclusão, sucesso, erro, abandono ou taxa de retorno.
- Alocação igual ou desigual entre intervenção e controle.
- Planejamento bilateral ou unilateral.
- Ajuste de Bonferroni para múltiplas comparações primárias planejadas.
- Correção opcional para população finita.
- Efeito de desenho opcional para clusters: `DEFF = 1 + (m - 1) * ICC`.
- Taxa de resposta/início, taxa de conclusão, taxa de dados utilizáveis e reserva extra.
- Cenários de sensibilidade para efeitos menores/maiores e poder mais alto.

Os cálculos usam aproximações normais. Ferramentas exatas, como G*Power ou R `pwr`, podem retornar um participante a mais por grupo porque usam distribuição t ou procedimentos exatos iterativos.

## Como Rodar o App

A partir da pasta do repositório:

```powershell
cd D:\GitHub\InterventionSamplePlanner
python run_app.py
```

ou:

```powershell
python -m intervention_sample_planner
```

Se estiver usando o executável Windows gerado, abra:

```text
dist\InterventionSamplePlanner\InterventionSamplePlanner.exe
```

ou, se foi gerado em arquivo único:

```text
dist\InterventionSamplePlanner.exe
```

## Problemas Rápidos Para Testar

Use estes casos para verificar se o app está funcionando como esperado.

### 1. Diferença de Média, Intervenção de Ensino

Problema: um novo método de ensino é comparado com aula tradicional. O pesquisador quer 80% de poder para detectar uma diferença média padronizada moderada.

Entradas:

- tipo de desfecho: contínuo;
- d de Cohen: `0.5`;
- alfa: `0.05`;
- poder: `0.80`;
- razão de alocação: `1`;
- resposta, conclusão e dados utilizáveis: `1`.

Resultado esperado:

- controle válido: `63`;
- intervenção válida: `63`;
- total válido: `126`.

Esse resultado acompanha o exemplo por aproximação normal da StatsIQ. Softwares exatos podem retornar `64` por grupo.

### 2. Diferença de Média Com 15% de Desistência

Mesmo caso anterior, mas com taxa de conclusão `0.85`.

Resultado esperado:

- alvo inicial válido: `63 + 63 = 126`;
- participantes a iniciar/alocar: `75 + 75 = 150`.

Por quê: `63 / 0.85 = 74.12`, arredondado para `75` por grupo.

### 3. Desfecho Binário, Taxa de Conclusão

Problema: uma versão de jogo com suporte adaptativo deve aumentar a conclusão de fase de 45% para 60%.

Entradas:

- tipo de desfecho: binário;
- proporção no controle: `0.45`;
- proporção na intervenção: `0.60`;
- alfa: `0.05`;
- poder: `0.80`;
- razão de alocação: `1`.

Resultado esperado:

- controle válido: `173`;
- intervenção válida: `173`;
- total válido: `346`.

### 4. Turmas Agrupadas

Problema: estudantes estão dentro de turmas, e estudantes da mesma turma tendem a ser mais parecidos entre si do que estudantes independentes.

Entradas:

- use o caso contínuo com `d = 0.5`;
- tamanho médio do cluster: `25`;
- ICC: `0.05`.

Resultado esperado:

- efeito de desenho: `2.2`;
- controle válido corrigido: `139`;
- intervenção válida corrigida: `139`;
- total válido corrigido: `278`.

## Carregando Exemplos

Os arquivos JSON de exemplo estão em:

```text
examples\
examples\from_sources\
```

Use `examples\` para configurações simples do app e `examples\from_sources\` para casos documentados que incluem metadados de fonte e resultados esperados.

No app:

1. Abra **Dados / Configuração**.
2. Clique em **Carregar configuração**.
3. Escolha um dos arquivos JSON.
4. Clique em **Calcular**.
5. Verifique as abas de **Resultados**.

Os arquivos em `examples/from_sources` também incluem um bloco `source_case` com fonte, problema real e resultados esperados. O app ignora esses metadados, mas a suíte de testes os utiliza.

## Esquema JSON

Arquivos de configuração podem ser documentados e verificados com JSON Schema:

```text
schemas/study_config.schema.json
```

Os arquivos JSON de exemplo incluem um campo `$schema` que aponta para esse esquema. Editores como VS Code podem usá-lo para autocomplete, descrições de campos e validação básica. O app em si é permissivo: ele ignora metadados desconhecidos como `$schema`, `_file_version`, `_file_date` e `source_case` ao carregar uma configuração.

O schema descreve os campos atuais de `StudyConfig`, valores suportados, intervalos numéricos e regras condicionais, como exigir `finite_population` quando `apply_fpc` é verdadeiro.

## Rodando os Testes

```powershell
cd D:\GitHub\InterventionSamplePlanner
python -m unittest discover -s tests
```

Os testes verificam:

- exemplos derivados de `resumoteoria.md`;
- arquivos JSON de exemplo baseados em fontes;
- correção por desistência;
- correção por efeito de desenho em clusters;
- carregamento de configuração ignorando metadados desconhecidos.

## Uso Pela API

```python
from intervention_sample_planner import StudyConfig, calculate_plan, render_report

config = StudyConfig(
    study_name="Validação de intervenção educacional",
    outcome_type="continuous",
    effect_size_d=0.5,
    alpha=0.05,
    power=0.80,
    allocation_ratio=1.0,
    completion_rate=0.85,
)

plan = calculate_plan(config)
print(plan.initial_valid.total)
print(plan.assigned_needed.total)
print(render_report(plan, "pt"))
```

## Como Interpretar os Resultados

O app relata vários números de amostra de propósito:

- **Alvo inicial de dados válidos**: amostra teórica válida/analisável se todos fornecerem dados utilizáveis.
- **Alvo corrigido de dados válidos**: amostra válida após correções de população finita e desenho/cluster.
- **Participantes a alocar/iniciar**: quantas pessoas devem começar depois de considerar conclusão e dados utilizáveis.
- **Pessoas a convidar/contatar**: quantas pessoas devem ser contatadas depois de considerar a taxa de resposta/início.

Por exemplo, se um estudo precisa de 63 participantes válidos por grupo e espera 15% de desistência, ele não deve recrutar apenas 63 por grupo. Deve iniciar cerca de 75 por grupo para preservar o alvo de dados válidos.

## Orientação Metodológica

O app segue a regra metodológica resumida em [`resumoteoria_pt.md`](resumoteoria_pt.md): tamanho de amostra é parte do planejamento da evidência, não apenas uma fórmula.

As suposições centrais são:

- o tamanho da amostra deve corresponder à inferência pretendida;
- uma afirmação causal ou de intervenção precisa de comparação e controle;
- análise de poder exige alfa, poder, tamanho de efeito, variabilidade ou taxas e razão de alocação;
- a amostra calculada é de dados válidos analisáveis, não de convites;
- desistência, não resposta, dados inválidos, clusters e múltiplas comparações devem ser planejados antes da coleta;
- as conclusões devem ser proporcionais à evidência.

Fontes externas usadas como orientação:

- [Exemplo trabalhado da StatsIQ](https://www.statisticstutor.app/study-guides/statistical-power-sample-size-calculation-type-ii-error)
- [Aula da StatsMasters sobre tamanho de efeito e poder](https://statsmasters.com/lessons/effect-size-power/)
- [G*Power](https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower/news-page)
- [Manual do G*Power 3.1](https://www.psychologie.hhu.de/fileadmin/redaktion/Fakultaeten/Mathematisch-Naturwissenschaftliche_Fakultaet/Psychologie/AAP/gpower/GPowerManual.pdf)
- [Documentação de poder e tamanho amostral do statsmodels](https://www.statsmodels.org/stable/stats.html)
- [Documentação do R pwr.t.test](https://search.r-project.org/CRAN/refmans/pwr/html/pwr.t.test.html)
- [Documentação do OpenEpi para coorte e ensaio clínico](https://www.openepi.com/Documentation/SSCohortdoc.htm)
- [Exemplos de tamanho amostral e poder do J-PAL](https://github.com/J-PAL/Sample_Size_and_Power)

## Diferenças em Relação às Fontes de Orientação

Este app foi inspirado por ferramentas consolidadas de tamanho amostral e poder, mas tem outro objetivo. Ele não tenta substituir software estatístico especializado. O objetivo é guiar um pesquisador por um fluxo comum de planejamento de intervenção e tornar explícitas as consequências de recrutamento.

| Fonte | Para que é boa | Como este app é diferente |
| --- | --- | --- |
| G*Power e manual do G*Power 3.1 | Software desktop amplo para análise de poder. Suporta muitas famílias de testes, incluindo testes exatos, F, t, qui-quadrado, z e casos de regressão/correlação. Também suporta análise a priori, compromisso, critério, post-hoc e sensibilidade, calculadoras de tamanho de efeito, gráficos de distribuição e protocolo de saída. | Este app é mais estreito: foca o planejamento de intervenção com dois grupos. Ele acrescenta linguagem de fluxo sobre dados válidos, alvos de início/alocação, convites, atrito, perda de dados utilizáveis, populações finitas, clusters e parágrafo de justificativa para texto acadêmico. |
| statsmodels | Biblioteca Python com classes e funções reutilizáveis de poder estatístico. É melhor para desenvolvedores que querem análise de poder dentro de um fluxo maior em Python. | Este app mantém uma API simples sem dependências externas e uma interface Tkinter. É mais fácil para planejamento local e ensino, mas muito menos completo que o statsmodels. |
| R `pwr.t.test` | Função compacta em R para resolver um parâmetro ausente em planejamento de poder para testes t. Integra-se naturalmente a scripts de análise em R. | Este app acrescenta explicações guiadas, rótulos bilíngues, arquivos JSON de projeto, correções de recrutamento e fluxo gráfico. Atualmente usa aproximações normais, então pode diferir por um participante por grupo em relação a funções t exatas. |
| OpenEpi | Calculadoras de estilo epidemiológico para tamanho de amostra e desenhos de saúde pública, com entradas como confiança, poder, razão entre grupos e frequência esperada do desfecho. | Este app usa esse estilo prático de entrada, mas é estruturado para validação de intervenção com grupo controle, planejamento de desistência/não resposta e escrita de protocolo ou tese. |
| Exemplos do J-PAL | Exemplos aplicados para avaliação de impacto, incluindo raciocínio sobre clusters e experimentos de campo. | Este app inclui correção simples por efeito de desenho, mas ainda não implementa toda a gama de modelos de poder para campo, ajuste por covariáveis, adesão imperfeita ou desenhos por nível de randomização. |
| Exemplos da StatsIQ e StatsMasters | Exemplos educacionais que mostram como alfa, poder, tamanho de efeito e amostra interagem. | Este app transforma exemplos semelhantes em casos JSON carregáveis e testes, depois os estende com etapas de correção para o número de pessoas a iniciar ou convidar. |

## Limites

Este app é um companheiro de planejamento. Ele não substitui um estatístico em decisões de alto risco ou desenhos complexos.

Use revisão especializada para:

- decisões clínicas, legais, de segurança ou institucionais;
- desfechos longitudinais;
- medidas repetidas além do planejamento simples de dois grupos;
- modelos mistos;
- poder ajustado por covariáveis;
- desfechos não normais ou raros que exigem modelos especializados;
- desenhos stepped-wedge, crossover, adaptativos ou bayesianos.

Para a versão original em inglês, veja [README.md](README.md). Para detalhes de desenvolvimento, veja [developers_pt.md](developers_pt.md). Para geração de executáveis, veja [build_pt.md](build_pt.md).
