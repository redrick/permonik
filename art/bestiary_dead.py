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


SKP = {  # a: arm swing, +1 = near arm back (near leg forward); sw: cloth trailing
    "idle": dict(lean=-4, hip=(0, 33.0), ff=(-6, 2.5), nf=(6, 2.5), head=0, jaw=0, a=0, sw=0),
    "walk": dict(lean=-8, hip=(0, 31.4), ff=(-9, 4.8), nf=(9, 2.5), head=-4, jaw=0, a=1, sw=-1),
    "walk2": dict(lean=-6.5, hip=(0, 32.9), ff=(-2.5, 8.5), nf=(0.5, 2.5), head=-1.5, jaw=1.5, a=0, sw=-3),
    "walk3": dict(lean=-8, hip=(0, 31.4), ff=(9, 2.5), nf=(-9, 4.8), head=-4, jaw=0, a=-1, sw=-1.5),
    "walk4": dict(lean=-6.5, hip=(0, 32.9), ff=(0.5, 2.5), nf=(-2.5, 8.5), head=-1.5, jaw=1.5, a=0, sw=-3.5),
    "windup": dict(lean=5, hip=(1, 32.5), ff=(-8, 2.5), nf=(9, 2.5), head=8, jaw=10, a=0, sw=1),
    "attack": dict(lean=-18, hip=(-2, 29.5), ff=(-15, 2.5), nf=(11, 2.5), head=-6, jaw=22, a=0, sw=-3),
}


def swing(q, back, fwd, mid=None):
    a = q["a"]
    if a == 0: return mid if mid is not None else tuple((b+f)/2 for b, f in zip(back, fwd))
    return back if a > 0 else fwd


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
    pose, v = view_of(pose)
    if v: return _havir_fb(pose, v == "b")

    def back(q):
        hx, hy = q["hip"]
        s = q["sw"]
        with T(hx, hy, 1, rot=q["lean"]):
            ap = bez((-4, 3), (-11, 1), (-12+s*0.6, -10), (-7+s, -15)) + [(-4+s, -13), (-2+s, -15), (1+s*0.5, -9)]
            form(ap, LEATHER, sh=0.18)

    def far(q):
        sh = (-1.5, 19)
        tgt = {"idle": (-4, 1), "windup": (8, 12), "attack": (17, 11)}.get(pose) or swing(q, (7, 6), (-8, 5), (-1, 2.5))
        skel_arm(sh, tgt, BONE_FAR)

    def torso(q):
        s = q["sw"]
        sm = bez((-4.5, 21.5), (-6.5, 16), (-6.5+s*0.3, 12), (-6+s*0.6, 9)) + rag_hem(-6+s*0.6, 3+s*0.3, 9, 3.5, 5, 1) + \
             [(3+s*0.3, 9), (2, 14), (5, 18), (6, 21)] + bez((6, 21), (3, 23), (-1, 23.5), (-4.5, 21.5))
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
        elif pose == "windup":
            h = (-3, 31)
            skel_arm(sh, h, BONE)
            pick((h[0]+8, h[1]-7), (h[0]-9, h[1]+11), 12)
        elif pose == "idle":
            h = (9, 7)
            skel_arm(sh, h, BONE)
            pick((h[0]-1, h[1]-36), (h[0]+1, h[1]+16), 11)
        else:
            h = swing(q, (-2, 7), (9, 6), (4, 5))
            skel_arm(sh, h, BONE)
            d = swing(q, ((-12, -10), (9, 15)), ((-14, -7), (6, 18)), ((-13, -9), (8, 17)))
            pick((h[0]+d[0][0], h[1]+d[0][1]), (h[0]+d[1][0], h[1]+d[1][1]), 11)
    skeleton(pose, EYE_Y, back, torso, near, far, hat)


def kostlivy_kusinik(pose):
    pose, v = view_of(pose)
    if v: return _kusinik_fb(pose, v == "b")

    def far(q):
        sh = (-1.5, 19)
        tgt = {"idle": (10, 9), "windup": (16, 17), "attack": (19, 22)}.get(pose) or swing(q, (11.5, 10.5), (9, 9.5), (10, 11))
        skel_arm(sh, tgt, BONE_FAR)
        rr = rrect(-9, -2, 4.2, 12, 1.5)
        with T(0, 0, 1, rot=12-q["sw"]*1.5):
            form(rr, LEATHER_D, sh=0.15)
            for i in range(3):
                stroke([(-8+i*1.2, 9.5), (-8.5+i*1.2, 14)], LINE*0.8, g=WOOD)
                fill([(-9+i*1.2, 13.5), (-7.6+i*1.2, 13.5), (-8.3+i*1.2, 15.5)], RAG)

    def torso(q):
        s = q["sw"]*0.6
        tb = bez((-5, 22), (-7.5, 15), (-7+s*0.5, 8), (-6.5+s, 3)) + rag_hem(-6.5+s, 7+s, 3, 4, 6, 3) + \
             bez((7+s, 3), (6, 10), (7, 16), (6.5, 22)) + bez((6.5, 22), (3, 23.5), (-2, 23.5), (-5, 22))
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
        elif pose == "windup":
            h = (9, 17)
            skel_arm(sh, h, BONE)
            crossbow((h[0]-5, h[1]), 8, True)
        elif pose == "idle":
            h = (6, 9)
            skel_arm(sh, h, BONE)
            crossbow((h[0]-2, h[1]+1), -28, True)
        else:
            h = swing(q, (6, 9.5), (8, 10.5), (7, 11))
            skel_arm(sh, h, BONE)
            crossbow((h[0]-2, h[1]+1), swing(q, (-21,), (-15,), (-18,))[0], True)
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
    pose, v = view_of(pose)
    if v:
        with T(0, 0, 1.12):
            return _kostej_fb(pose, v == "b")

    def back(q):
        hx, hy = q["hip"]
        with T(hx, hy, 1, rot=q["lean"]):
            sw = {"idle": 0, "walk": -2, "walk2": -3.5, "walk3": -1.5, "walk4": -4, "windup": -5, "attack": -8}[pose]
            cl = bez((-4, 25), (-12, 18), (-14+sw, 6), (-16+sw, -16)) + rag_hem(-16+sw, -2+sw*0.3, -16, 4, 7, 2) + \
                 bez((-2+sw*0.3, -16), (-4, -4), (2, 10), (4, 24))
            form(cl, VIOLET, sh=0.2)

    def far(q):
        sh = (-1.5, 19)
        tgt = {"idle": (2, 8), "windup": (7, 13), "attack": (-10, 12)}.get(pose) or swing(q, (6, 7), (-6, 6), (0, 5.5))
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
        elif pose == "windup":
            h = (-3, 30)
            skel_arm(sh, h, BONE)
            sword(h, 125)
        elif pose == "idle":
            h = (9, 10)
            skel_arm(sh, h, BONE)
            sword(h, -60)
        else:
            h = swing(q, (4, 11), (11, 12), (8, 11))
            skel_arm(sh, h, BONE)
            sword(h, swing(q, (-55,), (-32,), (-45,))[0])
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


# ------------------------------------------------------------------ skeletons from the front / back
LFB = {  # per leg (-x, +x): knee, ankle, foot scale (a foot toward the viewer is lower and bigger)
    "stand": (((-4.4, 17), (-5, 3), 1.0), ((4.4, 17), (5, 3), 1.0)),
    "c1": (((-4.2, 17.6), (-4.6, 4.8), 0.9), ((5.0, 16.0), (5.6, 1.6), 1.1)),
    "p1": (((-4.3, 17.2), (-4.7, 3), 1.0), ((5.4, 20.5), (4.8, 9.5), 1.05)),
    "brace": (((-7.5, 16.5), (-9.5, 3), 1.0), ((7.5, 16.5), (9.5, 3), 1.0)),
    "lunge": (((-6.5, 18), (-8, 4.6), 0.92), ((7.5, 15), (8.8, 1.2), 1.12)),
}

SKF = {  # a: +1 = the +x leg steps toward the viewer (so the -x arm swings forward)
    "idle": dict(hip=33, legs="stand", a=0, jaw=0, hd=0, sw=0),
    "walk": dict(hip=31.6, legs="c1", a=1, jaw=0, hd=-0.4, sw=1),
    "walk2": dict(hip=33, legs="p1", a=0, jaw=1.5, hd=0.3, sw=0.4),
    "walk3": dict(hip=31.6, legs="c2", a=-1, jaw=0, hd=-0.4, sw=-1),
    "walk4": dict(hip=33, legs="p2", a=0, jaw=1.5, hd=0.3, sw=-0.4),
    "windup": dict(hip=32.4, legs="brace", a=0, jaw=10, hd=0.5, sw=0),
    "attack": dict(hip=30.6, legs="lunge", a=0, jaw=22, hd=-1.5, sw=0),
}


