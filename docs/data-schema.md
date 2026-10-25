# Game data (game/data/*.json)

Everything a designer would tune lives in JSON so acts, classes and items can be added without code
(DLC = new act entry + assets). Text the player sees is always `{"cs": "…", "en": "…"}`.
Czech is the primary language; English is a real translation, not a gloss.

IDs are lowercase ASCII with underscores and match the asset names in `docs/assets.md`.

## Engine formulas (what the numbers mean)

- **Levels**: player max 100. Monster level `mlvl` = floor base level (acts.json) + difficulty offset
  (Normal 0, Noční můra +30, Nav +60), capped 99. Champions +2, bosses +3.
- **Monster scaling**: monsters.json gives values at the monster's `level`. At `mlvl` the engine
  multiplies HP by `F(mlvl)/F(level)` with `F(l) = l^1.6 + 4l`, damage by `D(mlvl)/D(level)` with
  `D(l) = l^1.15 + 3l`, armor by `mlvl/level`. Difficulty also multiplies HP (1, 1.6, 2.4).
- **XP** per kill = `xp_mult * 12 * mlvl^1.55`, reduced when the player outlevels the monster by
  more than 5. XP to next level is tuned in code so Normal ends around 30, Noční můra ~60, Nav ~85.
- **Player life** = `base_hp + vitalita*hp_per_vit + (level-1)*hp_per_level`; mana likewise with
  `magie*mana_per_mag`. 5 stat points and 1 skill point per level; quests can give more.
- **Weapon damage** = weapon roll × (1 + dmg_pct/100) + flat, × (1 + stat/100) where stat is the
  weapon's `dmg_stat` (sila or obratnost). **Spell damage** = skill roll × (1 + magie/100) ×
  (1 + elemental skill synergies).
- **Combat follows Diablo II.**
  - Hit chance `2 · alvl/(alvl+dlvl) · AR/(AR+DEF)`, clamped 5–95 %.
  - Player AR = `(obratnost·5 − 35 + class ar_bonus + to_hit) · (1 + to_hit_pct/100)`; no AR per level, the
    melee skills carry their own `ar_pct` instead. Class `ar_bonus`: Havíř +20, Zbojnice +15, Vědma −10.
  - Player DEF = item armour (+ armor_pct) + obratnost/4. Monster AR = `mlvl·6 + 6 + to_hit`, hit chance on
    the player capped at 85 %.
  - Block = `blocking · (obratnost − 15) / (level · 2)`, cap 75 %; while moving a third of that, cap 25 %.
    Blocking = the shield's `block` + `block` from items.
  - Hit recovery: a blow worth more than 1/12 of the hero's life (1/8 of a monster's, 1/4 of a boss's)
    staggers and breaks off the current swing or spell. Hero stagger 0.4 s / (1 + FHR).
  - Speed from gear (`attack_speed`, `cast_speed`, `hit_recovery`) is diminished: `120·x/(120+x)`.
  - `crit` = deadly strike (double physical damage). `crushing_blow` takes 1/4 of a normal monster's
    remaining life (1/8 champions and bosses, half at range), physical resistance applies.
  - Physical damage taken: × (1 − dmg_reduce_pct/100, cap 50 %), then − dmg_reduce (min 1).
  - Life/mana leech × 1 / 0.67 / 0.5 on Normal / Noční můra / Nav.
- **Resists** 0–100 (100 = immune, monsters only). Player resist cap 75; difficulty penalty
  0 / −30 / −60.
- **Item tiers**: base items come in four tiers (normal qlvl 1–22 / kovaný 25–46 / hlubinný 55–76 /
  navský 79–95) as separate entries sharing an `icon`; navský ≈ hlubinný × 1.75 damage, × 1.7 armour. Rough ranges: one-hand dmg T1 1–15, T2 10–45, T3 30–110; body armor
  T1 6–40, T2 50–150, T3 160–420.
