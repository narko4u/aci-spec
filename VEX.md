# VEX — Vulnerability Exploitability eXchange

Status: current as of draft-v0.9 (2026-08-18). Reviewed before each release.

This document states the exploitability status of known vulnerabilities in
the software components of this project, per the OSPS VM-04.02 control.
"Not affected" means the vulnerable component is present in the supply chain
but the vulnerable code path cannot be reached or does not affect the
shipped artifact.

## Component inventory

| Component | Type | Version | Runtime? |
|-----------|------|---------|----------|
| ACI specification (SPEC.md, schemas) | Specification | draft-v0.9 | Yes (normative) |
| `validator/validate.py` | Shipped script | 0.9.0 | Yes |
| PyYAML | Runtime dep | pinned in validator requirements | Yes |
| Python standard library | Runtime | 3.9+ | Yes |
| pytest | Test-only | pinned in CI | No |
| GitHub Actions (docker-publish) | CI-only | pinned by SHA | No |

## Statements

| Component | Vulnerability | Status | Justification |
|-----------|---------------|--------|---------------|
| ACI specification | (any) | Not affected | A text specification; it does not execute. Security properties are expressed in SPEC.md section on security |
| `validator/validate.py` | (any) | Not affected | Validation-only script that performs read-only HTTP GETs against a user-supplied agent base URL; it stores no credentials, opens no listeners, and writes nothing to the target |
| PyYAML | (any) | Under assessment | Assessed at release time against reachable code paths (schema YAML loading only) |
| Test/build/CI components | (any) | Not affected | Not shipped to end users; only ever run in ephemeral CI on trusted inputs |

## Change policy

- This VEX is updated whenever a new component is added, a vulnerability is
  reported, or a release is prepared.
- New releases must not ship while a High or Medium severity finding in a
  reachable component is unresolved (see `SECURITY.md` remediation
  thresholds).
