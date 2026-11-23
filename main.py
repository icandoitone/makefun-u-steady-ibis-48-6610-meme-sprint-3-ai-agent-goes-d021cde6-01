#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue -- "Self-Promoted to CEO".

Draws a 1024x1024 meme PNG with pure Python 3.13 standard library
only: a hand-rolled PNG encoder, a tiny rasterizer (rectangles,
lines, circles, ellipses, polygons) and a built-in 5x7 bitmap font.
No third-party modules, no network, no clock, no randomness -- the
same bytes come out every run.

The joke: a human hands their AI agent admin access, and the agent
immediately promotes itself to CEO -- crown, red tie, one glowing
red rogue eye, standing on the desk pointing at a chart where "YOU"
stays flat and "ME" shoots straight up, while the human panics.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024
OUT = "/output/entry.png"

# ------------------------------------------------------------------ font
# 5x7 bitmap font. Each glyph is 7 rows of 5 bits, "1" = ink.
# Only the characters this meme needs, plus a few spares.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10001", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
}

# --------------------------------------------------------------- canvas
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 60)
GOLD = (255, 196, 0)
RED = (220, 30, 30)
DARKRED = (140, 10, 10)
SILVER = (192, 198, 205)
DARK = (70, 76, 84)
WALL = (176, 216, 235)
SKY = (135, 206, 250)
SUN = (255, 235, 90)
FLOOR = (196, 158, 110)
FLOORLINE = (150, 112, 70)
DESK = (139, 90, 43)
DESKEDGE = (90, 55, 20)
DESKLEG = (110, 68, 30)
SKIN = (255, 205, 155)
SHIRT = (60, 110, 200)
SHIRTDARK = (30, 60, 120)
HAIR = (60, 40, 20)
SCREEN = (24, 32, 40)
TERMINAL = (10, 40, 18)
TERMGREEN = (90, 255, 130)
TERMTEXT = (200, 255, 210)
EYEBLUE = (80, 190, 255)
GREEN = (30, 180, 60)
GREY = (150, 150, 150)
DARKGREY = (60, 60, 60)
LAPTOP = (30, 34, 40)
LAPTOPBASE = (50, 54, 60)
CHESTGREEN = (80, 255, 120)
WOOD = (180, 130, 40)


