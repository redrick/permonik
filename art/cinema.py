"""Layered art for the cut-out cinematics (game/scripts/ui/ui_cinema.gd, choreography in cin_films.gd).

Each layer is drawn on its shot's canvas, cropped to what it covers and saved as WebP under
game/assets/cinema/<film>/<layer>.webp. game/data/cinema_layers.json keeps where every crop sits on
its canvas (px, y down) and the named points the choreography hangs things on.

    .venv/bin/python cinema.py                 # everything
    .venv/bin/python cinema.py intro/bell      # one layer;  intro/ for one film
"""
import os, sys, json
from multiprocessing import Pool
from PIL import Image
import common
from slides import *

MANIFEST = os.path.join(common.GAME, "data", "cinema_layers.json")
LAYERS = {}


def layer(name, w=1920, h=1080):
    def deco(fn):
        LAYERS[name] = (w, h, fn)
        return fn
    return deco


def _px(b, v):
    if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
        return [_px(b, p) for p in v]
    return [round(v[0]*common.SCALE, 1), round((b.h - v[1])*common.SCALE, 1)]


def render_one(name):
    w, h, fn = LAYERS[name]
    pts = {}

    def draw(b):
        got = fn(b)
        for k, v in (got or {}).items():
            pts[k] = _px(b, v)
    path = common.render(os.path.basename(name), w, h, draw, "cinema/" + os.path.dirname(name), paper=True)
    im = Image.open(path).convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > 3 else 0).getbbox() or (0, 0, 1, 1)
    im.crop(bb).save(path[:-4] + ".webp", quality=88, method=6)
    os.remove(path)
    return name, {"x": bb[0], "y": bb[1], "w": bb[2] - bb[0], "h": bb[3] - bb[1], "cw": w, "ch": h, "pts": pts}


