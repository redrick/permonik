# Touch controls (Android)

`game/scripts/ui/touch_pad.gd` is on whenever the build runs on a mobile OS, or on desktop with `-- --touch`.
In that mode a left mouse button press counts as a finger, so the scheme can be tried with a mouse.
Godot's own mouse-from-touch emulation is off. The pad sorts every finger by where it lands, and only the finger acting as the mouse is turned into mouse events, so all desktop code paths keep working unchanged.

## In the world

| Where the finger lands | What it does |
|---|---|
| Left 45 % of the screen | Floating stick: drag to walk in that direction. A quick tap is a normal click (walk, attack, talk, pick up). Holding still for 0.28 s turns into holding the left button. |
| Anywhere else | Diablo click: tap to walk, attack, talk or pick up. Hold and drag to keep walking or keep attacking. |
| Big button, bottom right | Attack. Hold it to fight the nearest monster in sight, favouring the direction you last moved. With no monster near, it uses the nearest NPC, item or prop and its label changes to Mluvit/Vzít/Použít (Talk/Take/Use). |
| Five buttons on the arc | The RMB/Q/W/E/R skills. Tap casts at the auto-target, or 220 px ahead when there is none. Hold to keep casting; buffs and summons are not repeated. Drag out of the button to aim, and release back on the button to cancel. An empty slot opens the skill picker. |
| Two small buttons next to them | Health potion and mana potion. Each drinks the first matching potion in the belt, falling back to rejuvenation. |
| Top left | ≡ pause (also the Android back button), eye = item labels on/off (Alt), scroll = town portal (only when you carry one and are outside town). |
| Minimap | Opens and closes the map. |
| Belt slot in the HUD | Drinks the potion while the inventory is closed. |
| Skill slot in the HUD | Opens the skill picker. |

## In panels and menus

- Tap is a left click. Double tap is a double click: it learns a skill, or plays the selected hero.
- Hold still for 0.55 s, while a gold ring fills, for a right click (equip, use, sell, move to the stash).
- Slide your finger to move the "mouse" without clicking. This shows tooltips, so you can read an item before picking it up. Sliding also scrolls lists, and dragging a slider moves it.

## Interface size

Settings → Rozhraní/Interface offers Auto, 100, 115, 130 and 150 %. Auto is 130 % on a screen under 8" diagonal and 100 % otherwise, and `-- --ui-scale X` overrides the setting.
The setting scales the HUD, the panels, the menus and the touch pad as whole layers. Anything drawn at a fixed design size shrinks back to fit when the scaled screen is too small for it: the 1920 px bar shrinks to the screen width, and panels shrink to the height above the bar.
On touch builds the quest tracker sits top left, so it stays clear of the skill arc.

## Shared device

`tools/android.sh` builds the APK and drives the device. It only ever touches `cz.antas.permonik` and takes the lock `$XDG_RUNTIME_DIR/adb-device-<serial>.lock` for every device step. It only sends input or takes screenshots while Permoník is the resumed activity and the screen is on.

The Godot editor setting `export/android/shutdown_adb_on_exit` must be `false` on a machine that builds several apps for the same device. When it is `true`, every Godot exit kills the shared adb server.
