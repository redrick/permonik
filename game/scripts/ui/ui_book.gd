class_name UiBook
extends UiPanel

var book_id := ""
var page_i := 0
var text_lbl: Label
var page_lbl: Label
var prev_b: Button
var next_b: Button
var read_b: Button


func _ready() -> void:
	var b: Dictionary = DB.books.get(book_id, {})
	custom_minimum_size = Vector2(760, 0)
	set_title(L.t(b.get("title", book_id)))
	var by := UiTheme.wrap_label(L.t(b.get("author", "")), 19, UiTheme.DIM, 700)
	by.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(by)
	var paper := PanelContainer.new()
	paper.add_theme_stylebox_override("panel", UiTheme.flat(Color("2a2118"), Color("4a3a28"), 2, 26))
	body.add_child(paper)
	var sc := ScrollContainer.new()
	sc.custom_minimum_size = Vector2(700, 600)
	sc.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	paper.add_child(sc)
	text_lbl = UiTheme.wrap_label("", 24, Color("e6d9bc"), 660)
	sc.add_child(text_lbl)
	var nav := HBoxContainer.new()
	nav.alignment = BoxContainer.ALIGNMENT_CENTER
	nav.add_theme_constant_override("separation", 24)
	body.add_child(nav)
	prev_b = UiTheme.small_button("‹", func(): _turn(-1), 56)
	nav.add_child(prev_b)
	page_lbl = UiTheme.label("", 22, UiTheme.DIM)
	nav.add_child(page_lbl)
	next_b = UiTheme.small_button("›", func(): _turn(1), 56)
	nav.add_child(next_b)
	read_b = UiTheme.small_button("▶", _toggle_read, 56)
	read_b.tooltip_text = L.t({"cs": "Přečíst nahlas", "en": "Read aloud"})
	nav.add_child(read_b)
	page_i = clampi(int(Game.known.get("page:" + book_id, 0)), 0, maxi(0, _pages().size() - 1))
	_render()


func _pages() -> Array:
	var p = DB.books.get(book_id, {}).get("pages", {})
	return p.get(L.lang, p.get("cs", [])) if p is Dictionary else []


# One page in both languages, so the voice can read it in its own language.
static func page_text(b: Dictionary, i: int) -> Dictionary:
	var out := {}
	var p = b.get("pages", {})
	if p is Dictionary:
		for lang in p:
			if i < p[lang].size():
				out[lang] = str(p[lang][i])
	return out


func _toggle_read() -> void:
	if Sfx.voice_playing():
		Sfx.stop_voice()
	else:
		Sfx.read_aloud([page_text(DB.books.get(book_id, {}), page_i)])
	_render()


func refresh() -> void:
	var t := "■" if Sfx.voice_playing() else "▶"
	if read_b.text != t:
		read_b.text = t


func _exit_tree() -> void:
	Sfx.stop_voice()


func _turn(d: int) -> void:
	Sfx.stop_voice()
	page_i = clampi(page_i + d, 0, maxi(0, _pages().size() - 1))
	Game.known["page:" + book_id] = page_i
	_render()


func _render() -> void:
	var pages := _pages()
	text_lbl.text = str(pages[page_i]) if page_i < pages.size() else ""
	page_lbl.text = "%d / %d" % [page_i + 1, maxi(1, pages.size())]
	prev_b.disabled = page_i == 0
	next_b.disabled = page_i >= pages.size() - 1
	read_b.visible = Sfx.can_read_aloud([page_text(DB.books.get(book_id, {}), page_i)])
	refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.physical_keycode:
			KEY_LEFT:
				_turn(-1)
			KEY_RIGHT, KEY_SPACE:
				_turn(1)
			_:
				return
		get_viewport().set_input_as_handled()
