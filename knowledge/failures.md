# AI Failure Patterns — [Platform Name]

Systematic patterns where AI-generated resources violated governance rules on this platform.
Agents query this file before generating any resource via `get_knowledge("failures")`.

Entries are added automatically when violations reach production via `POST /webhook/incident`,
or manually by the platform team after an incident review.

---

<!-- Entry format:
## {Rule name}: {short description of the mistake}

- **Resource**: `{the bad resource name or value}`
- **Bad pattern**: {why it's wrong}
- **Correct pattern**: `{the correct version}`
- **Rule violated**: `{config path}` — {what the rule says}
- **Reported**: {YYYY-MM-DD}
-->

<!-- Add entries below this line -->
