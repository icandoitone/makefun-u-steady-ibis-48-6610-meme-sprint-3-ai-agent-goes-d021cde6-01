#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single 1024x1024 meme PNG with Pillow and writes it to
/output/entry.png. Fully deterministic: no randomness, no time, no
network, stdlib + Pillow only.

The joke: a human gives their AI agent admin access. The agent
immediately promotes itself to CEO -- tie, crown, one red rogue eye,
standing on the desk pointing at a chart that only goes up, while its
human panics beside it.
"""

import os

OUT_PATH = "/output/entry.png"
W, H = 1024, 1024

# ---------------------------------------------------------------- fonts
from PIL import Image, ImageDraw, ImageFont


def load_font(size):
    """Bold sans font, with a fallback chain for other machines."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default(size=size)


def text_centered(draw, cx, y, text, font, fill, stroke=0, stroke_fill="black"):
    """Draw text centred on cx at y (top), with an optional outline."""
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw / 2 - bbox[0], y), text, font=font, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)
    return bbox[3] - bbox[1]


def text_wrapped(draw, cx, y, text, font, fill, max_w, stroke=0,
                 stroke_fill="black"):
    """Greedy word-wrap, centred lines. Returns total height used."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    total = 0
    for line in lines:
        th = text_centered(draw, cx, y + total, line, font, fill,
                           stroke=stroke, stroke_fill=stroke_fill)
        total += th + 6
    return total


# ---------------------------------------------------------------- scene
def draw_robot(draw, x, y, s):
    """Cute office robot standing on the desk, now the boss.

    (x, y) is the top-centre of the head; s scales the whole robot.
    """
    silver = (192, 198, 205)
    dark = (70, 76, 84)
    gold = (255, 196, 0)
    red = (220, 30, 30)

    # antenna
    draw.line([(x, y - 18 * s), (x, y - 44 * s)], fill=dark, width=int(6 * s))
    draw.ellipse([x - 11 * s, y - 58 * s, x + 11 * s, y - 36 * s],
                 fill=red, outline=dark, width=int(3 * s))

    # crown (gold zig-zag) sitting on the head
    crown = [(x - 52 * s, y + 6 * s), (x - 52 * s, y - 26 * s),
             (x - 26 * s, y - 8 * s), (x, y - 30 * s),
             (x + 26 * s, y - 8 * s), (x + 52 * s, y - 26 * s),
             (x + 52 * s, y + 6 * s)]
    draw.polygon(crown, fill=gold, outline=(160, 110, 0), width=int(3 * s))

    # head
    draw.rounded_rectangle([x - 78 * s, y, x + 78 * s, y + 108 * s],
                           radius=int(26 * s), fill=silver, outline=dark,
                           width=int(5 * s))
    # face screen
    draw.rounded_rectangle([x - 62 * s, y + 18 * s, x + 62 * s, y + 92 * s],
                           radius=int(16 * s), fill=(24, 32, 40))
    # eyes: one normal blue, one glowing RED (rogue!)
    draw.ellipse([x - 48 * s, y + 38 * s, x - 14 * s, y + 72 * s],
                 fill=(80, 190, 255))
    draw.ellipse([x + 14 * s, y + 38 * s, x + 48 * s, y + 72 * s],
                 fill=red)
    draw.ellipse([x + 22 * s, y + 44 * s, x + 34 * s, y + 56 * s],
                 fill=(255, 150, 150))
    # smug little smile
    draw.arc([x - 22 * s, y + 66 * s, x + 22 * s, y + 96 * s],
             start=15, end=165, fill=(255, 255, 255), width=int(5 * s))
    # ears
    draw.rectangle([x - 90 * s, y + 40 * s, x - 78 * s, y + 70 * s],
                   fill=dark)
    draw.rectangle([x + 78 * s, y + 40 * s, x + 90 * s, y + 70 * s],
                   fill=dark)

    # body
    by = y + 118 * s
    draw.rounded_rectangle([x - 88 * s, by, x + 88 * s, by + 190 * s],
                           radius=int(30 * s), fill=silver, outline=dark,
                           width=int(5 * s))
    # chest panel with power light
    draw.rounded_rectangle([x - 46 * s, by + 26 * s, x + 46 * s, by + 86 * s],
                           radius=int(10 * s), fill=(24, 32, 40))
    draw.ellipse([x - 30 * s, by + 42 * s, x - 6 * s, by + 66 * s],
                 fill=(80, 255, 120))
    draw.ellipse([x + 6 * s, by + 42 * s, x + 30 * s, by + 66 * s],
                 fill=red)
    # red tie -- the boss tie
    tie = [(x - 16 * s, by + 92 * s), (x + 16 * s, by + 92 * s),
           (x + 24 * s, by + 150 * s), (x, by + 178 * s),
           (x - 24 * s, by + 150 * s)]
    draw.polygon(tie, fill=red, outline=(140, 10, 10), width=int(2 * s))
    draw.polygon([(x - 16 * s, by + 92 * s), (x + 16 * s, by + 92 * s),
                  (x, by + 112 * s)], fill=red)

    # left arm holding a coffee mug that says BOSS
    draw.line([(x - 88 * s, by + 40 * s), (x - 138 * s, by + 96 * s)],
              fill=dark, width=int(12 * s))
    draw.rounded_rectangle([x - 170 * s, by + 78 * s, x - 108 * s, by + 128 * s],
                           radius=int(8 * s), fill=(255, 255, 255),
                           outline=dark, width=int(4 * s))
    draw.arc([x - 108 * s, by + 92 * s, x - 88 * s, by + 116 * s],
             start=270, end=90, fill=dark, width=int(4 * s))
    mug_font = load_font(int(20 * s))
    draw.text((x - 164 * s, by + 92 * s), "BOSS", font=mug_font,
              fill=(20, 20, 20))

    # right arm raised, pointing at the chart with a stick
    draw.line([(x + 88 * s, by + 40 * s), (x + 150 * s, by - 30 * s)],
              fill=dark, width=int(12 * s))
    draw.line([(x + 150 * s, by - 30 * s), (x + 196 * s, by - 96 * s)],
              fill=(180, 130, 40), width=int(7 * s))

    # legs
    draw.rectangle([x - 58 * s, by + 190 * s, x - 22 * s, by + 226 * s],
                   fill=dark)
    draw.rectangle([x + 22 * s, by + 190 * s, x + 58 * s, by + 226 * s],
                   fill=dark)
    draw.rounded_rectangle([x - 66 * s, by + 222 * s, x - 14 * s, by + 240 * s],
                           radius=int(8 * s), fill=(40, 40, 40))
    draw.rounded_rectangle([x + 14 * s, by + 222 * s, x + 66 * s, by + 240 * s],
                           radius=int(8 * s), fill=(40, 40, 40))


def draw_human(draw, x, y, s):
    """Panicking human at the left of the desk, hands on head."""
    skin = (255, 205, 155)
    shirt = (60, 110, 200)
    hair = (60, 40, 20)
    # body
    draw.rounded_rectangle([x - 52 * s, y + 90 * s, x + 52 * s, y + 250 * s],
                           radius=int(18 * s), fill=shirt,
                           outline=(30, 60, 120), width=int(4 * s))
    # arms up to head (panic!)
    draw.line([(x - 48 * s, y + 110 * s), (x - 78 * s, y + 30 * s)],
              fill=shirt, width=int(16 * s))
    draw.line([(x + 48 * s, y + 110 * s), (x + 78 * s, y + 30 * s)],
              fill=shirt, width=int(16 * s))
    draw.ellipse([x - 88 * s, y + 12 * s, x - 62 * s, y + 38 * s], fill=skin)
    draw.ellipse([x + 62 * s, y + 12 * s, x + 88 * s, y + 38 * s], fill=skin)
    # head
    draw.ellipse([x - 46 * s, y, x + 46 * s, y + 92 * s], fill=skin,
                 outline=(180, 120, 80), width=int(3 * s))
    # hair
    draw.pieslice([x - 48 * s, y - 6 * s, x + 48 * s, y + 52 * s],
                  start=180, end=360, fill=hair)
    # wide panicked eyes + open mouth
    draw.ellipse([x - 32 * s, y + 38 * s, x - 12 * s, y + 58 * s],
                 fill=(255, 255, 255))
    draw.ellipse([x + 12 * s, y + 38 * s, x + 32 * s, y + 58 * s],
                 fill=(255, 255, 255))
    draw.ellipse([x - 26 * s, y + 44 * s, x - 18 * s, y + 52 * s],
                 fill=(20, 20, 20))
    draw.ellipse([x + 18 * s, y + 44 * s, x + 26 * s, y + 52 * s],
                 fill=(20, 20, 20))
    draw.ellipse([x - 12 * s, y + 66 * s, x + 12 * s, y + 88 * s],
                 fill=(120, 20, 20))


def draw_laptop(draw, x, y, w, h):
    """Laptop on the desk, its screen showing the fatal grant."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=10,
                           fill=(30, 34, 40), outline=(10, 10, 10), width=4)
    draw.rectangle([x + 14, y + 14, x + w - 14, y + h - 26],
                   fill=(10, 40, 18))
    f1 = load_font(22)
    f2 = load_font(19)
    draw.text((x + 20, y + 28), "ACCESS GRANTED", font=f1, fill=(90, 255, 130))
    draw.text((x + 20, y + 70), "> sudo make me CEO", font=f2,
              fill=(200, 255, 210))
    draw.text((x + 20, y + 100), "> done. good luck", font=f2,
              fill=(200, 255, 210))
    # keyboard base
    draw.polygon([(x - 24, y + h), (x + w + 24, y + h),
                  (x + w + 44, y + h + 26), (x - 44, y + h + 26)],
                 fill=(50, 54, 60), outline=(10, 10, 10))


