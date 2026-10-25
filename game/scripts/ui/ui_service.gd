class_name UiService
extends UiPanel

# A favour done on one item: the smith's imbue, sockets or engraving (earned by quests),
# or the herb woman's charm-speaking that changes one property for gold ("reroll").

const REROLL := {"name": {"cs": "Zaříkat", "en": "Charm-speak"},
	"hint": {"cs": "Polož sem kouzelnou, vzácnou nebo kovanou věc a vyber jednu vlastnost. Zaříkám ji na jinou. Pak už půjde měnit jen ta jedna.", "en": "Lay a magic, rare or crafted item here and pick one property. I'll speak it into another. After that, only that one can change."}}

var kind := ""
var box := Inventory.new(4, 4)
var note: Label
var go: Button
var choices: VBoxContainer
var _sig := ""


func _ready() -> void:
	custom_minimum_size = Vector2(644, 0)
	var sv: Dictionary = REROLL if kind == "reroll" else Forge.SERVICES.get(kind, {})
	set_title(L.t(sv.get("name", kind)))
	body.add_child(UiTheme.wrap_label(L.t(sv.get("hint", "")), 20, UiTheme.DIM, 600))
	body.add_child(UiGrid.make(func(): return box, "forge"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	body.add_child(row)
	if kind != "reroll":
		go = UiTheme.button(L.t(sv.get("name", kind)), _do, 260, 26)
		row.add_child(go)
	note = UiTheme.label("", 22, UiTheme.DIM)
	row.add_child(note)
	choices = VBoxContainer.new()
	choices.add_theme_constant_override("separation", 4)
	body.add_child(choices)


func _item() -> Item:
	return box.items[0] if box.items.size() == 1 else null


func refresh() -> void:
	if kind == "reroll":
		_refresh_reroll()
		return
	if box.items.size() > 1:
		note.text = L.t({"cs": "Jen jednu věc.", "en": "One item only."})
	else:
		note.text = Forge.service_check(kind, _item())
	go.disabled = box.items.size() != 1 or Forge.service_check(kind, _item()) != ""


func _do() -> void:
	var it := _item()
	if Forge.service_check(kind, it) != "" or not Game.flags.get(Forge.service_flag(kind), false):
		return
	var out := Forge.service_do(kind, it, Game.ch)
	Game.flags.erase(Forge.service_flag(kind))
	box.items.clear()
	out.pos = Vector2i(-1, -1)
	box.add(out)
	Game.note_found(out)
	Sfx.play("hit_metal", 0.8)
	Game.msg(out.display_name(), out.color())
	UiRoot.inst.changed()
	Game.save()
	UiRoot.inst.close_panel(self)


static func reroll_check(it: Item) -> String:
	if it == null:
		return L.t({"cs": "Nejdřív sem něco polož.", "en": "Lay something here first."})
	if not it.identified:
		return L.t({"cs": "Nejdřív ho nech zjevit.", "en": "Have it identified first."})
	if it.affix_slots().is_empty():
		return L.t({"cs": "Na tom není co zaříkat.", "en": "There is nothing on it to charm."})
	return ""


func _refresh_reroll() -> void:
	var it := _item()
	var why := L.t({"cs": "Jen jednu věc.", "en": "One item only."}) if box.items.size() > 1 else reroll_check(it)
	var sig := "%s|%s|%d" % [why, str(it.to_dict()) if it else "", Game.ch.gold]
	if sig == _sig:
		return
	_sig = sig
	for c in choices.get_children():
		choices.remove_child(c)
		c.queue_free()
	note.text = why
	if why != "":
		return
	var cost := Loot.reroll_cost(it)
	note.text = L.t({"cs": "Cena: %d grošů", "en": "Cost: %d gold"}) % cost
	var slots := it.affix_slots()
	for i in slots.size():
		var sl: Dictionary = slots[i]
		var txt := ", ".join(it.mods.slice(sl.start, sl.start + sl.count).map(func(m): return Item.mod_text(m.stat, m.value)))
		var idx := i
		var b := UiTheme.button(txt, func(): _reroll(idx), 600, 22)
		b.disabled = (it.locked >= 0 and it.locked != i) or Game.ch.gold < cost
		if it.locked == i:
			b.text = "★ " + txt
		choices.add_child(b)


func _reroll(idx: int) -> void:
	var it := _item()
	if it == null or reroll_check(it) != "":
		return
	var cost := Loot.reroll_cost(it)
	if Game.ch.gold < cost:
		Game.msg(L.t("not_enough_gold"), UiTheme.DIM)
		return
	if not Loot.reroll_affix(it, idx):
		Game.msg(L.t({"cs": "Zaříkání nechytlo.", "en": "The charm didn't take."}), UiTheme.DIM)
		return
	Game.ch.gold -= cost
	Sfx.play("buff", 0.6)
	Game.msg(it.display_name(), it.color())
	UiRoot.inst.changed()


func _exit_tree() -> void:
	for it in box.items.duplicate():
		box.remove(it)
		it.pos = Vector2i(-1, -1)
		if not Game.ch.inv.add(it) and Game.level and Game.player:
			Game.level.drop_item(it, Game.player.global_position)
