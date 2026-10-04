"""Clean 'ligne claire' style: uniform confident outlines, flat tones, crisp shadow shapes."""
import math, random
import lib
from lib import C, G, ell, bez, rrect, resample
import palette as P
from reportlab.lib.colors import white, black

# ------------------------------------------------------------------ scale-aware transforms
_SC = [1.0]
class T:
    def __init__(self, x, y, s=1.0, flip=False, rot=0):
        self.a = (x, y, s, flip, rot)
    def __enter__(self):
        x, y, s, flip, rot = self.a
        C.saveState(); C.translate(x, y); C.rotate(rot); C.scale(-s if flip else s, s)
        _SC.append(_SC[-1]*s)
    def __exit__(self, *e):
        _SC.pop(); C.restoreState()

def poly(pts, closed=True):
    p = C.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if closed: p.close()
    return p

def bbox(pts):
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

# ------------------------------------------------------------------ primitives
LINE = 1.15   # page-space outline weight for characters (pt)

_R = random.Random(21)
def _noise(n, amp, freqs=((1.0, 0.7), (2.6, 0.3)), step_pt=1.1, period_pt=45.0):
    ph = [_R.random()*6.28 for _ in freqs]
    return [amp*sum(a*math.sin((t*step_pt/period_pt)*f*6.28 + p) for (f, a), p in zip(freqs, ph)) for t in range(n)]

import osobni
_OS = osobni.stroke_params() if osobni.on("lines") else None
_OH = osobni.hatch_params() if osobni.on("hatch") else None

def graphite():
    """soft pencil grey instead of ink black; in the B&W comic a touch lighter than black"""
    from reportlab.lib.colors import HexColor, Color
    return HexColor("#2e2d33") if lib.MODE == "color" else Color(0.16, 0.16, 0.16)

HAND = True
def stroke(pts, w=LINE, closed=False, g=0.0, alpha=None, taper=True, end_heavy=False):
    """hand-inked stroke: gentle wobble, pressure variation, tapered ends, overlapping closures"""
    sc = _SC[-1]
    if _OS: w *= _OS["width_k"]
    if not HAND:
        C.saveState(); C.setStrokeColor(G(g)); C.setLineWidth(w/sc); C.setLineCap(1); C.setLineJoin(1)
        C.drawPath(poly(pts, closed), fill=0, stroke=1); C.restoreState(); return
    P = resample(list(pts), 1.1/sc, closed)
    if len(P) < 3:
        P = resample(list(pts), 0.3/sc, closed)
        if len(P) < 2: return
    if closed:
        k = _R.randrange(len(P))
        P = P[k:] + P[:k]
        ov = max(2, int(len(P)*0.05))
        P = P + P[:ov]
    n = len(P)
    if _OS:
        # táta's line: his wobble spectrum, a slight bow over the whole stroke, his pressure swing
        wob = _noise(n, _OS["wob_amp"]/sc, _OS["wob_freqs"], step_pt=1.1, period_pt=_OS["wob_period"])
        bow = _R.choice((-1, 1)) * _OS["bow"] * n * 1.1/sc
        wob = [v + bow*math.sin(math.pi*i/(n-1)) for i, v in enumerate(wob)] if not closed else wob
        prs = _noise(n, _OS["prs_amp"], ((1.4, 0.7), (3.3, 0.3)), period_pt=30.0)
    else:
        wob = _noise(n, 0.3/sc)
        prs = _noise(n, 0.28, ((1.4, 0.7), (3.3, 0.3)), period_pt=30.0)
    left, right, centre = [], [], []
    for i in range(n):
        a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy/L, dx/L
        t = i/(n-1)
        px, py = P[i][0]+nx*wob[i], P[i][1]+ny*wob[i]
        if taper or closed:
            tp = min(1.0, t/0.12, (1-t)/0.12) if n > 8 else 1.0
            floor = _OS["taper_floor"] if _OS else 0.25
            tp = floor + (1-floor)*math.sin(tp*math.pi/2)
        else:
            tp = 1.0
        if end_heavy: tp *= 0.45 + 0.75*t  # a hatch stroke pressed harder toward its end
        ww = (w/sc)*tp*(1.0+prs[i])/2
        left.append((px+nx*ww, py+ny*ww)); right.append((px-nx*ww, py-ny*ww))
        centre.append((px, py, nx, ny, ww))
    alpha = lib.alpha_for(g, alpha)
    pencil = osobni.on("pencil") and not isinstance(g, lib.Col) and g == 0.0
    col = graphite() if pencil else G(g)
    C.saveState(); C.setFillColor(col)
    if alpha is not None: C.setFillAlpha(alpha)
    elif pencil: C.setFillAlpha(0.88)
    C.drawPath(poly(left + list(reversed(right))), fill=1, stroke=0); C.restoreState()
    if pencil and n > 12 and _R.random() < 0.55:
        # drawn over a second time: thinner, a hair off the first line, over part of its length
        i0 = int(n*_R.uniform(0.0, 0.3)); i1 = int(n*_R.uniform(0.7, 1.0))
        off = _R.choice((-1, 1))*_R.uniform(0.25, 0.55)/sc
        seg = centre[i0:i1]
        if len(seg) > 3:
            L2 = [(x+nx*(off+ww*0.45), y+ny*(off+ww*0.45)) for x, y, nx, ny, ww in seg]
            R2 = [(x+nx*(off-ww*0.45), y+ny*(off-ww*0.45)) for x, y, nx, ny, ww in seg]
            C.saveState(); C.setFillColor(graphite()); C.setFillAlpha(0.45 if alpha is None else alpha*0.5)
            C.drawPath(poly(L2 + list(reversed(R2))), fill=1, stroke=0); C.restoreState()

