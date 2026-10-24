import math
from bestiary_kit import *

WOLF = Col(0.5, "#746c63")
WOLF_D = Col(0.4, "#5c5650")
WOLF_L = Col(0.7, "#a9a196")
DOG = Col(0.33, "#5a5462")
DOG_D = Col(0.27, "#4a4552")
DOG_L = Col(0.42, "#6e6878")

QP = {
    "idle": dict(tilt=0, hipy=29, hipx=-19, ff=(0, 0), fn=(4, 0), hf=(-3, 0), hn=(1, 0), lift=(0, 0, 0, 0), head=-4, jaw=0, tail=-30, crouch=0),
    "walk": dict(tilt=-2, hipy=28.5, hipx=-19, ff=(-6, 0), fn=(10, 2), hf=(6, 3), hn=(-7, 0), lift=(0, 3, 3, 0), head=-8, jaw=0, tail=-20, crouch=0),
    "walk2": dict(tilt=-1, hipy=28.8, hipx=-19, ff=(10, 2), fn=(-6, 0), hf=(-7, 0), hn=(6, 3), lift=(3, 0, 0, 3), head=-6, jaw=0, tail=-26, crouch=0),
    "windup": dict(tilt=-7, hipy=26, hipx=-15, ff=(6, 0), fn=(9, 0), hf=(-6, 0), hn=(-2, 0), lift=(0, 0, 0, 0), head=-14, jaw=14, tail=-40, crouch=1),
    "attack": dict(tilt=14, hipy=24, hipx=-23, ff=(18, 10), fn=(22, 6), hf=(-12, 0), hn=(-8, 0), lift=(10, 6, 0, 0), head=8, jaw=34, tail=10, crouch=1),
}


def canine(pose, fur, fur_d, fur_l, eyecol, big=1.0, hackles=0.0):
    q = QP[pose]
    hip = (q["hipx"], q["hipy"])
    tilt = q["tilt"]
    sh = world(hip, tilt, (25, -2))
    hp = world(hip, tilt, (1, -2))

    def front(j, foot, lift, g):
        target = (foot[0]+sh[0]-3, lift+2.5)
        a, e, w = ik(j, target, 12, 12.5, -1 if lift < 5 else 1)
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


def vlk(pose):
    canine(pose, WOLF, WOLF_D, WOLF_L, EYE_Y)


def cerny_pes(pose):
    with T(0, 0, 1.08):
        canine(pose, DOG, DOG_D, DOG_L, EYE_R, hackles=2.0)


RAT = Col(0.45, "#7a6c62")
RAT_D = Col(0.36, "#5f544d")
RAT_TAIL = Col(0.6, "#b88d88")

RP = {
    "idle": dict(tilt=0, y=3, ff=(0, 0), fn=(2, 0), hf=(0, 0), hn=(2, 0), lf=(0, 0, 0, 0), head=-6, jaw=0, tail=0),
    "walk": dict(tilt=-3, y=3.4, ff=(-3, 1.5), fn=(4, 0), hf=(3, 0), hn=(-3, 1.5), lf=(1.5, 0, 0, 1.5), head=-2, jaw=0, tail=4),
    "walk2": dict(tilt=-1, y=3.4, ff=(4, 0), fn=(-3, 1.5), hf=(-3, 1.5), hn=(3, 0), lf=(0, 1.5, 1.5, 0), head=-5, jaw=0, tail=-3),
    "windup": dict(tilt=-8, y=2.6, ff=(1, 0), fn=(3, 0), hf=(-3, 0), hn=(-1, 0), lf=(0, 0, 0, 0), head=-14, jaw=16, tail=6),
    "attack": dict(tilt=22, y=4, ff=(5, 6), fn=(7, 4), hf=(-2, 0), hn=(0, 0), lf=(6, 4, 0, 0), head=10, jaw=30, tail=-4),
}


def krysa(pose):
    with T(3, 0, 0.9):
        _krysa(pose)


