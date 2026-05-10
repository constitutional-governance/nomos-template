# nomos-template

> Governance repository template for [Nomos](https://github.com/your-org/nomos) — the [Constitutional Governance](https://github.com/your-org/constitutional-governance) reference implementation.

This repo is **governance content only** — constitutions, ADRs, naming conventions, and executable Gherkin checks. The server is a separate package:

```bash
pip install nomos
nomos --repo .
```

| Document | Audience |
|---|---|
| This file | Everyone — quick start and structure overview |
| [FOR-TEAMS.md](FOR-TEAMS.md) | Product teams — day-to-day workflow, synergies, proposing rules |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Platform team — shared server setup, webhook, pre-commit, CI |
| [GOVERNANCE-PROCESS.md](GOVERNANCE-PROCESS.md) | Platform team — how to propose, review, and approve governance changes |
| [CHANGELOG.md](CHANGELOG.md) | Everyone — history of rule changes and migration notes |

---

## Five-minute start

```bash
# 1. Clone or use this repo as a GitHub template
git clone https://github.com/your-org/nomos-template my-governance
cd my-governance

# 2. Install Nomos
pip install nomos

# 3. Start the server — it reads this repo as-is
nomos --repo .
# → listening on http://127.0.0.1:8080

# 4. Connect Claude Code (or any MCP-compatible agent)
# In your project repo (not this governance repo):
nomos install-hooks --server http://127.0.0.1:8080
```

The server works immediately with the template content. Customize it to make it yours.

---

## What's here and what to do with it

```
nomos-template/
├── governance.yml          ← EDIT: your platform's validation rules
├── constitution.md         ← EDIT: your platform-wide principles
├── constitutions/
│   └── example.md          ← RENAME + EDIT: one file per domain
├── adrs/global/
│   └── 001-resource-naming.md  ← REPLACE: your first architectural decision
├── features/
│   ├── example/
│   │   └── resource-naming.feature  ← REPLACE: your first Gherkin check
│   └── steps/
│       └── README.md       ← READ: how to write step definitions
├── teams/                  ← OPTIONAL: team-scoped governance addenda
│   └── example-team/       ← one directory per team (see GOVERNANCE-PROCESS.md)
│       ├── constitutions/  ← domain constitution addenda (appended by Nomos)
│       ├── adrs/           ← team-scoped architectural decisions
│       └── features/       ← team-specific @enforced checks
└── examples/               ← REFERENCE: copy and adapt, do not edit directly
    ├── kafka/              ← complete Kafka platform governance
    └── rest-api/           ← complete REST API governance
```

**The short version:** edit the files at the root level. Use `examples/` as reference. Delete placeholder files once you've replaced them. Add `teams/<name>/` when a team needs rules that are too specific for a domain constitution.

---

## Adopting the template step by step

### Step 1 — Edit `governance.yml`

This file drives the built-in validators (`validate_topic_name`, `validate_rbac_binding`, `validate_sa_name`).

Uncomment the sections for the platforms you use. Remove sections you don't need. If you don't use Kafka, the file can be minimal:

```yaml
project:
  name: "Acme Platform Governance"
  description: "Governance for the Acme engineering platform"
```

See `examples/kafka/governance.yml` for a complete Kafka configuration.

### Step 2 — Write your constitution

Replace `constitution.md` with your platform's non-negotiable principles — the rules that apply everywhere, regardless of team or domain.

For each domain, scaffold the required files in one command:

```bash
nomos scaffold domain kafka
# Creates:
#   constitutions/kafka.md
#   adrs/kafka/001-resource-naming.md
#   features/kafka/kafka-conventions.feature  (@wip)
```

Then edit the generated files — each contains a template with TODO markers.

**Or manually:**

```bash
cp constitutions/example.md constitutions/kafka.md
# Edit constitutions/kafka.md
rm constitutions/example.md
```

### Step 3 — Record your first ADR

`nomos scaffold domain` creates a first ADR template at `adrs/<domain>/001-resource-naming.md`. Fill it in:

```markdown
# ADR-001: Topic Naming Convention

**Status:** Accepted
**Date:** 2024-01-15

## Decision
...

## Rationale
...

## Alternatives rejected
...

## Consequences
...
```

Every naming convention should have an ADR explaining why it exists.

### Step 4 — Write your first executable check

`nomos scaffold domain` creates a `@wip` feature file at `features/<domain>/<domain>-conventions.feature`. Edit the scenarios, add step definitions in `features/steps/`, then verify:

```bash
nomos check-promotion features/kafka/kafka-conventions.feature --run
```

When it passes, change `@wip` to `@enforced` and open a promotion PR.

Write step definitions in `features/steps/`:

```python
# features/steps/kafka_steps.py
from behave import given, when, then
from nomos.validators.topic import validate_topic_name  # if using built-in validators

@given('the topic name "{name}"')
def step_topic_name(context, name):
    context.name = name

@when("I validate the topic name")
def step_validate(context):
    # use built-in validator or your own
    context.result = validate_topic_name(name, config.kafka.topic)

@then("it should be valid")
def step_valid(context):
    assert context.result.valid, context.result.errors
```

See `examples/kafka/features/steps/validation_steps.py` for a complete working example.

Mark a scenario `@enforced` only when its step definitions exist and pass locally. `@wip` documents aspirations.

### Step 5 — Run checks locally

```bash
pip install behave

# Run only enforced checks (what CI runs)
GOVERNANCE_REPO_PATH=. behave features/ --tags=enforced

# Run everything including wip (local exploration)
GOVERNANCE_REPO_PATH=. behave features/ --no-skipped
```

### Step 6 — Add CI

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

---

## Deploying a shared server (the delegation model)

The platform team deploys **one** Nomos instance. Every team, agent, and pipeline delegates to it — nobody runs their own copy.

```bash
# Quick start — GitHub mode
export GOVERNANCE_REPO_URL=https://github.com/your-org/my-governance
export GITHUB_TOKEN=ghp_...
docker compose up -d
```

```bash
# Verify
curl http://your-server:8080/health
# → {"status": "ok"}
```

Teams connect their agents by adding `.mcp.json` to each project repo:

```json
{
  "mcpServers": {
    "nomos": {
      "type": "http",
      "url": "https://governance.yourcompany.com/mcp"
    }
  }
}
```

→ **Full setup guide: [DEPLOYMENT.md](DEPLOYMENT.md)**

Covers: platform deployment (process or Docker), GitHub webhook for live rule propagation, per-team agent configuration, pre-commit hooks, and CI integration.

---

## Reference implementations

Working governance setups you can copy and adapt:

| Example | Domains covered | Status |
|---|---|---|
| [`examples/kafka/`](examples/kafka/) | Kafka topics, RBAC, service accounts, Camel, SpringBoot, Helm | Validators + Gherkin |
| [`examples/rest-api/`](examples/rest-api/) | URL structure, versioning, error format | Gherkin only |

To use an example as your starting point:

```bash
# Use the Kafka example directly
nomos --repo examples/kafka

# Or copy it and customize
cp -r examples/kafka /path/to/my-governance
nomos --repo /path/to/my-governance
```

---

## Repository structure Nomos expects

```
your-governance-repo/
├── governance.yml          ← required: drives validators
├── constitution.md         ← optional: global principles
├── constitutions/
│   └── <domain>.md         ← optional: per-domain principles
├── adrs/
│   └── global/
│       └── NNN-title.md    ← optional: architectural decisions
└── features/
    ├── <domain>/
    │   └── *.feature       ← optional: Gherkin checks
    └── steps/
        └── *_steps.py      ← required if features/ has @enforced scenarios
```

Only `governance.yml` is strictly required. Everything else is optional but recommended.

---

*Built on [Constitutional Governance](https://github.com/your-org/constitutional-governance) — the methodology for treating organizational rules as infrastructure.*
