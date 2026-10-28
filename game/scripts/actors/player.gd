class_name Player
extends Actor

var lamp: PointLight2D
var cam: Camera2D
var look_key := ""
var form := ""
var intent := {}
var lmb_down := false
var pad_hold := false
var move_dir := Vector2.RIGHT
var _pad_scan := 0.0
var action_t := 0.0
var action_hit_at := 0.0
var action_cb: Callable
var action_cancel := false
# A skill pressed while busy (mid-swing, staggered, cooldown nearly over) fires as soon as the hero is free.
var queued := {}
var held_skill := ""
var held_key := ""
const QUEUE_TIME := 0.5
var cooldowns := {}
var step_t := 0.0
var regen_acc := 0.0
var summons: Array = []
var invuln := 0.0
# After a stagger the hero can't be staggered again for a moment, so a pack can't lock them in place.
var stagger_guard := 0.0
var hover_target = null
var light_mult := 1.0

signal hit_taken(amount: float)


func setup(lv: Node) -> void:
	level = lv
	team = 0
	radius = 15.0
	stride_len = 40.0
	casts = false
	collision_layer = 2
	collision_mask = 1 | 4
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
	if Game.main:
		cam.zoom = Vector2.ONE * Game.main.world_zoom()
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


# Leads a little in the walking direction; leans in when a boss fight is on.
func _update_cam(delta: float) -> void:
	if cam == null or level == null:
		return
	var lead := move_dir * 70.0 if moving else Vector2.ZERO
	cam.position = cam.position.lerp(lead, minf(1.0, delta * (1.6 if moving else 0.8)))
	var b = level.boss
	var fight: bool = b != null and is_instance_valid(b) and not b.dead and b.aggro and b.global_position.distance_to(global_position) < 700.0
	var z: float = (1.1 if fight else 1.0) * (Game.main.world_zoom() if Game.main else 1.0)
	cam.zoom = cam.zoom.lerp(Vector2(z, z), minf(1.0, delta * 1.5))


func top_pos() -> Vector2:
	return global_position + Vector2(0, -122 - float_h)


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
	reset_rig()
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
			held_skill = Game.ch.rmb
			held_key = ""
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
				held_skill = Game.ch.hotkeys[i]
				held_key = keys[i]
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


func _tick(delta: float) -> void:
	var ch := Game.ch
	invuln = maxf(0.0, invuln - delta)
	stagger_guard = maxf(0.0, stagger_guard - delta)
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
	# the press is kept while the hero is busy (up to a cap), and for a short moment once they're free
	if not queued.is_empty():
		queued.life -= delta
		if action_t <= 0.0 and can_act():
			queued.t -= delta
		if queued.t <= 0.0 or queued.life <= 0.0:
			queued = {}


func _ai(delta: float) -> void:
	var ch := Game.ch
	# a basic swing that has already landed gives way to a skill
	if action_t > 0.0 and action_cancel and not action_cb.is_valid() and not queued.is_empty() and queued.id != "utok":
		action_t = 0.0
	if action_t > 0.0:
		var prev := action_t
		swing_speed = 1.0 if not status.has("chill") else 1.0 / 1.4
		action_t -= delta * swing_speed
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
	if queued.is_empty():
		_repeat_held()
	if not queued.is_empty() and not cooldowns.has(queued.id):
		var q := queued
		queued = {}
		var at: Vector2 = q.at
		if q.node and is_instance_valid(q.node) and not q.node.dead:
			at = q.node.center_pos()
		_fire_skill(q.id, at)
		if action_t > 0.0:
			velocity = Vector2.ZERO
			moving = false
			return
		# nothing started (no mana, nobody in reach): a held key tries again a little later
		_repeat_wait = 0.4
	if lmb_down and not Input.is_mouse_button_pressed(MOUSE_BUTTON_LEFT):
		lmb_down = false
	var spd := 210.0 * (1.0 + float(ch.d.get("move_speed", 0.0)) / 100.0) * speed_mult()
	match intent.get("type", ""):
		"move":
			_hold_t -= delta
			if lmb_down and _hold_t <= 0.0:
				_hold_t = 0.12
				var m := mouse_world()
				if m.distance_to(global_position) > 24 and (path.is_empty() or path.back().distance_to(m) > 40):
					set_path_to(m)
			if follow_path(delta, spd) and not lmb_down:
				intent = {}
		"stand_attack":
			face_to(intent.pos)
			basic_attack(null, intent.pos)
			if not _held():
				intent = {}
			elif lmb_down:
				intent.pos = mouse_world()
		"monster":
			var t: Actor = intent.node if is_instance_valid(intent.node) else null
			if (t == null or t.dead) and lmb_down:
				# still holding after a kill: carry on with whatever is under the cursor
				var pk = level.pick_at(mouse_world())
				t = pk.node if pk and pk.type == "monster" else null
				intent = {"type": "monster", "node": t} if t else {"type": "_done"}
			if t == null or t.dead:
				if intent.get("type", "") != "_done":
					intent = {}
				velocity = Vector2.ZERO
				moving = false
				return
			if _in_attack_range(t):
				path.clear()
				if intent.has("skill"):
					var sid: String = intent.skill
					intent.erase("skill")
					_fire_skill(sid, t.center_pos())
				else:
					basic_attack(t, t.global_position)
				if not _held():
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
		"stick":
			var dv: Vector2 = intent.dir
			path.clear()
			velocity = dv * spd
			moving = dv.length() > 0.05
			if moving:
				face_to(global_position + dv)
		"_done":
			velocity = Vector2.ZERO
			moving = false
			if not _held():
				intent = {}
		_:
			velocity = Vector2.ZERO
			moving = false
	if velocity.length() > 1.0:
		move_dir = velocity.normalized()
	# pushing into a corner or a body without getting anywhere: find the way again
	if moving and not path.is_empty() and get_real_velocity().length() < 25.0:
		_stuck += delta
		if _stuck > 0.3:
			_stuck = 0.0
			set_path_to(path.back())
	else:
		_stuck = 0.0
	if moving and not tex.has("walk4"):
		step_t -= delta
		if step_t <= 0.0:
			step_t = 0.36
			Sfx.play(_step_sfx(), 0.22, 0.12)


