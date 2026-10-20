"""Genereert docs/Bouwgids-Kameralarm.pdf (stap-voor-stap bouwinstructies met tekeningen).

Gebruik:  python tools/maak_bouwgids.py
"""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Flowable, KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "Bouwgids-Kameralarm.pdf"

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic")

# ---------- stijlen ----------
INK = colors.HexColor("#1f2430")
MUTED = colors.HexColor("#5b6475")
RED = colors.HexColor("#d62828")
BLUE = colors.HexColor("#1d4ed8")
GREEN = colors.HexColor("#15803d")
ORANGE = colors.HexColor("#ea7a00")
WARN_BG = colors.HexColor("#fdecec")
TIP_BG = colors.HexColor("#eaf2fe")
OK_BG = colors.HexColor("#e9f7ee")

S = {
    "title": ParagraphStyle("title", fontName="Arial-Bold", fontSize=26, leading=31, textColor=INK, alignment=TA_CENTER),
    "subtitle": ParagraphStyle("subtitle", fontName="Arial", fontSize=13, leading=18, textColor=MUTED, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=18, leading=23, textColor=INK, spaceBefore=4, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=12.5, leading=16, textColor=INK, spaceBefore=8, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="Arial", fontSize=10.5, leading=14.5, textColor=INK),
    "step": ParagraphStyle("step", fontName="Arial", fontSize=10.5, leading=14.5, textColor=INK, leftIndent=16, firstLineIndent=-16, spaceAfter=3),
    "small": ParagraphStyle("small", fontName="Arial", fontSize=8.5, leading=11, textColor=MUTED),
    "cell": ParagraphStyle("cell", fontName="Arial", fontSize=9.5, leading=12.5, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="Arial-Bold", fontSize=9.5, leading=12.5, textColor=INK),
}


def P(text, style="body"):
    return Paragraph(text, S[style])


def steps(items):
    return [P(f"<b>{i}.</b>&nbsp;&nbsp;{t}", "step") for i, t in enumerate(items, 1)]


