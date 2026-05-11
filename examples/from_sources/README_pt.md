# Casos de Exemplo Baseados em Fontes

<!-- File version: 1.0; date: 2026-05-11 -->

Política de documentação: `README.md` é o original canônico em inglês. Este arquivo é sua tradução em português.

Estes arquivos JSON foram feitos para serem carregados pelo app e pela suíte de testes.
Cada arquivo contém uma configuração normal do app e um bloco `source_case` com a fonte externa ou a fonte local `theoryintroduction_pt.md`, o problema de vida real e os resultados esperados para esta calculadora.

A calculadora usa as fórmulas de aproximação normal descritas no resumo metodológico em `theoryintroduction_pt.md`. Algumas ferramentas exatas, como G*Power ou R `pwr`, podem retornar um participante a mais por grupo porque usam distribuição t ou procedimentos exatos iterativos. Os exemplos documentam essa diferença quando ela importa.

Os exemplos atuais baseados em fontes incluem:

- `statsiq_teaching_method_d05.json`;
- `statsmasters_medium_effect_power90.json`;
- `methodology_two_proportions_completion_45_60.json`;
- `methodology_clustered_classroom_icc.json`;
- `dropout_correction_assignment_15_percent.json`.

Cada arquivo JSON inclui um campo `$schema` que aponta para `schemas/study_config.schema.json`.
