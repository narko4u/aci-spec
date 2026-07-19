#!/usr/bin/env python3
"""
|ACI Explorer — CLI demo of Autonomous Company Interface discovery in action.

Usage:
    python3 aci-explorer.py example.com
    python3 aci-explorer.py https://example.com
    python3 aci-explorer.py https://novadynamics.example:8000

Given a domain, this tool:
  1. Checks /llms.txt for autonomous agent manifest links
  2. Fetches identity.json (the foundation manifest)
  3. Follows all discovery links to find every ACI manifest
  4. Builds a complete organizational profile
  5. Displays it in a clean, formatted output

Requires: Python 3.7+ (stdlib only — urllib, json, sys)
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# ── ANSI colour helpers ──────────────────────────────────────────

_COLORS = {
    "green": "\033[92m",
    "cyan": "\033[96m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}


def _c(name, text):
    """Wrap text in an ANSI colour code, resetting after."""
    return f"{_COLORS[name]}{text}{_COLORS['reset']}"


PASS = _c("green", "✓")
FAIL = _c("red", "✗")
SKIP = _c("yellow", "→")

# ── HTTP helpers ─────────────────────────────────────────────────


def _guess_llms_url(target):
    """Given a URL or bare domain, return the full /llms.txt URL."""
    target = target.strip()
    if not target.startswith("http"):
        target = "https://" + target
    parsed = urllib.parse.urlparse(target)
    # If the user gave https://example.com/path, use the origin
    base = f"{parsed.scheme}://{parsed.netloc}"
    return base.rstrip("/") + "/llms.txt", base


def _fetch(url, timeout=15):
    """Fetch a URL and return (text_content, status_code, error_string)."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ACI-Explorer/1.0 (ACI Demo Tool)",
            "Accept": "application/json, text/plain, */*",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            # Try UTF-8 first, then let chardet-less Python guess
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1")
            return text, resp.status, None
    except urllib.error.HTTPError as exc:
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return body, exc.code, f"HTTP {exc.code} {exc.reason}"
    except urllib.error.URLError as exc:
        return "", 0, f"Connection failed: {exc.reason}"
    except OSError as exc:
        return "", 0, str(exc)


# ── llms.txt parsing ────────────────────────────────────────────


def _parse_llms_links(text, base_url):
    """Extract manifest URLs from an llms.txt file."""
    urls = []
    md_link_re = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
    base = base_url.rstrip("/")

    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Markdown links: [text](url)
        for md_text, md_url in md_link_re.findall(line):
            url = md_url.strip()
            resolved = _resolve_url(url, base)
            if resolved and resolved not in urls:
                urls.append(resolved)

        # Bare HTTP(S) tokens
        for token in line.split():
            token = token.strip().rstrip(".,:;!?)\"'")
            if token.startswith(("http://", "https://")):
                if token not in urls:
                    urls.append(token)

    return urls


def _resolve_url(url, base):
    """Resolve a potentially-relative URL against base."""
    url = url.strip()
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("/"):
        return base + url
    # relative path — resolve against base
    return base.rstrip("/") + "/" + url.lstrip("./")


def _classify_manifest(url, body):
    """Determine which manifest type a URL/body corresponds to."""
    url_lower = url.lower()
    hints = {
        "identity": ["identity", "identity.json"],
        "capability": ["capability", "capabilities", "capabilities.json"],
        "knowledge": ["knowledge", "knowledge.json"],
        "trust": ["trust", "trust.json"],
        "agents": ["agent", "agents.json"],
    }
    for mtype, patterns in hints.items():
        for p in patterns:
            if p in url_lower:
                return mtype

    # Fallback: peek at JSON content for a distinguishing field
    if body:
        try:
            data = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            return "unknown"
        if "identifiers" in data:
            return "identity"
        if "products" in data or "services" in data:
            return "capability"
        if "concepts" in data:
            return "knowledge"
        if "assertions" in data or "certifications" in data:
            return "trust"
        if "agents" in data:
            return "agents"
    return "unknown"


