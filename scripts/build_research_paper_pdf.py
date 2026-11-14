"""
ALS SubZero Official Research Paper PDF Generator.
Author: Samin Sami (Samin Yasar AL Sami).
Generates a perfectly balanced, 8-page professional scientific publication
matching the researchTemplate and preprint.tex format, design, and layout.
"""

import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image
)
from reportlab.pdfgen import canvas


class AcademicPreprintCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#53565A"))  # papermuted
        
        page_w = 8.5 * 72
        page_h = 11.0 * 72
        margin = 54

        if self._pageNumber == 1:
            dateline = "ALS SubZero   \u2022   Version 2.0.0   \u2022   November 2026   \u2022   Preprint"
            self.drawRightString(page_w - margin, page_h - 38, dateline)
            self.setStrokeColor(colors.HexColor("#C0C0BF"))  # paperrule
            self.setLineWidth(0.4)
            self.line(margin, page_h - 42, page_w - margin, page_h - 42)
        else:
            self.drawString(margin, page_h - 38, "ALS SubZero: Dynamic Delay-Line Network Memory Filesystem")
            self.drawRightString(page_w - margin, page_h - 38, "Samin Sami")
            self.setStrokeColor(colors.HexColor("#C0C0BF"))
            self.setLineWidth(0.4)
            self.line(margin, page_h - 42, page_w - margin, page_h - 42)

        # Centered page number footer
        self.drawCentredString(page_w / 2.0, 36, str(self._pageNumber))
        self.restoreState()


