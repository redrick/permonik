# Asset contract

All art is drawn in code in `art/` with the Velká a malá detektivka library ( `lib.py`,
`style3.py`, `osobni.py`, `palette.py`, `chars3.py`, `letter.py`, `style_data/`, `fonts/`). Keep those
close to the comic's copy (they only lost the family's own characters); append colours to `palette.py`,
put new drawing code in new modules.

Render with `common.py` there: `render(name, w_px, h_px, draw, folder, paper=False)`. Sizes are final
pixels; the draw function gets a `Box` in points (`px / 2`). `common.FEET` = 4 pt (8 px) is the
feet line for every standing figure. Run with `.venv/bin/python <module>.py` (optionally
`--only <folder>` and names). Each module ends with `if __name__ == "__main__": common.run({...})`.

## Look

Same pencil line, crayon fills, faces and paper grain as the comics, but darker:
- Palette pushed toward night: slate, soot, rust, bone, moss, deep violet, cold blue. Warm accents
  (lamp flame, embers, blood-red, gold) are rare and therefore loud.
- Heavier hatching for shadow (`style3.hatch`), more `offset_shadow`, darker undersides.
- Creatures stay readable silhouettes at small size: strong outline, one clear light area
  (face/eyes/glow), big shapes first. Eyes of monsters often glow (yellow/green/red).
- Scary, not gory. No gore splashes, no body horror close-ups. Bones, rags, glowing eyes, claws OK.
- **Permoník never has a ground shadow.** Everything else standing on the ground draws
  `style3.cast_shadow(...)` under its feet.
- Every sprite faces **right**. The engine flips for left.

## Folders and sizes (game/assets/...)

| Folder | What | Size |
|---|---|---|
| `sprites/heroes/` | in layers (`heroes_gear.py`), so worn gear shows: `<class>/<pose>/<layer>[.<look>].png`, pose ∈ idle, walk1, walk2, attack, cast, hit, dead. Layers back to front: headgear_back, back, body_far, weapon_far, lamp_far, hand_far, offhand, legs, body, belt, lamp, weapon_belt, body_near, weapon, hand, head, headgear. Look = the base item's `icon`; `default` = what the class wears with the slot empty (a `kytel` counts as empty). The game stacks them per gear (`scripts/core/hero_look.gd`). `sprites/heroes_big/<class>/idle/` = the same at 600×600 for the hero list | 240×240 each, figure ~130 px tall, feet at FEET, centred. `dead` lies on the ground in the same canvas. |
| `sprites/npcs/` | `<npc>.png` + `<npc>_talk.png` | 200×240, figure ~130 px (children / small folk smaller) |
| `portraits/` | `<npc>.png` (also heroes: `hero_<class>.png`, bosses: `boss_<id>.png`) | 256×256, head and shoulders, dark vignette background filling the square |
| `sprites/monsters/` | `<id>_idle.png`, `<id>_walk.png`, `<id>_attack.png` (walk optional) | per creature, all poses of one creature **same canvas**, feet at FEET, centred. Small 96–128, medium 192–224, large 256–320, bosses 320–512 |
| `sprites/fx/` | projectiles and effects (see list) | small, centred, pointing right |
| `tiles/<set>/` | `floor_0..3.png` 64×64 · `wall_0..2.png` 64×96 (top 64 px = rock top seen from above, bottom 32 px = front face) · `floor_deco_0..3.png` 64×64 transparent overlays (cracks, rubble, rails, puddles, bones) · towns also `path_0..2.png` 128×128 soft footpath decals drawn centred on a 64 px cell so neighbours overlap | |
| `props/` | `<id>.png`, base (ground contact) at bottom-centre with FEET margin | see list |
| `items/` | `<icon>.png`, inventory icon, `w*56 × h*56` px for an item `w×h` cells, item centred, transparent | |
| `ui/` | HUD, panels, cursor, title, menus | see list |
| `ui/map_*`, `ui/minimap_*` | automap (`map_art.py`): `map_sheet` 1600×1000 paper, `minimap_disc` / `minimap_frame` 280×280 (map radius 118 px), seamless crayon swatches `map_floor`, `map_floor_town`, `map_water` 256×256, pencil symbols `map_stairs_down/up`, `map_cage`, `map_shrine`, `map_quest`, `map_book`, `map_npc`, `map_hero`, `map_portal`, `map_boss` 32×32 | |
| `ui/skills/` | `<skill_id>.png` | 64×64, opaque square icon |
| `slides/` | story illustrations | 1920×1080, `paper=True` |

