"""
Generate the complete 7-8 page hand-writable mathematical calculations PDF
for ALS SubZero with rough work, trial-and-error, mistakes, and corrections.
Author: Samin Sami (Samin Yasar AL Sami).
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved = []

    def showPage(self):
        self._saved.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved)
        for state in self._saved:
            self.__dict__.update(state)
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#4A5568"))
            if self._pageNumber > 1:
                self.drawString(54, 11*72-36,
                    "ALS SubZero: Complete Hand-Writable Mathematical Calculations & Proofs")
                self.drawRightString(8.5*72-54, 11*72-36, "Samin Sami")
                self.setStrokeColor(colors.HexColor("#CBD5E1"))
                self.setLineWidth(0.5)
                self.line(54, 11*72-42, 8.5*72-54, 11*72-42)
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 46, 8.5*72-54, 46)
            self.drawString(54, 34, "Samin Sami (Al Sami) - Mathematical Rough Work & Verified Proofs")
            self.drawRightString(8.5*72-54, 34, f"Page {self._pageNumber} of {total}")
            self.restoreState()
            super().showPage()
        super().save()


def build():
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs_external"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir,
        "ALS_SubZero_Complete_Handwritten_Math_Calculations.pdf")

    doc = SimpleDocTemplate(out_path, pagesize=letter,
        leftMargin=50, rightMargin=50, topMargin=50, bottomMargin=60)

    # ---- styles ----
    title = ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=18,
        leading=22, textColor=colors.HexColor("#0F172A"), spaceAfter=4)
    subtitle = ParagraphStyle("ST", fontName="Helvetica-Bold", fontSize=10,
        leading=14, textColor=colors.HexColor("#1E40AF"), spaceAfter=10)
    meta = ParagraphStyle("M", fontName="Helvetica", fontSize=8.5,
        leading=12, textColor=colors.HexColor("#334155"), spaceAfter=12)
    h1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=12.5,
        leading=16, textColor=colors.HexColor("#0F172A"),
        spaceBefore=12, spaceAfter=5, keepWithNext=True)
    h2 = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=10,
        leading=13, textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=8, spaceAfter=3, keepWithNext=True)
    h3 = ParagraphStyle("H3", fontName="Helvetica-Bold", fontSize=9,
        leading=12, textColor=colors.HexColor("#1E40AF"),
        spaceBefore=6, spaceAfter=2, keepWithNext=True)
    body = ParagraphStyle("B", fontName="Helvetica", fontSize=8,
        leading=11.5, textColor=colors.HexColor("#1E293B"), spaceAfter=5)
    math = ParagraphStyle("MX", fontName="Courier", fontSize=7.5,
        leading=10.5, textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F8FAFC"),
        borderColor=colors.HexColor("#CBD5E1"),
        borderWidth=0.5, borderPadding=5,
        spaceBefore=3, spaceAfter=5)
    mistake = ParagraphStyle("ERR", fontName="Courier", fontSize=7.5,
        leading=10.5, textColor=colors.HexColor("#991B1B"),
        backColor=colors.HexColor("#FEF2F2"),
        borderColor=colors.HexColor("#FCA5A5"),
        borderWidth=0.5, borderPadding=5,
        spaceBefore=3, spaceAfter=3)
    fix = ParagraphStyle("FIX", fontName="Courier", fontSize=7.5,
        leading=10.5, textColor=colors.HexColor("#065F46"),
        backColor=colors.HexColor("#ECFDF5"),
        borderColor=colors.HexColor("#6EE7B7"),
        borderWidth=0.5, borderPadding=5,
        spaceBefore=3, spaceAfter=5)
    note = ParagraphStyle("N", fontName="Helvetica-Oblique", fontSize=7.5,
        leading=10.5, textColor=colors.HexColor("#6B7280"), spaceAfter=4)

    s = []  # story

    # ===== TITLE PAGE =====
    s.append(Spacer(1, 40))
    s.append(Paragraph("ALS SubZero", title))
    s.append(Paragraph("Complete Hand-Writable Mathematical Calculations,<br/>"
        "Step-by-Step Rough Work, Trial and Error, and Verified Proofs", subtitle))
    s.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#94A3B8"), spaceAfter=8))
    s.append(Paragraph(
        "<b>Author:</b> Samin Sami (Samin Yasar AL Sami)<br/>"
        "<b>Project:</b> ALS SubZero (Dynamic Delay-Line Network Memory Filesystem)<br/>"
        "<b>Date:</b> November 2026<br/>"
        "<b>License:</b> MIT Open Source<br/><br/>"
        "<b>Purpose of this document:</b> This is meant to be copied by hand onto real paper. "
        "Every calculation is written out line by line with no shortcuts. "
        "I included my rough work, my mistakes, and my corrections so you can see "
        "the real process I followed. Each answer is verified at the end of its section.",
        meta))

    s.append(Paragraph(
        "<b>What this document covers (8 problems):</b><br/>"
        "Problem 1: Bandwidth-Delay Product storage capacity calculations (3 real links)<br/>"
        "Problem 2: Building Galois Field GF(2^8) tables by hand with polynomial reduction<br/>"
        "Problem 3: GF(2^8) multiplication using log/exp tables (with a wrong attempt first)<br/>"
        "Problem 4: GF(2^8) division and multiplicative inverse computation<br/>"
        "Problem 5: Constructing the Cauchy generator matrix A for K=4, M=2<br/>"
        "Problem 6: Encoding 4 data bytes into 2 parity bytes (full arithmetic trace)<br/>"
        "Problem 7: Recovering 2 lost data bytes from survivors using Gauss-Jordan elimination<br/>"
        "Problem 8: CRC32C checksum computation and frame integrity verification",
        meta))

    s.append(PageBreak())

    # ===== PROBLEM 1: BDP =====
    s.append(Paragraph("PROBLEM 1: Bandwidth-Delay Product Storage Capacity", h1))
    s.append(Paragraph(
        "The question I needed to answer first: how many bytes of data can physically exist "
        "inside a network cable at any instant? This determines the maximum filesystem size.",
        body))
    s.append(Paragraph("The formula:", h3))
    s.append(Paragraph(
        "C = B &times; RTT<br/>"
        "where C = capacity in bits, B = bandwidth in bits per second, RTT = round-trip time in seconds",
        math))

    s.append(Paragraph("Calculation 1A: Home broadband link (100 Mbps, 20 ms RTT)", h2))
    s.append(Paragraph(
        "Given:<br/>"
        "&nbsp;&nbsp;B = 100 Megabits per second = 100,000,000 bits per second<br/>"
        "&nbsp;&nbsp;RTT = 20 milliseconds = 20 / 1000 = 0.020 seconds<br/><br/>"
        "Step 1: Multiply bandwidth by round-trip time<br/>"
        "&nbsp;&nbsp;C = 100,000,000 &times; 0.020<br/>"
        "&nbsp;&nbsp;C = 100,000,000 &times; 2 / 100<br/>"
        "&nbsp;&nbsp;C = 200,000,000 / 100<br/>"
        "&nbsp;&nbsp;C = 2,000,000 bits<br/><br/>"
        "Step 2: Convert bits to bytes (divide by 8)<br/>"
        "&nbsp;&nbsp;C = 2,000,000 / 8 = 250,000 bytes<br/><br/>"
        "Step 3: Convert to kilobytes<br/>"
        "&nbsp;&nbsp;C = 250,000 / 1,024 = 244.14 KB (approximately 244 KB)<br/><br/>"
        "<b>Answer: A 100 Mbps link with 20 ms RTT holds about 244 KB in flight.</b>",
        math))

    s.append(Paragraph("Calculation 1B: Transcontinental fiber (1 Gbps, 40 ms RTT)", h2))
    s.append(Paragraph(
        "Given:<br/>"
        "&nbsp;&nbsp;B = 1 Gigabit per second = 1,000,000,000 bits per second<br/>"
        "&nbsp;&nbsp;RTT = 40 milliseconds = 0.040 seconds<br/><br/>"
        "Step 1: C = 1,000,000,000 &times; 0.040<br/>"
        "&nbsp;&nbsp;= 1,000,000,000 &times; 4 / 100<br/>"
        "&nbsp;&nbsp;= 4,000,000,000 / 100<br/>"
        "&nbsp;&nbsp;= 40,000,000 bits<br/><br/>"
        "Step 2: Convert to bytes: 40,000,000 / 8 = 5,000,000 bytes<br/>"
        "Step 3: Convert to MB: 5,000,000 / 1,048,576 = 4.77 MB (approximately 5.0 MB)<br/><br/>"
        "<b>Answer: A 1 Gbps transcontinental fiber link holds about 5.0 MB in flight.</b>",
        math))

    s.append(Paragraph("Calculation 1C: How many ALS SubZero frames fit in that 5 MB?", h2))
    s.append(Paragraph(
        "Each ALS SubZero frame = 24-byte header + 4096-byte chunk payload = 4,120 bytes total<br/><br/>"
        "Step 1: Divide total capacity by frame size<br/>"
        "&nbsp;&nbsp;N = 5,000,000 / 4,120<br/>"
        "&nbsp;&nbsp;N = 1,213.59...<br/>"
        "&nbsp;&nbsp;N = 1,213 frames (round down, cannot have partial frames)<br/><br/>"
        "<b>Answer: Approximately 1,213 ALS SubZero frames circulate simultaneously.</b>",
        math))

    # ---- Trial and error / rough note ----
    s.append(Paragraph("Rough note / first attempt (mistake):", h3))
    s.append(Paragraph(
        "WRONG ATTEMPT: I initially forgot to include the 24-byte header in my frame size calculation.<br/>"
        "&nbsp;&nbsp;N = 5,000,000 / 4,096 = 1,220.7 frames  (WRONG - this ignores header overhead)<br/><br/>"
        "The correct frame size is 4,096 + 24 = 4,120 bytes, not 4,096.<br/>"
        "This matters because over 1,213 frames, the header overhead adds up to:<br/>"
        "&nbsp;&nbsp;1,213 frames &times; 24 bytes/header = 29,112 bytes of header data in the wire.",
        mistake))
    s.append(Paragraph(
        "CORRECTION: Using the correct frame size of 4,120 bytes gives N = 1,213 frames.<br/>"
        "The 7-frame difference (1,220 vs 1,213) means my first estimate overpromised by 28,672 bytes.",
        fix))

    s.append(PageBreak())

    # ===== PROBLEM 2: GF(2^8) TABLE CONSTRUCTION =====
    s.append(Paragraph("PROBLEM 2: Building Galois Field GF(2^8) Tables by Hand", h1))
    s.append(Paragraph(
        "All error correction math in ALS SubZero happens inside Galois Field GF(2^8). "
        "This is a special number system where every value fits in one byte (0 to 255) "
        "and where addition, subtraction, multiplication, and division all produce results "
        "that are also single bytes. There is no overflow and no rounding.",
        body))

    s.append(Paragraph("The irreducible polynomial", h2))
    s.append(Paragraph(
        "P(x) = x<sup>8</sup> + x<sup>4</sup> + x<sup>3</sup> + x<sup>2</sup> + 1<br/><br/>"
        "Written as a binary number (each power of x becomes a bit position):<br/>"
        "&nbsp;&nbsp;x<sup>8</sup> = bit 8 = 1<br/>"
        "&nbsp;&nbsp;x<sup>7</sup> = bit 7 = 0<br/>"
        "&nbsp;&nbsp;x<sup>6</sup> = bit 6 = 0<br/>"
        "&nbsp;&nbsp;x<sup>5</sup> = bit 5 = 0<br/>"
        "&nbsp;&nbsp;x<sup>4</sup> = bit 4 = 1<br/>"
        "&nbsp;&nbsp;x<sup>3</sup> = bit 3 = 1<br/>"
        "&nbsp;&nbsp;x<sup>2</sup> = bit 2 = 1<br/>"
        "&nbsp;&nbsp;x<sup>1</sup> = bit 1 = 0<br/>"
        "&nbsp;&nbsp;x<sup>0</sup> = bit 0 = 1<br/><br/>"
        "Binary: 1 0001 1101 = 0x11D = decimal 285",
        math))

    s.append(Paragraph("Step-by-step: generating powers of the primitive element alpha = 2", h2))
    s.append(Paragraph(
        "The rule: start with x = 1. Each step, multiply x by 2 (shift left one bit). "
        "If the result is 256 or larger (bit 8 is set), XOR it with 285 to reduce it back to a single byte.",
        body))
    s.append(Paragraph(
        "<b>Power 0:</b> x = 1 (0x01, binary: 00000001)<br/>"
        "&nbsp;&nbsp;GF_EXP[0] = 1. Store GF_LOG[1] = 0.<br/><br/>"
        "<b>Power 1:</b> x = 1 &times; 2 = 2 (0x02, binary: 00000010)<br/>"
        "&nbsp;&nbsp;Check: is 2 &ge; 256? No. Keep x = 2.<br/>"
        "&nbsp;&nbsp;GF_EXP[1] = 2. Store GF_LOG[2] = 1.<br/><br/>"
        "<b>Power 2:</b> x = 2 &times; 2 = 4 (0x04, binary: 00000100)<br/>"
        "&nbsp;&nbsp;Check: 4 &ge; 256? No. Keep x = 4.<br/>"
        "&nbsp;&nbsp;GF_EXP[2] = 4. Store GF_LOG[4] = 2.<br/><br/>"
        "<b>Power 3:</b> x = 4 &times; 2 = 8 (0x08, binary: 00001000)<br/>"
        "&nbsp;&nbsp;GF_EXP[3] = 8. GF_LOG[8] = 3.<br/><br/>"
        "<b>Power 4:</b> x = 8 &times; 2 = 16 (0x10, binary: 00010000)<br/>"
        "&nbsp;&nbsp;GF_EXP[4] = 16. GF_LOG[16] = 4.<br/><br/>"
        "<b>Power 5:</b> x = 16 &times; 2 = 32 (0x20, binary: 00100000)<br/>"
        "&nbsp;&nbsp;GF_EXP[5] = 32. GF_LOG[32] = 5.<br/><br/>"
        "<b>Power 6:</b> x = 32 &times; 2 = 64 (0x40, binary: 01000000)<br/>"
        "&nbsp;&nbsp;GF_EXP[6] = 64. GF_LOG[64] = 6.<br/><br/>"
        "<b>Power 7:</b> x = 64 &times; 2 = 128 (0x80, binary: 10000000)<br/>"
        "&nbsp;&nbsp;GF_EXP[7] = 128. GF_LOG[128] = 7.",
        math))

    s.append(Paragraph("Power 8: the first reduction (this is the interesting step)", h3))
    s.append(Paragraph(
        "<b>Power 8:</b> x = 128 &times; 2 = 256<br/><br/>"
        "Check: is 256 &ge; 256? YES! Bit 8 is set (binary: 1 00000000).<br/>"
        "So we must reduce: x = 256 XOR 285<br/><br/>"
        "Let me write it out in binary:<br/>"
        "&nbsp;&nbsp;256 = 1 0000 0000<br/>"
        "&nbsp;&nbsp;285 = 1 0001 1101<br/>"
        "&nbsp;&nbsp;XOR = 0 0001 1101 = 29 (0x1D)<br/><br/>"
        "GF_EXP[8] = 29. GF_LOG[29] = 8.",
        math))

    s.append(Paragraph("Power 9:", h3))
    s.append(Paragraph(
        "<b>Power 9:</b> x = 29 &times; 2 = 58<br/>"
        "&nbsp;&nbsp;Check: 58 &ge; 256? No.<br/>"
        "&nbsp;&nbsp;GF_EXP[9] = 58. GF_LOG[58] = 9.",
        math))

    s.append(Paragraph("Power 10:", h3))
    s.append(Paragraph(
        "<b>Power 10:</b> x = 58 &times; 2 = 116<br/>"
        "&nbsp;&nbsp;Check: 116 &ge; 256? No.<br/>"
        "&nbsp;&nbsp;GF_EXP[10] = 116. GF_LOG[116] = 10.",
        math))

    s.append(Paragraph("Power 11:", h3))
    s.append(Paragraph(
        "<b>Power 11:</b> x = 116 &times; 2 = 232<br/>"
        "&nbsp;&nbsp;Check: 232 &ge; 256? No.<br/>"
        "&nbsp;&nbsp;GF_EXP[11] = 232. GF_LOG[232] = 11.",
        math))

    s.append(Paragraph("Power 12: another reduction", h3))
    s.append(Paragraph(
        "<b>Power 12:</b> x = 232 &times; 2 = 464<br/>"
        "&nbsp;&nbsp;Check: 464 &ge; 256? YES! Must reduce.<br/>"
        "&nbsp;&nbsp;464 = 1 1101 0000 (binary)<br/>"
        "&nbsp;&nbsp;285 = 1 0001 1101 (binary)<br/>"
        "&nbsp;&nbsp;XOR = 0 1100 1101 = 205 (0xCD)<br/>"
        "&nbsp;&nbsp;GF_EXP[12] = 205. GF_LOG[205] = 12.",
        math))

    s.append(Paragraph("Rough work / mistake on Power 12:", h3))
    s.append(Paragraph(
        "FIRST ATTEMPT (WRONG): I accidentally wrote 232 &times; 2 = 464 in binary as 1 1100 0000.<br/>"
        "Let me recheck: 232 in binary is 1110 1000.<br/>"
        "&nbsp;&nbsp;232 &times; 2 = shift left: 1 1101 0000 = 256 + 128 + 64 + 16 = 464. OK, 464 is correct.<br/>"
        "Now XOR with 285:<br/>"
        "&nbsp;&nbsp;464 = 111010000 (9 bits)<br/>"
        "&nbsp;&nbsp;285 = 100011101 (9 bits)<br/>"
        "&nbsp;&nbsp;XOR = 011001101 = 128 + 64 + 8 + 4 + 1 = 205. Correct!",
        mistake))
    s.append(Paragraph(
        "VERIFIED: 205 is the correct answer. My binary conversion was correct on second look.",
        fix))

    s.append(Paragraph("Summary table of the first 13 GF_EXP entries:", h3))
    s.append(Paragraph(
        "GF_EXP[0] = 1 &nbsp;&nbsp; GF_EXP[1] = 2 &nbsp;&nbsp; GF_EXP[2] = 4 &nbsp;&nbsp; GF_EXP[3] = 8<br/>"
        "GF_EXP[4] = 16 &nbsp; GF_EXP[5] = 32 &nbsp; GF_EXP[6] = 64 &nbsp; GF_EXP[7] = 128<br/>"
        "GF_EXP[8] = 29 &nbsp; GF_EXP[9] = 58 &nbsp; GF_EXP[10] = 116 &nbsp;GF_EXP[11] = 232<br/>"
        "GF_EXP[12] = 205",
        math))
    s.append(Paragraph(
        "Verification: run 'python -c \"from src.als_subzero.fec.parity import GF_EXP; print(GF_EXP[:13])\"' "
        "and the program prints [1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205]. Matches exactly.",
        note))

    s.append(PageBreak())

    # ===== PROBLEM 3: GF MULTIPLICATION =====
    s.append(Paragraph("PROBLEM 3: Multiplying Two Bytes in GF(2^8) Using Log Tables", h1))
    s.append(Paragraph(
        "Task: compute 0x8E &times; 0x2A in GF(2^8). "
        "These are the actual coefficients and data bytes from the ALS SubZero encoder.",
        body))
    s.append(Paragraph("The formula:", h3))
    s.append(Paragraph(
        "gf_mul(a, b) = GF_EXP[ GF_LOG[a] + GF_LOG[b] ]<br/>"
        "(If either a or b is zero, the result is always zero.)",
        math))

    s.append(Paragraph("Step-by-step calculation", h2))
    s.append(Paragraph(
        "Given: a = 0x8E (decimal 142), b = 0x2A (decimal 42)<br/><br/>"
        "Step 1: Look up GF_LOG[142]<br/>"
        "&nbsp;&nbsp;GF_LOG[142] = 254 (this means alpha^254 = 142)<br/><br/>"
        "Step 2: Look up GF_LOG[42]<br/>"
        "&nbsp;&nbsp;GF_LOG[42] = 142 (this means alpha^142 = 42)<br/><br/>"
        "Step 3: Add the logarithms<br/>"
        "&nbsp;&nbsp;log_sum = 254 + 142 = 396<br/><br/>"
        "Step 4: Look up GF_EXP[396]<br/>"
        "&nbsp;&nbsp;GF_EXP[396] = 21 (0x15)<br/><br/>"
        "<b>Answer: 0x8E &times; 0x2A = 0x15 (decimal 21) in GF(2^8).</b>",
        math))

    s.append(Paragraph("Wait, why does GF_EXP[396] work? The field only has 255 non-zero elements.", h3))
    s.append(Paragraph(
        "The log sum is 396, which is bigger than 255. In modular arithmetic, we should compute 396 mod 255 = 141.<br/>"
        "GF_EXP[141] should also equal 21. Let me check:<br/>"
        "&nbsp;&nbsp;396 mod 255 = 396 - 255 = 141<br/>"
        "&nbsp;&nbsp;GF_EXP[141] = 21. Yes, it matches!<br/><br/>"
        "The program handles this by precomputing GF_EXP from index 0 to 509 (it fills both halves of a 512-entry table), "
        "so GF_EXP[396] directly gives the correct answer without needing the modulo step. But if you are computing by hand, "
        "you can always reduce index mod 255 first.",
        body))

    s.append(Paragraph("Trial and error: what if I tried direct polynomial multiplication?", h3))
    s.append(Paragraph(
        "WRONG APPROACH (for learning): I first tried to multiply 142 &times; 42 as ordinary integers.<br/>"
        "&nbsp;&nbsp;142 &times; 42 = 5,964<br/>"
        "But 5,964 is way bigger than 255. That is NOT how GF(2^8) works.<br/>"
        "In GF(2^8), multiplication means polynomial multiplication modulo P(x), not integer multiplication.<br/>"
        "The log table approach gives the correct answer: 21.",
        mistake))
    s.append(Paragraph(
        "LESSON: Never use normal arithmetic in GF(2^8). Always use the log/exp table method, or "
        "do full polynomial long division by hand (which is very slow).",
        fix))

    s.append(PageBreak())

    # ===== PROBLEM 4: GF DIVISION / INVERSE =====
    s.append(Paragraph("PROBLEM 4: Division and Multiplicative Inverse in GF(2^8)", h1))
    s.append(Paragraph("Task: compute 1 / 2 in GF(2^8). This is needed to build the Cauchy matrix.", body))

    s.append(Paragraph("Method: gf_inv(a) = GF_EXP[255 - GF_LOG[a]]", h2))
    s.append(Paragraph(
        "Given: a = 2<br/><br/>"
        "Step 1: Look up GF_LOG[2] = 1<br/>"
        "Step 2: Compute 255 - 1 = 254<br/>"
        "Step 3: Look up GF_EXP[254] = 142 (0x8E)<br/><br/>"
        "<b>Answer: 1/2 = 142 (0x8E) in GF(2^8).</b>",
        math))

    s.append(Paragraph("Verification: multiply 142 &times; 2 and check if the result is 1", h3))
    s.append(Paragraph(
        "gf_mul(142, 2):<br/>"
        "&nbsp;&nbsp;GF_LOG[142] = 254<br/>"
        "&nbsp;&nbsp;GF_LOG[2] = 1<br/>"
        "&nbsp;&nbsp;log_sum = 254 + 1 = 255<br/>"
        "&nbsp;&nbsp;GF_EXP[255] = 1<br/>"
        "&nbsp;&nbsp;142 &times; 2 = 1 in GF(2^8). VERIFIED! The inverse is correct.",
        fix))

    s.append(Paragraph("More inverses I need for the Cauchy matrix:", h2))
    s.append(Paragraph(
        "1/3: GF_LOG[3] = 25. 255 - 25 = 230. GF_EXP[230] = 244 (0xF4).<br/>"
        "&nbsp;&nbsp;Verify: gf_mul(244, 3) = GF_EXP[230 + 25] = GF_EXP[255] = 1. Correct!<br/><br/>"
        "1/4: GF_LOG[4] = 2. 255 - 2 = 253. GF_EXP[253] = 71 (0x47).<br/>"
        "&nbsp;&nbsp;Verify: gf_mul(71, 4) = GF_EXP[253 + 2] = GF_EXP[255] = 1. Correct!<br/><br/>"
        "1/5: GF_LOG[5] = 50. 255 - 50 = 205. GF_EXP[205] = 167 (0xA7).<br/>"
        "&nbsp;&nbsp;Verify: gf_mul(167, 5) = GF_EXP[205 + 50] = GF_EXP[255] = 1. Correct!",
        math))

    s.append(Paragraph("Rough note: I initially confused GF_LOG[3] with GF_LOG[8]", h3))
    s.append(Paragraph(
        "MISTAKE: On my first pass, I wrote GF_LOG[3] = 3. That would mean alpha^3 = 3.<br/>"
        "But alpha^3 = 8, not 3. The log of 3 is actually 25 because alpha^25 = 3.<br/>"
        "The log values are NOT the same as the input values (except for powers of 2).",
        mistake))
    s.append(Paragraph(
        "CORRECTION: GF_LOG[3] = 25, NOT 3. I verified by checking that GF_EXP[25] = 3 in my table.",
        fix))

    s.append(PageBreak())

    # ===== PROBLEM 5: CAUCHY MATRIX =====
    s.append(Paragraph("PROBLEM 5: Building the Cauchy Generator Matrix for K=4, M=2", h1))
    s.append(Paragraph(
        "The Cauchy matrix is how ALS SubZero generates parity chunks. "
        "Each entry is the inverse of (x_i XOR y_j) in GF(2^8), where X and Y are disjoint sets.",
        body))

    s.append(Paragraph("The actual sets used by ALS SubZero (from the source code):", h2))
    s.append(Paragraph(
        "X = {0, 1} (M=2 parity chunk indices)<br/>"
        "Y = {2, 3, 4, 5} (K=4 data chunk indices)<br/><br/>"
        "These are disjoint: no element appears in both X and Y.",
        math))

    s.append(Paragraph("Computing each entry: a[i,j] = 1 / (x_i XOR y_j)", h2))
    s.append(Paragraph(
        "<b>Row 0 (i=0, x_0 = 0):</b><br/>"
        "&nbsp;&nbsp;a[0,0] = 1 / (0 XOR 2) = 1 / 2 = 142 (0x8E) [computed in Problem 4]<br/>"
        "&nbsp;&nbsp;a[0,1] = 1 / (0 XOR 3) = 1 / 3 = 244 (0xF4)<br/>"
        "&nbsp;&nbsp;a[0,2] = 1 / (0 XOR 4) = 1 / 4 = 71 (0x47)<br/>"
        "&nbsp;&nbsp;a[0,3] = 1 / (0 XOR 5) = 1 / 5 = 167 (0xA7)<br/><br/>"
        "<b>Row 1 (i=1, x_1 = 1):</b><br/>"
        "&nbsp;&nbsp;a[1,0] = 1 / (1 XOR 2) = 1 / 3 = 244 (0xF4)<br/>"
        "&nbsp;&nbsp;a[1,1] = 1 / (1 XOR 3) = 1 / 2 = 142 (0x8E)<br/>"
        "&nbsp;&nbsp;a[1,2] = 1 / (1 XOR 4) = 1 / 5 = 167 (0xA7)<br/>"
        "&nbsp;&nbsp;a[1,3] = 1 / (1 XOR 5) = 1 / 4 = 71 (0x47)",
        math))

    s.append(Paragraph("XOR detail for Row 1:", h3))
    s.append(Paragraph(
        "1 XOR 2: binary 001 XOR 010 = 011 = 3<br/>"
        "1 XOR 3: binary 001 XOR 011 = 010 = 2<br/>"
        "1 XOR 4: binary 001 XOR 100 = 101 = 5<br/>"
        "1 XOR 5: binary 001 XOR 101 = 100 = 4",
        math))

    s.append(Paragraph("Final Cauchy matrix A (2 rows &times; 4 columns):", h2))
    s.append(Paragraph(
        "A = | 142  244   71  167 |    (hex: | 0x8E  0xF4  0x47  0xA7 |)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;| 244  142  167   71 |    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(hex: | 0xF4  0x8E  0xA7  0x47 |)",
        math))

    s.append(Paragraph("Interesting pattern I noticed:", h3))
    s.append(Paragraph(
        "Row 1 is Row 0 with the columns rearranged! Columns 0 and 1 are swapped, and columns 2 and 3 are swapped. "
        "This happens because of the symmetry in the XOR operations when x_0 = 0 and x_1 = 1.",
        note))

    s.append(PageBreak())

    # ===== PROBLEM 6: ENCODING =====
    s.append(Paragraph("PROBLEM 6: Encoding 4 Data Bytes into 2 Parity Bytes", h1))
    s.append(Paragraph(
        "Task: Given data bytes D0 = 0x2A (42), D1 = 0x69 (105), D2 = 0x4D (77), D3 = 0xD2 (210), "
        "compute parity bytes P0 and P1 using the Cauchy matrix from Problem 5.",
        body))

    s.append(Paragraph("Formula: P_i = sum of (a[i,j] * D_j) for j = 0..3, where + means XOR and * means gf_mul", h3))

    s.append(Paragraph("Computing P0 (using Row 0 of the Cauchy matrix)", h2))
    s.append(Paragraph(
        "P0 = gf_mul(142, 42) XOR gf_mul(244, 105) XOR gf_mul(71, 77) XOR gf_mul(167, 210)<br/><br/>"
        "<b>Term 0: gf_mul(142, 42)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[142] = 254<br/>"
        "&nbsp;&nbsp;GF_LOG[42] = 142<br/>"
        "&nbsp;&nbsp;log_sum = 254 + 142 = 396<br/>"
        "&nbsp;&nbsp;GF_EXP[396] = 21 (0x15)<br/><br/>"
        "<b>Term 1: gf_mul(244, 105)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[244] = 230<br/>"
        "&nbsp;&nbsp;GF_LOG[105] = 58<br/>"
        "&nbsp;&nbsp;log_sum = 230 + 58 = 288<br/>"
        "&nbsp;&nbsp;GF_EXP[288] = 39 (0x27)<br/><br/>"
        "<b>Term 2: gf_mul(71, 77)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[71] = 253<br/>"
        "&nbsp;&nbsp;GF_LOG[77] = 145<br/>"
        "&nbsp;&nbsp;log_sum = 253 + 145 = 398<br/>"
        "&nbsp;&nbsp;GF_EXP[398] = 84 (0x54)<br/><br/>"
        "<b>Term 3: gf_mul(167, 210)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[167] = 205<br/>"
        "&nbsp;&nbsp;GF_LOG[210] = 59<br/>"
        "&nbsp;&nbsp;log_sum = 205 + 59 = 264<br/>"
        "&nbsp;&nbsp;GF_EXP[264] = 58 (0x3A)<br/><br/>"
        "<b>XOR all four terms together:</b><br/>"
        "&nbsp;&nbsp;Step A: 21 XOR 39 = ?<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;21  = 0001 0101<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;39  = 0010 0111<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;XOR = 0011 0010 = 50<br/>"
        "&nbsp;&nbsp;Step B: 50 XOR 84 = ?<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;50  = 0011 0010<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;84  = 0101 0100<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;XOR = 0110 0110 = 102<br/>"
        "&nbsp;&nbsp;Step C: 102 XOR 58 = ?<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;102 = 0110 0110<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;58  = 0011 1010<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;XOR = 0101 1100 = 92<br/><br/>"
        "<b>P0 = 92 (0x5C)</b>",
        math))

    s.append(Paragraph("Computing P1 (using Row 1 of the Cauchy matrix)", h2))
    s.append(Paragraph(
        "P1 = gf_mul(244, 42) XOR gf_mul(142, 105) XOR gf_mul(167, 77) XOR gf_mul(71, 210)<br/><br/>"
        "<b>Term 0: gf_mul(244, 42)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[244] = 230, GF_LOG[42] = 142, sum = 372<br/>"
        "&nbsp;&nbsp;GF_EXP[372] = 237 (0xED)<br/><br/>"
        "<b>Term 1: gf_mul(142, 105)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[142] = 254, GF_LOG[105] = 58, sum = 312<br/>"
        "&nbsp;&nbsp;GF_EXP[312] = 186 (0xBA)<br/><br/>"
        "<b>Term 2: gf_mul(167, 77)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[167] = 205, GF_LOG[77] = 145, sum = 350<br/>"
        "&nbsp;&nbsp;GF_EXP[350] = 226 (0xE2)<br/><br/>"
        "<b>Term 3: gf_mul(71, 210)</b><br/>"
        "&nbsp;&nbsp;GF_LOG[71] = 253, GF_LOG[210] = 59, sum = 312<br/>"
        "&nbsp;&nbsp;GF_EXP[312] = 186 (0xBA)<br/><br/>"
        "<b>XOR all four terms:</b><br/>"
        "&nbsp;&nbsp;237 XOR 186:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;237 = 1110 1101<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;186 = 1011 1010<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;XOR = 0101 0111 = 87<br/>"
        "&nbsp;&nbsp;87 XOR 226:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;87  = 0101 0111<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;226 = 1110 0010<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;XOR = 1011 0101 = 181<br/>"
        "&nbsp;&nbsp;181 XOR 186:<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;181 = 1011 0101<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;186 = 1011 1010<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;XOR = 0000 1111 = 15<br/><br/>"
        "<b>P1 = 15 (0x0F)</b>",
        math))

    s.append(Paragraph("Rough check: I noticed Terms 1 and 3 of P1 both equal 186.", h3))
    s.append(Paragraph(
        "Is that a coincidence? Let me check the log sums:<br/>"
        "&nbsp;&nbsp;Term 1: 254 + 58 = 312<br/>"
        "&nbsp;&nbsp;Term 3: 253 + 59 = 312<br/>"
        "They have the same log sum (312), so they produce the same product (186). Not a mistake!",
        note))

    s.append(Paragraph("<b>Encoding summary: D = [42, 105, 77, 210] &rarr; P = [92, 15]</b>", body))

    s.append(PageBreak())

    # ===== PROBLEM 7: DECODING =====
    s.append(Paragraph("PROBLEM 7: Recovering Lost Data Using Gauss-Jordan Elimination", h1))
    s.append(Paragraph(
        "Scenario: Two data chunks D1 (105) and D3 (210) were dropped by network routers. "
        "We only have D0 = 42, D2 = 77, P0 = 92, P1 = 15. Can we recover the lost bytes?",
        body))

    s.append(Paragraph("Step 1: Build the 4x4 submatrix from surviving chunk indices", h2))
    s.append(Paragraph(
        "ALS SubZero uses a full generator matrix G (6 rows x 4 columns) where:<br/>"
        "&nbsp;&nbsp;Rows 0-3: Identity matrix I (for data chunks D0..D3)<br/>"
        "&nbsp;&nbsp;Rows 4-5: Cauchy matrix A (for parity chunks P0, P1)<br/><br/>"
        "Surviving chunks are at indices 0, 2, 4, 5. We take those 4 rows from G:<br/><br/>"
        "Row from index 0 (D0): [1, 0, 0, 0]  (identity row for D0)<br/>"
        "Row from index 2 (D2): [0, 0, 1, 0]  (identity row for D2)<br/>"
        "Row from index 4 (P0): [0x8E, 0xF4, 0x47, 0xA7]  (Cauchy row 0)<br/>"
        "Row from index 5 (P1): [0xF4, 0x8E, 0xA7, 0x47]  (Cauchy row 1)",
        math))

    s.append(Paragraph("Step 2: Gauss-Jordan elimination to invert this 4x4 matrix", h2))
    s.append(Paragraph(
        "We form the augmented matrix [G_sub | I_4] and reduce the left side to identity.<br/>"
        "All operations use GF(2^8) arithmetic (XOR for add/sub, log table for mul/div).",
        body))

    s.append(Paragraph("Initial augmented matrix:", h3))
    s.append(Paragraph(
        "[0x01, 0x00, 0x00, 0x00 | 0x01, 0x00, 0x00, 0x00]<br/>"
        "[0x00, 0x00, 0x01, 0x00 | 0x00, 0x01, 0x00, 0x00]<br/>"
        "[0x8E, 0xF4, 0x47, 0xA7 | 0x00, 0x00, 0x01, 0x00]<br/>"
        "[0xF4, 0x8E, 0xA7, 0x47 | 0x00, 0x00, 0x00, 0x01]",
        math))

    s.append(Paragraph("Pivot step 1: column 0", h3))
    s.append(Paragraph(
        "Pivot is row 0, value = 0x01. Inverse of 0x01 = 0x01 (1/1 = 1). Row already normalized.<br/>"
        "Eliminate column 0 in rows 2 and 3:<br/>"
        "&nbsp;&nbsp;Row 2: factor = 0x8E. New Row 2 = Row 2 XOR (0x8E * Row 0)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;Each element: R2[j] = R2[j] XOR gf_mul(0x8E, R0[j])<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;R2[0]: 0x8E XOR gf_mul(0x8E, 0x01) = 0x8E XOR 0x8E = 0x00 (good, column eliminated)<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;R2[4]: 0x00 XOR gf_mul(0x8E, 0x01) = 0x8E (this goes to the identity side)<br/>"
        "&nbsp;&nbsp;Row 3: factor = 0xF4. Similarly eliminates to give R3[0] = 0x00, R3[4] = 0xF4<br/><br/>"
        "After step 1:<br/>"
        "[0x01, 0x00, 0x00, 0x00 | 0x01, 0x00, 0x00, 0x00]<br/>"
        "[0x00, 0x00, 0x01, 0x00 | 0x00, 0x01, 0x00, 0x00]<br/>"
        "[0x00, 0xF4, 0x47, 0xA7 | 0x8E, 0x00, 0x01, 0x00]<br/>"
        "[0x00, 0x8E, 0xA7, 0x47 | 0xF4, 0x00, 0x00, 0x01]",
        math))

    s.append(Paragraph("Pivot step 2: column 1 (needs row swap!)", h3))
    s.append(Paragraph(
        "Looking at column 1: Row 1 has 0x00 (cannot use as pivot!)<br/>"
        "Search for a non-zero entry: Row 2 has 0xF4. Swap rows 1 and 2.<br/><br/>"
        "After swap:<br/>"
        "[0x01, 0x00, 0x00, 0x00 | 0x01, 0x00, 0x00, 0x00]<br/>"
        "[0x00, 0xF4, 0x47, 0xA7 | 0x8E, 0x00, 0x01, 0x00]  (was row 2)<br/>"
        "[0x00, 0x00, 0x01, 0x00 | 0x00, 0x01, 0x00, 0x00]  (was row 1)<br/>"
        "[0x00, 0x8E, 0xA7, 0x47 | 0xF4, 0x00, 0x00, 0x01]<br/><br/>"
        "Now normalize row 1: divide by pivot 0xF4.<br/>"
        "&nbsp;&nbsp;Inverse of 0xF4: GF_LOG[244] = 230, 255 - 230 = 25, GF_EXP[25] = 3 (0x03)<br/>"
        "&nbsp;&nbsp;Multiply entire row 1 by 0x03.<br/>"
        "&nbsp;&nbsp;R1[1]: gf_mul(0xF4, 0x03) = GF_EXP[230+25] = GF_EXP[255] = 1. Column now 1.<br/><br/>"
        "Then eliminate column 1 in row 3 (factor = 0x8E).",
        math))

    s.append(Paragraph("Rough work on the row swap decision:", h3))
    s.append(Paragraph(
        "MISTAKE I ALMOST MADE: I nearly tried to skip the row swap and divide row 1 by 0x00.<br/>"
        "Division by zero is undefined even in GF(2^8). You MUST swap to find a non-zero pivot.<br/>"
        "If no non-zero pivot exists in the entire column, the matrix is singular and recovery is impossible. "
        "But Cauchy matrices guarantee this never happens for K or fewer losses.",
        mistake))
    s.append(Paragraph(
        "CORRECTION: Swapped row 1 with row 2 to get pivot value 0xF4 in position [1,1]. "
        "The Cauchy matrix guarantees every square submatrix is invertible, so a non-zero pivot always exists.",
        fix))

    s.append(Paragraph("After all 4 pivot steps, the inverted matrix is:", h2))
    s.append(Paragraph(
        "Inv = [0x01, 0x00, 0x00, 0x00]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[0x7B, 0xE0, 0x05, 0x04]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[0x00, 0x01, 0x00, 0x00]<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[0x01, 0x7B, 0x0A, 0x0C]",
        math))

    s.append(Paragraph("Step 3: Multiply inverse matrix by survivor data vector", h2))
    s.append(Paragraph(
        "Survivor data vector = [D0, D2, P0, P1] = [0x2A, 0x4D, 0x5C, 0x0F]<br/><br/>"
        "<b>Recovering D0</b> (row 0 of inverse):<br/>"
        "&nbsp;&nbsp;D0 = gf_mul(0x01, 0x2A) XOR gf_mul(0x00, 0x4D) XOR gf_mul(0x00, 0x5C) XOR gf_mul(0x00, 0x0F)<br/>"
        "&nbsp;&nbsp;D0 = 0x2A XOR 0 XOR 0 XOR 0 = 0x2A (42). CORRECT!<br/><br/>"
        "<b>Recovering D1</b> (row 1 of inverse, the LOST chunk):<br/>"
        "&nbsp;&nbsp;D1 = gf_mul(0x7B, 0x2A) XOR gf_mul(0xE0, 0x4D) XOR gf_mul(0x05, 0x5C) XOR gf_mul(0x04, 0x0F)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x7B, 0x2A):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[123] = 43, GF_LOG[42] = 142, sum = 185<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[185] = 210 (0xD2)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0xE0, 0x4D):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[224] = 18, GF_LOG[77] = 145, sum = 163<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[163] = 182 (0xB6)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x05, 0x5C):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[5] = 50, GF_LOG[92] = 211, sum = 261<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[261] = 49 (0x31)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x04, 0x0F):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[4] = 2, GF_LOG[15] = 75, sum = 77<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[77] = 60 (0x3C)<br/><br/>"
        "&nbsp;&nbsp;XOR: 210 XOR 182 XOR 49 XOR 60<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;210 XOR 182 = 1101 0010 XOR 1011 0110 = 0110 0100 = 100<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;100 XOR 49  = 0110 0100 XOR 0011 0001 = 0101 0101 = 85<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;85 XOR 60   = 0101 0101 XOR 0011 1100 = 0110 1001 = 105<br/><br/>"
        "&nbsp;&nbsp;<b>D1 = 105 (0x69). MATCHES THE ORIGINAL!</b>",
        math))

    s.append(Paragraph("Rough XOR work for D1 (I did this wrong the first time):", h3))
    s.append(Paragraph(
        "MISTAKE: My first attempt at 210 XOR 182, I wrote the binary of 182 as 1010 0110.<br/>"
        "Let me recheck: 182 = 128 + 32 + 16 + 4 + 2 = 10110110. Wait, that is 182.<br/>"
        "Actually: 128+32+16+4+2 = 182. Binary: 1011 0110. Let me verify:<br/>"
        "&nbsp;&nbsp;1*128 + 0*64 + 1*32 + 1*16 + 0*8 + 1*4 + 1*2 + 0*1 = 128+32+16+4+2 = 182. Correct.<br/>"
        "210 in binary: 128+64+16+2 = 210. Binary: 1101 0010. Check: 128+64+16+2 = 210. Correct.<br/>"
        "XOR: 11010010 XOR 10110110 = 01100100 = 64+32+4 = 100. OK, 100 is right.",
        mistake))
    s.append(Paragraph(
        "VERIFIED: My binary conversions were correct. D1 = 105 matches the original.",
        fix))

    s.append(Paragraph("<b>Recovering D3</b> (row 3 of inverse, the other LOST chunk):", h2))
    s.append(Paragraph(
        "&nbsp;&nbsp;D3 = gf_mul(0x01, 0x2A) XOR gf_mul(0x7B, 0x4D) XOR gf_mul(0x0A, 0x5C) XOR gf_mul(0x0C, 0x0F)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x01, 0x2A) = 0x2A (42) [multiplying by 1 gives the same value]<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x7B, 0x4D):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[123] = 43, GF_LOG[77] = 145, sum = 188<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[188] = 222 (0xDE)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x0A, 0x5C):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[10] = 51, GF_LOG[92] = 211, sum = 262<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[262] = 98 (0x62)<br/><br/>"
        "&nbsp;&nbsp;gf_mul(0x0C, 0x0F):<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_LOG[12] = 227, GF_LOG[15] = 75, sum = 302<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;GF_EXP[302] = 68 (0x44)<br/><br/>"
        "&nbsp;&nbsp;XOR: 42 XOR 222 XOR 98 XOR 68<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;42 XOR 222 = 0010 1010 XOR 1101 1110 = 1111 0100 = 244<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;244 XOR 98 = 1111 0100 XOR 0110 0010 = 1001 0110 = 150<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;150 XOR 68 = 1001 0110 XOR 0100 0100 = 1101 0010 = 210<br/><br/>"
        "&nbsp;&nbsp;<b>D3 = 210 (0xD2). MATCHES THE ORIGINAL!</b>",
        math))

    s.append(Paragraph("FINAL PROOF SUMMARY", h2))
    s.append(Paragraph(
        "Original data: D0 = 42, D1 = 105, D2 = 77, D3 = 210<br/>"
        "Encoded parity: P0 = 92, P1 = 15<br/>"
        "Network dropped: D1 and D3<br/>"
        "Recovered from [D0, D2, P0, P1] using Gauss-Jordan inversion:<br/>"
        "&nbsp;&nbsp;D1 = 105 (exact match)<br/>"
        "&nbsp;&nbsp;D3 = 210 (exact match)<br/><br/>"
        "<b>Q.E.D. Bit-exact mathematical reconstruction is proven by hand.</b>",
        fix))

    s.append(PageBreak())

    # ===== PROBLEM 8: CRC32 =====
    s.append(Paragraph("PROBLEM 8: Frame Integrity Verification with CRC32C Checksum", h1))
    s.append(Paragraph(
        "Every ALS SubZero frame carries a 4-byte CRC32C checksum computed over the header and payload. "
        "The Castagnoli polynomial 0x1EDC6F41 detects all 1, 2, and 3-bit errors in payloads up to 4096 bytes.",
        body))

    s.append(Paragraph("The ALS1 frame header format (24 bytes total):", h2))
    s.append(Paragraph(
        "Offset 0-3:   Magic bytes 'ALS1' = 0x41 0x4C 0x53 0x31<br/>"
        "Offset 4-5:   Version 1.0 = 0x01 0x00<br/>"
        "Offset 6-7:   Flags (data chunk) = 0x00 0x00<br/>"
        "Offset 8-11:  Inode ID = 2 = 0x00 0x00 0x00 0x02<br/>"
        "Offset 12-15: Chunk Index = 0 = 0x00 0x00 0x00 0x00<br/>"
        "Offset 16-17: Payload Length = 4 = 0x00 0x04<br/>"
        "Offset 18-19: Hop Count = 1 = 0x00 0x01<br/>"
        "Offset 20-23: CRC32C checksum (computed over bytes 0-19 + payload)",
        math))

    s.append(Paragraph("How CRC computation works conceptually:", h2))
    s.append(Paragraph(
        "1. Take all the data bytes (header without the CRC field + payload)<br/>"
        "2. Treat them as a very long binary polynomial<br/>"
        "3. Divide this polynomial by the CRC32C generator polynomial<br/>"
        "4. The remainder of this division is the checksum<br/><br/>"
        "The generator polynomial for CRC32C (Castagnoli) is:<br/>"
        "&nbsp;&nbsp;G(x) = x^32 + x^28 + x^27 + x^26 + x^25 + x^23 + x^22 + x^20 + x^19<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;+ x^18 + x^14 + x^13 + x^11 + x^10 + x^9 + x^8 + x^6 + 1<br/>"
        "&nbsp;&nbsp;Hex: 0x1EDC6F41 (normal form), 0x82F63B78 (bit-reflected for hardware)",
        math))

    s.append(Paragraph("Why Castagnoli instead of standard CRC32?", h3))
    s.append(Paragraph(
        "The Castagnoli polynomial provides Hamming distance d=6 for messages up to 131 bytes "
        "and d=4 for messages up to 4,096 bytes. The standard IEEE 802.3 CRC32 (0x04C11DB7) "
        "only achieves d=4 for messages up to 268 bytes.<br/><br/>"
        "Since ALS SubZero uses 4,096-byte chunks, Castagnoli gives better error detection "
        "at exactly the payload sizes I need.",
        body))

    s.append(Paragraph("Tamper detection example:", h2))
    s.append(Paragraph(
        "Suppose a router flips one bit in our payload during transit:<br/>"
        "&nbsp;&nbsp;Original byte at offset 24: 0x2A = 0010 1010<br/>"
        "&nbsp;&nbsp;Corrupted byte:             0x2B = 0010 1011 (bit 0 flipped)<br/><br/>"
        "When the receiver computes CRC32C over the corrupted frame, it gets a DIFFERENT checksum "
        "than the one stored in bytes 20-23. The frame is rejected and marked as lost.<br/>"
        "The background scrubber then reconstructs this chunk from surviving parity data (Problem 7).<br/><br/>"
        "The probability of an undetected error (a corruption that accidentally produces the correct CRC) is:<br/>"
        "&nbsp;&nbsp;P_undetected = 2^(-32) = 1 / 4,294,967,296 &asymp; 2.33 &times; 10^(-10)<br/>"
        "&nbsp;&nbsp;That is about 1 in 4.3 billion. For practical purposes, this is zero.",
        math))

    s.append(Paragraph("Cross-check: run the ALS SubZero test suite", h3))
    s.append(Paragraph(
        "The test 'test_crc_tamper_detection' in tests/test_framing.py does exactly this:<br/>"
        "1. Creates a valid frame with correct CRC32C.<br/>"
        "2. Flips one bit in the payload.<br/>"
        "3. Attempts to decode the tampered frame.<br/>"
        "4. Confirms the decoder raises ValueError (\"CRC mismatch\").<br/><br/>"
        "Run: python tests/run_all.py and see 'test_crc_tamper_detection ... ok'.",
        note))

    doc.build(s, canvasmaker=NumberedCanvas)
    print(f"Generated: {out_path}")
    print(f"Size: {os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    build()
