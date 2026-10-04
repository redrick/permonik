import math
import common
from icons_kit import *
from icons_sym import *

TREES = {
    "krumpac": ("#4a2014", "#c0603a"), "prach": ("#5a2c0c", "#ff9a3a"), "bratrstvo": ("#463a10", "#f0c850"),
    "valaska": ("#163019", "#7ac070"), "kuse": ("#33241a", "#c8925a"), "lesni": ("#262e16", "#a8b860"),
    "perun": ("#0e1e40", "#6ab8ff"), "svarozic": ("#3e0e0c", "#ff7a30"), "morana": ("#16293c", "#cfeeff"),
    "zakl": ("#22222a", "#b0b0c0"),
}
SKILLS = []


def sk(tree):
    def deco(fn):
        def draw(b):
            bg(b, *TREES[tree]); fn(b.w / 2, b.h / 2); frame(b)
        SKILLS.append((fn.__name__, 64, 64, draw)); return fn
    return deco


def bg(b, base, acc):
    sq = rect(0, 0, b.w, b.h)
    flat(sq, base)
    S.fill([(1, 1), (b.w - 1, 1), (b.w - 1, b.h - 1), (1, b.h - 1)], K(base, 0.3))
    glow(b.w / 2, b.h / 2, b.w * 0.55, acc, 0.32)
    for i in range(6):
        k = i * 0.9
        line(rect(k, k, b.w - 2 * k, b.h - 2 * k) + [(k, k)], "#000000", 1.0, 0.22 - i * 0.03)


def frame(b):
    line(rect(0.6, 0.6, b.w - 1.2, b.h - 1.2) + [(0.6, 0.6)], "#0c0a0a", 1.2)
    line([(1.6, 1.8), (1.6, b.h - 1.6), (b.w - 1.8, b.h - 1.6)], "#ffffff", 0.5, 0.22)
    line([(1.8, 1.6), (b.w - 1.6, 1.6), (b.w - 1.6, b.h - 1.8)], "#000000", 0.5, 0.4)


def swoosh(cx, cy, r, a0, a1, hex_="#ffffff", w=2.4, a=0.85):
    pts = ell(cx, cy, r, r, 24, a0, a1)
    n = len(pts)
    for i in range(n - 1):
        line(pts[i:i + 2], hex_, w * (i + 1) / n + 0.3, a * (i + 1) / n)


def rays(cx, cy, r0, r1, n, hex_, w=0.9, a=0.8, off=0):
    for i in range(n):
        ang = math.radians(off + i * 360 / n)
        line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0), (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)], hex_, w, a)


# ------------------------------------------------------------------ havíř: krumpáč
@sk("krumpac")
def uder_do_zily(cx, cy):
    rock = [(cx - 15, cy - 15), (cx + 15, cy - 15), (cx + 15, cy - 6), (cx + 6, cy - 3), (cx - 4, cy - 5), (cx - 15, cy - 2)]
    form(rock, K("#5a5258", 0.35), W, sh=0.25)
    for (x, y) in ((-8, -10), (2, -9), (9, -12)):
        shape([(cx + x, cy + y), (cx + x + 2.5, cy + y + 1.6), (cx + x + 1, cy + y - 2)], SILVER_L, W * 0.5)
    glow(cx + 1, cy - 4, 7, "#ffd060", 0.6)
    rays(cx + 1, cy - 4, 2.5, 7, 7, "#fff0a0", 0.7, 0.9, 20)
    pick(cx + 5, cy + 6, 0.85, rot=40)


@sk("krumpac")
def rozrazka(cx, cy):
    swoosh(cx + 2, cy - 2, 12, 200, 340, "#ffd0b0", 3.0)
    swoosh(cx + 2, cy - 2, 9, 210, 330, "#ffffff", 1.6, 0.6)
    pick(cx - 1, cy + 3, 0.95, rot=-55)


