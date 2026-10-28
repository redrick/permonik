class_name UiQuests
extends UiPanel

var list: VBoxContainer
var _sig := ""


func _ready() -> void:
	custom_minimum_size = Vector2(640, 0)
	set_title(L.t("quests"))
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(556, 520 if UiRoot.inst.compact() else 700)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	body.add_child(sc)
	list = VBoxContainer.new()
	list.add_theme_constant_override("separation", 4)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sc.add_child(list)
	refresh()


func refresh() -> void:
	var sig := str(Game.quests) + L.lang
	if sig == _sig:
		return
	_sig = sig
	for c in list.get_children():
		c.queue_free()
	var any := false
	for a in DB.acts:
		var an := int(a.get("id", 0))
		var active := []
		var done := []
		for qid in DB.quests:
			var q: Dictionary = DB.quests[qid]
			if int(q.get("act", 0)) != an:
				continue
			match Game.quest_state(qid):
				"active":
					active.append(qid)
				"done":
					done.append(qid)
		if active.is_empty() and done.is_empty():
			continue
		any = true
		var h := UiTheme.label("%s %s · %s" % [L.t("act"), _roman(an), L.t(a.get("name", ""))], 28, UiTheme.GOLD)
		list.add_child(h)
		list.add_child(UiTheme.rule(540))
		if a.has("goal"):
			list.add_child(UiTheme.wrap_label(L.t(a.goal), 20, Color("e0c890"), 540))
			list.add_child(UiTheme.sep(6))
		active.sort_custom(func(x, y): return bool(DB.quests[x].get("main", false)) and not bool(DB.quests[y].get("main", false)))
		for qid in active:
			_quest(qid, true)
		for qid in done:
			_quest(qid, false)
		list.add_child(UiTheme.sep(10))
	if not any:
		var l := UiTheme.wrap_label(UiTheme.t("no_quests"), 24, UiTheme.DIM, 540, false)
		list.add_child(l)


func _quest(qid: String, active: bool) -> void:
	var q: Dictionary = DB.quests[qid]
	var nm := L.t(q.get("name", qid))
	if bool(q.get("main", false)):
		nm += "  ·  " + UiTheme.t("main_quest")
	if not active:
		nm += "  ·  " + UiTheme.t("done")
	var t := UiTheme.label(nm, 25, UiTheme.INK if active else UiTheme.FAINT)
	list.add_child(t)
	if not active:
		return
	var step := Game.quest_step(qid)
	for s in q.get("steps", []):
		if s.get("id", "") == step:
			list.add_child(UiTheme.wrap_label("» " + L.t(s.get("text", "")), 21, Color("f0d8a8"), 520))
			var where := Game.place_text(Game.goal_place(qid))
			if where != "":
				list.add_child(UiTheme.wrap_label("⌖ " + where, 18, UiTheme.FAINT, 520))
	list.add_child(UiTheme.wrap_label(L.t(q.get("desc", "")), 19, UiTheme.DIM, 520))
	list.add_child(UiTheme.sep(6))


static func _roman(n: int) -> String:
	return ["", "I", "II", "III", "IV", "V", "VI"][clampi(n, 0, 6)]
