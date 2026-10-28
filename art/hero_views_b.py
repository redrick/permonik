"""Kovář, Žrec and Vlkodlak seen from the front and from the back (see hero_views.py)."""
import math
from lib import Col, ell, bez, rrect
from style3 import stroke, shape, form, fill, hatch, tube, clip_fill, dot, face, head_outline, LINE
import heroes as H
from heroes import SKIN, BOOT
import heroes_new as N
from hero_views import Spec, SPECS, LEGS_FB, legs_fb, ears, torso_back_plain


def nothing(*a):
    pass


def side_tufts(k, col):
    r = k.hr; cy = k.hy
    for sx in (-1, 1):
        shape(bez((sx*r*0.7, cy-r*0.5), (sx*r*1.05, cy-r*0.7), (sx*r*0.9, cy-r*1.2), (sx*r*0.4, cy-r*1.3)) +
              [(sx*r*0.3, cy-r*0.8)], col, LINE*0.7)


# ------------------------------------------------------------------ kovář
KO_FB = {
    "idle": ("stand", ("k", 24.5, 63, -1), ("k", -24.5, 63, 1), ("near", 84, 30), False, "think"),
    "walk1": ("c1", ("k", 25.5, 64, -1), ("k", -22, 68.5, 1), ("near", 80, 30), False, "think"),
    "walk2": ("p1", ("k", 25, 63.5, -1), ("k", -23.5, 65, 1), ("near", 83, 30), False, "think"),
    "walk3": ("c2", ("k", 22, 68.5, -1), ("k", -25.5, 64, 1), ("near", 88, 30), False, "think"),
    "walk4": ("p2", ("k", 23.5, 65, -1), ("k", -25, 63.5, 1), ("near", 85, 30), False, "think"),
    "windup": ("brace", ("a", 95, 105), ("a", 85, 75), ("near", 96, 30), False, "determined"),
    "attack": ("lunge", ("k", 5, 72, -1), ("k", -2, 74, 1), ("near", -58, 30), False, "wow"),
    "cast": ("brace", ("a", 72, 96), ("k", -24.5, 63, 1), ("far", -92, 30), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 118, 30), False, "worried"),
}
KO_SHIRT_D = Col(0.62, "#a89c84")


def ko_legs(k, phase, back):
    legs_fb(k, phase, N.KO_TROUS, BOOT, 10, back, kx=1.1)


def ko_head(k, md, look, back):
    r = k.hr; cy = k.hy
    H.neck(k, SKIN, 3.4)
    ears(k)
    shape(head_outline(k), SKIN)
    if back:
        side_tufts(k, N.KO_BEARD)
        clip_fill(head_outline(k), [(-r*2, cy-r*2), (r*2, cy-r*2), (r*2, cy+r*0.15)] +
                  bez((r*0.95, cy+r*0.1), (r*0.5, cy-r*0.45), (-r*0.5, cy-r*0.45), (-r*0.95, cy+r*0.1)) + [(-r*2, cy+r*0.15)], N.KO_BEARD)
        for xx in (-0.45, -0.15, 0.15, 0.45):
            stroke([(r*xx, cy-r*0.45), (r*xx*0.95, cy-r*0.8)], LINE*0.4, g=Col(0.15, "#3a2414"))
        stroke(bez((-r*0.35, cy+r*0.55), (-r*0.1, cy+r*0.68), (r*0.1, cy+r*0.68), (r*0.35, cy+r*0.55)), LINE*0.4, g=Col(0.7, "#c8a88a"))
        return
    for sx in (-1, 1):
        stroke(bez((sx*r*0.68, cy+r*0.5), (sx*r*0.5, cy+r*0.62), (sx*r*0.3, cy+r*0.6), (sx*r*0.1, cy+r*0.48)), LINE*0.9, g=N.KO_BEARD)
    H.beard(k, N.KO_BEARD, 1.75, line=Col(0.15, "#3a2414"), dx=0)
    face(0, cy, r*0.95, md)
    H.moustache(k, N.KO_BEARD, dx=0, w=0.65)


