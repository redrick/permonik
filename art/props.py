"""Props (game/assets/props/<id>.png) and their engine data (game/data/props.json)."""
import os, sys, math, random, json
import common
from common import FEET
import lib
from lib import ell, bez, rrect
import style3
from style3 import T, stroke, fill, form, shape, hatch, offset_shadow, dot, cast_shadow, tube, C, poly, clip_fill
from world_kit import c, rect, blob, chunk, pebble, clip

L = 0.9
WOOD, WOOD_D, WOOD_L = c("#7a5638"), c("#553b26"), c("#9a7350")
OAK = c("#6e5338")
IRON, IRON_L, IRON_D = c("#4c4c54"), c("#7a7a84"), c("#33333a")
STONE, STONE_D, STONE_L = c("#86817a"), c("#67635d"), c("#a29d94")
PLASTER, PLASTER_D, PLASTER_W = c("#a99a7e"), c("#8f8064"), c("#b6a98e")
ROOF, ROOF_D = c("#8a4232"), c("#6a3026")
SLATE, SLATE_D, SLATE_L = c("#4c5264"), c("#3a3f4e"), c("#626a80")
THATCH, THATCH_D = c("#7a6442"), c("#5a4830")
LIT, LIT_C = c("#ffc864"), c("#fff0b8")
DARKGLASS = c("#353d4e")
FLAME, FLAME_C = c("#ffa040"), c("#fff2b0")
GOLD, SILVER = c("#d9ad48"), c("#c9d3dc")
BONE, BONE_D = c("#d8cfb4"), c("#a99f86")
GREEN, GREEN_C = c("#86ec5c"), c("#e6ffcc")
CLAY, CLAY_D = c("#a2603e"), c("#7d452a")
BLACK = c("#000000"); INKC = c("#2e2d33")
LEAF, LEAF_D, LEAF_L = c("#40562e"), c("#304226"), c("#536a38")
SPRUCE, SPRUCE_D = c("#34503c"), c("#263c2d")
BARK, BARK_D = c("#5e4836"), c("#433325")


def a(col, al): return c(col.hex, al)


def shadow(cx, w, d=None, y=None): cast_shadow(cx, (y if y is not None else FEET) + 0.6, w / 2, d or max(2.0, w * 0.16))


def glow(x, y, r, col, n=6, k=0.85, al=0.07):
    for i in range(n):
        rr = r * (1 - i / n)
        fill(ell(x, y, rr, rr * k, 30), a(col, al))


def flame(x, y, s=1.0):
    with T(x, y, s):
        o = bez((0, 0), (-2.4, 1.2), (-1.6, 4.4), (0.2, 7.2)) + bez((0.2, 7.2), (1.2, 4.6), (2.6, 1.6), (0, 0))
        shape(o, FLAME, w=0.4)
        fill(bez((0, 0.6), (-1.1, 1.5), (-0.6, 3.4), (0.2, 4.6)) + bez((0.2, 4.6), (0.7, 3.0), (1.3, 1.4), (0, 0.6)), FLAME_C)


def boxp(x0, y0, w, h, d):
    """front face and top face of an axis box in 3/4 view"""
    return rect(x0, y0, w, h), rect(x0, y0 + h, w, d)


def planks_v(pts, x0, x1, step, y0, y1, g=WOOD_D, w=0.4):
    with clip(pts):
        x = x0 + step
        while x < x1 - 0.5:
            stroke([(x, y0), (x + 0.2, y1)], w, g=g); x += step


def planks_h(pts, y0, y1, step, x0, x1, g=WOOD_D, w=0.4):
    with clip(pts):
        y = y0 + step
        while y < y1 - 0.5:
            stroke([(x0, y), (x1, y + 0.15)], w, g=g); y += step


def grain(pts, x0, y0, x1, y1, r, n=4, g=WOOD_D, vertical=True):
    with clip(pts):
        for _ in range(n):
            if vertical:
                x = r.uniform(x0, x1); stroke([(x, r.uniform(y0, y0 + (y1 - y0) * 0.3)), (x + r.uniform(-0.4, 0.4), r.uniform(y0 + (y1 - y0) * 0.6, y1))], 0.25, g=g)
            else:
                y = r.uniform(y0, y1); stroke([(r.uniform(x0, x0 + (x1 - x0) * 0.3), y), (r.uniform(x0 + (x1 - x0) * 0.6, x1), y + r.uniform(-0.3, 0.3))], 0.25, g=g)


def beam_v(x, y0, y1, w, g=WOOD, top=True):
    p = rect(x - w / 2, y0, w, y1 - y0)
    form(p, g, w=L * 0.8, sdx=-w * 0.3, sdy=0, sh=0.16)
    r = random.Random(int(x * 13 + y0))
    grain(p, x - w / 2, y0, x + w / 2, y1, r, 2)
    if top: shape(rect(x - w / 2, y1, w, w * 0.45), WOOD_L, w=L * 0.6)


def beam_h(x0, x1, y, h, g=WOOD, d=None):
    f = rect(x0, y, x1 - x0, h)
    form(f, g, w=L * 0.8, sdx=0, sdy=h * 0.35, sh=0.15)
    if d: shape(rect(x0, y + h, x1 - x0, d), WOOD_L, w=L * 0.6)
    r = random.Random(int(x0 * 7 + y))
    grain(f, x0, y, x1, y + h, r, 3, vertical=False)


def window(x, y, w, h, lit=True, arch=False, shut=None, frame=WOOD_D, cross=True):
    o = rect(x, y, w, h) if not arch else [(x, y), (x + w, y), (x + w, y + h - w / 2)] + ell(x + w / 2, y + h - w / 2, w / 2, w / 2, 14, 0, 180)[1:] + [(x, y + h - w / 2)]
    if lit: glow(x + w / 2, y + h / 2, max(w, h) * 0.9, LIT, 4, 1.0, 0.06)
    shape([(px, py) for px, py in o], LIT if lit else DARKGLASS, w=L * 0.8)
    if lit: clip_fill(o, rect(x, y, w, h * 0.45), a(c("#ff9a3a"), 0.25))
    if cross:
        stroke([(x + w / 2, y), (x + w / 2, y + h - (w / 2 if arch else 0) + (w / 2 if arch else 0))], 0.6, g=frame)
        stroke([(x, y + h * 0.55), (x + w, y + h * 0.55)], 0.6, g=frame)
    shape(rect(x - 0.8, y - 1.0, w + 1.6, 1.0), STONE_L if frame == STONE_D else WOOD_L, w=0.5)
    if shut:
        for sx in (x - w * 0.45 - 0.4, x + w + 0.4):
            sp = rect(sx, y, w * 0.45, h)
            shape(sp, shut, w=0.6)
            for k in range(3): stroke([(sx + 0.4, y + h * (0.25 + k * 0.25)), (sx + w * 0.45 - 0.4, y + h * (0.25 + k * 0.25))], 0.3)


def door(x, y, w, h, g=WOOD_D, arch=True):
    o = [(x, y), (x + w, y), (x + w, y + h - w / 2)] + ell(x + w / 2, y + h - w / 2, w / 2, w / 2, 14, 0, 180)[1:] + [(x, y + h - w / 2)] if arch else rect(x, y, w, h)
    form(o, g, w=L * 0.9, sdx=-1, sdy=0, sh=0.18)
    planks_v(o, x, x + w, w / 3, y, y + h, WOOD_D if g != WOOD_D else c("#3e2a1a"))
    for yy in (y + h * 0.25, y + h * 0.6): stroke([(x + 0.5, yy), (x + w - 0.5, yy)], 0.6, g=IRON)
    dot(x + w * 0.78, y + h * 0.42, 0.55, IRON_L)


def tiles(roof, y0, y1, x0, x1, step=3.0, g=ROOF_D, tick=True):
    with clip(roof):
        y = y0 + step; row = 0
        while y < y1:
            stroke([(x0, y), (x1, y)], 0.4, g=g)
            if tick:
                xx = x0 + (row % 2) * 1.8
                while xx < x1:
                    stroke([(xx, y - step + 0.3), (xx, y - 0.3)], 0.25, g=g); xx += 3.6
            y += step; row += 1


def scallops(roof, y0, y1, x0, x1, step=2.6, g=SLATE_D):
    with clip(roof):
        y = y0; row = 0
        while y < y1:
            xx = x0 + (row % 2) * 1.5
            while xx < x1:
                stroke(ell(xx, y + step * 0.2, 1.5, step * 0.6, 8, 180, 360), 0.3, g=g); xx += 3.0
            y += step; row += 1


def thatch_lines(roof, y0, y1, x0, x1, r):
    with clip(roof):
        for _ in range(int((x1 - x0) * (y1 - y0) / 14)):
            x, y = r.uniform(x0, x1), r.uniform(y0, y1)
            stroke([(x, y), (x + r.uniform(-0.6, 0.6), y - r.uniform(2, 4))], 0.3, g=THATCH_D)


def chimney(x, y, w, h, smoke=True):
    form(rect(x, y, w, h), c("#8a5a48"), w=L * 0.8, sdx=-1, sdy=0, sh=0.18)
    for k in range(int(h / 2.5)): stroke([(x, y + 1.2 + k * 2.5), (x + w, y + 1.2 + k * 2.5)], 0.25, g=c("#6a4034"))
    shape(rect(x - 0.8, y + h, w + 1.6, 1.4), c("#6e463a"), w=L * 0.7)
    if smoke:
        for i, (dx, dy, rr) in enumerate(((0.5, 3.5, 2.2), (2.5, 8, 3), (5.5, 13, 3.8))):
            fill(ell(x + w / 2 + dx, y + h + 1.4 + dy, rr, rr * 0.75, 18), c("#9a9aa8", 0.35 - i * 0.08))


def stones_course(x0, x1, y0, y1, r, g=STONE, rows=2):
    hh = (y1 - y0) / rows
    for i in range(rows):
        x = x0 - r.uniform(0, 3)
        while x < x1:
            w = r.uniform(4, 7)
            p = rect(max(x, x0) + 0.2, y0 + i * hh + 0.2, min(w, x1 - max(x, x0)) - 0.4, hh - 0.4)
            if p[1][0] - p[0][0] > 0.6:
                form(p, g if r.random() < 0.6 else STONE_D, w=0.45, sdx=-0.5, sdy=0.4, sh=0.12)
            x += w


# ------------------------------------------------------------------ dungeon
def podpera(b):
    cx = b.w / 2
    for x in (cx - 22, cx + 22): shadow(x + 2, 12, 2.5)
    for x in (cx - 22, cx + 22):
        beam_v(x, FEET, 58, 6.5)
    for s in (-1, 1):
        x = cx + s * 22
        br = [(x - s * 3, 44), (x - s * 3, 47.5), (x - s * 12, 57), (x - s * 15.5, 57)]
        form(br, WOOD, w=L * 0.7, sh=0.12)
    beam_h(cx - 30, cx + 30, 56, 7, d=4)
    for x in (cx - 20, cx - 4, cx + 12):
        shape(rect(x, 67, 7, 3.2), WOOD_D, w=0.5)
    for k in (-8, 8): dot(cx + k, 59.5, 0.6, IRON_L)
    with clip(rect(cx - 30, 56, 60, 7)): fill(rect(cx - 30, 56, 60, 1.8), BLACK, 0.15)


def vozik(b):
    cx = b.w / 2; r = random.Random(4)
    shadow(cx, 58, 5)
    for x in (cx - 18, cx + 18):
        shape(ell(x, FEET + 6, 6, 6, 24), IRON, w=L)
        shape(ell(x, FEET + 6, 3.4, 3.4, 18), IRON_D, w=0.5)
        dot(x, FEET + 6, 1.2, IRON_L)
    body = [(cx - 28, FEET + 8), (cx + 28, FEET + 8), (cx + 32, FEET + 30), (cx - 32, FEET + 30)]
    form(body, WOOD, w=L, sdx=-2.5, sdy=0, sh=0.16)
    planks_h(body, FEET + 8, FEET + 30, 5.5, cx - 33, cx + 33)
    for x in (cx - 26, cx - 9, cx + 9, cx + 26):
        stroke([(x, FEET + 8.5), (x + (x - cx) * 0.12, FEET + 29.5)], 1.6, g=IRON)
        for y in (FEET + 11, FEET + 26): dot(x + (x - cx) * 0.07 * (y - FEET) / 22, y, 0.5, IRON_L)
    rim = [(cx - 32, FEET + 30), (cx + 32, FEET + 30), (cx + 31, FEET + 38), (cx - 31, FEET + 38)]
    form(rim, c("#3c2c22"), w=L * 0.8, sh=0)
    heap = []
    for i in range(12):
        x = cx + r.uniform(-26, 26); y = FEET + 32 + r.uniform(0, 7) + 4 * math.cos((x - cx) / 30)
        heap.append((y, x))
    for y, x in sorted(heap, reverse=True):
        s = r.uniform(2.6, 4.4)
        pebble(chunk(x, y, s, s * 0.75, r), r.choice((STONE, STONE_D, c("#8d939a"))), w=0.5, ground=0.15)
        if r.random() < 0.5:
            stroke([(x - 1.5, y), (x + 1, y + 0.8)], 0.5, g=SILVER); dot(x, y + 0.3, 0.35, c("#ffffff"))
    form([(cx - 32, FEET + 30), (cx + 32, FEET + 30), (cx + 32, FEET + 32), (cx - 32, FEET + 32)], c("#4a372a"), w=0.6, sh=0)


def barrel(cx, y0, w=22, h=25, g=WOOD, lid=True):
    rx = w / 2; ry = rx * 0.38
    left = bez((cx - rx * 0.86, y0), (cx - rx * 1.07, y0 + h * 0.3), (cx - rx * 1.07, y0 + h * 0.7), (cx - rx * 0.86, y0 + h))
    right = bez((cx + rx * 0.86, y0 + h), (cx + rx * 1.07, y0 + h * 0.7), (cx + rx * 1.07, y0 + h * 0.3), (cx + rx * 0.86, y0))
    bot = ell(cx, y0, rx * 0.86, ry, 18, 180, 360)
    body = bot + right + ell(cx, y0 + h, rx * 0.86, ry, 18, 0, 180) + left
    form(body, g, w=L, sdx=-3, sdy=0, sh=0.18)
    with clip(body):
        for k in (-0.6, -0.25, 0.1, 0.45, 0.75):
            stroke(bez((cx + k * rx * 0.86, y0 - ry * math.sqrt(1 - k * k)), (cx + k * rx * 1.05, y0 + h * 0.3), (cx + k * rx * 1.05, y0 + h * 0.7), (cx + k * rx * 0.86, y0 + h)), 0.3, g=WOOD_D)
        for t in (0.14, 0.86, 0.42, 0.58):
            k = 1 + 0.2 * math.sin(math.pi * t)
            y = y0 + h * t
            stroke(ell(cx, y, rx * 0.86 * k, ry, 18, 180, 360), 1.3 if t in (0.14, 0.86) else 0.8, g=IRON)
    if lid:
        top = ell(cx, y0 + h, rx * 0.86, ry, 24)
        shape(top, WOOD_L, w=L * 0.8)
        stroke(ell(cx, y0 + h, rx * 0.72, ry * 0.8, 20), 0.4, closed=True, g=WOOD_D)
        for k in (-0.3, 0.2): stroke([(cx + k * rx, y0 + h - ry * 0.75), (cx + k * rx + 0.6, y0 + h + ry * 0.75)], 0.3, g=WOOD_D)
    return body


def sud(b):
    cx = b.w / 2
    shadow(cx, 24, 4)
    barrel(cx, FEET + 3.5, 22, 25)


def staves(cx, y, r, n=6):
    for i in range(n):
        x = cx + r.uniform(-12, 12); yy = y + r.uniform(0, 6); rot = r.uniform(-60, 60)
        with T(x, yy, rot=rot):
            p = bez((-5, -1), (-2, -1.6), (2, -1.6), (5, -1)) + bez((5, 1), (2, 0.4), (-2, 0.4), (-5, 1))
            fill([(px + 0.5, py - 0.7) for px, py in p], BLACK, 0.2)
            form(p, WOOD, w=0.6, sh=0.15)


def sud_broken(b):
    cx = b.w / 2; r = random.Random(7)
    shadow(cx, 26, 4)
    body = barrel(cx, FEET + 3.5, 22, 8, lid=False)
    fill(ell(cx, FEET + 11.5, 9.4, 3.6, 20), c("#2a2220"))
    for k, hh in ((-0.7, 14), (-0.3, 10), (0.4, 12), (0.75, 9)):
        x = cx + k * 9.5
        st = [(x - 1.6, FEET + 9), (x + 1.6, FEET + 9), (x + 1.4 + r.uniform(-0.5, 0.5), FEET + hh), (x - 1.3, FEET + hh - 1.5)]
        form(st, WOOD, w=0.6, sh=0.12)
    stroke(ell(cx + 6, FEET + 2, 7, 2.5, 16, 200, 330), 1.1, g=IRON)
    staves(cx, FEET + 0.5, r, 4)


