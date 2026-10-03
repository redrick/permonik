class_name UiWaypoints
extends UiPanel


func _ready() -> void:
	custom_minimum_size = Vector2(760, 0)
	set_title(UiTheme.t("waypoints"))
	var hint := UiTheme.label(UiTheme.t("waypoint_hint"), 22, UiTheme.DIM)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(hint)
	var sc := ScrollContainer.new()
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	body.add_child(sc)
	var vb := VBoxContainer.new()
	vb.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vb.add_theme_constant_override("separation", 6)
	sc.add_child(vb)
	var height := 0
	for a in DB.acts:
		var an := int(a.get("id", 0))
		var floors := []
		for k in Game.waypoints:
			var p := str(k).split(":")
			if p.size() == 2 and int(p[0]) == an:
				floors.append(int(p[1]))
		if an > Game.act and floors.is_empty():
			continue
		floors.sort()
		vb.add_child(UiTheme.label("%s %s · %s" % [L.t("act"), UiQuests._roman(an), L.t(a.get("name", ""))], 26, UiTheme.GOLD))
		var flow := HFlowContainer.new()
		flow.add_theme_constant_override("h_separation", 6)
		flow.add_theme_constant_override("v_separation", 6)
		vb.add_child(flow)
		flow.add_child(_btn(an, 0, L.t(a.get("town", {}).get("name", L.t("town")))))
		for f in floors:
			var fd := DB.floor_def(an, f)
			var nm := "%s %d" % [L.t("floor"), f]
			if fd.has("name"):
				nm = L.t(fd.name)
			flow.add_child(_btn(an, f, nm))
		height += 44 + ceili((floors.size() + 1) / 3.0) * 64
	sc.custom_minimum_size = Vector2(676, mini(640, height))


func _btn(a: int, f: int, text: String) -> Button:
	var here := Game.act == a and Game.floor_n == f
	var go := func():
		UiRoot.inst.close_all()
		Sfx.play("waypoint", 0.7)
		Game.goto(a, f, "waypoint")
	var b := UiTheme.button(text, go, 210, 22)
	b.disabled = here
	return b
