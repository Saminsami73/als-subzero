"""
ALS SubZero Main Entrypoint.
Developed by Samin Sami.

Parses command-line options and boots the appropriate subsystem.
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).
"""

from __future__ import annotations

import argparse
import sys
import time

from als_subzero import __version__
from als_subzero.api.server import run_api_server
from als_subzero.cli.shell import SubZeroShell
from als_subzero.core.engine import SubZeroEngine
from als_subzero.net.transport import (
    RawICMPTransport,
    SimulatedNetworkTransport,
    StandaloneUDPReflector,
    UDPReflectorTransport,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="als-subzero",
        description="ALS SubZero: Dynamic Delay-Line Network Memory Filesystem & Storage Engine. Developed by Samin Sami.",
    )
    parser.add_argument("--version", action="version", version=f"ALS SubZero {__version__}")

    subparsers = parser.add_subparsers(dest="subcommand", help="Operational mode")

    # Shell mode
    p_shell = subparsers.add_parser("shell", help="Launch interactive shell")
    p_shell.add_argument(
        "--transport",
        choices=["simulated", "udp", "icmp"],
        default="simulated",
        help="Transport layer (default: simulated)",
    )
    p_shell.add_argument("--loop-ms", type=float, default=30.0, help="Target loop RTT pacing in ms")
    p_shell.add_argument("--fec-k", type=int, default=4, help="Data chunks per FEC block")
    p_shell.add_argument("--fec-m", type=int, default=2, help="Parity chunks per FEC block")
    p_shell.add_argument("--host", default="127.0.0.1", help="Reflector host")
    p_shell.add_argument("--port", type=int, default=9999, help="Reflector port")

    # Serve mode
    p_serve = subparsers.add_parser("serve", help="Start HTTP REST Control Plane")
    p_serve.add_argument("--host", default="0.0.0.0", help="HTTP bind address")
    p_serve.add_argument("--port", type=int, default=8080, help="HTTP bind port")
    p_serve.add_argument("--transport", choices=["simulated", "udp", "icmp"], default="simulated")

    # Reflector mode
    p_reflector = subparsers.add_parser("reflector", help="Run standalone UDP reflector node")
    p_reflector.add_argument("--host", default="0.0.0.0", help="Bind IP")
    p_reflector.add_argument("--port", type=int, default=9999, help="Bind UDP port")

    # Benchmark mode
    p_bench = subparsers.add_parser("benchmark", help="Run automated stress and persistence benchmark")
    p_bench.add_argument("--loss", type=float, default=0.05, help="Simulated packet loss fraction (default: 0.05 = 5%)")
    p_bench.add_argument("--cycles", type=int, default=100, help="Number of flight loops to circulate")

    args = parser.parse_args()

    if not args.subcommand or args.subcommand == "shell":
        transport_name = getattr(args, "transport", "simulated")
        loop_ms = getattr(args, "loop_ms", 30.0)
        fec_k = getattr(args, "fec_k", 4)
        fec_m = getattr(args, "fec_m", 2)
        ref_host = getattr(args, "host", "127.0.0.1")
        ref_port = getattr(args, "port", 9999)

        engine = _create_engine(transport_name, loop_ms, fec_k, fec_m, ref_host, ref_port)
        engine.start()
        try:
            shell = SubZeroShell(engine)
            shell.run()
        finally:
            engine.stop()

    elif args.subcommand == "serve":
        engine = _create_engine(args.transport, 30.0, 4, 2, "127.0.0.1", 9999)
        engine.start()
        server = run_api_server(engine, host=args.host, port=args.port)
        print(f"ALS SubZero HTTP REST API running at http://{args.host}:{args.port}/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
        finally:
            engine.stop()

    elif args.subcommand == "reflector":
        print(f"Starting ALS SubZero Standalone UDP Reflector on {args.host}:{args.port}...")
        reflector = StandaloneUDPReflector(host=args.host, port=args.port)
        reflector.start()
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            print("\nReflector stopped.")
        finally:
            reflector.stop()

    elif args.subcommand == "benchmark":
        _run_direct_benchmark(args.loss, args.cycles)


def _create_engine(
    transport_name: str,
    loop_ms: float,
    fec_k: int,
    fec_m: int,
    host: str,
    port: int,
) -> SubZeroEngine:
    if transport_name == "udp":
        transport = UDPReflectorTransport()
        reflectors = [(host, port)]
    elif transport_name == "icmp":
        transport = RawICMPTransport()
        reflectors = [(host, 0)]
    else:
        transport = SimulatedNetworkTransport(base_rtt_ms=loop_ms / 2.0, jitter_ms=2.0)
        reflectors = [(host, port)]

    return SubZeroEngine(
        transport=transport,
        reflectors=reflectors,
        fec_k=fec_k,
        fec_m=fec_m,
        target_loop_ms=loop_ms,
    )


def _run_direct_benchmark(loss_rate: float, cycles: int) -> None:
    print(f"Initializing benchmark: loss_rate={loss_rate * 100:.1f}%, target_cycles={cycles}")
    transport = SimulatedNetworkTransport(base_rtt_ms=10.0, jitter_ms=1.5, packet_loss_rate=loss_rate)
    engine = SubZeroEngine(
        transport=transport,
        reflectors=[("sim-node-1", 9999)],
        fec_k=4,
        fec_m=2,
        target_loop_ms=20.0,
    )
    engine.start()
    try:
        import os
        payload = b"ALS SubZero Verified Payload: " + os.urandom(8192)
        test_path = "/benchmark_file.bin"
        print(f"Writing {len(payload)} bytes into in-flight storage (8 data blocks + 4 parity blocks)...")
        engine.write_file(test_path, payload)

        start_tx = engine.get_telemetry().total_tx_packets
        start_time = time.time()
        target_packets = start_tx + (cycles * 12)

        while True:
            cur_tx = engine.get_telemetry().total_tx_packets
            if cur_tx >= target_packets or (time.time() - start_time) > 15.0:
                break
            time.sleep(0.05)

        elapsed = time.time() - start_time
        telemetry = engine.get_telemetry()
        read_back = engine.read_file(test_path)

        assert read_back == payload, "Data verification failed: bit mismatch"
        print("=" * 64)
        print(" BENCHMARK RESULT: PASS (100% Data Integrity Verified)")
        print(f" Duration:            {elapsed:.2f} seconds")
        print(f" Total Packet Loops:  {telemetry.total_tx_packets} TX, {telemetry.total_rx_packets} RX")
        print(f" Packet Loss Tested:  {loss_rate * 100:.1f}%")
        print(f" FEC Auto-Recovered:  {telemetry.fec_recovered_chunks} chunks")
        print(f" Mean Network RTT:    {telemetry.avg_rtt_ms:.2f} ms")
        print("=" * 64)
    finally:
        engine.stop()


if __name__ == "__main__":
    main()
