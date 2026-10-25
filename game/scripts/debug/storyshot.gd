extends Node

# Stages the Story page of the main menu for a --write-movie capture, plays one film from it,
# skips it with Esc and checks the menu is back and the tree is not left paused.


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	UiCinema.mark_seen("intro")
	UiCinema.mark_seen("act1_end")
	await get_tree().create_timer(1.0).timeout
	var menu: UiMenu = UiRoot.inst.screen
	menu._show("story")
	await get_tree().create_timer(2.0).timeout
	UiRoot.inst.play_cinema("act1_end", Callable())
	await get_tree().create_timer(4.0).timeout
	var ev := InputEventKey.new()
	ev.keycode = KEY_ESCAPE
	ev.physical_keycode = KEY_ESCAPE
	ev.pressed = true
	Input.parse_input_event(ev)
	await get_tree().create_timer(1.5).timeout
	print("STORYSHOT slides_gone=", UiRoot.inst.slides == null, " paused=", get_tree().paused, " menu=", UiRoot.inst.screen is UiMenu)
	get_tree().quit()
