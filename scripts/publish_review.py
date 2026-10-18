import argparse
import json
import os
from pathlib import Path

import requests


API_URL = "https://api.github.com"


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON file: {path}") from error


def github_request(method, url, token, **kwargs):
    headers = kwargs.pop("headers", {})
    headers.update(
        {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    response = requests.request(
        method, url, headers=headers, timeout=30, **kwargs
    )
    response.raise_for_status()
    return response.json() if response.content else None


def find_pull_request(repository, commit_sha, token):
    url = f"{API_URL}/repos/{repository}/commits/{commit_sha}/pulls"
    pull_requests = github_request("GET", url, token, params={"per_page": 100})
    if not pull_requests:
        raise RuntimeError(f"No pull request found for commit {commit_sha}.")
    return pull_requests[0]["number"]


def review_body(finding, explanation, impact, marker):
    return (
        f"{marker}\n\n"
        f"### {finding.get('title', 'CodeQL finding')}\n\n"
        f"{explanation}\n\n"
        f"**Impact:** {impact}\n\n"
        f"**CodeQL rule:** `{finding['rule_id']}`"
    )


def publish_review(findings, explanations, repository, commit_sha, token):
    if len(findings) != len(explanations):
        raise ValueError("Findings and LLM explanations must have the same length.")

    pull_number = find_pull_request(repository, commit_sha, token)
    marker = f"<!-- pr-reviewer-runner:{commit_sha} -->"
    reviews_url = f"{API_URL}/repos/{repository}/pulls/{pull_number}/reviews"

    existing_reviews = github_request(
        "GET", reviews_url, token, params={"per_page": 100}
    )
    if any(marker in (review.get("body") or "") for review in existing_reviews):
        print(f"Review for commit {commit_sha} already exists; skipping.")
        return

    comments = []
    unlocated = []
    for index, finding in enumerate(findings):
        explanation = explanations[index]
        body = review_body(
            finding,
            explanation["explanation"],
            explanation["impact"],
            marker,
        )
        locations = finding.get("locations") or []
        location = locations[0] if locations else {}
        path = location.get("file")
        line = location.get("start_line")
        if isinstance(path, str) and path and isinstance(line, int) and line > 0:
            comments.append(
                {
                    "path": path,
                    "line": line,
                    "side": "RIGHT",
                    "body": body,
                }
            )
        else:
            unlocated.append(body)

    summary = (
        f"{marker}\n\n"
        "Automated plain-language security explanations generated from CodeQL."
    )
    if unlocated:
        summary += "\n\n## Findings without an inline location\n\n"
        summary += "\n\n".join(unlocated)

    payload = {
        "commit_id": commit_sha,
        "body": summary,
        "event": "COMMENT",
        "comments": comments,
    }
    try:
        github_request("POST", reviews_url, token, json=payload)
    except requests.HTTPError as error:
        if error.response is None or error.response.status_code != 422:
            raise
        fallback_body = (
            f"{summary}\n\n"
            "## Inline explanations\n\n"
            "GitHub could not attach these findings to the current diff:\n\n"
            + "\n\n".join(
                f"- **{comment['path']}:{comment['line']}**\n\n{comment['body']}"
                for comment in comments
            )
        )
        github_request(
            "POST",
            reviews_url,
            token,
            json={
                "commit_id": commit_sha,
                "body": fallback_body,
                "event": "COMMENT",
                "comments": [],
            },
        )
        print("Published review summary because inline locations were rejected.")
    print(
        f"Published review {pull_number} with "
        f"{len(comments)} inline comment(s)."
    )


def main():
    parser = argparse.ArgumentParser(
        description="Publish structured LLM explanations as a pull request review."
    )
    parser.add_argument("--findings", type=Path, required=True)
    parser.add_argument("--llm-review", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY"),
        help="owner/repository; defaults to GITHUB_REPOSITORY",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"),
        help="GitHub token; defaults to GITHUB_TOKEN or GH_TOKEN",
    )
    args = parser.parse_args()

    if not args.repository or not args.token:
        raise ValueError("A repository and GitHub token are required.")

    findings = load_json(args.findings)
    explanations = load_json(args.llm_review)
    if not isinstance(findings, list) or not isinstance(explanations, list):
        raise ValueError("Findings and LLM review files must contain JSON arrays.")

    publish_review(
        findings,
        explanations,
        args.repository,
        args.commit,
        args.token,
    )


if __name__ == "__main__":
    main()
