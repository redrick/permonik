"""Act III bosses: Strzyga, Mincíř Ohnivec, Ježibaba and her Chaloupka."""
import math
from bosses_kit import *

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
def strzyga(pose):
    lean = {"idle": 0, "walk": 5, "walk2": 5, "windup": -3, "attack": 9}[pose]
    sway = {"idle": 0, "walk": -6, "walk2": 6, "windup": 5, "attack": -4}[pose]
    shadow(0, 36)
    legs = {"idle": [((-6, 26), (-7, 12), (-9, 3)), ((8, 26), (10, 12), (12, 3))],
            "walk": [((-6, 26), (-14, 14), (-22, 3)), ((8, 26), (18, 14), (22, 3))],
            "walk2": [((-6, 26), (4, 14), (12, 3)), ((8, 26), (0, 14), (-10, 3))],
            "windup": [((-6, 26), (-14, 13), (-18, 3)), ((8, 26), (17, 13), (20, 3))],
            "attack": [((-6, 26), (-16, 12), (-24, 3)), ((8, 26), (20, 15), (26, 3))]}[pose]
    for hip, kn, ft in legs:
        tube([hip, kn], 5, 4, HAG_DK); tube([kn, ft], 4, 3.2, HAG_DK)
        shape(ell(ft[0] + 2, ft[1] - 0.5, 4.5, 2.2, 12), HAG_DK, LINE * 0.8)
        foot_claws((ft[0] + 5.5, ft[1] - 1), -12, 3, 4.5)
    sh0 = (4 + lean, 96)
    if pose == "attack":
        e1 = (20 + lean, 118); h1 = (40 + lean, 126); a1 = 15
    elif pose == "walk":
        e1 = (-12, 84); h1 = (-34, 76); a1 = 200
    elif pose == "walk2":
        e1 = (8, 78); h1 = (22, 64); a1 = -40
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
    elif pose == "walk":
        e0 = (26 + lean, 74); h0 = (42 + lean, 66); ca = -30
    elif pose == "walk2":
        e0 = (16 + lean, 74); h0 = (8 + lean, 58); ca = -110
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
    if pose == "attack":
        el, hd = (36, 124), (22, 142); hang = 175
    elif pose == "walk":
        el, hd = (36, 80), (42, 62); hang = -60
    elif pose == "walk2":
        el, hd = (30, 80), (24, 60); hang = -118
    elif pose == "windup":
        el, hd = (34, 120), (12, 134); hang = 215
    else:
        el, hd = (34, 78), (40, 58); hang = -86
    if pose in ("attack", "windup"):
        hammer(hd, hang, 40)
    tube([sp, el], 14, 11, FUR_DEVIL, sh=0.15); tube([el, hd], 11, 9, FUR_DEVIL, sh=0.15)
    if pose not in ("attack", "windup"):
        hammer(hd, hang, 40 if pose in ("walk", "walk2") else 50)
    shape(ell(hd[0], hd[1], 5.5, 5, 14), FUR_DEVIL_DK, LINE * 0.8)
    claws(pt(hd, hang + 90, 3), hang + 90, 3, 4, 1.2, 8, BONE_DK, curl=-60)
    if pose == "attack":
        motion([bez((-30, 160), (-16, 164), (0, 160), (12, 150)), bez((-36, 120), (-40, 130), (-38, 142), (-32, 152))])
        for (x, y) in ((48, 104), (54, 92), (44, 114), (60, 98)):
            dot(x, y, 0.8, col(EMBER)); glow(x, y, 2.5, FIRE, 0.5, 4)


