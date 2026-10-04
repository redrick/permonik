import math
import common
from icons_kit import *

ITEMS = []
CELL = 56


def item(w, h):
    def deco(fn):
        ITEMS.append((fn.__name__, w * CELL, h * CELL, fn)); return fn
    return deco


def haft(y0, y1, w0, w1, g=WOOD, x=0.0):
    o = tube([(x, y0), (x, y1)], w0, w1, g, W, sh=0.18)
    stroke([(x - w0 * 0.15, y0 + 3), (x - w1 * 0.15, y1 - 3)], 0.35, g=WOOD_L, alpha=0.7)
    return o


def grip(y0, y1, w, g=LEATHER, n=6):
    r = rect(-w / 2, y0, w, y1 - y0)
    shape(r, g, W)
    for i in range(1, n):
        y = y0 + (y1 - y0) * i / n
        stroke([(-w / 2, y - 0.8), (w / 2, y + 0.8)], 0.45, g=LEATHER_D)


def band(y, w, h=2.2, g=IRON):
    shape(rect(-w / 2, y - h / 2, w, h), g, W * 0.8)
    hl([(-w / 2 + 0.6, y + h * 0.15), (w / 2 - 0.6, y + h * 0.15)], 0.35, 0.6)


# ------------------------------------------------------------------ weapons
@item(2, 3)
def krumpac(b):
    with T(b.w / 2 - 4, b.h / 2 - 4, 0.8, rot=-27):
        haft(-44, 26, 4.2, 5.2)
        band(-41, 4.8, 2.0)
        top = bez((-27, 22), (-12, 36), (10, 37), (25, 27))
        bot = bez((25, 27), (12, 31), (5, 29.5), (0, 29)) + bez((0, 29), (-6, 29.5), (-14, 29), (-27, 22))
        head = top + bot[1:]
        form(head, IRON, W, sdx=0, sdy=-1.8, sh=0.25)
        hl(bez((-22, 25), (-10, 33.5), (8, 34), (20, 28)), 0.6, 0.55)
        shape(rrect(-4, 26.5, 8, 9.5, 1.5), IRON_D, W * 0.8)
        rivet(0, 31.5, 1.0)
        stroke([(-27, 22), (-24.5, 24.2)], 0.6, g=STEEL_L)


@item(2, 3)
def sekera(b):
    with T(b.w / 2 - 4, b.h / 2 - 1, 0.88, rot=-28):
        haft(-44, 34, 4.0, 5.0)
        band(-41, 4.6, 2.0)
        head = [(-2.5, 34)] + bez((-2.5, 34), (6, 35), (12, 38), (20, 42)) + \
            bez((20, 42), (24, 32), (24, 18), (19, 9)) + bez((19, 9), (12, 14), (8, 20), (2.5, 21)) + [(-2.5, 21)]
        form(head, IRON, W, sdx=-1.5, sdy=0, sh=0.22)
        edge = bez((20, 42), (24, 32), (24, 18), (19, 9))
        stroke([(x - 2.2, y) for x, y in edge], 1.6, g=STEEL_L, alpha=0.75)
        shape(rrect(-3.6, 19.5, 7.2, 16, 1.5), IRON_D, W * 0.8)
        rivet(0, 27.5, 1.0)


@item(1, 3)
def valaska(b):
    with T(b.w / 2 - 3, b.h / 2 - 1, 0.95, rot=-3):
        haft(-41, 30, 3.0, 3.4, WOOD_L)
        for y in (-30, -14, 4, 18):
            band(y, 3.8, 1.5, BRASS)
        stroke(bez((-1.6, -26), (1.6, -22), (-1.6, -18), (1.6, -16)), 0.4, g=RED)
        head = [(-6.5, 37)] + bez((-6.5, 37), (-2, 38.5), (3, 38.5), (8, 40)) + \
            bez((8, 40), (11.5, 36), (11.5, 31), (8.5, 25.5)) + bez((8.5, 25.5), (5, 28), (3, 30), (1.8, 30.5)) + \
            [(-1.8, 30.5), (-6.5, 32.5)]
        form(head, STEEL, W, sdx=-1, sdy=-0.8, sh=0.25)
        stroke(bez((8, 40), (11.5, 36), (11.5, 31), (8.5, 25.5)), 0.9, g=STEEL_L, alpha=0.85)
        stroke([(-5.5, 35.5), (6, 37.5)], 0.35, g=STEEL_D)
        dot(-1, 34, 0.7, BRASS_L)


@item(1, 3)
def palcat(b):
    with T(b.w / 2, b.h / 2, 0.95, rot=-8):
        haft(-41, 22, 3.4, 3.8, WOOD_D)
        grip(-40, -24, 4.2)
        dot(0, -42, 2.6, IRON); stroke(ell(0, -42, 2.6, 2.6, 16), W * 0.8, closed=True)
        band(20, 4.6, 2.5)
        shape(ell(0, 31, 6.5, 10, 24), IRON_D, W)
        for dx in (-1, 0, 1):
            fl = [(dx * 4.2 - 2.6, 23), (dx * 6.8, 31), (dx * 4.2 - 2.6 + 5.2 * (dx == 0) * 0 + 0.0, 40)]
        for k, dx in enumerate((-7.5, -3.6, 0, 3.6, 7.5)):
            ww = 2.4 if abs(dx) > 5 else 3.0
            fl = [(dx * 0.55 - ww / 2, 22.5), (dx - ww / 2, 31), (dx * 0.55 - ww / 2, 40.5), (dx * 0.55 + ww / 2, 40.5),
                  (dx + ww / 2, 31), (dx * 0.55 + ww / 2, 22.5)]
            shape(fl, STEEL if abs(dx) < 1 else IRON_L, W * 0.7)
        hl([(-0.5, 25), (-0.5, 38)], 0.5, 0.7)
        shape(ell(0, 41.5, 1.8, 1.8, 12), IRON, W * 0.7)


@item(2, 3)
def cep(b):
    with T(b.w / 2 - 8, b.h / 2 - 8, 0.9, rot=-6):
        haft(-34, 14, 3.8, 4.4)
        grip(-33, -20, 4.6)
        band(13, 5.0, 2.4)
        pts = bez((0, 15), (4, 22), (9, 25), (13, 27), 7)
        for i in range(len(pts) - 1):
            x, y = pts[i]
            stroke(ell(x, y, 1.6, 1.0, 10, rot=math.degrees(math.atan2(pts[i + 1][1] - y, pts[i + 1][0] - x)) + (90 * (i % 2))),
                   0.6, closed=True, g=IRON_D)
    with T(b.w / 2 + 8, b.h / 2 + 19, 0.88, rot=-50):
        shape(rrect(-4, -6, 8, 26, 3), WOOD, W)
        offset_shadow(rrect(-4, -6, 8, 26, 3), -1.4, 0, 0.2)
        for y in (-3, 7, 17):
            band(y, 9.0, 2.2)
        for y in (2, 12):
            for sx in (-1, 1):
                sp = [(sx * 4, y - 1.2), (sx * 8, y), (sx * 4, y + 1.2)]
                shape(sp, STEEL, W * 0.6)
        shape(ell(0, -6.5, 2.0, 1.4, 12), IRON, W * 0.7)


@item(1, 3)
def kord(b):
    with T(b.w / 2, b.h / 2, 0.95, rot=-7):
        blade = [(-1.5, -10), (0, 42), (1.5, -10)]
        form(blade, STEEL, W * 0.8, sdx=-0.8, sdy=0, sh=0.25)
        stroke([(0.2, -9), (0.1, 38)], 0.4, g=STEEL_L, alpha=0.9)
        guard = bez((-9, -12), (-9, -2), (-3, -1), (0, -12))
        stroke(guard, 1.6, g=BRASS)
        stroke(bez((0, -12), (6, -14), (8, -20), (3, -27)), 1.4, g=BRASS)
        stroke(bez((-9, -12), (-8, -17), (-4, -20), (-2, -27)), 1.1, g=BRASS)
        shape(rect(-9.5, -13.2, 19, 2.4), BRASS, W * 0.7)
        grip(-27, -14, 3.6, WOOD_D, 5)
        shape(ell(0, -29.5, 2.8, 2.8, 16), BRASS, W * 0.8)
        hl([(-1, -29), (0.3, -28)], 0.5, 0.9)


@item(1, 3)
def savle(b):
    with T(b.w / 2 - 3, b.h / 2, 0.95, rot=-4):
        back = bez((-1.8, -12), (-1.5, 10), (2, 28), (10, 40))
        edge = bez((10, 40), (5, 30), (2.5, 14), (2.2, -12))
        blade = back + edge[1:]
        form(blade, STEEL, W * 0.8, sdx=-1, sdy=0, sh=0.25)
        stroke(bez((0.8, -10), (1, 8), (4, 26), (9, 37)), 0.45, g=STEEL_L, alpha=0.9)
        stroke([(-4, -13), (6, -13)], 2.0, g=GOLD_D)
        stroke([(-4.5, -13), (-6, -10)], 1.2, g=GOLD_D)
        stroke(bez((5, -13), (7, -18), (6, -24), (3, -28)), 0.9, g=GOLD_D)
        grip(-28, -14, 3.8, LEATHER_D, 5)
        shape(bez((-2.6, -28), (-3, -31), (0, -33), (3, -31)) + [(2, -28)], GOLD, W * 0.7)


