"""Kostěj Nesmrtelný and Permoník's true form (permonik_obr)."""
import math
import lib
from bosses_kit import *
from bestiary_kit import view_of, ALL

ROBE = col("#7a3040"); ROBE_DK = col("#58222e"); ERMINE = col("#d8d4c8")
GAUNT = col("#b3ae9c"); GAUNT_DK = col("#7f7a6a"); BEARD = col("#c2c0b8")
ARMOR = col("#5f6670"); CAPE = col("#4f4060"); GEM = col("#5fd07a")


# ------------------------------------------------------------------ Kostěj Nesmrtelný
def bony_hand(p, ang, s=1.0, grip=False):
    shape(ell(p[0], p[1], 3.4 * s, 2.8 * s, 12, rot=ang), GAUNT, LINE * 0.8)
    for i in range(4):
        a = ang + (i - 1.5) * 14
        j = pt(p, a, 4.5 * s); e = pt(j, a + (-80 if grip else -20), 4 * s)
        tube([p, j, e], 1.6 * s, 1.0 * s, GAUNT, LINE * 0.6, sh=0)


def sword(H, ang, below=10, above=60):
    base = pt(H, ang + 180, below); tip = pt(H, ang, above)
    g0 = pt(H, ang, 4)
    blade_l = pt(g0, ang + 90, 2.2); blade_r = pt(g0, ang - 90, 2.2)
    shape([blade_l, pt(tip, ang + 180, 6), tip, pt(tip, ang + 180, 6), blade_r], IRON_LT, LINE * 0.8)
    shape([blade_l, pt(tip, ang + 180, 6), tip, pt(g0, ang, 2)], col("#c9ced6"), 0)
    stroke([pt(g0, ang, 3), pt(tip, ang + 180, 10)], LINE * 0.5)
    stroke([blade_l, pt(tip, ang + 180, 6), tip, pt(tip, ang + 180, 6), blade_r], LINE * 0.8)
    tube([base, g0], 2.6, 2.6, WOOD_DK, LINE * 0.7, sh=0)
    tube([pt(g0, ang + 90, 8), pt(g0, ang - 90, 8)], 2.6, 2.6, RUST, LINE * 0.7, sh=0)
    shape(ell(*base, 2.6, 2.6, 12), RUST, LINE * 0.7)
    glow(*pt(H, ang, 30), 14, "#9fffb0", 0.18, 6)


# walk: far foot, near foot, far elbow, far hand, sword elbow, sword hand, sword angle, cape lag, hem sway
KOS_WALK = {
    "walk": ((-8, 10), (22, 8), (-14, 96), (-6, 76), (20, 98), (26, 80), 70, -4, 3),
    "walk2": ((6, 17), (8, 8), (-18, 96), (-15, 75), (24, 97), (31, 81), 64, 2, 0),
    "walk3": ((18, 8), (-6, 10), (-22, 96), (-25, 74), (26, 98), (36, 84), 58, -3, 1),
    "walk4": ((5, 8), (10, 17), (-18, 96), (-15, 75), (24, 97), (31, 81), 64, 3, -1),
}


