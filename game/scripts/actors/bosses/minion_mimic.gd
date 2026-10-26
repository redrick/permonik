extends Monster

var revealed := false
var real_tex := {}
var fuse := -1.0


func setup(mid: String, level_n: int, lv: Node, champion := false) -> void:
	super.setup(mid, level_n, lv, champion)
	no_drops = true
	xp_value = int(xp_value * 0.3)
	real_tex = tex.duplicate()
	var t := DB.tex("items/grose_hodne")
	if t == null:
		t = DB.tex("sprites/fx/coin")
	if t:
		setup_visual_swap({"idle": t})
	display_name = L.t({"cs": "Hromádka tolarů", "en": "A pile of thalers"})
	if light:
		light.energy = 0.25


func setup_visual_swap(textures: Dictionary) -> void:
	tex = textures
	sprite.texture = null
	set_pose("idle")


func _ai(delta: float) -> void:
	if revealed:
		if fuse > 0.0:
			fuse -= delta
			velocity = Vector2.ZERO
			moving = false
			if fuse <= 0.0:
				explode()
			return
		super._ai(delta)
		var p := player()
		if p and p.global_position.distance_to(global_position) < 60.0 and fuse < 0.0:
			_light_fuse()
		return
	velocity = Vector2.ZERO
	moving = false
	var p := player()
	if p and p.global_position.distance_to(global_position) < 95.0:
		reveal()


func reveal() -> void:
	if revealed:
		return
	revealed = true
	aggro = true
	tex = real_tex
	sprite.texture = null
	set_pose("attack", 0.4)
	display_name = L.t({"cs": "Kousavé tolary", "en": "Biting Thalers"})
	if light:
		light.energy = 0.9
	Sfx.play_at("coin_bounce", global_position)
	level.float_text(top_pos(), Sfx.cry("ohnivy_muzik", {"cs": "Cink! Kous!", "en": "Clink! Bite!"}), Color("ffcc55"))


func _light_fuse() -> void:
	fuse = 0.7
	Fx.ground_mark(level, global_position, 110.0, Fx.ELEM.fire, 0.9)


func _on_damaged(amount: float, elem: String, source: Node) -> void:
	super._on_damaged(amount, elem, source)
	reveal()
