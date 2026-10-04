"""Automap and minimap art: the paper sheet, the round minimap, crayon fills and the pencil map symbols."""
import math, random
import common
from icons_kit import *

MAP = []
GRAPHITE = 0.12


def art(name, w, h, paper=False):
    def deco(fn):
        MAP.append((name, w, h, fn, paper)); return fn
    return deco


def ragged(cx, cy, rx, ry, seed, n=90, amp=0.012):
    r = random.Random(seed)
    k = [1 + r.uniform(-amp, amp) for _ in range(n)]
    for _ in range(3):
        k = [(k[i - 1] + k[i] + k[(i + 1) % n]) / 3 for i in range(n)]
    return [(cx + math.cos(2 * math.pi * i / n) * rx * k[i], cy + math.sin(2 * math.pi * i / n) * ry * k[i]) for i in range(n)]


def torn_rect(x, y, w, h, seed, step=9.0, amp=1.6):
    r = random.Random(seed)
    pts = []
    for (ax, ay), (bx, by) in [((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))]:
        n = max(2, int(math.hypot(bx - ax, by - ay) / step))
        nx, ny = (by - ay), -(bx - ax)
        L = math.hypot(nx, ny) or 1
        for i in range(n):
            t = i / n
            j = r.uniform(-amp, amp)
            pts.append((ax + (bx - ax) * t + nx / L * j, ay + (by - ay) * t + ny / L * j))
    return pts


# ------------------------------------------------------------------ the sheet behind the Tab map
@art("map_sheet", 1600, 1000, True)
def map_sheet(b):
    m = 10
    sheet = torn_rect(m, m, b.w - 2 * m, b.h - 2 * m, 11)
    fill([(x + 3, y - 3) for x, y in sheet], 0.0, 0.25)
    flat(sheet, "#dcc89a")
    C.saveState(); C.clipPath(poly(sheet), stroke=0, fill=0)
    for k in range(10):
        flat(torn_rect(m + k * 2.4, m + k * 2.4, b.w - 2 * (m + k * 2.4), b.h - 2 * (m + k * 2.4), 20 + k), "#f1e2bb", 0.06)
    for fx in (b.w / 3, 2 * b.w / 3):
        line([(fx, m), (fx + 1.5, b.h - m)], "#8a6f44", 0.5, 0.35)
        line([(fx + 1.2, m), (fx + 2.7, b.h - m)], "#fff4d8", 0.5, 0.35)
    line([(m, b.h / 2), (b.w - m, b.h / 2 - 1)], "#8a6f44", 0.5, 0.3)
    r = random.Random(5)
    for _ in range(9):
        cx, cy = r.uniform(60, b.w - 60), r.uniform(60, b.h - 60)
        fill(ragged(cx, cy, r.uniform(8, 22), r.uniform(5, 14), r.random(), 30, 0.25), K("#b49866", 0.55), 0.18)
    C.restoreState()
    stroke(sheet, W * 1.3, closed=True, g=GRAPHITE)
    rose(b.w - 52, b.h - 58, 26)


def rose(cx, cy, r):
    """compass rose, north pointing up the sheet"""
    stroke(ragged(cx, cy, r * 0.62, r * 0.62, 3, 40, 0.02), W * 0.7, closed=True, g=GRAPHITE)
    for a, L in ((90, 1.0), (270, 0.7), (0, 0.7), (180, 0.7)):
        dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
        px, py = -dy, dx
        tip = (cx + dx * r * L, cy + dy * r * L)
        wing = 0.16 * r
        left = [(cx + px * wing, cy + py * wing), tip, (cx, cy)]
        right = [(cx - px * wing, cy - py * wing), tip, (cx, cy)]
        shape(left, K("#7a2a20", 0.3) if a == 90 else INK, W * 0.6)
        shape(right, PARCH if a != 90 else K("#c4553a", 0.5), W * 0.6)
    dot(cx, cy, 1.4, 0.0)
    nx, ny = cx, cy + r * 1.22
    stroke([(nx - 3, ny - 4), (nx - 3, ny + 4), (nx + 3, ny - 4), (nx + 3, ny + 4)], W * 0.8, g=GRAPHITE)


# ------------------------------------------------------------------ round minimap
MINI = 280
MINI_R = 118  # px radius of the paper disc the map is clipped to


@art("minimap_disc", MINI, MINI, True)
def minimap_disc(b):
    c = b.w / 2
    r = MINI_R / common.SCALE
    flat(ragged(c, c, r + 2, r + 2, 7, 80, 0.01), "#dcc89a")
    for k in range(8):
        flat(ragged(c, c, r - k * 2.5, r - k * 2.5, 30 + k, 60, 0.02), "#f1e2bb", 0.07)


