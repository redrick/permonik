extends BossBase

const FROST := Color("9fe0ff")
const SOUL2 := Color("b9a4ff")

var second := false
var rising_t := 0.0
var blink_t := 6.0


func _init_boss() -> void:
	set_meta("half_said", true)


func label_name() -> String:
	return "%s · %s" % [display_name, "II" if second else "I"]


func face_to(p: Vector2) -> void:
	super.face_to(p)
	if second and sprite:
		sprite.flip_h = not sprite.flip_h


func _always_tick(delta: float) -> void:
	if rising_t > 0.0:
		rising_t -= delta
		if rising_t <= 0.0:
			_rise_second()


func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	if rising_t > 0.0:
		note(L.t({"cs": "Druhé srdce ještě bije…", "en": "The second heart still beats…"}), SOUL2)
		return 0.0
	amount = super._modify_incoming(amount, elem, source, opts)
	if not second and amount >= hp:
		amount = maxf(0.0, hp - 1.0)
		_first_death.call_deferred()
	return amount


func _first_death() -> void:
	if second or rising_t > 0.0:
		return
	rising_t = 3.0
	stun_t = 3.0
	windup = 0.0
	busy = 0.0
	Sfx.play_at("death_ghost", global_position)
	level.boss_say(self, L.t({"cs": "Jedno srdce… stojí… To druhé ještě bije.", "en": "One heart… has stopped… The other one still beats."}), 3.5)
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", deg_to_rad(80.0 * facing), 0.35).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(sprite, "modulate", Color(0.6, 0.6, 0.7), 0.35)
	if shadow:
		shadow.visible = true


func _rise_second() -> void:
	second = true
	phase = 2
	hp = hp_max
	speed *= 1.4
	attack_cd *= 0.7
	ai = "caster"
	attack_range = 300.0
	projectile_fx = "ice_shard"
	element = "cold"
	float_h = 14.0
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", 0.0, 0.4).set_trans(Tween.TRANS_BACK)
	tw.parallel().tween_property(sprite, "modulate", Color(0.8, 0.75, 1.15), 0.4)
	Fx.burst(level, global_position + Vector2(0, -80), SOUL2, 40, 200.0, 1.0, 0.35, true)
	Fx.ring(level, global_position, 260.0, SOUL2, 0.7)
	Sfx.play_at("ghost_wail", global_position)
	say("half")
	bar()
	face_to(global_position + Vector2(facing, 0))


func _special(p: Actor, d: float) -> float:
	if not second:
		return _first_special(p, d)
	var r := randf()
	if r < 0.35:
		face_to(p.global_position)
		set_pose("attack", 0.6)
		shoot(p.global_position, "ice_shard", 360.0, 0.7, "cold", FROST, 5, 0.18, func(a): a.apply_status("chill", 2.0))
		Sfx.play_at("frost_cast", global_position)
		return randf_range(2.0, 3.0)
	if r < 0.65:
		busy = 0.9
		set_pose("attack", 0.9)
		for i in 3:
			var q := p.global_position + Vector2.RIGHT.rotated(TAU * i / 3.0 + randf()) * randf_range(0.0, 110.0)
			slam(q, 75.0, 1.0 + i * 0.15, 1.0, "cold", FROST, {}, func(a): a.apply_status("freeze", 0.8))
		return randf_range(3.0, 4.0)
	blink_to(open_spot_near(p.global_position, 200.0, 320.0), SOUL2)
	return randf_range(1.5, 2.5)


func _first_special(p: Actor, d: float) -> float:
	if d > 130.0 and d < 520.0:
		var tgt := p.global_position
		busy = 0.75
		set_pose("attack", 0.9)
		face_to(tgt)
		shout("Hhhaa!", "Hhhaa!", FROST)
		slam(tgt, 90.0, 0.75, 1.3, "physical", Color("e0e8ff"))
		later(0.6, func():
			if not level.is_solid(tgt):
				blink_to(tgt, Color("e0e8ff")))
		return randf_range(4.0, 6.0)
	busy = 0.6
	set_pose("attack", 0.6)
	cone(p.global_position - global_position, 140.0, 110.0, 0.55, 1.0, "physical", Color("e0e8ff"), func(a): a.apply_status("slow", 1.5))
	return randf_range(3.0, 4.0)
