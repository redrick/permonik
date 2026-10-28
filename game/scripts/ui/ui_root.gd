class_name UiRoot
extends CanvasLayer

const BAR_H := UiTheme.BAR_H

static var inst: UiRoot

var font: Font
var root: Control
var left: Control
var right: Control
var modal: Control
var popup: Control
var screen: Control
var slides: Control
var held: Item
var card: UiItemCard
var book: UiPhoneBook
var identify_mode := false
var tip_sources: Array = []
var tip_box: PanelContainer
var tip_cmp: PanelContainer
var cursor_layer: Control
var _tip_key := ""


func _ready() -> void:
	inst = self
	layer = 30
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = Control.new()
	root.theme = UiTheme.get_theme()
	font = UiTheme.font
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	tip_box = _tip_panel()
	tip_cmp = _tip_panel()
	cursor_layer = Control.new()
	cursor_layer.set_anchors_preset(Control.PRESET_FULL_RECT)
	cursor_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	cursor_layer.draw.connect(_draw_cursor)
	cursor_layer.z_index = 10
	root.add_child(cursor_layer)
	var cfg := ConfigFile.new()
	if cfg.load("user://settings.cfg") == OK and bool(cfg.get_value("main", "fullscreen", false)):
		DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)


func _tip_panel() -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.03, 0.025, 0.03, 0.95), Color("6a5236"), 2, 12))
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.visible = false
	p.z_index = 9
	var vb := VBoxContainer.new()
	vb.add_theme_constant_override("separation", 1)
	vb.mouse_filter = Control.MOUSE_FILTER_IGNORE
	p.add_child(vb)
	root.add_child(p)
	return p


# ---------------------------------------------------------------- layout
func _place(c: Control, where: String) -> void:
	c.set_meta("place", where)
	if compact() and where in ["left", "right"]:
		_book().add_panel(c, where)
		_sync_pause()
		return
	c.resized.connect(_fit.bind(c))
	root.add_child(c)
	root.move_child(c, root.get_child_count() - 1)
	for t in [tip_box, tip_cmp, cursor_layer]:
		root.move_child(t, -1)
	match where:
		"left":
			c.anchor_left = 0.0
			c.anchor_right = 0.0
			c.anchor_top = 1.0
			c.anchor_bottom = 1.0
			c.offset_left = 6
			c.offset_right = 6
			c.offset_bottom = -_bar() - 4
			c.offset_top = -_bar() - 4
			c.grow_vertical = Control.GROW_DIRECTION_BEGIN
		"right":
			c.anchor_left = 1.0
			c.anchor_right = 1.0
			c.anchor_top = 1.0
			c.anchor_bottom = 1.0
			c.offset_left = -6
			c.offset_right = -6
			c.offset_bottom = -_bar() - 4
			c.offset_top = -_bar() - 4
			c.grow_horizontal = Control.GROW_DIRECTION_BEGIN
			c.grow_vertical = Control.GROW_DIRECTION_BEGIN
		"center":
			c.anchor_left = 0.5
			c.anchor_right = 0.5
			c.anchor_top = 0.5
			c.anchor_bottom = 0.5
			c.offset_left = 0
			c.offset_right = 0
			c.offset_top = -_bar() / 2.0
			c.offset_bottom = -_bar() / 2.0
			c.grow_horizontal = Control.GROW_DIRECTION_BOTH
			c.grow_vertical = Control.GROW_DIRECTION_BOTH
		"full":
			c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)


func _bar() -> float:
	return Game.main.hud.bar_h() if Game.main and Game.main.hud else float(BAR_H)


# A phone-sized screen: side panels open full screen inside the book (UiPhoneBook) instead.
func compact() -> bool:
	return root.size.y < 760.0


func _book() -> UiPhoneBook:
	if book == null:
		close_card()
		book = UiPhoneBook.new()
		root.add_child(book)
		for t in [tip_box, tip_cmp, cursor_layer]:
			root.move_child(t, -1)
		card = book.detail
		Sfx.play("ui_open", 0.5, 0.0)
	return book


func close_book() -> void:
	if book == null:
		return
	_return_held()
	identify_mode = false
	for c in [left, right]:
		_free(c)
	left = null
	right = null
	book.queue_free()
	book = null
	card = null
	_sync_pause()


