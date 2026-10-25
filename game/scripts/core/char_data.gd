class_name CharData
extends RefCounted

signal changed
signal leveled(level: int)

const MAX_LEVEL := 100
const SLOTS := ["weapon", "offhand", "head", "body", "belt", "lamp", "ring1", "ring2", "amulet"]
const BASE_STATS := ["sila", "obratnost", "magie", "vitalita"]
const ELEMENTS := ["fire", "lightning", "cold", "poison"]

var class_id := "havir"
var hero_name := ""
var level := 1
var xp := 0
var alloc := {"sila": 0, "obratnost": 0, "magie": 0, "vitalita": 0}
var stat_points := 0
var skill_points := 0
var skills := {}
var hp := 1.0
var mana := 0.0
var gold := 0
var inv := Inventory.new(10, 4)
var stash := Inventory.new(12, 10)
var equip := {}
var belt: Array = []
var buffs: Array = []
var rmb := "utok"
var hotkeys := ["", "", "", ""]
# The hireling: {"type", "name", "dead", "hp" (share of max), "equip": {slot: Item}}; empty = none hired.
var merc := {}
var d := {}
var _charm_sig := ""
var set_worn := {}


func _init() -> void:
	inv.changed.connect(_on_inv_changed)


# Charms count from the bag, so the stats follow them in and out of it.
func _on_inv_changed() -> void:
	var sig := ""
	for it in inv.items:
		if it.slot() == "charm":
			sig += "%d|" % it.get_instance_id()
	if sig != _charm_sig:
		_charm_sig = sig
		recalc()
		changed.emit()


func cls() -> Dictionary:
	return DB.class_def(class_id)


static func xp_for(lv: int) -> int:
	if lv <= 1:
		return 0
	var l := float(lv - 1)
	var extra := 1.0 + pow(maxf(0.0, lv - 80.0), 2.0) / 60.0
	return int(177.0 * pow(l, 2.46) * extra + 60.0 * l)


func add_xp(n: int) -> void:
	if level >= MAX_LEVEL:
		return
	xp += int(n * (1.0 + d.get("xp_pct", 0.0) / 100.0))
	while level < MAX_LEVEL and xp >= xp_for(level + 1):
		level += 1
		stat_points += 5
		skill_points += 1
		recalc()
		hp = d.hp_max
		mana = d.mana_max
		leveled.emit(level)
	changed.emit()


func stat(s: String) -> int:
	return int(d.get(s, 0))


func meets_req(k: String, v: int) -> bool:
	if k == "level":
		return level >= v
	return stat(k) >= v


func can_equip(it: Item) -> bool:
	var only := str(it.base().get("class", ""))
	if only != "" and only != class_id:
		return false
	var r := it.req()
	for k in r:
		if not meets_req(k, int(r[k])):
			return false
	return true


func slot_for(it: Item) -> Array:
	match it.slot():
		"ring":
			return ["ring1", "ring2"]
		"weapon":
			return ["weapon"]
		_:
			return [it.slot()] if it.slot() in SLOTS else []


func weapon() -> Item:
	return equip.get("weapon", null)


func skill_rank(id: String) -> int:
	var r := int(skills.get(id, 0))
	if r <= 0:
		return 0
	var sk := DB.skill(id)
	return r + int(d.get("skills", 0)) + int(d.get("class_" + class_id, 0)) + int(d.get("tree_" + str(sk.get("tree", "")), 0))


func skill_param(id: String, p: String, rank := -1) -> Variant:
	var s := DB.skill(id)
	var v = s.get("params", {}).get(p, null)
	if v == null:
		return null
	if rank < 0:
		rank = maxi(1, skill_rank(id))
	if v is Array and v.size() == 2 and v[0] is Array:
		var a: Array = v[0]
		var b: Array = v[1]
		return Vector2(a[0] + b[0] * (rank - 1), a[1] + b[1] * (rank - 1))
	if v is Array and v.size() >= 2:
		return float(v[0]) + float(v[1]) * (rank - 1)
	return v


