extends Node

# Stages the new loot UI for screenshots (run with --write-movie): inventory arrows and the
# "if you wear it" tooltip, crafted/ethereal items, forge recipes, the collection, charm-speaking.


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	await get_tree().create_timer(2.0).timeout
	var ch := Game.ch
	ch.level = 30
	ch.gold = 50000
	ch.recalc()
	var worn: Item = ch.weapon()
	var better := Item.create(worn.base_id, 30)
	Loot.make_rare(better)
	better.mods.append({"stat": "dmg_pct", "value": 90})
	better.identified = true
	var worse := Item.create(worn.base_id, 5)
	worse.dmg = Vector2i(1, 2)
	var eth := Item.create("krumpac", 30)
	eth.make_ethereal()
	var ring := Item.create("prsten", 30)
	Loot.make_crafted(ring, "granat")
	ring.personal = "Ondra"
	for it in [better, worse, eth, ring]:
		ch.inv.add(it)
	for id in ["klekanicina_rouska", "srdce_zvonu_cep"]:
		Game.note_found(Loot.unique_item(id, 10))
	Game.note_found(Loot.set_item("kazin_korenar_hul", 10))
	var ui := UiRoot.inst
	ui.toggle_panel("inventory")
	await get_tree().process_frame
	await get_tree().process_frame
	_hover(better)
	await get_tree().create_timer(1.5).timeout
	Input.action_press("show_items")
	_hover(ring)
	await get_tree().create_timer(1.5).timeout
	Input.action_release("show_items")
	UiForge.show_recipes = true
	ui.open_forge()
	await get_tree().process_frame
	var sc: ScrollContainer = ui.left.recipes
	sc.scroll_vertical = 1400
	await get_tree().create_timer(1.5).timeout
	ui.open_kronika()
	await get_tree().process_frame
	ui.left._open_tab("grail")
	ui.left._show("grail:u")
	await get_tree().create_timer(1.5).timeout
	ui.open_service("reroll")
	await get_tree().process_frame
	ch.inv.remove(better)
	better.pos = Vector2i(-1, -1)
	ui.left.box.add(better)
	await get_tree().create_timer(1.5).timeout
	get_tree().quit()


func _hover(it: Item) -> void:
	for g in get_tree().root.find_children("*", "UiGrid", true, false):
		if g.mode == "inv":
			var p: Vector2 = g.get_global_rect().position + (Vector2(it.pos) + Vector2(0.5, 0.5)) * UiTheme.CELL * g.get_global_transform_with_canvas().get_scale()
			get_viewport().warp_mouse(p)
