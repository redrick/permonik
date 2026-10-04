class_name UiForge
extends UiPanel

# The smith's forge: a small box to lay things in, the strike button, and the recipes he knows.

var box := Inventory.new(4, 3)
var note: Label


func _ready() -> void:
	custom_minimum_size = Vector2(644, 0)
	set_title(L.t({"cs": "Výheň", "en": "The Forge"}))
	body.add_child(UiGrid.make(func(): return box, "forge"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	body.add_child(row)
	row.add_child(UiTheme.button(L.t({"cs": "Kovat", "en": "Strike"}), _strike, 220, 26))
	note = UiTheme.label("", 22, UiTheme.DIM)
	row.add_child(note)
	body.add_child(UiTheme.sep(8))
	body.add_child(UiTheme.label(L.t({"cs": "Co kovář umí:", "en": "What the smith knows:"}), 22, UiTheme.GOLD))
	for r in Forge.RECIPES:
		body.add_child(UiTheme.wrap_label("· " + L.t(r), 18, UiTheme.INK, 600))


func _strike() -> void:
	var msg := Forge.craft(box, Game.ch.level)
	note.text = msg
	Sfx.play("hit_metal", 0.8)
	UiRoot.inst.changed()


# Whatever is left in the forge goes back to the bag (or to the ground, if the bag is full).
func _exit_tree() -> void:
	for it in box.items.duplicate():
		box.remove(it)
		it.pos = Vector2i(-1, -1)
		if not Game.ch.inv.add(it) and Game.level and Game.player:
			Game.level.drop_item(it, Game.player.global_position)
