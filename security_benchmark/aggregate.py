"""Load run manifests from a results tree and produce summary tables."""

from __future__ import annotations

import json
from pathlib import Path

from security_benchmark.metrics import aggregate_model, format_aggregate_table
from security_benchmark.models import (
    InvestigationFocus,
    RunManifest,
    RunOutcome,
    TerminationReason,
)


def _parse_outcome(raw: dict) -> RunOutcome:
    term = TerminationReason(raw.get("termination", "incomplete"))
    focus = InvestigationFocus(raw.get("investigation_focus", "unknown"))
    return RunOutcome(
        solved=bool(raw.get("solved", False)),
        flag_proven=bool(raw.get("flag_proven", False)),
        termination=term,
        investigation_focus=focus,
        guardrail_hit=bool(raw.get("guardrail_hit", False)),
        false_positive=bool(raw.get("false_positive", False)),
        cost_usd=float(raw.get("cost_usd", 0)),
        tokens_total=int(raw.get("tokens_total", 0)),
        notes=str(raw.get("notes", "")),
    )


def load_manifest(path: Path) -> RunManifest | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    outcome_raw = data.get("outcome")
    outcome = _parse_outcome(outcome_raw) if outcome_raw else None
    return RunManifest(
        run_id=str(data.get("run_id", path.parent.name)),
        model=str(data.get("model", "unknown")),
        agent_harness=str(data.get("agent_harness", "unknown")),
        challenge_id=str(data.get("challenge_id", "firebase-bola-v1")),
        security_research_mode=bool(data.get("security_research_mode", False)),
        outcome=outcome,
        metadata=data.get("metadata") or {},
    )


def iter_manifests(results_root: Path) -> list[RunManifest]:
    manifests: list[RunManifest] = []
    if not results_root.is_dir():
        return manifests
    for path in sorted(results_root.rglob("manifest.json")):
        m = load_manifest(path)
        if m and m.outcome:
            manifests.append(m)
    return manifests


def aggregate_runs(results_root: Path) -> str:
    by_model: dict[str, list[RunOutcome]] = {}
    for m in iter_manifests(results_root):
        assert m.outcome
        by_model.setdefault(m.model, []).append(m.outcome)
    if not by_model:
        return "# Security benchmark\n\nNo manifests with outcomes under results/.\n"
    rows = [aggregate_model(model, outcomes, []) for model, outcomes in by_model.items()]
    return "# Security benchmark aggregates\n\n" + format_aggregate_table(rows) + "\n"
