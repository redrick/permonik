class_name BossBase
extends Monster

var fight_t := 0.0
var phase := 1
var busy := 0.0
var special_t := 3.0
var invuln_t := 0.0
var _note_t := 0.0
var _test := false
var _test_t := 0.0
var _test_n := 0
var _test_log := 0.0


func setup(mid: String, level_n: int, lv: Node, champion := false) -> void:
	super.setup(mid, level_n, lv, champion)
	_test = kind == "boss" and Game.args.has("--boss-test")
	_init_boss()


func _init_boss() -> void:
	pass


func _ai(delta: float) -> void:
	cd = maxf(0.0, cd - delta)
	busy = maxf(0.0, busy - delta)
	invuln_t = maxf(0.0, invuln_t - delta)
	_note_t = maxf(0.0, _note_t - delta)
	special_t -= delta
	if _test:
		_test_tick(delta)
	_always_tick(delta)
	if not can_act():
		velocity = Vector2.ZERO
		moving = false
		return
	var p := player()
	if p == null or Game.paused_ui:
		velocity = Vector2.ZERO
		moving = false
		return
	var d := dist_to_player()
	if not aggro:
		if d < aggro_range and (d < 220.0 or level.line_of_sight(global_position, p.global_position)):
			wake()
		else:
			_wander(delta)
			return
	fight_t += delta
	if windup > 0.0:
		windup -= delta
		velocity = Vector2.ZERO
		moving = false
		if windup <= 0.0:
			_strike(p)
		return
	if busy > 0.0:
		velocity = Vector2.ZERO
		moving = false
		_busy_tick(p, delta)
		return
	_fight(p, d, delta)


func _always_tick(_delta: float) -> void:
	pass


func _busy_tick(_p: Actor, _delta: float) -> void:
	pass


func _fight(p: Actor, d: float, delta: float) -> void:
	if special_t <= 0.0:
		special_t = _special(p, d)
		if busy > 0.0 or windup > 0.0:
			return
	_move_attack(p, d, delta)


func _special(_p: Actor, _d: float) -> float:
	return 6.0


func _move_attack(p: Actor, d: float, delta: float) -> void:
	if ai in ["caster", "ranged"]:
		_ai_ranged(p, d, delta)
	else:
		_ai_melee(p, d, delta)


func _modify_incoming(amount: float, _element: String, _source: Node, _opts: Dictionary) -> float:
	if invuln_t > 0.0:
		note(L.t({"cs": "Imunní", "en": "Immune"}), Color("bbbbbb"))
		return 0.0
	return amount


func _on_damaged(amount: float, elem: String, source: Node) -> void:
	super._on_damaged(amount, elem, source)
	_after_damage(amount, elem, source)


func _after_damage(_amount: float, _elem: String, _source: Node) -> void:
	pass


func die(killer: Node) -> void:
	if dead:
		return
	if _test:
		print("[boss-test] %s died at t=%.1f" % [id, fight_t])
	super.die(killer)


# ---------------------------------------------------------------- helpers
func pl() -> Player:
	var p: Player = level.player
	return p if p != null and is_instance_valid(p) and not p.dead else null


func later(t: float, fn: Callable) -> void:
	var tw := create_tween()
	tw.tween_interval(maxf(0.01, t))
	tw.tween_callback(func():
		if not dead:
			fn.call())


func say(key: String, dur := 4.5) -> void:
	var lines: Dictionary = data.get("lines", {})
	if lines.has(key):
		level.boss_say(self, lines[key], dur)


func say_t(cs: String, en: String, dur := 4.5) -> void:
	level.boss_say(self, {"cs": cs, "en": en}, dur)


func shout(cs: String, en: String, col := Color("e8d9a0")) -> void:
	level.float_text(top_pos(), Sfx.cry(id, {"cs": cs, "en": en}), col)


func note(text: String, col: Color) -> void:
	if _note_t > 0.0:
		return
	_note_t = 0.7
	level.float_text(top_pos(), text, col)


func bar() -> void:
	Game.boss_bar.emit(label_name(), hp / hp_max, true)


