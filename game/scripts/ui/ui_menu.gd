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
var sel_slot := ""


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
	Game.storage_changed.connect(_on_storage_changed)


func _on_storage_changed() -> void:
	if page in ["main", "saves"]:
		_show(page)


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
		"story":
			_story()
	if p == "options" and _phone():
		return
	content.modulate.a = 0.0
	_fit_content(content)


# Pages are laid out for a 1080 px tall screen; on a phone they shrink until everything is on screen.
func _fit_content(c: Control) -> void:
	await get_tree().process_frame
	await get_tree().process_frame
	if not is_instance_valid(c):
		return
	var box := Rect2()
	for n in c.find_children("*", "Control", true, false):
		var r: Rect2 = (n as Control).get_global_rect()
		if n is Container or r.size.x >= c.size.x - 1.0 or not (n as Control).is_visible_in_tree():
			continue
		box = r if box.size == Vector2.ZERO else box.merge(r)
	var gr := c.get_global_rect()
	var k := minf(1.0, minf((gr.size.y - 16.0) / maxf(1.0, box.size.y), (gr.size.x - 16.0) / maxf(1.0, box.size.x)))
	if k < 1.0:
		c.pivot_offset = gr.size / 2.0
		c.scale = Vector2(k, k)
		var mid := gr.position + gr.size / 2.0
		var top := mid.y + (box.position.y - mid.y) * k
		var bottom := mid.y + (box.end.y - mid.y) * k
		if top < gr.position.y + 8.0:
			c.position.y += gr.position.y + 8.0 - top
		elif bottom > gr.end.y - 8.0:
			c.position.y -= bottom - (gr.end.y - 8.0)
	create_tween().tween_property(c, "modulate:a", 1.0, 0.25)


func _unhandled_key_input(e: InputEvent) -> void:
	if page != "saves" or not e.is_pressed() or e.is_echo():
		return
	var saves := Game.list_saves()
	var i := -1
	for j in saves.size():
		if saves[j].slot == sel_slot:
			i = j
	match (e as InputEventKey).keycode:
		KEY_UP, KEY_DOWN:
			i = clampi(i + (1 if e.keycode == KEY_DOWN else -1), 0, saves.size() - 1)
			sel_slot = str(saves[i].slot)
			confirm_slot = ""
			_show("saves")
			get_viewport().set_input_as_handled()
		KEY_ENTER, KEY_KP_ENTER:
			_load(sel_slot)
			get_viewport().set_input_as_handled()


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


func _phone() -> bool:
	return UiRoot.inst != null and UiRoot.inst.compact()


func _btn(parent: Control, text: String, cb: Callable, w := 480.0) -> Button:
	var b := UiTheme.button(text, cb, w, 30)
	b.custom_minimum_size.y = 64
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	parent.add_child(b)
	return b


# ---------------------------------------------------------------- main
# Phones: the title on the left and the buttons beside it, so neither has to shrink.
func _main() -> void:
	var vb := _column()
	if _phone():
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 40)
		hb.alignment = BoxContainer.ALIGNMENT_CENTER
		vb.add_child(hb)
		_title(hb, 0.72)
		vb = VBoxContainer.new()
		vb.add_theme_constant_override("separation", 10)
		vb.alignment = BoxContainer.ALIGNMENT_CENTER
		hb.add_child(vb)
	else:
		_title(vb)
		vb.add_child(UiTheme.sep(30))
	var saves := Game.list_saves()
	var cont := _btn(vb, L.t("menu_continue"), func(): _load(saves[0].slot))
	cont.disabled = saves.is_empty()
	if not saves.is_empty():
		var s: Dictionary = saves[0]
		cont.text = "%s: %s (%d)" % [L.t("menu_continue"), s.name, int(s.level)]
	var lb := _btn(vb, UiTheme.t("menu_saves"), func(): _show("saves"))
	lb.disabled = saves.is_empty()
	_btn(vb, L.t("menu_new_game"), func(): _show("new"))
	_btn(vb, UiTheme.t("menu_story"), func(): _show("story"))
	_btn(vb, L.t("menu_options"), func(): _show("options"))
	if not OS.has_feature("web"):
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


