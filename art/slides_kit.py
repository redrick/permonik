import math, random
import lib
from lib import Col, C, ell, bez, rrect, resample
import style3 as S
from style3 import T, stroke, shape, form, hatch, clip_fill, offset_shadow, poly
import osobni


def K(h, a=None):
    r, g, b = (int(h[i:i+2], 16)/255 for i in (1, 3, 5))
    return Col(0.3*r + 0.59*g + 0.11*b, h, a)


def mix(h0, h1, t):
    a = [int(h0[i:i+2], 16) for i in (1, 3, 5)]; b = [int(h1[i:i+2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(round(x + (y-x)*t)) for x, y in zip(a, b))


def flat(pts, h, a=1.0):
    S.fill(pts, K(h), a)


def rect(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def grad(x0, y0, x1, y1, stops, n=140):
    """vertical gradient, stops = [(t, hex)] from bottom (0) to top (1)"""
    for i in range(n):
        t = (i+0.5)/n
        for k in range(len(stops)-1):
            if stops[k][0] <= t <= stops[k+1][0]:
                u = (t-stops[k][0])/max(1e-6, stops[k+1][0]-stops[k][0]); col = mix(stops[k][1], stops[k+1][1], u); break
        else:
            col = stops[-1][1] if t > stops[-1][0] else stops[0][1]
        ya = y0 + (y1-y0)*i/n; yb = y0 + (y1-y0)*(i+1)/n + 0.4
        flat(rect(x0, ya, x1, yb), col)


def glow(x, y, r, h, a=0.6, n=22, ry=None, power=1.6):
    ry = ry or r
    n = max(n, int(max(r, ry)/6))
    al = 1 - (1-a)**(1/n)
    for i in range(n):
        k = (1 - i/n)**(1/power)
        flat(ell(x, y, r*k, ry*k, 40), h, al)


def crayon_over(pts, h, alpha=0.5, key=0):
    """crayon strokes only (no wash), laid over whatever is already there"""
    col = K(h); rgb = (lib.G(col).red, lib.G(col).green, lib.G(col).blue)
    tile = osobni.crayon_tile(rgb, key, False)
    if tile is None: return
    x0, y0, x1, y1 = S.bbox(pts)
    t = osobni.TILE_MM*72/25.4
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0); C.setFillAlpha(alpha)
    rr = random.Random(key)
    C.translate((x0+x1)/2, (y0+y1)/2); C.rotate(rr.uniform(-25, 25))
    r = math.hypot(x1-x0, y1-y0)/2 + t
    ty = -r
    while ty < r:
        tx = -r
        while tx < r:
            C.drawImage(tile, tx, ty, t, t, mask="auto"); tx += t
        ty += t
    C.restoreState()


def stars(x0, y0, x1, y1, n, seed=1, h="#f4ecd6", big=0.08):
    r = random.Random(seed)
    for i in range(n):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        rad = r.uniform(0.35, 0.9)
        if r.random() < big:
            glow(x, y, 5, h, 0.35, 8)
            for a in (0, 90):
                with T(x, y, rot=a + r.uniform(-8, 8)):
                    S.fill([(-4.5, 0), (0, 0.45), (4.5, 0), (0, -0.45)], K(h), 0.9)
            rad = 1.1
        S.fill(ell(x, y, rad, rad, 10), K(h), r.uniform(0.6, 1.0))


def darken_bottom(b, frac=0.24, a=0.8, h="#06060c", n=40):
    for i in range(n):
        y = b.h*frac*(i+1)/n
        flat(rect(0, 0, b.w, y), h, a/n*1.6)


def vignette(b, a=0.55, h="#05050a", n=18):
    for i in range(n):
        k = 1.0 - 0.3*i/n
        p = C.beginPath(); p.rect(-10, -10, b.w+20, b.h+20)
        E = ell(b.w/2, b.h/2, b.w*0.62*k + 60, b.h*0.66*k + 40, 60)
        p.moveTo(*E[0])
        for q in E[1:]: p.lineTo(*q)
        p.close()
        C.saveState(); C.setFillColor(lib.G(K(h))); C.setFillAlpha(a/n)
        C.drawPath(p, fill=1, stroke=0, fillMode=0); C.restoreState()


def mist(x0, x1, y, h, col, a=0.35, seed=3, n=7):
    r = random.Random(seed)
    for i in range(n):
        cx = r.uniform(x0, x1); w = r.uniform(0.25, 0.5)*(x1-x0)
        flat(ell(cx, y + r.uniform(-h*0.3, h*0.3), w, h*r.uniform(0.5, 1.0), 40), col, a/n*2.2)


def hatch_dark(pts, spacing=3.2, ang=50, lw=0.5, alpha=0.5):
    hatch(pts, spacing, ang, lw, 0.0, alpha)


def rays(x, y, r0, r1, n, h, a=0.25, seed=2, width=4.0):
    rr = random.Random(seed)
    for i in range(n):
        ang = math.tau*i/n + rr.uniform(-0.12, 0.12)
        w = width*rr.uniform(0.5, 1.4)/r1
        L = r1*rr.uniform(0.6, 1.0)
        pts = [(x + math.cos(ang-w*8)*r0, y + math.sin(ang-w*8)*r0), (x + math.cos(ang)*L, y + math.sin(ang)*L),
               (x + math.cos(ang+w*8)*r0, y + math.sin(ang+w*8)*r0)]
        flat(pts, h, a)


def jag(x0, x1, y, amp, step, seed, top=True):
    """jagged rock edge as a list of points from x0 to x1"""
    r = random.Random(seed); out = []; x = x0
    while x < x1:
        out.append((x, y + r.uniform(-amp, amp))); x += step*r.uniform(0.6, 1.4)
    out.append((x1, y + r.uniform(-amp, amp)))
    return out


# ------------------------------------------------------------------ lamps
FLAME_WARM = ("#ffcf6a", "#fff3c4")
FLAME_COLD = ("#9fd8ff", "#f2fbff")


def flame(x, y, s=1.0, cold=False, lean=0.0):
    c0, c1 = FLAME_COLD if cold else FLAME_WARM
    with T(x, y, s):
        out = bez((-2.4, 0), (-3.4, 3.5), (-1+lean, 6), (lean*1.4, 10)) + bez((lean*1.4, 10), (1.6+lean, 6), (3.4, 3.5), (2.4, 0)) + \
              bez((2.4, 0), (1.4, -1.6), (-1.4, -1.6), (-2.4, 0))
        S.fill(out, K(c0), 1.0)
        S.fill([(px*0.55, py*0.62+0.2) for px, py in out], K(c1), 1.0)
        stroke(out, 0.7, closed=True, g=K("#3b2a1a" if not cold else "#1c2f4a"))


def lamp(x, y, s=1.0, cold=False, lit=True, glow_r=60, glow_a=0.55, body="#6e5236"):
    """a miner's kahan hanging from its hook; (x, y) = top of the hook"""
    gc = "#8fd0ff" if cold else "#ffb347"
    if lit and glow_r: glow(x, y - 16*s, glow_r, gc, glow_a, 26)
    with T(x, y, s):
        stroke(bez((0, 0), (2.5, -1), (2.5, -4), (0, -5)), 1.0)
        stroke([(0, -5), (0, -7)], 1.0)
        bod = bez((-5, -9), (-6.5, -15), (-3.5, -19), (0, -19)) + bez((0, -19), (3.5, -19), (6.5, -15), (5, -9)) + [(0, -7)]
        shape(bod, K(body), 1.0)
        offset_shadow(bod, -1.5, 1.2, 0.3)
        S.fill(ell(-1.8, -12, 1.2, 3, 10, rot=-10), K("#e8c890"), 0.55)
        spout = [(4.5, -10.5), (9, -9.5), (9.5, -11), (5, -13)]
        shape(spout, K(body), 0.9)
        if lit: flame(9.4, -10.3, 0.75, cold, lean=0.6)
        else:
            stroke(bez((9.4, -10), (10, -6), (8.5, -3), (9.5, 1)), 0.5, g=K("#8c8c9a"), alpha=0.6)


# ------------------------------------------------------------------ town
def gothic_window(x, y, w, h, col="#1a1a28", lw=0.8):
    pts = [(x-w/2, y), (x+w/2, y), (x+w/2, y+h-w*0.8)] + bez((x+w/2, y+h-w*0.8), (x+w/2, y+h-w*0.2), (x+w*0.1, y+h), (x, y+h)) + \
          bez((x, y+h), (x-w*0.1, y+h), (x-w/2, y+h-w*0.2), (x-w/2, y+h-w*0.8))
    shape(pts, K(col), lw)
    return pts


def tent_roof(cx, y, w, h, col, edge, lw=1.3, ribs=5):
    """St Barbara's concave tent roof"""
    L = bez((cx-w/2, y), (cx-w*0.18, y+h*0.12), (cx-w*0.06, y+h*0.5), (cx, y+h))
    R = bez((cx, y+h), (cx+w*0.06, y+h*0.5), (cx+w*0.18, y+h*0.12), (cx+w/2, y))
    pts = L + R[1:]
    shape(pts, K(col), lw)
    offset_shadow(pts, w*0.12, 0, 0.35)
    for k in range(1, ribs):
        t = k/ribs
        stroke(bez((cx-w/2 + w*t, y), (cx-w/2 + w*t + (cx-(cx-w/2+w*t))*0.6, y+h*0.25), (cx, y+h*0.8), (cx, y+h)), lw*0.4, g=K(edge), alpha=0.7)
    stroke(L[:int(len(L)*0.95)], lw*1.2, g=K(edge), alpha=0.8)
    stroke([(cx, y+h), (cx, y+h+h*0.12)], lw)
    S.dot(cx, y+h+h*0.12, lw*1.2, K(edge))
    return pts


def pinnacle(x, y, w, h, col, lw=0.8):
    pts = [(x-w/2, y), (x+w/2, y), (x, y+h)]
    shape(pts, K(col), lw)
    stroke([(x, y+h), (x, y+h+w*0.6)], lw*0.8)


def cathedral(x, y, s, wall="#2b2840", roof="#1f1c2e", edge="#c98a5a", win="#141320", lit=None):
    """chrám sv. Barbory, west-facing silhouette; (x, y) bottom centre"""
    with T(x, y, s):
        for side in (-1, 1):
            for k in range(3):
                bx = side*(88 + k*20); top = 54 - k*9
                arc_o = bez((side*74, 84 - k*6), (side*80 + side*k*8, 84 - k*6), (bx - side*2, top + 10), (bx, top))
                arc_i = bez((bx - side*5, top - 6), (bx - side*7, top + 2), (side*80 + side*k*6, 76 - k*6), (side*74, 74 - k*6))
                shape(arc_o + arc_i, K(roof), 0.8)
                shape(rect(bx-4.5, 0, bx+4.5, top), K(wall), 0.9)
                offset_shadow(rect(bx-4.5, 0, bx+4.5, top), side*3, 0, 0.3)
                pinnacle(bx, top, 9, 22, roof)
        body = rect(-74, 0, 74, 92)
        form(body, K(wall), 1.3, sdx=-18, sdy=0, sh=0.3)
        for wx in (-52, -26, 0, 26, 52):
            gl = gothic_window(wx, 22, 12, 52, lit or win)
            stroke([(wx, 22), (wx, 66)], 0.5, g=K("#55506a"))
        shape(rect(-80, 88, 80, 96), K(roof), 1.0)
        for px in range(-76, 80, 13): pinnacle(px, 96, 6, 16, roof, 0.6)
        tent_roof(-48, 96, 52, 108, roof, edge)
        tent_roof(48, 96, 52, 108, roof, edge)
        tent_roof(0, 96, 64, 150, roof, edge, 1.5)


def belfry(x, y, s, wall="#2a2a3c", roof="#1b1a28", edge="#c98a5a", bell="#6a5232", swing=0.0):
    with T(x, y, s):
        body = rect(-20, 0, 20, 150)
        form(body, K(wall), 1.2, sdx=-7, sdy=0, sh=0.32)
        for yy in range(12, 150, 11): stroke([(-20, yy), (20, yy)], 0.35, g=K("#4a4a60"), alpha=0.5)
        op = [(-12, 112), (12, 112), (12, 132)] + bez((12, 132), (12, 141), (-12, 141), (-12, 132))
        shape(op, K("#0c0b14"), 1.0)
        with T(0, 136, 1, rot=swing):
            stroke([(0, 0), (0, -3)], 1.2)
            b = bez((-3, -4), (-4, -9), (-8, -14), (-9, -17)) + [(9, -17)] + bez((9, -17), (8, -14), (4, -9), (3, -4))
            shape(b, K(bell), 1.0)
            S.fill([(-2, -6), (-1, -6), (-5, -15), (-7, -15)], K("#d9b27a"), 0.6)
            S.dot(0, -18.5, 1.6, K("#3a2a1a"))
        for wx in (-8, 8): gothic_window(wx, 70, 6, 18, "#0e0d16", 0.6)
        shape(rect(-24, 148, 24, 154), K(roof), 1.0)
        rf = [(-25, 154), (25, 154), (0, 214)]
        shape(rf, K(roof), 1.2)
        offset_shadow(rf, 9, 0, 0.35)
        stroke([(-25, 154), (0, 214)], 1.2, g=K(edge), alpha=0.8)
        stroke([(0, 214), (0, 226)], 1.0); stroke([(-4, 221), (4, 221)], 1.0)


def town_row(x0, x1, y, seed, col, roof, hmin=40, hmax=70, lit=0.3, win="#ffd27a", edge=None, wmin=28, wmax=46, lw=1.1):
    r = random.Random(seed)
    x = x0
    lights = []
    y_ = y
    while x < x1:
        y = y_ + r.uniform(-6, 6)
        w = r.uniform(wmin, wmax); hw = r.uniform(hmin, hmax); rh = w*r.uniform(0.6, 1.0)
        kind = r.random()
        wall = rect(x, y_ - 60, x + w, y + hw)
        shape(wall, K(col), lw)
        offset_shadow(wall, w*0.35, 0, 0.22)
        if kind < 0.45:
            rf = [(x - 3, y + hw), (x + w + 3, y + hw), (x + w/2, y + hw + rh)]
        elif kind < 0.7:
            st = w/6
            rf = [(x - 2, y + hw), (x + w + 2, y + hw), (x + w + 2, y + hw + rh*0.3), (x + w - st, y + hw + rh*0.3), (x + w - st, y + hw + rh*0.6),
                  (x + w - 2*st, y + hw + rh*0.6), (x + w - 2*st, y + hw + rh*0.9), (x + 2*st, y + hw + rh*0.9), (x + 2*st, y + hw + rh*0.6),
                  (x + st, y + hw + rh*0.6), (x + st, y + hw + rh*0.3), (x - 2, y + hw + rh*0.3)]
        else:
            rf = [(x - 4, y + hw), (x + w + 4, y + hw), (x + w*0.8, y + hw + rh*0.7), (x + w*0.2, y + hw + rh*0.7)]
        shape(rf, K(roof), lw)
        if edge: stroke(rf[1:] if kind < 0.45 else rf, lw*0.8, g=K(edge), alpha=0.5)
        if r.random() < 0.5:
            cx = x + w*r.uniform(0.2, 0.7)
            shape(rect(cx, y + hw + rh*0.3, cx + 5, y + hw + rh*0.75), K(roof), lw*0.7)
        rows = int(hw//18)
        for row in range(rows):
            for col_ in range(max(1, int(w//14))):
                wx = x + 6 + col_*14; wy = y + hw - 14 - row*17
                if wx + 6 > x + w - 2 or wy < y - 20: continue
                on = r.random() < lit
                gl = rect(wx, wy, wx + 6, wy + 9)
                shape(gl, K(win if on else "#13121c"), lw*0.6)
                if on:
                    lights.append((wx + 3, wy + 4.5))
                    stroke([(wx + 3, wy), (wx + 3, wy + 9)], 0.5); stroke([(wx, wy + 4.5), (wx + 6, wy + 4.5)], 0.5)
        x += w + r.uniform(-2, 3)
    return lights


# ------------------------------------------------------------------ figures
def miner_side(x, y, s=1.0, pose="walk", smock="#e9e4d6", flip=False, lamp_lit=True, cold=False, shade=0.35, seed=1, glow_k=1.0):
    """historic Kutná Hora miner in a white hooded smock, side view facing right; (x, y) feet"""
    r = random.Random(seed)
    with T(x, y, s, flip):
        skin = K("#d9b08c"); dark = K("#2c2622"); leather = K("#4a3324")
        if pose == "climb":
            legs = [[(-3, 40), (2, 28), (-1, 16)], [(3, 40), (6, 32), (4, 22)]]
        elif pose == "walk":
            legs = [[(-2, 40), (-6, 22), (-10, 3)], [(2, 40), (6, 21), (9, 3)]]
        else:
            legs = [[(-2, 40), (-2, 21), (-3, 3)], [(2, 40), (3, 21), (3, 3)]]
        for lg in legs:
            S.tube(lg, 6.2, 4.8, K("#3c3a40"), lw=1.0, sh=0.25)
            fx, fy = lg[-1]
            shape([(fx-3.5, fy-3), (fx+6, fy-3), (fx+5.5, fy+1.5), (fx-3, fy+3)], dark, 0.9)
        flek = [(-9, 52), (-4, 54), (-6, 30), (-13, 33)]
        shape(flek, leather, 1.0)
        body = bez((-8, 74), (-12, 60), (-12, 45), (-13, 34)) + bez((-13, 34), (-4, 31), (6, 31), (12, 34)) + \
               bez((12, 34), (11, 48), (10, 62), (7, 74))
        shape(body, K(smock), 1.2)
        offset_shadow(body, 6, 2, shade)
        stroke(bez((-4, 60), (-5, 50), (-5, 42), (-6, 34)), 0.5, alpha=0.6)
        stroke(bez((3, 62), (3, 52), (4, 42), (5, 34)), 0.5, alpha=0.6)
        shape([(-12, 46), (11, 46), (11, 49), (-12, 49)], leather, 0.8)
        # head under the hood
        hood = bez((-9, 72), (-12, 82), (-6, 92), (1, 92)) + bez((1, 92), (8, 92), (11, 84), (10, 74)) + [(5, 70), (-4, 70)]
        shape(hood, K(smock), 1.2)
        offset_shadow(hood, 4, 1, shade)
        fc = bez((3, 87), (8, 87), (9.5, 82), (9, 78)) + [(10.6, 77), (9, 75.5)] + bez((9, 75.5), (8, 73), (5, 73), (3, 75))
        shape(fc, skin, 0.9)
        offset_shadow(fc, 2.5, 0, 0.3)
        S.dot(7.2, 81.5, 0.7, 0.0)
        stroke(bez((3.5, 74.5), (2, 72), (5.5, 69), (8, 72)), 0.9, g=K("#5a4a3a"))
        if pose == "climb":
            for (sx, sy), (ex, ey), (hx, hy) in (((-4, 68), (2, 80), (6, 96)), ((4, 68), (9, 66), (13, 74))):
                S.tube([(sx, sy), (ex, ey), (hx, hy)], 5.2, 4.4, K(smock), lw=1.0, sh=shade*0.6)
                S.fill(ell(hx, hy, 2.4, 2.4, 10), skin); stroke(ell(hx, hy, 2.4, 2.4, 12), 0.8, closed=True)
            lh = None
        else:
            S.tube([(-2, 68), (4, 56), (12, 54)], 5.4, 4.6, K(smock), lw=1.0, sh=shade*0.6)
            S.fill(ell(13, 54, 2.4, 2.4, 10), skin); stroke(ell(13, 54, 2.4, 2.4, 12), 0.8, closed=True)
            lh = (14, 56)
    if lh:
        hx = x + (-lh[0] if flip else lh[0])*s; hy = y + lh[1]*s
        lamp(hx, hy, s*0.75, cold=cold, lit=lamp_lit, glow_r=70*s*glow_k if lamp_lit else 0, glow_a=0.45*glow_k + 0.1)
    return x, y


def miner_sit(x, y, s=1.0, flip=False, smock="#b4c4e4", dark="#5a6a90", seed=1, ghost=0.62):
    """dead miner sitting with bowed head, an extinguished lamp hanging from his hands; (x, y) seat bottom"""
    def gshape(pts, h, lw=1.0):
        S.fill(pts, K(h), ghost); stroke(pts, lw, closed=True, alpha=0.75)
    with T(x, y, s, flip):
        for dx in (0, 4):
            leg = [(-4 + dx, 0), (18 + dx, 2), (19 + dx, -18), (27 + dx, -18), (27 + dx, 6), (24 + dx, 13), (-2 + dx, 11)]
            gshape(leg, dark)
            gshape([(18 + dx, -22), (32 + dx, -22), (31 + dx, -16), (18 + dx, -15)], "#2a3048")
        body = bez((-10, 0), (-14, 18), (-12, 36), (-4, 46)) + bez((-4, 46), (4, 50), (12, 44), (14, 34)) + bez((14, 34), (12, 20), (10, 8), (8, 0))
        gshape(body, smock, 1.1)
        stroke(bez((-6, 40), (-8, 28), (-6, 16), (-6, 4)), 0.5, alpha=0.4)
        S.fill([(-12, 14), (10, 14), (10, 18), (-13, 18)], K("#3a3040"), 0.7)
        hood = [(0, 40)] + bez((0, 40), (-4, 54), (4, 64), (8, 66)) + bez((8, 66), (14, 60), (24, 50), (22, 40)) + [(14, 34)]
        gshape(hood, smock, 1.1)
        fc = bez((13, 54), (19, 52), (21, 44), (17, 39)) + [(12, 42)]
        S.fill(fc, K("#0c0e18"), 0.85)
        S.dot(17.5, 47, 0.8, K("#bfe2ff")); S.dot(15, 47.5, 0.6, K("#bfe2ff"))
        arm = [(4, 42), (18, 28), (27, 18)]
        S.tube(arm, 6, 5, K("#7f8fb6"), lw=0.9, sh=0)
        S.fill(ell(27, 18, 2.6, 2.6, 10), K("#c9d6ea"), 0.8); stroke(ell(27, 18, 2.6, 2.6, 12), 0.7, closed=True, alpha=0.7)
    hx = x + (-28 if flip else 28)*s; hy = y + 17*s
    lamp(hx, hy, s*0.8, lit=False, glow_r=0, body="#4a5068")


def miner_back(x, y, s=1.0, smock="#e9e4d6", shade=0.4, arm=(1, 1), rail=16):
    """miner seen from behind, climbing down a ladder; (x, y) = feet on the rung; returns lamp hook point"""
    with T(x, y, s):
        leather = K("#4a3324"); dark = K("#24201e")
        for side, ky in ((-1, 0), (1, 13)):
            S.tube([(side*5, 42), (side*8, 30 + ky*0.4), (side*6, 2 + ky)], 7, 5.5, K("#3c3a40"), lw=1.0, sh=0.3)
            shape([(side*6 - 5, ky - 1), (side*6 + 5, ky - 1), (side*6 + 4.5, ky + 4), (side*6 - 4.5, ky + 4)], dark, 0.9)
        for side, up in ((-1, arm[0]), (1, arm[1])):
            hy = 86 + up*8
            S.tube([(side*10, 74), (side*rail*1.15, 70 + up*4), (side*rail, hy)], 6, 5, K(smock), lw=1.0, sh=shade*0.7)
            S.fill(ell(side*rail, hy + 1, 2.8, 3.2, 10), K("#d9b08c")); stroke(ell(side*rail, hy + 1, 2.8, 3.2, 12), 0.8, closed=True)
        body = bez((-11, 76), (-14, 62), (-14, 48), (-15, 36)) + bez((-15, 36), (-5, 33), (5, 33), (15, 36)) + bez((15, 36), (14, 48), (14, 62), (11, 76))
        shape(body, K(smock), 1.2)
        offset_shadow(body, 7, 1, shade)
        flek = bez((-11, 50), (-12, 42), (-11, 32), (-9, 26)) + bez((-9, 26), (-3, 23), (3, 23), (9, 26)) + bez((9, 26), (11, 32), (12, 42), (11, 50))
        shape(flek, leather, 1.0)
        offset_shadow(flek, 4, 1, 0.3)
        shape([(-14, 50), (14, 50), (14, 53.5), (-14, 53.5)], leather, 0.8)
        hood = bez((-10, 74), (-13, 86), (-7, 96), (0, 97)) + bez((0, 97), (7, 96), (13, 86), (10, 74)) + bez((10, 74), (4, 72), (-4, 72), (-10, 74))
        shape(hood, K(smock), 1.2)
        offset_shadow(hood, 5, 0, shade)
        stroke(bez((0, 96), (1, 88), (0, 80), (1, 74)), 0.5, alpha=0.6)
    return x + 14*s, y + 52*s


def permonik(x, y, s=1.0, flip=False, lamp_up=True, grin=False, high=False, sil=None):
    """the small bearded miner, front-ish three-quarter view, knee-high; (x, y) feet. No shadow, ever."""
    hand = None
    with T(x, y, s, flip):
        smock = K("#ece8dc"); cap = K("#b8322a"); beard = K("#f1efe8"); skin = K("#e4b38f"); boot = K("#2f241c")
        if sil: smock = beard = skin = boot = K(sil); cap = K("#2a1014")
        for lx in (-5, 5):
            S.tube([(lx, 18), (lx*1.1, 4)], 6, 5, K("#4b3b31"), lw=1.0, sh=0.2)
            shape([(lx*1.1-4, 0), (lx*1.1+6, 0), (lx*1.1+5, 5), (lx*1.1-3.5, 5)], boot, 1.0)
        body = bez((-9, 40), (-13, 32), (-14, 22), (-14, 14)) + bez((-14, 14), (-6, 12), (6, 12), (14, 14)) + bez((14, 14), (14, 22), (13, 32), (9, 40))
        shape(body, smock, 1.2)
        offset_shadow(body, -4, 1.5, 0.22)
        shape([(-14, 20), (14, 20), (14, 23.5), (-14, 23.5)], K("#3a2a20"), 0.9)
        shape(rect(-2, 19.5, 2.5, 24), K("#c9a24a"), 0.7)
        S.tube([(-9, 37), (-14, 28), (-12, 20)], 5.5, 5, smock, lw=1.0, sh=0.15)
        S.fill(ell(-12, 19, 2.6, 2.6, 10), skin); stroke(ell(-12, 19, 2.6, 2.6, 12), 0.8, closed=True)
        if high:
            S.tube([(9, 37), (18, 44), (21, 60)], 5.5, 5, smock, lw=1.0, sh=0.15)
            hand = (21, 62)
        elif lamp_up:
            S.tube([(9, 37), (17, 40), (22, 48)], 5.5, 5, smock, lw=1.0, sh=0.15)
            hand = (22.5, 50)
        else:
            S.tube([(9, 37), (14, 28), (16, 22)], 5.5, 5, smock, lw=1.0, sh=0.15)
            hand = (16.5, 21)
        S.fill(ell(hand[0], hand[1]-1, 2.6, 2.6, 10), skin); stroke(ell(hand[0], hand[1]-1, 2.6, 2.6, 12), 0.8, closed=True)
        head = ell(0, 47, 9, 8.5, 30)
        shape(head, skin, 1.1)
        bd = bez((-9, 46), (-12, 34), (-6, 22), (0, 19)) + bez((0, 19), (6, 22), (12, 34), (9, 46)) + \
             bez((9, 46), (5, 42), (-5, 42), (-9, 46))
        shape(bd, beard, 1.1)
        for bx in (-4, 0, 4): stroke(bez((bx, 40), (bx*1.2, 34), (bx*0.9, 28), (bx*0.6, 23)), 0.45, g=K("#a7a49a"))
        mst = bez((-6, 43.5), (-3, 46), (3, 46), (6, 43.5)) + bez((6, 43.5), (2, 41.5), (-2, 41.5), (-6, 43.5))
        shape(mst, beard, 0.8)
        shape(ell(0, 45.5, 2.4, 2.6, 14), K("#d48f6f"), 0.8)
        if grin:
            stroke(bez((-5.5, 49), (-4, 47.5), (-2.5, 47.5), (-1.5, 49)), 0.9); stroke(bez((1.5, 49), (2.5, 47.5), (4, 47.5), (5.5, 49)), 0.9)
            stroke([(-6, 51.5), (-2, 50.5)], 0.9); stroke([(6, 51.5), (2, 50.5)], 0.9)
        else:
            S.dot(-3.6, 49, 1.0, 0.0); S.dot(3.6, 49, 1.0, 0.0)
            S.dot(-3.3, 49.4, 0.35, 1.0); S.dot(3.9, 49.4, 0.35, 1.0)
            stroke(bez((-6, 51.5), (-4.5, 52.5), (-3, 52.5), (-1.8, 51.8)), 0.8); stroke(bez((1.8, 51.8), (3, 52.5), (4.5, 52.5), (6, 51.5)), 0.8)
        for ex in (-1, 1): stroke([(ex*6.5, 47.5), (ex*8, 48.5)], 0.5)
        cp = [(-10, 52)] + bez((-10, 52), (-9, 60), (0, 64), (8, 63)) + [(14, 58), (12, 55.5)] + bez((12, 55.5), (11, 54), (10, 53), (10, 52))
        shape(cp, cap, 1.1)
        offset_shadow(cp, -3, 1, 0.25)
        shape([(-11, 50.5), (11, 50.5), (11, 54), (-11, 54)], K("#5a3a26"), 0.9)
    hx = x + (-hand[0] if flip else hand[0])*s; hy = y + hand[1]*s
    return hx, hy


def to_local(x, y, s, rot, px, py):
    a = math.radians(-rot); dx, dy = (px - x)/s, (py - y)/s
    return dx*math.cos(a) - dy*math.sin(a), dx*math.sin(a) + dy*math.cos(a)


def hero_silhouette(x, y, s=1.0, flip=False, col="#15141d", rim="#ffcf8a", reach=False, arm_to=None, rot=0):
    """class-neutral hooded traveller in a cloak, seen from behind/side; (x, y) feet."""
    with T(x, y, s, flip, rot):
        for lx, fx in ((-6, -9), (7, 10)):
            S.tube([(lx, 50), (lx*1.1, 24), (fx, 3)], 9, 7, K(col), lw=1.2, sh=0)
            shape([(fx-5, 0), (fx+8, 0), (fx+7, 6), (fx-4, 6)], K(col), 1.1)
        cloak = bez((-14, 112), (-24, 90), (-26, 60), (-30, 34)) + bez((-30, 34), (-12, 28), (8, 30), (22, 36)) + \
                bez((22, 36), (20, 60), (18, 90), (14, 112))
        shape(cloak, K(col), 1.4)
        stroke(bez((-10, 100), (-14, 80), (-16, 60), (-18, 36)), 0.6, g=K("#2c2a38"))
        stroke(bez((4, 100), (6, 80), (6, 58), (8, 34)), 0.6, g=K("#2c2a38"))
        hood = bez((-12, 108), (-18, 122), (-10, 138), (0, 138)) + bez((0, 138), (10, 138), (16, 124), (12, 108))
        shape(hood, K(col), 1.4)
        stroke(bez((-14, 112), (-17, 124), (-10, 136), (0, 137)), 1.2, g=K(rim), alpha=0.75)
        stroke(bez((-22, 90), (-25, 70), (-27, 52), (-29, 36)), 1.2, g=K(rim), alpha=0.6)
        hand = None
        if reach:
            tx, ty = arm_to if arm_to else (40, 100)
            S.tube([(10, 104), ((10+tx)/2 + 6, (104+ty)/2 - 6), (tx, ty)], 8, 6.5, K(col), lw=1.2, sh=0)
            S.fill(ell(tx+1, ty, 3.6, 3.0, 12), K(col if col == rim else "#c9a088")); stroke(ell(tx+1, ty, 3.6, 3.0, 14), 0.9, closed=True)
            for k in range(3): stroke(bez((tx+3, ty+1.5-k*1.5), (tx+5, ty+2-k*1.5), (tx+6, ty+1-k*1.5), (tx+6.5, ty-k*1.5)), 0.8)
            hand = (tx+4, ty)


def soul(x, y, s=1.0, h="#d8f1ff", a=0.9, face=True, seed=1):
    r = random.Random(seed)
    glow(x, y, 22*s, "#9fd8ff", 0.4, 12)
    with T(x, y, s, rot=r.uniform(-10, 10)):
        w1, w2 = r.uniform(-6, 6), r.uniform(-8, 8)
        tail = bez((-5.2, 0), (-6, -12), (w1 - 3, -24), (w2, -48)) + bez((w2, -48), (w1 + 2, -26), (5, -12), (5.2, 0))
        pts = ell(0, 0.5, 5.2, 6, 24, 0, 180) + tail
        S.fill(pts, K(h), a*0.55)
        S.fill(ell(0, 0.5, 5.2, 6, 24) , K(h), a)
        S.fill(ell(0, 1.5, 3, 3.6, 16), K("#ffffff"), a)
        if face:
            S.fill(ell(-1.7, 1.6, 0.7, 1.1, 8), K("#2a4a6a"), 0.8); S.fill(ell(1.7, 1.6, 0.7, 1.1, 8), K("#2a4a6a"), 0.8)
            S.fill(ell(0, -1.6, 0.7, 1.0, 8), K("#2a4a6a"), 0.6)
        stroke(pts, 0.5, closed=True, g=K("#5a8ab0"), alpha=0.5)


def teacup(x, y, s=1.0, rot=180, broken=True, col="#e9e2d0", pattern="#3a6aa8", seed=1, inner=None):
    """(x, y) centre; rot=180 is upturned (rim down)"""
    r = random.Random(seed)
    with T(x, y, s, rot=rot):
        cup = [(-11, 9), (11, 9)] + bez((11, 9), (11, 0), (7, -6), (4, -7)) + [(4, -9), (-4, -9), (-4, -7)] + bez((-4, -7), (-7, -6), (-11, 0), (-11, 9))
        shape(cup, K(col), 0.9)
        offset_shadow(cup, -3.5, 0, 0.3)
        stroke([(-4, -7), (4, -7)], 0.6)
        stroke(bez((-10, 4), (-4, 2.5), (4, 2.5), (10, 4)), 0.8, g=K(pattern))
        for k in range(4): S.dot(-6 + k*4, -0.5, 0.8, K(pattern))
        stroke(ell(12, 2, 3.4, 4, 14, -100, 100), 1.8)
        stroke(ell(12, 2, 3.4, 4, 14, -100, 100), 0.9, g=K(col))
        if broken:
            hole = [(-3, 9.5), (-1, 4), (2, 6), (4, 1), (7, 5), (8, 9.5)]
            shape(hole, K(inner or "#0b1418"), 0.7)
            if inner: S.fill(hole, K("#ffffff"), 0.4)
            for k in range(3):
                stroke([(r.uniform(-8, 8), r.uniform(-5, 6)), (r.uniform(-8, 8), r.uniform(-5, 6))], 0.4, alpha=0.7)
