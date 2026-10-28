class_name Hud
extends CanvasLayer

const BAR_H := 160
const BELT_X := 631
const SKILL_X := 945
const SLOT_Y := 72
const SLOT_GAP := 70
const XP_PHONE := 10.0

var font: Font
var root: Control
var bar: Control
var hp_orb: TextureProgressBar
var mana_orb: TextureProgressBar
var hp_lbl: Label
var mana_lbl: Label
var xp_bar: TextureProgressBar
var xp_lbl: Label
var hurt: TextureRect
var hurt_flash := 0.0
var last_hp := -1.0
var belt_slots: Array = []
var skill_slots: Array = []
var target_box: VBoxContainer
var target_name: Label
var target_sub: Label
var target_hp: ProgressBar
var boss_box: Control
var boss_fill: ColorRect
var boss_name: Label
var log_box: VBoxContainer
var say_box: PanelContainer
var say_portrait: TextureRect
var say_name: Label
var say_text: Label
var say_t := 0.0
var banner: Label
var lvl_btn: Button
var menu_btns: GridContainer
var mini: Control
var xp_back: ColorRect
var _home := {}
var automap: Automap
var minimap: Minimap
var tracker: QuestTracker
var hovered_controls: Array = []


func _ready() -> void:
	layer = 20
	font = load("res://assets/fonts/TataHand.ttf")
	root = Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	automap = Automap.new()
	automap.set_anchors_preset(Control.PRESET_FULL_RECT)
	automap.mouse_filter = Control.MOUSE_FILTER_IGNORE
	automap.visible = false
	root.add_child(automap)
	hurt = UiScreens.vignette(root, Color(0.55, 0.0, 0.0, 0.9), 0.45)
	hurt.modulate.a = 0.0
	minimap = Minimap.new()
	minimap.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	minimap.position = Vector2(-Minimap.SIZE - 14, 10)
	root.add_child(minimap)
	tracker = QuestTracker.new()
	if TouchPad.wanted():
		tracker.position = Vector2(16, 104)
	else:
		tracker.set_anchors_preset(Control.PRESET_TOP_RIGHT)
		tracker.position = Vector2(-QuestTracker.W - 34, Minimap.SIZE + 8)
	root.add_child(tracker)
	_build_bar()
	_build_target()
	_build_boss()
	_build_log()
	_build_say()
	banner = _label(54, Color("e8dcc0"))
	banner.set_anchors_preset(Control.PRESET_CENTER_TOP)
	banner.position = Vector2(-600, 170)
	banner.size = Vector2(1200, 80)
	banner.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	banner.modulate.a = 0.0
	root.add_child(banner)
	Game.message.connect(_on_message)
	Game.boss_bar.connect(_on_boss_bar)
	Game.ch.leveled.connect(_on_level)


func _label(size: int, color: Color) -> Label:
	var l := Label.new()
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	l.add_theme_constant_override("outline_size", 6)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


func _tex_rect(path: String, pos: Vector2, size: Vector2) -> TextureRect:
	var t := TextureRect.new()
	t.texture = DB.tex(path)
	t.position = pos
	t.size = size
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	return t


func _orb(tex_path: String, center: Vector2, fallback: Color) -> TextureProgressBar:
	var o := TextureProgressBar.new()
	o.fill_mode = TextureProgressBar.FILL_BOTTOM_TO_TOP
	var t := DB.tex(tex_path)
	if t == null:
		var img := Image.create(160, 160, false, Image.FORMAT_RGBA8)
		for y in 160:
			for x in 160:
				if Vector2(x - 80, y - 80).length() < 79:
					img.set_pixel(x, y, fallback.lightened(0.15 * (1.0 - y / 160.0)))
		t = ImageTexture.create_from_image(img)
	o.texture_progress = t
	o.position = center - Vector2(80, 80)
	o.size = Vector2(160, 160)
	o.max_value = 1000
	o.mouse_filter = Control.MOUSE_FILTER_PASS
	return o


