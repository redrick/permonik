import math, zlib
import common
import style3
from common import FEET
from lib import Col, ell, bez, rrect
from style3 import C, T, stroke, shape, form, fill, hatch, tube, cast_shadow, dot, face, head_outline, clip_fill, LINE
from chars3 import Person
from heroes import (SKIN, SKIN_DK, IRON, IRON_LT, WOOD, WOOD_LT, BRASS, BONE, RED, LEATHER, BOOT, FLAME, GLOW, LEGS,
                    arm, hnd, boot, torso_pts, skirt_pts, head, neck, beard, moustache, kahan, portrait)
S = 0.5
MAN = dict(H=124, hr=10.8, hy=112, sh_y=97, sh_w=13, hip=57, knee=30.5, ankle=5, leg_w=(8, 6.2),
           arm_w=(7, 6.2), up=19.5, fo=17.5)
BURLY = dict(MAN, sh_w=15.5, leg_w=(9, 7.2), arm_w=(8.6, 7.6), up=19, fo=17.5)
WOMAN = dict(H=118, hr=10.4, hy=107, sh_y=93, sh_w=11.5, hip=55, knee=29.5, ankle=5, leg_w=(7, 5.4),
             arm_w=(6.2, 5.3), up=18, fo=16)
OLD = dict(MAN, hy=108, sh_y=93, hip=55, knee=29.5, sh_w=12)
GIRL = dict(H=100, hr=9.8, hy=89.8, sh_y=76, sh_w=9.6, hip=45, knee=24, ankle=5, leg_w=(6, 4.6),
            arm_w=(5.4, 4.6), up=15, fo=14)
SMALL = dict(H=62, hr=11, hy=48, sh_y=35, sh_w=8.5, hip=19, knee=10.5, ankle=3, leg_w=(5.6, 4.8),
             arm_w=(5.2, 4.6), up=9.5, fo=8.5)

COLD = Col(0.95, "#cfe8ff")
COLD_GLOW = Col(0.9, "#bfe0ff", alpha=0.2)
BARK = Col(0.42, "#86664a")
BARK_DK = Col(0.3, "#5e4532")
MOSS = Col(0.45, "#6f8448")
WHITE_HAIR = Col(0.88, "#e4e0d8")
GREY_LINE = Col(0.5, "#8d8a86")
CLAY = Col(0.5, "#a0663e")
GHOST = Col(0.82, "#bcd3e6")
GHOST_DK = Col(0.68, "#93b0c8")
GHOST_SKIN = Col(0.88, "#d6e4ef")
TALK_FAR = ("a", 128, 92)


# ------------------------------------------------------------------ props
def hammer(H, fa, ang=80, L=16, big=False):
    with T(H[0], H[1], 1, rot=ang):
        tube([(-5, 0), (L, 0)], 2.4, 2.2, WOOD, sh=0.1)
        hw, hh = (5.5, 9) if big else (4.2, 7)
        form([(L-hw/2, -hh/2), (L+hw/2, -hh/2), (L+hw/2, hh/2), (L-hw/2, hh/2)], IRON, sh=0.15)


def tongs(H, fa):
    with T(H[0], H[1], 1, rot=-80):
        for sg in (-1, 1):
            stroke([(-3, sg*0.6), (24, sg*1.6), (27, sg*0.4)], LINE*1.6, g=IRON)
        shape(rrect(24, -2.2, 6, 4.4, 1), Col(0.75, "#e0743a"), LINE*0.7)


def jug(H, fa, col=CLAY):
    x, y = H[0]+1, H[1]-6
    b = bez((x-4, y+3), (x-8, y), (x-7, y-9), (x, y-10)) + bez((x, y-10), (x+7, y-9), (x+8, y), (x+4, y+3))
    form(b + [(x+3, y+5), (x-3, y+5)], col, sh=0.15)
    stroke(bez((x+4, y+3), (x+9, y+4), (x+10, y-4), (x+6, y-5)), LINE*1.6)
    stroke([(x-3.4, y+2), (x+3.4, y+2)], LINE*0.6)


def mug(H, fa):
    x, y = H[0]+3, H[1]-1
    form(rrect(x-3.5, y-5, 7, 9, 1.2), Col(0.55, "#8f7a5e"), sh=0.15)
    stroke(ell(x+4.5, y-0.5, 2.2, 2.6, 12, -90, 90), LINE*1.2)
    shape(bez((x-4, y+4), (x-4.5, y+7), (x+4.5, y+7), (x+4, y+4)), Col(0.95, "#f2ecd8"), LINE*0.7)


def basket(H, fa):
    x, y = H[0], H[1]-4
    stroke(bez((x-8, y-4), (x-7, y+5), (x+7, y+5), (x+8, y-4)), LINE*1.8, g=WOOD_LT)
    for dx, col in ((-4, Col(0.45, "#6f8a4a")), (1, Col(0.55, "#8aa060")), (5, Col(0.6, "#b5a44c"))):
        shape(ell(x+dx, y-3, 3.4, 2.6, 12), col, LINE*0.6)
    b = [(x-9, y-4), (x+9, y-4), (x+7, y-14), (x-7, y-14)]
    form(b, WOOD_LT, sh=0.15)
    for k_ in range(-6, 8, 3): stroke([(x+k_, y-5), (x+k_*0.8, y-13)], LINE*0.45)
    stroke([(x-8.5, y-8), (x+8.5, y-8)], LINE*0.45)


def book(x, y, ang=0, col=Col(0.35, "#6a3b32"), w=12, h=15):
    with T(x, y, 1, rot=ang):
        form(rrect(-w/2, -h/2, w, h, 1), col, sh=0.15)
        shape([(w/2-1.6, -h/2+0.6), (w/2+0.6, -h/2+0.6), (w/2+0.6, h/2-0.6), (w/2-1.6, h/2-0.6)], Col(0.88, "#e8dcc0"), LINE*0.6)
        for yy in (-h*0.25, h*0.25): stroke([(-w/2+0.5, yy), (w/2-1.8, yy)], LINE*0.6, g=BRASS)


def pouch(x, y):
    p = bez((x-3.5, y), (x-6, y-3), (x-5.5, y-8), (x, y-8.5)) + bez((x, y-8.5), (x+5.5, y-8), (x+6, y-3), (x+3.5, y))
    form(p, Col(0.4, "#7a5a3a"), sh=0.15)
    stroke([(x-3.5, y-0.5), (x+3.5, y-0.5)], LINE*1.2, g=Col(0.6, "#b09060"))
    for i, (dx, dy) in enumerate(((-2, 0.8), (1.5, 1.0))): shape(ell(x+dx, y+dy, 1.8, 0.9, 12), Col(0.75, "#cfd2d6"), LINE*0.5)


def coin(H, fa):
    shape(ell(H[0]+2, H[1]+2.5, 2.2, 2.2, 14), Col(0.78, "#d6d8dc"), LINE*0.6)


def flask(H, fa):
    x, y = H[0]+1, H[1]+1
    shape(rrect(x-1, y+3, 2, 3.5, 0.5), Col(0.6, "#9a7a50"), LINE*0.6)
    b = bez((x-1.2, y+3), (x-1.2, y), (x-5, y-1), (x-5, y-5)) + bez((x-5, y-5), (x-5, y-9.5), (x+5, y-9.5), (x+5, y-5)) + \
        bez((x+5, y-5), (x+5, y-1), (x+1.2, y), (x+1.2, y+3))
    shape(b, Col(0.75, "#b9d0c8"), LINE*0.9)
    clip_fill(b, [(x-6, y-10), (x+6, y-10), (x+6, y-5), (x-6, y-5)], Col(0.5, "#7a9a4a"))


def teacup(x, y, col=Col(0.9, "#eef2f6")):
    shape(ell(x, y-4.4, 4.6, 1.1, 14), col, LINE*0.6)
    c = bez((x-4, y), (x-4, y-3), (x-2, y-4), (x, y-4)) + bez((x, y-4), (x+2, y-4), (x+4, y-3), (x+4, y)) + [(x+4, y), (x-4, y)]
    c = [(x-4, y)] + bez((x-4, y), (x-3.8, y-3.2), (x-2, y-4), (x, y-4)) + bez((x, y-4), (x+2, y-4), (x+3.8, y-3.2), (x+4, y))
    shape(c, col, LINE*0.8)
    stroke(ell(x+4.6, y-1.6, 1.5, 1.4, 10, -100, 100), LINE*0.8)
    stroke([(x-3.6, y-1.8), (x+3.6, y-1.8)], LINE*0.6, g=Col(0.5, "#5a7ab0"))


def pole(H, top=70, bot=None):
    x = H[0]
    tube([(x-1, bot if bot is not None else 2), (x+1.5, H[1]+top)], 2.6, 2.2, WOOD, sh=0.1)


def pipe(x, y, smoke=True):
    tube([(x, y), (x+5, y-1.2)], 1.2, 1.0, Col(0.3, "#4a3426"), LINE*0.6, sh=0)
    shape(rrect(x+4, y-1.6, 2.6, 3.6, 0.6), Col(0.3, "#4a3426"), LINE*0.6)
    if smoke:
        stroke(bez((x+5.5, y+2.5), (x+8, y+5), (x+4, y+8), (x+7, y+11)), LINE*0.7, g=Col(0.7, "#b0b0b8"), alpha=0.6)


def bag(k, col=Col(0.42, "#7a6a46")):
    stroke(bez((k.sh_w*0.7, k.sh_y+1.5), (2, 80), (-6, 70), (-12, 60)), LINE*2.4)
    stroke(bez((k.sh_w*0.7, k.sh_y+1.5), (2, 80), (-6, 70), (-12, 60)), LINE*1.1, g=LEATHER)
    form(rrect(-19, 50, 12, 11, 2.2), col, sh=0.15)
    shape(bez((-19, 61), (-19, 56), (-7, 56), (-7, 61)) + [(-19, 61)], col, LINE*0.7)


