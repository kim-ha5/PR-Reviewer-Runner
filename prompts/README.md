# Prompt variants

These templates all use the schema required by `llm_test.py`, so they can be
compared by passing a different `--prompt` path:

```powershell
.\.venv\Scripts\python.exe .\llm_test.py --prompt .\prompts\evidence-first-prompt.md
```

| Template | Main trade-off |
| --- | --- |
| `test-prompt.md` | Simple baseline explanation |
| `evidence-first-prompt.md` | Strict source/data-flow grounding |
| `developer-mentor-prompt.md` | More teaching context for beginners |
| `triage-focused-prompt.md` | Short, high-signal queue-ready output |
| `false-positive-resistant-prompt.md` | Explicit uncertainty and conservative claims |
| `structured-review-prompt.md` | Repeatable rubric across findings |


