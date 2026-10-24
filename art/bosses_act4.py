"""Act IV bosses: Saň Tříhlavá, Vij."""
import math
from bosses_kit import *

WING = col("#7d5654"); WING_DK = col("#5e4241")
D_RED_DK = col("#7e2d22"); D_BLUE_DK = col("#35567f"); D_GREEN_DK = col("#3d6a2a")
ICE = col("#d4f0ff"); SLIME = col("#a6dd5a")
HEADS = {
    "fire": (D_RED, D_RED_DK, EYE_YELLOW, FIRE),
    "frost": (D_BLUE, D_BLUE_DK, EYE_WHITE, FROST),
    "poison": (D_GREEN, D_GREEN_DK, "#eaff5a", POISON),
}


# ------------------------------------------------------------------ Saň
def breath(kind, x, y, ln):
    if kind == "fire":
        glow_ell(x + ln * 0.5, y, ln * 0.65, ln * 0.3, FIRE, 0.6)
        for i, (dy, k) in enumerate(((0, 1.0), (4, 0.75), (-4, 0.8), (1.5, 0.55))):
            tip = (x + ln * k, y + dy * 1.6)
            fl = bez((x, y + 1.5), (x + ln * 0.3, y + 5 + dy), (tip[0] - 6, tip[1] + 3), tip) + \
                bez(tip, (tip[0] - 6, tip[1] - 3), (x + ln * 0.3, y - 5 + dy), (x, y - 1.5))
            flat(fl, FIRE if i % 2 == 0 else EMBER, 0.85)
        flat(ell(x + ln * 0.25, y, ln * 0.25, 2.2, 14), "#fff3c0", 0.9)
    elif kind == "frost":
        glow_ell(x + ln * 0.5, y, ln * 0.65, ln * 0.3, FROST, 0.65)
        for k in range(7):
            a = -22 + k * 7.3
            p0 = pt((x, y), a, 3); p1 = pt((x, y), a, ln * (0.6 + 0.4 * ((k * 37) % 5) / 5))
            stroke([p0, p1], LINE * 0.8, g=ICE)
        for (dx, dy, r) in ((ln * 0.6, 3, 2.2), (ln * 0.85, -4, 1.8), (ln * 0.4, -3, 1.6), (ln, 2, 1.4)):
            shape([(x + dx, y + dy + r * 1.6), (x + dx + r, y + dy), (x + dx, y + dy - r * 1.6), (x + dx - r, y + dy)], ICE, LINE * 0.5)
    else:
        glow_ell(x + ln * 0.5, y, ln * 0.6, ln * 0.32, POISON, 0.55)
        for (dx, dy, r) in ((ln * 0.3, 0, 4), (ln * 0.55, 3, 5), (ln * 0.8, -2, 5.5), (ln * 0.6, -5, 3.5)):
            flat(ell(x + dx, y + dy, r, r * 0.8, 16), "#8fc34a", 0.55)
            stroke(ell(x + dx, y + dy, r, r * 0.8, 16, 30, 200), LINE * 0.5, alpha=0.5)
        for (dx, dy) in ((ln * 0.4, -6), (ln * 0.7, -8)):
            shape(ell(x + dx, y + dy, 1.0, 1.4, 10), SLIME, LINE * 0.4)


