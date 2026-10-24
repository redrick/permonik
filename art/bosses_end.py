"""Kostěj Nesmrtelný and Permoník's true form (permonik_obr)."""
import math
import lib
from bosses_kit import *

ROBE = col("#7a3040"); ROBE_DK = col("#58222e"); ERMINE = col("#d8d4c8")
GAUNT = col("#b3ae9c"); GAUNT_DK = col("#7f7a6a"); BEARD = col("#c2c0b8")
ARMOR = col("#5f6670"); CAPE = col("#4f4060"); GEM = col("#5fd07a")


# ------------------------------------------------------------------ Kostěj Nesmrtelný
def bony_hand(p, ang, s=1.0, grip=False):
    shape(ell(p[0], p[1], 3.4 * s, 2.8 * s, 12, rot=ang), GAUNT, LINE * 0.8)
    for i in range(4):
        a = ang + (i - 1.5) * 14
        j = pt(p, a, 4.5 * s); e = pt(j, a + (-80 if grip else -20), 4 * s)
        tube([p, j, e], 1.6 * s, 1.0 * s, GAUNT, LINE * 0.6, sh=0)


def sword(H, ang, below=10, above=60):
    base = pt(H, ang + 180, below); tip = pt(H, ang, above)
    g0 = pt(H, ang, 4)
    blade_l = pt(g0, ang + 90, 2.2); blade_r = pt(g0, ang - 90, 2.2)
    shape([blade_l, pt(tip, ang + 180, 6), tip, pt(tip, ang + 180, 6), blade_r], IRON_LT, LINE * 0.8)
    shape([blade_l, pt(tip, ang + 180, 6), tip, pt(g0, ang, 2)], col("#c9ced6"), 0)
    stroke([pt(g0, ang, 3), pt(tip, ang + 180, 10)], LINE * 0.5)
    stroke([blade_l, pt(tip, ang + 180, 6), tip, pt(tip, ang + 180, 6), blade_r], LINE * 0.8)
    tube([base, g0], 2.6, 2.6, WOOD_DK, LINE * 0.7, sh=0)
    tube([pt(g0, ang + 90, 8), pt(g0, ang - 90, 8)], 2.6, 2.6, RUST, LINE * 0.7, sh=0)
    shape(ell(*base, 2.6, 2.6, 12), RUST, LINE * 0.7)
    glow(*pt(H, ang, 30), 14, "#9fffb0", 0.18, 6)


