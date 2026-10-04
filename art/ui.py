import math, random
import common
from reportlab.pdfgen.canvas import FILL_EVEN_ODD
from icons_kit import *

UI = []
DARKWOOD = K("#3a2618", 0.25); DARKWOOD_L = K("#5a3c24", 0.35)
PANEL_IN = "#211b17"
ORB_L = (100, 64); ORB_R = (1820, 64); ORB_RAD = 96
BELT_X = 631; SKILL_X = 945; SLOT_Y = 72; SLOT = 64; GAP = 6
XP = (360, 22, 1200, 20)


def ui(name, w, h, paper=False):
    def deco(fn):
        UI.append((name, w, h, fn, paper)); return fn
    return deco


def holes_path(outer, holes):
    p = C.beginPath()
    p.moveTo(*outer[0]); [p.lineTo(*q) for q in outer[1:]]; p.close()
    for h in holes:
        p.moveTo(*h[0]); [p.lineTo(*q) for q in h[1:]]; p.close()
    return p


def ring_fill(cx, cy, r0, r1, g, n=72):
    C.saveState()
    C.clipPath(holes_path(ell(cx, cy, r1, r1, n), [ell(cx, cy, r0, r0, n)]), stroke=0, fill=0, fillMode=FILL_EVEN_ODD)
    S.fill(rect(cx - r1, cy - r1, 2 * r1, 2 * r1), g)
    C.restoreState()


def grain(x, y, w, h, n, seed, hex_="#1c1008", a=0.5, horiz=True):
    r = random.Random(seed)
    for _ in range(n):
        if horiz:
            yy = y + r.uniform(0.05, 0.95) * h; x0 = x + r.uniform(-0.2, 0.7) * w; L = r.uniform(0.2, 0.6) * w
            pts = [(x0 + L * t / 8, yy + math.sin(t * 0.9 + r.random() * 6) * h * 0.04) for t in range(9)]
        else:
            xx = x + r.uniform(0.05, 0.95) * w; y0 = y + r.uniform(-0.2, 0.7) * h; L = r.uniform(0.2, 0.6) * h
            pts = [(xx + math.sin(t * 0.9 + r.random() * 6) * w * 0.04, y0 + L * t / 8) for t in range(9)]
        line(pts, hex_, r.uniform(0.25, 0.5), a * r.uniform(0.5, 1))


def planks(x, y, w, h, n, seed=1, g=DARKWOOD):
    S.fill(rect(x, y, w, h), g)
    ph = h / n
    for i in range(n):
        grain(x, y + i * ph, w, ph, int(w / 12), seed + i)
        if i:
            line([(x, y + i * ph), (x + w, y + i * ph)], "#0e0804", 0.9, 0.85)
            line([(x, y + i * ph - 0.7), (x + w, y + i * ph - 0.7)], "#a87a50", 0.35, 0.35)


def iron_band(x, y, w, h, rivets=True, step=40):
    S.fill(rect(x, y, w, h), IRON)
    line([(x, y + h - 0.5), (x + w, y + h - 0.5)], "#b8c0cc", 0.5, 0.6)
    line([(x, y + 0.4), (x + w, y + 0.4)], "#0a0a0c", 0.8, 0.8)
    if rivets:
        k = x + step / 2
        while k < x + w:
            rivet(k, y + h / 2, min(1.4, h * 0.28)); k += step


def inset(x, y, w, h, deep=True):
    flat(rect(x, y, w, h), "#120e0c")
    for i in range(4):
        line([(x + i * 0.6, y + i * 0.6), (x + i * 0.6, y + h - i * 0.6), (x + w - i * 0.6, y + h - i * 0.6)], "#000000", 0.7, 0.35)
    line([(x, y), (x + w, y), (x + w, y + h)], "#8a7a6a", 0.5, 0.5)


def slot_frame(x, y, s):
    inset(x, y, s, s)
    line(rect(x - 1.2, y - 1.2, s + 2.4, s + 2.4) + [(x - 1.2, y - 1.2)], "#5a5f68", 1.6)
    line(rect(x - 2.2, y - 2.2, s + 4.4, s + 4.4) + [(x - 2.2, y - 2.2)], "#0a0a0c", 0.6)
    for (px, py) in ((x - 1.2, y - 1.2), (x + s + 1.2, y - 1.2), (x - 1.2, y + s + 1.2), (x + s + 1.2, y + s + 1.2)):
        rivet(px, py, 1.1)


