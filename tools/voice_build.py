#!/usr/bin/env python3
"""Generates the spoken lines: game/assets/voice/<lang>/<speaker>/<key>.ogg.

English comes from Kokoro, Czech from Pocket-TTS-Czech speaking in the same character's English voice, so a
character sounds alike in both languages and no real person's voice is copied. Who sounds like what is in
game/data/voices.json. A file's key is the first 16 hex digits of sha1("<speaker>|<line text>"), the same
key the game computes, so a line edited in the JSON simply gets a new file and --prune drops the old one.

Setup once:  tools/voice_setup.sh
Run:         python3 tools/voice_build.py --list                 # what is missing, no generating
             python3 tools/voice_build.py --only films --lang en
             python3 tools/voice_build.py                         # everything missing, both languages
Every Czech sentence is the best of up to --takes tries as heard by Whisper; lines that still come out
poorly are listed in <voice home>/qa_cs.tsv. The run is niced and uses --threads cores (default 4): the
whole game takes hours, so leave it overnight.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "game" / "data"
OUT = ROOT / "game" / "assets" / "voice"
HOME = Path(os.environ.get("PERMONIK_VOICE_HOME", Path.home() / ".local/share/permonik-voice"))
CZ_CONFIG = "hf://vvolhejn/pocket-tts-czech/czech.yaml@7c1fbd0acba765617749dd17f3dbddc2be791cc7"
HEROES = list(json.loads((DATA / "classes.json").read_text()))
SCRIPTS = ROOT / "game" / "scripts"
STR = r'"((?:[^"\\]|\\.)*)"'
# Said once in each voice to give the Czech model something to copy.
REF_TEXT = ("Down in the old mine the lamps burn low, and every step echoes twice. I have walked these "
            "tunnels for longer than I care to say, and I still listen for the bell.")


def _venv_python():
    return HOME / "venv" / "bin" / "python"


try:
    import numpy as np
    import soundfile as sf
except ImportError:
    vp = _venv_python()
    if vp.exists() and Path(sys.prefix).resolve() != (HOME / "venv").resolve():
        os.execv(str(vp), [str(vp), *sys.argv])
    sys.exit("voice tools missing: run tools/voice_setup.sh first")


def key(speaker, text):
    return hashlib.sha1(f"{speaker}|{text}".encode("utf-8")).hexdigest()[:16]


def spoken(text):
    """What is actually said: no stage directions, no {name} placeholder, no sentence with a {v} count in it,
    no chapter numbers."""
    t = re.sub(r"\([^)]*\)", "", text)
    t = re.sub(r"(?m)^\s*[IVXLC]+\.\s*$", "", t)
    t = re.sub(r"[^.!?…]*\{v\}[^.!?…]*[.!?…]?", "", t)
    t = re.sub(r",?\s*\{name\}\s*,?", ",", t)
    t = re.sub(r"^\s*,\s*|\s*,\s*(?=[.!?…])", "", t)
    t = re.sub(r"([.!?…])\s*,\s*", r"\1 ", t)
    t = re.sub(r"\s+", " ", t).strip(" ,")
    return t if re.search(r"\w", t) else ""


# ---------------------------------------------------------------- what is said, and by whom
def lines():
    """(group, speaker, {lang: text}) for every line the game can speak."""
    out = []
    cin = json.loads((DATA / "cinematics.json").read_text())
    for film, f in cin.items():
        for k, t in f.get("lines", {}).items():
            out.append(("films", "narrator", t))
    for seq, items in json.loads((DATA / "slides.json").read_text()).items():
        for it in items:
            if isinstance(it.get("text"), dict):
                out.append(("films", "narrator", it["text"]))
    dialog = json.loads((DATA / "dialog.json").read_text())

    def walk(o, npc):
        if isinstance(o, dict):
            if "who" in o:
                who = str(o["who"])
                for k, t in o.items():
                    if not k.startswith("text") or not isinstance(t, dict):
                        continue
                    if who == "hero":
                        cls = HEROES if k == "text" else [k[5:]]
                        for c in cls:
                            if c in HEROES and (k != "text" or f"text_{c}" not in o):
                                out.append(("dialog", f"hero_{c}", t))
                    else:
                        out.append(("dialog", who, t))
                return
            for v in o.values():
                walk(v, npc)
        elif isinstance(o, list):
            for v in o:
                walk(v, npc)

    npcs = json.loads((DATA / "npcs.json").read_text())
    for _, t in dialog.get("_service", {}).items():
        by = str(t.get("by", ""))
        for n in [n for n, v in npcs.items() if v.get("role") == by] or [by]:
            out.append(("dialog", n, {"cs": t.get("cs", ""), "en": t.get("en", "")}))
    for npc, entries in dialog.items():
        if npc == "_service":
            continue
        if npc == "_gossip":
            for who, g in entries.items():
                for t in g:
                    out.append(("gossip", who, t))
        else:
            walk(entries, npc)
    for mid, m in json.loads((DATA / "monsters.json").read_text()).items():
        for t in m.get("lines", {}).values():
            if isinstance(t, dict):
                out.append(("bosses", mid, t))
    for sid, su in json.loads((DATA / "superuniques.json").read_text()).items():
        if isinstance(su.get("line"), dict):
            out.append(("bosses", sid, su["line"]))
    # Lines written in the boss scripts: say_t / shout take (cs, en), Sfx.cry names its speaker.
    for p in sorted(SCRIPTS.rglob("*.gd")):
        src = p.read_text()
        if p.parent.name == "bosses":
            for cs, en in re.findall(r"(?:say_t|shout)\(\s*" + STR + r",\s*" + STR, src):
                out.append(("bosses", p.stem, {"cs": cs, "en": en}))
            if "NAMES[h].cs).to_upper()" in src:
                for cs, en in re.findall(r'"\w+": \{"cs": ' + STR + r', "en": ' + STR + r"\}", src.split("const NAMES", 1)[1].split("\n", 1)[0]):
                    out.append(("bosses", p.stem, {"cs": cs.upper() + "!", "en": en.upper() + "!"}))
        for who, cs, en in re.findall(r'Sfx\.cry\("(\w+)", \{"cs": ' + STR + r', "en": ' + STR + r"\}", src):
            out.append(("bosses", who, {"cs": cs, "en": en}))
    # Read aloud on request: book pages, Kronika lore and codex entries.
    for b in json.loads((DATA / "books.json").read_text()).values():
        pages = b.get("pages", {})
        for i in range(max(len(v) for v in pages.values())):
            out.append(("reading", "reader", {l: v[i] for l, v in pages.items() if i < len(v)}))
    for e in json.loads((DATA / "lore.json").read_text()).values():
        if isinstance(e.get("text"), dict):
            out.append(("reading", "reader", e["text"]))
    for e in json.loads((DATA / "codex.json").read_text()).values():
        for k in ("text", "game"):
            if isinstance(e.get(k), dict):
                out.append(("reading", "reader", e[k]))
    seen, uniq = set(), []
    for g, s, t in out:
        sig = (s, t.get("cs", ""), t.get("en", ""))
        if sig not in seen:
            seen.add(sig)
            uniq.append((g, s, t))
    return uniq


def jobs(args, cast):
    todo, uncast = [], set()
    for g, s, t in lines():
        if args.only and g not in args.only:
            continue
        if args.speaker and s not in args.speaker:
            continue
        if s not in cast:
            uncast.add(s)
            continue
        for lang in args.lang:
            text = str(t.get(lang, ""))
            if not spoken(text):
                continue
            path = OUT / lang / s / f"{key(s, text)}.ogg"
            if args.force or not path.exists():
                todo.append((lang, s, text, path, g))
    return todo, uncast


# ---------------------------------------------------------------- engines
class English:
    def __init__(self, threads):
        import onnxruntime as ort
        from kokoro_onnx import EspeakConfig, Kokoro
        so = ort.SessionOptions()
        so.intra_op_num_threads = threads
        so.inter_op_num_threads = 1
        sess = ort.InferenceSession(str(HOME / "kokoro" / "kokoro-v1.0.onnx"), so, providers=["CPUExecutionProvider"])
        data = next(Path(p) for p in ["/usr/share/espeak-ng-data", "/usr/lib/x86_64-linux-gnu/espeak-ng-data"] if Path(p).exists())
        lib = next(str(p) for p in [Path("/usr/lib/libespeak-ng.so.1"), Path("/usr/lib/x86_64-linux-gnu/libespeak-ng.so.1")] if p.exists())
        self.k = Kokoro.from_session(sess, str(HOME / "kokoro" / "voices-v1.0.bin"), espeak_config=EspeakConfig(lib_path=lib, data_path=str(data)))
        vocab = getattr(self.k.tokenizer, "vocab", None)
        self.vocab = set(vocab.keys()) if vocab else None

    # Czech names keep their Czech sound: any word with Czech letters, and these.
    NAMES = {"Osel", "Hora", "Hory", "Brdy", "Megera", "Kosmas", "Prokop", "Nav", "Navi", "Smorodina", "Kalinov", "Vij",
             "Strzyga", "Agricola", "Fabián", "Zdař", "Sedlec", "Svornost", "Permonik"}
    CZ = re.compile(r"[áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ]")

    def _cs(self, word):
        ipa = subprocess.run(["espeak-ng", "-v", "cs", "-q", "--ipa=3", word], capture_output=True, text=True).stdout
        ipa = ipa.replace("_", "").replace("\n", " ").strip()
        return "".join(c for c in ipa if self.vocab is None or c in self.vocab or c == " ")

    def phonemes(self, text):
        out, buf = [], []
        for tok in re.findall(r"\w+|[^\w]+", text):
            if re.match(r"\w", tok) and (self.CZ.search(tok) or tok in self.NAMES):
                if buf:
                    out.append(self.k.tokenizer.phonemize("".join(buf), "en-gb"))
                    buf = []
                out.append(" " + self._cs(tok) + " ")
            else:
                buf.append(tok)
        if buf:
            out.append(self.k.tokenizer.phonemize("".join(buf), "en-gb"))
        return re.sub(r"\s+", " ", "".join(out)).strip()

    def style(self, v):
        if isinstance(v, list):
            return self.k.get_voice_style(v[0]) * float(v[2]) + self.k.get_voice_style(v[1]) * (1 - float(v[2]))
        return v

    def say(self, text, c):
        parts, sr = [], 24000
        text = re.sub(r"\bSt\. ", "Saint ", text)
        for s in [x.strip() for x in re.split(r"(?<=[.!?…])\s+", text) if x.strip()]:
            a, sr = self.k.create(self.phonemes(s), voice=self.style(c["voice"]), speed=float(c.get("speed", 1.0)),
                                  lang="en-gb", is_phonemes=True)
            parts += [a, np.zeros(int(sr * 0.3), dtype=a.dtype)]
        return np.concatenate(parts), sr


class Czech:
    """Pocket-TTS-Czech swallows the first word of an utterance, drops parts of long inputs and trips on
    quotes, so: clean punctuation, an "Inu." lead-in that is cut off again, at most two short sentences per
    call, and the best of several takes as heard by Whisper."""

    # Pocket skips digits, so numbers are said in words: years as cardinals, "13. století" as ordinals.
    ABBR = [(r"\bsv\. (?=\w+[yé]\b)", "svaté "), (r"\bsv\. ", "svatého "), (r"\bt\. j\.", "to jest"),
            (r"\batd\.", "a tak dále"), (r"\bJ\. M\. C\.", "Jeho Milosti Císaře"), (r"\b(Léta|léta) P\.", r"\1 Páně"),
            (r"\bDom\.", "Domini"), (r"(?<=\w) II\.(?=\s+[a-záčďéěíňóřšťúůýž])", " druhý"),
            (r"(?<=\w) I\.(?=\s+[a-záčďéěíňóřšťúůýž])", " první")]
    ORD = {1: "prvn*", 2: "druh", 3: "třet*", 4: "čtvrt", 5: "pát", 6: "šest", 7: "sedm", 8: "osm", 9: "devát",
           10: "desát", 11: "jedenáct", 12: "dvanáct", 13: "třináct", 14: "čtrnáct", 15: "patnáct", 16: "šestnáct",
           17: "sedmnáct", 18: "osmnáct", 19: "devatenáct", 20: "dvacát", 30: "třicát", 40: "čtyřicát",
           50: "padesát", 60: "šedesát", 70: "sedmdesát", 80: "osmdesát", 90: "devadesát"}

    @classmethod
    def ordinal(cls, n, case):
        ends = {"g": ("ého", "ího"), "l": ("ém", "ím"), "lp": ("ých", "ích")}[case]

        def one(k):
            st = cls.ORD[k]
            return st[:-1] + ends[1] if st.endswith("*") else st + ends[0]
        if n in cls.ORD:
            return one(n)
        if n < 100 and n // 10 * 10 in cls.ORD:
            return one(n // 10 * 10) + " " + one(n % 10)
        return None

    @classmethod
    def words(cls, t):
        from num2words import num2words
        for a, b in cls.ABBR:
            t = re.sub(a, b, t)
        t = re.sub(r"(\d) (\d{3})\b", r"\1\2", t)

        def ordn(m):
            before, n, after = m.group(1) or "", int(m.group(2)), m.group(3)
            case = "lp" if after.startswith("letech") else "l" if before.strip().lower() in ("v", "ve", "o", "na", "při") else "g"
            w = cls.ordinal(n, case)
            return f"{before}{w} {after}" if w else m.group(0)
        t = re.sub(r"(\b\w+ )?(\d+)\. ([a-záčďéěíňóřšťúůýž]\w*)", ordn, t)
        return re.sub(r"\d+", lambda m: num2words(int(m.group(0)), lang="cs"), t)

    def __init__(self, threads, takes):
        import torch
        from faster_whisper import WhisperModel
        from pocket_tts.models.tts_model import TTSModel
        torch.set_num_threads(threads)
        self.torch = torch
        self.m = TTSModel.load_model(config=CZ_CONFIG, temp=0.3)
        self.sr = self.m.config.mimi.sample_rate
        self.w = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=threads)
        self.threads = threads
        self.w_quick = None
        self.takes = takes
        self.quick = False
        self.states = {}
        self.qa = 0

    @classmethod
    def clean(cls, t):
        t = re.sub(r"[„“”‚‘’»«]", "", cls.words(t)).replace("…", ",")
        t = re.sub(r"\b(?:[A-Z]\.\s+)+(?=[A-ZÁ-Ž][a-zá-ž])", "", t)
        t = re.sub(r"\s*—\s*", ", ", t)
        t = re.sub(r"\s*[\[\]]\s*", " ", t)
        t = re.sub(r":\s+(?=[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])", ". ", t)
        t = re.sub(r"\s+,", ",", t)
        t = re.sub(r",\s*([,.!?])", r"\1", t)
        # A dash after a sentence end ("očí. — Já") would hide the sentence break, and the model stops there.
        return re.sub(r"([.!?])\s*,\s*", r"\1 ", t).strip(" ,")

    def sentences(self, t):
        out, joined = [], set()
        for x in [x.strip() for x in re.split(r"(?<=[.!?])\s+", self.clean(t)) if x.strip()]:
            if out and len(out) - 1 not in joined and (len(x) < 32 or len(out[-1]) < 32) and len(out[-1]) + len(x) < 90:
                out[-1] += " " + x
                joined.add(len(out) - 1)
            else:
                out.append(x)
        return [c for x in out for c in self.clauses(x)]

    @staticmethod
    def clauses(s, top=100, chunk=90):
        """Long sentences lose words, so they are said in pieces split at commas and semicolons."""
        if len(s) <= top:
            return [s]
        out = []
        for c in re.split(r"(?<=[,;:])\s+", s):
            if out and len(out[-1]) + len(c) < chunk:
                out[-1] += " " + c
            else:
                out.append(c)
        return out

    def norm(self, t):
        import unicodedata
        t = self.words(t).lower()
        t = "".join(c for c in unicodedata.normalize("NFD", t) if not unicodedata.combining(c))
        return re.sub(r"[^a-z0-9]", "", t)

    def score(self, a, text):
        import difflib
        import scipy.signal as ss
        a16 = ss.resample_poly(a, 16000, self.sr).astype(np.float32)
        w = self.w
        if self.quick:
            from faster_whisper import WhisperModel
            self.w_quick = self.w_quick or WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=self.threads)
            w = self.w_quick
        heard = " ".join(s.text for s in w.transcribe(a16, language="cs", beam_size=5)[0])
        return difflib.SequenceMatcher(None, self.norm(text), self.norm(heard)).ratio(), heard

    def trim_lead(self, a):
        n = int(self.sr * 0.02)
        env = np.convolve(np.abs(a), np.ones(n) / n, "same")
        quiet = env < 10 ** (-38 / 20) * max(np.abs(a).max(), 1e-6)
        run = 0
        for i, q in enumerate(quiet):
            run = run + 1 if q else 0
            if run > self.sr * 0.12 and i > self.sr * 0.25:
                return a[i - int(self.sr * 0.05):]
        return a

    def best(self, st, s):
        top = (-1.0, None, "")
        takes = max(1, self.takes // 2) if self.quick else self.takes
        for k in range(takes * 2):
            if k >= takes and top[0] >= 0.9:
                break
            self.torch.manual_seed(k)
            a = self.trim_lead(self.m.generate_audio(st, "Inu. " + s).squeeze().cpu().numpy())
            r, heard = self.score(a, s)
            if r > top[0]:
                top = (r, a, heard)
            if r >= 0.95:
                break
        # Some lone sentences come out silent ("Nikdy mu nedávejte kahan."); a leading "A" carries them.
        if top[0] < 0.5 and not s.startswith("A "):
            r, a, heard = self.best(st, "A " + s[0].lower() + s[1:])
            if r > top[0]:
                top = (r, a, heard)
        return top

    def say(self, text, ref):
        if ref not in self.states:
            self.states[ref] = self.m.get_state_for_audio_prompt(ref)
        st = self.states[ref]
        gap = np.zeros(int(self.sr * 0.35), dtype=np.float32)
        parts, worst = [], 1.0
        for s in self.sentences(text):
            r, a, heard = self.best(st, s)
            halves = re.split(r"(?<=[.!?])\s+", s)
            if r < 0.9 and len(halves) == 2:
                r1, a1, h1 = self.best(st, halves[0])
                r2, a2, h2 = self.best(st, halves[1])
                if (r1 + r2) / 2 > r:
                    r, a, heard = (r1 + r2) / 2, np.concatenate([a1, gap, a2]), f"{h1} {h2}"
            worst = min(worst, r)
            if r < 0.9:
                HOME.mkdir(parents=True, exist_ok=True)
                with open(HOME / "qa_cs.tsv", "a") as f:
                    f.write(f"{r:.2f}\t{s}\t{heard.strip()}\n")
                self.qa += 1
            parts += [a.astype(np.float32), gap]
        return np.concatenate(parts), self.sr, worst


# ---------------------------------------------------------------- output
def encode(a, sr, fx, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
        sf.write(tmp.name, a, sr)
        chain = (fx + "," if fx else "") + "loudnorm=I=-18:TP=-2"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", tmp.name, "-af", chain, "-ac", "1", "-ar", "24000",
                        "-c:a", "libvorbis", "-q:a", "3", str(path)], check=True)


def ref_clip(eng, speaker, c):
    sig = hashlib.sha1(json.dumps([c.get("voice"), c.get("speed"), REF_TEXT]).encode()).hexdigest()[:8]
    p = HOME / "ref" / f"{speaker}_{sig}.wav"
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        a, sr = eng.say(REF_TEXT, c)
        sf.write(p, a, sr)
    return str(p)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lang", nargs="+", default=["en", "cs"], choices=["en", "cs"])
    ap.add_argument("--only", nargs="+", choices=["films", "dialog", "gossip", "bosses", "reading"])
    ap.add_argument("--speaker", nargs="+")
    ap.add_argument("--limit", type=int, default=0, help="stop after this many lines")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--takes", type=int, default=4, help="Czech tries per sentence (doubled for poor ones)")
    ap.add_argument("--force", action="store_true", help="redo lines that already have a file")
    ap.add_argument("--list", action="store_true", help="only say what is missing")
    ap.add_argument("--prune", action="store_true", help="delete voice files no line uses any more")
    args = ap.parse_args()
    cast = {k: v for k, v in json.loads((DATA / "voices.json").read_text()).items() if not k.startswith("_")}
    todo, uncast = jobs(args, cast)
    if uncast:
        print("no voice in voices.json for:", ", ".join(sorted(uncast)))
    if args.prune:
        keep = {OUT / l / s / f"{key(s, str(t.get(l, '')))}.ogg" for _, s, t in lines() for l in ("en", "cs")}
        gone = 0
        for p in OUT.rglob("*.ogg"):
            if p not in keep:
                p.unlink()
                Path(str(p) + ".import").unlink(missing_ok=True)
                gone += 1
        print("pruned", gone)
    by = {}
    for lang, s, text, _, _ in todo:
        by.setdefault((lang, s), [0, 0])
        by[(lang, s)][0] += 1
        by[(lang, s)][1] += len(spoken(text))
    for (lang, s), (n, chars) in sorted(by.items()):
        print(f"  {lang} {s:22} {n:4} lines {chars:6} chars")
    print(f"missing: {len(todo)} lines, {sum(len(spoken(t)) for _, _, t, _, _ in todo)} chars")
    if args.list or not todo:
        return
    if args.limit:
        todo = todo[: args.limit]
    os.nice(10)
    eng = English(args.threads)
    cz = Czech(args.threads, args.takes) if any(j[0] == "cs" for j in todo) else None
    for i, (lang, s, text, path, g) in enumerate(todo, 1):
        # Read-aloud texts are most of the audio: fewer Czech takes, checked by a smaller Whisper.
        if cz:
            cz.quick = g == "reading"
        c = cast[s]
        said = spoken(text)
        if lang == "en":
            a, sr = eng.say(said, c)
            note = ""
        else:
            a, sr, worst = cz.say(said, ref_clip(eng, s, c))
            note = f" (asr {worst:.2f})"
        encode(a, sr, c.get("fx", ""), path)
        print(f"[{i}/{len(todo)}] {lang} {s}: {said[:60]}{note}", flush=True)
    if cz and cz.qa:
        print(f"{cz.qa} Czech sentences under 0.9, listed in {HOME / 'qa_cs.tsv'}")


if __name__ == "__main__":
    main()
