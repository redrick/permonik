class_name Summon
extends Node2D

# A hero's ally for a while. Without a "look" it is a flying spirit (the Firebird); with one it walks
# the ground in that monster's drawings (a golem, a wolf, an ancestor, a puppet) and strikes in melee.

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
var look := ""
var element := "fire"
var tex := {}
var col := Color("ff9a3a")


static func create(p: Player, id: String, pos: Vector2) -> Summon:
	var s := Summon.new()
	s.pl = p
	s.level = p.level
	s.skill_id = id
	s.life = float(Skills.p(id, "duration", 20.0))
	var d = Skills.p(id, "dmg", Vector2(5, 10))
	if d is Vector2:
		s.dmg = d
	var sk := DB.skill(id)
	s.look = str(sk.get("params", {}).get("look", ""))
	s.element = str(sk.get("element", "fire"))
	s.col = Fx.ELEM.get(s.element, Color("d8c8a0"))
	s.global_position = pos
	if s.look != "":
		p.level.ysort.add_child(s)
	else:
		p.level.fx_root.add_child(s)
	s._build()
	p.summons.append(s)
	return s


func _build() -> void:
	sprite = Sprite2D.new()
	var prm: Dictionary = DB.skill(skill_id).get("params", {})
	if look != "":
		for k in ["idle", "walk", "attack"]:
			var tx := DB.tex("sprites/monsters/%s_%s" % [look, k])
			if tx:
				tex[k] = tx
		var t0: Texture2D = tex.get("idle", Fx.soft())
		sprite.texture = t0
		sprite.offset = Vector2(0, -t0.get_height() / 2.0 + 8.0)
		sprite.scale = Vector2.ONE * float(prm.get("scale", 1.0))
		sprite.modulate = Color(str(prm.get("tint", "#ffffff")))
		var sh := Sprite2D.new()
		sh.texture = Actor.shadow_texture()
		sh.scale = Vector2(0.9, 0.5) * float(prm.get("scale", 1.0))
		add_child(sh)
		add_child(sprite)
		Fx.burst(level, global_position + Vector2(0, -40), col, 18, 120, 0.5, 0.3)
		return
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
		Fx.burst(level, global_position + Vector2(0, -40 if look != "" else -70), col, 16, 100, 0.5, 0.3, true)
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
	if look != "":
		_walk(delta)
		return
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
		Combat.player_spell_hit(pl, target, Combat.spell_damage(dmg, skill_id), element)
		Fx.burst(level, target.center_pos(), col, 10, 120, 0.4, 0.25)
		Sfx.play_at("fire_hit", global_position, 0.5)
	if int(t * 20) % 2 == 0:
		Fx.burst(level, global_position + Vector2(0, -70), Color("ffb050"), 1, 20, 0.4, 0.15, true)


# On foot: keep near the hero, close in on the nearest enemy, never through rock.
func _walk(delta: float) -> void:
	var side := Vector2(cos(t * 0.6 + get_instance_id() % 7), sin(t * 0.6 + get_instance_id() % 7)) * 60.0
	var goal := pl.global_position + side
	if target:
		goal = target.global_position
	var to := goal - global_position
	var reach := 58.0 + (target.radius if target else 0.0)
	var speed := 230.0 if to.length() > reach else 0.0
	var want := to.normalized() * speed
	vel = vel.lerp(want, 0.2)
	var step := vel * delta
	if not level.is_solid(global_position + step):
		global_position += step
	elif not level.is_solid(global_position + Vector2(step.x, 0)):
		global_position += Vector2(step.x, 0)
	elif not level.is_solid(global_position + Vector2(0, step.y)):
		global_position += Vector2(0, step.y)
	if global_position.distance_to(pl.global_position) > 700:
		global_position = pl.global_position + Vector2(randf_range(-40, 40), 20)
	if absf(vel.x) > 5:
		sprite.flip_h = vel.x < 0
	var moving := vel.length() > 20
	var want_tex: Texture2D = tex.get("walk" if moving and int(t * 5) % 2 == 0 else "idle", sprite.texture)
	if cd > 0.45 and tex.has("attack"):
		want_tex = tex.attack
	if want_tex and sprite.texture != want_tex:
		sprite.texture = want_tex
		sprite.offset = Vector2(0, -want_tex.get_height() / 2.0 + 8.0)
	if target and to.length() <= reach and cd <= 0.0:
		cd = 0.8
		Combat.player_spell_hit(pl, target, Combat.spell_damage(dmg, skill_id), element)
		Fx.burst(level, target.center_pos(), col, 8, 100, 0.35, 0.2)
		Sfx.play_at("hit_flesh" if element == "physical" else Skills.elem_sfx(element, false), global_position, 0.5)
