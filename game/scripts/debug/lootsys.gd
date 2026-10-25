extends Node

# Checks the loot systems headless: upgrade arrow, services, crafting, ethereal, collection, peddler,
# re-enchanting, roll ranges, loot filter. Prints LOOTSYS PASS/FAIL per check.

var fails := 0


func _ok(name: String, cond: bool, info = "") -> void:
	print("LOOTSYS %s %s %s" % ["PASS" if cond else "FAIL", name, str(info)])
	if not cond:
		fails += 1


func _ready() -> void:
	await get_tree().create_timer(1.5).timeout
	var ch := Game.ch
	_upgrade(ch)
	_services(ch)
	_crafting(ch)
	_ethereal(ch)
	await _collection(ch)
	_peddler(ch)
	_reroll(ch)
	_ranges(ch)
	await _filter(ch)
	print("LOOTSYS DONE fails=%d" % fails)
	get_tree().quit()


func _upgrade(ch: CharData) -> void:
	var worn: Item = ch.weapon()
	var better := Item.create(worn.base_id, 5)
	better.rarity = Item.MAGIC
	better.mods = [{"stat": "dmg_pct", "value": 80}, {"stat": "hp", "value": 40}]
	var worse := Item.create(worn.base_id, 5)
	worse.rarity = Item.MAGIC
	worse.mods = [{"stat": "dmg_pct", "value": -60}]
	worse.identified = true
	var hp0 := ch.hp
	var d0 := ch.d.duplicate()
	_ok("upgrade_better", ch.upgrade_score(better) > 1.5, ch.upgrade_score(better))
	_ok("upgrade_worse", ch.upgrade_score(worse) < -1.5, ch.upgrade_score(worse))
	_ok("upgrade_worn_nan", is_nan(ch.upgrade_score(worn)))
	_ok("preview_restores", ch.weapon() == worn and ch.hp == hp0 and ch.d == d0)
	_ok("delta_lines", ch.delta_lines(better).size() >= 2, ch.delta_lines(better))
	var hidden := Item.create(worn.base_id, 5)
	hidden.rarity = Item.MAGIC
	hidden.identified = false
	_ok("upgrade_unidentified_nan", is_nan(ch.upgrade_score(hidden)))


func _services(ch: CharData) -> void:
	var plain := Item.create("krumpac", 10)
	_ok("imbue_check_plain", Forge.service_check("imbue", plain) == "")
	var r := Forge.service_do("imbue", plain, ch)
	_ok("imbue_makes_rare", r.rarity == Item.RARE and r.identified and r.mods.size() >= 3, r.display_name())
	_ok("imbue_refuses_rare", Forge.service_check("imbue", r) != "")
	_ok("socket_rare_one", Forge.service_do("socket", r, ch).sockets == 1)
	var w := Item.create("krumpac", 10)
	_ok("socket_plain_max", Forge.service_do("socket", w, ch).sockets == w.max_sockets(), w.sockets)
	_ok("personalize_refuses_white", Forge.service_check("personalize", Item.create("krumpac", 10)) != "")
	ch.hero_name = "Ondra"
	Forge.service_do("personalize", r, ch)
	L.lang = "cs"
	_ok("personal_cs", r.display_name().begins_with("Ondr"), r.display_name())
	var back := Item.from_dict(r.to_dict())
	_ok("personal_saved", back.personal == "Ondra" and back.display_name() == r.display_name())
	var cases := [["Ondra", "m", "f", "Ondrova"], ["Andrej", "m", "m", "Andrejův"], ["Marek", "m", "n", "Markovo"],
		["Hanka", "f", "m", "Hančin"], ["Petra", "f", "f", "Petřina"], ["Lucie", "f", "n", "Luciino"], ["Jiří", "m", "m", ""],
		["Pavel", "m", "m", "Pavlův"], ["Olga", "f", "f", "Olžina"]]
	for c in cases:
		_ok("possessive_" + c[0], Item.possessive(c[0], c[1], c[2]) == c[3], Item.possessive(c[0], c[1], c[2]))
	L.lang = "en"
	_ok("personal_en", r.display_name().begins_with("Ondra's "), r.display_name())
	L.lang = "cs"
	Game.quest_done("srdce_zvonu")
	_ok("quest_grants_imbue", Game.flags.get("svc_imbue", false))