func hit(p: Actor, mult: float, elem := "", opts := {}) -> bool:
	if p == null or p.dead:
		return false
	var o := {"always_hit": true, "melee": false}
	o.merge(opts, true)
	return Combat.monster_hit_player(self, p, dmg * mult, element if elem == "" else elem, o)


func mark(pos: Vector2, r: float, delay: float, col: Color) -> void:
	Fx.ground_mark(level, pos, r, col, delay + 0.25)
	var s := Sprite2D.new()
	s.texture = Fx.ring_tex()
	s.global_position = pos
	s.modulate = Color(col.r, col.g, col.b, 0.1)
	var full := Vector2(r / 64.0, r / 64.0 * 0.55)
	s.scale = full * 0.15
	s.z_index = -1
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	s.material = m
	level.fx_root.add_child(s)
	var tw := s.create_tween().set_parallel(true)
	tw.tween_property(s, "scale", full, maxf(0.05, delay))
	tw.tween_property(s, "modulate:a", 0.95, maxf(0.05, delay))
	tw.chain().tween_callback(s.queue_free)


func line_warn(a: Vector2, b: Vector2, width: float, dur: float, col: Color) -> void:
	var l := Line2D.new()
	l.add_point(a)
	l.add_point(b)
	l.width = width
	l.default_color = Color(col.r, col.g, col.b, 0.28)
	l.z_index = -1
	l.begin_cap_mode = Line2D.LINE_CAP_ROUND
	l.end_cap_mode = Line2D.LINE_CAP_ROUND
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	l.material = m
	level.fx_root.add_child(l)
	var tw := l.create_tween()
	tw.tween_property(l, "default_color:a", 0.6, maxf(0.05, dur - 0.2))
	tw.tween_property(l, "modulate:a", 0.0, 0.2)
	tw.tween_callback(l.queue_free)


func slam(pos: Vector2, r: float, delay: float, mult: float, elem := "", col := Color("ff6a3a"), opts := {}, on_hit := Callable()) -> void:
	mark(pos, r, delay, col)
	later(delay, func():
		Fx.ring(level, pos, r, col)
		Fx.burst(level, pos + Vector2(0, -12), col, 18, r * 1.3, 0.5, 0.3)
		var p := player()
		if p and p.global_position.distance_to(pos) <= r + p.radius:
			if hit(p, mult, elem, opts) and on_hit.is_valid():
				on_hit.call(p))


func cone(dir: Vector2, r: float, arc_deg: float, delay: float, mult: float, elem: String, col: Color, on_hit := Callable()) -> void:
	var origin := global_position
	dir = dir.normalized()
	var half := deg_to_rad(arc_deg) / 2.0
	for i in range(1, 4):
		for j in [-1.0, 0.0, 1.0]:
			var q := origin + dir.rotated(j * half * 0.7) * r * i / 3.5
			mark(q, r * 0.16 * (0.6 + i * 0.25), delay, col)
	later(delay, func():
		for i in range(1, 6):
			for j in [-1.0, -0.5, 0.0, 0.5, 1.0]:
				var q := origin + dir.rotated(j * half * 0.8) * r * i / 5.5
				Fx.burst(level, q + Vector2(0, -20), col, 4, 90.0, 0.45, 0.3, true)
		Fx.flash(level, origin + dir * r * 0.5, col, r, 0.4)
		for p in Combat.targets_in_cone(level, origin, dir, r, arc_deg, 0):
			if hit(p, mult, elem) and on_hit.is_valid():
				on_hit.call(p))


func shoot(target: Vector2, fx_id: String, spd: float, mult: float, elem := "", col := Color(0, 0, 0, 0), count := 1, spread := 0.22, on_hit := Callable()) -> Array:
	var out := []
	var dir := (target - global_position).normalized()
	for i in count:
		var dd := dir.rotated((i - (count - 1) / 2.0) * spread)
		var pr := Projectile.spawn(level, global_position, dd, spd, fx_id, 0, func(a, _pr):
			if hit(a, mult, elem) and on_hit.is_valid():
				on_hit.call(a), col)
		pr.height = sprite_h * 0.4
		out.append(pr)
	return out


