class_name UiScreens
extends RefCounted


static func dim(parent: Control, a := 0.6) -> ColorRect:
	var c := ColorRect.new()
	c.color = Color(0, 0, 0, a)
	c.set_anchors_preset(Control.PRESET_FULL_RECT)
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(c)
	return c


static func vignette(parent: Control, edge: Color, inner := 0.35) -> TextureRect:
	var g := Gradient.new()
	g.set_color(0, Color(edge, 0.0))
	g.set_color(1, edge)
	g.add_point(inner, Color(edge, 0.0))
	var gt := GradientTexture2D.new()
	gt.gradient = g
	gt.fill = GradientTexture2D.FILL_RADIAL
	gt.fill_from = Vector2(0.5, 0.5)
	gt.fill_to = Vector2(1.0, 1.0)
	gt.width = 256
	gt.height = 256
	var t := TextureRect.new()
	t.texture = gt
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	t.set_anchors_preset(Control.PRESET_FULL_RECT)
	t.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(t)
	return t


# Phones: Back and the title stay pinned at the top, the settings scroll under them.
static func options_page(parent: Control, title: String, back: Callable, rebuild: Callable) -> void:
	var m := MarginContainer.new()
	m.set_anchors_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		m.add_theme_constant_override("margin_" + side, 14)
	m.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(m)
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 8)
	m.add_child(vb)
	var head := HBoxContainer.new()
	head.add_theme_constant_override("separation", 16)
	vb.add_child(head)
	head.add_child(UiTheme.button("‹ " + L.t("menu_back"), back, 220, 28))
	var t := UiTheme.title(title, 40)
	t.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(t)
	var pad := Control.new()
	pad.custom_minimum_size = Vector2(220, 0)
	head.add_child(pad)
	var sc := ScrollContainer.new()
	sc.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	vb.add_child(sc)
	var cc := CenterContainer.new()
	cc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(cc)
	var p := UiPanel.new()
	p.body.add_child(options(rebuild))
	cc.add_child(p)


static func center_box(parent: Control) -> VBoxContainer:
	var cc := CenterContainer.new()
	cc.set_anchors_preset(Control.PRESET_FULL_RECT)
	cc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(cc)
	var vb := VBoxContainer.new()
	vb.alignment = BoxContainer.ALIGNMENT_CENTER
	vb.add_theme_constant_override("separation", 12)
	cc.add_child(vb)
	return vb


