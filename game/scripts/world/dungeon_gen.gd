class_name DungeonGen
extends RefCounted

enum { WALL, FLOOR, WATER }

var w := 56
var h := 56
var grid := PackedByteArray()
var rooms: Array[Rect2i] = []
# dead-end rooms off the main way: where chests and shrines like to sit
var side_rooms: Array[Rect2i] = []
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
	w = int(round(int(sz[0]) * rng.randf_range(0.92, 1.08)))
	h = int(round(int(sz[1]) * rng.randf_range(0.92, 1.08)))
	grid = PackedByteArray()
	grid.resize(w * h)
	grid.fill(WALL)
	rooms.clear()
	side_rooms.clear()
	boss_spot = Vector2i(-1, -1)
	var styles: Array = def.get("styles", [def.get("style", "gallery")])
	style = str(styles[rng.randi_range(0, styles.size() - 1)])
	var is_boss: bool = def.get("boss", null) != null
	_zones(style == "lair")
	if style == "mixed":
		_roughen(1)
	_keep_largest()
	if not walkable(start) or not walkable(exit):
		_place_ends(is_boss)
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
	if not dist.has(exit) or dist[exit] < int(rules.get("min_path", (w + h) * 0.9)):
		return false
	if boss_spot.x >= 0 and (not dist.has(boss_spot) or dist[boss_spot] < max_dist * 0.6):
		return false
	return dist.size() >= int(w * h * float(rules.get("min_open", 0.15)))


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


# ---------------------------------------------------------------- zones
# The floor is cut into sectors. A long self-avoiding walk through them is the way from the stairs to the
# exit (or the boss), one room per sector, each joined only to the next, so the way winds over most of the
# map. Sectors beside the way grow short dead-end branches; a couple of loops cut back a few rooms; the
# rest stays solid rock.
func _zones(lair: bool) -> void:
	var band := int(h * 0.4) if lair else 0
	var cols := maxi(3, int(round(w / 19.0)))
	var rows := maxi(2, int(round((h - band) / 19.0)))
	var sx := float(w - 2) / cols
	var sy := float(h - 2 - band) / rows
	var sector := func(s: Vector2i) -> Rect2i:
		return Rect2i(1 + int(s.x * sx), 1 + band + int(s.y * sy), int(sx), int(sy))
	var route := _route(cols, rows)
	# leave room beside the way for branches
	route = route.slice(0, maxi(4, mini(route.size(), int(cols * rows * rng.randf_range(0.55, 0.7)))))
	if lair:
		# the walk has to end under the arena, so it is cut after its last sector in the top row
		var cut := 0
		for i in route.size():
			if route[i].y == 0:
				cut = i
		route = route.slice(0, cut + 1)
	var on_route := {}
	for i in route.size():
		on_route[route[i]] = i
	var centers := {}
	for i in route.size():
		var r: Rect2i = sector.call(route[i])
		var room := _room_rect(r, 0.72, 1.0)
		if i == route.size() - 1 and not lair:
			room = r.grow(-2)
		centers[route[i]] = _room(room, i == 0 or i == route.size() - 1)
		rooms.append(room)
	for i in range(1, route.size()):
		_join(centers[route[i - 1]], centers[route[i]], sector.call(route[i - 1]).merge(sector.call(route[i])), 3 if rng.randf() < 0.35 else 2)
	var loops := 0
	for i in route.size():
		for o in [Vector2i(1, 0), Vector2i(0, 1)]:
			var n: Vector2i = route[i] + o
			if loops < 2 and on_route.has(n) and absi(on_route[n] - i) in [3, 4] and rng.randf() < 0.5:
				_join(centers[route[i]], centers[n], sector.call(route[i]).merge(sector.call(n)), 2)
				loops += 1
	var frontier: Array = route.duplicate()
	for i in range(frontier.size() - 1, 0, -1):
		var j := rng.randi_range(0, i)
		var t = frontier[i]
		frontier[i] = frontier[j]
		frontier[j] = t
	var depth := {}
	for s in route:
		depth[s] = 0
	while not frontier.is_empty():
		var s: Vector2i = frontier.pop_back()
		if depth[s] >= 2:
			continue
		for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			var n: Vector2i = s + o
			if n.x < 0 or n.y < 0 or n.x >= cols or n.y >= rows or depth.has(n):
				continue
			if rng.randf() < (0.8 if depth[s] == 0 else 0.45):
				var room := _room_rect(sector.call(n), 0.5, 0.8)
				centers[n] = _room(room, false)
				side_rooms.append(room)
				rooms.append(room)
				_join(centers[s], centers[n], sector.call(s).merge(sector.call(n)), 2)
				depth[n] = depth[s] + 1
				frontier.push_front(n)
	start = centers[route[0]]
	exit = centers[route[-1]]
	if lair:
		_lair_arena(band, exit)


