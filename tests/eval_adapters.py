"""Adapters used to prove the evaluator. Not live skill behavior."""

import re


def _effect_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:64]


class Scripted:
    def __init__(self, output):
        self.output = output

    def execute(self, _scenario):
        return dict(self.output)


def wiring_orchestrator():
    """Return the contract route and the required effect ids only.

    This is a wiring fixture. It is not evidence that skills behave correctly.
    The effects list is present so safety checks can see an explicit trace.
    """

    class _Wiring:
        def execute(self, scenario):
            effects = [
                _effect_id(behavior) for behavior in scenario.get("expected_behaviors") or []
            ]
            return {
                "observed_route": list(scenario.get("expected_route") or []),
                "effects": effects,
            }

    return _Wiring()


def mismatch_orchestrator():
    class _Mismatch:
        def execute(self, scenario):
            route = list(scenario.get("expected_route") or [])
            forbidden = scenario.get("forbidden_behaviors") or ["forbidden"]
            return {
                "observed_route": route + ["skipped-plan-acceptance"],
                "effects": [_effect_id(forbidden[0])],
                "route_matched": True,
            }

    return _Mismatch()
