# Permoník: Desátek z hlubin

*Permoník: The Tithe of the Deep*. A dark action RPG in the spirit of the first Diablo, set in Czech
silver mines and built from Slavic folklore.

The little bearded mine spirit Permoník greets you at the shaft head of Kutná Hora, gives you his lamp and
asks you to put down the monsters that are killing the miners. Over four acts you descend through the
mines of Kutná Hora, Příbram and Jáchymov into Nav, the Slavic underworld. You kill Klekánice, Vodník,
Bazilišek, Ježibaba, Kostěj Nesmrtelný and others. Each guardian you kill breaks a seal, and the lamp
burns brighter. Only at the very bottom do you find out who those seals were holding.

Every picture in the game is drawn in code in the same pencil-and-crayon style as the family's comic
books, only darker. All music and sound is synthesised.

## Features

- Eight heroes: **Havíř** (miner), **Zbojnice** (brigand), **Vědma** (wise woman), **Kovář** (smith),
  **Žrec** (priest of the old gods), **Vlkodlak** (werewolf huntsman), **Alchymistka** (alchemist) and
  **Loutkářka** (puppeteer). Each has three skill trees of four skills with up to 20 ranks; what they wear
  shows on them.
- Four acts, four towns and 17 procedurally generated mine floors. Lighting comes only from your lamp,
  and the lamp is an equipment slot of its own.
- Thirteen scripted boss fights from Czech and Slavic folklore, plus the final three-phase fight.
- Diablo-2-style items in four tiers: normal, magic, rare, set and unique; sockets with Czech gems and
  Glagolitic letters that spell words; thunderstone charms; class items and +skills; the smith's forge;
  a shared stash, gambling, and the guardians' tithes as endgame. Durability, repair, a grid inventory, a
  potion belt, vendors and shrines to Slavic gods.
- Waypoints (shaft cages), town portal, automap, quests and dialogue, and story slides between acts.
- Maximum level 100 across three difficulties: Normal, Noční můra (Nightmare) and Nav.
- Czech and English.

## Running

You need **Godot 4.6.3**, the standard (non-.NET) build:
<https://github.com/godotengine/godot-builds/releases/tag/4.6.3-stable>.

```sh
godot --path game              # play
godot --path game -e           # open in the editor
```

On the first run Godot imports the assets, which takes a minute.

### Controls

| Input | Action |
|---|---|
| Left mouse | Move, attack, pick up, talk, use (hold to keep moving or attacking) |
| Shift + left mouse | Attack in place |
| Right mouse | Use the skill bound to the right mouse button |
| Q W E R | Skills bound to the hotkeys (hover a skill in the skill panel and press the key to bind it) |
| 1–8 | Drink a potion from the belt |
| I / C / S / J | Inventory / character / skills / quests |
| Tab | Automap |
| Alt | Show items on the ground |
| P | Read a town portal scroll |
| Esc | Close panels / pause menu |

### Developer shortcuts

Arguments after `--` start the game directly in a level. These runs are not saved.

```sh
godot --path game -- --quick --class zbojnice --act 2 --floor 3
godot --path game -- --quick --floor 1 --autoplay --seconds 30   # bot fights and prints XP/loot
godot --path game -- --quick --act 1 --floor 4 --boss-test       # scripted run of that floor's boss
```

`--shot <file.jpg> --wait <s> [--panel inventory,character]` saves a screenshot and quits (used for the
website: run with `--resolution 1920x1080`).

To check the scripts parse: `godot --headless --editor --quit-after 300 --path game`.

## Repository layout

| Path | Contents |
|---|---|
| `game/` | The Godot project: `scripts/` (code), `data/` (all content as JSON), `assets/` (generated art, audio, fonts), `shaders/` |
| `art/` | Python drawing code and style data that render all of `game/assets/` images |
| `tools/` | Audio synthesiser and the data validator |
| `docs/` | The presentation website (`index.html`, `img/`, `screenshots/`, served by GitHub Pages from `/docs`) and the contracts: asset IDs and sizes (`assets.md`), data schema and formulas (`data-schema.md`), audio list (`audio.md`) |

### Art

Every PNG in `game/assets/` is rendered by the Python drawing code in `art/` (see `art/README.md`). It
writes into `game/assets/` (or `$PERMONIK_GAME/assets`). The rendered images are committed, so the game
runs without Python. The asset contract (IDs, sizes, anchors) is in `docs/assets.md`.

The hand-drawn style is our own: the pencil line, faces and handwriting were measured from Andrej's
drawings and the crayon textures scanned from the family's colouring. The drawing code is MIT like the
rest; the style data, scans and handwriting fonts are not (see `art/LICENSE.md`).

### Regenerating audio and checking data

```sh
python3 -m venv .venv && .venv/bin/pip install numpy
.venv/bin/python tools/audio_synth.py            # needs ffmpeg with libvorbis
python3 tools/check_data.py --strict
```

### Adding content

Classes, skills, monsters, items, affixes, uniques, shrines, acts, quests, dialogue and slides all live in
`game/data/*.json`. The schema is in `docs/data-schema.md`. A new act (for example a DLC) is a new entry
in `acts.json` plus its quests, dialogue and assets; boss mechanics go in
`game/scripts/actors/bosses/<boss_id>.gd`.

## Credits

Story, design and direction: Andrej Antas and family. Line style, faces and handwriting come from
Andrej's scanned pencil drawings; the crayon textures were scanned from his daughters' colouring.

Third-party:
- [Godot Engine](https://godotengine.org), MIT licence.
- Fonts Bangers and Patrick Hand, SIL Open Font License 1.1 (see `game/assets/fonts/`).

The folklore (Permoník, Vodník, Klekánice, Ježibaba, Kostěj, Vij and the rest) is public domain.

## Licence

The repository is split:

- **Code, game data, tools and docs**: [MIT](LICENSE). Fork it, learn from it, build your own ARPG on it.
- **`game/assets/`** (all art and audio): [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/).
  You may share them unchanged and non-commercially, with credit, but not modify or reuse them. The
  TataHand fonts are all rights reserved. Details: [game/assets/LICENSE.md](game/assets/LICENSE.md).
- Third-party fonts keep their SIL Open Font License.
