class_name Level
extends Node2D

const CELL := 64
const DARK := {1: Color(0.07, 0.065, 0.075), 2: Color(0.06, 0.07, 0.06), 3: Color(0.075, 0.06, 0.055), 4: Color(0.055, 0.05, 0.08)}
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
var astar := AStarGrid2D.new()
var floor_layer: TileMapLayer
var deco_layer: TileMapLayer
var water_layer: TileMapLayer
var wall_layer: TileMapLayer
var ysort: Node2D
var items_root: Node2D
var fx_root: Node2D
var text_root: Node2D
var player: Player
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


func build(a: int, f: int, arrive: String) -> void:
	act_n = a
	floor_n = f
	is_town = f == 0
	font = load("res://assets/fonts/TataHand.ttf")
	var ad := DB.act(a)
	if is_town:
		tileset_name = str(ad.get("town", {}).get("tileset", "town_hora"))
		gen = TownLayout.make(a)
	else:
		def = DB.floor_def(a, f)
		tileset_name = str(ad.get("dungeon", {}).get("tileset", "hora"))
		gen = DungeonGen.new()
		gen.generate(def, hash("%d:%d:%d:%d" % [Game.difficulty, a, f, Game.session_seed]))
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
	var cm := CanvasModulate.new()
	cm.color = TOWN_DUSK.get(a, Color(0.4, 0.4, 0.5)) if is_town else DARK.get(a, Color(0.07, 0.065, 0.075)).darkened(f * 0.04)
	add_child(cm)
	if is_town:
		_populate_town()
	else:
		_populate_dungeon()
	_build_collision()
	_build_astar()
	_spawn_player(arrive)
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


func _make_tileset() -> TileSet:
	var ts := TileSet.new()
	ts.tile_size = Vector2i(CELL, CELL)
	var base := Color("4a4038") if not is_town else Color("6a6450")
	for i in 4:
		_add_src(ts, i, _tile_tex("tiles/%s/floor_%d" % [tileset_name, i], Vector2i(64, 64), base), Vector2i(64, 64), Vector2i.ZERO)
	for i in 3:
		_add_src(ts, 10 + i, _tile_tex("tiles/%s/wall_%d" % [tileset_name, i], Vector2i(64, 96), base.darkened(0.3)), Vector2i(64, 96), Vector2i(0, 16))
	for i in 4:
		var t := DB.tex("tiles/%s/floor_deco_%d" % [tileset_name, i])
		if t:
			_add_src(ts, 20 + i, t, Vector2i(64, 64), Vector2i.ZERO)
	_add_src(ts, 30, _water_tex(), Vector2i(64, 64), Vector2i.ZERO)
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
	for y in h:
		for x in w:
			var c := Vector2i(x, y)
			if solid[y * w + x] == 0:
				floor_layer.set_cell(c, rng.randi_range(0, 3) if rng.randf() < 0.45 else 0, Vector2i.ZERO)
				if water[y * w + x] == 1:
					water_layer.set_cell(c, 30, Vector2i.ZERO)
				elif has_deco and rng.randf() < 0.07:
					deco_layer.set_cell(c, 20 + rng.randi_range(0, 3), Vector2i.ZERO)
			elif _near_floor(x, y, 2):
				wall_layer.set_cell(c, 10 + (rng.randi_range(0, 2) if rng.randf() < 0.4 else 0), Vector2i.ZERO)


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
			if solid[y * w + x] == 1 and _near_floor(x, y, 1):
				var x0 := x
				while x < w and solid[y * w + x] == 1 and _near_floor(x, y, 1):
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
		var j := pts.size() - 1
		while j > i and not _clear_wide(cur, pts[j]):
			j -= 1
		out.append(pts[j])
		cur = pts[j]
		i = j + 1
	return out