def legs_fb(ph):
    m = {"c2": "c1", "p2": "p1"}
    if ph in m:
        l, r = LFB[m[ph]]
        return tuple(((-k[0], k[1]), (-a[0], a[1]), s) for k, a, s in (r, l))
    return LFB[ph]


def arm_hang(q, sx, back=False):
    f = -sx*q["a"]
    return (sx*(10.5-0.6*abs(f)), -4+3.5*abs(f)), (f >= 0) != back


def arm_out(sh, h, g, sx, l1=12, l2=11.5, w=2.2):
    d = math.hypot(h[0]-sh[0], h[1]-sh[1])
    if h[1] < sh[1]-12 and d < (l1+l2)*0.97:
        k = d/((l1+l2)*0.97); l1, l2 = l1*k, l2*k
    b = max((1, -1), key=lambda b: sx*ik(sh, h, l1, l2, b)[1][0])
    return skel_arm(sh, h, g, l1, l2, w, b)


BONE_BACK = Col(0.72, "#bfb391")


def skull_fb(r, jaw=0, eyecol=EYE_G, g=BONE, back=False):
    if back:
        for sx in (-1, 1):
            shape(ell(sx*0.48*r, -0.82*r, 0.2*r, 0.32*r, 10), g, LINE*0.7)
        cr = ell(0, 0.1*r, 0.97*r, 1.0*r, 30)
        form(cr, BONE_BACK, sdx=-r*0.25, sdy=r*0.25, sh=0.2)
        hatch(cr, 1.4, 35, 0.4, 0.0, 0.3)
        stroke(bez((0.55*r, 0.2*r), (0.4*r, -0.05*r), (0.5*r, -0.25*r), (0.3*r, -0.45*r)), LINE*0.45)
        stroke(bez((-0.45*r, 0.95*r), (-0.15*r, 0.6*r), (0.2*r, 0.85*r), (0.3*r, 0.35*r)), LINE*0.5)
        stroke(bez((-0.72*r, -0.5*r), (-0.3*r, -0.72*r), (0.3*r, -0.72*r), (0.72*r, -0.5*r)), LINE*0.6)
        return
    j = jaw*0.03*r
    if jaw > 4:
        fill(rrect(-0.42*r, -0.8*r-j, 0.84*r, j+0.25*r, 0.1*r), SOCKET)
    md = [(-0.56*r, -0.5*r)] + bez((-0.56*r, -0.62*r-j), (-0.62*r, -1.02*r-j), (-0.3*r, -1.2*r-j), (0, -1.2*r-j)) + \
        bez((0, -1.2*r-j), (0.3*r, -1.2*r-j), (0.62*r, -1.02*r-j), (0.56*r, -0.62*r-j)) + [(0.56*r, -0.5*r)]
    shape(md, g, LINE*0.9)
    for i in range(5):
        x = -0.34*r+i*0.17*r
        stroke([(x, -0.68*r-j), (x, -0.84*r-j)], LINE*0.45)
    hd = bez((-0.58*r, -0.66*r), (-0.75*r, -0.4*r), (-1.0*r, -0.1*r), (-0.95*r, 0.3*r)) + \
        bez((-0.95*r, 0.3*r), (-0.92*r, 1.12*r), (0.92*r, 1.12*r), (0.95*r, 0.3*r)) + \
        bez((0.95*r, 0.3*r), (1.0*r, -0.1*r), (0.75*r, -0.4*r), (0.58*r, -0.66*r))
    form(hd, g, sdx=0, sdy=r*0.14, sh=0.16)
    for sx in (-1, 1):
        fill(ell(sx*0.38*r, 0.04*r, 0.27*r, 0.3*r, 16), SOCKET)
        eye(sx*0.38*r, 0.02*r, 0.12*r, eyecol)
        stroke(bez((sx*0.72*r, -0.2*r), (sx*0.6*r, -0.36*r), (sx*0.45*r, -0.4*r), (sx*0.3*r, -0.38*r)), LINE*0.45)
    fill([(0, -0.14*r), (-0.13*r, -0.42*r), (0.13*r, -0.42*r)], SOCKET)
    stroke([(-0.5*r, -0.64*r), (0.5*r, -0.64*r)], LINE*0.6)
    for i in range(5):
        x = -0.34*r+i*0.17*r
        stroke([(x, -0.64*r), (x, -0.5*r)], LINE*0.45)


def ribs_fb(neck, w=10, g=BONE, back=False, n=5):
    for i in range(4):
        shape(ell(0, 1.5+i*2.1, 1.5, 1.0, 10), g, LINE*0.6)
    for i in range(n):
        y = neck-3.5-i*2.2
        ww = w*(0.78+0.22*math.sin(math.pi*(i+1)/(n+1)))
        for sx in (-1, 1):
            tube(bez((sx*1.2, y+0.5), (sx*ww*0.6, y+1.8), (sx*ww*1.05, y+0.2), (sx*ww*0.9, y-3.2)), 1.8, 1.2, g, lw=LINE*0.8, sh=0)
    if back:
        for i in range(6):
            shape(ell(0, neck-1.5-i*2.2, 1.3, 0.9, 10), g, LINE*0.6)
        for sx in (-1, 1):
            sc = [(sx*2.5, neck-1.5), (sx*7.5, neck-1.0), (sx*5.5, neck-9)]
            form(sc, g, sdx=0, sdy=0.6, sh=0.15)
    else:
        bone((0, neck-1.5), (0, neck-10.5), 2.4, g, knob=False)
    for sx in (-1, 1):
        tube([(sx*1, neck-0.5), (sx*8, neck-1.4)], 1.6, 1.4, g, sh=0)
    bone((0, neck-1), (0, neck+2.5), 2.0, g, knob=False)


def pelvis_fb(g=BONE, back=False):
    for sx in (-1, 1):
        p = bez((sx*1.2, 2.5), (sx*4.5, 4.5), (sx*7, 2.5), (sx*6.2, -0.5)) + \
            bez((sx*6.2, -0.5), (sx*5.5, -2.5), (sx*3, -3.8), (sx*1.2, -3))
        form(p, g, sdx=0, sdy=0.8, sh=0.15)
        if not back: fill(ell(sx*2.8, -1.8, 0.9, 1.0, 10), SOCKET)
    shape([(-1.6, 3), (1.6, 3), (0.8, -3.5), (-0.8, -3.5)], g, LINE*0.7)


def skel_foot_fb(a, sc, g, back):
    with T(a[0], a[1], sc):
        if back:
            shape(ell(0, -1.2, 1.9, 1.7, 12), g, LINE*0.8)
            return
        shape(ell(0, -0.6, 2.3, 1.5, 14), g, LINE*0.8)
        for i in range(4):
            x = -1.8+i*1.2
            p = [(x, -1.4), (x*1.3, -3.0)]
            stroke(p, LINE*1.1, g=g); stroke(p, LINE*0.4)


def skel_fb(q, back, eyecol, hands, torso=None, hat=None, worn=None, behind=None, front=None, neck=21, arm=(12, 11.5)):
    """hands: {sx: (target, in front of the body)}; behind/front(q, H) draw what the hands hold"""
    hy = q["hip"]
    if worn and not back:
        with T(0, hy): worn(q, back)
    for (k, a, s), sx in sorted(zip(legs_fb(q["legs"]), (-1, 1)), key=lambda t: t[0][2]):
        g = BONE_FAR if s < 0.97 else BONE
        hp = (sx*3.8, hy-1.5)
        bone(hp, k, 2.6, g); bone(k, a, 2.2, g)
        skel_foot_fb(a, s, g, back)
    H = {sx: t for sx, (t, _) in hands.items()}
    with T(0, hy):
        if behind: behind(q, H)
        for sx, (t, fr) in hands.items():
            if not fr: arm_out((sx*8, neck-1.7), t, BONE_FAR, sx, *arm)
        pelvis_fb(BONE, back)
        ribs_fb(neck, 10, BONE, back)
        if torso: torso(q, back)
        for sx, (t, fr) in hands.items():
            if fr: arm_out((sx*8, neck-1.7), t, BONE, sx, *arm)
        with T(0, neck+6.5+q["hd"], 1, rot=q.get("tilt", 0)):
            skull_fb(6.4, q["jaw"], eyecol, back=back)
            if hat: hat(q, back)
        if worn and back: worn(q, back)
        if front: front(q, H)


