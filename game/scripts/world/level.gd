class_name Level
extends Node2D

const CELL := 64
const SLEEP_PX := 1700.0
const SHADOW_MASK := 4
const DARK := {1: Color(0.15, 0.135, 0.15), 2: Color(0.12, 0.145, 0.13), 3: Color(0.16, 0.13, 0.115), 4: Color(0.12, 0.11, 0.17)}
const TOWN_DUSK := {1: Color(0.42, 0.4, 0.52), 2: Color(0.38, 0.42, 0.46), 3: Color(0.4, 0.36, 0.42), 4: Color(0.22, 0.22, 0.34)}

var act_n := 1
var floor_n := 0
var is_town := false
var def := {}
var gen: DungeonGen
var w := 0
var h := 0
var solid := PackedByteArray()
var water := PackedByteArray()
var explored := PackedByteArray()
var explored_rev := 0
var fog: Sprite2D
var fog_img: Image
var fog_dirty := false
var astar := AStarGrid2D.new()
var floor_layer: TileMapLayer
var deco_layer: TileMapLayer
var water_layer: TileMapLayer
var path_layer: TileMapLayer
var wall_layer: TileMapLayer
var ysort: Node2D
var items_root: Node2D
var fx_root: Node2D
var text_root: Node2D
var player: Player
var hireling: Hireling
var monsters: Array = []
var npcs: Array = []
var props: Array = []
var ground_items: Array = []
var hover_obj = null
var shake_amt := 0.0
var explore_t := 0.0
var arrive_points := {}
var portal_node: PropNode
var boss: Monster
var font: Font
var tileset_name := ""
var used_cells := {}
var placed := {}
var floor_seed := 0


func build(a: int, f: int, arrive: String) -> void:
	act_n = a
	floor_n = f
	is_town = f == 0
	font = load("res://assets/fonts/TataHand.ttf")
	var ad := DB.act(a)
	if is_town:
		tileset_name = str(ad.get("town", {}).get("tileset", "town_hora"))
		floor_seed = hash("town:%d:%d:%d" % [Game.difficulty, a, Game.session_seed])
		gen = TownLayout.make(a, floor_seed)
	else:
		def = DB.floor_def(a, f)
		tileset_name = str(ad.get("dungeon", {}).get("tileset", "hora"))
		gen = DungeonGen.new()
		floor_seed = hash("%d:%d:%d:%d" % [Game.difficulty, a, f, Game.session_seed])
		gen.generate(def, floor_seed)
	w = gen.w
	h = gen.h
	solid = PackedByteArray()
	solid.resize(w * h)
	water = PackedByteArray()
	water.resize(w * h)
	explored = PackedByteArray()
	explored.resize(w * h)
	for y in h:
		for x in w:
			var v := gen.at(x, y)
			solid[y * w + x] = 1 if v == DungeonGen.WALL else 0
			water[y * w + x] = 1 if v == DungeonGen.WATER else 0
	_make_layers()
	_paint_tiles()
	if not is_town:
		_make_wall_shade()
	var cm := CanvasModulate.new()
	cm.color = TOWN_DUSK.get(a, Color(0.4, 0.4, 0.5)) if is_town else DARK.get(a, Color(0.15, 0.135, 0.15)).darkened(f * 0.03)
	add_child(cm)
	if not is_town:
		_make_fog()
	# Seeded, so a floor visited again this session gets the same props and packs back.
	seed(floor_seed)
	if is_town:
		_populate_town()
	else:
		_populate_dungeon()
	randomize()
	for i in monsters.size():
		monsters[i].set_meta("spawn_i", i)
	_build_collision()
	_build_astar()
	_restore_state()
	_spawn_player(arrive)
	spawn_hireling()
	_restore_loot()
	var music := str(ad.get("town", {}).get("music", "town_hora")) if is_town else str(ad.get("dungeon", {}).get("music", "mine_%d" % a))
	if def.get("boss", null) != null and not is_town:
		music = music
	Sfx.music(music)


func _make_layers() -> void:
	var ts := _make_tileset()
	floor_layer = TileMapLayer.new()
	floor_layer.tile_set = ts
	floor_layer.z_index = -20
	add_child(floor_layer)
	water_layer = TileMapLayer.new()
	water_layer.tile_set = ts
	water_layer.z_index = -19
	add_child(water_layer)
	path_layer = TileMapLayer.new()
	path_layer.tile_set = ts
	path_layer.z_index = -19
	add_child(path_layer)
	deco_layer = TileMapLayer.new()
	deco_layer.tile_set = ts
	deco_layer.z_index = -18
	add_child(deco_layer)
	items_root = Node2D.new()
	items_root.z_index = -5
	add_child(items_root)
	ysort = Node2D.new()
	ysort.y_sort_enabled = true
	add_child(ysort)
	wall_layer = TileMapLayer.new()
	wall_layer.tile_set = ts
	wall_layer.y_sort_enabled = true
	ysort.add_child(wall_layer)
	for tl in [floor_layer, water_layer, path_layer, deco_layer, wall_layer]:
		tl.light_mask = 1 | SHADOW_MASK
	fx_root = Node2D.new()
	fx_root.z_index = 10
	add_child(fx_root)
	text_root = Node2D.new()
	text_root.z_index = 40
	add_child(text_root)


func _tile_tex(path: String, size: Vector2i, col: Color) -> Texture2D:
	var t := DB.tex(path)
	if t:
		return t
	var img := Image.create(size.x, size.y, false, Image.FORMAT_RGBA8)
	img.fill(col)
	if size.y > 64:
		img.fill_rect(Rect2i(0, 64, size.x, size.y - 64), col.lightened(0.25))
	for i in 40:
		img.set_pixel(randi() % size.x, randi() % size.y, col.darkened(0.3))
	return ImageTexture.create_from_image(img)


func _add_src(ts: TileSet, sid: int, t: Texture2D, size: Vector2i, origin: Vector2i) -> void:
	var src := TileSetAtlasSource.new()
	src.texture = t
	src.texture_region_size = size
	src.create_tile(Vector2i.ZERO)
	ts.add_source(src, sid)
	var td := src.get_tile_data(Vector2i.ZERO, 0)
	td.texture_origin = origin


# All variants of a layer share one texture, so the layer draws in a few batches instead of one per cell.
# Tiles sit PAD px apart with their edge pixels smeared into the gap against filtering bleed.
const PAD := 4


# entries: [texture, texture_origin]; tile i lands at atlas coords (i, 0), as tall as its texture.
func _atlas_src(ts: TileSet, sid: int, entries: Array, region: Vector2i) -> void:
	var hmax := 0
	for e in entries:
		hmax = maxi(hmax, e[0].get_height())
	var img := Image.create(entries.size() * (region.x + PAD), hmax, false, Image.FORMAT_RGBA8)
	for i in entries.size():
		var tile: Image = entries[i][0].get_image()
		if tile.is_compressed():
			tile.decompress()
		tile.convert(Image.FORMAT_RGBA8)
		var r := Rect2i(0, 0, region.x, tile.get_height())
		var x := i * (region.x + PAD)
		for dx in [-PAD / 2, PAD / 2]:
			img.blit_rect(tile, r, Vector2i(x + dx, 0))
		if tile.get_height() < hmax:
			img.blit_rect(tile, Rect2i(0, tile.get_height() - 1, region.x, 1), Vector2i(x, tile.get_height()))
		img.blit_rect(tile, r, Vector2i(x, 0))
	var src := TileSetAtlasSource.new()
	src.texture = ImageTexture.create_from_image(img)
	src.texture_region_size = region
	src.separation = Vector2i(PAD, 0)
	ts.add_source(src, sid)
	for i in entries.size():
		var at := Vector2i(i, 0)
		src.create_tile(at, Vector2i(1, maxi(1, entries[i][0].get_height() / region.y)))
		src.get_tile_data(at, 0).texture_origin = entries[i][1]


