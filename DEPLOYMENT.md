# Deploying Nomos — the delegation model

This document covers how to move from running Nomos locally to running a shared
instance that every team delegates to.

The delegation model has three roles:

| Role | Responsibility |
|---|---|
| **Platform team** | Deploys one shared Nomos instance, maintains the governance repo |
| **Team member** | Connects their AI agent to the shared server |
| **CI pipeline** | Runs `nomos-validate` or Gherkin checks against the shared server |

---

## Part 1 — Platform team: deploy the shared instance

### Option A — Process (simplest, no Docker required)

```bash
pip install nomos

# GitHub mode: Nomos reads the governance repo directly from GitHub
nomos \
  --github https://github.com/your-org/your-governance-repo \
  --host 0.0.0.0 \
  --port 8080

# Run as a background service (systemd, supervisord, screen, etc.)
```

Set `GITHUB_TOKEN` if the governance repo is private:

```bash
export GITHUB_TOKEN=ghp_...
nomos --github https://github.com/your-org/your-governance-repo --host 0.0.0.0
```

### Option B — Docker (recommended for production)

Create a `.env` file on the server:

```bash
# .env
GOVERNANCE_REPO_URL=https://github.com/your-org/your-governance-repo
GITHUB_TOKEN=ghp_...
GITHUB_BRANCH=main
CACHE_TTL_SECONDS=300
```

Run with Docker Compose — copy `docker-compose.yml` from this template:

```bash
docker compose up -d
```

The server is now running on port 8080. Verify:

```bash
curl http://your-server:8080/health
# → {"status": "ok"}
```

### Set up the GitHub webhook (required for live rule propagation)

Without a webhook, Nomos caches governance rules for `CACHE_TTL_SECONDS` (default: 5 minutes). A webhook ensures rule changes propagate immediately.

In your governance repo on GitHub:

1. Go to **Settings → Webhooks → Add webhook**
2. Payload URL: `https://your-server:8080/webhook/github`
3. Content type: `application/json`
4. Events: **Just the push event**
5. Active: ✓

When a rule changes and is pushed to `main`, the webhook fires, Nomos invalidates its cache, and the next request sees the updated rules.

---

## Part 2 — Team member: connect your AI agent

Each project repo that should be governed needs a `.mcp.json` at its root.
This tells Claude Code (or any MCP-compatible agent) where the governance server is.

```bash
# In your project repo (not the governance repo)
pip install nomos
nomos install-hooks --server https://governance.yourcompany.com
```

This creates `.mcp.json` and installs the pre-commit hook (see Part 3) in one step.

Commit `.mcp.json`. Every engineer who clones the project gets governance automatically.

**Or manually**, if you prefer not to install Nomos locally:

```bash
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "nomos": {
      "type": "http",
      "url": "https://governance.yourcompany.com/mcp"
    }
  }
}
EOF
```

### What the agent can now do

Once connected, the agent can call governance tools before generating code:

```
list_constitutions()          → ["global", "kafka", "camel"]
get_constitution("kafka")     → platform principles for Kafka
get_kafka_conventions()       → topic naming pattern, valid prefixes, RBAC roles
validate_topic_name("...")    → {valid: true/false, errors: [...]}
list_adrs()                   → all architectural decisions
search_adrs("consumer group") → ADRs matching the query
```

A governed agent queries the server before generating a topic name, SA name, or RBAC binding — and produces valid output on the first attempt.

---

## Part 3 — Team member: add a pre-commit hook

Pre-commit hooks validate resources locally before they reach CI. They call the shared server — no local files needed.

### Install the hook

If you ran `nomos install-hooks` in Part 2, the hook is already installed. Skip to "Customise the hook" below.

Otherwise:

```bash
nomos install-hooks --server https://governance.yourcompany.com
```

This installs `.git/hooks/pre-commit` (executable) and `.mcp.json` in the current directory.

### Customise the hook

The installed hook is a template. Open `.git/hooks/pre-commit` and uncomment the validation sections that apply to your project:

```bash
# Example: validate topic names found in staged HCL files
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep "topics\.hcl" || true)
for f in $STAGED; do
  # Extract topic keys and pass to nomos-validate
  nomos-validate --server "$NOMOS_SERVER" topic <extracted-name>
done
```

Adapt the extraction logic to your HCL structure. The hook template includes commented examples for topics, SAs, and RBAC.

