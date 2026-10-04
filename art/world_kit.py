"""Shared helpers for world.py and props.py: in-memory rendering, wrapped (seamless) drawing,
periodic lines, blobs, grain, and the world palette."""
import io, math, random, zlib
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
import pymupdf
import common
from common import Box, SCALE
import lib
from lib import Col, ell, bez
import style3
from style3 import T, stroke, fill, form, shape, hatch, offset_shadow, dot, C, poly


def c(h, a=None):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return Col(0.3 * r + 0.59 * g + 0.11 * b, h, a)


def to_image(w_px, h_px, draw, seed):
    buf = io.BytesIO()
    w, h = w_px / SCALE, h_px / SCALE
    cv = canvas.Canvas(buf, pagesize=(w, h)); lib.set_canvas(cv)
    style3._R.seed(seed if isinstance(seed, int) else zlib.crc32(seed.encode()))
    draw(Box(w, h)); cv.showPage(); cv.save()
    doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=True)
    im = Image.open(io.BytesIO(pix.tobytes("png"))).convert("RGBA"); doc.close()
    return im


def wrapped(fn, pw, ph, seed, xs=True, ys=True):
    """draw fn() at every periodic offset with identical randomness, so the result tiles"""
    for dx in ((-pw, 0, pw) if xs else (0,)):
        for dy in ((-ph, 0, ph) if ys else (0,)):
            style3._R.seed(seed)
            with T(dx, dy): fn()


def clip(pts):
    class _C:
        def __enter__(s): C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
        def __exit__(s, *e): C.restoreState()
    return _C()


def rect(x, y, w, h): return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def blob(x, y, rx, ry, rnd, n=9, k=0.28, rot=0):
    a0 = rnd.uniform(0, math.tau)
    ang = [a0 + math.tau * (i + rnd.uniform(-0.3, 0.3)) / n for i in range(n)]
    base = [(math.cos(a) * rx * (1 + rnd.uniform(-k, k)), math.sin(a) * ry * (1 + rnd.uniform(-k, k))) for a in ang]
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    base = [(x + px * cr - py * sr, y + px * sr + py * cr) for px, py in base]
    out = []
    for i in range(n):
        p0 = base[i]; p1 = base[(i + 1) % n]; p2 = base[(i + 2) % n]
        m0 = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2); m1 = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        out += bez(m0, p1, p1, m1, 5)[:-1]
    return out


def chunk(x, y, rx, ry, rnd, n=7, k=0.22, rot=0):
    """angular rock chunk"""
    a0 = rnd.uniform(0, math.tau)
    pts = []
    for i in range(n):
        a = a0 + math.tau * i / n + rnd.uniform(-0.25, 0.25)
        pts.append((math.cos(a) * rx * (1 + rnd.uniform(-k, k)), math.sin(a) * ry * (1 + rnd.uniform(-k, k))))
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(x + px * cr - py * sr, y + px * sr + py * cr) for px, py in pts]


def pebble(pts, g, w=0.35, sh=0.16, ground=0.18, gd=(0.5, -0.45)):
    if ground: fill([(px + gd[0], py + gd[1]) for px, py in pts], c("#000000"), ground)
    form(pts, g, w=w, sdx=-0.7, sdy=0.6, sh=sh)


def periodic(x0, x1, period, rnd, amp=0.5, harm=(1, 2, 3)):
    """f(x) periodic in `period` with random harmonics"""
    terms = [(h, amp * rnd.uniform(0.4, 1.0) / h ** 0.6, rnd.uniform(0, math.tau)) for h in harm]
    return lambda x: sum(a * math.sin(math.tau * h * x / period + p) for h, a, p in terms)


def pband(x0, x1, yf, w, g=None, period=32.0, wf=None, step=0.5):
    """ribbon along y=yf(x) with width w (+ periodic wf); fill colour g (None: ink)"""
    xs = [x0 + i * step for i in range(int((x1 - x0) / step) + 1)]
    top, bot = [], []
    for x in xs:
        ww = w * (1 + (wf(x) if wf else 0))
        top.append((x, yf(x) + ww / 2)); bot.append((x, yf(x) - ww / 2))
    pts = top + bot[::-1]
    C.saveState(); C.setFillColor(lib.G(g if g is not None else c("#2e2d33")))
    if g is None: C.setFillAlpha(0.85)
    elif getattr(g, "alpha", None) is not None: C.setFillAlpha(g.alpha)
    C.drawPath(poly(pts), fill=1, stroke=0); C.restoreState()


def pline(x0, x1, yf, w=0.5, period=32.0, rnd=None, g=None):
    rnd = rnd or random.Random(1)
    wf = periodic(x0, x1, period, rnd, 0.35, (2, 5))
    pband(x0, x1, yf, w, g, period, wf)


def grain(w, h, seed, strength=0.10, period=(64, 64)):
    """seamless paper grain (periodic in period), as a multiplier array h x w"""
    pw, ph = period
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (ph, pw))
    F = np.fft.fft2(n)
    fy = np.fft.fftfreq(ph)[:, None]; fx = np.fft.fftfreq(pw)[None, :]
    r = np.sqrt(fx ** 2 + fy ** 2)
    soft = np.real(np.fft.ifft2(F * np.exp(-(r / 0.06) ** 2)))
    fine = np.real(np.fft.ifft2(F * np.exp(-(r / 0.35) ** 2)))
    soft /= soft.std() + 1e-9; fine /= fine.std() + 1e-9
    g = 0.55 * soft + 0.45 * fine
    tiled = np.tile(g, (h // ph + 1, w // pw + 1))[:h, :w]
    return 1 + strength * tiled * 0.5


def apply_grain(im, seed, strength=0.10, period=(64, 64)):
    a = np.asarray(im).astype(np.float32)
    m = grain(im.width, im.height, seed, strength, period)
    a[..., :3] = np.clip(a[..., :3] * m[..., None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def over(base, top):
    out = base.copy(); out.alpha_composite(top); return out
