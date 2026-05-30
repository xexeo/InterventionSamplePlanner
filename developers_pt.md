<!-- File version: 2.4; date: 2026-05-30 -->

# Notas para Desenvolvedores

## Arquitetura principal

`intervention_sample_planner/calculator.py`
: motor de cálculo, seleção de desenho, modo de planejamento e modo de avaliação de resultado alcançado.

`intervention_sample_planner/gui.py`
: interface Tkinter, wizard, modo de configuração direta, liberações de faixa e aba de sugestões.

`intervention_sample_planner/web_app.py`
: API REST em Flask e servidor de arquivos estáticos para a interface no navegador.

`intervention_sample_planner/web_static/`
: cliente em HTML, CSS e JavaScript puro. Ele chama a API REST e não reimplementa fórmulas estatísticas.

`intervention_sample_planner/explanations.json`
: explicações longas, faixas recomendadas e descrições de desenhos usadas pela interface.

`intervention_sample_planner/content.py`
: funções auxiliares para carregar `explanations.json`.

## Caminhos de estudo na versão 2.4

- `parallel_two_group`
- `pretest_posttest_control`
- `one_group_pre_post`
- `one_group_post_survey`
- `stratified_post_survey`

O planejamento binário é suportado em `parallel_two_group`. A avaliação binária de resultado alcançado é suportada em `parallel_two_group` e em casos pareados de pré/pós com um grupo por meio dos campos de McNemar. O planejamento e a avaliação de questionário pós-intervenção são descritivos: trabalham com proporções favoráveis, médias de escala, histogramas JSON, contagens favoráveis e resumos de média/desvio padrão. Questionários pós-intervenção estratificados acrescentam estratos demográficos, métodos de alocação, planejamento de convites por estrato, razões de representação e pesos opcionais; eles continuam sendo estimação descritiva, não testes causais.

## Verificação de faixas

As faixas recomendadas ficam em `explanations.json`. As interfaces verificam essas faixas e bloqueiam valores fora delas, a menos que o usuário marque explicitamente a liberação daquele campo. As liberações aceitas são armazenadas em `range_override_fields`.

## Modo inverso

O fluxo inverso é representado por:

- `workflow_path = "evaluate_done"` para estudo realizado sem plano anterior
- `workflow_path = "evaluate_against_plan"` para estudo realizado comparado com plano anterior
- `analysis_mode = "evaluate"`
- `had_planned_sample`
- campos `planned_*` para o plano anterior
- campos `observed_*` para os dados alcançados
- campos `observed_survey_*` para histogramas, contagens favoráveis, média e desvio padrão de questionários pós-intervenção
- campos `stratified_*` e `observed_strata_counts` para planejamento e avaliação por estratos

A interface pode carregar um JSON de planejamento salvo. O objeto de resultado inclui `observed_analysis` com `z`, `p_value`, `achieved_power`, taxas binárias observadas quando disponíveis, `exact_p_value` opcional, metas de benchmark, metas do plano anterior, linhas de capacidade da amostra quando apenas o tamanho da amostra alcançada é informado, `survey_analysis` opcional para resumos de questionário pós-intervenção e `stratified_survey_analysis` opcional para planos por estrato e representação alcançada.

## Métodos estatísticos da v2.4

- A avaliação binária de dois grupos usa valor-p exato de Fisher quando as contagens são pequenas ou esparsas.
- A avaliação binária pareada com um grupo usa o teste exato de McNemar/binomial a partir das células discordantes antes/depois.
- O desenho pré-teste/pós-teste com controle continua sendo uma aproximação de planejamento e avaliação no espírito de ANCOVA, não um modelo ANCOVA ajustado.
- O suporte a clusters continua sendo uma aproximação por efeito de desenho. Trabalho futuro pode adicionar número explícito de clusters, alocação por cluster e rotinas de poder para modelos mistos.
- Fluxos de estudo realizado podem rodar sem efeito observado. Nesse caso apenas com tamanho da amostra, `capacity_rows` relata efeitos mínimos detectáveis para combinações comuns de alpha/poder, poder para efeitos comuns, limiares aproximados de alpha e cenários de alocação quando só se conhece a amostra total de dois grupos.
- O planejamento de questionário pós-intervenção com um grupo usa precisão de intervalo de confiança por aproximação normal para proporções favoráveis ou médias. A avaliação usa intervalos de confiança de Wilson para proporções favoráveis e intervalos descritivos para médias. Ela propositalmente não relata valor-p ou poder alcançado porque não há grupo de comparação nem linha de base pré-intervenção.
- O planejamento de questionário pós-intervenção estratificado parte do mesmo alvo de precisão do questionário e distribui respondentes válidos entre estratos por alocação proporcional, igual, mínimo por estrato ou manual. A avaliação compara participações observadas com participações esperadas e relata sub-representação, sobre-representação, estratos ausentes, pesos opcionais e proporções favoráveis por estrato quando disponíveis.

## Exportação de relatórios

`calculator.py` expõe `render_report_html()`, `save_report_html()` e `save_report_pdf()`. O gerador de PDF não usa dependências externas e é intencionalmente simples.

## Interface web e API REST

A interface web é propositalmente pequena: Flask serve o cliente estático e expõe endpoints JSON. Não há banco de dados, não há armazenamento persistente de arquivos do usuário no servidor e não há etapa de build com Node.js.

Endpoints principais:

- `GET /health`
- `GET /api/version`
- `GET /api/default-config`
- `GET /api/explanations?language=en`
- `GET /api/ui-text?language=en`
- `POST /api/calculate`
- `POST /api/report/text`
- `POST /api/report/html`
- `POST /api/report/pdf`

Os endpoints `POST` aceitam o mesmo formato de configuração descrito por `schemas/study_config.schema.json`. O salvamento e carregamento no navegador usam upload e download de arquivos locais.

## Implicações de build

Se você alterar `explanations.json`, lembre que o build do executável precisa incluí-lo com PyInstaller `--add-data`. Se empacotar a interface web em um pacote Python distribuível, inclua também `intervention_sample_planner/web_static/*` como dados do pacote.
