import math
import common
from common import FEET
from lib import Col, ell, bez, rrect
from style3 import C, T, stroke, shape, form, fill, hatch, tube, cast_shadow, dot, face, head_outline, clip_fill, LINE
from chars3 import Person
from heroes import (SKIN, SKIN_DK, IRON, IRON_LT, WOOD, WOOD_LT, BRASS, BONE, RED, LEATHER, BOOT, FLAME, GLOW,
                    arm, hnd, legs, torso_pts, skirt_pts, head, neck, beard, moustache, kahan, portrait)

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


# ------------------------------------------------------------------ hair & hats
def hair_cap(k, col, part=0.15, dark=None, low=-0.2):
    r = k.hr; cy = k.hy
    h = bez((-r*1.04, cy+r*low), (-r*1.18, cy+r*1.25), (r*1.18, cy+r*1.25), (r*1.04, cy+r*low+0.1*r)) + \
        bez((r*1.04, cy+r*(low+0.1)), (r*0.95, cy+r*0.45), (r*0.65, cy+r*0.6), (r*part, cy+r*0.68)) + \
        bez((r*part, cy+r*0.68), (-r*0.4, cy+r*0.6), (-r*0.9, cy+r*0.4), (-r*1.04, cy+r*low))
    form(h, col, sdx=-1, sdy=0.6, sh=0.1)


def long_back(k, col, length=3.2, w=1.25):
    r = k.hr; cy = k.hy
    b = bez((-r*1.0, cy+r*0.4), (-r*w*1.1, cy-r*0.8), (-r*w*1.15, cy-r*length*0.7), (-r*w, cy-r*length)) + \
        [(-r*0.4, cy-r*length-1), (r*0.4, cy-r*length-1)] + \
        bez((r*w, cy-r*length), (r*w*1.15, cy-r*length*0.7), (r*w*1.1, cy-r*0.8), (r*1.0, cy+r*0.4))
    form(b, col, sh=0.1)


def bun(k, col):
    r = k.hr; cy = k.hy
    shape(ell(-r*0.75, cy+r*0.7, r*0.42, r*0.4, 18), col)
    stroke(ell(-r*0.75, cy+r*0.7, r*0.2, r*0.18, 10, 20, 300), LINE*0.5)


def scarf(k, col, knot=True, line=None):
    r = k.hr; cy = k.hy
    if knot:
        shape([(-r*0.85, cy-r*0.55), (-r*1.6, cy-r*1.4), (-r*1.25, cy-r*1.6), (-r*0.6, cy-r*0.8)], col, LINE*0.8)
        shape([(-r*0.7, cy-r*0.6), (-r*1.0, cy-r*1.7), (-r*0.65, cy-r*1.75), (-r*0.45, cy-r*0.75)], col, LINE*0.8)
    s = bez((-r*1.12, cy-r*0.45), (-r*1.3, cy+r*1.45), (r*1.3, cy+r*1.45), (r*1.12, cy-r*0.1)) + \
        bez((r*1.12, cy-r*0.1), (r*0.9, cy+r*0.55), (r*0.5, cy+r*0.62), (r*0.1, cy+r*0.62)) + \
        bez((r*0.1, cy+r*0.62), (-r*0.4, cy+r*0.62), (-r*0.9, cy+r*0.3), (-r*0.95, cy-r*0.45))
    form(s, col, sdx=-1, sdy=0.6, sh=0.12)
    if line is not None:
        for (dx, dy) in ((-0.5, 1.0), (0.1, 1.15), (0.6, 0.95), (-0.8, 0.4), (0.9, 0.35)):
            dot(r*dx, cy+r*dy, r*0.08, line)