func skill_mana(id: String) -> float:
	var s := DB.skill(id)
	var m = s.get("mana", 0)
	var r := maxi(1, skill_rank(id))
	if m is Array:
		return float(m[0]) + float(m[1]) * (r - 1)
	return float(m)


func synergy_mult(id: String) -> float:
	var syn: Dictionary = DB.skill(id).get("synergy", {})
	var total := 0.0
	for k in syn:
		total += float(syn[k]) * int(skills.get(k, 0))
	return 1.0 + total / 100.0


func skill_req_level(id: String) -> int:
	return [1, 1, 6, 12, 18][clampi(int(DB.skill(id).get("tier", 1)), 0, 4)]


func can_learn(id: String) -> bool:
	var s := DB.skill(id)
	if s.is_empty() or s.get("class", "") != class_id:
		return false
	return skill_points > 0 and level >= skill_req_level(id) and int(skills.get(id, 0)) < int(s.get("max_rank", 20))


func learn(id: String) -> void:
	if not can_learn(id):
		return
	skills[id] = int(skills.get(id, 0)) + 1
	skill_points -= 1
	recalc()
	changed.emit()


func spend_stat(s: String) -> void:
	if stat_points <= 0:
		return
	alloc[s] = int(alloc.get(s, 0)) + 1
	stat_points -= 1
	recalc()
	changed.emit()


func respec() -> void:
	for s in alloc:
		stat_points += int(alloc[s])
		alloc[s] = 0
	for k in skills:
		skill_points += int(skills[k])
	skills.clear()
	rmb = "utok"
	hotkeys = ["", "", "", ""]
	recalc()
	changed.emit()


func belt_size() -> int:
	var b: Item = equip.get("belt", null)
	return clampi(4 + (int(b.base().get("belt_slots", 0)) if b else 0), 4, 8)


func add_buff(id: String, mods: Dictionary, seconds: float, form := "") -> void:
	for b in buffs:
		if b.id == id:
			b.mods = mods
			b.t = seconds
			b.form = form
			recalc()
			return
	buffs.append({"id": id, "mods": mods, "t": seconds, "form": form})
	recalc()


# The shape a buff has put the hero in ("" = their own).
func active_form() -> String:
	for b in buffs:
		if str(b.get("form", "")) != "":
			return str(b.form)
	return ""


func tick_buffs(delta: float) -> void:
	var dirty := false
	for b in buffs.duplicate():
		b.t -= delta
		if b.t <= 0:
			buffs.erase(b)
			dirty = true
	if dirty:
		recalc()


