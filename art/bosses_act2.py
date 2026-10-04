"""Act II bosses: Megera, Divoký Prokop z Valdeka, Bazilišek."""
import math
from bosses_kit import *

BREW = col("#7fc04a"); BREW_HEX = "#a6f05a"
PELT = col("#8f8b84"); PELT_DK = col("#625e58")
SHOE = col("#5c4838")
SHIRT = col("#9c907a")


# ------------------------------------------------------------------ Megera
def ladle(p0, p1, spill=False):
    tube([p0, p1], 3.0, 2.6, WOOD, sh=0.15)
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    c = pt(p1, a, 6)
    with T(c[0], c[1], 1, rot=a - 90):
        bowl = ell(0, 0, 10, 8, 24, 180, 360) + [(10, 1.5), (-10, 1.5)]
        form(bowl, IRON, sdx=-2, sdy=1, sh=0.2)
        glow(0, 2, 14, BREW_HEX, 0.35)
        shape(ell(0, 1.5, 9.5, 2.6, 20), BREW, LINE * 0.7)
        for x in (-4, 1, 5):
            shape(ell(x, 2.4, 1.2, 0.9, 8), col("#c8f59a"), LINE * 0.4)
        stroke(ell(0, 1.5, 10.2, 3.0, 20, 180, 360), LINE * 0.9)
    if spill:
        for i, (dx, dy, r) in enumerate(((8, -6, 2.6), (12, -14, 2.2), (14, -23, 1.9), (13, -32, 1.6), (10, -40, 1.3))):
            q = (c[0] + dx, c[1] + dy)
            glow(q[0], q[1], r * 2.4, BREW_HEX, 0.3, 4)
            shape(ell(q[0], q[1], r, r * 1.3, 10), BREW, LINE * 0.5)
    else:
        drips([(c[0] + 7, c[1]), (c[0] - 6, c[1] - 1)], BREW, 6)


