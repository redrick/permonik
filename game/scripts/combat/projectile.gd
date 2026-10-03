class_name Projectile
extends Node2D

var level: Node
var vel := Vector2.ZERO
var target_team := 1
var radius := 12.0
var life := 2.0
var pierce := 0
var hit_list: Array = []
var on_hit: Callable
var on_end: Callable
var returns := false
var owner_actor: Node2D
var returning := false
var spin := 0.0
var homing := 0.0
var bounce := 0
var height := 34.0
var sprite: Sprite2D
var light: PointLight2D
var trail_color := Color(0, 0, 0, 0)
var _trail_t := 0.0


static func spawn(lv: Node, from: Vector2, dir: Vector2, spd: float, fx_id: String, team: int, hit: Callable, color := Color(0, 0, 0, 0)) -> Projectile:
	var p := Projectile.new()
	p.level = lv
	p.vel = dir.normalized() * spd
	p.target_team = team
	p.on_hit = hit
	p.trail_color = color
	p.global_position = from
	lv.fx_root.add_child(p)
	p._build(fx_id, color)
	return p


func _build(fx_id: String, color: Color) -> void:
	sprite = Sprite2D.new()
	var t := DB.tex("sprites/fx/" + fx_id) if fx_id != "" else null
	if t:
		sprite.texture = t
	else:
		sprite.texture = Fx.soft()
		sprite.modulate = color if color.a > 0 else Color("ffe9b0")
		sprite.scale = Vector2(0.45, 0.45)
		var m := CanvasItemMaterial.new()
		m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
		sprite.material = m
	sprite.position = Vector2(0, -height)
	sprite.rotation = vel.angle()
	add_child(sprite)
	if color.a > 0:
		light = Fx.make_light(color, 110.0, 1.1)
		light.position = Vector2(0, -height)
		add_child(light)


func _physics_process(delta: float) -> void:
	life -= delta
	if life <= 0.0:
		_end()
		return
	if returning and is_instance_valid(owner_actor):
		var to := owner_actor.global_position - global_position
		vel = to.normalized() * vel.length()
		if to.length() < 30.0:
			queue_free()
			return
	elif homing > 0.0:
		var best: Node2D = null
		var bd := 260.0
		for a in level.actors_of_team(target_team):
			if a.dead or a in hit_list:
				continue
			var dd: float = a.global_position.distance_to(global_position)
			if dd < bd:
				bd = dd
				best = a
		if best:
			vel = vel.rotated(clampf(vel.angle_to(best.global_position - global_position), -homing * delta, homing * delta))
	var nxt := global_position + vel * delta
	if level.is_solid(nxt):
		if bounce > 0:
			bounce -= 1
			var c: Vector2i = level.to_cell(nxt)
			var cx: Vector2i = level.to_cell(Vector2(nxt.x, global_position.y))
			if level.is_solid_cell(cx):
				vel.x = -vel.x
			else:
				vel.y = -vel.y
			if c == Vector2i(-99, -99):
				pass
			Sfx.play_at("coin_bounce", global_position, 0.5)
		elif returns and not returning:
			returning = true
			hit_list.clear()
		else:
			_end()
			return
	else:
		global_position = nxt
	if spin != 0.0:
		sprite.rotation += spin * delta
	else:
		sprite.rotation = vel.angle()
	if trail_color.a > 0:
		_trail_t -= delta
		if _trail_t <= 0.0:
			_trail_t = 0.04
			Fx.burst(level, global_position + Vector2(0, -height), trail_color, 2, 30.0, 0.3, 0.18, true)
	for a in level.actors_of_team(target_team):
		if a.dead or a in hit_list:
			continue
		var c: Vector2 = a.global_position + Vector2(0, -a.sprite_h * 0.35)
		if c.distance_to(global_position + Vector2(0, -height * 0.5)) <= radius + a.radius + 8:
			hit_list.append(a)
			if on_hit.is_valid():
				on_hit.call(a, self)
			if pierce > 0:
				pierce -= 1
			elif returns and not returning:
				returning = true
			else:
				_end()
				return


func _end() -> void:
	if on_end.is_valid():
		on_end.call(self)
		on_end = Callable()
	queue_free()
