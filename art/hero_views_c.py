"""Front and back views of Alchymistka and Loutkářka (see hero_views.py)."""
from lib import ell, bez, rrect
from style3 import T, stroke, shape, form, fill, tube, dot, face, head_outline, clip_fill, LINE
import heroes as H
from heroes import SKIN, BOOT, LEATHER, WOOD, BRASS, braid
import heroes_new as N
from heroes_new import C_
from hero_views import Spec, SPECS, legs_fb, ears, torso_back_plain


def skirt_fb(top_y, top_w, hem, la, ra, pad):
    """a skirt whose hem swings out over each foot and lifts a little with a lifted one"""
    l, r = min(-top_w - 3.5, la[0] - pad), max(top_w + 3.5, ra[0] + pad)
    hl, hr = hem + max(0.0, la[1] - 5) * 0.4, hem + max(0.0, ra[1] - 5) * 0.4
    mid = min(hl, hr) - 1.5
    return [(-top_w, top_y), (top_w, top_y)] + bez((top_w, top_y), (top_w + 2, top_y - 12), (r - 2, hr + 10), (r, hr)) + \
        bez((r, hr), (r * 0.4, mid), (l * 0.4, mid), (l, hl)) + bez((l, hl), (l + 2, hl + 10), (-top_w - 2, top_y - 12), (-top_w, top_y))


def walk_arms(y0=60.5, x0=19):
    """near/far hand targets for idle + the four walk frames: the arm that swings toward the viewer rises and tucks in"""
    return {
        "idle": (("k", x0, y0, -1), ("k", -x0, y0, 1)),
        "walk1": (("k", x0 + 1, y0 + 0.5, -1), ("k", -x0 + 2, y0 + 5, 1)),
        "walk2": (("k", x0 + 0.5, y0, -1), ("k", -x0 + 0.5, y0 + 1.5, 1)),
        "walk3": (("k", x0 - 2, y0 + 5, -1), ("k", -x0 - 1, y0 + 0.5, 1)),
        "walk4": (("k", x0 - 0.5, y0 + 1.5, -1), ("k", -x0 - 0.5, y0, 1)),
    }


# ------------------------------------------------------------------ alchymistka
AL_STOCK = C_("#5a4a40", 0.35)
_aw = walk_arms()
AL_FB = {
    "idle": ("stand",) + _aw["idle"] + (("near", 78, 13, 3), False, "think"),
    "walk1": ("c1",) + _aw["walk1"] + (("near", 74, 13, 3), False, "think"),
    "walk2": ("p1",) + _aw["walk2"] + (("near", 77, 13, 3), False, "think"),
    "walk3": ("c2",) + _aw["walk3"] + (("near", 84, 13, 3), False, "think"),
    "walk4": ("p2",) + _aw["walk4"] + (("near", 80, 13, 3), False, "think"),
    "windup": ("brace", ("a", 70, 108), ("k", -16, 72, 1), ("near", 112, 13, 3), False, "determined"),
    "attack": ("lunge", ("k", 9, 76, -1), ("a", -150, -120), ("near", -60, 13, 3), False, "wow"),
    "cast": ("brace", ("a", 55, 95), ("k", -19, 62, 1), ("far", -95, 13, 3), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 118, 13, 3), False, "worried"),
}


def al_legs(k, phase, back):
    la, ra = legs_fb(k, phase, AL_STOCK, BOOT, 5, back)
    sk = skirt_fb(60, 13.5, 8, la, ra, 6)
    form(sk, N.AL_SKIRT, sdx=0, sdy=1, sh=0.15)
    for xx in (-9, -3, 3, 9):
        stroke(bez((xx * 0.6, 57), (xx * 0.8, 40), (xx, 25), (xx * 1.15, 11)), LINE * 0.4, g=C_("#232c48", 0.2))
    if back: return
    form([(-8, 58), (8, 58), (10, 20), (-10, 20)], C_("#cfc6b0", 0.8), sdx=0, sh=0.1)
    for (x, y, c) in ((-3, 40, "#86e05a"), (4, 30, "#7a5aa0"), (1, 48, "#c86a2a")):
        dot(x, y, 1.4, C_(c, 0.5))