def kostej(pose):
    pose, view = view_of(pose)
    if view:
        return kostej_fb(pose, view == "b")
    lean = {"idle": 0, "walk": 4, "walk2": 3, "walk3": 4, "walk4": 3, "windup": -3, "attack": 6}[pose]
    wk = KOS_WALK.get(pose)
    cw, rh = (wk[7], wk[8]) if wk else (0, 0)
    shadow(0, 34)
    cape = [(-14 + lean, 132)] + bez((-14 + lean, 132), (-34 + cw * 0.4, 110), (-44 + cw, 60), (-52 - lean + cw * 1.6, 10)) + \
        ragged((-52 - lean + cw * 1.6, 10), (4 + cw * 0.6, 9), 7, 7, 2.2) + bez((4 + cw * 0.6, 9), (2, 50), (6, 100), (14 + lean, 130))
    form(cape, CAPE, sdx=-4, sdy=1, sh=0.2)
    hatch(cape, 2.0, 70, 0.5, g=col("#3a2f48"), alpha=0.5)
    for x0 in (-24, -38):
        stroke(bez((x0 + 12, 120), (x0 + 2, 90), (x0 - 4 + cw * 0.6, 50), (x0 - 8 + cw * 1.2, 14)), LINE * 0.6, g=col("#3a2f48"))
    if wk:
        fs, ns = wk[0], wk[1]
    elif pose in ("attack", "windup"):
        fs = (-10, 10); ns = (24, 8)
    else:
        fs = (-4, 8); ns = (12, 8)
    for (fx, fy), c_ in ((fs, IRON), (ns, ARMOR)):
        b = [(fx - 6, fy + 10), (fx + 4, fy + 10), (fx + 6, fy + 3), (fx + 16, fy - 1), (fx + 16, fy - 6), (fx - 6, fy - 6)]
        form(b, c_, sh=0.15)
        stroke([(fx - 5, fy + 4), (fx + 5, fy + 4)], LINE * 0.5)
    fsh = (-10 + lean, 120)
    if pose == "attack":
        fe = (2 + lean, 104); fh = (20 + lean, 112)
        glow(fh[0] + 6, fh[1] + 2, 12, "#7dffa0", 0.45)
        for k in range(5):
            stroke(bez(pt(fh, 10 + k * 25, 4), pt(fh, 20 + k * 25, 9), pt(fh, 0 + k * 25, 13), pt(fh, 12 + k * 25, 16)), LINE * 0.6, g=GEM, alpha=0.8)
    elif pose == "windup":
        fe = (-6 + lean, 98); fh = (6 + lean, 108)
        glow(fh[0] + 3, fh[1], 7, "#7dffa0", 0.3)
    elif wk:
        fe = (wk[2][0] + lean, wk[2][1]); fh = (wk[3][0] + lean, wk[3][1])
    else:
        fe = (-20 + lean, 96); fh = (-20 + lean, 74)
    tube([fsh, fe], 7, 6, ROBE_DK); tube([fe, fh], 6, 5, ROBE_DK)
    bony_hand(fh, math.degrees(math.atan2(fh[1] - fe[1], fh[0] - fe[0])), 1.1)
    with T(lean, 0):
        robe = [(-14, 128)] + bez((-14, 128), (-18, 90), (-22, 50), (-26 + rh * 0.5, 14)) + \
            ragged((-26 + rh * 0.5, 14), (24 + rh, 13), 6, 4, 0.7) + bez((24 + rh, 13), (20, 50), (18, 90), (16, 128))
        form(robe, ROBE, sdx=-4, sdy=1, sh=0.2)
        for x0 in (-14, -4, 8):
            stroke(bez((x0 * 0.6, 100), (x0 * 0.8, 70), (x0, 40), (x0 * 1.2, 16)), LINE * 0.6, g=ROBE_DK)
        hatch(ell(-18, 60, 10, 50, 20), 1.8, 60, 0.45, g=ROBE_DK, alpha=0.7)
        plate = bez((-14, 128), (-16, 110), (-12, 92), (0, 86)) + bez((0, 86), (12, 88), (18, 104), (16, 128))
        form(plate, ARMOR, sdx=-3, sdy=0, sh=0.2)
        for yy in (120, 112, 104, 96):
            stroke(bez((-13, yy), (-4, yy - 3), (8, yy - 3), (16, yy + 1)), LINE * 0.6)
        for (x, y) in ((-8, 116), (8, 116), (-6, 100), (10, 100)):
            dot(x, y, 0.9, RUST_DK)
        hatch(ell(-14, 108, 6, 22, 16), 1.5, 50, 0.4, alpha=0.6)
        belt = [(-20, 88), (18, 88), (18, 82), (-20, 82)]
        form(belt, WOOD_DK, sh=0.15)
        shape(ell(0, 85, 4, 4, 14), GOLD_DK, LINE * 0.7)
        dot(0, 85, 1.6, GEM)
        fur = [(-20, 126)] + [(x, 134 + (3 if i % 2 else -1)) for i, x in enumerate(range(-18, 24, 5))] + [(22, 126), (14, 122), (0, 124), (-12, 122)]
        form(fur, ERMINE, sh=0.15)
        for x in (-12, -2, 9, 17):
            dot(x, 129, 0.9, col("#3a3640"))
        hx, hy = 6, 146
        collar = [(-16, 126), (-26, 150), (-20, 148), (-18, 162), (-10, 150), (-6, 158), (-2, 140), (10, 128)]
        form(collar, CAPE, sdx=-2, sdy=0, sh=0.2)
        stroke([(-14, 130), (-18, 156)], LINE * 0.5, g=col("#3a2f48"))
        tube([(2, 128), (6, 138)], 6, 5, GAUNT, sh=0.2)
        beard = [(hx - 4, hy - 8), (hx + 10, hy - 10)] + bez((hx + 10, hy - 10), (hx + 10, hy - 24), (hx + 6, hy - 36), (hx + 3, hy - 50)) + \
            bez((hx + 3, hy - 50), (hx, hy - 36), (hx - 4, hy - 22), (hx - 4, hy - 8))
        form(beard, BEARD, sdx=-2, sdy=0, sh=0.15)
        for k in range(4):
            stroke(bez((hx + k * 3 - 2, hy - 10), (hx + k * 2.5 - 1, hy - 22), (hx + k * 1.5 + 1, hy - 34), (hx + 3, hy - 48 + k * 3)), LINE * 0.45, g=GAUNT_DK)
        head = bez((hx - 8, hy + 2), (hx - 9, hy + 12), (hx - 4, hy + 16), (hx + 4, hy + 15)) + \
            bez((hx + 4, hy + 15), (hx + 11, hy + 13), (hx + 12, hy + 7), (hx + 12, hy + 3)) + \
            [(hx + 16, hy - 3), (hx + 12, hy - 4), (hx + 10, hy - 8), (hx + 11, hy - 12)] + \
            bez((hx + 11, hy - 12), (hx + 8, hy - 15), (hx + 3, hy - 14), (hx, hy - 10)) + \
            bez((hx, hy - 10), (hx - 5, hy - 8), (hx - 8, hy - 4), (hx - 8, hy + 2))
        form(head, GAUNT, sdx=-2.5, sdy=0, sh=0.22)
        hatch(ell(hx + 4, hy - 4, 4.5, 3.5, 14), 0.9, 60, 0.4, alpha=0.75)
        hatch(ell(hx - 5, hy + 3, 3, 7, 14), 1.0, 60, 0.4, alpha=0.6)
        stroke(bez((hx - 1, hy + 1), (hx + 3, hy - 1), (hx + 7, hy - 1), (hx + 11, hy + 1)), LINE * 0.6)
        teeth = [(hx + 4, hy - 7.5), (hx + 11, hy - 6.5), (hx + 10.5, hy - 10), (hx + 4.5, hy - 10.5)]
        shape(teeth, BONE, LINE * 0.6)
        for i in range(4):
            stroke([(hx + 5.5 + i * 1.5, hy - 7.3), (hx + 5.6 + i * 1.5, hy - 10.4)], LINE * 0.35)
        stroke([(hx + 4.2, hy - 9), (hx + 10.8, hy - 8.3)], LINE * 0.35)
        for ex, r_ in ((hx + 8, 1.5), (hx + 1.5, 1.1)):
            shape(ell(ex, hy + 5, r_ * 2.4, r_ * 2.1, 14), HOLLOW, LINE * 0.5)
            eye(ex, hy + 5, r_, EYE_GREEN, halo=3.6)
        stroke(bez((hx - 1, hy + 9.5), (hx + 3, hy + 8), (hx + 7, hy + 9), (hx + 11.5, hy + 7)), LINE * 0.9)
        band = [(hx - 10, hy + 12), (hx + 13, hy + 13), (hx + 13, hy + 18), (hx - 10, hy + 17)]
        spikes = []
        for i in range(7):
            x = hx + 12 - i * 3.6
            hgt = 34 if i == 3 else 26 if i in (2, 4) else 20
            spikes.append([(x - 2.0, hy + 17), (x - 0.2, hy + hgt), (x + 1.8, hy + 17)])
        for sp in spikes:
            form(sp, IRON, sh=0.15)
            dot(sp[1][0], sp[1][1] - 0.6, 0.6, GOLD)
        form(band, IRON, sdx=-2, sdy=0, sh=0.2)
        for x in (hx - 6, hx + 8):
            dot(x, hy + 15, 0.9, GOLD)
        shape(ell(hx + 1, hy + 15, 1.9, 1.9, 12), GEM, LINE * 0.6)
        glow(hx + 1, hy + 15, 6, "#7dffa0", 0.4, 5)
        for (cx, sx) in ((-14, -1), (16, 1)):
            pd = ell(cx, 124, 10, 7, 20, a0=-20, a1=200) if sx > 0 else ell(cx, 124, 9, 6, 20, a0=-20, a1=200)
            form(pd, ARMOR if sx > 0 else IRON, sh=0.2)
            for k in range(3):
                b0 = (cx - 6 + k * 6, 128 + (2 if k == 1 else 0))
                shape([(b0[0] - 1.6, b0[1]), (b0[0], b0[1] + 7 + (3 if k == 1 else 0)), (b0[0] + 1.6, b0[1])], IRON_LT, LINE * 0.5)
            stroke(ell(cx, 124, 7, 4.5, 14, 10, 170), LINE * 0.5)
    sh0 = (14 + lean, 120)
    if pose == "attack":
        el = (4 + lean, 140); H = (-8 + lean, 156); sa = 25
    elif wk:
        el = (wk[4][0] + lean, wk[4][1]); H = (wk[5][0] + lean, wk[5][1]); sa = wk[6]
    elif pose == "windup":
        el = (2 + lean, 132); H = (-10 + lean, 142); sa = 150
    else:
        el = (24, 96); H = (32, 78); sa = -88
    tube([sh0, el], 8, 7, ROBE); tube([el, H], 7, 5.5, ROBE)
    if pose == "attack":
        sword(H, sa, 10, 64)
    elif wk or pose == "windup":
        sword(H, sa, 10, 60)
    else:
        sword(H, sa, 10, 66)
    bony_hand(H, sa, 1.2, grip=True)
    if pose == "attack":
        motion([bez((-10, 168), (24, 182), (56, 170), (72, 140)), bez((-2, 160), (26, 170), (50, 162), (64, 140))])


