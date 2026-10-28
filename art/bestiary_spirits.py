import math
from bestiary_kit import *

WISP = Col(0.9, "#d6f2a8")
WISP_L = Col(0.98, "#f4ffe2")
WISP_LINE = Col(0.5, "#6f9a5a")
WISP_GLOW = Col(0.8, "#b8f08a")

BLP = {
    "idle": dict(lean=0, trail=0, fh=(-7, 18), nh=(9, 22), head=0, spark=False),
    "walk": dict(lean=-12, trail=7, fh=(-9, 17), nh=(8, 20), head=6, spark=False, hs=0, dy=0),
    "walk2": dict(lean=-9, trail=10, fh=(-10, 15), nh=(7, 18), head=3, spark=False, hs=2, dy=1.2),
    "walk3": dict(lean=-11, trail=12, fh=(-8, 18), nh=(9, 21), head=5, spark=False, hs=3.5, dy=0.3),
    "walk4": dict(lean=-8, trail=9, fh=(-9.5, 16), nh=(8, 19), head=2, spark=False, hs=1.5, dy=-0.8),
    "windup": dict(lean=7, trail=-2, fh=(-6, 22), nh=(-3, 35), head=-5, spark=False),
    "attack": dict(lean=-4, trail=3, fh=(-8, 20), nh=(10, 36), head=8, spark=True),
}


def _glowshape(pts, g, line=WISP_LINE, w=LINE*0.9):
    fill(pts, g); stroke(pts, w, closed=True, g=line)


def bludicka(pose):
    base, v = view_of(pose)
    if v: return _blud_fb(base, v == "b")
    q = BLP[base]
    tr = q["trail"]; hs = q.get("hs", 0)
    glow(0, 22, 26, WISP_GLOW, 0.12, 5, 30)
    with T(0, q.get("dy", 0), 1, rot=q["lean"]):
        a, e, h = ik((-1.5, 27), q["fh"], 7, 7, -1)
        tube([a, e, h], 2.2, 1.6, WISP, lw=LINE*0.7, sh=0)
        body = bez((-3, 29), (-6, 22), (-8, 14), (-9 - tr*0.4, 6)) + \
               [(-6 - tr*0.6, 8), (-6.5 - tr, 1), (-3.5 - tr*0.8, 5), (-3 - tr*1.6, -6), (-0.5 - tr*1.1, 3), (1.5 - tr*0.7, -2),
                (3 - tr*0.5, 5), (6 - tr*0.4, 1), (7.5 - tr*0.2, 7)] + bez((7.5 - tr*0.2, 7), (7, 14), (5, 22), (3, 29))
        _glowshape(body, WISP)
        clipped(body, lambda: fill(ell(0, 18, 3.5, 9, 18), WISP_L))
        for x in (-4, 0, 3.5):
            stroke(bez((x*0.4, 26), (x*0.8, 18), (x - tr*0.3, 12), (x*1.2 - tr*0.6, 4)), LINE*0.45, g=WISP_LINE)
        with T(0.5, 33, 1, rot=q["head"]):
            hair = bez((-3, 2), (-6, 4), (-7 - hs*0.4, 9 - hs*0.6), (-10 - hs, 13 - hs*1.2)) + \
                   bez((-10 - hs, 13 - hs*1.2), (-6, 11), (-4, 12), (-1.5, 15)) + \
                   bez((-1.5, 15), (-1, 12), (1, 10), (3.6, 3))
            _glowshape(hair, WISP_GLOW)
            hd = ell(0.5, 1.5, 3.4, 4.0, 22)
            _glowshape(hd, WISP_L)
            fill(ell(2.0, 2.0, 0.9, 0.6, 10), WISP_LINE)
            stroke(bez((1, -0.6), (1.8, -1.2), (2.6, -1.1), (3.2, -0.5)), LINE*0.5, g=WISP_LINE)
        a, e, h = ik((1.5, 27), q["nh"], 7, 7, -1)
        tube([a, e, h], 2.4, 1.8, WISP_L, lw=LINE*0.7, sh=0)
        if q["spark"]:
            glow(h[0]+1, h[1]+2, 9, FLAME_L, 0.3, 4)
            for k in range(8):
                aa = math.radians(k*45)
                stroke([(h[0]+1+math.cos(aa)*2.5, h[1]+2+math.sin(aa)*2.5), (h[0]+1+math.cos(aa)*(6 if k % 2 else 4), h[1]+2+math.sin(aa)*(6 if k % 2 else 4))],
                       LINE*0.7, g=FLAME)
            dot(h[0]+1, h[1]+2, 2.2, WHITE)
        else:
            dot(h[0]+0.6, h[1], 1.1, WISP_L)


FIRE_CORE = Col(0.45, "#6b4a3c")

OMP = {
    "idle": dict(s=1.0, hop=0, arms=(-40, 220), lean=0, burst=False),
    "walk": dict(s=1.0, hop=1, arms=(-125, 305), lean=-14, burst=False, dy=(1.2, 0), hx=(-3.5, 3.5), fc=(-6.5, 8.5), flick=2),
    "walk2": dict(s=1.0, hop=4, arms=(-85, 265), lean=-11, burst=False, dy=(5.5, 0), hx=(0, 0), fc=(2, 1), flick=3.5),
    "walk3": dict(s=1.0, hop=1, arms=(-50, 230), lean=-14, burst=False, dy=(0, 1.2), hx=(3.5, -3.5), fc=(8.5, -6.5), flick=2),
    "walk4": dict(s=1.0, hop=4, arms=(-95, 275), lean=-11, burst=False, dy=(0, 5.5), hx=(0, 0), fc=(1, 2), flick=3.5),
    "windup": dict(s=0.9, hop=0, arms=(35, 145), lean=6, burst=False),
    "attack": dict(s=1.25, hop=1, arms=(30, 150), lean=0, burst=True),
}


def _flame_tips(pts, flick):
    return [(x - flick*max(0, y-18)/10, y) for x, y in pts]


def ohnivy_muzik(pose):
    base, v = view_of(pose)
    if v: return _ohn_fb(base, v == "b")
    q = OMP[base]
    s = q["s"]; hop = q["hop"]; fk = q.get("flick", 0)
    if q["burst"]:
        glow(0, 20, 28, EMBER, 0.14, 5, 20)
        for k in range(12):
            aa = math.radians(k*30+8)
            if math.sin(aa) < -0.45: continue
            r0, r1 = 17, 24 + (k % 3)*2
            stroke([(math.cos(aa)*r0, 18+math.sin(aa)*r0), (math.cos(aa)*r1, 18+math.sin(aa)*r1)], LINE*0.8, g=FLAME, alpha=0.8)
    else:
        glow(0, 16, 20, EMBER, 0.12, 4)
    for x, dy, c in zip(q.get("hx", (-3, 3)), q.get("dy", (hop, 0)), q.get("fc", (-1, 5))):
        tube([(x, 9+hop), (c-1, 2.5+dy*0.6)], 3, 2.6, FIRE_CORE, lw=LINE*0.8, sh=0)
        shape(ell(c, 1.4+dy*0.6, 2.6, 1.4, 12), FIRE_CORE, LINE*0.7)
    with T(0, 8+hop, s, rot=q["lean"]):
        for side, a in ((-1, q["arms"][1]), (1, q["arms"][0])):
            sx = side*5
            aa = math.radians(a)
            hx, hy = sx+math.cos(aa)*9, 10+math.sin(aa)*9
            tube([(sx, 10), ((sx+hx)/2, (10+hy)/2+1), (hx, hy)], 3, 2, EMBER, lw=LINE*0.7, sh=0)
            for k in range(3):
                b = aa + (k-1)*0.5
                stroke([(hx, hy), (hx+math.cos(b)*2.4, hy+math.sin(b)*2.4)], LINE*0.6)
        fl = bez((-7, 2), (-10, 10), (-8, 18), (-5, 22)) + [(-6, 26), (-3, 23), (-2, 30), (0.5, 24), (3, 31), (4, 23), (7, 26), (6, 20)] + \
             bez((6, 20), (9, 14), (9, 6), (6, 0)) + bez((6, 0), (2, -2.5), (-3, -2.5), (-7, 2))
        form(_flame_tips(fl, fk), EMBER, sh=0.12)
        inner = bez((-4.5, 3), (-6, 10), (-4, 17), (-1, 20)) + [(0.5, 25), (2, 19)] + bez((2, 19), (5, 14), (5.5, 7), (3.5, 2)) + [(-4.5, 3)]
        fill(_flame_tips(inner, fk*0.7), FLAME)
        fill(ell(0, 9, 3.6, 5, 16), FLAME_L)
        for x in (-1.6, 2.4):
            fill(ell(x, 12, 1.1, 1.5, 12), FIRE_CORE)
            dot(x+0.3, 12.4, 0.45, WHITE)
            stroke([(x-1.6, 15.2 + (0.8 if x < 0 else -0.8)*0.0 + (1.0 if x < 0 else 0)), (x+1.4, 14.2 + (0 if x < 0 else 1.0))], LINE*0.8, g=FIRE_CORE)
        m = bez((-2.5, 7.5), (-1, 4.8 - (1.5 if q["burst"] else 0)), (2, 4.5 - (1.5 if q["burst"] else 0)), (4, 7.2)) + [(1, 6.6)]
        shape(m, FIRE_CORE, LINE*0.6)
        if q["burst"]:
            for p in ((-5, 6), (5, 14), (-3, 18)):
                stroke([p, (p[0]+1.5, p[1]-2), (p[0]+0.5, p[1]-4)], LINE*0.8, g=WHITE)


