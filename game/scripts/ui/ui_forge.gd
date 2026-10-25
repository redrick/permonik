class_name UiForge
extends UiPanel

# The smith's forge: a small box to lay things in, the strike button, and the recipes he knows.

static var show_recipes := false

var box := Inventory.new(4, 3)
var note: Label
var recipes: ScrollContainer
var toggle: Button


func _ready() -> void:
	custom_minimum_size = Vector2(644, 0)
	set_title(L.t({"cs": "Výheň", "en": "The Forge"}))
	body.add_child(UiGrid.make(func(): return box, "forge"))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	body.add_child(row)
	row.add_child(UiTheme.button(L.t({"cs": "Kovat", "en": "Strike"}), _strike, 200, 26))
	toggle = UiTheme.button("", _toggle_recipes, 200, 24)
	row.add_child(toggle)
	note = UiTheme.label("", 22, UiTheme.DIM)
	row.add_child(note)
	recipes = ScrollContainer.new()
	recipes.custom_minimum_size = Vector2(0, 500)
	recipes.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	body.add_child(recipes)
	var list := VBoxContainer.new()
	list.add_theme_constant_override("separation", 6)
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	recipes.add_child(list)
	var specs := _recipe_specs()
	for i in Forge.RECIPES.size():
		list.add_child(_card(specs[i], L.t(Forge.RECIPES[i])))
	_sync_toggle()


func _toggle_recipes() -> void:
	show_recipes = not show_recipes
	_sync_toggle()


func _sync_toggle() -> void:
	recipes.visible = show_recipes
	toggle.text = L.t({"cs": "Recepty ▴", "en": "Recipes ▴"}) if show_recipes else L.t({"cs": "Recepty ▾", "en": "Recipes ▾"})


func _strike() -> void:
	var msg := Forge.craft(box, Game.ch.level)
	note.text = msg
	Sfx.play("hit_metal", 0.8)
	UiRoot.inst.changed()


# Whatever is left in the forge goes back to the bag (or to the ground, if the bag is full).
func _exit_tree() -> void:
	for it in box.items.duplicate():
		box.remove(it)
		it.pos = Vector2i(-1, -1)
		if not Game.ch.inv.add(it) and Game.level and Game.player:
			Game.level.drop_item(it, Game.player.global_position)


func _card(formulas: Array, caption: String) -> Control:
	var card := PanelContainer.new()
	card.add_theme_stylebox_override("panel", UiTheme.flat(Color(0.08, 0.06, 0.05, 0.85), Color(UiTheme.BRONZE, 0.6), 1, 8))
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 4)
	card.add_child(v)
	for f in formulas:
		var h := HBoxContainer.new()
		h.add_theme_constant_override("separation", 6)
		v.add_child(h)
		var ins: Array = f[0]
		for k in ins.size():
			if k > 0:
				h.add_child(_glyph("+"))
			h.add_child(RecipeIcon.make(ins[k]))
		h.add_child(_glyph("→"))
		for o in f[1]:
			h.add_child(RecipeIcon.make(o))
	v.add_child(UiTheme.wrap_label(caption, 17, UiTheme.DIM, 560))
	return card


func _glyph(s: String) -> Label:
	var l := UiTheme.label(s, 26, UiTheme.GOLD)
	l.custom_minimum_size = Vector2(18, 52)
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return l


# One entry per Forge.RECIPES line: a list of [ingredients, results], each an icon spec.
func _recipe_specs() -> Array:
	var lad := Forge._letters_sorted()
	var any_plain := _gen("stit", Item.NORMAL, {"cs": "Jakýkoli obyčejný předmět bez zásuvek", "en": "Any plain item without sockets"})
	var socketed := _gen("stit", Item.NORMAL, {"cs": "Předmět, v jehož zásuvkách něco je", "en": "An item with something set in its sockets"}, 2, ["granat_2"])
	return [
		[[[_ex("granat_1", 3, {"cs": "Tři stejné drahokamy stejného stupně", "en": "Three gems of the same kind and grade"})], [_ex("granat_2")]]],
		[[[_ex(lad[0], 3)], [_ex(lad[1])]],
			[[_ex(lad[10], 2), _ex("granat_3", 1, {"cs": "Jakýkoli broušený drahokam (3. stupeň a výš)", "en": "Any cut gem (grade 3 or better)"})], [_ex(lad[11])]]],
		[[[any_plain, _ex("granat_1", 3, {"cs": "Tři úlomky drahokamů (1. stupeň)", "en": "Three chipped gems (grade 1)"})],
			[_gen("stit", Item.NORMAL, {"cs": "Týž předmět, teď se zásuvkami", "en": "The same item, now with sockets"}, 2)]]],
		[[[socketed, _ex("kapradi_kvet")],
			[_gen("stit", Item.NORMAL, {"cs": "Prázdný předmět…", "en": "The emptied item…"}, 2), _gen("granat_2", Item.NORMAL, {"cs": "…a vše, co v něm bylo", "en": "…and everything that was in it"})]]],
		[[[_gen("krumpac", Item.MAGIC, {"cs": "Jakýkoli kouzelný (modrý) předmět", "en": "Any magic (blue) item"}),
			_ex("ametyst_3", 3, {"cs": "Tři broušené drahokamy (3. stupeň a výš)", "en": "Three cut gems (grade 3 or better)"})],
			[_gen("krumpac", Item.MAGIC, {"cs": "Týž předmět s novým kouzlem", "en": "The same item with a new enchantment"})]]],
		[[[_gen("krumpac", Item.RARE, {"cs": "Jakýkoli vzácný (žlutý) předmět", "en": "Any rare (yellow) item"}),
			_ex("vltavin_4", 4, {"cs": "Čtyři dokonalé drahokamy (4. stupeň)", "en": "Four perfect gems (grade 4)"})],
			[_gen("krumpac", Item.RARE, {"cs": "Týž předmět s novými vlastnostmi", "en": "The same item with new properties"})]]],
		_craft_rows(),
		[[[_gen("krumpac", Item.NORMAL, {"cs": "Jakýkoli předmět", "en": "Any item"}), _ex("glag_r"),
			_ex("granat_2", 1, {"cs": "Drahokam 2. stupně a výš", "en": "A gem of grade 2 or better"})],
			[_gen("krumpac_kovany", Item.NORMAL, {"cs": "Kovaná verze, vše na ní zůstane", "en": "Its forged version, keeping all it carries"})]]],
		[[[_ex("ziva_voda", 3)], [_ex("ziva_voda_velka")]],
			[[_ex("svatojanska_rosa", 3)], [_ex("svatojanska_rosa_velka")]],
			[[_ex("ziva_voda_velka", 2), _ex("svatojanska_rosa_velka")], [_ex("kapradi_kvet")]]],
		[[[_ex("pecet_vody"), _ex("pecet_kamene"), _ex("pecet_ohne"), _ex("pecet_smrti")],
			[_unique("permonikuv_desatek")]]],
	]


