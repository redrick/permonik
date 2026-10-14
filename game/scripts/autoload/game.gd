extends Node

signal message(text: String, color: Color)
signal quests_changed

const SHARED_STASH := "user://saves/_shared_stash.json"
var shared_stash := Inventory.new(12, 10)
signal location_changed
signal boss_bar(name: String, ratio: float, visible: bool)

const SEALS := ["voda", "kamen", "ohen", "smrt"]

var ch := CharData.new()
var difficulty := 0
var act := 1
var floor_n := 0
var quests := {}
var flags := {}
var waypoints := {}
var known := {}
var _codex_news := []
var unlocked_difficulty := 0
var save_slot := ""
var main: Node = null
var player: Node = null
var level: Node = null
var portal := {}
var floor_loot := {}   # "difficulty:act:floor" -> {"seed": session_seed, "items": [[item dict, x, y], ...]}
var paused_ui := false
var play_time := 0.0
var session_seed := randi()
var _autosave_t := 30.0
# A release APK can't be started with command-line args; tools/android.sh run <args> writes them here.
const DEVICE_ARGS := "/storage/emulated/0/Android/data/cz.antas.permonik/files/args.txt"
var args := PackedStringArray()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	args = OS.get_cmdline_user_args()
	if OS.has_feature("android") and FileAccess.file_exists(DEVICE_ARGS):
		args.append_array(FileAccess.get_file_as_string(DEVICE_ARGS).split(" ", false))
	if args.has("--seed"):
		session_seed = int(args[args.find("--seed") + 1])
	_setup_input()
	quests_changed.connect(save)
	load_shared_stash()


var _fps_t := 5.0


func _process(delta: float) -> void:
	if args.has("--fps"):
		_fps_t -= delta
		if _fps_t <= 0.0:
			_fps_t = 5.0
			print("FPS %d" % Engine.get_frames_per_second())
	if level and not get_tree().paused:
		play_time += delta
		_autosave_t -= delta
		if _autosave_t <= 0.0:
			_autosave_t = 30.0
			save()


# Heroes save themselves (D2 style): every 30 s, on quest changes, on leaving and on closing the window.
# Loading always starts in the town of the hero's current act.
func _notification(what: int) -> void:
	if what in [NOTIFICATION_WM_CLOSE_REQUEST, NOTIFICATION_APPLICATION_PAUSED] and level:
		save()


func _setup_input() -> void:
	var keys := {
		"inventory": [KEY_I, KEY_B], "character": [KEY_C, KEY_A], "skills": [KEY_S, KEY_T], "quests": [KEY_J],
		"automap": [KEY_TAB], "pause": [KEY_ESCAPE], "show_items": [KEY_ALT], "stand": [KEY_SHIFT],
		"belt_1": [KEY_1], "belt_2": [KEY_2], "belt_3": [KEY_3], "belt_4": [KEY_4],
		"belt_5": [KEY_5], "belt_6": [KEY_6], "belt_7": [KEY_7], "belt_8": [KEY_8],
		"skill_q": [KEY_Q], "skill_w": [KEY_W], "skill_e": [KEY_E], "skill_r": [KEY_R],
		"town_portal": [KEY_P], "zoom_map": [KEY_M], "kronika": [KEY_K],
	}
	for a in keys:
		if not InputMap.has_action(a):
			InputMap.add_action(a)
		for k in keys[a]:
			var ev := InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event(a, ev)


func msg(text: String, color := Color("e8e2d4")) -> void:
	message.emit(text, color)


# Codex knowledge survives difficulty resets; keys are "<kind>:<id>" and "read:<entry>".
func learn(kind: String, id: String) -> void:
	var k := kind + ":" + id
	if id == "" or known.has(k):
		return
	known[k] = true
	for eid in DB.codex_by_ref.get(k, []):
		if not known.has("seen:" + eid):
			known["seen:" + eid] = true
			if _codex_news.is_empty():
				_flush_codex_news.call_deferred()
			_codex_news.append(eid)


