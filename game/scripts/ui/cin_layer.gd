class_name CinLayer
extends Node2D

# One cut-out piece of a cinematic shot. Its pivot and motion live in canvas px; UiCinema turns
# that into screen space every frame through the parallax camera (depth 0 = sky, 1 = the action).

var depth := 1.0
var pivot := Vector2.ZERO
var pos := Vector2.ZERO
var rot := 0.0
var scl := Vector2.ONE
var boil := 0.0
var step := false
var bob := 0.0
var bob_rate := 2.0
var swing_amp := 0.0
var swing_period := 2.0
var cycle_from := -1
var cycle_to := -1
var cycle_fps := 8.0
var frame := 0:
	set = set_frame

var sprite: Sprite2D
var _frames: Array = []
var _jit := Vector2.ZERO
var _jrot := 0.0
var _spos := Vector2.ZERO
var _srot := 0.0
var _sscl := Vector2.ONE


func _init() -> void:
	sprite = Sprite2D.new()
	sprite.centered = false
	add_child(sprite)


func add_frame(tex: Texture2D, top_left: Vector2) -> int:
	_frames.append([tex, top_left])
	if _frames.size() == 1:
		set_frame(0)
	return _frames.size() - 1


func set_frame(i: int) -> void:
	frame = i
	if i < 0 or i >= _frames.size():
		sprite.visible = false
		return
	sprite.visible = true
	sprite.texture = _frames[i][0]
	sprite.position = _frames[i][1] - pivot


func apply(sc: Vector2, cam: Vector2, zoom: float, fit: float, canvas: Vector2, t: float, boil_tick: bool, step_tick: bool) -> void:
	if boil > 0.0 and boil_tick:
		_jit = Vector2(randf_range(-boil, boil), randf_range(-boil, boil))
		_jrot = randf_range(-0.25, 0.25) * boil
	if not step or step_tick:
		_spos = pos
		if bob > 0.0:
			_spos.y -= absf(sin(t * bob_rate * PI)) * bob
		_srot = rot + (sin(TAU * t / swing_period) * swing_amp if swing_amp != 0.0 else 0.0)
		_sscl = scl
		if cycle_fps > 0.0 and cycle_from >= 0 and cycle_to >= cycle_from:
			var f := cycle_from + int(t * cycle_fps) % (cycle_to - cycle_from + 1)
			if f != frame:
				set_frame(f)
	var ce := canvas / 2.0 + (cam - canvas / 2.0) * depth
	var k := (1.0 + (zoom - 1.0) * depth) * fit
	position = sc + (pivot + _spos + _jit - ce) * k
	rotation = deg_to_rad(_srot + _jrot)
	scale = _sscl * k