def _krysa(pose):
    q = RP[pose]
    tilt = q["tilt"]
    hip = (-8, q["y"]+4)
    with T(hip[0], hip[1], 1, rot=tilt):
        tl = q["tail"]
        tube(bez((-4, -1), (-11, -4), (-14, 2+tl), (-19, 1+tl*0.5)), 2.4, 0.6, RAT_TAIL, lw=LINE*0.7, sh=0)

    def leg(j, foot, lift, g, front):
        f = (j[0]+foot[0]+(2 if front else -1), lift+0.8)
        a, k, w = ik(j, f, 3.4, 3.4, -1 if front else 1)
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


BAT = Col(0.42, "#6a5a62")
BAT_D = Col(0.33, "#54474f")
BAT_WING = Col(0.38, "#6e5560")

BTP = {
    "idle": dict(w=(0, 8), tilt=0, jaw=0, head=0),
    "walk": dict(w=(-9, -6), tilt=4, jaw=0, head=0),
    "walk2": dict(w=(11, 17), tilt=-2, jaw=0, head=2),
    "windup": dict(w=(14, 20), tilt=16, jaw=16, head=10),
    "attack": dict(w=(6, 14), tilt=-24, jaw=34, head=-10),
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
    with T(-3, 0, 0.88):
        _netopyr(pose)


def _netopyr(pose):
    q = BTP[pose]
    with T(0, 0, 1, rot=q["tilt"]):
        _bat_wing(-1, q["w"][0], BAT_D, 0.8)
        for s in (-1, 1):
            stroke([(s*1.5, -4), (s*2.2, -7.5), (s*3, -8)], LINE*0.6)
        body = notch(ell(0, 0, 4.6, 5.8, 26), 0.5, 3)
        form(body, BAT, sh=0.15)
        _bat_wing(1, q["w"][1], BAT_WING)
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


STONE = Col(0.5, "#7d8187")
STONE_D = Col(0.4, "#62676e")
STONE_L = Col(0.68, "#a6a9a6")
LICHEN = Col(0.5, "#7f8c4c")
SPIT = Col(0.7, "#a8d65a")

SNP = {
    "idle": dict(sp=[(-44, 3.5), (-36, 4), (-26, 10), (-14, 5)], up=[(-14, 5), (2, 0), (10, 8), (8, 22), (4, 34), (12, 42)], head=-8, jaw=0),
    "walk": dict(sp=[(-46, 6), (-38, 9), (-28, 3), (-16, 8)], up=[(-16, 8), (-2, 13), (10, 2), (14, 16), (12, 28), (20, 34)], head=-14, jaw=0),
    "walk2": dict(sp=[(-45, 4), (-37, 2.5), (-27, 8), (-15, 3.5)], up=[(-15, 3.5), (0, 1), (12, 11), (10, 22), (6, 32), (14, 40)], head=-10, jaw=0),
    "windup": dict(sp=[(-44, 3.5), (-36, 4), (-26, 10), (-14, 5)], up=[(-14, 5), (2, 0), (6, 10), (0, 22), (-6, 34), (0, 44)], head=-22, jaw=14),
    "attack": dict(sp=[(-44, 3.5), (-36, 4), (-26, 10), (-14, 5)], up=[(-14, 5), (0, 0), (8, 6), (10, 20), (18, 30), (30, 32)], head=-2, jaw=38),
}


def kamenny_had(pose):
    with T(0, 4.2, 1.15):
        _kamenny_had(pose)


def _kamenny_had(pose):
    q = SNP[pose]
    a = q["sp"]; u = q["up"]
    spine = bez(*a) + bez(u[0], u[1], u[2], u[3])[1:] + bez(u[3], (u[3][0]+(u[3][0]-u[2][0]), u[3][1]+(u[3][1]-u[2][1])), u[4], u[5])[1:]
    P = resample(spine, 0.8); n = len(P)
    left, right = [], []
    for i in range(n):
        p0 = P[max(0, i-1)]; p1 = P[min(n-1, i+1)]
        dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy) or 1
        t = i/(n-1)
        w = 1.0 + 13*min(1, t/0.35) if t < 0.75 else 14 - 4.5*(t-0.75)/0.25
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
    hx, hy = u[5]
    ang = math.degrees(math.atan2(u[5][1]-u[4][1], u[5][0]-u[4][0]))
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
                glow(dx, dy, r*2, SPIT, 0.18, 3)
                shape(ell(dx, dy, r, r*0.8, 14), SPIT, LINE*0.6)
                dot(dx+r*0.3, dy+r*0.3, r*0.3, WHITE)


