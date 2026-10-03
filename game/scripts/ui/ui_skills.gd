class_name UiSkills
extends UiPanel

var hover_id := ""
var pts_lbl: Label
var nodes: Array = []


func _ready() -> void:
	custom_minimum_size = Vector2(640, 0)
	set_title(L.t("skills"))
	pts_lbl = UiTheme.label("", 24, UiTheme.GOLD)
	pts_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(pts_lbl)
	var cols := HBoxContainer.new()
	cols.add_theme_constant_override("separation", 6)
	cols.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	body.add_child(cols)
	for tree in Game.ch.cls().get("trees", []):
		var col := VBoxContainer.new()
		col.custom_minimum_size = Vector2(182, 0)
		col.add_theme_constant_override("separation", 2)
		cols.add_child(col)
		var h := UiTheme.label(L.t(tree.get("name", tree.get("id", ""))), 27, UiTheme.GOLD)
		h.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		col.add_child(h)
		col.add_child(UiTheme.rule(170))
		var ids: Array = tree.get("skills", [])
		for i in ids.size():
			var n := SkillNode.new()
			n.id = str(ids[i])
			n.panel = self
			n.chained = i > 0
			col.add_child(n)
			nodes.append(n)
	body.add_child(UiTheme.sep(4))
	body.add_child(UiTheme.rule(556))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	body.add_child(row)
	var atk := SkillNode.new()
	atk.id = "utok"
	atk.panel = self
	atk.compact = true
	row.add_child(atk)
	nodes.append(atk)
	var hint := UiTheme.wrap_label(L.t("rmb_hint"), 19, UiTheme.FAINT, 460)
	hint.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(hint)
	refresh()


func refresh() -> void:
	var sp := Game.ch.skill_points
	pts_lbl.text = UiTheme.t("skill_points_n", {"v": sp})
	pts_lbl.modulate.a = 1.0 if sp > 0 else 0.45
	for n in nodes:
		n.refresh()


func bind_hover(i: int) -> bool:
	if hover_id == "" or not _bindable(hover_id):
		return false
	Game.ch.hotkeys[i] = hover_id
	Game.ch.changed.emit()
	Sfx.play("ui_click", 0.6, 0.0)
	return true


func bind_rmb(id: String) -> void:
	if not _bindable(id):
		return
	Game.ch.rmb = id
	Game.ch.changed.emit()
	Sfx.play("ui_click", 0.6, 0.0)


static func _bindable(id: String) -> bool:
	if id == "utok":
		return true
	return Game.ch.skill_rank(id) > 0 and DB.skill(id).get("type", "") != "passive"


static func fill_desc(id: String, rank: int) -> String:
	var s := DB.skill(id)
	var txt := L.t(s.get("desc", ""))
	for p in s.get("params", {}):
		var key := "{" + str(p) + "}"
		if txt.contains(key):
			txt = txt.replace(key, UiTheme.fmt_num(Game.ch.skill_param(id, p, rank)))
	return txt


static func skill_tip(id: String) -> Array:
	var ch := Game.ch
	var s := DB.skill(id)
	var lines := []
	lines.append([L.t(s.get("name", id)), UiTheme.GOLD])
	var base := int(ch.skills.get(id, 0))
	var rank := ch.skill_rank(id)
	var mx := int(s.get("max_rank", 20))
	if id != "utok":
		var rt := "%s %d / %d" % [L.t("rank"), base, mx]
		if rank > base:
			rt += "  (+%d)" % (rank - base)
		lines.append([rt, UiTheme.INK if base > 0 else UiTheme.DIM])
	lines.append([fill_desc(id, maxi(1, rank)), UiTheme.INK])
	if s.get("type", "") == "passive":
		lines.append([L.t("passive"), UiTheme.BLUE])
	else:
		var m := ch.skill_mana(id)
		if m > 0:
			lines.append([UiTheme.t("mana_cost", {"v": UiTheme.fmt_num(m)}), UiTheme.BLUE])
		var cd := float(s.get("cooldown", 0))
		if cd > 0:
			lines.append([UiTheme.t("cooldown", {"v": UiTheme.fmt_num(cd)}), UiTheme.DIM])
	if id != "utok" and base > 0 and base < mx:
		lines.append([L.t("next_rank") + ":", UiTheme.FAINT])
		lines.append([fill_desc(id, rank + 1), UiTheme.DIM])
	var rl := ch.skill_req_level(id)
	if ch.level < rl:
		lines.append([UiTheme.t("req_skill_level", {"v": rl}), UiTheme.RED])
	var syn: Dictionary = s.get("synergy", {})
	if not syn.is_empty():
		var names := []
		for k in syn:
			names.append("%s +%d %%" % [L.t(DB.skill(k).get("name", k)), int(syn[k])])
		lines.append([", ".join(names), Color("9a8fc0")])
	return lines


