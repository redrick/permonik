class_name Item
extends RefCounted

enum { NORMAL, MAGIC, UNIQUE, RARE, SET }

const COL_NORMAL := Color("e8e2d4")
const COL_MAGIC := Color("7f9bff")
const COL_UNIQUE := Color("d6b25e")
const COL_RARE := Color("efe06a")
const COL_SET := Color("5fd068")
const COL_SOCKET := Color("a0a6ae")
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
var affix_ids: Array = []      # rare: every prefix and suffix it rolled
var rare_name: Array = []      # rare: [first word, second word] indices into rare_names.json
var set_id := ""               # set piece id (sets.json)
var sockets := 0
var socketed: Array = []       # gem / letter items set into the sockets
var word := ""                 # a finished word (words.json) when the letters spell one
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
		RARE:
			return COL_RARE
		SET:
			return COL_SET
	if word != "":
		return COL_UNIQUE
	if sockets > 0:
		return COL_SOCKET
	return COL_NORMAL


func gender() -> String:
	return str(base().get("gender", "m"))


func display_name() -> String:
	if slot() == "gold":
		return "%d %s" % [qty, L.t("gold")]
	var bn := L.t(base().get("name", base_id))
	if rarity == UNIQUE and identified:
		return L.t(DB.uniques.get(unique_id, {}).get("name", bn))
	if rarity == RARE and identified and rare_name.size() == 2:
		var f: Array = DB.rare_names.get("first", [])
		var g: Array = DB.rare_names.get("second", [])
		if int(rare_name[0]) < f.size() and int(rare_name[1]) < g.size():
			return "%s %s" % [L.t(f[int(rare_name[0])]), L.t(g[int(rare_name[1])])]
	if rarity == SET and identified:
		return L.t(DB.set_items.get(set_id, {}).get("name", bn))
	if word != "":
		return "%s „%s“" % [bn, L.t(DB.words.get(word, {}).get("name", word))]
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
	var cat := socket_category()
	for g in socketed:
		for m in g.base().get("socket", {}).get(cat, []):
			out[m.stat] = out.get(m.stat, 0.0) + float(m.value)
	if word != "":
		for m in DB.words.get(word, {}).get("mods", []):
			out[m.stat] = out.get(m.stat, 0.0) + float(m.value)
	return out


# ---------------------------------------------------------------- sockets
func is_socketable() -> bool:
	return slot() in ["gem", "letter"]


# Which table of a gem's effects applies: in a weapon, a shield, or anything else worn.
func socket_category() -> String:
	if slot() == "weapon":
		return "weapon"
	if slot() == "offhand" and kind() == "shield":
		return "shield"
	return "armor"


func max_sockets() -> int:
	var t := int(base().get("tier", 1))
	var sz := size()
	match slot():
		"weapon":
			if sz.x >= 2:
				return 4 if t <= 1 else (5 if t == 2 else 6)
			return 2 if sz.y <= 2 else (3 if t <= 2 else 4)
		"body":
			return 3 if t <= 1 else (4 if t == 2 else 5)
		"head":
			return 2 if t <= 2 else 3
		"offhand":
			if kind() == "shield":
				return 3 if t <= 2 else 4
			return 2
	return 0


func can_socket(g: Item) -> bool:
	return g != null and g.is_socketable() and socketed.size() < sockets


func socket(g: Item) -> bool:
	if not can_socket(g):
		return false
	var one := Item.from_dict(g.to_dict())
	one.qty = 1
	socketed.append(one)
	_check_word()
	return true


# A plain item whose sockets are filled with exactly a word's letters, in order, speaks the word.
func _check_word() -> void:
	word = ""
	if rarity != NORMAL or socketed.size() != sockets:
		return
	var letters := []
	for g in socketed:
		if g.slot() != "letter":
			return
		letters.append(g.base_id.trim_prefix("glag_"))
	var cat := socket_category()
	var kinds := [cat]
	if slot() in ["head", "body"]:
		kinds.append("armor")
	if slot() == "body":
		kinds.append("body")
	for wid in DB.words:
		var wd: Dictionary = DB.words[wid]
		if wd.get("letters", []) == letters:
			for b in wd.get("bases", []):
				if b in kinds:
					word = wid
					return


func glyphs() -> String:
	var out := ""
	for l in DB.words.get(word, {}).get("letters", []):
		out += str(DB.item("glag_" + str(l)).get("glyph", ""))
	return out