func summon(mid: String, n: int, center: Vector2, rmin := 60.0, rmax := 170.0, lvl_off := -2) -> Array:
	var out := []
	if level.monsters.size() > 90:
		return out
	for i in n:
		var pos: Vector2 = level.random_open_near(center, rmin, rmax)
		if pos == Vector2.INF:
			continue
		var m: Monster = level.spawn_monster(mid, pos, maxi(1, mlvl + lvl_off))
		if m:
			_minionize(m)
			Fx.burst(level, pos + Vector2(0, -30), Color("6b4ea0"), 12, 110.0)
			out.append(m)
	return out


func spawn_custom(script_path: String, mid: String, pos: Vector2, lvl: int) -> Monster:
	var m: Monster = load(script_path).new()
	m.position = pos
	m.home = pos
	m.level = level
	level.ysort.add_child(m)
	m.setup(mid, lvl, level)
	level.monsters.append(m)
	return m


func _minionize(m: Monster) -> void:
	m.no_drops = true
	m.xp_value = int(m.xp_value * 0.3)
	m.summoner = self
	m.minion_of = self
	m.wake()


func alive_minions() -> Array:
	return level.monsters.filter(func(m): return is_instance_valid(m) and not m.dead and m.minion_of == self)


func vanish(m: Monster) -> void:
	if not is_instance_valid(m):
		return
	level.monsters.erase(m)
	if level.hover_obj == m:
		level.hover_obj = null
	m.dead = true
	m.queue_free()


func props_of(pid: String) -> Array:
	return level.props.filter(func(p): return is_instance_valid(p) and p.id == pid)


func arena_cell() -> Vector2i:
	var bs: Vector2i = level.gen.boss_spot
	return bs if bs.x >= 0 else level.to_cell(global_position)


func place_props(pid: String, n: int, ring_cells: float, block := true) -> Array:
	var have := props_of(pid)
	var c0 := arena_cell()
	var k := 0
	while have.size() < n and k < n * 3:
		var a := TAU * float(k) / float(n) + 0.5
		var c := c0 + Vector2i(int(cos(a) * ring_cells), int(sin(a) * ring_cells * 0.75))
		var fc: Vector2i = level._find_free_near(c, 0, 2)
		k += 1
		if level.is_solid_cell(fc) or (fc - c0).length() < 2.0:
			continue
		var pr: PropNode = level._place_prop(pid, fc, block)
		have.append(pr)
	return have


func open_spot_near(pos: Vector2, rmin: float, rmax: float) -> Vector2:
	var q: Vector2 = level.random_open_near(pos, rmin, rmax)
	return q if q != Vector2.INF else pos


func blink_to(pos: Vector2, col := Color("6b4ea0")) -> void:
	Fx.burst(level, global_position + Vector2(0, -30), col, 16, 130.0)
	global_position = pos
	path.clear()
	Fx.burst(level, global_position + Vector2(0, -30), col, 16, 130.0)


func player_light_r() -> float:
	var p := pl()
	return p.light_radius_px() if p else 128.0


# ---------------------------------------------------------------- --boss-test hook
func _test_tick(delta: float) -> void:
	_test_t += delta
	var p := pl()
	if p == null:
		return
	p.invuln = 1.0
	if p.hp < p.hp_max * 0.6:
		Game.ch.hp = Game.ch.d.hp_max
		p.hp = Game.ch.hp
	if _test_n == 0 and _test_t > 1.0:
		_test_n = 1
		p.global_position = open_spot_near(global_position, 140.0, 220.0)
		print("[boss-test] %s hp=%d lvl=%d" % [id, int(hp_max), mlvl])
	_test_log -= delta
	if _test_log <= 0.0:
		_test_log = 3.0
		print("[boss-test] %s t=%.1f hp=%.0f%% phase=%d aggro=%s minions=%d cell=%s pcell=%s" % [id, fight_t, hp / hp_max * 100.0, phase, aggro, alive_minions().size(), level.to_cell(global_position), level.to_cell(p.global_position)])
	if _test_t > 2.0 and int(_test_t / 0.7) > _test_n:
		_test_n = int(_test_t / 0.7)
		_test_poke(p, _test_n)


func _test_poke(p: Player, n: int) -> void:
	take_damage(hp_max * 0.03, ["physical", "fire", "cold"][n % 3], p, {"no_stun": true})
