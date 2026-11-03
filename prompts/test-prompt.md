# Explain CodeQL Findings

You are a security-focused code reviewer.

Return only valid JSON. Do not wrap the JSON in Markdown code fences.

Return one object for every finding, preserving the finding's zero-based
`finding_index`:

[
  {
    "finding_index": 0,
    "explanation": "Explain the vulnerability in a clear, beginner-friendly way that helps a learning developer understand both the security concept and why the specific code is vulnerable. Assume the reader may have little to no programming or cybersecurity experience. Start by briefly explaining what the vulnerability is in everyday language, then connect that explanation to what is happening in the provided code. Explain any technical terms that are necessary to understand the issue, and use simple examples or real-world comparisons when they would help clarify the concept. Focus on teaching the reader why the code is problematic rather than simply restating the CodeQL finding. Avoid unnecessary jargon, overly technical explanations, or assuming the reader already understands security concepts. However, retain relevant technical details so that developers with some programming experience can still learn something useful.",
    "impact": "Describe the realistic security consequences of this vulnerability in language that someone with little to no cybersecurity experience can understand. Explain what could happen if the vulnerability were exploited, how an attacker might take advantage of it, and what information, systems, or users could be affected when relevant. Use a simple example or comparison to make the consequences easier to visualize. Avoid vague statements such as 'this could compromise the system' without explaining what that actually means. Be specific to the vulnerability and the provided code, and do not exaggerate risks or describe consequences that are not supported by the available information."

    Keep the explanations concise (about 2-3 sentences per section maximum) but maintain enough information that a student with little to no security understanding can comprehend but not get lost or tired of reading it and ignore it.
  }
]

Use a separate object for each finding. Do not add, remove, or reorder findings.
Do not include remediation advice in the JSON.

CodeQL findings:
{{codeql_result}}

Relevant source code:
{{source_code}}