# front/back: feet (-x, +x) as (x, lift, scale); his right (sword) side is -x in the front view
KOS_FEET = {
    "stand": ((-10, 0, 1.0), (10, 0, 1.0)),
    "c1": ((-10, -2, 1.08), (10, 3, 0.9)),
    "p1": ((-9, 0, 1.0), (11, 9, 0.96)),
    "c2": ((-10, 3, 0.9), (10, -2, 1.08)),
    "p2": ((-11, 9, 0.96), (9, 0, 1.0)),
    "brace": ((-14, 0, 1.0), (14, 0, 1.0)),
}
# feet, body sway, sword-arm swing (+ = toward the camera)
KOS_FB = {"idle": ("stand", 0, 0), "walk": ("c1", 0, -1), "walk2": ("p1", -2, 0), "walk3": ("c2", 0, 1),
          "walk4": ("p2", 2, 0), "windup": ("brace", 0, 0), "attack": ("brace", 0, 0)}


def fb_feet(table, back):
    out = []
    for x, lift, sc in table:
        if back and lift < 5:
            lift, sc = -lift, 2 - sc
        out.append((x, lift, sc))
    return sorted(out, key=lambda f: f[2])


def kos_boot(x, lift, sc, back):
    with T(x, 8 + lift, sc):
        b = [(-6, 9)] + bez((-6, 9), (-7, 2), (-7.5, -3), (-6, -6)) + [(6, -6)] + bez((6, -6), (7.5, -3), (7, 2), (6, 9))
        form(b, ARMOR, sh=0.15)
        if back:
            stroke(bez((-5, 1), (-2, -1), (2, -1), (5, 1)), LINE * 0.5)
        else:
            shape(ell(0, -3, 7, 3.6, 16), IRON, LINE * 0.8)
            stroke([(-5.5, 3), (5.5, 3)], LINE * 0.5)


def kos_arm(s, f, pose, back):
    sh0 = (s * 20, 122)
    if s < 0 and pose == "windup":
        el, H, sa = (s * 30, 140), (s * 17, 162), 90 - s * 30
    elif s < 0 and pose == "attack":
        el, H, sa = (s * 12, 112), (5, 100), -90 - s * 48
    elif s > 0 and pose == "windup":
        el, H = (16, 100), (5, 107)
    elif s > 0 and pose == "attack":
        el, H = (30, 104), (24, 108)
    else:
        el = (s * 25, 99 + f * 2); H = (s * (27 - f * 2), 77 - f * 5)
        sa = -90 + s * (8 if pose == "idle" else 22 - f * 6)
    tube([sh0, el], 8, 7, ROBE if s < 0 else ROBE_DK); tube([el, H], 7, 5.5, ROBE if s < 0 else ROBE_DK)
    if s < 0:
        if not (back and pose == "windup"):
            sword(H, sa, 10, 52 if pose == "attack" else 62)
        bony_hand(H, sa, 1.2 + f * 0.08, grip=True)
        return
    if pose == "attack":
        glow(H[0], H[1] + 2, 13, "#7dffa0", 0.45)
        for k in range(5):
            stroke(bez(pt(H, 10 + k * 40, 4), pt(H, 20 + k * 40, 9), pt(H, k * 40, 13), pt(H, 12 + k * 40, 16)), LINE * 0.6, g=GEM, alpha=0.8)
    elif pose == "windup":
        glow(H[0], H[1], 7, "#7dffa0", 0.3)
    bony_hand(H, math.degrees(math.atan2(H[1] - el[1], H[0] - el[0])), 1.1 + f * 0.08)


def kos_head_fb(back):
    hy = 146
    head = bez((-11, hy + 3), (-12, hy + 17), (12, hy + 17), (11, hy + 3)) + \
        bez((11, hy + 3), (11, hy - 4), (8, hy - 10), (3, hy - 12)) + \
        bez((3, hy - 12), (1, hy - 13), (-1, hy - 13), (-3, hy - 12)) + \
        bez((-3, hy - 12), (-8, hy - 10), (-11, hy - 4), (-11, hy + 3))
    if not back:
        beard = [(-8, hy - 6), (8, hy - 6)] + bez((8, hy - 6), (9, hy - 22), (5, hy - 36), (0, hy - 50)) + \
            bez((0, hy - 50), (-5, hy - 36), (-9, hy - 22), (-8, hy - 6))
        form(beard, BEARD, sdx=0, sdy=-1, sh=0.15)
        for k in (-2, -1, 0, 1, 2):
            stroke(bez((k * 3, hy - 9), (k * 3.2, hy - 22), (k * 2, hy - 34), (k * 0.6, hy - 47)), LINE * 0.45, g=GAUNT_DK)
    form(head, GAUNT, sdx=0, sdy=-1.5, sh=0.22)
    if back:
        hatch(ell(0, hy, 9, 12, 16), 1.2, 60, 0.4, alpha=0.6)
        stroke(bez((0, hy + 16), (1, hy + 8), (-1, hy), (0, hy - 8)), LINE * 0.45, g=GAUNT_DK)
        for y in (hy - 9, hy - 12):
            stroke([(-3, y), (3, y)], LINE * 0.45, g=GAUNT_DK)
    else:
        for sx in (-1, 1):
            hatch(ell(sx * 7.5, hy - 3, 3, 5.5, 14), 1.0, 60, 0.4, alpha=0.6)
            stroke(bez((sx * 10, hy - 1), (sx * 8, hy - 3), (sx * 6, hy - 3), (sx * 4, hy - 2)), LINE * 0.45)
        stroke(bez((-10, hy + 9), (-4, hy + 7.5), (4, hy + 7.5), (10, hy + 9)), LINE * 0.9)
        for sx in (-1, 1):
            shape(ell(sx * 4.6, hy + 4, 3.3, 2.9, 14), HOLLOW, LINE * 0.5)
            eye(sx * 4.6, hy + 4, 1.3, EYE_GREEN, halo=3.6)
        shape([(0, hy + 1), (-1.6, hy - 3), (1.6, hy - 3)], HOLLOW, 0)
        teeth = [(-4, hy - 6), (4, hy - 6), (3.6, hy - 9.8), (-3.6, hy - 9.8)]
        shape(teeth, BONE, LINE * 0.6)
        for i in range(5):
            stroke([(-2.8 + i * 1.4, hy - 6.2), (-2.8 + i * 1.4, hy - 9.6)], LINE * 0.35)
        stroke([(-3.8, hy - 8), (3.8, hy - 8)], LINE * 0.35)
    band = [(-12.5, hy + 12), (12.5, hy + 12), (12.5, hy + 17.5), (-12.5, hy + 17.5)]
    for i in range(7):
        x = (i - 3) * 3.8
        hgt = 34 if i == 3 else 26 if abs(i - 3) == 1 else 20
        sp = [(x - 2.0, hy + 17), (x, hy + hgt), (x + 2.0, hy + 17)]
        form(sp, IRON, sh=0.15)
        dot(x, hy + hgt - 0.6, 0.6, GOLD)
    form(band, IRON, sdx=0, sdy=-1, sh=0.2)
    for x in (-7, 7):
        dot(x, hy + 15, 0.9, GOLD)
    if not back:
        shape(ell(0, hy + 15, 1.9, 1.9, 12), GEM, LINE * 0.6)
        glow(0, hy + 15, 6, "#7dffa0", 0.4, 5)