@item(1, 2)
def obusek(b):
    with T(b.w / 2, b.h / 2, 0.95, rot=-12):
        body = bez((-1.8, -24), (-2.4, 0), (-6, 14), (-5.5, 22)) + bez((-5.5, 22), (-4, 25), (4, 25), (5.5, 22)) + \
            bez((5.5, 22), (6, 14), (2.4, 0), (1.8, -24))
        form(body, WOOD, W, sdx=-1.4, sdy=0, sh=0.22)
        hl(bez((-1, -20), (-1.2, 0), (-3.5, 12), (-3, 20)), 0.45, 0.5)
        for (x, y) in ((-2.5, 18), (2.5, 16), (0, 11.5), (-3.2, 8), (3, 7), (0, 21.5)):
            rivet(x, y, 1.1, IRON)
        shape(ell(0, -24.5, 2.2, 1.4, 12), WOOD_D, W * 0.7)
        stroke(bez((0, -24), (-3, -27), (-2, -22), (0, -20)), 0.5, g=LEATHER_D)


@item(1, 2)
def nuz(b):
    with T(b.w / 2, b.h / 2, 0.95, rot=-14):
        blade = [(-2.4, -2)] + bez((-2.4, -2), (-2.6, 10), (-1.5, 18), (0.5, 25)) + bez((0.5, 25), (2, 16), (2.8, 8), (2.6, -2))
        form(blade, STEEL, W * 0.8, sdx=-1.2, sdy=0, sh=0.25)
        stroke(bez((1.5, 0), (1.8, 8), (1.4, 16), (0.4, 23)), 0.6, g=STEEL_L, alpha=0.9)
        shape(rrect(-4.5, -4, 9, 2.6, 1), IRON, W * 0.7)
        shape(rrect(-2.4, -20, 4.8, 16, 2), BONE, W * 0.8)
        offset_shadow(rrect(-2.4, -20, 4.8, 16, 2), -1, 0, 0.2)
        for y in (-16, -12, -8):
            stroke([(-2.4, y), (2.4, y + 0.6)], 0.35, g=BONE_D)
        shape(ell(0, -21.5, 2.6, 2.0, 12), IRON, W * 0.7)


@item(2, 3)
def obourucni_mec(b):
    with T(b.w / 2, b.h / 2 - 1, 0.98, rot=-32):
        blade = [(-3.2, -13), (-2.8, 38), (0, 46), (2.8, 38), (3.2, -13)]
        form(blade, STEEL, W * 0.8, sdx=-1.3, sdy=0, sh=0.25)
        stroke([(0, -11), (0, 40)], 0.5, g=STEEL_D, alpha=0.7)
        stroke([(-1.4, -11), (-1.4, 37)], 0.5, g=STEEL_L, alpha=0.8)
        guard = [(-14, -14.5), (-12, -11.5), (12, -11.5), (14, -14.5), (12, -16), (-12, -16)]
        shape(guard, IRON, W * 0.8)
        for sx in (-1, 1):
            shape(ell(sx * 14.5, -14, 1.7, 1.7, 12), IRON_D, W * 0.6)
        grip(-38, -16, 4.0, LEATHER_D, 8)
        shape(ell(0, -40.5, 3.6, 3.0, 16), IRON, W * 0.8)
        hl([(-1.5, -39.5), (0.5, -38.5)], 0.6, 0.8)


@item(2, 3)
def luk(b):
    with T(b.w / 2, b.h / 2, 1.0, rot=-30):
        top = bez((0, 4), (8, 14), (10, 30), (4, 44))
        botm = bez((0, -4), (8, -14), (10, -30), (4, -44))
        for arm in (top, botm):
            tube(arm, 3.6, 1.8, WOOD, W, sh=0.18)
        stroke([(4, 44), (4, -44)], 0.5, g=K("#d9cfb2", 0.85))
        shape(rrect(-1.2, -6, 5.6, 12, 2), LEATHER, W * 0.8)
        for y in (-3, 0, 3):
            stroke([(-1.2, y), (4.4, y + 0.6)], 0.35, g=LEATHER_D)
        dot(4.2, 44, 1.0, BONE); dot(4.2, -44, 1.0, BONE)


@item(2, 3)
def kuse(b):
    with T(b.w / 2, b.h / 2 - 2, 1.0, rot=-30):
        stock = [(-2.5, -40), (2.5, -40), (3.2, -20), (2.8, 26), (-2.8, 26), (-3.2, -20)]
        butt = [(-3.6, -42), (3.6, -42), (3.4, -26), (-3.4, -26)]
        form(stock, WOOD, W, sdx=-1.4, sdy=0, sh=0.2)
        form(butt, WOOD_D, W, sdx=-1.4, sdy=0, sh=0.2)
        stroke([(0, -18), (0, 25)], 0.6, g=WOOD_D)
        prod = bez((-24, 14), (-12, 24), (12, 24), (24, 14))
        tube(prod, 2.6, 2.6, IRON_L, W, sh=0.2)
        stroke([(-24, 14), (0, 2), (24, 14)], 0.5, g=K("#d9cfb2", 0.85))
        shape(rrect(-1.6, -8, 3.2, 3.5, 1), IRON, W * 0.6)
        stroke(bez((1.5, -10), (6, -14), (5, -22), (2, -24)), 0.9, g=IRON)
        stir = ell(0, 31, 4.5, 5.5, 20)
        stroke(stir, 1.1, closed=True, g=IRON)
        band(24, 6.4, 2.6)
        shape([(-1, 2.5), (0, 20), (1, 2.5)], K("#b48a52", 0.6), W * 0.5)


@item(1, 3)
def hul(b):
    with T(b.w / 2, b.h / 2 - 2, 0.95, rot=-5):
        st = bez((0.5, -42), (-1.5, -10), (1.5, 10), (0, 26))
        tube(st, 3.2, 3.8, WOOD, W, sh=0.2)
        stroke(bez((-0.5, -38), (-1.6, -10), (0.6, 10), (-0.8, 24)), 0.4, g=WOOD_L, alpha=0.6)
        for sx in (-1, 1):
            a = bez((0, 25), (sx * 3, 31), (sx * 8, 34), (sx * 10, 42))
            tube(a, 2.6, 1.2, BONE, W * 0.8, sh=0.15)
            tine = bez((sx * 4, 31), (sx * 3, 35), (sx * 3.5, 38), (sx * 2.5, 41))
            tube(tine, 1.6, 0.9, BONE, W * 0.7, sh=0)
            tube([(sx * 7.5, 34), (sx * 11, 35.5)], 1.4, 0.8, BONE, W * 0.7, sh=0)
        for y, c in ((20, RED), (17.5, RED), (15, RED_L)):
            stroke([(-2.2, y), (2.2, y + 0.8)], 0.8, g=c)
        stroke(bez((1.5, 17), (4, 12), (2, 8), (4.5, 4)), 0.5, g=RED)
        dot(4.6, 3.6, 1.0, BONE); dot(4.2, 7.5, 0.8, BONE_D)


@item(1, 3)
def berla(b):
    with T(b.w / 2, b.h / 2 - 1, 0.95, rot=-6):
        st = bez((0, -42), (0.5, -15), (-0.5, 10), (0, 22))
        tube(st, 2.8, 3.6, BONE, W, sh=0.2)
        for y in (-30, -16, -2, 12):
            shape(ell(0, y, 2.6, 1.4, 14), BONE_D, W * 0.6)
        stroke([(-0.4, -40), (-0.6, 20)], 0.4, g=K("#ffffff", 1), alpha=0.5)
        skull = bez((-6, 28), (-7, 38), (7, 38), (6, 28)) + bez((6, 28), (5, 25), (3, 23.5), (2.5, 21.5)) + \
            [(-2.5, 21.5)] + bez((-2.5, 21.5), (-3, 23.5), (-5, 25), (-6, 28))
        form(skull, BONE, W, sdx=-1, sdy=0.8, sh=0.2)
        shape(ell(-2.5, 29, 1.8, 2.0, 12), INK, W * 0.5)
        shape(ell(2.5, 29, 1.8, 2.0, 12), INK, W * 0.5)
        dot(-2.5, 29, 0.7, K("#7cff9a", 0.9)); dot(2.5, 29, 0.7, K("#7cff9a", 0.9))
        glow(0, 29, 6, "#7cff9a", 0.35)
        for x in (-1.6, 0, 1.6):
            stroke([(x, 23.5), (x, 25)], 0.4)
        for sx in (-1, 1):
            tube(bez((sx * 5, 35), (sx * 9, 38), (sx * 9, 42), (sx * 6, 44)), 2.0, 0.8, BONE_D, W * 0.7, sh=0)


# ------------------------------------------------------------------ off-hand
@item(2, 2)
def stit(b):
    cx, cy = b.w / 2, b.h / 2
    o = ell(cx, cy, 23, 23, 48)
    form(o, WOOD, W, sdx=-2, sdy=2, sh=0.2)
    for k in (-12, -4, 4, 12):
        stroke([(cx + k, cy - 22 + abs(k) * 0.2), (cx + k, cy + 22 - abs(k) * 0.2)], 0.45, g=WOOD_D)
    stroke(ell(cx, cy, 21.5, 21.5, 48), 2.6, closed=True, g=IRON)
    stroke(ell(cx, cy, 23, 23, 48), W, closed=True)
    for i in range(12):
        a = math.radians(i * 30 + 15)
        rivet(cx + math.cos(a) * 21.5, cy + math.sin(a) * 21.5, 0.8, IRON_L)
    boss = ell(cx, cy, 7, 7, 28)
    form(boss, IRON, W, sdx=-1.4, sdy=1.4, sh=0.3)
    hl(ell(cx - 2, cy + 2, 3, 3, 12, 90, 180), 0.8, 0.8)
    shade(ell(cx, cy, 23, 23, 48, 200, 340) + [(cx, cy)], 0.18)