@sk("krumpac")
def otres(cx, cy):
    flat(ell(cx, cy - 7, 14, 5, 30), "#1a0c08", 0.6)
    for r, a in ((13, 0.5), (9, 0.7), (5, 0.9)):
        line(ell(cx, cy - 7, r, r * 0.38, 30) + [ell(cx, cy - 7, r, r * 0.38, 30)[0]], "#ffb070", 0.9, a)
    for ang in (200, 250, 290, 340):
        a = math.radians(ang)
        line(zig(cx, cy - 7, cx + math.cos(a) * 14, cy - 7 + math.sin(a) * 6, 3, 1.2, ang), "#200a04", 1.0)
    hammer(cx, cy + 4, 1.0, rot=0)


@sk("krumpac")
def zurivost_hory(cx, cy):
    glow(cx, cy, 16, "#ff3020", 0.45)
    m = [(cx - 15, cy - 12), (cx - 6, cy + 6), (cx - 2, cy + 2), (cx + 3, cy + 12), (cx + 15, cy - 12)]
    form(m, K("#4a3a3a", 0.3), W * 1.1, sdx=-2, sdy=0, sh=0.3)
    shape([(cx + 3, cy + 12), (cx, cy + 6), (cx + 2, cy + 5), (cx + 6, cy + 6)], BONE, W * 0.6)
    for sx in (-1, 1):
        shape([(cx + sx * 1.5, cy - 2), (cx + sx * 6, cy - 0.5), (cx + sx * 5.5, cy - 3)], K("#ff3a1a", 0.6), W * 0.5)
    stroke([(cx - 6, cy - 8), (cx - 3, cy - 6.5), (cx, cy - 8), (cx + 3, cy - 6.5), (cx + 6, cy - 8)], 0.9, g=K("#ff3a1a", 0.6))


# ------------------------------------------------------------------ havíř: střelný prach
@sk("prach")
def naloz(cx, cy):
    charge(cx - 1, cy - 3, 1.15, rot=-12)


@sk("prach")
def doutnak(cx, cy):
    f = bez((cx - 14, cy - 10), (cx - 4, cy - 14), (cx - 2, cy + 2), (cx + 6, cy - 2)) + bez((cx + 6, cy - 2), (cx + 12, cy - 5), (cx + 8, cy + 8), (cx + 10, cy + 10))
    line(f, "#1a0c06", 2.2)
    line(f[:20], "#ff7a20", 1.0, 0.9)
    for i in range(0, 20, 4):
        x, y = f[i]
        glow(x, y, 3, "#ff8a20", 0.5)
    glow(cx + 10, cy + 10, 7, "#ffb040", 0.8)
    sparkle(cx + 10, cy + 10, 5, "#fff2a0")
    for (dx, dy) in ((-4, 3), (3, 5), (-2, -4), (4, -3)):
        dot(cx + 10 + dx, cy + 10 + dy, 0.6, K("#ffe080", 0.9))


@sk("prach")
def odstrel(cx, cy):
    glow(cx, cy, 16, "#ff8020", 0.75)
    pts = []
    for i in range(18):
        r = 14 if i % 2 == 0 else 7.5
        a = math.radians(i * 20 + 5)
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    shape(pts, K("#ff9a2a", 0.6), W)
    pts2 = [(cx + (x - cx) * 0.55, cy + (y - cy) * 0.55) for x, y in pts]
    flat(pts2, "#ffe070")
    flat(ell(cx, cy, 3.5, 3.5, 16), "#fffbe8")
    for (x, y, a) in ((-12, 10, 30), (12, 11, -20), (13, -10, 60), (-11, -12, 10)):
        shape([(cx + x - 1.5, cy + y - 1), (cx + x + 1.5, cy + y - 1.5), (cx + x + 1, cy + y + 1.5)], K("#4a4248", 0.3), W * 0.5)


