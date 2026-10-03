class_name Inventory
extends RefCounted

signal changed

var w := 10
var h := 4
var items: Array = []


func _init(cols := 10, rows := 4) -> void:
	w = cols
	h = rows


func item_at(cell: Vector2i) -> Item:
	for it in items:
		var s: Vector2i = it.size()
		if cell.x >= it.pos.x and cell.x < it.pos.x + s.x and cell.y >= it.pos.y and cell.y < it.pos.y + s.y:
			return it
	return null


func fits(it: Item, at: Vector2i, ignore: Item = null) -> bool:
	var s := it.size()
	if at.x < 0 or at.y < 0 or at.x + s.x > w or at.y + s.y > h:
		return false
	for o in items:
		if o == ignore or o == it:
			continue
		var os: Vector2i = o.size()
		if at.x < o.pos.x + os.x and at.x + s.x > o.pos.x and at.y < o.pos.y + os.y and at.y + s.y > o.pos.y:
			return false
	return true


func blockers(it: Item, at: Vector2i) -> Array:
	var out := []
	var s := it.size()
	for o in items:
		if o == it:
			continue
		var os: Vector2i = o.size()
		if at.x < o.pos.x + os.x and at.x + s.x > o.pos.x and at.y < o.pos.y + os.y and at.y + s.y > o.pos.y:
			out.append(o)
	return out


func find_space(it: Item) -> Vector2i:
	for x in w:
		for y in h:
			if fits(it, Vector2i(x, y)):
				return Vector2i(x, y)
	return Vector2i(-1, -1)


func add(it: Item) -> bool:
	if it.is_stackable() and it.slot() != "gold":
		for o in items:
			if o.base_id == it.base_id and o.qty < int(o.base().get("max_stack", 1)):
				o.qty += it.qty
				changed.emit()
				return true
	var p := find_space(it)
	if p.x < 0:
		return false
	it.pos = p
	items.append(it)
	changed.emit()
	return true


func place(it: Item, at: Vector2i) -> bool:
	if not fits(it, at):
		return false
	it.pos = at
	if not items.has(it):
		items.append(it)
	changed.emit()
	return true


func remove(it: Item) -> void:
	items.erase(it)
	changed.emit()


func count(base_id: String) -> int:
	var n := 0
	for it in items:
		if it.base_id == base_id:
			n += it.qty
	return n


func take(base_id: String, n := 1) -> bool:
	for it in items.duplicate():
		if it.base_id == base_id and n > 0:
			var k := mini(n, it.qty)
			it.qty -= k
			n -= k
			if it.qty <= 0:
				items.erase(it)
	changed.emit()
	return n == 0


func to_array() -> Array:
	return items.map(func(i): return i.to_dict())


func load_array(arr: Array) -> void:
	items.clear()
	for d in arr:
		items.append(Item.from_dict(d))
	changed.emit()
