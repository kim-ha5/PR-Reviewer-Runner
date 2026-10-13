
import glob
import json
from pathlib import Path


def extract_findings():
    sarif_files = glob.glob("sarif-results/*.sarif")
    findings = []

    if not sarif_files:
        raise FileNotFoundError(
            "No SARIF files found in sarif-results/"
        )

    for sarif_file in sarif_files:
        with open(sarif_file, encoding="utf-8") as file:
            sarif = json.load(file)

        for run in sarif.get("runs", []):
            tool = run.get("tool", {}).get("driver", {})
            rules = {
                rule.get("id"): rule
                for rule in tool.get("rules", [])
            }

            for result in run.get("results", []):
                rule_id = result.get("ruleId", "unknown")
                rule = rules.get(rule_id, {})

                locations = []
                for item in result.get("locations", []):
                    physical = item.get(
                        "physicalLocation", {}
                    )
                    region = physical.get("region", {})

                    locations.append({
                        "file": physical.get(
                            "artifactLocation", {}
                        ).get("uri"),
                        "start_line": region.get("startLine"),
                        "end_line": region.get("endLine"),
                        "start_column": region.get("startColumn"),
                    })

                flow_steps = []
                for flow in result.get("codeFlows", []):
                    for thread in flow.get("threadFlows", []):
                        for step in thread.get("locations", []):
                            loc = step.get("location", {})
                            physical = loc.get(
                                "physicalLocation", {}
                            )
                            region = physical.get("region", {})

                            flow_steps.append({
                                "file": physical.get(
                                    "artifactLocation", {}
                                ).get("uri"),
                                "line": region.get("startLine"),
                                "description": loc.get(
                                    "message", {}
                                ).get("text", ""),
                            })

                findings.append({
                    "rule_id": rule_id,
                    "title": rule.get(
                        "shortDescription", {}
                    ).get("text", rule_id),
                    "message": result.get(
                        "message", {}
                    ).get("text", ""),
                    "severity": rule.get(
                        "properties", {}
                    ).get("security-severity"),
                    "level": result.get("level"),
                    "locations": locations,
                    "data_flow": flow_steps,
                })

    output = Path("codeql-findings.json")
    output.write_text(
        json.dumps(findings, indent=2),
        encoding="utf-8",
    )

    print(f"Extracted {len(findings)} finding(s).")
    print(f"Saved to {output}")


if __name__ == "__main__":
    extract_findings()
