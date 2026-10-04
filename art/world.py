"""Tile sets: floors, walls and floor decals for the four mines and the four towns (game/assets/tiles/<set>/)."""
import os, sys, math, random, zlib
import numpy as np
from PIL import Image
import common
import world_kit as K
from world_kit import c, rect, blob, chunk, pebble, wrapped, clip, periodic, pband, pline
from lib import ell, bez
import lib
import style3
from style3 import T, stroke, fill, form, shape, hatch, offset_shadow, dot, C

OUT = os.path.join(common.OUT, "tiles")
W = 32.0
INK = 0.5

SETS = {
    "hora": dict(
        floor=c("#776d62"), floor_d=c("#5f564d"), floor_l=c("#93897b"), peb=c("#8e8577"), peb2=c("#6c645a"),
        top=c("#4f4944"), top_d=c("#3c3733"), top_l=c("#655d55"), face=c("#857b6f"), face_d=c("#6a6158"),
        timber=c("#8c6844"), timber_d=c("#5f452c"), accent=c("#c9d3dc"), water=c("#4d6876"), kind="mine"),
    "brdy": dict(
        floor=c("#7a6a55"), floor_d=c("#5f5141"), floor_l=c("#968470"), peb=c("#8f8272"), peb2=c("#6a5c4a"),
        top=c("#4b4436"), top_d=c("#38322a"), top_l=c("#5f5746"), face=c("#887358"), face_d=c("#6b5944"),
        timber=c("#7f5c3a"), timber_d=c("#553c26"), accent=c("#6f8c45"), moss=c("#46602e"), root=c("#6e5236"),
        water=c("#4f5f50"), kind="mine"),
    "jachymov": dict(
        floor=c("#68675f"), floor_d=c("#504f4a"), floor_l=c("#817f76"), peb=c("#7d7b72"), peb2=c("#57564f"),
        top=c("#403f3b"), top_d=c("#302f2c"), top_l=c("#545249"), face=c("#77746b"), face_d=c("#5c5a53"),
        timber=c("#6a5040"), timber_d=c("#3f2f25"), accent=c("#8cf26a"), glow=c("#b6ff7a"), rust=c("#8a4a2a"),
        water=c("#4c5e48"), kind="mine"),
    "nav": dict(
        floor=c("#58556a"), floor_d=c("#46435a"), floor_l=c("#6c6880"), peb=c("#6f6b80"), peb2=c("#4e4b60"),
        top=c("#37344a"), top_d=c("#2a283a"), top_l=c("#48445c"), face=c("#646078"), face_d=c("#504c64"),
        timber=c("#5c5048"), timber_d=c("#3e352f"), accent=c("#d9d1b8"), mist=c("#a3a8d8"), water=c("#3f4a6e"),
        kind="mine"),
    "town_hora": dict(
        path=c("#a08a68"), path_d=c("#86704f"), path_l=c("#b8a382"),
        floor=c("#8b7a5e"), floor_d=c("#715f47"), floor_l=c("#a69376"), peb=c("#a2967f"), peb2=c("#7b6c58"),
        top=c("#4f5e34"), top_d=c("#3d4a28"), top_l=c("#627245"), face=c("#9c8566"), face_d=c("#7e6a50"),
        timber=c("#8a6440"), timber_d=c("#5d4128"), accent=c("#b0bfd0"), water=c("#56708a"), grass=c("#6d7d40"),
        kind="town", masonry="ashlar"),
    "town_pribram": dict(
        path=c("#86704e"), path_d=c("#6b583c"), path_l=c("#9c8664"),
        floor=c("#637244"), floor_d=c("#515e38"), floor_l=c("#768653"), peb=c("#958d7c"), peb2=c("#6c6555"),
        top=c("#3a4a2c"), top_d=c("#2c3922"), top_l=c("#4b5e38"), face=c("#8d877a"), face_d=c("#6e695e"),
        timber=c("#7c5a38"), timber_d=c("#553c26"), accent=c("#e9d6a0"), water=c("#4f6a80"), grass=c("#7d9150"),
        kind="town", masonry="drystone"),
    "town_jachymov": dict(
        path=c("#8d8576"), path_d=c("#6f685b"), path_l=c("#a59d8c"),
        floor=c("#7b776b"), floor_d=c("#615d53"), floor_l=c("#958f80"), peb=c("#8f8a7e"), peb2=c("#625e55"),
        top=c("#55603f"), top_d=c("#424b30"), top_l=c("#69754f"), face=c("#958f86"), face_d=c("#77726a"),
        timber=c("#6f523a"), timber_d=c("#4a3726"), accent=c("#8cf26a"), water=c("#4e6474"), grass=c("#6a7448"),
        kind="town", masonry="granite"),
    "town_nav": dict(
        path=c("#5c5868"), path_d=c("#48455a"), path_l=c("#716d80"),
        floor=c("#67647a"), floor_d=c("#545166"), floor_l=c("#7c788e"), peb=c("#807c90"), peb2=c("#5a5770"),
        top=c("#3e3b50"), top_d=c("#2f2d3f"), top_l=c("#504c64"), face=c("#6e6a84"), face_d=c("#5a566e"),
        timber=c("#5c5048"), timber_d=c("#3e352f"), accent=c("#d9d1b8"), water=c("#3c4669"), grass=c("#6f6d7c"),
        mist=c("#a3a8d8"), kind="town", masonry="navstone"),
}
BONE = c("#d8cfb4"); BONE_D = c("#a99f86"); SILVER = c("#c9d3dc"); RAIL = c("#5b5650"); RUST = c("#8a4a2a")


def seed(*a): return zlib.crc32("/".join(map(str, a)).encode())


# ------------------------------------------------------------------ seamless textures
def _window(n):
    return np.sin(np.pi * (np.arange(n) + 0.5) / n) ** 2


