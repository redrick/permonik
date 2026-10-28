import math
from bestiary_kit import *

WALKS = ("walk", "walk2", "walk3", "walk4")


def phase(base):
    return 90*WALKS.index(base) if base in WALKS else None


def step(ph, off=0):
    """-> (forward -1..1, lift 0..1) of a leg at gait phase ph: 0 contact ahead, 90 stance under, 180 behind, 270 swing"""
    if ph is None: return 0.0, 0.0
    r = math.radians(ph+off)
    return math.cos(r), max(0.0, -math.sin(r))


def mirrored(half):
    return half + [(-x, y) for x, y in reversed(half[1:-1])]


WOLF = Col(0.5, "#746c63")
WOLF_D = Col(0.4, "#5c5650")
WOLF_L = Col(0.7, "#a9a196")
DOG = Col(0.33, "#5a5462")
DOG_D = Col(0.27, "#4a4552")
DOG_L = Col(0.42, "#6e6878")

QP = {
    "idle": dict(tilt=0, hipy=29, hipx=-19, ff=(0, 0), fn=(4, 0), hf=(-3, 0), hn=(1, 0), lift=(0, 0, 0, 0), head=-4, jaw=0, tail=-30, crouch=0),
    "windup": dict(tilt=-7, hipy=26, hipx=-15, ff=(6, 0), fn=(9, 0), hf=(-6, 0), hn=(-2, 0), lift=(0, 0, 0, 0), head=-14, jaw=14, tail=-40, crouch=1),
    "attack": dict(tilt=14, hipy=24, hipx=-23, ff=(18, 10), fn=(22, 6), hf=(-12, 0), hn=(-8, 0), lift=(10, 6, 0, 0), head=8, jaw=34, tail=10, crouch=1),
}
for _i, _n in enumerate(WALKS):
    _ca, _la = step(90*_i); _cb, _lb = step(90*_i, 180); _c2 = math.cos(math.radians(180*_i))
    QP[_n] = dict(tilt=-1.5+0.8*_c2, hipy=28-0.8*_c2, hipx=-19, fl=(12.5, 13),
                  ff=(2+11.5*_cb+1.5*_lb, 0), fn=(4+11.5*_ca+1.5*_la, 0), hf=(-1.5+11.5*_ca+1.5*_la, 0), hn=(-0.5+11.5*_cb+1.5*_lb, 0),
                  lift=(4.5*_lb, 4.5*_la, 4.5*_la, 4.5*_lb), head=-7+2*_c2, jaw=0, tail=-24-6*_c2, crouch=0)


def canine(pose, fur, fur_d, fur_l, eyecol, big=1.0, hackles=0.0):
    q = QP[pose]
    hip = (q["hipx"], q["hipy"])
    tilt = q["tilt"]
    sh = world(hip, tilt, (25, -2))
    hp = world(hip, tilt, (1, -2))

    def front(j, foot, lift, g):
        target = (foot[0]+sh[0]-3, lift+2.5)
        a, e, w = ik(j, target, *q.get("fl", (12, 12.5)), -1 if lift < 5 else 1)
        tube(chaikin([a, e, w]), 7.5, 4.0, g, sh=0.12)
        paw(w, g, 1 if lift < 5 else 0.6)

    def hind(j, foot, lift, g):
        x = foot[0]+hp[0]
        hock = (x-1.5, lift+9)
        a, k, h = ik(j, hock, 12, 11.5, 1)
        tube(chaikin([a, k, h]), 10, 4.2, g, sh=0.12)
        tube([h, (x+1, lift+2.5)], 4.0, 3.6, g, sh=0.1)
        paw((x+1, lift+2.5), g, 1)

    def paw(p, g, k):
        shape(ell(p[0]+1.8, p[1]-1.0, 3.2*k, 1.9, 14), g, LINE*0.8)
        for dx in (0.6, 2.2):
            stroke([(p[0]+dx+1, p[1]-0.6), (p[0]+dx+1.2, p[1]-2.4)], LINE*0.45)

    with T(hip[0], hip[1], 1, rot=tilt):
        tl = q["tail"]
        sp = bez((-2, 0), (-8, 1+tl*0.05), (-13, -4+tl*0.2), (-15, -12+tl*0.45))
        form(ribbon(sp, 5.5, 2.0, 7, 0.7, 4), fur, sh=0.15)
        fill(ribbon(sp[-6:], 3, 0.5), fur_d)

    front(world(hip, tilt, (24, -1)), q["ff"], q["lift"][0], fur_d)
    hind(world(hip, tilt, (2, -1)), q["hf"], q["lift"][2], fur_d)

    with T(hip[0], hip[1], 1, rot=tilt):
        h = hackles
        back = notch(bez((-5, -1), (-4, 4), (8, 4.5+h*0.5), (16, 5+h)) + bez((16, 5+h), (22, 6+h*1.5), (27, 8+h), (32, 4)), 0.8+h*0.15, 4)
        chest = notch(bez((32, 4), (36, 0), (35, -8), (29, -12)), 1.1, 3)
        belly = bez((29, -12), (22, -14), (14, -9.5), (6, -9)) + bez((6, -9), (0, -11), (-6, -7), (-5, -1))
        body = back + chest + belly
        form(body, fur, sdx=-3, sdy=1.6, sh=0.16)
        clipped(body, lambda: fill(ell(25, -9, 9, 4.5, 20), fur_l))
        stroke(bez((22, -9), (19, -4), (21, 1), (25, 3)), LINE*0.6)
        stroke(bez((1, -8), (-1, -3), (2, 1), (6, 2)), LINE*0.6)
        for i in range(4):
            x = 8+i*4
            stroke([(x, -3+i*0.3), (x-1.5, -6+i*0.3)], LINE*0.4)

    hind(world(hip, tilt, (-1, -2)), q["hn"], q["lift"][3], fur)
    front(world(hip, tilt, (26, -2)), q["fn"], q["lift"][1], fur)

    with T(hip[0], hip[1], 1, rot=tilt):
        with T(36, 5, 1, rot=q["head"]):
            canine_head(q["jaw"], eyecol, fur, fur_d, fur_l, q["crouch"])


def canine_head(jaw, eyecol, fur, fur_d, fur_l, snarl=0):
    ruff = notch(ell(-2, -1, 6.5, 7.5, 24), 1.5, 2)
    form(ruff, fur, sh=0.12)
    hx, hy = 3, -2
    lo = bez((2, -2.5), (3, -5.5), (9, -5), (13, -3.6)) + [(12, -2.6), (2, -1.5)]
    lo = rot(lo, hx, hy, -jaw)
    if jaw:
        tip = rot([(13, -3.6)], hx, hy, -jaw)[0]
        mo = [(2.5, -1.5), (14.5, -1.4), tip, (3, -3)]
        shape(mo, MOUTH_D, LINE*0.6)
        fill(rot(ell(8, -3.6, 4, 1.0, 12), hx, hy, -jaw*0.7), TONGUE)
        for x in (6.5, 9, 11.5, 13.5):
            fill([(x-0.6, -1.5), (x+0.6, -1.5), (x, -3.2)], TOOTH)
        for x in (7, 10, 12.2):
            p = rot([(x-0.6, -3.2), (x+0.6, -3.2), (x, -1.6)], hx, hy, -jaw)
            fill(p, TOOTH)
    form(lo, fur_d, sh=0.1)
    up = bez((-5, 1), (-6, 6), (-1, 7.5), (3, 6)) + bez((3, 6), (6, 4.8), (10, 2.8), (14, 1.2)) + \
         bez((14, 1.2), (15.6, 0.6), (15.6, -1.4), (14.6, -1.6)) + [(5, -1.8), (0, -3), (-4, -2)]
    form(up, fur, sdx=-1.5, sdy=0.8, sh=0.14)
    clipped(up, lambda: fill(ell(9, -1.8, 6, 1.6, 16), fur_l))
    for ex in (-3.5, 0.5):
        e = [(ex-1.5, 5.5), (ex+0.3, 13.5), (ex+2.8, 5.2)]
        form(e, fur, sh=0.15)
        fill([(ex-0.3, 6.2), (ex+0.4, 11), (ex+1.6, 6)], fur_d)
    dot(14.6, -0.2, 1.3, SOCKET)
    stroke(bez((8, 2.6+snarl), (9.5, 2.2+snarl), (10.5, 1.5), (11.5, 1.5)), LINE*0.5)
    stroke([(1.5, 4.4), (5.6, 3.0)], LINE*0.9)
    eye(4.0, 2.4, 1.05, eyecol, 2.4)


