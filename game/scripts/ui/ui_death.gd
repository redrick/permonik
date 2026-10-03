class_name UiDeath
extends Control


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	modulate.a = 0.0
	UiScreens.dim(self, 0.6)
	UiScreens.vignette(self, Color(0.32, 0.0, 0.0, 0.95), 0.25)
	var vb := UiScreens.center_box(self)
	var t := UiTheme.label(L.t("you_died"), 96, Color("c83a2a"))
	t.add_theme_constant_override("outline_size", 12)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vb.add_child(t)
	var lost := int(Game.ch.gold * 0.1)
	if lost > 0:
		var s := UiTheme.label("−%d %s" % [lost, L.t("gold")], 28, UiTheme.DIM)
		s.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		vb.add_child(s)
	vb.add_child(UiTheme.sep(30))
	var go := func():
		UiRoot.inst.close_all()
		Game.main.respawn()
	var b := UiTheme.button(L.t("respawn"), go, 360)
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(b)
	create_tween().tween_property(self, "modulate:a", 1.0, 1.2)


func on_escape() -> void:
	pass