def megera(pose):
    lean = {"idle": 0, "walk": 5, "attack": 7}[pose]
    shadow(0, 36)
    hx, hy = 24 + lean, 106
    hair = []
    for i in range(19):
        a = 75 + i * 10
        r = (24 if i % 2 else 12) + 5 * math.sin(i * 1.3)
        q = (hx - 4 + math.cos(math.radians(a)) * r * 1.25, hy + 2 + math.sin(math.radians(a)) * r * 0.95)
        hair.append((q[0] - (r - 12) * 0.35, q[1]) if i % 2 else q)
    shape(hair, HAIR_GREY, LINE)
    for i in range(9):
        a = 95 + i * 17
        p = (hx - 4 + math.cos(math.radians(a)) * 6, hy + 2 + math.sin(math.radians(a)) * 6)
        stroke(bez(p, pt(p, a, 6), pt(p, a - 10, 12), pt(p, a - 18, 18)), LINE * 0.5, g=HAIR_DK, alpha=0.55)
    if pose == "attack":
        lad = ((-4 + lean, 94), (36 + lean, 126))
    elif pose == "walk":
        lad = ((52 + lean, 4), (36 + lean, 122))
    else:
        lad = ((42, 4), (40, 126))
    if pose != "attack":
        ladle(*lad)
    for lx in ((10, 18) if pose != "walk" else (6, 26)):
        tube([(lx - 2, 20), (lx, 5)], 4.5, 4.0, col("#6e6a62"), sh=0.1)
    skirt = [(-22, 72), (14 + lean * 0.5, 68)] + bez((14 + lean * 0.5, 68), (22, 50), (28, 30), (28, 12)) + \
        ragged((28, 12), (-34, 12), 8, 6, 2.0) + bez((-34, 12), (-34, 36), (-28, 56), (-22, 72))
    form(skirt, CLOTH_PLUM, sdx=-5, sdy=1, sh=0.18)
    for (x, y, w, h, c) in ((-14, 30, 10, 9, RAG), (6, 44, 9, 8, CLOTH_SLATE), (-26, 52, 8, 10, col("#8a6a48"))):
        p = rrect(x, y, w, h, 1.2)
        shape(p, c, LINE * 0.6)
        for k in range(3):
            stroke([(x + 1 + k * w / 3, y - 0.8), (x + 2 + k * w / 3, y + 0.8)], LINE * 0.35)
    for (x0, x1) in ((-18, -24), (0, 2), (16, 22)):
        stroke(bez((x0 + lean * 0.3, 68), (x0, 50), (x1, 30), (x1, 16)), LINE * 0.5, g=RED_DK)
    for fx in ((14, 20) if pose != "walk" else (8, 30)):
        sh_ = [(fx - 6, 1), (fx - 6, 7), (fx + 4, 7)] + bez((fx + 4, 7), (fx + 10, 6), (fx + 13, 4), (fx + 16, 6)) + [(fx + 13, 1)]
        shape(sh_, SHOE, LINE * 0.8)
    tors = [(-22, 72)] + bez((-22, 72), (-32, 88), (-30, 108), (-16, 118)) + \
        bez((-16, 118), (-4, 124), (8 + lean, 120), (16 + lean, 112)) + \
        bez((16 + lean, 112), (20 + lean, 100), (18 + lean, 84), (14 + lean * 0.5, 68))
    form(tors, SHIRT, sdx=-4, sdy=1, sh=0.15)
    shawl = [(-16, 120)] + bez((-16, 120), (-34, 112), (-34, 88), (-24, 70)) + [(-18, 64), (-14, 72)] + \
        bez((-14, 72), (-6, 82), (6 + lean, 90), (16 + lean, 92)) + [(20 + lean, 112), (8 + lean, 122)]
    form(shawl, CLOTH_VIOLET, sdx=-3, sdy=1, sh=0.2)
    hatch(shawl, 2.2, 70, 0.45, g=col("#3e2b48"), alpha=0.5)
    for i in range(9):
        p = (-24 + i * 1.2, 70 - i * 0.6) if i < 5 else (-14 + (i - 5) * 6 + lean * 0.5, 76 + (i - 5) * 3.5)
        stroke([p, (p[0] - 1, p[1] - 6)], LINE * 0.5, g=col("#3e2b48"))
    pelt = [(-38, 100)] + bez((-38, 100), (-36, 114), (-22, 124), (-6, 126)) + \
        bez((-6, 126), (6 + lean, 126), (14 + lean, 120), (16 + lean, 112)) + \
        bez((16 + lean, 112), (10 + lean, 112), (0, 116), (-10, 112)) + \
        bez((-10, 112), (-20, 108), (-28, 98), (-34, 92))
    form(notch(pelt, 1.2, 4), PELT, sdx=-2, sdy=1.5, sh=0.15)
    for i in range(10):
        p = (-32 + i * 4.5, 112 + 6 * math.sin(i * 0.6))
        stroke([p, (p[0] - 2.5, p[1] - 4)], LINE * 0.45, g=PELT_DK)
    wh = [(-30, 102)] + bez((-30, 102), (-38, 104), (-46, 98), (-50, 90)) + [(-48, 87)] + \
        bez((-48, 87), (-42, 88), (-36, 90), (-28, 92))
    shape(wh, PELT, LINE * 0.9)
    shape([(-30, 103), (-28, 112), (-24, 104)], PELT_DK, LINE * 0.7)
    stroke([(-41, 96), (-38, 95)], LINE * 0.9)
    for k in range(3):
        shape([(-47 + k * 3, 88), (-46 + k * 3, 85), (-45 + k * 3, 88)], BONE, LINE * 0.3)
    for (px, py) in ((12 + lean, 104), (6 + lean, 92)):
        tube([(px, py), (px + 3, py - 12)], 4.0, 3.2, PELT, LINE * 0.8, sh=0)
        claws((px + 3, py - 13), -80, 3, 3, 0.8, 8, BONE)
    for i in range(6):
        t = i / 5
        p = (2 + lean + t * 16, 112 - t * 18 - 4 * math.sin(t * math.pi))
        shape([(p[0] - 1, p[1]), (p[0] + 1, p[1]), (p[0], p[1] - 4)], BONE, LINE * 0.4)
    stroke(bez((0 + lean, 113), (6 + lean, 100), (14 + lean, 94), (19 + lean, 94)), LINE * 0.45)
    head = bez((hx - 9, hy + 6), (hx - 9, hy + 13), (hx + 2, hy + 15), (hx + 8, hy + 9)) + \
        bez((hx + 8, hy + 9), (hx + 10, hy + 6), (hx + 10, hy + 3), (hx + 11, hy + 1)) + \
        bez((hx + 11, hy + 1), (hx + 16, hy - 2), (hx + 22, hy - 6), (hx + 20, hy - 9)) + \
        bez((hx + 20, hy - 9), (hx + 17, hy - 7), (hx + 14, hy - 5), (hx + 11, hy - 5)) + \
        bez((hx + 11, hy - 5), (hx + 12, hy - 8), (hx + 15, hy - 12), (hx + 15, hy - 16)) + \
        bez((hx + 15, hy - 16), (hx + 8, hy - 15), (hx + 2, hy - 13), (hx - 4, hy - 8)) + \
        bez((hx - 4, hy - 8), (hx - 9, hy - 4), (hx - 10, hy + 1), (hx - 9, hy + 6))
    form(head, HAG, sdx=-3, sdy=0.5, sh=0.2)
    hatch(ell(hx + 2, hy - 6, 4, 4, 12), 1.0, 50, 0.4, alpha=0.6)
    m = bez((hx + 4, hy - 7), (hx + 7, hy - 8), (hx + 10, hy - 8), (hx + 12, hy - 10)) + \
        bez((hx + 12, hy - 10), (hx + 9, hy - 12), (hx + 6, hy - 11.5), (hx + 4, hy - 7))
    shape(m, MOUTH_DK, LINE * 0.6)
    for tx in (hx + 6, hx + 8.5, hx + 10.5):
        shape([(tx - 0.6, hy - 8.2), (tx + 0.6, hy - 8.2), (tx, hy - 10.2)], BONE, LINE * 0.3)
    dot(hx + 17, hy - 3, 1.0, HAG_DK); dot(hx + 13, hy - 13, 0.8, HAG_DK)
    shape(ell(hx + 5, hy + 3, 2.6, 2.0, 12), HAG_DK, 0)
    eye(hx + 5.2, hy + 3, 1.9, EYE_GREEN, halo=3.4)
    stroke([(hx + 1, hy + 7.5), (hx + 9, hy + 5)], LINE * 1.1)
    for k in range(3):
        stroke([(hx - 2, hy - 2 + k * 2.5), (hx + 1, hy - 1 + k * 2.5)], LINE * 0.4)
    fr = [(hx - 10, hy + 10), (hx - 2, hy + 18), (hx + 4, hy + 16), (hx + 10, hy + 14), (hx + 6, hy + 10), (hx + 9, hy + 8), (hx + 2, hy + 9), (hx - 4, hy + 4)]
    shape(fr, HAIR_GREY, LINE * 0.9)
    stroke(bez((hx - 6, hy + 4), (hx - 8, hy - 8), (hx - 6, hy - 18), (hx - 9, hy - 28)), LINE * 0.8, g=HAIR_GREY)
    if pose == "attack":
        s0 = (8 + lean, 108); hand = (18 + lean, 124)
        ladle(*lad, spill=True)
        tube([s0, (24 + lean, 104)], 6.5, 5.5, SHIRT); tube([(24 + lean, 104), hand], 5.5, 4.4, HAG)
        shape(ell(hand[0], hand[1], 3.8, 3.2, 12), HAG, LINE * 0.8)
        claws(hand, 130, 3, 4, 1.0, 10, HAG_DK, curl=40)
        motion([bez((-10, 128), (0, 146), (22, 156), (44, 154)), bez((-2, 132), (8, 146), (24, 150), (38, 150))])
    else:
        s0 = (8 + lean, 108)
        hand = pt(lad[0], math.degrees(math.atan2(lad[1][1] - lad[0][1], lad[1][0] - lad[0][0])), 86)
        el = (hand[0] - 6, hand[1] - 16)
        tube([s0, el], 6.5, 5.5, SHIRT); tube([el, hand], 5.5, 4.4, HAG)
        shape(ell(hand[0], hand[1], 3.8, 3.2, 12), HAG, LINE * 0.8)
        claws((hand[0] + 2, hand[1]), 80, 3, 4, 1.0, 12, HAG_DK, curl=60)


