class_name WorldMap
extends Control

# The shaft cage's map: Bohemia in pencil with the mining towns where they really are, and under it the
# mine in cross-section, one shaft per act. Every town and every floor the hero has reached is a stop.

const SIZE := Vector2(1080, 780)
const GRAPHITE := Color(0.16, 0.13, 0.12, 0.9)
const SOFT := Color(0.25, 0.2, 0.17, 0.45)
const LAND := Color(0.55, 0.6, 0.38, 0.16)
const RIVER := Color(0.25, 0.42, 0.7, 0.75)
const DEEP := Color(0.12, 0.09, 0.08, 0.16)
const NAV := Color(0.08, 0.07, 0.12, 0.32)
const LAND_BOTTOM := 450.0
const SHAFT_X := [600.0, 360.0, 120.0, 830.0]  # by act; the shafts sit under their towns without crossing

# Simplified borders of the Czech lands and the big rivers, as [lon, lat].
const BORDER := [[12.09, 50.25], [12.5, 50.4], [13.0, 50.5], [13.5, 50.65], [14.3, 50.88], [14.8, 50.85],
	[15.0, 51.0], [15.5, 50.78], [16.2, 50.65], [16.4, 50.4], [16.9, 50.45], [17.2, 50.3], [17.7, 50.32],
	[18.0, 50.0], [18.8, 49.7], [18.5, 49.45], [17.9, 49.0], [17.2, 48.8], [16.9, 48.62], [16.0, 48.75],
	[15.0, 49.0], [14.7, 48.6], [14.0, 48.65], [13.6, 48.95], [13.0, 49.3], [12.5, 49.75], [12.4, 50.05], [12.09, 50.25]]
const RIVERS := [
	[[14.45, 48.7], [14.4, 49.0], [14.45, 49.6], [14.42, 50.08], [14.47, 50.35]],
	[[15.6, 50.7], [15.8, 50.2], [15.2, 50.05], [14.47, 50.35], [14.05, 50.65], [14.2, 50.9]],
	[[12.3, 50.1], [12.9, 50.25], [13.5, 50.35], [14.1, 50.5], [14.4, 50.5]],
]
const HILLS := [[12.5, 50.45, 13.7, 50.68], [13.75, 49.82, 14.05, 49.62], [15.4, 50.78, 15.9, 50.72]]
const PLACES := {"hora": [15.27, 49.95], "pribram": [14.0, 49.68], "jachymov": [12.91, 50.37]}
const PRAHA := [14.42, 50.08]

var _tex := {}


func _ready() -> void:
	custom_minimum_size = SIZE
	for k in ["map_sheet", "map_cage", "map_hero"]:
		_tex[k] = DB.tex("ui/" + k)
	for a in DB.acts:
		var an := int(a.get("id", 0))
		if not _act_known(an):
			continue
		var town: Dictionary = a.get("town", {})
		add_child(_stop(an, 0, L.t(town.get("name", L.t("town"))), _town_pos(an), true))
		for fl in _floors(an):
			var f := int(fl.get("n", 0))
			if Game.waypoints.has(Game.waypoint_key(an, f)):
				add_child(_stop(an, f, L.t(fl.get("name", "%s %d" % [L.t("floor"), f])), _floor_pos(an, f), false))


static func _act_known(an: int) -> bool:
	if an <= Game.act or Game.known.has("town:" + str(DB.act(an).get("town", {}).get("id", ""))):
		return true
	for k in Game.waypoints:
		if str(k).begins_with("%d:" % an):
			return true
	return false


static func _floors(an: int) -> Array:
	return DB.act(an).get("floors", []).filter(func(fl): return not fl.has("uber"))


# Longitude shrinks by cos(50°) so the country keeps its shape; the land fills the sheet above the mine.
func _geo(p: Array) -> Vector2:
	return Vector2(166.0 + (float(p[0]) - 12.0) * 108.4, 24.0 + (51.06 - float(p[1])) * 168.0)


func _town_pos(an: int) -> Vector2:
	var id := str(DB.act(an).get("town", {}).get("id", ""))
	if PLACES.has(id):
		return _geo(PLACES[id])
	return Vector2(SHAFT_X[clampi(an - 1, 0, 3)], LAND_BOTTOM + 40.0)


func _floor_pos(an: int, f: int) -> Vector2:
	var i := 0
	for fl in _floors(an):
		i += 1
		if int(fl.get("n", 0)) == f:
			break
	var top := LAND_BOTTOM + (40.0 if PLACES.has(str(DB.act(an).get("town", {}).get("id", ""))) else 90.0)
	var step := (SIZE.y - 40.0 - top) / maxf(1.0, _floors(an).size())
	return Vector2(SHAFT_X[clampi(an - 1, 0, 3)], top + step * (i - 0.5))


