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

Commit this file. Every engineer who clones the project gets governance automatically.

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

In each project repo:

```bash
# .git/hooks/pre-commit
#!/bin/sh
set -e
NOMOS_SERVER="https://governance.yourcompany.com"

# Validate any topic names found in staged HCL files
git diff --cached --name-only | grep '\.hcl$' | while read file; do
  grep -o '"[a-z][a-z0-9.]*\.[a-z][a-z0-9.]*"' "$file" | tr -d '"' | while read name; do
    nomos-validate --server "$NOMOS_SERVER" topic "$name"
  done
done
```

```bash
chmod +x .git/hooks/pre-commit
```

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
