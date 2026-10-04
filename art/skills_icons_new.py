"""Skill icons for the five later classes (ui/skills/<id>.png, 64 px), in the frame and light of skills_icons.py."""
import math
import common
from icons_kit import *
from icons_sym import *
from skills_icons import bg, frame, swoosh, rays

TREES = {
    "kladivo": ("#3a2418", "#d8904a"), "vyhen": ("#40140a", "#ff7a2a"), "kovani": ("#22262c", "#a8b8c8"),
    "modly": ("#2a2410", "#f0d070"), "obet": ("#3a0c10", "#e04050"), "dedkove": ("#14202e", "#bfe0ff"),
    "promena": ("#262420", "#c8b8a0"), "smecka": ("#1c2418", "#a0b890"), "les": ("#14240e", "#86c050"),
    "lucavka": ("#142a10", "#86e05a"), "golem": ("#2e2218", "#c8a07a"), "transmutace": ("#2e2408", "#f2c040"),
    "marionety": ("#2e1418", "#f2b030"), "dudy": ("#18203a", "#80b0ff"), "sibalstvi": ("#22182e", "#c8a0ff"),
}
SKILLS = []


def sk(tree):
    def deco(fn):
        def draw(b):
            bg(b, *TREES[tree]); fn(b.w / 2, b.h / 2); frame(b)
        SKILLS.append((fn.__name__, 64, 64, draw)); return fn
    return deco


# ------------------------------------------------------------------ shared motifs
def anvil(cx, cy, s=1.0):
    with T(cx, cy, s):
        top = [(-11, 2), (13, 2), (9, -1), (5, -2), (4, -6), (-5, -6), (-6, -2), (-9, -1)]
        form(top, IRON, W, sh=0.25)
        form(rect(-6, -11, 12, 5), IRON_D, W * 0.8, sh=0.2)
        hl([(-9, 1.4), (9, 1.4)], 0.6, 0.6)


def flask(cx, cy, s=1.0, liquid="#86e05a", round_=True):
    with T(cx, cy, s):
        body = ell(0, -3, 7, 7, 22) if round_ else [(-6, -10), (6, -10), (3, 2), (-3, 2)]
        shape(body, GLASS, W)
        clip_fill(body, rect(-8, -12, 16, 8), K(liquid, 0.55))
        shape(rect(-2, 3, 4, 7), GLASS, W * 0.8)
        shape(rect(-2.6, 9, 5.2, 2.4), K("#7a5232", 0.45), W * 0.6)
        hl([(-4, 0), (-3, -6)], 0.7, 0.8)


def golem(cx, cy, s=1.0, col="#a8865a"):
    with T(cx, cy, s):
        form(rrect(-8, -8, 16, 15, 3), K(col, 0.45), W, sh=0.25)
        form(rrect(-5, 6, 10, 8, 2.5), K(col, 0.5), W, sh=0.2)
        for sx in (-1, 1):
            form(rrect(sx * 8 - (4 if sx > 0 else 0), -10, 4, 13, 1.5), K(col, 0.4), W * 0.8, sh=0.2)
            form(rrect(sx * 3 - 2, -15, 4, 8, 1.2), K(col, 0.4), W * 0.8, sh=0.2)
        dot(-2, 10, 0.9, K("#ffd060", 0.9)); dot(2, 10, 0.9, K("#ffd060", 0.9))
        shape(rect(-2.5, 7, 5, 1.6), K("#f2ece0", 0.9), W * 0.4)


def wolf_head(cx, cy, s=1.0, col="#8a8680"):
    with T(cx, cy, s):
        hd = [(-9, 6), (-6, 14), (-3, 8), (3, 8), (6, 14), (9, 6), (8, -2), (2, -10), (-2, -10), (-8, -2)]
        form(hd, K(col, 0.5), W, sh=0.25)
        shape([(-2.5, -7), (2.5, -7), (0, -10.5)], INK, W * 0.5)
        for sx in (-1, 1):
            shape(ell(sx * 3.6, 1.5, 1.6, 1.0, 10), K("#ffd040", 0.85), W * 0.4)
            dot(sx * 3.6, 1.5, 0.5, 0.05)