def chest(b, opened=False, kostej=False):
    cx = b.w / 2; w = 30 if not kostej else 42; h = 14 if not kostej else 18; d = 9 if not kostej else 11
    x0 = cx - w / 2; y0 = FEET + 2
    shadow(cx, w + 4, 4)
    body_g = WOOD if not kostej else c("#4a3a30")
    band = IRON if not kostej else c("#3a3a42")
    if opened:
        lid = rect(x0 - 0.5, y0 + h + d - 1, w + 1, 13)
        form(lid, body_g, w=L, sdx=0, sdy=-2, sh=0.2)
        planks_h(lid, y0 + h + d - 1, y0 + h + d + 12, 4.3, x0, x0 + w)
        for x in (x0 + 3, x0 + w - 3): stroke([(x, y0 + h + d - 1), (x, y0 + h + d + 12)], 1.4, g=band)
    front, top = boxp(x0, y0, w, h, d)
    form(front, body_g, w=L, sdx=-2, sdy=0, sh=0.16)
    planks_h(front, y0, y0 + h, h / 3, x0, x0 + w)
    if opened:
        shape(top, c("#2a2018"), w=L * 0.8)
        for i in range(9):
            r = random.Random(i)
            dot(cx + r.uniform(-w / 2 + 3, w / 2 - 3), y0 + h + r.uniform(1.5, d - 1.5), r.uniform(1, 1.6), GOLD)
        glow(cx, y0 + h + d / 2, w * 0.45, c("#ffd870"), 4, 0.4, 0.08)
        for i in range(5):
            r = random.Random(20 + i)
            x, y = cx + r.uniform(-w / 2 + 3, w / 2 - 3), y0 + h + r.uniform(2, d - 1)
            shape(ell(x, y, 1.4, 0.8, 10), GOLD, w=0.3); dot(x - 0.3, y + 0.2, 0.3, c("#fff4c0"))
    else:
        lid = rect(x0, y0 + h, w, d + 2)
        form(lid, WOOD_L if not kostej else c("#5e4a3c"), w=L, sdx=0, sdy=1.5, sh=0.14)
        planks_h(lid, y0 + h, y0 + h + d + 2, (d + 2) / 3, x0, x0 + w)
        stroke([(x0, y0 + h), (x0 + w, y0 + h)], 0.9)
    for x in ((x0 + 3, x0 + w - 3) if not kostej else (x0 + 3, x0 + w / 3, x0 + 2 * w / 3, x0 + w - 3)):
        stroke([(x, y0 + 0.4), (x, y0 + h + (0 if opened else d + 1.6))], 1.5, g=band)
        for yy in (y0 + 2, y0 + h - 2): dot(x, yy, 0.45, IRON_L)
    if kostej:
        stroke([(x0, y0 + h * 0.5), (x0 + w, y0 + h * 0.5)], 1.3, g=band)
        for x in (x0 + 1, x0 + w - 1):
            for yy in (y0 + 1, y0 + h - 1): shape(ell(x, yy, 1.4, 1.4, 10), band, w=0.4)
    lk = rect(cx - 2.2, y0 + h - 5.5, 4.4, 5)
    shape(lk, GOLD if not kostej else c("#8a8a94"), w=0.6)
    dot(cx, y0 + h - 3.5, 0.6, BLACK)
    if kostej:
        for s in (-1, 1): stroke(bez((cx + s * 6, y0 + h * 0.75), (cx + s * 8, y0 + h * 0.9), (cx + s * 10, y0 + h * 0.6), (cx + s * 8, y0 + h * 0.4)), 0.5, g=c("#8a8a94"))


def truhla(b): chest(b)
def truhla_open(b): chest(b, True)
def truhla_kostej(b): chest(b, False, True)


def bone(x, y, Ln, rot, w=1.3, g=BONE):
    with T(x, y, rot=rot):
        stroke([(-Ln, 0), (Ln, 0)], w + 0.5, taper=False, g=INKC)
        stroke([(-Ln, 0), (Ln, 0)], w, taper=False, g=g)
        for s in (-1, 1):
            for dy in (-w * 0.45, w * 0.45):
                shape(ell(s * Ln, dy, w * 0.62, w * 0.62, 10), g, w=0.35)
        stroke([(-Ln + 0.6, -w * 0.3), (Ln - 0.6, -w * 0.3)], 0.3, g=BONE_D)


def skull(x, y, s=1.0, rot=0, jaw=True):
    with T(x, y, s, rot=rot):
        cr = bez((-3.4, 0.4), (-4.2, 4.5), (-2.2, 6.6), (0, 6.6)) + bez((0, 6.6), (2.2, 6.6), (4.2, 4.5), (3.4, 0.4)) + \
             [(2.4, -0.6), (2.2, -2.2), (-2.2, -2.2), (-2.4, -0.6)]
        form(cr, BONE, w=0.6, sdx=-1, sdy=0.8, sh=0.18)
        for sx in (-1.45, 1.45): shape(ell(sx, 1.9, 1.05, 1.15, 12), c("#2a2530"), w=0.3)
        fill([(-0.45, 0.2), (0.45, 0.2), (0, -0.8)], c("#2a2530"))
        for k in (-1.2, -0.4, 0.4, 1.2): stroke([(k, -2.2), (k, -1.0)], 0.3)
        stroke(bez((-2.5, 4.8), (-1.5, 5.8), (0.5, 6.1), (1.5, 5.8)), 0.3, g=BONE_D)


def kosti(b):
    cx = b.w / 2; r = random.Random(11)
    fill(ell(cx, FEET + 6, 20, 5, 24), BLACK, 0.12)
    for _ in range(7):
        bone(cx + r.uniform(-16, 16), FEET + 3 + r.uniform(0, 9), r.uniform(3, 6), r.uniform(-30, 210), r.uniform(1.0, 1.5))
    skull(cx + 6, FEET + 6, 0.95, -15)
    bone(cx - 6, FEET + 5, 5.5, 160, 1.4)


def lebky(b):
    cx = b.w / 2; r = random.Random(12)
    shadow(cx, 34, 4)
    for _ in range(5): bone(cx + r.uniform(-14, 14), FEET + r.uniform(1, 5), r.uniform(3, 5), r.uniform(-20, 20))
    rows = [(-12, 0), (-4, 0), (4, 0), (12, 0), (-8, 7), (0, 7), (8, 7), (-4, 14), (4, 14), (0, 21)]
    for dx, dy in rows:
        skull(cx + dx + r.uniform(-0.6, 0.6), FEET + 4 + dy, 1.05, r.uniform(-10, 10))


def kamen(b):
    cx = b.w / 2; r = random.Random(13)
    shadow(cx, 34, 5)
    items = [(cx - 9, FEET + 6, 8, 6), (cx + 8, FEET + 6, 9, 6.5), (cx - 1, FEET + 14, 8, 6), (cx + 13, FEET + 3, 4, 3), (cx - 15, FEET + 3, 3.5, 2.6)]
    for x, y, rx, ry in sorted(items, key=lambda t: -t[1]):
        p = chunk(x, y, rx, ry, r, n=8, k=0.15)
        form(p, r.choice((STONE, STONE_D)), w=L * 0.9, sdx=-2, sdy=1.6, sh=0.18)
        stroke([(x - rx * 0.4, y + ry * 0.2), (x + rx * 0.1, y - ry * 0.3)], 0.35, g=STONE_D)


def ruda(b):
    cx = b.w / 2; r = random.Random(14)
    shadow(cx, 40, 6)
    p = chunk(cx, FEET + 17, 20, 15, r, n=10, k=0.1)
    p = [(x, max(y, FEET + 2)) for x, y in p]
    form(p, c("#5e5a56"), w=L * 1.1, sdx=-4, sdy=3, sh=0.2)
    fill(chunk(cx - 4, FEET + 25, 12, 6, r, n=8), c("#77726b"))
    for k in range(3):
        y0 = FEET + 8 + k * 7 + r.uniform(-1, 1)
        pts = [(cx - 15 + r.uniform(0, 4), y0)]
        while pts[-1][0] < cx + 13:
            pts.append((pts[-1][0] + r.uniform(2.5, 4.5), pts[-1][1] + r.uniform(-2, 2)))
        with clip(p):
            stroke(pts, 2.2, g=c("#8d98a3")); stroke(pts, 0.9, g=SILVER)
            for q in pts[1:-1]:
                dot(q[0], q[1] + 0.4, 0.55, c("#ffffff"))
    stroke(p, L * 1.1, closed=True)
    for _ in range(4):
        x, y = cx + r.uniform(-12, 12), FEET + r.uniform(10, 26)
        stroke([(x - 1.6, y), (x + 1.6, y)], 0.35, g=c("#ffffff")); stroke([(x, y - 1.6), (x, y + 1.6)], 0.35, g=c("#ffffff"))
    for _ in range(3):
        pebble(chunk(cx + r.uniform(-20, 20), FEET + r.uniform(1, 3), 2, 1.5, r), STONE_D, w=0.5)


def lamp(x, y, s=1.0, cold=False):
    with T(x, y, s):
        stroke(bez((0, 12), (-1.6, 13.5), (-1.2, 15.5), (0.4, 15.5)), 0.6, g=IRON)
        body = bez((-2.6, 3), (-3, 6.5), (-1.8, 9.5), (-0.8, 10.4)) + [(0.8, 10.4)] + bez((0.8, 10.4), (1.8, 9.5), (3, 6.5), (2.6, 3))
        form(body + [(2.2, 0), (-2.2, 0)], c("#a8823c"), w=0.6, sh=0.2)
        stroke([(0, 10.4), (0, 12)], 0.5, g=IRON)
        stroke([(-2.6, 3.2), (2.6, 3.2)], 0.4, g=c("#6a5020"))
        stroke(bez((2.6, 6), (6, 6.5), (7, 8), (7.2, 9.5)), 1.1, g=c("#a8823c")); stroke(bez((2.6, 6), (6, 6.5), (7, 8), (7.2, 9.5)), 0.3)
        flame(7.2, 9.3, 0.6)


def kahan_nastenny(b):
    cx = b.w / 2
    glow(cx + 2.5, 28, 11, FLAME, 6, 1.0, 0.07)
    pl = rect(cx - 3.5, FEET + 8, 7, 22)
    form(pl, WOOD, w=L * 0.8, sdx=-1, sdy=0, sh=0.18)
    for y in (FEET + 11, FEET + 27): dot(cx, y, 0.6, IRON_L)
    stroke([(cx + 0.5, FEET + 24), (cx + 5, FEET + 24), (cx + 5, FEET + 22)], 0.9, g=IRON)
    lamp(cx + 3, FEET + 9.5, 0.95)


def schody_dolu(b):
    cx = b.w / 2; y0 = FEET + 2
    fill(rect(cx - 28, y0 - 1.5, 56, 34), BLACK, 0.18)
    inner = rect(cx - 19, y0 + 5, 38, 21)
    fill(inner, c("#141216"))
    with clip(inner):
        for i in range(5): fill(rect(cx - 19, y0 + 26 - 2.2 * (i + 1), 38, 2.2 * (i + 1)), c("#5a4a3c", 0.12))
        for x in (cx - 19, cx + 15): fill(rect(x, y0 + 5, 4, 21), c("#000000", 0.25))
    side = lambda x: (form(rect(x, y0 + 4, 7, 23), WOOD_L, w=L * 0.8, sdx=0, sdy=0, sh=0),
                      grain(rect(x, y0 + 4, 7, 23), x, y0 + 4, x + 7, y0 + 27, random.Random(int(x)), 3))
    side(cx - 26); side(cx + 19)
    far = rect(cx - 27, y0 + 25, 54, 6)
    form(far, WOOD_L, w=L * 0.8, sh=0); grain(far, cx - 27, y0 + 25, cx + 27, y0 + 31, random.Random(3), 3, vertical=False)
    for x0, x1 in ((cx - 8, cx - 7), (cx + 6, cx + 7)):
        p = [(x0 - 1.2, y0 + 4), (x0 + 1.2, y0 + 4), (x1 + 1.2, y0 + 38), (x1 - 1.2, y0 + 38)]
        form(p, WOOD, w=0.7, sdx=-0.6, sdy=0, sh=0.15)
    for k in range(8):
        y = y0 + 7 + k * 4.2
        shape(rect(cx - 7, y, 13, 1.2), WOOD_L, w=0.4)
    with clip(inner):
        for i in range(6): fill(rect(cx - 20, y0 + 5, 40, 3 + i * 3), c("#000000", 0.13))
    front, top = boxp(cx - 27, y0, 54, 2.5, 4.5)
    form(front, WOOD_D, w=L * 0.8, sh=0)
    form(top, WOOD_L, w=L * 0.8, sh=0)
    grain(top, cx - 27, y0 + 2.5, cx + 27, y0 + 7, random.Random(5), 3, vertical=False)
    for x in (cx - 24, cx + 24): dot(x, y0 + 4.7, 0.6, IRON_L); dot(x, y0 + 28, 0.6, IRON_L)


def schody_nahoru(b):
    cx = b.w / 2
    fill([(cx - 10, b.h), (cx + 18, b.h), (cx + 14, FEET + 2), (cx - 16, FEET + 2)], c("#e8eeff", 0.12))
    fill([(cx - 4, b.h), (cx + 10, b.h), (cx + 6, FEET + 2), (cx - 8, FEET + 2)], c("#e8eeff", 0.12))
    fill(ell(cx - 1, FEET + 3, 16, 4, 24), c("#e8eeff", 0.18))
    glow(cx, b.h - 4, 20, c("#dfe8ff"), 5, 0.6, 0.09)
    shadow(cx - 2, 26, 3)
    for x0, x1 in ((cx - 9, cx - 4), (cx + 7, cx + 12)):
        p = [(x0 - 1.4, FEET + 2), (x0 + 1.4, FEET + 2), (x1 + 1.4, b.h + 2), (x1 - 1.4, b.h + 2)]
        form(p, WOOD, w=L * 0.8, sdx=-1, sdy=0, sh=0.16)
    n = 0; y = FEET + 7
    while y < b.h - 4:
        t = (y - FEET - 2) / (b.h - FEET); xl = cx - 9 + 5 * t; xr = cx + 7 + 5 * t
        shape(rect(xl + 1, y, xr - xl - 2, 1.6), WOOD_L, w=0.5)
        y += 6.5; n += 1


def klec(b):
    cx = b.w / 2; y0 = FEET + 3; w = 46; h = 54; d = 14
    shadow(cx, w + 10, 6)
    stroke([(cx, y0 + h + d), (cx, b.h)], 2.2, g=c("#5a5048"), taper=False)
    stroke([(cx + 0.4, y0 + h + d), (cx + 0.4, b.h)], 0.5, g=c("#2a2420"), taper=False)
    for s in (-1, 1): stroke([(cx, y0 + h + d + 4), (cx + s * (w / 2 - 2), y0 + h + d * 0.6)], 0.7, g=IRON_D)
    floor = rect(cx - w / 2, y0, w, 4)
    back = rect(cx - w / 2 + 2, y0 + 4, w - 4, h - 4)
    fill(back, c("#26222a", 0.55))
    for k in range(7):
        x = cx - w / 2 + 4 + k * (w - 8) / 6
        stroke([(x, y0 + 4 + d * 0.5), (x, y0 + h + d * 0.5)], 0.5, g=IRON_L)
    beam_h(cx - w / 2, cx + w / 2, y0, 4, IRON, d=0)
    roof = rect(cx - w / 2, y0 + h, w, d)
    form(roof, c("#6a6a74"), w=L, sdx=0, sdy=-2, sh=0.15)
    for k in range(5): stroke([(cx - w / 2 + 3 + k * 10, y0 + h + 1), (cx - w / 2 + 3 + k * 10, y0 + h + d - 1)], 0.4, g=IRON_D)
    beam_h(cx - w / 2 - 1, cx + w / 2 + 1, y0 + h - 2.5, 3, IRON_D)
    for x in (cx - w / 2, cx + w / 2):
        form(rect(x - 1.6, y0, 3.2, h + 0.5), IRON, w=L * 0.8, sh=0.12)
    for k in range(9):
        x = cx - w / 2 + 3 + k * (w - 6) / 8
        stroke([(x, y0 + 4), (x, y0 + h - 2.5)], 1.1, g=INKC); stroke([(x - 0.2, y0 + 4), (x - 0.2, y0 + h - 2.5)], 0.6, g=IRON_L)
    stroke([(cx - w / 2, y0 + h * 0.5), (cx + w / 2, y0 + h * 0.5)], 1.3, g=IRON_D)
    shape(ell(cx, y0 + h * 0.35, 3.5, 3.5, 16), GOLD, w=0.5)
    stroke(ell(cx, y0 + h * 0.35, 2.2, 2.2, 12), 0.4, closed=True)


