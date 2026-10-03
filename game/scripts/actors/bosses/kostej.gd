extends BossBase

const FROST := Color("9fd8ff")
const DEATH := Color("7a5ab8")

var mortal := false
var hinted := false
var guard_t := 8.0
var oak: PropNode
var chest: PropNode


func _init_boss() -> void:
	set_meta("half_said", true)
	mortal = bool(Game.flags.get("kostej_needle_broken", false))
	var oaks := props_of("dub")
	var chests := props_of("truhla_kostej")
	oak = oaks[0] if oaks.size() > 0 else null
	chest = chests[0] if chests.size() > 0 else null
	if oak and chest:
		var c: Vector2i = level._find_free_near(oak.cell + Vector2i(2, 1), 0, 2)
		chest.cell = c
		chest.position = level.cell_center(c) + Vector2(0, Level.CELL / 2.0 - 10)
	if chest:
		chest.visible = false
		chest.interact = ""


func label_sub() -> String:
	return super.label_sub() + ("" if mortal else " · " + L.t({"cs": "nesmrtelný", "en": "deathless"}))


func _always_tick(delta: float) -> void:
	if not aggro:
		return
	if not mortal and not hinted and fight_t > 15.0:
		hinted = true
		say("half", 6.0)
	guard_t -= delta
	if guard_t <= 0.0 and can_act():
		guard_t = 18.0 if not mortal else 13.0
		if alive_minions().size() < 4:
			shout("Stráž!", "Guards!", DEATH)
			summon("kostejuv_nesmrtelny", 2, global_position, 90.0, 220.0)


func _modify_incoming(amount: float, elem: String, source: Node, opts: Dictionary) -> float:
	if not mortal:
		if source is Player and Game.ch.inv.count("vejce") > 0:
			_snap_needle.call_deferred()
			return 0.0
		note(L.t({"cs": "Nesmrtelný", "en": "Deathless"}), Color("cfd8e8"))
		Fx.burst(level, center_pos(), FROST, 4, 60.0, 0.3, 0.2)
		return 0.0
	return super._modify_incoming(amount, elem, source, opts)


func _snap_needle() -> void:
	if mortal:
		return
	mortal = true
	Game.ch.inv.take("vejce")
	Game.flags["kostej_needle_broken"] = true
	Game.give_item("kostejova_jehla")
	Game.ch.changed.emit()
	stun_t = 2.0
	windup = 0.0
	Sfx.play_at("hit_metal", global_position)
	Sfx.play_at("boss_roar", global_position)
	level.shake(12.0)
	Fx.ring(level, global_position, 260.0, DEATH, 0.8)
	Fx.burst(level, center_pos(), Color(1, 1, 1), 40, 260.0, 0.8, 0.35, true)
	level.float_text(top_pos(), L.t({"cs": "Jehla praskla!", "en": "The needle snaps!"}), Color("ffe7a0"))
	Game.msg(L.t({"cs": "Rozlomil jsi vejce a v něm jehlu. Kostěj je smrtelný.", "en": "You crack the egg and snap the needle inside. Koschei is mortal."}), Color("ffe7a0"))
	say_t("Jehla… Tak tedy. Zemři se mnou, poutníku, ať to nejsem já, kdo umírá sám.", "The needle… So be it. Die with me, wanderer, so I am not the only one dying.", 5.5)
	speed *= 1.2
	attack_cd *= 0.8
	phase = 2
	bar()


func _special(p: Actor, d: float) -> float:
	var r := randf()
	if r < 0.45:
		var tgt := p.global_position
		busy = 0.6
		set_pose("attack", 0.8)
		face_to(tgt)
		Fx.bolt(level, global_position + Vector2(0, -sprite_h * 0.6), tgt + Vector2(0, -20), DEATH, 2.0, 0.3)
		slam(tgt, 85.0, 1.0, 1.3, "cold", DEATH, {}, func(a): a.apply_status("slow", 2.0))
		return randf_range(3.0, 4.5)
	if d < 220.0:
		busy = 1.0
		set_pose("attack", 1.0)
		slam(global_position, 180.0, 0.95, 1.1, "cold", FROST, {"knock": 260.0}, func(a): a.apply_status("chill", 3.0))
		return randf_range(4.0, 5.5)
	if mortal:
		blink_to(open_spot_near(p.global_position, 90.0, 140.0), DEATH)
		return 2.0
	return 2.5


