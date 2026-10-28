"""Shared helpers and colours for the boss sprites (bosses_*.py)."""
import math
from reportlab.lib.colors import HexColor
import lib
from lib import Col, ell, bez, rrect, resample
from style3 import (C, T, stroke, shape, form, fill, hatch, tube, cast_shadow, offset_shadow, dot,
                    clip_fill, poly, LINE, notch, bbox)
import common
from common import FEET


def col(hex_, alpha=None):
    c = HexColor(hex_)
    return Col(0.3*c.red + 0.59*c.green + 0.11*c.blue, hex_, alpha)


BONE = col("#d9cfb2"); BONE_SH = col("#a99c7c"); BONE_DK = col("#7d715a")
SHEET = col("#d7d6cf"); SHEET_SH = col("#9fa4ad")
HAG = col("#a9b39b"); HAG_DK = col("#7d8873")
HAIR_GREY = col("#b9b6ae"); HAIR_DK = col("#5b5660")
CLOTH_VIOLET = col("#6a4f78"); CLOTH_PLUM = col("#7b3f55"); CLOTH_SLATE = col("#5f6b78")
RAG = col("#8a8070"); RAG_DK = col("#5e564b")
IRON = col("#6f747c"); IRON_LT = col("#9aa0a8"); RUST = col("#9a5c3a"); RUST_DK = col("#6e3e28")
BRONZE = col("#b08540"); GOLD = col("#e0b444"); GOLD_DK = col("#a07a26")
WOOD = col("#8a6240"); WOOD_DK = col("#5f4129"); WOOD_LT = col("#a87f55")
FROG = col("#7fa46a"); FROG_DK = col("#58784a"); FROG_BELLY = col("#c4cf98")
COAT_GREEN = col("#3f7a55"); COAT_GREEN_DK = col("#2c5a3e")
HAT_RED = col("#b8383c"); RED_DK = col("#7d2428")
WATER = col("#7fb3c9"); WATER_LT = col("#c3e2ee")
FUR_DEVIL = col("#6a4436"); FUR_DEVIL_DK = col("#4a2e25"); HORN = col("#cdbf9e")
SKIN_RED = col("#b0574a")
EARTH = col("#7a6049"); EARTH_DK = col("#574333"); EARTH_LT = col("#957a5e")
ROCK = col("#857f78"); ROCK_DK = col("#5f5a55"); ROCK_LT = col("#a39d94")
SILVER = col("#d3d9e2"); ROOT = col("#7c5b3e"); MOSS = col("#6f8445")
SCALE_OLIVE = col("#7c8a62"); SCALE_DK = col("#56613f")
COMB_RED = col("#c4373a"); BEAK = col("#d6a840")
DRAGON = col("#6f6a5e"); DRAGON_DK = col("#4d493f"); DRAGON_BELLY = col("#b9a57c")
D_RED = col("#b5442f"); D_BLUE = col("#4f7cb4"); D_GREEN = col("#5d9440")
CHICKEN = col("#d39a3e"); CHICKEN_DK = col("#a06a24")
THATCH = col("#a88d55"); THATCH_DK = col("#7a6537")
MOUTH_DK = col("#3a2a2e"); HOLLOW = col("#2f2b33")
WHITE = col("#f4f1e6")

EYE_YELLOW = "#ffe35a"; EYE_GREEN = "#9dff6a"; EYE_RED = "#ff4a2a"; EYE_BLUE = "#9fe3ff"
EYE_ORANGE = "#ffa030"; EYE_WHITE = "#f4fbff"; EYE_VIOLET = "#d58aff"
FIRE = "#ff8a2a"; EMBER = "#ffd24a"; FROST = "#a8e4ff"; POISON = "#9ee05a"; LAMP = "#e4f6ff"


def glow(x, y, r, hex_, a=0.5, n=8):
    """soft light: stacked translucent discs"""
    a0 = 1 - (1 - a) ** (1.0 / n)
    C.saveState(); C.setFillColor(HexColor(hex_)); C.setFillAlpha(a0)
    for i in range(n):
        C.circle(x, y, r * (1 - i / n) + 0.3, fill=1, stroke=0)
    C.restoreState()


