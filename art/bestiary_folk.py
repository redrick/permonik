import math
from bestiary_kit import *

SOT = Col(0.5, "#867a54")
SOT_D = Col(0.4, "#675e42")
SOT_L = Col(0.65, "#a89c70")
SACK = Col(0.5, "#8c6d4a")
GOLD = Col(0.85, "#f0c64a")

STP = {
    "idle": dict(hip=(0, 13), lean=-14, ff=(-4, 1.5), nf=(4, 1.5), fh=(-2, 12.5), nh=(8, 2), head=-4, swipe=False),
    "walk": dict(hip=(0, 12.2), lean=-27, ff=(-6, 1.5), nf=(6, 3.0), fh=(8, 6), nh=(-3, 9), head=12, swipe=False),
    "walk2": dict(hip=(0, 13), lean=-24, ff=(1, 4.5), nf=(-0.5, 1.5), fh=(4, 8), nh=(3, 6), head=8, swipe=False),
    "walk3": dict(hip=(0, 12.2), lean=-28, ff=(6, 3.0), nf=(-6, 1.5), fh=(-2, 12.5), nh=(9, 6), head=12, swipe=False),
    "walk4": dict(hip=(0, 13), lean=-24, ff=(-0.5, 1.5), nf=(1, 4.5), fh=(2, 9.5), nh=(5, 5), head=8, swipe=False),
    "windup": dict(hip=(1, 12.4), lean=-6, ff=(-6, 1.5), nf=(5, 1.5), fh=(-2, 12.5), nh=(-5, 19), head=6, swipe=False),
    "attack": dict(hip=(-3, 17), lean=-38, ff=(-11, 5), nf=(1, 9), fh=(-2, 12.5), nh=(15, 13), head=26, swipe=True),
}


def sotek(pose):
    pose, v = view_of(pose)
    if v: return _sotek_fb(pose, v == "b")
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
    "idle": dict(x=0, lean=-3, ff=(-2.5, 1.2), nf=(2.5, 1.2), nh=(7, 8), fh=(-4, 3), ka=-20, cap=0, swipe=False),
    "walk": dict(x=0, lean=-9, ff=(-3, 1.2), nf=(3.5, 2.2), nh=(2, 6.5), fh=(2, 3.5), ka=-30, cap=1, swipe=False),
    "walk2": dict(x=0, lean=-7, ff=(0.5, 3.2), nf=(0, 1.2), nh=(5, 7), fh=(-1.5, 3), ka=-15, cap=4, swipe=False),
    "walk3": dict(x=0, lean=-10, ff=(3.5, 2.2), nf=(-3, 1.2), nh=(8, 9), fh=(-5, 4), ka=0, cap=2, swipe=False),
    "walk4": dict(x=0, lean=-7, ff=(0, 1.2), nf=(0.5, 3.2), nh=(6, 8), fh=(-3, 3.5), ka=-8, cap=-1, swipe=False),
    "windup": dict(x=1, lean=5, ff=(-3, 1.2), nf=(3, 1.2), nh=(-1, 15), fh=(-4, 3), ka=70, cap=-3, swipe=False),
    "attack": dict(x=-2, lean=-20, ff=(-6, 1.2), nf=(5, 1.2), nh=(13, 11), fh=(-4, 3), ka=-5, cap=10, swipe=True),
}


def permonicek(pose):
    pose, v = view_of(pose)
    with T(0, 0, 1.18):
        if v: _permonicek_fb(pose, v == "b")
        else: _permonicek(pose)


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
        limb((-1, 9.5), q["fh"], 4, 4, 2.4, 2.0, PM_SMOCK_D, -1)
        sm = bez((-3.5, 11), (-5, 6), (-6.5, 2), (-7, -1.5)) + [(-4, -2), (-1, -1.4), (2, -2), (5.5, -1.3)] + \
             bez((5.5, -1.3), (5, 3), (4.5, 7), (3.5, 11)) + bez((3.5, 11), (1, 12.2), (-1, 12.2), (-3.5, 11))
        form(sm, PM_SMOCK, sdx=-1.6, sdy=0.6, sh=0.14)
        shape(rrect(-6, 3.2, 11.5, 1.6, 0.6), LEATHER, LINE*0.6)
        with T(0.5, 15.5, 1, rot=-lean*0.5):
            _permonik_head(q["cap"])
        a, e, h = limb((1.5, 9.5), q["nh"], 4, 4, 2.6, 2.2, PM_SMOCK, -1)
        _knife(h, q["ka"])
        shape(ell(h[0], h[1], 1.3, 1.2, 10), PM_SKIN, LINE*0.6)
        if q["swipe"]:
            swoosh(bez((4, 2), (10, 1), (16, 5), (17, 11)), 1.3, WHITE, 0.45)


def _knife(h, ka, s=1.0):
    with T(h[0], h[1], s, rot=ka):
        tube([(-1.5, 0), (1.6, 0)], 1.6, 1.6, WOOD, lw=LINE*0.6, sh=0)
        bl = bez((1.6, -0.8), (4, -1.0), (6.5, -0.5), (8.2, 0.9)) + [(5.5, 0.6), (1.6, 0.8)]
        shape(bl, IRON, LINE*0.6)
        stroke([(2, 0.3), (6.5, 0.3)], LINE*0.3, g=WHITE)


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
    "walk": dict(hip=(-6, 39.5), lean=-26, ff=(-16, 2), nf=(12, 4), fh=(32, 6), nh=(10, -4), head=-6, mouth=0.3, bob=-1.5),
    "walk2": dict(hip=(-6, 41), lean=-24, ff=(-1, 9), nf=(-3, 2), fh=(22, 0), nh=(20, -2), head=-10, mouth=0.3, bob=2.5),
    "walk3": dict(hip=(-6, 39), lean=-28, ff=(12, 4), nf=(-16, 2), fh=(8, -4), nh=(34, 6), head=-4, mouth=0.3, bob=-1.5),
    "walk4": dict(hip=(-6, 41), lean=-24, ff=(-3, 2), nf=(-1, 9), fh=(18, -3), nh=(25, 1), head=-10, mouth=0.3, bob=2.5),
    "windup": dict(hip=(-5, 40), lean=-4, ff=(-14, 2), nf=(10, 2), fh=(-14, 58), nh=(-8, 70), head=16, mouth=0.7),
    "attack": dict(hip=(-8, 39), lean=-14, ff=(-22, 2), nf=(14, 2), fh=(14, 66), nh=(46, 52), head=26, mouth=1.0),
}