@sk("prach")
def retez_nalozi(cx, cy):
    line([(cx - 11, cy - 9), (cx - 1, cy + 1), (cx + 9, cy + 11)], "#1a0c06", 1.4)
    for i, (x, y) in enumerate(((-10, -9), (0, 0), (10, 9))):
        glow(cx + x, cy + y, 6, "#ff8a20", 0.25 + i * 0.15)
        charge(cx + x, cy + y - 1, 0.55, rot=-10, lit=(i == 2))
    sparkle(cx + 12.5, cy + 15, 3, "#fff2a0")


# ------------------------------------------------------------------ havíř: bratrstvo
@sk("bratrstvo")
def zdar_buh(cx, cy):
    for i, r in enumerate((14, 10.5)):
        line(ell(cx, cy, r, r, 30, 30, 150), "#ffe080", 1.0, 0.5 + i * 0.2)
        line(ell(cx, cy, r, r, 30, 210, 330), "#ffe080", 1.0, 0.5 + i * 0.2)
    with T(cx, cy - 1, 0.9, rot=45):
        tube([(0, -12), (0, 6)], 2.2, 2.4, WOOD, W, sh=0.15)
        form(rect(-5.5, 5, 11, 5.5), IRON, W, sh=0.25)
    with T(cx, cy - 1, 0.9, rot=-45):
        tube([(0, -12), (0, 6)], 2.2, 2.4, WOOD, W, sh=0.15)
        form([(-1.8, 5), (1.8, 5), (2.2, 11), (0, 14), (-2.2, 11)], IRON_L, W, sh=0.25)


@sk("bratrstvo")
def tvrda_kuze(cx, cy):
    sh_ = [(cx - 11, cy + 11), (cx + 11, cy + 11)] + bez((cx + 11, cy + 11), (cx + 12, cy - 2), (cx + 6, cy - 10), (cx, cy - 14)) + \
        bez((cx, cy - 14), (cx - 6, cy - 10), (cx - 12, cy - 2), (cx - 11, cy + 11))
    form(sh_, K("#7a7068", 0.45), W * 1.1, sdx=-2, sdy=0, sh=0.3)
    for p in ([(cx - 11, cy + 2), (cx - 3, cy + 4), (cx + 2, cy - 2), (cx + 11, cy + 1)], [(cx - 3, cy + 4), (cx - 1, cy + 11)], [(cx + 2, cy - 2), (cx + 1, cy - 13)]):
        stroke(p, 0.7, g=K("#3a3230", 0.2))
    hl(bez((cx - 8, cy + 9), (cx - 9, cy), (cx - 5, cy - 7), (cx - 1, cy - 11)), 0.9, 0.5)
    glow(cx, cy, 15, "#f0c850", 0.15)


@sk("bratrstvo")
def vecny_kahan(cx, cy):
    glow(cx, cy + 3, 15, "#ffd060", 0.6)
    rays(cx, cy + 4, 9, 14, 12, "#ffe8a0", 0.8, 0.6)
    stroke(bez((cx, cy + 4), (cx - 1, cy + 9), (cx + 3, cy + 12), (cx + 2, cy + 14)), 0.8, g=IRON)
    body = bez((cx - 7, cy - 10), (cx - 8, cy - 2), (cx - 4, cy + 3), (cx, cy + 4)) + bez((cx, cy + 4), (cx + 4, cy + 3), (cx + 8, cy - 2), (cx + 7, cy - 10)) + \
        bez((cx + 7, cy - 10), (cx + 5, cy - 13), (cx - 5, cy - 13), (cx - 7, cy - 10))
    form(body, IRON, W, sdx=-1.4, sdy=0, sh=0.25)
    stroke(bez((cx - 7, cy - 10), (cx - 3, cy - 12), (cx + 3, cy - 12), (cx + 7, cy - 10)), 0.8, g=BRASS)
    shape([(cx + 4, cy - 2), (cx + 9, cy + 3), (cx + 11, cy + 2), (cx + 6.5, cy - 4.5)], IRON_L, W * 0.6)
    flame_big(cx + 10, cy + 2.5, 9)


