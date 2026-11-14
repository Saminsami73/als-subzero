"""
Unit tests for Recirculation Pacer rate shaping.
ALS SubZero - Developed by Samin Sami.
"""

import os
import sys
import time
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from als_subzero.core.pacer import RecirculationPacer


class TestPacer(unittest.TestCase):
    def test_pacer_queuing_and_release(self):
        transmitted = []

        def mock_send(data: bytes, host: str, port: int) -> None:
            transmitted.append((time.time(), data, host, port))

        pacer = RecirculationPacer(
            send_callback=mock_send,
            target_loop_ms=25.0,
            min_inter_packet_ms=1.0,
        )
        pacer.start()
        try:
            # Simulate a packet arriving on a sub-millisecond LAN (elapsed RTT = 0.5 ms)
            start_time = time.time()
            pacer.schedule_recirculation(
                frame_bytes=b"paced_packet",
                host_addr="127.0.0.1",
                host_port=9999,
                inode_id=1,
                chunk_idx=0,
                elapsed_rtt_ms=0.5,
            )

            # Check that pacer delayed release until target_loop_ms (approx 25ms)
            time.sleep(0.04)
            self.assertEqual(len(transmitted), 1)
            elapsed_release = (transmitted[0][0] - start_time) * 1000.0
            self.assertGreaterEqual(elapsed_release, 20.0)
        finally:
            pacer.stop()

    def test_pacer_telemetry_tracking(self):
        pacer = RecirculationPacer(lambda *args: None)
        pacer.record_rx(num_bytes=100, elapsed_rtt_ms=15.0)
        pacer.record_rx(num_bytes=100, elapsed_rtt_ms=25.0)

        m = pacer.get_metrics()
        self.assertEqual(m.total_rx_packets, 2)
        self.assertEqual(m.total_rx_bytes, 200)
        self.assertEqual(m.min_rtt_ms, 15.0)
        self.assertEqual(m.max_rtt_ms, 25.0)
        self.assertEqual(m.avg_rtt_ms, 20.0)


if __name__ == "__main__":
    unittest.main()