@art("minimap_frame", MINI, MINI)
def minimap_frame(b):
    c = b.w / 2
    r0 = MINI_R / common.SCALE
    r1 = r0 + 13
    outer = ragged(c, c, r1, r1, 13, 90, 0.008)
    inner = ragged(c, c, r0, r0, 17, 90, 0.008)
    C.saveState()
    p = C.beginPath()
    for ring in (outer, inner):
        p.moveTo(*ring[0]); [p.lineTo(*q) for q in ring[1:]]; p.close()
    C.clipPath(p, stroke=0, fill=0, fillMode=0)
    S.fill(rect(0, 0, b.w, b.h), WOOD)
    hatch(rect(0, 0, b.w, c), 1.4, 35, 0.35, alpha=0.45)
    for k in range(18):
        a = 2 * math.pi * k / 18
        line([(c + math.cos(a) * (r0 + 1), c + math.sin(a) * (r0 + 1)), (c + math.cos(a + 0.12) * (r1 - 1), c + math.sin(a + 0.12) * (r1 - 1))],
             "#2c1a0e", 0.45, 0.5)
    C.restoreState()
    stroke(outer, W * 1.1, closed=True, g=GRAPHITE)
    stroke(inner, W * 0.9, closed=True, g=GRAPHITE)
    for a in (45, 135, 225, 315):
        x, y = c + math.cos(math.radians(a)) * (r0 + 6.5), c + math.sin(math.radians(a)) * (r0 + 6.5)
        rivet(x, y, 1.5, IRON_L)
    tx, ty = c, c + r1 - 1
    shape([(tx - 6, ty - 3), (tx + 6, ty - 3), (tx, ty + 7)], K("#7a2a20", 0.3), W * 0.8)


# ------------------------------------------------------------------ crayon fills tiled under the explored ground
def swatch(b, col):
    fill(rect(-4, -4, b.w + 8, b.h + 8), col)


@art("map_floor", 256, 256)
def map_floor(b): swatch(b, K("#c9ab74", 0.75))


@art("map_floor_town", 256, 256)
def map_floor_town(b): swatch(b, K("#a9b46a", 0.72))


@art("map_water", 256, 256)
def map_water(b): swatch(b, K("#5f94b8", 0.6))


# ------------------------------------------------------------------ pencil map symbols (32 px)
def sym(name):
    return art(name, 32, 32)


@sym("map_stairs_down")
def map_stairs_down(b):
    steps = [(2.5, 2.5), (13.5, 2.5), (13.5, 4.8), (10.8, 4.8), (10.8, 7.4), (8.1, 7.4), (8.1, 10), (5.4, 10), (5.4, 12.6), (2.5, 12.6)]
    shape(steps, K("#a8774a", 0.55), W * 0.7)
    hatch(steps, 1.2, 60, 0.3, alpha=0.4)
    shape([(10.2, 14.2), (14, 14.2), (12.1, 10.4)], K("#c4553a", 0.5), W * 0.5)


@sym("map_stairs_up")
def map_stairs_up(b):
    steps = [(13.5, 2.5), (2.5, 2.5), (2.5, 4.8), (5.2, 4.8), (5.2, 7.4), (7.9, 7.4), (7.9, 10), (10.6, 10), (10.6, 12.6), (13.5, 12.6)]
    shape(steps, K("#a8774a", 0.55), W * 0.7)
    hatch(steps, 1.2, 120, 0.3, alpha=0.4)
    shape([(2, 10.6), (5.8, 10.6), (3.9, 14.4)], K("#79b4e8", 0.7), W * 0.5)


@sym("map_cage")
def map_cage(b):
    shape(rect(3.5, 2.5, 9, 11), K("#4a4e57", 0.35), W * 0.7)
    for x in (5.8, 8, 10.2):
        stroke([(x, 3), (x, 13)], W * 0.5, g=0.9)
    stroke([(8, 13.5), (8, 15.5)], W * 0.6, g=GRAPHITE)
    glow(8, 8, 3.2, "#7fb0ff", 0.5)


@sym("map_shrine")
def map_shrine(b):
    pole = [(6.5, 2), (9.5, 2), (9.2, 11), (6.8, 11)]
    shape(pole, WOOD, W * 0.6)
    shape(ragged(8, 12, 3.6, 3.2, 4, 18, 0.06), K("#9a7fd8", 0.55), W * 0.6)
    dot(6.8, 12.3, 0.55); dot(9.2, 12.3, 0.55)