def urn(cx, y0, s=1.0, broken=False):
    prof = [(5.5, 0), (8.5, 3), (10.5, 9), (10.2, 15), (7.5, 20.5), (5, 22.5), (5.3, 25), (7, 26)]
    prof = [(rr * s, yy * s) for rr, yy in prof]
    if broken: prof = [(rr, min(yy, 10 * s)) for rr, yy in prof[:4]]
    right = [(cx + rr, y0 + yy) for rr, yy in prof]
    left = [(cx - rr, y0 + yy) for rr, yy in reversed(prof)]
    o = ell(cx, y0, prof[0][0], prof[0][0] * 0.35, 12, 180, 360) + right + left
    form(o, CLAY, w=L, sdx=-3 * s, sdy=0, sh=0.2)
    with clip(o):
        for yy, col in ((y0 + 12 * s, c("#e0c090")), (y0 + 16 * s, CLAY_D)):
            if broken and yy > y0 + 10 * s: continue
            stroke(ell(cx, yy, 11 * s, 2.2 * s, 18, 180, 360), 1.0, g=col)
        if not broken:
            for k in range(6):
                x = cx - 8 * s + k * 3.2 * s
                stroke([(x, y0 + 13.5 * s), (x + 1.4 * s, y0 + 14.6 * s), (x + 2.8 * s, y0 + 13.5 * s)], 0.4, g=c("#e0c090"))
    top_r = prof[-1][0]; ty = y0 + prof[-1][1]
    shape(ell(cx, ty, top_r, top_r * 0.35, 18), c("#2a1c16") if not broken else c("#2a1c16"), w=L * 0.8)
    if not broken:
        stroke(ell(cx, ty, top_r, top_r * 0.35, 18, 180, 360), 0.8, g=CLAY_D)


def urna(b):
    cx = b.w / 2
    shadow(cx, 22, 3.5)
    urn(cx, FEET + 1.5, 1.0)


def urna_broken(b):
    cx = b.w / 2; r = random.Random(17)
    shadow(cx, 24, 3.5)
    urn(cx, FEET + 1.5, 1.0, broken=True)
    for _ in range(6):
        x = cx + r.uniform(-13, 13); y = FEET + r.uniform(0.5, 5); rr = r.uniform(1.6, 3)
        p = chunk(x, y, rr, rr * 0.6, r, n=5)
        fill([(px + 0.4, py - 0.5) for px, py in p], BLACK, 0.2)
        form(p, CLAY, w=0.5, sh=0.15)


# ------------------------------------------------------------------ shrines
SHRINE = {
    "perun": (OAK, c("#bfe0ff")), "veles": (c("#5a4630"), c("#8fd07a")), "mokos": (c("#7a5a40"), c("#e06060")),
    "svarog": (c("#6e4a30"), c("#ffb85c")), "morana": (c("#a69c88"), c("#cfe8ff")), "stribog": (c("#7a6a58"), c("#a8e8f0")),
    "triglav": (c("#5e4c40"), c("#b8a0ff")), "rod": (c("#86684a"), c("#ffd870")), "used": (c("#3e3630"), None),
}


def idol_face(x, y, s, glowcol, used=False, beard=True):
    with T(x, y, s):
        for sx in (-2.6, 2.6):
            fill(ell(sx, 1.2, 1.6, 0.9, 12), BLACK, 0.5)
            if glowcol and not used:
                dot(sx, 1.2, 1.6, a(glowcol, 0.35)); dot(sx, 1.2, 0.7, glowcol)
            else:
                dot(sx, 1.2, 0.55, c("#1a1614"))
        stroke([(-4.4, 2.8), (-1, 2.4)], 0.7); stroke([(1, 2.4), (4.4, 2.8)], 0.7)
        stroke([(0, 2.2), (-0.6, -1.4), (0.6, -1.6)], 0.5)
        if beard:
            stroke(bez((-4.5, -1.6), (-2, -3.2), (2, -3.2), (4.5, -1.6)), 0.9)
            for k in (-2.5, -1, 0.5, 2): stroke([(k, -3.0), (k + 0.2, -6)], 0.35)
        else:
            stroke([(-1.6, -2.4), (1.6, -2.4)], 0.6)


def symbol(kind, x, y, col, s=1.0):
    col = col or c("#4a4038")
    with T(x, y, s):
        if kind == "perun":
            for k in range(6):
                aa = math.radians(k * 60)
                stroke(bez((0, 0), (math.cos(aa) * 3, math.sin(aa) * 3 + 1.5), (math.cos(aa + 0.8) * 5, math.sin(aa + 0.8) * 5), (math.cos(aa + 1.05) * 4.4, math.sin(aa + 1.05) * 4.4)), 0.7, g=col)
            stroke(ell(0, 0, 5.4, 5.4, 30), 0.7, closed=True, g=col)
        elif kind == "veles":
            pts = [(math.cos(t * 0.5) * t * 0.55, math.sin(t * 0.5) * t * 0.55) for t in [i * 0.4 for i in range(26)]]
            stroke(pts, 0.8, g=col)
        elif kind == "mokos":
            stroke([(0, 5), (4, 0), (0, -5), (-4, 0)], 0.8, closed=True, g=col)
            for dx, dy in ((0, 2), (2, 0), (0, -2), (-2, 0)): dot(dx, dy, 0.5, col)
        elif kind == "svarog":
            stroke(ell(0, 0, 4.5, 4.5, 26), 0.8, closed=True, g=col)
            for k in range(8):
                aa = math.radians(k * 45); stroke([(0, 0), (math.cos(aa) * 4.5, math.sin(aa) * 4.5)], 0.5, g=col)
        elif kind == "morana":
            for k in range(3):
                aa = math.radians(k * 60); stroke([(-math.cos(aa) * 5, -math.sin(aa) * 5), (math.cos(aa) * 5, math.sin(aa) * 5)], 0.7, g=col)
        elif kind == "stribog":
            for k in range(3):
                yy = 3 - k * 3
                stroke(bez((-5, yy), (-2, yy + 2), (1, yy - 1), (4, yy + 1)) + ell(4, yy + 1 - 1.2, 1.2, 1.2, 8, 90, 360), 0.7, g=col)
        elif kind == "triglav":
            stroke([(-5, -3.5), (-2.5, 2), (0, -1), (2.5, 4), (5, -3.5)], 0.8, g=col)
            stroke([(-5.5, -3.5), (5.5, -3.5)], 0.7, g=col)
        elif kind == "rod":
            stroke(ell(0, 0, 5, 5, 30), 0.7, closed=True, g=col)
            for k in range(6):
                aa = math.radians(k * 60)
                stroke(ell(math.cos(aa) * 2.5, math.sin(aa) * 2.5, 2.5, 2.5, 14, math.degrees(aa) + 120, math.degrees(aa) + 240), 0.5, g=col)


def modla(kind):
    def d(b):
        cx = b.w / 2; r = random.Random(kind)
        wood, glowc = SHRINE[kind]
        used = kind == "used"
        shadow(cx, 36, 5)
        if glowc: glow(cx, 52, 26, glowc, 6, 1.2, 0.05)
        f, t = boxp(cx - 16, FEET, 32, 7, 7)
        form(f, STONE_D if not used else c("#4e4a46"), w=L, sdx=-1.5, sdy=0, sh=0.15)
        shape(t, STONE if not used else c("#5e5a54"), w=L * 0.8)
        for k in (-8, 3, 11): stroke([(cx + k, FEET + 0.5), (cx + k + 0.4, FEET + 6.5)], 0.35, g=STONE_D)
        pw = 15; y0 = FEET + 10; ph = 46 if kind != "triglav" else 42
        pil = [(cx - pw / 2, y0), (cx + pw / 2, y0), (cx + pw / 2 - 0.8, y0 + ph), (cx - pw / 2 + 0.8, y0 + ph)]
        form(pil, wood, w=L, sdx=-3, sdy=0, sh=0.2)
        grain(pil, cx - pw / 2, y0, cx + pw / 2, y0 + ph, r, 5, c("#2e241a"))
        for yy in (y0 + 5, y0 + 26):
            stroke([(cx - pw / 2 + 0.3, yy), (cx + pw / 2 - 0.3, yy)], 0.6, g=c("#2e241a"))
        symbol(kind if not used else "rod", cx, y0 + 15.5, glowc if glowc else c("#2a2420"), 0.95)
        hy = y0 + ph + 7
        head = ell(cx, hy, 9, 9.5, 30)
        if kind == "triglav":
            for sx in (-1, 1):
                sh_ = ell(cx + sx * 9, hy - 1, 6, 7.5, 24)
                form(sh_, wood, w=L * 0.9, sh=0.2)
                idol_face(cx + sx * 9.8, hy - 1.5, 0.55, glowc)
        form(head, wood, w=L, sdx=-2.5, sdy=1.5, sh=0.2)
        idol_face(cx, hy - 0.5, 0.85, glowc, used, beard=kind not in ("mokos", "morana"))
        if kind == "perun":
            cap = bez((cx - 9.5, hy + 4), (cx - 8, hy + 12), (cx + 8, hy + 12), (cx + 9.5, hy + 4)) + [(cx - 9.5, hy + 4)]
            form(cap, c("#5a4a3a"), w=L, sh=0.15)
            with T(cx + 11, y0 + 20, rot=-20):
                stroke([(0, -10), (0, 14)], 1.4, g=WOOD_L); stroke([(0.5, -10), (0.5, 14)], 0.4)
                shape([(0, 14), (5, 16.5), (6.5, 12), (0, 11)], IRON_L, w=0.6)
        elif kind == "veles":
            for s in (-1, 1):
                horn = bez((cx + s * 6, hy + 6), (cx + s * 14, hy + 9), (cx + s * 16, hy + 16), (cx + s * 13, hy + 21)) + \
                       bez((cx + s * 13, hy + 21), (cx + s * 12.5, hy + 15), (cx + s * 10, hy + 11), (cx + s * 4, hy + 8.5))
                form(horn, BONE, w=0.8, sh=0.15)
            fill(ell(cx, hy + 7.5, 7, 2.5, 18), c("#3a2c20"))
        elif kind == "mokos":
            sc = bez((cx - 10.5, hy - 6), (cx - 11, hy + 8), (cx - 6, hy + 12), (cx, hy + 12)) + bez((cx, hy + 12), (cx + 6, hy + 12), (cx + 11, hy + 8), (cx + 10.5, hy - 6)) + \
                 bez((cx + 10.5, hy - 6), (cx + 8, hy + 2), (cx + 7, hy + 5), (cx, hy + 6)) + bez((cx, hy + 6), (cx - 7, hy + 5), (cx - 8, hy + 2), (cx - 10.5, hy - 6))
            form(sc, c("#a03a32"), w=L, sh=0.15)
            for k in range(4): dot(cx - 6 + k * 4, hy + 9, 0.6, c("#f0d080"))
            for s in (-1, 1): stroke([(cx + s * 3, y0 + 4), (cx + s * 3.5, y0 + 1)], 0.6, g=c("#c84040"))
        elif kind == "svarog":
            cap = [(cx - 10, hy + 5), (cx + 10, hy + 5), (cx + 7, hy + 9), (cx - 7, hy + 9)]
            form(cap, c("#5a3a26"), w=L, sh=0.15)
            with T(cx - 12, y0 + 20, rot=25):
                stroke([(0, -8), (0, 8)], 1.4, g=WOOD_L)
                form(rect(-3.5, 8, 7, 4), IRON, w=0.6, sh=0.15)
            glow(cx, FEET + 15, 6, FLAME, 3, 0.6, 0.12)
        elif kind == "morana":
            for k in range(13):
                aa = math.radians(200 + k * 11.5)
                x1, y1 = cx + math.cos(aa) * 10.5, hy + 2 + math.sin(aa) * 6
                stroke([(cx + math.cos(aa) * 7, hy + 7 + math.sin(aa) * 3), (x1 + r.uniform(-1, 1), y1 - 8)], 0.7, g=c("#c8b070"))
            for k in range(9):
                aa = math.radians(20 + k * 17)
                stroke([(cx, hy + 6), (cx + math.cos(aa) * 11, hy + 6 + math.sin(aa) * 7)], 0.8, g=c("#d4bc7a"))
            with T(cx + 11, y0 + 24, rot=-10):
                stroke([(0, -10), (0, 6)], 1.2, g=WOOD_L)
                stroke(bez((0, 6), (6, 9), (10, 6), (9, 1)), 1.2, g=IRON_L); stroke(bez((0, 6), (6, 9), (10, 6), (9, 1)), 0.3)
        elif kind == "stribog":
            for k in range(3):
                yy = hy + 9 + k * 1.2
                stroke(bez((cx - 3, yy), (cx + 4, yy + 3), (cx + 10, yy + 1), (cx + 14, yy + 4)), 0.6, g=a(c("#c8eef4"), 0.8))
            bird = bez((cx - 6, hy + 10), (cx - 3, hy + 13), (cx, hy + 11), (cx, hy + 10)) + bez((cx, hy + 10), (cx + 3, hy + 13), (cx + 6, hy + 10), (cx + 7, hy + 11)) + [(cx, hy + 8.5)]
            form(bird, c("#4a4a52"), w=0.6, sh=0)
        elif kind == "rod":
            ring = ell(cx, hy + 13, 7, 7, 30)
            stroke(ring, 1.4, closed=True, g=GOLD); stroke(ring, 0.4, closed=True)
            for k in range(8):
                aa = math.radians(k * 45)
                stroke([(cx + math.cos(aa) * 7.8, hy + 13 + math.sin(aa) * 7.8), (cx + math.cos(aa) * 10, hy + 13 + math.sin(aa) * 10)], 0.7, g=GOLD)
        elif kind == "used":
            stroke([(cx - 3, y0 + ph - 2), (cx + 1, y0 + 30), (cx - 2, y0 + 18)], 0.7)
            stroke([(cx + 2, hy + 6), (cx + 4, hy - 2)], 0.6)
        if not used:
            for k, (dx, hh) in enumerate(((-11, 4), (-7, 6), (9, 5), (12, 3.5))):
                x = cx + dx; y = FEET + 7.5 + (k % 2) * 1.5
                shape(rect(x - 0.8, y, 1.6, hh), c("#e6dcc0"), w=0.35)
                flame(x, y + hh + 0.1, 0.35)
                glow(x, y + hh + 1.5, 3, FLAME, 3, 1, 0.08)
        else:
            for dx in (-10, 9):
                shape(rect(cx + dx - 0.8, FEET + 7.5, 1.6, 2.4), c("#8a8270"), w=0.35)
    return d


# ------------------------------------------------------------------ act props
def hrnek_dusicka(b):
    cx = b.w / 2
    glow(cx, FEET + 6, 11, c("#bfe0ff"), 6, 0.7, 0.08)
    shadow(cx, 14, 2.2)
    cup = [(cx - 7, FEET + 1)] + bez((cx - 7, FEET + 1), (cx - 6.6, FEET + 6), (cx - 5.5, FEET + 9), (cx - 4.5, FEET + 10)) + \
          [(cx + 4.5, FEET + 10)] + bez((cx + 4.5, FEET + 10), (cx + 5.5, FEET + 9), (cx + 6.6, FEET + 6), (cx + 7, FEET + 1))
    o = ell(cx, FEET + 1, 7, 2.2, 18, 180, 360) + cup[1:]
    form(o, c("#e8e2d8"), w=0.8, sdx=-1.5, sdy=0, sh=0.16)
    shape(ell(cx, FEET + 10, 4.5, 1.4, 16), c("#dcd4c6"), w=0.5)
    with clip(o):
        stroke(ell(cx, FEET + 4, 8, 1.8, 16, 180, 360), 0.6, g=c("#4a7ab8"))
        for k in range(4):
            dot(cx - 4.5 + k * 3, FEET + 6.2, 0.55, c("#4a7ab8"))
    hd = bez((cx + 6.5, FEET + 7.5), (cx + 10, FEET + 8), (cx + 10, FEET + 3), (cx + 6.8, FEET + 3))
    stroke(hd, 1.6, g=INKC); stroke(hd, 0.9, g=c("#e8e2d8"))
    fill(ell(cx, FEET + 1.3, 6.5, 1.0, 16), c("#cfe6ff", 0.7))
    for k in range(3):
        dot(cx - 4 + k * 4, FEET + 0.8, 0.5, c("#ffffff"))


def zvon(b):
    cx = b.w / 2
    shadow(cx, 52, 5)
    for s in (-1, 1):
        x = cx + s * 22
        beam_v(x, FEET, 66, 5)
        stroke([(x, FEET + 12), (x - s * 8, FEET + 1)], 3, g=WOOD_D, taper=False)
        stroke([(x, FEET + 12), (x - s * 8, FEET + 1)], 2, g=WOOD, taper=False)
    beam_h(cx - 28, cx + 28, 64, 5.5, d=3.5)
    stroke([(cx, 64), (cx, 58)], 1.4, g=IRON)
    bell = [(cx - 12, 26)] + bez((cx - 12, 26), (cx - 9, 30), (cx - 9, 40), (cx - 8, 50)) + bez((cx - 8, 50), (cx - 7, 58), (cx + 7, 58), (cx + 8, 50)) + \
           bez((cx + 8, 50), (cx + 9, 40), (cx + 9, 30), (cx + 12, 26))
    form(bell + ell(cx, 26, 12, 3, 20, 0, -180)[::-1], c("#a07a3a"), w=L * 1.1, sdx=-4, sdy=0, sh=0.22)
    stroke(ell(cx, 26, 12, 3, 20, 180, 360), L)
    for yy in (31, 48): stroke(ell(cx, yy, 9.5 - (yy - 31) * 0.05, 2, 18, 180, 360), 0.6, g=c("#6a4e22"))
    fill(ell(cx, 26.5, 10, 2.2, 18), c("#2a2018"))
    with clip(bell): stroke([(cx - 5, 30), (cx - 4, 54)], 1.4, g=c("#e0c070"), alpha=0.6)


