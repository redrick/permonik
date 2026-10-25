extends Node

signal message(text: String, color: Color)
signal quests_changed
signal storage_changed

const DEFAULT_SAVE_DIR := "user://saves"
const STORAGE_PERMISSION := "android.permission.MANAGE_EXTERNAL_STORAGE"
const STASH_FILE := "_shared_stash.json"
# Heroes and the shared stash live here; settings.cfg can point it at a synced folder shared by several devices.
var save_dir := DEFAULT_SAVE_DIR
# Write token of the hero file as this device last loaded or wrote it; a different one on disk = another device played.
var _hero_w := ""
var _stash_text := ""
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
# What the hero changed on each floor this session (explored cells, killed monsters, opened props). Not saved:
# the floors are drawn anew when a hero is loaded from the menu.
var floor_state := {}
var paused_ui := false
var play_time := 0.0
var session_seed := randi()
var _fixed_seed := false
var _autosave_t := 30.0
var _autosave_wait := 0.0
# A release APK can't be started with command-line args; tools/android.sh run <args> writes them here.
const DEVICE_ARGS := "/storage/emulated/0/Android/data/cz.antas.permonik/files/dev/args.txt"
var args := PackedStringArray()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	args = OS.get_cmdline_user_args()
	if OS.has_feature("android") and FileAccess.file_exists(DEVICE_ARGS):
		args.append_array(FileAccess.get_file_as_string(DEVICE_ARGS).strip_edges().split(" ", false))
	if args.has("--seed"):
		session_seed = int(args[args.find("--seed") + 1])
		_fixed_seed = true
	_setup_input()
	quests_changed.connect(func(): _autosave_t = minf(_autosave_t, 1.0))
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	save_dir = str(cfg.get_value("main", "save_dir", DEFAULT_SAVE_DIR))
	if needs_storage_permission():
		OS.request_permission(STORAGE_PERMISSION)
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
			# a save reads and writes whole files; not in the middle of a fight unless it has waited long
			_autosave_wait += 1.0
			if _autosave_wait < 30.0 and _in_fight():
				_autosave_t = 1.0
				return
			_autosave_t = 30.0
			_autosave_wait = 0.0
			save()


func _in_fight() -> bool:
	if player == null or not is_instance_valid(player) or level.is_town:
		return false
	for m in level.monsters:
		if m.aggro and not m.dead and m.global_position.distance_to(player.global_position) < 700.0:
			return true
	return false


# Heroes save themselves (D2 style): every 30 s, on quest changes, on leaving and on closing the window.
# Loading always starts in the town of the hero's current act.
func _notification(what: int) -> void:
	if what in [NOTIFICATION_WM_CLOSE_REQUEST, NOTIFICATION_APPLICATION_PAUSED] and level:
		save()
	elif what in [NOTIFICATION_APPLICATION_RESUMED, NOTIFICATION_APPLICATION_FOCUS_IN] and not level:
		load_shared_stash()
		storage_changed.emit()


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


# The collection (D2's holy grail): every unique, set piece and word ever held, kept across difficulties.
func note_found(it: Item) -> void:
	if it == null or not it.identified:
		return
	var keys := []
	if it.rarity == Item.UNIQUE and it.unique_id != "":
		keys.append("grail:u:" + it.unique_id)
	elif it.rarity == Item.SET and it.set_id != "":
		keys.append("grail:s:" + it.set_id)
	if it.word != "":
		keys.append("grail:w:" + it.word)
	for k in keys:
		if not known.has(k):
			known[k] = true
			msg(L.t({"cs": "Nový kus do sbírky: %s  (K)", "en": "New for your collection: %s  (K)"}) % it.display_name(), Item.COL_UNIQUE)


# The peddler's one item: a new one each hero level, gone once bought.
func peddler_item() -> Item:
	var p: Dictionary = flags.get("peddler", {})
	if int(p.get("lvl", -1)) != ch.level:
		p = {"lvl": ch.level, "item": Loot.peddler_item(ch.level).to_dict(), "seen": false}
		flags["peddler"] = p
	return Item.from_dict(p.item) if p.has("item") else null


func peddler_seen() -> bool:
	peddler_item()
	return bool(flags.peddler.get("seen", false))


func note_found_all() -> void:
	for it in ch.inv.items:
		note_found(it)
	for sl in ch.equip:
		note_found(ch.equip[sl])


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
	if r.has("service") and Forge.SERVICES.has(str(r.service)):
		flags[Forge.service_flag(str(r.service))] = true
		msg(L.t({"cs": "Kovář ti teď jednou udělá: %s", "en": "A smith will now do this for you once: %s"}) % L.t(Forge.SERVICES[str(r.service)].name), Item.COL_UNIQUE)
	drop_spent_quest_items()
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


