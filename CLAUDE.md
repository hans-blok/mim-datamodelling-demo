# CLAUDE.md

Dit bestand geeft Claude Code (claude.ai/code) richtlijnen voor het werken in deze repository.

## Wat is dit?

Dit is een demo- en leeromgeving voor datamodellering. We verkennen hier:

- **ORM** (Object-Role Modeling) om begrippen, feiten en regels duidelijk te maken en te bespreken;
- **Factum**, de extensie voor Visual Studio Code die het modelleren ondersteunt;
- **AI** bij het opstellen, controleren en toelichten van modellen.

De inhoud is verkennend. Het is geen vastgesteld datamodel en geen productieklare oplossing. Zie [README.md](README.md) voor doel, verkenningsvragen en werkwijze.

Alle inhoud is in het **Nederlands**, met uitzondering van technische standaardtermen.

## Wat hoort hier niet in?

- Geen architectuurwerk: geen ArchiMate, C4, TOGAF, ADRs of oplossingsontwerpen.
- Geen Gherkin of andere BDD-specificaties.
- Geen software die gebouwd moet worden. Het gaat om modellen, voorbeelden en leerervaringen. Kleine hulpscripts in `scripts/`, zoals het omzetten van bronnen, mogen wel. Die zijn hulpmiddel, geen onderwerp van de demo.

Wordt er iets gevraagd dat hierbuiten valt, meld dat dan kort in plaats van het stilzwijgend toe te voegen.

## Werkwijze bij modelleren

1. Kies een klein, herkenbaar voorbeeld.
2. Breng de begrippen en feiten in kaart en modelleer ze met ORM.
3. Bekijk en bespreek het model in Factum in Visual Studio Code.
4. Zet AI gericht in voor een voorstel, controle of toelichting.
5. Laat het model en de AI-uitvoer controleren door een deskundige.

### Richtlijnen voor ORM

- Begin bij **feiten in gewone zinnen**, bijvoorbeeld "Persoon woont op Adres". Teken of schrijf daarna pas het model uit.
- Leg per feittype de **rollen**, de **uniciteitsregels** en of een rol **verplicht** is vast.
- Houd begrippen en namen **consistent**. Gebruik dezelfde term overal, ook in voorbeelden en toelichting.
- Voeg bij elk model een paar **voorbeeldgegevens** toe. Die maken regels toetsbaar en bespreekbaar.
- Schrijf bij elk begrip een korte definitie in gewone taal. Verzin geen eigen definitie als er een bron is, verwijs dan naar die bron.
- Modelleer wat nodig is voor het voorbeeld. Maak het niet groter dan de demo vraagt.

### Richtlijnen voor AI

- Een AI-uitkomst is niet vanzelf correct. Maak altijd duidelijk wat door AI is voorgesteld en wat is gecontroleerd.
- Leg voor een voorstel kort uit **waarom** het model zo is opgebouwd, zodat een deskundige het kan beoordelen.
- Noem onzekerheden en aannames. Verzin geen feiten, regels of bronnen.
- Controleer modellen op juistheid, volledigheid en begrijpelijkheid.

## Publieke repository

Deze repository is publiek. Niets in de inhoud mag herleidbaar zijn tot een gemeente of andere organisatie. Noem dus geen gemeentenamen, organisatienamen, interne systemen, interne projecten of echte gegevens. Gebruik neutrale, verzonnen voorbeelden.

## Bestanden en structuur

De indeling volgt de vier beschouwingsniveaus van MIM 1.2 (Metamodel Informatie Modellering, Geonovum):

```
demo/
  {voorbeeld}/
    README.md          korte uitleg van het voorbeeld
    01-begrippen/      niveau 1: begrippen en definities (buiten MIM)
    02-conceptueel/    niveau 2: ORM-model met feittypen, rollen en regels
    03-logisch/        niveau 3: gegevensmodel voor uitwisseling
    04-fysiek/         niveau 4: technisch schema, alleen ter illustratie
    bronnen/
      bronnen.yaml     register van de bronnen van dit voorbeeld
      README.md        overzicht met links naar de bronnen (gegenereerd)
      {bron}/
        origineel/     het opgehaalde bronbestand, ongewijzigd
        chunks/        Markdown per artikel, met 00-index.md als ingang
        chunks.jsonl   dezelfde chunks in één bestand
scripts/               hulpscripts, zie scripts/README.md
```

