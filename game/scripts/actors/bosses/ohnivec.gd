extends BossBase

const EMBER := Color("ff8a2a")
const GOLD := Color("ffcc55")

var anvils: Array = []
var anvil_t := 6.0
var mimic_t := 14.0
var coins_thrown := 0


func _init_boss() -> void:
	ai = "caster"
	anvils = place_props("kovadlina", 4, 5.0, true)


func _always_tick(delta: float) -> void:
	if not aggro:
		return
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
	anvil_t -= delta
	if anvil_t <= 0.0:
		anvil_t = 6.5 if phase == 1 else 4.5
		_anvil_wave()
	mimic_t -= delta
	if mimic_t <= 0.0 and can_act():
		mimic_t = 16.0 if phase == 1 else 11.0
		_drop_mimics()


func _strike(p: Actor) -> void:
	if p == null:
		return
	face_to(p.global_position)
	lunge = 10.0
	_coins(p.global_position, 3 if phase == 1 else 5)


func _coins(target: Vector2, n: int) -> void:
	Sfx.play_at("coin_bounce", global_position, 0.8)
	var dir := (target - global_position).normalized()
	for i in n:
		coins_thrown += 1
		var tithe := coins_thrown % 10 == 0
		var dd := dir.rotated((i - (n - 1) / 2.0) * 0.28)
		var pr := Projectile.spawn(level, global_position, dd, 300.0 if not tithe else 240.0, "coin", 0, func(a, _pr):
			if hit(a, 1.8 if tithe else 0.8, "fire"):
				a.apply_status("burn", 2.5, {"dps": dmg.x * 0.25, "src": self})
				if tithe:
					level.float_text(a.top_pos(), L.t({"cs": "Desátek!", "en": "The tithe!"}), GOLD, true), EMBER)
		pr.bounce = 3
		pr.spin = 14.0
		pr.life = 3.2
		pr.height = sprite_h * 0.35
		if tithe:
			pr.sprite.scale *= 1.8


func _special(p: Actor, d: float) -> float:
	var r := randf()
	if r < 0.4 or d < 140.0:
		busy = 1.1
		set_pose("attack", 1.1)
		face_to(p.global_position)
		shout("Ražba!", "Strike the coin!", GOLD)
		slam(global_position, 170.0, 1.0, 1.3, "fire", EMBER, {"knock": 340.0})
		later(1.0, func(): level.shake(7.0))
		return randf_range(4.0, 6.0)
	set_pose("attack", 0.6)
	_coins(p.global_position, 7 if phase == 2 else 5)
	return randf_range(3.0, 4.5)


func _anvil_wave() -> void:
	var p := pl()
	if p == null:
		return
	var live := anvils.filter(func(k): return is_instance_valid(k))
	if live.is_empty():
		return
	live.sort_custom(func(a, b): return a.global_position.distance_to(p.global_position) < b.global_position.distance_to(p.global_position))
	var k: PropNode = live[0] if randf() < 0.7 else live.pick_random()
	var from := k.global_position + Vector2(0, 10)
	var dir := (p.global_position - from).normalized()
	var to: Vector2 = level.clamp_walkable(from + dir * 40.0, from + dir * 640.0, 640.0)
	k.sprite.modulate = Color(1.6, 0.9, 0.5)
	k.create_tween().tween_property(k.sprite, "modulate", Color.WHITE, 1.6)
	Sfx.play_at("hit_metal", k.global_position)
	line_warn(from, to, 70.0, 1.1, EMBER)
	var n := maxi(1, int(from.distance_to(to) / 50.0))
	var hit_once := [false]
	for i in n + 1:
		var q := from.lerp(to, float(i) / n)
		later(1.1 + i * 0.05, func():
			Fx.burst(level, q + Vector2(0, -16), EMBER, 6, 120.0, 0.45, 0.35, true)
			var pp := pl()
			if pp and not hit_once[0] and pp.global_position.distance_to(q) < 46.0:
				hit_once[0] = true
				hit(pp, 1.1, "fire", {"knock": 200.0}))
	later(1.1, func(): Sfx.play_at("fire_cast", from))


func _drop_mimics() -> void:
	set_pose("attack", 0.7)
	shout("Tolary pro tebe!", "Thalers for you!", GOLD)
	var n := 2 if phase == 1 else 3
	for i in n:
		var q := open_spot_near(global_position, 120.0, 320.0)
		Fx.burst(level, q + Vector2(0, -10), GOLD, 10, 90.0, 0.4, 0.2)
		var m := spawn_custom("res://scripts/actors/bosses/minion_mimic.gd", "ohnivy_muzik", q, maxi(1, mlvl - 2))
		m.minion_of = self
		m.summoner = self
	Sfx.play("gold", 0.6)


func _test_poke(p: Player, n: int) -> void:
	if n % 9 == 0:
		for m in alive_minions():
			if m.has_method("reveal"):
				m.reveal()
	super._test_poke(p, n)
