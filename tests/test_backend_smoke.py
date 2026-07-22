"""Smoke tests for the additive FastAPI backend."""

import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app
from careerhub_db import hash_password


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
        self.assertIn("/api/matching/analysis", paths)
        self.assertIn("/api/matching/invite", paths)
        self.assertIn("/api/cv/pdf", paths)
        self.assertIn("/api/profile/{user_email}/experiences", paths)
        self.assertIn("/api/profile/{user_email}/skills", paths)
        self.assertIn("/api/profile/{user_email}/skills/{skill_id}", paths)
        self.assertIn("/api/profile/{user_email}/experiences/{experience_id}/achievements", paths)
        self.assertIn("/api/cv/history/{user_email}", paths)
        self.assertIn("/api/cv/history/{user_email}/{cv_id}", paths)
        self.assertIn("/api/security/password/change", paths)
        self.assertIn("/api/security/password/reset/request", paths)
        self.assertIn("/api/security/password/reset/confirm", paths)
        self.assertIn("/api/security/2fa/setup/{email}", paths)
        self.assertIn("/api/security/2fa/confirm", paths)
        self.assertIn("/api/security/2fa/disable", paths)
        self.assertIn("/api/security/data/{email}", paths)
        self.assertIn("/api/security/account/delete", paths)
        self.assertIn("/api/recruiter/workspace/{email}", paths)
        self.assertIn("/api/communications/email/send", paths)

    def test_role_analysis_uses_actual_hr_job_description(self):
        response = self.client.post(
            "/api/matching/analysis",
            json={
                "job_description": "HR Advisor required with employee relations, recruitment, HRIS, compliance and conflict resolution experience.",
                "candidate_resume": "HR professional experienced in recruitment, HRIS and employee relations casework.",
            },
        )

        self.assertEqual(response.status_code, 200)
        analysis = response.json()
        self.assertIn("employee relations", analysis["matched_requirements"])
        self.assertIn("compliance", analysis["missing_requirements"])
        self.assertNotIn("react", analysis["requirements"])
        self.assertTrue(all(item["requirement"].lower() in analysis["missing_requirements"] for item in analysis["suggestions"]))

    def test_feedback_signature_uses_recruiter_profile(self):
        with patch("backend.routes.matching.generate_candidate_feedback", return_value="Regards,\n[Your Name]\n[Your Job Title]"):
            response = self.client.post(
                "/api/matching/feedback",
                json={
                    "job_description": "HR Advisor",
                    "candidate_resume": "HR experience",
                    "candidate_name": "Candidate",
                    "recruiter_name": "Alex Morgan",
                    "recruiter_job_title": "Talent Lead",
                },
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Alex Morgan", response.json()["feedback"])
        self.assertIn("Talent Lead", response.json()["feedback"])
        self.assertNotIn("[Your", response.json()["feedback"])

    def test_email_delivery_route_uses_provider_result(self):
        with patch("backend.routes.communications.send_recruiter_email", return_value={"success": True, "status": "delivered", "provider_status": 202, "message_id": "test-message"}):
            response = self.client.post("/api/communications/email/send", json={"recruiter_email": "recruiter@example.com", "to_email": "candidate@example.com", "subject": "Application update", "body": "Thank you"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message_id"], "test-message")


class SecurityFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.users_file = Path(self.temp_dir.name) / "users.json"
        self.email = "security-test@example.com"
        self.users_file.write_text(json.dumps({self.email: {"email": self.email, "password_hash": hash_password("OldPassword1")}}), encoding="utf-8")
        self.data_files = {}
        fixtures = {
            "PROFILES_FILE": {self.email: {"full_name": "Security Test"}},
            "WORK_EXP_FILE": {self.email: {"exp_test": {"id": "exp_test", "company": "Example"}}},
            "ACHIEVEMENTS_FILE": {"exp_test": {"ach_test": {"achievement": "Delivered"}}},
            "SKILLS_FILE": {self.email: {"skill_test": {"skill_name": "Testing"}}},
            "CVS_FILE": {self.email: {"cv_test": {"job_title": "Tester"}}},
            "USAGE_FILE": {self.email: {"count": 1}},
        }
        self.data_patches = []
        self.recruiter_file = Path(self.temp_dir.name) / "recruiter_workspaces.json"
        self.recruiter_file.write_text(json.dumps({self.email: {"job_title": "Test role"}}), encoding="utf-8")
        for constant, contents in fixtures.items():
            path = Path(self.temp_dir.name) / f"{constant.lower()}.json"
            path.write_text(json.dumps(contents), encoding="utf-8")
            self.data_files[constant] = path
            self.data_patches.append(patch(f"services.security_service.{constant}", str(path)))
        self.data_patches.append(patch("services.recruiter_service.RECRUITER_WORKSPACES_FILE", str(self.recruiter_file)))
        self.client = TestClient(app)
        self.users_patch = patch("services.security_service.USERS_FILE", str(self.users_file))
        self.db_users_patch = patch("careerhub_db.USERS_FILE", str(self.users_file))
        self.users_patch.start()
        self.db_users_patch.start()
        for data_patch in self.data_patches:
            data_patch.start()

    def tearDown(self):
        self.users_patch.stop()
        self.db_users_patch.stop()
        for data_patch in reversed(self.data_patches):
            data_patch.stop()
        self.temp_dir.cleanup()

    def test_password_reset_and_change(self):
        requested = self.client.post("/api/security/password/reset/request", json={"email": self.email})
        self.assertEqual(requested.status_code, 200)
        token = requested.json()["development_token"]

        confirmed = self.client.post("/api/security/password/reset/confirm", json={"email": self.email, "token": token, "new_password": "NewPassword2"})
        self.assertEqual(confirmed.status_code, 200)

        changed = self.client.post("/api/security/password/change", json={"email": self.email, "current_password": "NewPassword2", "new_password": "FinalPassword3"})
        self.assertEqual(changed.status_code, 200)

    def test_two_factor_setup_and_disable(self):
        import pyotp

        setup = self.client.post(f"/api/security/2fa/setup/{self.email}")
        self.assertEqual(setup.status_code, 200)
        code = pyotp.TOTP(setup.json()["secret"]).now()

        confirmed = self.client.post("/api/security/2fa/confirm", json={"email": self.email, "code": code})
        self.assertEqual(confirmed.status_code, 200)
        self.assertEqual(len(confirmed.json()["backup_codes"]), 6)

        challenged = self.client.post("/api/auth/login", json={"email": self.email, "password": "OldPassword1"})
        self.assertTrue(challenged.json()["requires_2fa"])
        verified = self.client.post("/api/auth/login", json={"email": self.email, "password": "OldPassword1", "otp_code": pyotp.TOTP(setup.json()["secret"]).now()})
        self.assertEqual(verified.status_code, 200)

        disable_code = pyotp.TOTP(setup.json()["secret"]).now()
        disabled = self.client.post("/api/security/2fa/disable", json={"email": self.email, "password": "OldPassword1", "code": disable_code})
        self.assertEqual(disabled.status_code, 200)

    def test_data_export_and_account_deletion(self):
        exported = self.client.get(f"/api/security/data/{self.email}")
        self.assertEqual(exported.status_code, 200)
        self.assertNotIn("password_hash", exported.json()["account"])
        self.assertEqual(exported.json()["profile"]["full_name"], "Security Test")

        deleted = self.client.post("/api/security/account/delete", json={"email": self.email, "password": "OldPassword1", "confirmation": self.email})
        self.assertEqual(deleted.status_code, 200)
        self.assertNotIn(self.email, json.loads(self.users_file.read_text(encoding="utf-8")))
        self.assertNotIn("exp_test", json.loads(self.data_files["ACHIEVEMENTS_FILE"].read_text(encoding="utf-8")))


class RecruiterPersistenceTests(unittest.TestCase):
    def test_workspace_round_trip(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace_file = Path(temp_dir) / "recruiter_workspaces.json"
            workspace_file.write_text("{}", encoding="utf-8")
            client = TestClient(app)
            email = "recruiter-test@example.com"
            payload = {"workspace": {"job_description": "Test Engineer\nMust know testing", "candidates": [{"name": "Example Candidate", "score": 82, "status": "Shortlist"}], "candidate_messages": {"Example Candidate": {"body": "Invite"}}, "threshold": 70, "has_reviewed": True}}
            with patch("services.recruiter_service.RECRUITER_WORKSPACES_FILE", str(workspace_file)):
                saved = client.put(f"/api/recruiter/workspace/{email}", json=payload)
                self.assertEqual(saved.status_code, 200)
                restored = client.get(f"/api/recruiter/workspace/{email}")
                self.assertEqual(restored.json()["workspace"]["candidates"][0]["score"], 82)
                deleted = client.delete(f"/api/recruiter/workspace/{email}")
                self.assertEqual(deleted.status_code, 200)
                self.assertIsNone(client.get(f"/api/recruiter/workspace/{email}").json()["workspace"])


if __name__ == "__main__":
    unittest.main()
