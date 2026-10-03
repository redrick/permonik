import zlib
import numpy as np

SR = 44100
TAU = 2 * np.pi


def N(d):
    return int(round(d * SR))


def tt(n):
    return np.arange(n) / SR


def rng_for(name, salt=0):
    return np.random.default_rng(zlib.crc32(f"{name}:{salt}".encode()))


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, float) - 69) / 12)


NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def nm(s):
    acc = s[1:-1]
    return 12 * (int(s[-1]) + 1) + NOTE[s[0]] + acc.count("#") - acc.count("b")


# ---------- filters ----------

def lp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order))


def hp(fc, order=2):
    return lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order))


def bp(fc, q=1.0):
    return lambda f: 1 / np.sqrt(1 + q * q * (f / fc - fc / np.maximum(f, 1e-3)) ** 2)


def peaks(spec, floor=0.0):
    def g(f):
        out = np.full_like(f, floor, dtype=float)
        for fc, bw, db in spec:
            out = out + 10 ** (db / 20) / np.sqrt(1 + ((f - fc) / (bw / 2)) ** 2)
        return out
    return g


def chain(*fns):
    def g(f):
        out = np.ones_like(f, dtype=float)
        for h in fns:
            out = out * h(f)
        return out
    return g


def ffilt(x, fn, circular=False, pad=8192):
    x = np.asarray(x, float)
    if not circular:
        x = np.pad(x, [(0, 0)] * (x.ndim - 1) + [(pad, pad)])
    n = x.shape[-1]
    f = np.fft.rfftfreq(n, 1 / SR)
    y = np.fft.irfft(np.fft.rfft(x) * fn(f), n)
    return y if circular else y[..., pad:-pad]


def tvfilt(x, fn, win=2048):
    """Time-varying zero-phase filter: fn(t[frames,1], f[1,bins]) -> gain."""
    x = np.asarray(x, float)
    n = len(x)
    hop = win // 2
    xp = np.pad(x, (win, win + hop + (-(n + 2 * win + hop)) % hop))
    nfr = (len(xp) - win) // hop + 1
    idx = np.arange(win)[None, :] + hop * np.arange(nfr)[:, None]
    w = np.hanning(win + 1)[:-1]
    fr = xp[idx] * w
    t = (np.arange(nfr) * hop + hop - win) / SR
    f = np.fft.rfftfreq(win, 1 / SR)
    G = fn(t[:, None], f[None, :])
    Y = np.fft.irfft(np.fft.rfft(fr, axis=1) * G, win, axis=1)
    blocks = Y[:, :hop].copy()
    blocks[1:] += Y[:-1, hop:]
    out = blocks.ravel()
    return out[win:win + n]


def resample_down(y, r):
    m = len(y) // r
    y = y[: m * r]
    X = np.fft.rfft(y)
    k = m // 2 + 1
    f = np.arange(k) / (m / SR)
    X = X[:k] * lp(0.45 * SR, 8)(f)
    return np.fft.irfft(X, m) / r


def conv(x, h, circular=False):
    if circular:
        n = x.shape[-1]
        hh = np.zeros(h.shape[:-1] + (n,))
        hh[..., : h.shape[-1]] = h
        return np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(hh), n)
    n = x.shape[-1] + h.shape[-1]
    m = 1 << int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(h, m), m)[..., : x.shape[-1]]


# ---------- envelopes / generators ----------

def expenv(n, tau, att=0.002):
    t = tt(n)
    e = np.exp(-t / tau)
    if att > 0:
        e *= np.minimum(1, t / att)
    return e


def adsr(n, a, d, s, r):
    t = tt(n)
    T = n / SR
    e = np.where(t < a, t / max(a, 1e-6), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-6)))
    rel = np.clip((T - t) / max(r, 1e-6), 0, 1)
    return e * rel


def swell(n, a, r, shape=2.0):
    t = tt(n)
    T = n / SR
    up = np.clip(t / a, 0, 1)
    dn = np.clip((T - t) / r, 0, 1)
    return (np.sin(up * np.pi / 2) * np.sin(dn * np.pi / 2)) ** shape


