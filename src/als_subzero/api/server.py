"""
ALS SubZero Web Dashboard and REST API Server.
Developed by Samin Sami.

Provides HTTP REST endpoints and an interactive web interface for inspecting
and managing the delay-line network filesystem.
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
"""

from __future__ import annotations

import json
import socketserver
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from als_subzero.core.engine import SubZeroEngine

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ALS SubZero Control Plane - Samin Sami</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: #111827;
      --border: #1f2937;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --accent: #3b82f6;
      --accent-glow: rgba(59, 130, 246, 0.2);
      --success: #10b981;
      --warning: #f59e0b;
      --font-mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      padding: 24px;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
    }
    .brand h1 {
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
      color: #fff;
    }
    .brand p {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 9999px;
      background: rgba(16, 185, 129, 0.1);
      color: var(--success);
      font-size: 12px;
      font-weight: 600;
      border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .badge::before {
      content: "";
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 8px var(--success);
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 18px;
    }
    .card h3 {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      margin-bottom: 8px;
    }
    .metric-val {
      font-size: 28px;
      font-weight: 700;
      font-family: var(--font-mono);
      color: #fff;
    }
    .metric-sub {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 4px;
    }
    .section-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 12px;
      color: #fff;
    }
    .terminal-card {
      background: #06090e;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
      font-family: var(--font-mono);
      font-size: 13px;
      color: #38bdf8;
      white-space: pre-wrap;
      max-height: 280px;
      overflow-y: auto;
      margin-bottom: 24px;
    }
    .action-row {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }
    input, button, textarea {
      font-family: inherit;
      font-size: 14px;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      background: var(--card-bg);
      color: #fff;
    }
    input:focus, textarea:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }
    button {
      background: var(--accent);
      border: none;
      cursor: pointer;
      font-weight: 600;
      transition: opacity 0.15s;
    }
    button:hover { opacity: 0.9; }
  </style>
</head>
<body>
  <div class="header">
    <div class="brand">
      <h1>ALS SubZero Control Plane</h1>
      <p>Dynamic Delay-Line Network Storage Engine | Developed by Samin Sami (ALS = Al Sami)</p>
    </div>
    <div class="badge">In-Flight Delay Line Online</div>
  </div>

  <div class="grid">
    <div class="card">
      <h3>Bytes in Flight</h3>
      <div class="metric-val" id="val-bytes">0 B</div>
      <div class="metric-sub" id="val-files">0 Active Files</div>
    </div>
    <div class="card">
      <h3>Active Delay Loops</h3>
      <div class="metric-val" id="val-chunks">0</div>
      <div class="metric-sub" id="val-parity">0 Data / 0 Parity Chunks</div>
    </div>
    <div class="card">
      <h3>Average Loop RTT</h3>
      <div class="metric-val" id="val-rtt">0.0 ms</div>
      <div class="metric-sub" id="val-queue">Pacer Queue: 0 frames</div>
    </div>
    <div class="card">
      <h3>FEC Self-Healing</h3>
      <div class="metric-val" id="val-fec" style="color: var(--success);">0</div>
      <div class="metric-sub">Chunks Auto-Reconstructed</div>
    </div>
  </div>

  <div class="section-title">Virtual Filesystem Tree (In-Flight Storage)</div>
  <div class="terminal-card" id="vfs-tree">Loading directory tree...</div>

  <div class="section-title">Quick Ingest (Network Delay-Line Injection)</div>
  <div class="action-row">
    <input type="text" id="input-path" placeholder="/demo.txt" style="width: 200px;">
    <input type="text" id="input-text" placeholder="Write text to circulate in flight..." style="flex: 1; min-width: 240px;">
    <button onclick="writeFile()">Inject Block</button>
    <button onclick="readFile()" style="background: #4b5563;">Read Block</button>
  </div>

  <div class="terminal-card" id="output-view" style="color: #a7f3d0; min-height: 80px;">Ready for commands.</div>

  <script>
    async function updateTelemetry() {
      try {
        const res = await fetch('/api/v1/telemetry');
        const data = await res.json();
        document.getElementById('val-bytes').innerText = formatBytes(data.total_bytes_in_flight);
        document.getElementById('val-files').innerText = `${data.active_files} Active Files`;
        document.getElementById('val-chunks').innerText = data.data_chunks_in_flight + data.parity_chunks_in_flight;
        document.getElementById('val-parity').innerText = `${data.data_chunks_in_flight} Data / ${data.parity_chunks_in_flight} Parity Chunks`;
        document.getElementById('val-rtt').innerText = `${data.avg_rtt_ms.toFixed(2)} ms`;
        document.getElementById('val-queue').innerText = `Pacer Queue: ${data.pacer_queue_depth} frames`;
        document.getElementById('val-fec').innerText = data.fec_recovered_chunks;

        const treeRes = await fetch('/api/v1/fs/tree');
        const treeData = await treeRes.json();
        document.getElementById('vfs-tree').innerText = treeData.tree || '/';
      } catch (e) {
        console.error(e);
      }
    }

    function formatBytes(bytes) {
      if (!bytes || bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
    }

    async function writeFile() {
      const path = document.getElementById('input-path').value.trim();
      const text = document.getElementById('input-text').value;
      if (!path) return alert('Please enter path');
      const res = await fetch(`/api/v1/fs/write?path=${encodeURIComponent(path)}`, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: text
      });
      const ret = await res.json();
      document.getElementById('output-view').innerText = `Injected ${path} (${text.length} bytes) into flight path.\nResponse: ` + JSON.stringify(ret, null, 2);
      updateTelemetry();
    }

    async function readFile() {
      const path = document.getElementById('input-path').value.trim();
      if (!path) return alert('Please enter path');
      const res = await fetch(`/api/v1/fs/cat?path=${encodeURIComponent(path)}`);
      if (!res.ok) {
        document.getElementById('output-view').innerText = `Read error (${res.status}): ${await res.text()}`;
        return;
      }
      const text = await res.text();
      document.getElementById('output-view').innerText = `Content of ${path}:\n---\n${text}`;
    }

    setInterval(updateTelemetry, 1500);
    updateTelemetry();
  </script>
