#!/usr/bin/env bash
# Export every platform into build/release/<version>/ ready for itch.io:
#   web/ (upload as html5), permonik-<v>-linux.zip, permonik-<v>-windows.zip, permonik-<v>.apk
#
#   tools/release.sh 0.1.0
#
# Sets the version in export_presets.cfg first (Android versionCode = yymmddHH, so every build installs over the
# last). Pushing is a separate step, printed at the end; it is never run from here.
set -euo pipefail

VER=${1:?usage: tools/release.sh <version>}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
GODOT=${GODOT:-$HOME/apps/godot-4.6/Godot_v4.6.3-stable_linux.x86_64}
OUT=$ROOT/build/release/$VER
PRESETS=$ROOT/game/export_presets.cfg

sed -i -E \
	-e "s/^version\/name=.*/version\/name=\"$VER\"/" \
	-e "s/^version\/code=.*/version\/code=$(date +%y%m%d%H)/" \
	-e "s/^application\/(file|product)_version=.*/application\/\1_version=\"$VER.0\"/" \
	"$PRESETS"

rm -rf "$OUT"
mkdir -p "$OUT"/{web,linux,windows}
"$GODOT" --headless --path "$ROOT/game" --import >/dev/null 2>&1 || true
"$GODOT" --headless --path "$ROOT/game" --export-release Web "$OUT/web/index.html"
"$GODOT" --headless --path "$ROOT/game" --export-release Linux "$OUT/linux/permonik.x86_64"
"$GODOT" --headless --path "$ROOT/game" --export-release Windows "$OUT/windows/Permonik.exe"
"$ROOT/tools/android.sh" build
cp "$ROOT/build/permonik.apk" "$OUT/permonik-$VER.apk"

for p in linux windows; do
	cp "$ROOT/LICENSE" "$OUT/$p/LICENSE.txt"
	cp "$ROOT/game/assets/LICENSE.md" "$OUT/$p/LICENSE-assets.md"
	(cd "$OUT/$p" && zip -qr "../permonik-$VER-$p.zip" .)
done
(cd "$OUT/web" && zip -qr "../permonik-$VER-web.zip" .)

ls -la "$OUT"
cat <<EOF

Push to itch.io (Andrej, after checking the builds):
  butler push "$OUT/web"                       redrick/permonik:html5   --userversion $VER
  butler push "$OUT/permonik-$VER-linux.zip"   redrick/permonik:linux   --userversion $VER
  butler push "$OUT/permonik-$VER-windows.zip" redrick/permonik:windows --userversion $VER
  butler push "$OUT/permonik-$VER.apk"         redrick/permonik:android --userversion $VER
EOF
