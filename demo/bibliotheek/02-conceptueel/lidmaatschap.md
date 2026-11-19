---
titel: Lidmaatschap van de openbare bibliotheek
doel: Het ORM-model lidmaatschap in gewone zinnen, voor bespreking met een deskundige.
auteur: Hans Blok
datum: '2026-11-19'
wijziging: Automatisch gemaakt uit de .orm.yaml met scripts/orm_naar_factum.py.
gegenereerd: true
---

# Lidmaatschap van de openbare bibliotheek

> Voorstel van AI, nog niet gecontroleerd door een deskundige.

Bron van de waarheid is [lidmaatschap.orm.yaml](lidmaatschap.orm.yaml). Het Factum-model is [lidmaatschap.orm.json](lidmaatschap.orm.json).

## Waarom zo opgebouwd

Het model volgt artikel 12 en 13. Een lidmaatschap is een eigen begrip, omdat het van een persoon is en een of beide voorzieningen kan omvatten. Het soort voorziening (fysiek of digitaal) is een waarde, omdat artikel 12 lid 3 die twee soorten noemt. De geboortedatum zit in het model, omdat de contributievrijstelling van de leeftijd afhangt.

## Aannames en open vragen

- Een lidmaatschap omvat minstens een voorziening. De wet zegt "een fysieke voorziening, de digitale voorziening of beide".
- De contributie hangt aan het lidmaatschap en niet aan de combinatie van lidmaatschap en voorziening. Dat is een vereenvoudiging voor de demo.
- De leeftijd volgt uit de geboortedatum en de peildatum van het lidmaatschap. De bron noemt geen peildatum.
- Contributiebedrag 0,00 betekent dat geen contributie wordt geheven. De wet noemt het bedrag niet.

## Feittypen

### Persoon is als ingezetene ingeschreven in Register

Bron: [artikel 12 lid 1](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)

- Elke combinatie van Persoon en Register komt hoogstens één keer voor.

| Persoon | Register |
|---|---|
| P001 | basisregistratie personen |
| P002 | basisregistratie personen |
| P003 | basisadministratie BES |

### Persoon heeft Geboortedatum

Nodig om te bepalen of iemand jonger is dan achttien jaar.

Bron: AI-voorstel, gebaseerd op [artikel 13 lid 1 en 2](../bronnen/wsob/chunks/h02-art13-contributievrijstelling-jeugd-lokale-bibliotheken.md)

- Per Persoon hoogstens één Geboortedatum.
- Elke Persoon komt hierin voor (verplicht).

| Persoon | Geboortedatum |
|---|---|
| P001 | 2015-03-12 |
| P002 | 1990-07-01 |
| P003 | 1990-07-01 |

### Lidmaatschap is van Persoon

Bron: [artikel 12 lid 1](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)

- Per Lidmaatschap hoogstens één Persoon.
- Elke Lidmaatschap komt hierin voor (verplicht).

| Lidmaatschap | Persoon |
|---|---|
| L001 | P001 |
| L002 | P002 |
| L003 | P002 |

### Lidmaatschap omvat Voorziening

Bron: [artikel 12 lid 2](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)

- Elke combinatie van Lidmaatschap en Voorziening komt hoogstens één keer voor.
- Elke Lidmaatschap komt hierin voor (verplicht).

| Lidmaatschap | Voorziening |
|---|---|
| L001 | V01 |
| L002 | V01 |
| L002 | V02 |
| L003 | V02 |

### Voorziening is van Soort voorziening

Bron: [artikel 12 lid 3](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)

- Per Voorziening hoogstens één Soort voorziening.
- Elke Voorziening komt hierin voor (verplicht).

| Voorziening | Soort voorziening |
|---|---|
| V01 | fysiek |
| V02 | digitaal |

### Lidmaatschap heeft Contributiebedrag

L001 is van een jongere en kost dus niets, L002 is van een volwassene.

Bron: AI-voorstel, gebaseerd op [artikel 13 lid 1 en 2](../bronnen/wsob/chunks/h02-art13-contributievrijstelling-jeugd-lokale-bibliotheken.md)

- Per Lidmaatschap hoogstens één Contributiebedrag.
- Elke Lidmaatschap komt hierin voor (verplicht).

| Lidmaatschap | Contributiebedrag |
|---|---|
| L001 | 0.00 |
| L002 | 40.00 |
| L003 | 25.00 |

## Overige regels

Deze regels zijn niet als ORM-regel in het diagram te tekenen.

- Een persoon kan alleen lid worden als die als ingezetene is ingeschreven in de basisregistratie personen of in een basisadministratie BES. Bron: [artikel 12 lid 1](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)
- Een lidmaatschap kan een fysieke voorziening (een lokale bibliotheek), de digitale voorziening (de landelijke digitale bibliotheek) of beide omvatten. Bron: [artikel 12 lid 2 en 3](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)
- Voor een lidmaatschap van een persoon jonger dan achttien jaar is het Contributiebedrag voor het uitlenen door lokale bibliotheken 0,00. Bron: [artikel 13 lid 1](../bronnen/wsob/chunks/h02-art13-contributievrijstelling-jeugd-lokale-bibliotheken.md)
- Voor een persoon jonger dan achttien jaar wordt geen tarief, contributie of geldelijke bijdrage vastgesteld voor toegang tot de door de Koninklijke Bibliotheek aangewezen digitale werken. Bron: [artikel 13 lid 2](../bronnen/wsob/chunks/h02-art13-contributievrijstelling-jeugd-lokale-bibliotheken.md)
- Onze Minister of het college van burgemeester en wethouders of bestuurscollege kan bepalen dat ook andere groepen natuurlijke personen lid kunnen worden. Dit staat niet in het model. Bron: [artikel 12 lid 4](../bronnen/wsob/chunks/h02-art12-lidmaatschap.md)
