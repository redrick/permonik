class_name TouchPad
extends CanvasLayer

# Godot's mouse-from-touch emulation is off: each finger is classified here, and only the one acting as
# the mouse is turned into mouse events. Scheme: docs/touch-controls.md.

const INJECTED := 7301
const STICK_R := 110.0
const TAP_MOVE := 22.0
const AIM_START := 44.0
const LONG_PRESS := 0.55
const STICK_START := 12.0
const TAP_TIME := 0.3
const REPEAT_AFTER := 0.3
const NO_REPEAT := ["buff", "summon", "passive"]

static var active := false
static var buzz := true

var desktop_test := false
var font: Font
var view: Control
var buttons: Array = []
var touches := {}
var mouse_finger := -1
var stick_finger := -1
var stick_origin := Vector2.ZERO
var stick_vec := Vector2.ZERO
var show_items := false
var _last_tap := {"t": -10.0, "pos": Vector2.ZERO}
var _last_screen := Vector2.ZERO
var _ctx := ""
var _ctx_t := 0.0


static func wanted() -> bool:
	return OS.has_feature("mobile") or OS.has_feature("web_android") or OS.has_feature("web_ios") or Game.args.has("--touch")


func _ready() -> void:
	active = true
	layer = 35
	process_mode = Node.PROCESS_MODE_ALWAYS
	desktop_test = Game.args.has("--touch")
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	buzz = bool(cfg.get_value("main", "vibrate", true))
	Input.emulate_mouse_from_touch = false
	font = load("res://assets/fonts/TataHand.ttf")
	view = Control.new()
	view.set_anchors_preset(Control.PRESET_FULL_RECT)
	view.mouse_filter = Control.MOUSE_FILTER_IGNORE
	view.draw.connect(_draw_view)
	add_child(view)


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_WM_GO_BACK_REQUEST:
			_key(KEY_ESCAPE)
		NOTIFICATION_APPLICATION_FOCUS_OUT, NOTIFICATION_APPLICATION_PAUSED:
			for i in touches.keys():
				_on_touch(i, touches[i].pos, false, true)


# ---------------------------------------------------------------- state
func _ui() -> UiRoot:
	return Game.main.ui if Game.main else null


func _in_game() -> bool:
	var ui := _ui()
	var p: Player = Game.player
	return ui != null and p != null and is_instance_valid(p) and not p.dead and Game.main.hud.visible \
		and not Game.paused_ui and ui.screen == null and ui.slides == null and ui.modal == null


func _panels_open() -> bool:
	var ui := _ui()
	return ui.left != null or ui.right != null or ui.popup != null


func _over_ui(p: Vector2) -> bool:
	return Game.main != null and Game.main.over_ui_at(p)


func _stick_zone(p: Vector2) -> bool:
	var vs := view.size
	return p.x < vs.x * 0.5 and p.y > 110.0 and p.y < vs.y - _bar_h()


func _bar_h() -> float:
	return Game.main.hud.bar_h()


func _slot_skill(k: int) -> String:
	return Game.main.hud.skill_for_slot(k)


func _layout() -> void:
	buttons.clear()
	if not _in_game():
		return
	var vs := view.size
	var mm: Control = Game.main.hud.minimap
	if mm.visible:
		var r := mm.get_global_rect()
		buttons.append({"id": "map", "c": r.get_center(), "r": r.size.x / 2.0, "hidden": true})
	var am: Automap = Game.main.hud.automap
	if am.visible:
		var sr := am.sheet.get_global_rect()
		buttons.append({"id": "map", "c": sr.position + Vector2(50.0, 50.0), "r": 38.0})
	if _panels_open():
		return
	var top := ["pause", "items"]
	var at := Vector2(52, 52)
	var step := 84.0
	if Game.main.hud.phone():
		top = ["book", "pause", "items"]
		at = Vector2((mm.get_global_rect().position.x if mm.visible else vs.x) - 58.0, 52)
		step = -84.0
	if Game.level and not Game.level.is_town and _portal_scroll() != null:
		top.append("portal")
	for id in top:
		buttons.append({"id": id, "c": at, "r": 44.0 if id == "book" else 36.0})
		at.x += step
	var phone: bool = Game.main.hud.phone()
	var c := Vector2(vs.x - 185, vs.y - 150) if phone else Vector2(vs.x - 150, vs.y - _bar_h() - 122)
	buttons.append({"id": "attack", "c": c, "r": 70.0 if phone else 84.0})
	for k in 5:
		var a := deg_to_rad(175.0 + k * 27.5)
		buttons.append({"id": "skill", "arg": k, "c": c + Vector2(cos(a), sin(a)) * (168.0 if phone else 230.0), "r": 43.0 if phone else 50.0})
	var by := vs.y - 56 if phone else vs.y - _bar_h() - 40
	var px := vs.x - (400 if phone else 480)
	var pr := 36.0 if phone else 40.0
	buttons.append({"id": "potion", "arg": "heal", "c": Vector2(px, by), "r": pr})
	buttons.append({"id": "potion", "arg": "mana", "c": Vector2(px - pr * 2.4, by), "r": pr})


