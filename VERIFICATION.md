# ALS SubZero: Verification & Benchmark Report

Tested by Samin Sami.  
ALS stands for "Al Sami" (first 3 letters of Samin Yasar AL Sami).

This report covers automated tests, packet loss benchmarks, and rate pacing measurements for ALS SubZero.

---

## 1. Unit Tests

Run the test suite:

```bash
python tests/run_all.py
```

Results:

```text
test_fec_encode_double_loss (test_fec.TestGaloisFieldAndFEC.test_fec_encode_double_loss) ... ok
test_fec_encode_single_loss (test_fec.TestGaloisFieldAndFEC.test_fec_encode_single_loss) ... ok
test_gf_arithmetic (test_fec.TestGaloisFieldAndFEC.test_gf_arithmetic) ... ok
test_insufficient_survivors_raises (test_fec.TestGaloisFieldAndFEC.test_insufficient_survivors_raises) ... ok
test_concurrent_files_in_flight (test_flight_persistence.TestFlightPersistence.test_concurrent_files_in_flight) ... ok
test_end_to_end_flight_loop (test_flight_persistence.TestFlightPersistence.test_end_to_end_flight_loop) ... ok
test_persistence_under_packet_loss (test_flight_persistence.TestFlightPersistence.test_persistence_under_packet_loss) ... ok
test_crc_tamper_detection (test_framing.TestFraming.test_crc_tamper_detection) ... ok
test_encode_decode_roundtrip (test_framing.TestFraming.test_encode_decode_roundtrip) ... ok
test_invalid_magic_rejection (test_framing.TestFraming.test_invalid_magic_rejection) ... ok
test_sequence_hop_increment (test_framing.TestFraming.test_sequence_hop_increment) ... ok
test_truncated_frame (test_framing.TestFraming.test_truncated_frame) ... ok
test_pacer_queuing_and_release (test_pacer.TestPacer.test_pacer_queuing_and_release) ... ok
test_pacer_telemetry_tracking (test_pacer.TestPacer.test_pacer_telemetry_tracking) ... ok
test_file_create_and_readdir (test_vfs.TestVFS.test_file_create_and_readdir) ... ok
test_mkdir_and_hierarchy (test_vfs.TestVFS.test_mkdir_and_hierarchy) ... ok
test_rename (test_vfs.TestVFS.test_rename) ... ok
test_root_lookup (test_vfs.TestVFS.test_root_lookup) ... ok
test_tree_string (test_vfs.TestVFS.test_tree_string) ... ok
test_unlink_file (test_vfs.TestVFS.test_unlink_file) ... ok

----------------------------------------------------------------------
Ran 20 tests in 0.801s

OK
```

All 20 test cases pass with zero external pip dependencies.

---

## 2. Packet Drop Resilience Benchmark

Run the loss benchmark:

```bash
python scripts/run_benchmark.py
```

Tested with 16,384 bytes of random data across 60 network loops under simulated packet drops:

| Loss Rate | Size | Loops | TX Packets | RX Packets | Chunks Healed | Result |
|---|---|---|---|---|---|---|
| **0.0%** | 16,384 B | 60 | 1,473 | 1,450 | 0 | **PASS** (100% match) |
| **2.0%** | 16,384 B | 60 | 1,471 | 1,430 | 19 | **PASS** (100% match) |
| **5.0%** | 16,384 B | 60 | 1,475 | 1,383 | 71 | **PASS** (100% match) |
| **10.0%** | 16,384 B | 60 | 1,472 | 1,320 | 134 | **PASS** (100% match) |

At a 10% packet drop rate, the Cauchy FEC engine reconstructed 134 lost chunks in flight. Every recovered byte matched the original file.

---

## 3. Pacer Stability

On local loopback (RTT < 1 ms), the departure pacer:
- Maintained a minimum 100-microsecond gap between departures.
- Kept average queue depth between 4 and 8 frames.
- Recorded zero socket buffer drops (`ENOBUFS`).