def hatch(clip, spacing=1.6, ang=45, lw=0.45, g=0.0, alpha=0.85, wob=True):
    """hand hatching inside clip (spacing, lw in page pt)"""
    sc = _SC[-1]
    if _OH: spacing *= _OH["spacing_k"]
    x0, y0, x1, y1 = bbox(clip)
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0)
    L = math.hypot(x1-x0, y1-y0)
    cx, cy = (x0+x1)/2, (y0+y1)/2
    dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    k = -L/2; i = 0
    while k < L/2:
        ox, oy = cx - dy*k, cy + dx*k
        j = (_R.random()-0.5)*spacing/sc*0.4
        stroke([(ox-dx*L/2+j, oy-dy*L/2), (ox+dx*L/2, oy+dy*L/2+j)], lw, g=g, alpha=alpha,
               end_heavy=bool(_OH and _OH["end_heavy"]))
        k += spacing/sc; i += 1
    C.restoreState()

def fill(pts, g, alpha=None):
    alpha = lib.alpha_for(g, alpha)
    if alpha is None and osobni.on("crayon") and crayon_fill(pts, g): return
    C.saveState(); C.setFillColor(G(g))
    if alpha is not None: C.setFillAlpha(alpha)
    C.drawPath(poly(pts), fill=1, stroke=0); C.restoreState()


def crayon_fill(pts, g):
    """coloured in by hand: a pale wash of the colour, then real crayon strokes in full colour on top.
    Very light (paper-like) and very dark (ink) areas stay flat."""
    col = G(g)
    rgb = (col.red, col.green, col.blue)
    lum = 0.3*rgb[0] + 0.59*rgb[1] + 0.11*rgb[2]
    if lum > 0.97 or lum < 0.12: return False
    x0, y0, x1, y1 = bbox(pts)
    sc = _SC[-1]
    if (x1-x0)*sc < 3 or (y1-y0)*sc < 3: return False  # buttons, dots: too small to show strokes
    bw = lib.MODE == "bw"
    tile = osobni.crayon_tile(rgb, int(abs(hash((round(x0), round(y0))))) % 997, bw)
    if tile is None: return False
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
    # the paper showing through the strokes, tinted; a dark colour is pressed in hard, so little paper shows
    wash = tuple(c + (1-c)*0.55*min(1.0, lum/0.5) for c in rgb)
    C.setFillColorRGB(*wash); C.drawPath(poly(pts), fill=1, stroke=0)
    t = osobni.TILE_MM*72/25.4/sc
    C.translate((x0+x1)/2, (y0+y1)/2); C.rotate(_R.uniform(-25, 25))
    r = math.hypot(x1-x0, y1-y0)/2 + t
    ty = -r
    while ty < r:
        tx = -r
        while tx < r:
            C.drawImage(tile, tx, ty, t, t, mask="auto"); tx += t
        ty += t
    C.restoreState()
    return True

