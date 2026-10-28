class_name Automap
extends Control

# Tab: the whole explored level on a paper sheet, with the floor's name pencilled at the top.

const SHEET := Vector2(1500, 938)

var sheet: TextureRect
var clip: Control
var view: MapView
var title: Label


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	sheet = TextureRect.new()
	sheet.texture = DB.tex("ui/map_sheet")
	sheet.stretch_mode = TextureRect.STRETCH_SCALE
	sheet.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	sheet.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sheet.modulate.a = 0.95
	add_child(sheet)
	clip = Control.new()
	clip.clip_contents = true
	clip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sheet.add_child(clip)
	view = MapView.new()
	view.follow = false
	view.icon_px = 26.0
	clip.add_child(view)
	title = Label.new()
	title.add_theme_font_override("font", load("res://assets/fonts/TataHand.ttf"))
	title.add_theme_font_size_override("font_size", 44)
	title.add_theme_color_override("font_color", Color(0.18, 0.14, 0.12, 0.9))
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	sheet.add_child(title)
	visibility_changed.connect(_layout)
	resized.connect(_layout)


func _layout() -> void:
	if not visible:
		return
	var vs := size
	var bar: float = Game.main.hud.bar_h() if Game.main and Game.main.hud else 160.0
	var k := minf(1.0, minf((vs.x - 60) / SHEET.x, (vs.y - bar - 40) / SHEET.y))
	sheet.size = SHEET * k
	sheet.position = Vector2((vs.x - sheet.size.x) / 2.0, maxf(10.0, (vs.y - bar - sheet.size.y) / 2.0))
	clip.position = Vector2(60, 90) * k
	clip.size = sheet.size - Vector2(120, 140) * k
	view.size = clip.size
	title.position = Vector2(0, 22 * k)
	title.size = Vector2(sheet.size.x, 60 * k)
	var lv: Level = Game.level
	if lv == null:
		return
	view.zoom = clampf(minf(clip.size.x / lv.w, clip.size.y / lv.h), 6.0, 18.0)
	view.follow = lv.w * view.zoom > clip.size.x or lv.h * view.zoom > clip.size.y
	if lv.is_town:
		title.text = L.t(DB.act(lv.act_n).get("town", {}).get("name", ""))
	else:
		title.text = L.t(DB.floor_def(lv.act_n, lv.floor_n).get("name", ""))
