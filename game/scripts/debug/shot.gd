extends Node

var args := OS.get_cmdline_user_args()


func _arg(k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	await get_tree().create_timer(float(_arg("--wait", "3"))).timeout
	if args.has("--menu"):
		Game.main.ui.screen._show(_arg("--menu", "main"))
		await get_tree().create_timer(0.5).timeout
	for p in _arg("--panel", "").split(",", false):
		Game.main.ui.toggle_panel(p)
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
	if args.has("--map"):
		Game.main.hud.toggle("automap")
	if args.has("--hide-hud") and Game.main.hud:
		Game.main.hud.visible = false
	await get_tree().create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_jpg(_arg("--shot", "user://shot.jpg"), 0.88)
	get_tree().quit()
