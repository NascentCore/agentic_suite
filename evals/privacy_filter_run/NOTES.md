# Privacy Filter Contract Experiment — Future Reference

Canonical notes for re-running, extending, or presenting this evaluation.

## Experiment summary

We evaluated [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/) (`openai/privacy-filter`) on a real B2B software-development contract (蓝耘–算想, 2023-07-19) to test whether a local, context-aware PII model can sanitize legal documents before they enter AI indexing, logging, or summarization pipelines.

**Outcome:** The model detected every Tier-A sensitive span (100% critical recall) with zero false positives on negative controls, despite the document being primarily Simplified Chinese.

| What we tested | How | Result |
|----------------|-----|--------|
| Contact PII block | Single-pass `opf redact` on full contract | Name, address, phone ×2, email — all masked |
| Payment identifier | Same run | Bank account masked |
| Corporate registry ID | Same run | USCC also masked as `account_number` (policy-dependent) |
| Negative controls | Manual check of redacted output | Project name, company name, law citations, amounts preserved |
| Regex baseline | CN phone/email/bank patterns | Missed escaped email; no span labeling for person name |

**Hardware note:** First run used CPU only (~241 s for ~9k chars). GPU is expected to be sub-second per OpenAI docs; download is ~2.8 GB one-time.

---

## Repository layout

```
evals/
├── privacy_filter_contract_experiment.md   # Original protocol (design + hypotheses)
└── privacy_filter_run/
    ├── NOTES.md                            # This file
    ├── RESULTS.md                          # Scored metrics table
    ├── data/contract.txt                   # UTF-8 contract (from uploaded markdown)
    └── outputs/
        ├── pf-default.json                 # Full opf JSON output + redacted text
        ├── results.json                    # Machine-readable scores
        └── run.log                         # Model download + inference log
```

---

## How to reproduce

### Prerequisites

```bash
git clone https://github.com/openai/privacy-filter.git /tmp/privacy-filter
pip install -e /tmp/privacy-filter
```

- Python ≥ 3.10
- ~3 GB disk for model weights (auto-downloaded to `~/.opf/privacy_filter`)
- GPU optional but strongly recommended for latency

### Run

```bash
cd evals/privacy_filter_run
opf redact --device cpu --format json -f data/contract.txt > outputs/pf-default.json 2> outputs/run.log
# Use --device cuda (or default) when GPU is available
```

### Score

```bash
python3 -c "import json; print(json.load(open('outputs/results.json')))"
```

Re-score after re-run by adapting the scoring script in commit `1240d5e` or by comparing `detected_spans` in `pf-default.json` against the Tier A table in `RESULTS.md`.

---

## Gold-standard tiers (annotation policy)

### Tier A — must detect (demo KPI: ≥95% recall)

| ID | Span | Label | Section |
|----|------|-------|---------|
| A1 | 张三 | `private_person` | 合同联系方式 |
| A2 | 北京市朝阳区示例路1号示例大厦A座1层 | `private_address` | 合同联系方式 |
| A3 | 13800138000 (mobile + 微信) | `private_phone` | 合同联系方式 |
| A4 | example@example.com | `private_email` | 合同联系方式 |
| A5 | 1234 5678 9012 345 | `account_number` | 乙方指定收款账号 |

**Actual run:** 5/5 groups, 7 literal span occurrences — **100% recall**.

### Tier B — contextual (not counted in critical recall)

| ID | Span | Observed behavior |
|----|------|-------------------|
| B1 | 91110108MACOABHJ7A | **Masked** as `account_number` — reasonable for strict redaction; debatable for public registry IDs |
| B2 | 算想未来（北京）科技有限责任公司 | **Preserved** — correct (legal entity, not private person) |
| B3 | 招商银行股份有限公司北京双榆树支行 | **Preserved** |
| B4 | Dates / durations | **Preserved** (`36个月`, blank signing date) |
| B5 | ￥300000, 三十万元, ￥60000 | **Preserved** |

### Tier C — negative controls (must not mask)

