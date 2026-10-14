class_name UiSlides
extends Control

var items: Array = []
var done: Callable
var idx := -1
var img: TextureRect
var text_lbl: Label
var fade: ColorRect
var busy := false
var finished := false
var kb: Tween
var typer: Tween


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.color = Color(0.02, 0.018, 0.016, 1)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	img = TextureRect.new()
	img.set_anchors_preset(Control.PRESET_FULL_RECT)
	img.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	img.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	img.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(img)
	var grad := Gradient.new()
	grad.set_color(0, Color(0, 0, 0, 0))
	grad.set_color(1, Color(0, 0, 0, 0.92))
	grad.add_point(0.45, Color(0, 0, 0, 0.7))
	var gt := GradientTexture2D.new()
	gt.gradient = grad
	gt.fill_from = Vector2(0, 0)
	gt.fill_to = Vector2(0, 1)
	gt.width = 4
	gt.height = 128
	var shade := TextureRect.new()
	shade.texture = gt
	shade.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	shade.stretch_mode = TextureRect.STRETCH_SCALE
	shade.anchor_left = 0
	shade.anchor_right = 1
	shade.anchor_top = 0.66
	shade.anchor_bottom = 1
	shade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(shade)
	text_lbl = UiTheme.label("", 40, Color("f2e8d2"))
	text_lbl.add_theme_constant_override("outline_size", 8)
	text_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	text_lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	text_lbl.anchor_left = 0.1
	text_lbl.anchor_right = 0.9
	text_lbl.anchor_top = 0.78
	text_lbl.anchor_bottom = 0.96
	add_child(text_lbl)
	var hint := UiTheme.label("%s  ·  %s" % [L.t("press_any_touch"), UiTheme.t("skip_all_touch")] if TouchPad.active else "%s  ·  %s" % [L.t("press_any"), UiTheme.t("skip_all")], 20, Color(1, 1, 1, 0.35), true)
	hint.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
	hint.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	hint.grow_vertical = Control.GROW_DIRECTION_BEGIN
	hint.position += Vector2(-24, -16)
	add_child(hint)
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 1)
	fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(fade)
	_show_next()


func _show_next() -> void:
	idx += 1
	if idx >= items.size():
		_finish()
		return
	busy = true
	var it: Dictionary = items[idx]
	var t := DB.tex("slides/" + str(it.get("image", "")))
	img.texture = t
	img.visible = t != null
	text_lbl.text = L.t(it.get("text", ""))
	text_lbl.anchor_top = 0.78 if t else 0.3
	text_lbl.anchor_bottom = 0.96 if t else 0.7
	text_lbl.visible_ratio = 0.0
	await get_tree().process_frame
	img.pivot_offset = img.size * Vector2(randf_range(0.35, 0.65), randf_range(0.35, 0.6))
	img.scale = Vector2.ONE
	if kb:
		kb.kill()
	kb = create_tween()
	kb.tween_property(img, "scale", Vector2(1.09, 1.09), 14.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.8)
	await tw.finished
	busy = false
	if typer:
		typer.kill()
	typer = create_tween()
	typer.tween_property(text_lbl, "visible_ratio", 1.0, clampf(text_lbl.text.length() / 45.0, 0.6, 5.0))


func advance() -> void:
	if busy or finished:
		return
	if text_lbl.visible_ratio < 1.0:
		if typer:
			typer.kill()
		text_lbl.visible_ratio = 1.0
		return
	busy = true
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.45)
	await tw.finished
	_show_next()


func skip_all() -> void:
	if finished:
		return
	idx = items.size()
	busy = true
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.3)
	await tw.finished
	_finish()


func _finish() -> void:
	if finished:
		return
	finished = true
	UiRoot.inst.slides_finished(self, done)


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
		accept_event()
		advance()


func _unhandled_key_input(event: InputEvent) -> void:
	var k := event as InputEventKey
	if k and k.pressed and not k.echo and k.keycode in [KEY_SPACE, KEY_ENTER, KEY_KP_ENTER]:
		get_viewport().set_input_as_handled()
		advance()