@sym("map_quest")
def map_quest(b):
    glow(8, 8, 5, "#ffb050", 0.45)
    star = [(8 + math.cos(math.radians(90 + i * 36)) * (6 if i % 2 == 0 else 2.6),
             8 + math.sin(math.radians(90 + i * 36)) * (6 if i % 2 == 0 else 2.6)) for i in range(10)]
    shape(star, K("#f08a24", 0.65), W * 0.7)


@sym("map_book")
def map_book(b):
    shape([(2.5, 4), (8, 3), (8, 13), (2.5, 14)], PARCH, W * 0.6)
    shape([(13.5, 4), (8, 3), (8, 13), (13.5, 14)], PARCH, W * 0.6)
    for y in (6.5, 8.5, 10.5):
        stroke([(4, y + 0.3), (7, y)], W * 0.3, g=0.3)
        stroke([(9, y), (12, y + 0.3)], W * 0.3, g=0.3)


@sym("map_npc")
def map_npc(b):
    shape(ragged(8, 11.5, 2.6, 2.6, 6, 16, 0.04), K("#e6c39a", 0.85), W * 0.6)
    shape([(4, 2.5), (12, 2.5), (10.6, 8.6), (5.4, 8.6)], K("#5d7a3a", 0.45), W * 0.6)


@sym("map_hero")
def map_hero(b):
    glow(8, 8, 6, "#ffd060", 0.55)
    shape([(8, 14), (12, 3), (8, 5.5), (4, 3)], K("#c4553a", 0.5), W * 0.8)


@sym("map_portal")
def map_portal(b):
    glow(8, 8, 6, "#9fd0ff", 0.6)
    stroke(ragged(8, 8, 3.2, 5.5, 8, 24, 0.05), W * 0.9, closed=True, g=0.45)


@sym("map_boss")
def map_boss(b):
    sk = bez((3.5, 7), (3, 14), (13, 14), (12.5, 7)) + [(11, 3.5), (5, 3.5)]
    shape(sk, BONE, W * 0.7)
    for sx in (5.8, 10.2):
        shape(ell(sx, 8.6, 1.5, 1.7, 10), INK, W * 0.3)
        dot(sx, 8.6, 0.5, K("#ff3020", 0.6))


# ------------------------------------------------------------------ quest marks over people's heads (48 x 64)
def bang(b, col, glow_hex):
    cx = b.w / 2
    glow(cx, 17, 13, glow_hex, 0.35)
    stem = bez((cx - 3.6, 30), (cx - 4.2, 22), (cx - 2.4, 13), (cx - 1.6, 11)) + [(cx + 1.6, 11)] + \
        bez((cx + 1.6, 11), (cx + 2.4, 13), (cx + 4.2, 22), (cx + 3.6, 30))
    shape(stem, col, W * 1.1)
    shape(ragged(cx, 5.6, 3.2, 3.0, 9, 20, 0.05), col, W * 1.1)
    hl([(cx - 1.6, 27), (cx - 1.2, 17)], W * 0.7, 0.6)


def query(b, col, glow_hex):
    cx = b.w / 2
    glow(cx, 17, 13, glow_hex, 0.35)
    hook = bez((cx - 7, 23), (cx - 7.5, 31), (cx + 7.5, 31.5), (cx + 7, 23)) + \
        bez((cx + 7, 23), (cx + 6.6, 17), (cx + 2.2, 16.5), (cx + 2.2, 11)) + [(cx - 2.6, 11)] + \
        bez((cx - 2.6, 11), (cx - 2.6, 18), (cx + 2.6, 18.5), (cx + 2.6, 23)) + \
        bez((cx + 2.6, 23), (cx + 2.4, 27), (cx - 2.6, 27), (cx - 2.4, 23))
    shape(hook, col, W * 1.1)
    shape(ragged(cx, 5.6, 3.2, 3.0, 4, 20, 0.05), col, W * 1.1)


@art("quest_new", 48, 64)
def quest_new(b): bang(b, K("#f2c040", 0.75), "#ffd060")


@art("quest_new_side", 48, 64)
def quest_new_side(b): bang(b, K("#d8dde4", 0.88), "#cfe6ff")


@art("quest_turnin", 48, 64)
def quest_turnin(b): query(b, K("#f2c040", 0.75), "#ffd060")


def make_seamless():
    """the swatches tile under every map cell, so their edges must meet"""
    import os
    from PIL import Image
    from world import seamless
    for n in ("map_floor", "map_floor_town", "map_water"):
        path = os.path.join(common.OUT, "ui", n + ".png")
        if os.path.exists(path):
            seamless(Image.open(path).convert("RGBA")).save(path)


if __name__ == "__main__":
    common.run({"ui": MAP})
    make_seamless()
