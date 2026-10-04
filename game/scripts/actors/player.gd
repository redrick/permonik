class_name Player
extends Actor

var lamp: PointLight2D
var cam: Camera2D
var look_key := ""
var form := ""
var intent := {}
var lmb_down := false
var action_t := 0.0
var action_hit_at := 0.0
var action_cb: Callable
var cooldowns := {}
var step_t := 0.0
var regen_acc := 0.0
var summons: Array = []
var invuln := 0.0
var hover_target = null
var light_mult := 1.0

signal hit_taken(amount: float)


func setup(lv: Node) -> void:
	level = lv
	team = 0
	radius = 15.0
	collision_layer = 2
	collision_mask = 1 | 4 | 8
	var cid := Game.ch.class_id
	look_key = HeroLook.key(cid, HeroLook.gear_of(Game.ch))
	var textures := HeroLook.textures(cid, HeroLook.gear_of(Game.ch))
	if textures.is_empty():
		textures["idle"] = DB.placeholder("hero", Vector2i(120, 200), Color("c9b48a"))
	setup_visual(textures, true, 50.0)
	display_name = Game.ch.hero_name
	Game.ch.changed.connect(_refresh_look)
	lamp = Fx.make_light(Color("ffcf8a"), 200.0, 1.15, true)
	lamp.position = Vector2(0, -60)
	lamp.range_item_cull_mask = 1
	add_child(lamp)
	cam = Camera2D.new()
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 7.0
	add_child(cam)
	cam.make_current()
	Game.ch.changed.connect(_on_char_changed)
	_on_char_changed()


func _exit_tree() -> void:
	if Game.ch.changed.is_connected(_on_char_changed):
		Game.ch.changed.disconnect(_on_char_changed)


func _on_char_changed() -> void:
	var d: Dictionary = Game.ch.d
	hp_max = d.hp_max
	hp = Game.ch.hp
	armor = d.armor
	mlvl = Game.ch.level
	for e in ["fire", "lightning", "cold", "poison"]:
		resist[e] = d.get("res_" + e, 0)
	_update_lamp()


func _update_lamp() -> void:
	var lr := float(Game.ch.d.get("light_radius", 2.0))
	if status.has("darkness"):
		lr *= 0.55
	lr *= light_mult
	if level and level.is_town:
		lr = maxf(lr, 7.0)
	var target := clampf(lr, 1.2, 12.0) * 64.0
	var l: Item = Game.ch.equip.get("lamp", null)
	var cold := l != null and l.base_id == "permonikuv_kahan"
	lamp.color = Color("d9ecff") if cold else Color("ffcf8a")
	lamp.texture_scale = lerpf(lamp.texture_scale, target * 2.0 / 256.0, 0.2)


func light_radius_px() -> float:
	return lamp.texture_scale * 128.0


func take_damage(amount: float, element := "physical", source: Node = null, opts := {}) -> float:
	if invuln > 0.0:
		return 0.0
	var dealt := super.take_damage(amount, element, source, opts)
	Game.ch.hp = hp
	if dealt > 0.0:
		hit_taken.emit(dealt)
	if dealt > 0.0 and not opts.get("dot", false):
		Sfx.play("player_hurt", 0.6)
		if pose_t <= 0.0:
			set_pose("hit", 0.18)
	return dealt


func _modify_incoming(amount: float, _element: String, _source: Node, _opts: Dictionary) -> float:
	var dodge := float(Game.ch.d.get("dodge", 0.0)) + float(Game.ch.d.get("dodge_pct", 0.0)) + float(Game.ch.d.get("evade", 0.0))
	if dodge > 0.0 and randf() * 100.0 < minf(dodge, 60.0):
		level.float_text(top_pos(), L.t({"cs": "úskok", "en": "evade"}), Color("c8e0a0"), true)
		return 0.0
	return amount


func heal(amount: float) -> void:
	super.heal(amount)
	Game.ch.hp = hp


