class_name UiCinema
extends Control

# Cut-out cinematics: pencil layers from art/cinema.py moved by a parallax camera, with line boil,
# lamp glows, drifting particles and narration in the letterbox. Choreography lives in CinFilms.

const BAR := 0.11

static var _man := {}
static var _texs := {}
static var _soft: Texture2D
static var _add: CanvasItemMaterial

var film := ""
var done: Callable
var shots: Array = []
var idx := -1
var canvas := Vector2(1920, 1080)
var cam_pos := Vector2(960, 540)
var cam_zoom := 1.0
var shake_amp := 0.0
var busy := true
var finished := false

var stage: Node2D
var black: ColorRect
var iris: ColorRect
var sub: Label
var card: Label
var _layers: Array = []
var _flicker: Array = []
var _tweens: Array = []
var _films := CinFilms.new()
var _shot := 0
var _t := 0.0
var _boil_t := 0.0
var _step_t := 0.0
var _text_end := 0.0
var _voice_free := 0.0
var _music_before := ""


static func manifest() -> Dictionary:
	if _man.is_empty():
		var d = JSON.parse_string(FileAccess.get_file_as_string("res://data/cinema_layers.json"))
		_man = d if d is Dictionary else {}
	return _man


static func tex(name: String) -> Texture2D:
	if not _texs.has(name):
		var p := "res://assets/cinema/%s.webp" % name
		_texs[name] = load(p) if ResourceLoader.exists(p) else null
	return _texs[name]


static func seen() -> Array:
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	return cfg.get_value("cinema", "seen", [])


static func mark_seen(id: String) -> void:
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	var s: Array = cfg.get_value("cinema", "seen", [])
	if not s.has(id):
		s.append(id)
		cfg.set_value("cinema", "seen", s)
		cfg.save("user://settings.cfg")


static func soft_tex() -> Texture2D:
	if _soft == null:
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.set_color(1, Color(1, 1, 1, 0))
		g.add_point(0.2, Color(1, 1, 1, 0.6))
		g.add_point(0.5, Color(1, 1, 1, 0.18))
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(0.5, 0.0)
		t.width = 256
		t.height = 256
		_soft = t
	return _soft


static func add_mat() -> CanvasItemMaterial:
	if _add == null:
		_add = CanvasItemMaterial.new()
		_add.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	return _add


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	mouse_filter = Control.MOUSE_FILTER_STOP
	clip_contents = true
	var bg := ColorRect.new()
	bg.color = Color(0, 0, 0, 1)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	stage = Node2D.new()
	add_child(stage)
	add_child(_shade(0.62, 0.55, 0.55))
	iris = _shade(3.0, 0.2, 1.0)
	add_child(iris)
	for top in [true, false]:
		var bar := ColorRect.new()
		bar.color = Color(0, 0, 0, 1)
		bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bar.anchor_right = 1
		bar.anchor_top = 0.0 if top else 1.0 - BAR
		bar.anchor_bottom = BAR if top else 1.0
		add_child(bar)
	sub = UiTheme.label("", 32, Color("f2e8d2"))
	sub.add_theme_constant_override("outline_size", 6)
	sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	sub.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	sub.anchor_left = 0.12
	sub.anchor_right = 0.88
	sub.anchor_top = 1.0 - BAR - 0.035
	sub.anchor_bottom = 1.0 - 0.01
	sub.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(sub)
	card = UiTheme.title("", 72)
	card.add_theme_constant_override("outline_size", 10)
	card.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	card.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	card.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	card.set_anchors_preset(Control.PRESET_FULL_RECT)
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	card.modulate.a = 0.0
	add_child(card)
	UiTheme.skip_label(self)
	black = ColorRect.new()
	black.color = Color(0, 0, 0, 1)
	black.set_anchors_preset(Control.PRESET_FULL_RECT)
	black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(black)
	shots = _films.shots(film)
	mark_seen(film)
	_music_before = Sfx._music_id
	var mus := str(DB.cinema.get(film, {}).get("music", ""))
	if mus != "":
		Sfx.music(mus)
	_start(0)


func _shade(radius: float, soft: float, alpha: float) -> ColorRect:
	var r := ColorRect.new()
	r.set_anchors_preset(Control.PRESET_FULL_RECT)
	r.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sh := Shader.new()
	sh.code = "shader_type canvas_item;
