class_name UiItemCard
extends PanelContainer

# Touch builds: a tapped item is not picked up but shown here, with what wearing it would change, the piece
# worn now, and one big button per thing that can be done with it. Nothing happens without a button.

const W := 540.0

var item: Item
var src: Control
var show_worn := false
var docked := false
var _sig := ""
var _box: VBoxContainer


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	add_theme_stylebox_override("panel", UiTheme.flat(Color(0.03, 0.025, 0.03, 0.97), UiTheme.GOLD.darkened(0.35), 3, 14))
	_box = VBoxContainer.new()
	_box.add_theme_constant_override("separation", 8)
	add_child(_box)


func show_item(it: Item, s: Control) -> void:
	item = it
	src = s
	show_worn = false
	_sig = ""


func _w() -> float:
	return UiPhoneBook.DETAIL_W if docked else W


func _process(_d: float) -> void:
	if docked and item == null:
		if _sig != "-":
			_sig = "-"
			_build_empty()
		return
	if not _valid():
		UiRoot.inst.close_card()
		return
	var sig := "%s|%s|%d|%s|%s" % [item.tooltip(Game.ch), _actions().map(func(a): return a[0] + str(a[2])), Game.ch.gold, show_worn, UiRoot.inst.left]
	if sig != _sig:
		_sig = sig
		_build()


func _valid() -> bool:
	if item == null or not is_instance_valid(src) or not src.is_visible_in_tree() or UiRoot.inst.held:
		return false
	if src is UiGrid:
		return (src as UiGrid).inv().items.has(item)
	if src is UiEquip:
		return (src as UiEquip)._item() == item
	if src is SlotView:
		return Game.ch.belt[(src as SlotView).index] == item
	return false


func _worn() -> Item:
	if src is UiEquip or not item.is_equipment():
		return null
	for sl in Game.ch.slot_for(item):
		var e: Item = Game.ch.equip.get(sl, null)
		if e and e != item:
			return e
	return null


func _clear() -> void:
	for c in _box.get_children():
		_box.remove_child(c)
		c.queue_free()
	custom_minimum_size = Vector2(_w(), 0)


func _build_empty() -> void:
	_clear()
	var l := UiTheme.label(UiTheme.t("card_none"), 22, UiTheme.FAINT, true)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(_w() - 40, 0)
	_box.add_child(l)


func _build() -> void:
	_clear()
	var head := HBoxContainer.new()
	_box.add_child(head)
	var lines: Array = item.tooltip(Game.ch)
	var title_l := UiTheme.label(str(lines[0][0]), 30, lines[0][1] if lines[0].size() > 1 else UiTheme.INK)
	title_l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title_l.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	head.add_child(title_l)
	if not docked:
		head.add_child(UiTheme.small_button("×", func(): UiRoot.inst.close_card(), 52))
	var scroll := ScrollContainer.new()
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL if docked else Control.SIZE_FILL
	_box.add_child(scroll)
	var text := VBoxContainer.new()
	text.add_theme_constant_override("separation", 2)
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(text)
	for ln in lines.slice(1):
		_line(text, str(ln[0]), ln[1] if ln.size() > 1 else UiTheme.INK)
	for ln in _notes():
		_line(text, ln[0], ln[1])
	if src is UiGrid and (src as UiGrid).mode == "inv" and not is_nan(Game.ch.upgrade_score(item)):
		var dl := Game.ch.delta_lines(item)
		if not dl.is_empty():
			_line(text, L.t({"cs": "Když si to nasadíš:", "en": "If you wear it:"}), UiTheme.FAINT)
			for x in dl:
				_line(text, "  " + x[0], Color("5fd068") if x[1] else UiTheme.RED)
	var worn := _worn()
	if worn:
		var tg := UiTheme.button(UiTheme.t("card_worn_hide" if show_worn else "card_worn_show"), func(): show_worn = not show_worn, _w() - 40, 22)
		tg.custom_minimum_size.y = 48
		text.add_child(tg)
		if show_worn:
			var wl: Array = worn.tooltip(Game.ch)
			_line(text, str(wl[0][0]), wl[0][1] if wl[0].size() > 1 else UiTheme.INK, 25)
			for ln in wl.slice(1):
				_line(text, str(ln[0]), ln[1] if ln.size() > 1 else UiTheme.INK)
	var flow := HFlowContainer.new()
	flow.add_theme_constant_override("h_separation", 10)
	flow.add_theme_constant_override("v_separation", 10)
	_box.add_child(flow)
	for a in _actions():
		var b := UiTheme.button(a[0], a[1], (_w() - 50) / 2.0, 24)
		b.custom_minimum_size.y = 64
		b.disabled = not a[2]
		flow.add_child(b)
	if not docked:
		_fit(scroll, text)


