extends BossBase

const BONE := Color("e8dcc0")

var reassembled := false
var collapsed_t := 0.0
var raise_t := 4.0


func _init_boss() -> void:
	set_meta("half_said", true)


func _special(p: Actor, d: float) -> float:
	var r := randf()
	if phase == 2 and r < 0.35:
		_bone_nova()
		return randf_range(4.0, 6.0)
	if d > 160.0 and r < 0.75 and level.line_of_sight(global_position, p.global_position):
		set_pose("attack", 0.5)
		face_to(p.global_position)
		shoot(p.global_position, "bone", 340.0, 0.8, "physical", Color(0, 0, 0, 0), 3 if phase == 2 else 1, 0.2)
		Sfx.play_at("swing_heavy", global_position, 0.6)
		return randf_range(3.0, 4.5)
	_stomp(p)
	return randf_range(4.0, 6.0)


func _always_tick(delta: float) -> void:
	if collapsed_t > 0.0:
		collapsed_t -= delta
		if collapsed_t <= 0.0:
			_rise()
		return
	if not aggro:
		return
	raise_t -= delta
	if raise_t <= 0.0 and can_act():
		raise_t = 11.0 if phase == 1 else 8.0
		_raise_dead()


func _stomp(p: Actor) -> void:
	busy = 1.1
	set_pose("attack", 1.1)
	face_to(p.global_position)
	slam(global_position, 150.0, 1.0, 1.2, "physical", BONE, {"knock": 300.0})
	later(1.0, func(): level.shake(6.0))


func _bone_nova() -> void:
	busy = 0.9
	set_pose("attack", 0.9)
	mark(global_position, 90.0, 0.7, BONE)
	later(0.7, func():
		Sfx.play_at("death_bone", global_position, 0.6)
		for i in 10:
			var dir := Vector2.RIGHT.rotated(TAU * i / 10.0)
			var pr := Projectile.spawn(level, global_position, dir, 300.0, "bone", 0, func(a, _pr): hit(a, 0.6, "physical"))
			pr.height = 50.0
			pr.spin = 12.0)


func _raise_dead() -> void:
	if alive_minions().size() >= 7:
		return
	var n := 2 if phase == 1 else 3
	shout("Vstaňte!", "Rise!", BONE)
	set_pose("attack", 0.8)
	busy = 0.8
	for i in n:
		var q := open_spot_near(global_position, 90.0, 260.0)
		mark(q, 40.0, 1.0, Color("9a6bd8"))
		later(1.0, func():
			Fx.burst(level, q, BONE, 14, 90.0, 0.6, 0.25, true)
			var m: Monster = level.spawn_monster("kostlivy_havir", q, maxi(1, mlvl - 2))
			if m:
				_minionize(m))
	Sfx.play_at("death_bone", global_position, 0.5)


func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	if collapsed_t > 0.0:
		note(L.t({"cs": "Jen hromada kostí…", "en": "Just a pile of bones…"}), BONE)
		return 0.0
	amount = super._modify_incoming(amount, elem, source, opts)
	if not reassembled and amount > 0.0 and hp - amount < hp_max * 0.5:
		amount = maxf(0.0, hp - hp_max * 0.5) + 0.01
		reassembled = true
		_collapse.call_deferred()
	return amount


func _collapse() -> void:
	collapsed_t = 3.0
	phase = 2
	windup = 0.0
	busy = 0.0
	stun_t = 3.0
	velocity = Vector2.ZERO
	Sfx.play_at("death_bone", global_position)
	Fx.burst(level, global_position + Vector2(0, -60), BONE, 40, 260.0, 0.9, 0.35)
	level.shake(8.0)
	var tw := create_tween()
	tw.tween_property(sprite, "scale", Vector2(1.3, 0.25), 0.35).set_ease(Tween.EASE_IN)
	say("half")


func _rise() -> void:
	hp = maxf(hp, hp_max * 0.5)
	bar()
	Sfx.play_at("boss_roar", global_position, 0.8)
	Fx.ring(level, global_position, 200.0, BONE, 0.6)
	var tw := create_tween()
	tw.tween_property(sprite, "scale", Vector2.ONE, 0.6).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	shout("Složen!", "Reassembled!", BONE)
	speed *= 1.15
	attack_cd *= 0.85
	_raise_dead()