uniform vec2 center = vec2(0.5);
uniform float radius = 0.6;
uniform float soft = 0.5;
uniform float alpha = 0.5;
uniform float aspect = 1.7778;
void fragment() {
	vec2 d = (UV - center) * vec2(aspect, 1.0);
	COLOR = vec4(0.0, 0.0, 0.0, alpha * smoothstep(radius, radius + soft, length(d)));
}"
	var m := ShaderMaterial.new()
	m.shader = sh
	m.set_shader_parameter("radius", radius)
	m.set_shader_parameter("soft", soft)
	m.set_shader_parameter("alpha", alpha)
	r.material = m
	return r


func _process(delta: float) -> void:
	_t += delta
	_boil_t += delta
	_step_t += delta
	var boil_tick := _boil_t >= 0.125
	var step_tick := _step_t >= 1.0 / 12.0
	if boil_tick:
		_boil_t = 0.0
	if step_tick:
		_step_t = 0.0
	var fit := maxf(size.x / 1920.0, size.y / 1080.0)
	var sc := size / 2.0
	if shake_amp > 0.0:
		sc += Vector2(randf_range(-1, 1), randf_range(-1, 1)) * shake_amp * fit
	var half := size / (2.0 * fit * cam_zoom) * Vector2(1.0, 1.0 - 2.0 * BAR)
	var cam := cam_pos
	if canvas.x > half.x * 2.0:
		cam.x = clampf(cam.x, half.x, canvas.x - half.x)
	if canvas.y > half.y * 2.0:
		cam.y = clampf(cam.y, half.y, canvas.y - half.y)
	for l in _layers:
		if is_instance_valid(l):
			l.apply(sc, cam, cam_zoom, fit, canvas, _t, boil_tick, step_tick)
	for f in _flicker:
		var s: Sprite2D = f[0]
		if is_instance_valid(s):
			var n := sin(_t * 7.3 + f[3]) * 0.5 + sin(_t * 13.1 + f[3] * 2.0) * 0.3 + sin(_t * 2.1 + f[3]) * 0.2
			s.modulate.a = f[1] * (1.0 + f[2] * n)
	for c in get_children():
		if c is ColorRect and c.material is ShaderMaterial:
			(c.material as ShaderMaterial).set_shader_parameter("aspect", size.x / maxf(size.y, 1.0))


# ---------------------------------------------------------------- flow
func _start(i: int) -> void:
	_shot += 1
	_clear()
	idx = i
	if i >= shots.size():
		_finish()
		return
	canvas = Vector2(1920, 1080)
	cam_pos = canvas / 2.0
	cam_zoom = 1.0
	shake_amp = 0.0
	_t = 0.0
	_text_end = 0.0
	_voice_free = 0.0
	var s: Array = shots[i]
	s[1].call(self)
	var dur := maxf(float(s[0]), _text_end + 1.0)
	busy = true
	var tw := create_tween()
	tw.tween_property(black, "color:a", 0.0, 0.8)
	tw.tween_callback(func(): busy = false)
	var tok := _shot
	get_tree().create_timer(dur - 0.7, true).timeout.connect(func():
		if tok == _shot:
			_end(0.7))


func _end(fade: float) -> void:
	busy = true
	var tok := _shot
	var tw := create_tween()
	tw.tween_property(black, "color:a", 1.0, fade)
	tw.tween_callback(func():
		if tok == _shot:
			_start(idx + 1))


func _clear() -> void:
	for t in _tweens:
		if t.is_valid():
			t.kill()
	_tweens.clear()
	for c in stage.get_children():
		c.queue_free()
	_layers.clear()
	_flicker.clear()
	sub.text = ""
	card.text = ""
	card.modulate.a = 0.0
	(iris.material as ShaderMaterial).set_shader_parameter("radius", 3.0)


func advance() -> void:
	if busy or finished:
		return
	_end(0.35)


func skip_all() -> void:
	if finished:
		return
	Sfx.stop_voice()
	_shot += 1
	idx = shots.size()
	busy = true
	var tw := create_tween()
	tw.tween_property(black, "color:a", 1.0, 0.3)
	tw.tween_callback(_finish)