def bald(k, col):
    r = k.hr; cy = k.hy
    shape(bez((-r*0.98, cy+r*0.45), (-r*1.1, cy+r*0.1), (-r*1.02, cy-r*0.2), (-r*0.85, cy-r*0.35)) + [(-r*0.7, cy+r*0.45)], col, LINE*0.7)
    shape(bez((r*0.98, cy+r*0.4), (r*1.06, cy+r*0.1), (r*1.02, cy-r*0.2), (r*0.92, cy-r*0.3)) + [(r*0.85, cy+r*0.4)], col, LINE*0.7)
    stroke(bez((-r*0.3, cy+r*0.85), (-r*0.1, cy+r*0.9), (r*0.1, cy+r*0.9), (r*0.3, cy+r*0.85)), LINE*0.5)


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
def npc_body(k, pose, o):
    talk = pose == "talk"
    md = o.get("talk_mood", "talk") if talk else o.get("mood", "think")
    skin = o.get("skin", SKIN)
    sleeve = o.get("sleeve", o.get("coat"))
    if o.get("back"): o["back"](k)
    if o.get("hair_back"): o["hair_back"](k)
    far = o.get("far_talk", TALK_FAR) if talk and o.get("far_talks") else o.get("far", ("a", -98, -86))
    H, fa = arm(k, -1, far, sleeve, skin, rolled=o.get("rolled", False), hand=False, cuff=o.get("cuff"))
    if o.get("far_item"): o["far_item"](H, fa)
    hnd(H[0], H[1], fa, 2.4, skin, open_=talk and o.get("far_talks", False))
    ph = legs(k, o.get("legs", "stand"), o.get("trousers", Col(0.45, "#5f584e")), o.get("boots", BOOT),
              boot_h=o.get("boot_h", 7), wk=o.get("wk", 1.0), kx=o.get("kx", 1.0))
    if o.get("skirt"):
        col, top, hem_y, w0, w1 = o["skirt"]
        sk = skirt_pts(top, w0, hem_y, -w1, w1)
        form(sk, col, sdx=-2.2, sdy=1, sh=0.14)
        for xx in (-0.6, -0.2, 0.25, 0.65):
            stroke(bez((xx*w0, top-3), (xx*w1*0.9, (top+hem_y)/2), (xx*w1, hem_y+6), (xx*w1*1.05, hem_y+1.5)), LINE*0.45, g=o.get("fold", Col(0.3, "#3a3434")))
    if o.get("coat"):
        tors = torso_pts(k, o.get("hem", 56), o.get("hem_w", k.sh_w+3), waist_w=o.get("waist_w"), collar=o.get("collar", 4.5))
        form(tors, o["coat"], sdx=-2.2, sdy=1.2, sh=0.13)
        if o.get("coat_detail"): o["coat_detail"](k, tors)
    if o.get("apron"):
        col, top, bot, w = o["apron"]
        ap = [(-w*0.85, top), (w*0.85, top)] + bez((w*0.85, top), (w, (top+bot)/2), (w*1.05, bot+8), (w, bot)) + \
            bez((w, bot), (w*0.3, bot-1), (-w*0.3, bot-1), (-w, bot)) + bez((-w, bot), (-w*1.05, bot+8), (-w, (top+bot)/2), (-w*0.85, top))
        form(ap, col, sdx=-1.5, sdy=0.8, sh=0.1)
        if o.get("bib"):
            bt = o["bib"]
            form([(-w*0.5, top), (w*0.5, top), (w*0.45, bt), (-w*0.45, bt)], col, sh=0.08)
            for sx in (-1, 1): stroke([(sx*w*0.45, bt), (sx*(k.sh_w-3), k.sh_y+1.5)], LINE*1.6, g=col)
    if o.get("belt"):
        col, y = o["belt"]; w = o.get("belt_w", k.sh_w+2.5)
        shape([(-w, y-2), (w, y-2), (w+0.2, y+2), (-w-0.2, y+2)], col, LINE*0.8)
    if o.get("front"): o["front"](k)
    near = o.get("near_talk", ("a", -40, 30)) if talk and not o.get("far_talks") else o.get("near", ("a", -82, -92))
    H, fa = arm(k, 1, near, sleeve, skin, rolled=o.get("rolled", False), hand=False, cuff=o.get("cuff"))
    if o.get("near_item"): o["near_item"](H, fa)
    hnd(H[0], H[1], fa, 2.4, skin, open_=talk and not o.get("far_talks") and not o.get("near_item"))
    if o.get("after_hand"): o["after_hand"](H, fa)
    head(k, md, skin, ear=o.get("ear", True), neck_w=o.get("neck_w", 2.8), do_face=not o.get("face_late"))
    if o.get("head"): o["head"](k, md)


def npc(o, Kd, shadow_rx=16, shadow=True, alpha=None):
    def draw(x, y, s, pose="idle"):
        k = Person(**Kd)
        if shadow and pose != "portrait": cast_shadow(x, y, shadow_rx*s, 3*s)
        C.saveState()
        if alpha: C.setFillAlpha(alpha); C.setStrokeAlpha(alpha)
        with T(x, y, s):
            npc_body(k, "talk" if pose == "talk" else "idle", o)
        C.restoreState()
    draw.K = Kd
    return draw


def late_face(dx=0.2):
    def f(k, md): face(k.hr*dx, k.hy, k.hr*0.95, md)
    return f


def chain(*fns):
    def f(*a):
        for fn in fns: fn(*a)
    return f


# ------------------------------------------------------------------ Permoník
PM_SMOCK = Col(0.88, "#e6e0d2")
PM_SMOCK_DK = Col(0.72, "#bdb5a2")
PM_CAP = Col(0.38, "#a83a30")


