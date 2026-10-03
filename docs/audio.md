# Audio

All audio is synthesised (no recordings) by `tools/audio_synth.py` with numpy, then encoded to Ogg Vorbis
(`libvorbis -q:a 5`). Re-running is deterministic (seeded per file name).

```
.venv/bin/python tools/audio_synth.py                 # render everything + verify
.venv/bin/python tools/audio_synth.py --only gold,boss  # render a subset + verify all
.venv/bin/python tools/audio_synth.py --verify-only    # just the level / seam / ffprobe table
```

Code: `tools/audio_dsp.py` (filters, Karplus-Strong cimbál, bells, formant voices, choir, reverb),
`tools/audio_sfx.py` (one `sfx_<id>` function per effect), `tools/audio_music.py` (one `t_<id>` per track).

- **SFX**: `game/assets/audio/sfx/<id>.ogg`, mono 44.1 kHz, peak normalised to -3 dBFS, short tails.
- **Music**: `game/assets/audio/music/<id>.ogg`, stereo 44.1 kHz, ~-14 to -17 LUFS (ungated estimate),
  peak below -1.5 dBFS. Loops are rendered circularly (event tails and reverb wrap into the head), so
  the last sample flows into the first; enable **Loop** on import for every track except the two
  `*_sting` files. Each loop is rotated by 60 ms so the seam sits in a quiet tail and the first downbeat
  lands at 0.06 s.

## SFX (59)

| id | what it is |
|---|---|
| swing | Light weapon whoosh (swept band-pass noise). |
| swing_heavy | Slower, lower whoosh with a sub swell, for two-handers/mauls. |
| hit_flesh | Body thump plus wet squelch. |
| hit_bone | Dry crack and woody knock, skeletons. |
| hit_metal | Armour clang, inharmonic bar partials. |
| hit_stone | Thud with gravel crackle, golems / stone foes. |
| block | Bright shield clang with thump. |
| player_hurt | Short pained grunt ("ah-uh", formant voice). |
| player_death | Long falling groan, body fall and dropped gear. |
| monster_death | Growling low death moan. |
| death_bone | Skeleton collapsing: crack and clattering bones. |
| death_beast | Animal yelp falling into a whine. |
| death_ghost | Descending eerie "oo" with breath, long reverb. |
| boss_roar | Huge layered roar with sub rumble. |
| boss_death | Roar collapsing into rumble, crumbling stone and a final thud. |
| fire_cast | Rising flame whoosh with crackle. |
| fire_hit | Fire burst: thump, flare, crackle. |
| lightning_cast | Buzzing electric crackle. |
| lightning_hit | Sharp crack and rolling thunder. |
| frost_cast | Glassy high chimes over airy hiss. |
| frost_hit | Ice shatter. |
| explosion | Black-powder blast: boom, roar, falling debris. |
| arrow_shot | Bowstring twang and arrow whoosh. |
| bolt_shot | Crossbow release: click, thunk, heavy string. |
| axe_throw | Spinning valaška whoosh (pulsing). |
| potion | Cork tick and gulping bubbles. |
| gold | Handful of coins jingling. |
| pickup | Soft grab: rustle, thump, tick. |
| drop_item | Item hitting a stone floor. |
| equip | Buckle clinks and leather creak. |
| levelup | Rising D-major cimbál arpeggio with bells. |
| quest_done | Cimbál A7 to D cadence with a bell. |
| chest_open | Latch click, creaking lid, lid thump. |
| barrel_break | Wood crack and tumbling staves. |
| urn_break | Ceramic smash with shards. |
| shrine | Choir swell (D-minor add9) with a high bell. |
| portal | Swirling filtered noise with phasing drones. |
| waypoint | Two bell chimes and a soft whoosh. |
| bell_toll | Single big church bell (G3), long decay. The Kutná Hora evening bell. |
| ui_click | Tiny wooden tick. |
| ui_open | Upward swish and tick (panel opens). |
| ui_close | Tick and downward swish (panel closes). |
| no_mana | Dull two-note "denied" buzz. |
| step_stone_1 | Footstep on stone, variant 1. |
| step_stone_2 | Footstep on stone, variant 2 (lower). |
| step_stone_3 | Footstep on stone, variant 3 (brighter). |
| water_splash | Larger splash with bubbles and drips. |
| coin_bounce | A single coin bouncing and spinning out. |
| laugh_permonik | Permoník's small creepy "hi-hi-hi" giggle (formant-filtered pulses, small-throat formants). |
| ghost_wail | Rising and falling ghost wail, long reverb. |
| wolf_howl | Wolf howl (formant voice "oo-oh"). |
| cauldron_bubble | Thick bubbling over a low simmer. |
| chains | Rattling chain links in three shakes. |
| petrify | Grinding stone, crackle building to a crunch. |
| heal | Soft rising D-major shimmer. |
| buff | Rising filtered saw sweep with fifths. |
| trap_snap | Spring-trap snap: click, clang, boing. |
| smoke | Smoke puff with hiss. |
| footstep_water | Footstep in shallow water. |

## Music (13)

| id | length | what it is |
|---|---|---|
| menu | 80 s loop | D minor. Dark dudy drones, faint "u/o" choir, three tolls of the evening bell then silence, slow cimbál main theme (D F E D C Bb A G A D). |
| town_hora | 85.7 s loop | Kutná Hora, the Tristram-like town theme. 3/4 at 84 bpm, cimbál arpeggios in D minor with harmonic-minor V (A major), bass strings, tremolo cimbál melody, low string drone, distant bell. |
| town_pribram | 80 s loop | Příbram. A dorian, 72 bpm, dudy drones, rolled cimbál chords, fiddle (housle) melody, distant mine hammers. |
| town_jachymov | 96 s loop | Jáchymov. E phrygian dominant, 3/4 at 60 bpm, low bowed drone, tremolo cimbál melody, distant anvils, wind. Uneasy. |
| town_nav | 96 s loop | The Nav (underworld) settlement. B minor with Neapolitan C, slow vowel-shifting choir, slow bells, high dulcimer harmonics, a quiet river. |
| mine_1 | 96 s loop | Silver mine (Act I). Drips, distant pick strikes, low D drone, sparse pentatonic dulcimer, occasional rumble. |
| mine_2 | 96 s loop | Brdy forest roots (Act II). Wind through roots, wooden knocks, creaking, G dudy drone with rare chanter notes. |
| mine_3 | 80 s loop | Jáchymov hell (Act III). 75 bpm double-thump sub pulse, reverberant anvils, steam hiss, Geiger-like clicks, E/F/Bb cluster drone, bowed-metal whine. |
| mine_4 | 112 s loop | Nav (Act IV). Slow choir vowel pads over A minor with Bb, slow bells, river. |
| boss | 75 s loop | 128 bpm D phrygian. Kick, frame drum, taiko and tom fills, low brass-like saw ostinato, brass chords, cimbál solo section, choir breakdown. |
| final_boss | 94.3 s loop | 112 bpm. Big bells on downbeats, choir chords (Dm, Eb, Dm, C#dim, Bb, A), taiko and drums, low brass, heartbeat breakdown, cimbál over the last section. |
| victory_sting | 8 s one-shot | Rising D-major cimbál run, tremolo high D, choir, bells. |
| death_sting | 6 s one-shot | Low bell toll, falling phrygian cimbál line, low "o/u" choir. |
