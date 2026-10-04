extends Node

# Skill test: give the hero every skill of the class at rank 5, then cast each in turn at a monster
# and report what refused to cast, how many allies were up, and the shape the hero was in.
var args := OS.get_cmdline_user_args()
var started := false
var queue: Array = []
var t := 0.0
var log_lines: Array = []


func _physics_process(delta: float) -> void:
	var p: Player = Game.player
	var lv: Level = Game.level
	if p == null or lv == null:
		return
	if not started:
		started = true
		Game.ch.level = 30
		for tr in DB.classes[Game.ch.class_id].trees:
			for sid in tr.skills:
				Game.ch.skills[sid] = 5
				queue.append(sid)
		Game.ch.gold = 100000
		Game.ch.recalc()
		p.invuln = 9999.0
		for m in lv.monsters.duplicate():
			m.queue_free()
		lv.monsters.clear()
		for i in 4:
			lv.spawn_monster("kostlivy_havir", lv.cell_center(lv._nearest_open(lv.to_cell(p.global_position + Vector2(160 + i * 30, 0)))), 10)
		return
	t -= delta
	if t > 0.0:
		return
	if queue.is_empty():
		print("SKILLTEST %s done, summons up %d, form '%s'" % [Game.ch.class_id, p.summons.size(), p.form])
		for l in log_lines:
			print("  " + l)
		get_tree().quit()
		return
	var sid: String = queue.pop_front()
	Game.ch.mana = Game.ch.d.mana_max
	Game.ch.hp = Game.ch.d.hp_max
	p.hp = Game.ch.hp
	p.cooldowns.clear()
	p.action_t = 0.0
	var target := p.global_position + Vector2(170, 0)
	for m in lv.monsters:
		if not m.dead:
			target = m.global_position
			break
	if lv.monsters.filter(func(m): return not m.dead).size() < 2:
		lv.spawn_monster("kostlivy_havir", lv.cell_center(lv._nearest_open(lv.to_cell(p.global_position + Vector2(180, 20)))), 10)
	var typ := str(DB.skill(sid).get("type", ""))
	var ok := Skills.use(p, sid, target) if typ != "passive" else true
	log_lines.append("%-18s %-10s %s" % [sid, typ, "ok" if ok else "REFUSED"])
	t = 1.0
