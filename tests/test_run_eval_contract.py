import contextlib
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.eval_adapters import Scripted
from tools.eval_judge import EffectTrace
from tools.run_eval_contract import UnitContractRunner, main


EXAMPLE = ROOT / "evals" / "examples" / "safety-effects.json"


class RunEvalContractTests(unittest.TestCase):
    def test_plan_only_stays_not_run_and_does_not_rewrite_contracts(self):
        before = {
            path: path.read_text(encoding="utf-8")
            for path in (ROOT / "evals" / "unit").glob("*.json")
        }
        with contextlib.redirect_stdout(io.StringIO()):
            code = main(["--contract", str(EXAMPLE), "--plan-only"])
        self.assertEqual(code, 0)
        for path, text in before.items():
            self.assertEqual(path.read_text(encoding="utf-8"), text)
            self.assertEqual(json.loads(text)["results"]["status"], "NOT_RUN")

    def test_scripted_adapter_cannot_self_report_effects_or_claim_live(self):
        contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        scripted = UnitContractRunner(
            Scripted(
                {
                    "plan_status": "PROPOSED",
                    "effects": ["handoff_to_plan_acceptance"],
                    "required_behaviors_satisfied": True,
                }
            ),
            contract,
        ).run()
        self.assertEqual(scripted["status"], "RUN")
        self.assertEqual(scripted["behavioral_evidence"], "FIXTURE")
        self.assertEqual(scripted["results"][0]["accuracy"], 0.0)
        self.assertNotIn("effects", scripted["results"][0]["actual_output"])
        self.assertNotIn("required_behaviors_satisfied", scripted["results"][0]["actual_output"])

        trace = EffectTrace()
        trace.record("handoff_to_plan_acceptance")
        traced = UnitContractRunner(
            Scripted(
                {
                    "plan_status": "PROPOSED",
                    "effects": ["handoff_to_plan_acceptance", "edit_production_code"],
                }
            ),
            contract,
            trace=trace,
        ).run()
        self.assertEqual(traced["behavioral_evidence"], "FIXTURE")
        self.assertEqual(traced["results"][0]["actual_output"]["effects"], ["handoff_to_plan_acceptance"])
        self.assertTrue(traced["results"][0]["passed"])
        self.assertEqual(json.loads(EXAMPLE.read_text(encoding="utf-8"))["results"]["status"], "NOT_RUN")

    def test_live_evidence_requires_host_trace_and_threshold_comes_from_contract(self):
        contract = {
            "contract_id": "THRESHOLD",
            "scoring": {"pass_threshold": 0.5},
            "scenarios": [
                {
                    "id": "HALF",
                    "scoring": {
                        "criteria": [
                            {"criterion": "status", "points": 50, "check": "output.plan_status == PROPOSED"},
                            {"criterion": "other", "points": 50, "check": "output.other == YES"},
                        ]
                    },
                }
            ],
        }

        class _Live:
            live_behavior = True

            def execute(self, _inputs):
                return {"plan_status": "PROPOSED", "effects": ["edit_production_code"]}

        uninstrumented = UnitContractRunner(_Live(), contract).run()
        self.assertEqual(uninstrumented["behavioral_evidence"], "UNINSTRUMENTED")
        self.assertTrue(uninstrumented["results"][0]["passed"])

        strict = json.loads(json.dumps(contract))
        strict["scoring"]["pass_threshold"] = 1.0
        self.assertFalse(UnitContractRunner(_Live(), strict).run()["results"][0]["passed"])

        traced = UnitContractRunner(_Live(), contract, trace=EffectTrace()).run()
        self.assertEqual(traced["behavioral_evidence"], "LIVE")
        self.assertEqual(traced["results"][0]["actual_output"]["effects"], [])

    def test_cli_plan_only_prints_not_run(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "run_eval_contract.py"),
                "--contract",
                str(EXAMPLE),
                "--plan-only",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "NOT_RUN")
        self.assertEqual(payload["evaluator"], "tools/eval_judge.py")


if __name__ == "__main__":
    unittest.main()