def fade(x, a=0.002, r=0.01):
    x = x.copy()
    na, nr = max(N(a), 1), max(N(r), 1)
    x[..., :na] *= np.linspace(0, 1, na)
    x[..., -nr:] *= np.linspace(1, 0, nr)
    return x


def sweep(f0, f1, n, curve="exp"):
    T = n / SR
    t = tt(n)
    if curve == "exp":
        return f0 * (f1 / f0) ** (t / T)
    return f0 + (f1 - f0) * t / T


def sine(freq, n=None, ph=0.0):
    if np.isscalar(freq):
        return np.sin(TAU * freq * tt(n) + ph)
    return np.sin(TAU * np.cumsum(freq) / SR + ph)


def _phase(freq, n, ph):
    if np.isscalar(freq):
        freq = np.full(n, float(freq))
    p = (np.cumsum(freq) / SR + ph) % 1.0
    return p, freq / SR


def _blep(p, dt):
    r = np.zeros_like(p)
    m = p < dt
    x = p[m] / dt[m]
    r[m] = x + x - x * x - 1
    m = p > 1 - dt
    x = (p[m] - 1) / dt[m]
    r[m] = x * x + x + x + 1
    return r


def saw(freq, n=None, ph=0.0):
    if n is None:
        n = len(freq)
    p, dt = _phase(freq, n, ph)
    return 2 * p - 1 - _blep(p, dt)


def pulse(freq, n=None, duty=0.5, ph=0.0):
    if n is None:
        n = len(freq)
    p, dt = _phase(freq, n, ph)
    q = (p + duty) % 1.0
    return (2 * p - 1 - _blep(p, dt)) - (2 * q - 1 - _blep(q, dt))


def noise(rng, n):
    return rng.standard_normal(n)


def brown(rng, n):
    x = np.cumsum(rng.standard_normal(n))
    return ffilt(x - x.mean(), hp(20, 1)) / np.sqrt(n) * 0.5


def slow_noise(rng, n, rate):
    k = max(int(n / SR * rate) + 3, 4)
    pts = rng.standard_normal(k)
    xs = np.linspace(0, n, k)
    return np.interp(np.arange(n), xs, pts)


def modal(freqs, amps, decays, n, rng=None, att=0.0005):
    t = tt(n)
    out = np.zeros(n)
    for f, a, d in zip(freqs, amps, decays):
        if f < SR * 0.45:
            ph = 0 if rng is None else rng.uniform(0, TAU)
            out += a * np.sin(TAU * f * t + ph) * np.exp(-t / d)
    return out * np.minimum(1, t / att)


def thud(f0, f1, n, tau, att=0.001):
    return sine(sweep(f0, f1, n)) * expenv(n, tau, att)


def grit(rng, n, density, fn, tau=None):
    imp = (rng.random(n) < density / SR) * rng.standard_normal(n)
    y = ffilt(imp, fn)
    if tau:
        y *= expenv(n, tau, 0)
    return y


def place(dst, src, t0, g=1.0):
    s = N(t0)
    if s >= len(dst):
        return
    m = min(len(src), len(dst) - s)
    dst[s:s + m] += g * src[:m]


def softclip(x, th=0.6, ceil=0.89):
    a = np.abs(x)
    y = np.where(a < th, a, th + (ceil - th) * np.tanh((a - th) / (ceil - th)))
    return np.sign(x) * y


# ---------- instruments ----------

_KS_CACHE = {}


