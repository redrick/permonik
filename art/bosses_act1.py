"""Act I bosses: Klekánice, Kostník ze Sedlce, Vodník Hastrman."""
import math
import lib
from bosses_kit import *
from bestiary_kit import ALL, view_of


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


def hag_foot(x, y, colr, front=False):
    if front:
        shape(ell(x, y + 2.5, 5, 3.4, 14), colr, LINE * 0.8)
        claws((x, y + 1), -90, 3, 4, 1.3, 14, HAG_DK, curl=0)
    else:
        shape(ell(x, y + 3, 7, 3.2, 14), colr, LINE * 0.8)
        claws((x + 5, y + 2.5), -5, 3, 6, 1.4, 10, HAG_DK, curl=-30)


# lean, sway, near arm (elbow, hand, claw angle) or None, bell rot, hem seed, peeking foot (x, colour)
KLEK = {
    "idle": (0, 0, ((28, 74), (40, 56), -60), 4, 1.3, None),
    "walk": (6, -8, ((30, 78), (46, 66), -35), 18, 1.3, (30, HAG)),
    "walk2": (3, -2, ((28, 76), (38, 58), -65), 9, 1.7, None),
    "walk3": (5, 6, ((24, 76), (30, 58), -80), -12, 2.1, (26, HAG_DK)),
    "walk4": (2, 1, ((28, 76), (38, 59), -60), -6, 0.9, None),
    "windup": (-5, 6, ((10, 126), (0, 146), 115), 32, 1.3, None),
    "attack": (7, -5, ((22, 120), (14, 142), 100), -25, 1.3, None),
}


def klekanice(pose):
    base, v = view_of(pose)
    if v:
        return klek_fb(base, v == "b")
    pose = base
    lean, sway, arm, brot, seed, foot = KLEK[pose]
    shadow(2, 38)
    glow_ell(-2, 8, 40, 8, "#bfe0ff", 0.22)
    if pose == "attack":
        fs = (26 + lean, 88); fe = (40 + lean, 96); fh = (53 + lean, 92)
        tube([fs, fe], 5.5, 4.4, HAG); tube([fe, fh], 4.4, 3.4, HAG)
        shape(ell(fh[0], fh[1], 3.4, 2.6, 12, rot=-10), HAG, LINE * 0.8)
        claws(fh, -5, 4, 11, 1.5, 16, HAG_DK, curl=-35)
    elif pose == "windup":
        fs = (26 + lean, 88); fe = (34 + lean, 80); fh = (41 + lean, 88)
        tube([fs, fe], 5.5, 4.4, HAG); tube([fe, fh], 4.4, 3.4, HAG)
        shape(ell(fh[0], fh[1], 3.2, 2.6, 12, rot=60), HAG, LINE * 0.8)
        claws(fh, 70, 4, 6, 1.5, 16, HAG_DK, curl=-60)
    if foot:
        hag_foot(foot[0] + lean * 0.5, 2, foot[1])
    body = ragged((-34 + sway, 16), (26 + sway * 0.2, 15), 7, 10, seed) + \
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
    (ex, ey), (hx_, hy_), ca = arm
    e0 = (ex + lean, ey); h0 = (hx_ + lean, hy_)
    tube([s0, e0], 6.0, 4.8, HAG); tube([e0, h0], 4.8, 3.6, HAG)
    shape(ell(h0[0], h0[1], 3.4, 2.8, 12, rot=ca), HAG, LINE * 0.8)
    claws(h0, ca + 150, 3, 5, 1.2, 10, HAG_DK, curl=-60)
    bell(h0[0], h0[1] - 1, 1.3, rot=brot, ringing=pose == "attack")
    sleeve = [(s0[0] - 8, s0[1] + 8)] + bez((s0[0] - 8, s0[1] + 8), (s0[0] + 6, s0[1] + 12), (e0[0] + 4, e0[1] + 6), (e0[0] + 3, e0[1] - 1)) + \
        ragged((e0[0] + 3, e0[1] - 1), (e0[0] - 6, e0[1] - 4), 3, 4, 2) + \
        bez((e0[0] - 6, e0[1] - 4), (s0[0] - 2, s0[1] - 14), (s0[0] - 12, s0[1] - 8), (s0[0] - 8, s0[1] + 8))
    form(sleeve, SHEET, sdx=-2, sdy=1.5, sh=0.16)
    if pose == "attack":
        motion([bez((36 + lean, 74), (46 + lean, 76), (56 + lean, 80), (62 + lean, 84)),
                bez((36 + lean, 82), (44 + lean, 84), (52 + lean, 86), (58 + lean, 88))])


# body rot, hem sway, hem seed, peeking foot x, near arm (elbow, hand), bell rot; back overrides
KLEK_FB = {
    "idle": (0, 0, 1.3, None, ((40, 82), (42, 60)), 0),
    "walk": (-2.5, -4, 1.3, -13, ((41, 84), (44, 64)), 14),
    "walk2": (-1, -1, 1.7, None, ((40, 82), (42, 60)), 6),
    "walk3": (2.5, 4, 2.1, 13, ((39, 80), (40, 58)), -12),
    "walk4": (1, 1, 0.9, None, ((40, 82), (42, 61)), -5),
    "windup": (-2, 2, 1.3, None, ((46, 126), (36, 152)), 30),
    "attack": (1.5, -2, 1.3, None, ((34, 98), (20, 110)), -20),
}
KLEK_B = {"attack": (1.5, -2, 1.3, None, ((44, 108), (42, 128)), -30)}


