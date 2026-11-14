"""
End-to-End Flight Persistence & Packet Loss Recovery Tests.
ALS SubZero - Developed by Samin Sami.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.core.engine import SubZeroEngine
from als_subzero.net.transport import SimulatedNetworkTransport


class TestFlightPersistence(unittest.TestCase):
    def test_end_to_end_flight_loop(self):
        transport = SimulatedNetworkTransport(base_rtt_ms=8.0, jitter_ms=1.0, packet_loss_rate=0.0)
        engine = SubZeroEngine(
            transport=transport,
            reflectors=[("sim-node-1", 9999)],
            fec_k=4,
            fec_m=2,
            target_loop_ms=16.0,
        )
        engine.start()
        try:
            # 5 KB payload -> spans 5 data chunks across 2 FEC groups
            payload = b"Flight-Payload-Alpha-" + os.urandom(5000)
            engine.write_file("/alpha.bin", payload)

            # Let it circulate for 150 ms (approx 10 network loops)
            time.sleep(0.15)

            read_back = engine.read_file("/alpha.bin")
            self.assertEqual(len(read_back), len(payload))
            self.assertEqual(read_back, payload)

            # Partial slice read
            slice_read = engine.read_file("/alpha.bin", offset=100, size=500)
            self.assertEqual(slice_read, payload[100:600])
        finally:
            engine.stop()

    def test_persistence_under_packet_loss(self):
        # 6% packet drop rate injected on network link
        transport = SimulatedNetworkTransport(base_rtt_ms=10.0, jitter_ms=1.0, packet_loss_rate=0.06)
        engine = SubZeroEngine(
            transport=transport,
            reflectors=[("sim-node-1", 9999)],
            fec_k=4,
            fec_m=2,
            target_loop_ms=20.0,
            scrub_interval_s=0.05,
        )
        engine.start()
        try:
            payload = b"Parity-Auto-Healing-Verification-" + os.urandom(4096)
            engine.write_file("/loss_test.bin", payload)

            # Let the packets circulate through multiple loss drops
            time.sleep(0.3)

            read_back = engine.read_file("/loss_test.bin")
            self.assertEqual(read_back, payload, "Data payload must match bit-for-bit despite packet drops")

            t = engine.get_telemetry()
            self.assertGreater(t.total_tx_packets, 20)
        finally:
            engine.stop()

    def test_concurrent_files_in_flight(self):
        transport = SimulatedNetworkTransport(base_rtt_ms=5.0, jitter_ms=0.5, packet_loss_rate=0.0)
        engine = SubZeroEngine(transport=transport, target_loop_ms=12.0)
        engine.start()
        try:
            engine.vfs.mkdir("/docs")
            doc1 = b"Documentation block one: ALS SubZero architecture overview."
            doc2 = b"Documentation block two: Galois field erasure coding specifications."

            engine.write_file("/docs/intro.txt", doc1)
            engine.write_file("/docs/spec.txt", doc2)

            time.sleep(0.1)

            self.assertEqual(engine.read_file("/docs/intro.txt"), doc1)
            self.assertEqual(engine.read_file("/docs/spec.txt"), doc2)

            # Unlink one file
            engine.unlink_file("/docs/intro.txt")
            with self.assertRaises(FileNotFoundError):
                engine.read_file("/docs/intro.txt")

            # Second file still intact
            self.assertEqual(engine.read_file("/docs/spec.txt"), doc2)
        finally:
            engine.stop()


if __name__ == "__main__":
    unittest.main()