Tile sets: `hora`, `brdy`, `jachymov`, `nav` (mines), `town_hora`, `town_pribram`, `town_jachymov`,
`town_nav` (towns: `floor_*` = ground, `wall_*` = cliff/house-wall block, `floor_deco_*` = path,
grass tufts, cobbles, puddles).

## Content IDs

### Heroes
havir (m, miner: pick-axe, leather cap with lamp hook, smock, apron *flek* worn at the back, heavy boots) ·
zbojnice (f, Valašsko brigand: valaška axe, wide belt, embroidered shirt, braids, crossbow on back) ·
vedma (f, Šumava wise woman: shawl, herbs at belt, staff with antlers, red threads, bone beads).

### NPCs (`sprites/npcs/` + `portraits/`)
| id | Act | Who |
|---|---|---|
| permonik | all | small bearded miner (knee-high to a human), white smock, red cap, lamp with cold blue-white flame, kind wrinkled face. **No shadow.** Also `permonik_grin.png` (sly) |
| kosmas | all | old chronicler, robe, spectacles, book under arm |
| kovar_hnevek | I | Hora smith, burly, leather apron, hammer |
| korenarka_dorota | I | herb woman, headscarf, basket |
| senkyrka_bara | I | innkeeper, apron, jug |
| kovar_vojtech | II | Příbram smith, young, soot |
| korenarka_medulina | II | Medulína, the good Brdy herb woman, flowers in hair |
| hostinsky_kuba | II | fat innkeeper, moustache |
| fabian | II | Brdy forest spirit: body of spruce cones, moss beard, hat, bag, pipe; a cursed knight |
| tremsinsky_muzicek | II | bark-faced little man, knee-long white beard |
| kovar_krystof | III | Jáchymov mint-smith, coin pouch |
| lekarnik_agricola | III | Georgius Agricola, town physician, Renaissance cap |
| senkyrka_rozina | III | barmaid, tired |
| predak_matej | IV | dead foreman, pale/translucent blue, extinguished lamp |
| anicka | IV | drowned miner's daughter (ghost girl, ~10 yrs), wet hair, holds a teacup |
| prevoznik | IV | ferryman of the Smorodina, hooded, pole |

### Monsters (`sprites/monsters/<id>_{idle,walk,attack}.png`)
Regular: krysa (rat, 96), sotek (imp, 128), kostlivy_havir (skeleton miner with pick, 192),
kostlivy_kusinik (skeleton crossbowman, 192), bludicka (will-o'-wisp: glowing pale woman-shaped
flame, floats, 128), utopenec (drowned man, green-grey, weed, 224), netopyr (bat, 96),
hejkal (hairy forest wild man, 256), vlk (wolf, 192), vlkodlak (werewolf, 288), diva_zena (wild
woman, long hair, bark skin, 224), mura (nightmare: moth-winged hag, 192), bubak (bogeyman: sack
of shadows with eyes, 224), kamenny_had (stone serpent, 224), cert (Czech devil: fur, horns, tail,
hoof, chain, 224), ohnivy_muzik (fire sprite, 128), svetlonos (lantern ghost with a pumpkin-like
lantern head, 224), upir (vampire in burial shroud, 224), smolak (pitch golem with green glow,
256), navka (dead maiden, pale, long hair, 224), cerny_pes (black dog, red eyes, 192),
bes (demon, gaunt, horned, 256), permonicek (tiny copies of Permoník with knives, grinning, 96),
kostejuv_nesmrtelny (skeleton knight in rusty armour, 224).

Bosses: klekanice (hag in white sheet, bell, 320), kostnik (lord built of bones, crown of skulls,
384), vodnik (Vodník/Hastrman: green coat with dripping tails, red hat, frog face, pipe,
teacups on belt, 352), megera (witch, crooked, cauldron ladle, 320), prokop (wild knight on
skeletal horse, 448), bazilisek (rooster-headed serpent-dragon, 416), strzyga (two-faced hag,
second face on the back of the head, 320), ohnivec (fat čert minter with hammer and coins, 352),
jezibaba (old witch with long nose and shovel, 320) + chaloupka (walking hut on a chicken leg,
448), san (three-headed dragon, 512), vij (huge earthen demon with eyelids to the ground, 448;
also `vij_open.png` with eyes open), kostej (gaunt skeletal king, crown, 352),
permonik_obr (Permoník's true form: giant of rock, silver ore and roots, the cold lamp in his chest,
512).

