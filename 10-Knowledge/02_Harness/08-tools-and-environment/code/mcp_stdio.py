"""Runnable JSON-RPC / MCP stdio subset, protocol 2025-06-18; no SDK dependency."""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from runtime import ROOT, build_registry


def serve(workspace):
    registry = build_registry(workspace)
    initialized = False
    for line in sys.stdin:
        request = json.loads(line)
        if "id" not in request:
            if request.get("method") == "notifications/initialized":
                initialized = True
            continue
        method, params = request["method"], request.get("params", {})
        response = {"jsonrpc": "2.0", "id": request["id"]}
        if method == "initialize":
            response["result"] = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                                  "serverInfo": {"name": "inventory-tools", "version": "1.0.0"}}
        elif not initialized:
            response["error"] = {"code": -32000, "message": "not initialized"}
        elif method == "tools/list":
            response["result"] = {"tools": registry.list_tools()}
        elif method == "tools/call":
            if params.get("name") not in registry.tools:
                response["error"] = {"code": -32602, "message": "unknown tool"}
                print(json.dumps(response, ensure_ascii=False), flush=True)
                continue
            local = registry.call({"id": str(request["id"]), "name": params.get("name"),
                                   "arguments": params.get("arguments", {})})
            payload = local["data"] if local["ok"] else local["error"]
            result = {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}], "isError": not local["ok"]}
            if local["ok"]:
                result["structuredContent"] = payload
            response["result"] = result
        else:
            response["error"] = {"code": -32601, "message": "method not found"}
        print(json.dumps(response, ensure_ascii=False), flush=True)


def client(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    messages = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "chapter-client", "version": "1.0.0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "search_docs", "arguments": {"query": "先读取笔记", "limit": 5}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "search_docs", "arguments": {"query": "先读取笔记", "limit": 200}}},
    ]
    process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--serve", "--workspace", str(output / "workspace")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    # Each request waits for its response; do not use this synchronous sample for an untrusted remote server.
    import threading
    watchdog = threading.Timer(5, process.kill)
    watchdog.start()
    replies = []
    try:
        for message in messages:
            process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
            process.stdin.flush()
            if "id" in message:
                reply = json.loads(process.stdout.readline())
                if reply.get("id") != message["id"]:
                    raise RuntimeError("response id mismatch")
                if message["method"] == "initialize" and reply["result"]["protocolVersion"] != "2025-06-18":
                    raise RuntimeError("protocol version mismatch")
                replies.append(reply)
        process.stdin.close()
        process.wait(timeout=5)
        if process.returncode:
            raise RuntimeError("MCP child failed")
    finally:
        watchdog.cancel()
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stdout.close()
        process.stderr.close()
    (output / "messages.json").write_text(json.dumps({"requests": messages, "responses": replies}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert len(replies[1]["result"]["tools"]) == 5
    assert replies[2]["result"]["structuredContent"]["matches"][0]["line"] == 3
    assert replies[3]["result"]["isError"] is True
    print("protocol=2025-06-18 tools=5 valid_call=True invalid_call=True")
    print(f"artifacts={output.as_posix()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--workspace", default=str(ROOT / "runs/mcp-server"))
    parser.add_argument("--output", default="runs/mcp")
    args = parser.parse_args()
    serve(args.workspace) if args.serve else client(args.output)
