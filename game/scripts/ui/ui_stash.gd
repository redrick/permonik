class_name UiStash
extends UiPanel


func _ready() -> void:
	custom_minimum_size = Vector2(644, 0)
	set_title(L.t("stash"))
	body.add_child(UiGrid.make(func(): return Game.ch.stash, "stash"))
