extends BossBase

const WATER := Color("6fb8d8")
const SOUL := Color("cfe8ff")

var cups_total := 0
var cup_t := 6.0
var pull_t := 3.0
var dive_t := 0.0


func _init_boss() -> void:
	cups_total = maxi(1, cups().size())


func cups() -> Array:
	return props_of("hrnek_dusicka").filter(func(c): return not c.used)


func cup_factor() -> float:
	return float(cups().size()) / float(cups_total)


func _always_tick(delta: float) -> void:
	if not aggro:
		return
	if level.is_water(global_position) and hp < hp_max:
		var rate := hp_max * 0.006 * (0.35 + 0.65 * cup_factor())
		heal(rate * delta)
		if int(fight_t * 2.0) % 3 == 0 and randf() < 0.05:
			Fx.burst(level, global_position + Vector2(0, -20), WATER, 4, 50.0, 0.6, 0.2, true)
	cup_t -= delta
	if cup_t <= 0.0:
		cup_t = 7.0
		_drink_souls()
	var p := pl()
	if p and level.is_water(p.global_position):
		p.apply_status("chill", 0.3)
		pull_t -= delta
		if pull_t <= 0.0 and p.global_position.distance_to(global_position) < 600.0:
			pull_t = 4.0
			p.knock = (global_position - p.global_position).normalized() * 320.0
			Sfx.play_at("water_splash", p.global_position, 0.7)
			Fx.burst(level, p.global_position, WATER, 14, 120.0, 0.5, 0.25)
			level.float_text(p.top_pos(), L.t({"cs": "Pod vodu!", "en": "Under you go!"}), WATER, true)


func _drink_souls() -> void:
	var live := cups()
	if live.is_empty() or hp >= hp_max:
		return
	for c in live:
		Fx.bolt(level, c.global_position + Vector2(0, -20), global_position + Vector2(0, -60), SOUL, 2.0, 0.4)
	heal(hp_max * 0.012 * live.size())
	bar()
	level.float_text(top_pos(), "+%d" % int(hp_max * 0.012 * live.size()), Color("8fe36b"))


func _fight(p: Actor, d: float, delta: float) -> void:
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
		summon("utopenec", 2, global_position, 80.0, 220.0)
	if dive_t > 0.0:
		dive_t -= delta
		if level.is_water(global_position) or path.is_empty():
			dive_t = 0.0
		else:
			follow_path(delta, speed * 1.3 * speed_mult())
			return
	super._fight(p, d, delta)


func _special(p: Actor, d: float) -> float:
	var r := randf()
	if hp < hp_max * 0.7 and not level.is_water(global_position) and r < 0.35:
		var w := _nearest_water()
		if w != Vector2.INF:
			shout("Do tůně!", "Into the pool!", WATER)
			set_path_to(w)
			dive_t = 4.0
			return randf_range(5.0, 7.0)
	if d > 120.0 or r < 0.6:
		face_to(p.global_position)
		set_pose("attack", 0.5)
		var n := 3 if phase == 2 else 1
		shoot(p.global_position, "", 330.0, 0.9, "cold", WATER, n, 0.25, func(a): a.apply_status("chill", 2.0))
		Sfx.play_at("water_splash", global_position, 0.6)
		return randf_range(2.2, 3.5)
	busy = 1.0
	set_pose("attack", 1.0)
	slam(global_position, 140.0, 0.95, 1.2, "cold", WATER, {"knock": 260.0})
	return randf_range(4.0, 5.5)


func _nearest_water() -> Vector2:
	var c: Vector2i = level.to_cell(global_position)
	for r in range(1, 9):
		for i in 16:
			var a := TAU * i / 16.0
			var q := c + Vector2i(int(cos(a) * r), int(sin(a) * r))
			var wp: Vector2 = level.cell_center(q)
			if level.is_water(wp) and not level.is_solid(wp):
				return wp
	return Vector2.INF


func on_quest_prop(prop: PropNode, p: Player) -> void:
	if prop.id != "hrnek_dusicka" or prop.used:
		Game.on_event("use", prop.id)
		return
	p.face_to(prop.global_position)
	p.start_action("attack", 0.35, 0.5, func(): _break_cup(prop))


func _break_cup(prop: PropNode) -> void:
	if prop.used:
		return
	prop.used = true
	prop.set_hover(false)
	Sfx.play_at("urn_break", prop.global_position)
	Sfx.play_at("ghost_wail", prop.global_position, 0.5)
	Fx.burst(level, prop.global_position + Vector2(0, -20), Color("d8d0c0"), 12, 120.0, 0.4, 0.2)
	Fx.sprite_fx(level, "soul", prop.global_position + Vector2(0, -30), 2.0, 1.2, 140.0)
	Fx.burst(level, prop.global_position + Vector2(0, -40), SOUL, 16, 70.0, 1.4, 0.3, true)
	if DB.has_tex("props/hrnek_dusicka_broken"):
		prop.set_texture("hrnek_dusicka_broken")
	else:
		prop.sprite.modulate = Color(0.45, 0.45, 0.5, 0.6)
	if prop.light:
		prop.create_tween().tween_property(prop.light, "energy", 0.0, 1.0)
	Game.on_event("use", "hrnek_dusicka")
	var left := cups().size()
	level.float_text(prop.global_position + Vector2(0, -80), L.t({"cs": "Dušička je volná", "en": "A soul is free"}), SOUL)
	if left == 0:
		say_t("Všechny… všechny jsi je pustil. Ty nevíš, komu do rukou.", "All… you let them all go. You don't know whose hands they run to.")
	elif left == cups_total - 1:
		say_t("Můj hrníček! Nech je být!", "My teacup! Leave them be!")


func _test_poke(p: Player, n: int) -> void:
	if n % 5 == 0:
		var live := cups()
		if live.size() > 0:
			_break_cup(live[0])
	super._test_poke(p, n)
