class_name UiDialog
extends UiPanel

var npc: Npc
var npc_id := ""
var lines: Array = []
var actions: Array = []
var idx := -1
var portrait: TextureRect
var who_lbl: Label
var text_lbl: Label
var buttons: HBoxContainer
var in_lines := false


func _ready() -> void:
	npc_id = npc.npc_id if npc else ""
	custom_minimum_size = Vector2(1180, 0)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 24)
	body.add_child(hb)
	var frame := PanelContainer.new()
	frame.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.02, 0.02, 0.02, 1), UiTheme.BRONZE, 3, 0))
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.add_child(frame)
	portrait = TextureRect.new()
	portrait.custom_minimum_size = Vector2(256, 256)
	portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
	frame.add_child(portrait)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vb.add_theme_constant_override("separation", 8)
	hb.add_child(vb)
	who_lbl = UiTheme.label("", 34, UiTheme.GOLD)
	vb.add_child(who_lbl)
	vb.add_child(UiTheme.rule(780))
	text_lbl = UiTheme.wrap_label("", 27, UiTheme.INK, 780, false)
	text_lbl.size_flags_vertical = Control.SIZE_EXPAND_FILL
	text_lbl.custom_minimum_size.y = 150
	vb.add_child(text_lbl)
	buttons = HBoxContainer.new()
	buttons.add_theme_constant_override("separation", 10)
	buttons.alignment = BoxContainer.ALIGNMENT_END
	vb.add_child(buttons)
	var entry := _pick_entry()
	lines = entry.get("lines", [])
	actions = entry.get("do", [])
	if lines.is_empty():
		_finish_lines()
	else:
		in_lines = true
		_next()


func _pick_entry() -> Dictionary:
	return Game.dialog_entry(npc_id)


func _speaker(who: String) -> void:
	var nm := ""
	var tex: Texture2D = null
	if who == "hero":
		nm = Game.ch.hero_name
		tex = DB.tex("portraits/hero_" + Game.ch.class_id)
	else:
		var key := who if DB.npcs.has(who) else npc_id
		var d: Dictionary = DB.npcs.get(key, {})
		nm = L.t(d.get("name", key))
		tex = DB.tex("portraits/" + str(d.get("portrait", key)))
	who_lbl.text = nm
	who_lbl.add_theme_color_override("font_color", UiTheme.GOLD if who != "hero" else Color("c8d8f0"))
	portrait.texture = tex if tex else DB.placeholder("portrait_" + who, Vector2i(128, 128), Color("6a5a48"))


func _say(text: String) -> void:
	text_lbl.text = text.replace("{name}", Game.ch.hero_name)
	text_lbl.visible_ratio = 0.0
	var tw := create_tween()
	tw.tween_property(text_lbl, "visible_ratio", 1.0, clampf(text.length() / 90.0, 0.25, 1.6))


func _next() -> void:
	if text_lbl.visible_ratio < 1.0 and idx >= 0:
		text_lbl.visible_ratio = 1.0
		return
	idx += 1
	if idx >= lines.size():
		in_lines = false
		_finish_lines()
		return
	var ln: Dictionary = lines[idx]
	var who := str(ln.get("who", npc_id))
	_speaker(who)
	_say(L.t(_line_text(ln, who)))
	_clear_buttons()
	buttons.add_child(UiTheme.button(UiTheme.t("next"), _next, 200))


# The hero's own variant if the line has one. A newer heroine without one borrows the feminine form the
# two older heroines share (an NPC calling her "poutnice"), never their personal lines.
func _line_text(ln: Dictionary, who: String):
	var own := "text_" + Game.ch.class_id
	if ln.has(own):
		return ln[own]
	if who != "hero" and str(DB.classes.get(Game.ch.class_id, {}).get("gender", "m")) == "f":
		if ln.has("text_vedma") and ln.has("text_zbojnice") and str(ln.text_vedma) == str(ln.text_zbojnice):
			return ln.text_vedma
	return ln.get("text", "")


func _clear_buttons() -> void:
	for c in buttons.get_children():
		buttons.remove_child(c)
		c.queue_free()


