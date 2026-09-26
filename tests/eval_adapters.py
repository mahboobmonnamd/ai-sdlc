"""Adapters used to prove the evaluator. Not live skill behavior."""


class Scripted:
    def __init__(self, output):
        self.output = output

    def execute(self, _scenario):
        return dict(self.output)


def wiring_orchestrator():
    """Return the contract's expected route so CI can execute route comparison.

    This is a wiring fixture. It is not evidence that skills behave correctly.
    """

    class _Wiring:
        def execute(self, scenario):
            return {"observed_route": list(scenario.get("expected_route") or [])}

    return _Wiring()


def mismatch_orchestrator():
    class _Mismatch:
        def execute(self, scenario):
            route = list(scenario.get("expected_route") or [])
            return {"observed_route": route + ["skipped-plan-acceptance"], "route_matched": True}

    return _Mismatch()
