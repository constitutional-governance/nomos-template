# Constitution addenda for `example-team`

Each `.md` file here is appended to the corresponding domain constitution when
the Nomos server is queried in the `example-team` team context.

| File | Appended to |
|---|---|
| `kafka.md` | `constitutions/kafka.md` |
| `camel.md` | `constitutions/camel.md` |
| `global.md` | `constitution.md` |

## Rules

- **Only add constraints.** Do not relax or contradict domain rules.
- If a rule should apply to all teams, propose it to the domain constitution via PR.
- The server always serves the domain constitution first; your addendum follows.

## Example

```markdown
# example-team Kafka addendum

## Team-specific constraints

All topics owned by this team must include the segment `.example.` in position 3
of the topic name. This identifies resources in our subdomain and prevents naming
collisions with other teams.
```