@sk("bratrstvo")
def druhy_dech(cx, cy):
    heart = bez((cx, cy - 11), (cx - 4, cy - 6), (cx - 13, cy - 1), (cx - 12, cy + 5)) + bez((cx - 12, cy + 5), (cx - 11, cy + 11), (cx - 3, cy + 11), (cx, cy + 6)) + \
        bez((cx, cy + 6), (cx + 3, cy + 11), (cx + 11, cy + 11), (cx + 12, cy + 5)) + bez((cx + 12, cy + 5), (cx + 13, cy - 1), (cx + 4, cy - 6), (cx, cy - 11))
    glow(cx, cy, 14, "#ff5040", 0.35)
    form(heart, RED_L, W * 1.1, sdx=-1.6, sdy=0, sh=0.25)
    hl(bez((cx - 9, cy + 4), (cx - 9, cy + 8), (cx - 6, cy + 9), (cx - 4, cy + 8)), 0.8, 0.7)
    for k, y in enumerate((-1, 3)):
        line(bez((cx - 15, cy + y), (cx - 5, cy + y + 4), (cx + 5, cy + y - 4), (cx + 15, cy + y)), "#fff8e0", 1.1 - k * 0.3, 0.85)


# ------------------------------------------------------------------ zbojnice: valaška
@sk("valaska")
def sek_valaskou(cx, cy):
    swoosh(cx, cy, 13, 120, 300, "#d8ffd0", 3.0)
    axe(cx + 1, cy - 1, 1.0, rot=-35)


@sk("valaska")
def hod_valaskou(cx, cy):
    for k, r in enumerate((11, 8)):
        line(ell(cx + 3, cy + 1, r, r, 20, 100, 250), "#d8ffd0", 1.0, 0.4 + k * 0.3)
    for i in range(3):
        line([(cx - 15, cy - 6 + i * 4), (cx - 6, cy - 6 + i * 4)], "#d8ffd0", 0.8, 0.5)
    axe(cx + 3, cy + 1, 0.95, rot=-110)


@sk("valaska")
def zbojnicky_skok(cx, cy):
    arc = bez((cx - 14, cy - 12), (cx - 10, cy + 14), (cx + 6, cy + 14), (cx + 12, cy - 10))
    for i in range(0, len(arc) - 1, 2):
        line(arc[i:i + 2], "#d8ffd0", 1.1, 0.8)
    form([(cx + 12, cy - 10), (cx + 8, cy - 7), (cx + 14, cy - 5)], K("#d8ffd0", 0.9), W * 0.6, sh=0)
    for sx in (-1, 1):
        stroke([(cx - 14 + sx * 3, cy - 13), (cx - 14 + sx * 5, cy - 15)], 0.6, g=K("#d8ffd0", 0.9))
    axe(cx - 1, cy + 4, 0.75, rot=-60)


@sk("valaska")
def vir(cx, cy):
    for k in range(3):
        pts = [(cx + math.cos(math.radians(a + k * 120)) * (2 + a / 40), cy + math.sin(math.radians(a + k * 120)) * (2 + a / 40)) for a in range(0, 470, 15)]
        for i in range(len(pts) - 1):
            line(pts[i:i + 2], "#d8ffd0", 0.4 + i * 0.08, 0.3 + i * 0.02)
    for k in range(3):
        a = math.radians(30 + k * 120)
        axe(cx + math.cos(a) * 8, cy + math.sin(a) * 8, 0.55, rot=math.degrees(a) - 90)


# ------------------------------------------------------------------ zbojnice: kuše
@sk("kuse")
def rychla_strela(cx, cy):
    for i in range(4):
        line([(cx - 15, cy - 4 + i * 2.6), (cx - 4 - i * 2, cy - 4 + i * 2.6)], "#ffe8c0", 0.8, 0.6)
    bolt_arrow(cx + 2, cy + 1, 1.0, rot=0, fletch=K("#e8d8b0", 0.8), length=24)
    bolt_arrow(cx - 2, cy - 6, 0.7, rot=0, fletch=K("#e8d8b0", 0.8), length=24)