def _hands(q, back, **over):
    out = {sx: arm_hang(q, sx, back) for sx in (-1, 1)}
    for k, v in over.items():
        out[-1 if k == "l" else 1] = v
    return out


def _havir_fb(pose, back):
    q = SKF[pose]
    s = q["sw"]

    def worn(q, back):
        if not back: return
        ap = [(-6, 2)] + bez((-6, 2), (-7+s*0.4, -6), (-6.5+s, -12), (-4+s, -14.5)) + [(-1+s, -13.5), (1.5+s, -15), (4+s, -13.5)] + \
            bez((4+s, -13.5), (6.5+s, -12), (7+s*0.4, -6), (6, 2))
        form(ap, LEATHER, sdx=0, sdy=1, sh=0.18)
        stroke(bez((-5.5, 0.5), (-2, -1), (2, -1), (5.5, 0.5)), LINE*0.6, g=LEATHER_D)

    def torso(q, back):
        if back:
            sm = [(-8.8, 21.5)] + bez((-8.8, 21.5), (-10, 16), (-9.5, 12), (-8.5+s*0.5, 9)) + rag_hem(-8.5+s*0.5, 8.5+s*0.5, 9, 3.5, 8, 2) + \
                bez((8.5+s*0.5, 9), (9.5, 12), (10, 16), (8.8, 21.5)) + bez((8.8, 21.5), (4, 23.5), (-4, 23.5), (-8.8, 21.5))
            form(sm, RAG, sdx=0, sdy=1.2, sh=0.2)
            hatch(sm, 1.8, 50, 0.4, 0.0, 0.4)
            stroke([(0, 22.5), (0.3, 9.5)], LINE*0.5, g=RAG_D)
        else:
            for sx in (-1, 1):
                p = [(sx*1.5, 22.5)] + bez((sx*1.5, 22.5), (sx*5, 23), (sx*9, 22.5), (sx*9.5, 19)) + \
                    bez((sx*9.5, 19), (sx*10, 15), (sx*9.5, 12), (sx*(8.5-s*0.4*sx), 9))
                p += rag_hem(sx*(8.5-s*0.4*sx), sx*2.5, 9, 3.5, 4, 1 if sx > 0 else 3) + [(sx*3, 14), (sx*1.8, 18)]
                form(p, RAG, sdx=0, sdy=1.2, sh=0.2)
                hatch(p, 1.8, 50*sx, 0.4, 0.0, 0.4)
        shape(rrect(-7, -1.5, 14, 3, 1.2), LEATHER_D, LINE*0.8)
        with T(7.2, -2.5, 1, rot=-s*4):
            stroke([(0, 1), (0, -2)], LINE*0.7)
            shape([(-2, -2), (2, -2), (2.6, -6), (-2.6, -6)], IRON_D, LINE*0.7)
            glow(0, -5, 4, FLAME, 0.2, 3)
            fill(ell(0, -4.2, 0.9, 1.6, 10), FLAME)

    def hat(q, back):
        cap = bez((-6.8, 2.5), (-7.6, 10.5), (7.6, 10.5), (6.8, 2.5)) + bez((6.8, 2.5), (3, 1.6), (-3, 1.6), (-6.8, 2.5))
        form(cap, LEATHER, sdx=0, sdy=1, sh=0.2)
        stroke(bez((-6.8, 2.6), (-3, 1.8), (3, 1.8), (6.8, 2.6)), LINE*0.7)
        if back:
            stroke(bez((0, 9.5), (0.3, 7), (-0.3, 5), (0, 2.5)), LINE*0.5, g=LEATHER_D)
        else:
            shape(rrect(-1.2, 2.5, 2.4, 3.6, 0.6), IRON, LINE*0.6)

    if pose == "idle":
        hands = _hands(q, back, r=((10, 1), not back))
        def held(q, H):
            h = H[1]; pick((h[0]+0.5, h[1]-31), (h[0]+1, h[1]+16), 9)
    elif pose == "windup":
        hands = _hands(q, back, r=((8, 33), True), l=((-12, 5), not back))
        def held(q, H):
            h = H[1]; pick((h[0]+2, h[1]-5), (h[0]-8, h[1]+12), 10)
    elif pose == "attack":
        hands = _hands(q, back, r=((3, 6), not back), l=((-12, 9), True))
        def held(q, H):
            h = H[1]; pick((h[0]-1, h[1]+7), (h[0]+1, h[1]-15), 10)
    else:
        hands = _hands(q, back)
        h = hands[1][0]
        hands[1] = ((h[0]-0.5, h[1]+1.5), hands[1][1])
        def held(q, H):
            h = H[1]; pick((h[0]-1, h[1]-8), (h[0]+4, h[1]+26), 9)
    in_front = hands[1][1] if pose != "windup" else back
    with T(0, 0, 1, flip=back):
        skel_fb(q, back, EYE_Y, hands, torso, hat, worn, None if in_front else held, held if in_front else None)
        if pose == "attack":
            swoosh(bez((12, 78), (19, 62), (15, 42), (4, 22)), 2.6, WHITE, 0.3)


def _kusinik_fb(pose, back):
    q = SKF[pose]
    s = q["sw"]

    def worn(q, back):
        with T(-8.5 if not back else -5.5, 4, 1, rot=-8+s*3):
            if back:
                for i in range(3):
                    stroke([(-1+i*1.2, 5.5), (-1.3+i*1.2, 10)], LINE*0.8, g=WOOD)
                    fill([(-2+i*1.2, 9.5), (-0.6+i*1.2, 9.5), (-1.3+i*1.2, 11.5)], RAG)
            form(rrect(-2.1, -6, 4.2, 12, 1.5), LEATHER_D, sdx=0, sdy=0.8, sh=0.15)
            stroke([(-2.1, 3.5), (2.1, 3.5)], LINE*0.6)
            if not back:
                for i in range(3):
                    stroke([(-1+i*1.2, 5.5), (-1.3+i*1.2, 10)], LINE*0.8, g=WOOD)
                    fill([(-2+i*1.2, 9.5), (-0.6+i*1.2, 9.5), (-1.3+i*1.2, 11.5)], RAG)
        if back:
            stroke(bez((-8, 21), (-4, 14), (-2, 9), (-5.5, 7)), LINE*0.9, g=LEATHER_D)

    def torso(q, back):
        tb = [(-8.5, 21.5)] + bez((-8.5, 21.5), (-10, 15), (-8.5, 8), (-8+s*0.5, 3)) + rag_hem(-8+s*0.5, 8+s*0.5, 3, 4, 8, 3) + \
            bez((8+s*0.5, 3), (8.5, 8), (10, 15), (8.5, 21.5)) + bez((8.5, 21.5), (4, 23.5), (-4, 23.5), (-8.5, 21.5))
        form(tb, RUST_D, sdx=0, sdy=1.2, sh=0.2)
        for x in ((-3, 0, 3) if not back else (-2.5, 2.5)):
            stroke([(x, 22.5), (x*1.1, 4)], LINE*0.45)
        if not back:
            shape(bez((-4, 23), (-2, 20.5), (2, 20.5), (4, 23)), SOCKET, LINE*0.6)
        shape(rrect(-8, -0.5, 16, 3, 1.2), LEATHER_D, LINE*0.8)

    def hat(q, back):
        dome = bez((-6, 4.2), (-6.5, 12.5), (6.5, 12.5), (6, 4.2))
        form(dome + [(0, 4.0)], RUST, sdx=0, sdy=1, sh=0.2)
        brim = ell(0, 3.8, 10.5, 2.0, 30)
        form(brim, RUST, sdx=0, sdy=0.6, sh=0.14)
        stroke(bez((-6, 4.6), (-2, 5.6), (2, 5.6), (6, 4.6)), LINE*0.5)
        for x in (-3, 0, 3): dot(x, 6.8, 0.45, RUST_D)

    def prod(y, w, bend):
        for sx in (-1, 1):
            arm = bez((0, y), (sx*w*0.4, y+bend*0.2), (sx*w*0.8, y-bend*0.2), (sx*w, y-bend))
            tube(arm, 1.8, 1.2, IRON, lw=LINE*0.7, sh=0)
        stroke([(-w, y-bend), (0, y-bend-2.5), (w, y-bend)], LINE*0.45, g=BONE)

    if pose in ("windup", "attack"):
        y = 22 if pose == "attack" else 13
        hands = {}

        def bow_aim(q, H):
            for sx in (-1, 1):
                el = (sx*13, y-6)
                bone((sx*8, 19.3), el, 2.2, BONE if not back else BONE_FAR)
                bone(el, (sx*3.5, y-1.5), 1.9, BONE if not back else BONE_FAR)
            if not back:
                shape(rrect(-1.8, y-5, 3.6, 5, 0.8), WOOD, LINE*0.7)
            prod(y, 15 if back else 12.5, 2.5)
            if not back:
                shape(ell(0, y+0.3, 1.5, 1.5, 12), WOOD, LINE*0.6)
                shape([(-1.0, y+0.3), (0, y+1.6), (1.0, y+0.3), (0, y-1.0)], IRON, LINE*0.5)
                if pose == "attack":
                    for a in range(0, 360, 45):
                        c, si = math.cos(math.radians(a+20)), math.sin(math.radians(a+20))
                        stroke([(c*15, y+si*9), (c*18, y+si*11)], LINE*0.6, g=WHITE)
        q = dict(q, jaw=0 if pose == "windup" else 6)
        with T(0, 0, 1, flip=back):
            skel_fb(q, back, EYE_R, hands, torso, hat, worn, bow_aim if back else None, None if back else bow_aim)
        return
    hands = _hands(q, back, r=((7, 3+(1.5 if q["a"] else 0)), not back), l=((-2, 12), not back))

    def bow_port(q, H):
        h = H[1]
        crossbow((h[0]+1, h[1]-0.5), 128 + (6*q["a"] if q["a"] else 0), True)
    with T(0, 0, 1, flip=back):
        skel_fb(q, back, EYE_R, hands, torso, hat, worn, bow_port if back else None, None if back else bow_port)