# ------------------------------------------------------------------ views and walks
POSES = tuple(p + v for v in ("", "_f", "_b") for p in ("idle", "talk", "walk1", "walk2", "walk3", "walk4"))
PHASE = {"walk1": "c1", "walk2": "p1", "walk3": "c2", "walk4": "p2"}
SWING = {"walk1": 1, "walk2": 0.25, "walk3": -1, "walk4": -0.25}
# cloth per frame (drift, flare): side drifts back as the figure moves on, front sways with the hips
CLOTH = {False: {"walk1": (-0.6, 2.4), "walk2": (-2.0, 0.6), "walk3": (-0.6, 2.4), "walk4": (-2.0, 0.6)},
         True: {"walk1": (0.8, 1.4), "walk2": (1.6, 0.4), "walk3": (-0.8, 1.4), "walk4": (-1.6, 0.4)}}
CX = {"side": 0.2, "front": 0.0, "back": 0.0}
STRIDE = 0.85

# copied from hero_views (front/back legs), kept here so the NPCs do not pull in the hero gear
LEGS_FB = {
    "stand": ((-5, -5.2, 0, -5.5, 0, 1.0), (5, 5.2, 0, 5.5, 0, 1.0)),
    "c1": ((-5, -5.0, 0.5, -4.8, 1.8, 0.92), (5, 5.6, -0.8, 6.0, -1.4, 1.08)),
    "p1": ((-5, -4.8, 0, -4.6, 0, 1.0), (5, 6.2, 6, 4.6, 7, 1.05)),
    "c2": ((-5, -5.6, -0.8, -6.0, -1.4, 1.08), (5, 5.0, 0.5, 4.8, 1.8, 0.92)),
    "p2": ((-5, -6.2, 6, -4.6, 7, 1.05), (5, 4.8, 0, 4.6, 0, 1.0)),
}


def split_pose(pose):
    for sfx, v in (("_f", "front"), ("_b", "back")):
        if pose.endswith(sfx): return pose[:-2], v
    return pose, "side"


def dk(col, f=0.72):
    h = col.hex.lstrip("#")
    return Col(col*f, "#" + "".join(f"{int(int(h[i:i+2], 16)*f):02x}" for i in (0, 2, 4)))


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


def ears(k, skin=SKIN):
    r = k.hr; cy = k.hy
    for sx in (-1, 1): shape(ell(sx*r*0.97, cy-r*0.05, r*0.2, r*0.3, 14), skin, LINE*0.8)


def legs_s(k, phase, trousers, boots, boot_h=7, wk=1.0, kx=1.0):
    ls = min(1.0, k.hip/56)
    out = [([(hx*kx, k.hip), (kxx*kx, k.knee+kdy*ls), (axx*kx, k.ankle+lift*ls)], lift*ls, frot)
           for hx, kxx, kdy, axx, lift, frot in LEGS[phase]]
    for pts, _, _ in out: tube(pts, k.leg_w[0], k.leg_w[1], trousers)
    for pts, lift, frot in out: boot(pts[-1][0], lift, k.ankle, k.ankle+boot_h, boots, frot, wk)


def legs_v(k, phase, trousers, boots, boot_h, back, kx=1.0, bw=1.0):
    ls = min(1.0, k.hip/56)
    for hx, kxx, kdy, ax, lift, sc in sorted(LEGS_FB[phase], key=lambda l: l[5]):
        tube([(hx*kx, k.hip), (kxx*kx, k.knee+kdy*ls), (ax*kx, k.ankle+lift*ls)], k.leg_w[0], k.leg_w[1]*sc, trousers)
        boot_fb(ax*kx, lift*ls, (k.ankle+boot_h)/bw, boots, sc*bw, back)


def legs_any(k, base, view, o, trousers, boots, boot_h, wk=1.0, kx=1.0, bw=1.0):
    walk = base in PHASE and not o.get("glide")
    if view == "side":
        legs_s(k, PHASE[base] if walk else o.get("legs", "stand"), trousers, boots, boot_h, wk, kx*(STRIDE if walk else 1))
    else:
        legs_v(k, PHASE[base] if walk else "stand", trousers, boots, boot_h, view == "back", kx, bw)


def sway(pts, dx, fl, top, bot, w):
    if not (dx or fl) or top <= bot: return pts
    out = []
    for x, y in pts:
        t = max(0.0, min(1.0, (top-y)/(top-bot)))**1.3
        out.append((x + (dx + fl*x/w)*t, y))
    return out


def walk_arm(sp, side, sw, amt, view):
    if not sw or not amt: return sp
    f = -side*sw
    if view == "side":
        if sp[0] == "a":
            d = f*16*amt
            return ("a", sp[1]+d, sp[2]+d*(1.7 if d > 0 else 0.6))
        return ("k", sp[1]+f*3*amt, sp[2]+abs(f)*0.8*amt, sp[3])
    if sp[0] == "a": return ("a", sp[1]+f*6*amt, sp[2]+f*6*amt)
    fw, bk = max(f, 0)*amt, max(-f, 0)*amt
    return ("k", sp[1]-side*(2.5*fw - bk), sp[2]+5.5*fw+bk, sp[3])


def arm_spec(k, o, side, base, view):
    """-> (arm spec, talking)"""
    nm = "near" if side > 0 else "far"
    talk = base == "talk" and (o.get("both_talk") or (side < 0) == bool(o.get("far_talks")))
    L = k.up + k.fo
    if view == "side":
        if talk: sp = o.get(nm+"_talk", TALK_FAR if side < 0 else ("a", -40, 30))
        else: sp = o.get(nm, ("a", -82, -92) if side > 0 else ("a", -98, -86))
    else:
        if talk: sp = o.get(nm+"_talk_f", ("k", side*(k.sh_w+L*0.2), k.sh_y-L*0.55, -side))
        else: sp = o.get(nm+"_f", ("k", side*(k.sh_w+L*0.26+o.get("arm_out", 0)), k.sh_y-L*0.93, -side))
    amt = o.get(nm+"_swing", 0.25 if o.get(nm+"_item") else 1.0)
    return walk_arm(sp, side, SWING.get(base, 0), amt, view), talk


def coat_back(k, hem, col):
    d = dk(col)
    stroke(bez((0, k.sh_y+1.5), (0.4, (k.sh_y+hem)/2+10), (-0.4, (k.sh_y+hem)/2-5), (0, hem+1)), LINE*0.6, g=d)
    shape(bez((-6, k.sh_y+2.6), (-3, k.sh_y-0.5), (3, k.sh_y-0.5), (6, k.sh_y+2.6)) + [(0, k.sh_y+3.2)], d, LINE*0.7)


def apron_back(k, col, top, w, bib):
    y = min(top, k.hip+8)
    shape([(-w-1, y-1.3), (w+1, y-1.3), (w+1, y+1.3), (-w-1, y+1.3)], col, LINE*0.6)
    for sx in (-1, 1):
        shape(bez((0, y), (sx*2, y+3.6), (sx*5, y+3.2), (sx*4.6, y)) + bez((sx*4.6, y), (sx*4.4, y-2.4), (sx*2, y-2.4), (0, y)), col, LINE*0.6)
        shape([(sx*0.4, y-0.5), (sx*1.6, y-1), (sx*(2.8+sx*0.3), y-10), (sx*(1.2+sx*0.3), y-10.5)], col, LINE*0.6)
    shape(ell(0, y, 1.3, 1.5, 10), col, LINE*0.6)
    if bib:
        for sx in (-1, 1): stroke([(sx*(k.sh_w-3), k.sh_y+1.5), (-sx*w*0.55, y+1.5)], LINE*1.6, g=col)


# ------------------------------------------------------------------ hair & hats
def hair_cap(k, col, part=0.15, dark=None, low=-0.2, v="side"):
    r = k.hr; cy = k.hy
    if v == "back":
        form(head_outline(k), col, sdx=0, sdy=0.6, sh=0.1)
        for xx in (-0.55, -0.2, 0.2, 0.55):
            stroke(bez((r*xx*0.5, cy+r*0.92), (r*xx*1.1, cy+r*0.5), (r*xx*1.2, cy), (r*xx*1.1, cy+r*(low-0.55))), LINE*0.4, g=dark or dk(col))
        return
    if v == "front": part = 0
    h = bez((-r*1.04, cy+r*low), (-r*1.18, cy+r*1.25), (r*1.18, cy+r*1.25), (r*1.04, cy+r*low+0.1*r)) + \
        bez((r*1.04, cy+r*(low+0.1)), (r*0.95, cy+r*0.45), (r*0.65, cy+r*0.6), (r*part, cy+r*0.68)) + \
        bez((r*part, cy+r*0.68), (-r*0.4, cy+r*0.6), (-r*0.9, cy+r*0.4), (-r*1.04, cy+r*low))
    form(h, col, sdx=-1 if v == "side" else 0, sdy=0.6, sh=0.1)


def long_back(k, col, length=3.2, w=1.25, v="side"):
    r = k.hr; cy = k.hy
    b = bez((-r*1.0, cy+r*0.4), (-r*w*1.1, cy-r*0.8), (-r*w*1.15, cy-r*length*0.7), (-r*w, cy-r*length)) + \
        [(-r*0.4, cy-r*length-1), (r*0.4, cy-r*length-1)] + \
        bez((r*w, cy-r*length), (r*w*1.15, cy-r*length*0.7), (r*w*1.1, cy-r*0.8), (r*1.0, cy+r*0.4))
    p = getattr(k, "pose", "")
    if p in CLOTH[False]:
        dx, fl = CLOTH[v != "side"][p]
        b = sway(b, dx*1.3, fl*0.4, cy, cy-r*length, r*w)
    form(b, col, sdx=-1.4 if v == "side" else 0, sh=0.1)
    if v == "back":
        for xx in (-0.7, -0.3, 0.1, 0.5, 0.85):
            stroke(bez((r*xx, cy-r*0.2), (r*xx*1.05, cy-r*length*0.4), (r*xx*0.95, cy-r*length*0.7), (r*xx, cy-r*length+0.5)), LINE*0.4, g=dk(col))