func _build_bar() -> void:
	bar = Control.new()
	bar.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	bar.size = Vector2(1920, BAR_H)
	bar.position = Vector2(-960, -BAR_H)
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(bar)
	var back := ColorRect.new()
	back.color = Color(0.06, 0.05, 0.05, 1)
	back.position = Vector2(0, 30)
	back.size = Vector2(1920, BAR_H - 30)
	back.mouse_filter = Control.MOUSE_FILTER_STOP
	bar.add_child(back)
	hp_orb = _orb("ui/orb_hp", Vector2(100, 64), Color("a01818"))
	mana_orb = _orb("ui/orb_mana", Vector2(1820, 64), Color("1838a0"))
	bar.add_child(hp_orb)
	bar.add_child(mana_orb)
	if DB.tex("ui/hud_bar"):
		bar.add_child(_tex_rect("ui/hud_bar", Vector2.ZERO, Vector2(1920, BAR_H)))
	for c in [Vector2(100, 64), Vector2(1820, 64)]:
		if DB.tex("ui/orb_frame"):
			bar.add_child(_tex_rect("ui/orb_frame", c - Vector2(96, 96), Vector2(192, 192)))
	hp_lbl = _label(22, Color("ffd8d0"))
	hp_lbl.position = Vector2(30, 50)
	hp_lbl.size = Vector2(140, 30)
	hp_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bar.add_child(hp_lbl)
	mana_lbl = _label(22, Color("d0dcff"))
	mana_lbl.position = Vector2(1750, 50)
	mana_lbl.size = Vector2(140, 30)
	mana_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	bar.add_child(mana_lbl)
	xp_bar = TextureProgressBar.new()
	var xt := DB.tex("ui/xp_bar")
	if xt:
		xp_bar.texture_progress = xt
		xp_bar.nine_patch_stretch = true
	xp_bar.position = Vector2(360, 22)
	xp_bar.size = Vector2(1200, 20)
	xp_bar.max_value = 1000
	xp_bar.mouse_filter = Control.MOUSE_FILTER_PASS
	bar.add_child(xp_bar)
	xp_lbl = _label(15, Color(0.92, 0.86, 0.7, 0.75))
	xp_lbl.position = xp_bar.position + Vector2(0, -2)
	xp_lbl.size = xp_bar.size
	xp_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	xp_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	xp_lbl.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.add_child(xp_lbl)
	for i in 8:
		var s := SlotView.new()
		s.hud = self
		s.kind = "belt"
		s.index = i
		s.position = Vector2(BELT_X + (i % 4) * SLOT_GAP, SLOT_Y - (70 if i >= 4 else 0))
		bar.add_child(s)
		belt_slots.append(s)
	var keys := ["RMB", "Q", "W", "E", "R"]
	for i in 5:
		var s := SlotView.new()
		s.hud = self
		s.kind = "skill"
		s.index = i
		s.key = keys[i]
		s.position = Vector2(SKILL_X + i * SLOT_GAP, SLOT_Y)
		bar.add_child(s)
		skill_slots.append(s)
	var touch := TouchPad.wanted()
	var btns := GridContainer.new()
	menu_btns = btns
	btns.columns = 3
	btns.position = Vector2(214, 52 if touch else 64)
	btns.add_theme_constant_override("h_separation", 6)
	btns.add_theme_constant_override("v_separation", 6)
	bar.add_child(btns)
	for pair in [["character", "C"], ["inventory", "I"], ["skills", "S"], ["quests", "J"], ["kronika", "K"], ["automap", "Tab"]]:
		var b := Button.new()
		b.text = L.t(pair[0]).left(9)
		b.tooltip_text = "%s (%s)" % [L.t(pair[0]), pair[1]]
		b.add_theme_font_override("font", font)
		b.add_theme_font_size_override("font_size", 22 if touch else 18)
		b.custom_minimum_size = Vector2(130, 46 if touch else 38)
		b.clip_text = true
		b.alignment = HORIZONTAL_ALIGNMENT_CENTER
		b.focus_mode = Control.FOCUS_NONE
		var action: String = pair[0]
		b.pressed.connect(func(): toggle(action))
		btns.add_child(b)
	lvl_btn = Button.new()
	lvl_btn.text = "+"
	lvl_btn.tooltip_text = L.t("level_up")
	lvl_btn.add_theme_font_override("font", font)
	lvl_btn.add_theme_font_size_override("font_size", 30)
	lvl_btn.add_theme_color_override("font_color", Color("ffd27a"))
	lvl_btn.position = Vector2(200, 4)
	lvl_btn.size = Vector2(44, 44)
	lvl_btn.focus_mode = Control.FOCUS_NONE
	lvl_btn.pressed.connect(func():
		if Game.ch.stat_points > 0:
			toggle("character")
		else:
			toggle("skills"))
	bar.add_child(lvl_btn)