# Whether a floor still lays out its quest item: a quest of that act has yet to pick it up, and this
# floor's copy hasn't been taken already. Quests that are done or past that step don't want it.
func quest_item_wanted(id: String, a: int, f: int) -> bool:
	if flags.has("took:%d:%d:%s" % [a, f, id]):
		return false
	var own := []
	var other := []
	for qid in DB.quests:
		var q: Dictionary = DB.quests[qid]
		var steps: Array = q.get("steps", [])
		for i in steps.size():
			if str(steps[i].get("goal", {}).get("pick", "")) == id:
				(own if int(q.get("act", a)) == a else other).append([qid, i, int(steps[i].goal.get("count", 1))])
	for e in own if not own.is_empty() else other:
		var st := quest_state(e[0])
		if st == "done":
			continue
		if st == "active":
			var cur := -1
			var steps: Array = DB.quests[e[0]].get("steps", [])
			for i in steps.size():
				if steps[i].id == quest_step(e[0]):
					cur = i
			if cur > e[1]:
				continue
		if ch.inv.count(id) < e[2]:
			return true
	return false


# Quest items marked "until" leave the bags once all those quests are done; nothing else uses them then.
func drop_spent_quest_items() -> void:
	for inv in [ch.inv, ch.stash]:
		for it in inv.items.duplicate():
			var until: Array = it.base().get("until", [])
			if until.is_empty():
				continue
			var spent := true
			for qid in until:
				if quest_state(str(qid)) != "done":
					spent = false
			if spent:
				inv.remove(it)


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
					main.play_slides("credits")
					main.play_slides(p[1], func(): main.show_menu())
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
	if main and level:
		main.play_slides("final", func(): goto(act, 0, "start"))


func start_next_difficulty() -> void:
	difficulty = mini(difficulty + 1, 2)
	quests = {}
	flags = {}
	waypoints = {}
	floor_loot = {}
	floor_state = {}
	act = 1
	ch.recalc()
	save()
	goto(1, 0, "start")


# ---------------------------------------------------------------- save / load
# Each time a hero is taken from the menu the mines are drawn anew; within one sitting they stay put.
func new_session() -> void:
	if not _fixed_seed:
		session_seed = randi()
	floor_state = {}


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
	new_session()
	play_time = 0.0
	known = {}
	save_slot = "%s_%d" % [cid, Time.get_unix_time_from_system()] if persist else ""
	_hero_w = ""
	load_shared_stash()
	learn("class", cid)
	save()


func save() -> void:
	if save_slot == "":
		return
	var path := _hero_path(save_slot)
	if FileAccess.file_exists(path) and _written_by(path) != _hero_w:
			save_slot = ""
			message.emit(UiTheme.t("save_newer_elsewhere"), UiTheme.RED)
			if level and main:
				main.save_and_menu.call_deferred()
			return
	if level and is_instance_valid(level):
		level.stash_loot()
	DirAccess.make_dir_recursive_absolute(save_dir)
	_hero_w = "%x%x" % [Time.get_ticks_usec(), randi()]
	var data := {"v": 1, "w": _hero_w, "char": ch.to_dict(), "difficulty": difficulty, "act": act, "quests": quests,
		"flags": flags, "waypoints": waypoints, "known": known, "unlocked": unlocked_difficulty, "time": play_time, "floor_loot": floor_loot,
		"saved_at": Time.get_datetime_string_from_system()}
	_write(path, JSON.stringify(data, "", false))
	save_shared_stash()


# Write to a temp file and swap it in, so a sync client never picks up half a save.
# The write token sits at the start of every save, so reading a few bytes is enough.
func _written_by(path: String) -> String:
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return ""
	var head := f.get_buffer(64).get_string_from_utf8()
	var i := head.find("\"w\":\"")
	if i >= 0 and head.find("\"", i + 5) > 0:
		return head.substr(i + 5, head.find("\"", i + 5) - i - 5)
	var disk = JSON.parse_string(FileAccess.get_file_as_string(path))
	return str(disk.get("w", "")) if disk is Dictionary else _hero_w


