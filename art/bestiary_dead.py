import math
from bestiary_kit import *


def skull(cx, cy, r, jaw=0, eyecol=EYE_G, g=BONE):
    hx, hy = cx-0.2*r, cy-0.5*r
    jw = bez((cx+0.8*r, cy-0.7*r), (cx+0.85*r, cy-1.0*r), (cx+0.6*r, cy-1.18*r), (cx+0.2*r, cy-1.12*r)) + \
         bez((cx+0.2*r, cy-1.12*r), (cx-0.15*r, cy-1.08*r), (cx-0.35*r, cy-0.8*r), (cx-0.3*r, cy-0.5*r))
    jw = rot(jw, hx, hy, -jaw)
    if jaw > 4:
        fill([(hx, hy), (cx+0.85*r, cy-0.7*r)] + rot([(cx+0.8*r, cy-0.7*r)], hx, hy, -jaw), SOCKET)
    shape(jw, g, LINE*0.9)
    for i in range(4):
        x = cx+0.3*r+i*0.14*r
        p = rot([(x, cy-0.78*r), (x+0.02*r, cy-0.92*r)], hx, hy, -jaw)
        stroke(p, LINE*0.5)
    head = bez((cx-0.35*r, cy-0.55*r), (cx-1.15*r, cy-0.25*r), (cx-1.15*r, cy+1.0*r), (cx+0.05*r, cy+1.02*r)) + \
           bez((cx+0.05*r, cy+1.02*r), (cx+0.8*r, cy+1.02*r), (cx+1.02*r, cy+0.55*r), (cx+0.98*r, cy+0.1*r)) + \
           bez((cx+0.98*r, cy+0.1*r), (cx+1.05*r, cy-0.25*r), (cx+0.98*r, cy-0.55*r), (cx+0.85*r, cy-0.74*r)) + \
           [(cx+0.15*r, cy-0.78*r)]
    form(head, g, sdx=-r*0.3, sdy=r*0.15, sh=0.16)
    fill(ell(cx+0.45*r, cy+0.03*r, 0.3*r, 0.33*r, 20), SOCKET)
    fill(ell(cx-0.05*r, cy+0.0*r, 0.12*r, 0.26*r, 14), SOCKET)
    eye(cx+0.47*r, cy+0.0*r, 0.13*r, eyecol)
    fill([(cx+0.84*r, cy-0.2*r), (cx+0.93*r, cy-0.48*r), (cx+0.72*r, cy-0.46*r)], SOCKET)
    stroke([(cx+0.15*r, cy-0.76*r), (cx+0.85*r, cy-0.74*r)], LINE*0.6)
    for i in range(4):
        x = cx+0.3*r+i*0.14*r
        stroke([(x, cy-0.74*r), (x+0.02*r, cy-0.6*r)], LINE*0.5)
    stroke(bez((cx+0.1*r, cy-0.35*r), (cx+0.3*r, cy-0.45*r), (cx+0.55*r, cy-0.45*r), (cx+0.7*r, cy-0.4*r)), LINE*0.5)


