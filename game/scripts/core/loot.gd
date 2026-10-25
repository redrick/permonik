class_name Loot
extends RefCounted

const SLOT_GROUPS := {
	"armor": ["head", "body", "offhand", "belt"],
	"jewelry": ["ring", "amulet"],
}


static func _slot_ok(it: Item, slots: Array) -> bool:
	if slots.is_empty() or "any" in slots:
		return true
	var s := it.slot()
	for g in slots:
		if g == s:
			return true
		if g == "ranged" and it.is_ranged():
			return true
		if g == "shield" and s == "offhand" and it.kind() == "shield":
			return true
		if g == "weapon" and s == "weapon":
			return true
		if g == "class" and str(it.base().get("class", "")) != "":
			return true
		if SLOT_GROUPS.has(g) and s in SLOT_GROUPS[g]:
			return true
	return false


# Smart drops only draw bases the hero can wield soon: their class's weapon and offhand kinds,
# no other class's items, nothing far above their level.
static func usable(b: Dictionary) -> bool:
	var ch := Game.ch
	var only := str(b.get("class", ""))
	if only != "" and only != ch.class_id:
		return false
	if int(b.get("req", {}).get("level", 1)) > ch.level + 3:
		return false
	var pref: Dictionary = DB.classes.get(ch.class_id, {}).get("loot", {})
	match str(b.get("slot", "")):
		"weapon":
			return str(b.get("kind", "")) in pref.get("weapons", [])
		"offhand":
			return str(b.get("kind", "")) in pref.get("offhand", [])
	return true


static func random_base(ilvl: int, filter := "", smart := false) -> String:
	var pool := []
	var weights := []
	for id in DB.items:
		var b: Dictionary = DB.items[id]
		var sl := str(b.get("slot", ""))
		if sl in ["gold", "quest"] or bool(b.get("no_drop", false)) or bool(b.get("quest", false)):
			continue
		if filter == "equipment" and sl == "consumable":
			continue
		if sl in ["gem", "letter"] and filter != sl:
			continue
		if sl == "charm" and filter not in ["charm", "equipment"]:
			continue
		if filter != "" and filter != "equipment" and sl != filter:
			continue
		var q := int(b.get("qlvl", 1))
		if q > ilvl:
			continue
		if smart and not usable(b):
			continue
		pool.append(id)
		weights.append(1.0 + q * 0.15 if sl != "consumable" else 6.0)
	if pool.is_empty():
		return ""
	return pool[_weighted(weights)]


static func _weighted(w: Array) -> int:
	var total := 0.0
	for x in w:
		total += x
	var r := randf() * total
	for i in w.size():
		r -= w[i]
		if r <= 0:
			return i
	return w.size() - 1


# What a charm may carry, and how much of an affix's value each size keeps.
const CHARM_STATS := ["hp", "mana", "to_hit", "dmg_max", "dmg_min", "res_fire", "res_cold", "res_lightning", "res_poison",
	"res_all", "magic_find", "gold_find", "fire_dmg", "cold_dmg", "lightning_dmg", "poison_dmg", "armor", "hit_recovery",
	"move_speed", "light_radius", "sila", "obratnost", "magie", "vitalita"]
const CHARM_SCALE := {"hromovy_kamen_maly": 0.35, "hromovy_kamen": 0.6, "hromovy_kamen_velky": 1.0}


static func _charm_ok(it: Item, a: Dictionary) -> bool:
	for m in a.get("mods", []):
		var st := str(m.get("stat", ""))
		if st.begins_with("tree_"):
			return it.base_id == "hromovy_kamen_velky"
		if not st in CHARM_STATS:
			return false
	return true


static func roll_affix(group: String, it: Item) -> Dictionary:
	var cands := []
	var ws := []
	var charm := it.slot() == "charm"
	for a in DB.affixes.get(group, []):
		if int(a.get("qlvl", 1)) > it.ilvl:
			continue
		if charm:
			if not _charm_ok(it, a):
				continue
		elif not _slot_ok(it, a.get("slots", ["any"])):
			continue
		var w := float(a.get("weight", 10))
		var owner := _skill_owner(a)
		if not DB.classes.has(owner) and owner != "":
			continue
		var cls := str(it.base().get("class", ""))
		if owner != "" and cls != "":
			if owner != cls:
				continue
			w *= 4.0
		elif owner != "":
			w *= 0.35
		cands.append(a)
		ws.append(w)
	if cands.is_empty():
		return {}
	return cands[_weighted(ws)]