def canine_face(jaw, eyecol, fur, fur_d, fur_l, snarl=0):
    for s in (-1, 1):
        e = [(s*2.2, 4.0), (s*6.6, 14.5), (s*8.0, 2.2)]
        form(e, fur, sh=0.15)
        fill([(s*3.4, 5.0), (s*6.3, 11.8), (s*7.0, 3.6)], fur_d)
    form(notch(ell(0, 0.5, 9.8, 6.4, 28), 1.3, 2), fur, sh=0.12)
    form(ell(0, 1.8, 7.4, 6.0, 26), fur, w=LINE*0.35, sdx=0, sdy=1.0, sh=0.14)
    jo = jaw*0.11
    if jaw:
        shape(ell(0, -7.6-jo*0.5, 3.6, 1.4+jo*0.55, 18), MOUTH_D, LINE*0.6)
        fill(ell(0, -8.4-jo*0.8, 2.0, 0.9+jo*0.25, 12), TONGUE)
        for s in (-1, 1):
            fill([(s*3.1, -6.6), (s*1.9, -6.6), (s*2.4, -8.8-jo*0.3)], TOOTH)
            fill([(s*2.9, -8.4-jo*1.0), (s*1.9, -8.4-jo*1.0), (s*2.4, -6.8-jo*0.7)], TOOTH)
        form(ell(0, -9.6-jo*1.05, 3.0, 1.5, 14), fur_d, sh=0)
    mz = bez((0, 0.8), (-2.6, 0.8), (-4.2, -2.0), (-3.6, -5.4)) + bez((-3.6, -5.4), (-3.2, -7.4), (-1.4, -8.0), (0, -8.0))
    mz = mirrored(mz + [(0, -8.0)])
    form(mz, fur, w=LINE*0.8, sdx=0, sdy=0.8, sh=0.1)
    clipped(mz, lambda: fill(ell(0, -4.6, 3.4, 3.8, 16), fur_l))
    shape(ell(0, -6.9, 1.6, 1.05, 14), SOCKET, LINE*0.5)
    dot(-0.4, -6.6, 0.35, WHITE)
    if not jaw:
        stroke(bez((-2.4, -8.0), (-1.2, -8.4), (1.2, -8.4), (2.4, -8.0)), LINE*0.5)
    for s in (-1, 1):
        stroke(bez((s*0.9, -2.0-snarl*0.3), (s*1.8, -2.6), (s*2.4, -2.2), (s*3.0, -2.8)), LINE*0.45)
        stroke([(s*1.2, 3.0-snarl*0.4), (s*5.6, 4.2)], LINE*0.9)
        eye(s*3.4, 1.6, 1.05, eyecol, 2.4)


def canine_nape(fur, fur_d):
    for s in (-1, 1):
        e = [(s*2.2, 4.0), (s*6.6, 14.5), (s*8.0, 2.2)]
        form(e, fur, sh=0.15)
        stroke([(s*3.6, 4.6), (s*6.3, 12)], LINE*0.5, g=fur_d)
    form(notch(ell(0, 1.2, 8.0, 6.6, 28), 1.1, 2), fur, sdx=0, sdy=1.0, sh=0.16)
    for i, x in enumerate((-3.5, -1, 1.5, 4)):
        stroke([(x, 3-i % 2), (x-0.4, -0.5-i % 2)], LINE*0.4)


QFB = {
    "idle": dict(by=0, hd=0, hs=1.0, jaw=0, spread=0, rear=0),
    "windup": dict(by=-3, hd=-7, hs=1.0, jaw=14, spread=2, rear=0),
    "attack": dict(by=-1, hd=-4, hs=1.14, jaw=34, spread=1, rear=1),
}


def quad_fb(base, view):
    ph = phase(base)
    if ph is None: return dict(QFB[base], ph=None, sway=0.0, c2=0.0)
    c2 = math.cos(math.radians(2*ph))
    return dict(by=0.5*c2-0.5, hd=-0.8+0.8*c2, hs=1.0, jaw=0, spread=0, rear=0, ph=ph, sway=math.sin(math.radians(ph)), c2=c2)


def foot_fb(q, pair, view, lift=4.0, depth=1.6):
    c, l = step(q["ph"], 180*pair)
    d = c if view == "f" else -c
    return -d*depth + lift*l, 1 + 0.06*d, l


def qleg(top, x, y, sc, w0, w1, g, back=False, r=3.3, lifted=0.0):
    knee = ((top[0]*0.6+x*0.4), (top[1]+y)/2 + lifted*2)
    tube(chaikin([top, knee, (x, y+2.4)]), w0, w1*sc, g, sh=0.12)
    with T(x, y, sc):
        shape(ell(0, 1.5, r*(1-lifted*0.25), 2.0*(1-lifted*0.3), 16), g, LINE*0.8)
        if not back:
            for dx in (-1.1, 0, 1.1):
                stroke([(dx*r/3.3, 0.5), (dx*r/3.3*1.1, 2.0)], LINE*0.4)