def permonik_draw(mood_idle="happy"):
    def draw(x, y, s, pose="idle"):
        k = Person(**SMALL)
        talk = pose == "talk"
        md = "talk" if talk else mood_idle
        with T(x, y, s):
            r = k.hr; cy = k.hy
            flek = [(-9.5, 22)] + bez((-9.5, 22), (-12, 16), (-12, 11), (-10.5, 8)) + [(-4, 9), (-3, 21)]
            form(flek, LEATHER, sh=0.15)
            far = ("a", 130, 100) if talk else ("a", -110, -95)
            H, fa = arm(k, -1, far, PM_SMOCK, hand=False, hr=2.3)
            hnd(H[0], H[1], fa, 2.3, open_=talk)
            legs(k, "stand", PM_SMOCK_DK, BOOT, boot_h=5, wk=0.85, kx=0.8)
            tors = torso_pts(k, 11, 12, waist_w=11.5, collar=3)
            form(tors, PM_SMOCK, sdx=-1.8, sdy=1, sh=0.14)
            shape([(-11.6, 19), (11.6, 19), (11.8, 22.5), (-11.8, 22.5)], LEATHER, LINE*0.8)
            shape(rrect(1, 18.5, 3.4, 4.6, 0.5), BRASS, LINE*0.6)
            H, fa = arm(k, 1, ("a", -30, 10), PM_SMOCK, hand=False, hr=2.3)
            kahan(H[0]+0.5, H[1]-0.5, 1.0, COLD, COLD_GLOW, Col(0.55, "#8a8f98"))
            hnd(H[0], H[1], fa, 2.3)
            head(k, md, neck_w=2.4, do_face=False)
            bd = bez((-r*0.95, cy-r*0.15), (-r*1.05, cy-r*1.6), (-r*0.5, cy-r*2.4), (r*0.25, cy-r*2.5)) + \
                bez((r*0.25, cy-r*2.5), (r*0.8, cy-r*2.2), (r*1.1, cy-r*1.2), (r*0.95, cy-r*0.15)) + \
                bez((r*0.95, cy-r*0.15), (r*0.7, cy-r*0.5), (r*0.45, cy-r*0.48), (r*0.3, cy-r*0.5)) + \
                bez((r*0.3, cy-r*0.5), (-r*0.1, cy-r*0.48), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.15))
            form(bd, WHITE_HAIR, sdx=-1, sdy=0.5, sh=0.08)
            for xx in (-0.5, -0.1, 0.3, 0.65):
                stroke(bez((r*xx, cy-r*0.8), (r*xx*1.05, cy-r*1.3), (r*xx, cy-r*1.8), (r*xx*0.8, cy-r*2.2)), LINE*0.45, g=GREY_LINE)
            face(r*0.2, cy, r*0.95, md)
            wrinkles(k)
            moustache(k, WHITE_HAIR, w=0.6)
            if md == "grin":
                c = r*0.2
                sm = bez((c-r*0.45, cy-r*0.58), (c-r*0.15, cy-r*0.98), (c+r*0.3, cy-r*0.95), (c+r*0.6, cy-r*0.5)) + \
                    bez((c+r*0.6, cy-r*0.5), (c+r*0.25, cy-r*0.72), (c-r*0.15, cy-r*0.74), (c-r*0.45, cy-r*0.58))
                shape(sm, Col(0.25, "#5a2228"), LINE*0.7)
                stroke(bez((c-r*0.3, cy-r*0.66), (c-r*0.05, cy-r*0.76), (c+r*0.2, cy-r*0.74), (c+r*0.45, cy-r*0.58)), LINE*0.9, g=Col(0.95, "#f4efe0"))
            if md == "talk":
                shape(ell(r*0.2, cy-r*0.72, r*0.14, r*0.1, 12), Col(0.25, "#6a2a30"), LINE*0.6)
            shape(ell(r*0.25, cy-r*0.12, r*0.2, r*0.16, 12), Col(0.75, "#e0a890"), LINE*0.6)
            cap = bez((-r*1.08, cy+r*0.35), (-r*1.3, cy+r*1.4), (-r*1.4, cy+r*2.2), (-r*2.4, cy+r*1.8)) + \
                bez((-r*2.4, cy+r*1.8), (-r*1.6, cy+r*2.7), (r*0.6, cy+r*2.0), (r*1.08, cy+r*0.4)) + \
                bez((r*1.08, cy+r*0.4), (r*0.4, cy+r*0.55), (-r*0.4, cy+r*0.55), (-r*1.08, cy+r*0.35))
            form(cap, PM_CAP, sdx=-1.4, sdy=1, sh=0.15)
            shape(ell(-r*2.45, cy+r*1.75, r*0.28, r*0.28, 14), WHITE_HAIR, LINE*0.7)
            shape(bez((-r*1.15, cy+r*0.15), (-r*0.4, cy+r*0.42), (r*0.4, cy+r*0.42), (r*1.15, cy+r*0.2)) +
                  bez((r*1.15, cy+r*0.2), (r*1.15, cy+r*0.55), (r*0.4, cy+r*0.78), (-r*1.15, cy+r*0.55)), PM_SMOCK, LINE*0.8)
    draw.K = SMALL
    return draw


permonik = permonik_draw("happy")
permonik_grin = permonik_draw("grin")


# ------------------------------------------------------------------ townsfolk
def kosmas_head(k, md):
    r = k.hr; cy = k.hy
    bald(k, WHITE_HAIR)
    beard(k, WHITE_HAIR, 1.45, GREY_LINE)
    face(r*0.2, cy, r*0.95, md)
    moustache(k, WHITE_HAIR)
    wrinkles(k); specs(k)


def kosmas_book(k):
    book(9, 70, -12, Col(0.35, "#5a3a30"), 13, 17)


kosmas = npc(dict(coat=Col(0.38, "#5a4a5e"), hem=6, hem_w=17, waist_w=15, sleeve=Col(0.38, "#5a4a5e"),
                  belt=(Col(0.6, "#a8946c"), 60), front=kosmas_book, near=("a", -100, -40), far_talks=True,
                  cuff=Col(0.45, "#4a3d4e"), head=kosmas_head, face_late=True, boot_h=5), OLD)


def hnevek_head(k, md):
    r = k.hr; cy = k.hy
    bald(k, Col(0.22, "#3a2c26"))
    beard(k, Col(0.22, "#3a2c26"), 1.6)
    face(r*0.2, cy, r*0.95, md)
    moustache(k, Col(0.22, "#3a2c26"))
    for sx in (-1, 1): shape(ell(r*0.2+sx*r*0.38, cy+r*0.32, r*0.24, r*0.08, 10), Col(0.22, "#3a2c26"), LINE*0.5)


