class_name SlotView
extends Control

var hud: Hud
var kind := "belt"
var index := 0
var key := ""


func _ready() -> void:
	size = Vector2(64, 64)
	mouse_filter = Control.MOUSE_FILTER_STOP


func _draw() -> void:
	var ch := Game.ch
	var st := DB.tex("ui/slot")
	if st and kind == "belt" and index >= 4:
		draw_texture_rect(st, Rect2(Vector2.ZERO, size), false)
	if kind == "belt":
		if index >= ch.belt.size():
			return
		var it: Item = ch.belt[index]
		if it:
			var t := it.icon()
			var s := minf(56.0 / t.get_width(), 56.0 / t.get_height())
			var sz := Vector2(t.get_width(), t.get_height()) * s
			draw_texture_rect(t, Rect2((size - sz) / 2, sz), false)
		draw_string(hud.font, Vector2(4, 18), str(index + 1), HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(1, 1, 1, 0.75))
	else:
		var id := hud.skill_for_slot(index)
		if id != "":
			var t := DB.tex("ui/skills/" + id)
			if t:
				draw_texture_rect(t, Rect2(Vector2.ZERO, size), false)
			else:
				draw_rect(Rect2(Vector2.ZERO, size), Color(0.2, 0.15, 0.12))
				draw_string(hud.font, Vector2(4, 40), L.t(DB.skill(id).get("name", id)).left(6), HORIZONTAL_ALIGNMENT_LEFT, -1, 16)
			var p: Player = Game.player
			if p and p.cooldowns.has(id):
				var cdv := float(DB.skill(id).get("cooldown", 1))
				var fr := clampf(p.cooldowns[id] / maxf(0.1, cdv), 0.0, 1.0)
				draw_rect(Rect2(0, 64 * (1.0 - fr), 64, 64 * fr), Color(0, 0, 0, 0.6))
			if id != "utok" and Game.ch.mana < Game.ch.skill_mana(id):
				draw_rect(Rect2(Vector2.ZERO, size), Color(0.1, 0.1, 0.5, 0.45))
		draw_string(hud.font, Vector2(4, 62), key, HORIZONTAL_ALIGNMENT_LEFT, -1, 16, Color(1, 0.9, 0.7, 0.9))


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		if kind == "belt":
			if Game.player and (event.button_index == MOUSE_BUTTON_RIGHT or (TouchPad.active and Game.main.ui.right == null and Game.main.ui.held == null)):
				Game.player.use_belt(index)
			elif event.button_index == MOUSE_BUTTON_LEFT and Game.main:
				var ui: UiRoot = Game.main.ui
				var cur: Item = Game.ch.belt[index]
				if ui.held and ui.held.base().get("use", {}).size() > 0 and ui.held.slot() == "consumable":
					Game.ch.belt[index] = ui.held
					ui.held = cur
				elif ui.held == null and cur:
					ui.held = cur
					Game.ch.belt[index] = null
				Game.ch.changed.emit()
				ui.cursor_layer.queue_redraw()
		else:
			if Game.main:
				Game.main.ui.open_skill_picker(index)
		accept_event()


func _make_custom_tooltip(_for_text: String) -> Object:
	return null


func _get_tooltip(_at: Vector2) -> String:
	if kind == "belt":
		var it: Item = Game.ch.belt[index] if index < Game.ch.belt.size() else null
		return it.display_name() if it else ""
	var id := hud.skill_for_slot(index)
	return L.t(DB.skill(id).get("name", id)) if id != "" else ""