def canine_fb(base, view, fur, fur_d, fur_l, eyecol, hackles=0.0):
    q = quad_fb(base, view)
    by, sp, h = q["by"], q["spread"], hackles
    sw = q["sway"]*3
    if view == "f":
        tl = bez((6, 30+by), (12, 30+by), (15+sw, 25+by), (14+sw*1.3, 17+by))
        form(ribbon(tl, 5.5, 2.0, 6.5, 0.7, 4), fur, sh=0.15)
        fill(ribbon(tl[-6:], 3, 0.5), fur_d)
        for s, pair in ((-1, 1), (1, 0)):
            y, sc, l = foot_fb(q, pair, view, 3.5)
            qleg((s*9, 26+by), s*(9.5+sp), y+3, sc*0.9, 7, 4, fur_d, lifted=l)
        form(notch(ell(0, 32+by, 13.5, 9.5, 28), 0.8+h*0.3, 3), fur, sh=0.14)
        chest = notch(ell(0, 23+by, 10, 11.5, 28), 1.0, 3)
        form(chest, fur, sdx=0, sdy=1.2, sh=0.15)
        clipped(chest, lambda: fill(ell(0, 19+by, 4.2, 7, 20), fur_l, 0.7))
        for x in (-5, -1.5, 2, 5.5):
            stroke([(x, 20+by), (x+0.4, 16.5+by)], LINE*0.4)
        for s, pair in ((-1, 0), (1, 1)):
            if q["rear"]:
                top = (s*6, 22+by); paw = (s*9.5, 13+by)
                tube(chaikin([top, (s*9, 19+by), paw]), 7.5, 4.5, fur, sh=0.12)
                shape(ell(paw[0], paw[1], 3.6, 2.8, 16), fur, LINE*0.8)
                claws(paw[0], paw[1]-1.5, -90, 3, 2.6, 26, BONE_FAR, LINE*0.6)
            else:
                y, sc, l = foot_fb(q, pair, view)
                qleg((s*6, 22+by), s*(5.5+sp), y, sc, 7.5, 4.5, fur, lifted=l)
        form(notch(ell(0, 34+by, 10.5, 8, 26), 1.5+h*0.4, 2), fur, sh=0.12)
        with T(q["sway"]*0.5, 40+by+q["hd"], q["hs"], rot=q["sway"]*-2):
            canine_face(q["jaw"], eyecol, fur, fur_d, fur_l, 1 if q["jaw"] else 0)
    else:
        with T(q["sway"]*0.5, 42+by+q["hd"], 1, rot=q["sway"]*2):
            canine_nape(fur, fur_d)
        for s, pair in ((-1, 0), (1, 1)):
            if q["rear"]:
                top = (s*8, 30+by); paw = (s*13, 41+by)
                tube(chaikin([top, (s*12, 33+by), paw]), 7, 4.5, fur_d, sh=0.12)
                shape(ell(paw[0], paw[1], 3.2, 2.6, 16), fur_d, LINE*0.8)
            else:
                y, sc, l = foot_fb(q, pair, view)
                qleg((s*8, 26+by), s*(8.5+sp), y+3, sc*0.9, 6.5, 4, fur_d, back=True, lifted=l)
        form(notch(ell(0, 32+by, 12.5, 9.5, 28), 0.8+h*0.35, 3), fur, sdx=0, sdy=1.2, sh=0.14)
        stroke(bez((0, 41+by), (0.6, 37+by), (-0.6, 31+by), (0, 27+by)), LINE*0.5)
        for s, pair in ((-1, 1), (1, 0)):
            y, sc, l = foot_fb(q, pair, view, 3.5)
            x = s*(6.5+sp)
            tube(chaikin([(s*6.5, 22+by), (s*7.6, 13+by*0.5+y*0.6), (x, y+2.4)]), 9.5, 4.4*sc, fur, sh=0.12)
            with T(x, y, sc):
                shape(ell(0, 1.4, 3.2, 1.9, 16), fur, LINE*0.8)
        rump = notch(ell(0, 22+by, 10.5, 9.5, 28), 0.8, 3)
        form(rump, fur, sdx=0, sdy=1.4, sh=0.15)
        for s in (-1, 1):
            stroke(bez((s*3.5, 14+by), (s*7, 14.5+by), (s*9.5, 19+by), (s*9, 25+by)), LINE*0.5)
        tsw = -q["sway"]*3 if q["ph"] is not None else 0
        up = 5 if base == "windup" else (-3 if base == "attack" else 0)
        tl = bez((0, 29+by), (tsw*0.2, 24+by+up), (tsw*0.7+1, 16+by+up), (tsw*1.6+2, 8+by+up*1.4))
        form(ribbon(tl, 6, 2.2, 8.5, 0.9, 3), fur, w=LINE*0.9, sdx=-1.5, sdy=1, sh=0.12)
        stroke(tl[3:-4], LINE*0.4, g=fur_d)


def vlk(pose):
    base, v = view_of(pose)
    if v: canine_fb(base, v, WOLF, WOLF_D, WOLF_L, EYE_Y)
    else: canine(base, WOLF, WOLF_D, WOLF_L, EYE_Y)


def cerny_pes(pose):
    base, v = view_of(pose)
    with T(0, 0, 1.08):
        if v: canine_fb(base, v, DOG, DOG_D, DOG_L, EYE_R, hackles=2.0)
        else: canine(base, DOG, DOG_D, DOG_L, EYE_R, hackles=2.0)


RAT = Col(0.45, "#7a6c62")
RAT_D = Col(0.36, "#5f544d")
RAT_TAIL = Col(0.6, "#b88d88")

RP = {
    "idle": dict(tilt=0, y=3, ff=(0, 0), fn=(2, 0), hf=(0, 0), hn=(2, 0), lf=(0, 0, 0, 0), head=-6, jaw=0, tail=0),
    "windup": dict(tilt=-8, y=2.6, ff=(1, 0), fn=(3, 0), hf=(-3, 0), hn=(-1, 0), lf=(0, 0, 0, 0), head=-14, jaw=16, tail=6),
    "attack": dict(tilt=22, y=4, ff=(5, 6), fn=(7, 4), hf=(-2, 0), hn=(0, 0), lf=(6, 4, 0, 0), head=10, jaw=30, tail=-4),
}
for _i, _n in enumerate(WALKS):
    _ca, _la = step(90*_i); _cb, _lb = step(90*_i, 180); _c2 = math.cos(math.radians(180*_i))
    RP[_n] = dict(tilt=-2+1*_c2, y=3.3-0.2*_c2, ll=3.7, ff=(-1.5+5*_cb+0.8*_lb, 0), fn=(-0.5+5*_ca+0.8*_la, 0),
                  hf=(5*_ca+0.8*_la, 0), hn=(1+5*_cb+0.8*_lb, 0), lf=(2*_lb, 2*_la, 2*_la, 2*_lb),
                  head=-4+2*_c2, jaw=0, tail=0.5+3.5*math.sin(math.radians(90*_i)))


def krysa(pose):
    base, v = view_of(pose)
    if v:
        with T(0, 0, 0.9):
            krysa_fb(base, v)
    else:
        with T(3, 0, 0.9):
            _krysa(base)


