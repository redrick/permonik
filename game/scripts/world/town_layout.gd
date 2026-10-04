class_name TownLayout
extends DungeonGen

var placements: Array = []
var points := {}
var npc_spots := {}
var reserved := {}
var paths := {}
var keep_clear: Array[Vector2i] = []

const BUILDINGS := {
	1: {"mine": "sachta_hora", "smith": "kovarna", "inn": "hostinec", "healer": "chalupa", "a": "dum_a", "b": "dum_b", "landmark": "chram_barbory", "extra": "zvonice"},
	2: {"mine": "sachta_vojtech", "smith": "kovarna", "inn": "hostinec", "healer": "chalupa", "a": "dum_c", "b": "dum_a", "landmark": "socha_permonika", "extra": "dum_b"},
	3: {"mine": "sachta_svornost", "smith": "mincovna", "inn": "hostinec", "healer": "chalupa", "a": "dum_b", "b": "dum_c", "landmark": "kovarna", "extra": "dum_a"},
	4: {"mine": "schody_dolu", "smith": "stan", "inn": "stan", "healer": "stan", "a": "stan", "b": "ohniste", "landmark": "kalinov_most", "extra": "stan"},
}
# Where a non-building NPC stands: "edge" = among the trees at the town's rim, "square" = by the well.
const NPC_PLACE := {"fabian": "edge", "tremsinsky_muzicek": "edge", "anicka": "square", "ghost": "square", "other": "any"}


static func make(act_n: int, seed_v: int) -> TownLayout:
	var t := TownLayout.new()
	for attempt in 16:
		t._make(act_n, seed_v + attempt * 104729)
		if t._reachable():
			break
	return t


# Fixed rules, random everything else: the shaft is on the north edge with the cage beside it, you arrive by
# the well with the stash at hand, each trader stands at the door of their own house, the chronicler's
# lectern is on the square, and every one of them can be walked to.
func _make(act_n: int, seed_v: int) -> void:
	rng.seed = seed_v
	placements.clear()
	points.clear()
	npc_spots.clear()
	reserved.clear()
	paths.clear()
	keep_clear.clear()
	w = rng.randi_range(46, 54)
	h = rng.randi_range(34, 40)
	grid = PackedByteArray()
	grid.resize(w * h)
	grid.fill(FLOOR)
	for y in h:
		for x in w:
			if x < 2 or y < 3 or x >= w - 2 or y >= h - 2:
				grid[y * w + x] = WALL
	var b: Dictionary = BUILDINGS.get(act_n, BUILDINGS[1])
	var mine := Vector2i(rng.randi_range(int(w * 0.3), int(w * 0.7)), rng.randi_range(7, 8))
	_put(b.mine, mine, {"interact": "stairs_down"})
	exit = mine + Vector2i(0, 1)
	points["mine"] = mine + Vector2i(0, 2)
	points["stairs_down"] = points.mine
	var side := 1 if rng.randf() < 0.5 else -1
	var cage := mine + Vector2i(side * rng.randi_range(5, 7), 1)
	if not _fits("klec", cage, 1):
		cage = mine + Vector2i(-side * 6, 1)
	_put("klec", cage, {"interact": "waypoint"})
	points["waypoint"] = cage + Vector2i(0, 1)
	var sq := Vector2i(rng.randi_range(int(w * 0.38), int(w * 0.62)), rng.randi_range(maxi(mine.y + 10, int(h * 0.48)), int(h * 0.62)))
	_put("studna" if act_n != 4 else "ohniste", sq)
	start = sq + Vector2i(0, -3)
	points["center"] = sq + Vector2i(0, 2)
	points["start"] = start
	points["portal"] = start + Vector2i(-3, 1)
	points["portal_back"] = points.portal
	var stash := sq + Vector2i(rng.randi_range(3, 5) * (1 if rng.randf() < 0.5 else -1), -2)
	_put("truhla", stash, {"interact": "stash"})
	points["stash"] = stash + Vector2i(0, 1)
	points["lectern"] = sq + Vector2i(-5 if stash.x > sq.x else 5, 1)
	npc_spots["guide"] = mine + Vector2i(-side * 3, 2)
	npc_spots["chronicler"] = points.lectern + Vector2i(2 if stash.x > sq.x else -2, 1)
	keep_clear = [points.mine, points.waypoint, start, points.portal, points.center, points.stash, points.lectern,
		npc_spots.guide, npc_spots.chronicler]
	for key in ["smith", "inn", "healer"]:
		var c := _plot(b[key], sq, 7, 16, Rect2i(3, mine.y + 3, w - 6, h - mine.y - 6))
		if c.x >= 0:
			_put(b[key], c)
			npc_spots[key] = c + Vector2i(1, 2)
			keep_clear.append(npc_spots[key])
	var lm := _plot(b.landmark, sq, 9, 20, Rect2i(3, sq.y + 2, w - 6, h - sq.y - 4))
	if lm.x < 0:
		lm = _plot(b.landmark, sq, 8, 24, Rect2i(3, 6, w - 6, h - 8))
	if lm.x >= 0:
		_put(b.landmark, lm, {"block": DB.prop(b.landmark).get("blocks", true)})
	for key in (["a", "b", "extra"] if act_n != 4 else ["a", "extra"]):
		var c := _plot(b[key], sq, 6, 22, Rect2i(3, 5, w - 6, h - 7))
		if c.x >= 0:
			_put(b[key], c)
	_place_side_npcs(act_n, sq)
	_lay_paths(sq)
	var lamp := "lucerna" if act_n != 4 else "navi_svice"
	var a0 := rng.randf() * TAU
	for i in 4:
		var a := a0 + TAU * i / 4.0
		var c := sq + Vector2i(int(round(cos(a) * 5)), int(round(sin(a) * 3.5)))
		if _fits(lamp, c, 0):
			_put(lamp, c, {"block": false})
	var trail: Array = paths.keys()
	trail.shuffle()
	var lamps := 0
	for c in trail:
		if lamps >= 4:
			break
		var off: Vector2i = c + Vector2i(1 if rng.randf() < 0.5 else -1, 0)
		if not paths.has(off) and _fits(lamp, off, 1) and (off - sq).length() > 7:
			_put(lamp, off, {"block": false})
			lamps += 1
	_plant_trees(act_n)