def shape(pts, g, w=LINE, shadow=None):
    """flat fill; optional crisp shadow shape clipped inside; outline"""
    if HAND and g < 0.98:
        sc = _SC[-1]; ox, oy = 0.28/sc, -0.22/sc
        fill([(x+ox, y+oy) for x, y in pts], g)
    else:
        fill(pts, g)
    if shadow is not None:
        sh_pts, sh_g = shadow
        C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0); fill(sh_pts, sh_g); C.restoreState()
    if w: stroke(pts, w, closed=True)

def clip_fill(clip, pts, g, alpha=None):
    C.saveState(); C.clipPath(poly(clip), stroke=0, fill=0); fill(pts, g, alpha); C.restoreState()

def offset_shadow(pts, dx, dy, g_delta=0.12, base=None):
    """crisp shadow: part of shape NOT covered by a shifted copy"""
    x0, y0, x1, y1 = bbox(pts)
    C.saveState(); C.clipPath(poly(pts), stroke=0, fill=0)
    p = C.beginPath(); p.rect(x0-100, y0-100, x1-x0+200, y1-y0+200)
    sh = [(x+dx, y+dy) for x, y in pts]
    p.moveTo(*sh[0])
    for q in sh[1:]: p.lineTo(*q)
    p.close()
    C.setFillColor(black); C.setFillAlpha(g_delta)
    C.drawPath(p, fill=1, stroke=0, fillMode=0); C.restoreState()

def form(pts, g, w=LINE, sdx=-1.4, sdy=1.2, sh=0.13):
    if HAND and g < 0.98:
        sc = _SC[-1]; fill([(x+0.28/sc, y-0.22/sc) for x, y in pts], g)
    else:
        fill(pts, g)
    if sh: offset_shadow(pts, sdx, sdy, sh)
    if w: stroke(pts, w, closed=True)

def dot(x, y, r, g=0.0):
    C.saveState(); C.setFillColor(G(g)); C.circle(x, y, r, fill=1, stroke=0); C.restoreState()

def cast_shadow(x, y, rx, ry, g=0.0, a=0.16):
    e = ell(x, y, rx, ry, 30)
    fill(e, 0.0, 0.07)
    hatch(e, 1.5, 20, 0.45, 0.0, 0.6)

def tube(pts, w0, w1, g, lw=LINE, cap=True, sh=0.12):
    P = resample(pts, 0.6)
    n = len(P); left, right = [], []
    for i in range(n):
        a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        w = (w0 + (w1-w0)*i/(n-1))/2
        left.append((P[i][0]-dy/L*w, P[i][1]+dx/L*w)); right.append((P[i][0]+dy/L*w, P[i][1]-dx/L*w))
    a2 = math.degrees(math.atan2(P[-1][1]-P[-2][1], P[-1][0]-P[-2][0]))
    a1 = math.degrees(math.atan2(P[1][1]-P[0][1], P[1][0]-P[0][0]))
    cap1 = ell(P[-1][0], P[-1][1], w1/2, w1/2, 10, a2-90, a2+90)
    cap0 = ell(P[0][0], P[0][1], w0/2, w0/2, 10, a1+90, a1+270)
    outline = left + cap1 + list(reversed(right)) + cap0
    fill(outline, g)
    if sh: offset_shadow(outline, -w0*0.3, w0*0.12, sh)
    stroke(left, lw); stroke(right, lw)
    if cap: stroke(cap1, lw)
    return outline