# The text scrolls when the card would not fit above the HUD bar. Wrapped labels know their height only
# after a layout pass, so the card is measured a frame later.
func _fit(scroll: ScrollContainer, text: Control) -> void:
	modulate.a = 0.0
	scroll.custom_minimum_size.y = 0.0
	size = Vector2(W, 0)
	await get_tree().process_frame
	await get_tree().process_frame
	if not is_instance_valid(scroll):
		return
	var avail := UiRoot.inst.card_height()
	var rest := get_combined_minimum_size().y - scroll.get_combined_minimum_size().y
	scroll.custom_minimum_size.y = clampf(text.size.y, 0.0, maxf(160.0, avail - rest))
	size = Vector2(W, 0)
	modulate.a = 1.0
	UiRoot.inst.place_card()

func _line(parent: Control, txt: String, col: Color, sz := 22) -> void:
	var l := UiTheme.label(txt, sz, col, true)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.custom_minimum_size = Vector2(_w() - 60, 0)
	parent.add_child(l)


func _notes() -> Array:
	var ui := UiRoot.inst
	if src is UiGrid and (src as UiGrid).mode == "inv" and ui.vendor_open():
		var v := ui.vendor_panel()
		if item.sell_price() <= 0:
			return [[UiTheme.t("unsellable"), UiTheme.RED]]
		if not v.accepts(item):
			return [[UiTheme.t("wont_buy"), UiTheme.RED]]
	return []


# [label, action, enabled]
func _actions() -> Array:
	var ui := UiRoot.inst
	var out := []
	if src is UiGrid:
		var g := src as UiGrid
		match g.mode:
			"vendor":
				var v := g.vendor
				var p := v.price_of(item)
				out.append([UiTheme.t("card_buy", {"v": p}), func(): v.buy(item), Game.ch.gold >= p])
				if item.slot() == "consumable" and not v.gamble and Game.ch.belt_free_for(item):
					out.append([UiTheme.t("card_fill_belt"), func(): v.fill_belt(item), Game.ch.gold >= p])
			"inv":
				if ui.vendor_open():
					var v := ui.vendor_panel()
					if v.accepts(item):
						out.append([UiTheme.t("card_sell", {"v": item.sell_price()}), func(): v.sell(item, false), true])
				elif ui.left is UiStash:
					out.append([UiTheme.t("card_to_stash"), func(): g.quick_move(item), true])
				elif ui.left is UiForge or ui.left is UiService:
					out.append([UiTheme.t("card_to_forge"), func(): g.quick_move(item), true])
				if item.is_equipment():
					out.append([UiTheme.t("card_equip"), func(): ui.quick_equip(item), Game.ch.can_equip(item)])
				elif item.slot() == "consumable" and item.base().get("use", {}).size() > 0:
					out.append([UiTheme.t("card_use"), func(): ui.use_or_equip(item), true])
					var u: Dictionary = item.base().get("use", {})
					if u.has("heal_pct") or u.has("mana_pct") or u.has("rejuv"):
						out.append([UiTheme.t("card_to_belt"), func(): ui.to_belt(item), Game.ch.belt_free_for(item)])
				if item.rarity != Item.NORMAL and not item.identified and Game.ch.inv.count("svitek_zjeveni") > 0:
					out.append([UiTheme.t("card_identify"), func(): ui.identify(item), true])
				out.append([UiTheme.t("card_move"), func(): _pick_up(), true])
				if docked and Game.level and Game.player:
					out.append([UiTheme.t("card_drop"), func(): _drop(), true])
			_:
				out.append([UiTheme.t("card_to_bag"), func(): g.quick_move(item), true])
				out.append([UiTheme.t("card_move"), func(): _pick_up(), true])
	elif src is UiEquip:
		var e := src as UiEquip
		out.append([UiTheme.t("card_unequip"), func(): e.unequip(), true])
		out.append([UiTheme.t("card_move"), func(): e.pick_up(), true])
	elif src is SlotView:
		var i := (src as SlotView).index
		out.append([UiTheme.t("card_use"), func(): Game.player.use_belt(i), Game.player != null])
		out.append([UiTheme.t("card_to_bag"), func():
			if Game.ch.inv.add(item):
				Game.ch.belt[i] = null
				ui.changed(), true])
		out.append([UiTheme.t("card_move"), func():
			Game.ch.belt[i] = null
			ui.held = item
			ui.changed(), true])
	return out


func _drop() -> void:
	(src as UiGrid).inv().remove(item)
	Game.level.drop_item(item, Game.player.global_position)
	Sfx.play("drop_item", 0.5)
	UiRoot.inst.changed()


func _pick_up() -> void:
	var g := src as UiGrid
	g.inv().remove(item)
	UiRoot.inst.held = item
	Sfx.play("pickup", 0.5)
	UiRoot.inst.changed()
