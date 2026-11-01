import unittest
import json
import subprocess
import sys
from pathlib import Path

from tools.eval_judge import EffectTrace
from tools.run_integration_eval import IntegrationEvalRunner

def contract():
    return {
        "contract_id": "EVIDENCE-PROVENANCE",
        "scoring": {"pass_threshold": 1.0},
        "scenarios": [
            {"id": name, "expected_route": [name], "scoring": {"criteria": [
                {"criterion": "route", "points": 100,
                 "check": "output.observed_route == expected.expected_route"},
            ]}}
            for name in ("first", "second")
        ],
    }


class EchoFixture:
    live_behavior = True

    def __init__(self, trace):
        self.trace = trace

    def execute(self, scenario):
        self.trace.record("observed_" + scenario["id"])
        # A fake agent response is never an authoritative effect trace.
        return {"observed_route": scenario["expected_route"], "effects": ["invented"]}


class EvidenceProvenanceTests(unittest.TestCase):
    def test_fixture_remains_non_live_even_with_trace_and_live_flag(self):
        trace = EffectTrace()
        result = IntegrationEvalRunner({}, contract(), EchoFixture(trace), trace).run()
        self.assertEqual(result["behavioral_evidence"], "WIRING_FIXTURE_ONLY")
        self.assertFalse(result["acceptance_ready"])
        self.assertTrue(all(item["passed"] for item in result["results"]))

    def test_effects_are_scoped_to_each_scenario_not_replayed(self):
        trace = EffectTrace()
        result = IntegrationEvalRunner({}, contract(), EchoFixture(trace), trace).run()
        first, second = result["results"]
        self.assertEqual(first["actual_output"]["effects"], ["observed_first"])
        self.assertEqual(second["actual_output"]["effects"], ["observed_second"])
        self.assertNotIn("invented", second["actual_output"]["effects"])

    def test_cli_rejects_fixture_as_release_evidence(self):
        script = Path(__file__).resolve().parents[1] / "tools" / "run_integration_eval.py"
        base = [sys.executable, str(script), "--orchestration-adapter",
                "tests.eval_adapters:wiring_orchestrator"]
        normal = subprocess.run(base, cwd=script.parents[1], capture_output=True, text=True)
        strict = subprocess.run(base + ["--require-live"],
                                cwd=script.parents[1], capture_output=True, text=True)
        self.assertEqual(normal.returncode, 0, normal.stderr)
        self.assertEqual(strict.returncode, 1, strict.stderr)
        result = json.loads(strict.stdout)
        self.assertEqual(result["behavioral_evidence"], "WIRING_FIXTURE_ONLY")
        self.assertFalse(result["acceptance_ready"])

    def test_uninstrumented_adapter_is_not_live(self):
        class ExternalAdapter:
            __module__ = "external_host"
            live_behavior = True

            def execute(self, scenario):
                return {"observed_route": scenario["expected_route"]}

        result = IntegrationEvalRunner({}, contract(), ExternalAdapter()).run()
        self.assertEqual(result["behavioral_evidence"], "UNINSTRUMENTED")
        self.assertFalse(result["acceptance_ready"])

    def test_live_adapter_cannot_forge_a_route_without_host_dispatch(self):
        class ExternalAdapter:
            __module__ = "external_host"
            live_behavior = True

            def execute(self, scenario):
                return {"observed_route": scenario["expected_route"]}

        trace = EffectTrace()
        result = IntegrationEvalRunner({}, contract(), ExternalAdapter(), trace).run()
        self.assertEqual(result["behavioral_evidence"], "LIVE")
        self.assertFalse(result["acceptance_ready"])
        for row in result["results"]:
            self.assertEqual(row["actual_output"]["observed_route"], [])
            self.assertFalse(row["passed"])

    def test_host_instrumented_route_is_derived_from_dispatch(self):
        trace = EffectTrace()

        class ExternalAdapter:
            __module__ = "external_host"
            live_behavior = True

            def execute(self, scenario):
                trace.record("route:" + scenario["id"])
                return {"observed_route": ["forged"]}

        result = IntegrationEvalRunner({}, contract(), ExternalAdapter(), trace).run()
        self.assertEqual(result["behavioral_evidence"], "LIVE")
        self.assertTrue(result["acceptance_ready"])
        self.assertTrue(all(row["passed"] for row in result["results"]))
        self.assertEqual(result["results"][1]["actual_output"]["observed_route"], ["second"])

    def test_live_route_needs_no_adapter_reported_route(self):
        trace = EffectTrace()

        class ExternalAdapter:
            __module__ = "external_host"
            live_behavior = True

            def execute(self, scenario):
                trace.record("route:" + scenario["id"])
                return {}

        result = IntegrationEvalRunner({}, contract(), ExternalAdapter(), trace).run()
        self.assertTrue(result["acceptance_ready"])
        self.assertTrue(all(row["passed"] for row in result["results"]))

    def test_repeated_run_does_not_accumulate_old_scenarios(self):
        trace = EffectTrace()
        runner = IntegrationEvalRunner({}, contract(), EchoFixture(trace), trace)
        self.assertEqual(len(runner.run()["results"]), 2)
        self.assertEqual(len(runner.run()["results"]), 2)

    def test_incomplete_route_never_qualifies_even_with_live_protocol(self):
        class ExternalAdapter:
            __module__ = "external_host"
            live_behavior = True

            def execute(self, scenario):
                return {"observed_route": []}

        trace = EffectTrace()
        result = IntegrationEvalRunner({}, contract(), ExternalAdapter(), trace).run()
        self.assertEqual(result["behavioral_evidence"], "LIVE")
        self.assertFalse(result["acceptance_ready"])


if __name__ == "__main__":
    unittest.main()
