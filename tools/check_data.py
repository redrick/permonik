#!/usr/bin/env python3
"""Validate game/data/*.json against docs/data-schema.md and docs/assets.md.

Usage: python3 tools/check_data.py [--strict]
Errors in the mechanics files fail the run. Problems in the narrative files (acts, quests,
dialog, lore, slides) are warnings unless --strict, since those may be work in progress.
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "game" / "data"
ASSETS_MD = ROOT / "docs" / "assets.md"

STATS = set("""sila obratnost magie vitalita vse_staty hp mana hp_pct mana_pct dmg_pct dmg_min dmg_max
to_hit armor armor_pct block fire_dmg lightning_dmg cold_dmg poison_dmg res_fire res_lightning res_cold
res_poison res_all life_steal mana_steal attack_speed cast_speed move_speed light_radius gold_find
magic_find hp_regen mana_regen thorns dmg_reduce skills crit xp_pct to_hit_pct crushing_blow
hit_recovery dmg_reduce_pct""".split())
ELEMENTS = {"physical", "fire", "lightning", "cold", "poison"}
SKILL_TYPES = {"melee", "melee_arc", "stomp", "leap", "spin", "projectile", "chain", "nova", "cone",
               "area", "wall", "trap", "summon", "buff", "cloud", "passive"}
STRING_PARAMS = {"fx", "id", "effect", "requires", "look", "tint", "form"}
AI = {"melee", "ranged", "caster", "swarm", "charger", "exploder", "phaser", "thief", "summoner",
      "flyer", "boss"}
SLOTS = {"weapon", "offhand", "head", "body", "belt", "lamp", "ring", "amulet", "consumable",
         "gold", "quest", "gem", "letter", "charm", "key"}
SLOT_GROUPS = {"weapon", "ranged", "offhand", "shield", "head", "body", "belt", "lamp", "ring",
               "amulet", "armor", "jewelry", "any", "class"}
SPEEDS = {"fast", "normal", "slow", "very_slow"}
_classes = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "game", "data", "classes.json")))
CLASS_IDS = set(_classes)
TREE_IDS = {t["id"] for c in _classes.values() for t in c.get("trees", [])}
ROLES = {"smith", "healer", "inn", "chronicler", "guide", "ghost", "other"}
SEALS = {"voda", "kamen", "ohen", "smrt"}
GENDERS = {"m", "f", "n"}
RESIST_KEYS = {"fire", "lightning", "cold", "poison"}
NARRATIVE = ["acts.json", "quests.json", "dialog.json", "lore.json", "slides.json"]
# Monster ids that are engine helpers rather than separately drawn creatures.
MONSTER_HELPERS = {"permonik": "npcs", "san_head": "part of san", "zar_ptak": "fx"}
REQUIRED_UNIQUES = """janosikuv_opasek srdce_zvonu_cep semikova_podkova tremsinsky_prsten fabianova_siska
kosmova_kronika hastrmanuv_hrnek kostnikova_koruna megerina_berla prokopuv_palcat baziliskovo_oko
strzygina_dvojnice ohnivcova_kovadlina jezibabina_lopata sanin_kozich vijova_vicka
kostejova_jehla_unique horymiruv_bic perunova_sekera moranina_naruc_amulet zdar_buh_kahan
karbidka_svatobarborska""".split()

errors, warnings = [], []


def err(where, msg):
    errors.append(f"{where}: {msg}")


def warn(where, msg):
    warnings.append(f"{where}: {msg}")


# ---------------------------------------------------------------- assets.md
def section(md, title):
    m = re.search(r"^### " + re.escape(title) + r".*?$(.*?)(?=^### |\Z)", md, re.S | re.M)
    return m.group(1) if m else ""


def strip_parens(text):
    prev = None
    while prev != text:
        prev, text = text, re.sub(r"\([^()]*\)", "", text)
    return text


def parse_assets():
    md = ASSETS_MD.read_text(encoding="utf-8")
    a = {}
    a["heroes"] = {"havir", "zbojnice", "vedma"}
    a["npcs"] = set(re.findall(r"^\| ([a-z_]+) \|", section(md, "NPCs"), re.M)) - {"id"}

    mon = strip_parens(" ".join(section(md, "Monsters").split()))
    mon = re.sub(r"`[^`]*`", "", mon)
    mon = re.sub(r"\b[A-Z][a-z]+:", "", mon)
    a["monsters"] = set(re.findall(r"\b([a-z][a-z_]*[a-z])\b", mon))

    fx = section(md, "FX").split("Sizes:")[0]
    fx = strip_parens(" ".join(fx.split()))
    a["fx"] = set(re.findall(r"\b([a-z][a-z_]*[a-z])\b", fx))

    a["props_text"] = section(md, "Props")

    items = strip_parens(" ".join(section(md, "Items").split()))
    a["items"] = {}
    for m in re.finditer(r"([A-Z][A-Za-z-]+)\s*(\d×\d)?[^:A-Z]*:\s*([^A-Z]*)", items):
        default = m.group(2)
        for part in m.group(3).split(","):
            mm = re.match(r"\s*([a-z][a-z_0-9]*)\s*(\d×\d)?", part)
            if mm:
                size = mm.group(2) or default
                a["items"][mm.group(1)] = tuple(int(x) for x in size.split("×")) if size else None

    sk = strip_parens(" ".join(section(md, "Skills").split()))
    a["skills"] = set()
    for m in re.finditer(r"\b(havir|zbojnice|vedma|kovar|zrec|vlkodlak|alchymistka|loutkarka|Plus)\b:?\s*([^.]*)", sk):
        a["skills"] |= set(re.findall(r"\b([a-z][a-z_]*[a-z])\b", m.group(2)))
    return a


# ---------------------------------------------------------------- helpers
def load(name, required=True):
    p = DATA / name
    if not p.exists():
        if required:
            err(name, "missing")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        (err if required else warn)(name, f"JSON error: {e}")
        return None


def text(where, v, report=err):
    if not isinstance(v, dict) or set(v) != {"cs", "en"}:
        report(where, f"must be {{cs, en}}, got {v!r:.60}")
        return False
    for lang in ("cs", "en"):
        if not isinstance(v[lang], str) or not v[lang].strip():
            report(where, f"empty {lang}")
    return True


def need(where, obj, keys):
    for k in keys:
        if k not in obj:
            err(where, f"missing field '{k}'")


def num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def check_mods(where, mods, keys=("min", "max")):
    if not isinstance(mods, list):
        err(where, "mods must be a list")
        return
    for i, m in enumerate(mods):
        w = f"{where}.mods[{i}]"
        st = str(m.get("stat"))
        if st not in STATS and not (st.startswith("class_") and st[6:] in CLASS_IDS) \
                and not (st.startswith("tree_") and st[5:] in TREE_IDS):
            err(w, f"unknown stat {m.get('stat')!r}")
        for k in keys:
            if not num(m.get(k)):
                err(w, f"'{k}' must be a number")
        if keys == ("min", "max") and num(m.get("min")) and num(m.get("max")) and m["min"] > m["max"]:
            err(w, "min > max")


# ---------------------------------------------------------------- mechanics files
def check_skills(skills, assets):
    for sid, s in skills.items():
        w = f"skills.{sid}"
        need(w, s, ["class", "tree", "tier", "name", "desc", "type", "element", "mana", "cooldown",
                    "params", "synergy", "max_rank"])
        if sid not in assets["skills"]:
            err(w, "id not in docs/assets.md skill list")
        text(w + ".name", s.get("name"))
        if text(w + ".desc", s.get("desc")):
            params = s.get("params", {})
            for lang in ("cs", "en"):
                for ph in re.findall(r"\{(\w+)\}", s["desc"][lang]):
                    if ph not in params and ph not in ("mana", "cooldown"):
                        err(w, f"desc.{lang} placeholder {{{ph}}} has no param")
            used = set(re.findall(r"\{(\w+)\}", s["desc"]["cs"]))
            if used != set(re.findall(r"\{(\w+)\}", s["desc"]["en"])):
                err(w, "cs and en desc use different placeholders")
        if s.get("type") not in SKILL_TYPES:
            err(w, f"unknown type {s.get('type')!r}")
        if s.get("element") not in ELEMENTS and not (s.get("element") == "holy" and s.get("type") in ("buff", "passive")):
            err(w, f"unknown element {s.get('element')!r}")
        if s.get("tier") not in (1, 2, 3, 4):
            err(w, "tier must be 1..4")
        mana = s.get("mana")
        if not (isinstance(mana, list) and len(mana) == 2 and all(num(x) for x in mana)):
            err(w, "mana must be [base, per_rank]")
        for pk, pv in s.get("params", {}).items():
            pw = f"{w}.params.{pk}"
            if pk in STRING_PARAMS:
                if not isinstance(pv, str):
                    err(pw, "must be a string")
                if pk == "fx" and pv not in assets["fx"]:
                    err(pw, f"fx {pv!r} not in docs/assets.md FX list")
                continue
            if pk == "dmg":
                ok = (isinstance(pv, list) and len(pv) == 2 and
                      all(isinstance(r, list) and len(r) == 2 and all(num(x) for x in r) for r in pv))
                if not ok:
                    err(pw, "dmg must be [[min,max],[min,max]]")
                elif pv[0][0] > pv[0][1] or pv[1][0] > pv[1][1]:
                    err(pw, "dmg min > max")
                continue
            if pk == "scale" and num(pv):
                continue
            if not (isinstance(pv, list) and len(pv) == 2 and all(num(x) for x in pv)):
                err(pw, "must be [base, per_rank]")
            elif s.get("type") in ("passive", "buff") and pk not in STATS and pk not in ("duration", "form"):
                err(pw, f"{s.get('type')} param must be a canonical stat or duration")
        if s.get("type") == "buff" and "duration" not in s.get("params", {}):
            err(w, "buff needs a duration param")
        if s.get("type") == "summon":
            prm = s.get("params", {})
            if "look" in prm:
                if prm["look"] not in MONSTERS:
                    err(w, f"summon look {prm['look']!r} not in monsters.json")
            elif prm.get("id") not in MONSTERS:
                err(w, f"summon id {prm.get('id')!r} not in monsters.json")
        for other in s.get("synergy", {}):
            if other not in skills:
                err(w, f"synergy refers to unknown skill {other!r}")
            elif skills[other].get("class") != s.get("class"):
                err(w, f"synergy {other!r} belongs to another class")
    for sid in assets["skills"]:
        if sid not in skills and sid not in ("brana", "zjeveni"):
            err("skills", f"assets.md skill {sid!r} missing")


def check_classes(classes, skills, items):
    for cid, c in classes.items():
        w = f"classes.{cid}"
        need(w, c, ["name", "desc", "gender", "base", "base_hp", "hp_per_vit", "hp_per_level",
                    "base_mana", "mana_per_mag", "mana_per_level", "start_items", "trees", "default_rmb"])
        text(w + ".name", c.get("name"))
        text(w + ".desc", c.get("desc"))
        if c.get("gender") not in GENDERS:
            err(w, "bad gender")
        if set(c.get("base", {})) != {"sila", "obratnost", "magie", "vitalita"}:
            err(w, "base must have sila obratnost magie vitalita")
        for it in c.get("start_items", []):
            if it not in items:
                err(w, f"start item {it!r} not in items_base")
        trees = c.get("trees", [])
        if len(trees) != 3:
            err(w, "needs 3 trees")
        for t in trees:
            text(f"{w}.trees.{t.get('id')}.name", t.get("name"))
            if len(t.get("skills", [])) != 4:
                err(w, f"tree {t.get('id')} needs 4 skills")
            for pos, sk in enumerate(t.get("skills", [])):
                s = skills.get(sk)
                if not s:
                    err(w, f"skill {sk!r} missing from skills.json")
                    continue
                if s.get("class") != cid or s.get("tree") != t.get("id"):
                    err(w, f"skill {sk!r} class/tree mismatch")
                if s.get("tier") != pos + 1:
                    err(w, f"skill {sk!r} tier {s.get('tier')} != position {pos + 1}")
        if c.get("default_rmb") not in skills:
            err(w, "default_rmb not a skill")
    for sid, s in skills.items():
        if s.get("class") not in classes and s.get("class") != "any":
            err(f"skills.{sid}", f"class {s.get('class')!r} unknown")


def check_monsters(monsters, uniques, assets):
    for mid, m in monsters.items():
        w = f"monsters.{mid}"
        need(w, m, ["name", "gender", "act", "level", "ai", "hp", "dmg", "armor", "speed",
                    "attack_range", "attack_cd", "element", "resist", "xp_mult", "size", "pack",
                    "projectile", "abilities", "light", "boss"])
        if mid not in assets["monsters"] and mid not in MONSTER_HELPERS:
            err(w, "id not in docs/assets.md monster list")
        text(w + ".name", m.get("name"))
        if m.get("gender") not in GENDERS:
            err(w, "bad gender")
        if m.get("ai") not in AI:
            err(w, f"unknown ai {m.get('ai')!r}")
        if m.get("element") not in ELEMENTS:
            err(w, "bad element")
        if set(m.get("resist", {})) != RESIST_KEYS:
            err(w, "resist must have fire lightning cold poison")
        for k, v in m.get("resist", {}).items():
            if not (num(v) and 0 <= v <= 100):
                err(w, f"resist {k} must be 0..100")
        d = m.get("dmg")
        if not (isinstance(d, list) and len(d) == 2 and d[0] <= d[1]):
            err(w, "dmg must be [min, max]")
        if m.get("projectile") is not None and m["projectile"] not in assets["fx"]:
            err(w, f"projectile {m['projectile']!r} not an fx id")
        if m.get("ai") in ("ranged", "caster") and not m.get("projectile"):
            err(w, "ranged/caster needs a projectile")
        light = m.get("light")
        if light is not None and not (re.fullmatch(r"#[0-9a-fA-F]{6}", str(light.get("color")))
                                      and num(light.get("radius"))):
            err(w, "light must be {color:#rrggbb, radius}")
        if m.get("boss"):
            need(w, m, ["title", "lines", "drops"])
            text(w + ".title", m.get("title"))
            for k in ("aggro", "half", "death"):
                text(f"{w}.lines.{k}", m.get("lines", {}).get(k))
            for u in m.get("drops", []):
                if u not in uniques:
                    err(w, f"drop {u!r} not in uniques.json")
        if "seal" in m and m["seal"] not in SEALS:
            err(w, f"bad seal {m['seal']!r}")
    seals = sorted(m["seal"] for m in monsters.values() if "seal" in m)
    if seals != sorted(SEALS):
        err("monsters", f"seals must be exactly {sorted(SEALS)}, got {seals}")
    for mid in assets["monsters"]:
        if mid not in monsters:
            err("monsters", f"assets.md monster {mid!r} missing")


def check_items(items, assets):
    icons_used = set()
    for iid, it in items.items():
        w = f"items_base.{iid}"
        need(w, it, ["name", "gender", "icon", "slot", "size", "req", "price", "qlvl"])
        text(w + ".name", it.get("name"))
        if "flavor" in it:
            text(w + ".flavor", it["flavor"])
        if it.get("gender") not in GENDERS:
            err(w, "bad gender")
        icon = it.get("icon")
        icons_used.add(icon)
        if icon not in assets["items"]:
            err(w, f"icon {icon!r} not in docs/assets.md items")
        elif assets["items"][icon] and tuple(it.get("size", ())) != assets["items"][icon]:
            err(w, f"size {it.get('size')} != assets.md {list(assets['items'][icon])}")
        slot = it.get("slot")
        if slot not in SLOTS:
            err(w, f"bad slot {slot!r}")
        if slot == "weapon":
            need(w, it, ["kind", "two_handed", "dmg", "dmg_stat", "speed", "durability", "tier"])
            if it.get("speed") not in SPEEDS:
                err(w, "bad speed")
            if it.get("dmg_stat") not in ("sila", "obratnost"):
                err(w, "bad dmg_stat")
            if it.get("kind") in ("bow", "crossbow") and it.get("projectile") not in assets["fx"]:
                err(w, "ranged weapon needs projectile fx")
        if slot in ("offhand", "head", "body", "belt"):
            need(w, it, ["armor", "durability", "tier"])
        if it.get("kind") == "shield" and "block" not in it:
            err(w, "shield needs block")
        if slot == "belt" and not (0 <= it.get("belt_slots", -1) <= 4):
            err(w, "belt_slots 0..4 required")
        if slot == "lamp" and not (2 <= it.get("light", 0) <= 6):
            err(w, "lamp light 2..6 required")
        if slot == "consumable":
            need(w, it, ["use", "stack"])
        tier = it.get("tier")
        if tier is not None:
            lo, hi = {1: (1, 30), 2: (25, 60), 3: (55, 90), 4: (75, 99)}.get(tier, (0, 0))
            if not lo <= it.get("qlvl", 0) <= hi:
                warn(w, f"qlvl {it.get('qlvl')} outside tier {tier} range {lo}-{hi}")
    for icon in assets["items"]:
        if icon not in icons_used:
            err("items_base", f"assets.md item icon {icon!r} unused")
    pk = items.get("permonikuv_kahan", {})
    if pk.get("slot") != "lamp" or pk.get("light") != 3 or not pk.get("unsellable"):
        err("items_base.permonikuv_kahan", "must be slot lamp, light 3, unsellable")


def check_affixes(aff):
    seen = set()
    for kind in ("prefixes", "suffixes"):
        for a in aff.get(kind, []):
            w = f"affixes.{a.get('id')}"
            need(w, a, ["id", "qlvl", "weight", "slots", "name", "mods"])
            if a.get("id") in seen:
                err(w, "duplicate id")
            seen.add(a.get("id"))
            for s in a.get("slots", []):
                if s not in SLOT_GROUPS:
                    err(w, f"bad slot group {s!r}")
            n = a.get("name", {})
            if kind == "prefixes":
                cs = n.get("cs", {})
                if not (isinstance(cs, dict) and set(cs) == GENDERS and all(cs.values())):
                    err(w, "prefix cs name needs m/f/n forms")
                if not (isinstance(n.get("en"), str) and n["en"]):
                    err(w, "missing en name")
            else:
                text(w + ".name", n)
            check_mods(w, a.get("mods"))
    return len(aff.get("prefixes", [])), len(aff.get("suffixes", []))


def check_uniques(uniques, items):
    for uid, u in uniques.items():
        w = f"uniques.{uid}"
        need(w, u, ["name", "base", "qlvl", "mods", "flavor"])
        text(w + ".name", u.get("name"))
        text(w + ".flavor", u.get("flavor"))
        b = items.get(u.get("base"))
        if not b:
            err(w, f"base {u.get('base')!r} not in items_base")
        elif u.get("qlvl", 0) < b.get("qlvl", 0):
            err(w, f"qlvl {u.get('qlvl')} below base qlvl {b.get('qlvl')}")
        check_mods(w, u.get("mods"))
    for uid in REQUIRED_UNIQUES:
        if uid not in uniques:
            err("uniques", f"required unique {uid!r} missing")


def check_shrines(shrines, assets):
    for sid in ("perun", "veles", "mokos", "svarog", "morana", "stribog", "triglav", "rod"):
        if sid not in shrines:
            err("shrines", f"missing {sid}")
    for sid, s in shrines.items():
        w = f"shrines.{sid}"
        need(w, s, ["name", "prop", "effect", "msg"])
        text(w + ".name", s.get("name"))
        text(w + ".msg", s.get("msg"))
        if s.get("prop") not in assets["props_text"]:
            err(w, f"prop {s.get('prop')!r} not in docs/assets.md props")
        e = s.get("effect", {})
        if "mods" in e:
            check_mods(w + ".effect", e["mods"], keys=("value",))
        if "curse" in e and e["curse"].get("stat") not in STATS:
            err(w, "curse stat unknown")
        if not any(k in e for k in ("mods", "heal", "random", "curse")):
            err(w, "effect has nothing in it")


def check_champions(ch):
    names = ch.get("names", [])
    if len(names) < 60:
        err("champions", f"only {len(names)} names (want 60+)")
    for i, n in enumerate(names):
        text(f"champions.names[{i}]", n)
    for mid, m in ch.get("mods", {}).items():
        w = f"champions.mods.{mid}"
        text(w + ".name", m.get("name"))
        check_mods(w, m.get("mods", []), keys=("value",))
        if "aura" in m:
            check_mods(w + ".aura", m["aura"], keys=("value",))
        if "element" in m and m["element"] not in ELEMENTS:
            err(w, "bad element")
    return len(names), len(ch.get("mods", {}))


def check_npcs(npcs, assets):
    for nid, n in npcs.items():
        w = f"npcs.{nid}"
        need(w, n, ["name", "role", "portrait"])
        text(w + ".name", n.get("name"))
        if n.get("role") not in ROLES:
            err(w, f"bad role {n.get('role')!r}")
        if nid not in assets["npcs"]:
            err(w, "id not in docs/assets.md NPC table")
    for nid in assets["npcs"]:
        if nid not in npcs:
            err("npcs", f"assets.md npc {nid!r} missing")


# ---------------------------------------------------------------- narrative cross-refs
def check_narrative(monsters, items, npcs, skills, classes):
    acts = load("acts.json", required=False)
    quests = load("quests.json", required=False)
    dialog = load("dialog.json", required=False)
    lore = load("lore.json", required=False)
    slides = load("slides.json", required=False)
    quest_ids = set(quests) if isinstance(quests, dict) else set()

    if isinstance(acts, list):
        for act in acts:
            w = f"acts[{act.get('id')}]"
            for n in act.get("town", {}).get("npcs", []):
                if n not in npcs:
                    warn(w, f"town npc {n!r} not in npcs.json")
            for f in act.get("floors", []):
                for m in f.get("monsters", []):
                    if m not in monsters:
                        warn(w, f"floor {f.get('n')} monster {m!r} not in monsters.json")
                b = f.get("boss")
                if b and b not in monsters:
                    warn(w, f"floor {f.get('n')} boss {b!r} not in monsters.json")
            for q in act.get("quests", []):
                if quests is not None and q not in quest_ids:
                    warn(w, f"quest {q!r} not in quests.json")
            for k in ("intro", "outro"):
                if slides is not None and act.get(k) and act[k] not in slides:
                    warn(w, f"{k} slide {act[k]!r} not in slides.json")

    if isinstance(quests, dict):
        for qid, q in quests.items():
            w = f"quests.{qid}"
            if q.get("giver") and q["giver"] not in npcs:
                warn(w, f"giver {q['giver']!r} not in npcs.json")
            for st in q.get("steps", []):
                g = st.get("goal", {})
                if "kill" in g and g["kill"] not in monsters:
                    warn(w, f"kill goal {g['kill']!r} not in monsters.json")
                if "pick" in g and g["pick"] not in items:
                    warn(w, f"pick goal {g['pick']!r} not in items_base.json")
                if "talk" in g and g["talk"] not in npcs:
                    warn(w, f"talk goal {g['talk']!r} not in npcs.json")
            r = q.get("reward", {})
            for it in ([r["item"]] if "item" in r else []) + r.get("items", []):
                if it not in items and it not in UNIQUES:
                    warn(w, f"reward item {it!r} not in items_base/uniques")

    if isinstance(dialog, dict):
        for who, entries in dialog.items():
            if who.startswith("_"):
                continue
            if who not in npcs:
                warn(f"dialog.{who}", "speaker not in npcs.json")
            for e in entries if isinstance(entries, list) else []:
                for c in e.get("if", []):
                    if c.startswith("has:") and c[4:] not in items and c[4:] not in UNIQUES:
                        warn(f"dialog.{who}", f"condition {c!r}: unknown item")
                    if c.startswith("class:") and c[6:] not in classes:
                        warn(f"dialog.{who}", f"condition {c!r}: unknown class")
                    if c.startswith("quest:") and quests is not None and c.split(":")[1] not in quest_ids:
                        warn(f"dialog.{who}", f"condition {c!r}: unknown quest")
                for a in e.get("do", []):
                    if a.startswith(("give:", "take:")):
                        it = a.split(":", 1)[1]
                        if it not in items and it not in UNIQUES:
                            warn(f"dialog.{who}", f"action {a!r}: unknown item")
                    if a.startswith(("quest_start:", "quest_step:", "quest_done:")) and quests is not None:
                        if a.split(":")[1] not in quest_ids:
                            warn(f"dialog.{who}", f"action {a!r}: unknown quest")
                    if a.startswith("slide:") and slides is not None and a[6:] not in slides:
                        warn(f"dialog.{who}", f"action {a!r}: unknown slide")
    _ = lore


# ---------------------------------------------------------------- main
MONSTERS, UNIQUES = {}, {}


def main():
    global MONSTERS, UNIQUES
    strict = "--strict" in sys.argv
    assets = parse_assets()
    classes = load("classes.json") or {}
    skills = load("skills.json") or {}
    MONSTERS = monsters = load("monsters.json") or {}
    items = load("items_base.json") or {}
    affixes = load("affixes.json") or {}
    UNIQUES = uniques = load("uniques.json") or {}
    shrines = load("shrines.json") or {}
    champions = load("champions.json") or {}
    npcs = load("npcs.json") or {}

    check_skills(skills, assets)
    check_classes(classes, skills, items)
    check_monsters(monsters, uniques, assets)
    check_items(items, assets)
    npre, nsuf = check_affixes(affixes)
    check_uniques(uniques, items)
    check_shrines(shrines, assets)
    nnames, nmods = check_champions(champions)
    check_npcs(npcs, assets)

    check_narrative(monsters, items, npcs, skills, classes)

    print(f"classes {len(classes)}, skills {len(skills)}, monsters {len(monsters)} "
          f"({sum(1 for m in monsters.values() if m.get('boss'))} bosses), items {len(items)}, "
          f"prefixes {npre}, suffixes {nsuf}, uniques {len(uniques)}, shrines {len(shrines)}, "
          f"champion names {nnames}, champion mods {nmods}, npcs {len(npcs)}")
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    bad = len(errors) + (len(warnings) if strict else 0)
    print("OK" if not bad else f"{bad} error(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
