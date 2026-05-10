# Changelog

This file records all governance rule changes — new rules, amendments, removals, and promotions from `@wip` to `@enforced`.

**Audience:** product teams consuming governance rules.
**Maintained by:** the platform team. Update this file in every PR that changes `governance.yml`, a constitution, or an ADR.

---

## How to read this file

Each entry answers four questions a team member needs:

1. **What changed?** — the rule or check affected
2. **Why?** — the ADR or incident that drove the change
3. **Breaking?** — will my existing resources stop passing validation?
4. **What do I do?** — if breaking: what to change and by when

Non-breaking changes (new rules, new `@enforced` checks for new resources) require no action from existing teams.

---

## Format

```markdown
## [YYYY-MM-DD] Short description of change

**Type:** New rule | Rule amendment | Rule removal | @wip → @enforced promotion | New domain
**Domain:** global | kafka | camel | springboot | ...
**ADR:** [ADR-NNN](adrs/global/NNN-title.md) | N/A
**Breaking:** Yes | No

### What changed
One or two sentences. What is now valid or invalid that wasn't before (or vice versa).

### Why
The constraint, incident, or decision that drove this.

### Migration path *(only for breaking changes)*
What teams need to do. By when.
```

---

## Entries

<!-- Most recent entry first -->

## [YYYY-MM-DD] Template entry — replace with your first real change

**Type:** New rule
**Domain:** global
**ADR:** [ADR-001](adrs/global/001-resource-naming.md)
**Breaking:** No

### What changed
All resources must follow the naming convention defined in ADR-001.

### Why
This is the initial governance baseline for this repository.

---

<!-- Add new entries above this line, most recent first -->
