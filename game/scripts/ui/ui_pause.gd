class_name UiPause
extends Control

var panel: UiPanel
var holder: Control
var in_options := false


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiScreens.dim(self, 0.55)
	UiScreens.vignette(self, Color(0, 0, 0, 0.8), 0.3)
	_build()


func _build() -> void:
	if holder:
		holder.queue_free()
	if in_options and UiRoot.inst.compact():
		holder = Control.new()
		holder.set_anchors_preset(Control.PRESET_FULL_RECT)
		holder.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(holder)
		var shade := ColorRect.new()
		shade.color = Color(0.03, 0.025, 0.022, 0.92)
		shade.set_anchors_preset(Control.PRESET_FULL_RECT)
		shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
		holder.add_child(shade)
		UiScreens.options_page(holder, L.t("menu_options"), on_escape, _build)
		return
	var cc := CenterContainer.new()
	holder = cc
	cc.set_anchors_preset(Control.PRESET_FULL_RECT)
	cc.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(cc)
	panel = UiPanel.new()
	cc.add_child(panel)
	var b := panel.body
	b.add_theme_constant_override("separation", 12)
	if in_options:
		b.add_child(UiTheme.title(L.t("menu_options")))
		b.add_child(UiScreens.options(_build))
		var back := UiTheme.button(L.t("menu_back"), on_escape, 300)
		back.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		b.add_child(back)
		return
	b.add_child(UiTheme.title(UiTheme.t("pause"), 44))
	b.add_child(UiTheme.sep(6))
	for pair in [["resume", _resume], ["menu_options", _options], ["save_quit", _quit]]:
		var btn := UiTheme.button(L.t(pair[0]), pair[1], 380)
		btn.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		b.add_child(btn)
	var info := UiTheme.label("%s · %s %d · %s" % [Game.ch.hero_name, L.t("level"), Game.ch.level, L.t("diff_%d" % Game.difficulty)], 20, UiTheme.FAINT, true)
	info.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	b.add_child(info)


func _resume() -> void:
	UiRoot.inst.close_panel(self)


func _options() -> void:
	in_options = true
	_build()


func _quit() -> void:
	UiRoot.inst.close_all()
	Game.main.save_and_menu()


func on_escape() -> void:
	if in_options:
		in_options = false
		_build()
	else:
		_resume()
