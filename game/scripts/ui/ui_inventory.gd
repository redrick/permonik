class_name UiInventory
extends UiPanel

const DOLL := {
	"head": [Vector2(224, 0), Vector2i(2, 2)],
	"lamp": [Vector2(118, 28), Vector2i(1, 1)],
	"amulet": [Vector2(386, 28), Vector2i(1, 1)],
	"weapon": [Vector2(28, 76), Vector2i(2, 3)],
	"body": [Vector2(224, 126), Vector2i(2, 3)],
	"offhand": [Vector2(420, 76), Vector2i(2, 3)],
	"ring1": [Vector2(56, 262), Vector2i(1, 1)],
	"ring2": [Vector2(448, 262), Vector2i(1, 1)],
	"belt": [Vector2(224, 304), Vector2i(2, 1)],
}
const DOLL_PHONE := {
	"head": [Vector2(134, 0), Vector2i(2, 2)],
	"lamp": [Vector2(40, 28), Vector2i(1, 1)],
	"amulet": [Vector2(284, 28), Vector2i(1, 1)],
	"weapon": [Vector2(0, 124), Vector2i(2, 3)],
	"body": [Vector2(134, 124), Vector2i(2, 3)],
	"offhand": [Vector2(268, 124), Vector2i(2, 3)],
	"ring1": [Vector2(28, 304), Vector2i(1, 1)],
	"ring2": [Vector2(296, 304), Vector2i(1, 1)],
	"belt": [Vector2(134, 304), Vector2i(2, 1)],
}

var gold_lbl: Label
var stats_lbl: Label


# On a phone a narrower doll stands beside the bag instead of above it, and is left out next to a shop or chest.
func _ready() -> void:
	set_title(L.t("inventory"))
	var ui := UiRoot.inst
	var compact := ui.compact()
	var layout: Dictionary = DOLL_PHONE if compact else DOLL
	var main: BoxContainer = HBoxContainer.new() if compact else VBoxContainer.new()
	main.add_theme_constant_override("separation", 18 if compact else 6)
	body.add_child(main)
	var doll := Control.new()
	doll.custom_minimum_size = Vector2(380, 360) if compact else Vector2(560, 370)
	doll.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var art := DB.tex("portraits/hero_" + Game.ch.class_id)
	if art:
		var tr := TextureRect.new()
		tr.texture = art
		tr.position = Vector2(80, 40) if compact else Vector2(170, 40)
		tr.size = Vector2(220, 220)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.modulate = Color(1, 1, 1, 0.13)
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		doll.add_child(tr)
	for sl in layout:
		doll.add_child(UiEquip.make(sl, layout[sl][0], layout[sl][1]))
	stats_lbl = UiTheme.label("", 19, UiTheme.DIM, true)
	if not compact:
		stats_lbl.position = Vector2(0, 336)
		doll.add_child(stats_lbl)
	if not (compact and ui.book and ui.book.trade()):
		main.add_child(doll)
		if not compact:
			main.add_child(UiTheme.sep(4))
	var bag := VBoxContainer.new()
	bag.add_theme_constant_override("separation", 6)
	bag.alignment = BoxContainer.ALIGNMENT_END
	main.add_child(bag)
	if compact:
		bag.add_child(stats_lbl)
	bag.add_child(UiGrid.make(func(): return Game.ch.inv, "inv"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	bag.add_child(row)
	var coin := DB.tex("items/grose_hromadka")
	if coin:
		var ct := TextureRect.new()
		ct.texture = coin
		ct.custom_minimum_size = Vector2(34, 34)
		ct.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		ct.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		row.add_child(ct)
	gold_lbl = UiTheme.label("", 26, UiTheme.GOLD)
	gold_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(gold_lbl)
	row.add_child(UiTheme.button(L.t("inv_sort"), func(): Game.ch.inv.arrange(), 170, 22))
	refresh()

func refresh() -> void:
	gold_lbl.text = "%d %s" % [Game.ch.gold, L.t("gold")]
	var d: Dictionary = Game.ch.d
	stats_lbl.text = "%s %d\n%s %d–%d" % [L.t("armor"), int(d.get("armor", 0)), L.t("damage"), int(d.get("dmg_min", 0)), int(d.get("dmg_max", 0))]
