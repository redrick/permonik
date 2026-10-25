class_name CinFilms
extends RefCounted

# The screenplay: what moves where in every cinematic shot. Layers come from art/cinema.py,
# narration from data/cinematics.json. Coordinates are canvas px of the shot (y down).

const ORDER := ["intro", "act1_end", "act2_end", "act3_end", "act4_intro", "final", "epilogue", "dlc_tease"]

const WARM := Color("ffb347")
const COLD := Color("8fd0ff")


static func has(id: String) -> bool:
	return id in ORDER and not UiCinema.manifest().is_empty()


func shots(id: String) -> Array:
	match id:
		"intro":
			return [[15.0, _hora], [15.0, _shaft], [17.0, _head], [7.5, _title]]
		"act1_end":
			return [[16.0, _flood], [16.0, _door]]
		"act2_end":
			return [[17.0, _brdy], [15.0, _road]]
		"act3_end":
			return [[18.0, _collapse], [12.0, _dark]]
		"act4_intro":
			return [[13.0, _smorodina], [18.0, _camp]]
		"final":
			return [[12.0, _heart], [13.0, _seals], [14.0, _crack]]
		"epilogue":
			return [[13.0, _bell_again], [14.0, _fifty], [12.0, _sixth_book]]
		"dlc_tease":
			return [[14.0, _eye], [6.0, _name]]
	return []


# ---------------------------------------------------------------- intro: Klekání
func _hora(c: UiCinema) -> void:
	c.canvas = Vector2(2400, 1080)
	c.cam_pos = Vector2(1000, 540)
	c.cam_zoom = 1.06
	c.cam_to(Vector2(1400, 560), 1.0, 16.0)
	c.layer("intro/sky", 0.08)
	c.particles("mist", Rect2(0, 520, 2400, 160), 0.3)
	c.layer("intro/far", 0.35)
	var bell := c.layer("intro/bell", 0.35)
	bell.swing_amp = 16.0
	bell.swing_period = 2.4
	c.sfx("bell_toll", 0.6)
	c.sfx("bell_toll", 3.0, 0.8)
	c.sfx("bell_toll", 5.4, 0.3)
	c.prop(bell, "swing_amp", 0.0, 2.6, 5.0, Tween.TRANS_QUAD, Tween.EASE_OUT)
	var town := c.layer("intro/town", 0.65)
	for p in c.pts("intro/town", "lights"):
		c.glow(town, p, 26, WARM, 0.18, 0.25)
	c.particles("mist", Rect2(0, 760, 2400, 140), 0.8, 10, Color(0.55, 0.45, 0.6, 0.06))
	var near := c.layer("intro/near", 1.0)
	for p in c.pts("intro/near", "lights"):
		c.glow(near, p, 34, WARM, 0.2, 0.25)
	var crow := c.layer("intro/crow", 1.0, 0.6)
	c.frame(crow, "intro/crow_up")
	c.frame(crow, "intro/crow_down")
	c.at(9.5, func():
		crow.cycle_from = 1
		crow.cycle_to = 2
		crow.cycle_fps = 7.0
		crow.step = true
		Sfx.play("swing_light", 0.3, 0.1))
	c.move(crow, Vector2(-1500, -620), 6.0, 9.5, Tween.TRANS_QUAD, Tween.EASE_IN)
	c.say("a", 1.2)


func _shaft(c: UiCinema) -> void:
	c.canvas = Vector2(1920, 2160)
	c.cam_pos = Vector2(960, 560)
	c.cam_to(Vector2(960, 1620), 1.0, 13.0, 1.5)
	c.layer("intro/shaft")
	for i in 5:
		var m := c.layer("intro/miner", 1.0, 0.5)
		var g := c.glow(m, c.pt("intro/miner", "lamp"), 190, Color("ffa94d"), 0.7, 0.25)
		m.modulate.a = 0.0
		m.pos = Vector2(0, -90)
		var d := 0.3 + i * 2.6
		c.fade(m, 1.0, 0.8, d)
		c.walk([m], Vector2(0, -90), Vector2(0, -90 + 1800), 15.0, d, 4.0, 1.4)
		c.prop(m, "modulate", Color(0.35, 0.35, 0.42, 1.0), 9.0, d + 2.0)
		c.glow_alpha(g, 0.12, 9.0, d + 3.0)
	c.particles("dust", Rect2(700, 500, 500, 1600), 1.0, 40, Color(0.6, 0.5, 0.4, 0.35))
	c.say("b", 1.2)


