import math, random
import lib
from lib import G, ell, bez, rrect, resample
import palette as P
from style3 import *
from style3 import C, _SC, Kid, draw_arm, draw_legs, head_outline, face, notch, hand

FUR = P.FUR; FACE = P.FUR_FACE

def torch(x, y, ang):
    with T(x, y, 1, rot=ang):
        shape([(-2, -1.4), (6, -1.4), (6, 1.4), (-2, 1.4)], P.TORCH_BODY, LINE*0.8)
        shape([(6, -2.2), (9, -2.2), (9, 2.2), (6, 2.2)], P.TORCH_HEAD, LINE*0.8)
        fill([(9, -1.8), (9.8, -1.8), (9.8, 1.8), (9, 1.8)], P.TORCH_LENS)

# ------------------------------------------------------------------ adults & Tonda
class Person(Kid):
    def __init__(self, **kw):
        self.young = False
        for k_, v in kw.items(): setattr(self, k_, v)

BABI = dict(H=112, hr=10.4, hy=101.2, sh_y=86.5, sh_w=11.5, hip=50, knee=27, ankle=5, leg_w=(6.8, 5.2), arm_w=(6.4, 5.8), up=17, fo=15.5)
DEDA = dict(H=126, hr=10.6, hy=114.8, sh_y=99.5, sh_w=13.5, hip=59, knee=31.5, ankle=5, leg_w=(8, 6.2), arm_w=(7, 6.2), up=20, fo=18)
TONDA = dict(H=104, hr=9.9, hy=94, sh_y=79.5, sh_w=10.2, hip=47, knee=25, ankle=5, leg_w=(6.4, 4.8), arm_w=(5.6, 4.8), up=15.5, fo=14.5)

def _neck(k, w=2.8):
    shape([(-w, k.hy-k.hr+2), (w, k.hy-k.hr+2), (w+0.3, k.sh_y+0.5), (-w-0.3, k.sh_y+0.5)], P.SKIN, 0)
    stroke([(-w, k.hy-k.hr+2.5), (-w-0.3, k.sh_y+0.8)], LINE*0.8); stroke([(w, k.hy-k.hr+2.5), (w+0.3, k.sh_y+0.8)], LINE*0.8)

