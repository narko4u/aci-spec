# Autonomous Company Interface (ACI)

**Draft Specification v0.9**

> Enable autonomous agents to discover, understand, verify, and interact with organizations
> through open, structured contracts.
>
> An ACI implementation SHOULD enable two independent autonomous systems to reach
> substantially the same understanding of an organization without prior bilateral agreement.

---

## ═══════════════════════════════════════════════
##  Normative Principle
## ═══════════════════════════════════════════════
##
##  ACI standardizes what an organization says about itself,
##  not how it implements its internal systems.
##
## ═══════════════════════════════════════════════

Every section of this specification SHALL be consistent with this principle.
Any future proposal that violates it SHALL be rejected without further consideration.

> Publish contracts. Don't expose secrets.
> Declare capabilities. Don't expose proprietary algorithms.
> Describe products. Don't expose internal architecture unless you choose to.
> Assert trust. Don't expose security posture.

ACI is a *self-description* standard, not an *introspection* standard. It tells the world
what an organization is, not how it works.

---

## Table of Contents

1.  [Purpose](#1-purpose)
2.  [Core Concepts](#2-core-concepts)
3.  [Conformance Levels](#3-conformance-levels)
4.  [Discovery](#4-discovery)
5.  [Identity Manifest](#5-identity-manifest)
6.  [Capability Manifest](#6-capability-manifest)
7.  [Knowledge Manifest](#7-knowledge-manifest)
8.  [Trust Manifest](#8-trust-manifest)
9.  [Agent Manifest](#9-agent-manifest)
10. [Identifiers](#10-identifiers)
11. [Lifecycle States](#11-lifecycle-states)
12. [Extensions](#12-extensions)
13. [Serialization](#13-serialization)
14. [Versioning & Evolution](#14-versioning--evolution)
15. [Non-Goals](#15-non-goals)
16. [Relationship to Other Standards](#16-relationship-to-other-standards)
17. [Validator](#17-validator)
18. [Reference Implementation](#18-reference-implementation)
19. [Governance](#19-governance)

* [Appendix A: Reference Implementation (Informative)](#appendix-a-reference-implementation-informative)

---

## 1. Purpose

Autonomous agents — AI systems that act on behalf of users or organizations — need a standard
way to discover, understand, verify, and interact with companies they encounter. Traditional
company websites are optimized for human readers. API documentation targets software developers.
Neither serves autonomous agents well.

The Autonomous Company Interface (ACI) fills this gap. It defines a set of structured contracts
that organizations publish at a well-known location, enabling autonomous agents to:

- **Discover** that an organization exists and what it does
- **Understand** its products, services, capabilities, and domain knowledge
- **Verify** its identity and claims through attestations and evidence
- **Interact** with it through declared agent endpoints and transaction contracts

ACI is not a replacement for websites, APIs, or human relationships. It is a *companion layer* —
machine-readable organizational contract that sits alongside existing channels.

---

## 2. Core Concepts

ACI defines five manifest types. Each represents a distinct facet of organizational self-description:

| Manifest | Purpose |
|----------|---------|
| **Identity Manifest** | Who the organization is — name, jurisdiction, identifiers, contact |
| **Capability Manifest** | What the organization offers — products, services, solutions |
| **Knowledge Manifest** | What the organization knows — concepts, ontology, domain model |
| **Trust Manifest** | How the organization verifies its claims — patents, attestations, evidence |
| **Agent Manifest** | What autonomous agents the organization exposes — endpoints, capabilities, discovery |

Each manifest is independent but designed to be linked. An agent SHOULD be able to start at any
manifest and navigate to the others via cross-references.

### 2.1 Key Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT",
"RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

---

## 3. Conformance Levels

ACI defines three conformance levels. An organization claims conformance at a specific level
only when all requirements of that level are met.

### 3.1 Level 1 — Discovery

Sufficient for an AI agent to know who the organization is and what it does.

**Requirements:**
- **Identity Manifest** MUST be published (§5)
- **Capability Manifest** MUST be published (§6)
- **Discovery chain** MUST be fully operational (§4)
- All mandatory fields for Identity and Capability manifests MUST be present

### 3.2 Level 2 — Understanding

Sufficient for an AI agent to reason about the organization's domain and verify its claims.

**Requirements:**
- Level 1 MUST be met
- **Knowledge Manifest** MUST be published (§7)
- **Trust Manifest** MUST be published (§8)
- All mandatory fields for Knowledge and Trust manifests MUST be present
- Cross-references between all Level 2 manifests MUST resolve

### 3.3 Level 3 — Interaction

Sufficient for autonomous agent-to-agent interaction.

**Requirements:**
- Level 2 MUST be met
- **Agent Manifest** MUST be published (§9)
- At least one agent endpoint MUST be declared with an operational interaction method
- All five manifests MUST pass ACI Validator checks with a score of 90 or above

### 3.4 Conformance Claims

An organization MAY claim conformance at Level 1 or Level 2 without meeting higher levels.
Claims SHALL be verifiable by the ACI Validator.

> Example: "We are ACI Level 2 compliant."

This is preferable to "we're halfway implemented" — it signals a specific, testable capability
boundary.

---

## 4. Discovery

An autonomous agent discovers an organization's ACI manifests through a discovery chain.

### 4.1 Entry Point: `llms.txt`

The primary entry point SHALL be `/llms.txt` at the organization's primary domain, as defined by
the [llms.txt community standard](https://llmstxt.org/). This file MUST link to all manifests
required by the organization's claimed conformance level.

Example:

```text
# AI manifests
- [Identity Manifest](https://example.com/identity.json)
- [Capability Manifest](https://example.com/capabilities.json)
- [Knowledge Manifest](https://example.com/knowledge.json)
- [Trust Manifest](https://example.com/trust.json)
- [Agent Manifest](https://example.com/agents.json)
```

### 4.2 Alternative Entry Points

Organizations MAY also:

- Include manifest links in `sitemap.xml`
- Reference manifests via `<link>` tags in HTML `<head>`
- Register manifests in a `/.well-known/` directory (e.g., `/.well-known/agents.json`)
- Advertise manifests through DNS TXT records or other service discovery mechanisms

### 4.3 Cross-Referencing

Each manifest SHOULD include a `discovery` section linking to the other manifests, allowing an
agent that discovers any single manifest to navigate to the full set.

---

## 5. Identity Manifest

### 5.1 Purpose

Declares who the organization is. This is the foundation — every other manifest references an
identity.

### 5.2 Required Fields

| Field | Specification |
|-------|--------------|
| `manifest_version` | MUST be present. Version of the ACI specification (§14). |
| `last_updated` | MUST be present. ISO 8601 timestamp of last change. |
| `publisher` | MUST be present. Legal name of the publishing organization. |
| `identifiers` | MUST be present. Array of canonical identifiers (§10) — at least one MUST be a stable, globally unique identifier (e.g., domain name, ABN, DUNS, LEI). |

### 5.3 Optional Fields

| Field | Specification |
|-------|--------------|
| `jurisdiction` | SHOULD be present. Country or region of incorporation. |
| `registration_number` | SHOULD be present. Company registration or ABN. |
| `website` | SHOULD be present. Primary website URL. |
| `contact` | SHOULD be present. Contact information (email, form URL, or agent endpoint). |
| `social` | MAY be present. Social media or professional profiles. |
| `brand` | MAY be present. Brand name(s) if different from legal name. |
| `description` | SHOULD be present. Short plain-text description of the organization. |

### 5.4 Example

See [Appendix A](#appendix-a-reference-implementation-informative) for a complete working example.

---

## 6. Capability Manifest

### 6.1 Purpose

Declares what the organization offers. Products, services, and solutions with enough structure
for an agent to evaluate relevance.

### 6.2 Required Fields

| Field | Specification |
|-------|--------------|
| `manifest_version` | MUST be present. Version of the ACI specification (§14). |
| `last_updated` | MUST be present. ISO 8601 timestamp of last change. |
| `publisher` | MUST be present. Legal name of the publishing organization. |

### 6.3 Optional Fields

| Field | Specification |
|-------|--------------|
| `industries` | MAY be present. Industry classification(s) using standard taxonomies. |
| `pricing_model` | MAY be present. Brief description of pricing approach. |
| `documentation` | SHOULD be present. Links to documentation and API references. |

### 6.4 Content Blocks

At least one of the following content blocks SHOULD be present:

- `products` — Array of product descriptions
- `services` — Array of service descriptions
- `solutions` — Array of solution descriptions

### 6.5 Example

See [Appendix A](#appendix-a-reference-implementation-informative).

---

## 7. Knowledge Manifest

### 7.1 Purpose

Declares what the organization knows. A structured ontology of domain concepts and their
relationships, enabling an agent to reason about the organization's area of expertise.

### 7.2 Required Fields

| Field | Specification |
|-------|--------------|
| `manifest_version` | MUST be present. |
| `last_updated` | MUST be present. |
| `publisher` | MUST be present. |

### 7.3 Optional Fields

| Field | Specification |
|-------|--------------|
| `domain` | SHOULD be present. Primary domain identifier. |
| `domain_label` | SHOULD be present. Human-readable domain label. |

### 7.4 Content Blocks

- `concepts` — Array of concept definitions (SHOULD be present for Level 2)

### 7.5 Example

See [Appendix A](#appendix-a-reference-implementation-informative).

---

## 8. Trust Manifest

### 8.1 Purpose

Declares how the organization verifies its claims. Attestations, certifications, patents, and
other evidence that an agent can evaluate to establish trust.

### 8.2 Required Fields

| Field | Specification |
|-------|--------------|
| `manifest_version` | MUST be present. |
| `last_updated` | MUST be present. |
| `publisher` | MUST be present. |

### 8.3 Optional Fields

| Field | Specification |
|-------|--------------|
| `certifications` | MAY be present. Industry certifications or accreditations. |
| `patents` | MAY be present. Filed or granted patents. |
| `compliance` | MAY be present. Regulatory compliance declarations. |
| `signatures` | MAY be present. Digital signatures over manifest content. |
| `history` | MAY be present. Change history of trust claims. |

### 8.4 Content Blocks

- `assertions` — Array of trust assertions (SHOULD be present for Level 2)

### 8.5 Example

See [Appendix A](#appendix-a-reference-implementation-informative).

---

## 9. Agent Manifest

### 9.1 Purpose

Declares what autonomous agents the organization exposes. Endpoints, capabilities,
authentication methods, and interaction models for agent-to-agent communication.

### 9.2 Required Fields

| Field | Specification |
|-------|--------------|
| `manifest_version` | MUST be present. |
| `last_updated` | MUST be present. |
| `publisher` | MUST be present. |

### 9.3 Optional Fields

| Field | Specification |
|-------|--------------|
| `authentication` | SHOULD be present. Default authentication method for all agents. |
| `discovery` | SHOULD be present. Links back to other manifests. |

### 9.4 Content Blocks

- `agents` — Array of agent declarations (SHOULD be present for Level 3)

Each agent declaration SHOULD include:

| Agent Field | Specification |
|-------------|--------------|
| `id` | MUST be present. Unique stable identifier. |
| `name` | SHOULD be present. Human-readable name. |
| `type` | SHOULD be present. Agent classification or role. |
| `description` | SHOULD be present. What the agent does. |
| `capabilities` | SHOULD be present. Array of capability identifiers. |
| `interface` | SHOULD be present. Interaction model and protocol. |
| `authentication` | SHOULD be present. Authentication method for this agent. |
| `status` | SHOULD be present. Operational status. |

### 9.5 Example

See [Appendix A](#appendix-a-reference-implementation-informative).

---

## 10. Identifiers

ACI identifiers provide stable, globally unique references for organizations, products, concepts,
and agents.

### 10.1 Grammar

An ACI identifier SHALL conform to the following grammar:

```
identifier       = segment *( "." segment )
segment          = alphanum *( alphanum / "-" / "_" )
alphanum         = %x41-5A / %x61-7A / %x30-39  ; A-Z / a-z / 0-9
```

Examples of valid identifiers:

```
org.novadynamics
novadynamics.nexus-bot
novadynamics.product.skyhook-api
autonomous-systems.deterministic-mission
```

An identifier SHALL NOT exceed 128 characters.

### 10.2 Identifier Types

| Type | Format | Example |
|------|--------|---------|
| **Organization ID** | `org.<name>` | `org.novadynamics` |
| **Product ID** | `<org>.<product>` | `novadynamics.skyhook` |
| **Agent ID** | `<org>.<agent>` | `novadynamics.nexus-bot` |
| **Concept ID** | `<domain>.<concept>` | `autonomous-systems.deterministic-mission` |

### 10.3 Stability

Identifiers SHALL NOT change once published. If an organization, product, or agent is renamed,
the old identifier SHOULD be deprecated with a `status` of `superseded` and a `superseded_by`
field pointing to the new identifier.

Unpublished identifiers (draft or withdrawn) MAY be recycled.

---

## 11. Lifecycle States

Every named entity in ACI (identifiers, products, agents, concepts) SHOULD declare a lifecycle
state.

### 11.1 Defined States

| State | Meaning |
|-------|---------|
| `active` | Currently operational / valid |
| `deprecated` | Still operational but slated for removal |
| `superseded` | Replaced by another entity |
| `withdrawn` | Removed, no longer valid |

### 11.2 Transitions

```
active ──→ deprecated ──→ superseded
  │                        ↑
  └─────→ withdrawn        │
                            │
                    (points to replacement)
```

### 11.3 Usage

When an entity is `superseded`, a `superseded_by` field SHOULD reference the new identifier.

---

## 12. Extensions

### 12.1 Extension Mechanism

Implementations MAY extend any manifest with custom fields using the `x-` prefix convention.
This follows the approach used by OpenAPI, JSON Schema, and similar standards.

### 12.2 Rules

1. Extension fields MUST start with `x-` (e.g., `x-internal-rating`, `x-shipping-zones`)
2. The ACI Validator SHALL ignore `x-` fields when checking conformance
3. Extensions MUST NOT redefine or contradict normative fields
4. Extensions SHOULD be documented in a companion file or README

### 12.3 Example

```json
{
  "manifest_version": "0.9.0",
  "publisher": "Example Corp",
  "x-preferred-partner-tier": "gold",
  "x-regional-availability": ["AU", "NZ", "SG"]
}
```

---

## 13. Serialization

### 13.1 JSON (Primary)

The primary serialization format for ACI manifests is JSON. All examples in this specification
use JSON.

- Manifests SHALL be valid JSON (RFC 7159)
- File extension SHOULD be `.json`
- MIME type SHOULD be `application/json`

### 13.2 Alternative Serializations

Organizations MAY serve manifests in alternative formats (YAML, CBOR, etc.) alongside JSON,
provided at least one JSON representation is available at the well-known location.

---

## 14. Versioning & Evolution

### 14.1 Specification Version

The ACI specification uses semantic versioning: `MAJOR.MINOR.PATCH`.

- **MAJOR**: Breaking changes to normative requirements
- **MINOR**: Non-breaking additions or clarifications
- **PATCH**: Editorial fixes, typos, better examples

### 14.2 Manifest Version

Each manifest includes a `manifest_version` field matching the specification version under
which it was published. This allows validators to determine which schema version applies.

### 14.3 Schema Version

An optional `schema_version` field MAY be present for granular validation. When absent,
validators SHOULD use the `manifest_version` to select the appropriate schema.

### 14.4 Version Status & Promotion

The current specification version is **Draft v0.9**. It SHALL remain at v0.9 until ALL of the
following conditions are met:

1. **Three or more independent implementations** exist, validated by the ACI Validator
2. **Feedback from implementers** has been received and incorporated
3. **The core specification** has stabilized through community review

At that point, the steward SHALL promote the specification to **v1.0**.

> This rule exists because a specification is not truly stable until multiple parties have
> implemented it independently. Version 1.0 is earned by adoption, not by declaration.

---

## 15. Non-Goals

ACI deliberately does NOT address the following:

1. **Not a replacement for human-facing websites** — ACI supplements, not replaces, existing
   web presence
2. **Not an API specification** — ACI describes *what* an organization offers, not *how* to
   call its APIs (use OpenAPI for that)
3. **Not a data model for internal systems** — ACI is a public self-description, not an
   internal schema
4. **Not a trust framework** — ACI provides a format for trust claims, but does not verify
   them. External attestation mechanisms handle verification
5. **Not a contract negotiation protocol** — ACI does not define how agents negotiate terms
6. **Not a payment or billing standard** — ACI describes offerings, not transactions
7. **Not a replacement for Schema.org** — Schema.org provides general web markup; ACI provides
   structured organizational contracts for autonomous agents
8. **Not a replacement for MCP (Model Context Protocol)** — MCP connects agents to tools and
   data; ACI describes organizations. They are complementary
9. **Not a registry** — ACI does not require a central registry, though one may be built on
   top of the specification
10. **Not a legal framework** — ACI manifests are self-descriptions, not legally binding contracts

---

## 16. Relationship to Other Standards

| Standard | Relationship to ACI |
|----------|-------------------|
| **llms.txt** | Primary discovery mechanism for ACI manifests |
| **OpenAPI** | ACI capabilities MAY link to OpenAPI specs. OpenAPI describes *how* to call an API; ACI describes *what* an organization offers |
| **Schema.org** | Complementary. Schema.org marks up web pages for search engines; ACI provides structured manifests for autonomous agents |
| **MCP** | An ACI agent manifest MAY declare MCP endpoints. MCP connects to tools; ACI finds the organization and its agents |
| **JSON Schema** | ACI schemas are expressed in YAML but compatible with JSON Schema concepts |
| **ISO 8601** | All timestamps MUST use ISO 8601 |
| **RFC 2119** | Key words (MUST, SHOULD, MAY) follow RFC 2119 semantics |

---

## 17. Validator

### 17.1 Purpose

The ACI Validator is a CLI tool that checks an organization's ACI implementation for conformance
with this specification. It is the reference tool for:

- Self-assessment before claiming conformance
- Third-party verification of conformance claims
- Debugging manifest issues during implementation

### 17.2 What It Checks

| Check | What It Validates |
|-------|-------------------|
| Discovery | `llms.txt` exists, is parseable, and links to manifests |
| Existence | Each required manifest is reachable and returns HTTP 200 |
| JSON Validity | Each manifest parses as valid JSON |
| Required Fields | All required fields per §5-9 are present |
| Content Blocks | Manifest-specific content blocks are populated |
| Version Consistency | All manifests use the same `manifest_version` |
| Identity Consistency | All manifests reference the same `publisher` |

### 17.3 Scoring

| Score | Rating |
|-------|--------|
| 90-100 | Full Compliance |
| 70-89 | Partial Compliance |
| 50-69 | Minimal Compliance |
| 0-49 | Non-Compliant |

A score of 100 requires all checks to pass with no warnings.

### 17.4 Usage

```bash
aci validate https://example.com
```

The output includes:
- Overall ACI Score
- Per-manifest scores with pass/fail per check
- Warnings for optional items that would improve the score
- A summary of the discovery chain

### 17.5 Implementation

The reference validator is published as open-source software (see §18.3). The validator loads
its schema definitions dynamically from `schema/` files, allowing the specification to evolve
without requiring validator logic changes.

---

## 18. Reference Implementation

### 18.1 Primary Reference: Empire Labs

The primary reference implementation of the ACI specification is the Empire Labs website at
[empirelabs.com.au](https://empirelabs.com.au/). All five manifests are published, linked from
`llms.txt`, and verifiable by the ACI Validator.

See [Appendix A](#appendix-a-reference-implementation-informative) for the complete manifest
content.

> **Note:** This reference implementation is INFORMATIVE, not NORMATIVE. The specification
> remains self-contained and valid independent of any particular implementation. If the
> Empire Labs reference were to disappear, the specification would not be affected.

### 18.2 What Makes a Valid Reference Implementation

A valid ACI reference implementation MUST:

1. Publish all five manifests (Identity, Capability, Knowledge, Trust, Agent)
2. Make them discoverable via `llms.txt`
3. Pass ACI Validator checks with a score of 100/100
4. Provide a contact mechanism for agent-to-human escalation
5. Keep `manifest_version`, `last_updated`, and `publisher` consistent across all manifests

### 18.3 Open-Source Tooling

The following tools are published as open source:

- **ACI Validator** — CLI tool for validating ACI implementations (`aci validate`)
- **ACI Template** — Starter template for organizations adopting ACI
- **JSON Schemas** — Machine-readable schema definitions for all five manifests

### 18.4 Adoption

Organizations implementing ACI are encouraged to:

1. Register their implementation in the ACI Adopters list
2. Contribute improvements to the specification
3. Maintain their manifests as living documents, updated with each significant change

---

## 19. Governance

ACI governance is documented in a set of companion files that are part of this specification
package but maintained separately from the normative content.

| Document | Purpose |
|----------|---------|
| [GOVERNANCE.md](./GOVERNANCE.md) | Who owns ACI, decision-making, and long-term stewardship |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | How to propose changes, report issues, and participate |
| [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) | Community standards and expectations |
| [CHANGE_PROCESS.md](./CHANGE_PROCESS.md) | How the specification evolves — RFC process, review, and approval |

These documents answer *who owns ACI* and *how it changes*. The specification itself answers
*what ACI is*. They are separated so that the normative content remains independent of any
particular governance model. If governance is transferred to a foundation or standards body
in the future, only the governance files need to change — the specification stays intact.

---

## Appendix A: Reference Implementation (Informative)

*This appendix is INFORMATIVE, not NORMATIVE. It provides a concrete example of an ACI
implementation for reference purposes. The specification does not depend on this content.*

### A.1 Discovery Chain

```
https://empirelabs.com.au/llms.txt
  ├── identity.json
  ├── capabilities.json
  ├── knowledge.json
  ├── trust.json
  └── agents.json
```

### A.2 Identity Manifest

```json
{
  "manifest_version": "0.9.0",
  "schema_version": "0.9.0",
  "last_updated": "2026-07-19T04:00:00Z",
  "publisher": "Empire Labs Pty Ltd",
  "jurisdiction": "Australia",
  "registration_number": "Pending",
  "website": "https://empirelabs.com.au",
  "contact": "contact@empirelabs.com.au",
  "brand": "Empire Labs",
  "description": "Autonomous Operations Systems Engineering — building infrastructure for governed autonomous systems",
  "identifiers": [
    {
      "id": "org.empire-labs",
      "type": "domain",
      "value": "empirelabs.com.au"
    }
  ],
  "discovery": {
    "llms-txt": "https://empirelabs.com.au/llms.txt",
    "capability-manifest": "https://empirelabs.com.au/capabilities.json",
    "agent-manifest": "https://empirelabs.com.au/.well-known/agents.json",
    "knowledge-graph": "https://empirelabs.com.au/knowledge.json",
    "trust-manifest": "https://empirelabs.com.au/trust.json"
  }
}
```

### A.3 Capability Manifest

```json
{
  "manifest_version": "0.9.0",
  "last_updated": "2026-07-19",
  "publisher": "Empire Labs Pty Ltd",
  "products": [
    {
      "id": "empire-labs.witnessos",
      "name": "WitnessOS",
      "type": "Runtime governance layer for autonomous AI",
      "description": "Policy enforcement, SHA-256 evidence-grade receipts, and R0-R6 structured remediation."
    },
    {
      "id": "empire-labs.atlasos",
      "name": "AtlasOS",
      "type": "Autonomous terrain operations system",
      "description": "Mission generation, digital twin, deterministic geometry, and WitnessOS governance."
    }
  ],
  "services": [
    {
      "id": "empire-labs.runtime-governance",
      "name": "Runtime Governance",
      "description": "Policy enforcement and evidence receipts for autonomous systems"
    }
  ],
  "capabilities": {
    "deterministic": true,
    "patent-protected": true,
    "local-first": true,
    "governed": true
  },
  "documentation": {
    "ai-index": "https://empirelabs.com.au/llms.txt",
    "identity-manifest": "https://empirelabs.com.au/identity.json",
    "capability-manifest": "https://empirelabs.com.au/capabilities.json",
    "agent-manifest": "https://empirelabs.com.au/.well-known/agents.json",
    "knowledge-graph": "https://empirelabs.com.au/knowledge.json",
    "trust-manifest": "https://empirelabs.com.au/trust.json"
  }
}
```

### A.4 Knowledge Manifest

```json
{
  "manifest_version": "0.9.0",
  "last_updated": "2026-07-19",
  "publisher": "Empire Labs Pty Ltd",
  "domain": "autonomous-systems-engineering",
  "domain_label": "Autonomous Systems Engineering",
  "concepts": [
    {
      "id": "autonomous-systems.runtime-governance",
      "name": "Runtime Governance",
      "description": "Policy enforcement and evidence generation for autonomous decision-making systems."
    },
    {
      "id": "autonomous-systems.evidence-receipt",
      "name": "Evidence Receipt",
      "description": "SHA-256 signed, tamper-evident record of an agent action and its policy evaluation result."
    },
    {
      "id": "autonomous-systems.deterministic-mission",
      "name": "Deterministic Mission",
      "description": "A robot mission plan fully reproducible from the same inputs."
    },
    {
      "id": "autonomous-systems.digital-twin",
      "name": "Digital Twin",
      "description": "A simulated representation of a mission mirroring the real environment."
    },
    {
      "id": "autonomous-systems.r0-r6-remediation",
      "name": "R0-R6 Structured Remediation",
      "description": "A seven-level remediation framework for policy violations."
    }
  ],
  "relationships": [
    { "source": "empire-labs.atlasos", "relation": "governed_by", "target": "empire-labs.witnessos" },
    { "source": "empire-labs.atlasos", "relation": "produces", "target": "autonomous-systems.deterministic-mission" },
    { "source": "empire-labs.witnessos", "relation": "implements", "target": "autonomous-systems.r0-r6-remediation" }
  ]
}
```

### A.5 Trust Manifest

```json
{
  "manifest_version": "0.9.0",
  "last_updated": "2026-07-19",
  "publisher": "Empire Labs Pty Ltd",
  "patents": [
    {
      "patent_id": "AU-2026906017",
      "title": "Runtime governance and evidence generation for autonomous decision-making systems",
      "status": "pending",
      "products": ["empire-labs.witnessos", "empire-labs.atlasos"]
    },
    {
      "patent_id": "AU-2026905005",
      "title": "Intelligent request distribution across LLM providers",
      "status": "pending",
      "products": ["empire-labs.smartrouter"]
    }
  ],
  "assertions": [
    {
      "type": "registration",
      "claims": "Empire Labs Pty Ltd is a registered Australian company.",
      "status": "active"
    },
    {
      "type": "patent",
      "claims": "Patent applications AU 2026906017 and AU 2026905005 are filed and being examined.",
      "evidence": "https://empirelabs.com.au/trust.json#patents",
      "status": "active"
    }
  ],
  "security": {
    "disclosure": "contact@empirelabs.com.au",
    "policy": "Responsible disclosure. Security-focused engineering with evidence-first delivery."
  }
}
```

### A.6 Agent Manifest

```json
{
  "manifest_version": "0.9.0",
  "last_updated": "2026-07-19",
  "publisher": "Empire Labs Pty Ltd",
  "agents": [
    {
      "id": "empire-labs.witnessos",
      "name": "WitnessOS",
      "type": "governance-agent",
      "description": "Runtime governance layer for autonomous AI.",
      "capabilities": ["policy-evaluation", "evidence-receipt-generation", "remediation-orchestration"],
      "interface": {
        "type": "api",
        "protocol": "https",
        "integration-model": "rest-api-webhook"
      },
      "authentication": "api-key",
      "status": "pre-order"
    },
    {
      "id": "empire-labs.atlasos",
      "name": "AtlasOS",
      "type": "mission-agent",
      "description": "Autonomous mission generation and governance platform.",
      "capabilities": ["mission-generation", "digital-twin-visualisation", "deterministic-geometry"],
      "interface": {
        "type": "web-ui-api",
        "protocol": "https"
      },
      "authentication": "api-key",
      "status": "alpha"
    }
  ],
  "discovery": {
    "llms-txt": "https://empirelabs.com.au/llms.txt",
    "identity-manifest": "https://empirelabs.com.au/identity.json",
    "capability-manifest": "https://empirelabs.com.au/capabilities.json",
    "knowledge-graph": "https://empirelabs.com.au/knowledge.json",
    "trust-manifest": "https://empirelabs.com.au/trust.json"
  },
  "authentication": {
    "type": "api-key",
    "details": "Contact contact@empirelabs.com.au for API access."
  }
}
```

---

## License

This specification is published under the Creative Commons Attribution 4.0 International License
(CC BY 4.0). Implementations, derivative works, and contributions are encouraged.

## See Also

- [GOVERNANCE.md](./GOVERNANCE.md) — Who owns ACI, decision-making, and long-term stewardship
- [CONTRIBUTING.md](./CONTRIBUTING.md) — How to propose changes and participate
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) — Community standards and expectations
- [CHANGE_PROCESS.md](./CHANGE_PROCESS.md) — RFC process for specification evolution

---

*Autonomous Company Interface (ACI) — Draft Specification v0.9*
*Reference Implementation: Empire Labs (https://empirelabs.com.au)*