### FX (`sprites/fx/`)
arrow, bolt, valaska (thrown axe), naloz (black-powder charge with fuse), firebolt, ice_shard,
spark, rock, bone, coin (burning tolar), web, morana (straw Morana effigy), flame (fire wall/burn
frame), blood (dark splat decal), soul (small pale soul light), zar_ptak (the firebird summon,
192×128). Sizes: projectiles 32–64 px, decals 64–96 px.

### Props (`props/<id>.png`, feet/base at FEET)
Dungeon, all acts: podpera (timber prop frame), vozik (mine cart), sud (barrel) + sud_broken,
truhla + truhla_open (chest), kosti (bone pile), ruda (silver ore vein in a rock), kahan_nastenny
(wall lamp, glow), schody_dolu (ladder down into a hole), schody_nahoru (ladder up), klec (shaft
cage = waypoint), kamen (rubble), lebky (skull pile), urna (urn, breakable) + urna_broken.
Shrines: modla_perun, modla_veles, modla_mokos, modla_svarog, modla_morana, modla_stribog,
modla_triglav, modla_rod (carved wooden idols / boží muka) + modla_used (darkened).
Act-specific: hrnek_dusicka (upturned teacup, glowing), zvon (bell), kotel (witch cauldron),
zrcadlo (big mirror), koren (root mass), houby (mushrooms), kovadlina (anvil), pec (oven),
smolinec (glowing green ore), kbelik (bucket of dead water), dub (old oak), truhla_kostej
(iron-bound chest), navi_svice (candles), kalinov_most (bridge segment, wide), oltar (stone altar
for the final room).
Towns: dum_a, dum_b, dum_c (houses), kovarna (smithy), hostinec (inn), chalupa (herb cottage),
sachta_hora (mine headframe/entrance), sachta_vojtech, sachta_svornost, chram_barbory (St Barbara
cathedral of Kutná Hora, landmark), zvonice (bell tower), socha_permonika (statue), mincovna (mint),
stan (tent), ohniste (campfire), studna (well), strom_a, strom_b, smrk (spruce), plot (fence
segment), vuz (wagon), lucerna (street lantern).

### Items (`items/<icon>.png`, size in cells)
Weapons: krumpac 2×3, sekera 2×3, valaska 1×3, palcat 1×3, cep 2×3, kord 1×3, savle 1×3, obusek 1×2,
nuz 1×2, obourucni_mec 2×3, luk 2×3, kuse 2×3, hul 1×3 (staff with antlers), berla 1×3 (bone scepter).
Off-hand: stit 2×2, paveza 2×3, kniha 2×2.
Head 2×2: beranice, havirska_prilba, kapuce, prilba, velka_prilba.
Body 2×3: kytel, kozich, kozeny_kabatec, krouzkova_kosile, krunyr, platova_zbroj.
Belt 2×1: opasek, siroky_opasek. Lamp 1×2: lojovy_kahan, havirsky_kahan, mosazny_kahan,
karbidka, permonikuv_kahan. Ring 1×1: prsten, prsten_b. Amulet 1×1: lunice, kaptorga.
Consumables 1×1: ziva_voda, ziva_voda_velka, svatojanska_rosa, svatojanska_rosa_velka,
kapradi_kvet, svitek_brana, svitek_zjeveni. Gold: grose_malo, grose_hromadka, grose_hodne.
Quest 1×1 unless noted: srdce_zvonu 1×2, strana_kroniky, zlaty_sin, kostejova_jehla, vejce,
mrtva_voda, hrnek (teacup), zrcadlo_strep.
Gems 1×1 (six Czech stones, grades 1–4, `items_more.py`): achat_1, achat_2, achat_3, achat_4, ametyst_1, ametyst_2, ametyst_3, ametyst_4, granat_1, granat_2, granat_3, granat_4, jaspis_1, jaspis_2, jaspis_3, jaspis_4, kristal_1, kristal_2, kristal_3, kristal_4, vltavin_1, vltavin_2, vltavin_3, vltavin_4.
Letters 1×1 (Glagolitic, `items_more.py`): glag_a, glag_b, glag_c, glag_ch, glag_d, glag_e, glag_g, glag_i, glag_ja, glag_k, glag_l, glag_m, glag_n, glag_o, glag_p, glag_r, glag_s, glag_t, glag_u, glag_v, glag_z.
Charm (thunderstones, work from the bag, `items_more.py`): hromovy_kamen_maly 1×1, hromovy_kamen 1×2, hromovy_kamen_velky 1×3.
Key 1×1 (endgame, `items_more.py`): klic_vody, klic_kamene, klic_ohne, klic_smrti, pecet_vody, pecet_kamene, pecet_ohne, pecet_smrti; unique icon permonikuv_desatek 1×3.
Class (one class only, drawn in `items_more.py`): faracka 2×2 (havir), zbojnicky_opasek 2×1 (zbojnice), zarikadla 2×2 (vedma), zastera 2×3 (kovar), obetni_nuz 1×2 (zrec), vlci_kape 2×2 (vlkodlak), krivule 2×2 (alchymistka), vahadlo 2×2 (loutkarka).