</body>
</html>
"""


class SubZeroHTTPHandler(BaseHTTPRequestHandler):
    engine: "SubZeroEngine"

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
            return

        if parsed.path == "/api/v1/telemetry":
            stats = self.engine.get_telemetry()
            data = {
                "active_files": stats.active_files,
                "total_bytes_in_flight": stats.total_bytes_in_flight,
                "data_chunks_in_flight": stats.data_chunks_in_flight,
                "parity_chunks_in_flight": stats.parity_chunks_in_flight,
                "fec_recovered_chunks": stats.fec_recovered_chunks,
                "total_rx_packets": stats.total_rx_packets,
                "total_tx_packets": stats.total_tx_packets,
                "avg_rtt_ms": stats.avg_rtt_ms,
                "pacer_queue_depth": stats.pacer_queue_depth,
            }
            self._send_json(data)
            return

        if parsed.path == "/api/v1/fs/tree":
            path = params.get("path", ["/"])[0]
            tree = self.engine.vfs.tree_str(path)
            self._send_json({"path": path, "tree": tree})
            return

        if parsed.path == "/api/v1/fs/cat":
            path = params.get("path", [""])[0]
            if not path:
                self._send_error_json("Missing 'path' query parameter", HTTPStatus.BAD_REQUEST)
                return
            try:
                content = self.engine.read_file(path)
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self._send_error_json(f"File not found: {path}", HTTPStatus.NOT_FOUND)
            except Exception as e:
                self._send_error_json(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_error_json("Endpoint not found", HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len)

        if parsed.path == "/api/v1/fs/write":
            path = params.get("path", [""])[0]
            if not path:
                self._send_error_json("Missing 'path' query parameter", HTTPStatus.BAD_REQUEST)
                return
            try:
                inode = self.engine.write_file(path, body)
                self._send_json({
                    "status": "success",
                    "path": path,
                    "inode_id": inode.inode_id,
                    "size": inode.size,
                    "chunks": len(inode.chunk_indices),
                })
            except Exception as e:
                self._send_error_json(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if parsed.path == "/api/v1/fs/mkdir":
            path = params.get("path", [""])[0]
            if not path:
                self._send_error_json("Missing 'path' query parameter", HTTPStatus.BAD_REQUEST)
                return
            try:
                inode = self.engine.vfs.mkdir(path)
                self._send_json({"status": "success", "path": path, "inode_id": inode.inode_id})
            except Exception as e:
                self._send_error_json(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_error_json("Endpoint not found", HTTPStatus.NOT_FOUND)

    def do_DELETE(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == "/api/v1/fs/rm":
            path = params.get("path", [""])[0]
            if not path:
                self._send_error_json("Missing 'path' query parameter", HTTPStatus.BAD_REQUEST)
                return
            try:
                self.engine.unlink_file(path)
                self._send_json({"status": "success", "deleted": path})
            except Exception as e:
                self._send_error_json(str(e), HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_error_json("Endpoint not found", HTTPStatus.NOT_FOUND)

    def _send_json(self, data: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_error_json(self, message: str, status: HTTPStatus) -> None:
        self._send_json({"error": message}, status=status)

    def log_message(self, format: str, *args: object) -> None:
        # Suppress noisy HTTP request logging in console
        pass


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


def run_api_server(engine: "SubZeroEngine", host: str = "127.0.0.1", port: int = 8080) -> HTTPServer:
    """Start the non-blocking multi-threaded HTTP server."""
    handler_class = SubZeroHTTPHandler
    handler_class.engine = engine
    server = ThreadedHTTPServer((host, port), handler_class)
    return server


