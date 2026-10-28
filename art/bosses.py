"""All boss sprites and boss portraits. Drawing lives in bosses_act1..4.py and bosses_end.py."""
import common
import bosses_act1, bosses_act2, bosses_act3, bosses_act4, bosses_end

MODS = (bosses_act1, bosses_act2, bosses_act3, bosses_act4, bosses_end)

if __name__ == "__main__":
    import sys
    if "--ids" in sys.argv:
        ids = sys.argv[sys.argv.index("--ids") + 1].split(",")
        del sys.argv[sys.argv.index("--ids"):sys.argv.index("--ids") + 2]
        common.run({"sprites/monsters": [it for m in MODS for it in m.SPRITES
                                         if any(it[0] == i or it[0].startswith(i + "_") for i in ids)]})
    else:
        common.run({"sprites/monsters": [it for m in MODS for it in m.SPRITES],
                    "portraits": [it for m in MODS for it in m.PORTRAITS]})
