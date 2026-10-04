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

var gold_lbl: Label
var stats_lbl: Label


func _ready() -> void:
	set_title(L.t("inventory"))
	var doll := Control.new()
	doll.custom_minimum_size = Vector2(560, 370)
	doll.mouse_filter = Control.MOUSE_FILTER_IGNORE
	body.add_child(doll)
	var art := DB.tex("portraits/hero_" + Game.ch.class_id)
	if art:
		var tr := TextureRect.new()
		tr.texture = art
		tr.position = Vector2(170, 40)
		tr.size = Vector2(220, 220)
		tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tr.modulate = Color(1, 1, 1, 0.13)
		tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
		doll.add_child(tr)
	for sl in DOLL:
		doll.add_child(UiEquip.make(sl, DOLL[sl][0], DOLL[sl][1]))
	stats_lbl = UiTheme.label("", 19, UiTheme.DIM, true)
	stats_lbl.position = Vector2(0, 336)
	doll.add_child(stats_lbl)
	body.add_child(UiTheme.sep(4))
	body.add_child(UiGrid.make(func(): return Game.ch.inv, "inv"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	body.add_child(row)
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