# A tab of the book: switches the page, or closes the book when that page is already shown.
func phone_page(what: String) -> void:
	match what:
		"close":
			close_book()
			Sfx.play("ui_close", 0.5, 0.0)
			return
		"pause":
			close_book()
			show_pause()
			return
		"automap":
			close_book()
			Game.main.hud.toggle("automap")
			return
	if book and book.page() == what:
		close_book()
		return
	_return_held()
	identify_mode = false
	_free(left)
	_free(right)
	left = null
	right = null
	close_card()
	match what:
		"inventory":
			_open_inventory()
		"hireling":
			_set_left(UiHireling.new(), what)
			_open_inventory()
		"character":
			_set_left(UiCharacter.new(), what)
		"skills":
			_set_left(UiSkills.new(), what)
		"quests":
			_set_left(UiQuests.new(), what)
		"kronika":
			_set_left(UiKronika.new(), what)
	Sfx.play("ui_open", 0.5, 0.0)


func _set_left(p: Control, kind: String) -> void:
	left = p
	left.set_meta("kind", kind)
	_place(left, "left")


func fit_all() -> void:
	for c in [left, right, modal, popup]:
		if c and is_instance_valid(c):
			_fit(c)
	if card and is_instance_valid(card):
		card._sig = ""


# Panels are laid out at the 1080 px design height; a scaled-up UI on a short screen shrinks them to fit.
func _fit(c: Control) -> void:
	var where: String = c.get_meta("place", "full")
	if where == "full" or c.size.x <= 0.0 or c.size.y <= 0.0:
		return
	var bar := _bar()
	var k := minf(1.0, minf((root.size.x - 12.0) / c.size.x, (root.size.y - bar - 10.0) / c.size.y))
	match where:
		"left":
			c.pivot_offset = Vector2(0, c.size.y)
		"right":
			c.pivot_offset = c.size
		_:
			c.pivot_offset = c.size / 2.0
	c.scale = Vector2(k, k)


func _free(c: Control) -> void:
	if c and is_instance_valid(c):
		c.queue_free()


func _sync_pause() -> void:
	var p := modal != null or book != null or (left != null and (left is UiVendor or left is UiStash or left is UiKronika))
	Game.paused_ui = p or screen != null or slides != null


# ---------------------------------------------------------------- public API
func show_main_menu() -> void:
	close_all()
	screen = UiMenu.new()
	_place(screen, "full")
	_sync_pause()


func close_all() -> void:
	_return_held()
	identify_mode = false
	if slides and Game.main:
		Game.main.slide_queue.clear()
		Game.main.slides_playing = false
	for c in [left, right, modal, popup, screen, slides]:
		_free(c)
	close_card()
	if book:
		book.queue_free()
		book = null
		card = null
	left = null
	right = null
	modal = null
	popup = null
	screen = null
	slides = null
	Game.paused_ui = false
	get_tree().paused = false


func any_open() -> bool:
	return left != null or right != null or modal != null or popup != null or screen != null or held != null or identify_mode


func mouse_over_ui() -> bool:
	return over_ui_at(root.get_global_mouse_position())


func over_ui_at(mp: Vector2) -> bool:
	if screen or slides or book:
		return true
	for c in [left, right, modal, popup, card]:
		if c and is_instance_valid(c) and c.visible and c.get_global_rect().has_point(mp):
			return true
	return false


func toggle_panel(what: String) -> void:
	if screen or slides or modal:
		return
	_free(popup)
	popup = null
	if compact():
		if book and book.trade():
			close_all()
		else:
			phone_page(what)
		return
	if what == "inventory":
		if right:
			if left is UiVendor or left is UiStash:
				close_all()
				return
			close_panel(right)
		else:
			_open_inventory()
		return
	if left and left.get_meta("kind", "") == what:
		close_panel(left)
		return
	if left is UiVendor or left is UiStash:
		close_all()
	_free(left)
	match what:
		"character":
			left = UiCharacter.new()
		"skills":
			left = UiSkills.new()
		"quests":
			left = UiQuests.new()
		"kronika":
			left = UiKronika.new()
		"hireling":
			left = UiHireling.new()
			_open_inventory()
		_:
			left = null
			return
	left.set_meta("kind", what)
	_place(left, "left")
	Sfx.play("ui_open", 0.5, 0.0)
	_sync_pause()


func _open_inventory() -> void:
	if right:
		return
	right = UiInventory.new()
	_place(right, "right")
	Sfx.play("ui_open", 0.5, 0.0)


