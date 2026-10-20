# Bouwen en testen

Test **elk onderdeel apart** voordat je het volgende aansluit. Zo vind je een fout of een defect onderdeel meteen.

## Voorbereiding
1. Installeer **PlatformIO** (VS Code-extensie of `pip install platformio`).
2. Kopieer `include/secrets.example.h` naar `include/secrets.h` en vul in:
   - `WIFI_SSID` / `WIFI_PASSWORD` – alleen **2,4 GHz** werkt met de ESP32 (de meeste routers zenden beide banden uit onder dezelfde naam);
   - `WEB_PIN` – kies een eigen pincode;
   - `NTFY_TOPIC` – een **lange, willekeurige** naam, bv. `kameralarm-` + 12 willekeurige tekens. Wie de naam kent, ziet je meldingen.
3. Installeer de **ntfy**-app op je gsm en abonneer je op je topic (server `ntfy.sh`).
   *Android:* in de ntfy-app kun je per topic een eigen meldingsgeluid kiezen, bv. je alarm-mp3.
4. Driver: borden met een **CP2102**-chip hebben de *CP210x Universal Windows Driver* van Silicon Labs nodig, borden met een **CH340** de CH340-driver.

## Uploaden
```
pio run -t upload        # firmware
pio run -t uploadfs      # webpagina (LET OP: wist ook logboek, instellingen en mp3)
pio device monitor       # seriële monitor, 115200 baud
```
In de seriële monitor zie je `=== Kameralarm start ===` en het IP-adres.

## Testcommando's
Typ in de seriële monitor (het alarm moet uit staan; **Enter** stopt een test):

| Onderdeel | Commando | Wat je moet zien |
|---|---|---|
| Rode + blauwe led | `t leds` | om en om knipperen |
| RGB-led | `t rgb` | rood → groen → blauw → kleurenwiel |
| Zoemer | `t buzzer` | 3 piepjes |
| Ultrasone sensor | `t sonar` | afstand in cm, klopt met een meetlat |
| Bewegingssensor | `t pir` | na ±60 s: "BEWEGING" bij zwaaien, "rust" bij stilzitten |
| IR-ontvanger | `t ir` | elke knop van de afstandsbediening toont een code |
| IR-diagnose | `t irpin` | niveau van D35 per seconde + aantal signaalwisselingen |
| Alles samen | `t alarm` | 5 s politielichten, kleurenwiel en zoemer |

Verder: `status`, `arm`, `disarm`, `cal` (basisafstand opnieuw meten) en `help`.

## Webpagina
- Open `http://kameralarm.local` of het IP-adres (gsm op hetzelfde wifi-netwerk).
- Tik één keer op **🔊 Geluid inschakelen** – browsers spelen pas geluid na een tik.
- Upload je mp3 (max. ±1,5 MB) bij **Alarmgeluid**.
- **Extra → Testmelding**: je gsm moet een ntfy-melding krijgen.
- Het logboek vraagt de pincode.

## De echte test
1. Tik op **Inschakelen** (of POWER op de afstandsbediening).
2. Verlaat binnen **30 s** het bereik van de sensoren – de blauwe led knippert.
3. Wacht tot de RGB-led zacht groen "ademt": het alarm bewaakt.
4. Loop voor de sensoren langs:
   - **vooralarm** (10 s): rood/blauw knippert rustig, piepje per seconde – nog uit te schakelen;
   - daarna **ALARM**: politielichten, kleurenwiel, zoemer, sirene/mp3 op de webpagina en een ntfy-melding.
5. Schakel uit en bekijk het logboek.

Een geslaagde test ziet er in het logboek zo uit:

```
22:38:47  ingeschakeld   via webpagina
22:39:31  binnenkomst    afstand 85 cm (basis 144 cm), PIR bevestigd
22:39:41  alarm
22:39:54  uitgeschakeld  via webpagina
```

## Problemen oplossen
| Probleem | Oplossing |
|---|---|
| Geen COM-poort | Driver installeren (CP210x of CH340); probeer een andere USB-kabel (sommige kabels laden alleen). |
| Geen wifi | Controleer of je router 2,4 GHz uitzendt. Lukt het niet, dan start de ESP32 een eigen netwerk `Kameralarm`. |
| Afstand altijd "geen echo" | Controleer Trig/Echo, de spanningsdeler en of er iets vasts binnen 4 m staat. |
| PIR geeft vaak beweging | Laat hem 60 s opwarmen; draai *Sensitivity* lager; richt hem weg van ramen en verwarming. |
| `t ir` toont niets | Kijk met je gsm-camera of de afstandsbediening paars licht geeft. Toont `t irpin` 0 wisselingen en knippert lampje "L" op de module niet, dan is de ontvanger waarschijnlijk defect. |
| RGB-led blijft uit | Gemeenschappelijke anode: lange poot naar 3V3 en `RGB_COMMON_ANODE = true` in `include/config.h`. |
