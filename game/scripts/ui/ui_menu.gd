class_name UiMenu
extends Control

const CLASSES := ["havir", "zbojnice", "vedma"]

var page := "main"
var content: Control
var bg: TextureRect
var sel_class := "havir"
var name_edit: LineEdit
var desc_lbl: Label
var cards := {}
var confirm_slot := ""


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	var base := ColorRect.new()
	base.color = Color(0.03, 0.025, 0.022, 1)
	base.set_anchors_preset(Control.PRESET_FULL_RECT)
	base.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(base)
	bg = TextureRect.new()
	bg.texture = DB.tex("ui/menu_bg")
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	bg.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	UiScreens.vignette(self, Color(0, 0, 0, 0.85), 0.3)
	_drift()
	_show("main")


func _drift() -> void:
	await get_tree().process_frame
	if not is_inside_tree():
		return
	bg.pivot_offset = bg.size * Vector2(0.5, 0.4)
	var tw := create_tween().set_loops()
	tw.tween_property(bg, "scale", Vector2(1.06, 1.06), 24.0).set_trans(Tween.TRANS_SINE)
	tw.tween_property(bg, "scale", Vector2(1.0, 1.0), 24.0).set_trans(Tween.TRANS_SINE)


func _show(p: String) -> void:
	page = p
	if content:
		content.queue_free()
	content = Control.new()
	content.set_anchors_preset(Control.PRESET_FULL_RECT)
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(content)
	match p:
		"main":
			_main()
		"saves":
			_saves()
		"new":
			_new()
		"options":
			_options()
	content.modulate.a = 0.0
	create_tween().tween_property(content, "modulate:a", 1.0, 0.25)


func on_escape() -> void:
	if page != "main":
		_show("main")


func _title(parent: Control, k := 1.0) -> void:
	var tt := DB.tex("ui/title")
	if tt:
		var tr := TextureRect.new()
		tr.texture = tt
		tr.custom_minimum_size = Vector2(1000, 300) * k
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		parent.add_child(tr)
		return
	var t := UiTheme.title("PERMONÍK", int(120 * k))
	t.add_theme_constant_override("outline_size", 12)
	parent.add_child(t)
	var s := UiTheme.label(UiTheme.t("menu_subtitle"), int(44 * k), UiTheme.DIM)
	s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	parent.add_child(s)


func _column() -> VBoxContainer:
	var vb := UiScreens.center_box(content)
	vb.add_theme_constant_override("separation", 14)
	return vb


func _btn(parent: Control, text: String, cb: Callable, w := 400.0) -> Button:
	var b := UiTheme.button(text, cb, w, 30)
	b.custom_minimum_size.y = 64
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	parent.add_child(b)
	return b


# ---------------------------------------------------------------- main
func _main() -> void:
	var vb := _column()
	_title(vb)
	vb.add_child(UiTheme.sep(30))
	var saves := Game.list_saves()
	var cont := _btn(vb, L.t("menu_continue"), func(): _load(saves[0].slot))
	cont.disabled = saves.is_empty()
	if not saves.is_empty():
		var s: Dictionary = saves[0]
		cont.tooltip_text = "%s · %s %d" % [s.name, L.t("level"), int(s.level)]
	var lb := _btn(vb, UiTheme.t("menu_saves"), func(): _show("saves"))
	lb.disabled = saves.is_empty()
	_btn(vb, L.t("menu_new_game"), func(): _show("new"))
	_btn(vb, L.t("menu_options"), func(): _show("options"))
	_btn(vb, L.t("menu_quit"), func(): get_tree().quit())
	var foot := UiTheme.label("Zdař Bůh!", 22, Color(UiTheme.DIM, 0.6))
	foot.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	foot.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	foot.grow_vertical = Control.GROW_DIRECTION_BEGIN
	foot.position += Vector2(-30, -20)
	content.add_child(foot)


func _load(slot: String) -> void:
	if Game.load_game(slot):
		Game.main.start_game()