def _kostej_fb(pose, back):
    q = SKF[pose]
    s = q["sw"]

    def worn(q, back):
        if back:
            cl = [(-7, 23)] + bez((-7, 23), (-11, 18), (-13, 4), (-14+s, -15)) + rag_hem(-14+s, 14+s, -15, 4, 10, 2) + \
                bez((14+s, -15), (13, 4), (11, 18), (7, 23)) + bez((7, 23), (3, 21.5), (-3, 21.5), (-7, 23))
            form(cl, VIOLET, sdx=0, sdy=1.4, sh=0.2)
            for x in (-6, -1.5, 3, 7.5):
                stroke(bez((x*0.4, 20), (x*0.8, 10), (x+s*0.5, 0), (x*1.05+s, -12)), LINE*0.5, g=VIOLET_L)
            shape(bez((-7.5, 23.5), (-3, 20), (3, 20), (7.5, 23.5)) + bez((7.5, 23.5), (3, 25), (-3, 25), (-7.5, 23.5)), VIOLET_L, LINE*0.7)
        else:
            cl = [(-8, 22)] + bez((-8, 22), (-13, 16), (-14, 4), (-15+s, -15)) + rag_hem(-15+s, 15+s, -15, 4, 10, 2) + \
                bez((15+s, -15), (14, 4), (13, 16), (8, 22))
            form(cl, VIOLET, sdx=0, sdy=1.4, sh=0.25)

    def torso(q, back):
        mail = [(-8, 6), (8, 6)] + rag_hem(8, -8, -5, 2.5, 9, 4)
        form(mail, IRON_D, sdx=0, sdy=1, sh=0.15)
        hatch(mail, 1.2, 60, 0.35, 0.0, 0.5); hatch(mail, 1.2, -60, 0.35, 0.0, 0.5)
        cu = bez((-8.5, 22), (-10.5, 16), (-9.5, 9), (-7, 3)) + bez((-7, 3), (-3, 1.5), (3, 1.5), (7, 3)) + \
            bez((7, 3), (9.5, 9), (10.5, 16), (8.5, 22)) + (bez((8.5, 22), (4, 21.5), (2.5, 19), (0, 19)) + bez((0, 19), (-2.5, 19), (-4, 21.5), (-8.5, 22)) if not back
                                                            else bez((8.5, 22), (4, 23.5), (-4, 23.5), (-8.5, 22)))
        form(cu, RUST, sdx=0, sdy=1.2, sh=0.2)
        if back:
            stroke([(0, 22.5), (0, 3)], LINE*0.5)
        else:
            stroke(bez((0, 18.5), (0.4, 12), (-0.4, 7), (0, 2)), LINE*0.6)
        for p in ((-6, 19), (6, 19), (-5.5, 5), (5.5, 5)): dot(p[0], p[1], 0.5, IRON_D)
        for sx in (-1, 1):
            pa = ell(sx*8.5, 20.5, 3.6, 3.0, 16)
            form(pa, RUST, sdx=0, sdy=0.8, sh=0.2)

    def hat(q, back):
        mail = bez((-7.2, 2), (-8.5, -3), (-7.5, -7), (-4.5, -9)) + bez((4.5, -9), (7.5, -7), (8.5, -3), (7.2, 2)) if back else None
        if back:
            form(mail, IRON_D, sdx=0, sdy=0.8, sh=0.1)
            hatch(mail, 1.1, 60, 0.35, 0.0, 0.5)
        else:
            for sx in (-1, 1):
                m = [(sx*6.5, 2), (sx*8.4, -6), (sx*5.2, -9), (sx*4.2, -4.5), (sx*5.2, 1)]
                form(m, IRON_D, sdx=0, sdy=0.6, sh=0.1)
                hatch(m, 1.1, 60*sx, 0.35, 0.0, 0.5)
        hm = bez((-7.4, 1.8), (-7.8, 7.5), (-3, 9.5), (0, 14)) + bez((0, 14), (3, 9.5), (7.8, 7.5), (7.4, 1.8)) + \
            bez((7.4, 1.8), (3, 3.0), (-3, 3.0), (-7.4, 1.8))
        form(hm, RUST, sdx=0, sdy=1, sh=0.2)
        for x in (-3.5, 3.5):
            stroke(bez((0, 13.5), (x*0.4, 10), (x*0.8, 6), (x, 2.8)), LINE*0.5)
        shape(rrect(-7.8, 1.2, 15.6, 2.4, 1), IRON_D, LINE*0.7)
        if not back:
            shape([(-0.7, 2), (0.7, 2), (0.6, -3.6), (-0.6, -3.6)], IRON, LINE*0.6)
        glow(0, 14.5, 3.5, EYE_G, 0.12, 3)

    def shield(h, rim=False):
        with T(h[0], h[1]):
            if rim:
                sd = ell(0, 0, 2.6, 9.5, 24)
                form(sd, RUST_D, sdx=0.8, sdy=0, sh=0.25)
                return
            form(ell(0, 0, 8, 9.5, 30), RUST_D, sdx=0, sdy=1, sh=0.2)
            stroke(ell(0, 0, 6.2, 7.6, 30), LINE*0.6, closed=True)
            shape(ell(0, 0, 2.0, 2.0, 14), IRON, LINE*0.7)

    if pose == "windup":
        hands = _hands(q, back, r=((9, 32), True), l=((-6, 10), not back))
        sw_ang, sw_front = 112, back
    elif pose == "attack":
        hands = _hands(q, back, r=((-2, 8), not back), l=((-13, 9), not back))
        sw_ang, sw_front = -152, not back
    elif pose == "idle":
        hands = _hands(q, back, r=((10.5, 0), not back), l=((-9.5, 2), not back))
        sw_ang, sw_front = -78, not back
    else:
        hands = _hands(q, back)
        f = -q["a"]
        hands[-1] = ((-9.5+abs(q["a"])*0.5, 2+2.5*max(0, -f)), not back)
        sw_ang, sw_front = -78+8*f, hands[1][1]

    def held_b(q, H):
        if not sw_front: sword(H[1], sw_ang)
        if back: shield((H[-1][0]-2.5, H[-1][1]+2), True)

    def held_f(q, H):
        if not back: shield(H[-1])
        if sw_front: sword(H[1], sw_ang)
        if not back: glow(0, 14, 6, EYE_G, 0.07, 3)
    with T(0, 0, 1, flip=back):
        skel_fb(q, back, EYE_G, hands, torso, hat, worn, held_b, held_f)
        if pose == "attack":
            swoosh(bez((22, 50), (20, 30), (2, 10), (-22, 2)), 2.8, EYE_G, 0.3)


DROWN = Col(0.6, "#90a794")
DROWN_D = Col(0.5, "#728b79")
WEED = Col(0.4, "#56692f")
WEED_L = Col(0.5, "#7d9142")
SHIRT_W = Col(0.5, "#6a7c8c")
TROUS = Col(0.4, "#5b5968")

