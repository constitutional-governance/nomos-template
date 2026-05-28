# AI Failure Patterns — Kafka Platform

Systematic patterns where AI-generated resources violated governance rules.
Review these before generating any Kafka resource.

Entries are added automatically via `POST /webhook/incident` when violations
reach production. Each entry is reviewed and merged by the platform team.

---

## Topic naming: wrong segment count

- **Resource**: `raw.payments.pos.checkout.v1`
- **Bad pattern**: 5 segments — missing domain and team
- **Correct pattern**: `raw.payments.pos.acme.checkout.receipt.v1` (7 segments: env.domain.subdomain.team.entity.event.version)
- **Rule violated**: `kafka.topic` — `segment_count = 7`
- **Reported**: 2026-03-12

---

## Topic naming: invalid environment prefix

- **Resource**: `test.payments.pos.acme.checkout.receipt.v1`
- **Bad pattern**: `test` prefix — not in the declared prefix list
- **Correct pattern**: `dev.payments.pos.acme.checkout.receipt.v1`
- **Rule violated**: `kafka.topic` — `prefixes`
- **Reported**: 2026-03-18

---

## Service account naming: missing connector direction

- **Resource**: `sa-payments-connector-jdbc-prod`
- **Bad pattern**: connector SA without `source` or `sink` direction segment
- **Correct pattern**: `sa-payments-connector-source-jdbc-prod`
- **Rule violated**: `kafka.service_account` — connector SAs require `source` or `sink`
- **Reported**: 2026-03-25

---

## RBAC: admin role applied to topic resource

- **Resource**: `DeveloperManage / Topic / raw.payments.pos.acme.checkout.receipt.v1`
- **Bad pattern**: admin role `DeveloperManage` on a topic — admin roles are reserved for cluster-level
- **Correct pattern**: `DeveloperWrite / Topic / raw.payments.pos.acme.checkout.receipt.v1`
- **Rule violated**: `kafka.rbac` — `admin_roles` may only bind to `admin_resource_types`
- **Reported**: 2026-04-22
