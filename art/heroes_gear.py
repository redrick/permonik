"""Heroes in layers, so what they wear shows: game/assets/sprites/heroes/<class>/<pose>/<layer>[.<look>].png.

The game stacks the layers in LAYERS order (back to front) for the gear the hero has on. A layer named
without a look is the class's own body; `default` is what the class wears with that slot empty.
"""
import math, os
import common
from common import FEET
from lib import Col, ell, bez, rrect
from style3 import (C, T, stroke, shape, form, fill, hatch, tube, cast_shadow, dot, face, head_outline, clip_fill, LINE)
from chars3 import Person
import heroes as H
from heroes import (SKIN, IRON, IRON_LT, WOOD, WOOD_LT, BRASS, BONE, RED, LEATHER, BOOT, FLAME, FLAME_CORE, GLOW,
                    ik, hnd, legs, torso_pts, skirt_pts, neck, beard, moustache, kahan, lean_rot, pick, valaska, staff,
                    spark, crossbow_back, braid)

LAYERS = ("headgear_back", "back", "body_far", "weapon_far", "lamp_far", "hand_far", "offhand", "legs", "body",
          "belt", "lamp", "weapon_belt", "body_near", "weapon", "hand", "head", "headgear")
SLOT_OF = {"headgear_back": "head", "body_far": "body", "weapon_far": "weapon", "lamp_far": "lamp", "offhand": "offhand",
           "body": "body", "belt": "belt", "lamp": "lamp", "weapon_belt": "weapon", "body_near": "body",
           "weapon": "weapon", "headgear": "head"}
LOOKS = {
    "body": ("default", "kozeny_kabatec", "kozich", "krouzkova_kosile", "krunyr", "platova_zbroj"),
    "head": ("default", "beranice", "kapuce", "havirska_prilba", "prilba", "velka_prilba"),
    "belt": ("default", "opasek", "siroky_opasek"),
    "lamp": ("lojovy_kahan", "havirsky_kahan", "mosazny_kahan", "karbidka", "permonikuv_kahan"),
    "offhand": ("stit", "paveza", "kniha"),
    "weapon": ("krumpac", "sekera", "valaska", "palcat", "obusek", "berla", "cep", "kord", "savle", "obourucni_mec",
               "nuz", "hul", "kuse", "luk"),
}
POSES = ("idle", "walk1", "walk2", "walk3", "walk4", "windup", "attack", "cast", "hit", "dead")

STEEL = Col(0.66, "#a3abb5"); STEEL_D = Col(0.45, "#6f7782"); STEEL_L = Col(0.88, "#dde2e8")
CHAIN = Col(0.55, "#868c94"); FUR = Col(0.4, "#6e4e34"); FUR_L = Col(0.85, "#e3d6bd")
HIDE = Col(0.38, "#7a5536"); HIDE_D = Col(0.28, "#5a3c26"); CLOTH = Col(0.42, "#5a6470"); CLOTH_D = Col(0.3, "#424a55")
HOOD = Col(0.35, "#5d4a3a"); HOOD_D = Col(0.25, "#45362a"); FLEECE = Col(0.82, "#d9ccb0"); FLEECE_D = Col(0.6, "#a8987a")
GOLD = Col(0.7, "#d4aa48"); COLD_FLAME = Col(0.92, "#dff3ff"); COLD_GLOW = Col(0.9, "#9fd8ff", alpha=0.18)


# ------------------------------------------------------------------ classes: the body, and what they wear bare
class Cls:
    def __init__(self, k, poses, sleeve, cuff, hem, belt, weapon_at, lie_w, shadow_rx, drop):
        self.k, self.poses, self.sleeve, self.cuff, self.hem, self.belt = k, poses, sleeve, cuff, hem, belt
        self.weapon_at, self.lie_w, self.shadow_rx, self.drop = weapon_at, lie_w, shadow_rx, drop


CLS = {
    "havir": Cls(H.HAV, H.HAV_POSE, H.H_SMOCK, H.H_SMOCK_DK, 52, (58, 62),
                 {"upright": ("near", 72), "swing": ("near", -16), "wind": ("near", 128), "flung": ("near", 115), "hang": ("far", -96)},
                 23, 18, (40, 15)),
    "zbojnice": Cls(H.ZB, H.ZB_POSE, H.Z_SHIRT, RED, 58, (58, 67),
                    {"rest": ("near", 78), "strike": ("near", 35), "flung": ("near", 120), "raised": ("near", 100),
                     "belt": ("belt", -100), "chop_back": ("near", 145)}, 29, 16, (44, 3)),
    "vedma": Cls(H.VE, H.VE_POSE, H.V_SHAWL, H.V_BLOUSE, 60, (59, 64),
                 {"stand": ("near", 92), "thrust": ("near", -4), "raise": ("near", 96), "flung": ("near", 112), "draw": ("near", 8)},
                 26, 16, (-6, 15)),
}


EXTRA = {}  # cls -> module-level hooks from heroes_new.py: back, legs, head, torso, belt, headgear, headgear_back


def arm_geom(k, side, spec):
    S = (side*k.sh_w, k.sh_y-1.5)
    if spec[0] == "k":
        E, Hd = ik(S, (spec[1], spec[2]), k.up, k.fo, spec[3])
    else:
        ua, fa_ = math.radians(spec[1]), math.radians(spec[2])
        E = (S[0]+math.cos(ua)*k.up, S[1]+math.sin(ua)*k.up)
        Hd = (E[0]+math.cos(fa_)*k.fo, E[1]+math.sin(fa_)*k.fo)
    return S, E, Hd, math.degrees(math.atan2(Hd[1]-E[1], Hd[0]-E[0]))