# ------------------------------------------------------------------ Prokop
BLACK_CLOTH = col("#3e3a44"); CAPA_RED = col("#9a2f32")
ARMOUR = col("#5f646d"); ARMOUR_LT = col("#8d929b")


def horse_leg(top, a1, l1, a2, l2, colr=BONE, far=False):
    k = 0.85 if far else 1.0
    knee = pt(top, a1, l1); foot = pt(knee, a2, l2)
    bone(top, knee, 5.6 * k, colr)
    bone(knee, foot, 4.0 * k, colr)
    shape(ell(knee[0], knee[1], 3.8 * k, 3.8 * k, 12), colr, LINE * 0.7)
    hoof = [(foot[0] - 3.5, foot[1] + 2), (foot[0] + 3.0, foot[1] + 2), (foot[0] + 4.5, foot[1] - 3), (foot[0] - 4, foot[1] - 3)]
    with T(foot[0], foot[1], 1, rot=a2 + 90):
        shape([(x - foot[0], y - foot[1]) for x, y in hoof], RUST_DK if not far else col("#5a3a2a"), LINE * 0.7)


def ghostfire(pts, hx_=EYE_BLUE, w=6, a=0.55):
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        glow(p[0], p[1], w * 1.6, hx_, 0.25, 4)
        tongue = [(p[0] - w * 0.5, p[1]), (q[0] - 2, q[1] + w * 1.6), (p[0] + w * 0.5, p[1] + 1)]
        flat(tongue, hx_, a)
        flat([(p[0] - w * 0.25, p[1]), (q[0] - 1, q[1] + w * 1.0), (p[0] + w * 0.25, p[1] + 1)], "#eefaff", 0.7)


