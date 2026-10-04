"""Item icons added after the first set: class-only items, gems, Glagolitic letters, charms and keys."""
import math
import common
import lib
from icons_kit import *
from items import item, ITEMS as _BASE

ITEMS = []
CELL = 56


def more(w, h):
    def deco(fn):
        ITEMS.append((fn.__name__, w * CELL, h * CELL, fn)); return fn
    return deco


# ------------------------------------------------------------------ class-only items
@more(2, 2)
def faracka(b):
    """the miner's work cap, with the crossed hammer and wedge of the miners on the front"""
    cx, cy = b.w / 2, b.h / 2 - 4
    crown = bez((cx - 17, cy - 6), (cx - 18, cy + 14), (cx - 8, cy + 22), (cx + 2, cy + 22)) + \
        bez((cx + 2, cy + 22), (cx + 12, cy + 22), (cx + 19, cy + 12), (cx + 17, cy - 6))
    form(crown, K("#2d3138", 0.2), W, sdx=-2, sdy=0, sh=0.22)
    for k in range(5):
        x = cx - 12 + k * 6
        stroke(bez((x, cy - 4), (x - 1, cy + 6), (x + 1, cy + 14), (x + 2, cy + 20)), 0.4, g=K("#4a5059", 0.3), alpha=0.7)
    band_ = bez((cx - 18, cy - 8), (cx - 8, cy - 3), (cx + 8, cy - 3), (cx + 18, cy - 8)) + \
        bez((cx + 18, cy - 8), (cx + 17, cy - 13), (cx - 17, cy - 13), (cx - 18, cy - 8))
    form(band_, LEATHER_D, W * 0.9, sdx=0, sdy=1.4, sh=0.2)
    with T(cx, cy + 8, 1.0):
        for sgn in (1, -1):
            with T(0, 0, 1.0, rot=45 * sgn):
                tube([(0, -7), (0, 7)], 1.3, 1.2, WOOD_L, W * 0.5, sh=0)
                shape(rrect(-3.2, 5.5, 6.4, 3.2, 0.6) if sgn > 0 else [(-1.6, 5.5), (1.6, 5.5), (0, 10.5)], GOLD, W * 0.5)
    stroke(bez((cx + 12, cy - 9), (cx + 16, cy - 16), (cx + 20, cy - 16), (cx + 21, cy - 11)), 0.9, g=IRON)


@more(2, 1)
def zbojnicky_opasek(b):
    """the brigands' broad belt, brass hearts and studs, wide enough to stop a knife"""
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=-4):
        strap = bez((-26, 6), (-10, 10), (10, 10), (26, 6)) + bez((26, -11), (10, -7), (-10, -7), (-26, -11))
        form(strap, K("#6b4a2e", 0.32), W, sdx=0, sdy=1.6, sh=0.22)
        for x in range(-23, 25, 4):
            yy = 1 - (x / 26) ** 2 * 4
            dot(x, yy + 5.5, 0.7, BRASS_L)
            dot(x, yy - 6.5, 0.7, BRASS_L)
        for x in (-14, 0, 14):
            yy = -0.5 - (x / 26) ** 2 * 4
            heart = bez((x, yy - 4), (x - 6, yy), (x - 4, yy + 5), (x, yy + 2.5)) + bez((x, yy + 2.5), (x + 4, yy + 5), (x + 6, yy), (x, yy - 4))
            shape(heart, BRASS, W * 0.6)
            dot(x, yy + 0.5, 0.9, RED)


@more(2, 2)
def zarikadla(b):
    """a little book of charms, tied shut with red thread, herbs and a bone tucked under it"""
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=-10):
        for k, (dx, ang) in enumerate(((-12, 70), (-6, 82), (2, 96))):
            with T(dx, 14, 1.0, rot=ang):
                tube([(0, 0), (14, 0)], 1.2, 0.8, K("#6f8a4a", 0.45), W * 0.4, sh=0)
                for t in (5, 9, 13):
                    shape(ell(t, 2, 2.2, 1.0, 8, rot=30), K("#7f9a52", 0.5), W * 0.3)
        cover = rrect(-15, -16, 30, 30, 2.0)
        form(cover, K("#3e2f45", 0.22), W, sdx=-1.4, sdy=1.4, sh=0.25)
        shape(rect(-15, -16, 4, 30), K("#2a1f30", 0.15), W * 0.7)
        stroke([(-15, -1), (15, -1)], 1.4, g=RED)
        stroke([(2, -16), (2, 14)], 1.4, g=RED)
        stroke(bez((2, -1), (6, 4), (9, 3), (8, -1)), 0.9, g=RED)
        tube([(-8, -20), (12, -12)], 2.2, 1.6, BONE, W * 0.6, sh=0)
        for (x, y) in ((-6, 7), (8, 7), (-6, -10), (8, -10)):
            dot(x, y, 0.8, BONE_D)