# ---------------------------------------------------------------- heroes
# The heroes on the left, the chosen one standing on the right in what they wear now.
func _saves() -> void:
	var saves := Game.list_saves()
	if saves.is_empty():
		_show("main")
		return
	if sel_slot == "" or saves.filter(func(x): return x.slot == sel_slot).is_empty():
		sel_slot = str(saves[0].slot)
	var s: Dictionary = saves.filter(func(x): return x.slot == sel_slot)[0]
	UiScreens.dim(content, 0.62)
	var left := PanelContainer.new()
	left.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.05, 0.04, 0.035, 0.9), Color("4a3a28"), 2, 18))
	var vs := UiRoot.inst.root.size
	left.position = Vector2(20, 16) if _phone() else Vector2(60, 70)
	left.size = Vector2(560, vs.y - 32) if _phone() else Vector2(560, 940)
	content.add_child(left)
	var lv := VBoxContainer.new()
	lv.add_theme_constant_override("separation", 10)
	left.add_child(lv)
	lv.add_child(UiTheme.title(UiTheme.t("menu_saves"), 48))
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	lv.add_child(sc)
	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_theme_constant_override("separation", 6)
	sc.add_child(list)
	for row: Dictionary in saves:
		list.add_child(_hero_row(row))
	var foot := HBoxContainer.new()
	foot.add_theme_constant_override("separation", 12)
	foot.alignment = BoxContainer.ALIGNMENT_CENTER
	lv.add_child(foot)
	foot.add_child(UiTheme.button(L.t("menu_new_game"), func(): _show("new"), 250, 26))
	foot.add_child(UiTheme.button(L.t("menu_back"), func(): _show("main"), 250, 26))
	_hero_stage(s)


func _hero_row(s: Dictionary) -> Control:
	var on := str(s.slot) == sel_slot
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.16, 0.12, 0.07, 0.95) if on else Color(0.08, 0.065, 0.05, 0.85),
		UiTheme.GOLD if on else Color("3a2e20"), 2, 10))
	p.mouse_filter = Control.MOUSE_FILTER_STOP
	p.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	var slot := str(s.slot)
	p.gui_input.connect(func(e: InputEvent):
		if e is InputEventMouseButton and e.pressed and e.button_index == MOUSE_BUTTON_LEFT:
			if e.double_click:
				_load(slot)
			elif sel_slot != slot:
				sel_slot = slot
				confirm_slot = ""
				_show("saves"))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 14)
	hb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_child(hb)
	var port := TextureRect.new()
	port.texture = DB.tex("portraits/hero_" + str(s.get("class", "")))
	port.custom_minimum_size = Vector2(72, 72)
	port.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	port.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	port.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.add_child(port)
	var info := VBoxContainer.new()
	info.add_theme_constant_override("separation", 0)
	info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hb.add_child(info)
	info.add_child(UiTheme.label(str(s.get("name", "?")), 30, UiTheme.GOLD if on else UiTheme.INK))
	var cls := L.t(DB.class_def(str(s.get("class", ""))).get("name", s.get("class", "")))
	info.add_child(UiTheme.label("%s · %s %d" % [cls, L.t("level"), int(s.get("level", 1))], 22, UiTheme.INK, true))
	info.add_child(UiTheme.label("%s %s · %s" % [L.t("act"), UiQuests._roman(int(s.get("act", 1))), L.t("diff_%d" % int(s.get("difficulty", 0)))], 18, UiTheme.FAINT, true))
	for c in info.get_children():
		c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


# A soft round pool of colour: darkness behind the hero, lamplight under the feet.
func _pool(col: Color, r: Rect2) -> TextureRect:
	var g := Gradient.new()
	g.set_color(0, col)
	g.set_color(1, Color(col, 0.0))
	var gt := GradientTexture2D.new()
	gt.gradient = g
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(0.5, 0.0)
	var t := TextureRect.new()
	t.texture = gt
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	t.position = r.position
	t.size = r.size
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return t


