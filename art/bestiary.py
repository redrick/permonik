import common
from bestiary_kit import sprite
import bestiary_dead as D
import bestiary_beasts as B
import bestiary_folk as F
import bestiary_spirits as Sp

POSES = ("idle", "walk", "walk2", "windup", "attack")

CREATURES = [
    # id, w, h, fn, shadow rx (None = none), flyer shadow rx, lift[, dx]
    ("kostlivy_havir", 192, 192, D.kostlivy_havir, 16, None, 0),
    ("kostlivy_kusinik", 192, 192, D.kostlivy_kusinik, 16, None, 0),
    ("kostejuv_nesmrtelny", 224, 224, D.kostejuv_nesmrtelny, 19, None, 0, -6),
    ("utopenec", 224, 224, D.utopenec, 21, None, 0),
    ("upir", 224, 224, D.upir, 19, None, 0),
    ("navka", 224, 224, D.navka, None, 12, 5),
    ("krysa", 96, 96, B.krysa, 11, None, 0),
    ("vlk", 192, 192, B.vlk, 26, None, 0),
    ("cerny_pes", 192, 192, B.cerny_pes, 27, None, 0),
    ("netopyr", 96, 96, B.netopyr, None, 8, 20),
    ("kamenny_had", 288, 224, B.kamenny_had, 34, None, 0),
    ("vlkodlak", 288, 288, B.vlkodlak, 26, None, 0),
    ("sotek", 128, 128, F.sotek, 10, None, 0),
    ("permonicek", 96, 96, F.permonicek, None, None, 0),
    ("hejkal", 256, 256, F.hejkal, 28, None, 0),
    ("diva_zena", 224, 224, F.diva_zena, 15, None, 0),
    ("cert", 224, 224, F.cert, 17, None, 0, -4),
    ("bludicka", 128, 128, Sp.bludicka, None, 8, 9),
    ("ohnivy_muzik", 128, 128, Sp.ohnivy_muzik, 10, None, 0),
    ("mura", 192, 192, Sp.mura, None, 12, 12),
    ("bubak", 224, 224, Sp.bubak, 22, None, 0, -5),
    ("svetlonos", 224, 224, Sp.svetlonos, None, 14, 5),
    ("smolak", 256, 256, Sp.smolak, 26, None, 0),
    ("bes", 256, 256, Sp.bes, 18, None, 0),
]


def items():
    out = []
    for cid, w, h, fn, sh, fl, lift, *dx in CREATURES:
        for p in POSES:
            out.append((f"{cid}_{p}", w, h, sprite(fn, p, sh, fl, dx[0] if dx else 0, lift)))
    return out


if __name__ == "__main__":
    common.run({"sprites/monsters": items()})
