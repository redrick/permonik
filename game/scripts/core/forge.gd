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
	{"cs": "kouzelný předmět + písmeno (šperk Dobro, zbroj Našь, zbraň Slovo) + broušený drahokam → kovaný předmět; kámen určí recept", "en": "magic item + a letter (jewellery Dobro, armour Našь, weapon Slovo) + a cut gem → a crafted item; the stone picks the recipe"},
	{"cs": "předmět + Rьci a drahokam (2.) / Ukъ (3.) / Chěrъ (4.) → kovaný / hlubinný / navský", "en": "item + Rьci and a gem (grade 2) / Ukъ (3) / Chěrъ (4) → forged / deep / Nav-forged"},
	{"cs": "3 malé lektvary → 1 velký; 2 velké živé vody + velká rosa → kapradí květ", "en": "3 small potions → 1 large; 2 large living waters + large dew → fern flower"},
	{"cs": "pečeť vody, kamene, ohně a smrti → Permoníkův desátek (pečeti leží v desátcích za Smorodinou; klíče k nim nechávají strážci pečetí od Noční můry výš)", "en": "seals of water, stone, fire and death → Permoník's Tithe (the seals lie in the tithes beyond the Smorodina; their keys are left by the seal guardians from Noční můra up)"},
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


# D2's crafting: the cut gem's stone picks the recipe, the letter must match what kind of thing it is.
const CRAFTS := {
	"granat": {"name": {"cs": "Moranina krev", "en": "Morana's Blood"},
		"mods": [{"stat": "life_steal", "min": 1, "max": 3}, {"stat": "hp", "min": 10, "max": 30}]},
	"achat": {"name": {"cs": "Perunův hrom", "en": "Perun's Thunder"},
		"mods": [{"stat": "crushing_blow", "min": 4, "max": 8}, {"stat": "thorns", "min": 5, "max": 15}]},
	"ametyst": {"name": {"cs": "Velesova moudrost", "en": "Veles's Wisdom"},
		"mods": [{"stat": "mana", "min": 15, "max": 30}, {"stat": "mana_regen", "min": 5, "max": 12}]},
	"vltavin": {"name": {"cs": "Mokošina ochrana", "en": "Mokosh's Shelter"},
		"mods": [{"stat": "dmg_reduce", "min": 2, "max": 5}, {"stat": "res_all", "min": 4, "max": 8}]},
	"jaspis": {"name": {"cs": "Svarogova výheň", "en": "Svarog's Forge"},
		"mods": [{"stat": "dmg_pct", "min": 10, "max": 20}, {"stat": "armor_pct", "min": 10, "max": 20}]},
	"kristal": {"name": {"cs": "Havířské štěstí", "en": "Miner's Luck"},
		"mods": [{"stat": "magic_find", "min": 6, "max": 12}, {"stat": "gold_find", "min": 15, "max": 30}]},
}
const CRAFT_LETTER := {"weapon": "glag_s", "armor": "glag_n", "jewelry": "glag_d"}


static func craft_letter(it: Item) -> String:
	if it.slot() == "weapon":
		return CRAFT_LETTER.weapon
	if it.slot() in ["ring", "amulet", "lamp", "belt"]:
		return CRAFT_LETTER.jewelry
	return CRAFT_LETTER.armor


# ---------------------------------------------------------------- the smiths' favours (D2's quest rewards)
# Each is earned once per difficulty by a quest ("service" in its reward) and spent at any smith.
const SERVICES := {
	"imbue": {"name": {"cs": "Zušlechtit", "en": "Imbue"},
		"hint": {"cs": "Polož sem obyčejný (bílý) předmět bez zásuvek. Kovář z něj ukove vzácný.", "en": "Lay a plain (white) item without sockets here. The smith forges it into a rare one."}},
	"socket": {"name": {"cs": "Vyvrtat zásuvky", "en": "Add sockets"},
		"hint": {"cs": "Polož sem předmět bez zásuvek. Obyčejný dostane nejvíc, kouzelný dvě, ostatní jednu.", "en": "Lay an item without sockets here. A plain one gets the most, a magic one two, any other one."}},
	"personalize": {"name": {"cs": "Vyrýt jméno", "en": "Engrave your name"},
		"hint": {"cs": "Polož sem kouzelný nebo lepší předmět. Mistr na něj vyryje tvé jméno.", "en": "Lay a magic or better item here. The foreman engraves your name on it."}},
}


static func service_flag(kind: String) -> String:
	return "svc_" + kind


# "" when the service can be done on it, otherwise why not.
static func service_check(kind: String, it: Item) -> String:
	if it == null:
		return L.t({"cs": "Nejdřív sem něco polož.", "en": "Lay something here first."})
	if not it.is_equipment():
		return L.t({"cs": "Tohle nejde.", "en": "That won't do."})
	match kind:
		"imbue":
			if it.rarity != Item.NORMAL or it.sockets > 0 or it.word != "":
				return L.t({"cs": "Jen obyčejný předmět bez zásuvek.", "en": "Only a plain item without sockets."})
		"socket":
			if it.sockets > 0 or it.max_sockets() <= 0:
				return L.t({"cs": "Do tohohle zásuvku nevyvrtám.", "en": "I can't socket that."})
		"personalize":
			if it.personal != "":
				return L.t({"cs": "Už na něm jméno je.", "en": "It already bears a name."})
			if it.rarity == Item.NORMAL and it.word == "":
				return L.t({"cs": "Jméno patří na kouzelnou nebo lepší věc.", "en": "A name belongs on a magic or better item."})
			if not it.identified:
				return L.t({"cs": "Nejdřív ho nech zjevit.", "en": "Have it identified first."})
	return ""


# Returns the item that leaves the forge (imbue makes a new one).
static func service_do(kind: String, it: Item, ch: CharData) -> Item:
	match kind:
		"imbue":
			var best: Item = null
			for i in 3:
				var c := Item.from_dict(it.to_dict())
				c.ilvl = maxi(it.ilvl, ch.level + 4)
				Loot.make_rare(c)
				if best == null or c.mods.size() > best.mods.size():
					best = c
			best.identified = true
			return best
		"socket":
			it.sockets = it.max_sockets() if it.rarity == Item.NORMAL else (mini(2, it.max_sockets()) if it.rarity == Item.MAGIC else 1)
		"personalize":
			it.personal = ch.hero_name
			it.personal_g = str(ch.cls().get("gender", "m"))
	return it


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
		# a crafted item
		elif rest.size() == 2 and it.rarity == Item.MAGIC and gems.size() == 1 and letters.size() == 1 \
				and _grade(gems[0]) >= 3 and letters[0].base_id == craft_letter(it) and CRAFTS.has(gems[0].kind()):
			var fresh := Item.create(it.base_id, ilvl / 2 + it.ilvl / 2)
			fresh.sockets = 0
			Loot.make_crafted(fresh, gems[0].kind())
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
					if it.eth:
						up.make_ethereal()
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