### Skills (`ui/skills/<id>.png`)
havir: uder_do_zily, rozrazka, otres, zurivost_hory, naloz, doutnak, odstrel, retez_nalozi,
zdar_buh, tvrda_kuze, vecny_kahan, druhy_dech.
zbojnice: sek_valaskou, hod_valaskou, zbojnicky_skok, vir, rychla_strela, prustrel, ohnivy_sip,
dest_sipu, uskok, past_na_vlky, janosikuv_opasek, kourova_clona.
vedma: jiskra, hromova_koule, retezovy_blesk, peruniv_hnev, ohnivy_jazyk, ohniva_stena,
kupalska_vatra, zar_ptak, mrazivy_dech, ledova_zbroj, moranina_naruc, vynaseni_morany.
kovar: uder_kladivem, rozkovat, hod_kladivem, kovadlina, rozpalene_zelezo, jiskry, vyhen, struska, kovana_kuze, zelezny_strazce, kalena_ocel, kovarova_vydrz.
zrec: svantovituv_zrak, triglavova_zastita, hnev_modly, perunova_prizen, krvava_obet, obetni_ohen, krev_za_krev, velka_obet, dedek, hlas_predku, babky, rod.
vlkodlak: vlci_kuze, kousnuti, vyti, besneni, vlk, smecka, vudce_smecky, vlkodlaci_bratr, trni, koreny, lesni_duch, hnev_lesa.
alchymistka: lucavka, jedovaty_dym, kyselina, kralovska_lucavka, hlineny_golem, rtutovy_golem, sem, prazsky_golem, zlata_strela, rtut, kamen_mudrcu, velke_dilo.
loutkarka: kasparek, cert_na_niti, loutkove_divadlo, obri_marioneta, chodska_pisen, ukolebavka, dupak, hromove_dudy, klubko, mlha, falesna_loutka, hrom_z_kulis.
Plus utok (basic attack), brana (town portal), zjeveni (identify).

### UI (`ui/`)
orb_frame 192×192 (iron ring frame, transparent centre), orb_hp 160×160 (red liquid disc),
orb_mana 160×160 (blue liquid disc), hud_bar 1920×160 (bottom bar, iron and wood, gaps for orbs at
both ends and 4 belt slots + 5 skill slots in the middle), panel 512×512 (9-slice frame, 48 px
border, dark leather/wood), slot 56×56 (inventory cell), slot_hover, button 256×64, button_hover,
button_down, cursor 48×48 (gauntlet/pick pointer, hotspot top-left), cursor_attack 48×48,
title 1200×360 (PERMONÍK hand lettering + "Desátek z hlubin"), menu_bg 1920×1080,
class_havir/class_zbojnice/class_vedma 480×720 (full figure, dramatic, for class select),
xp_bar 1200×20, boss_bar 900×48, map_marker 24×24.

### Slides (`slides/`, 1920×1080)
intro_1 (Hora at dusk, silent bell tower), intro_2 (the miners going down Osel, lamps), intro_3
(Permoník at the shaft head, offering the lamp), act1_end (freed souls rising from teacups),
act2_end (Fabián in the fog, the deep road west), act3_end (the earth closing behind the hero,
Kosmas with the book), act4_intro (the river Smorodina, the dead miners' camp), final_1 (Permoník
taking the lamp), final_2 (the lamp shattering), epilogue (the bell rings over Hora, fifty lamps),
dlc_tease (darkness below Nav, a huge closed eye).