func _flush_codex_news() -> void:
	if _codex_news.size() == 1:
		msg("%s: %s  (K)" % [L.t("codex_new"), L.t(DB.codex[_codex_news[0]].get("title", ""))], Color("c8b88a"))
	elif _codex_news.size() > 1:
		msg(L.t("codex_new_n", {"v": _codex_news.size()}), Color("c8b88a"))
	_codex_news.clear()


func codex_visible(eid: String) -> bool:
	var refs: Array = DB.codex_refs.get(eid, [])
	if refs.is_empty():
		return true
	for k in refs:
		if known.has(k):
			return true
	return false


func seal_count() -> int:
	var n := 0
	for s in SEALS:
		if flags.get("seal_" + s, false):
			n += 1
	return n


func mlvl_base(lv: int) -> int:
	return mini(99, lv + [0, 30, 60][clampi(difficulty, 0, 2)])


# ---------------------------------------------------------------- quests
func quest_state(qid: String) -> String:
	return str(quests.get(qid, {}).get("state", "none"))


func quest_step(qid: String) -> String:
	return str(quests.get(qid, {}).get("step", ""))


func quest_start(qid: String) -> void:
	var q: Dictionary = DB.quests.get(qid, {})
	if q.is_empty() or quest_state(qid) != "none":
		return
	var steps: Array = q.get("steps", [])
	quests[qid] = {"state": "active", "step": steps[0].id if steps.size() > 0 else ""}
	learn("quest", qid)
	msg("%s: %s" % [L.t("quest_new"), L.t(q.get("name", qid))], Color("e9c46a"))
	Sfx.play("quest_done", 0.5)
	quests_changed.emit()
	_check_pick_goals(qid)


func quest_set_step(qid: String, step: String) -> void:
	if quest_state(qid) == "none":
		quests[qid] = {"state": "active", "step": step}
	elif quest_state(qid) == "active":
		quests[qid].step = step
	quests_changed.emit()


func quest_advance(qid: String) -> void:
	var q: Dictionary = DB.quests.get(qid, {})
	var steps: Array = q.get("steps", [])
	var cur := quest_step(qid)
	for i in steps.size():
		if steps[i].id == cur:
			if i + 1 < steps.size():
				quests[qid].step = steps[i + 1].id
				quests_changed.emit()
				_check_pick_goals(qid)
			else:
				quest_done(qid)
			return
	quest_done(qid)


func quest_done(qid: String) -> void:
	if quest_state(qid) == "done":
		return
	quests[qid] = {"state": "done", "step": ""}
	var q: Dictionary = DB.quests.get(qid, {})
	var r: Dictionary = q.get("reward", {})
	if r.has("xp"):
		ch.add_xp(int(r.xp) * (1 + difficulty * 3))
	if r.has("gold"):
		ch.gold += int(r.gold) * (1 + difficulty * 2)
	ch.skill_points += int(r.get("skill_points", 0))
	ch.stat_points += int(r.get("stat_points", 0))
	if r.has("item"):
		give_item(str(r.item))
	for id in r.get("items", []):
		give_item(str(id))
	msg("%s: %s" % [L.t("quest_done"), L.t(q.get("name", qid))], Color("e9c46a"))
	Sfx.play("quest_done")
	quests_changed.emit()
	ch.changed.emit()


# ---------------------------------------------------------------- where to go next (tracker, map, marks)
# The dialog an NPC would open now: the first entry whose conditions hold.
func dialog_entry(nid: String) -> Dictionary:
	for e in DB.dialog.get(nid, []):
		var ok := true
		for c in e.get("if", []):
			if not cond(str(c)):
				ok = false
				break
		if ok:
			return e
	return {}


# "new" / "new_side": talking now starts a quest; "turnin": talking now moves an active quest on.
func npc_marker(nid: String) -> String:
	for qid in quests:
		if _cur_goal(qid).get("talk", "") == nid:
			return "turnin"
	for a in dialog_entry(nid).get("do", []):
		var p := str(a).split(":")
		if p[0] == "quest_start" and p.size() > 1 and quest_state(p[1]) == "none":
			return "new" if bool(DB.quests.get(p[1], {}).get("main", false)) else "new_side"
		if p[0] in ["quest_done", "quest_step"] and p.size() > 1 and quest_state(p[1]) == "active":
			return "turnin"
	return ""