def prokop(pose):
    gallop = pose != "idle"
    lift = {"idle": 0, "walk": 6, "attack": 8}[pose]
    tilt = {"idle": 0, "walk": -3, "attack": -6}[pose]
    shadow(0, 70)
    with T(0, lift, 1, rot=tilt):
        if pose == "idle":
            far = [((-46, 82), -95, 32, -88, 42), ((36, 84), -90, 30, -92, 46)]
            near = [((-56, 80), -100, 32, -84, 42), ((28, 84), -86, 30, -90, 46)]
        elif pose == "walk":
            far = [((-46, 82), -80, 32, -95, 40), ((36, 84), -70, 30, -150, 40)]
            near = [((-56, 80), -130, 32, -110, 40), ((28, 84), -40, 30, -100, 40)]
        else:
            far = [((-46, 82), -110, 32, -100, 38), ((36, 84), -50, 30, -110, 38)]
            near = [((-56, 80), -150, 32, -120, 38), ((28, 84), -10, 30, -70, 38)]
        for leg in far:
            horse_leg(*leg, colr=BONE_SH, far=True)
        tail = [(-72, 92), (-92, 86), (-104, 70), (-100, 52)]
        ghostfire(bez(*tail, 6), EYE_BLUE, 5, 0.45)
        if pose == "idle":
            cloak = [(-4, 152)] + bez((-4, 152), (-24, 148), (-36, 122), (-44, 96)) + \
                ragged((-44, 96), (-14, 100), 4, 7, 1) + bez((-14, 100), (-12, 120), (-8, 134), (-2, 140))
        else:
            cloak = [(-6, 152)] + bez((-6, 152), (-30, 150), (-50, 140), (-78, 146)) + \
                ragged((-78, 146), (-72, 112), 3, 6, 1) + bez((-72, 112), (-60, 118), (-50, 108), (-30, 118)) + [(-8, 124)]
        form(cloak, CAPA_RED, sdx=-3, sdy=-2, sh=0.2)
        spine = bez((-74, 92), (-40, 104), (0, 98), (34, 100))
        for i in range(0, len(spine) - 1, 1):
            bone(spine[i], spine[i + 1], 4.6, BONE)
        pel = [(-74, 90), (-64, 100), (-46, 98), (-42, 86), (-54, 76), (-68, 80)]
        form(pel, BONE, sdx=-1.5, sdy=1, sh=0.18)
        shape(ell(-56, 88, 4, 3, 10), HOLLOW, LINE * 0.6)
        for i in range(8):
            x = -34 + i * 8.5
            y0 = 100 - 0.8 * i * (i - 6) * 0.2
            rib = bez((x, y0), (x + 6, y0 - 8), (x + 8, y0 - 28), (x + 2 + i * 0.5, y0 - 44 + abs(i - 4) * 2.5))
            tube(rib, 2.8, 1.8, BONE, LINE * 0.6, sh=0)
        stroke(bez((-30, 60), (-10, 52), (14, 54), (30, 64)), LINE * 0.8, g=BONE_SH)
        glow(-2, 78, 18, EYE_BLUE, 0.25)
        capa = [(-58, 102)] + bez((-58, 102), (-40, 110), (0, 106), (24, 104)) + \
            ragged((24, 104), (16, 74), 3, 4, 3) + ragged((16, 74), (-60, 74), 8, 7, 1) + [(-62, 90)]
        form(capa, BLACK_CLOTH, sdx=-3, sdy=1.5, sh=0.15)
        C.saveState(); C.clipPath(poly(capa), stroke=0, fill=0)
        for x in range(-64, 30, 16):
            flat([(x, 60), (x + 7, 60), (x + 11, 112), (x + 4, 112)], CAPA_RED.hex)
        C.restoreState()
        stroke(capa, LINE, closed=True)
        neck = bez((26, 98), (42, 112), (52, 124), (58, 128))
        for i in range(len(neck) - 1):
            bone(neck[i], neck[i + 1], 3.8, BONE)
        ghostfire(bez((22, 104), (34, 120), (46, 132), (56, 136), 6), EYE_BLUE, 6, 0.5)
        sk = [(50, 134), (60, 138), (68, 132), (92, 110), (96, 104), (92, 100), (84, 102), (62, 116), (52, 122)]
        form(sk, BONE, sdx=-2, sdy=1.5, sh=0.2)
        jaw = [(58, 118), (84, 101), (92, 98), (90, 95), (80, 96), (60, 110)] if pose != "attack" else \
            [(58, 118), (82, 98), (88, 92), (86, 89), (76, 92), (58, 110)]
        shape(jaw, BONE_SH, LINE * 0.8)
        for i in range(5):
            x = 76 + i * 3.4; y = 104 - i * 2.2
            stroke([(x, y), (x + 0.6, y - 2.4)], LINE * 0.45)
        shape(ell(88, 104, 1.2, 1.6, 8, rot=40), HOLLOW, 0)
        shape(ell(66, 124, 4.0, 3.2, 12, rot=-30), HOLLOW, LINE * 0.6)
        eye(66, 124, 2.0, EYE_BLUE, halo=4)
        ghostfire([(66, 125), (60, 134)], EYE_BLUE, 3, 0.5)
        for leg in near:
            horse_leg(*leg)
        rein = [(56, 112), (36, 124), (24, 124)]
        stroke(rein, LINE * 0.8, g=RUST_DK)
        lean = {"idle": 0, "walk": 4, "attack": 10}[pose]
        shape(rrect(-20, 98, 36, 10, 3), col("#6b4a30"), LINE)
        thigh = [(-12, 108), (8, 110), (12, 98), (14, 84), (6, 82), (0, 96), (-12, 100)]
        form(thigh, ARMOUR, sdx=-2, sdy=1, sh=0.18)
        tube([(10, 86), (10, 64)], 7, 6, ARMOUR, sh=0.15)
        shape(ell(10, 86, 4.5, 4.5, 12), ARMOUR_LT, LINE * 0.8)
        shape([(5, 66), (18, 66), (20, 60), (4, 60)], RUST_DK, LINE * 0.8)
        stroke(ell(12, 59, 4, 3, 12, 180, 360), LINE * 0.8, g=IRON_LT)
        with T(0, 108, 1, rot=-lean):
            if pose == "attack":
                tube([(-10, 40), (4, 28), (16, 22)], 6.5, 5.5, ARMOUR)
            body = [(-14, 0), (12, 0)] + bez((12, 0), (18, 14), (18, 34), (14, 44)) + \
                [(-14, 46)] + bez((-14, 46), (-20, 30), (-20, 12), (-14, 0))
            form(body, ARMOUR, sdx=-4, sdy=1, sh=0.2)
            shape(rrect(-15, -2, 29, 7, 2), RUST, LINE * 0.8)
            for y in (14, 24):
                stroke(bez((-16, y), (-6, y - 2), (6, y - 2), (16, y)), LINE * 0.6)
            hatch(ell(-14, 24, 6, 20, 14), 1.6, 70, 0.45, alpha=0.6)
            for (x, y) in ((-10, 36), (8, 40), (12, 8)):
                dot(x, y, 0.9, RUST)
            shape(ell(-8, 44, 9, 6, 16), ARMOUR_LT, LINE * 0.9)
            hel = rrect(-10, 46, 22, 24, 4)
            form(hel, ARMOUR, sdx=-3, sdy=0, sh=0.2)
            shape([(-11, 66), (13, 66), (10, 74), (-8, 74)], ARMOUR_LT, LINE * 0.8)
            tube(bez((-6, 64), (-18, 66), (-24, 76), (-18, 90), 12), 6, 1.2, HORN, LINE * 0.8, sh=0.15)
            tube(bez((9, 64), (22, 66), (28, 76), (22, 92), 12), 6.5, 1.2, HORN, LINE * 0.8, sh=0.15)
            shape([(0, 57), (12, 57), (12, 60), (0, 60)], HOLLOW, 0)
            glow(9, 58.5, 7, EYE_BLUE, 0.5)
            flat([(3, 57.8), (11, 57.8), (11, 59.4), (3, 59.4)], EYE_BLUE)
            stroke([(1, 52), (1, 64)], LINE * 0.6)
            for y in (50, 53):
                for x in (5, 8, 11):
                    dot(x, y, 0.5, HOLLOW)
            if pose == "attack":
                hand = (16, 22)
            else:
                hand = (22, 18)
                tube([(-2, 38), (12, 20), hand], 6.5, 5.5, ARMOUR)
            shape(ell(hand[0], hand[1], 4.2, 3.8, 12), ARMOUR_LT, LINE * 0.8)
        if pose == "attack":
            lance((-30, 132), (74, 121))
        elif pose == "walk":
            lance((-2, 92), (42, 188))
        else:
            lance((22, 70), (22, 194), side=1)