@more(2, 3)
def zastera(b):
    """the smith's leather apron, scorched and studded"""
    cx, cy = b.w / 2, b.h / 2
    ap = [(cx - 11, cy + 30), (cx + 11, cy + 30), (cx + 15, cy + 8), (cx + 17, cy - 34), (cx - 17, cy - 34), (cx - 15, cy + 8)]
    form(ap, K("#6a4a30", 0.32), W, sdx=-2, sdy=1.4, sh=0.22)
    for (x, y) in ((-6, -10), (5, 2), (8, -22), (-3, 14), (-9, -26)):
        dot(cx + x, cy + y, 1.6, K("#2a1a10", 0.1))
    for sx in (-1, 1):
        stroke([(cx + sx * 11, cy + 30), (cx + sx * 6, cy + 40)], 1.6, g=K("#6a4a30", 0.32))
    shape(rect(cx - 8, cy - 4, 16, 9), K("#5a3c24", 0.3), W * 0.6)
    for x in (-5, 0, 5):
        rivet(cx + x, cy + 3, 0.8, BRASS)


@more(1, 2)
def obetni_nuz(b):
    """a bronze sacrificial knife with a bone grip and a red thread"""
    cx, cy = b.w / 2, b.h / 2
    with T(cx, cy, 1.0, rot=0):
        bl = [(-3, 2), (3, 2), (2, 22), (0, 27), (-2, 22)]
        form(bl, K("#b8873a", 0.6), W, sh=0.2)
        stroke([(0, 4), (0, 22)], 0.4, g=K("#f2d080", 0.9), alpha=0.8)
        shape(rect(-5, -1, 10, 3), K("#8a6a2a", 0.45), W * 0.7)
        tube([(0, -1), (0, -20)], 3.4, 3.0, BONE, W * 0.7, sh=0.15)
        for y in (-6, -12, -17):
            stroke([(-1.8, y), (1.8, y - 1)], 0.8, g=RED)


@more(2, 2)
def vlci_kape(b):
    """a hood made of a wolf's head, ears up, eyes of amber"""
    cx, cy = b.w / 2, b.h / 2
    hood = bez((cx - 18, cy - 18), (cx - 22, cy + 6), (cx - 12, cy + 18), (cx, cy + 18)) + bez((cx, cy + 18), (cx + 12, cy + 18), (cx + 22, cy + 6), (cx + 18, cy - 18))
    form(hood, K("#7a7670", 0.5), W, sh=0.22)
    hatch(hood, 1.5, 75, 0.35, alpha=0.3)
    for sx in (-1, 1):
        shape([(cx + sx * 6, cy + 14), (cx + sx * 12, cy + 26), (cx + sx * 15, cy + 12)], K("#4e4b47", 0.3), W * 0.7)
        shape(ell(cx + sx * 6, cy + 5, 2.4, 1.6, 12), K("#e8b040", 0.8), W * 0.5)
    shape([(cx - 4, cy - 2), (cx + 4, cy - 2), (cx, cy - 8)], INK, W * 0.5)


@more(2, 2)
def krivule(b):
    """a glass retort with a bubbling green tincture"""
    cx, cy = b.w / 2, b.h / 2
    body = ell(cx - 5, cy - 6, 13, 12, 26)
    shape(body, GLASS, W)
    clip_fill(body, rect(cx - 20, cy - 20, 30, 12), K("#86e05a", 0.55))
    tube(bez((cx + 5, cy + 2), (cx + 12, cy + 10), (cx + 18, cy + 8), (cx + 22, cy + 2)), 4, 2, GLASS, W * 0.8, sh=0)
    for (dx, dy, r) in ((-8, -10, 1.6), (-3, -13, 1.2), (-6, -6, 1.0)):
        stroke(ell(cx + dx, cy + dy, r, r, 10), 0.4, closed=True, g=K("#d8ffc0", 0.95))
    hl([(cx - 13, cy - 2), (cx - 10, cy + 4)], 1.0, 0.8)


