"""Zbojnice and vědma seen from the front and from the back (see hero_views.py)."""
import math
from lib import Col, bez, rrect
from style3 import T, stroke, shape, form, tube, dot, face, head_outline, LINE
import heroes as H
from heroes import SKIN, BOOT, BRASS, IRON, IRON_LT, WOOD, WOOD_LT, RED, BONE, braid
from hero_views import SPECS, Spec, legs_fb, ears, torso_back_plain

Z_SHIRT_DK = Col(0.62, "#b0a68f")
Z_SKIRT_DK = Col(0.25, "#3c3242")
Z_HAIR_BK = Col(0.24, "#4a2b1b")
V_BLOUSE_DK = Col(0.6, "#a59b82")
V_DRESS_DK = Col(0.28, "#3f472d")
V_STOCK = Col(0.3, "#4a4038")


def mood(md):
    """moods may carry a braid sway, 'think~1.5'"""
    m, _, sw = md.partition("~")
    return m, float(sw or 0)


def skirt(top_y, top_w, hl, hr, l, r, col, dk, folds, back):
    mid = (hl+hr)/2 - 1.5
    sk = [(-top_w, top_y), (top_w, top_y)] + bez((top_w, top_y), (top_w+2, top_y-12), (r-2, hr+10), (r, hr)) + \
        bez((r, hr), (r*0.4, mid+(hr-mid)*0.4), (l*0.4, mid+(hl-mid)*0.4), (l, hl)) + \
        bez((l, hl), (l+2, hl+10), (-top_w-2, top_y-12), (-top_w, top_y))
    form(sk, col, sdx=0, sdy=1, sh=0.14)
    for xx in folds:
        t = (xx-l)/(r-l)
        stroke(bez((xx*0.6, top_y-2), (xx*0.75, top_y-(top_y-hl)*0.4), (xx*0.95, mid+6), (xx*(1.02 if back else 1.0), hl+(hr-hl)*t+2)),
               LINE*0.45, g=dk)


def hem(base, ank, k_ank, gain):
    return base + max(-1.5, (ank[1]-k_ank)*gain)


# ------------------------------------------------------------------ zbojnice
ZB_FB = {
    "idle": ("stand", ("k", 20.5, 59.5, -1), ("k", -20.5, 59.5, 1), ("near", 84, 30, 8), False, "think"),
    "walk1": ("c1", ("k", 21.3, 60.5, -1), ("k", -18.3, 65, 1), ("near", 80, 30, 8), False, "think~-1.2"),
    "walk2": ("p1", ("k", 21, 60, -1), ("k", -19.6, 61.5, 1), ("near", 83, 30, 8), False, "think~-0.4"),
    "walk3": ("c2", ("k", 18.3, 65, -1), ("k", -21.3, 60.5, 1), ("near", 88, 30, 8), False, "think~1.2"),
    "walk4": ("p2", ("k", 19.6, 61.5, -1), ("k", -21, 60, 1), ("near", 85, 30, 8), False, "think~0.4"),
    "windup": ("brace", ("a", 75, 98), ("a", -140, -118), ("near", 100, 28, 6), False, "determined~-0.6"),
    "attack": ("lunge", ("k", 4, 68, -1), ("a", -160, -150), ("near", -55, 28, 6), False, "wow~2"),
    "cast": ("brace", ("a", 72, 96), ("k", -20.5, 59.5, 1), ("far", -95, 26, 4), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 118, 28, 6), False, "worried~-2.5"),
}


def zb_legs(k, phase, back):
    la, ra = legs_fb(k, phase, H.Z_LEG, BOOT, 10, back)
    skirt(60, 13.5, hem(34, la, k.ankle, 0.7), hem(34, ra, k.ankle, 0.7), min(-15, la[0]-5.5), max(15, ra[0]+5.5),
          H.Z_SKIRT, Z_SKIRT_DK, (-9, -3, 3, 9), back)