# The class a +skill affix belongs to ("" for any other affix).
static func _skill_owner(a: Dictionary) -> String:
	for m in a.get("mods", []):
		var cid := DB.stat_class(str(m.get("stat", "")))
		if cid != "":
			return cid
	return ""


static func _apply_mods(it: Item, mods: Array) -> void:
	var k := float(CHARM_SCALE.get(it.base_id, 1.0))
	for m in mods:
		var v := float(m.get("value", 0))
		if m.has("min"):
			v = randf_range(float(m.min), float(m.get("max", m.min)))
		if k < 1.0 and not str(m.stat).begins_with("tree_"):
			v = maxf(1.0, v * k) if v > 0 else v * k
		it.mods.append({"stat": m.stat, "value": round(v)})


static func make_magic(it: Item) -> void:
	it.rarity = Item.MAGIC
	it.identified = false
	var both := randf() < 0.4
	var use_prefix := both or randf() < 0.5
	var use_suffix := both or not use_prefix
	if use_prefix:
		var a := roll_affix("prefixes", it)
		if not a.is_empty():
			it.prefix = a.id
			_apply_mods(it, a.get("mods", []))
	if use_suffix:
		var a := roll_affix("suffixes", it)
		if not a.is_empty():
			it.suffix = a.id
			_apply_mods(it, a.get("mods", []))
	if it.mods.is_empty():
		it.rarity = Item.NORMAL
		it.identified = true


# D2 rare: up to three prefixes and three suffixes, never two of one family (perunuv_1 / perunuv_2),
# and a two-word name of its own.
static func make_rare(it: Item) -> void:
	it.rarity = Item.RARE
	it.identified = false
	it.prefix = ""
	it.suffix = ""
	it.mods = []
	it.affix_ids = []
	_add_rare_affixes(it, randi_range(3, 6) if it.ilvl >= 20 else randi_range(3, 4))
	if it.mods.is_empty():
		it.rarity = Item.NORMAL
		it.identified = true
		return
	it.rare_name = [randi() % maxi(1, DB.rare_names.get("first", []).size()), randi() % maxi(1, DB.rare_names.get("second", []).size())]


# D2 crafted: the recipe's own properties, then one to four rare affixes, under a rare's name.
static func make_crafted(it: Item, fam: String) -> void:
	it.rarity = Item.CRAFTED
	it.prefix = ""
	it.suffix = ""
	it.mods = []
	it.affix_ids = []
	it.craft = fam
	_apply_mods(it, Forge.CRAFTS.get(fam, {}).get("mods", []))
	_add_rare_affixes(it, randi_range(1, 4))
	it.rare_name = [randi() % maxi(1, DB.rare_names.get("first", []).size()), randi() % maxi(1, DB.rare_names.get("second", []).size())]
	it.identified = true


# Adds up to n more affixes, at most three of each kind, none of a family or stat the item already has.
static func _add_rare_affixes(it: Item, n: int) -> void:
	var total := it.affix_ids.size() + n
	var counts := {"prefixes": 0, "suffixes": 0}
	var families := {}
	for m in it.mods:
		families["stat:" + str(m.stat)] = true
	for id in it.affix_ids:
		families[str(id).rsplit("_", true, 1)[0]] = true
		counts["prefixes" if not Item._affix("prefixes", id).is_empty() else "suffixes"] += 1
	var tries := 0
	while it.affix_ids.size() < total and tries < 40:
		tries += 1
		var group := "prefixes" if randf() < 0.5 else "suffixes"
		if counts[group] >= 3:
			group = "suffixes" if group == "prefixes" else "prefixes"
		if counts[group] >= 3:
			break
		var a := roll_affix(group, it)
		if a.is_empty():
			continue
		var fam := str(a.id).rsplit("_", true, 1)[0]
		var clash := families.has(fam)
		for m in a.get("mods", []):
			if families.has("stat:" + str(m.stat)):
				clash = true
		if clash:
			continue
		families[fam] = true
		for m in a.get("mods", []):
			families["stat:" + str(m.stat)] = true
		counts[group] += 1
		it.affix_ids.append(a.id)
		_apply_mods(it, a.get("mods", []))


