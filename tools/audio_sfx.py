import numpy as np
from audio_dsp import *


def buf(d):
    return np.zeros(N(d))


def whoosh(rng, dur, f_lo, f_hi, q=1.5, peak=0.55, sharp=3.0):
    n = N(dur)
    T = dur
    x = rng.standard_normal(n)

    def g(t, f):
        u = np.clip(t / T, 0, 1)
        bump = np.sin(np.pi * u ** (np.log(0.5) / np.log(peak))) ** 2
        fc = f_lo + (f_hi - f_lo) * bump
        return bp(1, q)(f / fc)
    y = tvfilt(x, g, 1024)
    u = tt(n) / T
    env = np.sin(np.pi * u ** (np.log(0.5) / np.log(peak))) ** sharp
    return y * env


def room(x, rng, mix=0.15, dur=0.5, dark=3000):
    h = make_ir(rng, dur, 0.005, 6000, dark, 4, stereo=False)[0]
    y = np.concatenate([x, np.zeros(N(dur))])
    return y + mix * conv(y, h) * 0.5


def hall(x, rng, mix=0.35, dur=2.5, dark=1800):
    return room(x, rng, mix, dur, dark)


def tink(rng, f, n, decay=0.15):
    return modal([f, f * 2.32, f * 3.86, f * 5.1], [1, 0.6, 0.35, 0.2],
                 [decay, decay * 0.6, decay * 0.4, decay * 0.25], n, rng)


def shards(rng, dur, count, lo, hi, spread, dmin=0.01, dmax=0.05):
    y = buf(dur)
    for i in range(count):
        t0 = spread * (rng.random() ** 1.6)
        f = rng.uniform(lo, hi)
        d = rng.uniform(dmin, dmax)
        s = modal([f, f * rng.uniform(1.4, 2.1), f * rng.uniform(2.3, 3.2)], [1, 0.5, 0.3], [d, d * 0.7, d * 0.5], N(d * 6), rng)
        place(y, s, t0, rng.uniform(0.3, 1.0) * (1 - 0.6 * t0 / max(spread, 1e-3)))
    return y


def sfx_swing(r):
    return whoosh(r, 0.32, 350, 2600, 1.8, 0.55)


def sfx_swing_heavy(r):
    y = whoosh(r, 0.48, 180, 1300, 1.4, 0.6)
    n = len(y)
    y += 0.5 * sine(sweep(70, 55, n)) * swell(n, 0.25, 0.2, 2)
    return y


def sfx_hit_flesh(r):
    y = buf(0.4)
    place(y, thud(150, 50, N(0.2), 0.07), 0)
    n = N(0.25)
    sq = r.standard_normal(n)
    sq = tvfilt(sq, lambda t, f: bp(1, 2.5)(f / (1300 * np.exp(-t / 0.05) + 280)), 1024) * expenv(n, 0.05)
    place(y, 1.3 * sq, 0.003)
    place(y, 0.6 * ffilt(r.standard_normal(N(0.1)), lp(1500)) * expenv(N(0.1), 0.02), 0)
    return room(y, r, 0.08)


def sfx_hit_bone(r):
    y = buf(0.35)
    place(y, 0.9 * ffilt(r.standard_normal(N(0.03)), hp(2000)) * expenv(N(0.03), 0.004), 0)
    place(y, modal([620, 1340, 2210, 3150], [1, 0.7, 0.5, 0.3], [0.05, 0.035, 0.02, 0.015], N(0.3), r), 0.001)
    place(y, 0.7 * thud(160, 70, N(0.12), 0.04), 0)
    return room(y, r, 0.1)


def sfx_hit_metal(r):
    y = buf(0.9)
    place(y, metal(410, N(0.9), r, 0.35, click=0.8), 0)
    place(y, 0.5 * metal(633, N(0.6), r, 0.2, click=0), 0.002)
    place(y, 0.6 * thud(180, 90, N(0.1), 0.03), 0)
    return room(y, r, 0.12)


def sfx_hit_stone(r):
    y = buf(0.5)
    place(y, thud(110, 45, N(0.25), 0.08), 0)
    place(y, 0.6 * ffilt(r.standard_normal(N(0.2)), lp(900)) * expenv(N(0.2), 0.05), 0)
    place(y, 0.9 * grit(r, N(0.35), 220, bp(2600, 1.2), 0.08), 0)
    return room(y, r, 0.12)


