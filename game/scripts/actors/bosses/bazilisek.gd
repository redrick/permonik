extends BossBase

const GAZE := Color("d8f06a")
const STONE := Color("bcb6a8")

var gaze_dir := Vector2.RIGHT
var beam: Line2D
var self_stone := 0.0
var stoned_t := 0.0
var mirrors: Array = []
var mirror_cd := {}
var crow_t := 12.0


func _init_boss() -> void:
	set_meta("hit_sfx", "hit_stone")
	mirrors = place_props("zrcadlo", 4, 6.0, true)
	beam = Line2D.new()
	beam.width = 6.0
	beam.default_color = Color(GAZE.r, GAZE.g, GAZE.b, 0.0)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	beam.material = m
	beam.add_point(Vector2.ZERO)
	beam.add_point(Vector2.ZERO)
	level.fx_root.add_child(beam)


func _exit_tree() -> void:
	if is_instance_valid(beam):
		beam.queue_free()


func eye_pos() -> Vector2:
	return global_position + Vector2(facing * radius * 0.6, -sprite_h * 0.75)


func _mirror_between(a: Vector2, b: Vector2) -> PropNode:
	for k in mirrors:
		if not is_instance_valid(k) or k.used:
			continue
		var c: Vector2 = k.global_position + Vector2(0, -20)
		var cp := Geometry2D.get_closest_point_to_segment(c, a, b)
		if cp.distance_to(c) < 42.0 and cp.distance_to(a) > 30.0 and cp.distance_to(b) > 30.0:
			return k
	return null


func _always_tick(delta: float) -> void:
	for k in mirror_cd.keys():
		mirror_cd[k] -= delta
	if stoned_t > 0.0:
		stoned_t -= delta
		petrify = 1.2
		beam.default_color.a = 0.0
		if stoned_t <= 0.0:
			petrify = 0.0
			self_stone = 0.0
			Fx.burst(level, global_position + Vector2(0, -60), STONE, 24, 160.0, 0.6, 0.3)
		return
	self_stone = maxf(0.0, self_stone - delta * 0.3)
	petrify = self_stone * 0.8
	var p := pl()
	if p == null or not aggro:
		beam.default_color.a = 0.0
		return
	var to := (p.global_position - global_position).normalized()
	var turn := (1.1 if phase == 1 else 1.7) * delta
	gaze_dir = gaze_dir.rotated(clampf(gaze_dir.angle_to(to), -turn, turn))
	face_to(global_position + gaze_dir)
	var dist := p.global_position.distance_to(global_position)
	var in_cone := absf(gaze_dir.angle_to(to)) < deg_to_rad(35.0)
	var los: bool = level.line_of_sight(global_position, p.global_position)
	var a := eye_pos()
	beam.set_point_position(0, a)
	if in_cone and los and dist < 650.0:
		var b := p.global_position + Vector2(0, -50)
		var mirror := _mirror_between(global_position, p.global_position)
		if mirror:
			b = mirror.global_position + Vector2(0, -40)
			_reflect(delta * 0.9)
			beam.default_color = Color(1, 1, 1, 0.7)
		else:
			beam.default_color = Color(GAZE.r, GAZE.g, GAZE.b, 0.25 + p.petrify * 0.5)
			if not p.has_meta("baz_locked"):
				p.petrify = minf(1.2, p.petrify + delta * (0.45 if phase == 1 else 0.6))
				if p.petrify >= 1.0:
					p.set_meta("baz_locked", true)
					p.petrify = 1.2
					Sfx.play_at("petrify", p.global_position)
					level.float_text(p.top_pos(), L.t({"cs": "Zkameněl jsi!", "en": "Turned to stone!"}), STONE, true)
			elif p.petrify < 0.6:
				p.remove_meta("baz_locked")
		beam.set_point_position(1, b)
	else:
		beam.default_color.a = 0.06
		beam.set_point_position(1, a + gaze_dir * 260.0)
		if p.petrify < 0.6 and p.has_meta("baz_locked"):
			p.remove_meta("baz_locked")
	if phase == 2:
		crow_t -= delta
		if crow_t <= 0.0 and can_act():
			crow_t = 14.0
			_crow()


