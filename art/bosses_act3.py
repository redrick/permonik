"""Act III bosses: Strzyga, Mincíř Ohnivec, Ježibaba and her Chaloupka."""
import math
from bosses_kit import *
from bestiary_kit import view_of, ALL

WALKS = ("walk", "walk2", "walk3", "walk4")


def phase(p):
    return math.radians(WALKS.index(p) * 90) if p in WALKS else 0.0


def gait(p):
    """((near swing, near lift), (far swing, far lift)) of a 4-frame walk: contact A, passing, contact B, passing"""
    if p not in WALKS: return None
    ph = phase(p); c, s = math.cos(ph), math.sin(ph)
    up_f, up_n = max(0.0, s), max(0.0, -s)
    return (c + 0.15 * (up_n - up_f), up_n), (-c + 0.15 * (up_f - up_n), up_f)

DRESS = col("#7a8796"); DRESS_DK = col("#58636f"); BACKFACE = col("#aab7c3")
HOOF = col("#5a4a42"); LEATHER = col("#8b5a3a"); LEATHER_DK = col("#64402a")
SKIRT = col("#86704a"); SKIRT_DK = col("#5f4f33"); APRON = col("#b8ad92")
SCARF = col("#b83a36"); SHAWL = col("#6a4f78")
FEATHER = col("#9a7a52"); FEATHER_DK = col("#6e5636")
SMOKE = col("#8f8a8e", 0.55)


def fur_edge(pts, ln=2.6, step=3.2, colr=None, skip=None):
    cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
    for i, (x, y) in enumerate(resample(pts, step, True)):
        if skip and skip(x, y): continue
        dx, dy = x - cx, y - cy; L = math.hypot(dx, dy) or 1
        k = ln * (0.7 + 0.5 * ((i * 37) % 7) / 7)
        stroke([(x - dx / L * 1.5, y - dy / L * 1.5), (x + dx / L * k + dy / L * 0.8, y + dy / L * k - dx / L * 0.8)],
               LINE * 0.55, g=colr if colr is not None else 0.0)


def foot_claws(p, ang=0, n=3, ln=5, colr=None):
    claws(p, ang, n, ln, 1.4, 12, colr if colr is not None else BONE_DK, curl=-30)


# ------------------------------------------------------------------ Strzyga
def stride(hip, sw, lift, reach=20, foot_y=3, bend=3):
    ft = (hip[0] + 2 + sw * reach, foot_y + lift * 7)
    kn = ((hip[0] + ft[0]) / 2 + bend + lift * 7, (hip[1] + ft[1]) / 2 + lift * 2)
    return hip, kn, ft


def strzyga(pose):
    pose, v = view_of(pose)
    if v: return strzyga_fb(pose, v)
    g = gait(pose); ph = phase(pose)
    lean = {"idle": 0, "windup": -3, "attack": 9}.get(pose, 5)
    sway = {"idle": 0, "windup": 5, "attack": -4}.get(pose, -6 * math.cos(ph - 0.8))
    shadow(0, 36)
    if g:
        legs = [stride((-6, 26), *g[1]), stride((8, 26), *g[0])]
    else:
        legs = {"idle": [((-6, 26), (-7, 12), (-9, 3)), ((8, 26), (10, 12), (12, 3))],
                "windup": [((-6, 26), (-14, 13), (-18, 3)), ((8, 26), (17, 13), (20, 3))],
                "attack": [((-6, 26), (-16, 12), (-24, 3)), ((8, 26), (20, 15), (26, 3))]}[pose]
    for hip, kn, ft in legs:
        tube([hip, kn], 5, 4, HAG_DK); tube([kn, ft], 4, 3.2, HAG_DK)
        shape(ell(ft[0] + 2, ft[1] - 0.5, 4.5, 2.2, 12), HAG_DK, LINE * 0.8)
        foot_claws((ft[0] + 5.5, ft[1] - 1), -12, 3, 4.5)
    sh0 = (4 + lean, 96)
    if pose == "attack":
        e1 = (20 + lean, 118); h1 = (40 + lean, 126); a1 = 15
    elif g:
        a1 = -122 + 48 * g[0][0]; e1 = pt(sh0, a1 + 4, 19); h1 = pt(e1, a1, 21)
    elif pose == "windup":
        e1 = (-14, 110); h1 = (-26, 128); a1 = 120
    else:
        e1 = (-6, 80); h1 = (-16, 62); a1 = 240
    tube([sh0, e1], 5.5, 4.4, HAG_DK); tube([e1, h1], 4.4, 3.4, HAG_DK)
    shape(ell(h1[0], h1[1], 3.4, 2.6, 12, rot=a1), HAG_DK, LINE * 0.8)
    claws(h1, a1, 4, 11, 1.4, 16, BONE_DK, curl=-30)
    dress = ragged((-32 + sway, 26), (24 + sway * 0.3, 24), 6, 9, 0.7) + \
        bez((24 + sway * 0.3, 24), (30, 46), (24 + lean * 0.5, 70), (20 + lean, 88)) + \
        bez((20 + lean, 88), (16 + lean, 98), (8 + lean, 106), (-2 + lean * 0.6, 110)) + \
        bez((-2 + lean * 0.6, 110), (-18 + lean * 0.3, 112), (-28, 96), (-30, 76)) + \
        bez((-30, 76), (-34, 56), (-38 + sway, 40), (-32 + sway, 26))
    form(dress, DRESS, sdx=-4, sdy=2, sh=0.18)
    C.saveState(); C.clipPath(poly(dress), stroke=0, fill=0)
    hatch(ell(-28 + sway * 0.5, 60, 14, 60, 20), 1.9, 62, 0.5, g=DRESS_DK, alpha=0.8)
    hatch(ell(0, 20, 40, 10, 20), 2.0, 30, 0.45, g=DRESS_DK, alpha=0.7)
    shape(rrect(-14, 44, 10, 9, 1), DRESS_DK, LINE * 0.6)
    for i in range(4): stroke([(-13 + i * 2.6, 45), (-12 + i * 2.6, 52)], LINE * 0.35)
    C.restoreState()
    for (x0, y0, x1, y1) in ((-10, 104, -20 + sway, 22), (6, 96, 0 + sway * 0.5, 18), (16, 84, 16, 20), (-22, 96, -28 + sway, 30)):
        stroke(bez((x0 + lean * 0.5, y0), (x0 - 2, y0 - 30), (x1 + 2, y1 + 30), (x1, y1)), LINE * 0.55, g=DRESS_DK)
    belt = bez((-31, 58), (-10, 54), (10, 56), (26 + lean * 0.4, 62))
    stroke(belt, LINE * 2.6, g=ROOT); stroke(belt, LINE * 0.6)
    tube([(14, 58), (12, 44)], 1.6, 1.2, ROOT, LINE * 0.5, sh=0)
    for k in range(3): bone((-16 + k * 7, 54), (-15 + k * 7, 46), 1.4)
    hx, hy = 26 + lean, 102 - lean * 0.3
    hair = bez((hx - 4, hy + 13), (hx - 22, hy + 16), (-14 + lean * 0.5, 104), (-30 + sway * 0.4, 70)) + \
        ragged((-30 + sway * 0.4, 70), (-12 + sway * 0.3, 62), 4, 7, 1.1) + \
        bez((-12 + sway * 0.3, 62), (-4, 80), (hx - 18, hy - 4), (hx - 10, hy - 8))
    form(hair, HAIR_DK, sdx=-2, sdy=1, sh=0.2)
    for k in range(5):
        stroke(bez((hx - 8 - k * 2, hy + 10), (-6 + k * 2, 100 - k), (-18 + k * 3, 84), (-26 + k * 4 + sway * 0.4, 66 - k)), LINE * 0.5, g=HAIR_GREY, alpha=0.7)
    tube([(10 + lean, 96), (hx - 3, hy - 5)], 7, 6, HAG, sh=0.2)
    shape(ell(hx, hy, 12.5, 11.5, 30), HAIR_DK, LINE)
    ff = bez((hx + 1, hy + 9), (hx + 9, hy + 9), (hx + 12, hy + 4), (hx + 12, hy + 1)) + \
        [(hx + 18, hy - 4.5), (hx + 12.5, hy - 4.5)] + \
        bez((hx + 12.5, hy - 4.5), (hx + 14, hy - 10), (hx + 10, hy - 14), (hx + 4, hy - 13)) + \
        bez((hx + 4, hy - 13), (hx, hy - 10), (hx - 0.5, hy - 2), (hx + 1, hy + 9))
    form(ff, HAG, sdx=-1.5, sdy=0, sh=0.22)
    m = bez((hx + 6, hy - 7), (hx + 9, hy - 6), (hx + 12, hy - 6.5), (hx + 13.5, hy - 8)) + \
        bez((hx + 13.5, hy - 8), (hx + 11, hy - (12 if pose in ("attack", "windup") else 10)), (hx + 8, hy - 11), (hx + 6, hy - 7))
    shape(m, MOUTH_DK, LINE * 0.6)
    for tx in (hx + 8.5, hx + 11):
        shape([(tx - 0.5, hy - 6.6), (tx + 0.6, hy - 6.6), (tx, hy - 9)], BONE, LINE * 0.3)
    stroke([(hx + 4, hy + 6.5), (hx + 10.5, hy + 5)], LINE * 1.1)
    eye(hx + 7.5, hy + 3, 1.9, EYE_RED, halo=3.2)
    bf = bez((hx - 1, hy + 9), (hx - 8, hy + 9), (hx - 11, hy + 4), (hx - 11.5, hy + 1)) + \
        [(hx - 16.5, hy - 3.5), (hx - 11.5, hy - 4)] + \
        bez((hx - 11.5, hy - 4), (hx - 12.5, hy - 9), (hx - 9, hy - 13), (hx - 4, hy - 12.5)) + \
        bez((hx - 4, hy - 12.5), (hx - 1.5, hy - 9), (hx - 1.5, hy - 2), (hx - 1, hy + 9))
    form(bf, BACKFACE, sdx=1.5, sdy=0, sh=0.22)
    stroke(bez((hx - 11, hy - 8.5), (hx - 8.5, hy - 10.5), (hx - 6, hy - 10.5), (hx - 4, hy - 8.5)), LINE * 0.7)
    for i in range(4):
        x = hx - 10 + i * 1.8
        stroke([(x, hy - 8.3), (x - 0.3, hy - 10.6)], LINE * 0.4)
    stroke([(hx - 3.5, hy + 6.5), (hx - 9.5, hy + 5)], LINE * 1.1)
    eye(hx - 6.5, hy + 3, 1.7, EYE_BLUE, halo=3.2)
    for s in (-1, 1):
        tear = bez((hx + s * 6.5, hy + 1), (hx + s * 6.5, hy - 3), (hx + s * 5.5, hy - 6), (hx + s * 6, hy - 9))
        stroke(tear, LINE * 0.4, alpha=0.5)
    cap = bez((hx - 12.5, hy + 2), (hx - 13, hy + 13), (hx - 3, hy + 15), (hx, hy + 14)) + \
        bez((hx, hy + 14), (hx + 4, hy + 15), (hx + 13, hy + 12), (hx + 12, hy + 3)) + \
        bez((hx + 12, hy + 3), (hx + 7, hy + 9), (hx + 3, hy + 10), (hx, hy + 9)) + \
        bez((hx, hy + 9), (hx - 3, hy + 10), (hx - 8, hy + 9), (hx - 12.5, hy + 2))
    form(cap, HAIR_DK, sdx=0, sdy=-1, sh=0.15)
    stroke([(hx, hy + 14.5), (hx, hy + 9)], LINE * 0.6, g=HAIR_GREY)
    for s in (-1, 1):
        for k in range(3):
            stroke(bez((hx + s * 2, hy + 13 - k), (hx + s * (7 + k * 2), hy + 13 - k * 2), (hx + s * (11 + k), hy + 6 - k), (hx + s * (12 + k), hy + 2 - k)), LINE * 0.45, g=HAIR_GREY, alpha=0.8)
        lock = bez((hx + s * 11, hy + 4), (hx + s * 15, hy - 8), (hx + s * 13, hy - 20), (hx + s * (17 if s < 0 else 14), hy - 32)) + \
            [(hx + s * (14 if s < 0 else 11), hy - 31)] + \
            bez((hx + s * (14 if s < 0 else 11), hy - 31), (hx + s * 11, hy - 20), (hx + s * 12, hy - 8), (hx + s * 9, hy + 3))
        form(lock, HAIR_DK, sh=0.1)
        stroke(bez((hx + s * 11.5, hy), (hx + s * 13, hy - 10), (hx + s * 12.5, hy - 20), (hx + s * 14, hy - 28)), LINE * 0.4, g=HAIR_GREY)
    s0 = (12 + lean, 94)
    if pose == "attack":
        e0 = (32 + lean, 86); h0 = (50 + lean, 80); ca = -15
    elif g:
        ca = -68 + 42 * g[1][0]; e0 = pt(s0, ca + 6, 25); h0 = pt(e0, ca, 20)
    elif pose == "windup":
        e0 = (-2, 82); h0 = (-18, 92); ca = 160
    else:
        e0 = (24, 72); h0 = (34, 54); ca = -65
    tube([s0, e0], 6, 4.8, HAG); tube([e0, h0], 4.8, 3.6, HAG)
    for k in range(3):
        q = pt(e0, ca + 180, 3 + k * 3); stroke([q, pt(q, ca + 90, 2)], LINE * 0.45)
    shape(ell(h0[0], h0[1], 3.6, 2.8, 12, rot=ca), HAG, LINE * 0.8)
    claws(h0, ca, 4, 12, 1.5, 16, BONE_DK, curl=-30)
    slv = [(s0[0] - 7, s0[1] + 7)] + bez((s0[0] - 7, s0[1] + 7), (s0[0] + 5, s0[1] + 10), (e0[0] - 2, e0[1] + 8), (e0[0] - 1, e0[1] + 3)) + \
        ragged((e0[0] - 1, e0[1] + 3), (e0[0] - 9, e0[1] - 2), 3, 4, 2) + \
        bez((e0[0] - 9, e0[1] - 2), (s0[0] - 3, s0[1] - 12), (s0[0] - 10, s0[1] - 6), (s0[0] - 7, s0[1] + 7))
    form(slv, DRESS, sdx=-2, sdy=1.5, sh=0.16)
    if pose == "attack":
        motion([bez((30 + lean, 136), (44 + lean, 140), (56 + lean, 134), (64 + lean, 124)),
                bez((44 + lean, 96), (54 + lean, 94), (62 + lean, 88), (66 + lean, 80))])


