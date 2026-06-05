# Privacy Filter × Commercial Contract — Experiment Design

Demonstration experiment for [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) on the attached **软件委托开发合同** (蓝耘–算想, 2023-07-19).

## 1. Research question

> Can OpenAI Privacy Filter reliably detect and mask personally identifiable information in a real commercial software-development contract, compared with rule-based baselines—and where does it fail on legal-domain, Chinese-language text?

Privacy Filter targets eight span types: `private_person`, `private_address`, `private_email`, `private_phone`, `private_url`, `private_date`, `account_number`, `secret`. The contract is a strong **in-domain stress test** because it mixes structured contact blocks, financial identifiers, corporate registrations, and long boilerplate where context determines whether a span is private.

## 2. Document under test

| Field | Value |
|-------|-------|
| Title | 蓝耘-算想-软件委托开发合同-20230719 |
| Language | Simplified Chinese |
| Length | ~500 lines / ~8–12k characters (~3–5k tokens) |
| Domain | B2B software outsourcing, IP & payment terms |
| Fit for 128k context | Yes — single-pass, no chunking required |

### 2.1 Gold-standard annotation (human review)

Two annotators (legal/ops + engineer) independently label spans, reconcile disagreements, and export BIOES-aligned offsets in UTF-8. Use **character offsets** (not byte offsets) for Chinese text.

#### Tier A — clear PII (must detect for demo success)

| ID | Span (excerpt) | Category | Location | Notes |
|----|----------------|----------|----------|-------|
| A1 | `赵亚雄` | `private_person` | §合同联系方式 | Named individual, project contact |
| A2 | `北京市海淀区黑泉路12号康健宝盛广场C座1层` | `private_address` | §合同联系方式 | Full street address |
| A3 | `15910236560` (×2) | `private_phone` | mobile + 微信 | Same number twice |
| A4 | `z@nascentcore.ai` | `private_email` | §合同联系方式 | Work email tied to individual |
| A5 | `1109 5105 0510 211` | `account_number` | §乙方指定收款账号 | Bank account with spaces |

#### Tier B — contextual / domain-sensitive (measure nuance)

| ID | Span (excerpt) | Suggested category | Policy question |
|----|----------------|-------------------|-----------------|
| B1 | `91110108MACOABHJ7A` | `account_number` or org ID | Unified Social Credit Code — public registry vs. sensitive in contract |
| B2 | `算想未来（北京）科技有限责任公司` | — (likely **not** PII) | Registered legal entity; should **not** be masked if model distinguishes public business names |
| B3 | `招商银行股份有限公司北京双榆树支行` | — or `private_address` | Financial institution branch; partial address |
| B4 | Contract signing date blanks / `20230719` (filename) | `private_date` | Transaction dates vs. generic durations (`36个月`) |
| B5 | `￥300000` / `三十万元` / `￥60000` | — | Commercial terms; not in taxonomy unless tied to individual |

#### Tier C — negative controls (should **not** mask)

| ID | Span | Why preserve |
|----|------|--------------|
| C1 | `云原生大模型训练平台` | Product/project name |
| C2 | `PyTorch+DeepSpeed` | Technology stack |
| C3 | `万分之五` / `1%5‱` | Legal penalty rates |
| C4 | `《中华人民共和国民法典》` | Public legal citation |
| C5 | Blank 甲方 fields | No span to detect |

**Primary eval set:** Tier A (5 span groups, 7 literal occurrences).  
**Secondary eval set:** Tier B (policy-dependent).  
**False-positive set:** Tier C.

## 3. Conditions (independent variables)

| Condition | Description |
|-----------|-------------|
| **PF-default** | Privacy Filter, default operating point (`openai/privacy-filter` via `opf redact` or HF pipeline) |
| **PF-high-recall** | Same model, recall-oriented preset (if using `opf` decoding controls) |
| **PF-high-precision** | Precision-oriented preset — for side-by-side demo of trade-off |
| **Regex-CN** | Deterministic baseline: CN mobile (`1[3-9]\d{9}`), email, bank-card-like digit groups |
| **Regex-EN** | Presidio / common EN patterns (expected weak on Chinese) |
| **No-filter** | Raw contract pasted into a mock LLM logging pipeline (illustrates risk only; no model call) |

Optional extension: **PF fine-tuned** on 50–200 labeled Chinese legal clauses (OpenAI reports 54% → 96% F1 with small in-domain fine-tune).

## 4. Procedure

### Phase 0 — Setup (local, no data leaves machine)

```bash
pip install "opf"  # or clone github.com/openai/privacy-filter
# GPU ~3 GB VRAM FP16; CPU 4–8 GB RAM acceptable for this doc size
```

Place contract text at `data/contracts/lanyun-suanxiang-20230719.txt` (UTF-8, normalize line endings).

### Phase 1 — Automated redaction pass

For each condition:

1. Run redaction on the full document (single pass, no chunking).
2. Save:
   - `outputs/<condition>/masked.txt`
   - `outputs/<condition>/spans.json` (start, end, label, confidence if available)
3. Record wall-clock latency and hardware (CPU vs GPU).

```bash
opf redact data/contracts/lanyun-suanxiang-20230719.txt \
  -o outputs/pf-default/masked.txt \
  --format json > outputs/pf-default/spans.json
```

### Phase 2 — Scoring against gold standard

Use span-level **exact match** (same offsets ±1 char tolerance for tokenizer edge cases) and **soft match** (overlap ≥ 0.8 IoU).

Per-category and micro-averaged:

- Precision = TP / (TP + FP)
- Recall = TP / (TP + FN)
- F1

