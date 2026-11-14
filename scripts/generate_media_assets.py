"""
Generate high-resolution media visual assets for ALS SubZero.
Author: Samin Sami (Samin Yasar AL Sami).
Generates:
1. assets/architecture_overview.png
2. assets/benchmark_chart.png
3. assets/frame_structure.png
4. assets/recovery_pipeline.png
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def generate_architecture_overview(out_path):
    fig, ax = plt.subplots(figsize=(12, 7), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")
    ax.axis("off")

    # Title Banner
    ax.text(0.5, 0.94, "ALS SUBZERO: DYNAMIC DELAY-LINE NETWORK FILESYSTEM",
            ha="center", va="center", color="#F8FAFC", fontsize=15, weight="bold", fontfamily="sans-serif")
    ax.text(0.5, 0.89, "In-Flight Volatile Storage Architecture | Lead Engineer: Samin Sami (Al Sami)",
            ha="center", va="center", color="#38BDF8", fontsize=10, fontfamily="sans-serif")

    # Layers
    layers = [
        ("Layer 5: POSIX Virtual Filesystem (VFS)",
         "Hierarchical Inode Management | Directory Tree | open(), read(), write(), unlink() | Chunk Splitting (4096 B)",
         "#1E293B", "#38BDF8", 0.74),
        ("Layer 4: Cauchy Reed-Solomon Erasure Coding Engine",
         "Galois Field GF(2^8) Arithmetic | K=4 Data Chunks + M=2 Parity Chunks | Autonomous Background Scrubber",
         "#1E293B", "#818CF8", 0.58),
        ("Layer 3: Microsecond Departure Pacer & Rate Limiter",
         "Priority Departure Queue | Min Spacing: 100 us | Eliminates Socket Buffer Overflow on Sub-ms LANs",
         "#1E293B", "#34D399", 0.42),
        ("Layer 2: Multi-Protocol Transport Abstraction",
         "Unprivileged UDP Echo (RFC 768) | Raw ICMP Echo Requests (RFC 792) | Simulated Network Harness",
         "#1E293B", "#FBBF24", 0.26),
        ("Layer 1: Physical IP Network & Remote Echo Reflectors",
         "Continuous In-Flight Motion across Internet Routers | Bandwidth-Delay Product (C = B * RTT)",
         "#0F172A", "#F43F5E", 0.10),
    ]

    for title, desc, bg_col, border_col, y_pos in layers:
        # Box
        rect = patches.FancyBboxPatch((0.08, y_pos), 0.84, 0.11,
                                     boxstyle="round,pad=0.015,rounding_size=0.015",
                                     facecolor=bg_col, edgecolor=border_col, linewidth=2)
        ax.add_patch(rect)
        ax.text(0.12, y_pos + 0.075, title, color="#F8FAFC", fontsize=11, weight="bold", va="center")
        ax.text(0.12, y_pos + 0.035, desc, color="#94A3B8", fontsize=8.5, va="center")

    # Connective arrows
    for y_arrow in [0.71, 0.55, 0.39, 0.23]:
        ax.annotate("", xy=(0.5, y_arrow - 0.018), xytext=(0.5, y_arrow + 0.028),
                    arrowprops=dict(arrowstyle="->", color="#64748B", lw=2, mutation_scale=15))

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


def generate_benchmark_chart(out_path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=300)
    fig.patch.set_facecolor("#0F172A")

    # Data
    loss_rates = [0.0, 2.0, 5.0, 10.0]
    healed_chunks = [0, 20, 78, 151]
    rx_ratio = [1479/1498*100, 1436/1478*100, 1386/1476*100, 1307/1481*100]

    # Chart 1: FEC Healed Chunks
    ax1.set_facecolor("#1E293B")
    bars = ax1.bar([str(x) + "%" for x in loss_rates], healed_chunks, color="#38BDF8", edgecolor="#0284C7", width=0.55, linewidth=1.5)
    ax1.set_title("Self-Healing FEC Reconstructions vs. Drop Rate", color="#F8FAFC", fontsize=11, weight="bold", pad=12)
    ax1.set_xlabel("Simulated Network Packet Loss Rate", color="#94A3B8", fontsize=9)
    ax1.set_ylabel("Parity Chunks Reconstructed (60 Cycles)", color="#94A3B8", fontsize=9)
    ax1.tick_params(colors="#94A3B8", labelsize=8.5)
    ax1.grid(axis="y", linestyle="--", alpha=0.3, color="#64748B")
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 4, f"{int(yval)}", ha="center", va="bottom", color="#F8FAFC", fontsize=9, weight="bold")

    # Chart 2: Bit-Exact Recovery Rate (100% across all)
    ax2.set_facecolor("#1E293B")
    ax2.plot([str(x) + "%" for x in loss_rates], [100.0, 100.0, 100.0, 100.0], color="#10B981", marker="o", markersize=9, linewidth=3, label="Bit-Exact File Recovery (SHA256 Match)")
    ax2.plot([str(x) + "%" for x in loss_rates], rx_ratio, color="#F59E0B", marker="s", markersize=7, linewidth=2, linestyle="--", label="Raw Physical Ingress Ratio (%)")
    ax2.set_title("Data Integrity & Ingress vs. Packet Loss", color="#F8FAFC", fontsize=11, weight="bold", pad=12)
    ax2.set_xlabel("Simulated Network Packet Loss Rate", color="#94A3B8", fontsize=9)
    ax2.set_ylabel("Integrity & Delivery Percentage (%)", color="#94A3B8", fontsize=9)
    ax2.set_ylim(80, 105)
    ax2.tick_params(colors="#94A3B8", labelsize=8.5)
    ax2.grid(True, linestyle="--", alpha=0.3, color="#64748B")
    ax2.legend(facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8.5, loc="lower left")

    fig.suptitle("ALS SubZero Empirical Reliability & Recovery Performance (Samin Sami)", color="#F8FAFC", fontsize=13, weight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


def generate_frame_structure(out_path):
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")
    ax.axis("off")

    ax.text(0.5, 0.93, "ALS1 BINARY PROTOCOL FRAME SPECIFICATION",
            ha="center", va="center", color="#F8FAFC", fontsize=14, weight="bold")
    ax.text(0.5, 0.86, "24-Byte Fixed Binary Header + Variable Payload (up to 4096 B)",
            ha="center", va="center", color="#38BDF8", fontsize=9.5)

    fields = [
        ("Magic\n'ALS1'\n[0..3]", 4, "#0284C7"),
        ("Ver\n0x0100\n[4..5]", 2, "#0369A1"),
        ("Flags\nParity Bit\n[6..7]", 2, "#075985"),
        ("Inode ID\nuint32\n[8..11]", 4, "#4F46E5"),
        ("Chunk Index\nuint32\n[12..15]", 4, "#4338CA"),
        ("Payload Len\nuint16\n[16..17]", 2, "#3730A3"),
        ("Hop Count\nuint16\n[18..19]", 2, "#10B981"),
        ("CRC32C\nCastagnoli\n[20..23]", 4, "#F43F5E"),
    ]

    total_header_bytes = 24
    start_x = 0.05
    width_scale = 0.65 / total_header_bytes

    current_x = start_x
    for name, b_len, col in fields:
        w = b_len * width_scale
        rect = patches.FancyBboxPatch((current_x, 0.42), w - 0.005, 0.32,
                                     boxstyle="round,pad=0.008,rounding_size=0.01",
                                     facecolor="#1E293B", edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(current_x + (w - 0.005)/2, 0.58, name, color="#F8FAFC", fontsize=8, ha="center", va="center", weight="bold")
        current_x += w

    # Payload box
    payload_w = 0.23
    rect_payload = patches.FancyBboxPatch((current_x + 0.01, 0.42), payload_w, 0.32,
                                         boxstyle="round,pad=0.008,rounding_size=0.01",
                                         facecolor="#1E293B", edgecolor="#10B981", linewidth=2)
    ax.add_patch(rect_payload)
    ax.text(current_x + 0.01 + payload_w/2, 0.58, "Chunk Payload Data\n(0..4096 Bytes)\nRaw or Parity Stripe",
            color="#34D399", fontsize=8.5, ha="center", va="center", weight="bold")

    # Legend annotations below
    notes = [
        "Magic (0x41 0x4C 0x53 0x31): Identifies valid ALS SubZero frames; invalid packets dropped immediately.",
        "Flags: Bit 0 indicates Parity Chunk (1) or Data Chunk (0); remaining bits reserved for encryption.",
        "Castagnoli CRC32C (0x82F63B78): Covers all 20 preceding header bytes + payload; Hamming distance d=4.",
    ]
    y_note = 0.26
    for note in notes:
        ax.text(0.06, y_note, f"&bull; {note}".replace("&bull;", "-"), color="#94A3B8", fontsize=8)
        y_note -= 0.06

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


def generate_recovery_pipeline(out_path):
    fig, ax = plt.subplots(figsize=(12, 5.5), dpi=300)
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#0F172A")
    ax.axis("off")

    ax.text(0.5, 0.93, "ALS SUBZERO: IN-FLIGHT SELF-HEALING LIFECYCLE",
            ha="center", va="center", color="#F8FAFC", fontsize=14, weight="bold")
    ax.text(0.5, 0.86, "Autonomous Detection, Submatrix Inversion, and Re-Injection",
            ha="center", va="center", color="#34D399", fontsize=9.5)

    stages = [
        ("1. Ingress Capture", "Socket receives returning frame;\nextracts 24-B header;\nchecks Castagnoli CRC32C.", "#0284C7", 0.06),
        ("2. Stripe Assembly", "Buffers chunks into groups\nof K=4 data + M=2 parity;\nstarts timeout timer.", "#4F46E5", 0.29),
        ("3. Loss Detection", "Timer triggers with missing\nchunks (e.g. 1-2 dropped);\nidentifies survivors.", "#F59E0B", 0.52),
        ("4. Cauchy Inversion", "Inverts surviving submatrix\nin GF(2^8); recovers original\nbytes with 100% precision.", "#10B981", 0.75),
    ]

    for title, desc, col, x_pos in stages:
        rect = patches.FancyBboxPatch((x_pos, 0.36), 0.20, 0.38,
                                     boxstyle="round,pad=0.015,rounding_size=0.015",
                                     facecolor="#1E293B", edgecolor=col, linewidth=2)
        ax.add_patch(rect)
        ax.text(x_pos + 0.10, 0.65, title, color="#F8FAFC", fontsize=9.5, ha="center", weight="bold")
        ax.text(x_pos + 0.10, 0.48, desc, color="#94A3B8", fontsize=7.5, ha="center", va="center")

        if x_pos < 0.75:
            ax.annotate("", xy=(x_pos + 0.24, 0.55), xytext=(x_pos + 0.19, 0.55),
                        arrowprops=dict(arrowstyle="->", color="#64748B", lw=2, mutation_scale=14))

    # Re-injection return arrow
    ax.annotate("5. Paced Re-Injection: Healed frame scheduled in Departure Queue and re-sent into wire",
                xy=(0.16, 0.28), xytext=(0.85, 0.28),
                arrowprops=dict(arrowstyle="->", color="#34D399", lw=2, linestyle="--", mutation_scale=14),
                color="#34D399", fontsize=8.5, ha="center", va="center", weight="bold")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Generated: {out_path}")


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    assets_dir = os.path.join(root, "assets")
    ensure_dir(assets_dir)

    generate_architecture_overview(os.path.join(assets_dir, "architecture_overview.png"))
    generate_benchmark_chart(os.path.join(assets_dir, "benchmark_chart.png"))
    generate_frame_structure(os.path.join(assets_dir, "frame_structure.png"))
    generate_recovery_pipeline(os.path.join(assets_dir, "recovery_pipeline.png"))


if __name__ == "__main__":
    main()
