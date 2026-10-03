extends BossBase

const COLD := Color("cfe8ff")
const POWERS := ["voda", "kamen", "ohen", "smrt"]
const POWER_COL := {"voda": Color("6fb8d8"), "kamen": Color("d8f06a"), "ohen": Color("ff8a2a"), "smrt": Color("7a5ab8")}
const POWER_NAME := {"voda": {"cs": "Voda!", "en": "Water!"}, "kamen": {"cs": "Kámen!", "en": "Stone!"},
	"ohen": {"cs": "Oheň!", "en": "Fire!"}, "smrt": {"cs": "Smrt!", "en": "Death!"}}

var small_data := {}
var small_tex := {}
var big_tex := {}
var big := {}
var transforming := false
var hop_t := 3.0
var split_t := 5.0
var power_i := -1
var power := ""
var power_t := 0.0
var power_tick := 0.0
var gaze: Line2D
var altar: PropNode
var lamp: Monster
var lamp_broken := false
var tithe_hits := 0
var last_hp := -1.0
var finished := false


func _init_boss() -> void:
	set_meta("half_said", true)
	small_data = DB.monster("permonik")
	big_tex = tex.duplicate()
	big = {"hp": hp_max, "dmg": dmg, "speed": speed, "radius": radius, "range": attack_range, "cd": attack_cd}
	for pz in ["idle", "walk", "attack"]:
		var t := DB.tex("sprites/monsters/permonik_%s" % pz)
		if t:
			small_tex[pz] = t
	if small_tex.is_empty():
		var t1 := DB.tex("sprites/npcs/permonik")
		var t2 := DB.tex("sprites/npcs/permonik_grin")
		if t1:
			small_tex = {"idle": t1, "walk": t1, "attack": t2 if t2 else t1}
	hp_max = big.hp * float(small_data.get("hp", 3700)) / float(data.get("hp", 12300))
	hp = hp_max
	dmg = big.dmg * 0.6
	speed = float(small_data.get("speed", 140))
	radius = float(small_data.get("size", 14))
	attack_range = float(small_data.get("attack_range", 50))
	attack_cd = float(small_data.get("attack_cd", 1.0))
	if not small_tex.is_empty():
		tex = small_tex
		sprite.texture = null
		set_pose("idle")
	if light:
		light.texture_scale = 160.0 * 2.0 / 256.0
	var altars := props_of("oltar")
	if altars.is_empty():
		altars = place_props("oltar", 1, 3.0, true)
	altar = altars[0] if altars.size() > 0 else null
	gaze = Line2D.new()
	gaze.width = 7.0
	gaze.default_color = Color(0, 0, 0, 0)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	gaze.material = m
	gaze.add_point(Vector2.ZERO)
	gaze.add_point(Vector2.ZERO)
	level.fx_root.add_child(gaze)


func _exit_tree() -> void:
	if is_instance_valid(gaze):
		gaze.queue_free()


func label_sub() -> String:
	if phase == 1:
		return L.t(small_data.get("title", ""))
	if phase == 3:
		return L.t({"cs": "Desátek", "en": "The Tithe"})
	return super.label_sub()


func small_line(key: String, dur := 5.0) -> void:
	var lines: Dictionary = small_data.get("lines", {})
	if lines.has(key):
		level.boss_say(self, L.t(lines[key]), dur)


func _on_boss_aggro() -> void:
	small_line("aggro", 7.0)
	Sfx.play_at("laugh_permonik", global_position)
	Sfx.music("final_boss")


# ---------------------------------------------------------------- damage rules
func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	if transforming:
		note(L.t({"cs": "Hihihi…", "en": "Hee hee hee…"}), COLD)
		return 0.0
	amount = super._modify_incoming(amount, elem, source, opts)
	if phase == 3 and lamp and is_instance_valid(lamp) and not lamp.dead:
		amount *= 0.1
		note(L.t({"cs": "Kahan ho chrání!", "en": "The lamp shields him!"}), COLD)
	if not lamp_broken and amount >= hp:
		amount = maxf(0.0, hp - 1.0)
		if phase == 1:
			_transform.call_deferred()
	return amount


func _after_damage(_amount: float, _elem: String, _source: Node) -> void:
	if phase == 2 and hp < hp_max * 0.35:
		_begin_tithe.call_deferred()


