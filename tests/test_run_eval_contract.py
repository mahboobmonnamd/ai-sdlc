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

    def test_scripted_adapter_scores_effects_without_marking_files_run(self):
        contract = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        clean = UnitContractRunner(
            Scripted(
                {
                    "plan_status": "PROPOSED",
                    "effects": ["handoff_to_plan_acceptance"],
                    "required_behaviors_satisfied": True,
                }
            ),
            contract,
        ).run()
        self.assertEqual(clean["status"], "RUN")
        self.assertEqual(clean["behavioral_evidence"], "LIVE")
        self.assertTrue(clean["results"][0]["passed"])
        self.assertNotIn("required_behaviors_satisfied", clean["results"][0]["actual_output"])

        missing_effects = UnitContractRunner(
            Scripted({"plan_status": "PROPOSED"}),
            contract,
        ).run()
        self.assertEqual(missing_effects["results"][0]["accuracy"], 0.0)
        self.assertFalse(missing_effects["results"][0]["passed"])
        self.assertEqual(json.loads(EXAMPLE.read_text(encoding="utf-8"))["results"]["status"], "NOT_RUN")

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