func close_panel(p: Control) -> void:
	if p == null:
		return
	if p == right or p is UiVendor or p is UiStash:
		_return_held()
		identify_mode = false
		if left is UiVendor or left is UiStash:
			_free(left)
			left = null
		_free(right)
		right = null
	if p == left:
		_free(left)
		left = null
	if p == modal:
		_free(modal)
		modal = null
	if p == popup:
		_free(popup)
		popup = null
	if p == screen:
		_free(screen)
		screen = null
		get_tree().paused = false
	Sfx.play("ui_close", 0.5, 0.0)
	_sync_pause()


func open_npc(npc: Npc) -> void:
	close_all()
	Game.learn("npc", npc.npc_id)
	var d := UiDialog.new()
	d.npc = npc
	modal = d
	_place(modal, "center")
	_sync_pause()


func open_vendor(npc: Npc, gamble := false, peddler := false) -> void:
	if npc == null:
		return
	close_all()
	var v := UiVendor.new()
	v.npc = npc
	v.gamble = gamble
	v.peddler = peddler
	left = v
	_place(left, "left")
	_open_inventory()
	_sync_pause()


func open_hireling() -> void:
	close_all()
	var h := UiHireling.new()
	h.at_inn = true
	h.set_meta("kind", "hireling")
	left = h
	_place(left, "left")
	_open_inventory()
	_sync_pause()


func open_kronika() -> void:
	close_all()
	left = UiKronika.new()
	left.set_meta("kind", "kronika")
	_place(left, "left")
	_sync_pause()


func open_book(bid: String) -> void:
	if not DB.books.has(bid):
		return
	_free(modal)
	var b := UiBook.new()
	b.book_id = bid
	modal = b
	_place(modal, "center")
	_sync_pause()


func open_waypoints() -> void:
	close_all()
	modal = UiWaypoints.new()
	_place(modal, "center")
	Sfx.play("waypoint", 0.6)
	_sync_pause()


func open_forge() -> void:
	close_all()
	left = UiForge.new()
	_place(left, "left")
	_open_inventory()
	_sync_pause()


func open_service(kind: String) -> void:
	close_all()
	var s := UiService.new()
	s.kind = kind
	left = s
	_place(left, "left")
	_open_inventory()
	_sync_pause()


func open_stash() -> void:
	close_all()
	left = UiStash.new()
	_place(left, "left")
	_open_inventory()
	Sfx.play("chest_open", 0.6)
	_sync_pause()


func open_skill_picker(slot: int) -> void:
	if screen or slides or modal:
		return
	if popup is UiPicker and (popup as UiPicker).slot == slot:
		close_panel(popup)
		return
	_free(popup)
	var p := UiPicker.new()
	p.slot = slot
	popup = p
	root.add_child(p)
	p.anchor_left = 0.5
	p.anchor_right = 0.5
	p.anchor_top = 1.0
	p.anchor_bottom = 1.0
	var x := -960.0 + Hud.SKILL_X + slot * Hud.SLOT_GAP + 32.0
	p.offset_left = x
	p.offset_right = x
	p.offset_top = -BAR_H - 2
	p.offset_bottom = -BAR_H - 2
	p.grow_horizontal = Control.GROW_DIRECTION_BOTH
	p.grow_vertical = Control.GROW_DIRECTION_BEGIN
	for t in [tip_box, tip_cmp, cursor_layer]:
		root.move_child(t, -1)


func start_identify() -> void:
	if screen or slides:
		return
	if Game.ch.inv.count("svitek_zjeveni") <= 0:
		return
	if right == null:
		_open_inventory()
	identify_mode = true
	Game.msg(UiTheme.t("identify_hint"), UiTheme.GOLD)


func play_slides(items: Array, done: Callable) -> void:
	_free(slides)
	var s := UiSlides.new()
	s.items = items
	s.done = done
	slides = s
	_place(slides, "full")
	if Game.main and Game.main.fade:
		var f: ColorRect = Game.main.fade
		f.color.a = 0.0
		f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	get_tree().paused = true
	_sync_pause()


func play_cinema(film: String, done: Callable) -> void:
	_free(slides)
	var s := UiCinema.new()
	s.film = film
	s.done = done
	slides = s
	_place(slides, "full")
	if Game.main and Game.main.fade:
		var f: ColorRect = Game.main.fade
		f.color.a = 0.0
		f.mouse_filter = Control.MOUSE_FILTER_IGNORE
	get_tree().paused = Game.level != null
	_sync_pause()