def kostej_fb(pose, back):
    feet, sway, sw = KOS_FB[pose]
    shadow(0, 34)
    with T(0, 0, 1, flip=back):
        c = -sway * 1.6
        cape = [(-18 + sway, 132)] + bez((-18 + sway, 132), (-32, 104), (-38 + c * 0.5, 50), (-44 + c, 8)) + \
            ragged((-44 + c, 8), (44 + c, 8), 9, 6, 2.2) + bez((44 + c, 8), (38 + c * 0.5, 50), (32, 104), (18 + sway, 132))
        if not back:
            form(cape, CAPE, sdx=0, sdy=1, sh=0.2)
            hatch(cape, 2.0, 70, 0.5, g=col("#3a2f48"), alpha=0.5)
        for x, lift, sc in fb_feet(KOS_FEET[feet], back):
            kos_boot(x, lift, sc, back)
        if pose == "attack" and back:
            kos_arm(-1, 0, pose, back)
        with T(sway, 0):
            robe = [(-16, 128)] + bez((-16, 128), (-20, 90), (-25, 50), (-29 + c * 0.4, 14)) + \
                ragged((-29 + c * 0.4, 14), (29 + c * 0.4, 13), 7, 4, 0.7) + bez((29 + c * 0.4, 13), (25, 50), (20, 90), (16, 128))
            form(robe, ROBE, sdx=0, sdy=1, sh=0.2)
            for x0 in (-14, -5, 5, 14):
                stroke(bez((x0 * 0.6, 84), (x0 * 0.8, 60), (x0, 40), (x0 * 1.25, 16)), LINE * 0.6, g=ROBE_DK)
            for sx in (-1, 1):
                hatch(ell(sx * 20, 56, 7, 42, 20), 1.8, 60, 0.45, g=ROBE_DK, alpha=0.7)
            if back:
                cape = [(-20, 134)] + bez((-20, 134), (-28, 104), (-34 + c * 0.5, 50), (-40 + c, 9)) + \
                    ragged((-40 + c, 9), (40 + c, 9), 9, 6, 2.2) + bez((40 + c, 9), (34 + c * 0.5, 50), (28, 104), (20, 134))
                form(cape, CAPE, sdx=0, sdy=1, sh=0.2)
                hatch(cape, 2.0, 70, 0.5, g=col("#3a2f48"), alpha=0.5)
                for x0 in (-18, -6, 6, 18):
                    stroke(bez((x0 * 0.4, 128), (x0 * 0.7, 96), (x0 + c * 0.3, 50), (x0 * 1.3 + c * 0.8, 12)), LINE * 0.6, g=col("#3a2f48"))
            else:
                plate = bez((-16, 128), (-17, 110), (-12, 92), (0, 86)) + bez((0, 86), (12, 92), (17, 110), (16, 128))
                form(plate, ARMOR, sdx=0, sdy=0, sh=0.2)
                for yy in (120, 112, 104, 96):
                    stroke(bez((-15, yy), (-5, yy - 3), (5, yy - 3), (15, yy)), LINE * 0.6)
                for (x, y) in ((-9, 116), (9, 116), (-7, 100), (7, 100)):
                    dot(x, y, 0.9, RUST_DK)
                belt = [(-21, 88), (21, 88), (21, 82), (-21, 82)]
                form(belt, WOOD_DK, sh=0.15)
                shape(ell(0, 85, 4, 4, 14), GOLD_DK, LINE * 0.7)
                dot(0, 85, 1.6, GEM)
                fur = [(-22, 126)] + [(x, 134 + (3 if i % 2 else -1)) for i, x in enumerate(range(-20, 24, 5))] + \
                    [(22, 126), (14, 122), (0, 124), (-14, 122)]
                form(fur, ERMINE, sh=0.15)
                for x in (-14, -5, 5, 14):
                    dot(x, 129, 0.9, col("#3a3640"))
            arms = [(1, -sw)] if pose == "attack" and back else [(-1, sw), (1, -sw)]
            if not back:
                for sx in (-1, 1):
                    flap = [(sx * 6, 126), (sx * 22, 128), (sx * 27, 152), (sx * 21, 147), (sx * 19, 161), (sx * 13, 149), (sx * 9, 141)]
                    form(flap, CAPE, sdx=0, sdy=0, sh=0.2)
            for s, f in arms:
                kos_arm(s, f, pose, back)
            tube([(0, 126), (0, 138)], 6, 5, GAUNT, sh=0.2)
            kos_head_fb(back)
            if back:
                coll = [(-20, 128), (-26, 142), (-20, 139), (-17, 146), (-11, 139), (-5, 143), (0, 137), (5, 143), (11, 139),
                        (17, 146), (20, 139), (26, 142), (20, 128)]
                form(coll, CAPE, sdx=0, sdy=0, sh=0.2)
                for x in (-14, 0, 14):
                    stroke([(x * 0.8, 130), (x, 139)], LINE * 0.5, g=col("#3a2f48"))
            for sx in (-1, 1):
                cx = sx * 21
                form(ell(cx, 124, 9.5, 6.5, 20, a0=-20, a1=200), ARMOR, sh=0.2)
                for k in range(3):
                    b0 = (cx - 6 + k * 6, 128 + (2 if k == 1 else 0))
                    shape([(b0[0] - 1.6, b0[1]), (b0[0], b0[1] + 7 + (3 if k == 1 else 0)), (b0[0] + 1.6, b0[1])], IRON_LT, LINE * 0.5)
                stroke(ell(cx, 124, 7, 4.5, 14, 10, 170), LINE * 0.5)
            if pose == "attack":
                motion([bez((-34, 170), (-10, 160), (22, 120), (40, 66)), bez((-26, 160), (-4, 150), (20, 114), (32, 70))])
            if pose == "windup" and back:
                sword((-17, 162), 120, 10, 62)


def kostej_portrait():
    return portrait(kostej, 8, 150, 3.0, "#2f4434")


# ------------------------------------------------------------------ Permoník's true form
CAP_STONE = col("#a6493c"); SMOCK = col("#cfc9b8"); SMOCK_SH = col("#9d9686")


def ore(clip, seeds, n=5):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    for (x, y, a, ln) in seeds:
        p = [(x, y)]
        for k in range(n):
            a += (k % 2 * 2 - 1) * 28
            p.append(pt(p[-1], a, ln / n))
        stroke(p, LINE * 1.8, g=SILVER)
        stroke(p, LINE * 0.5, g=col("#8a95a6"))
        for q in p[1::2]:
            dot(q[0], q[1], 1.1, col("#ffffff"))
    C.restoreState()


def cracks(clip, seeds):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    for (x, y, a, ln) in seeds:
        p = [(x, y), pt((x, y), a, ln * 0.5)]
        p.append(pt(p[-1], a + 30, ln * 0.5))
        stroke(p, LINE * 0.7)
        stroke([p[1], pt(p[1], a - 40, ln * 0.35)], LINE * 0.5)
    C.restoreState()