func _button_at(p: Vector2):
	for b in buttons:
		if p.distance_to(b.c) <= b.r * 1.12:
			return b
	return null


func _potion_slot(kind: String) -> int:
	var ch := Game.ch
	for key in ["heal_pct" if kind == "heal" else "mana_pct", "rejuv"]:
		for i in ch.belt_size():
			var it: Item = ch.belt[i]
			if it and it.base().get("use", {}).has(key):
				return i
	return -1


func _portal_scroll() -> Item:
	for it in Game.ch.inv.items:
		if it.base().get("use", {}).has("portal"):
			return it
	return null


# ---------------------------------------------------------------- raw input
func _input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		_on_touch(event.index, event.position / scale.x, event.pressed, event.canceled)
		get_viewport().set_input_as_handled()
	elif event is InputEventScreenDrag:
		_on_drag(event.index, event.position / scale.x)
		get_viewport().set_input_as_handled()
	elif desktop_test and event is InputEventMouse and event.device != INJECTED:
		if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
			_on_touch(0, event.position / scale.x, event.pressed, false)
		elif event is InputEventMouseMotion and event.button_mask & MOUSE_BUTTON_MASK_LEFT:
			_on_drag(0, event.position / scale.x)
		get_viewport().set_input_as_handled()


func _on_touch(i: int, p: Vector2, pressed: bool, canceled: bool) -> void:
	if pressed:
		if not touches.has(i):
			_begin(i, p)
	elif touches.has(i):
		var t: Dictionary = touches[i]
		touches.erase(i)
		t.pos = p
		_end(i, t, canceled)


func _begin(i: int, p: Vector2) -> void:
	var t := {"start": p, "pos": p, "t": _now(), "mode": ""}
	touches[i] = t
	_layout()
	if _in_game() and not _over_ui(p):
		var b = _button_at(p)
		if b:
			t.mode = "button"
			t.btn = b
			_press_button(t)
			return
		if stick_finger == -1 and _stick_zone(p):
			t.mode = "stick?"
			return
		if mouse_finger == -1:
			t.mode = "world"
			mouse_finger = i
			_mouse_move(p)
			_mouse_button(p, MOUSE_BUTTON_LEFT, true)
		return
	if mouse_finger == -1:
		t.mode = "ui"
		mouse_finger = i
		_mouse_move(p)


func _on_drag(i: int, p: Vector2) -> void:
	if not touches.has(i):
		return
	var t: Dictionary = touches[i]
	t.pos = p
	var moved := p.distance_to(t.start) > TAP_MOVE
	match t.mode:
		"stick?":
			if p.distance_to(t.start) > STICK_START:
				t.mode = "stick"
				stick_finger = i
				stick_origin = t.start
				_stick_update(p)
		"stick":
			_stick_update(p)
		"world":
			_mouse_move(p, MOUSE_BUTTON_MASK_LEFT)
		"ui":
			if not t.get("dragging", false) and not t.get("long", false) and moved:
				t.dragging = true
				t.slider = get_viewport().gui_get_hovered_control() is Range
				t.scroll_y = t.start.y
				if t.slider:
					_mouse_button(t.start, MOUSE_BUTTON_LEFT, true)
			if t.get("slider", false):
				_mouse_move(p, MOUSE_BUTTON_MASK_LEFT)
			else:
				_mouse_move(p)
				if t.get("dragging", false):
					while absf(p.y - t.scroll_y) >= 36.0:
						var up: bool = p.y > t.scroll_y
						t.scroll_y += 36.0 if up else -36.0
						_wheel(p, up)


