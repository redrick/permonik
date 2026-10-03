class_name AreaZone
extends Node2D

var level: Node
var pl: Player
var skill_id := ""
var elem := "fire"
var col := Color.WHITE
var radius := 100.0
var duration := 3.0
var tick := 0.5
var delay := 0.0
var dmg := Vector2(1, 3)
var t := 0.0
var tick_t := 0.0
var mode := "area"
var seg_a := Vector2.ZERO
var seg_b := Vector2.ZERO
var armed := true
var stun := 0.0
var effect := ""
var light: PointLight2D


static func _base(p: Player, id: String, pos: Vector2, e: String, c: Color) -> AreaZone:
	var z := AreaZone.new()
	z.pl = p
	z.level = p.level
	z.skill_id = id
	z.elem = e
	z.col = c
	z.global_position = pos
	var dv = Skills.p(id, "dmg", Vector2(2, 6))
	if dv is Vector2:
		z.dmg = dv
	p.level.fx_root.add_child(z)
	return z


static func create(p: Player, id: String, pos: Vector2, e: String, c: Color) -> AreaZone:
	var z := _base(p, id, pos, e, c)
	z.radius = float(Skills.p(id, "radius", 110.0))
	z.duration = float(Skills.p(id, "duration", 0.0))
	z.tick = maxf(0.15, float(Skills.p(id, "tick", 0.5)))
	z.delay = float(Skills.p(id, "delay", 0.0))
	if z.duration <= 0.0:
		z.duration = 0.01
		z.tick = 99.0
	z.tick_t = 0.0
	Fx.ground_mark(p.level, pos, z.radius, c, z.delay + z.duration + 0.3)
	if id == "odstrel" or id == "naloz":
		var s := Sprite2D.new()
		s.texture = DB.tex("sprites/fx/naloz")
		if s.texture:
			z.add_child(s)
	z.light = Fx.make_light(c, z.radius * 1.5, 0.5)
	z.add_child(z.light)
	return z


static func create_wall(p: Player, id: String, pos: Vector2, dir: Vector2, e: String, c: Color) -> AreaZone:
	var z := _base(p, id, pos, e, c)
	z.mode = "wall"
	var length := float(Skills.p(id, "length", 260.0))
	var perp := dir.orthogonal().normalized()
	if id == "doutnak":
		z.seg_a = p.global_position + dir * 40.0
		z.seg_b = p.global_position + dir * length
	else:
		z.seg_a = pos - perp * length / 2.0
		z.seg_b = pos + perp * length / 2.0
	z.global_position = Vector2.ZERO
	z.duration = float(Skills.p(id, "duration", 4.0))
	z.tick = 0.25
	z.radius = 34.0
	var n := int(z.seg_a.distance_to(z.seg_b) / 34.0) + 1
	for i in n:
		var fp: Vector2 = z.seg_a.lerp(z.seg_b, float(i) / maxf(1, n - 1))
		if p.level.is_solid(fp):
			continue
		var s := Sprite2D.new()
		var ft := DB.tex("sprites/fx/flame")
		s.texture = ft if ft else Fx.soft()
		if ft == null:
			s.modulate = c
			s.scale = Vector2(0.6, 1.0)
		s.position = fp + Vector2(0, -24)
		var m := CanvasItemMaterial.new()
		m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		s.material = m
		z.add_child(s)
		var tw := s.create_tween().set_loops()
		tw.tween_property(s, "scale:y", s.scale.y * 1.15, 0.15 + randf() * 0.1)
		tw.tween_property(s, "scale:y", s.scale.y, 0.15 + randf() * 0.1)
	z.light = Fx.make_light(c, z.seg_a.distance_to(z.seg_b) * 0.7 + 60.0, 0.8)
	z.light.position = (z.seg_a + z.seg_b) / 2.0
	z.add_child(z.light)
	return z


static func create_trap(p: Player, id: String, pos: Vector2, e: String, c: Color) -> AreaZone:
	var z := _base(p, id, pos, e, c)
	z.mode = "trap"
	z.radius = float(Skills.p(id, "radius", 60.0))
	z.duration = float(Skills.p(id, "duration", 20.0))
	z.stun = float(Skills.p(id, "stun", 0.0))
	var s := Sprite2D.new()
	var tx := DB.tex("sprites/fx/" + ("naloz" if e == "fire" else "web"))
	s.texture = tx if tx else Fx.soft()
	s.scale = Vector2.ONE * (0.8 if tx else 0.4)
	z.add_child(s)
	return z


