"""
ALS SubZero Multi-Protocol Network Transport Subsystem.
Developed by Samin Sami.

Provides pluggable network interfaces:
- SimulatedNetworkTransport: High-fidelity network simulation with configurable RTT, jitter, and packet loss.
- UDPReflectorTransport: Cross-platform unprivileged UDP echo reflector transport.
- RawICMPTransport: Native ICMP Echo Request / Reply raw socket transport for Linux root environments.
"""

from __future__ import annotations

import abc
import os
import random
import select
import socket
import struct
import threading
import time
from typing import Callable, List, Optional, Tuple

ReceiveCallback = Callable[[bytes, str, int], None]


class BaseTransport(abc.ABC):
    """Abstract base transport for ALS SubZero packet circulation."""

    @abc.abstractmethod
    def start(self, on_receive: ReceiveCallback) -> None:
        pass

    @abc.abstractmethod
    def send(self, data: bytes, host: str, port: int) -> None:
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        pass


class SimulatedNetworkTransport(BaseTransport):
    """
    High-fidelity simulated network link.
    Models physical propagation delay, jitter, packet loss, and reflector turnaround time.
    Allows automated verification without network privileges.
    """

    def __init__(
        self,
        base_rtt_ms: float = 20.0,
        jitter_ms: float = 2.0,
        packet_loss_rate: float = 0.0,
        reflectors: Optional[List[str]] = None,
    ) -> None:
        self.base_rtt_ms = base_rtt_ms
        self.jitter_ms = jitter_ms
        self.packet_loss_rate = packet_loss_rate
        self.reflectors = reflectors or ["sim-node-1", "sim-node-2", "sim-node-3"]

        self._on_receive: Optional[ReceiveCallback] = None
        self._running = False
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)
        self._in_flight: List[Tuple[float, bytes, str, int]] = []
        self._worker_thread: Optional[threading.Thread] = None

    def start(self, on_receive: ReceiveCallback) -> None:
        with self._lock:
            self._on_receive = on_receive
            self._running = True
            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                name="SimulatedNetworkWorker",
                daemon=True,
            )
            self._worker_thread.start()

    def stop(self) -> None:
        with self._lock:
            self._running = False
            self._cv.notify_all()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)

    def send(self, data: bytes, host: str, port: int) -> None:
        # Check simulated packet drop
        if self.packet_loss_rate > 0.0 and random.random() < self.packet_loss_rate:
            # Packet dropped in simulated transit
            return

        # Calculate arrival time with simulated RTT and jitter
        delay_ms = max(1.0, self.base_rtt_ms + random.gauss(0, self.jitter_ms))
        arrival_time = time.time() + (delay_ms / 1000.0)

        with self._lock:
            self._in_flight.append((arrival_time, data, host, port))
            # Keep sorted by arrival time
            self._in_flight.sort(key=lambda x: x[0])
            self._cv.notify()

    def _worker_loop(self) -> None:
        while True:
            with self._lock:
                while self._running and not self._in_flight:
                    self._cv.wait()

                if not self._running:
                    break

                now = time.time()
                earliest_time, data, host, port = self._in_flight[0]

                if earliest_time > now:
                    wait_s = earliest_time - now
                    self._cv.wait(timeout=wait_s)
                    continue

                self._in_flight.pop(0)

            # Deliver packet to receiver
            if self._on_receive:
                try:
                    self._on_receive(data, host, port)
                except Exception:
                    pass


class UDPReflectorTransport(BaseTransport):
    """
    Standard UDP echo transport.
    Transmits frames to UDP echo reflectors (e.g. port 7 or dedicated SubZeroReflector)
    and receives the reflected payload.
    Fully unprivileged and cross-platform across Windows, Linux, and macOS.
    """

    def __init__(self, bind_port: int = 0) -> None:
        self.bind_port = bind_port
        self._sock: Optional[socket.socket] = None
        self._on_receive: Optional[ReceiveCallback] = None
        self._running = False
        self._rx_thread: Optional[threading.Thread] = None

    def start(self, on_receive: ReceiveCallback) -> None:
        self._on_receive = on_receive
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 * 1024 * 1024)
        self._sock.bind(("0.0.0.0", self.bind_port))
        self._running = True

        self._rx_thread = threading.Thread(
            target=self._rx_loop,
            name="UDPRxWorker",
            daemon=True,
        )
        self._rx_thread.start()

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if self._rx_thread and self._rx_thread.is_alive():
            self._rx_thread.join(timeout=1.0)

    def send(self, data: bytes, host: str, port: int) -> None:
        if self._sock:
            self._sock.sendto(data, (host, port))

    def _rx_loop(self) -> None:
        assert self._sock is not None
        while self._running:
            try:
                r, _, _ = select.select([self._sock], [], [], 0.5)
                if not r:
                    continue
                data, addr = self._sock.recvfrom(2048)
                if self._on_receive:
                    self._on_receive(data, addr[0], addr[1])
            except (socket.error, OSError):
                if not self._running:
                    break


