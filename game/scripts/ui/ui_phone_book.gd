class_name UiPhoneBook
extends Control

# Phones: panels open full screen, one page at a time, with the pages listed down the left edge. Wherever the
# bag shows, the tapped item's details stay in a fixed column on the right instead of a card over the grid.

const RAIL_W := 150.0
const DETAIL_W := 380.0
const PAGES := ["inventory", "character", "skills", "quests", "kronika", "hireling", "automap"]

var rail: VBoxContainer
var rail_bg: PanelContainer
var close_x: Button
var area: Control
var content: HBoxContainer
var detail: UiItemCard
var _rail_sig := ""


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := Panel.new()
	bg.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.045, 0.037, 0.035, 1.0), UiTheme.BRONZE.darkened(0.3), 0, 0))
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	row.add_theme_constant_override("separation", 0)
	add_child(row)
	rail_bg = PanelContainer.new()
	rail_bg.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.075, 0.06, 0.05, 1.0), UiTheme.BRONZE.darkened(0.2), 0, 6))
	rail_bg.custom_minimum_size = Vector2(RAIL_W, 0)
	row.add_child(rail_bg)
	rail = VBoxContainer.new()
	rail.add_theme_constant_override("separation", 4)
	rail_bg.add_child(rail)
	area = Control.new()
	area.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	area.clip_contents = true
	area.resized.connect(fit)
	row.add_child(area)
	content = HBoxContainer.new()
	content.add_theme_constant_override("separation", 14)
	content.resized.connect(fit)
	area.add_child(content)
	detail = UiItemCard.new()
	detail.docked = true
	content.add_child(detail)
	close_x = UiTheme.small_button("×", func(): UiRoot.inst.phone_page("close"), 64)
	close_x.custom_minimum_size.y = 64
	close_x.add_theme_font_size_override("font_size", 40)
	close_x.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	close_x.position = Vector2(-70, 6)
	add_child(close_x)


func add_panel(c: Control, where: String) -> void:
	content.add_child(c)
	content.move_child(c, 0 if where == "left" else maxi(0, detail.get_index()))
	_sort()
	c.minimum_size_changed.connect(fit)


func _sort() -> void:
	var ui := UiRoot.inst
	if ui.left and ui.left.get_parent() == content:
		content.move_child(ui.left, 0)
	detail.visible = ui.right != null
	content.move_child(detail, -1)
	fit.call_deferred()


func page() -> String:
	var ui := UiRoot.inst
	if ui.left:
		return str(ui.left.get_meta("kind", "trade"))
	return "inventory" if ui.right else ""


func trade() -> bool:
	return page() == "trade"


func fit() -> void:
	if not is_instance_valid(content) or area.size.x <= 0.0:
		return
	var want := content.get_combined_minimum_size()
	content.size = want
	var room := 80.0 if close_x.visible else 16.0
	var k := minf(1.35, minf((area.size.x - room) / maxf(1.0, want.x), (area.size.y - 12.0) / maxf(1.0, want.y)))
	content.scale = Vector2(k, k)
	content.position = (Vector2(area.size.x - room + 16.0 - want.x * k, area.size.y - want.y * k) / 2.0).floor()


func _process(_d: float) -> void:
	var ui := UiRoot.inst
	if ui.left == null and ui.right == null:
		ui.close_book()
		return
	var sig := page() + str(not Game.ch.merc.is_empty()) + str(Game.ch.stat_points > 0) + str(Game.ch.skill_points > 0)
	if sig != _rail_sig:
		_rail_sig = sig
		_build_rail()


func _build_rail() -> void:
	for c in rail.get_children():
		rail.remove_child(c)
		c.queue_free()
	var cur := page()
	rail_bg.visible = cur != "trade"
	close_x.visible = cur == "trade"
	if cur != "trade":
		for p in PAGES:
			if p == "hireling" and Game.ch.merc.is_empty():
				continue
			var txt := L.t({"cs": "Pomocník", "en": "Hireling"}) if p == "hireling" else L.t(p)
			if (p == "character" and Game.ch.stat_points > 0) or (p == "skills" and Game.ch.skill_points > 0):
				txt += " +"
			rail.add_child(_tab(txt, p, p == cur))
	var gap := Control.new()
	gap.size_flags_vertical = Control.SIZE_EXPAND_FILL
	rail.add_child(gap)
	rail.add_child(_tab(L.t({"cs": "Nabídka", "en": "Menu"}), "pause", false))
	rail.add_child(_tab("× " + UiTheme.t("close"), "close", false))
	fit.call_deferred()


func _tab(txt: String, what: String, on: bool) -> Button:
	var b := UiTheme.small_button(txt, func(): UiRoot.inst.phone_page(what), RAIL_W - 12)
	b.custom_minimum_size.y = 64
	b.clip_text = true
	b.add_theme_font_size_override("font_size", 25)
	b.add_theme_color_override("font_color", UiTheme.GOLD if on else UiTheme.INK)
	var bg := Color(0.24, 0.17, 0.09) if on else Color(0.11, 0.085, 0.065)
	b.add_theme_stylebox_override("normal", UiTheme.flat(bg, UiTheme.GOLD if on else UiTheme.BRONZE.darkened(0.3), 2, 4))
	return b