func _head(c: UiCinema) -> void:
	c.cam_pos = Vector2(960, 600)
	c.layer("intro/head_bg")
	c.glow(null, c.pt("intro/head_bg", "post_lamp"), 110, WARM, 0.35, 0.3)
	c.particles("motes", Rect2(0, 200, 1920, 700), 1.0, 24)
	var lamp_pt := c.pt("intro/lamp", "flame")
	var spill := c.glow(null, lamp_pt + Vector2(0, 60), 520, COLD, 0.22, 0.1)
	var shadow := c.layer("intro/hero_shadow")
	shadow.modulate.a = 0.8
	var hero := c.layer("intro/hero_walk", 1.0, 0.8)
	c.frame(hero, "intro/hero_reach")
	c.walk([hero, shadow], Vector2(-760, 20), Vector2.ZERO, 5.0, 0.3, 7.0, 2.0)
	var perm := c.layer("intro/perm", 1.0, 0.9)
	perm.bob = 2.0
	perm.bob_rate = 0.6
	var lamp := c.layer("intro/lamp", 1.0, 0.5)
	lamp.swing_amp = 5.0
	lamp.swing_period = 2.2
	c.glow(lamp, lamp_pt, 150, COLD, 0.55, 0.2)
	c.at(5.6, func():
		hero.frame = 1
		Sfx.play("shrine", 0.5, 0.0))
	c.glow_alpha(spill, 0.5, 2.5, 5.6)
	var end := c.say("c1", 1.0)
	c.cam_to(c.pt("intro/head_bg", "perm_feet") + Vector2(-40, -60), 1.75, 5.5, end - 1.5)
	c.say("c2", end + 0.4)


func _title(c: UiCinema) -> void:
	var t := c.sprite(DB.tex("ui/title"), Vector2(960, 500), 1.0, 1.25)
	t.boil = 0.6
	t.modulate.a = 0.0
	c.fade(t, 1.0, 2.0, 0.6)
	c.particles("motes", Rect2(260, 300, 1400, 500), 1.0, 30)
	c.cam_zoom = 1.0
	c.cam_to(Vector2(960, 530), 1.06, 7.5)
	c.sfx("bell_toll", 0.8, 0.45)


# ---------------------------------------------------------------- act1_end: Dušičky v hrníčcích
func _flood(c: UiCinema) -> void:
	c.cam_pos = Vector2(960, 560)
	c.cam_zoom = 1.04
	c.cam_to(Vector2(900, 520), 1.12, 16.0)
	c.layer("a1/cave")
	var cups := c.pts("a1/cave", "cups")
	for cp in cups:
		c.particles("bubbles", Rect2(cp.x - 30, cp.y - 10, 60, 20), 1.0, 6)
	c.particles("motes", Rect2(0, 300, 1920, 500), 1.0, 26)
	for i in 14:
		var cp: Vector2 = cups[(i * 5) % cups.size()]
		var s := c.layer("a1/soul" if i % 2 == 0 else "a1/soul2", 1.0, 0.6)
		var k := randf_range(0.9, 1.5)
		s.scl = Vector2(k, k)
		s.pos = cp - s.pivot
		s.modulate.a = 0.0
		s.swing_amp = randf_range(4.0, 9.0)
		s.swing_period = randf_range(2.0, 3.2)
		var d := 0.4 + i * 0.85
		c.fade(s, 0.95, 1.0, d)
		c.move(s, Vector2(cp.x + randf_range(-160, 160), randf_range(-60, 140)) - s.pivot, 10.0, d, Tween.TRANS_SINE, Tween.EASE_OUT)
		c.fade(s, 0.0, 2.0, d + 7.5)
		c.sfx("water_splash", d, 0.12)
	c.layer("a1/frame", 1.1)
	c.layer("a1/fg", 1.25)
	var arm := c.layer("a1/arm_lamp", 1.2, 0.4)
	c.glow(arm, c.pt("a1/arm_lamp", "flame"), 220, COLD, 0.55, 0.2)
	var f2 := c.layer("a1/flame2", 1.2, 0.4)
	f2.modulate.a = 0.0
	var g2 := c.glow(f2, f2.pivot, 160, COLD, 0.0, 0.25)
	c.at(9.5, func(): Sfx.play("shrine", 0.6, 0.0))
	c.fade(f2, 1.0, 1.2, 9.5)
	c.glow_alpha(g2, 0.6, 1.5, 9.5)
	c.say("a", 1.0)