@more(2, 2)
def vahadlo(b):
    """the puppeteer's wooden cross, strings hanging"""
    cx, cy = b.w / 2, b.h / 2 + 6
    tube([(cx - 20, cy + 6), (cx + 20, cy + 6)], 3.2, 3.0, WOOD, W * 0.7, sh=0.15)
    tube([(cx, cy + 16), (cx, cy - 6)], 3.2, 3.0, WOOD_L, W * 0.7, sh=0.15)
    for x0 in (-18, -8, 8, 18):
        line([(cx + x0, cy + 6), (cx + x0 * 0.8, cy - 24)], "#e8e2d4", 0.45, 0.85)
    line([(cx, cy - 6), (cx, cy - 26)], "#e8e2d4", 0.45, 0.85)
    shape(ell(cx, cy + 16, 2.2, 2.2, 12), K("#c8322e", 0.4), W * 0.5)


# ------------------------------------------------------------------ Czech gems (6 stones x 4 grades)
STONES = {"granat": ("#8e1a26", "#d84a4a"), "vltavin": ("#2f5e2a", "#7fbf5a"), "ametyst": ("#5a2f7e", "#b07fe0"),
          "achat": ("#7a4a2a", "#d8a070"), "kristal": ("#9fb4c4", "#f2f8ff"), "jaspis": ("#8a3a22", "#d0703e")}


def gem_icon(stone, grade):
    dark, light = STONES[stone]
    def draw(b):
        cx, cy = b.w / 2, b.h / 2
        r = 5.5 + grade * 1.9
        if grade == 1:
            pts = [(cx - r, cy - r * 0.4), (cx - r * 0.2, cy - r), (cx + r * 0.9, cy - r * 0.5), (cx + r * 0.6, cy + r * 0.8), (cx - r * 0.5, cy + r * 0.6)]
        else:
            n = 6 if grade < 4 else 8
            pts = [(cx + math.cos(2 * math.pi * i / n + 0.3) * r, cy + math.sin(2 * math.pi * i / n + 0.3) * r * 0.86) for i in range(n)]
        glow(cx, cy, r * 1.15, light, 0.18 + grade * 0.06)
        form(pts, K(dark, 0.3), W, sdx=-1.2, sdy=1.2, sh=0.25)
        inner = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55 + r * 0.06) for x, y in pts]
        shape(inner, K(light, 0.75), W * 0.6)
        for (x, y), (ix, iy) in zip(pts, inner):
            stroke([(x, y), (ix, iy)], 0.35, g=K(dark, 0.2), alpha=0.8)
        if stone == "achat":
            for k in range(3):
                stroke(ell(cx, cy, r * (0.75 - k * 0.18), r * (0.55 - k * 0.13), 24), 0.4, closed=True, g=K("#f2e0c0", 0.9), alpha=0.7)
        hl([(cx - r * 0.35, cy + r * 0.3), (cx - r * 0.05, cy + r * 0.45)], 0.8, 0.85)
        if grade >= 3:
            sparkle(cx + r * 0.45, cy + r * 0.5, 1.6 + grade * 0.4)
    return draw


for _st in STONES:
    for _g in range(1, 5):
        ITEMS.append(("%s_%d" % (_st, _g), CELL, CELL, gem_icon(_st, _g)))


# ------------------------------------------------------------------ Glagolitic letters on slate tablets
GLAG = {"a": 0x2C00, "o": 0x2C11, "e": 0x2C05, "i": 0x2C0B, "v": 0x2C02, "d": 0x2C04, "n": 0x2C10, "r": 0x2C13, "s": 0x2C14,
        "t": 0x2C15, "l": 0x2C0E, "k": 0x2C0D, "m": 0x2C0F, "p": 0x2C12, "u": 0x2C16, "g": 0x2C03, "b": 0x2C01, "c": 0x2C1D,
        "z": 0x2C06, "ch": 0x2C18, "ja": 0x2C21}
_FONT = None