func _build_target() -> void:
	target_box = VBoxContainer.new()
	target_box.set_anchors_preset(Control.PRESET_CENTER_TOP)
	target_box.position = Vector2(-260, 14)
	target_box.size = Vector2(520, 80)
	target_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	target_box.alignment = BoxContainer.ALIGNMENT_BEGIN
	root.add_child(target_box)
	target_name = _label(30, Color.WHITE)
	target_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	target_box.add_child(target_name)
	target_sub = _label(19, Color("bcae90"))
	target_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	target_box.add_child(target_sub)
	target_hp = ProgressBar.new()
	target_hp.custom_minimum_size = Vector2(520, 10)
	target_hp.show_percentage = false
	target_hp.max_value = 1.0
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0.1, 0.05, 0.05, 0.8)
	var fg := StyleBoxFlat.new()
	fg.bg_color = Color("9a1c1c")
	target_hp.add_theme_stylebox_override("background", bg)
	target_hp.add_theme_stylebox_override("fill", fg)
	target_hp.mouse_filter = Control.MOUSE_FILTER_IGNORE
	target_box.add_child(target_hp)


func _build_boss() -> void:
	boss_box = Control.new()
	boss_box.set_anchors_preset(Control.PRESET_CENTER_TOP)
	boss_box.position = Vector2(-450, 110)
	boss_box.size = Vector2(900, 48)
	boss_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	boss_box.visible = false
	root.add_child(boss_box)
	var bg := ColorRect.new()
	bg.color = Color(0.08, 0.02, 0.02, 0.85)
	bg.position = Vector2(48, 14)
	bg.size = Vector2(804, 20)
	boss_box.add_child(bg)
	boss_fill = ColorRect.new()
	boss_fill.color = Color("b01e1e")
	boss_fill.position = Vector2(48, 14)
	boss_fill.size = Vector2(804, 20)
	boss_box.add_child(boss_fill)
	if DB.tex("ui/boss_bar"):
		boss_box.add_child(_tex_rect("ui/boss_bar", Vector2.ZERO, Vector2(900, 48)))
	boss_name = _label(24, Color("f0d8a8"))
	boss_name.position = Vector2(0, 40)
	boss_name.size = Vector2(900, 30)
	boss_name.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	boss_box.add_child(boss_name)


func _build_log() -> void:
	log_box = VBoxContainer.new()
	log_box.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
	log_box.position = Vector2(220, -BAR_H - 230)
	log_box.size = Vector2(700, 220)
	log_box.alignment = BoxContainer.ALIGNMENT_END
	log_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(log_box)


func _build_say() -> void:
	say_box = PanelContainer.new()
	say_box.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	say_box.position = Vector2(-520, -BAR_H - 190)
	say_box.size = Vector2(1040, 150)
	say_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.04, 0.03, 0.04, 0.88)
	sb.border_color = Color("6a5a40")
	sb.set_border_width_all(2)
	sb.set_content_margin_all(12)
	say_box.add_theme_stylebox_override("panel", sb)
	say_box.modulate.a = 0.0
	root.add_child(say_box)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 16)
	say_box.add_child(hb)
	say_portrait = TextureRect.new()
	say_portrait.custom_minimum_size = Vector2(120, 120)
	say_portrait.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	say_portrait.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	hb.add_child(say_portrait)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(vb)
	say_name = _label(26, Color("e9c46a"))
	vb.add_child(say_name)
	say_text = _label(24, Color("efe6d4"))
	say_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	say_text.custom_minimum_size = Vector2(860, 0)
	vb.add_child(say_text)


func boss_line(who: String, text: String, portrait: String, dur := 4.5) -> void:
	say_name.text = who
	say_text.text = "„%s“" % text
	var pt := DB.tex("portraits/boss_" + portrait)
	if pt == null:
		pt = DB.tex("portraits/" + portrait)
	say_portrait.texture = pt
	say_portrait.visible = pt != null
	say_t = dur
	create_tween().tween_property(say_box, "modulate:a", 1.0, 0.3)


func on_location(a: int, f: int) -> void:
	var ad := DB.act(a)
	var txt := ""
	if f == 0:
		txt = L.t(ad.get("town", {}).get("name", "Hora"))
	else:
		var fd := DB.floor_def(a, f)
		txt = "%s · %s %d" % [L.t(ad.get("dungeon", {}).get("name", "")), L.t("floor"), f]
		if fd.has("name"):
			txt = L.t(fd.name)
	banner.text = txt
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 1.0, 0.6)
	tw.tween_interval(2.2)
	tw.tween_property(banner, "modulate:a", 0.0, 1.0)
	automap.visible = false
	minimap.visible = true
	tracker.visible = true
	_on_boss_bar("", 0.0, false)


