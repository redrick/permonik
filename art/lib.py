import math, random, os
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.utils import simpleSplit

pdfmetrics.registerFont(TTFont("Hand", os.path.join(FONTS, "PatrickHand-Regular.ttf")))
pdfmetrics.registerFont(TTFont("CN", os.path.join(FONTS, "ComicNeue-Regular.ttf")))
pdfmetrics.registerFont(TTFont("CNB", os.path.join(FONTS, "ComicNeue-Bold.ttf")))

MODE = "bw"   # "bw" for the printed comic, "color" for the game

class Col(float):
    """grey level (used in bw mode) that also carries a colour (used in color mode)"""
    def __new__(cls, g, hex_, alpha=None):
        o = float.__new__(cls, g); o.hex = hex_; o.alpha = alpha
        return o

def G(v):  # grey level 0=black 1=white
    if MODE == "color" and isinstance(v, Col):
        return HexColor(v.hex)
    return Color(v, v, v)

def alpha_for(g, alpha):
    if MODE == "color" and isinstance(g, Col) and g.alpha is not None:
        return g.alpha
    return alpha

RND = random.Random(7)
class _Proxy:
    cv = None
    def __getattr__(self, n): return getattr(_Proxy.cv, n)
C = _Proxy()
def set_canvas(cv):
    _Proxy.cv = cv

# ------------------------------------------------------------------ geometry
def ell(cx, cy, rx, ry, n=36, a0=0, a1=360, rot=0):
    pts = []
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    for i in range(n+1 if (a1-a0) < 360 else n):
        a = math.radians(a0 + (a1-a0)*i/(n if (a1-a0) < 360 else n))
        x, y = math.cos(a)*rx, math.sin(a)*ry
        pts.append((cx + x*cr - y*sr, cy + x*sr + y*cr))
    return pts

def bez(p0, p1, p2, p3, n=16):
    out = []
    for i in range(n+1):
        t = i/n; u = 1-t
        out.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                    u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
    return out

def rrect(x, y, w, h, r=6):
    pts = []
    for (cx, cy, a0) in ((x+w-r, y+r, -90), (x+w-r, y+h-r, 0), (x+r, y+h-r, 90), (x+r, y+r, 180)):
        pts += ell(cx, cy, r, r, 6, a0, a0+90)
    return pts

def resample(pts, step=3.0, closed=False):
    P = list(pts) + ([pts[0]] if closed else [])
    out = [P[0]]
    acc = 0
    for i in range(1, len(P)):
        x0, y0 = out[-1] if False else P[i-1]
        x1, y1 = P[i]
        d = math.hypot(x1-x0, y1-y0)
        if d == 0: continue
        n = max(1, int(d/step))
        for k in range(1, n+1):
            out.append((x0+(x1-x0)*k/n, y0+(y1-y0)*k/n))
    if closed and len(out) > 1: out.pop()
    return out

def jitter(pts, amt, closed=False):
    if amt <= 0: return pts
    ph = RND.random()*10; ph2 = RND.random()*10
    n = len(pts); out = []
    for i, (x, y) in enumerate(pts):
        t = i/max(1, n)
        dx = amt*(0.6*math.sin(t*6.3*2+ph) + 0.4*math.sin(t*6.3*5+ph2))
        dy = amt*(0.6*math.cos(t*6.3*2+ph2) + 0.4*math.sin(t*6.3*4+ph))
        out.append((x+dx, y+dy))
    return out

# ------------------------------------------------------------------ inking
def _poly(pts, closed=True):
    p = C.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    if closed: p.close()
    return p

def fill(pts, g=1.0):
    C.saveState(); C.setFillColor(G(g) if isinstance(g, (int, float)) else g)
    C.drawPath(_poly(pts), fill=1, stroke=0); C.restoreState()

def ink(pts, w=1.6, closed=False, taper=True, jit=0.6):
    """Draw a tapered ink ribbon along pts."""
    if len(pts) < 2: return
    P = resample(pts, 2.5, closed)
    P = jitter(P, jit, closed)
    n = len(P)
    if n < 2: return
    left, right = [], []
    ph = RND.random()*6
    for i in range(n):
        if closed:
            a = P[(i-1) % n]; b = P[(i+1) % n]
        else:
            a = P[max(0, i-1)]; b = P[min(n-1, i+1)]
        dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
        nx, ny = -dy/L, dx/L
        t = i/(n-1)
        if closed or not taper:
            ww = w*(0.85 + 0.25*math.sin(t*6.28*2 + ph))
        else:
            ww = w*(0.35 + 0.65*math.sin(math.pi*t)**0.5) * (0.9 + 0.15*math.sin(t*9+ph))
        left.append((P[i][0]+nx*ww/2, P[i][1]+ny*ww/2))
        right.append((P[i][0]-nx*ww/2, P[i][1]-ny*ww/2))
    C.saveState(); C.setFillColor(black)
    if closed:
        p = _poly(left); pr = _poly(list(reversed(right)))
        p = C.beginPath(); p.moveTo(*left[0])
        for q in left[1:]: p.lineTo(*q)
        p.close(); p.moveTo(*right[0])
        for q in right[1:]: p.lineTo(*q)
        p.close()
        C.drawPath(p, fill=1, stroke=0, fillMode=0)
    else:
        C.drawPath(_poly(left + list(reversed(right))), fill=1, stroke=0)
    C.restoreState()

def shape(pts, g=1.0, w=1.6, jit=0.5):
    """filled shape with ink outline"""
    if g is not None: fill(pts, g)
    ink(pts, w, closed=True, jit=jit)

def line(p0, p1, w=1.4, jit=0.4):
    ink([p0, p1], w, jit=jit)

def curve(p0, p1, p2, p3, w=1.4, jit=0.4):
    ink(bez(p0, p1, p2, p3), w, jit=jit)

def dot(x, y, r, g=0):
    C.saveState(); C.setFillColor(G(g)); C.circle(x, y, r, fill=1, stroke=0); C.restoreState()

def hatch(pts_clip, x0, y0, x1, y1, gap=5, ang=45, w=0.6, g=0.35):
    """diagonal hatching clipped to polygon"""
    C.saveState(); C.clipPath(_poly(pts_clip), stroke=0, fill=0)
    C.setStrokeColor(G(g)); C.setLineWidth(w)
    L = (x1-x0)+(y1-y0)
    k = -L
    while k < L:
        C.line(x0+k, y0, x0+k+(y1-y0), y1); k += gap
    C.restoreState()

# ------------------------------------------------------------------ transforms
class T:
    """context manager: translate/scale/flip local drawing"""
    def __init__(self, x, y, s=1.0, flip=False, rot=0):
        self.a = (x, y, s, flip, rot)
    def __enter__(self):
        x, y, s, flip, rot = self.a
        C.saveState(); C.translate(x, y); C.rotate(rot); C.scale(-s if flip else s, s)
    def __exit__(self, *e):
        C.restoreState()

# ------------------------------------------------------------------ text
def text_block(x, y, w, txt, font="Hand", size=15, lead=None, align="center", color=0):
    lead = lead or size*1.12
    lines = []
    for para in txt.split("\n"):
        lines += simpleSplit(para, font, size, w)
    C.saveState(); C.setFont(font, size); C.setFillColor(G(color))
    for i, ln in enumerate(lines):
        yy = y - i*lead
        if align == "center": C.drawCentredString(x + w/2, yy, ln)
        else: C.drawString(x, yy, ln)
    C.restoreState()
    return len(lines)

def measure(txt, w, font="Hand", size=15):
    n = 0
    for para in txt.split("\n"): n += len(simpleSplit(para, font, size, w))
    return n