func _finish() -> void:
	if finished:
		return
	finished = true
	Sfx.stop_voice()
	_clear()
	_texs.clear()
	# in a game whatever comes next (a new place, the next film) picks its own music
	if _music_before != "" and not done.is_valid():
		Sfx.music(_music_before)
	UiRoot.inst.slides_finished(self, done)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		accept_event()
		advance()


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k and k.pressed and not k.echo and k.keycode in [KEY_SPACE, KEY_ENTER, KEY_KP_ENTER]:
		get_viewport().set_input_as_handled()
		advance()


# ---------------------------------------------------------------- building blocks for CinFilms
func tw() -> Tween:
	var t := create_tween()
	_tweens.append(t)
	return t


func at(t: float, fn: Callable) -> void:
	var tok := _shot
	get_tree().create_timer(maxf(t, 0.01), true).timeout.connect(func():
		if tok == _shot:
			fn.call())


func pt(name: String, key: String) -> Vector2:
	var p = manifest().get(name, {}).get("pts", {}).get(key, [0, 0])
	return Vector2(p[0], p[1])


func pts(name: String, key: String) -> Array:
	var out := []
	for p in manifest().get(name, {}).get("pts", {}).get(key, []):
		out.append(Vector2(p[0], p[1]))
	return out


func _holder(pivot: Vector2, depth: float) -> CinLayer:
	var l := CinLayer.new()
	l.depth = depth
	l.pivot = pivot
	stage.add_child(l)
	_layers.append(l)
	return l


func layer(name: String, depth := 1.0, boil := 0.0) -> CinLayer:
	var m: Dictionary = manifest().get(name, {})
	var tl := Vector2(m.get("x", 0), m.get("y", 0))
	var p = m.get("pts", {}).get("pivot", null)
	var l := _holder(Vector2(p[0], p[1]) if p else tl + Vector2(m.get("w", 0), m.get("h", 0)) / 2.0, depth)
	l.boil = boil
	l.add_frame(tex(name), tl)
	return l


func frame(l: CinLayer, name: String) -> int:
	var m: Dictionary = manifest().get(name, {})
	return l.add_frame(tex(name), Vector2(m.get("x", 0), m.get("y", 0)))


func sprite(t: Texture2D, center: Vector2, depth := 1.0, s := 1.0) -> CinLayer:
	var l := _holder(center, depth)
	if t:
		l.add_frame(t, center - t.get_size() / 2.0)
	l.scl = Vector2.ONE * s
	return l


# A soft additive light hung on a layer (or alone at a canvas point when l is null).
func glow(l: CinLayer, at_pt: Vector2, radius: float, col: Color, alpha := 0.5, flicker := 0.0, depth := 1.0) -> Sprite2D:
	if l == null:
		l = _holder(at_pt, depth)
	var s := Sprite2D.new()
	s.texture = soft_tex()
	s.material = add_mat()
	s.position = at_pt - l.pivot
	s.scale = Vector2.ONE * radius / 128.0
	s.modulate = Color(col, alpha)
	l.add_child(s)
	if flicker > 0.0:
		_flicker.append([s, alpha, flicker, randf() * TAU])
	return s


func glow_alpha(s: Sprite2D, to: float, dur: float, delay := 0.0) -> void:
	for f in _flicker:
		if f[0] == s:
			var t := tw()
			if delay > 0.0:
				t.tween_interval(delay)
			t.tween_method(func(v): f[1] = v, f[1], to, dur)
			return
	var t := tw()
	if delay > 0.0:
		t.tween_interval(delay)
	t.tween_property(s, "modulate:a", to, dur)


func cam_to(p: Vector2, zoom: float, dur: float, delay := 0.0, trans := Tween.TRANS_SINE) -> void:
	var t := tw().set_parallel()
	t.tween_property(self, "cam_pos", p, dur).set_delay(delay).set_trans(trans).set_ease(Tween.EASE_IN_OUT)
	t.tween_property(self, "cam_zoom", zoom, dur).set_delay(delay).set_trans(trans).set_ease(Tween.EASE_IN_OUT)


