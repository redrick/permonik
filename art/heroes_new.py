"""The five later heroes, in the same layers as heroes_gear.py: Kovář, Žrec, Vlkodlak, Alchymistka, Loutkářka.

Importing this module registers them in heroes_gear.CLS / EXTRA, so heroes_gear renders them with the rest.
"""
import math
from lib import Col, ell, bez, rrect
from style3 import T, stroke, shape, form, fill, hatch, tube, dot, face, head_outline, clip_fill, LINE
import heroes as H
from heroes import SKIN, IRON, IRON_LT, WOOD, BRASS, BONE, RED, LEATHER, BOOT, legs, torso_pts, skirt_pts, neck, beard, moustache, braid
import heroes_gear as G


def C_(h, g):
    return Col(g, h)


def head_base(k, md, ear=True, neck_w=2.8, do_face=True):
    neck(k, SKIN, neck_w)
    r = k.hr; cy = k.hy
    if ear:
        shape(ell(-r * 0.95, cy - r * 0.05, r * 0.2, r * 0.3, 14), SKIN, LINE * 0.8)
    shape(head_outline(k), SKIN)
    if do_face:
        face(r * 0.2, cy, r * 0.95, md)


def nothing(*a):
    pass


class Hooks:
    def __init__(self, **fns):
        self.back = fns.get("back", nothing)
        self.legs = fns.get("legs", nothing)
        self.head = fns.get("head", nothing)
        self.torso = fns.get("torso", nothing)
        self.belt = fns.get("belt", nothing)
        self.headgear = fns.get("headgear", nothing)
        self.headgear_back = fns.get("headgear_back", nothing)


def register(cid, k, poses, sleeve, cuff, hem, belt_y, weapon_at, lie_w, shadow_rx, drop, hooks, rolled=False):
    c = G.Cls(k, poses, sleeve, cuff, hem, belt_y, weapon_at, lie_w, shadow_rx, drop)
    c.rolled = rolled
    G.CLS[cid] = c
    G.EXTRA[cid] = hooks


HEAVY_AT = {"upright": ("near", 72), "swing": ("near", -16), "wind": ("near", 128), "flung": ("near", 115), "hang": ("far", -96)}
AGILE_AT = {"rest": ("near", 78), "strike": ("near", 35), "flung": ("near", 120), "raised": ("near", 100), "belt": ("belt", -100)}
CASTER_AT = {"stand": ("near", 92), "thrust": ("near", -4), "raise": ("near", 96), "flung": ("near", 112)}


# ------------------------------------------------------------------ KOVÁŘ (the smith)
KO = dict(H=128, hr=11.4, hy=115.5, sh_y=100, sh_w=14.5, hip=58, knee=31, ankle=5, leg_w=(8.8, 7.0), arm_w=(8.2, 7.0), up=20, fo=18)
KO_SHIRT = C_("#d8cdb4", 0.85); KO_APRON = C_("#6a4a30", 0.32); KO_TROUS = C_("#4a4440", 0.3); KO_BEARD = C_("#5a3a24", 0.28)


def ko_torso(k):
    tors = torso_pts(k, 52, 16.5, waist_w=15.5)
    form(tors, KO_SHIRT, sdx=-2.4, sdy=1.2, sh=0.12)
    stroke([(1.0, k.sh_y + 1), (1.2, 86)], LINE * 0.7)
    apron = [(-10.5, 90), (10.5, 90), (13.5, 58), (15, 30), (-15, 30), (-13.5, 58)]
    form(apron, KO_APRON, sdx=-2, sdy=1, sh=0.16)
    for (x, y) in ((-6, 44), (4, 52), (8, 38), (-3, 70)):
        dot(x, y, 1.1, C_("#2a1a10", 0.1))
    for sx in (-1, 1):
        stroke([(sx * 10, 90), (sx * 6.5, k.sh_y + 1)], LINE * 1.2, g=KO_APRON)
    stroke(bez((-12, 40), (-4, 41), (4, 41), (12, 40)), LINE * 0.5, g=C_("#3e2a1a", 0.2))


def ko_legs(k, lg):
    legs(k, lg, KO_TROUS, BOOT, boot_h=10, wk=1.2)


