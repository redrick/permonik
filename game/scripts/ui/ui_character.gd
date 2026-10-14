class_name UiCharacter
extends UiPanel

var name_lbl: Label
var sub_lbl: Label
var xp_lbl: Label
var pts_lbl: Label
var stat_vals := {}
var stat_btns := {}
var stat_grid: GridContainer
var derived := {}

const DERIVED := ["hp", "mana", "armor", "to_hit", "damage", "attack_speed", "block", "res_fire",
	"res_lightning", "res_cold", "res_poison", "light_radius", "magic_find", "gold_find"]


func _ready() -> void:
	custom_minimum_size = Vector2(640, 0)
	set_title(L.t("character"))
	name_lbl = UiTheme.title("", 40)
	body.add_child(name_lbl)
	sub_lbl = UiTheme.label("", 24, UiTheme.DIM)
	sub_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(sub_lbl)
	xp_lbl = UiTheme.label("", 20, UiTheme.DIM, true)
	xp_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(xp_lbl)
	body.add_child(UiTheme.sep(4))
	body.add_child(UiTheme.rule(556))
	var g := GridContainer.new()
	g.columns = 3
	g.add_theme_constant_override("h_separation", 18)
	g.add_theme_constant_override("v_separation", 4)
	g.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	body.add_child(g)
	stat_grid = g
	for s in CharData.BASE_STATS:
		var l := UiTheme.label(L.t("stat_" + s), 28)
		l.custom_minimum_size = Vector2(220, 0)
		g.add_child(l)
		var v := UiTheme.label("", 28, Color.WHITE)
		v.custom_minimum_size = Vector2(90, 0)
		v.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		g.add_child(v)
		stat_vals[s] = v
		var stat: String = s
		var b := UiTheme.small_button("+", func(): Game.ch.spend_stat(stat), 40)
		g.add_child(b)
		stat_btns[s] = b
	pts_lbl = UiTheme.label("", 24, UiTheme.GOLD)
	pts_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	body.add_child(pts_lbl)
	body.add_child(UiTheme.rule(556))
	body.add_child(UiTheme.sep(2))
	var g2 := GridContainer.new()
	g2.columns = 2
	g2.add_theme_constant_override("h_separation", 30)
	g2.add_theme_constant_override("v_separation", 0)
	g2.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	body.add_child(g2)
	for k in DERIVED:
		var l := UiTheme.label(_name(k), 21, UiTheme.DIM, true)
		l.custom_minimum_size = Vector2(300, 0)
		g2.add_child(l)
		var v := UiTheme.label("", 21, UiTheme.INK, true)
		v.custom_minimum_size = Vector2(160, 0)
		v.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		g2.add_child(v)
		derived[k] = v
	body.add_child(UiTheme.sep(4))
	body.add_child(UiTheme.rule(556))
	var foot := UiTheme.label("", 20, UiTheme.FAINT, true)
	foot.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	foot.name = "foot"
	body.add_child(foot)
	refresh()


func _name(k: String) -> String:
	match k:
		"hp":
			return UiTheme.t("life")
		"attack_speed", "block", "light_radius", "magic_find", "gold_find":
			return UiTheme.t(k)
	return L.t(k)


func refresh() -> void:
	var ch := Game.ch
	var d: Dictionary = ch.d
	if d.is_empty():
		return
	name_lbl.text = ch.hero_name
	sub_lbl.text = "%s · %s %d" % [L.t(ch.cls().get("name", ch.class_id)), L.t("level"), ch.level]
	xp_lbl.text = "%s %d · %s %d" % [L.t("xp"), ch.xp, L.t("next_level"), CharData.xp_for(ch.level + 1)]
	for s in CharData.BASE_STATS:
		var v: Label = stat_vals[s]
		var base := int(ch.cls().get("base", {}).get(s, 0)) + int(ch.alloc.get(s, 0))
		var cur := ch.stat(s)
		v.text = str(cur)
		v.add_theme_color_override("font_color", UiTheme.BLUE if cur > base else (UiTheme.RED if cur < base else Color.WHITE))
		stat_btns[s].visible = ch.stat_points > 0
	stat_grid.columns = 3 if ch.stat_points > 0 else 2
	pts_lbl.text = UiTheme.t("stat_points", {"v": ch.stat_points}) if ch.stat_points > 0 else ""
	pts_lbl.visible = ch.stat_points > 0
	var vals := {
		"hp": "%d / %d" % [int(ch.hp), int(d.hp_max)],
		"mana": "%d / %d" % [int(ch.mana), int(d.mana_max)],
		"armor": str(int(d.armor)),
		"to_hit": str(int(d.to_hit)),
		"damage": "%d–%d" % [int(d.dmg_min), int(d.dmg_max)],
		"attack_speed": "%.2f" % float(d.aps),
		"block": "%d %%" % int(d.get("block", 0)),
		"light_radius": UiTheme.fmt_num(float(d.get("light_radius", 0))),
		"magic_find": "%d %%" % int(d.get("magic_find", 0)),
		"gold_find": "%d %%" % int(d.get("gold_find", 0)),
	}
	for e in CharData.ELEMENTS:
		vals["res_" + e] = "%d %%" % int(d.get("res_" + e, 0))
	for k in derived:
		var l: Label = derived[k]
		l.text = vals.get(k, "")
		if k.begins_with("res_"):
			var r := int(d.get(k, 0))
			l.add_theme_color_override("font_color", UiTheme.RED if r < 0 else (UiTheme.GOLD if r >= 75 else UiTheme.INK))
	var foot: Label = body.get_node("foot")
	foot.text = "%s: %s · %s %d · %s %d/4" % [L.t("menu_difficulty"), L.t("diff_%d" % Game.difficulty), L.t("act"), Game.act, UiTheme.t("seals"), Game.seal_count()]