kovar_hnevek = npc(dict(coat=Col(0.5, "#7a6e60"), hem=56, hem_w=17, waist_w=17, rolled=True, trousers=Col(0.35, "#4e4a44"),
                        apron=(LEATHER, 80, 30, 14), bib=93, near=("a", -80, -70), near_item=lambda H, fa: hammer(H, fa, 75, 17, True),
                        far_talks=True, head=hnevek_head, face_late=True, wk=1.15, boot_h=8, neck_w=4), BURLY, 19)


DOROTA_SCARF = Col(0.48, "#9a6a3a")


def dorota_head(k, md):
    scarf(k, DOROTA_SCARF, line=Col(0.8, "#d9c8a0"))
    wrinkles(k)


korenarka_dorota = npc(dict(coat=Col(0.6, "#9c8f76"), hem=58, hem_w=13, waist_w=11.5, sleeve=Col(0.6, "#9c8f76"),
                            skirt=(Col(0.38, "#5e5444"), 60, 6, 13, 18), apron=(Col(0.66, "#a8a090"), 61, 18, 11),
                            near=("a", -95, -80), near_item=basket, far_talks=True, mood="happy", head=dorota_head, boot_h=5), WOMAN)


def bara_head(k, md):
    hair_cap(k, Col(0.42, "#7a4f2e"))


senkyrka_bara = npc(dict(coat=Col(0.82, "#d6ccb6"), hem=60, hem_w=13, waist_w=12, rolled=True,
                         skirt=(Col(0.36, "#6a3a36"), 62, 6, 13, 19), apron=(Col(0.85, "#ddd6c4"), 63, 16, 12),
                         front=lambda k: shape([(-11, 62), (11, 62), (10, 80), (-10, 80)], Col(0.3, "#4a3a3a")),
                         belt=(Col(0.3, "#4a3a3a"), 63), belt_w=12.5,
                         near=("a", -88, -70), near_item=jug, far_talks=True, mood="happy", hair_back=lambda k: bun(k, Col(0.42, "#7a4f2e")),
                         head=bara_head, boot_h=5), dict(WOMAN, sh_w=12.5))


def vojtech_head(k, md):
    r = k.hr; cy = k.hy
    h = [(-r*1.04, cy-r*0.1), (-r*1.2, cy+r*0.6), (-r*0.9, cy+r*1.2), (-r*0.3, cy+r*1.35), (r*0.2, cy+r*1.4),
         (r*0.8, cy+r*1.2), (r*1.15, cy+r*0.7), (r*1.04, cy+r*0.1), (r*0.85, cy+r*0.55), (r*0.55, cy+r*0.45),
         (r*0.35, cy+r*0.7), (r*0.05, cy+r*0.5), (-r*0.3, cy+r*0.68), (-r*0.6, cy+r*0.45), (-r*0.85, cy+r*0.55)]
    shape(h, Col(0.3, "#4e3626"))
    soot(k)


kovar_vojtech = npc(dict(coat=Col(0.55, "#8a8070"), hem=56, hem_w=15, waist_w=14, rolled=True, trousers=Col(0.38, "#55504a"),
                         apron=(Col(0.36, "#6a4a34"), 78, 28, 13), bib=90,
                         near=("a", -82, -86), near_item=tongs, far_talks=True, head=vojtech_head, wk=1.1, boot_h=8), MAN)


MED_HAIR = Col(0.72, "#c8a86a")


def medulina_head(k, md):
    r = k.hr; cy = k.hy
    hair_cap(k, MED_HAIR)
    for i, (a, col) in enumerate(((150, Col(0.85, "#e8e0f0")), (115, Col(0.7, "#d8a0b8")), (80, Col(0.8, "#f0d070")),
                                   (45, Col(0.7, "#a0b8e0")), (20, Col(0.85, "#e8e0f0")))):
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
                              front=lambda k: form([(-10, 60), (10, 60), (11, 80), (5, 88), (-5, 88), (-11, 80)], Col(0.45, "#5f7450"), sh=0.1),
                              near=("a", -60, 20), near_item=flower, far_talks=True, mood="happy",
                              hair_back=lambda k: long_back(k, MED_HAIR, 3.3), head=medulina_head, boot_h=5), WOMAN)


def kuba_head(k, md):
    r = k.hr; cy = k.hy
    bald(k, Col(0.3, "#4a3a2c"))
    r_ = r
    m = bez((r*0.2-r*0.85, cy-r*0.35), (r*0.2-r*0.5, cy-r*0.2), (r*0.2+r*0.5, cy-r*0.2), (r*0.2+r*0.85, cy-r*0.35)) + \
        bez((r*0.2+r*0.85, cy-r*0.35), (r*0.2+r*0.6, cy-r*0.65), (r*0.2+r*0.2, cy-r*0.52), (r*0.2, cy-r*0.5)) + \
        bez((r*0.2, cy-r*0.5), (r*0.2-r*0.2, cy-r*0.52), (r*0.2-r*0.6, cy-r*0.65), (r*0.2-r*0.85, cy-r*0.35))
    shape(m, Col(0.3, "#4a3a2c"), LINE*0.8)
    for sx in (-1, 1): fill(ell(r*0.2+sx*r*0.6, cy-r*0.3, r*0.16, r*0.1, 12), Col(0.6, "#d07a6a", alpha=0.35))