func _make_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(CELL, CELL)
	var base := Color("4a4038") if not is_town else Color("6a6450")
	var floors := []
	for i in 4:
		floors.append([_tile_tex("tiles/%s/floor_%d" % [tileset_name, i], Vector2i(64, 64), base), Vector2i.ZERO])
	_atlas_src(ts, 0, floors, Vector2i(64, 64))
	var walls := []
	var tops := []
	for i in 3:
		var wt := _tile_tex("tiles/%s/wall_%d" % [tileset_name, i], Vector2i(64, 96), base.darkened(0.3))
		walls.append([wt, Vector2i(0, 16)])
		# the same rock without its front face, for rock that has more rock (or nothing) below it
		tops.append([ImageTexture.create_from_image(wt.get_image().get_region(Rect2i(0, 0, 64, 64))), Vector2i(0, 32)])
	_atlas_src(ts, 10, walls + tops, Vector2i(64, 32))
	var decos := []
	for i in 4:
		var t := DB.tex("tiles/%s/floor_deco_%d" % [tileset_name, i])
		if t:
			decos.append([t, Vector2i.ZERO])
	if not decos.is_empty():
		_atlas_src(ts, 20, decos, Vector2i(64, 64))
	_add_src(ts, 30, _water_tex(), Vector2i(64, 64), Vector2i.ZERO)
	var paths := []
	for i in 3:
		var t := DB.tex("tiles/%s/path_%d" % [tileset_name, i])
		if t:
			paths.append([t, Vector2i.ZERO])
	if not paths.is_empty():
		_atlas_src(ts, 40, paths, Vector2i(128, 128))
	return ts


func _water_tex() -> Texture2D:
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	var c := Color(0.12, 0.22, 0.26, 0.72) if act_n != 3 else Color(0.18, 0.3, 0.12, 0.72)
	for y in 64:
		for x in 64:
			var r := sin((x + y * 0.5) * 0.25) * 0.5 + sin((x * 0.6 - y) * 0.31) * 0.5
			img.set_pixel(x, y, c.lightened(0.08 * maxf(0.0, r)))
	return ImageTexture.create_from_image(img)


func _paint_tiles() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(tileset_name) + floor_n
	var has_deco := floor_layer.tile_set.has_source(20)
	var has_path := is_town and floor_layer.tile_set.has_source(40)
	var decos_n := (floor_layer.tile_set.get_source(20) as TileSetAtlasSource).get_tiles_count() if has_deco else 0
	var paths_n := (floor_layer.tile_set.get_source(40) as TileSetAtlasSource).get_tiles_count() if has_path else 0
	var noise := FastNoiseLite.new()
	noise.seed = rng.seed
	noise.frequency = 0.09
	var patches := PackedVector2Array()
	for y in h:
		for x in w:
			var c := Vector2i(x, y)
			if solid[y * w + x] == 0:
				var nv := noise.get_noise_2d(x, y)
				floor_layer.set_cell(c, 0, Vector2i(rng.randi_range(0, 3) if rng.randf() < 0.45 else 0, 0))
				if water[y * w + x] == 1:
					water_layer.set_cell(c, 30, Vector2i.ZERO)
				elif has_path and (gen as TownLayout).paths.has(c):
					path_layer.set_cell(c, 40, Vector2i(rng.randi_range(0, paths_n - 1), 0))
				elif has_deco and rng.randf() < (0.14 if nv > 0.3 else 0.03):
					deco_layer.set_cell(c, 20, Vector2i(rng.randi_range(0, decos_n - 1), 0))
				if is_town and nv > 0.12 and not (has_path and (gen as TownLayout).paths.has(c)):
					patches.append(Vector2(x * CELL + rng.randf_range(0, CELL), y * CELL + rng.randf_range(0, CELL)))
			else:
				var v := rng.randi_range(0, 2) if rng.randf() < 0.4 else 0
				var face := y + 1 < h and gen.at(x, y + 1) != DungeonGen.WALL
				wall_layer.set_cell(c, 10, Vector2i(v + (0 if face else 3), 0))

	if not patches.is_empty():
		var n := Node2D.new()
		n.z_index = -20
		var tex := Fx.soft()
		var cols := [Color(0.24, 0.32, 0.12, 0.4), Color(0.3, 0.36, 0.16, 0.32), Color(0.18, 0.24, 0.1, 0.35)]
		n.draw.connect(func():
			for i in patches.size():
				var r := 46.0 + float(i * 37 % 30)
				n.draw_texture_rect(tex, Rect2(patches[i] - Vector2(r, r * 0.7), Vector2(r * 2.0, r * 1.4)), false, cols[i % 3]))
		add_child(n)


func _near_floor(x: int, y: int, r: int) -> bool:
	for oy in range(-r, r + 1):
		for ox in range(-r, r + 1):
			var xx := x + ox
			var yy := y + oy
			if xx >= 0 and yy >= 0 and xx < w and yy < h and solid[yy * w + xx] == 0:
				return true
	return false


func _build_collision() -> void:
	var body := StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 0
	add_child(body)
	var occ_root := Node2D.new()
	add_child(occ_root)
	for y in h:
		var x := 0
		while x < w:
			if _rock(x, y) and _near_open(x, y):
				var x0 := x
				while x < w and _rock(x, y) and _near_open(x, y):
					x += 1
				var cs := CollisionShape2D.new()
				var rs := RectangleShape2D.new()
				rs.size = Vector2((x - x0) * CELL, CELL)
				cs.shape = rs
				cs.position = Vector2((x0 + x) * CELL / 2.0, y * CELL + CELL / 2.0)
				body.add_child(cs)
				if gen.at(x0, y) == DungeonGen.WALL:
					var oc := LightOccluder2D.new()
					var op := OccluderPolygon2D.new()
					var x1 := float(x * CELL)
					op.polygon = PackedVector2Array([Vector2(x0 * CELL, y * CELL), Vector2(x1, y * CELL), Vector2(x1, y * CELL + 30), Vector2(x0 * CELL, y * CELL + 30)])
					oc.occluder = op
					occ_root.add_child(oc)
			else:
				x += 1


func _rock(x: int, y: int) -> bool:
	return gen.at(x, y) == DungeonGen.WALL


func _near_open(x: int, y: int) -> bool:
	for oy in range(-1, 2):
		for ox in range(-1, 2):
			if not _rock(x + ox, y + oy) and x + ox >= 0 and y + oy >= 0 and x + ox < w and y + oy < h:
				return true
	return false


func _build_astar() -> void:
	astar.region = Rect2i(0, 0, w, h)
	astar.cell_size = Vector2(CELL, CELL)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	astar.update()
	for y in h:
		for x in w:
			if solid[y * w + x] == 1:
				astar.set_point_solid(Vector2i(x, y), true)


func block_cells(c0: Vector2i, size: Vector2i) -> void:
	for y in range(c0.y, c0.y + size.y):
		for x in range(c0.x, c0.x + size.x):
			if x >= 0 and y >= 0 and x < w and y < h:
				solid[y * w + x] = 1


# ---------------------------------------------------------------- queries
func to_cell(p: Vector2) -> Vector2i:
	return Vector2i(floori(p.x / CELL), floori(p.y / CELL))


func cell_center(c: Vector2i) -> Vector2:
	return Vector2(c.x * CELL + CELL / 2.0, c.y * CELL + CELL / 2.0)


func is_solid_cell(c: Vector2i) -> bool:
	if c.x < 0 or c.y < 0 or c.x >= w or c.y >= h:
		return true
	return solid[c.y * w + c.x] == 1


func is_solid(p: Vector2) -> bool:
	return is_solid_cell(to_cell(p))


func is_water(p: Vector2) -> bool:
	var c := to_cell(p)
	if c.x < 0 or c.y < 0 or c.x >= w or c.y >= h:
		return false
	return water[c.y * w + c.x] == 1


func line_of_sight(a: Vector2, b: Vector2) -> bool:
	var d := a.distance_to(b)
	var n := int(d / 20.0)
	for i in range(1, n):
		if is_solid(a.lerp(b, float(i) / n)):
			return false
	return true


func lit(p: Vector2) -> bool:
	if is_town:
		return true
	return player != null and player.global_position.distance_to(p) < player.light_radius_px()


func _nearest_open(c: Vector2i) -> Vector2i:
	c = Vector2i(clampi(c.x, 0, w - 1), clampi(c.y, 0, h - 1))
	if not is_solid_cell(c):
		return c
	for r in range(1, 6):
		for oy in range(-r, r + 1):
			for ox in range(-r, r + 1):
				var n := c + Vector2i(ox, oy)
				if not is_solid_cell(n):
					return n
	return c