# ------------------------------------------------------------------ orbs
@ui("orb_frame", 192, 192)
def orb_frame(b):
    cx, cy = b.w / 2, b.h / 2
    ring_fill(cx, cy, 40, 47.5, DARKWOOD_L)
    C.saveState()
    C.clipPath(holes_path(ell(cx, cy, 47.5, 47.5, 72), [ell(cx, cy, 40, 40, 72)]), stroke=0, fill=0, fillMode=FILL_EVEN_ODD)
    for i in range(36):
        a = math.radians(i * 10 + 3)
        line([(cx + math.cos(a) * 40, cy + math.sin(a) * 40), (cx + math.cos(a + 0.05) * 47.5, cy + math.sin(a + 0.05) * 47.5)], "#1c1008", 0.4, 0.5)
    glow(cx - 20, cy + 20, 50, "#ffffff", 0.08)
    C.restoreState()
    ring_fill(cx, cy, 40, 43.5, IRON)
    stroke(ell(cx, cy, 47.5, 47.5, 96), 1.4, closed=True)
    stroke(ell(cx, cy, 40, 40, 96), 1.2, closed=True)
    line(ell(cx, cy, 43.5, 43.5, 96) + [ell(cx, cy, 43.5, 43.5, 96)[0]], "#0a0a0c", 0.6, 0.8)
    line(ell(cx, cy, 41.2, 41.2, 60, 100, 200), "#c8d0da", 0.6, 0.5)
    line(ell(cx, cy, 46.5, 46.5, 60, 100, 190), "#c09a70", 0.5, 0.45)
    for i in range(16):
        a = math.radians(i * 22.5)
        rivet(cx + math.cos(a) * 41.8, cy + math.sin(a) * 41.8, 0.95)
    for a in (45, 135, 225, 315):
        r = math.radians(a)
        with T(cx + math.cos(r) * 45, cy + math.sin(r) * 45, 1.0, rot=a - 90):
            br = [(-5, -3), (5, -3), (4, 3.5), (0, 5), (-4, 3.5)]
            form(br, IRON, W, sdx=-0.8, sdy=0, sh=0.25)
            rivet(0, 0.5, 1.1)


def orb(b, deep, mid, light, hi):
    cx, cy = b.w / 2, b.h / 2
    R = b.w / 2
    disc = ell(cx, cy, R, R, 90)
    flat(disc, deep)
    C.saveState(); C.clipPath(poly(disc), stroke=0, fill=0)
    S.fill(disc, K(mid, 0.4))
    glow(cx + 6, cy - 10, R * 0.95, light, 0.55)
    glow(cx, cy, R * 1.25, "#000000", 0.0)
    for i in range(10):
        rr = R - i * 1.2
        line(ell(cx, cy, rr, rr, 90) + [ell(cx, cy, rr, rr, 90)[0]], "#000000", 1.3, 0.12)
    r = random.Random(len(mid))
    for _ in range(14):
        x, y, s = r.uniform(-R * 0.6, R * 0.6), r.uniform(-R * 0.7, R * 0.3), r.uniform(0.6, 2.0)
        line(ell(cx + x, cy + y, s, s, 12) + [ell(cx + x, cy + y, s, s, 12)[0]], hi, 0.35, 0.45)
    for k in range(3):
        y0 = cy + R * (0.25 - k * 0.32)
        line([(cx - R + (x / 40) * 2 * R, y0 + math.sin(x * 0.45 + k * 2) * 1.6) for x in range(41)], hi, 0.5, 0.18)
    C.restoreState()
    hlp = ell(cx - R * 0.08, cy + R * 0.1, R * 0.78, R * 0.78, 40, 105, 165)
    line(hlp, "#ffffff", 3.2, 0.4)
    line(hlp[8:30], "#ffffff", 1.4, 0.6)
    flat(ell(cx - R * 0.42, cy + R * 0.5, R * 0.12, R * 0.08, 16, rot=40), "#ffffff", 0.8)
    line(ell(cx + R * 0.05, cy - R * 0.15, R * 0.8, R * 0.8, 30, 280, 350), light, 1.0, 0.35)


