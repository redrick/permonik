class_name Hireling
extends Actor

const SLOTS := ["weapon", "head", "body"]

var kind := ""
var def := {}
var dmg := Vector2(2, 5)
var to_hit := 20
var attack_range := 60.0
var cd := 0.0
var target: Monster = null
var think_t := 0.0
var repath_t := 0.0
var regen_t := 0.0


# Everything the hireling's numbers come from, also shown in its panel.
static func stats(m: Dictionary, lvl: int) -> Dictionary:
	var d: Dictionary = DB.hirelings.get(str(m.get("type", "")), {})
	var eq: Dictionary = m.get("equip", {})
	var hp: Array = d.get("hp", [60, 10])
	var ar: Array = d.get("armor", [4, 2])
	var dm: Array = d.get("dmg", [2, 6])
	var th: Array = d.get("to_hit", [20, 7])
	var out := {"hp": float(hp[0]) + float(hp[1]) * lvl, "armor": int(float(ar[0]) + float(ar[1]) * lvl),
		"to_hit": int(float(th[0]) + float(th[1]) * lvl), "dmg": Vector2(float(dm[0]) + lvl * 0.6, float(dm[1]) + lvl * 1.4)}
	var w: Item = eq.get("weapon", null)
	if w and weapon_ok(m, w):
		out.dmg = w.damage_range() * (1.0 + lvl * 0.03)
	for sl in ["head", "body"]:
		var it: Item = eq.get(sl, null)
		if it and not it.broken():
			out.armor += it.total_armor()
	for sl in eq:
		var it: Item = eq[sl]
		if it == null or it.broken():
			continue
		var sm := it.stat_mods()
		out.hp += float(sm.get("hp", 0.0)) + float(sm.get("vitalita", 0.0)) * 3.0
		out.to_hit += int(sm.get("to_hit", 0.0))
	return out


static func weapon_ok(m: Dictionary, it: Item) -> bool:
	var d: Dictionary = DB.hirelings.get(str(m.get("type", "")), {})
	return it.slot() == "weapon" and it.kind() in d.get("weapons", []) and str(it.base().get("class", "")) == ""


static func slot_ok(m: Dictionary, it: Item, sl: String) -> bool:
	if sl == "weapon":
		return weapon_ok(m, it)
	return it.slot() == sl and str(it.base().get("class", "")) == ""


static func cost(m_type: String, lvl: int) -> int:
	var c: Array = DB.hirelings.get(m_type, {}).get("cost", [120, 40])
	return int(c[0]) + int(c[1]) * lvl


func setup(lv: Node) -> void:
	level = lv
	team = 0
	radius = 14.0
	stride_len = 40.0
	collision_layer = 2
	collision_mask = 1 | 4
	var m: Dictionary = Game.ch.merc
	kind = str(m.type)
	def = DB.hirelings.get(kind, {})
	display_name = str(m.get("name", L.t(def.get("name", ""))))
	attack_range = float(def.get("range", 60))
	refresh(true)
	modulate = Color(0.92, 0.95, 1.0)


func _gear() -> Dictionary:
	var g := {}
	for sl in SLOTS:
		var it: Item = Game.ch.merc.get("equip", {}).get(sl, null)
		if it:
			var bd := it.base()
			g[sl] = str(bd.get("look", bd.get("icon", "")))
	return g


# Re-reads level, gear and life share; called on spawn and whenever the gear changes.
func refresh(first := false) -> void:
	var s := stats(Game.ch.merc, Game.ch.level)
	var share := float(Game.ch.merc.get("hp", 1.0)) if first else hp / maxf(1.0, hp_max)
	hp_max = s.hp
	hp = maxf(1.0, hp_max * clampf(share, 0.05, 1.0))
	armor = s.armor
	dmg = s.dmg
	to_hit = s.to_hit
	mlvl = Game.ch.level
	var textures := HeroLook.textures(str(def.get("look", "havir")), _gear())
	if textures.is_empty():
		textures["idle"] = DB.placeholder("merc", Vector2i(110, 180), Color("8a9aa8"))
	if sprite == null:
		setup_visual(textures, true, 46.0)
		sprite.scale = Vector2.ONE * 0.92
	else:
		tex = textures
		var t: Texture2D = tex.get(pose + view, tex.get(pose, tex.get("idle")))
		sprite.texture = t
		sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)


func top_pos() -> Vector2:
	return global_position + Vector2(0, -112)


var hpbar: Node2D


func _process(delta: float) -> void:
	super._process(delta)
	if hpbar == null:
		hpbar = Node2D.new()
		hpbar.z_index = 35
		var mat := CanvasItemMaterial.new()
		mat.light_mode = CanvasItemMaterial.LIGHT_MODE_UNSHADED
		hpbar.material = mat
		hpbar.position = Vector2(0, -120)
		hpbar.draw.connect(func():
			var r := Rect2(-24, 0, 48, 5)
			hpbar.draw_rect(r.grow(1.5), Color(0.05, 0.03, 0.03, 0.85))
			hpbar.draw_rect(Rect2(r.position, Vector2(48 * clampf(hp / hp_max, 0.0, 1.0), 5)), Color("5fb04a")))
		add_child(hpbar)
	hpbar.visible = not dead
	hpbar.queue_redraw()


