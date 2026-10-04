class_name GroundItem
extends Node2D

static var font: Font

var item: Item
var sprite: Sprite2D
var lbl: Label
var hover := false


static func create(it: Item, pos: Vector2) -> GroundItem:
	var g := GroundItem.new()
	g.item = it
	g.position = pos
	g._build()
	return g


func _build() -> void:
	sprite = Sprite2D.new()
	sprite.texture = item.icon()
	var s := 44.0 / maxf(sprite.texture.get_width(), sprite.texture.get_height()) * 1.3
	sprite.scale = Vector2.ONE * s
	sprite.rotation = randf_range(-0.6, 0.6)
	sprite.position = Vector2(0, -10)
	add_child(sprite)
	lbl = Label.new()
	if font == null:
		font = load("res://assets/fonts/TataHand.ttf")
	lbl.add_theme_font_override("font", font)
	lbl.add_theme_font_size_override("font_size", 20)
	lbl.add_theme_color_override("font_color", item.color())
	lbl.add_theme_color_override("font_outline_color", Color(0, 0, 0, 1))
	lbl.add_theme_constant_override("outline_size", 6)
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.05, 0.04, 0.05, 0.75)
	sb.content_margin_left = 6
	sb.content_margin_right = 6
	lbl.add_theme_stylebox_override("normal", sb)
	lbl.text = item.display_name()
	lbl.visible = false
	lbl.z_index = 50
	add_child(lbl)
	lbl.reset_size()
	lbl.position = Vector2(-lbl.size.x / 2, -54)
	var tw := create_tween()
	position.y -= 30
	tw.tween_property(self, "position:y", position.y + 30, 0.35).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)
	if item.rarity == Item.UNIQUE or item.slot() == "quest":
		var l := Fx.make_light(item.color(), 80.0, 0.8)
		add_child(l)


func show_label(on: bool) -> void:
	lbl.visible = on or hover


# The label only counts while Alt shows every label; a hover label must not grow over the monsters standing on the loot.
func hit_rect() -> Rect2:
	var r := Rect2(global_position + Vector2(-26, -38), Vector2(52, 48))
	if lbl.visible and Input.is_action_pressed("show_items"):
		r = r.merge(Rect2(global_position + lbl.position, lbl.size))
	return r


func set_hover(on: bool) -> void:
	hover = on
	lbl.visible = on or Input.is_action_pressed("show_items")
	sprite.modulate = Color(1.4, 1.4, 1.2) if on else Color.WHITE