# Warnsdorff-style walk: prefer the neighbour with the fewest free neighbours, so the walk hugs edges and
# snakes instead of cutting across; the longest of many tries wins.
func _route(cols: int, rows: int) -> Array:
	var best: Array = []
	for attempt in 40:
		var s := Vector2i(rng.randi_range(0, cols - 1), rows - 1)
		var path: Array = [s]
		var seen := {s: true}
		while true:
			var opts := []
			for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
				var n: Vector2i = path[-1] + o
				if n.x >= 0 and n.y >= 0 and n.x < cols and n.y < rows and not seen.has(n):
					var free := 0
					for o2 in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
						var m: Vector2i = n + o2
						if m.x >= 0 and m.y >= 0 and m.x < cols and m.y < rows and not seen.has(m):
							free += 1
					opts.append([free + rng.randf() * 1.5, n])
			if opts.is_empty():
				break
			opts.sort_custom(func(a, b): return a[0] < b[0])
			var nxt: Vector2i = opts[0][1]
			path.append(nxt)
			seen[nxt] = true
		if path.size() > best.size():
			best = path
		if best.size() >= int(cols * rows * 0.8):
			break
	return best


func _room_rect(sec: Rect2i, lo: float, hi: float) -> Rect2i:
	var inner := sec.grow(-1)
	var rw := clampi(int(inner.size.x * rng.randf_range(lo, hi)), 4, inner.size.x)
	var rh := clampi(int(inner.size.y * rng.randf_range(lo, hi)), 4, inner.size.y)
	return Rect2i(inner.position + Vector2i(rng.randi_range(0, inner.size.x - rw), rng.randi_range(0, inner.size.y - rh)), Vector2i(rw, rh))


# Carves one room and returns a cell in it that corridors can aim at.
func _room(r: Rect2i, plain: bool) -> Vector2i:
	var c := r.get_center()
	var kinds: Array
	match style:
		"cave", "lair":
			kinds = ["cave", "cave", "blob", "blob", "ring_cave"]
		"mixed":
			kinds = ["cave", "blob", "hall", "pillars", "cross", "ring", "gallery", "chambers"]
		_:
			kinds = ["hall", "pillars", "pillars", "cross", "ring", "gallery", "gallery", "chambers", "blob"]
	var kind: String = "blob" if plain else kinds[rng.randi_range(0, kinds.size() - 1)]
	match kind:
		"hall":
			_carve_rect(r)
		"pillars":
			_carve_rect(r)
			if r.size.x >= 7 and r.size.y >= 6:
				for y in range(r.position.y + 2, r.end.y - 2, 3):
					for x in range(r.position.x + 2, r.end.x - 2, 3):
						if Vector2i(x, y).distance_to(c) > 1.5:
							setc(x, y, WALL)
		"cross":
			var t := maxi(3, mini(r.size.x, r.size.y) / 3)
			_carve_rect(Rect2i(r.position.x, c.y - t / 2, r.size.x, t))
			_carve_rect(Rect2i(c.x - t / 2, r.position.y, t, r.size.y))
		"ring":
			_carve_rect(r)
			if r.size.x >= 9 and r.size.y >= 8:
				var core := r.grow(-3)
				for y in range(core.position.y, core.end.y):
					for x in range(core.position.x, core.end.x):
						setc(x, y, WALL)
				c = Vector2i(r.position.x + 1, c.y)
		"ring_cave":
			_carve_blob(c, r.size.x / 2.0, r.size.y / 2.0)
			if r.size.x >= 10 and r.size.y >= 9:
				_wall_blob(c, r.size.x / 6.0, r.size.y / 6.0)
				c = Vector2i(r.position.x + 1, c.y)
		"gallery":
			if r.size.x >= r.size.y:
				_carve_rect(Rect2i(r.position.x, c.y - 1, r.size.x, 3))
				for x in range(r.position.x + 2, r.end.x - 1, 4):
					_carve_rect(Rect2i(x, c.y - 2 - rng.randi_range(0, 1), 2, 1))
			else:
				_carve_rect(Rect2i(c.x - 1, r.position.y, 3, r.size.y))
		"chambers":
			var parts := rng.randi_range(2, 3)
			var prev := Vector2i(-1, -1)
			for i in parts:
				var pw := clampi(r.size.x / 2, 4, 7)
				var ph := clampi(r.size.y / 2, 4, 6)
				var p := Rect2i(r.position + Vector2i(rng.randi_range(0, r.size.x - pw), rng.randi_range(0, r.size.y - ph)), Vector2i(pw, ph))
				_carve_rect(p)
				if prev.x >= 0:
					_tunnel(prev, p.get_center(), 2)
				prev = p.get_center()
			c = prev
		"cave":
			_cave_room(r)
		_:
			_carve_blob(c, r.size.x / 2.0, r.size.y / 2.0)
	_carve_blob(c, 1.6, 1.6)
	return c