func broken() -> bool:
	return max_dur > 0 and dur <= 0


func req() -> Dictionary:
	var r: Dictionary = base().get("req", {}).duplicate()
	if rarity == UNIQUE:
		var q := int(DB.uniques.get(unique_id, {}).get("qlvl", 0))
		r["level"] = maxi(int(r.get("level", 0)), int(q * 0.8))
	elif rarity == SET:
		r["level"] = maxi(int(r.get("level", 0)), int(int(DB.set_items.get(set_id, {}).get("qlvl", 0)) * 0.8))
	elif rarity == MAGIC or rarity == RARE:
		var lv := 0
		for id in [prefix, suffix] + affix_ids:
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
	elif rarity == UNIQUE or rarity == SET:
		p *= 6.0 + ilvl * 0.15
	elif rarity == RARE:
		p *= 3.0 + mods.size() * 1.8 + ilvl * 0.1
	p *= 1.0 + sockets * 0.4
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
	if b.has("desc"):
		lines.append([L.t(b.desc), COL_NORMAL])
	match slot():
		"quest", "key":
			lines.append([L.t({"cs": "Předmět k úkolu", "en": "Quest item"}), COL_QUEST])
		"charm":
			lines.append([L.t({"cs": "Působí, když ho neseš v torně", "en": "Works while carried in your bag"}), COL_INFO])
		"gem":
			if Forge._grade(self) < 4:
				lines.append([L.t({"cs": "3 stejné ve výhni → o stupeň lepší", "en": "3 alike in the forge → one grade better"}), COL_INFO])
		"letter":
			lines.append([L.t({"cs": "Písmena v zásuvkách jednoho předmětu mohou složit slovo", "en": "Letters socketed in one item can spell a word"}), COL_INFO])
	if b.has("flavor"):
		lines.append(["„%s“" % L.t(b.flavor), Color("a08a5a")])
	if u.has("heal_pct") or u.has("mana_pct") or u.has("rejuv"):
		lines.append([L.t({"cs": "Pravým tlačítkem vypít", "en": "Right-click to drink"}), COL_INFO])
	elif u.has("portal") or u.has("identify"):
		lines.append([L.t({"cs": "Pravým tlačítkem přečíst", "en": "Right-click to read"}), COL_INFO])
	if max_dur > 0:
		lines.append(["%s: %d / %d" % [L.t("durability"), dur, max_dur], COL_BAD if dur < max_dur / 5 else COL_INFO])
	if rarity != NORMAL and not identified:
		lines.append([L.t("unidentified"), COL_BAD])
	elif rarity != NORMAL:
		for m in mods:
			lines.append([Item.mod_text(m.stat, m.value), COL_MAGIC])
	if rarity == SET and identified:
		var si: Dictionary = DB.set_items.get(set_id, {})
		var sid := str(si.get("set", ""))
		var sd: Dictionary = DB.sets.get(sid, {})
		var have: int = ch.set_worn.get(sid, 0) if ch else 0
		lines.append([" ", COL_INFO])
		lines.append(["%s  (%d / %d)" % [L.t(sd.get("name", sid)), have, sd.get("pieces", []).size()], COL_SET])
		var worn_ids := {}
		if ch:
			for sl in ch.equip:
				var e: Item = ch.equip[sl]
				if e and e.rarity == SET:
					worn_ids[e.set_id] = true
		for pid in sd.get("pieces", []):
			lines.append(["  " + L.t(DB.set_items.get(pid, {}).get("name", pid)), COL_SET if worn_ids.has(pid) else Color(0.55, 0.6, 0.55)])
		for k in sd.get("bonus", {}):
			var need: int = sd.pieces.size() if k == "full" else int(k)
			var label := L.t({"cs": "Celá sada", "en": "Full set"}) if k == "full" else L.t({"cs": "%d kusy", "en": "%d pieces"}) % need
			var txt := ", ".join(sd.bonus[k].map(func(m): return Item.mod_text(m.stat, float(m.get("min", m.get("value", 0))))))
			lines.append(["%s: %s" % [label, txt], COL_SET if have >= need else Color(0.5, 0.52, 0.5)])
		if sd.has("flavor"):
			lines.append(["„%s“" % L.t(sd.flavor), Color("8aa88a")])
	if is_socketable():
		var where := {"weapon": {"cs": "Ve zbrani", "en": "In a weapon"}, "armor": {"cs": "Ve zbroji", "en": "In armour"}, "shield": {"cs": "Ve štítu", "en": "In a shield"}}
		if b.has("glyph"):
			lines.append(["%s  ·  %s" % [b.glyph, b.get("latin", "")], Color("e0c890")])
		for cat in ["weapon", "armor", "shield"]:
			var ms: Array = b.get("socket", {}).get(cat, [])
			if not ms.is_empty():
				lines.append(["%s: %s" % [L.t(where[cat]), ", ".join(ms.map(func(m): return Item.mod_text(m.stat, m.value)))], COL_MAGIC])
		lines.append([L.t({"cs": "Vlož do zásuvky: polož na předmět", "en": "Socket it: drop it onto an item"}), COL_INFO])
	if word != "":
		var wd: Dictionary = DB.words.get(word, {})
		lines.append(["%s  %s — „%s“" % [glyphs(), L.t(wd.get("name", word)).to_upper(), L.t(wd.get("meaning", ""))], COL_UNIQUE])
		for m in wd.get("mods", []):
			lines.append([Item.mod_text(m.stat, m.value), COL_UNIQUE])
	if sockets > 0:
		lines.append([L.t({"cs": "Zásuvky: %d / %d", "en": "Sockets: %d / %d"}) % [socketed.size(), sockets], COL_SOCKET])
		var cat2 := socket_category()
		for g in socketed:
			var eff: Array = g.base().get("socket", {}).get(cat2, [])
			lines.append(["  %s%s — %s" % [str(g.base().get("glyph", "")) + " " if g.slot() == "letter" else "", g.display_name(),
				", ".join(eff.map(func(m): return Item.mod_text(m.stat, m.value)))], COL_MAGIC])
	var only := str(b.get("class", ""))
	if only != "":
		var ok_cls: bool = ch == null or ch.class_id == only
		lines.append([L.t({"cs": "Jen pro: %s", "en": "%s only"}) % L.t(DB.classes.get(only, {}).get("name", only)), COL_NORMAL if ok_cls else COL_BAD])
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
	if stat.begins_with("class_"):
		var cn := L.t(DB.classes.get(stat.substr(6), {}).get("name", stat))
		return L.t({"cs": "+%d ke všem dovednostem (%s)", "en": "+%d to %s skills"}) % [v, cn]
	if stat.begins_with("tree_"):
		var tid := stat.substr(5)
		var tn := tid
		for cid in DB.classes:
			for t in DB.classes[cid].get("trees", []):
				if t.id == tid:
					tn = L.t(t.name)
		return L.t({"cs": "+%d k dovednostem: %s", "en": "+%d to %s skills"}) % [v, tn]
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
	"block": {"cs": "{v} k vykrývání", "en": "{v} to blocking"},
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
	"crit": {"cs": "{v} % šance na smrtící úder (dvojnásobné poškození)", "en": "{v}% deadly strike"},
	"crushing_blow": {"cs": "{v} % šance na drtivý úder", "en": "{v}% chance of crushing blow"},
	"hit_recovery": {"cs": "{v} % rychlejší zotavení z rány", "en": "{v}% faster hit recovery"},
	"dmg_reduce_pct": {"cs": "Poškození sníženo o {v} %", "en": "Damage reduced by {v}%"},
	"to_hit_pct": {"cs": "{v} % k útoku", "en": "{v}% bonus to attack rating"},
	"xp_pct": {"cs": "{v} % zkušeností", "en": "{v}% experience"},
}


func to_dict() -> Dictionary:
	var out := {"b": base_id, "r": rarity, "l": ilvl, "id": identified, "p": prefix, "s": suffix, "u": unique_id,
		"m": mods, "d": [dmg.x, dmg.y], "a": armor, "du": dur, "md": max_dur, "q": qty, "x": pos.x, "y": pos.y}
	if not affix_ids.is_empty():
		out["ax"] = affix_ids
	if not rare_name.is_empty():
		out["rn"] = rare_name
	if set_id != "":
		out["set"] = set_id
	if sockets > 0:
		out["so"] = sockets
		out["sg"] = socketed.map(func(g): return g.to_dict())
	if word != "":
		out["w"] = word
	return out


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
	it.affix_ids = d.get("ax", [])
	it.rare_name = d.get("rn", [])
	it.set_id = d.get("set", "")
	it.sockets = int(d.get("so", 0))
	for g in d.get("sg", []):
		it.socketed.append(Item.from_dict(g))
	it.word = d.get("w", "")
	return it
