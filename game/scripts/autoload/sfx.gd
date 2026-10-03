extends Node

var _cache := {}
var _pool: Array[AudioStreamPlayer] = []
var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _music_id := ""
var volume := 0.8
var music_volume := 0.6
var _last := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 16:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_pool.append(p)
	_music_a = AudioStreamPlayer.new()
	_music_b = AudioStreamPlayer.new()
	add_child(_music_a)
	add_child(_music_b)
	var cfg := ConfigFile.new()
	if cfg.load("user://settings.cfg") == OK:
		volume = cfg.get_value("main", "volume", 0.8)
		music_volume = cfg.get_value("main", "music_volume", 0.6)


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	cfg.set_value("main", "volume", volume)
	cfg.set_value("main", "music_volume", music_volume)
	cfg.save("user://settings.cfg")
	var cur := _music_a if _music_a.playing else _music_b
	cur.volume_db = linear_to_db(maxf(music_volume, 0.001))


func _stream(path: String) -> AudioStream:
	if _cache.has(path):
		return _cache[path]
	var s: AudioStream = null
	if ResourceLoader.exists(path):
		s = load(path)
	elif FileAccess.file_exists(path):
		s = AudioStreamOggVorbis.load_from_file(path)
	_cache[path] = s
	return s


func play(id: String, vol := 1.0, pitch_var := 0.08) -> void:
	var now := Time.get_ticks_msec()
	if now - int(_last.get(id, 0)) < 45:
		return
	_last[id] = now
	var s := _stream("res://assets/audio/sfx/%s.ogg" % id)
	if s == null:
		return
	for p in _pool:
		if not p.playing:
			p.stream = s
			p.volume_db = linear_to_db(maxf(volume * vol, 0.001))
			p.pitch_scale = 1.0 + randf_range(-pitch_var, pitch_var)
			p.play()
			return


func play_at(id: String, pos: Vector2, vol := 1.0) -> void:
	var cam := get_viewport().get_camera_2d()
	if cam:
		var d := cam.get_screen_center_position().distance_to(pos)
		vol *= clampf(1.0 - d / 1400.0, 0.0, 1.0)
		if vol < 0.05:
			return
	play(id, vol)


func music(id: String) -> void:
	if id == _music_id:
		return
	_music_id = id
	var s := _stream("res://assets/audio/music/%s.ogg" % id)
	var old := _music_a if _music_a.playing else _music_b
	var nu := _music_b if old == _music_a else _music_a
	if old.playing:
		var tw := create_tween()
		tw.tween_property(old, "volume_db", -60.0, 1.5)
		tw.tween_callback(old.stop)
	if s:
		if s is AudioStreamOggVorbis:
			s.loop = true
		nu.stream = s
		nu.volume_db = -60.0
		nu.play()
		create_tween().tween_property(nu, "volume_db", linear_to_db(maxf(music_volume, 0.001)), 1.5)