func find_path(from: Vector2, to: Vector2) -> Array:
	var a := _nearest_open(to_cell(from))
	var b := _nearest_open(to_cell(to))
	if a == b:
		return [to] if not is_solid(to) else [cell_center(b)]
	var ids := astar.get_id_path(a, b)
	if ids.is_empty():
		return []
	var pts: Array = []
	for i in range(1, ids.size()):
		pts.append(cell_center(ids[i]))
	if not is_solid(to) and pts.size() > 0:
		pts[pts.size() - 1] = to
	var out: Array = []
	var cur := from
	var i := 0
	while i < pts.size():
		var j := mini(pts.size() - 1, i + 14)
		while j > i and not _clear_wide(cur, pts[j]):
			j -= 1
		out.append(pts[j])
		cur = pts[j]
		i = j + 1
	return out


# A shortcut must leave room for a body (radius 15) plus a margin, checked finely enough not to skip a corner.
func _clear_wide(a: Vector2, b: Vector2) -> bool:
	var perp := (b - a).normalized().orthogonal() * 21.0
	var n := int(a.distance_to(b) / 10.0)
	for i in range(1, n + 1):
		var p := a.lerp(b, float(i) / n)
		if is_solid(p + perp) or is_solid(p - perp) or is_solid(p):
			return false
	return true


func random_open_near(p: Vector2, rmin: float, rmax: float) -> Vector2:
	for i in 20:
		var q := p + Vector2.RIGHT.rotated(randf() * TAU) * randf_range(rmin, rmax)
		var c := to_cell(q)
		if not is_solid_cell(c) and line_of_sight(p, q):
			return q
	return Vector2.INF


func clamp_walkable(from: Vector2, to: Vector2, maxd: float) -> Vector2:
	var dir := to - from
	if dir.length() > maxd:
		to = from + dir.normalized() * maxd
	var n := int(from.distance_to(to) / 16.0)
	var last := from
	for i in range(1, n + 1):
		var q := from.lerp(to, float(i) / maxf(1, n))
		if is_solid(q):
			break
		last = q
	return last


func actors_of_team(team: int) -> Array:
	if team == 0:
		var out := [player] if player and not player.dead else []
		if hireling and is_instance_valid(hireling) and not hireling.dead:
			out.append(hireling)
		return out
	return monsters


# ---------------------------------------------------------------- population
func _place_prop(id: String, c: Vector2i, block := true) -> PropNode:
	var p := PropNode.create(id, cell_center(c) + Vector2(0, CELL / 2.0 - 10), not id.begins_with("permonik"))
	p.cell = c
	ysort.add_child(p)
	props.append(p)
	var fp = p.def.get("footprint", [1, 1])
	var blocks := bool(p.def.get("blocks", true)) and block
	if blocks and int(fp[0]) > 0 and int(fp[1]) > 0:
		var fw := int(fp[0])
		var fh := int(fp[1])
		var c0 := Vector2i(c.x - fw / 2, c.y - fh + 1)
		block_cells(c0, Vector2i(fw, fh))
		var body := StaticBody2D.new()
		body.name = "Body"
		body.collision_layer = 1
		body.collision_mask = 0
		var cs := CollisionShape2D.new()
		var rs := RectangleShape2D.new()
		rs.size = Vector2(fw, fh) * CELL
		cs.shape = rs
		body.add_child(cs)
		body.position = Vector2(c0) * CELL + rs.size / 2.0 - p.position
		p.add_child(body)
		p.set_meta("cells", [c0, Vector2i(fw, fh)])
		if astar.region.size.x > 0:
			for yy in range(c0.y, c0.y + fh):
				for xx in range(c0.x, c0.x + fw):
					if xx >= 0 and yy >= 0 and xx < w and yy < h:
						astar.set_point_solid(Vector2i(xx, yy), true)
	return p


func _free_cells(min_from_start := 6, spacing := 2) -> Array:
	var out := []
	for y in range(1, h - 1):
		for x in range(1, w - 1):
			var c := Vector2i(x, y)
			if gen.at(x, y) == DungeonGen.FLOOR and solid[y * w + x] == 0 and (c - gen.start).length() >= min_from_start:
				out.append(c)
	out.shuffle()
	return out


func _cell_free_area(c: Vector2i, r := 1) -> bool:
	for oy in range(-r, r + 1):
		for ox in range(-r, r + 1):
			if is_solid_cell(c + Vector2i(ox, oy)):
				return false
	return true


func _populate_dungeon() -> void:
	var rng := RandomNumberGenerator.new()
	rng.seed = floor_seed
	var up := _place_prop("schody_nahoru", gen.start + Vector2i(0, -1) if _cell_free_area(gen.start + Vector2i(0, -1), 0) else gen.start, false)
	up.interact = "stairs_up"
	arrive_points["stairs_down"] = cell_center(gen.start) + Vector2(0, 40)
	arrive_points["start"] = arrive_points.stairs_down
	var wp_c := _find_free_near(gen.start, 2, 4)
	var wp := _place_prop("klec", wp_c)
	wp.interact = "waypoint"
	arrive_points["waypoint"] = cell_center(wp_c) + Vector2(0, 70)
	arrive_points["portal"] = cell_center(_find_free_near(gen.start, 1, 3))
	if floor_n < DB.floor_count(act_n):
		var dn := _place_prop("schody_dolu", gen.exit, false)
		dn.interact = "stairs_down"
		arrive_points["stairs_up"] = cell_center(gen.exit) + Vector2(0, 60)
	else:
		arrive_points["stairs_up"] = arrive_points.start
	var free := _free_cells(5)
	var area := free.size()
	used_cells.clear()
	var used := used_cells
	placed.clear()
	_place_quest_props()
	_place_books()
	var n_break := int(area * 0.025)
	var n_chest := 2 + int(area / 600)
	var n_shrine := 1 + (1 if rng.randf() < 0.5 else 0)
	var n_lamp := int(area / 110)
	var n_deco := int(area * 0.02)
	var wall_spots := gen.wall_adjacent_floor()
	wall_spots.shuffle()
	for i in mini(n_lamp, wall_spots.size()):
		var c: Vector2i = wall_spots[i]
		if (c - gen.start).length() > 3:
			var p := _place_prop("kahan_nastenny", c, false)
			p.position.y -= 34
	var idx := 0
	var take := func() -> Vector2i:
		while idx < free.size():
			var c: Vector2i = free[idx]
			idx += 1
			if not used.has(c) and _cell_free_area(c, 1):
				used[c] = true
				return c
		return Vector2i(-1, -1)
	for i in n_break:
		var c: Vector2i = take.call()
		if c.x < 0:
			break
		var id := "urna" if act_n >= 3 and rng.randf() < 0.5 else ("urna" if rng.randf() < 0.3 else "sud")
		var p := _place_prop(id, c)
		p.interact = "break"
	for i in n_chest:
		var c := _rule_cell({"far": 0.2, "spacing": 8, "group": "chest", "side": true})
		if c.x < 0:
			break
		used[c] = true
		_place_prop("truhla", c).interact = "chest"
	var gods := DB.shrines.keys()
	gods.shuffle()
	for i in mini(n_shrine, gods.size()):
		var c := _rule_cell({"far": 0.15, "spacing": 12, "from_boss": 10, "min_start": 8, "group": "shrine", "side": true})
		if c.x < 0:
			break
		used[c] = true
		var g: String = gods[i]
		var p := _place_prop(str(DB.shrines[g].get("prop", "modla_" + g)), c)
		p.interact = "shrine"
		p.data["shrine"] = g
	var deco_ids := ["kosti", "kamen", "ruda", "lebky", "podpera", "vozik"]
	match act_n:
		2:
			deco_ids += ["koren", "houby", "koren"]
		3:
			deco_ids += ["smolinec", "kovadlina", "smolinec"]
		4:
			deco_ids += ["navi_svice", "lebky", "kosti"]
	for i in n_deco:
		var c: Vector2i = take.call()
		if c.x < 0:
			break
		var id: String = deco_ids.pick_random()
		_place_prop(id, c, DB.prop(id).get("blocks", false))
	_spawn_monsters(rng, used)


func _find_free_near(c: Vector2i, rmin: int, rmax: int) -> Vector2i:
	for r in range(rmin, rmax + 3):
		for oy in range(-r, r + 1):
			for ox in range(-r, r + 1):
				var n := c + Vector2i(ox, oy)
				if _cell_free_area(n, 1) and n != gen.start and n != gen.exit:
					return n
	return c


