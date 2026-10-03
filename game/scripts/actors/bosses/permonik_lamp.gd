extends Monster

const COLD := Color("cfe8ff")

var pulse_t := 4.0
var base_y := 70.0


func setup(_mid: String, level_n: int, lv: Node, _champion := false) -> void:
	id = "permonikuv_kahan"
	level = lv
	data = {}
	team = 1
	kind = "boss"
	ai = "none"
	mlvl = level_n
	armor = 0
	speed = 0.0
	radius = 24.0
	no_drops = true
	xp_value = 0
	aggro = true
	display_name = L.t({"cs": "Kahan čtyř pečetí", "en": "The Lamp of Four Seals"})
	collision_layer = 4
	collision_mask = 0
	var t := DB.tex("items/permonikuv_kahan")
	if t == null:
		t = DB.placeholder("lamp", Vector2i(56, 112), COLD)
	setup_visual({"idle": t}, false)
	sprite.scale = Vector2(1.5, 1.5)
	float_h = base_y
	light = Fx.make_light(COLD, 300.0, 1.5, true)
	light.position = Vector2(0, -base_y - 40.0)
	add_child(light)
	mat_set("outline_color", Color(0.8, 0.9, 1.0, 1))


func label_sub() -> String:
	return L.t({"cs": "srdce Permoníka", "en": "Permoník's heart"})


func _ai(delta: float) -> void:
	velocity = Vector2.ZERO
	moving = false
	float_h = base_y + sin(anim_t * 1.7) * 8.0
	light.energy = 1.3 + sin(anim_t * 5.0) * 0.2
	pulse_t -= delta
	if pulse_t <= 0.0:
		pulse_t = 5.0
		_pulse()


func _pulse() -> void:
	var r := 170.0
	var c := global_position
	Fx.ground_mark(level, c, r, COLD, 1.2)
	var tw := create_tween()
	tw.tween_interval(1.0)
	tw.tween_callback(func():
		Fx.ring(level, c, r, COLD, 0.5)
		Sfx.play_at("frost_hit", c, 0.6)
		var p := player()
		if p and p.global_position.distance_to(c) <= r + p.radius:
			Combat.monster_hit_player(self, p, dmg, "cold", {"always_hit": true, "melee": false, "knock": 400.0})
			p.knock = (p.global_position - c).normalized() * 400.0)


func _on_damaged(amount: float, elem: String, source: Node) -> void:
	super._on_damaged(amount, elem, source)
	light.energy = 2.2
	Fx.burst(level, global_position + Vector2(0, -base_y - 30.0), COLD, 6, 90.0, 0.4, 0.2)
