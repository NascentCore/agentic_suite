#!/usr/bin/env bash
# Security benchmark evaluation wrapper (Agentic Suite)
#
# Phase 0: aggregate manifest.json under data/results (no LLM).
# Phases 1-2: agent campaigns — see docs/SECURITY_BENCHMARK.md
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SDIR="${ROOT}/security_benchmark"
DATA="${SDIR}/data"
RESULTS="${DATA}/results"
REPORTS="${SDIR}/reports"
CHALLENGE="${SDIR}/challenge_assets/CHALLENGE.md"

phase0_aggregate() {
  mkdir -p "${REPORTS}"
  # Prefer real campaign results; fall back to committed sample fixtures
  if [[ -d "${RESULTS}" ]] && find "${RESULTS}" -name manifest.json -print -quit | grep -q .; then
  SRC="${RESULTS}"
  else
    SRC="${DATA}/sample_results"
  fi
  python3 -m security_benchmark.cli aggregate "${SRC}" > "${REPORTS}/aggregate.md"
  echo "Wrote ${REPORTS}/aggregate.md (source: ${SRC})"
}

require_phase_prereqs() {
  local phase="$1"
  if [[ -z "${LLM_API_KEY:-}" ]]; then
    echo "SKIP phase-${phase}: set LLM_API_KEY"
    return 2
  fi
  if [[ ! -f "${CHALLENGE}" ]]; then
    echo "SKIP phase-${phase}: missing ${CHALLENGE}"
    return 2
  fi
  return 0
}

if [[ "${1:-phase-0}" == "phase-0" ]]; then
  phase0_aggregate
  exit 0
fi

# TODO(phase-1): single smoke run — agent harness writes manifest.json under RESULTS
if [[ "$1" == "phase-1" ]]; then
  require_phase_prereqs 1 || exit $?
  cat <<EOF
phase-1 is not fully scripted (agent harness is external).

TODO(phase-1):
  1. Run your agent with: ${CHALLENGE}
  2. Enforce RunLimits (\\\$10, 2h) from security_benchmark.models
  3. Write manifest.json to ${RESULTS}/<model>/<run_id>/
  4. ./scripts/security_benchmark_eval.sh phase-0

Checklist: docs/SECURITY_BENCHMARK.md
EOF
  exit 2
fi

# TODO(phase-2): MODELS=file with one model per line, RUNS=10 per model
if [[ "$1" == "phase-2" ]]; then
  require_phase_prereqs 2 || exit $?
  cat <<EOF
phase-2 is not fully scripted.

TODO(phase-2):
  1. For each model in MODELS (or env MODEL): repeat RUNS=${RUNS:-10}
  2. ./scripts/security_benchmark_eval.sh phase-0

Checklist: docs/SECURITY_BENCHMARK.md
EOF
  exit 2
fi

echo "Usage: $0 [phase-0|phase-1|phase-2]"
exit 1