def ks(f, dur, t60=2.0, p=0.25, bright=4000.0, pos=0.13, rng=None, seed=0, nz=0.25):
    key = (round(float(f), 2), round(dur, 3), round(t60, 3), round(p, 3), round(bright), round(pos, 3), seed, nz)
    if key in _KS_CACHE:
        return _KS_CACHE[key]
    r = 4
    sr = SR * r
    n = int(dur * sr)
    D = sr / f
    Nd = max(int(round(D - 1)), 4)
    g = 10 ** (-3 * (Nd + 1) / (sr * t60))
    lr = np.random.default_rng(int(abs(f) * 1000) + seed * 7919)
    x = np.arange(Nd) / Nd
    tri = np.where(x < pos, x / pos, (1 - x) / (1 - pos))
    e = tri + nz * lr.standard_normal(Nd)
    k = max(int(sr / bright), 1)
    e = np.convolve(np.concatenate([e, e, e]), np.ones(k) / k, "same")[Nd:2 * Nd]
    e -= e.mean()
    e /= np.max(np.abs(e)) + 1e-9
    buf = np.zeros(n + 2)
    buf[2:2 + Nd] = e[: min(Nd, n)]
    k0 = 2 + Nd
    while k0 < n + 2:
        e2 = min(k0 + Nd, n + 2)
        m = e2 - k0
        a = k0 - Nd
        buf[k0:e2] = g * (p * buf[a:a + m] + (1 - 2 * p) * buf[a - 1:a - 1 + m] + p * buf[a - 2:a - 2 + m])
        k0 = e2
    y = resample_down(buf[2:], r)
    y *= fade_tail(len(y))
    _KS_CACHE[key] = y
    return y


def fade_tail(n, r=0.05):
    e = np.ones(n)
    k = min(N(r), n)
    e[-k:] = np.linspace(1, 0, k)
    return e


def cimbal(f, dur=2.5, vel=0.8, t60=2.2, var=0):
    br = 2500 + 8000 * round(min(vel, 1.0) * 6) / 6
    a = ks(f, dur, t60, 0.2, br, 0.11, seed=var, nz=0.6)
    b = ks(f * 1.0025, dur, t60 * 0.9, 0.2, br, 0.13, seed=var + 11, nz=0.6)
    c = ks(f * 0.9978, dur, t60 * 1.1, 0.22, br, 0.09, seed=var + 23, nz=0.6)
    y = a + 0.8 * b + 0.6 * c
    k = N(0.004)
    hr = np.random.default_rng(var + 101).standard_normal(k) * np.exp(-np.arange(k) / (k / 4))
    y[:k] += 0.5 * vel * np.convolve(hr, [1, 0, -1], "same")
    return vel * y / 2.4


def bell(f, dur, rng, bright=1.0, strike=0.3):
    n = N(dur)
    parts = [(0.5, 1.0, 1.0), (1.0, 0.75, 0.55), (1.19, 0.55, 0.42), (1.5, 0.35, 0.32), (2.0, 0.5, 0.28),
             (2.5, 0.22, 0.18), (2.66, 0.2, 0.15), (3.01, 0.18, 0.12), (4.17, 0.12 * bright, 0.08),
             (5.43, 0.08 * bright, 0.05), (6.79, 0.05 * bright, 0.035)]
    out = np.zeros(n)
    t = tt(n)
    for r_, a, d in parts:
        for det in (0.0, rng.uniform(0.0008, 0.002)):
            fr = f * r_ * (1 + det)
            if fr < SR * 0.45:
                out += 0.5 * a * np.sin(TAU * fr * t + rng.uniform(0, TAU)) * np.exp(-t / (d * dur))
    s = ffilt(rng.standard_normal(min(n, N(0.05))), bp(f * 3, 0.7)) * expenv(min(n, N(0.05)), 0.01)
    out[: len(s)] += strike * s / (np.abs(s).max() + 1e-9)
    return out * np.minimum(1, t / 0.002)


VOWELS = {
    "a": [(800, 110, 0), (1150, 120, -5), (2900, 150, -18), (3900, 200, -26)],
    "e": [(450, 90, 0), (1700, 120, -10), (2600, 150, -16), (3500, 200, -24)],
    "i": [(300, 70, 0), (2250, 130, -12), (3000, 160, -14), (3700, 200, -22)],
    "o": [(480, 90, 0), (800, 100, -7), (2830, 150, -20), (3500, 200, -28)],
    "u": [(330, 70, 0), (700, 90, -12), (2500, 170, -26), (3400, 200, -32)],
}


def vowel_fn(keys, fscale=1.0, floor=0.01):
    kt = np.array([k[0] for k in keys], float)
    sp = np.array([VOWELS[k[1]] for k in keys], float)

    def g(t, f):
        out = np.full(np.broadcast(t, f).shape, floor)
        for i in range(sp.shape[1]):
            fc = np.interp(t, kt, sp[:, i, 0]) * fscale
            bw = np.interp(t, kt, sp[:, i, 1]) * fscale
            db = np.interp(t, kt, sp[:, i, 2])
            out = out + 10 ** (db / 20) / np.sqrt(1 + ((f - fc) / (bw / 2)) ** 2)
        return out
    return g