@ui("orb_hp", 160, 160)
def orb_hp(b):
    orb(b, "#2a0406", "#8a1018", "#e8403a", "#ffc0b0")


@ui("orb_mana", 160, 160)
def orb_mana(b):
    orb(b, "#040a2a", "#13308a", "#4a8aff", "#c0dcff")


# ------------------------------------------------------------------ HUD
def px(v): return v / 2


@ui("hud_bar", 1920, 160, True)
def hud_bar(b):
    H = b.h
    holes = []
    for (ox, oy) in (ORB_L, ORB_R):
        holes.append(ell(px(ox), H - px(oy), px(ORB_RAD) - 1, px(ORB_RAD) - 1, 90))
    body = rect(0, 0, b.w, H - 6)
    C.saveState(); C.clipPath(holes_path(body, holes), stroke=0, fill=0, fillMode=FILL_EVEN_ODD)
    planks(0, 0, b.w, H - 6, 4, 3)
    hatch(rect(0, 0, b.w, 14), 1.6, 30, 0.4, 0.0, 0.5)
    flat(rect(0, 0, b.w, 22), "#000000", 0.25)
    for xx in (112, 296):
        for side in (1, -1):
            x = b.w / 2 + side * (b.w / 2 - xx)
            iron_band(x - 7, 0, 14, H - 6, rivets=False)
            for y in (12, 34, 56):
                rivet(x, y, 1.4)
    iron_band(0, H - 13, b.w, 7, step=30)
    iron_band(0, 0, b.w, 5, rivets=False)
    xx, xy, xw, xh = [px(v) for v in XP]
    xt = H - xy - xh
    inset(xx - 2, xt - 2, xw + 4, xh + 4)
    line(rect(xx - 3, xt - 3, xw + 6, xh + 6) + [(xx - 3, xt - 3)], "#5a5f68", 1.4)
    for k in range(1, 10):
        line([(xx + xw * k / 10, xt), (xx + xw * k / 10, xt + 2.5)], "#8a7a6a", 0.5, 0.6)
    for (sx, n) in ((BELT_X, 4), (SKILL_X, 5)):
        x0, y0 = px(sx), H - px(SLOT_Y) - px(SLOT)
        bw_ = n * px(SLOT) + (n - 1) * px(GAP)
        S.fill(rect(x0 - 6, y0 - 5, bw_ + 12, px(SLOT) + 10), LEATHER_D)
        line(rect(x0 - 6, y0 - 5, bw_ + 12, px(SLOT) + 10) + [(x0 - 6, y0 - 5)], "#0a0604", 1.0)
        for i in range(n):
            slot_frame(x0 + i * (px(SLOT) + px(GAP)), y0, px(SLOT))
    mx = (px(BELT_X) + 4 * px(SLOT) + 3 * px(GAP) + px(SKILL_X)) / 2
    my = H - px(SLOT_Y) - px(SLOT) / 2
    glow(mx, my, 9, "#9fd8ff", 0.35)
    shape([(mx, my + 7), (mx + 5, my), (mx, my - 7), (mx - 5, my)], IRON, W)
    dot(mx, my, 1.4, K("#dff3ff", 0.97))
    for side in (-1, 1):
        cxo = b.w / 2 + side * (b.w / 2 - 215)
        lamp_emblem(cxo, H / 2 - 4, side)
    C.restoreState()
    for (ox, oy) in (ORB_L, ORB_R):
        cxh, cyh = px(ox), H - px(oy)
        C.saveState(); C.clipPath(poly(rect(0, 0, b.w, H - 6)), stroke=0, fill=0)
        stroke(ell(cxh, cyh, px(ORB_RAD) + 1, px(ORB_RAD) + 1, 120), 3.0, closed=True, g=IRON)
        stroke(ell(cxh, cyh, px(ORB_RAD) + 2.6, px(ORB_RAD) + 2.6, 120), 0.7, closed=True)
        C.restoreState()
    line([(0, H - 6), (b.w, H - 6)], "#0a0a0c", 1.0)


