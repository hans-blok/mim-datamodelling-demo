---
titel: Bibliotheek
doel: Uitleg van het demovoorbeeld over de openbare bibliotheek, gebaseerd op de Wet stelsel openbare bibliotheekvoorzieningen.
auteur: Hans Blok
datum: 2026-11-19
wijziging: Eerste versie.
---

# Bibliotheek

Dit voorbeeld modelleert het lidmaatschap van de openbare bibliotheek: wie lid kan worden, van welke voorziening en wanneer er geen contributie is. De regels komen uit de Wet stelsel openbare bibliotheekvoorzieningen (Wsob). Het voorbeeld laat ook zien hoe AI een ORM-model maakt uit een wettekst, en wat een deskundige daarna nog moet controleren.

Het model is een voorstel van AI en nog niet gecontroleerd door een deskundige.

## Indeling naar MIM

| Map | Niveau | Inhoud | In scope van MIM? |
|---|---|---|---|
| [bronnen](bronnen/README.md) | | De Wsob, per artikel opgedeeld | Nee |
| [01-begrippen](01-begrippen/lidmaatschap-begrippen.md) | 1, model van begrippen | Begrippen met definitie en bron | Nee |
| [02-conceptueel](02-conceptueel/lidmaatschap.md) | 2, conceptueel informatiemodel | ORM-model lidmaatschap, in zinnen en voor Factum | Ja |

Niveau 3 en 4 zijn voor dit voorbeeld nog niet uitgewerkt.

## ORM en MIM

| ORM | MIM |
|---|---|
| Entiteittype, zoals Lidmaatschap | Objecttype |
| Waardetype, zoals Geboortedatum | Attribuutsoort met een datatype |
| Waardetype met vaste waarden, zoals Soort voorziening | Enumeratie |
| Feittype tussen twee entiteittypen | Relatiesoort |
| Feittype tussen entiteittype en waardetype | Attribuutsoort van het objecttype |
| Uniciteits- en verplichtheidsregel | Kardinaliteit |
| Overige regels | Constraint |

## Werken aan het model

Pas [lidmaatschap.orm.yaml](02-conceptueel/lidmaatschap.orm.yaml) aan en draai `python scripts/orm_naar_factum.py demo/bibliotheek/02-conceptueel/lidmaatschap.orm.yaml`. Zie [scripts/README.md](../../scripts/README.md).