def lance(p0, p1, side=-1):
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    tube([p0, p1], 3.4, 2.4, WOOD, sh=0.15)
    tip = pt(p1, a, 14)
    shape([pt(p1, a + 90, 2.4), tip, pt(p1, a - 90, 2.4)], IRON_LT, LINE * 0.8)
    v = pt(p1, a + 180, 18)
    shape([pt(v, a + 90, 4.5), pt(v, a - 90, 4.5), pt(pt(v, a - 90, 4.5), a + 180, 3), pt(pt(v, a + 90, 4.5), a + 180, 3)], RUST, LINE * 0.7)
    q0 = pt(p1, a + 180, 24); q1 = pt(p1, a + 180, 40)
    d = 180 + side * 70
    flag = [q0, q1, pt(pt(q1, a + d, 22), a, 6), pt(pt(q0, a + d, 18), a, 2), pt(pt(q0, a + 180 + side * 80, 26), a, 6)]
    form(flag, CAPA_RED, sdx=-1, sdy=1, sh=0.15)


# ------------------------------------------------------------------ Bazilišek
WING = col("#5c6e6a"); WING_DK = col("#40504c"); WING_MEM = col("#7e8f86")
TALON = col("#b9ab88")


def gaze(x, y, ang, ln=60):
    for i, da in enumerate((-14, -7, 0, 7, 14)):
        q = pt((x, y), ang + da, ln * (1 - abs(da) / 40))
        stroke([(x, y), q], LINE * (1.2 if da == 0 else 0.7), g=col(EYE_GREEN), alpha=0.75)
    glow_ell(x + math.cos(math.radians(ang)) * ln * 0.45, y + math.sin(math.radians(ang)) * ln * 0.45,
             ln * 0.5, ln * 0.2, EYE_GREEN, 0.35, rot=ang)