def fb_legs(pose, back, stance=0.0):
    """per screen side (-1, +1): (depth toward viewer, lift); depth flips in the back view"""
    g = gait(pose)
    if g:
        out = {-1: g[0], 1: g[1]}
    else:
        out = {-1: (stance, 0), 1: (-stance, 0)}
    return {s: ((-d if back else d), l) for s, (d, l) in out.items()}


def hag_arm_fb(sh, el, hd, ca, sleeve, skin, claw=11, sc=1.0):
    tube([sh, el], 8.5 * sc, 7 * sc, sleeve, sh=0.16)
    tube([el, hd], 4.6 * sc, 3.6 * sc, skin)
    shape(ell(hd[0], hd[1], 3.6 * sc, 2.9 * sc, 12, rot=ca), skin, LINE * 0.8)
    claws(hd, ca, 4, claw * sc, 1.4, 18, BONE_DK, curl=-25)


def strzyga_fb(pose, v):
    back = v == "b"
    g = gait(pose); ph = phase(pose)
    lg = fb_legs(pose, back)
    tilt = 2.5 * math.cos(ph) if g else 0
    sway = 4 * math.sin(ph - 0.8) if g else 0
    wide = {"attack": 5, "windup": 3}.get(pose, 0)
    shadow(0, 32)
    for s in (-1, 1):
        d, l = lg[s]
        sc = 1 + 0.07 * d
        ft = (s * (9 + wide), 3 - 2 * d + 7 * l)
        kn = (s * (9 + wide * 0.6 + l * 2), 14 + l * 4)
        tube([(s * 7, 26), kn], 5 * sc, 4 * sc, HAG_DK); tube([kn, ft], 4 * sc, 3.2 * sc, HAG_DK)
        shape(ell(ft[0], ft[1] + 0.5, 3.8 * sc, 2.4 * sc, 12), HAG_DK, LINE * 0.8)
        if back:
            claws((ft[0], ft[1] + 1), -90, 1, 3.5, 1.4, 4, BONE_DK, curl=s * 20)
        else:
            claws((ft[0], ft[1] - 0.5), -90 + s * 8, 3, 4.5 * sc, 1.3, 14, BONE_DK, curl=s * 25)
    hx, hy = 0, 101
    with T(0, 0, 1, rot=tilt):
        if not back:
            hb = bez((-11, hy + 4), (-24, hy - 6), (-30, 86 + sway), (-28 + sway, 70)) + [(28 + sway, 70)] + \
                bez((28 + sway, 70), (30, 86 + sway), (24, hy - 6), (11, hy + 4))
            form(hb, HAIR_DK, sh=0.2)
        arms = {}
        for s in (-1, 1):
            sh0 = (s * 19, 97)
            if pose == "windup":
                el, hd, ca = (s * 31, 116), (s * 27, 136), 90 + s * 18
            elif pose == "attack" and not back:
                el, hd, ca = (s * 27, 86), (s * 13, 74), -90 + s * 35
            elif pose == "attack":
                el, hd, ca = (s * 26, 110), (s * 15, 124), 90 + s * 15
            else:
                a = -lg[s][0] if g else 0
                el = (s * (29 - a), 78 - a)
                hd = (s * (32 - 3 * a), 60 - 3 * a)
                ca = -90 + s * (12 + 6 * a)
            arms[s] = (sh0, el, hd, ca)
        if pose == "attack" and back:
            for s in (-1, 1): hag_arm_fb(*arms[s], DRESS, HAG, 10, 0.92)
        hem = ragged((-34 + sway, 24), (34 + sway, 24), 7, 9, 0.7)
        dress = hem + bez((34 + sway, 24), (40, 48), (36, 78), (24, 99)) + \
            bez((24, 99), (18, 110), (-18, 110), (-24, 99)) + bez((-24, 99), (-36, 78), (-40, 48), (-34 + sway, 24))
        form(dress, DRESS, sdx=-3, sdy=2, sh=0.18)
        C.saveState(); C.clipPath(poly(dress), stroke=0, fill=0)
        for s in (-1, 1):
            hatch(ell(s * 34, 60, 12, 54, 20), 1.9, 62 if s < 0 else 118, 0.5, g=DRESS_DK, alpha=0.8)
        hatch(ell(0, 20, 40, 10, 20), 2.0, 30, 0.45, g=DRESS_DK, alpha=0.7)
        if back:
            shape(rrect(-14, 38, 10, 9, 1), DRESS_DK, LINE * 0.6)
            for i in range(4): stroke([(-13 + i * 2.6, 39), (-12 + i * 2.6, 46)], LINE * 0.35)
        C.restoreState()
        for (x0, x1) in ((-14, -22), (-4, -6), (6, 8), (16, 24)):
            stroke(bez((x0, 104), (x0 - 1, 74), (x1 + 1, 50), (x1 + sway, 20)), LINE * 0.55, g=DRESS_DK)
        belt = bez((-35, 58), (-12, 53), (12, 53), (35, 58))
        stroke(belt, LINE * 2.6, g=ROOT); stroke(belt, LINE * 0.6)
        if back:
            tube([(-3, 54), (-5 + sway * 0.4, 42)], 1.6, 1.2, ROOT, LINE * 0.5, sh=0)
            tube([(3, 54), (5 + sway * 0.4, 44)], 1.6, 1.2, ROOT, LINE * 0.5, sh=0)
            hair = bez((-11, hy - 6), (-22, hy - 16), (-26, 88), (-25 + sway, 66)) + ragged((-25 + sway, 66), (25 + sway, 66), 5, 7, 1.1) + \
                bez((25 + sway, 66), (26, 88), (22, hy - 16), (11, hy - 6))
            form(hair, HAIR_DK, sdx=-2, sdy=1, sh=0.2)
            for k in range(7):
                x = -18 + k * 6
                stroke(bez((x * 0.4, hy - 8), (x * 0.8, 92), (x, 80), (x * 1.1 + sway, 68)), LINE * 0.5, g=HAIR_GREY, alpha=0.7)
        else:
            tube([(10, 55), (11 + sway * 0.4, 42)], 1.6, 1.2, ROOT, LINE * 0.5, sh=0)
            for k in range(3): bone((-8 + k * 7, 53), (-7.5 + k * 7, 45), 1.4)
        if not (pose == "attack" and back):
            for s in (-1, 1): hag_arm_fb(*arms[s], DRESS, HAG, 12 if pose == "attack" else 11, 1.12 if pose == "attack" else 1.0)
        shape(ell(hx, hy, 12.5, 11.5, 30), HAIR_DK, LINE)
        skin = BACKFACE if back else HAG
        face = bez((-8.5, hy + 8), (-10.5, hy - 2), (-6, hy - 12), (0, hy - 15)) + bez((0, hy - 15), (6, hy - 12), (10.5, hy - 2), (8.5, hy + 8)) + \
            bez((8.5, hy + 8), (4, hy + 10), (-4, hy + 10), (-8.5, hy + 8))
        form(face, skin, sdx=0, sdy=-1, sh=0.2)
        open_ = pose in ("attack", "windup")
        if back:
            for s in (-1, 1):
                stroke([(s * 2, hy + 5), (s * 8, hy + 6.5)], LINE * 1.1)
                eye(s * 4.2, hy + 2.6, 1.7, EYE_BLUE, halo=3.2)
            stroke(bez((-6, hy - 6), (-3, hy - 9), (3, hy - 9), (6, hy - 6)), LINE * 0.7)
            for i in range(6):
                x = -4.5 + i * 1.8
                stroke([(x, hy - 7.2 - (1.2 if 0 < i < 5 else 0)), (x, hy - 5.2 - (0.8 if 0 < i < 5 else 0))], LINE * 0.4)
        else:
            for s in (-1, 1):
                stroke([(s * 2, hy + 6.5), (s * 8, hy + 5)], LINE * 1.1)
                eye(s * 4.2, hy + 2.6, 1.9, EYE_RED, halo=3.2)
            stroke(bez((0, hy + 3), (-1.2, hy - 1), (-1.4, hy - 3), (0.8, hy - 3.6)), LINE * 0.6)
            m = bez((-5, hy - 7), (-2, hy - 6), (2, hy - 6), (5, hy - 7)) + \
                bez((5, hy - 7), (3, hy - (12 if open_ else 9.5)), (-3, hy - (12 if open_ else 9.5)), (-5, hy - 7))
            shape(m, MOUTH_DK, LINE * 0.6)
            for tx in (-2.2, 2.2):
                shape([(tx - 0.6, hy - 6.6), (tx + 0.6, hy - 6.6), (tx, hy - 9)], BONE, LINE * 0.3)
        for s in (-1, 1):
            stroke(bez((s * 4.5, hy + 1), (s * 4.5, hy - 3), (s * 4, hy - 6), (s * 4.5, hy - 9)), LINE * 0.4, alpha=0.5)
        cap = bez((-12.5, hy + 2), (-13, hy + 13), (-3, hy + 15), (0, hy + 14)) + \
            bez((0, hy + 14), (3, hy + 15), (13, hy + 13), (12.5, hy + 2)) + \
            bez((12.5, hy + 2), (8, hy + 9), (3, hy + 10), (0, hy + 9)) + \
            bez((0, hy + 9), (-3, hy + 10), (-8, hy + 9), (-12.5, hy + 2))
        form(cap, HAIR_DK, sdx=0, sdy=-1, sh=0.15)
        stroke([(0, hy + 14.5), (0, hy + 9)], LINE * 0.6, g=HAIR_GREY)
        for s in (-1, 1):
            for k in range(3):
                stroke(bez((s * 2, hy + 13 - k), (s * (7 + k * 2), hy + 13 - k * 2), (s * (11 + k), hy + 6 - k), (s * (12 + k), hy + 2 - k)), LINE * 0.45, g=HAIR_GREY, alpha=0.8)
            tip = s * 15 + sway * 0.6
            lock = bez((s * 11, hy + 4), (s * 15, hy - 8), (s * 13, hy - 20), (tip, hy - 32)) + [(tip - s * 3, hy - 31)] + \
                bez((tip - s * 3, hy - 31), (s * 10, hy - 20), (s * 11, hy - 8), (s * 8.5, hy + 3))
            form(lock, HAIR_DK, sh=0.1)
            stroke(bez((s * 11.5, hy), (s * 13, hy - 10), (s * 12.5, hy - 20), (tip - s, hy - 28)), LINE * 0.4, g=HAIR_GREY)
        if pose == "attack" and not back:
            motion([bez((-30, 128), (-26, 112), (-20, 96), (-16, 84)), bez((30, 128), (26, 112), (20, 96), (16, 84))])


strzyga.poses = ALL


# ------------------------------------------------------------------ Mincíř Ohnivec
def coin(x, y, r=2.6, squash=0.9, lit=True):
    if lit: glow(x, y, r * 2.6, FIRE, 0.45, 6)
    shape(ell(x, y, r, r * squash, 16), GOLD, LINE * 0.6)
    stroke(ell(x, y, r * 0.65, r * 0.65 * squash, 12), LINE * 0.35, closed=True, g=GOLD_DK)
    stroke([(x - r * 0.3, y), (x + r * 0.3, y)], LINE * 0.35, g=GOLD_DK)
    if lit: dot(x - r * 0.3, y + r * 0.3 * squash, r * 0.25, col(EMBER))