# Each book has one home (books.json "where"); dungeon copies sit in an open spot away from the stairs,
# town copies on a lectern next to the chronicler.
func _place_books() -> void:
	var here := str(DB.act(act_n).get("town", {}).get("id", "")) if is_town else "act%d_floor%d" % [act_n, floor_n]
	var n := 0
	for bid in DB.books:
		if str(DB.books[bid].get("where", "")) != here:
			continue
		var c := Vector2i(-1, -1)
		if is_town:
			var tp: Dictionary = (gen as TownLayout).points
			var lec: Vector2i = tp.get("lectern", tp.get("center", Vector2i(w / 2, h / 2)))
			c = _find_free_near(lec + Vector2i(-n * 2, 0), 0, 3)
		else:
			c = _rule_cell({"far": 0.3, "from_boss": 9, "spacing": 10, "group": "book"})
		if c.x < 0:
			continue
		var p := _place_prop("kniha", c)
		p.interact = "book"
		p.data["book"] = bid
		n += 1


# Where a placement may go. far = share of the longest walk from the stairs; from_boss = cells from the
# boss's room; spacing = cells from earlier placements of the same group; next_to = a placed id.
# Where the tracked quests point on this map: the target itself when it is here, else the way towards it.
func objective_points() -> Array:
	var out := []
	for tq in Game.tracked_quests():
		if not Game.quest_on_map(tq.qid):
			continue
		var pl := Game.goal_place(tq.qid)
		if pl.is_empty() or int(pl.act) != act_n:
			continue
		var floors: Array = pl.floors
		var here := floor_n in floors
		var pts := []
		if here:
			match str(pl.what):
				"boss":
					if boss and is_instance_valid(boss) and not boss.dead:
						pts.append(boss.global_position)
				"npc":
					for n in npcs:
						if n.npc_id == pl.id:
							pts.append(n.global_position)
				"prop":
					for pr in props:
						if is_instance_valid(pr) and pr.id == pl.id and pr.visible and not pr.used:
							pts.append(pr.global_position)
				"item":
					for g in ground_items:
						if is_instance_valid(g) and g.item.base_id == pl.id:
							pts.append(g.global_position)
		elif not floors.is_empty():
			var down := int(floors.min()) > floor_n
			for pr in props:
				if is_instance_valid(pr) and pr.interact == ("stairs_down" if down else "stairs_up"):
					pts.append(pr.global_position)
		for p in pts:
			# below ground a target shows once its spot has been seen; finding it is the point
			var c := to_cell(p)
			if not is_town and explored[clampi(c.y, 0, h - 1) * w + clampi(c.x, 0, w - 1)] == 0:
				continue
			out.append({"pos": p, "main": tq.main})
	return out


func _rule_cell(rule: Dictionary) -> Vector2i:
	var cands: Array = []
	if rule.has("next_to") and placed.has(str(rule.next_to)):
		var anchor: Vector2i = placed[str(rule.next_to)][0]
		for r in range(2, 5):
			for oy in range(-r, r + 1):
				for ox in range(-r, r + 1):
					cands.append(anchor + Vector2i(ox, oy))
	else:
		cands = gen.dist.keys()
		cands.shuffle()
		# rewards for whoever looks round the corner: side-room cells are tried first
		if rule.get("side", false) and not gen.side_rooms.is_empty():
			var side := []
			for c in cands:
				for r in gen.side_rooms:
					if r.has_point(c):
						side.append(c)
						break
			cands = side + cands
	var far := float(rule.get("far", 0.0)) * gen.max_dist
	var from_boss := float(rule.get("from_boss", 0.0)) if gen.boss_spot.x >= 0 else 0.0
	var spacing := float(rule.get("spacing", 0.0))
	var group := str(rule.get("group", ""))
	var others: Array = placed.get(group, []) if group != "" else []
	for c in cands:
		if not gen.dist.has(c) or gen.dist[c] < far or used_cells.has(c) or gen.at(c.x, c.y) != DungeonGen.FLOOR:
			continue
		if not _cell_free_area(c, 1) or (c - gen.start).length() < float(rule.get("min_start", 5)) or (c - gen.exit).length() < 3:
			continue
		if from_boss > 0.0 and (c - gen.boss_spot).length() < from_boss:
			continue
		var ok := true
		for o in others:
			if (c - o).length() < spacing:
				ok = false
				break
		if not ok:
			continue
		used_cells[c] = true
		if group != "":
			if not placed.has(group):
				placed[group] = []
			placed[group].append(c)
		return c
	return Vector2i(-1, -1)


# Story placements first, so nothing random can take their spot. Defaults: items to carry far from the
# stairs, props a boss fights with in a ring round its room, anything else past the middle of the floor.
func _quest_rule(qid: String) -> Dictionary:
	var custom: Dictionary = def.get("rules", {}).get("place", {})
	if custom.has(qid):
		return custom[qid]
	if DB.items.has(qid) and not DB.props.has(qid):
		return {"far": 0.5, "from_boss": 9}
	if gen.boss_spot.x >= 0:
		return {"near": "boss"}
	return {"far": 0.45}


func _place_quest_props() -> void:
	for q in def.get("quest_props", []):
		var qid := str(q)
		var rule := _quest_rule(qid)
		rule["group"] = qid
		if DB.items.has(qid) and not DB.props.has(qid):
			var ic := _rule_cell(rule)
			if ic.x < 0:
				ic = _rule_cell({"group": qid})
			var qi := Item.create(qid, 1)
			if ic.x >= 0 and Game.quest_item_wanted(qid, act_n, floor_n):
				drop_item(qi, cell_center(ic))
				ground_items.back().set_meta("quest_spawn", true)
			continue
		var n := 1
		match qid:
			"hrnek_dusicka":
				n = 6
			"zrcadlo":
				n = 4
			"kbelik":
				n = 4
		var ring0 := randf() * TAU
		for i in n:
			var c := Vector2i(-1, -1)
			if str(rule.get("near", "")) == "boss":
				var a := ring0 + TAU * i / n
				c = _find_free_near(gen.boss_spot + Vector2i(int(cos(a) * 6), int(sin(a) * 4)), 0, 3)
				used_cells[c] = true
				if not placed.has(qid):
					placed[qid] = []
				placed[qid].append(c)
			else:
				c = _rule_cell(rule)
				if c.x < 0:
					c = _rule_cell({"group": qid, "next_to": rule.get("next_to", "")} if rule.has("next_to") else {"group": qid})
			if c.x < 0:
				break
			var p := _place_prop(qid, c, qid in ["dub", "zrcadlo"])
			p.interact = "quest"


# Each visit draws its own mix from the floor's pool, so the same floor is not always the same fight.
func _spawn_monsters(rng: RandomNumberGenerator, used: Dictionary) -> void:
	var pool: Array = def.get("monsters", [])
	pool = pool.filter(func(m): return DB.monsters.has(m))
	pool.shuffle()
	var mix: Array = pool.slice(0, maxi(2, pool.size() - 1))
	var base_l := Game.mlvl_base(int(def.get("level", 1)))
	if not pool.is_empty():
		var area := gen.dist.size()
		var packs := int(area / 85.0 * float(def.get("density", 1.0)) * rng.randf_range(0.85, 1.15))
		var champs := 1 + (1 if floor_n > 1 else 0) + Game.difficulty
		for i in packs:
			# champions guard the side rooms, where the chests wait
			var c := _rule_cell({"spacing": 6, "from_boss": 10, "min_start": 9, "group": "pack", "side": i < champs})
			if c.x < 0:
				break
			var mid: String = (mix if rng.randf() < 0.85 else pool).pick_random()
			var pk = DB.monster(mid).get("pack", [2, 5])
			var count := rng.randi_range(int(pk[0]), int(pk[1]))
			var champ := i < champs
			for k in count + (2 if champ else 0):
				var off := Vector2(rng.randf_range(-90, 90), rng.randf_range(-70, 70))
				var pos := cell_center(c) + off
				if is_solid(pos):
					pos = cell_center(c)
				var m := spawn_monster(mid, pos, base_l + rng.randi_range(0, 1), champ and k == 0)
				if m and champ and k > 0:
					m.hp_max *= 1.3
					m.hp = m.hp_max
	_spawn_superuniques(rng, base_l)
	var bid = def.get("boss", null)
	var uber: Dictionary = def.get("uber", {})
	if bid != null and DB.monsters.has(str(bid)) and (not uber.is_empty() or not _boss_dead(str(bid))):
		var pos := cell_center(gen.boss_spot if gen.boss_spot.x >= 0 else gen.exit)
		boss = spawn_monster(str(bid), pos, base_l + 1)
		# the guardian that still keeps its tithe: the same fight, much harder
		if boss and not uber.is_empty():
			boss.hp_max *= float(uber.get("hp", 3.0))
			boss.hp = boss.hp_max
			boss.dmg *= float(uber.get("dmg", 1.6))
			boss.set_meta("uber", true)