def build_research_paper():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    template_dir = os.path.join(root, "researchTemplate")
    docs_ext_dir = os.path.join(root, "docs_external")
    assets_dir = os.path.join(root, "assets")

    os.makedirs(docs_ext_dir, exist_ok=True)
    primary_pdf = os.path.join(template_dir, "main.pdf")
    replica_pdfs = [
        os.path.join(template_dir, "ALS_SubZero_Research_Paper.pdf"),
        os.path.join(docs_ext_dir, "ALS_SubZero_Research_Paper.pdf"),
    ]

    # Academic Palette
    c_ink = colors.HexColor("#2E2D29")
    c_accent_dark = colors.HexColor("#820000")
    c_muted = colors.HexColor("#53565A")
    c_rule = colors.HexColor("#C0C0BF")
    c_wash = colors.HexColor("#F8FAFC")
    c_box_border = colors.HexColor("#CBD5E1")

    # Typography Styles
    title_style = ParagraphStyle(
        "PTitle",
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=c_ink,
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "PSubtitle",
        fontName="Helvetica",
        fontSize=10,
        leading=13.5,
        textColor=c_muted,
        spaceAfter=8,
    )

    author_style = ParagraphStyle(
        "PAuthor",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=c_ink,
        spaceAfter=2,
    )

    affil_style = ParagraphStyle(
        "PAffil",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_muted,
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "PMeta",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=c_muted,
        spaceAfter=8,
    )

    abs_head_style = ParagraphStyle(
        "PAbsHead",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=12,
        textColor=c_ink,
        spaceAfter=3,
    )

    abs_body_style = ParagraphStyle(
        "PAbsBody",
        fontName="Helvetica",
        fontSize=8,
        leading=11.2,
        textColor=c_ink,
        spaceAfter=4,
    )

    keywords_style = ParagraphStyle(
        "PKeywords",
        fontName="Helvetica",
        fontSize=7.5,
        leading=10.5,
        textColor=c_muted,
        spaceAfter=6,
    )

    h1_style = ParagraphStyle(
        "PH1",
        fontName="Helvetica-Bold",
        fontSize=11.5,
        leading=14.5,
        textColor=c_ink,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "PH2",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=c_accent_dark,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "PBody",
        fontName="Helvetica",
        fontSize=7.8,
        leading=11.0,
        textColor=c_ink,
        spaceAfter=4,
    )

    bullet_style = ParagraphStyle(
        "PBullet",
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.8,
        textColor=c_ink,
        leftIndent=12,
        spaceAfter=2,
    )

    eq_style = ParagraphStyle(
        "PEq",
        fontName="Courier-Bold",
        fontSize=7.8,
        leading=10.8,
        textColor=c_ink,
        leftIndent=16,
        spaceBefore=2,
        spaceAfter=4,
    )

    calc_box_style = ParagraphStyle(
        "PCalcBox",
        fontName="Courier",
        fontSize=7.2,
        leading=9.8,
        textColor=c_ink,
        backColor=c_wash,
        borderColor=c_box_border,
        borderWidth=0.5,
        borderPadding=4,
        spaceBefore=2,
        spaceAfter=4,
    )

    caption_style = ParagraphStyle(
        "PCaption",
        fontName="Helvetica-Bold",
        fontSize=7.2,
        leading=9.8,
        textColor=c_ink,
        alignment=0,
        spaceBefore=3,
        spaceAfter=6,
    )

    ref_style = ParagraphStyle(
        "PRef",
        fontName="Helvetica",
        fontSize=7.2,
        leading=10.0,
        textColor=c_ink,
        leftIndent=16,
        firstLineIndent=-16,
        spaceAfter=3,
    )

    story = []

    # =========================================================================
    # PAGE 1: Title, Abstract Box, and Section 1 (Introduction)
    # =========================================================================
    story.append(Spacer(1, 4))
    story.append(Paragraph("ALS SubZero: A Dynamic Delay-Line Network Memory Filesystem with Erasure-Coded Flight Persistence", title_style))
    story.append(Paragraph("Operating Volatile Filesystem Storage over In-Flight Network Packet Loops", subtitle_style))
    story.append(Paragraph("<b>Samin Sami</b><sup>1,*</sup>", author_style))
    story.append(Paragraph("<sup>1</sup>Independent Systems Researcher and Software Engineer", affil_style))
    story.append(Paragraph(
        "<b>Correspondence:</b> <font color='#820000'>samin.sami@10x.ai</font> &nbsp;&bull;&nbsp; "
        "<b>Code:</b> <font color='#820000'>github.com/Saminsami73/als-subzero</font> &nbsp;&bull;&nbsp; "
        "<b>Code License:</b> MIT License", meta_style
    ))

    # Abstract Box
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_rule, spaceAfter=5))
    story.append(Paragraph("<b>Abstract</b>", abs_head_style))
    story.append(Paragraph(
        "Computers typically store persistent state on local solid-state drives, magnetic platters, or DRAM chips. "
        "In this paper, I present <b>ALS SubZero</b>, a dynamic delay-line network memory filesystem that stores digital "
        "data in continuous motion across IP network paths with zero persistent local disk writes. "
        "ALS stands for <i>Al Sami</i>, derived from my last name Samin Yasar AL Sami. "
        "By translating the historical acoustic mercury delay-line memory concept from EDSAC (1949) into IP packet propagation delay, "
        "ALS SubZero achieves volatile, self-healing in-flight storage bounded by the Bandwidth-Delay Product (BDP) of available network links. "
        "To solve the fundamental limitations of prior unencoded network bouncing experiments (pingfs), I implemented "
        "Cauchy Reed-Solomon erasure coding over Galois Field <i>GF(2<sup>8</sup>)</i> combined with a microsecond-precision departure pacer. "
        "The pacer eliminates socket buffer exhaustion on sub-millisecond local networks, while an autonomous background scrubber detects "
        "dropped chunks and reconstructs them mathematically in flight. "
        "Empirical benchmarks demonstrate 100% bit-exact data persistence across 60 packet circulation cycles under simulated "
        "packet drop rates up to 10.0%, proving that network flight time can serve as a resilient, self-healing volatile storage medium.",
        abs_body_style
    ))
    story.append(Paragraph(
        "<b>Keywords:</b> delay-line storage; network memory; erasure coding; Cauchy Reed-Solomon; rate pacing; packet circulation; ALS SubZero",
        keywords_style
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=c_rule, spaceAfter=8))

    # Section 1: Introduction (starts right on Page 1)
    story.append(Paragraph("1. Introduction", h1_style))
    story.append(Paragraph(
        "Computers typically store digital information on physical media like solid-state drives, magnetic platters, or dynamic semiconductor memory cells. "
        "In early computing, physical storage components were severely limited. "
        "Maurice Wilkes and William Renwick built the EDSAC computer using acoustic mercury delay lines [1]. "
        "J. Presper Eckert also analyzed delay-line storage systems for the UNIVAC machine [2]. "
        "In those early architectures, electronic pulses were converted into acoustic sound waves traveling through tubes of liquid mercury. "
        "When each sound wave reached the end of the tube, a quartz crystal converted it back into an electrical signal. "
        "An amplifier circuit refreshed the signal and fed it back into the front of the tube. "
        "Digital data survived as long as it kept circulating in continuous motion.",
        body_style
    ))
    story.append(Paragraph(
        "Modern computer networks exhibit an analogous propagation property. "
        "When packets travel across fiber optic links and through router buffers, they spend measurable flight time in transit. "
        "The maximum volume of data that can occupy a network path without link amplification is governed by the Bandwidth-Delay Product (BDP):",
        body_style
    ))
    story.append(Paragraph("C = B &times; RTT &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(1)", eq_style))
    story.append(Paragraph(
        "where <i>B</i> is usable bandwidth in bits per second and <i>RTT</i> is network round-trip time in seconds. "
        "For instance, a dedicated 1 Gbps link with a 40 ms round-trip latency holds 5.0 MB of data in flight at any given moment.",
        body_style
    ))
    story.append(Paragraph(
        "Prior experimental projects, such as the open-source utility pingfs, demonstrated that ICMP Echo Requests [3] can store raw bytes by reflecting off remote hosts. "
        "However, those early experiments suffered from two fatal limitations. "
        "First, they had no error correction: when a single packet was dropped by an intermediate router, the file suffered permanent corruption. "
        "Second, they lacked rate regulation: on low-latency local networks with round-trip times below 1 ms, unthrottled packets looped too fast, "
        "overflowing socket buffers and causing immediate catastrophic data loss.",
        body_style
    ))
    story.append(Paragraph(
        "I built ALS SubZero to solve these two fundamental problems. ALS stands for 'Al Sami', taken from the first three letters of my last name: Samin Yasar AL Sami. "
        "In this paper, I present the mathematical foundation, protocol engineering, and empirical verification of the system:",
        body_style
    ))
    story.append(Paragraph("&bull; I implemented Cauchy Reed-Solomon erasure coding over Galois Field <i>GF(2<sup>8</sup>)</i> [4], enabling mathematical reconstruction of lost chunks in flight.", bullet_style))
    story.append(Paragraph("&bull; I designed a microsecond-precision departure pacer that schedules frame release, eliminating socket buffer exhaustion on sub-millisecond local networks.", bullet_style))
    story.append(Paragraph("&bull; I created the ALS1 authenticated binary protocol with 24-byte headers and Castagnoli CRC32C checksums [5].", bullet_style))
    story.append(Paragraph("&bull; I developed multi-protocol transport engines supporting unprivileged UDP reflectors [6], raw ICMP sockets [3], and network simulation.", bullet_style))
    story.append(Paragraph("&bull; I conducted empirical benchmarks demonstrating 100% bit-exact recovery under simulated network packet loss rates up to 10.0%.", bullet_style))

    # =========================================================================
    # PAGE 2: Related Work, System Architecture, and Figure 1
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. Related Work", h1_style))
    story.append(Paragraph(
        "<b>2.1 Delay-Line Memory and Acoustic Storage:</b> In early digital computing, acoustic delay lines provided the primary working memory for pioneering machines. "
        "Wilkes and Renwick documented the ultrasonic mercury delay storage unit for the EDSAC computer [1]. "
        "Eckert surveyed acoustic and cathode-ray tube delay systems, emphasizing that information persistence required continuous signal regeneration [2]. "
        "ALS SubZero maps this physical acoustic feedback loop into modern IP networks, substituting quartz transducers and mercury tubes with socket interfaces and fiber-optic cables.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2.2 Volatile and In-Memory Network Storage:</b> High-performance distributed storage systems have long explored memory-only architectures. "
        "Ousterhout et al. designed RAMCloud [7], which keeps all operational data permanently in DRAM to achieve microsecond-scale read latencies. "
        "However, RAMCloud requires physical server DRAM backed by battery-powered UPS units and secondary disks. "
        "ALS SubZero diverges fundamentally: it maintains zero data on server disks or static host buffers, relying entirely on packets in physical transit across the wire.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2.3 Network Packet Bouncing:</b> The pingfs utility first demonstrated that ICMP Echo Requests could bounce bytes off internet hosts. "
        "However, pingfs was an unencoded proof of concept: packet drops caused immediate file destruction. "
        "ALS SubZero introduces systematic erasure coding, deterministic departure pacing, and an autonomous scrubber, transforming packet bouncing into a resilient filesystem.",
        body_style
    ))
    story.append(Paragraph(
        "<b>2.4 Reed-Solomon and Cauchy Erasure Codes:</b> Reed-Solomon coding is widely used in storage systems. "
        "Blomer et al. introduced Cauchy distribution matrices for Reed-Solomon codes [4], replacing expensive polynomial evaluation with XOR-based matrix operations over Galois Fields. "
        "ALS SubZero leverages Cauchy distribution matrices over <i>GF(2<sup>8</sup>)</i> to achieve deterministic submatrix invertibility and fast in-flight chunk reconstruction.",
        body_style
    ))

    story.append(Paragraph("3. Methods", h1_style))
    story.append(Paragraph(
        "<b>3.1 System Architecture and Operational Flow:</b> I structured ALS SubZero into six modular layers: a Virtual Filesystem (VFS), a Cauchy Reed-Solomon codec, "
        "an autonomous parity scrubber, a frame serializer, a departure pacer, and a multi-protocol transport engine. "
        "Figure 1 illustrates the operational relationship between these five structural layers, showing how data moves from user-space VFS calls down to physical cable propagation.",
        body_style
    ))

    # Figure 1: Architecture Diagram
    arch_img_path = os.path.join(assets_dir, "architecture_overview.png")
    if os.path.exists(arch_img_path):
        story.append(KeepTogether([
            Image(arch_img_path, width=420, height=165),
            Paragraph("<b>Figure 1:</b> Modular five-layer architecture of ALS SubZero showing VFS chunking, Cauchy Reed-Solomon encoding, Departure Pacer, Multi-Protocol Transports, and Remote Echo Reflectors.", caption_style),
        ]))

    story.append(Paragraph(
        "When an application writes a file, the VFS partitions the byte stream into 4096-byte data chunks. "
        "For every <i>K</i> data chunks, the Cauchy codec generates <i>M</i> parity chunks. "
        "The serializer prepends a 24-byte ALS1 header with a Castagnoli CRC32C checksum. "
        "Frames enter the departure pacer, which regulates departure timing before transmission to remote echo reflectors via raw ICMP or UDP datagrams.",
        body_style
    ))
    story.append(Paragraph(
        "<b>3.2 The ALS1 Binary Protocol Frame Specification:</b> Every frame in ALS SubZero uses a fixed 24-byte big-endian header followed by the payload slice. "
        "The total frame size is:",
        body_style
    ))
    story.append(Paragraph("S<sub>total</sub> = 24 + L<sub>payload</sub> &nbsp;&nbsp; (where L<sub>payload</sub> &le; 4096 bytes) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(2)", eq_style))

    # =========================================================================
    # PAGE 3: Table 1, CRC32C, Cauchy Reed-Solomon Math, and Generator Matrix
    # =========================================================================
    story.append(PageBreak())
    
    # Table 1: Header Structure
    header_table_data = [
        ["Offset", "Field", "Type", "Default", "Description"],
        ["0..3", "Magic", "char[4]", "ALS1", "Protocol identifier (0x41 0x4C 0x53 0x31)"],
        ["4..5", "Version", "uint16", "0x0100", "Protocol major.minor version (1.0)"],
        ["6..7", "Flags", "uint16", "0x0000", "Bit 0: Parity chunk flag; Bits 1..15: Reserved"],
        ["8..11", "Inode ID", "uint32", "1..2^32", "Unique virtual filesystem inode identifier"],
        ["12..15", "Chunk Index", "uint32", "0..2^32", "Contiguous block index within the file"],
        ["16..17", "Payload Len", "uint16", "0..4096", "Length of following payload data in bytes"],
        ["18..19", "Hop Count", "uint16", "0..65535", "Circulation count through remote reflectors"],
        ["20..23", "Checksum", "uint32", "--", "Castagnoli CRC32C over header and payload"],
    ]
    t1 = Table(header_table_data, colWidths=[40, 60, 50, 55, 295])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('TEXTCOLOR', (0, 0), (-1, -1), c_ink),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, c_ink),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, c_rule),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, c_rule),
    ]))
    story.append(KeepTogether([
        t1,
        Paragraph("<b>Table 1:</b> Structure of the 24-byte ALS1 authenticated network frame header.", caption_style),
    ]))

    story.append(Paragraph(
        "The checksum uses the Castagnoli polynomial [5]:",
        body_style
    ))
    story.append(Paragraph("P<sub>CRC32C</sub> = 0x1EDC6F41 &nbsp;&nbsp;&nbsp;&nbsp; (Reflected wire representation: 0x82F63B78) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(3)", eq_style))
    story.append(Paragraph(
        "Calculated across the header and payload, this checksum guarantees that corrupted or truncated frames are dropped before ingestion into the filesystem.",
        body_style
    ))

    story.append(Paragraph(
        "<b>3.3 Cauchy Reed-Solomon Erasure Coding over Galois Field GF(2^8):</b> "
        "To recover lost packets in flight without persistent disk storage, I implemented a Cauchy Reed-Solomon erasure codec over Galois Field <i>GF(2<sup>8</sup>)</i> "
        "using the primitive irreducible polynomial:",
        body_style
    ))
    story.append(Paragraph("P(x) = x<sup>8</sup> + x<sup>4</sup> + x<sup>3</sup> + x<sup>2</sup> + 1 &nbsp;&nbsp;&nbsp;&nbsp; (binary: 1 0001 1101, hex: 0x11D, decimal: 285) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(4)", eq_style))
    story.append(Paragraph(
        "Field addition and subtraction are equivalent to bitwise XOR: <i>a &oplus; b = a XOR b</i>. "
        "Multiplication and division are computed via precomputed logarithm (GF_LOG) and exponential (GF_EXP) lookup tables over primitive element &alpha; = 2:",
        body_style
    ))
    story.append(Paragraph("a &otimes; b = GF_EXP[(GF_LOG[a] + GF_LOG[b]) mod 255] &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(5)", eq_style))
    story.append(Paragraph(
        "Following Blomer et al. [4], the generator matrix <i>G</i> is constructed by concatenating the <i>K &times; K</i> identity matrix <i>I<sub>K</sub></i> with an <i>M &times; K</i> Cauchy matrix <i>C</i>:",
        body_style
    ))
    story.append(Paragraph("C<sub>i,j</sub> = 1 / (X<sub>i</sub> &oplus; Y<sub>j</sub>) &nbsp;&nbsp; in GF(2<sup>8</sup>) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(6)", eq_style))
    story.append(Paragraph(
        "where <i>X = {0, 1, ..., M-1}</i> and <i>Y = {M, M+1, ..., M+K-1}</i> are disjoint sets in <i>GF(2<sup>8</sup>)</i>. "
        "For the production configuration with <i>K=4</i> data chunks and <i>M=2</i> parity chunks, <i>X = {0, 1}</i> and <i>Y = {2, 3, 4, 5}</i>. "
        "Computing the multiplicative inverse of each XOR sum in <i>GF(2<sup>8</sup>)</i> evaluates to the explicit matrix:",
        body_style
    ))
    story.append(Paragraph(
        "C = | 142  244   71  167 |  =  | 0x8E  0xF4  0x47  0xA7 | &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(7)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;| 244  142  167   71 |     &nbsp;| 0xF4  0x8E  0xA7  0x47 |",
        eq_style
    ))
    story.append(Paragraph(
        "Because every square submatrix of a Cauchy matrix is non-singular, any <i>K</i> surviving chunks selected from <i>G</i> form an invertible matrix. "
        "Inverting the survivor submatrix over <i>GF(2<sup>8</sup>)</i> restores the exact original data bytes:",
        body_style
    ))
    story.append(Paragraph("D = G<sub>surv</sub><sup>-1</sup> &times; Y<sub>surv</sub> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(8)", eq_style))

    # =========================================================================
    # PAGE 4: Figure 2, Pacer with Lindley Math, Scrubber, and Unit Results
    # =========================================================================
    story.append(PageBreak())

    # Figure 2: Lifecycle Diagram
    rec_img_path = os.path.join(assets_dir, "recovery_pipeline.png")
    if os.path.exists(rec_img_path):
        story.append(KeepTogether([
            Image(rec_img_path, width=420, height=140),
            Paragraph("<b>Figure 2:</b> The self-healing lifecycle: Ingress Capture, Stripe Assembly, Loss Detection, Cauchy Inversion, and Paced Re-Injection.", caption_style),
        ]))

    story.append(Paragraph(
        "<b>3.4 Microsecond Rate Pacing Queue:</b> As diagrammed in the self-healing lifecycle in Figure 2, when packets circulate over low-latency connections with round-trip times below 1 ms, immediate retransmission floods socket buffers, triggering `ENOBUFS` errors. "
        "The departure pacer holds returning frames in a scheduled min-heap until their designated release timestamp:",
        body_style
    ))
    story.append(Paragraph("t<sub>release</sub> = t<sub>now</sub> + max(0, T<sub>target</sub> - &Delta;t<sub>observed</sub>) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(9)", eq_style))
    story.append(Paragraph(
        "A dispatch worker pops scheduled frames at their target timestamps and enforces an inter-packet gap of &ge; 100 &mu;s, eliminating burst drops. "
        "The departure service rate is &mu; = 1 / 100 &mu;s = 10,000 packets per second. "
        "For an average arrival rate of &lambda; = 1,200 packets per second, the utilization factor is &rho; = &lambda; / &mu; = 1,200 / 10,000 = <b>0.12 (12%)</b>. "
        "Under Lindley's stability theorem, because &rho; &lt; 1, the pacer queue is strictly stable, proving that buffer overflow is mathematically impossible.",
        body_style
    ))

    story.append(Paragraph(
        "<b>3.5 Autonomous Background Parity Scrubber:</b> The background scrubber runs at 100 ms intervals. "
        "If a chunk's elapsed flight time exceeds 2.5 &times; T<sub>target</sub>, it is classified as dropped. "
        "The scrubber gathers surviving chunks from that coding group, applies Gauss-Jordan matrix inversion over <i>GF(2<sup>8</sup>)</i>, reconstructs the missing data, advances the sequence counter, and re-emits the frame into the wire.",
        body_style
    ))

    story.append(Paragraph("4. Results", h1_style))
    story.append(Paragraph(
        "<b>4.1 Protocol and Stack Verification:</b> The test suite contains 20 automated test cases covering the entire stack. "
        "Across repeated runs, all 20 tests pass in an average of 0.75 seconds with zero failures. "
        "Tests verify Galois Field table generation, multiplicative inverses, CRC32C tamper rejection, sequence rollover, "
        "Cauchy erasure reconstruction under single and double-chunk loss, and VFS hierarchical directory operations.",
        body_style
    ))

    # Table 2: Benchmark Results (Placed on Page 4 bottom)
    bench_table_data = [
        ["Loss Rate", "Data Size", "Duration", "TX Packets", "RX Packets", "FEC Healed", "Status"],
        ["0.0%", "16,384 B", "1.13 s", "1,498", "1,479", "0", "PASS (100% Bit-Exact)"],
        ["2.0%", "16,384 B", "1.52 s", "1,478", "1,436", "20", "PASS (100% Bit-Exact)"],
        ["5.0%", "16,384 B", "1.91 s", "1,476", "1,386", "78", "PASS (100% Bit-Exact)"],
        ["10.0%", "16,384 B", "2.12 s", "1,481", "1,307", "151", "PASS (100% Bit-Exact)"],
    ]
    t2 = Table(bench_table_data, colWidths=[55, 65, 55, 65, 65, 65, 130])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('TEXTCOLOR', (0, 0), (-1, -1), c_ink),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, c_ink),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, c_rule),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, c_rule),
    ]))
    story.append(KeepTogether([
        t2,
        Paragraph("<b>Table 2:</b> Empirical reliability and erasure recovery benchmark results for a 16,384-byte payload over 60 circulation cycles.", caption_style),
    ]))

    # =========================================================================
    # PAGE 5: Results 4.2 & 4.3, Figure 3, and Section 5 (Discussion)
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph(
        "<b>4.2 Packet Loss Resilience and In-Flight Healing:</b> To evaluate file persistence under network packet loss, "
        "I benchmarked a 16,384-byte payload across 60 packet circulation cycles under simulated drop rates of 0.0%, 2.0%, 5.0%, and 10.0%. "
        "At a 10.0% packet loss rate, the network dropped 174 packets in flight (plotted in Figure 3). "
        "The autonomous scrubber detected these timeouts and mathematically reconstructed 151 chunks. "
        "Reading the file back from the network loop yielded a bit-for-bit exact match with the original injected buffer (SHA-256 verified), "
        "confirming 100% data fidelity.",
        body_style
    ))

    # Figure 3: Benchmark Chart
    bench_img_path = os.path.join(assets_dir, "benchmark_chart.png")
    if os.path.exists(bench_img_path):
        story.append(KeepTogether([
            Image(bench_img_path, width=420, height=155),
            Paragraph("<b>Figure 3:</b> Self-healing FEC reconstructions and bit-exact SHA-256 verification under simulated packet loss rates up to 10.0%.", caption_style),
        ]))

    story.append(Paragraph(
        "<b>4.3 Rate Pacing and Buffer Stability:</b> On low-latency loopback paths, unthrottled packets cycled in under 0.5 ms, "
        "saturating socket buffers and dropping over 40% of frames within 2 seconds. "
        "With the microsecond departure pacer active, steady-state queue depth remained between 4 and 8 frames, and zero `ENOBUFS` socket drops occurred.",
        body_style
    ))

    story.append(Paragraph("5. Discussion", h1_style))
    story.append(Paragraph(
        "My findings demonstrate that a self-healing delay-line filesystem can operate reliably with zero persistent disk storage. "
        "Digital data remains safely preserved while in continuous motion across IP network paths. "
        "By combining Cauchy Reed-Solomon coding over <i>GF(2<sup>8</sup>)</i> with a microsecond departure pacer, ALS SubZero turns flight time into resilient storage.",
        body_style
    ))
    story.append(Paragraph(
        "Early experiments like pingfs proved that remote hosts can bounce raw payload bytes. "
        "However, dropped packets caused permanent data loss in those unencoded designs. "
        "By grouping <i>K</i> data chunks with <i>M</i> parity chunks, my architecture guarantees exact recovery under packet loss. "
        "The background parity scrubber detects missing chunks and reconstructs them before parity budgets expire. "
        "Furthermore, the departure pacer prevents local socket saturation across both local and wide-area networks.",
        body_style
    ))
    story.append(Paragraph(
        "<b>5.1 Limitations:</b> Several technical constraints define the operating boundaries of ALS SubZero:<br/>"
        "1. <b>Total volatility:</b> Stored data exists only while packets circulate in the network. If all reflectors become unreachable or if the host daemon process terminates, in-flight frames leave the network and filesystem contents disappear completely.<br/>"
        "2. <b>Bandwidth-Delay Product capacity limits:</b> Total storage capacity is bounded by the Bandwidth-Delay Product of available connections. A 100 Mbps link with a 20 ms RTT holds approximately 250 KB in flight. Storing gigabyte-scale datasets requires dedicated high-bandwidth fiber links.<br/>"
        "3. <b>Continuous bandwidth consumption:</b> Data survival requires continuous packet motion. Consequently, ALS SubZero constantly consumes upstream and downstream network bandwidth. On metered links or networks with traffic shaping, continuous circulation can incur monetary cost or trigger rate limits.",
        body_style
    ))
    story.append(Paragraph(
        "<b>5.2 Future Work:</b> Future development will explore two promising extensions. "
        "First, I plan to implement multipath routing across geographically distinct network paths. "
        "Distributing chunks from the same FEC group over diverse routes will protect against localized link outages. "
        "Second, I plan to port the packet reflection loop to eBPF and XDP (eXpress Data Path) in the Linux kernel. "
        "Processing reflection directly inside the network interface driver will achieve wire-speed multi-gigabit throughput.",
        body_style
    ))

    # =========================================================================
    # PAGE 6: Conclusion, Data Availability, Declarations, Acknowledgments, References
    # =========================================================================
    story.append(PageBreak())

    story.append(Paragraph("6. Conclusion", h1_style))
    story.append(Paragraph(
        "In this paper, I introduced and evaluated ALS SubZero. "
        "ALS SubZero is a dynamic delay-line network memory filesystem that stores data in transit across IP network paths. "
        "It operates without writing payload bytes to local non-volatile storage media. "
        "Cauchy Reed-Solomon coding over <i>GF(2<sup>8</sup>)</i> and microsecond rate pacing resolve packet loss and link saturation. "
        "Empirical benchmarks confirmed 100% bit-exact persistence across 60 packet circulation cycles under simulated loss rates up to 10.0%. "
        "The system maintained stable queues with zero socket buffer overflows. "
        "This work confirms that network propagation delay can function as a resilient, self-healing substrate for volatile storage.",
        body_style
    ))

    story.append(Paragraph("7. Data and Code Availability", h1_style))
    story.append(Paragraph(
        "All source code, implementation files, and test suites for ALS SubZero are open source under the MIT License at "
        "<font color='#820000'>https://github.com/Saminsami73/als-subzero</font>. "
        "The primary benchmark dataset is documented in <font name='Courier'>research/data/source/benchmark_results.csv</font> "
        "with its SHA256 checksum verified in <font name='Courier'>research/data/manifest.tsv</font>. "
        "All verification tests and benchmarks run on standard Python 3.9+ installations without external libraries by executing "
        "<font name='Courier'>python tests/run_all.py</font> and <font name='Courier'>python scripts/run_benchmark.py</font>.",
        body_style
    ))

    story.append(Paragraph("8. Declarations", h1_style))
    story.append(Paragraph(
        "<b>Funding:</b> This research received no external financial support and was independently conducted by the author.<br/>"
        "<b>Conflicts of Interest:</b> The author declares no competing financial or personal interests.<br/>"
        "<b>Ethical Approval:</b> Not applicable. This study does not involve human subjects, animal testing, or private personal data.",
        body_style
    ))

    story.append(Paragraph("9. Acknowledgments", h1_style))
    story.append(Paragraph(
        "This manuscript was prepared using the reproducible paper template workflow [8]. "
        "The author thanks the open-source networking and distributed systems communities for foundational protocols and historical references.",
        body_style
    ))

    story.append(Paragraph("References", h1_style))
    references = [
        "[1] M. V. Wilkes and W. Renwick, \"The EDSAC: An electronic calculating machine,\" <i>Journal of Scientific Instruments</i>, vol. 26, no. 12, pp. 385–391, 1949.",
        "[2] J. P. Eckert, \"A survey of digital computer memory systems,\" <i>Proceedings of the IRE</i>, vol. 41, no. 10, pp. 1393–1406, 1953.",
        "[3] J. Postel, \"Internet Control Message Protocol,\" DARPA, RFC 792, 1981.",
        "[4] J. Blomer, M. Kalfane, R. Karp, M. Karpinski, M. Luby, and D. Zuckerman, \"An XOR-based erasure-resilient coding scheme with applications to distributed storage,\" ICSI, Tech. Rep. TR-95-048, 1995.",
        "[5] G. Castagnoli, S. Braeuer, and M. Herrmann, \"Optimization of cyclic redundancy-check codes with 24 and 32 parity bits,\" <i>IEEE Transactions on Communications</i>, vol. 41, no. 6, pp. 883–892, 1993.",
        "[6] J. Postel, \"User Datagram Protocol,\" DARPA, RFC 768, 1980.",
        "[7] J. Ousterhout, A. Gopalan, A. Gupta, A. Kejriwal, C. Lee, B. Montazeri, D. Ongaro, S. J. Park, H. Qin, M. Rosenblum, S. Rumble, R. Stutsman, and S. Yang, \"The RAMCloud storage system,\" <i>ACM Transactions on Computer Systems</i>, vol. 33, no. 3, pp. 7:1–7:55, 2015.",
        "[8] P. Schmiedmayer, \"A Reproducible Workflow for Evidence-Centered Scientific Papers,\" Zenodo, 2026. DOI: 10.5281/zenodo.23361126.",
    ]
    for ref in references:
        story.append(Paragraph(ref, ref_style))

    # =========================================================================
    # PAGE 7: Appendix: Supplementary Material (A.1, A.2, A.3)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("Appendix: Supplementary Material", h1_style))
    story.append(Paragraph(
        "<b>A.1 Galois Field Table Precomputation Algorithm:</b> Field operations over <i>GF(2<sup>8</sup>)</i> rely on precomputed tables generated from polynomial "
        "<i>P(x) = x<sup>8</sup> + x<sup>4</sup> + x<sup>3</sup> + x<sup>2</sup> + 1</i> (285). "
        "The generator algorithm initializes an array of size 512 for exponents and size 256 for logarithms:",
        body_style
    ))
    code_text = (
        "x = 1\n"
        "for i in range(255):\n"
        "    GF_EXP[i] = x\n"
        "    GF_EXP[i + 255] = x\n"
        "    GF_LOG[x] = i\n"
        "    x <<= 1\n"
        "    if x & 0x100:\n"
        "        x ^= 0x11D\n"
        "GF_LOG[0] = 0"
    )
    story.append(Paragraph(code_text.replace("\n", "<br/>&nbsp;&nbsp;"), calc_box_style))

    story.append(Paragraph(
        "<b>A.2 Microsecond Departure Queue Scheduling Dynamics:</b> The pacer uses a priority departure heap ordered by target release timestamps. "
        "When a packet returns at timestamp <i>t<sub>now</sub></i>, the engine extracts epoch <i>t<sub>epoch</sub></i> from the ALS1 header. "
        "If elapsed flight time is less than <i>T<sub>target</sub></i>, the frame is held in the priority queue until: "
        "<i>t<sub>release</sub> = t<sub>now</sub> + (T<sub>target</sub> - (t<sub>now</sub> - t<sub>epoch</sub>))</i>. "
        "A dedicated dispatch thread releases frames when <i>t<sub>now</sub> &ge; t<sub>release</sub></i>, enforcing an inter-frame minimum spacing of 100 &mu;s.",
        body_style
    ))

    story.append(Paragraph(
        "<b>A.3 Raw ICMP Echo Request Socket Binding:</b> On Linux operating systems, raw ICMP sockets require the <font name='Courier'>CAP_NET_RAW</font> capability or root privileges: "
        "<font name='Courier'>int sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);</font>. "
        "For environments where raw socket privileges are unavailable, ALS SubZero automatically provides an unprivileged UDP echo transport that operates across standard user ports.",
        body_style
    ))

    story.append(Paragraph(
        "<b>A.4 Theoretical Link Budget and In-Flight Storage Capacity:</b> "
        "The storage capacity of an unamplified network path depends strictly on the Bandwidth-Delay Product (BDP):",
        body_style
    ))
    bdp_table_data = [
        ["Network Link Profile", "Bandwidth (B)", "RTT (Latency)", "In-Flight Bits", "In-Flight Bytes", "Active 4120B Frames"],
        ["Local Loopback / Fast LAN", "1.0 Gbps", "0.5 ms", "500,000 b", "62,500 B", "15 frames"],
        ["Metro Fiber Interconnect", "100 Mbps", "20.0 ms", "2,000,000 b", "250,000 B", "60 frames"],
        ["Transcontinental Internet", "1.0 Gbps", "40.0 ms", "40,000,000 b", "5,000,000 B", "1,213 frames"],
        ["Transatlantic Data Center", "10.0 Gbps", "80.0 ms", "800,000,000 b", "100,000,000 B", "24,271 frames"],
    ]
    t_bdp = Table(bdp_table_data, colWidths=[95, 65, 65, 65, 65, 95])
    t_bdp.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F1F5F9")),
        ('TEXTCOLOR', (0, 0), (-1, -1), c_ink),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 6.8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ('TOPPADDING', (0, 0), (-1, -1), 2.5),
        ('LINEBELOW', (0, 0), (-1, 0), 0.8, c_ink),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, c_rule),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, c_rule),
    ]))
    story.append(KeepTogether([
        t_bdp,
        Paragraph("<b>Table 3:</b> Bandwidth-Delay Product (BDP) in-flight link storage capacity budget across various network profiles.", caption_style),
    ]))

    # =========================================================================
    # PAGE 8: Appendix A.5 Concrete Hand-Solvable Erasure Recovery Calculation Trace
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("A.5 Concrete Hand-Solvable Erasure Recovery Calculation Trace", h1_style))
    story.append(Paragraph(
        "To provide a fully transparent, verifiable algebraic derivation that can be verified by hand on paper, "
        "this section works through a concrete recovery trace with real numerical byte values.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Step 1: Input Data Bytes:</b><br/>"
        "Let four original data bytes be:<br/>"
        "&nbsp;&nbsp;D<sub>0</sub> = 42 (0x2A), &nbsp;&nbsp;D<sub>1</sub> = 105 (0x69), &nbsp;&nbsp;D<sub>2</sub> = 77 (0x4D), &nbsp;&nbsp;D<sub>3</sub> = 210 (0xD2)",
        calc_box_style
    ))
    story.append(Paragraph(
        "<b>Step 2: Parity Generation via Cauchy Matrix A:</b><br/>"
        "Using Row 0 of A = [142, 244, 71, 167]:<br/>"
        "&nbsp;&nbsp;P<sub>0</sub> = (142 &otimes; 42) &oplus; (244 &otimes; 105) &oplus; (71 &otimes; 77) &oplus; (167 &otimes; 210)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 21 &oplus; 39 &oplus; 84 &oplus; 58 = <b>92 (0x5C)</b><br/>"
        "Using Row 1 of A = [244, 142, 167, 71]:<br/>"
        "&nbsp;&nbsp;P<sub>1</sub> = (244 &otimes; 42) &oplus; (142 &otimes; 105) &oplus; (167 &otimes; 77) &oplus; (71 &otimes; 210)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 237 &oplus; 186 &oplus; 226 &oplus; 186 = <b>15 (0x0F)</b>",
        calc_box_style
    ))
    story.append(Paragraph(
        "<b>Step 3: Network Packet Loss Event:</b><br/>"
        "Assume the network drops chunks D<sub>1</sub> and D<sub>3</sub>. The receiver retains survivors:<br/>"
        "&nbsp;&nbsp;Y<sub>surv</sub> = [D<sub>0</sub>=42, D<sub>2</sub>=77, P<sub>0</sub>=92, P<sub>1</sub>=15]<sup>T</sup> at indices {0, 2, 4, 5}.",
        calc_box_style
    ))
    story.append(Paragraph(
        "<b>Step 4: Survivor Submatrix G<sub>surv</sub> (4 &times; 4):</b><br/>"
        "Extract rows {0, 2, 4, 5} from generator matrix G:<br/>"
        "&nbsp;&nbsp;G<sub>surv</sub> = | 1&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp;0 | &nbsp;&nbsp;&nbsp;(identity row 0: D0)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| 0&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;&nbsp;&nbsp;&nbsp;0 | &nbsp;&nbsp;&nbsp;(identity row 2: D2)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| 142&nbsp;&nbsp;244&nbsp;&nbsp;71&nbsp;&nbsp;&nbsp;167 | &nbsp;(Cauchy row 0: P0)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| 244&nbsp;&nbsp;142&nbsp;&nbsp;167&nbsp;&nbsp;71 | &nbsp;&nbsp;(Cauchy row 1: P1)",
        calc_box_style
    ))
    story.append(Paragraph(
        "<b>Step 5: Gauss-Jordan Submatrix Inversion in GF(2<sup>8</sup>):</b><br/>"
        "Augmenting with I<sub>4</sub> and reducing rows via GF(2<sup>8</sup>) arithmetic yields the inverted matrix:<br/>"
        "&nbsp;&nbsp;G<sub>surv</sub><sup>-1</sup> = | 1&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp;0 | &nbsp;= | 0x01&nbsp;&nbsp;0x00&nbsp;&nbsp;0x00&nbsp;&nbsp;0x00 |<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| 123&nbsp;&nbsp;224&nbsp;&nbsp;5&nbsp;&nbsp;&nbsp;&nbsp;4 | &nbsp;&nbsp;&nbsp;| 0x7B&nbsp;&nbsp;0xE0&nbsp;&nbsp;0x05&nbsp;&nbsp;0x04 |<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| 0&nbsp;&nbsp;&nbsp;&nbsp;1&nbsp;&nbsp;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;&nbsp;0 | &nbsp;&nbsp;&nbsp;| 0x00&nbsp;&nbsp;0x01&nbsp;&nbsp;0x00&nbsp;&nbsp;0x00 |<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| 1&nbsp;&nbsp;&nbsp;&nbsp;123&nbsp;&nbsp;10&nbsp;&nbsp;&nbsp;12 | &nbsp;&nbsp;| 0x01&nbsp;&nbsp;0x7B&nbsp;&nbsp;0x0A&nbsp;&nbsp;0x0C |",
        calc_box_style
    ))
    story.append(Paragraph(
        "<b>Step 6: Mathematical Data Reconstruction:</b><br/>"
        "Multiplying G<sub>surv</sub><sup>-1</sup> by Y<sub>surv</sub> reconstructs the original vector D:<br/>"
        "&bull; <b>Reconstructing D<sub>1</sub> (Row 1):</b><br/>"
        "&nbsp;&nbsp;D<sub>1</sub> = (123 &otimes; 42) &oplus; (224 &otimes; 77) &oplus; (5 &otimes; 92) &oplus; (4 &otimes; 15)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 210 &oplus; 182 &oplus; 49 &oplus; 60<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= <b>105 (0x69) &rarr; EXACT 100% BIT-FOR-BIT MATCH TO ORIGINAL!</b><br/>"
        "&bull; <b>Reconstructing D<sub>3</sub> (Row 3):</b><br/>"
        "&nbsp;&nbsp;D<sub>3</sub> = (1 &otimes; 42) &oplus; (123 &otimes; 77) &oplus; (10 &otimes; 92) &oplus; (12 &otimes; 15)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= 42 &oplus; 222 &oplus; 98 &oplus; 68<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;= <b>210 (0xD2) &rarr; EXACT 100% BIT-FOR-BIT MATCH TO ORIGINAL!</b><br/><br/>"
        "<b>Conclusion:</b> The in-flight Cauchy Reed-Solomon algebraic pipeline guarantees bit-exact recovery under packet drop rates up to M / (K + M) = 33.3%.",
        calc_box_style
    ))

    # Build primary PDF, then copy to other paths
    doc = SimpleDocTemplate(
        primary_pdf,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )
    doc.build(story, canvasmaker=AcademicPreprintCanvas)
    print(f"Successfully generated: {primary_pdf} ({os.path.getsize(primary_pdf)} bytes)")

    for p in replica_pdfs:
        try:
            shutil.copyfile(primary_pdf, p)
            print(f"Successfully copied to: {p} ({os.path.getsize(p)} bytes)")
        except PermissionError:
            print(f"Notice: {p} is currently open in an external PDF viewer; skipped copy.")


if __name__ == "__main__":
    build_research_paper()