def sleeve(k, side, spec, col, cuff=None, under=None, plate=False, fur=False, rings=False, rolled=False):
    S, E, Hd, fa = arm_geom(k, side, spec)
    f = (Hd[0]-math.cos(math.radians(fa))*2.2, Hd[1]-math.sin(math.radians(fa))*2.2)
    tube([S, E], k.arm_w[0], k.arm_w[0]*0.95, col)
    if rolled:
        tube([E, f], k.arm_w[0]*0.85, k.arm_w[1], SKIN)
        tube([E, (E[0]+(f[0]-E[0])*0.18, E[1]+(f[1]-E[1])*0.18)], k.arm_w[0]*1.08, k.arm_w[0]*1.0, col, sh=0)
        return Hd, fa
    tube([E, f], k.arm_w[0]*0.95, k.arm_w[1], col)
    if rings:
        for P0, P1 in ((S, E), (E, f)):
            for t in (0.25, 0.5, 0.75):
                x, y = P0[0]+(P1[0]-P0[0])*t, P0[1]+(P1[1]-P0[1])*t
                stroke(ell(x, y, 1.1, 0.8, 8), LINE*0.35, closed=True, g=Col(0.3, "#4a4e55"))
    if plate:
        shape(ell(E[0], E[1], k.arm_w[0]*0.62, k.arm_w[0]*0.62, 14), STEEL_L, LINE*0.7)
        for P0, P1 in ((S, E), (E, f)):
            m = ((P0[0]+P1[0])/2, (P0[1]+P1[1])/2)
            stroke([(m[0]-1.8, m[1]+1.8), (m[0]+1.8, m[1]-1.8)], LINE*0.5)
    if cuff is not None:
        c0 = (f[0]-math.cos(math.radians(fa))*1.6, f[1]-math.sin(math.radians(fa))*1.6)
        tube([c0, f], k.arm_w[1]+(1.4 if fur else 0.6), k.arm_w[1]+(1.4 if fur else 0.6), cuff, sh=0)
    return Hd, fa


# ------------------------------------------------------------------ body armour
def body_parts(cls, look):
    """sleeve colour, cuff, extras for a body look on this class"""
    c = CLS[cls]
    if look == "default":
        return dict(col=c.sleeve, cuff=c.cuff, rolled=bool(getattr(c, "rolled", False)))
    return {
        "kytel": dict(col=CLOTH, cuff=CLOTH_D),
        "kozeny_kabatec": dict(col=c.sleeve, cuff=c.cuff),
        "kozich": dict(col=FUR, cuff=FUR_L, fur=True),
        "krouzkova_kosile": dict(col=CHAIN, cuff=STEEL_D, rings=True),
        "krunyr": dict(col=c.sleeve, cuff=c.cuff),
        "platova_zbroj": dict(col=STEEL, cuff=STEEL_D, plate=True),
    }[look]


def torso_default(cls, k):
    if cls in EXTRA: return EXTRA[cls].torso(k)
    if cls == "havir":
        tors = torso_pts(k, 52, 16.5, waist_w=15.5)
        form(tors, H.H_SMOCK, sdx=-2.4, sdy=1.2, sh=0.14)
        clip_fill(tors, [(-20, 52), (20, 52), (20, 56), (-20, 56)], H.H_SMOCK_DK)
        stroke([(1.2, k.sh_y+1), (1.6, 53)], LINE*0.8)
        for by in (90, 82, 74, 66): shape(ell(-0.6, by, 0.9, 0.9, 10), BRASS, LINE*0.5)
        for sx in (-1, 1):
            shape([(sx*0.8, k.sh_y+0.6), (sx*5.5, k.sh_y+3.2), (sx*9.5, k.sh_y+0.6), (sx*3.6, k.sh_y-4.5)], H.H_SMOCK_DK, LINE*0.8)
        stroke(bez((-9, 86), (-9.5, 78), (-10.5, 70), (-11, 64)), LINE*0.5, g=H.H_SMOCK_DK)
    elif cls == "zbojnice":
        tors = torso_pts(k, 58, 13.5, waist_w=11.5, collar=4)
        form(tors, H.Z_SHIRT, sdx=-2, sdy=1, sh=0.1)
        for sx in (-1, 1):
            v = [(sx*4.5, k.sh_y+2.4), (sx*(k.sh_w+1.6), k.sh_y-3.5), (sx*13.5, 72), (sx*13.5, 60), (sx*4, 60), (sx*3.2, 74)]
            form(v, H.Z_VEST, sdx=-1.5, sdy=1, sh=0.12)
            for yy in (86, 78, 70): dot(sx*4.2, yy, 0.8, RED)
        for i in range(5): dot(-2+i*1.0, k.sh_y+1.6-abs(i-2)*0.5, 0.55, RED)
    else:
        tors = torso_pts(k, 60, 13, waist_w=12, collar=4)
        form(tors, H.V_BLOUSE, sdx=-2, sdy=1, sh=0.1)
        r = k.hr; cy = k.hy
        shawl = [(-k.sh_w-2.5, k.sh_y+0.5)] + bez((-k.sh_w-2.5, k.sh_y+0.5), (-k.sh_w-3.2, 84), (-9, 72), (0, 68)) + \
            bez((0, 68), (9, 72), (k.sh_w+3.2, 84), (k.sh_w+2.5, k.sh_y+0.5)) + [(r*0.9, cy-r*0.6), (-r*0.9, cy-r*0.6)]
        form(shawl, H.V_SHAWL, sdx=-2, sdy=1, sh=0.14)
        for i in range(9):
            t = i/8
            px, py = (-9*(1-t)+9*t), 70+math.sin(t*math.pi)*2
            stroke([(px, py), (px+0.3, py-3.5)], LINE*0.5)
        for i in range(7):
            a = math.radians(200+i*20)
            dot(math.cos(a)*6.5, k.sh_y-1+math.sin(a)*5, 1.0, BONE)