def _krysa(pose):
    q = RP[pose]
    tilt = q["tilt"]
    hip = (-8, q["y"]+4)
    with T(hip[0], hip[1], 1, rot=tilt):
        tl = q["tail"]
        tube(bez((-4, -1), (-11, -4), (-14, 2+tl), (-19, 1+tl*0.5)), 2.4, 0.6, RAT_TAIL, lw=LINE*0.7, sh=0)

    def leg(j, foot, lift, g, front):
        f = (j[0]+foot[0]+(2 if front else -1), lift+0.8)
        a, k, w = ik(j, f, q.get("ll", 3.4), q.get("ll", 3.4), -1 if front else 1)
        tube(chaikin([a, k, w]), 3.2, 1.8, g, lw=LINE*0.7, sh=0)
        for i in range(3):
            stroke([w, (w[0]+1.6, w[1]-0.4+i*0.4-0.4)], LINE*0.45, g=RAT_TAIL)

    leg(world(hip, tilt, (13, -1)), q["ff"], q["lf"][0], RAT_D, True)
    leg(world(hip, tilt, (1, -1)), q["hf"], q["lf"][2], RAT_D, False)
    with T(hip[0], hip[1], 1, rot=tilt):
        body = notch(bez((-4, -1), (-6, 5), (2, 9), (9, 8)) + bez((9, 8), (14, 7.5), (17, 5), (18, 2)), 1.0, 3) + \
               bez((18, 2), (17, -2), (12, -3.5), (6, -3)) + bez((6, -3), (1, -4), (-3, -3.5), (-4, -1))
        form(body, RAT, sdx=-1.5, sdy=1, sh=0.16)
        stroke(bez((0, -2), (-1, 1), (1, 3), (3, 3.5)), LINE*0.5)
        with T(17, 4, 1, rot=q["head"]):
            hx, hy = 3, -1
            jaw = q["jaw"]
            lo = rot([(2, -1), (8, -2.2), (8.5, -1.2), (2, 0)], hx, hy, -jaw)
            if jaw:
                tp = rot([(8.5, -1.6)], hx, hy, -jaw)[0]
                shape([(2, -0.5), (10, -0.6), tp], MOUTH_D, LINE*0.5)
                fill([(9.3, -0.6), (10.3, -0.6), (9.8, -2.6)], TOOTH)
            form(lo, RAT_D, sh=0)
            hd = bez((-3, -2), (-4, 3), (1, 5), (4, 3.5)) + bez((4, 3.5), (6.5, 2), (9, 0.8), (10.5, 0)) + \
                 bez((10.5, 0), (11, -0.6), (10.5, -1.0), (9.5, -0.9)) + [(3, -1.5)]
            form(hd, RAT, sh=0.14)
            shape(ell(-0.5, 4.5, 2.6, 2.8, 16), RAT_TAIL, LINE*0.7)
            fill(ell(-0.3, 4.3, 1.4, 1.7, 12), RAT_D)
            dot(10.6, -0.3, 0.7, MOUTH_D)
            for k in (-1, 0, 1):
                stroke([(9, -0.2+k*0.3), (13, 0.8+k*1.2)], LINE*0.3)
            eye(4.6, 1.5, 0.75, EYE_R, 2.4)
    leg(world(hip, tilt, (0, -1.5)), q["hn"], q["lf"][3], RAT, False)
    leg(world(hip, tilt, (14, -1.5)), q["fn"], q["lf"][1], RAT, True)


RFB = {
    "idle": dict(by=0, hd=0, hs=1.0, jaw=0, up=0),
    "windup": dict(by=-0.6, hd=1.8, hs=0.96, jaw=16, up=0),
    "attack": dict(by=0.4, hd=-1.6, hs=1.16, jaw=30, up=1),
}


def rat_leg(top, x, y, g, back, l=0.0):
    tube(chaikin([top, ((top[0]+x)/2, (top[1]+y)/2+l), (x, y+0.8)]), 3.2, 1.8, g, lw=LINE*0.7, sh=0)
    for dx in (-0.8, 0, 0.8):
        stroke([(x, y+0.8), (x+dx, y-0.6 if not back else y+0.2)], LINE*0.45, g=RAT_TAIL)


def krysa_fb(base, view):
    ph = phase(base)
    q = dict(RFB[base]) if ph is None else dict(by=0, hd=-0.3+0.3*math.cos(math.radians(2*ph)), hs=1.0, jaw=0, up=0)
    by, sw = q["by"], (math.sin(math.radians(ph)) if ph is not None else 0)

    def foot(pair):
        c, l = step(ph, 180*pair)
        d = c if view == "f" else -c
        return -d*0.8 + 1.7*l, l

    if view == "f":
        tl = bez((3, 5+by), (8, 3), (12, 1.5+sw), (17+sw*2, 2.5+sw))
        tube(tl, 2.2, 0.6, RAT_TAIL, lw=LINE*0.7, sh=0)
        for s, pair in ((-1, 1), (1, 0)):
            y, l = foot(pair)
            rat_leg((s*5.5, 6+by), s*6.5, y+1, RAT_D, False, l)
        body = notch(ell(0, 9.5+by, 8.5, 7, 28), 1.0, 3)
        form(body, RAT, sdx=0, sdy=1, sh=0.16)
        for s, pair in ((-1, 0), (1, 1)):
            if q["up"]:
                p = (s*4.2, 8+by)
                tube([(s*3, 9+by), p], 3.2, 2, RAT_D, lw=LINE*0.7, sh=0)
                claws(p[0], p[1], -90+s*20, 3, 1.6, 28, RAT_TAIL, LINE*0.45)
            else:
                y, l = foot(pair)
                rat_leg((s*3, 7+by), s*3.4, y, RAT_D, False, l)
        with T(sw*0.3, 10.5+by+q["hd"], q["hs"]):
            for s in (-1, 1):
                shape(ell(s*4.4, 4.2, 2.7, 2.9, 16), RAT_TAIL, LINE*0.7)
                fill(ell(s*4.3, 4.0, 1.5, 1.8, 12), RAT_D)
            form(ell(0, 1.2, 4.6, 4.0, 22), RAT, sdx=0, sdy=0.8, sh=0.14)
            j = q["jaw"]
            if j:
                shape(ell(0, -4.4-j*0.03, 1.5, 0.8+j*0.04, 12), MOUTH_D, LINE*0.5)
                fill([(-0.6, -5.6-j*0.07), (0.6, -5.6-j*0.07), (0, -4.0-j*0.04)], TOOTH)
            sn = mirrored(bez((0, 0.5), (-2.8, 0.3), (-2.6, -2.4), (-0.7, -3.6)) + [(0, -3.8)])
            form(sn, RAT, sdx=0, sdy=0.6, sh=0.12)
            dot(0, -3.4, 0.8, RAT_TAIL)
            fill([(-0.6, -3.9), (0.6, -3.9), (0.45, -4.9), (-0.45, -4.9)], TOOTH)
            for s in (-1, 1):
                for k in (-1, 0, 1):
                    stroke([(s*1.4, -2.8+k*0.3), (s*6.2, -2.2+k*1.1)], LINE*0.3)
                eye(s*2.1, 1.3, 0.75, EYE_R, 2.4)
    else:
        with T(sw*0.3, 11+by+q["hd"]*0.5, 1):
            for s in (-1, 1):
                shape(ell(s*4.2, 4.0, 2.7, 2.9, 16), RAT, LINE*0.7)
                stroke(ell(s*4.2, 3.9, 1.6, 1.9, 12, a0=200 if s < 0 else -20, a1=340 if s < 0 else 160), LINE*0.4)
            form(ell(0, 1.0, 4.4, 3.6, 22), RAT, sdx=0, sdy=0.8, sh=0.14)
        for s, pair in ((-1, 0), (1, 1)):
            if q["up"]:
                p = (s*7.5, 13+by)
                tube([(s*5, 10+by), p], 3, 1.8, RAT_D, lw=LINE*0.7, sh=0)
            else:
                y, l = foot(pair)
                rat_leg((s*4, 7+by), s*4.2, y+1.2, RAT_D, True, l)
        body = notch(ell(0, 8.5+by, 8.5, 7, 28), 1.0, 3)
        form(body, RAT, sdx=0, sdy=1.2, sh=0.16)
        stroke(bez((0, 15+by), (0.5, 12+by), (-0.5, 7+by), (0, 3+by)), LINE*0.5)
        for s, pair in ((-1, 1), (1, 0)):
            y, l = foot(pair)
            rat_leg((s*5, 5+by), s*5.6, y, RAT, True, l)
        tl = bez((0, 4+by), (0, 0.5), (4+sw*2, -0.8), (11+sw*3, -0.5+sw))
        tube(tl, 2.5, 0.6, RAT_TAIL, lw=LINE*0.7, sh=0)


