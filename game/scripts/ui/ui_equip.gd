class_name UiEquip
extends Control

var slot := "weapon"


static func make(sl: String, pos: Vector2, cells: Vector2i) -> UiEquip:
	var e := UiEquip.new()
	e.slot = sl
	e.position = pos
	e.size = Vector2(cells) * UiTheme.CELL
	return e


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	UiRoot.inst.reg_tip(self)


func _process(_d: float) -> void:
	queue_redraw()


func _item() -> Item:
	return Game.ch.equip.get(slot, null)


func _draw() -> void:
	var r := Rect2(Vector2.ZERO, size)
	var hov := r.has_point(get_local_mouse_position())
	draw_rect(r, Color(0.05, 0.04, 0.035, 0.92))
	var st := DB.tex("ui/slot_hover" if hov else "ui/slot")
	if st:
		draw_texture_rect(st, r, false)
	draw_rect(r, Color(UiTheme.BRONZE, 0.9) if not hov else UiTheme.GOLD.darkened(0.2), false, 2.0)
	var it := _item()
	var ui := UiRoot.inst
	if ui.held:
		var fits: bool = slot in Game.ch.slot_for(ui.held)
		if fits:
			var ok := Game.ch.can_equip(ui.held)
			draw_rect(r.grow(-2), Color(0.3, 0.8, 0.35, 0.18) if ok else Color(0.9, 0.2, 0.2, 0.22))
	if it:
		UiTheme.draw_item(self, it, r.grow(-4))
		if ui.identify_mode and it.rarity != Item.NORMAL and not it.identified:
			draw_rect(r.grow(-2), Color(UiTheme.GOLD, 0.6), false, 2.0)
	else:
		var two: Item = Game.ch.weapon()
		if slot == "offhand" and two and two.two_handed():
			var t := two.icon()
			var s := minf(size.x / t.get_width(), size.y / t.get_height()) * 0.9
			var sz := Vector2(t.get_width(), t.get_height()) * s
			draw_texture_rect(t, Rect2((size - sz) / 2.0, sz), false, Color(1, 1, 1, 0.25))
		else:
			var txt := L.t("slot_" + slot)
			var f := UiTheme.small
			var w := f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16).x
			draw_string(f, Vector2((size.x - w) / 2.0, size.y / 2.0 + 6), txt, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(UiTheme.DIM, 0.55))


func _gui_input(event: InputEvent) -> void:
	if not (event is InputEventMouseButton and event.pressed):
		return
	accept_event()
	var ui := UiRoot.inst
	if event.button_index == MOUSE_BUTTON_LEFT:
		if ui.identify_mode:
			ui.identify(_item())
			return
		ui.equip_click(slot)
	elif event.button_index == MOUSE_BUTTON_RIGHT:
		if ui.identify_mode:
			ui.identify_mode = false
			return
		var it := _item()
		if it and ui.held == null and Game.ch.inv.add(it):
			Game.ch.equip.erase(slot)
			ui.after_equip()


func tip() -> Dictionary:
	var it := _item()
	if it == null or UiRoot.inst.held:
		return {}
	return {"lines": it.tooltip(Game.ch)}