def rock_seg(p0, p1, w0, w1, colr=None):
    o = tube([p0, p1], w0, w1, colr if colr is not None else ROCK, sh=0.2)
    a = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
    m = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
    cracks(o, [(m[0], m[1], a + 60, w0 * 0.7), (p0[0], p0[1], a + 120, w0 * 0.5)])
    return o


def root(pts, w0, w1):
    tube(pts, w0, w1, ROOT, LINE * 0.7, sh=0.15)


def fist(p, r, raised=False):
    f = ell(p[0], p[1], r, r * 0.85, 22)
    form(f, ROCK_LT, sh=0.2)
    for i in range(3):
        a = (60 if raised else -10) + i * 32
        q = pt(p, a, r * 0.75)
        shape(ell(q[0], q[1], r * 0.32, r * 0.28, 12), ROCK_LT, LINE * 0.7)
        dot(q[0], q[1], r * 0.1, SILVER)
    cracks(f, [(p[0], p[1], 200, r)])


def lamp(x, y, s=1.0):
    glow(x, y, 50 * s, LAMP, 0.45, 12)
    glow(x, y, 22 * s, "#9fd8ff", 0.5, 8)
    with T(x, y, s):
        body = [(-6, -10), (6, -10), (7, 6), (-7, 6)]
        form(body, BRONZE, sh=0.2)
        cage = rrect(-5.5, -6, 11, 11, 2)
        shape(cage, col("#dff4ff"), LINE * 0.7)
        flat(ell(0, -0.5, 2.6, 4.6, 16), "#ffffff")
        flat(ell(0, -0.5, 1.6, 3.2, 16), "#cfeeff")
        for x_ in (-2.5, 2.5):
            stroke([(x_, -6), (x_, 5)], LINE * 0.5)
        shape([(-4, 6), (4, 6), (0, 11)], BRONZE, LINE * 0.7)
        stroke(ell(0, 11, 3, 3, 12, 0, 180), LINE * 0.8)


def shards(base, spec, colr):
    for (a, ln, w) in spec:
        tip = pt(base, a, ln)
        l = pt(base, a + 90, w); r = pt(base, a - 90, w)
        mid = pt(pt(base, a, ln * 0.7), a + 90, w * 0.6)
        sh_ = [l, mid, tip, pt(pt(base, a, ln * 0.6), a - 90, w * 0.7), r]
        form(sh_, colr, sh=0.2)
        stroke([pt(base, a, ln * 0.2), tip], LINE * 0.45, alpha=0.6)


def crystal(base, a, ln, w):
    tip = pt(base, a, ln)
    body = [pt(base, a + 90, w), pt(pt(base, a, ln * 0.75), a + 90, w), tip, pt(pt(base, a, ln * 0.75), a - 90, w), pt(base, a - 90, w)]
    glow(*pt(base, a, ln * 0.6), w * 2.5, "#bfe4ff", 0.25, 5)
    form(body, SILVER, sh=0.25)
    stroke([base, tip], LINE * 0.5, g=col("#8a95a6"))


def obr_head(pose):
    hx, hy = 24, 200
    head = bez((hx - 22, hy - 6), (hx - 26, hy + 12), (hx - 14, hy + 24), (hx + 2, hy + 24)) + \
        bez((hx + 2, hy + 24), (hx + 20, hy + 24), (hx + 28, hy + 12), (hx + 25, hy - 6)) + \
        bez((hx + 25, hy - 6), (hx + 12, hy - 14), (hx - 8, hy - 14), (hx - 22, hy - 6))
    form(head, ROCK_LT, sdx=-4, sdy=1, sh=0.22)
    cracks(head, [(hx - 12, hy + 16, -70, 14)])
    cap = [(hx - 24, hy + 15)] + bez((hx - 24, hy + 15), (hx - 20, hy + 30), (hx - 32, hy + 36), (hx - 48, hy + 30)) + \
        bez((hx - 48, hy + 30), (hx - 32, hy + 42), (hx - 4, hy + 40), (hx + 12, hy + 32)) + \
        bez((hx + 12, hy + 32), (hx + 24, hy + 26), (hx + 28, hy + 20), (hx + 26, hy + 14))
    form(cap, CAP_STONE, sdx=-3, sdy=1, sh=0.2)
    cracks(cap, [(hx - 10, hy + 34, -150, 20), (hx + 8, hy + 28, 200, 14)])
    shape(bez((hx - 26, hy + 13), (hx - 4, hy + 19), (hx + 14, hy + 19), (hx + 27, hy + 13)) + [(hx + 27, hy + 17)] +
          bez((hx + 27, hy + 17), (hx + 14, hy + 23), (hx - 4, hy + 23), (hx - 26, hy + 17)), col("#8a3a30"), LINE * 0.8)
    brow = [(hx - 8, hy + 11), (hx + 24, hy + 9), (hx + 26, hy + 3), (hx - 6, hy + 6)]
    shape(brow, ROCK_DK, LINE * 0.8)
    for ex, r_ in ((hx + 17, 3.4), (hx + 4, 2.8)):
        shape(ell(ex, hy + 2, r_ * 1.5, r_ * 1.1, 14), col("#3a4452"), 0)
        glow(ex, hy + 2, r_ * 4, "#9fd8ff", 0.35, 5)
        eye(ex, hy + 2, r_, EYE_WHITE, halo=3)
    nose = [(hx + 22, hy + 2), (hx + 31, hy - 6), (hx + 23, hy - 9)]
    shape(nose, ROCK_LT, LINE * 0.9)
    mo = pose == "attack"
    if mo:
        shape(ell(hx + 14, hy - 12, 7, 4.5, 16), col("#3a4452"), LINE * 0.8)
        glow(hx + 14, hy - 12, 9, LAMP, 0.45, 5)
    beard = [(hx - 20, hy - 4)] + bez((hx - 20, hy - 4), (hx - 6, hy - 10 - mo * 6), (hx + 12, hy - 10 - mo * 6), (hx + 26, hy - 4)) + \
        [(hx + 26, hy - 18), (hx + 20, hy - 36), (hx + 16, hy - 28), (hx + 10, hy - 54), (hx + 4, hy - 36),
         (hx - 2, hy - 48), (hx - 8, hy - 30), (hx - 14, hy - 40), (hx - 18, hy - 22)]
    if mo:
        beard = [(hx - 20, hy - 4), (hx + 6, hy - 16), (hx + 24, hy - 18), (hx + 26, hy - 20), (hx + 20, hy - 38), (hx + 16, hy - 30), (hx + 10, hy - 56), (hx + 4, hy - 38),
                 (hx - 2, hy - 50), (hx - 8, hy - 32), (hx - 14, hy - 42), (hx - 18, hy - 22)]
    form(beard, ROOT, sdx=-3, sdy=0, sh=0.2)
    for k in range(5):
        x0 = hx - 14 + k * 8
        root(bez((x0, hy - 8), (x0 + 1, hy - 18), (x0 - 2, hy - 28), (x0 + 1, hy - 38 - (k % 2) * 8)), 2.4, 0.6)
    for (x, y) in ((hx + 10, hy - 54), (hx - 2, hy - 48), (hx + 20, hy - 36)):
        shape([(x - 2, y + 4), (x + 2, y + 4), (x, y - 3)], SILVER, LINE * 0.5)


