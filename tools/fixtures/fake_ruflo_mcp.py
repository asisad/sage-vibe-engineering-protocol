#!/usr/bin/env python3
"""Minimal deterministic MCP peer for SAGE adapter tests; NOT Ruflo."""
import json
import sys
import time

mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
for raw in sys.stdin:
    if not raw.strip():
        continue
    message = json.loads(raw)
    method = message.get("method")
    if "id" not in message:
        continue
    if method == "initialize":
        response = {"protocolVersion": "1900-01-01" if mode == "wrong-version" else "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "fake-ruflo-mcp", "version": "0.0-test"}}
    elif method == "tools/list":
        response = {"tools": [
            {"name": "memory_search", "inputSchema": {"type": "object"}},
            {"name": "agent_execute", "inputSchema": {"type": "object"}},
            {"name": "synthetic_test", "inputSchema": {"type": "object"}},
            {"name": "error_tool", "inputSchema": {"type": "object"}},
            {"name": "hang_tool", "inputSchema": {"type": "object"}},
        ]}
    elif method == "tools/call":
        name = message.get("params", {}).get("name")
        if name == "hang_tool":
            time.sleep(4)
        if name == "synthetic_test":
            response = {"content": [{"type": "text", "text": '{"synthetic":true,"success":true}'}]}
        elif name == "error_tool":
            response = {"isError": True, "content": [{"type": "text", "text": "expected error"}]}
        else:
            response = {"content": [{"type": "text", "text": "fake response"}],
                        "request_seen": {"name": name}}
    else:
        print(json.dumps({"jsonrpc": "2.0", "id": message["id"],
                          "error": {"code": -32601, "message": "unknown method"}}), flush=True)
        continue
    print(json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": response}), flush=True)