def seamless(im, xs=True, ys=True, target=None, contrast=1.0):
    a = np.asarray(im).astype(np.float32)
    mean = a.reshape(-1, 4).mean(0)
    if target is not None:
        t = np.array([int(target.hex[i:i + 2], 16) for i in (1, 3, 5)] + [255], np.float32)
        a = t + (a - mean) * contrast
        mean = t
    def blend(a, axis):
        n = a.shape[axis]; w = _window(n)
        w = w[None, :, None] if axis == 1 else w[:, None, None]
        b = np.roll(a, n // 2, axis=axis)
        wa, wb = w, 1 - w
        out = mean + (wa * (a - mean) + wb * (b - mean)) / np.sqrt(wa ** 2 + wb ** 2)
        return out
    if xs: a = blend(a, 1)
    if ys: a = blend(a, 0)
    a[..., 3] = 255
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def texture(S, base, dark, light, w_pt, h_pt, key, n=7, alpha_spots=True):
    """crayon base for a w x h pt area (no outlines)"""
    r = random.Random(seed(key))
    def d(b):
        lib.fill(rect(-2, -2, w_pt + 4, h_pt + 4), base)
        fill(rect(-2, -2, w_pt + 4, h_pt + 4), base)
        for i in range(n):
            g = dark if i % 2 else light
            fill(blob(r.uniform(0, w_pt), r.uniform(0, h_pt), r.uniform(3, 6), r.uniform(2, 4.5), r), g)
        if alpha_spots:
            for i in range(n * 2):
                g = K.c("#000000") if i % 3 else K.c("#ffffff")
                fill(blob(r.uniform(0, w_pt), r.uniform(0, h_pt), r.uniform(2, 6), r.uniform(1.5, 4), r), g, 0.06)
    return K.to_image(int(w_pt * 2), int(h_pt * 2), d, seed(key, "t"))


# ------------------------------------------------------------------ floors
def floor_shared(S, name):
    """wrapped fine texture shared by all floor variants of a set"""
    r = random.Random(seed(name, "fs"))
    specks = [(r.uniform(0, W), r.uniform(0, W), r.uniform(0.2, 0.45), r.random()) for _ in range(12)]
    strokes = []
    for _ in range(2):
        x, y = r.uniform(0, W), r.uniform(0, W); a = r.uniform(-0.6, 0.6); L = r.uniform(1.5, 3)
        strokes.append([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L * 0.6)])
    town = S["kind"] == "town"
    def fn():
        for x, y, rr, t in specks:
            dot(x, y, rr, S["floor_d"] if t < 0.6 else S["floor_l"])
        for s in strokes:
            stroke(s, 0.3, g=S["floor_d"], alpha=0.5)
    def d(b): wrapped(fn, W, W, seed(name, "fsw"))
    return K.to_image(64, 64, d, 1)


def floor_detail(S, name, v):
    r = random.Random(seed(name, "fd", v))
    town = S["kind"] == "town"
    M = 3.0
    def inside(rx, ry): return r.uniform(M + rx, W - M - rx), r.uniform(M + ry, W - M - ry)
    def d(b):
        for _ in range(3 + v):
            x, y = inside(5, 4)
            fill(blob(x, y, r.uniform(3, 5.5), r.uniform(2, 4), r), S["floor_d"] if r.random() < 0.6 else S["floor_l"], 0.22)
        if v == 0:
            for _ in range(5):
                x, y = inside(2, 2); s = r.uniform(0.8, 1.6)
                pebble(chunk(x, y, s, s * 0.75, r), S["peb"] if r.random() < 0.6 else S["peb2"])
        elif v == 1:
            x, y = inside(7, 5)
            pebble(chunk(x, y, 6.5, 4.5, r, n=8, k=0.15), S["peb2"] if not town else S["peb"], w=0.45, sh=0.2)
            stroke([(x - 3, y + 0.5), (x + 1, y - 1), (x + 3.5, y + 0.2)], 0.3, g=S["floor_d"])
            for _ in range(3):
                xx, yy = inside(1.5, 1.5); s = r.uniform(0.6, 1.1)
                pebble(chunk(xx, yy, s, s * 0.7, r), S["peb"])
        elif v == 2:
            cx, cy = inside(7, 6)
            for _ in range(14):
                x = cx + r.gauss(0, 3); y = cy + r.gauss(0, 2.4)
                x = min(max(x, M + 1), W - M - 1); y = min(max(y, M + 1), W - M - 1)
                s = r.uniform(0.4, 1.0)
                pebble(chunk(x, y, s, s * 0.8, r, n=5), S["peb"] if r.random() < 0.5 else S["peb2"], w=0.3, ground=0.12)
        else:
            x0, y0 = inside(6, 6)
            pts = [(x0 - 6, y0 + 3)]
            for i in range(5): pts.append((pts[-1][0] + r.uniform(2, 3), pts[-1][1] + r.uniform(-2, 1.4)))
            if town:
                for _ in range(4):
                    xx, yy = inside(2, 2); s = r.uniform(0.7, 1.3)
                    pebble(chunk(xx, yy, s, s * 0.7, r), S["peb"])
            else:
                stroke(pts, 0.55, g=S["top_d"])
                stroke([pts[2], (pts[2][0] + 1.5, pts[2][1] - 3)], 0.35, g=S["top_d"])
                stroke([(p[0] + 0.3, p[1] - 0.4) for p in pts], 0.3, g=S["floor_l"], alpha=0.6)
                for _ in range(2):
                    xx, yy = inside(1.5, 1.5); pebble(chunk(xx, yy, 1.0, 0.8, r), S["peb"])
                if name == "hora":
                    for _ in range(4): xx, yy = inside(1, 1); dot(xx, yy, 0.35, SILVER)
                if name == "jachymov":
                    stroke(pts[1:4], 0.9, g=c("#8cf26a", 0.35)); stroke(pts[1:4], 0.3, g=c("#d8ffb0"))
                if name == "nav":
                    xx, yy = inside(3, 2); bone(xx, yy, 2.4, r.uniform(-30, 30))
                if name == "brdy":
                    xx, yy = inside(5, 3)
                    stroke(bez((xx - 5, yy), (xx - 2, yy + 2), (xx + 2, yy - 2), (xx + 5, yy)), 0.9, g=S["root"])
                    stroke(bez((xx - 5, yy), (xx - 2, yy + 2), (xx + 2, yy - 2), (xx + 5, yy)), 0.25)
        if town and v in (0, 2):
            for _ in range(3):
                x, y = inside(2, 2); tuft(x, y, S["grass"], r, 0.8)
    return K.to_image(64, 64, d, seed(name, "fdi", v))