# ------------------------------------------------------------------ hands, props
def hand(x, y, ang, r=2.2):
    with T(x, y, 1, rot=ang+90):
        palm = bez((-r*0.8, r*0.3), (-r, -r*0.8), (-r*0.8, -r*1.9), (0, -r*2.0)) + bez((0, -r*2.0), (r*0.8, -r*1.9), (r, -r*0.8), (r*0.8, r*0.3))
        shape(palm, P.SKIN, LINE*0.9)
        stroke(bez((r*0.75, -r*0.2), (r*1.5, -r*0.3), (r*1.6, -r*1.1), (r*1.0, -r*1.3)), LINE*0.8)

def magnifier(x, y, ang=35, r=5.0):
    with T(x, y, rot=ang):
        tube([(0, -r-0.6), (0, -r-9.5)], 2.3, 2.1, P.MAGNIFIER_HANDLE)
        shape(ell(0, 0, r+1.2, r+1.2, 40), P.MAGNIFIER_RIM)
        shape(ell(0, 0, r, r, 40), P.GLASS)
        stroke(ell(0, 0, r*0.68, r*0.68, 16, 110, 165), LINE*1.3, g=1.0)

def notebook(x, y, s=1.0, drawing=False):
    with T(x, y, s):
        shape(rrect(-7.5, -5.4, 15, 10.8, 1), P.NOTEBOOK_COVER)
        for side in (-1, 1):
            pg = rrect(-7 if side < 0 else 0.2, -4.7, 6.8, 9.5, 0.5)
            shape(pg, 1.0, LINE*0.6)
            if drawing and side > 0:
                stroke(ell(3.6, 0, 1.8, 1.8, 14), LINE*0.5, closed=True)
                for a in range(0, 360, 60):
                    stroke([(3.6+math.cos(math.radians(a))*2.3, math.sin(math.radians(a))*2.3),
                            (3.6+math.cos(math.radians(a))*3.0, math.sin(math.radians(a))*3.0)], LINE*0.4)
            else:
                for k in range(4):
                    xo = -6.2 if side < 0 else 1.0
                    stroke([(xo, 2.6-k*2.0), (xo+5.2, 2.6-k*2.0)], LINE*0.3, g=P.NOTEBOOK_LINE)

# ------------------------------------------------------------------ faces
def hand_face(cx, cy, r, mood):
    """táta's drawn expression, scaled into the head circle; False when there is none for this mood"""
    polys = osobni.FACES.get(osobni.FACE_FOR.get(mood, "happy")) if osobni.on("faces") else None
    if not polys: return False
    p = C.beginPath()
    for pl in polys:
        pts = [(cx + x*r, cy + y*r) for x, y in pl["pts"]]
        p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.close()
    C.saveState(); C.setFillColor(black)
    C.drawPath(p, fill=1, stroke=0, fillMode=0)  # even-odd: an eye drawn as a ring keeps its white
    C.restoreState()
    return True


