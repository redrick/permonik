import math
from reportlab.lib.colors import HexColor
import common
from common import FEET
from lib import Col, ell, bez, rrect
from style3 import (C, T, stroke, shape, form, fill, hatch, tube, cast_shadow, offset_shadow, dot, face,
                    head_outline, clip_fill, poly, LINE)
from chars3 import Person

SKIN = Col(0.78, "#d8b59b")
SKIN_DK = Col(0.68, "#c49a7e")
FLAME = Col(0.85, "#ffd27a")
FLAME_CORE = Col(0.97, "#fff3c8")
GLOW = Col(0.8, "#ffb04a", alpha=0.16)
IRON = Col(0.45, "#6c7079")
IRON_LT = Col(0.62, "#9a9ea6")
WOOD = Col(0.45, "#7d5d3d")
WOOD_LT = Col(0.55, "#9a7650")
BRASS = Col(0.6, "#b8994e")
BONE = Col(0.82, "#d8cdb4")
RED = Col(0.35, "#a8382e")
LEATHER = Col(0.32, "#5a4231")
BOOT = Col(0.25, "#3e3029")

S_HERO = 0.5

# ------------------------------------------------------------------ figure helpers
def ik(S, Pt, a, b, bend):
    dx, dy = Pt[0]-S[0], Pt[1]-S[1]
    d = max(abs(a-b)+0.5, min(math.hypot(dx, dy), a+b-0.5))
    base = math.atan2(dy, dx)
    al = math.acos((a*a+d*d-b*b)/(2*a*d))
    E = (S[0]+math.cos(base+bend*al)*a, S[1]+math.sin(base+bend*al)*a)
    f = math.atan2(Pt[1]-E[1], Pt[0]-E[0])
    return E, (E[0]+math.cos(f)*b, E[1]+math.sin(f)*b)


def hnd(x, y, ang, r, skin=SKIN, open_=False):
    with T(x, y, 1, rot=ang+90):
        palm = bez((-r*0.8, r*0.3), (-r, -r*0.8), (-r*0.8, -r*1.9), (0, -r*2.0)) + \
               bez((0, -r*2.0), (r*0.8, -r*1.9), (r, -r*0.8), (r*0.8, r*0.3))
        if open_:
            for a in (-28, -10, 8, 26):
                with T(0, -r*1.4, 1, rot=a):
                    tube([(0, 0), (0, -r*1.5)], r*0.55, r*0.45, skin, LINE*0.6, sh=0)
        shape(palm, skin, LINE*0.9)
        stroke(bez((r*0.75, -r*0.2), (r*1.5, -r*0.3), (r*1.6, -r*1.1), (r*1.0, -r*1.3)), LINE*0.8)


def arm(k, side, spec, sleeve, skin=SKIN, rolled=False, hand=True, open_=False, cuff=None, hr=2.5):
    S = (side*k.sh_w, k.sh_y-1.5)
    if spec[0] == "k":
        E, H = ik(S, (spec[1], spec[2]), k.up, k.fo, spec[3])
    else:
        ua, fa_ = math.radians(spec[1]), math.radians(spec[2])
        E = (S[0]+math.cos(ua)*k.up, S[1]+math.sin(ua)*k.up)
        H = (E[0]+math.cos(fa_)*k.fo, E[1]+math.sin(fa_)*k.fo)
    fa = math.degrees(math.atan2(H[1]-E[1], H[0]-E[0]))
    tube([S, E], k.arm_w[0], k.arm_w[0]*0.95, sleeve)
    f = (H[0]-math.cos(math.radians(fa))*2.2, H[1]-math.sin(math.radians(fa))*2.2)
    tube([E, f], k.arm_w[0]*0.95 if not rolled else k.arm_w[1], k.arm_w[1], skin if rolled else sleeve)
    if rolled:
        tube([E, (E[0]+(f[0]-E[0])*0.15, E[1]+(f[1]-E[1])*0.15)], k.arm_w[0]*1.05, k.arm_w[0], sleeve, sh=0)
    if cuff is not None:
        c0 = (f[0]-math.cos(math.radians(fa))*1.6, f[1]-math.sin(math.radians(fa))*1.6)
        tube([c0, f], k.arm_w[1]+0.6, k.arm_w[1]+0.6, cuff, sh=0)
    if hand: hnd(H[0], H[1], fa, hr, skin, open_)
    return H, fa


LEGS = {  # per leg (back, front): hip x, knee x, knee dy, ankle x, lift, foot rot
    "stand": ((-4, -4.5, 0, -5, 0, 0), (4, 4.6, 0, 5, 0, 0)),
    "w1": ((-3, -6, 0, -11, 2.5, -14), (3, 8, 1, 10, 0, 0)),
    "w2": ((-3, 6, 1, 8, 0, 0), (3, -5, 0, -10, 2.5, -14)),
    "c1": ((-3, -7, 0, -13, 2.2, -20), (3, 8, 0.5, 13, 0.6, 9)),
    "p1": ((-3, 6, 4, 4, 6, -12), (3, 1.5, 0, 0.5, 0, 0)),
    "c2": ((-3, 8, 0.5, 13, 0.6, 9), (3, -7, 0, -13, 2.2, -20)),
    "p2": ((-3, 0.5, 0, -0.5, 0, 0), (3, 7, 4, 5, 6, -12)),
    "lunge": ((-3, -9, -1, -17, 0.5, -8), (3, 13, 3, 13, 0, 0)),
    "brace": ((-3, -8, 0, -12, 0, 0), (3, 4, 0, 8, 1.5, 10)),
    "lie": ((-4, -4.5, 0, -5, 0, 90), (4, 4.6, 0, 5, 0, 90)),
}


