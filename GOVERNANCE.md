# ACI Governance

**Version 0.9 (Draft)**

> Who owns ACI, and how are decisions made?

---

## Principle

ACI is an open standard. Its long-term value depends on being perceived as neutral,
implementation-agnostic, and community-driven.

During the Draft phase (v0.9), governance is steward-owned by Empire Labs Pty Ltd.
This is transitional. The goal is to transfer governance to a neutral foundation or
standards body once the specification reaches v1.0 and has three or more independent
implementations.

---

## Steward Role (Current Phase)

The specification steward (Empire Labs, as of v0.9):

- Maintains the specification text
- Approves changes to the core specification
- Operates the reference implementation
- Publishes releases and version tags
- Facilitates community input and tracks issues

The steward's authority is limited by the Normative Principle (see SPEC.md). No
change may violate the principle that ACI standardizes what an organization says
about itself, not how it implements its internal systems.

---

## Decision-Making

### Executive Decisions

During the Draft phase, the steward may make executive decisions on:

- Clarifications and errata (patch version bumps)
- Non-breaking additions (minor version bumps)
- Governance document changes

### Consensus Decisions

The following require broader input:

- Breaking changes to the core specification
- Changes to the Normative Principle
- Changes to conformance level definitions
- Transfer of governance to another entity

These SHALL be resolved through the Change Process (see CHANGE_PROCESS.md).

---

## Independence Path

The specification SHALL be transferred to neutral governance when ALL of the
following conditions are met:

1. Three or more independent organizations have published validated ACI
   implementations
2. No breaking change has been required for two consecutive minor versions
3. A suitable neutral host has been identified and agreed by implementers
4. The steward confirms readiness to transfer

At that point, a new governance model SHALL be established through community
consensus.

---

## Licensing

The specification is published under CC BY 4.0. Governance documents are published
under the same license. The steward retains no special rights under this license
that are not available to any other licensee.