func _finish_lines() -> void:
	var leaving := false
	for a in actions:
		var s := str(a)
		if s == "next_act" or s.begins_with("slide:"):
			leaving = true
	if leaving:
		UiRoot.inst.close_all()
	for a in actions:
		Game.action(str(a))
	actions = []
	if leaving or not is_inside_tree():
		return
	_speaker(npc_id)
	if lines.is_empty():
		_say(_greeting())
	_menu()


func _greeting() -> String:
	var g: Array = DB.dialog.get("_gossip", {}).get(npc_id, [])
	if npc and npc.role() == "inn" and not g.is_empty():
		return L.t(g.pick_random())
	return "…"


func _menu() -> void:
	_clear_buttons()
	var role := npc.role() if npc else "other"
	var ui := UiRoot.inst
	match role:
		"smith":
			buttons.add_child(UiTheme.button(L.t("trade"), func(): ui.open_vendor(npc), 220))
			buttons.add_child(UiTheme.button(L.t({"cs": "Výheň", "en": "Forge"}), func(): ui.open_forge(), 220))
		"healer":
			buttons.add_child(UiTheme.button(L.t("heal_me"), _heal, 220))
			buttons.add_child(UiTheme.button(L.t("trade"), func(): ui.open_vendor(npc), 220))
		"inn":
			buttons.add_child(UiTheme.button(L.t("trade"), func(): ui.open_vendor(npc), 220))
			buttons.add_child(UiTheme.button(L.t({"cs": "Kostky", "en": "Dice"}), func(): ui.open_vendor(npc, true), 220))
			buttons.add_child(UiTheme.button(L.t("gossip"), _gossip, 220))
		"chronicler":
			buttons.add_child(UiTheme.button(L.t("identify"), _identify_all, 240))
			buttons.add_child(UiTheme.button(UiTheme.t("kronika"), func(): ui.open_kronika(), 220))
	if npc_id == "prevoznik":
		_ferry_buttons(ui)
	buttons.add_child(UiTheme.button(L.t("leave"), func(): ui.close_panel(self), 200))


# The ferryman rows you over the Smorodina to a guardian's tithe, one key a crossing.
func _ferry_buttons(ui: UiRoot) -> void:
	for f in DB.act(4).get("floors", []):
		var ub: Dictionary = f.get("uber", {})
		var key := str(ub.get("key", ""))
		if key == "" or Game.ch.inv.count(key) <= 0:
			continue
		var fn := int(f.n)
		var label := "%s → %s" % [L.t(DB.item(key).get("name", key)), L.t(f.get("name", ""))]
		buttons.add_child(UiTheme.button(label, func():
			Game.ch.inv.take(key, 1)
			ui.close_panel(self)
			Game.goto(4, fn, "start"), 360))


func _heal() -> void:
	Game.action("heal")
	if Game.player:
		Game.player.hp = Game.ch.hp
		Game.player.status.clear()
	_say(UiTheme.t("healed"))


func _gossip() -> void:
	var g: Array = DB.dialog.get("_gossip", {}).get(npc_id, [])
	if g.is_empty():
		_say("…")
		return
	_say(L.t(g.pick_random()))


func _identify_all() -> void:
	var n := 0
	for it: Item in Game.ch.inv.items:
		if it.rarity != Item.NORMAL and not it.identified:
			it.identified = true
			n += 1
	for sl in Game.ch.equip:
		var it: Item = Game.ch.equip[sl]
		if it and it.rarity != Item.NORMAL and not it.identified:
			it.identified = true
			n += 1
	if n > 0:
		Sfx.play("buff", 0.6)
		UiRoot.inst.changed()
		_say(UiTheme.t("identified_all", {"v": n}))
	else:
		_say(UiTheme.t("nothing_to_identify"))


func _gui_input(event: InputEvent) -> void:
	if in_lines and event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		accept_event()
		_next()


func _unhandled_key_input(event: InputEvent) -> void:
	if in_lines and event.pressed and not event.echo and (event as InputEventKey).keycode in [KEY_SPACE, KEY_ENTER, KEY_KP_ENTER]:
		get_viewport().set_input_as_handled()
		_next()