func _end(i: int, t: Dictionary, canceled: bool) -> void:
	match t.mode:
		"stick?":
			if not canceled and mouse_finger == -1 and _now() - t.t < TAP_TIME:
				_mouse_move(t.start)
				_click(t.start, MOUSE_BUTTON_LEFT)
		"stick":
			stick_finger = -1
			stick_vec = Vector2.ZERO
			var pl: Player = Game.player
			if pl and is_instance_valid(pl) and pl.intent.get("type", "") == "stick":
				pl.intent = {}
		"button":
			_release_button(t, canceled)
		"world":
			_mouse_button(t.pos, MOUSE_BUTTON_LEFT, false)
		"ui":
			if canceled or t.get("long", false):
				pass
			elif t.get("slider", false):
				_mouse_button(t.pos, MOUSE_BUTTON_LEFT, false)
			elif not t.get("dragging", false):
				var now := _now()
				var dbl: bool = now - _last_tap.t < 0.4 and _last_tap.pos.distance_to(t.start) < 40.0
				_last_tap = {"t": -10.0 if dbl else now, "pos": t.start}
				_click(t.start, MOUSE_BUTTON_LEFT, dbl)
	if mouse_finger == i:
		mouse_finger = -1


func _stick_update(p: Vector2) -> void:
	var off := p - stick_origin
	if off.length() > STICK_R:
		stick_origin = p - off.normalized() * STICK_R
		off = p - stick_origin
	stick_vec = Vector2.ZERO if off.length() < STICK_START else off.normalized()


# ---------------------------------------------------------------- pad buttons
func _press_button(t: Dictionary) -> void:
	var b: Dictionary = t.btn
	var pl: Player = Game.player
	match b.id:
		"attack":
			pl.pad_hold = true
			pl.pad_attack(true)
		"potion":
			var s := _potion_slot(b.arg)
			if s >= 0:
				pl.use_belt(s)
		"portal":
			pl._use_portal_scroll()
		"items":
			show_items = not show_items
			if show_items:
				Input.action_press("show_items")
			else:
				Input.action_release("show_items")
		"map":
			Game.main.hud.toggle("automap")
		"book":
			Game.main.ui.toggle_panel("inventory")
	_vibrate(12)


func _hold_button(t: Dictionary) -> void:
	var b: Dictionary = t.btn
	var pl: Player = Game.player
	if pl == null or not is_instance_valid(pl):
		return
	match b.id:
		"attack":
			pl.pad_attack(false)
		"skill":
			var id := _slot_skill(b.arg)
			if not t.get("aiming", false) and t.pos.distance_to(b.c) > AIM_START:
				t.aiming = true
			if not t.get("aiming", false) and _now() - t.t > REPEAT_AFTER and _repeatable(id) and _ready_to_cast(id):
				pl.pad_skill(id)
				t.repeated = true


func _release_button(t: Dictionary, canceled: bool) -> void:
	var b: Dictionary = t.btn
	var pl: Player = Game.player
	if pl == null or not is_instance_valid(pl):
		return
	match b.id:
		"attack":
			pl.pad_hold = false
		"skill":
			var id := _slot_skill(b.arg)
			if canceled:
				return
			if id == "":
				Game.main.ui.open_skill_picker(b.arg)
			elif t.get("aiming", false):
				if t.pos.distance_to(b.c) > AIM_START:
					pl.pad_skill(id, _aim_world(b, t.pos))
			elif not t.get("repeated", false):
				pl.pad_skill(id)
		"pause":
			if not canceled:
				_key(KEY_ESCAPE)


func _vibrate(ms: int) -> void:
	if buzz:
		Input.vibrate_handheld(ms)


func _repeatable(id: String) -> bool:
	return str(DB.skill(id).get("type", "")) not in NO_REPEAT


func _ready_to_cast(id: String) -> bool:
	var pl: Player = Game.player
	return pl.action_t <= 0.0 and not pl.cooldowns.has(id) and (id == "utok" or Game.ch.mana >= Game.ch.skill_mana(id))


func _aim_world(b: Dictionary, finger: Vector2) -> Vector2:
	var a: Vector2 = finger - b.c
	var ps := _to_screen(Game.player.global_position)
	return _to_world(ps + a.normalized() * minf(a.length() * 3.0, 640.0))


# ---------------------------------------------------------------- per frame
func _process(_d: float) -> void:
	var playing := _in_game()
	var now := _now()
	for i in touches.keys():
		var t: Dictionary = touches[i]
		match t.mode:
			"ui":
				if not t.get("dragging", false) and not t.get("long", false) and now - t.t >= LONG_PRESS:
					t.long = true
					_click(t.start, MOUSE_BUTTON_RIGHT)
					_vibrate(30)
			"button":
				if playing:
					_hold_button(t)
	var pl: Player = Game.player
	if playing and stick_finger != -1 and stick_vec != Vector2.ZERO:
		pl.move_dir = stick_vec.normalized()
		if not pl.pad_hold and pl.action_t <= 0.0:
			pl.intent = {"type": "stick", "dir": stick_vec}
	if playing:
		_ctx_t -= _d
		if _ctx_t <= 0.0:
			_ctx_t = 0.2
			_ctx = _context(pl)
	_layout()
	view.queue_redraw()