def kotel(b):
    cx = b.w / 2; r = random.Random(23)
    shadow(cx, 46, 5)
    glow(cx, FEET + 4, 16, FLAME, 5, 0.4, 0.1)
    for k in range(5):
        x = cx - 12 + k * 6
        stroke([(x, FEET + 1), (x + r.uniform(-3, 3), FEET + 5)], 2, g=WOOD_D, taper=False)
    for k in range(6): flame(cx - 13 + k * 5.2, FEET + 2, r.uniform(0.6, 1.0))
    for s in (-1, 1): stroke([(cx + s * 16, FEET + 1), (cx + s * 13, FEET + 10)], 1.8, g=IRON_D)
    o = bez((cx - 20, FEET + 23), (cx - 21, FEET + 13), (cx - 12, FEET + 6), (cx, FEET + 6)) + bez((cx, FEET + 6), (cx + 12, FEET + 6), (cx + 21, FEET + 13), (cx + 20, FEET + 23))
    form(o + ell(cx, FEET + 23, 20, 4.5, 24, 0, 180)[1:-1], IRON_D, w=L * 1.1, sdx=-4, sdy=1, sh=0.22)
    shape(ell(cx, FEET + 23, 20, 4.5, 30), IRON, w=L)
    brew = ell(cx, FEET + 23, 17.5, 3.4, 30)
    glow(cx, FEET + 26, 18, GREEN, 5, 0.6, 0.07)
    shape(brew, c("#5fbf3a"), w=0.5)
    for _ in range(6):
        x, y = cx + r.uniform(-13, 13), FEET + 23 + r.uniform(-1.5, 1.5)
        stroke(ell(x, y, 1.4, 0.6, 10), 0.4, closed=True, g=GREEN_C)
    for i in range(3):
        fill(ell(cx - 4 + i * 5, FEET + 31 + i * 4, 4 + i, 2.5 + i * 0.5, 16), c("#b8f0a0", 0.18))
    with T(cx + 10, FEET + 28, rot=-30):
        stroke([(0, -4), (0, 16)], 1.5, g=WOOD_L); stroke([(0.5, -4), (0.5, 16)], 0.4)


def zrcadlo(b):
    cx = b.w / 2
    shadow(cx, 36, 4)
    for s in (-1, 1): stroke([(cx + s * 10, FEET + 1), (cx + s * 12, FEET + 10)], 2.2, g=WOOD_D, taper=False)
    fr = [(cx - 16, FEET + 6), (cx + 16, FEET + 6), (cx + 16, FEET + 52)] + ell(cx, FEET + 52, 16, 16, 20, 0, 180)[1:] + [(cx - 16, FEET + 52)]
    form(fr, c("#8a6a2e"), w=L * 1.1, sdx=-2, sdy=0, sh=0.2)
    gl = [(cx - 12.5, FEET + 9.5), (cx + 12.5, FEET + 9.5), (cx + 12.5, FEET + 52)] + ell(cx, FEET + 52, 12.5, 12.5, 20, 0, 180)[1:] + [(cx - 12.5, FEET + 52)]
    shape(gl, c("#7d8ea6"), w=0.7)
    with clip(gl):
        fill([(cx - 13, FEET + 30), (cx - 4, FEET + 60), (cx + 2, FEET + 60), (cx - 9, FEET + 26)], c("#d8e8f8", 0.45))
        fill([(cx + 2, FEET + 12), (cx + 7, FEET + 35), (cx + 9, FEET + 35), (cx + 4, FEET + 12)], c("#d8e8f8", 0.3))
        stroke([(cx + 6, FEET + 50), (cx + 1, FEET + 44), (cx + 3, FEET + 38)], 0.4, g=c("#ffffff"))
    for k in range(7):
        aa = math.radians(k * 30)
        shape(ell(cx + math.cos(aa) * 16, FEET + 52 + math.sin(aa) * 16, 1.8, 1.8, 10), GOLD, w=0.4)
    shape(ell(cx, FEET + 70, 3, 3, 16), c("#c03030"), w=0.5)


def koren(b):
    cx = b.w / 2; r = random.Random(29)
    shadow(cx, 70, 7)
    for i in range(12):
        x0 = cx + r.uniform(-8, 8); y0 = b.h - 2
        x1 = cx + r.uniform(-36, 36); y1 = FEET + r.uniform(0, 6)
        pts = bez((x0, y0), (x0 + r.uniform(-8, 8), y0 - 20), (x1 + r.uniform(-10, 10), y1 + 18), (x1, y1))
        w = r.uniform(2.2, 4.4)
        stroke(pts, w + 0.9, g=INKC); stroke(pts, w, g=c("#6e5236") if i % 3 else c("#7d6040"))
        stroke([(px - w * 0.2, py) for px, py in pts[2:12]], 0.3, g=c("#a08060"))
        for k in range(2):
            j = r.randrange(5, 14); x, y = pts[j]
            stroke(bez((x, y), (x + r.uniform(-4, 4), y - 3), (x + r.uniform(-7, 7), y - 6), (x + r.uniform(-9, 9), y - 9)), 0.7, g=c("#6e5236"))
    for _ in range(5):
        fill(blob(cx + r.uniform(-24, 24), r.uniform(FEET + 10, b.h - 10), r.uniform(3, 6), r.uniform(2, 3), r), c("#46602e"))
    for _ in range(4):
        pebble(chunk(cx + r.uniform(-30, 30), FEET + r.uniform(1, 6), 3, 2.2, r), STONE_D, w=0.5)


def houby(b):
    cx = b.w / 2; r = random.Random(31)
    glow(cx, FEET + 8, 16, c("#a0f0d0"), 5, 0.6, 0.06)
    items = sorted([(FEET + r.uniform(1, 11), cx + r.uniform(-15, 15), r.uniform(0.7, 1.4)) for _ in range(7)], reverse=True)
    for y, x, s in items:
        fill(ell(x + 1, y, 3 * s, 1 * s, 12), BLACK, 0.2)
        stem = [(x - 1 * s, y), (x + 1 * s, y), (x + 0.8 * s, y + 5 * s), (x - 0.8 * s, y + 5 * s)]
        shape(stem, c("#e6dcc8"), w=0.5)
        cap = bez((x - 4.5 * s, y + 4.5 * s), (x - 4 * s, y + 9 * s), (x + 4 * s, y + 9 * s), (x + 4.5 * s, y + 4.5 * s)) + [(x - 4.5 * s, y + 4.5 * s)]
        form(cap, c("#8fb0a0") if s > 1 else c("#b0905e"), w=0.6, sh=0.18)
        for k in range(3): dot(x - 2 * s + k * 2 * s, y + 6.5 * s, 0.45 * s, c("#e8fff0"))


def kovadlina(b):
    cx = b.w / 2
    shadow(cx, 34, 4)
    f, t = boxp(cx - 9, FEET, 18, 10, 5)
    form(f, WOOD_D, w=L, sdx=-2, sdy=0, sh=0.15); shape(t, WOOD, w=L * 0.8)
    stroke(ell(cx, FEET + 12.5, 6, 1.6, 16), 0.4, closed=True, g=WOOD_D)
    body = [(cx - 6, FEET + 12), (cx + 6, FEET + 12), (cx + 4, FEET + 17), (cx + 9, FEET + 21), (cx + 12, FEET + 21), (cx + 12, FEET + 25),
            (cx - 8, FEET + 25)] + bez((cx - 8, FEET + 25), (cx - 14, FEET + 25), (cx - 19, FEET + 23), (cx - 21, FEET + 21)) + \
           bez((cx - 21, FEET + 21), (cx - 15, FEET + 20), (cx - 8, FEET + 19), (cx - 4, FEET + 17))
    form(body, IRON, w=L * 1.1, sdx=-2, sdy=1.5, sh=0.2)
    shape(rect(cx - 8, FEET + 25, 20, 3), IRON_L, w=L * 0.8)
    stroke([(cx - 6, FEET + 26.5), (cx + 9, FEET + 26.5)], 0.4, g=c("#a8a8b4"))
    with T(cx + 6, FEET + 28.5, rot=12):
        stroke([(0, 0), (12, 0)], 1.4, g=WOOD_L); stroke([(0, 0.5), (12, 0.5)], 0.4)
        form(rect(-1.5, -2, 4, 4.2), IRON_D, w=0.6, sh=0.15)


def pec(b):
    cx = b.w / 2; r = random.Random(37)
    shadow(cx, 74, 7)
    glow(cx, FEET + 14, 30, FLAME, 6, 0.6, 0.07)
    body = [(cx - 34, FEET + 2)] + bez((cx - 34, FEET + 2), (cx - 36, FEET + 30), (cx - 26, FEET + 50), (cx, FEET + 52)) + \
           bez((cx, FEET + 52), (cx + 26, FEET + 50), (cx + 36, FEET + 30), (cx + 34, FEET + 2))
    form(body, c("#9a7458"), w=L * 1.2, sdx=-5, sdy=2, sh=0.2)
    with clip(body):
        for k in range(16):
            x, y = cx + r.uniform(-30, 30), FEET + r.uniform(4, 48)
            stroke([(x, y), (x + r.uniform(2, 5), y + r.uniform(-0.5, 0.5))], 0.4, g=c("#6e4e3a"))
        for k in range(10):
            fill(blob(cx + r.uniform(-28, 28), FEET + r.uniform(30, 50), 3, 1.8, r), c("#2a2422", 0.25))
    mouth = [(cx - 14, FEET + 5), (cx + 14, FEET + 5)] + ell(cx, FEET + 14, 14, 12, 24, 0, 180)
    shape(mouth, c("#3a1810"), w=L)
    with clip(mouth):
        fill(ell(cx, FEET + 6, 13, 9, 24), c("#ff7a20"))
        fill(ell(cx, FEET + 6, 9, 5.5, 24), c("#ffd060"))
        for k in range(5): flame(cx - 10 + k * 5, FEET + 5, r.uniform(1.0, 1.6))
    stroke(mouth, L * 1.1, closed=True)
    for k in range(-3, 4):
        aa = math.radians(90 - k * 22)
        shape(chunk(cx + math.cos(aa) * 16.5, FEET + 14 + math.sin(aa) * 14.5, 2.4, 1.7, r, n=5, rot=math.degrees(aa)), STONE_D, w=0.5)
    ch = rect(cx + 14, FEET + 40, 8, 26)
    form(ch, c("#8a6a52"), w=L, sdx=-1.5, sdy=0, sh=0.16)
    shape(rect(cx + 13, FEET + 66, 10, 2), c("#6e4e3a"), w=0.7)
    for i in range(3): fill(ell(cx + 18 + i * 3, FEET + 72 + i * 6, 3 + i, 2.2 + i, 16), c("#5a5a64", 0.35))
    for i in range(4):
        x = cx - 28 + i * 3.5
        stroke([(x, FEET + 1), (x + 1, FEET + 9)], 2.2, g=WOOD_D)


def smolinec(b):
    cx = b.w / 2; r = random.Random(41)
    shadow(cx, 40, 6)
    glow(cx, FEET + 18, 26, GREEN, 6, 0.9, 0.07)
    items = [(cx - 8, FEET + 9, 11, 8), (cx + 9, FEET + 8, 10, 7), (cx, FEET + 19, 10, 8)]
    for x, y, rx, ry in sorted(items, key=lambda t: -t[1]):
        p = chunk(x, y, rx, ry, r, n=8, k=0.15)
        form(p, c("#2e3a2c"), w=L, sdx=-2, sdy=1.6, sh=0.2)
        with clip(p):
            for k in range(3):
                q = [(x - rx + r.uniform(0, 3), y + r.uniform(-ry, ry) * 0.6)]
                while q[-1][0] < x + rx:
                    q.append((q[-1][0] + r.uniform(2, 4), q[-1][1] + r.uniform(-2, 2)))
                stroke(q, 2.6, g=a(GREEN, 0.3), taper=False); stroke(q, 1.0, g=GREEN); stroke(q, 0.35, g=GREEN_C)
        stroke(p, L, closed=True)
    for _ in range(6):
        dot(cx + r.uniform(-18, 18), FEET + r.uniform(14, 34), 0.5, GREEN_C)


def kbelik(b):
    cx = b.w / 2
    shadow(cx, 18, 3)
    o = ell(cx, FEET + 1.5, 6.5, 2.2, 16, 180, 360) + [(cx + 8, FEET + 15)] + ell(cx, FEET + 15, 8, 2.6, 16, 0, 180)[1:-1] + [(cx - 8, FEET + 15)]
    form(o, WOOD, w=L * 0.9, sdx=-2, sdy=0, sh=0.18)
    with clip(o):
        for k in (-4, -1, 2, 5): stroke([(cx + k * 0.85, FEET), (cx + k, FEET + 16)], 0.3, g=WOOD_D)
        for y in (FEET + 4, FEET + 12): stroke(ell(cx, y, 9, 2.3, 16, 180, 360), 1.0, g=IRON)
    shape(ell(cx, FEET + 15, 8, 2.6, 20), WOOD_D, w=0.7)
    shape(ell(cx, FEET + 15, 6.8, 2.0, 20), c("#3a4a5a"), w=0.4)
    fill(ell(cx - 2, FEET + 15.4, 2.5, 0.6, 10), c("#c8d8f0", 0.45))
    stroke(bez((cx - 8, FEET + 15), (cx - 7, FEET + 24), (cx + 7, FEET + 24), (cx + 8, FEET + 15)), 0.7, g=IRON)


def dub(b):
    cx = b.w / 2; r = random.Random(43)
    shadow(cx, 90, 10)
    for i in range(7):
        s = -1 if i % 2 else 1; x1 = cx + s * r.uniform(16, 40)
        pts = bez((cx + s * 6, FEET + 12), (cx + s * 12, FEET + 6), (x1 - s * 6, FEET + 3), (x1, FEET + r.uniform(0, 3)))
        stroke(pts, 4.4, g=INKC); stroke(pts, 3.4, g=BARK)
    trunk = bez((cx - 15, FEET + 2), (cx - 10, FEET + 30), (cx - 14, FEET + 55), (cx - 22, FEET + 80)) + [(cx + 18, FEET + 80)] + \
            bez((cx + 18, FEET + 80), (cx + 11, FEET + 55), (cx + 9, FEET + 30), (cx + 16, FEET + 2))
    form(trunk, BARK, w=L * 1.2, sdx=-6, sdy=0, sh=0.22)
    with clip(trunk):
        for k in range(12):
            x = cx + r.uniform(-12, 12)
            stroke(bez((x, FEET + r.uniform(0, 20)), (x + r.uniform(-3, 3), FEET + 30), (x + r.uniform(-3, 3), FEET + 50), (x + r.uniform(-6, 6), FEET + r.uniform(55, 80))), 0.45, g=BARK_D)
    hole = blob(cx + 1, FEET + 22, 4.5, 6.5, r)
    shape(hole, c("#1a1418"), w=0.8)
    for s, ang in ((-1, 140), (1, 40), (-1, 165), (1, 15)):
        x0, y0 = cx + s * 8, FEET + 70
        x1 = x0 + math.cos(math.radians(ang)) * 50; y1 = y0 + 30 + math.sin(math.radians(ang)) * 30
        pts = bez((x0, y0), (x0 + s * 10, y0 + 15), (x1 - s * 10, y1 - 8), (x1, y1))
        stroke(pts, 7.5, g=INKC); stroke(pts, 6, g=BARK)
    crowns = [(cx - 42, 136, 30, 22), (cx + 42, 132, 30, 22), (cx - 8, 150, 38, 24), (cx + 22, 158, 26, 18), (cx - 30, 160, 24, 17)]
    for x, y, rx, ry in crowns:
        pts = blob(x, y, rx, ry, r, n=12, k=0.12)
        form(pts, c("#3e3a50"), w=L * 1.1, sdx=4, sdy=3, sh=0.14)
        for _ in range(4):
            stroke(ell(x + r.uniform(-rx * 0.6, rx * 0.6), y + r.uniform(-ry * 0.6, ry * 0.4), 6, 4, 10, 200, 330), 0.5, g=c("#2c2a3a"))
    for _ in range(9):
        dot(cx + r.uniform(-60, 60), r.uniform(120, 170), 0.8, c("#a3a8d8"))
    for k in range(4):
        x = cx + r.uniform(-50, 50); y = r.uniform(110, 140)
        stroke([(x, y), (x + r.uniform(-1, 1), y - r.uniform(8, 18))], 0.5, g=c("#6e6a80"))


