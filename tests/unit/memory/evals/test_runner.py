"""Unit tests for evals.runner."""

import pytest
from evals.runner import run_eval
from evals.types import EvalProbe, EvalReport

pytestmark = pytest.mark.unit


def _passing_probe(probe_id: str = "p") -> EvalProbe:
    return EvalProbe(id=probe_id, description="always passes", run=lambda: (True, "ok"))


def _failing_probe(probe_id: str = "p") -> EvalProbe:
    return EvalProbe(id=probe_id, description="always fails", run=lambda: (False, "nope"))


def _raising_probe(probe_id: str = "p") -> EvalProbe:
    def _run():
        raise RuntimeError("boom")

    return EvalProbe(id=probe_id, description="raises", run=_run)


class TestRunEval:
    def test_returns_eval_report(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": [_passing_probe()], "THRESHOLD": 0.8})(),
        )
        report = run_eval("anything")
        assert isinstance(report, EvalReport)

    def test_report_name_matches_eval(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": [], "THRESHOLD": 0.8})(),
        )
        report = run_eval("my-eval")
        assert report.eval_name == "my-eval"

    def test_all_passing_probes_report_passed(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type(
                "M",
                (),
                {"PROBES": [_passing_probe("a"), _passing_probe("b")], "THRESHOLD": 0.8},
            )(),
        )
        report = run_eval("x")
        assert report.passed is True

    def test_below_threshold_report_not_passed(self, mocker):
        probes = [_passing_probe("a"), _failing_probe("b"), _failing_probe("c")]
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": probes, "THRESHOLD": 0.8})(),
        )
        report = run_eval("x")
        assert report.passed is False

    def test_results_length_equals_probes_length(self, mocker):
        probes = [_passing_probe("a"), _failing_probe("b"), _passing_probe("c")]
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": probes, "THRESHOLD": 0.5})(),
        )
        report = run_eval("x")
        assert len(report.results) == 3

    def test_each_probe_run_called_once(self, mocker):
        call_counts = {"a": 0, "b": 0}

        def _make(pid):
            def _run():
                call_counts[pid] += 1
                return True, "ok"

            return EvalProbe(id=pid, description="", run=_run)

        probes = [_make("a"), _make("b")]
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": probes, "THRESHOLD": 0.8})(),
        )
        run_eval("x")
        assert call_counts == {"a": 1, "b": 1}

    def test_raising_probe_recorded_as_failure(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": [_raising_probe("r")], "THRESHOLD": 0.8})(),
        )
        report = run_eval("x")
        assert len(report.results) == 1
        assert report.results[0].passed is False
        assert "boom" in report.results[0].notes

    def test_unknown_eval_name_raises_value_error(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            side_effect=ModuleNotFoundError("no module"),
        )
        with pytest.raises(ValueError, match="unknown-eval"):
            run_eval("unknown-eval")

    def test_missing_probes_attribute_raises_value_error(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"THRESHOLD": 0.8})(),  # no PROBES
        )
        with pytest.raises(ValueError, match="PROBES"):
            run_eval("x")

    def test_threshold_from_module_used_in_report(self, mocker):
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": [_passing_probe()], "THRESHOLD": 0.6})(),
        )
        report = run_eval("x")
        assert report.threshold == pytest.approx(0.6)

    def test_result_probe_ids_match_probe_ids(self, mocker):
        probes = [_passing_probe("alpha"), _failing_probe("beta")]
        mocker.patch(
            "evals.runner.importlib.import_module",
            return_value=type("M", (), {"PROBES": probes, "THRESHOLD": 0.5})(),
        )
        report = run_eval("x")
        ids = [r.probe_id for r in report.results]
        assert ids == ["alpha", "beta"]
