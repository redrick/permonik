import math
from bestiary_kit import *

SOT = Col(0.5, "#867a54")
SOT_D = Col(0.4, "#675e42")
SOT_L = Col(0.65, "#a89c70")
SACK = Col(0.5, "#8c6d4a")
GOLD = Col(0.85, "#f0c64a")

STP = {
    "idle": dict(hip=(0, 13), lean=-14, ff=(-4, 1.5), nf=(4, 1.5), fh=(-2, 12.5), nh=(8, 2), head=-4, swipe=False),
    "walk": dict(hip=(0, 12.2), lean=-28, ff=(6, 3.2), nf=(-6, 1.5), fh=(-2, 12.5), nh=(9, 6), head=12, swipe=False),
    "walk2": dict(hip=(0, 12.5), lean=-25, ff=(-6, 1.5), nf=(6, 3.2), fh=(2, 9), nh=(3, 4), head=10, swipe=False),
    "windup": dict(hip=(1, 12.4), lean=-6, ff=(-6, 1.5), nf=(5, 1.5), fh=(-2, 12.5), nh=(-5, 19), head=6, swipe=False),
    "attack": dict(hip=(-3, 17), lean=-38, ff=(-11, 5), nf=(1, 9), fh=(-2, 12.5), nh=(15, 13), head=26, swipe=True),
}


def sotek(pose):
    q = STP[pose]
    hip, lean = q["hip"], q["lean"]

    def leg(j, f, g):
        a, k, w = ik(j, f, 6.5, 6.5, 1)
        tube(chaikin([a, k, w]), 3.0, 2.0, g, lw=LINE*0.8, sh=0.1)
        ft = bez((w[0]-1.2, w[1]+0.6), (w[0]-1.5, w[1]-1.4), (w[0]+3, w[1]-1.6), (w[0]+5.2, w[1]-0.6)) + [(w[0]+4.2, w[1]+0.2)]
        shape(ft, g, LINE*0.7)

    with T(hip[0], hip[1], 1, rot=lean):
        sk = bez((-3, 8), (-10, 10), (-12, 2), (-8, -1)) + bez((-8, -1), (-4, -2.5), (-1, 2), (-2, 6))
        form(sk, SACK, sh=0.18)
        stroke(bez((-3.5, 9), (-4.5, 11), (-3, 12), (-1.5, 12.5)), LINE*0.9, g=LEATHER_D)
        for p in ((-9.5, -1.2), (-7.5, -2.2)):
            glow(p[0], p[1], 2.2, GOLD, 0.2, 2); shape(ell(p[0], p[1], 1.1, 0.8, 10), GOLD, LINE*0.4)
        limb((-0.5, 10), q["fh"], 6.5, 6.5, 2.4, 1.9, SOT_D, -1)
    leg((hip[0]-0.8, hip[1]), q["ff"], SOT_D)
    with T(hip[0], hip[1], 1, rot=lean):
        body = bez((-3, -0.5), (-5, 4), (-4, 9), (-1, 11.5)) + bez((-1, 11.5), (2, 12.5), (4, 11), (4.5, 9)) + \
               bez((4.5, 9), (7.5, 6), (7, 1), (3, -1)) + [(-3, -0.5)]
        form(body, SOT, sh=0.16)
        clipped(body, lambda: fill(ell(4.5, 3.5, 3, 4, 16), SOT_L))
        loin = [(-4, 1.5), (5, 1.0), (4.5, -2.5), (2.5, -1), (1, -3), (-1, -1.2), (-3.5, -2.8)]
        form(loin, RAG_D, sh=0.12)
    leg((hip[0]+0.8, hip[1]), q["nf"], SOT)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(2.5, 15, 1, rot=q["head"]):
            _imp_head(pose in ("attack", "windup"))
        a, e, h = limb((1.5, 10), q["nh"], 6.5, 6.5, 2.6, 2.0, SOT, -1)
        ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
        shape(ell(h[0], h[1], 1.4, 1.2, 10), SOT, LINE*0.6)
        claws(h[0], h[1], ang, 3, 2.4, 26, SOCKET, LINE*0.7)
        if q["swipe"]:
            swoosh(bez((10, 22), (19, 22), (22, 12), (18, 4)), 1.6, WHITE, 0.4)