BAT = Col(0.42, "#6a5a62")
BAT_D = Col(0.33, "#54474f")
BAT_WING = Col(0.38, "#6e5560")
BAT_L = Col(0.5, "#86727c")

BTP = {
    "idle": dict(w=(0, 8), k=(0.8, 1.0), y=0, tilt=0, jaw=0, head=0),
    "walk": dict(w=(-9, -6), k=(0.8, 1.0), y=1.2, tilt=4, jaw=0, head=0),
    "walk2": dict(w=(1, 5), k=(0.6, 0.72), y=0.4, tilt=1, jaw=0, head=1),
    "walk3": dict(w=(11, 17), k=(0.8, 1.0), y=-1.0, tilt=-2, jaw=0, head=2),
    "walk4": dict(w=(5, 10), k=(0.86, 1.08), y=-0.4, tilt=2, jaw=0, head=1),
    "windup": dict(w=(14, 20), k=(0.8, 1.0), y=0, tilt=16, jaw=16, head=10),
    "attack": dict(w=(6, 14), k=(0.8, 1.0), y=0, tilt=-24, jaw=34, head=-10),
}


def _bat_wing(s, wy, g, k=1.0):
    sh = (s*2.0, 2.5)
    wr = (s*11*k, 7+wy*0.7)
    tips = [(s*23*k, 6+wy), (s*21*k, -2+wy*0.6), (s*13*k, -7+wy*0.3)]
    mem = [sh, wr, tips[0]]
    prev = tips[0]
    for t in tips[1:] + [(s*3.5, -3.5)]:
        mx, my = (prev[0]+t[0])/2, (prev[1]+t[1])/2
        cx, cy = (mx + wr[0])/2, (my + wr[1])/2
        mem += bez(prev, (prev[0]*0.8+cx*0.2, prev[1]*0.8+cy*0.2), (t[0]*0.8+cx*0.2, t[1]*0.8+cy*0.2), t)[1:]
        prev = t
    form(mem, g, sh=0.15)
    stroke([sh, wr], LINE*1.0)
    for t in tips:
        stroke([wr, t], LINE*0.6)
    stroke([wr, (wr[0]+s*0.5, wr[1]+2.2)], LINE*0.9)


def netopyr(pose):
    base, v = view_of(pose)
    if v:
        with T(0, 0, 0.88):
            netopyr_fb(base, v)
    else:
        with T(-3, 0, 0.88):
            _netopyr(base)


def _netopyr(pose):
    q = BTP[pose]
    with T(0, q["y"], 1, rot=q["tilt"]):
        _bat_wing(-1, q["w"][0], BAT_D, q["k"][0])
        for s in (-1, 1):
            stroke([(s*1.5, -4), (s*2.2, -7.5), (s*3, -8)], LINE*0.6)
        body = notch(ell(0, 0, 4.6, 5.8, 26), 0.5, 3)
        form(body, BAT, sh=0.15)
        _bat_wing(1, q["w"][1], BAT_WING, q["k"][1])
        with T(1.5, 6, 1, rot=q["head"]):
            for ex in (-2.5, 1.5):
                e = [(ex-1.4, 1.5), (ex+0.2, 7.5), (ex+2.0, 1.8)]
                form(e, BAT, sh=0.12)
                fill([(ex-0.5, 2.4), (ex+0.2, 6), (ex+1.1, 2.4)], RAT_TAIL)
            hd = ell(0.5, 0, 3.6, 3.2, 22)
            form(hd, BAT, sh=0.12)
            sn = [(2.5, 1), (5.2, 0.1), (5.0, -1.4), (2.6, -1.8)]
            form(sn, BAT_D, sh=0)
            jaw = q["jaw"]
            if jaw:
                shape([(2.6, -1.2), (6.4, -2.8), (3.0, -3.4)], MOUTH_D, LINE*0.5)
                fill([(4.2, -1.6), (4.9, -1.6), (4.6, -3.0)], TOOTH)
                fill([(5.2, -2.1), (5.8, -2.3), (5.5, -3.0)], TOOTH)
            else:
                fill([(3.6, -1.6), (4.2, -1.6), (3.9, -2.6)], TOOTH)
            eye(2.2, 0.8, 0.7, EYE_R, 2.2)


def netopyr_fb(base, view):
    q = BTP[base]
    wy = (q["w"][0]+q["w"][1])/2
    k = q["k"][1]*0.94
    front = view == "f"
    hs = 1.15 if base == "attack" else 1.0
    with T(0, q["y"] - (1.5 if base == "attack" else 0), 1):
        for s in (-1, 1):
            _bat_wing(s, wy, BAT_WING if front else BAT_D, k)
        for s in (-1, 1):
            stroke([(s*1.5, -4), (s*1.9, -7.5), (s*2.6, -8.2)], LINE*0.6)
        body = notch(ell(0, 0, 4.6, 5.8, 26), 0.5, 3)
        form(body, BAT, sdx=0, sdy=1.0, sh=0.15)
        if front:
            clipped(body, lambda: fill(ell(0, -1.2, 2.8, 4.2, 18), BAT_L, 0.55))
        else:
            stroke(bez((0, 4.5), (0.4, 1.5), (-0.4, -1.5), (0, -4.5)), LINE*0.45)
        with T(0, 6.2 - (1.2 if base == "attack" else 0), hs):
            for s in (-1, 1):
                e = [(s*1.0, 1.4), (s*3.0, 7.6), (s*4.0, 1.0)]
                form(e, BAT, sh=0.12)
                if front:
                    fill([(s*1.8, 2.2), (s*3.0, 6.2), (s*3.4, 2.0)], RAT_TAIL)
            form(ell(0, 0, 3.6, 3.1, 22), BAT, sdx=0, sdy=0.8, sh=0.12)
            if front:
                jaw = q["jaw"]
                if jaw:
                    shape(ell(0, -2.4-jaw*0.02, 1.7, 0.6+jaw*0.035, 12), MOUTH_D, LINE*0.5)
                form(ell(0, -1.0, 1.8, 1.2, 14), BAT_D, sh=0)
                dot(-0.6, -0.9, 0.3, SOCKET); dot(0.6, -0.9, 0.3, SOCKET)
                for s in (-1, 1):
                    fill([(s*0.4, -2.0), (s*1.1, -2.0), (s*0.8, -3.2-jaw*0.02)], TOOTH)
                    eye(s*1.55, 0.7, 0.65, EYE_R, 2.2)
            else:
                stroke(bez((-2, 1.6), (-0.8, 2.2), (0.8, 2.2), (2, 1.6)), LINE*0.4)


STONE = Col(0.5, "#7d8187")
STONE_D = Col(0.4, "#62676e")
STONE_L = Col(0.68, "#a6a9a6")
LICHEN = Col(0.5, "#7f8c4c")
SPIT = Col(0.7, "#a8d65a")