func die(_killer: Node) -> void:
	if dead:
		return
	dead = true
	Game.ch.hp = 0
	set_pose("dead")
	collision_layer = 0
	Sfx.play("player_death")
	if shadow:
		shadow.visible = false
	if Game.main:
		Game.main.on_player_died()


func _unhandled_input(event: InputEvent) -> void:
	if dead or Game.paused_ui:
		return
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			lmb_down = event.pressed
			if event.pressed:
				_on_left_click()
				get_viewport().set_input_as_handled()
		elif event.button_index == MOUSE_BUTTON_RIGHT and event.pressed:
			use_skill(Game.ch.rmb)
			get_viewport().set_input_as_handled()
	elif event is InputEventKey and event.pressed and not event.echo:
		for i in 8:
			if event.is_action("belt_%d" % (i + 1)):
				use_belt(i)
				return
		var keys := ["skill_q", "skill_w", "skill_e", "skill_r"]
		for i in 4:
			if event.is_action(keys[i]) and Game.ch.hotkeys[i] != "":
				use_skill(Game.ch.hotkeys[i])
				return
		if event.is_action("town_portal"):
			_use_portal_scroll()


func mouse_world() -> Vector2:
	return get_global_mouse_position()


func _on_left_click() -> void:
	var m := mouse_world()
	if Input.is_action_pressed("stand"):
		intent = {"type": "stand_attack", "pos": m}
		return
	var pick = level.pick_at(m)
	if pick:
		intent = {"type": pick.type, "node": pick.node}
		if pick.type == "monster" and _in_attack_range(pick.node):
			return
		set_path_to(pick.node.global_position)
	else:
		intent = {"type": "move", "pos": m}
		set_path_to(m)


func _in_attack_range(t: Node2D) -> bool:
	var w := Game.ch.weapon()
	if w and w.is_ranged():
		return level.line_of_sight(global_position, t.global_position) and global_position.distance_to(t.global_position) < 900
	return global_position.distance_to(t.global_position) <= 62.0 + (t.radius if t is Actor else 20.0)


