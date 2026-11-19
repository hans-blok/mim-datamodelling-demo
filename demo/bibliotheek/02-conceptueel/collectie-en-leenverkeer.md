---
titel: Collectieplan, interbibliothecair leenverkeer en inkoop van digitale werken
doel: Het ORM-model collectie-en-leenverkeer in gewone zinnen, voor bespreking met een deskundige.
auteur: Hans Blok
datum: '2026-11-19'
wijziging: Automatisch gemaakt uit de .orm.yaml met scripts/orm_naar_factum.py.
gegenereerd: true
---

# Collectieplan, interbibliothecair leenverkeer en inkoop van digitale werken

> Voorstel van AI, nog niet gecontroleerd door een deskundige.

Bron van de waarheid is [collectie-en-leenverkeer.orm.yaml](collectie-en-leenverkeer.orm.yaml). Het Factum-model is [collectie-en-leenverkeer.orm.json](collectie-en-leenverkeer.orm.json).

## Waarom zo opgebouwd

Het model legt vast welk collectieplan geldt, wie deelneemt aan het interbibliothecaire leenverkeer, welk verzoek om een fysiek werk is gedaan en welke werken zijn ingekocht op welke voordracht. Taken en bevoegdheden die geen gegevens opleveren, zoals het vaststellen van het collectieplan in overeenstemming met vertegenwoordigers, zijn weggelaten. Lokale bibliotheek en provinciale ondersteuningsinstelling zijn als waarden van Soort deelnemer vastgelegd, omdat het script nog geen subtypen kent.

## Aannames en open vragen

- Subtypen zijn niet gemodelleerd (R28). Lokale bibliotheek en provinciale ondersteuningsinstelling zijn twee waarden van Soort deelnemer bij één entiteittype Deelnemer. Een deskundige moet beoordelen of een apart entiteittype per soort nodig is.
- De Koninklijke Bibliotheek is geen Deelnemer, omdat artikel 15 lid 1 alleen lokale bibliotheken en provinciale ondersteuningsinstellingen als deelnemers aan het leenverkeer noemt. Artikel 2 en artikel 7 zijn niet gelezen. Is de Koninklijke Bibliotheek ook deelnemer aan het netwerk, dan kan Soort deelnemer een waarde erbij krijgen.
- Het collectieplan geldt vanaf de vaststellingsdatum tot het volgende collectieplan is vastgesteld. Artikel 10 noemt alleen dat het elke vier jaar wordt vastgesteld, niet hoe lang een plan geldt.
- Een collectieplan geldt voor alle deelnemers aan het netwerk, daarom is het niet aan een Deelnemer gekoppeld.
- Een Leenverzoek betreft precies één Werk. Artikel 15 zegt niets over het aantal werken per verzoek.
- De gebruiker voor wie het verzoek is gedaan (artikel 15 lid 2 onder a en b) is niet vastgelegd. Persoon en Lidmaatschap uit het model lidmaatschap blijven buiten dit model.
- Of een Werk fysiek of digitaal is, is geen gegeven in dit model. Het staat bij de regels, omdat het alleen bepaalt waar het werk in voorkomt.
- Een Werk is hoogstens op één Voordracht ingekocht. De bron zegt niet of een werk opnieuw kan worden ingekocht.
- De Voordracht legt alleen het Inkoopbedrag vast waarop hij is afgestemd. Het jaar van het bedrag en de vertegenwoordigers die voordragen zijn niet gemodelleerd.

## Feittypen

### Collectieplan is vastgesteld op Vaststellingsdatum

Het collectieplan dat geldt, is het plan met de meest recente vaststellingsdatum tot en met vandaag.

Bron: [artikel 10 lid 1](../bronnen/wsob/chunks/h02-art10-collectieplan.md)

- Per Collectieplan hoogstens één Vaststellingsdatum.
- Elke Collectieplan komt hierin voor (verplicht).