def kostej(pose):
    lean = {"idle": 0, "walk": 4, "walk2": 3, "windup": -3, "attack": 6}[pose]
    shadow(0, 34)
    cape = [(-14 + lean, 132)] + bez((-14 + lean, 132), (-34, 110), (-44, 60), (-52 - lean, 10)) + \
        ragged((-52 - lean, 10), (4, 9), 7, 7, 2.2) + bez((4, 9), (2, 50), (6, 100), (14 + lean, 130))
    form(cape, CAPE, sdx=-4, sdy=1, sh=0.2)
    hatch(cape, 2.0, 70, 0.5, g=col("#3a2f48"), alpha=0.5)
    for x0 in (-24, -38):
        stroke(bez((x0 + 12, 120), (x0 + 2, 90), (x0 - 4, 50), (x0 - 8, 14)), LINE * 0.6, g=col("#3a2f48"))
    if pose == "walk":
        fs = (-8, 10); ns = (22, 8)
    elif pose == "walk2":
        fs = (16, 8); ns = (-4, 10)
    elif pose in ("attack", "windup"):
        fs = (-10, 10); ns = (24, 8)
    else:
        fs = (-4, 8); ns = (12, 8)
    for (fx, fy), c_ in ((fs, IRON), (ns, ARMOR)):
        b = [(fx - 6, fy + 10), (fx + 4, fy + 10), (fx + 6, fy + 3), (fx + 16, fy - 1), (fx + 16, fy - 6), (fx - 6, fy - 6)]
        form(b, c_, sh=0.15)
        stroke([(fx - 5, fy + 4), (fx + 5, fy + 4)], LINE * 0.5)
    fsh = (-10 + lean, 120)
    if pose == "attack":
        fe = (2 + lean, 104); fh = (20 + lean, 112)
        glow(fh[0] + 6, fh[1] + 2, 12, "#7dffa0", 0.45)
        for k in range(5):
            stroke(bez(pt(fh, 10 + k * 25, 4), pt(fh, 20 + k * 25, 9), pt(fh, 0 + k * 25, 13), pt(fh, 12 + k * 25, 16)), LINE * 0.6, g=GEM, alpha=0.8)
    elif pose == "windup":
        fe = (-6 + lean, 98); fh = (6 + lean, 108)
        glow(fh[0] + 3, fh[1], 7, "#7dffa0", 0.3)
    elif pose == "walk2":
        fe = (-14 + lean, 96); fh = (-6 + lean, 76)
    else:
        fe = (-20 + lean, 96); fh = (-20 + lean, 74)
    tube([fsh, fe], 7, 6, ROBE_DK); tube([fe, fh], 6, 5, ROBE_DK)
    bony_hand(fh, math.degrees(math.atan2(fh[1] - fe[1], fh[0] - fe[0])), 1.1)
    with T(lean, 0):
        robe = [(-14, 128)] + bez((-14, 128), (-18, 90), (-22, 50), (-26, 14)) + \
            ragged((-26, 14), (24, 13), 6, 4, 0.7) + bez((24, 13), (20, 50), (18, 90), (16, 128))
        form(robe, ROBE, sdx=-4, sdy=1, sh=0.2)
        for x0 in (-14, -4, 8):
            stroke(bez((x0 * 0.6, 100), (x0 * 0.8, 70), (x0, 40), (x0 * 1.2, 16)), LINE * 0.6, g=ROBE_DK)
        hatch(ell(-18, 60, 10, 50, 20), 1.8, 60, 0.45, g=ROBE_DK, alpha=0.7)
        plate = bez((-14, 128), (-16, 110), (-12, 92), (0, 86)) + bez((0, 86), (12, 88), (18, 104), (16, 128))
        form(plate, ARMOR, sdx=-3, sdy=0, sh=0.2)
        for yy in (120, 112, 104, 96):
            stroke(bez((-13, yy), (-4, yy - 3), (8, yy - 3), (16, yy + 1)), LINE * 0.6)
        for (x, y) in ((-8, 116), (8, 116), (-6, 100), (10, 100)):
            dot(x, y, 0.9, RUST_DK)
        hatch(ell(-14, 108, 6, 22, 16), 1.5, 50, 0.4, alpha=0.6)
        belt = [(-20, 88), (18, 88), (18, 82), (-20, 82)]
        form(belt, WOOD_DK, sh=0.15)
        shape(ell(0, 85, 4, 4, 14), GOLD_DK, LINE * 0.7)
        dot(0, 85, 1.6, GEM)
        fur = [(-20, 126)] + [(x, 134 + (3 if i % 2 else -1)) for i, x in enumerate(range(-18, 24, 5))] + [(22, 126), (14, 122), (0, 124), (-12, 122)]
        form(fur, ERMINE, sh=0.15)
        for x in (-12, -2, 9, 17):
            dot(x, 129, 0.9, col("#3a3640"))
        hx, hy = 6, 146
        collar = [(-16, 126), (-26, 150), (-20, 148), (-18, 162), (-10, 150), (-6, 158), (-2, 140), (10, 128)]
        form(collar, CAPE, sdx=-2, sdy=0, sh=0.2)
        stroke([(-14, 130), (-18, 156)], LINE * 0.5, g=col("#3a2f48"))
        tube([(2, 128), (6, 138)], 6, 5, GAUNT, sh=0.2)
        beard = [(hx - 4, hy - 8), (hx + 10, hy - 10)] + bez((hx + 10, hy - 10), (hx + 10, hy - 24), (hx + 6, hy - 36), (hx + 3, hy - 50)) + \
            bez((hx + 3, hy - 50), (hx, hy - 36), (hx - 4, hy - 22), (hx - 4, hy - 8))
        form(beard, BEARD, sdx=-2, sdy=0, sh=0.15)
        for k in range(4):
            stroke(bez((hx + k * 3 - 2, hy - 10), (hx + k * 2.5 - 1, hy - 22), (hx + k * 1.5 + 1, hy - 34), (hx + 3, hy - 48 + k * 3)), LINE * 0.45, g=GAUNT_DK)
        head = bez((hx - 8, hy + 2), (hx - 9, hy + 12), (hx - 4, hy + 16), (hx + 4, hy + 15)) + \
            bez((hx + 4, hy + 15), (hx + 11, hy + 13), (hx + 12, hy + 7), (hx + 12, hy + 3)) + \
            [(hx + 16, hy - 3), (hx + 12, hy - 4), (hx + 10, hy - 8), (hx + 11, hy - 12)] + \
            bez((hx + 11, hy - 12), (hx + 8, hy - 15), (hx + 3, hy - 14), (hx, hy - 10)) + \
            bez((hx, hy - 10), (hx - 5, hy - 8), (hx - 8, hy - 4), (hx - 8, hy + 2))
        form(head, GAUNT, sdx=-2.5, sdy=0, sh=0.22)
        hatch(ell(hx + 4, hy - 4, 4.5, 3.5, 14), 0.9, 60, 0.4, alpha=0.75)
        hatch(ell(hx - 5, hy + 3, 3, 7, 14), 1.0, 60, 0.4, alpha=0.6)
        stroke(bez((hx - 1, hy + 1), (hx + 3, hy - 1), (hx + 7, hy - 1), (hx + 11, hy + 1)), LINE * 0.6)
        teeth = [(hx + 4, hy - 7.5), (hx + 11, hy - 6.5), (hx + 10.5, hy - 10), (hx + 4.5, hy - 10.5)]
        shape(teeth, BONE, LINE * 0.6)
        for i in range(4):
            stroke([(hx + 5.5 + i * 1.5, hy - 7.3), (hx + 5.6 + i * 1.5, hy - 10.4)], LINE * 0.35)
        stroke([(hx + 4.2, hy - 9), (hx + 10.8, hy - 8.3)], LINE * 0.35)
        for ex, r_ in ((hx + 8, 1.5), (hx + 1.5, 1.1)):
            shape(ell(ex, hy + 5, r_ * 2.4, r_ * 2.1, 14), HOLLOW, LINE * 0.5)
            eye(ex, hy + 5, r_, EYE_GREEN, halo=3.6)
        stroke(bez((hx - 1, hy + 9.5), (hx + 3, hy + 8), (hx + 7, hy + 9), (hx + 11.5, hy + 7)), LINE * 0.9)
        band = [(hx - 10, hy + 12), (hx + 13, hy + 13), (hx + 13, hy + 18), (hx - 10, hy + 17)]
        spikes = []
        for i in range(7):
            x = hx + 12 - i * 3.6
            hgt = 34 if i == 3 else 26 if i in (2, 4) else 20
            spikes.append([(x - 2.0, hy + 17), (x - 0.2, hy + hgt), (x + 1.8, hy + 17)])
        for sp in spikes:
            form(sp, IRON, sh=0.15)
            dot(sp[1][0], sp[1][1] - 0.6, 0.6, GOLD)
        form(band, IRON, sdx=-2, sdy=0, sh=0.2)
        for x in (hx - 6, hx + 8):
            dot(x, hy + 15, 0.9, GOLD)
        shape(ell(hx + 1, hy + 15, 1.9, 1.9, 12), GEM, LINE * 0.6)
        glow(hx + 1, hy + 15, 6, "#7dffa0", 0.4, 5)
        for (cx, sx) in ((-14, -1), (16, 1)):
            pd = ell(cx, 124, 10, 7, 20, a0=-20, a1=200) if sx > 0 else ell(cx, 124, 9, 6, 20, a0=-20, a1=200)
            form(pd, ARMOR if sx > 0 else IRON, sh=0.2)
            for k in range(3):
                b0 = (cx - 6 + k * 6, 128 + (2 if k == 1 else 0))
                shape([(b0[0] - 1.6, b0[1]), (b0[0], b0[1] + 7 + (3 if k == 1 else 0)), (b0[0] + 1.6, b0[1])], IRON_LT, LINE * 0.5)
            stroke(ell(cx, 124, 7, 4.5, 14, 10, 170), LINE * 0.5)
    sh0 = (14 + lean, 120)
    if pose == "attack":
        el = (4 + lean, 140); H = (-8 + lean, 156); sa = 25
    elif pose == "walk":
        el = (26 + lean, 98); H = (36 + lean, 84); sa = 60
    elif pose == "walk2":
        el = (18 + lean, 98); H = (20 + lean, 80); sa = 72
    elif pose == "windup":
        el = (2 + lean, 132); H = (-10 + lean, 142); sa = 150
    else:
        el = (24, 96); H = (32, 78); sa = -88
    tube([sh0, el], 8, 7, ROBE); tube([el, H], 7, 5.5, ROBE)
    if pose == "attack":
        sword(H, sa, 10, 64)
    elif pose in ("walk", "walk2", "windup"):
        sword(H, sa, 10, 60)
    else:
        sword(H, sa, 10, 66)
    bony_hand(H, sa, 1.2, grip=True)
    if pose == "attack":
        motion([bez((-10, 168), (24, 182), (56, 170), (72, 140)), bez((-2, 160), (26, 170), (50, 162), (64, 140))])