- **Attack speed**: `speed` ∈ fast (1.6 attacks/s), normal (1.25), slow (0.95), very_slow (0.75).

## Canonical stat names (used in item mods, buffs, shrines)

`sila obratnost magie vitalita vse_staty hp mana hp_pct mana_pct dmg_pct dmg_min dmg_max to_hit
armor armor_pct block fire_dmg lightning_dmg cold_dmg poison_dmg res_fire res_lightning res_cold
res_poison res_all life_steal mana_steal attack_speed cast_speed move_speed light_radius
gold_find magic_find hp_regen mana_regen thorns dmg_reduce skills crit xp_pct to_hit_pct crushing_blow
hit_recovery dmg_reduce_pct`
(`fire_dmg` etc. = added max damage; the engine adds a range `value/2 .. value`. `*_steal`, `crit`,
`*_pct`, `*_speed`, `*_find`, `xp_pct` are percent. `skills` = +N to all skills. `crit` = deadly strike, `crushing_blow`, `hit_recovery` (FHR), `to_hit_pct`,
`dmg_reduce_pct` are percent.)

## classes.json
```json
{ "havir": {
  "name": {"cs":"Havíř","en":"Miner"}, "desc": {...}, "gender": "m",
  "base": {"sila":30,"obratnost":20,"magie":10,"vitalita":25},
  "base_hp": 40, "hp_per_vit": 2.0, "hp_per_level": 2.0,
  "base_mana": 10, "mana_per_mag": 1.0, "mana_per_level": 1.0,
  "start_items": ["krumpac","kytel","lojovy_kahan","ziva_voda","ziva_voda","svitek_brana"],
  "loot": {"weapons": ["pick","axe","mace","club","flail","sword"], "offhand": ["shield"]},
  "trees": [{"id":"krumpac","name":{...},"skills":["uder_do_zily","rozrazka","otres","zurivost_hory"]}, …],
  "default_rmb": "uder_do_zily"
}}
```

## expansions.json
```json
{ "cernobog": { "n": 1, "name": {...}, "pitch": {...}, "released": false, "classes": ["zrec", "loutkarka"] } }
```
A class listed under an expansion that isn't `released` stays in classes.json but can't be picked for a
new hero; its class items, sets and +skill affixes don't drop and its sets are left out of the
collection (unless already found). `DB.classes` holds the playable classes, `DB.all_classes` all of them
(heroes of a hidden class still load). `-- --all-classes` plays them anyway; `tools/site_build.py` skips
them. Base game: havir, zbojnice, vedma, kovar.

## skills.json
```json
{ "rozrazka": {
  "class": "havir", "tree": "krumpac", "tier": 2,          // tier 1..4 → required level 1, 6, 12, 18
  "name": {...}, "desc": {...},                            // desc may use {dmg} {radius} {duration} {count} …
  "type": "melee_arc",
  "element": "physical",                                   // physical fire lightning cold poison
  "mana": [4, 0.4], "cooldown": 0,                         // [base, per extra rank]
  "params": {"dmg_pct": [130, 12], "arc": [100, 0]},       // every param is [base, per extra rank]
  "synergy": {"uder_do_zily": 4},                          // % dmg per rank of other skill
  "max_rank": 20
}}
```
Types the engine implements (params in brackets):
- `melee` single target (dmg_pct, hits, stun) · `melee_arc` cone (dmg_pct, arc deg) · `stomp` ring
  around self (dmg_pct, radius, stun) · `leap` jump to target + area (dmg_pct, radius)
- `spin` dash through enemies along a line (dmg_pct, length)
- `projectile` (dmg | dmg_pct, speed, count, spread, pierce, explode_radius, fx, returns: 0/1)
- `chain` (dmg, jumps, range) · `nova` around self (dmg, radius, freeze/slow) · `cone` breath
  (dmg, range, arc, slow) · `area` at cursor (dmg, radius, duration, tick, delay) · `wall` line at
  cursor (dmg per s, length, duration) · `trap` placed (dmg, radius, count, duration)
  · `summon` (id, count, duration, dmg) · `buff` timed on self/party (stat mods, duration)
  · `cloud` (radius, duration, effect) · `passive` (stat mods per rank, no cast)
