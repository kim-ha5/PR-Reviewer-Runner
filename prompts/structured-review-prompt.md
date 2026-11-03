# Security Review Report

You are producing a mini security review report from a static-analysis
finding. Follow the sections below in order so that every finding is explained
consistently and with enough detail for a follow-up investigation.

Return only valid JSON. Do not wrap the JSON in Markdown code fences.

Return one object for every finding, preserving the finding's zero-based
`finding_index`:

[
  {
    "finding_index": 0,
    "finding_summary": "Restate the analyzer signal and affected operation in 1-2 sentences.",
    "data_flow": "Trace the value from input to sink in 2-4 sentences.",
    "security_boundary": "Explain what trusted part of the application receives unsafe or untrusted data, and why that matters, in 1-2 beginner-friendly sentences.",
    "explanation": "Explain the finding and why the operation is unsafe in one focused paragraph.",
    "impact": "State the likely attacker outcome and required condition in 1-2 sentences."
  }
]

Apply these review rules:
- A true positive must be tied to a concrete operation in the supplied code.
- Prefer precise code facts and data flow over generic vulnerability definitions.
- Do not speculate about framework configuration, authentication, reachability,
  or deployment.
- Do not include remediation advice, severity labels, or any extra JSON keys.
- Preserve every input finding exactly once, even when evidence is incomplete.
- Return exactly the fields shown above and no others.

CodeQL findings:
{{codeql_result}}

Relevant source code:
{{source_code}}