MURA_WING = Col(0.45, "#7d6c78")
MURA_WING_L = Col(0.62, "#b49a86")
MURA_WING_D = Col(0.36, "#62546a")
MURA_RAG = Col(0.42, "#6a6070")
MURA_SKIN = Col(0.6, "#a59a96")
MURA_SKIN_D = Col(0.5, "#88807e")
MURA_HAIR = Col(0.7, "#bcb7b0")

MRP = {
    "idle": dict(lean=-10, w1=0, w2=0, fh=(14, 6), nh=(18, 10), head=-6, legs=0),
    "walk": dict(lean=-16, w1=-26, w2=-14, fh=(12, 4), nh=(16, 6), head=-2, legs=4),
    "walk2": dict(lean=-15, w1=-6, w2=-4, fh=(12, 5), nh=(16, 7), head=-3, legs=2, dy=1.5),
    "walk3": dict(lean=-13, w1=18, w2=8, fh=(13, 6), nh=(17, 8), head=-4, legs=-2),
    "walk4": dict(lean=-14, w1=2, w2=0, fh=(13, 5), nh=(17, 7), head=-3, legs=1, dy=-1.5),
    "windup": dict(lean=-2, w1=32, w2=24, fh=(14, 24), nh=(21, 23), head=4, legs=2),
    "attack": dict(lean=-30, w1=14, w2=10, fh=(30, 18), nh=(34, 10), head=20, legs=8),
}


def _moth_wing(ang, L, W, g, gl, lower=False):
    with T(0, 0, 1, rot=ang):
        if lower:
            w = bez((0, 0), (L*0.3, W*0.7), (L*0.8, W*0.6), (L, 0)) + bez((L, 0), (L*0.8, -W*0.4), (L*0.3, -W*0.3), (0, 0))
        else:
            w = bez((0, 0), (L*0.2, W), (L*0.75, W*1.2), (L, W*0.5)) + bez((L, W*0.5), (L*1.05, 0), (L*0.6, -W*0.5), (0, 0))
        w = notch(w, 0.7, 4)
        form(w, g, sh=0.16)
        clipped(w, lambda: fill(ell(L*0.62, W*0.3, L*0.28, W*0.45, 20), gl))
        ex, ey = (L*0.62, W*0.3) if not lower else (L*0.65, W*0.08)
        r = W*0.22 if not lower else W*0.2
        shape(ell(ex, ey, r*1.4, r*1.4, 20), Col(0.4, "#5a4a5c"), LINE*0.6)
        fill(ell(ex, ey, r*0.9, r*0.9, 18), Col(0.8, "#d8c27a"))
        dot(ex, ey, r*0.45, SOCKET)
        for k in range(4):
            t = 0.25+k*0.18
            stroke([(L*0.08, 0), (L*t*1.2, W*(0.9-k*0.35))], LINE*0.4)


def mura(pose):
    base, v = view_of(pose)
    if v: return _mura_fb(base, v == "b")
    q = MRP[base]
    with T(0, q.get("dy", 0)):
        _mura_side(q)


def _mura_side(q):
    lean = q["lean"]
    with T(-3, 31, 1, rot=lean):
        _moth_wing(214 - q["w2"], 26, 12, MURA_WING_D, MURA_WING, True)
        _moth_wing(134 - q["w1"], 38, 16, MURA_WING_D, MURA_WING)
        _moth_wing(194 - q["w2"], 28, 13, MURA_WING, MURA_WING_L, True)
        _moth_wing(106 - q["w1"], 42, 17, MURA_WING, MURA_WING_L)
    with T(0, 18, 1, rot=lean):
        lg = q["legs"]
        for x, d in ((-2, 0), (2, lg)):
            tube(bez((x, 0), (x-1, -6), (x-4-d*0.3, -9), (x-6-d*0.6, -12+d*0.2)), 2.4, 1.2, MURA_SKIN_D, lw=LINE*0.7, sh=0)
        a, e, h = limb((0, 22), q["fh"], 11, 11, 2.8, 2.2, MURA_SKIN_D, -1)
        _hag_claw(h, e, MURA_SKIN_D)
        rag = bez((-6, 25), (-9, 16), (-10, 8), (-9, -2)) + [(-7, 1), (-6, -5), (-3, 0), (-1, -6), (1, -1), (3, -5), (5, 0)] + \
              bez((5, 0), (7, 8), (8, 16), (6, 25)) + bez((6, 25), (3, 28), (-3, 28), (-6, 25))
        form(rag, MURA_RAG, sdx=-2.5, sdy=1, sh=0.16)
        for x in (-5, -1, 3):
            stroke(bez((x, 24), (x-1, 16), (x+0.5, 8), (x-0.5, 1)), LINE*0.45)
        with T(3, 29, 1, rot=q["head"]):
            _hag_head()
        a, e, h = limb((2, 22), q["nh"], 11, 11, 3.0, 2.4, MURA_SKIN, -1)
        _hag_claw(h, e, MURA_SKIN)


def _hag_claw(h, e, g):
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    shape(ell(h[0], h[1], 1.6, 1.4, 12), g, LINE*0.6)
    for i in range(4):
        aa = math.radians(ang+(i-1.5)*18)
        p1 = (h[0]+math.cos(aa)*4.2, h[1]+math.sin(aa)*4.2)
        stroke([h, p1, (p1[0]+math.cos(aa-0.8)*1.6, p1[1]+math.sin(aa-0.8)*1.6)], LINE*0.7)


def _hag_head():
    hair = shaggy(bez((-2, 6), (-8, 6), (-11, -4), (-13, -12)) + [(-9, -9), (-8, -14), (-5, -6), (-3, -2)], 1.2, 3)
    form(hair, MURA_HAIR, sh=0.14)
    hd = bez((-2.5, -5.5), (-6.5, -4), (-6, 5.5), (0, 6.5)) + bez((0, 6.5), (4.5, 6.5), (6, 3), (6, 0.5)) + \
         bez((6, 0.5), (9, -1.5), (9, -4.5), (7, -5.5)) + bez((7, -5.5), (5, -4.5), (4, -6.8), (-2.5, -5.5))
    form(hd, MURA_SKIN, sh=0.15)
    fill(ell(3.2, 1.6, 1.9, 1.5, 12), SOCKET)
    eye(3.4, 1.5, 0.9, EYE_Y, 2.4)
    stroke(bez((0, 4.6), (2, 4.0), (4, 3.6), (5.5, 3.8)), LINE*0.6)
    m = bez((3.4, -3.6), (4.4, -4.6), (6, -4.4), (6.4, -3.5)) + [(5, -3.2)]
    shape(m, MOUTH_D, LINE*0.5)
    top = bez((-6.2, -1), (-7, 6), (-2, 8.5), (2, 7.5)) + bez((2, 7.5), (5, 7), (6.2, 4), (5.5, 2.5)) + [(2, 4.5), (-1, 3), (-4, -2)]
    form(top, MURA_HAIR, sh=0.1)
    for sgn in (0, 1):
        x0 = 1+sgn*2
        stroke(bez((x0, 7.5), (x0+1, 11), (x0+4, 13), (x0+7, 12)), LINE*0.6)
        for k in range(4):
            px, py = x0+1+k*1.5, 9.5+k*0.8
            stroke([(px, py), (px+0.6, py+1.4)], LINE*0.4)


SACKV = Col(0.42, "#655a74")
SACKV_D = Col(0.33, "#4f4660")
SHADE = Col(0.3, "#4a4258")
ROPE = Col(0.6, "#9a8a6a")

BBP = {
    "idle": dict(tilt=0, sq=1.0, open=0, reach=0, ff=(-7, 0), nf=(7, 0)),
    "walk": dict(tilt=-8, sq=0.94, open=0.25, reach=0, ff=(-11, 2), nf=(10, 0), tuft=1.5),
    "walk2": dict(tilt=-5, sq=0.98, open=0.1, reach=0, ff=(-2, 4), nf=(2, 0), tuft=3),
    "walk3": dict(tilt=-7, sq=0.94, open=0.25, reach=0, ff=(7, 0), nf=(-10, 2), tuft=1.5),
    "walk4": dict(tilt=-4, sq=0.98, open=0.1, reach=0, ff=(-3, 0), nf=(1, 4), tuft=3),
    "windup": dict(tilt=9, sq=0.92, open=0.6, reach=0, ff=(-9, 0), nf=(8, 0)),
    "attack": dict(tilt=-18, sq=1.05, open=1.0, reach=1, ff=(-14, 0), nf=(10, 0)),
}