def ko_torso_back(k):
    torso_back_plain(k, 52, 16.5, N.KO_SHIRT, KO_SHIRT_D, 15.5)
    for sx in (-1, 1):
        stroke([(sx*7, k.sh_y+1), (-sx*9, 62)], LINE*1.3, g=N.KO_APRON)
        form([(sx*13.2, 60), (sx*16, 59), (sx*16.5, 30), (sx*14, 30.5)], N.KO_APRON, sdx=0, sdy=1, sh=0.16)
    for sx in (-1, 1):
        shape(ell(sx*2.6, 56, 2.6, 1.5, 12, rot=sx*20), N.KO_APRON, LINE*0.6)
        stroke(bez((sx*0.8, 55.5), (sx*2, 52), (sx*1.6, 49), (sx*2.6, 46)), LINE*1.1, g=N.KO_APRON)


SPECS["kovar"] = Spec(KO_FB, ko_legs, ko_head, nothing, ko_torso_back, nothing)


# ------------------------------------------------------------------ žrec
ZR_FB = {
    "idle": ("stand", ("k", 22, 72, -1), ("k", -21, 64, 1), ("near", 90, 58), False, "think"),
    "walk1": ("c1", ("k", 22.5, 73, -1), ("k", -19, 68.5, 1), ("near", 88, 58), False, "think"),
    "walk2": ("p1", ("k", 22, 72.5, -1), ("k", -20.5, 65.5, 1), ("near", 89, 58), False, "think"),
    "walk3": ("c2", ("k", 21, 70.5, -1), ("k", -22, 63, 1), ("near", 93, 58), False, "think"),
    "walk4": ("p2", ("k", 21.5, 71.5, -1), ("k", -21.5, 64.5, 1), ("near", 91, 58), False, "think"),
    "windup": ("brace", ("a", 95, 105), ("a", -150, -115), ("near", 100, 30), True, "determined"),
    "attack": ("lunge", ("k", 5, 74, -1), ("k", -3, 76, 1), ("near", -66, 30), False, "wow"),
    "cast": ("brace", ("a", 70, 94), ("a", -148, -168), ("near", 96, 30), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 118, 30), False, "worried"),
}
ZR_LINEN_D = Col(0.72, "#c4bca6")
ZR_HAIR_D = Col(0.7, "#b8b2a8")


def zr_cloak(k, back):
    cl = [(-k.sh_w-2, k.sh_y+1), (k.sh_w+2, k.sh_y+1)] + bez((k.sh_w+2, k.sh_y+1), (k.sh_w+6, 70), (k.sh_w+8, 40), (k.sh_w+7, 16)) + \
        bez((k.sh_w+7, 16), (6, 14), (-6, 14), (-k.sh_w-7, 16)) + bez((-k.sh_w-7, 16), (-k.sh_w-8, 40), (-k.sh_w-6, 70), (-k.sh_w-2, k.sh_y+1))
    form(cl, N.ZR_FUR, sdx=0, sdy=1, sh=0.18)
    hatch(cl, 1.5, 80, 0.35, alpha=0.3)
    if back:
        stroke(bez((0, k.sh_y), (0.5, 70), (-0.5, 40), (0, 15)), LINE*0.5, g=Col(0.25, "#4a3826"))
        shape(bez((-k.sh_w-3, k.sh_y+2), (-8, k.sh_y-3), (8, k.sh_y-3), (k.sh_w+3, k.sh_y+2)) +
              bez((k.sh_w+3, k.sh_y+2), (8, k.sh_y+4), (-8, k.sh_y+4), (-k.sh_w-3, k.sh_y+2)), Col(0.5, "#8a7050"), LINE*0.7)