def chicken_leg(hip, knee, foot, far=False):
    c = SCALE_DK if far else SCALE_OLIVE
    tube([hip, knee], 13 if not far else 11, 9, c, sh=0.15)
    tube([knee, foot], 5.5, 4.5, BEAK if not far else col("#b08a36"), sh=0.12)
    for k in range(4):
        q = pt(knee, math.degrees(math.atan2(foot[1] - knee[1], foot[0] - knee[0])), 6 + k * 6)
        stroke([(q[0] - 2.5, q[1]), (q[0] + 2.5, q[1] + 1)], LINE * 0.5)
    for a, ln in ((0, 13), (20, 10), (180, 9)):
        tip = pt(foot, a, ln)
        tube([foot, tip], 3.6, 2.4, BEAK if not far else col("#b08a36"), LINE * 0.7, sh=0)
        cl = pt(tip, a - 50 if a < 90 else a + 50, 4)
        shape([pt(tip, a + 90, 1.3), cl, pt(tip, a - 90, 1.3)], TALON, LINE * 0.6)


def wing_shape(dx, dy, wy, membrane, bone_c, s=1.0):
    def W(p): return (dx + p[0] * s, dy + p[1] * s)
    top = W((-58, 178 + wy))
    wing = [W(p) for p in [(-14, 110), (-38, 146 + wy), (-58, 178 + wy), (-78, 166 + wy), (-92, 148 + wy),
                            (-100, 124 + wy * 0.5), (-86, 126), (-82, 108), (-68, 112), (-60, 94), (-46, 100), (-30, 88)]]
    form(wing, membrane, sdx=-3, sdy=-2, sh=0.18)
    for p in [W(q) for q in ((-100, 124 + wy * 0.5), (-82, 108), (-60, 94), (-30, 88))]:
        stroke(bez(top, ((top[0] + p[0]) / 2 + 3, (top[1] + p[1]) / 2 + 4), p, p), LINE * 0.9, g=bone_c)
    tube([W((-14, 110)), W((-38, 146 + wy)), top], 7 * s, 3.5 * s, bone_c, sh=0.1)
    shape([top, (top[0] + 3, top[1] + 9), (top[0] - 3, top[1] + 2)], TALON, LINE * 0.6)