def bubak(pose):
    base, v = view_of(pose)
    if v: return _bubak_fb(base, v == "b")
    q = BBP[base]
    for f, g in ((q["ff"], SHADE), (q["nf"], SACKV_D)):
        tube(bez((f[0]*0.5, 14), (f[0]*0.8, 9), (f[0], 6), (f[0], f[1]+2.5)), 5, 4, g, sh=0)
        shape(ell(f[0]+2.5, f[1]+1.5, 4.5, 2.0, 14), g, LINE*0.8)
    with T(0, 8, 1, rot=q["tilt"]):
        sq = q["sq"]; op = q["open"]
        if q["reach"]:
            for (sx, sy, ex, ey, g) in ((4, 30, 34, 40, SHADE), (6, 22, 37, 25, SACKV_D)):
                tube(bez((sx, sy), (sx+14, sy+8), (ex-12, ey+4), (ex, ey)), 4.5, 2, g, sh=0)
                claws(ex, ey, -10 if ey < 30 else 10, 4, 4.0, 20, Col(0.55, "#8a7e9a"), LINE*0.9)
        sack = bez((-14, 4), (-22, 14), (-22*sq, 36), (-12, 46)) + bez((-12, 46), (-8, 50), (-4, 52), (0, 52)) + \
               bez((0, 52), (6, 52), (14, 48), (17, 40)) + bez((17, 40), (23, 30), (22, 12), (14, 2)) + bez((14, 2), (6, -3), (-6, -3), (-14, 4))
        sack = notch(sack, 0.6, 7)
        form(sack, SACKV, sdx=-4, sdy=2, sh=0.2)
        pt = [(-16, 12), (-6, 10.5), (-5.5, 19), (-15, 20.5)]
        form(pt, SACKV_D, sh=0)
        for i in range(5):
            x = -15.5 + i*2.3
            stroke([(x, 12.6 - i*0.3), (x+1.2, 11.0 - i*0.3)], LINE*0.45, g=ROPE)
        for x in (-6, 2, 10):
            stroke(bez((x, 48), (x+2, 36), (x-1, 22), (x+1, 4)), LINE*0.45, g=SACKV_D)
        up = bez((-1, 29), (6, 30 + op*9), (15, 30 + op*9), (22, 27 + op*3))
        lo = bez((22, 27 + op*3), (15, 28 - op*9), (6, 28 - op*9), (-1, 29))
        mo = up + lo[1:]
        shape(mo, SOCKET if op > 0.05 else SACKV_D, LINE*0.8)
        for i in range(1, 9):
            p = up[i*2]; q_ = lo[16 - i*2]
            fill([(p[0]-0.9, p[1]+0.2), (p[0]+0.9, p[1]+0.2), (p[0], p[1]-1.6-op*1.4)], TOOTH)
            if op > 0.05:
                fill([(q_[0]-0.9, q_[1]-0.2), (q_[0]+0.9, q_[1]-0.2), (q_[0], q_[1]+1.6+op*1.2)], TOOTH)
        if op > 0.5:
            for (ex, ey, r) in ((6, 29, 1.2), (11, 31, 0.9), (16, 28, 1.1)):
                eye(ex, ey, r, EYE_R, 2.2)
        neck = bez((-6, 48), (-6, 52), (-4, 54), (-1, 54)) + bez((-1, 54), (3, 54), (6, 52), (6, 48))
        stroke([(-7, 49), (7, 49.5)], LINE*2.4, g=ROPE); stroke([(-7, 49), (7, 49.5)], LINE*0.5)
        tf = q.get("tuft", 0)
        top = [(-5, 50), (-9 - tf, 58 - tf*0.4), (-5, 55), (-3 - tf*0.8, 61), (-0.5, 55.5), (2 - tf*0.6, 60), (3, 55), (7 - tf*0.5, 58), (5.5, 50)]
        form(top, SACKV, sh=0.12)
        stroke([(5, 49.5), (8 - tf*0.5, 44), (7 - tf, 40)], LINE*1.6, g=ROPE)
        eyes = ((5, 41, 2.0, EYE_Y), (12, 40, 1.6, EYE_Y), (-5, 38, 1.4, EYE_G), (9, 18, 1.3, EYE_Y), (-1, 46, 1.1, EYE_Y), (16, 34.5 + op*4, 1.1, EYE_G))
        for i, (ex, ey, r, c) in enumerate(eyes):
            fill(ell(ex, ey, r*1.6, r*1.25, 14), SOCKET)
            eye(ex, ey, r, c, 2.2)
            stroke(bez((ex-r*1.7, ey+r*0.5), (ex-r, ey+r*1.3), (ex+r, ey+r*1.3), (ex+r*1.7, ey+r*0.4)), LINE*0.5)


ROBE_G = Col(0.38, "#5f5c6e")
ROBE_D = Col(0.3, "#4c4a5a")
GOURD = Col(0.55, "#c47a32")
GOURD_D = Col(0.45, "#9a5a26")
GHOST = Col(0.68, "#a8acb4")

SVP = {
    "idle": dict(lean=-4, fh=(10, 14), nh=(14, 18), sway=0, head=-4, blaze=False),
    "walk": dict(lean=-12, fh=(6, 12), nh=(16, 20), sway=6, head=0, blaze=False),
    "walk2": dict(lean=-10, fh=(11, 16), nh=(11, 16), sway=3, head=-1, blaze=False, dy=1.2),
    "walk3": dict(lean=-9, fh=(16, 20), nh=(6, 12), sway=-1, head=-2, blaze=False),
    "walk4": dict(lean=-11, fh=(11, 16), nh=(11, 16), sway=3.5, head=-1, blaze=False, dy=-1),
    "windup": dict(lean=5, fh=(4, 20), nh=(8, 25), sway=8, head=-8, blaze=False),
    "attack": dict(lean=-16, fh=(32, 30), nh=(34, 22), sway=4, head=8, blaze=True),
}


def svetlonos(pose):
    base, v = view_of(pose)
    if v: return _svet_fb(base, v == "b")
    q = SVP[base]
    with T(0, q.get("dy", 0)):
        _svet_side(q)


def _svet_side(q):
    lean, sw = q["lean"], q["sway"]
    hp = world((0, 4), lean, (5, 64))
    glow(hp[0], hp[1], 28 if q["blaze"] else 20, FLAME, 0.12, 5)
    with T(0, 4, 1, rot=lean):
        a, e, h = limb((-1, 50), q["fh"], 17, 17, 3.6, 2.6, Col(0.55, "#8a8e96"), -1)
        _long_fingers(h, e, Col(0.55, "#8a8e96"))
        robe = bez((-7, 54), (-14, 44), (-16 - sw*0.3, 24), (-19 - sw, 4)) + \
               [(-16 - sw, 7), (-15 - sw*0.9, -2), (-11 - sw*0.7, 5), (-9 - sw*0.6, -4), (-6 - sw*0.4, 4), (-3 - sw*0.3, -3), (0, 5),
                (3, -1), (5, 6), (8, 0), (9, 7)] + bez((9, 7), (11, 22), (12, 40), (8, 54)) + bez((8, 54), (4, 58), (-3, 58), (-7, 54))
        form(robe, ROBE_G, sdx=-4, sdy=1.5, sh=0.18)
        for x in (-10, -5, 0, 5):
            stroke(bez((x*0.5, 54), (x*0.8, 40), (x - sw*0.2, 24), (x*1.1 - sw*0.6, 6)), LINE*0.45, g=ROBE_D)
        hood = bez((-8, 52), (-12, 60), (-6, 70), (2, 70)) + bez((2, 70), (8, 70), (12, 64), (10, 54)) + [(4, 56), (-3, 56)]
        form(hood, ROBE_D, sh=0.12)
        with T(5, 62, 1.0 if not q["blaze"] else 1.12, rot=q["head"]):
            _lantern_head(q["blaze"])
        a, e, h = limb((3, 50), q["nh"], 17, 17, 4.0, 3.0, GHOST, -1)
        sl = ribbon([(3, 50), ((3+e[0])/2, (50+e[1])/2), e], 7, 6)
        form(sl, ROBE_G, sh=0.1)
        _long_fingers(h, e, GHOST)
    if q["blaze"]:
        for k in range(5):
            aa = math.radians(-30+k*20)
            stroke([(hp[0]+math.cos(aa)*14, hp[1]+math.sin(aa)*14), (hp[0]+math.cos(aa)*22, hp[1]+math.sin(aa)*22)], LINE*0.9, g=FLAME_L, alpha=0.8)


def _long_fingers(h, e, g):
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    shape(ell(h[0], h[1], 2.0, 1.6, 12), g, LINE*0.6)
    for i in range(4):
        aa = math.radians(ang+(i-1.5)*14)
        p1 = (h[0]+math.cos(aa)*5.5, h[1]+math.sin(aa)*5.5)
        stroke([h, p1, (p1[0]+math.cos(aa-0.6)*2.2, p1[1]+math.sin(aa-0.6)*2.2)], LINE*0.8)


def _lantern_head(blaze):
    for k, (x, rx) in enumerate(((-4.5, 4.5), (4.5, 4.5), (0, 5.5))):
        lobe = ell(x, 0, rx, 8, 24)
        form(lobe, GOURD if k == 2 else GOURD_D, sh=0.14)
    stroke(ell(0, 0, 9, 8, 30, 100, 260), LINE*0.5)
    stem = [(-1, 7), (1.5, 7), (3, 11), (1.5, 11.5)]
    form(stem, MOSS_D, sh=0)
    col = FLAME_L if blaze else FLAME
    for ex in (-3.5, 3.5):
        tri = [(ex-2.2, 0.5), (ex+2.2, 0.5), (ex+0.3, 4.2 if ex > 0 else 3.6)]
        shape(tri, col, LINE*0.6)
    shape([(-1, -1.5), (1.2, -1.5), (0, 0.6)], col, LINE*0.5)
    k = 1.6 if blaze else 1.0
    mo = [(-6, -3.5), (-4, -4.5 - k), (-2.5, -3.6), (-1, -4.8 - k), (1, -3.6), (2.5, -4.8 - k), (4, -3.6), (6, -3.4),
          (4.5, -5.5 - k*1.4), (2, -6.4 - k*1.5), (-2, -6.4 - k*1.5), (-4.5, -5.5 - k*1.4)]
    shape(mo, col, LINE*0.6)
    glow(0, 0, 7, FLAME_L, 0.18, 3)


PITCH = Col(0.3, "#565144")
PITCH_D = Col(0.26, "#48443a")
PITCH_L = Col(0.55, "#8e8a72")
SMOL = Col(0.8, "#9cf266")

