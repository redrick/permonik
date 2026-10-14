class_name Monster
extends Actor

var id := ""
var data := {}
var kind := "normal"
var ai := "melee"
var dmg := Vector2(1, 3)
var element := "physical"
var attack_range := 50.0
var attack_cd := 1.4
var cd := 0.0
var aggro := false
var aggro_range := 520.0
var home := Vector2.ZERO
var repath_t := 0.0
var windup := 0.0
var think_t := 0.0
var wander_t := 0.0
var abilities: Array = []
var champ_mods: Array = []
var champ_name := ""
var xp_value := 0
var projectile_fx := ""
var pack_leader: Monster = null
var ability_t := 3.0
var stolen_gold := 0
var flee_t := 0.0
var revived := false
var phase_walls := false
var light: PointLight2D
var summoner: Monster = null
var no_drops := false
var minion_of: Monster = null


# Tuned with debug/probe.gd so a pack of same-level monsters is a fight, not a wipe. Keyed by monster level:
# the dip over 9-27 covers the gap between tier-1 weapons (qlvl <= 12) and forged ones (qlvl 25+).
const HP_CURVE := [[1, 0.6], [8, 0.6], [14, 0.45], [24, 0.42], [28, 0.6]]
const DMG_CURVE := [[1, 0.65], [8, 0.6], [14, 0.45], [99, 0.45]]
const BOSS_HP := 0.85
const DIFF_DMG := [1.0, 1.15, 1.3]


static func curve(pts: Array, x: float) -> float:
	if x <= pts[0][0]:
		return pts[0][1]
	for i in range(1, pts.size()):
		if x <= pts[i][0]:
			return lerpf(pts[i - 1][1], pts[i][1], (x - pts[i - 1][0]) / float(pts[i][0] - pts[i - 1][0]))
	return pts.back()[1]


static func f_hp(l: float) -> float:
	return pow(l, 1.6) + 4.0 * l


static func f_dmg(l: float) -> float:
	return pow(l, 1.15) + 3.0 * l


func setup(mid: String, level_n: int, lv: Node, champion := false) -> void:
	id = mid
	level = lv
	data = DB.monster(mid)
	team = 1
	kind = "boss" if data.get("boss", false) else ("champion" if champion else "normal")
	var base_l := float(maxi(1, int(data.get("level", 1))))
	mlvl = clampi(level_n + (3 if kind == "boss" else (2 if champion else 0)), 1, 99)
	var di := clampi(Game.difficulty, 0, 2)
	var lv_n := float(mlvl - [0, 30, 60][di])
	var hpm : float = f_hp(mlvl) / f_hp(base_l) * [1.0, 1.6, 2.4][di] * (BOSS_HP if kind == "boss" else curve(HP_CURVE, lv_n))
	hp_max = float(data.get("hp", 10)) * hpm * (3.0 if champion else 1.0)
	hp = hp_max
	var dm: float = f_dmg(mlvl) / f_dmg(base_l) * curve(DMG_CURVE, lv_n) * DIFF_DMG[di]
	var dd = data.get("dmg", [1, 3])
	dmg = Vector2(float(dd[0]), float(dd[1])) * dm * (1.4 if champion else 1.0)
	armor = int(float(data.get("armor", 5)) * float(mlvl) / base_l)
	speed = float(data.get("speed", 80))
	attack_range = float(data.get("attack_range", 50))
	attack_cd = float(data.get("attack_cd", 1.4))
	element = str(data.get("element", "physical"))
	resist = data.get("resist", {}).duplicate()
	radius = float(data.get("size", 18))
	ai = str(data.get("ai", "melee"))
	abilities = data.get("abilities", [])
	projectile_fx = str(data.get("projectile", "")) if data.get("projectile", null) else ""
	xp_value = int(float(data.get("xp_mult", 1.0)) * 12.0 * pow(mlvl, 1.55) * (3.0 if champion else 1.0))
	display_name = L.t(data.get("name", mid))
	phase_walls = ai == "phaser" or "through_walls" in abilities
	collision_layer = 4
	collision_mask = 2 | 4 | (0 if phase_walls else 1)
	var textures := {}
	for p in ["idle", "walk", "attack"]:
		var t := DB.tex("sprites/monsters/%s_%s" % [mid, p])
		if t:
			textures[p] = t
	if textures.is_empty():
		var sz := int(clampf(radius * 6.0, 64, 400))
		textures["idle"] = DB.placeholder(mid, Vector2i(sz, sz), Color.from_hsv(float(hash(mid) % 360) / 360.0, 0.4, 0.6))
	var no_shadow := mid.begins_with("permonik") or bool(data.get("no_shadow", false)) or "no_shadow" in abilities
	var flying := ai in ["flyer", "phaser"] or "fly" in abilities
	set_meta("hit_sfx", "hit_bone" if mid.begins_with("kost") else ("hit_stone" if mid in ["kamenny_had", "smolak", "bazilisek", "permonik_obr"] else "hit_flesh"))
	setup_visual(textures, not no_shadow, radius * 3.0 * (0.7 if flying else 1.0))
	if flying:
		float_h = 18.0
	if phase_walls:
		modulate.a = 0.82
	var lt = data.get("light", null)
	if lt is Dictionary:
		light = Fx.make_light(Color(lt.get("color", "#ffffff")), float(lt.get("radius", 2)) * 64.0, 0.9)
		light.position = Vector2(0, -sprite_h * 0.5)
		add_child(light)
	if champion:
		_make_champion()
	if kind == "boss":
		aggro_range = 700.0