def glow_ell(x, y, rx, ry, hex_, a=0.5, n=8, rot=0):
    a0 = 1 - (1 - a) ** (1.0 / n)
    C.saveState(); C.setFillColor(HexColor(hex_)); C.setFillAlpha(a0)
    for i in range(n):
        k = 1 - i / n
        C.drawPath(poly(ell(x, y, rx * k + 0.3, ry * k + 0.3, 30, rot=rot)), fill=1, stroke=0)
    C.restoreState()


def flat(pts, hex_, a=1.0):
    C.saveState(); C.setFillColor(HexColor(hex_)); C.setFillAlpha(a)
    C.drawPath(poly(pts), fill=1, stroke=0); C.restoreState()


def eye(x, y, r, hex_, slit=False, rot=0, halo=3.2):
    glow(x, y, r * halo, hex_, 0.55)
    e = ell(x, y, r, r * 0.72, 20, rot=rot)
    flat(e, hex_)
    flat(ell(x, y, r * 0.55, r * 0.4, 14, rot=rot), "#fffbe8", 0.85)
    if slit:
        flat(ell(x, y, r * 0.16, r * 0.62, 10, rot=rot), "#2a1a12")
    stroke(e, LINE * 0.7, closed=True)


def pt(p, a, d):
    return (p[0] + math.cos(math.radians(a)) * d, p[1] + math.sin(math.radians(a)) * d)


def limb(p0, a1, l1, a2, l2, w0, w1, w2, colr, sh=0.12):
    """two-segment limb from p0; returns (joint, end, angle of second segment)"""
    j = pt(p0, a1, l1); e = pt(j, a2, l2)
    tube([p0, j], w0, w1, colr, sh=sh)
    tube([j, e], w1, w2, colr, sh=sh)
    return j, e, a2


def claws(p, ang, n=4, ln=7, w=1.6, spread=16, colr=None, curl=-25):
    """long hooked claw-fingers fanned around ang"""
    colr = colr if colr is not None else BONE
    for i in range(n):
        a = ang + (i - (n - 1) / 2) * spread / max(1, n - 1) * 2
        p1 = pt(p, a, ln * 0.55); p2 = pt(p1, a + curl, ln * 0.5)
        tube([p, p1, p2], w, w * 0.35, colr, LINE * 0.7, cap=True, sh=0)


def ragged(p0, p1, n=8, depth=4, seed=0):
    """zig-zag torn hem from p0 to p1 (points include ends); depth hangs below the line"""
    out = [p0]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
    nx, ny = dy / L, -dx / L
    for i in range(1, 2 * n):
        t = i / (2 * n)
        d = depth * (1.0 + 0.45 * math.sin(i * 2.3 + seed)) if i % 2 else depth * 0.15
        out.append((p0[0] + dx * t + nx * d, p0[1] + dy * t + ny * d))
    out.append(p1)
    return out


def drips(pts, hex_=None, ln=4):
    for (x, y) in pts:
        tube([(x, y), (x, y - ln)], 1.3, 0.5, hex_ or WATER, LINE * 0.5, sh=0)
        shape(ell(x, y - ln - 1.0, 0.9, 1.3, 10), hex_ or WATER, LINE * 0.5)


def streaks(pts_list, w=0.5, g=None, alpha=0.6):
    for pts in pts_list:
        stroke(pts, LINE * w, g=g if g is not None else 0.0, alpha=alpha)


def shadow(x, rx):
    cast_shadow(x, 0, rx, min(3.0, rx * 0.12))


def scales(clip, x0, y0, x1, y1, r=3.0, g=None, alpha=0.5):
    """overlapping scale arcs clipped inside clip"""
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    yy = y0; row = 0
    while yy < y1:
        xx = x0 + (r if row % 2 else 0)
        while xx < x1:
            stroke(ell(xx, yy, r, r * 0.8, 10, 200, 340), LINE * 0.45, g=g if g is not None else 0.0, alpha=alpha)
            xx += 2 * r
        yy += r * 1.1; row += 1
    C.restoreState()


def motion(pts_list, alpha=0.55):
    for pts in pts_list:
        stroke(pts, LINE * 0.6, alpha=alpha)