def _hej_arm(sh, hand, g, w, bend=-1, hs=1.0):
    a, e, h = ik(sh, hand, 23, 22, bend)
    o = shaggy(ribbon(chaikin([a, e, h]), w, w*0.75, w*1.15), 2.0, 3)
    form(o, g, sh=0.14)
    sb = shaggy(ell(a[0]-1, a[1]+1, w*0.75, w*0.7, 20), 1.6, 3, -1)
    form(sb, g, sh=0.1)
    fur_strokes(o, min(a[0], h[0])-8, max(a[0], h[0])+8, min(a[1], h[1])-8, max(a[1], h[1])+8, HEJ_D, 3.6, 2.6, 3)
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    with T(h[0], h[1], hs, rot=ang):
        shape(ell(2, 0, 4, 3.4, 16), HEJ_FACE, LINE*0.8)
        for i in range(4):
            yy = (i-1.5)*1.6
            tube([(4.5, yy), (7.5, yy*1.3), (9, yy*1.3-1.2)], 1.9, 1.4, HEJ_FACE, lw=LINE*0.6, sh=0)


def hejkal(pose):
    pose, v = view_of(pose)
    if v: return _hejkal_fb(pose, v == "b")
    q = HJP[pose]
    hip, lean = q["hip"], q["lean"]
    arm = _hej_arm

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
            _hejkal_head(q["mouth"], q.get("bob", 0))
        arm((6, 38), q["nh"], HEJ, 13)
    if pose == "attack":
        cx, cy = world(hip, lean, (16, 46))
        for a in (-20, 10, 40):
            aa = math.radians(a)
            stroke([(cx+18+math.cos(aa)*5, cy+4+math.sin(aa)*5), (cx+18+math.cos(aa)*12, cy+4+math.sin(aa)*12)], LINE*1.1, g=WHITE, alpha=0.7)


def _hejkal_head(m, bob=0):
    mane = shaggy(bez((-4, -14), (-14, -10), (-14, 8), (-6, 13)) + bez((-6, 13), (0, 16), (8, 14), (10, 7)) +
                  bez((10, 7), (12, 2), (11, -6), (6, -12)) + bez((6, -12), (2, -18), (-1, -18), (-4, -14)), 2.0, 3, -1)
    mane = [(x - bob*max(0, y)/16*0.6, y + bob*max(0, y)/16) for x, y in mane]
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
    "walk": dict(hip=(0, 37.3), lean=-9, ff=(-9, 1.8), nf=(9, 3), fh=(14, 8), nh=(-4, 6), head=-2, sway=4, stone=False),
    "walk2": dict(hip=(0, 38.5), lean=-7, ff=(1, 7), nf=(-1, 1.8), fh=(7, 4), nh=(5, 4), head=-3, sway=8, stone=False),
    "walk3": dict(hip=(0, 37), lean=-10, ff=(9, 3), nf=(-9, 1.8), fh=(-6, 6), nh=(14, 8), head=0, sway=4, stone=False),
    "walk4": dict(hip=(0, 38.5), lean=-7, ff=(-1, 1.8), nf=(1, 7), fh=(4, 4), nh=(9, 5), head=-3, sway=0, stone=False),
    "windup": dict(hip=(1, 37), lean=12, ff=(-10, 1.8), nf=(9, 1.8), fh=(18, 20), nh=(-16, 24), head=8, sway=9, stone="hold"),
    "attack": dict(hip=(-2, 37), lean=6, ff=(-12, 1.8), nf=(10, 1.8), fh=(26, 22), nh=(-14, 38), head=6, sway=-4, stone=True),
}


def diva_zena(pose):
    pose, v = view_of(pose)
    if v: return _diva_zena_fb(pose, v == "b")
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
    "walk": dict(hip=(-2, 36.3), lean=-14, ff=(-10, 1.8), nf=(10, 3), fh=(14, 9), nh=(5, 7), head=-4, tail=-2, ch=0),
    "walk2": dict(hip=(-2, 37.5), lean=-12, ff=(0, 7), nf=(-1, 1.8), fh=(7, 6), nh=(9, 8), head=-6, tail=-8, ch=1),
    "walk3": dict(hip=(-2, 36), lean=-16, ff=(10, 3), nf=(-10, 1.8), fh=(-4, 6), nh=(15, 10), head=-2, tail=4, ch=2),
    "walk4": dict(hip=(-2, 37.5), lean=-12, ff=(-1, 1.8), nf=(0, 7), fh=(4, 6), nh=(12, 9), head=-6, tail=10, ch=3),
    "windup": dict(hip=(-1, 37), lean=-2, ff=(-12, 1.8), nf=(8, 1.8), fh=(12, 14), nh=(-5, 38), head=8, tail=-14),
    "attack": dict(hip=(-8, 35), lean=-20, ff=(-20, 1.8), nf=(6, 1.8), fh=(-8, 24), nh=(24, 26), head=4, tail=-8),
}


def cert(pose):
    pose, v = view_of(pose)
    if v: return _cert_fb(pose, v == "b")
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
    elif pose.startswith("walk"):
        c = q["ch"]
        sw, ex = (0, -4, -1, 3)[c], (0, 2, 0, -2)[c]
        path = bez(hw, (hw[0]+1+sw, hw[1]-12), (hw[0]-8+sw, 4+(0, 2, 0, 2)[c]), (hw[0]-34+ex, 2.2))
        chain(path, 2.6)
        _hook((hw[0]-36+ex, 2.8), 190)
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