def sfx_block(r):
    y = buf(0.6)
    place(y, metal(720, N(0.6), r, 0.18, click=1.0), 0)
    place(y, 0.8 * thud(200, 100, N(0.1), 0.03), 0)
    place(y, 0.4 * ffilt(r.standard_normal(N(0.05)), hp(3000)) * expenv(N(0.05), 0.01), 0)
    return room(y, r, 0.12)


def grunt(r, f0, f1, dur, keys, rough=0.3, breath=0.12, fscale=1.0, att=0.02, rel=0.15):
    n = N(dur)
    y = voice(sweep(f0, f1, n), keys, r, rough, breath, fscale)
    return y * adsr(n, att, dur * 0.4, 0.6, rel)


def sfx_player_hurt(r):
    y = buf(0.5)
    place(y, grunt(r, 165, 110, 0.38, [(0, "a"), (0.38, "u")], 0.35), 0.01)
    place(y, 0.6 * thud(130, 60, N(0.12), 0.04), 0)
    return room(y, r, 0.1)


def sfx_player_death(r):
    y = buf(2.2)
    place(y, grunt(r, 150, 72, 1.5, [(0, "a"), (0.6, "o"), (1.5, "u")], 0.45, 0.2, att=0.04, rel=0.6), 0)
    place(y, 0.9 * thud(100, 45, N(0.35), 0.1), 1.35)
    place(y, 0.5 * grit(r, N(0.4), 150, bp(1800, 1), 0.1), 1.36)
    place(y, 0.6 * metal(520, N(0.5), r, 0.15, click=0.4), 1.42)
    return room(y, r, 0.25, 1.2)


def sfx_monster_death(r):
    y = buf(1.4)
    n = N(1.2)
    v = voice(sweep(95, 42, n), [(0, "o"), (1.2, "u")], r, 0.9, 0.35, 0.85, 0.03)
    place(y, v * adsr(n, 0.03, 0.4, 0.5, 0.5), 0)
    place(y, 0.6 * thud(90, 40, N(0.3), 0.12), 0.9)
    return room(y, r, 0.2, 1.0)


def sfx_death_bone(r):
    y = buf(1.4)
    place(y, 0.8 * ffilt(r.standard_normal(N(0.03)), hp(1500)) * expenv(N(0.03), 0.006), 0)
    t = 0.02
    gap = 0.11
    for i in range(22):
        f = r.uniform(700, 2800)
        d = r.uniform(0.02, 0.05)
        s = modal([f, f * 2.1, f * 3.3], [1, 0.5, 0.3], [d, d * 0.6, d * 0.4], N(0.2), r)
        place(y, s, t, r.uniform(0.4, 1.0) * np.exp(-t / 0.8))
        t += gap * r.uniform(0.3, 1.2)
        gap *= 0.9
    place(y, 0.5 * thud(140, 80, N(0.1), 0.03), 0.01)
    return room(y, r, 0.15)


def sfx_death_beast(r):
    y = buf(1.4)
    n = N(1.1)
    f0 = np.interp(tt(n), [0, 0.15, 0.4, 1.1], [380, 540, 420, 150])
    v = voice(f0, [(0, "a"), (0.3, "a"), (1.1, "u")], r, 0.6, 0.3, 1.2, 0.02)
    place(y, v * adsr(n, 0.02, 0.4, 0.55, 0.5), 0)
    return room(y, r, 0.2, 1.0)


def sfx_death_ghost(r):
    n = N(2.0)
    t = tt(n)
    f0 = sweep(720, 230, n) * (1 + 0.025 * np.sin(TAU * 6 * t))
    v = voice(f0, [(0, "u"), (1, "o"), (2, "u")], r, 0, 0.5, 1.0, 0.01)
    v = ffilt(v, lp(3000))
    w = ffilt(r.standard_normal(n), bp(900, 0.8)) * 0.3
    y = (v + w) * swell(n, 0.1, 1.3, 1.2)
    return hall(y, r, 0.6, 2.5)