### Or use pre-commit framework

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: nomos-validate-topics
        name: Validate Kafka topic names
        language: system
        entry: nomos-validate --server https://governance.yourcompany.com topic
        files: \.hcl$
        pass_filenames: true
```

```bash
pip install pre-commit
pre-commit install
```

---

## Part 4 — CI pipeline: governance checks on every PR

### Option A — Gherkin suite (checks defined in the governance repo)

Run enforced Gherkin checks against the governance repo content. Put this in the **governance repo's CI**:

```yaml
# .github/workflows/governance.yml
name: Governance checks
on: [pull_request]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install nomos behave
      - run: behave features/ --tags=enforced
        env:
          GOVERNANCE_REPO_PATH: ${{ github.workspace }}
```

### Option B — `nomos-validate` in any repo's CI

Call the shared server from any team's pipeline to validate resources before merge:

```yaml
# .github/workflows/validate.yml  (in a product team's repo)
name: Governance validation
on: [pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install nomos
      - name: Validate topic names
        run: |
          grep -r 'topic_name' . --include='*.hcl' -h | \
            grep -o '"[^"]*"' | tr -d '"' | \
            xargs -I{} nomos-validate --server ${{ vars.NOMOS_SERVER }} topic {}
```

Add `NOMOS_SERVER` as a repository variable in GitHub Settings → Variables.

---

## Part 5 — Team-scoped governance

Teams that need rules specific to their resources — too niche for a domain constitution —
can add a `teams/<name>/` directory to the governance repo. The Nomos server merges
team content on top of domain content when serving the team's endpoint.

### For the platform team: scaffold and CODEOWNERS

```bash
# In the governance repo
nomos scaffold team team-pos
```

Creates `teams/team-pos/constitutions/`, `adrs/`, and `features/` with README templates.

Then add the team to `.github/CODEOWNERS`:

```
teams/team-pos/  @your-org/team-pos
```

The team can now merge changes to their directory without platform team approval.

### For the team: connect your agent

```bash
# In the team's project repo
nomos install-hooks --server https://governance.yourcompany.com --team team-pos
```

This creates `.mcp.json` pointing at `/teams/team-pos/mcp`. Every governance query
from the team's agent returns domain + team rules merged — no extra steps needed.

### What the team endpoint serves

| Query | Response |
|---|---|
| `get_constitution("kafka")` | Domain kafka constitution + team addendum (if exists) |
| `list_adrs()` | Domain ADRs + team ADRs |
| `get_checks("kafka")` | Domain checks + team checks |
| `get_active_rules()` | Always domain `governance.yml` — teams cannot override |

### Automated contradiction check

Any PR that modifies `teams/*/constitutions/*.md` triggers an LLM-based review
that compares the team addendum against the domain constitution and posts findings
in the PR. See [GOVERNANCE-PROCESS.md](GOVERNANCE-PROCESS.md#team-scoped-governance)
for configuration and verdict meanings.

---

## Architecture summary

```
┌─────────────────────────────────────────────────────┐
│  Governance Repository (GitHub)                     │
│  constitution.md · governance.yml · ADRs · features │
└──────────────────────┬──────────────────────────────┘
                       │ push → webhook
                       ▼
              ┌────────────────┐
              │  Nomos Server  │  ← platform team deploys once
              │  :8080         │
              └───────┬────────┘
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
  /mcp endpoint   /validate/*    /webhook/github
       │              │
  AI Agents       nomos-validate
  (.mcp.json)     (pre-commit · CI)
```

One governance repo. One server. Every agent, hook, and pipeline delegates to it.
When a rule changes, the webhook fires, and every consumer sees the update immediately.

---

## Troubleshooting

**`nomos-validate --server URL` returns connection error**

The server is not reachable from the machine running the check. Verify:
- The server is running: `curl https://your-server/health`
- Firewall/VPN allows access from the CI runner or developer machine

**Agent does not pick up governance tools**

Verify `.mcp.json` exists at the project root and the URL is correct:
```bash
curl http://your-server:8080/health
```

**Rules not updating after a push**

The webhook is not configured or is failing. Check the webhook delivery log in GitHub → Settings → Webhooks → Recent Deliveries.

Alternatively, wait for `CACHE_TTL_SECONDS` (default: 5 minutes) for the cache to expire naturally.

**`behave --tags=enforced` fails with "step not implemented"**

A feature file has `@enforced` scenarios but no step definitions. Either add step definitions in `features/steps/` or change `@enforced` to `@wip` until they are ready.