def torso_armour(cls, k, look):
    hem = CLS[cls].hem
    if look == "default":
        return torso_default(cls, k)
    if look == "kytel":
        tors = torso_pts(k, hem, 16.0, waist_w=14.5)
        form(tors, CLOTH, sdx=-2.4, sdy=1.2, sh=0.14)
        clip_fill(tors, [(-20, hem), (20, hem), (20, hem+4), (-20, hem+4)], CLOTH_D)
        stroke([(1.2, k.sh_y+1), (1.6, hem+1)], LINE*0.8)
        for by in (90, 82, 74): shape(ell(-0.6, by, 0.9, 0.9, 10), BRASS, LINE*0.5)
    elif look == "kozeny_kabatec":
        tors = torso_pts(k, hem-2, 15.0, waist_w=13.5)
        form(tors, HIDE, sdx=-2, sdy=1, sh=0.16)
        clip_fill(tors, [(-20, hem-2), (20, hem-2), (20, hem+2), (-20, hem+2)], HIDE_D)
        for yy in range(int(hem+4), int(k.sh_y-3), 5):
            stroke([(-1.8, yy), (1.8, yy+2.2)], LINE*0.5, g=Col(0.8, "#d8c8a0"))
            stroke([(1.8, yy), (-1.8, yy+2.2)], LINE*0.5, g=Col(0.8, "#d8c8a0"))
        stroke([(0, k.sh_y), (0, hem)], LINE*0.7)
    elif look == "kozich":
        tors = torso_pts(k, hem-10, 18.0, waist_w=15.5)
        form(tors, FUR, sdx=-2.4, sdy=1.2, sh=0.16)
        hatch(tors, 1.5, 70, 0.35, alpha=0.35)
        shape(bez((-k.sh_w-1, k.sh_y-1), (-6, k.sh_y-6), (6, k.sh_y-6), (k.sh_w+1, k.sh_y-1)) +
              bez((k.sh_w+1, k.sh_y-1), (8, k.sh_y+4), (-8, k.sh_y+4), (-k.sh_w-1, k.sh_y-1)), FUR_L, LINE*0.7)
        shape([(-18.5, hem-10), (18.5, hem-10), (18.2, hem-6.5), (-18.2, hem-6.5)], FUR_L, LINE*0.7)
        stroke([(0.5, k.sh_y-5), (0.8, hem-6)], LINE*0.7)
    elif look == "krouzkova_kosile":
        tors = torso_pts(k, hem-6, 16.5, waist_w=14.5)
        form(tors, CHAIN, sdx=-2, sdy=1, sh=0.14)
        C.saveState(); from style3 import poly; C.clipPath(poly(tors), stroke=0, fill=0)
        for row, yy in enumerate(range(int(hem-8), int(k.sh_y+4), 2)):
            for xx in range(-20, 21, 2):
                stroke(ell(xx+(row % 2), yy, 1.05, 0.75, 8), LINE*0.3, closed=True, g=Col(0.3, "#4a4e55"))
        C.restoreState()
        stroke(bez((-16.5, hem-6), (-6, hem-7.5), (6, hem-7.5), (16.5, hem-6)), LINE*0.9)
    elif look in ("krunyr", "platova_zbroj"):
        if look == "platova_zbroj":
            for i, (y0, w) in enumerate(((hem-1, 15.5), (hem-6, 15.0))):
                shape([(-w, y0), (w, y0), (w-0.5, y0-5.5), (-w+0.5, y0-5.5)], STEEL_D if i else STEEL, LINE*0.7)
        under = torso_pts(k, hem, 14.5, waist_w=13)
        form(under, LEATHER, sh=0.1)
        plate = torso_pts(k, hem+3, 14.0, waist_w=12.5, collar=4.5)
        form(plate, STEEL, sdx=-2.6, sdy=1.2, sh=0.2)
        stroke(bez((1.5, k.sh_y-1), (3.5, 80), (3.5, 70), (1.5, hem+4)), LINE*0.6, g=STEEL_D)
        stroke(bez((5, k.sh_y-4), (8, 84), (9, 76), (7.5, 70)), LINE*1.4, g=STEEL_L, alpha=0.7)
        for xx in (-10, 10): dot(xx, k.sh_y-3, 0.7, 0.2)
        shape([(-k.sh_w-1, k.sh_y-1), (k.sh_w+1, k.sh_y-1), (k.sh_w, k.sh_y+2.5), (-k.sh_w, k.sh_y+2.5)], STEEL_D, LINE*0.7)


def pauldron(k, side):
    x = side*k.sh_w
    sh = bez((x-6, k.sh_y-4), (x-6.5, k.sh_y+5), (x+6.5, k.sh_y+5), (x+6, k.sh_y-4)) + [(x, k.sh_y-6)]
    form(sh, STEEL, sh=0.2)
    stroke(bez((x-5, k.sh_y-1), (x-2, k.sh_y+1.5), (x+2, k.sh_y+1.5), (x+5, k.sh_y-1)), LINE*0.5)


# ------------------------------------------------------------------ belts and lamps
def belt(cls, k, look):
    if look == "default" and cls in EXTRA: return EXTRA[cls].belt(k)
    y0, y1 = CLS[cls].belt
    if look == "default":
        if cls == "havir":
            shape([(-15.8, 58), (15.8, 58), (16, 62), (-16, 62)], LEATHER, LINE*0.8)
            shape(rrect(2.5, 57.4, 4, 5.2, 0.6), BRASS, LINE*0.6)
        elif cls == "zbojnice":
            form([(-14.2, 58), (14.2, 58), (14.6, 67), (-14.6, 67)], H.Z_BELT, sh=0.12)
            for xx in (-11, -6, -1, 4, 9): shape(ell(xx, 62.5, 1.1, 1.1, 10), BRASS, LINE*0.5)
            for xx in (-8.5, 6.5): stroke([(xx, 59), (xx, 66)], LINE*0.6)
        else:
            shape([(-13.5, 59), (13.5, 59), (13.8, 64), (-13.8, 64)], RED, LINE*0.7)
    elif look == "opasek":
        m = (y0+y1)/2
        shape([(-15, m-1.6), (15, m-1.6), (15.2, m+1.6), (-15.2, m+1.6)], LEATHER, LINE*0.7)
        shape(rrect(1.5, m-2.4, 3.6, 4.8, 0.5), IRON_LT, LINE*0.6)
    elif look == "siroky_opasek":
        form([(-15.5, y0-0.5), (15.5, y0-0.5), (15.8, y0+8), (-15.8, y0+8)], H.Z_BELT, sh=0.12)
        for xx in (-12, -7, -2, 3, 8, 12.5): shape(ell(xx, y0+3.8, 1.1, 1.1, 10), BRASS, LINE*0.5)
        shape(rrect(-1.5, y0+0.6, 5, 6.4, 0.8), BRASS, LINE*0.6)
    if cls == "vedma":
        for i, xx in enumerate((-9, -6.5, -4)):
            tube([(xx, 60), (xx-1+i, 50)], 1.6, 1.2, H.V_HERB, LINE*0.6, sh=0)
            for j in range(3): shape(ell(xx-0.5+i*0.3, 51.5+j*2.5, 1.6, 0.8, 8, rot=30), H.V_HERB, LINE*0.4)