SNP = {
    "idle": dict(sp=[(-44, 3.5), (-36, 4), (-26, 10), (-14, 5)], up=[(-14, 5), (2, 0), (10, 8), (8, 22), (4, 34), (12, 42)], head=-8, jaw=0),
    "windup": dict(sp=[(-44, 3.5), (-36, 4), (-26, 10), (-14, 5)], up=[(-14, 5), (2, 0), (6, 10), (0, 22), (-6, 34), (0, 44)], head=-22, jaw=14),
    "attack": dict(sp=[(-44, 3.5), (-36, 4), (-26, 10), (-14, 5)], up=[(-14, 5), (0, 0), (8, 6), (10, 20), (18, 30), (30, 32)], head=-2, jaw=38),
}
_SA = dict(sp=[(-46, 6), (-38, 9), (-28, 3), (-16, 8)], up=[(-16, 8), (-2, 13), (10, 2), (14, 16), (12, 28), (20, 34)], head=-14)
_SB = dict(sp=[(-45, 4), (-37, 2.5), (-27, 8), (-15, 3.5)], up=[(-15, 3.5), (0, 1), (12, 11), (10, 22), (6, 32), (14, 40)], head=-10)
_SP = dict(sp=[(0, -2.5), (1, 3), (0, -3), (0, 2.5)], up=[(0, 2.5), (2, -4), (-3, 4), (3, -3), (-2, 3), (-1, 3)], head=2)
for _i, _n in enumerate(WALKS):
    _c, _s = math.cos(math.radians(90*_i)), math.sin(math.radians(90*_i))
    _mix = lambda a, b, p: [((x+u)/2+_c*(x-u)/2+_s*px, (y+w)/2+_c*(y-w)/2+_s*py) for (x, y), (u, w), (px, py) in zip(a, b, p)]
    SNP[_n] = dict(sp=_mix(_SA["sp"], _SB["sp"], _SP["sp"]), up=_mix(_SA["up"], _SB["up"], _SP["up"]),
                   head=(_SA["head"]+_SB["head"])/2+_c*(_SA["head"]-_SB["head"])/2+_s*_SP["head"], jaw=0)


def kamenny_had(pose):
    base, v = view_of(pose)
    with T(0, 4.2, 1.15):
        if v: had_fb(base, v)
        else: _kamenny_had(base)


def stone_tube(spine, wf):
    P = resample(spine, 0.8); n = len(P)
    left, right = [], []
    for i in range(n):
        p0 = P[max(0, i-1)]; p1 = P[min(n-1, i+1)]
        dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy) or 1
        w = wf(i/(n-1))
        left.append((P[i][0]-dy/L*w/2, P[i][1]+dx/L*w/2)); right.append((P[i][0]+dy/L*w/2, P[i][1]-dx/L*w/2))
    body = left + list(reversed(right))
    form(body, STONE, sdx=-2.5, sdy=1.8, sh=0.2)

    def plates():
        for j, i in enumerate(range(8, n-4, 9)):
            p0 = P[i-1]; p1 = P[i+1]
            dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy) or 1
            sk = (1.5 if j % 2 else -1.0)
            m = ((left[i][0]+right[i][0])/2+dx/L*sk, (left[i][1]+right[i][1])/2+dy/L*sk)
            stroke([left[i], m, (right[i][0]+dx/L*1.6, right[i][1]+dy/L*1.6)], LINE*0.6)
            if j % 3 == 1:
                stroke([m, (m[0]-dx/L*3+1, m[1]-dy/L*3+1)], LINE*0.45)
        for i in range(10, n-10, 13):
            fill(ell(P[i][0]-1, P[i][1]+2, 2.6, 1.6, 12, rot=20), LICHEN)
        for i in range(14, n-6, 19):
            stroke([P[i], (P[i][0]+2, P[i][1]-2), (P[i][0]+1.5, P[i][1]-4)], LINE*0.5)
        stroke([(x+0.4, y-0.4) for x, y in right[int(n*0.6):-2]], LINE*1.6, g=STONE_L)
    clipped(body, plates)
    stroke(body, LINE, closed=True)
    return P


def _kamenny_had(pose):
    q = SNP[pose]
    a = q["sp"]; u = q["up"]
    spine = bez(*a) + bez(u[0], u[1], u[2], u[3])[1:] + bez(u[3], (u[3][0]+(u[3][0]-u[2][0]), u[3][1]+(u[3][1]-u[2][1])), u[4], u[5])[1:]
    stone_tube(spine, lambda t: 1.0 + 13*min(1, t/0.35) if t < 0.75 else 14 - 4.5*(t-0.75)/0.25)
    hx, hy = u[5]
    with T(hx, hy, 1, rot=q["head"]):
        jaw = q["jaw"]
        lo = rot([(0, -3), (10, -4.2), (11, -2.8), (0, -0.5)], 1, -2, -jaw)
        if jaw:
            tip = rot([(11, -3.5)], 1, -2, -jaw)[0]
            shape([(0, -1.5), (13, -1.3), tip], MOUTH_D, LINE*0.6)
            fill(rot([(3, -2.6), (9, -3.2), (12, -6), (10, -3)], 1, -2, -jaw*0.6), TONGUE)
            for x in (3, 7, 11):
                fill([(x-0.6, -1.4), (x+0.6, -1.4), (x, -3.0)], TOOTH)
        form(lo, STONE_D, sh=0)
        hd = bez((-5, -3), (-6, 3), (-2, 5.5), (3, 5.2)) + bez((3, 5.2), (7, 5), (11, 2.5), (13.5, 0)) + \
             bez((13.5, 0), (14, -1), (13.5, -1.6), (12.5, -1.6)) + [(1, -2), (-4, -4)]
        form(hd, STONE, sh=0.16)
        shape([(1.5, 4.5), (4.5, 6.8), (7.5, 4.4)], STONE_D, LINE*0.6)
        stroke([(-3, 1), (0, 2.5), (1, 0.5)], LINE*0.5)
        fill(ell(5.2, 2.6, 2.2, 1.5, 14), SOCKET)
        eye(5.4, 2.6, 1.0, EYE_Y, 2.4)
        dot(12, 0.2, 0.6, SOCKET)
        if pose == "attack":
            for i, (dx, dy, r) in enumerate(((19, -1, 2.6), (25, -2, 1.8), (29.5, -2.5, 1.2))):
                spit(dx, dy, r)


def spit(x, y, r):
    glow(x, y, r*2, SPIT, 0.18, 3)
    shape(ell(x, y, r, r*0.8, 14), SPIT, LINE*0.6)
    dot(x+r*0.3, y+r*0.3, r*0.3, WHITE)


HFB = {
    "idle": dict(hx=0, hy=40, hs=1.0, jaw=0, bend=0),
    "windup": dict(hx=0, hy=45, hs=0.92, jaw=14, bend=1),
    "attack": dict(hx=0, hy=33, hs=1.16, jaw=38, bend=-1),
}


