#!/usr/bin/env python3
"""Validate evaluation contracts against the P0-07-shaped schema used by score_accuracy()."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


REQUIRED_CONTRACT_FIELDS = (
    "contract_id",
    "contract_version",
    "skill",
    "scenarios",
    "scoring",
)

REQUIRED_SCENARIO_FIELDS = (
    "scenario_id",
    "name",
    "scoring",
)


def _is_index_contract(contract: dict) -> bool:
    return contract.get("category") == "index"


def _is_integration_contract(contract: dict) -> bool:
    return contract.get("category") == "integration" or contract.get("skill") == "core-development-loop"


def validate_criteria(criteria: list, path: str) -> list[str]:
    errors: list[str] = []
    if not criteria:
        errors.append(f"{path}: scoring.criteria must be a non-empty list")
        return errors
    for i, criterion in enumerate(criteria):
        if not isinstance(criterion, dict):
            errors.append(f"{path}: criteria[{i}] must be an object")
            continue
        if not criterion.get("criterion"):
            errors.append(f"{path}: criteria[{i}] missing criterion")
        if "points" not in criterion or not isinstance(criterion["points"], (int, float)):
            errors.append(f"{path}: criteria[{i}] missing numeric points")
        check = criterion.get("check") or criterion.get("verification")
        if not check or not isinstance(check, str):
            errors.append(
                f"{path}: criteria[{i}] missing check/verification expression "
                "(required by EvaluationContractHarness.score_accuracy)"
            )
    return errors


def validate_scenario(scenario: dict, path: str, *, require_skill: bool) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_SCENARIO_FIELDS:
        if field not in scenario:
            errors.append(f"{path}: missing {field}")
    sid = scenario.get("scenario_id") or scenario.get("id")
    if not sid:
        errors.append(f"{path}: missing scenario_id/id")
    if require_skill and not scenario.get("skill"):
        # integration route scenarios may omit skill when they only declare expected_route
        if "expected_route" not in scenario:
            errors.append(f"{path}: missing skill")
    scoring = scenario.get("scoring") or {}
    errors.extend(validate_criteria(scoring.get("criteria") or [], f"{path}.scoring"))
    return errors


def validate_contract(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path}: invalid JSON ({exc})"]

    if _is_index_contract(contract):
        for key in ("unit_contracts", "integration_contract"):
            if key not in contract:
                errors.append(f"{path}: index contract missing {key}")
        # Index contracts intentionally have empty scenarios; do not require criteria.
        if contract.get("results", {}).get("status") == "RUN":
            errors.append(f"{path}: index contract must not claim behavioral results RUN")
        return errors

    for field in REQUIRED_CONTRACT_FIELDS:
        if field not in contract:
            errors.append(f"{path}: missing {field}")

    scenarios = contract.get("scenarios") or []
    if not scenarios and contract.get("integration_scenarios"):
        scenarios = contract["integration_scenarios"]
    if not scenarios:
        errors.append(f"{path}: no scenarios")

    require_skill = not _is_integration_contract(contract)
    for i, scenario in enumerate(scenarios):
        sid = scenario.get("id") or scenario.get("scenario_id") or str(i)
        errors.extend(
            validate_scenario(
                scenario,
                f"{path}::scenario[{sid}]",
                require_skill=require_skill,
            )
        )

    # Honesty: do not allow claiming behavioral RUN without evidence fields.
    results = contract.get("results") or {}
    if results.get("status") == "RUN" and not results.get("test_results"):
        errors.append(
            f"{path}: results.status=RUN requires test_results evidence "
            "(schema validation alone is not behavioral execution)"
        )

    return errors


def discover_contracts(root: Path) -> list[Path]:
    evals = root / "evals"
    paths: list[Path] = []
    for pattern in ("*.json", "unit/*.json", "integration/*.json"):
        paths.extend(sorted(evals.glob(pattern)))
    # de-dupe while preserving order
    seen = set()
    unique = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        unique.append(path)
    return unique


def main(argv: list[str]) -> int:
    root = Path(argv[1]) if len(argv) > 1 else ROOT
    paths = discover_contracts(root)
    if not paths:
        print("No evaluation contracts found under evals/", file=sys.stderr)
        return 1
    all_errors: list[str] = []
    for path in paths:
        all_errors.extend(validate_contract(path))
    if all_errors:
        for error in all_errors:
            print(error, file=sys.stderr)
        print(f"FAIL: {len(all_errors)} evaluation contract error(s)", file=sys.stderr)
        return 1
    print(f"OK: validated {len(paths)} evaluation contract(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
