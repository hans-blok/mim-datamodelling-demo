---
titel: Datamodellering-demo
doel: Uitleg over het doel, de werkwijze en de status van de demo voor datamodellering met ORM, Factum en AI.
auteur: Hans Blok
datum: 2026-11-18
wijziging: Link naar de GitHub Pages-site toegevoegd.
---

# Datamodellering-demo

Deze repository is een demo- en leeromgeving. We verkennen hier tooling voor datamodellering, waaronder ORM (Object-Role Modeling), de Factum-extensie voor Visual Studio Code en de combinatie van modelleringstooling en AI. De inhoud is verkennend en is geen vastgesteld datamodel of productieklare oplossing.

De site staat op [hans-blok.github.io/mim-datamodelling-demo](https://hans-blok.github.io/mim-datamodelling-demo/).

## Doel

Met deze demo willen we leren:

- hoe ORM helpt om begrippen, feiten en regels duidelijk te maken en te bespreken;
- hoe Factum in Visual Studio Code het modelleren ondersteunt;
- hoe AI kan helpen bij het opstellen, controleren of toelichten van modellen;
- welke beperkingen en aandachtspunten er zijn, en welke kwaliteitscontroles nodig zijn.

## Verkenningsvragen

- Welke begrippen en regels worden duidelijker door ze met ORM te modelleren?
- Hoe bruikbaar is Factum voor het maken en bespreken van een model?
- Voor welke taken kan AI ondersteuning bieden, en waar schiet die tekort?
- Hoe controleren we modellen en AI-uitvoer op juistheid, volledigheid en begrijpelijkheid?

## Inhoud van de repository

De voorbeelden staan in [demo](demo). Elk voorbeeld heeft een eigen map, ingedeeld naar de vier beschouwingsniveaus van MIM 1.2 (Metamodel Informatie Modellering, Geonovum):

| Map | Niveau | In scope van MIM? |
|---|---|---|
| 01-begrippen | Model van begrippen | Nee |
| 02-conceptueel | Conceptueel informatiemodel | Ja |
| 03-logisch | Logisch gegevensmodel | Ja |
| 04-fysiek | Fysiek gegevensmodel, alleen ter illustratie | Nee |

De [homepage](docs/index.md) is de ingang tot de demo. De [kennisbank](docs/kennisbank/index.md) bevat achtergrond, zoals een korte uitleg van [MIM](docs/kennisbank/mim.md) met de bronnen.

Er is nog geen echt voorbeeld uitgewerkt. [demo/voorbeeld-01](demo/voorbeeld-01) is een leeg sjabloon.

## Werkwijze

1. Kies een klein, herkenbaar voorbeeld.
2. Breng de relevante begrippen en feiten in kaart en modelleer ze met ORM.
3. Bekijk en bespreek het model in Factum in Visual Studio Code.
4. Zet AI gericht in voor bijvoorbeeld een voorstel, controle of toelichting.
5. Laat het model en de AI-uitvoer controleren door een deskundige.

## Status en gebruik

Dit is een experimentele demo om te leren en mogelijkheden te evalueren. Controleer modellen, voorbeelden en AI-uitvoer voordat je ze gebruikt voor ontwerp- of besluitvorming. Een AI-uitkomst is niet vanzelf correct.
