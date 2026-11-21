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
  <title>ALS SubZero Control Console</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: #0d1117;
      color: #c9d1d9;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
      font-size: 13px;
      line-height: 1.45;
      padding: 16px;
    }
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
    
    /* Top Bar */
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      margin-bottom: 14px;
    }
    .brand-title {
      font-size: 15px;
      font-weight: 700;
      color: #f0f6fc;
      letter-spacing: 0.5px;
    }
    .brand-sub {
      font-size: 11px;
      color: #8b949e;
      margin-top: 1px;
    }
    .top-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
    }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 3px 8px;
      background: #0e2a1b;
      color: #3fb950;
      border: 1px solid #238636;
      border-radius: 12px;
      font-weight: 600;
      font-size: 11px;
    }
    .status-dot {
      width: 6px;
      height: 6px;
      background: #3fb950;
      border-radius: 50%;
    }

    /* Metric Grid */
    .stats-row {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 10px;
      margin-bottom: 14px;
    }
    .stat-box {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      padding: 10px 12px;
    }
    .stat-label {
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: #8b949e;
      margin-bottom: 4px;
    }
    .stat-value {
      font-size: 20px;
      font-weight: 700;
      color: #f0f6fc;
    }
    .stat-desc {
      font-size: 11px;
      color: #8b949e;
      margin-top: 2px;
    }

    /* Main Workspace Split */
    .workspace {
      display: grid;
      grid-template-columns: 1fr 1.2fr;
      gap: 14px;
    }
    @media (max-width: 900px) {
      .workspace { grid-template-columns: 1fr; }
    }

    .panel {
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .panel-header {
      background: #21262d;
      border-bottom: 1px solid #30363d;
      padding: 8px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-weight: 600;
      font-size: 12px;
      color: #f0f6fc;
    }
    .panel-body {
      padding: 12px;
      flex: 1;
    }

    /* Console & Tree */
    .terminal {
      background: #090d13;
      border: 1px solid #30363d;
      border-radius: 4px;
      padding: 10px;
      font-size: 12px;
      color: #79c0ff;
      white-space: pre-wrap;
      overflow-y: auto;
      max-height: 280px;
      min-height: 140px;
      line-height: 1.4;
    }
    .log-box {
      background: #090d13;
      border: 1px solid #30363d;
      border-radius: 4px;
      padding: 8px;
      font-size: 11px;
      color: #8b949e;
      max-height: 120px;
      overflow-y: auto;
      margin-top: 10px;
    }
    .log-entry { margin-bottom: 3px; }
    .log-entry .time { color: #58a6ff; }
    .log-entry .ok { color: #3fb950; }

    /* Forms & Buttons */
    .form-group {
      margin-bottom: 10px;
    }
    .form-label {
      display: block;
      font-size: 11px;
      font-weight: 600;
      color: #8b949e;
      margin-bottom: 4px;
    }
    input[type="text"], textarea {
      width: 100%;
      background: #090d13;
      border: 1px solid #30363d;
      border-radius: 4px;
      color: #f0f6fc;
      padding: 6px 10px;
      font-size: 12px;
      font-family: inherit;
    }
    input[type="text"]:focus, textarea:focus {
      outline: none;
      border-color: #58a6ff;
    }
    textarea { resize: vertical; min-height: 60px; }
    
    .btn-row {
      display: flex;
      gap: 8px;
      margin-top: 8px;
      flex-wrap: wrap;
    }
    button {
      padding: 6px 12px;
      font-size: 12px;
      font-weight: 600;
      border-radius: 4px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: background 0.1s;
    }
    .btn-primary { background: #238636; color: #fff; border-color: #2ea043; }
    .btn-primary:hover { background: #2ea043; }
    .btn-secondary { background: #21262d; color: #c9d1d9; border-color: #30363d; }
    .btn-secondary:hover { background: #30363d; }
    .btn-danger { background: #b62324; color: #fff; border-color: #d73a49; }
    .btn-danger:hover { background: #cb2431; }
    .btn-sm { padding: 3px 8px; font-size: 11px; }

    /* Footer info */
    .footer-note {
      text-align: center;
      margin-top: 14px;
      font-size: 11px;
      color: #8b949e;
    }
  </style>
</head>
<body>

  <!-- Top Bar -->
  <div class="topbar">
    <div>
      <div class="brand-title mono">ALS SUBZERO // CONSOLE</div>
      <div class="brand-sub">In-Flight Delay-Line Network Storage &bull; Built by Samin Sami (ALS = Al Sami)</div>
    </div>
    <div class="top-meta mono">
      <span id="poll-indicator">POLL: 1s</span>
      <span class="status-pill"><span class="status-dot"></span> LIVE IN-FLIGHT</span>
    </div>
  </div>

  <!-- Real-Time Metrics Row -->
  <div class="stats-row mono">
    <div class="stat-box">
      <div class="stat-label">In-Flight Memory</div>
      <div class="stat-value" id="val-bytes">0 B</div>
      <div class="stat-desc" id="val-files">0 files in VFS</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Circulating Chunks</div>
      <div class="stat-value" id="val-chunks">0</div>
      <div class="stat-desc" id="val-parity">0 data / 0 parity</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Wire Latency (RTT)</div>
      <div class="stat-value" id="val-rtt">0.0 ms</div>
      <div class="stat-desc" id="val-queue">Pacer queue: 0</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">FEC Recovered</div>
      <div class="stat-value" id="val-fec" style="color: #3fb950;">0</div>
      <div class="stat-desc">Dropped chunks healed</div>
    </div>
    <div class="stat-box">
      <div class="stat-label">Wire Packets</div>
      <div class="stat-value" id="val-packets">0 / 0</div>
      <div class="stat-desc">Total TX / RX frames</div>
    </div>
  </div>

  <!-- Workspace Split -->
  <div class="workspace">

    <!-- Left Pane: VFS -->
    <div class="panel">
      <div class="panel-header">
        <span>VIRTUAL FILESYSTEM (DELAY-LINE)</span>
        <button class="btn-secondary btn-sm" onclick="refreshTree()">Refresh Tree</button>
      </div>
      <div class="panel-body">
        <div class="terminal mono" id="vfs-tree">Loading filesystem tree...</div>
        <div style="margin-top: 10px; display: flex; gap: 6px;">
          <input type="text" id="mkdir-path" placeholder="/new_dir" style="flex: 1;">
          <button class="btn-secondary btn-sm" onclick="makeDir()">+ Mkdir</button>
        </div>
      </div>
    </div>

    <!-- Right Pane: Ingest & Reader -->
    <div class="panel">
      <div class="panel-header">
        <span>PACKET INJECTOR & RETRIEVAL</span>
        <span class="mono" style="font-size: 11px; color: #8b949e;">REST API v1</span>
      </div>
      <div class="panel-body">
        <div class="form-group">
          <label class="form-label">Virtual File Path</label>
          <input type="text" id="input-path" class="mono" placeholder="/notes/test.txt" value="/flight_sample.txt">
        </div>
        <div class="form-group">
          <label class="form-label">Payload Content (Written to Wire)</label>
          <textarea id="input-text" class="mono" placeholder="Type text to inject into circulating flight packets...">Hello from ALS SubZero delay-line memory! This data lives in network flight.</textarea>
        </div>
        <div class="btn-row">
          <button class="btn-primary" onclick="writeFile()">Inject Into Flight</button>
          <button class="btn-secondary" onclick="readFile()">Read From Wire</button>
          <button class="btn-danger" onclick="deleteFile()">Delete From VFS</button>
          <button class="btn-secondary" onclick="clearOutput()">Clear Output</button>
        </div>

        <div style="margin-top: 12px;">
          <div class="form-label">Console Transaction Log</div>
          <div class="terminal mono" id="output-view" style="color: #7ee787; min-height: 90px; max-height: 140px;">Ready. Enter a path and inject or read data.</div>
        </div>

        <div class="log-box mono" id="event-log">
          <div class="log-entry"><span class="time">[00:00:00]</span> Initialized connection to ALS SubZero HTTP daemon.</div>
        </div>
      </div>
    </div>

  </div>

  <div class="footer-note mono">
    Zero Disk Writes &bull; Cauchy Reed-Solomon GF(2^8) FEC &bull; Token-Bucket Microsecond Pacer &bull; Samin Sami
  </div>

  <script>
    function logEvent(msg, isOk = true) {
      const log = document.getElementById('event-log');
      const now = new Date().toTimeString().split(' ')[0];
      const div = document.createElement('div');
      div.className = 'log-entry';
      div.innerHTML = `<span class="time">[${now}]</span> <span class="${isOk ? 'ok' : ''}">${msg}</span>`;
      log.prepend(div);
      if (log.children.length > 25) log.removeChild(log.lastChild);
    }

    function formatBytes(bytes) {
      if (!bytes || bytes === 0) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
    }

    async function updateTelemetry() {
      try {
        const res = await fetch('/api/v1/telemetry');
        if (!res.ok) return;
        const d = await res.json();
        document.getElementById('val-bytes').innerText = formatBytes(d.total_bytes_in_flight);
        document.getElementById('val-files').innerText = `${d.active_files} file${d.active_files === 1 ? '' : 's'} in VFS`;
        document.getElementById('val-chunks').innerText = d.data_chunks_in_flight + d.parity_chunks_in_flight;
        document.getElementById('val-parity').innerText = `${d.data_chunks_in_flight} data / ${d.parity_chunks_in_flight} parity`;
        document.getElementById('val-rtt').innerText = `${d.avg_rtt_ms.toFixed(2)} ms`;
        document.getElementById('val-queue').innerText = `Pacer queue: ${d.pacer_queue_depth}`;
        document.getElementById('val-fec').innerText = d.fec_recovered_chunks;
        document.getElementById('val-packets').innerText = `${d.total_tx_packets} / ${d.total_rx_packets}`;
      } catch (e) {
        console.error(e);
      }
    }

    async function refreshTree() {
      try {
        const res = await fetch('/api/v1/fs/tree');
        if (res.ok) {
          const d = await res.json();
          document.getElementById('vfs-tree').innerText = d.tree || '/';
        }
      } catch (e) {
        console.error(e);
      }
    }

    async function writeFile() {
      const path = document.getElementById('input-path').value.trim();
      const text = document.getElementById('input-text').value;
      if (!path) return alert('Please enter path');
      try {
        const res = await fetch(`/api/v1/fs/write?path=${encodeURIComponent(path)}`, {
          method: 'POST',
          headers: { 'Content-Type': 'text/plain' },
          body: text
        });
        const ret = await res.json();
        document.getElementById('output-view').innerText = `SUCCESS: Wrote ${text.length} bytes into ${path}\n` + JSON.stringify(ret, null, 2);
        logEvent(`Injected ${text.length} B into ${path} (${ret.chunks} chunks).`);
        updateTelemetry();
        refreshTree();
      } catch (e) {
        document.getElementById('output-view').innerText = `Error: ${e}`;
        logEvent(`Write failed: ${e}`, false);
      }
    }

    async function readFile() {
      const path = document.getElementById('input-path').value.trim();
      if (!path) return alert('Please enter path');
      try {
        const res = await fetch(`/api/v1/fs/cat?path=${encodeURIComponent(path)}`);
        if (!res.ok) {
          const err = await res.text();
          document.getElementById('output-view').innerText = `READ ERROR (${res.status}): ${err}`;
          logEvent(`Read failed for ${path} (${res.status})`, false);
          return;
        }
        const text = await res.text();
        document.getElementById('output-view').innerText = `READ OK (${path}):\n${text}`;
        logEvent(`Retrieved ${path} (${text.length} bytes).`);
      } catch (e) {
        document.getElementById('output-view').innerText = `Error: ${e}`;
      }
    }

    async function deleteFile() {
      const path = document.getElementById('input-path').value.trim();
      if (!path) return alert('Please enter path');
      if (!confirm(`Delete ${path} from in-flight storage?`)) return;
      try {
        const res = await fetch(`/api/v1/fs/rm?path=${encodeURIComponent(path)}`, { method: 'DELETE' });
        const ret = await res.json();
        document.getElementById('output-view').innerText = `DELETED: ${path}\n` + JSON.stringify(ret, null, 2);
        logEvent(`Removed ${path} from flight memory.`);
        updateTelemetry();
        refreshTree();
      } catch (e) {
        document.getElementById('output-view').innerText = `Delete error: ${e}`;
      }
    }

    async function makeDir() {
      const dirInput = document.getElementById('mkdir-path');
      const dirPath = dirInput.value.trim();
      if (!dirPath) return alert('Enter directory path');
      try {
        const res = await fetch(`/api/v1/fs/mkdir?path=${encodeURIComponent(dirPath)}`, { method: 'POST' });
        const ret = await res.json();
        document.getElementById('output-view').innerText = `MKDIR OK: ${dirPath}\n` + JSON.stringify(ret, null, 2);
        dirInput.value = '';
        logEvent(`Created directory ${dirPath}`);
        refreshTree();
      } catch (e) {
        document.getElementById('output-view').innerText = `Mkdir error: ${e}`;
      }
    }

    function clearOutput() {
      document.getElementById('output-view').innerText = 'Output cleared.';
    }

    setInterval(updateTelemetry, 1000);
    setInterval(refreshTree, 3000);
    updateTelemetry();
    refreshTree();
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