WERE = Col(0.45, "#7b6a5a")
WERE_D = Col(0.36, "#5f5146")
WERE_L = Col(0.62, "#a39280")

WWP = {
    "idle": dict(hip=(-8, 46), lean=-24, ff=(-14, 0), nf=(6, 0), fh=(24, 4), nh=(30, 10), head=-4, jaw=10),
    "walk": dict(hip=(-8, 45), lean=-30, ff=(8, 3), nf=(-18, 0), fh=(14, 2), nh=(36, 18), head=0, jaw=10),
    "walk2": dict(hip=(-8, 45), lean=-28, ff=(-18, 0), nf=(8, 3), fh=(34, 18), nh=(16, 4), head=-2, jaw=10),
    "windup": dict(hip=(-6, 46), lean=2, ff=(-20, 0), nf=(10, 0), fh=(-4, 26), nh=(-22, 68), head=22, jaw=26),
    "attack": dict(hip=(-10, 48), lean=-10, ff=(-24, 0), nf=(8, 0), fh=(44, 30), nh=(-8, 74), head=14, jaw=40),
}


def vlkodlak(pose):
    q = WWP[pose]
    hip, lean = q["hip"], q["lean"]

    def leg(j, foot, g):
        hock = (foot[0]+j[0]-4, foot[1]+14)
        a, k, h = ik(j, hock, 21, 18, 1)
        tube(chaikin([a, k, h]), 17, 6.5, g, sh=0.14)
        toe = (foot[0]+j[0]+1, foot[1]+2.5)
        tube([h, toe], 6.5, 5.5, g, sh=0.1)
        shape(ell(toe[0]+2.5, toe[1]-1.2, 5, 2.4, 16), g, LINE*0.8)
        claws(toe[0]+6.5, toe[1]-1.2, -10, 3, 2.4, 18, BONE_FAR)

    def arm(sh, hand, g, w):
        a, e, h = ik(sh, hand, 22, 21, -1)
        tube(chaikin([a, e, h]), w, w*0.6, g, sh=0.14)
        ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
        shape(ell(h[0], h[1], 4.0, 3.4, 16), g, LINE*0.8)
        claws(h[0]+math.cos(math.radians(ang))*3, h[1]+math.sin(math.radians(ang))*3, ang, 4, 5.0, 16, BONE_FAR, LINE*0.8)

    with T(hip[0], hip[1], 1, rot=lean):
        arm((2, 44), q["fh"], WERE_D, 11)
        tl = bez((-6, 2), (-16, -2), (-22, -8), (-26, -20))
        form(ribbon(tl, 7, 2.5, 9, 0.8, 3), WERE_D, sh=0.12)
    leg((hip[0]-2, hip[1]), q["ff"], WERE_D)
    with T(hip[0], hip[1], 1, rot=lean):
        body = notch(bez((-8, -4), (-13, 10), (-14, 32), (-8, 46)) + bez((-8, 46), (-2, 56), (12, 54), (18, 44)), 1.6, 3) + \
               notch(bez((18, 42), (22, 32), (18, 16), (10, 4)), 1.2, 3) + bez((10, 4), (4, -4), (-4, -7), (-8, -4))
        form(body, WERE, sdx=-4, sdy=2, sh=0.18)
        clipped(body, lambda: fill(ell(13, 26, 6, 14, 20, rot=15), WERE_L))
        for y in (30, 24, 18):
            stroke(bez((8, y), (12, y-1.5), (16, y-1), (18, y+1)), LINE*0.5)
        stroke(bez((-4, 38), (-8, 30), (-9, 18), (-6, 8)), LINE*0.5)
    leg((hip[0]+3, hip[1]), q["nf"], WERE)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(20, 50, 1.55, rot=q["head"]):
            canine_head(q["jaw"], EYE_Y, WERE, WERE_D, WERE_L, 1)
        arm((6, 44), q["nh"], WERE, 12.5)
    if pose == "attack":
        for i in range(3):
            swoosh(bez((10+i*6, 112-i*4), (30+i*6, 112-i*4), (44+i*5, 96-i*4), (46+i*4, 76-i*4)), 1.4, WHITE, 0.35)
