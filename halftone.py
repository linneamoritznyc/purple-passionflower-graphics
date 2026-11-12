"""Passion flower designs in the pixel micrograph style.
Plates -> honeycomb halftone texture -> clipped into one huge crisp shape on a flat colour.
Plates come from plates/*.png if present (real photos, white = flower),
otherwise they are rendered from generate.py's passion flowers.
"""
import glob, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import generate as g

W, H, SS = 1800, 3680, 2
OUT = "halftone"

PAL = {
    "purple":   dict(field=(107, 76, 122), base=(58, 34, 62),  d1=(203, 214, 150), d2=(200, 182, 226)),
    "violet":   dict(field=(59, 31, 92),   base=(28, 16, 44),  d1=(237, 230, 200), d2=(169, 139, 214)),
    "lavender": dict(field=(205, 189, 235), base=(107, 63, 160), d1=(244, 240, 250), d2=(201, 215, 122)),
    "moss":     dict(field=(31, 42, 30),   base=(59, 31, 92),  d1=(205, 189, 235), d2=(203, 214, 150)),
}

# ------------------------------------------------------------ plates
def make_plates(n=5):
    files = sorted(glob.glob("plates/*.png")) + sorted(glob.glob("plates/*.jpg"))
    if files:
        plates = []
        for f in files:
            im = ImageOps.grayscale(Image.open(f))
            plates.append(ImageOps.autocontrast(im, cutoff=2))
        return plates
    plates = []
    for i in range(n):
        im = Image.new("RGB", (g.W * g.S, g.W * g.S), "#000000")
        g.flower(im, g.W / 2, g.W / 2, g.W * 0.48, 100 + i, petals=i % 2 == 0,
                 n_fil=120 + 20 * i, curl=1.0 + 0.3 * i)
        im = ImageOps.grayscale(im.resize((1200, 1200), Image.LANCZOS))
        plates.append(ImageOps.autocontrast(im, cutoff=1))
    return plates

