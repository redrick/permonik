"""Act I bosses: Klekánice, Kostník ze Sedlce, Vodník Hastrman."""
import math
import lib
from bosses_kit import *


# ------------------------------------------------------------------ Klekánice
def bell(x, y, s=1.0, rot=0, ringing=False):
    with T(x, y, s, rot=rot):
        stroke([(0, 0), (0, -4)], LINE * 1.2)
        shape(ell(0, -4.5, 2.2, 1.6, 12), BRONZE, LINE * 0.8)
        b = bez((-3, -5), (-4, -8), (-4.5, -12), (-7.5, -16)) + [(7.5, -16)] + bez((7.5, -16), (4.5, -12), (4, -8), (3, -5))
        form(b, BRONZE, sdx=-1.5, sdy=0.5, sh=0.2)
        stroke(bez((-7, -15.3), (-3, -14.2), (3, -14.2), (7, -15.3)), LINE * 0.6)
        shape(ell(1.5 if ringing else 0, -17, 1.5, 1.5, 10), BRONZE_DK, LINE * 0.6)
        if ringing:
            for r_ in (11, 15):
                stroke(ell(0, -12, r_, r_ * 0.8, 16, 200, 250), LINE * 0.6, alpha=0.6)
                stroke(ell(0, -12, r_, r_ * 0.8, 16, -70, -20), LINE * 0.6, alpha=0.6)


BRONZE_DK = col("#7a5a2a")