func recalc() -> void:
	var c := cls()
	var m := {}
	var add := func(k: String, v: float) -> void:
		m[k] = m.get(k, 0.0) + v
	for sl in equip:
		var it: Item = equip[sl]
		if it == null or it.broken():
			continue
		var sm := it.stat_mods()
		for k in sm:
			add.call(k, sm[k])
	# set bonuses by how many pieces of each set are worn
	var worn := {}
	for sl in equip:
		var it: Item = equip[sl]
		if it and not it.broken() and it.rarity == Item.SET and it.identified:
			var sid := str(DB.set_items.get(it.set_id, {}).get("set", ""))
			if sid != "":
				worn[sid] = int(worn.get(sid, 0)) + 1
	set_worn = worn
	for sid in worn:
		var sd: Dictionary = DB.sets.get(sid, {})
		for k in sd.get("bonus", {}):
			var need: int = sd.pieces.size() if k == "full" else int(k)
			if int(worn[sid]) >= need:
				for bm in sd.bonus[k]:
					add.call(str(bm.stat), float(bm.get("min", bm.get("value", 0))))
	# charms work from the bag
	for it in inv.items:
		if it.slot() == "charm" and it.identified and meets_req("level", int(it.req().get("level", 0))):
			var cm: Dictionary = it.stat_mods()
			for k in cm:
				add.call(k, cm[k])
	for id in skills:
		var s := DB.skill(id)
		if s.get("type", "") != "passive":
			continue
		for p in s.get("params", {}):
			var pv = skill_param(id, p)
			if pv is float or pv is int:
				add.call(p, float(pv))
	for b in buffs:
		for k in b.mods:
			add.call(k, float(b.mods[k]))
	var out := {}
	var base: Dictionary = c.get("base", {"sila": 15, "obratnost": 15, "magie": 15, "vitalita": 15})
	for s in BASE_STATS:
		out[s] = int(base.get(s, 10)) + int(alloc.get(s, 0)) + int(m.get(s, 0.0) + m.get("vse_staty", 0.0))
	out.hp_max = (float(c.get("base_hp", 40)) + out.vitalita * float(c.get("hp_per_vit", 2.0)) + (level - 1) * float(c.get("hp_per_level", 2.0)) + m.get("hp", 0.0)) * (1.0 + m.get("hp_pct", 0.0) / 100.0)
	out.mana_max = (float(c.get("base_mana", 10)) + out.magie * float(c.get("mana_per_mag", 1.0)) + (level - 1) * float(c.get("mana_per_level", 1.0)) + m.get("mana", 0.0)) * (1.0 + m.get("mana_pct", 0.0) / 100.0)
	var arm := 0.0
	for sl in equip:
		var it: Item = equip[sl]
		if it and not it.broken():
			arm += it.armor
	out.armor = int(arm * (1.0 + m.get("armor_pct", 0.0) / 100.0) + m.get("armor", 0.0) + out.obratnost / 4)
	out.to_hit = maxi(1, int((out.obratnost * 5 - 35 + float(c.get("ar_bonus", 0)) + m.get("to_hit", 0.0)) * (1.0 + m.get("to_hit_pct", 0.0) / 100.0)))
	var w := weapon()
	var stat_name := "sila"
	var wd := Vector2(1, 3)
	var spd := "normal"
	if w and not w.broken():
		wd = Vector2(w.dmg)
		stat_name = str(w.base().get("dmg_stat", "sila"))
		spd = str(w.base().get("speed", "normal"))
	var dmult : float = (1.0 + m.get("dmg_pct", 0.0) / 100.0) * (1.0 + out[stat_name] / 100.0)
	out.dmg_min = (wd.x + m.get("dmg_min", 0.0)) * dmult
	out.dmg_max = maxf(out.dmg_min, (wd.y + m.get("dmg_max", 0.0)) * dmult)
	out.aps = SPEED.get(spd, 1.25) * (1.0 + Combat.diminish(m.get("attack_speed", 0.0)) / 100.0)
	out.cast_speed = 1.0 + Combat.diminish(m.get("cast_speed", 0.0)) / 100.0
	out.hit_recovery = Combat.diminish(m.get("hit_recovery", 0.0))
	out.dmg_reduce_pct = minf(50.0, m.get("dmg_reduce_pct", 0.0))
	var pen : int = [0, 30, 60][clampi(Game.difficulty, 0, 2)]
	for e in ELEMENTS:
		out["res_" + e] = clampi(int(m.get("res_" + e, 0.0) + m.get("res_all", 0.0)) - pen, -100, 75)
		out[e + "_dmg"] = m.get(e + "_dmg", 0.0)
	var lamp: Item = equip.get("lamp", null)
	out.light_radius = 2.0 + (float(lamp.base().get("light", 0)) if lamp else 0.0) + m.get("light_radius", 0.0) + Game.seal_count()
	# D2: blocking from the shield and items, turned into a chance by dexterity against level
	var blocking: float = m.get("block", 0.0) + (float(equip["offhand"].base().get("block", 0)) if equip.get("offhand") else 0.0)
	out.blocking = blocking
	out.block = int(clampf(blocking * (out.obratnost - 15) / (level * 2.0), 0.0, 75.0)) if blocking > 0.0 else 0
	for k in m:
		if not out.has(k):
			out[k] = m[k]
	d = out
	hp = minf(hp, d.hp_max)
	mana = minf(mana, d.mana_max)


