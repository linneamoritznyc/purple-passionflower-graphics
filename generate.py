"""Passiflora studies: code-generated designs from the passion flower corona.
Renders 1200x2400 print files + case mockups into files/.
"""
import math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, S = 1200, 2400, 2
C = dict(
    night="#14111A", moss="#1F2A1E", violet="#3B1F5C", deep="#24123A",
    purple="#6B3FA0", lilac="#A98BD6", lavender="#CDBDEB", white="#F4F0FA",
    cream="#EDE6C8", lime="#C9D77A", wine="#5A1636", sage="#B9C8B0",
)

def rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def new(bg):
    im = Image.new("RGB", (W*S, H*S), C[bg]); return im, ImageDraw.Draw(im)

BANDS = ["deep", "white", "purple", "white", "lilac", "lavender", "white"]

def filament(d, x, y, ang, length, width, rnd, curl=1.0, bands=BANDS):
    """One corona filament: banded colour along its length, wavier toward the tip."""
    n = 70
    ph, fq = rnd.uniform(0, 6.28), rnd.uniform(2.5, 5)
    pts = []
    for i in range(n + 1):
        t = i / n
        r = t * length
        wob = math.sin(ph + t * fq * math.pi) * (t ** 1.6) * length * 0.09 * curl
        px = x + math.cos(ang) * r - math.sin(ang) * wob
        py = y + math.sin(ang) * r + math.cos(ang) * wob
        pts.append((px * S, py * S))
    nb = len(bands)
    for i in range(n):
        t = i / n
        col = C[bands[min(nb - 1, int(t * nb))]]
        w = max(1, int(width * S * (1 - 0.55 * t)))
        d.line([pts[i], pts[i+1]], fill=col, width=w)
        d.ellipse([pts[i+1][0]-w/2, pts[i+1][1]-w/2, pts[i+1][0]+w/2, pts[i+1][1]+w/2], fill=col)

def petal(d, cx, cy, ang, length, wid, col):
    pts = []
    for i in range(41):
        t = i / 40
        r = t * length
        w = math.sin(t * math.pi) ** 0.8 * wid
        pts.append((cx + math.cos(ang)*r - math.sin(ang)*w, cy + math.sin(ang)*r + math.cos(ang)*w))
    for i in range(40, -1, -1):
        t = i / 40
        r = t * length
        w = math.sin(t * math.pi) ** 0.8 * wid
        pts.append((cx + math.cos(ang)*r + math.sin(ang)*w, cy + math.sin(ang)*r - math.cos(ang)*w))
    d.polygon([(px*S, py*S) for px, py in pts], fill=C[col])

def centre(d, cx, cy, r, rnd):
    # dark ring, then the cream anthers and three stigmas
    d.ellipse([(cx-r)*S, (cy-r)*S, (cx+r)*S, (cy+r)*S], fill=C["deep"])
    d.ellipse([(cx-r*.55)*S, (cy-r*.55)*S, (cx+r*.55)*S, (cy+r*.55)*S], fill=C["lime"])
    for k in range(5):
        a = k * 2*math.pi/5 + 0.3
        ax, ay = cx + math.cos(a)*r*.7, cy + math.sin(a)*r*.7
        d.line([(cx*S, cy*S), (ax*S, ay*S)], fill=C["cream"], width=int(r*.12*S))
        d.ellipse([(ax-r*.22)*S, (ay-r*.12)*S, (ax+r*.22)*S, (ay+r*.12)*S], fill=C["cream"])
    for k in range(3):
        a = k * 2*math.pi/3 - math.pi/2
        sx, sy = cx + math.cos(a)*r*.45, cy + math.sin(a)*r*.45
        d.line([(cx*S, cy*S), (sx*S, sy*S)], fill=C["wine"], width=int(r*.07*S))
        d.ellipse([(sx-r*.1)*S, (sy-r*.1)*S, (sx+r*.1)*S, (sy+r*.1)*S], fill=C["wine"])

def flower(im, cx, cy, R, seed, petals=True, n_fil=110, curl=1.0, bands=BANDS):
    rnd = random.Random(seed); d = ImageDraw.Draw(im)
    if petals:
        for k in range(10):
            a = k * 2*math.pi/10 + rnd.uniform(-.05, .05)
            petal(d, cx, cy, a, R*1.05, R*0.2, "lavender" if k % 2 else "lilac")
    for k in range(n_fil):
        a = k * 2*math.pi/n_fil + rnd.uniform(-.03, .03)
        filament(d, cx, cy, a, R*rnd.uniform(.85, 1.0), R*0.022, rnd, curl, bands)
    centre(d, cx, cy, R*0.2, rnd)

