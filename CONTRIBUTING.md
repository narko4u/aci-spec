# Contributing to ACI

**Version 0.9 (Draft)**

> How to propose changes, report issues, and participate.

---

## Ways to Contribute

### Report a Bug or Issue

If you find a problem with the specification - an inconsistency, a missing edge
case, or something that doesn't make sense - open an issue in the aci-spec
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

Editorial improvements - better examples, clearer language, fixed typos - are
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

## Running tests

Validation runs automatically on **every pull request and every push to
`main`** via the `CI` workflow
([`.github/workflows/ci.yml`](.github/workflows/ci.yml)), across Python
3.10, 3.11 and 3.12. The suite covers:

- All example manifests under `examples/` parse as valid JSON
- All schemas under `schema/` load, including the five core manifest types
- The `aci-validate` and `aci-explore` CLI entry points load

Run the same checks locally before opening a PR:

```sh
python -m pip install -e .
aci-validate --help >/dev/null
aci-explore --help >/dev/null
python - <<'EOF'
import json, glob
from aci_validator.validate import load_schemas, SCHEMA_DIR
schemas, order = load_schemas(SCHEMA_DIR)
assert set(order) >= {"identity", "capability", "knowledge", "trust", "agents"}, order
files = glob.glob("examples/**/*.json", recursive=True)
assert files, "no example JSON files found"
for f in files:
    json.load(open(f))
print(f"OK: {len(files)} example manifests valid")
EOF
```

The full policy — when tests run, what the suite covers, and the
requirement that major changes add or update validation coverage — is
documented in [TESTING.md](TESTING.md).

---

## Code of Conduct

All participants SHALL follow the Code of Conduct (see CODE_OF_CONDUCT.md).
Be respectful, constructive, and assume good faith.
