# File version: 2.2; date: 2026-05-17

import ast
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from intervention_sample_planner.calculator import StudyConfig
from intervention_sample_planner.gui import (
    FIELD_GROUPS as GUI_FIELD_GROUPS,
    FIELD_TYPES as GUI_FIELD_TYPES,
    valid_outcome_types,
    visible_config_fields_for_path,
    wizard_fields_for_path,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = REPO_ROOT / "intervention_sample_planner"
WEB_APP_JS = PACKAGE_ROOT / "web_static" / "app.js"
DERIVED_OR_NON_FIELD_UI = {"analysis_mode", "had_planned_sample", "range_override_fields"}
WORKFLOW_PATHS = ("plan_study", "evaluate_done", "evaluate_against_plan")
STUDY_DESIGNS = ("parallel_two_group", "pretest_posttest_control", "one_group_pre_post")


def grouped_fields(groups) -> set[str]:
    return {field for _group, fields in groups for field in fields}


def web_grouped_fields() -> set[str]:
    text = WEB_APP_JS.read_text(encoding="utf-8")
    field_groups_block = text.split("const FIELD_TYPES", 1)[0]
    return set(re.findall(r'"([a-z_]+)"', field_groups_block))


def wizard_scenarios():
    for workflow_path in WORKFLOW_PATHS:
        for study_design in STUDY_DESIGNS:
            for outcome_type in valid_outcome_types(study_design, workflow_path):
                yield workflow_path, study_design, outcome_type


def function_body_field_uses() -> set[str]:
    fields = set(StudyConfig.__dataclass_fields__)
    uses: set[str] = set()

    class Visitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.function_depth = 0

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self.function_depth += 1
            self.generic_visit(node)
            self.function_depth -= 1

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_Attribute(self, node: ast.Attribute) -> None:
            if self.function_depth and node.attr in fields:
                uses.add(node.attr)
            self.generic_visit(node)

        def visit_Constant(self, node: ast.Constant) -> None:
            if self.function_depth and isinstance(node.value, str) and node.value in fields:
                uses.add(node.value)

    for path in PACKAGE_ROOT.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        Visitor().visit(tree)
    return uses


def web_runtime_check_script() -> str:
    scenarios = []
    for workflow_path, study_design, outcome_type in wizard_scenarios():
        scenarios.append(
            {
                "workflow_path": workflow_path,
                "study_design": study_design,
                "outcome_type": outcome_type,
                "expectedWizard": wizard_fields_for_path(workflow_path, study_design, outcome_type),
                "expectedVisible": visible_config_fields_for_path(workflow_path, study_design, outcome_type),
            }
        )
    app_js = WEB_APP_JS.read_text(encoding="utf-8")
    return f"""
global.document = {{
  addEventListener() {{}},
  querySelectorAll() {{ return []; }},
  getElementById() {{ return null; }},
  documentElement: {{}}
}};
global.window = {{}};
{app_js}
const scenarios = {json.dumps(scenarios)};
const failures = [];
for (const scenario of scenarios) {{
  config = {{
    workflow_path: scenario.workflow_path,
    study_design: scenario.study_design,
    outcome_type: scenario.outcome_type
  }};
  normalizeWorkflow();
  const actualWizard = wizardFields();
  const actualVisible = FIELD_GROUPS.flatMap(([, fields]) => fields).filter((field) => showField(field));
  if (JSON.stringify(actualWizard) !== JSON.stringify(scenario.expectedWizard)) {{
    failures.push(`wizard ${{scenario.workflow_path}}/${{scenario.study_design}}/${{scenario.outcome_type}}: ${{JSON.stringify(actualWizard)}}`);
  }}
  if (JSON.stringify([...actualVisible].sort()) !== JSON.stringify([...scenario.expectedVisible].sort())) {{
    failures.push(`visible ${{scenario.workflow_path}}/${{scenario.study_design}}/${{scenario.outcome_type}}: ${{JSON.stringify(actualVisible)}}`);
  }}
}}
if (failures.length) {{
  console.error(failures.join("\\n"));
  process.exit(1);
}}
"""


class UiFieldCoverageTests(unittest.TestCase):
    def test_configuration_variable_tabs_are_equal_between_tkinter_and_web(self):
        self.assertEqual(grouped_fields(GUI_FIELD_GROUPS), web_grouped_fields())

    def test_configuration_variable_tabs_cover_public_study_config_fields(self):
        config_fields = set(StudyConfig.__dataclass_fields__) - DERIVED_OR_NON_FIELD_UI
        self.assertEqual(config_fields, grouped_fields(GUI_FIELD_GROUPS))

    def test_tkinter_field_types_cover_grouped_configuration_fields(self):
        self.assertTrue(grouped_fields(GUI_FIELD_GROUPS).issubset(GUI_FIELD_TYPES))

    def test_all_wizard_paths_ask_only_visible_configuration_variables(self):
        for workflow_path, study_design, outcome_type in wizard_scenarios():
            with self.subTest(workflow_path=workflow_path, study_design=study_design, outcome_type=outcome_type):
                wizard_fields = wizard_fields_for_path(workflow_path, study_design, outcome_type)
                visible_fields = set(visible_config_fields_for_path(workflow_path, study_design, outcome_type))
                self.assertEqual(len(wizard_fields), len(set(wizard_fields)))
                self.assertTrue(set(wizard_fields).issubset(visible_fields))

    def test_web_wizard_paths_and_visible_fields_match_tkinter_rules(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is not available for web UI rule execution.")
        handle = tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".js", delete=False)
        try:
            with handle:
                handle.write(web_runtime_check_script())
            result = subprocess.run([node, handle.name], capture_output=True, text=True, timeout=20, check=False)
        finally:
            Path(handle.name).unlink(missing_ok=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_wizard_paths_include_the_conditional_variables_the_user_needs(self):
        self.assertIn(
            "proportion_control",
            wizard_fields_for_path("plan_study", "parallel_two_group", "binary"),
        )
        self.assertIn(
            "proportion_intervention",
            wizard_fields_for_path("plan_study", "parallel_two_group", "binary"),
        )
        self.assertIn(
            "extra_buffer_rate",
            wizard_fields_for_path("plan_study", "parallel_two_group", "continuous"),
        )
        self.assertIn(
            "observed_pre_success_post_failure",
            wizard_fields_for_path("evaluate_done", "one_group_pre_post", "binary"),
        )
        self.assertIn(
            "planned_effect_size",
            wizard_fields_for_path("evaluate_against_plan", "parallel_two_group", "continuous"),
        )

    def test_every_configuration_tab_variable_is_used_by_runtime_functions(self):
        unused_fields = grouped_fields(GUI_FIELD_GROUPS) - function_body_field_uses()
        self.assertEqual(set(), unused_fields)

    def test_every_wizard_variable_in_every_path_is_used_by_runtime_functions(self):
        used_fields = function_body_field_uses()
        for workflow_path, study_design, outcome_type in wizard_scenarios():
            with self.subTest(workflow_path=workflow_path, study_design=study_design, outcome_type=outcome_type):
                unused_fields = set(wizard_fields_for_path(workflow_path, study_design, outcome_type)) - used_fields
                self.assertEqual(set(), unused_fields)


if __name__ == "__main__":
    unittest.main()