func _place_side_npcs(act_n: int, sq: Vector2i) -> void:
	var ad := DB.act(act_n)
	for nid in ad.get("town", {}).get("npcs", []):
		var role := str(DB.npcs.get(nid, {}).get("role", "other"))
		if npc_spots.has(role) and role != "other":
			continue
		var how: String = NPC_PLACE.get(nid, NPC_PLACE.get(role, "any"))
		for t in 200:
			var c := Vector2i(rng.randi_range(4, w - 5), rng.randi_range(6, h - 4))
			match how:
				"edge":
					c.x = rng.randi_range(4, 6) if rng.randf() < 0.5 else rng.randi_range(w - 7, w - 5)
				"square":
					c = sq + Vector2i(rng.randi_range(-7, 7), rng.randi_range(-4, 5))
			if _fits("", c, 1) and _far_from_spots(c, 5):
				npc_spots[str(nid)] = c
				keep_clear.append(c)
				break


func _far_from_spots(c: Vector2i, d: float) -> bool:
	for k in npc_spots:
		if (npc_spots[k] - c).length() < d:
			return false
	return true


# A free spot for a building at min..max cells from the square, inside the area.
func _plot(id: String, sq: Vector2i, dmin: float, dmax: float, area: Rect2i) -> Vector2i:
	for t in 300:
		var c := Vector2i(rng.randi_range(area.position.x, area.end.x - 1), rng.randi_range(area.position.y, area.end.y - 1))
		var d := (c - sq).length()
		if d >= dmin and d <= dmax and _fits(id, c, 1, 3):
			return c
	return Vector2i(-1, -1)


func _rect_of(id: String, c: Vector2i) -> Rect2i:
	var fp := _footprint(id)
	var fw := maxi(fp.x, 1)
	var fh := maxi(fp.y, 1)
	return Rect2i(c.x - fw / 2, c.y - fh + 1, fw, fh)


