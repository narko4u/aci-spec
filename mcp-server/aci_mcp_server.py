#!/usr/bin/env python3
"""
ACI MCP Server — Exposes ACI validation and discovery as MCP tools.

Safe for HTTP hosting: stateless, no secrets, no side effects.
All tools are pure computation + public HTTP fetches (no auth).

Tools:
  - aci_validate        Validate a URL against the ACI specification
  - aci_discover        Discover ACI manifests for a domain
  - aci_explore         Fetch and display a specific manifest by URL

Usage:
  python aci_mcp_server.py           # stdio mode (for agent configs)
  python aci_mcp_server.py --http    # HTTP mode (safe for remote use)

Copyright (c) 2026 Empire Labs Pty Ltd
SPDX-License-Identifier: MIT
"""

import argparse
import json
import sys
from typing import Any

import anyio
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import (
    Tool,
    TextContent,
    CallToolResult,
)
import mcp.server.stdio


# ── ACI Bridge ──────────────────────────────────────────────────────

def _import_aci():
    """Lazy import aci_validator modules."""
    from aci_validator.validate import validate_aci, VERSION, MANIFEST_ORDER
    import aci_validator.explorer as aci_explorer
    return validate_aci, VERSION, MANIFEST_ORDER, aci_explorer


def _do_validate(url: str) -> dict:
    """Validate a URL against ACI spec. Returns structured result."""
    validate_aci, version, manifest_order, _ = _import_aci()
    try:
        result = validate_aci(url)
        data = result.to_dict()
        data["aci_version"] = version
        return data
    except Exception as e:
        return {
            "target_url": url,
            "error": f"Validation failed: {e}",
            "conformance_level": 0,
            "overall_score": 0,
        }


def _do_discover(url: str) -> dict:
    """Discover ACI manifests for a domain."""
    validate_aci, version, manifest_order, aci_explorer = _import_aci()

    try:
        # Use the explorer's discovery pipeline
        llms_url, base_url = aci_explorer._guess_llms_url(url)
        llms_text, status, err = aci_explorer._fetch(llms_url)

        discovered = {
            "target_url": url,
            "base_url": base_url,
            "llms_txt_url": llms_url,
            "llms_txt_found": llms_text is not None and status == 200,
            "discovered_manifests": [],
            "errors": [],
        }

        if err:
            discovered["errors"].append(f"llms.txt: {err}")

        if llms_text:
            links = aci_explorer._parse_llms_links(llms_text, base_url)
            manifest_urls = {}
            for link in links:
                mtype = aci_explorer._classify_manifest(link, "")
                if mtype and mtype != "unknown" and mtype not in manifest_urls:
                    manifest_urls[mtype] = link

            for mtype, murl in manifest_urls.items():
                discovered["discovered_manifests"].append({
                    "type": mtype,
                    "url": murl,
                })

            # Also show all raw links
            discovered["llms_txt_links"] = links

        return discovered

    except Exception as e:
        return {
            "target_url": url,
            "error": f"Discovery failed: {e}",
            "llms_txt_found": False,
        }


def _do_explore(manifest_url: str) -> dict:
    """Fetch and display a specific manifest."""
    validate_aci, version, manifest_order, aci_explorer = _import_aci()

    try:
        body, status, err = aci_explorer._fetch(manifest_url)
        if err or status != 200:
            return {
                "url": manifest_url,
                "error": err or f"HTTP {status}",
                "found": False,
            }

        data = json.loads(body)
        mtype = aci_explorer._classify_manifest(manifest_url, body)

        return {
            "url": manifest_url,
            "found": True,
            "manifest_type": mtype,
            "http_status": status,
            "size_bytes": len(body),
            "data": data,
        }

    except json.JSONDecodeError as e:
        return {
            "url": manifest_url,
            "found": False,
            "error": f"Invalid JSON: {e}",
        }
    except Exception as e:
        return {
            "url": manifest_url,
            "found": False,
            "error": str(e),
        }


# ── MCP Server ────────────────────────────────────────────────────────

app = Server("aci")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="aci_validate",
            description=(
                "Validate a URL against the ACI (Autonomous Company Interface) specification. "
                "Discovers and validates all ACI manifests (identity, capability, knowledge, trust, agents), "
                "computes conformance level (0-3) and overall score (0-100). "
                "Returns a comprehensive structured report."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Organization URL to validate (e.g., https://empirelabs.com.au)"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="aci_discover",
            description=(
                "Discover ACI manifests for a domain. "
                "Fetches the domain's /llms.txt and extracts all manifest URLs. "
                "Returns the discovery chain showing where each manifest type was found."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Organization URL or domain to discover manifests for"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="aci_explore",
            description=(
                "Fetch and return a specific ACI manifest by its URL. "
                "Useful for browsing individual manifests after running aci_discover. "
                "Returns the full manifest data as a structured JSON object."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "manifest_url": {
                        "type": "string",
                        "description": "Full URL to an ACI manifest JSON file"
                    }
                },
                "required": ["manifest_url"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        if name == "aci_validate":
            url = arguments["url"]
            result = _do_validate(url)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            )

        elif name == "aci_discover":
            url = arguments["url"]
            result = _do_discover(url)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            )

        elif name == "aci_explore":
            manifest_url = arguments["manifest_url"]
            result = _do_explore(manifest_url)
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            )

        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True
            )

    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            isError=True
        )


# ── Entry Points ──────────────────────────────────────────────────────

async def run_stdio():
    """Run MCP server over stdio."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="aci",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run_http(host: str = "0.0.0.0", port: int = 8200):
    """Run MCP server over HTTP (safe for ACI — public data only)."""
    import uvicorn
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route
    from starlette.responses import JSONResponse

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request,
            request.app.state.app,
        ) as streams:
            await app.run(
                streams[0], streams[1],
                InitializationOptions(
                    server_name="aci",
                    server_version="0.1.0",
                    capabilities=app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    async def handle_health(request):
        return JSONResponse({
            "status": "ok",
            "server": "aci-mcp",
            "version": "0.1.0",
            "safe": True,
            "tools": ["aci_validate", "aci_discover", "aci_explore"]
        })

    starlette_app = Starlette(
        routes=[
            Route("/health", handle_health),
            Route("/sse", handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )
    starlette_app.state.app = app

    print(f"🔧 ACI MCP Server (HTTP mode)")
    print(f"   Health: http://{host}:{port}/health")
    print(f"   SSE:    http://{host}:{port}/sse")
    print(f"   Tools:  validate, discover, explore")
    print(f"   Safe:   ✅ Stateless — public data only, no secrets/keys")
    uvicorn.run(starlette_app, host=host, port=port)


def main():
    parser = argparse.ArgumentParser(description="ACI MCP Server")
    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP mode (default: stdio)"
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=8200, help="HTTP port")
    args = parser.parse_args()

    if args.http:
        run_http(host=args.host, port=args.port)
    else:
        anyio.run(run_stdio)


if __name__ == "__main__":
    main()
