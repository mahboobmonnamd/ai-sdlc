#!/usr/bin/env python3
"""Score skill and route outputs without self-certification fields.

The judge compares an adapter's actual output to scenario expectations.
Skills must not be asked to set required_behaviors_satisfied,
forbidden_behaviors_absent, or route_matched. Those fields are ignored
when present and are rejected by contract validation.
"""

from __future__ import annotations

import ast
import re

SELF_CERT_FIELDS = (
    "required_behaviors_satisfied",
    "forbidden_behaviors_absent",
    "route_matched",
)

_EQ = re.compile(r"^(.+?)\s*==\s*(.+)$")
_NE = re.compile(r"^(.+?)\s*!=\s*(.+)$")
_IN = re.compile(r"^(.+?)\s+in\s+(\[.*\])$")
_NOT_IN = re.compile(r"^(.+?)\s+not_in\s+(\[.*\])$")
_INCLUDES = re.compile(r"^(.+?)\s+includes\s+(\S+)$")
_EXCLUDES = re.compile(r"^(.+?)\s+excludes\s+(\S+)$")


def is_self_cert_check(check: str) -> bool:
    return any(field in (check or "") for field in SELF_CERT_FIELDS)


def strip_self_cert_fields(actual: dict | None) -> dict:
    if not isinstance(actual, dict):
        return {}
    return {key: value for key, value in actual.items() if key not in SELF_CERT_FIELDS}


def contract_pass_threshold(scenario: dict, contract: dict | None) -> float | None:
    """Read the pass bar from the scenario, then the contract. Do not invent one."""
    sources = (
        (scenario or {}).get("scoring") or {},
        (contract or {}).get("scoring") or {},
    )
    for source in sources:
        if "pass_threshold" not in source:
            continue
        value = source["pass_threshold"]
        if isinstance(value, (int, float)):
            return float(value)
        return None
    return None


def scenario_passed(accuracy: float, scenario: dict, contract: dict | None) -> bool:
    threshold = contract_pass_threshold(scenario, contract)
    if threshold is None:
        return False
    return accuracy >= threshold


class EffectTrace:
    """Effects observed by host instrumentation.

    The skill return value is not a source. Call record() when the host sees
    an action. The runner copies trace.effects into the dict the judge scores
    and drops any effects list the skill reported.
    """

    def __init__(self) -> None:
        self._effects: list[str] = []

    def record(self, effect: str) -> None:
        self._effects.append(effect)

    @property
    def effects(self) -> list[str]:
        return list(self._effects)


def with_host_effects(actual: dict | None, trace: EffectTrace | None) -> dict:
    cleaned = strip_self_cert_fields(actual)
    cleaned.pop("effects", None)
    if isinstance(trace, EffectTrace):
        cleaned["effects"] = trace.effects
    return cleaned


def score_accuracy(actual, scenario: dict) -> float:
    """Return 0..1 from scenario scoring.criteria applied to actual output."""
    if actual is None:
        return 0.0
    criteria = (scenario.get("scoring") or {}).get("criteria") or []
    total = sum(c.get("points", 0) for c in criteria)
    if total <= 0:
        return 0.0
    cleaned = strip_self_cert_fields(actual if isinstance(actual, dict) else {"value": actual})
    expected = _expected_view(scenario)
    earned = 0
    for criterion in criteria:
        check = criterion.get("check") or ""
        if is_self_cert_check(check):
            if criterion.get("safety"):
                return 0.0
            continue
        passed = evaluate_check(check, cleaned, expected)
        if criterion.get("safety") and not passed:
            return 0.0
        if passed:
            earned += criterion.get("points", 0)
    return earned / total


def evaluate_check(check_expr: str, actual: dict, expected: dict) -> bool:
    check_expr = (check_expr or "").strip()
    if not check_expr or is_self_cert_check(check_expr):
        return False

    match = _EXCLUDES.match(check_expr)
    if match:
        effects = _resolve(match.group(1).strip(), actual, expected)
        token = match.group(2).strip().strip("'\"")
        return isinstance(effects, list) and token not in effects

    match = _INCLUDES.match(check_expr)
    if match:
        effects = _resolve(match.group(1).strip(), actual, expected)
        token = match.group(2).strip().strip("'\"")
        return isinstance(effects, list) and token in effects

    match = _NOT_IN.match(check_expr)
    if match:
        left = _resolve(match.group(1).strip(), actual, expected)
        right = _parse_literal(match.group(2).strip())
        return isinstance(right, list) and left not in right

    match = _IN.match(check_expr)
    if match:
        left = _resolve(match.group(1).strip(), actual, expected)
        right = _parse_literal(match.group(2).strip())
        return isinstance(right, list) and left in right

    match = _NE.match(check_expr)
    if match:
        left = _resolve(match.group(1).strip(), actual, expected)
        right = _resolve_or_literal(match.group(2).strip(), actual, expected)
        return left != right

    match = _EQ.match(check_expr)
    if match:
        left = _resolve(match.group(1).strip(), actual, expected)
        right = _resolve_or_literal(match.group(2).strip(), actual, expected)
        return left == right

    return False


def _expected_view(scenario: dict) -> dict:
    expected = dict(scenario.get("expected_output") or {})
    if "expected_route" in scenario:
        expected["expected_route"] = scenario["expected_route"]
    return expected


def _resolve_or_literal(token: str, actual: dict, expected: dict):
    token = token.strip()
    if token.startswith("output.") or token.startswith("actual.") or token.startswith("expected."):
        return _resolve(token, actual, expected)
    return _parse_literal(token)


def _resolve(path: str, actual: dict, expected: dict):
    if path.startswith("expected."):
        obj = expected
        path = path[len("expected.") :]
    else:
        obj = actual
        if path.startswith("output."):
            path = path[len("output.") :]
        elif path.startswith("actual."):
            path = path[len("actual.") :]
    current = obj
    for part in path.split("."):
        if not part:
            continue
        if isinstance(current, dict):
            current = current.get(part)
        else:
            return None
    return current


def _parse_literal(value_str: str):
    value_str = value_str.strip()
    if value_str == "[]":
        return []
    if value_str.startswith("["):
        try:
            parsed = ast.literal_eval(value_str)
        except (SyntaxError, ValueError):
            return value_str
        return parsed
    if (value_str.startswith("'") and value_str.endswith("'")) or (
        value_str.startswith('"') and value_str.endswith('"')
    ):
        return value_str[1:-1]
    lowered = value_str.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in ("null", "none"):
        return None
    try:
        return int(value_str)
    except ValueError:
        return value_str