func _hero_stage(s: Dictionary) -> void:
	var stage := Control.new()
	stage.position = Vector2(700, 40)
	stage.size = Vector2(1160, 1000)
	stage.mouse_filter = Control.MOUSE_FILTER_IGNORE
	content.add_child(stage)
	if _phone():
		var vs := UiRoot.inst.root.size
		var k := minf(vs.y / 1000.0, (vs.x - 600.0) / 1160.0)
		stage.scale = Vector2(k, k)
		stage.position = Vector2(600.0 + (vs.x - 600.0 - 1160.0 * k) / 2.0, (vs.y - 1000.0 * k) / 2.0)
	stage.add_child(_pool(Color(1.0, 0.85, 0.6, 0.1), Rect2(stage.size.x / 2 - 520, 120, 1040, 900)))
	stage.add_child(_pool(Color(1.0, 0.78, 0.45, 0.5), Rect2(stage.size.x / 2 - 320, 790, 640, 130)))
	var fig := TextureRect.new()
	fig.texture = HeroLook.portrait(str(s.get("class", "")), s.get("gear", {}))
	fig.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	fig.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	fig.size = Vector2(760, 760)
	fig.position = Vector2(stage.size.x / 2 - 380, 110)
	fig.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stage.add_child(fig)
	var name_l := UiTheme.title(str(s.get("name", "?")), 64)
	name_l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_l.position = Vector2(0, 30)
	name_l.size = Vector2(stage.size.x, 80)
	stage.add_child(name_l)
	var cls := L.t(DB.class_def(str(s.get("class", ""))).get("name", s.get("class", "")))
	var act := DB.act(int(s.get("act", 1)))
	var sub := UiTheme.label("%s · %s %d · %s" % [cls, L.t("level"), int(s.get("level", 1)), L.t(act.get("name", ""))], 28, UiTheme.INK)
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.position = Vector2(0, 104)
	sub.size = Vector2(stage.size.x, 40)
	stage.add_child(sub)
	var bar := HBoxContainer.new()
	bar.alignment = BoxContainer.ALIGNMENT_CENTER
	bar.add_theme_constant_override("separation", 18)
	bar.position = Vector2(0, 890)
	bar.size = Vector2(stage.size.x, 70)
	stage.add_child(bar)
	var slot := str(s.slot)
	if confirm_slot == slot:
		bar.add_child(UiTheme.label(UiTheme.t("menu_delete_q", {"v": s.get("name", "")}), 26, UiTheme.RED))
		bar.add_child(_mini(UiTheme.t("menu_yes"), func():
			Game.delete_save(slot)
			confirm_slot = ""
			sel_slot = ""
			_show("saves" if not Game.list_saves().is_empty() else "main")))
		bar.add_child(_mini(UiTheme.t("menu_no"), func():
			confirm_slot = ""
			_show("saves")))
	else:
		var play := UiTheme.button(UiTheme.t("menu_load"), func(): _load(slot), 360, 34)
		play.custom_minimum_size.y = 70
		bar.add_child(play)
		bar.add_child(_mini(L.t("delete"), func():
			confirm_slot = slot
			_show("saves")))
	if _phone():
		var vs := UiRoot.inst.root.size
		bar.reparent(content, false)
		bar.position = Vector2(stage.position.x, vs.y - 84.0)
		bar.size = Vector2(1160.0 * stage.scale.x, 70)


func _mini(text: String, cb: Callable) -> Button:
	var b := UiTheme.button(text, cb, 200, 24)
	b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	return b