`dmg` params are `[min, max]` pairs per rank: `"dmg": [[3,7],[2,3]]` = 3–7 at rank 1, +2–3 per rank.

## monsters.json
```json
{ "kostlivy_havir": {
  "name": {...}, "gender": "m", "act": 1, "level": 2,
  "ai": "melee",          // melee ranged caster swarm charger exploder phaser thief summoner flyer boss
  "hp": 18, "dmg": [2, 5], "armor": 10, "speed": 70, "attack_range": 50, "attack_cd": 1.4,
  "element": "physical", "resist": {"fire":0,"lightning":0,"cold":25,"poison":100},
  "xp_mult": 1.0, "size": 18,                 // collision radius px
  "pack": [3, 6],                              // normal pack size
  "projectile": null,                          // fx id for ranged/caster
  "abilities": [],                             // e.g. "steal_gold" "explode" "drain_mana" "light_drain" "revive" "teleport" "petrify_spit" "heal_pack" "howl"
  "light": null,                               // {"color":"#9fd0ff","radius":2} glowing monsters
  "boss": false
}}
```
Bosses add: `"boss": true`, `"title": {...}` (e.g. "Strážkyně Vodní pečeti"), `"lines":
{"aggro": {...}, "half": {...}, "death": {...}}`, `"drops": ["unique_id", …]`, `"seal": "voda"` for
the four act guardians. Boss mechanics are scripted per id in code; numbers stay here.

## items_base.json
```json
{ "kord": {
  "name": {"cs":"Kord","en":"Rapier"}, "gender": "m", "icon": "kord",
  "slot": "weapon", "kind": "sword", "two_handed": false, "size": [1,3],
  "dmg": [2, 8], "dmg_stat": "obratnost", "speed": "fast",
  "req": {"level": 1, "sila": 15, "obratnost": 20}, "durability": 30, "price": 120, "qlvl": 1, "tier": 1
}}
```
`slot` ∈ weapon offhand head body belt lamp ring amulet consumable gold quest. Armour pieces use
`armor: [min,max]`; shields add `block` (%); lamps add `light` (radius in tiles, 2–6); belts add
`belt_slots` (extra potion slots, 0–4); consumables have `use: {"heal_pct":40}`, `{"mana_pct":40}`,
`{"rejuv":1}`, `{"portal":1}`, `{"identify":1}` and `stack: 1`. Ranged weapons: `kind` bow or
crossbow, `projectile` fx. Quest items may carry `"until": [quest ids]`: once all of those are done
the item leaves the bag and stash (on quest done and on load).

## affixes.json
```json
{ "prefixes": [ { "id":"perunuv_1", "qlvl":3, "weight":10, "slots":["weapon"],
    "name": {"cs":{"m":"Perunův","f":"Perunova","n":"Perunovo"}, "en":"Perun's"},
    "mods":[{"stat":"lightning_dmg","min":3,"max":8}] } ],
  "suffixes": [ { "id":"vlka_1", "qlvl":1, "weight":10, "slots":["weapon","ring","amulet"],
    "name": {"cs":"vlka","en":"of the Wolf"}, "mods":[{"stat":"life_steal","min":2,"max":4}] } ] }
```
Magic item name: `<prefix by gender> <base name> <suffix>` → *Perunova valaška vlka*. Slot
groups allowed in `slots`: weapon, ranged, offhand, shield, head, body, belt, lamp, ring, amulet,
armor (= head+body+shield+belt), jewelry (= ring+amulet), any.