def hammer(hand, ang, ln=48, hot=True):
    end = pt(hand, ang, ln); start = pt(hand, ang + 180, 8)
    tube([start, end], 3.6, 4.2, WOOD, LINE * 0.8)
    for d in (-3, 3):
        q = pt(hand, ang, d); stroke([pt(q, ang + 90, 2.2), pt(q, ang - 90, 2.2)], LINE * 0.5)
    with T(end[0], end[1], 1, rot=ang - 90):
        blk = [(-12, -5), (12, -5), (13, 5), (-13, 5)]
        form(blk, IRON, sdx=-1.5, sdy=1, sh=0.25)
        shape([(-13, -6), (-16, -7), (-16, 7), (-13, 6)], IRON_LT, LINE * 0.8)
        shape([(12, -6), (15, -7), (15, 7), (12, 6)], IRON_LT, LINE * 0.8)
        for x in (-6, 0, 6): dot(x, 0, 0.9, IRON_LT)
        if hot:
            glow(-16, 0, 9, FIRE, 0.5); flat(rrect(-16.5, -5.5, 2.4, 11, 1), EMBER, 0.9)


def _ohn_arm(pose):
    sp = (18, 100)
    g = gait(pose)
    if pose == "attack":
        el, hd = (36, 124), (22, 142); hang = 175
    elif g:
        a = g[1][0]
        el = pt(sp, -54 + 18 * a, 27); hd = pt(el, -76 + 30 * a, 21); hang = -88 + 30 * a
    elif pose == "windup":
        el, hd = (34, 120), (12, 134); hang = 215
    else:
        el, hd = (34, 78), (40, 58); hang = -86
    if pose in ("attack", "windup"):
        hammer(hd, hang, 40)
    tube([sp, el], 14, 11, FUR_DEVIL, sh=0.15); tube([el, hd], 11, 9, FUR_DEVIL, sh=0.15)
    if pose not in ("attack", "windup"):
        hammer(hd, hang, 40 if g else 50)
    shape(ell(hd[0], hd[1], 5.5, 5, 14), FUR_DEVIL_DK, LINE * 0.8)
    claws(pt(hd, hang + 90, 3), hang + 90, 3, 4, 1.2, 8, BONE_DK, curl=-60)
    if pose == "attack":
        motion([bez((-30, 160), (-16, 164), (0, 160), (12, 150)), bez((-36, 120), (-40, 130), (-38, 142), (-32, 152))])
        for (x, y) in ((48, 104), (54, 92), (44, 114), (60, 98)):
            dot(x, y, 0.8, col(EMBER)); glow(x, y, 2.5, FIRE, 0.5, 4)


def pouch(hd):
    pc = bez((hd[0] - 3, hd[1]), (hd[0] - 12, hd[1] - 4), (hd[0] - 12, hd[1] - 18), (hd[0], hd[1] - 20)) + \
        bez((hd[0], hd[1] - 20), (hd[0] + 12, hd[1] - 18), (hd[0] + 12, hd[1] - 4), (hd[0] + 3, hd[1]))
    form(pc, LEATHER, sdx=-2, sdy=1, sh=0.22)
    stroke(bez((hd[0] - 4, hd[1] - 1), (hd[0] - 2, hd[1] - 3), (hd[0] + 2, hd[1] - 3), (hd[0] + 4, hd[1] - 1)), LINE * 1.2, g=LEATHER_DK)
    glow(hd[0] + 7, hd[1] - 12, 8, FIRE, 0.4)
    for (dx, dy) in ((9, -14), (11, -22), (8, -30), (12, -38)):
        if hd[1] + dy > 6: coin(hd[0] + dx, hd[1] + dy, 2.2, 0.55 + 0.1 * (dy % 3))


def floor_coins():
    for (x, y, r, sq) in ((-44, 7, 2.6, 0.4), (40, 6, 2.4, 0.4), (54, 7, 2.2, 0.4), (-30, 6, 2.2, 0.4), (30, 9, 2.4, 0.4)):
        coin(x, y, r, sq)


def ohnivec(pose):
    pose, v = view_of(pose)
    if v: return ohnivec_fb(pose, v)
    g = gait(pose); ph = phase(pose)
    shadow(0, 46)
    floor_coins()
    if g:
        legs = [stride((-14, 42), g[1][0], g[1][1], 16, 6, 1), stride((12, 40), g[0][0], g[0][1], 16, 7, 3)]
    elif pose in ("attack", "windup"):
        legs = [((-14, 42), (-26, 22), (-30, 6)), ((12, 40), (24, 22), (26, 7))]
    else:
        legs = [((-14, 42), (-20, 22), (-20, 6)), ((12, 40), (20, 22), (18, 7))]
    tw = 6 * math.sin(ph - 0.9) if g else 0
    tail = [(-34, 52), (-60, 44 + tw * 0.3), (-70 - tw * 0.5, 74), (-56 - tw, 96 - abs(tw) * 0.4)]
    tl = bez(*tail)
    tube(tl, 5, 2.4, FUR_DEVIL, sh=0.1)
    tip = tl[-1]
    tuft = [(tip[0] - 2, tip[1] - 2), (tip[0] - 8, tip[1] + 4), (tip[0] - 3, tip[1] + 4), (tip[0] - 4, tip[1] + 11),
            (tip[0] + 1, tip[1] + 6), (tip[0] + 4, tip[1] + 12), (tip[0] + 5, tip[1] + 4), (tip[0] + 10, tip[1] + 5), (tip[0] + 3, tip[1] - 2)]
    form(tuft, FUR_DEVIL_DK, sh=0.1)
    for i, (hip, kn, ft) in enumerate(legs):
        gc = FUR_DEVIL_DK if i == 0 else FUR_DEVIL
        tube([hip, kn], 16, 12, gc, sh=0.15); tube([kn, ft], 12, 8, gc, sh=0.15)
        if i == 0:
            fp = [(ft[0] - 6, ft[1] + 3), (ft[0] - 7, ft[1] - 5), (ft[0] + 9, ft[1] - 5), (ft[0] + 8, ft[1] + 1)]
            form(fp, SKIN_RED, sh=0.2)
            foot_claws((ft[0] + 8, ft[1] - 3), -15, 3, 4.5)
        else:
            hf = [(ft[0] - 6, ft[1] + 2), (ft[0] - 7, ft[1] - 6), (ft[0] + 8, ft[1] - 6), (ft[0] + 6, ft[1] + 2)]
            form(hf, HOOF, sh=0.2)
            stroke([(ft[0] + 1, ft[1] - 6), (ft[0] + 1.5, ft[1] - 1)], LINE * 0.8)
            fur = ragged((ft[0] - 8, ft[1] + 4), (ft[0] + 8, ft[1] + 4), 4, 3, 0.4)
            shape(fur + [(ft[0] + 6, ft[1] + 9), (ft[0] - 6, ft[1] + 9)], gc, LINE * 0.7)
    sp = (-22, 102)
    if pose in ("attack", "windup"):
        el, hd = (-40, 86), (-50, 70)
    elif g:
        a = g[0][0]
        el, hd = (-37 + 2 * a, 81), (-40 + 10 * a, 61 + abs(a) * 2)
    else:
        el, hd = (-36, 80), (-40, 60)
    tube([sp, el], 13, 10, FUR_DEVIL_DK, sh=0.15); tube([el, hd], 10, 8, FUR_DEVIL_DK, sh=0.15)
    pouch(hd)
    shape(ell(hd[0], hd[1] + 1, 4.5, 4, 12), FUR_DEVIL_DK, LINE * 0.8)
    body = ell(0, 66, 40, 44, 40)
    form(body, FUR_DEVIL, sdx=-6, sdy=3, sh=0.18)
    fur_edge(body, 3.0, 3.6, skip=lambda x, y: y < 30)
    belly = ell(8, 66, 26, 32, 30)
    form(belly, SKIN_RED, sdx=-4, sdy=1, sh=0.15)
    for k in range(4):
        stroke(ell(8, 70 - k * 2, 18 - k * 3, 20 - k * 4, 12, 210, 330), LINE * 0.4, alpha=0.5)
    shoulders = ell(-2, 100, 30, 16, 30)
    form(shoulders, FUR_DEVIL, sdx=-3, sdy=2, sh=0.15)
    fur_edge(shoulders, 2.6, 3.4, skip=lambda x, y: y < 96)
    apron = [(-16, 96), (22, 96)] + bez((22, 96), (30, 72), (38, 46), (34, 24)) + \
        bez((34, 24), (12, 18), (-12, 18), (-26, 26)) + bez((-26, 26), (-26, 50), (-22, 76), (-16, 96))
    form(apron, LEATHER, sdx=-4, sdy=1.5, sh=0.2)
    stroke([(p[0] * 0.92 + 1, p[1] * 0.97 + 2) for p in apron], LINE * 0.35, closed=True, g=LEATHER_DK)
    C.saveState(); C.clipPath(poly(apron), stroke=0, fill=0)
    hatch(ell(-24, 50, 10, 40, 16), 1.8, 60, 0.45, g=LEATHER_DK)
    for (x, y, r) in ((6, 40, 3), (18, 62, 2.2), (-8, 70, 2.6)):
        shape(ell(x, y, r, r * 0.8, 12), LEATHER_DK, LINE * 0.5)
        stroke(ell(x, y, r * 1.25, r, 12), LINE * 0.6, closed=True, g=col(FIRE), alpha=0.7)
    C.restoreState()
    for (x0, x1) in ((0, -4), (14, 16)):
        stroke(bez((x0, 94), (x0 - 2, 70), (x1 + 2, 44), (x1, 22)), LINE * 0.5, g=LEATHER_DK)
    stroke(bez((-16, 96), (-6, 106), (10, 108), (22, 96)), LINE * 1.6, g=LEATHER_DK)
    with T(10, 52):
        shape(ell(0, 0, 6, 6, 20), GOLD, LINE * 0.7)
        stroke(ell(0, 0, 4.2, 4.2, 16), LINE * 0.4, closed=True, g=GOLD_DK)
        stroke([(-2, -2), (0, 2), (2, -2)], LINE * 0.5, g=GOLD_DK)
        glow(0, 0, 10, FIRE, 0.25, 5)
    if pose in ("attack", "windup"):
        _ohn_arm(pose)
    hx, hy = 24, 118
    for s, gcol in ((-1, HORN), (1, HORN)):
        ox = 0 if s > 0 else -7
        hb = bez((hx - 4 + ox, hy + 9), (hx - 14 + ox, hy + 30), (hx - 34 + ox, hy + 30), (hx - 36 + ox, hy + 16)) + \
            bez((hx - 36 + ox, hy + 16), (hx - 37 + ox, hy + 10), (hx - 31 + ox, hy + 8), (hx - 30 + ox, hy + 13)) + \
            bez((hx - 30 + ox, hy + 13), (hx - 28 + ox, hy + 20), (hx - 14 + ox, hy + 20), (hx + 3 + ox, hy + 8))
        form(hb, gcol if s > 0 else BONE_SH, sdx=-1, sdy=-1.5, sh=0.2)
        for k in range(5):
            t = 0.15 + k * 0.17
            q0 = bez((hx - 4 + ox, hy + 9), (hx - 14 + ox, hy + 30), (hx - 34 + ox, hy + 30), (hx - 36 + ox, hy + 16), 10)[int(t * 10)]
            q1 = bez((hx + 3 + ox, hy + 8), (hx - 14 + ox, hy + 20), (hx - 28 + ox, hy + 20), (hx - 30 + ox, hy + 13), 10)[int(t * 10)]
            stroke([q0, q1], LINE * 0.5)
    ear = [(hx - 8, hy + 4), (hx - 24, hy + 2), (hx - 10, hy - 3)]
    form(ear, FUR_DEVIL, sh=0.15); stroke([(hx - 10, hy + 2), (hx - 19, hy + 1.5)], LINE * 0.5)
    open_ = pose == "attack"
    head = bez((hx - 12, hy + 4), (hx - 12, hy + 14), (hx + 2, hy + 16), (hx + 10, hy + 10)) + \
        bez((hx + 10, hy + 10), (hx + 18, hy + 6), (hx + 24, hy + 2), (hx + 25, hy - 4)) + \
        bez((hx + 25, hy - 4), (hx + 25, hy - 8), (hx + 20, hy - 9), (hx + 16, hy - 8)) + \
        bez((hx + 16, hy - 8), (hx + 14, hy - 14), (hx + 6, hy - 16), (hx, hy - 14)) + \
        bez((hx, hy - 14), (hx - 8, hy - 12), (hx - 12, hy - 6), (hx - 12, hy + 4))
    form(head, SKIN_RED, sdx=-3, sdy=1, sh=0.2)
    hatch(ell(hx - 7, hy, 5, 9, 14), 1.4, 60, 0.4, alpha=0.6)
    fur_edge(bez((hx - 12, hy + 4), (hx - 12, hy + 14), (hx + 2, hy + 16), (hx + 10, hy + 10)) + [(hx - 6, hy)], 2.4, 2.8)
    shape(ell(hx + 23, hy - 3, 2.6, 2.0, 12), MOUTH_DK, LINE * 0.6)
    m = bez((hx + 4, hy - 5), (hx + 10, hy - 7), (hx + 16, hy - 7), (hx + 21, hy - 6)) + \
        bez((hx + 21, hy - 6), (hx + 18, hy - (14 if open_ else 10)), (hx + 10, hy - (15 if open_ else 11)), (hx + 4, hy - 5))
    shape(m, MOUTH_DK, LINE * 0.7)
    for tx in (hx + 8, hx + 13, hx + 18):
        shape([(tx - 0.8, hy - 6.4), (tx + 0.8, hy - 6.4), (tx, hy - 9.5)], BONE, LINE * 0.3)
    if open_:
        tg = bez((hx + 10, hy - 11), (hx + 16, hy - 16), (hx + 22, hy - 22), (hx + 26, hy - 20)) + \
            bez((hx + 26, hy - 20), (hx + 24, hy - 16), (hx + 18, hy - 12), (hx + 13, hy - 10))
        form(tg, col("#c75a68"), sh=0.15)
    beard = [(hx + 2, hy - 12), (hx + 10, hy - 12), (hx + 7, hy - 22), (hx + 5, hy - 17), (hx + 2, hy - 24), (hx + 1, hy - 16)]
    form(beard, FUR_DEVIL_DK, sh=0.1)
    stroke([(hx + 4, hy + 7), (hx + 15, hy + 4)], LINE * 1.3)
    eye(hx + 11, hy + 1.5, 2.3, EYE_ORANGE, slit=True, halo=3.0)
    eye(hx + 3, hy + 2.5, 1.8, EYE_ORANGE, slit=True, halo=2.6)
    if pose not in ("attack", "windup"):
        _ohn_arm(pose)