func _door(c: UiCinema) -> void:
	c.layer("a1/gallery")
	var door := c.pt("a1/gallery", "door")
	c.glow(null, door + Vector2(0, -90), 300, Color("cfefff"), 0.3, 0.12)
	c.particles("motes", Rect2(500, 200, 900, 700), 1.0, 20)
	c.cam_to(door + Vector2(0, -60), 1.15, 15.0)
	var g := c.layer("a1/girl_away", 1.0, 0.7)
	c.frame(g, "a1/girl_look")
	g.modulate.a = 0.0
	c.fade(g, 0.85, 1.5, 0.3)
	var to := door + Vector2(-30, 0) - g.pivot
	c.walk([g], Vector2.ZERO, to, 7.0, 0.8, 3.0, 1.8)
	c.prop(g, "scl", Vector2(0.36, 0.36), 7.0, 0.8, Tween.TRANS_QUAD, Tween.EASE_OUT)
	for k in 11:
		c.sfx("footstep_water", 1.0 + k * 0.6, 0.18)
	c.at(8.2, func(): g.frame = 1)
	var end := c.say("b", 7.6)
	c.fade(g, 0.0, 2.0, end - 1.5)


# ---------------------------------------------------------------- act2_end: Fabiánova dýmka
func _brdy(c: UiCinema) -> void:
	c.canvas = Vector2(2400, 1080)
	c.cam_pos = Vector2(880, 560)
	c.cam_zoom = 1.06
	c.cam_to(Vector2(1480, 560), 1.0, 17.0)
	c.layer("a2/sky", 0.05)
	c.layer("a2/trees0", 0.25)
	c.layer("a2/trees1", 0.45)
	c.particles("mist", Rect2(0, 560, 2400, 200), 0.5, 14, Color(0.7, 0.75, 0.74, 0.08))
	c.layer("a2/trees2", 0.65)
	c.layer("a2/ground")
	var fab := c.layer("a2/fabian", 1.0, 0.8)
	c.glow(fab, c.pt("a2/fabian", "eyes"), 40, Color("e8c25a"), 0.35, 0.2)
	c.glow(fab, c.pt("a2/fabian", "pipe"), 22, Color("ff8a3a"), 0.6, 0.5)
	var pipe := c.pt("a2/fabian", "pipe")
	var smoke := c.particles("smoke", Rect2(pipe.x - 6, pipe.y - 6, 12, 12), 1.0, 30, Color(0.85, 0.88, 0.9, 0.4))
	smoke.direction = Vector2(1, -0.3)
	smoke.gravity = Vector2(22, 3)
	var hero := c.layer("a2/hero", 1.0, 0.6)
	c.glow(hero, c.pt("a2/hero", "flame"), 120, COLD, 0.55, 0.2)
	var mouth := c.pt("a2/ground", "mouth")
	c.walk([hero], Vector2.ZERO, Vector2(mouth.x - hero.pivot.x - 20, mouth.y - hero.pivot.y - 30), 14.0, 1.5, 4.0, 1.6)
	c.prop(hero, "scl", Vector2(0.5, 0.5), 14.0, 1.5, Tween.TRANS_SINE, Tween.EASE_IN)
	c.fade(hero, 0.0, 1.5, 15.0)
	var fog := c.layer("a2/fog", 1.1)
	c.move(fog, Vector2(220, 0), 17.0, 0.0, Tween.TRANS_LINEAR)
	c.layer("a2/fg", 1.4)
	c.sfx("wolf_howl", 7.0, 0.18)
	c.say("a", 1.0)