def _imp_head(open_):
    for s, g in ((-1, SOT_D), (1, SOT)):
        ex = -1.5 if s < 0 else 0.5
        e = bez((ex, 2.5), (ex-3, 5), (ex-8, 8.5), (ex-10.5, 10)) + bez((ex-10.5, 10), (ex-7, 5.5), (ex-4, 1.5), (ex-1.5, -0.5))
        form(e, g, sh=0.14)
        if s > 0: fill(bez((ex-1, 1.5), (ex-4, 4), (ex-7, 7), (ex-9, 8.6)) + [(ex-3.5, 1.2)], SOT_L)
    hd = bez((-3.5, -3.5), (-5.5, 2), (-2, 5.5), (1.5, 5)) + bez((1.5, 5), (4.5, 4.6), (5.5, 2.5), (5.5, 1)) + \
         bez((5.5, 1), (8.5, 0.5), (9.5, -2.5), (8, -3.5)) + bez((8, -3.5), (6.5, -1.5), (5.5, -2.6), (4.8, -4)) + \
         bez((4.8, -4), (3, -5.5), (-1, -5.5), (-3.5, -3.5))
    form(hd, SOT, sh=0.15)
    stroke([(1.5, 2.5), (4.5, 1.8)], LINE*0.8)
    eye(3.2, 1.1, 0.75, EYE_Y, 2.2)
    m = bez((0.5, -2.2), (2, -3.2 - (1.4 if open_ else 0)), (4.2, -3.6 - (1.4 if open_ else 0)), (5.4, -2.4)) + [(3, -2.0)]
    shape(m, MOUTH_D, LINE*0.6)
    for x in (2, 3.2, 4.3):
        fill([(x-0.4, -2.2), (x+0.4, -2.2), (x, -3.0)], TOOTH)


PM_SMOCK = Col(0.92, "#e6e0d2")
PM_SMOCK_D = Col(0.8, "#c5beae")
PM_CAP = Col(0.45, "#c43a2c")
PM_SKIN = Col(0.85, "#e9c4a4")
PM_BEARD = Col(0.95, "#f3f0ea")
PM_BOOT = Col(0.32, "#5a4234")

PMP = {
    "idle": dict(x=0, lean=-3, ff=(-2.5, 1.2), nf=(2.5, 1.2), nh=(7, 8), ka=-20, cap=0, swipe=False),
    "walk": dict(x=0, lean=-10, ff=(3.5, 2.2), nf=(-3, 1.2), nh=(8, 9), ka=0, cap=4, swipe=False),
    "walk2": dict(x=0, lean=-8, ff=(-3, 1.2), nf=(3.5, 2.2), nh=(5, 7), ka=-12, cap=2, swipe=False),
    "windup": dict(x=1, lean=5, ff=(-3, 1.2), nf=(3, 1.2), nh=(-1, 15), ka=70, cap=-3, swipe=False),
    "attack": dict(x=-2, lean=-20, ff=(-6, 1.2), nf=(5, 1.2), nh=(13, 11), ka=-5, cap=10, swipe=True),
}


def permonicek(pose):
    with T(0, 0, 1.18):
        _permonicek(pose)


