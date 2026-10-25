#!/usr/bin/env python3
"""Builds the website's class pages from the game: ability animations, icons and docs/data.js.

Run from anywhere: python3 tools/site_build.py
Reads game/data/*.json and game/assets/, writes docs/img/{anim,class,skills,items}/ and docs/data.js.
Nothing on the site may name the twist, so the last floor of Nav and its guardian are left out.
"""
import json
import math
import re
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
GAME = ROOT / "game"
A = GAME / "assets"
OUT = ROOT / "docs"
IMG = OUT / "img"

LAYERS = ["headgear_back", "back", "body_far", "weapon_far", "lamp_far", "hand_far", "offhand", "legs", "body",
          "belt", "lamp", "weapon_belt", "body_near", "weapon", "hand", "head", "headgear"]
SLOT_OF = {"headgear_back": "head", "body_far": "body", "weapon_far": "weapon", "lamp_far": "lamp", "offhand": "offhand",
           "body": "body", "belt": "belt", "lamp": "lamp", "weapon_belt": "weapon", "body_near": "body", "weapon": "weapon",
           "headgear": "head"}
DEFAULTED = {"body", "head", "belt"}

W, H = 420, 270
FRAMES = 16
GROUND = 252
HERO_X = 105
HSCALE = 1.25
R = HSCALE / 0.85

# Which ability each class shows on its card.
SHOWCASE = {"havir": "naloz", "zbojnice": "hod_valaskou", "vedma": "retezovy_blesk", "kovar": "kovadlina",
            "zrec": "dedek", "vlkodlak": "vlci_kuze", "alchymistka": "lucavka", "loutkarka": "kasparek"}


def load(name):
    return json.loads((GAME / "data" / f"{name}.json").read_text())


def rgba(p):
    return Image.open(p).convert("RGBA")


def hero(cls, pose, gear):
    d = A / "sprites" / "heroes" / cls / pose
    img = None
    for layer in LAYERS:
        slot = SLOT_OF.get(layer, "")
        f = layer
        if slot:
            look = gear.get(slot, "")
            if not look:
                if slot not in DEFAULTED:
                    continue
                look = "default"
            f += "." + look
        p = d / f"{f}.png"
        if not p.exists():
            continue
        src = rgba(p)
        img = src if img is None else Image.alpha_composite(img, src)
    return img


def gear_of(cls, classes, items):
    g = {}
    for iid in classes[cls]["start_items"]:
        b = items.get(iid, {})
        slot = b.get("slot")
        if slot in ("weapon", "offhand", "head", "body", "belt", "lamp"):
            g[slot] = b.get("look", b.get("icon", ""))
    if g.get("body") == "kytel":
        g.pop("body")
    return g


def scaled(img, s):
    return img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)


def tinted(img, hexcol):
    c = Image.new("RGBA", img.size, hexcol)
    out = ImageChops.multiply(img, c)
    out.putalpha(img.getchannel("A"))
    return out


def spirit(img, hexcol):
    out = Image.blend(img, Image.new("RGBA", img.size, hexcol), 0.4)
    out.putalpha(img.getchannel("A").point(lambda v: int(v * 0.85)))
    return out


def faded(img, a):
    out = img.copy()
    out.putalpha(img.getchannel("A").point(lambda v: int(v * max(0.0, min(1.0, a)))))
    return out