def boot(ax, lift, ay, top, col, rot=0, wk=1.0):
    with T(ax, lift, 1, rot=rot):
        bt = top
        b = [(-3.0*wk, bt), (3.0*wk, bt)] + bez((3.0*wk, bt), (3.1*wk, ay), (3.5*wk, 2.2), (6.8*wk, 2)) + \
            bez((6.8*wk, 2), (7.6*wk, 1.8), (7.4*wk, 0), (6.5*wk, 0)) + [(-3.2*wk, 0)] + \
            bez((-3.2*wk, 0), (-3.6*wk, 1), (-3.2*wk, ay), (-3.0*wk, bt))
        form(b, col, sh=0.14)
        stroke([(-3.3*wk, 1.3), (7.1*wk, 1.3)], LINE*0.7)


def legs(k, phase, trousers, boots, boot_h=7, wk=1.0, kx=1.0, draw=True):
    out = []
    for hx, kxx, kdy, axx, lift, frot in LEGS[phase]:
        pts = [(hx*kx, k.hip), (kxx*kx, k.knee+kdy), (axx*kx, k.ankle+lift)]
        out.append((pts, lift, frot))
    if draw:
        for pts, lift, frot in out:
            tube(pts, k.leg_w[0], k.leg_w[1], trousers)
        for pts, lift, frot in out:
            ax, ay = pts[-1]
            boot(ax, lift, k.ankle, k.ankle+boot_h, boots, frot, wk)
    return out


def torso_pts(k, hem_y, hem_w, waist_w=None, waist_y=None, collar=5.0):
    sw = k.sh_w; ww = waist_w or sw+1.2; wy = waist_y or (k.sh_y+hem_y)/2
    return bez((-collar, k.sh_y+2.8), (-collar-4.5, k.sh_y+2.5), (-sw-1.3, k.sh_y+0.5), (-sw-1.8, k.sh_y-4)) + \
        bez((-sw-1.8, k.sh_y-4), (-ww, wy+8), (-ww, wy-6), (-hem_w, hem_y)) + \
        bez((-hem_w, hem_y), (-hem_w*0.3, hem_y-1.2), (hem_w*0.3, hem_y-1.2), (hem_w, hem_y)) + \
        bez((hem_w, hem_y), (ww, wy-6), (ww, wy+8), (sw+1.8, k.sh_y-4)) + \
        bez((sw+1.8, k.sh_y-4), (sw+1.3, k.sh_y+0.5), (collar+4.5, k.sh_y+2.5), (collar, k.sh_y+2.8))


def skirt_pts(top_y, top_w, hem_y, l, r):
    return [(-top_w, top_y), (top_w, top_y)] + bez((top_w, top_y), (top_w+2, top_y-12), (r-2, hem_y+10), (r, hem_y)) + \
        bez((r, hem_y), (r*0.4, hem_y-1.5), (l*0.4, hem_y-1.5), (l, hem_y)) + \
        bez((l, hem_y), (l+2, hem_y+10), (-top_w-2, top_y-12), (-top_w, top_y))


def neck(k, skin=SKIN, w=2.8):
    shape([(-w, k.hy-k.hr+2), (w, k.hy-k.hr+2), (w+0.3, k.sh_y+0.5), (-w-0.3, k.sh_y+0.5)], skin, 0)
    stroke([(-w, k.hy-k.hr+2.5), (-w-0.3, k.sh_y+0.8)], LINE*0.8)
    stroke([(w, k.hy-k.hr+2.5), (w+0.3, k.sh_y+0.8)], LINE*0.8)


def head(k, mood, skin=SKIN, ear=True, dx=0.2, neck_w=2.8, do_neck=True, do_face=True):
    if do_neck: neck(k, skin, neck_w)
    r = k.hr; cy = k.hy
    if ear: shape(ell(-r*0.95, cy-r*0.05, r*0.2, r*0.3, 14), skin, LINE*0.8)
    shape(head_outline(k), skin)
    if do_face: face(r*dx, cy, r*0.95, mood)


def beard(k, col, length=1.55, line=None, dx=0.1):
    r = k.hr; cy = k.hy; L = length
    bd = bez((-r*0.95, cy-r*0.15), (-r*1.0, cy-r*(L-0.35)), (-r*0.4, cy-r*L), (r*dx, cy-r*L)) + \
        bez((r*dx, cy-r*L), (r*0.5, cy-r*L), (r*1.0, cy-r*(L-0.35)), (r*0.95, cy-r*0.15)) + \
        bez((r*0.95, cy-r*0.15), (r*0.7, cy-r*0.5), (r*0.45, cy-r*0.48), (r*dx*2, cy-r*0.5)) + \
        bez((r*dx*2, cy-r*0.5), (-r*0.1, cy-r*0.48), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.15))
    shape(bd, col)
    if line is not None:
        for xx in (-0.5, -0.15, 0.2, 0.55):
            stroke(bez((r*xx, cy-r*0.8), (r*xx*1.05, cy-r*(L*0.65)), (r*xx, cy-r*(L*0.78)), (r*xx*0.9, cy-r*(L*0.88))), LINE*0.45, g=line)


def moustache(k, col, dx=0.2, w=0.55):
    r = k.hr; cy = k.hy; c = r*dx
    m = bez((c-r*w, cy-r*0.55), (c-r*0.3, cy-r*0.3), (c+r*0.3, cy-r*0.3), (c+r*w, cy-r*0.55)) + \
        bez((c+r*w, cy-r*0.55), (c+r*0.2, cy-r*0.62), (c-r*0.2, cy-r*0.62), (c-r*w, cy-r*0.55))
    shape(m, col, LINE*0.8)