func _spawn_superuniques(rng: RandomNumberGenerator, base_l: int) -> void:
	var here := "act%d_floor%d" % [act_n, floor_n]
	for sid in DB.superuniques:
		var d: Dictionary = DB.superuniques[sid]
		if str(d.get("where", "")) != here:
			continue
		var c := _rule_cell({"far": 0.45, "from_boss": 10, "spacing": 8, "min_start": 12, "group": "pack"})
		if c.x < 0:
			c = _rule_cell({"far": 0.3, "from_boss": 5, "min_start": 8})
		if c.x < 0:
			continue
		var m := spawn_monster(str(d.get("monster", "")), cell_center(c), base_l + 2)
		if m == null:
			continue
		m.make_superunique(sid)
		var mn: Array = d.get("minions", [])
		if mn.size() == 3:
			for k in rng.randi_range(int(mn[1]), int(mn[2])):
				var pos := cell_center(c) + Vector2(rng.randf_range(-100, 100), rng.randf_range(-80, 80))
				var f := spawn_monster(str(mn[0]), cell_center(c) if is_solid(pos) else pos, base_l + 1)
				if f:
					f.hp_max *= 1.3
					f.hp = f.hp_max


func _boss_dead(bid: String) -> bool:
	return Game.flags.get("killed_" + bid, false)


func spawn_monster(mid: String, pos: Vector2, lvl: int, champion := false) -> Monster:
	if not DB.monsters.has(mid):
		return null
	var path := "res://scripts/actors/bosses/%s.gd" % mid
	var m: Monster
	if ResourceLoader.exists(path):
		m = load(path).new()
	else:
		m = Monster.new()
	m.position = pos
	m.home = pos
	m.level = self
	ysort.add_child(m)
	m.setup(mid, lvl, self, champion)
	monsters.append(m)
	return m


var corpses: Array = []
var decals: Array = []


func add_corpse(m: Monster) -> void:
	corpses.append(m)
	if corpses.size() > 40:
		var old = corpses.pop_front()
		if is_instance_valid(old):
			old.remove_corpse()
	get_tree().create_timer(45.0).timeout.connect(func():
		if is_instance_valid(m) and m in corpses:
			corpses.erase(m)
			m.remove_corpse())


func add_decal(n: Node2D) -> void:
	decals.append(n)
	if decals.size() > 80:
		var old = decals.pop_front()
		if is_instance_valid(old):
			old.create_tween().tween_property(old, "modulate:a", 0.0, 1.0).finished.connect(old.queue_free)


func on_monster_died(m: Monster) -> void:
	monsters.erase(m)
	if hover_obj == m:
		hover_obj = null
	if m.has_meta("spawn_i"):
		_state().dead[int(m.get_meta("spawn_i"))] = true
	Game.ch.add_xp(_xp_for(m))
	Game.on_event("kill", m.id)
	if m.kind == "boss":
		Game.flags["killed_" + m.id] = true
		var seal = m.data.get("seal", null)
		if seal:
			Game.flags["seal_" + str(seal)] = true
			Game.ch.recalc()
			Game.msg(L.t({"cs": "Pečeť se zlomila. Kahan zazářil jasněji.", "en": "The seal broke. The lamp burns brighter."}), Color("d9ecff"))
		Game.boss_bar.emit("", 0.0, false)
		var lines: Dictionary = m.data.get("lines", {})
		if lines.has("death"):
			boss_say(m, lines.death, 6.0)
		Game.save()
		_tithe_drops(m)
	if m.no_drops:
		return
	var ch := Game.ch
	var drops := Loot.monster_drops(m.mlvl, m.kind, float(ch.d.get("magic_find", 0.0)), float(ch.d.get("gold_find", 0.0)))
	if m.su_id != "":
		var su := Loot.roll_item(m.mlvl + 2, float(ch.d.get("magic_find", 0.0)) + 100.0, 1.0, "equipment", true)
		if su:
			drops.append(su)
	if m.kind == "boss":
		for uid in m.data.get("drops", []):
			if randf() < 0.65 or Game.difficulty > 0:
				var u := Loot.unique_item(str(uid), m.mlvl)
				if u:
					drops.append(u)
					break
	if m.stolen_gold > 0:
		var g := Item.create("grose_hromadka" if DB.items.has("grose_hromadka") else "grose_malo", 1)
		g.qty = m.stolen_gold
		drops.append(g)
	for it in drops:
		drop_item(it, m.global_position + Vector2(randf_range(-50, 50), randf_range(-30, 30)))


const KEY_BY_BOSS := {"vodnik": "klic_vody", "bazilisek": "klic_kamene", "jezibaba": "klic_ohne", "kostej": "klic_smrti"}


# On Noční můra and Nav the seal guardians may leave their key; their tithes leave a seal and rich loot.
func _tithe_drops(m: Monster) -> void:
	if m.has_meta("uber"):
		var seal := str(def.get("uber", {}).get("seal", ""))
		if DB.items.has(seal):
			drop_item(Item.create(seal, m.mlvl), m.global_position)
		for i in 3:
			var it := Loot.roll_item(m.mlvl, 200, 1.5, "equipment")
			if it:
				drop_item(it, m.global_position + Vector2(randf_range(-60, 60), randf_range(-40, 40)))
		return
	if Game.difficulty >= 1 and KEY_BY_BOSS.has(m.id) and randf() < [0.0, 0.3, 0.45][clampi(Game.difficulty, 0, 2)]:
		drop_item(Item.create(KEY_BY_BOSS[m.id], m.mlvl), m.global_position)


func _xp_for(m: Monster) -> int:
	var diff := Game.ch.level - m.mlvl
	var mult := 1.0 if diff <= 5 else maxf(0.05, 1.0 - 0.12 * (diff - 5))
	return int(m.xp_value * mult)


func drop_item(it: Item, pos: Vector2, quiet := false) -> void:
	if is_solid(pos):
		pos = cell_center(_nearest_open(to_cell(pos)))
	var g := GroundItem.create(it, pos)
	items_root.add_child(g)
	ground_items.append(g)
	if not quiet:
		g.toss()


# Floors are rebuilt on every visit, so whatever lies on the ground is kept aside when the hero leaves
# and laid back down on return. If the layout changed (a new session), it is heaped by the arrival point.
func _loot_key() -> String:
	return "%d:%d:%d" % [Game.difficulty, act_n, floor_n]


func _exit_tree() -> void:
	stash_loot()
	if not is_town and w > 0:
		_state().explored = explored


# This session's changes to the floor; dropped when the layout is a different one.
func _state() -> Dictionary:
	var st: Dictionary = Game.floor_state.get(_loot_key(), {})
	if int(st.get("seed", -1)) != Game.session_seed:
		st = {"seed": Game.session_seed, "dead": {}, "props": {}, "explored": PackedByteArray()}
		Game.floor_state[_loot_key()] = st
	return st


func _prop_key(p: PropNode) -> String:
	return "%s@%d,%d" % [p.id, p.cell.x, p.cell.y]


func _note_prop(p: PropNode, how: String) -> void:
	_state().props[_prop_key(p)] = how


func _restore_state() -> void:
	if is_town:
		return
	var st := _state()
	var dead: Dictionary = st.dead
	for m in monsters.duplicate():
		if dead.has(int(m.get_meta("spawn_i", -1))):
			monsters.erase(m)
			if m == boss:
				boss = null
			m.queue_free()
	var done: Dictionary = st.props
	for p in props:
		match str(done.get(_prop_key(p), "")):
			"open":
				p.used = true
				p.set_texture("truhla_open")
			"broken":
				_set_broken(p)
			"used":
				_set_shrine_used(p)
	var ex: PackedByteArray = st.explored
	if ex.size() == explored.size() and fog_img:
		explored = ex.duplicate()
		for y in h:
			for x in w:
				if explored[y * w + x] == 1:
					fog_img.set_pixel(x + 1, y + 1, Color(0, 0, 0, 0))
		(fog.texture as ImageTexture).update(fog_img)
		explored_rev += 1