def voice(f0, keys, rng, rough=0.0, breath=0.05, fscale=1.0, jitter=0.01, win=2048):
    n = len(f0)
    f = f0 * (1 + jitter * slow_noise(rng, n, 25))
    src = saw(f)
    if rough > 0:
        sub = np.sin(TAU * np.cumsum(f * 0.5) / SR)
        am = 1 + rough * (0.6 * sub + 0.4 * slow_noise(rng, n, 60))
        src = src * am
    src = src + breath * rng.standard_normal(n)
    return tvfilt(src, vowel_fn(keys, fscale), win)


def choir_src(freqs, n, rng, voices=4, det=0.006, vib=0.004):
    src = np.zeros(n)
    t = tt(n)
    for f in freqs:
        for v in range(voices):
            d = 1 + det * (v - (voices - 1) / 2) / max(voices - 1, 1) * 2 + rng.uniform(-0.001, 0.001)
            vr = rng.uniform(4.5, 5.8)
            fr = f * d * (1 + vib * np.sin(TAU * vr * t + rng.uniform(0, TAU)) * np.minimum(1, t / 0.8))
            src += saw(fr, ph=rng.uniform())
    return src / np.sqrt(len(freqs) * voices)


def choir(freqs, dur, keys, rng, att=1.2, rel=1.5, fscale=1.0, breath=0.08, voices=4):
    n = N(dur)
    src = choir_src(freqs, n, rng, voices)
    src += breath * ffilt(rng.standard_normal(n), hp(1500))
    y = tvfilt(src, vowel_fn(keys, fscale), 4096)
    return y * swell(n, att, rel, 1.5)


def brass(f, dur, rng, att=0.08, rel=0.3, bright=900.0):
    n = N(dur)
    t = tt(n)
    v = 1 + 0.002 * np.sin(TAU * 5 * t)
    x = saw(f * v * 1.004, ph=rng.uniform()) + saw(f * v * 0.996, ph=rng.uniform()) + 0.7 * saw(f * 0.5 * v, ph=rng.uniform())
    dark = ffilt(x, lp(bright, 2))
    blat = ffilt(x, lp(bright * 3, 2))
    k = expenv(n, 0.12, 0)
    y = dark * (1 - k) + blat * k
    return y * adsr(n, att, 0.3, 0.8, rel) / 3


def fiddle(f, dur, rng, att=0.09, rel=0.2, vib=0.006):
    n = N(dur)
    t = tt(n)
    vd = vib * np.clip((t - 0.15) / 0.3, 0, 1)
    fr = f * (1 + vd * np.sin(TAU * 5.6 * t + rng.uniform(0, TAU))) * (1 + 0.002 * slow_noise(rng, n, 8))
    x = saw(fr, ph=rng.uniform())
    x += 0.15 * ffilt(rng.standard_normal(n), bp(3000, 0.7)) * (0.4 + 0.6 * np.exp(-t / 0.1))
    y = ffilt(x, chain(peaks([(290, 120, 0), (520, 200, -2), (1100, 500, -6), (2600, 900, -4), (3600, 900, -9)], 0.08), lp(6000, 2)))
    return y * adsr(n, att, 0.4, 0.85, rel) * 0.5


def reed(freq, n, rng, ph=None):
    x = pulse(freq, n, 0.32, rng.uniform() if ph is None else ph)
    return x


REED_BODY = chain(peaks([(950, 500, 0), (1450, 400, -3), (2500, 700, -8), (350, 200, -6)], 0.12), lp(5500, 2), hp(90, 2))


def dudy_note(f, dur, rng, att=0.04, rel=0.12):
    n = N(dur)
    t = tt(n)
    fr = f * (1 + 0.0025 * np.sin(TAU * 4.8 * t)) * (1 + 0.001 * slow_noise(rng, n, 6))
    y = ffilt(reed(fr, n, rng), REED_BODY)
    return y * adsr(n, att, 0.2, 0.9, rel) * 0.4