class Frame:
    def __init__(self):
        self.im = Image.new("RGBA", (W, H), (0, 0, 0, 0))

    def put(self, sprite, cx, feet, alpha=1.0, flip=False):
        """Feet sit 8 px above the sprite's bottom edge, as in the game."""
        if sprite is None:
            return
        s = sprite.transpose(Image.FLIP_LEFT_RIGHT) if flip else sprite
        if alpha < 1.0:
            s = faded(s, alpha)
        x = round(cx - s.width / 2)
        y = round(feet - s.height + 8 * HSCALE)
        self._clip(s, x, y)

    def center(self, sprite, cx, cy, alpha=1.0, rot=0.0):
        s = sprite.rotate(rot, Image.BICUBIC, expand=True) if rot else sprite
        if alpha < 1.0:
            s = faded(s, alpha)
        self._clip(s, round(cx - s.width / 2), round(cy - s.height / 2))

    def _clip(self, s, x, y):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.paste(s, (x, y), s)
        self.im = Image.alpha_composite(self.im, layer)

    def glow(self, cx, cy, r, col, a=0.8):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for i in range(6, 0, -1):
            rr = r * i / 6
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (int(255 * a * (1 - i / 7) ** 1.5),))
        layer = layer.filter(ImageFilter.GaussianBlur(r / 5))
        self.im = Image.alpha_composite(self.im, layer)

    def shadow(self, cx, w=60):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([cx - w / 2, GROUND - 7, cx + w / 2, GROUND + 7], fill=(0, 0, 0, 110))
        self.im = Image.alpha_composite(self.im, layer.filter(ImageFilter.GaussianBlur(3)))

    def ring(self, cx, r, col, a, width=4):
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).ellipse([cx - r, GROUND - r * 0.32, cx + r, GROUND + r * 0.32], outline=col + (int(255 * a),), width=width)
        self.im = Image.alpha_composite(self.im, layer.filter(ImageFilter.GaussianBlur(1.2)))

    def bolt(self, a, b, col, seed, width=3):
        import random
        rnd = random.Random(seed)
        pts = [a]
        n = 7
        for i in range(1, n):
            t = i / n
            x = a[0] + (b[0] - a[0]) * t + rnd.uniform(-10, 10)
            y = a[1] + (b[1] - a[1]) * t + rnd.uniform(-14, 14)
            pts.append((x, y))
        pts.append(b)
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).line(pts, fill=col + (200,), width=width * 4, joint="curve")
        glow = glow.filter(ImageFilter.GaussianBlur(5))
        core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(core).line(pts, fill=(255, 255, 255, 255), width=width, joint="curve")
        self.im = Image.alpha_composite(Image.alpha_composite(self.im, glow), core)

    def line(self, a, b, col, width=1):
        ImageDraw.Draw(self.im).line([a, b], fill=col, width=width)


def mon(mid, pose="idle", s=1.0):
    p = A / "sprites" / "monsters" / f"{mid}_{pose}.png"
    if not p.exists():
        p = A / "sprites" / "monsters" / f"{mid}_idle.png"
    return scaled(rgba(p), s * HSCALE * 0.62)


def fx(name, s=1.0):
    return scaled(rgba(A / "sprites" / "fx" / f"{name}.png"), s)


def arc(t, a, b, h):
    x = a[0] + (b[0] - a[0]) * t
    y = a[1] + (b[1] - a[1]) * t - math.sin(t * math.pi) * h
    return x, y