def lamp(look, x, y, s=0.95):
    if look == "lojovy_kahan":
        kahan(x, y, s, body=Col(0.35, "#4e4a46"), flame=Col(0.8, "#ffbf5a"))
    elif look == "havirsky_kahan":
        kahan(x, y, s)
    elif look == "mosazny_kahan":
        kahan(x, y, s, body=BRASS)
    elif look == "permonikuv_kahan":
        kahan(x, y, s, body=Col(0.85, "#d7dce2"), flame=COLD_FLAME, glow=COLD_GLOW)
    elif look == "karbidka":
        with T(x, y, s):
            stroke(bez((0, 0), (-1.2, 1.5), (0.5, 3.5), (1.2, 2.2)), LINE*0.7)
            for rr in (7, 4.5): fill(ell(7, -3, rr, rr, 24), Col(0.9, "#fff6dc", alpha=0.18))
            form(rrect(-3, -12, 6, 10, 1.2), BRASS, sh=0.15)
            stroke([(-3, -7), (3, -7)], LINE*0.6)
            shape(ell(5.2, -4, 2.6, 3.4, 16), Col(0.85, "#e2e6ea"), LINE*0.7)
            shape(ell(7.4, -4, 0.9, 1.5, 10), Col(0.97, "#ffffff"), LINE*0.4)


# ------------------------------------------------------------------ weapons and off-hands
def weapon(look, x, y, ang, flip=False, glow=False, plant=False):
    if look == "krumpac": return pick(x, y, ang, 34, 12)
    if look == "valaska": return valaska(x, y, ang, 30, 8, flip)
    if look == "hul": return staff(x, y, ang, 58 if plant else 46, 78 if plant else 40, glow)
    with T(x, y, 1, rot=ang):
        if flip: C.scale(1, -1)
        if look == "sekera":
            tube([(-10, 0), (40, 0)], 2.8, 2.6, WOOD, sh=0.1)
            bl = [(34, 1.2)] + bez((34, 1.2), (30, 6), (29, 12), (31, 16)) + bez((31, 16), (37, 17), (43, 14), (45, 9)) + [(40, 1.2)]
            form(bl, IRON_LT, sdx=-0.8, sdy=0.8, sh=0.14)
            stroke(bez((30.5, 15), (37, 16.2), (42.5, 13.5), (44.4, 9)), LINE*1.2, g=STEEL_L, alpha=0.6)
            shape([(33.5, -3), (40.5, -3), (40.5, 1.4), (33.5, 1.4)], IRON, LINE*0.8)
        elif look == "palcat":
            tube([(-4, 0), (20, 0)], 2.2, 2.0, WOOD, sh=0.1)
            shape(rrect(-5, -1.6, 3, 3.2, 0.6), LEATHER, LINE*0.6)
            for a in range(0, 360, 60):
                with T(24, 0, 1, rot=a):
                    form([(0, 0), (6, -1.2), (6.5, 1.2), (0, 1.6)], STEEL, sh=0.15)
            shape(ell(24, 0, 3, 3, 14), STEEL_D, LINE*0.7)
        elif look == "obusek":
            tube([(-3, 0), (12, 0), (24, 0)], 2.2, 4.4, WOOD_LT, sh=0.15)
            for t in (14, 18, 22): dot(t, 1.5 if t % 4 else -1.5, 0.7, 0.2)
        elif look == "berla":
            tube([(-3, 0), (20, 0)], 1.8, 1.8, GOLD, sh=0.1)
            for t in (4, 12): shape(rrect(t-0.8, -1.6, 1.6, 3.2, 0.4), BRASS, LINE*0.5)
            shape(ell(24, 0, 3.6, 3.6, 16), GOLD, LINE*0.8)
            shape([(27, 0), (31.5, -2.4), (33.5, 0), (31.5, 2.4)], GOLD, LINE*0.6)
            dot(24, 0, 1.4, Col(0.4, "#a8382e"))
        elif look == "cep":
            tube([(-8, 0), (26, 0)], 2.6, 2.4, WOOD, sh=0.1)
            stroke(bez((26, 0), (28, 2), (29, 3.5), (30, 5)), LINE*1.2, g=IRON)
            with T(30, 5, 1, rot=-60):
                tube([(0, 0), (14, 0)], 3.2, 3.6, WOOD_LT, sh=0.12)
                for t in (4, 8, 12): shape(ell(t, 2.4, 1, 1.2, 8), IRON, LINE*0.4)
        elif look in ("kord", "savle", "obourucni_mec", "nuz"):
            L, back, w = {"kord": (36, 4, 1.6), "savle": (32, 4, 2.4), "obourucni_mec": (50, 10, 2.8), "nuz": (13, 3, 1.8)}[look]
            tube([(-back, 0), (-1, 0)], 2.2, 2.2, LEATHER, sh=0)
            shape(ell(-back-0.8, 0, 1.6, 1.6, 10), BRASS, LINE*0.5)
            if look == "savle":
                bl = [(0, w/2)] + bez((0, w/2), (L*0.5, w*0.7), (L*0.85, 1.5), (L, -3.5)) + bez((L, -3.5), (L*0.8, -1.4), (L*0.5, -w*0.5), (0, -w/2))
            else:
                bl = [(0, w/2), (L-3, w/2), (L, 0), (L-3, -w/2), (0, -w/2)]
            form(bl, STEEL, sdx=0, sdy=0.6, sh=0.12)
            stroke([(1, 0), (L*0.8, 0)], LINE*0.4, g=STEEL_L, alpha=0.7)
            if look == "kord":
                stroke(bez((0, -3.4), (-3, -3), (-4, 1), (-back, 1.5)), LINE*0.8, g=BRASS)
            gw = 3.6 if look != "obourucni_mec" else 6
            shape(rrect(-0.6, -gw, 1.6, gw*2, 0.6), BRASS if look != "obourucni_mec" else IRON, LINE*0.6)
        elif look == "kuse":
            tube([(-8, 0), (22, 0)], 3.0, 2.6, WOOD, sh=0.1)
            bow = bez((20, -13), (25, -5), (25, 5), (20, 13))
            tube(bow, 2.4, 1.8, WOOD_LT, LINE*0.9, sh=0)
            stroke([(20, -13), (12, 0), (20, 13)], LINE*0.5)
            shape(rrect(2, -1.4, 6, 2.8, 0.4), IRON, LINE*0.5)
        elif look == "luk":
            C.rotate(-ang + 90)
            bow = bez((0, -26), (9, -14), (9, 14), (0, 26))
            tube(bow, 2.6, 1.6, WOOD_LT, LINE*0.9, sh=0)
            stroke([(0, -26), (-1.5, 0), (0, 26)], LINE*0.5)
            shape(rrect(5.2, -2.2, 3, 4.4, 0.6), LEATHER, LINE*0.5)