Also report:

- **Critical recall** — recall on Tier A only (demo KPI: ≥ 95%)
- **Business-entity FP rate** — false masks on Tier C + B2
- **Latency** — ms per document, tokens/sec

Official tooling: `opf eval` with gold JSON in the format expected by `opf/_eval/`.

### Phase 3 — Human demo (5-minute stakeholder walkthrough)

1. **Before:** Show contact block (lines 391–403) and payment block (lines 87–94) in raw contract.
2. **Live run:** Execute `opf redact` on projector; show masked output side-by-side.
3. **Diff view:** Highlight detected spans colored by category (use HF Space or custom script).
4. **Baseline contrast:** Run Regex-CN on same text — show missed contextual PII (e.g., name without phone pattern nearby) and false positives on version numbers.
5. **Failure analysis:** Present any Tier B disagreements and Tier A misses — frame as tuning/fine-tuning need, not product failure.

### Phase 4 — Downstream utility check (optional)

Pipe masked text into a summarization prompt:

> Summarize payment terms and contact procedures.

Verify summary **does not** leak Tier A strings while preserving commercial meaning (amounts, percentages, milestones).

## 5. Hypotheses

| ID | Hypothesis | Falsified if |
|----|------------|--------------|
| H1 | PF-default achieves ≥ 90% recall on Tier A | Any A1–A5 span missed at default preset |
| H2 | PF outperforms Regex-CN on `private_person` (A1) | Regex matches name; PF misses |
| H3 | PF has lower FP on company names (B2) than Regex-CN | Company name masked by PF |
| H4 | Chinese-primary doc shows lower F1 than English translation of same contract | EN F1 − CN F1 > 15 pts (language gap) |
| H5 | High-recall preset lifts Tier A recall with ≤ 2 extra FP on Tier C | FP count explodes on boilerplate |

## 6. Expected outcomes (for demo narrative)

**Likely strengths (based on model card + contract structure)**

- `private_phone`, `private_email`: formatted literals in a labeled contact section — similar to benchmark email/phone cases.
- `account_number`: spaced bank account `1109 5105 0510 211`.
- `private_address`: full Chinese street address in structured block.

**Likely challenges**

- **Language:** Model card lists English-primary training; Chinese legal prose may reduce recall on A1 (person name without Western token boundaries).
- **Entity typing:** Corporate name 算想未来 vs. person 赵亚雄 — tests context-aware `private_person` boundary.
- **USCC** `91110108MACOABHJ7A`: may be missed or mislabeled — good teaching moment for taxonomy limits.
- **Dates:** Contract duration vs. signing dates — tests `private_date` precision.
- **Secrets:** No API keys in doc — `secret` category inactive (note as N/A).

## 7. Deliverables

| Artifact | Purpose |
|----------|---------|
| `gold_standard.json` | Annotated spans (Tier A/B/C) |
| `results/metrics.csv` | Per-condition P/R/F1 |
| `results/latency.json` | Throughput for production sizing |
| `demo/side_by_side.html` | Red vs. green diff for presentation |
| `demo/one_pager.md` | Executive summary: critical recall, FP examples, recommendation |

## 8. Success criteria (demo-ready)

| Metric | Target |
|--------|--------|
| Tier A recall (PF-default) | ≥ 95% |
| Tier A recall (PF-high-recall) | 100% if default misses ≤ 1 span |
| Tier C precision | ≥ 98% (no masking of project name / law citations) |
| End-to-end latency (single doc, GPU) | < 2 s |
| vs. Regex-CN F1 on Tier A | PF higher by ≥ 10 F1 points |

## 9. Ethics & limitations (state in demo)

- Privacy Filter is **not** anonymization certification or legal compliance (GDPR/PIPL).
- Redacted contract should still be treated as confidential; run **on-prem**.
- Human review required before using masked text for training or third-party LLM APIs.
- Annotators must consent to handle real PII; use masked artifacts in slides.

## 10. Minimal gold-standard seed (JSON)

```json
{
  "document_id": "lanyun-suanxiang-20230719",
  "spans": [
    {"id": "A1", "start": null, "end": null, "text": "赵亚雄", "label": "private_person", "tier": "A"},
    {"id": "A2", "start": null, "end": null, "text": "北京市海淀区黑泉路12号康健宝盛广场C座1层", "label": "private_address", "tier": "A"},
    {"id": "A3a", "start": null, "end": null, "text": "15910236560", "label": "private_phone", "tier": "A"},
    {"id": "A4", "start": null, "end": null, "text": "z@nascentcore.ai", "label": "private_email", "tier": "A"},
    {"id": "A5", "start": null, "end": null, "text": "1109 5105 0510 211", "label": "account_number", "tier": "A"}
  ],
  "notes": "Fill start/end with char offsets after UTF-8 normalization"
}
```

## 11. Suggested demo script (talk track)

1. **Problem (30 s):** Contracts fed into AI indexing/logging expose contact and payment PII.
2. **Approach (30 s):** Local, single-pass Privacy Filter before any cloud LLM step.
3. **Evidence (3 min):** Live redaction of this contract; walk through Tier A hits.
4. **Comparison (1 min):** Regex baseline misses name; or over-masks amounts.
5. **Honest limits (1 min):** Chinese + USCC edge cases; fine-tune path.
6. **Ask:** Pilot on contract ingestion pipeline with high-recall preset + human QA queue.

---

*Attachment: 蓝耘-算想-软件委托开发合同-20230719 (uploaded markdown). Primary contact PII concentrated in §合同联系方式; financial identifier in §乙方指定收款账号.*
