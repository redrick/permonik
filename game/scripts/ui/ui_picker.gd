class_name UiPicker
extends PanelContainer

var slot := 0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_theme_stylebox_override("panel", UiTheme.flat(Color(0.05, 0.04, 0.035, 0.96), UiTheme.BRONZE, 2, 10))
	var vb := VBoxContainer.new()
	add_child(vb)
	var key: String = ["RMB", "Q", "W", "E", "R"][slot]
	vb.add_child(UiTheme.label("%s · %s" % [UiTheme.t("pick_skill"), key], 20, UiTheme.GOLD, true))
	var ids := ["utok"]
	for t in Game.ch.cls().get("trees", []):
		for id in t.get("skills", []):
			if Game.ch.skill_rank(id) > 0 and DB.skill(id).get("type", "") != "passive":
				ids.append(id)
	var g := GridContainer.new()
	g.columns = mini(ids.size(), 6)
	g.add_theme_constant_override("h_separation", 4)
	g.add_theme_constant_override("v_separation", 4)
	vb.add_child(g)
	var cur := Game.ch.rmb if slot == 0 else str(Game.ch.hotkeys[slot - 1])
	for id in ids:
		var b := Pick.new()
		b.id = id
		b.current = id == cur
		b.picker = self
		g.add_child(b)
	if slot > 0:
		vb.add_child(UiTheme.small_button("×", func(): choose(""), 64))


func choose(id: String) -> void:
	if slot == 0:
		if id == "":
			return
		Game.ch.rmb = id
	else:
		Game.ch.hotkeys[slot - 1] = id
	Game.ch.changed.emit()
	Sfx.play("ui_click", 0.6, 0.0)
	UiRoot.inst.close_panel(self)


class Pick extends Control:
	var id := ""
	var current := false
	var picker: UiPicker

	func _ready() -> void:
		custom_minimum_size = Vector2(64, 64)
		mouse_filter = Control.MOUSE_FILTER_STOP
		UiRoot.inst.reg_tip(self)

	func _process(_d: float) -> void:
		queue_redraw()

	func _draw() -> void:
		var r := Rect2(Vector2.ZERO, size)
		var t := DB.tex("ui/skills/" + id)
		if t:
			draw_texture_rect(t, r, false)
		else:
			draw_rect(r, Color(0.2, 0.15, 0.12))
			draw_string(UiTheme.small, Vector2(4, 38), L.t(DB.skill(id).get("name", id)).left(7), HORIZONTAL_ALIGNMENT_LEFT, -1, 16)
		var hov := r.has_point(get_local_mouse_position())
		if hov or current:
			draw_rect(r, UiTheme.GOLD if hov else UiTheme.BRONZE, false, 3.0)

	func _gui_input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
			accept_event()
			picker.choose(id)

	func tip() -> Dictionary:
		return {"lines": UiSkills.skill_tip(id)}