# ---------------------------------------------------------------- what an item would change
# The hero's numbers with it worn in sl, everything else as it is now.
func preview(it: Item, sl: String) -> Dictionary:
	var keep := [equip.duplicate(), d, set_worn, hp, mana]
	equip[sl] = it
	if sl == "weapon" and it.two_handed():
		equip.erase("offhand")
	recalc()
	var out := d
	equip = keep[0]
	d = keep[1]
	set_worn = keep[2]
	hp = keep[3]
	mana = keep[4]
	return out


func caster() -> bool:
	return "book" in cls().get("loot", {}).get("offhand", [])


func _dps(dd: Dictionary) -> float:
	var elem := 0.0
	for e in ELEMENTS:
		elem += float(dd.get(e + "_dmg", 0.0))
	return ((float(dd.get("dmg_min", 0)) + float(dd.get("dmg_max", 0))) / 2.0 + elem) * float(dd.get("aps", 1.0)) * (1.0 + float(dd.get("crit", 0.0)) / 100.0)


func _skill_bonus(dd: Dictionary) -> float:
	var n := float(dd.get("skills", 0.0)) + float(dd.get("class_" + class_id, 0.0))
	for t in cls().get("trees", []):
		n += float(dd.get("tree_" + str(t.id), 0.0)) / 3.0
	return n


func _res(dd: Dictionary) -> float:
	var n := 0.0
	for e in ELEMENTS:
		n += float(dd.get("res_" + e, 0))
	return n / 4.0


# How much better (+) or worse (-) the hero gets, roughly in percent.
func _score(a: Dictionary, b: Dictionary) -> float:
	var rel := func(k_a: float, k_b: float) -> float: return (k_b - k_a) / maxf(1.0, absf(k_a)) * 100.0
	var s := 0.0
	s += rel.call(_dps(a), _dps(b)) * (0.3 if caster() else 1.0)
	s += rel.call(float(a.hp_max), float(b.hp_max)) * 0.8
	s += rel.call(float(a.mana_max), float(b.mana_max)) * (0.4 if caster() else 0.1)
	s += rel.call(float(a.armor), float(b.armor)) * 0.25
	s += (_res(b) - _res(a)) * 0.6
	s += (_skill_bonus(b) - _skill_bonus(a)) * (15.0 if caster() else 8.0)
	s += (float(b.get("cast_speed", 1.0)) - float(a.get("cast_speed", 1.0))) * (60.0 if caster() else 5.0)
	s += (float(b.get("life_steal", 0.0)) - float(a.get("life_steal", 0.0))) * 1.5
	s += (float(b.get("magic_find", 0.0)) - float(a.get("magic_find", 0.0))) * 0.05
	return s


# The slot an item would go into: an empty one if any, else the one it beats by most.
func best_slot(it: Item) -> String:
	var slots := slot_for(it)
	if slots.is_empty() or (it.slot() == "offhand" and weapon() and weapon().two_handed()):
		return ""
	var best := ""
	var bs := -INF
	for sl in slots:
		if not equip.get(sl):
			return sl
		var s := _score(d, preview(it, sl))
		if s > bs:
			bs = s
			best = sl
	return best


var _cmp_sig := ""
var _cmp_cache := {}


# NAN when there is nothing to judge (not wearable, unknown, already worn).
func upgrade_score(it: Item) -> float:
	if not it.is_equipment() or (it.rarity != Item.NORMAL and not it.identified) or not can_equip(it) or it in equip.values():
		return NAN
	var sig := "%d|%s|%s" % [level, str(alloc), ",".join(equip.values().map(func(e): return str(e.get_instance_id()) + ":" + str(e.socketed.size()) if e else "-"))]
	if sig != _cmp_sig:
		_cmp_sig = sig
		_cmp_cache.clear()
	var key := "%d:%d:%d" % [it.get_instance_id(), it.socketed.size(), it.mods.size()]
	if not _cmp_cache.has(key):
		var sl := best_slot(it)
		_cmp_cache[key] = NAN if sl == "" else _score(d, preview(it, sl))
	return _cmp_cache[key]


