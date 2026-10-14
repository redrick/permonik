class_name Actor
extends CharacterBody2D

signal died(actor: Actor)

const SHADER := preload("res://shaders/sprite_fx.gdshader")
const ELEMENT_COLORS := {"physical": Color("f2e6d0"), "fire": Color("ff9b4a"), "lightning": Color("bfe3ff"),
	"cold": Color("8fd3ff"), "poison": Color("8fe36b")}

static var _shadow_tex: Texture2D

var level: Node = null
var team := 1
var hp := 10.0
var hp_max := 10.0
var speed := 100.0
var radius := 16.0
var dead := false
var resist := {}
var armor := 0
var mlvl := 1
var display_name := ""
var sprite: Sprite2D
var shadow: Sprite2D
var tex := {}
var pose := "idle"
var pose_t := 0.0
var facing := 1
var status := {}
var path: Array = []
var anim_t := 0.0
var flash_t := 0.0
var stun_t := 0.0
var knock := Vector2.ZERO
var moving := false
var sprite_h := 128.0
var hover := false
var float_h := 0.0
var lunge := 0.0
var petrify := 0.0
var rig: Node2D
var swing_t := -1.0
var swing_dur := 0.0
var swing_hit := 0.0
var swing_pose := "attack"
var swing_style := "melee"
var swing_speed := 1.0
var recoil := 0.0
var recoil_dir := 1.0
var stride := 0.0
var stride_len := 0.0


func _ready() -> void:
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var cs := CollisionShape2D.new()
	var c := CircleShape2D.new()
	c.radius = radius
	cs.shape = c
	add_child(cs)


static func shadow_texture() -> Texture2D:
	if _shadow_tex == null:
		var img := Image.create(64, 24, false, Image.FORMAT_RGBA8)
		for y in 24:
			for x in 64:
				var dd := Vector2((x - 31.5) / 32.0, (y - 11.5) / 12.0).length()
				img.set_pixel(x, y, Color(0, 0, 0, clampf(1.0 - dd, 0.0, 1.0) * 0.55))
		_shadow_tex = ImageTexture.create_from_image(img)
	return _shadow_tex


func setup_visual(textures: Dictionary, with_shadow := true, shadow_w := -1.0) -> void:
	tex = textures
	for c in get_children():
		if c is CollisionShape2D and c.shape is CircleShape2D:
			(c.shape as CircleShape2D).radius = radius
	if with_shadow:
		shadow = Sprite2D.new()
		shadow.texture = shadow_texture()
		var sw := shadow_w if shadow_w > 0 else radius * 3.2
		shadow.scale = Vector2(sw / 64.0, sw / 64.0 * 0.9)
		add_child(shadow)
	rig = Node2D.new()
	add_child(rig)
	sprite = Sprite2D.new()
	var mat := ShaderMaterial.new()
	mat.shader = SHADER
	sprite.material = mat
	rig.add_child(sprite)
	set_pose("idle", 0.0)


func set_pose(p: String, hold := 0.0) -> void:
	var t: Texture2D = tex.get(p, null)
	if t == null:
		t = tex.get("idle", null)
	if t == null:
		return
	pose = p
	pose_t = hold
	if sprite.texture != t:
		sprite.texture = t
		sprite_h = t.get_height()
		sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)


func mat_set(k: String, v) -> void:
	if sprite and sprite.material:
		(sprite.material as ShaderMaterial).set_shader_parameter(k, v)


func set_hover(on: bool) -> void:
	if hover == on:
		return
	hover = on
	mat_set("outline", 2.0 if on else 0.0)


func top_pos() -> Vector2:
	return global_position + Vector2(0, -sprite_h + 8)


func center_pos() -> Vector2:
	return global_position + Vector2(0, -sprite_h * 0.45)


func hit_rect() -> Rect2:
	var t := sprite.texture if sprite else null
	var wv := maxf(52.0, (t.get_width() * 0.55) if t else 48.0)
	var hv := maxf(56.0, sprite_h - 8)
	return Rect2(global_position + Vector2(-wv / 2.0, 4 - hv - float_h), Vector2(wv, hv))


func can_act() -> bool:
	return not dead and stun_t <= 0.0 and status.get("freeze", 0.0) <= 0.0 and petrify < 1.0


func speed_mult() -> float:
	var m := 1.0
	if status.get("slow", 0.0) > 0.0:
		m *= 0.5
	if status.get("chill", 0.0) > 0.0:
		m *= 0.7
	if level and level.has_method("is_water") and level.is_water(global_position):
		m *= 0.65
	m *= 1.0 - clampf(petrify, 0.0, 1.0) * 0.8
	return m


