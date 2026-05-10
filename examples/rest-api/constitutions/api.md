# REST API Constitution

## Purpose

APIs are the public contracts of this platform. They are consumed by internal
teams, external partners, and AI agents. A contract that changes without notice
breaks consumers. A contract that is inconsistent across teams creates friction.

## Non-negotiable invariants

1. **APIs are versioned at the URL level.** `/v1/` and `/v2/` may coexist.
   `/v2/` does not replace `/v1/` without a deprecation period.

2. **Error responses follow RFC 9457 Problem Details.** Any client that handles
   errors from one API can handle errors from any API.

3. **Resource names are nouns, not verbs.** Actions are HTTP methods.
   `/payments` not `/getPayments`. `/payments/{id}/cancel` not `/cancelPayment`.

4. **Pagination is cursor-based for unbounded collections.** Offset pagination
   is prohibited for collections that may grow without bound.