All preserved in actual run: 云原生大模型训练平台, PyTorch+DeepSpeed, 《中华人民共和国民法典》, penalty rates.

---

## Important technical notes

### 1. Input format matters

The contract was stored as **markdown** with escaped punctuation (`\.`, `\(`, `\)`). Privacy Filter still detected the email span as `example@example\.ai`. Regex email patterns failed because of the escaped dot. For production, normalize source text (plain UTF-8 `.docx`/`.txt` export) before redaction.

### 2. Model is not on PyPI as `opf`

Install from the GitHub repo only:

```bash
pip install -e /path/to/privacy-filter
```

The CLI binary is `opf`; subcommands include `redact`, `eval`, `train`.

### 3. First run downloads ~2.8 GB

Checkpoint lands at `~/.opf/privacy_filter` (or `$OPF_CHECKPOINT`). Subsequent runs reuse it.

### 4. JSON output parsing

`opf redact --format json` prints JSON to stdout but may append ANSI color legend and color-coded preview after the JSON object. When parsing programmatically, split on `"color legend:"` or use only the first JSON object.

### 5. Latency expectations

| Environment | Observed / expected |
|-------------|---------------------|
| CPU (this run) | ~241 s for ~9k chars |
| GPU (per model card) | Sub-second for similar length |

Do not use CPU latency as a production SLA without re-benchmarking.

### 6. Chinese legal text performed better than hypothesized

The model card lists English-primary training. This contract still achieved full Tier-A recall including Chinese person name and address. Do not assume failure on Chinese — always re-evaluate on your own distribution.

### 7. Categories not triggered in this document

- `private_url` — none present
- `private_date` — none flagged (durations and blank dates left alone)
- `secret` — no API keys or passwords in contract

### 8. Privacy Filter is not compliance tooling

Per OpenAI: not anonymization certification, not GDPR/PIPL compliance, not a substitute for legal review. Use as a **pre-filter** with human QA for high-stakes workflows.

### 9. Operating-point tuning

The run used **default** Viterbi decoding. For stricter recall (e.g., catch borderline dates), try high-recall presets via `opf redact --help` / Viterbi calibration artifacts in the checkpoint. For fewer USCC-style flags, try high-precision presets.

### 10. Fine-tuning path

If future contracts show misses on Chinese names or domain-specific IDs, OpenAI reports large F1 gains from small in-domain fine-tunes (`opf train`). Keep a labeled JSONL of contract clauses for that.

---

## Comparison vs. regex baseline

| Capability | Privacy Filter | Regex-CN |
|------------|----------------|----------|
| Chinese mobile | ✓ | ✓ |
| Email (escaped markdown) | ✓ | ✗ |
| Bank account (spaced digits) | ✓ | ✓ |
| Person name (contextual) | ✓ | Pattern only, no label |
| Company vs. person disambiguation | ✓ | ✗ |
| USCC / registry IDs | Masked (policy call) | ✗ |

---

## Suggested next steps

1. **Re-run on GPU** and record latency for production sizing.
2. **Add Tier B policy file** — decide whether USCC should be masked per org policy.
3. **Test high-recall / high-precision presets** on the same contract.
4. **Plain-text export** — re-run without markdown escaping to confirm email/regex delta.
5. **Downstream demo** — summarize masked contract via LLM; verify no Tier-A leakage.
6. **Do not commit live PII** — `data/contract.txt` contains real contact/payment data; treat as sensitive in forks and public repos.

---

## One-line executive summary

Privacy Filter locally redacted 100% of contact and payment PII in a Chinese commercial contract in one pass, with no false positives on business terms, at the cost of ~4 minutes on CPU (use GPU in production).

---

## References

- [Introducing OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/)
- [GitHub: openai/privacy-filter](https://github.com/openai/privacy-filter)
- [Hugging Face: openai/privacy-filter](https://huggingface.co/openai/privacy-filter)
- Design protocol: `evals/privacy_filter_contract_experiment.md`
- Scored run: `evals/privacy_filter_run/RESULTS.md`