def klek_fb(pose, back):
    rot, sw, seed, foot, (el, hd), brot = (KLEK_B if back else {}).get(pose, KLEK_FB[pose])
    shadow(0, 36)
    glow_ell(0, 8, 40, 8, "#bfe0ff", 0.22)
    att = pose == "attack"

    def bell_arm():
        s0 = (26, 104)
        tube([s0, el], 12, 10, SHEET, sh=0.16)
        w = pt(el, math.degrees(math.atan2(hd[1] - el[1], hd[0] - el[0])), 0.55 * math.dist(el, hd))
        tube([el, w], 10, 9, SHEET, sh=0.16)
        tube([w, hd], 4.6, 3.6, HAG)
        stroke(ragged(pt(w, 0, -5), pt(w, 0, 5), 2, 3, 1), LINE * 0.6)
        bell(hd[0], hd[1] - 1, 1.6 if att and not back else 1.3, rot=brot, ringing=att)
        shape(ell(hd[0], hd[1], 3.4, 2.8, 12), HAG, LINE * 0.8)
        claws(hd, 90 if pose == "windup" else -90, 3, 4, 1.2, 10, HAG_DK, curl=50)

    def claw_arm():
        if pose not in ("attack", "windup"):
            return
        s1 = (-26, 104)
        if att:
            e1, h1, a1, k = (-34, 92), (-22, 84), -60, 1.5
        else:
            e1, h1, a1, k = (-40, 96), (-38, 112), 100, 1.0
        tube([s1, e1], 12, 10, SHEET, sh=0.16)
        tube([e1, h1], 5.0 * k, 3.8 * k, HAG)
        shape(ell(h1[0], h1[1], 3.4 * k, 2.8 * k, 12), HAG, LINE * 0.8)
        claws(h1, a1, 4, 9 * k, 1.5, 16, HAG_DK, curl=-35)

    with T(0, 0, 1, flip=back):
        if foot is not None:
            with T(foot, 0, 1.5):
                hag_foot(0, 0.5, HAG, front=not back)
        if back:
            bell_arm(); claw_arm()
        with T(0, 0, 1, rot=rot):
            body = ragged((-38 + sw, 16), (38 + sw, 16), 9, 10, seed) + \
                bez((38 + sw, 16), (44, 48), (40, 84), (36, 106)) + bez((36, 106), (32, 136), (16, 148), (0, 148)) + \
                bez((0, 148), (-16, 148), (-32, 136), (-36, 106)) + bez((-36, 106), (-40, 84), (-44, 48), (-38 + sw, 16))
            form(body, SHEET, sdx=0, sdy=2, sh=0.16)
            C.saveState(); C.clipPath(poly(body), stroke=0, fill=0)
            flat(ell(sw * 0.5, -6, 56, 38, 30), "#6f7f99", 0.28)
            for sx in (-1, 1):
                hatch(ell(sx * 34, 70, 14, 70, 20), 2.0, 90 - sx * 28, 0.5, g=SHEET_SH, alpha=0.75)
            if back:
                flat(ell(0, 140, 30, 14, 24), "#6f7f99", 0.18)
                hatch(ell(0, 126, 24, 20, 20), 2.2, 70, 0.45, g=SHEET_SH, alpha=0.55)
            C.restoreState()
            for sx in (-1, 1):
                for (x0, y0, x1, y1) in ((8, 132, 20 + sw * sx, 12), (20, 112, 32 + sw * sx, 20), (4, 92, 8 + sw * sx * 0.5, 14)):
                    stroke(bez((sx * x0, y0), (sx * x0 - 2 * sx, y0 - 30), (sx * x1 + 3 * sx, y1 + 30), (sx * x1, y1)), LINE * 0.6, g=SHEET_SH)
            if back:
                stroke(bez((0, 147), (1, 134), (-1, 118), (0, 102)), LINE * 0.6, g=SHEET_SH)
                for sx in (-1, 1):
                    stroke(bez((sx * 4, 146), (sx * 14, 136), (sx * 22, 122), (sx * 26, 104)), LINE * 0.55, g=SHEET_SH)
            else:
                hx, hy = 0, 108
                hole = ell(hx, hy, 11.5, 14, 24)
                shape(hole, HOLLOW, LINE)
                C.saveState(); C.clipPath(poly(hole), stroke=0, fill=0)
                fc = bez((hx, hy + 12), (hx + 8, hy + 12), (hx + 9, hy + 2), (hx + 8, hy - 4)) + \
                    bez((hx + 8, hy - 4), (hx + 7, hy - 12), (hx + 3, hy - 15), (hx, hy - 15)) + \
                    bez((hx, hy - 15), (hx - 3, hy - 15), (hx - 7, hy - 12), (hx - 8, hy - 4)) + \
                    bez((hx - 8, hy - 4), (hx - 9, hy + 2), (hx - 8, hy + 12), (hx, hy + 12))
                form(fc, HAG, sdx=0, sdy=1, sh=0.25)
                for sx in (-1, 1):
                    hatch(ell(hx + sx * 6, hy - 4, 2.5, 5, 12), 1.0, 60, 0.4, alpha=0.6)
                    stroke(bez((hx + sx * 9, hy + 10), (hx + sx * 7, hy + 2), (hx + sx * 9.5, hy - 6), (hx + sx * 8, hy - 16)), LINE * 0.7, g=HAIR_GREY)
                mo = 1.5 if att else 0
                m = bez((hx - 5, hy - 9), (hx - 2, hy - 7.5), (hx + 2, hy - 7.5), (hx + 5, hy - 9)) + \
                    bez((hx + 5, hy - 9), (hx + 2, hy - 12 - mo), (hx - 2, hy - 12 - mo), (hx - 5, hy - 9))
                shape(m, MOUTH_DK, LINE * 0.6)
                for tx in (hx - 2.5, hx + 2):
                    shape([(tx - 0.5, hy - 8.5), (tx + 0.6, hy - 8.5), (tx, hy - 11)], BONE, LINE * 0.3)
                C.restoreState()
                nose = [(hx - 1.6, hy + 4)] + bez((hx - 1.6, hy + 4), (hx - 2.8, hy - 1), (hx - 2.6, hy - 6), (hx, hy - 9)) + \
                    bez((hx, hy - 9), (hx + 2.6, hy - 6), (hx + 2.8, hy - 1), (hx + 1.6, hy + 4))
                shape(nose, HAG, LINE * 0.8)
                for sx in (-1, 1):
                    ex, ey = hx + sx * 4.6, hy + 4.5
                    shape(ell(ex, ey, 3.0, 2.4, 12), HAG_DK, 0)
                    eye(ex, ey, 1.7, EYE_YELLOW, halo=3.2)
                    stroke([(ex - 2.4 * sx, ey + 2.6), (ex + 2.6 * sx, ey + 1.8)], LINE * 0.7)
                for d in (0, 1):
                    stroke(bez((hx - 16, hy - 12 - d * 3), (hx - 8, hy - 19 - d * 3), (hx + 8, hy - 19 - d * 3), (hx + 16, hy - 12 - d * 3)), LINE * 0.5, g=SHEET_SH)
            if not back:
                claw_arm()
            if not back:
                bell_arm()
            if att and not back:
                for r_ in (20, 26):
                    stroke(ell(hd[0], hd[1] - 14, r_, r_ * 0.8, 16, -40, 40), LINE * 0.6, alpha=0.55)
                    stroke(ell(hd[0], hd[1] - 14, r_, r_ * 0.8, 16, 140, 220), LINE * 0.6, alpha=0.55)