def ko_belt(k):
    shape([(-16, 58), (16, 58), (16.2, 62.5), (-16.2, 62.5)], LEATHER, LINE * 0.8)
    shape(rrect(-2, 57.2, 5, 6, 0.6), IRON_LT, LINE * 0.6)
    with T(-11, 58, 1, rot=-80):
        tube([(0, 0), (16, 0)], 1.4, 1.2, IRON, LINE * 0.6, sh=0)
        tube([(0, 2), (16, 1)], 1.4, 1.2, IRON, LINE * 0.6, sh=0)


def ko_head(k, md, look):
    r = k.hr; cy = k.hy
    head_base(k, md, neck_w=3.4, do_face=False)
    if look != "velka_prilba":
        face(r * 0.2, cy, r * 0.95, md)
    for x in (-0.2, 0.3):
        stroke(bez((r * (x - 0.25), cy + r * 0.55), (r * x, cy + r * 0.62), (r * (x + 0.2), cy + r * 0.6), (r * (x + 0.35), cy + r * 0.5)), LINE * 0.9, g=KO_BEARD)
    beard(k, KO_BEARD, 1.75, line=C_("#3a2414", 0.15))
    moustache(k, KO_BEARD, w=0.65)


KO_POSE = dict(H.HAV_POSE,
               walk1=("c1", ("a", -100, -54), ("a", -64, -34), "upright", False, "think"),
               walk3=("c2", ("a", -62, -12), ("a", -114, -98), "upright", False, "think"))

register("kovar", KO, KO_POSE, KO_SHIRT, None, 52, (58, 62), HEAVY_AT, 23, 19, (40, 15),
         Hooks(torso=ko_torso, legs=ko_legs, belt=ko_belt, head=ko_head), rolled=True)


# ------------------------------------------------------------------ ŽREC (the priest)
ZR = dict(H=130, hr=10.8, hy=119, sh_y=104, sh_w=13, hip=61, knee=32, ankle=5, leg_w=(7.6, 6.0), arm_w=(6.8, 5.8), up=21, fo=19)
ZR_LINEN = C_("#e6dfcc", 0.9); ZR_RED = C_("#a8282e", 0.35); ZR_FUR = C_("#6a5038", 0.35); ZR_HAIR = C_("#e8e4dc", 0.92); ZR_LEAF = C_("#4f6a2a", 0.4)


ZR_SWAY = {"walk1": -2.5, "walk2": -0.5, "walk3": 2.5, "walk4": 0.5, "windup": 2, "attack": -4, "hit": 4}


def zr_back(k, pose):
    w = ZR_SWAY.get(pose, 0)
    cloak = [(-k.sh_w - 2, k.sh_y + 1), (k.sh_w + 2, k.sh_y + 1)] + bez((k.sh_w + 2, k.sh_y + 1), (k.sh_w + 6, 70), (k.sh_w + 8 + w * 0.5, 40), (k.sh_w + 7 + w, 18)) + \
        bez((k.sh_w + 7 + w, 18), (4 + w, 15), (-4 + w, 15), (-k.sh_w - 7 + w, 18)) + bez((-k.sh_w - 7 + w, 18), (-k.sh_w - 8 + w * 0.5, 40), (-k.sh_w - 6, 70), (-k.sh_w - 2, k.sh_y + 1))
    form(cloak, ZR_FUR, sdx=-2, sdy=1, sh=0.18)
    hatch(cloak, 1.5, 80, 0.35, alpha=0.3)
    r = k.hr; cy = k.hy; hw = w * 0.4
    hair = bez((-r * 0.9, cy + r * 0.4), (-r * 1.4, cy - r * 0.8), (-r * 1.3 + hw, cy - r * 2.6), (-r * 0.6 + hw, cy - r * 3.2)) + \
        bez((-r * 0.6 + hw, cy - r * 3.2), (0 + hw, cy - r * 3.0), (r * 0.4, cy - r * 2.0), (r * 0.6, cy - r * 0.6))
    form(hair, ZR_HAIR, sdx=-1, sdy=0.6, sh=0.12)


def zr_legs(k, lg):
    ph = legs(k, lg, ZR_LINEN, C_("#4e3a2a", 0.3), boot_h=5)
    xs = [p[0][-1][0] for p in ph]
    sk = skirt_pts(62, 13, 7, min(-16, min(xs) - 6), max(16, max(xs) + 6))
    form(sk, ZR_LINEN, sdx=-2.4, sdy=1, sh=0.12)
    clip_fill(sk, [(-30, 7), (30, 7), (30, 12), (-30, 12)], ZR_RED)
    for xx in (-9, -3, 3, 9):
        stroke(bez((xx * 0.6, 58), (xx * 0.8, 40), (xx, 25), (xx * 1.1, 12)), LINE * 0.4, g=C_("#b8b09a", 0.7))