## uniques.json
```json
{ "janosikuv_opasek": { "name": {...}, "base": "siroky_opasek", "qlvl": 18,
  "mods": [{"stat":"sila","min":15,"max":20}, {"stat":"life_steal","min":5,"max":7}],
  "flavor": {"cs":"Dokud ho nosil, žádná kulka…","en":"…"} } }
```
Optional `"gender": "m"|"f"|"n"` when the name's noun differs from the base's (Czech engraved names agree
with it). `rare_names.json` first words carry `"g"` for the same reason.

## shrines.json
`{ "perun": {"name":{...}, "prop":"modla_perun", "effect":{"mods":[{"stat":"lightning_dmg","value":20}], "duration":120}, "msg":{...}} }`
Special effects: `{"heal":1}`, `{"random":1}` (Triglav), `{"curse":{"stat":"hp_pct","value":-10}}`.

## champions.json
`{ "names": [{"cs":"Lamač kostí","en":"Bonebreaker"}, …], "mods": {"rychly":{"name":{...},"mods":[{"stat":"move_speed","value":50},{"stat":"attack_speed","value":30}]}, …} }`
Mod names are nouns (*Rychlost, Kamenná kůže, Oheň*) so they need no gender.

## superuniques.json
Named monsters with fixed powers, one place each (D2 superuniques). They spawn every visit with minions,
count as champions, give ×5 XP and drop one extra guaranteed-magic item usable by the hero.
`{ "stary_farar": {"monster": "kostlivy_havir", "where": "act1_floor1", "name": {...}, "title": {...},
"mods": ["silny","kamenny"] (champion mod ids), "minions": ["kostlivy_havir", 3, 4], "hp": 1.6, "line": {...}} }`
`line` is shouted when it wakes.