klekanice.poses = ALL


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


# lean, far leg, near leg, far arm (elbow, hand), near arm (elbow, hand, staff angle), cape sway, hem seed
KOST = {
    "idle": (0, ((-4, 62), (-10, 34), (-12, 8)), ((8, 62), (14, 34), (14, 8)),
             ((-26, 100), (-22, 76)), ((34, 102), (44, 86), 88), 0, 0.4),
    "walk": (4, ((-4, 62), (-20, 36), (-30, 8)), ((8, 62), (22, 38), (28, 8)),
             ((-16, 100), (-6, 78)), ((30, 102), (38, 86), 96), -4, 0.4),
    "walk2": (3, ((-4, 62), (2, 40), (-8, 18)), ((8, 62), (10, 34), (6, 8)),
              ((-22, 100), (-16, 76)), ((32, 102), (42, 86), 91), -8, 1.1),
    "walk3": (4, ((-4, 62), (10, 38), (18, 8)), ((8, 62), (-6, 36), (-18, 8)),
              ((-30, 102), (-34, 80)), ((36, 104), (48, 90), 80), -5, 1.8),
    "walk4": (3, ((-4, 62), (-2, 34), (-4, 8)), ((8, 62), (16, 40), (6, 18)),
              ((-24, 100), (-20, 76)), ((34, 102), (44, 87), 86), -1, 2.5),
    "windup": (-4, ((-4, 62), (-14, 34), (-20, 8)), ((8, 62), (18, 36), (22, 8)),
               ((-34, 108), (-40, 90)), ((40, 110), (46, 124), 102), 0, 0.4),
    "attack": (8, ((-4, 62), (-16, 36), (-24, 8)), ((8, 62), (24, 40), (30, 8)),
               ((-30, 104), (-30, 80)), ((38, 132), (40, 116), -15), -6, 0.4),
}


def kostnik(pose):
    base, v = view_of(pose)
    if v:
        return kost_fb(base, v == "b")
    pose = base
    lean, fl, nl, (fe, fh), (el, H, sa), cs, seed = KOST[pose]
    shadow(-2, 50)
    cape = [(-20 + lean, 138)] + bez((-20 + lean, 138), (-46, 120), (-56 + cs * 0.5, 70), (-62 + cs, 20)) + \
        ragged((-62 + cs, 20), (6 + cs * 0.3, 18), 8, 8, seed) + bez((6 + cs * 0.3, 18), (8, 60), (12, 100), (18 + lean, 134))
    form(cape, CLOTH_PLUM, sdx=-4, sdy=1, sh=0.2)
    hatch(cape, 2.0, 70, 0.5, g=RED_DK, alpha=0.5)
    for x0 in (-30, -44, -14):
        stroke(bez((x0 + 8, 130), (x0, 100), (x0 - 6 + cs * 0.5, 60), (x0 - 4 + cs, 22)), LINE * 0.6, g=RED_DK)
    for i, ang in enumerate(range(96, 176, 11)):
        ln = 40 + (i % 2) * 8
        b0 = (-4 + lean, 126); b1 = pt(b0, ang, ln)
        bone(pt(b0, ang, 12), b1, 4.2, BONE_SH)
        skull(b1[0], b1[1] + 2, 3.6, BONE_SH)
    bone_leg(*fl, BONE_SH, 9)
    fsh = (-16 + lean, 126)
    fe = (fe[0] + lean, fe[1]); fh = (fh[0] + lean, fh[1])
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
        skull(hx, hy, 17, BONE, eyes=EYE_ORANGE, jaw_open={"attack": 0.25, "windup": 0.12}.get(pose, 0.0), side=0.8, lw=LINE)
        band = [(hx - 15, hy + 9), (hx + 16, hy + 10), (hx + 16, hy + 15), (hx - 15, hy + 14)]
        form(band, IRON, sh=0.2)
        for i in range(6):
            bx = hx - 12 + i * 5.4
            shape([(bx - 2, hy + 14), (bx, hy + 24 + (3 if i in (2, 3) else 0)), (bx + 2, hy + 14)], IRON_LT, LINE * 0.6)
        for i in range(5):
            skull(hx - 10 + i * 5.2, hy + 18.5, 2.6, BONE)
        dot(hx + 0.5, hy + 12.5, 1.6, col("#c43a3a"))
    sh0 = (26 + lean, 128); el = (el[0] + lean, el[1])
    H = (H[0] + lean * (0.5 if pose == "attack" else 1), H[1])
    bundle(sh0, el, 8.5, BONE); bundle(el, H, 7.5, BONE)
    base = pt(H, sa + 180, 52 if pose != "attack" else 30)
    top = pt(H, sa, {"attack": 14, "windup": 24}.get(pose, 42))
    bone(base, top, 4.2, BONE_SH)
    chandelier(*pt(top, sa, 4), 1.0 if pose != "attack" else 0.85, rot=(sa - 90) * 0.4)
    shape(ell(H[0], H[1], 4.5, 3.8, 12), BONE, LINE * 0.8)
    claws(H, sa - 90 if pose != "attack" else sa + 90, 4, 6, 1.6, 10, BONE, curl=-60)
    if pose == "attack":
        motion([bez((40, 176), (62, 178), (78, 166), (84, 146)), bez((44, 168), (62, 170), (74, 160), (78, 146))])