SMP = {
    "idle": dict(hip=(-2, 32), lean=-10, ff=(-10, 2), nf=(9, 2), fh=(16, -10), nh=(22, -8), head=-4, smash=False),
    "walk": dict(hip=(-2, 30.5), lean=-16, ff=(-13, 3.5), nf=(11, 2), fh=(28, -4), nh=(8, -10), head=0, smash=False),
    "walk2": dict(hip=(-2, 32.5), lean=-13, ff=(-1, 9), nf=(1, 2), fh=(19, -8), nh=(17, -9), head=-3, smash=False),
    "walk3": dict(hip=(-2, 30.5), lean=-16, ff=(11, 2), nf=(-13, 3.5), fh=(8, -10), nh=(28, -4), head=0, smash=False),
    "walk4": dict(hip=(-2, 32.5), lean=-13, ff=(1, 2), nf=(-1, 9), fh=(17, -9), nh=(19, -8), head=-3, smash=False),
    "windup": dict(hip=(-1, 28), lean=-26, ff=(-14, 2), nf=(11, 2), fh=(-6, -4), nh=(-2, -2), head=-10, smash=False),
    "attack": dict(hip=(-4, 33), lean=6, ff=(-16, 2), nf=(12, 2), fh=(10, 66), nh=(20, 64), head=10, smash=True),
}


def smolak(pose):
    base, v = view_of(pose)
    if v: return _smolak_fb(base, v == "b")
    q = SMP[base]
    hip, lean = q["hip"], q["lean"]
    fill(ell(6, FEET*0+1.2, 26, 3.4, 30), Col(0.3, "#3e4a2c"), 0.55)
    glow(6, 1.2, 18, SMOL, 0.06, 3, 2.6)

    def arm(sh, hand, g, w):
        a, e, h = ik(sh, hand, 20, 19, -1)
        o = ribbon(chaikin([a, e, h]), w, w*0.85, w*1.1)
        form(o, g, sh=0.16)
        shape(notch(ell(h[0], h[1], 7, 6.5, 22), 0.8, 4), g, LINE*0.9)
        for d in (-2.5, 0, 2.5):
            stroke([(h[0]+2, h[1]+d), (h[0]+6, h[1]+d*1.2)], LINE*0.5)
        return h

    def leg(j, f, g):
        a, k, w = ik(j, (f[0], f[1]+4), 15, 14, 1)
        o = ribbon(chaikin([a, k, w]), 15, 13, 15)
        form(o, g, sh=0.16)
        shape(bez((w[0]-7, w[1]+2), (w[0]-8, w[1]-4.5), (w[0]+6, w[1]-4.6), (w[0]+9, w[1]-3)) + [(w[0]+7, w[1]+3)], g, LINE*0.9)

    with T(hip[0], hip[1], 1, rot=lean):
        fh = arm((-2, 34), q["fh"], PITCH_D, 13)
    leg((hip[0]-4, hip[1]), q["ff"], PITCH_D)
    with T(hip[0], hip[1], 1, rot=lean):
        body = bez((-12, -6), (-20, 8), (-20, 30), (-10, 42)) + bez((-10, 42), (-2, 48), (14, 48), (20, 38)) + \
               bez((20, 38), (25, 26), (22, 6), (14, -6)) + [(10, -9), (8, -5), (4, -11), (1, -6), (-3, -10), (-6, -5), (-9, -9)]
        form(body, PITCH, sdx=-4, sdy=2, sh=0.2)

        def veins():
            for pts in ([(-6, 34), (-2, 26), (-5, 18), (0, 10)], [(10, 40), (8, 30), (13, 22), (11, 12)], [(-14, 14), (-9, 8), (-12, 0)]):
                stroke(pts, LINE*2.4, g=SMOL, alpha=0.35)
                stroke(pts, LINE*0.9, g=SMOL)
            for x, y, r in ((-12, 34, 3.5), (4, 40, 2.6), (16, 30, 3), (-16, 20, 2.2)):
                fill(ell(x, y, r, r*0.6, 14, rot=20), PITCH_L, 0.55)
        clipped(body, veins)
        for x, l in ((-4, 6), (5, 9), (12, 5)):
            tube([(x, -8), (x+0.3, -8-l)], 2.6, 1.2, PITCH, lw=LINE*0.6, sh=0)
            dot(x+0.3, -9-l-1.2, 1.1, PITCH)
    leg((hip[0]+4, hip[1]), q["nf"], PITCH)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(10, 46, 1, rot=q["head"]):
            hd = bez((-7, -3), (-9, 5), (-3, 10), (3, 9)) + bez((3, 9), (8, 8.5), (10, 3), (9, -3)) + [(2, -5), (-4, -5)]
            form(hd, PITCH, sh=0.18)
            for ex in (2.5, 7):
                fill(ell(ex, 2.5, 1.9, 1.3, 12), SOCKET)
                eye(ex, 2.4, 1.0, SMOL, 2.6)
            mo = [(1, -1.5), (8.5, -1.0), (6, -3.2), (3, -3.0)] if not q["smash"] else [(0.5, -0.5), (9, -0.3), (7, -4.5), (2.5, -4.2)]
            shape(mo, SOCKET, LINE*0.6)
            glow(4.8, -1.5, 3, SMOL, 0.2, 2)
        nh = arm((6, 34), q["nh"], PITCH, 14)
    if q["smash"]:
        for k in range(3):
            stroke([(14+k*5, 108-k), (18+k*5, 116-k)], LINE*0.9, g=WHITE, alpha=0.6)
    for p in ((-14, 10), (18, 14)):
        drip(p[0], p[1], 1.0, PITCH_L)


BES = Col(0.5, "#7e7189")
BES_D = Col(0.4, "#655a73")
BES_L = Col(0.66, "#a395ad")
CURSE = Col(0.7, "#c27cff")

BSP = {
    "idle": dict(hip=(-2, 44), lean=-14, ff=(-9, 2), nf=(8, 2), fh=(18, 14), nh=(22, 16), head=-6, cast=0),
    "walk": dict(hip=(-2, 42.5), lean=-22, ff=(-13, 3.5), nf=(11, 2), fh=(26, 18), nh=(10, 8), head=0, cast=0, tail=2),
    "walk2": dict(hip=(-2, 45), lean=-19, ff=(-1, 8), nf=(1, 2), fh=(18, 13), nh=(18, 13), head=-3, cast=0, tail=-1),
    "walk3": dict(hip=(-2, 42.5), lean=-22, ff=(11, 2), nf=(-13, 3.5), fh=(10, 8), nh=(26, 18), head=0, cast=0, tail=-3),
    "walk4": dict(hip=(-2, 45), lean=-19, ff=(1, 2), nf=(-1, 8), fh=(18, 13), nh=(18, 13), head=-3, cast=0, tail=1),
    "windup": dict(hip=(-1, 44), lean=-2, ff=(-12, 2), nf=(9, 2), fh=(-10, 40), nh=(-6, 45), head=4, cast=0),
    "attack": dict(hip=(-6, 44), lean=-6, ff=(-16, 2), nf=(10, 2), fh=(26, 46), nh=(32, 38), head=12, cast=1),
}


def bes(pose):
    base, v = view_of(pose)
    if v: return _bes_fb(base, v == "b")
    q = BSP[base]
    hip, lean = q["hip"], q["lean"]; tl = q.get("tail", 0)

    def leg(j, f, g):
        hock = (f[0]+j[0]-3, f[1]+9)
        a, k, h = ik(j, hock, 20, 17, 1)
        tube(chaikin([a, k, h]), 7, 3.2, g, sh=0.14)
        toe = (f[0]+j[0]+1, f[1]+2)
        tube([h, toe], 3.2, 2.8, g, sh=0)
        shape(ell(toe[0]+2, toe[1]-0.8, 3.6, 1.6, 14), g, LINE*0.8)
        claws(toe[0]+5, toe[1]-1, -15, 3, 2.0, 22, BONE_FAR, LINE*0.6)

    def arm(sh, hand, g):
        a, e, h = ik(sh, hand, 19, 18, -1)
        tube(chaikin([a, e, h]), 5, 3, g, sh=0.14)
        stroke([e, (e[0]+1, e[1]-2)], LINE*0.5)
        _long_fingers(h, e, g)
        return h

    with T(hip[0], hip[1], 1, rot=lean):
        tube(bez((-3, 0), (-14, -6 - tl*0.5), (-22, 2 + tl), (-26, -6 + tl*1.5)), 2.6, 1.0, BES_D, sh=0)
        shape([(x, y + tl*1.5) for x, y in ((-26, -6), (-29, -4), (-27.5, -9.5), (-24.5, -7.5))], BES_D, LINE*0.6)
        fh = arm((-1, 36), q["fh"], BES_D)
    leg((hip[0]-2, hip[1]), q["ff"], BES_D)
    with T(hip[0], hip[1], 1, rot=lean):
        body = bez((-6, -3), (-9, 10), (-9, 26), (-6, 36)) + bez((-6, 36), (-2, 41), (6, 41), (10, 36)) + \
               bez((10, 36), (12, 30), (9, 22), (5, 16)) + bez((5, 16), (6, 8), (6, 2), (5, -3))
        form(body, BES, sdx=-3, sdy=1.2, sh=0.18)
        for i in range(4):
            y = 30 - i*3.6
            stroke(bez((-2, y+1), (2, y+0.5), (6, y-1), (8.5 - i*0.8, y-3)), LINE*0.55, g=BES_D)
        stroke(bez((-7, 34), (-8.5, 24), (-8, 14), (-6.5, 6)), LINE*0.5)
        lc = [(-7.5, 3), (7, 2)] + [(7, -6), (5, -14), (3, -7), (0, -16), (-2, -7), (-5, -13), (-7.5, -5)]
        form(lc, RAG_D, sh=0.16)
        shape(rrect(-8, 1, 15.5, 3, 1.2), LEATHER_D, LINE*0.7)
    leg((hip[0]+2, hip[1]), q["nf"], BES)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(5, 46, 1, rot=q["head"]):
            _bes_head()
        nh = arm((3, 36), q["nh"], BES)
        if q["cast"]:
            c = ((fh[0]+nh[0])/2+5, (fh[1]+nh[1])/2+2)
            glow(c[0], c[1], 13, CURSE, 0.22, 5)
            stroke(ell(c[0], c[1], 9, 9, 40), LINE*0.6, closed=True, g=CURSE)
            for k in range(6):
                aa = math.radians(k*60+10)
                px, py = c[0]+math.cos(aa)*9, c[1]+math.sin(aa)*9
                stroke([(px-1.2, py-1.2), (px+1.2, py+1.2)], LINE*0.6, g=CURSE)
                stroke([(px-1.2, py+1.2), (px+1.2, py-1.2)], LINE*0.6, g=CURSE)
            shape(ell(c[0], c[1], 3.6, 3.6, 20), Col(0.85, "#e8c4ff"), LINE*0.6)
            dot(c[0]+1, c[1]+1, 1.2, WHITE)
        else:
            c = (nh[0]+3, nh[1]+2)
            glow(c[0], c[1], 5, CURSE, 0.2, 3)
            for k in range(3):
                stroke(bez((c[0]-1+k, c[1]), (c[0]+k*1.5, c[1]+3), (c[0]-2+k, c[1]+5), (c[0]+k, c[1]+8)), LINE*0.5, g=CURSE, alpha=0.7)


