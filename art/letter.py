import math, random, zlib
import lib
from lib import G, ell, bez, rrect
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import black, white
from style3 import C, stroke, fill, poly, _SC

import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
import osobni
if osobni.on("font"):
    # táta's handwriting; the B font holds his second version of every letter, swapped in for every other letter
    pdfmetrics.registerFont(TTFont("SH", D+"TataHand.ttf"))
    pdfmetrics.registerFont(TTFont("SHB", D+"TataHand.ttf"))
    pdfmetrics.registerFont(TTFont("SH2", D+"TataHandB.ttf"))
else:
    pdfmetrics.registerFont(TTFont("SH", D+"ShantellHand.ttf"))
    pdfmetrics.registerFont(TTFont("SHB", D+"ShantellHandBold.ttf"))
pdfmetrics.registerFont(TTFont("BG", D+"f_Bangers-Regular.ttf"))

def _rng(txt): return random.Random(zlib.crc32(txt.encode("utf-8")))

def lines_of(txt, font, size, w):
    out = []
    for para in txt.split("\n"): out += simpleSplit(para, font, size, w)
    return out

def hand_line(x, y, line, font, size, r, rot_amp=2.2, dy_amp=0.035, g=0.0):
    cx = x
    for i, ch in enumerate(line):
        if osobni.on("font") and font in ("SH", "SHB") and i % 2: font_i = "SH2"
        else: font_i = font
        sw = pdfmetrics.stringWidth(ch, font_i, size)
        k = 1 + r.uniform(-0.035, 0.035)
        C.saveState(); C.translate(cx, y + r.uniform(-1, 1)*size*dy_amp)
        C.rotate(r.uniform(-rot_amp, rot_amp)); C.setFont(font_i, size*k); C.setFillColor(G(g))
        C.drawString(0, 0, ch); C.restoreState()
        cx += sw*k + r.uniform(-0.15, 0.2)
    return cx - x


def hand_text(x, y, w, txt, font="SH", size=14, align="center", lead=None, g=0.0):
    """y = baseline of first line"""
    lead = lead or size*1.18
    r = _rng(txt)
    L = lines_of(txt, font, size, w)
    for i, ln in enumerate(L):
        lw = pdfmetrics.stringWidth(ln, font, size)
        xx = x + (w - lw)/2 if align == "center" else x
        hand_line(xx, y - i*lead, ln, font, size, r, g=g)
    return len(L)

# ------------------------------------------------------------------ bubbles
def wobbly_ellipse(cx, cy, rx, ry, seed, n=72, kind="speech"):
    mine = osobni.balloon_outline(kind, cx, cy, rx, ry, n)
    if mine: return mine  # táta's balloon; bubble() hangs the tail on it by angle, so the order must stay
    r = random.Random(seed)
    ph1, ph2 = r.random()*6.28, r.random()*6.28
    pts = []
    for i in range(n):
        a = math.tau*i/n
        k = 1 + 0.025*math.sin(a*2 + ph1) + 0.015*math.sin(a*3 + ph2)
        c, s_ = math.cos(a), math.sin(a)
        e = 2/2.7
        pts.append((cx + math.copysign(abs(c)**e, c)*rx*k, cy + math.copysign(abs(s_)**e, s_)*ry*k))
    return pts