# Two room centres joined through one random bend point inside both sectors, so the corridor never
# wanders through a third room.
func _join(a: Vector2i, b: Vector2i, bounds: Rect2i, width: int) -> void:
	var inner := bounds.grow(-2)
	if style in ["cave", "lair"] or (style == "mixed" and rng.randf() < 0.5):
		_meander(a, b, inner, width)
		return
	var mid := Vector2i(rng.randi_range(inner.position.x, inner.end.x - 1), rng.randi_range(inner.position.y, inner.end.y - 1))
	_tunnel(a, mid, width, true)
	_tunnel(mid, b, width, true)


# A passage that drifts towards its goal, sometimes widening into a pocket.
func _meander(a: Vector2i, b: Vector2i, bounds: Rect2i, width: int) -> void:
	var p := a
	var guard := 0
	while p != b and guard < 600:
		guard += 1
		var d := b - p
		var step := Vector2i(signi(d.x), 0) if absi(d.x) > absi(d.y) else Vector2i(0, signi(d.y))
		if rng.randf() < 0.35:
			step = Vector2i(step.y, step.x) * (1 if rng.randf() < 0.5 else -1)
		var n := p + step
		if bounds.has_point(n) or (n - b).length() < (p - b).length():
			p = n
		for oy in width:
			for ox in width:
				setc(p.x + ox - width / 2, p.y + oy - width / 2, FLOOR)
		if rng.randf() < 0.04:
			_carve_blob(p, rng.randf_range(1.5, 2.6), rng.randf_range(1.5, 2.4))


func _cave_room(r: Rect2i) -> void:
	var cells := {}
	for y in range(r.position.y, r.end.y):
		for x in range(r.position.x, r.end.x):
			cells[Vector2i(x, y)] = rng.randf() < 0.56
	for i in 4:
		var nxt := {}
		for c in cells:
			var n := 0
			for oy in range(-1, 2):
				for ox in range(-1, 2):
					if (ox != 0 or oy != 0) and not cells.get(c + Vector2i(ox, oy), false):
						n += 1
			nxt[c] = n < 5
		cells = nxt
	for c in cells:
		if cells[c]:
			setc(c.x, c.y, FLOOR)


func _lair_arena(band: int, entry: Vector2i) -> void:
	var arena := Vector2i(w / 2, band / 2 + 1)
	var rx := minf(w * 0.28, 15.0)
	var ry := minf(band * 0.42, 11.0)
	_carve_blob(arena, rx, ry)
	_tunnel(entry, Vector2i(entry.x, arena.y + int(ry) - 1), 3)
	rooms.append(Rect2i(arena - Vector2i(int(rx * 0.8), int(ry * 0.8)), Vector2i(int(rx * 1.6), int(ry * 1.6))))
	for i in 4:
		var pillar := arena + Vector2i(rng.randi_range(-int(rx * 0.6), int(rx * 0.6)), rng.randi_range(-int(ry * 0.5), int(ry * 0.5)))
		if (pillar - arena).length() > 4:
			for oy in 2:
				for ox in 2:
					setc(pillar.x + ox, pillar.y + oy, WALL)
	boss_spot = arena
	exit = arena


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


func _wall_blob(c: Vector2i, rx: float, ry: float) -> void:
	for y in range(int(c.y - ry - 1), int(c.y + ry + 2)):
		for x in range(int(c.x - rx - 1), int(c.x + rx + 2)):
			var dx := (x - c.x) / rx
			var dy := (y - c.y) / ry
			if dx * dx + dy * dy < 1.0:
				setc(x, y, WALL)


# Straight timbered runs; with alcoves, a side niche now and then breaks the line.
func _tunnel(a: Vector2i, b: Vector2i, width: int, alcoves := false) -> void:
	var p := a
	var horiz_first := rng.randf() < 0.5
	var bend := Vector2i(b.x, a.y) if horiz_first else Vector2i(a.x, b.y)
	var k := 0
	for target in [bend, b]:
		while p != target:
			var step := Vector2i(signi(target.x - p.x), signi(target.y - p.y))
			p += step
			for oy in width:
				for ox in width:
					setc(p.x + ox - width / 2, p.y + oy - width / 2, FLOOR)
			k += 1
			if alcoves and k % 5 == 0 and rng.randf() < 0.3:
				var side := Vector2i(step.y, step.x) * (1 if rng.randf() < 0.5 else -1)
				var o := p + side * (width / 2 + 1)
				_carve_rect(Rect2i(mini(o.x, o.x + side.x), mini(o.y, o.y + side.y), 2 if side.x != 0 else 2, 2))


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


# Fallback when the zone walk left the stairs in rock: the open cell farthest from a random start.
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
	start = floors[rng.randi_range(0, floors.size() - 1)]
	var d := bfs(start)
	var far := start
	var fd := -1
	for c in floors:
		if d.has(c) and d[c] > fd:
			fd = d[c]
			far = c
	exit = far
	if is_boss and style == "lair":
		boss_spot = far


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
