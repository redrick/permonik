class_name UiCredits
extends Control

var done: Callable
var roll: VBoxContainer
var tw: Tween
var ended := false

const LINES := [
	["h", {"cs": "Permoník", "en": "Permoník"}],
	["s", {"cs": "Desátek z hlubin", "en": "The Tithe of the Deep"}],
	["gap"],
	["k", {"cs": "Příběh a návrh", "en": "Story & design"}],
	["v", {"cs": "Andrej Antas a celá rodina", "en": "Andrej Antas and the whole family"}],
	["gap"],
	["k", {"cs": "Kresby", "en": "Art"}],
	["v", {"cs": "Rodinná tužka a pastelky, po vzoru Velké a malé detektivky", "en": "The family's pencil and crayons, in the style of the Big & Small Detective comics"}],
	["gap"],
	["k", {"cs": "Písmo", "en": "Lettering"}],
	["v", {"cs": "Tátova ruka", "en": "Dad's own handwriting"}],
	["gap"],
	["k", {"cs": "Hudba a zvuky", "en": "Music & sound"}],
	["v", {"cs": "Vyčarováno z čísel", "en": "Conjured out of numbers"}],
	["gap"],
	["k", {"cs": "Pověsti a prameny", "en": "Folklore & sources"}],
	["v", {"cs": "Karel Jaromír Erben, Kytice a Prostonárodní české písně a říkadla", "en": "Karel Jaromír Erben, A Bouquet and Czech folk songs and rhymes"}],
	["v", {"cs": "Alois Jirásek, Staré pověsti české", "en": "Alois Jirásek, Old Czech Legends"}],
	["v", {"cs": "Božena Němcová, Národní báchorky a pověsti", "en": "Božena Němcová, Folk Tales and Legends"}],
	["v", {"cs": "Havířské pověsti z Kutné Hory, Příbrami a Jáchymova", "en": "Miners' legends of Kutná Hora, Příbram and Jáchymov"}],
	["v", {"cs": "Ius regale montanorum, král Václav II., léta Páně 1300", "en": "Ius regale montanorum, King Wenceslas II, AD 1300"}],
	["gap"],
	["k", {"cs": "Postaveno v", "en": "Built with"}],
	["v", {"cs": "Godot Engine", "en": "Godot Engine"}],
	["gap"],
	["v", {"cs": "Zdař Bůh!", "en": "Zdař Bůh!"}],
]


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	var bg := ColorRect.new()
	bg.color = Color(0.02, 0.018, 0.016, 1)
	bg.set_anchors_preset(Control.PRESET_FULL_RECT)
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(bg)
	UiScreens.vignette(self, Color(0, 0, 0, 0.9), 0.3)
	roll = VBoxContainer.new()
	roll.add_theme_constant_override("separation", 10)
	roll.alignment = BoxContainer.ALIGNMENT_CENTER
	roll.anchor_left = 0.5
	roll.anchor_right = 0.5
	roll.grow_horizontal = Control.GROW_DIRECTION_BOTH
	add_child(roll)
	for ln in LINES:
		match ln[0]:
			"gap":
				roll.add_child(UiTheme.sep(36))
			"h":
				var tt := DB.tex("ui/title")
				if tt:
					var tr := TextureRect.new()
					tr.texture = tt
					tr.custom_minimum_size = Vector2(900, 270)
					tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
					tr.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
					roll.add_child(tr)
				else:
					roll.add_child(_line(L.t(ln[1]), 96, UiTheme.GOLD))
			"s":
				if not DB.tex("ui/title"):
					roll.add_child(_line(L.t(ln[1]), 40, UiTheme.DIM))
			"k":
				roll.add_child(_line(L.t(ln[1]), 26, UiTheme.DIM, true))
			"v":
				roll.add_child(_line(L.t(ln[1]), 38, UiTheme.INK))
	await get_tree().process_frame
	var h := roll.get_combined_minimum_size().y
	roll.offset_top = size.y + 40
	roll.offset_bottom = roll.offset_top + h
	tw = create_tween()
	tw.tween_property(roll, "position:y", -h - 40, (size.y + h) / 70.0)
	tw.tween_callback(_end)


func _line(text: String, sz: int, col: Color, dense := false) -> Label:
	var l := UiTheme.label(text, sz, col, dense)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.custom_minimum_size = Vector2(1400, 0)
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	return l


func _end() -> void:
	if ended:
		return
	ended = true
	if tw:
		tw.kill()
	roll.visible = false
	var vb := UiScreens.center_box(self)
	var t := UiTheme.label(L.t("dlc_soon"), 72, UiTheme.GOLD)
	t.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	t.add_theme_constant_override("outline_size", 10)
	vb.add_child(t)
	vb.add_child(UiTheme.sep(40))
	if Game.unlocked_difficulty > Game.difficulty:
		var nd := L.t("diff_%d" % mini(Game.difficulty + 1, 2))
		var again := func():
			UiRoot.inst.close_all()
			Game.start_next_difficulty()
		var b := UiTheme.button(UiTheme.t("descend_again", {"v": nd}), again, 460)
		b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
		vb.add_child(b)
	var m := UiTheme.button(UiTheme.t("back_to_menu"), _to_menu, 460)
	m.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	vb.add_child(m)
	vb.modulate.a = 0.0
	create_tween().tween_property(vb, "modulate:a", 1.0, 1.5)


func _to_menu() -> void:
	var d := done
	UiRoot.inst.close_all()
	if d.is_valid():
		d.call()


func on_escape() -> void:
	_end()


func _gui_input(event: InputEvent) -> void:
	if not ended and event is InputEventMouseButton and event.pressed:
		accept_event()
		_end()
