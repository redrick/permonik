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
		if SLOT_GROUPS.has(g) and s in SLOT_GROUPS[g]:
			return true
	return false


static func random_base(ilvl: int, filter := "") -> String:
	var pool := []
	var weights := []
	for id in DB.items:
		var b: Dictionary = DB.items[id]
		var sl := str(b.get("slot", ""))
		if sl in ["gold", "quest"] or bool(b.get("no_drop", false)):
			continue
		if filter == "equipment" and sl == "consumable":
			continue
		if filter != "" and filter != "equipment" and sl != filter:
			continue
		var q := int(b.get("qlvl", 1))
		if q > ilvl:
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


static func roll_affix(group: String, it: Item) -> Dictionary:
	var cands := []
	var ws := []
	for a in DB.affixes.get(group, []):
		if int(a.get("qlvl", 1)) > it.ilvl:
			continue
		if not _slot_ok(it, a.get("slots", ["any"])):
			continue
		cands.append(a)
		ws.append(float(a.get("weight", 10)))
	if cands.is_empty():
		return {}
	return cands[_weighted(ws)]


static func _apply_mods(it: Item, mods: Array) -> void:
	for m in mods:
		var v := float(m.get("value", 0))
		if m.has("min"):
			v = randf_range(float(m.min), float(m.get("max", m.min)))
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


static func roll_item(ilvl: int, mf := 0.0, magic_bonus := 0.0, filter := "") -> Item:
	var id := random_base(ilvl, filter)
	if id == "":
		return null
	var it := Item.create(id, ilvl)
	if not it.is_equipment():
		return it
	var r := randf()
	var uchance := 0.012 * (1.0 + mf / 100.0) * (1.0 + magic_bonus * 4.0)
	var mchance := 0.18 * (1.0 + mf / 200.0) + magic_bonus
	if r < uchance and make_unique(it):
		return it
	if r < uchance + mchance or (it.slot() in ["ring", "amulet"]):
		make_magic(it)
	return it


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
			var it := roll_item(mlvl, mf, magic_bonus, "equipment")
			if it:
				out.append(it)
		elif r < 0.32:
			out.append(gold(mlvl, gf))
		elif r < 0.42:
			var p := potion_for(mlvl)
			if p:
				out.append(p)
	if kind == "boss":
		out.append(gold(mlvl * 3, gf))
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


static func vendor_stock(role: String, level: int) -> Array:
	var out := []
	match role:
		"smith":
			for i in 14:
				var it := roll_item(level + 2, 0, 0.0, "equipment")
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
