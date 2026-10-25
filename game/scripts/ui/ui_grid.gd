class_name UiGrid
extends Control

const CELL := UiTheme.CELL

var src: Callable
var mode := "inv"
var vendor: UiVendor


static func make(get_inv: Callable, m: String) -> UiGrid:
	var g := UiGrid.new()
	g.src = get_inv
	g.mode = m
	var inv: Inventory = get_inv.call()
	g.custom_minimum_size = Vector2(inv.w * CELL, inv.h * CELL)
	g.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	return g


func inv() -> Inventory:
	return src.call()


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiRoot.inst.reg_tip(self)


func _process(_d: float) -> void:
	queue_redraw()


func _mouse_cell() -> Vector2i:
	var p := get_local_mouse_position() / CELL
	return Vector2i(floori(p.x), floori(p.y))


func _drop_cell(it: Item) -> Vector2i:
	var s := it.size()
	var p := get_local_mouse_position() / CELL - Vector2(s) / 2.0
	var i := inv()
	return Vector2i(clampi(roundi(p.x), 0, maxi(0, i.w - s.x)), clampi(roundi(p.y), 0, maxi(0, i.h - s.y)))


func _hovering() -> bool:
	return Rect2(Vector2.ZERO, size).has_point(get_local_mouse_position())


func _draw() -> void:
	var i := inv()
	var ui := UiRoot.inst
	var hov := _hovering()
	var under: Item = i.item_at(_mouse_cell()) if hov else null
	for y in i.h:
		for x in i.w:
			UiTheme.draw_cell(self, Rect2(Vector2(x, y) * CELL, Vector2(CELL, CELL)))
	if hov and ui.held and mode != "vendor":
		var at := _drop_cell(ui.held)
		var bl := i.blockers(ui.held, at)
		var col := Color(0.3, 0.8, 0.35, 0.22) if bl.size() <= 1 else Color(0.9, 0.2, 0.2, 0.25)
		draw_rect(Rect2(Vector2(at) * CELL, Vector2(ui.held.size()) * CELL), col)
	for it: Item in i.items:
		var r := Rect2(Vector2(it.pos) * CELL, Vector2(it.size()) * CELL)
		if it == under and ui.held == null:
			draw_rect(r.grow(-1), Color(1, 0.85, 0.5, 0.12))
		UiTheme.draw_item(self, it, r)
		if not (mode == "vendor" and vendor.gamble):
			UiTheme.draw_upgrade(self, it, r)
		if ui.identify_mode and mode == "inv" and it.rarity != Item.NORMAL and not it.identified:
			draw_rect(r.grow(-2), Color(UiTheme.GOLD, 0.5 + 0.3 * sin(Time.get_ticks_msec() / 150.0)), false, 2.0)


func _gui_input(event: InputEvent) -> void:
	if not (event is InputEventMouseButton and event.pressed):
		return
	accept_event()
	var ui := UiRoot.inst
	var i := inv()
	var it: Item = i.item_at(_mouse_cell())
	if event.button_index == MOUSE_BUTTON_LEFT:
		if mode == "vendor":
			if ui.held:
				vendor.sell(ui.held, true)
			elif it and Input.is_key_pressed(KEY_SHIFT) and it.slot() == "consumable" and not vendor.gamble:
				vendor.fill_belt(it)
			elif it:
				vendor.buy(it)
			return
		if ui.identify_mode:
			ui.identify(it)
			return
		if ui.held:
			_put(ui)
		elif it:
			if event.shift_pressed and mode == "inv" and ui.to_belt(it):
				return
			i.remove(it)
			ui.held = it
			Sfx.play("pickup", 0.5)
			ui.changed()
	elif event.button_index == MOUSE_BUTTON_RIGHT:
		if ui.identify_mode:
			ui.identify_mode = false
			return
		if it and mode == "inv":
			if ui.vendor_open():
				ui.vendor_panel().sell(it, false)
			elif ui.left is UiStash:
				if (ui.left as UiStash).box().add(it):
					i.remove(it)
					ui.changed()
			elif ui.left is UiForge:
				if (ui.left as UiForge).box.add(it):
					i.remove(it)
					ui.changed()
			elif ui.left is UiService:
				if (ui.left as UiService).box.add(it):
					i.remove(it)
					ui.changed()
			else:
				ui.use_or_equip(it)
		elif it and mode == "forge":
			if Game.ch.inv.add(it):
				i.remove(it)
				ui.changed()
		elif it and mode == "stash":
			if Game.ch.inv.add(it):
				i.remove(it)
				ui.changed()


func _put(ui: UiRoot) -> void:
	var i := inv()
	var h: Item = ui.held
	var at := _drop_cell(h)
	var bl := i.blockers(h, at)
	if bl.size() == 0:
		if i.place(h, at):
			ui.held = null
	elif bl.size() == 1 and bl[0].can_socket(h):
		bl[0].socket(h)
		ui.held = null
		Sfx.play("block", 0.4)
		ui.changed()
		return
	elif bl.size() == 1:
		var o: Item = bl[0]
		var mx := int(o.base().get("max_stack", 1))
		if h.is_stackable() and o.base_id == h.base_id and o.qty < mx:
			var k := mini(h.qty, mx - o.qty)
			o.qty += k
			h.qty -= k
			if h.qty <= 0:
				ui.held = null
		else:
			i.remove(o)
			if i.place(h, at):
				ui.held = o
			else:
				i.place(o, o.pos)
	else:
		return
	Sfx.play("drop_item", 0.5)
	ui.changed()


func tip() -> Dictionary:
	if UiRoot.inst.held:
		return {}
	var it: Item = inv().item_at(_mouse_cell())
	if it == null:
		return {}
	var lines: Array = it.tooltip(Game.ch)
	var ui := UiRoot.inst
	if mode == "vendor":
		var p := vendor.price_of(it)
		lines.append([UiTheme.t("price", {"v": p}), UiTheme.GOLD if Game.ch.gold >= p else UiTheme.RED])
	elif mode == "inv" and ui.vendor_open():
		var sp := it.sell_price()
		if sp <= 0:
			lines.append([UiTheme.t("unsellable"), UiTheme.RED])
		elif not ui.vendor_panel().accepts(it):
			lines.append([UiTheme.t("wont_buy"), UiTheme.RED])
		else:
			lines.append([UiTheme.t("sell_for", {"v": sp}), UiTheme.GOLD])
	elif mode == "inv":
		if it.slot() == "consumable":
			lines.append([UiTheme.t("rc_use"), UiTheme.FAINT])
		elif it.is_equipment():
			lines.append([UiTheme.t("rc_equip"), UiTheme.FAINT])
	return {"lines": lines, "item": it}
