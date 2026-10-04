class_name Skills
extends RefCounted

const WEAPON_TYPES := ["melee", "melee_arc", "stomp", "leap", "spin"]


static func p(id: String, k: String, default = 0.0):
	var v = Game.ch.skill_param(id, k)
	return default if v == null else v


# Melee skills carry their own attack-rating bonus (ar_pct), as in D2.
static func _strike(id: String, pl: Player, t: Actor, pct: float, opts := {}) -> bool:
	opts["ar_pct"] = float(p(id, "ar_pct", 0.0))
	return Combat.player_strike(pl, t, pct, opts)


static func use(pl: Player, id: String, target: Vector2) -> bool:
	var ch := Game.ch
	var s := DB.skill(id)
	if s.is_empty() or ch.skill_rank(id) <= 0:
		return false
	var type := str(s.get("type", ""))
	if type == "passive":
		Game.msg(L.t("passive"))
		return false
	var req := str(p(id, "requires", ""))
	var w := ch.weapon()
	if req == "ranged" and (w == null or not w.is_ranged()):
		Game.msg(L.t({"cs": "Potřebuji luk nebo kuši.", "en": "I need a bow or crossbow."}))
		return false
	if type in WEAPON_TYPES and w and w.is_ranged():
		Game.msg(L.t({"cs": "S tímhle se to nedá.", "en": "Not with this weapon."}))
		return false
	if pl.cooldowns.has(id):
		return false
	var cost := ch.skill_mana(id)
	if ch.mana < cost:
		Game.msg(L.t("no_mana"), Color("8fa0ff"))
		Sfx.play("no_mana")
		return false
	var pick = pl.level.pick_at(target)
	var tgt: Actor = pick.node if pick and pick.type == "monster" else null
	if type == "melee":
		if tgt == null:
			var hits := Combat.targets_in_cone(pl.level, pl.global_position, (target - pl.global_position).normalized(), 90.0, 80.0, 1)
			if hits.is_empty():
				return false
			tgt = hits[0]
		if pl.global_position.distance_to(tgt.global_position) > 70.0 + tgt.radius:
			pl.intent = {"type": "monster", "node": tgt}
			pl.set_path_to(tgt.global_position)
			return false
	# some skills are paid in life (the priest's sacrifice) or in gold (the alchemist's great work)
	var hpc := float(p(id, "hp_cost", 0.0))
	if hpc > 0.0:
		var hp_take := float(ch.d.hp_max) * hpc / 100.0
		if ch.hp <= hp_take + 1.0:
			Game.msg(L.t({"cs": "Na tu oběť nemám dost krve.", "en": "Not enough blood for that offering."}), Color("e04b4b"))
			return false
		ch.hp -= hp_take
		pl.hp = ch.hp
	var gc := int(p(id, "gold_cost", 0.0))
	if gc > 0:
		if ch.gold < gc:
			Game.msg(L.t({"cs": "Na tu proměnu nemám dost grošů.", "en": "Not enough gold for that transmutation."}), UiTheme.GOLD)
			return false
		ch.gold -= gc
	ch.mana -= cost
	var cdv := float(s.get("cooldown", 0))
	if cdv > 0:
		pl.cooldowns[id] = cdv
	pl.face_to(target)
	var elem := str(s.get("element", "physical"))
	var col: Color = Fx.ELEM.get(elem, Color.WHITE)
	var weapon_dur := 1.0 / float(ch.d.get("aps", 1.2))
	var cast_dur := 0.42 / float(ch.d.get("cast_speed", 1.0))
	match type:
		"melee":
			var hits_n := int(p(id, "hits", 1.0))
			pl.lunge = 10.0
			pl.start_action("attack", weapon_dur * (1.0 + 0.3 * (hits_n - 1)), 0.55, func():
				for i in hits_n:
					if is_instance_valid(tgt) and not tgt.dead:
						_strike(id, pl, tgt, float(p(id, "dmg_pct", 100.0)), {"status": {"stun": float(p(id, "stun", 0.0))}, "knock": 80.0})
				Sfx.play_at("swing_heavy", pl.global_position))
		"melee_arc":
			pl.lunge = 8.0
			var dir := (target - pl.global_position).normalized()
			pl.start_action("attack", weapon_dur, 0.55, func():
				Sfx.play_at("swing_heavy", pl.global_position)
				_arc_fx(pl, dir, 110.0, float(p(id, "arc", 100.0)))
				for t in Combat.targets_in_cone(pl.level, pl.global_position, dir, 110.0, float(p(id, "arc", 100.0)), 1):
					_strike(id, pl, t, float(p(id, "dmg_pct", 100.0))))
		"stomp":
			pl.start_action("attack", weapon_dur * 1.1, 0.6, func():
				var r := float(p(id, "radius", 100.0))
				Fx.ring(pl.level, pl.global_position, r, Color("d8c8a0"))
				Fx.burst(pl.level, pl.global_position, Color("a89878"), 20, 160.0, 0.5, 0.3)
				Sfx.play_at("hit_stone", pl.global_position)
				pl.level.shake(6.0)
				for t in Combat.targets_in_radius(pl.level, pl.global_position, r, 1):
					_strike(id, pl, t, float(p(id, "dmg_pct", 100.0)), {"always_hit": true, "status": {"stun": float(p(id, "stun", 0.5))}})
					_fear(id, t))
		"leap":
			var dest : Vector2 = pl.level.clamp_walkable(pl.global_position, target, 380.0)
			pl.invuln = 0.5
			pl.collision_mask = 1
			var from := pl.global_position
			var tw := pl.create_tween()
			pl.start_action("attack", 0.5, 0.01, func(): pass)
			tw.tween_method(func(t):
				pl.global_position = from.lerp(dest, t)
				pl.float_h = sin(t * PI) * 60.0, 0.0, 1.0, 0.42)
			tw.tween_callback(func():
				pl.global_position = dest
				pl.float_h = 0.0
				pl.collision_mask = 1 | 4 | 8
				var r := float(p(id, "radius", 80.0))
				Fx.ring(pl.level, dest, r, Color("e8d0a0"))
				pl.level.shake(5.0)
				Sfx.play_at("hit_stone", dest)
				for t in Combat.targets_in_radius(pl.level, dest, r, 1):
					_strike(id, pl, t, float(p(id, "dmg_pct", 100.0)), {"always_hit": true, "knock": 220.0}))
		"spin":
			var dir := (target - pl.global_position).normalized()
			var length := float(p(id, "length", 250.0))
			var dest : Vector2 = pl.level.clamp_walkable(pl.global_position, pl.global_position + dir * length, length)
			var hit := []
			pl.invuln = 0.3
			pl.start_action("attack", 0.55, 0.01, func(): pass)
			var start := pl.global_position
			var tw := pl.create_tween()
			tw.tween_method(func(t):
				pl.global_position = start.lerp(dest, t)
				pl.sprite.rotation = t * TAU * 2.0
				for m in Combat.targets_in_radius(pl.level, pl.global_position, 70.0, 1):
					if not m in hit:
						hit.append(m)
						_strike(id, pl, m, float(p(id, "dmg_pct", 100.0)))
						Sfx.play_at("swing", pl.global_position, 0.6), 0.0, 1.0, 0.5)
			tw.tween_callback(func(): pl.sprite.rotation = 0.0)
		"projectile":
			var weapon_based : bool = s.get("params", {}).has("dmg_pct")
			pl.start_action("attack" if weapon_based else "cast", weapon_dur if weapon_based else cast_dur, 0.5, func():
				_fire_projectiles(pl, id, target, elem, col, weapon_based))
		"chain":
			pl.start_action("cast", cast_dur, 0.5, func():
				Sfx.play_at("lightning_cast", pl.global_position)
				var dmg: Vector2 = p(id, "dmg", Vector2(1, 4))
				var jumps := int(p(id, "jumps", 3.0))
				var rng := float(p(id, "range", 260.0))
				var cur: Vector2 = pl.global_position + Vector2(0, -60)
				var first: Actor = tgt
				if first == null:
					var c := Combat.targets_in_cone(pl.level, pl.global_position, (target - pl.global_position).normalized(), 420.0, 60.0, 1)
					first = _closest(c, pl.global_position)
				var hitl := []
				var t := first
				for i in jumps + 1:
					if t == null:
						if i == 0:
							Fx.bolt(pl.level, cur, target, col)
						break
					Fx.bolt(pl.level, cur, t.center_pos(), col)
					Combat.player_spell_hit(pl, t, Combat.spell_damage(dmg, id), elem)
					hitl.append(t)
					cur = t.center_pos()
					var cands := Combat.targets_in_radius(pl.level, t.global_position, rng, 1).filter(func(x): return not x in hitl)
					t = _closest(cands, t.global_position))
		"nova":
			pl.start_action("cast", cast_dur, 0.5, func():
				var r := float(p(id, "radius", 160.0))
				Fx.ring(pl.level, pl.global_position, r, col)
				Fx.burst(pl.level, pl.global_position + Vector2(0, -20), col, 30, r * 1.6, 0.5, 0.3)
				Sfx.play_at(elem_sfx(elem, true), pl.global_position)
				var fr := float(p(id, "freeze", 0.0))
				for t in Combat.targets_in_radius(pl.level, pl.global_position, r, 1):
					Combat.player_spell_hit(pl, t, Combat.spell_damage(p(id, "dmg", Vector2(1, 4)), id), elem,
						{"status": {"freeze": fr} if fr > 0.0 else {"slow": float(p(id, "slow", 0.0))}})
					_fear(id, t))
		"cone":
			var dir := (target - pl.global_position).normalized()
			pl.start_action("cast", cast_dur, 0.5, func():
				var rr := float(p(id, "range", 240.0))
				var arc := float(p(id, "arc", 60.0))
				Sfx.play_at(elem_sfx(elem, false), pl.global_position)
				for i in 10:
					var dd := dir.rotated(randf_range(-deg_to_rad(arc) / 2, deg_to_rad(arc) / 2))
					var pr := Projectile.spawn(pl.level, pl.global_position, dd, rr * 2.2, "ice_shard" if elem == "cold" else "", 1, func(_a, _p): pass, col)
					pr.life = 0.45
				for t in Combat.targets_in_cone(pl.level, pl.global_position, dir, rr, arc, 1):
					Combat.player_spell_hit(pl, t, Combat.spell_damage(p(id, "dmg", Vector2(1, 4)), id), elem, {"status": {"slow": float(p(id, "slow", 2.0))}}))
		"area":
			var pos := target
			pl.start_action("cast", cast_dur, 0.5, func():
				Sfx.play_at(elem_sfx(elem, false), pl.global_position)
				AreaZone.create(pl, id, pos, elem, col))
		"wall":
			var pos := target
			var dir := (target - pl.global_position).normalized()
			pl.start_action("cast", cast_dur, 0.5, func():
				Sfx.play_at("fire_cast", pl.global_position)
				AreaZone.create_wall(pl, id, pos, dir, elem, col))
		"trap":
			var pos := target
			pl.start_action("cast", cast_dur, 0.5, func():
				Sfx.play_at("trap_snap", pos)
				for i in int(p(id, "count", 1.0)):
					AreaZone.create_trap(pl, id, pos + Vector2(randf_range(-40, 40), randf_range(-30, 30)) * (1 if i > 0 else 0), elem, col))
		"cloud":
			var pos := target
			pl.start_action("cast", cast_dur, 0.5, func():
				Sfx.play_at("smoke", pos)
				AreaZone.create_cloud(pl, id, pos))
		"summon":
			pl.start_action("cast", cast_dur, 0.5, func():
				for i in int(p(id, "count", 1.0)):
					Summon.create(pl, id, pl.global_position + Vector2(randf_range(-40, 40), -20)))
		"buff":
			pl.start_action("cast", cast_dur, 0.5, func():
				var mods := {}
				for k in s.get("params", {}):
					if k != "duration":
						var v = p(id, k)
						if v is float:
							mods[k] = v
				var form := str(s.get("params", {}).get("form", ""))
				Game.ch.add_buff(id, mods, float(p(id, "duration", 30.0)), form)
				Game.ch.changed.emit()
				Fx.ring(pl.level, pl.global_position, 90.0, col if elem != "physical" else Color("ffd27a"))
				Fx.burst(pl.level, pl.global_position + Vector2(0, -50), col if elem != "physical" else Color("ffd27a"), 18, 90.0, 0.8, 0.25, true)
				Sfx.play("buff")
				if id == "zdar_buh":
					pl.level.float_text(pl.top_pos(), "ZDAŘ BŮH!", Color("ffd27a"), true)
					for m in Combat.targets_in_radius(pl.level, pl.global_position, 260.0, 1):
						if m.kind == "normal" and randf() < 0.5:
							m.flee_t = 2.5)
		_:
			return false
	return true


