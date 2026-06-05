# Privacy Filter Contract Experiment — Results

> **Future reference:** See [`NOTES.md`](NOTES.md) for reproduction steps, technical caveats, and policy notes.

**Run date:** 2026-06-05  
**Model:** `openai/privacy-filter` (default preset, CPU)  
**Document:** 蓝耘-算想-软件委托开发合同-20230719 (~9,149 chars)  
**Status:** Completed — Tier A recall target met (≥95%)

## Summary

| Metric | Result |
|--------|--------|
| Tier A critical recall | **100%** (5/5 groups, 7 span occurrences) |
| Spans detected | 7 |
| False positives (Tier C) | 0 |
| Extra detection | USCC `91110108MACOABHJ7A` masked as `account_number` |
| Latency (CPU) | 240.6 s |

## Detected spans

| Label | Text | Gold tier |
|-------|------|-----------|
| `private_person` | 张三 | A1 ✓ |
| `private_address` | 北京市朝阳区示例路1号示例大厦A座1层 | A2 ✓ |
| `private_phone` | 13800138000 (×2) | A3 ✓ |
| `private_email` | example@example.com | A4 ✓ |
| `account_number` | 1234 5678 9012 345 | A5 ✓ |
| `account_number` | 91110108MACOABHJ7A | B1 (bonus) |

## Preserved (not masked)

- 云原生大模型训练平台
- 算想未来（北京）科技有限责任公司
- 《中华人民共和国民法典》
- Contract amounts (￥300000, etc.)

## Regex-CN baseline (same document)

| Pattern | Matched |
|---------|---------|
| CN mobile `1[3-9]\d{9}` | Yes |
| Email | No (escaped `\.` in source markdown) |
| Bank digit groups | Yes |
| Person after 联系人 | Pattern match only; no span labeling |

Privacy Filter caught the email and Chinese person name that regex missed or could not label.

## Artifacts

- `outputs/pf-default.json` — full model output
- `outputs/results.json` — scored metrics
- `outputs/run.log` — download + inference log