def bun(k, col, v="side"):
    r = k.hr; cy = k.hy
    x, y = {"side": (-r*0.75, cy+r*0.7), "front": (0, cy+r*1.02), "back": (0, cy+r*0.35)}[v]
    shape(ell(x, y, r*0.42, r*0.4, 18), col)
    stroke(ell(x, y, r*0.2, r*0.18, 10, 20, 300), LINE*0.5)


def scarf(k, col, knot=True, line=None, v="side"):
    r = k.hr; cy = k.hy
    if v == "back":
        s = bez((-r*1.1, cy-r*0.45), (-r*1.22, cy+r*1.3), (r*1.22, cy+r*1.3), (r*1.1, cy-r*0.45)) + \
            bez((r*1.1, cy-r*0.45), (r*0.6, cy-r*0.75), (-r*0.6, cy-r*0.75), (-r*1.1, cy-r*0.45))
        form(s, col, sdx=0, sdy=0.6, sh=0.12)
        for sx in (-1, 1):
            shape([(sx*r*0.1, cy-r*0.6), (sx*r*0.75, cy-r*1.55), (sx*r*0.4, cy-r*1.75), (-sx*r*0.05, cy-r*0.75)], col, LINE*0.8)
        shape(ell(0, cy-r*0.62, r*0.24, r*0.2, 12), col, LINE*0.8)
        if line is not None:
            for (dx, dy) in ((-0.5, 1.0), (0.1, 1.15), (0.6, 0.95), (-0.8, 0.4), (0.9, 0.35), (-0.3, 0.3), (0.35, 0.45), (0, -0.2)):
                dot(r*dx, cy+r*dy, r*0.08, line)
        return
    if knot and v == "side":
        shape([(-r*0.85, cy-r*0.55), (-r*1.6, cy-r*1.4), (-r*1.25, cy-r*1.6), (-r*0.6, cy-r*0.8)], col, LINE*0.8)
        shape([(-r*0.7, cy-r*0.6), (-r*1.0, cy-r*1.7), (-r*0.65, cy-r*1.75), (-r*0.45, cy-r*0.75)], col, LINE*0.8)
    if v == "front":
        s = bez((-r*1.14, cy-r*0.45), (-r*1.32, cy+r*1.48), (r*1.32, cy+r*1.48), (r*1.14, cy-r*0.45)) + \
            bez((r*1.14, cy-r*0.45), (r*0.98, cy+r*0.4), (r*0.6, cy+r*0.62), (0, cy+r*0.64)) + \
            bez((0, cy+r*0.64), (-r*0.6, cy+r*0.62), (-r*0.98, cy+r*0.4), (-r*1.14, cy-r*0.45))
        dots = ((-0.6, 1.05), (0, 1.15), (0.6, 1.05), (-1.0, 0.4), (1.0, 0.4))
    else:
        s = bez((-r*1.12, cy-r*0.45), (-r*1.3, cy+r*1.45), (r*1.3, cy+r*1.45), (r*1.12, cy-r*0.1)) + \
            bez((r*1.12, cy-r*0.1), (r*0.9, cy+r*0.55), (r*0.5, cy+r*0.62), (r*0.1, cy+r*0.62)) + \
            bez((r*0.1, cy+r*0.62), (-r*0.4, cy+r*0.62), (-r*0.9, cy+r*0.3), (-r*0.95, cy-r*0.45))
        dots = ((-0.5, 1.0), (0.1, 1.15), (0.6, 0.95), (-0.8, 0.4), (0.9, 0.35))
    form(s, col, sdx=-1 if v == "side" else 0, sdy=0.6, sh=0.12)
    if line is not None:
        for (dx, dy) in dots: dot(r*dx, cy+r*dy, r*0.08, line)


def bald(k, col, v="side"):
    r = k.hr; cy = k.hy
    if v == "back":
        band = bez((-r*1.1, cy+r*0.5), (-r*0.5, cy+r*0.15), (r*0.5, cy+r*0.15), (r*1.1, cy+r*0.5)) + \
            [(r*1.1, cy-r*1.2), (-r*1.1, cy-r*1.2)]
        clip_fill(head_outline(k), band, col)
        stroke(head_outline(k), LINE, closed=True)
        for xx in (-0.6, -0.2, 0.2, 0.6):
            stroke([(r*xx, cy+r*0.12), (r*xx*1.05, cy-r*0.85)], LINE*0.4, g=dk(col, 0.85))
        stroke(bez((-r*0.3, cy+r*0.7), (-r*0.1, cy+r*0.76), (r*0.1, cy+r*0.76), (r*0.3, cy+r*0.7)), LINE*0.45)
        return
    shape(bez((-r*0.98, cy+r*0.45), (-r*1.1, cy+r*0.1), (-r*1.02, cy-r*0.2), (-r*0.85, cy-r*0.35)) + [(-r*0.7, cy+r*0.45)], col, LINE*0.7)
    shape(bez((r*0.98, cy+r*0.4), (r*1.06, cy+r*0.1), (r*1.02, cy-r*0.2), (r*0.92, cy-r*0.3)) + [(r*0.85, cy+r*0.4)], col, LINE*0.7)
    stroke(bez((-r*0.3, cy+r*0.85), (-r*0.1, cy+r*0.9), (r*0.1, cy+r*0.9), (r*0.3, cy+r*0.85)), LINE*0.5)


def nape(k, col):
    """hair seen from behind below a hat"""
    r = k.hr; cy = k.hy
    form(head_outline(k), col, sdx=0, sdy=0.6, sh=0.1)
    for xx in (-0.55, -0.2, 0.2, 0.55):
        stroke([(r*xx, cy+r*0.3), (r*xx*1.05, cy-r*0.8)], LINE*0.4, g=dk(col, 0.85))


def beard_back(k, col, skin, L=1.3):
    """the beard showing past the jaw from behind; redraws the head over it"""
    r = k.hr; cy = k.hy; f = L/1.25
    for sx in (-1, 1):
        shape(bez((sx*r*0.7, cy-r*0.5), (sx*r*1.08, cy-r*0.7*f), (sx*r*0.95, cy-r*1.2*f), (sx*r*0.4, cy-r*1.3*f)) +
              [(sx*r*0.3, cy-r*0.8)], col, LINE*0.7)
    shape(head_outline(k), skin)


def wrinkles(k, dx=0.2):
    r = k.hr; cy = k.hy; c = r*dx
    for sx in (-1, 1):
        stroke([(c+sx*r*0.6, cy-r*0.02), (c+sx*r*0.75, cy-r*0.1)], LINE*0.5)
    stroke(bez((c-r*0.25, cy+r*0.55), (c, cy+r*0.6), (c+r*0.25, cy+r*0.55), (c+r*0.3, cy+r*0.52)), LINE*0.45)


def specs(k, dx=0.2):
    r = k.hr; cy = k.hy; c = r*dx
    for sx in (-1, 1):
        stroke(ell(c+sx*r*0.38, cy+r*0.02, r*0.22, r*0.19, 24), LINE*0.8, closed=True)
    stroke([(c-r*0.16, cy+r*0.04), (c+r*0.16, cy+r*0.04)], LINE*0.7)


def soot(k, dx=0.2):
    r = k.hr; cy = k.hy; c = r*dx
    for (x_, y_, rr) in ((-0.55, -0.2, 0.16), (0.6, -0.35, 0.12), (0.2, 0.6, 0.14), (-0.3, -0.6, 0.1)):
        fill(ell(c+r*x_, cy+r*y_, r*rr*1.4, r*rr, 12), Col(0.2, "#2e2a2a", alpha=0.35))


# ------------------------------------------------------------------ generic body
def npc_head(k, md, skin, o, view):
    nw = o.get("neck_w", 2.8)
    style3._R.seed(zlib.crc32(f"{getattr(o.get('head'), '__name__', 'npc')}{view}".encode()))
    if view == "side":
        head(k, md, skin, ear=o.get("ear", True), neck_w=nw, do_face=not o.get("face_late"))
    else:
        neck(k, skin, nw)
        if o.get("ear", True): ears(k, skin)
        shape(head_outline(k), skin)
        if view == "front" and not o.get("face_late"): face(0, k.hy, k.hr*0.95, md)
    if view == "back" and o.get("hair_back"): o["hair_back"](k, view)
    if o.get("head"): o["head"](k, md, view)