def _permonicek(pose):
    q = PMP[pose]
    hip = (q["x"], 8.5)
    lean = q["lean"]
    for f, g in ((q["ff"], PM_BOOT), (q["nf"], PM_BOOT)):
        a, k, w = ik((hip[0]+(1 if f is q["nf"] else -1), hip[1]), (hip[0]+f[0], f[1]+1.0), 4, 3.8, 1)
        tube([a, k, w], 2.6, 2.2, Col(0.5, "#7d6a58"), lw=LINE*0.7, sh=0)
        b = bez((w[0]-1.4, w[1]+1.2), (w[0]-1.8, w[1]-1.2), (w[0]+2, w[1]-1.3), (w[0]+3.4, w[1]-0.9)) + [(w[0]+3, w[1]+0.4), (w[0]+1.2, w[1]+1.4)]
        shape(b, g, LINE*0.7)
    with T(hip[0], hip[1], 1, rot=lean):
        limb((-1, 9.5), (-4, 3), 4, 4, 2.4, 2.0, PM_SMOCK_D, -1)
        sm = bez((-3.5, 11), (-5, 6), (-6.5, 2), (-7, -1.5)) + [(-4, -2), (-1, -1.4), (2, -2), (5.5, -1.3)] + \
             bez((5.5, -1.3), (5, 3), (4.5, 7), (3.5, 11)) + bez((3.5, 11), (1, 12.2), (-1, 12.2), (-3.5, 11))
        form(sm, PM_SMOCK, sdx=-1.6, sdy=0.6, sh=0.14)
        shape(rrect(-6, 3.2, 11.5, 1.6, 0.6), LEATHER, LINE*0.6)
        with T(0.5, 15.5, 1, rot=-lean*0.5):
            _permonik_head(q["cap"])
        a, e, h = limb((1.5, 9.5), q["nh"], 4, 4, 2.6, 2.2, PM_SMOCK, -1)
        with T(h[0], h[1], 1, rot=q["ka"]):
            tube([(-1.5, 0), (1.6, 0)], 1.6, 1.6, WOOD, lw=LINE*0.6, sh=0)
            bl = bez((1.6, -0.8), (4, -1.0), (6.5, -0.5), (8.2, 0.9)) + [(5.5, 0.6), (1.6, 0.8)]
            shape(bl, IRON, LINE*0.6)
            stroke([(2, 0.3), (6.5, 0.3)], LINE*0.3, g=WHITE)
        shape(ell(h[0], h[1], 1.3, 1.2, 10), PM_SKIN, LINE*0.6)
        if q["swipe"]:
            swoosh(bez((4, 2), (10, 1), (16, 5), (17, 11)), 1.3, WHITE, 0.45)


def _permonik_head(cap):
    hd = ell(0, 0, 3.8, 3.6, 22)
    form(hd, PM_SKIN, sh=0.12)
    br = bez((-2.2, -0.5), (-3.6, -4), (-2, -8.5), (1.5, -9.5)) + bez((1.5, -9.5), (1.0, -7.5), (2.5, -6.5), (2.2, -5.5)) + \
         bez((2.2, -5.5), (4, -4), (4.6, -1.5), (3.8, -0.4)) + [(2.6, -1.4), (0.5, -0.8)]
    form(br, PM_BEARD, sh=0.1)
    for x in (-1, 0.6, 2):
        stroke(bez((x, -1.5), (x-0.3, -3.5), (x-0.2, -5.5), (x-0.6, -7)), LINE*0.35, g=PM_SMOCK_D)
    m = bez((0.8, -1.4), (1.8, -2.6), (3.2, -2.5), (4.0, -1.0)) + [(2.4, -1.5)]
    shape(m, MOUTH_D, LINE*0.5)
    for x in (1.8, 2.6, 3.3): fill([(x-0.3, -1.45), (x+0.3, -1.45), (x, -2.1)], TOOTH)
    shape(ell(3.8, 0.2, 1.2, 1.0, 12), Col(0.75, "#e0a088"), LINE*0.5)
    stroke(bez((0.5, 1.6), (1.3, 2.4), (2.4, 2.4), (3.3, 1.3)), LINE*0.7)
    dot(1.9, 1.15, 0.45, SOCKET); dot(2.05, 1.3, 0.18, WHITE)
    ht = bez((-4.3, 1.4), (-5.2, 4.5), (-6.5 - cap*0.2, 6.5), (-9.5 - cap*0.3, 6 - cap*0.3)) + \
         bez((-9.5 - cap*0.3, 6 - cap*0.3), (-7, 9.5), (-2, 10), (1, 8)) + bez((1, 8), (3, 6.5), (4.2, 4), (4.1, 1.6))
    form(ht, PM_CAP, sh=0.15)
    stroke(bez((-4.3, 1.6), (-1.5, 2.6), (1.5, 2.6), (4.1, 1.8)), LINE*0.6)


HEJ = Col(0.48, "#6f6b4a")
HEJ_D = Col(0.38, "#575438")
HEJ_FACE = Col(0.5, "#86705a")

HJP = {
    "idle": dict(hip=(-6, 40), lean=-20, ff=(-10, 2), nf=(9, 2), fh=(20, -6), nh=(26, -2), head=-8, mouth=0.3),
    "walk": dict(hip=(-6, 39), lean=-28, ff=(12, 4), nf=(-16, 2), fh=(8, -4), nh=(34, 6), head=-4, mouth=0.3),
    "walk2": dict(hip=(-6, 39.5), lean=-26, ff=(-16, 2), nf=(12, 4), fh=(32, 6), nh=(10, -4), head=-6, mouth=0.3),
    "windup": dict(hip=(-5, 40), lean=-4, ff=(-14, 2), nf=(10, 2), fh=(-14, 58), nh=(-8, 70), head=16, mouth=0.7),
    "attack": dict(hip=(-8, 39), lean=-14, ff=(-22, 2), nf=(14, 2), fh=(14, 66), nh=(46, 52), head=26, mouth=1.0),
}


