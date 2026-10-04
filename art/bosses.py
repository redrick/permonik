"""All boss sprites and boss portraits. Drawing lives in bosses_act1..4.py and bosses_end.py."""
import common
import bosses_act1, bosses_act2, bosses_act3, bosses_act4, bosses_end

MODS = (bosses_act1, bosses_act2, bosses_act3, bosses_act4, bosses_end)

if __name__ == "__main__":
    common.run({"sprites/monsters": [it for m in MODS for it in m.SPRITES],
                "portraits": [it for m in MODS for it in m.PORTRAITS]})