def idol(cx, cy, s=1.0, faces=4):
    with T(cx, cy, s):
        form(rect(-6, -14, 12, 26), WOOD, W, sh=0.25)
        for k in range(min(faces, 3)):
            y = 6 - k * 8
            stroke([(-3, y), (-1, y)], 0.6); stroke([(1, y), (3, y)], 0.6)
            stroke([(-1.5, y - 3), (1.5, y - 3)], 0.5)
        shape(ell(0, 12.5, 7.5, 2.4, 16), WOOD_D, W * 0.7)


def puppet(cx, cy, s=1.0, col="#f2b030", head="#e8c8a8"):
    with T(cx, cy, s):
        stroke([(-9, 13), (9, 13)], 1.4, g=WOOD)
        stroke([(0, 15), (0, 11)], 1.2, g=WOOD)
        for x0, x1, y1 in ((-9, -6, -2), (9, 6, -2), (0, 0, 6), (-5, -3, -11), (5, 3, -11)):
            line([(x0, 13), (x1, y1)], "#e8e2d4", 0.4, 0.8)
        shape(ell(0, 4, 3.4, 3.4, 16), K(head, 0.85), W * 0.7)
        shape([(-3, 0), (3, 0), (5, -9), (-5, -9)], K(col, 0.6), W * 0.7)
        shape([(-2.5, 7), (2.5, 7), (0, 12)], K("#c8322e", 0.4), W * 0.5)
        for sx in (-1, 1):
            stroke([(sx * 3, -1), (sx * 6, -3)], 1.2)
            stroke([(sx * 2, -9), (sx * 3, -13)], 1.2)


def bagpipe(cx, cy, s=1.0):
    with T(cx, cy, s):
        form(ell(-2, -2, 8, 6.5, 22), K("#6a4a30", 0.32), W, sh=0.22)
        for dx, L in ((-6, 15), (-2, 18), (2, 12)):
            tube([(dx, 3), (dx - 4, 3 + L)], 1.5, 1.2, WOOD_L, W * 0.5, sh=0)
        tube([(5, -4), (12, -12)], 1.6, 1.4, WOOD_L, W * 0.5, sh=0)
        hd = bez((6, 2), (9, 6), (13, 5), (13, 1)) + [(9, 0)]
        form(hd, K("#e8dcc0", 0.88), W * 0.6, sh=0.15)
        tube(bez((10, 5), (11, 9), (13, 10), (14, 9)), 1.0, 0.5, K("#a8987a", 0.6), W * 0.3, sh=0)


def notes(cx, cy, n=3, col="#ffffff"):
    for i in range(n):
        x, y = cx + i * 5 - 5, cy + (i % 2) * 4
        dot(x, y, 1.6, K(col, 0.95))
        line([(x + 1.4, y), (x + 1.4, y + 7)], col, 0.8, 0.9)


def roots(cx, cy, s=1.0, col="#6a4a2a"):
    with T(cx, cy, s):
        for a in (-60, -20, 20, 60, 100, 140):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            tube(bez((0, 0), (ca * 5, sa * 4 - 3), (ca * 10, sa * 9 - 2), (ca * 14, sa * 13 - 6)), 2.4, 0.6, K(col, 0.35), W * 0.6, sh=0)


def thorns(cx, cy, s=1.0):
    with T(cx, cy, s):
        tube(bez((-12, -8), (-4, 4), (4, -4), (12, 8)), 1.8, 1.4, K("#4a5a2a", 0.35), W * 0.6, sh=0)
        for t in range(6):
            x, y = -10 + t * 4, -6 + (t % 3) * 3
            shape([(x, y), (x + 1.6, y + 3.6), (x + 2.6, y)], K("#c8b890", 0.75), W * 0.3)


def blood(cx, cy, r=5):
    d = bez((cx, cy + r * 1.8), (cx - r * 0.2, cy + r), (cx - r, cy + r * 0.2), (cx - r, cy - r * 0.3)) + \
        bez((cx - r, cy - r * 0.3), (cx - r, cy - r * 1.2), (cx + r, cy - r * 1.2), (cx + r, cy - r * 0.3)) + \
        bez((cx + r, cy - r * 0.3), (cx + r, cy + r * 0.2), (cx + r * 0.2, cy + r), (cx, cy + r * 1.8))
    form(d, K("#a8182a", 0.3), W, sh=0.2)
    hl([(cx - r * 0.5, cy - r * 0.2), (cx - r * 0.3, cy + r * 0.5)], 0.7, 0.7)


