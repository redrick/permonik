import numpy as np
from audio_dsp import *


class Mix:
    def __init__(self, dur, loop=True, tail=4.0):
        self.loop = loop
        self.n = N(dur)
        self.L = self.n if loop else self.n + N(tail)
        self.dry = np.zeros((2, self.L))
        self.wet = np.zeros((2, self.L))
        self.secs = self.n / SR

    def add(self, x, t, pan=0.0, g=1.0, rev=0.25):
        if x.ndim == 1:
            a = (np.clip(pan, -1, 1) + 1) * np.pi / 4
            x = np.array([np.cos(a) * x, np.sin(a) * x]) * np.sqrt(2)
        x = x * g
        s = N(t)
        self._w(self.dry, x, s)
        if rev:
            self._w(self.wet, x * rev, s)

    def _w(self, b, x, s):
        m = x.shape[1]
        if not self.loop:
            if s >= self.L:
                return
            k = min(m, self.L - s)
            b[:, s:s + k] += x[:, :k]
            return
        pos = 0
        while pos < m:
            i = (s + pos) % self.L
            k = min(m - pos, self.L - i)
            b[:, i:i + k] += x[:, pos:pos + k]
            pos += k

    def bed(self, x, pan=0.0, g=1.0, rev=0.2):
        self.add(x[: self.L] if x.shape[-1] >= self.L else x, 0, pan, g, rev)

    def render(self, ir, target, tail_fade=None):
        out = self.dry + conv(self.wet, ir, circular=self.loop)
        shelf = lambda f: np.sqrt(1 + (10 ** (5 / 10) - 1) * (f / 2500) ** 2 / (1 + (f / 2500) ** 2))
        out = ffilt(out, chain(hp(28, 2), shelf), circular=self.loop)
        out -= out.mean(axis=1, keepdims=True)
        l0 = lufs(out)
        g = 10 ** ((target - l0) / 20)
        pk = np.abs(out).max()
        g = min(g, 1.25 / pk)
        out = softclip(out * g, 0.62, 0.89)
        if not self.loop:
            out = out[:, : self.L]
            e = np.ones(self.L)
            k = N(tail_fade or 1.0)
            e[-k:] = np.linspace(1, 0, k) ** 2
            out *= e
            out[:, : N(0.002)] *= np.linspace(0, 1, N(0.002))
        return out


def qf(f, secs):
    return max(1, round(f * secs)) / secs


def lfo(n, cycles, ph=0.0):
    return np.sin(TAU * cycles * np.arange(n) / n + ph)


def wobble(r, n, kmin=2, kmax=12, count=3):
    w = sum(lfo(n, int(r.integers(kmin, kmax)), r.uniform(0, TAU)) / (i + 1) for i in range(count))
    return w / np.abs(w).max()


def loop_wind(r, m, fcs=(250, 600, 1400), q=1.2, gust=2.0):
    n = m.L
    out = np.zeros((2, n))
    for ch in range(2):
        for fc in fcs:
            x = ffilt(r.standard_normal(n), bp(fc, q), circular=m.loop)
            env = (0.5 + 0.5 * wobble(r, n, 2, 14)) ** gust
            out[ch] += x * env / len(fcs)
    return out * 0.6


def loop_drone(r, m, f, kind="saw", fc=400, vib=0.0, am=0.25, ph=None):
    n = m.L
    fq = qf(f, m.secs)
    fr = fq * (1 + vib * lfo(n, max(1, round(m.secs * 4.7)), r.uniform(0, TAU)))
    if kind == "saw":
        x = ffilt(saw(fr, n, r.uniform()), lp(fc, 2), circular=m.loop)
    elif kind == "reed":
        x = ffilt(reed(fr, n, r), chain(REED_BODY, lp(fc, 1)), circular=m.loop)
    else:
        x = np.sin(TAU * np.cumsum(fr) / SR + r.uniform(0, TAU))
    return x * (1 - am + am * (0.5 + 0.5 * wobble(r, n, 1, 6)))


def loop_river(r, m, g=1.0):
    n = m.L
    out = np.zeros((2, n))
    for ch in range(2):
        b = np.cumsum(r.standard_normal(n))
        b = ffilt(b - b.mean(), chain(hp(40, 1), lp(500, 1)), circular=m.loop)
        b /= np.abs(b).max()
        mid = ffilt(r.standard_normal(n), bp(900, 0.8), circular=m.loop) * (0.5 + 0.5 * wobble(r, n, 8, 40)) * 0.08
        out[ch] = b * 0.6 + mid
    for i in range(int(m.secs * 6)):
        m.add(bubble(r, r.uniform(250, 900), r.uniform(0.01, 0.03)) * 0.12 * g, r.uniform(0, m.secs), r.uniform(-0.8, 0.8), 1, 0.3)
    return out * g


