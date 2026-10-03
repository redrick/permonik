extends Monster

var master: Monster
var holding := false
var spot := Vector2.ZERO


func _ai(delta: float) -> void:
	cd = maxf(0.0, cd - delta)
	if master == null or not is_instance_valid(master) or master.dead:
		super._ai(delta)
		return
	if not can_act():
		velocity = Vector2.ZERO
		moving = false
		return
	aggro = true
	if holding:
		velocity = Vector2.ZERO
		moving = false
		face_to(master.global_position)
		if pose_t <= 0.0:
			set_pose("attack", 0.6)
		return
	var tgt := master.global_position + spot
	if global_position.distance_to(tgt) < 24.0:
		holding = true
		level.float_text(top_pos(), L.t({"cs": "Zvedáme víčka!", "en": "Lifting the eyelids!"}), Color("d8c8a0"))
		return
	repath_t -= delta
	if repath_t <= 0.0 or path.is_empty():
		repath_t = 0.5
		set_path_to(tgt)
	follow_path(delta, speed * 1.2 * speed_mult())