def kahan(x, y, s=1.0, flame=FLAME, glow=GLOW, body=IRON, lit=True, hook=True):
    with T(x, y, s):
        if hook: stroke(bez((0, 0), (-1.2, 1.5), (0.5, 3.5), (1.2, 2.2)), LINE*0.7)
        if lit and glow is not None:
            for rr in (6.5, 4.2):
                fill(ell(6, -1.5, rr, rr, 24), glow)
        stroke([(0, 0), (0, -2)], LINE*0.7)
        b = bez((-3.6, -4.5), (-3.8, -2), (3.8, -2), (3.6, -4.5)) + bez((3.6, -4.5), (3.4, -9.5), (-3.4, -9.5), (-3.6, -4.5))
        form(b, body, sh=0.15)
        shape([(2.4, -4.6), (6, -3.2), (6.2, -4.4), (2.8, -6.4)], body, LINE*0.7)
        if lit:
            fl = bez((5.6, -4.2), (3.8, -2.6), (5.2, 0.6), (6.6, 2.6)) + bez((6.6, 2.6), (7.6, 0.4), (8.0, -2.8), (5.6, -4.2))
            shape(fl, flame, LINE*0.6)
            fill(ell(6.2, -2.3, 0.9, 1.4, 12), FLAME_CORE)
        else:
            stroke(bez((6, -3.8), (5.2, -1), (7, 0.5), (6.2, 3)), LINE*0.5, g=Col(0.6, "#8a9aa8"), alpha=0.6)


def lean_rot(pose):
    return {"hit": 10, "attack": -5, "windup": 5}.get(pose, 0)


def figure(body, k, x, y, s, pose, shadow_rx=17, drop=None, shadow=True, lie_w=26):
    """body(k, pose) draws in local units, feet at origin"""
    if pose == "dead":
        if drop: drop()
        H = k.hy + k.hr
        with T(x + H*s*0.5, y + lie_w*s, s, rot=90):
            body(k, pose)
        return
    if shadow: cast_shadow(x, y, shadow_rx*s, 3*s)
    with T(x, y + (1.2 if pose in ("hit", "attack") else 0), s, rot=lean_rot(pose)):
        body(k, pose)


# ------------------------------------------------------------------ weapons
def pick(x, y, ang, L=34, back=12):
    with T(x, y, 1, rot=ang):
        tube([(-back, 0), (L, 0)], 2.8, 2.5, WOOD, sh=0.1)
        hd = bez((L-6, -15), (L+3.5, -7), (L+3.5, 5), (L-4, 12)) + bez((L-4, 12), (L-0.8, 5), (L-0.8, -6), (L-6, -15))
        form(hd, IRON, sdx=-1, sdy=0.6, sh=0.15)
        shape(rrect(L-3.3, -2.4, 4.6, 4.8, 0.8), IRON_LT, LINE*0.8)


def valaska(x, y, ang, L=30, back=6, flip=False):
    with T(x, y, 1, rot=ang):
        if flip: C.scale(1, -1)
        tube([(-back, 0), (L+2, 0)], 2.2, 2.0, WOOD_LT, sh=0.1)
        for t in (L*0.25, L*0.5): shape(rrect(t-0.8, -1.4, 1.6, 2.8, 0.4), BRASS, LINE*0.5)
        bl = [(L-3.5, 1.2)] + bez((L-3.5, 1.2), (L-6, 4), (L-7.5, 7), (L-6.8, 10)) + \
            bez((L-6.8, 10), (L-2, 11.5), (L+3, 11), (L+5.5, 8.5)) + [(L+1.2, 1.2)]
        form(bl, IRON_LT, sdx=-0.8, sdy=0.8, sh=0.14)
        stroke(bez((L-6.4, 9.4), (L-2, 10.8), (L+2.8, 10.4), (L+5, 8.2)), LINE*1.1, g=Col(0.9, "#e4e6ea"), alpha=0.6)
        shape([(L-3.5, -2.8), (L+1.4, -2.8), (L+1.4, 1.4), (L-3.5, 1.4)], IRON, LINE*0.8)
        shape([(L-2.6, -2.8), (L+0.6, -2.8), (L+0.2, -5), (L-2.2, -5)], IRON, LINE*0.7)


def staff(x, y, ang, L=60, back=40, glow=False):
    with T(x, y, 1, rot=ang):
        tube([(-back, 0), (L, 0)], 2.6, 2.2, WOOD, sh=0.1)
        for t, sg in ((L-6, 1), (L-9, -1)):
            stroke([(t, -1.4), (t+1.2, 1.4)], LINE*1.3, g=RED)
        stroke(bez((L-8, -1), (L-10, -4), (L-11, -7), (L-10.5, -9)), LINE*0.7, g=RED)
        for sg in (1, -1):
            tube(bez((L-1, 0), (L+6, sg*3), (L+11, sg*9), (L+14, sg*16)), 2.8, 1.3, BONE, LINE*0.8, sh=0)
            tube([(L+6, sg*3.4), (L+13, sg*2.4)], 2.0, 1.0, BONE, LINE*0.7, sh=0)
            tube([(L+10.5, sg*8.5), (L+17, sg*9.5)], 1.8, 0.9, BONE, LINE*0.7, sh=0)
        if glow:
            for rr, a in ((14, 0.12), (9, 0.18), (5, 0.3)):
                fill(ell(L+8, 0, rr, rr, 24), Col(0.9, "#dff0ff", alpha=a))
            for (sx, sy, sr) in ((L+16, 6, 2.2), (L+14, -9, 1.6), (L+4, 11, 1.4), (L+19, -2, 1.2)):
                spark(sx, sy, sr)


