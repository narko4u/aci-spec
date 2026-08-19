# Testing Policy

This document defines **when** tests run and **what is required** of every
change that touches functional code in this repository. It is normative: the
CI pipeline enforces the automated portion, and maintainers enforce the
policy portion during review.

## When tests run

1. **Every pull request** — the `CI` workflow runs the full validation
   matrix on Python 3.10, 3.11 and 3.12 (see
   [`.github/workflows/ci.yml`](.github/workflows/ci.yml)). A PR that
   breaks CI cannot be merged.
2. **Every push to `main`** — the same `CI` workflow runs again.
3. **Locally, before opening a PR** — contributors are expected to run the
   same checks described in
   [CONTRIBUTING.md](CONTRIBUTING.md#running-tests) before requesting
   review.
4. **Before every release** — the `Release` workflow (see
   [`.github/workflows/release.yml`](.github/workflows/release.yml)) only
   runs on a tag; it builds the distributable and generates the SBOM, and
   the tag is created from a `main` commit that already passed CI.

## What the test suite covers

The repository does not ship a unit-test harness; correctness is enforced
by **schema and example validation** plus **CLI smoke tests**, which run in
CI:

- All example manifests under `examples/` must parse as valid JSON.
- All schemas under `schema/` must load, and the five core manifest types
  (`identity`, `capability`, `knowledge`, `trust`, `agents`) must be
  present.
- The `aci-validate` and `aci-explore` CLI entry points must load.

Run the same checks locally:

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

## Policy for major changes

> **Any significant change MUST add or update automated tests or validation
> coverage in the same PR.**

For this project, that means:

- A change to the **specification** MUST update the affected examples under
  `examples/` (or add a new one) so the change is exercised by CI
  validation.
- A change to the **schemas** MUST add or update at least one example
  manifest that validates against the new schema.
- A change to the **validator or CLI tools** MUST add or update a schema or
  example that exercises the changed behaviour, and MUST keep the existing
  validation checks green.

Trivial changes (typos, formatting, documentation-only edits) are exempt,
at the maintainer's discretion — but a PR that touches functional code
without updating validation coverage will be blocked in review.

## Enforcement

- CI failing = merge blocked (branch protection requires the `validate`
  check).
- Policy not followed = review comment, PR returned to author.
- Reviewers MUST verify the PR description states which validation
  coverage was added or updated.
