# ADR-001: URL Structure Convention

**Status:** Accepted
**Date:** 2024-03-10

## Decision

URL paths follow the pattern: `/api/v{N}/{resource}/{id?}/{sub-resource?}`

- Version prefix is mandatory
- Resource names are lowercase plural nouns
- IDs are path parameters, not query parameters

## Rationale

Version prefix in the URL ensures clients pin to a specific contract.
Header-based versioning is invisible in logs, browser bars, and gateway routing.

Plural nouns follow REST conventions (Fielding, 2000). Singular nouns create
inconsistency at collection endpoints (`GET /payment` vs `GET /payments`).

## Alternatives rejected

**Header versioning** (`Accept: application/vnd.api+json;version=2`): invisible
to proxies, harder to test manually.

**Action-based URLs** (`/payments/process`): verbs in URLs signal RPC thinking.
The action is the HTTP method.

## Consequences

URL structure is validated at CI time. Any route that does not match the pattern
blocks merge.