# The footprint plus a margin (and room above for the roof) must be open ground.
func _fits(id: String, c: Vector2i, margin: int, above := 0) -> bool:
	var r := _rect_of(id, c) if id != "" else Rect2i(c, Vector2i.ONE)
	r = Rect2i(r.position - Vector2i(margin, margin + above), r.size + Vector2i(margin * 2, margin * 2 + above))
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			if reserved.has(Vector2i(x, y)) or at(x, y) == WALL or paths.has(Vector2i(x, y)):
				return false
	for k in keep_clear:
		if r.grow(1).has_point(k):
			return false
	return true


func _footprint(id: String) -> Vector2i:
	var fp = DB.prop(id).get("footprint", [1, 1])
	return Vector2i(int(fp[0]), int(fp[1]))


func _put(id: String, c: Vector2i, opts := {}) -> void:
	var pl := {"id": id, "cell": c}
	pl.merge(opts)
	placements.append(pl)
	var r := _rect_of(id, c)
	for y in range(r.position.y - 1, r.end.y + 1):
		for x in range(r.position.x - 1, r.end.x + 1):
			reserved[Vector2i(x, y)] = true


func _blocked_grid() -> PackedByteArray:
	var g := PackedByteArray()
	g.resize(w * h)
	for y in h:
		for x in w:
			g[y * w + x] = 1 if at(x, y) == WALL else 0
	for pl in placements:
		if not pl.get("block", true) or not DB.prop(pl.id).get("blocks", true):
			continue
		var r := _rect_of(pl.id, pl.cell)
		for y in range(r.position.y, r.end.y):
			for x in range(r.position.x, r.end.x):
				if x >= 0 and y >= 0 and x < w and y < h:
					g[y * w + x] = 1
	return g


func _walk(from: Vector2i, g: PackedByteArray) -> Dictionary:
	var prev := {from: from}
	var q := [from]
	var i := 0
	while i < q.size():
		var c: Vector2i = q[i]
		i += 1
		for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = c + o
			if n.x >= 0 and n.y >= 0 and n.x < w and n.y < h and not prev.has(n) and g[n.y * w + n.x] == 0:
				prev[n] = c
				q.append(n)
	return prev


# Footpaths from the square to the shaft and to every door, drawn along the shortest walk.
func _lay_paths(sq: Vector2i) -> void:
	var g := _blocked_grid()
	var from := sq + Vector2i(0, 2)
	var prev := _walk(from, g)
	var goals: Array = [points.mine, points.waypoint]
	for k in ["smith", "inn", "healer"]:
		if npc_spots.has(k):
			goals.append(npc_spots[k])
	for goal in goals:
		var c: Vector2i = goal
		while prev.has(c) and c != from:
			paths[c] = true
			c = prev[c]
	for oy in range(-1, 3):
		for ox in range(-3, 4):
			var c := sq + Vector2i(ox, oy)
			if g[c.y * w + c.x] == 0:
				paths[c] = true


func _plant_trees(act_n: int) -> void:
	var tree_ids := ["strom_a", "strom_b", "smrk"] if act_n != 4 else ["lebky", "navi_svice", "kosti"]
	if act_n == 3:
		tree_ids = ["smrk", "smrk", "strom_b"]
	var n := rng.randi_range(60, 85)
	for i in n * 6:
		if n <= 0:
			break
		var c := Vector2i(rng.randi_range(3, w - 4), rng.randi_range(4, h - 3))
		var rim := c.x < 6 or c.x > w - 7 or c.y > h - 5 or c.y < 6
		if (rim or rng.randf() < 0.15) and _fits("strom_a", c, 1):
			_put(tree_ids[rng.randi_range(0, tree_ids.size() - 1)], c, {"block": true})
			n -= 1


func _reachable() -> bool:
	var reach := _walk(start, _blocked_grid())
	for k in points:
		if not reach.has(points[k]):
			return false
	for k in npc_spots:
		if not reach.has(npc_spots[k]):
			return false
	return npc_spots.has("smith") and npc_spots.has("inn") and npc_spots.has("healer")
