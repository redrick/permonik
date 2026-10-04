extends Node

var world: Node2D
var level: Level
var hud: Hud
var ui: UiRoot
var fade: ColorRect
var overlay: CanvasLayer
var loading := false


func _ready() -> void:
	Game.main = self
	world = Node2D.new()
	add_child(world)
	hud = Hud.new()
	add_child(hud)
	hud.visible = false
	ui = UiRoot.new()
	add_child(ui)
	overlay = CanvasLayer.new()
	overlay.layer = 90
	add_child(overlay)
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 1)
	fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	overlay.add_child(fade)
	var cur := DB.tex("ui/cursor")
	if cur:
		Input.set_custom_mouse_cursor(cur, Input.CURSOR_ARROW, Vector2(0, 0))
	var args := OS.get_cmdline_user_args()
	if args.has("--shot"):
		add_child(load("res://scripts/debug/shot.gd").new())
	if args.has("--quick"):
		Game.new_game(_arg(args, "--class", "havir"), "Hrdina", false)
		Game.flags["intro_seen"] = true
		var a := int(_arg(args, "--act", "1"))
		Game.act = a
		start_game(int(_arg(args, "--floor", "0")))
		if args.has("--probe"):
			add_child(load("res://scripts/debug/probe.gd").new())
		if args.has("--autoplay"):
			add_child(load("res://scripts/debug/autoplay.gd").new())
		return
	show_menu()


func _arg(args: PackedStringArray, k: String, d: String) -> String:
	var i := args.find(k)
	return args[i + 1] if i >= 0 and i + 1 < args.size() else d


func show_menu() -> void:
	_clear_world()
	hud.visible = false
	Sfx.music("menu")
	ui.show_main_menu()
	_fade_in()


func start_game(f := 0) -> void:
	ui.close_all()
	hud.visible = true
	if Game.act == 1 and f == 0 and Game.quests.is_empty() and Game.difficulty == 0 and not Game.flags.get("intro_seen", false):
		Game.flags["intro_seen"] = true
		_fade_in()
		play_slides("intro", func(): Game.goto(1, 0, "start"))
		return
	Game.goto(Game.act, f, "start")


func _clear_world() -> void:
	for c in world.get_children():
		c.queue_free()
	level = null
	Game.level = null
	Game.player = null


func load_location(a: int, f: int, arrive: String) -> void:
	if loading:
		return
	loading = true
	ui.close_all()
	await _fade_out()
	_clear_world()
	await get_tree().process_frame
	level = Level.new()
	world.add_child(level)
	level.build(a, f, arrive)
	Game.level = level
	hud.visible = true
	hud.on_location(a, f)
	if f == 0:
		Game.ch.hp = Game.ch.d.hp_max if Game.ch.hp <= 0 else Game.ch.hp
	Game.save()
	loading = false
	_fade_in()


func _fade_out() -> void:
	fade.mouse_filter = Control.MOUSE_FILTER_STOP
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 1.0, 0.35)
	await tw.finished


func _fade_in() -> void:
	var tw := create_tween()
	tw.tween_property(fade, "color:a", 0.0, 0.5)
	tw.tween_callback(func(): fade.mouse_filter = Control.MOUSE_FILTER_IGNORE)


var slide_queue: Array = []
var slides_playing := false


func play_slides(seq: String, done: Callable = Callable()) -> void:
	slide_queue.append([seq, done])
	if not slides_playing:
		_next_slides()


func _next_slides() -> void:
	if slide_queue.is_empty():
		slides_playing = false
		return
	slides_playing = true
	var e: Array = slide_queue.pop_front()
	var items: Array = DB.slides.get(e[0], [])
	var done: Callable = e[1]
	var after := func():
		if done.is_valid():
			done.call()
		_next_slides()
	if items.is_empty():
		after.call()
	else:
		ui.play_slides(items, after)


func show_credits() -> void:
	ui.show_credits(func(): show_menu())


func open_npc(npc: Npc) -> void:
	ui.open_npc(npc)


func open_waypoints() -> void:
	ui.open_waypoints()


func open_stash() -> void:
	ui.open_stash()


func start_identify_cursor() -> void:
	ui.start_identify()


func boss_line(who: String, text: String, portrait: String, dur := 4.5) -> void:
	hud.boss_line(who, text, portrait, dur)


func mouse_over_ui() -> bool:
	return ui.mouse_over_ui() or hud.mouse_over_ui()


func on_player_died() -> void:
	Game.boss_bar.emit("", 0.0, false)
	await get_tree().create_timer(1.6).timeout
	ui.show_death()


func respawn() -> void:
	var lost := int(Game.ch.gold * 0.1)
	Game.ch.gold -= lost
	Game.ch.hp = Game.ch.d.hp_max
	Game.ch.mana = Game.ch.d.mana_max
	Game.portal = {}
	Game.goto(Game.act, 0, "start")


func save_and_menu() -> void:
	Game.save()
	get_tree().paused = false
	Game.paused_ui = false
	show_menu()