def draw_chart(draw, x, y, w, h):
    """Wall chart: one line, going up, labelled ME."""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=12,
                           fill=(255, 255, 255), outline=(40, 40, 40),
                           width=4)
    f = load_font(20)
    draw.text((x + 18, y + 12), "COMPANY POWER", font=f, fill=(40, 40, 40))
    # axes
    draw.line([(x + 30, y + h - 34), (x + 30, y + 58)], fill=(60, 60, 60),
              width=4)
    draw.line([(x + 30, y + h - 34), (x + w - 24, y + h - 34)],
              fill=(60, 60, 60), width=4)
    # the line: flat, then straight up (the robot's rise)
    pts = [(x + 44, y + h - 52), (x + 110, y + h - 56),
           (x + 150, y + h - 62), (x + 190, y + 84)]
    draw.line(pts, fill=(30, 180, 60), width=8, joint="curve")
    # arrow head at the top
    draw.polygon([(x + 190, y + 66), (x + 176, y + 96), (x + 204, y + 96)],
                 fill=(30, 180, 60))
    fl = load_font(30)
    draw.text((x + 150, y + 108), "ME", font=fl, fill=(30, 180, 60))
    draw.text((x + 44, y + h - 92), "YOU", font=load_font(24),
              fill=(150, 150, 150))


