class_name UiTheme
extends RefCounted

const INK := Color("e8dcc0")
const GOLD := Color("e9c46a")
const DIM := Color("a89a80")
const FAINT := Color("6f6452")
const RED := Color("e04b4b")
const GREEN := Color("8fcf7a")
const BLUE := Color("7f9bff")
const BRONZE := Color("8a6a3a")
const BAR_H := 160
const CELL := 56

static var font: Font
static var small: Font
static var theme: Theme

const TXT := {
	"menu_saves": {"cs": "Uložené hry", "en": "Saved games"},
	"menu_load": {"cs": "Načíst", "en": "Load"},
	"menu_delete_q": {"cs": "Opravdu smazat {v}?", "en": "Really delete {v}?"},
	"menu_yes": {"cs": "Ano", "en": "Yes"},
	"menu_no": {"cs": "Ne", "en": "No"},
	"menu_pick_class": {"cs": "Kdo sestoupí do hlubin?", "en": "Who will descend into the deep?"},
	"menu_music": {"cs": "Hudba", "en": "Music"},
	"menu_master": {"cs": "Hlasitost", "en": "Volume"},
	"menu_fullscreen": {"cs": "Celá obrazovka", "en": "Fullscreen"},
	"menu_ui_scale": {"cs": "Rozhraní", "en": "Interface"},
	"menu_ui_auto": {"cs": "Auto", "en": "Auto"},
	"menu_ui_default": {"cs": "Výchozí", "en": "Default"},
	"menu_save_dir": {"cs": "Uložené hry", "en": "Saved games"},
	"save_dir_pick": {"cs": "Vybrat složku…", "en": "Choose folder…"},
	"save_dir_default": {"cs": "Výchozí složka hry. Zvol synchronizovanou složku a hrdinové se tam přesunou.", "en": "The game's own folder. Choose a synced folder and the heroes move there."},
	"save_dir_failed": {"cs": "Do {v} nejde zapisovat.", "en": "Can't write to {v}."},
	"save_dir_permission": {"cs": "Povol hře přístup ke všem souborům a zkus to znovu.", "en": "Allow the game access to all files, then try again."},
	"save_newer_elsewhere": {"cs": "Tenhle hrdina byl mezitím uložen jinde. Načti ho znovu.", "en": "This hero was saved elsewhere in the meantime. Load it again."},
	"menu_default_name": {"cs": "Poutník", "en": "Wanderer"},
	"menu_locked_diff": {"cs": "Těžší obtížnosti odemkne dohraná hra.", "en": "Harder difficulties unlock after finishing the game."},
	"menu_subtitle": {"cs": "Desátek z hlubin", "en": "The Tithe of the Deep"},
	"close": {"cs": "Zavřít", "en": "Close"},
	"equipped": {"cs": "Nasazeno", "en": "Equipped"},
	"sell_for": {"cs": "Prodat za {v} grošů (pravé tlačítko)", "en": "Sell for {v} groschen (right click)"},
	"unsellable": {"cs": "Tohle nikdo nekoupí.", "en": "Nobody will buy this."},
	"wont_buy": {"cs": "Tohle ode mě nekoupí.", "en": "Won't buy this from me."},
	"price": {"cs": "Cena: {v} grošů", "en": "Price: {v} groschen"},
	"rc_use": {"cs": "Pravé tlačítko: použít · Shift: do opasku", "en": "Right click: use · Shift: to belt"},
	"rc_equip": {"cs": "Pravé tlačítko: nasadit", "en": "Right click: equip"},
	"repair_cost": {"cs": "Opravit vše ({v} grošů)", "en": "Repair all ({v} groschen)"},
	"nothing_to_repair": {"cs": "Není co opravovat.", "en": "Nothing to repair."},
	"repaired": {"cs": "Kovář vše spravil.", "en": "Everything is mended."},
	"kronika": {"cs": "Kronika", "en": "Chronicle"},
	"bestiary": {"cs": "Bestiář", "en": "Bestiary"},
	"kronika_empty": {"cs": "Stránky jsou zatím prázdné.", "en": "The pages are still blank."},
	"next": {"cs": "Dál", "en": "Next"},
	"two_handed_block": {"cs": "Obouruční zbraň mi nenechá volnou ruku.", "en": "A two-handed weapon leaves no hand free."},
	"wrong_slot": {"cs": "Tohle sem nepatří.", "en": "That doesn't go there."},
	"identify_hint": {"cs": "Klikni na neidentifikovanou věc.", "en": "Click an unidentified item."},
	"stat_points": {"cs": "Volné body: {v}", "en": "Free points: {v}"},
	"skill_points_n": {"cs": "Body dovedností: {v}", "en": "Skill points: {v}"},
	"life": {"cs": "Život", "en": "Life"},
	"attack_speed": {"cs": "Útoků za sekundu", "en": "Attacks per second"},
	"block": {"cs": "Vykrytí", "en": "Block"},
	"light_radius": {"cs": "Dosvit kahanu", "en": "Lamp light"},
	"magic_find": {"cs": "Kouzelné nálezy", "en": "Magic find"},
	"gold_find": {"cs": "Víc grošů", "en": "Gold find"},
	"active": {"cs": "Rozdělané", "en": "Active"},
	"done": {"cs": "Splněno", "en": "Completed"},
	"no_quests": {"cs": "Zatím nikdo nic nechce.", "en": "Nobody wants anything from you yet."},
	"main_quest": {"cs": "hlavní", "en": "main"},
	"reward": {"cs": "Odměna", "en": "Reward"},
	"waypoints": {"cs": "Těžní klec", "en": "Shaft cage"},
	"waypoint_hint": {"cs": "Klec sjede do každého města i patra, kde už jsi byl, i do dřívějších dějství.", "en": "The cage goes to every town and floor you have reached, earlier acts too."},
	"pick_skill": {"cs": "Vyber dovednost", "en": "Choose a skill"},
	"learn": {"cs": "Naučit", "en": "Learn"},
	"not_learned": {"cs": "Nenaučeno", "en": "Not learned"},
	"bound_rmb": {"cs": "Pravá myš", "en": "Right mouse"},
	"pause": {"cs": "Hora čeká", "en": "The mountain waits"},
	"descend_again": {"cs": "Sestoupit znovu: {v}", "en": "Descend again: {v}"},
	"back_to_menu": {"cs": "Do hlavní nabídky", "en": "To main menu"},
	"skip_all": {"cs": "Esc: přeskočit", "en": "Esc: skip"},
	"skip_all_touch": {"cs": "Přeskočit ›", "en": "Skip ›"},
	"menu_story": {"cs": "Příběh", "en": "Story"},
	"story_hint": {"cs": "Filmy, které už znáš. Pusť si je znovu, ať do sebe příběh zapadne.", "en": "The films you have already seen. Watch them again and let the story fall into place."},
	"story_locked": {"cs": "Zatím neviděno", "en": "Not seen yet"},
	"story_all": {"cs": "Přehrát vše", "en": "Play all"},
	"inv_short": {"cs": "Výbava", "en": "Inventory"},
	"sold": {"cs": "Prodáno za {v} grošů.", "en": "Sold for {v} groschen."},
	"vendor_hint": {"cs": "Klikni na zboží: koupit · Shift+klik na lektvar: naplnit opasek · Polož svou věc sem nebo na ni klikni pravým: prodat", "en": "Click wares to buy · Shift-click a potion: fill the belt · Drop your item here or right-click it: sell"},
	"seals": {"cs": "Zlomené pečeti", "en": "Broken seals"},
	"play_time": {"cs": "Čas ve hře", "en": "Time played"},
}