# A howl or a song that sends ordinary monsters running for a while.
static func _fear(id: String, t: Actor) -> void:
	var f := float(p(id, "fear", 0.0))
	if f > 0.0 and is_instance_valid(t) and t.get("kind") == "normal":
		t.flee_t = maxf(t.flee_t, f)


static func elem_sfx(e: String, cast: bool) -> String:
	match e:
		"fire":
			return "fire_cast" if cast else "fire_hit"
		"lightning":
			return "lightning_cast" if cast else "lightning_hit"
		"cold":
			return "frost_cast" if cast else "frost_hit"
	return "swing_heavy"


static func _closest(arr: Array, pos: Vector2) -> Actor:
	var best: Actor = null
	var bd := INF
	for a in arr:
		var dd: float = a.global_position.distance_to(pos)
		if dd < bd:
			bd = dd
			best = a
	return best


static func _arc_fx(pl: Player, dir: Vector2, r: float, arc: float) -> void:
	var line := Line2D.new()
	var half := deg_to_rad(arc) / 2.0
	for i in 9:
		var a := dir.angle() - half + half * 2.0 * i / 8.0
		line.add_point(pl.global_position + Vector2(cos(a), sin(a) * 0.65) * r * 0.85 + Vector2(0, -40))
	line.width = 10.0
	line.default_color = Color(1, 0.95, 0.85, 0.6)
	var g := Gradient.new()
	g.set_color(0, Color(1, 1, 1, 0))
	g.set_color(1, Color(1, 1, 1, 0.8))
	line.gradient = g
	pl.level.fx_root.add_child(line)
	var tw := line.create_tween()
	tw.tween_property(line, "modulate:a", 0.0, 0.2)
	tw.tween_callback(line.queue_free)