def ribcage(neck, w=11, g=BONE, n=5):
    sp = bez((0, 0), (-3.5, 6), (-3.5, neck*0.6), (0, neck))
    bone(sp[0], sp[len(sp)//2], 2.4, g, knob=False)
    bone(sp[len(sp)//2], sp[-1], 2.2, g, knob=False)
    for i in range(n):
        t = 0.48 + i*0.1
        p = sp[min(len(sp)-1, int(t*len(sp)))]
        ww = w*(0.85+0.15*math.sin(math.pi*(i+1)/(n+1)))
        rib = bez(p, (p[0]+ww*0.35, p[1]+2.2), (p[0]+ww*0.95, p[1]+0.5), (p[0]+ww, p[1]-3.0-i*0.2))
        tube(rib, 1.9, 1.3, g, lw=LINE*0.8, sh=0)
    stroke(bez((w*0.95, neck-2), (w*1.05, neck-6), (w*1.0, neck-10), (w*0.8, neck-13)), LINE*1.6, g=g)
    stroke(bez((w*0.95, neck-2), (w*1.05, neck-6), (w*1.0, neck-10), (w*0.8, neck-13)), LINE*0.5)
    return sp


def pelvis(g=BONE):
    p = bez((-4.5, 2.5), (-5.5, -1), (-3, -4), (0, -3.5)) + bez((0, -3.5), (3, -4), (5.5, -1), (4.5, 2.5)) + \
        bez((4.5, 2.5), (2, 1.5), (-2, 1.5), (-4.5, 2.5))
    form(p, g, sh=0.15)
    fill(ell(1.6, -1.2, 1.2, 1.0, 12), SOCKET)


def skel_leg(hip, foot, g, l1=16, l2=15.5, w=2.6):
    a, k, f = ik(hip, foot, l1, l2, 1)
    bone(a, k, w, g); bone(k, f, w*0.85, g)
    ft = bez((f[0]-1.5, f[1]+0.5), (f[0]-2.5, f[1]-2.5), (f[0]+3, f[1]-2.6), (f[0]+6, f[1]-2.4)) + [(f[0]+5.5, f[1]-1.0), (f[0]+1.5, f[1]+0.8)]
    shape(ft, g, LINE*0.8)
    return k


def skel_arm(sh, hand, g, l1=12, l2=11.5, w=2.2, bend=-1):
    a, e, h = ik(sh, hand, l1, l2, bend)
    bone(a, e, w, g); bone(e, h, w*0.85, g)
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    for i in range(3):
        aa = math.radians(ang+(i-1)*24)
        p1 = (h[0]+math.cos(aa)*2.6, h[1]+math.sin(aa)*2.6)
        p2 = (p1[0]+math.cos(aa-0.9)*1.6, p1[1]+math.sin(aa-0.9)*1.6)
        stroke([h, p1, p2], LINE*0.9, g=g)
        stroke([h, p1, p2], LINE*0.35)
    return e, h


def pick(p0, p1, head_len=11, g=WOOD):
    tube([p0, p1], 2.3, 2.6, g, sh=0.12)
    a = math.atan2(p1[1]-p0[1], p1[0]-p0[0])
    nx, ny = -math.sin(a), math.cos(a)
    dx, dy = math.cos(a), math.sin(a)
    c = (p1[0]-dx*0.5, p1[1]-dy*0.5)
    L = head_len
    hd = bez((c[0]+nx*L+dx*0.0, c[1]+ny*L+dy*0.0), (c[0]+nx*L*0.4+dx*2.2, c[1]+ny*L*0.4+dy*2.2),
             (c[0]-nx*L*0.4+dx*2.2, c[1]-ny*L*0.4+dy*2.2), (c[0]-nx*L, c[1]-ny*L)) + \
         bez((c[0]-nx*L, c[1]-ny*L), (c[0]-nx*L*0.4-dx*0.4, c[1]-ny*L*0.4-dy*0.4),
             (c[0]+nx*L*0.4-dx*0.4, c[1]+ny*L*0.4-dy*0.4), (c[0]+nx*L, c[1]+ny*L))
    form(hd, IRON, sh=0.18)


def rag_hem(x0, x1, y, depth, n, seed=0):
    pts = []
    for i in range(n+1):
        x = x0+(x1-x0)*i/n
        d = depth*(0.4+0.6*((i*7+seed) % 5)/4) if i % 2 else 0
        pts.append((x, y-d))
    return pts


SKP = {
    "idle": dict(lean=-4, hip=(0, 33.0), ff=(-6, 2.5), nf=(6, 2.5), head=0, jaw=0),
    "walk": dict(lean=-8, hip=(0, 31.5), ff=(9, 2.5), nf=(-9, 4.5), head=-4, jaw=0),
    "attack": dict(lean=-18, hip=(-2, 29.5), ff=(-15, 2.5), nf=(11, 2.5), head=-6, jaw=22),
}


def skeleton(pose, eyecol, back=None, torso=None, near=None, far=None, hat=None, scale_neck=21):
    q = SKP[pose]
    hx, hy = q["hip"]
    neck = scale_neck
    if back: back(q)
    with T(hx, hy, 1, rot=q["lean"]):
        if far: far(q)
    skel_leg((hx-1, hy), q["ff"], BONE_FAR)
    with T(hx, hy, 1, rot=q["lean"]):
        ribcage(neck)
        pelvis()
        if torso: torso(q)
    skel_leg((hx+1, hy), q["nf"], BONE)
    with T(hx, hy, 1, rot=q["lean"]):
        with T(1.5, neck+6.5, 1, rot=q["head"]):
            skull(0, 0, 6.4, q["jaw"], eyecol)
            if hat: hat(q)
        if near: near(q)


def kostlivy_havir(pose):
    def back(q):
        hx, hy = q["hip"]
        with T(hx, hy, 1, rot=q["lean"]):
            ap = bez((-4, 3), (-11, 1), (-12, -10), (-7, -15)) + [(-4, -13), (-2, -15), (1, -9)]
            form(ap, LEATHER, sh=0.18)

    def far(q):
        sh = (-1.5, 19)
        tgt = {"idle": (-4, 1), "walk": (-8, 5), "attack": (17, 11)}[pose]
        skel_arm(sh, tgt, BONE_FAR)

    def torso(q):
        sm = bez((-4.5, 21.5), (-6.5, 16), (-6.5, 12), (-6, 9)) + rag_hem(-6, 3, 9, 3.5, 5, 1) + \
             [(3, 9), (2, 14), (5, 18), (6, 21)] + bez((6, 21), (3, 23), (-1, 23.5), (-4.5, 21.5))
        form(sm, RAG, sh=0.2)
        hatch(sm, 1.8, 50, 0.4, 0.0, 0.4)
        shape(rrect(-6.5, -1.5, 13, 3, 1.2), LEATHER_D, LINE*0.8)
        with T(5.5, -2.5):
            stroke([(0, 1), (0, -2)], LINE*0.7)
            shape([(-2, -2), (2, -2), (2.6, -6), (-2.6, -6)], IRON_D, LINE*0.7)
            glow(0, -5, 4, FLAME, 0.2, 3)
            fill(ell(0, -4.2, 0.9, 1.6, 10), FLAME)

    def hat(q):
        cap = bez((-6.6, 2.5), (-7.5, 9.5), (4.5, 10.5), (6.8, 3.5)) + [(7.6, 2.8), (7.4, 1.8), (-6.8, 1.6)]
        form(cap, LEATHER, sh=0.2)
        stroke([(-6.5, 2.4), (7.2, 2.6)], LINE*0.7)
        shape(rrect(1.5, 2.7, 2, 3.2, 0.6), IRON, LINE*0.6)

    def near(q):
        sh = (2.5, 19.5)
        if pose == "attack":
            h = (20, 20)
            skel_arm(sh, h, BONE)
            pick((h[0]-9, h[1]-6), (h[0]+7, h[1]+16), 12)
            swoosh(bez((-6, 40), (2, 54), (20, 54), (28, 32)), 2.4, WHITE, 0.3)
        elif pose == "walk":
            h = (9, 6)
            skel_arm(sh, h, BONE)
            pick((h[0]-14, h[1]-7), (h[0]+6, h[1]+18), 11)
        else:
            h = (9, 7)
            skel_arm(sh, h, BONE)
            pick((h[0]-1, h[1]-36), (h[0]+1, h[1]+16), 11)
    skeleton(pose, EYE_Y, back, torso, near, far, hat)


def kostlivy_kusinik(pose):
    def far(q):
        sh = (-1.5, 19)
        tgt = {"idle": (10, 9), "walk": (10, 10), "attack": (19, 22)}[pose]
        skel_arm(sh, tgt, BONE_FAR)
        rr = rrect(-9, -2, 4.2, 12, 1.5)
        with T(0, 0, 1, rot=12):
            form(rr, LEATHER_D, sh=0.15)
            for i in range(3):
                stroke([(-8+i*1.2, 9.5), (-8.5+i*1.2, 14)], LINE*0.8, g=WOOD)
                fill([(-9+i*1.2, 13.5), (-7.6+i*1.2, 13.5), (-8.3+i*1.2, 15.5)], RAG)

    def torso(q):
        tb = bez((-5, 22), (-7.5, 15), (-7, 8), (-6.5, 3)) + rag_hem(-6.5, 7, 3, 4, 6, 3) + \
             bez((7, 3), (6, 10), (7, 16), (6.5, 22)) + bez((6.5, 22), (3, 23.5), (-2, 23.5), (-5, 22))
        form(tb, RUST_D, sh=0.2)
        stroke([(0.5, 22.5), (1.2, 4)], LINE*0.6)
        shape(rrect(-7, -0.5, 14, 3, 1.2), LEATHER_D, LINE*0.8)

    def hat(q):
        brim = bez((-10, 3.2), (-6, 1.0), (6, 1.0), (10.5, 3.6)) + bez((10.5, 3.6), (7, 5.4), (-6, 5.4), (-10, 3.2))
        dome = bez((-6, 4.2), (-6.5, 12), (6.5, 12), (6.5, 4.4))
        form(dome + [(0, 4.2)], RUST, sh=0.2)
        form(brim, RUST, sh=0.14)
        for x in (-3, 0, 3): dot(x, 6.5, 0.45, RUST_D)

    def near(q):
        sh = (2.5, 19.5)
        if pose == "attack":
            h = (12, 21)
            skel_arm(sh, h, BONE)
            crossbow((h[0]-6, h[1]), 0, True)
            for i, dy in enumerate((-3, 0, 3)):
                stroke([(34, 22+dy), (39, 22+dy*1.4)], LINE*0.6, g=WHITE)
        else:
            h = (6, 9) if pose == "idle" else (7, 10)
            skel_arm(sh, h, BONE)
            crossbow((h[0]-2, h[1]+1), -28 if pose == "idle" else -18, True)
    skeleton(pose, EYE_R, None, torso, near, far, hat)


def crossbow(p, ang, loaded):
    with T(p[0], p[1], 1, rot=ang):
        st = [(-6, -1.6), (16, -1.2), (17, 1.0), (-4, 1.4), (-7, -0.2)]
        form(st, WOOD, sh=0.15)
        bow = bez((15, 0.5), (14, 6), (11, 10), (9, 12)) + bez((9, 12), (10, 10), (12.5, 6), (13.5, 0.5))
        bow2 = [(x, -y+1) for x, y in bow]
        shape(bow, IRON, LINE*0.7); shape(bow2, IRON, LINE*0.7)
        stroke([(9.2, 11.6), (5, 0.5), (9.2, -10.6)], LINE*0.45, g=BONE)
        if loaded:
            stroke([(5, 1.6), (19.5, 1.6)], LINE*0.8, g=WOOD)
            shape([(19, 0.6), (22, 1.6), (19, 2.6)], IRON, LINE*0.5)
        stroke([(0, -1.3), (-1, -4)], LINE*0.9)


def kostejuv_nesmrtelny(pose):
    def back(q):
        hx, hy = q["hip"]
        with T(hx, hy, 1, rot=q["lean"]):
            sw = {"idle": 0, "walk": -3, "attack": -8}[pose]
            cl = bez((-4, 25), (-12, 18), (-14+sw, 6), (-16+sw, -16)) + rag_hem(-16+sw, -2, -16, 4, 7, 2) + \
                 bez((-2, -16), (-4, -4), (2, 10), (4, 24))
            form(cl, VIOLET, sh=0.2)

    def far(q):
        sh = (-1.5, 19)
        tgt = {"idle": (2, 8), "walk": (-6, 6), "attack": (-10, 12)}[pose]
        e, h = skel_arm(sh, tgt, BONE_FAR)
        with T(h[0]+1, h[1]+1):
            sd = ell(0, 0, 8, 9.5, 30)
            form(sd, RUST_D, sh=0.2)
            stroke(ell(0, 0, 6.2, 7.6, 30), LINE*0.6, closed=True)
            shape(ell(0, 0, 2.0, 2.0, 14), IRON, LINE*0.7)

    def torso(q):
        mail = [(-7, 6), (8, 6)] + rag_hem(8, -7, -5, 2.5, 8, 4)
        form(mail, IRON_D, sh=0.15)
        hatch(mail, 1.2, 60, 0.35, 0.0, 0.5); hatch(mail, 1.2, -60, 0.35, 0.0, 0.5)
        cu = bez((-5, 23), (-8, 17), (-7.5, 9), (-6, 3)) + bez((-6, 3), (-1, 1), (5, 1), (9, 4)) + \
             bez((9, 4), (11.5, 11), (11, 18), (7.5, 23)) + bez((7.5, 23), (3, 24.5), (-1, 24.5), (-5, 23))
        form(cu, RUST, sdx=-2.5, sdy=1, sh=0.2)
        stroke(bez((5, 22), (8.5, 17), (9, 10), (6.5, 4)), LINE*0.6)
        for p in ((-3, 20), (6, 20), (-3, 6), (6.5, 6.5)): dot(p[0], p[1], 0.5, IRON_D)
        pa = bez((-2, 25.5), (-6, 25), (-7, 20), (-4, 17.5)) + bez((-4, 17.5), (0, 16.5), (4, 18), (5, 21)) + bez((5, 21), (5, 24), (2, 26), (-2, 25.5))
        form(pa, RUST, sh=0.2)

    def hat(q):
        mail = [(-6.8, 2), (-8.2, -6.5), (-4.5, -9), (-2, -6), (-3, 1)]
        form(mail, IRON_D, sh=0.1)
        hatch(mail, 1.1, 60, 0.35, 0.0, 0.5)
        hm = bez((-7.2, 1.8), (-7.6, 7.5), (-3, 9.5), (0.5, 13.5)) + bez((0.5, 13.5), (3, 9.5), (7.6, 7.5), (7.4, 1.8)) + \
             bez((7.4, 1.8), (3, 3.2), (-3, 3.2), (-7.2, 1.8))
        form(hm, RUST, sh=0.2)
        stroke([(0.5, 13), (0.6, 3.5)], LINE*0.5)
        shape(rrect(-7.6, 1.2, 15.4, 2.4, 1), IRON_D, LINE*0.7)
        shape([(5.2, 2), (6.6, 2), (6.4, -3.5), (5.4, -3.5)], IRON, LINE*0.6)
        glow(0.5, 14, 3.5, EYE_G, 0.12, 3)

    def near(q):
        sh = (2.5, 19.5)
        if pose == "attack":
            h = (17, 25)
            skel_arm(sh, h, BONE)
            sword(h, 25)
            swoosh(bez((-4, 58), (12, 64), (28, 52), (31, 30)), 2.6, EYE_G, 0.3)
        else:
            h = (9, 10) if pose == "idle" else (10, 12)
            skel_arm(sh, h, BONE)
            sword(h, -60 if pose == "idle" else -35)
        for p in ((3, 41), (-6, 30)):
            glow(p[0], p[1], 5, EYE_G, 0.08, 3)
    with T(0, 0, 1.12):
        skeleton(pose, EYE_G, back, torso, near, far, hat)


def sword(h, ang):
    with T(h[0], h[1], 1, rot=ang):
        tube([(-1, 0), (-5, 0)], 2.2, 2.2, LEATHER_D, sh=0)
        shape(ell(-5.8, 0, 1.4, 1.4, 12), IRON, LINE*0.7)
        shape([(1.5, -4), (2.6, -4), (2.6, 4), (1.5, 4)], IRON_D, LINE*0.7)
        bl = [(2.6, -1.6), (24, -1.2), (28, 0), (24, 1.2), (2.6, 1.6)]
        form(bl, IRON, sh=0.15)
        stroke([(3, 0), (23, 0)], LINE*0.4)
        for x in (8, 15, 21): fill(ell(x, 0.4, 1.2, 0.8, 10), RUST, 0.7)


DROWN = Col(0.6, "#90a794")
DROWN_D = Col(0.5, "#728b79")
WEED = Col(0.4, "#56692f")
WEED_L = Col(0.5, "#7d9142")
SHIRT_W = Col(0.5, "#6a7c8c")
TROUS = Col(0.4, "#5b5968")

UTP = {
    "idle": dict(hip=(0, 36), lean=-10, ff=(-7, 2), nf=(8, 2), fh=(13, 3), nh=(16, 5), head=-8, mouth=0.45),
    "walk": dict(hip=(0, 35), lean=-14, ff=(10, 2), nf=(-10, 3.5), fh=(6, 2), nh=(20, 9), head=-6, mouth=0.45),
    "attack": dict(hip=(-3, 33.5), lean=-22, ff=(-17, 2), nf=(11, 2), fh=(27, 21), nh=(30, 15), head=4, mouth=1.0),
}


def utopenec(pose):
    q = UTP[pose]
    hip, lean = q["hip"], q["lean"]
    with T(hip[0], hip[1], 1, rot=lean):
        limb((-1, 25), q["fh"], 15, 14, 6.5, 5.5, DROWN_D, -1)
        mitt(*_hand_end((-1, 25), q["fh"], 15, 14), 2.6, DROWN_D)
    limb((hip[0]-2, hip[1]), q["ff"], 18, 17, 8.5, 6.5, Col(0.32, "#4a4856"), 1)
    bare_foot(q["ff"], DROWN_D, 7)
    with T(hip[0], hip[1], 1, rot=lean):
        body = bez((-8, -1), (-12, 10), (-11, 22), (-6, 27)) + bez((-6, 27), (-2, 30.5), (4, 30.5), (7.5, 26.5)) + \
               bez((7.5, 26.5), (12.5, 21), (15.5, 10), (12, 1)) + bez((12, 1), (6, -3), (-3, -3), (-8, -1))
        form(body, DROWN, sdx=-3, sdy=1.2, sh=0.15)
        shirt = [(-14, 33), (16, 33)] + rag_hem(16, -14, 9, 5, 9, 2)
        clipped(body, lambda: (fill(shirt, SHIRT_W), offset_shadow(shirt, -3, 1.2, 0.18), hatch(shirt, 2.2, 70, 0.4, 0.0, 0.35)))
        stroke(shirt[2:], LINE*0.7)
        stroke(body, LINE, closed=True)
        stroke(bez((9, 14), (11, 10), (10.5, 6), (8, 3)), LINE*0.6)
        shape(rrect(-10, -2, 23, 3.4, 1.4), LEATHER_D, LINE*0.8)
        for x0, y0, x1, y1 in ((-6, 28, -11, 12), (-3, 29, -6, 16), (2, 30, 1, 20)):
            tube(bez((x0, y0), (x0-2, (y0+y1)/2+3), (x1+2, (y0+y1)/2), (x1, y1)), 2.2, 0.7, WEED, lw=LINE*0.6, sh=0)
    limb((hip[0]+2, hip[1]), q["nf"], 18, 17, 9, 7, TROUS, 1)
    bare_foot(q["nf"], DROWN, 7.5)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(4, 33, 1, rot=q["head"]):
            _drowned_head(q["mouth"])
        a, e, h = limb((2, 25), q["nh"], 15, 14, 7, 6, DROWN, -1)
        mitt(*_hand_end((2, 25), q["nh"], 15, 14), 2.8, DROWN, claw=None)
        tube(bez(e, (e[0]+1, e[1]-4), (e[0]-1, e[1]-7), (e[0]+0.5, e[1]-10)), 1.8, 0.5, WEED, lw=LINE*0.5, sh=0)
        drip(h[0]+4, h[1]-4.5); drip(h[0]+1, h[1]-6.5, 0.6)
    if pose == "attack":
        for i in range(3):
            stroke([(36, 30+i*4-4), (41, 31+i*5-4)], LINE*0.5, g=COLD_L)


def _hand_end(a, c, l1, l2):
    _, e, h = ik(a, c, l1, l2, -1)
    return h[0], h[1], math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))


def _drowned_head(m):
    r = 8.2
    tube(bez((-5, -3), (-7, -8), (-9, -12), (-12, -16)), 2.6, 0.6, WEED, lw=LINE*0.6, sh=0)
    hd = bez((-2, -8), (-9, -7), (-9.5, 6), (-3, 8.5)) + bez((-3, 8.5), (3, 10.5), (9.5, 7), (9.6, 0)) + \
         bez((9.6, 0), (10, -4), (9, -7.5), (5, -9)) + bez((5, -9), (2, -10), (0, -9.5), (-2, -8))
    form(hd, DROWN, sdx=-2.4, sdy=1, sh=0.16)
    shape(ell(-5.2, 0, 1.6, 2.4, 14), DROWN_D, LINE*0.7)
    fill(ell(3.8, 1.2, 2.2, 1.7, 14), DROWN_D)
    stroke(bez((1.4, 3.3), (3, 4.3), (5, 4.2), (6.6, 3.2)), LINE*0.8)
    eye(4.3, 1.0, 1.15, EYE_C, 2.2)
    stroke([(8.5, 1), (10.5, -2.5), (8.8, -3.4)], LINE*0.7)
    mo = ell(6.6, -5.6, 1.4+0.9*m, 1.0+2.0*m, 18)
    shape(mo, MOUTH_D, LINE*0.7)
    for (x0, y0, x1, y1) in ((-6, 7.5, -12, -2), (-2, 9.5, -6, -6), (2, 9.8, 0.5, 4.8), (5, 9, 9.5, 4), (-8, 4, -11, -8)):
        tube(bez((x0, y0), (x0-1, y0-1.5), (x1+1, y1+2), (x1, y1)), 2.2, 0.6, WEED_L if x0 > 0 else WEED, lw=LINE*0.6, sh=0)
    drip(6.8, -9.5, 0.7)


SHROUD = Col(0.78, "#cdc8b6")
SHROUD_D = Col(0.6, "#a39d8a")
GAUNT = Col(0.7, "#b8b1c2")
GAUNT_D = Col(0.55, "#958da3")

UPP = {
    "idle": dict(hip=(0, 38), lean=-6, ff=(-5, 1.5), nf=(6, 1.5), hb=-12, hf=10, fh=(10, 18), nh=(13, 20), head=-6, mouth=0, flare=0),
    "walk": dict(hip=(1, 37), lean=-14, ff=(10, 1.5), nf=(-8, 3), hb=-17, hf=12, fh=(12, 20), nh=(15, 23), head=-4, mouth=0, flare=4),
    "attack": dict(hip=(-2, 36), lean=-24, ff=(-14, 1.5), nf=(12, 1.5), hb=-26, hf=16, fh=(30, 28), nh=(33, 22), head=6, mouth=1, flare=12),
}


def upir(pose):
    q = UPP[pose]
    hip, lean = q["hip"], q["lean"]
    sh = world(hip, lean, (0, 27))
    neck = world(hip, lean, (3, 33))
    with T(hip[0], hip[1], 1, rot=lean):
        a, e, h = limb((-1, 26), q["fh"], 15, 15, 4.6, 3.6, GAUNT_D, -1)
        _claw_hand(h, e, GAUNT_D)
    for f in (q["ff"], q["nf"]):
        bare_foot(f, GAUNT_D if f is q["ff"] else GAUNT, 6)
    hb, hf, fl = q["hb"], q["hf"], q["flare"]
    back_top = world(hip, lean, (-7, 36))
    front_top = world(hip, lean, (9, 31))
    sr = bez(back_top, (back_top[0]-6-fl*0.6, back_top[1]-12), (hb+2-fl*0.3, 20), (hb, 4)) + \
         rag_hem(hb, hf, 4, 3.5, 9, 3) + \
         bez((hf, 4), (hf+1, 14), (front_top[0]+4, front_top[1]-14), front_top)
    form(sr, SHROUD, sdx=-4, sdy=1, sh=0.16)
    gap = bez(front_top, (front_top[0]-1, front_top[1]-12), (hf-3, 16), (hf-2.5, 4.5)) + [(hf-6, 4.5)] + \
          bez((hf-6, 4.5), (hf-7, 16), (front_top[0]-5, front_top[1]-14), (front_top[0]-3, front_top[1]-2))
    shape(gap, Col(0.3, "#4d4256"), LINE*0.7)
    for i in range(3):
        y = 10 + i*9
        x0 = hb + 3 + i*1.6 - fl*0.3
        stroke(bez((x0, y), (x0+6, y-2.5), (hf-10+i, y+2), (hf-6+i*0.6, y+4)), LINE*0.6, g=SHROUD_D)
    hatch(sr, 2.0, 70, 0.35, 0.0, 0.25)
    if fl > 6:
        inner = bez((hb+5, 8), (hb+2, 22), (back_top[0]-4, back_top[1]-12), back_top) + [(back_top[0]+2, back_top[1]-14), (hb+10, 9)]
        shape(inner, Col(0.35, "#5d4f66"), LINE*0.7)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(4, 37, 1, rot=q["head"]):
            _vamp_head(q["mouth"])
        a, e, h = limb((2, 26), q["nh"], 15, 15, 5.2, 4.0, GAUNT, -1)
        sl = [(a[0]-3.5, a[1]+2.5), (e[0]+1, e[1]+3.2), (e[0]+1.2, e[1]-3.2), (a[0]+3.5, a[1]-3.5)]
        _claw_hand(h, e, GAUNT)
    if pose == "attack":
        for i in range(3):
            stroke([(40, 45+i*4-4), (45, 46+i*5-4)], LINE*0.5, g=EYE_R)


def _claw_hand(h, e, g):
    ang = math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))
    shape(ell(h[0], h[1], 2.0, 1.8, 12), g, LINE*0.7)
    for i in range(4):
        aa = math.radians(ang+(i-1.5)*18)
        p1 = (h[0]+math.cos(aa)*4.0, h[1]+math.sin(aa)*4.0)
        p2 = (p1[0]+math.cos(aa-0.7)*2.2, p1[1]+math.sin(aa-0.7)*2.2)
        stroke([h, p1], LINE*1.0, g=g); stroke([h, p1], LINE*0.4)
        stroke([p1, p2], LINE*0.7, g=SOCKET)


