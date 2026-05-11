# Guia de Desenvolvimento

<!-- File version: 1.0; date: 2026-05-11 -->

Este guia é para pessoas que querem adicionar fórmulas, novas interfaces, traduções, testes ou fluxos de distribuição.

Política de documentação: `developers.md` é o original canônico em inglês. Este arquivo é sua tradução em português.

## Estrutura do Projeto

```text
intervention_sample_planner/
  __init__.py
  __main__.py
  calculator.py
  gui.py
  i18n.py
examples/
  from_sources/
tests/
scripts/
schemas/
run_app.py
README.md
README_pt.md
build.md
build_pt.md
developers.md
developers_pt.md
resumoteoria.md
resumoteoria_pt.md
requirements-build.txt
```

O projeto tem duas camadas:

- `calculator.py`: API pura de cálculo, sem Tkinter, sem diálogos de arquivo e sem estado de interface.
- `gui.py`: interface Tkinter que lê/escreve um `StudyConfig`, chama `calculate_plan` e renderiza os resultados.

Mantenha essa separação. Uma futura CLI, interface web ou integração em notebook deve conseguir reutilizar `calculator.py` sem importar Tkinter.

## Modelo de Dados Principal

A entrada principal é `StudyConfig`.

Campos importantes:

- `outcome_type`: `continuous` ou `binary`;
- `alpha`, `power`, `alternative`;
- `allocation_ratio`: intervenção/controle;
- `effect_size_d` para desfechos contínuos;
- `proportion_control` e `proportion_intervention` para desfechos binários;
- campos de correção, como `finite_population`, `cluster_average_size`, `intraclass_correlation`, `response_rate`, `completion_rate` e `usable_data_rate`.

A saída principal é `SamplePlan`.

Etapas importantes da saída:

- `initial_valid`: alvo de dados válidos supondo que todos forneçam dados utilizáveis;
- `fpc_adjusted_valid`: após correção para população finita;
- `design_adjusted_valid`: após correção de desenho/cluster;
- `assigned_needed`: participantes a alocar/iniciar após correção de conclusão e dados utilizáveis;
- `invited_needed`: pessoas a convidar/contatar após correção da taxa de resposta;
- `sensitivity`: linhas exibidas na tabela de sensibilidade.

## Adicionando Um Novo Cálculo

Fluxo recomendado:

1. Adicione ou estenda `SUPPORTED_OUTCOMES` em `calculator.py`.
2. Adicione campos de entrada a `StudyConfig`.
3. Adicione validação em `_validate_config`.
4. Implemente uma função privada de cálculo, seguindo o estilo de `_continuous_initial` ou `_binary_initial`.
5. Direcione `calculate_plan` e `_calculate_no_sensitivity` para a nova função.
6. Adicione fórmulas à lista `formulas` retornada.
7. Adicione avisos quando as suposições forem frágeis.
8. Adicione rótulos e textos de ajuda em `i18n.py`.
9. Adicione o campo a `FIELD_GROUPS` e `FIELD_TYPES` em `gui.py`.
10. Adicione JSON de exemplo e testes unitários.

Prefira fórmulas claras e validação conservadora a código esperto. Software de tamanho amostral é confiável quando suas suposições ficam visíveis.

## Notas Sobre a Interface

A interface usa Tkinter padrão e `ttk`.

Padrões importantes:

- Todo campo editável deve ter um rótulo `field_...` em `i18n.py`.
- Todo campo editável deve ter uma explicação `help_...` em `i18n.py`.
- Perguntas do assistente usam `wizard_question_...` e `wizard_why_...`.
- Configuração direta e modo assistente compartilham `self.vars`; mudar um modo atualiza o mesmo estado de configuração.
- A aba de sensibilidade usa `ttk.Treeview`, não widget de texto.

Evite adicionar dependências pesadas de interface, a menos que haja um motivo forte. A vantagem atual é que o app roda com uma instalação normal de Python.

## Traduções

As traduções da interface e dos relatórios ficam em `i18n.py`. As traduções da documentação ficam ao lado dos originais em inglês usando o sufixo `_pt.md`.

Ao adicionar um campo ou conceito visível ao usuário:

1. Adicione rótulo e texto de ajuda em inglês.
2. Adicione rótulo e texto de ajuda em português.
3. Use exemplos nos dois idiomas quando o conceito for fácil de confundir.
4. Mantenha os termos técnicos consistentes com o texto do relatório.
5. Atualize primeiro o Markdown em inglês e depois a tradução `_pt.md` correspondente.

## Casos de Exemplo

Exemplos baseados em fontes ficam em:

```text
examples/from_sources/
```

Cada JSON deve conter:

- campos normais de `StudyConfig`;
- um bloco `source_case` com:
  - `source_name`;
  - `source_url` ou `source_file`;
  - `real_life_problem`;
  - `calculator_expected`;
  - `note`, opcional.

O app ignora campos de metadados desconhecidos. Os testes usam esses campos.

## Esquema JSON

O schema de configuração fica em:

```text
schemas/study_config.schema.json
```

Mantenha-o alinhado com `StudyConfig` em `calculator.py`. Ao adicionar um campo de configuração, atualize as propriedades do schema e os testes. O schema permite propriedades adicionais de propósito, para que metadados dos exemplos e arquivos compatíveis com versões futuras ainda possam ser carregados pelo app.

## Testes

Execute:

```powershell
python -m unittest discover -s tests
```

Os testes devem cobrir:

- exemplos numéricos conhecidos;
- cada camada de correção;
- arquivos JSON de exemplo;
- comportamento de serialização da configuração;
- qualquer nova fórmula antes que ela apareça na interface.

Para fórmulas que diferem de software exato por um participante por grupo, documente o motivo nos metadados do exemplo e teste a aproximação pretendida pela própria calculadora.

## Estilo de Código

- Mantenha a calculadora sem dependências externas, salvo motivo forte.
- Mantenha código de interface fora de `calculator.py`.
- Use dataclasses para entradas e saídas.
- Arredonde necessidades amostrais para cima com `math.ceil`.
- Adicione avisos para armadilhas metodológicas em vez de aceitar entradas arriscadas silenciosamente.
- Mantenha comentários curtos e úteis.
- Preserve compatibilidade de JSON quando possível, ignorando campos desconhecidos.

## Ideias de Roadmap

Possíveis próximas funcionalidades:

- poder exato com distribuição t para duas médias independentes;
- desenhos pareados/pré-pós;
- desenhos de não inferioridade e equivalência;
- regressão e poder ajustado por covariáveis;
- modos de survey descritivo com população finita;
- exportação CSV da tabela de sensibilidade;
- exportação de relatório em PDF ou Markdown;
- modelos de relatório mais ricos em português;
- ícones e instaladores assinados para Windows e macOS.
