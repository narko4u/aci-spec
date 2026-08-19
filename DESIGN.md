# Design: aci-spec

This document describes the design of the Autonomous Company Interface (ACI)
project: the actors, the actions they perform, and the data flow through the
specification, validator, and explorer. It accompanies
[THREAT-ASSESSMENT.md](THREAT-ASSESSMENT.md) (threat model) and
[TESTING.md](TESTING.md) (test policy).

## Purpose

ACI is a specification that lets autonomous agents discover, understand,
verify, and interact with organizations through open, structured contracts.
This repository hosts the specification itself plus a reference validator and
explorer.

## Actors

| Actor | Description |
| --- | --- |
| **Organization** | An entity that publishes ACI manifests (identity, capability, knowledge, trust, agents) at a known endpoint (e.g. `/.well-known/aci.json` or GitHub Pages). |
| **Autonomous agent** | A software agent that discovers and reads an organization's ACI manifests to decide whether and how to interact. |
| **Validator operator** | A user running the `aci-validate` CLI or `validator/validate.py` to check that an ACI deployment conforms to the specification. |
| **Explorer operator** | A user running the `aci-explore` CLI or `demo/aci-explorer.py` to discover what an ACI-compatible organization exposes. |
| **Specification steward** | Maintains SPEC.md, the schema, and the change process (see CHANGE_PROCESS.md). |

## Actions

| Action | Performed by | Implemented in |
| --- | --- | --- |
| Discover organization manifests | Agent / Explorer operator | `demo/aci-explorer.py` |
| Load and validate manifests | Validator operator | `validator/validate.py`, `aci_validator/` |
| Validate against schemas | Validator operator | `schema/*.yaml`, `aci_validator/validate.py` |
| Parse example manifests | (CI / tests) | `examples/**/*.json` |
| Author manifests (AJSON) | Organization | [ajson](https://github.com/narko4u/ajson) |

## Data flow

```
organization endpoint (e.g. https://org.example/.well-known/aci.json)
        │
        ▼
aci-explore ──► discover manifests (identity, capability, knowledge, trust, agents)
        │
        ▼
aci-validate ──► load schemas (schema/*.yaml)
        │            │
        │            ▼
        │      validate each manifest against its schema
        │            │
        │            ▼
        ▼      conformance report (pass/fail per manifest)
  deployment assessment
```

## Design invariants

1. **Open by construction.** The specification and schemas are machine
   readable and freely licensed; two independent implementations must be able
   to reach substantially the same understanding without prior bilateral
   agreement.
2. **Zero-friction validation.** The validator and explorer are designed to
   run with no external dependencies (Python stdlib only), so any agent or
   operator can validate a deployment without installing a toolchain.
3. **Schema-driven.** All manifest types are defined by YAML schemas in
   `schema/`; the validator loads the schemas and the manifest order from
   `aci_validator/validate.py`.
4. **Explicit change process.** Specification changes follow CHANGE_PROCESS.md
   (RFCs for breaking changes), keeping the spec stable for implementers.