static func options(rebuild: Callable) -> VBoxContainer:
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 14)
	vb.custom_minimum_size = Vector2(560, 0)
	var lr := HBoxContainer.new()
	lr.add_theme_constant_override("separation", 10)
	vb.add_child(lr)
	var ll := UiTheme.label(L.t("menu_language"), 28)
	ll.custom_minimum_size = Vector2(200, 0)
	lr.add_child(ll)
	for pair in [["cs", "Čeština"], ["en", "English"]]:
		var code: String = pair[0]
		var pick := func():
			if L.lang != code:
				L.set_lang(code)
				rebuild.call()
		var b := UiTheme.button(pair[1], pick, 170, 24)
		if L.lang == code:
			b.add_theme_color_override("font_color", UiTheme.GOLD)
		lr.add_child(b)
	vb.add_child(_slider(UiTheme.t("menu_master"), Sfx.volume, func(v: float):
		Sfx.volume = v
		Sfx.save_settings()
		Sfx.play("ui_click", 1.0, 0.0)))
	vb.add_child(_slider(UiTheme.t("menu_music"), Sfx.music_volume, func(v: float):
		Sfx.music_volume = v
		Sfx.save_settings()))
	vb.add_child(_slider(L.t({"cs": "Hlasy", "en": "Voices"}), Sfx.voice_volume, func(v: float):
		Sfx.voice_volume = v
		Sfx.save_settings()))
	var vr := HBoxContainer.new()
	vr.add_theme_constant_override("separation", 8)
	vb.add_child(vr)
	var vl := UiTheme.label(L.t({"cs": "Mluví", "en": "Spoken in"}), 28)
	vl.custom_minimum_size = Vector2(200, 0)
	vr.add_child(vl)
	for pair in [["", {"cs": "Jako text", "en": "As text"}], ["cs", "Čeština"], ["en", "English"], ["off", {"cs": "Vypnuto", "en": "Off"}]]:
		var code: String = pair[0]
		var vb2 := UiTheme.button(L.t(pair[1]) if pair[1] is Dictionary else str(pair[1]), func():
			Sfx.voice_lang = code
			Sfx.save_settings()
			rebuild.call(), 150, 22)
		if Sfx.voice_lang == code:
			vb2.add_theme_color_override("font_color", UiTheme.GOLD)
		vr.add_child(vb2)
	var sr := HBoxContainer.new()
	sr.add_theme_constant_override("separation", 8)
	vb.add_child(sr)
	var sl := UiTheme.label(UiTheme.t("menu_ui_scale"), 28)
	sl.custom_minimum_size = Vector2(200, 0)
	sr.add_child(sl)
	var cfg0 := ConfigFile.new()
	cfg0.load("user://settings.cfg")
	var cur := float(cfg0.get_value("main", "ui_scale", 0.0))
	for v in Main.UI_SCALES:
		var val: float = v
		var pick := func():
			var cfg := ConfigFile.new()
			cfg.load("user://settings.cfg")
			cfg.set_value("main", "ui_scale", val)
			cfg.save("user://settings.cfg")
			Game.main.apply_ui_scale()
			rebuild.call()
		var b := UiTheme.button(UiTheme.t("menu_ui_auto") if val == 0.0 else "%d %%" % roundi(val * 100), pick, 96, 22)
		if is_equal_approx(val, cur):
			b.add_theme_color_override("font_color", UiTheme.GOLD)
		sr.add_child(b)
	var fr := HBoxContainer.new()
	fr.add_theme_constant_override("separation", 8)
	vb.add_child(fr)
	var fl := UiTheme.label(L.t({"cs": "Filtr kořisti", "en": "Loot filter"}), 28)
	fl.custom_minimum_size = Vector2(200, 0)
	fr.add_child(fl)
	var opts := [{"cs": "Vše", "en": "All"}, {"cs": "Bez obyčejných", "en": "No plain"}, {"cs": "Bez obyč. a modrých", "en": "No plain, no blue"}]
	for i in opts.size():
		var lvl := i
		var fb := UiTheme.button(L.t(opts[i]), func():
			GroundItem.set_filter(lvl)
			rebuild.call(), 200 if i < 2 else 260, 22)
		if GroundItem.get_filter() == i:
			fb.add_theme_color_override("font_color", UiTheme.GOLD)
		fr.add_child(fb)
	if TouchPad.wanted():
		var hr := HBoxContainer.new()
		hr.add_theme_constant_override("separation", 8)
		vb.add_child(hr)
		var hl := UiTheme.label(L.t({"cs": "Vibrace", "en": "Vibration"}), 28)
		hl.custom_minimum_size = Vector2(200, 0)
		hr.add_child(hl)
		for on in [true, false]:
			var val: bool = on
			var hb := UiTheme.button(L.t({"cs": "Zapnuto", "en": "On"} if on else {"cs": "Vypnuto", "en": "Off"}), func():
				TouchPad.buzz = val
				var cfg := ConfigFile.new()
				cfg.load("user://settings.cfg")
				cfg.set_value("main", "vibrate", val)
				cfg.save("user://settings.cfg")
				if val:
					Input.vibrate_handheld(30)
				rebuild.call(), 170, 22)
			if TouchPad.buzz == val:
				hb.add_theme_color_override("font_color", UiTheme.GOLD)
			hr.add_child(hb)
	if not OS.has_feature("web"):
		vb.add_child(_save_dir_row(rebuild))
	if OS.has_feature("mobile"):
		return vb
	var fs := CheckBox.new()
	fs.text = UiTheme.t("menu_fullscreen")
	fs.focus_mode = Control.FOCUS_NONE
	fs.add_theme_font_size_override("font_size", 28)
	fs.button_pressed = DisplayServer.window_get_mode() in [DisplayServer.WINDOW_MODE_FULLSCREEN, DisplayServer.WINDOW_MODE_EXCLUSIVE_FULLSCREEN]
	fs.toggled.connect(func(on: bool):
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if on else DisplayServer.WINDOW_MODE_WINDOWED)
		var cfg := ConfigFile.new()
		cfg.load("user://settings.cfg")
		cfg.set_value("main", "fullscreen", on)
		cfg.save("user://settings.cfg"))
	vb.add_child(fs)
	return vb