def _bes_head():
    for hx, g, s in ((-3.5, BONE_FAR, 0.9), (0.5, Col(0.75, "#c2b394"), 1.0)):
        hn = bez((hx, 4), (hx-6*s, 10*s), (hx-14*s, 14*s), (hx-20*s, 10*s)) + bez((hx-20*s, 10*s), (hx-14*s, 11*s), (hx-7*s, 7*s), (hx+3, 3))
        form(hn, g, sh=0.14)
        for k in range(4):
            x = hx - 3 - k*3.5*s
            stroke([(x, 5+k*1.5*s), (x-0.6, 8+k*1.2*s)], LINE*0.4)
    hd = bez((-3, -7), (-7, -4), (-6.5, 5), (0, 6.5)) + bez((0, 6.5), (4, 6.5), (6, 3), (6.2, 0)) + \
         bez((6.2, 0), (8.6, -2.6), (8, -6), (5.5, -8.5)) + bez((5.5, -8.5), (3, -10), (-1, -9), (-3, -7))
    form(hd, BES, sh=0.16)
    stroke(bez((-1, -2), (1, -4.5), (3, -6), (5, -6.4)), LINE*0.5, g=BES_D)
    fill(ell(3.0, 1.0, 2.2, 1.5, 12), SOCKET)
    eye(3.4, 0.9, 1.0, EYE_V, 2.6)
    stroke([(0.5, 3.4), (6, 1.4)], LINE*0.9)
    m = bez((3.5, -4.4), (5, -5.8), (7, -5.6), (7.6, -4.2)) + [(5.5, -4.0)]
    shape(m, MOUTH_D, LINE*0.5)
    fill([(5, -4.4), (5.7, -4.4), (5.35, -5.4)], TOOTH)
    ear = [(-3.5, 1), (-9, -1), (-4, -2.5)]
    form(ear, BES_D, sh=0)


# ------------------------------------------------------------------ front (_f) / back (_b) views

WALK_I = {"walk": 0, "walk2": 1, "walk3": 2, "walk4": 3}
# (lift, scale) of the -x and +x leg: contact (+x forward), passing (-x swings), contact, passing
FB_STEP = (((1.6, 0.93), (-1.2, 1.07)), ((6, 1.0), (0, 1.0)), ((-1.2, 1.07), (1.6, 0.93)), ((0, 1.0), (6, 1.0)))
SWING = (1, 0, -1, 0)


def _step(base, k=1.0):
    i = WALK_I.get(base)
    if i is None: return ((0, 1), (0, 1))
    return tuple((l*k, 1+(s-1)*k) for l, s in FB_STEP[i])


def _swing(base):
    i = WALK_I.get(base)
    return 0 if i is None else SWING[i]


def _phase(base):
    i = WALK_I.get(base)
    return 0.6 if i is None else i*math.pi/2


def _sym(half):
    return half + [(-x, y) for x, y in reversed(half)]


def _sway(pts, amt, below, span=10):
    return [(x + amt*min(1, max(0, below - y)/span), y) for x, y in pts]


def _mirror(fn, *a):
    fn(1, *a)
    with T(0, 0, 1, flip=True):
        fn(-1, *a)


def _spark(x, y, r=1.0):
    glow(x, y, 9*r, FLAME_L, 0.3, 4)
    for k in range(8):
        aa = math.radians(k*45)
        l = (6 if k % 2 else 4)*r
        stroke([(x+math.cos(aa)*2.5*r, y+math.sin(aa)*2.5*r), (x+math.cos(aa)*l, y+math.sin(aa)*l)], LINE*0.7, g=FLAME)
    dot(x, y, 2.2*r, WHITE)


def _blud_fb(base, back):
    ph = _phase(base); walking = base in WALK_I
    sw = math.sin(ph)*2.4
    c = math.cos(ph)
    hands = {"windup": ((-7, 21), (4.5, 36)), "attack": ((-7, 19), None)}.get(
        base, ((-6.3 - sw*0.2, 14.5 + c*1.4), (6.3 - sw*0.2, 14.5 - c*1.4)))
    glow(0, 22, 26, WISP_GLOW, 0.12, 5, 30)
    if base == "attack" and back:
        _spark(5.5, 30)

    def arm(sh, h, bend):
        a, e, hh = ik(sh, h, 7, 7, bend)
        tube([a, e, hh], 2.3, 1.7, WISP_L, lw=LINE*0.7, sh=0)
        dot(hh[0], hh[1], 1.1, WISP_L)

    half = [(0, 30), (3, 29.5)] + bez((3, 29.5), (5.5, 22), (7.5, 14), (8.5, 6)) + \
           [(8.8, -1), (6.2, 4), (4.8, -5.5), (2.6, 3), (0, -7.5)]
    body = _sway(_sym(half), sw, 10, 16)
    _glowshape(body, WISP)
    clipped(body, lambda: fill(ell(0, 18, 3.8 if not back else 3, 9, 18), WISP_L))
    for x in (-4.5, 0, 4.5):
        stroke(bez((x*0.4, 26), (x*0.8, 18), (x + sw*0.3, 12), (x*1.15 + sw*0.7, 3)), LINE*0.45, g=WISP_LINE)
    arm((-3, 27), hands[0], -1)
    if hands[1]: arm((3, 27), hands[1], -1 if base == "windup" else 1)
    with T(0, 33, 1, rot=-6 if base == "windup" else 0):
        hb = [(0, 15.5), (1.6, 11.5), (3.4, 14), (4.2, 9.5)] + bez((4.2, 9.5), (5, 6), (4.6, 2), (3.4, -1)) + [(0, -1)]
        hb = [(x - sw*0.9*max(0, y - 5)/10, y) for x, y in _sym(hb)]
        if back:
            fill(ell(0, 1.5, 3.4, 4.0, 22), WISP_L)
            _glowshape(hb, WISP_GLOW)
            for x in (-2.4, 0, 2.4):
                stroke(bez((x*1.1, -0.5), (x*1.2, 3), (x - sw*0.2, 7), (x*0.8 - sw*0.6, 12)), LINE*0.4, g=WISP_LINE)
        else:
            _glowshape(hb, WISP_GLOW)
            _glowshape(ell(0, 1.5, 3.4, 4.0, 22), WISP_L)
            fill(bez((-3.4, 2.6), (-3, 6.6), (3, 6.6), (3.4, 2.6)) + [(1.6, 4.3), (0, 3.7), (-1.6, 4.3)], WISP_GLOW)
            for x in (-1.3, 1.3):
                fill(ell(x, 1.8, 0.65, 0.75, 10), WISP_LINE)
            stroke(bez((-1.1, -0.6), (-0.4, -1.2), (0.4, -1.2), (1.1, -0.6)), LINE*0.5, g=WISP_LINE)
    if base == "attack" and not back:
        tube([(3, 27), (5, 25), (4.5, 23.5)], 2.6, 2.2, WISP_L, lw=LINE*0.7, sh=0)
        _spark(4.5, 23.5, 1.15)
    elif base == "attack":
        arm((3, 27), (7, 31), 1)


