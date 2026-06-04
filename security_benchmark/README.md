# Security benchmark

Minimal eval harness for **agentic security** campaigns — scoring, provenance, and tables
without vendoring a full vulnerable application.

## Methodology (source)

- [I spent $1,500 seeing if LLMs could hack my app](https://kasra.blog/blog/i-spent-1500-seeing-if-llms-could-hack-my-app/) — Firebase BOLA fixture, multi-run solve rates, Wilson CI, $/solve.
- [HN discussion](https://news.ycombinator.com/item?id=48392343) — revision guidelines baked into manifests:
  - Track **guardrail refusals** separately from capability (`capability_solve_rate`).
  - Flag **false positives** (reported exploit, flag not proven).
  - Record **investigation focus** (API vs client vs data layer).
  - Note **security_research_mode** when providers whitelist pen-test accounts (fair comparisons).

## Layout

```
security_benchmark/          # metrics + manifest schema
eval_harness/security/       # suite anchor (policy/provenance TODO)
scripts/security_benchmark_eval.sh
data/results/<model>/<run_id>/manifest.json   # gitignored campaign output
```

## Phase 0 — aggregate manifests (no LLM)

```bash
./scripts/security_benchmark_eval.sh phase-0
```

Writes `security_benchmark/reports/aggregate.md` from `security_benchmark/data/results/`.

## Phase 1 — agent run (TODO)

Wire your agent harness (pi, Claude Code, etc.), enforce `RunLimits`, write `manifest.json` per run.
See `docs/SECURITY_BENCHMARK.md`.

## Manifest example

```json
{
  "run_id": "run_001",
  "model": "example-model",
  "agent_harness": "pi+goal-x",
  "security_research_mode": true,
  "outcome": {
    "solved": true,
    "flag_proven": true,
    "termination": "solved",
    "investigation_focus": "data_layer",
    "cost_usd": 6.62,
    "tokens_total": 260000
  }
}
```

## Caveats

Not a scientific benchmark — small-N runs, provider guardrails, and harness choice dominate variance.