# D3's mystic: one affix rolled anew in its own place; the rest stay, and from then on only that one may change.
static func reroll_affix(it: Item, idx: int) -> bool:
	var slots := it.affix_slots()
	if idx < 0 or idx >= slots.size() or (it.locked >= 0 and it.locked != idx):
		return false
	var sl: Dictionary = slots[idx]
	var taken := {}
	for i in it.mods.size():
		if i < sl.start or i >= sl.start + sl.count:
			taken["stat:" + str(it.mods[i].stat)] = true
	for o in slots:
		if o != sl:
			taken[str(o.id).rsplit("_", true, 1)[0]] = true
	var a := {}
	for tries in 40:
		var c := roll_affix(sl.group, it)
		if c.is_empty() or c.id == sl.id or taken.has(str(c.id).rsplit("_", true, 1)[0]):
			continue
		if c.get("mods", []).any(func(m): return taken.has("stat:" + str(m.stat))):
			continue
		a = c
		break
	if a.is_empty():
		return false
	var head := it.mods.slice(0, sl.start)
	var tail := it.mods.slice(sl.start + sl.count)
	it.mods = head
	_apply_mods(it, a.get("mods", []))
	it.mods.append_array(tail)
	if it.rarity == Item.MAGIC:
		if sl.group == "prefixes":
			it.prefix = a.id
		else:
			it.suffix = a.id
	else:
		it.affix_ids[it.affix_ids.find(sl.id)] = a.id
	it.locked = idx
	it.rerolls += 1
	return true


static func reroll_cost(it: Item) -> int:
	return int((200 + it.ilvl * 40) * pow(1.4, it.rerolls) * (1.0 + 0.5 * Game.difficulty))


static func make_set(it: Item) -> bool:
	var cands := []
	for iid in DB.set_items:
		var si: Dictionary = DB.set_items[iid]
		if si.get("base", "") == it.base_id and int(si.get("qlvl", 1)) <= it.ilvl + 3 \
				and DB.class_released(str(DB.sets.get(str(si.get("set", "")), {}).get("class", ""))):
			cands.append(iid)
	if cands.is_empty():
		return false
	make_set_id(it, cands.pick_random())
	it.identified = false
	return true


static func make_set_id(it: Item, iid: String) -> void:
	var si: Dictionary = DB.set_items.get(iid, {})
	it.rarity = Item.SET
	it.set_id = iid
	it.mods = []
	_apply_mods(it, si.get("mods", []))
	it.identified = true


static func set_item(iid: String, ilvl: int) -> Item:
	var si: Dictionary = DB.set_items.get(iid, {})
	if si.is_empty():
		return null
	var it := Item.create(si.get("base", ""), ilvl)
	make_set_id(it, iid)
	return it


static func make_unique(it: Item) -> bool:
	var cands := []
	for uid in DB.uniques:
		var u: Dictionary = DB.uniques[uid]
		if u.get("base", "") == it.base_id and int(u.get("qlvl", 1)) <= it.ilvl + 3 and not bool(u.get("quest_only", false)):
			cands.append(uid)
	if cands.is_empty():
		return false
	make_unique_id(it, cands.pick_random())
	it.identified = false
	return true


static func make_unique_id(it: Item, uid: String) -> void:
	var u: Dictionary = DB.uniques.get(uid, {})
	it.rarity = Item.UNIQUE
	it.unique_id = uid
	it.mods = []
	_apply_mods(it, u.get("mods", []))
	it.identified = true