def zr_legs(k, phase, back):
    (lx, _), (rx, _) = legs_fb(k, phase, N.ZR_LINEN, Col(0.3, "#4e3a2a"), 5, back)
    sk = H.skirt_pts(62, 13, 7, min(-16, lx-6), max(16, rx+6))
    form(sk, N.ZR_LINEN, sdx=0, sdy=1, sh=0.12)
    clip_fill(sk, [(-30, 7), (30, 7), (30, 12), (-30, 12)], N.ZR_RED)
    for xx in (-9, -3, 3, 9):
        stroke(bez((xx*0.6, 58), (xx*0.8, 40), (xx, 25), (xx*1.1, 12)), LINE*0.4, g=ZR_LINEN_D)


def zr_head(k, md, look, back):
    r = k.hr; cy = k.hy
    if back:
        zr_cloak(k, True)
        H.neck(k, SKIN, 2.6)
        form(head_outline(k), N.ZR_HAIR, sdx=0, sdy=0.6, sh=0.1)
        mane = bez((-r*1.04, cy+r*0.3), (-r*1.4, cy-r*1.0), (-r*1.5, cy-r*2.4), (-r*1.0, cy-r*3.2)) + \
            bez((-r*1.0, cy-r*3.2), (-r*0.3, cy-r*3.45), (r*0.3, cy-r*3.45), (r*1.0, cy-r*3.2)) + \
            bez((r*1.0, cy-r*3.2), (r*1.5, cy-r*2.4), (r*1.4, cy-r*1.0), (r*1.04, cy+r*0.3)) + \
            bez((r*1.04, cy+r*0.3), (r*0.6, cy+r*0.9), (-r*0.6, cy+r*0.9), (-r*1.04, cy+r*0.3))
        form(mane, N.ZR_HAIR, sdx=0, sdy=0.8, sh=0.12)
        for xx in (-0.7, -0.35, 0, 0.35, 0.7):
            stroke(bez((r*xx*0.8, cy+r*0.6), (r*xx, cy-r*0.6), (r*xx*1.15, cy-r*1.8), (r*xx*1.05, cy-r*3.0)), LINE*0.4, g=ZR_HAIR_D)
        return
    H.neck(k, SKIN, 2.6)
    for sx in (-1, 1):
        lock = bez((sx*r*0.85, cy+r*0.5), (sx*r*1.35, cy+r*0.1), (sx*r*1.4, cy-r*1.2), (sx*r*1.2, cy-r*2.0)) + \
            bez((sx*r*1.2, cy-r*2.0), (sx*r*0.95, cy-r*1.6), (sx*r*0.85, cy-r*0.8), (sx*r*0.8, cy-r*0.2))
        form(lock, N.ZR_HAIR, sdx=0, sdy=0.6, sh=0.1)
    shape(head_outline(k), SKIN)
    H.beard(k, N.ZR_HAIR, 2.4, line=ZR_HAIR_D, dx=0)
    face(0, cy, r*0.95, md)
    H.moustache(k, N.ZR_HAIR, dx=0, w=0.6)
    top = bez((-r*1.04, cy+r*0.2), (-r*1.15, cy+r*1.25), (r*1.15, cy+r*1.25), (r*1.04, cy+r*0.2)) + \
        bez((r*1.04, cy+r*0.2), (r*0.8, cy+r*0.68), (r*0.2, cy+r*0.8), (0, cy+r*0.7)) + \
        bez((0, cy+r*0.7), (-r*0.2, cy+r*0.8), (-r*0.8, cy+r*0.68), (-r*1.04, cy+r*0.2))
    form(top, N.ZR_HAIR, sdx=0, sdy=0.6, sh=0.1)
    stroke(bez((0, cy+r*0.72), (0.2, cy+r*0.9), (-0.2, cy+r*1.05), (0, cy+r*1.15)), LINE*0.45, g=ZR_HAIR_D)


def zr_back_item(k, back):
    if not back: zr_cloak(k, False)


def zr_torso_back(k):
    torso_back_plain(k, 62, 13.5, N.ZR_LINEN, ZR_LINEN_D, 12.5)