# ================================================================== intro: Klekání
@layer("intro/sky", 2400)
def intro_sky(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#2a1c2c"), (0.3, "#b0664a"), (0.38, "#8e4f56"), (0.55, "#4b3458"), (0.8, "#22213f"), (1, "#121429")])
    crayon_over(rect(0, H*0.3, W, H), "#3a3768", 0.35, 3)
    stars(0, H*0.62, W, H, 90, 4, big=0.06)
    glow(W*0.36, H*0.27, 440, "#ff9b5a", 0.35, 30, ry=110)


def hora_hills(W, H, col="#3a2c48"):
    hl = [(0, H*0.3)] + [(x, H*0.33 + 14*math.sin(x/90) + 8*math.sin(x/37)) for x in range(0, int(W)+20, 20)] + [(W, H*0.3), (W, 0), (0, 0)]
    shape(hl, K(col), 0.9)


HORA_BELL = (0.2, 0.25, 1.62)


@layer("intro/far", 2400)
def intro_far(b):
    W, H = b.w, b.h
    hora_hills(W, H)
    mist(0, W, H*0.33, 22, "#c98a7a", 0.4, 2)
    cathedral(W*0.62, H*0.30, 1.62)
    bx, by, bs = HORA_BELL
    belfry(W*bx, H*by, bs, draw_bell=False)
    for (px, py, ps) in ((W*0.4, H*0.82, 1.0), (W*0.44, H*0.86, 0.8), (W*0.37, H*0.88, 0.7), (W*0.8, H*0.78, 0.9)):
        stroke(bez((px-7*ps, py+2*ps), (px-4*ps, py+5*ps), (px-2*ps, py+3*ps), (px, py)), 1.0)
        stroke(bez((px, py), (px+2*ps, py+3*ps), (px+4*ps, py+5*ps), (px+7*ps, py+2*ps)), 1.0)
    mist(0, W, H*0.36, 30, "#6e4a6a", 0.5, 5)


@layer("intro/bell", 2400)
def intro_bell(b):
    bx, by, bs = HORA_BELL
    x, y = b.w*bx, b.h*by + 136*bs
    with T(x, y, bs):
        bell_shape(0, 0)
    return {"pivot": (x, y)}


@layer("intro/town", 2400)
def intro_town(b):
    W, H = b.w, b.h
    lights = town_row(-20, W+20, H*0.30, 11, "#2c2536", "#211b2a", 26, 50, 0.16, edge="#b0664a", wmin=34, wmax=58)
    for lx, ly in lights:
        glow(lx, ly, 12, "#ffb85c", 0.25, 8)
    return {"lights": lights}


ROOF = (-20, 0, 0.78)


@layer("intro/near", 2400)
def intro_near(b):
    W, H = b.w, b.h
    flat(rect(0, 0, W, H*0.2), "#0e0c13")
    lights = town_row(-40, W+40, H*0.17, 5, "#1b1722", "#14111a", 38, 64, 0.18, wmin=52, wmax=86, lw=1.3)
    for lx, ly in lights:
        glow(lx, ly, 16, "#ffb85c", 0.3, 8)
    with T(W + 20, 0, 1.0, True):
        fg_roof(0, 0, ROOF[2], with_crow=False)
    return {"lights": lights}


def crow_fly(x, y, s, up, col="#0b0a10"):
    with T(x, y, s):
        shape(ell(0, 0, 9, 3.4, 20), K(col), 0.9)
        shape([(7, 2.2), (13.5, 1.0), (8, -1.4)], K(col), 0.8)
        S.dot(9, 1.2, 0.6, K("#d9a050"))
        shape([(-7, 1), (-15, 3.5), (-14, -3), (-7, -1)], K(col), 0.8)
        wing = [(-3, 1), (-8, 15), (5, 11), (3, 1)] if up else [(-3, -1), (-7, -13), (6, -8), (3, -1)]
        shape(wing, K(col), 0.9)


def _crow(b, fn):
    s = ROOF[2]
    x, y = b.w + 20 - 166*s, 220*s
    with T(x, y, 1.0, True):
        fn(1.4*s)
    return {"pivot": (x, y)}


@layer("intro/crow", 2400)
def intro_crow(b):
    return _crow(b, lambda s: crow(0, 0, s))


@layer("intro/crow_up", 2400)
def intro_crow_up(b):
    return _crow(b, lambda s: crow_fly(0, 8*s, s*1.1, True))


@layer("intro/crow_down", 2400)
def intro_crow_down(b):
    return _crow(b, lambda s: crow_fly(0, 8*s, s*1.1, False))


SHAFT_GY = 1080*0.8
SHAFT_X = (960*0.44, 960*0.62)


@layer("intro/shaft", 1920, 2160)
def intro_shaft(b):
    W, H = b.w, b.h
    gy = SHAFT_GY
    grad(0, gy, W, H, [(0, "#3a3a5c"), (0.5, "#1e2140"), (1, "#101226")])
    stars(0, gy + 20, W, H, 40, 8)
    glow(W*0.9, H*0.95, 36, "#e8e2c8", 0.3, 12)
    S.fill(ell(W*0.9, H*0.95, 11, 11, 30), K("#efe8d0"), 1.0); stroke(ell(W*0.9, H*0.95, 11, 11, 30), 0.9, closed=True)
    hl = [(0, gy)] + [(x, gy + 30 + 16*math.sin(x/140+1) + 6*math.sin(x/41)) for x in range(0, int(W)+20, 20)] + [(W, gy)]
    shape(hl, K("#1f1d2c"), 0.9)
    earth(0, 0, W, gy, 7)
    for i in range(40):
        flat(rect(0, 0, W, gy*0.8*(1 - i/40)), "#000000", 0.045)
    sx0, sx1 = SHAFT_X
    shape([(0, gy - 10)] + jag(0, W, gy + 2, 2, 7, 2) + [(W, gy - 10)], K("#24261e"), 1.3)
    shaft(sx0, sx1, 0, gy, "#3f2f22")
    ladder(sx0 + 52, gy + 40, sx0 + 58, -20, 34, step=17)
    for i in range(30):
        flat(rect(sx0 - 16, 0, sx1 + 16, gy*0.9*(1 - i/30)), "#000000", 0.07)
    headframe((sx0 + sx1)/2, gy - 6, 1.55)
    for i, (mx, s_) in enumerate(((W*0.06, 1.6), (W*0.2, 1.75))):
        miner_side(mx, gy - 4, s_, "stand", seed=10 + i, shade=0.4, glow_k=0.5)
    return {"top": ((sx0 + sx1)/2, gy), "bottom": ((sx0 + sx1)/2, 0)}


@layer("intro/miner", 1920, 2160)
def intro_miner(b):
    gy = SHAFT_GY
    sx0 = SHAFT_X[0]
    my, s_ = gy - 110, 1.45
    hx, hy = miner_back(sx0 + 54, my, s_, shade=0.45, rail=12)
    lamp(hx + 2, hy, 0.95*s_, glow_r=0)
    return {"lamp": (hx + 2 + 9.4*0.95*s_, hy - 10.3*0.95*s_), "pivot": (sx0 + 54, my)}


HEAD = dict(hxp=0.3, hyp=0.08, hs=2.4, hr=-10, ps=1.75)


def _head_geo(W, H):
    hxp, hyp, hs, hr, ps = W*HEAD["hxp"], H*HEAD["hyp"], HEAD["hs"], HEAD["hr"], HEAD["ps"]
    px, py = hxp + 118, H*0.06
    hand = (px + 21*ps, py + 62*ps)
    return hxp, hyp, hs, hr, px, py, ps, hand


@layer("intro/head_bg")
def intro_head_bg(b):
    W, H = b.w, b.h
    hz = H*0.42
    grad(0, hz, W, H, [(0, "#2a2f52"), (0.4, "#1a1d3a"), (1, "#0c0d1f")])
    stars(0, hz + 40, W, H, 80, 21, big=0.05)
    hl = [(0, hz)] + [(x, hz + 14 + 10*math.sin(x/120) + 5*math.sin(x/33)) for x in range(0, int(W)+20, 20)] + [(W, hz)]
    shape(hl, K("#161728"), 0.8)
    with T(W*0.86, hz + 12, 0.35):
        cathedral(0, 0, 1.0, wall="#1c1c30", roof="#151526", edge="#6a6a9a", win="#101020")
    belfry(W*0.72, hz + 8, 0.35, wall="#1c1c30", roof="#151526", edge="#6a6a9a")
    planks(-10, W + 10, 0, hz + 2, W*0.52, H*0.9, n=22)
    hx0, hx1 = W*0.6, W*0.86
    hole = [(hx0, hz - 40), (hx1, hz - 40), (hx1 + 30, hz - 120), (hx0 - 20, hz - 120)]
    shape(hole, K("#050407"), 1.4)
    for a_, b_ in ((hole[0], hole[1]), (hole[3], hole[0]), (hole[1], hole[2])):
        stroke([a_, b_], 6.0); stroke([a_, b_], 3.2, g=K("#3a2a1c"))
    for xx in (hx0 - 6, hx1 + 6):
        post = rect(xx - 8, hz - 60, xx + 8, H*0.95)
        shape(post, K("#21180f"), 1.3); offset_shadow(post, 6, 0, 0.35)
    beam = rect(hx0 - 30, H*0.84, hx1 + 30, H*0.9)
    shape(beam, K("#21180f"), 1.3)
    S.fill(ell((hx0 + hx1)/2, H*0.87, 24, 24, 30), K("#2a1e14")); stroke(ell((hx0 + hx1)/2, H*0.87, 24, 24, 30), 1.2, closed=True)
    stroke([((hx0 + hx1)/2 + 12, H*0.87), ((hx0 + hx1)/2 + 12, hz - 80)], 1.0, g=K("#6a5a48"))
    lamp(hx1 + 14, H*0.82, 1.2, glow_r=50, glow_a=0.35)
    hxp, hyp, hs, hr, px, py, ps, hand = _head_geo(W, H)
    return {"post_lamp": (hx1 + 14 + 9.4*1.2, H*0.82 - 10.3*1.2), "perm_feet": (px, py), "hero_feet": (hxp, hyp),
            "hole": ((hx0 + hx1)/2, hz - 80)}


@layer("intro/hero_walk")
def intro_hero_walk(b):
    hxp, hyp, hs, hr, px, py, ps, hand = _head_geo(b.w, b.h)
    hero_silhouette(hxp, hyp, hs, rim="#8fd0ff")
    return {"pivot": (hxp, hyp)}


@layer("intro/hero_reach")
def intro_hero_reach(b):
    hxp, hyp, hs, hr, px, py, ps, hand = _head_geo(b.w, b.h)
    lx, ly = hand[0], hand[1] + 1
    hero_silhouette(hxp, hyp, hs, rim="#8fd0ff", reach=True, arm_to=to_local(hxp, hyp, hs, hr, lx + 3, ly + 2), rot=hr)
    return {"pivot": (hxp, hyp)}


@layer("intro/hero_shadow")
def intro_hero_shadow(b):
    hxp, hyp, hs, hr, px, py, ps, hand = _head_geo(b.w, b.h)
    C.saveState(); C.transform(0.8, 0.0, -0.85, 0.5, hxp, hyp)
    hero_silhouette(0, 0, hs, col="#07070c", rim="#07070c", reach=True, arm_to=(40, 70))
    C.restoreState()
    return {"pivot": (hxp, hyp)}


@layer("intro/perm")
def intro_perm(b):
    hxp, hyp, hs, hr, px, py, ps, hand = _head_geo(b.w, b.h)
    permonik(px, py, ps, high=True)
    return {"pivot": (px, py), "hand": hand}


@layer("intro/lamp")
def intro_lamp(b):
    hxp, hyp, hs, hr, px, py, ps, hand = _head_geo(b.w, b.h)
    lx, ly = hand[0], hand[1] + 1
    lamp(lx, ly, ps*0.9, cold=True, glow_r=0, body="#5a4a3a")
    return {"pivot": (lx, ly), "flame": (lx + 9.4*ps*0.9, ly - 10.3*ps*0.9)}


# ================================================================== shared pieces
FLAME_FAN = ((9.4, -10.3, 0.75, 0.6), (7.4, -9.2, 0.6, -0.8), (11.5, -9.4, 0.6, 1.6), (9.2, -7.9, 0.5, 0.2))


def lamp_n(x, y, s, n, body="#5a4a3a"):
    """the cold kahan with n flames fanned on the spout; returns the flame points"""
    lamp(x, y, s, cold=True, glow_r=0, body=body)
    out = [(x + 9.4*s, y - 10.3*s + 2*s)]
    for fx, fy, fs, lean in FLAME_FAN[1:n]:
        flame(x + fx*s, y + fy*s, fs*s, cold=True, lean=lean)
        out.append((x + fx*s, y + fy*s + 2*s))
    return out


def hero_with_lamp(x, y, s, n, rim="#8fd0ff", hand=(26, 62)):
    """hooded hero, the lamp hanging from the right hand; returns the flame points"""
    hero_silhouette(x, y, s, rim=rim, reach=True, arm_to=hand)
    return lamp_n(x + (hand[0] + 4)*s, y + (hand[1] - 2)*s, s*0.8, n)


def ghost_fill(pts, h, a=0.6, lw=0.9, line="#5a7a9a"):
    S.fill(pts, K(h), a)
    stroke(pts, lw, closed=True, g=K(line), alpha=0.8)


def girl(x, y, s, look=False):
    """the drowned girl from the cups, from behind; look turns her head back over the shoulder"""
    pale, dark, skin = "#c4dcf0", "#5a7a9a", "#d8ecf8"
    with T(x, y, s):
        for lx in (-3, 3):
            ghost_fill([(lx - 1.6, 0), (lx + 1.6, 0), (lx + 1.3, 14), (lx - 1.3, 14)], skin, 0.55)
        dress = [(-12, 12)] + bez((-12, 12), (-9, 26), (-6, 38), (-5, 44)) + [(5, 44)] + bez((5, 44), (6, 38), (9, 26), (12, 12))
        dress = S.notch(dress, 1.2, 3)
        ghost_fill(dress, pale, 0.62)
        for k in range(4):
            stroke(bez((-8 + k*5, 13), (-7 + k*4.5, 22), (-5 + k*3.5, 32), (-3 + k*2, 42)), 0.5, g=K(dark), alpha=0.5)
        for side in (-1, 1):
            ghost_fill(S.tube([(side*5, 42), (side*8, 32), (side*8.5 if not (look and side > 0) else 12, 24 if not (look and side > 0) else 38)], 3.2, 2.6, K(pale), lw=0, sh=0), pale, 0.55)
        ghost_fill(ell(0, 51, 7, 7.5, 24), skin, 0.6)
        if look:
            hair = ell(-1.5, 52, 7, 7.8, 24, 60, 300)
            ghost_fill(hair, "#7a96b0", 0.75)
            S.fill(ell(4.2, 52.5, 0.9, 1.3, 8), K("#1a2a3a"), 0.9)
            stroke([(6.6, 50.5), (7.6, 49.6), (6.8, 49.2)], 0.6, g=K(dark))
            stroke([(4.2, 47.6), (5.8, 47.8)], 0.5, g=K(dark), alpha=0.8)
        else:
            ghost_fill(ell(0, 52, 7.2, 7.8, 24), "#7a96b0", 0.75)
        for side in (-1, 1):
            br = [(side*4, 50), (side*6, 42), (side*5.5, 34), (side*6.5, 30)]
            stroke(br, 2.6, g=K("#7a96b0"), alpha=0.8)
            stroke(br, 0.6, g=K(dark), alpha=0.6)
            S.dot(side*6.5, 29.5, 1.2, K("#b8d4ea"))
        for k in range(5):
            rr = random.Random(k)
            dx = rr.uniform(-10, 10)
            stroke([(dx, rr.uniform(4, 10)), (dx + rr.uniform(-0.5, 0.5), rr.uniform(-3, 2))], 0.5, g=K("#9fd0f0"), alpha=0.5)


def kosmas_full(x, y, s, rot=0):
    """old Kosmas mid-leap, book clamped under his arm; (x, y) is his middle"""
    robe, skin, beard = K("#4a2a26"), K("#e2b48e"), K("#e6e2da")
    with T(x, y, s, rot=rot):
        for side, (kx, ky), (fx, fy) in ((-1, (-14, -36), (-30, -44)), (1, (16, -30), (30, -22))):
            S.tube([(side*5, -14), (kx, ky), (fx, fy)], 8, 6.5, K("#3a2a24"), lw=1.1, sh=0.2)
            shape([(fx - 6, fy - 3), (fx + 6, fy - 3), (fx + 6, fy + 3), (fx - 5, fy + 4)], K("#2a1c16"), 1.0)
        body = [(-22, -26)] + bez((-22, -26), (-26, 0), (-20, 26), (-10, 34)) + bez((-10, 34), (0, 37), (10, 36), (18, 30)) + \
               bez((18, 30), (24, 10), (26, -12), (24, -30)) + [(10, -22), (0, -32), (-10, -22)]
        shape(body, robe, 1.4)
        offset_shadow(body, -8, 2, 0.35)
        book = [(-26, 0), (-6, -4), (-4, 12), (-24, 16)]
        shape(book, K("#3a2214"), 1.2)
        shape([(-24, 13), (-5, 9), (-4, 12), (-24, 16)], K("#e8dcc0"), 0.8)
        S.tube([(-14, 28), (-24, 14), (-14, 4)], 9, 8, robe, lw=1.1, sh=0.2)
        S.tube([(14, 28), (28, 40), (40, 52)], 9, 8, robe, lw=1.1, sh=0.2)
        shape(ell(41, 54, 4, 3.5, 14), skin, 1.0)
        head = ell(4, 48, 12, 13, 28)
        shape(head, skin, 1.2)
        bd = bez((-8, 46), (-10, 30), (0, 18), (6, 14)) + bez((6, 14), (12, 22), (18, 34), (16, 46))
        shape(S.notch(bd, 1.1, 3), beard, 1.1)
        cap = bez((-8, 54), (-8, 66), (16, 66), (16, 54)) + bez((16, 54), (8, 58), (0, 58), (-8, 54))
        shape(cap, K("#2a1a18"), 1.1)
        for ex in (-1, 1):
            stroke(ell(4 + ex*5, 49, 3.6, 3.2, 16), 1.0, closed=True)
            S.fill(ell(4 + ex*5, 49, 3.6, 3.2, 16), K("#ffd28a"), 0.3)
        shape(ell(4, 42, 3, 2.4, 12), K("#d9a07a"), 0.9)
        stroke(bez((0, 38), (2, 36), (6, 36), (8, 38)), 0.9)


# ================================================================== act1_end: Dušičky v hrníčcích
A1_WY = 540*0.36
A1_ROCKS = ((0.27, -6, 70, 26), (0.55, -10, 90, 30), (0.8, -4, 60, 22))


@layer("a1/cave")
def a1_cave(b):
    W, H = b.w, b.h
    wy = A1_WY
    grad(0, 0, W, H, [(0, "#06121a"), (0.4, "#0c1e28"), (0.75, "#10232d"), (1, "#081218")])
    crayon_over(rect(0, wy, W, H), "#1d3a44", 0.45, 2)
    glow(W*0.52, H*1.0, 260, "#9fd8ff", 0.35, 24, ry=200)
    crack = [(W*0.47, H + 5), (W*0.5, H*0.93), (W*0.53, H*0.95), (W*0.57, H + 5)]
    S.fill(crack, K("#cfefff"), 0.6)
    for i in range(3):
        rr = random.Random(30 + i)
        back = [(-20, wy - 5)] + jag(-20, W + 20, wy + 30 + i*35 + rr.uniform(0, 30), 18, 60, 40 + i) + [(W + 20, wy - 5)]
        shape(back, K(mix("#1a3540", "#0c171d", i/2)), 1.0)
    stalactites(0, W, H, 3, "#0f1d24", 22, 40, 150)
    S.fill(rect(0, 0, W, wy), K("#071016"), 1.0)
    crayon_over(rect(0, 0, W, wy), "#16323e", 0.5, 9)
    for k in range(9):
        y = wy - 6 - k*k*2.6
        stroke([(W*0.05 + k*30, y), (W*0.95 - k*25, y)], 0.5, g=K("#4a7a8a"), alpha=0.35)
    cups = []
    for i, (fx, dy, rw, rh) in enumerate(A1_ROCKS):
        x, y = W*fx, wy + dy
        rp = bez((x - rw, y - 4), (x - rw*0.7, y + rh), (x + rw*0.5, y + rh*1.1), (x + rw, y - 4))
        shape(rp, K("#1b2a30"), 1.2)
        offset_shadow(rp, -rw*0.3, 0, 0.35)
        for j in range(3):
            cx, cy = x - rw*0.5 + j*rw*0.5, y + rh*0.75 - abs(j - 1)*rh*0.2 + 8
            teacup(cx, cy, 1.5, rot=180 + (j - 1)*12, seed=i*3 + j, inner="#bfe6ff")
            cups.append((cx, cy + 10))
    return {"cups": cups, "water": (W/2, wy)}


@layer("a1/frame")
def a1_frame(b):
    cave_frame(b, "#05080b", 4, top=0.98, side=0.02)


@layer("a1/fg")
def a1_fg(b):
    W, H = b.w, b.h
    fg = [(-20, -20), (-20, H*0.3), (W*0.08, H*0.27), (W*0.17, H*0.2), (W*0.23, H*0.12), (W*0.27, -20)]
    shape(fg, K("#06090c"), 1.6)
    crayon_over(fg, "#12202a", 0.4, 13)
    for j, (cx, cy, rot) in enumerate(((W*0.09, H*0.27, 170), (W*0.17, H*0.205, 200))):
        teacup(cx, cy + 26, 3.2, rot=rot, seed=40 + j, inner="#bfe6ff")
    for j in range(7):
        rr2 = random.Random(60 + j)
        cx, cy = W*0.05 + j*24, H*0.24 - j*10
        S.fill([(cx, cy), (cx + rr2.uniform(5, 12), cy + rr2.uniform(-2, 4)), (cx + rr2.uniform(2, 8), cy + rr2.uniform(5, 9))], K("#e9e2d0"), 0.9)
    return {"big_cup": (W*0.09, H*0.27 + 40)}


@layer("a1/soul")
def a1_soul(b):
    soul(b.w/2, b.h/2, 1.3, seed=3)
    return {"pivot": (b.w/2, b.h/2)}


@layer("a1/soul2")
def a1_soul2(b):
    soul(b.w/2, b.h/2, 1.3, seed=11)
    return {"pivot": (b.w/2, b.h/2)}


A1_HAND, A1_LS = (0.8, 0.42), 3.6


@layer("a1/arm_lamp")
def a1_arm_lamp(b):
    W, H = b.w, b.h
    hx, hy = W*A1_HAND[0], H*A1_HAND[1]
    S.tube([(W + 40, -20), (W*0.92, H*0.18), (hx + 8, hy + 4)], 44, 30, K("#0c0b12"), lw=1.8, sh=0)
    stroke([(W*0.92 + 16, H*0.18 + 8), (hx + 20, hy + 10)], 1.6, g=K("#8fd0ff"), alpha=0.6)
    S.fill(ell(hx, hy, 13, 10, 14), K("#0c0b12")); stroke(ell(hx, hy, 13, 10, 16), 1.4, closed=True)
    fl = lamp_n(hx - 2, hy - 8, A1_LS, 1)
    return {"flame": fl[0], "pivot": (hx, hy)}


@layer("a1/flame2")
def a1_flame2(b):
    W, H = b.w, b.h
    x, y = W*A1_HAND[0] - 2 + 7.4*A1_LS, H*A1_HAND[1] - 8 - 9.2*A1_LS
    flame(x, y, 0.6*A1_LS, cold=True, lean=-0.8)
    return {"pivot": (x, y)}


A1_VP = (0.5, 0.47)


@layer("a1/gallery")
def a1_gallery(b):
    W, H = b.w, b.h
    vx, vy = W*A1_VP[0], H*A1_VP[1]
    flat(rect(0, 0, W, H), "#0a1216")
    crayon_over(rect(0, 0, W, H), "#1a2e36", 0.45, 21)
    frames = []
    for k in range(7):
        t = 0.66**k
        hw, top, bot = W*0.47*t, vy + H*0.56*t, vy - H*0.5*t
        frames.append((t, hw, top, bot))
    dw, dtop, dbot = frames[-1][1], frames[-1][2], frames[-1][3]
    glow(vx, (dtop + dbot)/2, 150, "#cfefff", 0.55, 20, ry=110)
    S.fill(rect(vx - dw*0.9, dbot, vx + dw*0.9, dtop - 2), K("#e8f8ff"), 0.95)
    for k in range(len(frames) - 1):
        t0, hw0, top0, bot0 = frames[k]
        t1, hw1, top1, bot1 = frames[k + 1]
        for side in (-1, 1):
            wall = [(vx + side*hw0, bot0), (vx + side*hw1, bot1), (vx + side*hw1, top1), (vx + side*hw0, top0)]
            shape(wall, K(mix("#1e2c30", "#2e4246", k/6)), 0.8)
            crayon_over(wall, "#3a5258", 0.3, 30 + k*2 + side)
        roof = [(vx - hw0, top0), (vx - hw1, top1), (vx + hw1, top1), (vx + hw0, top0)]
        shape(roof, K(mix("#141e22", "#24343a", k/6)), 0.8)
        floor = [(vx - hw0, bot0), (vx - hw1, bot1), (vx + hw1, bot1), (vx + hw0, bot0)]
        shape(floor, K(mix("#0c1a20", "#1e3a44", k/6)), 0.8)
    for k in range(10):
        rr = random.Random(70 + k)
        yy = vy - H*0.5*rr.uniform(0.05, 0.9)
        t = (vy - yy)/(H*0.5)
        stroke([(vx - W*0.47*t*rr.uniform(0.2, 0.9), yy), (vx + W*0.47*t*rr.uniform(0.2, 0.9), yy)], 0.6, g=K("#9fd8ef"), alpha=0.35)
    S.fill([(vx - dw*0.8, dbot), (vx + dw*0.8, dbot), (vx + W*0.12, 0), (vx - W*0.12, 0)], K("#cfefff"), 0.12)
    for t, hw, top, bot in frames:
        lw = 0.6 + 2.2*t
        for side in (-1, 1):
            post = rect(vx + side*hw - 9*t, bot, vx + side*hw + 9*t, top)
            shape(post, K("#2a2018"), lw); offset_shadow(post, -side*5*t, 0, 0.35)
        cap = rect(vx - hw - 16*t, top - 4*t, vx + hw + 16*t, top + 12*t)
        shape(cap, K("#2a2018"), lw); offset_shadow(cap, 0, -5*t, 0.35)
    return {"door": (vx, dbot + 2), "near": (vx - W*0.06, H*0.12)}


def _girl_at(b):
    return b.w*0.44, b.h*0.12, 3.4


@layer("a1/girl_away")
def a1_girl_away(b):
    x, y, s = _girl_at(b)
    girl(x, y, s)
    return {"pivot": (x, y)}


@layer("a1/girl_look")
def a1_girl_look(b):
    x, y, s = _girl_at(b)
    girl(x, y, s, look=True)
    return {"pivot": (x, y)}


# ================================================================== act2_end: Fabiánova dýmka
A2_GY = 540*0.2


@layer("a2/sky", 2400)
def a2_sky(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#1a2124"), (0.4, "#3c4a4c"), (0.7, "#2b3639"), (1, "#141a1e")])
    crayon_over(rect(0, 0, W, H), "#7a8a86", 0.25, 6)


A2_ROWS = ((0.4, 140, 230, "#4e5d5c", 32, 0.5), (0.32, 180, 300, "#344240", 23, 0.45), (0.24, 260, 420, "#1f2a28", 14, 0.4))


def _a2_trees(b, layer_i):
    W, H = b.w, b.h
    yb, hmin, hmax, col, n, fog = A2_ROWS[layer_i]
    yb *= H
    r = random.Random(10 + layer_i)
    for i in range(n):
        x = r.uniform(-30, W + 30)
        if layer_i == 2 and W*0.15 < x < W*0.45:
            continue
        spruce(x, yb + r.uniform(-10, 10), r.uniform(hmin, hmax), col, 0.9 + layer_i*0.25, seed=i + layer_i*50)
    mist(-40, W + 40, yb + 20, 50, "#9aaaa6", fog, 3 + layer_i, 16)


@layer("a2/trees0", 2400)
def a2_trees0(b): _a2_trees(b, 0)


@layer("a2/trees1", 2400)
def a2_trees1(b): _a2_trees(b, 1)


@layer("a2/trees2", 2400)
def a2_trees2(b): _a2_trees(b, 2)


A2_MOUTH = (0.82, 120, 150)


@layer("a2/ground", 2400)
def a2_ground(b):
    W, H = b.w, b.h
    gy = A2_GY
    gr = [(-20, -20), (-20, gy + 18)] + jag(-20, W + 20, gy + 14, 6, 40, 3) + [(W + 20, -20)]
    shape(gr, K("#1c2620"), 1.3)
    crayon_over(gr, "#3a4a30", 0.5, 7)
    hill = [(W*0.66, gy - 10)] + bez((W*0.66, gy - 10), (W*0.73, H*0.5), (W*0.86, H*0.66), (W + 20, H*0.7)) + [(W + 20, gy - 10)]
    shape(hill, K("#1b1f1c"), 1.4)
    crayon_over(hill, "#3a3c34", 0.5, 8)
    spruce(W*0.78, H*0.56, 200, "#141c1a", 1.3, 77)
    spruce(W*0.93, H*0.62, 240, "#141c1a", 1.3, 78)
    fx, mw, mh = A2_MOUTH
    mx, my = W*fx, gy - 2
    mouth = [(mx - mw/2, my)] + bez((mx - mw/2, my), (mx - mw/2, my + mh*0.9), (mx + mw/2, my + mh*0.9), (mx + mw/2, my)) + [(mx - mw/2, my)]
    shape(mouth, K("#030405"), 1.4)
    for xx in (mx - mw/2 - 4, mx + mw/2 + 4):
        p = rect(xx - 8, my - 4, xx + 8, my + mh*0.72)
        shape(p, K("#3a2c1e"), 1.2); offset_shadow(p, 5, 0, 0.35)
    lin = rect(mx - mw/2 - 18, my + mh*0.68, mx + mw/2 + 18, my + mh*0.68 + 16)
    shape(lin, K("#3a2c1e"), 1.3); offset_shadow(lin, 0, 5, 0.35)
    near = (mx - 150, mx + 10); far = (mx - 12, mx + 12)
    for j in range(9):
        t = (j/8)**1.6; yy = (my + 4)*(1 - t) - 10*t
        xa = far[0] + (near[0] - far[0])*t - 12*t; xb = far[1] + (near[1] - far[1])*t + 12*t
        stroke([(xa, yy), (xb, yy)], 2.6); stroke([(xa, yy), (xb, yy)], 1.1, g=K("#4a3a2a"))
    for k in range(2):
        stroke([(near[k], -10), (far[k], my + 4)], 4.0); stroke([(near[k], -10), (far[k], my + 4)], 1.8, g=K("#8a8a92"))
    return {"mouth": (mx, my + 30)}


A2_FAB = (0.27, 2.35)


@layer("a2/fabian", 2400)
def a2_fabian(b):
    fx, fs = A2_FAB
    x, y = b.w*fx, A2_GY + 6
    fabian(x, y, fs)
    return {"pipe": (x + 24*fs, y + 106*fs), "eyes": (x, y + 109*fs), "pivot": (x, y)}


@layer("a2/fog", 2400)
def a2_fog(b):
    W = b.w
    mist(-40, W*0.7, A2_GY + 30, 40, "#a9b8b2", 0.45, 21, 12)
    mist(W*0.4, W + 40, A2_GY + 10, 30, "#a9b8b2", 0.35, 22, 10)


@layer("a2/fg", 2400)
def a2_fg(b):
    spruce(b.w*0.02, -30, 560, "#0b100e", 1.6, 90)


A2_HERO = (0.42, -10, 1.7)


@layer("a2/hero", 2400)
def a2_hero(b):
    fx, dy, s = A2_HERO
    x, y = b.w*fx, A2_GY + dy
    fl = hero_with_lamp(x, y, s, 2)
    return {"pivot": (x, y), "flame": fl[0]}


A2_TUN = (0.3, 0.62)


@layer("a2/road", 2400)
def a2_road(b):
    W, H = b.w, b.h
    y0, y1 = H*A2_TUN[0], H*A2_TUN[1]
    earth(0, y1, W, H + 10, 31)
    earth(0, -10, W, y0, 32, veins=False)
    flat(rect(0, y0, W, y1), "#0d0b0c")
    crayon_over(rect(0, y0, W, y1), "#2a2420", 0.4, 33)
    for k in range(40):
        rr = random.Random(500 + k)
        x = rr.uniform(0, W); y = rr.uniform(y0 + 10, y1 - 10)
        stroke([(x, y), (x + rr.uniform(-20, 20), y + rr.uniform(-12, 12))], 0.6, g=K("#3a322c"), alpha=0.6)
    roots(0, W*0.45, y1 + 4, 14, 41, col="#2a1e14", lmin=20, lmax=70, lw=1.4)
    for x in range(30, int(W), 150):
        post = rect(x - 7, y0 - 2, x + 7, y1)
        shape(post, K("#3a2c1e"), 1.2); offset_shadow(post, 5, 0, 0.35)
        cap = rect(x - 40, y1 - 14, x + 40, y1)
        shape(cap, K("#3a2c1e"), 1.2); offset_shadow(cap, 0, -4, 0.35)
    for k, yy in enumerate((y0 + 4, y0 + 9)):
        stroke([(0, yy), (W, yy)], 2.4); stroke([(0, yy), (W, yy)], 1.0, g=K("#7a7a84"))
    for x in range(0, int(W), 22):
        shape(rect(x, y0 - 2, x + 10, y0 + 2), K("#2a1e14"), 0.6)
    for i in range(40):
        flat(rect(W*(0.7 + 0.3*i/40), y0 - 20, W + 20, y1 + 20), "#000000", 0.05)
    return {"floor_y": (0, y0)}


A2_PAIR = 0.12


@layer("a2/hero_side", 2400)
def a2_hero_side(b):
    x, y = b.w*A2_PAIR, b.h*A2_TUN[0] + 2
    fl = hero_with_lamp(x, y, 1.15, 2)
    return {"pivot": (x, y), "flame": fl[0]}


@layer("a2/perm_walk", 2400)
def a2_perm_walk(b):
    x, y = b.w*A2_PAIR + 62, b.h*A2_TUN[0] + 2
    permonik(x, y, 1.1, lamp_up=False)
    return {"pivot": (x, y), "head": (x, y + 52*1.1)}


@layer("a2/note")
def a2_note(b):
    x, y = b.w/2, b.h/2
    with T(x, y, 1.6):
        S.fill(ell(0, 0, 4.2, 3, 16, rot=20), K("#e9dcc0"), 1.0)
        stroke(ell(0, 0, 4.2, 3, 16, rot=20), 0.8, closed=True)
        stroke([(3.6, 1), (3.6, 16)], 1.0)
        stroke(bez((3.6, 16), (7, 13), (9, 10), (8, 6)), 1.0)
    return {"pivot": (x, y)}


# ================================================================== act3_end: Země se zavřela
@layer("a3/bg")
def a3_bg(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#0d0908"), (0.6, "#24140e"), (1, "#100a08")])
    crayon_over(rect(0, 0, W, H), "#3a2418", 0.35, 51)
    ox, oy = W*0.5, H*0.96
    glow(ox, oy, 120, "#ffcf7a", 0.7, 20, ry=50)
    S.fill(ell(ox, oy, 46, 16, 30), K("#ffe2a8"), 1.0)
    for i in range(18):
        rr = random.Random(600 + i)
        x = rr.uniform(W*0.2, W*0.8); y = rr.uniform(0, H*0.26); r_ = rr.uniform(8, 26)
        rock(x, y, r_, 610 + i, rr.choice(("#2a2220", "#221c1a", "#302622")), rot=rr.uniform(0, 3), light=(ox, oy))
    return {"opening": (ox, oy), "floor": (ox, H*0.1)}


@layer("a3/beam")
def a3_beam(b):
    W, H = b.w, b.h
    ox, oy = W*0.5, H*0.96
    for k in range(10):
        t = k/9
        tw, bw = 40*(1 - t*0.6), 170*(1 - t*0.55)
        flat([(ox - tw, oy), (ox + tw, oy), (ox + bw, 0), (ox - bw, 0)], "#ffcf8a", 0.035)
    glow(ox, H*0.08, 180, "#ffcf8a", 0.25, 16, ry=40)
    return {"pivot": (ox, oy)}


def _a3_wall(b, side):
    W, H = b.w, b.h
    r = random.Random(70 + side)
    edge = []
    for i in range(14):
        y = H + 10 - i*(H + 20)/13
        edge.append((W*0.5 + side*(r.uniform(-10, 30) + 30*math.sin(i*1.3)), y))
    far = W + 300 if side > 0 else -300
    pts = edge + [(far, -10), (far, H + 10)]
    shape(pts, K("#1e1612"), 1.8)
    crayon_over(pts, "#3a2a20", 0.5, 71 + side)
    for k in range(14):
        rr = random.Random(80 + k + side*20)
        x = W*0.5 + side*rr.uniform(60, 420); y = rr.uniform(0, H)
        stroke([(x, y), (x + rr.uniform(-40, 40), y + rr.uniform(-30, 30)), (x + rr.uniform(-60, 60), y + rr.uniform(-50, 50))], 1.0, alpha=0.7)
    stroke(edge, 2.4, g=K("#ff9a4a"), alpha=0.7)
    for i in range(6):
        rr = random.Random(90 + i + side*10)
        rock(W*0.5 + side*rr.uniform(20, 120), rr.uniform(20, H - 20), rr.uniform(14, 30), 95 + i + side*10, "#2a201a", light=(W*0.5, H*0.9))


@layer("a3/left")
def a3_left(b):
    _a3_wall(b, -1)


@layer("a3/right")
def a3_right(b):
    _a3_wall(b, 1)


@layer("a3/rock_a")
def a3_rock_a(b):
    rock(b.w/2, b.h/2, 22, 701, "#2e2420", light=(b.w/2, b.h))
    return {"pivot": (b.w/2, b.h/2)}


@layer("a3/rock_b")
def a3_rock_b(b):
    rock(b.w/2, b.h/2, 14, 702, "#2a201c", light=(b.w/2, b.h))
    return {"pivot": (b.w/2, b.h/2)}


@layer("a3/rock_c")
def a3_rock_c(b):
    rock(b.w/2, b.h/2, 30, 703, "#261e1a", light=(b.w/2, b.h))
    return {"pivot": (b.w/2, b.h/2)}


@layer("a3/hero")
def a3_hero(b):
    x, y = b.w*0.44, b.h*0.06
    fl = hero_with_lamp(x, y, 2.3, 3, rim="#ffb36a")
    return {"pivot": (x, y), "flame": fl[0]}


@layer("a3/kosmas")
def a3_kosmas(b):
    x, y = b.w*0.5, b.h*0.5
    kosmas_full(x, y, 2.2, rot=-18)
    return {"pivot": (x, y)}


@layer("a3/dark")
def a3_dark(b):
    W, H = b.w, b.h
    flat(rect(0, 0, W, H), "#050406")
    crayon_over(rect(0, 0, W, H), "#16121a", 0.35, 55)
    for i in range(30):
        rr = random.Random(800 + i)
        a = rr.uniform(0, math.tau); d = rr.uniform(160, 460)
        x, y = W*0.5 + math.cos(a)*d*1.4, H*0.52 + math.sin(a)*d
        rock(x, y, rr.uniform(14, 40), 810 + i, "#141016", light=(W*0.5, H*0.52), rim="#7cc4ff")


@layer("a3/lamp3")
def a3_lamp3(b):
    x, y = b.w*0.5 - 9.4*8, b.h*0.52 + 90
    fl = lamp_n(x, y, 8.0, 3)
    return {"pivot": (x, y), "flames": fl}


@layer("a3/hand")
def a3_hand(b):
    W, H = b.w, b.h
    sx, sy = W + 30, H*0.62
    ex, ey = W*0.72, H*0.6
    hx, hy = W*0.63, H*0.5
    S.tube([(sx, sy), (ex, ey), (hx + 10, hy + 6)], 40, 32, K("#ece8dc"), lw=1.6, sh=0.25)
    hand = bez((hx - 16, hy + 10), (hx - 22, hy - 4), (hx - 10, hy - 14), (hx + 4, hy - 10)) + bez((hx + 4, hy - 10), (hx + 18, hy - 4), (hx + 18, hy + 12), (hx + 6, hy + 16))
    shape(hand, K("#e4b38f"), 1.5)
    finger = [(hx - 10, hy - 8), (hx - 14, hy - 44), (hx - 6, hy - 46), (hx - 2, hy - 10)]
    shape(finger, K("#e4b38f"), 1.4)
    for k in range(3):
        stroke(bez((hx - 2 + k*5, hy - 6), (hx + 2 + k*5, hy - 14), (hx + 8 + k*5, hy - 12), (hx + 8 + k*5, hy - 4)), 1.0)
    return {"pivot": (sx, sy)}


# ================================================================== act4_intro: Poslední šichta
A4_RIVER = (0.24, 0.36)


@layer("a4/sky", 1920, 1620)
def a4_sky(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#08070e"), (0.25, "#1a1630"), (0.38, "#2e2850"), (0.6, "#1c1830"), (1, "#0a0812")])
    crayon_over(rect(0, H*0.3, W, H), "#3a3466", 0.35, 11)
    stars(0, H*0.4, W, H*0.75, 40, 61, h="#b8b0ff", big=0.03)


@layer("a4/roots", 1920, 1620)
def a4_roots(b):
    W, H = b.w, b.h
    mass = [(-20, H + 20)] + [(x, H - 60 - 40*math.sin(x/70) - 20*math.sin(x/23)) for x in range(-20, int(W) + 40, 30)] + [(W + 20, H + 20)]
    shape(mass, K("#120e16"), 1.6)
    crayon_over(mass, "#2a2236", 0.5, 62)
    for k in range(9):
        rr = random.Random(900 + k)
        x = W*(0.05 + 0.9*k/8) + rr.uniform(-20, 20)
        pts = [(x, H)]
        xx, yy = x, H
        L = rr.uniform(260, 470)
        for j in range(10):
            xx += rr.uniform(-18, 18); yy -= L/10; pts.append((xx, yy))
        stroke(pts, rr.uniform(9, 16)); stroke(pts, rr.uniform(5, 9), g=K("#1e1824"))
        stroke(pts, 1.0, g=K("#6a5ad8"), alpha=0.35)
        glow(xx, yy, 30, "#7a6ae8", 0.25, 10)
    roots(0, W, H - 70, 30, 63, col="#1e1824", lmin=80, lmax=300, lw=2.6)


@layer("a4/far", 1920, 1620)
def a4_far(b):
    W, H = b.w, b.h
    ry1 = H*A4_RIVER[1]
    for i in range(3):
        rr = random.Random(50 + i)
        far = [(-20, ry1 - 4)] + jag(-20, W + 20, ry1 + 40 + 30*i + rr.uniform(0, 20), 22, 70, 60 + i) + [(W + 20, ry1 - 4)]
        shape(far, K(mix("#2c2848", "#141224", i/2)), 0.9)
    kalinov_bridge(W*0.7, ry1 - 4, 1.3)
    return {"bridge": (W*0.7, ry1 + 20)}


@layer("a4/river", 2880, 1620)
def a4_river(b):
    W, H = b.w, b.h
    ry0, ry1 = H*A4_RIVER[0], H*A4_RIVER[1]
    flat(rect(0, ry0, W, ry1), "#05040a")
    for k in range(40):
        rr = random.Random(200 + k)
        yy = ry0 + (ry1 - ry0)*rr.random(); xx = rr.uniform(0, W)
        stroke([(xx, yy), (xx + rr.uniform(40, 160), yy)], 0.8, g=K(rr.choice(("#6a5aa8", "#ff5a3a", "#8a6ad8"))), alpha=0.4)
    mist(-40, W + 40, ry1 + 6, 22, "#8a7ad8", 0.4, 12, 18)


@layer("a4/near", 1920, 1620)
def a4_near(b):
    W, H = b.w, b.h
    ry0 = H*A4_RIVER[0]
    bank = [(-20, -20), (-20, ry0 + 10)] + jag(-20, W*0.7, ry0 + 6, 6, 40, 31) + [(W*0.78, ry0 - 4), (W*0.9, ry0 - 20), (W + 20, ry0 - 24), (W + 20, -20)]
    shape(bank, K("#14121c"), 1.3)
    crayon_over(bank, "#2a2638", 0.5, 12)
    mist(-40, W + 40, ry0 - 10, 30, "#7a6ac8", 0.35, 14, 12)


A4_FIRE = (0.47, 0.22)


@layer("a4/camp", 2400)
def a4_camp(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#0a0812"), (0.5, "#1c1830"), (0.8, "#141024"), (1, "#08070e")])
    crayon_over(rect(0, H*0.5, W, H), "#2a2448", 0.3, 71)
    roots(0, W, H, 30, 72, lmin=40, lmax=140)
    for i in range(2):
        rr = random.Random(73 + i)
        far = [(-20, H*0.66)] + jag(-20, W + 20, H*(0.72 + 0.04*i) + rr.uniform(0, 10), 14, 60, 74 + i) + [(W + 20, H*0.66)]
        shape(far, K(mix("#2a2646", "#161428", i)), 0.9)
    kalinov_bridge(W*0.86, H*0.68, 0.7)
    flat(rect(0, H*0.6, W, H*0.68), "#05040a")
    for k in range(30):
        rr = random.Random(76 + k)
        yy = H*(0.6 + 0.08*rr.random()); xx = rr.uniform(0, W)
        stroke([(xx, yy), (xx + rr.uniform(30, 120), yy)], 0.7, g=K("#6a5aa8"), alpha=0.4)
    bank = [(-20, -20), (-20, H*0.6)] + jag(-20, W + 20, H*0.6, 5, 40, 77) + [(W + 20, -20)]
    shape(bank, K("#15131d"), 1.3)
    crayon_over(bank, "#2a2638", 0.5, 78)
    cx, cy = W*A4_FIRE[0], H*A4_FIRE[1]
    tent = [(W*0.1, H*0.38), (W*0.16, H*0.55), (W*0.22, H*0.38)]
    shape(tent, K("#2a2838"), 1.2); offset_shadow(tent, 18, 0, 0.35)
    shape([(W*0.155, H*0.38), (W*0.16, H*0.48), (W*0.17, H*0.38)], K("#06060a"), 0.8)
    lamps = []
    rr = random.Random(79)
    for row, (yy, ss, n) in enumerate(((0.54, 0.55, 14), (0.47, 0.7, 12), (0.39, 0.85, 10))):
        for k in range(n):
            x = W*(0.05 + 0.9*(k + rr.uniform(0.1, 0.9))/n)
            if abs(x - cx) < 90 and row == 2:
                continue
            fl = rr.random() < 0.5
            miner_sit(x, H*yy + rr.uniform(-6, 6), ss, flip=fl)
            lamps.append((x + (-28 if fl else 28)*ss + 9.4*0.8*ss, H*yy + 17*ss - 10.3*0.8*ss))
    glow(cx, cy + 10, 200, "#6a7ad8", 0.35, 18, ry=80)
    ash = ell(cx, cy, 40, 10, 24)
    shape(ash, K("#3a3a44"), 1.0)
    for k in range(5):
        rr2 = random.Random(400 + k)
        stroke([(cx - 28 + k*14, cy + 2), (cx - 34 + k*16 + rr2.uniform(-6, 6), cy + 24)], 2.4)
        stroke([(cx - 28 + k*14, cy + 2), (cx - 34 + k*16 + rr2.uniform(-6, 6), cy + 24)], 1.0, g=K("#2a2220"))
    seats = [(cx - 150, cy - 6, 1.9, False), (cx - 90, cy + 34, 1.6, False), (cx + 80, cy + 36, 1.55, True), (cx - 300, cy + 30, 1.5, False)]
    for sx, sy, ss, fl in sorted(seats, key=lambda t: -t[1]):
        glow(sx, sy + 40*ss, 60*ss, "#8aa0e8", 0.2, 10)
        shape(ell(sx, sy - 2, 16*ss, 6*ss, 16), K("#24222e"), 0.9)
        miner_sit(sx, sy + 2*ss, ss, flip=fl)
        lamps.append((sx + (-28 if fl else 28)*ss + 9.4*0.8*ss, sy + 2*ss + 17*ss - 10.3*0.8*ss))
    mist(-40, W + 40, H*0.5, 30, "#7a6ac8", 0.35, 81, 14)
    return {"fire": (cx, cy + 14), "lamps": lamps}


A4_SEAT = (A4_FIRE[0] + 0.12, A4_FIRE[1] - 0.005)


@layer("a4/log", 2400)
def a4_log(b):
    x, y = b.w*A4_SEAT[0], b.h*A4_SEAT[1]
    log = [(x - 46, y - 10), (x + 46, y - 10), (x + 50, y + 4), (x + 46, y + 16), (x - 46, y + 16), (x - 50, y + 4)]
    shape(log, K("#2a2030"), 1.4)
    crayon_over(log, "#3a3048", 0.5, 82)
    shape(ell(x + 47, y + 3, 6, 13, 18), K("#4a3a40"), 1.1)
    for k in range(3):
        stroke(ell(x + 47, y + 3, 4 - k*1.2, 10 - k*3, 16), 0.5, closed=True, alpha=0.7)
    for k in range(4):
        stroke([(x - 40 + k*22, y + 12), (x - 28 + k*22, y + 10)], 0.6, alpha=0.6)


def _a4_perm(b, grin):
    x, y = b.w*A4_SEAT[0] + 4, b.h*A4_SEAT[1] + 4
    permonik(x, y, 1.75, lamp_up=False, grin=grin)
    return {"pivot": (x, y)}


@layer("a4/perm", 2400)
def a4_perm(b):
    return _a4_perm(b, False)


@layer("a4/perm_grin", 2400)
def a4_perm_grin(b):
    return _a4_perm(b, True)


# ================================================================== final: Srdce hory
F_LAMP = (0.4, 0.5)


@layer("f/bg")
def f_bg(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#06050a"), (0.5, "#141220"), (1, "#08070c")])
    crayon_over(rect(0, 0, W, H), "#2a2638", 0.4, 21)
    walls = [[(-20, -20), (-20, H + 20), (W*0.14, H + 20), (W*0.2, H*0.7), (W*0.12, H*0.36), (W*0.18, -20)],
             [(W + 20, -20), (W + 20, H + 20), (W*0.86, H + 20), (W*0.8, H*0.66), (W*0.9, H*0.4), (W*0.84, -20)]]
    for i, w in enumerate(walls):
        shape(w, K("#1a1722"), 1.6)
        crayon_over(w, "#2e2a3a", 0.5, 22 + i)
        ore_veins(w, 5, 30 + i, min(p[0] for p in w), 0, max(p[0] for p in w), H)
    stalactites(W*0.1, W*0.9, H, 23, "#100e16", 18, 30, 120)
    roots(W*0.2, W*0.8, H, 14, 24, col="#2a1e14", lmin=30, lmax=110, lw=1.6)
    ledge = [(W*0.56, -20), (W*0.58, H*0.26), (W*0.7, H*0.3), (W*0.82, H*0.27), (W*0.86, -20)]
    shape(ledge, K("#1e1a26"), 1.6)
    crayon_over(ledge, "#322c40", 0.5, 25)
    return {"ledge": (W*0.7, H*0.29)}


F_PERM = (0.69, 0.285, 2.2)


@layer("f/perm")
def f_perm(b):
    fx, fy, s = F_PERM
    x, y = b.w*fx, b.h*fy
    hx, hy = permonik(x, y, s, flip=True, high=True, grin=True)
    return {"pivot": (x, y), "hand": (hx, hy)}


F_HERO = (0.1, 0.04, 2.3, -8)


@layer("f/hero")
def f_hero(b):
    W, H = b.w, b.h
    fx, fy, s, r = F_HERO
    x, y = W*fx, H*fy
    lx, ly = W*F_LAMP[0], H*F_LAMP[1]
    hero_silhouette(x, y, s, rim="#9fd8ff", reach=True, arm_to=to_local(x, y, s, r, lx - 4, ly + 4), rot=r)
    return {"pivot": (x, y)}


@layer("f/lamp")
def f_lamp(b):
    x, y = b.w*F_LAMP[0], b.h*F_LAMP[1]
    fl = lamp_n(x, y, 2.4, 4, body="#4a4a58")
    return {"pivot": (x, y), "flame": fl[0]}


F_BIG = (0.35, 0.66, 4.6)


@layer("f/giant")
def f_giant(b):
    W, H = b.w, b.h
    lx, ly, LS = W*F_BIG[0], H*F_BIG[1], F_BIG[2]
    cxl, cyl = lx + 9, ly - 14*LS
    torso = [(W*0.5, -20), (W*0.47, H*0.3), (W*0.52, H*0.56), (W*0.6, H*0.7), (W*0.88, H*0.72), (W + 20, H*0.64), (W + 20, -20)]
    shape(torso, K("#201d26"), 2.0)
    crayon_over(torso, "#38343f", 0.45, 22)
    for k in range(14):
        rr = random.Random(30 + k)
        x0_ = rr.uniform(W*0.5, W); y0_ = rr.uniform(0, H*0.7)
        stroke([(x0_, y0_), (x0_ + rr.uniform(-50, 50), y0_ + rr.uniform(10, 50)), (x0_ + rr.uniform(-70, 70), y0_ + rr.uniform(40, 90))], 1.2, alpha=0.8)
    ore_veins(torso, 6, 7, W*0.5, 0, W, H*0.7)
    roots(W*0.55, W, H*0.72, 9, 9, col="#2a1e14", lmin=30, lmax=110, lw=1.6)
    giant_head(W*0.77, H*0.68, 1.2)
    arm = [(W*0.66, H*0.48), (W*0.56, H*0.56), (cxl + 70, cyl + 20)]
    ao = S.tube(arm, 110, 74, K("#2a2630"), lw=2.0, sh=0.3)
    ore_veins(ao, 3, 13, cxl + 40, cyl - 40, W*0.66, H*0.7)
    palm = [(lx + 30, ly + 34), (lx + 90, ly + 50), (lx + 104, ly - 4), (lx + 70, ly - 30), (lx + 24, ly - 14)]
    shape(palm, K("#2e2a34"), 1.8)
    for k in range(4):
        fy = ly + 26 - k*11
        fing = [(lx + 40, fy + 6), (lx + 4, fy + 8 - k), (lx - 16, fy + 2 - k*2), (lx - 18, fy - 6 - k*2), (lx - 6, fy - 7 - k), (lx + 40, fy - 6)]
        shape(fing, K("#36323e"), 1.5)
        offset_shadow(fing, 0, -3, 0.35)
    return {"eyes": [(W*0.77 - 22*1.2, H*0.68 + 26*1.2), (W*0.77 + 22*1.2, H*0.68 + 26*1.2)], "hold": (lx, ly + 40)}


@layer("f/lamp_big")
def f_lamp_big(b):
    lx, ly, LS = b.w*F_BIG[0], b.h*F_BIG[1], F_BIG[2]
    fl = lamp_n(lx, ly, LS, 4, body="#4a4a58")
    return {"pivot": (lx, ly), "flames": fl, "center": (lx + 9, ly - 14*LS)}


@layer("f/rays")
def f_rays(b):
    x, y = b.w/2, b.h/2
    rays(x, y, 20, 700, 40, "#d8f0ff", 0.12, 5, 10)
    return {"pivot": (x, y)}


for _k, (_kind, _col) in enumerate(SEALS):
    def _seal_fn(b, kind=_kind, col=_col):
        seal(b.w/2, b.h/2, kind, col, 17)
        return {"pivot": (b.w/2, b.h/2)}
    layer("f/seal_" + _kind)(_seal_fn)


@layer("f/shard")
def f_shard(b):
    x, y = b.w/2, b.h/2
    sh = [(x - 14, y - 4), (x + 3, y - 8), (x + 14, y + 2), (x - 3, y + 6)]
    S.fill(sh, K("#e8f6ff"), 0.9); stroke(sh, 0.9, closed=True, g=K("#3a6a9a"))
    return {"pivot": (x, y)}


@layer("f/shard2")
def f_shard2(b):
    x, y = b.w/2, b.h/2
    shape([(x - 10, y - 6), (x + 8, y - 4), (x + 11, y + 5), (x - 6, y + 7)], K("#4a4a58"), 1.0)
    return {"pivot": (x, y)}


# ================================================================== epilogue: Zvon zase zvoní
@layer("e/sky", 2400)
def e_sky(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#2a1c2c"), (0.3, "#e0905a"), (0.36, "#f2b870"), (0.45, "#c4786a"), (0.62, "#6a4a72"), (0.85, "#2a2a52"), (1, "#181a36")])
    glow(W*0.46, H*0.3, 240, "#ffd890", 0.6, 30, ry=120)
    S.fill(ell(W*0.46, H*0.3, 44, 44, 40), K("#fff0c0"), 1.0)
    stars(0, H*0.8, W, H, 30, 41, big=0.05)


@layer("e/far", 2400)
def e_far(b):
    W, H = b.w, b.h
    hora_hills(W, H, "#5a3a52")
    mist(0, W, H*0.34, 22, "#f2b880", 0.45, 2)
    cathedral(W*0.62, H*0.30, 1.62, wall="#4a3448", roof="#3a2638", edge="#ffc078", lit="#ffcf7a")
    bx, by, bs = HORA_BELL
    belfry(W*bx, H*by, bs, wall="#4a3448", roof="#3a2638", edge="#ffc078", draw_bell=False)


@layer("e/bell", 2400)
def e_bell(b):
    bx, by, bs = HORA_BELL
    x, y = b.w*bx, b.h*by + 136*bs
    with T(x, y, bs):
        bell_shape(0, 0, 0, "#8a6a3a")
    return {"pivot": (x, y)}


@layer("e/ring", 2400)
def e_ring(b):
    bx, by, bs = HORA_BELL
    x, y = b.w*bx, b.h*by + 136*bs - 18
    for k in range(3):
        stroke(ell(x, y, 46 + k*18, 40 + k*16, 30, -50, 50), 1.6, g=K("#ffe0a0"), alpha=0.8 - k*0.2)
        stroke(ell(x, y, 46 + k*18, 40 + k*16, 30, 130, 230), 1.6, g=K("#ffe0a0"), alpha=0.8 - k*0.2)
    return {"pivot": (x, y)}


@layer("e/town", 2400)
def e_town(b):
    W, H = b.w, b.h
    lights = town_row(-20, W+20, H*0.30, 11, "#3a2a3e", "#2c1e30", 26, 50, 0.2, win="#5a3c34", edge="#f2a060", wmin=34, wmax=58)
    return {"lights": lights}


@layer("e/near", 2400)
def e_near(b):
    W, H = b.w, b.h
    flat(rect(0, 0, W, H*0.2), "#140f18")
    lights = town_row(-40, W+40, H*0.17, 5, "#22182a", "#1a1220", 38, 64, 0.25, win="#4a3030", wmin=52, wmax=86, lw=1.3, edge="#e08850")
    with T(W + 20, 0, 1.0, True):
        fg_roof(0, 0, ROOF[2], col="#140f18", rim="#e08850", with_crow=False)
    return {"lights": lights}


def kid(x, y, s, frame, braids=False, col="#120d14", rim="#f2a060"):
    with T(x, y, s):
        legs = (((-2, 16), (-6, 8), (-11, 2)), ((2, 16), (6, 8), (9, 0))) if frame == 0 else (((-1, 16), (-2, 8), (-6, 0)), ((1, 16), (5, 9), (3, 1)))
        for lg in legs:
            S.tube(list(lg), 3.4, 2.8, K(col), lw=0.9, sh=0)
        body = [(-5, 15), (5, 15), (4, 30), (-4, 30)] if not braids else [(-8, 13), (8, 13), (4, 30), (-4, 30)]
        shape(body, K(col), 1.0)
        arms = ((-3, 28), (-9, 22), (-12, 26)) if frame == 0 else ((-3, 28), (2, 21), (8, 24))
        S.tube(list(arms), 3, 2.6, K(col), lw=0.9, sh=0)
        shape(ell(0, 36, 5.2, 5.5, 20), K(col), 1.0)
        stroke(ell(0, 36, 5.2, 5.5, 20, 30, 150), 1.0, g=K(rim), alpha=0.7)
        if braids:
            for side in (-1, 1):
                stroke([(side*4, 36), (side*7, 30), (side*7, 26)], 1.8, g=K(col))
        stroke([(5, 30), (4, 16)], 0.9, g=K(rim), alpha=0.6)


E_KIDS = (0.18, 0.15, 1.15)


def _kid(b, frame, braids, dx):
    fx, fy, s = E_KIDS
    x, y = b.w*fx + dx, b.h*fy
    kid(x, y, s, frame, braids)
    return {"pivot": (x, y)}


@layer("e/kid_a", 2400)
def e_kid_a(b): return _kid(b, 0, False, 0)


@layer("e/kid_b", 2400)
def e_kid_b(b): return _kid(b, 1, False, 0)


@layer("e/girl_a", 2400)
def e_girl_a(b): return _kid(b, 1, True, -40)


@layer("e/girl_b", 2400)
def e_girl_b(b): return _kid(b, 0, True, -40)


@layer("e/nav")
def e_nav(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#05040a"), (0.55, "#12102a"), (0.75, "#0c0a1a"), (1, "#05040a")])
    crayon_over(rect(0, 0, W, H), "#1e1a36", 0.3, 91)
    roots(0, W, H, 24, 92, lmin=40, lmax=160)
    flat(rect(0, H*0.52, W, H*0.58), "#040308")
    for k in range(20):
        rr = random.Random(93 + k)
        yy = H*(0.52 + 0.06*rr.random()); xx = rr.uniform(0, W)
        stroke([(xx, yy), (xx + rr.uniform(30, 120), yy)], 0.7, g=K("#5a4a98"), alpha=0.4)
    bank = [(-20, -20), (-20, H*0.52)] + jag(-20, W + 20, H*0.52, 4, 40, 94) + [(W + 20, -20)]
    shape(bank, K("#100e18"), 1.2)
    crayon_over(bank, "#221e30", 0.45, 95)
    lamps = []
    rr = random.Random(96)
    for yy, ss, n in ((0.48, 0.45, 12), (0.42, 0.6, 12), (0.33, 0.82, 11), (0.22, 1.12, 9), (0.08, 1.5, 6)):
        for k in range(n):
            x = W*(0.04 + 0.92*(k + rr.uniform(0.15, 0.85))/n)
            y = H*yy + rr.uniform(-5, 5)
            fl = rr.random() < 0.5
            miner_sit(x, y, ss, flip=fl, ghost=0.5)
            lamps.append((x + (-28 if fl else 28)*ss + 9.4*0.8*ss, y + 17*ss - 10.3*0.8*ss))
    return {"lamps": lamps}


@layer("e/study")
def e_study(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#140c0a"), (0.5, "#24160f"), (1, "#120a08")])
    for row in range(14):
        y = H*0.3 + row*28
        off = 30 if row % 2 else 0
        for k in range(12):
            x = -40 + off + k*90
            st = rect(x + 2, y + 2, x + 88, y + 26)
            S.fill(st, K("#2e2018"), 0.7); stroke(st, 0.6, closed=True, alpha=0.5)
    crayon_over(rect(0, H*0.3, W, H), "#4a3424", 0.35, 101)
    wx, wy = W*0.78, H*0.6
    win = [(wx - 60, wy - 80)] + [(wx + 60, wy - 80), (wx + 60, wy + 40)] + bez((wx + 60, wy + 40), (wx + 60, wy + 110), (wx - 60, wy + 110), (wx - 60, wy + 40))
    shape(win, K("#141a3a"), 1.6)
    stars(wx - 55, wy - 75, wx + 55, wy + 60, 14, 102)
    S.fill(ell(wx + 26, wy + 50, 12, 12, 24), K("#efe8d0"), 1.0)
    stroke([(wx, wy - 80), (wx, wy + 95)], 3.0); stroke([(wx - 60, wy + 10), (wx + 60, wy + 10)], 3.0)
    for k in range(9):
        rr = random.Random(103 + k)
        bx = W*0.06 + k*26
        bk = rect(bx, H*0.66, bx + rr.uniform(16, 24), H*0.66 + rr.uniform(60, 90))
        shape(bk, K(rr.choice(("#5a2a22", "#2a3a4a", "#4a4a22", "#3a2a3a"))), 1.0)
    shape(rect(W*0.04, H*0.64, W*0.32, H*0.66), K("#3a2618"), 1.2)
    ks, kx, ky = 1.9, W*0.5, H*0.32
    with T(kx, ky, ks):
        robe = K("#4a2a26"); skin = K("#e2b48e"); beard = K("#e6e2da")
        body = [(-80, -30)] + bez((-76, 20), (-66, 50), (-46, 70), (-20, 76)) + bez((-20, 76), (0, 80), (20, 76), (40, 70)) + bez((40, 70), (62, 52), (74, 22), (78, -30))
        shape(body, robe, 1.4)
        offset_shadow(body, -12, 4, 0.35)
        head = ell(4, 96, 24, 24, 30)
        shape(head, skin, 1.3)
        cap = bez((-22, 104), (-22, 128), (28, 128), (28, 104)) + bez((28, 104), (12, 112), (-6, 112), (-22, 104))
        shape(cap, K("#2a1a18"), 1.2)
        for ex in (-1, 1):
            stroke(ell(4 + ex*10, 92, 7, 5, 20), 1.3, closed=True)
            S.fill(ell(4 + ex*10, 92, 7, 5, 20), K("#ffd28a"), 0.35)
            stroke([(4 + ex*10 - 4, 91), (4 + ex*10 + 4, 91)], 1.0)
        bd = bez((-18, 88), (-20, 60), (-6, 30), (6, 22)) + bez((6, 22), (16, 32), (28, 60), (26, 88))
        shape(S.notch(bd, 1.2, 4), beard, 1.2)
        for bx in (-6, 0, 6, 12):
            stroke(bez((bx, 80), (bx*1.2, 64), (bx, 48), (bx*0.6, 32)), 0.6, g=K("#a8a49a"))
        S.tube([(40, 60), (60, 20), (40, -6)], 16, 13, robe, lw=1.2, sh=0.2)
        S.tube([(-40, 60), (-58, 24), (-30, 0)], 16, 13, robe, lw=1.2, sh=0.2)
        shape(ell(-28, 0, 8, 6, 16), skin, 1.0)
        shape(ell(38, -6, 8, 6, 16), skin, 1.0)
    desk = [(-20, -20), (-20, H*0.3), (W + 20, H*0.3), (W + 20, -20)]
    shape(desk, K("#3a2416"), 1.6)
    crayon_over(desk, "#5a3a22", 0.5, 104)
    stroke([(-20, H*0.3), (W + 20, H*0.3)], 3.0, g=K("#6a4a2a"))
    bx0, by0 = W*0.36, H*0.08
    pages = [[(bx0, by0), (bx0 + 150, by0 + 6), (bx0 + 150, by0 + 96), (bx0 + 6, by0 + 90)],
             [(bx0 + 150, by0 + 6), (bx0 + 300, by0), (bx0 + 294, by0 + 90), (bx0 + 150, by0 + 96)]]
    shape([(bx0 - 8, by0 - 6), (bx0 + 308, by0 - 6), (bx0 + 302, by0 + 96), (bx0 - 2, by0 + 96)], K("#3a1a10"), 1.3)
    for pg in pages:
        shape(pg, K("#efe2c0"), 1.1)
    for k in range(9):
        y = by0 + 80 - k*8
        stroke([(bx0 + 16, y), (bx0 + 136, y + 2)], 0.6, g=K("#5a4030"), alpha=0.7)
    stroke([(bx0 + 166, by0 + 80), (bx0 + 230, by0 + 80)], 0.7, g=K("#3a2418"))
    cx, cy = W*0.2, H*0.08
    shape(rect(cx - 7, cy, cx + 7, cy + 60), K("#efe6cc"), 1.0)
    shape(ell(cx, cy, 22, 6, 20), K("#6a5a40"), 1.0)
    stroke([(cx, cy + 60), (cx, cy + 66)], 0.8)
    flame(cx, cy + 64, 2.4)
    ix, iy = W*0.72, H*0.1
    shape(bez((ix - 16, iy), (ix - 20, iy + 20), (ix + 20, iy + 20), (ix + 16, iy)) + [(ix - 16, iy)], K("#141218"), 1.1)
    return {"candle": (cx, cy + 74), "nib": (bx0 + 230, by0 + 80)}


@layer("e/quill")
def e_quill(b):
    W, H = b.w, b.h
    x, y = W*0.36 + 230, H*0.08 + 80
    shaft_ = [(x, y), (x + 70, y + 110)]
    vane = bez((x + 22, y + 30), (x + 6, y + 70), (x + 40, y + 120), (x + 74, y + 116)) + bez((x + 74, y + 116), (x + 70, y + 80), (x + 54, y + 50), (x + 22, y + 30))
    shape(vane, K("#efeae0"), 1.1)
    for k in range(8):
        t = 0.3 + k*0.08
        px, py = x + 70*t, y + 110*t
        stroke([(px, py), (px - 14, py + 10)], 0.5, alpha=0.6)
    stroke(shaft_, 1.4)
    return {"pivot": (x, y)}


# ================================================================== dlc_tease: Pod Navem
D_EYE = (0.42, 0.58)


def _d_almond(cx, cy):
    up = bez((cx - 250, cy), (cx - 120, cy + 76), (cx + 130, cy + 76), (cx + 260, cy + 4))
    lo = bez((cx + 260, cy + 4), (cx + 120, cy - 44), (cx - 120, cy - 44), (cx - 250, cy))
    seam = bez((cx + 260, cy + 4), (cx + 120, cy - 40), (cx - 120, cy - 40), (cx - 250, cy))
    return up, lo, seam


@layer("d/face")
def d_face(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#030205"), (0.5, "#0b0710"), (1, "#040306")])
    cx, cy = W*D_EYE[0], H*D_EYE[1]
    glow(cx + 80, cy, 560, "#2a0a1e", 0.6, 30, ry=300)
    face = [(-20, H + 20), (-20, -20), (W + 20, -20), (W + 20, H + 20)]
    crayon_over(face, "#2a1a26", 0.35, 51)
    rim = "#6a1a2a"
    stroke(bez((cx - 380, cy + 150), (cx - 200, cy + 230), (cx + 160, cy + 220), (cx + 330, cy + 120)), 2.2, g=K(rim), alpha=0.8)
    stroke(bez((cx + 330, cy + 120), (cx + 380, cy + 60), (cx + 400, cy - 60), (cx + 470, cy - 200)), 2.2, g=K(rim), alpha=0.7)
    stroke(bez((cx - 300, cy - 110), (cx - 120, cy - 170), (cx + 140, cy - 160), (cx + 300, cy - 90)), 1.6, g=K(rim), alpha=0.6)
    horn = bez((W*0.8, H + 20), (W*0.86, H*0.8), (W*0.98, H*0.74), (W + 20, H*0.78)) + [(W + 20, H + 20)]
    S.fill(horn, K("#08060a"), 1.0)
    stroke(horn[:-1], 1.8, g=K(rim), alpha=0.85)
    for k, (sx, sh) in enumerate(((0.06, 70), (0.14, 110), (0.22, 60))):
        sp = [(W*sx - 30, H + 20), (W*sx, H - sh), (W*sx + 30, H + 20)]
        S.fill(sp, K("#08060a"), 1.0); stroke(sp, 1.4, g=K(rim), alpha=0.6)
    for k in range(3):
        stroke(bez((cx - 270 - k*20, cy + 20 + k*28), (cx - 130, cy + 104 + k*30), (cx + 130, cy + 104 + k*30), (cx + 280 + k*20, cy + 24 + k*28)), 1.2, g=K("#3a1424"), alpha=0.9)
    for k in range(4):
        stroke(bez((cx - 240 + k*10, cy - 54 - k*24), (cx - 120, cy - 96 - k*26), (cx + 120, cy - 96 - k*26), (cx + 250 - k*10, cy - 50 - k*24)), 1.1, g=K("#3a1424"), alpha=0.8)
    up, lo, seam = _d_almond(cx, cy)
    S.fill(up + lo, K("#0a0508"), 1.0)
    lx, ly = W*0.5, H*0.05
    flame(lx, ly + 8, 0.9, cold=True)
    return {"eye": (cx, cy), "flame": (lx, ly + 14)}


@layer("d/iris")
def d_iris(b):
    W, H = b.w, b.h
    cx, cy = W*D_EYE[0], H*D_EYE[1]
    up, lo, seam = _d_almond(cx, cy)
    C.saveState(); C.clipPath(S.poly(up + lo), stroke=0, fill=0)
    flat(up + lo, "#2a0808")
    glow(cx, cy + 14, 120, "#ff3a1a", 0.6, 20, ry=60)
    S.fill(ell(cx, cy + 14, 70, 44, 40), K("#c42a10"), 1.0)
    S.fill(ell(cx, cy + 14, 52, 34, 40), K("#ff7a2a"), 0.8)
    S.fill(ell(cx, cy + 14, 9, 40, 30), K("#050203"), 1.0)
    S.fill(ell(cx - 20, cy + 32, 6, 3, 12), K("#ffe0b0"), 0.8)
    C.restoreState()
    return {"pivot": (cx, cy + 14)}


@layer("d/lid")
def d_lid(b):
    W, H = b.w, b.h
    cx, cy = W*D_EYE[0], H*D_EYE[1]
    up, lo, seam = _d_almond(cx, cy)
    lid = up + seam
    S.fill(lid, K("#160c14"), 1.0)
    crayon_over(lid, "#3a1a2a", 0.5, 52)
    stroke(up, 2.0, g=K("#5a2236"))
    stroke(seam, 5.0)
    stroke(seam, 1.6, g=K("#ff5a3a"), alpha=0.75)
    for k in range(15):
        t = 0.08 + 0.84*k/14
        px = cx - 250 + 510*t; py = cy - 40*math.sin(math.pi*t) - 2
        stroke([(px, py), (px + (t - 0.5)*36, py - 30 - 12*math.sin(math.pi*t))], 1.8)
    return {"pivot": (cx, cy + 57)}


# ================================================================== thumbnails for the Story page
THUMBS = {
    "intro": (["intro/head_bg", "intro/hero_shadow", "intro/hero_reach", "intro/perm", "intro/lamp"], 0, 0),
    "act1_end": (["a1/cave", "a1/frame", "a1/fg", "a1/arm_lamp", "a1/flame2"], 0, 0),
    "act2_end": (["a2/sky", "a2/trees0", "a2/trees1", "a2/trees2", "a2/ground", "a2/fabian", "a2/hero", "a2/fog", "a2/fg"], 240, 0),
    "act3_end": (["a3/bg", "a3/beam", "a3/hero", "a3/kosmas"], 0, 0),
    "act4_intro": (["a4/camp", "a4/perm_grin", "a4/log"], 300, 0),
    "final": (["f/bg", "f/giant", "f/lamp_big"], 0, 0),
    "epilogue": (["e/sky", "e/far", "e/bell", "e/ring", "e/town", "e/near"], 0, 0),
    "dlc_tease": (["d/face", "d/iris", "d/lid"], 0, 0),
}


def thumbs(man):
    out = os.path.join(common.OUT, "cinema", "thumbs")
    os.makedirs(out, exist_ok=True)
    for film, (names, ox, oy) in THUMBS.items():
        if not all(n in man for n in names):
            continue
        cw, ch = man[names[0]]["cw"], man[names[0]]["ch"]
        im = Image.new("RGBA", (cw, ch), (0, 0, 0, 255))
        for n in names:
            e = man[n]
            im.alpha_composite(Image.open(os.path.join(common.OUT, "cinema", n + ".webp")).convert("RGBA"), (e["x"], e["y"]))
        im.crop((ox, oy, ox + 1920, oy + 1080)).convert("RGB").resize((480, 270), Image.LANCZOS).save(os.path.join(out, film + ".webp"), quality=88)


# ================================================================== main
def main():
    names = [a for a in sys.argv[1:] if not a.startswith("--")]
    todo = [n for n in LAYERS if not names or any(n == a or (a.endswith("/") and n.startswith(a)) for a in names)]
    man = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST) as f:
            man = json.load(f)
    with Pool(min(8, os.cpu_count() or 2)) as pool:
        for name, info in pool.imap_unordered(render_one, todo):
            man[name] = info
    man = {k: v for k, v in man.items() if k in LAYERS}
    with open(MANIFEST, "w") as f:
        json.dump(man, f, indent=1, sort_keys=True, ensure_ascii=False)
        f.write("\n")
    thumbs(man)


if __name__ == "__main__":
    main()