func _road(c: UiCinema) -> void:
	c.canvas = Vector2(2400, 1080)
	c.cam_pos = Vector2(560, 600)
	c.cam_zoom = 1.3
	c.cam_to(Vector2(1900, 600), 1.3, 15.5, 0.0, Tween.TRANS_LINEAR)
	c.layer("a2/road")
	var hero := c.layer("a2/hero_side", 1.0, 0.6)
	var perm := c.layer("a2/perm_walk", 1.0, 0.8)
	c.glow(hero, c.pt("a2/hero_side", "flame"), 260, COLD, 0.5, 0.2)
	c.walk([hero, perm], Vector2(-120, 0), Vector2(1500, 0), 15.5, 0.0, 5.0, 2.0)
	perm.bob_rate = 3.0
	c.particles("dust", Rect2(0, 420, 2400, 40), 1.0, 20, Color(0.5, 0.45, 0.4, 0.3))
	var head := c.pt("a2/perm_walk", "head")
	for k in 8:
		c.at(1.2 + k * 1.7, func():
			var n := c.layer("a2/note", 1.0, 0.5)
			n.pos = head + perm.pos + Vector2(10, -20) - n.pivot
			n.scl = Vector2(1.5, 1.5)
			n.swing_amp = 12.0
			c.move(n, n.pos + Vector2(randf_range(40, 90), -150), 2.6, 0.0, Tween.TRANS_SINE, Tween.EASE_OUT)
			c.fade(n, 0.0, 1.0, 1.6))
	for k in 30:
		c.sfx("footstep_rock", 0.3 + k * 0.5, 0.12)
	c.say("b", 1.0)


# ---------------------------------------------------------------- act3_end: Země se zavřela
func _collapse(c: UiCinema) -> void:
	c.layer("a3/bg")
	var beam := c.layer("a3/beam")
	beam.material = UiCinema.add_mat()
	var open := c.pt("a3/bg", "opening")
	var sky := c.glow(null, open, 240, Color("ffcf7a"), 0.5, 0.1)
	var hero := c.layer("a3/hero", 1.0, 0.6)
	c.glow(hero, c.pt("a3/hero", "flame"), 220, COLD, 0.55, 0.2)
	c.particles("dust", Rect2(560, 0, 800, 60), 1.0, 70)
	c.rumble(1.5)
	c.prop(c, "shake_amp", 6.0, 15.0, 0.5, Tween.TRANS_QUAD, Tween.EASE_IN)
	var times := [1.5, 2.8, 4.0, 5.1, 6.5, 7.6, 8.8, 10.0, 11.4, 12.6, 13.6]
	for i in times.size():
		var t: float = times[i]
		c.at(t, func():
			var r := c.layer(["a3/rock_a", "a3/rock_b", "a3/rock_c"][i % 3], 1.0, 0.4)
			var x := randf_range(-300, 300) * (1.0 - t / 16.0)
			r.pos = Vector2(x, -620)
			c.move(r, Vector2(x + randf_range(-30, 30), randf_range(300, 380)), 0.9, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN)
			c.prop(r, "rot", randf_range(-200, 200), 0.9)
			c.sfx("hit_stone", 0.85, 0.5))
	var kos := c.layer("a3/kosmas", 1.0, 0.8)
	kos.pos = Vector2(-40, -760)
	kos.rot = -30.0
	c.prop(kos, "pos:x", -240.0, 1.5, 10.0, Tween.TRANS_LINEAR)
	c.prop(kos, "pos:y", 300.0, 1.5, 10.0, Tween.TRANS_QUAD, Tween.EASE_IN)
	c.prop(kos, "rot", 8.0, 1.5, 10.0)
	c.sfx("hit_flesh", 11.5, 0.4)
	var left := c.layer("a3/left")
	var right := c.layer("a3/right")
	left.pos = Vector2(-700, 0)
	right.pos = Vector2(700, 0)
	c.move(left, Vector2(20, 0), 15.5, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN)
	c.move(right, Vector2(-20, 0), 15.5, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN)
	c.prop(beam, "scl", Vector2(0.05, 1.0), 15.5, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN)
	c.glow_alpha(sky, 0.0, 15.5)
	c.at(15.5, func():
		c.rumble(0.0)
		Sfx.play("explosion", 0.7, 0.0))
	c.shake(15.5, 1.4, 16.0)
	var end := c.say("a", 1.0)
	c.say("k", maxf(end + 0.3, 8.5))


