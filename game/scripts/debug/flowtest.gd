extends Node

# Flow test: floors keep their layout, kills, opened props and explored cells across town trips in one
# session and change with a new one; quest items stop dropping once their quest is past them; a skill
# pressed mid-swing fires as soon as the swing allows; the skip label ends slides.
# Run: godot --headless --path game -- --quick --flowtest --class vedma --act 1 --floor 1
var step := 0
var wait := 0.0
var fails := 0
var lvl: Level
var snap := {}


func _ok(cond: bool, what: String) -> void:
	print("FLOW %s %s" % ["ok  " if cond else "FAIL", what])
	if not cond:
		fails += 1


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS


func _signature(lv: Level) -> String:
	var parts := []
	for p in lv.props:
		if is_instance_valid(p) and p.id != "portal":
			parts.append("%s@%d,%d" % [p.id, p.cell.x, p.cell.y])
	return "|".join(parts)


func _goto(a: int, f: int, arrive: String) -> void:
	lvl = Game.level
	Game.goto(a, f, arrive)
	wait = 0.2


func _arrived() -> bool:
	return Game.level != null and Game.level != lvl and is_instance_valid(Game.level) and not Game.main.loading


func _process(delta: float) -> void:
	wait -= delta
	if wait > 0.0:
		return
	var lv: Level = Game.level
	match step:
		0:
			if lv == null or Game.main.loading:
				return
			snap.a = Game.act
			snap.f = Game.floor_n
			snap.sig = _signature(lv)
			snap.monsters = lv.monsters.size()
			var killed := 0
			for m in lv.monsters.duplicate():
				if killed < 3 and m.kind != "boss":
					m.take_damage(m.hp_max * 10.0, "physical", lv.player, {"always_hit": true})
					killed += 1
			snap.killed = killed
			for p in lv.props:
				if p.interact == "chest" and not snap.has("chest"):
					lv._use_prop(lv.player, p)
					snap.chest = lv._prop_key(p)
				elif p.interact == "break" and not snap.has("barrel"):
					lv._break_prop(p)
					snap.barrel = lv._prop_key(p)
			lv.player.global_position = lv.cell_center(lv.gen.exit)
			lv._explore()
			snap.explored = lv.explored.count(1)
			wait = 0.3
			step = 1
		1:
			_goto(snap.a, 0, "portal")
			step = 2
		2:
			if not _arrived():
				return
			_goto(snap.a, snap.f, "stairs_down")
			step = 3
		3:
			if not _arrived():
				return
			_ok(_signature(lv) == snap.sig, "same props after a town trip")
			_ok(lv.monsters.size() == snap.monsters - snap.killed, "killed monsters stay dead (%d -> %d)" % [snap.monsters, lv.monsters.size()])
			var chest_open := false
			var barrel_broken := false
			for p in lv.props:
				if lv._prop_key(p) == snap.get("chest", ""):
					chest_open = p.used
				if lv._prop_key(p) == snap.get("barrel", ""):
					barrel_broken = p.used and (not p.has_node("Body") or p.get_node("Body").is_queued_for_deletion())
			_ok(chest_open or not snap.has("chest"), "opened chest stays open")
			_ok(barrel_broken or not snap.has("barrel"), "broken barrel stays broken")
			_ok(lv.explored.count(1) >= snap.explored, "explored cells kept (%d >= %d)" % [lv.explored.count(1), snap.explored])
			Game.new_session()
			_goto(snap.a, snap.f, "stairs_down")
			step = 4
		4:
			if not _arrived():
				return
			_ok(_signature(lv) != snap.sig, "a new session draws a new floor")
			_ok(lv.explored.count(1) < 200, "a new session starts unexplored")
			Game.quests["srdce_zvonu"] = {"state": "done", "step": ""}
			_goto(1, 3, "stairs_down")
			step = 5
		5:
			if not _arrived():
				return
			_ok(_quest_items(lv, "srdce_zvonu") == 0, "finished quest's item no longer lies on its floor")
			Game.quests.erase("srdce_zvonu")
			_goto(1, 0, "portal")
			step = 6
		6:
			if not _arrived():
				return
			Game.floor_state.clear()
			_goto(1, 3, "stairs_down")
			step = 7
		7:
			if not _arrived():
				return
			_ok(_quest_items(lv, "srdce_zvonu") == 1, "quest not started yet: its item lies on the floor")
			for g in lv.ground_items.duplicate():
				if g.item.base_id == "srdce_zvonu":
					lv._pickup(g)
			Game.ch.inv.take("srdce_zvonu")
			Game.floor_state.clear()
			_goto(1, 3, "stairs_down")
			step = 8
		8:
			if not _arrived():
				return
			_ok(_quest_items(lv, "srdce_zvonu") == 0, "a taken quest item is not laid out again")
			Game.give_item("zrcadlo_strep")
			Game.quests["zrcadla_v_sevcine"] = {"state": "active", "step": "report"}
			Game.quest_done("zrcadla_v_sevcine")
			_ok(Game.ch.inv.count("zrcadlo_strep") == 0, "spent quest item leaves the bag on quest done")
			step = 9
		9:
			_skill_setup(lv)
			step = 10
		10:
			_skill_check(lv)
			snap.skipped = false
			Game.main.ui.play_slides(DB.slides.values()[0], func(): snap.skipped = true)
			wait = 0.3
			step = 11
		11:
			var skip: Label = null
			for c in Game.main.ui.slides.get_children():
				if c is Label and c.mouse_filter == Control.MOUSE_FILTER_STOP:
					skip = c
			_ok(skip != null, "slides show a tappable skip label")
			if skip:
				var e := InputEventMouseButton.new()
				e.button_index = MOUSE_BUTTON_LEFT
				e.pressed = true
				skip.gui_input.emit(e)
			wait = 0.8
			step = 12
		12:
			_ok(snap.skipped and Game.main.ui.slides == null, "tapping skip ends the slides")
			snap.dir = Game.save_dir
			Game.save_dir = OS.get_cache_dir().path_join("permonik_flowtest")
			Game.save_slot = "flow"
			Game.save()
			snap.stash_t = FileAccess.get_modified_time(Game.save_dir.path_join(Game.STASH_FILE))
			wait = 1.1
			step = 13
		13:
			var hero := Game.save_dir.path_join("flow.json")
			var t0 := FileAccess.get_modified_time(hero)
			Game.save()
			_ok(Game.save_slot == "flow" and FileAccess.get_modified_time(hero) > t0, "a second save writes the hero")
			_ok(FileAccess.get_modified_time(Game.save_dir.path_join(Game.STASH_FILE)) == snap.stash_t, "an unchanged stash is not rewritten")
			_ok(FileAccess.get_file_as_string(hero).begins_with("{\"v\":1,\"w\":"), "the write token heads the save")
			var d: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(hero))
			d.w = "elsewhere"
			var f := FileAccess.open(hero, FileAccess.WRITE)
			f.store_string(JSON.stringify(d))
			f.close()
			wait = 1.1
			step = 14
		14:
			Game.save()
			_ok(Game.save_slot == "", "a save made on another device is not overwritten")
			for fn in DirAccess.get_files_at(Game.save_dir):
				DirAccess.remove_absolute(Game.save_dir.path_join(fn))
			DirAccess.remove_absolute(Game.save_dir)
			Game.save_dir = snap.dir
			print("FLOW DONE fails=%d" % fails)
			get_tree().quit()


