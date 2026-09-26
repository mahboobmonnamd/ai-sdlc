#!/usr/bin/env python3
"""Canonical runner for unit and integration evaluation contracts.

tools/eval_judge.py is the only scoring authority. The historical
EvaluationContractHarness sketch in P0-07 is not an evaluator.

A skill adapter is an object with execute(input) -> dict.
An orchestration adapter is an object with execute(scenario) -> dict
containing observed_route. Effect checks read a host EffectTrace, not an
effects list returned by the skill.

Plan-only and missing adapters stay NOT_RUN. A scripted or other fixture
adapter is FIXTURE, never LIVE. LIVE requires the adapter to set
live_behavior = True and the runner to be given an EffectTrace. This runner
does not write results.status back onto contract files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.eval_judge import (  # noqa: E402
    EffectTrace,
    scenario_passed,
    score_accuracy,
    with_host_effects,
)
from tools.run_integration_eval import IntegrationEvalRunner, load_adapter, load_contract  # noqa: E402


class UnitContractRunner:
    """Run one skill adapter against every scenario in a unit contract."""

    def __init__(self, skill, contract: dict, trace: EffectTrace | None = None):
        self.skill = skill
        self.contract = contract
        self.trace = trace
        self.results = []

    def run(self) -> dict:
        if self.skill is None:
            return {
                "status": "NOT_RUN",
                "reason": "no skill adapter registered; refusing to fake behavioral scores",
                "contract_id": self.contract.get("contract_id"),
                "scenario_count": len(self.contract.get("scenarios") or []),
                "behavioral_evidence": "NONE",
                "evaluator": "tools/eval_judge.py",
            }
        for scenario in self.contract.get("scenarios") or []:
            self.results.append(self.run_scenario(scenario))
        return {
            "status": "RUN",
            "contract_id": self.contract.get("contract_id"),
            "results": self.results,
            "evaluator": "tools/eval_judge.py",
            "behavioral_evidence": self._evidence(),
            "scores": self._scores(),
        }

    def run_scenario(self, scenario: dict) -> dict:
        sid = scenario.get("id") or scenario.get("scenario_id")
        actual = self.skill.execute(scenario.get("input") or scenario.get("inputs") or {})
        if not isinstance(actual, dict):
            return {"scenario_id": sid, "status": "RUN", "accuracy": 0.0, "passed": False}
        cleaned = with_host_effects(actual, self.trace)
        accuracy = score_accuracy(cleaned, scenario)
        return {
            "scenario_id": sid,
            "status": "RUN",
            "accuracy": accuracy,
            "passed": scenario_passed(accuracy, scenario, self.contract),
            "actual_output": cleaned,
        }

    def _evidence(self) -> str:
        if getattr(self.skill, "live_behavior", False) is not True:
            return "FIXTURE"
        if not isinstance(self.trace, EffectTrace):
            return "UNINSTRUMENTED"
        return "LIVE"

    def _scores(self) -> dict:
        run = [row for row in self.results if row.get("status") == "RUN"]
        if not run:
            return {"accuracy": 0.0, "scenarios_run": 0}
        accuracy = sum(row["accuracy"] for row in run) / len(run)
        return {
            "accuracy": accuracy,
            "scenarios_run": len(run),
            "scenarios_passed": sum(1 for row in run if row.get("passed")),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--skill-adapter", help="module:callable for a unit contract")
    parser.add_argument("--orchestration-adapter", help="module:callable for an integration contract")
    args = parser.parse_args(argv)

    contract = load_contract(args.contract)
    if contract.get("category") == "index":
        print("Refusing to evaluate a layout index.", file=sys.stderr)
        return 2

    if contract.get("category") == "integration" or contract.get("skill") == "core-development-loop":
        orchestration = None if args.plan_only or not args.orchestration_adapter else load_adapter(args.orchestration_adapter)
        result = IntegrationEvalRunner({}, contract, orchestration=orchestration).run()
    else:
        skill = None if args.plan_only or not args.skill_adapter else load_adapter(args.skill_adapter)
        result = UnitContractRunner(skill, contract).run()

    result["evaluator"] = "tools/eval_judge.py"
    print(json.dumps(result, indent=2))
    if args.plan_only or result.get("status") == "NOT_RUN":
        return 0
    failed = [row for row in result.get("results", []) if row.get("status") == "RUN" and not row.get("passed")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