# ------------------------------------------------------------------ front (_f) and back (_b) views
# Per leg (-x, +x): lift and knee-out as fractions of leg length, foot scale, stance spread. The +x leg
# leads on walk (contact A); a foot coming toward the viewer is lower and bigger.
FBL = {
    "idle": ((0, 0, 1.0, 0), (0, 0, 1.0, 0)),
    "walk": ((0.05, 0, 0.93, 0), (-0.04, 0, 1.08, 0)),
    "walk2": ((0, 0, 1.0, 0), (0.2, 0.08, 1.04, 0)),
    "walk3": ((-0.04, 0, 1.08, 0), (0.05, 0, 0.93, 0)),
    "walk4": ((0.2, 0.08, 1.04, 0), (0, 0, 1.0, 0)),
    "windup": ((0, 0.04, 1.0, 0.1), (0, 0.04, 1.0, 0.1)),
    "attack": ((0.05, 0.04, 0.95, 0.08), (-0.05, 0.06, 1.1, 0.16)),
}
SWING = {"walk": -1, "walk3": 1}


def legs_fb(p, hx, hy, gx, L, leg):
    for i, (lift, kn, sc, sp) in sorted(enumerate(FBL[p]), key=lambda t: t[1][2]):
        s = 1 if i else -1
        leg(s, (s*hx, hy), (s*(gx + sp*L), lift*L), kn*L, sc)


def knee_of(s, h, a, kn, out=0.0):
    return ((h[0]+a[0])/2 + s*(kn+out), (h[1]+a[1])/2)


def swing_hand(s, p, hand, L):
    a = SWING.get(p, 0)*s
    if a > 0: return (hand[0] - s*0.05*L, hand[1] - 0.08*L), 1.1
    if a < 0: return (hand[0] + s*0.04*L, hand[1] + 0.06*L), 0.92
    return hand, 1.0


def foot_fb(x, y, w, g, sc=1.0, back=False, toes=3, claw=None):
    with T(x, y, sc):
        if back:
            shape(bez((-w*0.42, w*0.4), (-w*0.6, -w*0.25), (w*0.6, -w*0.25), (w*0.42, w*0.4)) + [(0, w*0.5)], g, LINE*0.8)
            stroke(bez((-w*0.3, w*0.05), (-w*0.1, -w*0.08), (w*0.1, -w*0.08), (w*0.3, w*0.05)), LINE*0.45)
            return
        shape(bez((-w*0.45, w*0.4), (-w*0.65, -w*0.3), (w*0.65, -w*0.3), (w*0.45, w*0.4)) + [(0, w*0.5)], g, LINE*0.8)
        for i in range(toes):
            tx = (i-(toes-1)/2)*w*0.26
            stroke([(tx, w*0.02), (tx*1.1, -w*0.16)], LINE*0.4)
            if claw is not None:
                stroke([(tx*1.1, -w*0.16), (tx*1.2, -w*0.42)], LINE*0.6, g=claw)


def _swoosh(pts, w=2.4, col=WHITE, a=0.5):
    P = resample(pts, 0.8); n = len(P)
    left, right = [], []
    for i in range(n):
        p, q = P[max(0, i-1)], P[min(n-1, i+1)]
        dx, dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx, dy) or 1
        ww = w*max(0.0, math.sin(math.pi*i/(n-1)))**0.7*(i/(n-1))**0.5
        left.append((P[i][0]-dy/L*ww, P[i][1]+dx/L*ww)); right.append((P[i][0]+dy/L*ww, P[i][1]-dx/L*ww))
    fill(left+list(reversed(right)), col, a)


def _fhand(a, e, h):
    return math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))


def _sotek_sack(x, y, s):
    with T(x, y, s):
        sk = bez((-5, -4), (-7.5, 1), (-5.5, 6), (0, 6.5)) + bez((0, 6.5), (5.5, 6), (7.5, 1), (5, -4)) + \
             bez((5, -4), (2, -6), (-2, -6), (-5, -4))
        form(sk, SACK, sh=0.18)
        for p in ((-1.6, 7.0), (1.2, 7.4)):
            glow(p[0], p[1], 2.2, GOLD, 0.2, 2); shape(ell(p[0], p[1], 1.1, 0.8, 10), GOLD, LINE*0.4)
        stroke(bez((-2.6, 6), (-1, 5.2), (1, 5.2), (2.6, 6)), LINE*0.9, g=LEATHER_D)


def _sotek_head_fb(back, open_):
    for s in (-1, 1):
        e = bez((s*3, 2.5), (s*6, 4.5), (s*10, 7.5), (s*13, 10)) + bez((s*13, 10), (s*10.5, 4), (s*7.5, 0.5), (s*3.8, -0.8))
        form(e, SOT_D if back else SOT, sh=0.14)
        if not back:
            fill(bez((s*4, 1.2), (s*7, 3.2), (s*10, 6), (s*11.6, 8.4)) + [(s*5, 0.2)], SOT_L)
    hd = bez((-4.8, 1), (-5.2, 5.8), (5.2, 5.8), (4.8, 1)) + bez((4.8, 1), (4.6, -3.5), (1.8, -6), (0, -6)) + \
         bez((0, -6), (-1.8, -6), (-4.6, -3.5), (-4.8, 1))
    form(hd, SOT, sdx=0, sh=0.15)
    if back:
        stroke(bez((-3, 4), (-1, 2), (1, 2), (3, 4)), LINE*0.45, g=SOT_D)
        stroke(bez((0, 4.6), (0.4, 1), (-0.3, -2), (0, -5)), LINE*0.45, g=SOT_D)
        return
    m = bez((-3.4, -3.0), (-1.6, -4.6 - open_*1.4), (1.6, -4.6 - open_*1.4), (3.4, -3.0)) + [(0, -3.4)]
    shape(m, MOUTH_D, LINE*0.6)
    for x in (-2, -0.7, 0.7, 2):
        fill([(x-0.4, -3.3), (x+0.4, -3.3), (x, -4.1)], TOOTH)
    for s in (-1, 1):
        eye(s*2.1, 1.2, 0.75, EYE_Y, 2.2)
        stroke([(s*0.7, 2.1), (s*3.6, 3.0)], LINE*0.8)
    shape(bez((-0.9, 1.0), (-1.4, -1.0), (-0.7, -2.6), (0, -2.9)) + bez((0, -2.9), (0.7, -2.6), (1.4, -1.0), (0.9, 1.0)), SOT, LINE*0.6)


