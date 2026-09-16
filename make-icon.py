#!/usr/bin/env python3
"""Generate the 512x512 AIM Terminal icon (Hanseatenblau + Gold)."""

from PIL import Image, ImageDraw

BG = (5, 23, 41)
GOLD = (202, 169, 96)
GOLD_DIM = (150, 124, 70)

SIZE = 512
SCALE = 4
S = SIZE * SCALE

img = Image.new("RGB", (S, S), BG)
d = ImageDraw.Draw(img)


def r(x):
    return int(round(x * SCALE))


margin = 96
d.rounded_rectangle(
    [r(margin), r(margin), r(SIZE - margin), r(SIZE - margin)],
    radius=r(28),
    outline=GOLD,
    width=r(10),
)

titlebar_y = margin + 58
d.line([r(margin + 1), r(titlebar_y), r(SIZE - margin - 1), r(titlebar_y)], fill=GOLD_DIM, width=r(6))
for i, cx in enumerate((margin + 34, margin + 60, margin + 86)):
    d.ellipse([r(cx - 8), r(titlebar_y - 34), r(cx + 8), r(titlebar_y - 18)], fill=GOLD_DIM)

chev = [
    (margin + 60, 232),
    (margin + 60, 268),
    (margin + 118, 288),
    (margin + 118, 212),
]
d.polygon([(r(x), r(y)) for x, y in chev], fill=GOLD)
d.rectangle([r(margin + 136), r(272), r(margin + 220), r(290)], fill=GOLD)

bar_base = 400
for i, h in enumerate((36, 68, 96)):
    x0 = margin + 60 + i * 54
    d.rectangle([r(x0), r(bar_base - h), r(x0 + 34), r(bar_base)], fill=GOLD_DIM if i < 2 else GOLD)

img = img.resize((SIZE, SIZE), Image.LANCZOS)
img.save("/home/opencode/workspace/aimighty-terminal/icon.png")
print("wrote icon.png", img.size)
