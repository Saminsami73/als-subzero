"""
ALS SubZero Dynamic Recirculation Pacer & Delay-Line Regulator.
Developed by Samin Sami.

Regulates packet circulation timing, eliminating buffer exhaustion and packet drops
when running against low-latency LAN or loopback reflectors.
"""

from __future__ import annotations

import heapq
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple


@dataclass(order=True)
class ScheduledFrame:
    release_time: float
    frame_data: bytes = field(compare=False)
    host_addr: str = field(compare=False)
    host_port: int = field(compare=False)
    inode_id: int = field(compare=False)
    chunk_idx: int = field(compare=False)


@dataclass
class PacerMetrics:
    total_tx_packets: int = 0
    total_rx_packets: int = 0
    total_tx_bytes: int = 0
    total_rx_bytes: int = 0
    min_rtt_ms: float = float("inf")
    max_rtt_ms: float = 0.0
    avg_rtt_ms: float = 0.0
    queue_depth: int = 0
    rtt_samples_count: int = 0


class RecirculationPacer:
    """
    Microsecond-precision pacing engine.
    Ensures network frames do not loop faster than target_loop_ms,
    absorbing burst traffic and preserving network stability.
    """

    def __init__(
        self,
        send_callback: Callable[[bytes, str, int], None],
        target_loop_ms: float = 40.0,
        min_inter_packet_ms: float = 0.1,
    ) -> None:
        self.send_callback = send_callback
        self.target_loop_ms = target_loop_ms
        self.min_inter_packet_ms = min_inter_packet_ms

        self._queue: List[ScheduledFrame] = []
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._running = False
        self._dispatcher_thread: Optional[threading.Thread] = None

        self._metrics = PacerMetrics()
        self._rtt_sum_ms = 0.0
        self._last_tx_time = 0.0

    def start(self) -> None:
        """Start the background paced transmission thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._dispatcher_thread = threading.Thread(
                target=self._dispatch_loop,
                name="SubZeroPacerDispatcher",
                daemon=True,
            )
            self._dispatcher_thread.start()

    def stop(self) -> None:
        """Stop the pacer dispatcher thread."""
        with self._lock:
            self._running = False
            self._cv.notify_all()
        if self._dispatcher_thread and self._dispatcher_thread.is_alive():
            self._dispatcher_thread.join(timeout=1.0)

    def record_rx(self, num_bytes: int, elapsed_rtt_ms: float) -> None:
        """Update telemetry when a reflected packet arrives."""
        with self._lock:
            self._metrics.total_rx_packets += 1
            self._metrics.total_rx_bytes += num_bytes
            self._metrics.rtt_samples_count += 1
            self._rtt_sum_ms += elapsed_rtt_ms
            self._metrics.avg_rtt_ms = self._rtt_sum_ms / self._metrics.rtt_samples_count

            if elapsed_rtt_ms < self._metrics.min_rtt_ms:
                self._metrics.min_rtt_ms = elapsed_rtt_ms
            if elapsed_rtt_ms > self._metrics.max_rtt_ms:
                self._metrics.max_rtt_ms = elapsed_rtt_ms

    def schedule_recirculation(
        self,
        frame_bytes: bytes,
        host_addr: str,
        host_port: int,
        inode_id: int,
        chunk_idx: int,
        elapsed_rtt_ms: float,
    ) -> None:
        """
        Schedule a chunk for its next reflection loop.
        If elapsed RTT < target_loop_ms, hold in pacer queue until release time.
        If elapsed RTT >= target_loop_ms, retransmit immediately.
        """
        now = time.time()
        hold_time_s = max(0.0, (self.target_loop_ms - elapsed_rtt_ms) / 1000.0)
        release_time = now + hold_time_s

        item = ScheduledFrame(
            release_time=release_time,
            frame_data=frame_bytes,
            host_addr=host_addr,
            host_port=host_port,
            inode_id=inode_id,
            chunk_idx=chunk_idx,
        )

        with self._lock:
            heapq.heappush(self._queue, item)
            self._metrics.queue_depth = len(self._queue)
            self._cv.notify()

    def transmit_immediate(
        self,
        frame_bytes: bytes,
        host_addr: str,
        host_port: int,
    ) -> None:
        """Direct immediate transmission for newly written blocks."""
        now = time.time()
        with self._lock:
            gap = (self.min_inter_packet_ms / 1000.0) - (now - self._last_tx_time)
            if gap > 0:
                time.sleep(gap)
            self._last_tx_time = time.time()
            self._metrics.total_tx_packets += 1
            self._metrics.total_tx_bytes += len(frame_bytes)

        self.send_callback(frame_bytes, host_addr, host_port)

    def _dispatch_loop(self) -> None:
        """Priority queue worker releasing frames according to microsecond schedule."""
        while True:
            with self._lock:
                while self._running and not self._queue:
                    self._cv.wait()

                if not self._running:
                    break

                now = time.time()
                earliest = self._queue[0]

                if earliest.release_time > now:
                    wait_s = earliest.release_time - now
                    self._cv.wait(timeout=wait_s)
                    continue

                item = heapq.heappop(self._queue)
                self._metrics.queue_depth = len(self._queue)

                # Smooth inter-packet gap
                gap = (self.min_inter_packet_ms / 1000.0) - (now - self._last_tx_time)
                if gap > 0:
                    time.sleep(gap)

                self._last_tx_time = time.time()
                self._metrics.total_tx_packets += 1
                self._metrics.total_tx_bytes += len(item.frame_data)

            # Transmit outside lock to prevent contention
            try:
                self.send_callback(item.frame_data, item.host_addr, item.host_port)
            except Exception:
                pass

    def get_metrics(self) -> PacerMetrics:
        with self._lock:
            return PacerMetrics(
                total_tx_packets=self._metrics.total_tx_packets,
                total_rx_packets=self._metrics.total_rx_packets,
                total_tx_bytes=self._metrics.total_tx_bytes,
                total_rx_bytes=self._metrics.total_rx_bytes,
                min_rtt_ms=self._metrics.min_rtt_ms if self._metrics.min_rtt_ms != float("inf") else 0.0,
                max_rtt_ms=self._metrics.max_rtt_ms,
                avg_rtt_ms=self._metrics.avg_rtt_ms,
                queue_depth=len(self._queue),
                rtt_samples_count=self._metrics.rtt_samples_count,
            )