static func _save_dir_row(rebuild: Callable) -> VBoxContainer:
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 8)
	box.add_child(hb)
	var l := UiTheme.label(UiTheme.t("menu_save_dir"), 28)
	l.custom_minimum_size = Vector2(200, 0)
	hb.add_child(l)
	var status := UiTheme.label(_dir_text(Game.save_dir), 20, UiTheme.DIM, true)
	status.custom_minimum_size = Vector2(560, 0)
	status.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	var move := func(dir: String):
		var n := Game.set_save_dir(dir)
		if n < 0:
			status.text = UiTheme.t("save_dir_failed", {"v": dir})
			status.add_theme_color_override("font_color", UiTheme.RED)
			return
		rebuild.call()
	hb.add_child(UiTheme.button(UiTheme.t("save_dir_pick"), func():
		if Game.needs_storage_permission("/storage"):
			OS.request_permission(Game.STORAGE_PERMISSION)
			status.text = UiTheme.t("save_dir_permission")
			status.add_theme_color_override("font_color", UiTheme.GOLD)
			return
		_pick_dir(move), 200, 22))
	if Game.save_dir != Game.DEFAULT_SAVE_DIR:
		hb.add_child(UiTheme.button(UiTheme.t("menu_ui_default"), func(): move.call(Game.DEFAULT_SAVE_DIR), 140, 22))
	box.add_child(status)
	return box


static func _dir_text(dir: String) -> String:
	return UiTheme.t("save_dir_default") if dir == Game.DEFAULT_SAVE_DIR else dir


# Desktop gets the system folder picker; touch builds browse shared storage in the game (UiFolderPicker).
static func _pick_dir(on_pick: Callable) -> void:
	if OS.has_feature("android") or TouchPad.active:
		var start: String = Game.save_dir if Game.save_dir != Game.DEFAULT_SAVE_DIR else UiFolderPicker.ROOT
		if not OS.has_feature("android") and start == UiFolderPicker.ROOT:
			start = OS.get_system_dir(OS.SYSTEM_DIR_DOCUMENTS)
		UiFolderPicker.open(start, on_pick)
		return
	var fd := FileDialog.new()
	fd.file_mode = FileDialog.FILE_MODE_OPEN_DIR
	fd.access = FileDialog.ACCESS_FILESYSTEM
	fd.title = UiTheme.t("save_dir_pick")
	fd.process_mode = Node.PROCESS_MODE_ALWAYS
	fd.use_native_dialog = true
	fd.current_dir = Game.save_dir if Game.save_dir != Game.DEFAULT_SAVE_DIR else OS.get_system_dir(OS.SYSTEM_DIR_DOCUMENTS)
	fd.dir_selected.connect(func(dir: String):
		fd.queue_free()
		on_pick.call(dir))
	fd.canceled.connect(fd.queue_free)
	Game.main.add_child(fd)
	fd.popup_centered_ratio(0.85)

static func _slider(text: String, v: float, cb: Callable) -> HBoxContainer:
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 10)
	var l := UiTheme.label(text, 28)
	l.custom_minimum_size = Vector2(200, 0)
	hb.add_child(l)
	var s := HSlider.new()
	s.min_value = 0.0
	s.max_value = 1.0
	s.step = 0.05
	s.value = v
	s.custom_minimum_size = Vector2(300, 32)
	s.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	s.focus_mode = Control.FOCUS_NONE
	hb.add_child(s)
	var pct := UiTheme.label("%d %%" % int(v * 100), 24, UiTheme.DIM)
	pct.custom_minimum_size = Vector2(70, 0)
	hb.add_child(pct)
	s.value_changed.connect(func(nv: float):
		pct.text = "%d %%" % int(nv * 100)
		cb.call(nv))
	return hb