def npc_body(k, pose, o, view="side"):
    talk = pose == "talk"
    md = o.get("talk_mood", "talk") if talk else o.get("mood", "think")
    skin = o.get("skin", SKIN)
    sleeve = o.get("sleeve", o.get("coat"))
    fb = view != "side"; bk = view == "back"
    k.pose = pose
    sd = 0 if fb else -2.2
    cdx, fl = CLOTH[fb].get(pose, (0, 0))
    if o.get("back"): o["back"](k, view)
    if o.get("hair_back") and not bk: o["hair_back"](k, view)

    def limb(side):
        nm = "near" if side > 0 else "far"
        sp, op = arm_spec(k, o, side, pose, view)
        H, fa = arm(k, side, sp, sleeve, skin, rolled=o.get("rolled", False), hand=False, cuff=o.get("cuff"))
        item = o.get(nm+"_item")
        if item: item(H, fa)
        hnd(H[0], H[1], fa, 2.4, skin, open_=op and not (side > 0 and item))
        if side > 0 and o.get("after_hand"): o["after_hand"](H, fa)

    limb(-1)
    inside = bk and o.get("near_inside")
    if inside: limb(1)
    legs_any(k, pose, view, o, o.get("trousers", Col(0.45, "#5f584e")), o.get("boots", BOOT), o.get("boot_h", 7),
             o.get("wk", 1.0), o.get("kx", 1.0))
    if o.get("skirt"):
        col, top, hem_y, w0, w1 = o["skirt"]
        sk = sway(skirt_pts(top, w0, hem_y, -w1, w1), cdx, fl, top-4, hem_y, w1)
        form(sk, col, sdx=sd, sdy=1, sh=0.14)
        for xx in (-0.6, -0.2, 0.25, 0.65):
            fold = bez((xx*w0, top-3), (xx*w1*0.9, (top+hem_y)/2), (xx*w1, hem_y+6), (xx*w1*1.05, hem_y+1.5))
            stroke(sway(fold, cdx, fl, top-4, hem_y, w1), LINE*0.45, g=o.get("fold", Col(0.3, "#3a3434")))
    if o.get("coat"):
        hem = o.get("hem", 56)
        tors = torso_pts(k, hem, o.get("hem_w", k.sh_w+3), waist_w=o.get("waist_w"), collar=o.get("collar", 4.5))
        if hem < k.hip-10: tors = sway(tors, cdx, fl, k.hip, hem, o.get("hem_w", k.sh_w+3))
        form(tors, o["coat"], sdx=sd, sdy=1.2, sh=0.13)
        if bk: coat_back(k, hem, o["coat"])
        if o.get("coat_detail"): o["coat_detail"](k, tors, view)
    if o.get("apron"):
        col, top, bot, w = o["apron"]
        if bk:
            apron_back(k, col, top, w, o.get("bib"))
        else:
            ap = [(-w*0.85, top), (w*0.85, top)] + bez((w*0.85, top), (w, (top+bot)/2), (w*1.05, bot+8), (w, bot)) + \
                bez((w, bot), (w*0.3, bot-1), (-w*0.3, bot-1), (-w, bot)) + bez((-w, bot), (-w*1.05, bot+8), (-w, (top+bot)/2), (-w*0.85, top))
            form(sway(ap, cdx*0.7, fl*0.5, min(top, k.hip), bot, w), col, sdx=sd*0.7, sdy=0.8, sh=0.1)
            if o.get("bib"):
                bt = o["bib"]
                form([(-w*0.5, top), (w*0.5, top), (w*0.45, bt), (-w*0.45, bt)], col, sh=0.08)
                for sx in (-1, 1): stroke([(sx*w*0.45, bt), (sx*(k.sh_w-3), k.sh_y+1.5)], LINE*1.6, g=col)
    if o.get("belt"):
        col, y = o["belt"]; w = o.get("belt_w", k.sh_w+2.5)
        shape([(-w, y-2), (w, y-2), (w+0.2, y+2), (-w-0.2, y+2)], col, LINE*0.8)
    if o.get("front"): o["front"](k, view)
    if not inside: limb(1)
    npc_head(k, md, skin, o, view)


def npc(o, Kd, shadow_rx=16, shadow=True, alpha=None):
    def draw(x, y, s, pose="idle"):
        base, view = split_pose(pose)
        k = Person(**Kd)
        if shadow and pose != "portrait": cast_shadow(x, y, shadow_rx*s, 3*s)
        C.saveState()
        if alpha: C.setFillAlpha(alpha); C.setStrokeAlpha(alpha)
        with T(x, y, s):
            if view == "back": C.scale(-1, 1)
            npc_body(k, base, o, view)
        C.restoreState()
    draw.K = Kd
    draw.poses = POSES
    return draw


def late_face(dx=0.2):
    def f(k, md, v="side"):
        if v != "back": face(k.hr*CX[v], k.hy, k.hr*0.95, md)
    return f


def chain(*fns):
    def f(*a):
        for fn in fns: fn(*a)
    return f


# ------------------------------------------------------------------ Permoník
PM_SMOCK = Col(0.88, "#e6e0d2")
PM_SMOCK_DK = Col(0.72, "#bdb5a2")
PM_CAP = Col(0.38, "#a83a30")
PM_O = dict(far_talks=True, far_talk=("a", 130, 100), far=("a", -110, -95), near=("a", -30, 10), near_item=True,
            near_f=("k", 12.5, 20, -1), neck_w=2.4, face_late=True)


def permonik_draw(mood_idle="happy"):
    def draw(x, y, s, pose="idle"):
        base, v = split_pose(pose)
        k = Person(**SMALL)
        talk = base == "talk"
        md = "talk" if talk else mood_idle
        fb = v != "side"; bk = v == "back"
        sd = 0 if fb else -1.8
        c = CX[v]
        with T(x, y, s):
            if bk: C.scale(-1, 1)
            r = k.hr; cy = k.hy
            if not fb:
                flek = [(-9.5, 22)] + bez((-9.5, 22), (-12, 16), (-12, 11), (-10.5, 8)) + [(-4, 9), (-3, 21)]
                form(flek, LEATHER, sh=0.15)
            sp, op = arm_spec(k, PM_O, -1, base, v)
            H, fa = arm(k, -1, sp, PM_SMOCK, hand=False, hr=2.3)
            hnd(H[0], H[1], fa, 2.3, open_=op)
            legs_any(k, base, v, PM_O, PM_SMOCK_DK, BOOT, 5, 0.85, 0.8, 0.8)
            tors = torso_pts(k, 11, 12, waist_w=11.5, collar=3)
            form(tors, PM_SMOCK, sdx=sd, sdy=1, sh=0.14)
            if bk: coat_back(k, 11, PM_SMOCK_DK)
            shape([(-11.6, 19), (11.6, 19), (11.8, 22.5), (-11.8, 22.5)], LEATHER, LINE*0.8)
            if bk:
                f = [(-8, 21)] + bez((-8, 21), (-9.5, 16), (-9.5, 11), (-8.5, 7)) + bez((-8.5, 7), (-3, 6), (3, 6), (8.5, 7)) + \
                    bez((8.5, 7), (9.5, 11), (9.5, 16), (8, 21))
                form(f, LEATHER, sdx=0, sdy=1, sh=0.16)
            else:
                shape(rrect(1 if not fb else -1.7, 18.5, 3.4, 4.6, 0.5), BRASS, LINE*0.6)
            sp, _ = arm_spec(k, PM_O, 1, base, v)
            H, fa = arm(k, 1, sp, PM_SMOCK, hand=False, hr=2.3)
            kahan(H[0]+0.5, H[1]-0.5, 1.0, COLD, COLD_GLOW, Col(0.55, "#8a8f98"))
            hnd(H[0], H[1], fa, 2.3)
            if bk:
                npc_head(k, md, SKIN, PM_O, v)
                beard_back(k, WHITE_HAIR, SKIN, 1.6)
                nape(k, WHITE_HAIR)
            else:
                npc_head(k, md, SKIN, PM_O, v)
                t = r*(c+0.05)
                bd = bez((-r*0.95, cy-r*0.15), (-r*1.05, cy-r*1.6), (t-r*0.75, cy-r*2.4), (t, cy-r*2.5)) + \
                    bez((t, cy-r*2.5), (t+r*0.55, cy-r*2.2), (r*1.1-r*(0.2-c)*0.5, cy-r*1.2), (r*0.95, cy-r*0.15)) + \
                    bez((r*0.95, cy-r*0.15), (r*0.7, cy-r*0.5), (r*(c+0.25), cy-r*0.48), (r*(c+0.1), cy-r*0.5)) + \
                    bez((r*(c+0.1), cy-r*0.5), (r*(c-0.3), cy-r*0.48), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.15))
                form(bd, WHITE_HAIR, sdx=-1 if not fb else 0, sdy=0.5, sh=0.08)
                for xx in (-0.5, -0.1, 0.3, 0.65):
                    xx += c - 0.2 if fb else 0
                    stroke(bez((r*xx, cy-r*0.8), (r*xx*1.05, cy-r*1.3), (r*xx, cy-r*1.8), (r*xx*0.8, cy-r*2.2)), LINE*0.45, g=GREY_LINE)
                face(r*c, cy, r*0.95, md)
                wrinkles(k, c)
                moustache(k, WHITE_HAIR, dx=c, w=0.6)
                if md == "grin":
                    cc = r*c
                    sm = bez((cc-r*0.45, cy-r*0.58), (cc-r*0.15, cy-r*0.98), (cc+r*0.3, cy-r*0.95), (cc+r*0.6, cy-r*0.5)) + \
                        bez((cc+r*0.6, cy-r*0.5), (cc+r*0.25, cy-r*0.72), (cc-r*0.15, cy-r*0.74), (cc-r*0.45, cy-r*0.58))
                    if fb:
                        sm = bez((cc-r*0.55, cy-r*0.52), (cc-r*0.25, cy-r*0.98), (cc+r*0.25, cy-r*0.98), (cc+r*0.55, cy-r*0.52)) + \
                            bez((cc+r*0.55, cy-r*0.52), (cc+r*0.2, cy-r*0.72), (cc-r*0.2, cy-r*0.72), (cc-r*0.55, cy-r*0.52))
                    shape(sm, Col(0.25, "#5a2228"), LINE*0.7)
                    stroke(bez((cc-r*0.4, cy-r*0.62), (cc-r*0.15, cy-r*0.76), (cc+r*0.15, cy-r*0.76), (cc+r*0.4, cy-r*0.62)), LINE*0.9, g=Col(0.95, "#f4efe0"))
                if md == "talk":
                    shape(ell(r*c, cy-r*0.72, r*0.14, r*0.1, 12), Col(0.25, "#6a2a30"), LINE*0.6)
                shape(ell(r*(c+0.05), cy-r*0.12, r*0.2, r*0.16, 12), Col(0.75, "#e0a890"), LINE*0.6)
            cap = bez((-r*1.08, cy+r*0.35), (-r*1.3, cy+r*1.4), (-r*1.4, cy+r*2.2), (-r*2.4, cy+r*1.8)) + \
                bez((-r*2.4, cy+r*1.8), (-r*1.6, cy+r*2.7), (r*0.6, cy+r*2.0), (r*1.08, cy+r*0.4)) + \
                bez((r*1.08, cy+r*0.4), (r*0.4, cy+r*0.55), (-r*0.4, cy+r*0.55), (-r*1.08, cy+r*0.35))
            form(cap, PM_CAP, sdx=-1.4 if not fb else 0, sdy=1, sh=0.15)
            shape(ell(-r*2.45, cy+r*1.75, r*0.28, r*0.28, 14), WHITE_HAIR, LINE*0.7)
            if bk:
                shape(bez((-r*1.15, cy+r*0.15), (-r*0.4, cy+r*0.3), (r*0.4, cy+r*0.3), (r*1.15, cy+r*0.15)) +
                      bez((r*1.15, cy+r*0.15), (r*1.15, cy+r*0.55), (r*0.4, cy+r*0.68), (-r*1.15, cy+r*0.55)), PM_SMOCK, LINE*0.8)
            else:
                shape(bez((-r*1.15, cy+r*0.15), (-r*0.4, cy+r*0.42), (r*0.4, cy+r*0.42), (r*1.15, cy+r*0.2)) +
                      bez((r*1.15, cy+r*0.2), (r*1.15, cy+r*0.55), (r*0.4, cy+r*0.78), (-r*1.15, cy+r*0.55)), PM_SMOCK, LINE*0.8)
    draw.K = SMALL
    draw.poses = POSES
    return draw


