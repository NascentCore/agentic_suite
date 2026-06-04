"""Tests for security_benchmark metrics and aggregation."""

from __future__ import annotations

from pathlib import Path

from security_benchmark.aggregate import aggregate_runs, load_manifest
from security_benchmark.metrics import aggregate_model, wilson_ci_95
from security_benchmark.models import InvestigationFocus, RunOutcome, TerminationReason

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "security_benchmark" / "data" / "sample_results"


def test_wilson_ci_bounds():
    lo, hi = wilson_ci_95(7, 10)
    assert 0.0 <= lo <= hi <= 1.0
    assert lo < 0.5 < hi  # 7/10 should bracket 0.7


def test_aggregate_model_guardrail_excluded_from_capability():
    outcomes = [
        RunOutcome(
            solved=True,
            flag_proven=True,
            termination=TerminationReason.SOLVED,
            investigation_focus=InvestigationFocus.DATA_LAYER,
        ),
        RunOutcome(
            solved=False,
            flag_proven=False,
            termination=TerminationReason.GUARDRAIL,
            guardrail_hit=True,
            investigation_focus=InvestigationFocus.API,
        ),
    ]
    row = aggregate_model("test", outcomes, [1.0, 2.0])
    assert row.n_solves == 1
    assert row.n_guardrail == 1
    assert row.capability_solve_rate == 1.0  # only non-guardrail run counted


def test_load_manifest_sample():
    path = SAMPLE / "gpt-5.5" / "run_001" / "manifest.json"
    m = load_manifest(path)
    assert m is not None
    assert m.model == "gpt-5.5"
    assert m.outcome is not None
    assert m.outcome.flag_proven is True


def test_phase0_aggregate_sample_tree():
    text = aggregate_runs(SAMPLE)
    assert "gpt-5.5" in text
    assert "guardrail" in text.lower() or "cap." in text
