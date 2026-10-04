class_name Minimap
extends Control

# Round map in the top-right corner: a paper disc, the map clipped to it, the wooden ring on top.

const SIZE := 280.0
const R := 118.0


class Disc extends Control:
	func _draw() -> void:
		draw_circle(size / 2.0, Minimap.R, Color.WHITE)


var view: MapView


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	size = Vector2(SIZE, SIZE)
	var paper := TextureRect.new()
	paper.texture = DB.tex("ui/minimap_disc")
	paper.size = size
	paper.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(paper)
	var mask := Disc.new()
	mask.size = size
	mask.clip_children = CanvasItem.CLIP_CHILDREN_ONLY
	mask.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(mask)
	view = MapView.new()
	view.size = size
	view.zoom = 7.0
	view.radius = R
	view.icon_px = 18.0
	mask.add_child(view)
	var frame := TextureRect.new()
	frame.texture = DB.tex("ui/minimap_frame")
	frame.size = size
	frame.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(frame)