func _reflect(amount: float) -> void:
	self_stone += amount
	mat_set("stone", clampf(self_stone, 0.0, 1.0))
	if self_stone >= 1.0:
		_petrified(0.07)


func _petrified(dmg_frac: float) -> void:
	if stoned_t > 0.0:
		return
	stoned_t = 3.2
	windup = 0.0
	busy = 0.0
	Sfx.play_at("petrify", global_position)
	level.shake(6.0)
	shout("Kokrhá… a kamení!", "It crows… and turns to stone!", STONE)
	var p := pl()
	take_damage(hp_max * dmg_frac, "physical", p, {"no_stun": true})


func _crow() -> void:
	busy = 1.3
	set_pose("attack", 1.3)
	shout("KYKYRYKÝÝ!", "COCK-A-DOODLE!", GAZE)
	mark(global_position, 520.0, 1.2, GAZE)
	later(1.2, func():
		Fx.ring(level, global_position, 520.0, GAZE, 0.6)
		var p := pl()
		if p and p.global_position.distance_to(global_position) < 520.0 and level.line_of_sight(global_position, p.global_position):
			if _mirror_between(global_position, p.global_position):
				_petrified(0.05)
			else:
				p.petrify = minf(1.2, p.petrify + 0.6)
				Sfx.play_at("petrify", p.global_position, 0.7))


func _special(p: Actor, d: float) -> float:
	if d > 200.0 and randf() < 0.6:
		face_to(p.global_position)
		set_pose("attack", 0.6)
		shoot(p.global_position, "rock", 280.0, 0.6, "physical", STONE, 1, 0.0, func(a): a.petrify = minf(1.2, a.petrify + 0.3))
		return randf_range(3.0, 4.0)
	busy = 1.0
	set_pose("attack", 1.0)
	slam(global_position, 190.0, 0.95, 1.2, "physical", STONE, {"knock": 300.0})
	return randf_range(4.0, 5.5)


func _fight(p: Actor, d: float, delta: float) -> void:
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
	super._fight(p, d, delta)


func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	amount = super._modify_incoming(amount, elem, source, opts)
	return amount * (1.6 if stoned_t > 0.0 else 1.0)


func on_quest_prop(prop: PropNode, p: Player) -> void:
	if prop.id != "zrcadlo":
		Game.on_event("use", prop.id)
		return
	var key := prop.get_instance_id()
	if mirror_cd.get(key, 0.0) > 0.0:
		level.float_text(prop.global_position + Vector2(0, -120), L.t({"cs": "Zrcadlo se ještě chvěje…", "en": "The mirror still trembles…"}), STONE)
		return
	Game.on_event("use", "zrcadlo")
	mirror_cd[key] = 12.0
	var src := prop.global_position + Vector2(0, -60)
	Sfx.play_at("frost_cast", prop.global_position)
	if global_position.distance_to(prop.global_position) < 800.0 and level.line_of_sight(prop.global_position, global_position):
		Fx.bolt(level, src, global_position + Vector2(0, -sprite_h * 0.6), Color(1, 1, 1), 6.0, 0.5)
		_petrified(0.08)
		var uses := int(prop.data.get("uses", 0)) + 1
		prop.data["uses"] = uses
		if uses >= 2:
			prop.used = true
			prop.set_hover(false)
			prop.sprite.modulate = Color(0.55, 0.55, 0.6)
			level.float_text(src + Vector2(0, -60), L.t({"cs": "Zrcadlo prasklo", "en": "The mirror cracked"}), STONE)
	else:
		Fx.flash(level, src, Color(1, 1, 1), 120.0, 0.3)
		level.float_text(src + Vector2(0, -60), L.t({"cs": "Odraz ho nezasáhl", "en": "The reflection missed him"}), STONE)


func _test_poke(p: Player, n: int) -> void:
	if n % 7 == 0 and mirrors.size() > 0:
		on_quest_prop(mirrors[n % mirrors.size()], p)
	super._test_poke(p, n)
