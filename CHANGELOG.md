# Changelog

## draft-v0.9 — 2026-07-19

Initial public draft of the Autonomous Company Interface specification.

### Highlights

- Five abstract manifest types: Identity, Capability, Knowledge, Trust, Agent
- Discovery chain via `llms.txt` plus `/.well-known/aci` and DNS TXT records
- Three conformance levels (L1 Discovery, L2 Understanding, L3 Interaction)
- Dynamic validator with YAML schema loading
- Open-source validator CLI
- YAML schemas for all five manifest types
- Extension mechanism (`x-` prefix)
- RFC 2119 terminology (MUST/SHOULD/MAY)
- Lifecycle states for manifests and identifiers
- Formal identifier grammar
- Clear non-goals and relationship to other standards
- Example implementations for all conformance levels

### Reference Implementation

- Empire Labs (https://empirelabs.com.au) — Level 3 compliant, 100/100 score

### RFC-002 — Discovery Improvements (2026-07-19)

- Added §4.2: Standardized `/.well-known/aci` discovery file (RFC 8615 pattern)
- Added §4.3: DNS TXT record discovery at `_aci.<domain>`
- Added §4.4: Discovery resolution order priority chain
