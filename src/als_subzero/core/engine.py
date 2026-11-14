"""
ALS SubZero Master Delay-Line Storage Engine.
Developed by Samin Sami.

Orchestrates the Virtual Filesystem, Recirculation Pacer, Galois Field FEC Scrubber,
and Network Transports.
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from als_subzero.core.framing import (
    CHUNK_SIZE,
    FLAG_LAST_CHUNK,
    FLAG_PARITY,
    FLAG_RECONSTRUCTED,
    ChunkFrame,
    decode_frame,
    encode_frame,
)
from als_subzero.core.pacer import RecirculationPacer
from als_subzero.fec.parity import CauchyErasureCodec
from als_subzero.net.transport import BaseTransport, SimulatedNetworkTransport
from als_subzero.vfs.filesystem import Inode, VirtualFileSystem


@dataclass
class EngineTelemetry:
    active_files: int
    total_bytes_in_flight: int
    data_chunks_in_flight: int
    parity_chunks_in_flight: int
    fec_recovered_chunks: int
    total_rx_packets: int
    total_tx_packets: int
    avg_rtt_ms: float
    pacer_queue_depth: int


class SubZeroEngine:
    """
    Central storage engine for ALS SubZero.
    Maintains volatile storage exclusively in network circulation,
    applying forward error correction and rate pacing.
    """

    def __init__(
        self,
        transport: Optional[BaseTransport] = None,
        reflectors: Optional[List[Tuple[str, int]]] = None,
        fec_k: int = 4,
        fec_m: int = 2,
        target_loop_ms: float = 30.0,
        scrub_interval_s: float = 0.1,
    ) -> None:
        self.fec_k = fec_k
        self.fec_m = fec_m
        self.target_loop_ms = target_loop_ms
        self.scrub_interval_s = scrub_interval_s

        self.reflectors = reflectors or [("127.0.0.1", 9999)]
        self._reflector_idx = 0

        self.vfs = VirtualFileSystem(default_k=fec_k, default_m=fec_m)
        self.codec = CauchyErasureCodec(k=fec_k, m=fec_m)
        self.transport = transport or SimulatedNetworkTransport(base_rtt_ms=10.0, jitter_ms=1.0)

        self.pacer = RecirculationPacer(
            send_callback=self._raw_send,
            target_loop_ms=target_loop_ms,
        )

        # In-flight chunk tracking: (inode_id, chunk_idx) -> (ChunkFrame, last_seen_timestamp)
        self._flight_table: Dict[Tuple[int, int], Tuple[ChunkFrame, float]] = {}
        # Track total data chunks for each file: inode_id -> int
        self._inode_data_chunks: Dict[int, int] = {}
        # Track all active chunks (data + parity) for each file: inode_id -> set of chunk_indices
        self._file_chunks: Dict[int, Set[int]] = {}
        # Track parity chunk indices: inode_id -> set of chunk_indices
        self._parity_chunks: Dict[int, Set[int]] = {}

        # Notification condition for reader threads waiting for a specific chunk
        self._lock = threading.Lock()
        self._read_cv = threading.Condition(self._lock)

        self._running = False
        self._scrubber_thread: Optional[threading.Thread] = None
        self._fec_recovered_count = 0

    def start(self) -> None:
        """Start network transport, pacer, and background FEC scrubber."""
        with self._lock:
            if self._running:
                return
            self._running = True

        self.transport.start(on_receive=self._on_packet_received)
        self.pacer.start()

        self._scrubber_thread = threading.Thread(
            target=self._scrubber_loop,
            name="SubZeroFECScrubber",
            daemon=True,
        )
        self._scrubber_thread.start()

    def stop(self) -> None:
        """Gracefully shut down all background threads and transports."""
        with self._lock:
            self._running = False
            self._read_cv.notify_all()

        if self._scrubber_thread and self._scrubber_thread.is_alive():
            self._scrubber_thread.join(timeout=1.0)

        self.pacer.stop()
        self.transport.stop()

    def _next_reflector(self) -> Tuple[str, int]:
        with self._lock:
            ref = self.reflectors[self._reflector_idx % len(self.reflectors)]
            self._reflector_idx += 1
            return ref

    def _raw_send(self, data: bytes, host: str, port: int) -> None:
        self.transport.send(data, host, port)

    def _on_packet_received(self, raw_data: bytes, host: str, port: int) -> None:
        """Handler invoked whenever a reflected packet returns from the network."""
        try:
            frame = decode_frame(raw_data)
        except Exception:
            # Drop malformed or corrupted frames
            return

        now = time.time()
        now_us = int(now * 1_000_000) & 0xFFFFFFFF
        elapsed_us = (now_us - frame.epoch_us) & 0xFFFFFFFF
        elapsed_ms = max(0.1, elapsed_us / 1000.0)

        key = (frame.inode_id, frame.chunk_idx)

        with self._lock:
            # Check if this chunk belongs to an active file
            if frame.inode_id not in self._file_chunks:
                # File was unlinked, do not recirculate
                return

            if frame.chunk_idx not in self._file_chunks[frame.inode_id]:
                # Stale chunk
                return

            # Update in-flight state and notify waiting reader
            self._flight_table[key] = (frame, now)
            self._read_cv.notify_all()

        # Record telemetry in pacer
        self.pacer.record_rx(len(raw_data), elapsed_ms)

        # Prepare frame for next hop
        frame.next_hop()
        next_host, next_port = self._next_reflector()
        next_bytes = encode_frame(
            inode_id=frame.inode_id,
            chunk_idx=frame.chunk_idx,
            fec_group=frame.fec_group,
            chunk_in_group=frame.chunk_in_group,
            payload=frame.payload,
            flags=frame.flags,
            seqno=frame.seqno,
            epoch_us=frame.epoch_us,
        )

        # Schedule recirculation through the pacer
        self.pacer.schedule_recirculation(
            frame_bytes=next_bytes,
            host_addr=next_host,
            host_port=next_port,
            inode_id=frame.inode_id,
            chunk_idx=frame.chunk_idx,
            elapsed_rtt_ms=elapsed_ms,
        )

    def write_file(self, path: str, data: bytes) -> Inode:
        """
        Split file data into blocks, compute Reed-Solomon parity,
        and inject all chunks into network recirculation.
        """
        inode = self.vfs.create_file(path)
        inode_id = inode.inode_id

        # Clean previous chunks if overwriting
        self._cleanup_inode_chunks(inode_id)

        chunk_payloads: List[bytes] = []
        if not data:
            chunk_payloads.append(b"")
        else:
            for offset in range(0, len(data), CHUNK_SIZE):
                chunk_payloads.append(data[offset : offset + CHUNK_SIZE])

        total_data_chunks = len(chunk_payloads)
        total_groups = math.ceil(total_data_chunks / self.fec_k)

        all_registered_chunks: Set[int] = set()
        parity_chunks_set: Set[int] = set()

        with self._lock:
            self._file_chunks[inode_id] = all_registered_chunks
            self._parity_chunks[inode_id] = parity_chunks_set
            self._inode_data_chunks[inode_id] = total_data_chunks

        # Encode in groups of K
        for g_idx in range(total_groups):
            g_start = g_idx * self.fec_k
            g_data = chunk_payloads[g_start : g_start + self.fec_k]

            actual_count = len(g_data)
            padded_group = list(g_data)
            while len(padded_group) < self.fec_k:
                padded_group.append(b"")

            # Generate M parity chunks
            parity_payloads = self.codec.encode(padded_group)

            # Transmit data chunks in this group: indices g_start .. g_start + actual_count - 1
            for in_grp, payload in enumerate(g_data):
                d_chunk_idx = g_start + in_grp
                is_last = (d_chunk_idx == (total_data_chunks - 1))
                flags = 0
                if is_last:
                    flags |= FLAG_LAST_CHUNK

                frame_bytes = encode_frame(
                    inode_id=inode_id,
                    chunk_idx=d_chunk_idx,
                    fec_group=g_idx,
                    chunk_in_group=in_grp,
                    payload=payload,
                    flags=flags,
                    seqno=0,
                )

                with self._lock:
                    all_registered_chunks.add(d_chunk_idx)
                    frame = decode_frame(frame_bytes)
                    self._flight_table[(inode_id, d_chunk_idx)] = (frame, time.time())

                host, port = self._next_reflector()
                self.pacer.transmit_immediate(frame_bytes, host, port)

            # Transmit M parity chunks for this group: indices total_data_chunks + (g_idx * M) + p_idx
            for p_idx, p_data in enumerate(parity_payloads):
                p_chunk_idx = total_data_chunks + (g_idx * self.fec_m) + p_idx
                flags = FLAG_PARITY

                frame_bytes = encode_frame(
                    inode_id=inode_id,
                    chunk_idx=p_chunk_idx,
                    fec_group=g_idx,
                    chunk_in_group=self.fec_k + p_idx,
                    payload=p_data,
                    flags=flags,
                    seqno=0,
                )

                with self._lock:
                    all_registered_chunks.add(p_chunk_idx)
                    parity_chunks_set.add(p_chunk_idx)
                    frame = decode_frame(frame_bytes)
                    self._flight_table[(inode_id, p_chunk_idx)] = (frame, time.time())

                host, port = self._next_reflector()
                self.pacer.transmit_immediate(frame_bytes, host, port)

        inode.size = len(data)
        inode.chunk_indices = sorted(list(all_registered_chunks - parity_chunks_set))
        inode.modified_at = time.time()
        return inode

    def read_file(
        self,
        path: str,
        offset: int = 0,
        size: Optional[int] = None,
        timeout_s: float = 4.0,
    ) -> bytes:
        """
        Assemble file content by capturing in-flight chunks or reconstructing
        missing chunks via Cauchy Reed-Solomon parity.
        """
        inode = self.vfs.lookup(path)
        if not inode:
            raise FileNotFoundError(f"File not found: {path}")
        if inode.is_directory:
            raise IsADirectoryError(f"Cannot read directory: {path}")

        file_size = inode.size
        if file_size == 0 or offset >= file_size:
            return b""

        read_len = (file_size - offset) if size is None else min(size, file_size - offset)
        end_offset = offset + read_len

        start_chunk = offset // CHUNK_SIZE
        end_chunk = (end_offset - 1) // CHUNK_SIZE

        needed_chunks = list(range(start_chunk, end_chunk + 1))
        assembled_chunks: Dict[int, bytes] = {}

        deadline = time.time() + timeout_s

        for c_idx in needed_chunks:
            chunk_data = self._fetch_or_reconstruct_chunk(inode.inode_id, c_idx, deadline)
            if chunk_data is None:
                raise IOError(f"Read failure: chunk {c_idx} unrecoverable within timeout")
            assembled_chunks[c_idx] = chunk_data

        buffer = bytearray()
        for c_idx in needed_chunks:
            c_offset = c_idx * CHUNK_SIZE
            data = assembled_chunks[c_idx]
            slice_start = max(0, offset - c_offset)
            slice_end = min(len(data), end_offset - c_offset)
            if slice_start < slice_end:
                buffer.extend(data[slice_start:slice_end])

        return bytes(buffer)

    def _fetch_or_reconstruct_chunk(
        self,
        inode_id: int,
        chunk_idx: int,
        deadline: float,
    ) -> Optional[bytes]:
        """Fetch chunk from in-flight memory or reconstruct using parity."""
        key = (inode_id, chunk_idx)

        # Check if recently received in flight
        with self._lock:
            if key in self._flight_table:
                frame, last_seen = self._flight_table[key]
                if time.time() - last_seen < (self.target_loop_ms * 2.5 / 1000.0):
                    return frame.payload

        # Wait bounded time (approx one RTT window) before triggering FEC reconstruction
        wait_window = min(0.08, max(0.02, (self.target_loop_ms * 1.5) / 1000.0))
        wait_until = min(deadline, time.time() + wait_window)

        while time.time() < wait_until:
            wait_s = max(0.005, wait_until - time.time())
            with self._lock:
                if key in self._flight_table:
                    frame, _ = self._flight_table[key]
                    return frame.payload
                self._read_cv.wait(timeout=wait_s)

        # Timeout elapsed: perform mathematical FEC reconstruction
        return self._reconstruct_chunk_via_fec(inode_id, chunk_idx)

    def _reconstruct_chunk_via_fec(self, inode_id: int, chunk_idx: int) -> Optional[bytes]:
        """Mathematically reconstruct a missing chunk using surviving group fragments."""
        g_idx = chunk_idx // self.fec_k
        in_group_idx = chunk_idx % self.fec_k

        survivors: List[Tuple[int, bytes]] = []

        with self._lock:
            total_data_chunks = self._inode_data_chunks.get(inode_id, 0)
            if total_data_chunks == 0:
                return None

            # Collect surviving data chunks in group g_idx
            for d_idx in range(self.fec_k):
                d_c_idx = (g_idx * self.fec_k) + d_idx
                if d_c_idx < total_data_chunks:
                    k_key = (inode_id, d_c_idx)
                    if k_key in self._flight_table:
                        survivors.append((d_idx, self._flight_table[k_key][0].payload))
                else:
                    # Trailing padding chunk is known to be b""
                    survivors.append((d_idx, b""))

            # Collect surviving parity chunks in group g_idx
            for p_idx in range(self.fec_m):
                p_c_idx = total_data_chunks + (g_idx * self.fec_m) + p_idx
                p_key = (inode_id, p_c_idx)
                if p_key in self._flight_table:
                    survivors.append((self.fec_k + p_idx, self._flight_table[p_key][0].payload))

        if len(survivors) < self.fec_k:
            return None

        try:
            target_len = max(len(data) for _, data in survivors) if survivors else 0
            recovered = self.codec.decode(survivors, target_len=target_len)
            reconstructed_payload = recovered[in_group_idx]

            # Re-inject reconstructed chunk into flight path
            frame_bytes = encode_frame(
                inode_id=inode_id,
                chunk_idx=chunk_idx,
                fec_group=g_idx,
                chunk_in_group=in_group_idx,
                payload=reconstructed_payload,
                flags=FLAG_RECONSTRUCTED,
                seqno=1,
            )
            with self._lock:
                frame = decode_frame(frame_bytes)
                self._flight_table[(inode_id, chunk_idx)] = (frame, time.time())
                self._fec_recovered_count += 1
                self._read_cv.notify_all()

            host, port = self._next_reflector()
            self.pacer.transmit_immediate(frame_bytes, host, port)
            return reconstructed_payload
        except Exception:
            return None

    def _scrubber_loop(self) -> None:
        """
        Background autonomous parity scrubber.
        Continuously scans active files, detects dropped frames,
        and regenerates missing chunks before data loss occurs.
        """
        while True:
            time.sleep(self.scrub_interval_s)
            with self._lock:
                if not self._running:
                    break
                active_files = list(self._file_chunks.keys())

            now = time.time()
            stale_threshold_s = (self.target_loop_ms * 2.5) / 1000.0

            for inode_id in active_files:
                with self._lock:
                    chunks = set(self._file_chunks.get(inode_id, set()))
                    parity_set = set(self._parity_chunks.get(inode_id, set()))

                for c_idx in chunks:
                    key = (inode_id, c_idx)
                    needs_reconstruction = False
                    with self._lock:
                        if key not in self._flight_table:
                            needs_reconstruction = True
                        else:
                            _, last_seen = self._flight_table[key]
                            if (now - last_seen) > stale_threshold_s:
                                needs_reconstruction = True

                    if needs_reconstruction:
                        if c_idx not in parity_set:
                            self._reconstruct_chunk_via_fec(inode_id, c_idx)

    def unlink_file(self, path: str) -> None:
        """Remove file from VFS and withdraw chunks from flight."""
        inode = self.vfs.unlink(path)
        self._cleanup_inode_chunks(inode.inode_id)

    def _cleanup_inode_chunks(self, inode_id: int) -> None:
        """Deregister all chunks for an inode."""
        with self._lock:
            if inode_id in self._file_chunks:
                for c_idx in self._file_chunks[inode_id]:
                    self._flight_table.pop((inode_id, c_idx), None)
                del self._file_chunks[inode_id]
            self._parity_chunks.pop(inode_id, None)
            self._inode_data_chunks.pop(inode_id, None)

    def get_telemetry(self) -> EngineTelemetry:
        """Return real-time operational telemetry."""
        pacer_metrics = self.pacer.get_metrics()
        with self._lock:
            active_files = len(self._file_chunks)
            total_flight_chunks = len(self._flight_table)
            parity_chunks = sum(len(p) for p in self._parity_chunks.values())
            data_chunks = total_flight_chunks - parity_chunks
            total_bytes = sum(len(f.payload) for f, _ in self._flight_table.values())

            return EngineTelemetry(
                active_files=active_files,
                total_bytes_in_flight=total_bytes,
                data_chunks_in_flight=max(0, data_chunks),
                parity_chunks_in_flight=parity_chunks,
                fec_recovered_chunks=self._fec_recovered_count,
                total_rx_packets=pacer_metrics.total_rx_packets,
                total_tx_packets=pacer_metrics.total_tx_packets,
                avg_rtt_ms=pacer_metrics.avg_rtt_ms,
                pacer_queue_depth=pacer_metrics.queue_depth,
            )