def zr_torso(k):
    tors = torso_pts(k, 62, 13.5, waist_w=12.5, collar=4)
    form(tors, ZR_LINEN, sdx=-2, sdy=1, sh=0.1)
    shape([(-1.6, k.sh_y + 1), (1.6, k.sh_y + 1), (1.8, 62), (-1.8, 62)], ZR_RED, LINE * 0.5)
    for y in range(66, int(k.sh_y), 5):
        dot(0, y, 0.7, C_("#f2d060", 0.8))
    for sx in (-1, 1):
        shape([(sx * 1.6, k.sh_y + 1), (sx * 7, k.sh_y + 2.5), (sx * 9.5, k.sh_y - 2), (sx * 2.5, k.sh_y - 3.5)], ZR_RED, LINE * 0.5)


def zr_belt(k):
    shape([(-13.8, 60), (13.8, 60), (14, 64.5), (-14, 64.5)], ZR_RED, LINE * 0.6)
    for x in (4, 6):
        tube([(x, 60), (x + 1, 50)], 1.2, 1.0, ZR_RED, LINE * 0.5, sh=0)


def zr_head(k, md, look):
    r = k.hr; cy = k.hy
    head_base(k, md, neck_w=2.6, do_face=look != "velka_prilba")
    beard(k, ZR_HAIR, 2.4, line=C_("#b8b2a8", 0.7))
    moustache(k, ZR_HAIR, w=0.6)
    hair = bez((-r * 1.04, cy - r * 0.3), (-r * 1.15, cy + r * 1.2), (r * 1.1, cy + r * 1.25), (r * 1.0, cy + r * 0.2)) + \
        bez((r * 1.0, cy + r * 0.2), (r * 0.5, cy + r * 0.55), (-r * 0.3, cy + r * 0.6), (-r * 1.04, cy - r * 0.3))
    form(hair, ZR_HAIR, sdx=-1, sdy=0.6, sh=0.1)


def zr_headgear(k):
    r = k.hr; cy = k.hy
    for i in range(11):
        a = math.radians(-10 + i * 20)
        x, y = math.cos(a) * r * 1.02, cy + r * 0.5 + math.sin(a) * r * 0.35
        shape(ell(x, y, 2.2, 1.2, 10, rot=math.degrees(a) + 40), ZR_LEAF, LINE * 0.4)
    dot(r * 0.95, cy + r * 0.55, 0.9, C_("#a87a3a", 0.5))


ZR_POSE = dict(H.VE_POSE,
               walk1=("c1", ("k", 25, 79, -1), ("a", -66, -40), "stand", False, "think"),
               walk2=("p1", ("k", 27, 80, -1), ("a", -88, -70), "stand", False, "think"),
               walk3=("c2", ("k", 31, 82, -1), ("a", -114, -102), "stand", False, "think"),
               walk4=("p2", ("k", 28, 81, -1), ("a", -94, -80), "stand", False, "think"),
               windup=("brace", ("a", -150, 10), ("a", -40, -15), "wind", True, "determined"))
ZR_AT = dict(CASTER_AT, wind=("near", 8))

register("zrec", ZR, ZR_POSE, ZR_LINEN, ZR_RED, 62, (60, 64), ZR_AT, 27, 17, (-6, 15),
         Hooks(back=zr_back, torso=zr_torso, legs=zr_legs, belt=zr_belt, head=zr_head, headgear=zr_headgear))


# ------------------------------------------------------------------ VLKODLAK (the werewolf huntsman)
VL = dict(H=126, hr=10.8, hy=115, sh_y=100, sh_w=13, hip=59, knee=31, ankle=5, leg_w=(8.0, 6.2), arm_w=(7.0, 6.0), up=20, fo=18)
VL_JERK = C_("#4f5a3a", 0.35); VL_PELT = C_("#7a7670", 0.5); VL_PELT_D = C_("#4e4b47", 0.3); VL_TROUS = C_("#5a4a36", 0.35); VL_HAIR = C_("#2e2620", 0.15)