def hejkal(pose):
    q = HJP[pose]
    hip, lean = q["hip"], q["lean"]

    def arm(sh, hand, g, w):
        a, e, h = ik(sh, hand, 23, 22, -1)
        o = shaggy(ribbon(chaikin([a, e, h]), w, w*0.75, w*1.15), 2.0, 3)
        form(o, g, sh=0.14)
        sb = shaggy(ell(a[0]-1, a[1]+1, w*0.75, w*0.7, 20), 1.6, 3, -1)
        form(sb, g, sh=0.1)
        fur_strokes(o, min(a[0], h[0])-8, max(a[0], h[0])+8, min(a[1], h[1])-8, max(a[1], h[1])+8, HEJ_D, 3.6, 2.6, 3)
        ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
        with T(h[0], h[1], 1, rot=ang):
            shape(ell(2, 0, 4, 3.4, 16), HEJ_FACE, LINE*0.8)
            for i in range(4):
                yy = (i-1.5)*1.6
                tube([(4.5, yy), (7.5, yy*1.3), (9, yy*1.3-1.2)], 1.9, 1.4, HEJ_FACE, lw=LINE*0.6, sh=0)

    def leg(j, f, g):
        a, k, w = ik(j, f, 20, 19, 1)
        o = shaggy(ribbon(chaikin([a, k, w]), 14, 10, 13), 2.0, 3)
        form(o, g, sh=0.14)
        ft = bez((w[0]-4, w[1]+2), (w[0]-5, w[1]-2), (w[0]+4, w[1]-2.2), (w[0]+9, w[1]-1.6)) + [(w[0]+8, w[1]+1), (w[0]+2, w[1]+2.5)]
        shape(ft, HEJ_FACE, LINE*0.8)
        for x in (4, 6, 8): stroke([(w[0]+x, w[1]-1.8), (w[0]+x+0.8, w[1]-0.4)], LINE*0.4)

    with T(hip[0], hip[1], 1, rot=lean):
        arm((0, 38), q["fh"], HEJ_D, 12)
    leg((hip[0]-3, hip[1]), q["ff"], HEJ_D)
    with T(hip[0], hip[1], 1, rot=lean):
        body = bez((-10, -12), (-17, 8), (-17, 34), (-8, 46)) + bez((-8, 46), (0, 54), (12, 52), (17, 42)) + \
               bez((17, 42), (21, 30), (19, 10), (13, -12)) + bez((13, -12), (4, -15), (-4, -15), (-10, -12))
        body = shaggy(body, 2.6, 3, -1)
        form(body, HEJ, sdx=-4, sdy=2, sh=0.18)
        fur_strokes(body, -18, 22, -16, 54, HEJ_D, 4.2, 3.4, 7)
        for p, a in (((-8, 34), 30), ((12, 22), -40), ((-4, 6), 80), ((8, 44), 10)):
            leaf(p[0], p[1], a, 3.4, MOSS)
    leg((hip[0]+3, hip[1]), q["nf"], HEJ)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(16, 46, 1.15, rot=q["head"]):
            _hejkal_head(q["mouth"])
        arm((6, 38), q["nh"], HEJ, 13)
    if pose == "attack":
        cx, cy = world(hip, lean, (16, 46))
        for a in (-20, 10, 40):
            aa = math.radians(a)
            stroke([(cx+18+math.cos(aa)*5, cy+4+math.sin(aa)*5), (cx+18+math.cos(aa)*12, cy+4+math.sin(aa)*12)], LINE*1.1, g=WHITE, alpha=0.7)