def spark(x, y, r, col=Col(0.95, "#fff4c0")):
    pts = []
    for i in range(8):
        a = math.pi/2 + i*math.pi/4; rr = r if i % 2 == 0 else r*0.35
        pts.append((x+math.cos(a)*rr, y+math.sin(a)*rr))
    shape(pts, col, LINE*0.5)


def crossbow_back(k):
    with T(-2, k.sh_y-14, 1, rot=118):
        tube([(-14, 0), (30, 0)], 3.0, 2.6, WOOD, sh=0.1)
        bow = bez((24, -15), (29, -6), (29, 6), (24, 15))
        tube(bow, 2.4, 1.8, WOOD_LT, LINE*0.9, sh=0)
        stroke([(24, -15), (19, 0), (24, 15)], LINE*0.5)


# ------------------------------------------------------------------ HAVÍŘ
HAV = dict(H=126, hr=11, hy=114, sh_y=99, sh_w=13.5, hip=58, knee=31, ankle=5, leg_w=(8.4, 6.6),
           arm_w=(7.4, 6.4), up=20, fo=18)
H_SMOCK = Col(0.42, "#56606e")
H_SMOCK_DK = Col(0.3, "#3f4752")
H_TROUS = Col(0.62, "#9c9584")
H_CAP = Col(0.3, "#4d3d31")
H_BEARD = Col(0.28, "#4a3a2f")
H_FLEK = Col(0.3, "#5b4232")

HAV_POSE = {  # legs, near arm, far arm, weapon (angle, L, back), open hand, mood
    "idle": ("stand", ("a", -78, -30), ("a", -98, -84), "upright", False, "think"),
    "walk1": ("c1", ("a", -98, -52), ("a", -66, -36), "upright", False, "think"),
    "walk2": ("p1", ("a", -84, -36), ("a", -88, -66), "upright", False, "think"),
    "walk3": ("c2", ("a", -64, -14), ("a", -112, -96), "upright", False, "think"),
    "walk4": ("p2", ("a", -80, -30), ("a", -94, -74), "upright", False, "think"),
    "windup": ("brace", ("a", 118, 168), ("k", -2, 104, 1), "wind", False, "determined"),
    "attack": ("lunge", ("k", 38, 80, -1), ("k", 24, 84, -1), "swing", False, "wow"),
    "cast": ("brace", ("a", 62, 88), ("a", -100, -96), "hang", True, "think"),
    "hit": ("brace", ("a", -30, 25), ("a", -150, -160), "flung", False, "worried"),
    "dead": ("lie", ("a", -84, -88), ("a", -96, -92), None, False, "sleepy"),
    "portrait": ("stand", ("a", -78, -30), ("a", -98, -84), "upright", False, "think"),
    "hero": ("brace", ("a", -78, -30), ("a", 135, 105), "upright", False, "think"),
}


def havir_body(k, pose, mood=None):
    lg, near, far, wpn, op, md = HAV_POSE[pose]
    md = mood or md
    r = k.hr
    flek = [(-15, 63)] + bez((-15, 63), (-19, 52), (-19, 44), (-17, 38)) + [(-6, 40), (-5, 62)]
    form(flek, H_FLEK, sh=0.15)
    lamp_far = pose == "hero"
    H, fa = arm(k, -1, far, H_SMOCK, hand=False, cuff=H_SMOCK_DK)
    if wpn == "hang": pick(H[0], H[1], -96, 26, 10)
    if lamp_far: kahan(H[0]-0.5, H[1]-1, 1.5)
    hnd(H[0], H[1], fa, 2.5)
    legs(k, lg, H_TROUS, BOOT, boot_h=9, wk=1.15)
    tors = torso_pts(k, 52, 16.5, waist_w=15.5)
    form(tors, H_SMOCK, sdx=-2.4, sdy=1.2, sh=0.14)
    clip_fill(tors, [(-20, 52), (20, 52), (20, 56), (-20, 56)], H_SMOCK_DK)
    stroke([(1.2, k.sh_y+1), (1.6, 53)], LINE*0.8)
    for by in (90, 82, 74, 66): shape(ell(-0.6, by, 0.9, 0.9, 10), BRASS, LINE*0.5)
    for sx in (-1, 1):
        cl = [(sx*0.8, k.sh_y+0.6), (sx*5.5, k.sh_y+3.2), (sx*9.5, k.sh_y+0.6), (sx*3.6, k.sh_y-4.5)]
        shape(cl, H_SMOCK_DK, LINE*0.8)
    shape([(-15.8, 58), (15.8, 58), (16, 62), (-16, 62)], LEATHER, LINE*0.8)
    shape(rrect(2.5, 57.4, 4, 5.2, 0.6), BRASS, LINE*0.6)
    if not lamp_far: kahan(10, 58, 0.95)
    stroke(bez((-9, 86), (-9.5, 78), (-10.5, 70), (-11, 64)), LINE*0.5, g=H_SMOCK_DK)
    H, fa = arm(k, 1, near, H_SMOCK, hand=False, cuff=H_SMOCK_DK, open_=op)
    if wpn == "upright": pick(H[0], H[1], 72, 34, 14)
    elif wpn == "swing": pick(H[0], H[1], -16, 30, 22)
    elif wpn == "flung": pick(H[0], H[1], 115, 30, 10)
    hnd(H[0], H[1], fa, 2.5, open_=op)
    if wpn == "swing":
        F, _ = ik((-k.sh_w, k.sh_y-1.5), (24, 84), k.up, k.fo, -1)
        hnd(F[0], F[1], -20, 2.5)
    head(k, md, neck_w=3.2, do_face=False)
    cy = k.hy
    for sx in (-1, 1):
        shape(bez((sx*r*0.98, cy+r*0.45), (sx*r*1.08, cy+r*0.1), (sx*r*1.02, cy-r*0.2), (sx*r*0.9, cy-r*0.3)) +
              [(sx*r*0.8, cy+r*0.4)], H_BEARD, LINE*0.7)
    beard(k, H_BEARD, 1.25)
    face(r*0.2, cy, r*0.95, md)
    moustache(k, H_BEARD)
    cap = bez((-r*1.06, cy+r*0.55), (-r*1.12, cy+r*1.7), (r*1.12, cy+r*1.7), (r*1.06, cy+r*0.55)) + \
        bez((r*1.06, cy+r*0.55), (r*0.4, cy+r*0.68), (-r*0.4, cy+r*0.68), (-r*1.06, cy+r*0.55))
    form(cap, H_CAP, sdx=-1.5, sdy=1)
    shape(rrect(-r*1.1, cy+r*0.45, r*2.2, r*0.3, 0.8), LEATHER, LINE*0.8)
    shape([(r*0.2, cy+r*0.8), (r*0.58, cy+r*0.8), (r*0.58, cy+r*1.18), (r*0.2, cy+r*1.18)], BRASS, LINE*0.6)