func _make_champion() -> void:
	var names: Array = DB.champions.get("names", [])
	champ_name = L.t(names.pick_random()) if names.size() > 0 else display_name
	var mods: Dictionary = DB.champions.get("mods", {})
	var keys := mods.keys()
	keys.shuffle()
	for k in keys.slice(0, randi_range(1, 2)):
		champ_mods.append(k)
		for m in mods[k].get("mods", []):
			_champ_stat(str(m.get("stat", "")), float(m.get("value", m.get("max", 0))))
	sprite.scale = Vector2.ONE * 1.15
	mat_set("outline_color", Color(0.85, 0.65, 0.25, 1))


func _champ_stat(stat: String, v: float) -> void:
	match stat:
		"move_speed":
			speed *= 1.0 + v / 100.0
		"attack_speed":
			attack_cd /= 1.0 + v / 100.0
		"armor_pct":
			armor = int(armor * (1.0 + v / 100.0))
		"hp_pct":
			hp_max *= 1.0 + v / 100.0
			hp = hp_max
		"dmg_pct":
			dmg *= 1.0 + v / 100.0
		"fire_dmg":
			element = "fire"
			dmg *= 1.2
		"cold_dmg":
			element = "cold"
			dmg *= 1.15
		"lightning_dmg":
			element = "lightning"
			dmg *= 1.25
		"life_steal":
			abilities = abilities + ["life_steal"]
		"res_all":
			for e in ["fire", "lightning", "cold", "poison"]:
				resist[e] = mini(95, int(resist.get(e, 0)) + int(v))
		"invisible":
			modulate.a = 0.35
		"curse":
			abilities = abilities + ["curse"]


func label_name() -> String:
	return champ_name if champ_name != "" else display_name


func label_sub() -> String:
	if kind == "boss":
		return L.t(data.get("title", ""))
	if champ_mods.is_empty():
		return ""
	var mods: Dictionary = DB.champions.get("mods", {})
	return ", ".join(champ_mods.map(func(k): return L.t(mods.get(k, {}).get("name", k)))) + " · " + display_name


func player() -> Actor:
	return Game.player if Game.player and not Game.player.dead else null


func dist_to_player() -> float:
	var p := player()
	return p.global_position.distance_to(global_position) if p else 99999.0


func _ai(delta: float) -> void:
	cd = maxf(0.0, cd - delta)
	ability_t -= delta
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
		if d < aggro_range * (1.0 if level.lit(global_position) or d < 260 else 0.6) and level.line_of_sight(global_position, p.global_position):
			wake()
		else:
			_wander(delta)
			return
	if not Game.known.has("monster:" + id):
		Game.learn("monster", id)
	if windup > 0.0:
		windup -= delta
		velocity = Vector2.ZERO
		moving = false
		if windup <= 0.0:
			_strike(p)
		return
	if flee_t > 0.0:
		flee_t -= delta
		var away := (global_position - p.global_position).normalized()
		velocity = away * speed * 1.3 * speed_mult()
		face_to(global_position + away)
		moving = true
		return
	if ability_t <= 0.0:
		ability_t = randf_range(4.0, 8.0)
		if _use_ability(p, d):
			return
	match ai:
		"ranged", "caster":
			_ai_ranged(p, d, delta)
		"charger":
			_ai_charger(p, d, delta)
		"exploder":
			_ai_melee(p, d, delta, 1.0)
		"swarm", "flyer":
			_ai_melee(p, d, delta, 1.0, true)
		"summoner":
			_ai_ranged(p, d, delta)
		_:
			_ai_melee(p, d, delta)