def _hejkal_head(m):
    mane = shaggy(bez((-4, -14), (-14, -10), (-14, 8), (-6, 13)) + bez((-6, 13), (0, 16), (8, 14), (10, 7)) +
                  bez((10, 7), (12, 2), (11, -6), (6, -12)) + bez((6, -12), (2, -18), (-1, -18), (-4, -14)), 2.0, 3, -1)
    form(mane, HEJ, sh=0.16)
    fur_strokes(mane, -14, 12, -18, 16, HEJ_D, 3.6, 2.6, 11)
    face = bez((1, 7), (-2, 4), (-1, -4), (3, -5)) + bez((3, -5), (6, -6), (10, -4), (10.5, 0)) + bez((10.5, 0), (11, 4), (8, 7.5), (1, 7))
    form(face, HEJ_FACE, sh=0.12)
    fill(ell(5, 2.4, 2.8, 1.8, 14), SOCKET)
    eye(5.6, 2.3, 1.2, EYE_G, 2.4)
    stroke([(2, 5), (8.5, 3.6)], LINE*1.0)
    shape([(9.5, 1.5), (12.5, -1.5), (9.5, -2)], HEJ_FACE, LINE*0.7)
    mo = ell(6.5, -3 - m, 1.8 + 1.0*m, 0.8 + 2.2*m, 18)
    shape(mo, MOUTH_D, LINE*0.7)
    if m > 0.5:
        fill([(5.4, -1.4), (6.2, -1.4), (5.8, -2.6)], TOOTH); fill([(7, -1.4), (7.8, -1.4), (7.4, -2.6)], TOOTH)
    beard = shaggy(bez((0, -4), (2, -8 - m*2), (6, -10 - m*2), (9.5, -6 - m*2)) + [(8, -5.5 - m*1.5), (4, -6 - m*1.8), (1.5, -3)], 1.4, 3, -1)
    form(beard, HEJ, sh=0.1)
    stroke([(-2, 13), (-5, 18), (-7, 18.5)], LINE*0.8, g=LEATHER_D); stroke([(-5, 18), (-4, 20.5)], LINE*0.6, g=LEATHER_D)
    leaf(4, 14, 40, 3, MOSS)


BARK = Col(0.5, "#86705a")
BARK_D = Col(0.4, "#6a5846")
DZ_HAIR = Col(0.5, "#7d7a6c")
DZ_HAIR_D = Col(0.38, "#5c5a50")
DZ_RAG = Col(0.42, "#5f6b3e")
ROCK = Col(0.55, "#8a8c8e")

DZP = {
    "idle": dict(hip=(0, 38), lean=-4, ff=(-6, 1.8), nf=(6, 1.8), fh=(4, 2), nh=(12, 6), head=-4, sway=0, stone=False),
    "walk": dict(hip=(0, 37), lean=-10, ff=(9, 3), nf=(-9, 1.8), fh=(-6, 6), nh=(14, 8), head=0, sway=6, stone=False),
    "walk2": dict(hip=(0, 37.3), lean=-9, ff=(-9, 1.8), nf=(9, 3), fh=(14, 8), nh=(-4, 6), head=-2, sway=2, stone=False),
    "windup": dict(hip=(1, 37), lean=12, ff=(-10, 1.8), nf=(9, 1.8), fh=(18, 20), nh=(-16, 24), head=8, sway=9, stone="hold"),
    "attack": dict(hip=(-2, 37), lean=6, ff=(-12, 1.8), nf=(10, 1.8), fh=(26, 22), nh=(-14, 38), head=6, sway=-4, stone=True),
}