func _dark(c: UiCinema) -> void:
	c.cam_to(Vector2(960, 540), 1.12, 12.0)
	c.layer("a3/dark")
	var lamp := c.layer("a3/lamp3", 1.0, 0.5)
	lamp.swing_amp = 2.0
	lamp.swing_period = 3.0
	c.glow(null, Vector2(960, 520), 700, COLD, 0.25, 0.1)
	for f in c.pts("a3/lamp3", "flames"):
		c.glow(lamp, f, 140, COLD, 0.6, 0.35)
	c.particles("motes", Rect2(300, 200, 1300, 700), 1.0, 20)
	var hand := c.layer("a3/hand", 1.0, 0.8)
	hand.pos = Vector2(760, 0)
	c.move(hand, Vector2.ZERO, 2.4, 2.5, Tween.TRANS_SINE, Tween.EASE_OUT)
	c.at(5.0, func():
		hand.bob = 6.0
		hand.bob_rate = 0.8)
	c.sfx("laugh_permonik", 8.5, 0.2)
	c.say("b", 1.2)


# ---------------------------------------------------------------- act4_intro: Poslední šichta
func _smorodina(c: UiCinema) -> void:
	c.canvas = Vector2(1920, 1620)
	c.cam_pos = Vector2(960, 560)
	c.cam_to(Vector2(960, 1080), 1.0, 12.0, 0.5)
	c.layer("a4/sky", 0.3)
	c.layer("a4/far", 0.75)
	c.glow(null, c.pt("a4/far", "bridge"), 260, Color("ff4a2a"), 0.3, 0.3, 0.75)
	var river := c.layer("a4/river", 0.85)
	c.move(river, Vector2(-900, 0), 14.0, 0.0, Tween.TRANS_LINEAR)
	c.particles("embers", Rect2(0, 1040, 1920, 180), 0.85, 50, Color(1.0, 0.4, 0.25, 0.8))
	c.layer("a4/near")
	c.particles("mist", Rect2(0, 1150, 1920, 200), 1.0, 12, Color(0.55, 0.5, 0.85, 0.08))
	c.layer("a4/roots", 1.15, 0.3)
	c.sfx("ember_crackle", 2.0, 0.25)
	c.say("a", 1.0)


func _camp(c: UiCinema) -> void:
	c.canvas = Vector2(2400, 1080)
	c.cam_pos = Vector2(760, 560)
	c.cam_zoom = 1.05
	c.cam_to(Vector2(1220, 600), 1.1, 8.0)
	c.layer("a4/camp")
	var fire := c.pt("a4/camp", "fire")
	c.glow(null, fire, 170, Color("8aa0e8"), 0.55, 0.45)
	c.glow(null, fire + Vector2(0, -20), 60, Color("e0ecff"), 0.6, 0.6)
	c.particles("embers", Rect2(fire.x - 40, fire.y - 10, 80, 20), 1.0, 26, Color(0.6, 0.75, 1.0, 0.8))
	c.particles("mist", Rect2(0, 560, 2400, 200), 1.0, 12, Color(0.5, 0.45, 0.8, 0.07))
	var perm := c.layer("a4/perm", 1.0, 0.8)
	c.frame(perm, "a4/perm_grin")
	c.walk([perm], Vector2(1000, -30), Vector2.ZERO, 5.0, 6.0, 4.0, 2.6)
	c.layer("a4/log")
	c.prop(perm, "pos:y", 46.0, 0.5, 11.4, Tween.TRANS_QUAD, Tween.EASE_OUT)
	c.at(14.0, func(): perm.frame = 1)
	c.cam_to(c.pt("a4/perm", "pivot") + Vector2(-140, -60), 1.45, 5.0, 11.0)
	var end := c.say("b", 1.0)
	c.say("c", end + 0.3)


