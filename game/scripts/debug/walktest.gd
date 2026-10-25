extends Node

# Walk test: clear the monsters, optionally break every barrel/urn, then walk the hero to random open
# cells like a click would, and report each time it stops short without arriving.
var args := OS.get_cmdline_user_args()
var started := false
var target := Vector2.ZERO
var last_pos := Vector2.ZERO
var still_t := 0.0
var walk_t := 0.0
var trips := 0
var reached := 0
var stuck: Array = []
var travelled := 0.0
var prev_pos := Vector2.ZERO
var trail: Array = []


func _arg(k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func _physics_process(delta: float) -> void:
	var p: Player = Game.player
	var lv: Level = Game.level
	if p == null or lv == null:
		return
	if not started:
		started = true
		for m in lv.monsters.duplicate():
			m.queue_free()
		lv.monsters.clear()
		if args.has("--break"):
			for pr in lv.props.duplicate():
				if is_instance_valid(pr) and pr.interact == "break":
					lv._break_prop(pr)
		p.invuln = 99999.0
		_next(p, lv)
		return
	walk_t += delta
	for m in lv.monsters.duplicate():
		m.queue_free()
		lv.monsters.erase(m)
	travelled += p.global_position.distance_to(prev_pos)
	prev_pos = p.global_position
	trail.append(p.global_position.round())
	if trail.size() > 8:
		trail.pop_front()
	if p.global_position.distance_to(target) < 40.0 or p.intent.is_empty():
		if p.global_position.distance_to(target) < 80.0:
			reached += 1
		_next(p, lv)
		return
	if p.global_position.distance_to(last_pos) < 1.5:
		still_t += delta
	else:
		still_t = 0.0
		travelled = 0.0
		last_pos = p.global_position
	if walk_t > 150.0:
		_next(p, lv)
	elif still_t > 1.2:
		var dir: Vector2 = (p.path[0] - p.global_position) if not p.path.is_empty() else Vector2.ZERO
		var hit := "none"
		var kc := p.get_last_slide_collision()
		if kc:
			var o := kc.get_collider()
			hit = "%s(%s) n=%s depth=%.1f" % [o.get_class(), (o.get_parent().get("id") if o.get_parent() else ""), kc.get_normal().round(), kc.get_depth()]
		hit += " travelled=%.0f trail=%s" % [travelled, trail.slice(4)]
		hit += " vel=%s stun=%.2f act=%.2f intent=%s path=%d mons=%d" % [p.velocity.round(), p.stun_t, p.action_t, p.intent.get("type", "-"), p.path.size(), lv.monsters.size()]
		var around := ""
		var pc := lv.to_cell(p.global_position)
		for oy in range(-1, 2):
			for ox in range(-1, 2):
				around += "#" if lv.gen.at(pc.x + ox, pc.y + oy) == DungeonGen.WALL else ("x" if lv.is_solid_cell(pc + Vector2i(ox, oy)) else ".")
			around += "/"
		stuck.append("hit %s around %s | at %s cell %s heading %s next %s solid_next=%s" % [hit, around, p.global_position.round(), lv.to_cell(p.global_position),
			_dir(dir), lv.to_cell(p.path[0]) if not p.path.is_empty() else "-",
			lv.is_solid(p.path[0]) if not p.path.is_empty() else "-"])
		_next(p, lv)
	if trips >= int(_arg("--trips", "60")):
		print("WALK trips=%d reached=%d stuck=%d" % [trips, reached, stuck.size()])
		for s in stuck:
			print("  STUCK " + s)
		get_tree().quit()


func _dir(v: Vector2) -> String:
	if v.length() < 0.1:
		return "-"
	var a := rad_to_deg(v.angle())
	return ["E", "SE", "S", "SW", "W", "NW", "N", "NE"][int(posmod(round(a / 45.0), 8))]


func _next(p: Player, lv: Level) -> void:
	trips += 1
	still_t = 0.0
	walk_t = 0.0
	for i in 200:
		var c := Vector2i(randi_range(1, lv.w - 2), randi_range(1, lv.h - 2))
		if not lv.is_solid_cell(c) and lv.find_path(p.global_position, lv.cell_center(c)).size() > 0:
			target = lv.cell_center(c)
			break
	p.intent = {"type": "move", "pos": target}
	p.set_path_to(target)
	last_pos = p.global_position