def box(title, lines, bg, border):
    content = [P(f"<b>{title}</b>", "body")] + [P(l, "body") for l in lines]
    t = Table([[content]], colWidths=[176 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1.2, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def warn(lines, title="LET OP"):
    return box(title, lines, WARN_BG, RED)


def tip(lines, title="Tip"):
    return box(title, lines, TIP_BG, BLUE)


def ok(lines, title="Wat je moet zien"):
    return box(title, lines, OK_BG, GREEN)


def table(rows, widths, header=True):
    data = [[P(c, "cellb" if (header and r == 0) else "cell") for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9cfda")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#eef1f6")))
    t.setStyle(TableStyle(style))
    return t


# ---------- breadboard-tekening ----------
# Kolomposities (in "gaatjes"): L+ L-  a b c d e  (gleuf)  f g h i j  R- R+
COLS = {"L+": 0, "L-": 1, "a": 3, "b": 4, "c": 5, "d": 6, "e": 7,
        "f": 10, "g": 11, "h": 12, "i": 13, "j": 14, "R+": 16, "R-": 17}
ROWS = 30

C_5V, C_GND = colors.HexColor("#e11d48"), colors.HexColor("#111827")
C_SIG = colors.HexColor("#ea7a00")
C_LOCAL = colors.HexColor("#7c3aed")

# Elk onderdeel: (stap, soort, gegevens)
ITEMS = [
    # Stap 2 – voeding
    (2, "esp", ("L+", 1, "VIN  (bb1 j2)", C_5V)),
    (2, "esp", ("L-", 3, "GND  (bb1 j3)", C_GND)),
    (2, "wire", (("L+", 30), ("R+", 30), C_5V)),
    (2, "wire", (("L-", 29), ("R-", 29), C_GND)),
    # Stap 3 – rode + blauwe led
    (3, "esp", ("b", 22, "D25  (bb1 j9)", C_SIG)),
    (3, "res", (("e", 22), ("f", 22), "220")),
    (3, "led", (("h", 22), ("h", 23), RED, "rood")),
    (3, "wire", (("j", 23), ("R-", 23), C_GND)),
    (3, "esp", ("b", 25, "D33  (bb1 j10)", C_SIG)),
    (3, "res", (("e", 25), ("f", 25), "220")),
    (3, "led", (("h", 25), ("h", 26), BLUE, "blauw")),
    (3, "wire", (("j", 26), ("R-", 26), C_GND)),
    # Stap 4 – RGB-led
    (4, "esp", ("b", 17, "D13  (bb1 j4)", C_SIG)),
    (4, "esp", ("b", 19, "D14  (bb1 j6)", C_SIG)),
    (4, "esp", ("b", 20, "D32  (bb1 j11)", C_SIG)),
    (4, "res", (("e", 17), ("f", 17), "220")),
    (4, "res", (("e", 19), ("f", 19), "220")),
    (4, "res", (("e", 20), ("f", 20), "220")),
    (4, "rgb", ("h", 17)),
    (4, "wire", (("j", 18), ("R-", 18), C_GND)),
    # Stap 5 – zoemer + transistor
    (5, "tr", ("g", 3)),
    (5, "res", (("f", 4), ("f", 7), "1k")),
    (5, "espR", ("g", 7, "D12  (bb1 j5)", C_SIG)),
    (5, "wire", (("j", 5), ("R-", 5), C_GND)),
    (5, "wire", (("h", 3), ("g", 10), C_LOCAL)),
    (5, "buz", (("j", 10), ("j", 13))),
    (5, "wire", (("g", 13), ("R+", 13), C_5V)),
    # Stap 6 – ultrasone sensor
    (6, "ext", ("a", 1, "VCC")), (6, "ext", ("a", 2, "Trig")),
    (6, "ext", ("a", 3, "Echo")), (6, "ext", ("a", 4, "GND")),
    (6, "wire", (("b", 1), ("L+", 1), C_5V)),
    (6, "wire", (("b", 4), ("L-", 4), C_GND)),
    (6, "esp", ("b", 2, "D26  (bb1 j8)", C_SIG)),
    (6, "res", (("c", 3), ("c", 6), "1k")),
    (6, "res", (("a", 6), ("L-", 6), "2k")),
    (6, "esp", ("b", 6, "D27  (bb1 j7)", C_SIG)),
    # Stap 7 – PIR
    (7, "ext", ("a", 8, "VCC")), (7, "ext", ("a", 9, "OUT")), (7, "ext", ("a", 10, "GND")),
    (7, "wire", (("b", 8), ("L+", 8), C_5V)),
    (7, "wire", (("b", 10), ("L-", 10), C_GND)),
    (7, "esp", ("b", 9, "D34  (bb1 j13)", C_SIG)),
    # Stap 8 – IR-ontvanger
    (8, "ext", ("a", 12, "S")), (8, "ext", ("a", 13, "+")), (8, "ext", ("a", 14, "−")),
    (8, "wire", (("b", 13), ("L+", 13), C_5V)),
    (8, "wire", (("b", 14), ("L-", 14), C_GND)),
    (8, "res", (("c", 12), ("c", 16), "1k")),
    (8, "esp", ("b", 16, "D35  (bb1 j12)", C_SIG)),
]

EXT_LABEL = {6: "ultrasone sensor", 7: "PIR", 8: "IR-ontvanger"}


class Breadboard(Flowable):
    """Tekent breadboard 2 met alle onderdelen t/m `step`; die van `step` zelf in kleur."""

    def __init__(self, step, pitch=4.25 * mm, all_active=False):
        super().__init__()
        self.step = step
        self.all_active = all_active
        self.p = pitch
        self.left_margin = 34 * mm
        self.right_margin = 30 * mm
        self.width = self.left_margin + 18 * pitch + self.right_margin
        self.height = (ROWS + 2.2) * pitch

    def xy(self, col, row):
        return self.left_margin + COLS[col] * self.p + self.p / 2, self.height - (row + 1.2) * self.p

    def draw(self):
        c = self.canv
        p = self.p
        # bord
        x0 = self.left_margin - 0.2 * p
        c.setFillColor(colors.HexColor("#f6f4ee"))
        c.setStrokeColor(colors.HexColor("#c8c2b0"))
        c.roundRect(x0, self.height - (ROWS + 1.9) * p, 18.4 * p, (ROWS + 1.4) * p, 4, fill=1, stroke=1)
        # middengleuf
        gx = self.left_margin + 8 * p + p * 0.15
        c.setFillColor(colors.HexColor("#e2ddcf"))
        c.rect(gx, self.height - (ROWS + 1.6) * p, 1.7 * p, (ROWS + 0.8) * p, fill=1, stroke=0)
        # railstrepen
        for col, colr, off in (("L+", C_5V, -0.55), ("L-", BLUE, 0.55), ("R+", C_5V, -0.55), ("R-", BLUE, 0.55)):
            x, _ = self.xy(col, 0)
            c.setStrokeColor(colr)
            c.setLineWidth(1.2)
            c.line(x + off * p, self.height - 1.0 * p, x + off * p, self.height - (ROWS + 1.4) * p)
        # kopjes
        c.setFont("Arial-Bold", 7)
        for col in COLS:
            x, _ = self.xy(col, 0)
            label = {"L+": "+", "L-": "−", "R-": "−", "R+": "+"}.get(col, col)
            c.setFillColor(C_5V if "+" in col else BLUE if "-" in col else INK)
            c.drawCentredString(x, self.height - 0.75 * p, label)
        # rijnummers
        c.setFont("Arial", 6)
        c.setFillColor(MUTED)
        for r in range(1, ROWS + 1):
            _, y = self.xy("a", r)
            c.drawCentredString(self.left_margin + 2 * p + p / 2, y - 2, str(r))
            c.drawCentredString(self.left_margin + 15 * p + p / 2, y - 2, str(r))
        # gaatjes
        c.setFillColor(colors.HexColor("#9a937f"))
        for col in COLS:
            for r in range(1, ROWS + 1):
                x, y = self.xy(col, r)
                c.rect(x - 0.9, y - 0.9, 1.8, 1.8, fill=1, stroke=0)
        # onderdelen
        for st, kind, data in ITEMS:
            if st > self.step:
                continue
            active = self.all_active or st == self.step
            getattr(self, "draw_" + kind)(data, active)
        # rails-uitleg
        c.setFont("Arial", 6.5)
        c.setFillColor(MUTED)
        c.drawString(x0, self.height - (ROWS + 2.15) * p,
                     "BREADBOARD 2  ·  rode lijn (+) = 5V   ·   blauwe lijn (−) = GND")

    # --- helpers ---
    def _col(self, base, active):
        if active:
            return base
        return colors.Color(base.red * 0.35 + 0.62, base.green * 0.35 + 0.62, base.blue * 0.35 + 0.62)

    def _dot(self, x, y, colr):
        c = self.canv
        c.setFillColor(colr)
        c.circle(x, y, 1.5, fill=1, stroke=0)

    def draw_wire(self, data, active):
        (c1, r1), (c2, r2), colr = data
        x1, y1 = self.xy(c1, r1)
        x2, y2 = self.xy(c2, r2)
        col = self._col(colr, active)
        c = self.canv
        c.setStrokeColor(col)
        c.setLineWidth(2.0 if active else 1.3)
        path = c.beginPath()
        path.moveTo(x1, y1)
        if y1 == y2:
            path.curveTo(x1, y1 + 3, x2, y2 + 3, x2, y2)
        else:
            path.lineTo(x2, y2)
        c.drawPath(path, stroke=1, fill=0)
        self._dot(x1, y1, col)
        self._dot(x2, y2, col)

    def _esp(self, data, active, side):
        col, row, label, colr = data
        x, y = self.xy(col, row)
        clr = self._col(colr, active)
        c = self.canv
        c.setStrokeColor(clr)
        c.setLineWidth(2.0 if active else 1.3)
        if side == "L":
            xe = self.left_margin - 1.2 * self.p
            hy = y + 0.75 * self.p  # draad loopt "over" de andere gaatjes heen
            for width, colr in ((4.2, colors.white), (2.0 if active else 1.3, clr)):
                c.setStrokeColor(colr)
                c.setLineWidth(width)
                path = c.beginPath()
                path.moveTo(x, y)
                path.curveTo(x, hy, x - 3, hy, x - 6, hy)
                path.lineTo(xe, hy)
                c.drawPath(path, stroke=1, fill=0)
            c.setFillColor(clr if active else MUTED)
            c.setFont("Arial-Bold" if active else "Arial", 7.2)
            c.drawRightString(xe - 2, hy - 2.4, label)
        else:
            xe = self.left_margin + 18.6 * self.p
            path = c.beginPath()
            path.moveTo(x, y)
            path.curveTo(x + 6, y - 6, xe - 6, y - 6, xe, y - 6)
            c.drawPath(path, stroke=1, fill=0)
            c.setFillColor(clr if active else MUTED)
            c.setFont("Arial-Bold" if active else "Arial", 7.2)
            c.drawString(xe + 2, y - 8.4, label)
        self._dot(x, y, clr)

    def draw_esp(self, data, active):
        self._esp(data, active, "L")

    def draw_espR(self, data, active):
        self._esp(data, active, "R")

    def draw_ext(self, data, active):
        col, row, label = data
        x, y = self.xy(col, row)
        clr = self._col(colors.HexColor("#0f9f6e"), active)
        c = self.canv
        c.setFillColor(clr)
        c.circle(x, y, 2.4, fill=1, stroke=0)
        tx, _ = self.xy("d", row)
        c.setFont("Arial-Bold" if active else "Arial", 6.2)
        c.drawString(tx - 2, y - 2.2, "← " + label)

    def draw_res(self, data, active):
        (c1, r1), (c2, r2), val = data
        x1, y1 = self.xy(c1, r1)
        x2, y2 = self.xy(c2, r2)
        c = self.canv
        lead = self._col(colors.HexColor("#6b7280"), active)
        body = self._col(colors.HexColor("#d9b779") if val == "220" else colors.HexColor("#8ec5ff") if val == "1k" else colors.HexColor("#b9f0b0"), active)
        c.setStrokeColor(lead)
        c.setLineWidth(1)
        c.line(x1, y1, x2, y2)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        horizontal = abs(x2 - x1) > abs(y2 - y1)
        w, h = (9, 4.2) if horizontal else (4.2, 9)
        c.setFillColor(body)
        c.setStrokeColor(self._col(INK, active))
        c.setLineWidth(0.5)
        c.roundRect(mx - w / 2, my - h / 2, w, h, 1.5, fill=1, stroke=1)
        c.setFont("Arial-Bold", 5.6)
        c.setFillColor(self._col(INK, active))
        txt = val + ("Ω" if val == "220" else "Ω" if val in ("1k", "2k") else "")
        if horizontal:
            c.drawCentredString(mx, my + 3.4, txt)
        else:
            c.drawString(mx + 3.2, my - 2, txt)
        self._dot(x1, y1, lead)
        self._dot(x2, y2, lead)

    def draw_led(self, data, active):
        (c1, r1), (c2, r2), colr, name = data
        x1, y1 = self.xy(c1, r1)
        x2, y2 = self.xy(c2, r2)
        c = self.canv
        clr = self._col(colr, active)
        c.setStrokeColor(clr)
        c.setLineWidth(1)
        mx, my = x1 + 6.5, (y1 + y2) / 2
        c.line(x1, y1, mx, y1)
        c.line(x2, y2, mx, y2)
        c.setFillColor(clr)
        c.circle(mx + 2, my, 3.4, fill=1, stroke=0)
        c.setFont("Arial-Bold", 6)
        c.setFillColor(self._col(INK, active))
        c.drawString(x1 - 9.5, y1 + 2.6, "+")
        c.drawString(x2 - 9.5, y2 - 6.3, "−")
        self._dot(x1, y1, clr)
        self._dot(x2, y2, clr)

    def draw_rgb(self, data, active):
        col, row = data
        c = self.canv
        pts = [self.xy(col, row + k) for k in range(4)]
        clr = self._col(colors.HexColor("#a3a3a3"), active)
        mx = pts[0][0] + 6.5
        my = (pts[0][1] + pts[3][1]) / 2
        c.setStrokeColor(clr)
        c.setLineWidth(1)
        for x, y in pts:
            c.line(x, y, mx, y)
            self._dot(x, y, clr)
        c.setFillColor(self._col(colors.HexColor("#e5e7eb"), active))
        c.setStrokeColor(clr)
        c.circle(mx + 3, my, 5.2, fill=1, stroke=1)
        c.setFont("Arial-Bold", 5.6)
        for (x, y), lab, colr in zip(pts, ["R", "GND", "G", "B"], [RED, INK, GREEN, BLUE]):
            c.setFillColor(self._col(colr, active))
            c.drawString(mx + 9.5, y - 2, lab)

    def draw_tr(self, data, active):
        col, row = data
        c = self.canv
        pts = [self.xy(col, row + k) for k in range(3)]
        x = pts[0][0]
        top, bot = pts[0][1] + 3.2, pts[2][1] - 3.2
        c.setFillColor(self._col(colors.HexColor("#374151"), active))
        c.roundRect(x - 4.5, bot, 7.5, top - bot, 3.2, fill=1, stroke=0)
        c.rect(x - 0.5, bot, 3.5, top - bot, fill=1, stroke=0)
        c.setStrokeColor(self._col(colors.HexColor("#facc15"), active))
        c.setLineWidth(1.6)
        c.line(x + 3.0, top, x + 3.0, bot)   # platte kant (geel) naar rechts
        c.setFont("Arial-Bold", 5.8)
        c.setFillColor(self._col(INK, active))
        for (px, py), lab in zip(pts, ["C", "B", "E"]):
            self._dot(px, py, self._col(colors.HexColor("#9ca3af"), active))
            c.drawString(px + 4.6, py - 2, lab)

    def draw_buz(self, data, active):
        (c1, r1), (c2, r2) = data
        x1, y1 = self.xy(c1, r1)
        x2, y2 = self.xy(c2, r2)
        c = self.canv
        mx, my = x1, (y1 + y2) / 2
        c.setFillColor(self._col(colors.HexColor("#111827"), active))
        c.circle(mx, my, 2.35 * self.p, fill=1, stroke=0)
        c.setFillColor(self._col(colors.white, active))
        c.circle(mx, my, 0.5 * self.p, fill=1, stroke=0)
        c.setFont("Arial-Bold", 6.5)
        c.drawCentredString(mx, y1 + 0.5, "−")
        c.drawCentredString(mx, y2 - 4.5, "+")
        self._dot(x1, y1, self._col(colors.HexColor("#9ca3af"), active))
        self._dot(x2, y2, self._col(colors.HexColor("#9ca3af"), active))


def diagram(step, caption, all_active=False):
    d = Breadboard(step, all_active=all_active)
    t = Table([[d], [P(caption, "small")]], colWidths=[d.width + 4])
    t.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    return t


# ---------- tekening breadboard 1 (ESP32) ----------
BB1_PINS = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34", "VN", "VP", "EN"]
BB1_USED = {"VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32", "D35", "D34"}


class Esp32Board(Flowable):
    """Breadboard 1 rechtop: ESP32 met linkerpinnen in kolom a, rechterpinnen in kolom i, kolom j vrij."""

    def __init__(self):
        super().__init__()
        self.p = 4.3 * mm
        self.width, self.height = 170 * mm, 20 * self.p

    def draw(self):
        c, p = self.canv, self.p
        x0 = 18 * mm
        cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 7, "g": 8, "h": 9, "i": 10, "j": 11}

        def X(col):
            return x0 + cols[col] * p + p / 2

        def Y(row):
            return self.height - (row + 1.2) * p

        c.setFillColor(colors.HexColor("#f6f4ee"))
        c.setStrokeColor(colors.HexColor("#c8c2b0"))
        c.roundRect(x0 - 0.3 * p, Y(18.6), 12.6 * p, 18.4 * p, 4, fill=1, stroke=1)
        c.setFillColor(colors.HexColor("#e2ddcf"))
        c.rect(x0 + 5.2 * p, Y(18.4), 1.6 * p, 18 * p, fill=1, stroke=0)
        c.setFont("Arial-Bold", 7)
        c.setFillColor(INK)
        for col in cols:
            c.drawCentredString(X(col), Y(0.35), col)
        for r in range(1, 19):
            c.setFont("Arial", 6)
            c.setFillColor(MUTED)
            c.drawRightString(x0 - 0.5 * p, Y(r) - 2, str(r))
            c.setFillColor(colors.HexColor("#9a937f"))
            for col in cols:
                c.rect(X(col) - 0.9, Y(r) - 0.9, 1.8, 1.8, fill=1, stroke=0)
        # ESP32-bord
        mid = (X("a") + X("i")) / 2
        c.setFillColor(colors.HexColor("#1f2937"))
        c.roundRect(X("a") - 0.45 * p, Y(17.2), X("i") - X("a") + 0.9 * p, 16.4 * p, 3, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#d1d5db"))
        c.rect(mid - 0.9 * p, Y(1.3), 1.8 * p, 1.2 * p, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#9ca3af"))
        c.roundRect(mid - 2.6 * p, Y(15.5), 5.2 * p, 6 * p, 2, fill=1, stroke=0)
        c.setFont("Arial-Bold", 7)
        c.setFillColor(colors.white)
        c.drawCentredString(mid, Y(12.7), "ESP32")
        c.setFont("Arial-Bold", 6)
        c.setFillColor(INK)
        c.drawCentredString(mid, Y(2.5) + 1, "USB-C")
        for k in range(15):
            r = k + 2
            c.setFillColor(colors.HexColor("#fbbf24"))
            c.circle(X("a"), Y(r), 1.5, fill=1, stroke=0)
            c.circle(X("i"), Y(r), 1.5, fill=1, stroke=0)
            name = BB1_PINS[k]
            c.setFillColor(colors.white)
            c.setFont("Arial", 5.2)
            c.drawRightString(X("i") - 3, Y(r) - 1.8, name)
            if name in BB1_USED:
                c.setStrokeColor(GREEN)
                c.setLineWidth(1.2)
                c.circle(X("j"), Y(r), 2.6, fill=0, stroke=1)
                c.setFillColor(GREEN)
                c.setFont("Arial-Bold", 7)
                c.drawString(X("j") + 0.9 * p, Y(r) - 2.3, f"j{r}  =  {name}")
        tx = X("j") + 6.5 * p
        c.setFont("Arial", 8.5)
        lines = [
            ("Linkerpinnen (3V3 … D23) in kolom a, rij 2 t/m 16.", INK),
            ("Rechterpinnen (VIN … EN) in kolom i, rij 2 t/m 16.", INK),
            ("De USB-C-aansluiting wijst naar boven.", INK),
            ("", INK),
            ("Kolom j blijft vrij. Een draad in j9 is dus", GREEN),
            ("verbonden met pin D25, enzovoort.", GREEN),
            ("", INK),
            ("De linkerpinnen gebruiken we niet.", MUTED),
        ]
        for n, (t, colr) in enumerate(lines):
            c.setFillColor(colr)
            c.drawString(tx, Y(3 + n * 1.2), t)
        c.setFont("Arial", 6.5)
        c.setFillColor(MUTED)
        c.drawString(x0 - 0.3 * p, Y(19.4), "BREADBOARD 1  ·  alleen de ESP32")


# ---------- inhoud ----------
def build():
    story = []

    # Voorblad
    story += [Spacer(1, 30 * mm), P("Kameralarm", "title"), Spacer(1, 4 * mm),
              P("Bouwgids voor de ELEGOO ESP32-starterset", "subtitle"), Spacer(1, 2 * mm),
              P("Stap voor stap, met een test na elk onderdeel", "subtitle"), Spacer(1, 18 * mm)]
    story.append(table([
        ["Hoe werkt deze gids?"],
        ["We bouwen het alarm in <b>9 kleine stappen</b>. Na elke stap controleer je je bedrading met de tekening, "
         "en pas daarna steek je de USB-kabel in. Met een testcommando in de seriële monitor zie je meteen of het onderdeel werkt."],
        ["Zo vinden we fouten meteen, en weet je bij een probleem precies welk onderdeel het is."],
        ["Je werkt met <b>5 volt</b>: dat is <b>niet gevaarlijk voor jou</b>. De regels hieronder zijn er om "
         "<b>de onderdelen</b> heel te houden."],
    ], [176]))
    story.append(PageBreak())

    # Veiligheid
    story.append(P("De 8 gouden regels", "h1"))
    story.append(warn([
        "<b>1. USB-kabel eruit</b> zolang je draden plaatst of verplaatst. Altijd.",
        "<b>2. Nooit + rechtstreeks met −</b> verbinden (rode rail met blauwe rail of 5V met GND). Dat is kortsluiting.",
        "<b>3. Nooit 5V op een D-pin</b> van de ESP32. De pinnen kunnen maar 3,3V aan. "
        "Daarom krijgt de ultrasone sensor een spanningsdeler (stap 6) en de IR-ontvanger een weerstand in serie (stap 8). Sla die nooit over.",
        "<b>4. Volg de gekleurde lijnen op je eigen breadboard</b> (rood = +, blauw = −), ook als de tekening anders lijkt.",
        "<b>5. De 9V-batterij en de voedingsmodule blijven in de doos.</b> We gebruiken alleen USB.",
        "<b>6. Leds en de zoemer hebben een richting:</b> lange poot = +. Draai je ze om, dan werken ze niet "
        "(maar ze gaan niet stuk).",
        "<b>7. Na het insteken van de USB: 10 seconden opletten.</b> Wordt iets <b>warm</b>, ruik je iets, "
        "of gaat het rode lampje op het bord uit? <b>Meteen de USB-kabel eruit</b> en stuur een foto.",
        "<b>8. Werk op een houten of plastic tafel</b>, niet op metaal, en laat geen losse draadjes of weerstanden onder het breadboard liggen.",
    ], title="VEILIGHEID – lees dit eerst"))
    story.append(Spacer(1, 6 * mm))
    story.append(P("Wat je moet weten over een breadboard", "h2"))
    story += steps([
        "De gaatjes in een <b>rij met hetzelfde nummer</b> zijn met elkaar verbonden: <b>a–b–c–d–e</b> samen, en <b>f–g–h–i–j</b> samen.",
        "De <b>middengleuf</b> scheidt die twee helften: a–e is <b>niet</b> verbonden met f–j.",
        "De lange <b>rails</b> aan de zijkant (rode lijn + en blauwe lijn −) zijn <b>over de hele lengte</b> verbonden.",
        "Steek draadjes en pootjes er <b>recht en stevig</b> in, tot ze niet meer verder gaan.",
    ])
    story.append(Spacer(1, 4 * mm))
    story.append(P("Pinnen die we gebruiken", "h2"))
    story.append(P("Alle draden naar de ESP32 vertrekken uit de <b>vrije kolom j van breadboard 1</b>, naast de rechterrij pinnen:"))
    story.append(Spacer(1, 2 * mm))
    story.append(table([
        ["Gaatje bb1", "Pin", "Waarvoor"],
        ["j2", "VIN", "5V naar de rode rail"], ["j3", "GND", "GND naar de blauwe rail"],
        ["j4 / j6 / j11", "D13 / D14 / D32", "RGB-led rood / groen / blauw"], ["j5", "D12", "zoemer (via transistor)"],
        ["j7", "D27", "ultrasone sensor Echo (via spanningsdeler)"], ["j8", "D26", "ultrasone sensor Trig"],
        ["j9", "D25", "rode led"], ["j10", "D33", "blauwe led"],
        ["j12", "D35", "IR-ontvanger (via 1 kΩ)"], ["j13", "D34", "bewegingssensor (PIR)"],
    ], [32, 40, 104]))
    story.append(Spacer(1, 4 * mm))
    story.append(P("Weerstanden herkennen", "h2"))
    story.append(P("De weerstanden zitten op <b>papieren strookjes</b> waarop de waarde staat. Haal ze er pas af als je ze nodig hebt. "
                   "Zonder strookje? Gebruik de kleurringen:"))
    story.append(Spacer(1, 2 * mm))
    story.append(table([
        ["Waarde", "Kleuren (5 ringen)", "Aantal nodig"],
        ["220 Ω", "rood – rood – zwart – zwart – bruin", "5"],
        ["1 kΩ", "bruin – zwart – zwart – bruin – bruin", "3"],
        ["2 kΩ", "rood – zwart – zwart – bruin – bruin", "1"],
    ], [30, 100, 46]))
    story.append(PageBreak())

    # Stap 1
    story.append(P("Stap 1 – Bord aansluiten en programmeren", "h1"))
    story.append(P("Nodig: <b>ESP32-bord</b>, <b>USB-C-kabel</b>, <b>breadboard 1</b>."))
    story += steps([
        "Steek het ESP32-bord <b>nog niet</b> in een breadboard. Steek het eerst gewoon met de USB-C-kabel in je <b>pc</b>.",
        "Op het bord gaat een <b>rood lampje</b> branden.",
        "Upload de firmware en de webpagina: <b>pio run -t upload</b> en daarna <b>pio run -t uploadfs</b> (zie README). Dat duurt ±1 minuut.",
        "Open de seriële monitor (<b>pio device monitor</b>): je ziet \"Kameralarm start\" en het IP-adres. Daarna: <b>USB-kabel eruit</b>.",
        "Draai het bord zodat de <b>USB-C-aansluiting naar boven</b> wijst. Links staan nu 3V3 … D23, rechts VIN … EN.",
        "Zet de <b>linkerpinnen in kolom a</b> (3V3 in <b>a2</b>) en de <b>rechterpinnen in kolom i</b> (VIN in <b>i2</b>). Kolom j blijft vrij.",
        "Druk het <b>gelijkmatig</b> aan, met twee duimen op de zwarte randen (<b>niet</b> op het metalen kapje). Dat vraagt wat kracht.",
    ])
    story.append(Spacer(1, 3 * mm))
    story.append(Esp32Board())
    story.append(Spacer(1, 2 * mm))
    story.append(warn([
        "Kijk of <b>kolom j naast de rechterpinnen vrij</b> is. Daar komen alle draden naar de ESP32.",
        "Staat er een pin scheef of naast een gaatje? Niet forceren: haal het bord eruit en probeer opnieuw.",
    ]))
    story.append(Spacer(1, 3 * mm))
    story.append(tip(["Op een ander bord kunnen de pinnen in een andere volgorde staan. Lees altijd de <b>namen op je eigen bord</b>, "
                      "en pas zo nodig de pinnummers aan in <b>include/config.h</b>."], title="Ander bord?"))
    story.append(PageBreak())

    # Stap 2
    story.append(P("Stap 2 – Voeding naar breadboard 2", "h1"))
    story.append(P("Nodig: <b>breadboard 2</b> en <b>4 draadjes</b> (bij voorkeur 2 rode en 2 zwarte of blauwe)."))
    story.append(P("Leg breadboard 2 <b>rechts</b> naast breadboard 1. Houd het <b>rechtop</b>, met rij 1 boven, zoals op de tekening. "
                   "Alle onderdelen komen op breadboard 2; breadboard 1 draagt alleen de ESP32."))
    story.append(Spacer(1, 2 * mm))
    story.append(diagram(2, "Gekleurd = deze stap. Lichtgrijs = eerdere stappen. Een draad die naar links verdwijnt, gaat naar de pin met die naam op de ESP32."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "<b>Rood draadje:</b> van <b>j2</b> van breadboard 1 (naast <b>VIN</b>) naar de <b>linker rode rail (+)</b> van breadboard 2.",
        "<b>Zwart draadje:</b> van <b>j3</b> van breadboard 1 (naast <b>GND</b>) naar de <b>linker blauwe rail (−)</b> van breadboard 2.",
        "Onderaan breadboard 2: <b>rood draadje</b> van de linker rode rail (+) naar de <b>rechter rode rail (+)</b>.",
        "Onderaan: <b>zwart draadje</b> van de linker blauwe rail (−) naar de <b>rechter blauwe rail (−)</b>.",
    ])
    story.append(warn([
        "Controleer twee keer dat <b>rood alleen op rood (+)</b> en <b>zwart alleen op blauw (−)</b> zit.",
        "Op sommige breadboards zitten de rode en de blauwe lijn aan de andere kant. <b>Volg altijd de gekleurde lijn</b> op je eigen breadboard, niet de tekening.",
    ]))
    story.append(ok(["Alles nagekeken? USB erin: het rode lampje brandt en er wordt <b>niets warm</b>."]))
    story.append(PageBreak())

    # Stap 3
    story.append(P("Stap 3 – Rode en blauwe led (politielichten)", "h1"))
    story.append(P("Nodig: <b>1 rode led</b>, <b>1 blauwe led</b>, <b>2 × 220 Ω</b>, <b>4 draadjes</b>."))
    story.append(diagram(3, "De weerstanden liggen óver de middengleuf: van kolom e naar kolom f in dezelfde rij."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "<b>Rode led:</b> weerstand 220 Ω van <b>e22</b> naar <b>f22</b>. Lange poot (+) van de rode led in <b>h22</b>, korte poot in <b>h23</b>.",
        "Draadje van <b>j23</b> naar de <b>rechter blauwe rail (−)</b>.",
        "Draadje van <b>b22</b> naar <b>j9</b> van breadboard 1 (D25).",
        "<b>Blauwe led:</b> weerstand 220 Ω van <b>e25</b> naar <b>f25</b>. Lange poot in <b>h25</b>, korte poot in <b>h26</b>.",
        "Draadje van <b>j26</b> naar de rechter blauwe rail (−). Draadje van <b>b25</b> naar <b>j10</b> van breadboard 1 (D33).",
    ])
    story.append(tip(["<b>Lange poot = +</b>. Zijn de pootjes even lang? Kijk dan in het ledje: het <b>kleine</b> metalen stukje is +. "
                      "De rand van de led is ook afgeplat aan de kant van de korte poot (−)."], title="Welke poot is +?"))
    story.append(ok(["Typ in de seriële monitor <b>t leds</b>: rood en blauw knipperen om en om."]))
    story.append(PageBreak())

    # Stap 4
    story.append(P("Stap 4 – RGB-led (kleurenwiel)", "h1"))
    story.append(P("Nodig: <b>RGB-led</b> (doorzichtig, 4 pootjes), <b>3 × 220 Ω</b>, <b>4 draadjes</b>."))
    story.append(diagram(4, "De RGB-led staat met zijn 4 pootjes in h17, h18, h19 en h20. De langste poot (GND) zit in h18."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "Bekijk de RGB-led: <b>de langste poot is GND</b>. Houd de led zo dat er <b>één poot boven</b> de lange poot zit en twee eronder.",
        "Pootjes in <b>h17 (R)</b>, <b>h18 (lange poot = GND)</b>, <b>h19 (G)</b>, <b>h20 (B)</b>.",
        "Draadje van <b>j18</b> naar de rechter blauwe rail (−).",
        "Drie weerstanden van 220 Ω: <b>e17–f17</b>, <b>e19–f19</b>, <b>e20–f20</b>. Laat ze elkaar niet raken: buig ze een klein beetje uit elkaar.",
        "Draadjes naar breadboard 1: <b>b17 → j4</b> (D13), <b>b19 → j6</b> (D14), <b>b20 → j11</b> (D32).",
    ])
    story.append(ok(["Typ in de seriële monitor <b>t rgb</b>: rood → groen → blauw, daarna een kleurenwiel.",
                     "Brandt de led helemaal niet? Dan heeft je led een gemeenschappelijke anode: lange poot naar 3V3 en "
                     "<b>RGB_COMMON_ANODE = true</b> in include/config.h.",
                     "Kloppen de kleuren niet? Wissel de draden naar D13/D14/D32 om."]))
    story.append(PageBreak())

    # Stap 5
    story.append(P("Stap 5 – Zoemer met transistor", "h1"))
    story.append(P("Nodig: <b>actieve zoemer</b> (die <b>met de sticker</b> bovenop), <b>transistor PN2222</b>, <b>1 × 1 kΩ</b>, <b>4 draadjes</b>."))
    story.append(diagram(5, "De transistor staat in g3, g4, g5 met de PLATTE kant naar rechts (naar kolom j). De zoemer staat in j10 (−) en j13 (+)."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "<b>Transistor:</b> lees de tekst op de platte kant (PN2222). Zet hem met de <b>platte kant naar rechts</b>: pootjes in <b>g3, g4, g5</b>.",
        "Weerstand <b>1 kΩ</b> van <b>f4</b> naar <b>f7</b>.",
        "Draadje van <b>g7</b> naar <b>j5</b> van breadboard 1 (D12).",
        "Draadje van <b>j5</b> naar de rechter blauwe rail (−).",
        "Draadje van <b>h3</b> naar <b>g10</b>.",
        "<b>Zoemer</b> (sticker er nog op laten): de poot met <b>+</b> (de langere) in <b>j13</b>, de andere in <b>j10</b>. "
        "Is de afstand tussen de pootjes anders, stuur dan een foto.",
        "Draadje van <b>g13</b> naar de <b>rechter rode rail (+)</b>.",
    ])
    story.append(tip(["Er zijn twee zoemers. De <b>actieve</b> heeft een <b>sticker</b> en een <b>dichte zwarte onderkant</b>. "
                      "De passieve heeft een <b>groen printplaatje</b> aan de onderkant. Gebruik de actieve."], title="Welke zoemer?"))
    story.append(ok(["Typ in de seriële monitor <b>t buzzer</b>: 3 piepjes."]))
    story.append(PageBreak())

    # Stap 6
    story.append(P("Stap 6 – Ultrasone sensor (de tripwire)", "h1"))
    story.append(P("Nodig: <b>ultrasone sensor</b> (twee \"oogjes\"), <b>4 female-male draden</b> (één kant een gaatje, andere kant een pin), "
                   "<b>1 × 1 kΩ</b>, <b>1 × 2 kΩ</b>, <b>4 draadjes</b>."))
    story.append(diagram(6, "Groene bolletjes = het pin-uiteinde van een female-male draad die naar de sensor gaat. De sensor zelf staat dus NIET op het breadboard."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "Op de sensor staan 4 pinnen: <b>VCC, Trig, Echo, GND</b>. Steek op elke pin het <b>gaatje-uiteinde</b> van een female-male draad.",
        "De andere uiteinden: <b>VCC → a1</b>, <b>Trig → a2</b>, <b>Echo → a3</b>, <b>GND → a4</b>. Kijk goed naar de namen op de sensor.",
        "Draadje <b>b1 → linker rode rail (+)</b>. Draadje <b>b4 → linker blauwe rail (−)</b>.",
        "Draadje <b>b2 → j8</b> van breadboard 1 (D26).",
        "<b>Spanningsdeler:</b> weerstand <b>1 kΩ</b> van <b>c3</b> naar <b>c6</b>. Weerstand <b>2 kΩ</b> van <b>a6</b> naar de <b>linker blauwe rail (−)</b>.",
        "Draadje <b>b6 → j7</b> van breadboard 1 (D27).",
    ])
    story.append(warn([
        "De sensor geeft op <b>Echo</b> 5 volt. Daarom gaat Echo <b>nooit rechtstreeks</b> naar de ESP32, maar via de 1 kΩ en de 2 kΩ. "
        "Zo komt er maar 3,3V op D27. <b>Controleer dit extra goed op je foto.</b>",
        "Verwissel de 1 kΩ en de 2 kΩ niet: <b>1 kΩ</b> zit tussen Echo en D27, <b>2 kΩ</b> tussen D27 en GND.",
    ], title="BELANGRIJKSTE STAP"))
    story.append(ok(["Typ in de seriële monitor <b>t sonar</b>: houd je hand op 20 cm en op 50 cm. De afstand op het scherm klopt ongeveer."]))
    story.append(PageBreak())

    # Stap 7
    story.append(P("Stap 7 – Bewegingssensor (PIR)", "h1"))
    story.append(P("Nodig: <b>HC-SR501</b> (witte koepel), <b>3 female-male draden</b>, <b>3 draadjes</b>."))
    story.append(diagram(7, "De PIR hangt aan 3 female-male draden: VCC → a8, OUT → a9, GND → a10."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "Trek het witte koepeltje er voorzichtig af (het klikt los). Eronder staan de namen van de 3 pinnen: <b>VCC, OUT, GND</b>. Zet het koepeltje terug.",
        "Female-male draden: <b>VCC → a8</b>, <b>OUT → a9</b>, <b>GND → a10</b>.",
        "Draadje <b>b8 → linker rode rail (+)</b>. Draadje <b>b10 → linker blauwe rail (−)</b>. Draadje <b>b9 → j13</b> van breadboard 1 (D34).",
        "Draai met een klein schroevendraaiertje (of je nagel) de oranje knopjes: <b>\"Time\" helemaal naar links</b> (tegen de klok in), "
        "<b>\"Sensitivity\" in het midden</b>.",
    ])
    story.append(tip(["Na het insteken heeft de PIR <b>±60 seconden</b> nodig om op te warmen. In die tijd geeft hij soms vals signaal. Dat is normaal."]))
    story.append(ok(["Typ in de seriële monitor <b>t pir</b>: na een minuut zie je \"BEWEGING\" als je zwaait en \"rust\" als je stilzit."]))
    story.append(PageBreak())

    # Stap 8
    story.append(P("Stap 8 – IR-ontvanger (afstandsbediening)", "h1"))
    story.append(P("Nodig: <b>IR Receiver Module</b> (zwart plaatje met een bolletje, <b>niet</b> de IR Emission), "
                   "<b>3 female-male draden</b>, <b>3 draadjes</b>, de afstandsbediening."))
    story.append(diagram(8, "De IR-ontvanger krijgt 5V; het signaal gaat via een weerstand van 1 kΩ naar D35."))
    story += steps([
        "<b>USB-kabel eruit.</b>",
        "Op de module staan 3 pinnen. Bij de ELEGOO-module heten ze <b>Y</b> (signaal), <b>R</b> (+) en <b>G</b> (−); "
        "bij andere modules <b>S</b>, <b>+</b> en <b>−</b>. Lees ze goed.",
        "Female-male draden: <b>Y/S → a12</b>, <b>R/+ → a13</b>, <b>G/− → a14</b>.",
        "Draadje <b>b13 → linker rode rail (+)</b>. Draadje <b>b14 → linker blauwe rail (−)</b>.",
        "Weerstand <b>1 kΩ</b> van <b>c12</b> naar <b>c16</b>. <b>Geen</b> weerstand naar − (de uitgang van de ontvanger is te zwak voor een spanningsdeler).",
        "Draadje <b>b16 → j12</b> van breadboard 1 (D35).",
        "Trek het plastic lipje uit de afstandsbediening (dat zit tussen de batterij).",
    ])
    story.append(warn(["De 1 kΩ in serie is verplicht: hij beperkt de stroom naar D35 tot een veilig minimum. "
                       "Sluit het signaal <b>nooit</b> rechtstreeks aan op de ESP32."]))
    story.append(ok(["Typ in de seriële monitor <b>t ir</b>: elke knop van de afstandsbediening geeft een code op het scherm."]))
    story.append(PageBreak())

    # Stap 9
    story.append(P("Stap 9 – Alles samen, webpagina en plaatsen", "h1"))
    story.append(diagram(8, "Zo ziet breadboard 2 er helemaal af uit (alle stappen samen).", all_active=True))
    story += steps([
        "Typ in de seriële monitor <b>t alarm</b>: 5 seconden politielichten, kleurenwiel en zoemer.",
        "Open op je gsm <b>http://kameralarm.local</b> (of het IP-adres uit de seriële monitor). Je gsm moet op je wifi zitten.",
        "Gebruik de pincode uit <b>include/secrets.h</b> (WEB_PIN). Tik op <b>Geluid inschakelen</b> en upload je mp3.",
        "<b>Extra → Testmelding</b>: je krijgt een melding in ntfy.",
        "Zet alles naast de deur op heuphoogte (±75–100 cm). Richt de ultrasone sensor <b>horizontaal dwars door de ingang</b> "
        "naar een vaste muur of kast, en de PIR schuin naar de deur (zie docs/plaatsing.md).",
        "Steek de USB-kabel in een <b>gsm-lader</b> in de stekkerdoos (niet in de pc).",
        "Druk op <b>POWER</b> op de afstandsbediening, verlaat de kamer binnen 30 s, en kom terug binnen: het vooralarm start. "
        "Druk op <b>POWER</b> om uit te zetten.",
    ])
    story.append(Spacer(1, 3 * mm))
    story.append(P("Overzicht van alle verbindingen", "h2"))
    story.append(table([
        ["ESP32-pin (bb1)", "Gaat naar (bb2)", "Onderdeel"],
        ["VIN (j2)", "linker rode rail (+)", "voeding 5V"],
        ["GND (j3)", "linker blauwe rail (−)", "voeding GND"],
        ["D25 (j9)", "b22", "rode led"],
        ["D33 (j10)", "b25", "blauwe led"],
        ["D13 / D14 / D32 (j4 / j6 / j11)", "b17 / b19 / b20", "RGB-led"],
        ["D12 (j5)", "g7", "zoemer (via transistor)"],
        ["D26 (j8)", "b2", "ultrasone sensor Trig"],
        ["D27 (j7)", "b6", "ultrasone sensor Echo (via spanningsdeler)"],
        ["D34 (j13)", "b9", "PIR"],
        ["D35 (j12)", "b16", "IR-ontvanger signaal (via 1 kΩ)"],
    ], [52, 44, 80]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Arial", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(17 * mm, 10 * mm, "Kameralarm – bouwgids")
        canvas.drawRightString(193 * mm, 10 * mm, f"pagina {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(str(OUT), pagesize=A4, leftMargin=17 * mm, rightMargin=17 * mm,
                            topMargin=14 * mm, bottomMargin=16 * mm, title="Kameralarm – bouwgids",
                            author="yassir222736")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print("Gemaakt:", OUT)


if __name__ == "__main__":
    build()