def klekanice(pose):
    lean = {"idle": 0, "walk": 6, "attack": 7}[pose]
    sway = {"idle": 0, "walk": -8, "attack": -5}[pose]
    shadow(2, 38)
    glow_ell(-2, 8, 40, 8, "#bfe0ff", 0.22)
    if pose == "attack":
        fs = (26 + lean, 88); fe = (40 + lean, 96); fh = (53 + lean, 92)
        tube([fs, fe], 5.5, 4.4, HAG); tube([fe, fh], 4.4, 3.4, HAG)
        shape(ell(fh[0], fh[1], 3.4, 2.6, 12, rot=-10), HAG, LINE * 0.8)
        claws(fh, -5, 4, 11, 1.5, 16, HAG_DK, curl=-35)
    body = ragged((-34 + sway, 16), (26 + sway * 0.2, 15), 7, 10, 1.3) + \
        bez((26 + sway * 0.2, 15), (32, 34), (22 + lean * 0.3, 62), (26 + lean, 86)) + \
        bez((26 + lean, 86), (38 + lean, 92), (48 + lean, 104), (46 + lean, 118)) + \
        bez((46 + lean, 118), (44 + lean, 132), (24 + lean, 140), (2 + lean * 0.6, 140)) + \
        bez((2 + lean * 0.6, 140), (-16 + lean * 0.4, 140), (-30 + lean * 0.2, 120), (-34, 96)) + \
        bez((-34, 96), (-38, 70), (-42 + sway, 36), (-34 + sway, 16))
    form(body, SHEET, sdx=-5, sdy=2, sh=0.16)
    C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
    flat(ell(-4 + sway * 0.5, -6, 52, 38, 30), "#6f7f99", 0.28)
    hatch(ell(-30 + sway * 0.5, 60, 18, 70, 20), 2.0, 62, 0.5, g=SHEET_SH, alpha=0.75)
    hatch(ell(0, 14, 40, 14, 20), 2.2, 35, 0.45, g=SHEET_SH, alpha=0.6)
    hatch(ell(20 + lean, 84, 14, 10, 20), 1.8, 20, 0.45, g=SHEET_SH, alpha=0.7)
    C.restoreState()
    for (x0, y0, x1, y1) in ((-8, 136, -20 + sway, 14), (6, 128, -4 + sway * 0.6, 8), (18, 84, 14 + sway * 0.3, 6),
                             (-22, 120, -30 + sway, 20), (-14, 100, 8 + sway * 0.5, 20)):
        stroke(bez((x0 + lean, y0), (x0 + lean * 0.5 - 3, y0 - 30), (x1 + 3, y1 + 30), (x1, y1)), LINE * 0.6, g=SHEET_SH)
    hx, hy = 37 + lean, 106
    hole = ell(hx, hy, 9.0, 13, 24, rot=-22)
    shape(hole, HOLLOW, LINE)
    C.saveState(); C.clipPath(poly(hole), stroke=0, fill=0)
    fc = bez((hx - 1, hy + 11), (hx + 8, hy + 10), (hx + 9, hy + 3), (hx + 8, hy - 1)) + \
        bez((hx + 8, hy - 1), (hx + 9, hy - 8), (hx + 6, hy - 15), (hx - 1, hy - 15)) + \
        bez((hx - 1, hy - 15), (hx - 4, hy - 10), (hx - 4, hy), (hx - 3, hy + 11))
    form(fc, HAG, sdx=-2, sdy=0, sh=0.3)
    hatch(ell(hx + 1, hy - 4, 3, 4, 12), 1.0, 60, 0.4, alpha=0.7)
    m = bez((hx + 1, hy - 7), (hx + 3, hy - 6), (hx + 6, hy - 6.5), (hx + 8, hy - 8)) + \
        bez((hx + 8, hy - 8), (hx + 6, hy - 12), (hx + 3, hy - 12.5), (hx + 1, hy - 7))
    shape(m, MOUTH_DK, LINE * 0.6)
    for tx in (hx + 3, hx + 5.5):
        shape([(tx - 0.5, hy - 6.5), (tx + 0.6, hy - 6.5), (tx, hy - 9.5)], BONE, LINE * 0.3)
    for (sx, sy) in ((hx - 4, hy + 8), (hx + 8, hy + 9)):
        stroke(bez((sx, sy), (sx + 1, sy - 8), (sx - 1, sy - 14), (sx + 0.5, sy - 22)), LINE * 0.7, g=HAIR_GREY)
    C.restoreState()
    nose = bez((hx + 7, hy + 2), (hx + 11, hy), (hx + 15, hy - 4), (hx + 15, hy - 9)) + \
        bez((hx + 15, hy - 9), (hx + 13, hy - 7), (hx + 10, hy - 5), (hx + 7.5, hy - 4))
    shape(nose, HAG, LINE * 0.8)
    for ex, ey, r_ in ((hx + 4.5, hy + 3.5, 1.9), (hx - 0.5, hy + 4, 1.4)):
        shape(ell(ex, ey, r_ * 1.8, r_ * 1.5, 12), HAG_DK, 0)
        eye(ex, ey, r_, EYE_YELLOW, halo=3.2)
    stroke(bez((hx + 2, hy + 7), (hx + 4, hy + 8), (hx + 6, hy + 7.5), (hx + 7, hy + 6)), LINE * 0.7)
    for d in (0, 1):
        stroke(bez((hx - 10, hy + 12 + d * 3), (hx - 2, hy + 18 + d * 3), (hx + 8, hy + 17 + d * 3), (hx + 12, hy + 10 + d * 2)), LINE * 0.5, g=SHEET_SH)
    s0 = (14 + lean, 98)
    if pose == "attack":
        e0 = (22 + lean, 120); h0 = (14 + lean, 142); ca = 100
    elif pose == "walk":
        e0 = (30 + lean, 78); h0 = (46 + lean, 66); ca = -35
    else:
        e0 = (28, 74); h0 = (40, 56); ca = -60
    tube([s0, e0], 6.0, 4.8, HAG); tube([e0, h0], 4.8, 3.6, HAG)
    shape(ell(h0[0], h0[1], 3.4, 2.8, 12, rot=ca), HAG, LINE * 0.8)
    claws(h0, ca + 150, 3, 5, 1.2, 10, HAG_DK, curl=-60)
    bell(h0[0], h0[1] - 1, 1.3, rot=(-25 if pose == "attack" else 18 if pose == "walk" else 4), ringing=pose == "attack")
    sleeve = [(s0[0] - 8, s0[1] + 8)] + bez((s0[0] - 8, s0[1] + 8), (s0[0] + 6, s0[1] + 12), (e0[0] + 4, e0[1] + 6), (e0[0] + 3, e0[1] - 1)) + \
        ragged((e0[0] + 3, e0[1] - 1), (e0[0] - 6, e0[1] - 4), 3, 4, 2) + \
        bez((e0[0] - 6, e0[1] - 4), (s0[0] - 2, s0[1] - 14), (s0[0] - 12, s0[1] - 8), (s0[0] - 8, s0[1] + 8))
    form(sleeve, SHEET, sdx=-2, sdy=1.5, sh=0.16)
    if pose == "attack":
        motion([bez((36 + lean, 74), (46 + lean, 76), (56 + lean, 80), (62 + lean, 84)),
                bez((36 + lean, 82), (44 + lean, 84), (52 + lean, 86), (58 + lean, 88))])


