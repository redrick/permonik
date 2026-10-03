class_name Fx
extends RefCounted

const ELEM := {"physical": Color("e8dcc0"), "fire": Color("ff8a2a"), "lightning": Color("a8d8ff"),
	"cold": Color("9fe0ff"), "poison": Color("86e05a"), "holy": Color("ffe7a0"), "dark": Color("9a6bd8"),
	"soul": Color("cfe8ff")}

static var _soft: Texture2D
static var _ring: Texture2D
static var _light: Texture2D


static func soft() -> Texture2D:
	if _soft == null:
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.set_color(1, Color(1, 1, 1, 0))
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(1.0, 0.5)
		t.width = 64
		t.height = 64
		_soft = t
	return _soft


static func light_tex() -> Texture2D:
	if _light == null:
		var g := Gradient.new()
		g.offsets = PackedFloat32Array([0.0, 0.55, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(0.8, 0.8, 0.8, 0.55), Color(0, 0, 0, 0)])
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill = GradientTexture2D.FILL_RADIAL
		t.fill_from = Vector2(0.5, 0.5)
		t.fill_to = Vector2(1.0, 0.5)
		t.width = 256
		t.height = 256
		_light = t
	return _light


static func ring_tex() -> Texture2D:
	if _ring == null:
		var img := Image.create(128, 128, false, Image.FORMAT_RGBA8)
		for y in 128:
			for x in 128:
				var dd := Vector2(x - 63.5, y - 63.5).length() / 63.5
				var a := clampf(1.0 - absf(dd - 0.88) / 0.12, 0.0, 1.0)
				img.set_pixel(x, y, Color(1, 1, 1, a * a))
		_ring = ImageTexture.create_from_image(img)
	return _ring


static func make_light(color: Color, radius_px: float, energy := 1.0, shadows := false) -> PointLight2D:
	var l := PointLight2D.new()
	l.texture = light_tex()
	l.color = color
	l.energy = energy
	l.texture_scale = radius_px * 2.0 / 256.0
	l.shadow_enabled = shadows
	if shadows:
		l.shadow_filter = Light2D.SHADOW_FILTER_PCF5
		l.shadow_filter_smooth = 2.0
	return l


static func ring(level: Node, pos: Vector2, radius: float, color: Color, dur := 0.45) -> void:
	var s := Sprite2D.new()
	s.texture = ring_tex()
	s.modulate = color
	s.global_position = pos
	s.scale = Vector2.ONE * 0.1
	s.material = _add_mat()
	level.fx_root.add_child(s)
	var tw := s.create_tween().set_parallel(true)
	tw.tween_property(s, "scale", Vector2(radius / 64.0, radius / 64.0 * 0.6), dur).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(s, "modulate:a", 0.0, dur).set_ease(Tween.EASE_IN)
	tw.chain().tween_callback(s.queue_free)
	flash(level, pos, color, radius * 1.4, dur * 0.8)


static func _add_mat() -> CanvasItemMaterial:
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	return m


static func flash(level: Node, pos: Vector2, color: Color, radius: float, dur := 0.3, energy := 1.4) -> void:
	var l := make_light(color, radius, energy)
	l.global_position = pos
	level.fx_root.add_child(l)
	var tw := l.create_tween()
	tw.tween_property(l, "energy", 0.0, dur)
	tw.tween_callback(l.queue_free)


static func burst(level: Node, pos: Vector2, color: Color, amount := 16, spd := 160.0, life := 0.5, size := 0.25, up := false) -> void:
	var p := CPUParticles2D.new()
	p.texture = soft()
	p.material = _add_mat()
	p.one_shot = true
	p.emitting = false
	p.amount = amount
	p.lifetime = life
	p.explosiveness = 0.95
	p.spread = 180.0
	p.direction = Vector2.UP if up else Vector2.RIGHT
	p.initial_velocity_min = spd * 0.4
	p.initial_velocity_max = spd
	p.gravity = Vector2(0, -60) if up else Vector2(0, 120)
	p.damping_min = 40.0
	p.damping_max = 120.0
	p.scale_amount_min = size * 0.5
	p.scale_amount_max = size
	var g := Gradient.new()
	g.set_color(0, color)
	g.set_color(1, Color(color.r, color.g, color.b, 0.0))
	p.color_ramp = g
	p.global_position = pos
	level.fx_root.add_child(p)
	p.emitting = true
	level.get_tree().create_timer(life + 0.2).timeout.connect(p.queue_free)


static func bolt(level: Node, a: Vector2, b: Vector2, color := Color("bfe3ff"), width := 4.0, dur := 0.22) -> void:
	var line := Line2D.new()
	var n := maxi(3, int(a.distance_to(b) / 22.0))
	var perp := (b - a).normalized().orthogonal()
	for i in n + 1:
		var t := float(i) / n
		var off := 0.0 if i == 0 or i == n else randf_range(-14.0, 14.0)
		line.add_point(a.lerp(b, t) + perp * off)
	line.width = width
	line.default_color = color
	line.material = _add_mat()
	line.joint_mode = Line2D.LINE_JOINT_ROUND
	level.fx_root.add_child(line)
	var core := line.duplicate() as Line2D
	core.width = width * 0.4
	core.default_color = Color(1, 1, 1, 1)
	level.fx_root.add_child(core)
	for l in [line, core]:
		var tw: Tween = l.create_tween()
		tw.tween_property(l, "modulate:a", 0.0, dur)
		tw.tween_callback(l.queue_free)
	flash(level, b, color, 160.0, dur)


static func sky_strike(level: Node, pos: Vector2, color := Color("bfe3ff")) -> void:
	bolt(level, pos + Vector2(randf_range(-30, 30), -420), pos, color, 5.0, 0.3)
	burst(level, pos, color, 10, 140.0, 0.35, 0.2)


static func ground_mark(level: Node, pos: Vector2, radius: float, color: Color, dur: float) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = soft()
	s.modulate = Color(color.r, color.g, color.b, 0.35)
	s.scale = Vector2(radius / 32.0, radius / 32.0 * 0.55)
	s.global_position = pos
	s.material = _add_mat()
	s.z_index = -1
	level.fx_root.add_child(s)
	var tw := s.create_tween()
	tw.tween_interval(maxf(0.0, dur - 0.4))
	tw.tween_property(s, "modulate:a", 0.0, 0.4)
	tw.tween_callback(s.queue_free)
	return s


static func sprite_fx(level: Node, id: String, pos: Vector2, dur := 0.6, scale := 1.0, rise := 0.0) -> void:
	var t := DB.tex("sprites/fx/" + id)
	if t == null:
		return
	var s := Sprite2D.new()
	s.texture = t
	s.global_position = pos
	s.scale = Vector2.ONE * scale
	level.fx_root.add_child(s)
	var tw := s.create_tween().set_parallel(true)
	tw.tween_property(s, "modulate:a", 0.0, dur)
	if rise != 0.0:
		tw.tween_property(s, "position:y", s.position.y - rise, dur)
	tw.chain().tween_callback(s.queue_free)
