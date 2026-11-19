---
titel: Scripts
doel: Uitleggen welke hulpscripts er zijn en hoe je ze gebruikt.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Script orm_naar_factum.py en de agent orm-modelleur toegevoegd.
---

# Scripts

De scripts hier zijn hulpmiddelen bij het modelleren. Ze zijn geen onderwerp van de demo.

| Script | Wat het doet |
|---|---|
| [bron_naar_chunks.py](#bron_naar_chunkspy) | Bronnen, zoals wetten, opdelen in Markdown per artikel |
| [orm_naar_factum.py](#orm_naar_factumpy) | Een compact ORM-model in YAML omzetten naar een Factum-model |
| `agent_naar_html.py` | Een agentbestand omzetten naar een leesbare HTML-pagina, bijvoorbeeld `python scripts/agent_naar_html.py .claude/agents/orm-modelleur.md docs/agents/orm-modelleur.html` |

Installeren:

```
pip install -r scripts/requirements.txt
```

## ORM-model laten maken door AI

De agent [orm-modelleur](../.claude/agents/orm-modelleur.md) maakt een ORM-model uit de bronnen van een voorbeeld. Vraag het in Claude Code zo:

```
Gebruik de orm-modelleur. Voorbeeld: bibliotheek. Bron: wsob.
Onderwerp: lidmaatschap van de openbare bibliotheek. Naam: lidmaatschap.
```

De agent gebruikt zo weinig mogelijk tokens:

- hij leest de inhoudsopgave van de bron en daarna alleen de artikelen die het onderwerp nodig heeft;
- hij schrijft een korte YAML in plaats van de lange Factum-JSON, en het script doet de rest;
- hij leest wat het script maakt niet terug en geeft een kort antwoord.

## orm_naar_factum.py

```
python scripts/orm_naar_factum.py demo/{voorbeeld}/02-conceptueel/{naam}.orm.yaml
```

De YAML is de bron van de waarheid. Het script maakt:

| Bestand | Inhoud |
|---|---|
| `02-conceptueel/{naam}.orm.json` | het model voor Factum |
| `02-conceptueel/{naam}.md` | het model in zinnen, met regels en voorbeeldgegevens, voor de deskundige |
| `01-begrippen/{naam}-begrippen.md` | de begrippen met definitie en een link naar het bronartikel |

Het script schrijft alleen als alles klopt:

- elk begrip heeft een definitie, elke entiteit een referentie (`ref`);
- elk feittype heeft een uniciteitsregel die lang genoeg is;
- de voorbeeldgegevens houden zich aan de uniciteitsregels en de toegestane waarden;
- het resultaat voldoet aan het [schema van Factum](https://www.factum-orm.com/schema/orm-model-2.schema.json).

Daarnaast meldt het met "let op" wat de moeite van bekijken waard is, zoals een verplichte rol zonder voorbeeld of een streepje als leesteken in een definitie.

Posities die je in Factum verschuift, blijven bij opnieuw draaien bewaard. Andere wijzigingen in de `.orm.json` gaan verloren, dus pas die aan in de YAML. Het formaat van de YAML staat in de [agent](../.claude/agents/orm-modelleur.md).

## bron_naar_chunks.py

Zet bronnen, zoals wetten, om naar kleine Markdown-bestanden ("chunks") die AI gericht kan lezen en citeren. Eén chunk is één artikel. Een artikel langer dan `max_woorden` wordt per lid gesplitst.

### Draaien

```
python scripts/bron_naar_chunks.py               alle bronnen
python scripts/bron_naar_chunks.py wsob          één bron
python scripts/bron_naar_chunks.py --download    origineel opnieuw ophalen
```

Het script zoekt zelf elk `bronnen/bronnen.yaml` in de repository, bijvoorbeeld `demo/bibliotheek/bronnen/bronnen.yaml`. Per map `bronnen/` schrijft het een `README.md` met een overzicht van de bronnen en links naar de leesbare tekst. Per bron komt in `bronnen/{id}/`:

| Pad | Inhoud |
|---|---|
| `origineel/` | het opgehaalde bestand, ongewijzigd |
| `chunks/00-index.md` | inhoudsopgave; AI leest die eerst |
| `chunks/*.md` | één chunk per artikel, met YAML-header en link naar het artikel op wetten.overheid.nl |
| `chunks.jsonl` | alle chunks als platte tekst in één bestand, voor zoektools |

### Controle

Het script schrijft alleen als de controle in orde is:

- het aantal chunks klopt met `verwacht` in `bronnen.yaml`;
- de woorden van elke chunk zijn gelijk aan die in het origineel, er gaat dus geen tekst verloren;
- er staan geen kapotte tekens in.

Het script schrijft een bestand alleen als de tekst echt veranderd is. Opnieuw draaien geeft dus geen onnodige wijzigingen in git.

### Een bron toevoegen

1. Zet de bron in `bronnen.yaml` van het voorbeeld, bijvoorbeeld [demo/bibliotheek/bronnen/bronnen.yaml](../demo/bibliotheek/bronnen/bronnen.yaml), met een `id`, `url`, `type`, `download`-adres en `doel`. Heeft het voorbeeld nog geen map `bronnen`, kopieer dan dat bestand en vervang de bronnen.
2. Draai het script. Het haalt het origineel op en maakt de chunks.
3. Leg een paar chunks naast het origineel en controleer ze.

Wetten van wetten.overheid.nl gebruiken type `bwb-xml`. Het downloadadres van een wet is:

```
https://repository.officiele-overheidspublicaties.nl/bwb/{BWB-id}/{datum}_0/xml/{BWB-id}_{datum}_0.xml
```

### Een brontype toevoegen

Voor een nieuw type, zoals PDF of HTML, schrijf je een lezer: een functie die een `Bron` leest en een lijst `Chunk`-objecten teruggeeft. Zet hem in `LEZERS` in het script. Schrijven en controleren werken dan vanzelf.

Kies waar het kan een gestructureerde bron (XML) boven PDF. In XML zijn artikelen en leden al gemarkeerd. Uit PDF komen afgebroken woorden, kop- en voetregels en soms kapotte tekens.