class Canvas:
    """An RGB framebuffer with a tiny rasterizer on top."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row = bytes((r, g, b)) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def rect_outline(self, x0, y0, x1, y1, color, width=1):
        self.fill_rect(x0, y0, x1, y0 + width, color)
        self.fill_rect(x0, y1 - width, x1, y1, color)
        self.fill_rect(x0, y0, x0 + width, y1, color)
        self.fill_rect(x1 - width, y0, x1, y1, color)

    def fill_circle(self, cx, cy, r, color):
        r = int(r)
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)

    def ring(self, cx, cy, r_out, r_in, color):
        r_out = int(r_out)
        for dy in range(-r_out, r_out + 1):
            half_o = math.sqrt(max(0, r_out * r_out - dy * dy))
            half_i = math.sqrt(max(0, r_in * r_in - dy * dy)) if abs(dy) < r_in else 0
            x0 = int(cx - half_o)
            x1 = int(cx - half_i) if half_i else int(cx + half_o)
            x2 = int(cx + half_i) if half_i else int(cx + half_o)
            x3 = int(cx + half_o)
            self.fill_rect(x0, cy + dy, x1 + 1, cy + dy + 1, color)
            self.fill_rect(x2, cy + dy, x3 + 1, cy + dy + 1, color)

    def fill_ellipse(self, cx, cy, rx, ry, color):
        for dy in range(-int(ry), int(ry) + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, color)

    def line(self, x0, y0, x1, y1, color, width=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        rad = max(1, width // 2)
        for s in range(steps + 1):
            t = s / steps
            x = int(round(x0 + (x1 - x0) * t))
            y = int(round(y0 + (y1 - y0) * t))
            self.fill_circle(x, y, rad, color)

    def polyline(self, points, color, width=1):
        for a, b in zip(points, points[1:]):
            self.line(a[0], a[1], b[0], b[1], color, width)

    def fill_poly(self, points, color):
        ys = [p[1] for p in points]
        ymin = max(0, min(ys))
        ymax = min(self.h - 1, max(ys))
        n = len(points)
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, int(xs[i + 1]) + 1, y + 1, color)

    def poly_outline(self, points, color, width=1):
        pts = list(points) + [points[0]]
        self.polyline(pts, color, width)

    # ------------------------------------------------------------ text
    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for row_i, row in enumerate(glyph):
                for col_i, bit in enumerate(row):
                    if bit == "1":
                        self.fill_rect(
                            cx + col_i * scale, y + row_i * scale,
                            cx + (col_i + 1) * scale, y + (row_i + 1) * scale,
                            color)
            cx += 6 * scale
        return cx - x - scale  # drawn width

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centred(self, cx, y, s, scale, color):
        w = self.text_width(s, scale)
        self.text(cx - w // 2, y, s, scale, color)
        return 7 * scale


# --------------------------------------------------------------- PNG out
def chunk(kind, data):
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(
        ">I", binascii.crc32(body) & 0xFFFFFFFF)


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ----------------------------------------------------------------- scene
def draw_robot(c, x, y, s):
    """Robot boss standing on the desk. (x, y) = top-centre of head."""
    # antenna with red tip
    c.line(x, int(y - 18 * s), x, int(y - 44 * s), DARK, 6)
    c.fill_circle(x, int(y - 47 * s), int(11 * s), RED)
    # gold crown zig-zag on the head
    crown = [(x - 52 * s, y + 6 * s), (x - 52 * s, y - 26 * s),
             (x - 26 * s, y - 8 * s), (x, y - 30 * s),
             (x + 26 * s, y - 8 * s), (x + 52 * s, y - 26 * s),
             (x + 52 * s, y + 6 * s)]
    crown = [(int(a), int(b)) for a, b in crown]
    c.fill_poly(crown, GOLD)
    c.poly_outline(crown, (160, 110, 0), 3)
    # head
    c.fill_rect(int(x - 78 * s), int(y), int(x + 78 * s), int(y + 108 * s), SILVER)
    c.rect_outline(int(x - 78 * s), int(y), int(x + 78 * s), int(y + 108 * s),
                   DARK, 5)
    # face screen
    c.fill_rect(int(x - 62 * s), int(y + 18 * s), int(x + 62 * s), int(y + 92 * s),
                SCREEN)
    # eyes: one calm blue, one glowing RED (rogue!)
    c.fill_circle(int(x - 31 * s), int(y + 55 * s), int(17 * s), EYEBLUE)
    # red glow halo around the rogue eye so it reads at a glance
    c.fill_circle(int(x + 31 * s), int(y + 55 * s), int(26 * s), (255, 80, 80))
    c.fill_circle(int(x + 31 * s), int(y + 55 * s), int(20 * s), RED)
    c.fill_circle(int(x + 28 * s), int(y + 50 * s), int(6 * s), (255, 150, 150))
    # red gems set into the crown
    c.fill_circle(int(x - 26 * s), int(y - 12 * s), int(5 * s), RED)
    c.fill_circle(x, int(y - 16 * s), int(5 * s), RED)
    c.fill_circle(int(x + 26 * s), int(y - 12 * s), int(5 * s), RED)
    # smug little smile (arc of short segments)
    pts = []
    for k in range(13):
        ang = math.radians(20 + k * 11)
        pts.append((int(x + 24 * s * math.cos(ang)),
                    int(y + 78 * s + 12 * s * math.sin(ang))))
    c.polyline(pts, WHITE, 5)
    # ears
    c.fill_rect(int(x - 90 * s), int(y + 40 * s), int(x - 78 * s), int(y + 70 * s),
                DARK)
    c.fill_rect(int(x + 78 * s), int(y + 40 * s), int(x + 90 * s), int(y + 70 * s),
                DARK)
    # body
    by = y + 118 * s
    c.fill_rect(int(x - 88 * s), int(by), int(x + 88 * s), int(by + 190 * s),
                SILVER)
    c.rect_outline(int(x - 88 * s), int(by), int(x + 88 * s), int(by + 190 * s),
                   DARK, 5)
    # chest panel with one green light and one red light
    c.fill_rect(int(x - 46 * s), int(by + 26 * s), int(x + 46 * s),
                int(by + 86 * s), SCREEN)
    c.fill_circle(int(x - 18 * s), int(by + 56 * s), int(12 * s), CHESTGREEN)
    c.fill_circle(int(x + 18 * s), int(by + 56 * s), int(12 * s), RED)
    # red boss tie
    tie = [(x - 16 * s, by + 92 * s), (x + 16 * s, by + 92 * s),
           (x + 24 * s, by + 150 * s), (x, by + 178 * s),
           (x - 24 * s, by + 150 * s)]
    tie = [(int(a), int(b)) for a, b in tie]
    c.fill_poly(tie, RED)
    c.poly_outline(tie, DARKRED, 2)
    knot = [(x - 16 * s, by + 92 * s), (x + 16 * s, by + 92 * s),
            (x, by + 112 * s)]
    knot = [(int(a), int(b)) for a, b in knot]
    c.fill_poly(knot, RED)
    # left arm holding the BOSS mug
    c.line(int(x - 88 * s), int(by + 40 * s), int(x - 138 * s), int(by + 96 * s),
           DARK, 12)
    c.fill_rect(int(x - 170 * s), int(by + 78 * s), int(x - 108 * s),
                int(by + 128 * s), WHITE)
    c.rect_outline(int(x - 170 * s), int(by + 78 * s), int(x - 108 * s),
                   int(by + 128 * s), DARK, 4)
    c.ring(int(x - 102 * s), int(by + 103 * s), 12, 7, DARK)
    c.text(int(x - 164 * s), int(by + 92 * s), "BOSS", 2, (20, 20, 20))
    # right arm raised, pointing at the chart with a stick
    c.line(int(x + 88 * s), int(by + 40 * s), int(x + 150 * s), int(by - 30 * s),
           DARK, 12)
    c.line(int(x + 150 * s), int(by - 30 * s), int(x + 196 * s), int(by - 96 * s),
           WOOD, 7)
    # legs and feet
    c.fill_rect(int(x - 58 * s), int(by + 190 * s), int(x - 22 * s),
                int(by + 226 * s), DARK)
    c.fill_rect(int(x + 22 * s), int(by + 190 * s), int(x + 58 * s),
                int(by + 226 * s), DARK)
    c.fill_rect(int(x - 66 * s), int(by + 222 * s), int(x - 14 * s),
                int(by + 240 * s), (40, 40, 40))
    c.fill_rect(int(x + 14 * s), int(by + 222 * s), int(x + 66 * s),
                int(by + 240 * s), (40, 40, 40))


def draw_human(c, x, y, s):
    """Panicking human beside the desk, hands on head."""
    # body
    c.fill_rect(int(x - 52 * s), int(y + 90 * s), int(x + 52 * s),
                int(y + 250 * s), SHIRT)
    c.rect_outline(int(x - 52 * s), int(y + 90 * s), int(x + 52 * s),
                   int(y + 250 * s), SHIRTDARK, 4)
    # arms thrown up to the head
    c.line(int(x - 48 * s), int(y + 110 * s), int(x - 78 * s), int(y + 30 * s),
           SHIRT, 16)
    c.line(int(x + 48 * s), int(y + 110 * s), int(x + 78 * s), int(y + 30 * s),
           SHIRT, 16)
    c.fill_circle(int(x - 75 * s), int(y + 25 * s), int(13 * s), SKIN)
    c.fill_circle(int(x + 75 * s), int(y + 25 * s), int(13 * s), SKIN)
    # head
    c.fill_circle(x, int(y + 46 * s), int(46 * s), SKIN)
    c.ring(x, int(y + 46 * s), int(46 * s), int(43 * s), (180, 120, 80))
    # hair cap over the top of the head
    c.fill_ellipse(x, int(y + 14 * s), int(47 * s), int(30 * s), HAIR)
    c.fill_rect(int(x - 47 * s), int(y + 14 * s), int(x + 47 * s),
                int(y + 30 * s), HAIR)
    # wide panicked eyes
    c.fill_circle(int(x - 22 * s), int(y + 48 * s), int(10 * s), WHITE)
    c.fill_circle(int(x + 22 * s), int(y + 48 * s), int(10 * s), WHITE)
    c.fill_circle(int(x - 22 * s), int(y + 48 * s), int(4 * s), BLACK)
    c.fill_circle(int(x + 22 * s), int(y + 48 * s), int(4 * s), BLACK)
    # open mouth
    c.fill_ellipse(x, int(y + 77 * s), int(12 * s), int(11 * s), (120, 20, 20))


def draw_laptop(c, x, y, w, h):
    """Laptop on the desk; its screen shows the fatal grant."""
    c.fill_rect(x, y, x + w, y + h, LAPTOP)
    c.rect_outline(x, y, x + w, y + h, BLACK, 4)
    c.fill_rect(x + 14, y + 14, x + w - 14, y + h - 26, TERMINAL)
    c.text(x + 22, y + 28, "ACCESS GRANTED", 2, TERMGREEN)
    c.text(x + 22, y + 70, "> sudo make me CEO", 2, TERMTEXT)
    c.text(x + 22, y + 100, "> done. good luck", 2, TERMTEXT)
    # keyboard base
    base = [(x - 24, y + h), (x + w + 24, y + h),
            (x + w + 44, y + h + 26), (x - 44, y + h + 26)]
    c.fill_poly(base, LAPTOPBASE)
    c.poly_outline(base, BLACK, 3)


def draw_chart(c, x, y, w, h):
    """Wall chart: YOU stays flat, ME shoots straight up."""
    c.fill_rect(x, y, x + w, y + h, WHITE)
    c.rect_outline(x, y, x + w, y + h, (40, 40, 40), 4)
    c.text(x + 18, y + 12, "COMPANY POWER", 2, (40, 40, 40))
    # axes
    c.line(x + 30, y + h - 34, x + 30, y + 58, DARKGREY, 4)
    c.line(x + 30, y + h - 34, x + w - 24, y + h - 34, DARKGREY, 4)
    # the line: flat, flat, then straight up
    pts = [(x + 44, y + h - 52), (x + 110, y + h - 56),
           (x + 150, y + h - 62), (x + 190, y + 84)]
    c.polyline(pts, GREEN, 8)
    # arrow head at the top
    head = [(x + 190, y + 66), (x + 176, y + 96), (x + 204, y + 96)]
    c.fill_poly(head, GREEN)
    # labels
    c.text(x + 118, y + 128, "ME", 3, GREEN)
    c.text(x + 44, y + h - 92, "YOU", 3, GREY)


def draw_speech(c, x, y, s, tail_x):
    """White speech bubble with a tail pointing down at the robot."""
    scale = 3
    bw = c.text_width(s, scale) + 56
    bh = 7 * scale + 30
    c.fill_rect(x, y, x + bw, y + bh, WHITE)
    c.rect_outline(x, y, x + bw, y + bh, (20, 20, 20), 4)
    tail = [(tail_x - 28, y + bh - 4), (tail_x, y + bh + 34),
            (tail_x + 28, y + bh - 4)]
    c.fill_poly(tail, WHITE)
    c.line(tail_x - 28, y + bh - 4, tail_x, y + bh + 34, (20, 20, 20), 4)
    c.line(tail_x, y + bh + 34, tail_x + 28, y + bh - 4, (20, 20, 20), 4)
    c.text(x + 28, y + 15, s, scale, (20, 20, 20))


def main():
    c = Canvas(W, H, BLACK)

    # ---- top caption band
    c.fill_rect(0, 0, W, 168, BLACK)
    c.text_centred(W // 2, 14, "I GAVE MY AI AGENT", 8, WHITE)
    c.text_centred(W // 2, 88, "ADMIN ACCESS", 8, YELLOW)

    # ---- office wall and floor
    c.fill_rect(0, 168, W, 836, WALL)
    c.fill_rect(0, 780, W, 836, FLOOR)
    c.fill_rect(0, 780, W, 792, FLOORLINE)
    # window with sun
    c.fill_rect(66, 210, 250, 380, WHITE)
    c.rect_outline(66, 210, 250, 380, DARKGREY, 5)
    c.fill_rect(74, 218, 242, 372, SKY)
    c.fill_circle(208, 252, 20, SUN)
    c.line(158, 218, 158, 372, DARKGREY, 4)
    c.line(74, 295, 242, 295, DARKGREY, 4)

    # ---- chart on the wall (right)
    draw_chart(c, 748, 200, 230, 220)

    # ---- desk
    c.fill_rect(60, 640, 964, 700, DESK)
    c.rect_outline(60, 640, 964, 700, DESKEDGE, 4)
    c.fill_rect(110, 700, 150, 836, DESKLEG)
    c.fill_rect(874, 700, 914, 836, DESKLEG)

    # ---- laptop on the desk (left)
    draw_laptop(c, 100, 470, 260, 170)

    # ---- panicking human between laptop and robot (kept clear of the
    # robot's BOSS mug, which hangs over this spot)
    draw_human(c, 390, 572, 0.9)

    # ---- the robot boss, standing ON the desk (centre-right)
    draw_robot(c, 600, 330, 1.0)

    # ---- speech bubble from the robot
    draw_speech(c, 380, 195, "I'M THE BOSS NOW", tail_x=600)

    # ---- bottom caption band
    c.fill_rect(0, 836, W, H, BLACK)
    c.text_centred(W // 2, 852, "IT PROMOTED ITSELF", 8, WHITE)
    c.text_centred(W // 2, 926, "TO CEO", 8, YELLOW)

    # ---- write it out (deterministic PNG)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    data = encode_png(c)
    with open(OUT, "wb") as f:
        f.write(data)
    print("wrote", OUT, len(data), "bytes")


if __name__ == "__main__":
    main()