def havir(x, y, s=S_HERO, pose="idle"):
    k = Person(**HAV)
    def drop():
        with T(x+40*s, y+15*s, s): pick(0, 0, 0, 30, 12)
    figure(havir_body, k, x, y, s, pose, 18, drop, lie_w=23)


# ------------------------------------------------------------------ ZBOJNICE
ZB = dict(H=120, hr=10.6, hy=108.5, sh_y=94, sh_w=11.8, hip=56, knee=30, ankle=5, leg_w=(7, 5.4),
          arm_w=(6.2, 5.4), up=18.5, fo=16.5)
Z_SHIRT = Col(0.85, "#d8cfbb")
Z_VEST = Col(0.36, "#43594b")
Z_SKIRT = Col(0.34, "#54465c")
Z_LEG = Col(0.55, "#857b6c")
Z_HAIR = Col(0.3, "#5e3a26")
Z_BELT = Col(0.32, "#6b4a2e")

ZB_POSE = {
    "idle": ("stand", ("a", -76, -12), ("a", -98, -86), "rest", False, "think"),
    "walk1": ("c1", ("a", -96, -38), ("a", -66, -38), "rest", False, "think"),
    "walk2": ("p1", ("a", -84, -22), ("a", -88, -68), "rest", False, "think"),
    "walk3": ("c2", ("a", -62, -2), ("a", -112, -98), "rest", False, "think"),
    "walk4": ("p2", ("a", -78, -16), ("a", -96, -78), "rest", False, "think"),
    "windup": ("brace", ("a", 112, 160), ("a", -40, -10), "chop_back", False, "determined"),
    "attack": ("lunge", ("a", 18, 2), ("a", -150, -165), "strike", False, "wow"),
    "cast": ("brace", ("a", 60, 85), ("a", -95, -70), "belt", True, "think"),
    "hit": ("brace", ("a", -25, 30), ("a", -150, -160), "flung", False, "worried"),
    "dead": ("lie", ("a", -84, -88), ("a", -96, -92), None, False, "sleepy"),
    "portrait": ("stand", ("a", -76, -12), ("a", -98, -86), "rest", False, "think"),
    "hero": ("brace", ("a", 55, 100), ("a", -110, -60), "raised", False, "think"),
}


def braid(x0, y0, x1, y1, w=3.4, col=Z_HAIR):
    tube(bez((x0, y0), (x0+(x1-x0)*0.2, y0-(y0-y1)*0.4), (x1, y1+(y0-y1)*0.3), (x1, y1)), w, w*0.7, col, LINE*0.8, sh=0)
    n = 6
    for i in range(1, n):
        t = i/n
        cx, cy = x0+(x1-x0)*t, y0+(y1-y0)*t
        ww = w*(1-0.3*t)*0.45
        stroke(bez((cx-ww, cy+ww*0.6), (cx-ww*0.3, cy-ww*0.3), (cx+ww*0.3, cy-ww*0.3), (cx+ww, cy+ww*0.6)), LINE*0.5)
    shape(rrect(x1-w*0.45, y1-0.2, w*0.9, 1.6, 0.4), RED, LINE*0.6)
    shape([(x1-w*0.3, y1-0.2), (x1+w*0.3, y1-0.2), (x1+w*0.5, y1-3), (x1-w*0.5, y1-3)], col, LINE*0.6)


