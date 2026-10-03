extends BossBase

const WHITE := Color("dfe8f0")

var fade := 1.0
var hidden_t := 0.0
var shown_t := 0.0
var bell_t := 9.0


func _init_boss() -> void:
	shown_t = randf_range(6.0, 8.0)


func in_light() -> bool:
	var p := pl()
	return p != null and p.global_position.distance_to(global_position) < p.light_radius_px() * 0.9


func _always_tick(delta: float) -> void:
	var target := 0.0 if hidden_t > 0.0 else (1.0 if in_light() else 0.3)
	fade = move_toward(fade, target, delta * 1.6)
	modulate.a = fade
	if not aggro:
		return
	bell_t -= delta
	if bell_t <= 0.0 and can_act():
		bell_t = 13.0 if phase == 1 else 10.0
		_ring_bell()


func _fight(p: Actor, d: float, delta: float) -> void:
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
	if hidden_t > 0.0:
		hidden_t -= delta
		var r := player_light_r()
		var to := p.global_position - global_position
		var circle := p.global_position - to.normalized().rotated(0.5) * (r + 90.0)
		if not level.is_solid(circle):
			path = [circle]
		follow_path(delta, speed * 1.2 * speed_mult())
		if hidden_t <= 0.0:
			_emerge(p)
		return
	shown_t -= delta
	if shown_t <= 0.0:
		_fade_out(p)
		return
	_ai_melee(p, d, delta)


func _fade_out(p: Actor) -> void:
	hidden_t = randf_range(3.0, 4.5)
	shown_t = randf_range(6.0, 9.0) * (0.75 if phase == 2 else 1.0)
	var q := open_spot_near(p.global_position, player_light_r() + 80.0, player_light_r() + 220.0)
	Fx.burst(level, global_position + Vector2(0, -60), WHITE, 18, 120.0, 0.8, 0.3, true)
	Sfx.play_at("ghost_wail", global_position, 0.7)
	global_position = q
	path.clear()


func _emerge(p: Actor) -> void:
	var tgt := p.global_position
	shout("Po klekání…", "After the bell…", WHITE)
	var q := open_spot_near(tgt, 60.0, 110.0)
	global_position = q
	face_to(tgt)
	set_pose("attack", 1.0)
	busy = 0.9
	slam(tgt, 70.0, 0.85, 1.3, "cold", Color("a9d8ff"), {}, func(a): a.apply_status("chill", 2.5))


func _ring_bell() -> void:
	Sfx.play_at("bell_toll", global_position, 0.9)
	Fx.ring(level, global_position, 260.0, WHITE, 0.9)
	shout("Bim… bam…", "Dong… dong…", WHITE)
	busy = 1.0
	set_pose("attack", 1.0)
	var n := 2 if phase == 1 else 4
	n = mini(n, 8 - alive_minions().size())
	if n > 0:
		summon("sotek", n, global_position, 80.0, 200.0)
	if phase == 2:
		var p := pl()
		if p:
			p.apply_status("darkness", 4.0)


func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	if hidden_t > 0.0 or not in_light():
		note(L.t({"cs": "Ve tmě ji nezasáhneš", "en": "Untouchable in the dark"}), Color("9fb4c8"))
		return 0.0
	return super._modify_incoming(amount, elem, source, opts)


func _test_poke(p: Player, n: int) -> void:
	if hidden_t <= 0.0 and n % 4 == 0:
		p.global_position = open_spot_near(global_position, 50.0, 90.0)
	super._test_poke(p, n)