VL_SWAY = {"walk1": -2, "walk2": -0.5, "walk3": 2, "walk4": 0.5, "windup": 1.5, "attack": -3, "hit": 3}


def vl_back(k, pose):
    w = VL_SWAY.get(pose, 0)
    cape = [(-k.sh_w - 1, k.sh_y + 2), (k.sh_w + 1, k.sh_y + 2)] + bez((k.sh_w + 1, k.sh_y + 2), (k.sh_w + 5, 80), (k.sh_w + 4 + w * 0.5, 62), (k.sh_w + 2 + w, 50)) + \
        [(6 + w, 46), (w, 52), (-6 + w, 46)] + bez((-k.sh_w - 2 + w, 50), (-k.sh_w - 4 + w * 0.5, 62), (-k.sh_w - 5, 80), (-k.sh_w - 1, k.sh_y + 2))
    form(cape, VL_PELT, sdx=-2, sdy=1, sh=0.18)
    hatch(cape, 1.4, 75, 0.35, alpha=0.3)


def vl_legs(k, lg):
    ph = legs(k, lg, VL_TROUS, BOOT, boot_h=9, wk=1.05)
    for pts, lift, frot in ph:
        kx, ky = pts[1]
        ax, ay = pts[2]
        for t in (0.25, 0.5, 0.75):
            x, y = kx + (ax - kx) * t, ky + (ay - ky) * t
            stroke([(x - 3.5, y + 1), (x + 3.5, y - 1)], LINE * 0.8, g=C_("#c8bba0", 0.8))


def vl_torso(k):
    tors = torso_pts(k, 54, 15.5, waist_w=14)
    form(tors, VL_JERK, sdx=-2.2, sdy=1.2, sh=0.15)
    for y in range(60, int(k.sh_y - 4), 6):
        stroke([(-1.8, y), (1.8, y + 2.6)], LINE * 0.5, g=C_("#c8b48a", 0.75))
        stroke([(1.8, y), (-1.8, y + 2.6)], LINE * 0.5, g=C_("#c8b48a", 0.75))
    stroke([(0, k.sh_y), (0, 55)], LINE * 0.7)


def vl_belt(k):
    shape([(-15, 57), (15, 57), (15.2, 61), (-15.2, 61)], LEATHER, LINE * 0.7)
    shape(rrect(1.5, 56.4, 3.6, 5.2, 0.5), BRASS, LINE * 0.5)
    horn = bez((-12, 58), (-16, 50), (-11, 44), (-6, 46)) + bez((-6, 46), (-9, 48), (-12, 52), (-10, 58))
    form(horn, BONE, sh=0.15)
    shape([(9, 58), (12, 58), (11, 46), (10, 46)], LEATHER, LINE * 0.5)


def vl_head(k, md, look):
    r = k.hr; cy = k.hy
    head_base(k, md, neck_w=2.8, do_face=look != "velka_prilba")
    for i in range(16):
        a = math.radians(200 + i * 9)
        dot(r * 0.2 + math.cos(a) * r * 0.85, cy - r * 0.15 + math.sin(a) * r * 0.75, 0.32, VL_HAIR)
    hair = bez((-r * 1.04, cy + r * 0.1), (-r * 1.1, cy + r * 1.15), (r * 1.1, cy + r * 1.15), (r * 1.02, cy + r * 0.2)) + \
        bez((r * 1.02, cy + r * 0.2), (r * 0.6, cy + r * 0.62), (-r * 0.4, cy + r * 0.62), (-r * 1.04, cy + r * 0.1))
    form(hair, VL_HAIR, sdx=-1, sdy=0.6, sh=0.1)


def vl_hood_back(k):
    r = k.hr; cy = k.hy
    hood = bez((-r * 1.3, cy - r * 1.2), (-r * 1.6, cy + r * 0.8), (-r * 0.6, cy + r * 1.7), (r * 0.4, cy + r * 1.6)) + \
        bez((r * 0.4, cy + r * 1.6), (r * 1.3, cy + r * 1.4), (r * 1.5, cy + r * 0.4), (r * 1.3, cy - r * 1.0))
    form(hood, VL_PELT, sdx=-1.5, sdy=1, sh=0.15)