def lamp_emblem(cx, cy, side):
    for sx in (-1, 1):
        stroke(bez((cx, cy - 10), (cx + sx * 14, cy - 12), (cx + sx * 22, cy), (cx + sx * 34, cy - 2)), 1.2, g=BRASS)
        stroke(bez((cx + sx * 18, cy - 4), (cx + sx * 20, cy + 6), (cx + sx * 26, cy + 8), (cx + sx * 28, cy + 3)), 0.8, g=BRASS)
    with T(cx, cy, 1.0, rot=45):
        tube([(0, -14), (0, 8)], 2.2, 2.4, WOOD, W, sh=0.15)
        form(rect(-5, 7, 10, 5), IRON, W, sh=0.25)
    with T(cx, cy, 1.0, rot=-45):
        tube([(0, -14), (0, 8)], 2.2, 2.4, WOOD, W, sh=0.15)
        form([(-1.8, 7), (1.8, 7), (2.2, 12), (0, 15), (-2.2, 12)], IRON_L, W, sh=0.25)


# ------------------------------------------------------------------ panel, slots, buttons
@ui("panel", 512, 512, True)
def panel(b):
    w, h = b.w, b.h
    B = 24
    flat(rect(0, 0, w, h), PANEL_IN)
    flat(rect(B, B, w - 2 * B, h - 2 * B), PANEL_IN)
    edges = [("b", rect(0, 0, w, B)), ("t", rect(0, h - B, w, B)), ("l", rect(0, 0, B, h)), ("r", rect(w - B, 0, B, h))]
    for side, r in edges:
        C.saveState()
        if side in "bt":
            C.clipPath(poly([(0, r[0][1]), (w, r[0][1]), (w - B, r[0][1] + B), (B, r[0][1] + B)] if side == "b" else
                            [(B, h - B), (w - B, h - B), (w, h), (0, h)]), stroke=0, fill=0)
        else:
            C.clipPath(poly([(0, 0), (B, B), (B, h - B), (0, h)] if side == "l" else [(w, 0), (w, h), (w - B, h - B), (w - B, B)]), stroke=0, fill=0)
        flat(r, "#3a2618")
        for k in range(5):
            o = 5 + k * 3.4
            if side in "bt":
                yy = o if side == "b" else h - o
                line([(0, yy), (w, yy)], "#1c1008", 0.4, 0.55)
                line([(0, yy + 0.8), (w, yy + 0.8)], "#7a5232", 0.35, 0.3)
            else:
                xx = o if side == "l" else w - o
                line([(xx, 0), (xx, h)], "#1c1008", 0.4, 0.55)
                line([(xx + 0.8, 0), (xx + 0.8, h)], "#7a5232", 0.35, 0.3)
        C.restoreState()
    line(rect(1, 1, w - 2, h - 2) + [(1, 1)], "#4a4e57", 2.2)
    line(rect(0.3, 0.3, w - 0.6, h - 0.6) + [(0.3, 0.3)], "#08080a", 0.6)
    line(rect(2.3, 2.3, w - 4.6, h - 4.6) + [(2.3, 2.3)], "#a0a8b4", 0.35, 0.5)
    line(rect(B - 4, B - 4, w - 2 * B + 8, h - 2 * B + 8) + [(B - 4, B - 4)], "#6b4429", 3.0)
    line(rect(B - 4, B - 4, w - 2 * B + 8, h - 2 * B + 8) + [(B - 4, B - 4)], "#c09040", 0.5, 0.7)
    line(rect(B - 1.6, B - 1.6, w - 2 * B + 3.2, h - 2 * B + 3.2) + [(B - 1.6, B - 1.6)], "#0a0806", 1.2)
    for (x, y, rx, ry) in ((0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)):
        with T(x, y, 1.0):
            br = [(0, 0), (rx * 22, 0), (rx * 22, ry * 6), (rx * 9, ry * 9), (rx * 6, ry * 22), (0, ry * 22)]
            form(br, IRON, W, sdx=-rx * 0.8, sdy=-ry * 0.8, sh=0.25)
            for (a, c) in ((3.5, 3.5), (16, 3), (3, 16), (8.5, 8.5)):
                rivet(rx * a, ry * c, 1.3)
            hl([(rx * 1.6, ry * 1.6), (rx * 20, ry * 1.6)], 0.5, 0.35)


