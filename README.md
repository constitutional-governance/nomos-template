# nomos-template

> Governance repository template for [Nomos](https://github.com/your-org/nomos) — the [Constitutional Governance](https://github.com/your-org/constitutional-governance) reference implementation.

Fork or use this template to create your organization's governance repository. It contains the structure Nomos expects: a constitution, ADRs, naming conventions, and executable Gherkin checks.

**The server is not here.** This repo is governance content only. Nomos is a separate package:

```bash
pip install nomos
nomos --repo /path/to/this-repo
```

---

## What's in this template

```
nomos-template/
├── governance.yml          ← your platform's rules — the main file to edit
├── constitution.md         ← platform-wide principles
├── constitutions/          ← per-domain constitutions
├── adrs/global/            ← Architecture Decision Records
├── features/               ← Gherkin checks (@enforced runs in CI)
│   └── example/            ← starter example — replace with your domain
└── examples/               ← complete reference implementations
    ├── kafka/              ← full Kafka governance (copy and adapt)
    └── rest-api/           ← REST API governance (copy and adapt)
```

---

## Getting started

```bash
# 1. Use this repo as a GitHub template (click "Use this template")
#    or clone it:
git clone https://github.com/your-org/nomos-template my-governance
cd my-governance

# 2. Install Nomos
pip install nomos

# 3. Edit governance.yml with your platform's conventions

# 4. Start the server
nomos --repo .

# 5. Connect your AI agent (.mcp.json in any project):
# {"mcpServers": {"nomos": {"type": "http", "url": "http://localhost:8080/mcp"}}}
```

---

## Adopting the template

### 1. Edit `governance.yml`

This is the only file that drives validators. Replace the example values with your platform's conventions. Remove sections for domains you don't use.

### 2. Write your constitution

Replace `constitution.md` with your platform's non-negotiable principles. Add per-domain constitutions in `constitutions/<domain>.md`.

### 3. Record architectural decisions

Add ADRs in `adrs/global/`. Use ADR-001 as a template. Every naming convention should have a corresponding ADR explaining why it exists.

### 4. Write executable checks

Add Gherkin feature files in `features/<your-domain>/`. Mark scenarios as `@enforced` when you have step definitions; `@wip` for documented aspirations.

Start from the example in `features/example/` or copy a complete example from `examples/`.

### 5. Run in CI

```yaml
# .github/workflows/governance.yml
- name: Governance checks
  run: |
    pip install nomos behave
    behave features/ --tags=enforced
  env:
    GOVERNANCE_REPO_PATH: ${{ github.workspace }}
```

---

## Deploying a shared instance

The platform team deploys one Nomos instance. All teams point their agents and pre-commit hooks at it.

```bash
# With a GitHub governance repo (recommended for shared deployment)
export GOVERNANCE_REPO_URL=https://github.com/your-org/my-governance
export GITHUB_TOKEN=ghp_...
docker compose up -d   # see docker-compose.yml in the nomos package
```

Teams configure their agents:

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

Pre-commit hooks delegate to the shared server:

```bash
nomos-validate --server https://governance.yourcompany.com topic your.topic.name
```

---

## Reference implementations

See `examples/` for complete governance setups:

| Example | What it shows |
|---|---|
| [`examples/kafka/`](examples/kafka/) | Kafka topic naming, RBAC, service accounts, Camel, SpringBoot, Helm |
| [`examples/rest-api/`](examples/rest-api/) | REST API URL structure, versioning, error format |

Copy the folder for your domain and adapt it. Delete what you don't need.

---

## The delegation model

```
this repo (your governance rules)
        │
        ▼
  nomos --repo .   or   GOVERNANCE_REPO_URL=github.com/your-org/my-governance
        │
  Nomos server (one instance, operated by platform team)
        │
   ┌────┴────────────┐
   ▼                 ▼
AI Agents       CI Pipeline
(MCP tools)   (nomos-validate)
```

One governance repo. One server. Every team, agent, and pipeline delegates to it.

---

*Built on [Constitutional Governance](https://github.com/your-org/constitutional-governance) — the methodology for treating organizational rules as infrastructure.*