static func _fire_projectiles(pl: Player, id: String, target: Vector2, elem: String, col: Color, weapon_based: bool) -> void:
	var count := int(p(id, "count", 1.0))
	var spread := deg_to_rad(float(p(id, "spread", 10.0)))
	var spd := float(p(id, "speed", 500.0))
	var fx := str(p(id, "fx", ""))
	var pierce := int(p(id, "pierce", 0.0))
	var ret := int(p(id, "returns", 0.0)) > 0
	var exr := float(p(id, "explode_radius", 0.0))
	var pct := float(p(id, "dmg_pct", 100.0))
	var dmg = p(id, "dmg", null)
	var dir := (target - pl.global_position).normalized()
	var rain := id == "dest_sipu"
	Sfx.play_at({"valaska": "axe_throw", "bolt": "bolt_shot", "arrow": "arrow_shot"}.get(fx, elem_sfx(elem, true)), pl.global_position)
	for i in count:
		var dd := dir.rotated((i - (count - 1) / 2.0) * spread) if count > 1 else dir
		if rain:
			var spot := target + Vector2(randf_range(-110, 110), randf_range(-70, 70))
			pl.get_tree().create_timer(randf_range(0.05, 0.5)).timeout.connect(func():
				if not is_instance_valid(pl):
					return
				Fx.sprite_fx(pl.level, fx, spot + Vector2(0, -20), 0.3)
				for t in Combat.targets_in_radius(pl.level, spot, 36.0, 1):
					_strike(id, pl, t, pct, {"always_hit": true})
				Fx.burst(pl.level, spot, Color("c8b898"), 4, 60.0, 0.3, 0.15))
			continue
		var pc := col if elem != "physical" else Color(0, 0, 0, 0)
		var pr := Projectile.spawn(pl.level, pl.global_position, dd, spd, fx, 1, func(a, proj):
			if exr > 0.0:
				_explode(pl, id, proj.global_position, exr, elem, col, dmg, pct, weapon_based)
				return
			if weapon_based:
				var opts := {"ranged": true}
				if elem != "physical":
					opts["element"] = elem
				_strike(id, pl, a, pct, opts)
				if dmg is Vector2:
					Combat.player_spell_hit(pl, a, Combat.spell_damage(dmg, id), elem)
			else:
				Combat.player_spell_hit(pl, a, Combat.spell_damage(dmg if dmg is Vector2 else Vector2(1, 3), id), elem)
				Fx.burst(pl.level, a.center_pos(), col, 8, 100.0, 0.35, 0.2), pc)
		pr.pierce = pierce
		pr.returns = ret
		pr.owner_actor = pl
		if fx == "valaska" or fx == "naloz":
			pr.spin = 14.0
		if id == "naloz" or id == "retez_nalozi":
			pr.life = minf(1.2, pl.global_position.distance_to(target) / spd)
		if id == "hromova_koule":
			pr.vel *= 0.45
			pr.life = 3.0
			pr.pierce = 99
		if id == "zar_ptak":
			pr.homing = 3.0
		if exr > 0.0:
			pr.on_end = func(proj): _explode(pl, id, proj.global_position, exr, elem, col, dmg, pct, weapon_based)