# ---------------------------------------------------------------- final: Srdce hory
func _heart(c: UiCinema) -> void:
	c.cam_zoom = 1.04
	c.layer("f/bg")
	c.particles("motes", Rect2(200, 200, 1500, 700), 1.0, 24)
	var perm := c.layer("f/perm", 1.0, 0.9)
	perm.bob = 2.0
	perm.bob_rate = 0.5
	c.layer("f/hero", 1.0, 0.6)
	var lamp := c.layer("f/lamp", 1.0, 0.5)
	lamp.swing_amp = 4.0
	lamp.swing_period = 2.0
	c.glow(lamp, c.pt("f/lamp", "flame"), 260, COLD, 0.6, 0.2)
	var hand := c.pt("f/perm", "hand")
	var to := hand + Vector2(0, 10) - lamp.pivot
	c.prop(lamp, "pos:x", to.x, 3.2, 3.0, Tween.TRANS_SINE, Tween.EASE_IN_OUT)
	c.prop(lamp, "pos:y", to.y, 3.2, 3.0, Tween.TRANS_BACK, Tween.EASE_IN_OUT)
	c.sfx("portal", 3.0, 0.5)
	c.sfx("laugh_permonik", 6.6, 0.3)
	c.dark_in(Vector2(hand.x / 1920.0, hand.y / 1080.0), 1.4, 0.3, 4.5, 6.8)
	c.say("a", 1.0)


func _giant_scene(c: UiCinema, risen: bool) -> Dictionary:
	var bg := c.layer("f/bg")
	bg.modulate = Color(0.55, 0.55, 0.62)
	var giant := c.layer("f/giant", 1.0, 0.6)
	var eyes: Array = []
	for e in c.pts("f/giant", "eyes"):
		eyes.append(c.glow(giant, e, 70, Color("9fe0ff"), 0.7 if risen else 0.0, 0.3))
	if not risen:
		giant.pos = Vector2(0, 760)
	var center := c.pt("f/lamp_big", "center")
	var rays := c.layer("f/rays")
	rays.material = UiCinema.add_mat()
	rays.pos = center - rays.pivot
	rays.modulate.a = 0.8
	c.prop(rays, "rot", 25.0, 16.0, 0.0, Tween.TRANS_LINEAR)
	var halo := c.glow(null, center, 520, COLD, 0.4, 0.15)
	var lamp := c.layer("f/lamp_big", 1.0, 0.4)
	lamp.swing_amp = 2.0
	lamp.swing_period = 3.4
	for f in c.pts("f/lamp_big", "flames"):
		c.glow(lamp, f, 110, Color("dff3ff"), 0.6, 0.35)
	var seals: Array = []
	var cols := [Color("4aa8ff"), Color("c4c4cc"), Color("ff6a2a"), Color("b58aff")]
	for i in 4:
		var s := c.layer("f/seal_" + ["water", "stone", "fire", "death"][i], 1.0, 0.5)
		c.glow(s, s.pivot, 90, cols[i], 0.5, 0.3)
		seals.append(s)
	var orbit := func(a: float):
		for i in 4:
			var s: CinLayer = seals[i]
			if is_instance_valid(s) and s.get_meta("free", false) == false:
				var ang := a + i * TAU / 4.0
				s.pos = center + Vector2(cos(ang) * 250.0, sin(ang) * 200.0) - s.pivot
	orbit.call(0.0)
	c.tw().tween_method(orbit, 0.0, TAU * 1.3, 16.0)
	return {"giant": giant, "eyes": eyes, "lamp": lamp, "seals": seals, "center": center, "rays": rays, "halo": halo}