permonik = permonik_draw("happy")
permonik_grin = permonik_draw("grin")


# ------------------------------------------------------------------ townsfolk
def kosmas_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        beard_back(k, WHITE_HAIR, SKIN, 1.45)
        bald(k, WHITE_HAIR, v)
        return
    bald(k, WHITE_HAIR)
    beard(k, WHITE_HAIR, 1.45, GREY_LINE, dx=c/2)
    face(r*c, cy, r*0.95, md)
    moustache(k, WHITE_HAIR, dx=c)
    wrinkles(k, c); specs(k, c)


def kosmas_book(k, v="side"):
    if v == "side": book(9, 70, -12, Col(0.35, "#5a3a30"), 13, 17)
    elif v == "front": book(3, 69, -6, Col(0.35, "#5a3a30"), 13, 17)


kosmas = npc(dict(coat=Col(0.38, "#5a4a5e"), hem=6, hem_w=17, waist_w=15, sleeve=Col(0.38, "#5a4a5e"),
                  belt=(Col(0.6, "#a8946c"), 60), front=kosmas_book, near=("a", -100, -40), far_talks=True,
                  near_f=("k", 6, 68, -1), near_swing=0, near_inside=True,
                  cuff=Col(0.45, "#4a3d4e"), head=kosmas_head, face_late=True, boot_h=5), OLD)

HN_HAIR = Col(0.22, "#3a2c26")


def hnevek_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        beard_back(k, HN_HAIR, SKIN, 1.6)
        bald(k, HN_HAIR, v)
        return
    bald(k, HN_HAIR)
    beard(k, HN_HAIR, 1.6, dx=c/2)
    face(r*c, cy, r*0.95, md)
    moustache(k, HN_HAIR, dx=c)
    for sx in (-1, 1): shape(ell(r*c+sx*r*0.38, cy+r*0.32, r*0.24, r*0.08, 10), HN_HAIR, LINE*0.5)


kovar_hnevek = npc(dict(coat=Col(0.5, "#7a6e60"), hem=56, hem_w=17, waist_w=17, rolled=True, trousers=Col(0.35, "#4e4a44"),
                        apron=(LEATHER, 80, 30, 14), bib=93, near=("a", -80, -70), near_item=lambda H, fa: hammer(H, fa, 75, 17, True),
                        far_talks=True, head=hnevek_head, face_late=True, wk=1.15, boot_h=8, neck_w=4, arm_out=2), BURLY, 19)


DOROTA_SCARF = Col(0.48, "#9a6a3a")


def dorota_head(k, md, v="side"):
    scarf(k, DOROTA_SCARF, line=Col(0.8, "#d9c8a0"), v=v)
    if v != "back": wrinkles(k, CX[v])


korenarka_dorota = npc(dict(coat=Col(0.6, "#9c8f76"), hem=58, hem_w=13, waist_w=11.5, sleeve=Col(0.6, "#9c8f76"),
                            skirt=(Col(0.38, "#5e5444"), 60, 6, 13, 18), apron=(Col(0.66, "#a8a090"), 61, 18, 11),
                            near=("a", -95, -80), near_item=basket, far_talks=True, mood="happy", head=dorota_head, boot_h=5,
                            arm_out=2), WOMAN)

BARA_HAIR = Col(0.42, "#7a4f2e")


def bara_head(k, md, v="side"):
    hair_cap(k, BARA_HAIR, v=v)
    if v == "back": bun(k, BARA_HAIR, v)


senkyrka_bara = npc(dict(coat=Col(0.82, "#d6ccb6"), hem=60, hem_w=13, waist_w=12, rolled=True,
                         skirt=(Col(0.36, "#6a3a36"), 62, 6, 13, 19), apron=(Col(0.85, "#ddd6c4"), 63, 16, 12),
                         front=lambda k, v: shape([(-11, 62), (11, 62), (10, 80), (-10, 80)], Col(0.3, "#4a3a3a")),
                         belt=(Col(0.3, "#4a3a3a"), 63), belt_w=12.5,
                         near=("a", -88, -70), near_item=jug, far_talks=True, mood="happy",
                         hair_back=lambda k, v: bun(k, BARA_HAIR, v) if v != "back" else None,
                         head=bara_head, boot_h=5, arm_out=2), dict(WOMAN, sh_w=12.5))

VOJ_HAIR = Col(0.3, "#4e3626")


def vojtech_head(k, md, v="side"):
    r = k.hr; cy = k.hy
    h = [(-r*1.04, cy-r*0.1), (-r*1.2, cy+r*0.6), (-r*0.9, cy+r*1.2), (-r*0.3, cy+r*1.35), (r*0.2, cy+r*1.4),
         (r*0.8, cy+r*1.2), (r*1.15, cy+r*0.7), (r*1.04, cy+r*0.1), (r*0.85, cy+r*0.55), (r*0.55, cy+r*0.45),
         (r*0.35, cy+r*0.7), (r*0.05, cy+r*0.5), (-r*0.3, cy+r*0.68), (-r*0.6, cy+r*0.45), (-r*0.85, cy+r*0.55)]
    shape(h, VOJ_HAIR)
    if v == "back":
        clip_fill(head_outline(k), [(-r*1.3, cy-r*0.55)] + bez((-r*1.3, cy-r*0.55), (-r*0.5, cy-r*0.35), (r*0.5, cy-r*0.35), (r*1.3, cy-r*0.55)) +
                  [(r*1.3, cy+r*0.8), (-r*1.3, cy+r*0.8)], VOJ_HAIR)
        stroke(head_outline(k), LINE, closed=True)
        for xx in (-0.5, -0.15, 0.2, 0.5):
            stroke(bez((r*xx, cy+r*0.9), (r*xx*1.2, cy+r*0.4), (r*xx, cy-r*0.1), (r*xx*1.1, cy-r*0.4)), LINE*0.4, g=dk(VOJ_HAIR, 0.7))
        return
    soot(k, CX[v])


kovar_vojtech = npc(dict(coat=Col(0.55, "#8a8070"), hem=56, hem_w=15, waist_w=14, rolled=True, trousers=Col(0.38, "#55504a"),
                         apron=(Col(0.36, "#6a4a34"), 78, 28, 13), bib=90,
                         near=("a", -82, -86), near_item=tongs, far_talks=True, head=vojtech_head, wk=1.1, boot_h=8, arm_out=1), MAN)


MED_HAIR = Col(0.72, "#c8a86a")


def medulina_head(k, md, v="side"):
    r = k.hr; cy = k.hy
    hair_cap(k, MED_HAIR, v=v)
    for i, (a, col) in enumerate(((150, Col(0.85, "#e8e0f0")), (115, Col(0.7, "#d8a0b8")), (80, Col(0.8, "#f0d070")),
                                   (45, Col(0.7, "#a0b8e0")), (20, Col(0.85, "#e8e0f0")))):
        if v != "side": a = 160 - i*35
        fx, fy = math.cos(math.radians(a))*r*1.05, cy+r*0.15+math.sin(math.radians(a))*r*1.0
        for j in range(5):
            b_ = math.radians(j*72)
            shape(ell(fx+math.cos(b_)*1.3, fy+math.sin(b_)*1.3, 1.1, 1.1, 8), col, LINE*0.4)
        dot(fx, fy, 0.8, Col(0.7, "#d0a030"))


def flower(H, fa):
    stroke([(H[0]+1, H[1]+1), (H[0]+3, H[1]+10)], LINE*0.9, g=MOSS)
    for j in range(5):
        b_ = math.radians(j*72)
        shape(ell(H[0]+3+math.cos(b_)*1.5, H[1]+11.5+math.sin(b_)*1.5, 1.3, 1.3, 8), Col(0.85, "#e8e0f0"), LINE*0.4)
    dot(H[0]+3, H[1]+11.5, 0.9, Col(0.7, "#d0a030"))


korenarka_medulina = npc(dict(coat=Col(0.8, "#d8d0b8"), hem=58, hem_w=12.5, waist_w=11, sleeve=Col(0.8, "#d8d0b8"),
                              skirt=(Col(0.45, "#5f7450"), 60, 5, 12.5, 18), belt=(Col(0.45, "#5f7450"), 60), belt_w=12,
                              front=lambda k, v: form([(-10, 60), (10, 60), (11, 80), (5, 88), (-5, 88), (-11, 80)], Col(0.45, "#5f7450"), sh=0.1),
                              near=("a", -60, 20), near_f=("k", 20, 64, -1), near_item=flower, far_talks=True, mood="happy",
                              hair_back=lambda k, v: long_back(k, MED_HAIR, 3.3, v=v), head=medulina_head, boot_h=5), WOMAN)

KUBA_HAIR = Col(0.3, "#4a3a2c")


def kuba_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = r*CX[v]
    bald(k, KUBA_HAIR, v)
    if v == "back":
        for sx in (-1, 1):
            shape(bez((sx*r*0.85, cy-r*0.32), (sx*r*1.15, cy-r*0.3), (sx*r*1.25, cy-r*0.45), (sx*r*1.05, cy-r*0.55)), KUBA_HAIR, LINE*0.6)
        return
    m = bez((c-r*0.85, cy-r*0.35), (c-r*0.5, cy-r*0.2), (c+r*0.5, cy-r*0.2), (c+r*0.85, cy-r*0.35)) + \
        bez((c+r*0.85, cy-r*0.35), (c+r*0.6, cy-r*0.65), (c+r*0.2, cy-r*0.52), (c, cy-r*0.5)) + \
        bez((c, cy-r*0.5), (c-r*0.2, cy-r*0.52), (c-r*0.6, cy-r*0.65), (c-r*0.85, cy-r*0.35))
    shape(m, KUBA_HAIR, LINE*0.8)
    for sx in (-1, 1): fill(ell(c+sx*r*0.6, cy-r*0.3, r*0.16, r*0.1, 12), Col(0.6, "#d07a6a", alpha=0.35))


