extends BossBase

const DUST := Color("c8a878")
const CHARGE_SPD := 620.0

var charge_t := 0.0
var charge_end := Vector2.ZERO
var charge_wall := false
var chain := 0
var dazed_t := 0.0
var trampled := false
var dogs_called := false


func _init_boss() -> void:
	special_t = 2.0


func _always_tick(delta: float) -> void:
	dazed_t = maxf(0.0, dazed_t - delta)


func _special(p: Actor, d: float) -> float:
	if d > 140.0 or randf() < 0.5:
		_aim_charge(p)
		return randf_range(5.0, 7.0) if phase == 1 else randf_range(3.5, 5.0)
	busy = 0.9
	set_pose("attack", 0.9)
	face_to(p.global_position)
	cone(p.global_position - global_position, 170.0, 100.0, 0.8, 1.3, "physical", DUST)
	return randf_range(3.0, 4.0)


func _aim_charge(p: Actor) -> void:
	var dir := (p.global_position - global_position).normalized()
	var far := global_position + dir * 900.0
	charge_end = level.clamp_walkable(global_position, far, 900.0)
	charge_wall = charge_end.distance_to(far) > 20.0
	face_to(p.global_position)
	set_pose("attack", 1.3)
	shout("HÝJÁ!", "HYAH!", Color("ffcf8a"))
	Sfx.play_at("boss_roar", global_position, 0.5)
	line_warn(global_position, charge_end, radius * 2.4, 1.2, Color("ff5a3a"))
	Fx.ground_mark(level, charge_end, 80.0, Color("ff5a3a"), 1.5)
	busy = 1.2
	later(1.2, func(): _start_charge())


func _start_charge() -> void:
	busy = 0.0
	trampled = false
	charge_t = global_position.distance_to(charge_end) / CHARGE_SPD + 0.05
	collision_mask = 1
	Sfx.play_at("swing_heavy", global_position)


func _fight(p: Actor, d: float, delta: float) -> void:
	if not dogs_called and hp < hp_max * 0.5:
		dogs_called = true
		phase = 2
		Sfx.play_at("wolf_howl", global_position)
		shout("Ke mně, psi!", "To me, hounds!", DUST)
		summon("cerny_pes", 3, global_position, 80.0, 220.0)
	if dazed_t > 0.0:
		velocity = Vector2.ZERO
		moving = false
		return
	if charge_t > 0.0:
		_charge_step(p, delta)
		return
	super._fight(p, d, delta)


func _charge_step(p: Actor, delta: float) -> void:
	charge_t -= delta
	var dir := (charge_end - global_position).normalized()
	velocity = dir * CHARGE_SPD
	moving = true
	face_to(charge_end)
	if int(fight_t * 20.0) % 3 == 0:
		Fx.burst(level, global_position, DUST, 3, 60.0, 0.4, 0.25)
	if not trampled and p.global_position.distance_to(global_position) < radius + p.radius + 20.0:
		trampled = true
		hit(p, 1.7, "physical", {"knock": 520.0})
		p.knock = dir.orthogonal() * (520.0 if dir.orthogonal().dot(p.global_position - global_position) > 0 else -520.0)
		level.shake(7.0)
	var blocked: bool = level.is_solid(global_position + dir * (radius + 18.0))
	if charge_t <= 0.0 or global_position.distance_to(charge_end) < 14.0 or blocked:
		charge_t = 0.0
		collision_mask = 2 | 4 | 1
		velocity = Vector2.ZERO
		if charge_wall or blocked:
			_crash()
		elif phase == 2 and chain < 1:
			chain += 1
			_aim_charge(p)
		else:
			chain = 0


func _crash() -> void:
	chain = 0
	dazed_t = 2.6
	stun_t = 2.6
	Sfx.play_at("hit_stone", global_position)
	Sfx.play_at("hit_metal", global_position)
	level.shake(10.0)
	Fx.burst(level, global_position + Vector2(0, -40), DUST, 30, 220.0, 0.7, 0.35)
	shout("Kůň se vzpíná!", "The horse rears!", Color("ffe39a"))
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", deg_to_rad(-14.0 * facing), 0.2)
	tw.tween_interval(2.0)
	tw.tween_property(sprite, "rotation", 0.0, 0.3)


func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	amount = super._modify_incoming(amount, elem, source, opts)
	return amount * (1.5 if dazed_t > 0.0 else 1.0)


func _test_poke(p: Player, n: int) -> void:
	if n % 6 == 0 and charge_t <= 0.0 and busy <= 0.0:
		_aim_charge(p)
	super._test_poke(p, n)
