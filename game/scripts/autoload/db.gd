extends Node

# classes = the ones a new hero can be; all_classes also holds those saved for an expansion not out yet.
var classes := {}
var all_classes := {}
var expansions := {}
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
var cinema := {}
var props := {}
var codex := {}
var books := {}
var superuniques := {}
var hirelings := {}
var rare_names := {"first": [], "second": []}
var sets := {}
var set_items := {}
var words := {}
var codex_refs := {}
var codex_by_ref := {}

var _tex := {}
var _missing := {}


func _ready() -> void:
	reload()


func reload() -> void:
	all_classes = _j("classes", {})
	expansions = _j("expansions", {})
	classes = {}
	for cid in all_classes:
		if class_released(cid):
			classes[cid] = all_classes[cid]
	skills = _j("skills", {})
	monsters = _j("monsters", {})
	items = _j("items_base", {})
	affixes = _j("affixes", {"prefixes": [], "suffixes": []})
	uniques = _j("uniques", {})
	shrines = _j("shrines", {})
	champions = _j("champions", {"names": [], "mods": {}})
	superuniques = _j("superuniques", {})
	hirelings = _j("hirelings", {})
	npcs = _j("npcs", {})
	var a = _j("acts", [])
	acts = a if a is Array else []
	quests = _j("quests", {})
	dialog = _j("dialog", {})
	lore = _j("lore", {})
	slides = _j("slides", {})
	cinema = _j("cinematics", {})
	props = _j("props", {})
	codex = _j("codex", {})
	books = _j("books", {})
	rare_names = _j("rare_names", {"first": [], "second": []})
	var sd = _j("sets", {"sets": {}, "items": {}})
	sets = sd.get("sets", {})
	set_items = sd.get("items", {})
	words = _j("words", {})
	for id in items:
		if not class_released(str(items[id].get("class", ""))):
			items[id]["no_drop"] = true
	_index_codex()


func class_def(cid: String) -> Dictionary:
	return all_classes.get(cid, {})


func class_expansion(cid: String) -> String:
	for eid in expansions:
		if cid in expansions[eid].get("classes", []):
			return eid
	return ""


func class_released(cid: String) -> bool:
	if cid == "" or not all_classes.has(cid):
		return true
	var eid := class_expansion(cid)
	return eid == "" or bool(expansions[eid].get("released", false)) or OS.get_cmdline_user_args().has("--all-classes")


# The class a "class_<id>" / "tree_<id>" stat belongs to, or "".
func stat_class(stat: String) -> String:
	if stat.begins_with("class_"):
		return stat.substr(6)
	if stat.begins_with("tree_"):
		var tid := stat.substr(5)
		for cid in all_classes:
			for t in all_classes[cid].get("trees", []):
				if t.id == tid:
					return cid
	return ""


func _index_codex() -> void:
	codex_refs = {}
	codex_by_ref = {}
	for eid in codex:
		var keys := []
		var refs: Dictionary = codex[eid].get("refs", {})
		for kind in refs:
			for id in refs[kind]:
				var k := "%s:%s" % [kind, id]
				keys.append(k)
				if not codex_by_ref.has(k):
					codex_by_ref[k] = []
				codex_by_ref[k].append(eid)
		codex_refs[eid] = keys


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
	return act(act_n).get("floors", []).filter(func(f): return not f.has("uber")).size()


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
