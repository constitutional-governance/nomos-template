# Governance process

This document defines how the governance repository itself is governed — who owns what,
how changes are proposed and approved, and how conflicts are resolved.

Without these rules, the governance repo becomes a bottleneck: PRs accumulate,
nobody knows who can approve what, and teams stop proposing improvements.

---

## Domain ownership

Each domain in the governance repo has one or more **domain owners**. A domain owner
is a person or team responsible for reviewing and approving changes to that domain's
constitutions, ADRs, and Gherkin checks.

Update this table when adding a new domain:

| Domain | Owner | Notes |
|---|---|---|
| `global` | Platform team | Cross-cutting rules — broad consensus required |
| `kafka` | TODO: team or person | Kafka topics, RBAC, service accounts |
| `camel` | TODO: team or person | Camel integration routes |
| `springboot` | TODO: team or person | Spring Boot application config |

**Ownership does not mean exclusivity.** Any team can propose changes to any domain.
Ownership means accountability for review and final approval.

---

## Proposing a change

Anyone can propose a governance change by opening a pull request on this repository.

### What the PR must contain

| Change type | Required in PR |
|---|---|
| New naming rule | ADR + updated `governance.yml` (if validator-driven) + `@wip` Gherkin scenario |
| Amendment to existing rule | Updated ADR (mark old decision as superseded) + updated `governance.yml` if needed |
| New `@enforced` check | Gherkin scenario + step definitions + passing `behave` run |
| Domain constitution change | Updated `constitutions/<domain>.md` + rationale in PR description |
| New domain | Constitution + at least one ADR + `governance.yml` entry if applicable |

### PR description template

```markdown
## What this changes
<!-- One sentence -->

## Why
<!-- The constraint, incident, or decision that drives this -->

## Domains affected
<!-- List the domains whose teams should review this -->

## Breaking change?
<!-- Yes/No. If yes: what existing resources will no longer comply? -->

## Migration path
<!-- If breaking: what do teams need to do? By when? -->
```

---

## Review process

### Who reviews what

- **Domain owner** reviews any change to their domain
- **Platform team** reviews any change to `global` or to `governance.yml`
- **Any affected team** can comment — especially when a change is breaking

Tag the domain owner when opening the PR. If you don't know who owns a domain,
tag the platform team.

### Review window

| Change type | Minimum review window |
|---|---|
| Non-breaking (new rule, new domain) | 3 business days |
| Breaking (rule amendment, prefix removal) | 5 business days |
| Emergency (production incident) | Same-day — see below |

A PR may not be merged before the minimum review window expires, even if everyone
has approved. This gives affected teams time to notice and raise concerns.

### Approval requirements

| Change type | Required approvals |
|---|---|
| `governance.yml` validator change | Platform team + domain owner |
| `@wip → @enforced` promotion | Domain owner |
| ADR amendment | Domain owner + 1 additional reviewer |
| New domain | Platform team |
| Constitution change | Platform team + domain owner |

---

## Breaking changes

A change is **breaking** if existing resources that were previously valid will no longer
pass validation after the change is merged.

Breaking changes require:

1. **Migration path documented in the ADR** — what teams need to do and by when
2. **Grace period** — `@enforced` check for the new rule is added with a `@wip` tag for
   at least one sprint; teams have time to migrate before CI starts blocking
3. **Announcement** — platform team posts in the team communication channel
   (Slack, Teams, email list — define yours here: TODO)
4. **CHANGELOG entry** — see [CHANGELOG.md](CHANGELOG.md)

### Grace period flow for breaking changes

```
PR merged (breaking rule change)
        │
        ▼
New rule is @wip — agents see it, CI does not enforce it yet
        │
        ▼  (grace period: typically 1–2 sprints)
Teams migrate existing resources
        │
        ▼
@wip → @enforced promotion PR
        │
        ▼
CI now enforces the new rule
```

---

## The `@wip → @enforced` promotion path

A `@wip` scenario is a documented aspiration. An `@enforced` scenario is a CI gate.
Promoting from one to the other is a deliberate step — not automatic.

### Steps to promote a scenario

1. **Write step definitions** in `features/steps/`. See `features/steps/README.md`.
   The proposing team can do this, or the platform team — agree in the PR.

2. **Run locally and confirm it passes**
   ```bash
   nomos check-promotion features/<domain>/<scenario>.feature --run
   ```
   This verifies step definitions exist and runs the full scenario suite.
   Include the output in the PR description.

3. **Open a promotion PR**
   - Change `@wip` to `@enforced` in the feature file
   - Include the `nomos check-promotion` output in the PR description

4. **Domain owner approves** — one approval is sufficient for a promotion-only PR
   (no new rule is being introduced, only enforcement is being activated)

5. **Merged** — CI now runs this scenario on every PR in repos that use it

### Who writes the step definitions?

By default, **the team that proposed the `@wip` scenario** is responsible for writing
the step definitions. If they need help, they can request it in the PR.

The platform team is responsible for maintaining the step definitions in
`examples/kafka/features/steps/` as a reference implementation.

---

## Conflict resolution

When two proposals are in conflict (e.g., Team A proposes prefix `orders` and
Team B proposes prefix `order` for different semantics):

1. Both teams explain their requirements in the PR comments
2. The domain owner proposes a resolution
3. If no resolution is found within the review window, the **platform team decides**
4. The losing proposal may be re-opened with a different approach

The platform team's decision is final, but the rationale must be documented in the ADR.

---

## Emergency changes

For production incidents where a governance rule is blocking a fix:

1. Open a PR marked `[EMERGENCY]` in the title
2. Tag the platform team lead directly (define who: TODO)
3. The emergency process bypasses minimum review windows
4. A post-incident ADR must document what was changed and why within 3 business days

Emergency PRs that are merged without full review must be reviewed retrospectively.
If the change was wrong, it will be reverted or amended.

---

## Governance health checks

The platform team reviews the governance repo quarterly:

- Are all domain owners still active?
- Are there open PRs older than 30 days? Why?
- Are there `@wip` scenarios older than 90 days with no promotion plan?
- Is the CHANGELOG up to date?

Stale `@wip` scenarios (no progress in 90 days) are either promoted or removed.
A `@wip` scenario that nobody is working on is noise, not governance.
