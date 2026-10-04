class_name UiKronika
extends UiPanel

const TABS := ["story", "book", "creature", "place", "person", "god", "item", "term"]

var tab := "story"
var tab_row: HBoxContainer
var list: VBoxContainer
var count_lbl: Label
var title_lbl: Label
var page: VBoxContainer
var text_scroll: ScrollContainer
var current := ""


func _ready() -> void:
	custom_minimum_size = Vector2(960, 0)
	set_title(UiTheme.t("kronika"))
	tab_row = HBoxContainer.new()
	tab_row.add_theme_constant_override("separation", 4)
	body.add_child(tab_row)
	body.add_child(UiTheme.sep(4))
	var hb := HBoxContainer.new()
	hb.add_theme_constant_override("separation", 18)
	body.add_child(hb)
	var lv := VBoxContainer.new()
	hb.add_child(lv)
	count_lbl = UiTheme.label("", 18, UiTheme.FAINT, true)
	lv.add_child(count_lbl)
	var ls := ScrollContainer.new()
	ls.custom_minimum_size = Vector2(310, 660)
	ls.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	lv.add_child(ls)
	list = VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_theme_constant_override("separation", 0)
	ls.add_child(list)
	var paper := PanelContainer.new()
	paper.add_theme_stylebox_override("panel", UiTheme.flat(Color("2a2118"), Color("4a3a28"), 2, 22))
	paper.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb.add_child(paper)
	var pv := VBoxContainer.new()
	paper.add_child(pv)
	title_lbl = UiTheme.label("", 32, UiTheme.GOLD)
	title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title_lbl.custom_minimum_size = Vector2(520, 0)
	pv.add_child(title_lbl)
	pv.add_child(UiTheme.rule(520))
	text_scroll = ScrollContainer.new()
	text_scroll.custom_minimum_size = Vector2(540, 620)
	text_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	pv.add_child(text_scroll)
	page = VBoxContainer.new()
	page.add_theme_constant_override("separation", 6)
	text_scroll.add_child(page)
	for tt in TABS:
		if _entries(tt).any(_unread):
			tab = tt
			break
	_open_tab(tab)


# ---------------------------------------------------------------- what is visible
# Entry keys: "lore:<id>" for story pages and in-world bestiary lines, "codex:<id>" for encyclopedia entries.
func _story() -> Array:
	var seals := Game.seal_count()
	var kron := []
	var boss := []
	for id in DB.lore:
		var e: Dictionary = DB.lore[id]
		match str(e.get("kind", "")):
			"kronika":
				var n := int(str(id).get_slice("_", 1))
				if n <= seals or Game.cond(str(e.get("unlock", "!always"))):
					kron.append("lore:" + id)
			"boss":
				if Game.flags.get("killed_" + str(e.get("monster", "")), false):
					boss.append("lore:" + id)
	return kron + boss


func _codex_ids(cat: String) -> Array:
	var out := []
	for eid in DB.codex:
		if str(DB.codex[eid].get("cat", "")) == cat:
			out.append(eid)
	out.sort_custom(func(a, b): return _sort_name(a) < _sort_name(b))
	return out


func _sort_name(eid: String) -> String:
	return L.t(DB.codex[eid].get("title", eid)).to_lower()


func _visible(key: String) -> bool:
	if key.begins_with("book:"):
		return Game.known.has(key)
	if key.begins_with("codex:"):
		return Game.codex_visible(key.substr(6))
	return true


func _entries(t: String) -> Array:
	if t == "story":
		return _story()
	if t == "book":
		var bs := []
		for bid in DB.books:
			bs.append("book:" + bid)
		return bs
	var out := []
	for eid in _codex_ids(t):
		out.append("codex:" + eid)
	if t == "creature":
		var covered := {}
		for eid in _codex_ids(t):
			for mid in DB.codex[eid].get("refs", {}).get("monster", []):
				covered[mid] = true
		for id in DB.lore:
			var e: Dictionary = DB.lore[id]
			if str(e.get("kind", "")) == "bestiar" and not covered.has(str(e.get("monster", ""))):
				out.append("lore:" + id)
	return out


func _unread(key: String) -> bool:
	return key.begins_with("codex:") and _visible(key) and not Game.known.has("read:" + key.substr(6))


func _lore_visible(id: String) -> bool:
	var e: Dictionary = DB.lore.get(id, {})
	if str(e.get("kind", "")) != "bestiar":
		return true
	var mid := str(e.get("monster", ""))
	if bool(DB.monster(mid).get("boss", false)):
		return Game.flags.get("killed_" + mid, false)
	return Game.known.has("monster:" + mid)


# ---------------------------------------------------------------- building
func _open_tab(t: String) -> void:
	tab = t
	for c in tab_row.get_children():
		c.queue_free()
	for tt in TABS:
		var any_new := _entries(tt).any(_unread)
		var b := Button.new()
		b.text = ("• " if any_new else "") + UiTheme.t("codex_tab_" + tt)
		b.toggle_mode = true
		b.button_pressed = tt == tab
		b.focus_mode = Control.FOCUS_NONE
		b.add_theme_font_override("font", UiTheme.small)
		b.add_theme_font_size_override("font_size", 20)
		b.custom_minimum_size = Vector2(108, 36)
		if any_new:
			b.add_theme_color_override("font_color", UiTheme.GOLD)
		var tid: String = tt
		b.pressed.connect(func():
			Sfx.play("ui_click", 0.4, 0.0)
			_open_tab(tid))
		tab_row.add_child(b)
	_fill()