def vl_headgear(k):
    r = k.hr; cy = k.hy
    top = bez((-r * 1.15, cy + r * 0.4), (-r * 1.2, cy + r * 1.6), (r * 1.25, cy + r * 1.6), (r * 1.2, cy + r * 0.4)) + \
        bez((r * 1.2, cy + r * 0.4), (r * 0.5, cy + r * 0.6), (-r * 0.4, cy + r * 0.6), (-r * 1.15, cy + r * 0.4))
    form(top, VL_PELT, sdx=-1.5, sdy=1, sh=0.16)
    for sx in (-0.6, 0.45):
        shape([(r * (sx - 0.25), cy + r * 1.45), (r * (sx + 0.05), cy + r * 2.2), (r * (sx + 0.3), cy + r * 1.45)], VL_PELT_D, LINE * 0.6)
    snout = bez((r * 0.6, cy + r * 0.65), (r * 1.4, cy + r * 0.7), (r * 1.7, cy + r * 0.55), (r * 1.55, cy + r * 0.35)) + [(r * 0.7, cy + r * 0.42)]
    form(snout, VL_PELT, sh=0.15)
    dot(r * 1.6, cy + r * 0.5, 0.9, 0.05)
    dot(r * 0.95, cy + r * 0.9, 0.7, C_("#e8c040", 0.85))


VL_POSE = dict(H.ZB_POSE,
               walk1=("c1", ("a", -100, -40), ("a", -64, -42), "rest", False, "think"),
               walk2=("p1", ("a", -84, -18), ("a", -88, -72), "rest", False, "think"),
               walk3=("c2", ("a", -62, -4), ("a", -114, -104), "rest", False, "think"),
               walk4=("p2", ("a", -80, -16), ("a", -96, -82), "rest", False, "think"),
               windup=("brace", ("a", 170, 100), ("a", -40, -10), "wind", False, "determined"))
VL_AT = dict(AGILE_AT, wind=("near", 140))

register("vlkodlak", VL, VL_POSE, VL_JERK, LEATHER, 54, (57, 61), VL_AT, 27, 17, (44, 3),
         Hooks(back=vl_back, torso=vl_torso, legs=vl_legs, belt=vl_belt, head=vl_head, headgear=vl_headgear, headgear_back=vl_hood_back))


# ------------------------------------------------------------------ ALCHYMISTKA (the alchemist)
AL = dict(H=120, hr=10.6, hy=108.5, sh_y=94, sh_w=11.8, hip=56, knee=30, ankle=5, leg_w=(7, 5.4), arm_w=(6.2, 5.4), up=18.5, fo=16.5)
AL_BODICE = C_("#7a2430", 0.3); AL_BLOUSE = C_("#e2dccb", 0.88); AL_SKIRT = C_("#2f3a5e", 0.28); AL_HAIR = C_("#8a4a2a", 0.32); AL_CAP = C_("#1e1c22", 0.1)


def al_back(k, pose):
    bag = rrect(-k.sh_w - 6, 60, 9, 16, 2)
    form(bag, LEATHER, sh=0.18)
    for i, (x, col) in enumerate(((-k.sh_w - 4.5, "#86e05a"), (-k.sh_w - 1.5, "#a8d8ff"))):
        tube([(x, 74), (x, 82)], 1.6, 1.2, C_("#c8d8d0", 0.85), LINE * 0.5, sh=0)
        dot(x, 76, 0.9, C_(col, 0.7))
    r = k.hr; cy = k.hy
    shape(ell(-r * 0.75, cy + r * 0.1, r * 0.55, r * 0.5, 16), AL_HAIR, LINE * 0.7)


def al_legs(k, lg):
    ph = legs(k, lg, C_("#5a4a40", 0.35), BOOT, boot_h=5)
    xs = [p[0][-1][0] for p in ph]
    sk = skirt_pts(60, 13.5, 8, min(-17, min(xs) - 6), max(17, max(xs) + 6))
    form(sk, AL_SKIRT, sdx=-2.4, sdy=1, sh=0.15)
    ap = [(-8, 58), (8, 58), (10, 20), (-10, 20)]
    form(ap, C_("#cfc6b0", 0.8), sh=0.1)
    for (x, y, c) in ((-3, 40, "#86e05a"), (4, 30, "#7a5aa0"), (1, 48, "#c86a2a")):
        dot(x, y, 1.4, C_(c, 0.5))


