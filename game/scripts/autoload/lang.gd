extends Node

signal changed

const LANGS := ["cs", "en"]
var lang := "cs"
var ui := {}


func _ready() -> void:
	ui = _load("res://data/ui.json")
	var cfg := ConfigFile.new()
	if cfg.load("user://settings.cfg") == OK:
		lang = cfg.get_value("main", "lang", "cs")


func _load(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var d = JSON.parse_string(FileAccess.get_file_as_string(path))
	return d if d is Dictionary else {}


func set_lang(l: String) -> void:
	lang = l
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	cfg.set_value("main", "lang", l)
	cfg.save("user://settings.cfg")
	changed.emit()


func t(x, args := {}) -> String:
	var s := ""
	if x is Dictionary:
		s = str(x.get(lang, x.get("cs", x.get("en", ""))))
	elif x is String:
		if ui.has(x):
			s = str(ui[x].get(lang, ui[x].get("cs", x)))
		else:
			s = FALLBACK.get(x, {}).get(lang, x) if FALLBACK.has(x) else x
	else:
		s = str(x)
	for k in args:
		s = s.replace("{" + str(k) + "}", str(args[k]))
	return s


func gendered(x, gender: String) -> String:
	if x is Dictionary and x.has(lang):
		var v = x[lang]
		if v is Dictionary:
			return str(v.get(gender, v.get("m", "")))
		return str(v)
	return t(x)


const FALLBACK := {
	"menu_new_game": {"cs": "Nová hra", "en": "New game"},
	"menu_continue": {"cs": "Pokračovat", "en": "Continue"},
	"menu_options": {"cs": "Nastavení", "en": "Options"},
	"menu_quit": {"cs": "Konec", "en": "Quit"},
	"menu_back": {"cs": "Zpět", "en": "Back"},
	"menu_start": {"cs": "Sestoupit", "en": "Descend"},
	"menu_language": {"cs": "Jazyk", "en": "Language"},
	"menu_volume": {"cs": "Hlasitost", "en": "Volume"},
	"menu_difficulty": {"cs": "Obtížnost", "en": "Difficulty"},
	"menu_name": {"cs": "Jméno", "en": "Name"},
	"diff_0": {"cs": "Normal", "en": "Normal"},
	"diff_1": {"cs": "Noční můra", "en": "Nightmare"},
	"diff_2": {"cs": "Nav", "en": "Nav"},
	"stat_sila": {"cs": "Síla", "en": "Strength"},
	"stat_obratnost": {"cs": "Obratnost", "en": "Dexterity"},
	"stat_magie": {"cs": "Magie", "en": "Magic"},
	"stat_vitalita": {"cs": "Vitalita", "en": "Vitality"},
	"hp": {"cs": "Život", "en": "Life"},
	"mana": {"cs": "Mana", "en": "Mana"},
	"armor": {"cs": "Zbroj", "en": "Armour"},
	"to_hit": {"cs": "Útok", "en": "Attack rating"},
	"damage": {"cs": "Poškození", "en": "Damage"},
	"level": {"cs": "Úroveň", "en": "Level"},
	"xp": {"cs": "Zkušenost", "en": "Experience"},
	"next_level": {"cs": "Další úroveň", "en": "Next level"},
	"free_points": {"cs": "Volné body", "en": "Free points"},
	"skill_points": {"cs": "Body dovedností", "en": "Skill points"},
	"res_fire": {"cs": "Odolnost: oheň", "en": "Fire resist"},
	"res_lightning": {"cs": "Odolnost: blesk", "en": "Lightning resist"},
	"res_cold": {"cs": "Odolnost: mráz", "en": "Cold resist"},
	"res_poison": {"cs": "Odolnost: jed", "en": "Poison resist"},
	"gold": {"cs": "groše", "en": "groschen"},
	"inventory": {"cs": "Výbava", "en": "Inventory"},
	"character": {"cs": "Postava", "en": "Character"},
	"skills": {"cs": "Dovednosti", "en": "Skills"},
	"quests": {"cs": "Úkoly", "en": "Quests"},
	"buy": {"cs": "Koupit", "en": "Buy"},
	"sell": {"cs": "Prodat", "en": "Sell"},
	"repair": {"cs": "Opravit vše", "en": "Repair all"},
	"identify": {"cs": "Identifikovat", "en": "Identify"},
	"talk": {"cs": "Mluvit", "en": "Talk"},
	"trade": {"cs": "Obchod", "en": "Trade"},
	"heal_me": {"cs": "Vyléčit", "en": "Heal"},
	"gossip": {"cs": "Novinky", "en": "Gossip"},
	"leave": {"cs": "Odejít", "en": "Leave"},
	"unidentified": {"cs": "Neidentifikováno", "en": "Unidentified"},
	"requirements": {"cs": "Požadavky", "en": "Requirements"},
	"durability": {"cs": "Trvanlivost", "en": "Durability"},
	"waypoint": {"cs": "Těžní klec", "en": "Shaft cage"},
	"town": {"cs": "Město", "en": "Town"},
	"floor": {"cs": "Patro", "en": "Level"},
	"you_died": {"cs": "Hora si tě vzala", "en": "The mountain took you"},
	"respawn": {"cs": "Vrátit se do města", "en": "Return to town"},
	"level_up": {"cs": "Nová úroveň!", "en": "Level up!"},
	"no_mana": {"cs": "Nemám dost many.", "en": "Not enough mana."},
	"inv_full": {"cs": "Nemám místo.", "en": "No room."},
	"cant_use": {"cs": "To nemůžu použít.", "en": "I can't use that."},
	"resume": {"cs": "Pokračovat", "en": "Resume"},
	"save_quit": {"cs": "Uložit a do menu", "en": "Save and exit to menu"},
	"automap": {"cs": "Mapa", "en": "Map"},
	"quest_done": {"cs": "Úkol splněn", "en": "Quest complete"},
	"quest_new": {"cs": "Nový úkol", "en": "New quest"},
	"loading": {"cs": "Sestupuji…", "en": "Descending…"},
	"skip": {"cs": "Pokračuj", "en": "Continue"},
	"speed_fast": {"cs": "Rychlá zbraň", "en": "Fast weapon"},
	"speed_normal": {"cs": "Běžná rychlost", "en": "Normal speed"},
	"speed_slow": {"cs": "Pomalá zbraň", "en": "Slow weapon"},
	"speed_very_slow": {"cs": "Velmi pomalá zbraň", "en": "Very slow weapon"},
	"tt_block": {"cs": "Vykrytí: {v} %", "en": "Block: {v}%"},
	"tt_light": {"cs": "Dosvit: {v}", "en": "Light radius: {v}"},
	"tt_belt": {"cs": "Místa na lahve: +{v}", "en": "Potion slots: +{v}"},
	"req_level": {"cs": "Úroveň", "en": "Level"},
	"req_sila": {"cs": "Síla", "en": "Strength"},
	"req_obratnost": {"cs": "Obratnost", "en": "Dexterity"},
	"req_magie": {"cs": "Magie", "en": "Magic"},
	"slot_weapon": {"cs": "Zbraň", "en": "Weapon"},
	"slot_offhand": {"cs": "Štít", "en": "Off-hand"},
	"slot_head": {"cs": "Hlava", "en": "Head"},
	"slot_body": {"cs": "Tělo", "en": "Body"},
	"slot_belt": {"cs": "Opasek", "en": "Belt"},
	"slot_lamp": {"cs": "Kahan", "en": "Lamp"},
	"slot_ring1": {"cs": "Prsten", "en": "Ring"},
	"slot_ring2": {"cs": "Prsten", "en": "Ring"},
	"slot_amulet": {"cs": "Amulet", "en": "Amulet"},
	"rank": {"cs": "Stupeň", "en": "Rank"},
	"next_rank": {"cs": "Další stupeň", "en": "Next rank"},
	"req_skill_level": {"cs": "Vyžaduje úroveň {v}", "en": "Requires level {v}"},
	"mana_cost": {"cs": "Mana: {v}", "en": "Mana: {v}"},
	"cooldown": {"cs": "Prodleva: {v} s", "en": "Cooldown: {v}s"},
	"passive": {"cs": "Trvalá dovednost", "en": "Passive skill"},
	"rmb_hint": {"cs": "Pravé tlačítko: nastavit na pravou myš · Q/W/E/R: nastavit na klávesu", "en": "Right click: bind to right mouse · Q/W/E/R: bind to key"},
	"identify_cost": {"cs": "Identifikovat ({v} grošů)", "en": "Identify ({v} groschen)"},
	"not_enough_gold": {"cs": "Nemám dost grošů.", "en": "Not enough gold."},
	"shrine_used": {"cs": "Modla mlčí.", "en": "The idol is silent."},
	"locked": {"cs": "Zatím zavřeno.", "en": "Not yet."},
	"town_portal": {"cs": "Brána domů", "en": "Town portal"},
	"dlc_soon": {"cs": "Pokračování příště…", "en": "To be continued…"},
	"act": {"cs": "Dějství", "en": "Act"},
	"press_any": {"cs": "Klikni nebo stiskni mezerník", "en": "Click or press space"},
	"press_any_touch": {"cs": "Klepni pro další", "en": "Tap to continue"},
	"empty_save": {"cs": "Žádná uložená hra", "en": "No saved game"},
	"delete": {"cs": "Smazat", "en": "Delete"},
	"stash": {"cs": "Truhla", "en": "Stash"},
}