| Collectieplan | Vaststellingsdatum |
|---|---|
| C01 | 2019-01-01 |
| C02 | 2023-01-01 |
| C03 | 2027-01-01 |

### Deelnemer is van de soort Soort deelnemer

Bron: AI-voorstel, gebaseerd op [artikel 15 lid 1](../bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md)

- Per Deelnemer hoogstens één Soort deelnemer.
- Elke Deelnemer komt hierin voor (verplicht).

| Deelnemer | Soort deelnemer |
|---|---|
| D01 | lokale bibliotheek |
| D02 | provinciale ondersteuningsinstelling |
| D03 | lokale bibliotheek |

### Leenverzoek is gedaan door Deelnemer

Bron: AI-voorstel, gebaseerd op [artikel 15 lid 2 onder a](../bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md)

- Per Leenverzoek hoogstens één Deelnemer.
- Elke Leenverzoek komt hierin voor (verplicht).

| Leenverzoek | Deelnemer |
|---|---|
| L01 | D01 |
| L02 | D01 |

### Leenverzoek is gericht aan Deelnemer

Bron: AI-voorstel, gebaseerd op [artikel 15 lid 2 onder b](../bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md)

- Per Leenverzoek hoogstens één Deelnemer.
- Elke Leenverzoek komt hierin voor (verplicht).

| Leenverzoek | Deelnemer |
|---|---|
| L01 | D02 |
| L02 | D03 |

### Leenverzoek betreft Werk

Hetzelfde werk kan in meer dan één verzoek voorkomen.

Bron: AI-voorstel, gebaseerd op [artikel 15 lid 2 onder a](../bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md)

- Per Leenverzoek hoogstens één Werk.
- Elke Leenverzoek komt hierin voor (verplicht).

| Leenverzoek | Werk |
|---|---|
| L01 | W01 |
| L02 | W01 |

### Werk is ingekocht op Voordracht

Een voordracht kan meer dan één ingekocht werk opleveren.

Bron: [artikel 18 lid 3](../bronnen/wsob/chunks/h04-art18-inkoop-digitale-werken.md)

- Per Werk hoogstens één Voordracht.

| Werk | Voordracht |
|---|---|
| W03 | V01 |
| W04 | V01 |

### Voordracht is afgestemd op Inkoopbedrag

Twee voordrachten kunnen op hetzelfde bedrag zijn afgestemd.

Bron: [artikel 18 lid 3](../bronnen/wsob/chunks/h04-art18-inkoop-digitale-werken.md)

- Per Voordracht hoogstens één Inkoopbedrag.
- Elke Voordracht komt hierin voor (verplicht).

| Voordracht | Inkoopbedrag |
|---|---|
| V01 | 250000.00 |
| V02 | 250000.00 |

## Overige regels

Deze regels zijn niet als ORM-regel in het diagram te tekenen.

- Het collectieplan wordt elke vier jaar vastgesteld, dus tussen twee opeenvolgende vaststellingsdatums zitten vier jaar. Bron: [artikel 10 lid 1](../bronnen/wsob/chunks/h02-art10-collectieplan.md)
- Een Leenverzoek is gedaan door een Deelnemer van de soort lokale bibliotheek. Bron: [artikel 15 lid 2 onder a](../bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md)
- Een Leenverzoek betreft een fysiek Werk. Bron: [artikel 15 lid 2 onder a](../bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md)
- Een Werk dat is ingekocht op een Voordracht is een digitaal werk voor de landelijke digitale bibliotheek. Bron: [artikel 18 lid 1](../bronnen/wsob/chunks/h04-art18-inkoop-digitale-werken.md)
- De inkoop van werken wordt alleen verricht op een Voordracht, en die Voordracht is afgestemd op het Inkoopbedrag. Bron: [artikel 18 lid 3](../bronnen/wsob/chunks/h04-art18-inkoop-digitale-werken.md)