def ohn_horns_fb(hx, hy, k=0.85):
    for s in (-1, 1):
        P = lambda x, y: (hx + s * (-x * k + 3), hy + y * k)
        a = ((-4, 9), (-14, 30), (-34, 30), (-36, 16))
        b = ((3, 8), (-14, 20), (-28, 20), (-30, 13))
        hb = bez(*[P(*q) for q in a]) + bez(P(-36, 16), P(-37, 10), P(-31, 8), P(-30, 13)) + bez(*[P(*q) for q in b[::-1]])
        form(hb, HORN if s > 0 else BONE_SH, sdx=-1, sdy=-1.5, sh=0.2)
        A = bez(*[P(*q) for q in a], 10); B = bez(*[P(*q) for q in b], 10)
        for t in range(2, 9, 2): stroke([A[t], B[t]], LINE * 0.5)
    for s in (-1, 1):
        ear = [(hx + s * 10, hy + 6), (hx + s * 27, hy + 3), (hx + s * 11, hy - 2)]
        form(ear, FUR_DEVIL, sh=0.15); stroke([(hx + s * 12, hy + 3), (hx + s * 21, hy + 2.5)], LINE * 0.5)


def ohnivec_fb(pose, v):
    back = v == "b"
    g = gait(pose); ph = phase(pose)
    lg = fb_legs(pose, back, 0.3 if pose in ("attack", "windup") else 0)
    rot = 3.5 * math.cos(ph) if g else 0
    shadow(0, 46)
    floor_coins()
    hs = -1 if back else 1
    for s in (-1, 1):
        d, l = lg[s]; sc = 1 + 0.06 * d
        hip = (s * 16, 42); ft = (s * 22, 6 - 2 * d + 8 * l); kn = (s * (25 + l * 2), 23 + 4 * l)
        gcol = FUR_DEVIL_DK if s == -hs else FUR_DEVIL
        tube([hip, kn], 16 * sc, 12 * sc, gcol, sh=0.15); tube([kn, ft], 12 * sc, 8 * sc, gcol, sh=0.15)
        if s == -hs:
            fp = ell(ft[0], ft[1] - 1, 7.5 * sc, 4 * sc, 16)
            form(fp, SKIN_RED, sh=0.2)
            if not back: claws((ft[0], ft[1] - 3), -90, 3, 4.5, 1.4, 14, BONE_DK, curl=s * 20)
        else:
            hf = [(ft[0] - 6 * sc, ft[1] + 3), (ft[0] - 7 * sc, ft[1] - 6), (ft[0] + 7 * sc, ft[1] - 6), (ft[0] + 6 * sc, ft[1] + 3)]
            form(hf, HOOF, sh=0.2)
            stroke([(ft[0], ft[1] - 6), (ft[0], ft[1] - 1)], LINE * 0.8)
            fur = ragged((ft[0] - 8, ft[1] + 4), (ft[0] + 8, ft[1] + 4), 4, 3, 0.4)
            shape(fur + [(ft[0] + 6, ft[1] + 9), (ft[0] - 6, ft[1] + 9)], gcol, LINE * 0.7)
    with T(0, 0, 1, rot=rot):
        tw = 6 * math.sin(ph - 0.9) if g else 0
        if not back:
            tl = bez((-20, 50), (-52, 40 + tw), (-64 - tw, 66), (-54 - tw, 92))
            tube(tl, 5, 2.4, FUR_DEVIL, sh=0.1)
            tip = tl[-1]
            form([(tip[0] - 2, tip[1] - 2), (tip[0] - 8, tip[1] + 4), (tip[0] - 3, tip[1] + 4), (tip[0] - 4, tip[1] + 11),
                  (tip[0] + 1, tip[1] + 6), (tip[0] + 4, tip[1] + 12), (tip[0] + 5, tip[1] + 4), (tip[0] + 10, tip[1] + 5), (tip[0] + 3, tip[1] - 2)], FUR_DEVIL_DK, sh=0.1)
        ps = -hs
        a = -lg[ps][0] if g else 0
        sp, el, hd = (ps * 34, 100), (ps * 46, 80), (ps * (46 - 2 * a), 60 - 3 * a)
        tube([sp, el], 13, 10, FUR_DEVIL_DK, sh=0.15); tube([el, hd], 10, 8, FUR_DEVIL_DK, sh=0.15)
        pouch(hd)
        shape(ell(hd[0], hd[1] + 1, 4.5, 4, 12), FUR_DEVIL_DK, LINE * 0.8)
        sp = (hs * 34, 98)
        if pose == "attack" and back:
            hd = (hs * 40, 74); el = (hs * 48, 88)
            hammer(hd, -90 + hs * 35, 40)
            tube([sp, el], 14, 11, FUR_DEVIL, sh=0.15); tube([el, hd], 11, 9, FUR_DEVIL, sh=0.15)
            shape(ell(hd[0], hd[1], 5.5, 5, 14), FUR_DEVIL_DK, LINE * 0.8)
        body = ell(0, 66, 42, 44, 40)
        form(body, FUR_DEVIL, sdx=-6, sdy=3, sh=0.18)
        fur_edge(body, 3.0, 3.6, skip=lambda x, y: y < 30)
        if back:
            C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
            for s in (-1, 1): hatch(ell(s * 34, 60, 14, 44, 16), 1.8, 60 if s < 0 else 120, 0.45, g=FUR_DEVIL_DK)
            for k in range(7):
                y = 34 + k * 9
                stroke(bez((-24, y), (-10, y - 3), (10, y - 3), (24, y)), LINE * 0.35, g=FUR_DEVIL_DK, alpha=0.7)
            C.restoreState()
            stroke(bez((0, 96), (1, 80), (-1, 60), (0, 36)), LINE * 0.6, g=FUR_DEVIL_DK)
            for s in (-1, 1):
                stroke(bez((s * 34, 66), (s * 20, 60), (s * 8, 60), (0, 62)), LINE * 1.6, g=LEATHER_DK)
                lp = bez((0, 62), (s * 10, 70), (s * 12, 56), (0, 62))
                shape(lp, LEATHER, LINE * 0.6)
                stroke(bez((0, 61), (s * 3, 54), (s * 6, 48), (s * 8 + tw * 0.3, 42)), LINE * 1.4, g=LEATHER_DK)
                stroke(bez((s * 22, 104), (s * 24, 90), (s * 30, 76), (s * 34, 68)), LINE * 1.4, g=LEATHER_DK)
            tl = bez((0, 40), (3 + tw, 18), (30, 6), (42 + tw, 28))
            tube(tl, 5, 2.4, FUR_DEVIL, sh=0.1)
            tip = tl[-1]
            form([(tip[0] - 2, tip[1] - 2), (tip[0] - 8, tip[1] + 4), (tip[0] - 3, tip[1] + 4), (tip[0] - 4, tip[1] + 11),
                  (tip[0] + 1, tip[1] + 6), (tip[0] + 4, tip[1] + 12), (tip[0] + 5, tip[1] + 4), (tip[0] + 10, tip[1] + 5), (tip[0] + 3, tip[1] - 2)], FUR_DEVIL_DK, sh=0.1)
        else:
            belly = ell(0, 64, 28, 32, 30)
            form(belly, SKIN_RED, sdx=-4, sdy=1, sh=0.15)
            apron = [(-18, 98), (18, 98)] + bez((18, 98), (26, 70), (32, 44), (30, 22)) + \
                bez((30, 22), (10, 16), (-10, 16), (-30, 22)) + bez((-30, 22), (-32, 44), (-26, 70), (-18, 98))
            form(apron, LEATHER, sdx=-4, sdy=1.5, sh=0.2)
            stroke([(p[0] * 0.9, p[1] * 0.96 + 3) for p in apron], LINE * 0.35, closed=True, g=LEATHER_DK)
            C.saveState(); C.clipPath(poly(apron), stroke=0, fill=0)
            for s in (-1, 1): hatch(ell(s * 28, 54, 8, 40, 16), 1.8, 60 if s < 0 else 120, 0.45, g=LEATHER_DK)
            for (x, y, r) in ((-12, 40, 3), (14, 66, 2.2), (-6, 76, 2.6), (16, 30, 2)):
                shape(ell(x, y, r, r * 0.8, 12), LEATHER_DK, LINE * 0.5)
                stroke(ell(x, y, r * 1.25, r, 12), LINE * 0.6, closed=True, g=col(FIRE), alpha=0.7)
            C.restoreState()
            for x in (-8, 8):
                stroke(bez((x, 96), (x * 1.1, 70), (x * 1.3, 44), (x * 1.4, 20)), LINE * 0.5, g=LEATHER_DK)
            with T(0, 54):
                shape(ell(0, 0, 6, 6, 20), GOLD, LINE * 0.7)
                stroke(ell(0, 0, 4.2, 4.2, 16), LINE * 0.4, closed=True, g=GOLD_DK)
                stroke([(-2, -2), (0, 2), (2, -2)], LINE * 0.5, g=GOLD_DK)
                glow(0, 0, 10, FIRE, 0.25, 5)
        shoulders = ell(0, 100, 36, 16, 30)
        form(shoulders, FUR_DEVIL, sdx=-3, sdy=2, sh=0.15)
        fur_edge(shoulders, 2.6, 3.4, skip=lambda x, y: y < 96)
        if not back:
            stroke(bez((-18, 98), (-10, 108), (10, 108), (18, 98)), LINE * 1.6, g=LEATHER_DK)
        with T(0, 120 - 1.15 * 118, 1.15):
            ohn_head_fb(back, pose == "attack")
        if not (pose == "attack" and back):
            if pose == "windup":
                el, hd, hang = (hs * 44, 116), (hs * 28, 132), 90 + hs * 35
            elif pose == "attack":
                el, hd, hang = (hs * 40, 88), (hs * 18, 76), -90 - hs * 12
            else:
                a = -lg[hs][0] if g else 0
                el, hd, hang = (hs * 46, 78), (hs * (47 - a), 58 - 3 * a), -90 + hs * (6 + 14 * a)
            if pose in ("attack", "windup"):
                hammer(hd, hang, 36)
            tube([sp, el], 14, 11, FUR_DEVIL, sh=0.15); tube([el, hd], 11, 9, FUR_DEVIL, sh=0.15)
            if pose not in ("attack", "windup"):
                hammer(hd, hang, 40)
            shape(ell(hd[0], hd[1], 5.5, 5, 14), FUR_DEVIL_DK, LINE * 0.8)
        if pose == "attack":
            sx = hs if not back else hs * 1.4
            motion([bez((sx * 30, 160), (sx * 40, 140), (sx * 40, 110), (sx * 30, 86)),
                    bez((sx * 44, 150), (sx * 52, 128), (sx * 52, 100), (sx * 44, 76))])
            for (x, y) in ((-14, 30), (12, 26), (24, 40), (-4, 22), (30, 30)):
                x = x * hs + (hs * 30 if back else 0)
                dot(x, y, 0.8, col(EMBER)); glow(x, y, 2.5, FIRE, 0.5, 4)