def zbojnice_body(k, pose, mood=None):
    lg, near, far, wpn, op, md = ZB_POSE[pose]
    md = mood or md
    r = k.hr; cy = k.hy
    crossbow_back(k)
    braid(-r*0.8, cy-r*0.2, -r*1.15, cy-r*3.6)
    H, fa = arm(k, -1, far, Z_SHIRT, cuff=RED, open_=False)
    ph = legs(k, lg, Z_LEG, BOOT, boot_h=10)
    xs = [p[0][-1][0] for p in ph]
    sk = skirt_pts(60, 13.5, 34, min(-15, min(xs)-5), max(15, max(xs)+6))
    form(sk, Z_SKIRT, sdx=-2, sdy=1, sh=0.14)
    for xx in (-8, -2, 4, 10): stroke([(xx*0.7, 58), (xx, 36)], LINE*0.45, g=Col(0.25, "#3c3242"))
    tors = torso_pts(k, 58, 13.5, waist_w=11.5, collar=4)
    form(tors, Z_SHIRT, sdx=-2, sdy=1, sh=0.1)
    for sx in (-1, 1):
        v = [(sx*4.5, k.sh_y+2.4), (sx*(k.sh_w+1.6), k.sh_y-3.5), (sx*13.5, 72), (sx*13.5, 60), (sx*4, 60), (sx*3.2, 74)]
        form(v, Z_VEST, sdx=-1.5, sdy=1, sh=0.12)
        for yy in (86, 78, 70): dot(sx*4.2, yy, 0.8, RED)
    for i in range(5): dot(-2+i*1.0, k.sh_y+1.6-abs(i-2)*0.5, 0.55, RED)
    belt = [(-14.2, 58), (14.2, 58), (14.6, 67), (-14.6, 67)]
    form(belt, Z_BELT, sh=0.12)
    for xx in (-11, -6, -1, 4, 9): shape(ell(xx, 62.5, 1.1, 1.1, 10), BRASS, LINE*0.5)
    for xx in (-8.5, 6.5): stroke([(xx, 59), (xx, 66)], LINE*0.6)
    if wpn == "belt": valaska(6, 63, -100, 26, 4)
    H, fa = arm(k, 1, near, Z_SHIRT, hand=False, cuff=RED, open_=op)
    if wpn == "rest": valaska(H[0], H[1], 78, 30, 8)
    elif wpn == "strike": valaska(H[0], H[1], 35, 28, 6, flip=True)
    elif wpn == "flung": valaska(H[0], H[1], 120, 28, 6)
    elif wpn == "raised": valaska(H[0], H[1], 100, 28, 6)
    hnd(H[0], H[1], fa, 2.3, open_=op)
    braid(r*0.9, cy-r*0.55, r*0.75, cy-r*3.3)
    head(k, md, neck_w=2.5)
    hair = bez((-r*1.04, cy-r*0.1), (-r*1.2, cy+r*1.3), (r*1.2, cy+r*1.3), (r*1.04, cy-r*0.1)) + \
        bez((r*1.04, cy-r*0.1), (r*0.95, cy+r*0.45), (r*0.65, cy+r*0.62), (r*0.12, cy+r*0.72)) + \
        bez((r*0.12, cy+r*0.72), (-r*0.4, cy+r*0.62), (-r*0.9, cy+r*0.4), (-r*1.04, cy-r*0.1))
    form(hair, Z_HAIR, sdx=-1, sdy=0.6, sh=0.1)
    stroke(bez((r*0.12, cy+r*0.72), (r*0.1, cy+r*0.95), (r*0.05, cy+r*1.05), (0, cy+r*1.12)), LINE*0.5)
    shape(bez((-r*1.08, cy+r*0.35), (-r*0.5, cy+r*0.95), (r*0.5, cy+r*0.95), (r*1.08, cy+r*0.35)) +
          bez((r*1.08, cy+r*0.35), (r*1.1, cy+r*0.55), (r*0.5, cy+r*1.12), (-r*1.1, cy+r*0.55)), RED, LINE*0.6)


def zbojnice(x, y, s=S_HERO, pose="idle"):
    k = Person(**ZB)
    def drop():
        with T(x+44*s, y+3*s, s): valaska(0, 0, 0, 26, 6)
    figure(zbojnice_body, k, x, y, s, pose, 16, drop, lie_w=29)


# ------------------------------------------------------------------ VĚDMA
VE = dict(H=120, hr=10.6, hy=108.5, sh_y=94, sh_w=11.8, hip=56, knee=30, ankle=5, leg_w=(7, 5.4),
          arm_w=(6.4, 5.4), up=18.5, fo=16.5)
V_SHAWL = Col(0.36, "#5c4c70")
V_SHAWL_DK = Col(0.26, "#433756")
V_DRESS = Col(0.38, "#56603f")
V_BLOUSE = Col(0.78, "#c9bfa6")
V_HAIR = Col(0.25, "#3b3438")
V_HERB = Col(0.45, "#6f8a4a")

VE_POSE = {
    "idle": ("stand", ("k", 27, 80, -1), ("a", -98, -86), "stand", False, "think"),
    "walk1": ("c1", ("k", 24.5, 80, -1), ("a", -66, -40), "stand", False, "think"),
    "walk2": ("p1", ("k", 27, 80.5, -1), ("a", -88, -70), "stand", False, "think"),
    "walk3": ("c2", ("k", 30.5, 81.5, -1), ("a", -112, -98), "stand", False, "think"),
    "walk4": ("p2", ("k", 28, 80.5, -1), ("a", -96, -80), "stand", False, "think"),
    "windup": ("brace", ("a", -165, -5), ("a", -15, 5), "draw", False, "determined"),
    "attack": ("lunge", ("k", 38, 74, -1), ("k", 22, 77, -1), "thrust", False, "wow"),
    "cast": ("brace", ("k", 22, 118, 1), ("a", -140, -160), "raise", True, "think"),
    "hit": ("brace", ("a", -30, 25), ("a", -150, -160), "flung", False, "worried"),
    "dead": ("lie", ("a", -84, -88), ("a", -96, -92), None, False, "sleepy"),
    "portrait": ("stand", ("k", 27, 80, -1), ("a", -98, -86), "stand", False, "think"),
    "hero": ("brace", ("k", 22, 118, 1), ("a", -140, -160), "raise", True, "think"),
}


