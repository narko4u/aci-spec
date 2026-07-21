#!/usr/bin/env python3
"""ACI Validator — Validate Autonomous Company Interface implementations.

Schemas are loaded from bundled package data (aci_validator/schemas/*.yaml).

Usage:
    aci-validate https://example.com
    aci-validate https://example.com --verbose
    aci-validate https://example.com --json
"""

import json
import sys
import urllib.request
import urllib.error
import urllib.parse
import ssl
import re
from pathlib import Path
from typing import Optional

import yaml

VERSION = "0.9.0"
SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


# ── Dynamic Schema Loading ────────────────────────────────────

def load_schemas(schema_dir: Path) -> tuple[dict, list]:
    """Load all manifest schemas from schema/*.yaml files."""
    schemas = {}
    order = []

    # Mapping from schema filename stem to manifest key
    key_map = {
        "identity": "identity",
        "capability": "capability",
        "knowledge": "knowledge",
        "trust": "trust",
        "agents": "agents",
    }

    # Preferred load order (alphabetically from filename)
    preferred = ["identity", "capability", "knowledge", "trust", "agents"]

    for stem in preferred:
        path = schema_dir / f"{stem}.yaml"
        if path.exists():
            with open(path, "r") as f:
                data = yaml.safe_load(f)
            if data:
                schemas[key_map[stem]] = data
                order.append(key_map[stem])
        else:
            # Try alternative filenames
            for fpath in sorted(schema_dir.glob("*.yaml")):
                data = yaml.safe_load(fpath.read_text())
                if data:
                    stem_guess = fpath.stem
                    mtype = key_map.get(stem_guess, stem_guess)
                    if mtype not in schemas:
                        schemas[mtype] = data
                        order.append(mtype)

    return schemas, order


MANIFEST_TYPES, MANIFEST_ORDER = load_schemas(SCHEMA_DIR)

# Fallback if no schemas loaded (should not happen with default install)
if not MANIFEST_TYPES:
    MANIFEST_TYPES = {
        "identity": {
            "required": ["manifest_version", "last_updated", "publisher", "identifiers"],
            "optional": ["jurisdiction", "registration_number", "website", "contact",
                         "social", "brand", "description", "schema_version"],
            "label": "Identity Manifest",
            "url_hints": ["identity", "company"],
        },
        "capability": {
            "required": ["manifest_version", "last_updated", "publisher"],
            "optional": ["schema_version", "industries", "pricing_model", "documentation"],
            "label": "Capability Manifest",
            "content_blocks": ["products", "services", "solutions"],
            "url_hints": ["capabilit", "product", "offerings"],
        },
        "knowledge": {
            "required": ["manifest_version", "last_updated", "publisher"],
            "optional": ["schema_version"],
            "label": "Knowledge Manifest",
            "content_blocks": ["concepts"],
            "url_hints": ["knowledge", "ontology", "concepts"],
        },
        "trust": {
            "required": ["manifest_version", "last_updated", "publisher"],
            "optional": ["schema_version", "certifications", "patents", "compliance", "signatures", "history"],
            "label": "Trust Manifest",
            "content_blocks": ["assertions"],
            "url_hints": ["trust", "assurance", "verification"],
        },
        "agents": {
            "required": ["manifest_version", "last_updated", "publisher"],
            "optional": ["schema_version"],
            "label": "Agent Manifest",
            "content_blocks": ["agents"],
            "url_hints": ["agent", "mcp", "agents"],
        },
    }
    MANIFEST_ORDER = ["identity", "capability", "knowledge", "trust", "agents"]


LEVEL_MANIFESTS = {
    1: ["identity", "capability"],
    2: ["identity", "capability", "knowledge", "trust"],
    3: ["identity", "capability", "knowledge", "trust", "agents"],
}


# ── Conformance Level Detection ───────────────────────────────

def detect_conformance_level(present_manifests: set[str]) -> int:
    """Determine the highest conformance level met by present manifests."""
    for level in [3, 2, 1]:
        if present_manifests.issuperset(LEVEL_MANIFESTS[level]):
            return level
    return 0  # Not even Level 1