func move(l: CinLayer, to: Vector2, dur: float, delay := 0.0, trans := Tween.TRANS_SINE, ease := Tween.EASE_IN_OUT) -> void:
	tw().tween_property(l, "pos", to, dur).set_delay(delay).set_trans(trans).set_ease(ease)


func fade(n: CanvasItem, to: float, dur: float, delay := 0.0) -> void:
	tw().tween_property(n, "modulate:a", to, dur).set_delay(delay)


func prop(o: Object, p: String, to, dur: float, delay := 0.0, trans := Tween.TRANS_SINE, ease := Tween.EASE_IN_OUT) -> void:
	tw().tween_property(o, p, to, dur).set_delay(delay).set_trans(trans).set_ease(ease)


func walk(ls: Array, from: Vector2, to: Vector2, dur: float, delay := 0.0, hop := 6.0, rate := 2.2) -> void:
	for l in ls:
		l.pos = from
		l.step = true
		move(l, to, dur, delay, Tween.TRANS_LINEAR)
	at(delay, func():
		for l in ls:
			l.bob = hop
			l.bob_rate = rate)
	at(delay + dur, func():
		for l in ls:
			l.bob = 0.0)


func shake(t: float, dur: float, amp: float) -> void:
	at(t, func():
		shake_amp = amp
		prop(self, "shake_amp", 0.0, dur, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN))


func rumble(amp: float) -> void:
	shake_amp = amp


func flash(t: float, col: Color, dur: float) -> void:
	at(t, func():
		var r := ColorRect.new()
		r.color = col
		r.mouse_filter = Control.MOUSE_FILTER_IGNORE
		r.set_anchors_preset(Control.PRESET_FULL_RECT)
		add_child(r)
		move_child(r, black.get_index())
		var tt := create_tween()
		tt.tween_property(r, "color:a", 0.0, dur)
		tt.tween_callback(r.queue_free))


# Closes the dark in around a screen point (UV), like the lamp going out of reach.
func dark_in(center_uv: Vector2, from_r: float, to_r: float, dur: float, delay := 0.0) -> void:
	var m: ShaderMaterial = iris.material
	m.set_shader_parameter("center", center_uv)
	m.set_shader_parameter("radius", from_r)
	tw().tween_method(func(v): m.set_shader_parameter("radius", v), from_r, to_r, dur).set_delay(delay).set_trans(Tween.TRANS_SINE)


func sfx(id: String, t: float, vol := 1.0) -> void:
	at(t, func(): Sfx.play(id, vol, 0.02))


func line(key: String) -> String:
	return L.t(DB.cinema.get(film, {}).get("lines", {}).get(key, key))


# Narration in the bottom bar; returns when it is gone so the next line can follow.
# A narrated line starts no earlier than the one before it has finished speaking, and the shot lasts
# until the voice is done (see _start).
func say(key: String, t: float, dur := 0.0) -> float:
	var text := line(key)
	var raw = DB.cinema.get(film, {}).get("lines", {}).get(key, null)
	var vs: AudioStream = Sfx.voice_stream("narrator", raw) if raw is Dictionary else null
	var vlen := vs.get_length() if vs else 0.0
	if dur <= 0.0:
		dur = clampf(text.length() / 15.0 + 1.4, 3.5, 14.0)
	if vlen > 0.0:
		t = maxf(t, _voice_free)
		dur = maxf(dur, vlen + 0.8)
		_voice_free = t + vlen + 0.4
	_text_end = maxf(_text_end, t + dur)
	at(t, func():
		if vlen > 0.0:
			Sfx.voice("narrator", raw)
		if Game.args.has("--cine-log"):
			print("CINE_SAY %s %s %d" % [film, key, Engine.get_frames_drawn()])
		sub.text = text
		sub.visible_ratio = 0.0
		sub.modulate.a = 1.0
		var tt := tw()
		tt.tween_property(sub, "visible_ratio", 1.0, clampf(text.length() / 40.0, 0.5, 4.0))
		tt.tween_interval(maxf(dur - text.length() / 40.0 - 0.6, 0.5))
		tt.tween_property(sub, "modulate:a", 0.0, 0.6))
	return t + dur