def dhead(x, y, s, kind, rot=0, gape=10, breathe=0):
    c, dk, eyec, mouthc = HEADS[kind]
    with T(x, y, s, rot=rot):
        if kind == "frost":
            for (bx, by, a, l) in ((-2, 9, 120, 12), (4, 11, 105, 10), (10, 10, 95, 8)):
                tip = pt((bx, by), a, l)
                shape([(bx - 2, by), tip, (bx + 2.5, by)], ICE, LINE * 0.6)
        for (bx, by, l, cv) in ((2, 8, 18, 8), (6, 8, 13, 5)) if kind != "frost" else ((2, 8, 12, 5),):
            horn = bez((bx - 2, by), (bx - l * 0.5, by + cv), (bx - l, by + cv * 1.3), (bx - l - 3, by + cv * 1.8)) + \
                bez((bx - l - 3, by + cv * 1.8), (bx - l * 0.6, by + cv * 0.6), (bx - l * 0.3, by - 1), (bx + 2, by - 1))
            form(horn, HORN, sdx=-1, sdy=1, sh=0.2)
        for i in range(4):
            fx = -6 - i * 1.5; fy = 4 - i * 4
            shape([(fx + 3, fy + 2), (fx - 7, fy - 1), (fx + 2, fy - 3)], dk, LINE * 0.6)
        hinge = (4, -2)
        jaw0 = [(2, -2), (26, -3), (29, -5), (25, -8), (10, -9), (1, -6)]
        ca, sa = math.cos(math.radians(-gape)), math.sin(math.radians(-gape))
        jaw = [(hinge[0] + (px - hinge[0]) * ca - (py - hinge[1]) * sa, hinge[1] + (px - hinge[0]) * sa + (py - hinge[1]) * ca) for px, py in jaw0]
        tip_u = (31, -1); tip_l = jaw[2]
        inner = [hinge, tip_u, (tip_l[0] + 1, tip_l[1] + 2)]
        shape(inner, MOUTH_DK, LINE * 0.6)
        glow((hinge[0] + tip_u[0]) / 2 + 4, (tip_u[1] + tip_l[1]) / 2, 8 + gape * 0.3, mouthc, 0.6)
        shape(jaw, c, LINE * 0.9)
        offset_shadow(jaw, 0, 1.5, 0.22)
        for k in range(5):
            tx = 9 + k * 4
            ty = hinge[1] + (tx - hinge[0]) * math.tan(math.radians(-gape)) - 0.5
            shape([(tx - 0.8, ty), (tx + 0.8, ty), (tx, ty + 2.4)], WHITE, LINE * 0.35)
        if kind == "poison":
            drips([(jaw[3][0], jaw[3][1]), (jaw[4][0] + 3, jaw[4][1])], SLIME, 5)
        up = [(-4, 8), (2, 11), (10, 12), (17, 9), (26, 5), (31, 2), (33, 0), (31, -1.5), (16, -1.5), (4, -3), (-5, -3)]
        form(up, c, sdx=-1, sdy=-2, sh=0.18)
        hatch(ell(4, 2, 9, 6, 16), 1.6, 50, 0.4, g=dk, alpha=0.6)
        for k in range(5):
            tx = 12 + k * 4
            shape([(tx - 0.8, -1.5), (tx + 0.8, -1.5), (tx, -4.3)], WHITE, LINE * 0.35)
        stroke(bez((11, 10.5), (15, 12), (19, 10), (22, 7)), LINE * 1.1)
        eye(16, 7.2, 2.2, eyec, slit=True, rot=-8, halo=2.6)
        dot(29, 1.6, 0.8, MOUTH_DK)
        for (sx, sy) in ((6, 5), (9, 2), (22, 3), (25, 1), (12, 4)):
            stroke(ell(sx, sy, 1.4, 1.0, 8, 200, 340), LINE * 0.45, alpha=0.6)
        if breathe:
            breath(kind, 32, -2 - gape * 0.2, breathe)


def neck(p0, p1, p2, p3, w0, w1, c, dk):
    o = tube(bez(p0, p1, p2, p3, 20), w0, w1, c, sh=0.16)
    C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
    x0, y0, x1, y1 = bbox(o)
    scales(o, x0, y0, x1, y1, 2.6, g=dk, alpha=0.55)
    C.restoreState()
    P = bez(p0, p1, p2, p3, 10)
    for i in range(1, 9):
        a, b_ = P[i - 1], P[i + 1]
        ang = math.degrees(math.atan2(b_[1] - a[1], b_[0] - a[0])) + 90
        w = w0 + (w1 - w0) * i / 10
        base = pt(P[i], ang, w * 0.42)
        shape([pt(base, ang - 90, 2.2), pt(base, ang + 20, 5.5), pt(base, ang + 90, 2.2)], dk, LINE * 0.5)