def play_cimbal(m, r, t, dur, midi, vel=0.7, trem=False, rate=0.09, pan=0.0, g=0.5, rev=0.3, t60=2.2):
    f = mtof(midi)
    if not trem or dur < rate * 2.5:
        m.add(cimbal(f, max(2.2, t60 * 1.1), vel, t60, int(r.integers(3))), t + r.uniform(0, 0.01), pan, g, rev)
        return
    k = int(dur / rate)
    for i in range(k):
        v = vel * (0.95 if i == 0 else 0.42 + 0.12 * np.sin(np.pi * i / k) + r.uniform(-0.05, 0.05))
        m.add(cimbal(f, 1.8 if i < k - 1 else 2.6, v, 1.4, int(r.integers(3))), t + i * rate + r.uniform(-0.006, 0.006), pan, g, rev)


def scale_for(base, chord):
    sc = set(base)
    cp = {c % 12 for c in chord}
    for c in cp:
        if c not in sc:
            for d in (-1, 1):
                if (c + d) % 12 not in cp:
                    sc.discard((c + d) % 12)
            sc.add(c)
    return sc


def melody(r, chords, base, bars, rhythms, lo, hi, unit, cadence_len, phrase=8, prev=None):
    out = []
    for b in bars:
        ch = chords[b]
        cp = {c % 12 for c in ch}
        sc = scale_for(base, ch)
        last = (b - bars[0]) % phrase == phrase - 1
        rh = [(0, cadence_len)] if last else rhythms[int(r.integers(len(rhythms)))]
        for j, (st, du) in enumerate(rh):
            allowed = cp if (j == 0 or last) else sc
            pool = [x for x in range(lo, hi + 1) if x % 12 in allowed]
            if last:
                pool = [x for x in pool if x % 12 == ch[0] % 12]
            if prev is None:
                x = pool[len(pool) // 2]
            else:
                w = np.array([np.exp(-abs(x - prev) / 2.2) * (0.25 if x == prev else 1.0) for x in pool])
                x = int(r.choice(pool, p=w / w.sum()))
            out.append((b, st * unit, du * unit, x))
            prev = x
    return out


SCALE_MINOR = [0, 2, 3, 5, 7, 8, 10]


def pcs(root, mode):
    return [(root + i) % 12 for i in mode]


# ---------------- tracks ----------------

def t_menu():
    r = rng_for("menu")
    bar = 4.0
    m = Mix(20 * bar)
    m.bed(loop_drone(r, m, mtof(nm("D2")), "reed", 900, 0.002, 0.3), -0.2, 0.18, 0.3)
    m.bed(loop_drone(r, m, mtof(nm("A2")), "reed", 900, 0.002, 0.3), 0.2, 0.12, 0.3)
    m.bed(loop_drone(r, m, mtof(nm("D1")), "sine", am=0.2), 0, 0.18, 0.05)
    m.bed(loop_wind(r, m, (300, 700), 1.5, 2.5), 0, 0.12, 0.1)
    chords = [[50, 53, 57], [46, 50, 53], [43, 46, 50], [45, 49, 52], [50, 53, 57]]
    for i, ch in enumerate(chords):
        voic = [c + 12 for c in ch] + [ch[0]]
        m.add(choir(mtof(voic), 4 * bar + 3, [(0, "u"), (8, "o"), (19, "u")], r, 4, 4, 0.9), i * 4 * bar - 1.5, 0, 0.32, 0.6)
    for k, t0 in enumerate((0, 4.2, 8.4, 40.0, 44.2, 48.4)):
        m.add(bell(mtof(nm("D3")), 8, r, 0.9, 0.3), t0 + 0.5, 0.1, 0.32 * (0.85 ** (k % 3)), 0.7)
    theme = [(0, 2, "D5"), (2, 1, "F5"), (3, 1, "E5"), (4, 2, "D5"), (6, 1, "C5"), (7, 1, "Bb4"),
             (8, 3, "A4"), (11, 1, "G4"), (12, 2, "A4"), (14, 2, "D4")]
    for start in (16.0, 60.0):
        for b, d, s in theme:
            play_cimbal(m, r, start + b, d, nm(s), 0.6, d >= 2, 0.1, r.uniform(-0.2, 0.2), 0.45, 0.45)
    for i in range(10):
        m.add(drip(r) * 0.12, r.uniform(0, m.secs), r.uniform(-0.9, 0.9), 1, 0.7)
    return m, make_ir(r, 5.0, 0.03, 5000, 1200), -16


def t_town_hora():
    r = rng_for("town_hora")
    e = 60 / 84 / 2
    bar = 6 * e
    bars = 40
    m = Mix(bars * bar)
    prog = [[50, 53, 57], [48, 52, 55], [46, 50, 53], [45, 49, 52], [50, 53, 57], [43, 46, 50], [45, 49, 52], [50, 53, 57]]
    chords = [prog[b % 8] for b in range(bars)]
    pat = [0, 1, 2, 3, 2, 1]
    for b in range(bars):
        ch = chords[b]
        tones = [c + 12 for c in ch] + [ch[0] + 24]
        sec = b // 8
        for j, k in enumerate(pat):
            if sec == 3 and j % 2:
                continue
            v = 0.5 + 0.18 * (j == 0) + r.uniform(-0.07, 0.07)
            play_cimbal(m, r, b * bar + j * e, e, tones[k], v, False, pan=-0.35 + 0.15 * k, g=0.42, rev=0.3)
        m.add(ks(mtof(ch[0] - 12), 4.5, 4.0, 0.3, 1400, 0.2), b * bar, 0.0, 0.8, 0.2)
        if b % 2 == 1:
            m.add(ks(mtof(ch[2] - 12), 3.0, 3.0, 0.3, 1200, 0.2), b * bar + 3 * e, 0.1, 0.4, 0.2)
    rh = [[(0, 2), (2, 2), (4, 2)], [(0, 3), (3, 1), (4, 2)], [(0, 4), (4, 1), (5, 1)], [(0, 2), (2, 1), (3, 1), (4, 2)]]
    base = pcs(2, SCALE_MINOR)
    for bars_ in (range(8, 24), range(32, 40)):
        for b, st, du, x in melody(r, chords, base, list(bars_), rh, nm("A4"), nm("F5"), e, 6):
            play_cimbal(m, r, b * bar + st, du, x, 0.7, du >= 2 * e, 0.085, 0.15, 0.55, 0.35)
    m.bed(loop_drone(r, m, mtof(nm("D2")), "saw", 260, 0.003, 0.4), -0.1, 0.12, 0.2)
    m.bed(loop_drone(r, m, mtof(nm("A2")), "saw", 300, 0.003, 0.4), 0.1, 0.07, 0.2)
    m.bed(loop_wind(r, m, (350, 900), 1.4, 3), 0, 0.06, 0.05)
    for t0 in (0.0, 20 * bar):
        m.add(bell(mtof(nm("D3")), 7, r, 0.8, 0.25), t0, -0.5, 0.22, 0.8)
    return m, make_ir(r, 3.0, 0.02, 6000, 1800), -15


def t_town_pribram():
    r = rng_for("town_pribram")
    beat = 60 / 72
    e = beat / 2
    bar = 4 * beat
    bars = 24
    m = Mix(bars * bar)
    prog = [[57, 60, 64], [55, 59, 62], [50, 54, 57], [57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59], [57, 60, 64]]
    chords = [prog[b % 8] for b in range(bars)]
    m.bed(loop_drone(r, m, mtof(nm("A2")), "reed", 2500, 0.002, 0.15), -0.15, 0.16, 0.25)
    m.bed(loop_drone(r, m, mtof(nm("A1")), "reed", 1200, 0.002, 0.15), 0.15, 0.14, 0.25)
    for b in range(bars):
        ch = chords[b]
        for bt in (0, 2):
            for i, c in enumerate(sorted(ch)):
                play_cimbal(m, r, b * bar + bt * beat + 0.035 * i, e, c + 12 * (i < 1), 0.45 + 0.1 * (bt == 0), False,
                            pan=-0.3 + 0.2 * i, g=0.38, rev=0.3)
        m.add(ks(mtof(ch[0] - 24 if ch[0] > 54 else ch[0] - 12), 4.0, 3.5, 0.3, 1200, 0.2), b * bar, 0, 0.75, 0.2)
        if b % 2 == 0:
            for h, off in enumerate((1.0, 1.5, 3.0)):
                s = metal(r.uniform(380, 520), N(1.2), r, 0.3, click=0.3)
                m.add(ffilt(s, lp(1500)), b * bar + off * beat, 0.7, 0.05, 1.0)
    rh = [[(0, 4), (4, 2), (6, 2)], [(0, 3), (3, 1), (4, 4)], [(0, 2), (2, 2), (4, 2), (6, 2)], [(0, 6), (6, 2)]]
    base = pcs(9, [0, 2, 3, 5, 7, 9, 10])
    for bars_ in (range(4, 12), range(16, 24)):
        for b, st, du, x in melody(r, chords, base, list(bars_), rh, nm("E4"), nm("D5"), e, 8):
            m.add(fiddle(mtof(x), du * 1.04 + 0.12, r), b * bar + st, 0.2, 0.55, 0.4)
    m.bed(loop_wind(r, m, (400,), 1.4, 3), 0, 0.05, 0.05)
    return m, make_ir(r, 2.8, 0.02, 6000, 2000), -15


def t_town_jachymov():
    r = rng_for("town_jachymov")
    bar = 3.0
    bars = 32
    m = Mix(bars * bar)
    prog = [[52, 56, 59], [53, 57, 60], [52, 56, 59], [50, 53, 57], [52, 56, 59], [53, 57, 60], [55, 59, 62], [53, 57, 60]]
    chords = [prog[b % 8] for b in range(bars)]
    base = pcs(4, [0, 1, 4, 5, 7, 8, 10])
    for b in range(bars):
        ch = chords[b]
        m.add(ks(mtof(ch[0] - 12), 5.0, 4.5, 0.3, 1200, 0.2), b * bar, 0, 0.8, 0.25)
        for j, k in enumerate((1, 2, 0)):
            play_cimbal(m, r, b * bar + (j + 1) * 1.0, 0.5, ch[k], 0.35, False, pan=-0.4, g=0.35, rev=0.35)
        if b % 2 == 1:
            m.add(ffilt(metal(r.choice([330, 352, 440]), N(2.5), r, 0.6, click=0.2), lp(1800)), b * bar + 1.5, 0.6, 0.06, 1.0)
    rh = [[(0, 2), (2, 2), (4, 2)], [(0, 4), (4, 2)], [(0, 3), (3, 1), (4, 2)], [(0, 6)]]
    for bars_ in (range(4, 16), range(20, 32)):
        for b, st, du, x in melody(r, chords, base, list(bars_), rh, nm("B4"), nm("A5"), 0.5, 6, phrase=4):
            play_cimbal(m, r, b * bar + st, du, x, 0.65, du >= 1.0, 0.07, 0.25, 0.5, 0.35, 2.4)
    m.bed(loop_drone(r, m, mtof(nm("E1")), "saw", 220, 0.0, 0.6), -0.1, 0.4, 0.3)
    m.bed(loop_drone(r, m, mtof(nm("B1")), "saw", 260, 0.0, 0.6), 0.1, 0.2, 0.3)
    m.bed(loop_wind(r, m, (250, 700), 1.5, 2.5), 0, 0.1, 0.1)
    return m, make_ir(r, 3.5, 0.025, 5000, 1500), -15


def t_town_nav():
    r = rng_for("town_nav")
    bar = 4.8
    bars = 20
    m = Mix(bars * bar)
    prog = [[47, 50, 54], [48, 52, 55], [47, 50, 54], [43, 47, 50], [40, 43, 47], [48, 52, 55], [42, 46, 49], [47, 50, 54], [43, 47, 50], [42, 45, 48]]
    vow = ["u", "o", "a", "o", "u"]
    for i, ch in enumerate(prog):
        v = [c + 12 for c in ch] + [ch[0], ch[1] + 24]
        k = [(0, vow[i % 5]), (5, vow[(i + 1) % 5]), (11, vow[(i + 2) % 5])]
        m.add(choir(mtof(v), 2 * bar + 3, k, r, 3, 3, 1.0, 0.1), i * 2 * bar - 1.5, 0, 0.35, 0.6)
        m.add(bell(mtof(ch[0] + 12), 7, r, 0.7, 0.2), i * 2 * bar + r.uniform(0.5, 3), r.uniform(-0.5, 0.5), 0.22, 0.7)
    for i in (0, 10):
        m.add(bell(mtof(nm("B2")), 9, r, 0.9, 0.3), i * bar, 0, 0.3, 0.8)
    pent = [nm(s) for s in ("B5", "D6", "E6", "F#6", "A6", "C6", "B6")]
    t = 1.0
    while t < m.secs:
        m.add(ks(mtof(int(r.choice(pent))), 3.0, 2.5, 0.1, 9000, 0.5), t, r.uniform(-0.7, 0.7), 0.14, 0.7)
        t += r.uniform(1.5, 4.5)
    m.bed(loop_river(r, m, 0.5), 0, 0.25, 0.3)
    m.bed(loop_wind(r, m, (500, 1200), 1.5, 3), 0, 0.06, 0.2)
    return m, make_ir(r, 7.0, 0.04, 4000, 1000), -16


def distant_pick(r):
    s = metal(r.uniform(900, 1400), N(0.6), r, 0.08, click=0.6)
    s[: N(0.1)] += 0.6 * thud(180, 120, N(0.1), 0.02)
    return ffilt(s, chain(lp(2200, 1), hp(150)))


def t_mine_1():
    r = rng_for("mine_1")
    m = Mix(96.0)
    m.bed(loop_drone(r, m, mtof(nm("D1")), "sine", am=0.3), 0, 0.1, 0.1)
    m.bed(loop_drone(r, m, mtof(nm("D2")) * 1.003, "saw", 180, 0, 0.5), -0.3, 0.18, 0.3)
    m.bed(loop_drone(r, m, mtof(nm("A2")), "saw", 220, 0, 0.6), 0.3, 0.1, 0.3)
    m.bed(loop_wind(r, m, (180, 450), 2.0, 3), 0, 0.12, 0.3)
    for i in range(48):
        m.add(drip(r) * r.uniform(0.15, 0.35), r.uniform(0, m.secs), r.uniform(-0.9, 0.9), 1, 0.9)
    for g in range(11):
        t0 = r.uniform(0, m.secs)
        pan = r.uniform(-0.8, 0.8)
        for k in range(int(r.integers(2, 5))):
            m.add(distant_pick(r), t0 + k * r.uniform(0.42, 0.55), pan, 0.08, 1.3)
    notes = [nm(s) for s in ("D4", "F4", "G4", "A4", "C5", "D5", "F5", "A3")]
    t = 3.0
    while t < m.secs - 1:
        x = int(r.choice(notes))
        play_cimbal(m, r, t, 0.5, x, 0.45, False, pan=r.uniform(-0.5, 0.5), g=0.4, rev=0.8, t60=3.0)
        if r.random() < 0.5:
            play_cimbal(m, r, t + r.choice([0.5, 0.75, 1.0]), 0.5, x + int(r.choice([-2, -3, 2, 5])), 0.35, False, g=0.4, rev=0.8, t60=3.0)
        t += r.uniform(4, 9)
    for i in range(2):
        n = N(6)
        m.add(ffilt(r.standard_normal(n), lp(120)) * swell(n, 2.5, 3, 1), r.uniform(0, m.secs), 0, 0.25, 0.3)
    return m, make_ir(r, 6.0, 0.04, 4000, 1100), -17


def t_mine_2():
    r = rng_for("mine_2")
    m = Mix(96.0)
    m.bed(loop_drone(r, m, mtof(nm("G1")), "reed", 700, 0.002, 0.25), -0.15, 0.22, 0.3)
    m.bed(loop_drone(r, m, mtof(nm("G2")), "reed", 1400, 0.002, 0.25), 0.15, 0.15, 0.3)
    m.bed(loop_drone(r, m, mtof(nm("D3")), "reed", 1600, 0.002, 0.5), 0.0, 0.05, 0.3)
    m.bed(loop_wind(r, m, (220, 520, 1100), 2.2, 2.5), 0, 0.3, 0.25)
    for g in range(16):
        t0 = r.uniform(0, m.secs)
        pan = r.uniform(-0.9, 0.9)
        for k in range(int(r.integers(1, 4))):
            f = r.uniform(140, 320)
            s = modal([f, f * 1.58, f * 2.4], [1, 0.5, 0.3], [0.08, 0.05, 0.03], N(0.5), r)
            s[: N(0.003)] += 0.3 * r.standard_normal(N(0.003))
            m.add(ffilt(s, lp(2500)), t0 + k * r.uniform(0.18, 0.4), pan, 0.25, 0.9)
    for i in range(7):
        m.add(creak(r, r.uniform(0.8, 1.8), r.uniform(15, 30), r.uniform(6, 12), (r.uniform(300, 600), r.uniform(900, 1500))),
              r.uniform(0, m.secs), r.uniform(-0.8, 0.8), 0.08, 0.8)
    for i in range(30):
        m.add(drip(r, r.uniform(500, 900)) * 0.12, r.uniform(0, m.secs), r.uniform(-0.9, 0.9), 1, 0.8)
    t = 10.0
    for k in range(5):
        x = int(r.choice([nm("D4"), nm("Bb3"), nm("G3"), nm("C4"), nm("A3")]))
        m.add(dudy_note(mtof(x), r.uniform(3.0, 5.5), r, 0.4, 1.0) * 0.6, t, 0.2, 0.2, 0.6)
        t += r.uniform(14, 20)
    return m, make_ir(r, 5.0, 0.03, 3500, 1200), -17


def t_mine_3():
    r = rng_for("mine_3")
    beat = 0.8
    m = Mix(100 * beat)
    for b in range(100):
        h = thud(58, 36, N(0.6), 0.18, 0.004)
        m.add(h, b * beat, 0, 0.55, 0.15)
        m.add(h * 0.55, b * beat + 0.22, 0, 0.55, 0.15)
    pitches = [420, 455, 610, 300]
    for b in range(0, 100, 2):
        sec = (b // 16) % 3
        hits = [0.0, 1.5] if sec == 0 else ([0.0, 0.5, 1.5] if sec == 1 else [0.0, 1.0])
        for hh in hits:
            f = pitches[int(r.integers(len(pitches)))]
            s = metal(f, N(2.0), r, 0.7, click=0.8)
            m.add(ffilt(s, lp(5000)), b * beat + hh * beat, r.uniform(-0.6, 0.6), 0.09, 0.9)
    m.bed(loop_drone(r, m, mtof(nm("E1")), "saw", 200, 0, 0.3), -0.2, 0.32, 0.2)
    m.bed(loop_drone(r, m, mtof(nm("F1")), "saw", 200, 0, 0.5), 0.2, 0.2, 0.2)
    m.bed(loop_drone(r, m, mtof(nm("Bb1")), "saw", 300, 0, 0.6), 0.0, 0.1, 0.3)
    n = m.L
    hiss = np.array([ffilt(r.standard_normal(n), chain(hp(2500), lp(9000, 1)), circular=True) for _ in range(2)])
    m.bed(hiss * (0.4 + 0.6 * (0.5 + 0.5 * wobble(r, n, 3, 10))), 0, 0.05, 0.1)
    for i in range(9):
        d = r.uniform(2, 4)
        k = N(d)
        s = ffilt(r.standard_normal(k), chain(hp(1200), lp(8000, 1))) * swell(k, 0.2, d * 0.6, 1.5)
        m.add(s, r.uniform(0, m.secs), r.uniform(-0.8, 0.8), 0.18, 0.5)
    for i in range(120):
        m.add(np.array([1.0, -0.6, 0.3, -0.1]) * 0.25, r.uniform(0, m.secs), r.uniform(-0.6, 0.6), 1, 0.1)
    t = tt(n)
    bm = sum(np.sin(TAU * qf(f, m.secs) * t + r.uniform(0, TAU)) * a for f, a in ((733, 1), (1871, 0.5), (2549, 0.3)))
    m.bed(bm * (0.5 + 0.5 * wobble(r, n, 2, 8)) ** 3, 0.3, 0.03, 0.6)
    return m, make_ir(r, 4.5, 0.03, 5000, 1500), -16


def t_mine_4():
    r = rng_for("mine_4")
    m = Mix(112.0)
    prog = [[45, 52, 60, 64, 71], [46, 53, 58, 62, 65], [43, 50, 58, 62, 67], [45, 52, 57, 60, 64],
            [41, 48, 57, 60, 65], [40, 47, 56, 59, 64], [38, 45, 53, 57, 62]]
    vk = [["a", "o"], ["o", "u"], ["u", "o"], ["o", "a"], ["a", "e"], ["e", "o"], ["o", "u"]]
    for i, ch in enumerate(prog):
        k = [(0, vk[i][0]), (19, vk[i][1])]
        m.add(choir(mtof(ch), 19, k, r, 3.5, 4.0, 0.95, 0.1, 3), i * 16 - 1.5, 0, 0.42, 0.65)
    t = 2.0
    while t < m.secs:
        ch = prog[int(t // 16) % 7]
        m.add(bell(mtof(int(r.choice(ch[2:])) + 12 * int(r.integers(0, 2))), 9, r, 0.6, 0.2), t, r.uniform(-0.6, 0.6), 0.16, 0.8)
        t += r.uniform(6, 10)
    for i in (0, 56):
        m.add(bell(mtof(nm("A2")), 10, r, 0.9, 0.3), i, 0, 0.28, 0.8)
    m.bed(loop_river(r, m, 1.0), 0, 0.35, 0.25)
    return m, make_ir(r, 8.0, 0.05, 3500, 900), -17


def drums_kit(r):
    return {
        "kick": kick(N(0.6)),
        "frame": [frame_drum(N(0.4), r, f) for f in (165, 172, 160)],
        "tom": [tom(N(0.5), f, r) for f in (140, 115, 95, 80)],
        "taiko": taiko(N(1.4), r),
    }


_BR = {}


def brass_c(f, d, r, **kw):
    k = (round(f, 2), round(d, 3), tuple(sorted(kw.items())))
    if k not in _BR:
        _BR[k] = brass(f, d, r, **kw)
    return _BR[k]


def t_boss():
    r = rng_for("boss")
    bpm = 128
    beat = 60 / bpm
    s16 = beat / 4
    bar = 4 * beat
    bars = 40
    m = Mix(bars * bar)
    kit = drums_kit(r)
    osti = [0, 0, 12, 0, 1, 0, 3, 1]
    chords = [[50, 53, 57], [51, 55, 58], [50, 53, 57], [48, 51, 55]]
    for b in range(bars):
        sec = b // 8
        t0 = b * bar
        fill = b % 4 == 3
        if sec != 3:
            for s in ([0, 6, 8] + ([10] if b % 2 else [])):
                m.add(kit["kick"], t0 + s * s16, 0, 0.9, 0.1)
            for s in (4, 12):
                if not (fill and s == 12):
                    m.add(kit["frame"][int(r.integers(3))], t0 + s * s16, 0.1, 0.55, 0.25)
            for s in range(0, 16, 2):
                m.add(ffilt(r.standard_normal(N(0.05)), hp(6000)) * expenv(N(0.05), 0.012), t0 + s * s16, -0.3, 0.08 + 0.05 * (s % 4 == 2), 0.1)
        if b % 2 == 0:
            m.add(kit["taiko"], t0, 0, 0.8, 0.35)
        if fill or sec == 3:
            for s in range(8 if fill else 12, 16):
                m.add(kit["tom"][min(3, (s - 8) // 2)], t0 + s * s16, -0.4 + 0.1 * (s % 8), 0.6, 0.25)
        if sec in (0, 1, 2, 4) or (sec == 3 and b % 2 == 0):
            for i, o in enumerate(osti):
                root = 38 + (1 if (b % 8) in (2, 6) and sec != 0 else 0)
                m.add(brass_c(mtof(root + o), beat / 2 * 0.9, r, att=0.01, rel=0.05, bright=700), t0 + i * beat / 2, 0, 0.45, 0.1)
        if sec in (1, 2, 4) and b % 2 == 0:
            ch = chords[(b // 2) % 4]
            for i, c in enumerate(ch):
                m.add(brass_c(mtof(c - 12), 2 * bar, r, att=0.15, rel=0.4, bright=1000), t0, -0.4 + 0.4 * i, 0.32, 0.35)
        if sec == 3 and b % 4 == 0:
            ch = chords[(b // 2) % 4]
            m.add(choir(mtof([c for c in ch] + [ch[0] + 12]), 4 * bar, [(0, "a"), (7, "o")], r, 1.5, 2, 0.85), t0, 0, 0.5, 0.5)
    base = pcs(2, [0, 1, 3, 5, 7, 8, 10])
    ch_seq = [chords[(b // 2) % 4] for b in range(bars)]
    for bars_ in (range(16, 24), range(32, 40)):
        for b, st, du, x in melody(r, ch_seq, base, list(bars_), [[(0, 4), (4, 4)], [(0, 2), (2, 2), (4, 4)], [(0, 6), (6, 2)]],
                                   nm("D5"), nm("D6"), beat / 2, 8):
            play_cimbal(m, r, b * bar + st, du, x, 0.75, du >= beat, 0.06, 0.3, 0.42, 0.25)
    return m, make_ir(r, 2.5, 0.02, 6000, 2000), -14


def t_final_boss():
    r = rng_for("final_boss")
    bpm = 112
    beat = 60 / bpm
    s16 = beat / 4
    bar = 4 * beat
    bars = 44
    m = Mix(bars * bar)
    kit = drums_kit(r)
    prog = [[50, 53, 57], [51, 55, 58], [50, 53, 57], [49, 52, 55], [46, 50, 53], [45, 49, 52]]
    chords = [prog[(b // 2) % 6] for b in range(bars)]
    for b in range(bars):
        t0 = b * bar
        sec = 0 if b < 8 else (1 if b < 24 else (2 if b < 32 else 3))
        ch = chords[b]
        if b % 2 == 0:
            v = [c for c in ch] + [ch[0] + 12, ch[2] + 12]
            m.add(choir(mtof(v), 2 * bar + 2, [(0, "a"), (2 * bar, "o")], r, 1.2 if sec else 2.5, 2.0, 0.85, 0.1, 3),
                  t0 - 0.5, 0, 0.45 if sec != 2 else 0.6, 0.5)
            m.add(brass_c(mtof(ch[0] - 24), 2 * bar, r, att=0.2, rel=0.5, bright=500), t0, 0, 0.45 if sec else 0.3, 0.3)
        if sec in (1, 3) or b % 2 == 0:
            m.add(bell(mtof(ch[0] - 12), 5, r, 0.8, 0.3), t0, -0.2, 0.3, 0.5)
        if sec in (1, 3):
            for bt in (0, 2):
                m.add(kit["taiko"], t0 + bt * beat, 0, 0.85, 0.35)
            for s in (3, 6, 10, 14):
                m.add(kit["kick"], t0 + s * s16, 0, 0.6, 0.1)
            for s in (4, 12):
                m.add(kit["frame"][int(r.integers(3))], t0 + s * s16, 0.15, 0.5, 0.3)
            if b % 4 == 3:
                for s in range(8, 16):
                    m.add(kit["tom"][(s - 8) // 2], t0 + s * s16, -0.3 + 0.1 * (s - 8), 0.55, 0.3)
            m.add(bell(mtof(ch[2] + 12), 3, r, 0.6, 0.15), t0 + 2 * beat, 0.4, 0.12, 0.5)
        elif sec == 0 and b % 2 == 0:
            m.add(kit["taiko"], t0, 0, 0.7, 0.5)
        else:
            h = thud(58, 36, N(0.6), 0.18, 0.004)
            for bt in range(4):
                m.add(h, t0 + bt * beat, 0, 0.8, 0.15)
                m.add(h * 0.5, t0 + bt * beat + 0.2, 0, 0.8, 0.15)
    base = pcs(2, [0, 1, 3, 5, 7, 8, 10])
    for b, st, du, x in melody(r, chords, base, list(range(32, 44)), [[(0, 4), (4, 4)], [(0, 6), (6, 2)], [(0, 2), (2, 2), (4, 4)]],
                               nm("A4"), nm("A5"), beat / 2, 8, phrase=12):
        play_cimbal(m, r, b * bar + st, du, x, 0.7, du >= beat, 0.065, 0.3, 0.4, 0.3)
    return m, make_ir(r, 4.0, 0.03, 4500, 1300), -14


def t_victory_sting():
    r = rng_for("victory_sting")
    m = Mix(6.5, loop=False, tail=1.5)
    notes = [nm(s) for s in ("D4", "F#4", "A4", "D5", "E5", "F#5", "A5")]
    for i, x in enumerate(notes):
        play_cimbal(m, r, 0.1 + 0.11 * i, 0.3, x, 0.75, False, pan=-0.3 + 0.1 * i, g=0.5, rev=0.35)
    play_cimbal(m, r, 0.95, 2.2, nm("D6"), 0.7, True, 0.07, 0.2, 0.45, 0.4)
    for i, x in enumerate(("D3", "A3", "D4", "F#4")):
        play_cimbal(m, r, 1.0 + 0.03 * i, 3.0, nm(x), 0.7, False, g=0.4, rev=0.4, t60=4.0)
    m.add(choir(mtof([nm(s) for s in ("D3", "A3", "D4", "F#4", "A4")]), 6.5, [(0, "o"), (6, "a")], r, 1.0, 3.5, 0.95), 0.8, 0, 0.5, 0.5)
    m.add(bell(mtof(nm("D4")), 7, r, 0.8, 0.25), 0.95, -0.3, 0.35, 0.6)
    m.add(bell(mtof(nm("A4")), 6, r, 0.7, 0.2), 1.6, 0.3, 0.2, 0.6)
    m.add(ks(mtof(nm("D2")), 6.0, 5.0, 0.3, 1200, 0.2), 0.95, 0, 0.8, 0.3)
    return m, make_ir(r, 3.0, 0.02, 6000, 1800), -15


def t_death_sting():
    r = rng_for("death_sting")
    m = Mix(4.8, loop=False, tail=1.2)
    m.add(bell(mtof(nm("D2")), 6.0, r, 1.0, 0.35), 0.05, 0, 0.6, 0.6)
    for i, s in enumerate(("D5", "C5", "Bb4", "A4", "G4", "Eb4", "D4")):
        play_cimbal(m, r, 0.6 + 0.42 * i + 0.05 * i * i, 0.4, nm(s), 0.55 - 0.04 * i, False, pan=0.2, g=0.45, rev=0.5)
    m.add(choir(mtof([nm("D2"), nm("A2"), nm("D3"), nm("F3")]), 5.6, [(0, "o"), (5, "u")], r, 1.5, 2.5, 0.85), 0.3, 0, 0.45, 0.5)
    m.add(ffilt(loop_drone(r, m, mtof(nm("D1")), "sine", am=0), lp(200))[0:N(6)] * swell(N(6), 0.5, 3, 1), 0, 0, 0.3, 0.1)
    return m, make_ir(r, 4.0, 0.03, 4000, 1200), -15


TRACKS = {
    "menu": t_menu, "town_hora": t_town_hora, "town_pribram": t_town_pribram, "town_jachymov": t_town_jachymov,
    "town_nav": t_town_nav, "mine_1": t_mine_1, "mine_2": t_mine_2, "mine_3": t_mine_3, "mine_4": t_mine_4,
    "boss": t_boss, "final_boss": t_final_boss, "victory_sting": t_victory_sting, "death_sting": t_death_sting,
}


def render_track(name):
    m, ir, target = TRACKS[name]()
    out = m.render(ir, target, 1.2 if not m.loop else None)
    if m.loop:
        out = np.roll(out, N(0.06), axis=1)
    return out, m.loop