def zb_head(k, md, look, back):
    r = k.hr; cy = k.hy
    md, sw = mood(md)
    H.neck(k, SKIN, 2.5)
    if back:
        form(head_outline(k), Z_HAIR_BK, sdx=0, sdy=1, sh=0.12)
        stroke(bez((0, cy+r*1.15), (r*0.05, cy+r*0.6), (-r*0.05, cy), (0, cy-r*0.55)), LINE*0.5, g=Col(0.2, "#3e2618"))
        for sx in (-1, 1):
            stroke(bez((sx*r*0.3, cy+r*1.0), (sx*r*0.6, cy+r*0.6), (sx*r*0.6, cy), (sx*r*0.45, cy-r*0.5)), LINE*0.4, g=Col(0.2, "#3e2618"))
            braid(sx*r*0.42, cy-r*0.45, sx*r*0.6+sw, cy-r*3.6)
        return
    for sx in (-1, 1):
        braid(sx*r*0.92, cy-r*0.25, sx*r*1.08+sw, cy-r*3.3)
    ears(k)
    shape(head_outline(k), SKIN)
    if look != "velka_prilba":
        face(0, cy, r*0.95, md)
    hair = bez((-r*1.06, cy-r*0.2), (-r*1.22, cy+r*1.35), (r*1.22, cy+r*1.35), (r*1.06, cy-r*0.2)) + \
        bez((r*1.06, cy-r*0.2), (r*0.98, cy+r*0.4), (r*0.6, cy+r*0.64), (0, cy+r*0.56)) + \
        bez((0, cy+r*0.56), (-r*0.6, cy+r*0.64), (-r*0.98, cy+r*0.4), (-r*1.06, cy-r*0.2))
    form(hair, H.Z_HAIR, sdx=0, sdy=0.6, sh=0.1)
    stroke(bez((0, cy+r*0.56), (r*0.03, cy+r*0.8), (0, cy+r*1.0), (0, cy+r*1.15)), LINE*0.5)


def zb_cap(k, back):
    r = k.hr; cy = k.hy
    band = bez((-r*1.12, cy+r*0.5), (-r*0.5, cy+r*0.82), (r*0.5, cy+r*0.82), (r*1.12, cy+r*0.5)) + \
        bez((r*1.12, cy+r*0.5), (r*1.12, cy+r*0.3), (r*0.5, cy+r*0.58), (-r*1.12, cy+r*0.3))
    shape(band, RED, LINE*0.6)
    if back:
        for sx in (-1, 1):
            shape(bez((0, cy+r*0.6), (sx*r*0.2, cy+r*0.45), (sx*r*0.3, cy+r*0.2), (sx*r*0.36, cy-r*0.05)) +
                  [(sx*r*0.14, cy+r*0.02)], RED, LINE*0.5)
        shape([(-r*0.2, cy+r*0.42), (r*0.2, cy+r*0.42), (r*0.2, cy+r*0.78), (-r*0.2, cy+r*0.78)], RED, LINE*0.6)
    else:
        for xx in (-0.55, 0, 0.55): dot(r*xx, cy+r*(0.58 - abs(xx)*0.15), 0.6, Col(0.85, "#e8d9a8"))


def zb_crossbow(k, back):
    with T(10, 66, 1, rot=113.75):
        tube([(-2, 0), (50, 0)], 3.4, 2.8, WOOD, sh=0.1)
        shape(rrect(17, -1.7, 7, 3.4, 0.5), IRON, LINE*0.5)
        stroke(bez((22, 1.7), (21, 4), (19, 4.5), (18, 3)), LINE*0.6)
        bow = bez((45, -18), (51, -7), (51, 7), (45, 18))
        tube(bow, 3.0, 2.0, WOOD_LT, LINE*0.9, sh=0)
        stroke([(45, -18), (37, 0), (45, 18)], LINE*0.5)
        stroke(bez((51, -2.4), (55.5, -3.2), (56, 3.2), (51, 2.4)), LINE*1.0, g=IRON_LT)
        if back:
            for t in (6, 30): shape(rrect(t-1, -2, 2, 4, 0.4), BRASS, LINE*0.5)
    if back:
        stroke(bez((-9, 106), (-3, 97), (5, 82), (8, 68)), LINE*1.4, g=H.Z_BELT)