func _clear_wide(a: Vector2, b: Vector2) -> bool:
	var perp := (b - a).normalized().orthogonal() * 16.0
	return line_of_sight(a + perp, b + perp) and line_of_sight(a - perp, b - perp)


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
		return [player] if player and not player.dead else []
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
		block_cells(Vector2i(c.x - fw / 2, c.y - fh + 1), Vector2i(fw, fh))
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
	rng.randomize()
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
	var used := {}
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
		var c: Vector2i = take.call()
		if c.x < 0:
			break
		_place_prop("truhla", c).interact = "chest"
	var gods := DB.shrines.keys()
	for i in n_shrine:
		var c: Vector2i = take.call()
		if c.x < 0 or gods.is_empty():
			break
		var g: String = gods.pick_random()
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
	_place_quest_props()
	_spawn_monsters(rng, used)


func _find_free_near(c: Vector2i, rmin: int, rmax: int) -> Vector2i:
	for r in range(rmin, rmax + 3):
		for oy in range(-r, r + 1):
			for ox in range(-r, r + 1):
				var n := c + Vector2i(ox, oy)
				if _cell_free_area(n, 1) and n != gen.start and n != gen.exit:
					return n
	return c


func _place_quest_props() -> void:
	for q in def.get("quest_props", []):
		var qid := str(q)
		if DB.items.has(qid) and not DB.props.has(qid):
			if Game.ch.inv.count(qid) > 0:
				continue
			var cells := _free_cells(14)
			if cells.size() > 0:
				drop_item(Item.create(qid, 1), cell_center(cells[0]))
			continue
		var n := 1
		var near_boss := gen.boss_spot.x >= 0
		match qid:
			"hrnek_dusicka":
				n = 6
			"zrcadlo":
				n = 4
			"kbelik":
				n = 4
		for i in n:
			var c: Vector2i
			if near_boss and qid != "dub" and qid != "truhla_kostej":
				c = _find_free_near(gen.boss_spot + Vector2i(int(cos(TAU * i / n) * 6), int(sin(TAU * i / n) * 4)), 0, 3)
			else:
				var cells := _free_cells(16)
				if cells.is_empty():
					break
				c = cells[i % cells.size()]
			var p := _place_prop(qid, c, qid in ["dub", "zrcadlo"])
			p.interact = "quest"


func _spawn_monsters(rng: RandomNumberGenerator, used: Dictionary) -> void:
	var pool: Array = def.get("monsters", [])
	pool = pool.filter(func(m): return DB.monsters.has(m))
	var base_l := Game.mlvl_base(int(def.get("level", 1)))
	if not pool.is_empty():
		var free := _free_cells(9)
		var packs := int(free.size() / 75.0 * float(def.get("density", 1.0)))
		var champs := 1 + (1 if floor_n > 1 else 0) + Game.difficulty
		for i in packs:
			if free.is_empty():
				break
			var c: Vector2i = free.pop_back()
			var mid: String = pool.pick_random()
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
	var bid = def.get("boss", null)
	if bid != null and DB.monsters.has(str(bid)) and not _boss_dead(str(bid)):
		var pos := cell_center(gen.boss_spot if gen.boss_spot.x >= 0 else gen.exit)
		boss = spawn_monster(str(bid), pos, base_l + 1)


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


func on_monster_died(m: Monster) -> void:
	monsters.erase(m)
	if hover_obj == m:
		hover_obj = null
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
			boss_say(m, L.t(lines.death), 6.0)
		Game.save()
	if m.no_drops:
		return
	var ch := Game.ch
	var drops := Loot.monster_drops(m.mlvl, m.kind, float(ch.d.get("magic_find", 0.0)), float(ch.d.get("gold_find", 0.0)))
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


func _xp_for(m: Monster) -> int:
	var diff := Game.ch.level - m.mlvl
	var mult := 1.0 if diff <= 5 else maxf(0.05, 1.0 - 0.12 * (diff - 5))
	return int(m.xp_value * mult)


func drop_item(it: Item, pos: Vector2) -> void:
	if is_solid(pos):
		pos = cell_center(_nearest_open(to_cell(pos)))
	var g := GroundItem.create(it, pos)
	items_root.add_child(g)
	ground_items.append(g)
	Sfx.play_at("drop_item", pos, 0.5)