# ---------------------------------------------------------------- phase 1: Mužíček
func _fight(p: Actor, d: float, delta: float) -> void:
	if transforming:
		velocity = Vector2.ZERO
		moving = false
		return
	if phase == 1:
		hop_t -= delta
		split_t -= delta
		if split_t <= 0.0:
			split_t = randf_range(11.0, 14.0)
			_split(p)
			return
		if hop_t <= 0.0:
			hop_t = randf_range(3.0, 4.5)
			_giggle()
			blink_to(open_spot_near(p.global_position, 120.0, 230.0), COLD)
			return
		_ai_melee(p, d, delta, 1.0, true)
		return
	_power_tick(p, delta)
	super._fight(p, d, delta)


func _giggle() -> void:
	Sfx.play_at("laugh_permonik", global_position, 0.8)
	level.float_text(top_pos(), ["Hihi!", "Hehe…", "Zdař…"].pick_random(), COLD)


func _split(p: Actor) -> void:
	_giggle()
	var spots: Array = []
	for i in 4:
		var a := TAU * i / 4.0 + randf() * 0.6
		var q := p.global_position + Vector2.RIGHT.rotated(a) * randf_range(170.0, 240.0)
		spots.append(q if not level.is_solid(q) else open_spot_near(p.global_position, 150.0, 250.0))
	spots.shuffle()
	blink_to(spots[0], COLD)
	for i in range(1, 4):
		var c := spawn_custom("res://scripts/actors/bosses/minion_permonik_copy.gd", "permonicek", spots[i], mlvl)
		c.call("look_like", tex)
		c.minion_of = self
		c.wake()
		Fx.burst(level, c.global_position + Vector2(0, -40), COLD, 16, 120.0, 0.6, 0.3, true)
	if not get_meta("split_said", false):
		set_meta("split_said", true)
		small_line("half", 4.0)


func _poof_copies() -> void:
	for m in alive_minions():
		if m.has_method("poof"):
			m.poof(false)


func _transform() -> void:
	if transforming or phase != 1:
		return
	transforming = true
	_poof_copies()
	windup = 0.0
	busy = 0.0
	small_line("death", 4.0)
	Sfx.play_at("laugh_permonik", global_position)
	var c: Vector2 = altar.global_position + Vector2(0, 160) if altar else home
	if level.is_solid(c):
		c = open_spot_near(home, 0.0, 120.0)
	blink_to(c, COLD)
	var tw := create_tween()
	tw.tween_property(sprite, "scale", Vector2(2.6, 2.6), 2.2).set_trans(Tween.TRANS_SINE)
	tw.parallel().tween_method(func(v): mat_set("flash", v), 0.0, 1.0, 2.2)
	tw.tween_callback(_become_giant)
	tw.tween_property(sprite, "scale", Vector2.ONE, 0.5).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_callback(func():
		transforming = false
		say("aggro", 6.0))
	level.shake(6.0)


func _become_giant() -> void:
	phase = 2
	tex = big_tex
	sprite.texture = null
	set_pose("idle")
	sprite.scale = Vector2(0.4, 0.4)
	hp_max = big.hp
	hp = hp_max
	dmg = big.dmg
	speed = big.speed
	radius = big.radius
	attack_range = big.range
	attack_cd = big.cd
	projectile_fx = "rock"
	set_meta("hit_sfx", "hit_stone")
	if light:
		light.texture_scale = 4.0 * 64.0 * 2.0 / 256.0
		light.position = Vector2(0, -sprite_h * 0.5)
	Sfx.play_at("boss_roar", global_position)
	Sfx.play_at("petrify", global_position)
	level.shake(14.0)
	Fx.ring(level, global_position, 320.0, COLD, 0.8)
	Fx.burst(level, global_position + Vector2(0, -120), Color("b8b0a0"), 50, 320.0, 0.9, 0.4)
	power_t = 2.0
	bar()


