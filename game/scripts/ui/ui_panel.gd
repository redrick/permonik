class_name UiPanel
extends PanelContainer

var body: VBoxContainer
var head: Label
var refresh_t := 0.0


func _init() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	body = VBoxContainer.new()
	body.add_theme_constant_override("separation", 6)
	add_child(body)


func set_title(text: String) -> void:
	var top := Control.new()
	top.custom_minimum_size = Vector2(0, 44)
	body.add_child(top)
	head = UiTheme.title(text)
	head.set_anchors_preset(Control.PRESET_FULL_RECT)
	top.add_child(head)
	var x := UiTheme.small_button("×", func(): UiRoot.inst.close_panel(self), 34)
	x.set_anchors_preset(Control.PRESET_TOP_RIGHT)
	x.position = Vector2(-34, 2)
	x.tooltip_text = UiTheme.t("close")
	top.add_child(x)


func _process(delta: float) -> void:
	refresh_t -= delta
	if refresh_t <= 0.0:
		refresh_t = 0.15
		refresh()


func refresh() -> void:
	pass


func tip() -> Dictionary:
	return {}
