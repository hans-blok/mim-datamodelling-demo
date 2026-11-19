---
titel: "Prompt: ORM-model collectie en leenverkeer"
doel: Prompt voor de demo waarin de agent orm-modelleur een ORM-model maakt van artikel 10, 15, 16 en 18 van de Wsob.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Prompt: ORM-model collectie en leenverkeer

In deze demo maakt de agent `orm-modelleur` een ORM-model van het collectieplan, het interbibliothecaire leenverkeer en de inkoop van digitale werken. De bron is de Wet stelsel openbare bibliotheekvoorzieningen (Wsob), artikel 10, 15, 16 en 18.

## Voorbereiding

1. Open de repository in Visual Studio Code en start Claude Code.
2. Controleer dat de agent er is: typ `/agents` en kijk of `orm-modelleur` in de lijst staat.
3. Controleer dat de scripts werken:

    ```
    pip install -r scripts/requirements.txt
    python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml
    ```

4. Open `demo/bibliotheek/bronnen/wsob/chunks/h03-art15-interbibliothecair-leenverkeer.md` in een tabblad. Dan kun je de wettekst naast het resultaat laten zien.

## De prompt

Plak deze tekst in Claude Code:

```text
Gebruik de orm-modelleur.

Voorbeeld: bibliotheek. Bron: wsob. Naam: collectie-en-leenverkeer.

Onderwerp: het gezamenlijk collectieplan, het interbibliothecaire leenverkeer
en de inkoop van digitale werken. Gebruik artikel 10, 15, 16 en 18, en
artikel 1 voor de begripsbepalingen. Lees geen andere artikelen.

Afbakening:
- Modelleer welke gegevens je nodig hebt om te weten welk collectieplan geldt,
  wie deelneemt aan het leenverkeer, welk verzoek om een fysiek werk is gedaan
  en welke digitale werken zijn ingekocht op welke voordracht.
- Laat taken en bevoegdheden weg die geen gegevens opleveren, zoals "de
  Koninklijke Bibliotheek stelt vast in overeenstemming met ...". Zet ze bij
  regels als ze een regel over de gegevens zijn.
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
| De YAML die de agent schreef | `demo/bibliotheek/02-conceptueel/collectie-en-leenverkeer.orm.yaml` | Kort en leesbaar: dit is het enige wat de AI schrijft |
| Het model in Factum | `collectie-en-leenverkeer.orm.json` | Feittypen, uniciteit en verplichtheid in het diagram |
| De Note van een begrip in Factum | Properties, veld Note | Definitie, soortbegrip en de letterlijke wettekst waar het begrip op rust |
| De begrippenlijst | `demo/bibliotheek/01-begrippen/collectie-en-leenverkeer-begrippen.md` | Soortbegrip en herkomst per begrip: letterlijk uit de wet of een voorstel van AI |
| Het model in zinnen | `demo/bibliotheek/02-conceptueel/collectie-en-leenverkeer.md` | Regels in gewone taal met voorbeeldgegevens, om met een deskundige te bespreken |

## Om te bespreken

- **Welke definities komen uit de wet?** Artikel 1 definieert "werk" en "lokale bibliotheek". Heeft de agent die letterlijk overgenomen, met `bron`?
- **Classificatie.** Valt elk begrip onder een goed soortbegrip? Klopt de definitie als je hem in de wettekst zet in plaats van de term (substitutietoets)?
- **Subtypen.** Hoe heeft de agent het verschil tussen lokale bibliotheek, provinciale ondersteuningsinstelling en Koninklijke Bibliotheek opgelost zonder subtypen? Is dat goed genoeg?
- **Wet en gegevens.** De wet zegt vooral wie wat moet doen. Welke van die regels gaan echt over gegevens, en welke niet?
- **Aannames.** Wat heeft de agent zelf moeten kiezen omdat de wet het niet zegt?

## Als het misgaat

- **De agent staat niet in `/agents`.** Herstart Claude Code, of vraag: "Lees .claude/agents/orm-modelleur.md en volg die instructies" met daarachter de prompt.
- **Het script geeft een FOUT.** De agent lost die meestal zelf op. Gebeurt dat niet, laat de melding dan zien: het is een goed voorbeeld van hoe het script de AI controleert.