def tuft(x, y, g, r, s=1.0, n=5):
    for i in range(n):
        a = math.radians(90 + (i - (n - 1) / 2) * 22 + r.uniform(-8, 8))
        L = s * r.uniform(1.8, 3.0)
        stroke([(x + (i - n / 2) * 0.3 * s, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 0.55 * s, g=g)
        stroke([(x + (i - n / 2) * 0.3 * s, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 0.2 * s, alpha=0.6)


def bone(x, y, L, rot, g=None):
    g = g or BONE
    with T(x, y, rot=rot):
        stroke([(-L, 0), (L, 0)], 0.75, g=g, taper=False)
        for s in (-1, 1):
            for dy in (-0.35, 0.35): dot(s * L, dy, 0.45, g)
        stroke([(-L + 0.2, -0.45), (L - 0.2, -0.45)], 0.2, g=BONE_D)


def skull(x, y, s=1.0, rot=0):
    with T(x, y, s, rot=rot):
        cr = bez((-2, 0), (-2.4, 2.2), (-1.2, 3.4), (0, 3.4)) + bez((0, 3.4), (1.2, 3.4), (2.4, 2.2), (2, 0)) + \
             [(1.3, -0.4), (1.2, -1.4), (-1.2, -1.4), (-1.3, -0.4)]
        form(cr, BONE, w=0.4, sh=0.18)
        for sx in (-0.85, 0.85): fill(ell(sx, 1.0, 0.6, 0.65, 10), c("#2a2530"))
        fill([(-0.25, 0.1), (0.25, 0.1), (0, -0.5)], c("#2a2530"))
        for k in (-0.6, 0, 0.6): stroke([(k, -1.4), (k, -0.6)], 0.2)


def floors(name, S):
    base = seamless(texture(S, S["floor"], S["floor_d"], S["floor_l"], W, W, (name, "floor")), target=S["floor"], contrast=0.5 if S["kind"] == "mine" else 0.38)
    base = K.over(base, floor_shared(S, name))
    for v in range(4):
        im = K.over(base, floor_detail(S, name, v))
        im = K.apply_grain(im, seed(name, "grain"), 0.12)
        save(im, name, f"floor_{v}")


# ------------------------------------------------------------------ walls
FACE = 16.0


def wall_shared(S, name):
    r = random.Random(seed(name, "ws"))
    town = S["kind"] == "town"
    lipf = periodic(0, W, W, r, 0.55, (1, 2, 4))
    lip = lambda x: FACE - 0.9 + lipf(x) * 0.9 if not town else FACE - 0.6 + lipf(x) * 0.4
    crags = []
    for _ in range(13 if not town else 0):
        x, y = r.uniform(0, W), r.uniform(FACE, FACE + W)
        crags.append((y, chunk(x, y, r.uniform(3.5, 7), r.uniform(2.5, 4.5), r, n=r.choice((6, 7, 8)), rot=r.uniform(-30, 30)),
                      r.choice((S["top"], S["top_d"]))))
    crags.sort(key=lambda t: -t[0])
    cracks = []
    for _ in range(5):
        x, y = r.uniform(0, W), r.uniform(FACE, FACE + W)
        cracks.append([(x, y), (x + r.uniform(-3, 3), y - r.uniform(1, 3)), (x + r.uniform(-4, 4), y - r.uniform(3, 5))])
    tufts = [(r.uniform(0, W), r.uniform(FACE, FACE + W)) for _ in range(14 if town else 0)]
    stones = [(r.uniform(0, W), r.uniform(FACE, FACE + W), r.uniform(0.8, 1.6)) for _ in range(5 if town else 0)]

    def top_fn():
        for y, pts, g in crags:
            fill([(px + 0.7, py - 0.9) for px, py in pts], c("#000000"), 0.16)
            fill(pts, g); offset_shadow(pts, -0.9, 0.8, 0.14)
            stroke(pts, 0.35, closed=True, alpha=0.45)
        for ck in cracks:
            stroke(ck, 0.4, g=S["top_d"])
        rr = random.Random(5)
        for x, y in tufts: tuft(x, y, S["top_l"], rr, 0.9)
        for x, y, s in stones: pebble(chunk(x, y, s, s * 0.7, rr), S["peb2"], w=0.35)

    strata = [(r.uniform(2, FACE - 4), periodic(0, W, W, r, 0.7, (1, 2))) for _ in range(3 if not town else 0)]

    def face_fn():
        for y0, f in strata:
            pline(-1, W + 1, lambda x, y0=y0, f=f: y0 + f(x), 0.35, rnd=random.Random(int(y0 * 100)), g=S["face_d"])

    def d(b):
        with clip(rect(0, FACE, W, W)):
            wrapped(top_fn, W, W, seed(name, "top"))
        with clip(rect(0, 0, W, FACE)):
            wrapped(face_fn, W, 0, seed(name, "face"), ys=False)
            if S["kind"] == "town":
                masonry(S, name)
            pband(-1, W + 1, lambda x: lip(x) - 1.6, 3.2, c("#000000", 0.22))
            pband(-1, W + 1, lambda x: 0.8, 1.6, c("#000000", 0.3))
            pband(-1, W + 1, lambda x: 0.25, 0.5, c("#000000", 0.35))
            if S["kind"] == "mine" and name != "nav":
                cap_beam(S, lip)
        # overhanging lip of the top mass
        xs = [i * 0.5 for i in range(-2, int(W * 2) + 3)]
        lp = [(x, lip(x)) for x in xs] + [(xs[-1], FACE + 0.01), (xs[0], FACE + 0.01)]
        lib.fill(lp, S["top"] if not town else S["top_d"])
        pline(-1, W + 1, lip, 0.6, rnd=random.Random(3))
    return K.to_image(64, 96, d, seed(name, "wsi"))


def cap_beam(S, lip):
    y0 = lambda x: lip(x) - 2.2
    pband(-1, W + 1, lambda x: 12.6, 3.0, S["timber"])
    pband(-1, W + 1, lambda x: 11.5, 0.8, c("#000000", 0.18))
    pline(-1, W + 1, lambda x: 14.1, 0.45, rnd=random.Random(11))
    pline(-1, W + 1, lambda x: 11.1, 0.45, rnd=random.Random(12))
    pline(-1, W + 1, lambda x: 12.9, 0.22, rnd=random.Random(13), g=S["timber_d"])


def masonry(S, name):
    kind = S["masonry"]
    r = random.Random(seed(name, "mas"))
    if kind in ("ashlar", "granite", "navstone"):
        rows = [(1.0, 5.0), (5.0, 9.6), (9.6, 14.6)] if kind != "ashlar" else [(1.0, 7.6), (7.6, 14.6)]
        for i, (y0, y1) in enumerate(rows):
            n = {"ashlar": 2, "granite": 3, "navstone": 3}[kind]
            off = (i % 2) * (W / n / 2)
            for k in range(n):
                x0 = off + k * W / n
                bl = [(x0 + 0.35, y0 + 0.3), (x0 + W / n - 0.35, y0 + 0.3), (x0 + W / n - 0.35, y1 - 0.3), (x0 + 0.35, y1 - 0.3)]
                g = S["face"] if (k + i) % 3 else S["face_d"]
                for dx in (-W, 0, W):
                    with T(dx, 0):
                        style3._R.seed(seed(name, i, k))
                        form(bl, g, w=0.4, sdx=-0.6, sdy=0.5, sh=0.12)
                        if kind == "granite":
                            rr = random.Random(seed(i, k))
                            for _ in range(5): dot(rr.uniform(x0 + 1, x0 + W / n - 1), rr.uniform(y0 + 1, y1 - 1), 0.25, S["face_d"])
    else:
        rr = random.Random(seed(name, "dry"))
        stones = []
        x = 0.0
        for row, (y0, y1) in enumerate([(1.0, 5.4), (5.0, 10.0), (9.6, 14.8)]):
            x = rr.uniform(0, 3)
            while x < W - 0.5:
                w = rr.uniform(3.5, 6.5); w = min(w, W - x) if W - x < 3 else w
                stones.append((x + w / 2, (y0 + y1) / 2, w / 2, (y1 - y0) / 2, rr.random()))
                x += w
        for dx in (-W, 0, W):
            for i, (cx, cy, rx, ry, t) in enumerate(stones):
                with T(dx, 0):
                    style3._R.seed(seed(name, "st", i))
                    pts = chunk(cx, cy, rx * 0.95, ry * 0.9, random.Random(i), n=8, k=0.1)
                    form(pts, S["face"] if t < 0.6 else S["face_d"], w=0.4, sdx=-0.6, sdy=0.5, sh=0.14)


def wall_detail(S, name, v):
    r = random.Random(seed(name, "wd", v))
    town = S["kind"] == "town"
    def post(x, h=11.0, g=None):
        g = g or S["timber"]
        p = [(x - 1.5, 0.4), (x + 1.5, 0.4), (x + 1.4, h), (x - 1.4, h)]
        fill([(x + 1.5, 0.4), (x + 2.6, 0.4), (x + 2.5, h - 0.4), (x + 1.4, h)], c("#000000"), 0.2)
        form(p, g, w=0.5, sdx=-0.9, sdy=0, sh=0.18)
        stroke([(x - 0.2, 2), (x + 0.1, h - 2)], 0.2, g=S["timber_d"])
        stroke([(x + 0.6, 1.5), (x + 0.5, 5)], 0.2, g=S["timber_d"])
    def d(b):
        M = 2.5
        # top details (inside margins)
        tops = sorted([(r.uniform(FACE + M + 6, FACE + W - M - 5), r.uniform(M + 6, W - M - 6)) for _ in range(2 + v % 2)], reverse=True)
        for y, x in tops:
            if not town:
                pts = chunk(x, y, r.uniform(3.5, 5.5), r.uniform(2.5, 4), r, n=7, rot=r.uniform(-25, 25))
                fill([(px + 0.6, py - 0.8) for px, py in pts], c("#000000"), 0.2)
                form(pts, S["top_l"] if v != 1 else S["top"], w=0.45, sdx=-0.8, sdy=0.7, sh=0.2)
            else:
                tuft(x, y, S["grass"], r, 1.1, 6)
        if name == "brdy":
            for _ in range(2):
                x, y = r.uniform(M + 5, W - M - 5), r.uniform(FACE + M + 3, FACE + W - M - 3)
                fill(blob(x, y, r.uniform(3, 5), r.uniform(2, 3), r), S["moss"])
        if name == "nav" and v != 1:
            x, y = r.uniform(M + 4, W - M - 4), r.uniform(FACE + M + 4, FACE + W - M - 4)
            bone(x, y, 2.6, r.uniform(-40, 40))
        if name == "jachymov":
            x, y = r.uniform(M + 4, W - M - 4), r.uniform(FACE + M + 4, FACE + W - M - 4)
            for k in range(3):
                dot(x + r.uniform(-3, 3), y + r.uniform(-3, 3), 0.9, c("#8cf26a", 0.25))
                dot(x + r.uniform(-3, 3), y + r.uniform(-3, 3), 0.35, c("#c8ff9a"))
        if town and v == 2 and name != "town_nav":
            ivy(S, r)
        # face details
        if S["kind"] == "mine" and name != "nav":
            g = S["timber"] if name != "jachymov" else c("#5a4436")
            if v == 0: post(W / 2)
            elif v == 1:
                for k in range(3):
                    y = 2.5 + k * 3
                    p = [(M + 1, y), (W - M - 1, y + r.uniform(-0.2, 0.2)), (W - M - 1, y + 2.6), (M + 1, y + 2.6)]
                    form(p, S["timber"] if k % 2 else S["timber_d"], w=0.4, sh=0.1)
                post(M + 3.5); post(W - M - 3.5)
            else:
                vein(S, name, r)
            if name == "brdy":
                for k in range(3 if v != 1 else 2):
                    x = r.uniform(M + 3, W - M - 3); L = r.uniform(5, 11)
                    pts = bez((x, FACE - 0.5), (x + r.uniform(-2, 2), FACE - L * 0.4), (x + r.uniform(-3, 3), FACE - L * 0.7),
                              (x + r.uniform(-3, 3), FACE - L))
                    stroke(pts, 1.1, g=S["root"]); stroke(pts, 0.3)
                    stroke([(p[0] + 0.25, p[1]) for p in pts[:10]], 0.25, g=c("#a08060"), alpha=0.7)
            if name == "jachymov" and v != 2:
                x = r.uniform(M + 6, W - M - 6) if v == 1 else r.uniform(M + 3, 10)
                glow_crack(x, r.uniform(3, 7), r)
        elif name == "nav":
            for k in range(2 + v):
                x, y = r.uniform(M + 3, W - M - 3), r.uniform(3, 11)
                bone(x, y, r.uniform(1.6, 2.6), r.uniform(-50, 50))
            if v == 1:
                skull(W / 2 + r.uniform(-4, 4), 5, 1.1)
            if v == 2:
                for k in range(3):
                    x = r.uniform(M + 4, W - M - 4); y = r.uniform(3, 10)
                    dot(x, y, 1.6, c("#a3a8d8", 0.18)); dot(x, y, 0.45, c("#dfe3ff"))
        else:
            if v == 1:
                if name in ("town_hora", "town_jachymov"):
                    gw = [(W / 2 - 3, 5), (W / 2 + 3, 5), (W / 2 + 3, 10), (W / 2 - 3, 10)]
                    form(gw, c("#2c2a30"), w=0.5, sh=0)
                    for k in (-1.5, 0, 1.5): stroke([(W / 2 + k, 5.2), (W / 2 + k, 9.8)], 0.5, g=c("#4d4a52"))
                    stroke([(W / 2 - 3, 7.5), (W / 2 + 3, 7.5)], 0.4, g=c("#4d4a52"))
                else:
                    for k in range(3):
                        x = r.uniform(M + 3, W - M - 3)
                        fill(blob(x, r.uniform(4, 11), 2.5, 1.6, r), S["grass"])
            if v == 2 and name == "town_nav":
                for k in range(3):
                    x = r.uniform(M + 3, W - M - 3); L = r.uniform(4, 9)
                    pts = bez((x, FACE - 0.5), (x + 1, FACE - L * 0.4), (x - 1, FACE - L * 0.7), (x + 0.5, FACE - L))
                    stroke(pts, 0.8, g=c("#cfc9d8")); stroke(pts, 0.25)
        # rubble at the foot
        for _ in range(2 + v % 2):
            x = r.uniform(M + 2, W - M - 2); s = r.uniform(0.8, 1.5)
            pebble(chunk(x, 1.0, s, s * 0.65, r), S["peb2"] if not town else S["peb"], w=0.35, ground=0.2)
    return K.to_image(64, 96, d, seed(name, "wdi", v))


def ivy(S, r):
    x0 = r.uniform(8, 24)
    for k in range(3):
        x = x0 + r.uniform(-4, 4); L = r.uniform(6, 12)
        pts = bez((x, FACE), (x + r.uniform(-2, 2), FACE - L * 0.4), (x + r.uniform(-3, 3), FACE - L * 0.7), (x + r.uniform(-2, 2), FACE - L))
        stroke(pts, 0.35, g=c("#3d4a28"))
        for p in pts[2::3]:
            fill(ell(p[0] + r.uniform(-0.8, 0.8), p[1], 1.1, 0.8, 8), S["grass"])
            stroke(ell(p[0], p[1], 1.1, 0.8, 8), 0.2, closed=True)


def vein(S, name, r):
    x0, x1 = 5, W - 5
    y = r.uniform(5, 9)
    pts = [(x0, y)]
    while pts[-1][0] < x1:
        pts.append((pts[-1][0] + r.uniform(2, 3.5), pts[-1][1] + r.uniform(-1.4, 1.4)))
    if name == "hora":
        stroke(pts, 1.1, g=c("#6f7378")); stroke(pts, 0.35, g=SILVER)
        for p in pts[1:-1]:
            if r.random() < 0.6: dot(p[0] + r.uniform(-0.8, 0.8), p[1] + r.uniform(-0.8, 0.8), 0.3, c("#eef4f8"))
    elif name == "brdy":
        stroke(pts, 1.2, g=c("#a07d4e")); stroke(pts, 0.4, g=c("#d4b27a"))
    else:
        glow_crack(W / 2, y, r)


def glow_crack(x, y, r):
    pts = [(x - 4, y + r.uniform(-1, 1))]
    for _ in range(4): pts.append((pts[-1][0] + r.uniform(1.6, 2.4), pts[-1][1] + r.uniform(-1.5, 1.5)))
    stroke(pts, 2.4, g=c("#8cf26a", 0.22), taper=False)
    stroke(pts, 0.9, g=c("#9cff6a"))
    stroke(pts, 0.35, g=c("#eaffd0"))


def walls(name, S):
    top = seamless(texture(S, S["top"], S["top_d"], S["top_l"], W, W, (name, "wtop")), target=S["top"], contrast=0.7 if S["kind"] == "mine" else 0.4)
    face = seamless(texture(S, S["face"], S["face_d"], S["face_d"], W, FACE, (name, "wface"), n=5), ys=False, target=S["face"], contrast=1.2)
    base = Image.new("RGBA", (64, 96)); base.paste(top, (0, 0)); base.paste(face, (0, 64))
    base = K.over(base, wall_shared(S, name))
    for v in range(3):
        im = K.over(base, wall_detail(S, name, v))
        im = K.apply_grain(im, seed(name, "wgrain"), 0.12)
        save(im, name, f"wall_{v}")


# ------------------------------------------------------------------ decals
def deco(name, S, v):
    r = random.Random(seed(name, "deco", v))
    kind = DECO[name][v]
    def d(b):
        DRAW[kind](S, r)
    return K.to_image(64, 64, d, seed(name, "dimg", v))


def d_crack(S, r):
    pts = [(5, r.uniform(10, 22))]
    while pts[-1][0] < 26:
        pts.append((pts[-1][0] + r.uniform(2.5, 4), min(28, max(4, pts[-1][1] + r.uniform(-3, 3)))))
    stroke([(x + 0.4, y - 0.5) for x, y in pts], 1.0, g=S["floor_l"], alpha=0.5)
    stroke(pts, 0.8, g=S["top_d"])
    for i in (1, 3):
        x, y = pts[i]; stroke([(x, y), (x + r.uniform(-2, 2), y + r.choice((-1, 1)) * r.uniform(3, 5))], 0.45, g=S["top_d"])


def d_rubble(S, r):
    items = []
    for _ in range(9):
        x, y = 16 + r.gauss(0, 5), 16 + r.gauss(0, 4)
        x = min(max(x, 5), 27); y = min(max(y, 5), 27); s = r.uniform(0.9, 2.6)
        items.append((y, x, s))
    for y, x, s in sorted(items, reverse=True):
        pebble(chunk(x, y, s, s * 0.75, r), r.choice((S["peb"], S["peb2"], S["face"])), w=0.4, sh=0.2, ground=0.25)


def d_rails(S, r, rusty=False):
    rail = RUST if rusty else RAIL
    for x in (3.5, 11, 18.5, 26):
        x += r.uniform(-0.4, 0.4)
        sl = [(x - 1.6, 8.5), (x + 1.6, 8.5), (x + 1.6, 23.5), (x - 1.6, 23.5)]
        fill([(px + 0.5, py - 0.6) for px, py in sl], c("#000000"), 0.25)
        form(sl, S["timber"], w=0.4, sdx=-0.7, sdy=0, sh=0.15)
        stroke([(x - 0.3, 9.5), (x - 0.2, 22.5)], 0.2, g=S["timber_d"])
    for y in (11.5, 20.5):
        lib.fill(rect(0, y - 1.4, W, 0.6), c("#000000"))
        lib.fill(rect(0, y - 0.8, W, 1.6), rail)
        lib.fill(rect(0, y + 0.2, W, 0.5), c("#9a958c") if not rusty else c("#b0704a"))
        lib.fill(rect(0, y - 0.95, W, 0.25), c("#2e2d33"))
        lib.fill(rect(0, y + 0.75, W, 0.2), c("#2e2d33"))
        for x in (3.5, 11, 18.5, 26): dot(x, y, 0.35, c("#2e2d33"))


def d_rails_rust(S, r): d_rails(S, r, True)


def d_puddle(S, r, col=None):
    col = col or S["water"]
    pts = blob(16, 16, r.uniform(9, 11), r.uniform(6, 8), r, n=10, k=0.18)
    fill(blob(16, 16, 12, 9, r, n=10, k=0.12), c("#000000"), 0.12)
    fill(pts, c("#1c2230"), 0.45)
    fill(pts, col, 0.35)
    stroke(pts, 0.3, closed=True, alpha=0.35)
    with clip(pts):
        stroke([(8, 18.5), (15, 19.6)], 0.5, g=c("#c8d4e8"), alpha=0.45)
        stroke([(17, 13), (22, 12.4)], 0.35, g=c("#c8d4e8"), alpha=0.3)
        stroke([(11, 15.5), (13.5, 15.8)], 0.3, g=c("#c8d4e8"), alpha=0.3)
    for k in range(3):
        a = r.uniform(0, math.tau)
        pebble(chunk(16 + math.cos(a) * 10, 16 + math.sin(a) * 7, 1.0, 0.7, r), S["peb2"])


def d_puddle_green(S, r): d_puddle(S, r, c("#4e6a45"))


def d_roots(S, r):
    for k in range(3):
        y0 = r.uniform(8, 24)
        pts = bez((4, y0), (r.uniform(10, 14), y0 + r.uniform(-6, 6)), (r.uniform(18, 22), y0 + r.uniform(-6, 6)), (28, y0 + r.uniform(-5, 5)))
        stroke([(x + 0.5, y - 0.6) for x, y in pts], 1.6, g=c("#000000"), alpha=0.2)
        stroke(pts, 1.5 - k * 0.3, g=S["root"])
        stroke(pts, 0.35)
        stroke([(x - 0.2, y + 0.3) for x, y in pts[3:12]], 0.25, g=c("#a08060"))
        i = r.randrange(4, 12); x, y = pts[i]
        stroke([(x, y), (x + r.uniform(-3, 3), y + r.uniform(-4, 4))], 0.6, g=S["root"])


def d_moss(S, r):
    for k in range(4):
        x, y = r.uniform(9, 23), r.uniform(9, 23)
        pts = blob(x, y, r.uniform(3, 5.5), r.uniform(2.5, 4), r)
        shape(pts, S["moss"] if k % 2 else c("#6d8a46"), w=0.35)
        for _ in range(5): dot(x + r.uniform(-2.5, 2.5), y + r.uniform(-2, 2), 0.35, c("#8fae5a"))


def d_mushrooms(S, r):
    for k in range(5):
        x, y = r.uniform(7, 25), r.uniform(7, 24); s = r.uniform(0.7, 1.2)
        mushroom(x, y, s, c("#c7a46a") if k % 2 else c("#a8805a"))


def mushroom(x, y, s, cap):
    with T(x, y, s):
        fill(ell(0.4, -0.3, 2.0, 0.6, 12), c("#000000"), 0.25)
        shape([(-0.5, 0), (0.5, 0), (0.4, 2.2), (-0.4, 2.2)], c("#e8dcc0"), w=0.3)
        shape(bez((-2, 2), (-1.8, 4), (1.8, 4), (2, 2)) + [(-2, 2)], cap, w=0.35)
        dot(-0.6, 3.1, 0.3, c("#f0e6cc"))


def d_needles(S, r):
    d_rubble(S, r)
    for _ in range(3):
        x, y = r.uniform(6, 26), r.uniform(6, 26)
        cone(x, y, r.uniform(-40, 40))


def cone(x, y, rot):
    with T(x, y, rot=rot):
        form(ell(0, 0, 2.4, 1.2, 14), c("#7a5233"), w=0.35, sh=0.2)
        for k in (-1.2, 0, 1.2): stroke([(k - 0.4, -0.9), (k + 0.4, 0.9)], 0.2)


def d_glow(S, r):
    for k in range(2):
        pts = [(r.uniform(5, 9), r.uniform(8, 24))]
        while pts[-1][0] < 26:
            pts.append((pts[-1][0] + r.uniform(2, 4), min(27, max(5, pts[-1][1] + r.uniform(-3, 3)))))
        stroke(pts, 3.2, g=c("#8cf26a", 0.16), taper=False)
        stroke(pts, 1.2, g=c("#7fe85a"))
        stroke(pts, 0.4, g=c("#eaffd0"))


def d_pitch(S, r):
    d_rubble(S, r)
    for _ in range(3):
        x, y = r.uniform(9, 23), r.uniform(9, 23); s = r.uniform(1.2, 2)
        dot(x, y, s * 1.7, c("#8cf26a", 0.18))
        pebble(chunk(x, y, s, s * 0.8, r), c("#3a4a34"), w=0.4)
        dot(x - 0.3, y + 0.3, 0.4, c("#b6ff7a"))


def d_chain(S, r):
    x, y = 5, r.uniform(12, 20)
    for k in range(9):
        a = r.uniform(-0.3, 0.3)
        nx, ny = x + 2.6 * math.cos(a), y + 2.6 * math.sin(a)
        e = ell((x + nx) / 2, (y + ny) / 2, 1.8, 0.9 if k % 2 else 0.45, 12, rot=math.degrees(a))
        stroke(e, 0.7, closed=True, g=c("#4a4440")); stroke(e, 0.25, closed=True, g=RUST)
        x, y = nx, ny


def d_bones(S, r):
    for _ in range(5):
        bone(r.uniform(7, 25), r.uniform(7, 25), r.uniform(1.6, 3), r.uniform(0, 180))


def d_skull(S, r):
    for _ in range(3):
        bone(r.uniform(7, 25), r.uniform(6, 14), r.uniform(1.6, 3), r.uniform(0, 180))
    skull(16, 17, 1.4, r.uniform(-15, 15))


def d_mist(S, r):
    for k in range(7):
        x, y = 16 + r.gauss(0, 4), 16 + r.gauss(0, 3)
        fill(blob(min(max(x, 10), 22), min(max(y, 10), 22), r.uniform(4, 7), r.uniform(2.5, 4), r), c("#a3a8d8", 0.13))
    for k in range(3):
        x, y = r.uniform(9, 23), r.uniform(10, 22)
        stroke(bez((x - 4, y), (x - 1, y + 1), (x + 1, y - 1), (x + 4, y)), 0.35, g=c("#c8ccf0"), alpha=0.5)


def d_candles(S, r):
    for k in range(3):
        x, y = 9 + k * 6 + r.uniform(-1, 1), r.uniform(12, 18)
        h = r.uniform(2, 4)
        dot(x, y + h + 1, 2.4, c("#ffb85c", 0.15))
        fill(ell(x + 0.4, y - 0.2, 1.5, 0.5, 10), c("#000000"), 0.25)
        shape([(x - 0.7, y), (x + 0.7, y), (x + 0.7, y + h), (x - 0.7, y + h)], c("#e8e0c8"), w=0.3)
        shape(bez((x, y + h + 0.1), (x - 0.6, y + h + 0.8), (x, y + h + 1.8), (x + 0.1, y + h + 2.3)) +
              bez((x + 0.1, y + h + 2.3), (x + 0.6, y + h + 1.4), (x + 0.5, y + h + 0.5), (x, y + h + 0.1)), c("#ffcf6a"), w=0.2)


def d_cobbles(S, r):
    for i in range(5):
        for j in range(5):
            x = 6 + i * 5 + (j % 2) * 2.5 + r.uniform(-0.4, 0.4); y = 6 + j * 4.6 + r.uniform(-0.3, 0.3)
            if math.hypot(x - 16, (y - 16) * 1.2) > 12 + r.uniform(-2, 1) or x > 27: continue
            pts = chunk(x, y, 2.2, 1.8, r, n=7, k=0.1)
            pebble(pts, S["peb"] if r.random() < 0.7 else S["peb2"], w=0.35, sh=0.18, ground=0.2)


def d_grass(S, r):
    for _ in range(6):
        tuft(r.uniform(7, 25), r.uniform(6, 24), S["grass"], r, r.uniform(1, 1.6), 6)


def d_flowers(S, r):
    d_grass(S, r)
    for _ in range(6):
        x, y = r.uniform(7, 25), r.uniform(7, 25)
        col = r.choice((c("#e9d6a0"), c("#c86a8a"), c("#8a9ad8")))
        for a in range(0, 360, 72):
            dot(x + math.cos(math.radians(a)) * 0.6, y + math.sin(math.radians(a)) * 0.6, 0.45, col)
        dot(x, y, 0.3, c("#e8c040"))


def d_steps(S, r):
    for k in range(3):
        x, y = 9 + k * 7 + r.uniform(-1, 1), 10 + k * 5 + r.uniform(-1, 1)
        pebble(chunk(x, y, 3.2, 2.4, r, n=8, k=0.1), S["peb"], w=0.45, sh=0.18, ground=0.25)


def d_leaves(S, r):
    for _ in range(9):
        x, y = r.uniform(6, 26), r.uniform(6, 26)
        with T(x, y, rot=r.uniform(0, 360)):
            pts = bez((0, -1.6), (1, -1), (1, 0.6), (0, 1.6)) + bez((0, 1.6), (-1, 0.6), (-1, -1), (0, -1.6))
            shape(pts, r.choice((c("#b5772f"), c("#8a5a2a"), c("#a0903a"))), w=0.25)
    for _ in range(5):
        x, y = r.uniform(6, 26), r.uniform(6, 26); a = r.uniform(0, math.pi)
        stroke([(x, y), (x + math.cos(a) * 3, y + math.sin(a) * 3)], 0.35, g=c("#d4b46a"))


def d_slag(S, r):
    for _ in range(7):
        x, y = 16 + r.gauss(0, 5), 16 + r.gauss(0, 4); s = r.uniform(0.8, 2)
        pebble(chunk(min(max(x, 5), 27), min(max(y, 5), 27), s, s * 0.8, r), r.choice((c("#3a3936"), c("#4a4038"), c("#56524a"))), w=0.35)


def d_weeds(S, r):
    for _ in range(4):
        x, y = r.uniform(8, 24), r.uniform(8, 22)
        for k in range(4):
            a = math.radians(r.uniform(50, 130)); L = r.uniform(3, 5)
            stroke([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], 0.5, g=c("#5c6a3c"))
            fill(ell(x + math.cos(a) * L, y + math.sin(a) * L, 0.9, 0.5, 8, rot=math.degrees(a)), c("#6d7d46"))


def d_reeds(S, r):
    for _ in range(9):
        x, y = r.uniform(7, 25), r.uniform(6, 20); L = r.uniform(4, 8); lean = r.uniform(-1.5, 1.5)
        stroke(bez((x, y), (x, y + L * 0.4), (x + lean, y + L * 0.7), (x + lean * 1.4, y + L)), 0.5, g=c("#8a8270"))
        if r.random() < 0.4: shape(ell(x + lean * 1.2, y + L * 0.85, 0.5, 1.3, 8), c("#4a3a30"), w=0.2)


DECO = {
    "hora": ["crack", "rubble", "rails", "puddle"],
    "brdy": ["roots", "moss", "needles", "mushrooms"],
    "jachymov": ["glow", "pitch", "rails_rust", "chain"],
    "nav": ["bones", "mist", "skull", "candles"],
    "town_hora": ["cobbles", "grass", "puddle", "leaves"],
    "town_pribram": ["grass", "flowers", "steps", "mushrooms"],
    "town_jachymov": ["cobbles", "slag", "puddle_green", "weeds"],
    "town_nav": ["bones", "reeds", "puddle", "candles"],
}
DRAW = {k[2:]: v for k, v in globals().items() if k.startswith("d_")}


# ------------------------------------------------------------------ town paths: trodden earth, soft edges so a chain of
# them reads as a footpath over the grass, not as squares
def path_decal(name, S, v):
    """128 px, drawn centred on its 64 px cell so neighbours overlap into one path"""
    r = random.Random(seed(name, "path", v))
    def d(b):
        for k in range(6):
            fill(blob(32, 32, 30 - k * 2.6, 29 - k * 2.6, r, n=16, k=0.12), S["path"], 0.22)
        for i in range(9):
            fill(blob(r.uniform(16, 48), r.uniform(16, 48), r.uniform(2.5, 5), r.uniform(1.8, 3.5), r), S["path_d"] if i % 2 else S["path_l"], 0.3)
        for _ in range(r.randint(3, 6)):
            x, y = r.uniform(18, 46), r.uniform(18, 46)
            pebble(chunk(x, y, r.uniform(0.9, 1.6), r.uniform(0.7, 1.2), r, n=6), S["peb"] if r.random() < 0.6 else S["peb2"], sh=0.15, ground=0.15)
        for _ in range(3):
            x, y = r.uniform(18, 46), r.uniform(18, 46)
            stroke([(x, y), (x + r.uniform(1.5, 3), y + r.uniform(-0.4, 0.4))], 0.3, g=S["path_d"], alpha=0.6)
    return K.to_image(128, 128, d, seed(name, "pimg", v))


def save(im, folder, name):
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    p = os.path.join(OUT, folder, name + ".png"); im.save(p)
    print("wrote", os.path.relpath(p, common.HERE))


def build(name):
    S = SETS[name]
    floors(name, S)
    walls(name, S)
    for v in range(4):
        save(deco(name, S, v), name, f"floor_deco_{v}")
    if S["kind"] == "town":
        for v in range(3):
            save(path_decal(name, S, v), name, f"path_{v}")


if __name__ == "__main__":
    only = [a for a in sys.argv[1:] if a in SETS]
    for n in (only or SETS):
        build(n)
