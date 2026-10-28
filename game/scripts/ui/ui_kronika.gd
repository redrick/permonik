class_name UiKronika
extends UiPanel

const TABS := ["story", "book", "creature", "place", "person", "god", "item", "term", "grail"]

var tab := "story"
var tab_row: HBoxContainer
var list: VBoxContainer
var count_lbl: Label
var title_lbl: Label
var page: VBoxContainer
var text_scroll: ScrollContainer
var read_btn: Button
var speech := ""
var read_at := 0
var read_parts: Array = []
var reading_voice := false
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
	ls.custom_minimum_size = Vector2(310, 460 if UiRoot.inst.compact() else 660)
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
	var head_row := HBoxContainer.new()
	pv.add_child(head_row)
	title_lbl = UiTheme.label("", 32, UiTheme.GOLD)
	title_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title_lbl.custom_minimum_size = Vector2(470, 0)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head_row.add_child(title_lbl)
	read_btn = UiTheme.small_button("▶", _toggle_read, 44)
	read_btn.tooltip_text = L.t({"cs": "Přečíst nahlas", "en": "Read aloud"})
	read_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	read_btn.visible = _voice() != ""
	head_row.add_child(read_btn)
	pv.add_child(UiTheme.rule(520))
	text_scroll = ScrollContainer.new()
	text_scroll.custom_minimum_size = Vector2(540, 420 if UiRoot.inst.compact() else 620)
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
	if t == "grail":
		var gs := ["grail:u"]
		for sid in DB.sets:
			if DB.class_released(str(DB.sets[sid].get("class", ""))) or Game.known.has("grail:s:" + sid):
				gs.append("grail:s:" + sid)
		gs.append("grail:w")
		return gs
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
		b.custom_minimum_size = Vector2(100, 36)
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
	if tab == "grail":
		var have := 0
		var total := 0
		for k in all:
			var ks := _grail_keys(k)
			total += ks.size()
			have += ks.filter(func(x): return Game.known.has(x)).size()
		count_lbl.text = L.t({"cs": "Nalezeno %d z %d", "en": "Found %d of %d"}) % [have, total]
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
	if key.begins_with("grail:"):
		var ks := _grail_keys(key)
		var nm := ""
		match key.get_slice(":", 1):
			"u":
				nm = L.t({"cs": "Jedinečné věci", "en": "Unique items"})
			"w":
				nm = L.t({"cs": "Slova", "en": "Words"})
			_:
				nm = L.t(DB.sets.get(key.get_slice(":", 2), {}).get("name", key))
		return "%s  %d/%d" % [nm, ks.filter(func(x): return Game.known.has(x)).size(), ks.size()]
	if key.begins_with("book:"):
		return L.t(DB.books.get(key.substr(5), {}).get("title", key))
	if key.begins_with("codex:"):
		return L.t(DB.codex.get(key.substr(6), {}).get("title", key))
	return L.t(DB.lore.get(key.substr(5), {}).get("title", key))


func _show(key: String) -> void:
	current = key
	Sfx.play("ui_click", 0.4, 0.0)
	if key.begins_with("grail:"):
		_show_grail(key)
		return
	if key.begins_with("book:"):
		var bk: Dictionary = DB.books.get(key.substr(5), {})
		var first: Array = bk.get("pages", {}).get(L.lang, [""])
		_page(L.t(bk.get("title", key)), [[L.t(bk.get("author", "")), UiTheme.DIM], [str(first[0]) if first.size() > 0 else "", Color("e6d9bc")]])
		_set_read([UiBook.page_text(bk, 0)])
		var bid := key.substr(5)
		page.add_child(UiTheme.button(UiTheme.t("book_read"), func(): UiRoot.inst.open_book(bid), 220, 22))
		return
	if key.begins_with("lore:"):
		var e: Dictionary = DB.lore.get(key.substr(5), {})
		var mid := str(e.get("monster", ""))
		_page(L.t(e.get("title", key)), [[L.t(e.get("text", "")), Color("e6d9bc")]], [], _pictures({"monster": [mid]} if mid != "" else {}))
		_set_read([e.get("text", {})])
		return
	var eid := key.substr(6)
	var e: Dictionary = DB.codex.get(eid, {})
	var blocks := []
	var parts := []
	for mid in e.get("refs", {}).get("monster", []):
		var lid := "bestiar_" + str(mid)
		if DB.lore.has(lid) and _lore_visible(lid):
			blocks.append(["„" + L.t(DB.lore[lid].get("text", "")) + "“", UiTheme.DIM])
			parts.append(DB.lore[lid].get("text", {}))
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
	_page(L.t(e.get("title", eid)), blocks, see, _pictures(e.get("refs", {})))
	_set_read(parts + [e.get("text", {}), e.get("game", {})])
	if not Game.known.has("read:" + eid):
		Game.known["read:" + eid] = true
		_open_tab(tab)


