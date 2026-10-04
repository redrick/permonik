# art

Drawing code for **Permoník: Desátek z hlubin**. Renders every PNG in `../game/assets` (or
`$PERMONIK_GAME/assets`) plus `game/data/props.json`.

The style is our own: the pencil line, hatching, faces and the TataHand handwriting were measured from
Andrej Antas's drawings, and the crayon textures were scanned from the family's colouring. The code is MIT;
the style data, scans and handwriting fonts are CC BY-NC-ND 4.0 / all rights reserved (see `LICENSE.md`).

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python heroes.py            # npcs bestiary bosses world props items skills_icons ui fx slides
.venv/bin/python ui.py map_marker     # one asset;  --only <folder> for one group
```

The first run fills `style_data/cache/` (about 0.5 GB of tinted textures, not committed).

Base library copied from Velká a malá detektivka (`lib`, `style3`, `osobni`, `palette`, `chars3`,
`letter`, `style_data/`, `fonts/`); keep it close to the comic's copy, add new modules. `common.py` =
render helper. Asset contract: `../docs/assets.md`.
