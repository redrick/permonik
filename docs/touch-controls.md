# Touch controls (Android)

`game/scripts/ui/touch_pad.gd` is on whenever the build runs on a mobile OS, or on desktop with `-- --touch`.
In that mode a left mouse button press counts as a finger, so the scheme can be tried with a mouse.
Godot's own mouse-from-touch emulation is off. The pad sorts every finger by where it lands, and only the finger acting as the mouse is turned into mouse events, so all desktop code paths keep working unchanged.

## In the world

| Where the finger lands | What it does |
|---|---|
| Left half of the screen | Floating stick wherever the thumb lands: once it moves 12 px the hero walks that way at full speed, even after the thumb has rested. A quick tap (under 0.3 s) is a normal click (walk, attack, talk, pick up). |
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
- **Items never move on a tap.** Tapping an item in the bag, a chest, a shop, the forge, the doll or the belt (while the bag is open) selects it and opens the item card. The card shows the item in large type, what wearing it would change, and on request the piece worn now. It has one button per action: Buy, Sell, Fill the belt, Equip, Take off, Use, To the belt, Into the chest, Lay it here, To the bag, Identify, and Move. Move puts the item on the finger like a mouse cursor, and the next tap on a cell, a slot, a shop or the ground places it (also into a socket). A tap on an empty cell or × closes the card.
- Hold still for 0.55 s, while a gold ring fills, for a right click. On items it only opens the card; elsewhere it works as before.
- Slide your finger to move the "mouse" without clicking. Sliding also scrolls lists, and dragging a slider moves it. Hover tooltips for items are off on touch; the card replaces them.

## Interface size

Settings → Rozhraní/Interface offers Auto, 100, 115, 130 and 150 %. Auto is 160 % on a screen under 7" diagonal (phones), 130 % under 8" and 100 % otherwise. `-- --ui-scale X` overrides the setting.
The setting scales the HUD, the panels, the menus and the touch pad as whole layers. Anything drawn at a fixed design size shrinks back to fit when the scaled screen is too small for it: the 1920 px bar shrinks to the screen width, panels shrink to the height above the bar, and menu pages shrink to the screen.
On touch builds the quest tracker sits top left, so it stays clear of the skill arc.

### Phone layout (logical height under 760 px)

- No HUD bar. Life and mana orbs sit in the bottom corners over a thin xp line across the whole bottom edge; the level-up + is beside the life orb. The quest tracker is top left, folded to the next step on one line (▸ opens it in full). The minimap shrinks to 70 %.
- The camera zooms in by the interface scale (160 %), so the hero is as big against the HUD and the screen as on a monitor.
- Next to the minimap: the bag button (opens the book; a gold dot means unspent points), the menu ≡, the item-names eye and, below ground, the portal scroll. Skills, attack and potions are the touch pad's buttons as on a tablet.
- Every panel opens full screen in one book (`UiPhoneBook`) and the game pauses behind it. Tabs down the left edge: Výbava, Postava, Dovednosti, Úkoly, Kronika, Pomocník (with a hireling), Mapa, then Nabídka (pause menu) and Zavřít. Tapping the open tab closes the book. Pages scale to fill the screen (up to 135 %).
- The bag page has a narrower doll beside the grid and a fixed detail column on the right instead of the floating card. It shows the tapped item, its buttons, and Zahodit (drop on the ground).
- A shop, chest, forge, service or hireling opens the book without tabs: their panel, the bag (without the doll) and the detail column, with × in the corner.
- Dialogue, books, waypoints and the pause menu stay centred windows as on a tablet.
- Action cluster is tighter on a phone: attack r 70, skills r 43 on a 168 px arc, potions r 36 beside it.
- The map sheet shrinks to the screen above the xp line; on touch its × (top-left corner of the sheet) closes it, as does tapping the minimap to open it.
- Menu pages have phone layouts: title beside the buttons on the main page, the hero list with the hero standing beside it and full-size Play/Delete, class cards in a row with the description and name in a column, settings scrolling between the title and Back.
- Choosing a save folder opens the game's own folder browser (also on tablets). Android's picker returns content:// URIs, and Godot's FileDialog is a separate window the touch layer doesn't reach.

## Shared device

`tools/android.sh` builds the APK and drives the device. It only ever touches `cz.antas.permonik` and takes the lock `$XDG_RUNTIME_DIR/adb-device-<serial>.lock` for every device step. It only sends input or takes screenshots while Permoník is the resumed activity and the screen is on.

The Godot editor setting `export/android/shutdown_adb_on_exit` must be `false` on a machine that builds several apps for the same device. When it is `true`, every Godot exit kills the shared adb server.
