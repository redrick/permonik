"""Synthesises every game sound into game/assets/audio/{sfx,music}/*.ogg.

Usage: .venv/bin/python tools/audio_synth.py [--only name,name] [--verify-only]
"""
import os
import subprocess
import sys
import tempfile
import wave
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audio_dsp import SR, lufs  # noqa: E402
from audio_sfx import SFX, SFX_LOOPS, render_sfx  # noqa: E402
from audio_music import TRACKS, render_track  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "game", "assets", "audio")
LOOPS = {k for k in TRACKS if not k.endswith("_sting")}


def write_wav(path, x):
    x = np.atleast_2d(x)
    rng = np.random.default_rng(0)
    d = (rng.random(x.shape) - rng.random(x.shape)) / 32768
    pcm = np.clip(np.round((x + d) * 32767), -32768, 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[0])
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.T.tobytes())


def encode(x, dst, tmp):
    wav = os.path.join(tmp, os.path.basename(dst)[:-4] + ".wav")
    write_wav(wav, x)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-c:a", "libvorbis", "-q:a", "5", dst], check=True)
    os.remove(wav)


def job(args):
    kind, name, tmp = args
    if kind == "sfx":
        encode(render_sfx(name), os.path.join(OUT, "sfx", name + ".ogg"), tmp)
    else:
        x, _ = render_track(name)
        encode(x, os.path.join(OUT, "music", name + ".ogg"), tmp)
    return name


def decode(path, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<f4").reshape(-1, ch).T.astype(float)


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,channels,sample_rate:format=duration",
                        "-of", "default=nw=1", path], capture_output=True, text=True, check=True).stdout
    return dict(line.split("=", 1) for line in r.split())


def db(v):
    return 20 * np.log10(max(v, 1e-12))


def verify():
    rows = []
    bad = []
    total = 0
    for kind, names in (("sfx", SFX), ("music", list(TRACKS))):
        for name in names:
            p = os.path.join(OUT, kind, name + ".ogg")
            info = probe(p)
            ch = int(info["channels"])
            x = decode(p, ch)
            size = os.path.getsize(p)
            total += size
            pk = np.abs(x).max()
            rms = np.sqrt(np.mean(x * x))
            dc = np.abs(x.mean(axis=1)).max()
            dur = x.shape[1] / SR
            seam = ""
            if name in LOOPS or name in SFX_LOOPS:
                jump = np.abs(x[:, 0] - x[:, -1]).max()
                typ = np.percentile(np.abs(np.diff(x, axis=1)), 99.9)
                w = 2048
                e0 = db(np.sqrt(np.mean(x[:, :w] ** 2)))
                e1 = db(np.sqrt(np.mean(x[:, -w:] ** 2)))
                seam = f"jump {jump:.3f}/p99.9 {typ:.3f} edgeRMS {e1:+.1f}->{e0:+.1f}dB"
                if jump > 1.5 * typ or abs(e0 - e1) > 6 or (kind == "music" and not 60 <= dur <= 120):
                    bad.append(name)
            ok = (info["codec_name"] == "vorbis" and info["sample_rate"] == str(SR) and pk < 0.999 and dc < 2e-3
                  and ch == (1 if kind == "sfx" else 2))
            if not ok:
                bad.append(name)
            lu = f"{lufs(x):6.1f}" if kind == "music" else "   -  "
            rows.append(f"{kind:5s} {name:16s} {ch}ch {info['sample_rate']} {dur:7.2f}s pk {db(pk):6.1f} rms {db(rms):6.1f} "
                        f"lufs~{lu} dc {dc:.1e} {size / 1024:7.1f}KB {seam}")
    print("\n".join(rows))
    print(f"\nfiles: {len(rows)}  total {total / 1e6:.1f} MB  problems: {sorted(set(bad)) or 'none'}")
    return not bad


def main():
    args = sys.argv[1:]
    if "--verify-only" not in args:
        only = None
        if "--only" in args:
            only = set(args[args.index("--only") + 1].split(","))
        os.makedirs(os.path.join(OUT, "sfx"), exist_ok=True)
        os.makedirs(os.path.join(OUT, "music"), exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp:
            jobs = [("music", n, tmp) for n in TRACKS] + [("sfx", n, tmp) for n in SFX]
            if only:
                jobs = [j for j in jobs if j[1] in only]
            with Pool(min(len(jobs), os.cpu_count() or 4)) as pool:
                for n in pool.imap_unordered(job, jobs):
                    print("done", n, flush=True)
    sys.exit(0 if verify() else 1)


if __name__ == "__main__":
    main()