func toggle(what: String) -> void:
	if what == "automap":
		automap.visible = not automap.visible
		minimap.visible = not automap.visible
		tracker.visible = not automap.visible
		return
	if Game.main:
		Game.main.ui.toggle_panel(what)


func _on_message(text: String, color: Color) -> void:
	var l := _label(22, color)
	l.text = text
	log_box.add_child(l)
	while log_box.get_child_count() > 6:
		var old := log_box.get_child(0)
		log_box.remove_child(old)
		old.queue_free()
	var tw := l.create_tween()
	tw.tween_interval(5.0)
	tw.tween_property(l, "modulate:a", 0.0, 1.5)
	tw.tween_callback(l.queue_free)


func _on_boss_bar(nm: String, ratio: float, vis: bool) -> void:
	boss_box.visible = vis
	if vis:
		boss_name.text = nm
		boss_fill.size.x = 804.0 * clampf(ratio, 0.0, 1.0)


func _on_level(lv: int) -> void:
	banner.text = "%s %d" % [L.t("level_up"), lv]
	Sfx.play("levelup")
	if Game.player and Game.level:
		Fx.burst(Game.level, Game.player.global_position + Vector2(0, -60), Color("ffe7a0"), 40, 140, 1.2, 0.3, true)
		Fx.ring(Game.level, Game.player.global_position, 140, Color("ffe7a0"), 0.8)
	var tw := create_tween()
	tw.tween_property(banner, "modulate:a", 1.0, 0.3)
	tw.tween_interval(1.6)
	tw.tween_property(banner, "modulate:a", 0.0, 0.8)


func fit() -> void:
	var k := minf(1.0, root.size.x / 1920.0)
	bar.pivot_offset = Vector2(960, BAR_H)
	bar.scale = Vector2(k, k)
	_set_compact(root.size.y < 760.0)
	var mk := 0.7 if not _home.is_empty() else 1.0
	minimap.scale = Vector2(mk, mk)
	minimap.offset_left = -Minimap.SIZE * mk - 14
	minimap.offset_right = minimap.offset_left + Minimap.SIZE
	minimap.offset_top = 10
	minimap.offset_bottom = 10 + Minimap.SIZE


# Phone screens: no bar. The orbs sit in the bottom corners over an xp line across the whole bottom edge, the
# quest tracker is top left; panels open from the touch pad's bag button, skills and potions are on the pad.
func _set_compact(on: bool) -> void:
	if mini == null:
		if not on:
			return
		mini = Control.new()
		mini.mouse_filter = Control.MOUSE_FILTER_IGNORE
		root.add_child(mini)
		xp_back = ColorRect.new()
		xp_back.color = Color(0.04, 0.03, 0.03, 0.85)
		xp_back.mouse_filter = Control.MOUSE_FILTER_IGNORE
		mini.add_child(xp_back)
	var nodes: Array = [hp_orb, mana_orb, hp_lbl, mana_lbl, xp_bar, xp_lbl, lvl_btn]
	if on and _home.is_empty():
		for n: Control in nodes:
			_home[n] = [n.position, n.scale]
			n.reparent(mini, false)
	elif not on and not _home.is_empty():
		for l: Label in [hp_lbl, mana_lbl]:
			l.add_theme_font_size_override("font_size", 22)
		for n: Control in nodes:
			n.reparent(bar, false)
			n.position = _home[n][0]
			n.scale = _home[n][1]
		_home.clear()
	mini.visible = on
	bar.visible = not on
	if not on:
		return
	var o := 0.68
	var w := root.size.x
	var h := root.size.y
	var d := 160.0 * o
	for l: Label in [hp_lbl, mana_lbl]:
		l.add_theme_font_size_override("font_size", 19)
	for pair in [[hp_orb, hp_lbl, 6.0], [mana_orb, mana_lbl, w - d - 6.0]]:
		pair[0].scale = Vector2(o, o)
		pair[0].position = Vector2(pair[2], h - d - XP_PHONE - 4.0)
		pair[1].position = pair[0].position + Vector2(d / 2.0 - 70.0, d / 2.0 - 15.0)
	xp_bar.position = Vector2(0, h - XP_PHONE)
	xp_bar.size = Vector2(w, XP_PHONE)
	xp_back.position = xp_bar.position
	xp_back.size = xp_bar.size
	xp_lbl.visible = false
	lvl_btn.position = Vector2(d + 12.0, h - XP_PHONE - 52.0)
	tracker.position = Vector2(8, 8)


func phone() -> bool:
	return not _home.is_empty()


