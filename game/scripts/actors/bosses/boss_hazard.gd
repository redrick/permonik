class_name BossHazard
extends Node2D

var level: Node
var src: Monster
var radius := 80.0
var life := 6.0
var delay := 0.0
var tick := 0.5
var tick_t := 0.0
var dmg := Vector2.ZERO
var element := "physical"
var status_id := ""
var status_t := 0.7
var petrify_add := 0.0
var col := Color.WHITE
var flames := false
var blob: Sprite2D
var light: PointLight2D


static func spawn(source: Monster, pos: Vector2, r: float, dur: float, c: Color, elem: String, d: Vector2, warn := 0.8, with_flames := false) -> BossHazard:
	var z := BossHazard.new()
	z.src = source
	z.level = source.level
	z.radius = r
	z.life = dur
	z.delay = warn
	z.col = c
	z.element = elem
	z.dmg = d
	z.flames = with_flames
	z.global_position = pos
	source.level.fx_root.add_child(z)
	z._build()
	return z


func _build() -> void:
	z_index = -1
	blob = Sprite2D.new()
	blob.texture = Fx.soft()
	blob.scale = Vector2(radius / 32.0, radius / 32.0 * 0.55)
	blob.modulate = Color(col.r, col.g, col.b, 0.0)
	var m := CanvasItemMaterial.new()
	m.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	m.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	blob.material = m
	add_child(blob)
	var tw := blob.create_tween()
	tw.tween_property(blob, "modulate:a", 0.3, maxf(0.05, delay))
	tw.tween_property(blob, "modulate:a", 0.6, 0.15)
	if flames:
		var ft := DB.tex("sprites/fx/flame")
		for i in 5:
			var s := Sprite2D.new()
			s.texture = ft if ft else Fx.soft()
			s.modulate = Color(1, 1, 1, 0) if ft else Color(col.r, col.g, col.b, 0)
			s.position = Vector2(randf_range(-radius, radius) * 0.6, randf_range(-radius, radius) * 0.3 - 20)
			s.material = m
			add_child(s)
			var t2 := s.create_tween()
			t2.tween_interval(maxf(0.05, delay))
			t2.tween_property(s, "modulate:a", 0.9, 0.2)
	light = Fx.make_light(col, radius * 1.6, 0.0)
	add_child(light)
	create_tween().tween_property(light, "energy", 0.6, maxf(0.05, delay))


func _physics_process(delta: float) -> void:
	if delay > 0.0:
		delay -= delta
		return
	life -= delta
	if life <= 0.0:
		set_physics_process(false)
		var tw := create_tween().set_parallel(true)
		tw.tween_property(self, "modulate:a", 0.0, 0.4)
		tw.tween_property(light, "energy", 0.0, 0.4)
		tw.chain().tween_callback(queue_free)
		return
	tick_t -= delta
	if tick_t > 0.0:
		return
	tick_t = tick
	var p: Player = level.player
	if p == null or not is_instance_valid(p) or p.dead:
		return
	if p.global_position.distance_to(global_position) > radius + p.radius:
		return
	if dmg.y > 0.0:
		p.take_damage(randf_range(dmg.x, dmg.y) * tick, element, src if is_instance_valid(src) else null, {"dot": true})
	if status_id != "":
		p.apply_status(status_id, status_t)
	if petrify_add > 0.0:
		p.petrify = minf(1.2, p.petrify + petrify_add)