# Where a goal is: {act, floors, what, id}. what = reach / boss / hunt / item / prop / npc.
func goal_place(qid: String) -> Dictionary:
	var g := _cur_goal(qid)
	var qa := int(DB.quests.get(qid, {}).get("act", act))
	if g.has("reach"):
		var p := str(g.reach).trim_prefix("act").split("_floor")
		if p.size() == 2:
			return {"act": int(p[0]), "floors": [int(p[1])], "what": "reach", "id": ""}
	if g.has("talk"):
		return {"act": qa, "floors": [0], "what": "npc", "id": str(g.talk)}
	for key in ["kill", "pick", "use"]:
		if not g.has(key):
			continue
		var id := str(g[key])
		var floors := []
		var what: String = {"kill": "hunt", "pick": "item", "use": "prop"}[key]
		for f in DB.act(qa).get("floors", []):
			if key == "kill" and str(f.get("boss", "")) == id:
				return {"act": qa, "floors": [int(f.n)], "what": "boss", "id": id}
			if key == "kill" and id in f.get("monsters", []):
				floors.append(int(f.n))
			if key != "kill" and id in f.get("quest_props", []):
				floors.append(int(f.n))
		if not floors.is_empty():
			return {"act": qa, "floors": floors, "what": what, "id": id}
		return {"act": qa, "floors": [], "what": what, "id": id}
	return {}


func place_text(pl: Dictionary) -> String:
	if pl.is_empty():
		return ""
	var a := int(pl.act)
	if pl.what == "npc":
		return "%s · %s" % [L.t(DB.act(a).get("town", {}).get("name", "")), L.t(DB.npcs.get(pl.id, {}).get("name", pl.id))]
	var fl: Array = pl.floors
	if fl.is_empty():
		return ""
	var mine := L.t(DB.act(a).get("dungeon", {}).get("name", ""))
	if fl.size() == 1:
		return "%s · %s" % [mine, L.t(DB.floor_def(a, int(fl[0])).get("name", ""))]
	return "%s · %s %d–%d" % [mine, L.t("floor"), int(fl.min()), int(fl.max())]


# The quests the HUD shows: the act's main quest first, then the side quests.
func tracked_quests() -> Array:
	var out := []
	for qid in quests:
		if quest_state(qid) != "active":
			continue
		var q: Dictionary = DB.quests.get(qid, {})
		var step_text := ""
		for st in q.get("steps", []):
			if st.id == quest_step(qid):
				step_text = L.t(st.get("text", ""))
		var g := _cur_goal(qid)
		var need := int(g.get("count", 1))
		out.append({"qid": qid, "main": bool(q.get("main", false)), "name": L.t(q.get("name", qid)), "text": step_text,
			"where": place_text(goal_place(qid)), "n": int(quests[qid].get("n", 0)) if need > 1 else -1, "count": need,
			"act": int(q.get("act", 0))})
	out.sort_custom(func(x, y): return x.main and not y.main or (x.main == y.main and x.act > y.act))
	return out


# The tracker's checkbox: whether a quest's targets are marked on the map.
func quest_on_map(qid: String) -> bool:
	return not flags.has("map_off:" + qid)


func set_quest_on_map(qid: String, on: bool) -> void:
	if on:
		flags.erase("map_off:" + qid)
	else:
		flags["map_off:" + qid] = true


func _cur_goal(qid: String) -> Dictionary:
	if quest_state(qid) != "active":
		return {}
	for s in DB.quests.get(qid, {}).get("steps", []):
		if s.id == quest_step(qid):
			return s.get("goal", {})
	return {}


