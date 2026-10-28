class_name QuestTracker
extends PanelContainer

# Under the minimap: the act and its seals, then the main quest's next step and where it is, then the
# side quests in hand. Rebuilt only when what it would say changes. It fades while the hero is busy,
# and under the mouse it gets a dark backing so the checkboxes (follow on map) and the fold are usable.

const W := 400.0

var font: Font
var box: VBoxContainer
var bg := StyleBoxFlat.new()
var buttons: Array = []
var busy_t := 0.0
var _sig := ""


func _ready() -> void:
	font = load("res://assets/fonts/TataHand.ttf")
	theme = UiTheme.get_theme()
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	bg.bg_color = Color(0.03, 0.02, 0.02, 0.0)
	bg.set_corner_radius_all(8)
	bg.set_content_margin_all(10)
	add_theme_stylebox_override("panel", bg)
	box = VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_theme_constant_override("separation", 2)
	box.custom_minimum_size = Vector2(W, 0)
	add_child(box)
	var t := Timer.new()
	t.wait_time = 0.5
	t.autostart = true
	t.timeout.connect(refresh)
	add_child(t)
	refresh()


func _process(delta: float) -> void:
	var hov := visible and get_global_rect().grow(6).has_point(get_global_mouse_position())
	var p := Game.player
	if p and is_instance_valid(p) and not p.dead and (p.moving or p.action_t > 0.0):
		busy_t = 1.5
	else:
		busy_t -= delta
	var want := 1.0 if hov or busy_t <= 0.0 else 0.4
	modulate.a = move_toward(modulate.a, want, delta * (5.0 if want > modulate.a else 1.6))
	bg.bg_color.a = move_toward(bg.bg_color.a, 0.6 if hov else 0.0, delta * 4.0)


# Only the checkboxes and the fold catch clicks; the rest lets clicks through to the world.
func over_controls(mp: Vector2) -> bool:
	if not visible:
		return false
	for b in buttons:
		if is_instance_valid(b) and b.get_global_rect().grow(4).has_point(mp):
			return true
	return false


func compact() -> bool:
	return Game.flags.get("ui_tracker_compact", false)


# Phones: folded to the next step on one line until opened.
func folded_phone() -> bool:
	return _phone() and not Game.flags.has("ui_tracker_open")


func _phone() -> bool:
	return Game.main != null and Game.main.hud != null and Game.main.hud.phone()