- Bronnen staan per voorbeeld in `demo/{voorbeeld}/bronnen/`. Een nieuwe bron zet je in `bronnen.yaml` van dat voorbeeld en verwerk je met `python scripts/bron_naar_chunks.py`. Het script vindt zelf elke `bronnen/bronnen.yaml`. Kies een gestructureerde bron (XML) boven PDF, voor wetten de geldende tekst van wetten.overheid.nl.
- Wijzig gegenereerde chunks (`gegenereerd: true` in de header) niet met de hand. Pas het script aan en draai het opnieuw.
- Lees bij het zoeken in een bron eerst `chunks/00-index.md` en haal daarna alleen de nodige chunks op. Verwijs in modellen naar de bron met artikel en lid.
- Een ORM-model maak je met de agent `orm-modelleur`. De bron van de waarheid is `02-conceptueel/{naam}.orm.yaml`. `python scripts/orm_naar_factum.py` maakt daar de `.orm.json` voor Factum, het model in zinnen en de begrippenlijst van. Wijzig die gegenereerde bestanden niet met de hand.
- Houd per voorbeeld de bestanden bij elkaar in een eigen map onder `demo/`, met een korte uitleg erbij. Kopieer `demo/voorbeeld-01` als sjabloon.
- Niveau 1 en 4 liggen buiten MIM. Laat die mappen leeg of weg als een voorbeeld ze niet nodig heeft.
- Een ORM-model hoort bij niveau 2. Leg in de README van het voorbeeld uit hoe de ORM-elementen zich verhouden tot de MIM-begrippen.
- Werk bij een nieuw voorbeeld de sectie "Inhoud van de repository" in [README.md](README.md) bij.
- Volg voor modelbestanden het formaat dat Factum gebruikt. Controleer dat bij het eerste model.

## Schrijfconventies

### Geen koppeltekens of gedachtestreepjes als interpunctie

Gebruik **nooit** een koppelteken (`-`), en-streepje (`–`) of gedachtestreepje (`—`) om een bijzin, toelichting, nuance of afsluitende constatering aan een zin te plakken. Dit geldt voor alle uitvoer: bestanden, mails, documentatie, commit messages en antwoorden in het gesprek.

Herformuleer in plaats daarvan met een komma, een dubbele punt of een nieuwe zin.

Fout:

> Elk feittype heeft minstens één uniciteitsregel — anders is het model niet te toetsen.

Goed:

> Elk feittype heeft minstens één uniciteitsregel. Anders is het model niet te toetsen.

**Wat wél mag**, want dit is geen interpunctie:

- Koppeltekens in samenstellingen en afleidingen: `ORM-model`, `feittype-definitie`, `niet-verplicht`.
- Koppeltekens in namen, bestandsnamen en identifiers: `mim-datamodelling-demo`.
- Streepjes als lijstteken aan het begin van een regel in Markdown.
- Een streepje als scheidingsteken in een tabelrij of versiebeheerregel: `Hans Blok - 2026 09 09 - Eerste vastlegging`.

Bij twijfel: als het streepje weggelaten kan worden door de zin te splitsen of een komma te zetten, dan is het interpunctie en moet het weg.

### Gegevens en informatie

Maak onderscheid tussen **gegevens** en **informatie**. Gegevens zijn wat wordt vastgelegd, opgeslagen, uitgewisseld en beheerd. Informatie ontstaat pas wanneer iemand gegevens in een context interpreteert.

Gebruik **gegevens** wanneer het gaat om:

- wat in een registratie, database of model staat ("persoonsgegevens", "adresgegevens");
- vastleggen, opslaan, synchroniseren, migreren of dubbel beheren;
- de bron van iets ("eenmalig vastleggen bij de bron").

Gebruik **informatie** wanneer het gaat om:

- wat een gebruiker nodig heeft om zijn werk te doen ("informatiebehoefte", "welke informatie heeft de medewerker nodig");
- vaktermen en namen waarin het woord vastligt: informatiebeheer, informatieobject, informatievoorziening.

**Documenten** zijn informatieobjecten en heten ook zo. Noem ze apart naast gegevens wanneer beide bedoeld zijn: "gegevens en documenten".

Fout:

> De informatie staat in verschillende registraties.

Goed:

> De gegevens staan in verschillende registraties.

### Schrijf zoals mensen praten

Teksten moeten klinken zoals een collega ze zou zeggen. Gebruik geen ambtelijke of juridische taal, en geen woorden die er alleen staan om iets stelliger of voorzichtiger te laten klinken.

| Vermijd | Schrijf in plaats daarvan |
|---|---|
| expliciet, uitdrukkelijk | meestal weglaten; anders "duidelijk" of "apart" |
| in beginsel | "meestal", "normaal gesproken", of noem de uitzondering gewoon |
| conform | volgens |
| middels | met, via |
| ten behoeve van | voor |
| teneinde | om |
| derhalve, aldus | daarom, dus |
| dient te, dienen te | moet, moeten |
| waarborgen, borgen | zorgen dat, vastleggen; alleen laten staan als het een vakterm is |
| inzichtelijk maken | laten zien |
| in het kader van | voor, bij |
| reeds | al |
| tevens | ook |
| ten aanzien van, met betrekking tot, omtrent | over, voor |
| c.q. | of |
| betreffende, desbetreffende | die, deze, of weglaten |
| welke (als betrekkelijk voornaamwoord) | die, dat |
| faciliteren | mogelijk maken, ondersteunen |
| voorafgaand aan | vóór |
| nader (onderzoek, uitwerking) | verder, later |

Fout:

> Ten behoeve van de controle worden middels een script de feittypen welke reeds zijn vastgelegd, inzichtelijk gemaakt.

Goed:

> Voor de controle laat een script zien welke feittypen al zijn vastgelegd.

**Wat wél mag:**

- Letterlijke citaten uit bronnen blijven ongewijzigd, ook als ze deze woorden bevatten.
- Vaktermen met een vaste betekenis blijven staan.
- In een eis of regel mag de toon streng blijven. Schrijf dan "moet", niet "dient te".

Bij twijfel: lees de zin hardop. Zou je hem zo tegen een collega zeggen? Zo niet, herschrijf hem.

## YAML-header in Markdown-bestanden

Elk `.md`-bestand dat je in deze repository maakt, krijgt bovenaan een YAML-header met deze velden:

```yaml
---
titel: {titel van het document}
doel: {waarvoor het document is, in één zin}
auteur: Hans Blok
datum: {jjjj-mm-dd, de datum van vandaag}
wijziging: {wat er in deze versie is veranderd; bij een nieuw bestand "Eerste versie."}
---
```

- Laat geen veld leeg. Is het doel niet uit de context af te leiden, vraag het dan na.
- Pas je een bestaand `.md`-bestand met zo'n header inhoudelijk aan, werk dan `datum` en `wijziging` bij.
- Heeft een bestaand bestand nog geen header, voeg hem dan toe wanneer je het bestand aanpast.
- Uitzondering: bestanden waarvan het formaat door een tool of agent is voorgeschreven, zoals `.prompt.md`, `.agent.md`, `SKILL.md`, `CLAUDE.md` en `MEMORY.md`, houden hun eigen header.

## Toestemming voor web fetches

Claude mag zonder voorafgaande toestemming publieke webpagina's en documentatie ophalen wanneer dat nodig is om ORM, Factum of andere tooling te verifiëren voor werk in deze repository.

Voorwaarden:

- Alleen publiek toegankelijke bronnen gebruiken.
- Geen login, betaalmuur of privéomgevingen benaderen.
- Geen persoonsgegevens of vertrouwelijke repository-inhoud delen met externe diensten.
- Web fetches beperken tot taakrelevante verificatie en brononderzoek.
- Alleen vragen bij twijfel over vertrouwelijkheid of externe publicatie van interne gegevens.