func _ai(delta: float) -> void:
	cd = maxf(0.0, cd - delta)
	var p: Player = level.player
	if p == null or p.dead or Game.paused_ui:
		velocity = Vector2.ZERO
		moving = false
		return
	_regen(delta)
	var dp := global_position.distance_to(p.global_position)
	if dp > 900.0:
		var spot: Vector2 = level.random_open_near(p.global_position, 50.0, 110.0)
		global_position = spot if spot != Vector2.INF else p.global_position
		target = null
		return
	if not can_act():
		velocity = Vector2.ZERO
		moving = false
		return
	think_t -= delta
	if think_t <= 0.0:
		think_t = 0.35
		target = _pick_target(p)
	if target and (target.dead or not is_instance_valid(target)):
		target = null
	if target and dp < 560.0:
		_fight(delta)
		return
	_follow(p, dp, delta)


func _pick_target(p: Player) -> Monster:
	var best: Monster = null
	var bd := INF
	for m in level.monsters:
		if m.dead or not m.visible or m.sight < 0.5:
			continue
		var d: float = m.global_position.distance_to(global_position)
		if d > 460.0 or m.global_position.distance_to(p.global_position) > 520.0:
			continue
		if not m.aggro and d > 200.0:
			continue
		if d < bd:
			bd = d
			best = m
	return best


func _fight(delta: float) -> void:
	var d := global_position.distance_to(target.global_position)
	var ranged := str(def.get("ai", "melee")) == "ranged"
	var los: bool = level.line_of_sight(global_position, target.global_position)
	if d <= attack_range + target.radius and (los or not ranged):
		velocity = Vector2.ZERO
		moving = false
		face_to(target.global_position)
		if cd <= 0.0 and swing_t < 0.0:
			cd = 1.25 if ranged else 1.05
			var tg := target
			play_swing(0.45, 0.22, "attack", "shoot" if ranged else "melee")
			get_tree().create_timer(0.22).timeout.connect(func(): _strike(tg))
		return
	_go_to(target.global_position, delta, 1.0)


func _strike(t: Monster) -> void:
	if dead or t == null or not is_instance_valid(t) or t.dead:
		return
	if str(def.get("ai", "melee")) == "ranged":
		var w: Item = Game.ch.merc.get("equip", {}).get("weapon", null)
		var fx := "bolt" if w and w.kind() == "crossbow" else "arrow"
		Sfx.play_at("bolt_shot" if fx == "bolt" else "arrow_shot", global_position, 0.6)
		Projectile.spawn(level, global_position, t.global_position - global_position, 680.0, fx, 1, func(a, _p): _hit(a))
		return
	if global_position.distance_to(t.global_position) <= attack_range + t.radius + 24.0:
		Sfx.play_at("swing_light", global_position, 0.5)
		_hit(t)


func _hit(a: Actor) -> void:
	if a == null or a.dead:
		return
	if randf() > Combat.hit_chance(mlvl, a.mlvl, float(to_hit), float(a.armor)):
		level.miss_text(a.top_pos(), L.t({"cs": "vedle", "en": "miss"}))
		return
	var ranged := str(def.get("ai", "melee")) == "ranged"
	var dealt := a.take_damage(randf_range(dmg.x, dmg.y), "physical", self, {"knock": 0.0 if ranged else 60.0})
	if dealt > 0.0:
		Fx.impact(level, a, "physical", false)
		Sfx.play_at(a.get_meta("hit_sfx", "hit_flesh"), a.global_position, 0.6)


func _follow(p: Player, dp: float, delta: float) -> void:
	var keep := 150.0 if str(def.get("ai", "melee")) == "ranged" else 95.0
	if dp < keep:
		velocity = Vector2.ZERO
		moving = false
		path = []
		return
	_go_to(p.global_position - (p.global_position - global_position).normalized() * keep * 0.7, delta, 1.08 if dp < 300.0 else 1.35)


func _go_to(where: Vector2, delta: float, spd: float) -> void:
	repath_t -= delta
	if level.line_of_sight(global_position, where):
		path = [where]
	elif repath_t <= 0.0 or path.is_empty():
		repath_t = 0.5
		set_path_to(where)
	follow_path(delta, 210.0 * spd * speed_mult())
	if velocity.length() > 1.0:
		face_to(global_position + velocity)


func _regen(delta: float) -> void:
	regen_t -= delta
	if regen_t > 0.0:
		return
	regen_t = 1.0
	var calm := target == null
	heal(hp_max * (0.12 if level.is_town else (0.02 if calm else 0.005)))
	Game.ch.merc.hp = hp / maxf(1.0, hp_max)


func take_damage(amount: float, element := "physical", source: Node = null, opts := {}) -> float:
	var dealt := super.take_damage(amount, element, source, opts)
	if not dead:
		Game.ch.merc.hp = hp / maxf(1.0, hp_max)
	return dealt


func die(killer: Node) -> void:
	if dead:
		return
	Game.ch.merc.dead = true
	Game.ch.merc.hp = 1.0
	var f := str(def.get("gender", "m")) == "f"
	Game.msg(L.t({"cs": "%s padl%s. V krčmě %s můžeš oživit." % [display_name, "a" if f else "", "ji" if f else "ho"], "en": "%s has fallen. You can revive %s at the inn." % [display_name, "her" if f else "him"]}), Color("e08060"))
	super.die(killer)