def ghost(cx, cy, s=1.0, col="#d8ecff"):
    with T(cx, cy, s):
        g = bez((-7, -10), (-8, 4), (-6, 12), (0, 12)) + bez((0, 12), (6, 12), (8, 4), (7, -10)) + \
            [(5, -7), (3, -11), (0, -8), (-3, -11), (-5, -7)]
        glow(0, 0, 13, col, 0.35)
        shape(g, K(col, 0.9), W * 0.8)
        dot(-2.4, 4, 1.1, K("#1a2a3a", 0.1)); dot(2.4, 4, 1.1, K("#1a2a3a", 0.1))


def coins(cx, cy):
    for i, (dx, dy) in enumerate(((-6, -6), (0, -7), (6, -6), (-3, -2), (3, -2))):
        coin(cx + dx, cy + dy, 4.2)


def fog(cx, cy, col="#d8d0e8"):
    for i, (dx, dy, r) in enumerate(((-7, 2, 6), (0, 5, 7), (7, 1, 6), (-3, -4, 6), (4, -5, 5))):
        flat(ell(cx + dx, cy + dy, r, r * 0.7, 18), col, 0.42)


def claw(cx, cy, col="#e8e2d4"):
    for k in range(3):
        x = cx - 6 + k * 6
        line(bez((x - 3, cy + 11), (x - 1, cy + 3), (x + 1, cy - 4), (x + 4, cy - 11)), col, 1.6, 0.9)


# ------------------------------------------------------------------ KOVÁŘ
@sk("kladivo")
def uder_kladivem(cx, cy):
    anvil(cx, cy - 7, 0.9)
    hammer(cx + 2, cy + 6, 1.0, rot=-40)
    rays(cx + 2, cy - 4, 3, 9, 8, "#ffd070", 0.7, 0.8)


@sk("kladivo")
def rozkovat(cx, cy):
    swoosh(cx, cy - 2, 12, 20, 200, "#ffe0a0", 2.6)
    hammer(cx - 4, cy + 4, 0.9, rot=30)
    shape(rect(cx - 11, cy - 12, 22, 3), K("#ff9a3a", 0.6), W * 0.6)


@sk("kladivo")
def hod_kladivem(cx, cy):
    for i in range(3):
        line([(cx - 14 + i * 3, cy - 6 + i * 4), (cx - 4 + i * 3, cy - 2 + i * 4)], "#ffe0a0", 1.2, 0.3 + i * 0.2)
    hammer(cx + 5, cy + 2, 0.9, rot=-120)


@sk("kladivo")
def kovadlina(cx, cy):
    anvil(cx, cy + 3, 1.15)
    for i, r in enumerate((14, 10)):
        stroke(ell(cx, cy - 9, r, r * 0.3, 24), 0.8, closed=True, g=K("#ffd070", 0.85), alpha=0.7)


@sk("vyhen")
def rozpalene_zelezo(cx, cy):
    glow(cx, cy, 14, "#ff8a2a", 0.6)
    hammer(cx, cy, 1.0, rot=-45)
    flame(cx + 6, cy + 4, 9)


@sk("vyhen")
def jiskry(cx, cy):
    for i in range(12):
        a = math.radians(-30 + i * 6)
        x, y = cx - 12 + math.cos(a) * (8 + i * 1.6), cy + math.sin(a) * (8 + i * 1.6)
        sparkle(x, y, 1.2 + (i % 3) * 0.5, "#ffd060")
    hammer(cx - 9, cy - 2, 0.7, rot=-20)


@sk("vyhen")
def vyhen(cx, cy):
    form(rect(cx - 12, cy - 13, 24, 9), K("#5a4a42", 0.3), W, sh=0.2)
    flame_big(cx, cy - 4, 18)
    flame(cx - 7, cy - 4, 9); flame(cx + 7, cy - 4, 9)


@sk("vyhen")
def struska(cx, cy):
    for k in range(4):
        x = cx - 12 + k * 8
        flame(x, cy - 8, 10 + (k % 2) * 4)
    flat(rect(cx - 14, cy - 12, 28, 4), "#ff6a1a", 0.8)