func _craft_rows() -> Array:
	var rows := []
	var letter_note := {"cs": "Zbraň: Slovo · zbroj a štít: Našь · prsten, amulet, opasek, kahan: Dobro", "en": "Weapon: Slovo · armour and shield: Našь · ring, amulet, belt, lamp: Dobro"}
	for stone in Forge.CRAFTS:
		var cf: Dictionary = Forge.CRAFTS[stone]
		var res := _gen("krumpac", Item.CRAFTED, cf.name)
		res.lines[0][1] = Item.COL_CRAFTED
		for m in cf.mods:
			res.lines.append(["%s  [%d–%d]" % [Item.mod_text(m.stat, m.max), int(m.min), int(m.max)], Item.COL_MAGIC])
		res.lines.append([L.t({"cs": "+ 1 až 4 náhodné vlastnosti", "en": "+ 1 to 4 random properties"}), Item.COL_INFO])
		rows.append([[_gen("krumpac", Item.MAGIC, {"cs": "Jakýkoli kouzelný (modrý) předmět", "en": "Any magic (blue) item"}),
			_ex("glag_s", 1, letter_note), _ex(stone + "_3", 1, {"cs": "Broušený drahokam (3. stupeň a výš)", "en": "A cut gem (grade 3 or better)"})], [res]])
	return rows


func _ex(id: String, n := 1, note_text = null) -> Dictionary:
	var it := Item.create(id, 1)
	var lines := it.tooltip(Game.ch)
	if note_text != null:
		lines.insert(1, [L.t(note_text), UiTheme.GOLD])
	return {"item": it, "n": n, "lines": lines}


func _gen(id: String, rarity: int, text: Dictionary, sockets := 0, socketed: Array = []) -> Dictionary:
	var it := Item.create(id, 1)
	it.rarity = rarity
	it.sockets = sockets
	for g in socketed:
		it.socketed.append(Item.create(g, 1))
	return {"item": it, "n": 1, "lines": [[L.t(text), UiTheme.INK]]}


func _unique(uid: String) -> Dictionary:
	var u: Dictionary = DB.uniques.get(uid, {})
	var it := Item.create(str(u.get("base", "")), 1)
	it.unique_id = uid
	it.rarity = Item.UNIQUE
	return {"item": it, "n": 1, "lines": [[L.t(u.get("name", uid)), Item.COL_UNIQUE], ["?", Item.COL_INFO]]}


class RecipeIcon extends Control:
	const SZ := 52.0
	var spec: Dictionary

	static func make(s: Dictionary) -> RecipeIcon:
		var r := RecipeIcon.new()
		r.spec = s
		return r

	func _ready() -> void:
		custom_minimum_size = Vector2(SZ, SZ)
		mouse_filter = Control.MOUSE_FILTER_STOP
		mouse_entered.connect(queue_redraw)
		mouse_exited.connect(queue_redraw)
		UiRoot.inst.reg_tip(self)

	func _draw() -> void:
		var r := Rect2(Vector2.ZERO, size)
		UiTheme.draw_cell(self, r, r.has_point(get_local_mouse_position()))
		UiTheme.draw_item(self, spec.item, r.grow(-3))
		if spec.get("dim", false):
			draw_rect(r.grow(-3), Color(0.03, 0.025, 0.02, 0.72))
		var n := int(spec.n)
		if n > 1:
			var s := "×%d" % n
			var p := Vector2(size.x - 26, size.y - 5)
			draw_string_outline(UiTheme.small, p, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, 4, Color.BLACK)
			draw_string(UiTheme.small, p, s, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, UiTheme.GOLD)

	# Scrolled out of view it is still "visible", so check the scroll's clip ourselves.
	func tip() -> Dictionary:
		var mp := get_global_mouse_position()
		var p := get_parent()
		while p:
			if p is ScrollContainer and not (p as Control).get_global_rect().has_point(mp):
				return {}
			p = p.get_parent()
		return {"lines": spec.lines}