def kostej_portrait():
    return portrait(kostej, 8, 150, 3.0, "#2f4434")


# ------------------------------------------------------------------ Permoník's true form
CAP_STONE = col("#a6493c"); SMOCK = col("#cfc9b8"); SMOCK_SH = col("#9d9686")


def ore(clip, seeds, n=5):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    for (x, y, a, ln) in seeds:
        p = [(x, y)]
        for k in range(n):
            a += (k % 2 * 2 - 1) * 28
            p.append(pt(p[-1], a, ln / n))
        stroke(p, LINE * 1.8, g=SILVER)
        stroke(p, LINE * 0.5, g=col("#8a95a6"))
        for q in p[1::2]:
            dot(q[0], q[1], 1.1, col("#ffffff"))
    C.restoreState()


def cracks(clip, seeds):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    for (x, y, a, ln) in seeds:
        p = [(x, y), pt((x, y), a, ln * 0.5)]
        p.append(pt(p[-1], a + 30, ln * 0.5))
        stroke(p, LINE * 0.7)
        stroke([p[1], pt(p[1], a - 40, ln * 0.35)], LINE * 0.5)
    C.restoreState()


def rock_seg(p0, p1, w0, w1, colr=None):
    o = tube([p0, p1], w0, w1, colr if colr is not None else ROCK, sh=0.2)
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    cracks(o, [(m[0], m[1], a + 60, w0 * 0.7), (p0[0], p0[1], a + 120, w0 * 0.5)])
    return o