@sk("kovani")
def kovana_kuze(cx, cy):
    sh_ = [(cx - 10, cy + 12), (cx + 10, cy + 12), (cx + 10, cy - 2)] + bez((cx + 10, cy - 2), (cx + 8, cy - 10), (cx, cy - 14), (cx - 10, cy - 2))
    form(sh_, STEEL, W, sh=0.25)
    for (x, y) in ((-6, 8), (6, 8), (-6, -2), (6, -2)):
        rivet(cx + x, cy + y, 1.1)


@sk("kovani")
def zelezny_strazce(cx, cy):
    golem(cx, cy, 0.95, "#9aa4b0")


@sk("kovani")
def kalena_ocel(cx, cy):
    kovana_kuze(cx, cy)
    for i in range(3):
        line([(cx - 6 + i * 5, cy - 14), (cx - 4 + i * 5, cy - 9)], "#9fe0ff", 1.0, 0.8)


@sk("kovani")
def kovarova_vydrz(cx, cy):
    anvil(cx, cy - 4, 0.9)
    glow(cx, cy + 4, 12, "#86e05a", 0.35)
    shape([(cx - 3, cy + 6), (cx + 3, cy + 6), (cx + 3, cy + 9), (cx + 6, cy + 9), (cx + 6, cy + 15), (cx + 3, cy + 15), (cx + 3, cy + 18), (cx - 3, cy + 18), (cx - 3, cy + 15), (cx - 6, cy + 15), (cx - 6, cy + 9), (cx - 3, cy + 9)], K("#e8e2d4", 0.9), W * 0.6)


# ------------------------------------------------------------------ ŽREC
@sk("modly")
def svantovituv_zrak(cx, cy):
    idol(cx, cy, 1.0, 4)
    for sx in (-1, 1):
        rays(cx + sx * 9, cy + 6, 1, 5, 3, "#fff0a0", 0.7, 0.8, 70 if sx > 0 else 250)


@sk("modly")
def triglavova_zastita(cx, cy):
    for dx in (-8, 0, 8):
        shape(ell(cx + dx, cy + 6, 3.6, 4.2, 16), K("#d8c8a0", 0.85), W * 0.7)
    form(rect(cx - 11, cy - 13, 22, 16), WOOD, W, sh=0.2)
    glow(cx, cy, 14, "#f0d070", 0.3)


@sk("modly")
def hnev_modly(cx, cy):
    idol(cx, cy - 2, 0.85, 3)
    lightning(zig(cx + 8, cy + 15, cx + 3, cy + 2, 4, 2.6, 3), 1.8)


@sk("modly")
def perunova_prizen(cx, cy):
    bigbolt(cx, cy, 1.0)
    glow(cx, cy + 10, 6, "#ffe7a0", 0.6)


@sk("obet")
def krvava_obet(cx, cy):
    with T(cx, cy, 1.0, rot=-40):
        form([(-1.4, -14), (1.4, -14), (1.4, 8), (0, 12), (-1.4, 8)], STEEL, W * 0.8, sh=0.2)
        shape(rect(-5, -14, 10, 2.2), BRASS, W * 0.6)
    blood(cx + 7, cy - 8, 3.5)


@sk("obet")
def obetni_ohen(cx, cy):
    stroke(ell(cx, cy - 6, 13, 4, 24), 1.0, closed=True, g=K("#ff7a30", 0.7))
    flame_big(cx, cy - 6, 16)
    blood(cx, cy - 10, 2.4)


@sk("obet")
def krev_za_krev(cx, cy):
    blood(cx - 5, cy, 4.5)
    blood(cx + 5, cy, 4.5)
    swoosh(cx, cy, 13, 200, 340, "#ff8080", 1.6)


@sk("obet")
def velka_obet(cx, cy):
    form(rect(cx - 12, cy - 14, 24, 7), K("#6a6260", 0.4), W, sh=0.25)
    flame_big(cx, cy - 7, 20)
    blood(cx, cy + 9, 3.2)


@sk("dedkove")
def dedek(cx, cy):
    ghost(cx, cy, 1.0)
    shape(bez((cx - 4, cy - 2), (cx - 4, cy - 9), (cx + 4, cy - 9), (cx + 4, cy - 2)), K("#f2f2f2", 0.95), W * 0.4)


