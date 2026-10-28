class_name UiFolderPicker
extends Control

# Android's folder picker hands back content:// URIs that plain file access can't use, and Godot's own
# FileDialog is a separate window the touch layer doesn't reach, so the game browses shared storage itself.

const ROOT := "/storage/emulated/0"

var dir := ROOT
var on_pick: Callable
var _path: Label
var _list: VBoxContainer
var _scroll: ScrollContainer


static func open(start: String, cb: Callable) -> void:
	var p := UiFolderPicker.new()
	p.dir = start if DirAccess.dir_exists_absolute(start) else ROOT
	p.on_pick = cb
	UiRoot.inst.root.add_child(p)


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	z_index = 8
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.7)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", UiTheme.panel_box())
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		panel.set("offset_" + side, (1 if side in ["left", "top"] else -1) * 24.0)
	add_child(panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	panel.add_child(box)
	box.add_child(UiTheme.title(UiTheme.t("save_dir_pick"), 36))
	_path = UiTheme.label("", 24, UiTheme.GOLD, true)
	_path.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	box.add_child(_path)
	_scroll = ScrollContainer.new()
	_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	box.add_child(_scroll)
	_list = VBoxContainer.new()
	_list.add_theme_constant_override("separation", 6)
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_scroll.add_child(_list)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_child(row)
	row.add_child(UiTheme.button(L.t({"cs": "Vybrat tuto složku", "en": "Use this folder"}), func():
		var d := dir
		queue_free()
		on_pick.call(d), 380, 28))
	row.add_child(UiTheme.button(L.t({"cs": "Zrušit", "en": "Cancel"}), queue_free, 220, 28))
	_fill()


func _fill() -> void:
	for c in _list.get_children():
		_list.remove_child(c)
		c.queue_free()
	_path.text = dir
	if dir != ROOT and dir.get_base_dir() != "":
		_list.add_child(_row("‹ " + L.t({"cs": "o složku výš", "en": "up one folder"}), dir.get_base_dir()))
	var subs := Array(DirAccess.get_directories_at(dir)).filter(func(d: String): return not d.begins_with("."))
	subs.sort_custom(func(a: String, b: String): return a.naturalnocasecmp_to(b) < 0)
	for d in subs:
		_list.add_child(_row("▸ " + d, dir.path_join(d)))
	if subs.is_empty():
		_list.add_child(UiTheme.label(L.t({"cs": "Žádné další složky.", "en": "No folders inside."}), 24, UiTheme.FAINT))
	_scroll.scroll_vertical = 0


func _row(text: String, to: String) -> Button:
	var b := UiTheme.button(text, func():
		dir = to
		_fill(), 0, 28)
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.custom_minimum_size.y = 72
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return b