class SkillNode extends Control:
	var id := ""
	var panel: UiSkills
	var chained := false
	var compact := false
	var plus: Button
	var name_lbl: Label
	var rank_lbl: Label
	var icon_rect := Rect2(59, 14, 64, 64)

	func _ready() -> void:
		mouse_filter = Control.MOUSE_FILTER_STOP
		UiRoot.inst.reg_tip(self)
		mouse_entered.connect(func(): panel.hover_id = id)
		mouse_exited.connect(func():
			if panel.hover_id == id:
				panel.hover_id = "")
		if compact:
			custom_minimum_size = Vector2(76, 76)
			icon_rect = Rect2(6, 6, 64, 64)
			return
		custom_minimum_size = Vector2(182, 154)
		name_lbl = UiTheme.label(L.t(DB.skill(id).get("name", id)), 19, UiTheme.INK, true)
		name_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		name_lbl.position = Vector2(0, 80)
		name_lbl.size = Vector2(182, 26)
		name_lbl.clip_text = true
		add_child(name_lbl)
		rank_lbl = UiTheme.label("", 22, UiTheme.DIM)
		rank_lbl.position = Vector2(30, 108)
		rank_lbl.size = Vector2(80, 30)
		rank_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		add_child(rank_lbl)
		plus = UiTheme.small_button("+", func(): Game.ch.learn(id), 36)
		plus.position = Vector2(118, 106)
		add_child(plus)

	func refresh() -> void:
		queue_redraw()
		if compact:
			return
		var ch := Game.ch
		var base := int(ch.skills.get(id, 0))
		rank_lbl.text = "%d/%d" % [base, int(DB.skill(id).get("max_rank", 20))]
		rank_lbl.add_theme_color_override("font_color", UiTheme.INK if base > 0 else UiTheme.FAINT)
		plus.visible = ch.can_learn(id)
		name_lbl.add_theme_color_override("font_color", UiTheme.INK if ch.level >= ch.skill_req_level(id) else UiTheme.FAINT)

	func _draw() -> void:
		var ch := Game.ch
		if chained:
			draw_line(Vector2(91, -10), Vector2(91, icon_rect.position.y), Color(UiTheme.BRONZE, 0.7), 3.0)
		var learned := id == "utok" or int(ch.skills.get(id, 0)) > 0
		var locked := ch.level < ch.skill_req_level(id)
		var t := DB.tex("ui/skills/" + id)
		var r := icon_rect
		draw_rect(r.grow(3), Color(0, 0, 0, 0.8))
		if t:
			draw_texture_rect(t, r, false, Color(1, 1, 1, 1) if learned else (Color(0.35, 0.33, 0.3) if locked else Color(0.6, 0.58, 0.55)))
		else:
			draw_rect(r, Color(0.2, 0.15, 0.12))
		var hov := Rect2(Vector2.ZERO, size).has_point(get_local_mouse_position())
		draw_rect(r.grow(3), UiTheme.GOLD if hov else (UiTheme.BRONZE if learned else Color(0.25, 0.2, 0.15)), false, 2.0)
		var tags := []
		if ch.rmb == id:
			tags.append("RMB")
		var keys := ["Q", "W", "E", "R"]
		for i in 4:
			if ch.hotkeys[i] == id:
				tags.append(keys[i])
		if not tags.is_empty():
			var s := " ".join(tags)
			draw_string_outline(UiTheme.small, r.position + Vector2(3, 17), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, 4, Color.BLACK)
			draw_string(UiTheme.small, r.position + Vector2(3, 17), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, UiTheme.GOLD)
		if locked and not learned:
			var lv := str(ch.skill_req_level(id))
			draw_string_outline(UiTheme.font, r.position + Vector2(r.size.x - 30, r.size.y - 6), lv, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, 4, Color.BLACK)
			draw_string(UiTheme.font, r.position + Vector2(r.size.x - 30, r.size.y - 6), lv, HORIZONTAL_ALIGNMENT_LEFT, -1, 22, UiTheme.RED)

	func _process(_d: float) -> void:
		queue_redraw()

	func _gui_input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed:
			if event.button_index == MOUSE_BUTTON_RIGHT:
				panel.bind_rmb(id)
				accept_event()
			elif event.button_index == MOUSE_BUTTON_LEFT and event.double_click and Game.ch.can_learn(id):
				Game.ch.learn(id)
				accept_event()

	func tip() -> Dictionary:
		var lines := UiSkills.skill_tip(id)
		if UiSkills._bindable(id):
			lines.append([L.t("rmb_hint"), UiTheme.FAINT])
		return {"lines": lines}