def ohn_head_fb(back, open_):
    hx, hy = 0, 118
    if back:
        hd_ = ell(hx, hy + 2, 13.5, 13, 30)
        form(hd_, FUR_DEVIL, sdx=-2, sdy=1, sh=0.18)
        fur_edge(hd_, 2.4, 2.8, skip=lambda x, y: y < hy - 6)
        hatch(hd_, 1.6, 80, 0.4, g=FUR_DEVIL_DK, alpha=0.6)
        ohn_horns_fb(hx, hy)
    else:
        ohn_horns_fb(hx, hy)
        face = bez((-13, hy + 6), (-14, hy + 16), (14, hy + 16), (13, hy + 6)) + bez((13, hy + 6), (13, hy - 4), (9, hy - 10), (8, hy - 16)) + \
            bez((8, hy - 16), (5, hy - 21), (-5, hy - 21), (-8, hy - 16)) + bez((-8, hy - 16), (-9, hy - 10), (-13, hy - 4), (-13, hy + 6))
        form(face, SKIN_RED, sdx=-2, sdy=1, sh=0.2)
        fur_edge(bez((-13, hy + 6), (-14, hy + 16), (14, hy + 16), (13, hy + 6)) + [(0, hy + 2)], 2.4, 2.8)
        beard = [(-4, hy - 19), (4, hy - 19), (2.5, hy - 31), (0.5, hy - 25), (-1.5, hy - 33), (-2.5, hy - 25)]
        form(beard, FUR_DEVIL_DK, sh=0.1)
        for s in (-1, 1):
            shape(ell(s * 2.8, hy - 11, 1.5, 1.2, 10), MOUTH_DK, LINE * 0.5)
            stroke([(s * 2, hy + 4.5), (s * 10, hy + 8)], LINE * 1.3)
            eye(s * 6, hy + 2, 2.2, EYE_ORANGE, slit=True, halo=2.8)
        m = bez((-8, hy - 15), (-3, hy - 17), (3, hy - 17), (8, hy - 15)) + \
            bez((8, hy - 15), (4, hy - (23 if open_ else 19)), (-4, hy - (23 if open_ else 19)), (-8, hy - 15))
        shape(m, MOUTH_DK, LINE * 0.7)
        for tx in (-5, 0, 5):
            shape([(tx - 0.8, hy - 15.8), (tx + 0.8, hy - 15.8), (tx, hy - 18.5)], BONE, LINE * 0.3)
        if open_:
            tg = bez((-3, hy - 19), (-4, hy - 26), (-2, hy - 34), (1, hy - 35)) + bez((1, hy - 35), (4, hy - 32), (4, hy - 25), (3, hy - 19))
            form(tg, col("#c75a68"), sh=0.15)


ohnivec.poses = ALL


# ------------------------------------------------------------------ Ježibaba
def shovel(base, ang, ln=86, embers=False):
    end = pt(base, ang, ln)
    tube([base, end], 3.2, 3.0, WOOD, LINE * 0.8)
    stroke([pt(base, ang, 10), pt(base, ang, ln - 8)], LINE * 0.4, g=WOOD_DK)
    with T(end[0], end[1], 1, rot=ang - 90):
        blade = [(-2, -2)] + bez((-2, -2), (-9, 2), (-11, 8), (-11, 22)) + bez((-11, 22), (-6, 26), (6, 26), (11, 22)) + \
            bez((11, 22), (11, 8), (9, 2), (2, -2))
        form(blade, WOOD_LT, sdx=-2, sdy=0, sh=0.2)
        for x in (-5, 0, 5): stroke([(x, 3), (x * 1.3, 23)], LINE * 0.4, g=WOOD_DK)
        hatch(ell(0, 12, 8, 6, 14), 1.4, 30, 0.4, g=RUST_DK, alpha=0.6)
        if embers:
            glow(0, 16, 14, FIRE, 0.55)
            for (x, y, r) in ((-4, 14, 3), (2, 16, 3.5), (5, 12, 2.5), (-1, 20, 2.6), (-6, 19, 2), (6, 20, 2.2)):
                shape(ell(x, y, r, r * 0.8, 10), col("#c4482a"), LINE * 0.5)
                flat(ell(x + 0.4, y + 0.3, r * 0.5, r * 0.35, 8), EMBER, 0.9)
    return end


