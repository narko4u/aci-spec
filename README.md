# Autonomous Company Interface (ACI)

[![OpenSSF Best Practices - Baseline 1](https://www.bestpractices.dev/projects/14141/badge)](https://www.bestpractices.dev/projects/14141)

**Status:** Draft Specification v0.9

[![PyPI version](https://img.shields.io/pypi/v/aci-spec?color=blue)](https://pypi.org/project/aci-spec/)
[![PyPI downloads](https://img.shields.io/pypi/dm/aci-spec)](https://pypi.org/project/aci-spec/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/spec-CC%20BY%204.0-lightgrey)](LICENSE-CC-BY-4.0)

> **Seeking three independent implementations for ACI v1.0** - [Track progress](https://github.com/narko4u/aci-spec/issues/6)

> **📢 Community feedback window: open until 2026-09-15.** ACI is heading to v1.0 and we want your input before we freeze the core. Review the [SPEC](SPEC.md), try the [CLI](https://pypi.org/project/aci-spec/), and tell us what breaks. Post via [GitHub Discussions](https://github.com/narko4u/aci-spec/discussions) or issues. Every substantive comment gets a reply.

An open specification for describing organizations to autonomous agents through structured, machine-readable contracts.

ACI enables autonomous systems to:

- **Discover** organizations and what they do
- **Understand** capabilities and domain knowledge
- **Verify** identity and claims through attestations
- **Locate** autonomous agents and interaction endpoints
- **Interact** through open, governed contracts

---

## Get started in 5 minutes

**Option A - Install from PyPI (recommended):**

```bash
pip install aci-spec
```

Then validate any ACI deployment:

```bash
aci-validate empirelabs.com.au
aci-explore empirelabs.com.au
```

**Option B - Fork the template:**

[![Use this template](https://img.shields.io/badge/Fork%20the-template-blue)](https://github.com/narko4u/aci-pages-template/generate)

Replace the placeholders with your organization details and deploy to GitHub Pages. No build tools required.

**Option C - Run the Explorer (zero-dep, from repo):**

```bash
# Zero-dependency discovery - see what an ACI-compatible organization exposes
python3 demo/aci-explorer.py empirelabs.com.au
```

**Option D - Validate a deployment (from repo):**

```bash
python3 validator/validate.py https://your-org.github.io/your-site
```

**Option E - Build from source:**

```bash
git clone https://github.com/narko4u/aci-spec.git
cd aci-spec
python -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install .
```

The build uses standard PEP 517 tooling (`setuptools>=64`); no external
system libraries are required. Python 3.9+ is supported. After building, the
`aci-validate` and `aci-explore` CLI entry points are available in the
virtualenv.

---

## Contents

- [SPEC.md](./SPEC.md) - The specification
- [schema/](./schema/) - Machine-readable YAML schemas for all five manifest types
- [validator/](./validator/) - Open-source ACI Validator CLI
- [examples/](./examples/) - Example implementations (JSON + AJSON authoring format)
- [demo/aci-explorer.py](./demo/aci-explorer.py) - Zero-dependency CLI discovery tool
- [AJSON](https://github.com/narko4u/ajson) - Manifest authoring format with comments, refs, and canonical compilation
- [AIP](https://github.com/narko4u/aip-spec) - Agent Interaction Protocol (negotiation + execution above ACI)

---

## The Empire Stack

ACI is one layer of a complete stack for autonomous agent commerce:

1. **🔍 [ACI](https://github.com/narko4u/aci-spec)** - *Discovery.* Tells agents who you are and what you offer.
2. **🤝 [AIP](https://github.com/narko4u/aip-spec)** - *Interaction.* Negotiates contracts, executes actions, handles settlements.
3. **✍️ [AJSON](https://github.com/narko4u/ajson)** - *Authoring.* Write manifests with comments and refs, compile to canonical JSON.

→ Use **ACI** to declare your presence, **AIP** to transact, **AJSON** to write it clean.

---

## Quick reference

| Resource | Link |
|----------|------|
| 📦 Package | `pip install aci-spec` - `aci-validate` / `aci-explore` |
| Specification | [SPEC.md](./SPEC.md) |
| Schema (YAML) | [schema/](./schema/) |
| Validator | [validator/validate.py](./validator/validate.py) |
| Explorer | [demo/aci-explorer.py](./demo/aci-explorer.py) |
| Example implementations | [examples/](./examples/) |
| Deployment template | [narko4u/aci-pages-template](https://github.com/narko4u/aci-pages-template) |
| Live implementation | [empirelabs.com.au](https://empirelabs.com.au) |

## Dependencies

- **Runtime**: zero external dependencies. The validator, explorer, and
  authoring tooling run on the Python standard library only.
- **Build**: `setuptools>=64` (PEP 517 backend).

### Dependency management

The project follows a deliberate, minimal dependency policy:

1. **Selection** - dependencies are avoided unless a standard-library
   alternative does not exist. The reference implementation currently has
   zero runtime dependencies.
2. **Obtaining** - dependencies are declared in `pyproject.toml` and pinned
   through the `uv.lock` lockfile, so every build uses a reproducible set of
   package versions.
3. **Tracking** - dependencies are monitored three ways:
   - **SCA**: every push/PR runs [OSV-Scanner](https://google.github.io/osv-scanner/)
     in the `security` workflow to detect known vulnerabilities in the lockfile.
   - **SBOM**: every release ships a CycloneDX SBOM (`sbom.cdx.json`) listing
     the exact dependency set of the released artifact.
   - **Integrity**: every release asset ships with a Sigstore signature and a
     `SHA256SUMS` checksum manifest (see [Verifying releases](#verifying-releases)).

## Verifying releases

Every release is built, checksummed, and signed by the release pipeline
([`.github/workflows/release.yml`](.github/workflows/release.yml)). The
following assets are attached to every GitHub release:

- `aci_spec-<version>-py3-none-any.whl` and `aci_spec-<version>.tar.gz`
  (the distributable)
- `sbom.cdx.json` — a CycloneDX software bill of materials for the release
- `SHA256SUMS` — integrity checksums for every asset
- `.sig` / `.pem` — a Sigstore signature and signing certificate for every
  asset

### 1. Verify integrity

Download `SHA256SUMS` and verify every asset matches its published hash:

```sh
sha256sum -c SHA256SUMS
```

### 2. Verify authenticity

Each asset is signed with Sigstore keyless signing using the GitHub
Actions OIDC identity of the release workflow. Verify a signature with
`cosign` (no signing key required):

```sh
cosign verify-blob \
  --certificate aci_spec-0.9.0-py3-none-any.whl.pem \
  --signature aci_spec-0.9.0-py3-none-any.whl.sig \
  --certificate-identity "https://github.com/narko4u/aci-spec/.github/workflows/release.yml@refs/tags/v*" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  aci_spec-0.9.0-py3-none-any.whl
```

The command fails if the signature does not trace back to the release
workflow of this repository.

### 3. Verify the release author identity

Releases are authored by the **release pipeline of `narko4u/aci-spec`**,
maintained by **Empire Labs Pty Ltd** (contact@empirelabs.com.au). The
Sigstore certificate in the `.pem` file binds each asset to:

- **Workflow identity** — the `Release` workflow of
  `github.com/narko4u/aci-spec` (the `--certificate-identity` match above)
- **OIDC issuer** — `https://token.actions.githubusercontent.com`, i.e.
  GitHub itself attests to the identity that signed the asset

No human key is involved; the identity is machine-verifiable and cannot be
spoofed by anyone who cannot trigger releases on this repository. Tags are
created on `main` after CI passes, so a release always corresponds to a
specific, tested commit.

### 4. Software bill of materials

`sbom.cdx.json` lists every dependency of the release. Inspect it with any
CycloneDX consumer or review it directly in the release assets.

### 5. Threat model and vulnerability disclosure

See [THREAT-ASSESSMENT.md](THREAT-ASSESSMENT.md) for the threat model and
attack-surface analysis, and [VEX.md](VEX.md) for the vulnerability
exploitability (VEX) statement. Security issues are handled per
[SECURITY.md](SECURITY.md).

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

<sub>Part of the [WitnessOS launch family](https://github.com/narko4u/witnessos): [witnessos-alpha](https://github.com/narko4u/witnessos-alpha) · [witnessos-compliance](https://github.com/narko4u/witnessos-compliance) · [eu-ai-act-compliance-grade](https://github.com/narko4u/eu-ai-act-compliance-grade) · [witnessos-rogue-agent-audit](https://github.com/narko4u/witnessos-rogue-agent-audit) · [witnessos-agent-asset-registry](https://github.com/narko4u/witnessos-agent-asset-registry) · [witnessos-verifier](https://github.com/narko4u/witnessos-verifier) · [agent-interaction-specs](https://github.com/narko4u/agent-interaction-specs) · [aci-spec](https://github.com/narko4u/aci-spec) · [aip-spec](https://github.com/narko4u/aip-spec) · [ajson](https://github.com/narko4u/ajson) - [Empire Labs Pty Ltd](https://www.empirelabs.com.au)</sub>