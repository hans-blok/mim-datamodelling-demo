---
titel: "Prompt: ORM-model functies en publieke waarden"
doel: Prompt voor de demo waarin de agent orm-modelleur een ORM-model maakt van artikel 4 en 5 van de Wsob.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Prompt: ORM-model functies en publieke waarden

In deze demo maakt de agent `orm-modelleur` een ORM-model van de publieke waarden en de bibliotheekfuncties van een openbare bibliotheekvoorziening. De bron is de Wet stelsel openbare bibliotheekvoorzieningen (Wsob), artikel 4 en 5.

Dit is het kleinste thema. Het laat goed zien wat er gebeurt als een wet vooral opsommingen geeft en weinig feiten: het model draait om waardetypen met toegestane waarden. Een goede vraag om mee te eindigen is of je dit wel moet modelleren.

## Voorbereiding

1. Open de repository in Visual Studio Code en start Claude Code.
2. Controleer dat de agent er is: typ `/agents` en kijk of `orm-modelleur` in de lijst staat.
3. Controleer dat de scripts werken:

    ```
    pip install -r scripts/requirements.txt
    python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml
    ```

4. Open `demo/bibliotheek/bronnen/wsob/chunks/h01-art05-bibliotheekfuncties.md` in een tabblad. Dan kun je de wettekst naast het resultaat laten zien.

## De prompt

Plak deze tekst in Claude Code:

```text
Gebruik de orm-modelleur.

Voorbeeld: bibliotheek. Bron: wsob. Naam: functies-en-publieke-waarden.

Onderwerp: de publieke waarden en de bibliotheekfuncties van een openbare
bibliotheekvoorziening. Gebruik artikel 4 en 5, en artikel 1 en 2 voor de
begripsbepalingen. Lees geen andere artikelen.

Afbakening:
- Modelleer welke gegevens je nodig hebt om vast te leggen welke functies een
  openbare bibliotheekvoorziening vervult en op welke publieke waarden haar
  taak rust.
- Neem de vijf functies uit artikel 5 en de vijf waarden uit artikel 4 over
  als toegestane waarden, letterlijk zoals de wet ze noemt.
- Artikel 5 zegt dat een voorziening "in ieder geval" deze functies omvat.
  Leg dat vast als regel. Zeg in aannames wat "in ieder geval" betekent voor
  de toegestane waarden: mag er een zesde functie bij?
- Verzin geen feiten die de wet niet noemt, zoals activiteiten of
  programma's die bij een functie horen. Levert de wet te weinig feiten op,
  zeg dat dan in aannames in plaats van het model op te vullen.
- Gebruik dezelfde namen als in
  demo/bibliotheek/01-begrippen/lidmaatschap-begrippen.md waar een begrip
  hetzelfde is.

Classificeer elk begrip met een soortbegrip (R9) en geef bij elk begrip en
feittype een bron of gebaseerd_op. Houd het model op hooguit 4 objecttypen.
```

## Wat je daarna laat zien

De agent werkt ongeveer een minuut. Daarna:

| Laat zien | Waar | Waar je op let |
|---|---|---|
| De YAML die de agent schreef | `demo/bibliotheek/02-conceptueel/functies-en-publieke-waarden.orm.yaml` | De lijsten met toegestane waarden |
| Het model in Factum | `functies-en-publieke-waarden.orm.json` | Hoe waardebeperkingen in het diagram staan |
| De begrippenlijst | `demo/bibliotheek/01-begrippen/functies-en-publieke-waarden-begrippen.md` | Welke definities de wet geeft en welke AI heeft voorgesteld |
| Het model in zinnen | `demo/bibliotheek/02-conceptueel/functies-en-publieke-waarden.md` | De regel uit artikel 5 in gewone taal |

## Om te bespreken

- **Geen definities in de wet.** Artikel 4 noemt onafhankelijkheid, betrouwbaarheid en de andere waarden, maar definieert ze niet. Wat heeft de agent als definitie gegeven, en staat er duidelijk bij dat het een voorstel is?
- **Gesloten of open lijst?** Een waardebeperking sluit andere waarden uit. "In ieder geval" laat ruimte voor meer. Hoe lost de agent die spanning op?
- **Is dit gegevens?** Als elke voorziening alle vijf functies vervult, wat leg je dan nog vast per voorziening? Is dit een gegevensmodel of eigenlijk een begrippenlijst?
- **Begrippen of model.** Zou dit thema beter alleen op niveau 1 (begrippen) passen dan op niveau 2?

## Als het misgaat

- **De agent staat niet in `/agents`.** Herstart Claude Code, of vraag: "Lees .claude/agents/orm-modelleur.md en volg die instructies" met daarachter de prompt.
- **Het script geeft een FOUT.** De agent lost die meestal zelf op. Gebeurt dat niet, laat de melding dan zien: het is een goed voorbeeld van hoe het script de AI controleert.