func _context(pl: Player) -> String:
	if pl.auto_target() != null:
		return ""
	var n := pl.nearest_interactable()
	return "" if n.is_empty() else n.type


# ---------------------------------------------------------------- drawing
func _draw_view() -> void:
	var now := _now()
	for t in touches.values():
		if t.mode == "ui" and not t.get("dragging", false) and not t.get("long", false) and now - t.t > 0.15:
			var f := clampf((now - t.t - 0.15) / (LONG_PRESS - 0.15), 0.0, 1.0)
			view.draw_arc(t.start, 46.0, -PI / 2, -PI / 2 + TAU * f, 40, Color(UiTheme.GOLD, 0.85), 5.0)
	if not _in_game():
		return
	var pressed := {}
	for t in touches.values():
		if t.mode == "button":
			pressed[t.btn.id + str(t.btn.get("arg", ""))] = t
	for b in buttons:
		if b.get("hidden", false):
			continue
		_draw_button(b, pressed.has(b.id + str(b.get("arg", ""))))
	if stick_finger != -1:
		var t: Dictionary = touches.get(stick_finger, {})
		view.draw_circle(stick_origin, STICK_R, Color(0.05, 0.04, 0.04, 0.35))
		view.draw_arc(stick_origin, STICK_R, 0, TAU, 48, Color(UiTheme.GOLD, 0.5), 3.0)
		var knob: Vector2 = stick_origin + (t.get("pos", stick_origin) - stick_origin).limit_length(STICK_R)
		view.draw_circle(knob, 44.0, Color(UiTheme.GOLD, 0.45))
	for t in pressed.values():
		if t.btn.id == "skill" and t.get("aiming", false):
			var ps := _to_screen(Game.player.global_position)
			var tgt := _to_screen(_aim_world(t.btn, t.pos))
			var col := Color(UiTheme.GOLD, 0.8) if t.pos.distance_to(t.btn.c) > AIM_START else Color(UiTheme.RED, 0.8)
			view.draw_dashed_line(ps, tgt, col, 3.0, 14.0)
			view.draw_arc(tgt, 34.0, 0, TAU, 32, col, 4.0)


func _draw_button(b: Dictionary, down: bool) -> void:
	var c: Vector2 = b.c
	var r: float = b.r
	view.draw_circle(c, r, Color(0.05, 0.04, 0.04, 0.72 if down else 0.5))
	view.draw_arc(c, r, 0, TAU, 48, Color(UiTheme.GOLD, 0.95 if down else 0.6), 4.0 if down else 3.0)
	match b.id:
		"attack":
			if _ctx != "":
				var word := {"npc": {"cs": "Mluvit", "en": "Talk"}, "item": {"cs": "Vzít", "en": "Take"}, "prop": {"cs": "Použít", "en": "Use"}}
				_text(c, L.t(word[_ctx]), 30, UiTheme.INK)
			else:
				var w := Game.ch.weapon()
				if w:
					_icon(w.icon(), c, r * 1.25)
				else:
					_text(c, L.t({"cs": "Útok", "en": "Attack"}), 30, UiTheme.INK)
		"skill":
			var id := _slot_skill(b.arg)
			if id == "":
				_text(c, "+", 40, UiTheme.FAINT)
				return
			var t := DB.tex("ui/skills/" + id)
			if t:
				_icon(t, c, r * 1.35)
			else:
				_text(c, L.t(DB.skill(id).get("name", id)).left(6), 18, UiTheme.INK)
			var pl: Player = Game.player
			if pl.cooldowns.has(id):
				var cd := float(DB.skill(id).get("cooldown", 1))
				_pie(c, r - 3.0, clampf(pl.cooldowns[id] / maxf(0.1, cd), 0.0, 1.0), Color(0, 0, 0, 0.6))
			if id != "utok" and Game.ch.mana < Game.ch.skill_mana(id):
				view.draw_circle(c, r - 3.0, Color(0.1, 0.1, 0.5, 0.45))
		"potion":
			var s := _potion_slot(b.arg)
			if s < 0:
				view.draw_circle(c, r * 0.45, Color(Color("a01818") if b.arg == "heal" else Color("1838a0"), 0.4))
				return
			var it: Item = Game.ch.belt[s]
			_icon(it.icon(), c, r * 1.4)
			var n := 0
			for o in Game.ch.belt:
				if o and o.base_id == it.base_id:
					n += 1
			_text(c + Vector2(r * 0.55, r * 0.6), str(n), 22, UiTheme.INK)
		"portal":
			var it := _portal_scroll()
			if it:
				_icon(it.icon(), c, r * 1.4)
		"map":
			for d in [Vector2(1, 1), Vector2(1, -1)]:
				view.draw_line(c - d * 14.0, c + d * 14.0, UiTheme.INK, 4.0)
		"book":
			var col := UiTheme.INK
			var bag := Rect2(c + Vector2(-17, -8), Vector2(34, 26))
			view.draw_rect(bag, col, false, 3.0)
			view.draw_arc(c + Vector2(0, -8), 10.0, PI, TAU, 16, col, 3.0)
			view.draw_line(c + Vector2(-17, 1), c + Vector2(17, 1), col, 3.0)
			if Game.ch.stat_points > 0 or Game.ch.skill_points > 0:
				view.draw_circle(c + Vector2(r * 0.7, -r * 0.7), 9.0, UiTheme.GOLD)
		"pause":
			for k in 3:
				view.draw_line(c + Vector2(-15, -10 + k * 10), c + Vector2(15, -10 + k * 10), UiTheme.INK, 4.0)
		"items":
			var col := UiTheme.GOLD if show_items else UiTheme.DIM
			var pts := PackedVector2Array()
			for k in 33:
				var a := TAU * k / 32.0
				pts.append(c + Vector2(cos(a) * 20.0, sin(a) * 11.0))
			view.draw_polyline(pts, col, 3.0)
			view.draw_circle(c, 6.0, col)


