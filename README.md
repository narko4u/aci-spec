# Autonomous Company Interface (ACI)

**Status:** Draft Specification v0.9 (seeking independent implementations and feedback)

An open specification for describing organizations to autonomous agents through structured, machine-readable contracts.

ACI enables autonomous systems to:

- **Discover** organizations and what they do
- **Understand** capabilities and domain knowledge
- **Verify** identity and claims through attestations
- **Locate** autonomous agents and interaction endpoints
- **Interact** through open, governed contracts

---

## Quick Start

```bash
# Validate an ACI implementation
python3 validator/validate.py https://example.com

# Example output:
#   Conformance: ACI Level 3
#   Overall: 95/100 — FULL COMPLIANCE
```

## Contents

- [SPEC.md](./SPEC.md) — The specification
- [schema/](./schema/) — Machine-readable YAML schemas for all five manifest types
- [validator/](./validator/) — Open-source ACI Validator CLI
- [examples/](./examples/) — Example implementations across all conformance levels

---

**Reference implementation:** [Empire Labs](https://empirelabs.com.au)

**License:** CC BY 4.0 (specification) / MIT (validator, schemas, examples)
