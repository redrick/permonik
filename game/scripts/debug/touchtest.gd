extends Node

# Touch test (run with --quick --touch --touchtest): feeds raw screen touches and prints PASS/FAIL per step.
var step := 0
var t := 0.0
var p0 := Vector2.ZERO
var fails := 0
var rmb_seen := false
var tap_at := Vector2.ZERO
var near: Monster = null


func _input(e: InputEvent) -> void:
	if e is InputEventMouseButton and e.button_index == MOUSE_BUTTON_RIGHT and e.pressed:
		rmb_seen = true


func _touch(i: int, p: Vector2, pressed: bool) -> void:
	var e := InputEventScreenTouch.new()
	e.index = i
	e.position = get_viewport().get_screen_transform() * p
	e.pressed = pressed
	Input.parse_input_event(e)


func _drag(i: int, p: Vector2) -> void:
	var e := InputEventScreenDrag.new()
	e.index = i
	e.position = get_viewport().get_screen_transform() * p
	Input.parse_input_event(e)


func _check(name: String, ok: bool, info := "") -> void:
	print("TOUCH %s %s %s" % ["PASS" if ok else "FAIL", name, info])
	if not ok:
		fails += 1


func _screen(w: Vector2) -> Vector2:
	return get_viewport().get_canvas_transform() * w


func _physics_process(delta: float) -> void:
	var pl: Player = Game.player
	if pl == null or Game.level == null:
		return
	t += delta
	var vs := get_viewport().get_visible_rect().size
	match step:
		0:
			if t < 1.0:
				return
			for m in Game.level.monsters:
				m.process_mode = Node.PROCESS_MODE_DISABLED
			pl.invuln = 9999.0
			p0 = pl.global_position
			_touch(0, Vector2(230, 700), true)
			_next()
		1:
			_drag(0, Vector2(230 + clampf(t - 0.5, 0.0, 0.3) * 400, 700))
			if t > 1.7:
				_touch(0, Vector2(350, 700), false)
				_check("stick_moves_right", pl.global_position.x - p0.x > 80, str(pl.global_position - p0))
				_next()
		2:
			if t < 0.3:
				return
			p0 = pl.global_position
			var tgt := _screen(p0) + Vector2(-260, -120)
			if tgt.x < vs.x * 0.45:
				tgt = _screen(p0) + Vector2(260, -120)
			tap_at = tgt
			_touch(0, tgt, true)
			_touch(0, tgt, false)
			_next()
		3:
			if t < 0.15:
				return
			var mp := get_viewport().get_mouse_position()
			_check("mouse_at_finger", mp.distance_to(tap_at) < 2.0, "%s vs %s" % [mp, tap_at])
			_check("world_mouse", pl.mouse_world().distance_to(Game.main.screen_to_world(tap_at)) < 4.0, "%s vs %s" % [pl.mouse_world(), Game.main.screen_to_world(tap_at)])
			_check("tap_walks", pl.intent.get("type", "") == "move" or pl.path.size() > 0 or pl.global_position.distance_to(p0) > 10, str(pl.intent))
			_next()
		4:
			if t < 1.5:
				return
			for m in Game.level.monsters:
				m.process_mode = Node.PROCESS_MODE_INHERIT
			for m in Game.level.monsters:
				if not m.dead and (near == null or m.global_position.distance_to(pl.global_position) < near.global_position.distance_to(pl.global_position)):
					near = m
			if near:
				for k in 8:
					var spot := pl.global_position + Vector2.RIGHT.rotated(k * TAU / 8.0) * 120.0
					if Game.level.line_of_sight(pl.global_position, spot):
						near.global_position = spot
						break
				near.visible = true
			_touch(1, _attack_btn(), true)
			_next()
		5:
			if t < 0.3:
				return
			_check("attack_targets_monster", near == null or pl.intent.get("type", "") == "monster", "%s near=%s vis=%s tgt=%s los=%s" % [pl.intent, near, near.visible if near else null,
				Game.level._targetable(near) if near else null, Game.level.line_of_sight(pl.global_position, near.global_position) if near else null])
			_touch(1, _attack_btn(), false)
			_next()
		6:
			if t < 0.2:
				return
			_check("attack_release", not pl.pad_hold)
			Game.main.hud.toggle("inventory")
			_next()
		7:
			if t < 0.3:
				return
			var r: Control = Game.main.ui.right
			p0 = (r.get_global_transform() * Rect2(Vector2.ZERO, r.size)).get_center() * Game.main.ui_scale
			_touch(0, p0, true)
			_next()
		8:
			if t < 0.8:
				return
			_touch(0, p0, false)
			_check("long_press_right_click", rmb_seen)
			_next()
		9:
			if t < 0.2:
				return
			Game.main.ui.close_all()
			Game.ch.hp = 10.0
			pl.hp = 10.0
			for pressed in [true, false]:
				var k := InputEventKey.new()
				k.physical_keycode = KEY_1
				k.keycode = KEY_1
				k.pressed = pressed
				Input.parse_input_event(k)
			_next()
		10:
			if t < 0.6:
				return
			_check("belt_key_reaches_player", Game.ch.hp > 10.0, str(Game.ch.hp))
			print("TOUCH DONE fails=%d" % fails)
			get_tree().quit(1 if fails else 0)


func _attack_btn() -> Vector2:
	var pad: TouchPad = Game.main.pad
	return Vector2(pad.view.size.x - 150, pad.view.size.y - Game.main.hud.bar_h() - 122) * pad.scale.x


func _next() -> void:
	step += 1
	t = 0.0