def animate(cls, poses, skills):
    """Sixteen frames, eight a second: idle, the windup, the ability, back to idle."""
    P = {k: scaled(v, HSCALE) for k, v in poses.items() if v is not None}
    hand = (HERO_X + 40 * R, GROUND - 120 * R)
    frames = []
    target_x = 330
    for i in range(FRAMES):
        f = Frame()
        pose = "idle"
        late = []

        if cls == "havir":
            pose = "cast" if 3 <= i <= 5 else "idle"
            if 5 <= i <= 9:
                t = (i - 5) / 4
                late.append(lambda f, t=t: f.center(fx("naloz", 1.3), *arc(t, hand, (target_x, GROUND - 20), 70), rot=-t * 540))
            if 10 <= i <= 14:
                k = (i - 10) / 4
                late.append(lambda f, k=k: (f.glow(target_x, GROUND - 40, 70 + 50 * k, (255, 150, 50), 0.95 - 0.6 * k),
                                            f.put(scaled(fx("flame"), 1.6 + k * 0.8), target_x - 18, GROUND, 1 - k),
                                            f.put(scaled(fx("flame"), 1.3 + k), target_x + 22, GROUND, 1 - k),
                                            [f.center(fx("rock", 0.8), target_x + math.cos(j * 1.3) * 90 * k,
                                                      GROUND - 30 - math.sin(j * 1.7 + 0.5) * 70 * k + 60 * k * k, 1 - k * 0.7, j * 50 * k)
                                             for j in range(6)]))

        elif cls == "zbojnice":
            pose = "attack" if 3 <= i <= 4 else "idle"
            if 4 <= i <= 12:
                t = (i - 4) / 8
                x = hand[0] + (target_x + 20 - hand[0]) * math.sin(t * math.pi)
                y = hand[1] + 10 - math.sin(t * math.pi) * 20
                late.append(lambda f, x=x, y=y, t=t: f.center(fx("valaska", 1.6), x, y, rot=-t * 1440))
            if 7 <= i <= 9:
                k = (i - 7) / 2
                late.append(lambda f, k=k: (f.glow(target_x + 20, hand[1], 30, (255, 230, 180), 0.8 - 0.5 * k),
                                            [f.center(fx("spark", 0.9), target_x + 20 + math.cos(j * 1.05) * 40 * (k + 0.3),
                                                      hand[1] + math.sin(j * 1.05) * 40 * (k + 0.3), 1 - k * 0.6) for j in range(6)]))

        elif cls == "vedma":
            pose = "cast" if 3 <= i <= 11 else "idle"
            if 4 <= i <= 11:
                tip = (HERO_X + 22, GROUND - 186)
                pts = [tip, (250, GROUND - 70), (320, GROUND - 120), (385, GROUND - 60)]
                hops = min(3, (i - 4) // 2 + 1)
                def lightning(f, i=i, hops=hops, pts=pts):
                    f.glow(*pts[0], 40, (150, 190, 255), 0.7)
                    for h in range(hops):
                        f.bolt(pts[h], pts[h + 1], (120, 170, 255), seed=i * 10 + h)
                        f.glow(*pts[h + 1], 34, (150, 200, 255), 0.75)
                late.append(lightning)

        elif cls == "kovar":
            pose = "attack" if 2 <= i <= 4 else "idle"
            if 4 <= i <= 12:
                k = (i - 4) / 8
                front = HERO_X + 55 * R
                late.append(lambda f, k=k, front=front: (f.ring(front, 30 + 150 * k, (255, 170, 80), 1 - k, 5),
                                                         f.ring(front, 20 + 100 * k, (255, 220, 160), 0.8 * (1 - k), 3),
                                                         f.glow(front, GROUND - 10, 60 * (1 - k) + 20, (255, 140, 40), 0.9 * (1 - k)),
                                                         [f.center(fx("spark", 0.9), front + math.cos(j * 0.8 - 2.6) * 120 * k,
                                                                   GROUND - 10 - abs(math.sin(j * 0.8 - 2.6)) * 110 * k + 70 * k * k, 1 - k)
                                                          for j in range(8)]))

        elif cls == "zrec":
            sk = skills["dedek"]["params"]
            ghost = spirit(mon(sk["look"], "idle", sk.get("scale", 1.0) * 1.35), sk.get("tint", "#ffffff"))
            pose = "cast" if 2 <= i <= 6 else "idle"
            gx = 300
            if 3 <= i <= 7:
                k = (i - 3) / 4
                cut = ghost.crop((0, 0, ghost.width, max(1, int(ghost.height * k))))
                late.append(lambda f, k=k, cut=cut: (f.glow(gx, GROUND - 20, 70, (170, 210, 255), 0.6),
                                                     f.ring(gx, 60, (190, 220, 255), 0.8),
                                                     f.im.alpha_composite(cut, (round(gx - ghost.width / 2), round(GROUND + 8 * HSCALE - ghost.height * k)))
                                                     if GROUND - ghost.height * k >= 0 else None))
            elif i >= 8:
                k = 0 if i < 14 else (i - 13) / 3
                a = mon(sk["look"], "attack" if i in (10, 11) else "idle", sk.get("scale", 1.0) * 1.35)
                late.append(lambda f, a=a, k=k: (f.glow(gx, GROUND - 60, 60, (170, 210, 255), 0.35 * (1 - k)), f.shadow(gx, 56),
                                                 f.put(spirit(a, sk.get("tint", "#ffffff")), gx, GROUND, 1 - k)))

        elif cls == "vlkodlak":
            pose = "cast" if 3 <= i <= 5 else "idle"
            if 6 <= i <= 7:
                late.append(lambda f, i=i: f.glow(HERO_X, GROUND - 130, 120, (255, 240, 210), 0.95 if i == 6 else 0.6))
            if i >= 7:
                wpose = "attack" if i in (10, 11, 14) else ("walk" if i in (12, 13) else "idle")
                w = mon("vlkodlak", wpose)
                late.append(lambda f, w=w, i=i: (f.shadow(HERO_X + 10, 90), f.put(w, HERO_X + 10, GROUND, 0.6 if i == 7 else 1.0)))

        elif cls == "alchymistka":
            pose = "cast" if 3 <= i <= 5 else "idle"
            flask = scaled(rgba(A / "items" / "krivule.png"), 0.8)
            if 5 <= i <= 9:
                t = (i - 5) / 4
                late.append(lambda f, t=t: f.center(flask, *arc(t, hand, (target_x, GROUND - 20), 80), rot=-t * 400))
            if 10 <= i <= 15:
                k = (i - 10) / 5
                def splash(f, k=k):
                    f.glow(target_x, GROUND - 30, 60 + 50 * k, (120, 230, 90), 0.85 - 0.6 * k)
                    f.ring(target_x, 40 + 60 * k, (150, 255, 120), 0.9 * (1 - k), 4)
                    for j in range(7):
                        ang = j * 0.9
                        f.glow(target_x + math.cos(ang) * 55 * k, GROUND - 20 - abs(math.sin(ang)) * 50 * k - 20 * k, 18 + 10 * k,
                               (110, 200, 70), 0.7 * (1 - k))
                late.append(splash)

        elif cls == "loutkarka":
            sk = skills["kasparek"]["params"]
            pose = "cast" if 2 <= i <= 5 else "idle"
            px = 290
            if i >= 4:
                a = 1.0 if i >= 6 else (i - 3) / 3
                bob = abs(math.sin(i * 0.9)) * 26
                pup = mon(sk["look"], "attack" if i % 4 == 1 else ("walk" if i % 2 else "idle"), sk.get("scale", 1.0) * 1.7)
                pup = tinted(pup, sk.get("tint", "#ffffff"))
                feet = GROUND - bob
                bb = pup.getbbox()
                fig_top = feet - pup.height + 8 * HSCALE + bb[1]
                fig_h = bb[3] - bb[1]
                bar_y = fig_top - 45
                def puppet(f, pup=pup, feet=feet, bar_y=bar_y, a=a, i=i, top=fig_top, fh=fig_h):
                    if i in (4, 5):
                        f.glow(px, GROUND - 50, 70, (255, 210, 110), 0.7)
                    f.shadow(px, 44 + (26 - (GROUND - feet)) * 0.6)
                    f.put(pup, px, feet, a)
                    col = (235, 225, 200, int(220 * a))
                    f.line((px - 34, bar_y), (px + 34, bar_y + 6), (120, 80, 40, int(255 * a)), 5)
                    for dx, ty in ((-30, top + fh * 0.4), (30, top + fh * 0.4), (0, top + 4)):
                        f.line((px + dx, bar_y + 3 + dx * 0.1), (px + dx * 0.6, ty), col, 1)
                    f.line((hand[0] + 4, hand[1] - 22), (px - 34, bar_y), (235, 225, 200, int(160 * a)), 1)
                late.append(puppet)

        if not (cls == "vlkodlak" and i >= 7):
            f.shadow(HERO_X, 70)
            f.put(P.get(pose, P["idle"]), HERO_X, GROUND)
        for fn in late:
            fn(f)
        frames.append(f.im)
    sheet = Image.new("RGBA", (W * FRAMES, H), (0, 0, 0, 0))
    for i, fr in enumerate(frames):
        sheet.paste(fr, (i * W, 0))
    return sheet


def mod_texts():
    src = (GAME / "scripts" / "core" / "item.gd").read_text()
    out = {}
    for m in re.finditer(r'"(\w+)": \{"cs": "(.*?)", "en": "(.*?)"\}', src.split("const MOD_TEXT")[1]):
        out[m.group(1)] = {"cs": m.group(2), "en": m.group(3)}
    return out


def mod_line(m, classes, tpl):
    lo, hi = m.get("min", m.get("value", 0)), m.get("max", m.get("value", 0))
    sign = "" if lo < 0 else "+"
    v = f"{sign}{lo}" if lo == hi else f"{sign}{lo}–{hi}"
    st = m["stat"]
    if st.startswith("class_"):
        cn = classes.get(st[6:], {}).get("name", {"cs": st, "en": st})
        return {"cs": f"{v} ke všem dovednostem ({cn['cs']})", "en": f"{v} to {cn['en']} skills"}
    if st.startswith("tree_"):
        tid = st[5:]
        tn = {"cs": tid, "en": tid}
        for c in classes.values():
            for t in c["trees"]:
                if t["id"] == tid:
                    tn = t["name"]
        return {"cs": f"{v} k dovednostem: {tn['cs']}", "en": f"{v} to {tn['en']} skills"}
    t = tpl.get(st)
    if not t:
        return {"cs": f"{v} {st}", "en": f"{v} {st}"}
    return {k: t[k].replace("{v}", v if t[k].startswith("{v}") else v.lstrip("+")) for k in ("cs", "en")}


def fmt_num(v):
    if isinstance(v, (list, tuple)):
        return f"{round(v[0])}–{round(v[1])}"
    if isinstance(v, float) and abs(v - round(v)) >= 0.05:
        return f"{v:.1f}"
    return str(round(v)) if isinstance(v, (int, float)) else str(v)


def skill_param(s, p, rank):
    v = s.get("params", {}).get(p)
    if isinstance(v, list) and len(v) == 2 and isinstance(v[0], list):
        return (v[0][0] + v[1][0] * (rank - 1), v[0][1] + v[1][1] * (rank - 1))
    if isinstance(v, list) and len(v) >= 2:
        return float(v[0]) + float(v[1]) * (rank - 1)
    return v


def fill_desc(s, rank=1):
    """The skill sheet's text with the numbers at a rank, as the game's tooltip shows them."""
    out = {}
    for lang, txt in s.get("desc", {}).items():
        for p in s.get("params", {}):
            if "{" + p + "}" in txt:
                txt = txt.replace("{" + p + "}", fmt_num(skill_param(s, p, rank)))
        out[lang] = txt
    return out


WROTE = set()


def icon(src, dst, size):
    WROTE.add(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = rgba(src)
    im.thumbnail((size, size), Image.LANCZOS)
    im.save(dst, "WEBP", quality=88, method=6)


# What the four seals forge into is left for the player to find.
SPOILERS = {"permonikuv_desatek"}

SLOT_NAMES = {
    "weapon": {"cs": "Zbraň", "en": "Weapon"}, "offhand": {"cs": "Druhá ruka", "en": "Off-hand"},
    "body": {"cs": "Zbroj", "en": "Armour"}, "head": {"cs": "Hlava", "en": "Head"}, "belt": {"cs": "Opasek", "en": "Belt"},
    "ring": {"cs": "Prsten", "en": "Ring"}, "amulet": {"cs": "Amulet", "en": "Amulet"}, "lamp": {"cs": "Kahan", "en": "Lamp"},
    "charm": {"cs": "Hromový kámen", "en": "Thunderstone"}, "gem": {"cs": "Drahokam", "en": "Gem"},
    "letter": {"cs": "Písmeno", "en": "Letter"},
}


def finder_entries(items, uniques, sets, words, classes, later, tpl):
    """Everything the item finder on the site can show: bases, uniques, set pieces, words, gems and letters."""
    out = []

    def ic(icon_id, size=96):
        src = A / "items" / f"{icon_id}.png"
        if src.exists():
            icon(src, IMG / "items" / f"{icon_id}.webp", size)
            return icon_id
        return None

    def base_stats(b):
        st = {}
        if b.get("dmg"):
            st["dmg"] = b["dmg"]
        if b.get("armor"):
            st["armor"] = b["armor"]
        if b.get("block"):
            st["block"] = b["block"]
        if b.get("light"):
            st["light"] = b["light"]
        if b.get("two_handed"):
            st["two"] = True
        if b.get("speed"):
            st["speed"] = b["speed"]
        return st

    for bid, b in items.items():
        slot = b.get("slot")
        if slot not in SLOT_NAMES or b.get("class") in later or b.get("no_drop"):
            continue
        e = {"k": "base", "id": bid, "name": b["name"], "slot": slot, "qlvl": b.get("qlvl", 1),
             "req": b.get("req", {}).get("level", 1), "icon": ic(b.get("icon", bid)), "tier": b.get("tier"),
             "cls": b.get("class"), "stats": base_stats(b)}
        if slot == "gem":
            e["k"] = "gem"
            e["socket"] = {k: [mod_line(m, classes, tpl) for m in v] for k, v in b.get("socket", {}).items()}
        elif slot == "letter":
            e["k"] = "letter"
            e["glyph"] = b.get("glyph")
            e["latin"] = b.get("latin")
            e["socket"] = {k: [mod_line(m, classes, tpl) for m in v] for k, v in b.get("socket", {}).items()}
        elif slot == "charm":
            e["k"] = "charm"
        out.append(e)
    for uid, u in uniques.items():
        b = items.get(u["base"], {})
        if b.get("class") in later or u.get("class") in later or uid in SPOILERS:
            continue
        out.append({"k": "unique", "id": uid, "name": u["name"], "base": b.get("name"), "slot": b.get("slot"),
                    "qlvl": u.get("qlvl", b.get("qlvl", 1)),
                    "icon": ic(u.get("icon", b.get("icon", u["base"]))), "cls": b.get("class"), "stats": base_stats(b),
                    "mods": [mod_line(m, classes, tpl) for m in u.get("mods", [])], "flavor": u.get("flavor")})
    for sid, st in sets["sets"].items():
        for pid in st["pieces"]:
            pc = sets["items"][pid]
            b = items.get(pc["base"], {})
            out.append({"k": "set", "id": pid, "name": pc["name"], "set": st["name"], "base": b.get("name"), "slot": b.get("slot"),
                        "qlvl": st.get("qlvl", 1), "icon": ic(b.get("icon", pc["base"])),
                        "cls": st.get("class"), "stats": base_stats(b), "mods": [mod_line(m, classes, tpl) for m in pc.get("mods", [])]})
    for wid, w in words.items():
        out.append({"k": "word", "id": wid, "name": w["name"], "meaning": w["meaning"], "qlvl": w["qlvl"],
                    "letters": [items[f"glag_{l}"]["glyph"] for l in w["letters"]], "bases": w["bases"],
                    "mods": [mod_line(m, classes, tpl) for m in w["mods"]]})
    return out


def main():
    all_classes = load("classes")
    later = {c for e in load("expansions").values() if not e.get("released") for c in e["classes"]}
    classes = {k: v for k, v in all_classes.items() if k not in later}
    skills = load("skills")
    items = load("items_base")
    sets = load("sets")
    sets["sets"] = {k: s for k, s in sets["sets"].items() if s.get("class") not in later}
    words = load("words")
    acts = load("acts")
    uniques = load("uniques")
    monsters = load("monsters")
    codex = load("codex")
    books = load("books")
    quests = load("quests")
    tpl = mod_texts()

    for d in ("anim", "class", "skills", "items"):
        (IMG / d).mkdir(parents=True, exist_ok=True)

    data = {"classes": [], "shared_sets": [], "words": [], "gems": [], "facts": {}}

    def set_entry(sid, s):
        pieces = []
        for pid in s["pieces"]:
            p = sets["items"][pid]
            b = items[p["base"]]
            ic = b.get("icon", p["base"])
            icon(A / "items" / f"{ic}.png", IMG / "items" / f"{ic}.webp", 96)
            pieces.append({"name": p["name"], "base": b["name"], "icon": ic,
                           "mods": [mod_line(m, classes, tpl) for m in p.get("mods", [])]})
        bonus = []
        for k in sorted(s["bonus"], key=lambda x: 99 if x == "full" else int(x)):
            bonus.append({"n": k, "mods": [mod_line(m, classes, tpl) for m in s["bonus"][k]]})
        return {"id": sid, "name": s["name"], "flavor": s.get("flavor"), "qlvl": s["qlvl"], "pieces": pieces, "bonus": bonus}

    for cid, c in classes.items():
        gear = gear_of(cid, classes, items)
        poses = {p: hero(cid, p, gear) for p in ("idle", "attack", "cast")}
        sheet = animate(cid, poses, skills)
        sheet.save(IMG / "anim" / f"{cid}.webp", "WEBP", quality=82, method=6)
        WROTE.add(IMG / "anim" / f"{cid}.webp")
        icon(A / "ui" / f"class_{cid}.png", IMG / "class" / f"{cid}.webp", 420)
        icon(A / "portraits" / f"hero_{cid}.png", IMG / "class" / f"hero_{cid}.webp", 200)
        trees = []
        for t in c["trees"]:
            sk = []
            for sid in t["skills"]:
                s = skills[sid]
                icon(A / "ui" / "skills" / f"{sid}.png", IMG / "skills" / f"{sid}.webp", 64)
                tier = int(s.get("tier", 1))
                sk.append({"id": sid, "name": s["name"], "desc": fill_desc(s), "type": s["type"], "element": s.get("element", "physical"),
                           "tier": tier, "req": [1, 1, 6, 12, 18][max(0, min(4, tier))], "max": s.get("max_rank", 20),
                           "mana": s.get("mana", 0), "cd": s.get("cooldown", 0), "tpl": s.get("desc", {}),
                           "params": {k: v for k, v in s.get("params", {}).items() if isinstance(v, (int, float, list))},
                           "syn": [{"id": k, "name": skills[k]["name"], "pct": v} for k, v in s.get("synergy", {}).items() if k in skills]})
            trees.append({"id": t["id"], "name": t["name"], "skills": sk})
        citem = next((b for k, b in items.items() if b.get("class") == cid and b.get("tier") == 1), None)
        if citem:
            icon(A / "items" / f"{citem['icon']}.png", IMG / "items" / f"{citem['icon']}.webp", 96)
        show = skills[SHOWCASE[cid]]
        data["classes"].append({
            "id": cid, "name": c["name"], "desc": c["desc"], "gender": c.get("gender", "m"), "base": c["base"],
            "show": {"id": SHOWCASE[cid], "name": show["name"]},
            "trees": trees,
            "item": {"name": citem["name"], "icon": citem["icon"], "slot": citem["slot"]} if citem else None,
            "sets": [set_entry(k, s) for k, s in sorted(sets["sets"].items(), key=lambda kv: kv[1]["qlvl"]) if s.get("class") == cid],
        })
    data["shared_sets"] = [set_entry(k, s) for k, s in sorted(sets["sets"].items(), key=lambda kv: kv[1]["qlvl"]) if not s.get("class")]

    for wid, w in sorted(words.items(), key=lambda kv: kv[1]["qlvl"]):
        glyphs = []
        for l in w["letters"]:
            b = items[f"glag_{l}"]
            glyphs.append({"g": b["glyph"], "latin": b["latin"]})
        data["words"].append({"name": w["name"], "meaning": w["meaning"], "letters": glyphs, "bases": w["bases"], "qlvl": w["qlvl"],
                              "mods": [mod_line(m, classes, tpl) for m in w["mods"]]})

    for kind in ("granat", "ametyst", "jaspis", "kristal", "vltavin", "achat"):
        for g in range(1, 5):
            icon(A / "items" / f"{kind}_{g}.png", IMG / "items" / f"{kind}_{g}.webp", 64)
        b = items.get(f"{kind}_4") or items[f"{kind}_1"]
        data["gems"].append({"kind": kind, "name": b["name"],
                             "socket": {k: [mod_line(m, classes, tpl) for m in v] for k, v in b["socket"].items()}})
    for extra in ("hromovy_kamen", "hromovy_kamen_maly", "hromovy_kamen_velky", "glag_a", "glag_v", "glag_ja",
                  "klic_vody", "klic_kamene", "klic_ohne", "klic_smrti", "kniha", "strana_kroniky"):
        icon(A / "items" / f"{extra}.png", IMG / "items" / f"{extra}.webp", 96)

    data["finder"] = finder_entries(items, uniques, sets, words, classes, later, tpl)
    data["shrines"] = [{"name": v["name"], "msg": v.get("msg"), "secs": v.get("effect", {}).get("duration", 0),
                        "mods": [mod_line(m, classes, tpl) for m in v.get("effect", {}).get("mods", [])]
                        or ([{"cs": "dar jedné z ostatních model, náhodně", "en": "one of the other idols' gifts, at random"}] if v.get("effect", {}).get("random") else [])}
                       for v in load("shrines").values()]
    champ = load("champions")
    data["champions"] = [{"name": v["name"], "special": v.get("special"), "aura": bool(v.get("aura")),
                          "mods": [mod_line(m, classes, tpl) for m in v.get("mods", []) + v.get("aura", [])]}
                         for v in champ.get("mods", {}).values()]
    data["superuniques"] = []
    for v in load("superuniques").values():
        w = str(v.get("where", ""))
        a, f = re.match(r"act(\d+)_floor(\d+)", w).groups() if re.match(r"act(\d+)_floor(\d+)", w) else (0, 0)
        data["superuniques"].append({"name": v["name"], "act": int(a), "floor": int(f),
                                     "monster": monsters.get(v.get("monster", ""), {}).get("name")})
    data["hirelings"] = [{"name": v["name"], "desc": v["desc"]} for v in load("hirelings").values()]
    data["bestiary"] = []
    for mid, m in monsters.items():
        if m.get("boss") or mid in ("permonik_obr", "zar_ptak") or int(m.get("act", 0)) < 1:
            continue
        p = A / "sprites" / "monsters" / f"{mid}_idle.png"
        if not p.exists():
            continue
        dst = IMG / "monsters" / f"{mid}.webp"
        dst.parent.mkdir(parents=True, exist_ok=True)
        im = rgba(p)
        bb = im.getbbox()
        if bb:
            im = im.crop(bb)
        im.thumbnail((160, 160), Image.LANCZOS)
        im.save(dst, "WEBP", quality=88, method=6)
        WROTE.add(dst)
        data["bestiary"].append({"id": mid, "name": m["name"], "act": int(m.get("act", 1)), "ai": m.get("ai", "melee"),
                                 "element": m.get("element", "physical"), "level": m.get("level", 1)})
    data["bestiary"].sort(key=lambda b: (b["act"], b["level"]))

    floors = [f for a in acts for f in a["floors"] if not (a["id"] == 4 and f["n"] == 5)]
    regular = [f for f in floors if "uber" not in f]
    data["facts"] = {
        "classes": len(classes), "skills": sum(len(t["skills"]) for c in classes.values() for t in c["trees"]),
        "acts": len(acts), "floors": len(regular), "bosses": len({f["boss"] for f in regular if f.get("boss")}),
        "tithes": len(floors) - len(regular), "sets": len(sets["sets"]), "set_pieces": sum(len(s["pieces"]) for s in sets["sets"].values()),
        "uniques": len(uniques), "words": len(words), "letters": sum(1 for k in items if k.startswith("glag_")),
        "gems": sum(1 for b in items.values() if b.get("slot") == "gem"), "monsters": len(monsters),
        "codex": len(codex), "books": len(books), "quests": len(quests), "levels": 100, "difficulties": 3,
    }

    # pictures of classes, skills and sets that are no longer on the site (hidden for an expansion)
    page = (OUT / "index.html").read_text()
    for d in ("anim", "class", "skills", "items", "monsters"):
        if not (IMG / d).exists():
            continue
        for f in sorted((IMG / d).iterdir()):
            if f not in WROTE and f"img/{d}/{f.name}" not in page:
                print("removed", f.relative_to(OUT))
                f.unlink()

    js = "window.PERMONIK = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (OUT / "data.js").write_text(js)
    print("facts", data["facts"])
    print("data.js", len(js) // 1024, "KB")


if __name__ == "__main__":
    main()
