"""Zet een compact ORM-model in YAML om naar een Factum-model (.orm.json).

Gebruik:
    python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml

De YAML is de bron. Het script maakt ernaast:
    02-conceptueel/{naam}.orm.json    model voor Factum
    02-conceptueel/{naam}.md          het model in zinnen, voor de deskundige
    01-begrippen/{naam}-begrippen.md  begrippen met definitie en bron

Posities die je in Factum hebt verschoven, blijven bij opnieuw draaien bewaard.
Andere wijzigingen in de .orm.json gaan verloren: pas de YAML aan.

Het formaat van de YAML staat in scripts/README.md.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_URL = "https://www.factum-orm.com/schema/orm-model-2.schema.json"
SCHEMA_CACHE = ROOT / "scripts" / ".cache" / "orm-model-2.schema.json"
PLAATS = re.compile(r"\{([^{}]+)\}")
SOORT = {"entiteit": "entity", "waarde": "value"}

fouten: list[str] = []
waarschuwingen: list[str] = []


def slug(s: str) -> str:
    s = s.lower()
    for a, b in {"ë": "e", "é": "e", "ï": "i", "ö": "o", "ü": "u"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


# ---------------------------------------------------------------------------
# Bronverwijzingen
# ---------------------------------------------------------------------------


def bron_link(tekst: str | None, bron_id: str | None, voorbeeld: Path, vanuit: Path) -> str:
    """Maakt van 'artikel 12 lid 1' een link naar de chunk van dat artikel."""
    if not tekst:
        return "geen bron"
    m = re.search(r"artikel (\d+)", tekst, re.I)
    if not (m and bron_id):
        return tekst
    chunks = voorbeeld / "bronnen" / bron_id / "chunks"
    gevonden = sorted(chunks.glob(f"*-art{int(m.group(1)):02d}-*.md"))
    if not gevonden:
        waarschuwingen.append(f"geen chunk gevonden voor '{tekst}'")
        return tekst
    rel = Path(*([".."] * len(vanuit.relative_to(voorbeeld).parts))) / gevonden[0].relative_to(voorbeeld)
    return f"[{tekst}]({rel.as_posix()})"


# Wordt in main gevuld: map van het voorbeeld, bron-id en afkorting van de bron.
CONTEXT: dict = {}


def verwijzingen(tekst: str) -> list[tuple[int, list[str]]]:
    """'artikel 12 lid 2 en 3; artikel 13' wordt [(12, ['2', '3']), (13, [])]."""
    uit = []
    for deel in tekst.split(";"):
        m = re.search(r"artikel\s+([\d\s,en]+?)(?:\s+lid\s+([\d\s,en]+))?\s*$", deel.strip(), re.I)
        if not m:
            continue
        artikelen = re.findall(r"\d+", m.group(1))
        leden = re.findall(r"\d+", m.group(2) or "")
        uit += [(int(a), leden if len(artikelen) == 1 else []) for a in artikelen]
    return uit


def _platte_md(regels: list[str]) -> str:
    tekst = "\n".join(r.strip().removeprefix("- ") for r in regels if r.strip())
    tekst = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", tekst)  # links: alleen de tekst
    return tekst.replace("*", "")


def bronpassage(tekst: str | None) -> str:
    """Haalt de letterlijke tekst van de genoemde artikelen en leden uit de chunks."""
    if not tekst or not CONTEXT.get("bron_id"):
        return ""
    chunks = CONTEXT["voorbeeld"] / "bronnen" / CONTEXT["bron_id"] / "chunks"
    stukken = []
    for artikel, leden in verwijzingen(tekst):
        gevonden = sorted(chunks.glob(f"*-art{artikel:02d}-*.md"))
        if not gevonden:
            waarschuwingen.append(f"geen chunk gevonden voor artikel {artikel}")
            continue
        lijf = gevonden[0].read_text(encoding="utf-8").split("\n# ", 1)[1].split("\n", 1)[1]
        # Een lid begint met 'N. ' aan het begin van de regel.
        per_lid, huidig = {}, None
        for regel in lijf.splitlines():
            m = re.match(r"^(\d+)\. ", regel)
            if m:
                huidig = m.group(1)
            per_lid.setdefault(huidig, []).append(regel)
        if leden:
            for lid in leden:
                if lid not in per_lid:
                    waarschuwingen.append(f"artikel {artikel} heeft geen lid {lid}")
                    continue
                stukken.append(f"Artikel {artikel} lid {lid}:\n{_platte_md(per_lid[lid])[len(lid) + 2:]}")
        else:
            stukken.append(f"Artikel {artikel}:\n{_platte_md(lijf.splitlines())}")
    return "\n\n".join(stukken)


def notitie(definitie: str | None, bron: str | None, gebaseerd_op: str | None) -> str:
    """Tekst voor het veld Note in Factum: definitie, herkomst en de letterlijke bronpassage."""
    afk = CONTEXT.get("afkorting", "")
    delen = []
    if definitie:
        delen.append(f"Definitie: {definitie}")
    if bron:
        extra = " De definitie staat letterlijk in de bron." if definitie else ""
        delen.append(f"Bron: {afk} {bron}.{extra}".replace("  ", " "))
    elif gebaseerd_op:
        delen.append(f"AI-voorstel, gebaseerd op {afk} {gebaseerd_op}.".replace("  ", " "))
    else:
        delen.append("AI-voorstel, zonder passage in de bron.")
    passage = bronpassage(bron or gebaseerd_op)
    if passage:
        delen.append(passage)
    return "\n\n".join(delen)


# ---------------------------------------------------------------------------
# Omzetten
# ---------------------------------------------------------------------------


def rol_index(verwijzing, namen: list[str], wat: str) -> int | None:
    """Een rol is een positie (0, 1, ...) of de naam van een objecttype."""
    if isinstance(verwijzing, int):
        if 0 <= verwijzing < len(namen):
            return verwijzing
    elif namen.count(verwijzing) == 1:
        return namen.index(verwijzing)
    elif namen.count(verwijzing) > 1:
        fouten.append(f"{wat}: '{verwijzing}' komt vaker voor, gebruik de positie (0, 1, ...)")
        return None
    fouten.append(f"{wat}: onbekende rol '{verwijzing}'")
    return None


def lezing_naar_factum(lezing: str, namen: list[str], wat: str) -> tuple[str, list[int]]:
    """'{Persoon} is lid van {Bibliotheek}' wordt '{0} is lid van {1}' plus rolvolgorde."""
    volgorde, gebruikt = [], set()
    for naam in PLAATS.findall(lezing):
        kandidaten = [i for i, n in enumerate(namen) if n == naam and i not in gebruikt]
        if not kandidaten:
            fouten.append(f"{wat}: '{naam}' past niet bij de rollen {namen}")
            return lezing, []
        volgorde.append(kandidaten[0])
        gebruikt.add(kandidaten[0])
    teller = iter(range(len(volgorde)))
    return PLAATS.sub(lambda _: "{%d}" % next(teller), lezing), volgorde


def omzetten(spec: dict, oud: dict | None) -> dict:
    ots, ot_ids = [], {}
    constraints = []
    for naam, o in (spec.get("objecttypen") or {}).items():
        wat = f"objecttype {naam}"
        soort = SOORT.get(o.get("soort"))
        if not soort:
            fouten.append(f"{wat}: soort moet 'entiteit' of 'waarde' zijn")
            continue
        oid = f"ot_{slug(naam)}"
        ot_ids[naam] = oid
        item = {"id": oid, "name": naam, "kind": soort}
        if soort == "entity":
            if not o.get("ref"):
                fouten.append(f"{wat}: een entiteit heeft een 'ref' nodig, bijvoorbeeld 'nr' of 'code'")
            item["refMode"] = o.get("ref", "nr")
        item["dataType"] = o.get("type", "string")
        if o.get("voorbeelden"):
            item["population"] = o["voorbeelden"]
        if not o.get("definitie"):
            fouten.append(f"{wat}: definitie ontbreekt")
        # Factum toont het veld note; meta gaat mee naar andere tools en generatoren.
        tekst = notitie(o.get("definitie"), o.get("bron"), o.get("gebaseerd_op"))
        if o.get("soortbegrip"):
            tekst = f"Soortbegrip: {o['soortbegrip']}\n{tekst}"
        item["note"] = tekst
        item["meta"] = {"shortDescription": o.get("definitie", ""), "description": tekst}
        ots.append(item)
        if o.get("waarden"):
            constraints.append({"id": f"vc_{slug(naam)}", "kind": "value", "objectTypeId": oid,
                                "ranges": [{"value": w} for w in o["waarden"]]})

    fts = []
    namen_per_ot = {v: k for k, v in ot_ids.items()}
    for n, f in enumerate(spec.get("feittypen") or [], 1):
        lezing = f.get("lezing", "")
        wat = f"feittype {n} '{lezing}'"
        namen = PLAATS.findall(lezing)
        if not namen:
            fouten.append(f"{wat}: geen {{Objecttype}} in de lezing")
            continue
        for nm in namen:
            if nm not in ot_ids:
                fouten.append(f"{wat}: objecttype '{nm}' bestaat niet")
        if fouten and any(nm not in ot_ids for nm in namen):
            continue
        fid = "ft_" + slug(f.get("id") or lezing)[:50]
        rollen = [{"id": f"r_{fid[3:]}_{i}", "objectTypeId": ot_ids[nm]} for i, nm in enumerate(namen)]
        rid = [r["id"] for r in rollen]
        tekst, volgorde = lezing_naar_factum(lezing, namen, wat)
        readings = [{"id": f"rd_{fid[3:]}", "roleOrder": [rid[i] for i in volgorde], "text": tekst, "isPrimary": True}]
        if f.get("omgekeerd"):
            t2, v2 = lezing_naar_factum(f["omgekeerd"], namen, wat + " (omgekeerd)")
            readings.append({"id": f"rd_{fid[3:]}_inv", "roleOrder": [rid[i] for i in v2], "text": t2})
        item = {"id": fid, "roles": rollen, "readings": readings}

        uniek = f.get("uniek") or []
        if not uniek:
            fouten.append(f"{wat}: elk feittype heeft minstens één uniciteitsregel nodig")
        for k, groep in enumerate(uniek):
            idx = [rol_index(r, namen, wat) for r in (groep if isinstance(groep, list) else [groep])]
            if None in idx:
                continue
            if len(namen) > 1 and len(idx) < len(namen) - 1:
                fouten.append(f"{wat}: uniciteit over {len(idx)} rol(len) is te kort voor een {len(namen)}-voudig feittype")
            constraints.append({"id": f"uc_{fid[3:]}_{k}", "kind": "uniqueness", "roles": [rid[i] for i in idx]})
        for k, r in enumerate(f.get("verplicht") or []):
            i = rol_index(r, namen, wat)
            if i is not None:
                constraints.append({"id": f"mc_{fid[3:]}_{k}", "kind": "mandatory", "roles": [rid[i]]})

        if f.get("voorbeelden"):
            item["population"] = [{"values": v} for v in f["voorbeelden"]]
        tekst = notitie(None, f.get("bron"), f.get("gebaseerd_op"))
        if f.get("toelichting"):
            tekst = f"{f['toelichting']}\n\n{tekst}"
        item["note"] = tekst
        item["meta"] = {"description": tekst}
        if f.get("toelichting"):
            item["meta"]["shortDescription"] = f["toelichting"]
        item["_namen"] = namen  # alleen voor controle en uitleg, wordt verwijderd
        item["_spec"] = f
        fts.append(item)

    model = {
        "$schema": SCHEMA_URL,
        "version": 2,
        "name": spec["naam"],
        "lang": "nl",
        "note": f"{spec.get('titel', '')}. {spec.get('status', '')}".strip(),
        "objectTypes": ots,
        "factTypes": fts,
        "subtypeRelations": [],
        "constraints": constraints,
        "meta": {"description": spec.get("toelichting", "")},
    }
    model["diagram"] = indeling(ots, fts, oud)
    return model


def indeling(ots: list, fts: list, oud: dict | None) -> dict:
    """Eenvoudige rasterindeling. Bestaande posities uit Factum blijven staan."""
    bewaard = ((oud or {}).get("diagram") or {}).get("shapes", {})
    shapes, pos = {}, {}
    entiteiten = [o for o in ots if o["kind"] == "entity"]
    waarden = [o for o in ots if o["kind"] == "value"]
    for i, o in enumerate(entiteiten):
        pos[o["id"]] = {"x": 120 + (i % 3) * 320, "y": 120 + (i // 3) * 300}
    for i, o in enumerate(waarden):
        pos[o["id"]] = {"x": 1100, "y": 40 + i * 110}
    for o in ots:
        shapes[o["id"]] = bewaard.get(o["id"], pos[o["id"]])
    for f in fts:
        punten = [shapes[r["objectTypeId"]] for r in f["roles"]]
        x = sum(p["x"] for p in punten) / len(punten)
        y = sum(p["y"] for p in punten) / len(punten) + (60 if len(punten) == 1 else 0)
        shapes[f["id"]] = bewaard.get(f["id"], {"x": round(x), "y": round(y), "orientation": "horizontal"})
    return {"shapes": shapes}


# ---------------------------------------------------------------------------
# Controle
# ---------------------------------------------------------------------------


LIDWOORDEN = ("een ", "de ", "het ")
VAAG = {"ding", "object", "gegeven", "iets", "zaak", "entiteit", "element"}


def controleer_definitie(naam: str, d: str, soortbegrip: str | None) -> None:
    """Regels voor definities volgens ISO 704 en ISO 10241-1 (agent: R9 tot en met R18)."""
    if not d:
        return
    if d.lower().startswith(LIDWOORDEN):
        fouten.append(f"definitie van {naam} begint met een lidwoord (R9)")
    if not soortbegrip:
        waarschuwingen.append(f"{naam} heeft geen soortbegrip; classificeer eerst (R9)")
    else:
        if not d.lower().startswith(soortbegrip.lower()):
            fouten.append(f"definitie van {naam} begint niet met het soortbegrip '{soortbegrip}' (R9)")
        if soortbegrip.lower() in VAAG:
            waarschuwingen.append(f"soortbegrip '{soortbegrip}' van {naam} is te algemeen (R10)")
        if " of " in f" {soortbegrip.lower()} ":
            waarschuwingen.append(f"soortbegrip '{soortbegrip}' van {naam} noemt twee begrippen (R10)")
        if soortbegrip.lower() == naam.lower():
            fouten.append(f"soortbegrip van {naam} is het begrip zelf (R17)")
    if not d.endswith("."):
        waarschuwingen.append(f"definitie van {naam} eindigt niet met een punt (R15)")
    if re.search(r"[.!?]\s+[A-Z]", d):
        waarschuwingen.append(f"definitie van {naam} bestaat uit meer dan één zin (R15)")
    if re.match(r"^\S+( \S+)? (die|dat) (geen|niet)\b", d.lower()):
        waarschuwingen.append(f"definitie van {naam} lijkt negatief (R18)")


def controleer(spec: dict, model: dict) -> None:
    ots = {o["id"]: o for o in model["objectTypes"]}
    toegestaan = {c["objectTypeId"]: {r["value"] for r in c["ranges"]}
                  for c in model["constraints"] if c["kind"] == "value"}
    for o in ots.values():
        if o["id"] in toegestaan:
            for v in o.get("population", []):
                if v not in toegestaan[o["id"]]:
                    fouten.append(f"objecttype {o['name']}: voorbeeld '{v}' is geen toegestane waarde")
        d = o["meta"]["shortDescription"]
        controleer_definitie(o["name"], d, (spec.get("objecttypen") or {}).get(o["name"], {}).get("soortbegrip"))
        if re.search(r"\s[-–—]\s", d):
            waarschuwingen.append(f"definitie van {o['name']} bevat een streepje als leesteken")
        if d and o["name"].lower() in d.lower().split(":")[0].split(" "):
            waarschuwingen.append(f"definitie van {o['name']} lijkt het begrip zelf te gebruiken (cirkel)")

    for f in model["factTypes"]:
        namen, rid = f["_namen"], [r["id"] for r in f["roles"]]
        wat = f"feittype '{f['_spec']['lezing']}'"
        rijen = [p["values"] for p in f.get("population", [])]
        if not rijen:
            waarschuwingen.append(f"{wat}: geen voorbeelden")
        for rij in rijen:
            if len(rij) != len(namen):
                fouten.append(f"{wat}: voorbeeld {rij} heeft {len(rij)} waarden, verwacht {len(namen)}")
                continue
            for i, v in enumerate(rij):
                ot = ots[f["roles"][i]["objectTypeId"]]
                if v is None:
                    continue
                if ot["id"] in toegestaan and v not in toegestaan[ot["id"]]:
                    fouten.append(f"{wat}: '{v}' is geen toegestane waarde van {ot['name']}")
                elif ot["kind"] == "entity" and ot.get("population") and v not in ot["population"]:
                    waarschuwingen.append(f"{wat}: '{v}' staat niet bij de voorbeelden van {ot['name']}")
        for c in model["constraints"]:
            if c.get("roles") and set(c["roles"]) <= set(rid):
                idx = [rid.index(r) for r in c["roles"]]
                if c["kind"] == "uniqueness":
                    sleutels = [tuple(r[i] for i in idx) for r in rijen if len(r) == len(namen)]
                    dubbel = {s for s in sleutels if sleutels.count(s) > 1}
                    if dubbel:
                        fouten.append(f"{wat}: voorbeelden breken de uniciteitsregel op {[namen[i] for i in idx]}: {sorted(dubbel)}")
                if c["kind"] == "mandatory":
                    ot = ots[f["roles"][idx[0]]["objectTypeId"]]
                    ontbreekt = set(ot.get("population", [])) - {r[idx[0]] for r in rijen if len(r) == len(namen)}
                    if ontbreekt:
                        waarschuwingen.append(f"{wat}: verplichte rol, maar {sorted(map(str, ontbreekt))} van {ot['name']} komt niet voor")


def valideer_schema(model: dict) -> None:
    try:
        import jsonschema
    except ImportError:
        waarschuwingen.append("jsonschema niet geïnstalleerd, schemacontrole overgeslagen")
        return
    try:
        if not SCHEMA_CACHE.exists():
            SCHEMA_CACHE.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(SCHEMA_URL, headers={"User-Agent": "orm-naar-factum/1.0"})
            SCHEMA_CACHE.write_bytes(urllib.request.urlopen(req, timeout=30).read())
        schema = json.loads(SCHEMA_CACHE.read_text(encoding="utf-8"))
    except Exception as e:  # geen netwerk: niet blokkeren
        waarschuwingen.append(f"schema niet op te halen ({e}), schemacontrole overgeslagen")
        return
    for fout in jsonschema.Draft202012Validator(schema).iter_errors(model):
        fouten.append(f"schema: {'/'.join(map(str, fout.absolute_path))}: {fout.message}")


# ---------------------------------------------------------------------------
# Leesbare uitvoer
# ---------------------------------------------------------------------------


def header(titel: str, doel: str) -> str:
    return "---\n" + yaml.safe_dump({
        "titel": titel, "doel": doel, "auteur": "Hans Blok", "datum": dt.date.today().isoformat(),
        "wijziging": "Automatisch gemaakt uit de .orm.yaml met scripts/orm_naar_factum.py.", "gegenereerd": True,
    }, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n"


def herkomst(item: dict, bron: str | None, voorbeeld: Path, vanuit: Path) -> str:
    """'artikel 12 lid 1' als link, of 'AI-voorstel, gebaseerd op ...'."""
    if item.get("bron"):
        return bron_link(item["bron"], bron, voorbeeld, vanuit)
    if item.get("gebaseerd_op"):
        return f"AI-voorstel, gebaseerd op {bron_link(item['gebaseerd_op'], bron, voorbeeld, vanuit)}"
    return "AI-voorstel"


def regel_in_zinnen(c: dict, namen: list[str], rid: list[str]) -> str:
    idx = [rid.index(r) for r in c["roles"]]
    if c["kind"] == "mandatory":
        return f"Elke {namen[idx[0]]} komt hierin voor (verplicht)."
    if len(namen) == 1:
        return f"Elke {namen[0]} komt hierin hoogstens één keer voor."
    if len(idx) == len(namen):
        return "Elke combinatie van " + " en ".join(namen) + " komt hoogstens één keer voor."
    andere = [namen[i] for i in range(len(namen)) if i not in idx]
    return f"Per {' en '.join(namen[i] for i in idx)} hoogstens één {' en '.join(andere)}."


def schrijf_leesbaar(spec: dict, model: dict, yaml_pad: Path, voorbeeld: Path) -> list[Path]:
    naam, titel = spec["naam"], spec.get("titel", spec["naam"])
    bron = spec.get("bron")
    con = voorbeeld / "02-conceptueel"
    beg = voorbeeld / "01-begrippen"

    # Begrippen (niveau 1)
    r = [f"# Begrippen: {titel}", "", f"> {spec.get('status', '')}", "",
         "| Begrip | Soortbegrip | Definitie | Bron |", "|---|---|---|---|"]
    for n, o in sorted((spec.get("objecttypen") or {}).items()):
        r.append(f"| {n} | {o.get('soortbegrip', '')} | {o.get('definitie', '')} | {herkomst(o, bron, voorbeeld, beg)} |")
    beg.mkdir(exist_ok=True)
    p1 = beg / f"{naam}-begrippen.md"
    p1.write_text(header(f"Begrippen: {titel}", f"Definities van de begrippen in het ORM-model {naam}.") + "\n".join(r) + "\n", encoding="utf-8", newline="\n")

    # Model in zinnen (niveau 2)
    r = [f"# {titel}", "", f"> {spec.get('status', '')}", "",
         f"Bron van de waarheid is [{yaml_pad.name}]({yaml_pad.name}). Het Factum-model is [{naam}.orm.json]({naam}.orm.json).", ""]
    if spec.get("toelichting"):
        r += ["## Waarom zo opgebouwd", "", spec["toelichting"].strip(), ""]
    if spec.get("aannames"):
        r += ["## Aannames en open vragen", ""] + [f"- {a}" for a in spec["aannames"]] + [""]
    r += ["## Feittypen", ""]
    for f in model["factTypes"]:
        s, namen, rid = f["_spec"], f["_namen"], [x["id"] for x in f["roles"]]
        r += [f"### {PLAATS.sub(lambda m: m.group(1), s['lezing'])}", ""]
        if s.get("toelichting"):
            r += [s["toelichting"], ""]
        r.append(f"Bron: {herkomst(s, bron, voorbeeld, con)}")
        r.append("")
        for c in model["constraints"]:
            if c.get("roles") and set(c["roles"]) <= set(rid):
                r.append(f"- {regel_in_zinnen(c, namen, rid)}")
        if f.get("population"):
            r += ["", "| " + " | ".join(namen) + " |", "|" + "---|" * len(namen)]
            r += ["| " + " | ".join("" if v is None else str(v) for v in p["values"]) + " |" for p in f["population"]]
        r.append("")
    if spec.get("regels"):
        r += ["## Overige regels", "", "Deze regels zijn niet als ORM-regel in het diagram te tekenen.", ""]
        r += [f"- {x['regel']} Bron: {bron_link(x.get('bron'), bron, voorbeeld, con)}" for x in spec["regels"]] + [""]
    p2 = con / f"{naam}.md"
    p2.write_text(header(titel, f"Het ORM-model {naam} in gewone zinnen, voor bespreking met een deskundige.") + "\n".join(r), encoding="utf-8", newline="\n")
    return [p1, p2]


# ---------------------------------------------------------------------------


def datums_als_tekst(x):
    """YAML leest 2015-03-12 als datum; Factum verwacht tekst."""
    if isinstance(x, dict):
        return {k: datums_als_tekst(v) for k, v in x.items()}
    if isinstance(x, list):
        return [datums_als_tekst(v) for v in x]
    if isinstance(x, (dt.date, dt.datetime)):
        return x.isoformat()
    return x


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # anders verminkt de Windows-console é en ë
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    yaml_pad = Path(sys.argv[1]).resolve()
    voorbeeld = yaml_pad.parent.parent
    spec = datums_als_tekst(yaml.safe_load(yaml_pad.read_text(encoding="utf-8")))
    if not spec.get("naam"):
        print("FOUT: 'naam' ontbreekt")
        return 1
    CONTEXT.update(voorbeeld=voorbeeld, bron_id=spec.get("bron"), afkorting="")
    register = voorbeeld / "bronnen" / "bronnen.yaml"
    if spec.get("bron") and register.exists():
        for b in yaml.safe_load(register.read_text(encoding="utf-8"))["bronnen"]:
            if b["id"] == spec["bron"]:
                CONTEXT["afkorting"] = b.get("afkorting", "")
    json_pad = yaml_pad.with_name(f"{spec['naam']}.orm.json")
    oud = json.loads(json_pad.read_text(encoding="utf-8")) if json_pad.exists() else None

    model = omzetten(spec, oud)
    if not fouten:
        controleer(spec, model)
    schoon = json.loads(json.dumps(model))
    for f in schoon["factTypes"]:
        f.pop("_namen", None)
        f.pop("_spec", None)
    if not fouten:
        valideer_schema(schoon)

    for w in waarschuwingen:
        print(f"let op: {w}")
    if fouten:
        for f in fouten:
            print(f"FOUT: {f}")
        print("Niets geschreven.")
        return 1

    json_pad.write_text(json.dumps(schoon, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    extra = schrijf_leesbaar(spec, model, yaml_pad, voorbeeld)
    print(f"In orde: {len(schoon['objectTypes'])} objecttypen, {len(schoon['factTypes'])} feittypen, "
          f"{len(schoon['constraints'])} regels.")
    for p in [json_pad, *extra]:
        print(f"  {p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
