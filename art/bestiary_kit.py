import math
from lib import Col, ell, bez, rrect, resample, C
from style3 import (stroke, shape, form, fill, hatch, tube, cast_shadow, offset_shadow, dot, T, poly,
                    clip_fill, notch, LINE)
import common

FEET = common.FEET

BONE = Col(0.85, "#d8cba8")
BONE_FAR = Col(0.65, "#a89c80")
SOCKET = Col(0.15, "#3b3039")
SLATE = Col(0.45, "#69737e")
SLATE_D = Col(0.35, "#525b66")
MOSS = Col(0.5, "#71804a")
MOSS_D = Col(0.4, "#58653a")
RUST = Col(0.45, "#9c5c36")
RUST_D = Col(0.35, "#7a4630")
SOOT = Col(0.32, "#55505a")
SOOT_L = Col(0.42, "#6a6470")
VIOLET = Col(0.4, "#6e5b8e")
VIOLET_L = Col(0.55, "#9480b4")
COLD = Col(0.55, "#7f9eb9")
COLD_L = Col(0.78, "#bcd4e6")
LEATHER = Col(0.4, "#7c5b40")
LEATHER_D = Col(0.32, "#5f4532")
RAG = Col(0.45, "#706858")
RAG_D = Col(0.35, "#575146")
WOOD = Col(0.45, "#8a6741")
IRON = Col(0.55, "#868a90")
IRON_D = Col(0.42, "#676b72")
WHITE = Col(1.0, "#ffffff")
MOUTH_D = Col(0.2, "#5c2329")
RED = Col(0.4, "#b23a30")
TONGUE = Col(0.5, "#c9474d")
TOOTH = Col(0.95, "#f2ead6")
EYE_Y = Col(0.9, "#ffd84a")
EYE_G = Col(0.85, "#a8f25c")
EYE_R = Col(0.6, "#ff4636")
EYE_C = Col(0.9, "#b0f2ff")
EYE_V = Col(0.7, "#d48cff")
EMBER = Col(0.6, "#ec7a2c")
FLAME = Col(0.8, "#f6b93c")
FLAME_L = Col(0.95, "#fff0a0")


def chaikin(pts, it=2):
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out += [(a[0]*0.75+b[0]*0.25, a[1]*0.75+b[1]*0.25), (a[0]*0.25+b[0]*0.75, a[1]*0.25+b[1]*0.75)]
        out.append(pts[-1]); pts = out
    return pts


def ik(a, c, l1, l2, bend=1):
    dx, dy = c[0]-a[0], c[1]-a[1]
    d = max(abs(l1-l2)+0.01, min(math.hypot(dx, dy), l1+l2-0.01))
    base = math.atan2(dy, dx)
    al = math.acos(max(-1, min(1, (l1*l1+d*d-l2*l2)/(2*l1*d))))
    an = base + bend*al
    b = (a[0]+math.cos(an)*l1, a[1]+math.sin(an)*l1)
    bc = math.atan2(c[1]-b[1], c[0]-b[0])
    return a, b, (b[0]+math.cos(bc)*l2, b[1]+math.sin(bc)*l2)


def limb(a, c, l1, l2, w0, w1, g, bend=1, sh=0.12, lw=LINE):
    p = ik(a, c, l1, l2, bend)
    wm = (w0+w1)/2
    tube(chaikin(list(p)), w0, w1, g, lw=lw, sh=sh)
    return p


def bone(a, b, w, g=BONE, knob=True):
    tube([a, b], w, w*0.85, g, sh=0.1)
    if knob:
        for p, r in ((a, w*0.62), (b, w*0.55)):
            shape(ell(p[0], p[1], r, r, 12), g, LINE*0.8)


def glow(x, y, r, col, a=0.22, n=4, ry=None):
    ry = ry or r
    steps = 12
    for i in range(steps):
        k = 1 - i/steps
        fill(ell(x, y, r*k, ry*k, 32), col, a*0.3)


