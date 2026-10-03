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
