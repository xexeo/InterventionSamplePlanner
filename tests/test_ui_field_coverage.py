# File version: 2.1; date: 2026-05-12

from pathlib import Path
import re
import unittest

from intervention_sample_planner.calculator import StudyConfig
from intervention_sample_planner.gui import FIELD_GROUPS as GUI_FIELD_GROUPS
from intervention_sample_planner.gui import FIELD_TYPES as GUI_FIELD_TYPES


REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_APP_JS = REPO_ROOT / "intervention_sample_planner" / "web_static" / "app.js"
DERIVED_OR_NON_FIELD_UI = {"analysis_mode", "had_planned_sample", "range_override_fields"}


def grouped_fields(groups) -> set[str]:
    return {field for _group, fields in groups for field in fields}


def web_grouped_fields() -> set[str]:
    text = WEB_APP_JS.read_text(encoding="utf-8")
    field_groups_block = text.split("const FIELD_TYPES", 1)[0]
    return set(re.findall(r'"([a-z_]+)"', field_groups_block))


class UiFieldCoverageTests(unittest.TestCase):
    def test_tkinter_configuration_groups_cover_public_study_config_fields(self):
        config_fields = set(StudyConfig.__dataclass_fields__) - DERIVED_OR_NON_FIELD_UI
        self.assertTrue(config_fields.issubset(grouped_fields(GUI_FIELD_GROUPS)))
        self.assertIn("proportion_control", grouped_fields(GUI_FIELD_GROUPS))
        self.assertIn("proportion_intervention", grouped_fields(GUI_FIELD_GROUPS))

    def test_tkinter_field_types_cover_grouped_configuration_fields(self):
        self.assertTrue(grouped_fields(GUI_FIELD_GROUPS).issubset(GUI_FIELD_TYPES))

    def test_web_configuration_groups_cover_public_study_config_fields(self):
        config_fields = set(StudyConfig.__dataclass_fields__) - DERIVED_OR_NON_FIELD_UI
        web_fields = web_grouped_fields()
        self.assertTrue(config_fields.issubset(web_fields))
        self.assertIn("proportion_control", web_fields)
        self.assertIn("proportion_intervention", web_fields)


if __name__ == "__main__":
    unittest.main()