@ui("slot", 56, 56)
def slot(b):
    inset(0, 0, b.w, b.h)
    S.fill(rect(1.5, 1.5, b.w - 3, b.h - 3), K("#1c1714", 0.12))
    flat(rect(1.5, 1.5, b.w - 3, b.h - 3), "#161210", 0.6)
    line(rect(0.5, 0.5, b.w - 1, b.h - 1) + [(0.5, 0.5)], "#4a4038", 0.8)
    line([(1.2, 1.2), (1.2, b.h - 1.2), (b.w - 1.2, b.h - 1.2)], "#000000", 0.8, 0.6)


@ui("slot_hover", 56, 56)
def slot_hover(b):
    slot(b)
    C.saveState(); C.clipPath(poly(rect(0, 0, b.w, b.h)), stroke=0, fill=0)
    glow(b.w / 2, b.h / 2, b.w * 0.6, "#ffc860", 0.22)
    C.restoreState()
    line(rect(0.6, 0.6, b.w - 1.2, b.h - 1.2) + [(0.6, 0.6)], "#e8b050", 1.0, 0.95)
    line(rect(1.8, 1.8, b.w - 3.6, b.h - 3.6) + [(1.8, 1.8)], "#ffe8a0", 0.4, 0.5)


def button(b, state):
    w, h = b.w, b.h
    off = -1.0 if state == "down" else 0.0
    plate = rrect(2, 2 + off * 0.5, w - 4, h - 4, 4)
    flat(rrect(2.5, 1.2, w - 4, h - 4, 4), "#000000", 0.5)
    C.saveState(); C.clipPath(poly(plate), stroke=0, fill=0)
    planks(2, 2 + off * 0.5, w - 4, h - 4, 2, 7, K("#4a3020", 0.3) if state != "hover" else K("#6a4628", 0.4))
    if state == "hover":
        glow(w / 2, h / 2, w * 0.45, "#ffc060", 0.3, ry=h * 0.8)
    if state == "down":
        flat(rect(0, 0, w, h), "#000000", 0.3)
        hatch(rect(0, h - 10, w, 10), 1.4, 30, 0.35, 0.0, 0.6)
    else:
        line([(4, h - 4.5), (w - 4, h - 4.5)], "#ffffff", 0.6, 0.18)
        flat(rect(0, 0, w, 6), "#000000", 0.25)
    C.restoreState()
    for x0 in (2, w - 16):
        cap = rect(x0, 2 + off * 0.5, 14, h - 4)
        C.saveState(); C.clipPath(poly(plate), stroke=0, fill=0)
        S.fill(cap, IRON); line([(x0 + 1, 3), (x0 + 1, h - 3)], "#b8c0cc", 0.4, 0.5)
        C.restoreState()
        rivet(x0 + 7, h / 2 + 7 + off * 0.5, 1.2); rivet(x0 + 7, h / 2 - 7 + off * 0.5, 1.2)
    stroke(plate, 1.2, closed=True)
    if state == "hover":
        line(rrect(1, 1, w - 2, h - 2, 5) + [rrect(1, 1, w - 2, h - 2, 5)[0]], "#e8b050", 0.9, 0.9)


@ui("button", 256, 64, True)
def button_n(b): button(b, "normal")


@ui("button_hover", 256, 64, True)
def button_hover(b): button(b, "hover")


@ui("button_down", 256, 64, True)
def button_down(b): button(b, "down")


# ------------------------------------------------------------------ cursors, bars, marker
@ui("cursor", 48, 48)
def cursor(b):
    with T(0.5, b.h - 0.5, 1.12):
        ar = [(0, 0), (0.2, -18), (4.6, -14), (8.2, -21.5), (11.6, -20), (8.2, -12.6), (13.8, -12.4)]
        form(ar, STEEL_D, W * 1.1, sdx=0.9, sdy=0.9, sh=0.3)
        for k in (5.5, 9.5):
            stroke([(0.2, -k * 1.15), (k * 0.86, -k * 0.86)], 0.5, g=IRON_D)
        hl([(1.2, -2.5), (1.4, -13)], 0.6, 0.7)
        hl([(1.8, -1.8), (9, -9.6)], 0.4, 0.5)
        tail = [(4.6, -14), (8.2, -21.5), (11.6, -20), (8.2, -12.6)]
        shape([(5.6, -15.4), (8.4, -21), (11, -19.8), (8, -14)], LEATHER, W * 0.6)
        rivet(3, -9, 0.8, BRASS)