def bony_foot_fb(a, sc, colr):
    x, y = a
    with T(x, y, sc):
        for dx in (-3.2, 0, 3.2):
            tube([(dx * 0.6, 0), (dx * 1.1, -4.5)], 2.8, 2.0, colr, LINE * 0.7, sh=0)
            shape(ell(dx * 1.1, -5, 1.5, 1.3, 8), colr, LINE * 0.5)
        shape(ell(0, 1.2, 4.2, 3.2, 12), colr, LINE * 0.8)


# per leg (-x, +x): knee (x, y), ankle (x, y), foot scale
KOST_LEGS = {
    "stand": (((-13, 34), (-13, 8), 1.0), ((13, 34), (13, 8), 1.0)),
    "c1": (((-12, 37), (-11, 12), 0.9), ((14, 32), (15, 5), 1.1)),
    "p1": (((-11, 42), (-10, 22), 1.0), ((13, 34), (13, 8), 1.0)),
    "c2": (((-14, 32), (-15, 5), 1.1), ((12, 37), (11, 12), 0.9)),
    "p2": (((-13, 34), (-13, 8), 1.0), ((11, 42), (10, 22), 1.0)),
    "brace": (((-18, 34), (-22, 8), 1.0), ((18, 34), (22, 8), 1.0)),
    "lunge": (((-16, 36), (-24, 10), 0.95), ((16, 30), (18, 4), 1.12)),
}
# legs, body rot, far arm (elbow, hand, claw angle), near arm (elbow, hand), staff angle, chandelier scale, cape sway
KOST_FB = {
    "idle": ("stand", 0, ((-34, 104), (-35, 80), -90), ((36, 104), (38, 86)), 90, 1.0, 0),
    "walk": ("c1", -1.5, ((-34, 106), (-33, 84), -90), ((36, 104), (39, 84)), 92, 1.0, -3),
    "walk2": ("p1", -0.5, ((-34, 104), (-35, 80), -90), ((36, 104), (38, 86)), 90, 1.0, -1),
    "walk3": ("c2", 1.5, ((-34, 102), (-36, 78), -90), ((36, 106), (37, 88)), 88, 1.0, 3),
    "walk4": ("p2", 0.5, ((-34, 104), (-35, 80), -90), ((36, 104), (38, 86)), 90, 1.0, 1),
    "windup": ("brace", 0, ((-42, 112), (-44, 128), 90), ((46, 116), (44, 136)), 100, 1.0, 0),
    "attack": ("lunge", 1, ((-38, 108), (-28, 92), -60), ((30, 112), (16, 118)), 150, 1.25, 0),
}
KOST_B = {"attack": ("lunge", 1, ((-40, 112), (-44, 128), 90), ((40, 118), (36, 140)), 70, 1.0, 0)}