def root(pts, w0, w1):
    tube(pts, w0, w1, ROOT, LINE * 0.7, sh=0.15)


def fist(p, r, raised=False):
    f = ell(p[0], p[1], r, r * 0.85, 22)
    form(f, ROCK_LT, sh=0.2)
    for i in range(3):
        a = (60 if raised else -10) + i * 32
        q = pt(p, a, r * 0.75)
        shape(ell(q[0], q[1], r * 0.32, r * 0.28, 12), ROCK_LT, LINE * 0.7)
        dot(q[0], q[1], r * 0.1, SILVER)
    cracks(f, [(p[0], p[1], 200, r)])


def lamp(x, y, s=1.0):
    glow(x, y, 50 * s, LAMP, 0.45, 12)
    glow(x, y, 22 * s, "#9fd8ff", 0.5, 8)
    with T(x, y, s):
        body = [(-6, -10), (6, -10), (7, 6), (-7, 6)]
        form(body, BRONZE, sh=0.2)
        cage = rrect(-5.5, -6, 11, 11, 2)
        shape(cage, col("#dff4ff"), LINE * 0.7)
        flat(ell(0, -0.5, 2.6, 4.6, 16), "#ffffff")
        flat(ell(0, -0.5, 1.6, 3.2, 16), "#cfeeff")
        for x_ in (-2.5, 2.5):
            stroke([(x_, -6), (x_, 5)], LINE * 0.5)
        shape([(-4, 6), (4, 6), (0, 11)], BRONZE, LINE * 0.7)
        stroke(ell(0, 11, 3, 3, 12, 0, 180), LINE * 0.8)


