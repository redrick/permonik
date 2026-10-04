import math
import lib
from lib import Col, C, ell, bez, rrect
import style3 as S
from style3 import T, stroke, shape, form, fill, hatch, tube, offset_shadow, dot, poly, clip_fill
from reportlab.lib.colors import HexColor


def K(hex_, g=0.5, a=None): return Col(g, hex_, a)


IRON = K("#4a4e57", 0.35); IRON_D = K("#2c2f36", 0.2); IRON_L = K("#8d939e", 0.6)
STEEL = K("#9aa3ae", 0.65); STEEL_L = K("#d9dee4", 0.9); STEEL_D = K("#5d6570", 0.4)
RUST = K("#8a4a2a", 0.4); RUST_L = K("#b4673a", 0.5)
WOOD = K("#7a5232", 0.45); WOOD_L = K("#a8774a", 0.6); WOOD_D = K("#4e321e", 0.3)
LEATHER = K("#6b4429", 0.4); LEATHER_L = K("#93633e", 0.55); LEATHER_D = K("#40281a", 0.25)
BONE = K("#e3d8bd", 0.88); BONE_D = K("#b2a582", 0.7)
GOLD = K("#d9a630", 0.65); GOLD_L = K("#f6d878", 0.85); GOLD_D = K("#94691c", 0.45)
BRASS = K("#c09040", 0.6); BRASS_L = K("#ecc978", 0.8)
SILVER = K("#c4c9cf", 0.8); SILVER_L = K("#f2f4f6", 0.95); SILVER_D = K("#7f8791", 0.5)
CLOTH_W = K("#ece4d2", 0.92); CLOTH_W_D = K("#bfb49c", 0.75)
FLEECE = K("#e8dcc0", 0.9); FLEECE_D = K("#b9a681", 0.7)
RED = K("#a82a2a", 0.4); RED_L = K("#d8504a", 0.55); RED_D = K("#5e1418", 0.2)
BLUE = K("#2f5d9e", 0.4); BLUE_L = K("#79b4e8", 0.7)
GREEN = K("#3f6a3a", 0.4); MOSS = K("#5d7a3a", 0.45)
GLASS = K("#d6e6ea", 0.9, 0.35)
PARCH = K("#dcc89a", 0.85); PARCH_D = K("#a98e5c", 0.6)
INK = K("#2a2220", 0.1)
FLAME_Y = K("#ffd560", 0.9); FLAME_O = K("#f08a24", 0.65); FLAME_W = K("#fff6d0", 0.98)
COLD = K("#dff3ff", 0.97); COLD_B = K("#7cc4ff", 0.75)

W = 0.85


def glow(x, y, r, hex_, a=0.6, n=12, ry=None):
    ry = ry or r
    ai = 1 - (1 - a) ** (1.0 / n)
    C.saveState(); C.setFillColor(HexColor(hex_)); C.setFillAlpha(ai)
    for i in range(n):
        k = 1 - i / n
        C.drawPath(poly(ell(x, y, r * k, ry * k, 32)), fill=1, stroke=0)
    C.restoreState()


def flat(pts, hex_, a=1.0):
    C.saveState(); C.setFillColor(HexColor(hex_)); C.setFillAlpha(a)
    C.drawPath(poly(pts), fill=1, stroke=0); C.restoreState()


def line(pts, hex_, w=0.6, a=1.0):
    C.saveState(); C.setStrokeColor(HexColor(hex_)); C.setStrokeAlpha(a); C.setLineWidth(w / S._SC[-1])
    C.setLineCap(1); C.setLineJoin(1); C.drawPath(poly(pts, False), fill=0, stroke=1); C.restoreState()


def hl(pts, w=0.6, a=0.75, hex_="#ffffff"):
    stroke(pts, w, g=K(hex_, 1.0), alpha=a)


def shade(pts, a=0.25, ang=40, sp=1.3):
    hatch(pts, sp, ang, 0.35, 0.0, a)


def rect(x, y, w, h): return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def flame(x, y, h, cold=False, lean=0.0):
    wid = h * 0.42
    outer = bez((x, y), (x - wid, y + h * 0.15), (x - wid * 0.4, y + h * 0.65), (x + lean, y + h)) + \
        bez((x + lean, y + h), (x + wid * 0.5, y + h * 0.6), (x + wid, y + h * 0.15), (x, y))
    inner = bez((x, y + h * 0.06), (x - wid * 0.5, y + h * 0.2), (x - wid * 0.2, y + h * 0.5), (x + lean * 0.6, y + h * 0.7)) + \
        bez((x + lean * 0.6, y + h * 0.7), (x + wid * 0.3, y + h * 0.45), (x + wid * 0.5, y + h * 0.18), (x, y + h * 0.06))
    if cold:
        glow(x, y + h * 0.45, h * 1.3, "#9fd8ff", 0.55)
        flat(outer, "#a8dcff"); flat(inner, "#f4fbff")
    else:
        glow(x, y + h * 0.45, h * 1.3, "#ffb040", 0.5)
        flat(outer, "#f08a24"); flat(inner, "#ffe48a")
    stroke(outer, 0.45, closed=True, g=K("#6a2a10" if not cold else "#2a5a8a", 0.2), alpha=0.6)


def rivet(x, y, r=0.9, g=None):
    dot(x, y, r, g or IRON_D)
    dot(x - r * 0.3, y + r * 0.3, r * 0.4, K("#c9ced6", 0.8))


def coin(x, y, r, face=GOLD, rim=GOLD_D, tilt=1.0, mark=True):
    e = ell(x, y, r, r * tilt, 28)
    if tilt < 0.95:
        edge = [(px, py - r * 0.18) for px, py in ell(x, y, r, r * tilt, 28, 180, 360)]
        shape(ell(x, y - r * 0.09, r, r * tilt, 28), rim, W * 0.8)
    shape(e, face, W * 0.8)
    stroke(ell(x, y, r * 0.72, r * 0.72 * tilt, 24), 0.35, closed=True, g=rim, alpha=0.8)
    if mark:
        stroke([(x - r * 0.3, y - r * 0.25 * tilt), (x, y + r * 0.35 * tilt), (x + r * 0.3, y - r * 0.25 * tilt)], 0.45, g=rim)
    hl(ell(x, y, r * 0.8, r * 0.8 * tilt, 12, 100, 170), 0.5, 0.8)


def sparkle(x, y, r, hex_="#ffffff", a=0.95):
    pts = []
    for i in range(8):
        rr = r if i % 2 == 0 else r * 0.22
        ang = math.radians(90 + i * 45)
        pts.append((x + math.cos(ang) * rr, y + math.sin(ang) * rr))
    flat(pts, hex_, a)
