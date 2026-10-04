import math
from icons_kit import *


def pick(x, y, s=1.0, rot=-35, head=IRON):
    with T(x, y, s, rot=rot):
        tube([(0, -12), (0, 8)], 2.4, 2.8, WOOD, W, sh=0.18)
        top = bez((-11, 6), (-5, 12), (5, 12), (11, 6))
        bot = bez((11, 6), (5, 8.5), (-5, 8.5), (-11, 6))
        form(top + bot[1:], head, W, sdx=0, sdy=-1.2, sh=0.25)
        hl(bez((-8, 7.5), (-4, 10.5), (4, 10.5), (8, 7.5)), 0.5, 0.6)


def hammer(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        tube([(0, -12), (0, 6)], 2.4, 2.6, WOOD, W, sh=0.18)
        form(rect(-5.5, 5, 11, 6), IRON, W, sdx=0, sdy=-1, sh=0.25)


def axe(x, y, s=1.0, rot=0, head=STEEL):
    with T(x, y, s, rot=rot):
        tube([(0, -13), (0, 9)], 2.2, 2.6, WOOD_L, W, sh=0.18)
        h = [(-4, 10)] + bez((-4, 10), (0, 11), (3, 11), (6, 12.5)) + bez((6, 12.5), (9, 9), (9, 4), (6.5, 0.5)) + [(1.2, 4), (-4, 6)]
        form(h, head, W, sdx=-1, sdy=-0.6, sh=0.25)
        stroke(bez((6, 12.5), (9, 9), (9, 4), (6.5, 0.5)), 0.8, g=STEEL_L, alpha=0.9)


def bolt_arrow(x, y, s=1.0, rot=0, fletch=RED, head=STEEL, length=24):
    with T(x, y, s, rot=rot):
        L = length / 2
        tube([(-L, 0), (L - 3, 0)], 1.4, 1.4, WOOD_L, W * 0.8, sh=0)
        form([(L - 4, -2.4), (L + 3, 0), (L - 4, 2.4)], head, W * 0.8, sh=0.2)
        for sy in (-1, 1):
            shape([(-L, 0), (-L + 5, 0), (-L + 2, sy * 3.4), (-L - 1.5, sy * 3.4)], fletch, W * 0.6)


def zig(x0, y0, x1, y1, n=4, amp=3.0, seed=1):
    import random
    r = random.Random(seed)
    pts = [(x0, y0)]
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
    for i in range(1, n):
        t = i / n
        a = amp * (1 if i % 2 else -1) * r.uniform(0.6, 1.0)
        pts.append((x0 + dx * t + nx * a, y0 + dy * t + ny * a))
    pts.append((x1, y1))
    return pts


def lightning(pts, w=2.2, core="#ffffff", halo="#7cc4ff"):
    line(pts, halo, w * 2.6, 0.35)
    line(pts, halo, w * 1.4, 0.8)
    line(pts, core, w * 0.6, 1.0)


def bigbolt(cx, cy, s=1.0):
    with T(cx, cy, s):
        p = [(2, 13), (-6, 0), (-0.5, 0.5), (-4, -13), (7, 3), (1, 2.5), (6, 13)]
        glow(0, 0, 14, "#7cc4ff", 0.45)
        shape(p, K("#f4fbff", 0.97), W)
        flat([(2.5, 11.5), (-3.5, 1.2), (-1, 1.4)], "#7cc4ff", 0.6)


def fireball(cx, cy, r, ang=0, tail=1.0):
    with T(cx, cy, 1.0, rot=ang):
        glow(0, 0, r * 2.2, "#ff9030", 0.55)
        t = [(r * 0.2, r)] + bez((r * 0.2, r), (-r * 1.5, r * 1.1), (-r * 2.6 * tail, r * 0.6), (-r * 3.6 * tail, 0)) + \
            bez((-r * 3.6 * tail, 0), (-r * 2.6 * tail, -r * 0.6), (-r * 1.5, -r * 1.1), (r * 0.2, -r))
        flat(t, "#f06a1c", 0.85)
        flat(ell(0, 0, r, r, 24), "#ff9a30")
        flat(ell(r * 0.15, 0, r * 0.65, r * 0.6, 20), "#ffe48a")
        flat(ell(r * 0.3, 0, r * 0.3, r * 0.28, 12), "#fffbe8")


def snowflake(cx, cy, r, w=1.0, col="#f2fbff"):
    for i in range(6):
        a = math.radians(90 + i * 60)
        ex, ey = cx + math.cos(a) * r, cy + math.sin(a) * r
        line([(cx, cy), (ex, ey)], "#5aa8e8", w * 2.4, 0.5)
        line([(cx, cy), (ex, ey)], col, w)
        for k in (0.5, 0.75):
            mx, my = cx + math.cos(a) * r * k, cy + math.sin(a) * r * k
            for da in (-50, 50):
                b = a + math.radians(da)
                line([(mx, my), (mx + math.cos(b) * r * 0.25, my + math.sin(b) * r * 0.25)], col, w * 0.8)


def shard(cx, cy, l, wd, ang, g=None):
    with T(cx, cy, 1.0, rot=ang):
        p = [(-l / 2, 0), (-l * 0.1, wd / 2), (l / 2, 0), (-l * 0.1, -wd / 2)]
        shape(p, g or K("#cfeeff", 0.92), W * 0.8)
        flat([(-l * 0.1, wd / 2 * 0.8), (l / 2 * 0.9, 0), (-l * 0.1, 0)], "#ffffff", 0.6)


def cloud(cx, cy, s, g, dark=False):
    with T(cx, cy, s):
        pts = []
        for (x, y, r) in ((-8, 0, 5), (-3, 4, 6), (4, 4, 6), (9, 0, 5)):
            pass
        blob = bez((-13, -3), (-16, 3), (-10, 7), (-7, 5)) + bez((-7, 5), (-6, 11), (2, 12), (3, 7)) + \
            bez((3, 7), (6, 11), (13, 9), (11, 3)) + bez((11, 3), (16, 2), (15, -4), (10, -4)) + [(-13, -3)]
        form(blob, g, W, sdx=0, sdy=2, sh=0.3)
        hl(bez((-9, 4), (-7, 7), (-3, 9), (0, 8)), 0.6, 0.4)


def flame_big(x, y, h, cold=False, lean=0.0, wide=0.42):
    wid = h * wide
    outer = bez((x, y), (x - wid * 1.2, y + h * 0.15), (x - wid * 0.5, y + h * 0.6), (x + lean, y + h)) + \
        bez((x + lean, y + h), (x + wid * 0.2, y + h * 0.7), (x + wid * 0.9, y + h * 0.6), (x + wid * 0.6, y + h * 0.4)) + \
        bez((x + wid * 0.6, y + h * 0.4), (x + wid * 1.3, y + h * 0.2), (x + wid * 0.6, y), (x, y))
    mid = bez((x, y + h * 0.04), (x - wid * 0.8, y + h * 0.15), (x - wid * 0.3, y + h * 0.5), (x + lean * 0.7, y + h * 0.72)) + \
        bez((x + lean * 0.7, y + h * 0.72), (x + wid * 0.4, y + h * 0.45), (x + wid * 0.8, y + h * 0.15), (x, y + h * 0.04))
    inner = bez((x, y + h * 0.06), (x - wid * 0.4, y + h * 0.15), (x - wid * 0.15, y + h * 0.35), (x + lean * 0.4, y + h * 0.45)) + \
        bez((x + lean * 0.4, y + h * 0.45), (x + wid * 0.25, y + h * 0.3), (x + wid * 0.4, y + h * 0.1), (x, y + h * 0.06))
    cols = ("#5ab0ff", "#bfe6ff", "#ffffff") if cold else ("#e2481a", "#ff9a2a", "#ffe880")
    flat(outer, cols[0]); flat(mid, cols[1]); flat(inner, cols[2])
    stroke(outer, 0.5, closed=True, g=K("#5a1a08" if not cold else "#1a3a6a", 0.15), alpha=0.7)
    return outer


def charge(x, y, s=1.0, rot=0, lit=True):
    with T(x, y, s, rot=rot):
        for k, dx in enumerate((-4.2, 0, 4.2)):
            r = rrect(dx - 2.2, -8, 4.4, 15, 1.6)
            form(r, K("#b8452a", 0.4) if k != 1 else K("#cf5a34", 0.5), W * 0.8, sdx=-0.8, sdy=0, sh=0.2)
        for yy in (-4, 3):
            stroke([(-6.6, yy), (6.6, yy + 0.4)], 1.0, g=K("#2a1a10", 0.15))
        fuse = bez((0, 7), (0, 11), (4, 10), (5, 14))
        stroke(fuse, 0.8, g=K("#3a2a1a", 0.2))
        if lit:
            glow(5, 14, 5, "#ffb040", 0.7)
            sparkle(5, 14, 3.2, "#fff2a0")
