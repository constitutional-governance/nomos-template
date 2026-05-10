# Platform Constitution

> Replace this file with your organization's platform-wide principles.
> Keep it focused — this is the document every engineer and AI agent reads first.

## What this constitution governs

Describe the scope of your platform here. What systems, teams, and resources
fall under this governance?

## Core principles

Replace these with your organization's non-negotiable invariants:

1. **Explicit over implicit** — Every resource name must express intent without
   reading the code. Consumers must understand what a topic, service account,
   or endpoint does from its name alone.

2. **Governance as code** — Every naming rule, RBAC constraint, and architectural
   decision lives in this repository. ADRs are the audit trail for every decision.

3. **AI-assisted, human-approved** — Agents use this governance server to propose
   correct configurations. A human reviews and approves every change.

## Domain constitutions

| Domain | File |
|---|---|
| Global | this file |

Add rows as you define new domain constitutions in `constitutions/`.

## ADR index

See `adrs/global/` for Architecture Decision Records.