def navi_svice(b):
    cx = b.w / 2; r = random.Random(47)
    glow(cx, FEET + 14, 20, FLAME, 6, 0.7, 0.06)
    fill(ell(cx, FEET + 3, 18, 4, 24), BLACK, 0.18)
    items = sorted([(FEET + r.uniform(0, 8), cx + r.uniform(-14, 14), r.uniform(5, 15)) for _ in range(7)], reverse=True)
    for y, x, h in items:
        fill(ell(x, y, 2.8, 1.0, 12), c("#e4dccc"))
        c_ = rect(x - 1.5, y, 3, h)
        form(c_, c("#e8e0cc"), w=0.6, sdx=-0.8, sdy=0, sh=0.15)
        for k in range(2):
            dy = r.uniform(1, h - 1)
            stroke([(x + r.choice((-1.5, 1.5)), y + h), (x + r.choice((-1.5, 1.5)), y + dy)], 0.7, g=c("#f4ecd8"))
        stroke([(x, y + h), (x, y + h + 0.8)], 0.4)
        flame(x, y + h + 0.7, 0.55)


def kalinov_most(b):
    w = b.w; cx = w / 2; r = random.Random(53)
    deck_y0 = FEET + 10; deck_h = 30
    for x in (24, w - 24):
        pf = rect(x - 5, FEET, 10, 12)
        form(pf, STONE_D, w=L, sdx=-2, sdy=0, sh=0.18)
    deck = rect(8, deck_y0, w - 16, deck_h)
    shape(deck, c("#6a3a2c"), w=L)
    with clip(deck):
        x = 8
        while x < w - 8:
            pw = r.uniform(5, 7)
            p = rect(x + 0.3, deck_y0, pw - 0.6, deck_h)
            g = r.choice((c("#7a4030"), c("#6e382a"), c("#86483a")))
            form(p, g, w=0.5, sdx=-0.6, sdy=0, sh=0.1)
            if r.random() < 0.45:
                yy = deck_y0 + r.uniform(4, deck_h - 4)
                stroke([(x + 1, yy), (x + pw - 1, yy + r.uniform(-1, 1))], 1.4, g=c("#ff7a30", 0.6)); stroke([(x + 1, yy), (x + pw - 1, yy)], 0.4, g=c("#ffd070"))
            x += pw
        fill(rect(8, deck_y0, w - 16, 4), c("#ff7a30", 0.18))
    beam_h(6, w - 6, deck_y0 - 4, 4, c("#4e2c22"))
    for yy in (deck_y0 + deck_h,):
        beam_h(6, w - 6, yy, 3, c("#5a3226"), d=1.5)
    for x in range(14, int(w) - 8, 22):
        beam_v(x, deck_y0 + deck_h, deck_y0 + deck_h + 14, 2.6, c("#5a3226"))
        beam_v(x, deck_y0 - 4, deck_y0 + 4, 2.6, c("#5a3226"))
    beam_h(10, w - 10, deck_y0 + deck_h + 12, 2.4, c("#6a3a2c"))
    beam_h(10, w - 10, deck_y0 + 2, 2.0, c("#6a3a2c"))
    for k in range(6):
        x = r.uniform(20, w - 20)
        fill(ell(x, deck_y0 + deck_h + 20 + k * 2, r.uniform(8, 14), 2.5, 16), c("#ffb070", 0.08))


def oltar(b):
    cx = b.w / 2; r = random.Random(59)
    shadow(cx, 84, 7)
    glow(cx, FEET + 46, 36, c("#bfd8ff"), 6, 0.9, 0.05)
    f, t = boxp(cx - 40, FEET, 80, 6, 10)
    form(f, STONE_D, w=L, sdx=-2, sdy=0, sh=0.15); shape(t, STONE, w=L * 0.8)
    f, t = boxp(cx - 30, FEET + 6, 60, 22, 14)
    form(f, c("#6e6a78"), w=L * 1.1, sdx=-3, sdy=0, sh=0.18)
    shape(t, c("#8a869a"), w=L)
    with clip(f):
        for k in range(5):
            x = cx - 24 + k * 12
            symbol(["perun", "veles", "svarog", "morana", "rod"][k], x, FEET + 17, c("#3a3646"), 0.75)
    stroke([(cx - 30, FEET + 24), (cx + 30, FEET + 24)], 0.5, g=c("#4a4656"))
    for s in (-1, 1): stroke([(cx + s * 20, FEET + 29), (cx + s * 5, FEET + 40), (cx + s * 12, FEET + 38)], 0.5, g=c("#4a4656"))
    glow(cx, FEET + 36, 7, c("#dff0ff"), 4, 1, 0.12)
    for s in (-1, 1):
        x = cx + s * 22
        shape(rect(x - 1.4, FEET + 30, 2.8, 8), c("#d8d0bc"), w=0.5)
        with T(x, FEET + 38.2, 0.5):
            o = bez((0, 0), (-2.4, 1.2), (-1.6, 4.4), (0.2, 7.2)) + bez((0.2, 7.2), (1.2, 4.6), (2.6, 1.6), (0, 0))
            shape(o, c("#bfe0ff"), w=0.4); fill(ell(0, 2, 0.9, 1.6, 10), c("#ffffff"))
    for k in range(6):
        x = cx + r.uniform(-14, 14)
        pebble(chunk(x, FEET + 31 + r.uniform(0, 6), 1.6, 1.1, r, n=6), c("#9aa6b4"), w=0.4, ground=0.1)
        dot(x, FEET + 32, 0.4, c("#ffffff"))


def kniha(b):
    """lectern with an open book and a candle; meant to be seen from across a dark room"""
    cx = b.w / 2; r = random.Random(61)
    shadow(cx, 40, 5)
    glow(cx + 4, FEET + 50, 30, FLAME, 6, 0.9, 0.06)
    shape(ell(cx, FEET + 1.5, 13, 3.5, 20), WOOD_D, w=L * 0.8)
    form(rect(cx - 3, FEET + 2, 6, 34), WOOD, w=L, sdx=-1.2, sdy=0, sh=0.18)
    top = [(cx - 22, FEET + 36), (cx + 22, FEET + 36), (cx + 20, FEET + 48), (cx - 20, FEET + 48)]
    form(top, WOOD_L, w=L, sdx=0, sdy=-1.5, sh=0.15)
    stroke([(cx - 22, FEET + 36), (cx + 22, FEET + 36)], 1.4, g=WOOD_D)
    for s in (-1, 1):
        pg = [(cx, FEET + 39), (cx + s * 17, FEET + 38), (cx + s * 16, FEET + 49), (cx, FEET + 47.5)]
        shape(pg, c("#e8dcbc"), w=0.7)
        for k in range(5):
            y = FEET + 40.5 + k * 1.6
            x0, x1 = (cx + s * 2.5, cx + s * r.uniform(11, 14.5))
            stroke([(x0, y), (x1, y + 0.3)], 0.35, g=c("#6a5a48"))
    stroke([(cx, FEET + 39), (cx, FEET + 47.5)], 0.7, g=c("#8a6a3a"))
    fill(rect(cx + 13, FEET + 37.5, 1.2, 9), c("#8a2a24"))
    x = cx + 17
    shape(ell(x, FEET + 49, 3.2, 1.1, 12), IRON_L, w=0.5)
    form(rect(x - 1.3, FEET + 49, 2.6, 8), c("#e8e0cc"), w=0.5, sdx=-0.6, sdy=0, sh=0.15)
    stroke([(x, FEET + 57), (x, FEET + 57.8)], 0.4)
    flame(x, FEET + 57.6, 0.6)
    glow(x, FEET + 60, 5, FLAME_C, 4, 1, 0.12)


# ------------------------------------------------------------------ town buildings
def roof_gable(cx, y0, w, h, ridge_d, col, kind="tiles"):
    """gable-front roof: triangle over the facade plus both slopes receding up"""
    apex = (cx, y0 + h)
    left = [(cx - w / 2 - 2, y0 - 1), apex, (apex[0], apex[1] + ridge_d), (cx - w / 2 - 2, y0 - 1 + ridge_d)]
    right = [(cx + w / 2 + 2, y0 - 1), apex, (apex[0], apex[1] + ridge_d), (cx + w / 2 + 2, y0 - 1 + ridge_d)]
    for side, g in ((left, col), (right, col)):
        form(side, g, w=L, sdx=0, sdy=0, sh=0)
    offset_shadow(right, -4, 0, 0.0)
    fill(right, BLACK, 0.16)
    for side in (left, right):
        with clip(side):
            k = 0
            while k < ridge_d:
                stroke([(cx - w / 2 - 3, y0 - 1 + k), (cx, y0 + h + k)] if side is left else [(cx + w / 2 + 3, y0 - 1 + k), (cx, y0 + h + k)], 0.35, g=ROOF_D if kind == "tiles" else SLATE_D)
                k += 3
        stroke(side, L, closed=True)