@item(2, 3)
def paveza(b):
    cx, cy = b.w / 2, b.h / 2
    body = [(cx - 20, cy - 36), (cx + 20, cy - 36), (cx + 22, cy + 30)] + \
        bez((cx + 22, cy + 30), (cx + 14, cy + 37), (cx - 14, cy + 37), (cx - 22, cy + 30))
    form(body, RED_D, W, sdx=-2, sdy=0, sh=0.25)
    rib = [(cx - 5, cy - 36), (cx + 5, cy - 36), (cx + 5.5, cy + 35), (cx - 5.5, cy + 35)]
    form(rib, K("#7a1e1e", 0.3), W * 0.8, sdx=-1.6, sdy=0, sh=0.25)
    hl([(cx + 3.5, cy - 34), (cx + 3.8, cy + 33)], 0.5, 0.25)
    with T(cx, cy + 4, 1.0):
        cup = bez((-8, 10), (-8, 1), (8, 1), (8, 10)) + [(8, 11), (-8, 11)]
        shape(cup, CLOTH_W, W * 0.7)
        shape([(-1.5, 1.5), (1.5, 1.5), (1.5, -7), (-1.5, -7)], CLOTH_W, W * 0.6)
        shape(bez((-6, -11), (-6, -7), (6, -7), (6, -11)), CLOTH_W, W * 0.6)
    stroke(body, 1.6, closed=True, g=IRON)
    stroke(body, W, closed=True)
    for (x, y) in ((-17, -33), (17, -33), (-19, 28), (19, 28), (-18, -2), (18, -2)):
        rivet(cx + x, cy + y, 0.9, IRON_L)
    shade([(cx - 20, cy - 36), (cx - 5, cy - 36), (cx - 5.5, cy + 35), (cx - 22, cy + 30)], 0.22)


@item(2, 2)
def kniha(b):
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=8):
        pages = [(-17, -21), (18, -21), (19.5, -19), (19.5, 20), (-17, 20)]
        shape(pages, PARCH, W)
        for k in range(1, 4):
            stroke([(-15, -21 + k * 0.9 - 1.6), (19.5, -21 + k * 0.9 - 1.6)], 0.3, g=PARCH_D)
        cover = rrect(-20, -19, 37, 41, 2.5)
        form(cover, LEATHER_D, W, sdx=-1.6, sdy=1.6, sh=0.25)
        shape(rect(-20, -19, 4.5, 41), K("#2b1a10", 0.18), W * 0.8)
        for y in (-12, 0, 12):
            stroke([(-20, y), (-15.5, y)], 1.0, g=GOLD_D)
        for (x, y, r) in ((-15, 21, -90), (17, 21, 180), (-15, -19, 0), (17, -19, 90)):
            pass
        for (x, y) in ((17, 22), (17, -19)):
            c = [(x, y), (x - 6, y), (x, y - 6 if y > 0 else y + 6)]
            shape(c, BRASS, W * 0.6)
        ring = ell(1.5, 1.5, 9, 9, 32)
        stroke(ring, 0.8, closed=True, g=GOLD_D)
        glow(1.5, 1.5, 9, "#8fe0a8", 0.25)
        eye = bez((-5, 1.5), (-2, 6), (5, 6), (8, 1.5)) + bez((8, 1.5), (5, -3), (-2, -3), (-5, 1.5))
        shape(eye, BONE, W * 0.6)
        dot(1.5, 1.5, 2.2, K("#4aa860", 0.5)); dot(1.5, 1.5, 1.0, INK)
        for i in range(6):
            a = math.radians(i * 60 + 30)
            stroke([(1.5 + math.cos(a) * 10.5, 1.5 + math.sin(a) * 10.5), (1.5 + math.cos(a) * 13, 1.5 + math.sin(a) * 13)], 0.6, g=GOLD_D)
        clasp = rect(14.5, -1, 6, 5)
        shape(clasp, BRASS, W * 0.7)
        rivet(18.5, 1.5, 0.7, BRASS)


# ------------------------------------------------------------------ head
@item(2, 2)
def beranice(b):
    cx, cy = b.w / 2, b.h / 2 - 2
    crown = bez((-17, -4), (-19, 16), (-6, 22), (4, 21)) + bez((4, 21), (14, 20), (19, 12), (17, -4))
    form([(cx + x, cy + y) for x, y in crown], LEATHER, W, sdx=-2, sdy=0, sh=0.2)
    stroke(bez((cx - 4, cy + 20), (cx - 2, cy + 10), (cx - 3, cy + 2), (cx - 5, cy - 2)), 0.6, g=LEATHER_D)
    stroke([(cx - 12, cy + 14), (cx + 10, cy + 15)], 0.4, g=RED)
    brim = []
    n = 26
    for i in range(n + 1):
        t = i / n
        x = -21 + 42 * t
        r = 2.2 + 0.9 * math.sin(t * 50)
        brim.append((cx + x, cy - 2 + math.sin(t * math.pi) * 2 + r))
    for i in range(n, -1, -1):
        t = i / n
        x = -21 + 42 * t
        r = 2.2 + 0.9 * math.cos(t * 47)
        brim.append((cx + x, cy - 12 - math.sin(t * math.pi) * 1.5 - r))
    form(brim, FLEECE, W, sdx=0, sdy=2.4, sh=0.2)
    for i in range(16):
        x = cx - 18 + i * 2.4 + (i % 2) * 0.6
        y = cy - 7 + ((i * 7) % 5 - 2) * 1.2
        stroke(ell(x, y, 1.3, 1.1, 10, 30, 300), 0.4, g=FLEECE_D)


@item(2, 2)
def havirska_prilba(b):
    cx, cy = b.w / 2, b.h / 2 - 3
    cap = bez((cx - 15, cy - 8), (cx - 17, cy + 10), (cx - 12, cy + 19), (cx, cy + 20)) + \
        bez((cx, cy + 20), (cx + 12, cy + 19), (cx + 17, cy + 10), (cx + 15, cy - 8))
    form(cap, LEATHER_D, W, sdx=-2.2, sdy=0, sh=0.22)
    stroke(bez((cx - 10, cy + 17), (cx - 3, cy + 21), (cx + 4, cy + 21), (cx + 11, cy + 17)), 0.5, g=LEATHER_L, alpha=0.8)
    stroke(bez((cx - 14, cy + 4), (cx - 5, cy + 7), (cx + 5, cy + 7), (cx + 14, cy + 4)), 0.5, g=LEATHER)
    brim = bez((cx - 20, cy - 9), (cx - 10, cy - 4), (cx + 10, cy - 4), (cx + 20, cy - 9)) + \
        bez((cx + 20, cy - 9), (cx + 12, cy - 15), (cx - 12, cy - 15), (cx - 20, cy - 9))
    form(brim, LEATHER, W, sdx=0, sdy=1.6, sh=0.2)
    shape(rrect(cx - 3, cy - 2, 6, 7, 1), BRASS, W * 0.7)
    stroke(bez((cx, cy + 5), (cx - 2, cy + 8), (cx + 2, cy + 10), (cx, cy + 12)), 0.9, g=BRASS)
    for x in (-8, 8):
        rivet(cx + x, cy - 4.5, 0.8, BRASS)
    shape([(cx - 4, cy + 22), (cx, cy + 25), (cx + 4, cy + 22), (cx, cy + 19.5)], K("#2b2b2b", 0.15), W * 0.5)


@item(2, 2)
def kapuce(b):
    cx, cy = b.w / 2, b.h / 2
    hood = bez((cx - 15, cy - 20), (cx - 22, cy + 2), (cx - 12, cy + 22), (cx + 3, cy + 22)) + \
        bez((cx + 3, cy + 22), (cx + 10, cy + 22), (cx + 18, cy + 10), (cx + 22, cy - 2)) + \
        bez((cx + 22, cy - 2), (cx + 18, cy - 10), (cx + 17, cy - 16), (cx + 15, cy - 20))
    form(hood, K("#4c4a3a", 0.35), W, sdx=-2, sdy=0, sh=0.2)
    opening = bez((cx - 10, cy - 19), (cx - 13, cy - 2), (cx - 6, cy + 13), (cx + 3, cy + 12)) + \
        bez((cx + 3, cy + 12), (cx + 10, cy + 9), (cx + 11, cy - 6), (cx + 9, cy - 19))
    shape(opening, K("#141216", 0.05), W * 0.8)
    dot(cx - 3, cy + 1, 0.9, K("#ffd560", 0.9)); dot(cx + 4, cy + 1, 0.9, K("#ffd560", 0.9))
    glow(cx + 0.5, cy + 1, 6, "#ffcc40", 0.2)
    stroke(bez((cx - 15, cy - 20), (cx - 5, cy - 22), (cx + 5, cy - 22), (cx + 15, cy - 20)), W)
    stroke(bez((cx + 5, cy + 21), (cx + 12, cy + 17), (cx + 17, cy + 8), (cx + 20, cy - 1)), 0.5, g=K("#7a7660", 0.6))