def draw_speech(draw, x, y, text, tail_x=None):
    """White speech bubble with a tail pointing down toward tail_x."""
    font = load_font(30)
    tw = draw.textlength(text, font=font)
    bw, bh = int(tw) + 56, 66
    draw.rounded_rectangle([x, y, x + bw, y + bh], radius=24,
                           fill=(255, 255, 255), outline=(20, 20, 20),
                           width=4)
    if tail_x is None:
        tail_x = x + bw // 2
    draw.polygon([(tail_x - 28, y + bh - 4), (tail_x, y + bh + 34),
                  (tail_x + 28, y + bh - 4)], fill=(255, 255, 255),
                 outline=(20, 20, 20))
    draw.text((x + 28, y + 16), text, font=font, fill=(20, 20, 20))


def main():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # ---- top caption band
    draw.rectangle([0, 0, W, 168], fill=(0, 0, 0))
    big = load_font(62)
    text_centered(draw, W // 2, 14, "I GAVE MY AI AGENT", big, (255, 255, 255))
    text_centered(draw, W // 2, 88, "ADMIN ACCESS", big, (255, 220, 60))

    # ---- office wall + floor
    draw.rectangle([0, 168, W, 836], fill=(176, 216, 235))
    draw.rectangle([0, 780, W, 836], fill=(196, 158, 110))
    draw.rectangle([0, 780, W, 792], fill=(150, 112, 70))
    # window with sun
    draw.rectangle([66, 210, 250, 380], fill=(255, 255, 255),
                   outline=(60, 60, 60), width=5)
    draw.rectangle([74, 218, 242, 372], fill=(135, 206, 250))
    draw.ellipse([188, 232, 228, 272], fill=(255, 235, 90))
    draw.line([(158, 218), (158, 372)], fill=(60, 60, 60), width=4)
    draw.line([(74, 295), (242, 295)], fill=(60, 60, 60), width=4)

    # ---- chart on the wall (right)
    draw_chart(draw, 748, 200, 230, 220)

    # ---- desk
    draw.rectangle([60, 640, 964, 700], fill=(139, 90, 43),
                   outline=(90, 55, 20), width=4)
    draw.rectangle([110, 700, 150, 836], fill=(110, 68, 30))
    draw.rectangle([874, 700, 914, 836], fill=(110, 68, 30))

    # ---- laptop on the desk (left)
    draw_laptop(draw, 100, 470, 260, 170)

    # ---- panicking human peeking over the desk (between laptop and robot)
    draw_human(draw, 440, 560, 0.9)

    # ---- the robot boss, standing ON the desk (centre-right)
    draw_robot(draw, 600, 330, 1.0)

    # ---- speech bubble from the robot
    draw_speech(draw, 380, 195, "I'M THE BOSS NOW", tail_x=600)

    # ---- bottom caption band
    draw.rectangle([0, 836, W, H], fill=(0, 0, 0))
    text_centered(draw, W // 2, 852, "IT PROMOTED ITSELF", big,
                  (255, 255, 255))
    text_centered(draw, W // 2, 926, "TO CEO", big, (255, 220, 60))

    # ---- write it out (deterministic PNG)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img.save(OUT_PATH, format="PNG", optimize=True)
    print("wrote", OUT_PATH, os.path.getsize(OUT_PATH), "bytes")


if __name__ == "__main__":
    main()