def _ohn_fb(base, back):
    q = OMP[base]
    s, hop = q["s"], q["hop"]
    st = _step(base, 0.8); swg = _swing(base)
    fk = q.get("flick", 0)*0.6*(swg or (1 if base == "walk2" else -1 if base == "walk4" else 0))
    if q["burst"]:
        glow(0, 20, 28, EMBER, 0.14, 5, 20)
        for k in range(12):
            aa = math.radians(k*30+15)
            if math.sin(aa) < -0.45: continue
            r0, r1 = 17, 24 + (k % 3)*2
            stroke([(math.cos(aa)*r0, 18+math.sin(aa)*r0), (math.cos(aa)*r1, 18+math.sin(aa)*r1)], LINE*0.8, g=FLAME, alpha=0.8)
    else:
        glow(0, 16, 20, EMBER, 0.12, 4)
    for x, (lift, sc) in sorted(zip((-3, 3), st), key=lambda t: t[1][1]):
        tube([(x, 9+hop), (x*1.15, 2.5+lift)], 3*sc, 2.6*sc, FIRE_CORE, lw=LINE*0.8, sh=0)
        shape(ell(x*1.2, 1.5+lift, 2.3*sc, 1.5*sc, 12), FIRE_CORE, LINE*0.7)
    ang = {"windup": (40, 140), "attack": (18, 162)}.get(base, (-55 - 15*swg, 235 - 15*swg))
    with T(0, 8+hop, s):
        for sx, a in ((5, ang[0]), (-5, ang[1])):
            aa = math.radians(a)
            hx, hy = sx+math.cos(aa)*9, 10+math.sin(aa)*9
            tube([(sx, 10), ((sx+hx)/2, (10+hy)/2+1), (hx, hy)], 3, 2, EMBER, lw=LINE*0.7, sh=0)
            for k in range(3):
                b = aa + (k-1)*0.5
                stroke([(hx, hy), (hx+math.cos(b)*2.4, hy+math.sin(b)*2.4)], LINE*0.6)
        half = [(0, 31.5), (1.8, 25), (3.6, 29.5), (5.2, 23.5), (7.2, 26.5), (6.3, 20)] + \
               bez((6.3, 20), (9, 14), (9, 6), (6.5, 0.5)) + bez((6.5, 0.5), (3, -2.5), (1, -2.5), (0, -2.6))
        form(_flame_tips(_sym(half), fk), EMBER, sh=0.12, sdx=0)
        inner = [(0, 26)] + bez((0, 26), (2.5, 20), (5.2, 14), (5.2, 8)) + bez((5.2, 8), (5, 3), (2, 1.5), (0, 1.5))
        fill(_flame_tips(_sym(inner), fk*0.7), FLAME)
        if back:
            fill(ell(0, 10, 2.8, 6.5, 16), FLAME_L)
            for x in (-2.5, 0, 2.5):
                stroke(bez((x*0.6, 3), (x, 8), (x*1.2, 13), (x*0.8 - fk*0.4, 19)), LINE*0.5, g=EMBER, alpha=0.8)
            return
        fill(ell(0, 9, 3.6, 5, 16), FLAME_L)
        for x in (-2, 2):
            fill(ell(x, 12, 1.1, 1.5, 12), FIRE_CORE)
            dot(x+0.3, 12.4, 0.45, WHITE)
            stroke([(x*0.4, 14.2), (x*1.7, 15.3)], LINE*0.8, g=FIRE_CORE)
        b = 1.5 if q["burst"] else 0
        shape(bez((-2.6, 7.2), (-1.2, 4.8-b), (1.2, 4.8-b), (2.6, 7.2)) + [(0, 6.6)], FIRE_CORE, LINE*0.6)
        if q["burst"]:
            for p in ((-5, 6), (5, 14), (-3, 18)):
                stroke([p, (p[0]+1.5, p[1]-2), (p[0]+0.5, p[1]-4)], LINE*0.8, g=WHITE)


MRF = {"idle": 8, "walk": 24, "walk2": 5, "walk3": -16, "walk4": 2, "windup": 30, "attack": -10}


def _mura_fb(base, back):
    q = MRP[base]; w = MRF[base]
    ph = _phase(base); sw = math.sin(ph)*1.6
    with T(0, q.get("dy", 0)):
        def wings(sd):
            with T(2, 38):
                _moth_wing(-28 + w*0.6, 26, 12, MURA_WING_D if not back else MURA_WING, MURA_WING_L, True)
                _moth_wing(22 + w, 36, 15, MURA_WING, MURA_WING_L)
        if not back: _mirror(wings)
        hands = {"windup": ((-10, 34), (10, 34)), "attack": ((-6, 15), (6, 15))}.get(
            base, ((-4, 11 + math.cos(ph)), (4, 11 - math.cos(ph))))

        def arms():
            sc = 1.35 if base == "attack" else 1.0
            for sx, h, g in ((-1, hands[0], MURA_SKIN_D), (1, hands[1], MURA_SKIN)):
                a, e, hh = limb((sx*5.5, 22), h, 8, 8, 2.9, 2.3, g, -sx if base == "windup" else sx)
                if back and base != "windup": continue
                with T(hh[0], hh[1], sc):
                    _hag_claw((0, 0), (e[0]-hh[0], e[1]-hh[1]), g)

        with T(0, 18):
            for x in (-2, 2):
                d = sw*0.6 + q["legs"]*0.15*x
                tube(bez((x, 0), (x*1.1, -5), (x*1.5 + d*0.5, -8), (x*1.7 + d, -12)), 2.4, 1.2, MURA_SKIN_D, lw=LINE*0.7, sh=0)
            if back: arms()
            half = [(0, 28.5), (4, 28), (6.5, 25)] + bez((6.5, 25), (8.5, 16), (9.5, 8), (9, -2)) + \
                   [(7, 1), (5.5, -5), (3, 0), (1, -6), (0, -1)]
            rag = _sway(_sym(half), sw, 6)
            form(rag, MURA_RAG, sdx=0, sdy=1, sh=0.16)
            for x in (-5, -1.5, 1.5, 5):
                stroke(bez((x, 24), (x*1.1, 16), (x*1.2 + sw*0.3, 8), (x*1.2 + sw, 0)), LINE*0.45)
        if back: _mirror(wings)
        with T(0, 18):
            with T(0, 30, 1, rot=-sw*1.5):
                _hag_fb(back)
            if not back: arms()


def _hag_fb(back):
    hair = [(0, 7)] + bez((0, 7), (6, 7.5), (8.5, 2), (8, -4)) + [(9.5, -10), (6.5, -8), (5.5, -13), (3.5, -6)] + [(0, -4)]
    form(shaggy(_sym(hair), 1.1, 3), MURA_HAIR, sh=0.14, sdx=0)
    for sd in (-1, 1):
        x0 = sd*1.6
        stroke(bez((x0, 7), (x0+sd*1.5, 11), (x0+sd*5, 13.5), (x0+sd*8, 12.5)), LINE*0.6)
        for k in range(4):
            px, py = x0+sd*(1.5+k*1.6), 9.5+k*0.9
            stroke([(px, py), (px+sd*0.6, py+1.4)], LINE*0.4)
    if back:
        cap = [(0, 7.5)] + bez((0, 7.5), (5, 7.5), (6.5, 2), (5.5, -4)) + [(3, -6.5), (0, -5)]
        form(shaggy(_sym(cap), 1.0, 3), MURA_HAIR, sh=0.1, sdx=0)
        for x in (-3, 0, 3):
            stroke(bez((x*0.5, 6), (x*0.9, 2), (x*1.1, -2), (x*1.3, -6)), LINE*0.45)
        return
    hd = [(0, 6.5)] + bez((0, 6.5), (4, 6.5), (5.5, 3), (5, -1)) + bez((5, -1), (4.5, -4), (2.5, -6.5), (0, -6.8))
    form(_sym(hd), MURA_SKIN, sh=0.15, sdx=0)
    for x in (-2.3, 2.3):
        fill(ell(x, 1.4, 1.7, 1.4, 12), SOCKET)
        eye(x, 1.3, 0.85, EYE_Y, 2.4)
    stroke(bez((0, 1.5), (0.7, -0.5), (1.0, -1.8), (0.1, -2.6)), LINE*0.6)
    shape(bez((-2, -4), (-1, -5.2), (1, -5.2), (2, -4)) + [(0, -3.6)], MOUTH_D, LINE*0.5)
    top = [(0, 8)] + bez((0, 8), (4, 8), (6, 5), (5.5, 2)) + [(3, 4), (1.2, 3.2), (0, 4.5)]
    form(_sym(top), MURA_HAIR, sh=0.1, sdx=0)


def _bubak_fb(base, back):
    q = BBP[base]
    st = _step(base, 0.7); swg = _swing(base)
    roll = {1: -3, 3: 3}.get(WALK_I.get(base), 0) + swg*1.5
    op = q["open"]; tf = q.get("tuft", 0)*(1 if base in ("walk", "walk2") else -1)
    for x, (lift, sc) in sorted(zip((-8.5, 8.5), st), key=lambda t: t[1][1]):
        tube(bez((x*0.7, 14), (x*0.9, 9), (x, 6), (x*1.1, lift+2.5)), 5*sc, 4*sc, SACKV_D, sh=0)
        shape(ell(x*1.15, lift+1.8, 4.2*sc, 2.2*sc, 14), SACKV_D, LINE*0.8)
    reach = q["reach"]

    def arms():
        for sd in (-1, 1):
            if back:
                tube(bez((sd*12, 30), (sd*18, 33), (sd*23, 33), (sd*28, 30)), 4.5, 2, SHADE, sh=0)
                claws(sd*28, 30, 90 - sd*80, 4, 4.0, 20, Col(0.55, "#8a7e9a"), LINE*0.9)
            else:
                tube(bez((sd*9, 28), (sd*15, 26), (sd*20, 20), (sd*23, 13)), 5, 2.4, SACKV_D, sh=0)
                claws(sd*23, 13, -90 + sd*25, 4, 4.4, 22, Col(0.55, "#8a7e9a"), LINE*0.9)

    with T(0, 8, 1, rot=roll):
        if reach and back: arms()
        sq = q["sq"]
        half = [(0, 52)] + bez((0, 52), (6, 52), (14, 49), (17, 41)) + bez((17, 41), (22*sq, 31), (21, 13), (14, 2)) + \
               bez((14, 2), (8, -3), (3, -3), (0, -3))
        sack = notch(_sym(half), 0.6, 7)
        form(sack, SACKV, sdx=-1.5, sdy=2, sh=0.2)
        for x in (-9, 0, 9):
            stroke(bez((x*0.7, 48), (x + 1.5, 36), (x - 1, 22), (x*0.9, 4)), LINE*0.45, g=SACKV_D)
        if back:
            pt = [(-6, 13), (5, 12), (5.5, 21.5), (-5.5, 22.5)]
            form(pt, SACKV_D, sh=0)
            for i in range(5):
                x = -5.5 + i*2.6
                stroke([(x, 13.6), (x+1.2, 11.8)], LINE*0.45, g=ROPE)
            for (ex, ey, r, c) in ((-9, 38, 1.3, EYE_G), (11, 30, 1.1, EYE_Y)):
                fill(ell(ex, ey, r*1.6, r*1.25, 14), SOCKET)
                eye(ex, ey, r, c, 2.2)
        else:
            up = bez((-13, 29), (-6, 30 + op*9), (6, 30 + op*9), (13, 29))
            lo = bez((13, 29), (6, 28 - op*9), (-6, 28 - op*9), (-13, 29))
            shape(up + lo[1:], SOCKET if op > 0.05 else SACKV_D, LINE*0.8)
            for i in range(1, 9):
                p = up[i*2 - 1]; q_ = lo[17 - i*2]
                fill([(p[0]-0.9, p[1]+0.2), (p[0]+0.9, p[1]+0.2), (p[0], p[1]-1.6-op*1.4)], TOOTH)
                if op > 0.05:
                    fill([(q_[0]-0.9, q_[1]-0.2), (q_[0]+0.9, q_[1]-0.2), (q_[0], q_[1]+1.6+op*1.2)], TOOTH)
            if op > 0.5:
                for (ex, ey, r) in ((-5, 29, 1.1), (0, 31, 0.9), (5, 28.5, 1.1)):
                    eye(ex, ey, r, EYE_R, 2.2)
            eyes = ((-6, 41, 1.9, EYE_Y), (6, 41, 1.9, EYE_Y), (-12.5, 35.5 + op*2, 1.4, EYE_G), (12.5, 35.5 + op*2, 1.4, EYE_G),
                    (0, 46.5, 1.1, EYE_Y), (-9, 18, 1.2, EYE_Y), (9, 18, 1.2, EYE_Y))
            for (ex, ey, r, c) in eyes:
                fill(ell(ex, ey, r*1.6, r*1.25, 14), SOCKET)
                eye(ex, ey, r, c, 2.2)
                stroke(bez((ex-r*1.7, ey+r*0.5), (ex-r, ey+r*1.3), (ex+r, ey+r*1.3), (ex+r*1.7, ey+r*0.4)), LINE*0.5)
        stroke([(-7, 49), (7, 49.5)], LINE*2.4, g=ROPE); stroke([(-7, 49), (7, 49.5)], LINE*0.5)
        top = [(-5, 50), (-8.5 + tf, 58), (-4.5, 55), (-2 + tf*0.8, 61), (0, 56), (2 + tf*0.6, 61), (4.5, 55), (8.5 + tf*0.5, 58), (5, 50)]
        form(top, SACKV, sh=0.12, sdx=0)
        knot_side = -1 if back else 1
        stroke([(knot_side*4, 49.5), (knot_side*6 + tf*0.5, 44), (knot_side*5.5 + tf, 40)], LINE*1.6, g=ROPE)
        if reach and not back: arms()