# ---------------------------------------------------------------- saves
func _saves() -> void:
	var vb := _column()
	vb.add_child(UiTheme.title(UiTheme.t("menu_saves"), 54))
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(1000, 620)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(sc)
	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_theme_constant_override("separation", 8)
	sc.add_child(list)
	var saves := Game.list_saves()
	if saves.is_empty():
		list.add_child(UiTheme.label(L.t("empty_save"), 28, UiTheme.DIM))
	for s: Dictionary in saves:
		list.add_child(_save_row(s))
	_btn(vb, L.t("menu_back"), func(): _show("main"), 300)


func _save_row(s: Dictionary) -> Control:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.06, 0.05, 0.04, 0.88), Color("4a3a28"), 2, 14))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	p.add_child(hb)
	var port := TextureRect.new()
	port.texture = DB.tex("portraits/hero_" + str(s.get("class", "")))
	port.custom_minimum_size = Vector2(84, 84)
	port.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	port.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	hb.add_child(port)
	var info := VBoxContainer.new()
	info.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	info.add_theme_constant_override("separation", 0)
	hb.add_child(info)
	info.add_child(UiTheme.label(str(s.get("name", "?")), 32, UiTheme.GOLD))
	var cls := L.t(DB.classes.get(str(s.get("class", "")), {}).get("name", s.get("class", "")))
	var act := DB.act(int(s.get("act", 1)))
	info.add_child(UiTheme.label("%s · %s %d · %s %s · %s" % [cls, L.t("level"), int(s.get("level", 1)), L.t("act"), UiQuests._roman(int(s.get("act", 1))), L.t("diff_%d" % int(s.get("difficulty", 0)))], 22, UiTheme.INK, true))
	var when := str(s.get("saved_at", "")).replace("T", " ")
	info.add_child(UiTheme.label("%s · %s" % [L.t(act.get("name", "")), when], 18, UiTheme.FAINT, true))
	var slot := str(s.slot)
	if confirm_slot == slot:
		hb.add_child(UiTheme.label(UiTheme.t("menu_delete_q", {"v": s.get("name", "")}), 24, UiTheme.RED))
		var yes := func():
			Game.delete_save(slot)
			confirm_slot = ""
			_show("saves" if not Game.list_saves().is_empty() else "main")
		hb.add_child(_mini(UiTheme.t("menu_yes"), yes))
		hb.add_child(_mini(UiTheme.t("menu_no"), func():
			confirm_slot = ""
			_show("saves")))
	else:
		hb.add_child(_mini(UiTheme.t("menu_load"), func(): _load(slot)))
		hb.add_child(_mini(L.t("delete"), func():
			confirm_slot = slot
			_show("saves")))
	return p


func _mini(text: String, cb: Callable) -> Button:
	var b := UiTheme.button(text, cb, 200, 24)
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	return b


# ---------------------------------------------------------------- new game
func _new() -> void:
	cards.clear()
	var vb := _column()
	vb.add_theme_constant_override("separation", 10)
	vb.add_child(UiTheme.title(UiTheme.t("menu_pick_class"), 50))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 30)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	vb.add_child(row)
	for cid in CLASSES:
		row.add_child(_card(cid))
	var box := PanelContainer.new()
	box.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.03, 0.025, 0.02, 0.86), Color("3a2e22"), 2, 16))
	box.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(box)
	var inner := VBoxContainer.new()
	inner.add_theme_constant_override("separation", 10)
	box.add_child(inner)
	desc_lbl = UiTheme.wrap_label("", 23, UiTheme.INK, 1120)
	desc_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	desc_lbl.custom_minimum_size.y = 96
	inner.add_child(desc_lbl)
	var form := HBoxContainer.new()
	form.add_theme_constant_override("separation", 16)
	form.alignment = BoxContainer.ALIGNMENT_CENTER
	inner.add_child(form)
	form.add_child(UiTheme.label(L.t("menu_name"), 30))
	name_edit = LineEdit.new()
	name_edit.custom_minimum_size = Vector2(340, 52)
	name_edit.max_length = 18
	name_edit.placeholder_text = UiTheme.t("menu_default_name")
	name_edit.text_submitted.connect(func(_t): _start())
	form.add_child(name_edit)
	form.add_child(UiTheme.sep(20))
	form.add_child(UiTheme.label("%s: %s" % [L.t("menu_difficulty"), L.t("diff_0")], 26, UiTheme.DIM))
	var note := UiTheme.label(UiTheme.t("menu_locked_diff"), 18, UiTheme.FAINT, true)
	note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	inner.add_child(note)
	var btns := HBoxContainer.new()
	btns.add_theme_constant_override("separation", 24)
	btns.alignment = BoxContainer.ALIGNMENT_CENTER
	vb.add_child(btns)
	var back := UiTheme.button(L.t("menu_back"), func(): _show("main"), 280, 30)
	btns.add_child(back)
	var go := UiTheme.button(L.t("menu_start"), _start, 340, 32)
	go.add_theme_color_override("font_color", UiTheme.GOLD)
	btns.add_child(go)
	_select(sel_class)