def al_head(k, md, look, back):
    r = k.hr; cy = k.hy
    H.neck(k, SKIN, 2.4)
    ears(k)
    if back:
        form(head_outline(k), N.AL_HAIR, sdx=0, sdy=1, sh=0.12)
        for xx in (-0.5, -0.2, 0.2, 0.5):
            stroke(bez((r * xx, cy + r * 0.9), (r * xx * 1.1, cy + r * 0.4), (r * xx, cy - r * 0.1), (r * xx * 0.6, cy - r * 0.3)), LINE * 0.4, g=C_("#5a2e1a", 0.2))
        form(ell(0, cy - r * 0.45, r * 0.5, r * 0.36, 18), N.AL_HAIR, sdx=0, sdy=0.6, sh=0.18)
        stroke([(-r * 0.55, cy - r * 0.25), (-r * 0.15, cy - r * 0.38)], LINE * 0.7, g=BRASS)
        return
    shape(head_outline(k), SKIN)
    hair = bez((-r * 1.04, cy - r * 0.35), (-r * 1.18, cy + r * 1.25), (r * 1.18, cy + r * 1.25), (r * 1.04, cy - r * 0.35)) + \
        bez((r * 1.04, cy - r * 0.35), (r * 0.95, cy + r * 0.25), (r * 0.7, cy + r * 0.55), (r * 0.25, cy + r * 0.62)) + \
        bez((r * 0.25, cy + r * 0.62), (-r * 0.3, cy + r * 0.5), (-r * 0.8, cy + r * 0.35), (-r * 0.9, cy - r * 0.05)) + \
        bez((-r * 0.9, cy - r * 0.05), (-r * 0.95, cy - r * 0.2), (-r * 1.0, cy - r * 0.3), (-r * 1.04, cy - r * 0.35))
    form(hair, N.AL_HAIR, sdx=0, sdy=0.6, sh=0.1)
    if look != "velka_prilba":
        face(0, cy, r * 0.95, md)
        for sx in (-1, 1):
            stroke(ell(sx * r * 0.37, cy + r * 0.06, r * 0.22, r * 0.2, 14), LINE * 0.5, closed=True, g=C_("#3a3028", 0.2))
        stroke([(-r * 0.15, cy + r * 0.1), (r * 0.15, cy + r * 0.1)], LINE * 0.4)


def al_cap(k, back):
    r = k.hr; cy = k.hy
    form(ell(0, cy + r * 1.0, r * 1.25, r * 0.42, 24), N.AL_CAP, sdx=0, sdy=0.6, sh=0.15)
    stroke(bez((-r * 1.1, cy + r * 0.85), (-r * 0.4, cy + r * 0.72), (r * 0.4, cy + r * 0.72), (r * 1.1, cy + r * 0.85)), LINE * 0.5, g=C_("#3a3640", 0.25))
    tube(bez((r * 0.45, cy + r * 1.3), (r * 1.1, cy + r * 2.0), (r * 1.8, cy + r * 2.0), (r * 2.2, cy + r * 1.5)), 1.8, 0.6, C_("#e8e2d8", 0.92), LINE * 0.5, sh=0)


def al_torso_back(k):
    torso_back_plain(k, 58, 13.5, N.AL_BLOUSE, C_("#b8b0a0", 0.7), 11.5)
    form([(-10.5, k.sh_y - 6), (10.5, k.sh_y - 6), (11.5, 60), (-11.5, 60)], N.AL_BODICE, sdx=0, sdy=1, sh=0.14)
    stroke([(0, k.sh_y - 6.5), (0, 61)], LINE * 0.5, g=C_("#4a141c", 0.15))


def al_back(k, back):
    if not back: return
    stroke(bez((9.5, k.sh_y - 1), (4, 86), (-4, 80), (-10, 75)), LINE * 1.6, g=LEATHER)
    for sx in (-1, 1):
        shape(ell(sx * 2.6, 55, 2.8, 1.8, 12, rot=sx * 20), C_("#cfc6b0", 0.8), LINE * 0.5)
        shape([(sx * 0.8, 55), (sx * 2.5, 44), (sx * 4.2, 45.5)], C_("#cfc6b0", 0.8), LINE * 0.5)
    shape(ell(0, 55, 1.2, 1.4, 10), C_("#cfc6b0", 0.8), LINE * 0.5)
    for x, col in ((-13, "#86e05a"), (-9.5, "#a8d8ff")):
        tube([(x, 74), (x, 82)], 1.6, 1.2, C_("#c8d8d0", 0.85), LINE * 0.5, sh=0)
        dot(x, 76, 0.9, C_(col, 0.7))
    form(rrect(-16, 62, 10, 15, 2), LEATHER, sdx=0, sh=0.18)
    shape(rrect(-16, 71, 10, 6, 1.5), C_("#5a3a22", 0.24), LINE * 0.6)
    dot(-11, 72.5, 0.8, BRASS)


