# File version: 2.1; date: 2026-05-12

import unittest


try:
    from intervention_sample_planner.web_app import app
except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional Flask install
    app = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


@unittest.skipIf(app is None, f"Flask web dependencies are not installed: {IMPORT_ERROR}")
class WebAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_and_default_config(self):
        health = self.client.get("/health")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(health.get_json()["status"], "ok")

        config = self.client.get("/api/default-config?language=en")
        self.assertEqual(config.status_code, 200)
        self.assertEqual(config.get_json()["language"], "en")

    def test_calculate_endpoint_uses_shared_engine(self):
        response = self.client.post(
            "/api/calculate",
            json={"effect_size_d": 0.5, "alpha": 0.05, "power": 0.8},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["summary"]["initial_valid"]["total"], 126)
        self.assertIn("sensitivity", payload)

    def test_report_exports(self):
        config = {"study_name": "Web report", "effect_size_d": 0.5}
        html = self.client.post("/api/report/html", json=config)
        self.assertEqual(html.status_code, 200)
        self.assertIn(b"<!doctype html>", html.data)

        pdf = self.client.post("/api/report/pdf", json=config)
        self.assertEqual(pdf.status_code, 200)
        self.assertTrue(pdf.data.startswith(b"%PDF-1.4"))

    def test_invalid_payload_returns_json_error(self):
        response = self.client.post("/api/calculate", json={"alpha": 2})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