func _seals(c: UiCinema) -> void:
	var g := _giant_scene(c, false)
	c.move(g.giant, Vector2.ZERO, 9.0, 0.5, Tween.TRANS_SINE, Tween.EASE_OUT)
	for e in g.eyes:
		c.glow_alpha(e, 0.8, 2.0, 8.0)
	c.rumble(3.0)
	c.prop(c, "shake_amp", 0.0, 9.0, 0.5)
	c.sfx("boss_roar", 1.0, 0.4)
	c.sfx("boss_roar", 8.5, 0.3)
	c.cam_to(Vector2(1000, 520), 1.08, 13.0)
	c.say("b", 1.5)


func _crack(c: UiCinema) -> void:
	var g := _giant_scene(c, true)
	var center: Vector2 = g.center
	c.flash(1.5, Color(0.9, 0.96, 1.0, 1.0), 1.2)
	c.shake(1.5, 1.6, 18.0)
	c.sfx("explosion", 1.5, 0.8)
	c.sfx("petrify", 1.6, 0.5)
	c.glow_alpha(g.halo, 0.0, 2.5, 1.6)
	c.at(1.5, func():
		g.lamp.visible = false
		g.rays.visible = false
		for i in 12:
			var sh := c.layer("f/shard" if i % 3 else "f/shard2", 1.0, 0.4)
			var a := randf() * TAU
			sh.pos = center - sh.pivot
			sh.scl = Vector2.ONE * randf_range(1.0, 2.2)
			c.move(sh, sh.pos + Vector2(cos(a), sin(a)) * randf_range(500, 1100), 1.8, 0.0, Tween.TRANS_QUAD, Tween.EASE_OUT)
			c.prop(sh, "rot", randf_range(-540, 540), 1.8)
			c.fade(sh, 0.0, 0.8, 1.2)
		for i in 4:
			var s: CinLayer = g.seals[i]
			s.set_meta("free", true)
			var a := PI * 0.25 + i * TAU / 4.0
			c.move(s, s.pos + Vector2(cos(a), sin(a)) * 1300.0, 2.6, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN))
	c.at(3.0, func():
		c.rumble(4.0)
		for e in g.eyes:
			c.glow_alpha(e, 0.0, 3.0))
	c.move(g.giant, Vector2(60, 980), 7.0, 3.0, Tween.TRANS_QUAD, Tween.EASE_IN)
	c.prop(g.giant, "rot", 4.0, 7.0, 3.0)
	c.particles("dust", Rect2(900, 0, 1000, 80), 1.0, 90)
	for k in 9:
		c.at(3.2 + k * 0.7, func():
			var r := c.layer(["a3/rock_a", "a3/rock_b", "a3/rock_c"][k % 3], 1.0, 0.4)
			var x := randf_range(-100, 800)
			r.pos = Vector2(x, -600)
			c.move(r, Vector2(x, 700), 1.2, 0.0, Tween.TRANS_QUAD, Tween.EASE_IN)
			c.prop(r, "rot", randf_range(-300, 300), 1.2)
			c.sfx("hit_stone", 1.0, 0.3))
	c.sfx("laugh_permonik", 3.6, 0.7)
	c.sfx("laugh_permonik", 7.4, 0.45)
	c.at(10.0, func(): c.rumble(0.0))
	c.say("c", 2.6)