UTP = {
    "idle": dict(hip=(0, 36), lean=-10, ff=(-7, 2), nf=(8, 2), fh=(13, 3), nh=(16, 5), head=-8, mouth=0.45),
    "walk": dict(hip=(0, 35), lean=-14, ff=(-10, 3.5), nf=(10, 2), fh=(20, 9), nh=(6, 3), head=-6, mouth=0.45, sw=-1),
    "walk2": dict(hip=(0, 36.4), lean=-12, ff=(-3, 8), nf=(0.5, 2), fh=(15, 6), nh=(13, 5), head=-4, mouth=0.55, sw=-3),
    "walk3": dict(hip=(0, 35), lean=-14, ff=(10, 2), nf=(-10, 3.5), fh=(7, 2), nh=(20, 9), head=-6, mouth=0.45, sw=-1.5),
    "walk4": dict(hip=(0, 36.4), lean=-12, ff=(0.5, 2), nf=(-3, 8), fh=(12, 4), nh=(16, 7), head=-4, mouth=0.55, sw=-3.5),
    "windup": dict(hip=(1, 35.5), lean=-3, ff=(-9, 2), nf=(9, 2), fh=(12, 33), nh=(17, 32), head=10, mouth=0.8),
    "attack": dict(hip=(-3, 33.5), lean=-22, ff=(-17, 2), nf=(11, 2), fh=(27, 21), nh=(30, 15), head=4, mouth=1.0),
}


def utopenec(pose):
    pose, v = view_of(pose)
    if v: return _utopenec_fb(pose, v == "b")
    q = UTP[pose]
    s = q.get("sw", 0)
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
            tube(bez((x0, y0), (x0-2+s*0.3, (y0+y1)/2+3), (x1+2+s*0.7, (y0+y1)/2), (x1+s, y1)), 2.2, 0.7, WEED, lw=LINE*0.6, sh=0)
    limb((hip[0]+2, hip[1]), q["nf"], 18, 17, 9, 7, TROUS, 1)
    bare_foot(q["nf"], DROWN, 7.5)
    with T(hip[0], hip[1], 1, rot=lean):
        with T(4, 33, 1, rot=q["head"]):
            _drowned_head(q["mouth"], s)
        a, e, h = limb((2, 25), q["nh"], 15, 14, 7, 6, DROWN, -1)
        mitt(*_hand_end((2, 25), q["nh"], 15, 14), 2.8, DROWN, claw=None)
        tube(bez(e, (e[0]+1, e[1]-4), (e[0]-1+s*0.4, e[1]-7), (e[0]+0.5+s*0.8, e[1]-10)), 1.8, 0.5, WEED, lw=LINE*0.5, sh=0)
        drip(h[0]+4, h[1]-4.5); drip(h[0]+1, h[1]-6.5, 0.6)
    if pose == "attack":
        for i in range(3):
            stroke([(36, 30+i*4-4), (41, 31+i*5-4)], LINE*0.5, g=COLD_L)


def _hand_end(a, c, l1, l2):
    _, e, h = ik(a, c, l1, l2, -1)
    return h[0], h[1], math.degrees(math.atan2(h[1]-e[1], h[0]-e[0]))


def _drowned_head(m, s=0):
    r = 8.2
    tube(bez((-5, -3), (-7, -8), (-9+s*0.5, -12), (-12+s, -16)), 2.6, 0.6, WEED, lw=LINE*0.6, sh=0)
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
        tube(bez((x0, y0), (x0-1, y0-1.5), (x1+1+s*0.4, y1+2), (x1+s*0.7, y1)), 2.2, 0.6, WEED_L if x0 > 0 else WEED, lw=LINE*0.6, sh=0)
    drip(6.8, -9.5, 0.7)


UTF = {  # hands (-x, +x): (pos, scale); bigger = nearer the viewer
    "idle": dict(hip=36, legs="stand", h=(((-8.5, 5), 1.0), ((8.5, 5), 1.0)), hd=0, mouth=0.45, sw=0),
    "walk": dict(hip=35, legs="c1", h=(((-7.5, 7.5), 1.15), ((10, 3), 0.9)), hd=-0.5, mouth=0.45, sw=1.2),
    "walk2": dict(hip=36.4, legs="p1", h=(((-8, 6), 1.05), ((9.2, 4.5), 0.95)), hd=0.5, mouth=0.55, sw=0.4),
    "walk3": dict(hip=35, legs="c2", h=(((-10, 3), 0.9), ((7.5, 7.5), 1.15)), hd=-0.5, mouth=0.45, sw=-1.2),
    "walk4": dict(hip=36.4, legs="p2", h=(((-9.2, 4.5), 0.95), ((8, 6), 1.05)), hd=0.5, mouth=0.55, sw=-0.4),
    "windup": dict(hip=35.5, legs="brace", h=(((-15, 41), 1.0), ((15, 40), 1.0)), hd=2, mouth=0.8, sw=0),
    "attack": dict(hip=33.5, legs="lunge", h=(((-8, 13), 1.35), ((8.5, 14), 1.4)), hd=-3.5, mouth=1.0, sw=0),
}


def foot_fb(x, y, sc, g, back, w=3.4):
    with T(x, y, sc):
        if back:
            shape(ell(0, 1.8, w*0.75, 2.0, 14), g, LINE*0.8)
            return
        shape(bez((-w, 1.5), (-w, 4), (w, 4), (w, 1.5)) + bez((w, 1.5), (w, -0.3), (-w, -0.3), (-w, 1.5)), g, LINE*0.8)
        for i in range(4):
            xx = -w*0.65+i*w*0.43
            stroke([(xx, 0.6), (xx, -0.1)], LINE*0.5)


def _utopenec_head_fb(m, back, s):
    hd = bez((0, 9), (7, 9), (9, 4), (8.6, -1)) + bez((8.6, -1), (8.2, -6), (4.5, -9.5), (0, -9.5)) + \
        bez((0, -9.5), (-4.5, -9.5), (-8.2, -6), (-8.6, -1)) + bez((-8.6, -1), (-9, 4), (-7, 9), (0, 9))
    if back:
        form(hd, DROWN_D, sdx=0, sdy=1, sh=0.16)
        for i, x in enumerate((-7, -4.5, -2, 0.5, 3, 5.5, 7.5)):
            tube(bez((x*0.6, 8.5), (x*0.9, 3), (x+s*0.5, -4), (x*1.1+s, -12-(i % 3)*2)), 2.4, 0.6, (WEED, WEED_L)[i % 2], lw=LINE*0.6, sh=0)
        return
    for sx in (-1, 1):
        tube(bez((sx*6, 5), (sx*9, 0), (sx*9.5+s*0.5, -6), (sx*10+s, -13)), 2.6, 0.6, WEED, lw=LINE*0.6, sh=0)
    form(hd, DROWN, sdx=0, sdy=1.2, sh=0.16)
    for sx in (-1, 1):
        fill(ell(sx*3.4, 0.8, 2.3, 1.8, 14), DROWN_D)
        eye(sx*3.4, 1.2, 1.1, EYE_C, 2.2)
        stroke(bez((sx*1.4, 3.6), (sx*2.8, 4.4), (sx*4.4, 4.3), (sx*5.8, 3.4)), LINE*0.8)
    stroke([(0, 0.5), (-0.6, -2.4), (0.6, -2.8)], LINE*0.6)
    shape(ell(0, -5.4, 1.5+1.2*m, 1.0+2.0*m, 18), MOUTH_D, LINE*0.7)
    for (x0, y0, x1, y1) in ((-6, 7.5, -8.5, -4), (-3, 8.8, -4.5, 3.5), (0, 9, 0.8, 5), (3, 8.8, 4.8, 2.5), (6, 7.5, 8.4, -3)):
        tube(bez((x0, y0), (x0*1.1, y0-1.5), (x1+s*0.4, y1+2), (x1+s*0.7, y1)), 2.2, 0.6, WEED_L if x0 > 0 else WEED, lw=LINE*0.6, sh=0)
    drip(2.5, -9.6, 0.7)