func _fill() -> void:
	for c in list.get_children():
		c.queue_free()
	var all := _entries(tab)
	var shown := []
	for k in all:
		if not _visible(k) or (k.begins_with("lore:") and not _lore_visible(k.substr(5))):
			continue
		shown.append(k)
	count_lbl.text = "" if tab == "story" else UiTheme.t("codex_count", {"v": shown.size(), "n": all.size()})
	var first := ""
	for k in shown:
		var b := Button.new()
		b.text = ("• " if _unread(k) else "") + _title(k)
		b.flat = true
		b.focus_mode = Control.FOCUS_NONE
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.add_theme_font_override("font", UiTheme.small)
		b.add_theme_font_size_override("font_size", 20)
		if _unread(k):
			b.add_theme_color_override("font_color", UiTheme.GOLD)
		b.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		b.custom_minimum_size = Vector2(290, 30)
		var key: String = k
		b.pressed.connect(func(): _show(key))
		list.add_child(b)
		if first == "":
			first = k
	if first == "":
		_page(UiTheme.t("codex_tab_" + tab), [[UiTheme.t({"story": "kronika_empty", "book": "book_none"}.get(tab, "codex_empty_tab")), UiTheme.DIM]])
	elif current == "" or not current in shown:
		_show(first)


func _title(key: String) -> String:
	if key.begins_with("book:"):
		return L.t(DB.books.get(key.substr(5), {}).get("title", key))
	if key.begins_with("codex:"):
		return L.t(DB.codex.get(key.substr(6), {}).get("title", key))
	return L.t(DB.lore.get(key.substr(5), {}).get("title", key))


func _show(key: String) -> void:
	current = key
	Sfx.play("ui_click", 0.4, 0.0)
	if key.begins_with("book:"):
		var bk: Dictionary = DB.books.get(key.substr(5), {})
		var first: Array = bk.get("pages", {}).get(L.lang, [""])
		_page(L.t(bk.get("title", key)), [[L.t(bk.get("author", "")), UiTheme.DIM], [str(first[0]) if first.size() > 0 else "", Color("e6d9bc")]])
		var bid := key.substr(5)
		page.add_child(UiTheme.button(UiTheme.t("book_read"), func(): UiRoot.inst.open_book(bid), 220, 22))
		return
	if key.begins_with("lore:"):
		var e: Dictionary = DB.lore.get(key.substr(5), {})
		_page(L.t(e.get("title", key)), [[L.t(e.get("text", "")), Color("e6d9bc")]])
		return
	var eid := key.substr(6)
	var e: Dictionary = DB.codex.get(eid, {})
	var blocks := []
	for mid in e.get("refs", {}).get("monster", []):
		var lid := "bestiar_" + str(mid)
		if DB.lore.has(lid) and _lore_visible(lid):
			blocks.append(["„" + L.t(DB.lore[lid].get("text", "")) + "“", UiTheme.DIM])
	if not blocks.is_empty():
		blocks.append(["#" + UiTheme.t("codex_folklore"), UiTheme.GOLD])
	blocks.append([L.t(e.get("text", "")), Color("e6d9bc")])
	if e.has("game"):
		blocks.append(["#" + UiTheme.t("codex_game"), UiTheme.GOLD])
		blocks.append([L.t(e.game), Color("d6c9a8")])
	var see := []
	for s in e.get("see", []):
		if DB.codex.has(s) and Game.codex_visible(s):
			see.append(s)
	_page(L.t(e.get("title", eid)), blocks, see)
	if not Game.known.has("read:" + eid):
		Game.known["read:" + eid] = true
		_open_tab(tab)


func _page(title: String, blocks: Array, see := []) -> void:
	title_lbl.text = title
	for c in page.get_children():
		c.queue_free()
	for b in blocks:
		var txt: String = b[0]
		if txt.begins_with("#"):
			page.add_child(UiTheme.sep(6))
			page.add_child(UiTheme.label(txt.substr(1), 22, b[1]))
		else:
			page.add_child(UiTheme.wrap_label(txt, 23, b[1], 520))
	if not see.is_empty():
		page.add_child(UiTheme.sep(8))
		page.add_child(UiTheme.label(UiTheme.t("codex_see"), 22, UiTheme.GOLD))
		var flow := HFlowContainer.new()
		flow.custom_minimum_size = Vector2(520, 0)
		page.add_child(flow)
		for s in see:
			var eid: String = s
			var b := Button.new()
			b.text = L.t(DB.codex[eid].get("title", eid))
			b.focus_mode = Control.FOCUS_NONE
			b.add_theme_font_override("font", UiTheme.small)
			b.add_theme_font_size_override("font_size", 19)
			b.pressed.connect(func(): _jump(eid))
			flow.add_child(b)
	text_scroll.scroll_vertical = 0


func _jump(eid: String) -> void:
	var cat := str(DB.codex.get(eid, {}).get("cat", "term"))
	current = "codex:" + eid
	if cat != tab:
		_open_tab(cat)
	_show(current)
