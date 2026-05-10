"""
Constitution contradiction checker — called by the constitution-review workflow.

For each changed teams/<team>/constitutions/<domain>.md file, reads the
corresponding domain constitution, calls GitHub Models, and posts a PR comment
with findings classified as BLOCKER / WARNING / OK.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

GITHUB_MODELS_URL = "https://models.inference.ai.azure.com"
MODEL = "gpt-4o"

_SYSTEM_PROMPT = """\
You are a governance reviewer. Your job is to detect contradictions between a
domain constitution and a team-specific addendum.

Rules:
- Teams may ONLY add constraints. They may not relax, override, or contradict domain rules.
- A team saying "we require X" when the domain already requires X is redundant but not a contradiction.
- A team saying "we allow Y" when the domain prohibits Y is a BLOCKER.
- A team using vague language that could be interpreted as relaxing a domain rule is a WARNING.
- A team adding a new, more specific constraint is OK.

Be precise and concise. Avoid false positives — only flag genuine contradictions or ambiguities.
"""

_USER_PROMPT = """\
Review this team constitution addendum for contradictions against the domain constitution.

DOMAIN CONSTITUTION (`{domain}`):
---
{domain_content}
---

TEAM ADDENDUM (`{team}` team, `{domain}` domain):
---
{team_content}
---

Respond in this exact format — no prose outside the format:

VERDICT: <OK|WARNING|BLOCKER>

FINDINGS:
- [<OK|WARNING|BLOCKER>] <finding>

SUMMARY: <one sentence>
"""


def call_model(domain: str, team: str, domain_content: str, team_content: str) -> str:
    token = os.environ["GITHUB_TOKEN"]
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _USER_PROMPT.format(
                    domain=domain,
                    team=team,
                    domain_content=domain_content,
                    team_content=team_content,
                ),
            },
        ],
        "temperature": 0,
        "max_tokens": 600,
    }
    req = urllib.request.Request(
        f"{GITHUB_MODELS_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["choices"][0]["message"]["content"]


def parse_verdict(result: str) -> str:
    for line in result.splitlines():
        if line.startswith("VERDICT:"):
            v = line.split(":", 1)[1].strip()
            if v in ("OK", "WARNING", "BLOCKER"):
                return v
    return "WARNING"


def post_pr_comment(body: str) -> None:
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    pr = os.environ["PR_NUMBER"]
    url = f"https://api.github.com/repos/{repo}/issues/{pr}/comments"
    req = urllib.request.Request(
        url,
        data=json.dumps({"body": body}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    urllib.request.urlopen(req)


def read_domain_constitution(domain: str) -> str | None:
    path = Path("constitution.md") if domain == "global" else Path(f"constitutions/{domain}.md")
    return path.read_text() if path.exists() else None


def main() -> int:
    changed_files = [f for f in sys.argv[1:] if f.endswith(".md")]
    if not changed_files:
        print("No constitution files to check.")
        return 0

    sections: list[str] = ["## Constitution contradiction check\n"]
    has_blocker = False

    for file_path in changed_files:
        parts = Path(file_path).parts
        # Expected: teams / <team> / constitutions / <domain>.md
        if len(parts) < 4 or parts[0] != "teams" or parts[2] != "constitutions":
            continue

        team = parts[1]
        domain = parts[3].removesuffix(".md")

        print(f"Checking {file_path} (team={team}, domain={domain})...")

        team_content = Path(file_path).read_text()
        domain_content = read_domain_constitution(domain)

        if domain_content is None:
            sections.append(
                f"### ⚠️ `{file_path}`\n"
                f"No domain constitution found for `{domain}`. "
                f"Create `constitutions/{domain}.md` before adding team addenda.\n"
            )
            continue

        result = call_model(domain, team, domain_content, team_content)
        verdict = parse_verdict(result)
        icon = {"OK": "✅", "WARNING": "⚠️", "BLOCKER": "🚫"}[verdict]

        if verdict == "BLOCKER":
            has_blocker = True

        sections.append(
            f"### {icon} `{file_path}` — {verdict}\n\n"
            f"```\n{result.strip()}\n```\n"
        )

    sections.append(
        "---\n"
        "*Advisory only — the domain owner makes the final call.*  \n"
        "*Powered by [GitHub Models](https://github.com/marketplace/models).*"
    )

    post_pr_comment("\n".join(sections))

    # Exit 1 on BLOCKER so the check shows as failed in the PR (non-blocking by default)
    return 1 if has_blocker else 0


if __name__ == "__main__":
    sys.exit(main())