def dwing(S, E, W, tips, rest, c):
    mem = [S, E, W]
    for i, t in enumerate(tips):
        prev = W if i == 0 else tips[i - 1]
        mid = ((prev[0] + t[0]) / 2, (prev[1] + t[1]) / 2)
        if i > 0:
            cx, cy = (mid[0] * 0.75 + W[0] * 0.25), (mid[1] * 0.75 + W[1] * 0.25)
            mem += bez(prev, (cx, cy), (cx, cy), t, 8)
        else:
            mem.append(t)
    mid = ((tips[-1][0] + rest[0]) / 2, (tips[-1][1] + rest[1]) / 2)
    mem += bez(tips[-1], (mid[0] * 0.8 + W[0] * 0.2, mid[1] * 0.8 + W[1] * 0.2), (mid[0], mid[1]), rest, 8) + [S]
    form(mem, c, sdx=-3, sdy=3, sh=0.15)
    hatch(mem, 2.6, 75, 0.4, g=WING_DK, alpha=0.4)
    tube([S, E], 6, 5, DRAGON, LINE * 0.9, sh=0.1)
    tube([E, W], 5, 4, DRAGON, LINE * 0.9, sh=0.1)
    for t in tips:
        tube([W, t], 2.6, 1.0, DRAGON, LINE * 0.6, sh=0)
    shape([pt(W, 80, 2), pt(W, 100, 8), pt(W, 140, 2)], HORN, LINE * 0.6)


def dleg(hip, knee, ankle, foot, w, c):
    tube([hip, knee], w, w * 0.7, c, sh=0.15)
    tube([knee, ankle], w * 0.7, w * 0.5, c, sh=0.15)
    tube([ankle, foot], w * 0.5, w * 0.45, c, sh=0.1)
    claws(foot, 0, 3, 6, 1.8, 12, HORN, curl=-50)


def san(pose):
    st = {"idle": 0, "walk": 1, "attack": 2, "portrait": 0, "walk2": 4, "windup": 5}[pose]
    shadow(-12, 92)
    wv = {2: (0, 6), 4: (0, 10), 5: (-4, 16)}.get(st, (0, 0))
    dwing((-2, 122), (-8 + wv[0], 182 + wv[1]), (-24, 222 + wv[1]),
          [(-62, 246 + wv[1] * 0.3), (-84, 222 + wv[1]), (-86, 190), (-66, 158)], (-28, 128), WING_DK)
    lf = {1: [(-46, 12), (8, 8)], 4: [(-70, 6), (34, 6)], 5: [(-64, 6), (18, 6)]}.get(st, [(-60, 10), (24, 6)])
    dleg((-52, 60), (-36, 40), (-48, 14), (lf[0][0], 6), 24, DRAGON_DK)
    dleg((18, 70), (24, 42), (18, 14), (lf[1][0], 6), 20, DRAGON_DK)
    tail = bez((-72, 72), (-108, 70), (-122, 44), (-106, 20), 24)
    o = tube(tail, 30, 5, DRAGON, sh=0.16)
    scales(o, -140, 10, -60, 80, 3.2, g=DRAGON_DK, alpha=0.45)
    tp = tail[-1]
    shape([pt(tp, 0, 3), pt(tp, -20, 9), pt(tp, -60, 12), pt(tp, -100, 9), pt(tp, -120, 3)], DRAGON_DK, LINE * 0.8)
    for i in range(2, len(tail) - 3, 3):
        p = tail[i]; q = tail[i + 1]
        ang = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) + 90
        w = 30 + (5 - 30) * i / len(tail)
        base = pt(p, ang, w * 0.4)
        shape([pt(base, ang - 90, 2.5), pt(base, ang + 25, 6), pt(base, ang + 90, 2.5)], DRAGON_DK, LINE * 0.5)
    body = bez((-74, 92), (-50, 118), (-10, 124), (22, 118)) + bez((22, 118), (44, 112), (56, 96), (50, 72)) + \
        bez((50, 72), (44, 50), (14, 40), (-20, 40)) + bez((-20, 40), (-56, 40), (-86, 50), (-86, 72)) + \
        bez((-86, 72), (-86, 82), (-80, 88), (-74, 92))
    form(body, DRAGON, sdx=-6, sdy=4, sh=0.14)
    C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
    scales(body, -90, 60, 60, 126, 4.0, g=DRAGON_DK, alpha=0.5)
    bel = bez((-80, 58), (-50, 60), (0, 56), (54, 80)) + [(60, 30), (-90, 30)]
    fill(bel, DRAGON_BELLY)
    for k in range(9):
        x = -72 + k * 15
        stroke(bez((x, 58 - abs(x) * 0.02), (x + 2, 52), (x + 2, 46), (x, 38)), LINE * 0.6, alpha=0.7)
    hatch(ell(-30, 40, 60, 12, 20), 1.8, 40, 0.45, alpha=0.6)
    C.restoreState()
    stroke(bez((-80, 58), (-50, 60), (0, 56), (50, 76)), LINE * 0.8)
    for i, x in enumerate(range(-72, 20, 12)):
        y = 92 + 26 * math.sin(math.pi * (x + 74) / 96) * 0.95
        shape([(x - 4, y - 2), (x + 1, y + 9 + (i % 2) * 3), (x + 5, y - 2)], DRAGON_DK, LINE * 0.6)
    lf2 = {1: [(-64, 6), (56, 8)], 4: [(-32, 6), (30, 6)], 5: [(-44, 6), (36, 4)]}.get(st, [(-40, 6), (44, 4)])
    dleg((-46, 66), (-28, 44), (-36, 14), (lf2[0][0], 6), 28, DRAGON)
    dleg((32, 76), (44, 48), (36, 16), (lf2[1][0], 6), 24, DRAGON)
    if st == 2:
        hp = {"poison": ((78, 66), -22), "frost": ((80, 132), -10), "fire": ((68, 192), -20)}
    elif pose == "portrait":
        hp = {"poison": ((60, 136), -12), "frost": ((76, 160), 2), "fire": ((52, 186), 10)}
    elif st == 5:
        hp = {"poison": ((58, 106), 16), "frost": ((60, 164), 24), "fire": ((34, 212), 32)}
    elif st == 4:
        hp = {"poison": ((74, 100), -4), "frost": ((76, 156), 8), "fire": ((50, 206), 14)}
    elif st == 1:
        hp = {"poison": ((78, 90), -12), "frost": ((80, 146), -2), "fire": ((58, 196), 4)}
    else:
        hp = {"poison": ((72, 96), -8), "frost": ((74, 152), 4), "fire": ((48, 202), 12)}
    bases = {"fire": (2, 112), "frost": (24, 110), "poison": (38, 96)}
    for kind in ("fire", "frost", "poison"):
        c, dk, _, _ = HEADS[kind]
        b0 = bases[kind]; (hx, hy), r = hp[kind]
        neck(b0, (b0[0] + 10, b0[1] + (hy - b0[1]) * 0.7), (hx - 22, hy - 4), (hx, hy), 26, 14, c, dk)
    for kind in ("fire", "frost", "poison"):
        (hx, hy), r = hp[kind]
        gape = {0: 8, 1: 12, 2: 30, 4: 10, 5: 18}[st] + (14 if pose == "portrait" else 0)
        dhead(hx - 14, hy, 1.35, kind, rot=r, gape=gape, breathe=18 if st == 2 else 0)


