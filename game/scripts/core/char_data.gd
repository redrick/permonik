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
var stash := Inventory.new(10, 8)
var equip := {}
var belt: Array = []
var buffs: Array = []
var rmb := "utok"
var hotkeys := ["", "", "", ""]
var d := {}


func cls() -> Dictionary:
	return DB.classes.get(class_id, {})


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
	return r + int(d.get("skills", 0))


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


func add_buff(id: String, mods: Dictionary, seconds: float) -> void:
	for b in buffs:
		if b.id == id:
			b.mods = mods
			b.t = seconds
			recalc()
			return
	buffs.append({"id": id, "mods": mods, "t": seconds})
	recalc()


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
	out.to_hit = int(out.obratnost * 5 + level * 8 + m.get("to_hit", 0.0))
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
	out.aps = SPEED.get(spd, 1.25) * (1.0 + m.get("attack_speed", 0.0) / 100.0)
	out.cast_speed = 1.0 + m.get("cast_speed", 0.0) / 100.0
	var pen : int = [0, 30, 60][clampi(Game.difficulty, 0, 2)]
	for e in ELEMENTS:
		out["res_" + e] = clampi(int(m.get("res_" + e, 0.0) + m.get("res_all", 0.0)) - pen, -100, 75)
		out[e + "_dmg"] = m.get(e + "_dmg", 0.0)
	var lamp: Item = equip.get("lamp", null)
	out.light_radius = 2.0 + (float(lamp.base().get("light", 0)) if lamp else 0.0) + m.get("light_radius", 0.0) + Game.seal_count()
	out.block = int(m.get("block", 0.0) + (float(equip["offhand"].base().get("block", 0)) if equip.get("offhand") else 0.0))
	for k in m:
		if not out.has(k):
			out[k] = m[k]
	d = out
	hp = minf(hp, d.hp_max)
	mana = minf(mana, d.mana_max)


const SPEED := {"fast": 1.6, "normal": 1.25, "slow": 0.95, "very_slow": 0.75}
const STAT_KEYS := ["sila", "obratnost", "magie", "vitalita", "vse_staty", "hp", "mana", "hp_pct", "mana_pct",
	"dmg_pct", "dmg_min", "dmg_max", "to_hit", "armor", "armor_pct", "block", "fire_dmg", "lightning_dmg",
	"cold_dmg", "poison_dmg", "res_fire", "res_lightning", "res_cold", "res_poison", "res_all", "life_steal",
	"mana_steal", "attack_speed", "cast_speed", "move_speed", "light_radius", "gold_find", "magic_find",
	"hp_regen", "mana_regen", "thorns", "dmg_reduce", "skills", "crit", "xp_pct"]


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


func _belt_put(it: Item) -> bool:
	if not str(it.base().get("use", {}).keys()).contains("pct") and not it.base().get("use", {}).has("rejuv"):
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
		"belt": belt.map(func(i): return i.to_dict() if i else null), "rmb": rmb, "hotkeys": hotkeys}


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
	recalc()
	hp = clampf(float(s.get("hp", d.hp_max)), 1.0, d.hp_max)
	mana = clampf(float(s.get("mana", d.mana_max)), 0.0, d.mana_max)