def glyph_contours(cp):
    """the glyph's outline from Noto Sans Glagolitic as closed polylines, em-normalised"""
    global _FONT
    import os
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import RecordingPen
    if _FONT is None:
        _FONT = TTFont(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansGlagolitic-Regular.ttf"))
    gs = _FONT.getGlyphSet()
    name = _FONT.getBestCmap()[cp]
    pen = RecordingPen()
    gs[name].draw(pen)
    em = float(_FONT["head"].unitsPerEm)
    out, cur = [], []
    def q(p0, p1, p2, n=6):
        return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(1, n + 1)]]
    for op, args in pen.value:
        if op == "moveTo":
            cur = [args[0]]
        elif op == "lineTo":
            cur.append(args[0])
        elif op == "qCurveTo":
            pts = [cur[-1]] + list(args)
            # TrueType implied on-curve points between consecutive off-curve points
            for i in range(1, len(pts) - 1):
                p0 = pts[i - 1] if i == 1 else ((pts[i - 1][0] + pts[i][0]) / 2, (pts[i - 1][1] + pts[i][1]) / 2)
                p2 = pts[i + 1] if i == len(pts) - 2 else ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
                cur += q(p0, pts[i], p2)
        elif op == "curveTo":
            p0 = cur[-1]; c1, c2, p3 = args
            for t in [i / 8 for i in range(1, 9)]:
                cur.append(((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * c1[0] + 3 * (1 - t) * t * t * c2[0] + t ** 3 * p3[0],
                            (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * c1[1] + 3 * (1 - t) * t * t * c2[1] + t ** 3 * p3[1]))
        elif op in ("closePath", "endPath"):
            if len(cur) > 2:
                out.append([(x / em, y / em) for x, y in cur])
            cur = []
    return out


def letter_icon(lat):
    def draw(b):
        cx, cy = b.w / 2, b.h / 2
        tab = rrect(cx - 11.5, cy - 12.5, 23, 25, 3.5)
        form(tab, K("#4a4e57", 0.32), W, sdx=-1.4, sdy=1.4, sh=0.25)
        hatch(tab, 1.6, 30, 0.3, alpha=0.25)
        cs = glyph_contours(GLAG[lat])
        xs = [x for c in cs for x, _ in c]; ys = [y for c in cs for _, y in c]
        w_, h_ = max(xs) - min(xs), max(ys) - min(ys)
        k = 17.0 / max(w_, h_)
        ox, oy = cx - (min(xs) + w_ / 2) * k, cy - (min(ys) + h_ / 2) * k
        glow(cx, cy, 10, "#f2c040", 0.22)
        C.saveState()
        p = C.beginPath()
        for c in cs:
            p.moveTo(c[0][0] * k + ox, c[0][1] * k + oy)
            for x, y in c[1:]:
                p.lineTo(x * k + ox, y * k + oy)
            p.close()
        C.setFillColor(lib.G(K("#e9b840", 0.75)))
        C.drawPath(p, fill=1, stroke=0, fillMode=0)
        C.restoreState()
        for c in cs:
            stroke([(x * k + ox, y * k + oy) for x, y in c], 0.45, closed=True, g=K("#5a3a10", 0.2))
    return draw


for _l in GLAG:
    ITEMS.append(("glag_" + _l, CELL, CELL, letter_icon(_l)))


# ------------------------------------------------------------------ thunderstones (charms): polished stone axes
def thunderstone(kind):
    def draw(b):
        cx, cy = b.w / 2, b.h / 2
        L = {"maly": 10, "": 22, "velky": 34}[kind]
        wd = {"maly": 8.5, "": 9.5, "velky": 11}[kind]
        body = bez((cx - wd * 0.55, cy - L * 0.5), (cx - wd, cy - L * 0.1), (cx - wd, cy + L * 0.3), (cx - wd * 0.6, cy + L * 0.5)) + \
            bez((cx - wd * 0.6, cy + L * 0.5), (cx - wd * 0.2, cy + L * 0.62), (cx + wd * 0.2, cy + L * 0.62), (cx + wd * 0.6, cy + L * 0.5)) + \
            bez((cx + wd * 0.6, cy + L * 0.5), (cx + wd, cy + L * 0.3), (cx + wd, cy - L * 0.1), (cx + wd * 0.55, cy - L * 0.5)) + \
            bez((cx + wd * 0.55, cy - L * 0.5), (cx + wd * 0.2, cy - L * 0.6), (cx - wd * 0.2, cy - L * 0.6), (cx - wd * 0.55, cy - L * 0.5))
        glow(cx, cy, wd + L * 0.3, "#bfe0ff", 0.18)
        form(body, K("#5d6168", 0.38), W, sdx=-1.4, sdy=1.2, sh=0.25)
        hl([(cx - wd * 0.55, cy + L * 0.35), (cx - wd * 0.7, cy - L * 0.2)], 0.9, 0.5)
        if kind == "velky":
            shape(ell(cx, cy + L * 0.18, 2.6, 2.6, 16), K("#1e1f22", 0.1), W * 0.6)
        bolt = [(cx + 1.5, cy + L * 0.32), (cx - 2.5, cy + L * 0.02), (cx + 0.8, cy + L * 0.02), (cx - 1.8, cy - L * 0.3)]
        stroke(bolt, 1.2, g=K("#f2d060", 0.85))
        stroke(bolt, 0.45, g=K("#fff6c8", 0.98))
    return draw


ITEMS.append(("hromovy_kamen_maly", CELL, CELL, thunderstone("maly")))
ITEMS.append(("hromovy_kamen", CELL, CELL * 2, thunderstone("")))
ITEMS.append(("hromovy_kamen_velky", CELL, CELL * 3, thunderstone("velky")))


# ------------------------------------------------------------------ tithe keys and seals
EL = {"vody": "#4a8cc8", "kamene": "#8a8f98", "ohne": "#e06a2a", "smrti": "#d8d2c0"}


def emblem(el, x, y, r):
    col = K(EL[el], 0.6)
    if el == "vody":
        for k in range(2):
            stroke(bez((x - r, y - k * r * 0.6), (x - r * 0.4, y + r * 0.5 - k * r * 0.6), (x + r * 0.4, y - r * 0.5 - k * r * 0.6), (x + r, y - k * r * 0.6)), 0.9, g=col)
    elif el == "kamene":
        shape([(x + math.cos(a) * r, y + math.sin(a) * r) for a in [i * math.pi / 3 + 0.5 for i in range(6)]], col, W * 0.5)
    elif el == "ohne":
        shape(bez((x, y - r), (x - r, y - r * 0.2), (x - r * 0.3, y + r * 0.6), (x, y + r * 1.1)) + bez((x, y + r * 1.1), (x + r * 0.5, y + r * 0.4), (x + r, y - r * 0.2), (x, y - r)), col, W * 0.5)
    else:
        shape(bez((x - r, y), (x - r, y + r * 1.1), (x + r, y + r * 1.1), (x + r, y)) + [(x + r * 0.5, y - r * 0.8), (x - r * 0.5, y - r * 0.8)], col, W * 0.5)
        dot(x - r * 0.4, y + r * 0.2, r * 0.25, 0.1); dot(x + r * 0.4, y + r * 0.2, r * 0.25, 0.1)


def key_icon(el):
    def draw(b):
        cx, cy = b.w / 2, b.h / 2
        with T(cx, cy, 1.0, rot=-35):
            tube([(-2, 0), (16, 0)], 2.6, 2.4, K("#4a4e57", 0.3), W * 0.7, sh=0.15)
            shape(rect(10, -5.5, 2.6, 5.5), K("#4a4e57", 0.3), W * 0.6)
            shape(rect(14, -4, 2.4, 4), K("#4a4e57", 0.3), W * 0.6)
            ring = ell(-7, 0, 6.5, 6.5, 24)
            form(ring, K("#5d6168", 0.35), W, sh=0.2)
            shape(ell(-7, 0, 4.2, 4.2, 20), K(EL[el], 0.5), W * 0.5)
            emblem(el, -7, 0, 2.4)
        glow(cx, cy, 10, EL[el], 0.18)
    return draw


def seal_icon(el):
    def draw(b):
        cx, cy = b.w / 2, b.h / 2
        glow(cx, cy, 13, EL[el], 0.25)
        wax = [(cx + math.cos(a) * (10.5 + (0.9 if i % 3 == 0 else 0)), cy + math.sin(a) * (10 + (0.9 if i % 3 == 0 else 0))) for i, a in enumerate([k * math.pi / 9 for k in range(18)])]
        form(wax, K("#8a1e22", 0.3), W, sdx=-1.2, sdy=1.2, sh=0.25)
        stroke(ell(cx, cy, 7.5, 7.2, 24), 0.6, closed=True, g=K("#5a1014", 0.2))
        emblem(el, cx, cy, 4.2)
        hl([(cx - 6, cy + 4), (cx - 3, cy + 7)], 0.8, 0.5)
    return draw


for _el in EL:
    ITEMS.append(("klic_" + _el, CELL, CELL, key_icon(_el)))
    ITEMS.append(("pecet_" + _el, CELL, CELL, seal_icon(_el)))


def desatek(b):
    """the tithe: a great thunderstone that glows with Permoník's cold blue light"""
    thunderstone("velky")(b)
    cx, cy = b.w / 2, b.h / 2
    for rr, a in ((16, 0.12), (10, 0.18)):
        fill(ell(cx, cy, rr, rr * 1.8, 30), lib.Col(0.9, "#bfe6ff", alpha=a))
    kahan_x, kahan_y = cx, cy - 12
    shape(rrect(kahan_x - 2.4, kahan_y - 3, 4.8, 5, 0.8), K("#d7dce2", 0.85), W * 0.5)
    shape(bez((kahan_x, kahan_y + 2), (kahan_x - 1.6, kahan_y + 4), (kahan_x, kahan_y + 7), (kahan_x + 0.6, kahan_y + 7)) + [(kahan_x + 1.4, kahan_y + 4)], K("#dff3ff", 0.97), W * 0.4)


ITEMS.append(("permonikuv_desatek", CELL, CELL * 3, desatek))


if __name__ == "__main__":
    common.run({"items": ITEMS})