def zb_torso_back(k):
    torso_back_plain(k, 58, 13.5, H.Z_SHIRT, Z_SHIRT_DK, 11.5)
    v = [(-4.5, k.sh_y+2.2), (4.5, k.sh_y+2.2), (k.sh_w+1.6, k.sh_y-3.5), (13.5, 72), (13.5, 60), (-13.5, 60),
         (-13.5, 72), (-k.sh_w-1.6, k.sh_y-3.5)]
    form(v, H.Z_VEST, sdx=0, sdy=1, sh=0.12)
    stroke([(0, k.sh_y+1.6), (0, 61)], LINE*0.4, g=Col(0.26, "#33443a"))
    for sx in (-1, 1):
        for yy in (86, 78, 70): dot(sx*10.5, yy, 0.8, RED)
        for i in range(3):
            a = math.radians(90+sx*(35+i*28))
            dot(math.cos(a)*5, 76+math.sin(a)*5, 0.8, RED)
    dot(0, 76, 1.3, RED)
    stroke([(0, 74.5), (0, 66)], LINE*0.6, g=Col(0.5, "#6a8a5a"))
    for sx in (-1, 1): dot(sx*1.8, 68.5, 0.7, RED)


SPECS["zbojnice"] = Spec(ZB_FB, zb_legs, zb_head, zb_crossbow, zb_torso_back, zb_cap, hand_r=2.3)


# ------------------------------------------------------------------ vědma
VE_FB = {
    "idle": ("stand", ("k", 22, 80, -1), ("k", -19, 60, 1), ("near", 90, 58, 78), False, "think"),
    "walk1": ("c1", ("k", 22.5, 79.5, -1), ("k", -17.5, 64, 1), ("near", 87, 58, 78), False, "think"),
    "walk2": ("p1", ("k", 22, 80.5, -1), ("k", -18.5, 61.5, 1), ("near", 89, 58, 78), False, "think"),
    "walk3": ("c2", ("k", 21, 82, -1), ("k", -20, 59.5, 1), ("near", 93, 58, 78), False, "think"),
    "walk4": ("p2", ("k", 21.5, 81, -1), ("k", -19.5, 60, 1), ("near", 91, 58, 78), False, "think"),
    "windup": ("brace", ("k", 18, 100, -1), ("k", -16, 76, 1), ("near", 120, 46, 40), False, "determined"),
    "attack": ("lunge", ("k", 8, 74, -1), ("k", -6, 68, 1), ("near", 55, 46, 40), False, "wow"),
    "cast": ("brace", ("k", 21, 106, -1), ("a", -150, -125), ("near", 92, 46, 40), False, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 112, 46, 40), False, "worried"),
}


def ve_legs(k, phase, back):
    la, ra = legs_fb(k, phase, V_STOCK, BOOT, 6, back)
    dx = (la[1]-ra[1])*0.35
    hl, hr = hem(8, la, k.ankle, 0.45), hem(8, ra, k.ankle, 0.45)
    l, r = min(-17, la[0]-6)+dx, max(17, ra[0]+6)+dx
    skirt(62, 13, hl, hr, l, r, H.V_DRESS, V_DRESS_DK, (-10, -4, 3, 9), back)
    stroke(bez((l+2, hl+10), (l*0.35, (hl+hr)/2+8.5), (r*0.35, (hl+hr)/2+8.5), (r-2, hr+10)), LINE*0.6, g=RED)


def ve_head(k, md, look, back):
    r = k.hr; cy = k.hy
    H.neck(k, SKIN, 2.5)
    if back:
        hb = head_outline(k)
        form(hb, H.V_HAIR, sdx=0, sdy=1, sh=0.12)
        for sx in (-1, 1):
            stroke(bez((sx*r*0.3, cy+r*1.0), (sx*r*0.7, cy+r*0.5), (sx*r*0.8, cy-r*0.2), (sx*r*0.7, cy-r*0.8)), LINE*0.4, g=Col(0.18, "#2a2428"))
        stroke(bez((r*0.3, cy+r*1.0), (r*0.55, cy+r*0.4), (r*0.6, cy-r*0.2), (r*0.5, cy-r*0.8)), LINE*1.3, g=Col(0.8, "#c8c2c8"))
        return
    shape(head_outline(k), SKIN)
    if look != "velka_prilba":
        face(0, cy, r*0.95, md)
    hair = bez((-r*1.04, cy-r*0.4), (-r*1.18, cy+r*1.25), (r*1.18, cy+r*1.25), (r*1.04, cy-r*0.4)) + \
        bez((r*1.04, cy-r*0.4), (r*0.9, cy+r*0.3), (r*0.55, cy+r*0.6), (0, cy+r*0.62)) + \
        bez((0, cy+r*0.62), (-r*0.55, cy+r*0.6), (-r*0.9, cy+r*0.3), (-r*1.04, cy-r*0.4))
    form(hair, H.V_HAIR, sdx=0, sdy=0.6, sh=0.1)
    stroke(bez((-r*0.15, cy+r*0.64), (-r*0.5, cy+r*0.55), (-r*0.85, cy+r*0.2), (-r*0.95, cy-r*0.3)), LINE*0.9, g=Col(0.8, "#c8c2c8"))