# ── HTTP Utilities ────────────────────────────────────────────

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(url: str, timeout: int = 15) -> Optional[str]:
    """Fetch a URL and return text content, or None on failure."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": f"ACI-Validator/{VERSION} (Autonomous Company Interface Validator)",
            "Accept": "text/plain,application/json,*/*",
        })
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None


def fetch_json(url: str, timeout: int = 15) -> tuple[Optional[dict], Optional[str]]:
    """Fetch a URL, parse as JSON. Returns (data, error_message)."""
    text = fetch(url, timeout)
    if text is None:
        return None, f"HTTP request failed for {url}"
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, f"Invalid JSON at {url}: {e}"


# ── Discovery ─────────────────────────────────────────────────

def guess_llms_txt(base_url: str) -> str:
    """Given a base URL, return the llms.txt URL."""
    base = base_url.rstrip("/")
    if not base.startswith("http"):
        base = "https://" + base
    return base + "/llms.txt"


def parse_llms_txt(text: str, base_url: str) -> list[str]:
    """Extract URLs from llms.txt that look like manifest files."""
    urls = []
    base = base_url.rstrip("/")
    md_link_re = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        md_matches = md_link_re.findall(line)
        for md_text, md_url in md_matches:
            url = md_url.strip()
            if url.startswith("http://") or url.startswith("https://"):
                if url not in urls:
                    urls.append(url)
            elif url.startswith("/"):
                full = base + url
                if full not in urls:
                    urls.append(full)

        for token in line.split():
            token = token.strip().rstrip(".,:;!?)\"")
            if token.startswith("http://") or token.startswith("https://"):
                if token not in urls:
                    urls.append(token)
    return urls


def classify_manifest(url: str) -> Optional[str]:
    """Guess which manifest type a URL corresponds to based on filename hints."""
    url_lower = url.lower()
    for mtype, schema in MANIFEST_TYPES.items():
        for hint in schema.get("url_hints", []):
            if hint in url_lower:
                return mtype
    return None


# ── Validation ────────────────────────────────────────────────

class ValidateResult:
    def __init__(self, manifest_type: str):
        self.manifest_type = manifest_type
        self.url: Optional[str] = None
        self.exists = False
        self.valid_json = False
        self.required_fields_present = False
        self.missing_required: list[str] = []
        self.has_content_blocks = False
        self.missing_content_blocks: list[str] = []
        self.version_consistent = False
        self.identity_consistent = False
        self.data: Optional[dict] = None
        self.error: Optional[str] = None
        self.warnings: list[str] = []

    @property
    def score(self) -> int:
        if not self.exists:
            return 0
        score = 0
        score += 10  # Exists
        if self.valid_json:
            score += 10
        if self.required_fields_present:
            score += 40
        else:
            score += max(0, 40 - len(self.missing_required) * 10)
        if self.has_content_blocks:
            score += 20
        else:
            score += max(0, 20 - len(self.missing_content_blocks) * 10)
        if self.version_consistent:
            score += 10
        if self.identity_consistent:
            score += 10
        score -= min(len(self.warnings) * 2, 20)
        return max(0, min(score, 100))

    def to_dict(self) -> dict:
        return {
            "manifest_type": self.manifest_type,
            "label": MANIFEST_TYPES[self.manifest_type].get("label", self.manifest_type),
            "url": self.url,
            "exists": self.exists,
            "valid_json": self.valid_json,
            "required_fields_present": self.required_fields_present,
            "missing_required": self.missing_required,
            "has_content_blocks": self.has_content_blocks,
            "missing_content_blocks": self.missing_content_blocks,
            "version_consistent": self.version_consistent,
            "identity_consistent": self.identity_consistent,
            "score": self.score,
            "error": self.error,
            "warnings": self.warnings,
        }


class ACIValidationResult:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.llms_txt_url: Optional[str] = None
        self.llms_txt_found = False
        self.llms_txt_content: Optional[str] = None
        self.manifest_results: dict[str, ValidateResult] = {}
        self.errors: list[str] = []
        self.discovery_chain: list[str] = []
        self.identity_fields: dict[str, str] = {}

        for mtype in MANIFEST_ORDER:
            self.manifest_results[mtype] = ValidateResult(mtype)

    def add_discovered_url(self, manifest_type: str, url: str):
        self.manifest_results[manifest_type].url = url
        self.manifest_results[manifest_type].exists = True
        self.discovery_chain.append(url)

    @property
    def conformance_level(self) -> int:
        present = {m for m in MANIFEST_ORDER if self.manifest_results[m].exists}
        return detect_conformance_level(present)

    @property
    def overall_score(self) -> int:
        scores = [r.score for r in self.manifest_results.values()]
        if not scores:
            return 0
        total = sum(scores)
        all_exist = all(r.exists for r in self.manifest_results.values())
        bonus = 10 if all_exist else 0
        return min(100, total // len(scores) + bonus)

    def to_dict(self) -> dict:
        return {
            "target_url": self.target_url,
            "aci_version": VERSION,
            "conformance_level": self.conformance_level,
            "llms_txt_url": self.llms_txt_url,
            "llms_txt_found": self.llms_txt_found,
            "discovery_chain": self.discovery_chain,
            "manifest_results": {k: v.to_dict() for k, v in self.manifest_results.items()},
            "overall_score": self.overall_score,
            "errors": self.errors,
        }


def validate_aci(target_url: str) -> ACIValidationResult:
    result = ACIValidationResult(target_url)

    # Step 1: Discover manifests via llms.txt
    llms_url = guess_llms_txt(target_url)
    result.llms_txt_url = llms_url
    llms_text = fetch(llms_url)

    manifest_urls: dict[str, str] = {}

    if llms_text is not None:
        result.llms_txt_found = True
        result.llms_txt_content = llms_text[:2000]
        discovered_urls = parse_llms_txt(llms_text, target_url)
        for url in discovered_urls:
            mtype = classify_manifest(url)
            if mtype and mtype not in manifest_urls:
                manifest_urls[mtype] = url
        result.discovery_chain = discovered_urls
    else:
        result.errors.append(f"llms.txt not found at {llms_url}")

    # Step 2: Fallback — try standard filenames for undiscovered manifests
    for mtype in MANIFEST_ORDER:
        schema = MANIFEST_TYPES.get(mtype, {})
        if mtype not in manifest_urls:
            for hint in schema.get("url_hints", []):
                for ext in [".json", ".yaml", ".yml"]:
                    guess_url = target_url.rstrip("/") + f"/{hint}{ext}"
                    text = fetch(guess_url)
                    if text is not None:
                        manifest_urls[mtype] = guess_url
                        break
                if mtype in manifest_urls:
                    break

    # Fallback: /.well-known/ paths
    if len(manifest_urls) == 0 and result.llms_txt_found is False:
        for mtype in MANIFEST_ORDER:
            for ext in [".json", ".yaml"]:
                guess_url = target_url.rstrip("/") + f"/.well-known/{mtype}{ext}"
                text = fetch(guess_url)
                if text is not None:
                    manifest_urls[mtype] = guess_url
                    break
            if mtype in manifest_urls:
                break

    # Step 3: Fetch and validate each manifest
    for mtype in MANIFEST_ORDER:
        res = result.manifest_results[mtype]
        schema = MANIFEST_TYPES.get(mtype, {})

        if mtype not in manifest_urls:
            res.error = "Not discovered"
            continue

        url = manifest_urls[mtype]
        result.add_discovered_url(mtype, url)

        data, error = fetch_json(url)
        if error:
            res.error = error
            continue

        res.valid_json = True
        res.data = data

        # Strip x- extension keys before validation
        stripped = {k: v for k, v in data.items() if not k.startswith("x-")}

        # Check required fields
        missing = []
        for field in schema.get("required", []):
            if field not in stripped:
                missing.append(field)
        res.missing_required = missing
        res.required_fields_present = len(missing) == 0

        # Check content blocks
        missing_blocks = []
        for block in schema.get("content_blocks", []):
            if block not in stripped or not stripped[block]:
                missing_blocks.append(block)
        res.missing_content_blocks = missing_blocks
        res.has_content_blocks = len(missing_blocks) == 0

        # Track identity fields for cross-manifest consistency
        if mtype == "identity":
            result.identity_fields["publisher"] = data.get("publisher", "")
            result.identity_fields["manifest_version"] = data.get("manifest_version", "")
        else:
            if data.get("publisher"):
                if "publisher" not in result.identity_fields:
                    result.identity_fields["publisher"] = data["publisher"]
            if data.get("manifest_version"):
                if "manifest_version" not in result.identity_fields:
                    result.identity_fields["manifest_version"] = data["manifest_version"]

    # Step 4: Cross-manifest consistency checks
    for mtype in MANIFEST_ORDER:
        res = result.manifest_results[mtype]
        if not res.data:
            continue

        # Version consistency
        if result.identity_fields.get("manifest_version"):
            if res.data.get("manifest_version") == result.identity_fields["manifest_version"]:
                res.version_consistent = True
            else:
                res.warnings.append(
                    f"manifest_version differs from identity.json: "
                    f"'{res.data.get('manifest_version')}' vs "
                    f"'{result.identity_fields['manifest_version']}'"
                )

        # Publisher consistency
        if result.identity_fields.get("publisher") and mtype != "identity":
            pub = res.data.get("publisher", "")
            if pub == result.identity_fields["publisher"]:
                res.identity_consistent = True
            else:
                res.warnings.append(
                    f"publisher differs from identity.json: "
                    f"'{pub}' vs '{result.identity_fields['publisher']}'"
                )

    return result


# ── Output Formatting ─────────────────────────────────────────

def format_human(result: ACIValidationResult, verbose: bool = False) -> str:
    lines = []
    lines.append("╔══════════════════════════════════════════════════╗")
    lines.append("║     ACI Validator — v0.9                        ║")
    lines.append("╚══════════════════════════════════════════════════╝")
    lines.append("")
    lines.append(f"  Target:   {result.target_url}")
    lines.append(f"  llms.txt: {'✓ found' if result.llms_txt_found else '✗ not found'}")
    if result.llms_txt_url:
        lines.append(f"            {result.llms_txt_url}")
    lines.append("")

    level = result.conformance_level
    level_label = f"ACI Level {level}" if level > 0 else "ACI Level 0 (not Level 1)"
    lines.append(f"  Conformance: {level_label}")
    if level >= 1:
        lines.append("    Level 1: ✓ Identity + Capability + Discovery")
    else:
        lines.append("    Level 1: ✗ Missing required manifests")
    if level >= 2:
        lines.append("    Level 2: ✓ Knowledge + Trust + Cross-references")
    elif result.manifest_results.get("knowledge", ValidateResult("knowledge")).exists or \
         result.manifest_results.get("trust", ValidateResult("trust")).exists:
        lines.append("    Level 2: ✗ Missing Knowledge or Trust manifest")
    if level >= 3:
        lines.append("    Level 3: ✓ Agent + Score ≥ 90")
    lines.append("")

    if result.discovery_chain:
        lines.append("  Discovery Chain:")
        for url in result.discovery_chain:
            lines.append(f"    → {url}")
        lines.append("")

    lines.append(f"  {'─' * 42}")
    lines.append(f"  {'Manifest':<25} {'Score':>8} {'Status':>12}")
    lines.append(f"  {'─' * 42}")

    for mtype in MANIFEST_ORDER:
        res = result.manifest_results[mtype]
        schema = MANIFEST_TYPES.get(mtype, {})
        label = schema.get("label", mtype.title())
        score_display = f"{res.score}/100" if res.exists else "  N/A"
        status = "✓" if res.exists and res.valid_json and res.required_fields_present else \
                 "!" if res.exists else "✗"
        lines.append(f"  {label:<25} {score_display:>8} {status:>12}")

    lines.append(f"  {'─' * 42}")
    overall = f"{result.overall_score}/100"
    badge = "FULL COMPLIANCE" if result.overall_score >= 90 else \
            "PARTIAL" if result.overall_score >= 70 else \
            "MINIMAL" if result.overall_score >= 50 else "NON-COMPLIANT"
    lines.append(f"  {'OVERALL':<25} {overall:>8} {badge:>12}")
    lines.append("")

    if verbose:
        for mtype in MANIFEST_ORDER:
            res = result.manifest_results[mtype]
            schema = MANIFEST_TYPES.get(mtype) or {}
            label = schema.get("label", mtype.title())
            if not res.exists:
                lines.append(f"  [{mtype}] ✗ Not discovered ({label})")
                continue
            lines.append(f"  [{mtype}] {res.url} ({label})")
            if res.error:
                lines.append(f"         ✗ {res.error}")
                continue
            lines.append(f"         JSON: {'✓' if res.valid_json else '✗'}")
            if res.missing_required:
                lines.append(f"         Missing required: {', '.join(res.missing_required)}")
            else:
                lines.append(f"         Required fields: ✓")
            if res.missing_content_blocks:
                lines.append(f"         Missing content blocks: {', '.join(res.missing_content_blocks)}")
            else:
                lines.append(f"         Content blocks: ✓")
            lines.append(f"         Versioning: {'✓' if res.version_consistent else '!'}")
            lines.append(f"         Identity: {'✓' if res.identity_consistent else '!'}")
            if res.warnings:
                for w in res.warnings:
                    lines.append(f"         ⚠ {w}")
            lines.append("")

    if result.errors:
        lines.append("  Errors:")
        for e in result.errors:
            lines.append(f"    ✗ {e}")
        lines.append("")

    return "\n".join(lines)


def format_json(result: ACIValidationResult) -> str:
    return json.dumps(result.to_dict(), indent=2)


# ── Main ──────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="ACI Validator — Validate Autonomous Company Interface implementations"
    )
    parser.add_argument("url", help="Organization URL to validate (e.g., https://empirelabs.com.au)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed per-manifest results")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON (machine-readable)")
    args = parser.parse_args()

    target_url = args.url.rstrip("/")
    if not target_url.startswith("http"):
        target_url = "https://" + target_url

    print(f"Validating ACI implementation at {target_url}...", file=sys.stderr)
    result = validate_aci(target_url)

    if args.json:
        print(format_json(result))
    else:
        print(format_human(result, verbose=args.verbose))

    sys.exit(0 if result.overall_score >= 70 else 1)


if __name__ == "__main__":
    main()
