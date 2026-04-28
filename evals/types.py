"""Core types for the evals harness.

Evals are distinct from tests:
- They hit real LLM APIs and cost money per run.
- They are non-deterministic — LLM output varies.
- They are run on demand, not in CI.
- Failure means behavior drifted, not code broke.

Each eval exposes PROBES: list[EvalProbe] and THRESHOLD: float.
The runner calls each probe, scores the result, and exits non-zero below threshold.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class EvalProbe:
    """One probe in an eval: a single behavior assertion against a live LLM."""

    id: str
    description: str
    run: Callable[[], tuple[bool, str]]
    """Returns (passed, notes). Notes are shown in the report regardless of outcome."""


@dataclass
class EvalResult:
    """The outcome of running one probe."""

    probe_id: str
    passed: bool
    notes: str = ""


@dataclass
class EvalReport:
    """Aggregated results for one eval run."""

    eval_name: str
    results: list[EvalResult] = field(default_factory=list)
    threshold: float = 0.8

    @property
    def score(self) -> float:
        """Fraction of probes that passed. 0.0 when no results."""
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.passed) / len(self.results)

    @property
    def passed(self) -> bool:
        """True when score meets or exceeds the threshold."""
        return self.score >= self.threshold