func wake() -> void:
	if aggro:
		return
	aggro = true
	for m in level.actors_of_team(1):
		if m != self and not m.aggro and m.global_position.distance_to(global_position) < 260:
			m.aggro = true
	if kind == "boss":
		_on_boss_aggro()


func _on_boss_aggro() -> void:
	var lines: Dictionary = data.get("lines", {})
	if lines.has("aggro"):
		level.boss_say(self, L.t(lines.aggro))
	Sfx.play("boss_roar")


func _wander(delta: float) -> void:
	wander_t -= delta
	if wander_t <= 0.0:
		wander_t = randf_range(2.0, 5.0)
		if randf() < 0.5:
			var tgt := home + Vector2(randf_range(-120, 120), randf_range(-120, 120))
			if not level.is_solid(tgt):
				path = [tgt]
	follow_path(delta, speed * 0.4 * speed_mult())


func _chase(p: Actor, delta: float, spd_mult := 1.0, erratic := false) -> void:
	repath_t -= delta
	var target := p.global_position
	if erratic:
		target += Vector2(sin(anim_t * 3.0 + get_instance_id()), cos(anim_t * 2.3)) * 40.0
	if level.line_of_sight(global_position, target) or phase_walls:
		path = [target]
	elif repath_t <= 0.0 or path.is_empty():
		repath_t = 0.6
		set_path_to(target)
	follow_path(delta, speed * spd_mult * speed_mult())


func _ai_melee(p: Actor, d: float, delta: float, spd := 1.0, erratic := false) -> void:
	if d <= attack_range + p.radius:
		velocity = Vector2.ZERO
		moving = false
		face_to(p.global_position)
		if cd <= 0.0:
			_begin_attack()
		return
	_chase(p, delta, spd, erratic)


func _ai_ranged(p: Actor, d: float, delta: float) -> void:
	var los : bool = level.line_of_sight(global_position, p.global_position)
	if d < 170.0 and los:
		var away := (global_position - p.global_position).normalized()
		var tgt := global_position + away * 60.0
		if not level.is_solid(tgt):
			path = [tgt]
			follow_path(delta, speed * speed_mult())
			return
	if d <= attack_range and los:
		velocity = Vector2.ZERO
		moving = false
		face_to(p.global_position)
		if cd <= 0.0:
			_begin_attack()
		return
	_chase(p, delta)


var charging := 0.0
var charge_dir := Vector2.ZERO


func _ai_charger(p: Actor, d: float, delta: float) -> void:
	if charging > 0.0:
		charging -= delta
		velocity = charge_dir * speed * 3.2 * speed_mult()
		moving = true
		if d < attack_range + p.radius + 10:
			charging = 0.0
			Combat.monster_hit_player(self, p, dmg * 1.5, element, {"knock": 380.0})
			cd = attack_cd
		elif get_slide_collision_count() > 0 and charging < 0.9:
			charging = 0.0
			stun_t = 0.6
		return
	if d > 160 and d < 480 and cd <= 0.0 and level.line_of_sight(global_position, p.global_position):
		charge_dir = (p.global_position - global_position).normalized()
		charging = 1.1
		face_to(p.global_position)
		set_pose("attack", 1.1)
		if abilities.has("shout") or id == "hejkal":
			level.float_text(top_pos(), "HÉÉJ!", Color("e8d9a0"))
		return
	_ai_melee(p, d, delta)


func _begin_attack() -> void:
	windup = 0.28 if kind != "boss" else 0.4
	play_swing(windup + 0.25, windup, "attack", "cast" if ai in ["ranged", "caster", "summoner"] else "melee")
	cd = attack_cd * randf_range(0.85, 1.15)


