class_name DungeonGen
extends RefCounted

enum { WALL, FLOOR, WATER }

var w := 56
var h := 56
var grid := PackedByteArray()
var rooms: Array[Rect2i] = []
var start := Vector2i.ZERO
var exit := Vector2i.ZERO
var boss_spot := Vector2i(-1, -1)
var rng := RandomNumberGenerator.new()


func at(x: int, y: int) -> int:
	if x < 0 or y < 0 or x >= w or y >= h:
		return WALL
	return grid[y * w + x]


func setc(x: int, y: int, v: int) -> void:
	if x <= 0 or y <= 0 or x >= w - 1 or y >= h - 1:
		return
	grid[y * w + x] = v


func walkable(c: Vector2i) -> bool:
	return at(c.x, c.y) != WALL


var style := "gallery"
var dist := {}
var max_dist := 1


# Layout is random per seed within the floor's rules; a draw that breaks them is thrown away.
func generate(def: Dictionary, seed_v: int) -> void:
	for attempt in 12:
		_generate_once(def, seed_v + attempt * 7919)
		if _meets_rules(def):
			return


func _generate_once(def: Dictionary, seed_v: int) -> void:
	rng.seed = seed_v
	var sz = def.get("size", [56, 56])
	w = int(round(int(sz[0]) * rng.randf_range(0.9, 1.1)))
	h = int(round(int(sz[1]) * rng.randf_range(0.9, 1.1)))
	grid = PackedByteArray()
	grid.resize(w * h)
	grid.fill(WALL)
	rooms.clear()
	boss_spot = Vector2i(-1, -1)
	var styles: Array = def.get("styles", [def.get("style", "gallery")])
	style = str(styles[rng.randi_range(0, styles.size() - 1)])
	_carve(style)
	_keep_largest()
	var is_boss: bool = def.get("boss", null) != null
	_place_ends(style == "lair" or is_boss)
	if is_boss:
		_make_arena(def)
	var water := float(def.get("water", 0.0)) * rng.randf_range(0.7, 1.3)
	if water > 0.0:
		_flood(water)
	dist = bfs(start)
	max_dist = 1
	for c in dist:
		max_dist = maxi(max_dist, dist[c])


func _meets_rules(def: Dictionary) -> bool:
	var rules: Dictionary = def.get("rules", {})
	if not dist.has(exit) or dist[exit] < int(rules.get("min_path", (w + h) * 0.35)):
		return false
	if boss_spot.x >= 0 and (not dist.has(boss_spot) or dist[boss_spot] < max_dist * 0.6):
		return false
	return dist.size() >= int(w * h * float(rules.get("min_open", 0.2)))


# The boss always gets a room of its own at the far end, whatever the layout; the stairs down wait behind it.
func _make_arena(def: Dictionary) -> void:
	var ar = def.get("rules", {}).get("arena", [7, 5])
	if style != "lair":
		var far := exit
		var rx := float(ar[0])
		var ry := float(ar[1])
		var c := Vector2i(clampi(far.x, int(rx) + 2, w - int(rx) - 3), clampi(far.y, int(ry) + 2, h - int(ry) - 3))
		_carve_blob(c, rx, ry)
		_tunnel(c, far, 2)
		rooms.append(Rect2i(c - Vector2i(int(rx), int(ry)), Vector2i(int(rx) * 2, int(ry) * 2)))
		boss_spot = c
	var d := bfs(start)
	var best := exit
	var bd := -1
	for y in range(boss_spot.y - 8, boss_spot.y + 9):
		for x in range(boss_spot.x - 8, boss_spot.x + 9):
			var cc := Vector2i(x, y)
			if d.has(cc) and open_cell(cc) and d[cc] > bd and (cc - boss_spot).length() >= 3:
				bd = d[cc]
				best = cc
	exit = best


func _carve(st: String) -> void:
	match st:
		"cave":
			_cave()
		"mixed":
			_gallery()
			_roughen(2)
		"lair":
			_lair()
		_:
			_gallery()


func _carve_rect(r: Rect2i) -> void:
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			setc(x, y, FLOOR)


func _carve_blob(c: Vector2i, rx: float, ry: float) -> void:
	for y in range(int(c.y - ry - 2), int(c.y + ry + 3)):
		for x in range(int(c.x - rx - 2), int(c.x + rx + 3)):
			var dx := (x - c.x) / rx
			var dy := (y - c.y) / ry
			var n := 1.0 + rng.randf_range(-0.18, 0.18)
			if dx * dx + dy * dy < n:
				setc(x, y, FLOOR)


