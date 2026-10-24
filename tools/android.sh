#!/usr/bin/env bash
# Build Permoník for Android and drive it on a device that other apps are developed on too.
#
#   tools/android.sh build            export build/permonik.apk (release; signed with ~/.config/permonik/release.env
#                                     when present, else with the debug keystore)
#   tools/android.sh install          install it (only cz.antas.permonik, data kept)
#   tools/android.sh run [args]       start it (stops the old instance first); args reach the game as user args
#   tools/android.sh stop             stop it
#   tools/android.sh log              follow our app's logcat lines only
#   tools/android.sh shot <file.png>  screenshot, only while Permoník is on screen
#   tools/android.sh tap <x> <y>      tap in device pixels, only while Permoník is on screen
#   tools/android.sh swipe <x1> <y1> <x2> <y2> [ms]   same rule
#   tools/android.sh back             Android back button, same rule
#   tools/android.sh deploy           build + install + run
#
# Shared-device rules: every adb call names the device (-s), never touches another package, never
# restarts the adb server or clears logcat, and screen input/screenshots happen only while our app is
# in front. Device steps hold the lock $LOCK, which other projects' scripts should take as well.
set -euo pipefail

PKG=cz.antas.permonik
ROOT=$(cd "$(dirname "$0")/.." && pwd)
GODOT=${GODOT:-$HOME/apps/godot-4.6/Godot_v4.6.3-stable_linux.x86_64}
APK=$ROOT/build/permonik.apk
RELEASE_ENV=${RELEASE_ENV:-$HOME/.config/permonik/release.env}
ARGS_FILE=/storage/emulated/0/Android/data/$PKG/files/dev/args.txt

serial() {
	if [[ -n ${ANDROID_SERIAL:-} ]]; then echo "$ANDROID_SERIAL"; return; fi
	local devs
	devs=$(adb devices | awk 'NR > 1 && $2 == "device" {print $1}')
	if [[ $(wc -w <<<"$devs") -ne 1 ]]; then
		echo "need exactly one device or ANDROID_SERIAL (found: ${devs:-none})" >&2
		exit 1
	fi
	echo "$devs"
}

device_cmd() {
	local s
	s=$(serial)
	LOCK=${XDG_RUNTIME_DIR:-/tmp}/adb-device-$s.lock
	exec 9>"$LOCK"
	if ! flock -w 120 9; then
		echo "device busy: $LOCK held for 120 s by another session" >&2
		exit 1
	fi
	ADB=(adb -s "$s")
}

in_front() {
	"${ADB[@]}" shell dumpsys power | grep -q "mWakefulness=Awake" \
		&& "${ADB[@]}" shell dumpsys activity activities | grep -m1 "ResumedActivity:" | grep -q " $PKG/"
}

need_front() {
	if ! in_front; then
		echo "Permoník is not on screen (or the screen is off); refusing to send input or take screenshots" >&2
		exit 1
	fi
}

cmd=${1:-}
shift || true
case $cmd in
	build)
		mkdir -p "$ROOT/build"
		if [[ -f $RELEASE_ENV ]]; then
			set -a; source "$RELEASE_ENV"; set +a
		fi
		export GODOT_ANDROID_KEYSTORE_RELEASE_PATH=${GODOT_ANDROID_KEYSTORE_RELEASE_PATH:-$HOME/.local/share/godot/keystores/debug.keystore}
		export GODOT_ANDROID_KEYSTORE_RELEASE_USER=${GODOT_ANDROID_KEYSTORE_RELEASE_USER:-androiddebugkey}
		export GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD=${GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD:-android}
		"$GODOT" --headless --path "$ROOT/game" --export-release Android "$APK"
		ls -la "$APK"
		;;
	install)
		device_cmd
		"${ADB[@]}" install -r "$APK"
		;;
	run)
		device_cmd
		"${ADB[@]}" shell am force-stop "$PKG"
		act=$("${ADB[@]}" shell cmd package resolve-activity --brief "$PKG" | tail -1 | tr -d '\r')
		# The game can't read a file shell writes into a folder the app created, so dev/ is always made by shell.
		"${ADB[@]}" shell "rm -rf $(dirname $ARGS_FILE) && mkdir -p $(dirname $ARGS_FILE) && echo '$*' > $ARGS_FILE"
		"${ADB[@]}" shell am start -n "$act"
		;;
	stop)
		device_cmd
		"${ADB[@]}" shell am force-stop "$PKG"
		;;
	log)
		s=$(serial)
		pid=$(adb -s "$s" shell pidof "$PKG" | tr -d '\r')
		[[ -n $pid ]] || { echo "$PKG is not running" >&2; exit 1; }
		exec adb -s "$s" logcat --pid="$pid" "$@"
		;;
	shot)
		device_cmd
		need_front
		"${ADB[@]}" exec-out screencap -p >"${1:?file.png}"
		echo "${1}"
		;;
	tap)
		device_cmd
		need_front
		"${ADB[@]}" shell input tap "${1:?x}" "${2:?y}"
		;;
	swipe)
		device_cmd
		need_front
		"${ADB[@]}" shell input swipe "${1:?x1}" "${2:?y1}" "${3:?x2}" "${4:?y2}" "${5:-300}"
		;;
	back)
		device_cmd
		need_front
		"${ADB[@]}" shell input keyevent KEYCODE_BACK
		;;
	deploy)
		"$0" build
		"$0" install
		"$0" run
		;;
	*)
		sed -n '2,16p' "$0"
		exit 1
		;;
esac
