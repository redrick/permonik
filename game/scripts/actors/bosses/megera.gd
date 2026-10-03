extends BossBase

const HEX := Color("9a6bd8")
const BREW := Color("9cff6a")

var cauldrons: Array = []
var hop_t := 8.0
var spit_t := 5.0


func _init_boss() -> void:
	ai = "caster"
	cauldrons = place_props("kotel", 4, 6.0, true)


func _cauldron_spot(k: PropNode) -> Vector2:
	var q := k.global_position + Vector2(0, 50)
	return q if not level.is_solid(q) else open_spot_near(k.global_position, 60.0, 110.0)


func _always_tick(delta: float) -> void:
	var p := pl()
	if p == null:
		return
	var cursed := p.status.has("cursed")
	for e in ["fire", "lightning", "cold", "poison"]:
		p.resist[e] = int(Game.ch.d.get("res_" + e, 0)) - (30 if cursed else 0)
	if not aggro or dead:
		return
	if phase == 2:
		spit_t -= delta
		if spit_t <= 0.0:
			spit_t = 3.5
			_cauldron_spit(p)


func _special(p: Actor, d: float) -> float:
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
	var r := randf()
	if (d < 170.0 or r < 0.25) and cauldrons.size() > 1:
		_hop(p)
		return randf_range(3.0, 4.5)
	if r < 0.5 and not p.status.has("cursed"):
		_curse(p)
		return randf_range(3.0, 4.0)
	if r < 0.8:
		_transform(p)
		return randf_range(6.0, 8.0)
	_brew_pools(p)
	return randf_range(4.0, 6.0)


func _curse(p: Actor) -> void:
	busy = 0.8
	set_pose("attack", 0.8)
	face_to(p.global_position)
	shout("Proklínám!", "I curse you!", HEX)
	Fx.bolt(level, global_position + Vector2(0, -80), p.global_position + Vector2(0, -50), HEX, 3.0, 0.4)
	p.apply_status("cursed", 9.0)
	Fx.burst(level, p.global_position + Vector2(0, -50), HEX, 18, 80.0, 0.8, 0.25, true)
	level.float_text(p.top_pos(), L.t({"cs": "Prokletí: odolnosti −30", "en": "Cursed: resistances −30"}), HEX, true)


func _transform(p: Actor) -> void:
	busy = 1.0
	set_pose("attack", 1.0)
	Sfx.play_at("wolf_howl", global_position)
	shout("Na čtyři nohy!", "On all fours!", HEX)
	var victims: Array = level.monsters.filter(func(m): return is_instance_valid(m) and not m.dead and m != self and m.id != "vlk" and m.kind != "boss" and m.global_position.distance_to(global_position) < 500.0)
	var n := 0
	for m in victims.slice(0, 3):
		var pos: Vector2 = m.global_position
		Fx.burst(level, pos + Vector2(0, -40), HEX, 20, 120.0, 0.7, 0.3)
		vanish(m)
		var w: Monster = level.spawn_monster("vlk", pos, maxi(1, mlvl - 2))
		if w:
			_minionize(w)
			n += 1
	if n == 0 and alive_minions().size() < 6:
		var k: PropNode = cauldrons.pick_random() if cauldrons.size() > 0 else null
		summon("vlk", 2, k.global_position if k else global_position, 60.0, 140.0)


func _hop(p: Actor) -> void:
	var options: Array = cauldrons.filter(func(k): return is_instance_valid(k) and k.global_position.distance_to(global_position) > 100.0)
	if options.is_empty():
		return
	options.sort_custom(func(a, b): return a.global_position.distance_to(p.global_position) > b.global_position.distance_to(p.global_position))
	var k: PropNode = options[0] if randf() < 0.6 else options.pick_random()
	Sfx.play_at("cauldron_bubble", global_position)
	blink_to(_cauldron_spot(k), BREW)
	Sfx.play_at("cauldron_bubble", global_position)
	busy = 0.5
	BossHazard.spawn(self, k.global_position + Vector2(0, 30), 110.0, 5.0, BREW, "poison", dmg * 0.5, 0.9)


func _brew_pools(p: Actor) -> void:
	busy = 0.8
	set_pose("attack", 0.8)
	for i in 3:
		var q := p.global_position + Vector2(randf_range(-120, 120), randf_range(-80, 80))
		if not level.is_solid(q):
			var z := BossHazard.spawn(self, q, 70.0, 6.0, BREW, "poison", dmg * 0.6, 1.0)
			z.status_id = "slow"


func _cauldron_spit(p: Actor) -> void:
	for k in cauldrons:
		if is_instance_valid(k) and k.global_position.distance_to(p.global_position) < 600.0 and level.line_of_sight(k.global_position, p.global_position):
			var pr := Projectile.spawn(level, k.global_position, p.global_position - k.global_position, 260.0, "", 0, func(a, _pr): hit(a, 0.6, "poison"), BREW)
			pr.height = 50.0
			Sfx.play_at("cauldron_bubble", k.global_position, 0.5)
			return


func die(killer: Node) -> void:
	super.die(killer)
	var p := pl()
	if p:
		p.status.erase("cursed")
		for e in ["fire", "lightning", "cold", "poison"]:
			p.resist[e] = int(Game.ch.d.get("res_" + e, 0))
