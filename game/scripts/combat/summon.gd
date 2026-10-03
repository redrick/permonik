class_name Summon
extends Node2D

var pl: Player
var level: Node
var skill_id := ""
var life := 20.0
var dmg := Vector2(5, 10)
var target: Actor
var cd := 0.0
var sprite: Sprite2D
var vel := Vector2.ZERO
var t := 0.0


static func create(p: Player, id: String, pos: Vector2) -> Summon:
	var s := Summon.new()
	s.pl = p
	s.level = p.level
	s.skill_id = id
	s.life = float(Skills.p(id, "duration", 20.0))
	var d = Skills.p(id, "dmg", Vector2(5, 10))
	if d is Vector2:
		s.dmg = d
	s.global_position = pos
	p.level.fx_root.add_child(s)
	s._build()
	p.summons.append(s)
	return s


func _build() -> void:
	sprite = Sprite2D.new()
	var tx := DB.tex("sprites/fx/zar_ptak")
	sprite.texture = tx if tx else Fx.soft()
	if tx == null:
		sprite.modulate = Color("ff9a3a")
	sprite.scale = Vector2.ONE * 0.6
	sprite.position = Vector2(0, -70)
	add_child(sprite)
	var l := Fx.make_light(Color("ffa04a"), 170.0, 1.0)
	l.position = Vector2(0, -70)
	add_child(l)


func _physics_process(delta: float) -> void:
	t += delta
	life -= delta
	cd -= delta
	if life <= 0.0 or not is_instance_valid(pl) or pl.dead:
		Fx.burst(level, global_position + Vector2(0, -70), Color("ff9a3a"), 16, 100, 0.5, 0.3, true)
		if is_instance_valid(pl):
			pl.summons.erase(self)
		queue_free()
		return
	if target == null or not is_instance_valid(target) or target.dead or target.global_position.distance_to(pl.global_position) > 600:
		target = null
		var bd := 480.0
		for m in level.actors_of_team(1):
			if m.dead:
				continue
			var dd: float = m.global_position.distance_to(global_position)
			if dd < bd:
				bd = dd
				target = m
	var goal := pl.global_position + Vector2(cos(t * 1.7), sin(t * 1.7)) * 70.0
	if target:
		goal = target.global_position
	var to := goal - global_position
	vel = vel.lerp(to.normalized() * minf(to.length() * 4.0, 360.0), 0.12)
	global_position += vel * delta
	sprite.flip_h = vel.x < 0
	sprite.position.y = -70 + sin(t * 6.0) * 6.0
	if target and to.length() < 60 and cd <= 0.0:
		cd = 0.7
		Combat.player_spell_hit(pl, target, Combat.spell_damage(dmg, skill_id), "fire")
		Fx.burst(level, target.center_pos(), Color("ff9a3a"), 10, 120, 0.4, 0.25)
		Sfx.play_at("fire_hit", global_position, 0.5)
	if int(t * 20) % 2 == 0:
		Fx.burst(level, global_position + Vector2(0, -70), Color("ffb050"), 1, 20, 0.4, 0.15, true)
