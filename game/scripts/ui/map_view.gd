class_name MapView
extends Control

# The explored level drawn like the rest of the game: crayon-coloured ground, pencil walls with hatching
# on the rock side, and the drawn map symbols. Used by the Tab sheet and the corner minimap.

const GRAPHITE := Color(0.16, 0.13, 0.12, 0.9)
const GRAPHITE_SOFT := Color(0.25, 0.2, 0.17, 0.4)
const ICON := {"stairs_down": "map_stairs_down", "stairs_up": "map_stairs_up", "waypoint": "map_cage", "portal": "map_portal",
	"shrine": "map_shrine", "quest": "map_quest", "book": "map_book"}

var zoom := 12.0
var follow := true          # centre on the hero (minimap) or on the level (sheet)
var radius := 0.0           # > 0: only draw cells within this many px of the centre
var icon_px := 22.0

var _rev := -1
var _level: Level = null
var _floor: Array[Vector2i] = []
var _water: Array[Vector2i] = []
var _path: Array[Vector2i] = []
var _walls: Array = []      # polylines in cell space
var _hatch: Array = []      # pairs of points in cell space
var _tex := {}
var _rebuilt_at := -1000


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	for k in ["map_floor", "map_floor_town", "map_water", "map_hero", "map_npc", "map_boss", "quest_new", "quest_new_side", "quest_turnin"] + ICON.values():
		_tex[k] = DB.tex("ui/" + k)


func _process(_d: float) -> void:
	if is_visible_in_tree():
		queue_redraw()


func origin() -> Vector2:
	var lv := _level
	if follow:
		return size / 2.0 - Vector2(lv.player.global_position) / Level.CELL * zoom
	return size / 2.0 - Vector2(lv.w, lv.h) * zoom / 2.0


func _rebuild(lv: Level) -> void:
	_level = lv
	_rev = lv.explored_rev
	_floor.clear()
	_water.clear()
	_path.clear()
	_walls.clear()
	_hatch.clear()
	var paths: Dictionary = (lv.gen as TownLayout).paths if lv.is_town else {}
	var seen := func(x: int, y: int) -> bool:
		return x >= 0 and y >= 0 and x < lv.w and y < lv.h and lv.explored[y * lv.w + x] == 1
	var open := func(x: int, y: int) -> bool:
		return lv.gen.at(x, y) != DungeonGen.WALL
	var edges := {}
	for y in lv.h:
		for x in lv.w:
			if not seen.call(x, y):
				continue
			if open.call(x, y):
				_floor.append(Vector2i(x, y))
				if lv.water[y * lv.w + x] == 1:
					_water.append(Vector2i(x, y))
				elif paths.has(Vector2i(x, y)):
					_path.append(Vector2i(x, y))
				# a wall edge wherever explored ground meets rock; stored as unit segments to chain later
				if not open.call(x, y - 1):
					edges[[Vector2i(x, y), Vector2i(x + 1, y)]] = true
				if not open.call(x, y + 1):
					edges[[Vector2i(x, y + 1), Vector2i(x + 1, y + 1)]] = true
				if not open.call(x - 1, y):
					edges[[Vector2i(x, y), Vector2i(x, y + 1)]] = true
				if not open.call(x + 1, y):
					edges[[Vector2i(x + 1, y), Vector2i(x + 1, y + 1)]] = true
			else:
				var touch := false
				for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
					if open.call(x + o.x, y + o.y) and seen.call(x + o.x, y + o.y):
						touch = true
				if touch:
					var h := _hash(x, y)
					for k in 2:
						var t := 0.25 + 0.5 * k + (h - 0.5) * 0.15
						_hatch.append([Vector2(x + t - 0.2, y + 0.85), Vector2(x + t + 0.25, y + 0.15)])
	_walls = _chain(edges)