def _vamp_head(m):
    hood_b = bez((-9, -8), (-12, 2), (-9, 12), (0, 12.5)) + bez((0, 12.5), (7, 12.5), (10, 8), (10, 3))
    hd = bez((-3, -9), (-8, -6), (-7.5, 7), (0, 8.5)) + bez((0, 8.5), (5, 9), (8, 5), (8.2, 0)) + \
         bez((8.2, 0), (10.5, -2.5), (9, -5), (7.5, -6)) + bez((7.5, -6), (6.5, -10), (2, -11.5), (-3, -9))
    form(hood_b + [(9, -2), (4, -1), (-4, -10)], SHROUD, sh=0.15)
    form(hd, GAUNT, sdx=-2.2, sdy=1, sh=0.18)
    fill(ell(3.8, 1.4, 2.6, 2.0, 14), GAUNT_D)
    eye(4.4, 1.2, 1.15, EYE_R, 2.4)
    stroke(bez((1.5, 3.8), (3.5, 4.6), (5.5, 4.4), (7.0, 3.4)), LINE*0.9)
    stroke(bez((0, -2), (1.5, -4), (3, -5), (4.5, -5)), LINE*0.5)
    mo = bez((4.5, -5.5), (5.5, -6.5 - 2*m), (7.5, -7 - 2*m), (8.5, -5.8)) + [(6.5, -5.2)]
    shape(mo, MOUTH_D, LINE*0.7)
    for x in (5.6, 7.4):
        fill([(x-0.5, -5.4), (x+0.5, -5.4), (x, -7.6 - m)], TOOTH)
    hood_f = bez((10, 3), (11, 9), (6, 13.5), (-1, 13)) + bez((-1, 13), (3, 11.5), (7, 9), (8.5, 2))
    form(hood_f, SHROUD, sh=0.1)
    stroke(bez((-9, -8), (-12, 2), (-9, 12), (0, 12.5)), LINE)


