class_name Automap
extends Control

var scale_px := 7.0


func _draw() -> void:
	var lv: Level = Game.level
	if lv == null or lv.player == null:
		return
	var vs := get_viewport_rect().size
	var center := vs / 2.0 - Vector2(0, 60)
	var pc := Vector2(lv.player.global_position) / Level.CELL
	var wall_col := Color(0.85, 0.75, 0.55, 0.85)
	var floor_col := Color(0.6, 0.55, 0.45, 0.18)
	var water_col := Color(0.3, 0.55, 0.7, 0.35)
	for y in lv.h:
		for x in lv.w:
			if lv.explored[y * lv.w + x] == 0:
				continue
			var p := center + (Vector2(x, y) - pc) * scale_px
			if p.x < -10 or p.y < -10 or p.x > vs.x + 10 or p.y > vs.y + 10:
				continue
			if lv.gen.at(x, y) == DungeonGen.WALL:
				var edge := false
				for o in [Vector2i(1, 0), Vector2i(-1, 0), Vector2i(0, 1), Vector2i(0, -1)]:
					var n : Vector2i = Vector2i(x, y) + o
					if n.x >= 0 and n.y >= 0 and n.x < lv.w and n.y < lv.h and lv.gen.at(n.x, n.y) != DungeonGen.WALL:
						edge = true
				if edge:
					draw_rect(Rect2(p, Vector2(scale_px, scale_px)), wall_col)
			else:
				draw_rect(Rect2(p, Vector2(scale_px, scale_px)), water_col if lv.water[y * lv.w + x] == 1 else floor_col)
	for pr in lv.props:
		if not is_instance_valid(pr):
			continue
		var col := Color(0, 0, 0, 0)
		match pr.interact:
			"stairs_down", "stairs_up":
				col = Color("e9c46a")
			"waypoint":
				col = Color("7fb0ff")
			"portal":
				col = Color("9fd0ff")
			"shrine":
				col = Color("c8a0ff") if not pr.used else Color(0, 0, 0, 0)
			"quest":
				col = Color("ff9a3a")
		var c := Vector2i(pr.position / Level.CELL)
		if col.a > 0 and lv.explored[clampi(c.y, 0, lv.h - 1) * lv.w + clampi(c.x, 0, lv.w - 1)] == 1:
			draw_circle(center + (pr.position / Level.CELL - pc) * scale_px, 5, col)
	for n in lv.npcs:
		draw_circle(center + (n.position / Level.CELL - pc) * scale_px, 4, Color("9ae07a"))
	draw_circle(center, 5, Color("ff4a3a"))
