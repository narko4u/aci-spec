# ACI Examples

Example implementations showing how to structure ACI manifests at each conformance level.

All examples use the fictional **NovaDynamics Inc.** to illustrate progressive adoption.

---

## Structure

```
examples/
├── minimal/     # Identity only (Level 0 — entry point)
│   ├── llms.txt
│   └── identity.json
├── level1/      # Identity + Capability (Level 1 — Discovery)
│   ├── llms.txt
│   ├── identity.json
│   └── capabilities.json
├── level2/      # Identity + Capability + Knowledge + Trust (Level 2 — Understanding)
│   ├── llms.txt
│   ├── identity.json
│   ├── capabilities.json
│   ├── knowledge.json
│   └── trust.json
└── level3/      # All 5 manifests (Level 3 — Interaction)
    ├── llms.txt
    ├── identity.json
    ├── capabilities.json
    ├── knowledge.json
    ├── trust.json
    └── agents.json
```

## Conformance Levels

| Level | Manifests | What It Enables |
|-------|-----------|-----------------|
| **Minimal** | Identity | An agent can discover who you are |
| **Level 1** | Identity + Capability | An agent can find you and understand what you offer |
| **Level 2** | + Knowledge + Trust | An agent can reason about your domain and verify claims |
| **Level 3** | + Agents | An agent can interact with your autonomous systems |

## Running Validation

To validate any level against the ACI Validator:

```bash
# The validator checks live HTTP servers.
# To test these examples, serve them locally:
cd examples/level3
python3 -m http.server 8000

# Then validate:
python3 ../../validator/validate.py http://localhost:8000
```

## Building Your Own Implementation

1. Start with `minimal/` — publish just an identity manifest
2. Add `capabilities.json` for Level 1
3. Expand with knowledge and trust manifests for Level 2
4. Add agent endpoints for Level 3
