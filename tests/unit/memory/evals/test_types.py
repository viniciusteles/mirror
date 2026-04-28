"""Unit tests for evals.types."""

import pytest
from evals.types import EvalProbe, EvalReport, EvalResult

pytestmark = pytest.mark.unit


class TestEvalReport:
    def _report(self, passed_flags: list[bool], threshold: float = 0.8) -> EvalReport:
        results = [EvalResult(probe_id=f"p{i}", passed=flag) for i, flag in enumerate(passed_flags)]
        return EvalReport(eval_name="test", results=results, threshold=threshold)

    def test_score_all_pass(self):
        assert self._report([True, True, True]).score == 1.0

    def test_score_all_fail(self):
        assert self._report([False, False, False]).score == 0.0

    def test_score_partial(self):
        assert self._report([True, True, False, False]).score == pytest.approx(0.5)

    def test_score_four_of_five(self):
        assert self._report([True, True, True, True, False]).score == pytest.approx(0.8)

    def test_score_zero_when_no_results(self):
        report = EvalReport(eval_name="empty", results=[], threshold=0.8)
        assert report.score == 0.0

    def test_passed_when_score_meets_threshold(self):
        assert self._report([True, True, True, True, False], threshold=0.8).passed is True

    def test_passed_when_score_exceeds_threshold(self):
        assert self._report([True, True, True, True, True], threshold=0.8).passed is True

    def test_not_passed_when_score_below_threshold(self):
        assert self._report([True, False, False, False, False], threshold=0.8).passed is False

    def test_passed_with_threshold_one_requires_all(self):
        assert self._report([True, True, False], threshold=1.0).passed is False

    def test_passed_with_threshold_zero_always_true(self):
        assert self._report([False, False], threshold=0.0).passed is True


class TestEvalProbe:
    def test_run_returns_passed_and_notes(self):
        probe = EvalProbe(
            id="p1",
            description="test probe",
            run=lambda: (True, "all good"),
        )
        passed, notes = probe.run()
        assert passed is True
        assert notes == "all good"

    def test_run_can_return_failure(self):
        probe = EvalProbe(
            id="p2",
            description="failing probe",
            run=lambda: (False, "nothing found"),
        )
        passed, notes = probe.run()
        assert passed is False
        assert "nothing found" in notes
