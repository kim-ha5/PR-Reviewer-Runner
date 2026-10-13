import json
import sys
from pathlib import Path


def load_findings(path: Path) -> list[dict]:
    """Load and validate the CodeQL findings JSON."""
    if not path.is_file():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Expected the input JSON to be an array.")

    for index, finding in enumerate(data):
        if not isinstance(finding, dict):
            raise ValueError(
                f"Finding at index {index} must be a JSON object."
            )

        if not isinstance(finding.get("rule_id"), str):
            raise ValueError(
                f"Finding at index {index} is missing a valid rule_id."
            )

    return data


def main():
    input_path = Path(
        sys.argv[1] if len(sys.argv) > 1
        else "findings/codeql-findings.json"
    )
    output_path = Path(
        sys.argv[2] if len(sys.argv) > 2
        else "findings/llm-input.json"
    )

    try:
        findings = load_findings(input_path)

        # Keep all fields extracted by CodeQL, including data-flow details.
        output = {
            "schema_version": "1.0",
            "source": "CodeQL",
            "finding_count": len(findings),
            "findings": findings,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(output, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        print(f"Loaded {len(findings)} CodeQL findings.")
        print(f"Output written to: {output_path}")
        print("Handoff preparation successful.")

    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error preparing findings: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()