def facade_gable(cx, y0, w, wall_h, gable_h, col):
    o = [(cx - w / 2, y0), (cx + w / 2, y0), (cx + w / 2, y0 + wall_h), (cx, y0 + wall_h + gable_h), (cx - w / 2, y0 + wall_h)]
    form(o, col, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    return o


def roof_eave(cx, y0, w, h, col, hip=0.0, kind="tiles"):
    o = [(cx - w / 2 - 3, y0 - 1), (cx + w / 2 + 3, y0 - 1), (cx + w / 2 - hip, y0 + h), (cx - w / 2 + hip, y0 + h)]
    form(o, col, w=L * 1.1, sdx=0, sdy=-3, sh=0.14)
    if kind == "tiles": tiles(o, y0 - 1, y0 + h, cx - w / 2 - 4, cx + w / 2 + 4, 3.2)
    elif kind == "slate": scallops(o, y0, y0 + h, cx - w / 2 - 4, cx + w / 2 + 4)
    else: thatch_lines(o, y0, y0 + h, cx - w / 2 - 4, cx + w / 2 + 4, random.Random(3))
    shape(rect(cx - w / 2 + hip - 1, y0 + h - 0.5, w - 2 * hip + 2, 2.2), ROOF_D if kind != "slate" else SLATE_D, w=L * 0.8)
    if hip:
        for s in (-1, 1):
            stroke([(cx + s * (w / 2 + 3), y0 - 1), (cx + s * (w / 2 - hip), y0 + h)], L * 0.8)
    return o


def plinth(x0, x1, y0, h, r):
    p = rect(x0, y0, x1 - x0, h)
    form(p, STONE_D, w=L, sdx=0, sdy=0, sh=0)
    stones_course(x0, x1, y0, y0 + h, r, STONE, 1)


def timber_frame(x0, x1, y0, y1, r, g=c("#4e3626")):
    for x in [x0 + 1] + [x0 + (x1 - x0) * k / 4 for k in (1, 2, 3)] + [x1 - 1]:
        stroke([(x, y0), (x, y1)], 2.2, g=g, taper=False); stroke([(x + 0.8, y0), (x + 0.8, y1)], 0.35)
    for y in (y0 + 0.8, (y0 + y1) / 2, y1 - 0.8):
        stroke([(x0, y), (x1, y)], 2.2, g=g, taper=False)
    for k in range(4):
        xa = x0 + (x1 - x0) * k / 4; xb = x0 + (x1 - x0) * (k + 1) / 4
        if k % 2 == 0: stroke([(xa + 1, y0 + 1), (xb - 1, (y0 + y1) / 2 - 1)], 1.8, g=g, taper=False)
        else: stroke([(xa + 1, (y0 + y1) / 2 - 1), (xb - 1, y0 + 1)], 1.8, g=g, taper=False)


def dum_a(b):
    """gable-front burgher house, plastered, painted bands, red tiles"""
    cx = b.w / 2; r = random.Random(61); w = 120; wall_h = 62; gh = 34
    shadow(cx, w + 20, 8)
    roof_gable(cx, FEET + wall_h, w, gh, 40, ROOF)
    o = facade_gable(cx, FEET, w, wall_h, gh, PLASTER)
    plinth(cx - w / 2, cx + w / 2, FEET, 8, r)
    stroke([(cx - w / 2, FEET + wall_h), (cx + w / 2, FEET + wall_h)], 1.6, g=PLASTER_D)
    stroke([(cx - w / 2, FEET + 34), (cx + w / 2, FEET + 34)], 1.2, g=PLASTER_D)
    door(cx - 8, FEET + 1, 16, 26)
    for x in (cx - 46, cx - 28, cx + 16, cx + 34):
        window(x, FEET + 13, 11, 15, lit=(x == cx - 28))
    for x in (cx - 46, cx - 28, cx - 6, cx + 16, cx + 34):
        window(x, FEET + 41, 11, 15, lit=(x in (cx - 6, cx + 34)), shut=c("#5a6e4a"))
    window(cx - 6, FEET + wall_h + 8, 12, 14, lit=True, arch=True)
    stroke(o, L * 1.1, closed=True)
    chimney(cx + 26, FEET + wall_h + gh + 10, 7, 18)
    sign(cx + 14, FEET + 30)


def sign(x, y):
    stroke([(x, y), (x + 9, y)], 0.9, g=IRON)
    shape(rect(x + 3, y - 8, 9, 7), WOOD_L, w=0.6)
    stroke([(x + 5, y), (x + 5, y - 1)], 0.4); stroke([(x + 10, y), (x + 10, y - 1)], 0.4)


def dum_b(b):
    """eave-front house with dormer, slate roof, timber upper floor"""
    cx = b.w / 2; r = random.Random(67); w = 150; wall_h = 58
    shadow(cx, w + 20, 8)
    roof_eave(cx, FEET + wall_h, w, 52, SLATE, hip=10, kind="slate")
    dorm = [(cx - 12, FEET + wall_h + 18), (cx + 12, FEET + wall_h + 18), (cx + 12, FEET + wall_h + 32), (cx, FEET + wall_h + 40), (cx - 12, FEET + wall_h + 32)]
    form(dorm, PLASTER_W, w=L, sh=0.12)
    window(cx - 5, FEET + wall_h + 20, 10, 11, lit=True)
    shape([(cx - 15, FEET + wall_h + 31), (cx, FEET + wall_h + 42), (cx + 15, FEET + wall_h + 31), (cx + 15, FEET + wall_h + 29), (cx, FEET + wall_h + 39), (cx - 15, FEET + wall_h + 29)], SLATE_D, w=L * 0.8)
    chimney(cx - 50, FEET + wall_h + 38, 8, 20)
    f = rect(cx - w / 2, FEET, w, wall_h)
    form(f, PLASTER_W, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    fill(rect(cx - w / 2, FEET + 30, w, wall_h - 30), c("#b49e7c"))
    timber_frame(cx - w / 2, cx + w / 2, FEET + 30, FEET + wall_h, r)
    plinth(cx - w / 2, cx + w / 2, FEET, 7, r)
    door(cx + 20, FEET + 1, 15, 24)
    for x in (cx - 62, cx - 42, cx - 14, cx + 46):
        window(x, FEET + 11, 11, 14, lit=(x in (cx - 42, cx + 46)))
    for x in (cx - 60, cx - 30, cx + 10, cx + 40):
        window(x + 4, FEET + 37, 10, 13, lit=(x == cx + 10))
    stroke(f, L * 1.1, closed=True)
    fill(rect(cx - w / 2, FEET + wall_h - 3, w, 3), BLACK, 0.25)


def dum_c(b):
    """narrow baroque gable house, ochre"""
    cx = b.w / 2; r = random.Random(71); w = 104; wall_h = 60
    shadow(cx, w + 20, 8)
    roof_gable(cx, FEET + wall_h, w, 30, 38, ROOF)
    g = [(cx - w / 2, FEET), (cx + w / 2, FEET), (cx + w / 2, FEET + wall_h)] + \
        bez((cx + w / 2, FEET + wall_h), (cx + w / 2 - 4, FEET + wall_h + 2), (cx + w / 2 - 14, FEET + wall_h + 4), (cx + 34, FEET + wall_h + 14)) + \
        bez((cx + 34, FEET + wall_h + 14), (cx + 22, FEET + wall_h + 18), (cx + 20, FEET + wall_h + 28), (cx + 10, FEET + wall_h + 36)) + \
        bez((cx + 10, FEET + wall_h + 36), (cx + 6, FEET + wall_h + 42), (cx - 6, FEET + wall_h + 42), (cx - 10, FEET + wall_h + 36)) + \
        bez((cx - 10, FEET + wall_h + 36), (cx - 20, FEET + wall_h + 28), (cx - 22, FEET + wall_h + 18), (cx - 34, FEET + wall_h + 14)) + \
        bez((cx - 34, FEET + wall_h + 14), (cx - w / 2 + 14, FEET + wall_h + 4), (cx - w / 2 + 4, FEET + wall_h + 2), (cx - w / 2, FEET + wall_h))
    form(g, c("#a8844e"), w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    plinth(cx - w / 2, cx + w / 2, FEET, 8, r)
    for x in (cx - w / 2 + 2, cx + w / 2 - 6):
        shape(rect(x, FEET + 8, 4, wall_h - 8), c("#d8b27a"), w=0.6)
    stroke([(cx - w / 2, FEET + wall_h), (cx + w / 2, FEET + wall_h)], 1.6, g=c("#9a7444"))
    door(cx - 8, FEET + 1, 16, 25, g=c("#4e5a3a"))
    for x in (cx - 38, cx + 26):
        window(x, FEET + 12, 11, 15, lit=(x > cx))
    for x in (cx - 38, cx - 6, cx + 26):
        window(x, FEET + 38, 11, 15, lit=(x == cx - 38))
    window(cx - 6, FEET + wall_h + 14, 12, 14, lit=False, arch=True)
    shape(ell(cx, FEET + wall_h + 34, 3, 3, 14), c("#e0c070"), w=0.6)
    stroke(g, L * 1.1, closed=True)


def kovarna(b):
    cx = b.w / 2; r = random.Random(73); w = 140; wall_h = 50
    shadow(cx, w + 30, 9)
    roof_eave(cx, FEET + wall_h, w, 44, ROOF, hip=0)
    chimney(cx + 34, FEET + wall_h + 24, 12, 30)
    f = rect(cx - w / 2, FEET, w, wall_h)
    form(f, STONE, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    stones_course(cx - w / 2, cx + w / 2, FEET, FEET + wall_h, r, STONE, 6)
    op = [(cx - 50, FEET), (cx + 4, FEET), (cx + 4, FEET + 34)] + ell(cx - 23, FEET + 34, 27, 10, 20, 0, 180)[1:] + [(cx - 50, FEET + 34)]
    shape(op, c("#2a1e18"), w=L * 1.1)
    with clip(op):
        glow(cx - 23, FEET + 14, 26, FLAME, 6, 0.8, 0.12)
        f2, t2 = boxp(cx - 34, FEET, 22, 12, 6)
        form(f2, STONE_D, w=0.8, sh=0.1); shape(t2, c("#3a2a22"), w=0.7)
        fill(ell(cx - 23, FEET + 15, 8, 2.5, 16), c("#ff8a30")); fill(ell(cx - 23, FEET + 15.5, 4.5, 1.3, 12), c("#ffe080"))
        for k in range(3): flame(cx - 27 + k * 4, FEET + 15, 0.6)
        for k in range(4): stroke([(cx - 45 + k * 3, FEET + 34), (cx - 45 + k * 3 + 1, FEET + 22)], 0.5, g=IRON_L)
    beam_h(cx - 52, cx + 6, FEET + 34 + 10, 3)
    for x in (cx - 50, cx + 4): beam_v(x, FEET, FEET + 44, 3.2, top=False)
    door(cx + 16, FEET + 1, 15, 24)
    window(cx + 44, FEET + 18, 12, 14, lit=True)
    shape(rect(cx - 14, FEET + 1, 12, 5), WOOD_D, w=0.6)
    stroke(f, L * 1.1, closed=True)
    sign(cx + 52, FEET + 38)
    hs = ell(cx + 61, FEET + 34, 3, 3, 14, 200, 520)
    stroke(hs, 1.0, g=IRON_L)


def hostinec(b):
    cx = b.w / 2; r = random.Random(79); w = 180; wall_h = 64
    shadow(cx, w + 24, 9)
    roof_eave(cx, FEET + wall_h, w, 58, ROOF, hip=14)
    for x in (cx - 50, cx + 50):
        dorm = [(x - 10, FEET + wall_h + 18), (x + 10, FEET + wall_h + 18), (x + 10, FEET + wall_h + 30), (x, FEET + wall_h + 37), (x - 10, FEET + wall_h + 30)]
        form(dorm, PLASTER, w=L, sh=0.12)
        window(x - 4, FEET + wall_h + 19, 8, 10, lit=True)
        shape([(x - 13, FEET + wall_h + 29), (x, FEET + wall_h + 39), (x + 13, FEET + wall_h + 29), (x + 13, FEET + wall_h + 27), (x, FEET + wall_h + 36), (x - 13, FEET + wall_h + 27)], ROOF_D, w=L * 0.8)
    chimney(cx - 10, FEET + wall_h + 40, 9, 22)
    f = rect(cx - w / 2, FEET, w, wall_h)
    form(f, PLASTER, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    plinth(cx - w / 2, cx + w / 2, FEET, 8, r)
    arc = [(cx - 14, FEET), (cx + 14, FEET), (cx + 14, FEET + 26)] + ell(cx, FEET + 26, 14, 10, 18, 0, 180)[1:] + [(cx - 14, FEET + 26)]
    shape(arc, c("#2e221c"), w=L * 1.1)
    door(cx - 10, FEET, 20, 32)
    for x in (cx - 78, cx - 56, cx - 34, cx + 22, cx + 44, cx + 66):
        window(x, FEET + 14, 12, 15, lit=True)
    for x in (cx - 78, cx - 56, cx - 34, cx - 6, cx + 22, cx + 44, cx + 66):
        window(x, FEET + 42, 12, 15, lit=(x in (cx - 56, cx - 6, cx + 66)), shut=c("#7a3a2e"))
    stroke(f, L * 1.1, closed=True)
    stroke([(cx + 20, FEET + 38), (cx + 34, FEET + 38)], 1.0, g=IRON)
    sg = rect(cx + 24, FEET + 26, 13, 11)
    shape(sg, WOOD_L, w=0.7)
    m = bez((cx + 27, FEET + 34), (cx + 27, FEET + 28), (cx + 34, FEET + 28), (cx + 34, FEET + 34))
    shape(m + [(cx + 27, FEET + 34)], c("#e0c070"), w=0.5)
    for x in (cx - 22, cx + 18):
        stroke([(x, FEET + 34), (x, FEET + 30)], 0.6, g=IRON)
        glow(x, FEET + 27, 9, FLAME, 4, 1, 0.08)
        shape(rect(x - 2, FEET + 24, 4, 6), LIT, w=0.6)
    barrel(cx - 64, FEET + 1, 14, 15)
    barrel(cx + 82, FEET + 1, 12, 13)


def chalupa(b):
    cx = b.w / 2; r = random.Random(83); w = 120; wall_h = 40
    shadow(cx, w + 24, 8)
    o = roof_eave(cx, FEET + wall_h, w + 6, 60, THATCH, hip=18, kind="thatch")
    with clip(o):
        for k in range(6):
            fill(blob(cx + r.uniform(-50, 50), FEET + wall_h + r.uniform(10, 50), r.uniform(5, 9), r.uniform(3, 5), r), c("#5d7a3c", 0.55))
    chimney(cx + 20, FEET + wall_h + 44, 7, 18)
    f = rect(cx - w / 2, FEET, w, wall_h)
    form(f, c("#aea286"), w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    for x in range(int(cx - w / 2) + 8, int(cx + w / 2), 22):
        stroke([(x, FEET), (x, FEET + wall_h)], 2.4, g=c("#5a4030"), taper=False)
    stroke([(cx - w / 2, FEET + wall_h - 1.2), (cx + w / 2, FEET + wall_h - 1.2)], 2.4, g=c("#5a4030"), taper=False)
    plinth(cx - w / 2, cx + w / 2, FEET, 6, r)
    door(cx - 9, FEET + 1, 14, 26, g=c("#4e5a3a"), arch=False)
    for x in (cx - 46, cx + 22):
        window(x, FEET + 14, 11, 12, lit=True, shut=c("#4e6a7a"))
    for k in range(6):
        x = cx - 48 + k * 9
        stroke([(x, FEET + wall_h - 2), (x, FEET + wall_h - 8)], 0.4)
        bunch = blob(x, FEET + wall_h - 10, 2.2, 3.2, r, n=7)
        shape(bunch, r.choice((c("#6a8a44"), c("#8a7a3a"), c("#9a5a6a"))), w=0.4)
    stroke(f, L * 1.1, closed=True)
    for k in range(5):
        x = cx + 38 + k * 4; pot = rect(x - 1.5, FEET + 1, 3, 3)
        if x < cx + w / 2 + 6: shape(pot, CLAY, w=0.4); tuft_small(x, FEET + 4)


def tuft_small(x, y):
    for k in range(4):
        aa = math.radians(60 + k * 20)
        stroke([(x, y), (x + math.cos(aa) * 3, y + math.sin(aa) * 3)], 0.6, g=LEAF_L)


def lattice_tower(cx, y0, w0, w1, h, g=WOOD):
    for s in (-1, 1):
        stroke([(cx + s * w0 / 2, y0), (cx + s * w1 / 2, y0 + h)], 3.4, g=INKC, taper=False)
        stroke([(cx + s * w0 / 2, y0), (cx + s * w1 / 2, y0 + h)], 2.4, g=g, taper=False)
    n = 4
    for k in range(n + 1):
        t = k / n; y = y0 + h * t; hw = (w0 + (w1 - w0) * t) / 2
        stroke([(cx - hw, y), (cx + hw, y)], 2.6, g=INKC, taper=False); stroke([(cx - hw, y), (cx + hw, y)], 1.7, g=g, taper=False)
        if k < n:
            t2 = (k + 1) / n; y2 = y0 + h * t2; hw2 = (w0 + (w1 - w0) * t2) / 2
            for s in (-1, 1):
                stroke([(cx - s * hw, y), (cx + s * hw2, y2)], 1.4, g=INKC, taper=False)
                stroke([(cx - s * hw, y), (cx + s * hw2, y2)], 0.8, g=g, taper=False)


def wheel(x, y, rr, g=IRON, spokes=8):
    stroke(ell(x, y, rr, rr, 40), 3.0, closed=True, g=INKC)
    stroke(ell(x, y, rr, rr, 40), 2.0, closed=True, g=g)
    for k in range(spokes):
        aa = math.tau * k / spokes
        stroke([(x, y), (x + math.cos(aa) * rr, y + math.sin(aa) * rr)], 0.8, g=g)
    shape(ell(x, y, rr * 0.16, rr * 0.16, 14), IRON_D, w=0.6)


def shaft_house(cx, w, h, wall, roof, r, glowc=None, roof_kind="tiles"):
    f = rect(cx - w / 2, FEET, w, h)
    roof_eave(cx, FEET + h, w, h * 0.7, roof, hip=6, kind=roof_kind)
    form(f, wall, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    gate = [(cx - 12, FEET), (cx + 12, FEET), (cx + 12, FEET + 20)] + ell(cx, FEET + 20, 12, 8, 16, 0, 180)[1:] + [(cx - 12, FEET + 20)]
    shape(gate, c("#1c1814"), w=L * 1.1)
    if glowc:
        with clip(gate):
            glow(cx, FEET + 2, 18, glowc, 6, 0.7, 0.12)
    return f


def sachta_hora(b):
    cx = b.w / 2; r = random.Random(89)
    shadow(cx, 110, 10)
    lattice_tower(cx, FEET + 30, 70, 26, 110, WOOD)
    wheel(cx, FEET + 146, 15, WOOD_D, 6)
    shape(rect(cx - 18, FEET + 138, 36, 4), WOOD, w=L)
    stroke([(cx + 14, FEET + 146), (cx + 4, FEET + 40)], 0.7, g=c("#8a7a5a"))
    f = rect(cx - 50, FEET, 100, 34)
    roof_eave(cx, FEET + 34, 100, 26, ROOF, hip=4)
    form(f, PLASTER_D, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    timber_frame(cx - 50, cx + 50, FEET + 2, FEET + 34, r)
    gate = rect(cx - 12, FEET, 24, 22)
    shape(gate, c("#1c1814"), w=L * 1.1)
    with clip(gate):
        glow(cx, FEET + 4, 14, LIT, 4, 0.6, 0.12)
        stroke([(cx - 6, FEET), (cx - 6, FEET + 22)], 1.2, g=WOOD); stroke([(cx + 6, FEET), (cx + 6, FEET + 22)], 1.2, g=WOOD)
    beam_h(cx - 14, cx + 14, FEET + 22, 3)
    window(cx - 38, FEET + 12, 10, 11, lit=True); window(cx + 28, FEET + 12, 10, 11, lit=False)
    stroke(f, L * 1.1, closed=True)
    lantern_small(cx - 18, FEET + 18); lantern_small(cx + 18, FEET + 18)


def lantern_small(x, y):
    glow(x, y, 8, FLAME, 4, 1, 0.08)
    shape(rect(x - 1.8, y - 2.5, 3.6, 5), LIT, w=0.5)
    stroke([(x - 2.2, y + 2.5), (x + 2.2, y + 2.5)], 0.7, g=IRON)


def sachta_vojtech(b):
    cx = b.w / 2; r = random.Random(97)
    shadow(cx, 116, 10)
    lattice_tower(cx, FEET + 40, 64, 40, 100, c("#5a5a62"))
    for dx in (-10, 10): wheel(cx + dx, FEET + 146, 13, IRON, 10)
    stroke([(cx - 10, FEET + 133), (cx - 22, FEET + 40)], 0.6, g=IRON_L)
    stroke([(cx + 10, FEET + 133), (cx + 22, FEET + 40)], 0.6, g=IRON_L)
    f = rect(cx - 54, FEET, 108, 46)
    roof_eave(cx, FEET + 46, 108, 22, SLATE, hip=0, kind="slate")
    form(f, c("#9a5a44"), w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    with clip(f):
        for k in range(18): stroke([(cx - 54, FEET + k * 2.6), (cx + 54, FEET + k * 2.6)], 0.3, g=c("#7a4234"))
    for x in (cx - 46, cx - 26, cx + 14, cx + 34):
        window(x, FEET + 16, 12, 20, lit=(x in (cx - 26, cx + 34)), arch=True, frame=STONE_D)
    gate = [(cx - 10, FEET), (cx + 10, FEET), (cx + 10, FEET + 22)] + ell(cx, FEET + 22, 10, 7, 14, 0, 180)[1:] + [(cx - 10, FEET + 22)]
    shape(gate, c("#1c1814"), w=L * 1.1)
    with clip(gate): glow(cx, FEET + 4, 14, LIT, 4, 0.6, 0.12)
    shape(rect(cx - 14, FEET + 34, 28, 6), c("#d8ccb0"), w=0.6)
    stroke([(cx - 10, FEET + 37), (cx + 10, FEET + 37)], 0.6, g=c("#4a3a30"))
    stroke(f, L * 1.1, closed=True)


def sachta_svornost(b):
    cx = b.w / 2; r = random.Random(101)
    shadow(cx, 110, 10)
    tw = rect(cx - 16, FEET + 36, 32, 86)
    form(tw, c("#8e8a82"), w=L * 1.1, sdx=-3, sdy=0, sh=0.12)
    stones_course(cx - 16, cx + 16, FEET + 36, FEET + 122, r, c("#8e8a82"), 10)
    window(cx - 5, FEET + 88, 10, 16, lit=True, arch=True, frame=STONE_D)
    shape(rect(cx - 18, FEET + 122, 36, 3), STONE_D, w=L)
    tent = [(cx - 19, FEET + 125), (cx + 19, FEET + 125), (cx, FEET + 162)]
    form(tent, c("#5a6a5a"), w=L * 1.1, sdx=3, sdy=0, sh=0.18)
    stroke([(cx, FEET + 162), (cx, FEET + 170)], 0.9, g=GOLD); dot(cx, FEET + 170, 1.2, GOLD)
    wheel(cx, FEET + 136, 9, IRON, 8)
    f = rect(cx - 52, FEET, 104, 38)
    roof_eave(cx, FEET + 38, 104, 24, SLATE, hip=6, kind="slate")
    form(f, PLASTER, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    plinth(cx - 52, cx + 52, FEET, 7, r)
    gate = [(cx - 12, FEET), (cx + 12, FEET), (cx + 12, FEET + 20)] + ell(cx, FEET + 20, 12, 8, 16, 0, 180)[1:] + [(cx - 12, FEET + 20)]
    shape(gate, c("#141a14"), w=L * 1.1)
    with clip(gate):
        glow(cx, FEET + 2, 20, GREEN, 6, 0.6, 0.14)
    for x in (cx - 42, cx - 26, cx + 16, cx + 32): window(x, FEET + 14, 10, 13, lit=(x == cx - 26))
    stroke(f, L * 1.1, closed=True)
    symbol("morana", cx, FEET + 32, c("#4a4038"), 0.4)
    stroke([(cx - 4, FEET + 30), (cx + 4, FEET + 34)], 1.0, g=IRON_D); stroke([(cx + 4, FEET + 30), (cx - 4, FEET + 34)], 1.0, g=IRON_D)


def chram_barbory(b):
    cx = b.w / 2; r = random.Random(103)
    shadow(cx, 240, 14)
    W_ = 210; H_ = 108
    tents = [(cx - 62, 86, 92), (cx + 62, 86, 92), (cx, 104, 132)]
    base_y = FEET + H_
    for x, tw, th in tents:
        tent = [(x - tw / 2, base_y)] + bez((x - tw / 2, base_y), (x - tw * 0.28, base_y + th * 0.25), (x - tw * 0.06, base_y + th * 0.6), (x, base_y + th)) + \
               bez((x, base_y + th), (x + tw * 0.06, base_y + th * 0.6), (x + tw * 0.28, base_y + th * 0.25), (x + tw / 2, base_y))
        form(tent, SLATE, w=L * 1.2, sdx=6, sdy=0, sh=0.2)
        scallops(tent, base_y, base_y + th, x - tw / 2, x + tw / 2, 3.2)
        stroke([(x, base_y + th * 0.15), (x, base_y + th)], 0.6, g=SLATE_L)
        for k in range(1, 4):
            yy = base_y + th * k / 4.2; hw = tw / 2 * (1 - k / 4.2) ** 1.3
            shape(rect(x - 1.8, yy - 2, 3.6, 4.4), SLATE_D, w=0.5)
        stroke([(x, base_y + th), (x, base_y + th + 9)], 1.1, g=GOLD)
        shape(ell(x, base_y + th + 9.5, 1.6, 1.6, 12), GOLD, w=0.5)
        stroke(tent, L * 1.2, closed=True)
    for s in (-1, 1):
        for k in range(2):
            x0 = cx + s * (W_ / 2 + 4 + k * 12); y0 = FEET + 40 + k * 20
            arc = bez((x0, y0), (x0 + s * 4, y0 + 20), (cx + s * (W_ / 2 - 10), FEET + H_ - 10), (cx + s * (W_ / 2 - 16), FEET + H_ - 4))
            stroke(arc, 3.6, g=INKC); stroke(arc, 2.6, g=c("#b4a68a"))
            p = rect(x0 - 3.5, FEET, 7, y0 - FEET + 6)
            form(p, c("#a8987a"), w=L, sdx=-2, sdy=0, sh=0.14)
            spire = [(x0 - 4, y0 + 6), (x0 + 4, y0 + 6), (x0, y0 + 20)]
            form(spire, c("#b4a68a"), w=L * 0.9, sh=0.15)
    f = rect(cx - W_ / 2, FEET, W_, H_)
    form(f, c("#a89878"), w=L * 1.2, sdx=-4, sdy=0, sh=0.1)
    with clip(f):
        for k in range(26): stroke([(cx - W_ / 2, FEET + k * 4.4), (cx + W_ / 2, FEET + k * 4.4)], 0.3, g=c("#a29274"))
    fill(rect(cx - W_ / 2, FEET + H_ - 6, W_, 6), BLACK, 0.15)
    piers = [cx - W_ / 2 + 4 + i * (W_ - 8) / 6 for i in range(7)]
    for i, x in enumerate(piers[:-1]):
        x1 = piers[i + 1]; wx = (x + x1) / 2
        ww = 14 if i not in (2, 3) else 16
        lancet(wx, FEET + 26, ww, 60 if i not in (2, 3) else 66, lit=i in (1, 4))
    for x in piers:
        p = [(x - 4, FEET), (x + 4, FEET), (x + 3, FEET + H_ - 4), (x - 3, FEET + H_ - 4)]
        form(p, c("#ad9d7e"), w=L, sdx=-2, sdy=0, sh=0.16)
        for k in range(3): stroke([(x - 4 + k * 0.4, FEET + 20 + k * 26), (x + 4 - k * 0.4, FEET + 20 + k * 26)], 0.6)
        pin = [(x - 3.5, FEET + H_ - 4), (x + 3.5, FEET + H_ - 4), (x, FEET + H_ + 14)]
        form(pin, c("#b4a68a"), w=L * 0.9, sh=0.15)
        for k in range(3):
            dot(x + (k - 1) * 1.6 * (1 - k * 0.2), FEET + H_ + 2 + k * 4, 0.6, c("#8e7e62"))
    portal = [(cx - 14, FEET), (cx + 14, FEET), (cx + 14, FEET + 22)] + bez((cx + 14, FEET + 22), (cx + 14, FEET + 34), (cx + 4, FEET + 40), (cx, FEET + 42)) + \
             bez((cx, FEET + 42), (cx - 4, FEET + 40), (cx - 14, FEET + 34), (cx - 14, FEET + 22))
    form(portal, c("#2a201a"), w=L * 1.2, sh=0)
    with clip(portal): glow(cx, FEET + 4, 20, LIT, 5, 0.6, 0.1)
    door(cx - 10, FEET, 20, 30, g=c("#4a3020"))
    stroke(f, L * 1.2, closed=True)
    rose = ell(cx, FEET + 92, 9, 9, 30)
    shape(rose, LIT, w=L)
    for k in range(8):
        aa = math.tau * k / 8
        stroke([(cx, FEET + 92), (cx + math.cos(aa) * 9, FEET + 92 + math.sin(aa) * 9)], 0.6, g=c("#5a4030"))
    stroke(ell(cx, FEET + 92, 4, 4, 16), 0.6, closed=True, g=c("#5a4030"))


def lancet(x, y, w, h, lit=False):
    o = [(x - w / 2, y), (x + w / 2, y), (x + w / 2, y + h - w * 0.8)] + bez((x + w / 2, y + h - w * 0.8), (x + w / 2, y + h - w * 0.2), (x + w * 0.1, y + h - 0.5), (x, y + h)) + \
        bez((x, y + h), (x - w * 0.1, y + h - 0.5), (x - w / 2, y + h - w * 0.2), (x - w / 2, y + h - w * 0.8))
    if lit: glow(x, y + h / 2, h * 0.6, LIT, 4, 1.4, 0.05)
    shape(o, LIT if lit else c("#3a4458"), w=L)
    with clip(o):
        if lit: fill(rect(x - w, y, w * 2, h * 0.4), c("#ff9a3a", 0.25))
        for k in (-1, 1): stroke([(x + k * w / 6, y), (x + k * w / 6, y + h - w * 0.6)], 0.7, g=c("#4a3a2e"))
        for k in range(1, 6): stroke([(x - w / 2, y + k * h / 7), (x + w / 2, y + k * h / 7)], 0.4, g=c("#4a3a2e"))
        stroke(ell(x, y + h - w * 0.55, w * 0.2, w * 0.2, 14), 0.5, closed=True, g=c("#4a3a2e"))


def zvonice(b):
    cx = b.w / 2; r = random.Random(107)
    shadow(cx, 70, 8)
    f = rect(cx - 30, FEET, 60, 30)
    form(f, STONE, w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    stones_course(cx - 30, cx + 30, FEET, FEET + 30, r, STONE, 4)
    door(cx - 7, FEET, 14, 22)
    tw = [(cx - 26, FEET + 30), (cx + 26, FEET + 30), (cx + 22, FEET + 112), (cx - 22, FEET + 112)]
    form(tw, WOOD, w=L * 1.1, sdx=-3, sdy=0, sh=0.14)
    planks_v(tw, cx - 26, cx + 26, 5, FEET + 30, FEET + 112)
    bel = rect(cx - 16, FEET + 86, 32, 22)
    shape(bel, c("#1e1a1c"), w=L)
    with clip(bel):
        bell = [(cx - 9, FEET + 88)] + bez((cx - 9, FEET + 88), (cx - 7, FEET + 96), (cx - 6, FEET + 102), (cx, FEET + 104)) + bez((cx, FEET + 104), (cx + 6, FEET + 102), (cx + 7, FEET + 96), (cx + 9, FEET + 88))
        form(bell, c("#8a6a34"), w=L, sh=0.2)
        beam_h(cx - 16, cx + 16, FEET + 104, 3)
    for s in (-1, 1): stroke([(cx + s * 9, FEET + 86), (cx + s * 9, FEET + 108)], 2.2, g=WOOD_D, taper=False)
    window(cx - 4, FEET + 54, 8, 14, lit=False, arch=True)
    roof = [(cx - 32, FEET + 110), (cx + 32, FEET + 110), (cx, FEET + 168)]
    form(roof, SLATE, w=L * 1.1, sdx=4, sdy=0, sh=0.2)
    scallops(roof, FEET + 110, FEET + 168, cx - 32, cx + 32, 3)
    stroke(roof, L * 1.1, closed=True)
    stroke([(cx, FEET + 168), (cx, FEET + 176)], 1.0, g=GOLD)
    stroke([(cx - 3, FEET + 173), (cx + 3, FEET + 173)], 1.0, g=GOLD)


def socha_permonika(b):
    cx = b.w / 2
    shadow(cx, 36, 4)
    f, t = boxp(cx - 14, FEET, 28, 20, 8)
    form(f, STONE, w=L, sdx=-2, sdy=0, sh=0.15); shape(t, STONE_L, w=L * 0.8)
    shape(rect(cx - 15.5, FEET + 18, 31, 2.5), STONE_L, w=0.7)
    for k in range(3): stroke([(cx - 6 + k * 6, FEET + 8), (cx - 6 + k * 6 + 3, FEET + 11)], 0.4, g=STONE_D)
    ST, STD = c("#9a958a"), c("#77726a")
    y0 = FEET + 24
    for s in (-1, 1):
        shape(ell(cx + s * 3.5, y0 + 1.5, 3.5, 2, 14), STD, w=0.7)
    body = [(cx - 7, y0 + 3), (cx + 7, y0 + 3), (cx + 8.5, y0 + 18), (cx - 8.5, y0 + 18)]
    form(body, ST, w=L, sdx=-2, sdy=0, sh=0.18)
    stroke([(cx - 7.5, y0 + 9), (cx + 7.5, y0 + 9)], 1.0, g=STD)
    shape(ell(cx, y0 + 24, 6, 6, 24), ST, w=L)
    beard = bez((cx - 5.5, y0 + 23), (cx - 5, y0 + 15), (cx - 1, y0 + 12), (cx, y0 + 12)) + bez((cx, y0 + 12), (cx + 1, y0 + 12), (cx + 5, y0 + 15), (cx + 5.5, y0 + 23))
    form(beard + [(cx, y0 + 21)], c("#aaa59a"), w=L * 0.9, sh=0.15)
    for k in (-2, 0, 2): stroke([(cx + k, y0 + 19), (cx + k * 0.8, y0 + 14)], 0.35, g=STD)
    dot(cx - 2, y0 + 24.5, 0.7, c("#3a3632")); dot(cx + 2, y0 + 24.5, 0.7, c("#3a3632"))
    shape(ell(cx, y0 + 22.5, 1.4, 1.1, 10), ST, w=0.5)
    cap = bez((cx - 6.5, y0 + 26), (cx - 5, y0 + 33), (cx + 3, y0 + 36), (cx + 9, y0 + 31)) + [(cx + 6.5, y0 + 26)]
    form(cap, c("#8a3a30"), w=L, sh=0.15)
    stroke([(cx + 7.5, y0 + 15), (cx + 11, y0 + 11)], 2.0, g=ST)
    with T(cx + 11, y0 + 3, 0.7): lamp(0, 0, 1.0)
    for k in range(4):
        r = random.Random(k)
        fill(blob(cx + r.uniform(-12, 12), FEET + r.uniform(2, 16), 2.6, 1.6, r), c("#56703a", 0.5))


def mincovna(b):
    cx = b.w / 2; r = random.Random(109); w = 176; wall_h = 72
    shadow(cx, w + 24, 9)
    roof_eave(cx, FEET + wall_h, w, 50, ROOF, hip=12)
    chimney(cx + 54, FEET + wall_h + 30, 9, 20)
    chimney(cx - 60, FEET + wall_h + 26, 8, 16, smoke=False)
    f = rect(cx - w / 2, FEET, w, wall_h)
    form(f, c("#ad9a76"), w=L * 1.1, sdx=-3, sdy=0, sh=0.1)
    for i in range(5):
        x = cx - 70 + i * 35
        o = [(x - 13, FEET), (x + 13, FEET), (x + 13, FEET + 20)] + ell(x, FEET + 20, 13, 10, 18, 0, 180)[1:] + [(x - 13, FEET + 20)]
        shape(o, c("#3a2a22"), w=L)
        with clip(o):
            glow(x, FEET + 10, 16, FLAME if i in (1, 3) else LIT, 4, 0.7, 0.1 if i in (1, 3) else 0.05)
        stroke(ell(x, FEET + 20, 13, 10, 18, 0, 180), 1.6, g=STONE_D)
    for x in (cx - 80, cx - 52, cx - 22, cx + 10, cx + 40, cx + 68):
        window(x, FEET + 42, 12, 16, lit=(x in (cx - 52, cx + 40)), frame=STONE_D)
    stroke([(cx - w / 2, FEET + 34), (cx + w / 2, FEET + 34)], 1.8, g=c("#9a8460"))
    stroke(f, L * 1.1, closed=True)
    shape(ell(cx, FEET + 64, 8, 5, 24), c("#a8a8b0"), w=0.8)
    shape(ell(cx, FEET + 64, 4.5, 4.5, 20), GOLD, w=0.7)
    stroke(ell(cx, FEET + 64, 3, 3, 14), 0.4, closed=True, g=c("#8a6a20"))
    with T(cx - 40, FEET): barrel(0, 0.5, 13, 14)
    for k in range(4):
        x = cx + 48 + k * 3.5
        shape(ell(x, FEET + 2 + k * 0.6, 2, 0.8, 10), GOLD, w=0.3)


def stan(b):
    cx = b.w / 2; r = random.Random(113)
    shadow(cx, 80, 7)
    o = [(cx - 40, FEET + 2), (cx + 40, FEET + 2), (cx + 10, FEET + 46), (cx - 10, FEET + 46)]
    top = [(cx - 10, FEET + 46), (cx + 10, FEET + 46), (cx + 8, FEET + 60), (cx - 8, FEET + 60)]
    form(o, c("#7a7466"), w=L * 1.1, sdx=4, sdy=0, sh=0.16)
    form(top, c("#8a8474"), w=L, sh=0.1)
    with clip(o):
        for k in range(6):
            stroke([(cx - 40 + k * 16, FEET + 2), (cx - 10 + k * 4, FEET + 46)], 0.5, g=c("#5e5a4e"))
        for k in range(4):
            fill(blob(cx + r.uniform(-28, 28), FEET + r.uniform(6, 36), r.uniform(4, 7), r.uniform(3, 5), r), c("#5e5a4e", 0.4))
    fl = [(cx - 12, FEET + 2), (cx + 12, FEET + 2), (cx, FEET + 38)]
    shape(fl, c("#1e1a20"), w=L)
    with clip(fl): glow(cx, FEET + 4, 12, c("#9ab0e0"), 4, 0.6, 0.12)
    stroke([(cx, FEET + 38), (cx - 18, FEET + 2)], 0.8, g=c("#8a8474"))
    for s in (-1, 1):
        stroke([(cx + s * 8, FEET + 58), (cx + s * 44, FEET + 1)], 0.5, g=c("#a09a88"))
        stroke([(cx + s * 44, FEET + 0.5), (cx + s * 44, FEET + 3)], 1.4, g=WOOD_D)
    stroke([(cx, FEET + 60), (cx, FEET + 68)], 1.4, g=WOOD_D)


def ohniste(b):
    cx = b.w / 2; r = random.Random(127)
    glow(cx, FEET + 12, 24, FLAME, 6, 0.7, 0.08)
    shadow(cx, 34, 5)
    for k in range(10):
        aa = math.tau * k / 10
        x, y = cx + math.cos(aa) * 13, FEET + 7 + math.sin(aa) * 5
        if math.sin(aa) > 0:
            pebble(chunk(x, y, 3, 2.2, r, n=6), STONE_D, w=0.6)
    fill(ell(cx, FEET + 7, 11, 3.6, 20), c("#2a2020"))
    fill(ell(cx, FEET + 7.5, 7, 2.2, 16), c("#ff7a30"))
    for s in (-1, 1):
        stroke([(cx + s * 9, FEET + 5), (cx - s * 2, FEET + 13)], 2.6, g=INKC); stroke([(cx + s * 9, FEET + 5), (cx - s * 2, FEET + 13)], 1.8, g=WOOD_D)
    stroke([(cx - 6, FEET + 9), (cx + 7, FEET + 6)], 2.4, g=INKC); stroke([(cx - 6, FEET + 9), (cx + 7, FEET + 6)], 1.6, g=WOOD)
    for k, s in enumerate((1.4, 2.0, 1.6, 1.1)):
        flame(cx - 4.5 + k * 3, FEET + 7, s)
    for k in range(4):
        aa = math.tau * k / 10 + math.pi
        x, y = cx + math.cos(aa * 1.0 + 0.3 * k) * 13, FEET + 7 - abs(math.sin(aa + 0.3 * k)) * 5
        pebble(chunk(x, y, 3.2, 2.3, r, n=6), STONE, w=0.6)
    for k in range(5):
        dot(cx + r.uniform(-6, 6), FEET + r.uniform(22, 36), 0.4, c("#ffd070"))


def studna(b):
    cx = b.w / 2; r = random.Random(131)
    shadow(cx, 52, 6)
    o = ell(cx, FEET + 3, 20, 5, 24, 180, 360) + [(cx + 20, FEET + 16)] + ell(cx, FEET + 16, 20, 6, 24, 0, 180)[1:-1] + [(cx - 20, FEET + 16)]
    form(o, STONE, w=L * 1.1, sdx=-3, sdy=0, sh=0.14)
    with clip(o):
        for k in range(3):
            y = FEET + 4 + k * 4.4
            stroke(ell(cx, y, 21, 5.5, 24, 180, 360), 0.4, g=STONE_D)
            for j in range(8):
                x = cx - 18 + j * 5 + (k % 2) * 2.5
                stroke([(x, y - 5 * math.sqrt(max(0, 1 - ((x - cx) / 21) ** 2))), (x, y + 4.4 - 5 * math.sqrt(max(0, 1 - ((x - cx) / 21) ** 2)))], 0.35, g=STONE_D)
    shape(ell(cx, FEET + 16, 20, 6, 30), STONE_L, w=L)
    shape(ell(cx, FEET + 16, 16, 4.4, 30), c("#151a22"), w=0.7)
    fill(ell(cx - 3, FEET + 15.5, 5, 1.2, 14), c("#5a7090", 0.5))
    for s in (-1, 1): beam_v(cx + s * 18, FEET + 14, FEET + 46, 3.2)
    beam_h(cx - 20, cx + 20, FEET + 34, 3)
    stroke(ell(cx, FEET + 35.5, 3, 3, 12), 0.6, closed=True)
    stroke([(cx, FEET + 34), (cx, FEET + 22)], 0.6, g=c("#8a7a5a"))
    with T(cx, FEET + 18): barrel(0, 0, 7, 6, lid=False)
    roof = [(cx - 26, FEET + 44), (cx + 26, FEET + 44), (cx + 18, FEET + 60), (cx - 18, FEET + 60)]
    form(roof, ROOF, w=L * 1.1, sdx=0, sdy=-2, sh=0.15)
    tiles(roof, FEET + 44, FEET + 60, cx - 27, cx + 27, 3)
    stroke(roof, L * 1.1, closed=True)


def crown(cx, cy, rx, ry, r, g, n=11):
    pts = []
    for i in range(n):
        a0 = math.tau * i / n; a1 = math.tau * (i + 1) / n
        p0 = (cx + math.cos(a0) * rx, cy + math.sin(a0) * ry); p1 = (cx + math.cos(a1) * rx, cy + math.sin(a1) * ry)
        am = (a0 + a1) / 2; k = 1.14 + 0.1 * r.random()
        m = (cx + math.cos(am) * rx * k, cy + math.sin(am) * ry * k)
        pts += bez(p0, ((p0[0] + m[0]) / 2 + (m[0] - cx) * 0.18, (p0[1] + m[1]) / 2 + (m[1] - cy) * 0.18),
                   ((p1[0] + m[0]) / 2 + (m[0] - cx) * 0.18, (p1[1] + m[1]) / 2 + (m[1] - cy) * 0.18), p1, 6)[:-1]
    fill(pts, g)
    offset_shadow(pts, -rx * 0.18, ry * 0.2, 0.18)
    stroke(pts, L * 1.1, closed=True)
    return pts


def tree(b, kind):
    cx = b.w / 2; r = random.Random(kind)
    shadow(cx + 4, 64, 9)
    trunk = bez((cx - 7, FEET), (cx - 4.5, FEET + 16), (cx - 5, FEET + 30), (cx - 3.5, FEET + 50)) + [(cx + 3.5, FEET + 50)] + \
            bez((cx + 3.5, FEET + 50), (cx + 5, FEET + 30), (cx + 4.5, FEET + 16), (cx + 7, FEET))
    form(trunk, BARK, w=L, sdx=-2, sdy=0, sh=0.18)
    for k in range(3):
        x = cx + r.uniform(-3, 3); stroke(bez((x, FEET + 4), (x + 0.5, FEET + 18), (x - 0.5, FEET + 30), (x, FEET + 40)), 0.4, g=BARK_D)
    for s in (-1, 1):
        stroke([(cx + s * 6, FEET + 1), (cx + s * 11, FEET - 0.5)], 2.2, g=BARK)
    if kind == "a":
        masses = [(cx - 20, 74, 24, 19, LEAF_D), (cx + 20, 76, 24, 19, LEAF_D), (cx, 96, 34, 25, LEAF), (cx - 11, 114, 21, 15, LEAF_L), (cx + 13, 112, 19, 14, LEAF)]
    else:
        masses = [(cx, 70, 28, 21, c("#344c32")), (cx, 92, 34, 25, c("#3e5a38")), (cx, 116, 26, 19, c("#4a663e"))]
    for x, y, rx, ry, g in masses:
        crown(x, y, rx, ry, r, g)
        for _ in range(3):
            stroke(ell(x + r.uniform(-rx * 0.5, rx * 0.5), y + r.uniform(-ry * 0.5, ry * 0.3), rx * 0.25, ry * 0.2, 10, 200, 330), 0.5, g=c("#2a3a22"))
    for _ in range(14):
        x, y = cx + r.uniform(-30, 30), r.uniform(70, 125)
        dot(x, y, 0.7, c("#7a9858") if kind == "a" else c("#80a060"))


def strom_a(b): tree(b, "a")
def strom_b(b): tree(b, "b")


def smrk(b):
    cx = b.w / 2; r = random.Random(137)
    shadow(cx + 3, 50, 7)
    form(rect(cx - 3.5, FEET, 7, 20), BARK, w=L, sdx=-1.5, sdy=0, sh=0.18)
    tiers = 6; y0 = FEET + 14; H = 128
    for i in range(tiers):
        t = i / tiers
        yb = y0 + H * t * 0.85; yt = yb + H * 0.32
        hw = 34 * (1 - t) + 6
        pts = [(cx - hw, yb)]
        n = 7
        for k in range(1, n):
            x = cx - hw + 2 * hw * k / n
            pts.append((x - hw / n * 0.5, yb + 3 + r.uniform(-0.5, 1)))
            pts.append((x, yb + r.uniform(-1.2, 0)))
        pts += [(cx + hw, yb), (cx + hw * 0.15, yt - 2), (cx, yt), (cx - hw * 0.15, yt - 2)]
        g = SPRUCE if i % 2 else c("#3c5a44")
        fill(pts, g)
        offset_shadow(pts, -5, 2, 0.18)
        stroke(pts, L, closed=True)
        for k in range(4):
            x = cx + r.uniform(-hw * 0.6, hw * 0.6)
            stroke([(x, yb + 3), (x + (x - cx) * 0.1, yb + 8)], 0.4, g=SPRUCE_D)
    for _ in range(4):
        x, y = cx + r.uniform(-20, 20), r.uniform(30, 90)
        shape(ell(x, y, 1.6, 2.4, 10), c("#7a5233"), w=0.4)


def plot(b):
    cx = b.w / 2; r = random.Random(139)
    shadow(cx, 60, 3)
    for y in (FEET + 8, FEET + 20):
        p = [(cx - 32, y), (cx + 32, y + r.uniform(-1, 1)), (cx + 32, y + 3.2), (cx - 32, y + 3.2)]
        form(p, WOOD, w=L * 0.9, sh=0.12)
    for k in range(6):
        x = cx - 28 + k * 11.2 + r.uniform(-0.6, 0.6); h = 28 + r.uniform(-2, 2)
        pk = [(x - 3, FEET), (x + 3, FEET), (x + 3, FEET + h), (x, FEET + h + 4), (x - 3, FEET + h)]
        form(pk, WOOD_L if k % 2 else WOOD, w=L * 0.9, sdx=-1.4, sdy=0, sh=0.16)
        stroke([(x - 0.5, FEET + 3), (x - 0.3, FEET + h - 3)], 0.3, g=WOOD_D)
        dot(x, FEET + 9.6, 0.5, IRON_L); dot(x, FEET + 21.6, 0.5, IRON_L)


def vuz(b):
    cx = b.w / 2; r = random.Random(149)
    shadow(cx, 84, 6)
    wheel(cx - 26, FEET + 12, 12, WOOD_D, 10)
    bed = [(cx - 42, FEET + 14), (cx + 36, FEET + 14), (cx + 40, FEET + 32), (cx - 46, FEET + 32)]
    form(bed, WOOD, w=L, sdx=-3, sdy=0, sh=0.16)
    planks_h(bed, FEET + 14, FEET + 32, 6, cx - 47, cx + 41)
    for x in (cx - 30, cx, cx + 26):
        stroke([(x, FEET + 14.5), (x + (x - cx) * 0.06, FEET + 31.5)], 1.4, g=WOOD_D)
    top = [(cx - 46, FEET + 32), (cx + 40, FEET + 32), (cx + 40, FEET + 44), (cx - 46, FEET + 44)]
    shape(top, WOOD_D, w=L)
    for k in range(5):
        x = cx - 38 + k * 14
        sack = blob(x, FEET + 40, 7, 6, r, n=8, k=0.1)
        form(sack, c("#b8a47a"), w=L * 0.8, sdx=-1.5, sdy=1, sh=0.16)
        stroke([(x - 2, FEET + 44), (x + 1, FEET + 45)], 0.5)
    wheel(cx + 24, FEET + 12, 12, WOOD_D, 10)
    with T(cx + 40, FEET + 18):
        stroke([(0, 0), (28, -6)], 2.6, g=INKC); stroke([(0, 0), (28, -6)], 1.8, g=WOOD)


def lucerna(b):
    cx = b.w / 2
    glow(cx, 66, 20, FLAME, 6, 1.0, 0.07)
    shadow(cx, 14, 2.5)
    f, t = boxp(cx - 4, FEET, 8, 4, 2.5)
    form(f, STONE_D, w=L * 0.8, sh=0.1); shape(t, STONE, w=0.6)
    p = rect(cx - 1.6, FEET + 4, 3.2, 52)
    form(p, IRON, w=L * 0.8, sdx=-0.8, sdy=0, sh=0.18)
    for y in (FEET + 14, FEET + 50): shape(rect(cx - 2.4, y, 4.8, 1.6), IRON_D, w=0.5)
    stroke([(cx, FEET + 56), (cx + 7, FEET + 58)], 1.0, g=IRON)
    box = [(cx - 5, FEET + 56), (cx + 5, FEET + 56), (cx + 6.5, FEET + 68), (cx - 6.5, FEET + 68)]
    shape(box, LIT, w=L * 0.9)
    with clip(box):
        fill(rect(cx - 7, FEET + 56, 14, 4), c("#ff9a3a", 0.3))
        flame(cx, FEET + 58, 0.7)
    for x in (cx - 1.8, cx + 1.8): stroke([(x, FEET + 56), (x * 1.0, FEET + 68)], 0.5, g=IRON_D)
    shape([(cx - 8, FEET + 68), (cx + 8, FEET + 68), (cx, FEET + 74)], IRON, w=L * 0.8)
    dot(cx, FEET + 75, 1, IRON)


# ------------------------------------------------------------------ registry
def J(fp, blocks=True, light=None, breakable=False, interact=None):
    return {"footprint": list(fp), "blocks": blocks, "light": light, "breakable": breakable, "interact": interact}


def LT(col, rad): return {"color": col, "radius": rad}


PROPS = [
    ("podpera", 128, 160, podpera, J((2, 1), False)),
    ("vozik", 140, 110, vozik, J((2, 1))),
    ("sud", 64, 80, sud, J((1, 1), breakable=True)),
    ("sud_broken", 64, 80, sud_broken, J((0, 0), False)),
    ("truhla", 80, 88, truhla, J((1, 1), interact="chest")),
    ("truhla_open", 80, 88, truhla_open, J((1, 1))),
    ("kosti", 96, 64, kosti, J((0, 0), False)),
    ("ruda", 96, 96, ruda, J((1, 1), breakable=True)),
    ("kahan_nastenny", 48, 80, kahan_nastenny, J((0, 0), False, LT("#ffb85c", 3))),
    ("schody_dolu", 128, 112, schody_dolu, J((2, 1), True, interact="stairs_down")),
    ("schody_nahoru", 96, 160, schody_nahoru, J((1, 1), True, LT("#dfe8ff", 2), interact="stairs_up")),
    ("klec", 160, 200, klec, J((2, 1), True, interact="waypoint")),
    ("kamen", 80, 64, kamen, J((1, 1))),
    ("lebky", 80, 72, lebky, J((1, 1))),
    ("urna", 64, 80, urna, J((1, 1), breakable=True)),
    ("urna_broken", 64, 80, urna_broken, J((0, 0), False)),
]
for k in ("perun", "veles", "mokos", "svarog", "morana", "stribog", "triglav", "rod"):
    PROPS.append((f"modla_{k}", 96, 160, modla(k), J((1, 1), True, LT(SHRINE[k][1].hex, 2), interact="shrine")))
PROPS.append(("modla_used", 96, 160, modla("used"), J((1, 1))))
PROPS += [
    ("hrnek_dusicka", 48, 48, hrnek_dusicka, J((1, 1), False, LT("#bfe0ff", 2), breakable=True)),
    ("zvon", 128, 160, zvon, J((2, 1), interact="quest")),
    ("kotel", 112, 112, kotel, J((1, 1), True, LT("#9cff6a", 3))),
    ("zrcadlo", 96, 160, zrcadlo, J((1, 1))),
    ("koren", 160, 128, koren, J((2, 1))),
    ("houby", 80, 64, houby, J((0, 0), False, LT("#a0f0d0", 1))),
    ("kovadlina", 96, 80, kovadlina, J((1, 1))),
    ("pec", 160, 176, pec, J((2, 1), True, LT("#ff9a40", 4))),
    ("smolinec", 96, 96, smolinec, J((1, 1), True, LT("#8cf26a", 2), breakable=True)),
    ("kbelik", 56, 64, kbelik, J((1, 1), False, interact="quest")),
    ("dub", 280, 360, dub, J((2, 1), interact="quest")),
    ("truhla_kostej", 112, 96, truhla_kostej, J((1, 1), interact="chest")),
    ("navi_svice", 80, 80, navi_svice, J((0, 0), False, LT("#ffb85c", 2))),
    ("kalinov_most", 320, 160, kalinov_most, J((5, 2), False, LT("#ff7a30", 2))),
    ("kniha", 96, 150, kniha, J((1, 1), True, LT("#ffc864", 2), interact="book")),
    ("oltar", 192, 160, oltar, J((3, 1), True, LT("#bfd8ff", 3), interact="quest")),
    ("dum_a", 288, 304, dum_a, J((4, 2))),
    ("dum_b", 352, 300, dum_b, J((5, 2))),
    ("dum_c", 256, 296, dum_c, J((4, 2))),
    ("kovarna", 352, 280, kovarna, J((5, 2), True, LT("#ff9a40", 3))),
    ("hostinec", 420, 336, hostinec, J((6, 2), True, LT("#ffc864", 3))),
    ("chalupa", 320, 296, chalupa, J((4, 2), True, LT("#ffc864", 2))),
    ("sachta_hora", 260, 360, sachta_hora, J((3, 2), True, LT("#ffc864", 2), interact="stairs_down")),
    ("sachta_vojtech", 260, 360, sachta_vojtech, J((3, 2), True, LT("#ffc864", 2), interact="stairs_down")),
    ("sachta_svornost", 260, 360, sachta_svornost, J((3, 2), True, LT("#8cf26a", 2), interact="stairs_down")),
    ("chram_barbory", 520, 560, chram_barbory, J((7, 3), True, LT("#ffc864", 3))),
    ("zvonice", 192, 360, zvonice, J((2, 2), True, interact="quest")),
    ("socha_permonika", 96, 160, socha_permonika, J((1, 1))),
    ("mincovna", 400, 340, mincovna, J((6, 2), True, LT("#ff9a40", 3))),
    ("stan", 192, 160, stan, J((2, 2))),
    ("ohniste", 96, 96, ohniste, J((1, 1), True, LT("#ffb85c", 4))),
    ("studna", 128, 144, studna, J((2, 1))),
    ("strom_a", 220, 280, strom_a, J((1, 1))),
    ("strom_b", 220, 280, strom_b, J((1, 1))),
    ("smrk", 160, 300, smrk, J((1, 1))),
    ("plot", 128, 80, plot, J((2, 1))),
    ("vuz", 192, 144, vuz, J((3, 1))),
    ("lucerna", 48, 160, lucerna, J((1, 1), True, LT("#ffb85c", 3))),
]


def write_json(names=None):
    path = os.path.join(common.GAME, "data", "props.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = {pid: meta for pid, _, _, _, meta in PROPS}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("wrote", os.path.relpath(path, common.HERE))


DUSK = {"dum_a", "dum_b", "dum_c", "kovarna", "hostinec", "chalupa", "sachta_hora", "sachta_vojtech", "sachta_svornost",
        "chram_barbory", "zvonice", "socha_permonika", "mincovna", "studna", "strom_a", "strom_b", "smrk", "plot", "vuz", "lucerna"}


def dusk(path, tint=(0.80, 0.80, 0.92)):
    """evening light over a town prop; lamp-lit and fire-lit pixels keep their warmth"""
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGBA")).astype(np.float32)
    rgb = im[..., :3] / 255
    warm = np.clip((rgb[..., 0] - rgb[..., 2] - 0.25) * 4, 0, 1) * np.clip((rgb[..., 0] - 0.75) * 5, 0, 1)
    k = np.array(tint, np.float32)
    out = rgb * (k + (1 - k) * warm[..., None])
    im[..., :3] = np.clip(out * 255, 0, 255)
    Image.fromarray(im.astype(np.uint8), "RGBA").save(path)


if __name__ == "__main__":
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    for pid, w, h, fn, meta in PROPS:
        if names and pid not in names: continue
        p = common.render(pid, w, h, fn, "props")
        if pid in DUSK: dusk(p)
    write_json()