func _quest_items(lv: Level, id: String) -> int:
	var n := 0
	for g in lv.ground_items:
		if is_instance_valid(g) and g.item.base_id == id:
			n += 1
	return n


var sid := ""
var t_press := 0.0


func _skill_setup(lv: Level) -> void:
	var p: Player = lv.player
	for want in ["projectile", "melee", "melee_arc", "stomp", "nova"]:
		for tr in Game.ch.cls().trees:
			for s in tr.skills:
				if sid == "" and str(DB.skill(s).get("type", "")) == want and DB.skill(s).get("requires", "") == "":
					sid = s
	Game.ch.skills[sid] = 1
	Game.ch.recalc()
	p.invuln = 999.0
	for m in lv.monsters.duplicate():
		m.queue_free()
	lv.monsters.clear()
	var m := lv.spawn_monster("kostlivy_havir", lv.cell_center(lv._nearest_open(lv.to_cell(p.global_position + Vector2(70, 0)))), 1)
	m.hp_max = 1e6
	m.hp = 1e6
	p.global_position = m.global_position - Vector2(60, 0)
	p.basic_attack(m, m.global_position)
	Game.ch.mana = Game.ch.d.mana_max
	snap.mana = Game.ch.mana
	p.use_skill(sid, m.center_pos())
	_ok(not p.queued.is_empty(), "skill pressed mid-swing is queued (%s)" % sid)
	t_press = Time.get_ticks_msec()
	wait = 1.2


func _skill_check(lv: Level) -> void:
	_ok(Game.ch.mana < snap.mana, "queued skill fired after the swing (mana %d -> %d)" % [snap.mana, Game.ch.mana])