func _crafting(_ch: CharData) -> void:
	for stone in Forge.CRAFTS:
		var box := Inventory.new(4, 3)
		var it := Item.create("prsten", 30)
		Loot.make_magic(it)
		it.identified = true
		box.add(it)
		box.add(Item.create(Forge.craft_letter(it), 30))
		box.add(Item.create(stone + "_3", 30))
		Forge.craft(box, 40)
		var r: Item = box.items[0] if box.items.size() == 1 else null
		var fam_stats: Array = Forge.CRAFTS[stone].mods.map(func(m): return m.stat)
		var has_fam := r != null and fam_stats.all(func(s): return r.mods.any(func(m): return m.stat == s))
		_ok("craft_" + stone, r != null and r.rarity == Item.CRAFTED and r.craft == stone and has_fam and r.affix_ids.size() >= 1,
			"%s %s" % [r.display_name() if r else "-", r.mods if r else ""])
		if r:
			var back := Item.from_dict(r.to_dict())
			_ok("craft_saved_" + stone, back.craft == stone and back.rarity == Item.CRAFTED and back.req().get("level", 0) >= 5)
	var box := Inventory.new(4, 3)
	var w := Item.create("krumpac", 30)
	Loot.make_magic(w)
	box.add(w)
	box.add(Item.create("glag_d", 30))
	box.add(Item.create("granat_3", 30))
	Forge.craft(box, 40)
	_ok("craft_wrong_letter_refused", box.items.size() == 3)


func _ethereal(_ch: CharData) -> void:
	var a := Item.create("krumpac", 10)
	var e := Item.create("krumpac", 10)
	e.make_ethereal()
	_ok("eth_dmg", e.dmg.y == int(a.dmg.y * 1.5) and e.max_dur == a.max_dur / 2 + 1, "%s %s" % [e.dmg, e.max_dur])
	e.dur = 1
	_ok("eth_no_repair", e.repair_cost() == 0)
	_ok("eth_saved", Item.from_dict(e.to_dict()).eth)
	var n := 0
	for i in 3000:
		var it := Loot.roll_item(30, 0, 0.0, "equipment")
		if it and it.eth:
			n += 1
	_ok("eth_drops_some", n > 5 and n < 300, n)


func _collection(ch: CharData) -> void:
	var u := Loot.unique_item("klekanicina_rouska", 10)
	u.identified = false
	ch.pickup(u)
	_ok("grail_skips_unidentified", not Game.known.has("grail:u:klekanicina_rouska"))
	u.identified = true
	UiRoot.inst.changed()
	_ok("grail_unique", Game.known.has("grail:u:klekanicina_rouska"))
	ch.pickup(Loot.set_item("kazin_korenar_hul", 10))
	_ok("grail_set", Game.known.has("grail:s:kazin_korenar_hul"))
	var w := Item.create("krumpac", 30)
	w.sockets = 3
	for l in ["glag_l", "glag_e", "glag_d"]:
		w.socket(Item.create(l, 30))
	ch.pickup(w)
	_ok("grail_word", w.word == "led" and Game.known.has("grail:w:led"), w.word)
	UiRoot.inst.open_kronika()
	await get_tree().process_frame
	var k: UiKronika = UiRoot.inst.left
	k._open_tab("grail")
	await get_tree().process_frame
	_ok("grail_tab", k.list.get_child_count() == DB.sets.keys().filter(func(x): return DB.class_released(str(DB.sets[x].get("class", "")))).size() + 2 and k.count_lbl.text.contains("4 "), k.count_lbl.text)
	k._show("grail:s:kazin_korenar")
	await get_tree().process_frame
	_ok("grail_page", k.title_lbl.text.contains("1/"), k.title_lbl.text)
	UiRoot.inst.close_all()


func _peddler(ch: CharData) -> void:
	Game.flags.erase("peddler")
	var a := Game.peddler_item()
	_ok("peddler_quality", a != null and a.rarity in [Item.RARE, Item.UNIQUE, Item.SET] and a.identified, a.display_name() if a else "")
	_ok("peddler_stable", Game.peddler_item().to_dict() == a.to_dict())
	_ok("peddler_unseen", not Game.peddler_seen())
	ch.level += 1
	_ok("peddler_new_on_level", Game.peddler_item().to_dict() != a.to_dict())
	ch.level -= 1
	_ok("peddler_fee", Loot.peddler_fee(ch.level) >= 50)