@sk("dedkove")
def hlas_predku(cx, cy):
    ghost(cx - 6, cy + 2, 0.7)
    ghost(cx + 6, cy + 2, 0.7)
    for i in range(3):
        stroke(ell(cx, cy + 4, 4 + i * 4, 3 + i * 3, 20, 300, 420), 0.7, g=K("#bfe0ff", 0.9), alpha=0.7)


@sk("dedkove")
def babky(cx, cy):
    for dx in (-8, 0, 8):
        ghost(cx + dx, cy - 1, 0.55, "#e8f2ff")
    snowflake(cx, cy + 11, 3.5)


@sk("dedkove")
def rod(cx, cy):
    tube([(cx, cy - 14), (cx, cy + 2)], 3, 2.2, WOOD, W * 0.6, sh=0)
    for (dx, dy, r) in ((-7, 4, 5), (7, 4, 5), (0, 9, 6)):
        form(ell(cx + dx, cy + dy, r, r * 0.85, 18), K("#5d7a3a", 0.42), W * 0.7, sh=0.2)
    roots(cx, cy - 13, 0.6)


# ------------------------------------------------------------------ VLKODLAK
@sk("promena")
def vlci_kuze(cx, cy):
    ghost(cx - 5, cy - 3, 0.6, "#e8d8c0")
    wolf_head(cx + 4, cy + 1, 0.85)


@sk("promena")
def kousnuti(cx, cy):
    for sx in (-1, 1):
        for k in range(4):
            x = cx - 8 + k * 5.3
            shape([(x, cy + sx * 3), (x + 2.4, cy + sx * 3), (x + 1.2, cy + sx * 9)], K("#f2ece0", 0.95), W * 0.5)
    blood(cx, cy - 12, 2.2)


@sk("promena")
def vyti(cx, cy):
    wolf_head(cx - 3, cy - 2, 0.8)
    for i in range(3):
        stroke(ell(cx + 4, cy + 8, 4 + i * 3.5, 4 + i * 3.5, 16, 10, 80), 0.9, g=K("#e8e2d4", 0.9), alpha=0.8)


@sk("promena")
def besneni(cx, cy):
    glow(cx, cy, 14, "#e04050", 0.4)
    claw(cx, cy, "#ff8080")


@sk("smecka")
def vlk(cx, cy):
    wolf_head(cx, cy, 1.0)


@sk("smecka")
def smecka(cx, cy):
    wolf_head(cx - 7, cy - 4, 0.6, "#a8a49e")
    wolf_head(cx + 7, cy - 4, 0.6, "#a8a49e")
    wolf_head(cx, cy + 3, 0.7)


@sk("smecka")
def vudce_smecky(cx, cy):
    wolf_head(cx, cy - 2, 0.85)
    shape([(cx - 6, cy + 9), (cx - 4, cy + 14), (cx, cy + 10), (cx + 4, cy + 14), (cx + 6, cy + 9)], GOLD, W * 0.6)


@sk("smecka")
def vlkodlaci_bratr(cx, cy):
    glow(cx, cy, 13, "#c8b8a0", 0.35)
    wolf_head(cx, cy, 1.1, "#5a5650")
    claw(cx + 2, cy - 2, "#e8e2d4")


@sk("les")
def trni(cx, cy):
    thorns(cx, cy, 1.0)


@sk("les")
def koreny(cx, cy):
    roots(cx, cy + 8, 1.1)
    glow(cx, cy, 10, "#86c050", 0.3)


@sk("les")
def lesni_duch(cx, cy):
    ghost(cx, cy, 0.95, "#c8f0a8")
    for (dx, dy) in ((-6, 9), (6, 9), (0, 12)):
        shape(ell(cx + dx, cy + dy, 2.4, 1.2, 10, rot=30), K("#5d7a3a", 0.45), W * 0.4)


@sk("les")
def hnev_lesa(cx, cy):
    thorns(cx, cy + 4, 1.0)
    thorns(cx, cy - 6, 0.8)
    glow(cx, cy, 12, "#86e05a", 0.3)


# ------------------------------------------------------------------ ALCHYMISTKA
@sk("lucavka")
def lucavka(cx, cy):
    flask(cx, cy + 2, 1.0, "#86e05a")