def zr_wreath(k, back):
    r = k.hr; cy = k.hy
    for i in range(12):
        t = i/11
        x = -r*1.08 + t*r*2.16
        y = cy + r*0.88 - math.sin(t*math.pi)*r*0.12
        shape(ell(x, y, 2.2, 1.2, 10, rot=(t-0.5)*-70 + (25 if i % 2 else -25)), N.ZR_LEAF, LINE*0.4)
    for sx in (-1, 1):
        dot(sx*r*0.95, cy+r*0.9, 0.9, Col(0.5, "#a87a3a"))


SPECS["zrec"] = Spec(ZR_FB, zr_legs, zr_head, zr_back_item, zr_torso_back, zr_wreath, hand_r=2.3)


# ------------------------------------------------------------------ vlkodlak
class Mood(str):
    """a mood that also carries how far the cape swings (the head hook gets no pose)"""
    def __new__(cls, s, sway=0):
        m = super().__new__(cls, s)
        m.sway = sway
        return m


VL_FB = {
    "idle": ("stand", ("k", 21.5, 63, -1), ("k", -21.5, 63, 1), ("near", 72, 30), False, "think"),
    "walk1": ("c1", ("k", 22.5, 64, -1), ("k", -19, 68.5, 1), ("near", 68, 30), False, Mood("think", -2)),
    "walk2": ("p1", ("k", 22, 63.5, -1), ("k", -20.5, 65, 1), ("near", 71, 30), False, Mood("think", -0.7)),
    "walk3": ("c2", ("k", 19, 68.5, -1), ("k", -22.5, 64, 1), ("near", 76, 30), False, Mood("think", 2)),
    "walk4": ("p2", ("k", 20.5, 65, -1), ("k", -22, 63.5, 1), ("near", 73, 30), False, Mood("think", 0.7)),
    "windup": ("brace", ("a", 70, 125), ("k", -12, 80, 1), ("near", 115, 30), False, Mood("determined", 0.8)),
    "attack": ("lunge", ("k", 8, 76, -1), ("a", -160, -175), ("near", -75, 30), False, Mood("wow", -1.5)),
    "cast": ("brace", ("a", 72, 96), ("k", -21.5, 63, 1), ("far", -92, 30), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 118, 30), False, Mood("worried", 2.5)),
}
VL_JERK_D = Col(0.25, "#3a4428")


def vl_legs(k, phase, back):
    legs_fb(k, phase, N.VL_TROUS, BOOT, 9, back)
    for hx, kxx, kdy, ax, lift, sc in LEGS_FB[phase]:
        kn, an = (kxx, k.knee+kdy), (ax, k.ankle+lift)
        for t in (0.25, 0.5, 0.75):
            x, y = kn[0]+(an[0]-kn[0])*t, kn[1]+(an[1]-kn[1])*t
            stroke([(x-3.3*sc, y-1.2), (x+3.3*sc, y+1.2)], LINE*0.8, g=Col(0.8, "#c8bba0"))