@ui("cursor_attack", 48, 48)
def cursor_attack(b):
    with T(0.8, b.h - 0.8, 1.0, rot=45):
        blade = [(0, 0), (-1.8, -4), (-1.6, -15), (1.6, -15), (1.8, -4)]
        form(blade, STEEL, W, sdx=0.8, sdy=0, sh=0.25)
        shape(rect(-5, -17, 10, 2.2), BRASS, W * 0.8)
        shape(rect(-1.3, -23, 2.6, 6), LEATHER_D, W * 0.7)
        shape(ell(0, -24.5, 1.7, 1.7, 12), BRASS, W * 0.6)
    with T(12, b.h - 12, 0.62, rot=-45):
        tube([(0, -14), (0, 6)], 2.6, 3.0, WOOD, W, sh=0.15)
        top = bez((-11, 4), (-5, 10), (5, 10), (11, 4))
        bot = bez((11, 4), (5, 6.5), (-5, 6.5), (-11, 4))
        form(top + bot[1:], IRON, W, sh=0.25)


@ui("xp_bar", 1200, 20)
def xp_bar(b):
    w, h = b.w, b.h
    flat(rect(0, 0, w, h), "#8a5a10")
    S.fill(rect(0, 0, w, h), K("#c8901c", 0.55))
    flat(rect(0, h * 0.55, w, h * 0.3), "#ffe08a", 0.35)
    flat(rect(0, 0, w, h * 0.3), "#3a2006", 0.35)
    line([(0, h * 0.75), (w, h * 0.75)], "#fff4c0", 0.5, 0.6)


@ui("boss_bar", 900, 48)
def boss_bar(b):
    w, h = b.w, b.h
    fx, fy, fw, fh = 24, 7, w - 48, 10
    body = rrect(10, 2, w - 20, h - 4, 3)
    C.saveState(); C.clipPath(holes_path(body, [rect(fx, fy, fw, fh)]), stroke=0, fill=0, fillMode=FILL_EVEN_ODD)
    S.fill(rect(0, 0, w, h), IRON)
    line([(10, h - 3), (w - 10, h - 3)], "#c8d0da", 0.5, 0.5)
    flat(rect(0, 0, w, 6), "#000000", 0.3)
    C.restoreState()
    stroke(body, 1.0, closed=True)
    line(rect(fx - 0.5, fy - 0.5, fw + 1, fh + 1) + [(fx - 0.5, fy - 0.5)], "#08080a", 1.0)
    line([(fx, fy + fh + 0.6), (fx + fw, fy + fh + 0.6)], "#000000", 0.8, 0.4)
    for x in range(int(fx + 30), int(fx + fw - 10), 60):
        rivet(x, 4.5, 0.8); rivet(x, h - 4.2, 0.8)
    for side in (-1, 1):
        cx = w / 2 + side * (w / 2 - 12)
        with T(cx, h / 2, 1.0):
            sk = bez((-8, -2), (-9, 10), (9, 10), (8, -2)) + bez((8, -2), (7, -6), (4, -7.5), (3.5, -10)) + [(-3.5, -10)] + bez((-3.5, -10), (-4, -7.5), (-7, -6), (-8, -2))
            form(sk, BONE, W, sdx=-1, sdy=1, sh=0.25)
            for sx in (-1, 1):
                shape(ell(sx * 3.4, 1, 2.4, 2.6, 12), INK, W * 0.5)
                dot(sx * 3.4, 1, 0.8, K("#ff3020", 0.6))
            shape([(-1, -3.5), (0, -1.5), (1, -3.5)], INK, W * 0.4)
            for x in (-2, 0, 2):
                stroke([(x, -10), (x, -7.5)], 0.4)


@ui("map_marker", 24, 24)
def map_marker(b):
    cx, cy = b.w / 2, b.h / 2
    glow(cx, cy, 6, "#ffd060", 0.6)
    p = [(cx, cy + 5.5), (cx + 4, cy - 4.5), (cx, cy - 2.5), (cx - 4, cy - 4.5)]
    shape(p, K("#ffcf4a", 0.8), 0.9)
    flat([(cx, cy + 4), (cx - 2.6, cy - 3.2), (cx, cy - 2)], "#fff4c0", 0.8)


if __name__ == "__main__":
    common.run({"ui": UI})