def face(cx, cy, r, mood="happy", look=(0, 0), young=False, freckles=False):
    if hand_face(cx, cy, r, mood):
        if young:
            for s in (-1, 1):
                fill(ell(cx+s*r*0.6, cy-r*0.33, r*0.16, r*0.1, 16), P.BLUSH, 0.07)
        return
    ex = r*0.40 if not young else r*0.42
    ey = cy - r*0.02 if not young else cy - r*0.12
    erx, ery = r*0.095, r*0.135
    if young: erx, ery = r*0.105, r*0.14
    lx, ly = look[0]*r*0.04, look[1]*r*0.03
    for s in (-1, 1):
        x = cx + s*ex
        if mood in ("closed", "sleepy"):
            stroke(bez((x-erx*1.4, ey), (x-erx*0.5, ey-ery*0.8), (x+erx*0.5, ey-ery*0.8), (x+erx*1.4, ey)), LINE*0.9)
            continue
        k = 1.25 if mood in ("surprised", "wow") else 1.0
        if mood in ("grin", "laugh"):
            stroke(bez((x-erx*1.4, ey-ery*0.3), (x-erx*0.6, ey+ery*0.9), (x+erx*0.6, ey+ery*0.9), (x+erx*1.4, ey-ery*0.3)), LINE*1.2)
            continue
        C.saveState(); C.setFillColor(black)
        C.ellipse(x+lx-erx*k, ey+ly-ery*k, x+lx+erx*k, ey+ly+ery*k, fill=1, stroke=0); C.restoreState()
        dot(x+lx+erx*0.35, ey+ly+ery*0.4, erx*0.38, 1.0)
    # brows
    by = ey + r*(0.32 if not young else 0.3)
    bw = r*0.17
    for s in (-1, 1):
        x = cx + s*ex
        if mood in ("surprised", "wow"):
            pts = bez((x-bw, by+r*0.06), (x-bw*0.3, by+r*0.14), (x+bw*0.3, by+r*0.14), (x+bw, by+r*0.06))
        elif mood == "determined":
            pts = [(x-s*bw, by+r*0.05), (x+s*bw, by-r*0.03)]
        elif mood in ("worried", "sad", "think"):
            pts = [(x-s*bw, by-r*0.02), (x+s*bw, by+r*0.07)]
        else:
            pts = bez((x-bw, by), (x-bw*0.3, by+r*0.06), (x+bw*0.3, by+r*0.06), (x+bw, by))
        stroke(pts, LINE*0.85)
    # nose
    ny = ey - r*(0.3 if not young else 0.26)
    if young:
        stroke(bez((cx-r*0.07, ny+r*0.02), (cx-r*0.02, ny-r*0.05), (cx+r*0.05, ny-r*0.05), (cx+r*0.09, ny+r*0.02)), LINE*0.75)
    else:
        stroke(bez((cx+r*0.05, ey-r*0.1), (cx+r*0.12, ny), (cx+r*0.06, ny-r*0.06), (cx-r*0.05, ny-r*0.04)), LINE*0.75)
    # mouth
    my = ey - r*(0.52 if not young else 0.48)
    mw = r*0.2
    if mood in ("happy", "determined", "calm"):
        stroke(bez((cx-mw, my+r*0.03), (cx-mw*0.4, my-r*0.07), (cx+mw*0.4, my-r*0.07), (cx+mw, my+r*0.03)), LINE*0.85)
    elif mood in ("grin", "laugh"):
        m = bez((cx-mw*1.2, my+r*0.04), (cx-mw*0.6, my-r*0.24), (cx+mw*0.6, my-r*0.24), (cx+mw*1.2, my+r*0.04)) + [(cx-mw*1.2, my+r*0.04)]
        shape(m, P.MOUTH, LINE*0.85)
        clip_fill(m, ell(cx, my-r*0.2, mw*0.6, r*0.08, 12), P.TONGUE)
    elif mood in ("surprised", "wow"):
        shape(ell(cx, my-r*0.04, r*0.08, r*0.11, 16), P.MOUTH, LINE*0.8)
    elif mood == "whisper":
        shape(ell(cx, my, r*0.05, r*0.06, 12), P.MOUTH, LINE*0.7)
    elif mood == "think":
        stroke(bez((cx-mw*0.6, my), (cx, my-r*0.02), (cx+mw*0.4, my+r*0.01), (cx+mw*0.8, my+r*0.05)), LINE*0.85)
    elif mood == "talk":
        shape(ell(cx, my-r*0.03, r*0.12, r*0.085, 16), P.MOUTH, LINE*0.8)
        clip_fill(ell(cx, my-r*0.03, r*0.12, r*0.085, 16), ell(cx, my-r*0.09, r*0.08, r*0.04, 12), P.TONGUE)
    elif mood in ("sad", "worried"):
        stroke(bez((cx-mw*0.8, my-r*0.04), (cx-mw*0.3, my+r*0.03), (cx+mw*0.3, my+r*0.03), (cx+mw*0.8, my-r*0.04)), LINE*0.85)
    else:
        stroke([(cx-mw*0.6, my), (cx+mw*0.6, my)], LINE*0.85)
    if young:
        for s in (-1, 1):
            fill(ell(cx+s*r*0.6, ey-r*0.33, r*0.16, r*0.1, 16), P.BLUSH, 0.07)
    if freckles:
        for s in (-1, 1):
            for dx, dy in ((-0.08, 0.02), (0.03, 0.06), (0.1, -0.02), (0.0, -0.05)):
                dot(cx+s*(r*0.52+dx*r), ey-r*0.25+dy*r, r*0.02, P.FRECKLE)

