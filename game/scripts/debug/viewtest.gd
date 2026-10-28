extends Node

# View test: walk the hero right, down, up, left and down-left, grab a few frames of each walk and of
# a swing, and save them as one strip (--out, default user://viewtest.png).
var args := OS.get_cmdline_user_args()


func _arg(k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func _ready() -> void:
	await get_tree().create_timer(1.5).timeout
	var p: Player = Game.player
	p.invuln = 99999.0
	Game.main.hud.visible = false
	if args.has("--keep"):
		await _crowd(p)
		return
	if args.has("--ground"):
		await _ground(p)
		return
	for m in Game.level.monsters.duplicate():
		m.queue_free()
	Game.level.monsters.clear()
	var frames: Array[Image] = []
	for d in [Vector2.RIGHT, Vector2.DOWN, Vector2.UP, Vector2.LEFT, Vector2(-1, 1).normalized()]:
		var start := p.global_position
		p.intent = {"type": "move", "pos": start + d * 400.0}
		p.set_path_to(start + d * 400.0)
		await get_tree().create_timer(0.35).timeout
		for i in 6:
			frames.append(await _grab(p))
			await get_tree().create_timer(0.07).timeout
		p.intent = {}
		p.path.clear()
		await get_tree().create_timer(0.3).timeout
		p.face_to(p.global_position + d * 50.0)
		p.play_swing(0.5, 0.25)
		await get_tree().create_timer(0.12).timeout
		frames.append(await _grab(p))
		await get_tree().create_timer(0.15).timeout
		frames.append(await _grab(p))
		await get_tree().create_timer(0.4).timeout
		p.global_position = start
	var w := frames[0].get_width()
	var h := frames[0].get_height()
	var cols := 8
	var sheet := Image.create(w * cols, h * ceili(frames.size() / float(cols)), false, Image.FORMAT_RGBA8)
	for i in frames.size():
		sheet.blit_rect(frames[i], Rect2i(Vector2i.ZERO, frames[i].get_size()), Vector2i((i % cols) * w, (i / cols) * h))
	sheet.save_png(_arg("--out", "user://viewtest.png"))
	get_tree().quit()


# --keep: leave the floor's monsters, pull the nearest ones in around the hero and grab whole frames
# while they come at him from every side.
func _crowd(p: Player) -> void:
	var ms: Array = Game.level.monsters.duplicate()
	ms.sort_custom(func(a, b): return a.global_position.distance_to(p.global_position) < b.global_position.distance_to(p.global_position))
	var ring := 0
	for m in ms.slice(0, 8):
		m.global_position = p.global_position + Vector2.from_angle(ring * TAU / 8.0) * float(_arg("--ring", "260"))
		ring += 1
		if args.has("--still"):
			m.stun_t = 999.0

	var seq := _arg("--seq", "")
	for i in (int(_arg("--frames", "90")) if seq != "" else 6):
		if seq == "":
			await get_tree().create_timer(0.35).timeout
		await RenderingServer.frame_post_draw
		var img := get_viewport().get_texture().get_image()
		if not args.has("--full"):
			img.resize(img.get_width() / 2, img.get_height() / 2)
		if seq != "":
			var c := img.get_size() / 2
			img.get_region(Rect2i(c - Vector2i(400, 260), Vector2i(800, 520))).save_png(seq.path_join("%03d.png" % i))
			continue
		img.save_png(_arg("--out", "user://viewtest.png").replace(".png", "_%d.png" % i))
	get_tree().quit()


# --ground: hold the camera still and stack the frames of one walk to the right, so the feet can be
# checked against the floor.
func _ground(p: Player) -> void:
	for m in Game.level.monsters.duplicate():
		m.queue_free()
	Game.level.monsters.clear()
	var dx := float(_arg("--dir", "1"))
	var start := p.global_position
	await get_tree().create_timer(0.3).timeout
	var vp := get_viewport()
	p.intent = {"type": "move", "pos": start + Vector2(dx * 400.0, 0)}
	p.set_path_to(start + Vector2(dx * 400.0, 0))
	var frames: Array[Image] = []
	var seq := _arg("--seq", "")
	for i in int(_arg("--frames", "24")):
		if seq == "":
			await get_tree().create_timer(1.0 / 30.0).timeout
		await RenderingServer.frame_post_draw
		var img := vp.get_texture().get_image()
		var z := vp.get_canvas_transform()
		var f := Vector2(img.get_size()) / vp.get_visible_rect().size
		var a := z * (start + Vector2(-40 if dx > 0 else -360, -150)) * f
		var b := z * (start + Vector2(360 if dx > 0 else 40, 20)) * f
		var r := Rect2i(Vector2i(a), Vector2i(b - a)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
		if seq != "":
			img.get_region(r).save_png(seq.path_join("%03d.png" % i))
			continue
		frames.append(img.get_region(r))
	if seq != "":
		get_tree().quit()
		return
	var w := frames[0].get_width()
	var h := frames[0].get_height()
	var sheet := Image.create(w * 2, h * 12, false, frames[0].get_format())
	for i in frames.size():
		sheet.blit_rect(frames[i], Rect2i(Vector2i.ZERO, frames[i].get_size()), Vector2i((i / 12) * w, (i % 12) * h))
	sheet.save_png(_arg("--out", "user://viewtest.png"))
	get_tree().quit()


func _grab(p: Player) -> Image:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var c := img.get_size() / 2
	var r := Rect2i(c - Vector2i(110, 190), Vector2i(220, 230)).intersection(Rect2i(Vector2i.ZERO, img.get_size()))
	var out := Image.create(220, 230, false, img.get_format())
	out.blit_rect(img, r, Vector2i.ZERO)
	out.convert(Image.FORMAT_RGBA8)
	return out