static func unique_item(uid: String, ilvl: int) -> Item:
	var u: Dictionary = DB.uniques.get(uid, {})
	if u.is_empty():
		return null
	var it := Item.create(u.get("base", ""), ilvl)
	if it.base().is_empty():
		return null
	make_unique_id(it, uid)
	return it


const ETH_CHANCE := [0.03, 0.05, 0.08]


static func roll_item(ilvl: int, mf := 0.0, magic_bonus := 0.0, filter := "", smart := false) -> Item:
	var id := random_base(ilvl, filter, smart)
	if id == "" and smart:
		id = random_base(ilvl, filter)
	if id == "":
		return null
	var it := Item.create(id, ilvl)
	if it.slot() == "charm":
		make_magic(it)
		return it
	if not it.is_equipment():
		return it
	if it.slot() in ["weapon", "offhand", "head", "body"] and it.max_dur > 0 and randf() < ETH_CHANCE[clampi(Game.difficulty, 0, 2)]:
		it.make_ethereal()
	var r := randf()
	var uchance := 0.012 * (1.0 + mf / 100.0) * (1.0 + magic_bonus * 4.0)
	var rchance := (0.05 if ilvl >= 6 else 0.0) * (1.0 + mf / 150.0) * (1.0 + magic_bonus * 2.0)
	var mchance := 0.18 * (1.0 + mf / 200.0) + magic_bonus
	var schance := 0.02 * (1.0 + mf / 100.0) * (1.0 + magic_bonus * 3.0)
	if r < uchance and make_unique(it):
		return it
	if r >= uchance and r < uchance + schance and make_set(it):
		return it
	r -= schance
	if r < uchance + rchance:
		make_rare(it)
		return it
	if r < uchance + rchance + mchance or (it.slot() in ["ring", "amulet"]):
		make_magic(it)
	elif it.max_sockets() > 0 and randf() < 0.15:
		it.sockets = randi_range(1, it.max_sockets())
	return it


# A gem of a random stone, its grade climbing with the monster's level.
static func gem(mlvl: int) -> Item:
	var top := 1 if mlvl < 12 else (2 if mlvl < 30 else (3 if mlvl < 55 else 4))
	var g := randi_range(maxi(1, top - 1), top)
	var stones := ["granat", "vltavin", "ametyst", "achat", "kristal", "jaspis"]
	return Item.create("%s_%d" % [stones.pick_random(), g], mlvl)


# Letters follow D2's rune ladder: each step up is a quarter rarer, and none above the monster's level.
static func letter(mlvl: int) -> Item:
	var ids := []
	var ws := []
	var rank := 0
	for id in DB.items:
		if str(DB.items[id].get("slot", "")) == "letter" and int(DB.items[id].get("qlvl", 1)) <= mlvl + 2:
			ids.append(id)
	ids.sort_custom(func(a, b): return int(DB.items[a].qlvl) < int(DB.items[b].qlvl))
	for id in ids:
		ws.append(pow(0.75, rank))
		rank += 1
	if ids.is_empty():
		return null
	return Item.create(ids[_weighted(ws)], mlvl)


static func gold(ilvl: int, gf := 0.0) -> Item:
	var it := Item.create("grose_malo", ilvl)
	if it.base().is_empty():
		it.base_id = "grose_malo"
	it.qty = int(randi_range(ilvl * 2 + 3, ilvl * 6 + 12) * (1.0 + gf / 100.0))
	if it.qty > 400:
		it.base_id = "grose_hodne" if DB.items.has("grose_hodne") else it.base_id
	elif it.qty > 60:
		it.base_id = "grose_hromadka" if DB.items.has("grose_hromadka") else it.base_id
	return it


const SMART_SHARE := {"normal": 0.35, "champion": 0.5, "boss": 0.6}