def _utopenec_fb(pose, back):
    q = UTF[pose]
    hy, s = q["hip"], q["sw"]
    up = pose == "windup"

    def arms():
        for sx, (h, k) in zip((-1, 1), q["h"]):
            sh = (sx*12, 25.5)
            el = ((sh[0]+h[0])/2+sx*(4.5 if not up else 4), (sh[1]+h[1])/2+(1 if not up else -2))
            g = DROWN if k >= 1 else DROWN_D
            tube(chaikin([sh, el, h]), 6.5*k, 5.5*k, g)
            if not back or up:
                with T(h[0], h[1], k):
                    mitt(0, 0, 90 if up else -90+sx*12, 3.2, g)
                if not up:
                    drip(h[0]+sx*1.5, h[1]-5*k); drip(h[0]-sx*1.2, h[1]-6.5*k, 0.6)
            tube(bez(el, (el[0]+sx, el[1]-3), (el[0]-sx+s*0.4, el[1]-6), (el[0]+s*0.8, el[1]-9)), 1.8, 0.5, WEED, lw=LINE*0.5, sh=0)

    with T(0, 0, 1, flip=back):
        for (k, a, sc), sx in sorted(zip(legs_fb(q["legs"]), (-1, 1)), key=lambda t: t[0][2]):
            hp = (sx*5.5, hy)
            kn = (k[0]*1.3, k[1]+1)
            an = (a[0]*1.25, a[1]-0.5)
            tube(chaikin([hp, kn, an]), 9, 6.8*sc, TROUS if sc >= 0.97 else Col(0.32, "#4a4856"))
            foot_fb(an[0], an[1]-2.5, sc, DROWN if sc >= 0.97 else DROWN_D, back)
        with T(0, hy):
            if back and not up: arms()
            body = bez((-10, -2), (-14, 6), (-15, 17), (-13.5, 25)) + bez((-13.5, 25), (-11, 30), (-6, 32), (0, 32)) + \
                bez((0, 32), (6, 32), (11, 30), (13.5, 25)) + bez((13.5, 25), (15, 17), (14, 6), (10, -2)) + \
                bez((10, -2), (5, -3.5), (-5, -3.5), (-10, -2))
            form(body, DROWN if not back else DROWN_D, sdx=0, sdy=1.2, sh=0.15)
            shirt = [(-16, 34), (16, 34)] + rag_hem(16, -16, 9, 5, 11, 2)
            vee = [(-4.5, 34), (4.5, 34), (0, 21)]
            clipped(body, lambda: (fill(shirt, SHIRT_W), offset_shadow(shirt, 0, 1.4, 0.18), hatch(shirt, 2.2, 70, 0.4, 0.0, 0.35),
                                   None if back else fill(vee, DROWN)))
            stroke(shirt[2:], LINE*0.7)
            if not back: stroke([vee[0], vee[2], vee[1]], LINE*0.6)
            else: stroke(bez((0, 30), (0.4, 22), (-0.4, 16), (0, 9)), LINE*0.5, g=SHIRT_W)
            stroke(body, LINE, closed=True)
            shape(rrect(-12, -2.5, 24, 3.4, 1.4), LEATHER_D, LINE*0.8)
            for x0, y0, x1, y1 in ((-8, 28, -11, 12), (-3, 30, -4, 17), (5, 29.5, 7, 15)):
                tube(bez((x0, y0), (x0-1, (y0+y1)/2+3), (x1+1+s*0.6, (y0+y1)/2), (x1+s, y1)), 2.2, 0.7, WEED, lw=LINE*0.6, sh=0)
            with T(0, 30+q["hd"]-(2 if back else 0)):
                _utopenec_head_fb(q["mouth"], back, s)
            if not back or up: arms()
    if pose == "attack" and not back:
        for sx in (-1, 1):
            for i in range(3):
                stroke([(sx*(17+i*1.5), 60-i*4), (sx*(21+i*1.5), 62-i*4)], LINE*0.5, g=COLD_L)


SHROUD = Col(0.78, "#cdc8b6")
SHROUD_D = Col(0.6, "#a39d8a")
GAUNT = Col(0.7, "#b8b1c2")
GAUNT_D = Col(0.55, "#958da3")

UPP = {
    "idle": dict(hip=(0, 38), lean=-6, ff=(-5, 1.5), nf=(6, 1.5), hb=-12, hf=10, fh=(10, 18), nh=(13, 20), head=-6, mouth=0, flare=0),
    "walk": dict(hip=(1, 37), lean=-14, ff=(-8, 3), nf=(10, 1.5), hb=-16, hf=13, fh=(12, 20), nh=(14, 21), head=-4, mouth=0, flare=4),
    "walk2": dict(hip=(1, 37.6), lean=-12, ff=(-2, 4), nf=(1, 1.5), hb=-18, hf=11.5, fh=(12.5, 21), nh=(15, 22.5), head=-5, mouth=0, flare=7),
    "walk3": dict(hip=(1, 37), lean=-14, ff=(10, 1.5), nf=(-8, 3), hb=-15, hf=14, fh=(13, 22), nh=(15, 23), head=-4, mouth=0, flare=3),
    "walk4": dict(hip=(1, 37.6), lean=-12, ff=(1, 1.5), nf=(-2, 4), hb=-17.5, hf=12, fh=(12.5, 21), nh=(14.5, 22), head=-5, mouth=0, flare=6),
    "windup": dict(hip=(1, 38.5), lean=-2, ff=(-6, 1.5), nf=(8, 1.5), hb=-22, hf=18, fh=(12, 36), nh=(16, 37), head=10, mouth=1, flare=16),
    "attack": dict(hip=(-2, 36), lean=-24, ff=(-14, 1.5), nf=(12, 1.5), hb=-26, hf=16, fh=(30, 28), nh=(33, 22), head=6, mouth=1, flare=12),
}


def upir(pose):
    pose, v = view_of(pose)
    if v: return _upir_fb(pose, v == "b")
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


UPF = {  # fl: how far the shroud is thrown open; feet (-x, +x): (x, y, scale)
    "idle": dict(fl=0, sw=0, feet=((-4, 1.5, 1), (4, 1.5, 1)), hd=0, m=0),
    "walk": dict(fl=0.05, sw=1.2, feet=((-4, 3.2, 0.9), (4.5, 0.4, 1.1)), hd=-0.4, m=0),
    "walk2": dict(fl=0.1, sw=0.4, feet=((-4, 1.5, 1), (4, 4.5, 1.05)), hd=0.4, m=0),
    "walk3": dict(fl=0.05, sw=-1.2, feet=((-4.5, 0.4, 1.1), (4, 3.2, 0.9)), hd=-0.4, m=0),
    "walk4": dict(fl=0.1, sw=-0.4, feet=((-4, 4.5, 1.05), (4, 1.5, 1)), hd=0.4, m=0),
    "windup": dict(fl=1, sw=0, feet=((-6, 1.5, 1), (6, 1.5, 1)), hd=1.5, m=1),
    "attack": dict(fl=0.55, sw=0, feet=((-6, 2.4, 0.95), (6, 0.6, 1.1)), hd=-3.5, m=1),
}
UP_IN = Col(0.3, "#4d4256")
UP_LINING = Col(0.35, "#5d4f66")


