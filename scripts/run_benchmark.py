"""
ALS SubZero Performance & Reliability Benchmark Runner.
Developed by Samin Sami.
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).

Runs automated persistence benchmarks across various packet loss profiles
and prints verification metrics.
"""

import csv
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.core.engine import SubZeroEngine
from als_subzero.net.transport import SimulatedNetworkTransport


def run_benchmark_profile(loss_rate: float, data_size: int = 16384, cycles: int = 60) -> dict:
    transport = SimulatedNetworkTransport(
        base_rtt_ms=8.0,
        jitter_ms=1.0,
        packet_loss_rate=loss_rate,
    )
    engine = SubZeroEngine(
        transport=transport,
        reflectors=[("bench-1", 9999), ("bench-2", 9999)],
        fec_k=4,
        fec_m=2,
        target_loop_ms=16.0,
        scrub_interval_s=0.04,
    )
    engine.start()
    try:
        payload = os.urandom(data_size)
        path = "/bench.dat"
        t0 = time.time()
        engine.write_file(path, payload)

        start_tx = engine.get_telemetry().total_tx_packets
        target_packets = start_tx + (cycles * 24)

        while True:
            cur_tx = engine.get_telemetry().total_tx_packets
            if cur_tx >= target_packets or (time.time() - t0) > 10.0:
                break
            time.sleep(0.02)

        elapsed = time.time() - t0
        telemetry = engine.get_telemetry()
        read_back = engine.read_file(path)

        verified = (read_back == payload)
        return {
            "loss_rate": loss_rate,
            "data_size": data_size,
            "elapsed_s": elapsed,
            "tx_packets": telemetry.total_tx_packets,
            "rx_packets": telemetry.total_rx_packets,
            "fec_recovered": telemetry.fec_recovered_chunks,
            "avg_rtt_ms": telemetry.avg_rtt_ms,
            "verified": verified,
        }
    finally:
        engine.stop()


def main() -> None:
    print(" ALS SubZero Reliability & FEC Recovery Benchmark Suite")
    print(" Developed by Samin Sami (ALS = Al Sami)")
    
    profiles = [0.0, 0.02, 0.05, 0.10]
    results = []

    print(f"{'Loss Rate':<10} | {'Data Size':<10} | {'Duration':<10} | {'TX/RX Pkts':<14} | {'FEC Healed':<10} | {'Status':<8}")
    print("|" * 76)

    for loss in profiles:
        res = run_benchmark_profile(loss_rate=loss, data_size=16384, cycles=60)
        results.append(res)
        status_str = "PASS" if res["verified"] else "FAIL"
        tx_rx_str = f"{res['tx_packets']}/{res['rx_packets']}"
        print(f"{res['loss_rate']*100:>8.1f}% | {res['data_size']:>8} B | {res['elapsed_s']:>8.2f} s | {tx_rx_str:>14} | {res['fec_recovered']:>10} | {status_str:<8}")

    print("=" * 76)
    all_passed = all(r["verified"] for r in results)
    if all_passed:
        print("ALL PROFILES PASSED: 100% Bit-Exact Persistence Under Up to 10% Packet Loss.")
    else:
        print("SOME PROFILES FAILED.")

    # Export latest run to derived directory if present
    derived_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "researchTemplate", "research", "data", "derived"))
    if os.path.exists(derived_dir):
        csv_path = os.path.join(derived_dir, "latest_benchmark_results.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["loss_rate_percent", "data_size_bytes", "duration_seconds", "tx_packets", "rx_packets", "fec_healed", "verified"])
            for r in results:
                writer.writerow([r["loss_rate"] * 100, r["data_size"], f"{r['elapsed_s']:.2f}", r["tx_packets"], r["rx_packets"], r["fec_recovered"], r["verified"]])
        print(f"Exported latest benchmark metrics to {csv_path}")


if __name__ == "__main__":
    main()