hostinsky_kuba = npc(dict(coat=Col(0.6, "#8f8268"), hem=50, hem_w=23, waist_w=27, sleeve=Col(0.8, "#d4ccb8"), rolled=False,
                          trousers=Col(0.36, "#4e4840"), apron=(Col(0.85, "#ddd6c4"), 66, 30, 17),
                          coat_detail=lambda k, t: [form(v, Col(0.32, "#5a4632"), sh=0.1) for v in (
                              [(-5, k.sh_y+2.4), (-k.sh_w-1.6, k.sh_y-3.5), (-22, 70), (-21, 52), (-4, 50), (-3, 70)],
                              [(5, k.sh_y+2.4), (k.sh_w+1.6, k.sh_y-3.5), (22, 70), (21, 52), (4, 50), (3, 70)])],
                          near=("a", -60, 10), near_item=mug, far_talks=True, mood="happy", head=kuba_head, wk=1.1, neck_w=4), dict(MAN, sh_w=14, hy=110, sh_y=95), 21)


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


def fabian_body_detail(k, tors):
    cone_scales(tors, -20, 20, 40, 100)
    from style3 import stroke as st
    st(tors, LINE, closed=True)


def fabian_head(k, md):
    r = k.hr; cy = k.hy
    bd = bez((-r*0.95, cy-r*0.1), (-r*1.3, cy-r*1.5), (-r*0.6, cy-r*2.6), (r*0.2, cy-r*2.8)) + \
        bez((r*0.2, cy-r*2.8), (r*0.9, cy-r*2.4), (r*1.3, cy-r*1.2), (r*0.95, cy-r*0.1)) + \
        bez((r*0.95, cy-r*0.1), (r*0.7, cy-r*0.5), (r*0.4, cy-r*0.45), (r*0.2, cy-r*0.5)) + \
        bez((r*0.2, cy-r*0.5), (-r*0.1, cy-r*0.45), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.1))
    form(bd, MOSS, sdx=-1, sdy=0.6, sh=0.12)
    for (dx, dy) in ((-0.5, -1.0), (0.1, -1.4), (0.5, -0.9), (-0.2, -2.0), (0.4, -2.2), (-0.7, -1.6)):
        stroke(ell(r*dx, cy+r*dy, r*0.14, r*0.12, 8, 30, 250), LINE*0.45, g=Col(0.3, "#4a5a30"))
    face(r*0.2, cy, r*0.95, md)
    if md not in ("talk",): pipe(r*0.35, cy-r*0.62)
    brim = bez((-r*1.9, cy+r*0.55), (-r*1.0, cy+r*0.95), (r*1.0, cy+r*0.95), (r*1.95, cy+r*0.6)) + \
        bez((r*1.95, cy+r*0.6), (r*1.2, cy+r*0.3), (-r*1.2, cy+r*0.3), (-r*1.9, cy+r*0.55))
    form(brim, FAB_HAT, sh=0.1)
    crown = [(-r*0.85, cy+r*0.75), (-r*0.7, cy+r*1.9), (r*0.75, cy+r*1.95), (r*0.9, cy+r*0.8)]
    form(crown, FAB_HAT, sdx=-1.2, sdy=0.6, sh=0.12)
    shape([(-r*0.84, cy+r*0.8), (r*0.89, cy+r*0.85), (r*0.86, cy+r*1.1), (-r*0.8, cy+r*1.05)], Col(0.4, "#6a3a2e"), LINE*0.6)
    tube(bez((-r*0.6, cy+r*1.0), (-r*1.4, cy+r*1.6), (-r*1.9, cy+r*2.6), (-r*1.8, cy+r*3.0)), 2.2, 0.8, Col(0.6, "#8a9a7a"), LINE*0.6, sh=0)


fabian = npc(dict(coat=Col(0.42, "#7a5636"), hem=50, hem_w=16, waist_w=14, coat_detail=fabian_body_detail,
                  sleeve=BARK, skin=BARK, trousers=BARK_DK, boots=Col(0.28, "#4a3a2a"), boot_h=6,
                  back=None, front=bag, near=("a", -80, -60), far_talks=True, head=fabian_head, face_late=True,
                  talk_mood="talk"), MAN)