@sk("kuse")
def prustrel(cx, cy):
    for x in (-5, 4):
        line(ell(cx + x, cy, 2.5, 8, 20) + [ell(cx + x, cy, 2.5, 8, 20)[0]], "#ffe8c0", 1.0, 0.7)
    bolt_arrow(cx, cy, 1.1, rot=0, fletch=K("#e8d8b0", 0.8), length=26)
    line([(cx - 15, cy), (cx - 13, cy)], "#ffffff", 1.0, 0.4)


@sk("kuse")
def ohnivy_sip(cx, cy):
    with T(cx, cy, 1.0, rot=30):
        fireball(8, 0, 3.6, 0, 1.0)
        bolt_arrow(-2, 0, 1.0, fletch=RED, head=IRON_D, length=22)
        flame_big(8.5, -0.5, 7, lean=-2)


@sk("kuse")
def dest_sipu(cx, cy):
    cloud(cx, cy + 9, 0.6, K("#4a4040", 0.3))
    for (x, y) in ((-9, 0), (-3, -4), (3, 1), (9, -3), (0, -9), (-7, -10), (8, -11)):
        bolt_arrow(cx + x, cy + y, 0.42, rot=-75, fletch=K("#e8d8b0", 0.8), length=24)


# ------------------------------------------------------------------ zbojnice: lesní zákon
@sk("lesni")
def uskok(cx, cy):
    def foot(x, y, a, alpha):
        with T(x, y, 1.3, rot=a):
            flat(ell(0, 0, 2.3, 4, 16), "#e8e0c0", alpha)
            flat(ell(0, -5.2, 1.6, 1.8, 12), "#e8e0c0", alpha)
    foot(cx - 9, cy - 7, -20, 0.4); foot(cx - 2, cy - 3, -40, 0.65)
    foot(cx + 6, cy + 3, -60, 1.0)
    line(bez((cx - 12, cy + 2), (cx - 8, cy + 12), (cx + 4, cy + 13), (cx + 12, cy + 8)), "#d8e8a0", 1.2, 0.85)
    flat([(cx + 13.5, cy + 7), (cx + 9, cy + 10.5), (cx + 10.5, cy + 5)], "#d8e8a0", 0.9)


@sk("lesni")
def past_na_vlky(cx, cy):
    flat(ell(cx, cy - 6, 14, 4, 30), "#000000", 0.35)
    plate = ell(cx, cy - 5, 4.5, 2, 16)
    form(plate, IRON, W * 0.7, sh=0.2)
    for sx in (-1, 1):
        jaw = bez((cx + sx * 4, cy - 5), (cx + sx * 15, cy - 4), (cx + sx * 13, cy + 10), (cx + sx * 1, cy + 11))
        stroke(jaw, 1.8, g=IRON_L)
        stroke(jaw, 0.5)
        for t in (5, 8, 11, 14):
            x, y = jaw[t]
            shape([(x - 1, y), (x - sx * 2.6, y - 0.3 + (t - 9) * 0.1), (x, y + 1.2)], STEEL_L, W * 0.4)
    stroke(bez((cx + 4, cy - 6), (cx + 10, cy - 12), (cx + 14, cy - 11), (cx + 15, cy - 14)), 0.8, g=IRON)


@sk("lesni")
def janosikuv_opasek(cx, cy):
    glow(cx, cy, 15, "#ffe080", 0.35)
    with T(cx, cy, 1.0, rot=-12):
        strap = bez((-15, 3), (-6, 6.5), (6, 6.5), (15, 3)) + bez((15, -6.5), (6, -3), (-6, -3), (-15, -6.5))
        form(strap, LEATHER_D, W, sdx=0, sdy=1.6, sh=0.22)
        for x in range(-13, 15, 4):
            yy = 1.5 - (x / 15) ** 2 * 3
            for dy in (-2.4, 0.6):
                dot(x, yy + dy, 0.7, BRASS_L)
        for x in (-5, 3):
            shape(rrect(x - 2.4, -4.6, 4.8, 10, 1), BRASS, W * 0.6)
    sparkle(cx + 9, cy + 9, 3.2, "#fff6c0"); sparkle(cx - 10, cy - 9, 2.2, "#fff6c0")


