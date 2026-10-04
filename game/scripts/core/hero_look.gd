class_name HeroLook
extends RefCounted

# Builds the hero's sprites from layers (art/heroes_gear.py) so the worn gear shows. Layers are stacked
# back to front; a slot with nothing in it uses the class's own `default`, weapons/off-hands/lamps none.

const LAYERS := ["headgear_back", "back", "body_far", "weapon_far", "lamp_far", "hand_far", "offhand", "legs", "body",
	"belt", "lamp", "weapon_belt", "body_near", "weapon", "hand", "head", "headgear"]
const SLOT_OF := {"headgear_back": "head", "body_far": "body", "weapon_far": "weapon", "lamp_far": "lamp", "offhand": "offhand",
	"body": "body", "belt": "belt", "lamp": "lamp", "weapon_belt": "weapon", "body_near": "body", "weapon": "weapon", "headgear": "head"}
const DEFAULTED := ["body", "head", "belt"]
const POSES := ["idle", "walk1", "walk2", "attack", "cast", "hit", "dead"]

static var _cache := {}


# What each visible slot looks like: the base item's icon (uniques and tiers share it). A kytel is
# everyday clothing, so each class wears its own in it.
static func gear_of(ch: CharData) -> Dictionary:
	var eq := {}
	for slot in ch.equip:
		if ch.equip[slot]:
			eq[slot] = {"b": ch.equip[slot].base_id}
	return gear_from_equip(eq)


# Same from a save file's "equip" block, for the hero list.
static func gear_from_equip(eq: Dictionary) -> Dictionary:
	var g := {}
	for slot in ["weapon", "offhand", "head", "body", "belt", "lamp"]:
		if eq.has(slot) and eq[slot] is Dictionary:
			var bd := DB.item(str(eq[slot].get("b", "")))
			var icon := str(bd.get("look", bd.get("icon", "")))
			if icon != "":
				g[slot] = icon
	if g.get("body", "") == "kytel":
		g.erase("body")
	return g


static func key(cls: String, gear: Dictionary, big := false) -> String:
	var parts := [cls, "big" if big else "small"]
	for slot in ["weapon", "offhand", "head", "body", "belt", "lamp"]:
		parts.append(str(gear.get(slot, "")))
	return "|".join(parts)


static func textures(cls: String, gear: Dictionary) -> Dictionary:
	var k := key(cls, gear)
	if _cache.has(k):
		return _cache[k]
	var out := {}
	for pose in POSES:
		var t := _compose("res://assets/sprites/heroes/%s/%s/" % [cls, pose], gear)
		if t:
			out[pose] = t
	if _cache.size() > 6:
		_cache.clear()
	_cache[k] = out
	return out


# The large standing figure for the hero list.
static func portrait(cls: String, gear: Dictionary) -> Texture2D:
	var k := key(cls, gear, true)
	if not _cache.has(k):
		_cache[k] = _compose("res://assets/sprites/heroes_big/%s/idle/" % cls, gear)
	return _cache[k]


static func _compose(dir: String, gear: Dictionary) -> Texture2D:
	var img: Image = null
	for layer in LAYERS:
		var slot: String = SLOT_OF.get(layer, "")
		var file: String = layer
		if slot != "":
			var look := str(gear.get(slot, ""))
			if look == "":
				if slot not in DEFAULTED:
					continue
				look = "default"
			file += "." + look
		var path: String = dir + file + ".png"
		if not ResourceLoader.exists(path):
			continue
		var src: Image = (load(path) as Texture2D).get_image()
		if src.is_compressed():
			src.decompress()
		if src.get_format() != Image.FORMAT_RGBA8:
			src.convert(Image.FORMAT_RGBA8)
		if img == null:
			img = Image.create(src.get_width(), src.get_height(), false, Image.FORMAT_RGBA8)
		img.blend_rect(src, Rect2i(Vector2i.ZERO, src.get_size()), Vector2i.ZERO)
	return ImageTexture.create_from_image(img) if img else null