# ---------------------------------------------------------------- new game
# Phones: smaller cards in a row on the left, the description, name and buttons in a column beside them.
func _new() -> void:
	cards.clear()
	var ph := _phone()
	var vb := _column()
	vb.add_theme_constant_override("separation", 10)
	vb.add_child(UiTheme.title(UiTheme.t("menu_pick_class"), 40 if ph else 50))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 30 if DB.classes.size() <= 4 and not ph else 12)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	var side := vb
	if ph:
		var hb := HBoxContainer.new()
		hb.add_theme_constant_override("separation", 20)
		hb.alignment = BoxContainer.ALIGNMENT_CENTER
		vb.add_child(hb)
		hb.add_child(row)
		side = VBoxContainer.new()
		side.add_theme_constant_override("separation", 10)
		side.alignment = BoxContainer.ALIGNMENT_CENTER
		hb.add_child(side)
	else:
		vb.add_child(row)
	for cid in DB.classes:
		row.add_child(_card(cid))
	var box := PanelContainer.new()
	box.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.03, 0.025, 0.02, 0.86), Color("3a2e22"), 2, 16))
	box.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	side.add_child(box)
	var inner := VBoxContainer.new()
	inner.add_theme_constant_override("separation", 10)
	box.add_child(inner)
	desc_lbl = UiTheme.wrap_label("", 23, UiTheme.INK, 520 if ph else 1120)
	desc_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	desc_lbl.custom_minimum_size.y = 190 if ph else 96
	inner.add_child(desc_lbl)
	var form: BoxContainer = VBoxContainer.new() if ph else HBoxContainer.new()
	form.add_theme_constant_override("separation", 8 if ph else 16)
	form.alignment = BoxContainer.ALIGNMENT_CENTER
	inner.add_child(form)
	var name_row := HBoxContainer.new()
	name_row.add_theme_constant_override("separation", 16)
	name_row.alignment = BoxContainer.ALIGNMENT_CENTER
	form.add_child(name_row)
	name_row.add_child(UiTheme.label(L.t("menu_name"), 30))
	name_edit = LineEdit.new()
	name_edit.custom_minimum_size = Vector2(340, 56)
	name_edit.max_length = 18
	name_edit.placeholder_text = UiTheme.t("menu_default_name")
	name_edit.text_submitted.connect(func(_t): _start())
	name_row.add_child(name_edit)
	if not ph:
		form.add_child(UiTheme.sep(20))
	var diff := UiTheme.label("%s: %s" % [L.t("menu_difficulty"), L.t("diff_0")], 26, UiTheme.DIM)
	diff.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	form.add_child(diff)
	var note := UiTheme.label(UiTheme.t("menu_locked_diff"), 18, UiTheme.FAINT, true)
	note.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	inner.add_child(note)
	var btns := HBoxContainer.new()
	btns.add_theme_constant_override("separation", 24)
	btns.alignment = BoxContainer.ALIGNMENT_CENTER
	side.add_child(btns)
	var back := UiTheme.button(L.t("menu_back"), func(): _show("main"), 220 if ph else 280, 30)
	btns.add_child(back)
	var go := UiTheme.button(L.t("menu_start"), _start, 280 if ph else 340, 32)
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
	var wide := DB.classes.size() <= 4 and not _phone()
	t.custom_minimum_size = Vector2(300, 450) if wide else Vector2(196, 294)
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vb.add_child(t)
	var cd: Dictionary = DB.classes.get(cid, {})
	var n := UiTheme.title(L.t(cd.get("name", cid)), 38 if wide else 28)
	vb.add_child(n)
	var b: Dictionary = cd.get("base", {})
	var st := UiTheme.label("%s %d · %s %d · %s %d · %s %d" % [L.t("stat_sila").left(3), int(b.get("sila", 0)), L.t("stat_obratnost").left(3), int(b.get("obratnost", 0)), L.t("stat_magie").left(3), int(b.get("magie", 0)), L.t("stat_vitalita").left(3), int(b.get("vitalita", 0))], 17 if wide else 13, UiTheme.DIM, true)
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
# Phones: the settings scroll between the title and Back instead of shrinking.
func _options() -> void:
	if _phone():
		UiScreens.options_page(content, L.t("menu_options"), func(): _show("main"), func(): _show("options"))
		return
	var vb := _column()
	vb.add_child(UiTheme.title(L.t("menu_options"), 54))
	vb.add_child(UiTheme.sep(10))
	var p := UiPanel.new()
	p.body.add_child(UiScreens.options(func(): _show("options")))
	vb.add_child(p)
	vb.add_child(UiTheme.sep(10))
	_btn(vb, L.t("menu_back"), func(): _show("main"), 300)