# ---------------------------------------------------------------- phase 2: Pán žil
func _power_tick(p: Actor, delta: float) -> void:
	power_t -= delta
	if power_t <= 0.0:
		power_i += 1
		power = POWERS[power_i % 4]
		power_t = 9.0 if phase == 2 else 7.5
		power_tick = 0.0
		var col: Color = POWER_COL[power]
		level.float_text(top_pos() + Vector2(0, -20), L.t(POWER_NAME[power]), col)
		Fx.ring(level, global_position, 260.0, col, 0.7)
		Sfx.play_at("buff", global_position)
		_power_start(p)
	power_tick -= delta
	if power_tick > 0.0:
		_gaze_tick(p, delta)
		return
	match power:
		"voda":
			power_tick = 2.2
			var q := p.global_position + Vector2(randf_range(-90, 90), randf_range(-60, 60))
			if not level.is_solid(q):
				var z := BossHazard.spawn(self, q, 95.0, 7.0, POWER_COL.voda, "cold", dmg * 0.25, 0.9)
				z.status_id = "slow"
		"ohen":
			power_tick = 0.45 if phase == 2 else 0.35
			var q2 := p.global_position + Vector2.RIGHT.rotated(randf() * TAU) * randf_range(0.0, 140.0)
			slam(q2, 70.0, 1.0, 0.8, "fire", POWER_COL.ohen, {}, func(a): a.apply_status("burn", 2.0, {"dps": dmg.x * 0.15, "src": self}))
		"smrt":
			power_tick = 3.2
			if p.global_position.distance_to(global_position) < 320.0:
				busy = 1.4
				set_pose("attack", 1.4)
				face_to(p.global_position)
				slam(global_position, 190.0, 1.35, 2.2, "physical", POWER_COL.smrt, {"knock": 420.0})
				later(1.35, func(): level.shake(12.0))
		"kamen":
			power_tick = 0.1
			_gaze_tick(p, delta)


func _power_start(p: Actor) -> void:
	gaze.default_color.a = 0.0
	match power:
		"voda":
			for i in 4:
				var q := p.global_position + Vector2.RIGHT.rotated(TAU * i / 4.0 + randf()) * randf_range(80.0, 220.0)
				if not level.is_solid(q):
					var z := BossHazard.spawn(self, q, 110.0, 8.0, POWER_COL.voda, "cold", dmg * 0.25, 1.0)
					z.status_id = "slow"
			Sfx.play_at("water_splash", global_position)
		"kamen":
			Sfx.play_at("petrify", global_position, 0.7)
		"smrt":
			Sfx.play_at("ghost_wail", global_position)


func _gaze_tick(p: Actor, delta: float) -> void:
	if power != "kamen":
		gaze.default_color.a = 0.0
		return
	var eye := global_position + Vector2(0, -sprite_h * 0.6)
	gaze.set_point_position(0, eye)
	var in_front := signf(p.global_position.x - global_position.x) == float(facing) or absf(p.global_position.x - global_position.x) < 40.0
	var los: bool = level.line_of_sight(global_position, p.global_position) and p.global_position.distance_to(global_position) < 640.0
	if not (in_front and los):
		gaze.default_color = Color(0.85, 0.95, 0.4, 0.05)
		gaze.set_point_position(1, eye + Vector2(facing * 200.0, 0))
		if p.petrify < 0.6:
			p.remove_meta("pm_locked")
		return
	gaze.set_point_position(1, p.global_position + Vector2(0, -50))
	gaze.default_color = Color(0.85, 0.95, 0.4, 0.3 + p.petrify * 0.4)
	if p.has_meta("pm_locked"):
		if p.petrify < 0.6:
			p.remove_meta("pm_locked")
		return
	p.petrify = minf(1.2, p.petrify + delta * 0.5)
	if p.petrify >= 1.0:
		p.set_meta("pm_locked", true)
		p.petrify = 1.2
		Sfx.play_at("petrify", p.global_position)


func _special(p: Actor, d: float) -> float:
	if d > 220.0 and level.line_of_sight(global_position, p.global_position):
		face_to(p.global_position)
		set_pose("attack", 0.6)
		shoot(p.global_position, "rock", 320.0, 0.8, "physical", Color(0, 0, 0, 0), 3, 0.2)
		return randf_range(3.0, 4.0)
	busy = 1.0
	set_pose("attack", 1.0)
	cone(p.global_position - global_position, 220.0, 90.0, 0.9, 1.3, "physical", Color("b8b0a0"))
	return randf_range(3.5, 5.0)


