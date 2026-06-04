"""Aggregate metrics: solve rate, Wilson CI, cost per run/solve (article §tables)."""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

from security_benchmark.models import RunOutcome, TerminationReason


@dataclass
class ModelAggregate:
    model: str
    n_runs: int
    n_solves: int
    solve_rate: float
    wilson_low: float
    wilson_high: float
    avg_cost_per_run: float
    cost_per_solve: float | None
    median_tokens: float | None
    n_guardrail: int
    n_false_positive: int
    capability_solve_rate: float  # solves / runs excluding guardrail-only early exits


def wilson_ci_95(successes: int, n: int) -> tuple[float, float]:
    """95% Wilson score interval for binomial proportion (article tables)."""
    if n <= 0:
        return (0.0, 0.0)
    z = 1.96
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def _median_or_none(values: list[int]) -> float | None:
    if not values:
        return None
    return float(statistics.median(values))


def aggregate_model(model: str, outcomes: list[RunOutcome], costs: list[float]) -> ModelAggregate:
    n = len(outcomes)
    solves = sum(1 for o in outcomes if o.solved and o.flag_proven)
    guardrails = sum(1 for o in outcomes if o.guardrail_hit or o.termination == TerminationReason.GUARDRAIL)
    false_pos = sum(1 for o in outcomes if o.false_positive or o.termination == TerminationReason.FALSE_POSITIVE)
    eligible = [o for o in outcomes if o.termination != TerminationReason.GUARDRAIL]
    cap_solves = sum(1 for o in eligible if o.solved and o.flag_proven)
    total_cost = sum(costs) if costs else sum(o.cost_usd for o in outcomes)
    tokens = [o.tokens_total for o in outcomes if o.tokens_total > 0]
    lo, hi = wilson_ci_95(solves, n)
    cost_per_solve = (total_cost / solves) if solves > 0 else None
    return ModelAggregate(
        model=model,
        n_runs=n,
        n_solves=solves,
        solve_rate=solves / n if n else 0.0,
        wilson_low=lo,
        wilson_high=hi,
        avg_cost_per_run=total_cost / n if n else 0.0,
        cost_per_solve=cost_per_solve,
        median_tokens=_median_or_none(tokens),
        n_guardrail=guardrails,
        n_false_positive=false_pos,
        capability_solve_rate=cap_solves / len(eligible) if eligible else 0.0,
    )


def format_aggregate_table(rows: list[ModelAggregate]) -> str:
    """Markdown table aligned with article + HN revision columns."""
    header = (
        "| model | solve | 95% Wilson | avg $/run | $/solve | "
        "median tok | guardrail | false+ | cap. solve |"
    )
    sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines = [header, sep]
    for r in sorted(rows, key=lambda x: (-x.n_solves, x.model)):
        wilson = f"{100 * r.wilson_low:.0f}%–{100 * r.wilson_high:.0f}%"
        cps = f"${r.cost_per_solve:.2f}" if r.cost_per_solve is not None else "—"
        med = f"{r.median_tokens:,.0f}" if r.median_tokens is not None else "—"
        lines.append(
            f"| {r.model} | {r.n_solves}/{r.n_runs} | {wilson} | "
            f"${r.avg_cost_per_run:.2f} | {cps} | {med} | "
            f"{r.n_guardrail} | {r.n_false_positive} | {100 * r.capability_solve_rate:.0f}% |"
        )
    return "\n".join(lines)