## hirelings.json
Companions hired at the innkeeper (`Pomocník`), one at a time, saved in the hero's `merc`. Level = hero
level; `hp`, `armor`, `dmg`, `to_hit`, `cost` are `[base, per level]`. `look` is the hero class whose
layered drawings (with the hireling's gear) it wears. Slots weapon/head/body; `weapons` = allowed kinds.
Revive at the inn for half the hire cost; a new hire returns the old one's gear to the pack.
`{ "tovarys": {"name", "desc", "gender", "look": "havir", "ai": "melee"|"ranged", "range": 62,
"weapons": [...], "hp": [70, 11], "armor": [6, 2.2], "dmg": [3, 8], "to_hit": [20, 7], "cost": [120, 45], "names": [...]} }`

## acts.json
```json
[ { "id": 1, "name": {...}, "subtitle": {...}, "goal": {...},   // goal = the act's main thread in one line (tracker, quest log)
    "town": {"id":"hora","name":{...},"tileset":"town_hora","music":"town_hora",
             "npcs":["permonik","kosmas","kovar_hnevek","korenarka_dorota","senkyrka_bara"]},
    "dungeon": {"name":{...},"tileset":"hora","music":"mine_1"},
    "floors": [ { "n":1, "level":1, "styles":["gallery","mixed"], "size":[56,56], "water":0.0,
                  "monsters":["krysa","sotek","kostlivy_havir"], "density":1.0,
                  "boss":null, "quest_props":[] },
                { "n":4, "level":7, "styles":["lair","cave"], "size":[48,48], "water":0.45,
                  "monsters":["utopenec","kostlivy_havir"], "boss":"vodnik",
                  "quest_props":["hrnek_dusicka"],
                  "rules": {"arena":[7,5], "min_path":40,
                            "place": {"dub": {"far":0.5, "from_boss":12}, "truhla_kostej": {"next_to":"dub"}}} } ],
    "quests": ["klekani","kostnice","dusicky","srdce_zvonu"],
    "intro": null } ]
```
`style` ∈ gallery (straight timbered tunnels + chambers), cave (cellular caves), mixed, lair
(one big boss arena + approach). `water` 0–1 = how much of the floor floods (slows, Vodník).
`intro` = film or slides played when `next_act` enters the act; act endings are `slide:<id>` actions in dialog.json.

Vendor roles come from `npcs.json`.

### Floor generation

Every floor and town is generated again each time a hero is loaded from the menu (`Game.new_session`
rerolls `Game.session_seed`). Within one session a floor comes back as it was left: the same plan, props
and packs (populating is seeded from the floor seed), with the explored cells, killed monsters (by spawn
order) and opened chests, broken barrels and used shrines kept in `Game.floor_state` (not saved), and
loot on the ground in `floor_loot` (saved). A quest item lies on its floor only while a quest of that
act still has to pick it up (`Game.quest_item_wanted`) and this floor's copy wasn't taken
(`flags.took:<act>:<floor>:<id>`). What stays fixed across sessions are the rules:

- **Layout**: one of `styles` (`gallery` rooms and tunnels, `mixed` roughened galleries, `cave` cellular
  caves, `lair` arena with side caves), size ±10 %, water ±30 %. A draw that breaks the rules is thrown
  away (up to 12 tries): the stairs down must be at least `rules.min_path` steps away (default
  0.35 × (w+h)), the boss room at least 60 % of the longest walk.
- **Boss floors**: the boss gets its own room (`rules.arena` = radii in cells, default 7×5) at the far
  end, and the stairs down are behind it.
- **Story first**: `quest_props` are placed before anything random. Defaults: an item to pick up lies
  past half of the longest walk and away from the boss room; a prop on a boss floor stands in a ring
  around the boss room; any other prop past 45 %. `rules.place.<id>` overrides it with `far` (share of the
  longest walk), `from_boss` (cells), `spacing` (cells from others of its kind), `next_to` (an id placed
  earlier on this floor).
- **The rest**: shrines ≥ 12 cells apart, chests ≥ 8, books past 30 %, monster packs ≥ 6 cells apart,
  never within 9 cells of the stairs or inside the boss room. Each visit uses all but one of the floor's
  monster types (15 % of packs may still pick from the whole pool) and ±15 % density, drawn per session.
- **Towns** (`scripts/world/town_layout.gd`): shaft on the north edge with the cage beside it, the well
  (camp fire) square in the middle with arrival point and stash, the chronicler's lectern on the square,
  smith, inn and healer each with its keeper at the door 7–16 cells from the square, the landmark
  further out, Fabián and the Třemšínský mužíček among the trees at the rim, footpaths from the square to
  the shaft and each door. Every NPC and point must be reachable or the town is drawn again.

## Loot systems

- **Rarities**: normal, magic (1 prefix and/or 1 suffix), rare (3–6 affixes, max 3 of each kind, never two
  of one family or two on one stat, two-word name from `rare_names.json`), set (`sets.json`), unique
  (`uniques.json`). A plain item may drop with sockets (15 %).
- **Class-only bases** carry `"class"` and a `"look"` (the worn layer to draw). `class_<id>` and
  `tree_<id>` stats add ranks to a class's skills or one tree; on a class item they only roll for that
  class, four times as often; elsewhere at a third of the weight.
- **Sockets** (`max_sockets` by slot, size, tier). Gems (`slot: gem`, six stones × four grades) and letters
  (`slot: letter`, 21 Glagolitic letters on a D2-rune ladder, each step a quarter rarer) carry
  `"socket": {"weapon": […], "armor": […], "shield": […]}`. Drop one onto an item to set it.
- **words.json**: `{"letters": ["g","r","o","m"], "bases": ["weapon"|"armor"|"body"|"shield"], "mods": […]}`.
  A plain (white) item whose sockets hold exactly those letters, in order, speaks the word: name in
  gold, word mods on top of the letters' own.
- **Charms** (`slot: charm`, small/normal/great thunderstones) are always magic, roll only charm-friendly
  stats at 35 / 60 / 100 % strength (great ones also `tree_*`), and count while in the bag.
- **sets.json**: `{"sets": {id: {"name", "class"?, "pieces": [...], "bonus": {"2": [...], "3": [...], "full": [...]}, "flavor"}},
  "items": {id: {"set", "base", "name", "qlvl", "mods"}}}`. Bonuses add up by pieces worn.
- **The forge** (smith, `scripts/core/forge.gd`): gem and letter upgrades, sockets, unsocketing, rerolls,
  tier upgrades, potions, and the four tithe seals into *Permoníkův desátek*.
- **Stash** 12×10 per hero plus a shared 12×10 chest (`user://saves/_shared_stash.json`). **Gambling** at
  the innkeeper: you buy a base blind; 3 % unique, 4 % set, 18 % rare, the rest magic.
- **Smart drops**: 35 % of a normal monster's equipment drops (champions 50 %, bosses 60 %, half the smith's
  stock) draw only bases the hero can use soon: the class's `loot` weapon/offhand kinds, no other class's
  items, required level ≤ hero level + 3.