# ------------------------------------------------------------------ bodies
class Kid:
    """param set for a child figure (units: older child height = 100)"""
    def __init__(self, young):
        self.young = young
        if young:
            self.H = 80; self.hr = 9.6; self.hy = 70.2
            self.sh_y = 57.5; self.sh_w = 8.3; self.hip = 31; self.knee = 16; self.ankle = 4.5
            self.leg_w = (6.0, 4.6); self.arm_w = (5.2, 4.6); self.up = 11.5; self.fo = 11.5
        else:
            self.H = 100; self.hr = 9.8; self.hy = 89.8
            self.sh_y = 76; self.sh_w = 9.6; self.hip = 45; self.knee = 24; self.ankle = 5
            self.leg_w = (6.0, 4.4); self.arm_w = (5.4, 4.6); self.up = 15; self.fo = 14

POSES = {  # (upper arm angle, forearm angle) in degrees, measured from +x (right side arm; mirrored for left)
    "down":  (-80, -85),
    "wave":  (-10, 80),
    "up":    (70, 85),
    "lens":  (-55, 25),
    "point": (-15, 5),
    "hip":   (-60, -170),
    "front": (-75, 170),
    "chin":  (-75, 120),
    "hush":  (-72, 118),
    "hold":  (-60, -5),
    "hug":   (-80, 160),
    "back":  (-100, -110),
}

IK = {"chin": (3.0, -0.95), "hush": (1.2, -0.52), "cheek": (6.0, -0.5)}
def arm_pts(k, side, pose):
    if pose in IK:
        tx, ty = IK[pose]
        S = (side*k.sh_w, k.sh_y - 1.5); P = (side*tx, k.hy + ty*k.hr)
        a, b = k.up, k.fo
        dx, dy = P[0]-S[0], P[1]-S[1]; d = min(math.hypot(dx, dy), a+b-0.5); d = max(d, abs(a-b)+0.5)
        base = math.atan2(dy, dx); al = math.acos((a*a+d*d-b*b)/(2*a*d))
        best = None
        for sg in (-1, 1):
            E = (S[0]+math.cos(base+sg*al)*a, S[1]+math.sin(base+sg*al)*a)
            score = 0.3*side*E[0] - E[1]
            if best is None or score > best[0]: best = (score, E)
        E = best[1]
        fa = math.degrees(math.atan2(P[1]-E[1], P[0]-E[0]))
        Hh = (E[0]+math.cos(math.radians(fa))*b, E[1]+math.sin(math.radians(fa))*b)
        return S, E, Hh, fa
    ua, fa = POSES[pose]
    if side < 0: ua, fa = 180-ua, 180-fa
    sx, sy = side*k.sh_w, k.sh_y - 1.5
    ex, ey = sx + math.cos(math.radians(ua))*k.up, sy + math.sin(math.radians(ua))*k.up
    hx, hy = ex + math.cos(math.radians(fa))*k.fo, ey + math.sin(math.radians(fa))*k.fo
    return (sx, sy), (ex, ey), (hx, hy), fa