def sfx_boss_roar(r):
    n = N(2.4)
    env = adsr(n, 0.15, 0.8, 0.75, 0.9)
    y = np.zeros(n)
    for f0, fs in ((68, 0.8), (71.5, 0.82), (104, 0.9)):
        f = f0 * np.interp(tt(n), [0, 0.3, 1.6, 2.4], [0.85, 1.1, 1.0, 0.7])
        y += voice(f, [(0, "a"), (1.2, "a"), (2.4, "o")], r, 1.1, 0.5, fs, 0.04)
    y = np.tanh(1.8 * y / np.abs(y).max()) * env
    y += 0.6 * sine(sweep(45, 32, n)) * env
    return hall(y, r, 0.3, 2.0)


def sfx_boss_death(r):
    y = buf(5.0)
    n = N(3.2)
    env = adsr(n, 0.1, 1.0, 0.6, 1.6)
    v = np.zeros(n)
    for f0, fs in ((80, 0.8), (83, 0.82), (121, 0.9)):
        v += voice(sweep(f0, f0 * 0.38, n), [(0, "a"), (1.5, "o"), (3.2, "u")], r, 1.2, 0.5, fs, 0.05)
    v = np.tanh(1.6 * v / np.abs(v).max()) * env
    place(y, v, 0)
    m = N(4.5)
    place(y, 0.7 * ffilt(r.standard_normal(m), lp(180)) * swell(m, 1.5, 2.5, 1), 0.3)
    place(y, 0.8 * grit(r, N(2.5), 90, chain(bp(1200, 0.6), lp(4000)), 1.2), 1.8)
    place(y, 1.0 * thud(80, 32, N(0.8), 0.3), 2.6)
    return hall(y, r, 0.35, 3.0)


def crackle(r, n, density, tau=None):
    return grit(r, n, density, chain(hp(1500), lp(9000)), tau)


def sfx_fire_cast(r):
    n = N(0.75)
    x = r.standard_normal(n)
    y = tvfilt(x, lambda t, f: lp(250 + 3500 * np.clip(t / 0.45, 0, 1), 2)(f), 1024) * swell(n, 0.35, 0.35, 1.5)
    y += 0.6 * crackle(r, n, 120) * swell(n, 0.2, 0.4, 1)
    y += 0.4 * sine(sweep(60, 90, n)) * swell(n, 0.3, 0.3, 2)
    return room(y, r, 0.1)


def sfx_fire_hit(r):
    n = N(0.9)
    y = ffilt(r.standard_normal(n), lp(2800)) * expenv(n, 0.18, 0.004)
    y += 0.9 * thud(110, 40, n, 0.15)
    y += 0.7 * crackle(r, n, 200, 0.3)
    return room(y, r, 0.15)