static func _explode(pl: Player, id: String, pos: Vector2, r: float, elem: String, col: Color, dmg, pct: float, weapon_based: bool) -> void:
	if not is_instance_valid(pl):
		return
	Fx.ring(pl.level, pos, r, col)
	Fx.burst(pl.level, pos + Vector2(0, -20), col, 22, r * 2.0, 0.5, 0.32)
	Sfx.play_at("explosion" if elem == "fire" else elem_sfx(elem, false), pos)
	if r > 90:
		pl.level.shake(4.0)
	for t in Combat.targets_in_radius(pl.level, pos, r, 1):
		if dmg is Vector2:
			Combat.player_spell_hit(pl, t, Combat.spell_damage(dmg, id), elem, {"knock": 120.0})
		elif weapon_based:
			_strike(id, pl, t, pct, {"always_hit": true})


static func fire_weapon(pl: Player, target: Vector2, pct: float) -> void:
	var w := Game.ch.weapon()
	var fx := str(w.base().get("projectile", "bolt" if w.kind() == "crossbow" else "arrow")) if w else "arrow"
	Sfx.play_at("bolt_shot" if fx == "bolt" else "arrow_shot", pl.global_position)
	Projectile.spawn(pl.level, pl.global_position, target - pl.global_position, 720.0, fx, 1, func(a, _p):
		Combat.player_strike(pl, a, pct, {"ranged": true}))