def offhand(look, x, y):
    with T(x, y, 1):
        if look == "stit":
            sh = ell(0, 0, 11, 11, 32)
            form(sh, WOOD, sh=0.18)
            for a in range(0, 180, 45):
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                stroke([(-ca*10.5, -sa*10.5), (ca*10.5, sa*10.5)], LINE*0.4, g=Col(0.3, "#5a4030"))
            stroke(ell(0, 0, 10.6, 10.6, 32), LINE*1.4, closed=True, g=IRON)
            shape(ell(0, 0, 3.2, 3.2, 16), IRON_LT, LINE*0.7)
        elif look == "paveza":
            pv = [(-10, -18), (10, -18), (11, 14)] + bez((11, 14), (6, 19), (-6, 19), (-11, 14))
            form(pv, Col(0.82, "#d9cfb6"), sh=0.18)
            shape([(-1.6, -12), (1.6, -12), (1.6, 13), (-1.6, 13)], RED, LINE*0.5)
            shape([(-7, 2.5), (7, 2.5), (7, 5.5), (-7, 5.5)], RED, LINE*0.5)
            stroke([(-3.5, -18), (-3.5, 17.5)], LINE*0.4, g=0.4)
            stroke([(3.5, -18), (3.5, 17.5)], LINE*0.4, g=0.4)
        elif look == "kniha":
            form(rrect(-5, -6.5, 10, 13, 1.0), Col(0.32, "#5b2e2a"), sh=0.15)
            shape(rrect(-4.2, -6.5, 1.4, 13, 0.3), BRASS, LINE*0.5)
            shape(ell(1.5, 0, 2, 2.6, 12), GOLD, LINE*0.5)


# ------------------------------------------------------------------ heads
def headgear_back(cls, k, look):
    if look == "default" and cls in EXTRA: return EXTRA[cls].headgear_back(k)
    r = k.hr; cy = k.hy
    hood = bez((-r*1.35, cy-r*1.6), (-r*1.75, cy+r*0.6), (-r*1.1, cy+r*1.75), (r*0.2, cy+r*1.7)) + \
        bez((r*0.2, cy+r*1.7), (r*1.3, cy+r*1.6), (r*1.6, cy+r*0.6), (r*1.4, cy-r*1.4))
    if look == "default" and cls == "vedma":
        form(hood, H.V_SHAWL, sdx=-1.5, sdy=1, sh=0.15)
    elif look == "kapuce":
        form(hood, HOOD, sdx=-1.5, sdy=1, sh=0.15)


def hood_front(k, col, dk):
    r = k.hr; cy = k.hy
    hf = bez((-r*1.25, cy-r*0.9), (-r*1.4, cy+r*0.9), (-r*0.6, cy+r*1.5), (r*0.2, cy+r*1.45)) + \
        bez((r*0.2, cy+r*1.45), (r*1.0, cy+r*1.4), (r*1.4, cy+r*0.9), (r*1.25, cy-r*0.6)) + \
        bez((r*1.25, cy-r*0.6), (r*1.3, cy+r*0.6), (r*0.8, cy+r*1.1), (r*0.2, cy+r*1.1)) + \
        bez((r*0.2, cy+r*1.1), (-r*0.6, cy+r*1.12), (-r*1.15, cy+r*0.6), (-r*1.05, cy-r*0.9))
    form(hf, col, sdx=-1, sdy=0.8, sh=0.12)
    stroke(bez((-r*1.2, cy+r*0.5), (-r*0.6, cy+r*1.3), (r*0.6, cy+r*1.3), (r*1.25, cy+r*0.6)), LINE*0.6, g=dk)


