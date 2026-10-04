class_name Forge
extends RefCounted

# The smith's forge (D2's cube): put things in, strike, and what lies there turns into something else.

const NEXT_TIER := {"": "_kovany", "_kovany": "_hlubinny", "_hlubinny": "_navsky"}
const TIER_KEY := {"_kovany": ["glag_r", 2], "_hlubinny": ["glag_u", 3], "_navsky": ["glag_ch", 4]}

const RECIPES := [
	{"cs": "3 stejné drahokamy → drahokam o stupeň lepší", "en": "3 matching gems → one gem a grade better"},
	{"cs": "3 stejná písmena → další písmeno (od Ljudije výš 2 písmena + broušený drahokam)", "en": "3 matching letters → the next letter (from Ljudije up: 2 letters + a cut gem)"},
	{"cs": "obyčejný předmět + 3 úlomky drahokamů → zásuvky", "en": "plain item + 3 chipped gems → sockets"},
	{"cs": "předmět se zásuvkami + kapradí květ → vrátí, co v něm je", "en": "socketed item + fern flower → gives back what is in it"},
	{"cs": "kouzelný předmět + 3 broušené drahokamy → nové kouzlo", "en": "magic item + 3 cut gems → new enchantment"},
	{"cs": "vzácný předmět + 4 dokonalé drahokamy → nové vlastnosti", "en": "rare item + 4 perfect gems → new properties"},
	{"cs": "předmět + Rьci a drahokam (2.) / Ukъ (3.) / Chěrъ (4.) → kovaný / hlubinný / navský", "en": "item + Rьci and a gem (grade 2) / Ukъ (3) / Chěrъ (4) → forged / deep / Nav-forged"},
	{"cs": "3 malé lektvary → 1 velký; 2 velké živé vody + velká rosa → kapradí květ", "en": "3 small potions → 1 large; 2 large living waters + large dew → fern flower"},
	{"cs": "pečeť vody, kamene, ohně a smrti → Permoníkův desátek", "en": "seals of water, stone, fire and death → Permoník's Tithe"},
]


static func _grade(it: Item) -> int:
	return int(it.base_id.get_slice("_", it.base_id.get_slice_count("_") - 1)) if it.slot() == "gem" else 0


static func _letters_sorted() -> Array:
	var ids := []
	for id in DB.items:
		if str(DB.items[id].get("slot", "")) == "letter":
			ids.append(id)
	ids.sort_custom(func(a, b): return int(DB.items[a].qlvl) < int(DB.items[b].qlvl))
	return ids


static func _tier_suffix(id: String) -> String:
	for s in ["_navsky", "_hlubinny", "_kovany"]:
		if id.ends_with(s):
			return s
	return ""


# Returns a message; on success the box holds the result instead of the ingredients.
static func craft(box: Inventory, ilvl: int) -> String:
	var its: Array = box.items.duplicate()
	if its.is_empty():
		return ""
	var gems := its.filter(func(i): return i.slot() == "gem")
	var letters := its.filter(func(i): return i.slot() == "letter")
	var gear := its.filter(func(i): return i.is_equipment())
	var other := its.filter(func(i): return not i.is_equipment() and i.slot() != "gem" and i.slot() != "letter")
	var out: Array = []
	# gems up a grade
	if its.size() == 3 and gems.size() == 3 and gems.all(func(g): return g.base_id == gems[0].base_id) and _grade(gems[0]) < 4:
		out = [Item.create("%s_%d" % [gems[0].kind(), _grade(gems[0]) + 1], ilvl)]
	# letters up the ladder
	elif letters.size() >= 2 and gear.is_empty() and other.is_empty():
		var lad := _letters_sorted()
		var rank := lad.find(letters[0].base_id)
		var same := letters.all(func(l): return l.base_id == letters[0].base_id)
		if same and rank >= 0 and rank + 1 < lad.size():
			if rank < 10 and letters.size() == 3 and gems.is_empty():
				out = [Item.create(lad[rank + 1], ilvl)]
			elif rank >= 10 and letters.size() == 2 and gems.size() == 1 and _grade(gems[0]) >= 3:
				out = [Item.create(lad[rank + 1], ilvl)]
	elif gear.size() == 1:
		var it: Item = gear[0]
		var rest := its.filter(func(i): return i != it)
		# sockets into a plain item
		if rest.size() == 3 and rest.all(func(g): return g.slot() == "gem" and _grade(g) == 1) and it.rarity == Item.NORMAL and it.sockets == 0 and it.max_sockets() > 0:
			it.sockets = randi_range(1, it.max_sockets())
			out = [it]
		# take the stones out again
		elif rest.size() == 1 and rest[0].base_id == "kapradi_kvet" and not it.socketed.is_empty():
			out = [it] + it.socketed
			it.socketed = []
			it.word = ""
		# a new enchantment
		elif rest.size() == 3 and it.rarity == Item.MAGIC and rest.all(func(g): return g.slot() == "gem" and _grade(g) >= 3):
			var fresh := Item.create(it.base_id, maxi(it.ilvl, ilvl))
			Loot.make_magic(fresh)
			fresh.identified = true
			out = [fresh]
		elif rest.size() == 4 and it.rarity == Item.RARE and rest.all(func(g): return g.slot() == "gem" and _grade(g) == 4):
			var fresh := Item.create(it.base_id, maxi(it.ilvl, ilvl))
			Loot.make_rare(fresh)
			fresh.identified = true
			out = [fresh]
		# up a tier, keeping everything it carries
		elif rest.size() == 2:
			var cur := _tier_suffix(it.base_id)
			var nxt: String = NEXT_TIER.get(cur, "")
			var stem := it.base_id.trim_suffix(cur) if cur != "" else it.base_id
			if nxt != "" and DB.items.has(stem + nxt):
				var key: Array = TIER_KEY[nxt]
				var has_letter := rest.any(func(l): return l.base_id == key[0])
				var has_gem := rest.any(func(g): return g.slot() == "gem" and _grade(g) >= int(key[1]))
				if has_letter and has_gem:
					var up := Item.create(stem + nxt, maxi(it.ilvl, ilvl))
					it.base_id = up.base_id
					it.dmg = up.dmg
					it.armor = up.armor
					it.max_dur = up.max_dur
					it.dur = up.max_dur
					out = [it]
	# potions, and the four seals
	elif gear.is_empty() and gems.is_empty() and letters.is_empty():
		var ids := other.map(func(i): return i.base_id)
		ids.sort()
		if ids == ["pecet_kamene", "pecet_ohne", "pecet_smrti", "pecet_vody"]:
			var t := Loot.unique_item("permonikuv_desatek", 99)
			if t:
				out = [t]
		if not out.is_empty():
			pass
		elif ids == ["ziva_voda", "ziva_voda", "ziva_voda"]:
			out = [Item.create("ziva_voda_velka", ilvl)]
		elif ids == ["svatojanska_rosa", "svatojanska_rosa", "svatojanska_rosa"]:
			out = [Item.create("svatojanska_rosa_velka", ilvl)]
		elif ids == ["svatojanska_rosa_velka", "ziva_voda_velka", "ziva_voda_velka"]:
			out = [Item.create("kapradi_kvet", ilvl)]
	if out.is_empty():
		return L.t({"cs": "Z toho nic neukuješ.", "en": "Nothing comes of that."})
	box.items.clear()
	for o in out:
		o.pos = Vector2i(-1, -1)
		box.add(o)
	return L.t({"cs": "Výheň zasyčela.", "en": "The forge hisses."})