func apply_status(s: String, t: float, data = null) -> void:
	if dead:
		return
	if s in ["burn", "poison"]:
		var cur: Dictionary = status.get(s, {"dps": 0.0, "t": 0.0, "src": null})
		status[s] = {"dps": maxf(cur.dps, float(data.get("dps", 1.0))), "t": maxf(cur.t, t), "src": data.get("src", null)}
	else:
		status[s] = maxf(float(status.get(s, 0.0)), t)


func _tick_status(delta: float) -> void:
	for s in status.keys():
		var v = status[s]
		if v is Dictionary:
			v.t -= delta
			take_damage(v.dps * delta, "fire" if s == "burn" else "poison", v.src, {"dot": true})
			if v.t <= 0.0 or dead:
				status.erase(s)
		else:
			status[s] = v - delta
			if status[s] <= 0.0:
				status.erase(s)
	var tint := Color(1, 1, 1, 1)
	if status.has("freeze"):
		tint = Color(0.55, 0.8, 1.2)
	elif status.has("chill") or status.has("slow"):
		tint = Color(0.75, 0.9, 1.1)
	elif status.has("burn"):
		tint = Color(1.2, 0.8, 0.6)
	elif status.has("poison"):
		tint = Color(0.8, 1.15, 0.7)
	mat_set("tint", tint)
	mat_set("stone", clampf(petrify, 0.0, 1.0))


func take_damage(amount: float, element := "physical", source: Node = null, opts := {}) -> float:
	if dead or amount <= 0.0:
		return 0.0
	var r := float(resist.get(element, 0))
	if r >= 100.0:
		if not opts.get("dot", false) and level:
			level.float_text(top_pos(), L.t({"cs": "Imunní", "en": "Immune"}), Color("bbbbbb"))
		return 0.0
	amount *= 1.0 - clampf(r, -100.0, 95.0) / 100.0
	amount = _modify_incoming(amount, element, source, opts)
	if amount <= 0.0:
		return 0.0
	hp -= amount
	if not opts.get("dot", false):
		flash_t = 0.12
		if level:
			level.float_text(top_pos() + Vector2(randf_range(-14, 14), 0), str(maxi(1, int(round(amount)))),
				Color("ffdd55") if opts.get("crit", false) else ELEMENT_COLORS.get(element, Color.WHITE), team == 0)
		recoil = maxf(recoil, clampf(amount / hp_max * 6.0, 0.45, 1.0))
		if source is Node2D:
			var dx: float = global_position.x - (source as Node2D).global_position.x
			recoil_dir = signf(dx) if absf(dx) > 1.0 else float(-facing)
		if amount > hp_max / hit_divisor() and not opts.get("no_stun", false):
			stun_t = maxf(stun_t, hit_recovery_time())
			swing_t = -1.0
			_on_hit_recover()
		if opts.has("knock") and source:
			knock = (global_position - source.global_position).normalized() * float(opts.knock)
	_on_damaged(amount, element, source)
	if hp <= 0.0:
		hp = 0.0
		die(source)
	return amount


# D2 hit recovery: a blow worth more than 1/12 of a hero's life (1/8 of a monster's) staggers.
func hit_divisor() -> float:
	return 8.0


func hit_recovery_time() -> float:
	return 0.22


func _modify_incoming(amount: float, _element: String, _source: Node, _opts: Dictionary) -> float:
	return amount


func _on_damaged(_amount: float, _element: String, _source: Node) -> void:
	pass


func _on_hit_recover() -> void:
	pass


func heal(amount: float) -> void:
	if dead:
		return
	hp = minf(hp_max, hp + amount)


func die(_killer: Node) -> void:
	if dead:
		return
	dead = true
	collision_layer = 0
	collision_mask = 0
	died.emit(self)
	set_hover(false)
	reset_rig()
	if shadow:
		create_tween().tween_property(shadow, "modulate:a", 0.0, 0.6)
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", deg_to_rad(80.0 * facing), 0.35).set_ease(Tween.EASE_IN)
	tw.parallel().tween_property(sprite, "position", Vector2(facing * sprite_h * 0.25, -6), 0.35)
	tw.tween_method(func(v): mat_set("dissolve", v), 0.0, 1.0, 0.9).set_delay(0.4)
	tw.tween_callback(queue_free)


func face_to(p: Vector2) -> void:
	var dx := p.x - global_position.x
	if absf(dx) > 2.0:
		facing = 1 if dx > 0 else -1
	if sprite:
		sprite.flip_h = facing < 0


func set_path_to(target: Vector2) -> void:
	if level:
		path = level.find_path(global_position, target)
	else:
		path = [target]


