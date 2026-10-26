#!/bin/bash
# One-time setup for tools/voice_build.py: a Python venv with the speech models, outside the repo.
# Needs python3, ffmpeg and espeak-ng on the system. About 3 GB with the models.
set -e
HOME_DIR="${PERMONIK_VOICE_HOME:-$HOME/.local/share/permonik-voice}"
mkdir -p "$HOME_DIR/kokoro"
for t in ffmpeg espeak-ng python3; do command -v $t >/dev/null || { echo "missing: $t"; exit 1; }; done
[ -x "$HOME_DIR/venv/bin/python" ] || python3 -m venv "$HOME_DIR/venv"
"$HOME_DIR/venv/bin/pip" install -q --index-url https://download.pytorch.org/whl/cpu torch
"$HOME_DIR/venv/bin/pip" install -q pocket-tts kokoro-onnx soundfile faster-whisper scipy num2words
cd "$HOME_DIR/kokoro"
base=https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$f" ] || "$HOME_DIR/venv/bin/python" -c "import urllib.request,sys; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])" "$base/$f" "$f"
done
echo "ready: $HOME_DIR"