func _reroll(_ch: CharData) -> void:
	var it := Item.create("krumpac", 40)
	Loot.make_rare(it)
	it.identified = true
	var slots := it.affix_slots()
	var total := 0
	for s in slots:
		total += s.count
	_ok("slots_cover_mods", total == it.mods.size(), "%d %d" % [total, it.mods.size()])
	var before: Array = it.mods.duplicate(true)
	var ok := Loot.reroll_affix(it, 0)
	var n0: int = slots[0].count
	_ok("reroll_changes_first", ok and it.mods.slice(0, it.affix_slots()[0].count) != before.slice(0, n0), "%s -> %s" % [before, it.mods])
	_ok("reroll_keeps_rest", it.mods.slice(it.affix_slots()[0].count) == before.slice(n0))
	_ok("reroll_locked", not Loot.reroll_affix(it, 1) and it.locked == 0 and it.rerolls == 1)
	var stats := {}
	var dup := false
	for m in it.mods:
		dup = dup or stats.has(m.stat)
		stats[m.stat] = true
	_ok("reroll_no_dup_stat", not dup)
	var back := Item.from_dict(it.to_dict())
	_ok("reroll_saved", back.locked == 0 and back.rerolls == 1)
	var mg := Item.create("prsten", 30)
	mg.rarity = Item.MAGIC
	mg.prefix = ""
	mg.suffix = ""
	mg.mods = []
	while mg.suffix == "":
		mg = Item.create("prsten", 30)
		Loot.make_magic(mg)
	mg.identified = true
	var old := mg.suffix
	var last := mg.affix_slots().size() - 1
	Loot.reroll_affix(mg, last)
	_ok("reroll_magic_suffix", mg.suffix != old and mg.suffix != "", "%s -> %s %s" % [old, mg.suffix, mg.display_name()])
	var cr := Item.create("prsten", 30)
	Loot.make_crafted(cr, "granat")
	Loot.reroll_affix(cr, 0)
	_ok("reroll_crafted_keeps_recipe", cr.mods[0].stat == "life_steal" and cr.mods[1].stat == "hp", cr.mods)
	_ok("reroll_cost_grows", Loot.reroll_cost(it) > 200)


func _ranges(_ch: CharData) -> void:
	var u := Loot.unique_item("klekanicina_rouska", 10)
	var r := u.mod_ranges()
	_ok("ranges_unique", r.size() == u.mods.size() and r[0] == Vector2(5, 8), r)
	var it := Item.create("krumpac", 40)
	Loot.make_rare(it)
	it.identified = true
	var rr := it.mod_ranges()
	var inside := rr.size() == it.mods.size()
	for i in rr.size():
		if rr[i] != null:
			inside = inside and it.mods[i].value >= rr[i].x and it.mods[i].value <= rr[i].y
	_ok("ranges_rare_contain_values", inside, "%s %s" % [rr, it.mods])
	var c := Item.create("hromovy_kamen_maly", 30)
	Loot.make_magic(c)
	var cr := c.mod_ranges()
	var cin := cr.size() == c.mods.size()
	for i in cr.size():
		if cr[i] != null:
			cin = cin and c.mods[i].value >= cr[i].x and c.mods[i].value <= cr[i].y
	_ok("ranges_charm_scaled", cin, "%s %s" % [cr, c.mods])
	Input.action_press("show_items")
	var lines := u.tooltip(null)
	Input.action_release("show_items")
	_ok("ranges_in_tooltip", lines.any(func(l): return str(l[0]).contains("[5–8]")))
	_ok("ranges_hint", u.tooltip(null).any(func(l): return str(l[0]).contains("Alt")))


func _filter(_ch: CharData) -> void:
	var keep := GroundItem.filter_level
	var white := Item.create("krumpac", 10)
	var blue := Item.create("krumpac", 10)
	Loot.make_magic(blue)
	var ring := Item.create("prsten", 10)
	Loot.make_magic(ring)
	var sock := Item.create("krumpac", 10)
	sock.sockets = 2
	GroundItem.filter_level = 0
	_ok("filter_off", not GroundItem.hides(white))
	GroundItem.filter_level = 1
	_ok("filter_1", GroundItem.hides(white) and not GroundItem.hides(blue) and not GroundItem.hides(sock) and not GroundItem.hides(Item.create("granat_1", 1)))
	GroundItem.filter_level = 2
	_ok("filter_2", GroundItem.hides(blue) and not GroundItem.hides(ring))
	var lv = Game.level
	var p: Vector2 = Game.player.global_position + Vector2(60, 0)
	lv.drop_item(white, p, true)
	await get_tree().process_frame
	await get_tree().process_frame
	var g = lv.ground_items.back()
	_ok("filter_hidden_on_ground", not g.visible and lv.pick_at(g.global_position) == null or lv.pick_at(g.global_position).get("node") != g)
	GroundItem.filter_level = keep
