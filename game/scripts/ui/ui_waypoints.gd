class_name UiWaypoints
extends UiPanel


func _ready() -> void:
	set_title(UiTheme.t("waypoints"))
	var hint := UiTheme.label(UiTheme.t("waypoint_hint"), 22, UiTheme.DIM)
	hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(hint)
	body.add_child(WorldMap.new())