def al_torso(k):
    tors = torso_pts(k, 58, 13.5, waist_w=11.5, collar=4)
    form(tors, AL_BLOUSE, sdx=-2, sdy=1, sh=0.1)
    bod = [(-10.5, k.sh_y - 6), (10.5, k.sh_y - 6), (11.5, 60), (-11.5, 60)]
    form(bod, AL_BODICE, sdx=-1.5, sdy=1, sh=0.14)
    for y in range(64, int(k.sh_y - 8), 5):
        stroke([(-2, y), (2, y + 2.4)], LINE * 0.45, g=C_("#e8c070", 0.8))
        stroke([(2, y), (-2, y + 2.4)], LINE * 0.45, g=C_("#e8c070", 0.8))


def al_belt(k):
    shape([(-13, 58), (13, 58), (13.2, 61.5), (-13.2, 61.5)], LEATHER, LINE * 0.6)
    for x, c in ((-8, "#86e05a"), (-4, "#e8b040"), (6, "#a8d8ff")):
        tube([(x, 58), (x, 50)], 2.2, 2.6, C_("#d8e4e0", 0.85), LINE * 0.5, sh=0)
        fill(ell(x, 52, 1.2, 1.6, 10), C_(c, 0.6))
        shape(rrect(x - 1, 57.5, 2, 1.6, 0.3), C_("#7a5a3a", 0.4), LINE * 0.4)


def al_head(k, md, look):
    r = k.hr; cy = k.hy
    head_base(k, md, neck_w=2.4, do_face=look != "velka_prilba")
    hair = bez((-r * 1.04, cy - r * 0.2), (-r * 1.15, cy + r * 1.2), (r * 1.1, cy + r * 1.2), (r * 1.04, cy - r * 0.1)) + \
        bez((r * 1.04, cy - r * 0.1), (r * 0.8, cy + r * 0.5), (r * 0.2, cy + r * 0.66), (-r * 1.04, cy - r * 0.2))
    form(hair, AL_HAIR, sdx=-1, sdy=0.6, sh=0.1)
    if look != "velka_prilba":
        for x in (r * 0.05, r * 0.6):
            stroke(ell(x, cy + r * 0.08, r * 0.22, r * 0.2, 14), LINE * 0.5, closed=True, g=C_("#3a3028", 0.2))
        stroke([(r * 0.27, cy + r * 0.1), (r * 0.38, cy + r * 0.1)], LINE * 0.4)


def al_headgear(k):
    r = k.hr; cy = k.hy
    cap = ell(-r * 0.05, cy + r * 1.0, r * 1.25, r * 0.42, 24)
    form(cap, AL_CAP, sdx=-1, sdy=0.6, sh=0.15)
    tube(bez((-r * 0.4, cy + r * 1.3), (-r * 1.2, cy + r * 1.9), (-r * 2.0, cy + r * 1.8), (-r * 2.3, cy + r * 1.3)), 1.8, 0.6, C_("#e8e2d8", 0.92), LINE * 0.5, sh=0)


AL_POSE = dict(H.ZB_POSE,
               walk1=("c1", ("a", -98, -40), ("a", -68, -44), "rest", False, "think"),
               walk2=("p1", ("a", -86, -22), ("a", -88, -72), "rest", False, "think"),
               walk3=("c2", ("a", -66, -2), ("a", -112, -98), "rest", False, "think"),
               walk4=("p2", ("a", -80, -16), ("a", -96, -84), "rest", False, "think"),
               windup=("brace", ("a", -172, 168), ("a", -30, -8), "wind", False, "determined"))
AL_AT = dict(AGILE_AT, wind=("near", 145))

register("alchymistka", AL, AL_POSE, AL_BLOUSE, C_("#f2ece0", 0.95), 58, (58, 61), AL_AT, 29, 16, (44, 3),
         Hooks(back=al_back, torso=al_torso, legs=al_legs, belt=al_belt, head=al_head, headgear=al_headgear))


# ------------------------------------------------------------------ LOUTKÁŘKA (the puppeteer)
LO = dict(H=120, hr=10.6, hy=108.5, sh_y=94, sh_w=11.8, hip=56, knee=30, ankle=5, leg_w=(7, 5.4), arm_w=(6.6, 5.4), up=18.5, fo=16.5)
LO_BLOUSE = C_("#f2eee2", 0.95); LO_VEST = C_("#b8282e", 0.35); LO_SKIRT = C_("#3a5a9a", 0.35); LO_HAIR = C_("#d8b060", 0.72); LO_SCARF = C_("#c8322e", 0.38)


