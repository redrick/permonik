class_name UiVendor
extends UiPanel

var npc: Npc
var gamble := false
var peddler := false
var stock_inv := Inventory.new(10, 10)
var gold_lbl: Label
var repair_btn: Button
var _sig := -1


func _ready() -> void:
	custom_minimum_size = Vector2(644, 0)
	if peddler:
		var pi := Game.peddler_item()
		npc.stock = [pi] if pi else []
	elif npc.stock.is_empty():
		npc.stock = Loot.vendor_stock(npc.role(), Game.ch.level)
	if gamble and npc.gamble_stock.is_empty():
		npc.gamble_stock = Loot.gamble_stock(Game.ch.level)
	set_title(npc.display_name + ("  ·  " + L.t({"cs": "Kostky", "en": "Dice"}) if gamble else ""))
	_rebuild()
	var g := UiGrid.make(func(): return stock_inv, "vendor")
	g.vendor = self
	body.add_child(g)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	body.add_child(row)
	gold_lbl = UiTheme.label("", 26, UiTheme.GOLD)
	gold_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(gold_lbl)
	if npc.role() == "smith":
		repair_btn = UiTheme.button("", _repair, 300, 22)
		row.add_child(repair_btn)
	body.add_child(UiTheme.wrap_label(UiTheme.t("vendor_hint_touch" if TouchPad.active else "vendor_hint"), 18, UiTheme.FAINT, 556))
	refresh()


func _rebuild() -> void:
	stock_inv.items.clear()
	var seen := {}
	for it: Item in (npc.gamble_stock if gamble else npc.stock):
		if it.slot() == "consumable":
			if seen.has(it.base_id):
				continue
			seen[it.base_id] = true
		var p := stock_inv.find_space(it)
		if p.x >= 0:
			it.pos = p
			stock_inv.items.append(it)
	_sig = (npc.gamble_stock if gamble else npc.stock).size()


func refresh() -> void:
	if _sig != (npc.gamble_stock if gamble else npc.stock).size():
		_rebuild()
	gold_lbl.text = "%d %s" % [Game.ch.gold, L.t("gold")]
	if repair_btn:
		var c := _repair_cost()
		repair_btn.text = UiTheme.t("repair_cost", {"v": c}) if c > 0 else L.t("repair")
		repair_btn.disabled = c <= 0


func price_of(it: Item) -> int:
	if gamble:
		return Loot.gamble_price(it, Game.ch.level)
	if peddler:
		return maxi(1, int(it.price() * 3.0 * (1.0 + 0.5 * Game.difficulty)))
	return maxi(1, int(it.price() * (1.0 + 0.5 * Game.difficulty)))


func accepts(it: Item) -> bool:
	if peddler or it.sell_price() <= 0:
		return false
	var s := it.slot()
	match npc.role():
		"smith":
			return s in ["weapon", "offhand", "head", "body", "belt"]
		"healer":
			return s == "consumable"
		"inn":
			return s in ["consumable", "ring", "amulet", "lamp", "belt"]
	return false


func buy(it: Item) -> void:
	var p := price_of(it)
	var ch := Game.ch
	if ch.gold < p:
		Game.msg(L.t("not_enough_gold"), UiTheme.DIM)
		return
	var ok := false
	if gamble:
		var won := Loot.gamble(it.base_id, Game.ch.level)
		ok = ch.inv.add(won)
		if ok:
			var i := npc.gamble_stock.find(it)
			var fresh := Loot.gamble_stock(Game.ch.level)
			npc.gamble_stock[i] = fresh[randi() % fresh.size()]
			Game.msg(won.display_name(), won.color())
	elif it.slot() == "consumable":
		ok = ch.pickup(Item.create(it.base_id, it.ilvl))
	else:
		ok = ch.inv.add(it)
		if ok:
			npc.stock.erase(it)
			if peddler:
				Game.flags.peddler.erase("item")
	if not ok:
		Game.msg(L.t("inv_full"), UiTheme.DIM)
		return
	ch.gold -= p
	Sfx.play("gold", 0.7)
	_rebuild()
	UiRoot.inst.changed()


# Shift-click on a potion: buy until the belt slots that take it are full (D2's shift-buy).
func fill_belt(it: Item) -> void:
	var ch := Game.ch
	var p := price_of(it)
	var n := 0
	while ch.gold >= p and n < 16 and ch.belt_free_for(it):
		if not ch.pickup(Item.create(it.base_id, it.ilvl)):
			break
		ch.gold -= p
		n += 1
	if n == 0:
		buy(it)
		return
	Sfx.play("gold", 0.7)
	_rebuild()
	UiRoot.inst.changed()


func sell(it: Item, from_held: bool) -> void:
	if not from_held and not Game.ch.inv.items.has(it):
		return
	if not accepts(it):
		Game.msg(UiTheme.t("unsellable") if it.sell_price() <= 0 else UiTheme.t("wont_buy"), UiTheme.DIM)
		return
	var sp := it.sell_price()
	if from_held:
		UiRoot.inst.held = null
	else:
		Game.ch.inv.remove(it)
	Game.ch.gold += sp
	if it.slot() != "consumable":
		npc.stock.append(it)
	Game.msg(UiTheme.t("sold", {"v": sp}), UiTheme.GOLD)
	Sfx.play("gold", 0.7)
	_rebuild()
	UiRoot.inst.changed()


func _repair_items() -> Array:
	var out := []
	for sl in Game.ch.equip:
		if Game.ch.equip[sl]:
			out.append(Game.ch.equip[sl])
	out.append_array(Game.ch.inv.items)
	return out


func _repair_cost() -> int:
	var c := 0
	for it: Item in _repair_items():
		c += it.repair_cost()
	return c


func _repair() -> void:
	var c := _repair_cost()
	if c <= 0:
		Game.msg(UiTheme.t("nothing_to_repair"), UiTheme.DIM)
		return
	if Game.ch.gold < c:
		Game.msg(L.t("not_enough_gold"), UiTheme.DIM)
		return
	Game.ch.gold -= c
	for it: Item in _repair_items():
		if not it.eth:
			it.dur = it.max_dur
	Sfx.play("hit_metal", 0.6)
	Game.msg(UiTheme.t("repaired"), UiTheme.GOLD)
	UiRoot.inst.changed()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT and UiRoot.inst.held:
		accept_event()
		sell(UiRoot.inst.held, true)