func _page(title: String, blocks: Array, see := [], pics := {}) -> void:
	title_lbl.text = title
	_stop_read()
	speech = title
	read_parts = []
	read_btn.visible = _voice() != ""
	for c in page.get_children():
		c.queue_free()
	var big: Array = pics.get("big", [])
	if not big.is_empty():
		var row := HBoxContainer.new()
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_theme_constant_override("separation", 10)
		page.add_child(row)
		for t in big:
			var fr := PanelContainer.new()
			fr.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.1, 0.08, 0.06), Color("4a3a28"), 2, 6))
			var tr := TextureRect.new()
			tr.texture = t
			tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
			tr.custom_minimum_size = Vector2(160, 190) if big.size() > 1 else Vector2(240, 220)
			fr.add_child(tr)
			row.add_child(fr)
		page.add_child(UiTheme.sep(4))
	for b in blocks:
		var txt: String = b[0]
		speech += ".\n" + txt.trim_prefix("#")
		if txt.begins_with("#"):
			page.add_child(UiTheme.sep(6))
			page.add_child(UiTheme.label(txt.substr(1), 22, b[1]))
		else:
			page.add_child(UiTheme.wrap_label(txt, 23, b[1], 520))
	var icons: Array = pics.get("icons", [])
	if not icons.is_empty():
		page.add_child(UiTheme.sep(6))
		var irow := HFlowContainer.new()
		irow.custom_minimum_size = Vector2(520, 0)
		irow.add_theme_constant_override("h_separation", 6)
		page.add_child(irow)
		for spec in icons:
			irow.add_child(UiForge.RecipeIcon.make(spec))
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


# ---------------------------------------------------------------- the collection
# The "known" keys a collection page counts (Game.note_found writes them).
func _grail_keys(key: String) -> Array:
	match key.get_slice(":", 1):
		"u":
			return DB.uniques.keys().map(func(u): return "grail:u:" + u)
		"w":
			return DB.words.keys().map(func(w): return "grail:w:" + w)
	return DB.sets.get(key.get_slice(":", 2), {}).get("pieces", []).map(func(p): return "grail:s:" + p)


const WORD_BASE := {"weapon": "krumpac", "armor": "kapuce", "body": "kozeny_kabatec", "shield": "stit"}


func _grail_spec(gk: String) -> Dictionary:
	var kind := gk.get_slice(":", 1)
	var id := gk.get_slice(":", 2)
	var found := Game.known.has(gk)
	var it: Item = null
	match kind:
		"u":
			it = Loot.unique_item(id, 1)
		"s":
			it = Loot.set_item(id, 1)
		"w":
			var wd: Dictionary = DB.words.get(id, {})
			it = Item.create(WORD_BASE.get(str(wd.get("bases", ["weapon"])[0]), "krumpac"), 1)
			it.sockets = wd.get("letters", []).size()
			it.word = id
	if it == null:
		return {}
	var lines: Array = it.tooltip(null)
	if kind == "w":
		lines[0] = ["%s  %s" % [it.glyphs(), L.t(DB.words[id].get("name", id)).to_upper()], Item.COL_UNIQUE]
		lines.insert(1, [L.t({"cs": "Písmena: %s", "en": "Letters: %s"}) % " ".join(DB.words[id].get("letters", [])), Item.COL_INFO])
	if not found:
		lines = [[lines[0][0], Item.COL_INFO], [L.t({"cs": "Zatím nenalezeno", "en": "Not found yet"}), UiTheme.DIM]]
	return {"item": it, "n": 1, "lines": lines, "dim": not found}


func _show_grail(key: String) -> void:
	var blocks := []
	var kind := key.get_slice(":", 1)
	if kind == "s":
		var sd: Dictionary = DB.sets.get(key.get_slice(":", 2), {})
		if sd.has("flavor"):
			blocks.append(["„" + L.t(sd.flavor) + "“", UiTheme.DIM])
	elif kind == "w":
		blocks.append([L.t({"cs": "Slovo zazní, když písmena v zásuvkách obyčejné věci leží přesně v pořadí.", "en": "A word speaks when the letters in a plain item's sockets lie in exactly the right order."}), UiTheme.DIM])
	else:
		blocks.append([L.t({"cs": "Sbírka platí pro všechny obtížnosti.", "en": "The collection counts across all difficulties."}), UiTheme.DIM])
	var icons := []
	for gk in _grail_keys(key):
		var spec := _grail_spec(gk)
		if not spec.is_empty():
			icons.append(spec)
	_page(_title(key), blocks, [], {"icons": icons})


