"""Tekent een bouwstap zoals de breadboards bij de gebruiker liggen:
dwars, rij 1 rechts, rij 30 links, breadboard 1 (ESP32) boven breadboard 2.

Gebruik: python tools/teken_stap.py 3   -> docs/img/stapN.png
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
F = "C:/Windows/Fonts/arial.ttf"
FB = "C:/Windows/Fonts/arialbd.ttf"

P = 52                      # afstand tussen gaatjes
X0 = 120                    # x van rij 30
W = X0 + 30 * P + 260
RED, BLUE, INK, MUTED = (214, 40, 40), (29, 78, 216), (31, 36, 48), (110, 118, 135)
YEL, BWIRE, ORANGE = (234, 179, 8), (37, 99, 235), (234, 122, 0)
BOARD, HOLE, GAP = (246, 244, 238), (150, 143, 125), (226, 221, 207)


def font(size, bold=False):
    return ImageFont.truetype(FB if bold else F, size)


def x(row):
    return X0 + (30 - row) * P + P // 2


# y-posities
Y = {}
y = 110
Y["b1_j"] = y + 40                 # kolom j van breadboard 1
Y["b1_rp"] = Y["b1_j"] + 70        # rails onder breadboard 1 (niet gebruiken)
Y["b1_rm"] = Y["b1_rp"] + P
y2 = Y["b1_rm"] + 150              # begin breadboard 2
Y["Tp"], Y["Tm"] = y2, y2 + P      # bovenste rails: + buiten, - binnen
for i, c in enumerate("abcde"):
    Y[c] = y2 + 2 * P + 30 + i * P
for i, c in enumerate("fghij"):
    Y[c] = Y["e"] + 2 * P + 10 + i * P
Y["Bp"], Y["Bm"] = Y["j"] + P + 30, Y["j"] + 2 * P + 30   # onderste rails: + binnen, - buiten
H = Y["Bm"] + 260


def board(d):
    # breadboard 1 (alleen onderrand)
    d.rounded_rectangle([X0 - 30, Y["b1_j"] - 60, X0 + 30 * P + 30, Y["b1_rm"] + 35], 14, fill=BOARD, outline=(200, 194, 176), width=2)
    d.text((X0 - 20, Y["b1_j"] - 55), "BREADBOARD 1  (met de ESP32)", font=font(22, True), fill=MUTED)
    d.rectangle([X0 - 30, Y["b1_j"] - 35, X0 + 30 * P + 30, Y["b1_j"] - 22], fill=(31, 41, 55))
    d.text((X0 + 30 * P - 330, Y["b1_j"] - 37), "ESP32-bord ligt hierboven", font=font(14), fill=(255, 255, 255))
    for r in range(1, 31):
        hole(d, x(r), Y["b1_j"])
        for k in ("b1_rp", "b1_rm"):
            hole(d, x(r), Y[k], (205, 200, 188))
    d.text((X0 - 70, Y["b1_j"] - 12), "j", font=font(24, True), fill=INK)
    d.line([X0, Y["b1_rp"] - 22, X0 + 30 * P, Y["b1_rp"] - 22], fill=(235, 160, 160), width=3)
    d.line([X0, Y["b1_rm"] + 22, X0 + 30 * P, Y["b1_rm"] + 22], fill=(160, 180, 235), width=3)
    d.text((X0 + 30 * P + 40, Y["b1_rp"] + 5), "rails van bb1:\nNIET gebruiken", font=font(18), fill=MUTED)
    labels = {2: "VIN", 3: "GND", 4: "D13", 5: "D12", 6: "D14", 7: "D27", 8: "D26", 9: "D25", 10: "D33", 11: "D32", 12: "D35", 13: "D34"}
    for r, n in labels.items():
        d.text((x(r), Y["b1_j"] + 32), n, font=font(16, True), fill=(21, 128, 61), anchor="mm")

    # breadboard 2
    d.rounded_rectangle([X0 - 30, Y["Tp"] - 45, X0 + 30 * P + 30, Y["Bm"] + 45], 14, fill=BOARD, outline=(200, 194, 176), width=2)
    d.rectangle([X0 - 30, Y["e"] + P // 2 + 8, X0 + 30 * P + 30, Y["f"] - P // 2 - 8], fill=GAP)
    d.text((X0 + 30 * P // 2, (Y["e"] + Y["f"]) // 2), "middengleuf", font=font(16), fill=MUTED, anchor="mm")
    d.line([X0, Y["Tp"] - 25, X0 + 30 * P, Y["Tp"] - 25], fill=RED, width=4)
    d.line([X0, Y["Tm"] + 25, X0 + 30 * P, Y["Tm"] + 25], fill=BLUE, width=4)
    d.line([X0, Y["Bp"] - 25, X0 + 30 * P, Y["Bp"] - 25], fill=RED, width=4)
    d.line([X0, Y["Bm"] + 25, X0 + 30 * P, Y["Bm"] + 25], fill=BLUE, width=4)
    for k, lab, colr in (("Tp", "+", RED), ("Tm", "−", BLUE), ("Bp", "+", RED), ("Bm", "−", BLUE)):
        d.text((X0 - 60, Y[k]), lab, font=font(34, True), fill=colr, anchor="mm")
        d.text((X0 + 30 * P + 60, Y[k]), lab, font=font(34, True), fill=colr, anchor="mm")
    for c in "abcdefghij":
        d.text((X0 - 60, Y[c]), c, font=font(24, True), fill=INK, anchor="mm")
        d.text((X0 + 30 * P + 60, Y[c]), c, font=font(24, True), fill=INK, anchor="mm")
    for r in range(1, 31):
        d.text((x(r), Y["a"] - P + 4), str(r), font=font(17), fill=MUTED, anchor="mm")
        d.text((x(r), Y["j"] + P - 12), str(r), font=font(17), fill=MUTED, anchor="mm")
        for k in ("Tp", "Tm", "Bp", "Bm") + tuple("abcdefghij"):
            hole(d, x(r), Y[k])
    d.text((X0 - 20, Y["Bm"] + 55), "BREADBOARD 2", font=font(22, True), fill=MUTED)


def hole(d, cx, cy, colr=HOLE):
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=colr)


def dot(d, cx, cy, colr):
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=colr, outline=(255, 255, 255), width=2)


def wire(d, p1, p2, colr, bend=0):
    (x1, y1), (x2, y2) = p1, p2
    pts = [(x1, y1), (x1 + (x2 - x1) * 0.15 + bend, y1 + (y2 - y1) * 0.5), (x2, y2)]
    # zachte curve via kwadratische bezier
    curve = []
    for t in [i / 30 for i in range(31)]:
        cx = (1 - t) ** 2 * pts[0][0] + 2 * (1 - t) * t * pts[1][0] + t ** 2 * pts[2][0]
        cy = (1 - t) ** 2 * pts[0][1] + 2 * (1 - t) * t * pts[1][1] + t ** 2 * pts[2][1]
        curve.append((cx, cy))
    d.line(curve, fill=(255, 255, 255), width=14)
    d.line(curve, fill=colr, width=8)
    dot(d, x1, y1, colr)
    dot(d, x2, y2, colr)


def resistor(d, row, c1, c2):
    x1, y1, y2 = x(row), Y[c1], Y[c2]
    d.line([x1, y1, x1, y2], fill=(120, 120, 120), width=4)
    my = (y1 + y2) // 2
    d.rounded_rectangle([x1 - 14, my - 38, x1 + 14, my + 38], 8, fill=(140, 190, 240), outline=INK, width=2)
    for k, colr in enumerate([(200, 30, 30), (200, 30, 30), (20, 20, 20), (20, 20, 20)]):
        d.rectangle([x1 - 14, my - 28 + k * 12, x1 + 14, my - 22 + k * 12], fill=colr)
    dot(d, x1, y1, (120, 120, 120))
    dot(d, x1, y2, (120, 120, 120))
    return x1, my


def led(d, row_long, colr, name):
    xl, xs, yy = x(row_long), x(row_long + 1), Y["h"]
    cx, cy = (xl + xs) // 2, yy + 75
    d.line([xl, yy, xl, cy - 10], fill=(150, 150, 150), width=4)
    d.line([xs, yy, xs, cy - 10], fill=(150, 150, 150), width=4)
    d.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], fill=colr, outline=INK, width=2)
    dot(d, xl, yy, (150, 150, 150))
    dot(d, xs, yy, (150, 150, 150))
    d.text((xl, yy - 26), "+", font=font(26, True), fill=RED, anchor="mm")
    d.text((xs, yy - 26), "−", font=font(26, True), fill=BLUE, anchor="mm")


def callout(d, n, cx, cy):
    d.ellipse([cx - 19, cy - 19, cx + 19, cy + 19], fill=INK)
    d.text((cx, cy), str(n), font=font(22, True), fill=(255, 255, 255), anchor="mm")


def stap3():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    board(d)
    for row, colr, name, j_row, pin in ((22, (230, 40, 40), "rood", 9, "D25"), (25, (40, 90, 230), "blauw", 10, "D33")):
        rx, ry = resistor(d, row, "e", "f")
        led(d, row, colr, name)
        wire(d, (x(row + 1), Y["j"]), (x(row + 1) - 18, Y["Bm"]), BWIRE)
        wire(d, (x(row), Y["b"]), (x(j_row), Y["b1_j"]), YEL, bend=-40)
    # nummers
    for n, (cx, cy) in enumerate([
        (x(22) + 45, (Y["e"] + Y["f"]) // 2), (x(22) + 60, Y["h"] + 80), (x(23) - 60, Y["Bm"] - 10), (x(22) + 40, Y["b"] - 50),
        (x(25) + 45, (Y["e"] + Y["f"]) // 2), (x(25) + 60, Y["h"] + 80), (x(26) - 60, Y["Bm"] - 10), (x(25) + 40, Y["b"] - 50),
    ], 1):
        callout(d, n, cx, cy)
    leg = [
        "1  Weerstand 220 Ω van e22 naar f22 (over de middengleuf)",
        "2  Rode led: lange poot (+) h22, korte poot (−) h23",
        "3  Blauw draadje: j23 → onderste blauwe rail (−)",
        "4  Geel draadje: b22 → j9 van breadboard 1 (D25)",
        "5  Weerstand 220 Ω van e25 naar f25",
        "6  Blauwe led: lange poot (+) h25, korte poot (−) h26",
        "7  Blauw draadje: j26 → onderste blauwe rail (−)",
        "8  Geel draadje: b25 → j10 van breadboard 1 (D33)",
    ]
    yy = Y["Bm"] + 95
    for k, t in enumerate(leg):
        d.text((X0 + (k // 4) * 800, yy + (k % 4) * 34), t, font=font(21, k % 4 in (0, 1) and False), fill=INK)
    d.text((X0, 22), "STAP 3 – rode en blauwe led   (breadboards liggend: rij 1 rechts)", font=font(30, True), fill=INK)
    return img


def ghost_stap3(d):
    """Onderdelen uit stap 3 lichtgrijs tekenen (zitten er al)."""
    g = (200, 200, 200)
    for row in (22, 25):
        d.line([x(row), Y["e"], x(row), Y["f"]], fill=g, width=6)
        d.ellipse([x(row + 1) - 12, Y["h"] + 30, x(row) + 12, Y["h"] + 75], fill=(225, 225, 225))
        d.line([x(row + 1), Y["j"], x(row + 1) - 18, Y["Bm"]], fill=g, width=5)
        d.line([x(row), Y["b"], x(9 if row == 22 else 10), Y["b1_j"]], fill=g, width=5)


def rgb(d, row_r):
    pts = [(x(row_r + k), Y["h"]) for k in range(4)]  # R, GND, G, B (naar links = hogere rij)
    cx = (pts[0][0] + pts[3][0]) // 2
    cy = Y["h"] + 85
    for (px, py) in pts:
        d.line([px, py, cx + (px - cx) // 3, cy - 20], fill=(150, 150, 150), width=4)
        dot(d, px, py, (150, 150, 150))
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(235, 235, 240), outline=INK, width=3)
    d.text((cx, cy), "RGB", font=font(18, True), fill=INK, anchor="mm")
    for (px, py), lab, colr in zip(pts, ["R", "GND", "G", "B"], [RED, INK, (21, 128, 61), BLUE]):
        d.text((px, py - 28), lab, font=font(20, True), fill=colr, anchor="mm")


def stap4():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    board(d)
    ghost_stap3(d)
    for row in (17, 19, 20):
        resistor(d, row, "e", "f")
    rgb(d, 17)
    wire(d, (x(18), Y["j"]), (x(18) + 18, Y["Bm"]), BWIRE)
    for row, j_row in ((17, 4), (19, 6), (20, 11)):
        wire(d, (x(row), Y["b"]), (x(j_row), Y["b1_j"]), YEL, bend=-30)
    for n, (cx, cy) in enumerate([
        (x(17) - 0, (Y["e"] + Y["f"]) // 2 + 60), (x(20) - 70, Y["h"] + 85), (x(18) + 70, Y["Bm"] - 10),
        (x(17) + 30, Y["b"] - 45), (x(19) - 30, Y["b"] - 45), (x(20) - 40, Y["b"] - 45),
    ], 1):
        callout(d, n, cx, cy)
    leg = [
        "1  Drie weerstanden 220 Ω over de middengleuf: e17–f17, e19–f19, e20–f20",
        "2  RGB-led: R in h17, lange poot (GND) in h18, G in h19, B in h20",
        "3  Blauw draadje: j18 → onderste blauwe rail (−)",
        "4  Geel draadje: b17 → j4 van breadboard 1 (D13)",
        "5  Geel draadje: b19 → j6 van breadboard 1 (D14)",
        "6  Geel draadje: b20 → j11 van breadboard 1 (D32)",
        "Grijs = zit er al (stap 3)",
    ]
    yy = Y["Bm"] + 95
    for k, t in enumerate(leg):
        d.text((X0 + (k // 4) * 900, yy + (k % 4) * 34), t, font=font(21), fill=MUTED if t.startswith("Grijs") else INK)
    d.text((X0, 22), "STAP 4 – RGB-led   (breadboards liggend: rij 1 rechts)", font=font(30, True), fill=INK)
    return img


if __name__ == "__main__":
    n = sys.argv[1] if len(sys.argv) > 1 else "3"
    out = ROOT / "docs" / "img" / f"stap{n}.png"
    globals()[f"stap{n}"]().save(out)
    print(out)