LO_SWAY = {"walk1": 1.5, "walk2": -1, "walk3": -1.5, "walk4": 1}


def lo_back(k, pose):
    bag = ell(-k.sh_w - 3, 72, 7, 9, 20)
    form(bag, C_("#6a4a30", 0.32), sh=0.18)
    sw = LO_SWAY.get(pose, 0)
    for i, (dx, L) in enumerate(((-2, 24), (1, 30), (4, 20))):
        tube([(-k.sh_w - 3 + dx, 76), (-k.sh_w - 9 + dx * 2 + sw, 76 + L)], 1.6, 1.3, WOOD, LINE * 0.5, sh=0)
        shape(ell(-k.sh_w - 9 + dx * 2 + sw, 76 + L, 1.6, 1.0, 10), BRASS, LINE * 0.4)
    with T(-k.sh_w - 3, 62, 1, rot=-20 + sw * 4):
        head = bez((-3, 0), (-4, -6), (3, -8), (5, -3)) + bez((5, -3), (4, 0), (1, 1), (-3, 0))
        form(head, C_("#e8dcc0", 0.88), sh=0.12)
        for sx in (-1, 1):
            tube(bez((sx * 1.5, -6), (sx * 3, -10), (sx * 5, -11), (sx * 6, -9)), 1.2, 0.6, C_("#a8987a", 0.6), LINE * 0.4, sh=0)
        dot(2.5, -4, 0.6, 0.05)


def lo_legs(k, lg):
    ph = legs(k, lg, C_("#c8322e", 0.38), BOOT, boot_h=6)
    xs = [p[0][-1][0] for p in ph]
    sk = skirt_pts(60, 13.5, 30, min(-16, min(xs) - 6), max(16, max(xs) + 6))
    form(sk, LO_SKIRT, sdx=-2.2, sdy=1, sh=0.14)
    clip_fill(sk, [(-30, 30), (30, 30), (30, 34), (-30, 34)], C_("#f2d060", 0.8))
    ap = [(-9, 58), (9, 58), (10, 34), (-10, 34)]
    form(ap, C_("#f2eee2", 0.95), sh=0.08)
    for (x, y, c) in ((-5, 44, "#c8322e"), (0, 40, "#3a8a4a"), (5, 46, "#c8322e"), (-2, 50, "#f2b030"), (3, 52, "#3a8a4a")):
        dot(x, y, 1.1, C_(c, 0.45))


def lo_torso(k):
    tors = torso_pts(k, 58, 13.5, waist_w=11.5, collar=4)
    form(tors, LO_BLOUSE, sdx=-2, sdy=1, sh=0.08)
    for sx in (-1, 1):
        v = [(sx * 3.5, k.sh_y - 1), (sx * (k.sh_w - 0.5), k.sh_y - 4), (sx * 12.5, 60), (sx * 3, 60)]
        form(v, LO_VEST, sdx=-1.5, sdy=1, sh=0.12)
        for yy in (84, 76, 68):
            dot(sx * 6.5, yy, 0.9, C_("#f2d060", 0.85))
    for y in range(64, 88, 6):
        stroke([(-2.6, y), (2.6, y + 2.6)], LINE * 0.45)
        stroke([(2.6, y), (-2.6, y + 2.6)], LINE * 0.45)


def lo_belt(k):
    for i, c in enumerate(("#f2b030", "#3a8a4a", "#c8322e")):
        shape([(-13.2, 58 + i * 1.6), (13.2, 58 + i * 1.6), (13.3, 59.6 + i * 1.6), (-13.3, 59.6 + i * 1.6)], C_(c, 0.5), LINE * 0.35)
    tube(bez((10, 59), (12, 52), (13, 46), (12, 40)), 1.4, 1.0, C_("#c8322e", 0.38), LINE * 0.4, sh=0)


def lo_head(k, md, look):
    r = k.hr; cy = k.hy
    braid(-r * 0.7, cy - r * 0.3, -r * 0.9, cy - r * 3.3, col=LO_HAIR)
    head_base(k, md, neck_w=2.4, do_face=look != "velka_prilba")
    hair = bez((-r * 1.04, cy - r * 0.1), (-r * 1.18, cy + r * 1.25), (r * 1.15, cy + r * 1.25), (r * 1.04, cy - r * 0.1)) + \
        bez((r * 1.04, cy - r * 0.1), (r * 0.9, cy + r * 0.45), (r * 0.6, cy + r * 0.62), (r * 0.1, cy + r * 0.7)) + \
        bez((r * 0.1, cy + r * 0.7), (-r * 0.4, cy + r * 0.62), (-r * 0.9, cy + r * 0.4), (-r * 1.04, cy - r * 0.1))
    form(hair, LO_HAIR, sdx=-1, sdy=0.6, sh=0.1)
    braid(r * 0.85, cy - r * 0.5, r * 0.7, cy - r * 3.2, col=LO_HAIR)


