class_name GroundItem
extends Node2D

static var font: Font
# Loot filter from the settings: 0 shows everything, 1 hides plain gear, 2 also magic weapons and armour.
static var filter_level := -1

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
	if item.eth:
		sprite.self_modulate = Color(0.8, 0.9, 1.0, 0.6)
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
	if item.rarity in [Item.UNIQUE, Item.SET] or item.slot() == "quest":
		var l := Fx.make_light(item.color(), 90.0, 0.9)
		l.position = Vector2(0, -10)
		add_child(l)
		_beam()
	elif item.rarity in [Item.RARE, Item.CRAFTED]:
		var l := Fx.make_light(item.color(), 60.0, 0.6)
		add_child(l)


static var _beam_tex: Texture2D


# A pillar of light over the best loot, so it reads across the room even in the dark.
func _beam() -> void:
	if _beam_tex == null:
		var g := Gradient.new()
		g.offsets = PackedFloat32Array([0.0, 0.7, 1.0])
		g.colors = PackedColorArray([Color(1, 1, 1, 0), Color(1, 1, 1, 0.5), Color(1, 1, 1, 0.9)])
		var t := GradientTexture2D.new()
		t.gradient = g
		t.fill_from = Vector2(0, 0)
		t.fill_to = Vector2(0, 1)
		t.width = 16
		t.height = 128
		_beam_tex = t
	var mat := CanvasItemMaterial.new()
	mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	mat.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	for i in 2:
		var b := Sprite2D.new()
		b.texture = _beam_tex
		b.material = mat
		b.centered = false
		b.scale = Vector2(3.0 if i == 0 else 0.8, 2.4)
		b.position = Vector2(-8.0 * b.scale.x, -128.0 * b.scale.y - 4.0)
		var c := item.color()
		b.modulate = Color(c.r, c.g, c.b, 0.3 if i == 0 else 0.75)
		b.z_index = 2
		add_child(b)
		var tw := b.create_tween().set_loops()
		tw.tween_property(b, "modulate:a", b.modulate.a * 0.45, 1.1).set_trans(Tween.TRANS_SINE)
		tw.tween_property(b, "modulate:a", b.modulate.a, 1.1).set_trans(Tween.TRANS_SINE)
	var st = load("res://assets/audio/sfx/loot_beam.ogg")
	if st:
		st = st.duplicate()
		st.loop = true
		var ap := AudioStreamPlayer2D.new()
		ap.stream = st
		ap.max_distance = 700.0
		ap.volume_db = linear_to_db(maxf(Sfx.volume * 0.8, 0.001))
		ap.autoplay = true
		add_child(ap)


# Flung out of the kill in an arc, spinning, with a small bounce where it lands.
func toss() -> void:
	var land := position
	var from := land + Vector2(randf_range(-36, 36), randf_range(-24, 0))
	position = from
	var base_rot := sprite.rotation
	var h := randf_range(55.0, 85.0)
	var dur := 0.45
	var tw := create_tween().set_parallel(true)
	tw.tween_property(self, "position", land, dur)
	tw.tween_method(func(t: float): sprite.position.y = -10.0 - h * 4.0 * t * (1.0 - t), 0.0, 1.0, dur)
	tw.tween_property(sprite, "rotation", base_rot, dur).from(base_rot + randf_range(-1, 1) * TAU)
	tw.chain().tween_property(sprite, "position:y", -18.0, 0.08).set_ease(Tween.EASE_OUT)
	tw.chain().tween_property(sprite, "position:y", -10.0, 0.1).set_ease(Tween.EASE_IN)
	lbl.visible = false
	var snd := "drop_item"
	match item.rarity:
		Item.UNIQUE, Item.SET:
			snd = "drop_unique"
		Item.RARE, Item.CRAFTED:
			snd = "drop_rare"
		Item.MAGIC:
			snd = "drop_magic"
	get_tree().create_timer(dur).timeout.connect(func():
		if is_instance_valid(self):
			Sfx.play_at(snd, global_position, {"drop_unique": 0.9, "drop_rare": 0.6, "drop_magic": 0.45}.get(snd, 0.5)))


static func get_filter() -> int:
	if filter_level < 0:
		var cfg := ConfigFile.new()
		cfg.load("user://settings.cfg")
		filter_level = int(cfg.get_value("main", "loot_filter", 0))
	return filter_level


static func set_filter(v: int) -> void:
	filter_level = v
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	cfg.set_value("main", "loot_filter", v)
	cfg.save("user://settings.cfg")


static func hides(it: Item) -> bool:
	var f := get_filter()
	if f <= 0 or not it.is_equipment() or it.eth or it.sockets > 0 or it.word != "":
		return false
	if it.rarity == Item.NORMAL:
		return true
	return f >= 2 and it.rarity == Item.MAGIC and not it.slot() in ["ring", "amulet"]


# Filtered loot stays on the ground, unseen until Alt shows it, dimmed.
func show_label(on: bool) -> void:
	var hidden := GroundItem.hides(item)
	visible = on or not hidden
	modulate.a = 0.55 if hidden else 1.0
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