func stash_loot() -> void:
	var kept := []
	for g in ground_items:
		if is_instance_valid(g) and g.item and not g.has_meta("quest_spawn"):
			kept.append([g.item.to_dict(), g.position.x, g.position.y])
	if kept.is_empty():
		Game.floor_loot.erase(_loot_key())
	else:
		Game.floor_loot[_loot_key()] = {"seed": Game.session_seed, "items": kept.slice(maxi(0, kept.size() - 300))}


func _restore_loot() -> void:
	var saved: Dictionary = Game.floor_loot.get(_loot_key(), {})
	var same_map := int(saved.get("seed", -1)) == Game.session_seed
	for e in saved.get("items", []):
		var it := Item.from_dict(e[0])
		var pos := Vector2(float(e[1]), float(e[2]))
		if not same_map and player:
			pos = player.global_position + Vector2(randf_range(-90, 90), randf_range(-60, 60))
		drop_item(it, pos, true)


# ---------------------------------------------------------------- town
func _populate_town() -> void:
	var tl: TownLayout = gen
	for pl in tl.placements:
		var p := _place_prop(pl.id, pl.cell, pl.get("block", true))
		if pl.has("interact"):
			p.interact = pl.interact
	for k in tl.points:
		arrive_points[k] = cell_center(tl.points[k])
	_place_books()
	var ad := DB.act(act_n)
	var spots: Dictionary = tl.npc_spots
	for nid in ad.get("town", {}).get("npcs", []):
		var npc := Npc.new()
		var role := str(DB.npcs.get(nid, {}).get("role", "other"))
		var c: Vector2i = spots.get(nid, spots.get(role, tl.points.get("center", Vector2i(w / 2, h / 2))))
		if spots.has(role) and not spots.has(nid):
			spots.erase(role)
		npc.position = cell_center(_nearest_open(c))
		ysort.add_child(npc)
		npc.setup(str(nid), self)
		npcs.append(npc)
		if not spots.has(nid) and not spots.has(role):
			spots[role] = c + Vector2i(2, 1)


func _spawn_player(arrive: String) -> void:
	player = Player.new()
	var pos: Vector2 = arrive_points.get(arrive, arrive_points.get("start", cell_center(gen.start)))
	if arrive == "portal_back" and not Game.portal.is_empty():
		pos = Game.portal.pos + Vector2(0, 50)
		Game.portal = {}
	if is_solid(pos):
		pos = cell_center(_nearest_open(to_cell(pos)))
	player.position = pos
	ysort.add_child(player)
	player.setup(self)
	Game.player = player
	if arrive == "portal" or (Game.portal.get("town_end", false) and is_town):
		pass
	if not Game.portal.is_empty() and Game.portal.get("act", 0) == act_n:
		var pp: Vector2 = Game.portal.pos if not is_town else arrive_points.get("portal", pos + Vector2(80, 0))
		if is_town or Game.portal.floor == floor_n:
			_make_portal_node(pp)


func spawn_hireling() -> void:
	if hireling and is_instance_valid(hireling):
		hireling.queue_free()
	hireling = null
	var m: Dictionary = Game.ch.merc
	if m.is_empty() or m.get("dead", false) or player == null:
		return
	hireling = Hireling.new()
	var spot := random_open_near(player.global_position, 60.0, 120.0)
	hireling.position = spot if spot != Vector2.INF else player.global_position + Vector2(-60, 20)
	ysort.add_child(hireling)
	hireling.setup(self)


# ---------------------------------------------------------------- portals
func open_portal(pos: Vector2) -> void:
	Game.portal = {"act": act_n, "floor": floor_n, "pos": pos + Vector2(70, 0)}
	if portal_node:
		portal_node.queue_free()
		props.erase(portal_node)
	_make_portal_node(pos + Vector2(70, 0))
	Sfx.play_at("portal", pos)


func _make_portal_node(pos: Vector2) -> void:
	var p := PropNode.new()
	p.id = "portal"
	p.interact = "portal"
	p.position = pos
	p.sprite = Sprite2D.new()
	p.sprite.texture = Fx.ring_tex()
	p.sprite.modulate = Color(0.5, 0.75, 1.0, 0.9)
	p.sprite.scale = Vector2(0.9, 1.4)
	p.sprite.position = Vector2(0, -80)
	var mat := ShaderMaterial.new()
	mat.shader = Actor.SHADER
	p.sprite.material = mat
	p.add_child(p.sprite)
	var l := Fx.make_light(Color(0.5, 0.75, 1.0), 180, 1.2)
	l.position = Vector2(0, -80)
	p.add_child(l)
	var tw := p.sprite.create_tween().set_loops()
	tw.tween_property(p.sprite, "rotation", TAU, 2.0).from(0.0)
	ysort.add_child(p)
	props.append(p)
	portal_node = p


# ---------------------------------------------------------------- picking & interaction
func pick_at(pos: Vector2):
	if Input.is_action_pressed("show_items"):
		for g in ground_items:
			if is_instance_valid(g) and g.hit_rect().has_point(pos):
				return {"type": "item", "node": g}
	var best = null
	var bd := INF
	for m in monsters:
		if m.dead or not m.visible:
			continue
		if m.hit_rect().has_point(pos) and _targetable(m):
			var dd: float = m.center_pos().distance_to(pos)
			if dd < bd:
				bd = dd
				best = {"type": "monster", "node": m}
	if best:
		return best
	for n in npcs:
		if n.hit_rect().has_point(pos):
			return {"type": "npc", "node": n}
	for g in ground_items:
		if is_instance_valid(g) and g.visible and g.hit_rect().has_point(pos):
			return {"type": "item", "node": g}
	for p in props:
		if is_instance_valid(p) and p.interact != "" and not p.used and p.hit_rect().has_point(pos):
			return {"type": "prop", "node": p}
	return null


# Aggro monsters stay clickable a bit past the lamp, so archers and casters at the edge of the light can be answered.
func _targetable(m: Monster) -> bool:
	if is_town or m.kind == "boss" or m.revealed_t > 0.0 or lit(m.global_position):
		return true
	return m.aggro and player != null and player.global_position.distance_to(m.global_position) < player.light_radius_px() * 1.6 + 60.0


func interact(pl: Player, type: String, node: Node) -> void:
	match type:
		"item":
			_pickup(node)
		"npc":
			if Game.main:
				node.talk_pose()
				Game.main.open_npc(node)
		"prop":
			_use_prop(pl, node)


func collect_gold_near(pos: Vector2, r: float) -> void:
	for g in ground_items.duplicate():
		if is_instance_valid(g) and g.item.slot() == "gold" and g.global_position.distance_to(pos) <= r:
			_pickup(g)


func _pickup(g: GroundItem) -> void:
	if not is_instance_valid(g):
		return
	if Game.ch.pickup(g.item):
		Sfx.play("gold" if g.item.slot() == "gold" else "pickup")
		if g.item.slot() == "gold":
			float_text(g.global_position + Vector2(0, -30), "+%d" % g.item.qty, Color("e9c46a"))
		ground_items.erase(g)
		g.queue_free()
		if g.has_meta("quest_spawn"):
			Game.flags["took:%d:%d:%s" % [act_n, floor_n, g.item.base_id]] = true
		Game.on_event("pick", g.item.base_id)
		Game.learn("item", g.item.base_id)
		Game.learn("unique", g.item.unique_id)
		for qid in Game.quests.keys():
			Game._check_pick_goals(qid)
		if g.item.base_id == "srdce_zvonu":
			Game.flags["has_clapper"] = true
	else:
		Game.msg(L.t("inv_full"))


func _use_prop(pl: Player, p: PropNode) -> void:
	match p.interact:
		"stairs_down":
			if is_town:
				Game.goto(act_n, 1, "stairs_down")
			else:
				Game.goto(act_n, floor_n + 1, "stairs_down")
		"stairs_up":
			if floor_n <= 1 or def.has("uber"):
				Game.goto(act_n, 0, "mine")
			else:
				Game.goto(act_n, floor_n - 1, "stairs_up")
		"waypoint":
			Sfx.play("waypoint")
			if Game.main:
				Game.main.open_waypoints()
		"portal":
			Sfx.play("portal")
			if is_town:
				var pt: Dictionary = Game.portal
				Game.goto(int(pt.act), int(pt.floor), "portal_back")
				return
			Game.goto(act_n, 0, "portal")
		"stash":
			if Game.main:
				Game.main.open_stash()
		"chest":
			p.used = true
			p.set_hover(false)
			p.set_texture("truhla_open")
			_note_prop(p, "open")
			Sfx.play_at("chest_open", p.global_position)
			var n := randi_range(1, 3)
			for i in n:
				var it := Loot.roll_item(Game.mlvl_base(int(def.get("level", 1))) + 1, float(Game.ch.d.get("magic_find", 0.0)), 0.15) if randf() < 0.6 else Loot.gold(Game.mlvl_base(int(def.get("level", 1))))
				if it:
					drop_item(it, p.global_position + Vector2(randf_range(-50, 50), randf_range(10, 50)))
		"break":
			pl.face_to(p.global_position)
			pl.start_action("attack", 0.35, 0.5, func(): _break_prop(p))
		"shrine":
			_use_shrine(p)
		"book":
			var bid := str(p.data.get("book", ""))
			Game.learn("book", bid)
			Sfx.play("ui_open", 0.6, 0.0)
			if Game.main:
				Game.main.ui.open_book(bid)
		"quest":
			_use_quest_prop(pl, p)


