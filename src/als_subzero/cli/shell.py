"""
ALS SubZero Interactive Shell and Diagnostic Suite.
Developed by Samin Sami.

Provides a Unix-like interactive terminal environment for manipulating in-flight files,
inspecting delay-line telemetry, and executing stress benchmarks.
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
"""

from __future__ import annotations

import os
import shlex
import sys
import threading
import time
from typing import List, Optional

from als_subzero.api.server import run_api_server
from als_subzero.core.engine import SubZeroEngine


class SubZeroShell:
    """Interactive command-line interface for ALS SubZero."""

    def __init__(self, engine: SubZeroEngine) -> None:
        self.engine = engine
        self._cwd = "/"
        self._http_server = None

    def run(self) -> None:
        """Run interactive REPL loop."""
        print("=" * 68)
        print(" ALS SubZero Shell - Dynamic Delay-Line Network Storage Engine")
        print(" Developed by Samin Sami (ALS = Al Sami)")
        print(" Type 'help' for commands, 'status' for telemetry, 'exit' to quit.")
        print("=" * 68)

        while True:
            try:
                prompt = f"subzero:{self._cwd}$ "
                line = input(prompt).strip()
                if not line:
                    continue
                parts = shlex.split(line)
                cmd = parts[0].lower()
                args = parts[1:]

                if cmd in ("exit", "quit", "q"):
                    break
                self._dispatch(cmd, args)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nInterrupted.")
                break
            except Exception as e:
                print(f"Error: {e}")

    def _resolve(self, path: str) -> str:
        if path.startswith("/"):
            return self.engine.vfs.normalize_path(path)
        if self._cwd == "/":
            return "/" + path
        return self.engine.vfs.normalize_path(f"{self._cwd}/{path}")

    def _dispatch(self, cmd: str, args: List[str]) -> None:
        if cmd == "help":
            self._cmd_help()
        elif cmd == "ls":
            self._cmd_ls(args)
        elif cmd == "cd":
            self._cmd_cd(args)
        elif cmd == "pwd":
            print(self._cwd)
        elif cmd == "cat":
            self._cmd_cat(args)
        elif cmd == "write":
            self._cmd_write(args)
        elif cmd == "mkdir":
            self._cmd_mkdir(args)
        elif cmd == "rm":
            self._cmd_rm(args)
        elif cmd == "stat":
            self._cmd_stat(args)
        elif cmd == "tree":
            self._cmd_tree(args)
        elif cmd in ("status", "telemetry"):
            self._cmd_status()
        elif cmd == "put":
            self._cmd_put(args)
        elif cmd == "get":
            self._cmd_get(args)
        elif cmd == "bench":
            self._cmd_bench(args)
        elif cmd == "serve":
            self._cmd_serve(args)
        else:
            print(f"Unknown command: {cmd}. Type 'help' for available commands.")

    def _cmd_help(self) -> None:
        print("""Available Commands:
  ls [path]               List directory contents
  cd [path]               Change working directory
  pwd                     Print current working directory
  cat <path>              Read and print file contents from flight path
  write <path> <text>     Write text into an in-flight file
  put <local> [remote]    Upload local file into in-flight storage
  get <remote> [local]    Download in-flight file to local disk
  mkdir <path>            Create a new directory
  rm <path>               Remove a file
  stat <path>             Display inode and chunk metadata
  tree [path]             Display hierarchical directory tree
  status | telemetry      Display live in-flight telemetry and RTT
  bench [loops]           Run flight persistence benchmark across N loops
  serve [port]            Start the HTTP REST / Web dashboard (default 8080)
  exit | quit             Exit the shell""")

    def _cmd_ls(self, args: List[str]) -> None:
        target = self._resolve(args[0]) if args else self._cwd
        entries = self.engine.vfs.readdir(target)
        if not entries:
            return
        for e in sorted(entries, key=lambda x: (not x.is_directory, x.name)):
            kind = "d" if e.is_directory else "-"
            size = f"{e.size:>8} B" if not e.is_directory else "     DIR"
            name = f"{e.name}/" if e.is_directory else e.name
            print(f"{kind}rw-r--r-- {size}  {name}")

    def _cmd_cd(self, args: List[str]) -> None:
        target = self._resolve(args[0]) if args else "/"
        node = self.engine.vfs.lookup(target)
        if not node:
            print(f"Directory not found: {target}")
            return
        if not node.is_directory:
            print(f"Not a directory: {target}")
            return
        self._cwd = target

    def _cmd_cat(self, args: List[str]) -> None:
        if not args:
            print("Usage: cat <path>")
            return
        target = self._resolve(args[0])
        try:
            content = self.engine.read_file(target)
            try:
                print(content.decode("utf-8"))
            except UnicodeDecodeError:
                print(f"[Binary payload: {len(content)} bytes]")
        except Exception as e:
            print(f"Read error: {e}")

    def _cmd_write(self, args: List[str]) -> None:
        if len(args) < 2:
            print("Usage: write <path> <text...>")
            return
        target = self._resolve(args[0])
        text = " ".join(args[1:])
        inode = self.engine.write_file(target, text.encode("utf-8"))
        print(f"Injected {len(text)} bytes into {target} ({len(inode.chunk_indices)} chunks).")

    def _cmd_put(self, args: List[str]) -> None:
        if not args:
            print("Usage: put <local_file> [remote_path]")
            return
        local_path = args[0]
        if not os.path.isfile(local_path):
            print(f"Local file not found: {local_path}")
            return
        with open(local_path, "rb") as f:
            data = f.read()
        remote_path = self._resolve(args[1] if len(args) > 1 else os.path.basename(local_path))
        inode = self.engine.write_file(remote_path, data)
        print(f"Uploaded {len(data)} bytes to {remote_path} ({len(inode.chunk_indices)} chunks in flight).")

    def _cmd_get(self, args: List[str]) -> None:
        if not args:
            print("Usage: get <remote_path> [local_file]")
            return
        remote_path = self._resolve(args[0])
        local_path = args[1] if len(args) > 1 else os.path.basename(remote_path)
        data = self.engine.read_file(remote_path)
        with open(local_path, "wb") as f:
            f.write(data)
        print(f"Downloaded {len(data)} bytes to {local_path}.")

    def _cmd_mkdir(self, args: List[str]) -> None:
        if not args:
            print("Usage: mkdir <path>")
            return
        target = self._resolve(args[0])
        self.engine.vfs.mkdir(target)
        print(f"Created directory: {target}")

    def _cmd_rm(self, args: List[str]) -> None:
        if not args:
            print("Usage: rm <path>")
            return
        target = self._resolve(args[0])
        self.engine.unlink_file(target)
        print(f"Removed: {target}")

    def _cmd_stat(self, args: List[str]) -> None:
        if not args:
            print("Usage: stat <path>")
            return
        target = self._resolve(args[0])
        node = self.engine.vfs.lookup(target)
        if not node:
            print(f"Path not found: {target}")
            return
        print(f"  File: {target}")
        print(f"  Inode: {node.inode_id}")
        print(f"  Type: {'Directory' if node.is_directory else 'Regular File'}")
        print(f"  Size: {node.size} bytes")
        print(f"  Mode: {oct(node.mode)}")
        print(f"  Chunks: {node.chunk_indices}")
        print(f"  Modified: {time.ctime(node.modified_at)}")

    def _cmd_tree(self, args: List[str]) -> None:
        target = self._resolve(args[0]) if args else self._cwd
        print(self.engine.vfs.tree_str(target))

    def _cmd_status(self) -> None:
        t = self.engine.get_telemetry()
        print("--- ALS SubZero Operational Telemetry ---")
        print(f"  Active Files in VFS:       {t.active_files}")
        print(f"  Total In-Flight Memory:    {t.total_bytes_in_flight} bytes")
        print(f"  Data Chunks Circulating:   {t.data_chunks_in_flight}")
        print(f"  Parity Chunks Circulating: {t.parity_chunks_in_flight}")
        print(f"  FEC Chunks Healed:         {t.fec_recovered_chunks}")
        print(f"  Packets Transmitted (TX):  {t.total_tx_packets}")
        print(f"  Packets Received (RX):     {t.total_rx_packets}")
        print(f"  Average Loop Latency:      {t.avg_rtt_ms:.2f} ms")
        print(f"  Pacer Queue Depth:         {t.pacer_queue_depth} frames")

    def _cmd_bench(self, args: List[str]) -> None:
        loops = int(args[0]) if args else 50
        print(f"Running flight persistence benchmark across {loops} circulation cycles...")
        test_data = b"ALS SubZero Bit-Exact Verification Block: " + os.urandom(2048)
        bench_path = "/_bench_test.bin"
        self.engine.write_file(bench_path, test_data)

        start_tx = self.engine.get_telemetry().total_tx_packets
        start_time = time.time()

        # Wait until target packet loops have completed
        target_tx = start_tx + (loops * 4)
        while True:
            cur_tx = self.engine.get_telemetry().total_tx_packets
            if cur_tx >= target_tx or (time.time() - start_time) > 10.0:
                break
            time.sleep(0.05)

        elapsed = time.time() - start_time
        read_back = self.engine.read_file(bench_path)
        self.engine.unlink_file(bench_path)

        if read_back == test_data:
            print(f"BENCHMARK PASS: 2048 bytes preserved with 100% bit-exact fidelity over {loops} loops ({elapsed:.2f}s).")
        else:
            print("BENCHMARK FAIL: Payload corrupted during circulation.")

    def _cmd_serve(self, args: List[str]) -> None:
        port = int(args[0]) if args else 8080
        if self._http_server:
            print(f"Web server already running on port {self._http_server.server_port}")
            return
        self._http_server = run_api_server(self.engine, host="0.0.0.0", port=port)
        srv_thread = threading.Thread(target=self._http_server.serve_forever, daemon=True)
        srv_thread.start()
        print(f"HTTP REST Control Plane online at http://127.0.0.1:{port}/")


