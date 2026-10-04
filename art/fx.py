import math, random
import common
from icons_kit import *
from icons_sym import *
import skills_icons as SI

FX = []


def fx(w, h):
    def deco(fn):
        FX.append((fn.__name__, w, h, fn)); return fn
    return deco


@fx(64, 16)
def arrow(b):
    with T(b.w / 2, b.h / 2, 1.0):
        tube([(-14, 0), (10, 0)], 1.2, 1.2, WOOD_L, W * 0.7, sh=0)
        form([(9, -2.4), (16, 0), (9, 2.4)], IRON_L, W * 0.7, sh=0.2)
        for sy in (-1, 1):
            shape([(-15, 0), (-9, 0), (-11.5, sy * 3.2), (-16, sy * 3.2)], K("#d8d0b8", 0.85), W * 0.5)


@fx(48, 16)
def bolt(b):
    with T(b.w / 2, b.h / 2, 1.0):
        tube([(-9, 0), (6, 0)], 1.6, 1.6, WOOD, W * 0.7, sh=0)
        form([(5, -2.8), (11.5, 0), (5, 2.8)], IRON, W * 0.7, sh=0.25)
        for sy in (-1, 1):
            shape([(-10, 0), (-5, 0), (-7, sy * 2.8), (-10.5, sy * 2.8)], LEATHER_L, W * 0.5)


@fx(48, 48)
def valaska(b):
    for k, r in enumerate((10, 7.5)):
        line(ell(b.w / 2, b.h / 2, r, r, 20, 110, 250), "#e8fff0", 1.0, 0.25 + k * 0.2)
    axe(b.w / 2, b.h / 2 - 1, 0.75, rot=-60)


@fx(40, 40)
def naloz(b):
    charge(b.w / 2 - 1, b.h / 2 - 3, 0.85, rot=-20)
    r = random.Random(3)
    for _ in range(6):
        dot(b.w / 2 + 8 + r.uniform(-3, 3), b.h / 2 + 10 + r.uniform(-3, 3), 0.45, K("#ffe080", 0.9))


@fx(64, 32)
def firebolt(b):
    fireball(b.w / 2 + 8, b.h / 2, 5.0, 0, 1.1)


@fx(48, 24)
def ice_shard(b):
    glow(b.w / 2 + 2, b.h / 2, 10, "#9fd8ff", 0.45)
    for i in range(3):
        line([(b.w / 2 - 20, b.h / 2 - 2 + i * 2), (b.w / 2 - 8, b.h / 2 - 2 + i * 2)], "#dff3ff", 0.5, 0.4)
    shard(b.w / 2 + 2, b.h / 2, 18, 6.5, 0)


@fx(32, 32)
def spark(b):
    cx, cy = b.w / 2, b.h / 2
    glow(cx, cy, 9, "#7cc4ff", 0.75)
    for a in (10, 130, 250):
        r = math.radians(a)
        lightning(zig(cx, cy, cx + math.cos(r) * 7.5, cy + math.sin(r) * 7.5, 3, 1.0, a), 0.5)
    sparkle(cx, cy, 6, "#ffffff")


@fx(32, 32)
def rock(b):
    cx, cy = b.w / 2, b.h / 2
    p = [(cx - 7, cy - 3), (cx - 4, cy + 6), (cx + 3, cy + 7), (cx + 8, cy + 1), (cx + 6, cy - 6), (cx - 2, cy - 7)]
    form(p, K("#6a6460", 0.4), W, sdx=-1.4, sdy=1.4, sh=0.3)
    stroke([(cx - 4, cy + 6), (cx, cy), (cx + 6, cy - 6)], 0.5, g=K("#3a3432", 0.2))
    hl([(cx - 5, cy + 2), (cx - 2, cy + 6)], 0.6, 0.5)
    for i in range(3):
        line([(cx - 15, cy - 2 + i * 2.5), (cx - 9, cy - 2 + i * 2.5)], "#c8c0b8", 0.5, 0.35)