def muzicek_draw():
    def draw(x, y, s, pose="idle"):
        k = Person(**SMALL)
        talk = pose == "talk"
        md = "talk" if talk else "think"
        if pose != "portrait": cast_shadow(x, y, 10*s, 2.4*s)
        with T(x, y, s):
            r = k.hr; cy = k.hy
            far = ("a", 130, 100) if talk else ("a", -110, -95)
            arm(k, -1, far, Col(0.42, "#6a5a40"), BARK, open_=talk, hr=2.3)
            legs(k, "stand", BARK_DK, Col(0.3, "#4a3a2a"), boot_h=5, wk=0.8, kx=0.8)
            tors = torso_pts(k, 12, 11, waist_w=10.5, collar=3)
            form(tors, Col(0.42, "#6a5a40"), sdx=-1.8, sdy=1, sh=0.14)
            arm(k, 1, ("a", -60, -20) if not talk else ("a", -20, 40), Col(0.42, "#6a5a40"), BARK, open_=talk, hr=2.3)
            head(k, md, BARK, do_face=False, neck_w=2.4)
            for (x0, y0, x1, y1) in ((-0.7, 0.6, -0.5, 0.1), (0.75, 0.5, 0.85, 0.0), (-0.3, -0.2, -0.45, -0.4)):
                stroke([(r*x0, cy+r*y0), (r*x1, cy+r*y1)], LINE*0.5, g=BARK_DK)
            face(r*0.2, cy, r*0.95, md)
            bd = bez((-r*0.95, cy-r*0.15), (-r*1.2, cy-r*2.0), (-r*0.9, cy-r*3.6), (-r*0.3, cy-r*4.15)) + \
                bez((-r*0.3, cy-r*4.15), (r*0.3, cy-r*4.25), (r*1.0, cy-r*3.8), (r*1.15, cy-r*2.6)) + \
                bez((r*1.15, cy-r*2.6), (r*1.2, cy-r*1.4), (r*1.05, cy-r*0.6), (r*0.95, cy-r*0.15)) + \
                bez((r*0.95, cy-r*0.15), (r*0.7, cy-r*0.5), (r*0.45, cy-r*0.48), (r*0.3, cy-r*0.5)) + \
                bez((r*0.3, cy-r*0.5), (-r*0.1, cy-r*0.48), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.15))
            form(bd, WHITE_HAIR, sdx=-1, sdy=0.4, sh=0.08)
            for xx in (-0.5, -0.1, 0.3, 0.7):
                stroke(bez((r*xx, cy-r*0.9), (r*xx*1.1, cy-r*1.8), (r*xx, cy-r*2.8), (r*xx*0.8, cy-r*3.7)), LINE*0.45, g=GREY_LINE)
            if talk: shape(ell(r*0.2, cy-r*0.65, r*0.13, r*0.1, 12), Col(0.25, "#4a2a20"), LINE*0.6)
            moustache(k, WHITE_HAIR, w=0.6)
            hat = bez((-r*1.1, cy+r*0.3), (-r*0.8, cy+r*1.4), (-r*0.1, cy+r*2.4), (r*0.3, cy+r*2.6)) + \
                bez((r*0.3, cy+r*2.6), (r*0.5, cy+r*1.6), (r*0.9, cy+r*1.0), (r*1.1, cy+r*0.35)) + \
                bez((r*1.1, cy+r*0.35), (r*0.4, cy+r*0.5), (-r*0.4, cy+r*0.5), (-r*1.1, cy+r*0.3))
            form(hat, MOSS, sdx=-1, sdy=0.8, sh=0.14)
            for (dx, dy) in ((-0.5, 0.8), (0.1, 1.3), (0.5, 0.7), (-0.1, 1.9)):
                stroke(ell(r*dx, cy+r*dy, r*0.12, r*0.1, 8, 30, 250), LINE*0.4, g=Col(0.3, "#4a5a30"))
    draw.K = SMALL
    return draw


tremsinsky_muzicek = muzicek_draw()


# ------------------------------------------------------------------ Jáchymov
def krystof_head(k, md):
    r = k.hr; cy = k.hy
    beard(k, Col(0.38, "#6a4a30"), 1.25)
    face(r*0.2, cy, r*0.95, md)
    moustache(k, Col(0.38, "#6a4a30"))
    cap = bez((-r*1.08, cy+r*0.35), (-r*1.2, cy+r*1.5), (r*1.2, cy+r*1.5), (r*1.08, cy+r*0.35)) + \
        bez((r*1.08, cy+r*0.35), (r*0.4, cy+r*0.5), (-r*0.4, cy+r*0.5), (-r*1.08, cy+r*0.35))
    form(cap, Col(0.38, "#5e4e3e"), sh=0.12)
    shape(rrect(-r*1.12, cy+r*0.28, r*2.24, r*0.3, 0.8), LEATHER, LINE*0.7)


kovar_krystof = npc(dict(coat=Col(0.45, "#5e6670"), hem=56, hem_w=15, waist_w=14.5, rolled=True, trousers=Col(0.36, "#4a4640"),
                         apron=(LEATHER, 76, 30, 13), belt=(Col(0.3, "#3e2e24"), 58), front=lambda k: pouch(10, 57),
                         near=("a", -55, 15), near_item=coin, far_talks=True, head=krystof_head, face_late=True,
                         far_item=lambda H, fa: hammer(H, fa, -100, 14), wk=1.1, boot_h=8), MAN)


AG_ROBE = Col(0.34, "#6a3438")
FUR = Col(0.45, "#7a6248")