def headgear(cls, k, look):
    if look == "default" and cls in EXTRA: return EXTRA[cls].headgear(k)
    r = k.hr; cy = k.hy
    if look == "default":
        if cls == "havir":
            cap = bez((-r*1.06, cy+r*0.55), (-r*1.12, cy+r*1.7), (r*1.12, cy+r*1.7), (r*1.06, cy+r*0.55)) + \
                bez((r*1.06, cy+r*0.55), (r*0.4, cy+r*0.68), (-r*0.4, cy+r*0.68), (-r*1.06, cy+r*0.55))
            form(cap, H.H_CAP, sdx=-1.5, sdy=1)
            shape(rrect(-r*1.1, cy+r*0.45, r*2.2, r*0.3, 0.8), LEATHER, LINE*0.8)
            shape([(r*0.2, cy+r*0.8), (r*0.58, cy+r*0.8), (r*0.58, cy+r*1.18), (r*0.2, cy+r*1.18)], BRASS, LINE*0.6)
        elif cls == "zbojnice":
            shape(bez((-r*1.08, cy+r*0.35), (-r*0.5, cy+r*0.95), (r*0.5, cy+r*0.95), (r*1.08, cy+r*0.35)) +
                  bez((r*1.08, cy+r*0.35), (r*1.1, cy+r*0.55), (r*0.5, cy+r*1.12), (-r*1.1, cy+r*0.55)), RED, LINE*0.6)
        else:
            hood_front(k, H.V_SHAWL, H.V_SHAWL_DK)
    elif look == "kapuce":
        hood_front(k, HOOD, HOOD_D)
    elif look == "beranice":
        cap = bez((-r*1.12, cy+r*0.5), (-r*1.3, cy+r*2.0), (r*1.3, cy+r*2.0), (r*1.12, cy+r*0.5)) + \
            bez((r*1.12, cy+r*0.5), (r*0.4, cy+r*0.7), (-r*0.4, cy+r*0.7), (-r*1.12, cy+r*0.5))
        form(cap, FLEECE, sdx=-1.5, sdy=1, sh=0.16)
        for i in range(14):
            a = math.radians(15+i*11)
            x, y = math.cos(a)*r*0.95, cy+r*0.7+math.sin(a)*r*1.05
            stroke(bez((x-1, y), (x-0.6, y+1.2), (x+0.6, y+1.2), (x+1, y)), LINE*0.45, g=FLEECE_D)
        shape(rrect(-r*1.18, cy+r*0.38, r*2.36, r*0.42, 1.0), FLEECE_D, LINE*0.7)
    elif look == "havirska_prilba":
        dome = bez((-r*1.08, cy+r*0.5), (-r*1.15, cy+r*1.85), (r*1.15, cy+r*1.85), (r*1.08, cy+r*0.5)) + \
            bez((r*1.08, cy+r*0.5), (r*0.4, cy+r*0.62), (-r*0.4, cy+r*0.62), (-r*1.08, cy+r*0.5))
        form(dome, Col(0.35, "#4a3a2c"), sdx=-1.5, sdy=1, sh=0.18)
        stroke(bez((-r*0.2, cy+r*1.75), (0, cy+r*1.2), (r*0.1, cy+r*0.9), (r*0.1, cy+r*0.6)), LINE*0.6)
        shape([(r*0.3, cy+r*0.42), (r*1.65, cy+r*0.32), (r*1.6, cy+r*0.62), (r*0.3, cy+r*0.72)], Col(0.3, "#3e3026"), LINE*0.7)
        shape(rrect(r*0.45, cy+r*0.9, r*0.45, r*0.45, 0.4), BRASS, LINE*0.6)
    elif look == "prilba":
        dome = bez((-r*1.0, cy+r*0.55), (-r*1.05, cy+r*1.9), (r*1.05, cy+r*1.9), (r*1.0, cy+r*0.55))
        form(dome + [(-r*1.0, cy+r*0.55)], STEEL, sdx=-1.5, sdy=1, sh=0.2)
        brim = ell(0, cy+r*0.55, r*1.75, r*0.3, 28)
        form(brim, STEEL_D, sh=0.15)
        stroke(bez((r*0.35, cy+r*1.75), (r*0.55, cy+r*1.4), (r*0.65, cy+r*1.0), (r*0.6, cy+r*0.7)), LINE*1.2, g=STEEL_L, alpha=0.7)
    elif look == "velka_prilba":
        hm = [(-r*1.12, cy-r*1.1), (r*1.18, cy-r*1.1)] + bez((r*1.18, cy-r*1.1), (r*1.25, cy+r*0.4), (r*1.2, cy+r*1.2), (r*0.8, cy+r*1.6)) + \
            bez((r*0.8, cy+r*1.6), (r*0.2, cy+r*1.85), (-r*0.6, cy+r*1.75), (-r*1.12, cy+r*1.2)) + [(-r*1.12, cy-r*1.1)]
        form(hm, STEEL, sdx=-1.8, sdy=1, sh=0.22)
        shape([(-r*0.1, cy+r*0.12), (r*1.2, cy+r*0.12), (r*1.2, cy+r*0.32), (-r*0.1, cy+r*0.32)], Col(0.08, "#151416"), LINE*0.5)
        for yy in (-0.35, -0.6):
            for xx in (0.55, 0.8, 1.0): dot(r*xx, cy+r*yy, 0.55, 0.1)
        stroke([(r*0.25, cy+r*1.8), (r*0.25, cy-r*1.05)], LINE*0.7, g=STEEL_D)


# ------------------------------------------------------------------ the class bodies, layer by layer
def class_back(cls, k, pose):
    if cls in EXTRA: return EXTRA[cls].back(k, pose)
    r = k.hr; cy = k.hy
    if cls == "havir":
        flek = [(-15, 63)] + bez((-15, 63), (-19, 52), (-19, 44), (-17, 38)) + [(-6, 40), (-5, 62)]
        form(flek, H.H_FLEK, sh=0.15)
    elif cls == "zbojnice":
        crossbow_back(k)
        braid(-r*0.8, cy-r*0.2, -r*1.15, cy-r*3.6)