def _upir_head_fb(m, back):
    hood = bez((0, 14), (-6, 13), (-10, 8), (-9.8, 0)) + bez((-9.8, 0), (-9.8, -6), (-7, -10), (0, -10.5)) + \
        bez((0, -10.5), (7, -10), (9.8, -6), (9.8, 0)) + bez((9.8, 0), (10, 8), (6, 13), (0, 14))
    if back:
        hood = bez((0, 16), (-3, 13), (-10, 9), (-10.5, 0)) + bez((-10.5, 0), (-11, -7), (-9, -12), (-6, -13)) + \
            [(6, -13)] + bez((6, -13), (9, -12), (11, -7), (10.5, 0)) + bez((10.5, 0), (10, 9), (3, 13), (0, 16))
        form(hood, SHROUD, sdx=0, sdy=2.5, sh=0.2)
        hatch(hood, 1.8, 60, 0.35, 0.0, 0.3)
        stroke(bez((-8.5, -10.5), (-4, -12.5), (4, -12.5), (8.5, -10.5)), LINE*0.6, g=SHROUD_D)
        stroke(bez((0, 13.5), (0.5, 6), (-0.5, -2), (0, -10)), LINE*0.6, g=SHROUD_D)
        for sx in (-1, 1):
            stroke(bez((sx*3, 11), (sx*6, 5), (sx*6.5, -2), (sx*5.5, -9)), LINE*0.5, g=SHROUD_D)
        return
    form(hood, SHROUD, sdx=0, sdy=1.2, sh=0.16)
    fill(bez((0, 10.5), (-7, 10), (-7.5, -1), (-5, -8.5)) + bez((-5, -8.5), (-2, -10), (2, -10), (5, -8.5)) +
         bez((5, -8.5), (7.5, -1), (7, 10), (0, 10.5)), UP_IN)
    hd = bez((0, 8.5), (-5, 8.5), (-5.8, 2), (-5, -3)) + bez((-5, -3), (-4, -7.5), (-1.5, -8.8), (0, -8.8)) + \
        bez((0, -8.8), (1.5, -8.8), (4, -7.5), (5, -3)) + bez((5, -3), (5.8, 2), (5, 8.5), (0, 8.5))
    form(hd, GAUNT, sdx=0, sdy=1, sh=0.18)
    for sx in (-1, 1):
        fill(ell(sx*2.4, 1.4, 2.0, 1.8, 14), GAUNT_D)
        eye(sx*2.4, 1.2, 1.1, EYE_R, 2.4)
        stroke(bez((sx*0.6, 3.6), (sx*2, 4.6), (sx*3.4, 4.4), (sx*4.6, 3.2)), LINE*0.9)
        stroke(bez((sx*3.6, -1.5), (sx*3.4, -3.5), (sx*2.8, -5), (sx*2.2, -6)), LINE*0.45)
    stroke([(0, 2.5), (0.5, -1.8), (-0.4, -2.6)], LINE*0.6)
    mo = bez((-2.4, -5), (-1, -5.6-2*m), (1, -5.6-2*m), (2.4, -5)) + bez((2.4, -5), (1, -4.4), (-1, -4.4), (-2.4, -5))
    shape(mo, MOUTH_D, LINE*0.7)
    for x in (-1.1, 1.1):
        fill([(x-0.45, -5), (x+0.45, -5), (x, -7.2-m)], TOOTH)
    for sx in (-1, 1):
        fl = bez((sx*7.5, 11), (sx*5.5, 6), (sx*5.8, -2), (sx*5, -9.5)) + [(sx*9.5, -9.5)] + bez((sx*9.5, -9.5), (sx*10, -2), (sx*10, 6), (sx*7.5, 11))
        form(fl, SHROUD, sdx=0, sdy=0.8, sh=0.1)


def _upir_fb(pose, back):
    q = UPF[pose]
    fl, sw = q["fl"], q["sw"]
    W = 14 + 4*fl
    S = [(sx*(10+11*fl), 64+9*fl) for sx in (-1, 1)]
    Hm = [(sx*W+sw, 4) for sx in (-1, 1)]
    hy = 75 + q["hd"]
    with T(0, 0, 1, flip=back):
        for (x, y, sc) in sorted(q["feet"], key=lambda f: f[2]):
            foot_fb(x, y-1, sc, GAUNT if sc >= 0.97 else GAUNT_D, back, 2.8)
        sr = [(-6, 70)] + bez((-6, 70), (-8.5, 70), (S[0][0]+2, S[0][1]+2), S[0]) + \
            bez(S[0], (S[0][0]-1.5-fl*2, 48), (Hm[0][0]+0.5, 24), Hm[0]) + rag_hem(Hm[0][0], Hm[1][0], 4, 3.5, 12, 3) + \
            bez(Hm[1], (Hm[1][0]-0.5, 24), (S[1][0]+1.5+fl*2, 48), S[1]) + bez(S[1], (S[1][0]-2, S[1][1]+2), (8.5, 70), (6, 70))
        form(sr, SHROUD, sdx=0, sdy=1.4, sh=0.16)
        hatch(sr, 2.0, 70, 0.35, 0.0, 0.25)
        if back:
            for x in (-7, -2.5, 2.5, 7):
                stroke(bez((x*0.5, 64), (x*0.8, 45), (x+sw*0.4, 25), (x*1.15+sw, 6)), LINE*0.55, g=SHROUD_D)
        else:
            gw = 2.5 + 11*fl
            gap = [(0, 67)] + bez((0, 67), (-1-gw*0.5, 55), (-gw+sw*0.3, 30), (-gw-1+sw*0.5, 4.5)) + \
                [(gw+1+sw*0.5, 4.5)] + bez((gw+1+sw*0.5, 4.5), (gw+sw*0.3, 30), (1+gw*0.5, 55), (0, 67))
            shape(gap, UP_IN if fl < 0.3 else UP_LINING, LINE*0.8)
            if fl >= 0.3:
                bd = bez((-3, 64), (-4.8, 52), (-4, 42), (-3, 30)) + [(3, 30)] + bez((3, 30), (4, 42), (4.8, 52), (3, 64))
                shape(bd, GAUNT_D, LINE*0.7)
                for i in range(4):
                    y = 58 - i*3.5
                    stroke(bez((-0.5, y), (-2, y+0.6), (-3.5, y), (-4, y-1)), LINE*0.5)
                    stroke(bez((0.5, y), (2, y+0.6), (3.5, y), (4, y-1)), LINE*0.5)
                for sx in (-1, 1):
                    tube([(sx*2, 31), (sx*2.6, 18), (sx*2.4, 6)], 2.8, 2.0, GAUNT_D, lw=LINE*0.7, sh=0)
            for sx in (-1, 1):
                for i in range(3):
                    x0 = sx*(gw+3+i*2.5)
                    stroke(bez((x0*0.6, 62-i*2), (x0, 45), (x0*1.05+sw*0.4, 25), (x0*1.1+sw, 7)), LINE*0.5, g=SHROUD_D)
        with T(0, hy):
            _upir_head_fb(q["m"], back)
        if pose == "attack" and not back:
            for sx in (-1, 1):
                with T(sx*8.5, 52, 1.8):
                    _claw_hand((0, 0), (sx*1.5, -4), GAUNT)
            for sx in (-1, 1):
                for i in range(3):
                    stroke([(sx*(14+i*2), 56-i*4), (sx*(18+i*2), 57-i*4)], LINE*0.5, g=EYE_R)
        elif fl >= 0.3:
            for sx, s_ in zip((-1, 1), S):
                _claw_hand((s_[0]+sx*0.5, s_[1]+2), (s_[0]+sx*0.2, s_[1]-2), GAUNT)
        elif not back:
            for sx in (-1, 1):
                _claw_hand((sx*3.6, 57), (sx*6.5, 53), GAUNT)


NAV_SKIN = Col(0.8, "#c3d4de")
NAV_SKIN_D = Col(0.65, "#9db3c2")
NAV_DRESS = Col(0.88, "#dde5e8")
NAV_HAIR = Col(0.35, "#4e5b70")
NAV_HAIR_L = Col(0.45, "#66748a")

NVP = {
    "idle": dict(hip=(0, 38), lean=-3, hb=-9, hf=9, fh=(6, 14), nh=(9, 13), head=-3, sway=0, cast=False),
    "walk": dict(hip=(1, 39), lean=-10, hb=-14, hf=8, fh=(4, 12), nh=(12, 16), head=0, sway=5, cast=False, ph=0),
    "walk2": dict(hip=(1, 39.6), lean=-8.5, hb=-13, hf=9, fh=(7, 13.5), nh=(9, 14.5), head=-1, sway=1.5, cast=False, ph=1.6),
    "walk3": dict(hip=(1, 39.2), lean=-7, hb=-11, hf=10, fh=(10, 15), nh=(5, 12), head=-2, sway=-4, cast=False, ph=3.2),
    "walk4": dict(hip=(1, 38.8), lean=-9, hb=-12.5, hf=9, fh=(7, 13), nh=(8.5, 14), head=-1, sway=1, cast=False, ph=4.8),
    "windup": dict(hip=(-1, 38), lean=0, hb=-11, hf=9, fh=(10, 16), nh=(15, 31), head=6, sway=2, cast="charge"),
    "attack": dict(hip=(-1, 38), lean=-6, hb=-12, hf=11, fh=(-8, 20), nh=(27, 27), head=4, sway=3, cast=True),
}


def navka(pose):
    pose, v = view_of(pose)
    if v: return _navka_fb(pose, v == "b")
    q = NVP[pose]
    ph, amp = q.get("ph", 0), 1.1 if "ph" in q else 0
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
         [(x, y+amp*math.sin(ph+i*1.3)) for i, (x, y) in enumerate(((hb+2.5, 3), (hb+4.5, -1.5), (hb+7, 2.5), (hb+9.5, -2), (hb+12, 2), (hf-3, -1)))] + [(hf, 1)] + \
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
        if q["cast"] is True:
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