@fx(40, 24)
def bone(b):
    with T(b.w / 2, b.h / 2, 1.0, rot=-20):
        tube([(-9, 0), (9, 0)], 3.0, 3.0, BONE, W * 0.8, sh=0.2)
        for sx in (-1, 1):
            for sy in (-1, 1):
                shape(ell(sx * 10, sy * 1.8, 2.3, 2.3, 14), BONE, W * 0.7)


@fx(32, 32)
def coin(b):
    cx, cy = b.w / 2, b.h / 2
    glow(cx, cy, 13, "#ff8020", 0.6)
    flame(cx - 3, cy + 2, 8, lean=-3)
    _coin(cx, cy - 1, 6.5)


def _coin(x, y, r):
    import icons_kit
    icons_kit.coin(x, y, r, GOLD, GOLD_D, 0.9)
    flat(ell(x, y, r, r * 0.9, 24), "#ff6010", 0.25)


@fx(64, 64)
def web(b):
    cx, cy = b.w / 2, b.h / 2
    r = random.Random(5)
    spokes = [math.radians(i * 45 + r.uniform(-8, 8)) for i in range(8)]
    for a in spokes:
        line([(cx, cy), (cx + math.cos(a) * 15, cy + math.sin(a) * 15)], "#e8e8f0", 0.5, 0.8)
    for k in range(1, 5):
        rr = k * 3.4
        pts = []
        for a in spokes + [spokes[0]]:
            pts.append((cx + math.cos(a) * rr * r.uniform(0.9, 1.05), cy + math.sin(a) * rr * r.uniform(0.9, 1.05)))
        line(pts, "#e8e8f0", 0.4, 0.75)


@fx(48, 64)
def morana(b):
    with T(b.w / 2 - 1, b.h / 2, 0.92, rot=-20):
        SI.vynaseni_morany(0, 0)


@fx(48, 64)
def flame_fx(b):
    glow(b.w / 2, 16, 15, "#ff7020", 0.45)
    flame_big(b.w / 2, 4, 26, lean=1, wide=0.4)


@fx(96, 64)
def blood(b):
    cx, cy = b.w / 2, b.h / 2
    r = random.Random(11)
    blob = []
    for i in range(28):
        a = math.radians(i * 360 / 28)
        rr = r.uniform(9, 14) if i % 3 else r.uniform(14, 19)
        blob.append((cx + math.cos(a) * rr * 1.5, cy + math.sin(a) * rr))
    flat(blob, "#3a0608", 0.85)
    flat([(cx + (x - cx) * 0.6, cy + (y - cy) * 0.6) for x, y in blob], "#4e0a0c", 0.8)
    for _ in range(9):
        a = r.uniform(0, 6.28); d = r.uniform(22, 30)
        x, y = cx + math.cos(a) * d * 1.4, cy + math.sin(a) * d * 0.9
        flat(ell(x, y, r.uniform(1, 2.6), r.uniform(0.8, 2), 12), "#3a0608", 0.85)
    flat(ell(cx - 6, cy + 3, 4, 1.5, 12), "#a03030", 0.25)


@fx(32, 32)
def soul(b):
    cx, cy = b.w / 2, b.h / 2
    glow(cx, cy, 14, "#cfe8ff", 0.6)
    tail = bez((cx - 2, cy + 3), (cx - 6, cy + 1), (cx - 8, cy - 4), (cx - 13, cy - 3)) + bez((cx - 13, cy - 3), (cx - 7, cy - 6), (cx - 3, cy - 4), (cx, cy - 3))
    flat(tail, "#e8f4ff", 0.6)
    flat(ell(cx + 1, cy, 4, 4, 20), "#f4faff", 0.95)
    flat(ell(cx + 1.6, cy + 0.6, 2, 2, 12), "#ffffff")


@fx(192, 128)
def zar_ptak(b):
    SI.firebird(b.w / 2 + 6, b.h / 2 - 2, 1.8)
    r = random.Random(2)
    for _ in range(14):
        dot(b.w / 2 - 22 + r.uniform(-12, 12), b.h / 2 - 22 + r.uniform(-14, 14), r.uniform(0.4, 1.0), K("#ffe080", 0.9))


FX = [("flame" if n == "flame_fx" else n, w, h, f) for n, w, h, f in FX]

if __name__ == "__main__":
    common.run({"sprites/fx": FX})
