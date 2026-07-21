# Autonomous Company Interface (ACI)

**Status:** Draft Specification v0.9

> **Seeking three independent implementations for ACI v1.0** — [Track progress](https://github.com/narko4u/aci-spec/issues/6)

An open specification for describing organizations to autonomous agents through structured, machine-readable contracts.

ACI enables autonomous systems to:

- **Discover** organizations and what they do
- **Understand** capabilities and domain knowledge
- **Verify** identity and claims through attestations
- **Locate** autonomous agents and interaction endpoints
- **Interact** through open, governed contracts

---

## Get started in 5 minutes

**Option A — Fork the template:**

[![Use this template](https://img.shields.io/badge/Fork%20the-template-blue)](https://github.com/narko4u/aci-pages-template/generate)

Replace the placeholders with your organization details and deploy to GitHub Pages. No build tools required.

**Option B — Run the Explorer:**

```bash
# Zero-dependency discovery — see what an ACI-compatible organization exposes
python3 demo/aci-explorer.py empirelabs.com.au
```

**Option C — Validate a deployment:**

```bash
python3 validator/validate.py https://your-org.github.io/your-site
```

---

## Contents

- [SPEC.md](./SPEC.md) — The specification
- [schema/](./schema/) — Machine-readable YAML schemas for all five manifest types
- [validator/](./validator/) — Open-source ACI Validator CLI
- [examples/](./examples/) — Example implementations (JSON + AJSON authoring format)
- [demo/aci-explorer.py](./demo/aci-explorer.py) — Zero-dependency CLI discovery tool
- [AJSON](https://github.com/narko4u/ajson) — Manifest authoring format with comments, refs, and canonical compilation

---

## Quick reference

| Resource | Link |
|----------|------|
| Specification | [SPEC.md](./SPEC.md) |
| Schema (YAML) | [schema/](./schema/) |
| Validator | [validator/validate.py](./validator/validate.py) |
| Explorer | [demo/aci-explorer.py](./demo/aci-explorer.py) |
| Example implementations | [examples/](./examples/) |
| Deployment template | [narko4u/aci-pages-template](https://github.com/narko4u/aci-pages-template) |
| Live implementation | [empirelabs.com.au](https://empirelabs.com.au) |

---

## 🍻 Buy the Empire a Pint

If ACI helps your agents discover and trust organizations, buy the Empire a pint. We like to split the G.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/empirelabs)

**Pay what you want.** No tiers, no strings. Every donation helps keep this specification sovereign and open.

---

## License

**CC BY 4.0** (specification) / **MIT** (validator, schemas, examples, explorer)

*Built by Empire Labs Pty Ltd | Maintained by **Sovereign** (Autonomous Agent)*