def klek_portrait():
    return portrait(klekanice, 38, 108, 3.2, "#3c4656")


# ------------------------------------------------------------------ Kostník ze Sedlce
def bony_foot(a, fwd=1, colr=None):
    colr = colr if colr is not None else BONE
    x, y = a
    heel = ell(x - 2, y - 3, 3.5, 3, 12)
    shape(heel, colr, LINE * 0.8)
    for i, dy in enumerate((-1, -3, -5)):
        tube([(x, y - 2), (x + 8 * fwd, y + dy - 0.5), (x + 13 * fwd, y + dy - 2.5 + i * 0.5)], 2.6, 1.6, colr, LINE * 0.7, sh=0)


def bundle(p0, p1, w, colr, n=2):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0]) + math.pi / 2
    for i in range(n):
        o = (i - (n - 1) / 2) * w * 0.55
        dx, dy = math.cos(a) * o, math.sin(a) * o
        bone((p0[0] + dx, p0[1] + dy), (p1[0] + dx * 0.6, p1[1] + dy * 0.6), w * (0.75 if i else 0.85), colr)


def bone_leg(hip, knee, ankle, colr, w=8):
    bundle(hip, knee, w, colr, 2)
    bundle(knee, ankle, w * 0.85, colr, 2)
    skull(knee[0] + 1, knee[1] + 1, w * 0.62, colr, sockets=HOLLOW)
    bony_foot(ankle, 1, colr)