# ------------------------------------------------------------ texture
def source(plates, rnd, closeup=False):
    src = Image.new("L", (W, H), 0)
    picks = [rnd.choice(plates)] if closeup else rnd.sample(plates, 3)
    for p in picks:
        size = rnd.randint(3400, 3900) if closeup else rnd.randint(1500, 2600)
        q = p.resize((size, size), Image.LANCZOS).rotate(rnd.choice([0, 90, 180, 270]))
        x = rnd.randint(-size // 3, W - size * 2 // 3)
        y = rnd.randint(-size // 3, H - size * 2 // 3)
        if closeup:
            x, y = (W - size) // 2, (H - size) // 2
        src.paste(Image.composite(q, src.crop((x, y, x + size, y + size)), q), (x, y))
    return src

def halftone(src, pal, colors=("d1", "d2"), cell=13):
    v = np.asarray(src.filter(ImageFilter.GaussianBlur(5)), dtype=float) / 255
    tex = Image.new("RGB", (W * SS, H * SS), pal["base"])
    d = ImageDraw.Draw(tex)
    for layer, key in enumerate(colors):
        off = cell / 2 if layer else 0
        row = 0
        y = off
        while y < H:
            x = (cell / 2 if row % 2 else 0) + off
            while x < W:
                val = v[min(H - 1, int(y)), min(W - 1, int(x))]
                if layer:  # second colour reads the inverse-ish mid tones so colours interleave
                    val = val * 0.85
                if val >= 0.12:
                    r = cell * 0.48 * val ** 0.6 * SS
                    cx, cy = x * SS, y * SS
                    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=pal[key])
                x += cell
            y += cell * 0.866
            row += 1
    return tex.resize((W, H), Image.LANCZOS)

# ------------------------------------------------------------ shapes (huge, run off the edges)
def mask(draw_fn):
    m = Image.new("L", (W // 2, H // 2), 0)
    draw_fn(ImageDraw.Draw(m), W // 2, H // 2)
    m = m.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(2))
    return m.point(lambda p: 255 if p > 127 else 0)

def petal_poly(cx, cy, ang, L, wid):
    left, right = [], []
    for i in range(61):
        t = i / 60
        w = math.sin(t * math.pi) ** 0.75 * wid
        px, py = cx + math.cos(ang) * t * L, cy + math.sin(ang) * t * L
        left.append((px - math.sin(ang) * w, py + math.cos(ang) * w))
        right.append((px + math.sin(ang) * w, py - math.cos(ang) * w))
    return left + right[::-1]

def shape_petal(d, w, h):          # one giant petal, diagonal
    d.polygon(petal_poly(-w * 0.15, h * 1.05, -1.05, h * 1.25, w * 0.55), fill=255)

def shape_bloom(d, w, h):          # ten-petal silhouette cropped by the right edge
    cx, cy = w * 0.85, h * 0.55
    for k in range(10):
        d.polygon(petal_poly(cx, cy, k * math.pi / 5 + 0.15, w * 0.95, w * 0.2), fill=255)
    d.ellipse([cx - w * .4, cy - w * .4, cx + w * .4, cy + w * .4], fill=255)

def shape_filament(d, w, h):       # one fat wavy filament, top to bottom
    pts = []
    for i in range(201):
        t = i / 200
        x = w * 0.5 + math.sin(t * math.pi * 2.3 + 0.4) * w * 0.33 * (0.4 + t)
        pts.append((x, -40 + t * (h + 80)))
    width = lambda t: w * (0.16 - 0.08 * t)
    left = [(x - width(i / 200), y) for i, (x, y) in enumerate(pts)]
    right = [(x + width(i / 200), y) for i, (x, y) in enumerate(pts)]
    d.polygon(left + right[::-1], fill=255)

def shape_stigma(d, w, h):         # the three-armed stigma, huge
    cx, cy = w * 0.5, h * 0.58
    for k in range(3):
        a = k * 2 * math.pi / 3 - math.pi / 2
        ex, ey = cx + math.cos(a) * w * 0.62, cy + math.sin(a) * w * 0.62
        d.line([(cx, cy), (ex, ey)], fill=255, width=int(w * 0.13))
        r = w * 0.2
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=255)
    d.ellipse([cx - w * .16, cy - w * .16, cx + w * .16, cy + w * .16], fill=255)

def shape_halfmoon(d, w, h):       # corona seen as a huge disc entering from below
    r = w * 0.9
    d.ellipse([w * 0.5 - r, h * 0.95 - r, w * 0.5 + r, h * 0.95 + r], fill=255)

# ------------------------------------------------------------ compose
def grain(im, rnd):
    a = np.asarray(im, dtype=float)
    n = np.random.default_rng(rnd.randint(0, 9999)).normal(0, 1, a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a * (1 + 0.03 * n), 0, 255).astype(np.uint8))

def design(name, plates, pal_key, shape=None, closeup=False, seed=0):
    rnd = random.Random(seed)
    pal = PAL[pal_key]
    src = source(plates, rnd, closeup)
    if closeup:
        tex = halftone(src, dict(pal, base=pal["field"]), colors=("d1",))
        out = tex
    else:
        tex = halftone(src, pal)
        out = Image.new("RGB", (W, H), pal["field"])
        out.paste(tex, (0, 0), mask(shape))
    out = grain(out, rnd)
    os.makedirs(OUT, exist_ok=True)
    out.save(f"{OUT}/{name}.png")
    return out

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
    plates = make_plates()
    jobs = [
        ("h01_petal_purple",     "purple",   shape_petal),
        ("h02_bloom_violet",     "violet",   shape_bloom),
        ("h03_filament_moss",    "moss",     shape_filament),
        ("h04_stigma_purple",    "purple",   shape_stigma),
        ("h05_halfmoon_lavender","lavender", shape_halfmoon),
        ("h06_closeup_violet",   "violet",   None),
        ("h07_filament_lavender","lavender", shape_filament),
        ("h08_closeup_moss",     "moss",     None),
    ]
    mocks = []
    for i, (name, pal, shp) in enumerate(jobs):
        im = design(name, plates, pal, shp, closeup=shp is None, seed=i + 1)
        mocks.append(mock(im))
    sheet = Image.new("RGB", (640 * 4 + 30, 1266 * 2 + 30), "#f4f1ec")
    for i, m in enumerate(mocks):
        sheet.paste(m, (10 + (i % 4) * 645, 10 + (i // 4) * 1276), m)
    sheet.resize((sheet.width // 2, sheet.height // 2), Image.LANCZOS).save("halftone_sheet.png")
    print("done")