def shards(base, spec, colr):
    for (a, ln, w) in spec:
        tip = pt(base, a, ln)
        l = pt(base, a + 90, w); r = pt(base, a - 90, w)
        mid = pt(pt(base, a, ln * 0.7), a + 90, w * 0.6)
        sh_ = [l, mid, tip, pt(pt(base, a, ln * 0.6), a - 90, w * 0.7), r]
        form(sh_, colr, sh=0.2)
        stroke([pt(base, a, ln * 0.2), tip], LINE * 0.45, alpha=0.6)


def crystal(base, a, ln, w):
    tip = pt(base, a, ln)
    body = [pt(base, a + 90, w), pt(pt(base, a, ln * 0.75), a + 90, w), tip, pt(pt(base, a, ln * 0.75), a - 90, w), pt(base, a - 90, w)]
    glow(*pt(base, a, ln * 0.6), w * 2.5, "#bfe4ff", 0.25, 5)
    form(body, SILVER, sh=0.25)
    stroke([base, tip], LINE * 0.5, g=col("#8a95a6"))


def obr_head(pose):
    hx, hy = 24, 200
    head = bez((hx - 22, hy - 6), (hx - 26, hy + 12), (hx - 14, hy + 24), (hx + 2, hy + 24)) + \
        bez((hx + 2, hy + 24), (hx + 20, hy + 24), (hx + 28, hy + 12), (hx + 25, hy - 6)) + \
        bez((hx + 25, hy - 6), (hx + 12, hy - 14), (hx - 8, hy - 14), (hx - 22, hy - 6))
    form(head, ROCK_LT, sdx=-4, sdy=1, sh=0.22)
    cracks(head, [(hx - 12, hy + 16, -70, 14)])
    cap = [(hx - 24, hy + 15)] + bez((hx - 24, hy + 15), (hx - 20, hy + 30), (hx - 32, hy + 36), (hx - 48, hy + 30)) + \
        bez((hx - 48, hy + 30), (hx - 32, hy + 42), (hx - 4, hy + 40), (hx + 12, hy + 32)) + \
        bez((hx + 12, hy + 32), (hx + 24, hy + 26), (hx + 28, hy + 20), (hx + 26, hy + 14))
    form(cap, CAP_STONE, sdx=-3, sdy=1, sh=0.2)
    cracks(cap, [(hx - 10, hy + 34, -150, 20), (hx + 8, hy + 28, 200, 14)])
    shape(bez((hx - 26, hy + 13), (hx - 4, hy + 19), (hx + 14, hy + 19), (hx + 27, hy + 13)) + [(hx + 27, hy + 17)] +
          bez((hx + 27, hy + 17), (hx + 14, hy + 23), (hx - 4, hy + 23), (hx - 26, hy + 17)), col("#8a3a30"), LINE * 0.8)
    brow = [(hx - 8, hy + 11), (hx + 24, hy + 9), (hx + 26, hy + 3), (hx - 6, hy + 6)]
    shape(brow, ROCK_DK, LINE * 0.8)
    for ex, r_ in ((hx + 17, 3.4), (hx + 4, 2.8)):
        shape(ell(ex, hy + 2, r_ * 1.5, r_ * 1.1, 14), col("#3a4452"), 0)
        glow(ex, hy + 2, r_ * 4, "#9fd8ff", 0.35, 5)
        eye(ex, hy + 2, r_, EYE_WHITE, halo=3)
    nose = [(hx + 22, hy + 2), (hx + 31, hy - 6), (hx + 23, hy - 9)]
    shape(nose, ROCK_LT, LINE * 0.9)
    mo = pose == "attack"
    if mo:
        shape(ell(hx + 14, hy - 12, 7, 4.5, 16), col("#3a4452"), LINE * 0.8)
        glow(hx + 14, hy - 12, 9, LAMP, 0.45, 5)
    beard = [(hx - 20, hy - 4)] + bez((hx - 20, hy - 4), (hx - 6, hy - 10 - mo * 6), (hx + 12, hy - 10 - mo * 6), (hx + 26, hy - 4)) + \
        [(hx + 26, hy - 18), (hx + 20, hy - 36), (hx + 16, hy - 28), (hx + 10, hy - 54), (hx + 4, hy - 36),
         (hx - 2, hy - 48), (hx - 8, hy - 30), (hx - 14, hy - 40), (hx - 18, hy - 22)]
    if mo:
        beard = [(hx - 20, hy - 4), (hx + 6, hy - 16), (hx + 24, hy - 18), (hx + 26, hy - 20), (hx + 20, hy - 38), (hx + 16, hy - 30), (hx + 10, hy - 56), (hx + 4, hy - 38),
                 (hx - 2, hy - 50), (hx - 8, hy - 32), (hx - 14, hy - 42), (hx - 18, hy - 22)]
    form(beard, ROOT, sdx=-3, sdy=0, sh=0.2)
    for k in range(5):
        x0 = hx - 14 + k * 8
        root(bez((x0, hy - 8), (x0 + 1, hy - 18), (x0 - 2, hy - 28), (x0 + 1, hy - 38 - (k % 2) * 8)), 2.4, 0.6)
    for (x, y) in ((hx + 10, hy - 54), (hx - 2, hy - 48), (hx + 20, hy - 36)):
        shape([(x - 2, y + 4), (x + 2, y + 4), (x, y - 3)], SILVER, LINE * 0.5)