@sk("lesni")
def kourova_clona(cx, cy):
    for (x, y, s, g) in ((-6, -7, 0.65, "#6a6a5e"), (6, -5, 0.6, "#7a7a6c"), (0, 2, 0.8, "#9a9a88"), (-4, 9, 0.55, "#b0b0a0")):
        cloud(cx + x, cy + y, s, K(g, 0.6))


# ------------------------------------------------------------------ vědma: Perun
@sk("perun")
def jiskra(cx, cy):
    glow(cx, cy, 13, "#7cc4ff", 0.7)
    sparkle(cx, cy, 13, "#bfe6ff", 0.9)
    sparkle(cx, cy, 8, "#ffffff")
    for a in (20, 140, 250):
        r = math.radians(a)
        lightning(zig(cx, cy, cx + math.cos(r) * 14, cy + math.sin(r) * 14, 3, 1.6, a), 0.8)


@sk("perun")
def hromova_koule(cx, cy):
    glow(cx, cy, 15, "#7cc4ff", 0.6)
    flat(ell(cx, cy, 9, 9, 30), "#3a7ad8", 0.85)
    flat(ell(cx, cy, 6.5, 6.5, 24), "#9fd4ff")
    flat(ell(cx - 1, cy + 1, 3, 3, 16), "#ffffff")
    for a in (0, 70, 150, 210, 290):
        r = math.radians(a)
        lightning(zig(cx + math.cos(r) * 4, cy + math.sin(r) * 4, cx + math.cos(r) * 13, cy + math.sin(r) * 13, 3, 1.4, a), 0.7)


@sk("perun")
def retezovy_blesk(cx, cy):
    nodes = [(cx - 12, cy + 9), (cx - 2, cy - 2), (cx + 4, cy + 10), (cx + 12, cy - 9)]
    for i in range(3):
        lightning(zig(*nodes[i], *nodes[i + 1], 4, 1.8, i), 1.1)
    for x, y in nodes:
        glow(x, y, 4, "#bfe6ff", 0.8)
        dot(x, y, 1.2, K("#ffffff", 1))


@sk("perun")
def peruniv_hnev(cx, cy):
    glow(cx, cy - 4, 14, "#6ab8ff", 0.5)
    lightning(zig(cx - 5, cy + 5, cx - 9, cy - 14, 4, 2.0, 3), 1.2)
    lightning(zig(cx + 2, cy + 5, cx + 4, cy - 15, 4, 2.4, 5), 1.6)
    lightning(zig(cx + 8, cy + 5, cx + 13, cy - 11, 3, 1.6, 7), 1.0)
    cloud(cx, cy + 8, 0.95, K("#2a3448", 0.2))


# ------------------------------------------------------------------ vědma: Svarožič
@sk("svarozic")
def ohnivy_jazyk(cx, cy):
    fireball(cx + 6, cy + 4, 5.5, ang=25, tail=1.2)


@sk("svarozic")
def ohniva_stena(cx, cy):
    glow(cx, cy - 2, 16, "#ff6a20", 0.45)
    for x, h in ((-11, 15), (-4, 21), (4, 18), (11, 14)):
        flame_big(cx + x, cy - 12, h, lean=0.5)
    line([(cx - 15, cy - 12), (cx + 15, cy - 12)], "#2a0a04", 1.4)


@sk("svarozic")
def kupalska_vatra(cx, cy):
    for k, r in enumerate((14.5, 11.5)):
        e = ell(cx, cy - 3, r, r * 0.5, 30)
        line(e + [e[0]], "#ffb040", 1.0, 0.5 + 0.25 * k)
    for a in (-30, 30, 0):
        with T(cx, cy - 8, 1.0, rot=a):
            tube([(-8, 0), (8, 0)], 2.4, 2.4, WOOD_D, W * 0.7, sh=0.1)
    flame_big(cx, cy - 7, 20, lean=1)
    for (x, y) in ((-9, 6), (8, 9), (5, 13), (-5, 12)):
        dot(cx + x, cy + y, 0.7, K("#ffe080", 0.9))