def draw_arm(k, side, pose, sleeve_g, cuff_g=None):
    s, e, h, fa = arm_pts(k, side, pose)
    tube([s, e], k.arm_w[0], k.arm_w[0]*0.95, sleeve_g)
    # forearm sleeve ends a bit before hand
    fx, fy = h[0]-math.cos(math.radians(fa))*2.2, h[1]-math.sin(math.radians(fa))*2.2
    tube([e, (fx, fy)], k.arm_w[0]*0.95, k.arm_w[1], sleeve_g)
    if cuff_g is not None:
        cx, cy = fx-math.cos(math.radians(fa))*1.0, fy-math.sin(math.radians(fa))*1.0
        tube([(cx, cy), (fx, fy)], k.arm_w[1]+0.4, k.arm_w[1]+0.4, cuff_g, sh=0)
    hand(h[0], h[1], fa, 2.1 if k.young else 2.3)
    return h, fa

def draw_legs(k, pose, leg_g, stripes=False, boots=0.3, boot_top=None):
    if pose == "walk":
        pts = [[(-3.8, k.hip), (-5.5, k.knee), (-9, k.ankle+1.5)], [(3.8, k.hip), (6.5, k.knee+0.5), (7.2, k.ankle)]]
    else:
        pts = [[(-3.8, k.hip), (-4.0, k.knee), (-4.2, k.ankle)], [(3.8, k.hip), (4.0, k.knee), (4.2, k.ankle)]]
    for leg in pts:
        o = tube(leg, k.leg_w[0], k.leg_w[1], leg_g)
        if stripes:
            C.saveState(); C.clipPath(poly(o), stroke=0, fill=0)
            for j in range(12):
                yy = k.ankle + j*3.4
                fill([(-20, yy), (20, yy), (20, yy+1.6), (-20, yy+1.6)], P.TIGHTS_STRIPE)
            C.restoreState()
            stroke(o, LINE, closed=True)
    bt = boot_top if boot_top is not None else k.ankle + (7 if not k.young else 5.5)
    for leg in pts:
        ax, ay = leg[-1]
        b = [(ax-3.0, bt), (ax+3.0, bt)] + bez((ax+3.0, bt), (ax+3.1, ay), (ax+3.5, 2.2), (ax+6.8, 2)) + \
            bez((ax+6.8, 2), (ax+7.6, 1.8), (ax+7.4, 0), (ax+6.5, 0)) + [(ax-3.2, 0)] + bez((ax-3.2, 0), (ax-3.6, 1), (ax-3.2, ay), (ax-3.0, bt))
        form(b, boots, sh=0.12)
        stroke([(ax-3.3, 1.3), (ax+7.1, 1.3)], LINE*0.7)
        stroke([(ax-3.0, bt-1.2), (ax+3.0, bt-1.2)], LINE*0.6)

def head_outline(k):
    r = k.hr; cy = k.hy
    if k.young:
        return bez((0, cy+r), (r*0.75, cy+r), (r*1.02, cy+r*0.45), (r*1.02, cy-r*0.05)) + \
               bez((r*1.02, cy-r*0.05), (r*1.02, cy-r*0.65), (r*0.6, cy-r*0.98), (0, cy-r*0.98)) + \
               bez((0, cy-r*0.98), (-r*0.6, cy-r*0.98), (-r*1.02, cy-r*0.65), (-r*1.02, cy-r*0.05)) + \
               bez((-r*1.02, cy-r*0.05), (-r*1.02, cy+r*0.45), (-r*0.75, cy+r), (0, cy+r))
    return bez((0, cy+r), (r*0.72, cy+r), (r*0.98, cy+r*0.5), (r*0.97, cy)) + \
           bez((r*0.97, cy), (r*0.95, cy-r*0.55), (r*0.6, cy-r*1.02), (0, cy-r*1.05)) + \
           bez((0, cy-r*1.05), (-r*0.6, cy-r*1.02), (-r*0.95, cy-r*0.55), (-r*0.97, cy)) + \
           bez((-r*0.97, cy), (-r*0.98, cy+r*0.5), (-r*0.72, cy+r), (0, cy+r))

def notch(pts, amp=0.9, every=5):
    P = resample(pts, 1.0); out = []
    for i in range(len(P)):
        a = P[max(0, i-1)]; b = P[min(len(P)-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        kk = amp if i % every == every-1 else 0
        out.append((P[i][0]-dy/L*kk, P[i][1]+dx/L*kk))
    return out