# ---------------------------------------------------------------- story
# Every cinematic once seen (or passed with any hero), to watch again in order.
static func film_unlocked(id: String, saves: Array) -> bool:
	if UiCinema.seen().has(id):
		return true
	var need := {"intro": [1, 0], "act1_end": [2, 0], "act2_end": [3, 0], "act3_end": [4, 0], "act4_intro": [4, 0]}
	for s in saves:
		var act := int(s.act)
		var diff := int(s.difficulty)
		if diff > 0 or (need.has(id) and act >= need[id][0]):
			return true
	return false


func _story() -> void:
	UiScreens.dim(content, 0.7)
	var vb := _column()
	vb.add_theme_constant_override("separation", 18)
	vb.add_child(UiTheme.title(UiTheme.t("menu_story"), 56))
	var hint := UiTheme.label(UiTheme.t("story_hint"), 22, UiTheme.DIM)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(hint)
	var grid := GridContainer.new()
	grid.columns = 4
	grid.add_theme_constant_override("h_separation", 18)
	grid.add_theme_constant_override("v_separation", 18)
	vb.add_child(grid)
	var saves := Game.list_saves()
	var open: Array = []
	for id in CinFilms.ORDER:
		var ok := film_unlocked(id, saves)
		if ok:
			open.append(id)
		grid.add_child(_film_card(id, ok))
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 20)
	vb.add_child(row)
	var all := _btn(row, UiTheme.t("story_all"), func():
		for id in open:
			Game.main.play_slides(id), 300)
	all.disabled = open.is_empty()
	_btn(row, L.t("menu_back"), func(): _show("main"), 300)


func _film_card(id: String, ok: bool) -> Button:
	var info: Dictionary = DB.cinema.get(id, {})
	var b := Button.new()
	b.custom_minimum_size = Vector2(390, 300)
	b.focus_mode = Control.FOCUS_NONE
	b.add_theme_stylebox_override("normal", UiTheme.flat(Color(0.05, 0.04, 0.035, 0.9), Color("4a3a28"), 2, 10))
	b.add_theme_stylebox_override("hover", UiTheme.flat(Color(0.08, 0.06, 0.045, 0.95), UiTheme.GOLD, 2, 10))
	b.add_theme_stylebox_override("pressed", UiTheme.flat(Color(0.08, 0.06, 0.045, 0.95), UiTheme.GOLD, 2, 10))
	b.add_theme_stylebox_override("disabled", UiTheme.flat(Color(0.03, 0.025, 0.02, 0.9), Color("2a2218"), 2, 10))
	b.disabled = not ok
	b.pressed.connect(func():
		Sfx.play("ui_click")
		UiRoot.inst.play_cinema(id, Callable()))
	var col := VBoxContainer.new()
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.set_anchors_preset(Control.PRESET_FULL_RECT)
	col.offset_left = 12
	col.offset_top = 12
	col.offset_right = -12
	col.offset_bottom = -10
	col.add_theme_constant_override("separation", 6)
	b.add_child(col)
	var pic := TextureRect.new()
	pic.texture = UiCinema.tex("thumbs/" + id) if ok else null
	pic.custom_minimum_size = Vector2(366, 206)
	pic.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	pic.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	pic.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(pic)
	var t := UiTheme.label(L.t(info.get("title", id)) if ok else "?", 26, UiTheme.GOLD if ok else UiTheme.DIM)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(t)
	var w := UiTheme.label(L.t(info.get("when", "")) if ok else UiTheme.t("story_locked"), 18, UiTheme.DIM, true)
	w.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	col.add_child(w)
	return b