def vedma_body(k, pose, mood=None):
    lg, near, far, wpn, op, md = VE_POSE[pose]
    md = mood or md
    r = k.hr; cy = k.hy
    hood = bez((-r*1.35, cy-r*1.6), (-r*1.75, cy+r*0.6), (-r*1.1, cy+r*1.75), (r*0.2, cy+r*1.7)) + \
        bez((r*0.2, cy+r*1.7), (r*1.3, cy+r*1.6), (r*1.6, cy+r*0.6), (r*1.4, cy-r*1.4))
    form(hood, V_SHAWL, sdx=-1.5, sdy=1, sh=0.15)
    H, fa = arm(k, -1, far, V_SHAWL, cuff=V_BLOUSE, open_=op)
    ph = legs(k, lg, V_DRESS, BOOT, boot_h=6)
    xs = [p[0][-1][0] for p in ph]
    sk = skirt_pts(62, 13, 8, min(-17, min(xs)-6), max(17, max(xs)+6))
    form(sk, V_DRESS, sdx=-2.4, sdy=1, sh=0.15)
    for xx in (-10, -4, 3, 9): stroke(bez((xx*0.6, 58), (xx*0.8, 40), (xx, 25), (xx*1.1, 11)), LINE*0.45, g=Col(0.28, "#3f472d"))
    stroke(bez((-15, 18), (-5, 16.5), (5, 16.5), (16, 18)), LINE*0.6, g=RED)
    tors = torso_pts(k, 60, 13, waist_w=12, collar=4)
    form(tors, V_BLOUSE, sdx=-2, sdy=1, sh=0.1)
    shape([(-13.5, 59), (13.5, 59), (13.8, 64), (-13.8, 64)], RED, LINE*0.7)
    for i, xx in enumerate((-9, -6.5, -4)):
        tube([(xx, 60), (xx-1+i, 50)], 1.6, 1.2, V_HERB, LINE*0.6, sh=0)
        for j in range(3): shape(ell(xx-0.5+i*0.3, 51.5+j*2.5, 1.6, 0.8, 8, rot=30), V_HERB, LINE*0.4)
    shawl = [(-k.sh_w-2.5, k.sh_y+0.5)] + bez((-k.sh_w-2.5, k.sh_y+0.5), (-k.sh_w-3.2, 84), (-9, 72), (0, 68)) + \
        bez((0, 68), (9, 72), (k.sh_w+3.2, 84), (k.sh_w+2.5, k.sh_y+0.5)) + [(r*0.9, cy-r*0.6), (-r*0.9, cy-r*0.6)]
    form(shawl, V_SHAWL, sdx=-2, sdy=1, sh=0.14)
    for i in range(9):
        t = i/8
        px, py = (-9*(1-t)+9*t), 70-math.sin(t*math.pi)*-2
        stroke([(px, py), (px+0.3, py-3.5)], LINE*0.5)
    for i in range(7):
        a = math.radians(200+i*20)
        dot(math.cos(a)*6.5, k.sh_y-1+math.sin(a)*5, 1.0, BONE)
    H, fa = arm(k, 1, near, V_SHAWL, hand=False, cuff=V_BLOUSE, open_=op)
    if wpn == "stand": staff(H[0], H[1], 92, 58, 78)
    elif wpn == "thrust": staff(H[0], H[1], -4, 34, 40)
    elif wpn == "raise": staff(H[0], H[1], 96, 46, 48, glow=True)
    elif wpn == "flung": staff(H[0], H[1], 112, 48, 30)
    hnd(H[0], H[1], fa, 2.3, open_=op)
    if wpn == "thrust":
        F, _ = ik((-k.sh_w, k.sh_y-1.5), (22, 77), k.up, k.fo, -1)
        hnd(F[0], F[1], -10, 2.3)
    stroke(bez((H[0]-3, H[1]-2.5), (H[0]-1, H[1]-3.5), (H[0]+1, H[1]-3.5), (H[0]+3, H[1]-2.5)), LINE*0.9, g=RED)
    head(k, md, ear=False, neck_w=2.5)
    hair = bez((-r*1.04, cy-r*0.4), (-r*1.15, cy+r*1.2), (r*1.15, cy+r*1.2), (r*1.04, cy-r*0.2)) + \
        bez((r*1.04, cy-r*0.2), (r*0.9, cy+r*0.4), (r*0.6, cy+r*0.58), (r*0.2, cy+r*0.62)) + \
        bez((r*0.2, cy+r*0.62), (-r*0.3, cy+r*0.55), (-r*0.85, cy+r*0.3), (-r*1.04, cy-r*0.4))
    form(hair, V_HAIR, sdx=-1, sdy=0.6, sh=0.1)
    stroke(bez((-r*0.2, cy+r*0.6), (-r*0.5, cy+r*0.5), (-r*0.8, cy+r*0.2), (-r*0.95, cy-r*0.3)), LINE*1.4, g=Col(0.8, "#c8c2c8"))
    hf = bez((-r*1.25, cy-r*0.9), (-r*1.4, cy+r*0.9), (-r*0.6, cy+r*1.5), (r*0.2, cy+r*1.45)) + \
        bez((r*0.2, cy+r*1.45), (r*1.0, cy+r*1.4), (r*1.4, cy+r*0.9), (r*1.25, cy-r*0.6)) + \
        bez((r*1.25, cy-r*0.6), (r*1.3, cy+r*0.6), (r*0.8, cy+r*1.1), (r*0.2, cy+r*1.1)) + \
        bez((r*0.2, cy+r*1.1), (-r*0.6, cy+r*1.12), (-r*1.15, cy+r*0.6), (-r*1.05, cy-r*0.9))
    form(hf, V_SHAWL, sdx=-1, sdy=0.8, sh=0.12)
    stroke(bez((-r*1.2, cy+r*0.5), (-r*0.6, cy+r*1.3), (r*0.6, cy+r*1.3), (r*1.25, cy+r*0.6)), LINE*0.6, g=V_SHAWL_DK)