func on_event(key: String, value: String) -> void:
	if key == "talk":
		return
	for qid in quests.keys():
		var g := _cur_goal(qid)
		if str(g.get(key, "")) != value:
			continue
		if key == "pick":
			_check_pick_goals(qid)
			continue
		var need := int(g.get("count", 1))
		if need > 1:
			quests[qid]["n"] = int(quests[qid].get("n", 0)) + 1
			if int(quests[qid].n) < need:
				msg("%s: %d / %d" % [L.t(DB.quests[qid].get("name", qid)), int(quests[qid].n), need], Color("c8b88a"))
				continue
		quest_advance(qid)


func _check_pick_goals(qid: String) -> void:
	var g := _cur_goal(qid)
	if g.has("pick") and ch.inv.count(str(g.pick)) >= int(g.get("count", 1)):
		quest_advance(qid)


func give_item(id: String) -> void:
	var it: Item = null
	if DB.uniques.has(id):
		it = Loot.unique_item(id, mlvl_base(ch.level))
	elif DB.items.has(id):
		it = Item.create(id, ch.level)
	if it == null:
		return
	if id == "permonikuv_kahan":
		var old: Item = ch.equip.get("lamp", null)
		ch.equip["lamp"] = it
		if old:
			ch.pickup(old)
		ch.recalc()
		ch.changed.emit()
		msg(it.display_name(), it.color())
		return
	if not ch.pickup(it) and player:
		level.drop_item(it, player.global_position)
	msg(it.display_name(), it.color())


# ---------------------------------------------------------------- conditions / actions (dialog)
func cond(c: String) -> bool:
	if c == "always" or c == "":
		return true
	var neg := c.begins_with("!")
	if neg:
		c = c.substr(1)
	var p := c.split(":")
	var r := false
	match p[0]:
		"quest":
			if p.size() >= 3:
				if p[2].begins_with("step="):
					r = quest_state(p[1]) == "active" and quest_step(p[1]) == p[2].substr(5)
				else:
					r = quest_state(p[1]) == p[2]
		"act":
			r = act == int(p[1])
		"flag":
			r = flags.get(p[1], false)
		"class":
			r = ch.class_id == p[1]
		"has":
			r = ch.inv.count(p[1]) > 0
		"difficulty":
			r = difficulty == int(p[1])
		"seals":
			r = seal_count() >= int(p[1])
	return r != neg


func action(a: String) -> void:
	var p := a.split(":")
	match p[0]:
		"quest_start":
			quest_start(p[1])
		"quest_step":
			quest_set_step(p[1], p[2])
		"quest_done":
			quest_done(p[1])
		"flag":
			flags[p[1]] = true
		"give":
			give_item(p[1])
		"take":
			ch.inv.take(p[1], int(p[2]) if p.size() > 2 else 1)
		"gold":
			ch.gold += int(p[1])
		"xp":
			ch.add_xp(int(p[1]))
		"heal":
			ch.hp = ch.d.hp_max
			ch.mana = ch.d.mana_max
			Sfx.play("heal")
		"stat_points":
			ch.stat_points += int(p[1])
		"skill_points":
			ch.skill_points += int(p[1])
		"slide":
			if main:
				if p[1] == "dlc_tease":
					main.play_slides(p[1], func(): main.show_credits())
				else:
					main.play_slides(p[1])
		"next_act":
			next_act()
		"respec":
			ch.respec()
	ch.changed.emit()


# ---------------------------------------------------------------- travel
func waypoint_key(a: int, f: int) -> String:
	return "%d:%d" % [a, f]


func goto(a: int, f: int, arrive := "start") -> void:
	act = a
	floor_n = f
	if f > 0 and not DB.floor_def(a, f).has("uber"):
		waypoints[waypoint_key(a, f)] = true
		on_event("reach", "act%d_floor%d" % [a, f])
		learn("floor", "act%d_floor%d" % [a, f])
	else:
		learn("town", str(DB.act(a).get("town", {}).get("id", "")))
	if main:
		main.load_location(a, f, arrive)
	location_changed.emit()


func next_act() -> void:
	var na := act + 1
	if DB.act(na).is_empty():
		return
	var intro = DB.act(na).get("intro", null)
	act = na
	floor_n = 0
	save()
	if main:
		main.play_slides(str(intro) if intro else "", func(): goto(na, 0, "start"))