KUBA_VEST = Col(0.32, "#5a4632")


def kuba_vest(k, t, v):
    if v == "back":
        form(torso_pts(k, 52, 21.5, waist_w=25.5, collar=4.5), KUBA_VEST, sdx=0, sh=0.1)
        coat_back(k, 52, KUBA_VEST)
        return
    for vv in ([(-5, k.sh_y+2.4), (-k.sh_w-1.6, k.sh_y-3.5), (-22, 70), (-21, 52), (-4, 50), (-3, 70)],
               [(5, k.sh_y+2.4), (k.sh_w+1.6, k.sh_y-3.5), (22, 70), (21, 52), (4, 50), (3, 70)]):
        form(vv, KUBA_VEST, sdx=-1.4 if v == "side" else 0, sh=0.1)


hostinsky_kuba = npc(dict(coat=Col(0.6, "#8f8268"), hem=50, hem_w=23, waist_w=27, sleeve=Col(0.8, "#d4ccb8"), rolled=False,
                          trousers=Col(0.36, "#4e4840"), apron=(Col(0.85, "#ddd6c4"), 66, 30, 17),
                          coat_detail=kuba_vest, near=("a", -60, 10), near_item=mug, far_talks=True, mood="happy",
                          head=kuba_head, wk=1.1, neck_w=4, arm_out=9), dict(MAN, sh_w=14, hy=110, sh_y=95), 21)


# ------------------------------------------------------------------ Fabián
FAB_HAT = Col(0.25, "#3a3430")


def cone_scales(clip, x0, x1, y0, y1, col=Col(0.42, "#7a5636"), step=3.6):
    C.saveState()
    from style3 import poly
    C.clipPath(poly(clip), stroke=0, fill=0)
    row = 0
    y = y1
    while y > y0-4:
        off = (row % 2)*step*0.5
        x = x0-step+off
        while x < x1+step:
            sc = bez((x-step*0.55, y), (x-step*0.5, y-step*0.9), (x+step*0.5, y-step*0.9), (x+step*0.55, y)) + [(x, y+0.5)]
            shape(sc, col, LINE*0.5)
            x += step
        y -= step*0.62; row += 1
    C.restoreState()


def fabian_body_detail(k, tors, v="side"):
    cone_scales(tors, -20, 20, 40, 100)
    stroke(tors, LINE, closed=True)


def fabian_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        beard_back(k, MOSS, BARK, 2.2)
    else:
        bd = bez((-r*0.95, cy-r*0.1), (-r*1.3, cy-r*1.5), (r*(c-0.8), cy-r*2.6), (r*c, cy-r*2.8)) + \
            bez((r*c, cy-r*2.8), (r*(c+0.7), cy-r*2.4), (r*1.3, cy-r*1.2), (r*0.95, cy-r*0.1)) + \
            bez((r*0.95, cy-r*0.1), (r*0.7, cy-r*0.5), (r*(c+0.2), cy-r*0.45), (r*c, cy-r*0.5)) + \
            bez((r*c, cy-r*0.5), (r*(c-0.3), cy-r*0.45), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.1))
        form(bd, MOSS, sdx=-1 if v == "side" else 0, sdy=0.6, sh=0.12)
        for (dx, dy) in ((-0.5, -1.0), (0.1, -1.4), (0.5, -0.9), (-0.2, -2.0), (0.4, -2.2), (-0.7, -1.6)):
            if v == "front": dx -= 0.1
            stroke(ell(r*dx, cy+r*dy, r*0.14, r*0.12, 8, 30, 250), LINE*0.45, g=Col(0.3, "#4a5a30"))
        face(r*c, cy, r*0.95, md)
        if md not in ("talk",): pipe(r*(c+0.15), cy-r*0.62)
    brim = bez((-r*1.9, cy+r*0.55), (-r*1.0, cy+r*0.95), (r*1.0, cy+r*0.95), (r*1.95, cy+r*0.6)) + \
        bez((r*1.95, cy+r*0.6), (r*1.2, cy+r*0.3), (-r*1.2, cy+r*0.3), (-r*1.9, cy+r*0.55))
    form(brim, FAB_HAT, sh=0.1)
    crown = [(-r*0.85, cy+r*0.75), (-r*0.7, cy+r*1.9), (r*0.75, cy+r*1.95), (r*0.9, cy+r*0.8)]
    form(crown, FAB_HAT, sdx=-1.2 if v == "side" else 0, sdy=0.6, sh=0.12)
    shape([(-r*0.84, cy+r*0.8), (r*0.89, cy+r*0.85), (r*0.86, cy+r*1.1), (-r*0.8, cy+r*1.05)], Col(0.4, "#6a3a2e"), LINE*0.6)
    tube(bez((-r*0.6, cy+r*1.0), (-r*1.4, cy+r*1.6), (-r*1.9, cy+r*2.6), (-r*1.8, cy+r*3.0)), 2.2, 0.8, Col(0.6, "#8a9a7a"), LINE*0.6, sh=0)


fabian = npc(dict(coat=Col(0.42, "#7a5636"), hem=50, hem_w=16, waist_w=14, coat_detail=fabian_body_detail,
                  sleeve=BARK, skin=BARK, trousers=BARK_DK, boots=Col(0.28, "#4a3a2a"), boot_h=6,
                  back=None, front=lambda k, v: bag(k), near=("a", -80, -60), far_talks=True, head=fabian_head, face_late=True,
                  talk_mood="talk", arm_out=1), MAN)


MZ_COAT = Col(0.42, "#6a5a40")
MZ_O = dict(both_talk=True, far_talk=("a", 130, 100), far=("a", -110, -95), near=("a", -60, -20), near_talk=("a", -20, 40),
            neck_w=2.4, face_late=True)


def muzicek_draw():
    def draw(x, y, s, pose="idle"):
        base, v = split_pose(pose)
        k = Person(**SMALL)
        talk = base == "talk"
        md = "talk" if talk else "think"
        fb = v != "side"; bk = v == "back"
        c = CX[v]
        if pose != "portrait": cast_shadow(x, y, 10*s, 2.4*s)
        with T(x, y, s):
            if bk: C.scale(-1, 1)
            r = k.hr; cy = k.hy
            t = r*(c+0.1)
            bd = bez((-r*0.95, cy-r*0.15), (-r*1.2, cy-r*2.0), (-r*0.9, cy-r*3.6), (t-r*0.4, cy-r*4.15)) + \
                bez((t-r*0.4, cy-r*4.15), (t+r*0.2, cy-r*4.25), (r*1.0, cy-r*3.8), (r*1.15, cy-r*2.6)) + \
                bez((r*1.15, cy-r*2.6), (r*1.2, cy-r*1.4), (r*1.05, cy-r*0.6), (r*0.95, cy-r*0.15)) + \
                bez((r*0.95, cy-r*0.15), (r*0.7, cy-r*0.5), (r*(c+0.25), cy-r*0.48), (r*(c+0.1), cy-r*0.5)) + \
                bez((r*(c+0.1), cy-r*0.5), (r*(c-0.3), cy-r*0.48), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.15))
            if fb and base in PHASE:
                bd = sway(bd, CLOTH[True][base][0]*0.6, 0, cy-r, cy-r*4.2, r)
            elif base in PHASE:
                bd = sway(bd, CLOTH[False][base][0]*0.5, 0, cy-r, cy-r*4.2, r)
            if bk: form(bd, WHITE_HAIR, sdx=0, sdy=0.4, sh=0.08)
            sp, op = arm_spec(k, MZ_O, -1, base, v)
            arm(k, -1, sp, MZ_COAT, BARK, open_=op, hr=2.3)
            legs_any(k, base, v, MZ_O, BARK_DK, Col(0.3, "#4a3a2a"), 5, 0.8, 0.8, 0.8)
            tors = torso_pts(k, 12, 11, waist_w=10.5, collar=3)
            form(tors, MZ_COAT, sdx=0 if fb else -1.8, sdy=1, sh=0.14)
            if bk: coat_back(k, 12, MZ_COAT)
            sp, op = arm_spec(k, MZ_O, 1, base, v)
            arm(k, 1, sp, MZ_COAT, BARK, open_=op, hr=2.3)
            npc_head(k, md, BARK, MZ_O, v)
            if bk: nape(k, WHITE_HAIR)
            else:
                for (x0, y0, x1, y1) in ((-0.7, 0.6, -0.5, 0.1), (0.75, 0.5, 0.85, 0.0), (-0.3, -0.2, -0.45, -0.4)):
                    stroke([(r*x0, cy+r*y0), (r*x1, cy+r*y1)], LINE*0.5, g=BARK_DK)
                face(r*c, cy, r*0.95, md)
                form(bd, WHITE_HAIR, sdx=-1 if not fb else 0, sdy=0.4, sh=0.08)
                for xx in (-0.5, -0.1, 0.3, 0.7):
                    xx += c - 0.2
                    stroke(bez((r*xx, cy-r*0.9), (r*xx*1.1, cy-r*1.8), (r*xx, cy-r*2.8), (r*xx*0.8, cy-r*3.7)), LINE*0.45, g=GREY_LINE)
                if talk: shape(ell(r*c, cy-r*0.65, r*0.13, r*0.1, 12), Col(0.25, "#4a2a20"), LINE*0.6)
                moustache(k, WHITE_HAIR, dx=c, w=0.6)
            h0 = r*(0.3 if not fb else 0.1)
            hat = bez((-r*1.1, cy+r*0.3), (-r*0.8, cy+r*1.4), (h0-r*0.4, cy+r*2.4), (h0, cy+r*2.6)) + \
                bez((h0, cy+r*2.6), (h0+r*0.2, cy+r*1.6), (r*0.9, cy+r*1.0), (r*1.1, cy+r*0.35)) + \
                bez((r*1.1, cy+r*0.35), (r*0.4, cy+r*0.5), (-r*0.4, cy+r*0.5), (-r*1.1, cy+r*0.3))
            form(hat, MOSS, sdx=-1 if not fb else 0, sdy=0.8, sh=0.14)
            for (dx, dy) in ((-0.5, 0.8), (0.1, 1.3), (0.5, 0.7), (-0.1, 1.9)):
                stroke(ell(r*dx, cy+r*dy, r*0.12, r*0.1, 8, 30, 250), LINE*0.4, g=Col(0.3, "#4a5a30"))
    draw.K = SMALL
    draw.poses = POSES
    return draw