def _sotek_fb(p, back):
    op = p in ("windup", "attack")
    with T(0, 0, 1, flip=back):
        if not back: _sotek_sack(-5.5, 21, 0.75)

        def leg(s, h, g, kn, sc):
            a = (g[0], g[1]+1.6)
            tube(chaikin([h, knee_of(s, h, a, kn, 0.6), a]), 3.0, 2.0, SOT_D if sc < 1 else SOT, lw=LINE*0.8, sh=0.1)
            foot_fb(a[0], g[1]+1.1, 4.4, SOT_D if sc < 1 else SOT, sc, back, 3, SOCKET)
        legs_fb(p, 2.4, 12.5, 3.0, 13, leg)

        arms = []
        for s in (-1, 1):
            hand, bend = (s*7.5, 13.5), s
            if op: hand = (s*8.5, 16)
            if p == "windup" and s > 0: hand, bend = (8.5, 33), -s
            if p == "attack" and s > 0: hand = (1.5, 15.5)
            hand, sc = swing_hand(s, p, hand, 13)
            arms.append((s, hand, bend, sc))

        def arm(s, hand, bend, sc):
            a, e, h = limb((s*5, 22.5), hand, 6.5, 6.5, 2.6, 2.0*sc, SOT, bend)
            shape(ell(h[0], h[1], 1.4*sc, 1.2*sc, 10), SOT, LINE*0.6)
            claws(h[0], h[1], _fhand(a, e, h), 3, 2.4*sc, 26, SOCKET, LINE*0.7)
        if back and p == "attack": arm(*arms[1])
        body = bez((-3.5, 10.5), (-6.5, 13), (-6.5, 20), (-4.5, 23.5)) + bez((-4.5, 23.5), (-2, 25.5), (2, 25.5), (4.5, 23.5)) + \
               bez((4.5, 23.5), (6.5, 20), (6.5, 13), (3.5, 10.5)) + bez((3.5, 10.5), (1, 9.8), (-1, 9.8), (-3.5, 10.5))
        form(body, SOT, sdx=0, sdy=1, sh=0.16)
        if back:
            stroke(bez((0, 24), (0.4, 20), (-0.4, 16), (0, 12)), LINE*0.5, g=SOT_D)
        else:
            clipped(body, lambda: fill(ell(0, 16, 3.6, 4.6, 16), SOT_L))
        loin = [(-5.8, 14), (5.8, 14), (5.4, 10.4), (3, 11.2), (1.5, 8.6), (0, 10.6), (-1.5, 8.8), (-3, 11.2), (-5.4, 10.4)]
        form(loin, RAG_D, sdx=0, sh=0.12)
        stroke(bez((-4, 23.5), (-1, 19), (2, 15.5), (5.5, 13.5)), LINE*0.9, g=LEATHER_D)
        if back: _sotek_sack(-1.5, 17.5, 1.0)
        with T(0, 29.5, 1):
            _sotek_head_fb(back, op)
        for a in arms:
            if not (back and p == "attack" and a[0] > 0): arm(*a)
        if p == "attack":
            _swoosh(bez((11, 32), (6, 26), (2, 18), (-6, 12)), 1.6, WHITE, 0.4)


def _permonik_head_fb(cap, back):
    if back:
        for s in (-1, 1):
            form([(s*2.6, -1), (s*4.4, -2.4), (s*3.8, -5.5), (s*2.2, -3.2)], PM_BEARD, sdx=0, sh=0.1)
    form(ell(0, 0, 3.8, 3.6, 22), PM_SKIN, sdx=0, sh=0.12)
    if back:
        hr = bez((-3.8, 1.6), (-4.1, -1.8), (-2.2, -3.6), (0, -3.6)) + bez((0, -3.6), (2.2, -3.6), (4.1, -1.8), (3.8, 1.6))
        form(hr, PM_BEARD, sdx=0, sh=0.1)
        for x in (-2, -0.7, 0.7, 2):
            stroke(bez((x, 1.4), (x*1.05, 0), (x*1.1, -1.4), (x, -3)), LINE*0.35, g=PM_SMOCK_D)
    else:
        br = bez((-3.2, -0.4), (-4.4, -4), (-2, -8.5), (0, -9.8)) + bez((0, -9.8), (2, -8.5), (4.4, -4), (3.2, -0.4)) + \
             [(1.6, -1.0), (0, -0.6), (-1.6, -1.0)]
        form(br, PM_BEARD, sdx=0, sh=0.1)
        for x in (-1.8, -0.6, 0.6, 1.8):
            stroke(bez((x, -2.5), (x*1.1, -4.5), (x*0.9, -6.5), (x*0.6, -8)), LINE*0.35, g=PM_SMOCK_D)
        m = bez((-1.6, -2.0), (-0.8, -3.2), (0.8, -3.2), (1.6, -2.0)) + [(0, -2.3)]
        shape(m, MOUTH_D, LINE*0.5)
        for x in (-0.7, 0, 0.7): fill([(x-0.3, -2.1), (x+0.3, -2.1), (x, -2.7)], TOOTH)
        for s in (-1, 1):
            stroke(bez((0, -0.8), (s*1.2, -1.8), (s*2.4, -1.6), (s*3.0, -0.7)), LINE*0.6, g=PM_SMOCK_D)
            dot(s*1.4, 1.1, 0.45, SOCKET); dot(s*1.4+0.15, 1.25, 0.18, WHITE)
            stroke(bez((s*0.5, 1.9), (s*1.2, 2.5), (s*2.0, 2.5), (s*2.7, 1.8)), LINE*0.6, g=PM_BEARD)
        shape(ell(0, -0.1, 1.2, 1.0, 12), Col(0.75, "#e0a088"), LINE*0.5)
    tx = cap*0.3
    ht = bez((-4.3, 1.4), (-4.4, 5), (-2.6 + tx*0.3, 8.5), (tx, 11 - abs(cap)*0.15)) + \
         bez((tx, 11 - abs(cap)*0.15), (2.6 + tx*0.3, 8.5), (4.4, 5), (4.3, 1.4)) + bez((4.3, 1.4), (1.5, 2.6), (-1.5, 2.6), (-4.3, 1.4))
    form(ht, PM_CAP, sdx=0, sh=0.15)
    stroke(bez((-4.3, 1.6), (-1.5, 2.8), (1.5, 2.8), (4.3, 1.6)), LINE*0.6)


