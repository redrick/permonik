extends Node

var _cache := {}
var _pool: Array[AudioStreamPlayer] = []
var _music_a: AudioStreamPlayer
var _music_b: AudioStreamPlayer
var _music_id := ""
var volume := 0.8
var music_volume := 0.6
var voice_volume := 0.9
# "" speaks the language of the text, "cs"/"en" always that one, "off" nothing
var voice_lang := ""
var _last := {}
var _voice: AudioStreamPlayer
var _read_queue: Array = []


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
	_voice = AudioStreamPlayer.new()
	add_child(_voice)
	_voice.finished.connect(_voice_done)
	var cfg := ConfigFile.new()
	if cfg.load("user://settings.cfg") == OK:
		volume = cfg.get_value("main", "volume", 0.8)
		music_volume = cfg.get_value("main", "music_volume", 0.6)
		voice_volume = cfg.get_value("main", "voice_volume", 0.9)
		voice_lang = str(cfg.get_value("main", "voice_lang", ""))


func save_settings() -> void:
	var cfg := ConfigFile.new()
	cfg.load("user://settings.cfg")
	cfg.set_value("main", "volume", volume)
	cfg.set_value("main", "music_volume", music_volume)
	cfg.set_value("main", "voice_volume", voice_volume)
	cfg.set_value("main", "voice_lang", voice_lang)
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


# ---------------------------------------------------------------- voice
# Lines spoken by generated voices (tools/voice_build.py): one file per speaker and exact line text,
# named by the same sha1 the tool uses, so a line without a file simply stays silent.
func voice_stream(speaker: String, text) -> AudioStream:
	if voice_lang == "off" or speaker == "":
		return null
	var lang := voice_lang if voice_lang != "" else L.lang
	var line := str(text.get(lang, "")) if text is Dictionary else (str(text) if lang == L.lang else "")
	if line.strip_edges() == "":
		return null
	var k := (speaker + "|" + line).sha1_text().left(16)
	return _stream("res://assets/voice/%s/%s/%s.ogg" % [lang, speaker, k])


# Plays the line (cutting off any line still speaking) and returns its length, 0 when there is none.
func voice(speaker: String, text) -> float:
	_read_queue = []
	return _play_voice(speaker, text)


func _play_voice(speaker: String, text) -> float:
	var st := voice_stream(speaker, text)
	_voice.stop()
	if st == null:
		_unduck()
		return 0.0
	_voice.stream = st
	_voice.volume_db = linear_to_db(maxf(voice_volume, 0.001))
	_voice.play()
	var cur := _music_a if _music_a.playing else _music_b
	create_tween().tween_property(cur, "volume_db", linear_to_db(maxf(music_volume * 0.45, 0.001)), 0.3)
	return st.get_length()


# A short cry over the fight, spoken only when no other line is speaking. Returns the text to show.
func cry(speaker: String, text: Dictionary) -> String:
	if not _voice.playing:
		voice(speaker, text)
	return L.t(text)


func stop_voice() -> void:
	_read_queue = []
	_voice.stop()
	_unduck()


# Book pages and Kronika entries, read one text after another by the reader's voice. False when none of
# them has a recording.
func read_aloud(texts: Array) -> bool:
	var q := texts.filter(func(t): return voice_stream("reader", t) != null)
	if q.is_empty():
		return false
	voice("reader", q.pop_front())
	_read_queue = q
	return true


func can_read_aloud(texts: Array) -> bool:
	return texts.any(func(t): return voice_stream("reader", t) != null)


func _voice_done() -> void:
	if _read_queue.is_empty():
		_unduck()
	else:
		_play_voice("reader", _read_queue.pop_front())


func voice_playing() -> bool:
	return _voice.playing


func _unduck() -> void:
	var cur := _music_a if _music_a.playing else _music_b
	if cur.playing:
		create_tween().tween_property(cur, "volume_db", linear_to_db(maxf(music_volume, 0.001)), 0.6)