def eye(x, y, r, col=EYE_Y, halo=2.6):
    glow(x, y, r*halo, col, 0.25, 3)
    dot(x, y, r, col)
    dot(x+r*0.3, y+r*0.32, r*0.38, WHITE)


def claws(x, y, ang, n=3, l=3.5, spread=22, g=0.0, w=LINE*0.8, curl=1):
    for i in range(n):
        a = math.radians(ang + (i-(n-1)/2)*spread)
        p0 = (x, y); p1 = (x+math.cos(a)*l, y+math.sin(a)*l)
        a2 = a - curl*0.6
        p2 = (p1[0]+math.cos(a2)*l*0.4, p1[1]+math.sin(a2)*l*0.4)
        stroke([p0, p1, p2], w, g=g)


def strands(base, tips, g=0.0, w=LINE*0.5):
    for (a, b) in zip(base, tips):
        stroke(bez(a, (a[0]*0.7+b[0]*0.3, a[1]*0.4+b[1]*0.6), (a[0]*0.3+b[0]*0.7+0.6, a[1]*0.1+b[1]*0.9), b), w, g=g)


def swoosh(pts, w=2.4, col=WHITE, a=0.5):
    P = resample(pts, 0.8)
    n = len(P)
    left, right = [], []
    for i in range(n):
        p = P[max(0, i-1)]; q = P[min(n-1, i+1)]
        dx, dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx, dy) or 1
        ww = w*max(0.0, math.sin(math.pi*i/(n-1)))**0.7*(i/(n-1))**0.5
        left.append((P[i][0]-dy/L*ww, P[i][1]+dx/L*ww)); right.append((P[i][0]+dy/L*ww, P[i][1]-dx/L*ww))
    fill(left+list(reversed(right)), col, a)


def ground(b, rx, ry=None, dx=0):
    cast_shadow(b.w/2+dx, FEET, rx, ry or min(3.3, max(2.2, rx*0.17)))


def faint(b, rx, dx=0):
    e = ell(b.w/2+dx, FEET, rx, min(3.0, max(1.6, rx*0.16)), 30)
    fill(e, 0.0, 0.05)
    hatch(e, 1.8, 20, 0.4, 0.0, 0.3)


# Poses a drawing can take. A drawing that supports more than the old five sets fn.poses (e.g. = ALL);
# its pose argument is then e.g. "walk3" or "attack_f". walk..walk4 = contact, passing, contact, passing.
POSES = ("idle", "walk", "walk2", "windup", "attack")
POSES4 = ("idle", "walk", "walk2", "walk3", "walk4", "windup", "attack")
ALL = tuple(p + v for v in ("", "_f", "_b") for p in POSES4)


def view_of(pose):
    """"walk3_f" -> ("walk3", "f"); "idle" -> ("idle", "")"""
    if pose.endswith(("_f", "_b")): return pose[:-2], pose[-1]
    return pose, ""


def poses_of(fn):
    return getattr(fn, "poses", POSES)


def sprite(fn, pose, shadow=None, flyer=None, dx=0, lift=0, s=1.0):
    def draw(b):
        if shadow: ground(b, shadow, dx=dx)
        if flyer: faint(b, flyer, dx=dx)
        with T(b.w/2+dx, FEET+lift, s):
            fn(pose)
    return draw


def rot(pts, cx, cy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(cx+(x-cx)*c-(y-cy)*s, cy+(x-cx)*s+(y-cy)*c) for x, y in pts]


def mitt(x, y, ang, r, g, n=4, claw=None):
    with T(x, y, 1, rot=ang):
        palm = ell(r*0.5, 0, r*0.9, r*0.75, 16)
        shape(palm, g, LINE*0.8)
        for i in range(n):
            yy = (i-(n-1)/2)*r*0.42
            p = [(r*1.1, yy*0.9), (r*2.0, yy*1.25), (r*2.5, yy*1.15-r*0.25)]
            stroke(p, LINE*0.75)
            if claw is not None:
                stroke([(r*2.5, yy*1.15-r*0.25), (r*3.1, yy*1.1-r*0.8)], LINE*0.6, g=claw)


