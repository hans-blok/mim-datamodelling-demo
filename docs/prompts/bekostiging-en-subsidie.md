---
titel: "Prompt: ORM-model bekostiging en subsidie"
doel: Prompt voor de demo waarin de agent orm-modelleur een ORM-model maakt van artikel 19 tot en met 23 van de Wsob.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Prompt: ORM-model bekostiging en subsidie

In deze demo maakt de agent `orm-modelleur` een ORM-model van de bekostiging van de Koninklijke Bibliotheek, de subsidies die zij en de minister verstrekken, en het toezicht daarop. De bron is de Wet stelsel openbare bibliotheekvoorzieningen (Wsob), artikel 19 tot en met 23.

Dit thema is het meest procedureel. Het laat zien hoe je uit regels over besluiten, reglementen en goedkeuring de gegevens haalt die je moet vastleggen.

## Voorbereiding

1. Open de repository in Visual Studio Code en start Claude Code.
2. Controleer dat de agent er is: typ `/agents` en kijk of `orm-modelleur` in de lijst staat.
3. Controleer dat de scripts werken:

    ```
    pip install -r scripts/requirements.txt
    python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml
    ```

4. Open `demo/bibliotheek/bronnen/wsob/chunks/h05-art20-subsidieverstrekking-koninklijke-bibliotheek.md` in een tabblad. Dan kun je de wettekst naast het resultaat laten zien.

## De prompt

Plak deze tekst in Claude Code:

```text
Gebruik de orm-modelleur.

Voorbeeld: bibliotheek. Bron: wsob. Naam: bekostiging-en-subsidie.

Onderwerp: de bekostiging van de Koninklijke Bibliotheek, de verstrekking van
subsidie door de Koninklijke Bibliotheek en door de minister, en het toezicht
op ministeriële subsidies. Gebruik artikel 19 tot en met 23, en artikel 1
voor de begripsbepalingen. Lees geen andere artikelen.

Afbakening:
- Modelleer welke gegevens je nodig hebt om te weten wie welke subsidie heeft
  verstrekt aan welke subsidieontvanger, onder welk reglement, of dat
  reglement is goedgekeurd door de minister, en wie als toezichthouder is
  aangewezen.
- Artikel 20 lid 4 zegt dat een reglement pas in werking treedt na
  goedkeuring. Leg dat vast als regel.
- Artikel 19 gaat vooral over verantwoording in plannen en verslagen volgens
  de WHW. Lees de WHW niet. Neem van artikel 19 alleen op wat je nodig hebt
  voor een feit, en noem de rest in aannames.
- Artikel 22 gaat over intellectuele eigendomsrechten. Neem het alleen op als
  het een feit oplevert dat je kunt vastleggen. Anders laat je het weg en zeg
  je waarom.
- Laat bevoegdheden uit de Algemene wet bestuursrecht (artikel 23 lid 2) en
  de bekendmaking in de Staatscourant (artikel 23 lid 3) weg.
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
| De YAML die de agent schreef | `demo/bibliotheek/02-conceptueel/bekostiging-en-subsidie.orm.yaml` | Kort en leesbaar: dit is het enige wat de AI schrijft |
| Het model in Factum | `bekostiging-en-subsidie.orm.json` | Feittypen, uniciteit en verplichtheid in het diagram |
| De Note van een begrip in Factum | Properties, veld Note | Definitie, soortbegrip en de letterlijke wettekst waar het begrip op rust |
| De begrippenlijst | `demo/bibliotheek/01-begrippen/bekostiging-en-subsidie-begrippen.md` | Welke begrippen de wet niet definieert, zoals subsidie en subsidieontvanger |
| Het model in zinnen | `demo/bibliotheek/02-conceptueel/bekostiging-en-subsidie.md` | De regel over goedkeuring van het reglement, met voorbeeldgegevens |

## Om te bespreken

- **Twee verstrekkers.** De Koninklijke Bibliotheek en de minister verstrekken allebei subsidie, maar onder andere regels. Is het één feittype met een verstrekker, of twee aparte?
- **Begrippen zonder definitie.** Subsidie, subsidieontvanger en reglement worden in de Wsob niet gedefinieerd. Wat heeft de agent voorgesteld, en is dat duidelijk een voorstel?
- **Toestand of gebeurtenis.** Goedkeuring is een besluit op een moment. Legt de agent een datum vast, of alleen of het reglement is goedgekeurd? Wat heb je nodig?
- **Wet en gegevens.** Veel van deze artikelen regelen bevoegdheden. Welke regels gaan echt over gegevens?

## Als het misgaat

- **De agent staat niet in `/agents`.** Herstart Claude Code, of vraag: "Lees .claude/agents/orm-modelleur.md en volg die instructies" met daarachter de prompt.
- **Het script geeft een FOUT.** De agent lost die meestal zelf op. Gebeurt dat niet, laat de melding dan zien: het is een goed voorbeeld van hoe het script de AI controleert.
