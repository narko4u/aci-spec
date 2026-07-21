# ACI Examples

Example implementations showing how to structure ACI manifests at each conformance level.

All examples use the fictional **NovaDynamics Inc.** to illustrate progressive adoption, except `empirelabs/` which is a real-world implementation.

---

## Structure

```
examples/
├── minimal/       # Identity only (Level 0 — entry point)
│   ├── llms.txt
│   └── identity.json
├── level1/        # Identity + Capability (Level 1 — Discovery)
│   ├── llms.txt
│   ├── identity.json
│   └── capabilities.json
├── level2/        # Identity + Capability + Knowledge + Trust (Level 2 — Understanding)
│   ├── llms.txt
│   ├── identity.json
│   ├── capabilities.json
│   ├── knowledge.json
│   └── trust.json
├── level3/        # All 5 manifests (Level 3 — Interaction)
│   ├── llms.txt
│   ├── identity.json
│   ├── capabilities.json
│   ├── knowledge.json
│   ├── trust.json
│   └── agents.json
├── level4/        # All 5 manifests + AIP Actions (Level 4 — Governed Interaction)
│   ├── llms.txt
│   ├── identity.json
│   ├── capabilities.json
│   ├── knowledge.json
│   ├── trust.json
│   └── agents.json                   # Also has AJSON versions (*.ajson) with comments & refs
└── empirelabs/    # Real-world implementation by Empire Labs
    └── capabilities.json
```

## Conformance Levels

| Level | Manifests | What It Enables |
|-------|-----------|-----------------|
| **Minimal** | Identity | An agent can discover who you are |
| **Level 1** | Identity + Capability | An agent can find you and understand what you offer |
| **Level 2** | + Knowledge + Trust | An agent can reason about your domain and verify claims |
| **Level 3** | + Agents | An agent can interact with your autonomous systems |
| **Level 4** | + AIP Actions | An agent can execute governed, verifiable actions via AIP contracts |

## Running Validation

To validate any level against the ACI Validator:

```bash
# The validator checks live HTTP servers.
# To test these examples, serve them locally:
cd examples/level4
python3 -m http.server 8000

# Then validate:
python3 ../../validator/validate.py http://localhost:8000
```

## Building Your Own Implementation

1. Start with `minimal/` — publish just an identity manifest
2. Add `capabilities.json` for Level 1
3. Expand with knowledge and trust manifests for Level 2
4. Add agent endpoints for Level 3
5. Add AIP-governed actions in `capabilities.json` for Level 4

> **Tip:** Author your manifests in [AJSON](https://github.com/narko4u/ajson) — a superset of JSON with comments, multi-line strings, and reusable references. Compile to canonical JSON with `pip install ajson-spec && ajson compile manifest.ajson -o manifest.json`.
