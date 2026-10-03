extends Monster

var run_t := 0.0
var rest_t := 0.0
var jink := 1.0


func _ai(delta: float) -> void:
	if not can_act():
		velocity = Vector2.ZERO
		moving = false
		return
	var p := player()
	if p == null or Game.paused_ui:
		velocity = Vector2.ZERO
		moving = false
		return
	aggro = true
	if rest_t > 0.0:
		rest_t -= delta
		velocity = Vector2.ZERO
		moving = false
		return
	var d := dist_to_player()
	if d > 520.0:
		velocity = Vector2.ZERO
		moving = false
		return
	run_t += delta
	if run_t > 2.4:
		run_t = 0.0
		rest_t = 0.9
		jink = -jink
		level.float_text(top_pos(), "…", Color("d8d0b8"))
		return
	var away := (global_position - p.global_position).normalized().rotated(0.5 * jink * sin(anim_t * 4.0))
	var tgt := global_position + away * 80.0
	if level.is_solid(tgt):
		away = away.rotated(PI * 0.5 * jink)
		tgt = global_position + away * 80.0
		if level.is_solid(tgt):
			jink = -jink
			tgt = global_position - away * 80.0
	path = [tgt]
	follow_path(delta, speed * speed_mult())


func _on_damaged(_amount: float, _elem: String, _source: Node) -> void:
	rest_t = 0.0
	run_t = 0.0