@item(2, 2)
def prilba(b):
    cx, cy = b.w / 2, b.h / 2 - 2
    dome = bez((cx - 13, cy - 4), (cx - 14, cy + 14), (cx - 6, cy + 19), (cx, cy + 19)) + \
        bez((cx, cy + 19), (cx + 6, cy + 19), (cx + 14, cy + 14), (cx + 13, cy - 4))
    form(dome, IRON, W, sdx=-2.4, sdy=0, sh=0.25)
    stroke([(cx, cy + 19), (cx, cy - 4)], 0.8, g=IRON_D)
    hl(bez((cx - 9, cy), (cx - 10, cy + 10), (cx - 6, cy + 15), (cx - 3, cy + 16)), 0.9, 0.6)
    brim = bez((cx - 23, cy - 9), (cx - 12, cy - 2), (cx + 12, cy - 2), (cx + 23, cy - 9)) + \
        bez((cx + 23, cy - 9), (cx + 12, cy - 6.5), (cx - 12, cy - 6.5), (cx - 23, cy - 9))
    brim = bez((cx - 23, cy - 8), (cx - 14, cy - 1), (cx + 14, cy - 1), (cx + 23, cy - 8)) + \
        bez((cx + 23, cy - 8), (cx + 14, cy - 12), (cx - 14, cy - 12), (cx - 23, cy - 8))
    form(brim, IRON_L, W, sdx=0, sdy=1.4, sh=0.25)
    for x in (-10, -4, 4, 10):
        rivet(cx + x, cy - 3.2, 0.7)


@item(2, 2)
def velka_prilba(b):
    cx, cy = b.w / 2, b.h / 2
    helm = [(cx - 14, cy - 20), (cx + 14, cy - 20)] + bez((cx + 14, cy - 20), (cx + 16, cy), (cx + 15, cy + 14), (cx, cy + 22)) + \
        bez((cx, cy + 22), (cx - 15, cy + 14), (cx - 16, cy), (cx - 14, cy - 20))
    form(helm, STEEL_D, W, sdx=-2.4, sdy=0, sh=0.25)
    stroke([(cx, cy + 22), (cx, cy - 20)], 0.9, g=IRON_D)
    shape(rect(cx - 13, cy + 1, 11, 2.6), INK, W * 0.5)
    shape(rect(cx + 2, cy + 1, 11, 2.6), INK, W * 0.5)
    for i in range(4):
        for j in range(3):
            dot(cx + 3 + i * 2.8, cy - 6 - j * 3, 0.55, INK)
    hl(bez((cx - 11, cy - 16), (cx - 13, cy - 4), (cx - 12, cy + 8), (cx - 6, cy + 17)), 0.9, 0.5)
    band_pts = rect(cx - 15, cy + 7, 30, 3)
    stroke([(cx - 15, cy + 8), (cx + 15, cy + 8)], 1.4, g=BRASS)
    for x in (-11, -5, 5, 11):
        rivet(cx + x, cy - 17.5, 0.7, BRASS)
    shape([(cx - 2, cy + 21), (cx, cy + 25), (cx + 2, cy + 21)], RED, W * 0.5)


# ------------------------------------------------------------------ body
def torso(cx, cy, g, sleeves=True, sleeve_g=None, hem=-36, top=30, width=14):
    pts = [(cx - width, cy + hem)] + bez((cx - width, cy + hem), (cx - width + 1, cy), (cx - width - 1, cy + 12), (cx - width + 2, cy + top - 4)) + \
        [(cx - 6, cy + top), (cx + 6, cy + top)] + bez((cx + width - 2, cy + top - 4), (cx + width + 1, cy + 12), (cx + width - 1, cy), (cx + width, cy + hem))
    sl = []
    if sleeves:
        for sx in (-1, 1):
            s = [(cx + sx * (width - 2), cy + top - 4), (cx + sx * (width + 7), cy + top - 14), (cx + sx * (width + 11), cy - 8),
                 (cx + sx * (width + 5), cy - 9.5), (cx + sx * (width + 2), cy + 8)]
            sl.append(s)
            form(s, sleeve_g or g, W, sdx=sx * 1.5, sdy=0, sh=0.2)
    form(pts, g, W, sdx=-2, sdy=0, sh=0.2)
    return pts, sl


@item(2, 3)
def kytel(b):
    cx, cy = b.w / 2, b.h / 2 - 1
    pts, sl = torso(cx, cy, CLOTH_W)
    hood = bez((cx - 9, cy + 26), (cx - 12, cy + 38), (cx + 12, cy + 38), (cx + 9, cy + 26))
    form(hood, CLOTH_W, W, sdx=0, sdy=-1.5, sh=0.2)
    shape(bez((cx - 5, cy + 27), (cx - 6, cy + 33), (cx + 6, cy + 33), (cx + 5, cy + 27)), CLOTH_W_D, W * 0.6)
    stroke([(cx, cy + 27), (cx, cy + 12)], 0.6, g=CLOTH_W_D)
    for y in (24, 20, 16):
        dot(cx + 1.6, cy + y, 0.8, K("#2a2a2a", 0.2))
    stroke([(cx - 13.5, cy - 6), (cx + 13.5, cy - 6)], 2.2, g=K("#2b1c12", 0.2))
    shape(rrect(cx - 2.6, cy - 8, 5.2, 4, 0.8), BRASS, W * 0.6)
    for k in range(5):
        y = cy - 13 - k * 4.5
        stroke([(cx - 12.5, y), (cx - 6, y - 2)], 0.35, g=CLOTH_W_D, alpha=0.7)
    stroke(bez((cx + 6, cy - 7), (cx + 8, cy - 18), (cx + 6, cy - 28), (cx + 7, cy - 35)), 0.5, g=CLOTH_W_D)
    flek = [(cx - 14, cy - 9), (cx + 14, cy - 9), (cx + 12, cy - 30), (cx - 12, cy - 30)]


@item(2, 3)
def kozich(b):
    cx, cy = b.w / 2, b.h / 2 - 1
    pts, sl = torso(cx, cy, LEATHER_L, width=15)
    for sx in (-1, 1):
        cuff = [(cx + sx * 26, cy - 8), (cx + sx * 20, cy - 9.5), (cx + sx * 20.5, cy - 4.5), (cx + sx * 26.5, cy - 3)]
        shape(cuff, FLEECE, W * 0.7)
        lap = [(cx + sx * 6, cy + 30), (cx + sx * 12, cy + 26), (cx + sx * 3, cy - 36), (cx + sx * 0.5, cy - 36)]
        shape(lap, FLEECE, W * 0.8)
    stroke([(cx, cy + 30), (cx, cy - 36)], 0.6, g=LEATHER_D)
    hem = [(cx - 15, cy - 36), (cx + 15, cy - 36), (cx + 15, cy - 31), (cx - 15, cy - 31)]
    shape(hem, FLEECE, W * 0.7)
    for sx in (-1, 1):
        for k, c in enumerate((RED, GREEN, RED)):
            x = cx + sx * (10 + k * 1.3)
            stroke(bez((x, cy + 18), (x + sx * 2, cy + 10), (x - sx * 1, cy), (x + sx * 1, cy - 10)), 0.6, g=c)
        for y in (12, 2, -8):
            dot(cx + sx * 13, cy + y, 1.2, RED_L); dot(cx + sx * 13, cy + y, 0.5, GOLD_L)
    for i in range(14):
        x = cx - 13.5 + i * 2.1
        stroke(ell(x, cy - 33.5, 1.1, 1.0, 10, 30, 300), 0.35, g=FLEECE_D)


@item(2, 3)
def kozeny_kabatec(b):
    cx, cy = b.w / 2, b.h / 2 - 1
    pts, sl = torso(cx, cy, LEATHER, sleeves=False, width=17, hem=-34)
    collar = [(cx - 9, cy + 30), (cx, cy + 22), (cx + 9, cy + 30), (cx + 6, cy + 31), (cx, cy + 26), (cx - 6, cy + 31)]
    shape(collar, LEATHER_D, W * 0.7)
    for y in range(-28, 22, 7):
        stroke([(cx - 2, y + cy), (cx + 2, y + cy + 3)], 0.6, g=LEATHER_D)
        stroke([(cx + 2, y + cy), (cx - 2, y + cy + 3)], 0.6, g=LEATHER_D)
    for x in (-11, 11):
        stroke([(cx + x, cy + 24), (cx + x * 0.9, cy - 32)], 0.45, g=LEATHER_D, alpha=0.8)
    for y in range(-30, 24, 5):
        stroke([(cx - 16, cy + y), (cx - 13, cy + y)], 0.3, g=LEATHER_D)
    stroke([(cx - 17, cy - 22), (cx + 17, cy - 22)], 2.4, g=LEATHER_D)
    shape(rrect(cx - 3, cy - 24.5, 6, 5, 1), IRON_L, W * 0.6)
    for sx in (-1, 1):
        shape(ell(cx + sx * 15, cy + 25, 4, 3.5, 16), LEATHER_D, W * 0.7)


@item(2, 3)
def krouzkova_kosile(b):
    cx, cy = b.w / 2, b.h / 2 - 1
    pts, sl = torso(cx, cy, IRON_L, width=14, hem=-34)
    for clip in [pts] + sl:
        C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
        for j in range(0, 40):
            for i in range(0, 30):
                x = cx - 32 + i * 2.2 + (j % 2) * 1.1
                y = cy - 36 + j * 1.8
                stroke(ell(x, y, 1.15, 0.9, 8), 0.28, closed=True, g=IRON_D, alpha=0.7)
        C.restoreState()
    hl(bez((cx - 12, cy + 24), (cx - 13, cy + 10), (cx - 12, cy - 10), (cx - 13, cy - 28)), 1.0, 0.35)
    stroke(pts, W, closed=True)
    shape(bez((cx - 7, cy + 30), (cx - 5, cy + 23), (cx + 5, cy + 23), (cx + 7, cy + 30)), LEATHER_D, W * 0.6)
    stroke([(cx - 14, cy - 30), (cx + 14, cy - 30)], 1.2, g=BRASS)