func _break_prop(p: PropNode) -> void:
	if p.used:
		return
	_set_broken(p)
	_note_prop(p, "broken")
	Sfx.play_at("urn_break" if p.id == "urna" else "barrel_break", p.global_position)
	Fx.burst(self, p.global_position + Vector2(0, -30), Color("8a7458"), 14, 140, 0.5, 0.2)
	var r := randf()
	var lvl := Game.mlvl_base(int(def.get("level", 1)))
	if r < 0.12 and act_n >= 1 and p.id == "sud":
		Fx.ring(self, p.global_position, 100, Fx.ELEM.fire)
		Sfx.play_at("explosion", p.global_position)
		for m in Combat.targets_in_radius(self, p.global_position, 100, 1):
			m.take_damage(10 + lvl * 3, "fire", player)
		if player.global_position.distance_to(p.global_position) < 100:
			player.take_damage(5 + lvl * 2, "fire", null)
	elif r < 0.25 and p.id == "urna" and DB.monsters.has("kostlivy_havir") and act_n >= 2:
		var m := spawn_monster(def.get("monsters", ["kostlivy_havir"]).pick_random(), p.global_position, lvl)
		if m:
			m.wake()
	elif r < 0.5:
		var it: Item = Loot.gold(lvl) if randf() < 0.6 else Loot.potion_for(lvl)
		if it:
			drop_item(it, p.global_position + Vector2(0, 20))
	elif r < 0.58:
		var it2 := Loot.roll_item(lvl, 0.0, 0.0, "equipment")
		if it2:
			drop_item(it2, p.global_position + Vector2(0, 20))


func _set_broken(p: PropNode) -> void:
	p.used = true
	p.set_hover(false)
	p.set_texture(p.id + "_broken")
	if not DB.has_tex("props/%s_broken" % p.id):
		p.sprite.visible = false
	var body := p.get_node_or_null("Body")
	if body:
		body.queue_free()
	var cells: Array = p.get_meta("cells", [p.cell, Vector2i.ONE])
	for yy in range(cells[0].y, cells[0].y + cells[1].y):
		for xx in range(cells[0].x, cells[0].x + cells[1].x):
			if xx >= 0 and yy >= 0 and xx < w and yy < h and gen.at(xx, yy) != DungeonGen.WALL:
				solid[yy * w + xx] = 0
				astar.set_point_solid(Vector2i(xx, yy), false)


func _set_shrine_used(p: PropNode) -> void:
	p.used = true
	p.set_hover(false)
	if DB.has_tex("props/modla_used"):
		p.set_texture("modla_used")
	else:
		p.sprite.modulate = Color(0.5, 0.5, 0.5)


func _use_shrine(p: PropNode) -> void:
	var sid := str(p.data.get("shrine", ""))
	var sd: Dictionary = DB.shrines.get(sid, {})
	Game.learn("shrine", sid)
	_set_shrine_used(p)
	_note_prop(p, "used")
	Sfx.play_at("shrine", p.global_position)
	var eff: Dictionary = sd.get("effect", {})
	if eff.get("random", false):
		var keys := DB.shrines.keys().filter(func(k): return not DB.shrines[k].get("effect", {}).get("random", false))
		if keys.size() > 0:
			sd = DB.shrines[keys.pick_random()]
			eff = sd.get("effect", {})
	var mods := {}
	for m in eff.get("mods", []):
		mods[str(m.stat)] = float(m.get("value", 0))
	if eff.has("curse"):
		mods[str(eff.curse.stat)] = float(eff.curse.value)
	if not mods.is_empty():
		Game.ch.add_buff("shrine_" + sid, mods, float(eff.get("duration", 120)))
	if eff.get("heal", false):
		Game.ch.hp = Game.ch.d.hp_max
		Game.ch.mana = Game.ch.d.mana_max
		player.hp = Game.ch.hp
	Game.ch.changed.emit()
	Game.msg(L.t(sd.get("msg", sd.get("name", sid))), Color("e9d8a6"))
	Fx.ring(self, p.global_position, 120, Color("ffe7a0"))
	Fx.burst(self, player.global_position + Vector2(0, -50), Color("ffe7a0"), 24, 90, 1.0, 0.3, true)


func _use_quest_prop(pl: Player, p: PropNode) -> void:
	if boss and is_instance_valid(boss) and boss.has_method("on_quest_prop"):
		boss.on_quest_prop(p, pl)
		return
	match p.id:
		"zvon":
			Sfx.play_at("bell_toll", p.global_position, 0.5)
			if Game.ch.inv.count("srdce_zvonu") > 0:
				Game.msg(L.t({"cs": "Tohle není zvon z Hory. Srdce zvonu patří Báře do krčmy.", "en": "This is not the Mountain's bell. Take the clapper to Bára at the tavern."}), Color("e9d8a6"))
			elif Game.quest_state("srdce_zvonu") == "active":
				Game.msg(L.t({"cs": "Zvon bez srdce jen tupě duní. Bára slyšela srdce cinkat o patro níž.", "en": "Without its clapper the bell only thuds. Bára heard the clapper clinking one level further down."}), Color("e9d8a6"))
			else:
				Game.msg(L.t({"cs": "Zvon bez srdce jen tupě duní.", "en": "Without its clapper the bell only thuds."}), Color("e9d8a6"))
	Game.on_event("use", p.id)


# ---------------------------------------------------------------- feedback
func float_text(pos: Vector2, text: String, color: Color, is_player := false, size := 0) -> void:
	var l := _float_label(text, color, size if size > 0 else (24 if is_player else 26))
	l.position = pos - l.size / 2.0 + Vector2(0, -12)
	var tw := l.create_tween().set_parallel(true)
	tw.tween_property(l, "scale", Vector2.ONE, 0.14).from(Vector2.ONE * 1.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "position:y", l.position.y - 46, 1.0).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(l, "modulate:a", 0.0, 0.45).set_delay(0.6)
	tw.chain().tween_callback(l.queue_free)


func miss_text(pos: Vector2, text: String) -> void:
	var l := _float_label(text, Color(0.62, 0.6, 0.56, 0.85), 18)
	l.position = pos - l.size / 2.0 + Vector2(randf_range(-10, 10), -4)
	var tw := l.create_tween().set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 22, 0.6).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "modulate:a", 0.0, 0.3).set_delay(0.3)
	tw.chain().tween_callback(l.queue_free)


# Hits on the same target within a short window add up into one number instead of a column of small ones.
func damage_number(target: Node2D, amount: float, color: Color, crit := false, is_player := false) -> void:
	var now := Time.get_ticks_msec()
	var prev = target.get_meta("dmg_label") if target.has_meta("dmg_label") else null
	if is_instance_valid(prev) and not prev.is_queued_for_deletion() and now - int(target.get_meta("dmg_t", 0)) < 350:
		amount += float(prev.get_meta("sum", 0.0))
		crit = crit or bool(prev.get_meta("crit", false))
		prev.queue_free()
	var n := maxi(1, int(round(amount)))
	var big := crit or (is_player and target is Actor and amount > (target as Actor).hp_max * 0.2)
	var size := 46 if crit else (int(clampf(26.0 + log(float(n)) * 2.2, 26.0, 38.0)) if not is_player else 28)
	var col := Color("ffd23f") if crit else (Color("ff5a4a") if is_player else color)
	var l := _float_label(str(n) + ("!" if crit else ""), col, size)
	l.set_meta("sum", amount)
	l.set_meta("crit", crit)
	target.set_meta("dmg_label", l)
	target.set_meta("dmg_t", now)
	var top: Vector2 = target.top_pos() if target.has_method("top_pos") else target.global_position + Vector2(0, -60)
	var side := (1.0 if randf() < 0.5 else -1.0) * randf_range(8.0, 22.0)
	l.position = top - l.size / 2.0 + Vector2(side * 0.5, -8)
	var tw := l.create_tween().set_parallel(true)
	tw.tween_property(l, "scale", Vector2.ONE, 0.18 if big else 0.12).from(Vector2.ONE * (1.9 if big else 1.4)).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "position:x", l.position.x + side, 0.9).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "position:y", l.position.y - (60 if big else 40), 0.9).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(l, "modulate:a", 0.0, 0.35).set_delay(0.75 if big else 0.55)
	tw.chain().tween_callback(l.queue_free)