# ---------------------------------------------------------------- town
func _populate_town() -> void:
	var tl: TownLayout = gen
	for pl in tl.placements:
		var p := _place_prop(pl.id, pl.cell, pl.get("block", true))
		if pl.has("interact"):
			p.interact = pl.interact
	for k in tl.points:
		arrive_points[k] = cell_center(tl.points[k])
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
	if Input.is_action_pressed("show_items") or true:
		for g in ground_items:
			if is_instance_valid(g) and g.lbl.visible and g.hit_rect().has_point(pos):
				return {"type": "item", "node": g}
	var best = null
	var bd := INF
	for m in monsters:
		if m.dead or not m.visible:
			continue
		if m.hit_rect().has_point(pos) and (is_town or lit(m.global_position) or m.kind == "boss"):
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
		if is_instance_valid(g) and g.hit_rect().has_point(pos):
			return {"type": "item", "node": g}
	for p in props:
		if is_instance_valid(p) and p.interact != "" and not p.used and p.hit_rect().has_point(pos):
			return {"type": "prop", "node": p}
	return null


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


func _pickup(g: GroundItem) -> void:
	if not is_instance_valid(g):
		return
	if Game.ch.pickup(g.item):
		Sfx.play("gold" if g.item.slot() == "gold" else "pickup")
		if g.item.slot() == "gold":
			float_text(g.global_position + Vector2(0, -30), "+%d" % g.item.qty, Color("e9c46a"))
		ground_items.erase(g)
		g.queue_free()
		Game.on_event("pick", g.item.base_id)
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
			if floor_n <= 1:
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
		"quest":
			_use_quest_prop(pl, p)


func _break_prop(p: PropNode) -> void:
	if p.used:
		return
	p.used = true
	p.set_hover(false)
	p.set_texture(p.id + "_broken")
	if not DB.has_tex("props/%s_broken" % p.id):
		p.sprite.visible = false
	Sfx.play_at("urn_break" if p.id == "urna" else "barrel_break", p.global_position)
	Fx.burst(self, p.global_position + Vector2(0, -30), Color("8a7458"), 14, 140, 0.5, 0.2)
	astar.set_point_solid(p.cell, false)
	solid[p.cell.y * w + p.cell.x] = 0 if gen.at(p.cell.x, p.cell.y) != DungeonGen.WALL else 1
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


func _use_shrine(p: PropNode) -> void:
	var sid := str(p.data.get("shrine", ""))
	var sd: Dictionary = DB.shrines.get(sid, {})
	p.used = true
	p.set_hover(false)
	if DB.has_tex("props/modla_used"):
		p.set_texture("modla_used")
	else:
		p.sprite.modulate = Color(0.5, 0.5, 0.5)
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
			if Game.ch.inv.count("srdce_zvonu") > 0:
				Game.on_event("use", "zvon")
	Game.on_event("use", p.id)


# ---------------------------------------------------------------- feedback
func float_text(pos: Vector2, text: String, color: Color, is_player := false) -> void:
	var l := Label.new()
	l.text = text
	l.add_theme_font_override("font", font)
	l.add_theme_font_size_override("font_size", 26 if not is_player else 24)
	l.add_theme_color_override("font_color", color)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	l.add_theme_constant_override("outline_size", 6)
	l.position = pos + Vector2(-30, -20)
	l.material = CanvasItemMaterial.new()
	(l.material as CanvasItemMaterial).light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	text_root.add_child(l)
	var tw := l.create_tween().set_parallel(true)
	tw.tween_property(l, "position:y", l.position.y - 50, 0.9).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "modulate:a", 0.0, 0.9).set_delay(0.35)
	tw.chain().tween_callback(l.queue_free)


func boss_say(m: Monster, text: String, dur := 4.5) -> void:
	if Game.main:
		Game.main.boss_line(m.label_name(), text, m.id, dur)


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
			var near: bool = m.global_position.distance_to(player.global_position) < lr or m.kind == "boss"
			m.visible = near or m.light != null
			if m.shadow:
				m.shadow.visible = near


func _explore() -> void:
	var c := to_cell(player.global_position)
	var r := int(player.light_radius_px() / CELL) + 1 if not is_town else 12
	for oy in range(-r, r + 1):
		for ox in range(-r, r + 1):
			var n := c + Vector2i(ox, oy)
			if n.x >= 0 and n.y >= 0 and n.x < w and n.y < h and ox * ox + oy * oy <= r * r:
				explored[n.y * w + n.x] = 1


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