def kost_fb(pose, back):
    legs, rot, (fe, fh, fa), (el, H), sa, cs_, csw = (KOST_B if back else {}).get(pose, KOST_FB[pose])
    att = pose == "attack"
    shadow(0, 46)

    def staff_arm():
        sh0 = (26, 128)
        bundle(sh0, el, 8.5, BONE); bundle(el, H, 7.5, BONE)
        if att and not back:
            top = pt(H, sa, 10)
            chandelier(*pt(top, sa, 4), cs_, rot=(sa - 90) * 0.4)
        else:
            short = pose in ("windup", "attack")
            base = pt(H, sa + 180, 40 if short else 52)
            top = pt(H, sa, 24 if short else 42)
            bone(base, top, 4.2, BONE_SH)
            chandelier(*pt(top, sa, 4), 1.0, rot=(sa - 90) * 0.4)
        shape(ell(H[0], H[1], 4.5, 3.8, 12), BONE, LINE * 0.8)
        claws(H, -90 if pose != "windup" else 90, 4, 6, 1.6, 10, BONE, curl=-60)
        if att and not back:
            motion([bez((60, 150), (62, 130), (50, 116), (34, 112)), bez((54, 156), (58, 136), (46, 122), (30, 120))])

    def claw_arm():
        bundle((-26, 128), fe, 8, BONE_SH if back else BONE); bundle(fe, fh, 7, BONE_SH if back else BONE)
        claws(fh, fa, 4, 9 * (1.3 if att else 1), 1.8, 14, BONE, curl=25)

    def fan(c):
        for i, ang in enumerate(range(22, 170, 12)):
            ln = 38 + (i % 2) * 8
            b0 = (0, 124); b1 = pt(b0, ang, ln)
            bone(pt(b0, ang, 16), b1, 4.2, c)
            skull(b1[0], b1[1] + 2, 3.6, c)

    with T(0, 0, 1, flip=back):
        with T(0, 0, 1, rot=rot):
            cape = [(-30, 136)] + bez((-30, 136), (-40, 110), (-46, 60), (-50 + csw, 20)) + \
                ragged((-50 + csw, 20), (50 + csw, 20), 10, 8, 0.4 + csw * 0.3) + \
                bez((50 + csw, 20), (46, 60), (40, 110), (30, 136))
            if not back:
                fan(BONE_SH)
                form(cape, CLOTH_PLUM, sdx=0, sdy=1, sh=0.2)
                hatch(cape, 2.0, 80, 0.5, g=RED_DK, alpha=0.5)
            else:
                staff_arm(); claw_arm()
            for side, ((kx, ky), (ax, ay), sc) in zip((-1, 1), KOST_LEGS[legs]):
                hip = (side * 10, 62)
                bundle(hip, (kx, ky), 9, BONE)
                bundle((kx, ky), (ax, ay), 8, BONE)
                skull(kx, ky + 1, 5.6 * sc, BONE, sockets=HOLLOW if not back else BONE_SH)
                bony_foot_fb((ax, ay), sc, BONE)
            if back:
                form(cape, CLOTH_PLUM, sdx=0, sdy=1, sh=0.2)
                hatch(cape, 2.0, 80, 0.5, g=RED_DK, alpha=0.5)
                for x0 in (-24, -8, 8, 24):
                    stroke(bez((x0 * 0.6, 132), (x0 * 0.8, 100), (x0, 60), (x0 * 1.3 + csw, 22)), LINE * 0.6, g=RED_DK)
                fan(BONE)
                for sx in (-1, 1):
                    for (dx, dy, r_) in ((-6, 0, 5), (6, 0, 5), (0, 6, 5.5)):
                        skull(sx * 26 + dx * 1.1, 128 + dy * 1.1, r_ * 1.1, BONE_SH, sockets=BONE_DK)
            else:
                pelvis = bez((-18, 70), (-20, 60), (-8, 54), (0, 58)) + bez((0, 58), (8, 54), (20, 60), (18, 70)) + \
                    bez((18, 70), (10, 76), (-10, 76), (-18, 70))
                form(pelvis, BONE, sdx=0, sdy=1, sh=0.18)
                for sx in (-1, 1):
                    shape(ell(sx * 7, 64, 3.4, 3.6, 12), HOLLOW, LINE * 0.6)
                for i in range(4):
                    shape(rrect(-4, 76 + i * 6, 8, 5, 1.5), BONE_SH, LINE * 0.7)
                cage = ell(0, 104, 28, 24, 36)
                flat(cage, "#2f2b33", 0.8)
                glow(0, 100, 22, "#ff6a2a", 0.55)
                glow(0, 100, 8, "#ffd060", 0.6)
                shape(ell(0, 100, 3.5, 4.5, 14), col("#ff8a3a"), LINE * 0.6)
                for k in range(7):
                    yb = 124 - k * 6.5; d = 1 - abs(k - 2.5) / 6
                    for sx in (-1, 1):
                        rib = bez((sx * 2, yb), (sx * 14, yb + 2), (sx * (26 * d + 4), yb - 3), (sx * (26 * d + 2), yb - 10))
                        tube(rib, 3.4, 2.6, BONE, LINE * 0.7, sh=0.1)
                bone((0, 128), (0, 92), 4.5, BONE)
                for i in range(5):
                    skull(-16 + i * 8, 74 - abs(i - 2) * 1.5, 4.2, BONE)
                stroke(bez((-30, 128), (-14, 118), (14, 118), (30, 128)), LINE * 0.8)
                for x, y in lib.bez((-26, 128), (-12, 120), (12, 120), (26, 128), 5)[1:-1]:
                    skull(x, y - 2, 3.4, BONE)
                for sx in (-1, 1):
                    for (dx, dy, r_) in ((-6, 0, 5), (6, 0, 5), (0, 6, 5.5), (0, -2, 4.5)):
                        skull(sx * 26 + dx * 1.2, 128 + dy * 1.2, r_ * 1.2, BONE)
            hx, hy = 0, 152
            tube([(0, 132), (0, 140)], 7, 6, BONE_SH, LINE * 0.7, sh=0)
            if back:
                cr = ell(hx, hy, 17, 16, 30)
                form(cr, BONE, sdx=0, sdy=1, sh=0.2)
                stroke(bez((hx, hy + 15), (hx + 2, hy + 6), (hx - 2, hy), (hx + 1, hy - 8)), LINE * 0.5, g=BONE_DK)
                stroke(bez((hx - 12, hy - 4), (hx - 6, hy - 6), (hx + 6, hy - 6), (hx + 12, hy - 4)), LINE * 0.5, g=BONE_DK)
                shape([(hx - 9, hy - 14), (hx + 9, hy - 14), (hx + 7, hy - 18), (hx - 7, hy - 18)], BONE_SH, LINE * 0.7)
            else:
                skull(hx, hy, 17, BONE, eyes=EYE_ORANGE, jaw_open={"attack": 0.25, "windup": 0.12}.get(pose, 0.0), lw=LINE)
            band = [(hx - 16, hy + 9), (hx + 16, hy + 9), (hx + 16, hy + 14), (hx - 16, hy + 14)]
            form(band, IRON, sh=0.2)
            for i in range(7):
                bx = hx - 13.5 + i * 4.5
                shape([(bx - 2, hy + 14), (bx, hy + 24 + (3 if i == 3 else 0)), (bx + 2, hy + 14)], IRON_LT, LINE * 0.6)
            for i in range(5):
                skull(hx - 10.4 + i * 5.2, hy + 11.5 if back else hy + 18.5, 2.6, BONE)
            if not back:
                dot(hx, hy + 12.5, 1.6, col("#c43a3a"))
                claw_arm(); staff_arm()


kostnik.poses = ALL


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


# lean, rock, far leg, near leg, far arm (elbow, hand), near arm (elbow, hand, angle), tail sway, drip length
VOD = {
    "idle": (0, 0, ((-6, 44), (-12, 26), (-10, 8)), ((12, 44), (20, 26), (18, 8)),
             ((-20, 74), (-16, 56)), ((32, 74), (38, 58), -70), 0, 5),
    "walk": (4, -2, ((-6, 44), (-16, 26), (-20, 8)), ((12, 44), (24, 28), (28, 8)),
             ((-14, 74), (-4, 58)), ((28, 74), (30, 57), -95), -6, 7),
    "walk2": (3, 1, ((-6, 44), (2, 30), (-4, 16)), ((12, 44), (14, 26), (10, 8)),
              ((-18, 74), (-12, 56)), ((32, 74), (38, 58), -70), -9, 4),
    "walk3": (4, 2, ((-6, 44), (8, 28), (16, 8)), ((12, 44), (4, 26), (-6, 8)),
              ((-24, 76), (-24, 58)), ((34, 76), (46, 66), -30), -4, 6),
    "walk4": (3, -1, ((-6, 44), (-6, 26), (-8, 8)), ((12, 44), (22, 32), (14, 16)),
              ((-20, 74), (-16, 56)), ((32, 74), (38, 58), -70), 2, 4),
    "windup": (-2, 0, ((-6, 44), (-14, 26), (-18, 8)), ((12, 44), (26, 30), (32, 8)),
               ((-24, 84), (-30, 68)), ((38, 84), (34, 102), 95), 0, 5),
    "attack": (6, 0, ((-6, 44), (-14, 26), (-18, 8)), ((12, 44), (26, 30), (32, 8)),
               ((-22, 80), (-26, 62)), ((36, 112), (40, 134), 80), 0, 5),
}


