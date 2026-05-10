# Team Gherkin checks for `example-team`

Team-specific executable checks. Organise by domain, mirroring `features/`:

```
features/
└── example-team/
    └── features/
        └── kafka/
            └── example-team-topic-naming.feature
```

## Rules

- Start all new scenarios as `@wip`.
- Promote to `@enforced` with: `nomos check-promotion features/... --run`
- Domain `@enforced` checks always run — your checks add on top, never replace.
- Step definitions go in the root `features/steps/` directory.

## Connecting

Team agents query these checks automatically via the team-scoped endpoint:

```json
{ "mcpServers": { "nomos": { "url": "https://governance.acme.com/teams/example-team/mcp" } } }
```

Or install in one command:

```bash
nomos install-hooks --server https://governance.acme.com --team example-team
```