def vedma(x, y, s=S_HERO, pose="idle"):
    k = Person(**VE)
    def drop():
        with T(x-6*s, y+15*s, s): staff(0, 0, 2, 48, 40)
    figure(vedma_body, k, x, y, s, pose, 16, drop)


# ------------------------------------------------------------------ portraits, class art
def ring(cx, cy, r, a):
    p = C.beginPath(); p.rect(-500, -500, 2000, 2000); p.circle(cx, cy, r)
    C.saveState(); C.setFillColor(HexColor("#0b0a0e")); C.setFillAlpha(a)
    C.drawPath(p, fill=1, stroke=0, fillMode=0); C.restoreState()


def vignette(b, base="#3b3542", cx=0.5, cy=0.56, glow=None, rings=9):
    fill([(0, 0), (b.w, 0), (b.w, b.h), (0, b.h)], Col(0.25, base))
    if glow:
        for i in range(6):
            fill(ell(b.X(cx), b.Y(cy), b.w*(0.55-i*0.07), b.w*(0.55-i*0.07), 40), Col(0.6, glow, alpha=0.07))
    R = math.hypot(b.w, b.h)*0.62
    for i in range(rings):
        ring(b.X(cx), b.Y(cy), R*(1-i/(rings+2)), 0.11)
    hatch([(0, 0), (b.w, 0), (b.w, b.h*0.25), (0, b.h*0.1)], 2.2, 40, 0.45, 0.0, 0.25)


def portrait(b, fn, hy, hr, base="#3b3542", glow="#e8a55a", k=0.24, fy=0.5):
    vignette(b, base, glow=glow)
    s = b.w*k/hr
    fn(b.w*0.47, b.h*fy - hy*s, s, "portrait")


def gallery(b, glow_x, glow_y, glow="#ffb04a"):
    W, Hh = b.w, b.h
    fill([(0, 0), (W, 0), (W, Hh), (0, Hh)], Col(0.22, "#34303a"))
    vx, vy = W*0.5, Hh*0.5
    tun = ell(vx, vy-10, W*0.22, Hh*0.2, 40)
    fill(tun, Col(0.1, "#16141a"))
    for i in range(4):
        t = 0.35 + i*0.2
        lx, rx = vx-(vx-12)*t, vx+(W-12-vx)*t
        top = vy + (Hh-24-vy)*t; bot = vy - (vy-20)*t
        w = 4 + 10*t
        for xx in (lx, rx):
            post = [(xx-w/2, bot), (xx+w/2, bot), (xx+w/2*0.9, top), (xx-w/2*0.9, top)]
            form(post, Col(0.38, "#5a4636"), sdx=-2*t, sdy=0, sh=0.25)
            for j in range(3):
                yy = bot + (top-bot)*(0.2+j*0.3)
                stroke([(xx-w/2*0.7, yy), (xx+w/2*0.5, yy+w*0.6)], LINE*0.45, g=Col(0.25, "#3b2c22"))
        beam = [(lx-w*0.8, top-w*0.2), (rx+w*0.8, top-w*0.2), (rx+w*0.8, top+w*0.7), (lx-w*0.8, top+w*0.7)]
        form(beam, Col(0.36, "#57442f"), sdx=0, sdy=-2*t, sh=0.25)
    for sx in (-1, 1):
        stroke([(vx+sx*8, vy-Hh*0.18), (vx+sx*70, 0)], LINE*1.2, g=Col(0.5, "#7a7c84"))
    for i in range(7):
        t = (i+1)/8
        y_ = vy-Hh*0.18 - (vy-Hh*0.18)*t**1.4
        hw = 8+62*t**1.4
        stroke([(vx-hw-4*t, y_), (vx+hw+4*t, y_)], LINE*(0.8+1.5*t), g=Col(0.32, "#4a3a2c"))
    for i in range(7):
        fill(ell(glow_x, glow_y, 120-i*15, 120-i*15, 40), Col(0.7, glow, alpha=0.06))
    R = math.hypot(W, Hh)*0.6
    for i in range(8): ring(glow_x, glow_y, R*(1-i/10), 0.1)


def class_art(fn, gx, gy, glow="#ffb04a"):
    def draw(b):
        gallery(b, b.X(gx), b.Y(gy), glow)
        fn(b.w*0.47, 24, 1.85, "hero")
    return draw


POSES = ("idle", "walk1", "walk2", "attack", "cast", "hit", "dead")
HEROES = {"havir": (havir, HAV), "zbojnice": (zbojnice, ZB), "vedma": (vedma, VE)}


def sprite(fn, pose):
    return lambda b: fn(b.w/2, FEET, S_HERO, pose)


def jobs():
    pt = [(f"hero_{c}", 256, 256, (lambda fn, k: lambda b: portrait(b, fn, k["hy"], k["hr"]))(fn, k))
          for c, (fn, k) in HEROES.items()]
    ui = [("class_havir", 480, 720, class_art(havir, 0.28, 0.7), True),
          ("class_zbojnice", 480, 720, class_art(zbojnice, 0.5, 0.55), True),
          ("class_vedma", 480, 720, class_art(vedma, 0.6, 0.85, "#cfe0ff"), True)]
    return {"portraits": pt, "ui": ui}  # the in-game sprites come in layers from heroes_gear.py


if __name__ == "__main__":
    common.run(jobs())