func bar_h() -> float:
	if phone():
		return XP_PHONE
	return 0.0 if not bar.visible else BAR_H * bar.scale.y


func mouse_over_ui() -> bool:
	return over_ui_at(root.get_global_mouse_position())


func over_ui_at(mp: Vector2) -> bool:
	if not visible:
		return false
	if bar.visible and (bar.get_global_transform() * Rect2(0, 30, 1920, BAR_H - 30)).has_point(mp):
		return true
	for c in [hp_orb, mana_orb, lvl_btn]:
		if c.is_visible_in_tree() and (c.get_global_transform() * Rect2(Vector2.ZERO, c.size)).has_point(mp):
			return true
	return tracker.over_controls(mp)


func _unhandled_input(event: InputEvent) -> void:
	if not visible or Game.player == null:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		for a in ["inventory", "character", "skills", "quests", "kronika", "automap"]:
			if event.is_action(a):
				toggle(a)
				get_viewport().set_input_as_handled()
				return
		if (event as InputEventKey).keycode == KEY_H:
			toggle("hireling")
			get_viewport().set_input_as_handled()
			return
		if event.is_action("pause"):
			if Game.main.ui.any_open():
				Game.main.ui.close_all()
			else:
				Game.main.ui.show_pause()
			get_viewport().set_input_as_handled()


func _process(delta: float) -> void:
	if not visible:
		return
	var ch := Game.ch
	var d: Dictionary = ch.d
	if d.is_empty():
		return
	hp_orb.value = 1000.0 * ch.hp / maxf(1.0, d.hp_max)
	mana_orb.value = 1000.0 * ch.mana / maxf(1.0, d.mana_max)
	hp_lbl.text = "%d / %d" % [int(ch.hp), int(d.hp_max)]
	mana_lbl.text = "%d / %d" % [int(ch.mana), int(d.mana_max)]
	var x0 := CharData.xp_for(ch.level)
	var x1 := CharData.xp_for(ch.level + 1)
	xp_bar.value = 1000.0 * float(ch.xp - x0) / maxf(1.0, x1 - x0)
	xp_bar.tooltip_text = "%s %d · %s %d / %d" % [L.t("level"), ch.level, L.t("xp"), ch.xp, x1]
	xp_lbl.text = "%s %d  ·  %d %%" % [L.t("level"), ch.level, int(xp_bar.value / 10.0)]
	_update_hurt(delta, ch.hp / maxf(1.0, d.hp_max))
	lvl_btn.visible = ch.stat_points > 0 or ch.skill_points > 0
	if lvl_btn.visible:
		lvl_btn.modulate.a = 0.6 + 0.4 * sin(Time.get_ticks_msec() / 200.0)
	for s in belt_slots:
		s.visible = s.index < ch.belt_size()
		s.queue_redraw()
	for s in skill_slots:
		s.queue_redraw()
	var info: Dictionary = Game.level.hover_info() if Game.level else {}
	target_box.visible = not info.is_empty() and not (info.get("kind", "") == "boss" and boss_box.visible)
	if target_box.visible:
		target_name.text = info.name
		target_name.add_theme_color_override("font_color", info.color)
		target_sub.text = info.get("sub", "")
		target_sub.visible = target_sub.text != ""
		target_hp.visible = info.has("hp")
		if info.has("hp"):
			target_hp.value = info.hp
	if say_t > 0.0:
		say_t -= delta
		if say_t <= 0.0:
			create_tween().tween_property(say_box, "modulate:a", 0.0, 0.5)


# Red edges: a flash on a heavy blow, and a slow pulse while life is low.
func _update_hurt(delta: float, ratio: float) -> void:
	var hp := Game.ch.hp
	if last_hp >= 0.0 and hp < last_hp:
		hurt_flash = maxf(hurt_flash, clampf((last_hp - hp) / maxf(1.0, Game.ch.d.hp_max) * 4.0, 0.0, 0.8))
	last_hp = hp
	hurt_flash = maxf(0.0, hurt_flash - delta * 1.8)
	var low := 0.0
	if ratio < 0.35 and hp > 0.0:
		low = (1.0 - ratio / 0.35) * (0.45 + 0.25 * sin(Time.get_ticks_msec() / 160.0))
		hp_orb.modulate = Color(1.0 + low * 0.6, 1.0, 1.0)
	else:
		hp_orb.modulate = Color.WHITE
	hurt.modulate.a = maxf(hurt_flash, low)


func skill_for_slot(i: int) -> String:
	return Game.ch.rmb if i == 0 else Game.ch.hotkeys[i - 1]