@item(2, 3)
def krunyr(b):
    cx, cy = b.w / 2, b.h / 2
    plate = [(cx - 13, cy + 24)] + bez((cx - 17, cy + 18), (cx - 18, cy - 4), (cx - 16, cy - 16), (cx - 12, cy - 24)) + \
        bez((cx - 12, cy - 24), (cx - 5, cy - 27), (cx + 5, cy - 27), (cx + 12, cy - 24)) + \
        bez((cx + 12, cy - 24), (cx + 16, cy - 16), (cx + 18, cy - 4), (cx + 17, cy + 18)) + \
        [(cx + 13, cy + 24), (cx + 7, cy + 22)] + bez((cx + 7, cy + 22), (cx + 3, cy + 19), (cx - 3, cy + 19), (cx - 7, cy + 22))
    form(plate, STEEL, W, sdx=-2.6, sdy=0, sh=0.28)
    stroke([(cx, cy + 19), (cx, cy - 26)], 0.6, g=STEEL_D)
    hl(bez((cx - 10, cy + 16), (cx - 13, cy + 2), (cx - 12, cy - 10), (cx - 9, cy - 20)), 1.2, 0.5)
    hl([(cx + 3, cy + 15), (cx + 3, cy - 20)], 0.6, 0.35)
    for i in range(3):
        y = cy - 28 - i * 4.5
        lame = bez((cx - 12 + i, y), (cx - 4, y - 2.5), (cx + 4, y - 2.5), (cx + 12 - i, y)) + \
            bez((cx + 12 - i, y - 4), (cx + 4, y - 6.5), (cx - 4, y - 6.5), (cx - 12 + i, y - 4))
        form(lame, STEEL_D, W * 0.8, sdx=0, sdy=1, sh=0.2)
    for sx in (-1, 1):
        stroke([(cx + sx * 13, cy + 24), (cx + sx * 15, cy + 31)], 1.6, g=LEATHER)
        shape(rrect(cx + sx * 14 - 1.6, cy + 20, 3.2, 3, 0.6), BRASS, W * 0.5)
    stroke(bez((cx - 12, cy - 24), (cx - 5, cy - 27), (cx + 5, cy - 27), (cx + 12, cy - 24)), 1.2, g=BRASS)
    for x in (-8, 8):
        rivet(cx + x, cy - 22, 0.8, BRASS)


@item(2, 3)
def platova_zbroj(b):
  with T(b.w * 0.07, b.h * 0.07, 0.86):
    cx, cy = b.w / 2, b.h / 2 - 2
    for sx in (-1, 1):
        paul = bez((cx + sx * 9, cy + 26), (cx + sx * 22, cy + 30), (cx + sx * 28, cy + 22), (cx + sx * 27, cy + 10)) + \
            bez((cx + sx * 27, cy + 10), (cx + sx * 22, cy + 13), (cx + sx * 16, cy + 14), (cx + sx * 12, cy + 12))
        form(paul, STEEL_D, W, sdx=sx * 1.5, sdy=1.5, sh=0.25)
        for k in (1, 2):
            stroke(bez((cx + sx * 15, cy + 14 - k * 4.5), (cx + sx * 21, cy + 15 - k * 4.5), (cx + sx * 25, cy + 13 - k * 4.5), (cx + sx * 27, cy + 10 - k * 4.5)), 2.4, g=STEEL_D)
    plate = bez((cx - 9, cy + 28), (cx - 18, cy + 24), (cx - 18, cy - 10), (cx - 13, cy - 20)) + \
        [(cx + 13, cy - 20)] + bez((cx + 13, cy - 20), (cx + 18, cy - 10), (cx + 18, cy + 24), (cx + 9, cy + 28))
    form(plate, STEEL, W, sdx=-2.6, sdy=0, sh=0.28)
    stroke([(cx, cy + 27), (cx, cy - 20)], 0.6, g=STEEL_D)
    hl(bez((cx - 10, cy + 20), (cx - 14, cy + 6), (cx - 13, cy - 8), (cx - 10, cy - 16)), 1.2, 0.5)
    for i in range(4):
        y = cy - 20 - i * 4.2
        lame = [(cx - 13 + i * 0.5, y), (cx + 13 - i * 0.5, y), (cx + 12.5 - i * 0.5, y - 4.6), (cx - 12.5 + i * 0.5, y - 4.6)]
        form(lame, STEEL_D if i % 2 else STEEL, W * 0.8, sdx=0, sdy=1, sh=0.2)
        rivet(cx - 10 + i * 0.5, y - 2.3, 0.6); rivet(cx + 10 - i * 0.5, y - 2.3, 0.6)
    gorget = bez((cx - 9, cy + 28), (cx - 4, cy + 33), (cx + 4, cy + 33), (cx + 9, cy + 28)) + \
        bez((cx + 9, cy + 28), (cx + 4, cy + 30), (cx - 4, cy + 30), (cx - 9, cy + 28))
    shape(gorget, GOLD, W * 0.7)
    shape(ell(cx, cy + 8, 3.5, 3.5, 16), GOLD, W * 0.6)


# ------------------------------------------------------------------ belts
@item(2, 1)
def opasek(b):
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=-6):
        strap = bez((-25, -1), (-10, 3), (10, 3), (24, -1)) + bez((24, -7), (10, -3), (-10, -3), (-25, -7))
        form(strap, LEATHER, W, sdx=0, sdy=1.2, sh=0.2)
        stroke(bez((-24, -2.5), (-10, 1.5), (10, 1.5), (23, -2.5)), 0.3, g=LEATHER_L)
        for x in (12, 16, 20):
            dot(x, -2.6 + (x - 12) * -0.15, 0.6, LEATHER_D)
        stroke(rrect(-7, -6.5, 9, 9.5, 1.5), 1.6, closed=True, g=IRON_L)
        stroke(rrect(-7, -6.5, 9, 9.5, 1.5), 0.5, closed=True)
        stroke([(-2.5, -6.5), (-2.5, 3)], 0.9, g=IRON)
        shape([(-25, -1), (-29, -3), (-25, -7)], LEATHER_D, W * 0.7)


@item(2, 1)
def siroky_opasek(b):
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=-5):
        strap = bez((-26, 4), (-10, 8), (10, 8), (26, 4)) + bez((26, -9), (10, -5), (-10, -5), (-26, -9))
        form(strap, LEATHER_D, W, sdx=0, sdy=1.6, sh=0.22)
        for x in range(-22, 24, 5):
            yy = 1.5 - (x / 26) ** 2 * 4
            for dy in (-3.2, 0, 3.2):
                dot(x, yy + dy, 0.75, BRASS_L)
        for k, x in enumerate((-12, -2, 8)):
            shape(rrect(x - 3, -5.5 - abs(x) * 0.03, 6, 12, 1.2), BRASS, W * 0.6)
            stroke([(x, -5), (x, 6)], 0.5, g=GOLD_D)
        stroke(bez((-26, 3), (-10, 7), (10, 7), (26, 3)), 0.5, g=RED)
        stroke(bez((-26, -8), (-10, -4), (10, -4), (26, -8)), 0.5, g=RED)


# ------------------------------------------------------------------ lamps
def hook(x, y, top, g=IRON):
    stroke([(x, y), (x, top - 4)], 0.9, g=g)
    stroke(bez((x, top - 4), (x, top), (x + 4, top), (x + 4, top - 3)), 0.9, g=g)


@item(1, 2)
def lojovy_kahan(b):
    cx = b.w / 2
    hook(cx - 2, 18, 50)
    stroke(bez((cx - 2, 20), (cx - 6, 20), (cx - 8, 18), (cx - 8, 14)), 0.9, g=IRON)
    dish = bez((cx - 10, 14), (cx - 10, 4), (cx + 4, 3), (cx + 9, 9)) + [(cx + 12, 15), (cx + 6, 13)] + \
        bez((cx + 6, 13), (cx + 2, 14), (cx - 4, 14.5), (cx - 10, 14))
    form(dish, K("#8a6a4a", 0.5), W, sdx=-1.2, sdy=1.2, sh=0.25)
    shape(ell(cx - 1.5, 13.5, 7.2, 1.6, 20), K("#e9dcae", 0.88), W * 0.5)
    stroke([(cx + 9, 13), (cx + 10.5, 16)], 0.6, g=K("#2a2a2a", 0.2))
    flame(cx + 10.5, 15.5, 9, lean=-1)
    hook(cx - 2, 20, 52)


@item(1, 2)
def havirsky_kahan(b):
    cx = b.w / 2
    stroke(bez((cx, 34), (cx - 1, 42), (cx + 6, 48), (cx + 5, 52)), 0.9, g=IRON)
    stroke(bez((cx + 5, 52), (cx + 4, 55), (cx + 1, 54.5), (cx + 1.5, 52)), 0.8, g=IRON)
    body = bez((cx - 10, 14), (cx - 11, 26), (cx - 5, 33), (cx, 34)) + bez((cx, 34), (cx + 5, 33), (cx + 11, 26), (cx + 10, 14)) + \
        bez((cx + 10, 14), (cx + 8, 8), (cx - 8, 8), (cx - 10, 14))
    form(body, IRON, W, sdx=-1.8, sdy=0, sh=0.25)
    hl(bez((cx - 6, 14), (cx - 7.5, 22), (cx - 4, 29), (cx - 1, 31)), 0.8, 0.45)
    stroke(bez((cx - 10, 14), (cx - 5, 11), (cx + 5, 11), (cx + 10, 14)), 0.9, g=BRASS)
    spout = [(cx + 6, 26), (cx + 13, 34), (cx + 15, 33), (cx + 9, 23)]
    shape(spout, IRON_L, W * 0.7)
    flame(cx + 14, 33.5, 10, lean=0.5)
    foot = [(cx - 7, 9), (cx + 7, 9), (cx + 6, 5), (cx - 6, 5)]
    shape(foot, IRON_D, W * 0.7)
    rivet(cx - 4, 20, 0.7, BRASS); rivet(cx + 4, 20, 0.7, BRASS)