def ikat(im, amp=26, seed=0):
    """Horizontal ikat smear: rows of the image slide sideways by small random amounts."""
    a = np.array(im)
    rng = np.random.default_rng(seed)
    h = a.shape[0]
    noise = rng.normal(0, 1, h)
    noise = np.convolve(noise, np.ones(3)/3, mode="same")
    for y in range(h):
        a[y] = np.roll(a[y], int(noise[y] * amp), axis=0)
    return Image.fromarray(a)

def save(im, name):
    os.makedirs("files", exist_ok=True); os.makedirs("mockups", exist_ok=True)
    im = im.resize((W, H), Image.LANCZOS)
    im.save(f"files/{name}.png")
    m = Image.new("RGBA", (W+120, H+120), (0, 0, 0, 0))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W, H], 170, fill=255)
    m.paste(Image.new("RGBA", (W, H), (0, 0, 0, 90)), (75, 85), mask)
    m = m.filter(ImageFilter.GaussianBlur(22)); m.paste(im, (60, 60), mask)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([110, 110, 560, 560], 110, fill=(30, 28, 34, 235))
    for cx, cy in [(225, 225), (225, 445), (445, 335)]:
        d.ellipse([cx-85, cy-85, cx+85, cy+85], fill=(15, 15, 18, 255))
        d.ellipse([cx-45, cy-45, cx+45, cy+45], fill=(50, 52, 66, 255))
    m.save(f"mockups/{name}_mock.png")

# ------------------------------------------------------------- designs
def corona():                      # one full bloom, low on the case
    im, _ = new("moss"); flower(im, 600, 1500, 620, 1); save(im, "01_corona")

def cropped():                     # huge bloom cut by the edge
    im, _ = new("night"); flower(im, 1150, 1300, 1150, 2, n_fil=170); save(im, "02_cropped_bloom")

def fringe():                      # filaments hang like fringe from the top
    im, d = new("violet"); rnd = random.Random(3)
    for k in range(60):
        x = 20 + k * 19.5
        filament(d, x, -20, math.pi/2 + rnd.uniform(-.04, .04), rnd.uniform(1700, 2400), 16, rnd, 1.4,
                 ["night", "white", "purple", "white", "lilac", "lavender", "white", "lilac"])
    save(im, "03_fringe")

def ikat_bloom():                  # the bloom smeared like ikat thread
    im, _ = new("deep"); flower(im, 600, 1200, 700, 4); save(ikat(im, 30, 4), "04_ikat_bloom")

def corona_only():                 # only the filament crown, no petals, airy
    im, _ = new("white")
    flower(im, 600, 1250, 680, 5, petals=False, n_fil=140, curl=1.6,
           bands=["deep", "purple", "lilac", "purple", "lavender", "lilac", "deep"])
    save(im, "05_corona_only")

def heart():                       # extreme close-up of the centre
    im, d = new("lavender"); rnd = random.Random(6)
    for k in range(200):
        a = k * 2*math.pi/200
        filament(d, 600, 1300, a, 1400, 30, rnd, .8)
    centre(d, 600, 1300, 420, rnd); save(im, "06_heart")

def field():                       # scattered blooms, a vine of them
    im, _ = new("moss")
    for i, (x, y, r) in enumerate([(250, 500, 260), (900, 900, 330), (350, 1500, 300), (950, 1950, 280), (200, 2250, 200)]):
        flower(im, x, y, r, 10+i, n_fil=80)
    save(im, "07_field")

def ikat_fringe():                 # fringe, smeared hard
    im, d = new("night"); rnd = random.Random(8)
    for k in range(45):
        x = 30 + k * 26
        filament(d, x, 2450, -math.pi/2 + rnd.uniform(-.05, .05), rnd.uniform(1200, 2300), 22, rnd, 1.2,
                 ["purple", "white", "lilac", "white", "lavender", "white", "lime"])
    save(ikat(im, 45, 8), "08_ikat_fringe")

if __name__ == "__main__":
    for f in [corona, cropped, fringe, ikat_bloom, corona_only, heart, field, ikat_fringe]:
        f()
    fs = sorted(f for f in os.listdir("mockups") if f.endswith("_mock.png"))
    sheet = Image.new("RGB", (330*4+50, 660*2+30), "#f4f1ec")
    for i, f in enumerate(fs):
        t = Image.open("mockups/"+f).resize((330, 660))
        sheet.paste(t, (10+(i % 4)*340, 10+(i//4)*670), t)
    sheet.save("sheet.png"); print("done")