func finish_game() -> void:
	unlocked_difficulty = maxi(unlocked_difficulty, mini(difficulty + 1, 2))
	flags["game_finished"] = true
	save()
	if main:
		main.play_slides("final", func(): goto(act, 0, "start"))


func start_next_difficulty() -> void:
	difficulty = mini(difficulty + 1, 2)
	quests = {}
	flags = {}
	waypoints = {}
	floor_loot = {}
	act = 1
	ch.recalc()
	save()
	goto(1, 0, "start")


# ---------------------------------------------------------------- save / load
func new_game(cid: String, nm: String, persist := true) -> void:
	ch = CharData.new()
	ch.start_new(cid, nm)
	difficulty = 0
	unlocked_difficulty = 0
	act = 1
	floor_n = 0
	quests = {}
	flags = {}
	waypoints = {}
	portal = {}
	floor_loot = {}
	play_time = 0.0
	known = {}
	save_slot = "%s_%d" % [cid, Time.get_unix_time_from_system()] if persist else ""
	learn("class", cid)
	save()


func save() -> void:
	if save_slot == "":
		return
	if level and is_instance_valid(level):
		level.stash_loot()
	DirAccess.make_dir_recursive_absolute("user://saves")
	var data := {"v": 1, "char": ch.to_dict(), "difficulty": difficulty, "act": act, "quests": quests,
		"flags": flags, "waypoints": waypoints, "known": known, "unlocked": unlocked_difficulty, "time": play_time, "floor_loot": floor_loot,
		"saved_at": Time.get_datetime_string_from_system()}
	var f := FileAccess.open("user://saves/%s.json" % save_slot, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(data))
	save_shared_stash()


# One stash every hero can reach, kept beside the hero files.
func save_shared_stash() -> void:
	DirAccess.make_dir_recursive_absolute("user://saves")
	var f := FileAccess.open(SHARED_STASH, FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify(shared_stash.to_array()))


func load_shared_stash() -> void:
	if not FileAccess.file_exists(SHARED_STASH):
		return
	var d = JSON.parse_string(FileAccess.get_file_as_string(SHARED_STASH))
	if d is Array:
		shared_stash.load_array(d)


func load_game(slot: String) -> bool:
	var path := "user://saves/%s.json" % slot
	if not FileAccess.file_exists(path):
		return false
	var data = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not data is Dictionary:
		return false
	save_slot = slot
	ch = CharData.new()
	difficulty = int(data.get("difficulty", 0))
	act = int(data.get("act", 1))
	quests = data.get("quests", {})
	flags = data.get("flags", {})
	waypoints = data.get("waypoints", {})
	known = data.get("known", {})
	floor_loot = data.get("floor_loot", {})
	unlocked_difficulty = int(data.get("unlocked", 0))
	play_time = float(data.get("time", 0.0))
	ch.from_dict(data.get("char", {}))
	learn("class", ch.class_id)
	floor_n = 0
	portal = {}
	return true


func list_saves() -> Array:
	var out := []
	var da := DirAccess.open("user://saves")
	if da == null:
		return out
	for fn in da.get_files():
		if not fn.ends_with(".json") or fn.begins_with("_"):
			continue
		var data = JSON.parse_string(FileAccess.get_file_as_string("user://saves/" + fn))
		if data is Dictionary:
			var c: Dictionary = data.get("char", {})
			out.append({"slot": fn.get_basename(), "name": c.get("name", "?"), "class": c.get("class", ""),
				"level": c.get("level", 1), "act": data.get("act", 1), "difficulty": data.get("difficulty", 0),
				"saved_at": data.get("saved_at", ""), "gear": HeroLook.gear_from_equip(c.get("equip", {}))})
	out.sort_custom(func(a, b): return a.saved_at > b.saved_at)
	return out


func delete_save(slot: String) -> void:
	DirAccess.remove_absolute("user://saves/%s.json" % slot)