def vodnik(pose):
    base, v = view_of(pose)
    if v:
        return vod_fb(base, v == "b")
    pose = base
    lean, rock, fl, nl, (fe, fh), (el, hd, ha), ts, dl = VOD[pose]
    shadow(2, 44)
    flat(ell(4, 1, 46, 3.2, 30), "#7fb3c9", 0.3)
    tx = -48 + lean * -1.5 + ts
    tails = [(-6 + lean, 78)] + bez((-6 + lean, 78), (-30, 66), (-40 + ts * 0.5, 40), (tx, 18)) + \
        ragged((tx, 18), (-30 + ts * 0.6, 22), 2, 5, 0.3) + ragged((-30 + ts * 0.6, 22), (-18 + ts * 0.3, 28), 2, 4, 1.4) + \
        bez((-18 + ts * 0.3, 28), (-16, 44), (-10, 58), (6, 62))
    form(tails, COAT_GREEN, sdx=-3, sdy=1, sh=0.2)
    hatch(tails, 2.0, 70, 0.45, g=COAT_GREEN_DK, alpha=0.6)
    stroke(bez((-14, 70), (-24, 56), (-30 + ts * 0.3, 40), (-34 + ts * 0.6, 22)), LINE * 0.6, g=COAT_GREEN_DK)
    drips([(tx + 1, 16), (-36 + ts * 0.6, 18), (-24 + ts * 0.3, 22)], WATER, dl)
    for leg, c_ in ((fl, FROG_DK), (nl, FROG)):
        tube([leg[0], leg[1]], 13, 10, OCHRE if c_ is FROG else col("#8a6c38"))
        tube([leg[1], leg[2]], 7, 5.5, c_)
        cuff = ell(leg[1][0], leg[1][1] - 1, 6.2, 2.6, 14, rot=-10)
        shape(cuff, OCHRE if c_ is FROG else col("#8a6c38"), LINE * 0.7)
        frog_foot((leg[2][0], leg[2][1] - 2), c_)
    fsh = (-8 + lean, 92); fe = (fe[0] + lean, fe[1]); fh = (fh[0] + lean, fh[1])
    tube([fsh, fe], 10, 8, COAT_GREEN_DK); tube([fe, fh], 8, 6.5, COAT_GREEN_DK)
    shape(ell(fh[0], fh[1] - 2, 3.5, 4, 12), FROG_DK, LINE * 0.8)
    teacup(fh[0], fh[1] - 4, 1.1)
    with T(lean, 0, 1, rot=rock):
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
        mo = {"attack": 5, "windup": 2}.get(pose, 0)
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
    sh0 = (20 + lean, 94); el = (el[0] + lean, el[1]); hd = (hd[0] + lean, hd[1])
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
    elif pose == "windup":
        ox, oy = hd[0] + 1, hd[1] + 10
        glow(ox, oy, 9, "#7fd0ff", 0.35)
        form(ell(ox, oy, 4.5, 4, 20), WATER, sh=0.15)
        stroke(ell(ox, oy, 3, 2.6, 14, 40, 290), LINE * 0.5, g=WATER_LT)
    else:
        drips([(hd[0] + 2, hd[1] - 9)], WATER, 6)


def frog_foot_fb(a, sc, colr, back=False):
    with T(a[0], a[1], sc * 1.4):
        toes = [(-6, -2.5), (0, -4), (6, -2.5)]
        web = [(-3, 2.5), toes[0], (-2, -1), toes[1], (2, -1), toes[2], (3, 2.5)]
        shape(web, colr, LINE * 0.75)
        if not back:
            for t in toes: shape(ell(t[0], t[1], 1.3, 1.1, 8), FROG_DK, LINE * 0.5)


VOD_LEGS = {
    "stand": (((-17, 26), (-18, 8), 1.0), ((17, 26), (18, 8), 1.0)),
    "c1": (((-16, 28), (-16, 12), 0.9), ((18, 25), (19, 5), 1.1)),
    "p1": (((-15, 32), (-14, 20), 1.0), ((17, 26), (18, 8), 1.0)),
    "c2": (((-18, 25), (-19, 5), 1.1), ((16, 28), (16, 12), 0.9)),
    "p2": (((-17, 26), (-18, 8), 1.0), ((15, 32), (14, 20), 1.0)),
    "brace": (((-22, 26), (-26, 8), 1.0), ((22, 26), (26, 8), 1.0)),
    "lunge": (((-20, 27), (-24, 10), 0.95), ((20, 24), (22, 4), 1.12)),
}
# legs, rock, cup arm (elbow, hand), free arm (elbow, hand, finger angle), tail sway, drip length
VOD_FB = {
    "idle": ("stand", 0, ((-36, 74), (-38, 56)), ((36, 74), (38, 56), -90), 0, 5),
    "walk": ("c1", -2.5, ((-36, 76), (-37, 60)), ((36, 72), (39, 54), -90), -4, 7),
    "walk2": ("p1", -1, ((-36, 74), (-38, 56)), ((36, 74), (38, 56), -90), -2, 4),
    "walk3": ("c2", 2.5, ((-36, 72), (-39, 54)), ((36, 76), (37, 60), -90), 4, 6),
    "walk4": ("p2", 1, ((-36, 74), (-38, 56)), ((36, 74), (38, 56), -90), 2, 4),
    "windup": ("brace", 0, ((-40, 80), (-44, 66)), ((44, 104), (40, 124), 90), 0, 5),
    "attack": ("lunge", 0, ((-40, 80), (-44, 66)), ((30, 104), (18, 112), 60), 0, 5),
}