def lo_scarf_back(k):
    r = k.hr; cy = k.hy
    for dx in (-1.5, 1.5):
        shape([(-r * 0.9, cy - r * 0.3), (-r * 1.1 + dx, cy - r * 1.6), (-r * 0.6 + dx, cy - r * 1.5)], LO_SCARF, LINE * 0.5)


def lo_headgear(k):
    r = k.hr; cy = k.hy
    sc = bez((-r * 1.15, cy + r * 0.0), (-r * 1.3, cy + r * 1.6), (r * 1.3, cy + r * 1.6), (r * 1.15, cy + r * 0.1)) + \
        bez((r * 1.15, cy + r * 0.1), (r * 0.9, cy + r * 0.62), (-r * 0.6, cy + r * 0.65), (-r * 1.15, cy + r * 0.0))
    form(sc, LO_SCARF, sdx=-1.5, sdy=1, sh=0.15)
    for (x, y) in ((-0.5, 1.2), (0.1, 1.35), (0.65, 1.15), (-0.2, 0.95), (0.4, 0.85)):
        shape(ell(r * x, cy + r * y, 1.1, 1.1, 10), C_("#f2d060", 0.8), LINE * 0.3)


LO_POSE = dict(H.VE_POSE,
               walk1=("c1", ("k", 24, 80, -1), ("a", -66, -46), "stand", False, "think"),
               walk2=("p1", ("k", 27, 82, -1), ("a", -88, -74), "stand", False, "think"),
               walk3=("c2", ("k", 31, 81, -1), ("a", -112, -100), "stand", False, "think"),
               walk4=("p2", ("k", 28, 83, -1), ("a", -96, -84), "stand", False, "think"),
               windup=("brace", ("k", -2, 86, -1), ("a", -30, -6), "wind", False, "determined"))
LO_AT = dict(CASTER_AT, wind=("near", 12))

register("loutkarka", LO, LO_POSE, LO_BLOUSE, LO_VEST, 58, (58, 63), LO_AT, 26, 16, (-6, 15),
         Hooks(back=lo_back, torso=lo_torso, legs=lo_legs, belt=lo_belt, head=lo_head, headgear=lo_headgear, headgear_back=lo_scarf_back))


# ------------------------------------------------------------------ the whole figure, for portraits and class art
START = {"kovar": "palcat", "zrec": "berla", "vlkodlak": "nuz", "alchymistka": "nuz", "loutkarka": "hul"}


def figure_fn(cid):
    def fn(x, y, s, pose):
        p = pose if pose in G.CLS[cid].poses else "idle"
        for layer in G.LAYERS:
            slot = G.SLOT_OF.get(layer)
            look = None
            if slot in ("body", "head", "belt"):
                look = "default"
            elif slot == "weapon":
                look = START[cid]
            elif slot == "lamp":
                look = "lojovy_kahan"
            elif slot == "offhand":
                continue
            if G.skip(cid, layer, p):
                continue
            G.draw(cid, layer, look, p, x, y, s)
    return fn


def jobs():
    pt = [(f"hero_{c}", 256, 256, (lambda fn, k: lambda b: H.portrait(b, fn, k["hy"], k["hr"]))(figure_fn(c), G.CLS[c].k)) for c in START]
    glow = {"kovar": ("#ff9a3a", 0.3, 0.6), "zrec": ("#ffe7a0", 0.55, 0.8), "vlkodlak": ("#cfe0ff", 0.4, 0.75),
            "alchymistka": ("#86e05a", 0.6, 0.6), "loutkarka": ("#f2d060", 0.45, 0.7)}
    ui = [(f"class_{c}", 480, 720, H.class_art(figure_fn(c), glow[c][1], glow[c][2], glow[c][0]), True) for c in START]
    return {"portraits": pt, "ui": ui}


if __name__ == "__main__":
    import common
    common.run(jobs())
