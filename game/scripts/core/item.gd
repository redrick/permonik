class_name Item
extends RefCounted

enum { NORMAL, MAGIC, UNIQUE }

const COL_NORMAL := Color("e8e2d4")
const COL_MAGIC := Color("7f9bff")
const COL_UNIQUE := Color("d6b25e")
const COL_QUEST := Color("e98c3a")
const COL_BAD := Color("e04b4b")
const COL_INFO := Color("b9b3a6")

var base_id := ""
var rarity := NORMAL
var ilvl := 1
var identified := true
var prefix := ""
var suffix := ""
var unique_id := ""
var mods: Array = []
var dmg := Vector2i.ZERO
var armor := 0
var dur := 0
var max_dur := 0
var qty := 1
var pos := Vector2i(-1, -1)


static func create(id: String, level := 1) -> Item:
	var it := Item.new()
	it.base_id = id
	it.ilvl = level
	var b := it.base()
	var d = b.get("dmg", null)
	if d is Array and d.size() >= 2:
		it.dmg = Vector2i(int(d[0]), int(d[1]))
	var a = b.get("armor", null)
	if a is Array and a.size() >= 2:
		it.armor = randi_range(int(a[0]), int(a[1]))
	elif a != null:
		it.armor = int(a)
	it.max_dur = int(b.get("durability", 0))
	it.dur = it.max_dur
	return it


func base() -> Dictionary:
	return DB.item(base_id)


func slot() -> String:
	return str(base().get("slot", "quest"))


func kind() -> String:
	return str(base().get("kind", ""))


func size() -> Vector2i:
	var s = base().get("size", [1, 1])
	return Vector2i(int(s[0]), int(s[1]))


func icon() -> Texture2D:
	var ic := str(base().get("icon", base_id))
	if unique_id != "":
		ic = str(DB.uniques.get(unique_id, {}).get("icon", ic))
	var t := DB.tex("items/" + ic)
	if t == null:
		var s := size()
		t = DB.placeholder("item_" + slot(), Vector2i(s.x * 56, s.y * 56), color())
	return t


func is_equipment() -> bool:
	return slot() in ["weapon", "offhand", "head", "body", "belt", "lamp", "ring", "amulet"]


func is_stackable() -> bool:
	return int(base().get("stack", 0)) > 0 or slot() == "gold"


func is_ranged() -> bool:
	return kind() in ["bow", "crossbow"]


func two_handed() -> bool:
	return bool(base().get("two_handed", false))


func color() -> Color:
	if slot() == "quest":
		return COL_QUEST
	match rarity:
		MAGIC:
			return COL_MAGIC
		UNIQUE:
			return COL_UNIQUE
	return COL_NORMAL


func gender() -> String:
	return str(base().get("gender", "m"))


func display_name() -> String:
	if slot() == "gold":
		return "%d %s" % [qty, L.t("gold")]
	var bn := L.t(base().get("name", base_id))
	if rarity == UNIQUE and identified:
		return L.t(DB.uniques.get(unique_id, {}).get("name", bn))
	if rarity == MAGIC and identified:
		var parts := []
		if prefix != "":
			var p := _affix("prefixes", prefix)
			parts.append(L.gendered(p.get("name", ""), gender()))
		parts.append(bn if parts.is_empty() or L.lang == "en" else bn.left(1).to_lower() + bn.substr(1))
		if suffix != "":
			parts.append(L.t(_affix("suffixes", suffix).get("name", "")))
		var s := " ".join(parts)
		return s
	return bn


static func _affix(group: String, id: String) -> Dictionary:
	for a in DB.affixes.get(group, []):
		if a.get("id", "") == id:
			return a
	return {}


func stat_mods() -> Dictionary:
	var out := {}
	for m in mods:
		out[m.stat] = out.get(m.stat, 0.0) + float(m.value)
	return out


func broken() -> bool:
	return max_dur > 0 and dur <= 0


func req() -> Dictionary:
	var r: Dictionary = base().get("req", {}).duplicate()
	if rarity == UNIQUE:
		var q := int(DB.uniques.get(unique_id, {}).get("qlvl", 0))
		r["level"] = maxi(int(r.get("level", 0)), int(q * 0.8))
	elif rarity == MAGIC:
		var lv := 0
		for id in [prefix, suffix]:
			if id != "":
				var a := _affix("prefixes", id)
				if a.is_empty():
					a = _affix("suffixes", id)
				lv = maxi(lv, int(int(a.get("qlvl", 0)) * 0.75))
		r["level"] = maxi(int(r.get("level", 0)), lv)
	return r


func price() -> int:
	var p := float(base().get("price", 10))
	if rarity == MAGIC:
		p *= 2.0 + mods.size() * 1.5 + ilvl * 0.08
	elif rarity == UNIQUE:
		p *= 6.0 + ilvl * 0.15
	if max_dur > 0:
		p *= 0.4 + 0.6 * float(dur) / max_dur
	return maxi(1, int(p))