def jezibaba(pose):
    pose, v = view_of(pose)
    if v: return jezibaba_fb(pose, v)
    g = gait(pose); ph = phase(pose)
    lean = {"idle": 0, "windup": -3, "attack": 7}.get(pose, 4 + math.sin(ph))
    sk = -3.5 * math.cos(ph - 0.8) if g else 0
    cast_shadow(2, 0, 34, 2.6)
    if g:
        sb, sa = (44 + 9 * g[0][0], 4 + 3 * g[1][1]), 94 + 7 * g[0][0]
    elif pose == "idle":
        sb, sa = (44, 4), 94
    if pose not in ("attack", "windup"):
        shovel(sb, sa, 104)
    if g:
        (ns, nl), (fs, fl) = g
        lf = ((-8, 26), (-7 + 13 * fs, 4 + 6 * fl))
        ln_ = ((8, 26), (9 + 8 * ns, 4 + 4 * nl))
    elif pose == "windup":
        lf, ln_ = ((-8, 26), (-16, 4)), ((8, 26), (14, 4))
    elif pose == "attack":
        lf, ln_ = ((-8, 26), (-20, 4)), ((8, 26), (20, 4))
    else:
        lf, ln_ = ((-8, 26), (-9, 4)), ((8, 26), (11, 4))
    if g and fl > 0:
        kf = ((lf[0][0] + lf[1][0]) / 2 + 6, 15)
        tube([lf[0], kf], 6, 5.5, SKIRT_DK); tube([kf, lf[1]], 5.5, 5, SKIRT_DK)
    else:
        tube(list(lf), 6, 5, SKIRT_DK)
    shoe = [(lf[1][0] - 5, lf[1][1] + 3), (lf[1][0] - 6, lf[1][1] - 3.5), (lf[1][0] + 9, lf[1][1] - 3.5), (lf[1][0] + 7, lf[1][1] + 2)]
    form(shoe, WOOD_DK, sh=0.2)
    for k in range(3): stroke([(lf[1][0] - 4 + k * 4, lf[1][1] + 2), (lf[1][0] - 2 + k * 4, lf[1][1] - 3)], LINE * 0.4)
    bone(ln_[0], (ln_[1][0], ln_[1][1] + 2), 3.2)
    kp = ((ln_[0][0] + ln_[1][0]) / 2 + (3 * nl if g else 0), (ln_[0][1] + ln_[1][1]) / 2 + 2)
    shape(ell(kp[0], kp[1], 3, 2.6, 12), BONE, LINE * 0.7)
    foot = ln_[1]
    for k, a in enumerate((-8, 0, 8)):
        bone((foot[0] + 1, foot[1] - 0.5), (foot[0] + 8 + k, foot[1] - 2 + k * 0.6), 1.3)
    bone((foot[0] - 1, foot[1]), (foot[0] - 5, foot[1] - 2.2), 1.6)
    skirt = [(-20, 66), (18 + lean * 0.5, 66)] + bez((18 + lean * 0.5, 66), (24, 50), (30, 30), (32, 14)) + \
        ragged((32, 14), (-34 + sk, 14), 7, 3, 0.4)[1:-1] + [(-34 + sk, 14)] + bez((-34 + sk, 14), (-32, 32), (-26, 50), (-20, 66))
    form(skirt, SKIRT, sdx=-4, sdy=1.5, sh=0.18)
    C.saveState(); C.clipPath(poly(skirt), stroke=0, fill=0)
    for y0 in (18, 24): fill([(-40, y0), (40, y0), (40, y0 + 2.4), (-40, y0 + 2.4)], RED_DK)
    hatch(ell(-30, 40, 10, 30, 14), 1.8, 60, 0.45, g=SKIRT_DK)
    shape(rrect(-24, 36, 9, 8, 1), CLOTH_SLATE, LINE * 0.5)
    C.restoreState()
    for x0 in (-22, -10, 2):
        stroke(bez((x0, 64), (x0 - 2, 44), (x0 - 5, 30), (x0 - 7, 16)), LINE * 0.5, g=SKIRT_DK)
    ap = [(4, 66), (20 + lean * 0.5, 66)] + bez((20 + lean * 0.5, 66), (26, 48), (30, 30), (30, 20)) + [(8, 20)] + bez((8, 20), (8, 36), (6, 52), (4, 66))
    form(ap, APRON, sdx=-2, sdy=1, sh=0.15)
    for k in range(3): stroke([(10 + k * 5, 24), (12 + k * 5, 22)], LINE * 0.4)
    shape(rrect(14, 34, 9, 7, 1.2), APRON, LINE * 0.6)
    hx, hy = 30 + lean, 92
    top = [(-20, 64)] + bez((-20, 64), (-30, 80), (-26, 100), (-12, 108)) + \
        bez((-12, 108), (0, 114), (12 + lean, 104), (20 + lean, 90)) + bez((20 + lean, 90), (22 + lean, 80), (20 + lean, 72), (18 + lean * 0.5, 66))
    form(top, col("#8a7f6a"), sdx=-3, sdy=1, sh=0.18)
    shawl = bez((-28, 96), (-22, 112), (0, 116), (18 + lean, 98)) + \
        ragged((18 + lean, 98), (2 + lean * 0.5, 72), 4, 4, 0.8)[1:] + \
        ragged((2 + lean * 0.5, 72), (-28, 76), 6, 5, 1.6)[1:] + [(-28, 96)]
    form(shawl, SHAWL, sdx=-3, sdy=1.5, sh=0.18)
    C.saveState(); C.clipPath(poly(shawl), stroke=0, fill=0)
    for k in range(4):
        stroke(bez((-24 + k * 8, 110), (-20 + k * 8, 96), (-16 + k * 7, 86), (-14 + k * 7, 76)), LINE * 0.45, g=col("#4c3858"))
    C.restoreState()
    if pose in ("attack", "windup"):
        fs, fe, fh = ((-6, 94), (6, 84), (14 + lean, 90)) if pose == "attack" else ((-6, 94), (-2, 82), (5, 95))
        tube([fs, fe], 6, 5, SHAWL); tube([fe, fh], 5, 4, HAG)
    nose = bez((hx + 4, hy + 4), (hx + 12, hy + 2), (hx + 18, hy - 4), (hx + 20, hy - 14)) + \
        bez((hx + 20, hy - 14), (hx + 17, hy - 12), (hx + 14, hy - 8), (hx + 9, hy - 4))
    fc = bez((hx - 6, hy + 9), (hx + 2, hy + 10), (hx + 6, hy + 7), (hx + 6, hy + 3)) + \
        bez((hx + 6, hy + 3), (hx + 9, hy - 3), (hx + 8, hy - 6), (hx + 6, hy - 7)) + \
        bez((hx + 6, hy - 7), (hx + 10, hy - 9), (hx + 14, hy - 14), (hx + 13, hy - 20)) + \
        bez((hx + 13, hy - 20), (hx + 8, hy - 18), (hx + 2, hy - 16), (hx - 2, hy - 12)) + \
        bez((hx - 2, hy - 12), (hx - 7, hy - 6), (hx - 8, hy + 2), (hx - 6, hy + 9))
    form(fc, HAG, sdx=-2, sdy=0, sh=0.22)
    stroke(bez((hx + 1, hy - 7), (hx + 3, hy - 8), (hx + 5, hy - 8.5), (hx + 7, hy - 7)), LINE * 0.8)
    shape([(hx + 4, hy - 7.7), (hx + 5.4, hy - 7.9), (hx + 4.8, hy - 5.2)], BONE, LINE * 0.35)
    for k in range(3):
        stroke(bez((hx - 4 + k, hy - 2 - k * 3), (hx - 2 + k, hy - 3 - k * 3), (hx + k, hy - 3 - k * 3), (hx + 1 + k, hy - 2 - k * 3)), LINE * 0.35, alpha=0.6)
    form(nose, HAG, sh=0.15)
    shape(ell(hx + 15, hy - 4, 1.4, 1.2, 10), HAG_DK, LINE * 0.4)
    shape(ell(hx + 0, hy + 4, 3, 2.2, 12), HAG_DK, 0)
    eye(hx + 1.5, hy + 4, 1.7, EYE_GREEN, halo=3.0)
    stroke(bez((hx - 3, hy + 8), (hx, hy + 9), (hx + 3, hy + 8.5), (hx + 6, hy + 6)), LINE * 1.2, g=HAIR_GREY)
    stroke(bez((hx - 3, hy + 8), (hx, hy + 9), (hx + 3, hy + 8.5), (hx + 6, hy + 6)), LINE * 0.4)
    for k in range(4):
        stroke(bez((hx - 6 - k, hy + 8), (hx - 6 - k * 2, hy), (hx - 4 - k * 3, hy - 8), (hx - 8 - k * 3, hy - 16)), LINE * 0.5, g=HAIR_GREY)
    sc = bez((hx + 5, hy + 8), (hx + 6, hy + 18), (hx - 6, hy + 22), (hx - 14, hy + 16)) + \
        bez((hx - 14, hy + 16), (hx - 26, hy + 8), (hx - 30, hy - 6), (hx - 40, hy - 18)) + \
        [(hx - 30, hy - 14)] + bez((hx - 30, hy - 14), (hx - 22, hy - 8), (hx - 14, hy - 8), (hx - 10, hy - 10)) + \
        bez((hx - 10, hy - 10), (hx - 8, hy - 2), (hx - 9, hy + 6), (hx - 5, hy + 10)) + \
        bez((hx - 5, hy + 10), (hx, hy + 12), (hx + 3, hy + 11), (hx + 5, hy + 8))
    form(sc, SCARF, sdx=-2, sdy=-1, sh=0.2)
    C.saveState(); C.clipPath(poly(sc), stroke=0, fill=0)
    for i in range(-50, 12, 5):
        for j in range(-24, 26, 5):
            x, y = hx + i + (2.5 if (j // 5) % 2 else 0), hy + j
            dot(x, y, 0.8, col("#f0e2c0")); dot(x + 1.2, y + 0.6, 0.5, col("#e8c048"))
    C.restoreState()
    knot = [(hx - 12, hy - 6), (hx - 6, hy - 10), (hx - 8, hy - 18), (hx - 12, hy - 14), (hx - 16, hy - 20), (hx - 18, hy - 12)]
    form(knot, SCARF, sh=0.15)
    if pose == "attack":
        sh0, el, hd = (8 + lean, 96), (22 + lean, 86), (28 + lean, 93)
    elif g:
        sh0, el, hd = (8 + lean, 96), (20 + lean, 78), pt(sb, sa, 70)
    elif pose == "windup":
        sh0, el, hd = (8 + lean, 96), (22, 80), (14, 89)
    else:
        sh0, el, hd = (8, 96), (18, 76), (40, 70)
    if pose == "attack":
        shovel((-8, 84), 12, 46, embers=True)
    elif pose == "windup":
        shovel((21, 84), 145, 52, embers=True)
    tube([sh0, el], 7, 6, SHAWL); tube([el, hd], 6, 4.6, HAG)
    shape(ell(hd[0], hd[1], 3.8, 3.2, 12), HAG, LINE * 0.8)
    claws(pt(hd, 90, 1), 100, 3, 5, 1.3, 10, HAG_DK, curl=-70)
    if pose == "windup":
        shape(ell(fh[0], fh[1], 3.4, 3.0, 12), HAG, LINE * 0.8)
    if pose == "attack":
        shape(ell(fh[0], fh[1], 3.4, 3.0, 12), HAG, LINE * 0.8)
        motion([bez((-10, 120), (14, 128), (36, 128), (56, 120)), bez((-6, 70), (16, 66), (36, 70), (52, 80))])
        for (x, y) in ((64, 116), (58, 124), (66, 108), (50, 128), (62, 126)):
            glow(x, y, 2.6, FIRE, 0.6, 4); dot(x, y, 0.8, col(EMBER))


def baba_scarf_dots(clip, x0, y0, x1, y1):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    for i in range(int(x0), int(x1), 5):
        for j in range(int(y0), int(y1), 5):
            x = i + (2.5 if ((j - int(y0)) // 5) % 2 else 0)
            dot(x, j, 0.8, col("#f0e2c0")); dot(x + 1.2, j + 0.6, 0.5, col("#e8c048"))
    C.restoreState()


def jezibaba_fb(pose, v):
    back = v == "b"
    g = gait(pose); ph = phase(pose)
    lg = fb_legs(pose, back, 0.3 if pose == "attack" else 0)
    hs = -1 if back else 1
    rot = (3 * math.cos(ph) - 1) * hs if g else 0
    sk = 3 * math.sin(ph - 0.8) if g else 0
    cast_shadow(0, 0, 34, 2.6)
    if pose not in ("attack", "windup"):
        lift = 4 * lg[hs][1] if g else 0
        shovel((hs * 35, 4 + lift), 90 - hs * 3, 104)
    for s in (-1, 1):
        d, l = lg[s]
        bony = s == hs
        if bony: d *= 0.6
        sc = 1 + 0.06 * d
        hip = (s * 8, 26); ft = (s * 10, 4 - 2 * d + (4 if bony else 6) * l)
        if bony:
            bone(hip, (ft[0], ft[1] + 2), 3.2 * sc)
            shape(ell((hip[0] + ft[0]) / 2, (hip[1] + ft[1]) / 2 + 2, 3, 2.6, 12), BONE, LINE * 0.7)
            if back:
                bone((ft[0], ft[1]), (ft[0], ft[1] - 2), 1.8)
            else:
                for k in (-1, 0, 1):
                    bone((ft[0] + k * 0.8, ft[1]), (ft[0] + k * 3, ft[1] - 4.5), 1.3)
        else:
            kn = (s * (9 + 2 * l), 15 + 3 * l)
            tube([hip, kn], 6, 5.5, SKIRT_DK); tube([kn, ft], 5.5, 5, SKIRT_DK)
            clog = ell(ft[0], ft[1] - 0.5, 5.6 * sc, 3.4 * sc, 16)
            form(clog, WOOD_DK, sh=0.2)
            if not back:
                stroke(ell(ft[0], ft[1] - 1.5, 3.4 * sc, 1.6 * sc, 12, 200, 340), LINE * 0.4)
    with T(0, 0, 1, rot=rot):
        if pose == "attack" and back:
            base = (hs * 14, 96)
            shovel(base, 90 - hs * 45, 24, embers=True)
            for (x, y) in ((40, 104), (54, 112), (60, 100), (46, 122)):
                glow(x * hs, y, 2.6, FIRE, 0.6, 4); dot(x * hs, y, 0.8, col(EMBER))
        hy = 104 if back else 94
        if back:
            hood = ell(0, hy + 4, 15, 15, 30)
            form(hood, SCARF, sdx=-2, sdy=-1, sh=0.2)
            baba_scarf_dots(hood, -16, hy - 12, 16, hy + 20)
        skirt = [(-20, 66), (20, 66)] + bez((20, 66), (26, 50), (32, 30), (34 + sk, 14)) + \
            ragged((34 + sk, 14), (-34 + sk, 14), 8, 3, 0.4)[1:-1] + [(-34 + sk, 14)] + bez((-34 + sk, 14), (-32, 30), (-26, 50), (-20, 66))
        form(skirt, SKIRT, sdx=-4, sdy=1.5, sh=0.18)
        C.saveState(); C.clipPath(poly(skirt), stroke=0, fill=0)
        for y0 in (18, 24): fill([(-40, y0), (40, y0), (40, y0 + 2.4), (-40, y0 + 2.4)], RED_DK)
        for s in (-1, 1): hatch(ell(s * 32, 40, 10, 30, 14), 1.8, 60 if s < 0 else 120, 0.45, g=SKIRT_DK)
        if back: shape(rrect(-14, 34, 9, 8, 1), CLOTH_SLATE, LINE * 0.5)
        C.restoreState()
        for x0 in (-20, -8, 8, 20):
            stroke(bez((x0 * 0.7, 64), (x0 * 0.8, 44), (x0 * 0.9, 30), (x0 + sk * 0.6, 16)), LINE * 0.5, g=SKIRT_DK)
        if back:
            for s in (-1, 1):
                shape(bez((0, 64), (s * 8, 70), (s * 9, 58), (0, 64)), APRON, LINE * 0.6)
                stroke(bez((0, 63), (s * 2, 56), (s * 4, 50), (s * 5 + sk * 0.5, 44)), LINE * 1.4, g=APRON)
                stroke(bez((0, 63), (s * 2, 56), (s * 4, 50), (s * 5 + sk * 0.5, 44)), LINE * 0.4)
        else:
            ap = [(-14, 66), (14, 66)] + bez((14, 66), (16, 48), (18, 30), (18, 20)) + [(-18, 20)] + bez((-18, 20), (-18, 30), (-16, 48), (-14, 66))
            form(ap, APRON, sdx=-2, sdy=1, sh=0.15)
            for k in range(5): stroke([(-12 + k * 6, 24), (-10 + k * 6, 22)], LINE * 0.4)
            shape(rrect(3, 34, 9, 7, 1.2), APRON, LINE * 0.6)
        top = [(-20, 64)] + bez((-20, 64), (-30, 80), (-28, 100), (-16, 110)) + bez((-16, 110), (-6, 117), (6, 117), (16, 110)) + \
            bez((16, 110), (28, 100), (30, 80), (20, 64))
        form(top, col("#8a7f6a"), sdx=-3, sdy=1, sh=0.18)
        low = 58 if back else 70
        shawl = bez((-31, 98), (-26, 118), (26, 118), (31, 98)) + ragged((31, 98), (22, 78), 3, 4, 0.8)[1:] + \
            ragged((22, 78), (0, low), 3, 4, 1.2)[1:] + ragged((0, low), (-22, 78), 3, 4, 1.6)[1:] + ragged((-22, 78), (-31, 98), 3, 4, 2.0)[1:]
        form(shawl, SHAWL, sdx=-3, sdy=1.5, sh=0.18)
        C.saveState(); C.clipPath(poly(shawl), stroke=0, fill=0)
        for k in range(-3, 4):
            stroke(bez((k * 8, 116), (k * 7, 104), (k * 5, 90), (k * 3, low + 4)), LINE * 0.45, g=col("#4c3858"))
        C.restoreState()
        if back:
            for s in (-1, 1):
                tl = [(s * 2, hy - 6), (s * 9, hy - 10), (s * 7 + sk, hy - 26), (s * 3 + sk, hy - 22)]
                form(tl, SCARF, sh=0.15)
                baba_scarf_dots(tl, -12 + sk, hy - 28, 12 + sk, hy - 4)
            form(ell(0, hy - 6, 4.5, 3.5, 14), SCARF, sh=0.2)
        else:
            hood = bez((-14, hy + 2), (-17, hy + 19), (17, hy + 19), (14, hy + 2)) + bez((14, hy + 2), (15, hy - 8), (12, hy - 14), (8, hy - 17)) + \
                [(-8, hy - 17)] + bez((-8, hy - 17), (-12, hy - 14), (-15, hy - 8), (-14, hy + 2))
            form(hood, SCARF, sdx=-2, sdy=-1, sh=0.2)
            baba_scarf_dots(hood, -18, hy - 18, 18, hy + 20)
            fc = bez((-8, hy + 9), (-10, hy), (-8, hy - 10), (-3, hy - 16)) + [(0, hy - 19)] + \
                bez((3, hy - 16), (8, hy - 10), (10, hy), (8, hy + 9)) + bez((8, hy + 9), (4, hy + 11), (-4, hy + 11), (-8, hy + 9))
            form(fc, HAG, sdx=-1.5, sdy=0, sh=0.22)
            for s in (-1, 1):
                for k in range(3):
                    stroke(bez((s * (2 + k * 2), hy + 10), (s * (5 + k * 2), hy + 6), (s * (7 + k), hy + 2), (s * (8 + k), hy - 3)), LINE * 0.5, g=HAIR_GREY)
                shape(ell(s * 4, hy + 3, 2.6, 2.0, 12), HAG_DK, 0)
                eye(s * 4, hy + 3, 1.6, EYE_GREEN, halo=3.0)
                stroke([(s * 1.5, hy + 5), (s * 7, hy + 7)], LINE * 0.9, g=HAIR_GREY)
                for k in range(2):
                    stroke(bez((s * 3, hy - 1 - k * 3), (s * 4, hy - 2 - k * 3), (s * 6, hy - 2 - k * 3), (s * 7, hy - 1 - k * 3)), LINE * 0.35, alpha=0.6)
            stroke(bez((-4, hy - 12.5), (-2, hy - 14), (2, hy - 14), (4, hy - 12.5)), LINE * 0.8)
            shape([(1, hy - 13.6), (2.2, hy - 13.6), (1.6, hy - 11.4)], BONE, LINE * 0.35)
            nose = bez((-1.6, hy + 4), (-2.6, hy - 2), (-3.2, hy - 8), (-1.2, hy - 12)) + bez((-1.2, hy - 12), (1, hy - 13), (3, hy - 11), (2, hy - 8)) + \
                bez((2, hy - 8), (2, hy - 2), (1.6, hy + 2), (1.6, hy + 4))
            form(nose, HAG, sh=0.15)
            shape(ell(-2.2, hy - 6, 1.1, 1.0, 10), HAG_DK, LINE * 0.4)
        if pose == "windup":
            base = (hs * 20, 100)
            shovel(base, 90 + hs * 60, 34, embers=True)
            for hd in (base, pt(base, 90 + hs * 60, 14)):
                shape(ell(hd[0], hd[1], 3.8, 3.2, 12), HAG, LINE * 0.8)
        elif pose == "attack" and not back:
            base = (hs * 16, 104)
            tube([(hs * 22, 100), base], 6, 5, SHAWL)
            shovel(base, -90 - hs * 12, 46, embers=True)
            for hd in (base, pt(base, -90 - hs * 12, 12)):
                shape(ell(hd[0], hd[1], 3.8, 3.2, 12), HAG, LINE * 0.8)
            motion([bez((-28, 118), (-32, 102), (-30, 86), (-24, 70)), bez((30, 118), (34, 102), (32, 86), (26, 70))])
            for (x, y) in ((-20, 40), (14, 34), (26, 48), (-8, 28), (4, 46)):
                glow(x, y, 2.6, FIRE, 0.6, 4); dot(x, y, 0.8, col(EMBER))
        elif pose != "attack":
            a = -lg[hs][0] if g else 0
            hd = (hs * 34, 72 + 2 * a)
            tube([(hs * 24, 100), (hs * 31, 84)], 7, 6, SHAWL); tube([(hs * 31, 84), hd], 6, 4.6, HAG)
            shape(ell(hd[0], hd[1], 3.8, 3.2, 12), HAG, LINE * 0.8)
            claws(pt(hd, 90, 1), 90 - hs * 80, 3, 5, 1.3, 10, HAG_DK, curl=hs * 70)
            if not back:
                shape(ell(-hs * 7, 84, 3.6, 3.0, 12), HAG, LINE * 0.8)
                claws((-hs * 7, 83), -90, 3, 4, 1.2, 10, HAG_DK, curl=-hs * 50)


jezibaba.poses = ALL


# ------------------------------------------------------------------ Chaloupka
def chicken_foot(p, spread, lift=False):
    toes = [(spread[0], 22, 0), (spread[1], 18, 1), (spread[2], 14, 2)]
    for a, ln, k in toes:
        q1 = pt(p, a, ln * 0.55); q2 = pt(q1, a + (-14 if lift else -4), ln * 0.45)
        tube([p, q1, q2], 7 - k, 4.5 - k * 0.6, CHICKEN, LINE * 0.8, sh=0.12)
        for t in (0.35, 0.65):
            m = pt(p, a, ln * t); stroke([pt(m, a + 90, 2.5), pt(m, a - 90, 2.5)], LINE * 0.4, g=CHICKEN_DK)
        tal = [pt(q2, a + 90, 2), pt(q2, a - 4, 7), pt(q2, a - 90, 2)]
        form(tal, BONE_DK, sh=0)
    bk = pt(p, spread[3], 10)
    tube([p, bk], 6, 4, CHICKEN, LINE * 0.8, sh=0.1)
    form([pt(bk, spread[3] + 90, 1.8), pt(bk, spread[3] + 10, 6), pt(bk, spread[3] - 90, 1.8)], BONE_DK, sh=0)


def hut():
    W = 48
    logs = [(-W, 0), (W, 0), (W, 58), (-W, 58)]
    form(logs, WOOD, sdx=-6, sdy=0, sh=0.2)
    C.saveState(); C.clipPath(poly(logs), stroke=0, fill=0)
    for i in range(8):
        y = i * 7.4
        stroke(bez((-W, y + 7.4), (-20, y + 8), (20, y + 7), (W, y + 7.4)), LINE * 0.7)
        stroke(bez((-W, y + 2.4), (-10, y + 2.8), (10, y + 2), (W, y + 2.5)), LINE * 0.35, g=WOOD_DK)
    hatch([(-W, 0), (-W + 14, 0), (-W + 14, 58), (-W, 58)], 1.7, 60, 0.45, g=WOOD_DK)
    for (x, y, r) in ((-30, 4, 7), (36, 50, 6), (24, 3, 5)):
        flat(ell(x, y, r * 1.4, r * 0.7, 16), MOSS.hex, 0.75)
    C.restoreState()
    for s in (-1, 1):
        for i in range(8):
            y = i * 7.4 + 3.7
            shape(ell(s * (W + 3), y, 4.0, 3.6, 14), WOOD_LT, LINE * 0.7)
            stroke(ell(s * (W + 3), y, 2.0, 1.8, 10), LINE * 0.35, closed=True, g=WOOD_DK)
    door = [(-34, 0), (-14, 0), (-14, 36)] + bez((-14, 36), (-15, 42), (-33, 42), (-34, 36))
    form(door, WOOD_DK, sh=0.25)
    for x in (-29, -24, -19): stroke([(x, 1), (x, 39)], LINE * 0.45)
    for y in (8, 28):
        stroke([(-34, y), (-20, y)], LINE * 2.2, g=IRON); stroke([(-34, y), (-20, y)], LINE * 0.4)
    shape(ell(-17, 20, 1.6, 1.6, 10), IRON, LINE * 0.5)
    flat([(-14, 1), (-12, 1), (-12, 34), (-14, 34)], EMBER, 0.7)
    glow(-13, 18, 8, FIRE, 0.35, 5)
    skull(-24, 49, 4.2, eyes=EYE_ORANGE)
    wx0, wy0, ww, wh = 6, 18, 28, 24
    glow(wx0 + ww / 2, wy0 + wh / 2, 34, FIRE, 0.45)
    win = rrect(wx0, wy0, ww, wh, 1.5)
    shape(win, col("#f2a03a"), LINE)
    flat(rrect(wx0 + 3, wy0 + 3, ww - 6, wh - 6, 1), EMBER, 0.9)
    flat(ell(wx0 + 16, wy0 + 11, 5, 4, 14), "#fff4c0", 0.8)
    stroke([(wx0 + ww / 2, wy0), (wx0 + ww / 2, wy0 + wh)], LINE * 1.8, g=WOOD_DK)
    stroke([(wx0, wy0 + wh / 2), (wx0 + ww, wy0 + wh / 2)], LINE * 1.8, g=WOOD_DK)
    for s in (-1, 1):
        x = wx0 - 9 if s < 0 else wx0 + ww
        sh_ = [(x, wy0 - 1), (x + 9, wy0), (x + 9, wy0 + wh), (x, wy0 + wh + (2 if s > 0 else -1))]
        form(sh_, WOOD_LT, sh=0.15)
        for k in (1, 2): stroke([(x + 3 * k, wy0 + 1), (x + 3 * k, wy0 + wh - 1)], LINE * 0.35, g=WOOD_DK)
    shape(rrect(wx0 - 2, wy0 - 3, ww + 4, 3, 0.8), WOOD_LT, LINE * 0.6)
    ch = [(26, 74), (38, 74), (38, 112), (26, 112)]
    form(ch, ROCK, sh=0.2)
    for y in (82, 90, 98, 106):
        stroke([(26, y), (38, y)], LINE * 0.45)
        stroke([(30 + (y % 16) / 2, y), (30 + (y % 16) / 2, y + 8)], LINE * 0.35)
    shape([(24, 112), (40, 112), (40, 115), (24, 115)], ROCK_DK, LINE * 0.7)
    glow(32, 116, 6, FIRE, 0.4, 4)
    for (x, y, r) in ((31, 119, 3.5), (25, 124, 4.2), (18, 127, 4.6)):
        fill(ell(x, y, r, r * 0.8, 16), SMOKE)
        stroke(ell(x, y, r, r * 0.8, 16, 20, 200), LINE * 0.4, alpha=0.5)
    roof = [(-62, 54), (62, 54)] + bez((62, 54), (40, 76), (14, 100), (0, 104)) + bez((0, 104), (-14, 100), (-40, 76), (-62, 54))
    eave = ragged((62, 54), (-62, 54), 14, 4, 0.9)
    roofp = roof[:1] + eave[::-1][:-1] + roof[2:]
    form(roofp, THATCH, sdx=-5, sdy=-2, sh=0.2)
    C.saveState(); C.clipPath(poly(roofp), stroke=0, fill=0)
    for i in range(30):
        x = -60 + i * 4.1
        top = (0, 104)
        stroke([(x, 50), (x * 0.55 + top[0] * 0.45, 54 + (104 - 54) * 0.45 + abs(x) * -0.25)], LINE * 0.4, g=THATCH_DK)
    for (x, y, r) in ((-30, 66, 9), (20, 84, 7), (40, 62, 8), (-6, 94, 5)):
        flat(ell(x, y, r * 1.5, r * 0.7, 16, rot=20), MOSS.hex, 0.8)
    hatch([(-62, 50), (62, 50), (62, 62), (-62, 62)], 1.8, 70, 0.45, g=THATCH_DK)
    C.restoreState()
    stroke(bez((-4, 102), (-2, 104), (2, 104), (4, 102)), LINE * 2.2, g=THATCH_DK)
    shape(rrect(-6, 70, 12, 12, 1), col("#f2a03a"), LINE * 0.8)
    flat(ell(0, 76, 3.5, 3.5, 14), EMBER, 0.9)
    glow(0, 76, 12, FIRE, 0.35, 5)
    stroke([(0, 70), (0, 82)], LINE * 1.0, g=WOOD_DK)
    with T(0, 108, 0.9):
        skull(0, 0, 5.5, eyes=EYE_ORANGE)
    shape([(-2, 102), (2, 102), (1, 106), (-1, 106)], WOOD_DK, LINE * 0.5)


def chaloupka(pose):
    pose, v = view_of(pose)
    if v: return chaloupka_fb(pose, v)
    if pose == "attack":
        hip, jt, ft, tilt = (-6, 90), (-26, 62), (40, 58), 11
        spread = (10, 30, -10, 190)
    elif pose == "walk":
        hip, jt, ft, tilt = (0, 82), (-26, 50), (22, 9), -6
        spread = (0, 12, -8, 182)
    elif pose == "walk2":
        hip, jt, ft, tilt = (2, 74), (-30, 40), (2, 9), -2
        spread = (2, 12, -6, 182)
    elif pose == "walk3":
        hip, jt, ft, tilt = (10, 92), (-6, 58), (-20, 10), 6
        spread = (-12, 0, -22, 172)
    elif pose == "walk4":
        hip, jt, ft, tilt = (6, 98), (-18, 64), (6, 28), 2
        spread = (-34, -18, -50, 150)
    elif pose == "windup":
        hip, jt, ft, tilt = (-4, 72), (-32, 42), (8, 9), -10
        spread = (4, 14, -6, 184)
    else:
        hip, jt, ft, tilt = (0, 88), (-18, 52), (6, 9), 0
        spread = (2, 12, -6, 182)
    shadow({"attack": -4, "walk3": 4, "walk4": 4}.get(pose, ft[0]), 46)
    if pose not in ("attack", "walk4"):
        for (x, s) in ((-22, 1), (18, -1)):
            stroke([(ft[0] + x, 2), (ft[0] + x + s * 6, 6)], LINE * 0.5, alpha=0.5)
    tube([jt, ft], 14, 10, CHICKEN, sh=0.15)
    a = math.degrees(math.atan2(ft[1] - jt[1], ft[0] - jt[0]))
    L = math.hypot(ft[0] - jt[0], ft[1] - jt[1])
    for k in range(1, 12):
        m = pt(jt, a, L * k / 12)
        stroke(ell(m[0], m[1], 6.4, 2.2, 12, 180, 360, rot=a + 90), LINE * 0.45, g=CHICKEN_DK)
    sp = pt(jt, a, L * 0.78)
    form([pt(sp, a + 90, 3), pt(pt(sp, a + 150, 9), a + 90, 0), pt(sp, a + 90, 1) if False else pt(sp, a, 3)], BONE_DK, sh=0)
    chicken_foot(ft, spread, lift=pose in ("attack", "walk4"))
    shape(ell(jt[0], jt[1], 7.5, 7, 16), CHICKEN, LINE * 0.9)
    thigh = [pt(hip, 0, 16), pt(hip, 180, 16)]
    tb = math.degrees(math.atan2(jt[1] - hip[1], jt[0] - hip[0]))
    th = [pt(hip, tb + 90, 17)] + bez(pt(hip, tb + 90, 17), pt(pt(hip, tb, 18), tb + 90, 18), pt(jt, tb + 90, 9), pt(jt, tb + 90, 6)) + \
        bez(pt(jt, tb - 90, 6), pt(jt, tb - 90, 9), pt(pt(hip, tb, 18), tb - 90, 18), pt(hip, tb - 90, 17))
    form(th, FEATHER, sdx=-3, sdy=1, sh=0.2)
    C.saveState(); C.clipPath(poly(th), stroke=0, fill=0)
    for k in range(9):
        q = pt(hip, tb, 6 + k * 4.5)
        for s in (-1, 0, 1):
            c = pt(q, tb + 90, s * 8)
            stroke(ell(c[0], c[1], 5, 3.5, 10, 200, 340, rot=tb + 90), LINE * 0.45, g=FEATHER_DK)
    C.restoreState()
    with T(hip[0], hip[1], 1, rot=tilt):
        fr = ragged((48, 4), (-48, 4), 12, 10, 2.1)
        form(fr + [(-46, 8), (46, 8)], FEATHER, sh=0.15)
        with T(0, 4, 0.92):
            hut()
    if pose == "attack":
        motion([bez((10, 40), (24, 34), (40, 34), (56, 40)), bez((4, 52), (20, 46), (34, 46), (48, 50))])
    elif pose == "walk":
        motion([bez((-64, 110), (-70, 100), (-72, 90), (-70, 80)), bez((-60, 70), (-66, 64), (-70, 56), (-70, 46))])
    if pose in ("walk", "walk3"):
        dust(ft[0] + (-26 if pose == "walk3" else 0), pose == "walk3")


def dust(x, behind):
    for (dx, dy, r) in (((-6, 5, 4), (-13, 8, 3), (6, 4, 3.4)) if not behind else ((-6, 6, 4.2), (-14, 10, 3.4), (-20, 6, 2.6))):
        fill(ell(x + dx, dy, r, r * 0.8, 14), SMOKE)
        stroke(ell(x + dx, dy, r, r * 0.8, 14, 20, 200), LINE * 0.4, alpha=0.4)


def chicken_foot_fb(p, back, curl=0.0, sc=1.0):
    k = 1 - 0.45 * curl
    if back:
        toes = [(-90, 6, 7, 0), (-172 + curl * 60, 14, 6, 1), (-8 - curl * 60, 14, 6, 1)]
    else:
        toes = [(-158 + curl * 50, 17, 6.5, 1), (-22 - curl * 50, 17, 6.5, 1), (-90, 8, 7.5, 0)]
    for a, ln, w, _ in toes:
        ln *= k * sc; w *= sc
        q1 = pt(p, a, ln * 0.6); q2 = pt(q1, a + (0 if a == -90 else (12 if a < -90 else -12)) * (1 + curl), ln * 0.4)
        tube([p, q1, q2], w, w * 0.65, CHICKEN, LINE * 0.8, sh=0.12)
        m = pt(p, a, ln * 0.45); stroke([pt(m, a + 90, w * 0.4), pt(m, a - 90, w * 0.4)], LINE * 0.4, g=CHICKEN_DK)
        form([pt(q2, a + 90, 2 * sc), pt(q2, a, 6 * sc), pt(q2, a - 90, 2 * sc)], BONE_DK, sh=0)


def hut_end(back):
    D = 36
    if back:
        ch = [(-18, 80), (-6, 80), (-6, 114), (-18, 114)]
        form(ch, ROCK, sh=0.2)
        shape([(-20, 112), (-4, 112), (-4, 115), (-20, 115)], ROCK_DK, LINE * 0.7)
    wall = [(-D, 0), (D, 0), (D, 58), (-D, 58)]
    form(wall, WOOD, sdx=-5, sdy=0, sh=0.2)
    C.saveState(); C.clipPath(poly(wall), stroke=0, fill=0)
    for i in range(8):
        y = i * 7.4
        stroke(bez((-D, y + 7.4), (-12, y + 8), (12, y + 7), (D, y + 7.4)), LINE * 0.7)
        stroke(bez((-D, y + 2.4), (-6, y + 2.8), (6, y + 2), (D, y + 2.5)), LINE * 0.35, g=WOOD_DK)
    for s in (-1, 1): hatch([(s * D, 0), (s * (D - 10), 0), (s * (D - 10), 58), (s * D, 58)], 1.7, 60, 0.45, g=WOOD_DK)
    for (x, y, r) in ((-20, 4, 6), (24, 48, 5), (14, 3, 4)) if not back else ((18, 5, 7), (-26, 44, 6), (-6, 2, 5)):
        flat(ell(x, y, r * 1.4, r * 0.7, 16), MOSS.hex, 0.75)
    C.restoreState()
    for s in (-1, 1):
        for i in range(8):
            y = i * 7.4 + 3.7
            shape(ell(s * (D + 3), y, 4.0, 3.6, 14), WOOD_LT, LINE * 0.7)
            stroke(ell(s * (D + 3), y, 2.0, 1.8, 10), LINE * 0.35, closed=True, g=WOOD_DK)
    if back:
        sh_ = rrect(-9, 20, 18, 20, 1.2)
        form(sh_, WOOD_LT, sh=0.15)
        for x in (-3, 3): stroke([(x, 21), (x, 39)], LINE * 0.4, g=WOOD_DK)
        stroke([(-9, 30), (9, 30)], LINE * 1.6, g=IRON); stroke([(-9, 30), (9, 30)], LINE * 0.4)
        flat([(-9, 20), (9, 20), (9, 21.5), (-9, 21.5)], EMBER, 0.6)
        for (x, y) in ((-24, 30), (24, 26)):
            tube([(x, 44), (x, 38)], 0.8, 0.8, ROOT, LINE * 0.4, sh=0)
            bone((x - 2, 36), (x + 2, 32), 1.4)
    else:
        wx0, wy0, ww, wh = -12, 18, 24, 22
        glow(0, wy0 + wh / 2, 30, FIRE, 0.45)
        shape(rrect(wx0, wy0, ww, wh, 1.5), col("#f2a03a"), LINE)
        flat(rrect(wx0 + 3, wy0 + 3, ww - 6, wh - 6, 1), EMBER, 0.9)
        flat(ell(2, wy0 + 10, 4.5, 3.6, 14), "#fff4c0", 0.8)
        stroke([(0, wy0), (0, wy0 + wh)], LINE * 1.8, g=WOOD_DK)
        stroke([(wx0, wy0 + wh / 2), (wx0 + ww, wy0 + wh / 2)], LINE * 1.8, g=WOOD_DK)
        for s in (-1, 1):
            x = wx0 - 8 if s < 0 else wx0 + ww
            form([(x, wy0 - 1), (x + 8, wy0), (x + 8, wy0 + wh), (x, wy0 + wh + (2 if s > 0 else -1))], WOOD_LT, sh=0.15)
            for k in (1, 2): stroke([(x + 2.7 * k, wy0 + 1), (x + 2.7 * k, wy0 + wh - 1)], LINE * 0.35, g=WOOD_DK)
        shape(rrect(wx0 - 2, wy0 - 3, ww + 4, 3, 0.8), WOOD_LT, LINE * 0.6)
        skull(-24, 49, 3.8, eyes=EYE_ORANGE)
    roof = [(-52, 54), (52, 54)] + bez((52, 54), (34, 76), (12, 100), (0, 104)) + bez((0, 104), (-12, 100), (-34, 76), (-52, 54))
    eave = ragged((52, 54), (-52, 54), 12, 4, 0.9)
    roofp = roof[:1] + eave[::-1][:-1] + roof[2:]
    form(roofp, THATCH, sdx=-5, sdy=-2, sh=0.2)
    C.saveState(); C.clipPath(poly(roofp), stroke=0, fill=0)
    for i in range(26):
        x = -52 + i * 4.1
        stroke([(x, 50), (x * 0.55, 54 + 50 * 0.45 - abs(x) * 0.25)], LINE * 0.4, g=THATCH_DK)
    for (x, y, r) in (((-24, 66, 8), (18, 84, 6), (32, 62, 7)) if not back else ((22, 68, 8), (-16, 86, 6), (-34, 60, 7))):
        flat(ell(x, y, r * 1.5, r * 0.7, 16, rot=20), MOSS.hex, 0.8)
    hatch([(-52, 50), (52, 50), (52, 62), (-52, 62)], 1.8, 70, 0.45, g=THATCH_DK)
    C.restoreState()
    if not back:
        shape(rrect(-5, 70, 10, 10, 1), col("#f2a03a"), LINE * 0.8)
        flat(ell(0, 75, 3, 3, 14), EMBER, 0.9)
        glow(0, 75, 10, FIRE, 0.35, 5)
        stroke([(0, 70), (0, 80)], LINE * 1.0, g=WOOD_DK)
        ch = [(14, 82), (26, 82), (26, 112), (14, 112)]
        form(ch, ROCK, sh=0.2)
        for y in (90, 98, 106): stroke([(14, y), (26, y)], LINE * 0.45)
        shape([(12, 112), (28, 112), (28, 115), (12, 115)], ROCK_DK, LINE * 0.7)
    cx = 20 if not back else -12
    glow(cx, 116, 6, FIRE, 0.4, 4)
    for (x, y, r) in ((cx - 1, 119, 3.5), (cx - 7, 124, 4.2), (cx - 14, 127, 4.6)):
        fill(ell(x, y, r, r * 0.8, 16), SMOKE)
        stroke(ell(x, y, r, r * 0.8, 16, 20, 200), LINE * 0.4, alpha=0.5)
    stroke(bez((-4, 102), (-2, 104), (2, 104), (4, 102)), LINE * 2.2, g=THATCH_DK)
    with T(0, 108, 0.9):
        skull(0, 0, 5.5, eyes=None if back else EYE_ORANGE)
    shape([(-2, 102), (2, 102), (1, 106), (-1, 106)], WOOD_DK, LINE * 0.5)


def chaloupka_fb(pose, v):
    back = v == "b"
    hip, jt, fy, rot, curl, fsc = {
        "idle": (88, 52, 9, 0, 0, 1.0), "walk": (82, 48, 9, -4, 0, 1.0), "walk2": (74, 40, 9, -1, 0, 1.0),
        "walk3": (92, 58, 10, 4, 0, 1.0), "walk4": (98, 64, 28, 1, 1, 0.9), "windup": (72, 42, 9, -6, 0, 1.0),
        "attack": (92, 66, 40, 3, 0, 1.3) if not back else (94, 58, 74, 3, 0.6, 0.8)}[pose]
    shadow(0, 40 if pose != "walk4" else 34)
    if pose == "walk":
        dust(0, False); dust(14, False)
    elif pose == "walk3":
        dust(-6, True); dust(20, False)
    ft = (0, fy + 3); kj = (3 * (1 if not back else -1), jt)
    tube([kj, ft], 16, 11, CHICKEN, sh=0.15)
    for k in range(1, 10):
        y = jt + (fy - jt) * k / 10
        stroke(ell(kj[0] * (1 - k / 10), y, 6.4, 2.2, 12, 180, 360), LINE * 0.45, g=CHICKEN_DK)
    chicken_foot_fb(ft, back, curl, fsc * 1.35)
    shape(ell(kj[0], kj[1], 7.5, 7, 16), CHICKEN, LINE * 0.9)
    th = bez((-15, hip), (-17, hip - (hip - jt) * 0.5), (-9, jt + 6), (-6, jt)) + bez((6, jt), (9, jt + 6), (17, hip - (hip - jt) * 0.5), (15, hip))
    form(th, FEATHER, sdx=-3, sdy=1, sh=0.2)
    C.saveState(); C.clipPath(poly(th), stroke=0, fill=0)
    y = hip - 4
    while y > jt:
        for s in (-1, 0, 1):
            stroke(ell(s * 8, y, 5, 3.5, 10, 200, 340), LINE * 0.45, g=FEATHER_DK)
        y -= 4.5
    C.restoreState()
    with T(0, hip, 1, rot=rot):
        fr = ragged((40, 4), (-40, 4), 10, 10, 2.1)
        form(fr + [(-38, 8), (38, 8)], FEATHER, sh=0.15)
        with T(0, 4, 0.92):
            hut_end(back)
    if pose == "attack" and not back:
        motion([bez((-30, 70), (-24, 58), (-18, 50), (-14, 44)), bez((30, 70), (24, 58), (18, 50), (14, 44))])


chaloupka.poses = ALL


# ------------------------------------------------------------------ registry
SPRITES = boss_items("strzyga", strzyga, 320) + boss_items("ohnivec", ohnivec, 352) + \
    boss_items("jezibaba", jezibaba, 320, 1.12) + boss_items("chaloupka", chaloupka, 448)
PORTRAITS = [("boss_strzyga", 256, 256, portrait(strzyga, 26, 100, 3.0, "#3b4658")),
             ("boss_ohnivec", 256, 256, portrait(ohnivec, 26, 124, 1.9, "#5a3020")),
             ("boss_jezibaba", 256, 256, portrait(jezibaba, 36, 92, 2.6, "#4a3030"))]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