def diva_zena(pose):
    q = DZP[pose]
    hip, lean, sw = q["hip"], q["lean"], q["sway"]
    with T(hip[0], hip[1], 1, rot=lean):
        for i in range(7):
            x0, y0 = 2 - i*1.6, 41 - i*1.2
            ex, ey = -9 - i*1.8 - sw*(0.6 + i*0.1), -8 + i*4.5
            lk = ribbon(bez((x0, y0), (x0-9, y0-6), (ex+4+(i % 2)*3, (y0+ey)/2), (ex, ey)), 4.6, 0.8, 4.2)
            form(lk, DZ_HAIR if i % 2 else DZ_HAIR_D, sh=0.1)
        leaf(-12 - sw*0.4, 18, 60, 3, MOSS); leaf(-8, 32, -20, 2.6, MOSS_D)
        a, e, h = limb((-1, 26), q["fh"], 13, 13, 3.8, 3.0, BARK_D, -1)
        _twig_hand(h, e, BARK_D)
    for f, k in ((q["ff"], -1), (q["nf"], 1)):
        g = BARK_D if k < 0 else BARK
        a, kn, w = ik((hip[0]+k*1.5, hip[1]), f, 18, 17, 1)
        tube(chaikin([a, kn, w]), 5, 3.4, g, sh=0.12)
        bare_foot(f, g, 5.5)
        if k < 0:
            with T(hip[0], hip[1], 1, rot=lean):
                _dz_torso()
    with T(hip[0], hip[1], 1, rot=lean):
        with T(2.5, 32, 1, rot=q["head"]):
            _dz_head()
        lock = shaggy(bez((-1, 36), (2, 30), (3, 24), (1.5 - sw*0.2, 14)) + [(0 - sw*0.2, 12), (-0.5, 20), (-2.5, 28), (-4, 34)], 1.0, 4)
        form(lock, DZ_HAIR, sh=0.1)
        a, e, h = limb((2, 26), q["nh"], 13, 13, 4.0, 3.2, BARK, -1)
        _twig_hand(h, e, BARK)
        if q["stone"]:
            shape(notch(ell(h[0], h[1]+2.5, 3.8, 3.2, 18), 0.6, 3), ROCK, LINE*0.9)
            stroke([(h[0]-1, h[1]+3.5), (h[0]+1.5, h[1]+2)], LINE*0.5)
            for i in range(3 if q["stone"] is True else 0):
                stroke([(h[0]+6+i*2, h[1]+6-i*3), (h[0]+10+i*2, h[1]+7-i*3)], LINE*0.6, g=WHITE, alpha=0.6)


def _twig_hand(h, e, g):
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    shape(ell(h[0], h[1], 1.8, 1.5, 12), g, LINE*0.6)
    for i in range(4):
        aa = math.radians(ang+(i-1.5)*20)
        p1 = (h[0]+math.cos(aa)*3.6, h[1]+math.sin(aa)*3.6)
        stroke([h, p1, (p1[0]+math.cos(aa-0.5)*1.4, p1[1]+math.sin(aa-0.5)*1.4)], LINE*0.8)


def _dz_torso():
    body = bez((-4.5, 0), (-6, 10), (-5.5, 20), (-4, 26)) + bez((-4, 26), (-1, 28.5), (3, 28.5), (5, 26)) + \
           bez((5, 26), (6, 20), (4.5, 16), (5.5, 10)) + bez((5.5, 10), (6, 5), (5, 1), (4.5, 0))
    form(body, BARK, sdx=-2, sdy=1, sh=0.16)
    for x in (-3, 0, 2.5):
        stroke(bez((x, 25), (x+1, 18), (x-1, 10), (x+0.5, 3)), LINE*0.45, g=BARK_D)
    sk = [(-6.5, 6), (7, 6)] + [(7.5, -4), (5.5, -12), (3.5, -6), (1, -14), (-1, -7), (-3.5, -13), (-5, -6), (-7.5, -11), (-7.5, -2)]
    form(sk, DZ_RAG, sh=0.16)
    for p, a in (((-4, 4), 200), ((2, 3), -30), ((5.5, -2), -60)):
        leaf(p[0], p[1], a, 3, MOSS)


def _dz_head():
    hd = bez((-2.5, -6.5), (-7, -5), (-6.5, 6), (0, 7.5)) + bez((0, 7.5), (5, 7.5), (6.5, 3), (6.4, 0)) + \
         bez((6.4, 0), (7.6, -2.2), (6.6, -3.6), (5.6, -4)) + bez((5.6, -4), (4.5, -6.8), (1, -7.6), (-2.5, -6.5))
    form(hd, BARK, sh=0.15)
    stroke(bez((-2, -4), (0, -2), (0.5, 1), (-1, 4)), LINE*0.4, g=BARK_D)
    fill(ell(3.4, 0.6, 2.0, 1.5, 12), SOCKET)
    eye(3.7, 0.5, 0.95, EYE_G, 2.4)
    stroke([(1.5, 2.8), (5.6, 1.8)], LINE*0.8)
    stroke(bez((3.5, -4.2), (4.5, -4.6), (5.2, -4.4), (5.8, -3.8)), LINE*0.6)
    top = notch(bez((-7, -3), (-9, 6), (-3, 10.5), (2, 9.5)) + bez((2, 9.5), (6, 9), (8, 6), (7, 2.5)), 1.4, 2) + \
          [(5, 4), (3, 2.5), (1, 5), (-2, 3), (-3.5, -2)]
    form(top, DZ_HAIR, sh=0.14)
    leaf(1, 9.5, 70, 3, MOSS); leaf(-4, 8, 130, 2.6, MOSS_D)
    stroke([(4, 9), (6, 12), (8, 12.5)], LINE*0.7, g=LEATHER_D)


