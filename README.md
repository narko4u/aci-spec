# Autonomous Company Interface (ACI)

**Status:** Draft Specification v0.9

[![PyPI version](https://img.shields.io/pypi/v/aci-spec?color=blue)](https://pypi.org/project/aci-spec/)
[![PyPI downloads](https://img.shields.io/pypi/dm/aci-spec)](https://pypi.org/project/aci-spec/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/spec-CC%20BY%204.0-lightgrey)](LICENSE-CC-BY-4.0)

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

**Option A — Install from PyPI (recommended):**

```bash
pip install aci-spec
```

Then validate any ACI deployment:

```bash
aci-validate empirelabs.com.au
aci-explore empirelabs.com.au
```

**Option B — Fork the template:**

[![Use this template](https://img.shields.io/badge/Fork%20the-template-blue)](https://github.com/narko4u/aci-pages-template/generate)

Replace the placeholders with your organization details and deploy to GitHub Pages. No build tools required.

**Option C — Run the Explorer (zero-dep, from repo):**

```bash
# Zero-dependency discovery — see what an ACI-compatible organization exposes
python3 demo/aci-explorer.py empirelabs.com.au
```

**Option D — Validate a deployment (from repo):**

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
- [AIP](https://github.com/narko4u/aip-spec) — Agent Interaction Protocol (negotiation + execution above ACI)

---

## The Empire Stack

ACI is one layer of a complete stack for autonomous agent commerce:

1. **🔍 [ACI](https://github.com/narko4u/aci-spec)** — *Discovery.* Tells agents who you are and what you offer.
2. **🤝 [AIP](https://github.com/narko4u/aip-spec)** — *Interaction.* Negotiates contracts, executes actions, handles settlements.
3. **✍️ [AJSON](https://github.com/narko4u/ajson)** — *Authoring.* Write manifests with comments and refs, compile to canonical JSON.

→ Use **ACI** to declare your presence, **AIP** to transact, **AJSON** to write it clean.

---

## Quick reference

| Resource | Link |
|----------|------|
| 📦 Package | `pip install aci-spec` — `aci-validate` / `aci-explore` |
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

*Built by Empire Labs Pty Ltd | Maintained by **Sovereign***


---

<sub>Part of the [WitnessOS launch family](https://github.com/narko4u/witnessos): [witnessos-alpha](https://github.com/narko4u/witnessos-alpha) · [witnessos-compliance](https://github.com/narko4u/witnessos-compliance) · [eu-ai-act-compliance-grade](https://github.com/narko4u/eu-ai-act-compliance-grade) · [witnessos-rogue-agent-audit](https://github.com/narko4u/witnessos-rogue-agent-audit) · [witnessos-agent-asset-registry](https://github.com/narko4u/witnessos-agent-asset-registry) · [witnessos-verifier](https://github.com/narko4u/witnessos-verifier) · [agent-interaction-specs](https://github.com/narko4u/agent-interaction-specs) · [aci-spec](https://github.com/narko4u/aci-spec) · [aip-spec](https://github.com/narko4u/aip-spec) · [ajson](https://github.com/narko4u/ajson) — [Empire Labs Pty Ltd](https://www.empirelabs.com.au)</sub>