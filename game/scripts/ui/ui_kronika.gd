class_name UiKronika
extends UiPanel

var list: VBoxContainer
var title_lbl: Label
var text_lbl: Label
var text_scroll: ScrollContainer


func _ready() -> void:
	custom_minimum_size = Vector2(900, 0)
	set_title(UiTheme.t("kronika"))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 18)
	body.add_child(hb)
	var ls := ScrollContainer.new()
	ls.custom_minimum_size = Vector2(300, 700)
	ls.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	hb.add_child(ls)
	list = VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_theme_constant_override("separation", 0)
	ls.add_child(list)
	var page := PanelContainer.new()
	page.add_theme_stylebox_override("panel", UiTheme.flat(Color("2a2118"), Color("4a3a28"), 2, 22))
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(page)
	var pv := VBoxContainer.new()
	page.add_child(pv)
	title_lbl = UiTheme.label("", 32, UiTheme.GOLD)
	title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title_lbl.custom_minimum_size = Vector2(480, 0)
	pv.add_child(title_lbl)
	pv.add_child(UiTheme.rule(480))
	text_scroll = ScrollContainer.new()
	text_scroll.custom_minimum_size = Vector2(500, 600)
	text_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	pv.add_child(text_scroll)
	text_lbl = UiTheme.wrap_label("", 23, Color("e6d9bc"), 480)
	text_scroll.add_child(text_lbl)
	_fill()


func _unlocked() -> Array:
	var out := []
	var seals := Game.seal_count()
	var kron := []
	var boss := []
	var best := []
	for id in DB.lore:
		var e: Dictionary = DB.lore[id]
		match str(e.get("kind", "")):
			"kronika":
				var n := int(str(id).get_slice("_", 1))
				if n <= seals or Game.cond(str(e.get("unlock", "!always"))):
					kron.append(id)
			"boss":
				if Game.flags.get("killed_" + str(e.get("monster", "")), false):
					boss.append(id)
			"bestiar":
				var mid := str(e.get("monster", ""))
				var m := DB.monster(mid)
				var ok := false
				if bool(m.get("boss", false)):
					ok = Game.flags.get("killed_" + mid, false)
				else:
					ok = int(m.get("act", 99)) <= Game.act
				if ok:
					best.append(id)
	if not kron.is_empty():
		out.append(UiTheme.t("kronika"))
		out.append_array(kron)
	if not boss.is_empty():
		out.append("—")
		out.append_array(boss)
	if not best.is_empty():
		out.append(UiTheme.t("bestiary"))
		out.append_array(best)
	return out


func _fill() -> void:
	var first := ""
	for id in _unlocked():
		if not DB.lore.has(id):
			if id != "—":
				list.add_child(UiTheme.sep(8))
				list.add_child(UiTheme.label(id, 26, UiTheme.GOLD))
			else:
				list.add_child(UiTheme.sep(6))
			continue
		var e: Dictionary = DB.lore[id]
		var b := Button.new()
		b.text = L.t(e.get("title", id))
		b.flat = true
		b.focus_mode = Control.FOCUS_NONE
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_override("font", UiTheme.small)
		b.add_theme_font_size_override("font_size", 20)
		b.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		b.custom_minimum_size = Vector2(280, 30)
		var lid: String = id
		b.pressed.connect(func(): _show(lid))
		list.add_child(b)
		if first == "":
			first = id
	if first == "":
		title_lbl.text = UiTheme.t("kronika")
		text_lbl.text = UiTheme.t("kronika_empty")
	else:
		_show(first)


func _show(id: String) -> void:
	var e: Dictionary = DB.lore.get(id, {})
	title_lbl.text = L.t(e.get("title", id))
	text_lbl.text = L.t(e.get("text", ""))
	text_scroll.scroll_vertical = 0
	Sfx.play("ui_click", 0.4, 0.0)
