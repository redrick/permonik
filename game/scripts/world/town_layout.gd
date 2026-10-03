class_name TownLayout
extends DungeonGen

var placements: Array = []
var points := {}
var npc_spots := {}
var reserved := {}

const BUILDINGS := {
	1: {"mine": "sachta_hora", "smith": "kovarna", "inn": "hostinec", "healer": "chalupa", "a": "dum_a", "b": "dum_b", "landmark": "chram_barbory", "extra": "zvonice"},
	2: {"mine": "sachta_vojtech", "smith": "kovarna", "inn": "hostinec", "healer": "chalupa", "a": "dum_c", "b": "dum_a", "landmark": "socha_permonika", "extra": "dum_b"},
	3: {"mine": "sachta_svornost", "smith": "mincovna", "inn": "hostinec", "healer": "chalupa", "a": "dum_b", "b": "dum_c", "landmark": "kovarna", "extra": "dum_a"},
	4: {"mine": "schody_dolu", "smith": "stan", "inn": "stan", "healer": "stan", "a": "stan", "b": "ohniste", "landmark": "kalinov_most", "extra": "stan"},
}


static func make(act_n: int) -> TownLayout:
	var t := TownLayout.new()
	t._make(act_n)
	return t


func _make(act_n: int) -> void:
	rng.seed = 1000 + act_n
	w = 48
	h = 36
	grid = PackedByteArray()
	grid.resize(w * h)
	grid.fill(FLOOR)
	for y in h:
		for x in w:
			if x < 2 or y < 3 or x >= w - 2 or y >= h - 2:
				grid[y * w + x] = WALL
	var b: Dictionary = BUILDINGS.get(act_n, BUILDINGS[1])
	_put(b.mine, Vector2i(24, 8), {"interact": "stairs_down", "block": true})
	_put("klec", Vector2i(18, 9), {"interact": "waypoint"})
	_put(b.smith, Vector2i(10, 15))
	_put(b.inn, Vector2i(38, 15))
	_put(b.healer, Vector2i(10, 27))
	_put(b.a, Vector2i(38, 27))
	_put(b.landmark, Vector2i(24, 31))
	_put(b.extra, Vector2i(33, 8))
	_put("studna" if act_n != 4 else "ohniste", Vector2i(24, 20))
	_put("truhla", Vector2i(28, 18), {"interact": "stash"})
	if act_n != 4:
		_put(b.b, Vector2i(14, 8))
	for c in [Vector2i(19, 16), Vector2i(29, 16), Vector2i(19, 24), Vector2i(29, 24), Vector2i(24, 12)]:
		_put("lucerna" if act_n != 4 else "navi_svice", c, {"block": false})
	start = Vector2i(24, 17)
	exit = Vector2i(24, 9)
	points = {"start": Vector2i(24, 17), "mine": Vector2i(24, 10), "stairs_down": Vector2i(24, 10), "portal": Vector2i(21, 18),
		"portal_back": Vector2i(21, 18), "waypoint": Vector2i(18, 10), "center": Vector2i(24, 22)}
	npc_spots = {"guide": Vector2i(27, 10), "smith": Vector2i(11, 17), "inn": Vector2i(37, 17), "healer": Vector2i(11, 29),
		"chronicler": Vector2i(21, 21), "other": Vector2i(32, 22), "ghost": Vector2i(16, 22), "fabian": Vector2i(43, 22),
		"tremsinsky_muzicek": Vector2i(6, 21), "anicka": Vector2i(14, 28), "prevoznik": Vector2i(34, 30), "predak_matej": Vector2i(11, 17)}
	var tree_ids := ["strom_a", "strom_b", "smrk"] if act_n != 4 else ["lebky", "navi_svice", "kosti"]
	if act_n == 3:
		tree_ids = ["smrk", "smrk", "strom_b"]
	for i in 40:
		var c := Vector2i(rng.randi_range(3, w - 4), rng.randi_range(4, h - 3))
		if _free(c, 2) and (c.x < 6 or c.x > w - 7 or c.y > h - 5 or c.y < 6 or rng.randf() < 0.2):
			_put(tree_ids[rng.randi_range(0, tree_ids.size() - 1)], c, {"block": true})


func _footprint(id: String) -> Vector2i:
	var fp = DB.prop(id).get("footprint", [1, 1])
	return Vector2i(int(fp[0]), int(fp[1]))


func _free(c: Vector2i, margin: int) -> bool:
	for oy in range(-margin - 1, margin + 1):
		for ox in range(-margin, margin + 1):
			if reserved.has(c + Vector2i(ox, oy)) or at(c.x + ox, c.y + oy) == WALL:
				return false
	for k in [Vector2i(24, 10), Vector2i(24, 17), Vector2i(21, 18), Vector2i(18, 10)]:
		if (c - k).length() < 3:
			return false
	return true


func _put(id: String, c: Vector2i, opts := {}) -> void:
	var pl := {"id": id, "cell": c}
	pl.merge(opts)
	placements.append(pl)
	var fp := _footprint(id)
	for y in range(c.y - maxi(fp.y, 1) - 1, c.y + 2):
		for x in range(c.x - maxi(fp.x, 1) / 2 - 1, c.x + maxi(fp.x, 1) / 2 + 2):
			reserved[Vector2i(x, y)] = true