func _footfall() -> void:
	Sfx.play(_step_sfx(), 0.18, 0.12)
	if not level.is_water(global_position):
		Fx.scuff(level, global_position + Vector2(facing * 8.0 if view == "" else 0.0, 2.0), 30.0)


func _step_sfx() -> String:
	if level.is_water(global_position):
		return "footstep_water"
	if level.is_town:
		return "footstep_grass" if randf() < 0.25 else "footstep_dirt"
	return "footstep_rock" if randf() < 0.4 else "step_stone_%d" % randi_range(1, 3)


var _repath := 0.0
var _hold_t := 0.0
var _stuck := 0.0
var _repeat_wait := 0.0
var _gold_t := 0.0


func repath_soon(target: Vector2) -> void:
	_repath -= get_physics_process_delta_time()
	if _repath <= 0.0 or path.is_empty():
		_repath = 0.3
		set_path_to(target)


func start_action(pose_name: String, duration: float, hit_frac: float, cb: Callable, style := "") -> void:
	action_cancel = false
	action_t = duration
	action_hit_at = duration * (1.0 - hit_frac)
	action_cb = cb
	if style == "":
		style = "cast" if pose_name == "cast" else "melee"
	play_swing(duration, duration * hit_frac, pose_name, style)


func basic_attack(target: Actor, pos: Vector2) -> void:
	if action_t > 0.0:
		return
	face_to(pos)
	var w := Game.ch.weapon()
	var dur := 1.0 / float(Game.ch.d.get("aps", 1.2))
	if w and w.is_ranged():
		start_action("attack", dur, 0.5, func(): Skills.fire_weapon(self, pos, 100.0), "shoot")
		action_cancel = true
		return
	start_action("attack", dur, 0.55, func():
		Sfx.play_at("swing_heavy" if dur > 0.85 else "swing_light", global_position, 0.6)
		if target and is_instance_valid(target) and not target.dead:
			Combat.player_strike(self, target)
		else:
			var hits := Combat.targets_in_cone(level, global_position, (pos - global_position).normalized(), 80.0, 70.0, 1)
			if hits.size() > 0:
				Combat.player_strike(self, hits[0]))
	action_cancel = true


func use_skill(id: String, at := Vector2.INF) -> void:
	if id == "" or dead:
		return
	if at == Vector2.INF:
		at = mouse_world()
	if action_t > 0.0 and action_cancel and not action_cb.is_valid() and id != "utok" and can_act():
		action_t = 0.0
	if action_t > 0.0 or not can_act() or float(cooldowns.get(id, 0.0)) > 0.0:
		if float(cooldowns.get(id, 0.0)) <= QUEUE_TIME:
			var pick = level.pick_at(at)
			queued = {"id": id, "at": at, "node": pick.node if pick and pick.type == "monster" else null, "t": QUEUE_TIME, "life": 1.5}
		return
	queued = {}
	_fire_skill(id, at)


# Holding the right button or a skill key keeps using the skill, at the cursor.
func _repeat_held() -> void:
	_repeat_wait -= get_physics_process_delta_time()
	if held_skill == "" or _repeat_wait > 0.0:
		return
	var still := Input.is_action_pressed(held_key) if held_key != "" else Input.is_mouse_button_pressed(MOUSE_BUTTON_RIGHT)
	if not still:
		held_skill = ""
		return
	if intent.has("skill") or float(cooldowns.get(held_skill, 0.0)) > QUEUE_TIME:
		return
	queued = {"id": held_skill, "at": mouse_world(), "node": null, "t": QUEUE_TIME, "life": 1.5}