const DELTA_KEYS := [
	["dps", {"cs": "Poškození za sekundu", "en": "Damage per second"}],
	["hp_max", {"cs": "Život", "en": "Life"}],
	["mana_max", {"cs": "Mana", "en": "Mana"}],
	["armor", {"cs": "Zbroj", "en": "Armour"}],
	["to_hit", {"cs": "Útok", "en": "Attack rating"}],
	["block", {"cs": "Vykrytí %", "en": "Block %"}],
	["skillsum", {"cs": "Úrovně dovedností", "en": "Skill levels"}],
	["res_fire", {"cs": "Odolnost: oheň", "en": "Fire resist"}],
	["res_cold", {"cs": "Odolnost: mráz", "en": "Cold resist"}],
	["res_lightning", {"cs": "Odolnost: blesk", "en": "Lightning resist"}],
	["res_poison", {"cs": "Odolnost: jed", "en": "Poison resist"}],
	["sila", {"cs": "Síla", "en": "Strength"}],
	["obratnost", {"cs": "Obratnost", "en": "Dexterity"}],
	["magie", {"cs": "Magie", "en": "Magic"}],
	["vitalita", {"cs": "Vitalita", "en": "Vitality"}],
	["life_steal", {"cs": "Krádež života %", "en": "Life stolen %"}],
	["mana_steal", {"cs": "Krádež many %", "en": "Mana stolen %"}],
	["move_speed", {"cs": "Rychlost chůze %", "en": "Movement speed %"}],
	["magic_find", {"cs": "Šance na kouzelné věci %", "en": "Magic find %"}],
	["gold_find", {"cs": "Groše %", "en": "Gold find %"}],
	["light_radius", {"cs": "Dosvit", "en": "Light radius"}],
]


# [text, good?] per number that changes if the item were worn.
func delta_lines(it: Item) -> Array:
	var sl := best_slot(it)
	if sl == "":
		return []
	var a := d.duplicate()
	var b := preview(it, sl).duplicate()
	a["dps"] = _dps(a)
	b["dps"] = _dps(b)
	a["skillsum"] = _skill_bonus(a)
	b["skillsum"] = _skill_bonus(b)
	var out := []
	for kv in DELTA_KEYS:
		var dv := float(b.get(kv[0], 0.0)) - float(a.get(kv[0], 0.0))
		if absf(dv) < 0.5:
			continue
		out.append(["%s %s%d" % [L.t(kv[1]), "+" if dv > 0 else "−", absi(roundi(dv))], dv > 0])
	return out


const SPEED := {"fast": 1.6, "normal": 1.25, "slow": 0.95, "very_slow": 0.75}
const STAT_KEYS := ["sila", "obratnost", "magie", "vitalita", "vse_staty", "hp", "mana", "hp_pct", "mana_pct",
	"dmg_pct", "dmg_min", "dmg_max", "to_hit", "armor", "armor_pct", "block", "fire_dmg", "lightning_dmg",
	"cold_dmg", "poison_dmg", "res_fire", "res_lightning", "res_cold", "res_poison", "res_all", "life_steal",
	"mana_steal", "attack_speed", "cast_speed", "move_speed", "light_radius", "gold_find", "magic_find",
	"hp_regen", "mana_regen", "thorns", "dmg_reduce", "skills", "crit", "xp_pct", "to_hit_pct", "crushing_blow",
	"hit_recovery", "dmg_reduce_pct"]


func start_new(cid: String, nm: String) -> void:
	class_id = cid
	hero_name = nm
	level = 1
	xp = 0
	gold = 50
	skills = {}
	var c := cls()
	var first := ""
	for t in c.get("trees", []):
		if first == "" and t.get("skills", []).size() > 0:
			first = t.skills[0]
	if first != "":
		skills[first] = 1
	rmb = str(c.get("default_rmb", first if first != "" else "utok"))
	belt = []
	belt.resize(8)
	for id in c.get("start_items", []):
		var it := Item.create(id, 1)
		if it.base().is_empty():
			continue
		if it.slot() == "consumable" and _belt_put(it):
			continue
		var placed := false
		for sl in slot_for(it):
			if not equip.get(sl):
				equip[sl] = it
				placed = true
				break
		if not placed:
			inv.add(it)
	recalc()
	hp = d.hp_max
	mana = d.mana_max