func _ai(delta: float) -> void:
	var ch := Game.ch
	invuln = maxf(0.0, invuln - delta)
	ch.tick_buffs(delta)
	if ch.active_form() != form:
		form = ch.active_form()
		_apply_form()
	for k in cooldowns.keys():
		cooldowns[k] -= delta
		if cooldowns[k] <= 0.0:
			cooldowns.erase(k)
	regen_acc += delta
	if regen_acc >= 0.25:
		var hr := float(ch.d.get("hp_regen", 0.0)) * regen_acc
		ch.hp = minf(ch.d.hp_max, ch.hp + hr)
		ch.mana = minf(ch.d.mana_max, ch.mana + ch.d.mana_max * 0.012 * regen_acc * (1.0 + float(ch.d.get("mana_regen", 0.0)) / 100.0))
		hp = ch.hp
		regen_acc = 0.0
	petrify = maxf(0.0, petrify - delta * 0.18)
	var curse := 30 if status.has("cursed") else 0
	for e in ["fire", "lightning", "cold", "poison"]:
		resist[e] = int(ch.d.get("res_" + e, 0)) - curse
	_update_lamp()
	if action_t > 0.0:
		var prev := action_t
		action_t -= delta / maxf(0.3, 1.0 if not status.has("chill") else 1.4)
		if prev > action_hit_at and action_t <= action_hit_at and action_cb.is_valid():
			var cb := action_cb
			action_cb = Callable()
			cb.call()
		velocity = Vector2.ZERO
		moving = false
		return
	if not can_act():
		velocity = Vector2.ZERO
		moving = false
		return
	_gold_t -= delta
	if _gold_t <= 0.0:
		_gold_t = 0.15
		level.collect_gold_near(global_position, 56.0)
	if lmb_down and not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		lmb_down = false
	var spd := 210.0 * (1.0 + float(ch.d.get("move_speed", 0.0)) / 100.0) * speed_mult()
	match intent.get("type", ""):
		"move":
			if lmb_down and int(anim_t * 10.0) % 2 == 0:
				var m := mouse_world()
				if m.distance_to(global_position) > 24 and (path.is_empty() or path.back().distance_to(m) > 40):
					set_path_to(m)
			if follow_path(delta, spd) and not lmb_down:
				intent = {}
		"stand_attack":
			face_to(intent.pos)
			basic_attack(null, intent.pos)
			if not lmb_down:
				intent = {}
			else:
				intent.pos = mouse_world()
		"monster":
			var t: Actor = intent.node if is_instance_valid(intent.node) else null
			if t == null or t.dead:
				intent = {}
				velocity = Vector2.ZERO
				moving = false
				return
			if _in_attack_range(t):
				path.clear()
				basic_attack(t, t.global_position)
				if not lmb_down:
					intent = {"type": "_done"}
			else:
				repath_soon(t.global_position)
				follow_path(delta, spd)
		"npc", "item", "prop":
			var n: Node2D = intent.node if is_instance_valid(intent.node) else null
			if n == null:
				intent = {}
				return
			var reach := 84.0 if intent.type != "prop" else 54.0 + float(n.get_meta("reach", 0.0))
			if global_position.distance_to(n.global_position) <= reach:
				path.clear()
				velocity = Vector2.ZERO
				moving = false
				var t: String = intent.type
				intent = {}
				level.interact(self, t, n)
			elif follow_path(delta, spd):
				var t2: String = intent.type
				var retried := bool(intent.get("retried", false))
				intent = {}
				if global_position.distance_to(n.global_position) <= reach + 50:
					level.interact(self, t2, n)
				elif t2 == "item" and not retried:
					intent = {"type": "item", "node": n, "retried": true}
					set_path_to(n.global_position)
		"_done":
			velocity = Vector2.ZERO
			moving = false
			if not lmb_down:
				intent = {}
		_:
			velocity = Vector2.ZERO
			moving = false
	if moving:
		step_t -= delta
		if step_t <= 0.0:
			step_t = 0.36
			Sfx.play("footstep_water" if level.is_water(global_position) else "step_stone_%d" % randi_range(1, 3), 0.25)


var _repath := 0.0
var _gold_t := 0.0


func repath_soon(target: Vector2) -> void:
	_repath -= get_physics_process_delta_time()
	if _repath <= 0.0 or path.is_empty():
		_repath = 0.3
		set_path_to(target)


func start_action(pose_name: String, duration: float, hit_frac: float, cb: Callable) -> void:
	action_t = duration
	action_hit_at = duration * (1.0 - hit_frac)
	action_cb = cb
	set_pose(pose_name, duration)


func basic_attack(target: Actor, pos: Vector2) -> void:
	if action_t > 0.0:
		return
	face_to(pos)
	var w := Game.ch.weapon()
	var dur := 1.0 / float(Game.ch.d.get("aps", 1.2))
	if w and w.is_ranged():
		start_action("attack", dur, 0.5, func(): Skills.fire_weapon(self, pos, 100.0))
		return
	lunge = 8.0
	start_action("attack", dur, 0.55, func():
		Sfx.play_at("swing", global_position, 0.7)
		if target and is_instance_valid(target) and not target.dead:
			Combat.player_strike(self, target)
		else:
			var hits := Combat.targets_in_cone(level, global_position, (pos - global_position).normalized(), 80.0, 70.0, 1)
			if hits.size() > 0:
				Combat.player_strike(self, hits[0]))


func use_skill(id: String) -> void:
	if id == "" or action_t > 0.0 or not can_act():
		return
	if id == "utok":
		var pick = level.pick_at(mouse_world())
		basic_attack(pick.node if pick and pick.type == "monster" else null, mouse_world())
		return
	Skills.use(self, id, mouse_world())


func use_belt(i: int) -> void:
	var ch := Game.ch
	if i >= ch.belt_size() or ch.belt[i] == null:
		return
	var it: Item = ch.belt[i]
	if use_item(it):
		ch.belt[i] = null
		for j in range(i + 1, ch.belt_size()):
			if ch.belt[j] and ch.belt[j].base_id == it.base_id and ch.belt[i] == null:
				ch.belt[i] = ch.belt[j]
				ch.belt[j] = null
		ch.changed.emit()


