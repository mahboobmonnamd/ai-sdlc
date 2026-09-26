#!/usr/bin/env python3
"""Multi-skill integration evaluation runner.

The documented P0-07 EvaluationContractHarness binds one skill_instance.
Integration contracts declare scenarios/routes that span skills; this runner
dispatches each scenario to the skill named in scenario['skill'] when present,
or records route-only scenarios for adapter-driven orchestration.

Behavioral execution requires a live skill adapter registry. Without adapters,
this tool validates dispatch wiring and exits with status NOT_RUN rather than
pretending the single-skill harness scored the multi-skill file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class IntegrationEvalRunner:
    """Dispatch integration/unit scenarios across multiple skill instances."""

    def __init__(self, skill_registry: dict, contract: dict):
        """
        skill_registry: mapping of skill name -> object with .execute(input) -> dict
        contract: loaded integration (or multi-skill) contract
        """
        self.skills = skill_registry
        self.contract = contract
        self.results = []

    def scenarios(self) -> list[dict]:
        return list(self.contract.get("scenarios") or self.contract.get("integration_scenarios") or [])

    def run(self) -> dict:
        if not self.skills:
            return {
                "status": "NOT_RUN",
                "reason": "no skill adapters registered; refusing to fake behavioral scores",
                "contract_id": self.contract.get("contract_id"),
                "scenario_count": len(self.scenarios()),
                "dispatch_plan": self.dispatch_plan(),
            }

        for scenario in self.scenarios():
            self.results.append(self.run_scenario(scenario))
        return {
            "status": "RUN",
            "contract_id": self.contract.get("contract_id"),
            "results": self.results,
            "scores": self.score_results(),
        }

    def dispatch_plan(self) -> list[dict]:
        plan = []
        for scenario in self.scenarios():
            sid = scenario.get("id") or scenario.get("scenario_id")
            skill = scenario.get("skill")
            if skill:
                plan.append({"scenario_id": sid, "dispatch": "skill", "skill": skill})
            elif scenario.get("expected_route"):
                plan.append(
                    {
                        "scenario_id": sid,
                        "dispatch": "route",
                        "expected_route": scenario["expected_route"],
                    }
                )
            else:
                plan.append({"scenario_id": sid, "dispatch": "unspecified"})
        return plan

    def run_scenario(self, scenario: dict) -> dict:
        sid = scenario.get("id") or scenario.get("scenario_id")
        skill_name = scenario.get("skill")
        if not skill_name:
            return {
                "scenario_id": sid,
                "status": "NOT_RUN",
                "reason": "route-only scenario requires an orchestration adapter",
            }
        skill = self.skills.get(skill_name)
        if skill is None:
            return {
                "scenario_id": sid,
                "status": "NOT_RUN",
                "reason": f"no adapter registered for skill '{skill_name}'",
            }
        actual = skill.execute(scenario.get("input") or scenario.get("inputs") or {})
        accuracy = self.score_accuracy(actual, scenario)
        return {
            "scenario_id": sid,
            "skill": skill_name,
            "status": "RUN",
            "accuracy": accuracy,
            "passed": accuracy >= 0.9,
            "actual_output": actual,
        }

    def score_accuracy(self, actual, scenario) -> float:
        """Compatible with P0-07 EvaluationContractHarness.score_accuracy semantics."""
        if actual is None:
            return 0.0
        criteria = (scenario.get("scoring") or {}).get("criteria") or []
        total = sum(c.get("points", 0) for c in criteria)
        if total <= 0:
            return 0.0
        earned = 0
        expected = scenario.get("expected_output") or {}
        for criterion in criteria:
            check = criterion.get("check") or ""
            if self._evaluate_check(check, actual, expected):
                earned += criterion.get("points", 0)
        return earned / total

    def _evaluate_check(self, check_expr: str, actual, expected) -> bool:
        if "==" in check_expr:
            left_s, right_s = [p.strip() for p in check_expr.split("==", 1)]
            left = self._resolve(left_s, actual, expected)
            right = self._parse_literal(right_s)
            return left == right
        if "contains" in check_expr:
            left_s, right_s = [p.strip() for p in check_expr.split("contains", 1)]
            left = self._resolve(left_s, actual, expected)
            right = self._parse_literal(right_s)
            return isinstance(left, str) and right in left
        return False

    def _resolve(self, path: str, actual, expected):
        path = path.replace("output.", "").replace("actual.", "")
        if path.startswith("expected."):
            obj = expected
            path = path[len("expected.") :]
        else:
            obj = actual
        current = obj
        for part in path.split("."):
            if not part:
                continue
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _parse_literal(self, value_str: str):
        value_str = value_str.strip().strip("'\"")
        if value_str.lower() in ("true", "false"):
            return value_str.lower() == "true"
        try:
            return int(value_str)
        except ValueError:
            return value_str

    def score_results(self) -> dict:
        run = [r for r in self.results if r.get("status") == "RUN"]
        if not run:
            return {"accuracy": 0.0, "scenarios_run": 0}
        accuracy = sum(r.get("accuracy", 0) for r in run) / len(run)
        return {
            "accuracy": accuracy,
            "scenarios_run": len(run),
            "scenarios_passed": sum(1 for r in run if r.get("passed")),
        }


def load_contract(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=ROOT / "evals" / "integration" / "core-development-loop.json",
        help="Integration contract path",
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Print dispatch plan without requiring skill adapters (status NOT_RUN)",
    )
    args = parser.parse_args(argv)

    contract = load_contract(args.contract)
    if contract.get("category") == "index":
        print(
            "Refusing to treat the layout index as an executable integration contract. "
            "Pass evals/integration/core-development-loop.json.",
            file=sys.stderr,
        )
        return 2

    runner = IntegrationEvalRunner(skill_registry={}, contract=contract)
    result = runner.run()
    print(json.dumps(result, indent=2))
    # Without adapters, NOT_RUN is the honest outcome (exit 0 for plan-only wiring check).
    if args.plan_only or result.get("status") == "NOT_RUN":
        return 0
    failed = [r for r in result.get("results", []) if r.get("status") == "RUN" and not r.get("passed")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
