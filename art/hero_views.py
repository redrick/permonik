"""Heroes seen from the front (walking down the screen) and from the back (walking up).

Same layers and looks as heroes_gear.py, rendered into <pose>_f/ and <pose>_b/. The back view is the
front view mirrored, so the weapon stays in the same hand when the hero turns.

Each class registers a Spec in SPECS (havíř here, the rest in hero_views_*.py). A Spec gives the pose
tables and the drawings that differ per class; everything else (sleeves, hands, weapons, belts, lamps,
off-hands, helmets) is shared.
"""
import math
from lib import Col, ell, bez, rrect
from style3 import C, T, stroke, shape, form, fill, hatch, tube, cast_shadow, dot, face, head_outline, LINE
import heroes as H
from heroes import SKIN, BOOT, LEATHER, BRASS, IRON, hnd, torso_pts
import heroes_gear as G

VIEWS = {"front": "_f", "back": "_b"}
ORDER = {
    "front": G.LAYERS,
    "back": ("body_far", "weapon_far", "lamp_far", "hand_far", "offhand", "lamp", "legs", "body", "back", "belt",
             "weapon_belt", "body_near", "weapon", "hand", "head", "headgear", "headgear_back"),
}
POSE_NAMES = ("idle", "walk1", "walk2", "walk3", "walk4", "windup", "attack", "cast", "hit")

# Per leg (-x, +x): hip x, knee x, knee dy, ankle x, lift, foot scale. A foot coming toward the
# viewer is drawn lower and a touch bigger; the trailing one lifts its heel.
LEGS_FB = {
    "stand": ((-5, -5.2, 0, -5.5, 0, 1.0), (5, 5.2, 0, 5.5, 0, 1.0)),
    "c1": ((-5, -5.0, 0.5, -4.8, 1.8, 0.92), (5, 5.6, -0.8, 6.0, -1.4, 1.08)),
    "p1": ((-5, -4.8, 0, -4.6, 0, 1.0), (5, 6.2, 6, 4.6, 7, 1.05)),
    "c2": ((-5, -5.6, -0.8, -6.0, -1.4, 1.08), (5, 5.0, 0.5, 4.8, 1.8, 0.92)),
    "p2": ((-5, -6.2, 6, -4.6, 7, 1.05), (5, 4.8, 0, 4.6, 0, 1.0)),
    "brace": ((-6, -8.5, 0, -9.5, 0, 1.0), (6, 8.5, 0, 9.5, 0, 1.0)),
    "lunge": ((-6, -10, -2, -10.5, 0, 1.0), (6, 10, -2, 10.5, 0, 1.0)),
    "recoil": ((-5, -7, 1, -8, 2.5, 0.95), (6, 8.5, 0, 9.5, 0, 1.0)),
}


class Spec:
    """poses: {pose: (legs phase, near arm, far arm, weapon (hand, angle, L, back) or None, open hand, mood)};
    back_poses overrides some of them for the back view. Hooks get (k, ...); back=True for the back view."""
    def __init__(self, poses, legs, head, back_item, torso_back, cap, back_poses=None, hand_r=2.5, lamp_x=10, cap_back=None):
        self.poses = {"front": poses, "back": dict(poses, **(back_poses or {}))}
        self.legs, self.head, self.back_item, self.torso_back, self.cap = legs, head, back_item, torso_back, cap
        self.hand_r, self.lamp_x, self.cap_back = hand_r, lamp_x, cap_back


SPECS = {}


def boot_fb(ax, lift, top, col, sc, back):
    with T(ax, lift, sc):
        sh = [(-3.2, top), (3.2, top)] + bez((3.2, top), (3.4, 4), (3.9, 2.6), (3.9, 1.6)) + \
            bez((3.9, 1.6), (3.9, -0.2), (-3.9, -0.2), (-3.9, 1.6)) + bez((-3.9, 1.6), (-3.9, 2.6), (-3.4, 4), (-3.2, top))
        form(sh, col, sh=0.14)
        if back:
            stroke(bez((-2.6, 3.2), (-1, 2.2), (1, 2.2), (2.6, 3.2)), LINE*0.6)
        else:
            shape(ell(0, 1.4, 4.4, 2.2, 20), col, LINE*0.9)
            stroke(bez((-3, 2.4), (-1, 3.2), (1, 3.2), (3, 2.4)), LINE*0.5)


