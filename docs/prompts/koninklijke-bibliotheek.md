---
titel: "Prompt: ORM-model Koninklijke Bibliotheek en landelijke digitale bibliotheek"
doel: Prompt voor de demo waarin de agent orm-modelleur een ORM-model maakt van artikel 9, 11 en 17 van de Wsob.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Prompt: ORM-model Koninklijke Bibliotheek en landelijke digitale bibliotheek

In deze demo maakt de agent `orm-modelleur` een ORM-model van de taken van de Koninklijke Bibliotheek, de landelijke digitale bibliotheek en de gegevens die voorzieningen aanleveren. De bron is de Wet stelsel openbare bibliotheekvoorzieningen (Wsob), artikel 9, 11 en 17.

Dit thema is interessant omdat artikel 11 zelf over gegevenslevering gaat. De wet zegt hier dus heel direct welke gegevens van wie naar wie gaan.

## Voorbereiding

1. Open de repository in Visual Studio Code en start Claude Code.
2. Controleer dat de agent er is: typ `/agents` en kijk of `orm-modelleur` in de lijst staat.
3. Controleer dat de scripts werken:

    ```
    pip install -r scripts/requirements.txt
    python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml
    ```

4. Open `demo/bibliotheek/bronnen/wsob/chunks/h02-art11-gegevenslevering.md` in een tabblad. Dan kun je de wettekst naast het resultaat laten zien.

## De prompt

Plak deze tekst in Claude Code:

```text
Gebruik de orm-modelleur.

Voorbeeld: bibliotheek. Bron: wsob. Naam: koninklijke-bibliotheek.

Onderwerp: de taken van de Koninklijke Bibliotheek, het in stand houden van
de landelijke digitale bibliotheek en de levering van gegevens. Gebruik
artikel 9, 11 en 17, en artikel 1 voor de begripsbepalingen. Lees geen
andere artikelen.

Afbakening:
- Modelleer welke gegevens je nodig hebt om te weten welke voorziening welke
  gegevens levert, aan wie en voor welk doel (artikel 11), welk reglement
  voor de toegang tot digitale werken geldt en welk beheerplan bij welk
  instellingsplan hoort (artikel 17).
- Artikel 11 lid 2 zegt dat de gegevens voor de minister niet tot de persoon
  herleidbaar mogen zijn. Leg dat vast als regel.
- De taken in artikel 9 en artikel 17 lid 1 zijn geen gegevens. Neem ze op
  als toegestane waarden van een waardetype als je ze nodig hebt voor een
  feit. Anders laat je ze weg en noem je dat in aannames.
- Artikel 9 en 17 verwijzen naar de WHW. Lees die niet. Noem in aannames
  welke begrippen daardoor zonder definitie uit de wet blijven, zoals
  instellingsplan.
- Het script kent nog geen subtypen. Lokale bibliotheek, provinciale
  ondersteuningsinstelling en Koninklijke Bibliotheek zijn soorten openbare
  bibliotheekvoorziening (artikel 2). Kies zelf hoe je dat vastlegt en leg de
  keuze uit in aannames.
- Gebruik dezelfde namen als in
  demo/bibliotheek/01-begrippen/lidmaatschap-begrippen.md waar een begrip
  hetzelfde is.

Classificeer elk begrip met een soortbegrip (R9) en geef bij elk begrip en
feittype een bron of gebaseerd_op. Houd het model op hooguit 8 objecttypen.
```

## Wat je daarna laat zien

De agent werkt ongeveer een tot twee minuten. Daarna:

| Laat zien | Waar | Waar je op let |
|---|---|---|
| De YAML die de agent schreef | `demo/bibliotheek/02-conceptueel/koninklijke-bibliotheek.orm.yaml` | Kort en leesbaar: dit is het enige wat de AI schrijft |
| Het model in Factum | `koninklijke-bibliotheek.orm.json` | Hoe de gegevenslevering als feittype is gemodelleerd |
| De Note van een begrip in Factum | Properties, veld Note | Definitie, soortbegrip en de letterlijke wettekst waar het begrip op rust |
| De begrippenlijst | `demo/bibliotheek/01-begrippen/koninklijke-bibliotheek-begrippen.md` | Welke begrippen naar de WHW verwijzen en dus geen definitie uit deze wet hebben |
| Het model in zinnen | `demo/bibliotheek/02-conceptueel/koninklijke-bibliotheek.md` | De regel over niet herleidbare gegevens, met voorbeeldgegevens |

## Om te bespreken

- **Gegevens over gegevens.** Artikel 11 gaat over gegevenslevering. Modelleert de agent de levering zelf als feit, of de gegevens die geleverd worden? Wat is nodig?
- **Verwijzing naar een andere wet.** De Koninklijke Bibliotheek en het instellingsplan zijn in de WHW gedefinieerd. Wat doet de agent met een begrip waarvan de definitie buiten de bron ligt?
- **Twee rollen van de Koninklijke Bibliotheek.** Ze is deelnemer aan het netwerk, ontvanger van gegevens en beheerder van de landelijke digitale bibliotheek. Blijft dat één begrip?
- **Wet en gegevens.** Artikel 11 lid 3 en 4 laten de Koninklijke Bibliotheek en de minister zelf bepalen welke gegevens het zijn. Wat betekent dat voor hoe ver je het model kunt uitwerken?

## Als het misgaat

- **De agent staat niet in `/agents`.** Herstart Claude Code, of vraag: "Lees .claude/agents/orm-modelleur.md en volg die instructies" met daarachter de prompt.
- **Het script geeft een FOUT.** De agent lost die meestal zelf op. Gebeurt dat niet, laat de melding dan zien: het is een goed voorbeeld van hoe het script de AI controleert.