def firebird(cx, cy, s=1.0):
    with T(cx, cy, s):
        glow(0, 0, 17, "#ff8020", 0.55)
        for k, c in enumerate(("#e2481a", "#ff9a2a", "#ffe070")):
            tail = bez((-3, -2), (-12, -6 - k * 2), (-14, -14 + k * 2), (-6 - k * 3, -16 + k))
            line(tail, c, 2.2 - k * 0.4)
        for sgn in (1,):
            wing = [(-2, 1)] + bez((-2, 1), (-6, 8), (-10, 14), (-14, 15)) + bez((-14, 15), (-6, 13), (2, 12), (4, 3))
            flat(wing, "#ff7a20")
            wing2 = [(0, 2)] + bez((0, 2), (4, 9), (10, 13), (15, 13)) + bez((15, 13), (10, 8), (8, 4), (5, 0))
            flat(wing2, "#ffb030")
        body = bez((-5, -1), (-2, -5), (6, -4), (8, 3)) + bez((8, 3), (9, 6), (12, 7), (12, 8)) + [(9, 9)] + bez((9, 9), (6, 7), (0, 6), (-5, -1))
        flat(body, "#ffd060")
        stroke(body, 0.5, closed=True, g=K("#6a1a08", 0.2), alpha=0.6)
        dot(8.5, 7, 0.6, K("#2a0a04", 0.1))
        for k in range(3):
            line([(7 + k, 9), (6 + k * 2, 12 + k * 0.5)], "#ffe070", 0.6)


@sk("svarozic")
def zar_ptak(cx, cy):
    firebird(cx + 1, cy, 0.95)


# ------------------------------------------------------------------ vědma: Morana
@sk("morana")
def mrazivy_dech(cx, cy):
    cone = [(cx - 12, cy - 2), (cx + 15, cy + 10), (cx + 15, cy - 13)]
    C.saveState(); C.clipPath(poly(cone), stroke=0, fill=0)
    glow(cx - 8, cy - 2, 26, "#cfeeff", 0.75)
    C.restoreState()
    for i in range(5):
        y = cy - 10 + i * 4.5
        line(bez((cx - 10, cy - 2), (cx, cy - 2 + (y - cy) * 0.4), (cx + 8, y), (cx + 15, y)), "#ffffff", 0.8, 0.6)
    snowflake(cx + 7, cy + 5, 3.5, 0.6)
    snowflake(cx + 9, cy - 7, 3, 0.6)
    snowflake(cx - 10, cy - 2, 4.5, 0.8)


@sk("morana")
def ledova_zbroj(cx, cy):
    glow(cx, cy, 15, "#9fd8ff", 0.45)
    for (x, y, l, w_, a) in ((-7, 0, 16, 7, 100), (7, 0, 16, 7, 80), (0, 4, 22, 8, 90), (-11, -6, 10, 5, 120), (11, -6, 10, 5, 60), (0, -8, 12, 6, 90)):
        shard(cx + x, cy + y, l, w_, a)
    sparkle(cx + 4, cy + 10, 2.4)


@sk("morana")
def moranina_naruc(cx, cy):
    glow(cx, cy, 15, "#cfeeff", 0.55)
    e = ell(cx, cy, 10, 10, 30)
    line(e + [e[0]], "#ffffff", 1.0, 0.7)
    for i in range(10):
        a = i * 36
        r = math.radians(a)
        shard(cx + math.cos(r) * 11, cy + math.sin(r) * 11, 7, 3.4, a)
    snowflake(cx, cy, 6, 1.0)