def legs_fb(k, phase, trousers, boots, boot_h, back, kx=1.0):
    """returns the ankle points (-x leg, +x leg) so skirts can follow the feet"""
    out = {}
    for hx, kxx, kdy, ax, lift, sc in sorted(LEGS_FB[phase], key=lambda l: l[5]):
        tube([(hx*kx, k.hip), (kxx*kx, k.knee+kdy), (ax*kx, k.ankle+lift)], k.leg_w[0], k.leg_w[1]*sc, trousers)
        boot_fb(ax*kx, lift, k.ankle+boot_h, boots, sc, back)
        out[hx < 0] = (ax*kx, k.ankle+lift)
    return out[True], out[False]


def ears(k, skin=SKIN):
    r = k.hr; cy = k.hy
    for sx in (-1, 1): shape(ell(sx*r*0.97, cy-r*0.05, r*0.2, r*0.3, 14), skin, LINE*0.8)


def torso_back_plain(k, hem, hem_w, col, dk, waist_w=None):
    tors = torso_pts(k, hem, hem_w, waist_w=waist_w or hem_w-1, collar=3.5)
    form(tors, col, sdx=0, sdy=1.2, sh=0.14)
    stroke(bez((0, k.sh_y+1.5), (0.4, 84), (-0.4, 66), (0, hem+1)), LINE*0.6, g=dk)
    for sx in (-1, 1):
        stroke(bez((sx*k.sh_w*0.66, k.sh_y-2), (sx*k.sh_w*0.78, 84), (sx*k.sh_w*0.8, 70), (sx*k.sh_w*0.85, hem+3)), LINE*0.45, g=dk)
    shape(bez((-6, k.sh_y+2.6), (-3, k.sh_y-0.5), (3, k.sh_y-0.5), (6, k.sh_y+2.6)) + [(0, k.sh_y+3.2)], dk, LINE*0.7)
    return tors


def torso_back_armour(cls, k, look):
    """the armour looks seen from behind; False for the class's own clothes (the Spec draws those)"""
    hem = G.CLS[cls].hem
    if look in ("krouzkova_kosile", "kozich", "krunyr", "platova_zbroj"):
        G.torso_armour(cls, k, look)
        return True
    if look == "kytel":
        torso_back_plain(k, hem, 16.0, G.CLOTH, G.CLOTH_D, 14.5)
        return True
    if look == "kozeny_kabatec":
        torso_back_plain(k, hem-2, 15.0, G.HIDE, G.HIDE_D, 13.5)
        return True
    return False