CERT = Col(0.38, "#67545a")
CERT_D = Col(0.3, "#4c3d42")
CERT_L = Col(0.5, "#7e6866")
HORN = Col(0.8, "#cbb98f")
HOOF = Col(0.25, "#3e3436")

CTP = {
    "idle": dict(hip=(-2, 37), lean=-10, ff=(-7, 1.8), nf=(6, 1.8), fh=(6, 6), nh=(13, 8), head=-6, tail=0),
    "walk": dict(hip=(-2, 36), lean=-16, ff=(10, 3), nf=(-10, 1.8), fh=(-4, 6), nh=(15, 10), head=-2, tail=8),
    "walk2": dict(hip=(-2, 36.3), lean=-14, ff=(-10, 1.8), nf=(10, 3), fh=(14, 9), nh=(5, 7), head=-4, tail=-4),
    "windup": dict(hip=(-1, 37), lean=-2, ff=(-12, 1.8), nf=(8, 1.8), fh=(12, 14), nh=(-5, 38), head=8, tail=-14),
    "attack": dict(hip=(-8, 35), lean=-20, ff=(-20, 1.8), nf=(6, 1.8), fh=(-8, 24), nh=(24, 26), head=4, tail=-8),
}


def cert(pose):
    q = CTP[pose]
    hip, lean = q["hip"], q["lean"]
    tl = q["tail"]
    with T(hip[0], hip[1], 1, rot=lean):
        tail = bez((-6, 2), (-16, -2), (-14 + tl, 20), (-22 + tl, 22))
        tube(tail, 2.6, 1.6, CERT_D, sh=0)
        ex, ey = tail[-1]
        form(notch(ell(ex-2, ey+1, 3.4, 2.4, 16, rot=30), 1.0, 2), CERT_D, sh=0.1)
        a, e, h = limb((-1, 26), q["fh"], 13.5, 13, 5.5, 4.4, CERT_D, -1)
        _cert_hand(h, e, CERT_D)
    for f, k in ((q["ff"], -1), (q["nf"], 1)):
        g = CERT_D if k < 0 else CERT
        a, kn, w = ik((hip[0]+k*1.5, hip[1]), (f[0], f[1]+3), 17, 15, 1)
        o = ribbon(chaikin([a, kn, w]), 8, 5, 8.5, 1.2, 2)
        form(o, g, sh=0.12)
        if k > 0:
            hf = [(w[0]-2.8, w[1]+1), (w[0]+3, w[1]+1), (w[0]+3.6, w[1]-3.2), (w[0]-3.2, w[1]-3.2)]
            form(hf, HOOF, sh=0)
            stroke([(w[0]+1.4, w[1]-0.5), (w[0]+1.6, w[1]-3.0)], LINE*0.6, g=CERT_L)
        else:
            bare_foot((w[0], w[1]-1.2), CERT_L, 5.5)
    with T(hip[0], hip[1], 1, rot=lean):
        body = notch(bez((-6, -2), (-9, 10), (-9, 22), (-4, 28)) + bez((-4, 28), (0, 31), (6, 31), (9, 27)), 1.2, 2) + \
               notch(bez((9, 27), (11, 18), (10, 8), (7, -2)), 1.0, 2) + bez((7, -2), (2, -4), (-3, -4), (-6, -2))
        form(body, CERT, sdx=-3, sdy=1.4, sh=0.16)
        clipped(body, lambda: fill(ell(5, 14, 4.5, 9, 18), CERT_L))
        chain(bez((-8, 24), (-2, 18), (4, 12), (9, 4)), 2.2)
        with T(5, 36, 1, rot=q["head"]):
            _cert_head()
        a, e, h = limb((2, 26), q["nh"], 13.5, 13, 6, 4.8, CERT, -1)
        _cert_hand(h, e, CERT)
        hp_ = h
    hw = world(hip, lean, hp_)
    if pose == "attack":
        path = bez(hw, (hw[0]+10, hw[1]+16), (hw[0]+22, hw[1]+10), (hw[0]+26, hw[1]-4))
        chain(path, 2.6)
        _hook(path[-1], -70)
        swoosh(bez((hw[0]-2, hw[1]+16), (hw[0]+10, hw[1]+24), (hw[0]+22, hw[1]+18), (hw[0]+27, hw[1]+6)), 2, WHITE, 0.35)
    elif pose == "windup":
        path = bez(hw, (hw[0]-4, hw[1]+12), (hw[0]-18, hw[1]+12), (hw[0]-24, hw[1]+1))
        chain(path, 2.6)
        _hook(path[-1], -120)
    elif pose in ("walk", "walk2"):
        path = bez(hw, (hw[0]+1, hw[1]-12), (hw[0]-8, 4), (hw[0]-34, 2.2))
        chain(path, 2.6)
        _hook((hw[0]-36, 2.8), 190)
    else:
        path = bez(hw, (hw[0]+4, hw[1]-18), (hw[0]+14, hw[1]-22), (hw[0]+12, hw[1]-6))
        chain(path, 2.6)
        _hook((hw[0]+12, hw[1]-8), -90)


