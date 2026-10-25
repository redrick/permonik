extends Node

# Floor generator stats: size, walk from the stairs to the exit and the boss, and the XP a full clear
# gives, then a hero who clears every floor once on Normal: level on arrival vs the floor and its boss.
# Run: godot --headless --path game -- --quick --genstats [--seeds 12]
var args := OS.get_cmdline_user_args()


func _ready() -> void:
	if args.has("--real"):
		_real()
		return
	var seeds := int(args[args.find("--seeds") + 1]) if args.has("--seeds") else 12
	var lvl := 1
	var xp := 0
	print("GEN act floor | size  open  rooms  exit_path boss_path dead_ends | monsters  xp_clear | hero_in -> floor_lv  hero_boss -> boss_lv")
	for a in DB.acts:
		for f in a.floors:
			if f.has("uber"):
				continue
			var s := {"w": 0.0, "open": 0.0, "rooms": 0.0, "exit": 0.0, "boss": 0.0, "dead": 0.0}
			for i in seeds:
				var g := DungeonGen.new()
				g.generate(f, 1000 + i * 31)
				s.w += g.w * g.h
				s.open += g.dist.size()
				s.rooms += g.rooms.size()
				s.exit += g.dist.get(g.exit, 0)
				s.boss += g.dist.get(g.boss_spot, 0)
				s.dead += _dead_ends(g)
				if i < 2 and args.has("--png"):
					_png(g, "%s/a%d_f%d_s%d.png" % [args[args.find("--png") + 1], a.id, f.n, i])
			for k in s:
				s[k] /= seeds
			var mon := _monsters(f, s.open)
			var fl := int(f.level)
			var hero_in := lvl
			for m in mon.list:
				var diff: int = lvl - m.lvl
				var mult := 1.0 if diff <= 5 else maxf(0.05, 1.0 - 0.12 * (diff - 5))
				xp += int(m.xp * mult)
				while xp >= CharData.xp_for(lvl + 1):
					lvl += 1
			var hero_boss := lvl
			if f.get("boss") != null:
				var bm: Dictionary = DB.monster(str(f.boss))
				xp += int(float(bm.get("xp_mult", 1.0)) * 12.0 * pow(fl + 1, 1.55) * 5.0)
			print("GEN %d %2d | %5d %5d %5.1f %9.0f %9.0f %9.1f | %8d %9d | %7d -> %2d  %9d -> %2s" % [
				a.id, f.n, s.w, s.open, s.rooms, s.exit, s.boss, s.dead, mon.list.size(), mon.xp, hero_in, fl,
				hero_boss, str(fl + 1) if f.get("boss") != null else "-"])
			while xp >= CharData.xp_for(lvl + 1):
				lvl += 1
		for q in DB.quests:
			if int(DB.quests[q].get("act", 0)) == int(a.id):
				xp += int(DB.quests[q].get("reward", {}).get("xp", 0))
		while xp >= CharData.xp_for(lvl + 1):
			lvl += 1
		print("GEN act %d done, quests paid: hero level %d" % [a.id, lvl])
	get_tree().quit()


# What _spawn_monsters would put down on average: packs by open area and density, champions with two extra.
func _monsters(f: Dictionary, open: float) -> Dictionary:
	var pool: Array = f.get("monsters", [])
	var list := []
	var total := 0
	if pool.is_empty():
		return {"list": list, "xp": 0}
	var packs := int(open / 85.0 * float(f.get("density", 1.0)))
	var champs := 1 + (1 if int(f.n) > 1 else 0)
	for i in packs:
		var mid: String = pool[i % pool.size()]
		var md: Dictionary = DB.monster(mid)
		var pk = md.get("pack", [2, 5])
		var count := int(round((float(pk[0]) + float(pk[1])) / 2.0)) + (2 if i < champs else 0)
		for k in count:
			var ml := int(f.level) + (k % 2)
			var x := int(float(md.get("xp_mult", 1.0)) * 12.0 * pow(ml, 1.55) * (3.0 if i < champs and k == 0 else 1.0))
			list.append({"lvl": ml, "xp": x})
			total += x
	return {"list": list, "xp": total}


func _dead_ends(g: DungeonGen) -> int:
	var n := 0
	for c in g.dist:
		var k := 0
		for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
			if g.walkable(c + o):
				k += 1
		if k == 1:
			n += 1
	return n


# Builds every regular floor for real and counts what spawned.
func _real() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for a in DB.acts:
		for f in a.floors:
			if f.has("uber"):
				continue
			var before: Level = Game.level
			var t0 := Time.get_ticks_msec()
			Game.goto(int(a.id), int(f.n), "stairs_down")
			while Game.level == before or Game.level == null or Game.main.loading:
				await get_tree().process_frame
			var ms := Time.get_ticks_msec() - t0
			await get_tree().process_frame
			var lv: Level = Game.level
			var xp := 0
			var n := 0
			for m in lv.monsters:
				if m.kind != "boss":
					xp += m.xp_value
					n += 1
			var walk: int = lv.gen.dist.get(lv.gen.exit, 0)
			print("REAL %d %d | %dx%d open %d side %d | monsters %d xp %d | exit walk %d cells | build %d ms" % [a.id, f.n, lv.gen.w, lv.gen.h, lv.gen.dist.size(), lv.gen.side_rooms.size(), n, xp, walk, ms])
	get_tree().quit()


func _png(g: DungeonGen, path: String) -> void:
	var img := Image.create(g.w * 4, g.h * 4, false, Image.FORMAT_RGB8)
	var side := {}
	for r in g.side_rooms:
		for y in range(r.position.y, r.end.y):
			for x in range(r.position.x, r.end.x):
				side[Vector2i(x, y)] = true
	for y in g.h:
		for x in g.w:
			var v := g.at(x, y)
			var col := Color(0.12, 0.1, 0.09)
			if v == DungeonGen.FLOOR:
				col = Color(0.62, 0.55, 0.45) if not side.has(Vector2i(x, y)) else Color(0.45, 0.62, 0.45)
			elif v == DungeonGen.WATER:
				col = Color(0.3, 0.45, 0.65)
			img.fill_rect(Rect2i(x * 4, y * 4, 4, 4), col)
	for p in [[g.start, Color(0.2, 0.9, 0.2)], [g.exit, Color(0.9, 0.2, 0.2)], [g.boss_spot, Color(0.9, 0.2, 0.9)]]:
		if p[0].x >= 0:
			img.fill_rect(Rect2i(p[0].x * 4 - 4, p[0].y * 4 - 4, 12, 12), p[1])
	img.save_png(path)
