extends BossBase

const EARTH := Color("b09a70")
const EYE := Color("ff4a2a")

var closed_tex := {}
var open_tex := {}
var eyes_open := false
var lift_t := 0.0
var call_t := 3.0
var gaze_tick := 0.0
var gaze_warm := 0.0
var beam: Line2D


func _init_boss() -> void:
	closed_tex = tex.duplicate()
	var ot := DB.tex("sprites/monsters/vij_open")
	open_tex = {"idle": ot, "walk": ot, "attack": ot} if ot else closed_tex
	set_meta("hit_sfx", "hit_stone")
	beam = Line2D.new()
	beam.width = 10.0
	beam.default_color = Color(EYE.r, EYE.g, EYE.b, 0.0)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	beam.material = m
	beam.add_point(Vector2.ZERO)
	beam.add_point(Vector2.ZERO)
	level.fx_root.add_child(beam)


func _exit_tree() -> void:
	if is_instance_valid(beam):
		beam.queue_free()


func lifters() -> Array:
	return alive_minions().filter(func(m): return m.get("holding") != null)


func holding_count() -> int:
	return lifters().filter(func(m): return m.holding).size()


func _always_tick(delta: float) -> void:
	if not aggro:
		return
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
	var holders := holding_count()
	if not eyes_open:
		beam.default_color.a = 0.0
		if holders > 0:
			lift_t += delta
			if int(lift_t * 2.0) != int((lift_t - delta) * 2.0):
				shout("…", "…", Color("d8c8a0"))
			if lift_t >= 4.0:
				_open_eyes()
		else:
			lift_t = maxf(0.0, lift_t - delta)
		call_t -= delta
		if call_t <= 0.0 and lifters().size() == 0:
			call_t = 11.0 if phase == 1 else 8.0
			_call_lifters()
	else:
		if holders == 0:
			_close_eyes()
		else:
			_gaze(delta)


func _call_lifters() -> void:
	shout("Zvedněte mi víčka!", "Lift up my eyelids!", Color("d8c8a0"))
	Sfx.play_at("ghost_wail", global_position, 0.7)
	var n := 2 if phase == 1 else 3
	for i in n:
		var q := open_spot_near(global_position, 320.0, 460.0)
		var mid := "bes" if i % 2 == 0 else "navka"
		var m := spawn_custom("res://scripts/actors/bosses/minion_lifter.gd", mid, q, maxi(1, mlvl - 3))
		m.set("master", self)
		m.set("spot", Vector2(-radius - 30.0 if i % 2 == 0 else radius + 30.0, 10.0 + i * 12.0))
		m.minion_of = self
		m.summoner = self
		m.no_drops = true
		m.xp_value = int(m.xp_value * 0.4)
		Fx.burst(level, q + Vector2(0, -40), Color("6b4ea0"), 14, 110.0)


func _open_eyes() -> void:
	eyes_open = true
	gaze_warm = 1.0
	tex = open_tex
	sprite.texture = null
	set_pose("idle")
	Sfx.play_at("boss_roar", global_position)
	level.shake(8.0)
	if not get_meta("half_said", false) or randf() < 0.3:
		say("half")
		set_meta("half_said", true)
	else:
		shout("VIDÍM TĚ!", "I SEE YOU!", EYE)


func _close_eyes() -> void:
	eyes_open = false
	lift_t = 0.0
	call_t = 6.0
	tex = closed_tex
	sprite.texture = null
	set_pose("idle")
	beam.default_color.a = 0.0
	shout("Tma…", "Darkness…", EARTH)
	Sfx.play_at("hit_stone", global_position, 0.8)


func _gaze(delta: float) -> void:
	var p := pl()
	var eye := global_position + Vector2(0, -sprite_h * 0.7)
	beam.set_point_position(0, eye)
	if p == null:
		return
	face_to(p.global_position)
	var los: bool = level.line_of_sight(global_position, p.global_position) and p.global_position.distance_to(global_position) < 900.0
	if not los:
		beam.default_color.a = 0.05
		beam.set_point_position(1, eye)
		return
	beam.set_point_position(1, p.global_position + Vector2(0, -50))
	if gaze_warm > 0.0:
		gaze_warm -= delta
		beam.width = 3.0
		beam.default_color = Color(EYE.r, EYE.g, EYE.b, 0.25)
		return
	beam.width = 10.0
	beam.default_color = Color(EYE.r, EYE.g, EYE.b, 0.7)
	gaze_tick -= delta
	if gaze_tick <= 0.0:
		gaze_tick = 0.5
		hit(p, 0.6, "physical", {"no_stun": true})
		Fx.burst(level, p.global_position + Vector2(0, -50), EYE, 8, 80.0, 0.4, 0.25)


func _special(p: Actor, d: float) -> float:
	if d < 260.0:
		busy = 1.5
		set_pose("attack", 1.5)
		slam(global_position, 220.0, 1.4, 0.8 if not eyes_open else 1.4, "physical", EARTH, {"knock": 280.0})
		later(1.4, func(): level.shake(9.0))
		return randf_range(5.0, 7.0)
	return 3.0


func _move_attack(p: Actor, d: float, delta: float) -> void:
	if d <= attack_range + p.radius:
		velocity = Vector2.ZERO
		moving = false
		face_to(p.global_position)
		if cd <= 0.0:
			_begin_attack()
		return
	_chase(p, delta, 1.0 if eyes_open else 0.7)


func _strike(p: Actor) -> void:
	if p == null:
		return
	if dist_to_player() <= attack_range + p.radius + 24:
		hit(p, 1.0 if eyes_open else 0.5, "physical", {"always_hit": false, "melee": true})
		Sfx.play_at("swing_heavy", global_position, 0.6)


func _test_poke(p: Player, n: int) -> void:
	if eyes_open and n % 8 == 0:
		for m in lifters():
			m.take_damage(m.hp_max * 2.0, "physical", p)
	super._test_poke(p, n)