def agricola_head(k, md):
    r = k.hr; cy = k.hy
    for sx in (-1, 1):
        shape(bez((sx*r*0.98, cy+r*0.45), (sx*r*1.1, cy+r*0.1), (sx*r*1.02, cy-r*0.2), (sx*r*0.9, cy-r*0.3)) +
              [(sx*r*0.8, cy+r*0.4)], Col(0.35, "#5a4636"), LINE*0.7)
    beard(k, Col(0.35, "#5a4636"), 1.75, Col(0.25, "#3a2e26"))
    face(r*0.2, cy, r*0.95, md)
    moustache(k, Col(0.35, "#5a4636"))
    cap = bez((-r*1.35, cy+r*0.6), (-r*1.6, cy+r*1.2), (-r*0.6, cy+r*1.55), (r*0.6, cy+r*1.5)) + \
        bez((r*0.6, cy+r*1.5), (r*1.6, cy+r*1.4), (r*1.5, cy+r*0.8), (r*1.2, cy+r*0.6)) + \
        bez((r*1.2, cy+r*0.6), (r*0.4, cy+r*0.45), (-r*0.4, cy+r*0.45), (-r*1.35, cy+r*0.6))
    form(cap, Col(0.22, "#34303a"), sdx=-1, sdy=0.6, sh=0.12)
    stroke(bez((-r*1.2, cy+r*0.62), (-r*0.4, cy+r*0.55), (r*0.4, cy+r*0.55), (r*1.15, cy+r*0.66)), LINE*0.6, g=BRASS)


def agricola_detail(k, tors):
    for sx in (-1, 1):
        f = [(sx*4, k.sh_y+3), (sx*(k.sh_w+2.4), k.sh_y+0.5), (sx*(k.sh_w+2.6), k.sh_y-7), (sx*8, 60), (sx*4.5, 8), (sx*1.2, 8), (sx*1.5, 60)]
        form(f, FUR, sdx=-1, sdy=0.5, sh=0.1)
        for yy in range(16, 90, 9): stroke([(sx*2.5, yy), (sx*3.6, yy-2)], LINE*0.4, g=Col(0.3, "#4e3e2e"))
    form([(-3.5, k.sh_y+2.5), (3.5, k.sh_y+2.5), (2.5, 70), (-2.5, 70)], Col(0.25, "#2e2a30"), sh=0)
    stroke(bez((-3, k.sh_y+1), (-1, 82), (1, 82), (3, k.sh_y+1)), LINE*0.6, g=BRASS)


lekarnik_agricola = npc(dict(coat=AG_ROBE, hem=6, hem_w=16.5, waist_w=14.5, coat_detail=agricola_detail, cuff=FUR,
                             near=("a", -55, 20), near_item=flask, far_talks=True, head=agricola_head, face_late=True,
                             boot_h=5), MAN, 17)


def rozina_head(k, md):
    r = k.hr; cy = k.hy
    hair_cap(k, Col(0.36, "#5e3e2e"))
    for (x0, y0, x1, y1) in ((0.6, 0.55, 1.0, -0.3), (-0.2, 0.62, -0.05, 0.25), (-0.95, 0.2, -1.15, -0.6)):
        stroke(bez((r*x0, cy+r*y0), (r*(x0+x1)/2+r*0.1, cy+r*(y0+y1)/2), (r*x1, cy+r*y1+r*0.1), (r*x1, cy+r*y1)), LINE*0.8, g=Col(0.36, "#5e3e2e"))
    for sx in (-1, 1):
        stroke(bez((r*0.2+sx*r*0.38-r*0.15, cy-r*0.12), (r*0.2+sx*r*0.38, cy-r*0.2), (r*0.2+sx*r*0.38+r*0.15, cy-r*0.12), (r*0.2+sx*r*0.38+r*0.18, cy-r*0.1)), LINE*0.4, g=Col(0.4, "#8a6a6a"))


def rag(H, fa):
    r_ = [(H[0]-2, H[1]-1), (H[0]+3, H[1]-1.5)] + bez((H[0]+3, H[1]-1.5), (H[0]+4, H[1]-6), (H[0]+2, H[1]-9), (H[0]+3, H[1]-12)) + \
        [(H[0]-1, H[1]-11)] + bez((H[0]-1, H[1]-11), (H[0]-2.5, H[1]-7), (H[0]-1, H[1]-4), (H[0]-2, H[1]-1))
    shape(r_, Col(0.75, "#c8c0ac"), LINE*0.7)


senkyrka_rozina = npc(dict(coat=Col(0.72, "#b8ae98"), hem=60, hem_w=12.5, waist_w=11, rolled=True,
                           skirt=(Col(0.4, "#4e5a6a"), 62, 6, 12.5, 18), apron=(Col(0.78, "#cfc8b4"), 63, 20, 11),
                           belt=(Col(0.32, "#3e3a3a"), 63), belt_w=12, mood="sleepy", talk_mood="sad",
                           near=("a", -92, -100), near_item=rag, far_talks=True, head=rozina_head,
                           hair_back=lambda k: long_back(k, Col(0.36, "#5e3e2e"), 1.6, 1.1), boot_h=5), WOMAN)


# ------------------------------------------------------------------ the dead
def matej_head(k, md):
    r = k.hr; cy = k.hy
    beard(k, GHOST_DK, 1.3)
    face(r*0.2, cy, r*0.95, md)
    moustache(k, GHOST_DK)
    cap = bez((-r*1.06, cy+r*0.55), (-r*1.12, cy+r*1.7), (r*1.12, cy+r*1.7), (r*1.06, cy+r*0.55)) + \
        bez((r*1.06, cy+r*0.55), (r*0.4, cy+r*0.68), (-r*0.4, cy+r*0.68), (-r*1.06, cy+r*0.55))
    form(cap, GHOST_DK, sdx=-1.5, sdy=1)
    shape(rrect(-r*1.1, cy+r*0.45, r*2.2, r*0.3, 0.8), GHOST_DK, LINE*0.8)


def dead_lamp(H, fa):
    kahan(H[0], H[1]-1, 1.15, lit=False, body=GHOST_DK)