func sell_price() -> int:
	if slot() == "quest" or bool(base().get("unsellable", false)):
		return 0
	return maxi(1, price() / 4)


func repair_cost() -> int:
	if max_dur <= 0 or dur >= max_dur:
		return 0
	return maxi(1, int(float(base().get("price", 10)) * 0.25 * (1.0 - float(dur) / max_dur) * (1 + rarity)))


func damage_range() -> Vector2:
	var sm := stat_mods()
	var pct : float = 1.0 + sm.get("dmg_pct", 0.0) / 100.0
	return Vector2((dmg.x + sm.get("dmg_min", 0.0)) * pct, (dmg.y + sm.get("dmg_max", 0.0)) * pct)


func total_armor() -> int:
	var sm := stat_mods()
	return int(armor * (1.0 + sm.get("armor_pct", 0.0) / 100.0) + sm.get("armor", 0.0))


func tooltip(ch = null) -> Array:
	var lines := []
	lines.append([display_name(), color()])
	if rarity != NORMAL and identified and slot() != "gold":
		lines.append([L.t(base().get("name", base_id)), COL_INFO])
	var b := base()
	if dmg != Vector2i.ZERO:
		var r := damage_range()
		lines.append(["%s: %d–%d" % [L.t("damage"), int(r.x), int(r.y)], COL_NORMAL])
		lines.append([L.t("speed_" + str(b.get("speed", "normal"))), COL_INFO])
	if armor > 0:
		lines.append(["%s: %d" % [L.t("armor"), total_armor()], COL_NORMAL])
	if b.has("block"):
		lines.append([L.t("tt_block", {"v": b.block, "n": b.block}), COL_NORMAL])
	if b.has("light"):
		lines.append([L.t("tt_light", {"v": b.light, "n": b.light}), COL_NORMAL])
	if b.has("belt_slots"):
		lines.append([L.t("tt_belt", {"v": b.belt_slots, "n": b.belt_slots}), COL_NORMAL])
	var u: Dictionary = b.get("use", {})
	if u.has("heal_pct"):
		lines.append([L.t({"cs": "Doplní %d %% života", "en": "Restores %d%% life"}) % int(u.heal_pct), COL_INFO])
	if u.has("mana_pct"):
		lines.append([L.t({"cs": "Doplní %d %% many", "en": "Restores %d%% mana"}) % int(u.mana_pct), COL_INFO])
	if b.has("desc") or b.has("flavor"):
		lines.append([L.t(b.get("desc", b.get("flavor", ""))), COL_INFO])
	if u.has("heal_pct") or u.has("mana_pct") or u.has("rejuv"):
		lines.append([L.t({"cs": "Pravým tlačítkem vypít", "en": "Right-click to drink"}), COL_INFO])
	if max_dur > 0:
		lines.append(["%s: %d / %d" % [L.t("durability"), dur, max_dur], COL_BAD if dur < max_dur / 5 else COL_INFO])
	if rarity != NORMAL and not identified:
		lines.append([L.t("unidentified"), COL_BAD])
	elif rarity != NORMAL:
		for m in mods:
			lines.append([Item.mod_text(m.stat, m.value), COL_MAGIC])
	var rq := req()
	var parts := []
	for k in ["level", "sila", "obratnost", "magie"]:
		if int(rq.get(k, 0)) > 0:
			var ok := true
			if ch:
				ok = ch.meets_req(k, int(rq[k]))
			parts.append([("%s %d" % [L.t("req_" + k), int(rq[k])]), COL_NORMAL if ok else COL_BAD])
	if not parts.is_empty():
		lines.append([L.t("requirements") + ":", COL_INFO])
		for p in parts:
			lines.append(p)
	if rarity == UNIQUE and identified:
		var fl = DB.uniques.get(unique_id, {}).get("flavor", null)
		if fl:
			lines.append(["„%s“" % L.t(fl), Color("a08a5a")])
	return lines


static func mod_text(stat: String, value: float) -> String:
	var v := int(round(value))
	var key := "mod_" + stat
	var sgn := "+" if v >= 0 else ""
	if L.ui.has(key) or MOD_TEXT.has(stat):
		var tpl = L.ui[key] if L.ui.has(key) else MOD_TEXT[stat]
		return L.t(tpl, {"v": "%s%d" % [sgn, v], "n": v})
	return "%s%d %s" % [sgn, v, stat]