@item(1, 2)
def mosazny_kahan(b):
    cx = b.w / 2
    stroke(bez((cx - 6, 40), (cx - 6, 50), (cx + 6, 50), (cx + 6, 40)), 0.9, g=BRASS)
    cap = [(cx - 8, 38)] + bez((cx - 8, 38), (cx - 7, 44), (cx + 7, 44), (cx + 8, 38))
    form(cap, BRASS, W * 0.8, sh=0.2)
    glass = rect(cx - 7, 16, 14, 22)
    glow(cx, 26, 11, "#ffcc60", 0.55)
    shape(glass, K("#f6e2a0", 0.9, 0.45), W * 0.7)
    flame(cx, 20, 11)
    for x in (-7, 0, 7):
        stroke([(cx + x, 16), (cx + x, 38)], 1.1 if x else 0.7, g=BRASS)
    base = [(cx - 9, 16), (cx + 9, 16), (cx + 8, 8), (cx - 8, 8)]
    form(base, BRASS, W, sdx=-1.4, sdy=0, sh=0.25)
    hl([(cx - 5, 9.5), (cx - 5.5, 14.5)], 0.6, 0.7)
    stroke([(cx - 9, 16), (cx + 9, 16)], 1.0, g=GOLD_D)
    stroke([(cx - 8.5, 38), (cx + 8.5, 38)], 1.0, g=GOLD_D)
    hl([(cx - 5, 18), (cx - 5, 35)], 0.6, 0.5)


@item(1, 2)
def karbidka(b):
    cx = b.w / 2 - 1
    lower = rrect(cx - 7, 6, 14, 14, 2)
    form(lower, STEEL_D, W, sdx=-1.4, sdy=0, sh=0.25)
    upper = rrect(cx - 6, 21, 12, 14, 2)
    form(upper, BRASS, W, sdx=-1.4, sdy=0, sh=0.25)
    stroke([(cx - 7.5, 20.5), (cx + 7.5, 20.5)], 1.6, g=IRON)
    for x in (-5, 0, 5):
        rivet(cx + x, 20.5, 0.55, BRASS)
    shape(ell(cx, 37, 2.5, 2, 12), BRASS, W * 0.7)
    stroke(bez((cx, 38), (cx, 44), (cx + 3, 47), (cx + 2, 51)), 0.9, g=IRON)
    stroke(bez((cx + 2, 51), (cx + 1, 54), (cx - 2, 53), (cx - 1.5, 51)), 0.8, g=IRON)
    hl([(cx - 4, 23), (cx - 4, 33)], 0.6, 0.6)
    refl = ell(cx + 10, 28, 4, 7, 24)
    form(refl, SILVER, W * 0.8, sdx=1, sdy=0, sh=0.2)
    stroke([(cx + 6, 28), (cx + 9, 28)], 0.9, g=BRASS)
    flame(cx + 10, 27, 7, lean=0.3)


@item(1, 2)
def permonikuv_kahan(b):
    cx = b.w / 2
    glow(cx, 26, 15, "#a8dcff", 0.45)
    stroke(bez((cx, 33), (cx - 1, 40), (cx + 5, 45), (cx + 4, 49)), 0.8, g=SILVER_D)
    stroke(bez((cx + 4, 49), (cx + 3, 52), (cx, 51.5), (cx + 0.5, 49)), 0.7, g=SILVER_D)
    body = bez((cx - 7, 14), (cx - 8, 24), (cx - 4, 30), (cx, 31)) + bez((cx, 31), (cx + 4, 30), (cx + 8, 24), (cx + 7, 14)) + \
        bez((cx + 7, 14), (cx + 5, 10), (cx - 5, 10), (cx - 7, 14))
    form(body, SILVER_D, W, sdx=-1.4, sdy=0, sh=0.25)
    hl(bez((cx - 4, 14), (cx - 5, 20), (cx - 3, 26), (cx - 1, 28)), 0.7, 0.6)
    stroke(bez((cx - 7, 14), (cx - 3, 12), (cx + 3, 12), (cx + 7, 14)), 0.8, g=SILVER_L)
    spout = [(cx + 4, 24), (cx + 9, 30), (cx + 11, 29), (cx + 6.5, 21.5)]
    shape(spout, SILVER, W * 0.6)
    flame(cx + 10, 29.5, 10, cold=True, lean=0.4)
    shape([(cx - 5, 10.5), (cx + 5, 10.5), (cx + 4, 7), (cx - 4, 7)], SILVER_D, W * 0.6)
    sparkle(cx + 10, 34, 2.4, "#ffffff")


# ------------------------------------------------------------------ jewellery
@item(1, 1)
def prsten(b):
    cx, cy = b.w / 2, b.h / 2 - 2
    outer = ell(cx, cy, 9.5, 8, 36); inner = ell(cx, cy + 0.8, 6.8, 5.4, 36)
    C.saveState()
    p = C.beginPath(); p.moveTo(*outer[0]); [p.lineTo(*q) for q in outer[1:]]; p.close()
    p.moveTo(*inner[0]); [p.lineTo(*q) for q in inner[1:]]; p.close()
    C.restoreState()
    stroke(ell(cx, cy, 8.1, 6.7, 36), 2.8, closed=True, g=GOLD)
    stroke(ell(cx, cy, 9.6, 8.1, 36), 0.6, closed=True); stroke(ell(cx, cy + 0.7, 6.7, 5.3, 36), 0.6, closed=True)
    hl(ell(cx, cy, 8.4, 7, 14, 120, 200), 0.6, 0.8)
    shape([(cx - 4, cy + 6), (cx + 4, cy + 6), (cx + 3, cy + 9), (cx - 3, cy + 9)], GOLD_D, W * 0.6)
    glow(cx, cy + 11, 6, "#ff5050", 0.3)
    gem = ell(cx, cy + 11, 4, 3.2, 16)
    shape(gem, RED_L, W * 0.7)
    flat(ell(cx - 1, cy + 12, 1.4, 1, 10), "#ffffff", 0.8)


@item(1, 1)
def prsten_b(b):
    cx, cy = b.w / 2, b.h / 2 - 2
    stroke(ell(cx, cy, 8.1, 6.7, 36), 2.4, closed=True, g=SILVER)
    stroke(ell(cx, cy, 9.4, 7.9, 36), 0.6, closed=True); stroke(ell(cx, cy + 0.6, 6.8, 5.5, 36), 0.6, closed=True)
    hl(ell(cx, cy, 8.4, 7, 14, 120, 200), 0.6, 0.8)
    glow(cx, cy + 10, 7, "#60b0ff", 0.35)
    gem = [(cx - 4.5, cy + 10), (cx - 2.5, cy + 13.5), (cx + 2.5, cy + 13.5), (cx + 4.5, cy + 10), (cx, cy + 5.5)]
    shape(gem, BLUE_L, W * 0.7)
    stroke([(cx - 4.5, cy + 10), (cx + 4.5, cy + 10)], 0.35, g=BLUE)
    stroke([(cx, cy + 5.5), (cx - 1.5, cy + 10), (cx, cy + 13.5)], 0.35, g=BLUE)
    for sx in (-1, 1):
        dot(cx + sx * 5.5, cy + 8, 0.9, SILVER_L)


def cord(cx, top, y):
    stroke(bez((cx - 9, top), (cx - 9, y + 6), (cx - 4, y + 3), (cx, y + 1)), 0.6, g=LEATHER_D)
    stroke(bez((cx + 9, top), (cx + 9, y + 6), (cx + 4, y + 3), (cx, y + 1)), 0.6, g=LEATHER_D)


@item(1, 1)
def lunice(b):
    cx, cy = b.w / 2, b.h / 2 - 3
    cord(cx, 27, cy + 7)
    shape(ell(cx, cy + 7.5, 1.6, 1.6, 10), SILVER, W * 0.5)
    outer = ell(cx, cy, 10, 9, 30, 180, 360)
    inner = list(reversed(ell(cx, cy + 0.5, 6, 4.5, 30, 180, 360)))
    moon = outer + inner
    form(moon, SILVER, W * 0.8, sdx=0, sdy=1.4, sh=0.2)
    for i in range(7):
        a = math.radians(195 + i * 25)
        dot(cx + math.cos(a) * 8, cy + 0.3 + math.sin(a) * 6.8, 0.75, SILVER_L)
    for sx in (-1, 1):
        dot(cx + sx * 10, cy + 0.2, 1.1, SILVER); stroke(ell(cx + sx * 10, cy + 0.2, 1.1, 1.1, 8), 0.4, closed=True)
    for i in range(3):
        dot(cx - 2 + i * 2, cy - 9.8, 0.8, SILVER_D)
    hl(ell(cx, cy, 8.8, 7.8, 10, 200, 250), 0.6, 0.8)