def bare_foot(f, g, l=6.5, w=LINE*0.9):
    x, y = f
    ft = bez((x-2.4, y+1.6), (x-3.4, y-2), (x+1, y-2.1), (x+l, y-1.9)) + \
         bez((x+l, y-1.9), (x+l+1.6, y-1.7), (x+l+1.1, y+0.3), (x+l-1.6, y+0.4)) + [(x+1.6, y+2.0)]
    shape(ft, g, w)


def clipped(clip, fn):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0); fn(); C.restoreState()


def drip(x, y, r=0.8, col=COLD_L):
    fill(bez((x, y+r*2.2), (x+r*0.3, y+r), (x+r, y), (x, y-r)) + bez((x, y-r), (x-r, y), (x-r*0.3, y+r), (x, y+r*2.2)), col)


def world(hip, lean, p):
    c, s = math.cos(math.radians(lean)), math.sin(math.radians(lean))
    return (hip[0]+p[0]*c-p[1]*s, hip[1]+p[0]*s+p[1]*c)



def ribbon(spine, w0, w1, wmid=None, notch_amp=0.0, every=4):
    P = resample(spine, 0.8); n = len(P)
    left, right = [], []
    for i in range(n):
        a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        t = i/(n-1)
        w = (w0+(w1-w0)*t) if wmid is None else (w0*(1-t)**2 + 2*wmid*t*(1-t) + w1*t*t)
        left.append((P[i][0]-dy/L*w/2, P[i][1]+dx/L*w/2)); right.append((P[i][0]+dy/L*w/2, P[i][1]-dx/L*w/2))
    pts = left + list(reversed(right))
    return notch(pts, notch_amp, every) if notch_amp else pts


def chain(path, link=2.4, g=IRON):
    P = resample(path, link*0.85)
    for i in range(len(P)-1):
        a, b = P[i], P[i+1]
        ang = math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
        m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
        if i % 2:
            stroke([(m[0]-math.cos(math.radians(ang))*link*0.55, m[1]-math.sin(math.radians(ang))*link*0.55),
                    (m[0]+math.cos(math.radians(ang))*link*0.55, m[1]+math.sin(math.radians(ang))*link*0.55)], LINE*1.0)
        else:
            e = ell(m[0], m[1], link*0.62, link*0.36, 14, rot=ang)
            fill(e, g); stroke(e, LINE*0.6, closed=True)


def leaf(x, y, ang, l=2.4, g=MOSS):
    with T(x, y, 1, rot=ang):
        p = bez((0, 0), (l*0.3, l*0.45), (l*0.8, l*0.35), (l, 0)) + bez((l, 0), (l*0.8, -l*0.35), (l*0.3, -l*0.45), (0, 0))
        shape(p, g, LINE*0.45)


def shaggy(pts, amp=1.6, every=3, side=1):
    P = resample(pts, 1.0); out = []
    n = len(P)
    for i in range(n):
        if i % every == every-1:
            a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
            dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
            nx, ny = -dy/L*side, dx/L*side
            out.append((P[i][0]+nx*amp*0.7, P[i][1]+ny*amp*0.7-amp*0.7))
        else:
            out.append(P[i])
    return out


def fur_strokes(clip, x0, x1, y0, y1, g, gap=3.2, l=3.0, seed=0):
    def go():
        k = seed
        y = y1
        row = 0
        while y > y0:
            x = x0 + (row % 2)*gap*0.5
            while x < x1:
                k = (k*1103515245 + 12345) & 0x7fffffff
                jx = (k % 100)/100*gap*0.6; jy = ((k >> 8) % 100)/100*gap*0.5
                px, py = x+jx, y-jy
                stroke(bez((px, py), (px-0.3, py-l*0.4), (px+0.2, py-l*0.7), (px-0.4, py-l)), LINE*0.4, g=g)
                x += gap
            y -= gap*1.1; row += 1
    clipped(clip, go)
