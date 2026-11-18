"""The Daily Meridian - one-image summary of Tuesday 17 November 2026.

A program/v1 make.fun entry. Python 3 standard library only.
The program draws the whole newspaper page with its own rasteriser
and its own stroke font, then writes it as a PNG to the output dir.
Deterministic: no randomness, no clock, no file or network input.
Run twice and the two entry.png files are byte-identical.
"""
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (244, 238, 222)
PAPER2 = (236, 228, 205)
INK = (24, 22, 20)
GREY = (96, 92, 84)
RULE = (40, 38, 34)
RED = (178, 34, 28)
BLUE = (30, 74, 138)
SKY = (168, 200, 224)
SKY2 = (198, 220, 240)
SEA = (86, 138, 178)
SEA2 = (64, 112, 158)
SAND = (226, 205, 158)
GREEN = (62, 122, 62)
GREEN2 = (96, 152, 84)
BROWN = (128, 92, 56)
ORANGE = (224, 122, 36)
YELLOW = (244, 196, 48)
WHITE = (250, 250, 246)
BLACK = (16, 16, 16)
SMOKE = (110, 108, 104)
FIRE = (238, 120, 30)

REGION_COLOURS = {
    "AMERICAS": (30, 110, 170),
    "EUROPE": (122, 62, 160),
    "MIDDLE EAST": (196, 120, 20),
    "ASIA": (190, 44, 44),
    "AFRICA": (40, 140, 80),
    "OCEANIA": (20, 150, 160),
    "GLOBAL": (90, 90, 90),
}

# ---------------------------------------------------------------- png out
def png_bytes(px, w, h):
    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        c += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return c
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += px[y * stride:(y + 1) * stride]
    head = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", head)
    out += chunk(b"IDAT", zlib.compress(bytes(raw), 7))
    out += chunk(b"IEND", b"")
    return bytes(out)

# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, colour):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, colour)

    def set_px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = colour[0]
            self.px[i + 1] = colour[1]
            self.px[i + 2] = colour[2]

    def grain(self, x, y, colour, amp=5):
        n = ((x // 3) * 73856093) ^ ((y // 3) * 19349663)
        n = (n ^ (n >> 13)) & 7
        d = int(n) - 3
        return (max(0, min(255, colour[0] + d * amp // 3)),
                max(0, min(255, colour[1] + d * amp // 3)),
                max(0, min(255, colour[2] + d * amp // 3)))

    def fill_rect(self, x, y, w, h, colour, grain=False):
        x = int(x); y = int(y); w = int(w); h = int(h)
        for yy in range(y, y + h):
            if yy < 0 or yy >= self.h:
                continue
            base = (yy * self.w) * 3
            for xx in range(x, x + w):
                if xx < 0 or xx >= self.w:
                    continue
                c = self.grain(xx, yy, colour) if grain else colour
                i = base + xx * 3
                self.px[i] = c[0]; self.px[i + 1] = c[1]; self.px[i + 2] = c[2]

    def rect_outline(self, x, y, w, h, colour, t=1):
        self.fill_rect(x, y, w, t, colour)
        self.fill_rect(x, y + h - t, w, t, colour)
        self.fill_rect(x, y, t, h, colour)
        self.fill_rect(x + w - t, y, t, h, colour)

    def line(self, x1, y1, x2, y2, colour, t=1):
        x1 = float(x1); y1 = float(y1); x2 = float(x2); y2 = float(y2)
        steps = int(max(abs(x2 - x1), abs(y2 - y1))) + 1
        r = max(0, (t - 1) // 2)
        for s in range(steps + 1):
            f = s / steps if steps else 0
            cx = int(round(x1 + (x2 - x1) * f))
            cy = int(round(y1 + (y2 - y1) * f))
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if dx * dx + dy * dy <= r * r + 1:
                        self.set_px(cx + dx, cy + dy, colour)
            if t >= 2:
                self.set_px(cx, cy, colour)

    def dashed(self, x1, y1, x2, y2, colour, t=1, dash=6, gap=4):
        x1 = float(x1); y1 = float(y1); x2 = float(x2); y2 = float(y2)
        steps = int(max(abs(x2 - x1), abs(y2 - y1))) + 1
        for s in range(steps + 1):
            if (s % (dash + gap)) >= dash:
                continue
            f = s / steps if steps else 0
            self.set_px(int(round(x1 + (x2 - x1) * f)),
                        int(round(y1 + (y2 - y1) * f)), colour)
            if t >= 2:
                self.set_px(int(round(x1 + (x2 - x1) * f)) + 1,
                            int(round(y1 + (y2 - y1) * f)), colour)

    def circle(self, cx, cy, r, colour, fill=True, t=1):
        cx = int(cx); cy = int(cy); r = int(r)
        for yy in range(cy - r - 1, cy + r + 2):
            for xx in range(cx - r - 1, cx + r + 2):
                d2 = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if fill:
                    if d2 <= r * r:
                        self.set_px(xx, yy, colour)
                else:
                    if (r - t) * (r - t) <= d2 <= r * r:
                        self.set_px(xx, yy, colour)

    def poly(self, pts, colour, fill=True, t=1):
        if fill:
            ys = [p[1] for p in pts]
            for yy in range(int(min(ys)), int(max(ys)) + 1):
                nodes = []
                n = len(pts)
                for i in range(n):
                    x1, y1 = pts[i]
                    x2, y2 = pts[(i + 1) % n]
                    if (y1 <= yy < y2) or (y2 <= yy < y1):
                        nodes.append(x1 + (yy - y1) * (x2 - x1) / (y2 - y1))
                nodes.sort()
                for i in range(0, len(nodes) - 1, 2):
                    xa = int(round(nodes[i])); xb = int(round(nodes[i + 1]))
                    for xx in range(xa, xb + 1):
                        self.set_px(xx, yy, colour)
        else:
            n = len(pts)
            for i in range(n):
                self.line(pts[i][0], pts[i][1], pts[(i + 1) % n][0],
                          pts[(i + 1) % n][1], colour, t)

    def tri(self, a, b, c, colour):
        self.poly([a, b, c], colour, True)

# ---------------------------------------------------------------- font
# Own stroke font on a 4-wide, 6-high grid. Each glyph is a list of
# strokes; each stroke is a list of (x, y) points joined by lines.
# y grows downward, (0,0) is top-left, cap height is 6 units.
def _g(*strokes):
    return [list(s) for s in strokes]

GLYPHS = {
    "A": _g(((0, 6), (2, 0), (4, 6)), ((0.7, 4), (3.3, 4))),
    "B": _g(((0, 0), (0, 6)), ((0, 0), (2.5, 0), (3.5, 1), (3.5, 2), (2.5, 3), (0, 3)),
            ((2.5, 3), (3.8, 3.8), (3.8, 5), (2.5, 6), (0, 6))),
    "C": _g(((3.8, 1), (2.8, 0.2), (1.2, 0.2), (0.2, 1.2), (0.2, 4.8), (1.2, 5.8), (2.8, 5.8), (3.8, 5))),
    "D": _g(((0, 0), (0, 6)), ((0, 0), (2.2, 0), (3.8, 1.5), (3.8, 4.5), (2.2, 6), (0, 6))),
    "E": _g(((4, 0), (0, 0), (0, 6), (4, 6)), ((0, 3), (3.2, 3))),
    "F": _g(((4, 0), (0, 0), (0, 6)), ((0, 3), (3, 3))),
    "G": _g(((3.8, 1), (2.8, 0.2), (1.2, 0.2), (0.2, 1.2), (0.2, 4.8), (1.2, 5.8), (2.8, 5.8), (3.9, 5), (3.9, 3.4), (2.3, 3.4))),
    "H": _g(((0, 0), (0, 6)), ((4, 0), (4, 6)), ((0, 3), (4, 3))),
    "I": _g(((0.6, 0), (3.4, 0)), ((2, 0), (2, 6)), ((0.6, 6), (3.4, 6))),
    "J": _g(((3.6, 0), (3.6, 4.8), (2.6, 5.8), (1, 5.8), (0.2, 5))),
    "K": _g(((0, 0), (0, 6)), ((4, 0), (0.7, 2.8)), ((1.3, 3.4), (4, 6))),
    "L": _g(((0, 0), (0, 6), (4, 6))),
    "M": _g(((0, 6), (0, 0), (2, 3), (4, 0), (4, 6))),
    "N": _g(((0, 6), (0, 0), (4, 6), (4, 0))),
    "O": _g(((1.2, 0.2), (2.8, 0.2), (3.8, 1.2), (3.8, 4.8), (2.8, 5.8), (1.2, 5.8), (0.2, 4.8), (0.2, 1.2), (1.2, 0.2))),
    "P": _g(((0, 6), (0, 0)), ((0, 0), (2.8, 0), (3.8, 1), (3.8, 2.2), (2.8, 3.2), (0, 3.2))),
    "Q": _g(((1.2, 0.2), (2.8, 0.2), (3.8, 1.2), (3.8, 4.8), (2.8, 5.8), (1.2, 5.8), (0.2, 4.8), (0.2, 1.2), (1.2, 0.2)), ((2.4, 4.2), (4.1, 6.1))),
    "R": _g(((0, 6), (0, 0)), ((0, 0), (2.8, 0), (3.8, 1), (3.8, 2.2), (2.8, 3.2), (0, 3.2)), ((2, 3.2), (4, 6))),
    "S": _g(((3.8, 0.8), (2.8, 0.1), (1.2, 0.1), (0.3, 0.9), (0.3, 2), (1, 2.7), (3, 3.3), (3.8, 4), (3.8, 5.1), (2.8, 5.9), (1.2, 5.9), (0.2, 5.2))),
    "T": _g(((0, 0), (4, 0)), ((2, 0), (2, 6))),
    "U": _g(((0, 0), (0, 4.8), (1, 5.8), (3, 5.8), (4, 4.8), (4, 0))),
    "V": _g(((0, 0), (2, 6), (4, 0))),
    "W": _g(((0, 0), (1, 6), (2, 2.5), (3, 6), (4, 0))),
    "X": _g(((0, 0), (4, 6)), ((4, 0), (0, 6))),
    "Y": _g(((0, 0), (2, 2.8), (4, 0)), ((2, 2.8), (2, 6))),
    "Z": _g(((0, 0), (4, 0), (0, 6), (4, 6))),
    "0": _g(((1, 0.2), (3, 0.2), (3.8, 1), (3.8, 5), (3, 5.8), (1, 5.8), (0.2, 5), (0.2, 1), (1, 0.2))),
    "1": _g(((1.2, 1), (2.4, 0), (2.4, 6)), ((0.8, 6), (3.6, 6))),
    "2": _g(((0.3, 1), (1, 0.2), (3, 0.2), (3.8, 1), (3.8, 2.2), (0.2, 6), (4, 6))),
    "3": _g(((0.3, 0.5), (1.2, 0.1), (2.8, 0.1), (3.7, 0.9), (3.7, 2), (2.8, 2.9), (1.6, 3)),
            ((1.6, 3), (2.9, 3.1), (3.8, 3.9), (3.8, 5.1), (2.9, 5.9), (1.2, 5.9), (0.3, 5.4))),
    "4": _g(((2.8, 6), (2.8, 0), (0, 4), (4, 4))),
    "5": _g(((3.8, 0), (0.2, 0), (0.2, 2.6), (2.6, 2.4), (3.8, 3.2), (3.8, 5), (2.8, 5.9), (1, 5.9), (0.2, 5.2))),
    "6": _g(((3.6, 0.6), (2.6, 0.1), (1.2, 0.1), (0.3, 1), (0.3, 4.9), (1.2, 5.8), (2.8, 5.8), (3.8, 5), (3.8, 3.4), (2.9, 2.6), (1.2, 2.6), (0.3, 3.2))),
    "7": _g(((0.2, 0), (4, 0), (1.6, 6))),
    "8": _g(((1.3, 0.2), (2.7, 0.2), (3.4, 0.9), (3.4, 2.1), (2.7, 2.9), (1.3, 2.9), (0.6, 2.1), (0.6, 0.9), (1.3, 0.2)),
            ((1.1, 2.9), (2.9, 2.9), (3.8, 3.8), (3.8, 5), (2.9, 5.8), (1.1, 5.8), (0.2, 5), (0.2, 3.8), (1.1, 2.9))),
    "9": _g(((0.4, 5.4), (1.4, 5.9), (2.8, 5.9), (3.7, 5), (3.7, 1.1), (2.8, 0.2), (1.2, 0.2), (0.2, 1), (0.2, 2.6), (1.1, 3.4), (2.8, 3.4), (3.7, 2.8))),
    ".": _g(((2, 5.4), (2, 6))),
    ",": _g(((2.1, 5.2), (1.8, 6.3))),
    "'": _g(((2, 0), (2, 1.3))),
    '"': _g(((1.2, 0), (1.2, 1.3)), ((3, 0), (3, 1.3))),
    "-": _g(((0.6, 3), (3.4, 3))),
    ":": _g(((2, 1.2), (2, 1.8)), ((2, 4.4), (2, 5))),
    ";": _g(((2, 1.2), (2, 1.8)), ((2.1, 4.6), (1.8, 6.1))),
    "!": _g(((2, 0), (2, 4.2)), ((2, 5.4), (2, 6))),
    "?": _g(((0.4, 0.9), (1.2, 0.1), (2.8, 0.1), (3.7, 0.9), (3.7, 1.8), (2.8, 2.7), (2, 3.2), (2, 4.1)), ((2, 5.4), (2, 6))),
    "$": _g(((3.8, 0.8), (2.8, 0.1), (1.2, 0.1), (0.3, 0.9), (0.3, 2), (1, 2.7), (3, 3.3), (3.8, 4), (3.8, 5.1), (2.8, 5.9), (1.2, 5.9), (0.2, 5.2)), ((2, -0.3), (2, 6.3))),
    "%": _g(((0.4, 6), (3.6, 0)), ((1, 0.6), (1.7, 0.6), (1.7, 1.7), (1, 1.7), (1, 0.6)), ((2.6, 4.3), (3.3, 4.3), (3.3, 5.4), (2.6, 5.4), (2.6, 4.3))),
    "+": _g(((2, 1.5), (2, 4.5)), ((0.8, 3), (3.2, 3))),
    "/": _g(((0.5, 6), (3.5, 0))),
    "(": _g(((3.2, 0.2), (2, 0.8), (1.2, 2.4), (1.2, 3.6), (2, 5.2), (3.2, 5.8))),
    ")": _g(((0.8, 0.2), (2, 0.8), (2.8, 2.4), (2.8, 3.6), (2, 5.2), (0.8, 5.8))),
    "&": _g(((3.6, 5.8), (1.4, 3.4), (0.6, 2.4), (0.8, 0.7), (2, 0.1), (2.9, 0.8), (2.6, 2), (0.4, 4.4), (1.2, 5.8), (2.8, 5.8), (3.8, 4.6))),
    "*": _g(((2, 0.6), (2, 3.4)), ((0.7, 1.2), (3.3, 2.8)), ((3.3, 1.2), (0.7, 2.8))),
    "=": _g(((0.6, 2.2), (3.4, 2.2)), ((0.6, 3.8), (3.4, 3.8))),
    "€": _g(((3.8, 1), (2.8, 0.2), (1.2, 0.2), (0.2, 1.2), (0.2, 4.8), (1.2, 5.8), (2.8, 5.8), (3.8, 5)), ((0.2, 2.4), (2.8, 2.4)), ((0.2, 3.6), (2.8, 3.6))),
    "·": _g(((2, 2.8), (2, 3.4))),
    "—": _g(((0.2, 3), (3.8, 3))),
    "–": _g(((0.6, 3), (3.4, 3))),
}

def text_width(s, size, tracking=1.15):
    scale = size / 6.0
    adv = 4 * scale + tracking * scale
    return adv * len(s) - tracking * scale

def draw_text(cv, x, y, s, size, colour, t=1, tracking=1.15, align="l"):
    s = s.upper()
    scale = size / 6.0
    adv = 4 * scale + tracking * scale
    w = text_width(s, size, tracking)
    if align == "c":
        x = x - w / 2
    elif align == "r":
        x = x - w
    cx = x
    for ch in s:
        if ch == " ":
            cx += adv
            continue
        glyph = GLYPHS.get(ch)
        if glyph is None:
            cx += adv
            continue
        for stroke in glyph:
            pts = [(cx + px * scale, y + py * scale) for px, py in stroke]
            for i in range(len(pts) - 1):
                cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], colour, t)
            if len(pts) == 1:
                cv.set_px(int(pts[0][0]), int(pts[0][1]), colour)
        cx += adv
    return w

def wrap_text(s, size, max_w, tracking=1.15):
    words = s.upper().split()
    lines = []
    cur = ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_width(trial, size, tracking) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def draw_wrapped(cv, x, y, s, size, colour, max_w, t=1, leading=1.32,
                 tracking=1.15, max_lines=99):
    lines = wrap_text(s, size, max_w, tracking)[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * size * leading, ln, size, colour, t, tracking)
    return len(lines)

# ---------------------------------------------------------------- helpers
def chip(cv, x, y, num, colour, r=9):
    cv.circle(x + r, y + r, r, colour, True)
    s = str(num)
    tw = text_width(s, 10, 1.0)
    draw_text(cv, x + r - tw / 2, y + r - 5, s, 10, WHITE, 2, 1.0)

def person(cv, x, y, h, shirt, skin=(232, 190, 150), trousers=INK):
    head_r = max(2, int(h * 0.13))
    cv.circle(x, y + head_r, head_r, skin, True)
    top = y + head_r * 2
    cv.line(x, top, x, y + h * 0.62, shirt, max(2, int(h * 0.09)))
    cv.line(x, top + 3, x - h * 0.2, y + h * 0.42, shirt, 2)
    cv.line(x, top + 3, x + h * 0.2, y + h * 0.42, shirt, 2)
    cv.line(x, y + h * 0.62, x - h * 0.16, y + h, trousers, 2)
    cv.line(x, y + h * 0.62, x + h * 0.16, y + h, trousers, 2)

def flag_us(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, WHITE)
    for i in range(4):
        cv.fill_rect(x, y + i * h // 4 + (h // 8 if i else 0), w, max(1, h // 8), RED)
    cv.fill_rect(x, y, w * 0.45, h * 0.55, BLUE)
    for r in range(3):
        for c in range(4):
            cv.set_px(int(x + 3 + c * w * 0.1), int(y + 3 + r * h * 0.16), WHITE)
            cv.set_px(int(x + 4 + c * w * 0.1), int(y + 3 + r * h * 0.16), WHITE)
    cv.rect_outline(x, y, w, h, INK, 1)

def flag_in(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h // 3, ORANGE)
    cv.fill_rect(x, y + h // 3, w, h // 3, WHITE)
    cv.fill_rect(x, y + 2 * h // 3, w, h - 2 * h // 3, GREEN)
    cv.circle(x + w // 2, y + h // 2, max(2, h // 7), BLUE, False, 1)
    cv.rect_outline(x, y, w, h, INK, 1)

def flag_jp(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.circle(x + w // 2, y + h // 2, max(2, int(h * 0.28)), RED, True)
    cv.rect_outline(x, y, w, h, INK, 1)

def flag_au(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, BLUE)
    cv.line(x + 2, y + 2, x + w * 0.4, y + h * 0.4, WHITE, 2)
    cv.line(x + w * 0.4, y + 2, x + 2, y + h * 0.4, WHITE, 2)
    cv.line(x + 2, y + 2, x + w * 0.4, y + h * 0.4, RED, 1)
    for sx, sy in ((0.7, 0.3), (0.82, 0.62), (0.62, 0.78), (0.9, 0.85)):
        cv.set_px(int(x + w * sx), int(y + h * sy), WHITE)
        cv.set_px(int(x + w * sx) + 1, int(y + h * sy), WHITE)
    cv.rect_outline(x, y, w, h, INK, 1)

def cloud(cv, x, y, w, colour=SMOKE):
    cv.circle(x + w * 0.25, y, w * 0.18, colour, True)
    cv.circle(x + w * 0.5, y - 3, w * 0.24, colour, True)
    cv.circle(x + w * 0.75, y, w * 0.18, colour, True)
    cv.fill_rect(x + w * 0.1, y, w * 0.8, 6, colour)

def explosion(cv, cx, cy, r):
    import math
    for a in range(12):
        ang = a * 3.14159 / 6
        rr = r if a % 2 == 0 else r * 0.55
        cv.line(cx, cy, cx + rr * math.cos(ang),
                cy + rr * math.sin(ang), FIRE, 3)
    cv.circle(cx, cy, int(r * 0.32), YELLOW, True)
    cv.circle(cx, cy, int(r * 0.18), FIRE, True)

def header_block(cv, x, y, w, num, region, kicker, headline, hsize=11.5):
    colour = REGION_COLOURS.get(region, INK)
    chip(cv, x, y, num, colour, 8)
    draw_text(cv, x + 21, y + 1, region + " · " + kicker, 7.5, colour, 2)
    lines = wrap_text(headline, hsize, w - 2)
    for i, ln in enumerate(lines[:2]):
        draw_text(cv, x + 1, y + 13 + i * hsize * 1.25, ln, hsize, INK, 2)
    return y + 13 + min(2, len(lines)) * hsize * 1.25 + 3

# ---------------------------------------------------------------- data
FEATURES = [
    (4, "AFRICA", "HEALTH", "EBOLA CASES PASS 11,000 IN CONGO OUTBREAK",
     "CLINICS IN THE EAST ARE OVERWHELMED; WHO TEAMS RACE TO TRACE CONTACTS."),
    (5, "GLOBAL", "CLIMATE", "COP31 DRAFT DEAL TEARS APART ON FOSSIL TEXT",
     "NEGOTIATORS FIGHT OVER ONE PARAGRAPH AS THE SUMMIT NEARS ITS END."),
    (6, "AMERICAS", "HEALTH", "AMERICAS LOSE MEASLES-FREE STATUS AT LAST",
     "CASES IN THE US, MEXICO AND BOLIVIA END THE REGION'S ELIMINATION BADGE."),
    (7, "AMERICAS", "MARKETS", "NVIDIA'S $115.8BN QUARTER CANNOT SAVE DOW",
     "CHIP SALES DOUBLE, UP 103%, BUT THE DOW STILL FALLS 849 POINTS."),
    (8, "MIDDLE EAST", "AID", "AID TRUCKS HELD AGAIN AS RAIN FLOODS TENTS",
     "FAMILIES WAIT IN THE RAIN WHILE CONVOYS IDLE AT THE CROSSINGS."),
    (9, "ASIA", "POLITICS", "MONGOLIA'S PRESIDENT QUITS OVER COAL ROW",
     "RESIGNATION IN ULAANBAATAR AFTER WEEKS OF PARLIAMENT DEADLOCK."),
    (10, "EUROPE", "PROTEST", "STUDENTS FILL BELGRADE AS VOTE GOES 140-103",
     "PARLIAMENT BACKS THE GOVERNMENT, BUT STREET PROTESTS GROW LOUDER."),
    (11, "ASIA", "LABOUR", "GARMENT WORKERS MARCH FOR TK 30,000 WAGE",
     "TEAR GAS DRIFTS OVER A DHAKA RALLY FOR A HIGHER MINIMUM WAGE."),
    (12, "ASIA", "DISASTER", "AN-12 CARGO PLANE CRASHES IN SIBERIAN SNOW",
     "WRECK FOUND NEAR KEMEROVO; RESCUE TEAMS SEARCH THE FROZEN SITE."),
    (13, "AFRICA", "COURTS", "MONDLANE FACES COURT IN MAPUTO HEARING",
     "THE OPPOSITION LEADER'S CASE OPENS AS SUPPORTERS WAIT OUTSIDE."),
]

ONELINERS = [
    "EU OPENS MIGRANT RETURN HUBS PLAN TO A MEMBER STATE VOTE",
    "JPMORGAN RESTORES ITS APP AFTER A MORNING OUTAGE IN THE US",
    "VULCAN ROCKET LAUNCH SCRUBBED AGAIN AT CAPE CANAVERAL",
    "UKRAINE SEEKS MORE AIR DEFENCE AFTER A NIGHT OF DRONE WAVES",
    "OIL PRICES JUMP AS HORMUZ TANKER TRAFFIC SLOWS TO A CRAWL",
    "GOLD HOLDS NEAR A RECORD AS INVESTORS SEEK SAFETY IN SELLOFF",
    "FRANCE AND GERMANY AGREE A JOINT FUND FOR GRID STORAGE",
    "INDIA RAILWAYS ANNOUNCES 40 NEW OVERNIGHT ROUTES FOR WINTER",
    "JAPAN EXPORTS BEAT FORECASTS ON CHIP EQUIPMENT DEMAND",
    "BRAZIL FLOODS: RESCUE TEAMS REACH CUT-OFF TOWNS IN THE SOUTH",
    "CANADA WILDFIRE SMOKE DRIFTS OVER GREAT LAKES CITIES AGAIN",
    "AUSTRALIA BUSHFIRE WATCH RAISED FOR NEW SOUTH WALES HEAT",
    "SOUTH AFRICA POWER CUTS EASE AS TWO PLANTS RETURN TO GRID",
    "KENYA LAUNCHES A DROUGHT RELIEF APPEAL FOR NORTHERN COUNTIES",
    "TURKIYE CENTRAL BANK HOLDS RATES, SIGNALS CAUTION ON PRICES",
    "SOUTH KOREA SHIPBUILDERS WIN $2BN IN NEW GAS CARRIER ORDERS",
    "ARGENTINA HARVEST FORECAST IS CUT AFTER A DRY PAMPAS SPRING",
    "CHILE COPPER OUTPUT DIPS AS SMELTER MAINTENANCE DRAGS ON",
    "NORWAY SOVEREIGN FUND BACKS A NEW NORTH SEA WIND ZONE",
    "SPAIN RAIL STRIKE TALKS RESUME AFTER A DAY OF CANCELLATIONS",
    "ITALY MUSEUM WORKERS STRIKE OVER PAY IN ROME AND FLORENCE",
    "PAKISTAN AND THE IMF REACH A STAFF DEAL ON LOAN REVIEW",
    "INDONESIA VOLCANO ALERT RAISED; VILLAGES TOLD TO PREPARE",
    "PHILIPPINES FERRY ROUTES HALTED AS A STORM NEARS LUZON",
    "NEW ZEALAND RUGBY NAMES ITS SQUAD FOR THE YEAR-END TOUR",
    "CRICKET: DHONI CONFIRMS A FINAL IPL SEASON WITH CHENNAI",
    "FOOTBALL: CHAMPIONS LEAGUE RETURNS WITH A FULL MIDWEEK ROUND",
    "TENNIS: A TEEN QUALIFIER REACHES THE LAST EIGHT AT FINALS",
    "FILM FESTIVAL JURY PRIZE GOES TO A FIRST-TIME DIRECTOR TEAM",
    "STATION CREW RETURNS SAFELY AFTER A ROTATION IN ORBIT",
    "ARCTIC SEA ICE RECOVERS SLIGHTLY AFTER A RECORD LOW AUTUMN",
    "WHO BACKS A NEW MALARIA VACCINE ROLLOUT IN WEST AFRICA",
    "GLOBAL STOCKS CLOSE MIXED AS TECH OFFSETS FALLING BANKS",
]

# ---------------------------------------------------------------- scenes
def scene_kerch(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY2, True)
    sea_y = y + int(h * 0.52)
    cv.fill_rect(x, sea_y, w, h - (sea_y - y), SEA, True)
    for i in range(9):
        wx = x + 8 + i * (w // 8)
        cv.line(wx, sea_y + 10 + (i % 3) * 9, wx + 16, sea_y + 10 + (i % 3) * 9, SEA2, 2)
    # land masses
    cv.poly([(x, y), (x + w * 0.30, y), (x + w * 0.26, sea_y - 6), (x, sea_y + 8)], SAND, True)
    cv.poly([(x + w, y), (x + w * 0.74, y), (x + w * 0.78, sea_y - 4), (x + w, sea_y + 10)], GREEN2, True)
    draw_text(cv, x + 8, y + 6, "CRIMEA", 9, INK, 2)
    draw_text(cv, x + w - 62, y + 6, "RUSSIA", 9, INK, 2)
    # bridge deck: two standing parts and a fallen middle span
    deck_y = sea_y - 14
    cv.fill_rect(x + w * 0.08, deck_y, w * 0.30, 6, GREY)
    cv.fill_rect(x + w * 0.64, deck_y, w * 0.30, 6, GREY)
    cv.poly([(x + w * 0.40, deck_y + 4), (x + w * 0.60, deck_y + 4),
             (x + w * 0.64, sea_y + 16), (x + w * 0.46, sea_y + 18)], GREY, True)
    for px in (0.16, 0.30, 0.70, 0.84):
        cv.fill_rect(x + w * px, deck_y + 4, 5, sea_y - deck_y, BROWN)
    cv.line(x + w * 0.08, deck_y - 12, x + w * 0.38, deck_y, INK, 1)
    cv.line(x + w * 0.94, deck_y - 12, x + w * 0.64, deck_y, INK, 1)
    explosion(cv, x + w * 0.52, deck_y - 8, 25)
    cloud(cv, x + w * 0.58, deck_y - 30, 52, SMOKE)
    cloud(cv, x + w * 0.68, deck_y - 38, 40, (140, 138, 134))
    # splash and debris
    for dx in (-14, -4, 8, 18):
        cv.line(x + w * 0.52 + dx, sea_y + 14, x + w * 0.52 + dx - 3, sea_y + 2, WHITE, 2)
    draw_text(cv, x + 8, sea_y + h * 0.30, "KERCH STRAIT", 8, WHITE, 2)

def scene_gulf(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SEA2, True)
    # Arabia bottom-left, Iran top, gulf water between
    cv.poly([(x, y + h), (x, y + h * 0.52), (x + w * 0.30, y + h * 0.60),
             (x + w * 0.42, y + h), ], SAND, True)
    cv.poly([(x + w * 0.34, y), (x + w, y), (x + w, y + h * 0.30),
             (x + w * 0.62, y + h * 0.34), (x + w * 0.44, y + h * 0.16)], SAND, True)
    cv.poly([(x + w * 0.80, y + h), (x + w, y + h), (x + w, y + h * 0.62),
             (x + w * 0.90, y + h * 0.78)], GREEN2, True)
    draw_text(cv, x + w * 0.58, y + 6, "IRAN", 10, INK, 2)
    draw_text(cv, x + 8, y + h - 16, "ARABIA", 9, INK, 2)
    draw_text(cv, x + w - 58, y + h - 16, "HORMUZ", 8, WHITE, 2)
    # Qeshm island
    cv.poly([(x + w * 0.60, y + h * 0.36), (x + w * 0.74, y + h * 0.33),
             (x + w * 0.76, y + h * 0.42), (x + w * 0.62, y + h * 0.45)], YELLOW, True)
    draw_text(cv, x + w * 0.615, y + h * 0.365, "QESHM", 7, INK, 2)
    # Bahrain island + radar burst
    bx = x + w * 0.30; by = y + h * 0.42
    cv.circle(bx, by, 7, YELLOW, True)
    draw_text(cv, bx - 24, by + 12, "BAHRAIN", 7.5, WHITE, 2)
    import math
    for a in range(8):
        ang = a * 3.14159 / 4
        cv.line(bx, by, bx + 20 * math.cos(ang), by + 20 * math.sin(ang), YELLOW, 2)
    cv.circle(bx, by, 3, RED, True)
    # dashed strike arcs from Iran side toward Bahrain
    for off in (0, 10, 20):
        pts = []
        for s in range(21):
            f = s / 20
            px = x + w * 0.66 - (w * 0.36) * f
            py = y + h * 0.20 + (h * 0.22) * f - 14 * (1 - (2 * f - 1) ** 2) + off * 0.4
            pts.append((px, py))
        for i in range(0, len(pts) - 1, 2):
            cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 2)
    # drones
    for dx, dy in ((0.52, 0.16), (0.44, 0.26)):
        dxp = x + w * dx; dyp = y + h * dy
        cv.fill_rect(dxp - 7, dyp - 2, 14, 4, BLACK)
        cv.line(dxp - 10, dyp - 5, dxp + 10, dyp + 5, BLACK, 2)
        cv.line(dxp - 10, dyp + 5, dxp + 10, dyp - 5, BLACK, 2)
    cv.fill_rect(x + w * 0.06, y + 6, 104, 15, RED)
    draw_text(cv, x + w * 0.06 + 6, y + 9, "DRONES DOWNED", 8.5, WHITE, 2)

def scene_quad(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (214, 226, 236), True)
    cv.fill_rect(x, y, w, 26, BLUE)
    draw_text(cv, x + w / 2, y + 7, "QUAD SUMMIT · MANILA", 10.5, WHITE, 2, align="c")
    flags = (flag_us, flag_in, flag_jp, flag_au)
    names = ("USA", "INDIA", "JAPAN", "AUSTRALIA")
    fw = int(w * 0.20); fh = int(h * 0.30)
    for i, fn in enumerate(flags):
        fx = x + int(w * 0.05) + i * int(w * 0.24)
        fy = y + 36
        cv.line(fx + 3, fy + fh, fx + 3, fy + fh + 16, INK, 2)
        fn(cv, fx, fy, fw, fh)
        tw = text_width(names[i], 7, 1.0)
        draw_text(cv, fx + fw / 2 - tw / 2, fy + fh + 18, names[i], 7, INK, 2, 1.0)
    # summit table with seated leaders
    ty = y + h - 34
    cv.fill_rect(x + w * 0.10, ty, w * 0.80, 10, BROWN)
    cv.fill_rect(x + w * 0.14, ty + 10, w * 0.72, 5, (96, 66, 38))
    for i in range(4):
        px = x + w * (0.22 + i * 0.19)
        person(cv, px, ty - 30, 30, (RED, BLUE, GREEN, ORANGE)[i])

def lead_box(cv, x, y, w, h, num, region, headline, scene, caption):
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect_outline(x, y, w, h, RULE, 2)
    colour = REGION_COLOURS.get(region, INK)
    chip(cv, x + 6, y + 5, num, colour, 8)
    draw_text(cv, x + 27, y + 6, region, 7.5, colour, 2)
    draw_text(cv, x + 6, y + 24, headline, 12.4, INK, 3)
    sy = y + 46
    scene(cv, x + 4, sy, w - 8, h - 46 - 20)
    cv.fill_rect(x + 1, y + h - 19, w - 2, 18, INK)
    draw_text(cv, x + w / 2, y + h - 13.5, caption, 7.8, WHITE, 2, 0.9, "c")

def scene_feature(cv, num, x, y, w, h):
    if num == 4:  # Ebola: virus shapes, clinic, rising bars
        cv.fill_rect(x, y, w, h, (232, 240, 226), True)
        for vx, vy, vr in ((24, 16, 10), (52, 38, 8), (30, 46, 6)):
            cv.circle(x + vx, y + vy, vr, (150, 60, 140), True)
            for a in range(6):
                import math
                ang = a * 1.047
                cv.line(x + vx, y + vy, x + vx + (vr + 4) * math.cos(ang),
                        y + vy + (vr + 4) * math.sin(ang), (150, 60, 140), 2)
        cv.fill_rect(x + 84, y + 12, 62, 34, WHITE)
        cv.rect_outline(x + 84, y + 12, 62, 34, INK, 1)
        cv.fill_rect(x + 106, y + 18, 8, 22, RED)
        cv.fill_rect(x + 99, y + 25, 22, 8, RED)
        draw_text(cv, x + 88, y + 48, "CLINIC", 7, INK, 2)
        for i, bh in enumerate((10, 19, 30)):
            cv.fill_rect(x + 168 + i * 20, y + h - 8 - bh, 14, bh, RED)
        draw_text(cv, x + 160, y + 1, "11,000+", 8, RED, 2)
    elif num == 5:  # COP31: globe + torn draft
        cv.fill_rect(x, y, w, h, SKY2, True)
        cv.circle(x + 34, y + h // 2, 22, SEA, True)
        cv.poly([(x + 20, y + 14), (x + 34, y + 10), (x + 38, y + 22), (x + 24, y + 26)], GREEN, True)
        cv.poly([(x + 38, y + 34), (x + 50, y + 38), (x + 44, y + 50), (x + 32, y + 44)], GREEN, True)
        cv.fill_rect(x + 76, y + 8, 66, 42, WHITE)
        cv.rect_outline(x + 76, y + 8, 66, 42, INK, 1)
        for i in range(4):
            cv.line(x + 82, y + 16 + i * 8, x + 128, y + 16 + i * 8, GREY, 1)
        cv.line(x + 110, y + 8, x + 118, y + 24, RED, 2)
        cv.line(x + 118, y + 24, x + 108, y + 38, RED, 2)
        cv.line(x + 108, y + 38, x + 116, y + 50, RED, 2)
        draw_text(cv, x + 152, y + 14, "COP31", 11, BLUE, 2)
        draw_text(cv, x + 152, y + 30, "DRAFT", 9, INK, 2)
        draw_text(cv, x + 152, y + 43, "TORN", 9, RED, 2)
    elif num == 6:  # Measles: cracked shield + three country tags
        cv.fill_rect(x, y, w, h, (240, 232, 214), True)
        cx = x + 44; cy = y + h // 2
        cv.poly([(cx - 20, cy - 22), (cx + 20, cy - 22), (cx + 20, cy + 2),
                 (cx, cy + 24), (cx - 20, cy + 2)], (200, 170, 60), True)
        cv.poly([(cx - 20, cy - 22), (cx + 20, cy - 22), (cx + 20, cy + 2),
                 (cx, cy + 24), (cx - 20, cy + 2)], INK, False, 1)
        cv.line(cx - 4, cy - 20, cx + 4, cy - 6, INK, 2)
        cv.line(cx + 4, cy - 6, cx - 6, cy + 6, INK, 2)
        cv.line(cx - 6, cy + 6, cx + 2, cy + 20, INK, 2)
        cv.fill_rect(cx - 3, cy - 12, 6, 18, RED)
        cv.fill_rect(cx - 9, cy - 6, 18, 6, RED)
        for i, tag in enumerate(("US", "MEXICO", "BOLIVIA")):
            tx = x + 92 + i * 48
            cv.fill_rect(tx, y + 18, 42, 18, WHITE)
            cv.rect_outline(tx, y + 18, 42, 18, RED, 1)
            tw = text_width(tag, 7.5, 1.0)
            draw_text(cv, tx + 21 - tw / 2, y + 23, tag, 7.5, INK, 2, 1.0)
        draw_text(cv, x + 92, y + 42, "STATUS LOST", 8, RED, 2)
    elif num == 7:  # Nvidia bars + chip vs Dow arrow
        cv.fill_rect(x, y, w, h, (226, 236, 226), True)
        for i, bh in enumerate((12, 24, 40)):
            cv.fill_rect(x + 12 + i * 20, y + h - 10 - bh, 14, bh, GREEN)
        cv.fill_rect(x + 76, y + 12, 30, 30, INK)
        cv.fill_rect(x + 82, y + 18, 18, 18, GREEN2)
        for i in range(3):
            cv.line(x + 72, y + 16 + i * 10, x + 76, y + 16 + i * 10, INK, 2)
            cv.line(x + 106, y + 16 + i * 10, x + 110, y + 16 + i * 10, INK, 2)
        draw_text(cv, x + 118, y + 10, "$115.8BN", 11, GREEN, 3)
        cv.line(x + 122, y + 34, x + 176, y + 48, RED, 3)
        cv.poly([(x + 176, y + 48), (x + 164, y + 46), (x + 170, y + 38)], RED, True)
        draw_text(cv, x + 182, y + 38, "-849", 11, RED, 3)
        draw_text(cv, x + 118, y + 24, "DOW", 8, INK, 2)
    elif num == 8:  # Gaza tents + held truck in rain
        cv.fill_rect(x, y, w, h, (196, 204, 210), True)
        for i in range(14):
            rx = x + 8 + i * 16
            cv.line(rx, y + 4, rx - 4, y + 14, BLUE, 1)
        for i, tx in enumerate((10, 52, 94)):
            cv.tri((x + tx, y + h - 10), (x + tx + 18, y + 22), (x + tx + 36, y + h - 10), (238, 226, 200))
            cv.line(x + tx + 18, y + 22, x + tx + 18, y + h - 10, BROWN, 1)
        cv.fill_rect(x + 152, y + 26, 52, 22, WHITE)
        cv.rect_outline(x + 152, y + 26, 52, 22, INK, 1)
        cv.fill_rect(x + 198, y + 32, 12, 16, SKY)
        cv.circle(x + 164, y + 50, 5, INK, True)
        cv.circle(x + 196, y + 50, 5, INK, True)
        cv.fill_rect(x + 158, y + 32, 8, 10, RED)
        cv.fill_rect(x + 155, y + 35, 14, 4, RED)
        draw_text(cv, x + 96, y + 6, "AID HELD", 8.5, RED, 2)
    elif num == 9:  # Mongolia parliament + ger + figure
        cv.fill_rect(x, y, w, h, SKY2, True)
        cv.fill_rect(x, y + h - 12, w, 12, GREEN2)
        cv.fill_rect(x + 16, y + 16, 84, 30, (214, 204, 188))
        cv.rect_outline(x + 16, y + 16, 84, 30, INK, 1)
        for c in range(4):
            cv.fill_rect(x + 24 + c * 20, y + 24, 10, 14, SKY)
        cv.tri((x + 10, y + 16), (x + 58, y + 4), (x + 106, y + 16), BROWN)
        cv.poly([(x + 132, y + 46), (x + 148, y + 22), (x + 164, y + 46)], WHITE, True)
        cv.poly([(x + 132, y + 46), (x + 148, y + 22), (x + 164, y + 46)], INK, False, 1)
        cv.fill_rect(x + 145, y + 34, 6, 12, BROWN)
        person(cv, x + 196, y + 12, 36, BLUE)
        cv.line(x + 188, y + 8, x + 206, y + 8, INK, 2)
        draw_text(cv, x + 176, y + 50, "QUITS", 8, RED, 2)
    elif num == 10:  # Serbia parliament + crowd
        cv.fill_rect(x, y, w, h, (232, 226, 240), True)
        cv.fill_rect(x + 12, y + 6, 76, 28, (206, 198, 220))
        cv.rect_outline(x + 12, y + 6, 76, 28, INK, 1)
        cv.tri((x + 6, y + 6), (x + 50, y - 4 + 4), (x + 94, y + 6), (140, 120, 170))
        for c in range(3):
            cv.fill_rect(x + 22 + c * 24, y + 14, 10, 14, WHITE)
        draw_text(cv, x + 100, y + 12, "140 - 103", 11, INK, 3)
        draw_text(cv, x + 100, y + 28, "THE VOTE", 7.5, GREY, 2)
        for i in range(5):
            person(cv, x + 20 + i * 26, y + h - 24, 20, (RED, BLUE, GREEN, ORANGE)[i % 4])
        cv.fill_rect(x + 152, y + h - 16, 62, 12, WHITE)
        cv.rect_outline(x + 152, y + h - 16, 62, 12, INK, 1)
        draw_text(cv, x + 158, y + h - 13, "STUDENTS", 7.5, RED, 2)
    elif num == 11:  # Dhaka factory + banner crowd + gas
        cv.fill_rect(x, y, w, h, (226, 220, 204), True)
        cv.fill_rect(x + 8, y + 6, 74, 40, (188, 178, 164))
        cv.rect_outline(x + 8, y + 6, 74, 40, INK, 1)
        for r in range(2):
            for c in range(3):
                cv.fill_rect(x + 14 + c * 22, y + 12 + r * 16, 14, 10, YELLOW)
        cv.fill_rect(x + 66, y - 2 + 2, 8, 10, GREY)
        cloud(cv, x + 150, y + 6, 60, (170, 190, 170))
        cv.fill_rect(x + 98, y + 24, 118, 15, RED)
        draw_text(cv, x + 104, y + 28, "TK 30,000 NOW", 9.5, WHITE, 2)
        for i in range(6):
            person(cv, x + 108 + i * 20, y + h - 20, 17, (BLUE, GREEN, ORANGE)[i % 3])
    elif num == 12:  # An-12 wreck in snow
        cv.fill_rect(x, y, w, h, (238, 242, 246), True)
        for i in range(10):
            cv.line(x + 10 + i * 24, y + 8 + (i % 3) * 5, x + 16 + i * 24, y + 8 + (i % 3) * 5, SKY, 2)
        cv.poly([(x + 30, y + 36), (x + 96, y + 28), (x + 150, y + 34),
                 (x + 148, y + 44), (x + 40, y + 48)], (196, 202, 208), True)
        cv.poly([(x + 30, y + 36), (x + 96, y + 28), (x + 150, y + 34),
                 (x + 148, y + 44), (x + 40, y + 48)], INK, False, 1)
        cv.fill_rect(x + 34, y + 37, 112, 4, RED)
        cv.poly([(x + 128, y + 30), (x + 148, y + 12), (x + 156, y + 13),
                 (x + 146, y + 32)], (176, 184, 192), True)
        cv.poly([(x + 58, y + 30), (x + 84, y + 16), (x + 94, y + 18),
                 (x + 82, y + 34)], (176, 184, 192), True)
        for px in (66, 104):
            cv.line(x + px, y + 40, x + px, y + 52, INK, 2)
            cv.line(x + px - 5, y + 46, x + px + 5, y + 46, INK, 2)
        cv.fill_rect(x + 24, y + 48, 60, 6, WHITE)
        cv.fill_rect(x + 120, y + 50, 70, 6, WHITE)
        draw_text(cv, x + 168, y + 10, "AN-12", 10, INK, 2)
        draw_text(cv, x + 168, y + 24, "SNOW", 8, GREY, 2)
    elif num == 13:  # Mondlane courthouse + scales + ribbon
        cv.fill_rect(x, y, w, h, (240, 234, 218), True)
        cv.fill_rect(x + 14, y + 14, 82, 32, (220, 212, 196))
        cv.rect_outline(x + 14, y + 14, 82, 32, INK, 1)
        cv.tri((x + 8, y + 14), (x + 55, y + 2), (x + 102, y + 14), BROWN)
        for c in range(3):
            cv.fill_rect(x + 24 + c * 26, y + 18, 8, 24, WHITE)
            cv.rect_outline(x + 24 + c * 26, y + 18, 8, 24, GREY, 1)
        sx = x + 140
        cv.line(sx, y + 8, sx, y + 40, INK, 2)
        cv.line(sx - 18, y + 12, sx + 18, y + 12, INK, 2)
        cv.poly([(sx - 26, y + 22), (sx - 10, y + 22), (sx - 18, y + 30)], YELLOW, True)
        cv.poly([(sx + 10, y + 22), (sx + 26, y + 22), (sx + 18, y + 30)], YELLOW, True)
        cv.line(sx - 18, y + 12, sx - 18, y + 22, INK, 1)
        cv.line(sx + 18, y + 12, sx + 18, y + 22, INK, 1)
        cv.fill_rect(sx - 12, y + 42, 24, 4, INK)
        cv.fill_rect(x + 186, y + 8, 10, 40, GREEN)
        cv.fill_rect(x + 196, y + 8, 10, 40, YELLOW)
        cv.fill_rect(x + 206, y + 8, 10, 40, RED)

# ---------------------------------------------------------------- map
CONTINENTS = [
    [(2, 18), (10, 8), (24, 6), (36, 10), (38, 18), (34, 26), (28, 30),
     (26, 38), (21, 35), (17, 27), (8, 26)],
    [(29, 40), (38, 38), (42, 44), (40, 54), (34, 58), (30, 50)],
    [(44, 16), (50, 10), (58, 10), (60, 16), (56, 22), (49, 22), (45, 20)],
    [(46, 26), (58, 24), (64, 30), (62, 42), (56, 52), (50, 50), (46, 38)],
    [(60, 14), (74, 8), (90, 10), (98, 18), (94, 26), (86, 30), (84, 38),
     (78, 32), (69, 26), (61, 22)],
    [(84, 34), (88, 34), (87, 42), (84, 40)],
    [(88, 44), (98, 43), (100, 51), (92, 54), (86, 50)],
]
PINS = [
    (1, 59, 15, "EUROPE"), (2, 66, 27, "MIDDLE EAST"), (3, 93, 32, "ASIA"),
    (4, 54, 38, "AFRICA"), (5, 60, 21, "EUROPE"), (6, 16, 28, "AMERICAS"),
    (7, 30, 20, "AMERICAS"), (8, 62, 25, "MIDDLE EAST"), (9, 84, 16, "ASIA"),
    (10, 53, 17, "EUROPE"), (11, 80, 27, "ASIA"), (12, 76, 12, "ASIA"),
    (13, 56, 49, "AFRICA"),
]

def draw_map(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (172, 204, 226), True)
    def mp(lx, ly):
        return (x + lx / 100 * w, y + ly / 60 * h)
    for poly_pts in CONTINENTS:
        cv.poly([mp(a, b) for a, b in poly_pts], (214, 198, 156), True)
        cv.poly([mp(a, b) for a, b in poly_pts], (120, 104, 70), False, 1)
    for num, lx, ly, region in PINS:
        px, py = mp(lx, ly)
        cv.circle(int(px), int(py), 8, REGION_COLOURS[region], True)
        cv.circle(int(px), int(py), 8, WHITE, False, 1)
        s = str(num)
        tw = text_width(s, 9, 0.8)
        draw_text(cv, px - tw / 2, py - 4.5, s, 9, WHITE, 2, 0.8)

def scene_feature_scaled(cv, num, x, y, w, h):
    # scenes are composed on a 238-wide stage, then resampled onto the
    # narrower feature cell so no element can spill past the cell edge
    stage_w = 238
    tmp = Canvas(stage_w, h, WHITE)
    scene_feature(tmp, num, 0, 0, stage_w, h)
    for yy in range(h):
        for xx in range(w):
            sx = int(xx * stage_w / w)
            di = ((y + yy) * cv.w + (x + xx)) * 3
            si = (yy * stage_w + sx) * 3
            cv.px[di] = tmp.px[si]
            cv.px[di + 1] = tmp.px[si + 1]
            cv.px[di + 2] = tmp.px[si + 2]

def feature_box(cv, x, y, w, h, feat):
    num, region, kicker, headline, summary = feat
    cv.fill_rect(x, y, w, h, WHITE)
    cv.rect_outline(x, y, w, h, RULE, 1)
    sy = int(header_block(cv, x + 5, y + 4, w - 10, num, region, kicker, headline, 11))
    scene_feature_scaled(cv, num, x + 5, sy, w - 10, 54)
    draw_wrapped(cv, x + 6, sy + 58, summary, 7.2, GREY, w - 12, 1, 1.3, 1.0, 3)

# ---------------------------------------------------------------- page
def build_page():
    cv = Canvas(W, H, PAPER)
    cv.fill_rect(0, 0, W, H, PAPER, True)
    M = 14
    CW = W - 2 * M
    # top strip
    draw_text(cv, M, 10, "THE WORLD'S NEWS IN ONE PICTURE", 9, INK, 2)
    draw_text(cv, W - M - 4, 10, "45+ STORIES · 6 CONTINENTS · ALL FROM TUESDAY",
              9, RED, 2, align="r")
    cv.fill_rect(M, 26, CW, 2, INK)
    # paper name
    draw_text(cv, W / 2, 32, "THE DAILY MERIDIAN", 19, INK, 3, align="c")
    cv.fill_rect(M, 56, CW, 3, INK)
    # giant date masthead
    draw_text(cv, W / 2, 64, "Tuesday 17 November 2026", 43, INK, 5, 0.9, "c")
    draw_text(cv, W / 2, 114, "46 STORIES · 13 ILLUSTRATED · NUMBERED WORLD MAP · ONE DAY ONLY",
              9.5, BLUE, 2, align="c")
    cv.fill_rect(M, 130, CW, 2, INK)
    # lead trio
    ly = 138; lh = 232
    lw = (CW - 16) // 3
    lead_box(cv, M, ly, lw, lh, 1, "EUROPE", "CRIMEAN BRIDGE STRUCK AGAIN",
             scene_kerch, "KERCH STRAIT · STRUCK FOR A SECOND DAY")
    lead_box(cv, M + lw + 8, ly, lw, lh, 2, "MIDDLE EAST", "IRAN DRONES DOWNED AT BAHRAIN",
             scene_gulf, "DRONES DOWNED OVER THE GULF")
    lead_box(cv, M + 2 * (lw + 8), ly, CW - 2 * (lw + 8), lh, 3, "ASIA",
             "QUAD LEADERS MEET IN MANILA", scene_quad,
             "US · INDIA · JAPAN · AUSTRALIA SUMMIT")
    # features in two rows of five
    fy = 378; fh = 140; gap = 6
    fw = (CW - 4 * gap) // 5
    for i, feat in enumerate(FEATURES):
        row = i // 5; col = i % 5
        fx = M + col * (fw + gap)
        if col == 4:
            fw2 = CW - 4 * (fw + gap)
        else:
            fw2 = fw
        feature_box(cv, fx, fy + row * (fh + gap), fw2, fh, feat)
    # bottom: map + also-on list
    by = 670; bh = 186
    cv.fill_rect(M, by, 376, bh, WHITE)
    cv.rect_outline(M, by, 376, bh, RULE, 2)
    draw_text(cv, M + 8, by + 6, "WHERE IT HAPPENED — WORLD MAP", 10.5, INK, 2)
    draw_map(cv, M + 8, by + 26, 360, 118)
    regions = list(REGION_COLOURS.items())
    for i, (name, colour) in enumerate(regions):
        lx = M + 10 + (i % 4) * 92
        ly2 = by + 150 + (i // 4) * 16
        cv.fill_rect(lx, ly2 + 2, 10, 8, colour)
        draw_text(cv, lx + 14, ly2, name, 6.8, INK, 1, 0.9)
    ax = M + 384; aw = CW - 384
    cv.fill_rect(ax, by, aw, bh, WHITE)
    cv.rect_outline(ax, by, aw, bh, RULE, 2)
    draw_text(cv, ax + 8, by + 6, "ALSO ON TUESDAY 17 NOVEMBER", 10.5, RED, 2)
    colw = (aw - 24) // 2
    for i, line in enumerate(ONELINERS):
        col = 0 if i < 17 else 1
        row = i if i < 17 else i - 17
        ix = ax + 8 + col * (colw + 8)
        iy = by + 27 + row * 9.4
        draw_text(cv, ix, iy, str(14 + i), 6.8, RED, 2, 0.9)
        draw_text(cv, ix + 19, iy, line, 5.9, INK, 1, 0.5)
    # stat strip
    sy = 864
    cv.fill_rect(M, sy, CW, 54, INK)
    stats = [
        ("2 DAYS", "STRIKES ON THE CRIMEAN BRIDGE"),
        ("11,000+", "EBOLA CASES IN DR CONGO"),
        ("$115.8BN", "NVIDIA QUARTERLY SALES, UP 103%"),
        ("-849", "DOW FALL (-1.6%) ON THE DAY"),
    ]
    cell = CW // 4
    for i, (big, label) in enumerate(stats):
        cx = M + i * cell + cell / 2
        draw_text(cv, cx, sy + 7, big, 19, YELLOW, 3, align="c")
        draw_text(cv, cx, sy + 34, label, 7.3, WHITE, 1, 0.9, "c")
        if i:
            cv.fill_rect(M + i * cell, sy + 6, 1, 42, GREY)
    # footer
    draw_text(cv, W / 2, 928,
              "EVERY STORY HERE HAPPENED OR WAS FIRST REPORTED ON TUESDAY 17 NOVEMBER 2026. CONTESTED CLAIMS ARE MARKED AS CLAIMS.",
              8.6, INK, 1, 0.8, "c")
    draw_text(cv, W / 2, 946,
              "SOURCES: REUTERS, AP, AFP, BBC, AL JAZEERA, WHO, UN. ORIGINAL DRAWINGS.",
              8.6, GREY, 1, 0.8, "c")
    cv.fill_rect(M, 962, CW, 2, INK)
    draw_text(cv, W / 2, 970, "THE DAILY MERIDIAN · ONE DAY · ONE PICTURE · NO PHOTOGRAPHS",
              8, INK, 2, align="c")
    apply_print_grain(cv)
    return cv

def apply_print_grain(cv):
    # a deterministic newsprint grain: a small per-block shade shift,
    # hashed from block coordinates only, so runs stay byte-identical
    for yy in range(cv.h):
        by = (yy // 2) * 19349663
        base = yy * cv.w * 3
        for xx in range(cv.w):
            n = ((xx // 2) * 73856093) ^ by
            n = (n ^ (n >> 13)) & 7
            d = (int(n) - 3) * 2
            if d:
                i = base + xx * 3
                cv.px[i] = max(0, min(255, cv.px[i] + d))
                cv.px[i + 1] = max(0, min(255, cv.px[i + 1] + d))
                cv.px[i + 2] = max(0, min(255, cv.px[i + 2] + d))

def main():
    cv = build_page()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(cv.px, cv.w, cv.h))
    # the repo also keeps a copy beside main.py for the feed snapshot
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.png"), "wb") as f:
        f.write(png_bytes(cv.px, cv.w, cv.h))

if __name__ == "__main__":
    main()
