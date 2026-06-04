"""Security benchmark — minimal harness metrics for agentic security evals.

Adapted from Kasra's Firebase BOLA challenge methodology (kasra.blog, 2026).
See docs/SECURITY_BENCHMARK.md and eval_harness/security/.
"""

__all__ = [
    "RunManifest",
    "RunOutcome",
    "TerminationReason",
    "InvestigationFocus",
    "aggregate_runs",
    "load_manifest",
    "wilson_ci_95",
]

from security_benchmark.aggregate import aggregate_runs, load_manifest
from security_benchmark.metrics import wilson_ci_95
from security_benchmark.models import InvestigationFocus, RunManifest, RunOutcome, TerminationReason