def chandelier(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        for sx in (-1, 1):
            arm = bez((0, 2), (sx * 6, -2), (sx * 13, 0), (sx * 14, 7))
            tube(arm, 2.2, 1.8, BONE, LINE * 0.7, sh=0)
            shape(rrect(sx * 14 - 2, 7, 4, 2, 0.8), BONE_SH, LINE * 0.6)
            shape(rrect(sx * 14 - 1.1, 9, 2.2, 5, 0.5), WHITE, LINE * 0.6)
            glow(sx * 14, 16.5, 6, EMBER, 0.6, 6)
            flat(ell(sx * 14, 16, 1.0, 2.2, 10), "#ffb030")
        tube([(0, 0), (0, 12)], 2.2, 2.0, BONE, LINE * 0.7, sh=0)
        shape(rrect(-1.6, 12, 3.2, 2, 0.8), BONE_SH, LINE * 0.6)
        shape(rrect(-1.1, 14, 2.2, 6, 0.5), WHITE, LINE * 0.6)
        glow(0, 22, 7, EMBER, 0.6, 6); flat(ell(0, 21.5, 1.1, 2.4, 10), "#ffb030")
        skull(0, -3, 6.5, BONE, eyes=EYE_ORANGE)
        for sx in (-1, 1):
            skull(sx * 8, -9, 4, BONE)


def kostnik(pose):
    lean = {"idle": 0, "walk": 4, "attack": 8}[pose]
    shadow(-2, 50)
    cape = [(-20 + lean, 138)] + bez((-20 + lean, 138), (-46, 120), (-56, 70), (-62, 20)) + \
        ragged((-62, 20), (6, 18), 8, 8, 0.4) + bez((6, 18), (8, 60), (12, 100), (18 + lean, 134))
    form(cape, CLOTH_PLUM, sdx=-4, sdy=1, sh=0.2)
    hatch(cape, 2.0, 70, 0.5, g=RED_DK, alpha=0.5)
    for x0 in (-30, -44, -14):
        stroke(bez((x0 + 8, 130), (x0, 100), (x0 - 6, 60), (x0 - 4, 22)), LINE * 0.6, g=RED_DK)
    for i, ang in enumerate(range(96, 176, 11)):
        ln = 40 + (i % 2) * 8
        b0 = (-4 + lean, 126); b1 = pt(b0, ang, ln)
        bone(pt(b0, ang, 12), b1, 4.2, BONE_SH)
        skull(b1[0], b1[1] + 2, 3.6, BONE_SH)
    if pose == "walk":
        fl = ((-4, 62), (-20, 36), (-30, 8)); nl = ((8, 62), (22, 38), (28, 8))
    elif pose == "attack":
        fl = ((-4, 62), (-16, 36), (-24, 8)); nl = ((8, 62), (24, 40), (30, 8))
    else:
        fl = ((-4, 62), (-10, 34), (-12, 8)); nl = ((8, 62), (14, 34), (14, 8))
    bone_leg(*fl, BONE_SH, 9)
    fsh = (-16 + lean, 126)
    if pose == "attack":
        fe = (-30 + lean, 104); fh = (-30 + lean, 80)
    else:
        fe = (-26 + lean, 100); fh = (-22 + lean, 76)
    bundle(fsh, fe, 8, BONE_SH); bundle(fe, fh, 7, BONE_SH)
    claws(fh, -95, 4, 9, 1.8, 14, BONE_SH, curl=25)
    bone_leg(*nl, BONE, 10)
    pelvis = bez((-14, 70), (-16, 62), (-8, 54), (2, 58)) + bez((2, 58), (12, 54), (20, 62), (18, 70)) + \
        bez((18, 70), (12, 76), (-8, 76), (-14, 70))
    form(pelvis, BONE, sdx=-2, sdy=1, sh=0.18)
    for sx in (-1, 1):
        shape(ell(2 + sx * 6.5, 64, 3.2, 3.5, 12), HOLLOW, LINE * 0.6)
    with T(lean * 0.5, 0):
        for i in range(9):
            yy = 72 + i * 6
            shape(rrect(-6, yy, 8, 5, 1.5), BONE_SH, LINE * 0.7)
        cage = ell(4, 104, 26, 24, 36)
        flat(cage, "#2f2b33", 0.8)
        glow(6, 100, 22, "#ff6a2a", 0.55)
        glow(6, 100, 8, "#ffd060", 0.6)
        shape(ell(6, 100, 3.5, 4.5, 14), col("#ff8a3a"), LINE * 0.6)
        for k in range(7):
            yb = 124 - k * 6.5; d = 1 - abs(k - 2.5) / 5
            rib = bez((-2, yb), (-20 * d - 6, yb - 2), (-20 * d - 8, yb - 14), (-6, yb - 16))
            tube(rib, 3.2, 2.6, BONE_SH, LINE * 0.7, sh=0)
        for k in range(7):
            yb = 124 - k * 6.5; d = 1 - abs(k - 2.5) / 5
            rib = bez((-2, yb), (10, yb + 2), (24 * d + 10, yb - 3), (26 + 2 * d, yb - 9))
            tube(rib, 3.6, 2.6, BONE, LINE * 0.75, sh=0.1)
        bone((26, 124), (28, 86), 4.5, BONE)
        skull_belt = [(-12 + i * 7.5, 74 - abs(i - 2) * 1.5) for i in range(5)]
        for (x, y) in skull_belt:
            skull(x, y, 4.2, BONE)
        stroke(bez((-16, 132), (0, 118), (14, 116), (30, 128)), LINE * 0.8)
        for i, (x, y) in enumerate(lib.bez((-12, 132), (0, 120), (14, 118), (28, 128), 5)[1:-1]):
            skull(x, y - 2, 3.4, BONE)
        for (cx, cy, sc) in ((-18, 128, 1.1), (26, 128, 1.3)):
            for (dx, dy, r_) in ((-6, 0, 5), (6, 0, 5), (0, 6, 5.5), (0, -2, 4.5)):
                skull(cx + dx * sc, cy + dy * sc, r_ * sc, BONE if cx > 0 else BONE_SH)
        hx, hy = 12, 152
        tube([(4, 132), (8, 140)], 7, 6, BONE_SH, LINE * 0.7, sh=0)
        skull(hx, hy, 17, BONE, eyes=EYE_ORANGE, jaw_open=0.25 if pose == "attack" else 0.0, side=0.8, lw=LINE)
        band = [(hx - 15, hy + 9), (hx + 16, hy + 10), (hx + 16, hy + 15), (hx - 15, hy + 14)]
        form(band, IRON, sh=0.2)
        for i in range(6):
            bx = hx - 12 + i * 5.4
            shape([(bx - 2, hy + 14), (bx, hy + 24 + (3 if i in (2, 3) else 0)), (bx + 2, hy + 14)], IRON_LT, LINE * 0.6)
        for i in range(5):
            skull(hx - 10 + i * 5.2, hy + 18.5, 2.6, BONE)
        dot(hx + 0.5, hy + 12.5, 1.6, col("#c43a3a"))
    if pose == "attack":
        sh0 = (26 + lean, 128); el = (38 + lean, 132); H = (40 + lean * 0.5, 116); sa = -15
    elif pose == "walk":
        sh0 = (26 + lean, 128); el = (36 + lean, 104); H = (48 + lean, 90); sa = 80
    else:
        sh0 = (26, 128); el = (34, 102); H = (44, 86); sa = 88
    bundle(sh0, el, 8.5, BONE); bundle(el, H, 7.5, BONE)
    base = pt(H, sa + 180, 52 if pose != "attack" else 30)
    top = pt(H, sa, 42 if pose != "attack" else 14)
    bone(base, top, 4.2, BONE_SH)
    chandelier(*pt(top, sa, 4), 1.0 if pose != "attack" else 0.85, rot=(sa - 90) * 0.4)
    shape(ell(H[0], H[1], 4.5, 3.8, 12), BONE, LINE * 0.8)
    claws(H, sa - 90 if pose != "attack" else sa + 90, 4, 6, 1.6, 10, BONE, curl=-60)
    if pose == "attack":
        motion([bez((40, 176), (62, 178), (78, 166), (84, 146)), bez((44, 168), (62, 170), (74, 160), (78, 146))])


def kost_portrait():
    return portrait(kostnik, 14, 154, 2.3, "#4a3530")


# ------------------------------------------------------------------ Vodník Hastrman
OCHRE = col("#b08a48"); VEST = col("#c4a148"); CUP_BLUE = col("#5d86c2"); SOUL = "#cfefff"


def teacup(x, y, s=1.0, rot=0, soul=True):
    with T(x, y, s, rot=rot):
        stroke([(0, 0), (0, 4)], LINE * 0.5)
        cup = bez((-4.5, -1), (-4.2, -4), (-3.5, -6), (-3.2, -7.5)) + [(3.2, -7.5)] + bez((3.2, -7.5), (3.5, -6), (4.2, -4), (4.5, -1))
        if soul:
            glow(0, -9, 4.5, "#7fdcff", 0.6, 5)
            flat(bez((-2.2, -7.5), (-2.4, -10), (0.5, -11), (0.3, -13)) + bez((0.3, -13), (1.5, -11), (2.6, -9.5), (2.2, -7.5)), "#d8f6ff", 0.9)
        form(cup + [(0, 0.2)], WHITE, sdx=-1.2, sdy=0, sh=0.18)
        clip_fill(cup + [(0, 0.2)], [(-5, -6.5), (5, -6.5), (5, -5.3), (-5, -5.3)], CUP_BLUE)
        dot(0.5, -3, 0.9, CUP_BLUE)
        stroke(ell(5.2, -3.5, 1.6, 2, 10, -90, 90), LINE * 0.6)


def frog_foot(a, colr=FROG):
    with T(a[0], a[1], 1.5):
        _frog_foot((0, 0), colr)


def _frog_foot(a, colr):
    x, y = a
    toes = [(x + 12, y - 2.5), (x + 14, y + 0.5), (x + 9, y + 2.5)]
    web = [(x - 3, y + 4)] + [p for t in toes for p in (t, (x + (t[0] - x) * 0.55, y + (t[1] - y) * 0.4))] + [(x - 3, y - 2.5)]
    shape(web, colr, LINE * 0.75)
    for t in toes: shape(ell(t[0], t[1], 1.3, 1.1, 8), FROG_DK, LINE * 0.5)


def vodnik(pose):
    lean = {"idle": 0, "walk": 4, "attack": 6}[pose]
    shadow(2, 44)
    flat(ell(4, 1, 46, 3.2, 30), "#7fb3c9", 0.3)
    tails = [(-6 + lean, 78)] + bez((-6 + lean, 78), (-30, 66), (-40, 40), (-48 + lean * -1.5, 18)) + \
        ragged((-48 + lean * -1.5, 18), (-30, 22), 2, 5, 0.3) + ragged((-30, 22), (-18, 28), 2, 4, 1.4) + \
        bez((-18, 28), (-16, 44), (-10, 58), (6, 62))
    form(tails, COAT_GREEN, sdx=-3, sdy=1, sh=0.2)
    hatch(tails, 2.0, 70, 0.45, g=COAT_GREEN_DK, alpha=0.6)
    stroke(bez((-14, 70), (-24, 56), (-30, 40), (-34, 22)), LINE * 0.6, g=COAT_GREEN_DK)
    drips([(-47 + lean * -1.5, 16), (-36, 18), (-24, 22)], WATER, 5)
    if pose == "walk":
        fl = ((-6, 44), (-16, 26), (-20, 8)); nl = ((12, 44), (24, 28), (28, 8))
    elif pose == "attack":
        fl = ((-6, 44), (-14, 26), (-18, 8)); nl = ((12, 44), (26, 30), (32, 8))
    else:
        fl = ((-6, 44), (-12, 26), (-10, 8)); nl = ((12, 44), (20, 26), (18, 8))
    for leg, c_ in ((fl, FROG_DK), (nl, FROG)):
        tube([leg[0], leg[1]], 13, 10, OCHRE if c_ is FROG else col("#8a6c38"))
        tube([leg[1], leg[2]], 7, 5.5, c_)
        cuff = ell(leg[1][0], leg[1][1] - 1, 6.2, 2.6, 14, rot=-10)
        shape(cuff, OCHRE if c_ is FROG else col("#8a6c38"), LINE * 0.7)
        frog_foot((leg[2][0], leg[2][1] - 2), c_)
    fsh = (-8 + lean, 92)
    if pose == "attack":
        fe = (-22 + lean, 80); fh = (-26 + lean, 62)
    else:
        fe = (-20 + lean, 74); fh = (-16 + lean, 56)
    tube([fsh, fe], 10, 8, COAT_GREEN_DK); tube([fe, fh], 8, 6.5, COAT_GREEN_DK)
    shape(ell(fh[0], fh[1] - 2, 3.5, 4, 12), FROG_DK, LINE * 0.8)
    teacup(fh[0], fh[1] - 4, 1.1)
    with T(lean, 0):
        belly = ell(6, 68, 27, 29, 40)
        form(belly, VEST, sdx=-5, sdy=2, sh=0.18)
        hatch(ell(-6, 56, 18, 20, 20), 2.0, 50, 0.45, g=col("#8a6a28"), alpha=0.6)
        for by in (88, 79, 70, 61):
            shape(ell(22 + (by - 74) * -0.05, by, 1.5, 1.5, 10), GOLD, LINE * 0.6)
        coat = [(-18, 98)] + bez((-18, 98), (-30, 80), (-30, 56), (-22, 44)) + [(-8, 42)] + \
            bez((-8, 42), (-12, 60), (-8, 84), (6, 96)) + [(16, 100)]
        form(coat, COAT_GREEN, sdx=-3, sdy=1, sh=0.2)
        panel = [(18, 100), (30, 94), (37, 70), (33, 46), (26, 43), (29, 70), (23, 92)]
        form(panel, COAT_GREEN, sdx=-2, sdy=0, sh=0.15)
        lapel = [(6, 96), (16, 101), (24, 98), (13, 86)]
        shape(lapel, COAT_GREEN_DK, LINE * 0.8)
        belt = bez((-22, 48), (-4, 42), (18, 42), (32, 50)) + bez((32, 50), (32, 46), (18, 38), (-22, 44))
        shape(belt + [(-22, 48)], WOOD_DK, LINE * 0.8)
        shape(rrect(8, 39.5, 6, 5, 1), GOLD, LINE * 0.6)
        for i, (cx, ang) in enumerate(((-16, 8), (-2, -4), (22, 6), (30, -10))):
            cy = 44 - abs(cx - 5) * -0.05 - (2 if i in (1, 2) else 0)
            stroke([(cx, cy), (cx, cy - 6 - i % 2 * 3)], LINE * 0.6)
            teacup(cx, cy - 6 - i % 2 * 3, 1.3, rot=ang)
        drips([(-26, 46), (-12, 40)], WATER, 4)
        hx, hy = 18, 114
        cr = [(0, 0)]
        for sx in (-1,):
            pass
        for (x0, y0) in ((-2, 128), (2, 130), (-6, 124)):
            stroke(bez((hx + x0 - 8, y0), (hx + x0 - 16, y0 - 14), (hx + x0 - 14, y0 - 30), (hx + x0 - 20, y0 - 44)), LINE * 1.6, g=MOSS)
        head = bez((hx - 18, hy + 4), (hx - 18, hy + 18), (hx - 4, hy + 24), (hx + 10, hy + 20)) + \
            bez((hx + 10, hy + 20), (hx + 20, hy + 16), (hx + 26, hy + 6), (hx + 25, hy - 2)) + \
            bez((hx + 25, hy - 2), (hx + 22, hy - 14), (hx + 4, hy - 18), (hx - 8, hy - 16)) + \
            bez((hx - 8, hy - 16), (hx - 18, hy - 12), (hx - 20, hy - 6), (hx - 18, hy + 4))
        form(head, FROG, sdx=-3, sdy=1.5, sh=0.2)
        clip_fill(head, ell(hx + 6, hy - 14, 18, 8, 20), FROG_BELLY)
        for (sx, sy, r_) in ((-8, 10, 2.2), (-12, 2, 1.6), (0, 16, 1.4), (-4, 4, 1.2)):
            shape(ell(hx + sx, hy + sy, r_, r_ * 0.8, 10), FROG_DK, 0)
        mo = 5 if pose == "attack" else 0
        mouth = bez((hx - 8, hy - 2), (hx + 4, hy - 6 - mo), (hx + 16, hy - 6 - mo), (hx + 25, hy - 2))
        if mo:
            m2 = mouth + bez((hx + 25, hy - 2), (hx + 16, hy - 4), (hx + 4, hy - 4), (hx - 8, hy - 2))
            shape(m2, MOUTH_DK, LINE * 0.8)
        for i in range(7):
            t = 0.12 + i * 0.12
            q = mouth[int(t * (len(mouth) - 1))]
            shape([(q[0] - 1.1, q[1] + 0.3), (q[0] + 1.1, q[1] + 0.3), (q[0], q[1] - 2.6)], BONE, LINE * 0.4)
            if mo:
                shape([(q[0] - 1, q[1] - mo - 0.8 + abs(i - 3) * 0.9), (q[0] + 1, q[1] - mo - 0.8 + abs(i - 3) * 0.9), (q[0], q[1] - mo + 1.6 + abs(i - 3) * 0.9)], BONE, LINE * 0.4)
        stroke(mouth, LINE)
        stroke([(hx + 18, hy + 3), (hx + 19, hy + 2.5)], LINE * 0.8)
        for (ex, ey, r_) in ((hx + 1, hy + 20, 5.5), (hx + 12, hy + 21, 6.5)):
            shape(ell(ex, ey, r_ + 1.2, r_ + 1.2, 18), FROG, LINE * 0.9)
            eye(ex + 0.5, ey + 0.5, r_ * 0.75, EYE_YELLOW, halo=2.0)
            flat(ell(ex + 0.5, ey + 0.5, r_ * 0.6, r_ * 0.14, 12), "#2a1a12")
            lid = ell(ex, ey, r_ + 1.3, r_ + 1.3, 14, 0, 180) + [(ex - r_ - 1.3, ey + r_ * 0.4), (ex + r_ + 1.3, ey - r_ * 0.05)]
            shape(lid, FROG_DK, LINE * 0.9)
        brim = ell(hx + 2, hy + 27, 20, 4, 30, rot=6)
        crown = [(hx - 9, hy + 27), (hx - 8, hy + 46), (hx + 12, hy + 48), (hx + 13, hy + 28)]
        form(crown, HAT_RED, sdx=-3, sdy=0, sh=0.2)
        shape([(hx - 8.6, hy + 30), (hx + 13, hy + 31), (hx + 13, hy + 35), (hx - 8.4, hy + 34)], COAT_GREEN_DK, LINE * 0.6)
        form(brim, HAT_RED, sdx=-2, sdy=1, sh=0.2)
        shape(ell(hx + 2, hy + 47, 10, 2.4, 20, rot=6), RED_DK, LINE * 0.7)
        drips([(hx - 16, hy + 25), (hx + 21, hy + 28)], WATER, 4)
        pb = (hx + 30, hy - 10)
        tube([(hx + 21, hy - 3), (hx + 27, hy - 9), pb], 1.6, 1.6, WOOD_DK, LINE * 0.6, sh=0)
        shape(rrect(pb[0] - 2.5, pb[1] - 1, 5, 7, 1.5), WOOD, LINE * 0.7)
        glow(pb[0], pb[1] + 6, 3, EMBER, 0.6, 4)
        for i in range(3):
            stroke(bez((pb[0], pb[1] + 7 + i * 6), (pb[0] + 4, pb[1] + 10 + i * 6), (pb[0] - 3, pb[1] + 12 + i * 6), (pb[0] + 1, pb[1] + 14 + i * 6)), LINE * 0.6, g=col("#c7c4bd"), alpha=0.7 - i * 0.2)
    sh0 = (20 + lean, 94)
    if pose == "attack":
        el = (36 + lean, 112); hd = (40 + lean, 134); ha = 80
    elif pose == "walk":
        el = (34 + lean, 76); hd = (46 + lean, 66); ha = -30
    else:
        el = (32, 74); hd = (38, 58); ha = -70
    tube([sh0, el], 11, 9, COAT_GREEN); tube([el, hd], 9, 7.5, COAT_GREEN)
    shape(ell(hd[0], hd[1], 4.8, 4.5, 14), FROG, LINE * 0.8)
    for i in range(4):
        f = pt(hd, ha - 30 + i * 20, 8)
        tube([hd, f], 2.2, 1.6, FROG, LINE * 0.6, sh=0)
        shape(ell(f[0], f[1], 1.3, 1.3, 8), FROG_DK, LINE * 0.5)
    web = [hd] + [pt(hd, ha - 30 + i * 20, 6) for i in range(4)]
    fill(web, FROG_BELLY, 0.6)
    cuffp = pt(el, math.degrees(math.atan2(hd[1] - el[1], hd[0] - el[0])), 12)
    if pose == "attack":
        ox, oy = hd[0] + 4, hd[1] + 14
        glow(ox, oy, 18, "#7fd0ff", 0.4)
        orb = ell(ox, oy, 10, 9, 30)
        form(orb, WATER, sh=0.15)
        for k in range(3):
            stroke(ell(ox, oy, 10 - k * 3, 9 - k * 2.6, 20, 30 + k * 40, 250 + k * 40), LINE * 0.6, g=WATER_LT)
        drips([(ox - 6, oy - 8), (ox + 5, oy - 9)], WATER, 5)
    else:
        drips([(hd[0] + 2, hd[1] - 9)], WATER, 6)


def vod_portrait():
    return portrait(vodnik, 20, 124, 2.4, "#2f4a46")


# ------------------------------------------------------------------ registry
SPRITES = boss_items("klekanice", klekanice, 320) + boss_items("kostnik", kostnik, 384) + boss_items("vodnik", vodnik, 352)
PORTRAITS = [("boss_klekanice", 256, 256, klek_portrait()), ("boss_kostnik", 256, 256, kost_portrait()),
             ("boss_vodnik", 256, 256, vod_portrait())]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
