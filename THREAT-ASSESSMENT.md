# Security Assessment

Status: assessment performed for the draft-v0.9 release (2026-08-18). This
document records the most likely and impactful potential security problems
for this project and the mitigations in place. It is reviewed before each
release.

## What this project is

The ACI (Autonomous Company Interface) open specification plus a
validation script. The specification defines how agent-driven companies
advertise themselves and their capabilities. The validator performs
read-only HTTP GETs against a user-supplied agent base URL and checks the
response against the ACI schemas.

## Assets

1. **Specification integrity** — the normative text and schemas must not
   silently change (trust anchor for implementations).
2. **Validator correctness** — the validator must not be tricked into
   declaring a non-conforming agent as conforming.
3. **No foothold from validation** — validating an untrusted agent must not
   compromise the validator host.

## Likely and impactful problems

| # | Problem | Likelihood | Impact | Mitigation |
|---|---------|------------|--------|------------|
| 1 | Malicious agent serving crafted JSON to exploit parser bugs | Medium | Medium (validator host compromise) | Schemas validated with PyYAML safe loading patterns; validator performs read-only GETs only; output is local |
| 2 | SSRF-style abuse via crafted base URLs | Medium | Medium | Validator is user-invoked against a URL the user chooses; it performs GETs only and never tunnels credentials |
| 3 | Specification ambiguity leading to divergent implementations | Medium | High (ecosystem trust) | Schemas are machine-readable; conformance levels 1-3 defined in SPEC.md; validator enforces them |
| 4 | Typosquatting / impersonation of companies in the ACI directory | Medium | Medium | Deployment template and live directory use verified organization claims; registry verification is in scope for the WitnessOS evidence layer |
| 5 | Dependency supply-chain risk | Low | Low | Minimal dependencies (PyYAML only); CI installs from pinned source |

## Threat model scope

- **In scope:** specification semantics, schema validation, validator input
  handling.
- **Explicitly out of scope:** transport security of the agent's HTTP
  endpoint (implementer's responsibility), identity issuance and
  delegated authorization (AAIF Identity & Trust WG domain).

## Attack surface analysis

- `validator/validate.py` — HTTP GET, schema loading, conformance checks.
- `schema/*.yaml` — parsing and structural validation.
- SPEC.md normative text — interpretation by implementers.
