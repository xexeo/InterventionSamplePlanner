<!-- File version: 2.0; date: 2026-05-11 -->

# Notas para Desenvolvedores

## Arquitetura principal

`intervention_sample_planner/calculator.py`
: motor de cálculo, seleção de desenho, modo de planejamento e modo de resultado alcançado.

`intervention_sample_planner/gui.py`
: interface Tkinter, wizard, modo de configuração direta, liberações de faixa e aba de sugestões.

`intervention_sample_planner/explanations.json`
: explicações longas, faixas recomendadas e descrições de desenho usadas pela GUI.

`intervention_sample_planner/content.py`
: helpers de carregamento para `explanations.json`.

## Caminhos de estudo na versão 2.0

- `parallel_two_group`
- `pretest_posttest_control`
- `one_group_pre_post`

Desfechos binários, no momento, são suportados apenas em `parallel_two_group`.

## Verificação de faixas

As faixas recomendadas ficam em `explanations.json`. A GUI as verifica e bloqueia valores fora da faixa, a menos que o usuário ative explicitamente a caixa de liberação daquele campo. As liberações aceitas são armazenadas em `range_override_fields`.

## Modo inverso

O fluxo inverso é representado por:

- `analysis_mode = "evaluate"`
- `observed_control_n`
- `observed_intervention_n`
- `observed_total_n`
- `observed_effect_size`

O objeto de resultado inclui `observed_analysis` com `z`, `p_value` e `achieved_power` aproximados.

## Implicações de build

Se você alterar `explanations.json`, lembre-se de que o build do executável precisa incluí-lo com PyInstaller `--add-data`.