func _chain(edges: Dictionary) -> Array:
	var adj := {}
	for e in edges:
		for i in 2:
			var p: Vector2i = e[i]
			if not adj.has(p):
				adj[p] = []
			adj[p].append(e[1 - i])
	var used := {}
	var out := []
	for e in edges:
		if used.has(e):
			continue
		used[e] = true
		var line: Array = [e[0], e[1]]
		for dir in 2:
			var grow := true
			while grow:
				grow = false
				var tip: Vector2i = line[line.size() - 1] if dir == 0 else line[0]
				for nb in adj.get(tip, []):
					var key := [tip, nb] if edges.has([tip, nb]) else [nb, tip]
					if used.has(key):
						continue
					used[key] = true
					if dir == 0:
						line.append(nb)
					else:
						line.push_front(nb)
					grow = true
					break
		var pts := PackedVector2Array()
		for i in line.size():
			var p: Vector2i = line[i]
			var j := Vector2(_hash(p.x, p.y) - 0.5, _hash(p.y + 31, p.x + 17) - 0.5) * 0.22
			pts.append(Vector2(p) + j)
		out.append(pts)
	return out


func _hash(x: int, y: int) -> float:
	var n := (x * 374761393 + y * 668265263) & 0x7fffffff
	n = ((n ^ (n >> 13)) * 1274126177) & 0x7fffffff
	return float(n % 10007) / 10007.0


func _draw() -> void:
	var lv: Level = Game.level
	if lv == null or lv.player == null:
		return
	var now := Time.get_ticks_msec()
	if lv != _level or (lv.explored_rev != _rev and now - _rebuilt_at > 250):
		_rebuilt_at = now
		_rebuild(lv)
	var o := origin()
	var mid := size / 2.0
	var r2 := (radius + zoom * 2) * (radius + zoom * 2)
	var cs := Vector2(zoom, zoom) + Vector2(0.6, 0.6)
	var ground: Texture2D = _tex.map_floor_town if lv.is_town else _tex.map_floor
	for list in [[_floor, ground, 0.85], [_path, _tex.map_floor, 0.7], [_water, _tex.map_water, 0.9]]:
		var t: Texture2D = list[1]
		if t == null:
			continue
		var mod := Color(1, 1, 1, list[2])
		for c in list[0]:
			var p: Vector2 = o + Vector2(c) * zoom
			if radius > 0.0 and (p - mid).length_squared() > r2:
				continue
			var src := Rect2(posmod(c.x * 16, 256), posmod(c.y * 16, 256), 16, 16)
			draw_texture_rect_region(t, Rect2(p, cs), src, mod)
	var lw := clampf(zoom * 0.14, 1.0, 2.2)
	for hs in _hatch:
		var a: Vector2 = o + hs[0] * zoom
		if radius > 0.0 and (a - mid).length_squared() > r2:
			continue
		draw_line(a, o + hs[1] * zoom, GRAPHITE_SOFT, lw * 0.6, true)
	for pl in _walls:
		var pts := PackedVector2Array()
		for q in pl:
			pts.append(o + q * zoom)
		if radius > 0.0:
			var near := false
			for q in pts:
				if (q - mid).length_squared() < r2:
					near = true
					break
			if not near:
				continue
		draw_polyline(pts, GRAPHITE, lw, true)
		var soft := PackedVector2Array()
		for q in pts:
			soft.append(q + Vector2(0.7, 0.9))
		draw_polyline(soft, GRAPHITE_SOFT, lw * 0.7, true)
	if lv.is_town:
		_draw_town_props(lv, o, mid, lw)
	for pr in lv.props:
		if not is_instance_valid(pr) or not ICON.has(pr.interact):
			continue
		if pr.interact == "shrine" and pr.used:
			continue
		if pr.interact == "book" and Game.known.has("book:" + str(pr.data.get("book", ""))):
			continue
		var c := Vector2i(pr.position / Level.CELL)
		if lv.explored[clampi(c.y, 0, lv.h - 1) * lv.w + clampi(c.x, 0, lv.w - 1)] == 1:
			_icon(ICON[pr.interact], o + pr.position / Level.CELL * zoom, mid)
	if lv.boss and is_instance_valid(lv.boss) and not lv.boss.dead:
		var bc := lv.to_cell(lv.boss.global_position)
		if lv.explored[clampi(bc.y, 0, lv.h - 1) * lv.w + clampi(bc.x, 0, lv.w - 1)] == 1:
			_icon("map_boss", o + lv.boss.global_position / Level.CELL * zoom, mid)
	for n in lv.npcs:
		var mk := Game.npc_marker(n.npc_id)
		if mk != "":
			_icon("quest_" + mk, o + n.position / Level.CELL * zoom + Vector2(0, -icon_px * 0.3), mid, 1.1)
		else:
			_icon("map_npc", o + n.position / Level.CELL * zoom, mid)
	_icon("map_hero", o + lv.player.global_position / Level.CELL * zoom, mid, 1.15)
	_draw_objectives(lv, o, mid)