NVF = {  # hands (-x, +x) in hip space; sw/ph: the hover's sway and hem ripple
    "idle": dict(hip=38, sw=0, ph=0, amp=0, h=((-6.8, 3), (6.8, 3)), hd=0, cast=False),
    "walk": dict(hip=38, sw=2.5, ph=0, amp=1.1, h=((-7.6, 4), (6.4, 2)), hd=-0.4, cast=False),
    "walk2": dict(hip=38.6, sw=0.8, ph=1.6, amp=1.1, h=((-7.2, 3.5), (6.8, 2.6)), hd=0, cast=False),
    "walk3": dict(hip=38.2, sw=-2.5, ph=3.2, amp=1.1, h=((-6.4, 2), (7.6, 4)), hd=0.4, cast=False),
    "walk4": dict(hip=37.6, sw=-0.8, ph=4.8, amp=1.1, h=((-6.8, 2.6), (7.2, 3.5)), hd=0, cast=False),
    "windup": dict(hip=38, sw=0.5, ph=0, amp=0, h=((-7.5, 4), (12, 35)), hd=0.5, cast="charge"),
    "attack": dict(hip=38, sw=0, ph=0, amp=0, h=((-10, 6), (4, 19)), hd=-0.5, cast=True),
}


def _navka_head_fb(back, sw):
    if back:
        form(ell(0, 0.3, 6.0, 7.2, 26), NAV_HAIR, sdx=0, sdy=1, sh=0.14)
        stroke([(0, 7.2), (0, -6.5)], LINE*0.45, g=NAV_HAIR_L)
        for sx in (-1, 1):
            for k in range(3):
                stroke(bez((sx*1.2, 6.8), (sx*(3+k), 5), (sx*(4+k*0.6), 0), (sx*(3+k*0.8), -6)), LINE*0.45, g=NAV_HAIR_L)
    else:
        hd = bez((0, 7.2), (-5.2, 7.2), (-5.6, 1), (-4.6, -3)) + bez((-4.6, -3), (-3.5, -6.2), (-1.5, -6.8), (0, -6.8)) + \
            bez((0, -6.8), (1.5, -6.8), (3.5, -6.2), (4.6, -3)) + bez((4.6, -3), (5.6, 1), (5.2, 7.2), (0, 7.2))
        form(hd, NAV_SKIN, sdx=0, sdy=0.8, sh=0.14)
        for sx in (-1, 1):
            fill(ell(sx*2.2, 0.6, 1.6, 1.3, 12), NAV_SKIN_D)
            eye(sx*2.2, 0.5, 0.85, EYE_C, 2.4)
            stroke(bez((sx*0.9, 2.5), (sx*1.8, 3.1), (sx*2.8, 3.1), (sx*3.6, 2.5)), LINE*0.6)
        stroke([(0, -1.0), (0.3, -2.2)], LINE*0.45)
        stroke(bez((-1.2, -4.2), (-0.4, -4.6), (0.4, -4.6), (1.2, -4.2)), LINE*0.6)
        cap = bez((-5.6, -1), (-6.6, 6), (-3, 8.8), (0, 8.6)) + bez((0, 8.6), (3, 8.8), (6.6, 6), (5.6, -1)) + \
            bez((5.6, -1), (5, 3), (3, 5.2), (0.4, 5.6)) + [(0, 4.8), (-0.4, 5.6)] + bez((-0.4, 5.6), (-3, 5.2), (-5, 3), (-5.6, -1))
        form(cap, NAV_HAIR, sdx=0, sdy=0.6, sh=0.12)
        for sx in (-1, 1):
            stroke(bez((sx*0.6, 8), (sx*2.5, 7), (sx*4, 5), (sx*5, 2)), LINE*0.45, g=NAV_HAIR_L)
    for i, x in enumerate((-5, -3.4, -1.7, 0, 1.7, 3.4, 5)):
        y = 7.6 + 1.2*math.cos(x/5*1.4)
        shape(ell(x, y, 1.15, 0.9, 10), (Col(0.8, "#e8e0f0"), Col(0.75, "#b8d8a0"))[i % 2], LINE*0.4)


def _navka_fb(pose, back):
    q = NVF[pose]
    sw, ph, amp = q["sw"], q["ph"], q["amp"]
    hl, hr = q["h"]

    def burst(h, big):
        glow(h[0], h[1], 9*big, COLD, 0.22, 4)
        if q["cast"] is True:
            for k in range(8):
                aa = math.radians(k*45+10)
                stroke([(h[0]+math.cos(aa)*2*big, h[1]+math.sin(aa)*2*big), (h[0]+math.cos(aa)*7*big, h[1]+math.sin(aa)*7*big)], LINE*0.7, g=COLD_L)
            dot(h[0], h[1], 1.8*big, WHITE)

    def arms():
        for sx, h in ((-1, hl), (1, hr)):
            g = NAV_SKIN if (sx > 0) != back else NAV_SKIN_D
            d = math.hypot(h[0]-sx*5, h[1]-25)
            k = min(1, d/23.5)
            limb((sx*5, 25), h, 13*k, 12*k, 3.8, 3.0, g, -sx if h[1] > 20 else sx)
            shape(ell(h[0], h[1], 1.9, 1.5, 12), g, LINE*0.7)

    with T(0, 0, 1, flip=back):
        with T(0, q["hip"]):
            if q["cast"] is True and back: burst((hr[0], hr[1]+2), 1.5)
            hair = bez((-5.5, 39), (-10, 33), (-9.5+sw*0.3, 18), (-10.5+sw, 4)) + \
                [(-7.5+sw, 7), (-5+sw*0.8, 3.5), (-2.5+sw*0.7, 6.5), (0+sw*0.6, 3), (2.5+sw*0.7, 6.5), (5+sw*0.8, 3.5), (7.5+sw, 7)] + \
                bez((10.5+sw, 4), (9.5+sw*0.3, 18), (10, 33), (5.5, 39))
            if not back:
                form(hair, NAV_HAIR, sdx=0, sdy=1, sh=0.18)
            top_y, hem_y = 26, -37
            dr = [(-5.5, top_y)] + bez((-5.5, top_y), (-6, 20), (-6.5, 4), (-10.5+sw, hem_y+1)) + \
                [(x+sw, hem_y+(1.5 if i % 2 else -0.8)+amp*math.sin(ph+i*1.3)) for i, x in enumerate((-8.5, -6, -3.5, -1, 1.5, 4, 6.5, 9))] + \
                bez((10.5+sw, hem_y+1), (6.5, 4), (6, 20), (5.5, top_y)) + bez((5.5, top_y), (2, 27.5), (-2, 27.5), (-5.5, top_y))
            form(dr, NAV_DRESS, sdx=0, sdy=1.2, sh=0.16)
            for x in ((-3.5, 0, 3.5) if not back else (-2, 2)):
                stroke(bez((x*0.6, 18), (x*0.8, 2), (x+sw*0.4, -18), (x*1.2+sw, -34)), LINE*0.45, g=COLD)
            for i, x in enumerate(range(-9, 10, 3)):
                stroke([(x+sw, hem_y), (x+sw*1.3-0.5, hem_y-2.5-(i % 3))], LINE*0.6, g=COLD_L, alpha=0.6)
            if not back:
                stroke(bez((-4.5, 21), (-1.5, 19.5), (1.5, 19.5), (4.5, 21)), LINE*0.5, g=COLD)
            if back:
                arms()
                hb = bez((-6, 38), (-8.5, 30), (-8+sw*0.3, 14), (-8.5+sw, -2)) + \
                    [(-5.5+sw, 1), (-3+sw*0.8, -3), (0+sw*0.7, 0.5), (3+sw*0.8, -3), (5.5+sw, 1)] + \
                    bez((8.5+sw, -2), (8+sw*0.3, 14), (8.5, 30), (6, 38))
                form(hb, NAV_HAIR, sdx=0, sdy=1, sh=0.18)
                for k in range(5):
                    x = -5+k*2.5
                    stroke(bez((x*0.5, 36), (x*0.9, 26), (x+sw*0.3, 12), (x*1.05+sw*0.9, 0)), LINE*0.5, g=NAV_HAIR_L)
            with T(0, 33.5+q["hd"]):
                _navka_head_fb(back, sw)
            if not back:
                for sx in (-1, 1):
                    tube(bez((sx*4.6, 31), (sx*6, 26), (sx*5.2+sw*0.3, 20), (sx*5.8+sw*0.6, 14)), 2.4, 1.0, NAV_HAIR, lw=LINE*0.6, sh=0)
                arms()
            if q["cast"] == "charge":
                glow(hr[0]+0.5, hr[1]+2, 8, COLD, 0.22, 4)
            if q["cast"] is True and not back:
                burst(hr, 1.3)


for _fn in (kostlivy_havir, kostlivy_kusinik, kostejuv_nesmrtelny, utopenec, upir, navka):
    _fn.poses = ALL