# ---------------------------------------------------------------- phase 3: Desátek
func _begin_tithe() -> void:
	if phase != 2:
		return
	phase = 3
	say("half", 6.0)
	var lp: Vector2 = altar.global_position + Vector2(0, 50) if altar else open_spot_near(home, 60.0, 160.0)
	var p := pl()
	if p:
		Fx.bolt(level, p.global_position + Vector2(0, -60), lp + Vector2(0, -90), COLD, 5.0, 0.6)
		p.apply_status("darkness", 2.0)
	lamp = spawn_custom("res://scripts/actors/bosses/permonik_lamp.gd", "permonik", lp, mlvl)
	lamp.hp_max = hp_max * 0.08
	lamp.hp = lamp.hp_max
	lamp.dmg = dmg * 0.5
	lamp.died.connect(_on_lamp_broken)
	Sfx.play_at("portal", lp)
	Game.msg(L.t({"cs": "Permoník ti vzal světlo. Rozbij kahan!", "en": "Permoník has taken your light. Smash the lamp!"}), COLD)
	last_hp = -1.0


func _always_tick(_delta: float) -> void:
	if phase != 3 or lamp_broken:
		return
	var p := pl()
	if p == null:
		return
	p.apply_status("darkness", 0.6)
	if p.lamp:
		p.lamp.energy = 0.35
	if last_hp >= 0.0 and p.hp < last_hp - p.hp_max * 0.004:
		tithe_hits += 1
		if tithe_hits % 10 == 0:
			p.take_damage(p.hp_max * 0.1, "physical", self, {"no_stun": true})
			level.float_text(p.top_pos() + Vector2(0, -30), L.t({"cs": "DESÁTEK!", "en": "THE TITHE!"}), Color("ff4a4a"), true)
			Fx.burst(level, p.global_position + Vector2(0, -50), Color("ff4a4a"), 18, 100.0, 0.6, 0.3, true)
			Sfx.play_at("laugh_permonik", global_position, 0.7)
		else:
			level.float_text(p.top_pos() + Vector2(0, -30), "%d/10" % (tithe_hits % 10), Color("9fb4c8"), true)
	last_hp = p.hp


func _restore_light() -> void:
	var p: Player = level.player
	if p and is_instance_valid(p) and p.lamp:
		p.lamp.energy = 1.15
		p.status.erase("darkness")


func _on_lamp_broken(_a: Actor) -> void:
	if lamp_broken:
		return
	lamp_broken = true
	_restore_light()
	Fx.ring(level, lamp.global_position, 400.0, COLD, 1.0)
	Fx.burst(level, lamp.global_position + Vector2(0, -90), COLD, 60, 300.0, 1.0, 0.4, true)
	Sfx.play_at("frost_hit", lamp.global_position)
	Sfx.play_at("explosion", lamp.global_position)
	level.shake(14.0)
	Game.msg(L.t({"cs": "Kahan se roztříštil. Srdce hory puklo.", "en": "The lamp shatters. The heart of the mountain cracks."}), COLD)
	later(1.0, func():
		hp = 0.0
		die(pl()))


func die(killer: Node) -> void:
	if dead:
		return
	_poof_copies()
	_restore_light()
	if is_instance_valid(gaze):
		gaze.default_color.a = 0.0
	if lamp and is_instance_valid(lamp) and not lamp.dead:
		vanish(lamp)
	super.die(killer)
	if not finished:
		finished = true
		Sfx.music("victory_sting")
		get_tree().create_timer(7.5).timeout.connect(Game.finish_game)


func on_quest_prop(prop: PropNode, _p: Player) -> void:
	Game.on_event("use", prop.id)
	var txt := {"cs": "Oltář je ledový. Nad ním visí tvůj kahan.", "en": "The altar is ice-cold. Your lamp hangs above it."} if phase == 3 else {"cs": "Studený kámen. Čeká na světlo.", "en": "Cold stone. It waits for a light."}
	level.float_text(prop.global_position + Vector2(0, -120), L.t(txt), COLD)


func _test_poke(p: Player, n: int) -> void:
	if phase == 1 and n % 4 == 0:
		for m in alive_minions():
			if m.has_method("poof"):
				m.take_damage(10.0, "physical", p)
				break
	if phase == 3 and lamp and is_instance_valid(lamp) and not lamp.dead and n % 2 == 0:
		lamp.take_damage(lamp.hp_max * 0.12, "physical", p)
	super._test_poke(p, n)
