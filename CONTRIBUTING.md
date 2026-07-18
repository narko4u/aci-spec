# Contributing to ACI

**Version 0.9 (Draft)**

> How to propose changes, report issues, and participate.

---

## Ways to Contribute

### Report a Bug or Issue

If you find a problem with the specification — an inconsistency, a missing edge
case, or something that doesn't make sense — open an issue in the aci-spec
repository. Include:

- The section and version affected
- What you expected
- What actually happens or reads wrong
- If applicable, what implementation you were building

### Propose a Change

Changes to the specification follow the Change Process (see CHANGE_PROCESS.md).
In brief:

1. Open an issue describing the proposed change
2. Discuss with the community and steward
3. If the change is non-breaking, submit a pull request or RFC
4. For breaking changes, a formal RFC and review period is required

### Submit an Implementation

Adding your organization to the ACI Adopters list helps demonstrate that the
specification is implementable. To register:

1. Ensure your implementation passes the ACI Validator
2. Open a pull request adding your organization to the adopters list (see ADOPTERS.md)
3. Include the validator output showing your score

### Improve Documentation

Editorial improvements — better examples, clearer language, fixed typos — are
always welcome. Submit a pull request with a clear description of what changed
and why.

---

## Pull Request Guidelines

- Keep changes focused. One PR per logical change.
- Reference the related issue or RFC in the PR description.
- For spec changes, update both the specification text and Appendix A examples
  if applicable.
- Ensure the ACI Validator still passes on the reference implementation.
- Do not change normative content without prior discussion.

---

## Code of Conduct

All participants SHALL follow the Code of Conduct (see CODE_OF_CONDUCT.md).
Be respectful, constructive, and assume good faith.