# ------------------------------------------------------------------ helmets and hoods, centred
def headgear_fb(cls, k, look, back):
    r = k.hr; cy = k.hy
    if look == "beranice":
        cp = bez((-r*1.12, cy+r*0.5), (-r*1.3, cy+r*2.0), (r*1.3, cy+r*2.0), (r*1.12, cy+r*0.5)) + \
            bez((r*1.12, cy+r*0.5), (r*0.4, cy+r*0.7), (-r*0.4, cy+r*0.7), (-r*1.12, cy+r*0.5))
        form(cp, G.FLEECE, sdx=0, sdy=1, sh=0.16)
        for i in range(14):
            a = math.radians(15+i*11)
            x, y = math.cos(a)*r*0.95, cy+r*0.7+math.sin(a)*r*1.05
            stroke(bez((x-1, y), (x-0.6, y+1.2), (x+0.6, y+1.2), (x+1, y)), LINE*0.45, g=G.FLEECE_D)
        shape(rrect(-r*1.18, cy+r*0.38, r*2.36, r*0.42, 1.0), G.FLEECE_D, LINE*0.7)
    elif look == "kapuce":
        if back:
            hd = bez((-r*1.3, cy-r*1.5), (-r*1.55, cy+r*0.8), (-r*1.0, cy+r*1.75), (0, cy+r*1.8)) + \
                bez((0, cy+r*1.8), (r*1.0, cy+r*1.75), (r*1.55, cy+r*0.8), (r*1.3, cy-r*1.5))
            form(hd, G.HOOD, sdx=0, sdy=1, sh=0.15)
            stroke(bez((0, cy+r*1.75), (r*0.1, cy+r*0.6), (-r*0.1, cy-r*0.4), (0, cy-r*1.4)), LINE*0.5, g=G.HOOD_D)
        else:
            hf = bez((-r*1.3, cy-r*1.0), (-r*1.45, cy+r*0.9), (-r*0.8, cy+r*1.6), (0, cy+r*1.6)) + \
                bez((0, cy+r*1.6), (r*0.8, cy+r*1.6), (r*1.45, cy+r*0.9), (r*1.3, cy-r*1.0)) + \
                bez((r*1.3, cy-r*1.0), (r*1.2, cy+r*0.5), (r*0.8, cy+r*1.15), (0, cy+r*1.15)) + \
                bez((0, cy+r*1.15), (-r*0.8, cy+r*1.15), (-r*1.2, cy+r*0.5), (-r*1.3, cy-r*1.0))
            form(hf, G.HOOD, sdx=0, sdy=0.8, sh=0.12)
            stroke(bez((-r*1.2, cy+r*0.5), (-r*0.6, cy+r*1.3), (r*0.6, cy+r*1.3), (r*1.2, cy+r*0.5)), LINE*0.6, g=G.HOOD_D)
    elif look == "havirska_prilba":
        dome = bez((-r*1.08, cy+r*0.5), (-r*1.15, cy+r*1.85), (r*1.15, cy+r*1.85), (r*1.08, cy+r*0.5)) + \
            bez((r*1.08, cy+r*0.5), (r*0.4, cy+r*0.62), (-r*0.4, cy+r*0.62), (-r*1.08, cy+r*0.5))
        form(dome, Col(0.35, "#4a3a2c"), sdx=0, sdy=1, sh=0.18)
        shape(ell(0, cy+r*0.5, r*1.4, r*0.2, 24), Col(0.3, "#3e3026"), LINE*0.7)
        if not back:
            shape(rrect(-r*0.23, cy+r*0.9, r*0.46, r*0.45, 0.4), BRASS, LINE*0.6)
        else:
            stroke(bez((0, cy+r*1.8), (r*0.05, cy+r*1.3), (-r*0.05, cy+r*0.9), (0, cy+r*0.6)), LINE*0.6)
    elif look == "prilba":
        dome = bez((-r*1.0, cy+r*0.55), (-r*1.05, cy+r*1.9), (r*1.05, cy+r*1.9), (r*1.0, cy+r*0.55))
        form(dome + [(-r*1.0, cy+r*0.55)], G.STEEL, sdx=0, sdy=1, sh=0.2)
        form(ell(0, cy+r*0.55, r*1.75, r*0.3, 28), G.STEEL_D, sh=0.15)
        stroke(bez((-r*0.35, cy+r*1.75), (-r*0.55, cy+r*1.4), (-r*0.6, cy+r*1.0), (-r*0.55, cy+r*0.7)), LINE*1.2, g=G.STEEL_L, alpha=0.7)
    elif look == "velka_prilba":
        hm = [(-r*1.15, cy-r*1.1), (r*1.15, cy-r*1.1)] + bez((r*1.15, cy-r*1.1), (r*1.25, cy+r*0.4), (r*1.2, cy+r*1.3), (r*0.7, cy+r*1.7)) + \
            bez((r*0.7, cy+r*1.7), (r*0.3, cy+r*1.85), (-r*0.3, cy+r*1.85), (-r*0.7, cy+r*1.7)) + \
            bez((-r*0.7, cy+r*1.7), (-r*1.2, cy+r*1.3), (-r*1.25, cy+r*0.4), (-r*1.15, cy-r*1.1))
        form(hm, G.STEEL, sdx=0, sdy=1, sh=0.22)
        stroke([(0, cy+r*1.82), (0, cy-r*1.05)], LINE*0.7, g=G.STEEL_D)
        if not back:
            for sx in (-1, 1):
                shape([(sx*r*0.12, cy+r*0.12), (sx*r*0.95, cy+r*0.12), (sx*r*0.95, cy+r*0.34), (sx*r*0.12, cy+r*0.34)], Col(0.08, "#151416"), LINE*0.5)
            for yy in (-0.35, -0.6):
                for xx in (-0.5, -0.25, 0.25, 0.5): dot(r*xx, cy+r*yy, 0.55, 0.1)