def vl_cape(k, back, sw=0):
    w = k.sh_w
    if not back:
        cp = [(-w-1, k.sh_y+2), (w+1, k.sh_y+2)] + bez((w+1, k.sh_y+2), (w+5, 84), (w+4.5, 70), (w+2.5, 62)) + \
            [(5, 58), (-5, 58)] + bez((-w-2.5, 62), (-w-4.5, 70), (-w-5, 84), (-w-1, k.sh_y+2))
        form(cp, N.VL_PELT, sdx=0, sdy=1, sh=0.18)
        return
    top = k.sh_y+2.5
    hem = [(w-1.5+sw, 67), (w-4+sw, 64.5), (w-6.5+sw, 67.5), (6.5+sw, 64.5), (4+sw, 66.5)]
    cp = [(-w-2, top)] + bez((-w-2, top), (-6, top+3), (6, top+3), (w+2, top)) + \
        bez((w+2, top), (w+3, k.sh_y-5), (w, 84), (w-1.5+sw*0.4, 72)) + hem + \
        [(-x+2*sw, y) for x, y in reversed(hem)] + bez((-w+1.5+sw*0.4, 72), (-w, 84), (-w-3, k.sh_y-5), (-w-2, top))
    form(cp, N.VL_PELT, sdx=0, sdy=1, sh=0.18)
    hatch(cp, 1.4, 75, 0.35, alpha=0.3)
    stripe = bez((-4, top+1), (-4.5, 88), (-3, 76), (-2+sw*0.6, 67)) + bez((2+sw*0.6, 67), (3, 76), (4.5, 88), (4, top+1))
    fill(stripe, N.VL_PELT_D)
    fur = Col(0.25, "#3a3734")
    for y in range(int(k.sh_y-3), 70, -6):
        stroke(bez((-2.2, y), (-0.8, y-2.2), (0.8, y-2.2), (2.2, y)), LINE*0.4, g=fur)
    for sx in (-1, 1):
        for y in (92, 84, 76):
            x = sx*(w-0.5)
            stroke([(x, y), (x+sx*1.6, y-2.4)], LINE*0.45, g=fur)
    tail = bez((sw*0.5, 68), (sw*0.8, 60), (sw*1.3, 54), (sw*1.8, 47))
    tube(tail, 6.5, 3.6, N.VL_PELT, LINE*0.8, sh=0.15)
    tube(bez((sw*0.5, 67), (sw*0.75, 62), (sw*1.0, 58), (sw*1.2, 55)), 2.4, 1.2, N.VL_PELT_D, 0, sh=0)
    tip = bez((sw*1.6+2, 50), (sw*1.7+1.4, 47.6), (sw*1.8+0.6, 46.4), (sw*1.8, 46)) + \
        bez((sw*1.8, 46), (sw*1.8-0.6, 46.4), (sw*1.7-1.4, 47.6), (sw*1.6-2, 50))
    shape(tip, Col(0.88, "#e6e2da"), LINE*0.5)


def vl_head(k, md, look, back):
    r = k.hr; cy = k.hy
    if back:
        vl_cape(k, True, getattr(md, "sway", 0))
        H.neck(k, SKIN, 2.8)
        ears(k)
        form(head_outline(k), N.VL_HAIR, sdx=0, sdy=0.6, sh=0.1)
        for xx in (-0.45, -0.15, 0.15, 0.45):
            stroke(bez((r*xx, cy+r*0.6), (r*xx*1.1, cy+r*0.1), (r*xx, cy-r*0.4), (r*xx*0.9, cy-r*0.8)), LINE*0.4, g=Col(0.08, "#1a1410"))
        return
    H.neck(k, SKIN, 2.8)
    ears(k)
    shape(head_outline(k), SKIN)
    for i in range(18):
        a = math.radians(205 + i*7.5)
        dot(math.cos(a)*r*0.82, cy - r*0.12 + math.sin(a)*r*0.72, 0.32, N.VL_HAIR)
    face(0, cy, r*0.95, md)
    hair = bez((-r*1.04, cy+r*0.1), (-r*1.1, cy+r*1.15), (r*1.1, cy+r*1.15), (r*1.04, cy+r*0.1)) + \
        bez((r*1.04, cy+r*0.1), (r*0.6, cy+r*0.62), (r*0.2, cy+r*0.5), (0, cy+r*0.62)) + \
        bez((0, cy+r*0.62), (-r*0.2, cy+r*0.5), (-r*0.6, cy+r*0.62), (-r*1.04, cy+r*0.1))
    form(hair, N.VL_HAIR, sdx=0, sdy=0.6, sh=0.1)


def vl_back_item(k, back):
    if not back: vl_cape(k, False)


def vl_torso_back(k):
    torso_back_plain(k, 54, 15.5, N.VL_JERK, VL_JERK_D, 14)


