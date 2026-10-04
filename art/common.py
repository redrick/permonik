"""Shared render helper for every Permoník art module.

Each asset is drawn on its own transparent PDF page in points, then rasterised at SCALE px per pt.
Sizes passed to render() are final PNG pixels; the draw function receives a Box in points (px / SCALE).
"""
import os, sys, zlib
from reportlab.pdfgen import canvas
import pymupdf
import lib
lib.MODE = "color"
import osobni
import style3

HERE = os.path.dirname(os.path.abspath(__file__))
GAME = os.environ.get("PERMONIK_GAME", os.path.join(HERE, "..", "game"))
OUT = os.path.join(GAME, "assets")
SCALE = 2.0
FEET = 4.0  # pt above the bottom edge where every character's feet stand (= 8 px)


class Box:
    def __init__(self, w, h): self.x, self.y, self.w, self.h = 0, 0, w, h
    def X(self, f): return self.w * f
    def Y(self, f): return self.h * f


def render(name, w_px, h_px, draw, folder, paper=False):
    """draw(b) on a w_px x h_px transparent PNG at game/assets/<folder>/<name>.png"""
    os.makedirs(os.path.join(OUT, folder), exist_ok=True)
    w, h = w_px / SCALE, h_px / SCALE
    tmp = os.path.join(OUT, folder, f"_{name}.{os.getpid()}.pdf")
    cv = canvas.Canvas(tmp, pagesize=(w, h)); lib.set_canvas(cv)
    style3._R.seed(zlib.crc32(name.encode()))
    draw(Box(w, h)); cv.showPage(); cv.save()
    doc = pymupdf.open(tmp)
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=True)
    path = os.path.join(OUT, folder, name + ".png"); pix.save(path); doc.close(); os.remove(tmp)
    if paper: osobni.paper(path)
    print("wrote", os.path.relpath(path, HERE))
    return path


def run(groups):
    """groups: {folder: [(name, w_px, h_px, fn), ...]}; argv: --only <folder> and/or name filters"""
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
    names = [a for a in sys.argv[1:] if not a.startswith("--") and a != only]
    for folder, items in groups.items():
        if only not in (None, folder): continue
        for it in items:
            name, w, h, fn = it[:4]
            if names and name not in names: continue
            render(name, w, h, fn, folder, paper=bool(it[4]) if len(it) > 4 else False)
