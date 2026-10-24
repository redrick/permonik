class_name PropNode
extends Node2D

var id := ""
var def := {}
var interact := ""
var used := false
var sprite: Sprite2D
var light: PointLight2D
var cell := Vector2i.ZERO
var data := {}
var hover := false

# A material per prop would cost a draw call each; props only wear one while hovered.
static var _outline: ShaderMaterial


static func create(prop_id: String, pos: Vector2, with_shadow := true) -> PropNode:
	var p := PropNode.new()
	p.id = prop_id
	p.def = DB.prop(prop_id)
	p.interact = str(p.def.get("interact", "")) if p.def.get("interact", null) != null else ""
	if bool(p.def.get("breakable", false)) and p.interact == "":
		p.interact = "break"
	p.position = pos
	p._build(with_shadow)
	return p


func _build(with_shadow: bool) -> void:
	sprite = Sprite2D.new()
	var t := DB.tex("props/" + id)
	if t == null:
		var fp = def.get("footprint", [1, 1])
		t = DB.placeholder("prop_" + id, Vector2i(maxi(48, int(fp[0]) * 64), maxi(48, int(fp[1]) * 64 + 40)), Color("7a6a58"))
	sprite.texture = t
	sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)
	if with_shadow and not def.get("footprint", [1, 1]) == [0, 0]:
		var sh := Sprite2D.new()
		sh.texture = Actor.shadow_texture()
		if t.get_height() < 260:
			var sw := t.get_width() * 0.7
			sh.scale = Vector2(sw / 64.0, sw / 64.0 * 0.7)
		else:
			var fw := float(def.get("footprint", [2, 1])[0]) * 64.0 * 1.05
			sh.scale = Vector2(fw / 64.0, minf(fw / 64.0 * 0.32, 1.4))
			sh.position = Vector2(0, -6)
		add_child(sh)
	add_child(sprite)
	if id in CHIMNEYS:
		_smoke(t)
	var lt = def.get("light", null)
	if lt is Dictionary:
		light = Fx.make_light(Color(lt.get("color", "#ffb85c")), float(lt.get("radius", 3)) * 64.0, 0.95)
		light.position = Vector2(0, -t.get_height() * 0.6)
		add_child(light)
		var tw := light.create_tween().set_loops()
		tw.tween_property(light, "energy", 0.8, 0.25 + randf() * 0.2)
		tw.tween_property(light, "energy", 1.0, 0.25 + randf() * 0.2)
	if id in ["kovarna", "pec"]:
		var st = load("res://assets/audio/sfx/ember_crackle.ogg")
		if st:
			st = st.duplicate()
			st.loop = true
			var ap := AudioStreamPlayer2D.new()
			ap.stream = st
			ap.max_distance = 500.0
			ap.volume_db = linear_to_db(maxf(Sfx.volume, 0.001))
			ap.autoplay = true
			add_child(ap)
	set_meta("reach", float(t.get_width()) * 0.3)


const CHIMNEYS := ["dum_a", "dum_b", "chalupa", "kovarna", "hostinec", "mincovna"]
static var _chimney := {}


# The drawn smoke curl is the highest ink on a house, so the chimney sits just under it.
static func chimney_of(prop_id: String, t: Texture2D) -> Vector2:
	if _chimney.has(prop_id):
		return _chimney[prop_id]
	var img := t.get_image()
	if img.is_compressed():
		img.decompress()
	var out := Vector2(-1, -1)
	for y in img.get_height():
		for x in img.get_width():
			if img.get_pixel(x, y).a > 0.16:
				out = Vector2(x + 2, y + 26)
				break
		if out.x >= 0:
			break
	_chimney[prop_id] = out
	return out


func _smoke(t: Texture2D) -> void:
	var c := chimney_of(id, t)
	if c.x < 0:
		return
	var p := CPUParticles2D.new()
	p.texture = Fx.soft()
	p.amount = 9
	p.lifetime = 3.2
	p.preprocess = 3.0
	p.direction = Vector2.UP
	p.spread = 12.0
	p.initial_velocity_min = 14.0
	p.initial_velocity_max = 24.0
	p.gravity = Vector2(9, -6)
	p.scale_amount_min = 0.35
	p.scale_amount_max = 0.6
	var curve := Curve.new()
	curve.add_point(Vector2(0, 0.4))
	curve.add_point(Vector2(1, 1.6))
	p.scale_amount_curve = curve
	var g := Gradient.new()
	g.offsets = PackedFloat32Array([0.0, 0.25, 1.0])
	g.colors = PackedColorArray([Color(0.55, 0.53, 0.56, 0.0), Color(0.5, 0.49, 0.53, 0.3), Color(0.42, 0.42, 0.48, 0.0)])
	p.color_ramp = g
	var mat := CanvasItemMaterial.new()
	mat.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
	p.material = mat
	p.position = Vector2(c.x - t.get_width() / 2.0, c.y - t.get_height() + 8.0)
	p.z_index = 1
	add_child(p)


func set_texture(prop_id: String) -> void:
	var t := DB.tex("props/" + prop_id)
	if t:
		sprite.texture = t
		sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)


func hit_rect() -> Rect2:
	var t := sprite.texture
	var w := t.get_width() * 0.7
	return Rect2(global_position + Vector2(-w / 2, -t.get_height() + 12), Vector2(w, t.get_height() - 4))


func set_hover(on: bool) -> void:
	if hover == on:
		return
	hover = on
	if on and _outline == null:
		_outline = ShaderMaterial.new()
		_outline.shader = Actor.SHADER
		_outline.set_shader_parameter("outline", 2.0)
		_outline.set_shader_parameter("outline_color", Color(0.95, 0.85, 0.5, 1))
	sprite.material = _outline if on else null


func label() -> String:
	if data.has("book"):
		return L.t(DB.books.get(data.book, {}).get("title", data.book))
	var n = def.get("name", null)
	if n:
		return L.t(n)
	return L.t(PROP_NAMES.get(id, PROP_NAMES.get(interact, {"cs": id, "en": id})))


const PROP_NAMES := {
	"chest": {"cs": "Truhla", "en": "Chest"}, "shrine": {"cs": "Modla", "en": "Idol"},
	"stairs_down": {"cs": "Dolů do hlubin", "en": "Down into the deep"}, "stairs_up": {"cs": "Nahoru", "en": "Up"},
	"waypoint": {"cs": "Těžní klec", "en": "Shaft cage"}, "break": {"cs": "Sud", "en": "Barrel"},
	"urna": {"cs": "Urna", "en": "Urn"}, "sud": {"cs": "Sud", "en": "Barrel"},
	"stash": {"cs": "Truhla na věci", "en": "Stash"}, "portal": {"cs": "Brána", "en": "Portal"},
	"hrnek_dusicka": {"cs": "Hrníček s dušičkou", "en": "Teacup with a soul"},
	"zrcadlo": {"cs": "Zrcadlo", "en": "Mirror"}, "kbelik": {"cs": "Kbelík mrtvé vody", "en": "Bucket of dead water"},
	"dub": {"cs": "Starý dub", "en": "Old oak"}, "truhla_kostej": {"cs": "Okovaná truhla", "en": "Iron-bound chest"},
	"zvon": {"cs": "Zvon", "en": "The bell"},
}
