extends Node

var t := 0.0
var kills := 0
var start_xp := 0
var skill_i := 0


func _ready() -> void:
	start_xp = Game.ch.xp
	get_tree().create_timer(float(_arg("--seconds", "25"))).timeout.connect(_report)


func _arg(k: String, d: String) -> String:
	var a := OS.get_cmdline_user_args()
	var i := a.find(k)
	return a[i + 1] if i >= 0 and i + 1 < a.size() else d


var dbg := 0.0


func _process(delta: float) -> void:
	dbg += delta
	if dbg > 1.0:
		dbg = 0.0
		var pl: Player = Game.player
		print("T paused=%s ui=%s pos=%s action=%.2f intent=%s hp=%d" % [get_tree().paused, Game.paused_ui, pl.global_position if pl else Vector2.ZERO, pl.action_t if pl else 0.0, pl.intent.get("type", "") if pl else "", Game.ch.hp])
	var p: Player = Game.player
	var lv: Level = Game.level
	if p == null or lv == null or p.dead:
		return
	t -= delta
	if t > 0.0:
		return
	t = 0.4
	Game.ch.hp = maxf(Game.ch.hp, Game.ch.d.hp_max * 0.5)
	p.hp = Game.ch.hp
	Game.ch.mana = Game.ch.d.mana_max
	var best: Monster = null
	var bd := INF
	for m in lv.monsters:
		var dd: float = m.global_position.distance_to(p.global_position)
		if not m.dead and dd < bd and not m.has_meta("skip"):
			bd = dd
			best = m
	if best == null:
		return
	if dbg == 0.0:
		print("  best=%s bd=%.0f vis=%s" % [best.id, bd, best.visible])
	if bd > 700:
		var tp: Vector2 = lv.random_open_near(best.global_position, 120, 200)
		if tp == Vector2.INF:
			best.set_meta("skip", true)
		else:
			p.global_position = tp
		return
	var skills: Array = Game.ch.skills.keys()
	if randf() < 0.4 and skills.size() > 0:
		var sid: String = skills[skill_i % skills.size()]
		skill_i += 1
		Skills.use(p, sid, best.global_position)
	else:
		p.intent = {"type": "monster", "node": best}
		p.set_path_to(best.global_position)
		p.lmb_down = true


func _report() -> void:
	print("AUTOPLAY level=%d xp=%d gained=%d gold=%d monsters_left=%d inv=%d hp=%d" % [Game.ch.level, Game.ch.xp, Game.ch.xp - start_xp, Game.ch.gold, Game.level.monsters.size() if Game.level else -1, Game.ch.inv.items.size(), Game.ch.hp])
	for it in Game.ch.inv.items:
		print("  item: ", it.display_name(), " r=", it.rarity, " id=", it.identified)
	if Game.level:
		print("  ground items: ", Game.level.ground_items.size())
	get_tree().quit()