def headgear_back_fb(cls, k, look, back):
    """what goes behind the head: hoods from the front; from the back the hood is drawn whole on top"""
    if look == "kapuce":
        if back:
            headgear_fb(cls, k, look, True)
        else:
            r = k.hr; cy = k.hy
            form(bez((-r*1.4, cy-r*1.6), (-r*1.75, cy+r*0.6), (-r*1.1, cy+r*1.8), (0, cy+r*1.8)) +
                 bez((0, cy+r*1.8), (r*1.1, cy+r*1.8), (r*1.75, cy+r*0.6), (r*1.4, cy-r*1.6)), G.HOOD, sdx=0, sdy=1, sh=0.15)


# ------------------------------------------------------------------ havíř
HAV_FB = {
    "idle": ("stand", ("k", 23.5, 63, -1), ("k", -23.5, 63, 1), ("near", 84, 34, 14), False, "think"),
    "walk1": ("c1", ("k", 24.5, 64, -1), ("k", -21, 68.5, 1), ("near", 80, 34, 14), False, "think"),
    "walk2": ("p1", ("k", 24, 63.5, -1), ("k", -22.5, 65, 1), ("near", 83, 34, 14), False, "think"),
    "walk3": ("c2", ("k", 21, 68.5, -1), ("k", -24.5, 64, 1), ("near", 88, 34, 14), False, "think"),
    "walk4": ("p2", ("k", 22.5, 65, -1), ("k", -24, 63.5, 1), ("near", 85, 34, 14), False, "think"),
    "windup": ("brace", ("a", 95, 105), ("a", 85, 75), ("near", 96, 26, 12), False, "determined"),
    "attack": ("lunge", ("k", 5, 72, -1), ("k", -2, 74, 1), ("near", -58, 30, 12), False, "wow"),
    "cast": ("brace", ("a", 72, 96), ("k", -23.5, 63, 1), ("far", -92, 26, 10), True, "think"),
    "hit": ("recoil", ("a", -22, -2), ("a", -158, -178), ("near", 118, 30, 10), False, "worried"),
}


def hav_legs(k, phase, back):
    legs_fb(k, phase, H.H_TROUS, BOOT, 9, back)


def hav_head(k, md, look, back):
    r = k.hr; cy = k.hy
    H.neck(k, SKIN, 3.2)
    ears(k)
    if back:
        for sx in (-1, 1):
            shape(bez((sx*r*0.7, cy-r*0.5), (sx*r*1.05, cy-r*0.7), (sx*r*0.9, cy-r*1.2), (sx*r*0.4, cy-r*1.3)) +
                  [(sx*r*0.3, cy-r*0.8)], H.H_BEARD, LINE*0.7)
        form(head_outline(k), H.H_BEARD, sdx=0, sdy=1, sh=0.12)
        for xx in (-0.45, -0.15, 0.15, 0.45):
            stroke(bez((r*xx, cy+r*0.6), (r*xx*1.1, cy+r*0.1), (r*xx, cy-r*0.4), (r*xx*0.9, cy-r*0.8)), LINE*0.4, g=Col(0.2, "#3a2d24"))
        return
    shape(head_outline(k), SKIN)
    for sx in (-1, 1):
        shape(bez((sx*r*0.98, cy+r*0.45), (sx*r*1.08, cy+r*0.1), (sx*r*1.02, cy-r*0.2), (sx*r*0.9, cy-r*0.3)) +
              [(sx*r*0.8, cy+r*0.4)], H.H_BEARD, LINE*0.7)
    H.beard(k, H.H_BEARD, 1.25, dx=0)
    if look != "velka_prilba":
        face(0, cy, r*0.95, md)
    H.moustache(k, H.H_BEARD, dx=0)


def hav_cap(k, back):
    r = k.hr; cy = k.hy
    c = bez((-r*1.06, cy+r*0.55), (-r*1.12, cy+r*1.7), (r*1.12, cy+r*1.7), (r*1.06, cy+r*0.55)) + \
        bez((r*1.06, cy+r*0.55), (r*0.4, cy+r*0.68), (-r*0.4, cy+r*0.68), (-r*1.06, cy+r*0.55))
    form(c, H.H_CAP, sdx=0, sdy=1)
    shape(rrect(-r*1.1, cy+r*0.45, r*2.2, r*0.3, 0.8), LEATHER, LINE*0.8)
    if not back:
        shape([(-r*0.19, cy+r*0.8), (r*0.19, cy+r*0.8), (r*0.19, cy+r*1.18), (-r*0.19, cy+r*1.18)], BRASS, LINE*0.6)