@item(1, 1)
def kaptorga(b):
    cx, cy = b.w / 2, b.h / 2 - 3
    cord(cx, 27, cy + 8)
    box = [(cx - 7, cy + 7), (cx + 7, cy + 7), (cx + 7.5, cy - 7), (cx, cy - 10), (cx - 7.5, cy - 7)]
    form(box, GOLD, W * 0.8, sdx=-1.2, sdy=0, sh=0.25)
    shape([(cx - 5, cy + 5), (cx + 5, cy + 5), (cx + 5.3, cy - 6), (cx, cy - 8), (cx - 5.3, cy - 6)], GOLD_D, W * 0.4)
    stroke(ell(cx, cy - 0.5, 3, 3, 16), 0.5, closed=True, g=GOLD_L)
    for i in range(8):
        a = math.radians(i * 45)
        dot(cx + math.cos(a) * 3, cy - 0.5 + math.sin(a) * 3, 0.45, GOLD_L)
    dot(cx, cy - 0.5, 1.0, RED_L)
    for x in (-5, 0, 5):
        dot(cx + x, cy + 8, 0.7, GOLD_L)


# ------------------------------------------------------------------ consumables
def flask(cx, base, w, h, neck, liquid, glow_hex, level=0.7, cork=WOOD_L):
    body = bez((cx - neck, base + h), (cx - neck, base + h * 0.75), (cx - w, base + h * 0.65), (cx - w, base + h * 0.35)) + \
        bez((cx - w, base + h * 0.35), (cx - w, base), (cx + w, base), (cx + w, base + h * 0.35)) + \
        bez((cx + w, base + h * 0.35), (cx + w, base + h * 0.65), (cx + neck, base + h * 0.75), (cx + neck, base + h))
    glow(cx, base + h * 0.35, w * 1.5, glow_hex, 0.35)
    fill(body, K("#e8f0f0", 0.9, 0.25))
    lvl = base + h * level * 0.6
    C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
    liq = rect(cx - w - 2, base - 2, 2 * w + 4, lvl - base + 2)
    S.fill(liq, liquid)
    offset_shadow(liq, w * 0.5, 0, 0.25)
    flat(ell(cx, lvl, w, w * 0.18, 20), "#ffffff", 0.25)
    C.restoreState()
    stroke(body, W, closed=True)
    hl(bez((cx - w * 0.65, base + h * 0.25), (cx - w * 0.75, base + h * 0.45), (cx - w * 0.6, base + h * 0.6), (cx - neck * 0.6, base + h * 0.75)), 0.8, 0.8)
    c = rrect(cx - neck - 0.6, base + h - 1, 2 * neck + 1.2, 4.5, 1)
    shape(c, cork, W * 0.7)
    stroke([(cx - neck - 0.8, base + h - 0.8), (cx + neck + 0.8, base + h - 0.8)], 0.8, g=K("#6b3a2a", 0.3))


@item(1, 1)
def ziva_voda(b):
    flask(b.w / 2, 2.5, 7.5, 19, 2.6, K("#c8282e", 0.4), "#ff4040")


@item(1, 1)
def ziva_voda_velka(b):
    flask(b.w / 2, 1.5, 10, 21, 3.0, K("#c8282e", 0.4), "#ff4040", level=0.8)
    stroke([(b.w / 2 - 3, 19), (b.w / 2 + 3, 19)], 0.6, g=RED_D)


def vial(cx, base, w, h, liquid, glow_hex, cork=WOOD_L):
    body = [(cx - w, base + h)] + bez((cx - w, base + 3), (cx - w, base - 1), (cx + w, base - 1), (cx + w, base + 3)) + [(cx + w, base + h)]
    glow(cx, base + h * 0.4, w * 2.6, glow_hex, 0.35)
    fill(body, K("#e8f0f0", 0.9, 0.25))
    C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
    liq = rect(cx - w - 1, base - 2, 2 * w + 2, h * 0.68)
    S.fill(liq, liquid)
    offset_shadow(liq, w * 0.6, 0, 0.25)
    C.restoreState()
    stroke(body, W, closed=True)
    stroke([(cx - w - 1.2, base + h), (cx + w + 1.2, base + h)], 1.2, g=K("#c0c8cc", 0.8))
    shape(rrect(cx - w + 0.6, base + h, 2 * w - 1.2, 4, 0.8), cork, W * 0.6)
    hl([(cx - w * 0.5, base + 3), (cx - w * 0.5, base + h - 2)], 0.7, 0.8)


@item(1, 1)
def svatojanska_rosa(b):
    with T(b.w / 2, 0, 1.0, rot=-10):
        vial(0, 3, 4.2, 18, K("#3a7fe0", 0.5), "#60b0ff")
    sparkle(b.w / 2 + 6, 20, 2.2, "#dff3ff")


@item(1, 1)
def svatojanska_rosa_velka(b):
    flask(b.w / 2, 1.5, 9.5, 21, 2.8, K("#3a7fe0", 0.5), "#60b0ff", level=0.8)
    sparkle(b.w / 2 + 5, 15, 2, "#ffffff")
    sparkle(b.w / 2 - 4, 9, 1.4, "#dff3ff")


@item(1, 1)
def kapradi_kvet(b):
    cx, cy = b.w / 2, b.h / 2 - 1
    for sx in (-1, 1):
        for k in range(3):
            y0 = cy - 8 + k * 4
            fr = bez((cx, y0), (cx + sx * 5, y0 - 1), (cx + sx * 9, y0 - 4), (cx + sx * 12, y0 - 9 + k * 2))
            stroke(fr, 0.9, g=MOSS)
            for t in range(1, 4):
                px, py = fr[t * 4]
                stroke([(px, py), (px + sx * 1.5, py - 2.4)], 0.6, g=GREEN)
    stroke(bez((cx, cy - 13), (cx - 1, cy - 5), (cx + 1, cy), (cx, cy + 3)), 1.0, g=GREEN)
    glow(cx, cy + 5, 13, "#ffe070", 0.6)
    for i in range(5):
        a = math.radians(90 + i * 72)
        pet = ell(cx + math.cos(a) * 3.6, cy + 5 + math.sin(a) * 3.6, 3.6, 1.9, 14, rot=math.degrees(a))
        shape(pet, K("#ff7a3a", 0.6), W * 0.5)
    dot(cx, cy + 5, 2.4, K("#fff2a0", 0.95))
    for (x, y, r) in ((-8, 9, 1.6), (8, 12, 1.3), (5, -1, 1.0), (-6, 1, 1.0)):
        sparkle(cx + x, cy + y, r, "#fff6c0")


def scroll(b, seal_hex, sym):
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=-30):
        body = rect(-6, -10, 12, 20)
        form(body, PARCH, W, sdx=-1.4, sdy=0, sh=0.22)
        for y in (-10, 10):
            shape(ell(0, y, 6.5, 2.4, 20), PARCH_D, W * 0.7)
            shape(ell(0, y + (1 if y > 0 else -1) * 0.2, 1.6, 1.0, 10), K("#6b4e2a", 0.3), W * 0.4)
        stroke([(-6, -3), (6, -3)], 1.4, g=K("#7a2a1a", 0.3))
        seal = ell(3, -3, 3.6, 3.6, 20)
        shape(seal, K(seal_hex, 0.4), W * 0.6)
        sym(3, -3)
        stroke(bez((1, -6), (0, -9), (2, -12), (1, -14)), 0.8, g=K("#7a2a1a", 0.3))


@item(1, 1)
def svitek_brana(b):
    def sym(x, y):
        stroke(bez((x - 1.4, y - 1.6), (x - 1.4, y + 1.8), (x + 1.4, y + 1.8), (x + 1.4, y - 1.6)), 0.5, g=K("#ffd0c0", 0.9))
    scroll(b, "#b8282a", sym)
    glow(b.w / 2 + 5, b.h / 2 - 2, 6, "#7cc4ff", 0.15)


@item(1, 1)
def svitek_zjeveni(b):
    def sym(x, y):
        stroke(bez((x - 2, y), (x - 1, y + 1.4), (x + 1, y + 1.4), (x + 2, y)), 0.4, g=K("#e0f0ff", 0.9))
        stroke(bez((x - 2, y), (x - 1, y - 1.4), (x + 1, y - 1.4), (x + 2, y)), 0.4, g=K("#e0f0ff", 0.9))
        dot(x, y, 0.6, K("#e0f0ff", 0.9))
    scroll(b, "#2c58a0", sym)


# ------------------------------------------------------------------ gold
@item(1, 1)
def grose_malo(b):
    cx, cy = b.w / 2, b.h / 2
    coin(cx - 4, cy - 4, 6, SILVER, SILVER_D, 0.55)
    coin(cx + 4, cy - 2, 6, SILVER, SILVER_D, 0.55)
    coin(cx, cy + 4, 6.4, SILVER, SILVER_D, 0.85)


@item(1, 1)
def grose_hromadka(b):
    cx, cy = b.w / 2, b.h / 2
    for i in range(6):
        coin(cx - 6 + (i % 2) * 1.2, cy - 8 + i * 2.2, 5.6, SILVER, SILVER_D, 0.4, mark=False)
    coin(cx + 6, cy - 7, 5.5, SILVER, SILVER_D, 0.4, mark=False)
    coin(cx + 6.6, cy - 5, 5.5, SILVER, SILVER_D, 0.4, mark=False)
    coin(cx + 5, cy + 3, 6, SILVER, SILVER_D, 0.9)