predak_matej = npc(dict(coat=GHOST, hem=52, hem_w=16, waist_w=15, sleeve=GHOST, skin=GHOST_SKIN, trousers=GHOST_DK,
                        boots=GHOST_DK, belt=(GHOST_DK, 58), cuff=GHOST_DK, mood="sad", talk_mood="talk",
                        coat_detail=lambda k, t: [dot(-0.6, by, 0.8, GHOST_DK) for by in (90, 82, 74, 66)],
                        near=("a", -60, 5), near_item=dead_lamp, far_talks=True, head=matej_head, face_late=True,
                        wk=1.1, boot_h=8), MAN, alpha=0.78)

ANI_HAIR = Col(0.65, "#8fa8bc")


def anicka_hair_back(k):
    long_back(k, ANI_HAIR, 3.6, 1.15)


def anicka_head(k, md):
    r = k.hr; cy = k.hy
    hair_cap(k, ANI_HAIR, low=-0.6)
    for sx in (-1, 1):
        stroke(bez((sx*r*1.0, cy-r*0.2), (sx*r*1.1, cy-r*1.0), (sx*r*1.05, cy-r*2.0), (sx*r*1.1, cy-r*2.8)), LINE*0.6, g=Col(0.5, "#6a8aa0"))
    for (dx, dy) in ((-1.15, -3.4), (1.1, -3.1), (-0.3, -3.9)):
        shape(bez((r*dx, cy+r*dy+1.6), (r*dx-0.9, cy+r*dy), (r*dx+0.9, cy+r*dy), (r*dx, cy+r*dy+1.6)), Col(0.85, "#d8ecff"), LINE*0.4)


def cup_held(H, fa):
    teacup(H[0]+1.5, H[1]+3.5, Col(0.9, "#e6eef6"))


anicka = npc(dict(coat=GHOST, hem=40, hem_w=13, waist_w=10.5, sleeve=GHOST, skin=GHOST_SKIN, trousers=GHOST_SKIN,
                  boots=GHOST_DK, boot_h=4, skirt=(GHOST, 46, 22, 10.5, 15), mood="sad", talk_mood="talk",
                  near=("k", 9, 52, -1), near_item=cup_held, far=("k", 5, 50, -1), far_talks=False,
                  near_talk=("k", 10, 56, -1), hair_back=anicka_hair_back, head=anicka_head, kx=0.8, neck_w=2.4), GIRL, 12,
             alpha=0.78)

FERRY = Col(0.32, "#4a4e58")
FERRY_DK = Col(0.2, "#2e3038")


def prevoznik_back(k):
    r = k.hr; cy = k.hy
    hood = bez((-r*1.45, cy-r*1.4), (-r*1.9, cy+r*0.8), (-r*1.0, cy+r*2.0), (r*0.3, cy+r*1.9)) + \
        bez((r*0.3, cy+r*1.9), (r*1.4, cy+r*1.7), (r*1.7, cy+r*0.6), (r*1.5, cy-r*1.3))
    form(hood, FERRY, sdx=-1.5, sdy=1, sh=0.15)


def prevoznik_head(k, md):
    r = k.hr; cy = k.hy
    fill(ell(r*0.15, cy+r*0.2, r*1.05, r*0.9, 30), Col(0.1, "#141418", alpha=0.55))
    hf = bez((-r*1.3, cy-r*1.0), (-r*1.5, cy+r*1.0), (-r*0.6, cy+r*1.7), (r*0.25, cy+r*1.65)) + \
        bez((r*0.25, cy+r*1.65), (r*1.1, cy+r*1.6), (r*1.5, cy+r*1.0), (r*1.35, cy-r*0.7)) + \
        bez((r*1.35, cy-r*0.7), (r*1.3, cy+r*0.5), (r*0.9, cy+r*0.95), (r*0.25, cy+r*0.98)) + \
        bez((r*0.25, cy+r*0.98), (-r*0.6, cy+r*1.0), (-r*1.15, cy+r*0.5), (-r*1.1, cy-r*1.0))
    form(hf, FERRY, sdx=-1, sdy=0.8, sh=0.14)
    beard(k, Col(0.55, "#8a8680"), 1.9, Col(0.4, "#6a6660"))
    face(r*0.2, cy, r*0.95, md)
    moustache(k, Col(0.55, "#8a8680"))


def ferry_pole(H, fa):
    pole(H, 46, 2)


prevoznik = npc(dict(coat=FERRY, hem=6, hem_w=18, waist_w=15.5, sleeve=FERRY, cuff=FERRY_DK, back=prevoznik_back,
                     belt=(Col(0.4, "#6a5a44"), 60), mood="think",
                     near=("k", 26, 74, -1), near_item=ferry_pole, after_hand=lambda H, fa: None, far_talks=True,
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
        sp += [(name, 200, 240, sprite(fn, "idle")), (f"{name}_talk", 200, 240, sprite(fn, "talk"))]
        pt.append((name, 256, 256, port(fn, glow)))
    sp.append(("permonik_grin", 200, 240, sprite(permonik_grin, "idle")))
    pt.append(("permonik_grin", 256, 256, port(permonik_grin, None)))
    return {"sprites/npcs": sp, "portraits": pt}


if __name__ == "__main__":
    common.run(jobs())
