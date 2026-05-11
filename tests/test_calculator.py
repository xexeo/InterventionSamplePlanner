import unittest

from intervention_sample_planner import StudyConfig, calculate_plan, config_from_dict, config_to_dict


class CalculatorTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