func _float_label(text: String, color: Color, size: int) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0.04, 0.03, 0.03, 0.95))
	l.add_theme_constant_override("outline_size", maxi(6, size / 4))
	l.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	l.add_theme_constant_override("shadow_offset_y", 2)
	l.material = CanvasItemMaterial.new()
	(l.material as CanvasItemMaterial).light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	text_root.add_child(l)
	l.reset_size()
	l.pivot_offset = l.size / 2.0
	return l


# text is the line from the data ({cs, en}), spoken in the boss's own generated voice, or a plain string.
func boss_say(m: Monster, text, dur := 4.5) -> void:
	if text is Dictionary:
		dur = maxf(dur, Sfx.voice(m.id, text) + 0.8)
		text = L.t(text)
	if Game.main:
		Game.main.boss_line(m.label_name(), str(text), m.id, dur)


func shake(amt: float) -> void:
	shake_amt = maxf(shake_amt, amt)


func _process(delta: float) -> void:
	if player == null:
		return
	if shake_amt > 0.1 and player.cam:
		player.cam.offset = Vector2(randf_range(-1, 1), randf_range(-1, 1)) * shake_amt
		shake_amt = move_toward(shake_amt, 0.0, delta * 30.0)
	elif player.cam:
		player.cam.offset = Vector2.ZERO
	explore_t -= delta
	if explore_t <= 0.0:
		explore_t = 0.2
		_explore()
	_update_hover()
	var alt := Input.is_action_pressed("show_items")
	for g in ground_items:
		if is_instance_valid(g):
			g.show_label(alt)
	if not is_town:
		var lr := player.light_radius_px() * 1.15
		for m in monsters:
			var d: float = m.global_position.distance_to(player.global_position)
			# far, unwoken monsters sleep; the floors are big enough that most of them are
			var awake: bool = m.aggro or d < SLEEP_PX or m.kind == "boss"
			if m.is_physics_processing() != awake:
				m.set_physics_process(awake)
				m.set_process(awake)
			if not awake:
				continue
			m.revealed_t = maxf(0.0, m.revealed_t - delta)
			var near: bool = m.kind == "boss" or m.revealed_t > 0.0 or (d < lr and (d < CELL * 1.6 or in_sight(m.global_position)))
			m.sight = move_toward(m.sight, 1.0 if near else 0.0, delta * 5.0)
			m.visible = m.sight > 0.01 or m.light != null
			m.sprite.self_modulate.a = m.sight if m.light == null else maxf(m.sight, 0.25)
			if m.shadow:
				m.shadow.visible = m.sight > 0.5
			m.update_bar(delta)


func _explore() -> void:
	var c := to_cell(player.global_position)
	var r := int(player.light_radius_px() / CELL) + 1 if not is_town else 12
	for oy in range(-r, r + 1):
		for ox in range(-r, r + 1):
			var n := c + Vector2i(ox, oy)
			if n.x >= 0 and n.y >= 0 and n.x < w and n.y < h and ox * ox + oy * oy <= r * r and explored[n.y * w + n.x] == 0:
				explored[n.y * w + n.x] = 1
				explored_rev += 1
				if fog_img:
					fog_img.set_pixel(n.x + 1, n.y + 1, Color(0, 0, 0, 0))
					fog_dirty = true
	if fog_dirty:
		fog_dirty = false
		(fog.texture as ImageTexture).update(fog_img)


# Contact shadow on the floor along every wall, so rooms read as dug out rather than painted on.
func _make_wall_shade() -> void:
	var tex := {}
	for d in [Vector2i.UP, Vector2i.DOWN, Vector2i.LEFT, Vector2i.RIGHT]:
		var g := Gradient.new()
		g.offsets = PackedFloat32Array([0.0, 0.45, 1.0])
		g.colors = PackedColorArray([Color(0, 0, 0, 0.62), Color(0, 0, 0, 0.22), Color(0, 0, 0, 0)])
		var t := GradientTexture2D.new()
		t.gradient = g
		t.width = 32
		t.height = 32
		t.fill_from = Vector2(0.5, 0.5) + Vector2(d) * 0.5
		t.fill_to = Vector2(0.5, 0.5) - Vector2(d) * 0.5
		tex[d] = t
	var rects := []
	for y in h:
		for x in w:
			if solid[y * w + x] == 1:
				continue
			var o := Vector2(x * CELL, y * CELL)
			if y > 0 and solid[(y - 1) * w + x] == 1:
				rects.append([tex[Vector2i.UP], Rect2(o + Vector2(0, 30), Vector2(CELL, 30))])
			if y < h - 1 and solid[(y + 1) * w + x] == 1:
				rects.append([tex[Vector2i.DOWN], Rect2(o + Vector2(0, CELL - 14), Vector2(CELL, 14))])
			if x > 0 and solid[y * w + x - 1] == 1:
				rects.append([tex[Vector2i.LEFT], Rect2(o, Vector2(22, CELL))])
			if x < w - 1 and solid[y * w + x + 1] == 1:
				rects.append([tex[Vector2i.RIGHT], Rect2(o + Vector2(CELL - 22, 0), Vector2(22, CELL))])
	var n := Node2D.new()
	n.z_index = -17
	n.light_mask = 1 | SHADOW_MASK
	n.draw.connect(func():
		for r in rects:
			n.draw_texture_rect(r[0], r[1], false))
	add_child(n)


# Unexplored cells stay pitch black; explored ones show dimly under the ambient, like D1's remembered walls.
func _make_fog() -> void:
	fog_img = Image.create(w + 2, h + 2, false, Image.FORMAT_RGBA8)
	fog_img.fill(Color(0, 0, 0, 1))
	fog = Sprite2D.new()
	fog.texture = ImageTexture.create_from_image(fog_img)
	fog.centered = false
	fog.scale = Vector2(CELL, CELL)
	fog.position = Vector2(-CELL * 1.5, -CELL * 1.5)
	fog.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
	fog.z_index = 30
	var mat := CanvasItemMaterial.new()
	mat.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	fog.material = mat
	add_child(fog)


func in_sight(p: Vector2) -> bool:
	var a := to_cell(player.global_position)
	var b := to_cell(p)
	var n := maxi(absi(b.x - a.x), absi(b.y - a.y))
	for i in range(1, n):
		var c := Vector2i(roundi(lerpf(a.x, b.x, float(i) / n)), roundi(lerpf(a.y, b.y, float(i) / n)))
		if c.x >= 0 and c.y >= 0 and c.x < w and c.y < h and solid[c.y * w + c.x] == 1:
			return false
	return true


func _update_hover() -> void:
	if Game.paused_ui or (Game.main and Game.main.mouse_over_ui()):
		_set_hover(null)
		return
	var pick = pick_at(get_global_mouse_position())
	_set_hover(pick.node if pick else null)


func _set_hover(n) -> void:
	if hover_obj == n:
		return
	if hover_obj and is_instance_valid(hover_obj):
		hover_obj.set_hover(false)
	hover_obj = n
	if n:
		n.set_hover(true)


func hover_info() -> Dictionary:
	if hover_obj == null or not is_instance_valid(hover_obj):
		return {}
	if hover_obj is Monster:
		return {"name": hover_obj.label_name(), "sub": hover_obj.label_sub(), "hp": hover_obj.hp / hover_obj.hp_max,
			"kind": hover_obj.kind, "color": Color("e9c46a") if hover_obj.kind != "normal" else Color("e8e2d4")}
	if hover_obj is Npc:
		return {"name": hover_obj.display_name, "sub": "", "color": Color("b9d6a0")}
	if hover_obj is PropNode:
		return {"name": hover_obj.label(), "sub": "", "color": Color("d8d0b8")}
	return {}