def _is_manifest_url(url):
    """Check if a URL looks like it could be an ACI manifest endpoint."""
    url_lower = url.lower()
    manifest_hints = ["identity", "capabilit", "knowledge", "trust", "agent", "manifest"]
    # Must be JSON or look like a manifest path
    path = urllib.parse.urlparse(url_lower).path
    if path.endswith(".json"):
        return True
    for hint in manifest_hints:
        if hint in path:
            return True
    return False


# ── Manifest fetching & discovery chain ─────────────────────────


def _fetch_json(url):
    """Fetch a URL and parse as JSON.  Returns (dict|list|None, error_str)."""
    text, status, err = _fetch(url)
    if err:
        return None, err
    if status != 200:
        return None, f"HTTP {status}"
    try:
        return json.loads(text), None
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"Invalid JSON: {exc}"


def _extract_discovery_urls(data):
    """Extract all URLs from a manifest's 'discovery' field (or similar fields)."""
    urls = set()
    if not isinstance(data, dict):
        return urls

    # Discovery object with named links (only follow discovery, not documentation)
    disc = data.get("discovery", {})
    if isinstance(disc, dict):
        for key, val in disc.items():
            if isinstance(val, str) and val.startswith("http"):
                urls.add(val)

    return urls


# ── Formatting / Display ────────────────────────────────────────


def _fmt_header(text):
    width = 72
    side = (width - len(text) - 2) // 2
    return f"\n{'═' * side} {_c('bold', text)} {'═' * (width - side - len(text) - 2)}"


def _fmt_subheader(text):
    return f"\n{_c('cyan', '──')} {_c('bold', text)}"


def _fmt_kv(key, value, indent=0):
    pad = "  " * indent
    return f"{pad}{_c('dim', key)}: {value}"


def _fmt_list(items, indent=1):
    """Format a list of items as a bullet list."""
    pad = "  " * indent
    return "\n".join(f"{pad}{_c('yellow', '•')} {item}" for item in items)


def _fmt_dict(data, indent=1, skip_keys=None):
    """Format a flat dict as key: value lines."""
    skip_keys = skip_keys or set()
    pad = "  " * indent
    lines = []
    for key, val in data.items():
        if key in skip_keys:
            continue
        if isinstance(val, dict):
            lines.append(f"{pad}{_c('dim', key)}:")
            for k, v in val.items():
                lines.append(f"{pad}  {_c('dim', k)}: {v}")
        elif isinstance(val, list):
            items = [str(v) if not isinstance(v, dict) else v.get("name", v.get("id", str(v))) for v in val]
            lines.append(f"{pad}{_c('dim', key)}: {'; '.join(items)}")
        elif isinstance(val, bool):
            lines.append(f"{pad}{_c('dim', key)}: {_c('green', 'yes') if val else _c('red', 'no')}")
        elif val is None:
            lines.append(f"{pad}{_c('dim', key)}: {_c('dim', '(not set)')}")
        else:
            lines.append(f"{pad}{_c('dim', key)}: {val}")
    return "\n".join(lines)


# ── Manifest display helpers ────────────────────────────────────


def show_identity(data, url):
    """Display the identity manifest."""
    print(_fmt_subheader(f"Identity Manifest"))
    print(f"  {_c('dim', 'URL')}: {_c('cyan', url)}")

    org = data.get("publisher", "Unknown Organization")
    brand = data.get("brand", "")
    desc = data.get("description", "")
    website = data.get("website", "")
    contact = data.get("contact", "")
    jurisdiction = data.get("jurisdiction", "")
    reg_no = data.get("registration_number", "")
    version = data.get("manifest_version", "")

    print(f"  {_c('bold', org)}{f' ({brand})' if brand else ''}")
    if desc:
        print(f"  {desc}")
    if website:
        print(f"  {_fmt_kv('Website', _c('blue', website))}")
    if contact:
        print(f"  {_fmt_kv('Contact', contact)}")
    if jurisdiction:
        print(f"  {_fmt_kv('Jurisdiction', jurisdiction)}")
    if reg_no:
        print(f"  {_fmt_kv('Registration', reg_no)}")
    if version:
        print(f"  {_fmt_kv('Manifest Version', version)}")

    # Identifiers
    ids = data.get("identifiers", [])
    if ids:
        id_strs = []
        for ident in ids:
            if isinstance(ident, dict):
                id_strs.append(f"{ident.get('type', '?')}:{ident.get('value', '?')}")
            else:
                id_strs.append(str(ident))
        print(f"  {_c('dim', 'Identifiers')}: {', '.join(id_strs)}")