@item(1, 1)
def grose_hodne(b):
    cx, cy = b.w / 2, b.h / 2
    pouch = bez((cx - 4, cy + 6), (cx - 13, cy + 4), (cx - 14, cy - 10), (cx - 6, cy - 11)) + \
        bez((cx - 6, cy - 11), (cx, cy - 12), (cx + 2, cy - 8), (cx + 1, cy + 6))
    form(pouch, LEATHER, W, sdx=-1.4, sdy=0, sh=0.22)
    stroke([(cx - 5, cy + 6), (cx + 1, cy + 6)], 1.0, g=RED)
    shape([(cx - 5, cy + 6), (cx - 7, cy + 11), (cx - 1, cy + 9), (cx + 2, cy + 11), (cx + 1, cy + 6)], LEATHER, W * 0.7)
    for (x, y, t) in ((5, -10, 0.4), (11, -10, 0.4), (7, -7.5, 0.4), (3, -4.5, 0.45), (10, -4, 0.45), (6.5, -1, 0.5)):
        coin(cx + x, cy + y, 4.6, SILVER, SILVER_D, t, mark=False)
    coin(cx + 7, cy + 5, 5.2, SILVER, SILVER_D, 0.85)
    sparkle(cx + 10, cy + 9, 2.2)


# ------------------------------------------------------------------ quest
@item(1, 2)
def srdce_zvonu(b):
    cx = b.w / 2
    with T(cx, b.h / 2, 1.0, rot=-8):
        stroke(bez((0, 20), (-4, 24), (-1, 27), (0, 25)), 1.2, g=IRON)
        shape(ell(0, 21, 2.6, 2.6, 16), IRON_D, W * 0.8)
        rod = [(-1.6, 18.5), (1.6, 18.5), (2.2, -6), (-2.2, -6)]
        form(rod, IRON, W, sdx=-0.8, sdy=0, sh=0.25)
        ball = bez((-2.2, -6), (-8, -10), (-8, -22), (0, -23.5)) + bez((0, -23.5), (8, -22), (8, -10), (2.2, -6))
        form(ball, IRON, W, sdx=-2, sdy=0.8, sh=0.28)
        hl(bez((-4, -9), (-6, -13), (-5.5, -18), (-3, -20)), 0.9, 0.5)
        stroke([(0.5, 12), (0.6, -4)], 0.5, g=IRON_L, alpha=0.7)
        glow(0, -15, 10, "#ffd070", 0.18)
        stroke(bez((-3, 8), (-6, 5), (-4, 2), (-7, -1)), 0.5, g=RUST_L, alpha=0.8)


@item(1, 1)
def strana_kroniky(b):
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=6):
        page = [(-10, -12)] + bez((-10, -12), (-4, -11), (4, -13), (10, -12)) + [(10.5, 12)] + bez((10.5, 12), (4, 13), (-4, 11.5), (-10.5, 12.5))
        form(page, PARCH, W, sdx=-1, sdy=1, sh=0.2)
        for k in range(7):
            y = 8 - k * 2.8
            stroke([(-7.5 + (k == 0) * 3, y), (7.5 - (k % 3) * 1.5, y + 0.2)], 0.35, g=INK, alpha=0.7)
        shape(rect(-7.5, 6.5, 3, 3.5), K("#a82a2a", 0.4), W * 0.3)
        tear = [(6, -12.5), (10.5, -7), (10.5, -12.5)]
        shape(tear, PARCH_D, W * 0.5)


@item(1, 1)
def zlaty_sin(b):
    cx, cy = b.w / 2, b.h / 2
    top = [(cx - 10, cy + 1), (cx + 3, cy + 7), (cx + 12, cy + 3), (cx - 1, cy - 3)]
    front = [(cx - 10, cy + 1), (cx - 1, cy - 3), (cx - 1, cy - 9), (cx - 11, cy - 4.5)]
    side = [(cx - 1, cy - 3), (cx + 12, cy + 3), (cx + 12, cy - 3), (cx - 1, cy - 9)]
    shape(side, GOLD_D, W * 0.8)
    shape(front, GOLD, W * 0.8)
    shape(top, GOLD_L, W * 0.8)
    stroke([(cx - 4, cy + 1.5), (cx + 4, cy + 4.5)], 0.45, g=GOLD_D)
    sparkle(cx - 4, cy + 3, 2.6)
    sparkle(cx + 9, cy + 7, 1.6)


@item(1, 1)
def kostejova_jehla(b):
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=-45):
        glow(0, 0, 10, "#b080ff", 0.3)
        nd = [(-0.9, -12), (0, -14.5), (0.9, -12), (1.1, 11), (-1.1, 11)]
        shape(nd, SILVER, W * 0.6)
        eye = ell(0, 12.5, 1.6, 2.6, 16)
        stroke(eye, 0.9, closed=True, g=SILVER)
        stroke(ell(0, 12.5, 2.1, 3.1, 16), 0.4, closed=True)
        hl([(-0.3, -11), (-0.3, 9)], 0.4, 0.9)
        stroke(bez((0, 15), (3, 18), (-2, 20), (2, 23)), 0.5, g=K("#c02a2a", 0.4))
    sparkle(cx + 7, cy + 7, 2.4, "#efe0ff")


@item(1, 1)
def vejce(b):
    cx, cy = b.w / 2, b.h / 2 - 1
    glow(cx, cy, 12, "#ffe8a0", 0.25)
    egg = bez((cx, cy - 10), (cx - 9, cy - 10), (cx - 8, cy + 6), (cx, cy + 11)) + bez((cx, cy + 11), (cx + 8, cy + 6), (cx + 9, cy - 10), (cx, cy - 10))
    form(egg, K("#efe6d4", 0.92), W, sdx=-1.6, sdy=0.6, sh=0.2)
    stroke([(cx - 7, cy - 1), (cx - 4, cy + 1.5), (cx - 1, cy - 1.5), (cx + 2, cy + 1.5), (cx + 5, cy - 1), (cx + 7.4, cy + 0.6)], 0.5, g=INK)
    hl(ell(cx - 3, cy + 4, 2, 3, 10, 90, 200), 0.7, 0.8)
    for (x, y) in ((-3, -5), (3, -6), (1, 6), (-4, 5.5)):
        dot(cx + x, cy + y, 0.5, K("#b49a70", 0.6))


@item(1, 1)
def mrtva_voda(b):
    flask(b.w / 2, 2.5, 7.5, 19, 2.6, K("#3a4a3e", 0.3), "#7a9a80", level=0.75, cork=WOOD_D)
    dot(b.w / 2 - 2, 8, 0.9, K("#9ab8a0", 0.7)); dot(b.w / 2 + 2, 11, 0.6, K("#9ab8a0", 0.7))


@item(1, 1)
def hrnek(b):
    cx, cy = b.w / 2, b.h / 2 - 3
    glow(cx, cy + 4, 12, "#cfe8ff", 0.3)
    saucer = ell(cx, cy - 6, 12, 3.4, 30)
    form(saucer, K("#f4f2ec", 0.95), W * 0.8, sdx=0, sdy=1, sh=0.15)
    cup = [(cx - 8, cy + 6)] + bez((cx - 8, cy + 6), (cx - 8, cy - 4), (cx - 4, cy - 6), (cx, cy - 6)) + \
        bez((cx, cy - 6), (cx + 4, cy - 6), (cx + 8, cy - 4), (cx + 8, cy + 6))
    form(cup, K("#f4f2ec", 0.95), W, sdx=-1.6, sdy=0, sh=0.2)
    stroke(bez((cx + 7.5, cy + 3), (cx + 13, cy + 4), (cx + 12, cy - 3), (cx + 6.5, cy - 2)), 1.0, g=K("#f4f2ec", 0.95))
    stroke(bez((cx + 7.5, cy + 3), (cx + 13, cy + 4), (cx + 12, cy - 3), (cx + 6.5, cy - 2)), 0.4)
    shape(ell(cx, cy + 6, 8, 2, 24), K("#7a5a3a", 0.4), W * 0.7)
    stroke(bez((cx - 7, cy + 1), (cx - 3, cy - 1), (cx + 3, cy - 1), (cx + 7, cy + 1)), 0.6, g=K("#4a7ac0", 0.5))
    for x in (-4, 0, 4):
        dot(cx + x, cy - 2.8, 0.7, K("#c03a4a", 0.4))
    for k, x in enumerate((-3, 1.5)):
        stroke(bez((cx + x, cy + 9), (cx + x - 2, cy + 12), (cx + x + 2, cy + 14), (cx + x, cy + 17)), 0.6, g=K("#dff3ff", 0.97), alpha=0.8)


@item(1, 1)
def zrcadlo_strep(b):
    cx, cy = b.w / 2, b.h / 2
    sh = [(cx - 9, cy - 10), (cx + 3, cy - 12), (cx + 10, cy - 2), (cx + 5, cy + 12), (cx - 3, cy + 7), (cx - 10, cy + 3)]
    form(sh, K("#9fb4c4", 0.65), W, sdx=-1.4, sdy=0, sh=0.2)
    C.saveState(); C.clipPath(poly(sh), stroke=0, fill=0)
    flat([(cx - 12, cy - 4), (cx + 2, cy + 14), (cx + 6, cy + 14), (cx - 8, cy - 4)], "#ffffff", 0.55)
    flat([(cx - 2, cy - 14), (cx + 12, cy + 4), (cx + 14, cy + 2), (cx, cy - 14)], "#ffffff", 0.35)
    flat(ell(cx + 1, cy - 1, 5, 2.4, 20), "#2a3a50", 0.35)
    dot(cx - 0.6, cy - 1, 0.8, K("#ffd040", 0.85)); dot(cx + 2.6, cy - 1, 0.8, K("#ffd040", 0.85))
    C.restoreState()
    stroke([(cx - 4, cy - 10.8), (cx - 1, cy - 2), (cx + 7.5, cy + 3)], 0.4, g=K("#ffffff", 1), alpha=0.8)


if __name__ == "__main__":
    common.run({"items": ITEMS})