SPECS["alchymistka"] = Spec(AL_FB, al_legs, al_head, al_back, al_torso_back, al_cap, hand_r=2.3)


# ------------------------------------------------------------------ loutkářka
LO_STOCK = C_("#c8322e", 0.38)
_lw = walk_arms()
LO_FB = {
    "idle": ("stand", ("k", 18, 75, -1), _lw["idle"][1], ("near", 90, 58, 78), False, "think"),
    "walk1": ("c1", ("k", 18.5, 74, -1), _lw["walk1"][1], ("near", 92, 58, 78), False, "think"),
    "walk2": ("p1", ("k", 18, 75.5, -1), _lw["walk2"][1], ("near", 90, 58, 78), False, "think"),
    "walk3": ("c2", ("k", 17.5, 77, -1), _lw["walk3"][1], ("near", 88, 58, 78), False, "think"),
    "walk4": ("p2", ("k", 18, 75.5, -1), _lw["walk4"][1], ("near", 90, 58, 78), False, "think"),
    "windup": ("brace", ("k", 20, 98, -1), ("k", -16, 72, 1), ("near", 108, 46, 40), False, "determined"),
    "attack": ("lunge", ("k", 10, 82, -1), ("a", -150, -120), ("near", 58, 46, 40), False, "wow"),
    "cast": ("brace", ("a", 75, 95), ("a", -140, -160), ("near", 92, 46, 40), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 112, 46, 40), False, "worried"),
}


def lo_legs(k, phase, back):
    la, ra = legs_fb(k, phase, LO_STOCK, BOOT, 6, back)
    sk = skirt_fb(60, 13.5, 30, la, ra, 5)
    form(sk, N.LO_SKIRT, sdx=0, sdy=1, sh=0.14)
    clip_fill(sk, [(-30, 25), (30, 25), (30, 35), (-30, 35)], C_("#f2d060", 0.8))
    stroke(bez((-15, 35), (-5, 33.6), (5, 33.6), (15, 35)), LINE * 0.5)
    if back: return
    form([(-9, 58), (9, 58), (10, 34), (-10, 34)], C_("#f2eee2", 0.95), sdx=0, sh=0.08)
    for (x, y, c) in ((-5, 44, "#c8322e"), (0, 40, "#3a8a4a"), (5, 46, "#c8322e"), (-2, 50, "#f2b030"), (3, 52, "#3a8a4a")):
        dot(x, y, 1.1, C_(c, 0.45))


def lo_hair_front(k):
    r = k.hr; cy = k.hy
    hair = bez((-r * 1.05, cy - r * 0.45), (-r * 1.2, cy + r * 1.25), (r * 1.2, cy + r * 1.25), (r * 1.05, cy - r * 0.45)) + \
        bez((r * 1.05, cy - r * 0.45), (r * 0.95, cy + r * 0.2), (r * 0.6, cy + r * 0.55), (0, cy + r * 0.66)) + \
        bez((0, cy + r * 0.66), (-r * 0.6, cy + r * 0.55), (-r * 0.95, cy + r * 0.2), (-r * 1.05, cy - r * 0.45))
    form(hair, N.LO_HAIR, sdx=0, sdy=0.6, sh=0.1)
    stroke(bez((0, cy + r * 0.66), (0, cy + r * 0.8), (0, cy + r * 0.95), (0, cy + r * 1.05)), LINE * 0.5)


def lo_head(k, md, look, back):
    r = k.hr; cy = k.hy
    H.neck(k, SKIN, 2.4)
    ears(k)
    if back:
        form(head_outline(k), N.LO_HAIR, sdx=0, sdy=1, sh=0.1)
        stroke(bez((0, cy + r * 1.0), (r * 0.05, cy + r * 0.4), (-r * 0.05, cy - r * 0.2), (0, cy - r * 0.6)), LINE * 0.5)
        for sx in (-1, 1):
            braid(sx * r * 0.45, cy - r * 0.5, sx * r * 0.7, cy - r * 3.3, col=N.LO_HAIR)
        return
    for sx in (-1, 1):
        braid(sx * r * 0.85, cy - r * 0.3, sx * r * 1.05, cy - r * 3.1, col=N.LO_HAIR)
    shape(head_outline(k), SKIN)
    lo_hair_front(k)
    if look != "velka_prilba":
        face(0, cy, r * 0.95, md)