def had_face(jaw, back):
    up = jaw*0.06
    half = bez((0, 6), (5, 6.2), (8.6, 3.8), (8.6, 0.6)) + bez((8.6, 0.6), (8.6, -2.4), (5.2, -4.4+up), (2.6, -5.0+up)) + [(0, -5.2+up)]
    if not back and jaw:
        jo = jaw*0.14
        shape([(-6.5, -2.4), (6.5, -2.4), (4.5, -5.5-jo), (0, -6.4-jo), (-4.5, -5.5-jo)], MOUTH_D, LINE*0.6)
        fill([(-0.6, -4), (0.6, -4), (1.6, -6.4-jo*0.8), (0.4, -5.6-jo*0.6), (-0.4, -5.6-jo*0.6), (-1.6, -6.4-jo*0.8)], TONGUE)
        form([(-5.5, -4.2-jo), (5.5, -4.2-jo), (3.5, -7.2-jo), (-3.5, -7.2-jo)], STONE_D, sh=0)
    if back:
        half = bez((0, 6.4), (5, 6.6), (8.8, 4), (8.6, 0.6)) + bez((8.6, 0.6), (8.4, -2.6), (4.5, -4.4), (0, -4.6))
    sk = mirrored(half)
    form(sk, STONE, sdx=0, sdy=1.0, sh=0.16)
    if back:
        clipped(sk, lambda: [fill(ell(3, 2.6, 2.6, 1.5, 12, rot=20), LICHEN),
                             stroke([(-5.5, 4.2), (0, 1.6), (5.5, 4.2)], LINE*0.6),
                             stroke([(-6.5, 0.2), (0, -2.6), (6.5, 0.2)], LINE*0.6),
                             stroke([(0, 6), (0, 1.6)], LINE*0.5)])
        for s in (-1, 1):
            shape([(s*4.5, 5.6), (s*6.8, 6.6), (s*8.2, 3.4)], STONE_D, LINE*0.6)
        return
    for s in (-1, 1):
        shape([(s*1.2, 4.6), (s*3.8, 6.6), (s*6.6, 4.2)], STONE_D, LINE*0.6)
        fill(ell(s*5.3, 1.4, 2.3, 1.6, 14), SOCKET)
        eye(s*5.4, 1.4, 1.0, EYE_Y, 2.4)
        dot(s*1.5, -3.6+up, 0.6, SOCKET)
        if jaw:
            fill([(s*3.6, -2.4), (s*2.6, -2.4), (s*3.0, -5.0)], TOOTH)
    stroke([(-1, 3), (0, 1.5), (1, 3)], LINE*0.45)
    if not jaw:
        stroke(bez((-6.5, -2.0), (-3, -3.8), (3, -3.8), (6.5, -2.0)), LINE*0.6)


def had_fb(base, view):
    ph = phase(base)
    if ph is None:
        q = HFB[base]; sw = 0.0
    else:
        sw = math.sin(math.radians(ph))
        q = dict(hx=-2.5*math.cos(math.radians(ph)), hy=39+math.cos(math.radians(2*ph)), hs=1.0, jaw=0, bend=0)
    rx, ry, cy = 21+1.2*(math.cos(math.radians(ph)) if ph is not None else 0), 6.5, 7
    hx, hy = q["hx"], q["hy"]
    oval = lambda a: (rx*math.cos(math.radians(a)), cy+ry*math.sin(math.radians(a)))

    def neck(p0, tan):
        b = q["bend"]
        mid1 = (p0[0]+tan[0]*8, p0[1]+tan[1]*8)
        mid2 = (-4*sw - 3*b + hx*0.3, hy*0.62 - 2*b)
        sp = bez(p0, mid1, (mid2[0]-2*sw, mid2[1]-5), mid2) + bez(mid2, (mid2[0]+2*sw, mid2[1]+6), (hx+3*sw, hy-9), (hx, hy-3))[1:]
        stone_tube(sp, lambda t: 12.5 - 2.5*t)

    if view == "f":
        tip = (rx+8, cy+3+2*sw)
        coil = bez(tip, (rx+4, cy+5), (rx+1, cy+3), oval(10))[:-1] + [oval(a) for a in range(10, 301, 6)]
        stone_tube(coil, lambda t: 1.5 + 10.5*min(1, t/0.22))
        neck(oval(300), (math.sin(math.radians(300))*-1, math.cos(math.radians(300))))
        with T(hx, hy, q["hs"]*1.35):
            had_face(q["jaw"], False)
        if base == "attack":
            for dy, r in ((-14, 2.8), (-21, 3.6), (-29, 4.4)):
                spit(hx+dy*0.05, hy+dy, r)
    else:
        if base == "attack":
            for dy, r in ((12, 1.6), (17, 1.1)):
                spit(hx, hy+dy, r)
        neck(oval(90), (0, 1))
        with T(hx, hy, q["hs"]*1.3):
            had_face(q["jaw"], True)
        coil = [oval(a) for a in range(96, 445, 6)] + [(oval(445)[0]-2*sw, oval(445)[1]+1)]
        stone_tube(coil, lambda t: 12 if t < 0.78 else 12 - 10.5*(t-0.78)/0.22)


WERE = Col(0.45, "#7b6a5a")
WERE_D = Col(0.36, "#5f5146")
WERE_L = Col(0.62, "#a39280")

WWP = {
    "idle": dict(hip=(-8, 46), lean=-24, ff=(-14, 0), nf=(6, 0), fh=(24, 4), nh=(30, 10), head=-4, jaw=10, tail=0),
    "walk": dict(hip=(-8, 45), lean=-29, ff=(-18, 2), nf=(10, 0), fh=(36, 18), nh=(16, 4), head=0, jaw=10, tail=-3),
    "walk2": dict(hip=(-8, 46.5), lean=-27, ff=(-3, 8), nf=(-5, 0), fh=(27, 10), nh=(25, 8), head=-3, jaw=10, tail=3),
    "walk3": dict(hip=(-8, 45), lean=-29, ff=(10, 0), nf=(-18, 2), fh=(16, 4), nh=(36, 18), head=0, jaw=10, tail=-3),
    "walk4": dict(hip=(-8, 46.5), lean=-27, ff=(-5, 0), nf=(-3, 8), fh=(25, 8), nh=(27, 10), head=-3, jaw=10, tail=3),
    "windup": dict(hip=(-6, 46), lean=2, ff=(-20, 0), nf=(10, 0), fh=(-4, 26), nh=(-22, 68), head=22, jaw=26, tail=6),
    "attack": dict(hip=(-10, 48), lean=-10, ff=(-24, 0), nf=(8, 0), fh=(44, 30), nh=(-8, 74), head=14, jaw=40, tail=-4),
}


def were_leg(j, foot, g):
    hock = (foot[0]+j[0]-4, foot[1]+14)
    a, k, h = ik(j, hock, 21, 18, 1)
    tube(chaikin([a, k, h]), 17, 6.5, g, sh=0.14)
    toe = (foot[0]+j[0]+1, foot[1]+2.5)
    tube([h, toe], 6.5, 5.5, g, sh=0.1)
    shape(ell(toe[0]+2.5, toe[1]-1.2, 5, 2.4, 16), g, LINE*0.8)
    claws(toe[0]+6.5, toe[1]-1.2, -10, 3, 2.4, 18, BONE_FAR)