@sk("lucavka")
def jedovaty_dym(cx, cy):
    fog(cx, cy + 4, "#a8e08a")
    flask(cx, cy - 6, 0.6, "#86e05a")


@sk("lucavka")
def kyselina(cx, cy):
    flat(ell(cx, cy - 8, 13, 4, 22), "#86e05a", 0.75)
    for (dx, dy) in ((-4, -6), (3, -5), (7, -8)):
        stroke(ell(cx + dx, cy + dy, 1.5, 1.5, 10), 0.5, closed=True, g=K("#d8ffc0", 0.95))
    flask(cx + 2, cy + 6, 0.55, "#86e05a", False)


@sk("lucavka")
def kralovska_lucavka(cx, cy):
    flask(cx, cy + 2, 1.05, "#f2c040")
    rays(cx, cy - 1, 9, 14, 10, "#f2e0a0", 0.7, 0.8)


@sk("golem")
def hlineny_golem(cx, cy):
    golem(cx, cy, 0.95, "#a8865a")


@sk("golem")
def rtutovy_golem(cx, cy):
    golem(cx, cy, 0.9, "#c8d0dc")
    snowflake(cx + 10, cy + 10, 3)


@sk("golem")
def sem(cx, cy):
    form(rrect(cx - 10, cy - 8, 20, 14, 2), K("#e8dcc0", 0.88), W, sh=0.2)
    for i in range(3):
        stroke([(cx - 6 + i * 6, cy + 3), (cx - 4 + i * 6, cy - 4)], 1.0, g=K("#2a2220", 0.15))
    glow(cx, cy, 12, "#ffd060", 0.25)


@sk("golem")
def prazsky_golem(cx, cy):
    golem(cx, cy - 1, 1.15, "#8a6a4a")
    shape([(cx - 3, cy - 14), (cx + 3, cy - 14), (cx + 1, cy - 11), (cx - 1, cy - 11)], GOLD, W * 0.4)


@sk("transmutace")
def zlata_strela(cx, cy):
    for i in range(4):
        line([(cx - 14 + i * 3, cy - 6 + i * 2), (cx + 2 + i * 3, cy + i * 2)], "#f2c040", 1.4, 0.4 + i * 0.15)
    coin(cx + 8, cy + 4, 5)


@sk("transmutace")
def rtut(cx, cy):
    d = bez((cx, cy + 12), (cx - 2, cy + 6), (cx - 8, cy + 1), (cx - 8, cy - 4)) + bez((cx - 8, cy - 4), (cx - 8, cy - 12), (cx + 8, cy - 12), (cx + 8, cy - 4)) + \
        bez((cx + 8, cy - 4), (cx + 8, cy + 1), (cx + 2, cy + 6), (cx, cy + 12))
    form(d, SILVER, W, sh=0.25)
    hl([(cx - 4, cy - 2), (cx - 3, cy + 3)], 1.0, 0.9)
    for i in range(3):
        line([(cx + 10, cy - 6 + i * 4), (cx + 15, cy - 6 + i * 4)], "#e8f2ff", 0.8, 0.7)


@sk("transmutace")
def kamen_mudrcu(cx, cy):
    glow(cx, cy, 14, "#e04050", 0.4)
    gem = [(cx, cy + 11), (cx + 9, cy + 3), (cx + 6, cy - 9), (cx - 6, cy - 9), (cx - 9, cy + 3)]
    form(gem, K("#a8182a", 0.3), W, sh=0.25)
    shape([(cx, cy + 5), (cx + 4, cy + 1), (cx + 2, cy - 5), (cx - 2, cy - 5), (cx - 4, cy + 1)], K("#e8606a", 0.6), W * 0.5)
    sparkle(cx + 5, cy + 6, 2.2)


@sk("transmutace")
def velke_dilo(cx, cy):
    coins(cx, cy - 2)
    rays(cx, cy + 5, 6, 14, 12, "#fff0a0", 0.9, 0.8)
    glow(cx, cy + 5, 8, "#ffffff", 0.5)


