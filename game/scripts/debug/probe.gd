extends Node

# Melee probe: surround the hero with monsters, hold attack on the nearest one, count kills and deaths.
var args := OS.get_cmdline_user_args()
var t := 0.0
var kills := 0
var started := false
var mons: Array = []
var _click_t := 0.5
var clicks := 0
var misclicks := 0


func _arg(k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func _process(delta: float) -> void:
	var p: Player = Game.player
	var lv: Level = Game.level
	if p == null or lv == null:
		return
	if not started:
		started = true
		var pl := int(_arg("--plvl", "1"))
		Game.ch.level = pl
		var base: Dictionary = DB.classes[Game.ch.class_id].base
		var main_stat := "sila"
		for st in ["sila", "obratnost", "magie"]:
			if int(base[st]) > int(base[main_stat]):
				main_stat = st
		Game.ch.alloc = {main_stat: 3 * (pl - 1), "vitalita": 2 * (pl - 1)}
		for ai in _arg("--armor", "").split(",", false):
			var it := Item.create(ai, pl)
			Game.ch.equip[it.slot()] = it
		if args.has("--weapon"):
			Game.ch.equip["weapon"] = Item.create(_arg("--weapon", ""), pl)
		Game.ch.recalc()
		Game.ch.hp = Game.ch.d.hp_max
		p.hp = Game.ch.hp
		p.hp_max = Game.ch.d.hp_max
		for m in lv.monsters.duplicate():
			m.queue_free()
		lv.monsters.clear()
		var n := int(_arg("--n", "6"))
		for i in n:
			var pos := p.global_position + Vector2.RIGHT.rotated(TAU * i / n) * 90.0
			var m := lv.spawn_monster(_arg("--mon", "krysa"), lv.cell_center(lv._nearest_open(lv.to_cell(pos))), int(_arg("--mlvl", "1")))
			if m:
				m.died.connect(func(_a): kills += 1)
				m.wake()
				mons.append(m)
		if args.has("--loot"):
			for i in 10:
				var at := p.global_position + Vector2(randf_range(-110, 110), randf_range(-90, 90))
				lv.drop_item(Loot.gold(5) if i % 2 == 0 else Item.create("kytel", 1), at)
		get_tree().create_timer(float(_arg("--seconds", "10"))).timeout.connect(_report)
		return
	t += delta
	if p.dead or kills >= int(_arg("--n", "6")):
		_report()
		return
	var best: Monster = null
	var bd := INF
	for m in lv.monsters:
		if is_instance_valid(m) and not m.dead and m.global_position.distance_to(p.global_position) < bd:
			bd = m.global_position.distance_to(p.global_position)
			best = m
	if best and args.has("--clicks"):
		_click_t -= delta
		if _click_t <= 0.0 and (p.intent.is_empty() or p.intent.get("type", "") in ["_done", "move", "item"]):
			_click_t = 0.25
			var sp: Vector2 = get_viewport().get_canvas_transform() * best.center_pos()
			Input.warp_mouse(sp)
			for pressed in [true, false]:
				var ev := InputEventMouseButton.new()
				ev.button_index = MOUSE_BUTTON_LEFT
				ev.pressed = pressed
				ev.position = sp
				ev.global_position = sp
				Input.parse_input_event(ev)
			clicks += 1
			if p.intent.get("type", "") != "monster":
				misclicks += 1
		return
	if best and (p.intent.is_empty() or p.intent.get("type", "") == "_done"):
		p.intent = {"type": "monster", "node": best}
		p.lmb_down = false


func _report() -> void:
	print("PROBE t=%.1f kills=%d/%s dead=%s hp=%d/%d gold=%d clicks=%d stray=%d" % [t, kills, _arg("--n", "6"), Game.player.dead, Game.ch.hp, Game.ch.d.hp_max, Game.ch.gold, clicks, misclicks])
	get_tree().quit()