def wolf_ears(k):
    r = k.hr; cy = k.hy
    for sx in (-1, 1):
        ear = bez((sx*r*1.02, cy+r*0.95), (sx*r*1.05, cy+r*1.6), (sx*r*0.95, cy+r*2.1), (sx*r*0.82, cy+r*2.4)) + \
            bez((sx*r*0.82, cy+r*2.4), (sx*r*0.6, cy+r*2.0), (sx*r*0.35, cy+r*1.6), (sx*r*0.2, cy+r*1.2))
        form(ear, N.VL_PELT_D, sdx=0, sdy=0.6, sh=0.12)
        stroke(bez((sx*r*0.85, cy+r*1.3), (sx*r*0.85, cy+r*1.7), (sx*r*0.82, cy+r*2.0), (sx*r*0.8, cy+r*2.2)), LINE*0.4, g=Col(0.6, "#a89a8a"))


def vl_hood(k, back):
    r = k.hr; cy = k.hy
    if back: return
    wolf_ears(k)
    top = bez((-r*1.15, cy+r*0.4), (-r*1.2, cy+r*1.6), (r*1.2, cy+r*1.6), (r*1.15, cy+r*0.4)) + \
        bez((r*1.15, cy+r*0.4), (r*0.5, cy+r*0.6), (-r*0.5, cy+r*0.6), (-r*1.15, cy+r*0.4))
    form(top, N.VL_PELT, sdx=0, sdy=1, sh=0.16)
    snout = bez((-r*0.5, cy+r*1.1), (-r*0.62, cy+r*0.7), (-r*0.45, cy+r*0.42), (0, cy+r*0.4)) + \
        bez((0, cy+r*0.4), (r*0.45, cy+r*0.42), (r*0.62, cy+r*0.7), (r*0.5, cy+r*1.1))
    form(snout, Col(0.66, "#a8a29a"), w=LINE*0.7, sdx=0, sdy=0.6, sh=0.12)
    shape([(-r*0.16, cy+r*0.56), (r*0.16, cy+r*0.56), (0, cy+r*0.44)], Col(0.06, "#141210"), LINE*0.3)
    for sx in (-1, 1):
        shape(ell(sx*r*0.68, cy+r*1.12, r*0.13, r*0.09, 10), Col(0.85, "#e8c040"), LINE*0.35)


def vl_hood_back(k, back):
    r = k.hr; cy = k.hy
    if back:
        wolf_ears(k)
        skull = bez((-r*0.95, cy-r*1.5), (-r*1.25, cy-r*0.6), (-r*1.25, cy+r*1.35), (0, cy+r*1.4)) + \
            bez((0, cy+r*1.4), (r*1.25, cy+r*1.35), (r*1.25, cy-r*0.6), (r*0.95, cy-r*1.5))
        form(skull, N.VL_PELT, sdx=0, sdy=1, sh=0.16)
        hatch(skull, 1.4, 80, 0.35, alpha=0.25)
        fill(bez((-r*0.22, cy+r*1.38), (-r*0.4, cy+r*0.6), (-r*0.38, cy-r*0.6), (-r*0.32, cy-r*1.5)) +
             bez((r*0.32, cy-r*1.5), (r*0.38, cy-r*0.6), (r*0.4, cy+r*0.6), (r*0.22, cy+r*1.38)), N.VL_PELT_D)
        for i in range(6):
            x = -r*0.95 + i*r*0.38
            stroke([(x, cy-r*1.2), (x+r*0.12, cy-r*1.55)], LINE*0.45, g=Col(0.2, "#3a3734"))
        return
    hood = bez((-r*1.2, cy-r*1.3), (-r*1.45, cy+r*0.8), (-r*1.05, cy+r*1.5), (0, cy+r*1.55)) + \
        bez((0, cy+r*1.55), (r*1.05, cy+r*1.5), (r*1.45, cy+r*0.8), (r*1.2, cy-r*1.3))
    form(hood, N.VL_PELT, sdx=0, sdy=1, sh=0.15)


SPECS["vlkodlak"] = Spec(VL_FB, vl_legs, vl_head, vl_back_item, vl_torso_back, vl_hood, hand_r=2.3, cap_back=vl_hood_back)
