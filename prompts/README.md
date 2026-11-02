# Prompt variants

These templates all use the schema required by `llm_test.py`, so they can be
compared by passing a different `--prompt` path:

```powershell
.\.venv\Scripts\python.exe .\llm_test.py --prompt .\prompts\evidence-first-prompt.md
```

| Template | Main trade-off |
| --- | --- |
| `test-prompt.md` | General detailed explanation |
| `evidence-first-prompt.md` | Forensic source-to-sink reconstruction |
| `developer-mentor-prompt.md` | Guided lesson with a hypothetical scenario |
| `triage-focused-prompt.md` | Exploitability and reachability assessment |
| `false-positive-resistant-prompt.md` | Claim-calibrated uncertainty analysis |
| `structured-review-prompt.md` | Fixed mini-report with section headings |

The variants use a few focused sections rather than one oversized explanation.
`llm_test.py` validates the optional sections, and the publisher includes them
in the pull-request review.