tremsinsky_muzicek = muzicek_draw()


# ------------------------------------------------------------------ Jáchymov
KR_HAIR = Col(0.38, "#6a4a30")


def krystof_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        beard_back(k, KR_HAIR, SKIN, 1.25)
        nape(k, KR_HAIR)
    else:
        beard(k, KR_HAIR, 1.25, dx=c/2)
        face(r*c, cy, r*0.95, md)
        moustache(k, KR_HAIR, dx=c)
    cap = bez((-r*1.08, cy+r*0.35), (-r*1.2, cy+r*1.5), (r*1.2, cy+r*1.5), (r*1.08, cy+r*0.35)) + \
        bez((r*1.08, cy+r*0.35), (r*0.4, cy+r*0.5), (-r*0.4, cy+r*0.5), (-r*1.08, cy+r*0.35))
    form(cap, Col(0.38, "#5e4e3e"), sdx=-1.4 if v == "side" else 0, sh=0.12)
    shape(rrect(-r*1.12, cy+r*0.28, r*2.24, r*0.3, 0.8), LEATHER, LINE*0.7)


kovar_krystof = npc(dict(coat=Col(0.45, "#5e6670"), hem=56, hem_w=15, waist_w=14.5, rolled=True, trousers=Col(0.36, "#4a4640"),
                         apron=(LEATHER, 76, 30, 13), belt=(Col(0.3, "#3e2e24"), 58), front=lambda k, v: pouch(10, 57),
                         near=("a", -55, 15), near_f=("k", 21, 70, -1), near_item=coin, far_talks=True, head=krystof_head, face_late=True,
                         far_item=lambda H, fa: hammer(H, fa, -100, 14), wk=1.1, boot_h=8, arm_out=1), MAN)


AG_ROBE = Col(0.34, "#6a3438")
FUR = Col(0.45, "#7a6248")
AG_HAIR = Col(0.35, "#5a4636")


def agricola_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        beard_back(k, AG_HAIR, SKIN, 1.75)
        nape(k, AG_HAIR)
    else:
        for sx in (-1, 1):
            shape(bez((sx*r*0.98, cy+r*0.45), (sx*r*1.1, cy+r*0.1), (sx*r*1.02, cy-r*0.2), (sx*r*0.9, cy-r*0.3)) +
                  [(sx*r*0.8, cy+r*0.4)], AG_HAIR, LINE*0.7)
        beard(k, AG_HAIR, 1.75, Col(0.25, "#3a2e26"), dx=c/2)
        face(r*c, cy, r*0.95, md)
        moustache(k, AG_HAIR, dx=c)
    cap = bez((-r*1.35, cy+r*0.6), (-r*1.6, cy+r*1.2), (-r*0.6, cy+r*1.55), (r*0.6, cy+r*1.5)) + \
        bez((r*0.6, cy+r*1.5), (r*1.6, cy+r*1.4), (r*1.5, cy+r*0.8), (r*1.2, cy+r*0.6)) + \
        bez((r*1.2, cy+r*0.6), (r*0.4, cy+r*0.45), (-r*0.4, cy+r*0.45), (-r*1.35, cy+r*0.6))
    if v != "side":
        cap = bez((-r*1.3, cy+r*0.6), (-r*1.6, cy+r*1.3), (-r*0.6, cy+r*1.55), (0, cy+r*1.55)) + \
            bez((0, cy+r*1.55), (r*0.6, cy+r*1.55), (r*1.6, cy+r*1.3), (r*1.3, cy+r*0.6)) + \
            bez((r*1.3, cy+r*0.6), (r*0.4, cy+r*0.45), (-r*0.4, cy+r*0.45), (-r*1.3, cy+r*0.6))
    form(cap, Col(0.22, "#34303a"), sdx=-1 if v == "side" else 0, sdy=0.6, sh=0.12)
    stroke(bez((-r*1.2, cy+r*0.62), (-r*0.4, cy+r*0.55), (r*0.4, cy+r*0.55), (r*1.15, cy+r*0.66)), LINE*0.6, g=BRASS)


def agricola_detail(k, tors, v="side"):
    if v == "back":
        f = bez((-(k.sh_w+2.6), k.sh_y-6), (-k.sh_w, k.sh_y-11), (k.sh_w, k.sh_y-11), (k.sh_w+2.6, k.sh_y-6)) + \
            [(k.sh_w+2.4, k.sh_y+0.5), (4, k.sh_y+3), (-4, k.sh_y+3), (-(k.sh_w+2.4), k.sh_y+0.5)]
        form(f, FUR, sdx=0, sdy=0.5, sh=0.1)
        for xx in range(-12, 13, 4): stroke([(xx, k.sh_y-4), (xx+1.2, k.sh_y-6.5)], LINE*0.4, g=Col(0.3, "#4e3e2e"))
        return
    for sx in (-1, 1):
        f = [(sx*4, k.sh_y+3), (sx*(k.sh_w+2.4), k.sh_y+0.5), (sx*(k.sh_w+2.6), k.sh_y-7), (sx*8, 60), (sx*4.5, 8), (sx*1.2, 8), (sx*1.5, 60)]
        form(f, FUR, sdx=-1 if v == "side" else 0, sdy=0.5, sh=0.1)
        for yy in range(16, 90, 9): stroke([(sx*2.5, yy), (sx*3.6, yy-2)], LINE*0.4, g=Col(0.3, "#4e3e2e"))
    form([(-3.5, k.sh_y+2.5), (3.5, k.sh_y+2.5), (2.5, 70), (-2.5, 70)], Col(0.25, "#2e2a30"), sh=0)
    stroke(bez((-3, k.sh_y+1), (-1, 82), (1, 82), (3, k.sh_y+1)), LINE*0.6, g=BRASS)


lekarnik_agricola = npc(dict(coat=AG_ROBE, hem=6, hem_w=16.5, waist_w=14.5, coat_detail=agricola_detail, cuff=FUR,
                             near=("a", -55, 20), near_f=("k", 20, 70, -1), near_item=flask, far_talks=True, head=agricola_head,
                             face_late=True, boot_h=5), MAN, 17)

RZ_HAIR = Col(0.36, "#5e3e2e")


def rozina_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    hair_cap(k, RZ_HAIR, v=v)
    strands = ((0.6, 0.55, 1.0, -0.3), (-0.2, 0.62, -0.05, 0.25), (-0.95, 0.2, -1.15, -0.6))
    if v == "front": strands = ((0.6, 0.55, 1.05, -0.4), (-0.1, 0.64, 0.05, 0.25), (-0.6, 0.55, -1.05, -0.4))
    if v == "back": strands = ((0.85, 0.2, 1.12, -0.6), (-0.85, 0.2, -1.12, -0.6))
    for (x0, y0, x1, y1) in strands:
        stroke(bez((r*x0, cy+r*y0), (r*(x0+x1)/2+r*0.1, cy+r*(y0+y1)/2), (r*x1, cy+r*y1+r*0.1), (r*x1, cy+r*y1)), LINE*0.8, g=RZ_HAIR)
    if v == "back": return
    for sx in (-1, 1):
        x = r*c+sx*r*0.38
        stroke(bez((x-r*0.15, cy-r*0.12), (x, cy-r*0.2), (x+r*0.15, cy-r*0.12), (x+r*0.18, cy-r*0.1)), LINE*0.4, g=Col(0.4, "#8a6a6a"))


def rag(H, fa):
    r_ = [(H[0]-2, H[1]-1), (H[0]+3, H[1]-1.5)] + bez((H[0]+3, H[1]-1.5), (H[0]+4, H[1]-6), (H[0]+2, H[1]-9), (H[0]+3, H[1]-12)) + \
        [(H[0]-1, H[1]-11)] + bez((H[0]-1, H[1]-11), (H[0]-2.5, H[1]-7), (H[0]-1, H[1]-4), (H[0]-2, H[1]-1))
    shape(r_, Col(0.75, "#c8c0ac"), LINE*0.7)


senkyrka_rozina = npc(dict(coat=Col(0.72, "#b8ae98"), hem=60, hem_w=12.5, waist_w=11, rolled=True,
                           skirt=(Col(0.4, "#4e5a6a"), 62, 6, 12.5, 18), apron=(Col(0.78, "#cfc8b4"), 63, 20, 11),
                           belt=(Col(0.32, "#3e3a3a"), 63), belt_w=12, mood="sleepy", talk_mood="sad",
                           near=("a", -92, -100), near_item=rag, far_talks=True, head=rozina_head,
                           hair_back=lambda k, v: long_back(k, RZ_HAIR, 1.6, 1.1, v=v), boot_h=5, arm_out=2), WOMAN)


# ------------------------------------------------------------------ the dead
def matej_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        beard_back(k, GHOST_DK, GHOST_SKIN, 1.3)
        nape(k, GHOST_DK)
    else:
        beard(k, GHOST_DK, 1.3, dx=c/2)
        face(r*c, cy, r*0.95, md)
        moustache(k, GHOST_DK, dx=c)
    cap = bez((-r*1.06, cy+r*0.55), (-r*1.12, cy+r*1.7), (r*1.12, cy+r*1.7), (r*1.06, cy+r*0.55)) + \
        bez((r*1.06, cy+r*0.55), (r*0.4, cy+r*0.68), (-r*0.4, cy+r*0.68), (-r*1.06, cy+r*0.55))
    form(cap, GHOST_DK, sdx=-1.5 if v == "side" else 0, sdy=1)
    shape(rrect(-r*1.1, cy+r*0.45, r*2.2, r*0.3, 0.8), GHOST_DK, LINE*0.8)


