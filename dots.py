"""Passion flower dot cases, made from a photo.
python dots.py  -> dots/*.png (1800x3680) + dots_sheet.png
"""
import os
import numpy as np
from PIL import Image, ImageDraw

W, H, SS, CELL = 1800, 3680, 2, 14
PHOTO = "plates/passiflora.png"

# key colours in the photo: lilac petal, violet ring, white filament, pale green stamen, mauve centre
KEYS = np.array([(160, 150, 205), (90, 60, 150), (235, 232, 245), (225, 225, 170), (150, 110, 140)], float)

CASES = [
    dict(name="d1_olive_full",   bg=(34, 48, 26),  scale=7.0, rot=0,  pos=(0.55, 0.5),
         cols=[(190, 170, 230), (120, 70, 170), (240, 236, 248), (214, 226, 140), (150, 96, 150)]),
    dict(name="d2_purple_crop",  bg=(58, 34, 74),  scale=9.5, rot=20, pos=(0.42, 0.55),
         cols=[(190, 170, 230), (30, 16, 44), (240, 236, 248), (214, 226, 140), (150, 96, 150)]),
    dict(name="d3_olive_mono",   bg=(34, 48, 26),  scale=7.5, rot=0,  pos=(0.5, 0.45),
         cols=[(203, 214, 150)] * 5),
    dict(name="d4_blue",         bg=(55, 128, 184), scale=9.0, rot=-35, pos=(0.5, 0.48),
         cols=[(214, 226, 140), (26, 44, 82), (214, 226, 140), (150, 196, 232), (150, 196, 232)]),
]

def place(photo, scale, rot, pos):
    p = photo.resize((int(photo.width * scale), int(photo.height * scale)), Image.LANCZOS)
    # fade the photo's cut edges to black so the crop never shows as a hard line
    yy, xx = np.mgrid[0:p.height, 0:p.width]
    e = np.minimum.reduce([xx, yy, p.width - 1 - xx, p.height - 1 - yy]) / (0.12 * min(p.size))
    p = Image.fromarray((np.asarray(p, float) * np.clip(e, 0, 1)[..., None] ** 1.5).astype(np.uint8))
    if rot:
        p = p.rotate(rot, Image.BICUBIC, expand=True, fillcolor=(0, 0, 0))
    can = Image.new("RGB", (W, H), (0, 0, 0))
    can.paste(p, (int(W * pos[0] - p.width / 2), int(H * pos[1] - p.height / 2)))
    return np.asarray(can, float) / 255

def mask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    m = np.clip((lum - 0.18) / 0.5, 0, 1)
    leaf = (g > r) & (g > b) & (lum < 0.45)
    m[leaf] = 0
    return m

def render(case, photo):
    a = place(photo, case["scale"], case["rot"], case["pos"])
    m = mask(a)
    im = Image.new("RGB", (W * SS, H * SS), case["bg"])
    d = ImageDraw.Draw(im)
    row, y = 0, CELL / 2
    while y < H:
        x = CELL / 2 + (CELL / 2 if row % 2 else 0)
        while x < W:
            yi, xi = int(y), int(x)
            v = m[yi, xi]
            if v >= 0.08:
                c = a[yi, xi] * 255
                k = int(((KEYS - c) ** 2).sum(1).argmin())
                r = CELL * 0.5 * v ** 0.55 * SS
                d.ellipse([x * SS - r, y * SS - r, x * SS + r, y * SS + r], fill=case["cols"][k])
            x += CELL
        y += CELL * 0.866
        row += 1
    im = im.resize((W, H), Image.LANCZOS)
    arr = np.asarray(im, float)
    n = np.random.default_rng(1).normal(0, 1, arr.shape[:2])[..., None]
    return Image.fromarray(np.clip(arr * (1 + 0.03 * n), 0, 255).astype(np.uint8))

def mock(im):
    w, h = 600, 1226
    im = im.resize((w, h), Image.LANCZOS)
    m = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    mk = Image.new("L", (w, h), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, w, h], 80, fill=255)
    m.paste(im, (20, 20), mk)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([45, 45, 255, 255], 50, fill=(25, 24, 28, 240))
    for cx, cy in [(100, 100), (100, 200), (200, 150)]:
        d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=(12, 12, 14, 255))
    return m

if __name__ == "__main__":
    photo = Image.open(PHOTO).convert("RGB")
    os.makedirs("dots", exist_ok=True)
    sheet = Image.new("RGB", (640 * 4 + 30, 1266 + 20), "#f4f1ec")
    for i, c in enumerate(CASES):
        im = render(c, photo)
        im.save(f"dots/{c['name']}.png")
        m = mock(im); sheet.paste(m, (10 + i * 645, 10), m)
    sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save("dots_sheet.png")
    print("done")
