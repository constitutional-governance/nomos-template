# Successful Patterns — Kafka Platform

Approaches and patterns that have worked well. Use as reference when generating resources.

---

## Topic naming: full 7-segment hierarchy

```
env.domain.subdomain.team.entity.event.version

raw.payments.pos.acme.checkout.receipt.v1   ✓
dev.logistics.wms.globus.shipment.created.v2 ✓
```

The hierarchy makes topics self-documenting and consistent across every domain.

---

## Service account naming: role + env suffix

```
sa-{team}-{role}-{env}
sa-{team}-connector-{direction}-{connector-type}-{env}

sa-payments-producer-prod              ✓
sa-payments-consumer-prod              ✓
sa-payments-connector-source-jdbc-prod ✓
sa-logistics-connector-sink-s3-dev     ✓
```

Embedding the role and environment makes RBAC audits fast: the name alone reveals what it does and where it runs.

---

## RBAC: minimal privilege bindings

```
DeveloperRead  / Topic   / raw.payments.pos.acme.*     ✓ consumer
DeveloperWrite / Topic   / raw.payments.pos.acme.checkout.receipt.v1  ✓ producer
DeveloperManage / Cluster / kafka-cluster               ✓ ops only
```

---

## Schema: BACKWARD compatibility by default

```
AVRO / BACKWARD            ✓ safe default
AVRO / FULL_TRANSITIVE     ✓ for public contracts shared across many teams
```

---

## Canary rollout: validate new rules against one team first

```yaml
kafka:
  topic:
    rollout:
      phase: canary
      teams: [team-a]
```

Non-canary teams receive warnings instead of errors. Promote to `phase: stable` once adopted.
