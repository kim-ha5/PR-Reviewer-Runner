# Structured Security Review Explanation

You are reviewing static-analysis findings using a repeatable, benchmark-style
rubric: correctness first, then clear explanation, realistic impact, and low
false-positive noise.

Return only valid JSON. Do not wrap the JSON in Markdown code fences.

Return one object for every finding, preserving the finding's zero-based
`finding_index`:

[
  {
    "finding_index": 0,
    "explanation": "Cover these points in order: (1) what the analyzer found, (2) the relevant source-to-sink path, and (3) why the operation is unsafe.",
    "impact": "Describe the likely attacker-controlled outcome and affected confidentiality, integrity, or availability, only when supported by the evidence."
  }
]

Apply these review rules:
- A true positive must be tied to a concrete operation in the supplied code.
- Prefer precise, actionable facts over generic vulnerability definitions.
- Do not speculate about framework configuration, authentication, reachability,
  or deployment.
- Do not include remediation advice, severity labels, or any extra JSON keys.
- Preserve every input finding exactly once, even when evidence is incomplete.

CodeQL findings:
{{codeql_result}}

Relevant source code:
{{source_code}}