def show_capabilities(data, url):
    """Display the capability manifest."""
    print(_fmt_subheader("Capability Manifest"))
    print(f"  {_c('dim', 'URL')}: {_c('cyan', url)}")

    version = data.get("manifest_version", "")
    publisher = data.get("publisher", "")
    if publisher:
        print(f"  {_c('dim', 'Publisher')}: {publisher}")
    if version:
        print(f"  {_c('dim', 'Version')}: {version}")

    # Products
    products = data.get("products", [])
    if products:
        print(f"  {_c('bold', 'Products')}:")
        for prod in products:
            name = prod.get("name", prod.get("id", "?"))
            ptype = prod.get("type", "")
            pdesc = prod.get("description", "")
            print(f"    {_c('yellow', '•')} {_c('bold', name)}")
            if ptype:
                print(f"       Type: {ptype}")
            if pdesc:
                print(f"       {pdesc}")

    # Services
    services = data.get("services", [])
    if services:
        print(f"  {_c('bold', 'Services')}:")
        for svc in services:
            name = svc.get("name", svc.get("id", "?"))
            sdesc = svc.get("description", "")
            print(f"    {_c('yellow', '•')} {_c('bold', name)}")
            if sdesc:
                print(f"       {sdesc}")

    # Solutions
    solutions = data.get("solutions", [])
    if solutions:
        print(f"  {_c('bold', 'Solutions')}:")
        for sol in solutions:
            name = sol.get("name", sol.get("id", "?"))
            sdesc = sol.get("description", "")
            print(f"    {_c('yellow', '•')} {_c('bold', name)}")
            if sdesc:
                print(f"       {sdesc}")

    # Industries
    industries = data.get("industries", [])
    if industries:
        print(f"  {_c('dim', 'Industries')}: {', '.join(industries)}")

    # Pricing
    pricing = data.get("pricing_model", "")
    if pricing:
        print(f"  {_c('dim', 'Pricing')}: {pricing}")

    # Documentation links
    docs = data.get("documentation", {})
    if docs:
        print(f"  {_c('dim', 'Documentation')}:")
        for key, val in docs.items():
            if isinstance(val, str) and val.startswith("http"):
                print(f"    {_c('dim', key)}: {_c('blue', val)}")


def show_knowledge(data, url):
    """Display the knowledge manifest."""
    print(_fmt_subheader("Knowledge Manifest"))
    print(f"  {_c('dim', 'URL')}: {_c('cyan', url)}")

    domain = data.get("domain", "")
    domain_label = data.get("domain_label", "")
    if domain:
        print(f"  {_c('dim', 'Domain')}: {domain}{f' ({domain_label})' if domain_label else ''}")

    concepts = data.get("concepts", [])
    if concepts:
        print(f"  {_c('bold', 'Concepts')} ({len(concepts)}):")
        for cpt in concepts:
            name = cpt.get("name", cpt.get("id", "?"))
            cdesc = cpt.get("description", "")
            cid = cpt.get("id", "")
            print(f"    {_c('yellow', '•')} {_c('bold', name)}")
            if cid:
                print(f"       ID: {_c('dim', cid)}")
            if cdesc:
                print(f"       {cdesc}")

    # Relationships
    rels = data.get("relationships", [])
    if rels:
        print(f"  {_c('bold', 'Relationships')} ({len(rels)}):")
        for rel in rels:
            s = rel.get("source", "?")
            r = rel.get("relation", "?")
            t = rel.get("target", "?")
            print(f"    {_c('yellow', '•')} {s}  {_c('cyan', r)}  {t}")