def vlkodlak(pose):
    base, v = view_of(pose)
    if v:
        vlkodlak_fb(base, v)
        return
    pose = base
    q = WWP[pose]
    hip, lean = q["hip"], q["lean"]

    def arm(sh, hand, g, w):
        a, e, h = ik(sh, hand, 22, 21, -1)
        tube(chaikin([a, e, h]), w, w*0.6, g, sh=0.14)
        ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
        shape(ell(h[0], h[1], 4.0, 3.4, 16), g, LINE*0.8)
        claws(h[0]+math.cos(math.radians(ang))*3, h[1]+math.sin(math.radians(ang))*3, ang, 4, 5.0, 16, BONE_FAR, LINE*0.8)

    with T(hip[0], hip[1], 1, rot=lean):
        arm((2, 44), q["fh"], WERE_D, 11)
        t = q["tail"]
        tl = bez((-6, 2), (-16, -2+t*0.3), (-22, -8+t*0.7), (-26, -20+t))
        form(ribbon(tl, 7, 2.5, 9, 0.8, 3), WERE_D, sh=0.12)
    were_leg((hip[0]-2, hip[1]), q["ff"], WERE_D)
    with T(hip[0], hip[1], 1, rot=lean):
        body = notch(bez((-8, -4), (-13, 10), (-14, 32), (-8, 46)) + bez((-8, 46), (-2, 56), (12, 54), (18, 44)), 1.6, 3) + \
               notch(bez((18, 42), (22, 32), (18, 16), (10, 4)), 1.2, 3) + bez((10, 4), (4, -4), (-4, -7), (-8, -4))
        form(body, WERE, sdx=-4, sdy=2, sh=0.18)
        clipped(body, lambda: fill(ell(13, 26, 6, 14, 20, rot=15), WERE_L))
        for y in (30, 24, 18):
            stroke(bez((8, y), (12, y-1.5), (16, y-1), (18, y+1)), LINE*0.5)
        stroke(bez((-4, 38), (-8, 30), (-9, 18), (-6, 8)), LINE*0.5)
    were_leg((hip[0]+3, hip[1]), q["nf"], WERE)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(20, 50, 1.55, rot=q["head"]):
            canine_head(q["jaw"], EYE_Y, WERE, WERE_D, WERE_L, 1)
        arm((6, 44), q["nh"], WERE, 12.5)
    if pose == "attack":
        for i in range(3):
            swoosh(bez((10+i*6, 112-i*4), (30+i*6, 112-i*4), (44+i*5, 96-i*4), (46+i*4, 76-i*4)), 1.4, WHITE, 0.35)


WFB = {
    "idle": dict(hand=(27, 52), up=0, jaw=10, hd=0, hs=1.55, by=0),
    "windup": dict(hand=(31, 116), up=1, jaw=26, hd=3, hs=1.55, by=1),
    "attack": dict(hand=(11, 56), up=0, jaw=40, hd=-4, hs=1.68, by=-2),
}


def vlkodlak_fb(base, view):
    ph = phase(base)
    q = dict(WFB[base]) if ph is None else dict(WFB["idle"], hd=-1+math.cos(math.radians(2*ph)), by=-0.5+0.5*math.cos(math.radians(2*ph)))
    by = q["by"]
    front = view == "f"
    sw = math.sin(math.radians(ph)) if ph is not None else 0.0

    def legs():
        for s, pair in ((-1, 0), (1, 1)):
            c, l = step(ph, 180*pair)
            d = c if front else -c
            y = -d*2.5 + 8*l
            sc = 1 + 0.07*d
            x = s*11
            tube(chaikin([(s*10, 47+by), (s*15, 31+6*l), (s*11, 15+y)]), 17*sc, 7.5*sc, WERE, sh=0.14)
            shape(ell(s*11.2, 15.5+y, 3.6*sc, 3.0*sc, 14), WERE, LINE*0.6)
            tube([(s*11.5, 15+y), (x, y+3)], 7*sc, 6*sc, WERE, sh=0.1)
            with T(x, y, sc):
                if front:
                    shape(ell(0, 2.6, 5.8, 2.9, 18), WERE, LINE*0.8)
                    for dx in (-3, 0, 3):
                        claws(dx, 0.6, -90, 1, 2.2, 0, BONE_FAR, LINE*0.7)
                else:
                    shape(ell(0, 3.2, 4.6, 2.6, 18), WERE, LINE*0.8)
                    fill(ell(0, 3.0, 2.2, 1.2, 12), WERE_D)

    def tail(g):
        t = -sw*3
        tl = bez((0, 50+by), (2+t*0.4, 42+by), (9+t, 34+by), (17+t*1.4, 30+by))
        form(ribbon(tl, 8, 2.5, 10, 1.0, 3), g, sh=0.12)

    def torso():
        half = bez((0, 100), (12, 101), (22, 97), (23, 88)) + bez((23, 88), (23, 78), (17, 68), (14, 60)) + \
               bez((14, 60), (13, 54), (16, 48), (9, 42)) + [(0, 41)]
        body = mirrored([(x, y+by) for x, y in half])
        form(body, WERE, sdx=0, sdy=2, sh=0.18)
        if front:
            clipped(body, lambda: fill(ell(0, 72+by, 12, 15, 24), WERE_L))
            for s in (-1, 1):
                stroke(bez((s*13, 82+by), (s*8, 77+by), (s*3, 77+by), (s*0.5, 79+by)), LINE*0.55)
                for y in (66, 60, 54):
                    stroke(bez((s*1.5, y+by), (s*4, y-1+by), (s*6.5, y-0.6+by), (s*8, y+0.6+by)), LINE*0.45)
        else:
            sp = bez((0, 100+by), (0.8, 84+by), (-0.8, 66+by), (0, 52+by))
            form(ribbon(sp, 6, 1.5, 5, 1.0, 3), WERE_D, w=LINE*0.6, sh=0.06)
            for s in (-1, 1):
                stroke(bez((s*5, 92+by), (s*13, 91+by), (s*17, 84+by), (s*12, 76+by)), LINE*0.55)
                stroke(bez((s*6, 64+by), (s*10, 62+by), (s*13, 57+by), (s*12, 52+by)), LINE*0.45)
        mane = notch(bez((-23, 90+by), (-14, 104+by), (14, 104+by), (23, 90+by)) +
                     bez((23, 90+by), (14, 96+by), (-14, 96+by), (-23, 90+by)), 1.8, 2)
        form(mane, WERE_D, sh=0.1)

    def arms():
        for s, pair in ((-1, 1), (1, 0)):
            sh = (s*20, 90+by)
            if ph is not None:
                c, _ = step(ph, 180*pair)
                d = c if front else -c
                hand = (s*(27-1.5*d), 52-5*d)
            else:
                hand = (s*q["hand"][0], q["hand"][1])
            up = q["up"]
            a, e, h = ik(sh, hand, 22, 21, -s if up else s)
            tube(chaikin([a, e, h]), 12.5, 7.5, WERE, sh=0.14)
            shape(ell(h[0], h[1], 4.4, 3.8, 16), WERE, LINE*0.8)
            ang = 90 if up else (-90 + s*25 if base == "attack" else -90)
            claws(h[0]+math.cos(math.radians(ang))*3, h[1]+math.sin(math.radians(ang))*3, ang, 4, 5.0, 16, BONE_FAR, LINE*0.8)

    hx = sw*1.0
    if front:
        legs()
        torso()
        with T(hx, 84+by+q["hd"], q["hs"]):
            canine_face(q["jaw"], EYE_Y, WERE, WERE_D, WERE_L, 1)
        arms()
    else:
        with T(hx, 88+by+q["hd"], q["hs"]):
            canine_nape(WERE, WERE_D)
        legs()
        torso()
        tail(WERE_D)
        arms()
    if base == "attack":
        for s in (-1, 1):
            for i in range(3):
                swoosh(bez((s*(36-i*5), 116-i*3), (s*(40-i*5), 92-i*3), (s*(30-i*4), 70-i*3), (s*(14-i*2), 56-i*2)), 1.4, WHITE, 0.35)


for _f in (krysa, vlk, cerny_pes, netopyr, kamenny_had, vlkodlak):
    _f.poses = ALL