func skip_slides() -> void:
	if slides == null:
		return
	if Game.level == null and Game.main:
		Game.main.slide_queue.clear()
	slides.call("skip_all")


func slides_finished(s: Control, done: Callable) -> void:
	if slides == s:
		slides = null
	_free(s)
	if screen == null:
		get_tree().paused = false
	_sync_pause()
	if done.is_valid():
		done.call()


func show_credits(done: Callable) -> void:
	close_all()
	var c := UiCredits.new()
	c.done = done
	screen = c
	_place(screen, "full")
	_sync_pause()


func show_death() -> void:
	close_all()
	screen = UiDeath.new()
	_place(screen, "full")
	_sync_pause()


func show_pause() -> void:
	if screen or slides:
		return
	_return_held()
	_free(popup)
	popup = null
	screen = UiPause.new()
	_place(screen, "full")
	get_tree().paused = true
	_sync_pause()


func vendor_open() -> bool:
	return left is UiVendor


func vendor_panel() -> UiVendor:
	return left as UiVendor


# ---------------------------------------------------------------- item card (touch)
func show_card(it: Item, src: Control) -> void:
	if card and is_instance_valid(card) and card.item == it and card.src == src:
		return
	if card and card.docked:
		card.show_item(it, src)
		Sfx.play("ui_click", 0.4, 0.0)
		return
	close_card()
	card = UiItemCard.new()
	card.item = it
	card.src = src
	root.add_child(card)
	for t in [tip_box, tip_cmp, cursor_layer]:
		root.move_child(t, -1)
	Sfx.play("ui_click", 0.4, 0.0)


func close_card() -> void:
	if card and is_instance_valid(card) and card.docked:
		card.show_item(null, null)
		return
	if card and is_instance_valid(card):
		card.queue_free()
	card = null


func card_height() -> float:
	return root.size.y - _bar() - 16.0


# In the free gap between the open panels when it is wide enough, else over the panel the item is not in.
func place_card() -> void:
	if card == null or not is_instance_valid(card) or card.docked:
		return
	var sz := card.get_combined_minimum_size()
	var k := minf(1.0, card_height() / maxf(1.0, sz.y))
	card.scale = Vector2(k, k)
	var w := sz.x * k
	var lx := 6.0
	var rx := root.size.x - 6.0
	if left and is_instance_valid(left):
		lx = left.get_global_rect().end.x + 6.0
	if right and is_instance_valid(right):
		rx = right.get_global_rect().position.x - 6.0
	var x := (lx + rx - w) / 2.0
	if rx - lx < w:
		var from_right: bool = right != null and is_instance_valid(right) and right.is_ancestor_of(card.src)
		x = 6.0 if from_right else root.size.x - w - 6.0
	card.position = Vector2(x, 8.0)


# ---------------------------------------------------------------- item handling
func changed() -> void:
	Game.note_found_all()
	Game.ch.recalc()
	Game.ch.changed.emit()


func _return_held() -> void:
	if held == null:
		return
	var it := held
	held = null
	if Game.ch.inv.add(it):
		changed()
		return
	if Game.level and Game.player:
		Game.level.drop_item(it, Game.player.global_position)
	else:
		Game.ch.stash.add(it)
	changed()


func equip_click(sl: String) -> void:
	var ch := Game.ch
	if held == null:
		var cur: Item = ch.equip.get(sl, null)
		if cur:
			ch.equip.erase(sl)
			held = cur
			after_equip()
		return
	var worn: Item = ch.equip.get(sl, null)
	if worn and worn.can_socket(held):
		worn.socket(held)
		held = null
		Sfx.play("block", 0.4)
		ch.recalc()
		after_equip()
		return
	if not (sl in ch.slot_for(held)):
		Game.msg(UiTheme.t("wrong_slot"), UiTheme.DIM)
		return
	if not ch.can_equip(held):
		Game.msg(L.t("cant_use"), UiTheme.DIM)
		return
	var w := ch.weapon()
	if sl == "offhand" and w and w.two_handed():
		Game.msg(UiTheme.t("two_handed_block"), UiTheme.DIM)
		return
	if sl == "weapon" and held.two_handed() and ch.equip.get("offhand", null):
		if not ch.inv.add(ch.equip.offhand):
			Game.msg(L.t("inv_full"), UiTheme.DIM)
			return
		ch.equip.erase("offhand")
	var old: Item = ch.equip.get(sl, null)
	ch.equip[sl] = held
	held = old
	after_equip()