func _strike(p: Actor) -> void:
	if p == null:
		return
	face_to(p.global_position)
	if ai in ["ranged", "caster", "summoner"]:
		_shoot(p.global_position)
		return
	if ai == "exploder" or abilities.has("explode"):
		explode()
		return
	if dist_to_player() <= attack_range + p.radius + 24:
		var ok := Combat.monster_hit_player(self, p, dmg, element)
		if ok:
			_on_melee_hit(p)
		Sfx.play_at("swing", global_position, 0.6)


func _on_melee_hit(p: Actor) -> void:
	if abilities.has("steal_gold") and Game.ch.gold > 0:
		var g := mini(Game.ch.gold, randi_range(5, 20 + mlvl * 4))
		Game.ch.gold -= g
		stolen_gold += g
		level.float_text(top_pos(), "-%d" % g, Color("e9c46a"))
		Sfx.play("gold")
		flee_t = 3.0
	if abilities.has("drain_mana"):
		Game.ch.mana = maxf(0.0, Game.ch.mana - dmg.y)
	if abilities.has("life_steal"):
		heal(dmg.y * 0.5)
	if abilities.has("light_drain"):
		p.apply_status("darkness", 6.0)
	if abilities.has("petrify"):
		p.petrify = minf(1.2, p.petrify + 0.25)
	if element == "cold":
		p.apply_status("chill", 1.5)


func _shoot(target: Vector2) -> void:
	var from := global_position + Vector2(0, -sprite_h * 0.4)
	var dir := (target - global_position).normalized()
	var col : Color = Fx.ELEM.get(element, Color(0, 0, 0, 0)) if element != "physical" else Color(0, 0, 0, 0)
	var fx := projectile_fx if projectile_fx != "" else ("" if element != "physical" else "rock")
	var spd := 380.0 if ai == "ranged" else 300.0
	var count := 3 if abilities.has("multishot") else 1
	for i in count:
		var dd := dir.rotated((i - (count - 1) / 2.0) * 0.22)
		var pr := Projectile.spawn(level, global_position, dd, spd, fx, 0, func(a, _p):
			Combat.monster_hit_player(self, a, dmg, element, {"melee": false}), col)
		pr.height = from.y - global_position.y
		pr.height = -pr.height
	Sfx.play_at("bolt_shot" if fx in ["bolt", "arrow"] else ("fire_cast" if element == "fire" else ("lightning_cast" if element == "lightning" else "frost_cast")), global_position, 0.6)


func explode() -> void:
	var r := 110.0
	Fx.ring(level, global_position, r, Fx.ELEM.fire)
	Fx.burst(level, global_position + Vector2(0, -20), Fx.ELEM.fire, 24, 220.0, 0.6, 0.35)
	Sfx.play_at("explosion", global_position)
	var p := player()
	if p and p.global_position.distance_to(global_position) < r:
		Combat.monster_hit_player(self, p, dmg * 1.6, "fire", {"always_hit": true})
	no_drops = false
	hp = 0.0
	die(null)