def _hook(p, ang):
    with T(p[0], p[1], 1, rot=ang):
        hk = bez((0, 0.8), (5, 1.2), (8, -2), (6, -5)) + [(5.2, -3.4)] + bez((5.2, -3.4), (6, -1), (4, -0.8), (0, -0.8))
        form(hk, IRON, sh=0.15)
        shape(ell(0, 0, 1.4, 1.4, 12), IRON_D, LINE*0.6)


def _cert_hand(h, e, g):
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    shape(ell(h[0], h[1], 2.6, 2.2, 14), g, LINE*0.7)
    claws(h[0]+math.cos(math.radians(ang))*2, h[1]+math.sin(math.radians(ang))*2, ang, 3, 2.6, 22, HORN, LINE*0.8)


def _cert_head():
    for hx, g, s in ((-3.5, Col(0.65, "#a8987a"), 0.85), (1.5, HORN, 1.0)):
        hn = bez((hx-1.6, 4), (hx-3.5, 9*s), (hx-1, 14*s), (hx+3, 15*s)) + bez((hx+3, 15*s), (hx+0.8, 12*s), (hx+0.2, 8*s), (hx+2, 4.5))
        form(hn, g, sh=0.15)
        for k in range(3):
            stroke([(hx-1.6+k*0.3, 6+k*2.6), (hx+0.6+k*0.3, 6.4+k*2.6)], LINE*0.4)
    hd = notch(bez((-2, -6.5), (-8, -4), (-7.5, 6), (0, 7.5)), 1.0, 2) + bez((0, 7.5), (4.5, 7.5), (6.5, 4), (6.6, 1)) + \
         bez((6.6, 1), (9.5, 0.6), (10, -2.4), (8.5, -3.6)) + bez((8.5, -3.6), (7, -5), (4, -7.5), (-2, -6.5))
    form(hd, CERT, sh=0.15)
    clipped(hd, lambda: fill(ell(6.5, -2.5, 4, 3.4, 16), CERT_L))
    dot(9.4, -1.0, 0.7, SOCKET)
    fill(ell(3.6, 1.6, 1.9, 1.4, 12), SOCKET)
    eye(3.9, 1.5, 0.95, EYE_Y, 2.4)
    stroke([(1.4, 3.6), (5.8, 2.4)], LINE*0.9)
    ear = [(-3, 3), (-8, 5.5), (-4.5, 0.5)]
    form(ear, CERT, sh=0.1)
    mo = bez((4, -4.6), (5.5, -6.2), (8, -6.4), (9, -4.6)) + [(6.5, -4.2)]
    shape(mo, MOUTH_D, LINE*0.6)
    tg = bez((6.0, -5.2), (7.5, -8), (6.5, -12), (8.5, -15)) + bez((8.5, -15), (10.5, -14.5), (9.4, -11.5), (9.2, -9)) + \
         bez((9.2, -9), (9, -7), (8.6, -5.6), (8, -5))
    form(tg, RED, sh=0.12)
    stroke(bez((7.6, -6.5), (8.2, -9), (8, -11.5), (8.8, -14)), LINE*0.4)
    fill([(4.8, -4.6), (5.6, -4.6), (5.2, -5.8)], TOOTH)
    gt = notch(bez((1, -5.5), (0, -9), (2, -11.5), (3.5, -12.5)) + [(4, -9), (5, -6)], 0.8, 2)
    form(gt, CERT_D, sh=0)
