extends Node

var args := OS.get_cmdline_user_args()


func _arg(k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var wait := float(_arg("--wait", "3"))
	if args.has("--lvl") or args.has("--near-boss"):
		await get_tree().create_timer(0.5).timeout
		wait -= 0.5
		_hero(int(_arg("--lvl", "30")))
	await get_tree().create_timer(wait).timeout
	if args.has("--menu"):
		Game.main.ui.screen._show(_arg("--menu", "main"))
		await get_tree().create_timer(0.5).timeout
	for k in _arg("--waypoints", "").split(",", false):
		Game.waypoints[k] = true
	for p in _arg("--panel", "").split(",", false):
		Game.main.ui.toggle_panel(p)
	if args.has("--recipes"):
		UiForge.show_recipes = true
	for k in _arg("--know", "").split(",", false):
		Game.learn(k.get_slice(":", 0), k.get_slice(":", 1))
	if args.has("--codex"):
		for n in get_tree().root.find_children("*", "", true, false):
			if n is UiKronika:
				n._jump(_arg("--codex", ""))
	if args.has("--open"):
		Game.main.ui.call("open_" + _arg("--open", "stash"))
	if args.has("--book"):
		Game.main.ui.open_book(_arg("--book", ""))
	for qs in _arg("--quest", "").split(",", false):
		var qp := qs.split(":")
		Game.quest_start(qp[0])
		if qp.size() > 1:
			Game.quest_set_step(qp[0], qp[1])
	if args.has("--loot-demo"):
		var demo := []
		var w := Item.create("krumpac_kovany", 40)
		w.sockets = 4
		for l in ["g", "r", "o", "m"]:
			w.socket(Item.create("glag_" + l, 40))
		demo.append(w)
		var r := Loot.roll_item(45, 400, 0.0, "body")
		if r:
			Loot.make_rare(r)
			r.identified = true
			demo.append(r)
		for id in ["granat_4", "vltavin_2", "glag_ja", "glag_a", "faracka_kovany"]:
			demo.append(Item.create(id, 40))
		var sh := Item.create("stit_hlubinny", 60)
		sh.sockets = 3
		sh.socket(Item.create("jaspis_3", 40))
		demo.append(sh)
		for it in demo:
			Game.ch.inv.add(it)
		Game.ch.inv.arrange()
	for id in _arg("--equip", "").split(",", false):
		var it := Item.create(id, 1)
		Game.ch.equip[it.slot()] = it
	if args.has("--equip"):
		Game.ch.changed.emit()
	if args.has("--bright") and Game.level:
		for c in Game.level.get_children():
			if c is CanvasModulate:
				c.color = Color(0.85, 0.85, 0.85)
	if args.has("--reveal") and Game.level:
		Game.level.explored.fill(1)
		Game.level.explored_rev += 1
		if Game.level.fog_img:
			Game.level.fog_img.fill(Color(0, 0, 0, 0))
			(Game.level.fog.texture as ImageTexture).update(Game.level.fog_img)
	if args.has("--map"):
		Game.main.hud.toggle("automap")
	if args.has("--hide-hud") and Game.main.hud:
		Game.main.hud.visible = false
	await get_tree().create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_jpg(_arg("--shot", "user://shot.jpg"), 0.88)
	get_tree().quit()


# A hero of the given level with every skill at rank 5, next to the floor's boss (with --near-boss);
# --autoplay then fights.
func _hero(lvl: int) -> void:
	var p: Player = Game.player
	var lv: Level = Game.level
	if p == null or lv == null:
		return
	Game.ch.level = lvl
	for tr in DB.classes[Game.ch.class_id].trees:
		for sid in tr.skills:
			Game.ch.skills[sid] = 5
	Game.ch.recalc()
	Game.ch.hp = Game.ch.d.hp_max
	Game.ch.mana = Game.ch.d.mana_max
	p.hp = Game.ch.hp
	p.invuln = 9999.0
	if args.has("--near-boss") and lv.boss:
		var tp := lv.random_open_near(lv.boss.global_position, 140, 220)
		if tp != Vector2.INF:
			p.global_position = tp
			lv._explore()