func _jump(eid: String) -> void:
	var cat := str(DB.codex.get(eid, {}).get("cat", "term"))
	current = "codex:" + eid
	if cat != tab:
		_open_tab(cat)
	_show(current)


# What we have drawings for, limited to what the player has met so nothing is spoiled.
func _pictures(refs: Dictionary) -> Dictionary:
	var big := []
	for mid in refs.get("monster", []):
		if Game.known.has("monster:" + str(mid)) or Game.flags.get("killed_" + str(mid), false):
			big.append(DB.tex("portraits/boss_" + str(mid)) if DB.has_tex("portraits/boss_" + str(mid)) else DB.tex("sprites/monsters/%s_idle" % mid))
	for nid in refs.get("npc", []):
		if Game.known.has("npc:" + str(nid)):
			big.append(DB.tex_or("portraits/" + str(nid), "sprites/npcs/" + str(nid)))
	for cid in refs.get("class", []):
		big.append(DB.tex("portraits/hero_" + str(cid)))
	for sid in refs.get("shrine", []):
		big.append(DB.tex("props/modla_" + str(sid)))
	big = big.filter(func(t): return t != null).slice(0, 3)
	var icons := []
	for uid in refs.get("unique", []):
		var u: Dictionary = DB.uniques.get(uid, {})
		if Game.known.has("unique:" + str(uid)) and DB.items.has(str(u.get("base", ""))):
			var it := Item.create(str(u.base), 1)
			it.unique_id = uid
			it.rarity = Item.UNIQUE
			var lines := [[L.t(u.get("name", uid)), Item.COL_UNIQUE], [L.t(DB.item(it.base_id).get("name", "")), Item.COL_INFO]]
			if u.has("flavor"):
				lines.append(["„%s“" % L.t(u.flavor), Color("a08a5a")])
			icons.append({"item": it, "n": 1, "lines": lines})
	for iid in refs.get("item", []):
		if Game.known.has("item:" + str(iid)) and DB.items.has(str(iid)):
			var it := Item.create(str(iid), 1)
			icons.append({"item": it, "n": 1, "lines": it.tooltip(Game.ch)})
	return {"big": big, "icons": icons.slice(0, 8)}


# ---------------------------------------------------------------- reading aloud
# Without a recording the system's text-to-speech reads; the button stays hidden when there is neither.
static var _voices := {}


static func _voice() -> String:
	if not _voices.has(L.lang):
		_voices[L.lang] = _pick_voice() if DisplayServer.has_feature(DisplayServer.FEATURE_TEXT_TO_SPEECH) else ""
	return _voices[L.lang]


static func _pick_voice() -> String:
	var voices := DisplayServer.tts_get_voices_for_language(L.lang)
	if voices.is_empty():
		return ""
	var all := DisplayServer.tts_get_voices()
	for pref in ["piper", "rhvoice", "natural", "neural", "zdenek", "jirka", "alan"]:
		for v in all:
			if v.id in voices and (str(v.name) + str(v.id)).to_lower().contains(pref):
				return v.id
	for v in voices:
		if not str(v).to_lower().contains("espeak"):
			return v
	return voices[0]


# Generated recordings first (tools/voice_build.py); the system voice when this page has none.
func _set_read(parts: Array) -> void:
	read_parts = parts
	read_btn.visible = Sfx.can_read_aloud(parts) or _voice() != ""


func _toggle_read() -> void:
	if DisplayServer.tts_is_speaking() or reading_voice:
		_stop_read()
		return
	if Sfx.read_aloud(read_parts):
		reading_voice = true
		read_btn.text = "■"
		return
	var v := _voice()
	if v != "" and speech != "":
		DisplayServer.tts_speak(speech, v, 80, 0.95, 0.92)
		read_at = Time.get_ticks_msec()
		read_btn.text = "■"


func _stop_read() -> void:
	if DisplayServer.tts_is_speaking():
		DisplayServer.tts_stop()
	if reading_voice:
		reading_voice = false
		Sfx.stop_voice()
	if read_btn:
		read_btn.text = "▶"


func refresh() -> void:
	if reading_voice and not Sfx.voice_playing():
		reading_voice = false
		read_btn.text = "▶"
	elif read_btn and read_btn.text == "■" and not reading_voice and Time.get_ticks_msec() - read_at > 1000 and not DisplayServer.tts_is_speaking():
		read_btn.text = "▶"


func _exit_tree() -> void:
	_stop_read()