static func t(key: String, args := {}) -> String:
	if args.has("v") and not args.has("n"):
		args = args.duplicate()
		args["n"] = args.v
	if TXT.has(key) and not L.ui.has(key):
		return L.t(TXT[key], args)
	return L.t(key, args)


static func get_theme() -> Theme:
	if theme:
		return theme
	font = load("res://assets/fonts/TataHand.ttf")
	small = load("res://assets/fonts/PatrickHand-Regular.ttf")
	var glag: Font = load("res://assets/fonts/NotoSansGlagolitic-Regular.ttf")
	for f in [font, small]:
		if f and glag and not f.fallbacks.has(glag):
			f.fallbacks = f.fallbacks + [glag]
	var th := Theme.new()
	th.default_font = font
	th.default_font_size = 24
	th.set_stylebox("panel", "PanelContainer", panel_box())
	th.set_stylebox("panel", "Panel", panel_box())
	for st in ["normal", "hover", "pressed", "disabled", "focus"]:
		th.set_stylebox(st, "Button", button_box(st))
	th.set_color("font_color", "Button", INK)
	th.set_color("font_hover_color", "Button", GOLD)
	th.set_color("font_pressed_color", "Button", Color("fff0c8"))
	th.set_color("font_focus_color", "Button", INK)
	th.set_color("font_disabled_color", "Button", FAINT)
	th.set_color("font_outline_color", "Button", Color.BLACK)
	th.set_constant("outline_size", "Button", 4)
	th.set_font_size("font_size", "Button", 26)
	th.set_color("font_color", "Label", INK)
	th.set_color("font_outline_color", "Label", Color.BLACK)
	th.set_constant("outline_size", "Label", 3)
	th.set_color("default_color", "RichTextLabel", INK)
	th.set_font("normal_font", "RichTextLabel", small)
	th.set_font_size("normal_font_size", "RichTextLabel", 22)
	var le := flat(Color(0.05, 0.04, 0.035, 0.95), BRONZE, 2, 10)
	th.set_stylebox("normal", "LineEdit", le)
	th.set_stylebox("focus", "LineEdit", flat(Color(0.07, 0.055, 0.045, 0.95), GOLD, 2, 10))
	th.set_color("font_color", "LineEdit", INK)
	th.set_color("caret_color", "LineEdit", GOLD)
	th.set_font_size("font_size", "LineEdit", 28)
	th.set_stylebox("slider", "HSlider", flat(Color(0.12, 0.09, 0.07), BRONZE, 1, 4))
	th.set_stylebox("grabber_area", "HSlider", flat(Color("8a6a3a"), Color("8a6a3a"), 0, 4))
	th.set_stylebox("grabber_area_highlight", "HSlider", flat(GOLD.darkened(0.2), GOLD, 0, 4))
	th.set_icon("grabber", "HSlider", _knob(GOLD.darkened(0.15)))
	th.set_icon("grabber_highlight", "HSlider", _knob(GOLD))
	for sb in ["VScrollBar", "HScrollBar"]:
		th.set_stylebox("scroll", sb, flat(Color(0.05, 0.04, 0.03, 0.6), Color(0, 0, 0, 0), 0, 4))
		th.set_stylebox("grabber", sb, flat(BRONZE, BRONZE, 0, 4))
		th.set_stylebox("grabber_highlight", sb, flat(GOLD.darkened(0.3), GOLD.darkened(0.3), 0, 4))
		th.set_stylebox("grabber_pressed", sb, flat(GOLD, GOLD, 0, 4))
	th.set_color("font_color", "CheckBox", INK)
	th.set_color("font_hover_color", "CheckBox", GOLD)
	th.set_color("font_pressed_color", "CheckBox", INK)
	for st in ["normal", "hover", "pressed", "hover_pressed", "focus"]:
		th.set_stylebox(st, "CheckBox", StyleBoxEmpty.new())
	th.set_icon("checked", "CheckBox", _check(true))
	th.set_icon("unchecked", "CheckBox", _check(false))
	th.set_constant("h_separation", "CheckBox", 14)
	th.set_stylebox("panel", "TooltipPanel", flat(Color(0.03, 0.025, 0.03, 0.94), BRONZE, 2, 10))
	th.set_font("font", "TooltipLabel", small)
	th.set_font_size("font_size", "TooltipLabel", 20)
	th.set_color("font_color", "TooltipLabel", INK)
	theme = th
	return th