const GOAL := Color(0.95, 0.72, 0.2)
const GOAL_SIDE := Color(0.82, 0.86, 0.9)


# The tracked quests' targets, seen or not; on the round map a target off the disc becomes an arrow on its rim.
func _draw_objectives(lv: Level, o: Vector2, mid: Vector2) -> void:
	var pulse := 0.75 + 0.25 * sin(Time.get_ticks_msec() / 260.0)
	var obs := lv.objective_points()
	obs.sort_custom(func(a, b): return not a.main and b.main)
	for ob in obs:
		var col: Color = GOAL if ob.main else GOAL_SIDE
		var p: Vector2 = o + ob.pos / Level.CELL * zoom
		if radius > 0.0 and (p - mid).length() > radius - 14.0:
			var dir: Vector2 = (p - mid).normalized()
			var tip := mid + dir * (radius - 6.0)
			var side := dir.orthogonal() * 10.0
			var tri := PackedVector2Array([tip, tip - dir * 20.0 + side, tip - dir * 20.0 - side])
			draw_colored_polygon(tri, Color(col, pulse))
			draw_polyline(PackedVector2Array([tri[0], tri[1], tri[2], tri[0]]), GRAPHITE, 1.4, true)
			continue
		draw_arc(p, icon_px * 0.55 * (0.9 + 0.2 * pulse), 0.0, TAU, 24, Color(col, 0.9 * pulse), 2.2, true)
		_icon("map_quest", p, mid, 0.8)


const ROOF := Color(0.55, 0.3, 0.22, 0.85)
const LEAF := Color(0.24, 0.36, 0.2, 0.75)


# Houses as pencilled roofs over their footprint, trees as little crayon blobs.
func _draw_town_props(lv: Level, o: Vector2, mid: Vector2, lw: float) -> void:
	for pr in lv.props:
		if not is_instance_valid(pr) or not pr.def.get("blocks", true):
			continue
		var c: Vector2i = pr.cell
		if lv.explored[clampi(c.y, 0, lv.h - 1) * lv.w + clampi(c.x, 0, lv.w - 1)] == 0:
			continue
		var fp = pr.def.get("footprint", [1, 1])
		var fw := int(fp[0])
		var fh := int(fp[1])
		if fw * fh >= 4:
			var r := Rect2(o + Vector2(c.x - fw / 2, c.y - fh + 1) * zoom, Vector2(fw, fh) * zoom)
			if radius > 0.0 and (r.get_center() - mid).length() > radius:
				continue
			draw_rect(r, ROOF)
			for k in range(1, fw * 2):
				var x := r.position.x + r.size.x * k / (fw * 2.0)
				draw_line(Vector2(x, r.position.y), Vector2(x - zoom * 0.3, r.end.y), GRAPHITE_SOFT, lw * 0.5, true)
			draw_line(Vector2(r.position.x, r.get_center().y), Vector2(r.end.x, r.get_center().y), GRAPHITE, lw * 0.8, true)
			draw_polyline(PackedVector2Array([r.position, Vector2(r.end.x, r.position.y), r.end, Vector2(r.position.x, r.end.y), r.position]), GRAPHITE, lw, true)
		elif pr.interact == "":
			var p := o + (Vector2(c) + Vector2(0.5, 0.5)) * zoom
			if radius > 0.0 and (p - mid).length() > radius:
				continue
			var rr := zoom * (0.42 + _hash(c.x, c.y) * 0.15)
			draw_circle(p, rr, LEAF)
			draw_arc(p, rr, 0.0, TAU, 14, GRAPHITE_SOFT, lw * 0.7, true)


func _icon(key: String, p: Vector2, mid: Vector2, k := 1.0) -> void:
	if radius > 0.0 and (p - mid).length() > radius - icon_px * 0.3:
		return
	var t: Texture2D = _tex.get(key)
	var s := icon_px * k
	if t:
		draw_texture_rect(t, Rect2(p - Vector2(s, s) / 2.0, Vector2(s, s)), false)
	else:
		draw_circle(p, s * 0.25, Color("ff4a3a"))