def class_legs(cls, k, lg):
    if cls in EXTRA: return EXTRA[cls].legs(k, lg)
    if cls == "havir":
        legs(k, lg, H.H_TROUS, BOOT, boot_h=9, wk=1.15)
    elif cls == "zbojnice":
        ph = legs(k, lg, H.Z_LEG, BOOT, boot_h=10)
        xs = [p[0][-1][0] for p in ph]
        form(skirt_pts(60, 13.5, 34, min(-15, min(xs)-5), max(15, max(xs)+6)), H.Z_SKIRT, sdx=-2, sdy=1, sh=0.14)
        for xx in (-8, -2, 4, 10): stroke([(xx*0.7, 58), (xx, 36)], LINE*0.45, g=Col(0.25, "#3c3242"))
    else:
        ph = legs(k, lg, H.V_DRESS, BOOT, boot_h=6)
        xs = [p[0][-1][0] for p in ph]
        form(skirt_pts(62, 13, 8, min(-17, min(xs)-6), max(17, max(xs)+6)), H.V_DRESS, sdx=-2.4, sdy=1, sh=0.15)
        for xx in (-10, -4, 3, 9): stroke(bez((xx*0.6, 58), (xx*0.8, 40), (xx, 25), (xx*1.1, 11)), LINE*0.45, g=Col(0.28, "#3f472d"))
        stroke(bez((-15, 18), (-5, 16.5), (5, 16.5), (16, 18)), LINE*0.6, g=RED)


def class_head(cls, k, md, look):
    if cls in EXTRA: return EXTRA[cls].head(k, md, look)
    r = k.hr; cy = k.hy
    covered = look == "velka_prilba"
    if cls == "havir":
        head(k, md, neck_w=3.2, do_face=False)
        for sx in (-1, 1):
            shape(bez((sx*r*0.98, cy+r*0.45), (sx*r*1.08, cy+r*0.1), (sx*r*1.02, cy-r*0.2), (sx*r*0.9, cy-r*0.3)) +
                  [(sx*r*0.8, cy+r*0.4)], H.H_BEARD, LINE*0.7)
        beard(k, H.H_BEARD, 1.25)
        if not covered:
            face(r*0.2, cy, r*0.95, md)
        moustache(k, H.H_BEARD)
    elif cls == "zbojnice":
        braid(r*0.9, cy-r*0.55, r*0.75, cy-r*3.3)
        head(k, md, neck_w=2.5)
        hair = bez((-r*1.04, cy-r*0.1), (-r*1.2, cy+r*1.3), (r*1.2, cy+r*1.3), (r*1.04, cy-r*0.1)) + \
            bez((r*1.04, cy-r*0.1), (r*0.95, cy+r*0.45), (r*0.65, cy+r*0.62), (r*0.12, cy+r*0.72)) + \
            bez((r*0.12, cy+r*0.72), (-r*0.4, cy+r*0.62), (-r*0.9, cy+r*0.4), (-r*1.04, cy-r*0.1))
        form(hair, H.Z_HAIR, sdx=-1, sdy=0.6, sh=0.1)
        stroke(bez((r*0.12, cy+r*0.72), (r*0.1, cy+r*0.95), (r*0.05, cy+r*1.05), (0, cy+r*1.12)), LINE*0.5)
    else:
        head(k, md, ear=False, neck_w=2.5)
        hair = bez((-r*1.04, cy-r*0.4), (-r*1.15, cy+r*1.2), (r*1.15, cy+r*1.2), (r*1.04, cy-r*0.2)) + \
            bez((r*1.04, cy-r*0.2), (r*0.9, cy+r*0.4), (r*0.6, cy+r*0.58), (r*0.2, cy+r*0.62)) + \
            bez((r*0.2, cy+r*0.62), (-r*0.3, cy+r*0.55), (-r*0.85, cy+r*0.3), (-r*1.04, cy-r*0.4))
        form(hair, H.V_HAIR, sdx=-1, sdy=0.6, sh=0.1)
        stroke(bez((-r*0.2, cy+r*0.6), (-r*0.5, cy+r*0.5), (-r*0.8, cy+r*0.2), (-r*0.95, cy-r*0.3)), LINE*1.4, g=Col(0.8, "#c8c2c8"))


def head(k, mood, skin=SKIN, ear=True, dx=0.2, neck_w=2.8, do_face=True):
    neck(k, skin, neck_w)
    r = k.hr; cy = k.hy
    if ear: shape(ell(-r*0.95, cy-r*0.05, r*0.2, r*0.3, 14), skin, LINE*0.8)
    shape(head_outline(k), skin)
    if do_face: face(r*dx, cy, r*0.95, mood)