func _stop(an: int, f: int, text: String, pos: Vector2, town: bool) -> Button:
	var b := Button.new()
	b.text = text
	b.flat = true
	b.focus_mode = Control.FOCUS_NONE
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.add_theme_font_override("font", UiTheme.small)
	b.add_theme_font_size_override("font_size", 22 if town else 19)
	for k in ["font_color", "font_focus_color"]:
		b.add_theme_color_override(k, GRAPHITE)
	b.add_theme_color_override("font_hover_color", Color("8a4a12"))
	b.add_theme_color_override("font_pressed_color", Color("8a4a12"))
	b.add_theme_color_override("font_disabled_color", Color("6a2a10"))
	if not town:
		b.icon = _tex.map_cage
	b.position = pos + (Vector2(14, -22) if town else Vector2(-18, -20))
	b.size = Vector2(230, 40)
	b.disabled = Game.act == an and Game.floor_n == f
	b.pressed.connect(func():
		UiRoot.inst.close_all()
		Sfx.play("waypoint", 0.7)
		Game.goto(an, f, "waypoint"))
	return b


func _draw() -> void:
	if _tex.map_sheet:
		draw_texture_rect(_tex.map_sheet, Rect2(Vector2.ZERO, SIZE), false)
	var land := PackedVector2Array()
	for p in BORDER:
		land.append(_geo(p))
	draw_colored_polygon(land, LAND)
	draw_polyline(land, GRAPHITE, 2.5, true)
	for r in RIVERS:
		var line := PackedVector2Array()
		for p in r:
			line.append(_geo(p))
		draw_polyline(line, RIVER, 2.5, true)
	for h in HILLS:
		var a := _geo([h[0], h[1]])
		var z := _geo([h[2], h[3]])
		for i in 7:
			var c := a.lerp(z, i / 6.0)
			draw_polyline(PackedVector2Array([c + Vector2(-9, 5), c + Vector2(0, -7), c + Vector2(9, 5)]), SOFT, 2.0, true)
	var pr := _geo(PRAHA)
	draw_circle(pr, 4.0, SOFT)
	draw_string(UiTheme.small, pr + Vector2(8, 6), "Praha", HORIZONTAL_ALIGNMENT_LEFT, -1, 17, SOFT)
	draw_rect(Rect2(14, LAND_BOTTOM, SIZE.x - 28, SIZE.y - LAND_BOTTOM - 14), DEEP)
	for i in 40:
		var x := 20.0 + i * 27.0
		draw_line(Vector2(x, LAND_BOTTOM), Vector2(x + 14, LAND_BOTTOM + 10), SOFT, 1.5)
	draw_line(Vector2(14, LAND_BOTTOM), Vector2(SIZE.x - 14, LAND_BOTTOM), GRAPHITE, 2.5)
	for a in DB.acts:
		var an := int(a.get("id", 0))
		if not _act_known(an):
			continue
		var x: float = SHAFT_X[clampi(an - 1, 0, 3)]
		var tp := _town_pos(an)
		var fls := _floors(an)
		var bottom := _floor_pos(an, int(fls[-1].get("n", 0))) if not fls.is_empty() else tp
		if not PLACES.has(str(a.get("town", {}).get("id", ""))):
			draw_rect(Rect2(x - 50, LAND_BOTTOM + 20, 280, SIZE.y - LAND_BOTTOM - 44), NAV)
		else:
			_dashed(tp, Vector2(x, LAND_BOTTOM))
		draw_line(Vector2(x, maxf(LAND_BOTTOM, tp.y)), bottom, GRAPHITE, 3.0)
		_town_mark(tp)
		draw_string(UiTheme.small, Vector2(x - 110, SIZE.y - 22), "%s %s" % [L.t("act"), UiQuests._roman(an)], HORIZONTAL_ALIGNMENT_CENTER, 220, 18, SOFT)
		for fl in fls:
			var f := int(fl.get("n", 0))
			if not Game.waypoints.has(Game.waypoint_key(an, f)):
				draw_circle(_floor_pos(an, f), 5.0, SOFT)
	var here := _floor_pos(Game.act, Game.floor_n) if Game.floor_n > 0 else _town_pos(Game.act)
	if _tex.map_hero:
		draw_texture_rect(_tex.map_hero, Rect2(here + Vector2(-44, -16), Vector2(32, 32)), false)


func _town_mark(p: Vector2) -> void:
	draw_rect(Rect2(p + Vector2(-9, -6), Vector2(18, 12)), Color(0.7, 0.55, 0.35, 0.8))
	draw_rect(Rect2(p + Vector2(-9, -6), Vector2(18, 12)), GRAPHITE, false, 2.0)
	draw_colored_polygon(PackedVector2Array([p + Vector2(-3, -6), p + Vector2(0, -16), p + Vector2(3, -6)]), GRAPHITE)


func _dashed(a: Vector2, b: Vector2) -> void:
	var n := int(a.distance_to(b) / 10.0)
	for i in range(0, n, 2):
		draw_line(a.lerp(b, float(i) / n), a.lerp(b, float(i + 1) / n), SOFT, 2.0)