func _use_ability(p: Actor, d: float) -> bool:
	for a in abilities:
		match a:
			"teleport", "bat_form":
				if d < 600 and randf() < 0.6:
					var tgt : Vector2 = level.random_open_near(p.global_position, 140.0, 220.0)
					if tgt != Vector2.INF:
						Fx.burst(level, global_position + Vector2(0, -30), Color("6b4ea0"), 14, 120.0)
						global_position = tgt
						Fx.burst(level, global_position + Vector2(0, -30), Color("6b4ea0"), 14, 120.0)
						return true
			"heal_pack":
				for m in level.actors_of_team(1):
					if m.global_position.distance_to(global_position) < 240 and m.hp < m.hp_max:
						m.heal(m.hp_max * 0.25)
						Fx.burst(level, m.global_position + Vector2(0, -30), Color("8fe36b"), 10, 80.0, 0.6, 0.2, true)
				return false
			"howl":
				Sfx.play_at("wolf_howl", global_position)
				for m in level.actors_of_team(1):
					if m.global_position.distance_to(global_position) < 300:
						m.speed *= 1.15
						m.wake()
				return false
			"summon":
				if level.actors_of_team(1).size() < 90:
					var sid := str(data.get("summon", "krysa"))
					for i in randi_range(2, 3):
						var pos : Vector2 = level.random_open_near(global_position, 40.0, 120.0)
						if pos != Vector2.INF:
							var m: Monster = level.spawn_monster(sid, pos, mlvl - 2)
							if m:
								m.no_drops = true
								m.xp_value = int(m.xp_value * 0.3)
								m.wake()
					Fx.ring(level, global_position, 120, Color("6b4ea0"))
					return true
			"hook", "chain_pull":
				if d > 120 and d < 420 and level.line_of_sight(global_position, p.global_position):
					Fx.bolt(level, global_position + Vector2(0, -50), p.global_position + Vector2(0, -40), Color("9a9a9a"), 3.0, 0.3)
					Sfx.play_at("chains", global_position)
					p.knock = (global_position - p.global_position).normalized() * 700.0
					return true
			"petrify_spit":
				if d < 420:
					var pr := Projectile.spawn(level, global_position, (p.global_position - global_position), 280.0, "rock", 0, func(a, _p):
						a.petrify = minf(1.2, a.petrify + 0.35)
						Combat.monster_hit_player(self, a, dmg * 0.6, "physical", {"always_hit": true}), Color("bcb6a8"))
					pr.height = 30.0
					return true
			"lure":
				if d < 500 and d > 120:
					p.knock = (global_position - p.global_position).normalized() * 260.0
					Fx.burst(level, p.global_position + Vector2(0, -50), Color("cfe8ff"), 8, 60.0, 0.6, 0.2, true)
					return false
			"fear":
				if d < 300:
					p.apply_status("slow", 2.0)
					level.float_text(p.top_pos(), L.t({"cs": "strach", "en": "fear"}), Color("b0a0d0"), true)
			"poison_pool":
				var pool_pos := global_position
				Fx.ground_mark(level, pool_pos, 70.0, Color("6ab04a"), 6.0)
				var src := self
				for k in 12:
					level.get_tree().create_timer(0.5 * k).timeout.connect(func():
						var pl := Game.player
						if pl and not pl.dead and pl.global_position.distance_to(pool_pos) < 70.0 and is_instance_valid(src):
							pl.take_damage(src.dmg.x * 0.4, "poison", src, {"dot": true}))
			"curse":
				if d < 400:
					p.apply_status("cursed", 6.0)
					Fx.burst(level, p.global_position + Vector2(0, -50), Color("9a6bd8"), 12, 80.0, 0.6, 0.2, true)
			"frenzy":
				if hp < hp_max * 0.4:
					speed *= 1.4
					attack_cd *= 0.7
					abilities = abilities.filter(func(x): return x != "frenzy")
					level.float_text(top_pos(), "!!!", Color("ff5544"))
	return false


func _on_damaged(_amount: float, _element: String, _source: Node) -> void:
	if not aggro:
		wake()
	if kind == "boss":
		Game.boss_bar.emit(label_name(), hp / hp_max, true)
		if hp < hp_max * 0.5 and not get_meta("half_said", false):
			set_meta("half_said", true)
			var lines: Dictionary = data.get("lines", {})
			if lines.has("half"):
				level.boss_say(self, L.t(lines.half))


func _on_hit_recover() -> void:
	windup = 0.0
	if kind != "boss":
		set_pose("idle")


func die(killer: Node) -> void:
	if dead:
		return
	if abilities.has("revive") and not revived and kind != "boss":
		revived = true
		hp = 0.01
		dead = false
		_revive_later()
		return
	super.die(killer)
	if light:
		create_tween().tween_property(light, "energy", 0.0, 0.5)
	level.on_monster_died(self)
	var snd := "death_bone" if id.begins_with("kost") else ("death_ghost" if ai == "phaser" or id in ["bludicka", "navka", "mura", "svetlonos"] else ("death_beast" if id in ["vlk", "vlkodlak", "cerny_pes", "krysa", "netopyr"] else "monster_death"))
	Sfx.play_at(snd if kind != "boss" else "boss_death", global_position)


func _revive_later() -> void:
	collision_layer = 0
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", deg_to_rad(85.0 * facing), 0.3)
	tw.tween_interval(randf_range(2.5, 4.0))
	tw.tween_property(sprite, "rotation", 0.0, 0.4)
	tw.tween_callback(func():
		if is_instance_valid(self) and not dead:
			hp = hp_max * 0.5
			collision_layer = 4
			level.float_text(top_pos(), L.t({"cs": "Vstává!", "en": "Rises!"}), Color("cfe8ff")))
	stun_t = 5.0


func hit_divisor() -> float:
	return 4.0 if kind == "boss" else 8.0