def ohnivec(pose):
    shadow(0, 46)
    for (x, y, r, sq) in ((-44, 7, 2.6, 0.4), (40, 6, 2.4, 0.4), (54, 7, 2.2, 0.4), (-30, 6, 2.2, 0.4), (30, 9, 2.4, 0.4)):
        coin(x, y, r, sq)
    if pose == "walk":
        legs = [((-14, 42), (-26, 22), (-32, 6)), ((12, 40), (28, 24), (30, 7))]
    elif pose == "walk2":
        legs = [((-14, 42), (-4, 24), (2, 6)), ((12, 40), (6, 22), (-6, 7))]
    elif pose in ("attack", "windup"):
        legs = [((-14, 42), (-26, 22), (-30, 6)), ((12, 40), (24, 22), (26, 7))]
    else:
        legs = [((-14, 42), (-20, 22), (-20, 6)), ((12, 40), (20, 22), (18, 7))]
    tail = [(-34, 52), (-60, 44), (-70, 74), (-56, 96)]
    tl = bez(*tail)
    tube(tl, 5, 2.4, FUR_DEVIL, sh=0.1)
    tip = tl[-1]
    tuft = [(tip[0] - 2, tip[1] - 2), (tip[0] - 8, tip[1] + 4), (tip[0] - 3, tip[1] + 4), (tip[0] - 4, tip[1] + 11),
            (tip[0] + 1, tip[1] + 6), (tip[0] + 4, tip[1] + 12), (tip[0] + 5, tip[1] + 4), (tip[0] + 10, tip[1] + 5), (tip[0] + 3, tip[1] - 2)]
    form(tuft, FUR_DEVIL_DK, sh=0.1)
    for i, (hip, kn, ft) in enumerate(legs):
        g = FUR_DEVIL_DK if i == 0 else FUR_DEVIL
        tube([hip, kn], 16, 12, g, sh=0.15); tube([kn, ft], 12, 8, g, sh=0.15)
        if i == 0:
            fp = [(ft[0] - 6, ft[1] + 3), (ft[0] - 7, ft[1] - 5), (ft[0] + 9, ft[1] - 5), (ft[0] + 8, ft[1] + 1)]
            form(fp, SKIN_RED, sh=0.2)
            foot_claws((ft[0] + 8, ft[1] - 3), -15, 3, 4.5)
        else:
            hf = [(ft[0] - 6, ft[1] + 2), (ft[0] - 7, ft[1] - 6), (ft[0] + 8, ft[1] - 6), (ft[0] + 6, ft[1] + 2)]
            form(hf, HOOF, sh=0.2)
            stroke([(ft[0] + 1, ft[1] - 6), (ft[0] + 1.5, ft[1] - 1)], LINE * 0.8)
            fur = ragged((ft[0] - 8, ft[1] + 4), (ft[0] + 8, ft[1] + 4), 4, 3, 0.4)
            shape(fur + [(ft[0] + 6, ft[1] + 9), (ft[0] - 6, ft[1] + 9)], g, LINE * 0.7)
    sp = (-22, 102)
    if pose in ("attack", "windup"):
        el, hd = (-40, 86), (-50, 70)
    elif pose == "walk":
        el, hd = (-38, 82), (-30, 62)
    elif pose == "walk2":
        el, hd = (-38, 82), (-48, 64)
    else:
        el, hd = (-36, 80), (-40, 60)
    tube([sp, el], 13, 10, FUR_DEVIL_DK, sh=0.15); tube([el, hd], 10, 8, FUR_DEVIL_DK, sh=0.15)
    pouch = bez((hd[0] - 3, hd[1]), (hd[0] - 12, hd[1] - 4), (hd[0] - 12, hd[1] - 18), (hd[0], hd[1] - 20)) + \
        bez((hd[0], hd[1] - 20), (hd[0] + 12, hd[1] - 18), (hd[0] + 12, hd[1] - 4), (hd[0] + 3, hd[1]))
    form(pouch, LEATHER, sdx=-2, sdy=1, sh=0.22)
    stroke(bez((hd[0] - 4, hd[1] - 1), (hd[0] - 2, hd[1] - 3), (hd[0] + 2, hd[1] - 3), (hd[0] + 4, hd[1] - 1)), LINE * 1.2, g=LEATHER_DK)
    glow(hd[0] + 7, hd[1] - 12, 8, FIRE, 0.4)
    for (dx, dy) in ((9, -14), (11, -22), (8, -30), (12, -38)):
        if hd[1] + dy > 6: coin(hd[0] + dx, hd[1] + dy, 2.2, 0.55 + 0.1 * (dy % 3))
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
    lean = {"idle": 0, "walk": 4, "walk2": 4, "windup": -3, "attack": 7}[pose]
    cast_shadow(2, 0, 34, 2.6)
    if pose == "walk":
        sb, sa = (52, 4), 100
    elif pose == "walk2":
        sb, sa = (36, 4), 83
    elif pose == "idle":
        sb, sa = (44, 4), 94
    if pose not in ("attack", "windup"):
        shovel(sb, sa, 104)
    if pose == "walk":
        lf, ln_ = ((-8, 26), (-18, 4)), ((8, 26), (18, 4))
    elif pose == "walk2":
        lf, ln_ = ((-8, 26), (4, 4)), ((8, 26), (-4, 4))
    elif pose == "windup":
        lf, ln_ = ((-8, 26), (-16, 4)), ((8, 26), (14, 4))
    elif pose == "attack":
        lf, ln_ = ((-8, 26), (-20, 4)), ((8, 26), (20, 4))
    else:
        lf, ln_ = ((-8, 26), (-9, 4)), ((8, 26), (11, 4))
    tube(list(lf), 6, 5, SKIRT_DK)
    shoe = [(lf[1][0] - 5, lf[1][1] + 3), (lf[1][0] - 6, lf[1][1] - 3.5), (lf[1][0] + 9, lf[1][1] - 3.5), (lf[1][0] + 7, lf[1][1] + 2)]
    form(shoe, WOOD_DK, sh=0.2)
    for k in range(3): stroke([(lf[1][0] - 4 + k * 4, lf[1][1] + 2), (lf[1][0] - 2 + k * 4, lf[1][1] - 3)], LINE * 0.4)
    bone(ln_[0], (ln_[1][0], ln_[1][1] + 2), 3.2)
    kp = ((ln_[0][0] + ln_[1][0]) / 2, (ln_[0][1] + ln_[1][1]) / 2 + 2)
    shape(ell(kp[0], kp[1], 3, 2.6, 12), BONE, LINE * 0.7)
    foot = ln_[1]
    for k, a in enumerate((-8, 0, 8)):
        bone((foot[0] + 1, foot[1] - 0.5), (foot[0] + 8 + k, foot[1] - 2 + k * 0.6), 1.3)
    bone((foot[0] - 1, foot[1]), (foot[0] - 5, foot[1] - 2.2), 1.6)
    skirt = [(-20, 66), (18 + lean * 0.5, 66)] + bez((18 + lean * 0.5, 66), (24, 50), (30, 30), (32, 14)) + \
        ragged((32, 14), (-34, 14), 7, 3, 0.4)[1:-1] + [(-34, 14)] + bez((-34, 14), (-32, 32), (-26, 50), (-20, 66))
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
    elif pose in ("walk", "walk2"):
        sh0, el, hd = (8 + lean, 96), (20 + lean, 78), (44, 74)
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
    if pose == "attack":
        hip, jt, ft, tilt = (-6, 90), (-26, 62), (40, 58), 11
        spread = (10, 30, -10, 190)
    elif pose == "walk":
        hip, jt, ft, tilt = (0, 82), (-26, 50), (22, 9), -6
        spread = (0, 12, -8, 182)
    elif pose == "walk2":
        hip, jt, ft, tilt = (8, 90), (-8, 56), (-22, 10), 4
        spread = (-14, 2, -24, 168)
    elif pose == "windup":
        hip, jt, ft, tilt = (-4, 72), (-32, 42), (8, 9), -10
        spread = (4, 14, -6, 184)
    else:
        hip, jt, ft, tilt = (0, 88), (-18, 52), (6, 9), 0
        spread = (2, 12, -6, 182)
    shadow({"attack": -4, "walk2": 0}.get(pose, ft[0]), 46)
    if pose != "attack":
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
    chicken_foot(ft, spread, lift=pose in ("attack", "walk2"))
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


# ------------------------------------------------------------------ registry
SPRITES = boss_items("strzyga", strzyga, 320) + boss_items("ohnivec", ohnivec, 352) + \
    boss_items("jezibaba", jezibaba, 320, 1.12) + boss_items("chaloupka", chaloupka, 448)
PORTRAITS = [("boss_strzyga", 256, 256, portrait(strzyga, 26, 100, 3.0, "#3b4658")),
             ("boss_ohnivec", 256, 256, portrait(ohnivec, 26, 124, 1.9, "#5a3020")),
             ("boss_jezibaba", 256, 256, portrait(jezibaba, 36, 92, 2.6, "#4a3030"))]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