def sfx_lightning_cast(r):
    n = N(0.55)
    hold = np.repeat(r.uniform(70, 230, n // N(0.012) + 2), N(0.012))[:n]
    y = ffilt(saw(hold), chain(hp(500), lp(7000))) * 0.5
    y += 0.8 * grit(r, n, 400, hp(3000))
    y *= swell(n, 0.04, 0.25, 1) * (0.6 + 0.4 * (r.random(n) > 0.15))
    return room(y, r, 0.1)


def sfx_lightning_hit(r):
    y = buf(1.8)
    k = N(0.04)
    place(y, 1.4 * r.standard_normal(k) * expenv(k, 0.008), 0)
    n = N(1.7)
    rum = ffilt(r.standard_normal(n), lp(260, 2))
    am = 0.5 + np.abs(slow_noise(r, n, 14))
    place(y, 2.5 * rum * am * swell(n, 0.03, 1.4, 1), 0.01)
    place(y, 0.5 * grit(r, N(0.3), 600, hp(2500), 0.06), 0)
    return room(y, r, 0.25, 1.5)


def sfx_frost_cast(r):
    y = buf(0.95)
    for i in range(14):
        f = r.uniform(2200, 7000)
        place(y, 0.4 * modal([f, f * 2.01], [1, 0.3], [0.12, 0.06], N(0.4), r), r.uniform(0, 0.55))
    n = N(0.9)
    place(y, 0.5 * ffilt(r.standard_normal(n), hp(4000)) * swell(n, 0.3, 0.5, 1.5), 0)
    return room(y, r, 0.25, 0.8)


def sfx_frost_hit(r):
    y = buf(0.75)
    place(y, shards(r, 0.75, 34, 2800, 9000, 0.25, 0.01, 0.04), 0)
    place(y, 0.8 * ffilt(r.standard_normal(N(0.03)), hp(1800)) * expenv(N(0.03), 0.006), 0)
    place(y, 0.5 * thud(150, 70, N(0.1), 0.03), 0)
    return room(y, r, 0.15)


def sfx_explosion(r):
    y = buf(2.6)
    n = N(2.4)
    place(y, 1.2 * thud(95, 26, n, 0.5, 0.003), 0)
    place(y, ffilt(r.standard_normal(n), lp(900, 1)) * expenv(n, 0.5, 0.004), 0)
    place(y, 1.2 * r.standard_normal(N(0.06)) * expenv(N(0.06), 0.015), 0)
    place(y, 0.5 * grit(r, N(1.5), 60, bp(1500, 0.7), 0.6), 0.25)
    y = np.tanh(1.5 * y / np.abs(y).max())
    return hall(y, r, 0.25, 2.0)


def sfx_arrow_shot(r):
    y = buf(0.5)
    place(y, 1.0 * ks(98, 0.4, 0.25, 0.3, 3000, 0.2), 0)
    place(y, 0.5 * ffilt(r.standard_normal(N(0.01)), hp(2000)) * expenv(N(0.01), 0.002), 0)
    place(y, 0.6 * whoosh(r, 0.18, 1500, 5000, 2, 0.4), 0.02)
    return room(y, r, 0.08)


def sfx_bolt_shot(r):
    y = buf(0.55)
    place(y, 0.9 * ffilt(r.standard_normal(N(0.012)), hp(2500)) * expenv(N(0.012), 0.003), 0)
    place(y, 0.8 * thud(220, 80, N(0.12), 0.04), 0.008)
    place(y, 0.9 * ks(73, 0.45, 0.2, 0.3, 2500, 0.25), 0.01)
    place(y, 0.6 * metal(1900, N(0.15), r, 0.04, click=0.2), 0.0)
    place(y, 0.5 * whoosh(r, 0.2, 1200, 4000, 2, 0.4), 0.03)
    return room(y, r, 0.08)


def sfx_axe_throw(r):
    n = N(0.7)
    x = r.standard_normal(n)
    y = tvfilt(x, lambda t, f: bp(1, 2.2)(f / (1100 - 400 * t)), 1024)
    t = tt(n)
    y *= ((0.5 + 0.5 * np.sin(TAU * 13 * t)) ** 3) * swell(n, 0.2, 0.35, 1.5)
    return room(y, r, 0.08)


def sfx_potion(r):
    y = buf(0.9)
    place(y, 0.6 * ffilt(r.standard_normal(N(0.02)), bp(1200, 2)) * expenv(N(0.02), 0.004), 0)
    t = 0.08
    for i in range(6):
        place(y, bubble(r, r.uniform(280, 520), 0.035), t, 0.9)
        t += r.uniform(0.08, 0.13)
    n = N(0.75)
    place(y, 0.25 * ffilt(r.standard_normal(n), chain(lp(1200), hp(200))) * swell(n, 0.1, 0.2, 1), 0.07)
    return room(y, r, 0.1)


def sfx_gold(r):
    y = buf(0.7)
    for i in range(8):
        place(y, tink(r, r.uniform(2400, 4200), N(0.4), r.uniform(0.08, 0.2)), 0.25 * r.random() ** 1.3, r.uniform(0.4, 1))
    return room(y, r, 0.1)


def sfx_pickup(r):
    y = buf(0.25)
    n = N(0.08)
    place(y, 0.6 * ffilt(r.standard_normal(n), bp(2200, 1.2)) * swell(n, 0.02, 0.05, 1), 0)
    place(y, 0.7 * thud(170, 120, N(0.08), 0.025), 0.03)
    place(y, 0.4 * modal([2400, 3600], [1, 0.4], [0.02, 0.01], N(0.1), r), 0.05)
    return y


def sfx_drop_item(r):
    y = buf(0.35)
    place(y, thud(130, 60, N(0.2), 0.05), 0)
    place(y, 0.4 * grit(r, N(0.15), 300, bp(2200, 1.2), 0.04), 0)
    place(y, 0.25 * metal(1300, N(0.25), r, 0.06, click=0), 0.003)
    return room(y, r, 0.1)


def sfx_equip(r):
    y = buf(0.45)
    place(y, 0.7 * tink(r, 1800, N(0.3), 0.07), 0)
    place(y, 0.5 * tink(r, 2350, N(0.3), 0.05), 0.07)
    place(y, 0.5 * creak(r, 0.25, 60, 40, (900, 1800)), 0.1)
    place(y, 0.5 * thud(160, 110, N(0.06), 0.02), 0.02)
    return room(y, r, 0.1)


def sfx_levelup(r):
    y = buf(2.4)
    notes = [nm(s) for s in ("D4", "F#4", "A4", "D5", "F#5", "A5")]
    for i, m in enumerate(notes):
        place(y, cimbal(mtof(m), 2.0, 0.8, 1.8, i), 0.065 * i)
    place(y, 0.3 * bell(mtof(nm("D6")), 2.0, r, 0.6, 0.1), 0.4)
    place(y, 0.25 * bell(mtof(nm("A5")), 2.0, r, 0.6, 0.1), 0.42)
    return hall(y, r, 0.3, 2.0)


def sfx_quest_done(r):
    y = buf(3.0)
    for i, s in enumerate(("A3", "C#4", "E4", "G4")):
        place(y, cimbal(mtof(nm(s)), 1.5, 0.7, 1.4, i), 0.04 * i)
    for i, s in enumerate(("D3", "D4", "F#4", "A4", "D5")):
        place(y, cimbal(mtof(nm(s)), 2.4, 0.8, 2.2, i + 4), 0.55 + 0.035 * i)
    place(y, 0.35 * bell(mtof(nm("D4")), 2.6, r, 0.7, 0.15), 0.55)
    return hall(y, r, 0.3, 2.0)


def sfx_chest_open(r):
    y = buf(1.2)
    place(y, 0.8 * metal(1500, N(0.15), r, 0.03, click=0.6), 0)
    place(y, creak(r, 0.75, 42, 18, (650, 1500)), 0.08)
    place(y, 0.7 * thud(140, 80, N(0.2), 0.05), 0.85)
    place(y, 0.3 * grit(r, N(0.1), 300, bp(2000, 1), 0.03), 0.85)
    return room(y, r, 0.15)


def wood_knock(r, f, d=0.06):
    return modal([f, f * 1.58, f * 2.4, f * 3.7], [1, 0.6, 0.35, 0.2], [d, d * 0.7, d * 0.5, d * 0.3], N(d * 6), r)


def sfx_barrel_break(r):
    y = buf(1.1)
    place(y, 1.0 * ffilt(r.standard_normal(N(0.05)), chain(hp(400), lp(6000))) * expenv(N(0.05), 0.012), 0)
    place(y, 0.8 * thud(150, 70, N(0.2), 0.06), 0)
    t = 0.03
    for i in range(10):
        place(y, wood_knock(r, r.uniform(180, 520), r.uniform(0.04, 0.08)), t, r.uniform(0.4, 1.0) * np.exp(-t / 0.6))
        t += r.uniform(0.03, 0.11)
    place(y, 0.5 * grit(r, N(0.4), 300, hp(2500), 0.12), 0)
    return room(y, r, 0.15)


def sfx_urn_break(r):
    y = buf(0.9)
    place(y, 0.7 * thud(200, 90, N(0.1), 0.03), 0)
    place(y, 0.6 * modal([880, 1530, 2470], [1, 0.6, 0.4], [0.03, 0.02, 0.015], N(0.2), r), 0)
    place(y, shards(r, 0.9, 28, 1800, 6000, 0.4, 0.02, 0.07), 0.01)
    return room(y, r, 0.15)


def sfx_shrine(r):
    y = buf(3.2)
    ch = choir(mtof([nm("D3"), nm("A3"), nm("F4"), nm("E5")]), 2.8, [(0, "o"), (2.8, "a")], r, 0.8, 1.4, 1.0)
    place(y, ch, 0)
    place(y, 0.4 * bell(mtof(nm("A5")), 2.5, r, 0.7, 0.1), 0.6)
    n = N(2.4)
    place(y, 0.15 * ffilt(r.standard_normal(n), hp(5000)) * swell(n, 0.8, 1.2, 1), 0.3)
    return hall(y, r, 0.45, 2.8)


def sfx_portal(r):
    n = N(1.9)
    t = tt(n)
    x = r.standard_normal(n)
    y = tvfilt(x, lambda tm, f: bp(1, 3)(f / (800 + 600 * np.sin(TAU * 2.6 * tm))), 1024) * 0.7
    y += 0.4 * (sine(110.0, n) + sine(110.9, n) + 0.6 * sine(165.6, n) + 0.4 * sine(sweep(220, 660, n)))
    y *= swell(n, 0.5, 0.8, 1.3)
    return hall(y, r, 0.4, 2.0)


def sfx_waypoint(r):
    y = buf(2.4)
    place(y, 0.6 * bell(mtof(nm("E5")), 2.2, r, 0.8, 0.15), 0.05)
    place(y, 0.35 * bell(mtof(nm("B5")), 1.8, r, 0.6, 0.1), 0.25)
    place(y, 0.5 * whoosh(r, 0.8, 300, 2000, 1.5, 0.4), 0)
    return hall(y, r, 0.35, 2.2)


def sfx_bell_toll(r):
    y = buf(6.5)
    place(y, bell(mtof(nm("G3")), 6.4, r, 1.0, 0.35), 0)
    return hall(y, r, 0.35, 3.5, 1400)


def sfx_ui_click(r):
    y = buf(0.06)
    place(y, wood_knock(r, 1900, 0.008), 0)
    place(y, 0.4 * r.standard_normal(N(0.002)), 0)
    return y


def sfx_ui_open(r):
    y = buf(0.25)
    n = N(0.18)
    place(y, tvfilt(r.standard_normal(n), lambda t, f: bp(1, 2)(f / (500 + 12000 * t)), 512) * swell(n, 0.08, 0.08, 1), 0)
    place(y, 0.6 * wood_knock(r, 1100, 0.015), 0.16)
    return y


def sfx_ui_close(r):
    y = buf(0.25)
    n = N(0.18)
    place(y, 0.6 * wood_knock(r, 800, 0.015), 0)
    place(y, tvfilt(r.standard_normal(n), lambda t, f: bp(1, 2)(f / (2600 - 11000 * t)), 512) * swell(n, 0.06, 0.1, 1), 0.02)
    return y


def sfx_no_mana(r):
    y = buf(0.45)
    for i, f in enumerate((233, 196)):
        n = N(0.16)
        s = ffilt(saw(f * np.ones(n)) + saw(f * 1.01 * np.ones(n)), lp(700, 2)) * adsr(n, 0.01, 0.05, 0.6, 0.05)
        place(y, s, 0.18 * i)
    return room(y, r, 0.1)


def step(r, f, grit_fc):
    y = buf(0.2)
    place(y, thud(f, f * 0.6, N(0.1), 0.025), 0)
    place(y, 0.7 * grit(r, N(0.12), 500, bp(grit_fc, 1.5), 0.025), 0.002)
    place(y, 0.3 * ffilt(r.standard_normal(N(0.04)), lp(1200)) * expenv(N(0.04), 0.01), 0)
    return room(y, r, 0.12, 0.3)


def sfx_step_stone_1(r):
    return step(r, 105, 2200)


def sfx_step_stone_2(r):
    return step(r, 92, 1800)


def sfx_step_stone_3(r):
    return step(r, 120, 2700)


def splash(r, dur, size):
    y = buf(dur)
    n = N(dur * 0.4)
    place(y, ffilt(r.standard_normal(n), chain(lp(2500 + 1500 * size), hp(150))) * expenv(n, 0.06 + 0.1 * size, 0.003), 0)
    for i in range(int(4 + 10 * size)):
        place(y, bubble(r, r.uniform(500, 1600), r.uniform(0.015, 0.03)), r.uniform(0.02, dur * 0.6), 0.4)
    for i in range(int(2 + 4 * size)):
        place(y, drip(r), r.uniform(0.1, dur * 0.7), 0.25)
    return y


def sfx_water_splash(r):
    return room(splash(r, 1.0, 1.0), r, 0.2)


def sfx_footstep_water(r):
    y = splash(r, 0.35, 0.15)
    place(y, 0.5 * thud(90, 60, N(0.08), 0.02), 0)
    return room(y, r, 0.12, 0.3)


def sfx_coin_bounce(r):
    y = buf(1.0)
    t = 0.0
    gap = 0.2
    a = 1.0
    f = 3100
    while t < 0.75 and a > 0.05:
        place(y, tink(r, f * r.uniform(0.98, 1.02), N(0.3), 0.12), t, a)
        t += gap
        gap *= 0.72
        a *= 0.8
    for i in range(10):
        place(y, tink(r, f, N(0.1), 0.02), t + i * 0.012, 0.2 * (1 - i / 10))
    return room(y, r, 0.12)


def sfx_laugh_permonik(r):
    y = buf(1.4)
    t = 0.0
    pitches = [330, 360, 385, 360, 330, 300, 280]
    durs = [0.11, 0.1, 0.09, 0.085, 0.08, 0.09, 0.16]
    for i, (p, d) in enumerate(zip(pitches, durs)):
        n = N(d)
        f = sweep(p * 1.08, p * 0.92, n)
        v = voice(f, [(0, "e"), (d, "i")], r, 0.15, 0.25, 1.25, 0.02, 1024)
        h = ffilt(r.standard_normal(N(0.03)), hp(2500)) * swell(N(0.03), 0.005, 0.02, 1) * 0.6
        place(y, h, t)
        place(y, v * adsr(n, 0.008, 0.04, 0.5, 0.03), t + 0.02, 1.0 - 0.06 * i)
        t += d + 0.045 + 0.01 * i
    return room(y, r, 0.3, 1.2, 2000)


def sfx_ghost_wail(r):
    n = N(2.6)
    t = tt(n)
    f0 = np.interp(t, [0, 0.8, 1.6, 2.6], [380, 640, 560, 280]) * (1 + 0.02 * np.sin(TAU * 5.2 * t))
    v = ffilt(voice(f0, [(0, "u"), (1.0, "o"), (2.6, "u")], r, 0, 0.6, 1.0, 0.01), lp(3200))
    v2 = ffilt(voice(f0 * 1.5, [(0, "u"), (2.6, "o")], r, 0, 0.3, 1.0, 0.01), lp(3200))
    y = (v + 0.4 * v2) * swell(n, 0.4, 1.0, 1.2)
    return hall(y, r, 0.7, 3.0)


def sfx_wolf_howl(r):
    n = N(2.6)
    t = tt(n)
    f0 = np.interp(t, [0, 0.45, 1.8, 2.6], [320, 560, 545, 400]) * (1 + 0.012 * np.sin(TAU * 5 * t) * np.clip(t - 0.4, 0, 1))
    v = voice(f0, [(0, "u"), (0.5, "o"), (2.0, "o"), (2.6, "u")], r, 0, 0.15, 1.0, 0.006)
    v = ffilt(v, lp(2500))
    y = v * swell(n, 0.35, 0.8, 1.2)
    return hall(y, r, 0.5, 3.0, 2500)


def sfx_cauldron_bubble(r):
    y = buf(1.7)
    for i in range(26):
        place(y, bubble(r, r.uniform(140, 420), r.uniform(0.03, 0.07)), r.uniform(0, 1.5), r.uniform(0.4, 1))
    n = N(1.7)
    place(y, 0.4 * ffilt(r.standard_normal(n), chain(lp(350), hp(40))) * swell(n, 0.2, 0.3, 1), 0)
    return room(y, r, 0.15)


def sfx_chains(r):
    y = buf(1.1)
    for c, t0 in enumerate((0.0, 0.3, 0.62)):
        for i in range(12):
            f = r.uniform(1700, 3600)
            s = tink(r, f, N(0.12), r.uniform(0.02, 0.06))
            place(y, s, t0 + 0.2 * r.random() ** 1.5, r.uniform(0.3, 1.0) * (1 - 0.25 * c))
    n = N(1.0)
    place(y, 0.15 * grit(r, n, 400, bp(3000, 1)) * swell(n, 0.05, 0.4, 1), 0)
    return room(y, r, 0.15)


def sfx_petrify(r):
    y = buf(1.5)
    n = N(1.3)
    g = ffilt(r.standard_normal(n), lp(500)) * (0.6 + 0.4 * np.abs(slow_noise(r, n, 30)))
    place(y, g * swell(n, 0.5, 0.3, 1), 0)
    place(y, 0.6 * grit(r, n, 300, bp(2000, 1)) * np.clip(tt(n) / 1.0, 0, 1) ** 2, 0)
    place(y, 0.5 * sine(sweep(62, 44, n)) * swell(n, 0.4, 0.4, 1), 0)
    place(y, 1.0 * thud(120, 50, N(0.25), 0.07), 1.15)
    place(y, 0.6 * grit(r, N(0.3), 400, bp(2400, 1), 0.06), 1.15)
    return room(y, r, 0.2)


def sfx_heal(r):
    y = buf(1.5)
    for i, s in enumerate(("D5", "F#5", "A5", "D6")):
        n = N(1.2 - 0.12 * i)
        tone = (sine(mtof(nm(s)), n) + 0.2 * sine(mtof(nm(s)) * 2, n)) * (1 + 0.2 * np.sin(TAU * 7 * tt(n)))
        place(y, 0.4 * tone * swell(n, 0.15, 0.6, 1.2), 0.12 * i)
    n = N(1.2)
    place(y, 0.25 * ffilt(r.standard_normal(n), hp(3500)) * swell(n, 0.4, 0.6, 1.5), 0)
    return hall(y, r, 0.3, 1.5)


def sfx_buff(r):
    n = N(0.9)
    f = sweep(110, 220, n)
    x = saw(f) + saw(f * 1.5 * 1.003) + 0.6 * saw(f * 2)
    y = tvfilt(x, lambda t, fr: lp(300 + 5000 * np.clip(t / 0.7, 0, 1), 2)(fr), 1024)
    y *= swell(n, 0.4, 0.35, 1.2) * 0.4
    return hall(y, r, 0.25, 1.2)


def sfx_trap_snap(r):
    y = buf(0.7)
    place(y, 1.0 * ffilt(r.standard_normal(N(0.005)), hp(2000)), 0)
    place(y, 0.8 * metal(950, N(0.5), r, 0.12, click=0.5), 0.002)
    n = N(0.5)
    place(y, 0.5 * sine(180 * (1 + 0.15 * np.sin(TAU * 28 * tt(n)) * np.exp(-tt(n) / 0.15))) * expenv(n, 0.14), 0.01)
    place(y, 0.6 * thud(150, 70, N(0.12), 0.04), 0.003)
    return room(y, r, 0.12)


def sfx_smoke(r):
    n = N(1.2)
    y = ffilt(r.standard_normal(n), chain(lp(1100, 1), hp(80))) * adsr(n, 0.05, 0.35, 0.3, 0.6)
    y += 0.25 * ffilt(r.standard_normal(n), hp(3000)) * swell(n, 0.1, 0.8, 1.5)
    return room(y, r, 0.2)


SFX = [
    "swing", "swing_heavy", "hit_flesh", "hit_bone", "hit_metal", "hit_stone", "block", "player_hurt",
    "player_death", "monster_death", "death_bone", "death_beast", "death_ghost", "boss_roar", "boss_death",
    "fire_cast", "fire_hit", "lightning_cast", "lightning_hit", "frost_cast", "frost_hit", "explosion",
    "arrow_shot", "bolt_shot", "axe_throw", "potion", "gold", "pickup", "drop_item", "equip", "levelup",
    "quest_done", "chest_open", "barrel_break", "urn_break", "shrine", "portal", "waypoint", "bell_toll",
    "ui_click", "ui_open", "ui_close", "no_mana", "step_stone_1", "step_stone_2", "step_stone_3",
    "water_splash", "coin_bounce", "laugh_permonik", "ghost_wail", "wolf_howl", "cauldron_bubble", "chains",
    "petrify", "heal", "buff", "trap_snap", "smoke", "footstep_water",
]


def render_sfx(name):
    r = rng_for(name)
    y = globals()["sfx_" + name](r)
    y = ffilt(y, hp(30, 2))
    y -= y.mean()
    a = np.abs(y)
    th = 10 ** (-58 / 20) * a.max()
    nz_ = np.nonzero(a > th)[0]
    y = y[: nz_[-1] + 1] if len(nz_) else y
    y = fade(y, 0.001, min(0.03, len(y) / SR * 0.2))
    return y / np.abs(y).max() * 10 ** (-3 / 20)