def _permonicek_fb(p, back):
    cap = {"walk": 1, "walk2": 2, "walk3": -1, "walk4": -2, "attack": 2}.get(p, 0)
    with T(0, 0, 1, flip=back):
        def leg(s, h, g, kn, sc):
            a = (g[0], g[1]+2.6)
            tube([h, knee_of(s, h, a, kn), a], 2.6, 2.2, Col(0.5, "#7d6a58"), lw=LINE*0.7, sh=0)
            with T(a[0], g[1]+0.9, sc):
                b = [(-1.7, 2.0), (1.7, 2.0)] + bez((1.7, 2.0), (2.5, 1), (2.6, -0.3), (1.6, -0.8)) + \
                    bez((1.6, -0.8), (0.5, -1.1), (-0.5, -1.1), (-1.6, -0.8)) + bez((-1.6, -0.8), (-2.6, -0.3), (-2.5, 1), (-1.7, 2.0))
                shape(b, PM_BOOT, LINE*0.7)
        legs_fb(p, 1.8, 8.5, 2.2, 8, leg)

        arms = []
        for s in (-1, 1):
            hand, bend, ka = (s*5.4, 10.5), s, 70
            if p == "windup" and s > 0: hand, bend, ka = (5.5, 24.5), -s, 95
            if p == "attack" and s > 0: hand, ka = (1.5, 13), -100
            hand, sc = swing_hand(s, p, hand, 8)
            arms.append((s, hand, bend, sc, ka))

        def arm(s, hand, bend, sc, ka):
            a, e, h = limb((s*3.8, 18), hand, 4, 4, 2.6, 2.2*sc, PM_SMOCK if s > 0 else PM_SMOCK_D, bend)
            if s > 0: _knife(h, ka, 0.85 if p == "attack" else 1.0)
            shape(ell(h[0], h[1], 1.3*sc, 1.2*sc, 10), PM_SKIN, LINE*0.6)
        if back and p == "attack": arm(*arms[1])
        sm = bez((-4, 19), (-5, 14), (-6, 10), (-6.5, 6.5)) + [(-3, 6), (0, 6.6), (3, 6), (6.5, 6.5)] + \
             bez((6.5, 6.5), (6, 10), (5, 14), (4, 19)) + bez((4, 19), (1.5, 20.2), (-1.5, 20.2), (-4, 19))
        form(sm, PM_SMOCK, sdx=0, sdy=0.8, sh=0.14)
        stroke(bez((0, 19.5), (0.3, 16), (-0.3, 13), (0, 7)), LINE*0.4, g=PM_SMOCK_D)
        shape(rrect(-6, 10.8, 12, 1.6, 0.6), LEATHER, LINE*0.6)
        if not back: shape(rrect(-0.9, 10.6, 1.8, 2.0, 0.3), IRON, LINE*0.5)
        with T(0, 24, 1):
            _permonik_head_fb(cap, back)
        for a in arms:
            if not (back and p == "attack" and a[0] > 0): arm(*a)
        if p == "attack":
            _swoosh(bez((8, 23), (4, 18), (0, 13), (-5, 9)), 1.3, WHITE, 0.45)


def _hejkal_head_fb(m, back, bob):
    mane = shaggy(ell(0, 2, 14, 15, 40), 2.0, 3, -1)
    mane = [(x*(1 + bob*0.01*max(0, y)/15), y + bob*max(0, y)/15) for x, y in mane]
    form(mane, HEJ, sdx=0, sh=0.16)
    fur_strokes(mane, -15, 15, -14, 19, HEJ_D, 3.6, 2.6, 11)
    stroke([(2, 15 + bob), (4, 21 + bob), (7, 22 + bob)], LINE*0.8, g=LEATHER_D); stroke([(4, 21 + bob), (3.5, 24 + bob)], LINE*0.6, g=LEATHER_D)
    leaf(-5, 15 + bob, 120, 3, MOSS); leaf(9, 9, 30, 2.6, MOSS_D)
    if back:
        for p, a in (((-6, 2), 200), ((5, -6), -60)): leaf(p[0], p[1], a, 3, MOSS)
        return
    face = bez((0, 7), (-6, 7), (-8.5, 2), (-7.5, -3)) + bez((-7.5, -3), (-6, -8), (6, -8), (7.5, -3)) + bez((7.5, -3), (8.5, 2), (6, 7), (0, 7))
    form(face, HEJ_FACE, sdx=0, sh=0.12)
    for s in (-1, 1):
        fill(ell(s*3.4, 1.4, 2.6, 1.7, 14), SOCKET)
        eye(s*3.4, 1.3, 1.1, EYE_G, 2.4)
        stroke([(s*1.0, 3.2), (s*6.4, 4.4)], LINE*1.0)
    shape([(-1.2, 0.6), (0, -2.4), (1.2, 0.6)], HEJ_FACE, LINE*0.7)
    mo = ell(0, -4.6 - m, 2.0 + 1.2*m, 0.8 + 2.2*m, 18)
    shape(mo, MOUTH_D, LINE*0.7)
    if m > 0.5:
        for x in (-1.2, 1.2): fill([(x-0.4, -3.2), (x+0.4, -3.2), (x, -4.4)], TOOTH)
    beard = shaggy(bez((-6, -6), (-5, -12 - m*2), (5, -12 - m*2), (6, -6)) + [(3.5, -7.6 - m*1.5), (0, -6.8 - m*2.2), (-3.5, -7.6 - m*1.5)], 1.4, 3, -1)
    form(beard, HEJ, sdx=0, sh=0.1)
    fr = shaggy(bez((-9, 4), (-6, 10.5 + bob*0.5), (6, 10.5 + bob*0.5), (9, 4)) + [(5.5, 5.5), (2.5, 4.2), (0, 5.5), (-2.5, 4.2), (-5.5, 5.5)], 1.4, 3)
    form(fr, HEJ, sdx=0, sh=0.1)


