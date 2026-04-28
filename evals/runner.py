"""Eval runner: loads a named eval module, runs its probes, prints a report.

Usage:
    uv run python -m memory eval <name>

Each eval module must expose:
    PROBES: list[EvalProbe]
    THRESHOLD: float
"""

from __future__ import annotations

import importlib
import sys

from evals.types import EvalProbe, EvalReport, EvalResult

_PASS = "\033[32m✓\033[0m"
_FAIL = "\033[31m✗\033[0m"
_BOLD = "\033[1m"
_RESET = "\033[0m"


def run_eval(eval_name: str) -> EvalReport:
    """Load and run a named eval. Raises ValueError for unknown names."""
    module_path = f"evals.{eval_name}"
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise ValueError(f"Unknown eval '{eval_name}'. No module found at {module_path}.") from exc

    probes: list[EvalProbe] = getattr(module, "PROBES", None)
    threshold: float = getattr(module, "THRESHOLD", 0.8)

    if probes is None:
        raise ValueError(f"Eval module '{module_path}' must expose a PROBES list.")

    report = EvalReport(eval_name=eval_name, threshold=threshold)

    for probe in probes:
        try:
            passed, notes = probe.run()
        except Exception as exc:
            passed = False
            notes = f"probe raised: {exc}"
        report.results.append(EvalResult(probe_id=probe.id, passed=passed, notes=notes))

    return report


def print_report(report: EvalReport) -> None:
    """Print a human-readable eval report to stdout."""
    width = 60
    print(
        f"\n{_BOLD}── {report.eval_name} eval {'─' * (width - len(report.eval_name) - 8)}{_RESET}"
    )

    id_width = max((len(r.probe_id) for r in report.results), default=10) + 2
    for result in report.results:
        icon = _PASS if result.passed else _FAIL
        pad = id_width - len(result.probe_id)
        print(f"  {icon}  {result.probe_id}{' ' * pad}{result.notes}")

    passes = sum(1 for r in report.results if r.passed)
    total = len(report.results)
    outcome = f"{_BOLD}✓ PASS{_RESET}" if report.passed else f"{_BOLD}\033[31m✗ FAIL\033[0m{_RESET}"
    print(f"\n  {passes}/{total} passed  (threshold: {report.threshold:.2f})  {outcome}\n")


def main(args: list[str] | None = None) -> int:
    """Entry point for `python -m memory eval <name>`. Returns exit code."""
    argv = args if args is not None else sys.argv[1:]
    if not argv:
        print("Usage: python -m memory eval <name>", file=sys.stderr)
        return 1

    eval_name = argv[0]
    try:
        report = run_eval(eval_name)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print_report(report)
    return 0 if report.passed else 1
