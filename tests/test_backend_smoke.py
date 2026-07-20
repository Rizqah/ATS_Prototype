"""Smoke tests for the additive FastAPI backend."""

import unittest

from fastapi.testclient import TestClient

from backend.main import app


class BackendSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_render_cv_text(self):
        response = self.client.post(
            "/api/cv/render",
            json={
                "profile": {"full_name": "Test User"},
                "work_experiences": [],
                "achievements_by_experience": {},
                "skills": [],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Test User", response.json()["text"])

    def test_openapi_contains_core_routes(self):
        response = self.client.get("/openapi.json")
        paths = response.json()["paths"]

        self.assertIn("/api/auth/login", paths)
        self.assertIn("/api/matching/batch", paths)
        self.assertIn("/api/matching/invite", paths)
        self.assertIn("/api/cv/pdf", paths)


if __name__ == "__main__":
    unittest.main()