def san_head_sprite(b):
    with T(b.w / 2 + 2, b.h / 2 + 4, 1.15):
        stump = [(-22, -14), (-10, -12)]
        o = tube(bez((-24, -16), (-16, -12), (-8, -6), (0, 0)), 18, 14, D_RED, sh=0.16)
        scales(o, -34, -26, 4, 10, 2.4, g=D_RED_DK, alpha=0.5)
        cap = ell(-24, -16, 5, 9, 20, rot=-35)
        shape(cap, D_RED_DK, LINE * 0.9)
        glow(-24, -16, 9, EMBER, 0.55)
        flat(ell(-24, -16, 3, 6, 16, rot=-35), "#ffb040", 0.9)
        dhead(-2, 0, 1.0, "fire", rot=8, gape=18)


# ------------------------------------------------------------------ Vij
LID = col("#94725c"); LID_DK = col("#6e5444"); VIJ_EARTH = col("#6a5241")


def lid_down(top, foot, w0, sway, pool):
    tx, ty = top; bx = foot
    mid = (tx + (bx - tx) * 0.45 + sway, ty - (ty - 10) * 0.45)
    L = bez((tx - w0 / 2, ty + 2), (tx - w0 / 2 - 2, ty - 20), (mid[0] - 11, mid[1] + 10), (mid[0] - 10, mid[1])) + \
        bez((mid[0] - 10, mid[1]), (mid[0] - 12, mid[1] - 34), (bx - 16, 34), (bx - 26, 3))
    P = [(bx + pool, 2)] + bez((bx + pool, 2), (bx + pool + 6, 3), (bx + pool + 6, 10), (bx + pool - 2, 10))
    R = bez((bx + 16, 10), (bx + 10, 36), (mid[0] + 10, mid[1] - 30), (mid[0] + 10, mid[1])) + \
        bez((mid[0] + 10, mid[1]), (mid[0] + 11, mid[1] + 10), (tx + w0 / 2 + 2, ty - 20), (tx + w0 / 2, ty + 2))
    top_ = bez((tx + w0 / 2, ty + 2), (tx + w0 / 3, ty + 10), (tx - w0 / 3, ty + 10), (tx - w0 / 2, ty + 2), 8)
    lid = L + P + R + top_
    form(lid, LID, sdx=-3, sdy=0, sh=0.22)
    C.saveState(); C.clipPath(poly(lid), stroke=0, fill=0)
    flat(ell(bx - 12, ty * 0.5, 6, ty * 0.6, 16), LID_DK.hex, 0.45)
    y = ty - 5; k = 0
    while y > 14:
        t = (ty - y) / (ty - 10)
        cx = tx + (bx - tx) * t + sway * math.sin(math.pi * t)
        w = w0 * (1 - t) + 22 * t if t < 0.45 else 22 + (t - 0.45) * 30
        bow = 2 + (k % 3)
        stroke(bez((cx - w / 2, y + 1), (cx - w / 5, y - bow), (cx + w / 5, y - bow), (cx + w / 2, y + 1)), LINE * 0.55, g=LID_DK)
        y -= 8 + (k * 7) % 6; k += 1
    stroke(bez((bx - 8, 9), (bx, 12), (bx + pool * 0.5, 10), (bx + pool, 8)), LINE * 0.55, g=LID_DK)

    C.restoreState()
    for k in range(6):
        x = bx + pool + 3 - k * 1.2; y = 3 + k * 1.3
        stroke([(x, y), (x + 6, y + 1.5 - k * 0.6)], LINE * 0.8)


