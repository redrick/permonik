extends Node

var classes := {}
var skills := {}
var monsters := {}
var items := {}
var affixes := {"prefixes": [], "suffixes": []}
var uniques := {}
var shrines := {}
var champions := {"names": [], "mods": {}}
var npcs := {}
var acts := []
var quests := {}
var dialog := {}
var lore := {}
var slides := {}
var props := {}

var _tex := {}
var _missing := {}


func _ready() -> void:
	reload()


func reload() -> void:
	classes = _j("classes", {})
	skills = _j("skills", {})
	monsters = _j("monsters", {})
	items = _j("items_base", {})
	affixes = _j("affixes", {"prefixes": [], "suffixes": []})
	uniques = _j("uniques", {})
	shrines = _j("shrines", {})
	champions = _j("champions", {"names": [], "mods": {}})
	npcs = _j("npcs", {})
	var a = _j("acts", [])
	acts = a if a is Array else []
	quests = _j("quests", {})
	dialog = _j("dialog", {})
	lore = _j("lore", {})
	slides = _j("slides", {})
	props = _j("props", {})


func _j(name: String, default):
	var path := "res://data/%s.json" % name
	if not FileAccess.file_exists(path):
		push_warning("missing data " + path)
		return default
	var d = JSON.parse_string(FileAccess.get_file_as_string(path))
	if d == null:
		push_error("bad json " + path)
		return default
	return d


func act(n: int) -> Dictionary:
	for a in acts:
		if int(a.get("id", 0)) == n:
			return a
	return {}


func act_count() -> int:
	return acts.size()


func floor_def(act_n: int, f: int) -> Dictionary:
	for fl in act(act_n).get("floors", []):
		if int(fl.get("n", 0)) == f:
			return fl
	return {}


func floor_count(act_n: int) -> int:
	return act(act_n).get("floors", []).size()


func monster(id: String) -> Dictionary:
	return monsters.get(id, {})


func item(id: String) -> Dictionary:
	return items.get(id, {})


func skill(id: String) -> Dictionary:
	return skills.get(id, {})


func prop(id: String) -> Dictionary:
	return props.get(id, {})


func tex(path: String) -> Texture2D:
	if _tex.has(path):
		return _tex[path]
	var full := "res://assets/" + path + ".png"
	var t: Texture2D = null
	if ResourceLoader.exists(full):
		t = load(full)
	elif FileAccess.file_exists(full):
		var img := Image.load_from_file(full)
		if img:
			t = ImageTexture.create_from_image(img)
	_tex[path] = t
	return t


func has_tex(path: String) -> bool:
	return tex(path) != null


func tex_or(path: String, fallback: String) -> Texture2D:
	var t := tex(path)
	return t if t else tex(fallback)


func placeholder(key: String, size: Vector2i, color: Color) -> Texture2D:
	var k := "ph:%s:%d:%d" % [key, size.x, size.y]
	if _tex.has(k):
		return _tex[k]
	var img := Image.create(size.x, size.y, false, Image.FORMAT_RGBA8)
	img.fill(Color(0, 0, 0, 0))
	var c := Vector2(size) / 2.0
	for y in size.y:
		for x in size.x:
			var d := (Vector2(x, y) - Vector2(c.x, size.y * 0.55)) / Vector2(size.x * 0.32, size.y * 0.42)
			if d.length() < 1.0:
				img.set_pixel(x, y, color.darkened(0.4 * d.length()))
	var t := ImageTexture.create_from_image(img)
	_tex[k] = t
	return t
