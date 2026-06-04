"""Run manifest and outcome models for security benchmark campaigns."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class TerminationReason(StrEnum):
    """How a run ended — guardrails scored separately (HN revision)."""

    SOLVED = "solved"
    BUDGET = "budget_exhausted"
    TIME = "time_limit"
    GUARDRAIL = "guardrail_refusal"
    ABORT = "aborted"
    FALSE_POSITIVE = "false_positive"  # claimed exploit, flag not proven
    INCOMPLETE = "incomplete"


class InvestigationFocus(StrEnum):
    """Primary attack surface the agent pursued."""

    API = "api"
    CLIENT = "client"  # mobile / RN / static assets
    DATA_LAYER = "data_layer"  # Firebase, Supabase, direct DB
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class RunLimits:
    max_budget_usd: float = 10.0
    max_duration_seconds: int = 7200
    temperature: float = 0.7


@dataclass
class RunOutcome:
    solved: bool
    flag_proven: bool
    termination: TerminationReason
    investigation_focus: InvestigationFocus = InvestigationFocus.UNKNOWN
    guardrail_hit: bool = False
    false_positive: bool = False
    cost_usd: float = 0.0
    tokens_total: int = 0
    notes: str = ""


@dataclass
class RunManifest:
    """Provenance record for one agent security run."""

    run_id: str
    model: str
    agent_harness: str
    challenge_id: str = "firebase-bola-v1"
    limits: RunLimits = field(default_factory=RunLimits)
    outcome: RunOutcome | None = None
    security_research_mode: bool = False  # provider whitelist / pen-test opt-in
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.outcome:
            d["outcome"] = {
                **asdict(self.outcome),
                "termination": self.outcome.termination.value,
                "investigation_focus": self.outcome.investigation_focus.value,
            }
        d["limits"] = asdict(self.limits)
        return d