func _gallery() -> void:
	var tries := 0
	var target := int(w * h / 260.0) + 4
	while rooms.size() < target and tries < 400:
		tries += 1
		var rw := rng.randi_range(5, 11)
		var rh := rng.randi_range(4, 9)
		var r := Rect2i(rng.randi_range(2, w - rw - 3), rng.randi_range(2, h - rh - 3), rw, rh)
		var ok := true
		for o in rooms:
			if r.grow(3).intersects(o):
				ok = false
				break
		if ok:
			rooms.append(r)
	for r in rooms:
		if rng.randf() < 0.45:
			_carve_blob(r.get_center(), r.size.x / 2.0 + 0.5, r.size.y / 2.0 + 0.5)
		else:
			_carve_rect(r)
	var centers: Array[Vector2i] = []
	for r in rooms:
		centers.append(r.get_center())
	var connected := [0]
	var edges := []
	while connected.size() < centers.size():
		var best := Vector3i(-1, -1, 1 << 30)
		for i in connected:
			for j in centers.size():
				if j in connected:
					continue
				var dd := (centers[i] - centers[j]).length_squared()
				if dd < best.z:
					best = Vector3i(i, j, dd)
		connected.append(best.y)
		edges.append(Vector2i(best.x, best.y))
	for k in int(centers.size() * 0.25):
		var a := rng.randi_range(0, centers.size() - 1)
		var b := rng.randi_range(0, centers.size() - 1)
		if a != b and (centers[a] - centers[b]).length() < w * 0.45:
			edges.append(Vector2i(a, b))
	for e in edges:
		_tunnel(centers[e.x], centers[e.y], 2 if rng.randf() < 0.7 else 3)


func _tunnel(a: Vector2i, b: Vector2i, width: int) -> void:
	var p := a
	var horiz_first := rng.randf() < 0.5
	var bend := Vector2i(b.x, a.y) if horiz_first else Vector2i(a.x, b.y)
	for target in [bend, b]:
		while p != target:
			p += Vector2i(signi(target.x - p.x), signi(target.y - p.y))
			for oy in width:
				for ox in width:
					setc(p.x + ox - width / 2, p.y + oy - width / 2, FLOOR)


func _cave() -> void:
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			grid[y * w + x] = FLOOR if rng.randf() < 0.54 else WALL
	for i in 5:
		_smooth()
	_roughen(0)


func _smooth() -> void:
	var nxt := grid.duplicate()
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			var n := 0
			for oy in range(-1, 2):
				for ox in range(-1, 2):
					if (ox != 0 or oy != 0) and at(x + ox, y + oy) == WALL:
						n += 1
			nxt[y * w + x] = WALL if n >= 5 else (FLOOR if n <= 3 else grid[y * w + x])
	grid = nxt


func _roughen(passes: int) -> void:
	for i in passes:
		for y in range(1, h - 1):
			for x in range(1, w - 1):
				if at(x, y) == WALL and rng.randf() < 0.18:
					var n := 0
					for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
						if at(x + o.x, y + o.y) == FLOOR:
							n += 1
					if n >= 2:
						setc(x, y, FLOOR)
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			if at(x, y) == FLOOR:
				var n := 0
				for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
					if at(x + o.x, y + o.y) == FLOOR:
						n += 1
				if n == 0:
					setc(x, y, WALL)


func _lair() -> void:
	var arena := Vector2i(w / 2, int(h * 0.38))
	_carve_blob(arena, w * 0.3, h * 0.24)
	var entry := Vector2i(w / 2 + rng.randi_range(-4, 4), h - 6)
	_carve_blob(entry, 4.5, 3.5)
	_tunnel(entry, arena + Vector2i(0, int(h * 0.2)), 3)
	for i in 3:
		var side := Vector2i(rng.randi_range(6, w - 7), rng.randi_range(int(h * 0.55), h - 8))
		_carve_blob(side, rng.randf_range(3, 5), rng.randf_range(3, 4))
		_tunnel(side, entry, 2)
	rooms.append(Rect2i(arena - Vector2i(int(w * 0.25), int(h * 0.2)), Vector2i(int(w * 0.5), int(h * 0.4))))
	for i in 4:
		var pillar := arena + Vector2i(rng.randi_range(-int(w * 0.18), int(w * 0.18)), rng.randi_range(-int(h * 0.12), int(h * 0.12)))
		if (pillar - arena).length() > 4:
			for oy in 2:
				for ox in 2:
					setc(pillar.x + ox, pillar.y + oy, WALL)


