"""Zet bronnen uit elk bronnen/bronnen.yaml in de repository om naar Markdown-chunks.

Gebruik:
    python scripts/bron_naar_chunks.py               alle bronnen
    python scripts/bron_naar_chunks.py wsob          alleen de bron met id 'wsob'
    python scripts/bron_naar_chunks.py --download    eerst het origineel (opnieuw) ophalen

Per bron komt in bronnen/{id}/:
    origineel/     het opgehaalde bronbestand, ongewijzigd
    chunks/        één Markdown-bestand per artikel, plus 00-index.md
    chunks.jsonl   dezelfde chunks in één bestand, voor tools

Een nieuw brontype toevoegen: schrijf een functie die een Bron leest en een
lijst Chunk-objecten teruggeeft, en zet hem in LEZERS.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def vind_registers() -> list[Path]:
    """Alle bronnen/bronnen.yaml in de repository, bijvoorbeeld per voorbeeld."""
    return sorted(
        p for p in ROOT.glob("**/bronnen/bronnen.yaml") if ".git" not in p.parts
    )


# ---------------------------------------------------------------------------
# Gedeeld model
# ---------------------------------------------------------------------------


@dataclass
class Chunk:
    chunk_id: str  # bestandsnaam zonder extensie
    titel: str  # kop van de chunk, bijvoorbeeld "Artikel 12. Lidmaatschap"
    markdown: str  # inhoud zonder kop
    platte_tekst: str  # dezelfde inhoud zonder opmaak, voor controle en zoeken
    bron_tekst: str  # tekst zoals die in het origineel staat, voor controle
    velden: dict = field(default_factory=dict)  # extra header-velden


@dataclass
class Bron:
    id: str
    config: dict
    basis: Path  # de map bronnen/ waarin bronnen.yaml staat

    @property
    def map(self) -> Path:
        return self.basis / self.id

    @property
    def origineel(self) -> Path:
        return self.map / "origineel" / self.config["bestand"]


# ---------------------------------------------------------------------------
# Lezer: BWB-toestand-XML van wetten.overheid.nl
# ---------------------------------------------------------------------------

BLOK = {"al", "lid", "lijst", "li", "redactie"}
OVERSLAAN = {"meta-data", "kop", "lidnr", "li.nr", "jcis"}


def _jci_naar_url(jci: str) -> str:
    """Maakt van een Juriconnect-verwijzing een webadres.

    In BWB-XML staat een verwijzing naar een wet als jci-code, bijvoorbeeld
    'jci1.3:c:BWBR0001886&artikel=10'. wetten.overheid.nl stuurt zo'n adres
    door naar het juiste artikel.
    """
    return "https://wetten.overheid.nl/" + jci


def _inline(e: ET.Element) -> tuple[str, str]:
    """Geeft (markdown, platte tekst) van een element met gemengde inhoud."""
    md, pt = [e.text or ""], [e.text or ""]
    for kind in e:
        if kind.tag in OVERSLAAN:
            pass
        elif kind.tag == "nadruk":
            m, p = _inline(kind)
            teken = "**" if kind.get("type") == "vet" else "*"
            md.append(f"{teken}{m.strip()}{teken}" + (" " if m.endswith(" ") else ""))
            pt.append(p)
        elif kind.tag in ("extref", "intref") and kind.get("doc"):
            m, p = _inline(kind)
            md.append(f"[{m}]({_jci_naar_url(kind.get('doc'))})")
            pt.append(p)
        else:
            m, p = _inline(kind)
            md.append(m)
            pt.append(p)
        md.append(kind.tail or "")
        pt.append(kind.tail or "")
    return _schoon("".join(md)), _schoon("".join(pt))


def _schoon(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _blokken(e: ET.Element, inspring: str = "") -> tuple[list[str], list[str]]:
    """Zet een artikel of lid om naar Markdown-regels en platte-tekstregels."""
    md, pt = [], []
    for kind in e:
        tag = kind.tag
        if tag in OVERSLAAN:
            continue
        if tag == "al":
            m, p = _inline(kind)
            md.append(inspring + m)
            pt.append(p)
        elif tag == "lid":
            nr = (kind.findtext("lidnr") or "").strip().rstrip(".")
            m, p = _blokken(kind, inspring + "   ")
            if m:
                m[0] = f"{inspring}{nr}. {m[0].lstrip()}"
            md += m
            pt += [nr] + p
        elif tag == "lijst":
            m, p = _blokken(kind, inspring)
            md += m
            pt += p
        elif tag == "li":
            nr = (kind.findtext("li.nr") or "").strip()
            m, p = _blokken(kind, inspring + "  ")
            if m:
                m[0] = f"{inspring}- {nr} {m[0].lstrip()}"
            md += m
            pt += [nr] + p
        elif tag == "redactie":
            m, p = _inline(kind)
            md.append(f"{inspring}*[{m}]*")
            pt.append(p)
        else:
            # Onbekend element: tekst behouden en melden, zodat niets verloren gaat.
            print(f"  let op: onbekend element <{tag}>, als gewone tekst opgenomen")
            m, p = _inline(kind)
            md.append(inspring + m)
            pt.append(p)
    return md, pt


def _bron_tekst(e: ET.Element) -> str:
    """Alle tekst van een element behalve metadata en de kop."""
    delen = []

    def loop(x: ET.Element):
        if x.tag in ("meta-data", "kop", "jcis"):
            return
        delen.append(x.text or "")
        for k in x:
            loop(k)
            delen.append(k.tail or "")

    delen.append(e.text or "")
    for k in e:
        loop(k)
        delen.append(k.tail or "")
    return _schoon("".join(delen))


def _kop(e: ET.Element) -> tuple[str, str]:
    kop = e.find("kop")
    nr = _schoon("".join(kop.find("nr").itertext())) if kop is not None else ""
    titel_el = kop.find("titel") if kop is not None else None
    titel = _schoon("".join(titel_el.itertext())) if titel_el is not None else ""
    return nr, titel


def _slug(s: str) -> str:
    s = s.lower()
    for a, b in {"ë": "e", "é": "e", "ï": "i", "ö": "o", "ü": "u"}.items():
        s = s.replace(a, b)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60]


def lees_bwb_xml(bron: Bron) -> tuple[list[Chunk], dict]:
    wortel = ET.parse(bron.origineel).getroot()
    if wortel.tag != "toestand":
        sys.exit(f"{bron.origineel} is geen BWB-toestand")
    basis = wortel.get("bwb-ng-vast-deel").replace(
        "http://wetten.overheid.nl/id/", "https://wetten.overheid.nl/"
    )
    meta = {
        "bwb_id": wortel.get("bwb-id"),
        "geldend_vanaf": wortel.get("inwerkingtreding"),
        "intitule": _schoon(wortel.findtext(".//intitule") or ""),
    }
    max_woorden = bron.config.get("max_woorden", 600)

    chunks: list[Chunk] = []
    for hoofdstuk in wortel.iter("hoofdstuk"):
        h_nr, h_titel = _kop(hoofdstuk)
        for artikel in hoofdstuk.iter("artikel"):
            a_nr, a_titel = _kop(artikel)
            pad = artikel.get("bwb-ng-variabel-deel")
            basisvelden = {
                "hoofdstuk": f"{h_nr}. {h_titel}",
                "artikel": a_nr,
                "bron_url": basis + pad,
                "status": artikel.get("status"),
                "in_werking": artikel.get("inwerking"),
            }
            stam = f"h{int(h_nr):02d}-art{int(a_nr):02d}-{_slug(a_titel)}"
            kop = f"Artikel {a_nr}. {a_titel}"

            leden = artikel.findall("lid")
            woorden = len(_bron_tekst(artikel).split())
            if woorden > max_woorden and len(leden) > 1:
                # Te lang: per lid een chunk.
                for lid in leden:
                    nr = (lid.findtext("lidnr") or "").strip().rstrip(".")
                    md, pt = _blokken(lid)
                    chunks.append(
                        Chunk(
                            chunk_id=f"{stam}-lid{nr}",
                            titel=f"{kop}, lid {nr}",
                            markdown="\n".join(md),
                            platte_tekst=" ".join(pt),
                            bron_tekst=_bron_tekst(lid),
                            velden={**basisvelden, "lid": nr},
                        )
                    )
            else:
                md, pt = _blokken(artikel)
                chunks.append(
                    Chunk(
                        chunk_id=stam,
                        titel=kop,
                        markdown="\n".join(md),
                        platte_tekst=" ".join(pt),
                        bron_tekst=_bron_tekst(artikel),
                        velden=basisvelden,
                    )
                )
    return chunks, meta


LEZERS = {
    "bwb-xml": lees_bwb_xml,
}


# ---------------------------------------------------------------------------
# Schrijven
# ---------------------------------------------------------------------------


def _header(velden: dict) -> str:
    return "---\n" + yaml.safe_dump(
        velden, allow_unicode=True, sort_keys=False, width=1000
    ) + "---\n"


def _schrijf_als_gewijzigd(pad: Path, inhoud: str, vandaag: str) -> bool:
    """Schrijft alleen als de inhoud (los van de datum) is veranderd.

    Zo blijft de datum in de header staan op de dag dat de tekst echt veranderde,
    en geeft opnieuw draaien geen onnodige wijzigingen in git.
    """
    zonder_datum = lambda s: re.sub(r"^datum: .*$", "", s, count=1, flags=re.M)
    if pad.exists() and zonder_datum(pad.read_text(encoding="utf-8")) == zonder_datum(inhoud):
        return False
    pad.write_text(inhoud, encoding="utf-8", newline="\n")
    return True


def schrijf(bron: Bron, chunks: list[Chunk], meta: dict, auteur: str) -> None:
    c = bron.config
    vandaag = dt.date.today().isoformat()
    uit = bron.map / "chunks"
    uit.mkdir(parents=True, exist_ok=True)

    gewijzigd = 0
    bekend = set()
    for ch in chunks:
        velden = {
            "titel": f"{c['afkorting']}, {ch.titel}",
            "doel": c["doel"],
            "auteur": auteur,
            "datum": vandaag,
            "wijziging": "Automatisch gemaakt uit het origineel met scripts/bron_naar_chunks.py.",
            "bron_id": bron.id,
            "bron_titel": c["titel"],
            **ch.velden,
            "gegenereerd": True,
        }
        tekst = _header(velden) + f"\n# {ch.titel}\n\n{ch.markdown}\n"
        pad = uit / f"{ch.chunk_id}.md"
        gewijzigd += _schrijf_als_gewijzigd(pad, tekst, vandaag)
        bekend.add(pad.name)

    # Index
    regels = [
        f"# {c['titel']}",
        "",
        f"{meta.get('intitule', '')}",
        "",
        f"Bron: [{c['url']}]({c['url']}), geldend vanaf {meta.get('geldend_vanaf')}.",
        "",
        "Deze chunks zijn automatisch gemaakt uit het origineel. De tekst is letterlijk overgenomen.",
        "Wijzig ze niet met de hand: pas het script aan en draai het opnieuw.",
    ]
    vorige = None
    for ch in chunks:
        h = ch.velden.get("hoofdstuk")
        if h != vorige:
            regels += ["", f"## Hoofdstuk {h}", ""]
            vorige = h
        regels.append(f"- [{ch.titel}]({ch.chunk_id}.md)")
    index = _header(
        {
            "titel": f"{c['afkorting']}, inhoudsopgave",
            "doel": f"Overzicht van de chunks van de {c['afkorting']}, zodat AI eerst de index leest en daarna gericht artikelen ophaalt.",
            "auteur": auteur,
            "datum": vandaag,
            "wijziging": "Automatisch gemaakt uit het origineel met scripts/bron_naar_chunks.py.",
            "bron_id": bron.id,
            "gegenereerd": True,
        }
    ) + "\n" + "\n".join(regels) + "\n"
    gewijzigd += _schrijf_als_gewijzigd(uit / "00-index.md", index, vandaag)
    bekend.add("00-index.md")

    # Verouderde chunks opruimen, bijvoorbeeld na een vervallen artikel.
    for oud in uit.glob("*.md"):
        if oud.name not in bekend:
            oud.unlink()
            print(f"  verwijderd: {oud.name}")

    # JSONL voor tools
    with open(bron.map / "chunks.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for ch in chunks:
            f.write(
                json.dumps(
                    {
                        "id": f"{bron.id}/{ch.chunk_id}",
                        "bron_id": bron.id,
                        "titel": ch.titel,
                        **ch.velden,
                        "tekst": ch.platte_tekst,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"  {len(chunks)} chunks, {gewijzigd} bestanden nieuw of gewijzigd")


# ---------------------------------------------------------------------------
# Controle
# ---------------------------------------------------------------------------


def _woorden(s: str) -> list[str]:
    return re.findall(r"\w+", s.lower())


def controleer(bron: Bron, chunks: list[Chunk]) -> bool:
    ok = True
    verwacht = bron.config.get("verwacht", {})
    if "chunks" in verwacht and len(chunks) != verwacht["chunks"]:
        print(f"  FOUT: {len(chunks)} chunks, verwacht {verwacht['chunks']}")
        ok = False
    for ch in chunks:
        if _woorden(ch.platte_tekst) != _woorden(ch.bron_tekst):
            print(f"  FOUT: tekst van {ch.chunk_id} wijkt af van het origineel")
            ok = False
        if "�" in ch.markdown:
            print(f"  FOUT: kapot teken in {ch.chunk_id}")
            ok = False
        if not ch.platte_tekst.strip():
            print(f"  FOUT: {ch.chunk_id} is leeg")
            ok = False
    print("  controle: " + ("in orde" if ok else "NIET in orde"))
    return ok


def schrijf_overzicht(register: dict, basis: Path) -> None:
    """Schrijft bronnen/README.md: een leesbaar overzicht van alle bronnen."""
    vandaag = dt.date.today().isoformat()
    def chunks_link(cfg: dict) -> str:
        index = basis / cfg["id"] / "chunks" / "00-index.md"
        return f"[inhoudsopgave]({cfg['id']}/chunks/00-index.md)" if index.exists() else "nog niet gemaakt"

    regels = [
        "# Bronnen",
        "",
        "Bronnen die dit voorbeeld gebruikt. Volg de link onder **Bron** om de tekst te lezen zoals de uitgever hem publiceert.",
        "De link onder **Chunks** gaat naar dezelfde tekst, opgedeeld per artikel, zodat AI hem gericht kan lezen.",
        "",
        "Dit overzicht wordt gemaakt uit [bronnen.yaml](bronnen.yaml) met `python scripts/bron_naar_chunks.py`.",
        "Pas bronnen en toelichtingen aan in bronnen.yaml, niet hier.",
        "",
        "## Overzicht",
        "",
        "| Bron | Waarvoor | Chunks |",
        "|---|---|---|",
    ]
    for cfg in register["bronnen"]:
        regels.append(f"| [{cfg['titel']}]({cfg['url']}) | {cfg['doel']} | {chunks_link(cfg)} |")

    kopjes = [("onderwerp", "Waar gaat het over?"), ("doel", "Wat is het doel?"), ("betrokkenen", "Wie raakt het?")]
    for cfg in register["bronnen"]:
        toel = cfg.get("toelichting")
        if not toel:
            continue
        regels += ["", f"## {cfg['afkorting']}: {cfg['titel']}", ""]
        regels.append(f"**{cfg['afkorting']}** staat voor *{cfg['titel']}*.")
        regels.append(f"Bron: [{cfg['url']}]({cfg['url']}). Chunks: {chunks_link(cfg)}.")
        for sleutel, kop in kopjes:
            if toel.get(sleutel):
                regels += ["", f"### {kop}", "", _schoon(toel[sleutel])]
        if toel.get("status"):
            regels += ["", f"> {_schoon(toel['status'])}"]
    inhoud = _header(
        {
            "titel": "Bronnen",
            "doel": "Overzicht van de bronnen met links naar de leesbare tekst en naar de chunks.",
            "auteur": register["auteur"],
            "datum": vandaag,
            "wijziging": "Automatisch gemaakt uit bronnen.yaml met scripts/bron_naar_chunks.py.",
            "gegenereerd": True,
        }
    ) + "\n" + "\n".join(regels) + "\n"
    if _schrijf_als_gewijzigd(basis / "README.md", inhoud, vandaag):
        print(f"[overzicht] {(basis / 'README.md').relative_to(ROOT).as_posix()} bijgewerkt")


# ---------------------------------------------------------------------------
# Hoofdprogramma
# ---------------------------------------------------------------------------


def download(bron: Bron) -> None:
    bron.origineel.parent.mkdir(parents=True, exist_ok=True)
    url = bron.config["download"]
    print(f"  ophalen: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "bron-naar-chunks/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        bron.origineel.write_bytes(r.read())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", help="bron-id's; leeg betekent alle bronnen")
    ap.add_argument("--download", action="store_true", help="origineel eerst (opnieuw) ophalen")
    args = ap.parse_args()

    registers = vind_registers()
    if not registers:
        print("Geen bronnen/bronnen.yaml gevonden.")
        return 1

    alle_ok = True
    for pad in registers:
        basis = pad.parent
        print(f"== {basis.relative_to(ROOT).as_posix()}")
        register = yaml.safe_load(pad.read_text(encoding="utf-8"))
        auteur = register["auteur"]
        for cfg in register["bronnen"]:
            if args.ids and cfg["id"] not in args.ids:
                continue
            bron = Bron(cfg["id"], cfg, basis)
            print(f"[{bron.id}] {cfg['titel']}")
            lezer = LEZERS.get(cfg["type"])
            if lezer is None:
                print(f"  overgeslagen: geen lezer voor type '{cfg['type']}'")
                continue
            if args.download or not bron.origineel.exists():
                download(bron)
            chunks, meta = lezer(bron)
            if controleer(bron, chunks):
                schrijf(bron, chunks, meta, auteur)
            else:
                alle_ok = False
                print("  niets geschreven")
        schrijf_overzicht(register, basis)
    return 0 if alle_ok else 1


if __name__ == "__main__":
    sys.exit(main())
