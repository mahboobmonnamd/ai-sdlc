#!/usr/bin/env python3
"""Multi-skill integration evaluation runner.

The documented P0-07 EvaluationContractHarness binds one skill_instance.
Integration contracts declare routes that span skills. This runner dispatches
each scenario to a registered skill adapter or to an orchestration adapter.

The evaluator compares adapter output to the contract. Route scenarios are
scored by comparing observed_route with expected_route. Self-certification
fields (route_matched, required_behaviors_satisfied, forbidden_behaviors_absent)
are stripped before scoring.

Without adapters, status stays NOT_RUN. A wiring fixture under tests/ is not
live behavioral evidence and must not be written back as results.status=RUN
on the contract.
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.eval_judge import score_accuracy, strip_self_cert_fields  # noqa: E402


class IntegrationEvalRunner:
    """Dispatch integration scenarios across skill or orchestration adapters."""

    def __init__(self, skill_registry: dict, contract: dict, orchestration=None):
        """
        skill_registry: skill name -> object with execute(input) -> dict
        orchestration: object with execute(scenario) -> dict including observed_route
        contract: integration contract. Only contract['scenarios'] is canonical.
        """
        self.skills = skill_registry or {}
        self.orchestration = orchestration
        self.contract = contract
        self.results = []

    def scenarios(self) -> list[dict]:
        if "integration_scenarios" in self.contract and "scenarios" in self.contract:
            raise ValueError(
                "integration contract has both scenarios and integration_scenarios; "
                "keep one canonical collection"
            )
        return list(self.contract.get("scenarios") or [])

    def run(self) -> dict:
        if not self.skills and self.orchestration is None:
            return {
                "status": "NOT_RUN",
                "reason": "no skill or orchestration adapters registered; refusing to fake behavioral scores",
                "contract_id": self.contract.get("contract_id"),
                "scenario_count": len(self.scenarios()),
                "dispatch_plan": self.dispatch_plan(),
                "behavioral_evidence": "NONE",
            }

        for scenario in self.scenarios():
            self.results.append(self.run_scenario(scenario))
        evidence = "LIVE"
        if _is_wiring_fixture(self.orchestration) and not self.skills:
            evidence = "WIRING_FIXTURE_ONLY"
        return {
            "status": "RUN",
            "contract_id": self.contract.get("contract_id"),
            "results": self.results,
            "scores": self.score_results(),
            "behavioral_evidence": evidence,
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
                        "dispatch": "orchestration",
                        "expected_route": scenario["expected_route"],
                    }
                )
            else:
                plan.append({"scenario_id": sid, "dispatch": "unspecified"})
        return plan

    def run_scenario(self, scenario: dict) -> dict:
        sid = scenario.get("id") or scenario.get("scenario_id")
        skill_name = scenario.get("skill")
        if skill_name:
            skill = self.skills.get(skill_name)
            if skill is None:
                return {
                    "scenario_id": sid,
                    "status": "NOT_RUN",
                    "reason": f"no adapter registered for skill '{skill_name}'",
                }
            actual = skill.execute(scenario.get("input") or scenario.get("inputs") or {})
        elif scenario.get("expected_route"):
            if self.orchestration is None:
                return {
                    "scenario_id": sid,
                    "status": "NOT_RUN",
                    "reason": "route scenario requires an orchestration adapter",
                }
            actual = self.orchestration.execute(scenario)
        else:
            return {
                "scenario_id": sid,
                "status": "NOT_RUN",
                "reason": "scenario has neither skill nor expected_route",
            }

        if not isinstance(actual, dict):
            return {
                "scenario_id": sid,
                "status": "RUN",
                "accuracy": 0.0,
                "passed": False,
                "reason": "adapter did not return an output object",
            }
        if scenario.get("expected_route") and "observed_route" not in actual:
            return {
                "scenario_id": sid,
                "status": "RUN",
                "accuracy": 0.0,
                "passed": False,
                "reason": "orchestration adapter omitted observed_route",
                "actual_output": strip_self_cert_fields(actual),
            }

        cleaned = strip_self_cert_fields(actual)
        accuracy = score_accuracy(cleaned, scenario)
        return {
            "scenario_id": sid,
            "skill": skill_name,
            "status": "RUN",
            "accuracy": accuracy,
            "passed": accuracy >= 0.9,
            "actual_output": cleaned,
        }

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


def load_adapter(spec: str):
    """Load module:callable. The callable returns an adapter or a skill registry."""
    if ":" not in spec:
        raise SystemExit(f"adapter spec must be module:callable, got {spec!r}")
    module_name, attr = spec.split(":", 1)
    module = importlib.import_module(module_name)
    factory = getattr(module, attr)
    return factory() if callable(factory) else factory


def _is_wiring_fixture(orchestration) -> bool:
    if orchestration is None:
        return False
    module = getattr(orchestration.__class__, "__module__", "")
    return module.startswith("tests.")


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
        help="Print dispatch plan without adapters (status NOT_RUN)",
    )
    parser.add_argument(
        "--skill-adapter",
        action="append",
        default=[],
        metavar="NAME=module:callable",
        help="Register a skill adapter. Callable returns an object with execute(input)->dict.",
    )
    parser.add_argument(
        "--orchestration-adapter",
        metavar="module:callable",
        help="Register an orchestration adapter. Callable returns an object with execute(scenario)->dict including observed_route.",
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
    if "integration_scenarios" in contract:
        print(
            "Integration contract must not declare integration_scenarios alongside scenarios.",
            file=sys.stderr,
        )
        return 2

    skills = {}
    for item in args.skill_adapter:
        if "=" not in item:
            print(f"--skill-adapter must be NAME=module:callable, got {item!r}", file=sys.stderr)
            return 2
        name, spec = item.split("=", 1)
        skills[name] = load_adapter(spec)
    orchestration = load_adapter(args.orchestration_adapter) if args.orchestration_adapter else None

    if args.plan_only:
        skills = {}
        orchestration = None

    runner = IntegrationEvalRunner(skills, contract, orchestration=orchestration)
    result = runner.run()
    print(json.dumps(result, indent=2))
    if args.plan_only or result.get("status") == "NOT_RUN":
        return 0
    failed = [r for r in result.get("results", []) if r.get("status") == "RUN" and not r.get("passed")]
    not_run = [r for r in result.get("results", []) if r.get("status") == "NOT_RUN"]
    return 1 if failed or not_run else 0


if __name__ == "__main__":
    raise SystemExit(main())