def _svet_fb(base, back):
    q = SVP[base]
    ph = _phase(base); walking = base in WALK_I
    sw = math.sin(ph)*3 if walking else q["sway"]*0.2
    c = math.cos(ph) if walking else 0
    blaze = q["blaze"]
    hands = {"windup": ((-7, 27), (7, 27)), "attack": ((-13, 40), (13, 40))}.get(base, ((-13, 19 + c*2.5), (13, 19 - c*2.5)))
    with T(0, 4 + q.get("dy", 0)):
        glow(0, 62, 28 if blaze else 20, FLAME, 0.12, 5)

        def arms():
            for sd, h in ((-1, hands[0]), (1, hands[1])):
                a, e, hh = limb((sd*6.5, 50), h, 17, 17, 4.0, 3.0, GHOST, sd)
                form(ribbon([(sd*6.5, 50), ((sd*6.5+e[0])/2, (50+e[1])/2), e], 6, 4.6), ROBE_G, sh=0.1)
                _long_fingers(hh, e, GHOST)

        if back and base in ("windup", "attack"): arms()
        half = [(0, 58), (3.5, 57.5), (7, 54)] + bez((7, 54), (12, 44), (14, 24), (16, 4)) + \
               [(14, 7), (12.5, -2), (9.5, 5), (7, -4), (4.5, 4), (2, -3), (0, 4)]
        robe = _sway(_sym(half), sw, 14, 24)
        form(robe, ROBE_G, sdx=0, sdy=1.5, sh=0.18)
        for x in (-8, -3, 3, 8):
            stroke(bez((x*0.5, 54), (x*0.8, 40), (x + sw*0.2, 24), (x*1.15 + sw*0.6, 6)), LINE*0.45, g=ROBE_D)
        hood = [(0, 71), (5, 70.5)] + bez((5, 70.5), (10, 69), (11.5, 61), (9.5, 52)) + [(4.5, 55), (0, 55.5)]
        if not back: form(_sym(hood), ROBE_D, sh=0.12, sdx=0)
        with T(0, 62, 1.12 if blaze else 1.0, rot=-sw*0.6 + (6 if base == "windup" else 0)):
            if back: _lantern_back()
            else: _lantern_head(blaze)
        if back:
            cowl = [(0, 63), (5, 62.5)] + bez((5, 62.5), (10, 61.5), (11.5, 57), (9.5, 52)) + [(4.5, 54.5), (0, 55)]
            form(_sym(cowl), ROBE_D, sh=0.12, sdx=0)
            stroke(bez((0, 66), (0.5, 61), (-0.5, 57), (0, 54)), LINE*0.5, g=ROBE_G)
        if not (back and base in ("windup", "attack")): arms()
    if blaze:
        for sd in (-1, 1):
            for k in range(4):
                aa = math.radians(-25+k*22)
                cx = sd*math.cos(aa); cy = math.sin(aa)
                stroke([(cx*15, 66+cy*15), (cx*23, 66+cy*23)], LINE*0.9, g=FLAME_L, alpha=0.8)


def _lantern_back():
    for k, (x, rx) in enumerate(((-4.5, 4.5), (4.5, 4.5), (0, 5.5))):
        form(ell(x, 0, rx, 8, 24), GOURD if k == 2 else GOURD_D, sh=0.14)
    stroke(ell(0, 0, 9, 8, 30, 100, 260), LINE*0.5)
    form([(-1, 7), (1.5, 7), (3, 11), (1.5, 11.5)], MOSS_D, sh=0)
    for x in (-6.5, 6.5):
        glow(x*1.3, 0, 4, FLAME_L, 0.14, 2)


def _pitch_arm(sh, hand, g, w, bend, s=1.0, back=False):
    a, e, h = ik(sh, hand, 20, 19, bend)
    form(ribbon(chaikin([a, e, h]), w, w*0.85, w*1.1), g, sh=0.16, sdx=0)
    shape(notch(ell(h[0], h[1], 7*s, 6.5*s, 22), 0.8, 4), g, LINE*0.9)
    if not back:
        for d in (-2.5, 0, 2.5):
            stroke([(h[0]+d*s, h[1]-1*s), (h[0]+d*1.2*s, h[1]-5*s)], LINE*0.5)
    return h


def _smolak_fb(base, back):
    q = SMP[base]
    hip = q["hip"][1]
    st = _step(base, 1.3); swg = _swing(base)
    roll = {1: -3.5, 3: 3.5}.get(WALK_I.get(base), 0)
    fill(ell(0, 1.2, 24, 3.4, 30), Col(0.3, "#3e4a2c"), 0.55)
    glow(0, 1.2, 17, SMOL, 0.06, 3, 2.6)
    for x, (lift, sc) in sorted(zip((-1, 1), st), key=lambda t: t[1][1]):
        a, k, w = ik((x*8, hip), (x*11, lift+6), 15, 14, x)
        form(ribbon(chaikin([a, k, w]), 15*sc, 13*sc, 15*sc), PITCH_D if x < 0 else PITCH, sh=0.16, sdx=0)
        foot = bez((w[0]-8*sc, w[1]+1), (w[0]-9*sc, w[1]-4.5), (w[0]+9*sc, w[1]-4.5), (w[0]+8*sc, w[1]+1))
        shape(foot, PITCH_D if x < 0 else PITCH, LINE*0.9)
        if not back:
            for d in (-3.5, 0, 3.5):
                stroke([(w[0]+d*sc, w[1]-1.2), (w[0]+d*sc, w[1]-3.6)], LINE*0.45)
    if base == "windup":
        fists = ((-27, 12, 1), (27, 12, 1))
    elif base == "attack":
        fists = ((-7, 100, 1.05), (7, 100, 1.05))
    else:
        fists = ((-24 + swg*2.5, 22 + swg*5, 1 + swg*0.08), (24 + swg*2.5, 22 - swg*5, 1 - swg*0.08))
    with T(0, hip, 1, rot=roll):
        if back:
            with T(0, 46, 1):
                form(_sym([(0, 10)] + bez((0, 10), (6, 10), (9, 5), (8.5, -1)) + [(4, -5), (0, -5)]), PITCH, sh=0.18, sdx=0)
        half = [(0, 48)] + bez((0, 48), (10, 48), (19, 43), (21, 32)) + bez((21, 32), (23, 20), (21, 4), (14, -6)) + \
               [(11, -9), (8, -5), (5, -11), (2, -6), (0, -9)]
        body = _sym(half)
        form(body, PITCH, sdx=0, sdy=2, sh=0.2)

        def veins():
            vs = ([(-5, 38), (-2, 30), (-6, 22), (-2, 12)], [(7, 40), (5, 30), (10, 22), (8, 10)], [(-15, 16), (-11, 8), (-14, 0)],
                  [(15, 18), (12, 10), (15, 2)]) if not back else \
                 ([(0, 46), (-2, 36), (2, 26), (-1, 14), (1, 2)], [(-12, 40), (-8, 32), (-13, 24)], [(12, 38), (9, 28), (13, 18)])
            for pts in vs:
                stroke(pts, LINE*2.4, g=SMOL, alpha=0.35)
                stroke(pts, LINE*0.9, g=SMOL)
            for x, y, r in ((-12, 32, 3.5), (5, 42, 2.6), (14, 28, 3), (-16, 18, 2.2)):
                fill(ell(x, y, r, r*0.6, 14, rot=20), PITCH_L, 0.55)
        clipped(body, veins)
        for x, l in ((-7, 7), (0, 9), (7, 6)):
            tube([(x, -8), (x+0.3, -8-l)], 2.6, 1.2, PITCH, lw=LINE*0.6, sh=0)
            dot(x+0.3, -9-l-1.2, 1.1, PITCH)
        if not back:
            with T(0, 45, 1):
                form(_sym([(0, 10)] + bez((0, 10), (6, 10), (9, 5), (8.5, -1)) + [(4, -5), (0, -5)]), PITCH, sh=0.18, sdx=0)
                for ex in (-3.3, 3.3):
                    fill(ell(ex, 2.5, 1.9, 1.3, 12), SOCKET)
                    eye(ex, 2.4, 1.0, SMOL, 2.6)
                mo = [(-3.5, -1.2), (3.5, -1.2), (2, -3.2), (-2, -3.2)] if base != "attack" else [(-4, -0.4), (4, -0.4), (2.5, -4.4), (-2.5, -4.4)]
                shape(mo, SOCKET, LINE*0.6)
                glow(0, -1.8, 3, SMOL, 0.2, 2)
    for x, y, s in sorted(fists, key=lambda f: f[2]):
        sd = 1 if x > 0 else -1
        sh = world((0, hip), roll, (sd*17, 34))
        _pitch_arm(sh, (x, y), PITCH if sd > 0 else PITCH_D, 13.5*s, -sd if base == "attack" else sd, s, back)
    if base == "attack":
        for sd in (-1, 1):
            for k in range(3):
                stroke([(sd*(10+k*5), 110-k), (sd*(13+k*5), 118-k)], LINE*0.9, g=WHITE, alpha=0.6)
    for p in ((-17, 10), (17, 12)):
        drip(p[0], p[1], 1.0, PITCH_L)