NAV_SKIN = Col(0.8, "#c3d4de")
NAV_SKIN_D = Col(0.65, "#9db3c2")
NAV_DRESS = Col(0.88, "#dde5e8")
NAV_HAIR = Col(0.35, "#4e5b70")
NAV_HAIR_L = Col(0.45, "#66748a")

NVP = {
    "idle": dict(hip=(0, 38), lean=-3, hb=-9, hf=9, fh=(6, 14), nh=(9, 13), head=-3, sway=0, cast=False),
    "walk": dict(hip=(1, 39), lean=-10, hb=-14, hf=8, fh=(4, 12), nh=(12, 16), head=0, sway=5, cast=False),
    "attack": dict(hip=(-1, 38), lean=-6, hb=-12, hf=11, fh=(-8, 20), nh=(27, 27), head=4, sway=3, cast=True),
}


def navka(pose):
    q = NVP[pose]
    hip, lean, sw = q["hip"], q["lean"], q["sway"]
    with T(hip[0], hip[1], 1, rot=lean):
        hair = bez((-6, 40), (-14, 34), (-14 - sw, 12), (-17 - sw, -6)) + \
               [(-14 - sw, -2), (-12 - sw, -8), (-9 - sw*0.6, -1), (-6, 0)] + bez((-6, 0), (-6, 10), (-3, 24), (3, 31))
        form(hair, NAV_HAIR, sh=0.18)
        for k in range(5):
            stroke(bez((-5-k*1.6, 38-k), (-11-k*1.3, 30), (-11-k*1.2-sw, 12), (-12-k*1.0-sw, -3+k*1.5)), LINE*0.5, g=NAV_HAIR_L)
        limb((-1, 26), q["fh"], 13, 12, 3.8, 3.0, NAV_SKIN_D, -1)
    hb, hf = q["hb"], q["hf"]
    top_b = world(hip, lean, (-6, 27)); top_f = world(hip, lean, (6, 26))
    dr = bez(top_b, (top_b[0]-3, top_b[1]-10), (hb+1, 18), (hb, 0)) + \
         [(hb+2.5, 3), (hb+4.5, -1.5), (hb+7, 2.5), (hb+9.5, -2), (hb+12, 2), (hf-3, -1), (hf, 1)] + \
         bez((hf, 1), (hf+1, 14), (top_f[0]+3, top_f[1]-10), top_f) + [(top_f[0]-4, top_f[1]+3), (top_b[0]+4, top_b[1]+3)]
    form(dr, NAV_DRESS, sdx=-3.5, sdy=0.8, sh=0.16)
    for x in (-3, 1, 4):
        stroke(bez((x, 22), (x-1, 14), (x+1-sw*0.3, 8), (x-1-sw*0.5, 2)), LINE*0.45, g=COLD)
    for i, x in enumerate(range(int(hb)+1, int(hf), 3)):
        wisp_y = -1.5 - (i % 3)
        stroke([(x, 1.5), (x - sw*0.3 - 0.8, wisp_y - 2.5)], LINE*0.6, g=COLD_L, alpha=0.6)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(3, 33.5, 1, rot=q["head"]):
            _navka_head()
        a, e, h = limb((2, 26), q["nh"], 13, 12, 4.0, 3.2, NAV_SKIN, -1)
        shape(ell(h[0], h[1], 1.9, 1.5, 12), NAV_SKIN, LINE*0.7)
        if q["cast"]:
            glow(h[0]+3, h[1], 9, COLD, 0.22, 4)
            for k in range(6):
                aa = math.radians(k*60+15)
                stroke([(h[0]+3+math.cos(aa)*1.5, h[1]+math.sin(aa)*1.5), (h[0]+3+math.cos(aa)*5.5, h[1]+math.sin(aa)*5.5)], LINE*0.7, g=COLD_L)
            shape([(h[0]+6, h[1]-1.6), (h[0]+18, h[1]), (h[0]+6, h[1]+1.6)], COLD_L, LINE*0.6)
            dot(h[0]+3, h[1], 1.6, WHITE)


