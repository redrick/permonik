class_name Npc
extends Actor

var npc_id := ""
var def := {}
var home := Vector2.ZERO
var wander_t := 2.0
var talk_t := 0.0
var stock: Array = []
var gamble_stock: Array = []
var mark: Sprite2D
var mark_kind := ""


func setup(id: String, lv: Node) -> void:
	npc_id = id
	level = lv
	def = DB.npcs.get(id, {})
	team = 2
	radius = 14.0
	collision_layer = 8
	collision_mask = 1
	display_name = L.t(def.get("name", id))
	var textures := {}
	var t := DB.tex("sprites/npcs/" + id)
	if t:
		textures["idle"] = t
	for v in ["", "_f", "_b"]:
		for p in ["idle", "talk", "walk1", "walk2", "walk3", "walk4"]:
			if p == "idle" and v == "":
				continue
			var tv := DB.tex("sprites/npcs/%s_%s%s" % [id, p, v])
			if tv:
				textures[("attack" if p == "talk" else p) + v] = tv
	if textures.is_empty():
		textures["idle"] = DB.placeholder("npc_" + id, Vector2i(100, 180), Color("b8a888"))
	setup_visual(textures, not id.begins_with("permonik"), 44.0)
	if id in ["predak_matej", "anicka"]:
		modulate = Color(0.8, 0.9, 1.1, 0.8)
	if id == "permonik":
		var l := Fx.make_light(Color("d9ecff"), 150.0, 0.9)
		l.position = Vector2(0, -40)
		add_child(l)
	home = global_position
	_make_mark()


# "!" / "?" over the head when talking now starts or moves on a quest.
func _make_mark() -> void:
	mark = Sprite2D.new()
	mark.visible = false
	var t: Texture2D = tex.get("idle")
	var top := -150.0
	if t:
		var img := t.get_image()
		if img:
			if img.is_compressed():
				img.decompress()
			top = -t.get_height() + 8.0 + img.get_used_rect().position.y
	mark.position = Vector2(0, top - 34.0)
	mark.z_index = 30
	add_child(mark)
	var tw := mark.create_tween().set_loops()
	tw.tween_property(mark, "offset:y", -6.0, 0.6).set_trans(Tween.TRANS_SINE)
	tw.tween_property(mark, "offset:y", 0.0, 0.6).set_trans(Tween.TRANS_SINE)
	var timer := Timer.new()
	timer.wait_time = 0.4
	timer.autostart = true
	timer.timeout.connect(_update_mark)
	add_child(timer)
	_update_mark()


func _update_mark() -> void:
	var k := Game.npc_marker(npc_id)
	if k == mark_kind:
		return
	mark_kind = k
	mark.visible = k != ""
	if k != "":
		mark.texture = DB.tex("ui/quest_" + k)


func role() -> String:
	return str(def.get("role", "other"))


func talk_pose() -> void:
	set_pose("attack", 1.6)
	if npc_id == "permonik" and Game.act >= 3 and DB.tex("sprites/npcs/permonik_grin"):
		for v in ["", "_f", "_b"]:
			var g := DB.tex("sprites/npcs/permonik_grin" + v)
			if g:
				tex["attack" + v] = g
		set_pose("attack", 1.6)


func _ai(delta: float) -> void:
	if Game.player and Game.player.global_position.distance_to(global_position) < 200:
		face_to(Game.player.global_position)
		velocity = Vector2.ZERO
		moving = false
		return
	wander_t -= delta
	if wander_t <= 0.0:
		wander_t = randf_range(4, 9)
		if role() != "guide" and randf() < 0.5:
			path = [home + Vector2(randf_range(-70, 70), randf_range(-40, 40))]
	if path.size() > 0 and level.is_solid(path[0]):
		path.clear()
	follow_path(delta, 45.0)


func take_damage(_amount: float, _element := "physical", _source: Node = null, _opts := {}) -> float:
	return 0.0
