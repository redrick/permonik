import math, random
import common
from lib import ell, bez, rrect
import style3 as S
from lib import C
from style3 import T, stroke, shape, form, hatch, offset_shadow
from slides_kit import *


def intro_1(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#2a1c2c"), (0.3, "#b0664a"), (0.38, "#8e4f56"), (0.55, "#4b3458"), (0.8, "#22213f"), (1, "#121429")])
    crayon_over(rect(0, H*0.3, W, H), "#3a3768", 0.35, 3)
    stars(0, H*0.62, W, H, 70, 4, big=0.06)
    glow(W*0.33, H*0.27, 380, "#ff9b5a", 0.35, 30, ry=110)
    hl = [(0, H*0.3)] + [(x, H*0.33 + 14*math.sin(x/90) + 8*math.sin(x/37)) for x in range(0, int(W)+20, 20)] + [(W, H*0.3), (W, 0), (0, 0)]
    shape(hl, K("#3a2c48"), 0.9)
    mist(0, W, H*0.33, 22, "#c98a7a", 0.4, 2)
    cathedral(W*0.64, H*0.30, 1.62)
    belfry(W*0.2, H*0.25, 1.62)
    for (bx, by, bs) in ((W*0.41, H*0.82, 1.0), (W*0.45, H*0.86, 0.8), (W*0.38, H*0.88, 0.7), (W*0.83, H*0.78, 0.9)):
        stroke(bez((bx-7*bs, by+2*bs), (bx-4*bs, by+5*bs), (bx-2*bs, by+3*bs), (bx, by)), 1.0)
        stroke(bez((bx, by), (bx+2*bs, by+3*bs), (bx+4*bs, by+5*bs), (bx+7*bs, by+2*bs)), 1.0)
    mist(0, W, H*0.36, 30, "#6e4a6a", 0.5, 5)
    lights = town_row(-20, W+20, H*0.30, 11, "#2c2536", "#211b2a", 26, 50, 0.12, edge="#b0664a", wmin=34, wmax=58)
    for lx, ly in lights: glow(lx, ly, 12, "#ffb85c", 0.25, 8)
    flat(rect(0, 0, W, H*0.2), "#0e0c13")
    lights = town_row(-40, W+40, H*0.17, 5, "#1b1722", "#14111a", 38, 64, 0.14, wmin=52, wmax=86, lw=1.3)
    for lx, ly in lights: glow(lx, ly, 16, "#ffb85c", 0.3, 8)
    fg_roof(-20, 0, 0.78)
    darken_bottom(b, 0.26, 0.85)
    vignette(b, 0.5)


def earth(x0, y0, x1, y1, seed=3, base="#2a221f", bands=("#332824", "#251e1c", "#3a2e28", "#1e1918"), veins=True):
    r = random.Random(seed)
    flat(rect(x0, y0, x1, y1), base)
    crayon_over(rect(x0, y0, x1, y1), "#4a3a30", 0.4, seed)
    y = y1
    while y > y0:
        th = r.uniform(25, 70)
        sl = r.uniform(-0.12, 0.12)
        top = [(px, py + (px - (x0+x1)/2)*sl) for px, py in jag(x0-10, x1+10, y, 9, 40, r.randrange(999))]
        bot = [(px, py + (px - (x0+x1)/2)*sl) for px, py in jag(x0-10, x1+10, y-th, 9, 40, r.randrange(999))]
        S.fill(top + list(reversed(bot)), K(r.choice(bands)), 0.75)
        stroke(top, 0.6, alpha=0.5)
        y -= th
    for i in range(int((x1-x0)*(y1-y0)/2500)):
        x, yy = r.uniform(x0, x1), r.uniform(y0, y1)
        rr = r.uniform(2, 7)
        pts = [(x + math.cos(a)*rr*r.uniform(0.7, 1.2), yy + math.sin(a)*rr*0.7*r.uniform(0.7, 1.2)) for a in [k*math.tau/7 for k in range(7)]]
        shape(pts, K(r.choice(("#4a3e36", "#3b322d", "#55483e"))), 0.6)
    if veins:
        for i in range(4):
            x, yy = r.uniform(x0, x1), r.uniform(y0, y1)
            pts = [(x, yy)]
            for k in range(8):
                x += r.uniform(8, 20); yy += r.uniform(-10, 10); pts.append((x, yy))
            stroke(pts, 1.6, g=K("#b9c2cc"), alpha=0.55)
            stroke(pts, 0.5, g=K("#ffffff"), alpha=0.6)


def shaft(x0, x1, y0, y1, crib="#4a3826"):
    flat(rect(x0, y0, x1, y1), "#0b0a0c")
    for y in range(int(y1), int(y0), -26):
        for xa, xb in ((x0-14, x0), (x1, x1+14)):
            beam = rect(xa, y-7, xb, y)
            shape(beam, K(crib), 0.8)
            offset_shadow(beam, 0, 2.5, 0.35)
    stroke([(x0, y0), (x0, y1)], 1.2); stroke([(x1, y0), (x1, y1)], 1.2)


def ladder(x0, y0, x1, y1, w=26, col="#6b5038", step=13):
    L = math.hypot(x1-x0, y1-y0); ux, uy = (x1-x0)/L, (y1-y0)/L; nx, ny = -uy, ux
    for side in (-0.5, 0.5):
        a = (x0 + nx*w*side, y0 + ny*w*side); b_ = (x1 + nx*w*side, y1 + ny*w*side)
        stroke([a, b_], 3.2); stroke([a, b_], 1.6, g=K(col))
    k = step/2
    while k < L:
        cx, cy = x0 + ux*k, y0 + uy*k
        stroke([(cx - nx*w/2, cy - ny*w/2), (cx + nx*w/2, cy + ny*w/2)], 2.2)
        stroke([(cx - nx*w/2, cy - ny*w/2), (cx + nx*w/2, cy + ny*w/2)], 1.0, g=K(col))
        k += step


def headframe(x, y, s, col="#2a2018", rim="#ffb35c"):
    with T(x, y, s):
        for px in (-40, 40):
            shape(rect(px-4, 0, px+4, 70), K(col), 1.1)
        roof = [(-60, 66), (60, 66), (0, 112)]
        shape(roof, K("#1a1512"), 1.3)
        offset_shadow(roof, 14, 0, 0.3)
        for k in range(1, 7): stroke([(-60 + k*8.5, 66 + k*6.5), (60 - k*8.5, 66 + k*6.5)], 0.5, alpha=0.6)
        shape(rect(-36, 40, 36, 46), K(col), 1.0)
        S.fill(ell(0, 43, 9, 9, 20), K("#3a2c20")); stroke(ell(0, 43, 9, 9, 24), 1.0, closed=True)
        for a in range(0, 360, 45):
            stroke([(0, 43), (math.cos(math.radians(a))*13, 43 + math.sin(math.radians(a))*13)], 1.0)
        stroke([(4, 43), (4, -10)], 0.9, g=K("#8a7a60"))
        stroke([(-60, 66), (0, 112)], 1.0, g=K(rim), alpha=0.5)


def intro_2(b):
    W, H = b.w, b.h
    gy = H*0.64
    grad(0, gy, W, H, [(0, "#3a3a5c"), (0.5, "#1e2140"), (1, "#101226")])
    stars(0, gy + 20, W, H, 50, 8)
    glow(W*0.9, H*0.93, 36, "#e8e2c8", 0.3, 12)
    S.fill(ell(W*0.9, H*0.93, 11, 11, 30), K("#efe8d0"), 1.0); stroke(ell(W*0.9, H*0.93, 11, 11, 30), 0.9, closed=True)
    hl = [(0, gy)] + [(x, gy + 30 + 16*math.sin(x/140+1) + 6*math.sin(x/41)) for x in range(0, int(W)+20, 20)] + [(W, gy)]
    shape(hl, K("#1f1d2c"), 0.9)
    earth(0, 0, W, gy, 7)
    sx0, sx1 = W*0.44, W*0.62
    shape([(0, gy - 10)] + jag(0, W, gy + 2, 2, 7, 2) + [(W, gy - 10)], K("#24261e"), 1.3)
    shaft(sx0, sx1, 0, gy, "#3f2f22")
    lad = (sx0 + 52, sx0 + 58)
    miners = ((gy - 110, 1.45, 0.4), (gy - 250, 1.3, 0.3))
    C.saveState(); C.clipPath(S.poly(rect(sx0 - 16, 0, sx1 + 16, gy)), stroke=0, fill=0)
    for my, s_, a in miners:
        glow(lad[0] + 16*s_, my + 50*s_, 110*s_, "#ffa94d", a, 26, ry=80*s_, power=1.0)
    C.restoreState()
    ladder(lad[0], gy + 40, lad[1], -20, 34, step=17)
    for i, (my, s_, a) in enumerate(miners):
        t = (gy - my)/gy
        hx, hy = miner_back(lad[0] + (lad[1]-lad[0])*t + 2, my, s_, shade=0.45, rail=12)
        lamp(hx + 2, hy, 0.95*s_, glow_r=0)
        flame(hx + 2 + 9.4*0.95*s_, hy - 10.3*0.95*s_, 0.9*s_)
    for i in range(30):
        flat(rect(sx0 - 16, 0, sx1 + 16, 170*(1 - i/30)), "#000000", 0.09)
    headframe((sx0+sx1)/2, gy - 6, 1.55)
    C.saveState(); C.clipPath(S.poly(rect(sx0 - 16, 0, sx1 + 16, gy)), stroke=0, fill=0)
    glow(lad[0] + 24, 40, 40, "#ffa94d", 0.35, 12)
    C.restoreState()
    flame(lad[0] + 24, 36, 0.5)
    for i, (mx, s_) in enumerate(((W*0.03, 1.6), (W*0.17, 1.75), (W*0.31, 1.8))):
        miner_side(mx, gy - 4, s_, "walk", seed=10+i, shade=0.4, glow_k=0.5)
    darken_bottom(b, 0.26, 0.9, "#000000")
    vignette(b, 0.55)



def planks(x0, x1, y0, y1, vx, vy, col="#2b2119", n=14, seed=4):
    """boards receding to a vanishing point"""
    r = random.Random(seed)
    flat(rect(x0, y0, x1, y1), col)
    crayon_over(rect(x0, y0, x1, y1), "#4a3a2c", 0.5, seed)
    for i in range(n + 1):
        x = x0 + (x1 - x0)*i/n
        t = (y1 - y0)/(vy - y0)
        stroke([(x, y0), (x + (vx - x)*t, y1)], 1.4, alpha=0.85)
        stroke([(x + 3, y0), (x + 3 + (vx - x - 3)*t, y1)], 0.8, g=K("#6a5440"), alpha=0.5)
    for k in range(9):
        y = y0 + (y1 - y0)*(1 - 0.72**(k+1))
        for j in range(n//3):
            i = r.randrange(n); xa = x0 + (x1 - x0)*i/n; xb = x0 + (x1 - x0)*(i+1)/n
            t = (y - y0)/(vy - y0)
            stroke([(xa + (vx - xa)*t, y), (xb + (vx - xb)*t, y)], 1.0, alpha=0.7)


def intro_3(b):
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
    hxp, hyp, hs, hr = W*0.3, H*0.08, 2.4, -10
    px, py, ps = hxp + 118, H*0.06, 1.75
    hand = (px + 21*ps, py + 62*ps)
    lx, ly = hand[0], hand[1] + 1
    glow(lx + 9, ly - 22, 330, "#7cc4ff", 0.5, 36, ry=240, power=1.2)
    C.saveState(); C.transform(0.8, 0.0, -0.85, 0.5, hxp, hyp)
    hero_silhouette(0, 0, hs, col="#07070c", rim="#07070c", reach=True, arm_to=(40, 70))
    C.restoreState()
    hero_silhouette(hxp, hyp, hs, rim="#8fd0ff", reach=True, arm_to=to_local(hxp, hyp, hs, hr, lx + 3, ly + 2), rot=hr)
    permonik(px, py, ps, high=True)
    lamp(lx, ly, ps*0.9, cold=True, glow_r=120, glow_a=0.6, body="#5a4a3a")
    darken_bottom(b, 0.24, 0.7)
    vignette(b, 0.6)


def stalactites(x0, x1, y, seed, col, n=14, lmin=20, lmax=90, up=False, lw=1.0):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(x0, x1); w = r.uniform(8, 26); L = r.uniform(lmin, lmax)
        d = 1 if up else -1
        pts = [(x - w/2, y - d*10)] + bez((x - w/2, y), (x - w*0.3, y + d*L*0.5), (x - 1, y + d*L*0.8), (x, y + d*L)) + \
              bez((x, y + d*L), (x + 1, y + d*L*0.8), (x + w*0.3, y + d*L*0.5), (x + w/2, y))[1:] + [(x + w/2, y - d*10)]
        shape(pts, K(col), lw)
        offset_shadow(pts, w*0.3, 0, 0.3)


def cave_frame(b, col="#0a0b0f", seed=5, top=0.86, side=0.1, lw=1.6):
    W, H = b.w, b.h
    r = random.Random(seed)
    inner = []
    for i in range(61):
        t = i/60; a = math.pi*(1 - t)
        k = 1 + 0.07*math.sin(t*9 + seed) + r.uniform(-0.04, 0.04)
        x = W/2 + math.cos(a)*W*(0.5 - side)*k
        y = H*0.05 + math.sin(a)*H*(top - 0.05)*k + (1 - math.sin(a))*H*0.1 + 25*math.sin(t*5 + seed)*math.sin(a)
        inner.append((x, y))
    outer = [(W + 20, inner[-1][1]), (W + 20, H + 20), (-20, H + 20), (-20, inner[0][1])]
    pts = inner + outer
    shape(pts, K(col), lw)
    return inner


def act1_end(b):
    W, H = b.w, b.h
    wy = H*0.36
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
    rr = random.Random(77)
    souls = []
    for i in range(15):
        x = W*(0.12 + 0.76*rr.random()); y = wy + 30 + rr.random()**0.8*(H*0.6)
        souls.append((x, y, 0.6 + 0.9*rr.random()*(y/H) + 0.3))
    for x, y, s_ in souls:
        for j in range(4):
            yy = wy - 5 - j*7 - (y - wy)*0.05*j; hw = (10 - j*2)*s_
            stroke([(x - hw + rr.uniform(-2, 2), yy), (x + hw, yy + rr.uniform(-0.5, 0.5))], 0.9, g=K("#cfefff"), alpha=0.35 - j*0.06)
    rocks = [(W*0.27, wy - 6, 70, 26), (W*0.55, wy - 10, 90, 30), (W*0.8, wy - 4, 60, 22)]
    for i, (x, y, rw, rh) in enumerate(rocks):
        rp = bez((x - rw, y - 4), (x - rw*0.7, y + rh), (x + rw*0.5, y + rh*1.1), (x + rw, y - 4))
        shape(rp, K("#1b2a30"), 1.2)
        offset_shadow(rp, -rw*0.3, 0, 0.35)
        for j in range(3):
            teacup(x - rw*0.5 + j*rw*0.5, y + rh*0.75 - abs(j - 1)*rh*0.2 + 8, 1.5, rot=180 + (j - 1)*12, seed=i*3 + j, inner="#bfe6ff")
            soul(x - rw*0.5 + j*rw*0.5, y + rh + 34 + j*10, 0.7 + 0.15*j, seed=i*3 + j)
    for x, y, s_ in souls:
        soul(x, y, s_*1.3, seed=int(x))
    fg = [(-20, -20), (-20, H*0.3), (W*0.08, H*0.27), (W*0.17, H*0.2), (W*0.23, H*0.12), (W*0.27, -20)]
    shape(fg, K("#06090c"), 1.6)
    for j, (cx, cy, rot) in enumerate(((W*0.09, H*0.27, 170), (W*0.17, H*0.205, 200))):
        teacup(cx, cy + 26, 3.2, rot=rot, seed=40 + j, inner="#bfe6ff")
    for j in range(7):
        rr2 = random.Random(60 + j)
        cx, cy = W*0.05 + j*24, H*0.24 - j*10
        S.fill([(cx, cy), (cx + rr2.uniform(5, 12), cy + rr2.uniform(-2, 4)), (cx + rr2.uniform(2, 8), cy + rr2.uniform(5, 9))], K("#e9e2d0"), 0.9)
    soul(W*0.13, H*0.38, 2.4, seed=99)
    cave_frame(b, "#05080b", 4, top=0.98, side=0.02)
    darken_bottom(b, 0.24, 0.8)
    vignette(b, 0.6)


def spruce(x, y, h, col, lw=1.0, seed=1, rim=None):
    r = random.Random(seed)
    w = h*0.36
    stroke([(x, y), (x, y + h*0.2)], max(1.5, h*0.025))
    tiers = 7
    for i in range(tiers):
        t0 = i/tiers; t1 = (i + 1.6)/tiers
        yb = y + h*0.08 + h*0.9*t0; yt = y + h*0.08 + h*0.92*min(1, t1)
        hw = w*(1 - t0)*r.uniform(0.9, 1.1)
        pts = [(x, yt)] + bez((x, yt), (x + hw*0.4, yt - (yt - yb)*0.4), (x + hw*0.8, yb + 4), (x + hw*1.05, yb - 3))
        for k in range(4):
            xx = x + hw*(1 - k/4)
            pts += [(xx - hw*0.12, yb + r.uniform(0, 4)), (xx - hw*0.25, yb - r.uniform(1, 4))]
        pts += [(x - hw*1.05, yb - 3)] + bez((x - hw*1.05, yb - 3), (x - hw*0.8, yb + 4), (x - hw*0.4, yt - (yt - yb)*0.4), (x, yt))
        shape(pts, K(col), lw)
        if rim: stroke(pts[:len(pts)//3], lw*1.2, g=K(rim), alpha=0.5)


def fabian(x, y, s=1.0):
    """Brdy forest spirit: a body of spruce cones, moss beard, hat, bag, pipe; (x, y) feet"""
    with T(x, y, s):
        cone = K("#6b4a2c"); cone_d = K("#4a3220"); moss = K("#2f4a1c"); moss_d = K("#1f3210")
        for lx in (-7, 7):
            S.tube([(lx, 40), (lx*1.1, 18), (lx*1.2, 3)], 9, 8, K("#3a2a1c"), lw=1.1, sh=0.3)
            shape([(lx*1.2 - 6, 0), (lx*1.2 + 7, 0), (lx*1.2 + 6, 6), (lx*1.2 - 5, 6)], K("#2a1e14"), 1.0)
        stroke(bez((-14, 100), (-24, 80), (-26, 62), (-22, 46)), 1.6)
        bag = bez((-30, 60), (-34, 46), (-26, 36), (-18, 38)) + bez((-18, 38), (-14, 48), (-16, 58), (-22, 64))
        shape(bag, K("#5a4a32"), 1.1); offset_shadow(bag, 4, 1, 0.3)
        body = bez((-18, 100), (-26, 80), (-24, 54), (-16, 36)) + bez((-16, 36), (-6, 30), (6, 30), (16, 36)) + bez((16, 36), (24, 54), (26, 80), (18, 100))
        shape(body, cone, 1.3)
        C.saveState(); C.clipPath(S.poly(body), stroke=0, fill=0)
        for row in range(10):
            yy = 34 + row*7.5
            for col_ in range(8):
                xx = -26 + col_*7.5 + (3.7 if row % 2 else 0)
                sc = bez((xx - 4.5, yy + 4), (xx - 4, yy - 2), (xx + 4, yy - 2), (xx + 4.5, yy + 4))
                S.fill(sc + [(xx, yy + 5)], cone_d, 0.6)
                stroke(sc, 0.6, alpha=0.8)
        C.restoreState()
        offset_shadow(body, 9, 1, 0.35)
        for side in (-1, 1):
            arm = [(side*16, 90), (side*26, 74), (side*30, 60)] if side < 0 else [(16, 90), (26, 82), (24, 98)]
            S.tube(arm, 8, 7, cone, lw=1.1, sh=0.2)
        beard = bez((-12, 104), (-16, 86), (-10, 66), (-2, 52)) + [(0, 56), (3, 50)] + bez((3, 50), (10, 66), (16, 86), (12, 104))
        beard = S.notch(beard, 1.3, 3)
        shape(beard, moss, 1.1)
        clip_fill(beard, ell(5, 80, 9, 26, 20), moss_d)
        for k in range(7):
            bx = -9 + k*3.2
            stroke(bez((bx, 100), (bx*1.1, 88), (bx*0.8, 74), (bx*0.5, 60)), 0.6, g=K("#2a3a18"))
        for k in range(9):
            rr = random.Random(k)
            S.dot(rr.uniform(-9, 9), rr.uniform(60, 98), rr.uniform(0.6, 1.2), K("#9ab85a"))
        hood_face = ell(0, 108, 11, 9, 28)
        shape(hood_face, K("#2a2018"), 1.0)
        S.dot(-4, 109, 1.5, K("#e8c25a")); S.dot(4, 109, 1.5, K("#e8c25a"))
        glow(0, 109, 14, "#e8c25a", 0.25, 8)
        brim = ell(0, 115, 30, 5.5, 36)
        shape(brim, K("#2c2a24"), 1.2)
        crown = [(-15, 116)] + bez((-15, 116), (-16, 128), (-10, 136), (0, 136)) + bez((0, 136), (10, 136), (16, 128), (15, 116))
        shape(crown, K("#2c2a24"), 1.2)
        offset_shadow(crown, 5, 0, 0.3)
        shape([(-15, 118), (15, 118), (15, 122), (-15, 122)], K("#3a4a26"), 0.8)
        spruce(9, 120, 16, "#2e4a2a", 0.6, 5)
        S.fill(ell(24, 98, 3.5, 3.5, 12), K("#3a2a1c")); stroke(ell(24, 98, 3.5, 3.5, 12), 0.8, closed=True)
        stroke([(3, 102), (23, 98)], 1.8); stroke([(3, 102), (23, 98)], 0.8, g=K("#6a4a2a"))
        bowl = [(21, 98), (27, 98), (26.5, 105), (21.5, 105)]
        shape(bowl, K("#4a3020"), 0.9)
        S.fill(ell(24, 105, 2.4, 0.9, 10), K("#ff9a3a"), 1.0)
        glow(24, 106, 7, "#ff8a3a", 0.5, 8)
        for k, (sx, sy, rr) in enumerate(((25, 111, 2), (22, 118, 3), (26, 127, 4), (21, 138, 5.5))):
            S.fill(ell(sx, sy, rr, rr*0.7, 16), K("#c9cfd6"), 0.3 - k*0.05)


def act2_end(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#1a2124"), (0.4, "#3c4a4c"), (0.7, "#2b3639"), (1, "#141a1e")])
    crayon_over(rect(0, 0, W, H), "#7a8a86", 0.25, 6)
    gy = H*0.2
    for layer, (yb, hmin, hmax, col, n, fog) in enumerate(((H*0.4, 140, 230, "#4e5d5c", 26, 0.5), (H*0.32, 180, 300, "#344240", 18, 0.45),
                                                          (H*0.24, 260, 420, "#1f2a28", 11, 0.4))):
        r = random.Random(10 + layer)
        for i in range(n):
            x = r.uniform(-30, W + 30)
            if layer == 2 and W*0.18 < x < W*0.5: continue
            spruce(x, yb + r.uniform(-10, 10), r.uniform(hmin, hmax), col, 0.9 + layer*0.25, seed=i + layer*50)
        mist(-40, W + 40, yb + 20, 50, "#9aaaa6", fog, 3 + layer, 16)
    gr = [(-20, -20), (-20, gy + 18)] + jag(-20, W + 20, gy + 14, 6, 40, 3) + [(W + 20, -20)]
    shape(gr, K("#1c2620"), 1.3)
    crayon_over(gr, "#3a4a30", 0.5, 7)
    hill = [(W*0.62, gy - 10)] + bez((W*0.62, gy - 10), (W*0.7, H*0.5), (W*0.85, H*0.66), (W + 20, H*0.7)) + [(W + 20, gy - 10)]
    shape(hill, K("#1b1f1c"), 1.4)
    crayon_over(hill, "#3a3c34", 0.5, 8)
    spruce(W*0.75, H*0.56, 200, "#141c1a", 1.3, 77)
    spruce(W*0.92, H*0.62, 240, "#141c1a", 1.3, 78)
    mx, my, mw, mh = W*0.8, gy - 2, 120, 150
    mouth = [(mx - mw/2, my)] + bez((mx - mw/2, my), (mx - mw/2, my + mh*0.9), (mx + mw/2, my + mh*0.9), (mx + mw/2, my)) + [(mx - mw/2, my)]
    shape(mouth, K("#030405"), 1.4)
    glow(mx + 4, my + 36, 16, "#8fd0ff", 0.4, 10)
    S.dot(mx + 4, my + 36, 1.2, K("#e8f6ff"))
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
    fabian(W*0.32, gy + 6, 2.35)
    mist(-40, W*0.6, gy + 30, 40, "#a9b8b2", 0.45, 21, 12)
    spruce(W*0.03, -30, 560, "#0b100e", 1.6, 90)
    darken_bottom(b, 0.24, 0.75)
    vignette(b, 0.55)


def rock(x, y, r, seed, col="#3a3230", lw=1.0, rot=0, light=None, rim="#ff9a4a"):
    rr = random.Random(seed)
    n = rr.randint(7, 11)
    pts = [(x + math.cos(a)*r*rr.uniform(0.6, 1.2), y + math.sin(a)*r*rr.uniform(0.55, 1.1)) for a in [rot + k*math.tau/n + rr.uniform(-0.2, 0.2) for k in range(n)]]
    shape(pts, K(col), lw)
    if light:
        ang = math.atan2(light[1] - y, light[0] - x)
        offset_shadow(pts, -math.cos(ang)*r*0.4, -math.sin(ang)*r*0.4, 0.5)
        lit = [p for p in pts if (p[0] - x)*math.cos(ang) + (p[1] - y)*math.sin(ang) > r*0.2]
        if len(lit) > 1: stroke(lit, lw*1.6, g=K(rim), alpha=0.85)
    else:
        offset_shadow(pts, r*0.35, -r*0.2, 0.4)
    return pts


def kosmas_bust(x, y, s=1.0):
    """old chronicler, head and shoulders with the burning page in his hands; (x, y) bottom centre"""
    with T(x, y, s):
        robe = K("#4a2a26"); skin = K("#e2b48e"); beard = K("#e6e2da")
        body = [(-74, -80)] + bez((-70, 0), (-66, 40), (-50, 66), (-24, 74)) + bez((-24, 74), (-8, 78), (8, 78), (24, 74)) + bez((24, 74), (50, 66), (66, 40), (70, 0)) + [(74, -80)]
        shape(body, robe, 1.4)
        offset_shadow(body, -12, 4, 0.35)
        stroke(bez((-30, 70), (-34, 50), (-30, 24), (-34, 0)), 0.8, alpha=0.6)
        stroke(bez((30, 70), (34, 50), (30, 24), (34, 0)), 0.8, alpha=0.6)
        book = [(-66, -30), (-28, -34), (-24, -4), (-62, 2)]
        shape(book, K("#3a2214"), 1.2)
        shape([(-62, -1), (-25, -7), (-24, -4), (-62, 2)], K("#e8dcc0"), 0.8)
        neck = rect(-9, 70, 9, 86)
        shape(neck, skin, 0.9)
        head = bez((0, 136), (18, 136), (25, 120), (24, 104)) + bez((24, 104), (23, 90), (14, 80), (0, 80)) + \
               bez((0, 80), (-14, 80), (-23, 90), (-24, 104)) + bez((-24, 104), (-25, 120), (-18, 136), (0, 136))
        shape(head, skin, 1.3)
        clip_fill(head, ell(0, 128, 40, 14, 24), K("#b07a5a"))
        cap = bez((-24, 118), (-24, 140), (24, 140), (24, 118)) + bez((24, 118), (10, 124), (-10, 124), (-24, 118))
        shape(cap, K("#2a1a18"), 1.2)
        for ex in (-1, 1):
            shape(ell(ex*24, 104, 3.5, 6, 14), skin, 1.0)
        bd = bez((-22, 102), (-26, 74), (-14, 40), (0, 30)) + bez((0, 30), (14, 40), (26, 74), (22, 102)) + \
             bez((22, 102), (14, 94), (6, 92), (0, 93)) + bez((0, 93), (-6, 92), (-14, 94), (-22, 102))
        shape(S.notch(bd, 1.2, 4), beard, 1.2)
        for bx in (-12, -6, 0, 6, 12):
            stroke(bez((bx, 90), (bx*1.2, 74), (bx, 56), (bx*0.6, 40)), 0.6, g=K("#a8a49a"))
        shape(bez((-12, 95), (-6, 99), (6, 99), (12, 95)) + bez((12, 95), (6, 92), (-6, 92), (-12, 95)), beard, 0.9)
        nose = bez((-2, 112), (-7, 102), (-6, 96), (0, 96)) + bez((0, 96), (6, 96), (7, 102), (2, 112))
        shape(nose, K("#d9a07a"), 1.0)
        for ex in (-1, 1):
            gl = ell(ex*10, 108, 7, 6, 24)
            S.fill(gl, K("#ffd28a"), 0.3)
            stroke(gl, 1.3, closed=True)
            S.dot(ex*10 + 1, 107, 1.6, 0.0)
            stroke([(ex*10 + 3, 111), (ex*10 + 5, 109)], 1.2, g=K("#fff3c4"))
            shape(ell(ex*10, 118, 7, 2.2, 14, rot=ex*-8), beard, 0.8)
        stroke([(-3, 108), (3, 108)], 1.1)
        for k in range(3): stroke([(-8, 128 - k*3), (8, 128 - k*3)], 0.4, alpha=0.5)
        for side in (-1, 1):
            S.tube([(side*48, 50), (side*40, 6), (side*24, 12)], 14, 12, robe, lw=1.2, sh=0.2)
        page = [(-20, -6), (20, -2), (24, 46), (-16, 50)]
        shape(page, K("#f0e2bc"), 1.1)
        for k in range(6):
            yy = 4 + k*6.5
            stroke([(-14 + k*0.3, yy), (16 + k*0.3, yy + 2.5)], 0.6, g=K("#6a4a2a"), alpha=0.7)
        rr = random.Random(9)
        burn = [(24, 46), (22, 34)] + [(20 - k*5, 36 + rr.uniform(-4, 4)) for k in range(8)] + [(-17, 40), (-16, 50)]
        S.fill(burn, K("#1a120c"), 1.0)
        stroke(burn[1:-1], 1.6, g=K("#ff7a2a"))
        glow(4, 56, 110, "#ff9a3a", 0.5, 24)
        for k in range(5):
            fx = -12 + k*8
            flame(fx, 38 + rr.uniform(-2, 3), 2.0 + rr.uniform(-0.4, 0.8), lean=rr.uniform(-1, 1))
        for k in range(6):
            ax, ay = rr.uniform(-30, 40), rr.uniform(70, 150)
            S.fill([(ax, ay), (ax + 3, ay + 1), (ax + 2, ay + 3)], K("#ffb34a"), 0.8)
        for side in (-1, 1):
            hp = bez((side*28, 6), (side*30, 16), (side*24, 24), (side*18, 22)) + bez((side*18, 22), (side*14, 18), (side*16, 8), (side*22, 4))
            shape(hp, skin, 1.0)
            for k in range(3): stroke([(side*(17 + k*0.5), 20 - k*4), (side*21, 20 - k*4)], 0.6)


def act3_end(b):
    W, H = b.w, b.h
    flat(rect(0, 0, W, H), "#0b0a0d")
    gx0, gx1 = W*0.6, W*0.66
    left = [(-5, -5), (gx1 - 10, -5), (gx0 + 10, H + 5), (-5, H + 5)]
    right = [(gx1 + 4, -5), (W + 5, -5), (W + 5, H + 5), (gx0 + 24, H + 5)]
    C.saveState(); C.clipPath(S.poly(left), stroke=0, fill=0)
    grad(0, 0, W*0.7, H, [(0, "#120d0c"), (0.5, "#2a1a14"), (1, "#100c0c")])
    cx, cy = W*0.3, H*0.52
    glow(cx, cy, 200, "#ff7a2a", 0.7, 30, ry=170)
    open_ = ell(cx, cy, 70, 85, 30)
    S.fill(open_, K("#ffcf7a"), 0.9)
    for i in range(16):
        rr = random.Random(i)
        ang = rr.uniform(0, math.tau); d = rr.uniform(0.2, 1.0)
        rock(cx + math.cos(ang)*70*d, cy + math.sin(ang)*85*d + 30, rr.uniform(14, 30), i, "#1e1816", light=(cx, cy - 60))
    mass = [(cx - 160, H + 5), (cx - 120, cy + 70), (cx - 60, cy + 40), (cx - 10, cy + 55), (cx + 40, cy + 30), (cx + 90, cy + 60), (cx + 150, cy + 90), (cx + 170, H + 5)]
    shape(mass, K("#1a1412"), 1.4)
    stroke(mass[1:-1], 2.2, g=K("#ff8a3a"), alpha=0.8)
    for k in range(5):
        stroke([(cx - 100 + k*50, cy + 120), (cx - 100 + k*50, cy + 70)], 0.9, alpha=0.6)
    for k, (ax, sc) in enumerate(((0.75, 1.0), (0.55, 0.75))):
        for side in (-1, 1):
            px = cx + side*W*0.22*sc
            p = rect(px - 9*sc, H*0.5 - 230*sc, px + 9*sc, H*0.5 + 220*sc)
            shape(p, K("#2e2016"), 1.2); offset_shadow(p, -side*6*sc, 0, 0.4)
        shape(rect(cx - W*0.24*sc, H*0.5 + 200*sc, cx + W*0.24*sc, H*0.5 + 222*sc), K("#2e2016"), 1.2)
    for i in range(26):
        rr = random.Random(100 + i)
        x = rr.uniform(20, W*0.6); y = rr.uniform(H*0.35, H*1.0); r_ = rr.uniform(6, 26)
        for k in range(3):
            stroke([(x + rr.uniform(-r_, r_)*0.6, y + r_ + 4 + k*3), (x + rr.uniform(-r_, r_)*0.6, y + r_ + 30 + k*12)], 0.8, alpha=0.5)
        rock(x, y, r_, 200 + i, rr.choice(("#2a2220", "#221c1a", "#302622")), rot=rr.uniform(0, 3), light=(cx, cy))
    for i in range(10):
        rr = random.Random(300 + i)
        flat(ell(cx + rr.uniform(-180, 180), H*0.3 + rr.uniform(-40, 60), rr.uniform(50, 110), rr.uniform(30, 50), 30), "#8a6a5a", 0.12)
    fl = [(-5, -5), (-5, H*0.24), (W*0.2, H*0.3), (W*0.5, H*0.28), (W*0.7, H*0.22), (W*0.7, -5)]
    shape(fl, K("#120e0e"), 1.3)
    hx, hy = W*0.2, H*0.06
    glow(hx + 52, hy + 120, 120, "#8fd0ff", 0.45, 18)
    hero_silhouette(hx, hy, 2.6, rim="#ff9a4a")
    lamp(hx + 52, hy + 150, 1.9, cold=True, glow_r=0)
    C.restoreState()
    C.saveState(); C.clipPath(S.poly(right), stroke=0, fill=0)
    grad(W*0.55, 0, W, H, [(0, "#0d0908"), (0.6, "#24140e"), (1, "#0d0908")])
    for i in range(14):
        rr = random.Random(400 + i)
        stroke([(W*0.62 + i*26, H + 5), (W*0.62 + i*26 + rr.uniform(-6, 6), -5)], 0.5, g=K("#3a2a20"), alpha=0.6)
    kosmas_bust(W*0.83, H*0.1, 2.2)
    C.restoreState()
    gut = [(gx1 - 10, -5), (gx1 + 4, -5), (gx0 + 24, H + 5), (gx0 + 10, H + 5)]
    S.fill(gut, K("#cfc2a2"), 1.0)
    stroke([(gx1 - 10, -5), (gx0 + 10, H + 5)], 2.2); stroke([(gx1 + 4, -5), (gx0 + 24, H + 5)], 2.2)
    darken_bottom(b, 0.24, 0.65)
    vignette(b, 0.45)


def roots(x0, x1, y, n, seed, col="#140f18", lmin=40, lmax=180, lw=2.0):
    r = random.Random(seed)
    for i in range(n):
        x = r.uniform(x0, x1); L = r.uniform(lmin, lmax)
        pts = [(x, y + 10)]
        xx, yy = x, y
        for k in range(8):
            xx += r.uniform(-8, 8); yy -= L/8; pts.append((xx, yy))
        stroke(pts, lw*r.uniform(1.5, 3.5)); stroke(pts, lw*r.uniform(0.6, 1.2), g=K(col))
        for k in range(2):
            j = r.randrange(2, 7); bx, by = pts[j]
            stroke([(bx, by), (bx + r.uniform(-20, 20), by - r.uniform(10, 30))], lw*0.8)


def kalinov_bridge(x, y, s, col="#3a1a1a", glow_c="#ff4a2a"):
    with T(x, y, s):
        glow(0, 20, 160, glow_c, 0.4, 20, ry=60)
        deck = bez((-120, 0), (-60, 34), (60, 34), (120, 0)) + list(reversed(bez((-120, -8), (-60, 26), (60, 26), (120, -8))))
        shape(deck, K(col), 1.0)
        stroke(bez((-120, 0), (-60, 34), (60, 34), (120, 0)), 1.6, g=K("#ff6a3a"), alpha=0.9)
        for k in range(-5, 6):
            px = k*20; py = 30 - abs(k)**2*1.0
            stroke([(px, py), (px, py + 10)], 0.8)
        for k in range(3):
            ax = -60 + k*60
            stroke(ell(ax, 0, 22, 22, 20, 0, 180), 1.0, g=K("#ff6a3a"), alpha=0.6)


def act4_intro(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#0a0812"), (0.35, "#1c1830"), (0.55, "#2e2850"), (0.75, "#1a1630"), (1, "#08070e")])
    crayon_over(rect(0, H*0.4, W, H), "#3a3466", 0.35, 11)
    roots(0, W, H, 26, 4, lmin=60, lmax=220)
    for i in range(3):
        rr = random.Random(50 + i)
        far = [(-20, H*0.44)] + jag(-20, W + 20, H*(0.5 + 0.06*i) + rr.uniform(0, 20), 22, 70, 60 + i) + [(W + 20, H*0.44)]
        shape(far, K(mix("#2c2848", "#141224", i/2)), 0.9)
    kalinov_bridge(W*0.72, H*0.5, 1.25)
    ry0, ry1 = H*0.3, H*0.5
    flat(rect(0, ry0, W, ry1), "#05040a")
    for k in range(18):
        rr = random.Random(200 + k)
        yy = ry0 + (ry1 - ry0)*rr.random(); xx = rr.uniform(0, W)
        stroke([(xx, yy), (xx + rr.uniform(40, 160), yy)], 0.8, g=K("#6a5aa8"), alpha=0.4)
    for k in range(6):
        rr = random.Random(300 + k)
        stroke([(W*0.72 + rr.uniform(-60, 60), ry1 - 4 - k*7), (W*0.72 + rr.uniform(-60, 60) + 40, ry1 - 4 - k*7)], 1.2, g=K("#ff5a3a"), alpha=0.45 - k*0.05)
    mist(-40, W + 40, ry1 + 6, 22, "#8a7ad8", 0.4, 12, 14)
    mist(-40, W*0.5, ry0 + 30, 18, "#7a6ac8", 0.2, 13, 8)
    bank = [(-20, -20), (-20, H*0.34)] + jag(-20, W*0.7, H*0.32, 6, 40, 31) + [(W*0.75, H*0.3), (W*0.9, H*0.22), (W + 20, H*0.2), (W + 20, -20)]
    shape(bank, K("#14121c"), 1.3)
    crayon_over(bank, "#2a2638", 0.5, 12)
    cx, cy = W*0.36, H*0.24
    glow(cx, cy + 10, 160, "#6a7ad8", 0.35, 18, ry=70)
    tent = [(cx - 230, cy + 10), (cx - 180, cy + 110), (cx - 120, cy + 10)]
    shape(tent, K("#2a2838"), 1.2); offset_shadow(tent, 18, 0, 0.35)
    stroke([(cx - 180, cy + 110), (cx - 180, cy + 124)], 1.6)
    shape([(cx - 186, cy + 10), (cx - 180, cy + 70), (cx - 168, cy + 10)], K("#06060a"), 0.8)
    ash = ell(cx, cy, 34, 9, 24)
    shape(ash, K("#3a3a44"), 1.0)
    for k in range(5):
        rr = random.Random(400 + k)
        stroke([(cx - 24 + k*12, cy + 2), (cx - 30 + k*14 + rr.uniform(-6, 6), cy + 22)], 2.2); stroke([(cx - 24 + k*12, cy + 2), (cx - 30 + k*14 + rr.uniform(-6, 6), cy + 22)], 1.0, g=K("#2a2220"))
    for k in range(3):
        rr = random.Random(500 + k)
        stroke(bez((cx - 6 + k*6, cy + 10), (cx - 14 + k*8, cy + 40), (cx + 10 + k*4, cy + 60), (cx - 4 + k*6, cy + 90 + k*10)), 0.8, g=K("#9aaad8"), alpha=0.35)
    seats = [(cx - 120, cy - 4, 1.9, False), (cx - 70, cy + 34, 1.6, False), (cx + 70, cy + 32, 1.6, True), (cx + 128, cy - 6, 1.95, True),
             (cx + 230, cy + 26, 1.5, True), (cx - 300, cy + 40, 1.4, False)]
    for sx, sy, ss, fl in sorted(seats, key=lambda t: -t[1]):
        glow(sx, sy + 40*ss, 60*ss, "#8aa0e8", 0.22, 10)
        shape(ell(sx, sy - 2, 16*ss, 6*ss, 16), K("#24222e"), 0.9)
        miner_sit(sx, sy + 2*ss, ss, flip=fl)
    mist(-40, W + 40, H*0.2, 40, "#7a6ac8", 0.4, 14, 12)
    darken_bottom(b, 0.24, 0.8)
    vignette(b, 0.55)


SEALS = (("water", "#4aa8ff"), ("stone", "#c4c4cc"), ("fire", "#ff6a2a"), ("death", "#b58aff"))


def seal(x, y, kind, col, r=13):
    glow(x, y, r*3, col, 0.55, 14)
    shape(ell(x, y, r, r, 30), K("#16141c"), 1.4)
    stroke(ell(x, y, r*0.82, r*0.82, 30), 1.2, closed=True, g=K(col))
    with T(x, y, r/10):
        if kind == "water":
            for k in (-3, 2):
                stroke(bez((-6, k), (-3, k + 3), (0, k - 3), (3, k)) + bez((3, k), (4.5, k + 2), (6, k + 1), (6.5, k)), 1.2, g=K(col))
        elif kind == "stone":
            shape([(-6, -4), (-1, 5), (2, 1), (6, -4)], K(col), 0.8)
        elif kind == "fire":
            flame(0, -5, 0.9)
        else:
            shape(ell(0, 1, 5, 5, 20), K("#e8dcff"), 0.8)
            shape([(-3, -2), (3, -2), (3, -5), (-3, -5)], K("#e8dcff"), 0.7)
            S.dot(-2, 1.5, 1.4, 0.0); S.dot(2, 1.5, 1.4, 0.0)


def giant_head(x, y, s, eye="#9fe0ff", grin=True):
    with T(x, y, s):
        rock_ = K("#2a2730"); dk = K("#141218")
        bd = [(-46, 4), (-58, -40), (-40, -110), (-20, -150), (0, -170), (18, -146), (40, -106), (58, -40), (46, 4)]
        shape(S.notch(bd, 2.5, 3), K("#5a5866"), 1.6)
        for k in range(9):
            bx = -36 + k*9
            stroke(bez((bx, -6), (bx*1.15, -50), (bx*0.9, -100), (bx*0.5, -140)), 0.9, g=K("#2a2830"))
        for k in range(5):
            rr = random.Random(k)
            stroke(bez((-30 + k*15, -20), (-34 + k*16, -60), (-24 + k*12, -120), (-28 + k*14, -175 - rr.uniform(0, 30))), 1.8, g=K("#1a1612"))
        head = [(-52, 0), (-58, 30), (-50, 60), (-30, 78), (0, 84), (30, 78), (50, 60), (58, 30), (52, 0), (30, -12), (0, -14), (-30, -12)]
        shape(head, rock_, 1.8)
        offset_shadow(head, -14, 4, 0.35)
        for a_, b_ in (((-40, 50), (-20, 30)), ((20, 70), (36, 44)), ((-10, 78), (-4, 60))):
            stroke([a_, b_], 0.9, alpha=0.7)
        brow = [(-46, 40), (-10, 30), (0, 34), (10, 30), (46, 40), (40, 50), (0, 42), (-40, 50)]
        shape(brow, dk, 1.4)
        for ex in (-1, 1):
            sock = ell(ex*22, 26, 13, 8, 20, rot=ex*10)
            S.fill(sock, K("#050407"), 1.0)
            glow(ex*22, 26, 16, eye, 0.8, 10)
            eye_ = [(ex*12, 28), (ex*22, 30), (ex*31, 23), (ex*22, 24)]
            S.fill(eye_, K("#f2fbff"), 1.0)
        nose = [(-12, 30), (-16, 6), (-8, -4), (8, -4), (16, 6), (12, 30)]
        shape(nose, K("#4a4652"), 1.4)
        offset_shadow(nose, -6, 2, 0.35)
        mouth = bez((-30, -6), (-16, -22), (16, -22), (30, -6)) + bez((30, -6), (14, -14), (-14, -14), (-30, -6))
        shape(mouth, K("#08060a"), 1.3)
        for k in range(5):
            rr = random.Random(40 + k)
            tx = -20 + k*10 + rr.uniform(-2, 2)
            shape([(tx - 2.5, -12 - abs(k - 2)*1.2), (tx + 2.5, -12 - abs(k - 2)*1.2), (tx + rr.uniform(-1, 1), -17 + abs(k - 2)*0.6)], K("#a8a49a"), 0.6)
        cap = [(-56, 72), (-40, 120), (-10, 160), (30, 190), (60, 186), (44, 160), (54, 110), (56, 72)]
        shape(cap, K("#4a2226"), 1.6)
        offset_shadow(cap, -12, 2, 0.35)
        shape([(-60, 64), (60, 64), (62, 80), (-62, 80)], K("#2e2a32"), 1.4)
        for k in range(4):
            rr = random.Random(20 + k)
            px = rr.uniform(-40, 40); py = rr.uniform(90, 150)
            stroke([(px, py), (px + rr.uniform(10, 24), py + rr.uniform(-8, 8))], 1.8, g=K("#c8d0dc"), alpha=0.8)


def ore_veins(pts_clip, n, seed, x0, y0, x1, y1):
    rr = random.Random(seed)
    C.saveState(); C.clipPath(S.poly(pts_clip), stroke=0, fill=0)
    for i in range(n):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        pts = [(x, y)]
        for k in range(rr.randint(3, 5)):
            x += rr.uniform(8, 18); y += rr.uniform(-6, 6); pts.append((x, y))
        stroke(pts, 4.5, g=K("#6a7280"))
        stroke(pts, 1.6, g=K("#e2e8f2"))
        p = pts[rr.randrange(len(pts))]
        for a_ in (0, 90):
            with T(p[0], p[1], rot=a_ + 20):
                S.fill([(-6, 0), (0, 0.8), (6, 0), (0, -0.8)], K("#ffffff"), 0.9)
    for i in range(n*2):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        stroke([(x, y), (x + rr.uniform(-30, 30), y + rr.uniform(-30, 30))], 0.8, alpha=0.6)
    C.restoreState()


def final_1(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#06050a"), (0.5, "#141220"), (1, "#08070c")])
    crayon_over(rect(0, 0, W, H), "#2a2638", 0.4, 21)
    lx, ly = W*0.35, H*0.66
    LS = 4.6
    cxl, cyl = lx + 9, ly - 14*LS
    rays(lx + 9.4*LS, ly - 12*LS, 20, 700, 40, "#d8f0ff", 0.1, 5, 10)
    glow(cxl, cyl, 380, "#9fd8ff", 0.6, 34, power=1.4)
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
    for k in range(4):
        t = 0.25 + k*0.18
        ax = arm[0][0] + (arm[2][0] - arm[0][0])*t; ay = arm[0][1] + (arm[2][1] - arm[0][1])*t
        stroke([(ax - 14, ay + 34), (ax + 8, ay), (ax - 6, ay - 34)], 1.3, alpha=0.8)
    glow(lx + 9.4*LS, ly - 12*LS, 90, "#ffffff", 0.6, 14)
    lamp(lx, ly, LS, cold=True, glow_r=0, body="#4a4a58")
    flame(lx + 9.4*LS, ly - 10.3*LS, LS*0.95, cold=True, lean=1.5)
    glow(lx + 9.6*LS, ly - 8*LS, 20, "#ffffff", 0.8, 8)
    palm = [(lx + 30, ly + 34), (lx + 90, ly + 50), (lx + 104, ly - 4), (lx + 70, ly - 30), (lx + 24, ly - 14)]
    shape(palm, K("#2e2a34"), 1.8)
    for k in range(4):
        fy = ly + 26 - k*11
        fing = [(lx + 40, fy + 6), (lx + 4, fy + 8 - k), (lx - 16, fy + 2 - k*2), (lx - 18, fy - 6 - k*2), (lx - 6, fy - 7 - k), (lx + 40, fy - 6)]
        shape(fing, K("#36323e"), 1.5)
        offset_shadow(fing, 0, -3, 0.35)
        stroke([(lx - 18, fy - 6 - k*2), (lx - 6, fy - 7 - k)], 1.6, g=K("#cfeeff"), alpha=0.9)
    for i, (kind, col) in enumerate(SEALS):
        a = math.radians(110 + i*55)
        seal(cxl + math.cos(a)*120, cyl + math.sin(a)*105, kind, col, 17)
    stroke(ell(cxl, cyl, 120, 105, 60, 100, 290), 1.0, g=K("#dff3ff"), alpha=0.45)
    hx, hy, hr = W*0.1, H*0.03, -12
    hero_silhouette(hx, hy, 2.1, rim="#9fd8ff", reach=True, arm_to=to_local(hx, hy, 2.1, hr, lx - 22, cyl - 4), rot=hr)
    darken_bottom(b, 0.24, 0.7)
    vignette(b, 0.55)


def final_2(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#05040a"), (0.5, "#10142a"), (1, "#05040a")])
    cx, cy = W*0.5, H*0.58
    rr = random.Random(5)
    for i, (kind, col) in enumerate(SEALS):
        for k in range(5):
            a0 = math.radians(i*90 + k*14 + 20)
            pts = []
            for j in range(30):
                t = j/29; a = a0 + t*1.6; r_ = 30 + t*560
                pts.append((cx + math.cos(a)*r_, cy + math.sin(a)*r_*0.75))
            if k < 3: stroke(pts, 3.5 - k, g=K(col), alpha=0.35)
    rays(cx, cy, 10, 900, 60, "#fff6e0", 0.16, 3, 14)
    glow(cx, cy, 460, "#bfe6ff", 0.8, 40, power=0.45)
    glow(cx, cy, 170, "#ffffff", 0.97, 26, power=0.6)
    for i in range(40):
        a = rr.uniform(0, math.tau); d = rr.uniform(70, 420); sz = rr.uniform(5, 22)*(1 - d/600)
        x, y = cx + math.cos(a)*d, cy + math.sin(a)*d*0.8
        for k in range(3):
            stroke([(x - math.cos(a)*(14 + k*10), y - math.sin(a)*(14 + k*10)*0.8), (x - math.cos(a)*(30 + k*22), y - math.sin(a)*(30 + k*22)*0.8)],
                   0.8, g=K("#dff3ff"), alpha=0.6 - k*0.15)
        with T(x, y, 1, rot=math.degrees(a) + rr.uniform(-40, 40)):
            sh = [(-sz, -sz*0.3), (sz*0.2, -sz*0.5), (sz, sz*0.1), (-sz*0.2, sz*0.4)]
            if rr.random() < 0.35:
                shape(sh, K("#4a4a58"), 1.0)
            else:
                S.fill(sh, K("#e8f6ff"), 0.85); stroke(sh, 0.8, closed=True, g=K("#3a6a9a"))
    for i, (kind, col) in enumerate(SEALS):
        a = math.radians(i*90 + 60)
        x, y = cx + math.cos(a)*260, cy + math.sin(a)*190
        for k in range(4):
            stroke([(x - math.cos(a)*(20 + k*14), y - math.sin(a)*(20 + k*14)), (x - math.cos(a)*(50 + k*30), y - math.sin(a)*(50 + k*30))], 1.4, g=K(col), alpha=0.7 - k*0.15)
        seal(x, y, kind, col, 16)
        with T(x, y, 1, rot=35):
            stroke([(-14, -14), (14, 14)], 2.2, g=K("#ffffff"))
    with T(W*0.9, H*0.62, 1.0):
        for k in range(4):
            fy = 40 - k*34
            fing = [(120, fy + 12), (20, fy + 16), (-40, fy + 30 + k*4), (-56, fy + 18 + k*4), (-30, fy - 2), (120, fy - 14)]
            shape(fing, K("#16141a"), 1.8)
            stroke(fing[2:5], 1.8, g=K("#cfeeff"), alpha=0.9)
    with T(W*0.06, -20, 1.0):
        arm = [(-40, 20), (40, 120), (130, 170)]
        S.tube(arm, 60, 46, K("#0c0b10"), lw=1.8, sh=0)
        stroke([(40, 140), (130, 186)], 1.8, g=K("#cfeeff"), alpha=0.8)
        hand = [(120, 150), (160, 168), (176, 196), (150, 200), (130, 190), (112, 186)]
        shape(hand, K("#0c0b10"), 1.6)
    darken_bottom(b, 0.24, 0.6)
    vignette(b, 0.5)


def epilogue(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#2a1c2c"), (0.3, "#e0905a"), (0.36, "#f2b870"), (0.45, "#c4786a"), (0.62, "#6a4a72"), (0.85, "#2a2a52"), (1, "#181a36")])
    glow(W*0.42, H*0.3, 220, "#ffd890", 0.6, 30, ry=120)
    S.fill(ell(W*0.42, H*0.3, 44, 44, 40), K("#fff0c0"), 1.0)
    stars(0, H*0.8, W, H, 25, 41, big=0.05)
    hl = [(0, H*0.3)] + [(x, H*0.33 + 14*math.sin(x/90) + 8*math.sin(x/37)) for x in range(0, int(W)+20, 20)] + [(W, H*0.3), (W, 0), (0, 0)]
    shape(hl, K("#5a3a52"), 0.9)
    mist(0, W, H*0.34, 22, "#f2b880", 0.45, 2)
    cathedral(W*0.64, H*0.30, 1.62, wall="#4a3448", roof="#3a2638", edge="#ffc078", lit="#ffcf7a")
    belfry(W*0.2, H*0.25, 1.62, wall="#4a3448", roof="#3a2638", edge="#ffc078", swing=24)
    bx, by = W*0.2, H*0.25 + 136*1.62
    for k in range(3):
        stroke(ell(bx, by - 10, 46 + k*18, 40 + k*16, 30, -50, 50), 1.6, g=K("#ffe0a0"), alpha=0.8 - k*0.2)
        stroke(ell(bx, by - 10, 46 + k*18, 40 + k*16, 30, 130, 230), 1.6, g=K("#ffe0a0"), alpha=0.8 - k*0.2)
    rr = random.Random(50)
    for i in range(50):
        t = i/49
        x = W*(0.08 + 0.84*t) + rr.uniform(-30, 30)
        y = H*(0.44 + 0.38*math.sin(math.pi*t)**0.7) + rr.uniform(-40, 40)
        a = 0.35 + 0.65*rr.random()
        glow(x, y, 20, "#ffcf6a", 0.55*a, 10)
        S.fill(ell(x, y, 3.2, 3.2, 12), K("#fff2c8"), 0.9*a + 0.1)
    lights = town_row(-20, W+20, H*0.30, 11, "#3a2a3e", "#2c1e30", 26, 50, 0.2, edge="#f2a060", wmin=34, wmax=58)
    for lx, ly in lights: glow(lx, ly, 12, "#ffb85c", 0.25, 8)
    flat(rect(0, 0, W, H*0.2), "#140f18")
    lights = town_row(-40, W+40, H*0.17, 5, "#22182a", "#1a1220", 38, 64, 0.25, wmin=52, wmax=86, lw=1.3, edge="#e08850")
    for lx, ly in lights: glow(lx, ly, 16, "#ffb85c", 0.3, 8)
    darken_bottom(b, 0.24, 0.8)
    vignette(b, 0.4)


def dlc_tease(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#030205"), (0.5, "#0b0710"), (1, "#040306")])
    cx, cy = W*0.42, H*0.58
    glow(cx + 80, cy, 560, "#2a0a1e", 0.6, 30, ry=300)
    face = [(-20, H + 20), (-20, -20), (W + 20, -20), (W + 20, H + 20)]
    crayon_over(face, "#2a1a26", 0.35, 51)
    rim = "#6a1a2a"
    stroke(bez((cx - 380, cy + 150), (cx - 200, cy + 230), (cx + 160, cy + 220), (cx + 330, cy + 120)), 2.2, g=K(rim), alpha=0.8)
    stroke(bez((cx + 330, cy + 120), (cx + 380, cy + 60), (cx + 400, cy - 60), (cx + 470, cy - 200)), 2.2, g=K(rim), alpha=0.7)
    stroke(bez((cx - 300, cy - 110), (cx - 120, cy - 170), (cx + 140, cy - 160), (cx + 300, cy - 90)), 1.6, g=K(rim), alpha=0.6)
    for k in range(5):
        stroke(bez((cx + 260 + k*6, cy - 40 - k*20), (cx + 300, cy - 80 - k*20), (cx + 340, cy - 70 - k*16), (cx + 380, cy - 100 - k*18)), 0.9, g=K("#3a1424"), alpha=0.8)
    horn = bez((W*0.8, H + 20), (W*0.86, H*0.8), (W*0.98, H*0.74), (W + 20, H*0.78)) + [(W + 20, H + 20)]
    S.fill(horn, K("#08060a"), 1.0)
    stroke(horn[:-1], 1.8, g=K(rim), alpha=0.85)
    horn2 = bez((W*0.74, H + 20), (W*0.8, H*0.72), (W*0.96, H*0.6), (W + 20, H*0.62))
    stroke(horn2, 1.2, g=K("#3a1424"), alpha=0.8)
    for k in range(6):
        t = 0.15 + k*0.14
        x = W*0.8 + (W*0.2)*t; y = H*(0.95 - 0.2*t)
        stroke([(x, y), (x + 8, y - 30)], 0.8, g=K("#3a1424"), alpha=0.7)
    for k, (sx, sh) in enumerate(((0.06, 70), (0.14, 110), (0.22, 60))):
        sp = [(W*sx - 30, H + 20), (W*sx, H - sh), (W*sx + 30, H + 20)]
        S.fill(sp, K("#08060a"), 1.0); stroke(sp[:-1] + [sp[-1]], 1.4, g=K(rim), alpha=0.6)
    rr = random.Random(7)
    for k in range(6):
        x0, y0 = cx + rr.uniform(-400, 400), cy + rr.uniform(-240, 240)
        pts = [(x0, y0)]
        for j in range(5):
            x0 += rr.uniform(-30, 30); y0 += rr.uniform(10, 34)*rr.choice((-1, 1)); pts.append((x0, y0))
        stroke(pts, 0.9, g=K("#1a0e16"))
    lid = bez((cx - 250, cy), (cx - 120, cy + 76), (cx + 130, cy + 76), (cx + 260, cy + 4)) + bez((cx + 260, cy + 4), (cx + 120, cy - 44), (cx - 120, cy - 44), (cx - 250, cy))
    S.fill(lid, K("#160c14"), 1.0)
    crayon_over(lid, "#3a1a2a", 0.5, 52)
    stroke(bez((cx - 250, cy), (cx - 120, cy + 76), (cx + 130, cy + 76), (cx + 260, cy + 4)), 2.0, g=K("#5a2236"))
    seam = bez((cx - 250, cy), (cx - 120, cy - 40), (cx + 120, cy - 40), (cx + 260, cy + 4))
    glow(cx, cy - 24, 220, "#ff3a2a", 0.28, 16, ry=30)
    stroke(seam, 5.0)
    stroke(seam, 1.6, g=K("#ff5a3a"), alpha=0.75)
    for k in range(15):
        t = 0.08 + 0.84*k/14
        px = cx - 250 + 510*t; py = cy - 40*math.sin(math.pi*t) - 2
        stroke([(px, py), (px + (t - 0.5)*36, py - 30 - 12*math.sin(math.pi*t))], 1.8)
    for k in range(3):
        stroke(bez((cx - 270 - k*20, cy + 20 + k*28), (cx - 130, cy + 104 + k*30), (cx + 130, cy + 104 + k*30), (cx + 280 + k*20, cy + 24 + k*28)), 1.2, g=K("#3a1424"), alpha=0.9)
    for k in range(4):
        stroke(bez((cx - 240 + k*10, cy - 54 - k*24), (cx - 120, cy - 96 - k*26), (cx + 120, cy - 96 - k*26), (cx + 250 - k*10, cy - 50 - k*24)), 1.1, g=K("#3a1424"), alpha=0.8)
    for k in range(4):
        a = math.radians(160 + k*14)
        stroke([(cx - 250 + math.cos(a)*20, cy + math.sin(a)*20), (cx - 250 + math.cos(a)*80, cy + math.sin(a)*60)], 1.0, g=K("#3a1424"), alpha=0.8)
    lx, ly = W*0.5, H*0.05
    glow(lx, ly + 14, 34, "#8fd0ff", 0.45, 10)
    flame(lx, ly + 8, 0.9, cold=True)
    darken_bottom(b, 0.24, 0.5)
    vignette(b, 0.7)


def glyph_contours(font, ch, size):
    from fontTools.pens.basePen import BasePen
    gs = font.getGlyphSet(); g = gs[font.getBestCmap()[ord(ch)]]
    k = size/font["head"].unitsPerEm

    class Pen(BasePen):
        def __init__(self):
            super().__init__(gs); self.cs = []; self.cur = []
        def _moveTo(self, p): self.cur = [(p[0]*k, p[1]*k)]
        def _lineTo(self, p): self.cur.append((p[0]*k, p[1]*k))
        def _curveToOne(self, p1, p2, p3):
            p0 = self.cur[-1]
            self.cur += bez(p0, (p1[0]*k, p1[1]*k), (p2[0]*k, p2[1]*k), (p3[0]*k, p3[1]*k), 8)[1:]
        def _closePath(self):
            if len(self.cur) > 2: self.cs.append(self.cur)
            self.cur = []
        _endPath = _closePath
    pen = Pen(); g.draw(pen)
    return pen.cs, g.width*k


def multipath(contours, dx=0, dy=0):
    p = C.beginPath()
    for c in contours:
        p.moveTo(c[0][0] + dx, c[0][1] + dy)
        for q in c[1:]: p.lineTo(q[0] + dx, q[1] + dy)
        p.close()
    return p


def carved_letter(cs, seed):
    from reportlab.pdfgen.canvas import FILL_EVEN_ODD
    from reportlab.lib.colors import HexColor
    xs = [p[0] for c in cs for p in c]; ys = [p[1] for c in cs for p in c]
    x0, y0, x1, y1 = min(xs), min(ys), max(xs), max(ys)
    for k in range(9, 0, -1):
        C.saveState(); C.setFillColor(HexColor("#0d0a0a" if k > 1 else "#1c1614"))
        C.drawPath(multipath(cs, k*0.9, -k*1.1), fill=1, stroke=0, fillMode=FILL_EVEN_ODD); C.restoreState()
    C.saveState(); C.clipPath(multipath(cs), stroke=0, fill=0, fillMode=FILL_EVEN_ODD)
    grad(x0 - 5, y0 - 5, x1 + 5, y1 + 5, [(0, "#5e564c"), (0.45, "#a39a88"), (0.8, "#d9cfba"), (1, "#efe6d2")], 50)
    crayon_over(rect(x0 - 5, y0 - 5, x1 + 5, y1 + 5), "#6a6052", 0.55, seed)
    for c in cs:
        stroke([(x + 2.2, y - 2.6) for x, y in c], 4.0, closed=True, g=K("#2a221c"), alpha=0.55)
        stroke([(x - 1.4, y + 1.6) for x, y in c], 2.2, closed=True, g=K("#fff6e2"), alpha=0.6)
    rr = random.Random(seed)
    for i in range(2):
        x, y = rr.uniform(x0, x1), rr.uniform(y0, y1)
        pts = [(x, y)]
        for j in range(4): x += rr.uniform(-10, 10); y += rr.uniform(-14, -4); pts.append((x, y))
        stroke(pts, 0.9, g=K("#2a221c"))
    x, y = rr.uniform(x0, x1), rr.uniform(y0 + 10, y1 - 10)
    stroke([(x - 8, y), (x, y + 3), (x + 9, y - 1)], 2.4, g=K("#7a8496"))
    stroke([(x - 8, y), (x, y + 3), (x + 9, y - 1)], 0.9, g=K("#ffffff"))
    C.restoreState()
    for c in cs: stroke(c, 1.8, closed=True)


def title(b):
    from fontTools.ttLib import TTFont
    import os
    from letter import hand_text
    font = TTFont(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "f_Bangers-Regular.ttf"))
    size = 122; word = "PERMONIK"
    glyphs = [glyph_contours(font, ch, size) for ch in word]
    track = 5
    total = sum(w for _, w in glyphs) + track*(len(word) - 1)
    x = (b.w - total)/2; base = 64
    rr = random.Random(3)
    accent = None
    for i, (cs, w) in enumerate(glyphs):
        rot = rr.uniform(-3.5, 3.5); dy = rr.uniform(-3, 3)
        with T(x + w/2, base + dy, 1.0, rot=rot):
            carved_letter([[(px - w/2, py) for px, py in c] for c in cs], 10 + i)
        if word[i] == "I": accent = (x + w/2 + 2, base + dy + size*0.721 + 4)
        x += w + track
    ax, ay = accent
    with T(ax + 4, ay + 2, 1.0, rot=-30):
        lamp(0, 22, 1.0, cold=True, glow_r=16, glow_a=0.7, body="#4a4a58")
    sub = "Desátek z hlubin"
    for dx, dy, col in ((1.6, -1.8, "#0d0a0a"), (0, 0, "#e9dcc0")):
        hand_text(dx, 18 + dy, b.w, sub, "SHB", 31, g=K(col))


def menu_bg(b):
    W, H = b.w, b.h
    grad(0, 0, W, H, [(0, "#0a0a14"), (0.3, "#1a1c34"), (0.6, "#222648"), (1, "#0c0d1e")])
    stars(0, H*0.45, W, H, 110, 61, big=0.05)
    glow(W*0.14, H*0.86, 40, "#e8e2c8", 0.25, 12)
    S.fill(ell(W*0.14, H*0.86, 12, 12, 30), K("#e8e2c8"), 1.0); stroke(ell(W*0.14, H*0.86, 12, 12, 30), 0.9, closed=True)
    S.fill(ell(W*0.14 + 5, H*0.86 + 2, 10, 10.5, 30), K("#1d203c"), 1.0)
    hl = [(0, H*0.3)] + [(x, H*0.36 + 20*math.sin(x/160) + 7*math.sin(x/47)) for x in range(0, int(W)+20, 20)] + [(W, H*0.3), (W, 0), (0, 0)]
    shape(hl, K("#191a2c"), 1.0)
    with T(W*0.33, H*0.36, 0.42):
        cathedral(0, 0, 1.0, wall="#1e1e34", roof="#17172a", edge="#5a5a8a", win="#101020")
    for i in range(14):
        rr = random.Random(70 + i)
        spruce(rr.uniform(W*0.52, W + 20), H*0.33 + rr.uniform(-6, 6), rr.uniform(70, 130), "#10121e", 0.9, 70 + i)
    hill = [(W*0.5, -20), (W*0.56, H*0.3), (W*0.66, H*0.5), (W*0.78, H*0.6), (W + 20, H*0.64), (W + 20, -20)]
    shape(hill, K("#16141c"), 1.4)
    crayon_over(hill, "#2e2a36", 0.55, 62)
    hatch(hill, 5.0, 60, 0.5, 0.0, 0.35)
    mx, my, mw, mh = W*0.74, H*0.2, 150, 170
    glow(mx, my + 50, 190, "#ffa24a", 0.32, 30, ry=150)
    mouth = [(mx - mw/2, my)] + bez((mx - mw/2, my), (mx - mw/2, my + mh), (mx + mw/2, my + mh), (mx + mw/2, my)) + [(mx - mw/2, my)]
    shape(mouth, K("#140a06"), 1.4)
    C.saveState(); C.clipPath(S.poly(mouth), stroke=0, fill=0)
    glow(mx, my + 40, 110, "#ffb85c", 0.55, 20, ry=80)
    for k in range(3):
        t = k/3
        stroke([(mx - mw*0.4*(1 - t), my + mh*0.62*(1 - t*0.5)), (mx + mw*0.4*(1 - t), my + mh*0.62*(1 - t*0.5))], 3 - k, g=K("#3a2414"))
    C.restoreState()
    for xx in (mx - mw/2 - 6, mx + mw/2 + 6):
        p = rect(xx - 9, my - 4, xx + 9, my + mh*0.74)
        shape(p, K("#3a2a1c"), 1.3); offset_shadow(p, 6, 0, 0.35)
    lin = rect(mx - mw/2 - 22, my + mh*0.7, mx + mw/2 + 22, my + mh*0.7 + 18)
    shape(lin, K("#3a2a1c"), 1.4); offset_shadow(lin, 0, 6, 0.35)
    lamp(mx + mw/2 + 22, my + mh*0.7, 1.4, glow_r=60, glow_a=0.45)
    hf = (W*0.86, H*0.56)
    with T(hf[0], hf[1], 1.25):
        for px in (-40, 40):
            shape(rect(px - 4, 0, px + 4, 80), K("#1a140e"), 1.1)
        for a_, b_ in (((-40, 0), (0, 110)), ((40, 0), (0, 110))):
            stroke([a_, b_], 4.0); stroke([a_, b_], 2.0, g=K("#2a1e14"))
        shape(rect(-50, 74, 50, 82), K("#1a140e"), 1.1)
        S.fill(ell(0, 96, 12, 12, 24), K("#20160e")); stroke(ell(0, 96, 12, 12, 24), 1.1, closed=True)
        for a in range(0, 360, 45): stroke([(0, 96), (math.cos(math.radians(a))*16, 96 + math.sin(math.radians(a))*16)], 1.0)
        stroke([(12, 96), (12, -60)], 0.9, g=K("#5a4a38"))
    gr = [(-20, -20), (-20, H*0.2)] + jag(-20, W*0.6, H*0.2, 4, 40, 63) + [(W*0.6, H*0.18), (W + 20, H*0.16), (W + 20, -20)]
    shape(gr, K("#0e0d14"), 1.3)
    crayon_over(gr, "#22202c", 0.5, 64)
    near = (mx - 120, mx + 40); far = (mx - 14, mx + 14)
    for j in range(8):
        t = (j/7)**1.6; yy = (my + 2)*(1 - t) - 10*t
        xa = far[0] + (near[0] - far[0])*t - 12*t; xb = far[1] + (near[1] - far[1])*t + 12*t
        stroke([(xa, yy), (xb, yy)], 3.0); stroke([(xa, yy), (xb, yy)], 1.2, g=K("#3a2a1c"))
    for k in range(2):
        stroke([(near[k], -10), (far[k], my + 2)], 3.6); stroke([(near[k], -10), (far[k], my + 2)], 1.6, g=K("#6a6a78"))
    px, py = mx - mw/2 - 58, my - 20
    glow(px + 21*1.2, py + 62*1.2 - 16, 110, "#8fd0ff", 0.45, 24, ry=90)
    hx, hy = permonik(px, py, 1.2, high=True, sil="#0d0c12")
    lamp(hx, hy + 1, 1.1, cold=True, glow_r=0, body="#2a2a34")
    darken_bottom(b, 0.2, 0.6)
    for i in range(30):
        flat(rect(0, 0, W*0.5*(1 - i/30), H), "#05050c", 0.02)
    vignette(b, 0.55)


def fg_roof(x, y, s, col="#0f0d14", rim="#c27a52", with_crow=True):
    with T(x, y, s):
        rf = [(0, 0), (0, 250), (40, 262), (230, 120), (250, 0)]
        shape(rf, K(col), 1.6)
        for k in range(1, 12):
            t = k/12
            stroke([(0 + 30*t, 250*(1-t) + 0), (230*(1-t*0.15) + 20*t, 120*(1-t))], 0.4, g=K("#2a2433"), alpha=0.6)
        stroke([(40, 262), (230, 120)], 1.6, g=K(rim), alpha=0.7)
        ch = rect(150, 150, 172, 214)
        shape(ch, K("#17131c"), 1.3)
        shape(rect(146, 212, 176, 220), K("#17131c"), 1.2)
        stroke([(146, 220), (176, 220)], 1.2, g=K(rim), alpha=0.7)
        if with_crow: crow(166, 220, 1.4)


def crow(x, y, s=1.0, col="#0b0a10"):
    with T(x, y, s):
        bd = bez((-12, 6), (-6, 13), (4, 13), (7, 10)) + [(12, 9.5), (8, 7.5)] + bez((8, 7.5), (6, 2), (0, 0), (-5, 2)) + [(-14, 0)]
        shape(bd, K(col), 0.9)
        S.dot(5, 10.5, 0.7, K("#d9a050"))
        stroke([(-1, 1), (-2, -3)], 0.8); stroke([(2, 1), (2, -3)], 0.8)


NAMES = ["intro_1", "intro_2", "intro_3", "act1_end", "act2_end", "act3_end", "act4_intro", "final_1", "final_2", "epilogue", "dlc_tease"]
SLIDES = [(n, globals()[n]) for n in NAMES if n in globals()]

if __name__ == "__main__":
    common.run({"slides": [(n, 1920, 1080, f, True) for n, f in SLIDES],
                "ui": [("title", 1200, 360, title), ("menu_bg", 1920, 1080, menu_bg, True)]})