func on_quest_prop(prop: PropNode, p: Player) -> void:
	match prop.id:
		"dub":
			Game.on_event("use", "dub")
			if chest and not chest.visible:
				chest.visible = true
				chest.interact = "quest"
				Fx.burst(level, chest.global_position + Vector2(0, -20), Color("8a7458"), 20, 120.0, 0.6, 0.3)
				Sfx.play_at("chest_open", chest.global_position, 0.5)
			level.float_text(prop.global_position + Vector2(0, -150), L.t({"cs": "Mezi kořeny je zakopaná okovaná truhla.", "en": "An iron-bound chest is buried among the roots."}), Color("e9d8a6"))
		"truhla_kostej":
			if prop.used or not prop.visible:
				return
			_open_chest(prop, p)
		_:
			Game.on_event("use", prop.id)


func _open_chest(prop: PropNode, p: Player) -> void:
	prop.used = true
	prop.set_hover(false)
	prop.set_texture("truhla_open")
	Sfx.play_at("chest_open", prop.global_position)
	Game.on_event("use", "dub")
	Game.on_event("use", "truhla_kostej")
	var q := prop.global_position + (p.global_position - prop.global_position).normalized() * -50.0
	if level.is_solid(q):
		q = open_spot_near(prop.global_position, 40.0, 90.0)
	var hare := spawn_custom("res://scripts/actors/bosses/minion_fleer.gd", "vlk", q, maxi(1, mlvl - 4))
	hare.display_name = L.t({"cs": "Zajíc", "en": "Hare"})
	hare.speed = 180.0
	hare.no_drops = true
	hare.sprite.scale = Vector2(0.6, 0.6)
	hare.mat_set("tint", Color(1.25, 1.05, 0.8))
	hare.died.connect(_on_hare_died)
	Game.msg(L.t({"cs": "Z truhly vyskočil zajíc!", "en": "A hare leaps out of the chest!"}), Color("e9d8a6"))
	if aggro:
		say_t("Ne! Chyťte toho zajíce!", "No! Catch that hare!", 3.0)


func _on_hare_died(a: Actor) -> void:
	var duck := spawn_custom("res://scripts/actors/bosses/minion_fleer.gd", "netopyr", a.global_position, maxi(1, mlvl - 4))
	duck.display_name = L.t({"cs": "Kachna", "en": "Duck"})
	duck.speed = 190.0
	duck.no_drops = true
	duck.hp_max *= 3.0
	duck.hp = duck.hp_max
	duck.died.connect(_on_duck_died)
	Fx.burst(level, a.global_position + Vector2(0, -30), Color("d8d0b8"), 24, 160.0, 0.6, 0.25, true)
	Game.msg(L.t({"cs": "Ze zajíce vyletěla kachna!", "en": "A duck bursts out of the hare!"}), Color("e9d8a6"))


func _on_duck_died(a: Actor) -> void:
	level.drop_item(Item.create("vejce", 1), a.global_position)
	Fx.burst(level, a.global_position + Vector2(0, -20), Color("fff4d8"), 20, 120.0, 0.6, 0.25, true)
	Game.msg(L.t({"cs": "Kachna snesla vejce. V něm je Kostějova smrt.", "en": "The duck dropped an egg. Koschei's death is inside."}), Color("e9d8a6"))
	if aggro:
		say_t("Polož to vejce. Prosím. Nevíš, co držíš.", "Put the egg down. Please. You don't know what you're holding.", 4.0)


func _test_poke(p: Player, n: int) -> void:
	match n:
		5:
			if oak:
				on_quest_prop(oak, p)
		7:
			if chest:
				on_quest_prop(chest, p)
	if n > 8 and n % 3 == 0:
		for m in level.monsters.duplicate():
			if is_instance_valid(m) and m.get("rest_t") != null and not m.dead:
				m.take_damage(m.hp_max * 2.0, "physical", p)
		for g in level.ground_items.duplicate():
			if is_instance_valid(g) and g.item.base_id == "vejce":
				level._pickup(g)
	super._test_poke(p, n)