static func create_cloud(p: Player, id: String, pos: Vector2) -> AreaZone:
	var z := _base(p, id, pos, "physical", Color("8a8a90"))
	z.mode = "cloud"
	z.radius = float(Skills.p(id, "radius", 120.0))
	z.duration = float(Skills.p(id, "duration", 5.0))
	z.effect = str(Skills.p(id, "effect", "blind"))
	z.tick = 0.3
	for i in 14:
		var s := Sprite2D.new()
		s.texture = Fx.soft()
		s.modulate = Color(0.55, 0.55, 0.6, 0.5)
		s.position = Vector2(randf_range(-z.radius, z.radius), randf_range(-z.radius, z.radius) * 0.6 - 30)
		s.scale = Vector2.ONE * randf_range(1.2, 2.2)
		z.add_child(s)
		var tw := s.create_tween().set_loops()
		tw.tween_property(s, "position:x", s.position.x + randf_range(-20, 20), 1.0 + randf())
		tw.tween_property(s, "position:x", s.position.x, 1.0 + randf())
	return z


func _physics_process(delta: float) -> void:
	if not is_instance_valid(pl):
		queue_free()
		return
	t += delta
	if t < delay:
		return
	if mode == "trap":
		_trap_tick()
	else:
		tick_t -= delta
		if tick_t <= 0.0:
			tick_t = tick
			_pulse()
	if t >= delay + duration:
		if light:
			light.energy = 0.0
		queue_free()


func _pulse() -> void:
	match mode:
		"area":
			if elem == "lightning":
				for i in 2:
					var sp := global_position + Vector2(randf_range(-radius, radius), randf_range(-radius, radius) * 0.6)
					Fx.sky_strike(level, sp, col)
				Sfx.play_at("lightning_hit", global_position, 0.6)
			elif elem == "fire":
				Fx.burst(level, global_position, col, 26, radius * 1.4, 0.6, 0.35, true)
				Fx.ring(level, global_position, radius, col, 0.4)
				Sfx.play_at("explosion" if skill_id == "odstrel" else "fire_hit", global_position, 0.8)
				if skill_id == "odstrel":
					level.shake(8.0)
			else:
				Fx.burst(level, global_position, col, 16, radius, 0.5, 0.3)
			for m in Combat.targets_in_radius(level, global_position, radius, 1):
				Combat.player_spell_hit(pl, m, Combat.spell_damage(dmg, skill_id), elem, {"no_stun": tick < 0.4})
		"wall":
			for m in level.actors_of_team(1):
				if m.dead:
					continue
				var cp := Geometry2D.get_closest_point_to_segment(m.global_position, seg_a, seg_b)
				if cp.distance_to(m.global_position) < radius + m.radius:
					Combat.player_spell_hit(pl, m, Combat.spell_damage(dmg, skill_id) * tick, elem, {"dot": true})
					m.apply_status("burn", 1.0, {"dps": dmg.x * 0.2, "src": pl})
		"cloud":
			for m in Combat.targets_in_radius(level, global_position, radius, 1):
				if effect == "blind":
					m.aggro = false
					m.path.clear()
					m.windup = 0.0
					m.apply_status("slow", 0.5)
				else:
					m.apply_status("slow", 0.5)


func _trap_tick() -> void:
	if not armed:
		return
	for m in Combat.targets_in_radius(level, global_position, radius * 0.6, 1):
		armed = false
		Sfx.play_at("trap_snap" if elem == "physical" else "explosion", global_position)
		Fx.ring(level, global_position, radius, col if elem != "physical" else Color("c8c0b0"))
		for v in Combat.targets_in_radius(level, global_position, radius, 1):
			Combat.player_spell_hit(pl, v, Combat.spell_damage(dmg, skill_id), elem, {"status": {"stun": stun} if stun > 0 else {}})
		duration = t - delay + 0.05
		return
