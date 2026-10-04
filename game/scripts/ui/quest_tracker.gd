class_name QuestTracker
extends VBoxContainer

# Under the minimap: the act and its seals, then the main quest's next step and where it is, then the
# side quests in hand. Rebuilt only when what it would say changes.

const W := 400.0

var font: Font
var _sig := ""


func _ready() -> void:
	font = load("res://assets/fonts/TataHand.ttf")
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_theme_constant_override("separation", 2)
	custom_minimum_size = Vector2(W, 0)
	var t := Timer.new()
	t.wait_time = 0.5
	t.autostart = true
	t.timeout.connect(refresh)
	add_child(t)
	refresh()


func refresh() -> void:
	var tq := Game.tracked_quests()
	var sig := str(tq) + str(Game.flags.size()) + str(Game.act) + str(Game.seal_count()) + L.lang
	if sig == _sig:
		return
	_sig = sig
	for c in get_children():
		if c is Label:
			c.queue_free()
	var ad := DB.act(Game.act)
	_line("%s %s · %s" % [L.t("act"), UiQuests._roman(Game.act), L.t(ad.get("name", ""))], 26, UiTheme.GOLD)
	_line(L.t({"cs": "Pečeti zlomeny: %d / 4", "en": "Seals broken: %d / 4"}) % Game.seal_count(), 18, Color("bcd4ea"))
	if tq.filter(func(q): return q.main).is_empty():
		for nid in ad.get("town", {}).get("npcs", []):
			if Game.npc_marker(str(nid)) == "new":
				_line(" ", 8, Color.TRANSPARENT)
				var who := L.t(DB.npcs.get(nid, {}).get("name", nid))
				_line("◆ " + L.t({"cs": "Promluv si: %s", "en": "Talk to %s"}) % who, 24, Color("f0d8a8"))
				_line("⌖ " + L.t(ad.get("town", {}).get("name", "")), 16, UiTheme.FAINT, true)
				break
	var sides := 0
	for q in tq:
		if not q.main and sides >= 3:
			continue
		_line(" ", 8, Color.TRANSPARENT)
		_line(("◆ " if q.main else "◇ ") + q.name, 24 if q.main else 21, Color("f0d8a8") if q.main else Color("d6d8dc"))
		var text: String = q.text
		if q.n >= 0:
			text += "  (%d / %d)" % [q.n, q.count]
		_line(text, 19 if q.main else 17, UiTheme.INK if q.main else UiTheme.DIM, true)
		if q.where != "":
			_line("⌖ " + q.where, 16, UiTheme.FAINT, true)
		if not q.main:
			sides += 1


func _line(text: String, sz: int, col: Color, wrap := false) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", sz)
	l.add_theme_color_override("font_color", col)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.95))
	l.add_theme_constant_override("outline_size", 5)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	if wrap:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(W, 0)
	add_child(l)
