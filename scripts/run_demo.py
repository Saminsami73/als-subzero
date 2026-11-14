"""
ALS SubZero Live Demonstration Script.
Developed by Samin Sami.
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).

Demonstrates creating directories, writing multiple files into in-flight delay lines,
observing packet reflections, and reading back content with bit-exact verification.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.core.engine import SubZeroEngine
from als_subzero.net.transport import SimulatedNetworkTransport


def main() -> None:
    print("=" * 70)
    print(" ALS SubZero Dynamic Delay-Line Network Filesystem Demonstration")
    print(" Developed by Samin Sami (ALS = Al Sami)")
    print("=" * 70)

    transport = SimulatedNetworkTransport(base_rtt_ms=12.0, jitter_ms=1.5, packet_loss_rate=0.02)
    engine = SubZeroEngine(
        transport=transport,
        reflectors=[("reflector-us-east.net", 9999), ("reflector-eu-central.net", 9999)],
        fec_k=4,
        fec_m=2,
        target_loop_ms=25.0,
    )

    print("\n[1/5] Booting ALS SubZero Delay-Line Engine & Background Parity Scrubber...")
    engine.start()

    try:
        print("[2/5] Creating VFS directory structure (/system, /data)...")
        engine.vfs.mkdir("/system")
        engine.vfs.mkdir("/data")

        print("[3/5] Injecting files into network delay lines...")
        manifest = b"ALS SubZero System Manifest v2.0 - Operating on dynamic network memory."
        engine.write_file("/system/manifest.txt", manifest)

        dataset = b"ALS SubZero In-Flight Binary Buffer: " + os.urandom(3000)
        engine.write_file("/data/stream.bin", dataset)

        print("\n[4/5] Directory Tree in Volatile Network Storage:")
        print(engine.vfs.tree_str("/"))

        print("\n[5/5] Circulating packets across network reflectors (2.0% simulated loss)...")
        for i in range(1, 6):
            time.sleep(0.1)
            t = engine.get_telemetry()
            print(f"  Cycle {i*5:>2}: TX={t.total_tx_packets:<4} RX={t.total_rx_packets:<4} "
                  f"RTT={t.avg_rtt_ms:.1f}ms  In-Flight Chunks={t.data_chunks_in_flight + t.parity_chunks_in_flight} "
                  f"Healed={t.fec_recovered_chunks}")

        print("\nVerifying data read back from in-flight network loop...")
        read_manifest = engine.read_file("/system/manifest.txt")
        read_dataset = engine.read_file("/data/stream.bin")

        assert read_manifest == manifest, "Manifest mismatch!"
        assert read_dataset == dataset, "Dataset mismatch!"

        print("SUCCESS: Both files verified 100% bit-exact after active network flight!")
        print("=" * 70)
    finally:
        engine.stop()


if __name__ == "__main__":
    main()