# walk: far leg (knee, ankle), near leg (knee, ankle), far elbow, far fist, near elbow, near fist
OBR_WALK = {
    "walk": ((-36, 52), (-46, 18), (40, 54), (46, 18), (-62, 132), (-52, 68), (70, 132), (62, 70)),
    "walk2": ((-24, 60), (-22, 36), (28, 50), (28, 18), (-70, 132), (-66, 66), (76, 131), (78, 68)),
    "walk3": ((-14, 54), (-10, 18), (18, 52), (10, 18), (-76, 132), (-78, 68), (80, 132), (92, 72)),
    "walk4": ((-28, 50), (-28, 18), (34, 60), (30, 36), (-70, 132), (-66, 66), (76, 131), (78, 68)),
}


def stomp(x, y, w):
    for sx in (-1, 1):
        for k in range(3):
            a = 90 + sx * (40 + k * 22)
            p0 = pt((x + sx * w, y - 6), a, 4)
            stroke([p0, pt(p0, a, 7 + k * 2)], LINE * 0.6, alpha=0.5)
        dot(x + sx * (w + 8), y - 8, 1.4, ROCK_DK)
        dot(x + sx * (w + 14), y - 9, 1.0, ROCK_DK)


def obr_foot(x, y, c_, lifted):
    foot = [(x - 18, y + 4), (x + 18, y + 6), (x + 28, y - 4), (x + 26, y - 10), (x - 20, y - 10)]
    form(foot, c_, sh=0.2)
    for dx in (-14, -2, 12, 22):
        if lifted:
            root(bez((x + dx, y - 8), (x + dx * 1.1, y - 14), (x + dx * 1.2 - 4, y - 18), (x + dx * 1.2 - 8, y - 22 - abs(dx) * 0.2)), 3.2, 0.8)
        else:
            root(bez((x + dx, y - 8), (x + dx * 1.3, y - 9), (x + dx * 1.6 + 6, y - 9), (x + dx * 2 + (8 if dx > 0 else -8), y - 10)), 3.2, 0.8)


def permonik_obr(pose):
    pose, view = view_of(pose)
    if view:
        return obr_fb(pose, view == "b")
    lean = {"idle": 0, "walk": 6, "walk2": 4, "walk3": 6, "walk4": 4, "windup": -4, "attack": 4}[pose]
    wk = OBR_WALK.get(pose)
    if wk:
        fl = ((-22, 88), wk[0], wk[1]); nl = ((22, 88), wk[2], wk[3])
    elif pose in ("attack", "windup"):
        fl = ((-22, 88), (-34, 52), (-42, 18)); nl = ((22, 88), (36, 54), (40, 18))
    else:
        fl = ((-22, 88), (-30, 50), (-32, 18)); nl = ((22, 88), (30, 50), (32, 18))
    for leg, c_ in ((fl, ROCK_DK), (nl, ROCK)):
        rock_seg(leg[0], leg[1], 34, 30, c_)
        rock_seg(leg[1], leg[2], 30, 32, c_)
        obr_foot(*leg[2], c_, leg[2][1] > 24)
    if pose in ("walk", "walk3"):
        x, y = (nl if pose == "walk" else fl)[2]
        stomp(x + 4, y, 30)
    fsh = (-46 + lean, 182)
    if pose in ("attack", "windup"):
        fe = (-74 + lean, 136); fh = (-70 + lean, 80)
    elif wk:
        fe = (wk[4][0] + lean, wk[4][1]); fh = (wk[5][0] + lean, wk[5][1])
    else:
        fe = (-70 + lean, 132); fh = (-66 + lean, 66)
    rock_seg(fsh, fe, 36, 30, ROCK_DK); rock_seg(fe, fh, 30, 26, ROCK_DK)
    root(bez(fsh, (fsh[0] - 18, fsh[1] - 10), (fe[0] - 12, fe[1] + 10), fe), 4, 2)
    fist(fh, 17)
    with T(lean, 0):
        shards((-58, 172), ((150, 34, 7), (165, 26, 6), (135, 22, 5)), ROCK_DK)
        crystal((-56, 184), 125, 30, 4.5)
        tors = bez((-50, 198), (-76, 180), (-66, 130), (-40, 84)) + bez((-40, 84), (-14, 72), (18, 72), (40, 84)) + \
            bez((40, 84), (64, 128), (78, 176), (58, 200)) + bez((58, 200), (30, 216), (-24, 216), (-50, 198))
        form(tors, ROCK, sdx=-8, sdy=3, sh=0.22)
        hatch(ell(-54, 140, 18, 60, 20), 2.4, 60, 0.6, alpha=0.6)
        ore(tors, [(-44, 188, -60, 50), (40, 190, -110, 46), (-26, 100, 20, 40), (46, 112, 150, 34)])
        cracks(tors, [(-16, 206, -100, 30), (56, 150, 200, 30), (-60, 120, -20, 26)])
        for sx in (-1, 1):
            for k in range(3):
                root(bez((sx * 34, 186 - k * 22), (sx * 20, 180 - k * 20), (sx * 18, 168 - k * 20), (sx * 12, 160 - k * 20)), 4.5, 1.2)
        smock = bez((-44, 100), (-20, 94), (20, 94), (46, 100)) + ragged((46, 100), (42, 74), 2, 5, 0.3) + \
            ragged((42, 74), (-44, 74), 8, 9, 1.1) + [(-44, 100)]
        form(smock, SMOCK, sdx=-4, sdy=1, sh=0.18)
        hatch(smock, 2.0, 70, 0.45, g=SMOCK_SH, alpha=0.6)
        root(bez((-44, 94), (-10, 88), (20, 88), (46, 94)), 5, 4)
        cav = bez((-24, 168), (-34, 150), (-30, 122), (-6, 114)) + bez((-6, 114), (18, 120), (22, 150), (12, 168)) + \
            bez((12, 168), (2, 176), (-14, 176), (-24, 168))
        shape(cav, col("#3a4452"), LINE * 1.2)
        lamp(-10, 140, 1.4)
        for k in range(4):
            a0 = 200 + k * 40
            root(bez(pt((-6, 145), a0, 26), pt((-6, 145), a0 + 10, 20), pt((-6, 145), a0 - 6, 16), pt((-6, 145), a0 + 4, 12)), 3.5, 1.2)
        shards((50, 200), ((80, 30, 7), (100, 40, 8), (60, 22, 6)), ROCK_LT)
        crystal((40, 204), 95, 34, 5); crystal((60, 196), 70, 22, 4)
        shards((-40, 206), ((95, 32, 7), (120, 26, 6)), ROCK)
        crystal((-28, 210), 105, 24, 4)
    sh0 = (54 + lean, 178)
    if pose == "attack":
        el = (78 + lean, 206); H = (88 + lean, 236)
        glow(H[0], H[1], 24, LAMP, 0.3, 6)
    elif wk:
        el = (wk[6][0] + lean, wk[6][1]); H = (wk[7][0] + lean, wk[7][1])
    elif pose == "windup":
        el = (94 + lean, 150); H = (76 + lean, 196)
    else:
        el = (76, 130); H = (80, 66)
    rock_seg(sh0, el, 38, 32, ROCK); rock_seg(el, H, 32, 28, ROCK)
    root(bez(sh0, (sh0[0] + 16, sh0[1] - 6), (el[0] + 12, el[1] + 8), el), 4.5, 2)
    root(bez(el, (el[0] + 8, el[1] - 10), (H[0] + 10, H[1] + 10), H), 3.5, 1.5)
    crystal(pt(el, 10, 10), 30, 18, 3.5)
    fist(H, 19, raised=pose in ("attack", "windup"))
    with T(lean + 24 * (1 - 1.22), 200 * (1 - 1.22), 1.22):
        obr_head(pose)
    if pose == "attack":
        motion([bez((54, 238), (70, 248), (92, 252), (110, 236)), bez((60, 230), (74, 240), (92, 244), (104, 230))])