class StandaloneUDPReflector:
    """
    Standalone UDP reflector service.
    Runs on remote hosts or test nodes to echo back incoming ALS SubZero packets.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 9999) -> None:
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.host, self.port))
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="UDPReflectorServer", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    def _loop(self) -> None:
        assert self._sock is not None
        while self._running:
            try:
                r, _, _ = select.select([self._sock], [], [], 0.5)
                if not r:
                    continue
                data, addr = self._sock.recvfrom(2048)
                self._sock.sendto(data, addr)
            except (socket.error, OSError):
                if not self._running:
                    break


class RawICMPTransport(BaseTransport):
    """
    Native raw socket ICMP transport.
    Sends standard ICMP Echo Requests (Type 8) with ALS SubZero frames as payload.
    Parses incoming ICMP Echo Replies (Type 0).
    Requires superuser capabilities (CAP_NET_RAW or root on Linux).
    """

    def __init__(self) -> None:
        self._sock: Optional[socket.socket] = None
        self._on_receive: Optional[ReceiveCallback] = None
        self._running = False
        self._rx_thread: Optional[threading.Thread] = None

    def start(self, on_receive: ReceiveCallback) -> None:
        self._on_receive = on_receive
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 * 1024 * 1024)
        except PermissionError as exc:
            raise PermissionError(
                "Raw ICMP socket requires root or CAP_NET_RAW privileges. "
                "Use UDPReflectorTransport or run with sudo."
            ) from exc

        self._running = True
        self._rx_thread = threading.Thread(
            target=self._rx_loop,
            name="RawICMPRxWorker",
            daemon=True,
        )
        self._rx_thread.start()

    def stop(self) -> None:
        self._running = False
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
        if self._rx_thread and self._rx_thread.is_alive():
            self._rx_thread.join(timeout=1.0)

    def send(self, data: bytes, host: str, port: int = 0) -> None:
        if not self._sock:
            return

        # Format ICMP Echo Request header (Type 8, Code 0, Checksum 0, ID 0, Seq 0)
        icmp_header = struct.pack("!BBHHH", 8, 0, 0, 0x5353, 1)
        chk = self._checksum(icmp_header + data)
        icmp_header = struct.pack("!BBHHH", 8, 0, chk, 0x5353, 1)

        packet = icmp_header + data
        try:
            self._sock.sendto(packet, (host, 0))
        except OSError:
            pass

    def _rx_loop(self) -> None:
        assert self._sock is not None
        while self._running:
            try:
                r, _, _ = select.select([self._sock], [], [], 0.5)
                if not r:
                    continue
                packet, addr = self._sock.recvfrom(2048)

                # Skip IPv4 header (usually 20 bytes)
                if len(packet) < 28:
                    continue
                ip_header_len = (packet[0] & 0x0F) * 4
                icmp_packet = packet[ip_header_len:]

                if len(icmp_packet) < 8:
                    continue
                icmp_type, icmp_code = icmp_packet[0], icmp_packet[1]

                # Only handle ICMP Echo Reply (Type 0)
                if icmp_type == 0:
                    payload = icmp_packet[8:]
                    if self._on_receive:
                        self._on_receive(payload, addr[0], 0)
            except (socket.error, OSError):
                if not self._running:
                    break

    @staticmethod
    def _checksum(data: bytes) -> int:
        if len(data) % 2 == 1:
            data += b"\x00"
        words = struct.unpack(f"!{len(data)//2}H", data)
        total = sum(words)
        while total >> 16:
            total = (total & 0xFFFF) + (total >> 16)
        return (~total) & 0xFFFF