def vij(pose):
    st = {"idle": 0, "walk": 1, "attack": 2, "open": 3, "walk2": 4, "windup": 5}[pose]
    shadow(-6, 100)
    for (x0, a, l) in ((-42, 188, 22), (-30, 196, 16), (-58, 172, 20), (36, 352, 18), (24, 344, 14)):
        x0 += (8 if st == 1 and x0 > 0 else -8 if st == 4 and x0 < 0 else 0)
        tube([(x0, 9), pt((x0, 9), a, l * 0.6), pt(pt((x0, 9), a, l * 0.6), a + (-8 if a < 270 else 8), l * 0.5)], 6, 1.2, ROOT, LINE * 0.6, sh=0)
    tube([(-62, 150), (-98, 104), (-104, 26)], 26, 18, EARTH_DK, sh=0.18)
    for a in (190, 220, 250, 280, 310):
        tube([(-104, 24), pt((-104, 24), a, 11), pt(pt((-104, 24), a, 11), a + 30, 7)], 6, 1.2, ROOT, LINE * 0.6, sh=0)
    fl = {1: 8, 4: -6, 5: 3}.get(st, 0)
    tube([(-40, 50), (-46 - fl, 20)], 34, 32, EARTH_DK, sh=0.15)
    tube([(28, 50), (34 + fl, 20)], 36, 34, VIJ_EARTH, sh=0.15)
    body = bez((-82, 44), (-104, 80), (-100, 130), (-74, 160)) + bez((-74, 160), (-56, 186), (-20, 200), (8, 194)) + \
        bez((8, 194), (30, 190), (48, 176), (60, 150)) + bez((60, 150), (78, 126), (84, 90), (72, 58)) + \
        bez((72, 58), (60, 36), (-60, 34), (-82, 44))
    body = notch(body, 2.6, 6)
    form(body, VIJ_EARTH, sdx=-8, sdy=4, sh=0.16)
    C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
    hatch(ell(-84, 100, 30, 80, 20), 2.0, 60, 0.5, g=EARTH_DK, alpha=0.8)
    hatch(ell(0, 40, 90, 16, 20), 2.0, 30, 0.5, g=EARTH_DK, alpha=0.8)
    for (x, y, rx, ry) in ((-60, 112, 6, 4), (-30, 70, 5, 3.5), (-78, 62, 4, 3), (-24, 152, 5, 3), (54, 84, 4, 3), (-46, 170, 3.5, 2.5), (-4, 104, 4, 3)):
        form(ell(x, y, rx, ry, 14, rot=x), ROCK, LINE * 0.7, sdx=-1, sdy=1, sh=0.2)
    for (x, y, rx, ry) in ((-42, 182, 18, 6), (-90, 90, 6, 20), (14, 62, 14, 5)):
        flat(ell(x, y, rx, ry, 20), MOSS.hex, 0.7)
        for k in range(6):
            stroke([(x - rx + k * rx / 3, y), (x - rx + k * rx / 3 + 1, y + 3)], LINE * 0.4, g=MOSS)
    for pts in (bez((-96, 80), (-60, 100), (-40, 90), (-10, 124)), bez((-64, 176), (-40, 150), (-30, 120), (-54, 90)),
                bez((-20, 40), (-10, 70), (20, 80), (44, 112)), bez((-30, 196), (-10, 170), (10, 160), (30, 172))):
        tube(pts, 4.5, 2, ROOT, LINE * 0.6, sh=0)
    C.restoreState()
    for (x, y) in ((-74, 162), (-46, 190), (-16, 199), (8, 196)):
        tube([(x, y - 3), (x - 3, y + 7), (x - 9, y + 10)], 3.2, 1, ROOT, LINE * 0.5, sh=0)
    for x in (-70, -50, -10, 40, 60):
        tube([(x, 40), (x - 2, 28), (x + 2, 20)], 3, 0.8, ROOT, LINE * 0.5, sh=0)
    s0 = (64, 128)
    if st == 2:
        e0, h0, ha = (100, 168), (86, 206), 100
    elif st == 5:
        e0, h0, ha = (114, 98), (118, 160), 70
    elif st == 4:
        e0, h0, ha = (94, 102), (86, 22), -100
    elif st == 1:
        e0, h0, ha = (98, 100), (106, 22), -80
    else:
        e0, h0, ha = (96, 100), (98, 16), -90
    tube([s0, e0], 28, 20, VIJ_EARTH, sh=0.16)
    tube([e0, h0], 20, 15, VIJ_EARTH, sh=0.16)
    for k in range(3):
        stroke(bez(pt(s0, -30, 4 + k * 6), pt(e0, 120, 10 - k * 4), pt(e0, -60, 4), pt(h0, 90 + ha, 4 + k)), LINE * 0.6, g=ROOT, alpha=0.9)
    for (q, a) in ((pt(s0, -60, 10), -100), (pt(e0, -90, 8), -80)):
        tube([q, pt(q, a, 8), pt(pt(q, a, 8), a + 25, 6)], 3, 0.8, ROOT, LINE * 0.5, sh=0)
    for i in range(5):
        a = ha + (i - 2) * 24
        p1 = pt(h0, a, 10); p2 = pt(p1, a + (22 if st not in (2, 5) else -22), 8)
        tube([h0, p1, p2], 5.5, 1.2, ROOT, LINE * 0.7, sh=0)
    fx, fy, fs = 34, 150, 1.3
    with T(fx, fy, fs):
        face = bez((-26, 18), (-10, 26), (14, 26), (30, 16)) + bez((30, 16), (36, 0), (32, -26), (18, -36)) + \
            bez((18, -36), (6, -42), (-14, -40), (-24, -30)) + bez((-24, -30), (-34, -10), (-32, 8), (-26, 18))
        form(face, IRON, sdx=-4, sdy=1, sh=0.22)
        C.saveState(); C.clipPath(poly(face), stroke=0, fill=0)
        flat(ell(6, -30, 10, 5, 14), RUST.hex, 0.55)
        flat(ell(-20, -8, 5, 9, 14), RUST.hex, 0.45)
        flat(ell(22, 18, 8, 4, 14), RUST.hex, 0.45)
        stroke(bez((20, 14), (26, 4), (28, -6), (24, -20)), LINE * 1.6, g=IRON_LT, alpha=0.7)
        stroke([(-8, 22), (-4, 12), (-9, 2)], LINE * 0.6)
        C.restoreState()
        brow = bez((-28, 12), (-14, 22), (16, 22), (32, 10)) + bez((32, 10), (16, 14), (-14, 14), (-28, 12))
        shape(brow, IRON_LT, LINE * 0.8)
        for (rx, ry) in ((-22, 8), (26, 6), (-20, -24), (22, -26), (2, 18)):
            shape(ell(rx, ry, 1.3, 1.3, 10), IRON_LT, LINE * 0.5)
        nose = bez((0, 4), (-2, -6), (-5, -14), (-4, -20)) + bez((-4, -20), (0, -22), (5, -22), (8, -18)) + [(4, 4)]
        form(nose, IRON, LINE * 0.8, sdx=-1.5, sdy=0, sh=0.25)
        m = bez((-16, -28), (-4, -32), (10, -32), (20, -27)) + bez((20, -27), (10, -38), (-6, -38), (-16, -28))
        shape(m, MOUTH_DK, LINE * 0.8)
        for k in range(6):
            tx = -12 + k * 6
            shape([(tx - 1.4, -29.5), (tx + 1.4, -29.5), (tx, -33.5)], IRON_LT, LINE * 0.4)
        if st == 3:
            for (ex, ey) in ((-12, 4), (14, 3)):
                ray = [(ex, ey + 2), (ex + 60, ey + 18), (ex + 62, ey - 22), (ex, ey - 2)]
                for k, a_ in ((1.0, 0.1), (0.75, 0.12), (0.5, 0.16)):
                    flat([(ex, ey + 2), (ex + 44 * k, ey + 15 * k), (ex + 46 * k, ey - 18 * k), (ex, ey - 2)], "#ffb040", a_)
            for (ex, ey) in ((-12, 4), (14, 3)):
                shape(ell(ex, ey, 10, 8, 24), MOUTH_DK, LINE)
                eye(ex, ey, 7.5, "#ff6a2a", halo=3.0)
                glow(ex, ey, 5, "#fff2b0", 0.8, 5)
                flat(ell(ex + 1, ey, 1.6, 4, 12), "#3a1208", 0.9)
            for (ex, ey) in ((-12, 4), (14, 3)):
                roll = ell(ex, ey + 24, 14, 7, 24, rot=-5)
                form(roll, LID, sdx=-2, sdy=-2, sh=0.22)
                for k in range(3):
                    stroke(ell(ex, ey + 24, 14 - k * 4, 7 - k * 2, 16, 190, 350, rot=-5), LINE * 0.5, g=LID_DK)
                for k in range(7):
                    x = ex - 11 + k * 3.7
                    stroke([(x, ey + 30), (x + (k - 3) * 0.8, ey + 36)], LINE * 0.9)
    eyes = [(fx + ex * fs, fy + ey * fs) for ex, ey in ((-12, 4), (14, 3))]
    if st != 3:
        sway = {0: 0, 1: -8, 2: 8, 4: 6, 5: -4}[st]
        for (ex, ey), foot, pool in zip(eyes, (24, 56), (10, 14)):
            lid_down((ex, ey + 9), foot + sway, 30, sway * 0.6, pool)
        with T(fx, fy, fs):
            nose = bez((0, 4), (-2, -6), (-5, -14), (-4, -20)) + bez((-4, -20), (0, -22), (5, -22), (8, -18)) + [(4, 4)]
            form(nose, IRON, LINE * 0.8, sdx=-1.5, sdy=0, sh=0.25)
            brow = bez((-28, 12), (-14, 22), (16, 22), (32, 10)) + bez((32, 10), (16, 14), (-14, 14), (-28, 12))
            shape(brow, IRON_LT, LINE * 0.8)
    if st == 2:
        motion([bez((70, 214), (88, 222), (100, 212), (104, 196)), bez((76, 220), (94, 230), (106, 218), (108, 202))])


# ------------------------------------------------------------------ registry
SPRITES = boss_items("san", san, 512, 0.92) + [("san_head", 192, 192, san_head_sprite)] + \
    boss_items("vij", vij, 448, 0.84, extra=("open",))
PORTRAITS = [("boss_san", 256, 256, portrait(san, 70, 160, 1.35, "#4a3030", pose="portrait")),
             ("boss_vij", 256, 256, portrait(vij, 36, 150, 1.55, "#4a3a28", pose="open"))]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