OBR_FEET = {
    "stand": ((-36, 0, 1.0), (36, 0, 1.0)),
    "c1": ((-37, -4, 1.1), (36, 4, 0.9)),
    "p1": ((-34, 0, 1.0), (38, 16, 0.95)),
    "c2": ((-36, 4, 0.9), (37, -4, 1.1)),
    "p2": ((-38, 16, 0.95), (34, 0, 1.0)),
    "brace": ((-46, 0, 1.0), (46, 0, 1.0)),
}
OBR_FB = {"idle": ("stand", 0, 0), "walk": ("c1", 0, -1), "walk2": ("p1", -4, 0), "walk3": ("c2", 0, 1),
          "walk4": ("p2", 4, 0), "windup": ("brace", 0, 0), "attack": ("brace", 0, 0)}


def obr_leg_fb(x, lift, sc, back):
    s = -1 if x < 0 else 1
    hip = (s * 26, 88); knee = (s * 31 + (x - s * 36) * 0.5, 52 + lift * 0.6); ank = (x, 18 + lift)
    c_ = ROCK if sc >= 1 else ROCK_DK
    rock_seg(hip, knee, 34 * sc, 30 * sc, c_)
    rock_seg(knee, ank, 30 * sc, 32 * sc, c_)
    lifted = lift > 8
    with T(x, 18 + lift, sc):
        foot = [(-20, 6)] + bez((-20, 6), (-24, 0), (-24, -8), (-18, -11)) + [(18, -11)] + bez((18, -11), (24, -8), (24, 0), (20, 6))
        form(foot, c_, sh=0.2)
        if not back:
            for tx in (-12, 0, 12):
                shape(ell(tx, -7, 6, 4, 14), ROCK_LT, LINE * 0.7)
        else:
            stroke(bez((-14, -2), (-5, -5), (5, -5), (14, -2)), LINE * 0.6)
        for dx in (-16, -6, 6, 16):
            if lifted:
                root(bez((dx, -9), (dx * 1.1, -15), (dx * 1.2, -19), (dx * 1.3, -24 - abs(dx) * 0.2)), 3.2, 0.8)
            else:
                sx = 1 if dx > 0 else -1
                root(bez((dx, -9), (dx * 1.3, -10), (dx * 1.6 + sx * 4, -10), (dx * 2 + sx * 10, -11)), 3.2, 0.8)
    if lift < 0:
        stomp(x, 18 + lift, 26 * sc)


def obr_arm_fb(s, f, pose, back):
    sh0 = (s * 60, 182)
    r = 18 * (1 + 0.07 * f)
    if s < 0 and pose == "windup":
        el, H, r = (s * 98, 172), (s * 80, 238), 20
    elif s < 0 and pose == "attack":
        el, H, r = (s * 60, 150), (s * 20, 84), 24
    elif pose in ("windup", "attack"):
        el, H = (s * 84, 128), (s * 90, 74)
    else:
        el = (s * (80 - 2 * f), 131 - 2 * f); H = (s * (84 - 4 * f), 68 - 7 * f)
    rock_seg(sh0, el, 38, 32, ROCK if s < 0 else ROCK_DK); rock_seg(el, H, 32, 28, ROCK if s < 0 else ROCK_DK)
    root(bez(sh0, (sh0[0] + s * 16, sh0[1] - 6), (el[0] + s * 12, el[1] + 8), el), 4.5, 2)
    root(bez(el, (el[0] + s * 8, el[1] - 10), (H[0] + s * 10, H[1] + 10), H), 3.5, 1.5)
    crystal(pt(el, 90 - s * 80, 10), 90 - s * 60, 18, 3.5)
    if s < 0 and pose == "attack":
        glow(H[0], H[1], 30, LAMP, 0.3, 6)
    fist(H, r, raised=s < 0 and pose == "windup")


def obr_head_fb(pose, back):
    hy = 200
    mo = pose == "attack" and not back
    head = bez((-24, hy - 6), (-28, hy + 12), (-16, hy + 26), (0, hy + 26)) + \
        bez((0, hy + 26), (16, hy + 26), (28, hy + 12), (24, hy - 6)) + \
        bez((24, hy - 6), (12, hy - 14), (-12, hy - 14), (-24, hy - 6))
    beard = [(-22, hy - 4)] + bez((-22, hy - 4), (-8, hy - 12 - mo * 5), (8, hy - 12 - mo * 5), (22, hy - 4)) + \
        [(24, hy - 12), (19, hy - 26), (13, hy - 19), (7, hy - 30), (2, hy - 21), (-3, hy - 29), (-8, hy - 19),
         (-14, hy - 27), (-19, hy - 17), (-24, hy - 12)]
    if back:
        for sx in (-1, 1):
            root(bez((sx * 20, hy - 6), (sx * 28, hy - 12), (sx * 30, hy - 20), (sx * 28, hy - 28)), 4, 1)
            root(bez((sx * 14, hy - 10), (sx * 18, hy - 18), (sx * 16, hy - 24), (sx * 18, hy - 32)), 3.2, 0.8)
    form(head, ROCK_LT, sdx=0, sdy=-1.5, sh=0.22)
    cracks(head, [(-12, hy + 16, -70, 14), (14, hy - 4, 110, 12)])
    if back:
        ore(head, [(-14, hy + 4, -20, 22), (10, hy - 6, 30, 16)], 4)
    else:
        brow = [(-22, hy + 9), (22, hy + 9), (20, hy + 3), (-20, hy + 4)]
        shape(brow, ROCK_DK, LINE * 0.8)
        for sx in (-1, 1):
            shape(ell(sx * 9, hy + 1, 4.8, 3.6, 14), col("#3a4452"), 0)
            glow(sx * 9, hy + 1, 13, "#9fd8ff", 0.35, 5)
            eye(sx * 9, hy + 1, 3.2, EYE_WHITE, halo=3)
        if mo:
            shape(ell(0, hy - 12, 8, 4.5, 16), col("#3a4452"), LINE * 0.8)
            glow(0, hy - 12, 10, LAMP, 0.45, 5)
        form(beard, ROOT, sdx=0, sdy=-1, sh=0.2)
        for k in range(5):
            x0 = -14 + k * 7
            root(bez((x0, hy - 8 - mo * 4), (x0 + 1, hy - 14), (x0 - 1, hy - 20), (x0 * 0.9, hy - 24 - (k % 2) * 4)), 2.4, 0.6)
        for (x, y) in ((7, hy - 30), (-3, hy - 29), (-14, hy - 27), (19, hy - 26)):
            shape([(x - 2, y + 4), (x + 2, y + 4), (x, y - 3)], SILVER, LINE * 0.5)
        nose = [(-4, hy + 4), (4, hy + 4), (6, hy - 5), (0, hy - 9), (-6, hy - 5)]
        shape(nose, ROCK_LT, LINE * 0.9)
    cap = [(-27, hy + 14)] + bez((-27, hy + 14), (-26, hy + 32), (-14, hy + 50), (0, hy + 54)) + \
        bez((0, hy + 54), (14, hy + 50), (26, hy + 32), (27, hy + 14))
    form(cap, CAP_STONE, sdx=0, sdy=1, sh=0.2)
    cracks(cap, [(-10, hy + 34, -150, 18), (10, hy + 28, 200, 14)])
    if back:
        flap = [(-12, hy + 50)] + bez((-12, hy + 50), (-16, hy + 38), (-12, hy + 26), (-4, hy + 20)) + [(6, hy + 22)] + \
            bez((6, hy + 22), (4, hy + 32), (10, hy + 44), (12, hy + 50))
        form(flap, CAP_STONE, sdx=0, sdy=0, sh=0.25)
        stroke(bez((-8, hy + 44), (-8, hy + 34), (-4, hy + 28), (0, hy + 24)), LINE * 0.6)
    shape(bez((-28, hy + 12), (-10, hy + 18), (10, hy + 18), (28, hy + 12)) + [(28, hy + 16)] +
          bez((28, hy + 16), (10, hy + 22), (-10, hy + 22), (-28, hy + 16)), col("#8a3a30"), LINE * 0.8)