func refresh() -> void:
	var tq := Game.tracked_quests()
	var sig := str(tq) + str(tq.map(func(q): return Game.quest_on_map(q.qid))) + str(compact()) \
		+ str(Game.flags.size()) + str(Game.act) + str(Game.seal_count()) + L.lang + str(folded_phone())
	if sig == _sig:
		return
	_sig = sig
	for c in box.get_children():
		box.remove_child(c)
		c.queue_free()
	buttons.clear()
	reset_size.call_deferred()
	var short := compact()
	var ad := DB.act(Game.act)
	box.custom_minimum_size.x = 0.0 if folded_phone() else W
	if folded_phone():
		_one_line(tq, ad)
		return
	var head := _row()
	head.add_child(_line("%s %s · %s" % [L.t("act"), UiQuests._roman(Game.act), L.t(ad.get("name", ""))], 26, UiTheme.GOLD))
	var fold := UiTheme.small_button("▸" if short else "▾", _toggle_phone if _phone() else _toggle_compact, 44 if _phone() else 30)
	fold.tooltip_text = L.t({"cs": "Zobrazit popisy", "en": "Show descriptions"}) if short else L.t({"cs": "Skrýt popisy", "en": "Hide descriptions"})
	head.add_child(fold)
	buttons.append(fold)
	_line(L.t({"cs": "Pečeti zlomeny: %d / 4", "en": "Seals broken: %d / 4"}) % Game.seal_count(), 18, Color("bcd4ea"), false, box)
	if tq.filter(func(q): return q.main).is_empty():
		for nid in ad.get("town", {}).get("npcs", []):
			if Game.npc_marker(str(nid)) == "new":
				_line(" ", 8, Color.TRANSPARENT, false, box)
				var who := L.t(DB.npcs.get(nid, {}).get("name", nid))
				_line("◆ " + L.t({"cs": "Promluv si: %s", "en": "Talk to %s"}) % who, 24, Color("f0d8a8"), true, box)
				if not short:
					_line("⌖ " + L.t(ad.get("town", {}).get("name", "")), 16, UiTheme.FAINT, true, box)
				break
	var sides := 0
	for q in tq:
		if not q.main and sides >= 3:
			continue
		if not short:
			_line(" ", 8, Color.TRANSPARENT, false, box)
		var on := Game.quest_on_map(q.qid)
		var qid: String = q.qid
		var folded: bool = short or Game.flags.has("fold:" + qid)
		var row := _row()
		var name_col := (Color("f0d8a8") if q.main else Color("d6d8dc")) if on else UiTheme.FAINT
		var nl := _line(("◆ " if q.main else "◇ ") + q.name, 24 if q.main else 21, name_col, true)
		nl.custom_minimum_size = Vector2(W - 76, 0)
		row.add_child(nl)
		if not short:
			var fb := UiTheme.small_button("▸" if folded else "▾", func(): _toggle_fold(qid), 28)
			fb.tooltip_text = L.t({"cs": "Zobrazit popis", "en": "Show description"}) if folded else L.t({"cs": "Skrýt popis", "en": "Hide description"})
			fb.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			row.add_child(fb)
			buttons.append(fb)
		var cb := CheckBox.new()
		cb.button_pressed = on
		cb.focus_mode = Control.FOCUS_NONE
		cb.tooltip_text = L.t({"cs": "Sledovat na mapě", "en": "Follow on the map"})
		cb.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		cb.toggled.connect(func(v: bool):
			Sfx.play("ui_click", 0.4, 0.0)
			Game.set_quest_on_map(qid, v)
			refresh())
		row.add_child(cb)
		buttons.append(cb)
		if not folded:
			var text: String = q.text
			if q.n >= 0:
				text += "  (%d / %d)" % [q.n, q.count]
			_line(text, 19 if q.main else 17, UiTheme.INK if q.main else UiTheme.DIM, true, box)
			if q.where != "":
				_line("⌖ " + q.where, 16, UiTheme.FAINT, true, box)
		if not q.main:
			sides += 1


func _toggle_fold(qid: String) -> void:
	if Game.flags.has("fold:" + qid):
		Game.flags.erase("fold:" + qid)
	else:
		Game.flags["fold:" + qid] = true
	refresh()


func _one_line(tq: Array, ad: Dictionary) -> void:
	var txt := "%s %s · %s" % [L.t("act"), UiQuests._roman(Game.act), L.t(ad.get("name", ""))]
	var mains := tq.filter(func(q): return q.main)
	if not mains.is_empty():
		txt = "◆ " + str(mains[0].name)
	else:
		for nid in ad.get("town", {}).get("npcs", []):
			if Game.npc_marker(str(nid)) == "new":
				txt = "◆ " + L.t({"cs": "Promluv si: %s", "en": "Talk to %s"}) % L.t(DB.npcs.get(nid, {}).get("name", nid))
				break
	var row := _row()
	var b := UiTheme.small_button("▸", _toggle_phone, 44)
	row.add_child(b)
	buttons.append(b)
	var l := _line(txt, 21, Color("f0d8a8"))
	l.clip_text = true
	l.custom_minimum_size = Vector2(minf(330.0, font.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 21).x + 12.0), 0)
	l.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(l)


func _toggle_phone() -> void:
	if Game.flags.has("ui_tracker_open"):
		Game.flags.erase("ui_tracker_open")
	else:
		Game.flags["ui_tracker_open"] = true
	refresh()


func _toggle_compact() -> void:
	if compact():
		Game.flags.erase("ui_tracker_compact")
	else:
		Game.flags["ui_tracker_compact"] = true
	refresh()


func _row() -> HBoxContainer:
	var r := HBoxContainer.new()
	r.alignment = BoxContainer.ALIGNMENT_BEGIN if TouchPad.wanted() else BoxContainer.ALIGNMENT_END
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	r.add_theme_constant_override("separation", 6)
	box.add_child(r)
	return r


func _line(text: String, sz: int, col: Color, wrap := false, parent: Control = null) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", sz)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.95))
	l.add_theme_constant_override("outline_size", 5)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT if TouchPad.wanted() else HORIZONTAL_ALIGNMENT_RIGHT
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(W, 0)
	if parent:
		parent.add_child(l)
	return l