def bubble(x, y, w, txt, tx, ty, size=14.5, whisper=False, font="SH"):
    L = lines_of(txt, font, size, w-30)
    lead = size*1.15
    h = len(L)*lead + 16
    cx, cy = x + w/2, y - h/2
    rx, ry = w/2*1.02, h/2*1.12
    seed = zlib.crc32(txt.encode())
    E = wobbly_ellipse(cx, cy, rx, ry, seed, kind="whisper" if whisper else "speech")
    ang = math.atan2(ty-cy, tx-cx)
    # make sure the tail tip is outside the balloon
    ex_r = 1/math.sqrt((math.cos(ang)/rx)**2 + (math.sin(ang)/ry)**2)
    d = math.hypot(tx-cx, ty-cy)
    if d < ex_r + 14:
        tx, ty = cx + math.cos(ang)*(ex_r+14), cy + math.sin(ang)*(ex_r+14)
    n = len(E)
    # find tail base indices
    ai = int(((ang % math.tau)/math.tau)*n)
    half = max(3, int(n*0.045))
    i0, i1 = (ai - half) % n, (ai + half) % n
    p0, p1 = E[i0], E[i1]
    mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
    # curved tail
    bend = 0.25
    nx, ny = -(ty-my), (tx-mx)
    c0 = (p0[0] + (tx-p0[0])*0.55 + nx*bend*0.3, p0[1] + (ty-p0[1])*0.55 + ny*bend*0.3)
    c1 = (p1[0] + (tx-p1[0])*0.55 + nx*bend*0.3, p1[1] + (ty-p1[1])*0.55 + ny*bend*0.3)
    tail = bez(p1, c1, c1, (tx, ty), 10) + bez((tx, ty), c0, c0, p0, 10)
    # outline polygon: ellipse from i1 around to i0, then tail
    seq = []
    k = i1
    while k != i0:
        seq.append(E[k]); k = (k+1) % n
    seq.append(E[i0])
    outline = seq[:-1] + list(reversed(tail))[1:] if False else seq + tail[::-1][1:-1]
    # simpler: ellipse arc i1->i0 then tail back p0->tip->p1
    outline = seq + bez(p0, c0, c0, (tx, ty), 10)[1:] + bez((tx, ty), c1, c1, p1, 10)[1:]
    fill(outline, 1.0)
    if whisper:
        # hand dashes (táta's: long, uneven dashes with short gaps)
        P = lib.resample(outline, 1.0, True)
        mine = osobni.whisper_dashes()
        rd = random.Random(seed)
        dash, gap = 5, 4; i = 0
        while i < len(P)-1:
            if mine:
                dash = max(2, int(mine[0]*(1 + rd.uniform(-1, 1)*mine[1]))); gap = max(2, int(mine[2]))
            seg = P[i:i+dash]
            if len(seg) > 1: stroke(seg, 1.1)
            i += dash + gap
    else:
        stroke(outline, 1.25, closed=True)
    hand_text(x+15, cy + (len(L)*lead)/2 - size*0.82, w-30, txt, font, size, lead=lead)
    return h

def shout(x, y, w, txt, tx=None, ty=None, size=15, font="SH"):
    """a shouted line: spiky balloon (táta's, when the personal style is on), no tail needed"""
    L = lines_of(txt, font, size, w-36)
    lead = size*1.15
    h = len(L)*lead + 26
    cx, cy = x + w/2, y - h/2
    seed = zlib.crc32(txt.encode())
    E = osobni.balloon_outline("shout", cx, cy, w/2*1.05, h/2*1.25)
    if not E:
        r = random.Random(seed); E = []
        for i in range(48):
            a = math.tau*i/48; k = 1.0 if i % 2 else 1.18 + r.uniform(-0.05, 0.05)
            E.append((cx + math.cos(a)*w/2*k, cy + math.sin(a)*h/2*1.2*k))
    fill(E, 1.0); stroke(E, 1.3, closed=True)
    hand_text(x+18, cy + (len(L)*lead)/2 - size*0.82, w-36, txt, font, size, lead=lead)
    return h


def thought(x, y, w, h, tx, ty, seed=1):
    cx, cy = x + w/2, y - h/2
    mine = osobni.balloon_outline("thought", cx, cy, w/2, h/2)
    if mine:
        # táta draws a thought as a calm oval with two small rings trailing to the thinker
        fill(mine, 1.0); stroke(mine, 1.2, closed=True)
        for k, rr in ((0.45, 4.2), (0.78, 2.6)):
            bx = cx + (tx-cx)*k; by = cy - h/2 + (ty-(cy-h/2))*k
            e = ell(bx, by, rr, rr*0.95, 16); fill(e, 1.0); stroke(e, 1.0, closed=True)
        return
    r = random.Random(seed)
    pts = []; N = 11
    for i in range(N):
        a0 = math.tau*i/N; a1 = math.tau*(i+1)/N
        p0 = (cx+math.cos(a0)*w/2, cy+math.sin(a0)*h/2); p1 = (cx+math.cos(a1)*w/2, cy+math.sin(a1)*h/2)
        am = (a0+a1)/2; k = 1.18 + r.random()*0.06
        m = (cx+math.cos(am)*w/2*k, cy+math.sin(am)*h/2*k)
        pts += bez(p0, ((p0[0]+m[0])/2+(m[0]-cx)*0.12, (p0[1]+m[1])/2+(m[1]-cy)*0.12),
                   ((p1[0]+m[0])/2+(m[0]-cx)*0.12, (p1[1]+m[1])/2+(m[1]-cy)*0.12), p1, 6)
    fill(pts, 1.0); stroke(pts, 1.2, closed=True)
    for k, rr in ((0.35, 5), (0.62, 3.4), (0.85, 2.2)):
        bx = cx + (tx-cx)*k; by = cy - h/2 + (ty-(cy-h/2))*k
        e = ell(bx, by, rr, rr*0.9, 16); fill(e, 1.0); stroke(e, 1.0, closed=True)

