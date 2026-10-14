#!/usr/bin/env python3
"""Android launcher icons from Permoník's portrait: game/assets/ui/app_icon{,_fg,_bg}.png."""
from pathlib import Path

from PIL import Image, ImageDraw

A = Path(__file__).resolve().parent.parent / "game" / "assets"
src = Image.open(A / "portraits" / "permonik.png").convert("RGBA")

src.resize((192, 192), Image.LANCZOS).save(A / "ui" / "app_icon.png")

# Adaptive icons mask the outer third away, so the portrait sits in the 288 px safe zone.
bg = Image.new("RGBA", (432, 432), src.getpixel((8, 8)))
bg.save(A / "ui" / "app_icon_bg.png")
fg = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
face = src.resize((288, 288), Image.LANCZOS)
mask = Image.new("L", (288, 288), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, 287, 287), 48, fill=255)
fg.paste(face, (72, 72), mask)
fg.save(A / "ui" / "app_icon_fg.png")