def hav_torso_back(k):
    torso_back_plain(k, 52, 16.5, H.H_SMOCK, H.H_SMOCK_DK, 15.5)


def hav_flek(k, back):
    if not back: return
    f = [(-12, 61)] + bez((-12, 61), (-14, 52), (-14.5, 44), (-13, 37)) + bez((-13, 37), (-5, 35.5), (5, 35.5), (13, 37)) + \
        bez((13, 37), (14.5, 44), (14, 52), (12, 61))
    form(f, H.H_FLEK, sdx=0, sdy=1, sh=0.16)
    stroke(bez((-11, 38.5), (-4, 37.4), (4, 37.4), (11, 38.5)), LINE*0.5, g=Col(0.2, "#3d2b20"))


SPECS["havir"] = Spec(HAV_FB, hav_legs, hav_head, hav_flek, hav_torso_back, hav_cap)


# ------------------------------------------------------------------ shared layer drawing
def hold(spec_hand, wpn, layer):
    return wpn is not None and wpn[0] == spec_hand and \
        (layer == "weapon" if spec_hand == "near" else layer == "weapon_far")


def body(cls, k, pose, layer, look, view):
    sp = SPECS[cls]
    lg, near, far, wpn, op, md = sp.poses[view][pose]
    back = view == "back"
    if layer == "legs":
        if back: cast_shadow(0, 0, G.CLS[cls].shadow_rx, 3)
        sp.legs(k, lg, back)
    elif layer == "back":
        if not back: cast_shadow(0, 0, G.CLS[cls].shadow_rx, 3)
        sp.back_item(k, back)
    elif layer == "body_far" or layer == "body_near":
        side, spec = (-1, far) if layer == "body_far" else (1, near)
        bp = G.body_parts(cls, look)
        G.sleeve(k, side, spec, bp["col"], bp.get("cuff"), plate=bp.get("plate", False), fur=bp.get("fur", False),
                 rings=bp.get("rings", False), rolled=bp.get("rolled", False))
        if look == "platova_zbroj": G.pauldron(k, side)
    elif layer in ("weapon_far", "hand_far", "offhand", "weapon", "hand"):
        side, spec = (-1, far) if layer in ("weapon_far", "hand_far", "offhand") else (1, near)
        _, _, Hd, fa = G.arm_geom(k, side, spec)
        if layer in ("weapon_far", "weapon"):
            if hold("near" if side > 0 else "far", wpn, layer):
                G.weapon(look, Hd[0], Hd[1], wpn[1], plant=wpn[2] >= 55)
        elif layer == "offhand":
            G.offhand(look, Hd[0]-1, Hd[1]+2)
        else:
            hnd(Hd[0], Hd[1], fa, sp.hand_r, open_=op and side > 0)
    elif layer == "body":
        if back:
            if not torso_back_armour(cls, k, look): sp.torso_back(k)
        else: G.torso_armour(cls, k, look)
    elif layer == "belt": G.belt(cls, k, look)
    elif layer == "lamp": G.lamp(look, sp.lamp_x, G.CLS[cls].belt[0], 0.95)
    elif layer == "head": sp.head(k, md, look, back)
    elif layer == "headgear":
        if look == "default": sp.cap(k, back)
        else: headgear_fb(cls, k, look, back)
    elif layer == "headgear_back":
        if look == "default": sp.cap_back(k, back)
        else: headgear_back_fb(cls, k, look, back)


def draw(cls, layer, look, pose, view, x, y, s):
    from chars3 import Person
    k = Person(**G.CLS[cls].k)
    with T(x, y + (1.2 if pose in ("hit", "attack") else 0), s):
        if view == "back": C.scale(-1, 1)
        body(cls, k, pose, layer, look, view)


def skip(cls, layer, pose, view):
    wpn = SPECS[cls].poses[view][pose][3]
    if layer == "weapon": return not (wpn and wpn[0] == "near")
    if layer == "weapon_far": return not (wpn and wpn[0] == "far")
    if layer in ("weapon_belt", "lamp_far"): return True
    return False


def load():
    """import the modules that register the other classes"""
    import importlib
    for m in ("hero_views_a", "hero_views_b", "hero_views_c"):
        try: importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name != m: raise
    return SPECS