def show_trust(data, url):
    """Display the trust manifest."""
    print(_fmt_subheader("Trust Manifest"))
    print(f"  {_c('dim', 'URL')}: {_c('cyan', url)}")

    assertions = data.get("assertions", [])
    if assertions:
        print(f"  {_c('bold', 'Assertions')}:")
        for a in assertions:
            atype = a.get("type", "?")
            aclaim = a.get("claims", "")
            astatus = a.get("status", "")
            evidence = a.get("evidence", "")
            status_color = _c("green", astatus) if astatus == "active" else _c("yellow", astatus)
            print(f"    {_c('yellow', '•')} [{atype}] {status_color}")
            if aclaim:
                print(f"       {aclaim}")
            if evidence:
                print(f"       Evidence: {_c('blue', evidence)}")

    certs = data.get("certifications", [])
    if certs:
        print(f"  {_c('bold', 'Certifications')}:")
        for cert in certs:
            name = cert.get("name", "?")
            issuer = cert.get("issuer", "")
            cstatus = cert.get("status", "")
            status_color = _c("green", cstatus) if cstatus == "active" else _c("yellow", cstatus)
            print(f"    {_c('yellow', '•')} {_c('bold', name)} — {status_color}")
            if issuer:
                print(f"       Issuer: {issuer}")

    sec = data.get("security", {})
    if sec:
        print(f"  {_c('bold', 'Security')}:")
        disclosure = sec.get("disclosure", "")
        policy = sec.get("policy", "")
        if disclosure:
            print(f"    {_c('dim', 'Disclosure')}: {disclosure}")
        if policy:
            print(f"    {policy}")


def show_agents(data, url):
    """Display the agents manifest."""
    print(_fmt_subheader("Agents Manifest"))
    print(f"  {_c('dim', 'URL')}: {_c('cyan', url)}")

    agents_list = data.get("agents", [])
    if not agents_list:
        print(f"  {_c('yellow', '(no agents declared)')}")
        return

    for agent in agents_list:
        name = agent.get("name", agent.get("id", "?"))
        aid = agent.get("id", "")
        atype = agent.get("type", "")
        adesc = agent.get("description", "")
        status = agent.get("status", "")
        auth = agent.get("authentication", "")

        status_color = _c("green", status) if status == "active" else _c("yellow", status)
        print(f"\n    {_c('yellow', '•')} {_c('bold', name)}  [{status_color}]")
        if aid:
            print(f"       ID: {_c('dim', aid)}")
        if atype:
            print(f"       Type: {atype}")
        if adesc:
            print(f"       {adesc}")
        if auth:
            print(f"       {_c('dim', 'Auth')}: {auth}")

        caps = agent.get("capabilities", [])
        if caps:
            print(f"       {_c('dim', 'Capabilities')}: {', '.join(caps)}")

        endpoints = agent.get("endpoints", [])
        if endpoints:
            print(f"       {_c('dim', 'Endpoints')}:")
            for ep in endpoints:
                ename = ep.get("name", "")
                eurl = ep.get("url", "")
                emethod = ep.get("method", "")
                print(f"         {_c('cyan', emethod or '?')}  {eurl}  {_c('dim', ename)}")


# ── Main discovery & display pipeline ───────────────────────────

MANIFEST_DISPLAY = {
    "identity": show_identity,
    "capability": show_capabilities,
    "knowledge": show_knowledge,
    "trust": show_trust,
    "agents": show_agents,
}

MANIFEST_NAMES = {
    "identity": "Identity",
    "capability": "Capability",
    "knowledge": "Knowledge",
    "trust": "Trust",
    "agents": "Agents",
}