static func monster_drops(mlvl: int, kind: String, mf: float, gf: float) -> Array:
	var out := []
	var rolls := 1
	var magic_bonus := 0.0
	match kind:
		"champion":
			rolls = 2
			magic_bonus = 0.25
		"boss":
			rolls = 5
			magic_bonus = 0.6
	for i in rolls:
		var r := randf()
		if kind == "boss" or r < 0.14:
			var it := roll_item(mlvl, mf, magic_bonus, "equipment", randf() < SMART_SHARE.get(kind, 0.35))
			if it:
				out.append(it)
		elif r < 0.32:
			out.append(gold(mlvl, gf))
		elif r < 0.42:
			var p := potion_for(mlvl)
			if p:
				out.append(p)
		elif r < 0.46:
			out.append(gem(mlvl))
		elif r < 0.475:
			var l := letter(mlvl)
			if l:
				out.append(l)
	if kind == "boss":
		out.append(gold(mlvl * 3, gf))
		if randf() < 0.5:
			out.append(gem(mlvl))
		if randf() < 0.35:
			var bl := letter(mlvl)
			if bl:
				out.append(bl)
	return out


static func potion_for(mlvl: int) -> Item:
	var big := mlvl > 14
	var choices := ["ziva_voda_velka" if big else "ziva_voda", "svatojanska_rosa_velka" if big else "svatojanska_rosa", "ziva_voda_velka" if big else "ziva_voda"]
	if randf() < 0.05:
		choices = ["kapradi_kvet"]
	elif randf() < 0.12:
		choices = ["svitek_brana", "svitek_zjeveni"]
	var id: String = choices.pick_random()
	if not DB.items.has(id):
		return null
	return Item.create(id, mlvl)


# D1's Wirt, here the little man of Třemšín: one strong thing from the mountain, for those who pay to look.
static func peddler_item(level: int) -> Item:
	for i in 40:
		var it := roll_item(level + 5, 300, 1.0, "equipment", true)
		if it and it.is_equipment() and it.rarity in [Item.RARE, Item.UNIQUE, Item.SET]:
			it.identified = true
			return it
	var id := random_base(level + 5, "equipment", true)
	var f := Item.create(id if id != "" else "krumpac", level + 5)
	make_rare(f)
	f.identified = true
	return f


static func peddler_fee(level: int) -> int:
	return 50 * (1 + Game.difficulty) + level * 5


# The innkeeper's dice: plain-looking things you pay for blind; the roll happens when you buy.
static func gamble_stock(level: int) -> Array:
	var out := []
	for sl in ["weapon", "weapon", "weapon", "body", "head", "offhand", "belt", "ring", "ring", "amulet", "amulet", "lamp", "charm"]:
		var id := random_base(level + 5, sl)
		if id != "":
			var it := Item.create(id, level)
			out.append(it)
	return out


static func gamble_price(it: Item, level: int) -> int:
	return int((float(it.base().get("price", 50)) * 3.0 + 120.0) * (1.0 + level * 0.12))


static func gamble(base_id: String, level: int) -> Item:
	var it := Item.create(base_id, clampi(level + randi_range(-4, 5), 1, 99))
	var r := randf()
	if it.slot() == "charm":
		make_magic(it)
	elif r < 0.03 and make_unique(it):
		pass
	elif r < 0.07 and make_set(it):
		pass
	elif r < 0.25:
		make_rare(it)
	else:
		make_magic(it)
	it.identified = true
	return it


static func vendor_stock(role: String, level: int) -> Array:
	var out := []
	match role:
		"smith":
			for i in 14:
				var it := roll_item(level + 2, 0, 0.0, "equipment", i < 7)
				if it and it.slot() in ["weapon", "offhand", "head", "body", "belt"]:
					if randf() < 0.3:
						make_magic(it)
						it.identified = true
					out.append(it)
		"healer":
			for id in ["ziva_voda", "ziva_voda_velka", "svatojanska_rosa", "svatojanska_rosa_velka"]:
				if DB.items.has(id) and (level > 10 or not id.ends_with("velka")):
					for k in 3:
						out.append(Item.create(id, level))
		"inn":
			for id in ["svitek_brana", "svitek_brana", "svitek_zjeveni", "svitek_zjeveni"]:
				if DB.items.has(id):
					out.append(Item.create(id, level))
			for i in 6:
				var it := roll_item(level + 3, 0, 0.0, "equipment")
				if it and it.slot() in ["ring", "amulet", "lamp", "belt"]:
					it.identified = true
					out.append(it)
	return out
