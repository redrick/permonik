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
- **Hit chance** (D2): `2 * alvl/(alvl+dlvl) * AR/(AR+DEF)`, clamped 5–95 %. Player AR =
  `obratnost*5 + level*8 + to_hit`. Monster `armor` is its DEF; player DEF = sum of item armor
  (+ armor_pct). Monster AR = `mlvl*12 + to_hit`.
- **Resists** 0–100 (100 = immune, monsters only). Player resist cap 75; difficulty penalty
  0 / −30 / −60.
- **Item tiers**: base items come in up to three tiers (normal / kovaný / hlubinný) as separate
  entries sharing an `icon`. Rough ranges: one-hand dmg T1 1–15, T2 10–45, T3 30–110; body armor
  T1 6–40, T2 50–150, T3 160–420.
- **Attack speed**: `speed` ∈ fast (1.6 attacks/s), normal (1.25), slow (0.95), very_slow (0.75).

## Canonical stat names (used in item mods, buffs, shrines)

`sila obratnost magie vitalita vse_staty hp mana hp_pct mana_pct dmg_pct dmg_min dmg_max to_hit
armor armor_pct block fire_dmg lightning_dmg cold_dmg poison_dmg res_fire res_lightning res_cold
res_poison res_all life_steal mana_steal attack_speed cast_speed move_speed light_radius
gold_find magic_find hp_regen mana_regen thorns dmg_reduce skills crit xp_pct`
(`fire_dmg` etc. = added max damage; the engine adds a range `value/2 .. value`. `*_steal`, `crit`,
`*_pct`, `*_speed`, `*_find`, `xp_pct` are percent. `skills` = +N to all skills.)

## classes.json
```json
{ "havir": {
  "name": {"cs":"Havíř","en":"Miner"}, "desc": {...}, "gender": "m",
  "base": {"sila":30,"obratnost":20,"magie":10,"vitalita":25},
  "base_hp": 40, "hp_per_vit": 2.0, "hp_per_level": 2.0,
  "base_mana": 10, "mana_per_mag": 1.0, "mana_per_level": 1.0,
  "start_items": ["krumpac","kytel","lojovy_kahan","ziva_voda","ziva_voda","svitek_brana"],
  "trees": [{"id":"krumpac","name":{...},"skills":["uder_do_zily","rozrazka","otres","zurivost_hory"]}, …],
  "default_rmb": "uder_do_zily"
}}
```

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
crossbow, `projectile` fx.

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

## shrines.json
`{ "perun": {"name":{...}, "prop":"modla_perun", "effect":{"mods":[{"stat":"lightning_dmg","value":20}], "duration":120}, "msg":{...}} }`
Special effects: `{"heal":1}`, `{"random":1}` (Triglav), `{"curse":{"stat":"hp_pct","value":-10}}`.

## champions.json
`{ "names": [{"cs":"Lamač kostí","en":"Bonebreaker"}, …], "mods": {"rychly":{"name":{...},"mods":[{"stat":"move_speed","value":50},{"stat":"attack_speed","value":30}]}, …} }`
Mod names are nouns (*Rychlost, Kamenná kůže, Oheň*) so they need no gender.

## acts.json
```json
[ { "id": 1, "name": {...}, "subtitle": {...},
    "town": {"id":"hora","name":{...},"tileset":"town_hora","music":"town_hora",
             "npcs":["permonik","kosmas","kovar_hnevek","korenarka_dorota","senkyrka_bara"]},
    "dungeon": {"name":{...},"tileset":"hora","music":"mine_1"},
    "floors": [ { "n":1, "level":1, "style":"gallery", "size":[56,56], "water":0.0,
                  "monsters":["krysa","sotek","kostlivy_havir"], "density":1.0,
                  "boss":null, "quest_props":[] },
                { "n":4, "level":7, "style":"cave", "size":[48,48], "water":0.45,
                  "monsters":["utopenec","kostlivy_havir"], "boss":"vodnik",
                  "quest_props":["hrnek_dusicka"] } ],
    "quests": ["klekani","kostnice","dusicky","srdce_zvonu"],
    "intro": "act1_intro", "outro": "act1_end" } ]
```
`style` ∈ gallery (straight timbered tunnels + chambers), cave (cellular caves), mixed, lair
(one big boss arena + approach). `water` 0–1 = how much of the floor floods (slows, Vodník).

Vendor roles come from `npcs.json`.

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
{ "kniha_vodnik": { "title": {...}, "author": {...}, "source": "url", "licence": "public domain — …",
  "pages": {"cs": ["…", "…"], "en": ["…"]}, "codex": ["e_vodnik"], "where": "act1_floor4" } }
```
`where`: a floor (`act1_floor4`, lectern in a random open spot) or a town id (`hora`, lectern beside
the chronicler). Only public-domain texts or our own translations of them; record the basis in `licence`.

## slides.json
`{ "intro": [ {"image":"intro_1","text":{...}}, … ], "act1_end": [ … ] }`