# ------------------------------------------------------------------ captions
def caption(p, txt, w=None, size=12.5, where="tl", font="SHB"):
    w = w or min(p.w - 16, 230)
    L = lines_of(txt, font, size, w-16)
    lead = size*1.15
    h = len(L)*lead + 11
    x = p.x + 6 if where in ("tl", "bl") else p.x + p.w - w - 6
    y = p.y + p.h - h - 6 if where in ("tl", "tr") else p.y + 6
    r = _rng(txt)
    j = lambda: r.uniform(-1.2, 1.2)
    box = [(x+j(), y+j()), (x+w+j(), y+j()), (x+w+j(), y+h+j()), (x+j(), y+h+j())]
    fill(box, 0.92)
    for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
        p0, p1 = box[a], box[b]
        dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L_ = math.hypot(dx, dy)
        ex = 1.6/L_
        stroke([(p0[0]-dx*ex, p0[1]-dy*ex), (p1[0]+dx*ex, p1[1]+dy*ex)], 1.1)
    hand_text(x+8, y+h-size-2.5, w-16, txt, font, size, align="left", lead=lead)

# ------------------------------------------------------------------ SFX / title
def sfx(x, y, txt, size=22, rot=0, fill_g=1.0, shadow=True, seed=None):
    r = random.Random(seed if seed is not None else zlib.crc32(txt.encode()))
    C.saveState(); C.translate(x, y); C.rotate(rot)
    cx = 0
    for ch in txt:
        sw = pdfmetrics.stringWidth(ch, "BG", size)
        a = r.uniform(-7, 7); dy = r.uniform(-size*0.06, size*0.06); k = 1 + r.uniform(-0.06, 0.08)
        for mode in (("shadow",) if shadow else ()) + ("main",):
            C.saveState()
            if mode == "shadow": C.translate(cx + size*0.05, dy - size*0.05)
            else: C.translate(cx, dy)
            C.rotate(a)
            t = C.beginText(0, 0); t.setFont("BG", size*k)
            if mode == "shadow":
                t.setTextRenderMode(0); C.setFillColor(G(0.25))
            else:
                t.setTextRenderMode(2); C.setFillColor(G(fill_g)); C.setStrokeColor(black); C.setLineWidth(size*0.035)
            t.textOut(ch); C.drawText(t); C.restoreState()
        cx += sw*k + size*0.06
    C.restoreState()
    return cx

def title(cx, y, txt, size=80):
    w = sum(pdfmetrics.stringWidth(ch, "BG", size) + size*0.06 for ch in txt)
    sfx(cx - w/2, y, txt, size, 0, 1.0, True, seed=7)

# ------------------------------------------------------------------ hand ruled panel
class Panel:
    def __init__(self, x, y, w, h, bg=1.0):
        self.x, self.y, self.w, self.h = x, y, w, h
        C.saveState()
        fill([(x, y), (x+w, y), (x+w, y+h), (x, y+h)], bg)
        C.clipPath(poly([(x, y), (x+w, y), (x+w, y+h), (x, y+h)]), stroke=0, fill=0)
    def __enter__(self): return self
    def __exit__(self, *e):
        C.restoreState()
        x, y, w, h = self.x, self.y, self.w, self.h
        mine = osobni.frame_overshoot()
        o = mine[0]*1.6 if mine else 2.2  # how far táta's frame lines run past the corners
        stroke([(x-o, y), (x+w+o*0.6, y)], 1.9)
        stroke([(x+w, y-o*0.7), (x+w, y+h+o)], 1.9)
        stroke([(x+w+o*0.5, y+h), (x-o, y+h)], 1.9)
        stroke([(x, y+h+o*0.6), (x, y-o)], 1.9)
    def X(self, f): return self.x + self.w*f
    def Y(self, f): return self.y + self.h*f
