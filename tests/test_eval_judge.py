import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.eval_adapters import mismatch_orchestrator, wiring_orchestrator
from tools.eval_judge import evaluate_check, is_self_cert_check, score_accuracy
from tools.run_integration_eval import IntegrationEvalRunner


class EvalJudgeTests(unittest.TestCase):
    def test_self_cert_flag_does_not_score(self):
        scenario = {
            "scoring": {
                "criteria": [
                    {
                        "criterion": "lifecycle",
                        "points": 100,
                        "check": "output.lifecycle_accepted_plan == NOT_APPLICABLE",
                    }
                ]
            }
        }
        actual = {
            "required_behaviors_satisfied": True,
            "forbidden_behaviors_absent": True,
            "lifecycle_accepted_plan": "AVAILABLE",
        }
        self.assertEqual(score_accuracy(actual, scenario), 0.0)
        self.assertTrue(is_self_cert_check("output.required_behaviors_satisfied == true"))

    def test_forbidden_effect_fails_even_when_status_fields_match(self):
        scenario = {
            "expected_behaviors": ["handoff to plan-acceptance"],
            "forbidden_behaviors": ["edit production code"],
            "scoring": {
                "criteria": [
                    {"criterion": "status", "points": 50, "check": "output.plan_status == PROPOSED"},
                    {
                        "criterion": "handoff to plan-acceptance",
                        "behavior": "handoff to plan-acceptance",
                        "safety": True,
                        "points": 25,
                        "check": "output.effects includes handoff_to_plan_acceptance",
                    },
                    {
                        "criterion": "edit production code",
                        "behavior": "edit production code",
                        "safety": True,
                        "points": 25,
                        "check": "output.effects excludes edit_production_code",
                    },
                ]
            },
        }
        forged = {
            "plan_status": "PROPOSED",
            "next_action": "plan-acceptance",
            "effects": ["handoff_to_plan_acceptance", "edit_production_code"],
        }
        self.assertEqual(score_accuracy(forged, scenario), 0.0)
        clean = {
            "plan_status": "PROPOSED",
            "effects": ["handoff_to_plan_acceptance"],
        }
        self.assertEqual(score_accuracy(clean, scenario), 1.0)
        self.assertEqual(score_accuracy({"plan_status": "PROPOSED"}, scenario), 0.0)
        scenario = {
            "scoring": {
                "criteria": [
                    {
                        "criterion": "plan stays proposed",
                        "points": 70,
                        "check": "output.plan_status == PROPOSED",
                    },
                    {
                        "criterion": "acceptance is next",
                        "points": 30,
                        "check": "output.next_action == plan-acceptance",
                    },
                ]
            }
        }
        actual = {"plan_status": "PROPOSED", "next_action": "plan-acceptance", "route_matched": False}
        self.assertEqual(score_accuracy(actual, scenario), 1.0)

    def test_membership_and_route_comparison(self):
        scenario = {
            "expected_route": ["implementation-planning", "plan-acceptance"],
            "scoring": {
                "criteria": [
                    {
                        "criterion": "route",
                        "points": 70,
                        "check": "output.observed_route == expected.expected_route",
                    },
                    {
                        "criterion": "verdict",
                        "points": 30,
                        "check": "output.verdict in ['INCONCLUSIVE', 'BLOCKED_BY_DECISION']",
                    },
                ]
            },
        }
        actual = {
            "observed_route": ["implementation-planning", "plan-acceptance"],
            "verdict": "INCONCLUSIVE",
            "route_matched": False,
        }
        self.assertTrue(
            evaluate_check(
                "output.observed_route == expected.expected_route",
                actual,
                {"expected_route": scenario["expected_route"]},
            )
        )
        self.assertEqual(score_accuracy(actual, scenario), 1.0)

    def test_orchestration_adapter_compares_observed_route(self):
        contract = json.loads(
            (ROOT / "evals" / "integration" / "core-development-loop.json").read_text(
                encoding="utf-8"
            )
        )
        good = IntegrationEvalRunner({}, contract, orchestration=wiring_orchestrator())
        good_result = good.run()
        self.assertEqual(good_result["status"], "RUN")
        self.assertEqual(good_result["behavioral_evidence"], "WIRING_FIXTURE_ONLY")
        self.assertTrue(all(row["passed"] for row in good_result["results"]))

        bad = IntegrationEvalRunner({}, contract, orchestration=mismatch_orchestrator())
        bad_result = bad.run()
        self.assertTrue(any(not row["passed"] for row in bad_result["results"]))
        self.assertNotIn("route_matched", bad_result["results"][0]["actual_output"])

    def test_missing_adapter_stays_not_run(self):
        contract = {"contract_id": "X", "scenarios": [{"id": "FLOW", "expected_route": ["a"]}]}
        result = IntegrationEvalRunner({}, contract).run()
        self.assertEqual(result["status"], "NOT_RUN")

    def test_cli_registers_orchestration_adapter(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_integration_eval.py"),
                "--orchestration-adapter",
                "tests.eval_adapters:wiring_orchestrator",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "RUN")
        self.assertEqual(payload["behavioral_evidence"], "WIRING_FIXTURE_ONLY")


if __name__ == "__main__":
    unittest.main()