# ---------------------------------------------------------------- epilogue: Zvon zase zvoní
func _bell_again(c: UiCinema) -> void:
	c.canvas = Vector2(2400, 1080)
	c.cam_pos = Vector2(1000, 560)
	c.cam_zoom = 1.06
	c.cam_to(Vector2(1320, 560), 1.0, 14.0)
	c.layer("e/sky", 0.08)
	c.layer("e/far", 0.35)
	var bell := c.layer("e/bell", 0.35)
	bell.swing_amp = 20.0
	bell.swing_period = 2.4
	for k in 6:
		var t := 0.6 + k * 2.4
		c.sfx("bell_toll", t, 0.9)
		c.at(t, func():
			var r := c.layer("e/ring", 0.35)
			r.scl = Vector2(0.6, 0.6)
			c.prop(r, "scl", Vector2(1.5, 1.5), 1.4, 0.0, Tween.TRANS_SINE, Tween.EASE_OUT)
			c.fade(r, 0.0, 1.4))
	for pair in [["e/town", 0.65, 26], ["e/near", 1.0, 34]]:
		var l := c.layer(pair[0], pair[1])
		for p in c.pts(pair[0], "lights"):
			var g := c.glow(l, p, pair[2], WARM, 0.55, 0.2)
			c.glow_alpha(g, 0.0, 0.25, randf_range(3.5, 12.0))
	var kid := c.layer("e/kid_a", 1.0, 0.5)
	c.frame(kid, "e/kid_b")
	var girl := c.layer("e/girl_a", 1.0, 0.5)
	c.frame(girl, "e/girl_b")
	for k in [kid, girl]:
		k.cycle_from = 0
		k.cycle_to = 1
		k.cycle_fps = 6.0
		c.walk([k], Vector2(-420, 0), Vector2(760, 0), 6.5, 2.5, 3.0, 3.0)
		c.fade(k, 0.0, 0.5, 8.8)
	c.say("a", 1.0)


func _fifty(c: UiCinema) -> void:
	c.cam_to(Vector2(960, 560), 1.08, 14.0)
	c.layer("e/nav")
	c.particles("motes", Rect2(0, 300, 1920, 600), 1.0, 20)
	var lamps := c.pts("e/nav", "lamps")
	var order := range(lamps.size())
	order.shuffle()
	for i in order.size():
		var p: Vector2 = lamps[order[i]]
		var g := c.glow(null, p, 34 + p.y / 30.0, WARM, 0.0, 0.25)
		c.glow_alpha(g, 0.6, 0.4, 2.0 + i * 0.09)
		c.glow_alpha(g, 0.0, 1.4, 9.5 + i * 0.07)
		if i % 8 == 0:
			c.sfx("ember_crackle", 2.0 + i * 0.09, 0.12)
	c.say("b", 1.0)


func _sixth_book(c: UiCinema) -> void:
	c.cam_to(c.pt("e/study", "nib") + Vector2(-120, -60), 1.15, 12.0)
	c.layer("e/study")
	c.glow(null, c.pt("e/study", "candle"), 260, WARM, 0.45, 0.35)
	c.glow(null, c.pt("e/study", "candle"), 50, Color("fff3c4"), 0.6, 0.5)
	var q := c.layer("e/quill", 1.0, 0.4)
	q.step = true
	var t := c.tw().set_loops(8)
	t.tween_property(q, "pos", Vector2(18, -3), 0.35)
	t.tween_property(q, "pos", Vector2(36, 1), 0.35)
	t.tween_property(q, "pos", Vector2(54, -2), 0.35)
	t.tween_property(q, "pos", Vector2(0, 14), 0.5)
	c.particles("motes", Rect2(200, 300, 1500, 500), 1.0, 14, Color(1.0, 0.85, 0.6, 0.4))
	c.say("c", 1.0)


# ---------------------------------------------------------------- dlc_tease: Pod Navem
func _eye(c: UiCinema) -> void:
	var eye := c.pt("d/face", "eye")
	c.cam_to(eye, 1.12, 14.0)
	c.layer("d/face")
	var glow := c.glow(null, eye + Vector2(0, 30), 420, Color("ff2a1a"), 0.08, 0.4)
	c.layer("d/iris")
	var lid := c.layer("d/lid", 1.0, 0.4)
	c.rumble(1.2)
	c.prop(lid, "scl", Vector2(1.0, 0.94), 0.25, 3.0)
	c.prop(lid, "scl", Vector2(1.0, 1.0), 0.4, 3.3)
	c.prop(lid, "scl", Vector2(1.0, 0.68), 2.6, 7.0, Tween.TRANS_SINE, Tween.EASE_OUT)
	c.glow_alpha(glow, 0.35, 2.6, 7.0)
	c.shake(7.0, 2.5, 7.0)
	c.sfx("boss_roar", 7.0, 0.5)
	c.say("a", 1.0)


func _name(c: UiCinema) -> void:
	c.title_card("b", 0.5, 5.0, 96)
	c.sfx("bell_toll", 0.6, 0.35)