def _bes_fb(base, back):
    q = BSP[base]
    hip = q["hip"][1]
    st = _step(base, 1.2); swg = _swing(base); tl = q.get("tail", 0)

    def tail():
        if back:
            pts = bez((0, hip+1), (1 + tl, hip-10), (-4 + tl*1.5, hip-20), (3 + tl*2, hip-30))
        else:
            pts = bez((0, hip+1), (-8, hip-6), (-14 - tl*0.5, hip-8), (-17 - tl, hip-18))
        tube(pts, 2.6, 1.0, BES_D, sh=0)
        e = pts[-1]
        shape([(e[0], e[1]+1.5), (e[0]-2.4, e[1]-1), (e[0], e[1]-4.5), (e[0]+2.4, e[1]-1)], BES_D, LINE*0.6)

    if not back: tail()
    if base == "windup":
        hands = ((-16, hip+55, 1), (16, hip+55, 1))
    elif base == "attack":
        hands = ((-7, hip+22, 1.1), (7, hip+22, 1.1))
    else:
        hands = ((-13 + swg*1.5, hip+3 + swg*4, 1 + swg*0.06), (13 + swg*1.5, hip+3 - swg*4, 1 - swg*0.06))
    if base == "attack" and back:
        glow(0, hip+28, 18, CURSE, 0.22, 5)

    def arm(sd, h, s):
        a, e, hh = ik((sd*9.5, hip+35), h, 19, 18, -sd if h[1] > hip+35 else sd)
        g = BES if sd > 0 else BES_D
        tube(chaikin([a, e, hh]), 5*s, 3*s, g, sh=0.14)
        _long_fingers(hh, e, g)
        return hh

    if back and base == "attack":
        for sd, (x, y, s) in zip((-1, 1), hands): arm(sd, (x, y), s)
    for x, (lift, sc) in sorted(zip((-1, 1), st), key=lambda t: t[1][1]):
        g = BES_D if x < 0 else BES
        j = (x*3.5, hip); k = (x*6, hip-17+lift*0.6); hk = (x*4.5, 10+lift); toe = (x*5, 2.6+lift)
        tube(chaikin([j, k, hk]), 7*sc, 3.2*sc, g, sh=0.14)
        tube([hk, toe], 3.2*sc, 2.8*sc, g, sh=0)
        shape(ell(toe[0], toe[1]-0.6, 2.6*sc, 1.9*sc, 14), g, LINE*0.8)
        if not back:
            claws(toe[0], toe[1]-1.6, -90, 3, 2.0, 28, BONE_FAR, LINE*0.6)
    with T(0, hip):
        half = [(0, 41)] + bez((0, 41), (5, 41), (9.5, 39), (10, 35)) + bez((10, 35), (9, 28), (6.5, 20), (5.5, 12)) + \
               bez((5.5, 12), (6, 6), (6.2, 2), (5.5, -3)) + [(0, -3)]
        form(_sym(half), BES, sdx=0, sdy=1.2, sh=0.18)
        if back:
            stroke(bez((0, 38), (0.4, 28), (-0.4, 18), (0, 4)), LINE*0.55, g=BES_D)
            for sd in (-1, 1):
                stroke(bez((sd*2.5, 36), (sd*6.5, 35), (sd*7.5, 30), (sd*4, 26)), LINE*0.5, g=BES_D)
                for i in range(3):
                    y = 22 - i*3.2
                    stroke([(sd*1.2, y), (sd*4.5, y-0.8)], LINE*0.4, g=BES_D)
        else:
            for i in range(4):
                y = 30 - i*3.6
                for sd in (-1, 1):
                    stroke(bez((sd*1, y+0.6), (sd*3, y+0.8), (sd*5.5, y-0.4), (sd*(7.5 - i*0.6), y-2.5)), LINE*0.55, g=BES_D)
        lc = [(-7, 3), (7, 3), (6.5, -5), (4, -13), (2, -6), (0, -15), (-2, -6), (-4, -13), (-6.5, -5)]
        form(lc, RAG_D, sh=0.16, sdx=0)
        shape(rrect(-7.5, 1, 15, 3, 1.2), LEATHER_D, LINE*0.7)
    if back: tail()
    with T(0, hip+46, 1, rot=-swg*2):
        _bes_head_fb(back)
    if not (back and base == "attack"):
        hh = [arm(sd, (x, y), s) for sd, (x, y, s) in zip((-1, 1), hands)]
    if base == "attack":
        if back: return
        c = (0, hip+26)
        glow(c[0], c[1], 13, CURSE, 0.22, 5)
        stroke(ell(c[0], c[1], 9, 9, 40), LINE*0.6, closed=True, g=CURSE)
        for k in range(6):
            aa = math.radians(k*60+30)
            px, py = c[0]+math.cos(aa)*9, c[1]+math.sin(aa)*9
            stroke([(px-1.2, py-1.2), (px+1.2, py+1.2)], LINE*0.6, g=CURSE)
            stroke([(px-1.2, py+1.2), (px+1.2, py-1.2)], LINE*0.6, g=CURSE)
        shape(ell(c[0], c[1], 3.6, 3.6, 20), Col(0.85, "#e8c4ff"), LINE*0.6)
        dot(c[0]+1, c[1]+1, 1.2, WHITE)
    elif base != "windup":
        c = (hh[1][0]+1, hh[1][1]+3)
        glow(c[0], c[1], 5, CURSE, 0.2, 3)
        for k in range(3):
            stroke(bez((c[0]-1+k, c[1]), (c[0]+k*1.5-1, c[1]+3), (c[0]-2+k, c[1]+5), (c[0]+k-1, c[1]+8)), LINE*0.5, g=CURSE, alpha=0.7)


def _bes_head_fb(back):
    def horn(sd):
        hx = 2.5
        hn = bez((hx, 3), (hx+4, 9), (hx+9, 13), (hx+14, 11.5)) + bez((hx+14, 11.5), (hx+9, 11), (hx+5, 7), (hx+3.5, 1))
        form(hn, BONE_FAR if back else Col(0.75, "#c2b394"), sh=0.14, sdx=0)
        for k in range(4):
            x = hx + 3 + k*2.6
            stroke([(x, 6.5+k*1.2), (x+0.9, 5.2+k*1.3)], LINE*0.4)
        form([(4.8, 1), (10, 0.5), (5, -2.5)], BES_D, sh=0, sdx=0)
    if back:
        hd = [(0, 6.5)] + bez((0, 6.5), (4, 6.5), (5.5, 3), (5.2, -1)) + bez((5.2, -1), (4.8, -4), (3, -6), (0, -6.5))
        form(_sym(hd), BES, sh=0.16, sdx=0)
        stroke(bez((-3, 5), (-1, 3), (1, 3), (3, 5)), LINE*0.45, g=BES_D)
        _mirror(horn)
        return
    _mirror(horn)
    hd = [(0, 6.5)] + bez((0, 6.5), (4, 6.5), (5.5, 3), (5.2, -1)) + bez((5.2, -1), (4.5, -5), (3, -8.5), (0, -9.5))
    form(_sym(hd), BES, sh=0.16, sdx=0)
    for sd in (-1, 1):
        fill(ell(sd*2.3, 1.0, 1.8, 1.3, 12), SOCKET)
        eye(sd*2.3, 0.9, 0.95, EYE_V, 2.6)
        stroke([(sd*0.5, 2.9), (sd*4.6, 1.6)], LINE*0.9)
        dot(sd*0.8, -3.6, 0.35, SOCKET)
    shape(bez((-2.6, -5.4), (-1, -6.8), (1, -6.8), (2.6, -5.4)) + [(0, -5.1)], MOUTH_D, LINE*0.5)
    for sd in (-1, 1):
        fill([(sd*1.0, -5.7), (sd*1.7, -5.7), (sd*1.35, -6.9)], TOOTH)


for _fn in (bludicka, ohnivy_muzik, mura, bubak, svetlonos, smolak, bes):
    _fn.poses = ALL