def ve_hood(k, back):
    r = k.hr; cy = k.hy
    if back: return
    hf = bez((-r*1.28, cy-r*1.0), (-r*1.45, cy+r*0.9), (-r*0.8, cy+r*1.6), (0, cy+r*1.6)) + \
        bez((0, cy+r*1.6), (r*0.8, cy+r*1.6), (r*1.45, cy+r*0.9), (r*1.28, cy-r*1.0)) + \
        bez((r*1.28, cy-r*1.0), (r*1.2, cy+r*0.5), (r*0.8, cy+r*1.12), (0, cy+r*1.12)) + \
        bez((0, cy+r*1.12), (-r*0.8, cy+r*1.12), (-r*1.2, cy+r*0.5), (-r*1.28, cy-r*1.0))
    form(hf, H.V_SHAWL, sdx=0, sdy=0.8, sh=0.12)
    stroke(bez((-r*1.18, cy+r*0.5), (-r*0.6, cy+r*1.28), (r*0.6, cy+r*1.28), (r*1.18, cy+r*0.5)), LINE*0.6, g=H.V_SHAWL_DK)
    for sx in (-1, 1):
        stroke(bez((sx*r*1.33, cy-r*0.95), (sx*r*1.27, cy+r*0.55), (sx*r*0.85, cy+r*1.2), (0, cy+r*1.2)), LINE*0.5, g=RED)


def ve_hood_back(k, back):
    r = k.hr; cy = k.hy
    if not back:
        form(bez((-r*1.4, cy-r*1.65), (-r*1.72, cy+r*0.7), (-r*1.1, cy+r*1.8), (0, cy+r*1.85)) +
             bez((0, cy+r*1.85), (r*1.1, cy+r*1.8), (r*1.72, cy+r*0.7), (r*1.4, cy-r*1.65)), H.V_SHAWL, sdx=0, sdy=1, sh=0.15)
        return
    w, sy = k.sh_w+7, k.sh_y-5
    half = bez((0, cy+r*1.6), (r*0.9, cy+r*1.6), (r*1.36, cy+r*0.8), (r*1.22, cy-r*0.45)) + \
        bez((r*1.22, cy-r*0.45), (r*1.2, cy-r*1.0), (w-5, k.sh_y+1), (w, sy)) + bez((w, sy), (w-1, 84), (8, 71), (0, 64))
    form(half + [(-x, y) for x, y in reversed(half)], H.V_SHAWL, sdx=0, sdy=1, sh=0.15)
    for sx in (-1, 1):
        stroke(bez((sx*r*0.55, cy+r*1.45), (sx*r*0.85, cy+r*0.6), (sx*r*0.8, cy-r*0.5), (sx*r*1.2, cy-r*1.7)), LINE*0.45, g=H.V_SHAWL_DK)
        stroke(bez((sx*(w-1.5), sy+0.5), (sx*(w-2.5), 84), (sx*7, 73), (0, 67)), LINE*0.55, g=RED)
        for i in range(7):
            t = i/7
            x0, y0 = sx*(w-t*w), sy-t*(sy-64)
            stroke([(x0, y0), (x0-sx*0.4, y0-3)], LINE*0.45)
    stroke(bez((0, cy+r*1.7), (r*0.06, cy+r*0.6), (-r*0.06, cy-r*1.4), (0, 66)), LINE*0.5, g=H.V_SHAWL_DK)


def ve_back(k, back):
    pass


def ve_torso_back(k):
    torso_back_plain(k, 60, 13, H.V_BLOUSE, V_BLOUSE_DK, 12)


SPECS["vedma"] = Spec(VE_FB, ve_legs, ve_head, ve_back, ve_torso_back, ve_hood, hand_r=2.3, cap_back=ve_hood_back)