def lo_cap(k, back):
    r = k.hr; cy = k.hy
    lo = cy - r * 0.15 if back else cy + r * 0.62
    sc = bez((-r * 1.17, cy + r * 0.05), (-r * 1.3, cy + r * 1.6), (r * 1.3, cy + r * 1.6), (r * 1.17, cy + r * 0.05)) + \
        bez((r * 1.17, cy + r * 0.05), (r * 0.9, lo), (-r * 0.9, lo), (-r * 1.17, cy + r * 0.05))
    form(sc, N.LO_SCARF, sdx=0, sdy=1, sh=0.15)
    dots = ((-0.6, 1.15), (0, 1.35), (0.6, 1.15), (-0.3, 0.9), (0.3, 0.9)) if not back else \
        ((-0.6, 1.1), (0, 1.3), (0.6, 1.1), (-0.35, 0.6), (0.35, 0.6), (0, 0.2))
    for (x, y) in dots:
        shape(ell(r * x, cy + r * y, 1.1, 1.1, 10), C_("#f2d060", 0.8), LINE * 0.3)


def lo_cap_back(k, back):
    r = k.hr; cy = k.hy
    for dx in (-1.5, 1.8):
        shape([(0, cy - r * 0.2), (dx * 1.6 - r * 0.15, cy - r * 1.75), (dx * 1.6 + r * 0.4, cy - r * 1.6)], N.LO_SCARF, LINE * 0.5)
    if back:
        shape(ell(0, cy - r * 0.2, r * 0.3, r * 0.25, 12), N.LO_SCARF, LINE * 0.5)


def lo_torso_back(k):
    torso_back_plain(k, 58, 13.5, N.LO_BLOUSE, C_("#c8c2b4", 0.75), 11.5)
    v = [(-k.sh_w + 0.5, k.sh_y - 3)] + bez((-k.sh_w + 0.5, k.sh_y - 3), (-4, k.sh_y - 0.5), (4, k.sh_y - 0.5), (k.sh_w - 0.5, k.sh_y - 3)) + \
        [(12.5, 60), (-12.5, 60)]
    form(v, N.LO_VEST, sdx=0, sdy=1, sh=0.12)
    for (x, y) in ((-6, 84), (6, 84), (0, 78), (-6, 72), (6, 72), (0, 66)):
        dot(x, y, 0.9, C_("#f2d060", 0.85))


def lo_back(k, back):
    ox = -5 if back else -9
    for dx, L in ((-3, 24), (0, 30), (3, 21)):
        x0, x1 = ox + dx, ox - 4 + dx * 2.2
        tube([(x0, 76), (x1, 76 + L)], 1.6, 1.3, WOOD, LINE * 0.5, sh=0)
        shape(ell(x1, 76 + L, 1.6, 1.0, 10), BRASS, LINE * 0.4)
    if not back: return
    form(ell(ox, 72, 8, 9.5, 20), C_("#6a4a30", 0.32), sdx=0, sh=0.18)
    stroke(bez((ox - 6, 79), (ox - 2, 81), (ox + 2, 81), (ox + 6, 79)), LINE * 0.6, g=C_("#3e2a1a", 0.2))
    stroke(bez((ox + 4, 80), (2, 88), (6, 92), (10, k.sh_y - 1)), LINE * 1.4, g=LEATHER)
    with T(ox - 7, 64, 1, rot=10):
        head = bez((-3, 0), (-4, -6), (3, -8), (5, -3)) + bez((5, -3), (4, 0), (1, 1), (-3, 0))
        form(head, C_("#e8dcc0", 0.88), sh=0.12)
        for sx in (-1, 1):
            tube(bez((sx * 1.5, -6), (sx * 3, -10), (sx * 5, -11), (sx * 6, -9)), 1.2, 0.6, C_("#a8987a", 0.6), LINE * 0.4, sh=0)


SPECS["loutkarka"] = Spec(LO_FB, lo_legs, lo_head, lo_back, lo_torso_back, lo_cap, hand_r=2.3, cap_back=lo_cap_back)