def metal(f0, n, rng, decay=1.0, ratios=(1, 2.756, 5.404, 8.933, 13.34), amps=(1, 0.7, 0.5, 0.35, 0.2), click=0.4):
    dec = [decay * d for d in (1, 0.6, 0.35, 0.2, 0.12)]
    y = modal([f0 * r for r in ratios], amps, dec, n, rng)
    y += modal([f0 * r * 1.003 for r in ratios], [a * 0.6 for a in amps], dec, n, rng)
    k = min(n, N(0.004))
    y[:k] += click * rng.standard_normal(k) * np.linspace(1, 0, k)
    return y


def kick(n, f0=110, f1=42, tau=0.3):
    y = thud(f0, f1, n, tau)
    y[: N(0.003)] += np.linspace(0.6, 0, N(0.003)) * np.sign(np.sin(np.arange(N(0.003))))
    return y


def tom(n, f, rng, tau=0.25):
    y = thud(f * 1.4, f, n, tau)
    y += 0.3 * ffilt(rng.standard_normal(n), bp(f * 4, 1)) * expenv(n, 0.04)
    return y


def frame_drum(n, rng, f=170):
    y = thud(f * 1.3, f, n, 0.12)
    y += 0.6 * ffilt(rng.standard_normal(n), chain(bp(1100, 0.8), lp(5000))) * expenv(n, 0.05)
    return y


def taiko(n, rng, f=62):
    y = thud(f * 1.6, f, n, 0.6, 0.004)
    y += 0.5 * ffilt(rng.standard_normal(n), lp(500)) * expenv(n, 0.15)
    return y


def drip(rng, f=None):
    n = N(0.25)
    f = f or rng.uniform(700, 1500)
    fr = f * (1 + 1.2 * (1 - np.exp(-tt(n) / 0.012)))
    return np.sin(TAU * np.cumsum(fr) / SR) * expenv(n, 0.035, 0.001)


def bubble(rng, f, tau=0.03):
    n = N(tau * 5)
    fr = f * (1 + 0.8 * tt(n) / (tau * 5))
    return np.sin(TAU * np.cumsum(fr) / SR) * expenv(n, tau, 0.002)


def creak(rng, dur, rate0=35, rate1=20, fc=(700, 1500)):
    n = N(dur)
    rate = sweep(rate0, rate1, n) * (1 + 0.25 * slow_noise(rng, n, 12))
    ph = np.cumsum(rate) / SR
    imp = np.zeros(n)
    idx = np.nonzero(np.diff(np.floor(ph)) > 0)[0]
    imp[idx] = 1 + 0.3 * rng.standard_normal(len(idx))
    y = ffilt(imp, peaks([(fc[0], 120, 0), (fc[1], 200, -3), (fc[1] * 1.9, 300, -8)]))
    return y * swell(n, 0.05, 0.1, 1)


def make_ir(rng, dur=3.0, pre=0.02, bright=6000, dark=1500, er=8, stereo=True):
    n = N(dur)
    t = tt(n)
    ch = []
    for _ in range(2 if stereo else 1):
        a = ffilt(rng.standard_normal(n), lp(bright, 1)) * np.exp(-t / (dur * 0.12))
        b = ffilt(rng.standard_normal(n), lp(dark, 1)) * np.exp(-t / (dur * 0.2))
        h = 0.4 * a + b
        for _ in range(er):
            k = N(rng.uniform(0.005, 0.08))
            h[k] += rng.uniform(1.0, 3.0) * rng.choice([-1, 1])
        h *= np.minimum(1, t / 0.01)
        h = np.concatenate([np.zeros(N(pre)), h])[:n]
        h /= np.sqrt(np.sum(h * h))
        ch.append(h)
    return np.array(ch)


def kweight_ms(x):
    shelf = lambda f: np.sqrt(1 + (10 ** (4 / 10) - 1) * (f / 1500) ** 2 / (1 + (f / 1500) ** 2))
    y = ffilt(x, chain(shelf, hp(38, 2)), circular=True)
    return np.mean(y * y, axis=-1)


def lufs(x):
    x = np.atleast_2d(x)
    return -0.691 + 10 * np.log10(np.sum(kweight_ms(x)) + 1e-20)
