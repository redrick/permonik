extends BossBase

const FIRE := Color("ff8a2a")
const STEAM := Color("e8f0f4")

var oven: PropNode
var heat := 0.0
var pulse_t := 4.0
var hut: Monster
var buckets: Array = []
var refill := {}


func _init_boss() -> void:
	ai = "caster"
	var ovens := props_of("pec")
	if ovens.is_empty():
		ovens = place_props("pec", 1, 4.0, true)
	oven = ovens[0] if ovens.size() > 0 else null
	buckets = props_of("kbelik")
	if buckets.size() < 3:
		buckets = place_props("kbelik", 4, 7.0, false)
		for b in buckets:
			b.interact = "quest"
	var q := open_spot_near(global_position, 140.0, 260.0)
	hut = level.spawn_monster("chaloupka", q, mlvl)
	if hut:
		hut.minion_of = self
		hut.no_drops = true


func oven_pos() -> Vector2:
	return oven.global_position if oven and is_instance_valid(oven) else home


func pulse_radius() -> float:
	return lerpf(130.0, 560.0, heat / 100.0)


func _always_tick(delta: float) -> void:
	for k in refill.keys():
		refill[k] -= delta
		if refill[k] <= 0.0:
			refill.erase(k)
			var b: PropNode = instance_from_id(k) as PropNode
			if b and is_instance_valid(b):
				b.used = false
				b.sprite.modulate = Color.WHITE
				level.float_text(b.global_position + Vector2(0, -70), L.t({"cs": "Kbelík je zase plný", "en": "The bucket is full again"}), STEAM)
	if not aggro:
		return
	if phase == 1 and hp < hp_max * 0.5:
		phase = 2
		if hut and is_instance_valid(hut) and not hut.dead:
			hut.speed *= 1.35
			hut.attack_cd *= 0.75
			hut.wake()
	heat = minf(100.0, heat + delta * (4.0 if phase == 1 else 5.5))
	if oven and oven.light:
		oven.light.texture_scale = pulse_radius() * 2.0 / 256.0
		oven.light.energy = 0.8 + heat / 100.0
	pulse_t -= delta
	if pulse_t <= 0.0:
		pulse_t = lerpf(4.0, 1.6, heat / 100.0)
		_oven_pulse()


func _oven_pulse() -> void:
	var c := oven_pos()
	var r := pulse_radius()
	mark(c, r, 0.9, FIRE)
	later(0.9, func():
		Fx.ring(level, c, r, FIRE, 0.5)
		Fx.burst(level, c + Vector2(0, -40), FIRE, int(10 + heat * 0.3), r, 0.6, 0.35, true)
		Sfx.play_at("fire_hit", c, 0.6 + heat / 250.0)
		var p := pl()
		if p and p.global_position.distance_to(c) <= r:
			if hit(p, 0.35 + heat / 100.0 * 0.9, "fire"):
				p.apply_status("burn", 2.0, {"dps": dmg.x * 0.15 * (1.0 + heat / 50.0), "src": self}))
	if heat >= 100.0 and randf() < 0.5:
		shout("Pec je rozpálená!", "The oven is roaring!", FIRE)


func _special(p: Actor, d: float) -> float:
	var r := randf()
	if d < 150.0:
		_shovel(p)
		return randf_range(3.0, 4.0)
	if r < 0.3 and oven:
		_stoke()
		return randf_range(5.0, 7.0)
	set_pose("attack", 0.6)
	face_to(p.global_position)
	shoot(p.global_position, "firebolt", 340.0, 0.9, "fire", FIRE, 3 if phase == 2 else 1, 0.2)
	Sfx.play_at("fire_cast", global_position, 0.7)
	return randf_range(2.5, 3.5)


func _shovel(p: Actor) -> void:
	busy = 0.7
	set_pose("attack", 0.7)
	face_to(p.global_position)
	shout("Na lopatu!", "Onto the shovel!", FIRE)
	cone(p.global_position - global_position, 130.0, 100.0, 0.6, 1.1, "physical", Color("d8b080"), func(a):
		a.knock = (oven_pos() - a.global_position).normalized() * 560.0)


func _stoke() -> void:
	var q := open_spot_near(oven_pos() + Vector2(0, 70), 10.0, 60.0)
	blink_to(q, Color("ffb070"))
	busy = 1.2
	set_pose("attack", 1.2)
	shout("Přiložím!", "More wood!", FIRE)
	Sfx.play_at("fire_cast", oven_pos())
	later(1.0, func():
		heat = minf(100.0, heat + 25.0)
		Fx.burst(level, oven_pos() + Vector2(0, -50), FIRE, 30, 200.0, 0.7, 0.35, true))


func on_quest_prop(prop: PropNode, p: Player) -> void:
	Game.on_event("use", prop.id)
	if prop.id != "kbelik":
		return
	if prop.used:
		level.float_text(prop.global_position + Vector2(0, -70), L.t({"cs": "Kbelík je prázdný", "en": "The bucket is empty"}), STEAM)
		return
	prop.used = true
	prop.set_hover(false)
	prop.sprite.modulate = Color(0.5, 0.5, 0.55)
	refill[prop.get_instance_id()] = 30.0
	p.face_to(oven_pos())
	p.set_pose("attack", 0.4)
	Fx.bolt(level, p.global_position + Vector2(0, -60), oven_pos() + Vector2(0, -50), Color("9fd8ff"), 6.0, 0.5)
	douse()


func douse() -> void:
	heat = 0.0
	pulse_t = 4.0
	var c := oven_pos()
	Sfx.play_at("smoke", c)
	Sfx.play_at("water_splash", c)
	Fx.burst(level, c + Vector2(0, -60), STEAM, 40, 180.0, 1.4, 0.45, true)
	level.float_text(c + Vector2(0, -120), L.t({"cs": "Pec syčí a hasne", "en": "The oven hisses and dies down"}), STEAM)
	if aggro:
		say_t("Moje pec! Ty mrtvou vodou na můj oheň?!", "My oven! Dead water on my fire?!", 3.0)


func _test_poke(p: Player, n: int) -> void:
	if n % 12 == 0:
		for b in buckets:
			if is_instance_valid(b) and not b.used:
				on_quest_prop(b, p)
				break
	super._test_poke(p, n)
