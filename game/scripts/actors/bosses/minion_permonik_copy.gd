extends Monster

var life := 14.0
var title := ""
var gone := false


func setup(_mid: String, level_n: int, lv: Node, _champion := false) -> void:
	super.setup("permonicek", level_n, lv, false)
	var pd := DB.monster("permonik")
	display_name = L.t(pd.get("name", "Permoník"))
	title = L.t(pd.get("title", ""))
	kind = "champion"
	no_drops = true
	xp_value = 0
	dmg *= 0.5
	shadow = Sprite2D.new()
	shadow.texture = Actor.shadow_texture()
	shadow.scale = Vector2(0.75, 0.6)
	add_child(shadow)
	move_child(shadow, 0)
	light = Fx.make_light(Color("cfe8ff"), 140.0, 0.9)
	light.position = Vector2(0, -50)
	add_child(light)


func look_like(textures: Dictionary) -> void:
	tex = textures
	sprite.texture = null
	set_pose("idle")


func label_sub() -> String:
	return title


func _ai(delta: float) -> void:
	life -= delta
	if life <= 0.0:
		poof(false)
		return
	super._ai(delta)


func _modify_incoming(_amount: float, _element: String, _source: Node, _opts: Dictionary) -> float:
	poof.call_deferred(true)
	return 0.0


func poof(punish := true) -> void:
	if gone or not is_instance_valid(level):
		return
	gone = true
	Fx.burst(level, global_position + Vector2(0, -40), Color("cfe8ff"), 22, 140.0, 0.6, 0.3, true)
	Sfx.play_at("laugh_permonik", global_position, 0.7)
	level.float_text(top_pos(), Sfx.cry("permonik", {"cs": "Hihi! Vedle!", "en": "Hee hee! Wrong one!"}), Color("cfe8ff"))
	if punish:
		var p := player()
		if p and p.global_position.distance_to(global_position) < 110.0:
			Combat.monster_hit_player(self, p, dmg * 1.5, "cold", {"always_hit": true, "melee": false})
			p.apply_status("chill", 2.0)
	level.monsters.erase(self)
	if level.hover_obj == self:
		level.hover_obj = null
	dead = true
	queue_free()