func title_card(key: String, t: float, dur: float, px := 72) -> float:
	_text_end = maxf(_text_end, t + dur)
	at(t, func():
		card.text = line(key)
		card.add_theme_font_size_override("font_size", px)
		var tt := tw()
		tt.tween_property(card, "modulate:a", 1.0, 1.2)
		tt.tween_interval(maxf(dur - 2.4, 0.3))
		tt.tween_property(card, "modulate:a", 0.0, 1.2))
	return t + dur


# Drifting particles in canvas px, carried by the camera at the given depth.
func particles(kind: String, area: Rect2, depth := 1.0, amount := 0, col := Color()) -> CPUParticles2D:
	var h := _holder(Vector2.ZERO, depth)
	var p := CPUParticles2D.new()
	p.local_coords = true
	p.texture = soft_tex()
	p.position = area.get_center()
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.emission_rect_extents = area.size / 2.0
	p.direction = Vector2(0, -1)
	var ramp := Gradient.new()
	ramp.set_color(0, Color(1, 1, 1, 0))
	ramp.set_color(1, Color(1, 1, 1, 0))
	ramp.add_point(0.2, Color(1, 1, 1, 1))
	ramp.add_point(0.75, Color(1, 1, 1, 0.8))
	p.color_ramp = ramp
	match kind:
		"mist":
			p.amount = amount if amount > 0 else 14
			p.lifetime = 16.0
			p.preprocess = 16.0
			p.spread = 20.0
			p.direction = Vector2(1, 0)
			p.initial_velocity_min = 8.0
			p.initial_velocity_max = 26.0
			p.gravity = Vector2.ZERO
			p.scale_amount_min = 2.5
			p.scale_amount_max = 5.0
			p.color = col if col != Color() else Color(0.75, 0.7, 0.8, 0.07)
		"dust":
			p.amount = amount if amount > 0 else 70
			p.lifetime = 4.0
			p.preprocess = 4.0
			p.direction = Vector2(0, 1)
			p.spread = 15.0
			p.initial_velocity_min = 30.0
			p.initial_velocity_max = 90.0
			p.gravity = Vector2(0, 120)
			p.scale_amount_min = 0.02
			p.scale_amount_max = 0.06
			p.color = col if col != Color() else Color(0.75, 0.62, 0.5, 0.7)
		"embers":
			p.amount = amount if amount > 0 else 40
			p.lifetime = 5.0
			p.preprocess = 5.0
			p.spread = 30.0
			p.initial_velocity_min = 20.0
			p.initial_velocity_max = 60.0
			p.gravity = Vector2(6, -25)
			p.scale_amount_min = 0.025
			p.scale_amount_max = 0.06
			p.material = add_mat()
			p.color = col if col != Color() else Color(1.0, 0.55, 0.2, 0.9)
		"motes":
			p.amount = amount if amount > 0 else 30
			p.lifetime = 9.0
			p.preprocess = 9.0
			p.spread = 180.0
			p.initial_velocity_min = 3.0
			p.initial_velocity_max = 14.0
			p.gravity = Vector2(0, -3)
			p.scale_amount_min = 0.02
			p.scale_amount_max = 0.05
			p.material = add_mat()
			p.color = col if col != Color() else Color(0.75, 0.9, 1.0, 0.6)
		"bubbles":
			p.amount = amount if amount > 0 else 30
			p.lifetime = 4.0
			p.preprocess = 4.0
			p.spread = 12.0
			p.initial_velocity_min = 30.0
			p.initial_velocity_max = 70.0
			p.gravity = Vector2(0, -20)
			p.scale_amount_min = 0.03
			p.scale_amount_max = 0.07
			p.material = add_mat()
			p.color = col if col != Color() else Color(0.7, 0.9, 1.0, 0.5)
		"smoke":
			p.amount = amount if amount > 0 else 24
			p.lifetime = 6.0
			p.preprocess = 6.0
			p.spread = 18.0
			p.initial_velocity_min = 18.0
			p.initial_velocity_max = 30.0
			p.gravity = Vector2(14, -4)
			p.scale_amount_min = 0.15
			p.scale_amount_max = 0.3
			var c := Curve.new()
			c.add_point(Vector2(0, 0.3))
			c.add_point(Vector2(1, 1.6))
			p.scale_amount_curve = c
			p.color = col if col != Color() else Color(0.8, 0.83, 0.86, 0.22)
	h.add_child(p)
	return p
