class_name Npc
extends Actor

var npc_id := ""
var def := {}
var home := Vector2.ZERO
var wander_t := 2.0
var talk_t := 0.0
var stock: Array = []


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
	var tt := DB.tex("sprites/npcs/%s_talk" % id)
	if tt:
		textures["attack"] = tt
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


func role() -> String:
	return str(def.get("role", "other"))


func talk_pose() -> void:
	set_pose("attack", 1.6)
	if npc_id == "permonik" and Game.act >= 3 and DB.tex("sprites/npcs/permonik_grin"):
		tex["attack"] = DB.tex("sprites/npcs/permonik_grin")
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
