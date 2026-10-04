extends Node

var args := OS.get_cmdline_user_args()


func _arg(k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	await get_tree().create_timer(float(_arg("--wait", "3"))).timeout
	for p in _arg("--panel", "").split(",", false):
		Game.main.ui.toggle_panel(p)
	if args.has("--book"):
		Game.main.ui.open_book(_arg("--book", ""))
	if args.has("--hide-hud") and Game.main.hud:
		Game.main.hud.visible = false
	await get_tree().create_timer(0.6).timeout
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_jpg(_arg("--shot", "user://shot.jpg"), 0.88)
	get_tree().quit()