def _hejkal_fb(p, back):
    mouth = {"windup": 0.7, "attack": 1.0}.get(p, 0.3)
    bob = {"walk": -1.5, "walk2": 2.5, "walk3": -1.5, "walk4": 2.5}.get(p, 0)
    with T(0, 0, 1, flip=back):
        def leg(s, h, g, kn, sc):
            a = (g[0], g[1]+4)
            o = shaggy(ribbon(chaikin([h, knee_of(s, h, a, kn, 1.0), a]), 14, 11*sc, 13), 2.0, 3)
            form(o, HEJ if sc >= 1 else HEJ_D, sdx=0, sh=0.14)
            fur_strokes(o, h[0]-10, h[0]+10, a[1]-2, h[1]+4, HEJ_D, 4.0, 3.0, 5)
            foot_fb(a[0], g[1]+2.6, 11, HEJ_FACE, sc, back, 4)
        arms = []
        for s in (-1, 1):
            hand, bend, hs = (s*24, 32), s, 1.0
            if p == "windup": hand, bend = (s*24, 108), -s
            if p == "attack": hand, hs = (s*21, 58), 1.3
            hand, sc = swing_hand(s, p, hand, 45)
            arms.append((s, hand, bend, hs*sc))

        def arm(s, hand, bend, hs):
            _hej_arm((s*17, 78), hand, HEJ if s > 0 else HEJ_D, 12.5, bend, hs)
        if back and p == "attack":
            for a in arms: arm(*a)
        legs_fb(p, 9, 40, 11, 39, leg)
        body = bez((-14, 32), (-22, 50), (-22, 76), (-12, 88)) + bez((-12, 88), (-5, 93), (5, 93), (12, 88)) + \
               bez((12, 88), (22, 76), (22, 50), (14, 32)) + bez((14, 32), (5, 28), (-5, 28), (-14, 32))
        body = shaggy(body, 2.6, 3, -1)
        form(body, HEJ, sdx=0, sdy=2, sh=0.18)
        fur_strokes(body, -23, 23, 26, 94, HEJ_D, 4.2, 3.4, 7)
        for pp, a in (((-10, 70), 30), ((11, 58), -40), ((-4, 44), 80), ((8, 80), 10), ((-14, 52), 150)):
            leaf(pp[0], pp[1], a, 3.4, MOSS)
        if not (back and p == "attack"):
            for a in arms: arm(*a)
        with T(0, 75 if p != "attack" else 72, 1.15):
            _hejkal_head_fb(mouth, back, bob)
        if not back and p == "attack":
            for s in (-1, 1):
                for a in (-20, 10, 40):
                    aa = math.radians(a)
                    stroke([(s*(18+math.cos(aa)*5), 76+math.sin(aa)*5), (s*(18+math.cos(aa)*12), 76+math.sin(aa)*12)], LINE*1.1, g=WHITE, alpha=0.7)


def _dz_hair_fb(sw, back):
    n = 9 if back else 7
    for i in range(n):
        t = i/(n-1) - 0.5
        x0, y0 = t*(10 if back else 12), 76
        ex, ey = t*(22 if back else 32) + sw*(0.6 + abs(t)), 28 + (i % 2)*4 + abs(t)*6
        lk = ribbon(bez((x0, y0), (x0*1.4, y0-14), (ex*0.9 + sw*0.3, (y0+ey)/2), (ex, ey)), 4.8 if back else 4.6, 0.8, 5.2 if back else 4.2)
        form(lk, DZ_HAIR if i % 2 else DZ_HAIR_D, sdx=0, sh=0.1)
    leaf(-6 + sw*0.4, 48, 60, 3, MOSS); leaf(5, 38, -20, 2.6, MOSS_D)