func belt_free_for(it: Item) -> bool:
	if not _belt_kind(it):
		return false
	for i in belt_size():
		if belt[i] == null:
			return true
	return false


func _belt_kind(it: Item) -> bool:
	return str(it.base().get("use", {}).keys()).contains("pct") or it.base().get("use", {}).has("rejuv")


func _belt_put(it: Item) -> bool:
	if not _belt_kind(it):
		return false
	for i in belt_size():
		if belt[i] == null:
			belt[i] = it
			return true
	return false


func pickup(it: Item) -> bool:
	if it.slot() == "gold":
		gold += it.qty
		changed.emit()
		return true
	if it.slot() == "consumable" and _belt_put(it):
		changed.emit()
		return true
	var ok := inv.add(it)
	if ok:
		Game.note_found(it)
	changed.emit()
	return ok


func to_dict() -> Dictionary:
	var eq := {}
	for k in equip:
		if equip[k]:
			eq[k] = equip[k].to_dict()
	return {"class": class_id, "name": hero_name, "level": level, "xp": xp, "alloc": alloc,
		"sp": stat_points, "kp": skill_points, "skills": skills, "hp": hp, "mana": mana, "gold": gold,
		"inv": inv.to_array(), "stash": stash.to_array(), "equip": eq,
		"belt": belt.map(func(i): return i.to_dict() if i else null), "rmb": rmb, "hotkeys": hotkeys,
		"merc": _merc_dict()}


func _merc_dict() -> Dictionary:
	if merc.is_empty():
		return {}
	var eq := {}
	for k in merc.get("equip", {}):
		if merc.equip[k]:
			eq[k] = merc.equip[k].to_dict()
	return {"type": merc.type, "name": merc.name, "dead": merc.get("dead", false), "hp": merc.get("hp", 1.0), "equip": eq}


func from_dict(s: Dictionary) -> void:
	class_id = s.get("class", "havir")
	hero_name = s.get("name", "")
	level = int(s.get("level", 1))
	xp = int(s.get("xp", 0))
	alloc = s.get("alloc", alloc)
	stat_points = int(s.get("sp", 0))
	skill_points = int(s.get("kp", 0))
	skills = {}
	var sk: Dictionary = s.get("skills", {})
	for k in sk:
		skills[k] = int(sk[k])
	gold = int(s.get("gold", 0))
	inv.load_array(s.get("inv", []))
	stash.load_array(s.get("stash", []))
	equip = {}
	var eq: Dictionary = s.get("equip", {})
	for k in eq:
		equip[k] = Item.from_dict(eq[k])
	belt = []
	belt.resize(8)
	var bl: Array = s.get("belt", [])
	for i in mini(8, bl.size()):
		belt[i] = Item.from_dict(bl[i]) if bl[i] else null
	rmb = s.get("rmb", "utok")
	hotkeys = s.get("hotkeys", ["", "", "", ""])
	merc = {}
	var mc: Dictionary = s.get("merc", {})
	if DB.hirelings.has(str(mc.get("type", ""))):
		var meq := {}
		for k in mc.get("equip", {}):
			meq[k] = Item.from_dict(mc.equip[k])
		merc = {"type": str(mc.type), "name": str(mc.get("name", "")), "dead": bool(mc.get("dead", false)), "hp": float(mc.get("hp", 1.0)), "equip": meq}
	recalc()
	hp = clampf(float(s.get("hp", d.hp_max)), 1.0, d.hp_max)
	mana = clampf(float(s.get("mana", d.mana_max)), 0.0, d.mana_max)
