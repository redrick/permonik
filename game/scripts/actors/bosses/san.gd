extends BossBase

const HEADS := ["fire", "cold", "poison"]
const NAMES := {"fire": {"cs": "ohnivá", "en": "fire"}, "cold": {"cs": "mrazivá", "en": "frost"}, "poison": {"cs": "jedovatá", "en": "venom"}}

var heads := {"fire": "on", "cold": "on", "poison": "on"}
var regrow_t := {}
var stumps := {}
var breath_i := 0


func _init_boss() -> void:
	set_meta("half_said", true)


func alive_heads() -> Array:
	return HEADS.filter(func(h): return heads[h] == "on")


func missing() -> int:
	return 3 - alive_heads().size()


func _always_tick(delta: float) -> void:
	for h in regrow_t.keys():
		regrow_t[h] -= delta
		if heads[h] == "cut" and regrow_t[h] <= 0.0:
			_regrow(h)
	phase = 1 + missing()


func _after_damage(_amount: float, elem: String, source: Node) -> void:
	if source is Player and elem == "fire":
		for h in regrow_t.keys():
			if heads[h] == "cut":
				_burn_stump(h)
	var alive := alive_heads()
	if alive.size() > 1 and hp < hp_max * (1.0 - 0.333 * (missing() + 1)):
		_cut(alive.pick_random())


func _cut(h: String) -> void:
	heads[h] = "cut"
	regrow_t[h] = 8.0
	Sfx.play_at("boss_roar", global_position)
	level.shake(9.0)
	var q := open_spot_near(global_position, 90.0, 160.0)
	var s := Sprite2D.new()
	var t := DB.tex("sprites/monsters/san_head")
	s.texture = t if t else Fx.soft()
	s.global_position = q
	s.offset = Vector2(0, -s.texture.get_height() * 0.4)
	s.modulate = Fx.ELEM.get(h, Color.WHITE).lerp(Color.WHITE, 0.6)
	level.ysort.add_child(s)
	stumps[h] = s
	var tw := s.create_tween()
	tw.tween_property(s, "rotation", deg_to_rad(randf_range(-60, 60)), 0.4)
	Fx.burst(level, global_position + Vector2(0, -sprite_h * 0.7), Color("8a1f1f"), 20, 200.0, 0.6, 0.3)
	level.float_text(top_pos(), L.t({"cs": "Utnuta %s hlava! Vypal pahýl!", "en": "The %s head is off! Burn the stump!"}) % L.t(NAMES[h]), Color("ffcf8a"))
	if missing() == 1:
		say("half")


func _burn_stump(h: String) -> void:
	heads[h] = "burned"
	regrow_t.erase(h)
	Sfx.play_at("fire_hit", global_position)
	Fx.burst(level, global_position + Vector2(0, -sprite_h * 0.7), Fx.ELEM.fire, 26, 160.0, 0.8, 0.35, true)
	level.float_text(top_pos(), L.t({"cs": "Pahýl vypálen!", "en": "Stump seared!"}), Fx.ELEM.fire)
	if stumps.has(h) and is_instance_valid(stumps[h]):
		var s: Sprite2D = stumps[h]
		s.create_tween().tween_property(s, "modulate", Color(0.25, 0.2, 0.2), 0.6)


func _regrow(h: String) -> void:
	heads[h] = "on"
	regrow_t.erase(h)
	heal(hp_max * 0.15)
	bar()
	Sfx.play_at("boss_roar", global_position, 0.8)
	Fx.burst(level, global_position + Vector2(0, -sprite_h * 0.7), Fx.ELEM.get(h, Color.WHITE), 24, 140.0, 0.7, 0.35, true)
	level.float_text(top_pos(), L.t({"cs": "Hlava dorostla!", "en": "The head grew back!"}), Color("ff6a6a"))
	if stumps.has(h) and is_instance_valid(stumps[h]):
		var s: Sprite2D = stumps[h]
		stumps.erase(h)
		var tw := s.create_tween()
		tw.tween_property(s, "modulate:a", 0.0, 0.5)
		tw.tween_callback(s.queue_free)


func _special(p: Actor, d: float) -> float:
	var alive := alive_heads()
	if alive.is_empty():
		return 3.0
	if d > 340.0 and randf() < 0.5:
		var h: String = alive.pick_random()
		face_to(p.global_position)
		set_pose("attack", 0.6)
		shoot(p.global_position, "firebolt" if h == "fire" else ("ice_shard" if h == "cold" else ""), 320.0, 0.8, h, Fx.ELEM[h], alive.size(), 0.25)
		return randf_range(2.0, 3.0)
	breath_i += 1
	var head: String = alive[breath_i % alive.size()]
	_breath(p, head)
	if alive.size() >= 2 and randf() < 0.4:
		var other: String = alive[(breath_i + 1) % alive.size()]
		later(0.7, func():
			var pp := pl()
			if pp:
				_breath(pp, other))
	return randf_range(2.6, 3.8) - 0.3 * (3 - alive.size())


func _breath(p: Actor, h: String) -> void:
	busy = 1.2
	face_to(p.global_position)
	set_pose("attack", 1.2)
	var col: Color = Fx.ELEM[h]
	shout(L.t(NAMES[h]).to_upper() + "!", L.t(NAMES[h]).to_upper() + "!", col)
	Sfx.play_at("fire_cast" if h == "fire" else ("frost_cast" if h == "cold" else "smoke"), global_position)
	var cb := func(a):
		match h:
			"fire":
				a.apply_status("burn", 3.0, {"dps": dmg.x * 0.3, "src": self})
			"cold":
				a.apply_status("chill", 3.0)
				a.apply_status("freeze", 0.6)
			"poison":
				a.apply_status("poison", 4.0, {"dps": dmg.x * 0.3, "src": self})
	cone(p.global_position - global_position, 300.0, 55.0, 1.0, 1.3, h, col, cb)


func die(killer: Node) -> void:
	for h in stumps.keys():
		if is_instance_valid(stumps[h]):
			var s: Sprite2D = stumps[h]
			var tw := s.create_tween()
			tw.tween_property(s, "modulate:a", 0.0, 3.0)
			tw.tween_callback(s.queue_free)
	super.die(killer)


func _test_poke(p: Player, n: int) -> void:
	if n % 3 == 1 and n > 30:
		take_damage(hp_max * 0.02, "fire", p, {"no_stun": true})
	super._test_poke(p, n)