def permonik_obr(pose):
    lean = {"idle": 0, "walk": 6, "walk2": 3, "windup": -4, "attack": 4}[pose]
    if pose == "walk":
        fl = ((-22, 88), (-36, 52), (-46, 18)); nl = ((22, 88), (40, 54), (46, 18))
    elif pose == "walk2":
        fl = ((-22, 88), (-26, 50), (-24, 18)); nl = ((22, 88), (34, 60), (26, 30))
    elif pose in ("attack", "windup"):
        fl = ((-22, 88), (-34, 52), (-42, 18)); nl = ((22, 88), (36, 54), (40, 18))
    else:
        fl = ((-22, 88), (-30, 50), (-32, 18)); nl = ((22, 88), (30, 50), (32, 18))
    for leg, c_ in ((fl, ROCK_DK), (nl, ROCK)):
        rock_seg(leg[0], leg[1], 34, 30, c_)
        rock_seg(leg[1], leg[2], 30, 32, c_)
        x, y = leg[2]
        foot = [(x - 18, y + 4), (x + 18, y + 6), (x + 28, y - 4), (x + 26, y - 10), (x - 20, y - 10)]
        form(foot, c_, sh=0.2)
        for dx in (-14, -2, 12, 22):
            root(bez((x + dx, y - 8), (x + dx * 1.3, y - 9), (x + dx * 1.6 + 6, y - 9), (x + dx * 2 + (8 if dx > 0 else -8), y - 10)), 3.2, 0.8)
    fsh = (-46 + lean, 182)
    if pose in ("attack", "windup"):
        fe = (-74 + lean, 136); fh = (-70 + lean, 80)
    else:
        fe = (-70 + lean, 132); fh = (-66 + lean, 66)
    rock_seg(fsh, fe, 36, 30, ROCK_DK); rock_seg(fe, fh, 30, 26, ROCK_DK)
    root(bez(fsh, (fsh[0] - 18, fsh[1] - 10), (fe[0] - 12, fe[1] + 10), fe), 4, 2)
    fist(fh, 17)
    with T(lean, 0):
        shards((-58, 172), ((150, 34, 7), (165, 26, 6), (135, 22, 5)), ROCK_DK)
        crystal((-56, 184), 125, 30, 4.5)
        tors = bez((-50, 198), (-76, 180), (-66, 130), (-40, 84)) + bez((-40, 84), (-14, 72), (18, 72), (40, 84)) + \
            bez((40, 84), (64, 128), (78, 176), (58, 200)) + bez((58, 200), (30, 216), (-24, 216), (-50, 198))
        form(tors, ROCK, sdx=-8, sdy=3, sh=0.22)
        hatch(ell(-54, 140, 18, 60, 20), 2.4, 60, 0.6, alpha=0.6)
        ore(tors, [(-44, 188, -60, 50), (40, 190, -110, 46), (-26, 100, 20, 40), (46, 112, 150, 34)])
        cracks(tors, [(-16, 206, -100, 30), (56, 150, 200, 30), (-60, 120, -20, 26)])
        for sx in (-1, 1):
            for k in range(3):
                root(bez((sx * 34, 186 - k * 22), (sx * 20, 180 - k * 20), (sx * 18, 168 - k * 20), (sx * 12, 160 - k * 20)), 4.5, 1.2)
        smock = bez((-44, 100), (-20, 94), (20, 94), (46, 100)) + ragged((46, 100), (42, 74), 2, 5, 0.3) + \
            ragged((42, 74), (-44, 74), 8, 9, 1.1) + [(-44, 100)]
        form(smock, SMOCK, sdx=-4, sdy=1, sh=0.18)
        hatch(smock, 2.0, 70, 0.45, g=SMOCK_SH, alpha=0.6)
        root(bez((-44, 94), (-10, 88), (20, 88), (46, 94)), 5, 4)
        cav = bez((-24, 168), (-34, 150), (-30, 122), (-6, 114)) + bez((-6, 114), (18, 120), (22, 150), (12, 168)) + \
            bez((12, 168), (2, 176), (-14, 176), (-24, 168))
        shape(cav, col("#3a4452"), LINE * 1.2)
        lamp(-10, 140, 1.4)
        for k in range(4):
            a0 = 200 + k * 40
            root(bez(pt((-6, 145), a0, 26), pt((-6, 145), a0 + 10, 20), pt((-6, 145), a0 - 6, 16), pt((-6, 145), a0 + 4, 12)), 3.5, 1.2)
        shards((50, 200), ((80, 30, 7), (100, 40, 8), (60, 22, 6)), ROCK_LT)
        crystal((40, 204), 95, 34, 5); crystal((60, 196), 70, 22, 4)
        shards((-40, 206), ((95, 32, 7), (120, 26, 6)), ROCK)
        crystal((-28, 210), 105, 24, 4)
    sh0 = (54 + lean, 178)
    if pose == "attack":
        el = (78 + lean, 206); H = (88 + lean, 236)
        glow(H[0], H[1], 24, LAMP, 0.3, 6)
    elif pose == "walk":
        el = (80 + lean, 132); H = (92 + lean, 72)
    elif pose == "walk2":
        el = (70 + lean, 132); H = (66 + lean, 70)
    elif pose == "windup":
        el = (94 + lean, 150); H = (76 + lean, 196)
    else:
        el = (76, 130); H = (80, 66)
    rock_seg(sh0, el, 38, 32, ROCK); rock_seg(el, H, 32, 28, ROCK)
    root(bez(sh0, (sh0[0] + 16, sh0[1] - 6), (el[0] + 12, el[1] + 8), el), 4.5, 2)
    root(bez(el, (el[0] + 8, el[1] - 10), (H[0] + 10, H[1] + 10), H), 3.5, 1.5)
    crystal(pt(el, 10, 10), 30, 18, 3.5)
    fist(H, 19, raised=pose in ("attack", "windup"))
    with T(lean + 24 * (1 - 1.22), 200 * (1 - 1.22), 1.22):
        obr_head(pose)
    if pose == "attack":
        motion([bez((54, 238), (70, 248), (92, 252), (110, 236)), bez((60, 230), (74, 240), (92, 244), (104, 230))])


def obr_portrait():
    return portrait(permonik_obr, 30, 206, 1.4, "#2a3a4c")


SPRITES = boss_items("kostej", kostej, 352, 0.86) + boss_items("permonik_obr", permonik_obr, 512, 0.92)
PORTRAITS = [("boss_kostej", 256, 256, kostej_portrait()), ("boss_permonik_obr", 256, 256, obr_portrait())]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