def _diva_zena_fb(p, back):
    sw = {"walk": 2, "walk2": 3, "walk3": -2, "walk4": -3, "windup": -2, "attack": 2}.get(p, 0)
    stone = {"windup": "hold", "attack": True}.get(p, False)
    with T(0, 0, 1, flip=back):
        if not back: _dz_hair_fb(sw, back)

        def leg(s, h, g, kn, sc):
            a = (g[0], g[1]+2.2)
            tube(chaikin([h, knee_of(s, h, a, kn, 0.5), a]), 5, 3.4, BARK_D if sc < 1 else BARK, sh=0.12)
            foot_fb(a[0], g[1]+1.4, 5.6, BARK_D if sc < 1 else BARK, sc, back, 4)
        legs_fb(p, 3.5, 40, 4.5, 36, leg)
        sk = [(-7, 46), (7, 46)] + [(8.5, 36), (7.5, 26), (5, 32), (3, 24), (1, 31), (-1, 25), (-3.5, 31), (-5.5, 24), (-7.5, 31), (-8.5, 37)]
        form(sk, DZ_RAG, sdx=0, sh=0.16)
        for pp, a in (((-4, 40), 200), ((3, 42), -30), ((6, 34), -60)):
            leaf(pp[0], pp[1], a, 3, MOSS)
        tor = bez((-5, 44), (-5.5, 52), (-6.5, 60), (-6.5, 65)) + bez((-6.5, 65), (-3, 67.5), (3, 67.5), (6.5, 65)) + \
              bez((6.5, 65), (6.5, 60), (5.5, 52), (5, 44)) + [(-5, 44)]
        form(tor, BARK, sdx=0, sdy=1, sh=0.16)
        for x in (-3, 0, 3):
            stroke(bez((x, 66), (x+1, 59), (x-1, 52), (x+0.5, 46)), LINE*0.45, g=BARK_D)
        arms = []
        for s in (-1, 1):
            hand, bend = (s*8.5, 42), s
            if p == "windup": hand = (9, 88) if s > 0 else (-11, 50)
            if p == "attack": hand = (4, 57) if s > 0 else (-11, 46)
            if p == "windup" and s > 0: bend = -s
            hand, sc = swing_hand(s, p, hand, 26)
            arms.append((s, hand, bend, sc))

        def arm(s, hand, bend, sc):
            a, e, h = limb((s*6, 64), hand, 13, 13, 4.0, 3.2*sc, BARK if s > 0 else BARK_D, bend)
            _twig_hand(h, e, BARK if s > 0 else BARK_D)
            if s > 0 and stone:
                r = 1.3 if stone is True else 1.0
                shape(notch(ell(h[0], h[1]+2.5, 3.8*r, 3.2*r, 18), 0.6, 3), ROCK, LINE*0.9)
                stroke([(h[0]-1, h[1]+3.5), (h[0]+1.5, h[1]+2)], LINE*0.5)
                if stone is True:
                    for i in range(3):
                        aa = math.radians(60 + i*40)
                        stroke([(h[0]+math.cos(aa)*7, h[1]+2.5+math.sin(aa)*7), (h[0]+math.cos(aa)*11, h[1]+2.5+math.sin(aa)*11)], LINE*0.6, g=WHITE, alpha=0.6)
        if back:
            if p == "attack": arm(*arms[1])
            _dz_hair_fb(sw, back)
        with T(0, 72, 1):
            if back:
                form(notch(ell(0, 1, 6.6, 8.6, 30), 1.0, 2), DZ_HAIR, sdx=0, sh=0.14)
                for x in (-3, 0, 3):
                    stroke(bez((x, 8.5), (x*1.2, 4), (x*1.3, -2), (x*1.5, -7)), LINE*0.4, g=DZ_HAIR_D)
            else:
                form(ell(0, 0, 5.6, 7.2, 30), BARK, sdx=0, sh=0.15)
                for s in (-1, 1):
                    fill(ell(s*2.4, 0.6, 1.8, 1.3, 12), SOCKET)
                    eye(s*2.4, 0.5, 0.9, EYE_G, 2.4)
                    stroke([(s*0.8, 2.4), (s*4.4, 2.0)], LINE*0.7)
                stroke(bez((0.3, 1), (0.6, -1), (0.2, -2), (-0.4, -2.2)), LINE*0.45, g=BARK_D)
                stroke(bez((-1.6, -4.4), (-0.5, -4.9), (0.5, -4.9), (1.6, -4.4)), LINE*0.6)
                top = notch(bez((-6.6, -1), (-8, 7), (-3, 10.5), (0, 10.5)) + bez((0, 10.5), (3, 10.5), (8, 7), (6.6, -1)), 1.4, 2) + \
                      [(5.2, 3), (3, 2.2), (1.5, 4.2), (0, 3), (-1.5, 4.2), (-3, 2.2), (-5.2, 3)]
                form(top, DZ_HAIR, sdx=0, sh=0.14)
            leaf(1, 10, 70, 3, MOSS); leaf(-4, 9, 130, 2.6, MOSS_D)
            stroke([(2, 10), (3.5, 13), (6, 13.5)], LINE*0.7, g=LEATHER_D)
        if not back:
            for s in (-1, 1):
                lk = shaggy(bez((s*5, 72), (s*7, 66), (s*7.5, 60), (s*7 + sw*0.4, 52)) + [(s*6 + sw*0.4, 51), (s*5.5, 60), (s*4.5, 66)], 1.0, 4)
                form(lk, DZ_HAIR, sdx=0, sh=0.1)
        for a in arms:
            if not (back and p == "attack" and a[0] > 0): arm(*a)


def _cert_head_fb(back):
    for s in (-1, 1):
        hn = bez((s*2.0, 5), (s*3.5, 10), (s*6.5, 13.5), (s*9, 17)) + bez((s*9, 17), (s*5.5, 14.5), (s*2.5, 12), (s*-0.8, 6.2))
        form(hn, HORN, sdx=0, sh=0.15)
        for k in range(3):
            stroke([(s*(1.6+k*1.2), 7+k*2.2), (s*(3.2+k*1.2), 6.6+k*2.2)], LINE*0.4)
        form([(s*5, 3), (s*11, 5.5), (s*5.5, -0.5)], CERT, sdx=0, sh=0.1)
    hd = notch(bez((-6, 1), (-6.5, 7.8), (6.5, 7.8), (6, 1)), 1.0, 2) + bez((6, 1), (5.5, -4), (3, -8), (0, -8.5)) + \
         bez((0, -8.5), (-3, -8), (-5.5, -4), (-6, 1))
    form(hd, CERT, sdx=0, sh=0.15)
    if back:
        for x in (-2.5, 0, 2.5):
            form(notch([(x-1.4, 6.5), (x+1.4, 6.5), (x*1.2, 1.5)], 0.6, 2), CERT_D, sdx=0, sh=0)
        stroke(bez((0, 1), (0.4, -2.5), (-0.3, -5), (0, -7.5)), LINE*0.45, g=CERT_D)
        return
    clipped(hd, lambda: fill(ell(0, -4.5, 3.9, 3.4, 16), CERT_L))
    for s in (-1, 1):
        dot(s*1.1, -3.0, 0.55, SOCKET)
        fill(ell(s*2.6, 1.3, 1.9, 1.4, 12), SOCKET)
        eye(s*2.8, 1.2, 0.95, EYE_Y, 2.4)
        stroke([(s*0.8, 2.5), (s*5, 3.7)], LINE*0.9)
    gt = notch(bez((-2.2, -7.5), (-2.6, -11), (-1, -13.5), (0, -14.5)) + bez((0, -14.5), (1, -13.5), (2.6, -11), (2.2, -7.5)), 0.8, 2)
    form(gt, CERT_D, sdx=0, sh=0)
    shape(bez((-3.2, -6.0), (-1.6, -7.6), (1.6, -7.6), (3.2, -6.0)) + [(0, -6.5)], MOUTH_D, LINE*0.6)
    for s in (-1, 1): fill([(s*2.2-0.4, -6.2), (s*2.2+0.4, -6.2), (s*2.2, -7.4)], TOOTH)
    tg = bez((-1.2, -7), (-1.8, -10), (-0.6, -13), (0.2, -16.5)) + bez((0.2, -16.5), (2.2, -16), (1.6, -12.5), (1.4, -9.5)) + \
         bez((1.4, -9.5), (1.3, -8), (1.1, -7.4), (0.6, -7))
    form(tg, RED, sdx=0, sh=0.12)
    stroke(bez((0.2, -7.8), (0.4, -10), (0.3, -12.5), (0.9, -15.5)), LINE*0.4)


