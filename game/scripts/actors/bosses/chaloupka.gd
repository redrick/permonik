extends BossBase

const WOOD := Color("d8b080")

var roam_t := 0.0


func _init_boss() -> void:
	special_t = 3.0
	set_meta("hit_sfx", "hit_stone")


func _fight(p: Actor, d: float, delta: float) -> void:
	if d < 210.0 and special_t <= 0.0:
		special_t = randf_range(3.0, 4.5)
		_kick(p)
		return
	if d < 210.0:
		_chase(p, delta, 0.7)
		return
	roam_t -= delta
	if roam_t <= 0.0 or path.is_empty():
		roam_t = randf_range(2.0, 4.0)
		var q := open_spot_near(p.global_position, 150.0, 300.0)
		set_path_to(q)
	follow_path(delta, speed * speed_mult())
	if int(anim_t * 3.0) % 2 == 0 and moving and randf() < 0.03:
		level.shake(2.0)


func _kick(p: Actor) -> void:
	busy = 1.0
	face_to(p.global_position)
	set_pose("attack", 1.0)
	shout("Kvok!", "Cluck!", WOOD)
	cone(p.global_position - global_position, 190.0, 80.0, 0.9, 1.4, "physical", WOOD, func(a):
		a.knock = (a.global_position - global_position).normalized() * 600.0
		level.shake(8.0))
