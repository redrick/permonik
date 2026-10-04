class_name Combat
extends RefCounted


static func hit_chance(alvl: int, dlvl: int, ar: float, def: float, lo := 0.05, hi := 0.95) -> float:
	var c := 2.0 * float(alvl) / float(alvl + dlvl) * ar / maxf(1.0, ar + def)
	return clampf(c, lo, hi)


static func player_weapon_damage(pct := 100.0) -> Dictionary:
	var d: Dictionary = Game.ch.d
	var out := {"min": d.dmg_min * pct / 100.0, "max": d.dmg_max * pct / 100.0, "element": "physical", "extra": []}
	for e in ["fire", "lightning", "cold", "poison"]:
		var v := float(d.get(e + "_dmg", 0.0))
		if v > 0.0:
			out.extra.append({"element": e, "min": v * 0.5, "max": v})
	return out


static func player_strike(player: Actor, target: Actor, pct := 100.0, opts := {}) -> bool:
	if target == null or target.dead:
		return false
	var d: Dictionary = Game.ch.d
	var hc := hit_chance(Game.ch.level, target.mlvl, float(d.to_hit) + float(opts.get("to_hit", 0)), float(target.armor), 0.2)
	if not opts.get("always_hit", false) and randf() > hc:
		player.level.float_text(target.top_pos(), L.t({"cs": "vedle", "en": "miss"}), Color("9a948a"))
		Sfx.play_at("swing", player.global_position, 0.5)
		return false
	var dm := player_weapon_damage(pct)
	var crit := randf() * 100.0 < float(d.get("crit", 0.0)) + 3.0
	var amt := randf_range(dm.min, dm.max) * (2.0 if crit else 1.0)
	var total := target.take_damage(amt, opts.get("element", "physical"), player, {"crit": crit, "knock": opts.get("knock", 0.0)})
	for e in dm.extra:
		total += target.take_damage(randf_range(e.min, e.max), e.element, player, {"no_stun": true})
		_elem_status(target, e.element, randf_range(e.min, e.max), player)
	if opts.has("status"):
		for s in opts.status:
			target.apply_status(s, float(opts.status[s]))
	if total > 0.0:
		_leech(total)
		Sfx.play_at(target.get_meta("hit_sfx", "hit_flesh"), target.global_position, 0.8)
		wear_item("weapon", 0.08)
	return true


static func _elem_status(t: Actor, e: String, amount: float, src: Node) -> void:
	match e:
		"cold":
			t.apply_status("chill", 2.0)
		"fire":
			if randf() < 0.3:
				t.apply_status("burn", 2.0, {"dps": amount * 0.25, "src": src})
		"poison":
			t.apply_status("poison", 3.0, {"dps": amount * 0.35, "src": src})


static func _leech(total: float) -> void:
	var ch := Game.ch
	var ls := float(ch.d.get("life_steal", 0.0))
	var ms := float(ch.d.get("mana_steal", 0.0))
	if ls > 0.0:
		ch.hp = minf(ch.d.hp_max, ch.hp + total * ls / 100.0)
	if ms > 0.0:
		ch.mana = minf(ch.d.mana_max, ch.mana + total * ms / 100.0)


static func spell_damage(dmg: Vector2, skill_id := "") -> float:
	var mult := 1.0 + Game.ch.stat("magie") / 100.0
	if skill_id != "":
		mult *= Game.ch.synergy_mult(skill_id)
	return randf_range(dmg.x, dmg.y) * mult


static func player_spell_hit(player: Actor, target: Actor, amount: float, element: String, opts := {}) -> float:
	if target == null or target.dead:
		return 0.0
	var extra_d := float(Game.ch.d.get(element + "_dmg", 0.0)) * 0.5 if element != "physical" else 0.0
	var dealt := target.take_damage(amount + extra_d, element, player, opts)
	if dealt > 0.0:
		_elem_status(target, element, dealt, player)
		if opts.has("status"):
			for s in opts.status:
				target.apply_status(s, float(opts.status[s]))
	return dealt


static func monster_hit_player(m: Actor, p: Actor, dmg: Vector2, element := "physical", opts := {}) -> bool:
	if p == null or p.dead:
		return false
	var ch := Game.ch
	var ar := float(6 + m.mlvl * 6 + int(opts.get("to_hit", 0)))
	if not opts.get("always_hit", false) and randf() > hit_chance(m.mlvl, ch.level, ar, float(ch.d.armor), 0.05, 0.85):
		p.level.float_text(p.top_pos(), L.t({"cs": "uhnul", "en": "dodge"}), Color("9a948a"), true)
		return false
	if element == "physical" and randf() * 100.0 < float(ch.d.get("block", 0)) * (1.0 if not p.moving else 0.5):
		p.level.float_text(p.top_pos(), L.t({"cs": "vykryto", "en": "block"}), Color("d8d0b8"), true)
		Sfx.play_at("block", p.global_position)
		p.set_pose("attack", 0.15)
		wear_item("offhand", 0.3)
		return false
	var amt := randf_range(dmg.x, dmg.y)
	if element == "physical":
		amt = maxf(1.0, amt - float(ch.d.get("dmg_reduce", 0.0)))
	var dealt := p.take_damage(amt, element, m, opts)
	if dealt > 0.0:
		var th := float(ch.d.get("thorns", 0.0))
		if th > 0.0 and opts.get("melee", true):
			m.take_damage(th, "physical", p, {"no_stun": true})
		for sl in ["body", "head", "offhand"]:
			wear_item(sl, 0.05)
	return dealt > 0.0


static func wear_item(slot: String, chance: float) -> void:
	var it: Item = Game.ch.equip.get(slot, null)
	if it == null or it.max_dur <= 0 or randf() > chance:
		return
	it.dur = maxi(0, it.dur - 1)
	if it.dur == 0:
		Game.msg(L.t({"cs": "Rozbilo se: %s", "en": "Broken: %s"}) % it.display_name(), Item.COL_BAD)
		Game.ch.recalc()
		Game.ch.changed.emit()


static func targets_in_radius(level: Node, pos: Vector2, r: float, team: int) -> Array:
	var out := []
	for a in level.actors_of_team(team):
		if not a.dead and a.global_position.distance_to(pos) <= r + a.radius:
			out.append(a)
	return out


static func targets_in_cone(level: Node, pos: Vector2, dir: Vector2, r: float, arc_deg: float, team: int) -> Array:
	var out := []
	var half := deg_to_rad(arc_deg) / 2.0
	for a in level.actors_of_team(team):
		if a.dead:
			continue
		var to: Vector2 = a.global_position - pos
		if to.length() <= r + a.radius and (to.length() < a.radius + 4 or absf(dir.angle_to(to)) <= half):
			out.append(a)
	return out