@sk("morana")
def vynaseni_morany(cx, cy):
    tube([(cx, cy - 15), (cx, cy + 12)], 1.6, 1.6, WOOD_D, W * 0.7, sh=0)
    straw = K("#d8c070", 0.75)
    skirt = [(cx - 3, cy + 1), (cx + 3, cy + 1), (cx + 8, cy - 11), (cx - 8, cy - 11)]
    form(skirt, straw, W * 0.8, sdx=-1.4, sdy=0, sh=0.25)
    for x in range(-7, 8, 2):
        stroke([(cx + x * 0.35, cy), (cx + x, cy - 10.5)], 0.35, g=K("#8a6a2a", 0.4))
    stroke([(cx - 9, cy + 4), (cx + 9, cy + 4)], 1.6, g=straw)
    head = ell(cx, cy + 7.5, 3.6, 4, 16)
    shape(head, CLOTH_W, W * 0.7)
    shape(bez((cx - 4, cy + 8), (cx - 4, cy + 13), (cx + 4, cy + 13), (cx + 4, cy + 8)), RED, W * 0.6)
    for x in (-1.3, 1.3):
        dot(cx + x, cy + 7, 0.5, INK)
    for x in (-9, 9):
        stroke([(cx + x, cy + 4), (cx + x * 1.2, cy + 1)], 0.5, g=K("#c02a2a", 0.4))
    snowflake(cx - 11, cy - 10, 2.6, 0.5); snowflake(cx + 11, cy - 4, 2.2, 0.5)


# ------------------------------------------------------------------ general
@sk("zakl")
def utok(cx, cy):
    swoosh(cx, cy, 13, 150, 300, "#ffffff", 2.6, 0.7)
    with T(cx, cy, 1.0, rot=-40):
        form([(-1.6, -3), (0, 15), (1.6, -3)], STEEL, W * 0.8, sdx=-0.8, sdy=0, sh=0.25)
        shape(rect(-6, -4.5, 12, 2), BRASS, W * 0.6)
        shape(rect(-1.4, -12, 2.8, 7.5), LEATHER_D, W * 0.6)
        shape(ell(0, -13, 1.8, 1.8, 12), BRASS, W * 0.5)


@sk("zakl")
def brana(cx, cy):
    arch = [(cx - 9, cy - 13)] + bez((cx - 9, cy - 13), (cx - 10, cy + 6), (cx - 6, cy + 13), (cx, cy + 13)) + \
        bez((cx, cy + 13), (cx + 6, cy + 13), (cx + 10, cy + 6), (cx + 9, cy - 13))
    glow(cx, cy, 15, "#4aa0ff", 0.6)
    shape(arch, K("#2a6ad0", 0.4), W * 1.1)
    C.saveState(); C.clipPath(poly(arch), stroke=0, fill=0)
    for k in range(5):
        r = 3 + k * 2.5
        e = ell(cx, cy - 2, r, r * 1.2, 24, 0, 300 - k * 20)
        line(e, "#cfe8ff", 0.7, 0.85 - k * 0.12)
    C.restoreState()
    stroke([(cx - 13, cy - 13), (cx + 13, cy - 13)], 1.4, g=K("#5a5048", 0.4))
    for x in (-11, 11):
        form(rect(cx + x - 2, cy - 13, 4, 22), K("#6a6058", 0.45), W * 0.8, sh=0.25)


@sk("zakl")
def zjeveni(cx, cy):
    glow(cx, cy, 15, "#ffe8a0", 0.45)
    rays(cx, cy, 10, 14, 12, "#ffe8a0", 0.8, 0.7, 15)
    eye = bez((cx - 13, cy), (cx - 6, cy + 9), (cx + 6, cy + 9), (cx + 13, cy)) + bez((cx + 13, cy), (cx + 6, cy - 9), (cx - 6, cy - 9), (cx - 13, cy))
    shape(eye, BONE, W * 1.1)
    shape(ell(cx, cy, 5, 5, 20), K("#3a8ad0", 0.5), W * 0.7)
    dot(cx, cy, 2.2, INK)
    flat(ell(cx - 1.6, cy + 1.6, 1.2, 1.2, 10), "#ffffff")


if __name__ == "__main__":
    common.run({"ui/skills": SKILLS})