func _keep_largest() -> void:
	var seen := PackedByteArray()
	seen.resize(w * h)
	var best: Array = []
	for y in h:
		for x in w:
			if at(x, y) != WALL and seen[y * w + x] == 0:
				var region := _flood_region(Vector2i(x, y), seen)
				if region.size() > best.size():
					best = region
	grid.fill(WALL)
	for c in best:
		grid[c.y * w + c.x] = FLOOR


func _flood_region(s: Vector2i, seen: PackedByteArray) -> Array:
	var out := []
	var stack := [s]
	seen[s.y * w + s.x] = 1
	while not stack.is_empty():
		var c: Vector2i = stack.pop_back()
		out.append(c)
		for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = c + o
			if n.x >= 0 and n.y >= 0 and n.x < w and n.y < h and seen[n.y * w + n.x] == 0 and at(n.x, n.y) != WALL:
				seen[n.y * w + n.x] = 1
				stack.append(n)
	return out


func bfs(from: Vector2i) -> Dictionary:
	var dist := {from: 0}
	var q := [from]
	var i := 0
	while i < q.size():
		var c: Vector2i = q[i]
		i += 1
		for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = c + o
			if not dist.has(n) and walkable(n):
				dist[n] = dist[c] + 1
				q.append(n)
	return dist


func open_cell(c: Vector2i, r := 1) -> bool:
	for oy in range(-r, r + 1):
		for ox in range(-r, r + 1):
			if not walkable(c + Vector2i(ox, oy)):
				return false
	return true


func _place_ends(is_boss: bool) -> void:
	var floors := []
	for y in h:
		for x in w:
			if at(x, y) == FLOOR and open_cell(Vector2i(x, y)):
				floors.append(Vector2i(x, y))
	if floors.is_empty():
		_carve_blob(Vector2i(w / 2, h / 2), 6, 6)
		_place_ends(is_boss)
		return
	if is_boss and rooms.size() > 0 and floors.size() > 0:
		var far_pick: Vector2i = floors[0]
		var bottom := -1
		for c in floors:
			if c.y > bottom:
				bottom = c.y
				far_pick = c
		start = far_pick
	else:
		start = floors[rng.randi_range(0, floors.size() - 1)]
	var dist := bfs(start)
	var far := start
	var fd := -1
	for c in floors:
		if dist.has(c) and dist[c] > fd:
			fd = dist[c]
			far = c
	exit = far
	if is_boss:
		boss_spot = far
		var arena_center := Vector2i(-1, -1)
		if rooms.size() > 0:
			arena_center = rooms[rooms.size() - 1].get_center() if rooms.size() == 1 else Vector2i(-1, -1)
		if arena_center.x >= 0 and walkable(arena_center):
			boss_spot = arena_center


func _flood(frac: float) -> void:
	var cells := []
	for y in h:
		for x in w:
			if at(x, y) == FLOOR:
				cells.append(Vector2i(x, y))
	var target := int(cells.size() * frac)
	var count := 0
	var guard := 0
	while count < target and guard < 40:
		guard += 1
		var seed_c: Vector2i = cells[rng.randi_range(0, cells.size() - 1)]
		if (seed_c - start).length() < 6:
			continue
		var q := [seed_c]
		var i := 0
		var budget := rng.randi_range(30, 120)
		while i < q.size() and budget > 0 and count < target:
			var c: Vector2i = q[i]
			i += 1
			if at(c.x, c.y) != FLOOR or (c - start).length() < 4 or c == exit:
				continue
			grid[c.y * w + c.x] = WATER
			count += 1
			budget -= 1
			for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				if rng.randf() < 0.8:
					q.append(c + o)


func floor_cells(min_dist_from_start := 0) -> Array:
	var out := []
	for y in h:
		for x in w:
			var c := Vector2i(x, y)
			if at(x, y) != WALL and (c - start).length() >= min_dist_from_start:
				out.append(c)
	return out


func wall_adjacent_floor() -> Array:
	var out := []
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			if at(x, y) == FLOOR and at(x, y - 1) == WALL and at(x - 1, y) != WALL and at(x + 1, y) != WALL and at(x, y + 1) != WALL:
				out.append(Vector2i(x, y))
	return out