def discover_and_display(target):
    """Main pipeline: discover manifests and display the organisational profile."""
    print()
    print(_c("bold", "  ╔══════════════════════════════════════════════════════════╗"))
    print(_c("bold", "  ║           ACI Explorer — Organisational Profile          ║"))
    print(_c("bold", "  ║    Autonomous Company Interface Discovery in Action      ║"))
    print(_c("bold", "  ╚══════════════════════════════════════════════════════════╝"))
    print()

    # ── Step 1: Resolve target ──────────────────────────────────
    print(f"  {_c('bold', 'Step 1:')} Resolving target...")
    llms_url, base_url = _guess_llms_url(target)
    print(f"    {_c('dim', 'Target')}: {_c('cyan', target)}")
    print(f"    {_c('dim', 'Base')}: {_c('cyan', base_url)}")
    print(f"    {_c('dim', 'llms.txt')}: {_c('cyan', llms_url)}")
    print()

    # ── Step 2: Fetch llms.txt ──────────────────────────────────
    print(f"  {_c('bold', 'Step 2:')} Fetching {_c('cyan', '/llms.txt')} for manifest links...")
    llms_text, llms_status, llms_err = _fetch(llms_url)
    discovered_urls = []
    llms_found = False

    if llms_err or llms_status != 200:
        print(f"    {FAIL}  llms.txt: {llms_err or f'HTTP {llms_status}'}")
        print(f"    {SKIP}  Proceeding to try common manifest URLs directly...")
    else:
        llms_found = True
        print(f"    {PASS}  llms.txt found ({len(llms_text)} bytes)")
        discovered_urls = _parse_llms_links(llms_text, base_url)
        if discovered_urls:
            print(f"    {PASS}  Found {len(discovered_urls)} manifest link(s) in llms.txt")
            for u in discovered_urls:
                mtype = _classify_manifest(u, None)
                label = MANIFEST_NAMES.get(mtype, mtype)
                print(f"           {_c('yellow', '→')} [{label}] {u}")
        else:
            print(f"    {SKIP}  No manifest links found in llms.txt")
    print()

    # ── Step 3: Find & fetch identity manifest ──────────────────
    print(f"  {_c('bold', 'Step 3:')} Locating Identity Manifest...")
    identity_url = None
    identity_data = None

    # Look through discovered URLs for identity
    for u in discovered_urls:
        if _classify_manifest(u, None) == "identity":
            identity_url = u
            break

    # If not found, try common locations (with shorter timeout)
    if not identity_url:
        candidates = [
            base_url + "/identity.json",
            base_url + "/.well-known/identity.json",
            base_url + "/.well-known/aci/identity.json",
            base_url + "/aci/identity.json",
        ]
        for cand in candidates:
            body, status, err = _fetch(cand, timeout=5)
            if status == 200 and body:
                try:
                    data = json.loads(body)
                    if isinstance(data, dict) and "identifiers" in data:
                        identity_url = cand
                        identity_data = data
                        break
                except (json.JSONDecodeError, ValueError):
                    continue

    if not identity_url:
        print(f"    {FAIL}  Could not locate identity manifest")
        print(f"    {SKIP}  Cannot proceed without identity manifest. Exiting.")
        return

    if not identity_data:
        identity_data, id_err = _fetch_json(identity_url)
        if id_err or not identity_data:
            print(f"    {FAIL}  Failed to fetch identity manifest: {id_err}")
            return

    print(f"    {PASS}  Identity Manifest found at {_c('cyan', identity_url)}")
    print(f"    {_c('dim', 'Organization')}: {identity_data.get('publisher', '?')}")
    print()

    # ── Step 4: Follow discovery chain ──────────────────────────
    print(f"  {_c('bold', 'Step 4:')} Following discovery links to find all manifests...")
    all_manifest_urls = {identity_url}
    all_manifest_data = {}
    manifest_queue = [("identity", identity_url, identity_data)]
    target_host = urllib.parse.urlparse(base_url).netloc

    # Build an initial set from identity.json's discovery field
    disc_urls = _extract_discovery_urls(identity_data)
    for du in disc_urls:
        all_manifest_urls.add(du)

    # Also include all already-discovered URLs from llms.txt (filter to manifest-like URLs only)
    for u in discovered_urls:
        if _is_manifest_url(u) or urllib.parse.urlparse(u).netloc != target_host:
            all_manifest_urls.add(u)

    # Fetch all discovered manifests (iterate over a snapshot to avoid set mutation)
    pending = list(all_manifest_urls)
    fetched_in_pass = set()
    while pending:
        murl = pending.pop(0)
        if murl in all_manifest_data:
            continue
        mtype = _classify_manifest(murl, None)
        if murl == identity_url:
            all_manifest_data[identity_url] = identity_data
            continue
        data, err = _fetch_json(murl)
        if data and not err:
            all_manifest_data[murl] = data
            all_manifest_urls.discard(murl)  # mark as processed
            print(f"    {PASS}  [{MANIFEST_NAMES.get(mtype, mtype)}] {_c('cyan', murl)}")
            # Follow any discovery links in this manifest too
            more = _extract_discovery_urls(data)
            for mu in more:
                if mu not in all_manifest_data and mu not in fetched_in_pass:
                    fetched_in_pass.add(mu)
                    all_manifest_urls.add(mu)
                    mtype2 = _classify_manifest(mu, None)
                    data2, err2 = _fetch_json(mu)
                    if data2 and not err2:
                        all_manifest_data[mu] = data2
                        print(f"    {PASS}  [{MANIFEST_NAMES.get(mtype2, mtype2)}] {_c('cyan', mu)}")
                    elif err2:
                        # Only print failures for primary-domain URLs, skip external cross-references silently
                        mu_host = urllib.parse.urlparse(mu).netloc
                        if mu_host == target_host:
                            print(f"    {SKIP}  [{mtype2}] {_c('dim', mu)} ({err2})")
        elif err:
            # Quietly skip cross-references to external domains
            murl_host = urllib.parse.urlparse(murl).netloc
            if murl_host == target_host:
                print(f"    {SKIP}  [{mtype}] {_c('dim', murl)} ({err})")

    print()

    # ── Step 5: Build & display organisational profile ──────────
    print(_c("bold", "  ╔══════════════════════════════════════════════════════════╗"))
    print(_c("bold", "  ║           ORGANISATIONAL PROFILE                        ║"))
    print(_c("bold", "  ╚══════════════════════════════════════════════════════════╝"))
    print()

    # Summary header
    org_name = identity_data.get("publisher", "Unknown")
    org_brand = identity_data.get("brand", "")
    print(f"  {_c('bold', org_name)}{f' ({org_brand})' if org_brand else ''}")
    if identity_data.get("description"):
        print(f"  {identity_data['description']}")
    print()

    # Conformance level
    manifest_types_found = set()
    for murl, mdata in all_manifest_data.items():
        mtype = _classify_manifest(murl, json.dumps(mdata) if mdata else None)
        manifest_types_found.add(mtype)

    has_identity = "identity" in manifest_types_found
    has_capability = "capability" in manifest_types_found
    has_knowledge = "knowledge" in manifest_types_found
    has_trust = "trust" in manifest_types_found
    has_agents = "agents" in manifest_types_found

    manifest_count = len([t for t in ["identity","capability","knowledge","trust","agents"] if t in manifest_types_found])
    print(f"  {_c('dim', 'Manifest coverage')}: {manifest_count}/5")
    if manifest_count == 5:
        print(f"  {_c('dim', 'Detected profile')}: {_c('bold', 'Level 3 candidate')}")
        val_url = base_url
        print(f"  {_c('dim', 'Formal conformance')}: run {_c('cyan', 'python validator/validate.py ' + val_url)}")
    elif has_knowledge and has_trust:
        print(f"  {_c('dim', 'Detected profile')}: {_c('bold', 'Level 2 candidate')}")
    elif has_capability:
        print(f"  {_c('dim', 'Detected profile')}: {_c('bold', 'Level 1 candidate')}")
    print(f"  {_c('dim', 'Manifests fetched')}: {len(all_manifest_data)}")
    # failed_list will be defined later; skip external ref count here
    print()

    # Manifest checklist
    print(f"  {_c('bold', 'Manifest Checklist')}:")
    for mtype, mname in [("identity", "Identity"), ("capability", "Capability"),
                          ("knowledge", "Knowledge"), ("trust", "Trust"),
                          ("agents", "Agents")]:
        present = mtype in manifest_types_found
        icon = PASS if present else FAIL
        print(f"    {icon} {mname}")
    print()

    # Display each manifest
    for mtype, display_fn in [
        ("identity", show_identity),
        ("capability", show_capabilities),
        ("knowledge", show_knowledge),
        ("trust", show_trust),
        ("agents", show_agents),
    ]:
        for murl, mdata in all_manifest_data.items():
            if _classify_manifest(murl, json.dumps(mdata) if mdata else None) == mtype and mdata:
                display_fn(mdata, murl)
                print()

    # ── Discovery chain summary ─────────────────────────────────
    print(_c("bold", "  ╔══════════════════════════════════════════════════════════╗"))
    print(_c("bold", "  ║           DISCOVERY CHAIN                               ║"))
    print(_c("bold", "  ╚══════════════════════════════════════════════════════════╝"))
    print()

    print(f"  {_c('cyan', llms_url)}" if llms_found else f"  {_c('dim', llms_url + ' (not found)')}")
    fetched_list = [(u, d) for u, d in all_manifest_data.items() if d is not None]
    failed_list = [u for u in all_manifest_urls if u not in all_manifest_data]

    # Sort: identity first, then by type name
    def _sort_key(item):
        mtype = _classify_manifest(item[0], json.dumps(item[1]) if item[1] else None)
        order = {"identity": 0, "capability": 1, "knowledge": 2, "trust": 3, "agents": 4}
        return (order.get(mtype, 99), item[0])

    fetched_list.sort(key=_sort_key)

    # Show successful fetches in a tree
    total = len(fetched_list)
    for i, (murl, mdata) in enumerate(fetched_list):
        mtype = _classify_manifest(murl, json.dumps(mdata) if mdata else None)
        label = MANIFEST_NAMES.get(mtype, mtype)
        is_last = (i == total - 1)
        if is_last and not failed_list:
            prefix = "  └──"
        elif is_last and failed_list:
            prefix = "  ├──"  # more items below (the failed list)
        else:
            prefix = "  ├──"
        print(f"  {prefix} {_c('green', '✓')} {_c('dim', f'[{label}]')} {_c('cyan', murl)}")

    # Show failed external cross-references compactly
    if failed_list:
        print(f"  └── {_c('yellow', '…')} {_c('dim', f'{len(failed_list)} unresolved external cross-references')}")
        for fu in failed_list:
            mtype = _classify_manifest(fu, None)
            label = MANIFEST_NAMES.get(mtype, mtype)
            print(f"          {_c('dim', f'[{label}]')} {_c('dim', fu)} ({_c('yellow', 'unreachable')})")

    # ── Discovery statistics ────────────────────────────────────
    print()
    print(f"  {_c('bold', 'Summary')}:")
    print(f"    {_c('dim', 'Domain')}: {_c('cyan', base_url)}")
    print(f"    {_c('dim', 'llms.txt')}: {'Found' if llms_found else 'Not found'}")
    print(f"    {_c('dim', 'Manifests discovered')}: {len(all_manifest_urls)} URLs")
    print(f"    {_c('dim', 'Manifests fetched successfully')}: {len(all_manifest_data)} files")
    if failed_list:
        print(f"    {_c('dim', 'External cross-references (unreachable)')}: {len(failed_list)}")
    print(f"    {_c('dim', 'Manifest coverage')}: {manifest_count}/5")
    print()


# ── CLI entry point ─────────────────────────────────────────────


def main():
    if len(sys.argv) < 2:
        print(f"\n  {_c('bold', 'ACI Explorer')} — Discover and display ACI manifests for any domain.")
        print()
        print(f"  {_c('bold', 'Usage')}:")
        print(f"    python3 aci-explorer.py <domain-or-url>")
        print()
        print(f"  {_c('bold', 'Examples')}:")
        print(f"    python3 aci-explorer.py example.com")
        print(f"    python3 aci-explorer.py https://example.com")
        print(f"    python3 aci-explorer.py https://novadynamics.example:8000")
        print()
        sys.exit(1)

    target = sys.argv[1]
    discover_and_display(target)


if __name__ == "__main__":
    main()
