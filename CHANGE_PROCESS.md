# ACI Change Process

**Version 0.9 (Draft)**

> How the specification evolves — RFC process, review, and approval.

---

## Change Types

Changes fall into three categories:

| Category | Description | Approval | Version Impact |
|----------|-------------|----------|----------------|
| **Editorial** | Typos, formatting, clarifications, better examples | Steward only | Patch |
| **Non-breaking** | New optional fields, new conformance level guidance, new examples | Steward + reasonable notice | Minor |
| **Breaking** | Removed or renamed required fields, changed semantics, changed discovery mechanism | RFC + review period + implementer consensus | Major |

---

## Process for Breaking Changes

### Step 1: Open an RFC Issue

Submit a GitHub issue with the label `rfc` containing:

- **Summary**: What is being proposed, in one paragraph
- **Motivation**: Why the change is necessary
- **Design**: What the specification would look like after the change
- **Impact**: What existing implementations would need to change
- **Migration**: How existing implementations could transition

### Step 2: Review Period

The RFC SHALL remain open for a minimum of 14 days for public comment.

### Step 3: Implementer Input

If the ACI Adopters list contains three or more independent implementations,
at least two of them MUST be consulted before the RFC can proceed.

### Step 4: Decision

The steward makes a decision based on:
- Consistency with the Normative Principle
- Feedback from the review period
- Impact on existing implementations
- Clarity and quality of the proposed specification text

The decision SHALL be documented in the RFC issue.

### Step 5: Implementation

Once approved, the change is implemented as a pull request, reviewed, and merged.
A new version tag is created.

---

## Process for Non-Breaking Changes

1. Open an issue or pull request describing the change
2. Allow 7 days for comment
3. Steward reviews and merges

---

## Process for Editorial Changes

1. Submit a pull request
2. Steward reviews and merges

No waiting period is required for editorial changes.

---

## Emergency Changes

If a security vulnerability or critical interoperability issue is discovered,
the steward may make an emergency change without following the full process.
An emergency change MUST be:

1. Documented in an issue within 24 hours
2. Ratified by the community within 14 days, or reverted

---

## Versioning

See SPEC.md §14 for versioning semantics. In summary:

- Patch version: editorial changes
- Minor version: non-breaking additions
- Major version: breaking changes

The specification SHALL remain at v0.9 until the promotion rule (SPEC.md §14.4)
is satisfied.
