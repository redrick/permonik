extends Node

# Ground loot survives leaving a floor and coming back.


func _ready() -> void:
	var G = Game
	await get_tree().create_timer(2.0).timeout
	G.goto(1, 1, "start")
	await get_tree().create_timer(2.0).timeout
	var lv = G.level
	var p: Vector2 = G.player.global_position
	for id in ["granat_3", "krumpac", "ziva_voda"]:
		lv.drop_item(Item.create(id, 5), p + Vector2(40, 0))
	print("LOOT before: ", lv.ground_items.size())
	G.goto(1, 0, "start")
	await get_tree().create_timer(2.0).timeout
	print("LOOT stored keys: ", G.floor_loot.keys())
	await get_tree().create_timer(2.0).timeout
	G.goto(1, 1, "start")
	await get_tree().create_timer(2.0).timeout
	print("LOOT after return: ", G.level.ground_items.size(), " ", G.level.ground_items.map(func(g): return g.item.base_id))
	G.session_seed += 1
	G.goto(1, 0, "start")
	await get_tree().create_timer(2.0).timeout
	await get_tree().create_timer(2.0).timeout
	G.goto(1, 1, "start")
	await get_tree().create_timer(2.0).timeout
	print("LOOT after new seed: ", G.level.ground_items.size())
	get_tree().quit()
