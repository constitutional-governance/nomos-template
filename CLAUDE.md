# nomos-template

Governance repository template for [Nomos](../govern-mcp). This repo is **content only** — constitutions, ADRs, naming conventions, and Gherkin checks. No application code.

**Read README.md for structure overview. Read FOR-TEAMS.md for the day-to-day workflow.**

---

## Structure

```
nomos-template/
├── governance.yml          ← validation rules (prefixes, roles, SA envs, schema formats)
├── constitution.md         ← platform-wide principles
├── constitutions/          ← per-domain principles (one .md per domain)
├── adrs/global/            ← Architecture Decision Records (NNN-title.md)
├── knowledge/
│   ├── failures.md         ← platform-specific AI failure patterns (queryable via MCP)
│   └── successful.md       ← patterns that have worked well
├── features/               ← Gherkin checks (@enforced = CI, @wip = in progress)
│   └── steps/              ← step definitions
└── teams/                  ← team-scoped addenda (extend, never override)
```

## Patterns in use

**Layered Configuration Context** — four layers: Constitution → ADRs → Validators (governance.yml) → Gherkin. Each layer constrains the one below. Changes to a lower layer must be consistent with the layers above.

**Memory Synthesis from Execution Logs** — `knowledge/failures.md` is the failures catalog: platform-specific AI mistakes, each with bad pattern, correct pattern, and enforcement mechanism. It is fed to agents before generation via `get_knowledge("failures")`.

**Incident-to-Eval Synthesis** — roadmap target: violations caught in CI feed back into `knowledge/failures.md` automatically. When adding new entries manually, follow the existing structure so they're machine-parseable when automation arrives.

**Spec-As-Test Feedback Loop** — every rule that matters has a Gherkin scenario. `@enforced` tags gate CI. `@wip` tags are in progress. Never remove a `@wip` scenario — fix the step definition instead.

## Conventions

- ADRs are numbered sequentially (`NNN-title.md`) and never deleted — superseded ADRs get an `## Amendment` section
- `governance.yml` is the source of truth for all validators; if you change a rule, update the yml first, then the Gherkin
- Gherkin scenarios are written in plain English understandable by non-engineers
- Team addenda in `teams/<name>/` can extend domain rules but must not contradict them
- `knowledge/failures.md` entries include: pattern name, bad example, correct example, enforcement mechanism

## Testing changes

```bash
# Start the server pointed at this repo
pip install nomos
nomos --repo .

# Run Gherkin checks
GOVERNANCE_REPO_PATH=. behave --tags=enforced

# Validate a specific resource
nomos-validate topic raw.payments.pos.checkout.receipts.transaction.v1
```

## Related repos

- [govern-mcp](../govern-mcp) — the server that reads this repo
- [constitutional-governance](../constitutional-governance) — methodology docs and principles