def bone(p0, p1, w, colr=None, lw=LINE * 0.8):
    colr = colr if colr is not None else BONE
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    for p in (p0, p1):
        for s in (-1, 1):
            q = pt(p, a + 90 * s, w * 0.42)
            shape(ell(q[0], q[1], w * 0.55, w * 0.55, 12), colr, lw)
    tube([p0, p1], w * 0.75, w * 0.65, colr, lw, cap=False, sh=0.1)


def skull(x, y, r, colr=None, eyes=None, jaw_open=0.0, side=0.0, lw=LINE * 0.8, sockets=HOLLOW):
    """small skull, roughly frontal; side shifts features toward +x for a 3/4 view"""
    colr = colr if colr is not None else BONE
    ox = side * r * 0.25
    jaw = [(x - r * 0.5 + ox, y - r * 0.55), (x + r * 0.55 + ox, y - r * 0.55),
           (x + r * 0.45 + ox, y - r * (1.05 + jaw_open)), (x - r * 0.4 + ox, y - r * (1.05 + jaw_open))]
    shape(jaw, colr, lw)
    cr = ell(x, y, r, r * 0.92, 24)
    shape(cr + [(x + r * 0.6 + ox, y - r * 0.75), (x - r * 0.55 + ox, y - r * 0.75)], colr, lw)
    for s in (-1, 1):
        ex, ey = x + ox + s * r * 0.38, y - r * 0.18
        shape(ell(ex, ey, r * 0.27, r * 0.3, 12), sockets, 0)
        if eyes: glow(ex, ey, r * 0.42, eyes, 0.5, 5); dot(ex, ey, r * 0.11, col(eyes)); dot(ex, ey, r * 0.05, col("#fff6d8"))
    shape([(x + ox, y - r * 0.4), (x - r * 0.1 + ox, y - r * 0.62), (x + r * 0.1 + ox, y - r * 0.62)], sockets, 0)
    for i in range(4):
        tx = x + ox - r * 0.3 + i * r * 0.2
        stroke([(tx, y - r * 0.68), (tx, y - r * 0.86)], lw * 0.6)
    stroke([(x - r * 0.42 + ox, y - r * 0.77), (x + r * 0.48 + ox, y - r * 0.77)], lw * 0.6)


# ------------------------------------------------------------------ rendering glue
def sprite(fn, pose, s=1.0):
    def draw(b):
        with T(b.w / 2, FEET, s):
            fn(pose)
    return draw


def portrait(fn, hx, hy, zoom, tint="#3a3040", pose="idle", cx=64, cy=60):
    """256x256 close-up: vignette, figure placed so local (hx, hy) lands at (cx, cy)"""
    def draw(b):
        W, H = b.w, b.h
        C.saveState()
        C.setFillColor(HexColor("#16131a")); C.rect(0, 0, W, H, fill=1, stroke=0)
        p = C.beginPath(); p.rect(0, 0, W, H); C.clipPath(p, stroke=0, fill=0)
        C.radialGradient(W / 2, H * 0.55, W * 0.62, [HexColor(tint), HexColor("#16131a")], extend=True)
        C.restoreState()
        C.saveState(); p = C.beginPath(); p.rect(0, 0, W, H); C.clipPath(p, stroke=0, fill=0)
        with T(cx - hx * zoom, cy - hy * zoom, zoom):
            fn(pose)
        for i in range(10):
            r = W * (0.78 - i * 0.026)
            q = C.beginPath(); q.rect(-10, -10, W + 20, H + 20)
            for k, (x, y) in enumerate(ell(W / 2, H / 2, r, r, 48)):
                (q.moveTo if k == 0 else q.lineTo)(x, y)
            q.close()
            C.setFillColor(HexColor("#0e0c11")); C.setFillAlpha(0.09)
            C.drawPath(q, fill=1, stroke=0, fillMode=0)
        C.restoreState()
    return draw


def boss_items(name, fn, px, s=1.0, extra=()):
    from bestiary_kit import poses_of
    out = [(f"{name}_{p}", px, px, sprite(fn, p, s)) for p in poses_of(fn)]
    out += [(f"{name}_{p}", px, px, sprite(fn, p, s)) for p in extra]
    return out