def bazilisek(pose):
    shadow(-8, 74)
    att = pose == "attack"
    if pose == "walk":
        lf = [(-6, 72), (-20, 36), (-30, 6)]; ln_ = [(12, 70), (34, 44), (40, 16)]
    elif att:
        lf = [(-8, 72), (-30, 40), (-42, 6)]; ln_ = [(10, 70), (22, 34), (24, 6)]
    else:
        lf = [(-8, 72), (-16, 38), (-12, 6)]; ln_ = [(8, 70), (18, 36), (16, 6)]
    wy = {"idle": 0, "walk": -10, "attack": 6}[pose]
    wing_shape(22, 4, wy * 0.7, WING_DK, col("#33403c"), 0.92)
    chicken_leg(*lf, far=True)
    tail = bez((-34, 76), (-72, 70), (-98, 42), (-84, 18)) + bez((-84, 18), (-72, 4), (-42, 4), (-38, 20))
    pts = resample(tail, 1.5)
    n = len(pts)
    ol, orr = [], []
    for i in range(n):
        a = pts[max(0, i - 1)]; b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1
        w = 14 * (1 - i / n) + 1.5
        ol.append((pts[i][0] - dy / L * w, pts[i][1] + dx / L * w))
        orr.append((pts[i][0] + dy / L * w, pts[i][1] - dx / L * w))
    for i in range(3, n - 5, 7):
        p = pts[i]; a = pts[i + 1]
        ang = math.degrees(math.atan2(a[1] - p[1], a[0] - p[0])) + 90
        w = 14 * (1 - i / n) + 1.5
        b0 = pt(p, ang, w - 1.5)
        shape([pt(b0, ang - 70, 3.5), pt(b0, ang + 10, 9 * (1 - i / n) + 3), pt(b0, ang + 80, 3.5)], COMB_RED, LINE * 0.6)
    tl = ol + list(reversed(orr))
    form(tl, SCALE_OLIVE, sdx=-2, sdy=2, sh=0.2)
    scales(tl, -104, 0, -20, 90, 3.0, g=SCALE_DK, alpha=0.6)
    tip = pts[-1]
    shape([(tip[0] - 4, tip[1] + 1), (tip[0] + 4, tip[1] + 12), (tip[0] + 6, tip[1] - 2)], COMB_RED, LINE * 0.7)
    body = bez((-40, 98), (-52, 82), (-40, 60), (-12, 58)) + bez((-12, 58), (18, 56), (40, 74), (40, 96)) + \
        bez((40, 96), (40, 114), (28, 122), (14, 124)) + bez((14, 124), (-10, 126), (-32, 114), (-40, 98))
    for i in range(9):
        t = i / 8
        p = bez((16, 124), (-6, 128), (-30, 118), (-44, 96), 8)[i]
        a = 90 + t * 60
        shape([pt(p, a - 60, 4), pt(p, a, 11 - t * 4), pt(p, a + 60, 4)], SCALE_DK, LINE * 0.6)
        stroke([pt(p, a, 4), pt(p, a, 10 - t * 4)], LINE * 1.2, g=SILVER, alpha=0.7)
    form(body, SCALE_OLIVE, sdx=-6, sdy=2, sh=0.22)
    belly = bez((-26, 66), (0, 58), (26, 64), (38, 86)) + bez((38, 86), (26, 82), (0, 74), (-24, 74))
    shape(belly, col("#b2ac84"), LINE * 0.7)
    for i in range(6):
        x = -18 + i * 9
        stroke(bez((x, 74 - i * 0.2), (x + 2, 70), (x + 3, 66), (x + 3, 62)), LINE * 0.45)
    scales(body, -44, 76, 42, 128, 3.2, g=SCALE_DK, alpha=0.55)
    hatch(ell(-30, 86, 14, 22, 16), 1.8, 60, 0.45, alpha=0.45)
    wing_shape(0, 0, wy, WING, WING_DK)
    if att:
        nk = [(16, 112), (34, 132), (50, 126), (58, 118)]; hd = (62, 118); ha = -10
    elif pose == "walk":
        nk = [(16, 112), (26, 140), (44, 150), (56, 148)]; hd = (60, 150); ha = -6
    else:
        nk = [(16, 112), (22, 144), (34, 158), (46, 160)]; hd = (52, 162); ha = 4
    neck = bez(*nk, 14)
    for i in range(1, len(neck) - 2, 2):
        p = neck[i]; q = neck[i + 1]
        a = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) + 90
        w = 11 - i * 0.35
        b0 = pt(p, a, w - 1)
        shape([pt(b0, a - 70, 3), pt(b0, a + 5, 8 - i * 0.25), pt(b0, a + 70, 3)], col("#b0622e"), LINE * 0.6)
    tube(neck, 22, 15, SCALE_OLIVE, sh=0.18)
    C.saveState()
    for i in range(1, len(neck) - 1, 2):
        p = neck[i]; q = neck[i + 1]
        a = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
        w = 11 - i * 0.4
        stroke([pt(p, a - 90, w * 0.9), pt(pt(p, a - 90, w * 0.2), a, 1)], LINE * 0.45, alpha=0.6)
    C.restoreState()
    chicken_leg(*ln_)
    with T(hd[0], hd[1], 1.2, rot=ha):
        for i, (x, h) in enumerate(((-12, 9), (-7, 13), (-2, 16), (3, 14), (8, 10))):
            shape(ell(x, 8 + h * 0.45, 3.0, h * 0.6, 14, rot=-15 - i * 3), COMB_RED, LINE * 0.7)
        for i in range(3):
            shape([(-10 - i * 3, 2 - i * 3), (-22 - i * 4, 6 - i * 4), (-12 - i * 3, -2 - i * 3)], SCALE_DK, LINE * 0.6)
        hd_pts = ell(0, 0, 14, 10, 30)
        form(hd_pts, SCALE_OLIVE, sdx=-3, sdy=1, sh=0.22)
        scales(hd_pts, -15, -10, 2, 10, 2.2, g=SCALE_DK, alpha=0.45)
        wat = bez((6, -6), (11, -16), (5, -28), (-1, -22)) + bez((-1, -22), (-4, -15), (0, -10), (2, -6))
        form(wat, COMB_RED, sdx=-1, sdy=0, sh=0.2)
        gap = 8 if att else 0
        upper = [(9, 4)] + bez((9, 4), (18, 4), (27, 1), (29, -6)) + [(25, -3), (11, -3)]
        lower = [(10, -4), (23, -5 - gap), (24, -7 - gap), (9, -9)]
        if att:
            shape([(10, -3), (25, -3), (22, -6 - gap), (10, -7)], MOUTH_DK, 0)
            stroke(bez((11, -5), (18, -6), (24, -2 - gap * 0.6), (28, -7 - gap * 0.4)), LINE * 1.1, g=COMB_RED)
        shape(lower, BEAK, LINE * 0.8)
        shape(upper, BEAK, LINE * 0.8)
        dot(17, 1.5, 0.7, MOUTH_DK)
        shape(ell(4, 2.5, 4.6, 3.6, 14), SCALE_DK, 0)
        eye(4.5, 2.5, 3.0, EYE_GREEN, slit=True, halo=4.8)
        brow = [(-4, 5), (2, 8.5), (11, 7), (12, 4.5), (6, 5.5), (0, 4)]
        shape(brow, SCALE_DK, LINE * 0.8)
        if att:
            gaze(7, 2.5, 0, 20)
    if att:
        for r_ in (6, 10):
            stroke(ell(hd[0] + 12, hd[1] + 1, r_, r_, 16, -40, 40), LINE * 0.6, alpha=0.5)


# ------------------------------------------------------------------ registry
SPRITES = boss_items("megera", megera, 320) + boss_items("prokop", prokop, 448) + boss_items("bazilisek", bazilisek, 416)
PORTRAITS = [("boss_megera", 256, 256, portrait(megera, 32, 104, 3.0, "#3a4a32")),
             ("boss_prokop", 256, 256, portrait(prokop, 4, 160, 2.3, "#2e3a50", cy=58)),
             ("boss_bazilisek", 256, 256, portrait(bazilisek, 56, 162, 2.2, "#3e4a2a"))]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