func follow_path(delta: float, spd: float) -> bool:
	if path.is_empty():
		moving = false
		velocity = Vector2.ZERO
		return true
	var tgt: Vector2 = path[0]
	var to := tgt - global_position
	var step := spd * delta
	if to.length() <= maxf(step, 6.0):
		path.pop_front()
		if path.is_empty():
			moving = false
			velocity = Vector2.ZERO
			return true
	face_to(tgt)
	velocity = to.normalized() * spd
	moving = true
	return false


func _physics_process(delta: float) -> void:
	if dead:
		return
	_tick_status(delta)
	stun_t = maxf(0.0, stun_t - delta)
	if knock.length() > 5.0:
		velocity = knock
		knock = knock.move_toward(Vector2.ZERO, 900.0 * delta)
		move_and_slide()
		return
	_ai(delta)
	move_and_slide()


func _ai(_delta: float) -> void:
	pass


func _process(delta: float) -> void:
	if sprite == null:
		return
	anim_t += delta
	flash_t = maxf(0.0, flash_t - delta)
	mat_set("flash", clampf(flash_t / 0.12, 0.0, 1.0) * 0.8)
	if dead:
		return
	if pose_t > 0.0:
		pose_t -= delta
		if pose_t <= 0.0:
			set_pose("idle")
	_animate(delta)


# The drawings have one frame per pose, so the motion between them is done on the rig:
# anticipation before the blow, a snap on impact, and a recoil on whoever gets hit.
func play_swing(dur: float, hit_at: float, strike_pose := "attack", style := "melee") -> void:
	swing_t = 0.0
	swing_dur = maxf(dur, hit_at + 0.05)
	swing_hit = maxf(hit_at, 0.0)
	swing_pose = strike_pose
	swing_style = style
	set_pose("idle", swing_hit)
	if swing_hit <= 0.0:
		set_pose(strike_pose, swing_dur)
		swing_pose = ""


func reset_rig() -> void:
	swing_t = -1.0
	recoil = 0.0
	if rig:
		rig.position = Vector2.ZERO
		rig.rotation = 0.0
		rig.scale = Vector2.ONE


func _animate(delta: float) -> void:
	var bob := 0.0
	var rot := 0.0
	var off := 0.0
	var sc := Vector2.ONE
	if moving and pose_t <= 0.0:
		stride += velocity.length() * delta / (stride_len if stride_len > 0.0 else maxf(28.0, radius * 2.2))
		var step := int(stride) % 2
		bob = -sin(fmod(stride, 1.0) * PI) * 3.0
		rot = 0.035
		if tex.has("walk"):
			set_pose("walk" if step == 0 else "idle")
		elif tex.has("walk1"):
			set_pose("walk1" if step == 0 else "walk2")
		elif pose != "idle":
			set_pose("idle")
	elif pose_t <= 0.0 and pose != "idle":
		set_pose("idle")
	else:
		bob = sin(anim_t * 2.2) * 0.8
		sc.y += sin(anim_t * 2.2) * 0.008
	if swing_t >= 0.0:
		swing_t += delta * swing_speed
		var wind := 0.0
		var hit := 0.0
		if swing_t < swing_hit:
			wind = ease(swing_t / swing_hit, 0.45)
		else:
			if swing_pose != "":
				set_pose(swing_pose, swing_dur - swing_t)
				swing_pose = ""
			var k := swing_t - swing_hit
			hit = k / 0.05 if k < 0.05 else 1.0 - ease(clampf((k - 0.05) / maxf(0.06, swing_dur - swing_hit - 0.05), 0.0, 1.0), 0.6)
			wind = 1.0 - minf(1.0, k / 0.05)
		match swing_style:
			"cast":
				sc *= Vector2(1.0 + 0.05 * wind - 0.04 * hit, 1.0 - 0.06 * wind + 0.07 * hit)
				rot += -0.03 * wind
			"shoot":
				rot += -0.05 * wind - 0.06 * hit
				off += -3.0 * wind - 6.0 * hit
			_:
				rot += -0.10 * wind + 0.14 * hit
				off += -6.0 * wind + 14.0 * hit
				sc *= Vector2(1.0 - 0.04 * wind + 0.07 * hit, 1.0 + 0.04 * wind - 0.05 * hit)
		if swing_t >= swing_dur:
			swing_t = -1.0
	var r := recoil * recoil
	recoil = maxf(0.0, recoil - delta * 6.0)
	rig.position = Vector2(off * facing + recoil_dir * r * 9.0, 0.0)
	rig.rotation = rot * facing + recoil_dir * r * 0.12
	rig.scale = sc * Vector2(1.0 + 0.08 * r, 1.0 - 0.08 * r)
	lunge = move_toward(lunge, 0.0, delta * 60.0)
	sprite.position = Vector2(lunge * facing, bob - float_h)