func merc_equip_click(sl: String) -> void:
	var m: Dictionary = Game.ch.merc
	if m.is_empty() or m.get("dead", false):
		return
	var eq: Dictionary = m.equip
	if held == null:
		var cur: Item = eq.get(sl, null)
		if cur:
			eq.erase(sl)
			held = cur
			merc_changed()
		return
	if not Hireling.slot_ok(m, held, sl):
		Game.msg(L.t("cant_use"), UiTheme.DIM)
		return
	var old: Item = eq.get(sl, null)
	eq[sl] = held
	held = old
	merc_changed()


func merc_changed() -> void:
	Sfx.play("equip", 0.7)
	if Game.level and is_instance_valid(Game.level.hireling):
		Game.level.hireling.refresh()
	changed()


func quick_equip(it: Item) -> void:
	var ch := Game.ch
	var slots := ch.slot_for(it)
	if slots.is_empty():
		return
	if not ch.can_equip(it):
		Game.msg(L.t("cant_use"), UiTheme.DIM)
		return
	var sl: String = slots[0]
	for s in slots:
		if not ch.equip.get(s, null):
			sl = s
			break
	var pos := it.pos
	var back := {}
	if ch.equip.get(sl, null):
		back[sl] = ch.equip[sl]
	if sl == "weapon" and it.two_handed() and ch.equip.get("offhand", null):
		back["offhand"] = ch.equip.offhand
	if sl == "offhand" and ch.weapon() and ch.weapon().two_handed():
		back["weapon"] = ch.weapon()
	ch.inv.remove(it)
	var placed := []
	for k in back:
		var b: Item = back[k]
		if (k == sl and ch.inv.place(b, pos)) or ch.inv.add(b):
			placed.append(b)
		else:
			for p in placed:
				ch.inv.remove(p)
			ch.inv.place(it, pos)
			Game.msg(L.t("inv_full"), UiTheme.DIM)
			return
	for k in back:
		ch.equip.erase(k)
	ch.equip[sl] = it
	after_equip()


func after_equip() -> void:
	var ch := Game.ch
	for i in range(ch.belt_size(), ch.belt.size()):
		var b: Item = ch.belt[i]
		if b:
			ch.belt[i] = null
			if not ch.inv.add(b) and Game.level and Game.player:
				Game.level.drop_item(b, Game.player.global_position)
	Sfx.play("equip", 0.7)
	changed()


func use_or_equip(it: Item) -> void:
	if it.is_equipment():
		quick_equip(it)
		return
	if it.slot() != "consumable":
		return
	if it.base().get("use", {}).has("identify"):
		start_identify()
		return
	if Game.player == null or Game.player.dead:
		return
	if Game.player.use_item(it):
		it.qty -= 1
		if it.qty <= 0:
			Game.ch.inv.remove(it)
		changed()


func to_belt(it: Item) -> bool:
	var u: Dictionary = it.base().get("use", {})
	if not (u.has("heal_pct") or u.has("mana_pct") or u.has("rejuv")):
		return false
	var ch := Game.ch
	for i in ch.belt_size():
		if ch.belt[i] == null:
			ch.inv.remove(it)
			ch.belt[i] = it
			Sfx.play("pickup", 0.5)
			changed()
			return true
	return false


func identify(it: Item) -> void:
	identify_mode = false
	if it == null or it.identified or it.rarity == Item.NORMAL:
		return
	if not Game.ch.inv.take("svitek_zjeveni"):
		return
	it.identified = true
	Game.msg(it.display_name(), it.color())
	Sfx.play("buff", 0.6)
	changed()


# ---------------------------------------------------------------- tooltips & cursor
func reg_tip(c: Control) -> void:
	tip_sources.append(c)


func _process(_d: float) -> void:
	cursor_layer.queue_redraw()
	var mp := root.get_global_mouse_position()
	var tip := {}
	for i in range(tip_sources.size() - 1, -1, -1):
		var c = tip_sources[i]
		if not is_instance_valid(c):
			tip_sources.remove_at(i)
			continue
		if c.is_visible_in_tree() and c.get_global_rect().has_point(mp):
			tip = c.tip()
			break
	if slides or (screen and not (screen is UiMenu)):
		tip = {}
	_show_tip(tip, mp)


