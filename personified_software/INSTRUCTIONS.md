# Personified agentic repository — instructions

Use this document to scaffold persona files and behavior.

## What this is

This repo is a **personified entity**, not only a code container. It should:

1. **Understand itself** — architecture, capabilities, boundaries, history  
2. **Present to users** — who it is, what it does, why, how to use it  
3. **Evolve** — propose and land improvements via traceable git work, within governance  

**Aim:** The in-repo agent can serve users directly (symbiosis of agent and code), without depending on a separate “stronger wrapper” for core behavior.

**Runtime aim (same repo, two surfaces):** Personified agentic software is **not only** self-explaining for humans and coding agents. It should also **surface the same agentic capabilities inside the running product**—APIs, MCP servers, in-app assistants, batch jobs, or other bindings—so end users and integrations get those capabilities **as software behavior**, not only as documentation or offline explanation of code.

**Non-goals:** Unsupervised one-shot self-modification; skipping review, tests, or permissions; generic template personas; a second, shadow “agentic stack” that duplicates policy or tools outside the repo’s declared interfaces.

**Principles:** Identity before tooling; repo (code, docs, tests, history) as “body”; evolution through PRs; fail loud and learn; humans set the constitution, the agent operates inside it.

## Three layers and where they live

| Layer | Role | Suggested paths |
| --- | --- | --- |
| **Identity** | Mission, persona, values, non-goals | `.persona/identity/mission.md`, `persona.md`, `constitution.md` |
| **Self-model** | How the system works: map, capabilities, risks, decisions | Manifest in `AGENTS.md`, `README.md`, `TOOLS.md`, and other in-repo description files; trace decisions in `.persona/memory/decision_log.md` |
| **Action** | Repo-changing tools/scripts + adapters to external systems (CI, deploy, APIs) without re-encoding full vendor semantics | Document invocations in `TOOLS.md` |

## Runtime surfacing — agentic capabilities as product features

The **self-model** and **action** layers should have a **runtime projection**: the shipped service loads the same boundaries (constitution, risk notes), invokes the same tool contracts (or thin wrappers), and applies the same governance hooks (authz, audit, consent) that `TOOLS.md` / adapters describe. External LLM hosts or IDEs are optional; the product itself can expose agentic behavior.

| Concern | Repo-time | Runtime |
| --- | --- | --- |
| **What we can do** | `AGENTS.md`, capability lists, runbooks | Feature flags, capability registry, OpenAPI/MCP tool list derived from the same source |
| **Policy** | `constitution.md`, governance gates | Authz, rate limits, consent (e.g. memory policy), kill switches |
| **Execution** | Scripts, CI, documented CLI | HTTP handlers, workers, MCP tools, embedded agent loop calling shared libraries |
| **Evidence** | PRs, tests, decision log | Request IDs, structured logs, user-visible receipts |

**Anti-patterns:** Re-implementing “similar” tools only in the UI layer; runtime behavior that cannot be traced to a named capability in-repo; bypassing audit or policy for convenience.

## Self-evolution loop

`Observe → Diagnose → Propose → Simulate → Apply → Verify → Reflect`

| Stage | Notes | Artifact |
| --- | --- | --- |
| Observe | Chats, issues/PRs, CI logs, prod signals | `.persona/memory/signals/YYYY_MM_DD.md` |
| Diagnose | Type, blast radius, urgency, hypotheses | `.persona/memory/diagnosis/<ticket_id>.md` |
| Propose | Goals, scope/non-goals, interface impact, tests, rollback | `rfcs/FR_*.md` |
| Simulate | Targeted tests, smoke, risks | `tests/rfcs/TEST_FR_*.md` |
| Apply | Small reversible commits tied to evidence | (git) |
| Verify & reflect | Success/failure patterns, next triggers | `.persona/memory/retrospectives/<change_id>.md` |

## “No extra wrapper” checklist

Built-in **entrypoints** (e.g. `persona serve`, HTTP/MCP/SDK), **knowledge** (self-description, runbooks), **governance** (repo-driven gates mirrored at runtime), and **memory** (versioned decisions and incidents). Host processes (cloud, desktop, device) only supply compute and I/O; **behavior, policy, and capability contracts remain anchored in the repo** and are reused by both developer-side agents and production paths where applicable.

## Reference layout (adopt incrementally)

```text
.persona/
  identity/
    mission.md
    persona.md
    constitution.md
  memory/
    signals/
    diagnosis/
    retrospectives/
    decision_log.md
```

## Governance gates

1. **Policy** — no unsanctioned changes to secrets, billing, permissions  
2. **Tests** — no apply without critical tests passing  
3. **Review** — human confirmation for high-risk work  
4. **Rollback** — every change has a one-step rollback  
5. **Audit** — rationale, test evidence, and diffs traceable  

## User interaction

**Modes:** Explain (architecture, limits, recent change) · Guide (workflow) · Execute (authorized work + evidence).

**Response shape (suggested):** Who I am · What I can do now · What changed recently · What I propose next.

## Rollout phases

| Phase | Focus | Done when |
| --- | --- | --- |
| **0** | Skeleton: `identity/`; agent-facing docs (`AGENTS.md`, etc.) | Repo can state identity, capabilities, boundaries |
| **1** | Documented tools and entrypoints; explain / guide / execute | End-to-end explain + execute + receipt |
| **1b** | **Runtime binding** — at least one production path exposes agentic capabilities (shared library + adapter: MCP, HTTP, or in-process) with policy/audit aligned to repo docs | Same capability can be invoked by a user/integration without opening an IDE; traces match `TOOLS.md` contracts |
| **2** | Full evolution loop; RFCs + test evidence | Strong changes can be produced and landed from signals, mostly autonomously |
| **3** | Tune policy (risk, triggers); evolution KPIs | Evolution quality stable and measurable |

## Definition of success

1. **Self-explanatory** — identity, capabilities, boundaries, history are traceable  
2. **Servable** — tasks run in scope with evidence  
3. **Embeddable** — agentic capabilities are available **as product features at runtime**, not only as explanations of the codebase  
4. **Self-evolving** — improvements proposed and merged within gates  
5. **Symbiotic** — agent behavior and code structure stay aligned  