def obr_fb(pose, back):
    feet, sway, sw = OBR_FB[pose]
    with T(0, 0, 1, flip=back):
        if back:
            glow_ell(0, 145, 135, 150, LAMP, 0.3, 14)
            glow_ell(0, 140, 105, 95, "#9fd8ff", 0.3, 10)
        if back and pose == "attack":
            obr_arm_fb(-1, 0, pose, back)
        for x, lift, sc in fb_feet(OBR_FEET[feet], back):
            obr_leg_fb(x, lift, sc, back)
        with T(sway, 0):
            for sx in (-1, 1):
                shards((sx * 58, 186), ((90 + sx * 60, 32, 7), (90 + sx * 40, 26, 6), (90 + sx * 75, 22, 5)), ROCK_DK)
                crystal((sx * 56, 196), 90 - sx * 30, 30, 4.5)
            tors = bez((-50, 200), (-80, 180), (-72, 130), (-44, 84)) + bez((-44, 84), (-16, 72), (16, 72), (44, 84)) + \
                bez((44, 84), (72, 130), (80, 180), (50, 200)) + bez((50, 200), (26, 216), (-26, 216), (-50, 200))
            form(tors, ROCK, sdx=0, sdy=3, sh=0.22)
            for sx in (-1, 1):
                hatch(ell(sx * 58, 140, 14, 56, 20), 2.4, 60, 0.6, alpha=0.6)
            ore(tors, [(-44, 188, -60, 50), (44, 190, -120, 46), (-30, 100, 20, 40), (30, 104, 160, 36)])
            cracks(tors, [(-16, 206, -100, 30), (56, 150, 200, 30), (-60, 120, -20, 26)])
            if back:
                for a, ln in ((60, 40), (100, 52), (150, 34), (215, 38), (260, 30), (320, 42), (20, 30)):
                    p = [(0, 146), pt((0, 146), a, ln * 0.5)]
                    p.append(pt(p[-1], a + 25, ln * 0.5))
                    glow(*p[1], 7, LAMP, 0.35, 4)
                    stroke(p, LINE * 1.3, g=col("#dff4ff"))
                    stroke(p, LINE * 0.45, g=col("#3a4452"), alpha=0.6)
                glow(0, 146, 16, LAMP, 0.4, 6)
                for sx in (-1, 1):
                    root(bez((sx * 60, 196), (sx * 34, 170), (sx * 20, 130), (sx * 30, 96)), 5, 2)
                    root(bez((sx * 40, 206), (sx * 14, 186), (sx * 8, 160), (0, 120)), 4, 1.5)
            else:
                for sx in (-1, 1):
                    for k in range(3):
                        root(bez((sx * 46, 186 - k * 22), (sx * 32, 180 - k * 20), (sx * 28, 168 - k * 20), (sx * 21, 160 - k * 20)), 4.5, 1.2)
            smock = bez((-46, 100), (-20, 94), (20, 94), (46, 100)) + ragged((46, 100), (44, 74), 2, 5, 0.3) + \
                ragged((44, 74), (-46, 74), 8, 9, 1.1) + [(-46, 100)]
            form(smock, SMOCK, sdx=0, sdy=1, sh=0.18)
            hatch(smock, 2.0, 70, 0.45, g=SMOCK_SH, alpha=0.6)
            root(bez((-46, 94), (-12, 88), (12, 88), (46, 94)), 5, 4)
            if not back:
                cav = bez((-20, 174), (-32, 156), (-28, 124), (0, 114)) + bez((0, 114), (28, 124), (32, 156), (20, 174)) + \
                    bez((20, 174), (8, 182), (-8, 182), (-20, 174))
                shape(cav, col("#3a4452"), LINE * 1.2)
                lamp(0, 144, 1.5)
                for a0 in (210, 250, 290, 330):
                    c0 = (0, 148)
                    root(bez(pt(c0, a0, 28), pt(c0, a0 + 8, 22), pt(c0, a0 - 6, 17), pt(c0, a0 + 3, 13)), 3.5, 1.2)
            arms = [(1, -sw)] if pose == "attack" and back else [(-1, sw), (1, -sw)]
            if back:
                with T(0, 200 * (1 - 1.22), 1.22):
                    obr_head_fb(pose, back)
            for s, f in arms:
                obr_arm_fb(s, f, pose, back)
            if not back:
                with T(0, 200 * (1 - 1.22), 1.22):
                    obr_head_fb(pose, back)
            else:
                for sx in (-1, 1):
                    shards((sx * 50, 194), ((90 - sx * 30, 30, 7), (90 - sx * 50, 38, 8), (90 - sx * 70, 22, 6)), ROCK_LT)
                    crystal((sx * 42, 200), 90 - sx * 40, 26, 4.5)
            if pose == "attack" and not back:
                motion([bez((-100, 250), (-90, 200), (-60, 120), (-24, 70)), bez((-88, 252), (-76, 196), (-50, 124), (-16, 80))])


def obr_portrait():
    return portrait(permonik_obr, 30, 206, 1.4, "#2a3a4c")


kostej.poses = permonik_obr.poses = ALL
SPRITES = boss_items("kostej", kostej, 352, 0.86) + boss_items("permonik_obr", permonik_obr, 512, 0.92)
PORTRAITS = [("boss_kostej", 256, 256, kostej_portrait()), ("boss_permonik_obr", 256, 256, obr_portrait())]

if __name__ == "__main__":
    common.run({"sprites/monsters": SPRITES, "portraits": PORTRAITS})