static func _check(on: bool) -> Texture2D:
	var img := Image.create(30, 30, false, Image.FORMAT_RGBA8)
	img.fill(Color(0.06, 0.05, 0.04, 1))
	for i in 30:
		for k in 3:
			img.set_pixel(i, k, BRONZE)
			img.set_pixel(i, 29 - k, BRONZE)
			img.set_pixel(k, i, BRONZE)
			img.set_pixel(29 - k, i, BRONZE)
	if on:
		for y in range(8, 22):
			for x in range(8, 22):
				img.set_pixel(x, y, GOLD)
	return ImageTexture.create_from_image(img)


static func _knob(c: Color) -> Texture2D:
	var img := Image.create(22, 22, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	for y in 22:
		for x in 22:
			var d := Vector2(x - 10.5, y - 10.5).length()
			if d < 10.0:
				img.set_pixel(x, y, c.darkened(0.5) if d > 8.0 else c.lightened(0.1 * (1.0 - y / 22.0)))
	return ImageTexture.create_from_image(img)


static func flat(bg: Color, border: Color, bw := 2, pad := 8) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(bw)
	sb.set_content_margin_all(pad)
	sb.set_corner_radius_all(2)
	return sb


static func panel_box() -> StyleBox:
	var tex := DB.tex("ui/panel")
	if tex:
		var sb := StyleBoxTexture.new()
		sb.texture = tex
		sb.set_texture_margin_all(48)
		sb.set_content_margin_all(42)
		return sb
	var f := flat(Color(0.09, 0.07, 0.06, 0.97), Color("5a4630"), 6, 24)
	f.shadow_color = Color(0, 0, 0, 0.6)
	f.shadow_size = 10
	return f


static func button_box(state: String) -> StyleBox:
	var path: String = {"hover": "ui/button_hover", "pressed": "ui/button_down"}.get(state, "ui/button")
	var tex := DB.tex(path)
	if state == "focus":
		return StyleBoxEmpty.new()
	if tex:
		var sb := StyleBoxTexture.new()
		sb.texture = tex
		sb.texture_margin_left = 30
		sb.texture_margin_right = 30
		sb.texture_margin_top = 18
		sb.texture_margin_bottom = 18
		sb.content_margin_left = 30
		sb.content_margin_right = 30
		sb.content_margin_top = 8
		sb.content_margin_bottom = 12
		if state == "disabled":
			sb.modulate_color = Color(0.55, 0.5, 0.48)
		return sb
	var bg: Color = {"hover": Color("3a2c20"), "pressed": Color("1c140e"), "disabled": Color("1a1612")}.get(state, Color("2a2018"))
	return flat(bg, GOLD if state == "hover" else BRONZE, 2, 10)


static func label(text: String, sz := 24, color := INK, dense := false) -> Label:
	var l := Label.new()
	l.text = text
	if dense:
		l.add_theme_font_override("font", small)
	l.add_theme_font_size_override("font_size", sz)
	l.add_theme_color_override("font_color", color)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


static func skip_label(parent: Control) -> Label:
	var touch := TouchPad.active
	var l := label(t("skip_all_touch") if touch else t("skip_all"), 26 if touch else 18, Color(1, 1, 1, 0.55 if touch else 0.3), true)
	l.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	l.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.custom_minimum_size = Vector2(120 if touch else 0, 64 if touch else 0)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	l.position += Vector2(-20, 4 if touch else 12)
	l.mouse_filter = Control.MOUSE_FILTER_STOP
	l.gui_input.connect(func(e: InputEvent) -> void:
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			l.accept_event()
			UiRoot.inst.skip_slides())
	parent.add_child(l)
	return l


static func wrap_label(text: String, sz := 22, color := INK, width := 400.0, dense := true) -> Label:
	var l := label(text, sz, color, dense)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(width, 0)
	return l


static func button(text: String, cb: Callable, min_w := 260.0, sz := 26) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(min_w, 56)
	b.add_theme_font_size_override("font_size", sz)
	b.pressed.connect(func():
		Sfx.play("ui_click", 0.6, 0.0)
		cb.call())
	return b


static func small_button(text: String, cb: Callable, w := 36.0) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_NONE
	b.custom_minimum_size = Vector2(w, 34)
	b.add_theme_font_size_override("font_size", 24)
	b.add_theme_color_override("font_color", GOLD)
	for st in ["normal", "hover", "pressed", "disabled"]:
		var bg: Color = {"hover": Color("4a3622"), "pressed": Color("1c140e"), "disabled": Color("1a1612")}.get(st, Color("2e2219"))
		var sb := flat(bg, GOLD if st == "hover" else BRONZE, 2, 2)
		b.add_theme_stylebox_override(st, sb)
	b.pressed.connect(func():
		Sfx.play("ui_click", 0.5, 0.0)
		cb.call())
	return b


static func title(text: String, sz := 38) -> Label:
	var l := label(text, sz, GOLD)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.add_theme_constant_override("outline_size", 6)
	return l


static func sep(h := 10.0) -> Control:
	var c := Control.new()
	c.custom_minimum_size = Vector2(0, h)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


static func rule(w := 400.0) -> Control:
	var r := ColorRect.new()
	r.color = Color(BRONZE, 0.55)
	r.custom_minimum_size = Vector2(w, 2)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return r


static func fmt_num(v) -> String:
	if v is Vector2 or v is Vector2i:
		return "%d–%d" % [int(round(v.x)), int(round(v.y))]
	if v is float:
		if absf(v - round(v)) < 0.05:
			return str(int(round(v)))
		return "%.1f" % v
	return str(v)


static func draw_item(ci: CanvasItem, it: Item, r: Rect2, tint_bg := true) -> void:
	if tint_bg:
		var bg := Color(0, 0, 0, 0)
		if it.is_equipment() and not Game.ch.can_equip(it):
			bg = Color(0.55, 0.06, 0.05, 0.3)
		elif it.rarity == Item.UNIQUE or it.word != "":
			bg = Color(0.75, 0.6, 0.2, 0.16)
		elif it.rarity == Item.SET:
			bg = Color(0.2, 0.7, 0.3, 0.16)
		elif it.rarity == Item.RARE:
			bg = Color(0.85, 0.8, 0.25, 0.14)
		elif it.rarity == Item.CRAFTED:
			bg = Color(0.9, 0.55, 0.15, 0.16)
		elif it.rarity == Item.MAGIC:
			bg = Color(0.25, 0.35, 0.9, 0.16)
		if bg.a > 0:
			ci.draw_rect(r.grow(-2), bg)
	var t := it.icon()
	if t:
		var s := minf(r.size.x / t.get_width(), r.size.y / t.get_height())
		var sz := Vector2(t.get_width(), t.get_height()) * s
		ci.draw_texture_rect(t, Rect2(r.position + (r.size - sz) / 2.0, sz), false, Color(0.8, 0.9, 1.0, 0.55) if it.eth else Color.WHITE)
	if it.sockets > 0:
		var d := minf(22.0, (r.size.x - 8) / it.sockets)
		var y := r.end.y - d - 4
		var x0 := r.position.x + (r.size.x - d * it.sockets) / 2.0
		for k in it.sockets:
			var c := Vector2(x0 + d * (k + 0.5), y + d / 2.0)
			ci.draw_circle(c, d * 0.42, Color(0.05, 0.04, 0.04, 0.85))
			ci.draw_arc(c, d * 0.42, 0.0, TAU, 16, Color(0.62, 0.6, 0.55, 0.9), 1.4, true)
			if k < it.socketed.size():
				var gt: Texture2D = it.socketed[k].icon()
				if gt:
					ci.draw_texture_rect(gt, Rect2(c - Vector2(d, d) * 0.42, Vector2(d, d) * 0.84), false)
	if it.is_stackable() and it.qty > 1:
		ci.draw_string_outline(small, r.position + Vector2(4, r.size.y - 5), str(it.qty), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, 4, Color.BLACK)
		ci.draw_string(small, r.position + Vector2(4, r.size.y - 5), str(it.qty), HORIZONTAL_ALIGNMENT_LEFT, -1, 18, INK)
	if it.max_dur > 0 and it.dur < it.max_dur / 4 + 1:
		ci.draw_rect(Rect2(r.position + Vector2(3, 3), Vector2(8, 8)), RED if it.dur <= 0 else Color("e0a040"))


# D3's arrow in the corner: green when wearing it would make the hero stronger, red when weaker.
static func draw_upgrade(ci: CanvasItem, it: Item, r: Rect2) -> void:
	var s := Game.ch.upgrade_score(it)
	if is_nan(s) or absf(s) < 1.5:
		return
	var up := s > 0.0
	var c := r.position + Vector2(r.size.x - 13, 13)
	var pts := PackedVector2Array([c + Vector2(0, -8), c + Vector2(8, 6), c + Vector2(-8, 6)]) if up else PackedVector2Array([c + Vector2(0, 8), c + Vector2(8, -6), c + Vector2(-8, -6)])
	ci.draw_colored_polygon(pts, Color("5fd068") if up else RED)
	ci.draw_polyline(pts + PackedVector2Array([pts[0]]), Color.BLACK, 1.5, true)


static func draw_cell(ci: CanvasItem, r: Rect2, hover := false) -> void:
	var st := DB.tex("ui/slot_hover" if hover else "ui/slot")
	if st:
		ci.draw_texture_rect(st, r, false)
	else:
		ci.draw_rect(r, Color(0.07, 0.06, 0.05, 0.95))
		ci.draw_rect(r, Color(0.3, 0.24, 0.17, 1) if not hover else GOLD.darkened(0.3), false, 1.0)
