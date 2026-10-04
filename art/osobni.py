"""The family's personal style ("osobni"), built by build_style.py from the scanned style sheets.

On by default since 2026-10-03 (game and comic). The previous look is one switch away:
    VMD_STYLE=puvodni .venv/bin/python export_assets.py
When on: palette.py takes the family's crayon colours, style3.stroke() draws with táta's measured line,
hatch() with his hatching, face() with his expressions, and letter.py letters in his handwriting.
Must not import palette or style3 (both import this).
"""
import os, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "style_data")
ACTIVE = os.environ.get("VMD_STYLE", "osobni") == "osobni"
# which parts are on (all by default); e.g. VMD_STYLE_PARTS=faces,palette to compare one at a time
ALL_PARTS = ("lines", "hatch", "faces", "palette", "font", "crayon", "pencil", "paper", "balloons")
PARTS = set(os.environ.get("VMD_STYLE_PARTS", ",".join(ALL_PARTS)).split(",")) if ACTIVE else set()


def on(part): return part in PARTS
PT_PER_MM = 72 / 25.4


def _load(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        raise SystemExit(f"VMD_STYLE=osobni, ale chybí {path} – spusť nejdřív build_style.py")
    with open(path, encoding="utf-8") as f: return json.load(f)


LINES = _load("lines.json") if ACTIVE else None
FACES = _load("faces.json") if ACTIVE else None
PALETTE = _load("palette.json") if ACTIVE else None
BALLOONS = _load("balloons.json") if ACTIVE else None

# the expression drawn for each mood the code asks for; moods without their own drawing borrow the nearest
FACE_FOR = {"happy": "happy", "calm": "happy", "grin": "grin", "laugh": "grin", "surprised": "surprised",
            "wow": "wow", "think": "think", "worried": "worried", "sad": "sad", "whisper": "whisper",
            "determined": "determined", "sleepy": "sleepy", "closed": "sleepy", "talk": "surprised"}


def palette_overrides():
    return PALETTE["overrides"] if on("palette") else {}


def stroke_params():
    """wobble/pressure in page pt, from táta's lines. The comic is printed about at the size he drew, so mm map
    to pt one to one; only the pressure swing is damped, because part of a pencil line's width noise is grain."""
    L = LINES
    p1, p2 = L["wobble_periods_mm"]; w1, w2 = L["wobble_weights"]
    period = max(p1, p2) * PT_PER_MM
    freqs = ((1.0, w1 if p1 >= p2 else w2), (max(p1, p2) / min(p1, p2), w2 if p1 >= p2 else w1))
    rms_unit = math.sqrt(sum(a * a for _, a in freqs) / 2)
    return dict(
        wob_amp=L["wobble_mm"] * PT_PER_MM / rms_unit,
        wob_freqs=freqs, wob_period=period,
        bow=L["bow_per_len"],
        prs_amp=min(0.5, L["pressure_cv"] * 0.7 / 0.54),
        taper_floor=min(0.9, max(0.25, L["end_width_ratio"] * 0.8)),
        width_k=max(0.85, min(1.25, L["width_mm"] * PT_PER_MM / 1.15)))


def hatch_params():
    h = LINES["hatch"]
    return dict(spacing_k=max(1.0, min(2.2, h["spacing_mm"] * PT_PER_MM / 1.6)),
                end_heavy=h.get("end_weight", 1.0) > 1.3)


def font_path(name): return os.path.join(HERE, "fonts", name)


# ------------------------------------------------------------------ materials
TEX = os.path.join(DATA, "textures")
CACHE = os.path.join(DATA, "cache")
TILE_MM = 34.0   # a texture tile covers this much of the page, about the size it was coloured


def _textures(kind):
    return sorted(os.path.join(TEX, f) for f in os.listdir(TEX) if f.startswith(kind)) if os.path.isdir(TEX) else []


def crayon_tile(rgb, key, bw=False):
    """RGBA tile: the colour laid down with a real crayon (or pencil, for the B&W comic), transparent in the gaps.
    `key` picks one of the scanned colourings, so neighbouring areas don't share the same strokes."""
    from PIL import Image
    tex = _textures("pencil" if bw else "crayon")
    if not tex: return None
    src = tex[key % len(tex)]
    hexs = "%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb)
    path = os.path.join(CACHE, f"{os.path.basename(src)[:-4]}_{hexs}.png")
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        a = Image.open(src).convert("L")
        im = Image.new("RGBA", a.size, tuple(int(round(c * 255)) for c in rgb) + (0,)); im.putalpha(a)
        tmp = f"{path}.{os.getpid()}.tmp"  # several builds may run at once: never let one read a half-written tile
        im.save(tmp, format="PNG"); os.replace(tmp, path)
    return path


def paper(png_path, strength=0.22):
    """press the scanned paper grain into a finished picture (rooms; characters sit on them)"""
    from PIL import Image, ImageChops
    src = os.path.join(TEX, "paper.png")
    if not on("paper") or not os.path.exists(src): return
    im = Image.open(png_path); mode = im.mode
    rgb = im.convert("RGB")
    g = Image.open(src).convert("L")
    tiled = Image.new("L", rgb.size)
    for y in range(0, rgb.size[1], g.size[1]):
        for x in range(0, rgb.size[0], g.size[0]): tiled.paste(g, (x, y))
    # grain around mid-grey: darker specks multiply in, lighter ones lift a little
    lut = [max(0, min(255, int(255 - (128 - v) * strength * 2))) if v < 128 else 255 for v in range(256)]
    out = ImageChops.multiply(rgb, Image.merge("RGB", [tiled.point(lut)] * 3))
    if mode == "RGBA": out.putalpha(im.getchannel("A"))
    out.save(png_path)


# ------------------------------------------------------------------ balloons
def balloon_outline(kind, cx, cy, rx, ry, n=None):
    """táta's balloon shape (speech, thought, shout, whisper) stretched over the ellipse rx, ry; None if off"""
    if not on("balloons") or kind not in BALLOONS: return None
    prof = BALLOONS[kind]["profile"]
    if kind == "shout": prof = [1 + (k - 1) * 1.6 for k in prof]  # his spikes, a bit bolder at comic size
    n = n or len(prof)
    pts = []
    for j in range(n):  # parametric angle from 0, counter-clockwise, like letter.wobbly_ellipse
        t = 2 * math.pi * j / n
        k = prof[int(((t + math.pi) / (2 * math.pi)) * len(prof)) % len(prof)]
        pts.append((cx + math.cos(t) * rx * k, cy + math.sin(t) * ry * k))
    return pts


def whisper_dashes():
    w = BALLOONS.get("whisper", {}) if on("balloons") else {}
    return (w["dash_mm"] * PT_PER_MM, w["dash_cv"], w["gap_mm"] * PT_PER_MM) if "dash_mm" in w else None


def frame_overshoot():
    f = BALLOONS.get("frame") if on("balloons") else None
    return (f["overshoot_mm"] * PT_PER_MM, f["overshoot_max_mm"] * PT_PER_MM) if f else None