def body(cls, k, pose, layer, look):
    c = CLS[cls]
    lg, near, far, wpn, op, md = c.poses[pose]
    hold = c.weapon_at.get(wpn)
    if layer == "headgear_back": headgear_back(cls, k, look)
    elif layer == "back": class_back(cls, k, pose)
    elif layer == "body_far":
        bp = body_parts(cls, look)
        sleeve(k, -1, far, bp["col"], bp.get("cuff"), plate=bp.get("plate", False), fur=bp.get("fur", False), rings=bp.get("rings", False), rolled=bp.get("rolled", False))
        if look == "platova_zbroj": pauldron(k, -1)
    elif layer in ("weapon_far", "lamp_far", "hand_far", "offhand"):
        _, _, Hd, fa = arm_geom(k, -1, far)
        if layer == "weapon_far" and hold and hold[0] == "far": weapon(look, Hd[0], Hd[1], hold[1])
        if layer == "lamp_far" and pose == "hero" and cls == "havir": lamp(look, Hd[0]-0.5, Hd[1]-1, 1.5)
        if layer == "hand_far": hnd(Hd[0], Hd[1], fa, 2.5 if cls == "havir" else 2.3)
        if layer == "offhand": offhand(look, Hd[0]-2, Hd[1]+(2 if look != "kniha" else 0))
    elif layer == "legs": class_legs(cls, k, lg)
    elif layer == "body": torso_armour(cls, k, look)
    elif layer == "belt": belt(cls, k, look)
    elif layer == "lamp":
        if not (pose == "hero" and cls == "havir"):
            lamp(look, 10, c.belt[0], 0.95)
    elif layer == "weapon_belt":
        if hold and hold[0] == "belt": weapon(look, 6, 63, hold[1])
    elif layer == "body_near":
        bp = body_parts(cls, look)
        sleeve(k, 1, near, bp["col"], bp.get("cuff"), plate=bp.get("plate", False), fur=bp.get("fur", False), rings=bp.get("rings", False), rolled=bp.get("rolled", False))
        if look == "platova_zbroj": pauldron(k, 1)
    elif layer == "weapon":
        _, _, Hd, fa = arm_geom(k, 1, near)
        if hold and hold[0] == "near":
            weapon(look, Hd[0], Hd[1], hold[1], flip=(wpn in ("strike", "chop_back")), glow=(wpn == "raise"), plant=(wpn == "stand"))
    elif layer == "hand":
        _, _, Hd, fa = arm_geom(k, 1, near)
        hnd(Hd[0], Hd[1], fa, 2.5 if cls == "havir" else 2.3, open_=op)
        if cls == "havir" and wpn == "swing":
            F, _ = ik((-k.sh_w, k.sh_y-1.5), (24, 84), k.up, k.fo, -1)
            hnd(F[0], F[1], -20, 2.5)
        if cls == "vedma" and wpn == "thrust":
            F, _ = ik((-k.sh_w, k.sh_y-1.5), (22, 77), k.up, k.fo, -1)
            hnd(F[0], F[1], -10, 2.3)
        if cls == "vedma":
            stroke(bez((Hd[0]-3, Hd[1]-2.5), (Hd[0]-1, Hd[1]-3.5), (Hd[0]+1, Hd[1]-3.5), (Hd[0]+3, Hd[1]-2.5)), LINE*0.9, g=RED)
    elif layer == "head": class_head(cls, k, md, look)
    elif layer == "headgear": headgear(cls, k, look)


def draw(cls, layer, look, pose, x, y, s):
    c = CLS[cls]
    k = Person(**c.k)
    if pose == "dead":
        if layer == "weapon":
            with T(x + c.drop[0]*s, y + c.drop[1]*s, s): weapon(look, 0, 0, 0 if look != "hul" else 2)
            return
        with T(x + (k.hy+k.hr)*s*0.5, y + c.lie_w*s, s, rot=90):
            body(cls, k, pose, layer, look)
        return
    if layer == "back": cast_shadow(x, y, c.shadow_rx*s, 3*s)
    with T(x, y + (1.2 if pose in ("hit", "attack", "windup") else 0), s, rot=lean_rot(pose)):
        body(cls, k, pose, layer, look)


# ------------------------------------------------------------------ what gets rendered
def skip(cls, layer, pose):
    """layers that are empty for this class and pose"""
    c = CLS[cls]
    wpn = c.poses[pose][3]
    hold = c.weapon_at.get(wpn)
    if layer == "weapon_far": return not (hold and hold[0] == "far")
    if layer == "weapon_belt": return not (hold and hold[0] == "belt")
    if layer == "weapon": return not (pose == "dead" or (hold and hold[0] == "near"))
    if layer == "lamp_far": return not (pose == "hero" and cls == "havir")
    if layer == "headgear_back": return False
    return False


def layer_jobs(scale=1.0, size=240, poses=POSES, folder="sprites/heroes"):
    out = {}
    for cls in CLS:
        for pose in poses:
            if pose not in CLS[cls].poses: continue
            items = []
            for layer in LAYERS:
                if skip(cls, layer, pose): continue
                slot = SLOT_OF.get(layer)
                looks = LOOKS[slot] if slot else (None,)
                for look in looks:
                    if layer == "headgear_back" and look not in ("default", "kapuce"): continue
                    if layer == "headgear_back" and look == "default" and cls != "vedma" and cls not in EXTRA: continue
                    name = layer + ("." + look if look else "")
                    fn = (lambda cls, layer, look, pose: lambda b: draw(cls, layer, look, pose, b.w/2, FEET*scale, H.S_HERO*scale))(cls, layer, look, pose)
                    items.append((name, size, size, fn))
            out[f"{folder}/{cls}/{pose}"] = items
    return out


def view_jobs(size=240, folder="sprites/heroes"):
    import hero_views as V
    out = {}
    for cls, sp in V.load().items():
        for view, sfx in V.VIEWS.items():
            for pose in sp.poses[view]:
                items = []
                for layer in V.ORDER[view]:
                    if V.skip(cls, layer, pose, view): continue
                    slot = SLOT_OF.get(layer)
                    for look in (LOOKS[slot] if slot else (None,)):
                        if layer == "headgear_back" and not (look == "kapuce" or (look == "default" and sp.cap_back)): continue
                        name = layer + ("." + look if look else "")
                        fn = (lambda cls, layer, look, pose, view: lambda b: V.draw(cls, layer, look, pose, view, b.w/2, FEET, H.S_HERO))(cls, layer, look, pose, view)
                        items.append((name, size, size, fn))
                out[f"{folder}/{cls}/{pose}{sfx}"] = items
    return out


def jobs():
    j = layer_jobs()
    j.update(view_jobs())
    j.update(layer_jobs(2.5, 600, ("idle",), "sprites/heroes_big"))
    return j


if __name__ == "__main__":
    import sys
    sys.modules["heroes_gear"] = sys.modules["__main__"]
    import heroes_new
    only_cls = [a for a in sys.argv[1:] if a in CLS]
    sys.argv = [a for a in sys.argv if a not in CLS]
    jj = jobs()
    if only_cls:
        jj = {k: v for k, v in jj.items() if any(f"/{c}/" in k for c in only_cls)}
    common.run(jj)