def vod_fb(pose, back):
    legs, rock, (fe, fh), (el, hd, ha), ts, dl = VOD_FB[pose]
    att = pose == "attack"
    shadow(0, 44)
    flat(ell(0, 1, 46, 3.2, 30), "#7fb3c9", 0.3)

    def tails():
        for sx in (-1, 1):
            t = [(sx * 18, 62)] + bez((sx * 18, 62), (sx * 34, 56), (sx * 40, 40), (sx * 44 + ts, 18)) + \
                ragged((sx * 44 + ts, 18), (sx * 26 + ts * 0.6, 20), 2, 5, 0.3 + sx) + \
                bez((sx * 26 + ts * 0.6, 20), (sx * 22, 36), (sx * 18, 48), (sx * 8, 56))
            if sx > 0: t = t[::-1]
            form(t, COAT_GREEN_DK if not back else COAT_GREEN, sdx=0, sdy=1, sh=0.2)
            hatch(t, 2.0, 80, 0.45, g=COAT_GREEN_DK, alpha=0.6)
            drips([(sx * 43 + ts, 16), (sx * 32 + ts * 0.6, 18)], WATER, dl)

    def arm_cup():
        sh0 = (-26, 94)
        tube([sh0, fe], 11, 9, COAT_GREEN); tube([fe, fh], 9, 7.5, COAT_GREEN)
        shape(ell(fh[0], fh[1] - 2, 3.8, 4, 12), FROG, LINE * 0.8)
        teacup(fh[0], fh[1] - 4, 1.2)

    def arm_free():
        sh0 = (26, 94)
        tube([sh0, el], 11, 9, COAT_GREEN); tube([el, hd], 9, 7.5, COAT_GREEN)
        k = 1.25 if att and not back else 1.0
        if att and not back:
            glow(hd[0], hd[1], 22, "#7fd0ff", 0.4)
        with T(hd[0], hd[1], k):
            shape(ell(0, 0, 4.8, 4.5, 14), FROG, LINE * 0.8)
            for i in range(4):
                f = pt((0, 0), ha - 30 + i * 20, 8)
                tube([(0, 0), f], 2.2, 1.6, FROG, LINE * 0.6, sh=0)
                shape(ell(f[0], f[1], 1.3, 1.3, 8), FROG_DK, LINE * 0.5)
        if att and not back:
            ox, oy = hd[0] - 4, hd[1] + 2
            orb = ell(ox, oy, 12, 11, 30)
            form(orb, WATER, sh=0.15)
            for kk in range(3):
                stroke(ell(ox, oy, 12 - kk * 3.4, 11 - kk * 3, 20, 30 + kk * 40, 250 + kk * 40), LINE * 0.6, g=WATER_LT)
            drips([(ox - 7, oy - 9), (ox + 6, oy - 10)], WATER, 5)
        elif pose == "windup":
            ox, oy = hd[0], hd[1] + 11
            glow(ox, oy, 10, "#7fd0ff", 0.35)
            form(ell(ox, oy, 5, 4.5, 20), WATER, sh=0.15)
            stroke(ell(ox, oy, 3.2, 2.8, 14, 40, 290), LINE * 0.5, g=WATER_LT)
        else:
            drips([(hd[0], hd[1] - 9)], WATER, dl + 1)

    with T(0, 0, 1, flip=back):
        if not back:
            tails()
        else:
            arm_cup(); arm_free()
        for side, ((kx, ky), (ax, ay), sc) in zip((-1, 1), VOD_LEGS[legs]):
            hip = (side * 12, 46)
            tube([hip, (kx, ky)], 14, 11, OCHRE)
            tube([(kx, ky), (ax, ay)], 7.5 * sc, 6 * sc, FROG)
            shape(ell(kx, ky - 1, 6.6, 2.6, 14), OCHRE, LINE * 0.7)
            frog_foot_fb((ax, ay - 1), sc, FROG, back)
        with T(0, 0, 1, rot=rock):
            if back:
                coat = [(-28, 100)] + bez((-28, 100), (-34, 80), (-34, 60), (-42 + ts, 20)) + \
                    ragged((-42 + ts, 20), (-3 + ts, 24), 3, 5, 0.6) + [(0 + ts * 0.5, 50), (3 + ts, 24)] + \
                    ragged((3 + ts, 24), (42 + ts, 20), 3, 5, 1.7) + bez((42 + ts, 20), (34, 60), (34, 80), (28, 100))
                form(coat, COAT_GREEN, sdx=0, sdy=1, sh=0.2)
                hatch(coat, 2.0, 75, 0.45, g=COAT_GREEN_DK, alpha=0.6)
                for sx in (-1, 1):
                    stroke(bez((sx * 14, 96), (sx * 18, 70), (sx * 22, 46), (sx * 28 + ts, 22)), LINE * 0.6, g=COAT_GREEN_DK)
                    shape(ell(sx * 8, 52, 1.6, 1.6, 10), GOLD, LINE * 0.6)
                stroke([(-30, 50), (30, 50)], LINE * 0.6, g=COAT_GREEN_DK)
                drips([(-40 + ts, 18), (-20 + ts, 20), (20 + ts, 20), (40 + ts, 18)], WATER, dl)
            else:
                belly = ell(0, 68, 26, 29, 40)
                form(belly, VEST, sdx=0, sdy=2, sh=0.18)
                hatch(ell(-14, 58, 12, 20, 20), 2.0, 50, 0.45, g=col("#8a6a28"), alpha=0.6)
                for by in (88, 79, 70, 61):
                    shape(ell(0, by, 1.5, 1.5, 10), GOLD, LINE * 0.6)
                for sx in (-1, 1):
                    panel = [(sx * 14, 102), (sx * 30, 98), (sx * 36, 72), (sx * 32, 46), (sx * 22, 43),
                             (sx * 20, 70), (sx * 13, 92)]
                    form(panel[::sx], COAT_GREEN, sdx=0, sdy=1, sh=0.18)
                    shape([(sx * 6, 98), (sx * 15, 103), (sx * 22, 99), (sx * 12, 86)][::sx], COAT_GREEN_DK, LINE * 0.8)
                belt = bez((-30, 48), (-10, 42), (10, 42), (30, 48)) + bez((30, 48), (30, 44), (10, 38), (-30, 44))
                shape(belt + [(-30, 48)], WOOD_DK, LINE * 0.8)
                shape(rrect(-3, 39.5, 6, 5, 1), GOLD, LINE * 0.6)
                for i, (cx, ang) in enumerate(((-24, 8), (-12, -4), (12, 6), (24, -10))):
                    cy = 44 - (2 if i in (1, 2) else 0)
                    stroke([(cx, cy), (cx, cy - 6 - i % 2 * 3)], LINE * 0.6)
                    teacup(cx, cy - 6 - i % 2 * 3, 1.3, rot=ang + rock * 3)
                drips([(-28, 46), (28, 46)], WATER, 4)
            hx, hy = 0, 114
            for sx in (-1, 1):
                for (x0, y0) in ((16, 128), (20, 124), (24, 120)):
                    stroke(bez((sx * x0, y0), (sx * (x0 + 6), y0 - 14), (sx * (x0 + 4), y0 - 28), (sx * (x0 + 8), y0 - 40)), LINE * 1.6, g=MOSS)
            head = bez((hx - 27, hy), (hx - 27, hy + 14), (hx - 14, hy + 21), (hx, hy + 21)) + \
                bez((hx, hy + 21), (hx + 14, hy + 21), (hx + 27, hy + 14), (hx + 27, hy)) + \
                bez((hx + 27, hy), (hx + 26, hy - 12), (hx + 14, hy - 17), (hx, hy - 17)) + \
                bez((hx, hy - 17), (hx - 14, hy - 17), (hx - 26, hy - 12), (hx - 27, hy))
            if back:
                for sx in (-1, 1):
                    shape(ell(hx + sx * 12, hy + 20, 7, 6.5, 18), FROG, LINE * 0.9)
            form(head, FROG, sdx=0, sdy=1.5, sh=0.2)
            if back:
                for (x0, y0) in ((-6, 132), (0, 134), (6, 132), (-12, 128), (12, 128)):
                    stroke(bez((x0, y0), (x0 * 1.3 + 2, y0 - 16), (x0 * 1.1 - 2, y0 - 30), (x0 * 1.4, y0 - 52)), LINE * 1.6, g=MOSS)
                for (sx, sy, r_) in ((-8, 4, 2.2), (10, 0, 1.6), (2, 10, 1.4), (-14, -6, 1.2)):
                    shape(ell(hx + sx, hy + sy, r_, r_ * 0.8, 10), FROG_DK, 0)
            else:
                clip_fill(head, ell(hx, hy - 16, 22, 9, 24), FROG_BELLY)
                for (sx, sy, r_) in ((-16, 8, 2.2), (-20, 0, 1.6), (17, 6, 1.6), (14, 12, 1.2)):
                    shape(ell(hx + sx, hy + sy, r_, r_ * 0.8, 10), FROG_DK, 0)
                mo = {"attack": 5, "windup": 2}.get(pose, 0)
                mouth = bez((hx - 24, hy - 1), (hx - 10, hy - 7 - mo), (hx + 10, hy - 7 - mo), (hx + 24, hy - 1))
                if mo:
                    shape(mouth + bez((hx + 24, hy - 1), (hx + 10, hy - 5), (hx - 10, hy - 5), (hx - 24, hy - 1)), MOUTH_DK, LINE * 0.8)
                for i in range(9):
                    q = mouth[int((0.1 + i * 0.1) * (len(mouth) - 1))]
                    shape([(q[0] - 1.1, q[1] + 0.3), (q[0] + 1.1, q[1] + 0.3), (q[0], q[1] - 2.6)], BONE, LINE * 0.4)
                stroke(mouth, LINE)
                for sx in (-1, 1):
                    stroke([(hx + sx * 3, hy + 8), (hx + sx * 4, hy + 7.5)], LINE * 0.8)
                    ex, ey, r_ = hx + sx * 12, hy + 20, 6
                    shape(ell(ex, ey, r_ + 1.2, r_ + 1.2, 18), FROG, LINE * 0.9)
                    eye(ex, ey, r_ * 0.75, EYE_YELLOW, halo=2.0)
                    flat(ell(ex, ey, r_ * 0.6, r_ * 0.14, 12), "#2a1a12")
                    lid = ell(ex, ey, r_ + 1.3, r_ + 1.3, 14, 0, 180) + [(ex - r_ - 1.3, ey + r_ * 0.3), (ex + r_ + 1.3, ey + r_ * 0.3)]
                    shape(lid, FROG_DK, LINE * 0.9)
            brim = ell(hx, hy + 28, 22, 4.5, 30)
            crown = [(hx - 10, hy + 28), (hx - 9, hy + 47), (hx + 9, hy + 47), (hx + 10, hy + 28)]
            form(crown, HAT_RED, sdx=0, sdy=0, sh=0.2)
            shape([(hx - 9.8, hy + 31), (hx + 9.8, hy + 31), (hx + 9.6, hy + 35), (hx - 9.6, hy + 35)], COAT_GREEN_DK, LINE * 0.6)
            form(brim, HAT_RED, sdx=0, sdy=1, sh=0.2)
            shape(ell(hx, hy + 47, 9, 2.4, 20), RED_DK, LINE * 0.7)
            drips([(hx - 19, hy + 26), (hx + 20, hy + 26)], WATER, 4)
            if not back:
                pb = (hx + 26, hy - 14)
                tube([(hx + 16, hy - 4), (hx + 22, hy - 10), pb], 1.6, 1.6, WOOD_DK, LINE * 0.6, sh=0)
                shape(rrect(pb[0] - 2.5, pb[1] - 1, 5, 7, 1.5), WOOD, LINE * 0.7)
                glow(pb[0], pb[1] + 6, 3, EMBER, 0.6, 4)
                for i in range(3):
                    stroke(bez((pb[0], pb[1] + 7 + i * 6), (pb[0] + 4, pb[1] + 10 + i * 6), (pb[0] - 3, pb[1] + 12 + i * 6), (pb[0] + 1, pb[1] + 14 + i * 6)), LINE * 0.6, g=col("#c7c4bd"), alpha=0.7 - i * 0.2)
        if not back:
            arm_cup(); arm_free()


vodnik.poses = ALL


def vod_portrait():
    return portrait(vodnik, 20, 124, 2.4, "#2f4a46")


# ------------------------------------------------------------------ registry
SPRITES = boss_items("klekanice", klekanice, 320) + boss_items("kostnik", kostnik, 384) + boss_items("vodnik", vodnik, 352)
PORTRAITS = [("boss_klekanice", 256, 256, klek_portrait()), ("boss_kostnik", 256, 256, kost_portrait()),
             ("boss_vodnik", 256, 256, vod_portrait())]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