func _icon(t: Texture2D, c: Vector2, box: float) -> void:
	if t == null:
		return
	var s := minf(box / t.get_width(), box / t.get_height())
	var sz := Vector2(t.get_width(), t.get_height()) * s
	view.draw_texture_rect(t, Rect2(c - sz / 2.0, sz), false)


func _text(c: Vector2, s: String, size: int, col: Color) -> void:
	var w := font.get_string_size(s, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
	var pos := c + Vector2(-w / 2.0, size * 0.35)
	view.draw_string_outline(font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, 6, Color.BLACK)
	view.draw_string(font, pos, s, HORIZONTAL_ALIGNMENT_LEFT, -1, size, col)


func _pie(c: Vector2, r: float, frac: float, col: Color) -> void:
	if frac <= 0.0:
		return
	var pts := PackedVector2Array([c])
	for k in 33:
		var a := -PI / 2 + TAU * frac * k / 32.0
		pts.append(c + Vector2(cos(a), sin(a)) * r)
	view.draw_colored_polygon(pts, col)


# ---------------------------------------------------------------- synthesised events
func _now() -> float:
	return Time.get_ticks_msec() / 1000.0


func _to_screen(world: Vector2) -> Vector2:
	return Game.main.world_to_screen(world) / scale.x


func _to_world(p: Vector2) -> Vector2:
	return Game.main.screen_to_world(p * scale.x)


# Positions here are in this layer's scaled space; Input.parse_input_event takes window coordinates.
func _window(p: Vector2) -> Vector2:
	return get_viewport().get_screen_transform() * (p * scale.x)


func _mouse_move(p: Vector2, mask := 0) -> void:
	var e := InputEventMouseMotion.new()
	e.device = INJECTED
	var s := _window(p)
	e.position = s
	e.global_position = s
	e.relative = s - _last_screen
	e.button_mask = mask
	_last_screen = s
	Input.parse_input_event(e)


func _mouse_button(p: Vector2, button: MouseButton, pressed: bool, dbl := false) -> void:
	var e := InputEventMouseButton.new()
	e.device = INJECTED
	var s := _window(p)
	e.position = s
	e.global_position = s
	e.button_index = button
	e.pressed = pressed
	e.double_click = dbl
	e.factor = 1.0
	if pressed and button == MOUSE_BUTTON_LEFT:
		e.button_mask = MOUSE_BUTTON_MASK_LEFT
	elif pressed and button == MOUSE_BUTTON_RIGHT:
		e.button_mask = MOUSE_BUTTON_MASK_RIGHT
	Input.parse_input_event(e)


func _click(p: Vector2, button: MouseButton, dbl := false) -> void:
	_mouse_button(p, button, true, dbl)
	_mouse_button(p, button, false)


func _wheel(p: Vector2, up: bool) -> void:
	_click(p, MOUSE_BUTTON_WHEEL_UP if up else MOUSE_BUTTON_WHEEL_DOWN)


func _key(k: Key) -> void:
	for pressed in [true, false]:
		var e := InputEventKey.new()
		e.keycode = k
		e.physical_keycode = k
		e.pressed = pressed
		Input.parse_input_event(e)
