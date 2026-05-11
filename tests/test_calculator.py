# File version: 1.0; date: 2026-05-11

import unittest
import json
from pathlib import Path

from intervention_sample_planner import (
    APP_VERSION,
    APP_WINDOW_TITLE,
    StudyConfig,
    calculate_plan,
    config_from_dict,
    config_to_dict,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_EXAMPLES = REPO_ROOT / "examples" / "from_sources"
SCHEMA_PATH = REPO_ROOT / "schemas" / "study_config.schema.json"


class CalculatorTests(unittest.TestCase):
    def test_application_version_metadata(self):
        self.assertEqual(APP_VERSION, "1.0")
        self.assertIn("ISP v1.0", APP_WINDOW_TITLE)

    def test_continuous_balanced_example_from_methodology_chapter(self):
        config = StudyConfig(effect_size_d=0.5, alpha=0.05, power=0.80)
        plan = calculate_plan(config)

        self.assertEqual(plan.initial_valid.control, 63)
        self.assertEqual(plan.initial_valid.intervention, 63)
        self.assertEqual(plan.initial_valid.total, 126)

    def test_completion_correction_increases_assigned_sample(self):
        config = StudyConfig(effect_size_d=0.5, completion_rate=0.85)
        plan = calculate_plan(config)

        self.assertEqual(plan.initial_valid.control, 63)
        self.assertEqual(plan.assigned_needed.control, 75)
        self.assertEqual(plan.assigned_needed.total, 150)

    def test_two_proportions_example_from_methodology_chapter(self):
        config = StudyConfig(
            outcome_type="binary",
            proportion_control=0.45,
            proportion_intervention=0.60,
            alpha=0.05,
            power=0.80,
        )
        plan = calculate_plan(config)

        self.assertEqual(plan.initial_valid.control, 173)
        self.assertEqual(plan.initial_valid.intervention, 173)
        self.assertEqual(plan.initial_valid.total, 346)

    def test_cluster_design_effect(self):
        config = StudyConfig(
            effect_size_d=0.5,
            cluster_average_size=25,
            intraclass_correlation=0.05,
        )
        plan = calculate_plan(config)

        self.assertAlmostEqual(plan.design_effect, 2.2)
        self.assertEqual(plan.design_adjusted_valid.control, 139)
        self.assertEqual(plan.design_adjusted_valid.intervention, 139)
        self.assertEqual(plan.design_adjusted_valid.total, 278)

    def test_config_roundtrip_ignores_unknown_fields(self):
        data = config_to_dict(StudyConfig(study_name="Roundtrip"))
        data["unknown"] = "ignored"
        config = config_from_dict(data)

        self.assertEqual(config.study_name, "Roundtrip")
        self.assertFalse(hasattr(config, "unknown"))

    def test_source_examples_match_expected_outputs(self):
        cases = sorted(SOURCE_EXAMPLES.glob("*.json"))
        self.assertGreaterEqual(len(cases), 5)

        for case_path in cases:
            with self.subTest(case=case_path.name):
                data = json.loads(case_path.read_text(encoding="utf-8"))
                expected = data["source_case"]["calculator_expected"]
                config = config_from_dict(data)
                plan = calculate_plan(config)

                checks = {
                    "initial_valid_control": plan.initial_valid.control,
                    "initial_valid_intervention": plan.initial_valid.intervention,
                    "initial_valid_total": plan.initial_valid.total,
                    "design_adjusted_valid_control": plan.design_adjusted_valid.control,
                    "design_adjusted_valid_intervention": plan.design_adjusted_valid.intervention,
                    "design_adjusted_valid_total": plan.design_adjusted_valid.total,
                    "assigned_control": plan.assigned_needed.control,
                    "assigned_intervention": plan.assigned_needed.intervention,
                    "assigned_total": plan.assigned_needed.total,
                }

                for key, expected_value in expected.items():
                    if key == "design_effect":
                        self.assertAlmostEqual(plan.design_effect, expected_value)
                    else:
                        self.assertEqual(checks[key], expected_value)

    def test_json_schema_covers_study_config_fields(self):
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        properties = schema["properties"]
        config_fields = set(StudyConfig.__dataclass_fields__)

        self.assertTrue(SCHEMA_PATH.exists())
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertTrue(config_fields.issubset(properties))
        self.assertIn("$schema", properties)
        self.assertIn("_file_version", properties)
        self.assertIn("_file_date", properties)
        self.assertIn("source_case", properties)

    def test_examples_reference_existing_json_schema(self):
        examples = sorted((REPO_ROOT / "examples").glob("*.json"))
        examples.extend(sorted(SOURCE_EXAMPLES.glob("*.json")))
        self.assertGreaterEqual(len(examples), 7)

        for example_path in examples:
            with self.subTest(example=example_path.name):
                data = json.loads(example_path.read_text(encoding="utf-8"))
                schema_ref = data.get("$schema")
                self.assertIsNotNone(schema_ref)
                resolved = (example_path.parent / schema_ref).resolve()
                self.assertEqual(resolved, SCHEMA_PATH.resolve())


if __name__ == "__main__":
    unittest.main()
