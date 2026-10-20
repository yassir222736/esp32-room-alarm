# Plaatsing

Het alarm werkt als een **onzichtbare struikeldraad** in de ingang van een kamer, met een bewegingssensor als tweede controle.

```
 gang   ┃ deur ┃
────────┛      ┗──────────────── muur
  muur/kast   ╲ (deur draait open)      [meubel]
  aan de       ╲                        ★ apparaat
  overkant      ←──── ultrasone straal ────┘
                       (kamer)
```

## Waar
- **Apparaat:** op een meubel of plank **naast de deur**, aan de binnenkant van de kamer, op **heuphoogte (±75–100 cm)**.
  Zo raakt de straal een volwassene, maar geen kleine huisdieren.
- **Ultrasone sensor:** **horizontaal**, **evenwijdig aan de deurmuur**, dwars door de ingang naar iets **vasts** aan de overkant
  (muur, kast). De straal loopt ±30–50 cm vóór de muur.
  Draait de deur naar binnen open, dan onderbreekt de deur zelf de straal al voor iemand binnen is.
- **Bewegingssensor (PIR):** naast de ultrasone sensor, **schuin naar de deur**.
- **Leds:** naar de kamer gericht, zodat je de status ziet.
- **Vrije straal:** zet niets in de straal (flesjes, doosjes…). De ultrasone sensor kijkt in een kegel van ±15°.

## Stroom
Gebruik een **gsm-lader** (5 V, ≥1 A) met een USB-C-kabel. Een pc-poort valt uit als de pc slaapt.

## Afstellen
- Bij elk inschakelen meet het alarm automatisch de **basisafstand** (mediaan van 30 metingen).
- Een **doorbraak** = de afstand wijkt meer dan **20 cm** af (of de echo verdwijnt), **2 metingen op rij** (0,1 s).
- Met PIR-bevestiging aan moet de PIR binnen **10 s** ook beweging zien; anders volgt alleen een logregel
  "tripwire zonder PIR" en een nieuwe kalibratie.
- Alles is aan te passen op de webpagina onder **Instellingen**. Op de webpagina zie je de afstand live: controleer na
  het plaatsen of de basisafstand logisch is (bv. 80–150 cm).

## Testen zonder vals alarm
Laat het alarm een uur bewaken terwijl niemand in de kamer is en kijk in het logboek. Zie je regels
"tripwire zonder PIR", verhoog dan de drempel of richt de sensor op een vlakker, groter oppervlak.