def babicka(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True, legs="stand"):
    k = Person(**BABI)
    if shadow: cast_shadow(x, y, 17*s, 2.8*s)
    CARD = P.CARDIGAN; DRESS = P.DRESS
    with T(x, y, s, flip):
        draw_legs(k, legs, P.STOCKINGS, boots=P.BABI_SHOES, boot_top=k.ankle+3)
        draw_arm(k, -1, left, CARD)
        skirt = [(-12.5, 60), (12.5, 60)] + bez((12.5, 60), (15, 45), (17, 32), (18, 20)) + \
                bez((18, 20), (6, 18), (-6, 18), (-18, 20)) + bez((-18, 20), (-17, 32), (-15, 45), (-12.5, 60))
        fill(skirt, DRESS)
        C.saveState(); C.clipPath(poly(skirt), stroke=0, fill=0)
        for yy in range(22, 60, 6):
            for xx in range(-18, 19, 6):
                dot(xx + (3 if (yy//6) % 2 else 0), yy, 0.9, 0.95)
        C.restoreState()
        offset_shadow(skirt, -2.5, 1, 0.12); stroke(skirt, LINE, closed=True)
        # cardigan
        card = bez((-5, k.sh_y+2.5), (-9, k.sh_y+2.2), (-k.sh_w-1.2, k.sh_y+0.5), (-k.sh_w-1.8, k.sh_y-4)) + \
               bez((-k.sh_w-1.8, k.sh_y-4), (-14, 70), (-14.5, 60), (-14, 52)) + [(14, 52)] + \
               bez((14, 52), (14.5, 60), (14, 70), (k.sh_w+1.8, k.sh_y-4)) + \
               bez((k.sh_w+1.8, k.sh_y-4), (k.sh_w+1.2, k.sh_y+0.5), (9, k.sh_y+2.2), (5, k.sh_y+2.5))
        form(card, CARD, sdx=-2.4, sdy=1.2)
        vee = [(-4.5, k.sh_y+2.4), (4.5, k.sh_y+2.4), (1, 66), (-1, 66)]
        shape(vee, DRESS, LINE*0.8)
        for by in (62, 57): shape(ell(-2.2, by, 1.0, 1.0, 12), P.CARD_BUTTON, LINE*0.6)
        # apron
        ap = [(-10, 60), (10, 60)] + bez((10, 60), (11.5, 45), (12, 33), (11.5, 24)) + \
             bez((11.5, 24), (4, 22.5), (-4, 22.5), (-11.5, 24)) + bez((-11.5, 24), (-12, 33), (-11.5, 45), (-10, 60))
        form(ap, 1.0, sdx=-2, sdy=0.8, sh=0.08)
        pk = rrect(-4.5, 36, 9, 7, 1.5); shape(pk, 1.0, LINE*0.7)
        shape([(-11.5, 58.5), (11.5, 58.5), (11.5, 61.5), (-11.5, 61.5)], 0.95, LINE*0.8)
        h, fa = draw_arm(k, 1, right, CARD)
        if item: item(*h)
        _neck(k)
        ho = head_outline(k); shape(ho, P.SKIN)
        face(0, k.hy, k.hr, mood, look)
        # wrinkles at eyes
        for sx in (-1, 1):
            stroke([(sx*k.hr*0.58, k.hy-k.hr*0.05), (sx*k.hr*0.7, k.hy-k.hr*0.1)], LINE*0.5)
        # glasses
        for sx in (-1, 1):
            stroke(ell(sx*k.hr*0.4, k.hy-k.hr*0.02, k.hr*0.24, k.hr*0.21, 30), LINE*0.8, closed=True)
        stroke([(-k.hr*0.16, k.hy), (k.hr*0.16, k.hy)], LINE*0.7)
        # hair: grey, pulled back + bun
        r = k.hr; cy = k.hy
        shape(ell(0, cy+r*1.25, r*0.5, r*0.4, 24), P.BABI_HAIR, LINE)
        stroke(ell(0, cy+r*1.25, r*0.25, r*0.2, 12, 20, 300), LINE*0.5)
        cap = bez((-r*1.0, cy+r*0.1), (-r*1.1, cy+r*1.15), (r*1.1, cy+r*1.15), (r*1.0, cy+r*0.1)) + \
              bez((r*1.0, cy+r*0.1), (r*0.7, cy+r*0.62), (r*0.3, cy+r*0.72), (0, cy+r*0.7)) + \
              bez((0, cy+r*0.7), (-r*0.3, cy+r*0.72), (-r*0.7, cy+r*0.62), (-r*1.0, cy+r*0.1))
        shape(cap, P.BABI_HAIR)
        for xx in (-0.55, -0.2, 0.2, 0.55):
            stroke(bez((r*xx*0.9, cy+r*0.75), (r*xx, cy+r*0.9), (r*xx*0.95, cy+r*1.0), (r*xx*0.7, cy+r*1.08)), LINE*0.45, g=P.GREY_HAIR_LINE)

def deda(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True, legs="stand"):
    k = Person(**DEDA)
    if shadow: cast_shadow(x, y, 18*s, 3*s)
    SHIRT = P.SHIRT; VEST = P.VEST; TR = P.TROUSERS
    with T(x, y, s, flip):
        draw_legs(k, legs, TR, boots=P.DEDA_BOOTS, boot_top=k.ankle+6)
        draw_arm(k, -1, left, SHIRT)
        tors = bez((-5.5, k.sh_y+2.8), (-10, k.sh_y+2.5), (-k.sh_w-1.3, k.sh_y+0.5), (-k.sh_w-1.8, k.sh_y-4)) + \
               bez((-k.sh_w-1.8, k.sh_y-4), (-15.5, 82), (-15.5, 70), (-15, 57)) + [(15, 57)] + \
               bez((15, 57), (15.5, 70), (15.5, 82), (k.sh_w+1.8, k.sh_y-4)) + \
               bez((k.sh_w+1.8, k.sh_y-4), (k.sh_w+1.3, k.sh_y+0.5), (10, k.sh_y+2.5), (5.5, k.sh_y+2.8))
        fill(tors, SHIRT)
        C.saveState(); C.clipPath(poly(tors), stroke=0, fill=0)
        for g_ in range(-18, 19, 5):
            fill([(g_, 50), (g_+1.6, 50), (g_+1.6, 110), (g_, 110)], P.SHIRT_CHECK)
        for g_ in range(55, 105, 5):
            fill([(-20, g_), (20, g_), (20, g_+1.6), (-20, g_+1.6)], P.SHIRT_CHECK)
        C.restoreState()
        stroke(tors, LINE, closed=True)
        for sx in (-1, 1):
            vest = [(sx*6, k.sh_y+2.4), (sx*(k.sh_w+1.6), k.sh_y-3.5), (sx*15.6, 70), (sx*15.2, 56), (sx*3, 55), (sx*2.2, 70), (sx*3.5, 88)]
            form(vest, VEST, sdx=-2, sdy=1, sh=0.1)
        for by in (84, 76, 68, 60): shape(ell(-3.3, by, 0.9, 0.9, 10), P.VEST_BUTTON, LINE*0.5)
        stroke(bez((-3, 65), (-6, 67), (-9, 66), (-11, 64)), LINE*0.6, g=P.WATCH_CHAIN)
        shape([(-15, 55), (15, 55), (15, 58), (-15, 58)], P.BELT, LINE*0.8)
        h, fa = draw_arm(k, 1, right, SHIRT)
        if item: item(*h)
        _neck(k, 3.2)
        r = k.hr; cy = k.hy
        for sx in (-1, 1): shape(ell(sx*r*0.98, cy-r*0.05, r*0.2, r*0.3, 14), P.SKIN, LINE*0.8)
        ho = head_outline(k); shape(ho, P.SKIN)
        # grey hair at sides
        for sx in (-1, 1):
            shape(bez((sx*r*0.98, cy+r*0.45), (sx*r*1.08, cy+r*0.1), (sx*r*1.02, cy-r*0.2), (sx*r*0.9, cy-r*0.3)) + [(sx*r*0.8, cy+r*0.4)], P.DEDA_SIDE_HAIR, LINE*0.7)
        # beard
        bd = bez((-r*0.95, cy-r*0.15), (-r*1.0, cy-r*1.2), (-r*0.4, cy-r*1.55), (0, cy-r*1.55)) + \
             bez((0, cy-r*1.55), (r*0.4, cy-r*1.55), (r*1.0, cy-r*1.2), (r*0.95, cy-r*0.15)) + \
             bez((r*0.95, cy-r*0.15), (r*0.6, cy-r*0.5), (r*0.3, cy-r*0.48), (0, cy-r*0.5)) + \
             bez((0, cy-r*0.5), (-r*0.3, cy-r*0.48), (-r*0.6, cy-r*0.5), (-r*0.95, cy-r*0.15))
        shape(bd, P.BEARD)
        for xx in (-0.5, -0.15, 0.2, 0.55):
            stroke(bez((r*xx, cy-r*0.8), (r*xx*1.05, cy-r*1.0), (r*xx, cy-r*1.2), (r*xx*0.9, cy-r*1.35)), LINE*0.45, g=P.GREY_HAIR_LINE)
        face(0, k.hy, k.hr, mood if mood not in ("grin",) else "happy", look)
        # moustache over mouth
        mst = bez((-r*0.5, cy-r*0.5), (-r*0.3, cy-r*0.3), (r*0.3, cy-r*0.3), (r*0.5, cy-r*0.5)) + \
              bez((r*0.5, cy-r*0.5), (r*0.2, cy-r*0.62), (-r*0.2, cy-r*0.62), (-r*0.5, cy-r*0.5))
        shape(mst, P.BEARD, LINE*0.8)
        if mood in ("grin", "laugh", "surprised"):
            shape(ell(0, cy-r*0.72, r*0.14, r*0.1, 12), P.MOUTH, LINE*0.6)
        # bushy brows
        for sx in (-1, 1):
            shape(ell(sx*r*0.4, cy+r*0.33, r*0.22, r*0.08, 12), P.DEDA_BROWS, LINE*0.6)
        # flat cap
        capb = bez((-r*1.05, cy+r*0.35), (-r*1.15, cy+r*1.25), (r*0.5, cy+r*1.45), (r*1.05, cy+r*0.65)) + \
               [(r*1.6, cy+r*0.45), (r*1.55, cy+r*0.3), (r*1.0, cy+r*0.35)]
        form(capb, P.FLAT_CAP, sdx=-1.5, sdy=1)
        stroke(bez((-r*0.2, cy+r*1.3), (r*0.2, cy+r*1.0), (r*0.6, cy+r*0.8), (r*1.0, cy+r*0.62)), LINE*0.6)

def tonda(x, y, s=1.0, flip=False, left="down", right="down", mood="happy", look=(0, 0), item=None, shadow=True, legs="stand"):
    k = Person(**TONDA)
    if shadow: cast_shadow(x, y, 15*s, 2.6*s)
    HOOD = P.HOODIE; JEANS = P.JEANS
    with T(x, y, s, flip):
        draw_legs(k, legs, JEANS, boots=1.0, boot_top=k.ankle+2.5)
        draw_arm(k, -1, left, HOOD)
        hood = bez((-8, k.sh_y+3), (-10, k.sh_y+9), (10, k.sh_y+9), (8, k.sh_y+3)) + [(0, k.sh_y+1)]
        shape(hood, HOOD)
        tors = bez((-4.5, k.sh_y+2.6), (-8, k.sh_y+2.4), (-k.sh_w-1.1, k.sh_y+0.5), (-k.sh_w-1.5, k.sh_y-3.5)) + \
               bez((-k.sh_w-1.5, k.sh_y-3.5), (-12.5, 62), (-12.8, 52), (-12.5, 44)) + [(12.5, 44)] + \
               bez((12.5, 44), (12.8, 52), (12.5, 62), (k.sh_w+1.5, k.sh_y-3.5)) + \
               bez((k.sh_w+1.5, k.sh_y-3.5), (k.sh_w+1.1, k.sh_y+0.5), (8, k.sh_y+2.4), (4.5, k.sh_y+2.6))
        form(tors, HOOD, sdx=-2, sdy=1)
        shape([(-12.5, 44), (12.5, 44), (12.5, 47.5), (-12.5, 47.5)], HOOD, LINE*0.8)
        pk = [(-7, 58), (7, 58), (9, 50), (-9, 50)]
        stroke(pk, LINE*0.7, closed=True)
        for sx in (-1, 1):
            stroke([(sx*2, k.sh_y+1.5), (sx*2.5, k.sh_y-8)], LINE*0.7); dot(sx*2.5, k.sh_y-8.5, 0.6, 0.2)
        # star on hoodie
        pts = []
        for i in range(10):
            a = math.pi/2 + i*math.pi/5; rr = 3.4 if i % 2 == 0 else 1.4
            pts.append((0+math.cos(a)*rr, 66+math.sin(a)*rr))
        shape(pts, P.HOODIE_STAR, LINE*0.6)
        h, fa = draw_arm(k, 1, right, HOOD)
        if item: item(*h)
        _neck(k, 2.6)
        r = k.hr; cy = k.hy
        for sx in (-1, 1): shape(ell(sx*r*0.98, cy-r*0.05, r*0.2, r*0.3, 14), P.SKIN, LINE*0.8)
        ho = head_outline(k); shape(ho, P.SKIN)
        face(0, k.hy, k.hr, mood, look, freckles=False)
        for sx in (-1, 1):
            for dx, dy in ((-0.08, 0.02), (0.03, 0.06), (0.1, -0.02)):
                dot(sx*(r*0.5+dx*r), cy-r*0.25+dy*r, r*0.022, P.FRECKLE)
        hair = [(-r*1.02, cy+r*0.1), (-r*1.2, cy+r*0.55), (-r*0.9, cy+r*0.6), (-r*1.05, cy+r*1.05), (-r*0.55, cy+r*0.92),
                (-r*0.5, cy+r*1.35), (-r*0.1, cy+r*1.02), (r*0.25, cy+r*1.4), (r*0.4, cy+r*1.0), (r*0.9, cy+r*1.2),
                (r*0.85, cy+r*0.75), (r*1.2, cy+r*0.6), (r*1.02, cy+r*0.1), (r*0.7, cy+r*0.5), (r*0.35, cy+r*0.4),
                (0, cy+r*0.58), (-r*0.35, cy+r*0.42), (-r*0.7, cy+r*0.55)]
        shape(hair, P.TONDA_HAIR)

# ------------------------------------------------------------------ animals
def cat(x, y, s=1.0, flip=False, mood="sleepy"):
    with T(x, y, s, flip):
        tube(bez((10, 3), (24, 1), (28, 10), (22, 18), 12), 4.4, 3.4, P.CAT, sh=0)
        body = bez((-12, 0), (-15, 14), (-10, 26), (0, 28)) + bez((0, 28), (10, 26), (15, 14), (12, 0))
        form(body, P.CAT, sdx=-2, sdy=1)
        for k_ in range(3):
            stroke(bez((-12+k_*2, 10+k_*5), (-8, 11+k_*5), (-5, 10+k_*5), (-3, 9+k_*5)), LINE*0.9)
        for sx in (-1, 1): shape(ell(sx*5, 1, 4, 2.5, 14), P.CAT)
        shape(ell(0, 33, 11, 9.5, 36), P.CAT)
        for sx in (-1, 1):
            shape([(sx*4, 40), (sx*10, 46.5), (sx*10.5, 37)], P.CAT)
            fill([(sx*6, 40.5), (sx*9.3, 44.5), (sx*9.5, 39.5)], P.CAT_EAR)
        fill(ell(0, 28.5, 5, 3.5, 16), P.CAT_MUZZLE)
        for sx in (-1, 1):
            if mood == "sleepy":
                stroke(bez((sx*4.5-1.8, 34), (sx*4.5-0.6, 33), (sx*4.5+0.6, 33), (sx*4.5+1.8, 34)), LINE*0.9)
            else:
                fill(ell(sx*4.5, 34, 1.4, 1.8, 12), 0.0); dot(sx*4.5+0.4, 34.6, 0.5, 1.0)
        fill([(-1.2, 31), (1.2, 31), (0, 29.8)], P.CAT_NOSE)
        for sx in (-1, 1):
            for k_ in (-1, 0, 1): stroke([(sx*4, 30+k_*0.8), (sx*12, 31+k_*2)], LINE*0.4)
        for k_ in (-3, 0, 3): stroke([(k_, 42), (k_, 38.5)], LINE*0.8)

def magpie(x, y, s=1.0, flip=False, item=None):
    with T(x, y, s, flip):
        shape([(-8, 6), (-30, 0), (-31, 3.5), (-10, 10)], P.MAGPIE_BLACK)
        shape(ell(0, 10, 11, 7, 30, rot=15), P.MAGPIE_BLACK)
        shape(ell(2, 7, 7, 4, 20, rot=10), 1.0, LINE*0.8)
        shape(ell(-3, 12, 7, 3, 20, rot=15), 0.95, LINE*0.8)
        shape(ell(10, 19, 5.5, 5, 24), P.MAGPIE_BLACK)
        shape([(15, 20), (21, 19), (15, 17.5)], 0.25, LINE*0.8)
        dot(12, 20.5, 1.3, 1.0); dot(12.3, 20.6, 0.7, 0)
        stroke([(-1, 3), (-1, -3)], LINE); stroke([(3, 3), (3, -3)], LINE)
        if item: item(21, 18)

def spoon(x, y):
    with T(x, y, 0.8, rot=-20):
        shape(ell(6, 0, 4, 2.6, 16), 0.92, LINE*0.8); stroke([(-8, 0), (2, 0)], LINE*1.4)

def dormouse(x, y, s=1.0, flip=False, mood="happy", tail=True):
    DG = P.DORMOUSE
    with T(x, y, s, flip):
        if tail:
            tl = bez((-6, 5), (-22, 0), (-28, 18), (-17, 26))
            pts = resample(tl, 1.0); n = len(pts)
            left, right = [], []
            for i in range(n):
                a = pts[max(0, i-1)]; b = pts[min(n-1, i+1)]
                dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
                w = (4 + 6*i/(n-1))/2
                left.append((pts[i][0]-dy/L*w, pts[i][1]+dx/L*w)); right.append((pts[i][0]+dy/L*w, pts[i][1]-dx/L*w))
            outline = notch(left, 0.5, 6) + ell(pts[-1][0], pts[-1][1], 5, 5, 10, 60, 240) + list(reversed(notch(right, 0.5, 6)))
            shape(outline, DG)
        shape(ell(0, 9, 10, 9, 36), DG)
        fill(ell(2, 6, 6, 5.5, 20), P.DORMOUSE_BELLY)
        for sx in (-1, 1):
            shape(ell(sx*6+2, 26, 4, 4.3, 20), DG); fill(ell(sx*6+2, 26, 2.3, 2.6, 14), P.DORMOUSE_EAR)
        shape(ell(2, 19, 8.5, 7.5, 30), DG)
        fill(ell(4, 16, 4, 3, 16), P.DORMOUSE_BELLY)
        for sx in (-1, 1):
            if mood == "sleepy":
                stroke(bez((2+sx*3.6-1.5, 20), (2+sx*3.6-0.5, 19.2), (2+sx*3.6+0.5, 19.2), (2+sx*3.6+1.5, 20)), LINE*0.8)
            else:
                fill(ell(2+sx*3.6, 20, 1.9, 2.3, 14), 0.0); dot(2+sx*3.6+0.6, 20.8, 0.7, 1.0)
        dot(4.5, 16.5, 1.1, 0.1)
        for sx in (-1, 1):
            for k_ in (-1, 1): stroke([(4+sx*1.5, 16+k_*0.4), (4+sx*7, 17+k_*1.5)], LINE*0.35)
        for px in (-1, 6): shape(ell(px, 10, 2, 1.6, 12), P.DORMOUSE_BELLY, LINE*0.7)

# ------------------------------------------------------------------ props
def key(x, y, s=1.0, rot=0, tag=True):
    with T(x, y, s, rot=rot):
        shape(ell(0, 0, 7, 7, 30), P.BRASS)
        shape(ell(0, 0, 3.4, 3.4, 20), 1.0, LINE*0.8)
        shape([(6, -1.8), (30, -1.8), (30, 1.8), (6, 1.8)], P.BRASS)
        shape([(24, -1.8), (24, -7), (27, -7), (27, -4.5), (29, -4.5), (29, -7), (30.5, -7), (30.5, -1.8)], P.BRASS)
        if tag:
            stroke(bez((-4, 5), (-8, 12), (-10, 14), (-12, 16)), LINE*0.7)
            with T(-17, 20, rot=15):
                shape([(-6, -6), (6, -6), (8, 0), (6, 6), (-6, 6)], P.TAG)
                shape(ell(5, 0, 1, 1, 10), 1.0, LINE*0.5)
                star(-1, 0, 3.4, P.TAG_STAR)

def star(x, y, r=4, g=1.0, w=None):
    pts = []
    for i in range(10):
        a = math.pi/2 + i*math.pi/5; rr = r if i % 2 == 0 else r*0.45
        pts.append((x+math.cos(a)*rr, y+math.sin(a)*rr))
    shape(pts, g, w or LINE*0.7)

def sock_item(x, y, s=1.0, g=0.35, rot=0):
    with T(x, y, s, rot=rot):
        pts = bez((-4, 0), (-4, -8), (-4, -14), (-3.5, -16)) + bez((-3.5, -16), (0, -24), (8, -27), (9.5, -23)) + \
              bez((9.5, -23), (10, -19), (5, -17), (4, -14)) + [(4, 0)]
        shape(pts, g)
        shape([(-4, 0), (4, 0), (4, -4), (-4, -4)], 0.9, LINE*0.8)

def glove(x, y, s=1.0, g=0.5, rot=0):
    with T(x, y, s, rot=rot):
        pts = [(-7, 0), (7, 0), (7, 14), (10, 16), (9, 19), (6, 18), (6, 26), (3, 26), (3, 20), (1, 28), (-2, 28), (-2, 20), (-4, 27), (-7, 26), (-7, 14)]
        shape(pts, g)
        shape([(-7, 0), (7, 0), (7, 5), (-7, 5)], P.GLOVE_CUFF, LINE*0.8)

def wool(x, y, r=8, g=0.55):
    shape(ell(x, y, r, r, 30), g)
    for k_ in range(4):
        stroke(ell(x+(k_-1.5)*r*0.18, y, r*0.8, r*0.5, 14, 20+k_*30, 200+k_*30, rot=k_*40), LINE*0.6)

def basket(x, y):
    with T(x, y, 1.0):
        stroke(bez((-14, 14), (-12, 30), (12, 30), (14, 14)), LINE*2.2)
        stroke(bez((-14, 14), (-12, 30), (12, 30), (14, 14)), LINE*0.9, g=0.7)
        shape(ell(-5, 16, 7, 3, 16), 0.95, LINE*0.8); shape(ell(5, 17, 6, 3, 16), 0.5, LINE*0.8)
        shape([(-14, 0), (14, 0), (17, 14), (-17, 14)], 0.7)
        for k_ in range(-12, 14, 5): stroke([(k_, 1), (k_*1.15, 13)], LINE*0.5)

def hammer(x, y):
    with T(x, y, 1.0, rot=30):
        tube([(0, -4), (0, 18)], 2.4, 2.2, 0.7, sh=0)
        shape([(-7, 16), (7, 16), (7, 22), (-7, 22)], 0.3)

def ball(x, y, r=8):
    shape(ell(x, y, r, r, 30), 1.0)
    stroke(bez((x-r, y), (x-r*0.3, y+r*0.5), (x+r*0.3, y+r*0.5), (x+r, y)), LINE*0.8)
    fill(ell(x, y-r*0.35, r*0.5, r*0.35, 14), 0.35)

def birdhouse(x, y, s=1.0):
    with T(x, y, s):
        form([(-18, 0), (18, 0), (18, 30), (-18, 30)], P.BIRDHOUSE_WOOD, sdx=3, sdy=0)
        for k_ in (-9, 0, 9): stroke([(k_, 1), (k_, 29)], LINE*0.5)
        shape([(-24, 28), (0, 46), (24, 28), (20, 26), (0, 40), (-20, 26)], P.BIRDHOUSE_ROOF)
        shape(ell(0, 17, 6, 6, 24), 0.12)
        shape([(-3, 7), (3, 7), (3, 9), (-3, 9)], P.BIRDHOUSE_PERCH, LINE*0.7)
        stroke([(0, 8), (0, 4)], LINE*1.2)

def moon(x, y, r=16):
    pts = ell(x, y, r, r, 36, 60, 300) + list(reversed(ell(x+r*0.55, y, r*0.8, r*0.85, 30, 90, 270)))
    shape(pts, 0.97)
    dot(x-r*0.45, y+r*0.2, 1.3, 0)
    stroke(bez((x-r*0.7, y-r*0.35), (x-r*0.5, y-r*0.5), (x-r*0.3, y-r*0.45), (x-r*0.2, y-r*0.3)), LINE*0.8)

def footprints(x, y, n=5, dx=12, dy=4, s=1.0, g=0.3):
    for i in range(n):
        px = x + i*dx; py = y + (i % 2)*dy
        fill(ell(px, py, 2.3*s, 3*s, 14, rot=-20), g)
        for t in range(4):
            a = math.radians(50 + t*27)
            dot(px + math.cos(a)*4.5*s, py + math.sin(a)*4.5*s, 0.9*s, g)

def notebook_big(x, y, w, h, title, lines_, check=False):
    from letter import hand_text
    shape(rrect(x-6, y-6, w+12, h+12, 6), 0.4, 1.4)
    shape(rrect(x, y, w, h, 3), 1.0, 1.0)
    for k_ in range(int((h-10)/19)):
        yy = y + h - 29 - k_*19
        stroke([(x+8, yy), (x+w-8, yy)], 0.4, g=0.7)
    stroke([(x+24, y+4), (x+24, y+h-4)], 0.6, g=0.5)
    hand_text(x+30, y+h-24, w-40, title, "SHB", 16, align="left")
    for i, l in enumerate(lines_):
        if l: hand_text(x+30, y+h-24-(i+1)*19, w-40, l, "SH", 15, align="left")
    if check:
        stroke([(x+w-46, y+28), (x+w-35, y+15), (x+w-14, y+46)], 3.4)