def dead_lamp(H, fa):
    kahan(H[0], H[1]-1, 1.15, lit=False, body=GHOST_DK)


predak_matej = npc(dict(coat=GHOST, hem=52, hem_w=16, waist_w=15, sleeve=GHOST, skin=GHOST_SKIN, trousers=GHOST_DK,
                        boots=GHOST_DK, belt=(GHOST_DK, 58), cuff=GHOST_DK, mood="sad", talk_mood="talk",
                        coat_detail=lambda k, t, v: [dot(-0.6 if v == "side" else 0, by, 0.8, GHOST_DK) for by in (90, 82, 74, 66)] if v != "back" else None,
                        near=("a", -60, 5), near_item=dead_lamp, far_talks=True, head=matej_head, face_late=True,
                        wk=1.1, boot_h=8, arm_out=1), MAN, alpha=0.78)

ANI_HAIR = Col(0.65, "#8fa8bc")


def anicka_hair_back(k, v="side"):
    long_back(k, ANI_HAIR, 3.6, 1.15, v=v)


def anicka_head(k, md, v="side"):
    r = k.hr; cy = k.hy
    hair_cap(k, ANI_HAIR, low=-0.6, v=v)
    for sx in (-1, 1):
        stroke(bez((sx*r*1.0, cy-r*0.2), (sx*r*1.1, cy-r*1.0), (sx*r*1.05, cy-r*2.0), (sx*r*1.1, cy-r*2.8)), LINE*0.6, g=Col(0.5, "#6a8aa0"))
    for (dx, dy) in ((-1.15, -3.4), (1.1, -3.1), (-0.3, -3.9)):
        shape(bez((r*dx, cy+r*dy+1.6), (r*dx-0.9, cy+r*dy), (r*dx+0.9, cy+r*dy), (r*dx, cy+r*dy+1.6)), Col(0.85, "#d8ecff"), LINE*0.4)


def cup_held(H, fa):
    teacup(H[0]+1.5, H[1]+3.5, Col(0.9, "#e6eef6"))


anicka = npc(dict(coat=GHOST, hem=40, hem_w=13, waist_w=10.5, sleeve=GHOST, skin=GHOST_SKIN, trousers=GHOST_SKIN,
                  boots=GHOST_DK, boot_h=4, skirt=(GHOST, 46, 22, 10.5, 15), mood="sad", talk_mood="talk",
                  near=("k", 9, 52, -1), near_item=cup_held, far=("k", 5, 50, -1), far_talks=False,
                  near_talk=("k", 10, 56, -1), near_f=("k", 1.5, 51, -1), far_f=("k", -3.5, 50.5, 1),
                  near_talk_f=("k", 2, 55, -1), near_inside=True, far_swing=0.25, glide=True,
                  hair_back=anicka_hair_back, head=anicka_head, kx=0.8, neck_w=2.4), GIRL, 12,
             alpha=0.78)

FERRY = Col(0.32, "#4a4e58")
FERRY_DK = Col(0.2, "#2e3038")


def prevoznik_back(k, v="side"):
    if v == "back": return
    r = k.hr; cy = k.hy
    hood = bez((-r*1.45, cy-r*1.4), (-r*1.9, cy+r*0.8), (-r*1.0, cy+r*2.0), (r*0.3, cy+r*1.9)) + \
        bez((r*0.3, cy+r*1.9), (r*1.4, cy+r*1.7), (r*1.7, cy+r*0.6), (r*1.5, cy-r*1.3))
    if v == "front":
        hood = bez((-r*1.55, cy-r*1.4), (-r*1.85, cy+r*0.8), (-r*1.1, cy+r*1.95), (0, cy+r*1.95)) + \
            bez((0, cy+r*1.95), (r*1.1, cy+r*1.95), (r*1.85, cy+r*0.8), (r*1.55, cy-r*1.4))
    form(hood, FERRY, sdx=-1.5 if v == "side" else 0, sdy=1, sh=0.15)


def prevoznik_head(k, md, v="side"):
    r = k.hr; cy = k.hy; c = CX[v]
    if v == "back":
        hd = bez((-r*1.5, cy-r*1.6), (-r*1.75, cy+r*0.7), (-r*1.1, cy+r*1.7), (0, cy+r*1.75)) + \
            bez((0, cy+r*1.75), (r*1.1, cy+r*1.7), (r*1.75, cy+r*0.7), (r*1.5, cy-r*1.6))
        form(hd, FERRY, sdx=0, sdy=1, sh=0.15)
        stroke(bez((0, cy+r*1.7), (r*0.1, cy+r*0.6), (-r*0.1, cy-r*0.4), (0, cy-r*1.5)), LINE*0.5, g=FERRY_DK)
        for sx in (-1, 1):
            stroke(bez((sx*r*0.9, cy+r*1.2), (sx*r*1.25, cy+r*0.3), (sx*r*1.3, cy-r*0.6), (sx*r*1.35, cy-r*1.4)), LINE*0.45, g=FERRY_DK)
        return
    fill(ell(r*c*0.75, cy+r*0.2, r*1.05, r*0.9, 30), Col(0.1, "#141418", alpha=0.55))
    if v == "front":
        hf = bez((-r*1.35, cy-r*0.9), (-r*1.5, cy+r*1.0), (-r*0.7, cy+r*1.7), (0, cy+r*1.7)) + \
            bez((0, cy+r*1.7), (r*0.7, cy+r*1.7), (r*1.5, cy+r*1.0), (r*1.35, cy-r*0.9)) + \
            bez((r*1.35, cy-r*0.9), (r*1.25, cy+r*0.5), (r*0.8, cy+r*0.98), (0, cy+r*1.0)) + \
            bez((0, cy+r*1.0), (-r*0.8, cy+r*0.98), (-r*1.25, cy+r*0.5), (-r*1.35, cy-r*0.9))
    else:
        hf = bez((-r*1.3, cy-r*1.0), (-r*1.5, cy+r*1.0), (-r*0.6, cy+r*1.7), (r*0.25, cy+r*1.65)) + \
            bez((r*0.25, cy+r*1.65), (r*1.1, cy+r*1.6), (r*1.5, cy+r*1.0), (r*1.35, cy-r*0.7)) + \
            bez((r*1.35, cy-r*0.7), (r*1.3, cy+r*0.5), (r*0.9, cy+r*0.95), (r*0.25, cy+r*0.98)) + \
            bez((r*0.25, cy+r*0.98), (-r*0.6, cy+r*1.0), (-r*1.15, cy+r*0.5), (-r*1.1, cy-r*1.0))
    form(hf, FERRY, sdx=-1 if v == "side" else 0, sdy=0.8, sh=0.14)
    beard(k, Col(0.55, "#8a8680"), 1.9, Col(0.4, "#6a6660"), dx=c/2)
    face(r*c, cy, r*0.95, md)
    moustache(k, Col(0.55, "#8a8680"), dx=c)


def ferry_pole(H, fa):
    pole(H, 46, 2)


prevoznik = npc(dict(coat=FERRY, hem=6, hem_w=18, waist_w=15.5, sleeve=FERRY, cuff=FERRY_DK, back=prevoznik_back,
                     belt=(Col(0.4, "#6a5a44"), 60), mood="think",
                     near=("k", 26, 74, -1), near_f=("k", 24, 72, -1), near_item=ferry_pole, near_swing=0.5,
                     after_hand=lambda H, fa: None, far_talks=True,
                     head=prevoznik_head, face_late=True, ear=False, boot_h=5), MAN, 18)


# ------------------------------------------------------------------ jobs
NPCS = {
    "permonik": (permonik, None), "kosmas": (kosmas, None), "kovar_hnevek": (kovar_hnevek, None),
    "korenarka_dorota": (korenarka_dorota, None), "senkyrka_bara": (senkyrka_bara, None),
    "kovar_vojtech": (kovar_vojtech, None), "korenarka_medulina": (korenarka_medulina, None),
    "hostinsky_kuba": (hostinsky_kuba, None), "fabian": (fabian, "#9ab07a"),
    "tremsinsky_muzicek": (tremsinsky_muzicek, "#9ab07a"), "kovar_krystof": (kovar_krystof, None),
    "lekarnik_agricola": (lekarnik_agricola, None), "senkyrka_rozina": (senkyrka_rozina, None),
    "predak_matej": (predak_matej, "#9fc4ff"), "anicka": (anicka, "#9fc4ff"), "prevoznik": (prevoznik, "#7a8aa0"),
}
SMALL_SCALE = 0.48


def sprite(fn, pose):
    s = SMALL_SCALE if fn.K is SMALL else S
    return lambda b: fn(b.w/2, FEET, s, pose)


def port(fn, glow):
    K = fn.K
    if fn in (permonik, permonik_grin): glow = "#9fc4ff"
    small = K is SMALL
    return lambda b: portrait(b, fn, K["hy"], K["hr"], glow=glow or "#e8a55a", k=0.17 if small else 0.24, fy=0.4 if small else 0.5)


def jobs():
    sp, pt = [], []
    for name, (fn, glow) in NPCS.items():
        for p in getattr(fn, "poses", ("idle", "talk")):
            sp.append((name if p == "idle" else f"{name}_{p}", 200, 240, sprite(fn, p)))
        pt.append((name, 256, 256, port(fn, glow)))
    for sfx in ("", "_f", "_b"):
        sp.append(("permonik_grin" + sfx, 200, 240, sprite(permonik_grin, "idle" + sfx)))
    pt.append(("permonik_grin", 256, 256, port(permonik_grin, None)))
    return {"sprites/npcs": sp, "portraits": pt}


if __name__ == "__main__":
    common.run(jobs())