func use_item(it: Item) -> bool:
	var ch := Game.ch
	var u: Dictionary = it.base().get("use", {})
	if u.is_empty():
		return false
	if u.has("heal_pct"):
		ch.hp = minf(ch.d.hp_max, ch.hp + ch.d.hp_max * float(u.heal_pct) / 100.0)
		hp = ch.hp
		Fx.burst(level, global_position + Vector2(0, -50), Color("ff5050"), 12, 60.0, 0.7, 0.2, true)
	if u.has("mana_pct"):
		ch.mana = minf(ch.d.mana_max, ch.mana + ch.d.mana_max * float(u.mana_pct) / 100.0)
		Fx.burst(level, global_position + Vector2(0, -50), Color("5080ff"), 12, 60.0, 0.7, 0.2, true)
	if u.has("rejuv"):
		ch.hp = ch.d.hp_max
		ch.mana = ch.d.mana_max
		hp = ch.hp
		status.clear()
		petrify = 0.0
		Fx.burst(level, global_position + Vector2(0, -50), Color("a0ff90"), 20, 80.0, 0.9, 0.25, true)
	if u.has("portal"):
		if level.is_town:
			Game.msg(L.t("cant_use"))
			return false
		level.open_portal(global_position)
	if u.has("identify"):
		if Game.main:
			Game.main.start_identify_cursor()
		return true
	if u.has("respec"):
		ch.respec()
	Sfx.play("potion")
	ch.changed.emit()
	return true


func _use_portal_scroll() -> void:
	for it in Game.ch.inv.items:
		if it.base().get("use", {}).has("portal"):
			if use_item(it):
				Game.ch.inv.remove(it)
				Game.ch.changed.emit()
			return


func _animate(delta: float) -> void:
	super._animate(delta)
	if petrify > 0.0:
		mat_set("stone", clampf(petrify, 0.0, 1.0))


# A shapeshift wears a monster's drawings until it ends; then the hero's own (with their gear) return.
func _apply_form() -> void:
	if form == "":
		look_key = ""
		_refresh_look()
		return
	var tx := {}
	for p in ["idle", "walk", "attack"]:
		var t := DB.tex("sprites/monsters/%s_%s" % [form, p])
		if t:
			tx[p] = t
	if not tx.has("idle"):
		return
	tex = {"idle": tx.idle, "walk1": tx.get("walk", tx.idle), "walk2": tx.idle, "attack": tx.get("attack", tx.idle),
		"cast": tx.get("attack", tx.idle), "hit": tx.idle, "dead": tx.idle}
	var t: Texture2D = tex.get(pose, tex.idle)
	sprite.texture = t
	sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)
	Fx.burst(level, global_position + Vector2(0, -50), Color("8a7a6a"), 24, 140.0, 0.5, 0.3)


# Re-dress the sprite when the worn gear changes.
func _refresh_look() -> void:
	if form != "":
		return
	var gear := HeroLook.gear_of(Game.ch)
	var k := HeroLook.key(Game.ch.class_id, gear)
	if k == look_key:
		return
	look_key = k
	var textures := HeroLook.textures(Game.ch.class_id, gear)
	if textures.is_empty():
		return
	tex = textures
	var t: Texture2D = tex.get(pose, tex.get("idle"))
	if t:
		sprite.texture = t
		sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)


func hit_divisor() -> float:
	return 12.0


# 0.4 s base stagger, shortened by faster hit recovery (already diminished in CharData).
func hit_recovery_time() -> float:
	return 0.4 / (1.0 + float(Game.ch.d.get("hit_recovery", 0.0)) / 100.0)


# A staggering blow breaks off the swing or spell in progress, as in D2.
func _on_hit_recover() -> void:
	action_t = 0.0
	action_cb = Callable()
	set_pose("hit", stun_t)
