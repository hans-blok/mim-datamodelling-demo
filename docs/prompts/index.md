---
titel: Prompts per thema
doel: Overzicht van de prompts waarmee de agent orm-modelleur per thema een deelmodel van de Wsob maakt.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Prompts per thema

Het voorbeeld bibliotheek deelt de Wet stelsel openbare bibliotheekvoorzieningen (Wsob) op in thema's. Per thema maakt de agent `orm-modelleur` in één run een deelmodel. Elke prompt hieronder is zo'n run, met afbakening, wat je daarna laat zien en wat je met een deskundige bespreekt.

| Thema | Artikelen | Prompt |
|---|---|---|
| Stelsel en netwerk | 1, 2, 6, 7, 8 | [stelsel-en-netwerk](stelsel-en-netwerk.md) |
| Functies en publieke waarden | 4, 5 | [functies-en-publieke-waarden](functies-en-publieke-waarden.md) |
| Lidmaatschap en contributie | 12, 13, 14 | al gemaakt, zie het model `lidmaatschap` |
| Collectie en leenverkeer | 10, 15, 16, 18 | [collectie-en-leenverkeer](collectie-en-leenverkeer.md) |
| Koninklijke Bibliotheek en landelijke digitale bibliotheek | 9, 11, 17 | [koninklijke-bibliotheek](koninklijke-bibliotheek.md) |
| Bekostiging en subsidie | 19 tot en met 23 | [bekostiging-en-subsidie](bekostiging-en-subsidie.md) |

## Volgorde

Begin bij stelsel en netwerk. Dat model legt de soorten openbare bibliotheekvoorziening vast waar de andere thema's naar verwijzen. Daarna kun je de thema's in elke volgorde doen.

Elke prompt vraagt de agent dezelfde namen te gebruiken als in de begrippenlijst van lidmaatschap. Is stelsel en netwerk al gemaakt, voeg dan ook die begrippenlijst toe aan de prompt: `demo/bibliotheek/01-begrippen/stelsel-en-netwerk-begrippen.md`.

## Wat elke prompt vastlegt

- **Voorbeeld, bron en naam**, zodat de agent weet waar hij leest en schrijft.
- **De artikelen**, en dat hij geen andere artikelen leest.
- **De afbakening**: welke gegevens het model moet opleveren en wat hij weglaat.
- **De omvang**: een maximum aantal objecttypen, zodat het model klein blijft.
