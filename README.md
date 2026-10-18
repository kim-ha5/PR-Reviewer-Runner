# PR-Reviewer-Runner

## Local CodeQL and Ollama test

`testing_code.py` is intentionally vulnerable so the CodeQL-to-LLM handoff can
be tested. The GitHub Actions workflow runs CodeQL and
`scripts/extract_output.py`, which writes `codeql-findings.json`. The local
Ollama test then loads that JSON, the source file, and
`prompts/test-prompt.md` before sending the completed prompt to Qwen:

```powershell
.\.venv\Scripts\python.exe .\llm_test.py `
  --findings .\codeql-findings.json `
  --source .\testing_code.py `
  --prompt .\prompts\test-prompt.md
```

The findings file must be a JSON array in the format produced by
`scripts/extract_output.py`. Run CodeQL first; `llm_test.py` reports a clear
error when the findings file is missing, invalid, or empty.

## GitHub Actions CodeQL and Ollama workflow

The `CodeQL` workflow runs the analysis and uploads the extracted findings.
After it succeeds, `LLM Review` runs on a fresh Ubuntu runner and:

1. Installs Ollama and the Python `requests` dependency.
2. Starts Ollama and downloads `qwen2.5:7b`.
3. Runs `llm_test.py` with the CodeQL findings and source file.
4. Publishes a pull-request review with an inline layman explanation for each
   finding with a valid source location.
5. Uploads `findings/llm-review.md` and `findings/llm-review.json` as the
   `llm-review` artifact.

Because GitHub-hosted runners are temporary, Ollama and the model are
downloaded on every workflow run. The model download and review can take
several minutes.

To test the workflow, push a branch containing a change to
`testing_code.py`, open a pull request, and wait for both workflows to
complete. The generated explanation appears in the pull request's Files
changed or Conversation view. The workflow also uploads the raw Markdown and
validated JSON responses as artifacts.

The workflow skips publishing a duplicate review when it is rerun for the
same commit. Findings without a valid inline location are retained in the
review summary because GitHub only accepts inline comments on valid pull
request diff lines.