func _write(path: String, text: String) -> bool:
	var f := FileAccess.open(path + ".tmp", FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(text)
	f.close()
	return DirAccess.rename_absolute(path + ".tmp", path) == OK


func _hero_path(slot: String) -> String:
	return save_dir.path_join(slot + ".json")


# One stash every hero can reach, kept beside the hero files.
func save_shared_stash() -> void:
	var text := JSON.stringify(shared_stash.to_array())
	var path := save_dir.path_join(STASH_FILE)
	if text == _stash_text and FileAccess.file_exists(path):
		return
	DirAccess.make_dir_recursive_absolute(save_dir)
	if _write(path, text):
		_stash_text = text


func load_shared_stash() -> void:
	_stash_text = ""
	var d = _read_json(save_dir.path_join(STASH_FILE))
	shared_stash.load_array(d if d is Array else [])


func _read_json(path: String) -> Variant:
	if not FileAccess.file_exists(path):
		return null
	return JSON.parse_string(FileAccess.get_file_as_string(path))


func needs_storage_permission(dir := save_dir) -> bool:
	return OS.has_feature("android") and not dir.begins_with("user://") \
		and not OS.get_granted_permissions().has(STORAGE_PERMISSION)


# Moves every hero and the shared stash into dir and saves there from now on. A hero already in dir
# (synced from another device) keeps whichever copy was saved later; two shared stashes are merged.
# Returns the number of files moved, or -1 when dir can't be written.
func set_save_dir(dir: String) -> int:
	if dir != DEFAULT_SAVE_DIR:
		dir = dir.trim_suffix("/")
	if dir == save_dir:
		return 0
	DirAccess.make_dir_recursive_absolute(dir)
	var probe := dir.path_join(".permonik_probe")
	var pf := FileAccess.open(probe, FileAccess.WRITE)
	if pf == null:
		return -1
	pf.close()
	DirAccess.remove_absolute(probe)
	if level:
		save()
	var moved := 0
	var da := DirAccess.open(save_dir)
	if da:
		for fn in da.get_files():
			if not fn.ends_with(".json"):
				continue
			var src := save_dir.path_join(fn)
			var dst := dir.path_join(fn)
			var ok := true
			if fn == STASH_FILE:
				ok = _merge_stash(src, dst)
			elif not FileAccess.file_exists(dst) or _saved_at(src) > _saved_at(dst):
				ok = DirAccess.copy_absolute(src, dst) == OK
			if ok:
				DirAccess.remove_absolute(src)
				moved += 1
	save_dir = dir
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	cfg.set_value("main", "save_dir", dir)
	cfg.save("user://settings.cfg")
	load_shared_stash()
	storage_changed.emit()
	return moved


func _saved_at(path: String) -> String:
	var d = _read_json(path)
	return str(d.get("saved_at", "")) if d is Dictionary else ""


func _merge_stash(src: String, dst: String) -> bool:
	var ours = _read_json(src)
	var theirs = _read_json(dst)
	if not theirs is Array:
		return DirAccess.copy_absolute(src, dst) == OK
	var inv := Inventory.new(shared_stash.w, shared_stash.h)
	inv.load_array(theirs)
	var left := []
	for d in ours if ours is Array else []:
		var it := Item.from_dict(d)
		if not inv.add(it):
			left.append(d)
	if not left.is_empty():
		_write(dst.get_basename() + "_left_%d.json" % Time.get_unix_time_from_system(), JSON.stringify(left))
	return _write(dst, JSON.stringify(inv.to_array()))


func load_game(slot: String) -> bool:
	var path := _hero_path(slot)
	if not FileAccess.file_exists(path):
		return false
	var data = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not data is Dictionary:
		return false
	save_slot = slot
	_hero_w = str(data.get("w", ""))
	load_shared_stash()
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
	drop_spent_quest_items()
	learn("class", ch.class_id)
	floor_n = 0
	portal = {}
	new_session()
	return true


func list_saves() -> Array:
	var out := []
	var da := DirAccess.open(save_dir)
	if da == null:
		return out
	for fn in da.get_files():
		if not fn.ends_with(".json") or fn.begins_with("_"):
			continue
		var data = _read_json(save_dir.path_join(fn))
		if data is Dictionary:
			var c: Dictionary = data.get("char", {})
			out.append({"slot": fn.get_basename(), "name": c.get("name", "?"), "class": c.get("class", ""),
				"level": c.get("level", 1), "act": data.get("act", 1), "difficulty": data.get("difficulty", 0),
				"saved_at": data.get("saved_at", ""), "gear": HeroLook.gear_from_equip(c.get("equip", {}))})
	out.sort_custom(func(a, b): return a.saved_at > b.saved_at)
	return out


func delete_save(slot: String) -> void:
	DirAccess.remove_absolute(_hero_path(slot))
