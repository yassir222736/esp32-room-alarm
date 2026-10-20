# Bedrading

> **Altijd eerst de USB-kabel uittrekken** voor je draden plaatst of verplaatst.
> De stap-voor-stap-versie met tekeningen staat in **[Bouwgids-Kameralarm.pdf](Bouwgids-Kameralarm.pdf)**.

## Opstelling

Het 30-pins ESP32-bord (DOIT DevKit V1-stijl, CP2102) is zo breed dat er op een breadboard van 400 punten
maar aan **één kant** een vrij gaatje overblijft. Daarom:

- **Breadboard 1** draagt alleen de ESP32: USB-C naar boven, linkerpinnen in kolom **a**, rechterpinnen in kolom **i** (rij 2–16).
- **Kolom j** naast de rechterrij blijft vrij: elke draad naar de ESP32 vertrekt daar.
- Alle pinnen die we gebruiken zitten in de **rechterrij** (VIN … EN).
- **Breadboard 2** bevat alle onderdelen en krijgt 5V/GND via de rails.

## ESP32-pinnen

| Gaatje bb1 | Pin | GPIO | Gaat naar (bb2) | Onderdeel |
|---|---|---|---|---|
| j2  | VIN | – | linker rode rail (+) | 5V-voeding |
| j3  | GND | – | linker blauwe rail (−) | massa |
| j4  | D13 | 13 | b17 | RGB-led rood (via 220 Ω) |
| j5  | D12 | 12 | g7 | zoemer (via 1 kΩ + PN2222) |
| j6  | D14 | 14 | b19 | RGB-led groen (via 220 Ω) |
| j7  | D27 | 27 | b6 | HC-SR04 **Echo** (via spanningsdeler) |
| j8  | D26 | 26 | b2 | HC-SR04 Trig |
| j9  | D25 | 25 | b22 | rode led (via 220 Ω) |
| j10 | D33 | 33 | b25 | blauwe led (via 220 Ω) |
| j11 | D32 | 32 | b20 | RGB-led blauw (via 220 Ω) |
| j12 | D35 | 35 | b16 | IR-ontvanger signaal (via 1 kΩ) |
| j13 | D34 | 34 | b9  | PIR-uitgang |

Breadboard 2: verbind onderaan de linker en rechter rails (+ met +, − met −).

## Per onderdeel (breadboard 2)

### Ultrasone sensor HC-SR04 (rij 1–6)
| Sensor | Gaatje | Verder |
|---|---|---|
| VCC  | a1 | b1 → rode rail (+) |
| Trig | a2 | b2 → D26 |
| Echo | a3 | 1 kΩ van c3 naar c6 |
| GND  | a4 | b4 → blauwe rail (−) |
| – | a6 | 2 kΩ van a6 naar blauwe rail (−); b6 → D27 |

**Spanningsdeler:** Echo geeft 5 V; via 1 kΩ / 2 kΩ wordt dat 3,3 V. Nooit overslaan.

```
Echo ──[ 1 kΩ ]──┬──── D27
                 │
              [ 2 kΩ ]
                 │
                GND
```

### Bewegingssensor HC-SR501 (rij 8–10)
| PIR | Gaatje | Verder |
|---|---|---|
| VCC | a8  | b8 → rode rail (+) |
| OUT | a9  | b9 → D34 |
| GND | a10 | b10 → blauwe rail (−) |

Potmeter *Time* helemaal tegen de klok in (kortst), *Sensitivity* in het midden. ±60 s opwarmen na het inschakelen.

### IR-ontvanger (rij 12–16)
| Module (ELEGOO: Y/R/G) | Gaatje | Verder |
|---|---|---|
| Y / S (signaal) | a12 | 1 kΩ van c12 naar c16; b16 → D35 |
| R / + | a13 | b13 → rode rail (+) |
| G / − | a14 | b14 → blauwe rail (−) |

**Geen** pulldown naar GND: de uitgang van de ontvanger is te zwak voor een spanningsdeler. De 1 kΩ in serie
beperkt de stroom naar D35 tot enkele tientallen µA.

### Zoemer met transistor (rij 3–13, rechterhelft)
| Wat | Waar |
|---|---|
| PN2222 (platte kant naar kolom j) | g3 (C), g4 (B), g5 (E) |
| 1 kΩ | f4 → f7 |
| draad | g7 → D12 |
| draad | j5 → blauwe rail (−) |
| draad | h3 → g10 |
| actieve zoemer | − in j10, + (lange poot) in j13 |
| draad | g13 → rode rail (+) |

### RGB-led (rij 17–20) – gemeenschappelijke kathode
| Poot | Gaatje | Verder |
|---|---|---|
| R   | h17 | 220 Ω e17–f17; b17 → D13 |
| GND (langste) | h18 | j18 → blauwe rail (−) |
| G   | h19 | 220 Ω e19–f19; b19 → D14 |
| B   | h20 | 220 Ω e20–f20; b20 → D32 |

### Rode en blauwe led (rij 22–26)
| Led | Lange poot (+) | Korte poot (−) | Weerstand | Naar ESP32 |
|---|---|---|---|---|
| Rood  | h22 | h23 → j23 → (−) | 220 Ω e22–f22 | b22 → D25 |
| Blauw | h25 | h26 → j26 → (−) | 220 Ω e25–f25 | b25 → D33 |

## Ander bord?
De pinnummers staan centraal in [`include/config.h`](../include/config.h). Vermijd GPIO 6–11 (flash),
gebruik GPIO 34–39 alleen als ingang, en let op opstart-pinnen (0, 2, 12, 15).