def _navka_head():
    r = 6.2
    hd = bez((-2, -6.5), (-7, -5), (-6.5, 6), (0, 7.5)) + bez((0, 7.5), (5, 7.5), (6.5, 3), (6.4, 0)) + \
         bez((6.4, 0), (7.2, -2), (6.5, -3.5), (5.6, -4)) + bez((5.6, -4), (4.5, -6.6), (1.5, -7.4), (-2, -6.5))
    form(hd, NAV_SKIN, sdx=-2, sdy=0.8, sh=0.14)
    fill(ell(3.2, 0.6, 1.8, 1.4, 12), NAV_SKIN_D)
    eye(3.6, 0.5, 0.9, EYE_C, 2.4)
    stroke(bez((1.8, 2.6), (3, 3.2), (4.2, 3.2), (5.2, 2.6)), LINE*0.6)
    stroke([(4.4, -3.8), (5.6, -3.6)], LINE*0.6)
    cap = bez((-6.8, -2), (-8, 5), (-3, 9.5), (2, 8.5)) + bez((2, 8.5), (5.5, 8), (7, 5), (6, 2.5)) + \
          bez((6, 2.5), (3, 5.5), (-1, 5), (-3.2, 1)) + [(-4.5, -4)]
    form(cap, NAV_HAIR, sh=0.12)
    for x0 in (-1, 2, 4.5):
        stroke(bez((x0, 8), (x0-1, 6.5), (x0-2.5, 5), (x0-3.5, 3)), LINE*0.45, g=NAV_HAIR_L)
    for i, x in enumerate((-4, -1, 2, 4.5)):
        shape(ell(x, 8.6+(i % 2)*0.4, 1.2, 0.9, 10), (Col(0.8, "#e8e0f0"), Col(0.75, "#b8d8a0"))[i % 2], LINE*0.4)
