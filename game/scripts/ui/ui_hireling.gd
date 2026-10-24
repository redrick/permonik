class_name UiHireling
extends UiPanel

const DOLL := {
	"head": [Vector2(224, 0), Vector2i(2, 2)],
	"weapon": [Vector2(60, 40), Vector2i(2, 3)],
	"body": [Vector2(224, 126), Vector2i(2, 3)],
}

var at_inn := false
var name_lbl: Label
var stats_lbl: Label
var doll: Control
var offers: VBoxContainer
var shown := ""


func _ready() -> void:
	custom_minimum_size = Vector2(600, 0)
	set_title(L.t({"cs": "Pomocník", "en": "Hireling"}))
	name_lbl = UiTheme.title("", 34)
	body.add_child(name_lbl)
	doll = Control.new()
	doll.custom_minimum_size = Vector2(560, 300)
	doll.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(doll)
	for sl in DOLL:
		var e := UiEquip.make(sl, DOLL[sl][0], DOLL[sl][1])
		e.merc = true
		doll.add_child(e)
	stats_lbl = UiTheme.label("", 21, UiTheme.DIM, true)
	stats_lbl.position = Vector2(380, 20)
	doll.add_child(stats_lbl)
	offers = VBoxContainer.new()
	offers.add_theme_constant_override("separation", 8)
	body.add_child(offers)
	refresh()


func refresh() -> void:
	var m: Dictionary = Game.ch.merc
	var hired := not m.is_empty()
	var key := "%s|%s|%d|%d" % [str(m.get("type", "")), str(m.get("dead", false)), Game.ch.gold, Game.ch.level]
	doll.visible = hired and not m.get("dead", false)
	if hired:
		var d: Dictionary = DB.hirelings.get(str(m.type), {})
		name_lbl.text = "%s · %s" % [str(m.get("name", "")), L.t(d.get("name", ""))]
		var s := Hireling.stats(m, Game.ch.level)
		var hp_now := int(s.hp * float(m.get("hp", 1.0)))
		stats_lbl.text = "%s %d\n%s %d / %d\n%s %d\n%s %d–%d\n%s %d" % [L.t("level"), Game.ch.level, L.t({"cs": "Život", "en": "Life"}), hp_now, int(s.hp),
			L.t("armor"), int(s.armor), L.t("damage"), int(s.dmg.x), int(s.dmg.y), L.t({"cs": "Útok", "en": "Attack"}), int(s.to_hit)]
	else:
		name_lbl.text = L.t({"cs": "Nikoho nemáš najatého", "en": "Nobody is hired"})
	if key == shown:
		return
	shown = key
	for c in offers.get_children():
		offers.remove_child(c)
		c.queue_free()
	if not at_inn:
		if hired and not m.get("dead", false):
			offers.add_child(UiTheme.wrap_label(L.t({"cs": "Výstroj mu dáš přetažením předmětu do políček.", "en": "Drag items onto the slots to equip them."}), 19, UiTheme.DIM, 540))
		else:
			offers.add_child(UiTheme.wrap_label(L.t({"cs": "Pomocníka najmeš v krčmě.", "en": "Hire a companion at the inn."}), 20, UiTheme.DIM, 540))
		return
	if hired and m.get("dead", false):
		var rc := Hireling.cost(str(m.type), Game.ch.level) / 2
		offers.add_child(UiTheme.button(L.t({"cs": "Oživit %s (%d grošů)", "en": "Revive %s (%d groats)"}) % [str(m.name), rc], func(): _revive(rc), 520, 22))
	offers.add_child(UiTheme.rule(540))
	for t in DB.hirelings:
		var d: Dictionary = DB.hirelings[t]
		var c := Hireling.cost(t, Game.ch.level)
		offers.add_child(UiTheme.label(L.t(d.get("name", t)), 26, UiTheme.GOLD))
		offers.add_child(UiTheme.wrap_label(L.t(d.get("desc", "")), 19, UiTheme.INK, 540))
		var b := UiTheme.button(L.t({"cs": "Najmout (%d grošů)", "en": "Hire (%d groats)"}) % c, func(): _hire(t, c), 340, 22)
		b.disabled = Game.ch.gold < c
		offers.add_child(b)


func _hire(t: String, c: int) -> void:
	if Game.ch.gold < c:
		return
	_return_gear()
	Game.ch.gold -= c
	var names: Array = DB.hirelings[t].get("names", ["?"])
	Game.ch.merc = {"type": t, "name": str(names.pick_random()), "dead": false, "hp": 1.0, "equip": {}}
	Sfx.play("gold")
	_respawn()


func _revive(c: int) -> void:
	if Game.ch.gold < c:
		Game.msg(L.t({"cs": "Nemáš dost grošů.", "en": "Not enough groats."}), UiTheme.DIM)
		return
	Game.ch.gold -= c
	Game.ch.merc.dead = false
	Game.ch.merc.hp = 1.0
	Sfx.play("heal")
	_respawn()


# The old hireling's gear comes back to the hero instead of vanishing with them.
func _return_gear() -> void:
	var eq: Dictionary = Game.ch.merc.get("equip", {})
	for sl in eq:
		var it: Item = eq[sl]
		if it and not Game.ch.inv.add(it):
			Game.ch.stash.add(it)
	if not eq.is_empty():
		Game.msg(L.t({"cs": "Výstroj bývalého pomocníka máš v batohu.", "en": "Your former hireling's gear is in your pack."}), UiTheme.DIM)


func _respawn() -> void:
	shown = ""
	if Game.level:
		Game.level.spawn_hireling()
	UiRoot.inst.changed()
	Game.save()
	refresh()