func _fire_skill(id: String, at: Vector2) -> void:
	if id == "utok":
		var pick = level.pick_at(at)
		var t: Actor = pick.node if pick and pick.type == "monster" else null
		if t and not _in_attack_range(t):
			intent = {"type": "monster", "node": t}
			set_path_to(t.global_position)
			return
		basic_attack(t, at)
		return
	Skills.use(self, id, at)


func _held() -> bool:
	return lmb_down or pad_hold


# ---------------------------------------------------------------- touch pad
func auto_target(reach := 520.0) -> Monster:
	var cur = intent.get("node") if intent.get("type", "") == "monster" else null
	var best: Monster = null
	var bs := INF
	for m in level.monsters:
		if m.dead or not m.visible or not level._targetable(m):
			continue
		var to: Vector2 = m.global_position - global_position
		var d := to.length()
		if d > reach or not level.line_of_sight(global_position, m.global_position):
			continue
		var s := d * (1.25 - 0.25 * move_dir.dot(to / maxf(d, 1.0)))
		if m == cur:
			s *= 0.6
		if s < bs:
			bs = s
			best = m
	return best


func nearest_interactable(reach := 240.0) -> Dictionary:
	var best := {}
	var bd := reach
	for pair in [["npc", level.npcs], ["item", level.ground_items], ["prop", level.props]]:
		for n in pair[1]:
			if not is_instance_valid(n) or (pair[0] == "prop" and (n.interact == "" or n.used)) or (pair[0] == "item" and not n.visible):
				continue
			var d: float = n.global_position.distance_to(global_position)
			if d < bd:
				bd = d
				best = {"type": pair[0], "node": n}
	return best


func pad_attack(first: bool) -> void:
	if dead or Game.paused_ui:
		return
	var t = intent.get("node") if intent.get("type", "") == "monster" else null
	if t and is_instance_valid(t) and not t.dead:
		return
	_pad_scan -= get_process_delta_time()
	if not first and _pad_scan > 0.0:
		return
	_pad_scan = 0.12
	var m := auto_target()
	if m:
		intent = {"type": "monster", "node": m}
		if not _in_attack_range(m):
			set_path_to(m.global_position)
		return
	if not first:
		return
	var n := nearest_interactable()
	if not n.is_empty():
		intent = n
		set_path_to(n.node.global_position)
		return
	path.clear()
	intent = {"type": "stand_attack", "pos": global_position + move_dir * 80.0}


func pad_aim(id: String) -> Vector2:
	var type := str(DB.skill(id).get("type", "melee"))
	var m := auto_target(300.0 if type in ["melee", "melee_arc", "spin", "stomp", "utok"] or id == "utok" else 700.0)
	if m:
		return m.center_pos()
	return global_position + move_dir * 220.0


func pad_skill(id: String, at := Vector2.INF) -> void:
	if id == "" or dead or Game.paused_ui:
		return
	use_skill(id, pad_aim(id) if at == Vector2.INF else at)


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
	_update_cam(delta)
	if petrify > 0.0:
		mat_set("stone", clampf(petrify, 0.0, 1.0))


# A shapeshift wears a monster's drawings until it ends; then the hero's own (with their gear) return.
func _apply_form() -> void:
	if form == "":
		look_key = ""
		_refresh_look()
		return
	var tx := Monster.load_tex(form)
	if not tx.has("idle"):
		return
	tex = {}
	for v in ["", "_f", "_b"]:
		if not tx.has("idle" + v):
			continue
		var idle: Texture2D = tx["idle" + v]
		for p in ["idle", "walk1", "walk2", "walk3", "walk4", "windup", "attack"]:
			if tx.has(p + v):
				tex[p + v] = tx[p + v]
		var atk: Texture2D = tx.get("attack" + v, idle)
		tex["cast" + v] = atk
		tex["hit" + v] = idle
	tex["dead"] = tx.idle
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
	var t: Texture2D = tex.get(pose + view, tex.get(pose, tex.get("idle")))
	if t:
		sprite.texture = t
		sprite.offset = Vector2(0, -t.get_height() / 2.0 + 8.0)


func hit_divisor() -> float:
	return 12.0


# 0.4 s base stagger, shortened by faster hit recovery (already diminished in CharData).
func hit_recovery_time() -> float:
	return 0.4 / (1.0 + float(Game.ch.d.get("hit_recovery", 0.0)) / 100.0)


func can_stagger() -> bool:
	return stagger_guard <= 0.0


# A staggering blow breaks off the swing or spell in progress, as in D2.
func _on_hit_recover() -> void:
	stagger_guard = stun_t + 0.8
	action_t = 0.0
	action_cb = Callable()
	action_cancel = false
	set_pose("hit", stun_t)