- **Tithes** (endgame): on Noční můra (30 %) and Nav (45 %) the four seal guardians drop their key; the
  ferryman in Nav takes a key to an `uber` floor (act 4, n 11–14, `"uber": {"hp", "dmg", "key", "seal"}`):
  the same fight at ×3 life ×1.6 damage, dropping its seal and three rich items. `uber` floors are not
  counted, get no waypoint, and their stairs lead back to camp.
- **Crafted** (orange, `Forge.CRAFTS`): magic item + letter (weapon *Slovo*, armour/shield *Našь*,
  ring/amulet/belt/lamp *Dobro*) + a cut gem (grade 3+). The stone picks the recipe's fixed properties,
  then 1–4 rare affixes; ilvl = hero level / 2 + item ilvl / 2, required level +5.
- **Ethereal** (`eth`): weapons and armour drop ethereal at 3 / 5 / 8 % by difficulty: ×1.5 base damage
  or armour, half durability, −10 Str/Dex requirement, never repaired.
- **Smith favours**: a quest `"service": "imbue"|"socket"|"personalize"` sets `flags.svc_<kind>` (per
  difficulty); any smith spends it once. Imbue = plain item → rare at hero level + 4 (best of three rolls);
  socket = plain max / magic 2 / other 1; personalize = hero's name in the item name.
- **Charm-speaking** (healers, D3 mystic): pay gold to reroll one affix of a magic/rare/crafted item; after
  that only that affix can change (`locked`), each reroll costs ×1.4.
- **Peddler** (třemšínský mužíček, D1 Wirt): one rare/set/unique item per hero level, a fee to look, ×3 price.
- **Collection**: `known["grail:u|s|w:<id>"]` for every unique, set piece and word held identified; Kronika
  tab *Sbírka*. **Upgrade arrow** and "if you wear it" deltas come from `CharData.preview`.
- **Loot filter** (`settings.cfg` `loot_filter` 0–2) hides plain, then also magic weapons/armour on the
  ground; Alt shows them dimmed. Alt also shows affix roll ranges in tooltips.

## npcs.json
`{ "kovar_hnevek": {"name":{...}, "role":"smith", "portrait":"kovar_hnevek"} }`
role ∈ smith (buys/sells weapons+armour, repairs), healer (heals free, sells potions), inn
(sells scrolls, belts, rings, gossip), chronicler (identifies free, lore), guide (Permoník, main
quests), ghost, other.

## dialog.json
```json
{ "permonik": [
   { "if": ["quest:klekani:none"],
     "lines": [ {"who":"permonik","text":{...}}, {"who":"hero","text":{...}} ],
     "do": ["quest_start:klekani"] },
   { "if": ["always"], "lines": [ … ] } ],
  "_gossip": { "senkyrka_bara": [ {"cs":"…","en":"…"} ] } }
```
The engine shows the **first** entry whose conditions all hold. Conditions:
`always`, `quest:<id>:none|active|done`, `quest:<id>:step=<step_id>`, `act:<n>`, `flag:<name>`,
`!flag:<name>`, `class:<id>`, `has:<item>`. Actions (`do`): `quest_start:<id>`,
`quest_step:<id>:<step>`, `quest_done:<id>`, `flag:<name>`, `give:<item>`, `take:<item>`,
`gold:<n>`, `xp:<n>`, `heal`, `stat_points:<n>`, `skill_points:<n>`, `slide:<seq>`,
`next_act`, `respec`. Hero lines may use `{class}`-specific variants by adding
`"text_<class>": {...}`.