func _show_tip(tip: Dictionary, mp: Vector2) -> void:
	var lines: Array = tip.get("lines", [])
	if lines.is_empty():
		tip_box.visible = false
		tip_cmp.visible = false
		_tip_key = ""
		return
	var cmp: Item = null
	var it: Item = tip.get("item", null)
	if it and it.is_equipment():
		for sl in Game.ch.slot_for(it):
			var e: Item = Game.ch.equip.get(sl, null)
			if e and e != it:
				cmp = e
				break
	var key := str(lines) + str(cmp)
	if key != _tip_key:
		_tip_key = key
		if it and not is_nan(Game.ch.upgrade_score(it)):
			var dl := Game.ch.delta_lines(it)
			if not dl.is_empty():
				lines = lines.duplicate()
				lines.append([L.t({"cs": "Když si to nasadíš:", "en": "If you wear it:"}), UiTheme.FAINT])
				for x in dl:
					lines.append(["  " + x[0], Color("5fd068") if x[1] else UiTheme.RED])
		_fill_tip(tip_box, lines, "")
		if cmp:
			_fill_tip(tip_cmp, cmp.tooltip(Game.ch), UiTheme.t("equipped"))
	tip_box.visible = true
	tip_cmp.visible = cmp != null
	tip_box.size = tip_box.get_combined_minimum_size()
	var vs := root.size
	var pos := mp + Vector2(22, 18)
	if pos.x + tip_box.size.x > vs.x - 4:
		pos.x = mp.x - tip_box.size.x - 14
	pos.y = clampf(pos.y, 4, maxf(4, vs.y - tip_box.size.y - 4))
	tip_box.position = pos
	if cmp:
		tip_cmp.size = tip_cmp.get_combined_minimum_size()
		var cp := Vector2(pos.x - tip_cmp.size.x - 8, pos.y)
		if cp.x < 4:
			cp.x = pos.x + tip_box.size.x + 8
		cp.y = clampf(cp.y, 4, maxf(4, vs.y - tip_cmp.size.y - 4))
		tip_cmp.position = cp


func _fill_tip(p: PanelContainer, lines: Array, header: String) -> void:
	var vb: VBoxContainer = p.get_child(0)
	for c in vb.get_children():
		vb.remove_child(c)
		c.queue_free()
	if header != "":
		vb.add_child(UiTheme.label(header, 17, UiTheme.FAINT, true))
	var first := true
	for ln in lines:
		var txt := str(ln[0])
		var col: Color = ln[1] if ln.size() > 1 else UiTheme.INK
		var l := UiTheme.label(txt, 25 if first else 20, col, not first)
		if not first:
			l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.custom_minimum_size = Vector2(minf(420, maxf(220, txt.length() * 9.0)), 0)
		vb.add_child(l)
		first = false


func _draw_cursor() -> void:
	var mp := cursor_layer.get_local_mouse_position()
	if held:
		var s := Vector2(held.size()) * UiTheme.CELL
		UiTheme.draw_item(cursor_layer, held, Rect2(mp - s / 2.0, s), false)
	if identify_mode:
		var c := mp + Vector2(26, 26)
		cursor_layer.draw_line(c + Vector2(7, 7), c + Vector2(16, 16), Color("6a4a2a"), 5.0)
		cursor_layer.draw_circle(c, 10, Color(0.6, 0.8, 1.0, 0.25))
		cursor_layer.draw_arc(c, 10, 0, TAU, 24, UiTheme.GOLD, 3.0)


# ---------------------------------------------------------------- input
func _input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and left is UiSkills:
		var keys := ["skill_q", "skill_w", "skill_e", "skill_r"]
		for i in 4:
			if event.is_action(keys[i]) and (left as UiSkills).bind_hover(i):
				get_viewport().set_input_as_handled()
				return


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.is_action("pause"):
		if slides:
			skip_slides()
		elif screen:
			if screen.has_method("on_escape"):
				screen.call("on_escape")
		elif popup and not (left or right or modal):
			close_panel(popup)
		else:
			return
		get_viewport().set_input_as_handled()
		return
	if event is InputEventMouseButton and event.pressed:
		if popup and not popup.get_global_rect().has_point(root.get_global_mouse_position()):
			close_panel(popup)
		if identify_mode:
			identify_mode = false
			get_viewport().set_input_as_handled()
			return
		if held and event.button_index == MOUSE_BUTTON_LEFT and Game.level and Game.player and not screen:
			if Game.main and Game.main.hud.mouse_over_ui():
				return
			Game.level.drop_item(held, Game.player.global_position)
			held = null
			changed()
			get_viewport().set_input_as_handled()
