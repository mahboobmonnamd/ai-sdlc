import importlib.util
import unittest
from datetime import datetime, timezone
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "skills/projectstatus/scripts/render_dashboard.py"
spec = importlib.util.spec_from_file_location("projectstatus_dashboard", PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class DashboardTests(unittest.TestCase):
    def test_reconciles_and_escapes_untrusted_tracker_text(self):
        data = {
            "project": "<script>alert(1)</script>",
            "plan": {"url": "https://github.com/acme/repo/blob/main/plan", "revision": "r1",
                     "items": [{"issue": 1, "title": "One", "milestone": "M1"},
                               {"issue": 2, "title": "Two", "milestone": "M1"}]},
            "issues": [
                {"number": 1, "title": "<img src=x onerror=alert(2)>", "state": "open",
                 "labels": ["needs:implementation"], "milestone": "M1",
                 "url": "javascript:alert(3)", "updated_at": "2026-10-01T00:00:00Z"},
                {"number": 3, "title": "Added scope", "state": "closed", "milestone": "M1"}]
        }
        html = module.render(data, milestone="M1", now=datetime(2026,10,8,tzinfo=timezone.utc))
        self.assertIn("50%", html)
        self.assertIn("Plan issue #2", html)
        self.assertIn("Unplanned", html)
        self.assertIn("CLOSED (unverified)", html)
        self.assertIn("&lt;img", html)
        self.assertNotIn("<script>alert", html)
        self.assertNotIn('href="javascript:', html)

    def test_open_dependency_blocks_ready_and_missing_plan_is_incomplete(self):
        data = {"project": "Test", "issues": [
            {"number": 1, "state": "open", "labels": ["needs:implementation"], "blocked_by": [2]},
            {"number": 2, "state": "open"}]}
        html = module.render(data, now=datetime(2026,10,8,tzinfo=timezone.utc))
        self.assertIn("INCOMPLETE", html)
        self.assertIn("BLOCKED", html)
        self.assertIn("Authoritative plan", html)

if __name__ == "__main__":
    unittest.main()