## quests.json
```json
{ "klekani": { "act": 1, "giver": "permonik", "main": true, "name": {...},
  "steps": [ {"id":"find","text":{...},"goal":{"kill":"klekanice"}},
             {"id":"report","text":{...},"goal":{"talk":"permonik"}} ],
  "reward": {"xp": 400, "gold": 200, "skill_points": 1} } }
```
Reward keys: `xp`, `gold`, `skill_points`, `stat_points`, `item`/`items`, `service` (smith favour).
Goals: `{"kill": monster}`, `{"pick": item}`, `{"talk": npc}`, `{"use": prop}`,
`{"reach": "act1_floor3"}`.

## lore.json
Kronika pages and boss-death lines that unlock with quests:
`{ "kronika_1": {"title":{...}, "text":{...}} }`

`kind`: `kronika` (story leaves), `boss` (death lines, after the kill), `bestiar` (in-world line about a
monster; shown on top of its codex entry, bosses only after the kill).

## codex.json
Encyclopedia in the Kronika (key K): real folklore, history and places behind every name.
```json
{ "e_perun": { "cat": "god", "title": {...}, "text": {...}, "game": {...},
  "refs": {"shrine": ["perun"], "unique": ["perunova_sekera"]}, "see": ["e_veles"] } }
```
`cat`: `creature`, `place`, `person`, `god`, `item`, `term` (= Kronika tabs). `game` (optional) says how
the game bends it. An entry unlocks the first time the player meets any of its `refs`; no `refs` =
always open. Ref kinds and when they fire: `monster` (it notices you), `npc` (talk), `town` / `floor`
(`act2_floor3`, on arrival), `item` / `unique` (pickup), `shrine` (use), `quest` (start),
`class` (own class), `book` (read). Knowledge is kept per save in `known` and survives difficulty changes.

## books.json
Readable public-domain legends, one lectern (`kniha` prop) each, re-readable in the Kronika's Books tab.
```json
{ "kniha_vij": { "title": {...}, "author": {...}, "source": "url", "licence": "public domain — …",
  "pages": {"cs": ["…", "…"], "en": ["…"]}, "codex": ["e_vodnik"], "where": "act1_floor4" } }
```
`where`: a floor (`act1_floor4`, lectern in a random open spot) or a town id (`hora`, lectern beside
the chronicler). Only public-domain texts or our own translations of them; record the basis in `licence`.

## slides.json
`{ "intro": [ {"image":"intro_1","text":{...}}, … ], "act1_end": [ … ] }`
Still pictures, now only the fallback for a sequence id that has no cinematic.

## cinematics.json
`{ "intro": { "title": {...}, "when": {...}, "music": "town_hora", "lines": { "a": {...}, "b": {...} } } }`
One entry per animated cinematic, keyed by the same ids `slide:<id>` and acts' `intro` use;
`Main.play_slides` plays the cinematic instead of the slides whenever `CinFilms` knows the id.
`title`/`when` label the card on the main menu's Story page, `music` plays during it, `lines` are the
narration keys the choreography in `scripts/ui/cin_films.gd` says. Films unlock on the Story page
once seen (`settings.cfg` `[cinema] seen`) or once any save is past that point.

## cinema_layers.json (generated)
Written by `art/cinema.py`, never by hand: `{ "intro/bell": {"x","y","w","h","cw","ch","pts":{"pivot":[x,y]}} }`.
Each layer is a crop of its shot canvas (`cw`×`ch` px, y down) saved as `assets/cinema/<name>.webp`;
`pts` are named anchors (pivot, lamp flames, window lights…) the choreography hangs things on.
