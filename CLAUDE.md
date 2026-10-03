# Permoník: Desátek z hlubin

A dark Diablo-1-style action RPG. Czech mining towns above, procedurally generated mines below,
Slavic folklore throughout. Four acts; Permoník, the friendly mine spirit, is the guide who turns
out to be the final enemy. Max level 100 over three difficulties (Normal, Noční můra, Nav).
The story bible lives in the author's private notes, not in this repo.

## Tech
- **Godot 4.6.3** portable binary: `~/apps/godot-4.6/Godot_v4.6.3-stable_linux.x86_64`.
  Run: `… --path game`. Parse check: `… --headless --editor --quit-after 300 --path game`.
- GDScript only, no plugins.
- Art is drawn in code in the private sibling repo `../permonik-art` (the family's pencil-and-crayon
  library, see `docs/assets.md`). It renders into `game/assets/`. Never recolour PNGs by hand; change the
  drawing code there and re-render.
- Audio is synthesised with numpy (`tools/audio_synth.py`) into `game/assets/audio/`.

## Layout
- `game/` Godot project. `game/data/*.json` = all content (schema: `docs/data-schema.md`).
  `game/scripts/` code, `game/scenes/` scenes, `game/assets/` generated art and audio.
- `docs/` = GitHub Pages site (`index.html`, `img/`, `screenshots/`; CZ/EN, no spoiler of the Permoník twist) + contracts (assets, data schema, audio). `tools/` helpers.

## Languages
Czech + English. Content text in JSON is `{"cs","en"}`; UI strings in `game/data/ui.json`.
`L.t(x)` translates a dict or a UI key.

## Licence split
Code/data/docs/tools: MIT. `game/assets/`: CC BY-NC-ND 4.0, TataHand fonts all rights reserved.
Never add the drawing code, style data, scans or the children's names to this repo.

## Conventions
- Few code comments: only what the code can't say.
- Sprites face right, feet at 8 px above the bottom edge, engine flips them.
- Permoník never casts a shadow (story clue). Everything else does.
