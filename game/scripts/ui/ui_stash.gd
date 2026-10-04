class_name UiStash
extends UiPanel

# Two chests: the hero's own and the one every hero shares.

var shared := false
var grid_holder: VBoxContainer
var tabs: HBoxContainer


func _ready() -> void:
	custom_minimum_size = Vector2(760, 0)
	set_title(L.t("stash"))
	tabs = HBoxContainer.new()
	tabs.add_theme_constant_override("separation", 10)
	body.add_child(tabs)
	grid_holder = VBoxContainer.new()
	body.add_child(grid_holder)
	_build()


func box() -> Inventory:
	return Game.shared_stash if shared else Game.ch.stash


func _build() -> void:
	for c in tabs.get_children():
		c.queue_free()
	for c in grid_holder.get_children():
		c.queue_free()
	var own := UiTheme.button(L.t({"cs": "Moje truhla", "en": "My chest"}), func(): _switch(false), 220, 22)
	var common := UiTheme.button(L.t({"cs": "Společná truhla", "en": "Shared chest"}), func(): _switch(true), 240, 22)
	own.disabled = not shared
	common.disabled = shared
	tabs.add_child(own)
	tabs.add_child(common)
	grid_holder.add_child(UiGrid.make(func(): return box(), "stash"))
	var b := UiTheme.button(L.t("inv_sort"), func(): box().arrange(), 170, 22)
	b.size_flags_horizontal = Control.SIZE_SHRINK_END
	grid_holder.add_child(b)


func _switch(to_shared: bool) -> void:
	shared = to_shared
	_build()


func _exit_tree() -> void:
	Game.save_shared_stash()