const MOD_TEXT := {
	"sila": {"cs": "{v} k síle", "en": "{v} to Strength"},
	"obratnost": {"cs": "{v} k obratnosti", "en": "{v} to Dexterity"},
	"magie": {"cs": "{v} k magii", "en": "{v} to Magic"},
	"vitalita": {"cs": "{v} k vitalitě", "en": "{v} to Vitality"},
	"vse_staty": {"cs": "{v} ke všem vlastnostem", "en": "{v} to all attributes"},
	"hp": {"cs": "{v} k životu", "en": "{v} to Life"},
	"mana": {"cs": "{v} k maně", "en": "{v} to Mana"},
	"hp_pct": {"cs": "{v} % života", "en": "{v}% Life"},
	"mana_pct": {"cs": "{v} % many", "en": "{v}% Mana"},
	"dmg_pct": {"cs": "{v} % poškození", "en": "{v}% enhanced damage"},
	"dmg_min": {"cs": "{v} k minimálnímu poškození", "en": "{v} to minimum damage"},
	"dmg_max": {"cs": "{v} k maximálnímu poškození", "en": "{v} to maximum damage"},
	"to_hit": {"cs": "{v} k útoku", "en": "{v} to attack rating"},
	"armor": {"cs": "{v} ke zbroji", "en": "{v} to armour"},
	"armor_pct": {"cs": "{v} % zbroje", "en": "{v}% enhanced armour"},
	"block": {"cs": "{v} % šance vykrýt", "en": "{v}% chance to block"},
	"fire_dmg": {"cs": "{v} ohnivého poškození", "en": "{v} fire damage"},
	"lightning_dmg": {"cs": "{v} bleskového poškození", "en": "{v} lightning damage"},
	"cold_dmg": {"cs": "{v} mrazivého poškození", "en": "{v} cold damage"},
	"poison_dmg": {"cs": "{v} jedového poškození", "en": "{v} poison damage"},
	"res_fire": {"cs": "Odolnost proti ohni {v} %", "en": "Fire resist {v}%"},
	"res_lightning": {"cs": "Odolnost proti blesku {v} %", "en": "Lightning resist {v}%"},
	"res_cold": {"cs": "Odolnost proti mrazu {v} %", "en": "Cold resist {v}%"},
	"res_poison": {"cs": "Odolnost proti jedu {v} %", "en": "Poison resist {v}%"},
	"res_all": {"cs": "Všechny odolnosti {v} %", "en": "All resistances {v}%"},
	"life_steal": {"cs": "{v} % poškození ukradne život", "en": "{v}% life stolen per hit"},
	"mana_steal": {"cs": "{v} % poškození ukradne manu", "en": "{v}% mana stolen per hit"},
	"attack_speed": {"cs": "{v} % rychlost útoku", "en": "{v}% attack speed"},
	"cast_speed": {"cs": "{v} % rychlost kouzlení", "en": "{v}% cast speed"},
	"move_speed": {"cs": "{v} % rychlost chůze", "en": "{v}% movement speed"},
	"light_radius": {"cs": "{v} k dosvitu", "en": "{v} to light radius"},
	"gold_find": {"cs": "{v} % víc grošů", "en": "{v}% extra gold"},
	"magic_find": {"cs": "{v} % šance na kouzelné věci", "en": "{v}% magic find"},
	"hp_regen": {"cs": "Obnova života {v}/s", "en": "Regenerate {v} life/s"},
	"mana_regen": {"cs": "{v} % obnova many", "en": "{v}% mana regeneration"},
	"thorns": {"cs": "Útočník utrpí {v} poškození", "en": "Attacker takes {v} damage"},
	"dmg_reduce": {"cs": "Poškození sníženo o {v}", "en": "Damage reduced by {v}"},
	"skills": {"cs": "{v} ke všem dovednostem", "en": "{v} to all skills"},
	"crit": {"cs": "{v} % šance na zničující úder", "en": "{v}% chance of crushing blow"},
	"xp_pct": {"cs": "{v} % zkušeností", "en": "{v}% experience"},
}


func to_dict() -> Dictionary:
	return {"b": base_id, "r": rarity, "l": ilvl, "id": identified, "p": prefix, "s": suffix, "u": unique_id,
		"m": mods, "d": [dmg.x, dmg.y], "a": armor, "du": dur, "md": max_dur, "q": qty, "x": pos.x, "y": pos.y}


static func from_dict(d: Dictionary) -> Item:
	var it := Item.new()
	it.base_id = d.get("b", "")
	it.rarity = int(d.get("r", 0))
	it.ilvl = int(d.get("l", 1))
	it.identified = bool(d.get("id", true))
	it.prefix = d.get("p", "")
	it.suffix = d.get("s", "")
	it.unique_id = d.get("u", "")
	it.mods = d.get("m", [])
	var dd = d.get("d", [0, 0])
	it.dmg = Vector2i(int(dd[0]), int(dd[1]))
	it.armor = int(d.get("a", 0))
	it.dur = int(d.get("du", 0))
	it.max_dur = int(d.get("md", 0))
	it.qty = int(d.get("q", 1))
	it.pos = Vector2i(int(d.get("x", -1)), int(d.get("y", -1)))
	return it