# ------------------------------------------------------------------ LOUTKÁŘKA
@sk("marionety")
def kasparek(cx, cy):
    puppet(cx, cy, 1.0, "#c8322e")
    shape([(cx - 3, cy + 7), (cx, cy + 12), (cx + 3, cy + 7)], K("#f2b030", 0.7), W * 0.5)


@sk("marionety")
def cert_na_niti(cx, cy):
    puppet(cx, cy, 1.0, "#3a2a2a", "#7a4a3a")
    for sx in (-1, 1):
        shape([(cx + sx * 2, cy + 7), (cx + sx * 4, cy + 11), (cx + sx * 1, cy + 8)], K("#e8dcc0", 0.9), W * 0.4)
    flame(cx + 9, cy - 10, 6)


@sk("marionety")
def loutkove_divadlo(cx, cy):
    form(rect(cx - 13, cy - 13, 26, 4), K("#7a2a2a", 0.3), W * 0.8, sh=0.2)
    shape(rect(cx - 13, cy + 9, 26, 3), K("#c8322e", 0.4), W * 0.6)
    for dx in (-7, 0, 7):
        puppet(cx + dx, cy - 2, 0.5)


@sk("marionety")
def obri_marioneta(cx, cy):
    puppet(cx, cy - 1, 1.2, "#8a6a4a")


@sk("dudy")
def chodska_pisen(cx, cy):
    bagpipe(cx - 2, cy - 2, 0.85)
    notes(cx + 4, cy + 7)


@sk("dudy")
def ukolebavka(cx, cy):
    shape(ell(cx - 4, cy + 4, 7, 7, 24), K("#e8f2ff", 0.95), W * 0.6)
    flat(ell(cx - 1, cy + 6, 6.5, 6.5, 24), TREES["dudy"][0], 1.0)
    notes(cx + 4, cy - 6, 2, "#bfe0ff")
    snowflake(cx + 8, cy + 8, 2.6)


@sk("dudy")
def dupak(cx, cy):
    for sx, rot in ((-1, -15), (1, 15)):
        with T(cx + sx * 5, cy - 4, 1.0, rot=rot):
            form([(-3, 0), (3, 0), (4, 8), (-4, 8)], K("#c8322e", 0.38), W * 0.7, sh=0.2)
            form([(-4, -4), (6, -4), (6, 0), (-4, 0)], BOOT if False else K("#2a2220", 0.15), W * 0.6, sh=0.2)
    notes(cx, cy + 9, 3)


@sk("dudy")
def hromove_dudy(cx, cy):
    bagpipe(cx - 3, cy - 3, 0.75)
    lightning(zig(cx + 6, cy + 14, cx + 11, cy - 4, 4, 2.4, 5), 1.6)


@sk("sibalstvi")
def klubko(cx, cy):
    shape(ell(cx, cy - 2, 9, 9, 24), K("#c8322e", 0.4), W)
    for a in range(0, 180, 30):
        stroke(ell(cx, cy - 2, 8.5, 3 + (a % 60) / 15, 20, a, a + 180), 0.5, g=K("#7a1a1a", 0.25))
    line(bez((cx + 7, cy - 6), (cx + 12, cy - 10), (cx + 8, cy - 14), (cx + 14, cy - 15)), "#c8322e", 0.9, 1.0)


@sk("sibalstvi")
def mlha(cx, cy):
    fog(cx, cy, "#e0d8f0")
    stroke([(cx - 13, cy - 13), (cx - 13, cy + 13)], 1.4, g=K("#7a2a2a", 0.3))
    stroke([(cx + 13, cy - 13), (cx + 13, cy + 13)], 1.4, g=K("#7a2a2a", 0.3))


@sk("sibalstvi")
def falesna_loutka(cx, cy):
    for dx, dy in ((-8, -3), (0, 2), (8, -3)):
        puppet(cx + dx, cy + dy, 0.45, "#e8dcc8")


@sk("sibalstvi")
def hrom_z_kulis(cx, cy):
    form(rect(cx - 13, cy - 13, 6, 26), K("#7a2a2a", 0.3), W * 0.7, sh=0.2)
    form(rect(cx + 7, cy - 13, 6, 26), K("#7a2a2a", 0.3), W * 0.7, sh=0.2)
    bigbolt(cx, cy, 0.8)


if __name__ == "__main__":
    common.run({"ui/skills": SKILLS})
