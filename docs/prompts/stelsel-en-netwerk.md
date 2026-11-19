---
titel: "Prompt: ORM-model stelsel en netwerk"
doel: Prompt voor de demo waarin de agent orm-modelleur een ORM-model maakt van artikel 1, 2, 6, 7 en 8 van de Wsob.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Prompt: ORM-model stelsel en netwerk

In deze demo maakt de agent `orm-modelleur` een ORM-model van het stelsel van openbare bibliotheekvoorzieningen: welke voorzieningen er zijn, wie er verantwoordelijk voor is en wie deelneemt aan het netwerk. De bron is de Wet stelsel openbare bibliotheekvoorzieningen (Wsob), artikel 1, 2, 6, 7 en 8.

Dit model is de basis voor de andere thema's. Het legt de begrippen vast waar de rest naar verwijst, zoals lokale bibliotheek, provinciale ondersteuningsinstelling en Koninklijke Bibliotheek.

## Voorbereiding

1. Open de repository in Visual Studio Code en start Claude Code.
2. Controleer dat de agent er is: typ `/agents` en kijk of `orm-modelleur` in de lijst staat.
3. Controleer dat de scripts werken:

    ```
    pip install -r scripts/requirements.txt
    python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml
    ```

4. Open `demo/bibliotheek/bronnen/wsob/chunks/h02-art07-netwerk-en-deelnemers.md` en `h01-art01-begripsbepalingen.md` in een tabblad. Dan kun je de wettekst naast het resultaat laten zien.

## De prompt

Plak deze tekst in Claude Code:

```text
Gebruik de orm-modelleur.

Voorbeeld: bibliotheek. Bron: wsob. Naam: stelsel-en-netwerk.

Onderwerp: het stelsel van openbare bibliotheekvoorzieningen en het netwerk
dat ze samen vormen. Gebruik artikel 1, 2, 6, 7 en 8. Lees geen andere
artikelen.

Afbakening:
- Modelleer welke gegevens je nodig hebt om te weten welke openbare
  bibliotheekvoorzieningen er zijn, van welke soort ze zijn, welke overheid
  een voorziening subsidieert of in stand houdt en wie deelneemt aan het
  netwerk.
- Artikel 1 lid 1 onder c zegt dat een lokale bibliotheek een rechtspersoon
  is met een of meer vestigingen. Neem de vestiging alleen op als je hem nodig
  hebt voor een feit uit deze artikelen.
- De verplichtingen van een deelnemer in artikel 8 (gezamenlijke catalogus,
  leenverkeer, collectieplan, digitale infrastructuur, ledenadministratie,
  onderwijs) zijn geen gegevens. Zet ze bij regels als ze iets zeggen over
  wie deelnemer is. Laat de rest weg en noem dat in aannames.
- Laat artikel 6 lid 5 en 6 weg: die gaan over de procedure voor een
  algemene maatregel van bestuur.
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
| De YAML die de agent schreef | `demo/bibliotheek/02-conceptueel/stelsel-en-netwerk.orm.yaml` | Kort en leesbaar: dit is het enige wat de AI schrijft |
| Het model in Factum | `stelsel-en-netwerk.orm.json` | Feittypen, uniciteit en verplichtheid in het diagram |
| De Note van een begrip in Factum | Properties, veld Note | Definitie, soortbegrip en de letterlijke wettekst waar het begrip op rust |
| De begrippenlijst | `demo/bibliotheek/01-begrippen/stelsel-en-netwerk-begrippen.md` | Soortbegrip en herkomst per begrip: letterlijk uit de wet of een voorstel van AI |
| Het model in zinnen | `demo/bibliotheek/02-conceptueel/stelsel-en-netwerk.md` | Regels in gewone taal met voorbeeldgegevens, om met een deskundige te bespreken |

## Om te bespreken

- **Definities uit de wet.** Artikel 1 definieert lokale bibliotheek, provinciale ondersteuningsinstelling en landelijke digitale bibliotheek. Heeft de agent die letterlijk overgenomen, met `bron`?
- **Voorziening of organisatie?** Een lokale bibliotheek is volgens artikel 1 een organisatie die voorzieningen verzorgt. Artikel 2 noemt diezelfde lokale bibliotheek een openbare bibliotheekvoorziening. Hoe gaat de agent met dat verschil om?
- **Overeenkomst met lidmaatschap.** Het lidmaatschapsmodel kent het begrip Voorziening. Sluit dit model daarop aan, of ontstaan er twee namen voor hetzelfde?
- **Subtypen.** Hoe heeft de agent het verschil tussen de drie soorten voorzieningen opgelost zonder subtypen? Is dat goed genoeg?
- **Wet en gegevens.** Artikel 6 en 8 gaan over verantwoordelijkheden en plichten. Welke daarvan leveren gegevens op, en welke niet?

## Als het misgaat

- **De agent staat niet in `/agents`.** Herstart Claude Code, of vraag: "Lees .claude/agents/orm-modelleur.md en volg die instructies" met daarachter de prompt.
- **Het script geeft een FOUT.** De agent lost die meestal zelf op. Gebeurt dat niet, laat de melding dan zien: het is een goed voorbeeld van hoe het script de AI controleert.
