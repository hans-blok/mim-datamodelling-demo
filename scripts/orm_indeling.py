"""Meet en verbetert de indeling van een ORM-diagram in een Factum-model (.orm.json).

Het script past alleen `diagram.shapes` aan. Objecttypen, feittypen en regels blijven
ongewijzigd.

Gebruik:
    python scripts/orm_indeling.py structuur MODEL.orm.json
    python scripts/orm_indeling.py meet      MODEL.orm.json
    python scripts/orm_indeling.py toepas    MODEL.orm.json INDELING.yaml|- [--schrijf]
    python scripts/orm_indeling.py schik     MODEL.orm.json [--vast id,id] [--stappen N] [--schrijf]

Zonder --schrijf verandert er niets: je ziet alleen de meting vooraf en achteraf.

Indeling (YAML) voor `toepas`: per vorm het MIDDELPUNT, met optioneel v (verticaal) of
h (horizontaal) voor een feittype. Vormen die je niet noemt, blijven staan.

    ot_e1: [400, 700]
    ft_b:  [700, 560, h]
    ft_k:  [880, 540, v]

Aannames over Factum (afgeleid uit schermafbeeldingen, niet uit documentatie):
- x en y in `diagram.shapes` zijn de linkerbovenhoek van een vorm;
- de rollen van een horizontaal feittype staan van links naar rechts in de volgorde van
  `roles`, bij een verticaal feittype van boven naar beneden;
- een geobjectiveerd feittype wordt getekend als kader rond het feittype; de eigen
  positie van het objecttype doet er dan niet toe.
De afmetingen van vormen zijn schattingen.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import sys
from pathlib import Path

ROL = 28          # breedte van één rolvak
FT_H = 22         # hoogte van een feittype
MARGE = 12        # minimale ruimte tussen vormen

GEWICHT = {
    "kruising": 100,
    "overlap": 300,
    "lijn_door_vorm": 60,
    "regelkruising": 10,
    "lengte": 0.05,
}


# ---------------------------------------------------------------- model

class Model:
    def __init__(self, pad: Path):
        self.pad = pad
        self.data = json.loads(pad.read_text(encoding="utf-8"))
        self.ot = {o["id"]: o for o in self.data.get("objectTypes", [])}
        self.ft = {f["id"]: f for f in self.data.get("factTypes", [])}
        self.cs = {c["id"]: c for c in self.data.get("constraints", [])}
        self.subtypes = self.data.get("subtypeRelations", [])
        self.rol_ft = {r["id"]: f["id"] for f in self.ft.values() for r in f["roles"]}
        # geobjectiveerd objecttype -> feittype
        self.alias = {o["id"]: o["objectifiedFactTypeId"]
                      for o in self.ot.values() if o.get("objectifiedFactTypeId")}
        self.shapes = self.data.setdefault("diagram", {}).setdefault("shapes", {})

    def naam(self, i: str) -> str:
        if i in self.ot:
            return self.ot[i]["name"]
        if i in self.ft:
            f = self.ft[i]
            rd = next((r for r in f.get("readings", []) if r.get("isPrimary")), None) or \
                (f.get("readings") or [{}])[0]
            return rd.get("text", f.get("name", i))
        if i in self.cs:
            return self.cs[i]["kind"]
        return i

    def speler(self, rol: dict) -> str:
        return rol.get("objectTypeId") or rol.get("playerId")

    def maat(self, i: str, orient: str = "h") -> tuple[float, float]:
        if i in self.ot:
            n = len(self.ot[i]["name"])
            if self.ot[i]["kind"] == "entity":
                return max(110, 7.5 * n + 40), 50
            return max(90, 7.5 * n + 40), 36
        if i in self.ft:
            lengte = ROL * len(self.ft[i]["roles"])
            return (lengte, FT_H) if orient == "h" else (FT_H, lengte)
        return 24, 24  # regelsymbool

    def regel_fts(self, cid: str) -> list[str]:
        """Feittypen waar een getekende regel (met eigen vorm) naar wijst."""
        c = self.cs[cid]
        rollen = list(c.get("roles", []))
        for groep in c.get("roleSequences", []) or []:
            rollen += groep if isinstance(groep, list) else groep.get("roles", [])
        for k in ("subsetRoles", "supersetRoles"):
            rollen += c.get(k, []) or []
        return sorted({self.rol_ft[r] for r in rollen if r in self.rol_ft})


# ---------------------------------------------------------------- posities

def lees_posities(m: Model) -> dict:
    """id -> [cx, cy, orient] (middelpunten)."""
    p = {}
    for i, s in m.shapes.items():
        o = "v" if s.get("orientation") == "vertical" else "h"
        w, h = m.maat(i, o)
        p[i] = [s["x"] + w / 2, s["y"] + h / 2, o]
    return p


def schrijf_posities(m: Model, p: dict) -> None:
    for i in list(m.shapes):
        if i not in p:
            continue
        cx, cy, o = p[i]
        if i in m.alias and m.alias[i] in p:  # kader volgt het feittype
            cx, cy = p[m.alias[i]][:2]
        w, h = m.maat(i, o)
        s = {"x": round(cx - w / 2), "y": round(cy - h / 2)}
        if i in m.ft:
            s["orientation"] = "vertical" if o == "v" else "horizontal"
        m.shapes[i] = s


def centrum(m: Model, p: dict, i: str) -> tuple[float, float]:
    if i in m.alias and m.alias[i] in p:
        return tuple(p[m.alias[i]][:2])
    return tuple(p[i][:2])


def rolpunt(m: Model, p: dict, fid: str, k: int) -> tuple[float, float]:
    cx, cy, o = p[fid]
    n = len(m.ft[fid]["roles"])
    d = (k - (n - 1) / 2) * ROL
    return (cx + d, cy) if o == "h" else (cx, cy + d)


def lijnen(m: Model, p: dict) -> list[tuple]:
    """(eind_a, eind_b, punt_a, punt_b) voor doorgaande lijnen."""
    L = []
    for f in m.ft.values():
        for k, r in enumerate(f["roles"]):
            s = m.speler(r)
            if s in p and f["id"] in p:
                L.append((f["id"], s, rolpunt(m, p, f["id"], k), centrum(m, p, s)))
    for st in m.subtypes:
        a, b = st["subtypeId"], st["supertypeId"]
        if a in p and b in p:
            L.append((a, b, centrum(m, p, a), centrum(m, p, b)))
    return L


def regellijnen(m: Model, p: dict) -> list[tuple]:
    L = []
    for cid in m.cs:
        if cid in p:
            for f in m.regel_fts(cid):
                if f in p:
                    L.append((cid, f, centrum(m, p, cid), centrum(m, p, f)))
    return L


def kader(m: Model, p: dict, i: str) -> tuple[float, float, float, float]:
    cx, cy = centrum(m, p, i)
    w, h = m.maat(i, p[i][2])
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


# ---------------------------------------------------------------- meetkunde

def _kruis(p, q, r):
    return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])


def snijden(a, b, c, d) -> bool:
    return _kruis(a, b, c) * _kruis(a, b, d) < 0 and _kruis(c, d, a) * _kruis(c, d, b) < 0


def lijn_door_kader(a, b, k) -> bool:
    x0, y0, x1, y1 = k[0] + 2, k[1] + 2, k[2] - 2, k[3] - 2
    if max(a[0], b[0]) < x0 or min(a[0], b[0]) > x1 or max(a[1], b[1]) < y0 or min(a[1], b[1]) > y1:
        return False
    hoeken = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    if any(x0 <= q[0] <= x1 and y0 <= q[1] <= y1 for q in (a, b)):
        return True
    return any(snijden(a, b, hoeken[i], hoeken[(i + 1) % 4]) for i in range(4))


def overlappen(k1, k2) -> bool:
    return not (k1[2] + MARGE <= k2[0] or k2[2] + MARGE <= k1[0] or
                k1[3] + MARGE <= k2[1] or k2[3] + MARGE <= k1[1])


# ---------------------------------------------------------------- meting

def meet(m: Model, p: dict, details: bool = False) -> dict:
    def eigen(i):  # een geobjectiveerd objecttype en zijn feittype gelden als één vorm
        return m.alias.get(i, i)

    L = lijnen(m, p)
    R = regellijnen(m, p)
    vormen = [i for i in p if i not in m.alias]
    kaders = {i: kader(m, p, i) for i in vormen}
    uit = {"kruising": [], "overlap": [], "lijn_door_vorm": [], "regelkruising": [], "lengte": 0.0}

    for s, t in itertools.combinations(L, 2):
        if {eigen(s[0]), eigen(s[1])} & {eigen(t[0]), eigen(t[1])}:
            continue
        if snijden(s[2], s[3], t[2], t[3]):
            uit["kruising"].append(f"{s[0]}-{s[1]} x {t[0]}-{t[1]}")
    for s in R:
        for t in L:
            if s[1] in (t[0], t[1]):
                continue
            if snijden(s[2], s[3], t[2], t[3]):
                uit["regelkruising"].append(f"{s[0]}-{s[1]} x {t[0]}-{t[1]}")
    for a, b in itertools.combinations(vormen, 2):
        if overlappen(kaders[a], kaders[b]):
            uit["overlap"].append(f"{a} / {b}")
    for s in L:
        eind = {eigen(s[0]), eigen(s[1])}
        for i in vormen:
            if i in eind:
                continue
            if lijn_door_kader(s[2], s[3], kaders[i]):
                uit["lijn_door_vorm"].append(f"{s[0]}-{s[1]} door {i}")
    for s in L + R:
        uit["lengte"] += math.dist(s[2], s[3])

    uit["score"] = round(sum(GEWICHT[k] * (len(v) if isinstance(v, list) else v)
                             for k, v in uit.items() if k in GEWICHT), 1)
    if not details:
        return {k: (len(v) if isinstance(v, list) else round(v)) for k, v in uit.items()}
    return uit


def toon(titel: str, r: dict) -> None:
    kort = {k: (len(v) if isinstance(v, list) else round(v)) for k, v in r.items()}
    print(f"{titel}: score {kort['score']} | kruisingen {kort['kruising']} | "
          f"overlap {kort['overlap']} | lijn door vorm {kort['lijn_door_vorm']} | "
          f"regellijn kruist {kort['regelkruising']} | lijnlengte {kort['lengte']}")
    for k in ("kruising", "overlap", "lijn_door_vorm"):
        if isinstance(r[k], list) and r[k]:
            print(f"  {k}: " + "; ".join(r[k][:12]) + (" ..." if len(r[k]) > 12 else ""))


# ---------------------------------------------------------------- structuur

def structuur(m: Model, p: dict) -> None:
    graad = {i: 0 for i in m.ot}
    for f in m.ft.values():
        for r in f["roles"]:
            graad[m.speler(r)] = graad.get(m.speler(r), 0) + 1
    for st in m.subtypes:
        graad[st["subtypeId"]] += 1
        graad[st["supertypeId"]] += 1
    print("# Objecttypen (meest verbonden eerst)")
    for i in sorted(m.ot, key=lambda i: -graad[i]):
        o = m.ot[i]
        extra = f" kader rond {m.alias[i]}" if i in m.alias else ""
        print(f"{i}\t{o['kind']}\t{graad[i]} lijnen\t{o['name']}{extra}")
    print("\n# Feittypen: rollen in volgorde (links->rechts, of boven->onder)")
    for f in m.ft.values():
        spelers = [m.speler(r) for r in f["roles"]]
        print(f"{f['id']}\t{' | '.join(spelers)}\t{m.naam(f['id'])}")
    if m.subtypes:
        print("\n# Subtypen")
        for st in m.subtypes:
            print(f"{st['subtypeId']} -> {st['supertypeId']}")
    groepen = [(c, m.regel_fts(c)) for c in m.cs]
    groepen = [(c, f) for c, f in groepen if len(f) > 1]
    if groepen:
        print("\n# Regels over meer feittypen: houd die feittypen bij elkaar")
        for c, f in groepen:
            vorm = " (eigen vorm)" if c in p else ""
            print(f"{c}\t{m.cs[c]['kind']}{vorm}\t{', '.join(f)}")


# ---------------------------------------------------------------- automatisch schikken

def schik(m: Model, p: dict, vast: set, stappen: int, zaad: int) -> dict:
    rnd = random.Random(zaad)
    beweeg = [i for i in p if i not in vast and i not in m.alias]
    if not beweeg:
        return p
    huidig = {k: list(v) for k, v in p.items()}
    s_huidig = meet(m, huidig)["score"]
    beste, s_beste = {k: list(v) for k, v in huidig.items()}, s_huidig
    for n in range(stappen):
        frac = n / max(1, stappen - 1)
        temp = 40 * (1 - frac) + 0.5
        stap = 200 * (1 - frac) + 10
        kandidaat = {k: list(v) for k, v in huidig.items()}
        i = rnd.choice(beweeg)
        keuze = rnd.random()
        if i in m.ft and keuze < 0.1:
            kandidaat[i][2] = "v" if kandidaat[i][2] == "h" else "h"
        elif keuze < 0.2:
            soort = [j for j in beweeg if (j in m.ft) == (i in m.ft) and j != i]
            if soort:
                j = rnd.choice(soort)
                kandidaat[i][:2], kandidaat[j][:2] = kandidaat[j][:2], kandidaat[i][:2]
        else:
            kandidaat[i][0] = round((kandidaat[i][0] + rnd.gauss(0, stap)) / 10) * 10
            kandidaat[i][1] = round((kandidaat[i][1] + rnd.gauss(0, stap)) / 10) * 10
        s = meet(m, kandidaat)["score"]
        if s <= s_huidig or rnd.random() < math.exp((s_huidig - s) / temp):
            huidig, s_huidig = kandidaat, s
            if s < s_beste:
                beste, s_beste = {k: list(v) for k, v in kandidaat.items()}, s
    # links en boven op 20 laten beginnen
    xs = [kader(m, beste, i)[0] for i in beste if i not in m.alias]
    ys = [kader(m, beste, i)[1] for i in beste if i not in m.alias]
    dx, dy = 20 - min(xs), 20 - min(ys)
    for v in beste.values():
        v[0] += dx
        v[1] += dy
    return beste


# ---------------------------------------------------------------- hoofdprogramma

def lees_indeling(bron: str) -> dict:
    import yaml  # alleen nodig voor `toepas`
    tekst = sys.stdin.read() if bron == "-" else Path(bron).read_text(encoding="utf-8")
    return yaml.safe_load(tekst) or {}


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("actie", choices=["structuur", "meet", "toepas", "schik"])
    ap.add_argument("model", type=Path)
    ap.add_argument("indeling", nargs="?")
    ap.add_argument("--vast", default="", help="ids die schik niet mag verplaatsen, met komma's")
    ap.add_argument("--stappen", type=int, default=4000)
    ap.add_argument("--zaad", type=int, default=1)
    ap.add_argument("--schrijf", action="store_true", help="het resultaat opslaan")
    a = ap.parse_args()

    m = Model(a.model)
    p = lees_posities(m)
    ontbreekt = [i for i in list(m.ot) + list(m.ft) if i not in p]
    if ontbreekt:
        print("FOUT: deze vormen staan niet in diagram.shapes: " + ", ".join(ontbreekt))
        return 1

    if a.actie == "structuur":
        structuur(m, p)
        return 0
    voor = meet(m, p, details=True)
    if a.actie == "meet":
        toon("Huidig", voor)
        return 0

    if a.actie == "toepas":
        if not a.indeling:
            print("FOUT: geef een indelingsbestand of - voor invoer via stdin.")
            return 1
        nieuw = {k: list(v) for k, v in p.items()}
        for i, w in lees_indeling(a.indeling).items():
            if i not in nieuw:
                print(f"FOUT: onbekende vorm {i}")
                return 1
            nieuw[i][0], nieuw[i][1] = float(w[0]), float(w[1])
            if len(w) > 2:
                nieuw[i][2] = "v" if str(w[2]).lower().startswith("v") else "h"
    else:
        vast = {v.strip() for v in a.vast.split(",") if v.strip()}
        nieuw = schik(m, p, vast, a.stappen, a.zaad)

    na = meet(m, nieuw, details=True)
    toon("Voor", voor)
    toon("Na  ", na)
    if a.schrijf:
        schrijf_posities(m, nieuw)
        a.model.write_text(json.dumps(m.data, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="\n")
        print(f"Geschreven: {a.model}")
    else:
        print("Niets geschreven. Gebruik --schrijf om op te slaan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