func _card(cid: String) -> Control:
	var c := PanelContainer.new()
	c.mouse_filter = Control.MOUSE_FILTER_STOP
	c.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 4)
	vb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.add_child(vb)
	var t := TextureRect.new()
	t.texture = DB.tex("ui/class_" + cid)
	if t.texture == null:
		t.texture = DB.tex("portraits/hero_" + cid)
	t.custom_minimum_size = Vector2(300, 450)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vb.add_child(t)
	var cd: Dictionary = DB.classes.get(cid, {})
	var n := UiTheme.title(L.t(cd.get("name", cid)), 38)
	vb.add_child(n)
	var b: Dictionary = cd.get("base", {})
	var st := UiTheme.label("%s %d · %s %d · %s %d · %s %d" % [L.t("stat_sila").left(3), int(b.get("sila", 0)), L.t("stat_obratnost").left(3), int(b.get("obratnost", 0)), L.t("stat_magie").left(3), int(b.get("magie", 0)), L.t("stat_vitalita").left(3), int(b.get("vitalita", 0))], 17, UiTheme.DIM, true)
	st.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(st)
	c.gui_input.connect(func(e: InputEvent):
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			Sfx.play("ui_click", 0.6, 0.0)
			_select(cid)
			if e.double_click:
				_start())
	c.mouse_entered.connect(func(): _hover(cid, true))
	c.mouse_exited.connect(func(): _hover(cid, false))
	cards[cid] = c
	return c


func _hover(cid: String, on: bool) -> void:
	if cid != sel_class and cards.has(cid):
		cards[cid].modulate = Color(0.85, 0.82, 0.78) if on else Color(0.55, 0.52, 0.5)


func _select(cid: String) -> void:
	sel_class = cid
	for k in cards:
		var c: PanelContainer = cards[k]
		var on: bool = k == cid
		var sb := UiTheme.flat(Color(0.04, 0.035, 0.03, 0.9), UiTheme.GOLD if on else Color("3a2e22"), 3 if on else 2, 6)
		if on:
			sb.shadow_color = Color(UiTheme.GOLD, 0.25)
			sb.shadow_size = 14
		c.add_theme_stylebox_override("panel", sb)
		c.modulate = Color.WHITE if on else Color(0.55, 0.52, 0.5)
	desc_lbl.text = L.t(DB.classes.get(cid, {}).get("desc", ""))


func _start() -> void:
	var nm := name_edit.text.strip_edges()
	if nm == "":
		nm = L.t(DB.classes.get(sel_class, {}).get("name", UiTheme.t("menu_default_name")))
	Game.new_game(sel_class, nm)
	Game.main.start_game()


# ---------------------------------------------------------------- options
func _options() -> void:
	var vb := _column()
	vb.add_child(UiTheme.title(L.t("menu_options"), 54))
	vb.add_child(UiTheme.sep(10))
	var p := UiPanel.new()
	p.body.add_child(UiScreens.options(func(): _show("options")))
	vb.add_child(p)
	vb.add_child(UiTheme.sep(10))
	_btn(vb, L.t("menu_back"), func(): _show("main"), 300)