def _cert_fb(p, back):
    tl = {"walk": -3, "walk2": 2, "walk3": 5, "walk4": 0, "windup": -4, "attack": 4}.get(p, 0)
    ch = {"walk": -2, "walk2": 1, "walk3": 3, "walk4": 1}.get(p, 0)
    with T(0, 0, 1, flip=back):
        def tail():
            if back: t = bez((0, 38), (3, 26), (-10 + tl*0.4, 24), (-17 + tl, 32))
            else: t = bez((-4, 40), (-14, 34), (-17 + tl*0.5, 46), (-21 + tl, 52))
            tube(t, 2.6, 1.6, CERT_D, sh=0)
            ex, ey = t[-1]
            form(notch(ell(ex - 1, ey + 1, 3.4, 2.4, 16, rot=30), 1.0, 2), CERT_D, sh=0.1)
        if not back: tail()

        def leg(s, h, g, kn, sc):
            a = (g[0], g[1]+4)
            o = ribbon(chaikin([h, knee_of(s, h, a, kn, 0.8), a]), 8, 5*sc, 8.5, 1.2, 2)
            form(o, CERT if sc >= 1 else CERT_D, sdx=0, sh=0.12)
            if s > 0:
                with T(a[0], g[1], sc):
                    form([(-2.8, 3.8), (2.8, 3.8), (3.5, 0), (-3.5, 0)], HOOF, sdx=0, sh=0)
                    if not back: stroke([(0, 0.3), (0, 2.8)], LINE*0.6, g=CERT_L)
            else:
                foot_fb(a[0], g[1]+1.5, 5.8, CERT_L, sc, back, 4)
        arms = []
        for s in (-1, 1):
            hand, bend = (s*12, 42), s
            if p == "windup": hand = (12, 84) if s > 0 else (-13, 50)
            if p == "attack": hand = (5, 50) if s > 0 else (-14, 48)
            if p == "windup" and s > 0: bend = -s
            hand, sc = swing_hand(s, p, hand, 26)
            arms.append((s, hand, bend, sc))

        def arm(s, hand, bend, sc):
            a, e, h = limb((s*9.5, 64), hand, 13.5, 13, 5.5, 4.4*sc, CERT if s > 0 else CERT_D, bend)
            _cert_hand(h, e, CERT if s > 0 else CERT_D)
            return h

        def held_chain(h):
            if p == "windup":
                path = bez(h, (h[0]-2, h[1]+14), (-14, 98), (-22, 86)); chain(path, 2.6); _hook(path[-1], -120)
            elif p == "attack":
                path = bez(h, (h[0]+12, h[1]+16), (h[0]+28, h[1]+6), (h[0]+24, h[1]-16)); chain(path, 2.8); _hook(path[-1], -100)
                _swoosh(bez((h[0]+6, h[1]+24), (h[0]+30, h[1]+20), (h[0]+34, h[1]-2), (h[0]+26, h[1]-22)), 2, WHITE, 0.35)
            elif p.startswith("walk"):
                path = bez(h, (h[0]+1+ch, h[1]-14), (h[0]+3+ch, 5), (h[0]+12+ch*1.5, 2.6)); chain(path, 2.6)
                _hook((h[0]+14+ch*1.5, 3.2), 10)
            else:
                path = bez(h, (h[0]+2, h[1]-14), (h[0]+6, 8), (h[0]+3, 3)); chain(path, 2.6); _hook((h[0]+3, 1.8), -20)
        if back and p == "attack":
            held_chain(arm(*arms[1]))
        legs_fb(p, 4, 38, 5, 33, leg)
        body = notch(bez((-8, 36), (-10.5, 46), (-11, 58), (-9, 66)) + bez((-9, 66), (-4, 70), (4, 70), (9, 66)), 1.2, 2) + \
               notch(bez((9, 66), (11, 58), (10.5, 46), (8, 36)), 1.0, 2) + bez((8, 36), (3, 34), (-3, 34), (-8, 36))
        form(body, CERT, sdx=0, sdy=1.4, sh=0.16)
        if back:
            stroke(bez((0, 68), (0.5, 58), (-0.5, 48), (0, 38)), LINE*0.5, g=CERT_D)
        else:
            clipped(body, lambda: fill(ell(0, 50, 5.5, 9, 18), CERT_L))
        chain(bez((-8, 64), (-3, 56), (3, 46), (8, 38)), 2.2)
        if back: tail()
        with T(0, 75, 1):
            _cert_head_fb(back)
        for a in arms:
            if back and p == "attack" and a[0] > 0: continue
            h = arm(*a)
            if a[0] > 0: held_chain(h)


for _fn in (sotek, permonicek, hejkal, diva_zena, cert):
    _fn.poses = ALL
