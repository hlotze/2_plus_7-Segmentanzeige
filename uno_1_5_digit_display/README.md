# UNO-Projekt: Binäranzeige 0–15

Der Arduino liest J1–J4 (D10–D13, Werte 8/4/2/1) beziehungsweise den
Codierschalter SW1 und zeigt den Wert als Dezimalzahl 0–15 an.
Ab 10 wird die Zehneranzeige zugeschaltet. L1–L4 zeigen denselben Wert binär.
Solange Eingangswert und Anzeigemodus unverändert bleiben, bleibt auch die
Anzeige unverändert. Der Sketch schreibt die Ausgänge nur bei einer Änderung.

Beim Start oder Reset initialisiert der Sketch die Anzeige mit 0 und schaltet
alle Status-LEDs aus. Anschließend übernimmt er sofort den tatsächlich
anliegenden Eingangswert. Bei offenen Eingängen beziehungsweise SW1 auf 0
bleibt die Anzeige 0. A4 wählt den Anzeigemodus; A5 bleibt frei.

## Umschaltung Dezimal / Hexadezimal

**Ohne Drahtbrücke ist die Dezimalanzeige 0–15 aktiv (Default).**
Eine **Drahtbrücke zwischen Arduino-GND und A4** schaltet die Anzeige auf
**0–F (hexadezimal)** um; die Zehneranzeige bleibt dabei aus.
Die Drahtbrücke entfernen, um wieder auf 0–15 umzuschalten.

A4 wird als digitaler Eingang mit `INPUT_PULLUP` verwendet. Einen Schalter
oder Jumper zwischen **A4 und GND** anschließen; kein zusätzlicher Widerstand nötig.

| A4 | Anzeige |
| --- | --- |
| Offen (HIGH) | Dezimal 0–15, Zehner ab 10 eingeschaltet |
| Mit GND verbunden (LOW) | Hexadezimal 0–9, A, b, C, d, E, F; Zehner immer aus |

Die Anzeige aktualisiert sich auch bei einem Moduswechsel ohne Änderung
des Eingangswerts. L1–L4 zeigen in beiden Modi weiterhin den Binärwert.
Der Moduseingang wird ohne zeitliche Entprellung gelesen.

Die Erweiterung wurde am 12.10.2026 für alle 16 Werte in beiden Modi mit
simulierten Ein-/Ausgängen geprüft, einschließlich reiner Moduswechsel und
unveränderter Eingänge. UNO-Build und Upload mit Flash-Verifikation waren
erfolgreich: 1.388 Byte Flash, 43 Byte RAM. Ein Funktionstest am Aufbau steht aus.

Dieses neue Projekt löst die Zehner-Erkennung nicht mehr mit den bisherigen ICs, sondern komplett im Arduino/UNO.

## Ziel

- 4 digitale Eingangspins lesen eine 4-Bit-Binärzahl (0–15) ein
- UNO berechnet die passende Anzeige
- Anzeige wird per Segment-Ausgaben auf die 1½-stellige 7-Segmentanzeige geschrieben
- Zehner-Erkennung erfolgt in Software statt über Decade-ICs

## Hardware-Konzept

- Binäreingänge: 4 digitale Pins, D10..D13
- Segment-Ausgänge: a, b, c, d, e, f, g auf eigene Arduino-Ausgänge
- Beide gemeinsamen Anoden direkt an +5 V; Kathoden über ULN2803A
- Serienwiderstände: 220 Ω pro Segment

## Pin-Belegung

### Binäreingänge

- D10 = J1, Wert 8 (Bit 3)
- D11 = J2, Wert 4 (Bit 2)
- D12 = J3, Wert 2 (Bit 1)
- D13 = J4, Wert 1 (Bit 0)

### ULN-Ausgänge und Eingangs-LEDs

- D2–D9 steuern U1-Eingänge 1–8 in dieser Reihenfolge.
- Einer a/b/c/d/e/f/g: D2/D7/D3/D4/D5/D8/D6.
- D9 steuert die Zehner-Kathode über ULN-Kanal 8 und R1.
- A0–A3 steuern L1–L4 (Werte 8/4/2/1).

> Display-Pins 1 und 2 direkt an den 5-V-Versorgungspin anschließen. Die Arduino-Ausgänge zum ULN2803A sind aktiv HIGH; der ULN zieht die Segmentkathoden nach GND.

## Software-Logik

1. 4-Bit-Binärwert (0–15) an D10–D13 auslesen.
2. Anzeigemodus an A4 auslesen: offen (HIGH) = Dezimal (Default),
   Drahtbrücke GND–A4 (LOW) = Hexadezimal.
3. Im Dezimalmodus zeigt die Eineranzeige den Wert modulo 10.
   Die Zehneranzeige bleibt bei 0–9 aus und zeigt bei 10–15 eine 1.
4. Im Hexadezimalmodus zeigt die Eineranzeige direkt 0–9 bzw. A, b, C, d, E, F.
   Zehner-b+c bleiben unabhängig vom Wert immer aus.
5. Anzeige und Status-LEDs bei einer Änderung des Eingangswerts oder des
   Anzeigemodus aktualisieren, auch bei einem reinen Moduswechsel.
6. Statische Anzeige über acht ULN-Kanäle, ohne Multiplexing.
7. A0–A3 schalten L1–L4 in beiden Modi entsprechend den vier eingelesenen Bits.

Die Binäreingänge D10–D13 sind aktiv HIGH und verwenden `INPUT` ohne interne
Pull-ups. RN1 zieht jeden Eingang über 10 kΩ nach GND. Der Moduseingang A4
verwendet dagegen `INPUT_PULLUP` und wird ohne zeitliche Entprellung gelesen.
Anzeige und Status-LEDs werden aus demselben eingelesenen Wert aktualisiert.

## Beispiel-Display-Mapping

Die folgenden Zuordnungen gelten für die Segmente a–g der Eineranzeige.
0–9 werden in beiden Modi gleich dargestellt; im Hexadezimalmodus kommen
für die Eingangswerte 10–15 die Zeichen A, b, C, d, E und F hinzu.

- 0 = a b c d e f
- 1 = b c
- 2 = a b g e d
- 3 = a b g c d
- 4 = f g b c
- 5 = a f g c d
- 6 = a f g e c d
- 7 = a b c
- 8 = a b c d e f g
- 9 = a b c d f g
- A (10) = a b c e f g
- b (11) = c d e f g
- C (12) = a d e f
- d (13) = b c d e g
- E (14) = a d e f g
- F (15) = a e f g

Beispiel für Eingangswert 12: Dezimal zeigt die Anzeige **12** (Zehner-b+c
an, Einer = 2); mit Drahtbrücke GND–A4 zeigt sie **C** (Zehner-b+c aus).

## Wichtig

### Warum der ULN2803A verwendet wird

Die Angabe von 20 mA pro Arduino-Ausgang bedeutet nicht, dass alle Ausgänge
gleichzeitig unabhängig voneinander mit 20 mA belastet werden dürfen.
Beim ATmega328P gehören **D5–D9 zur selben Stromgruppe** (PB0–PB5 und
PD5–PD7). Diese Gruppe darf beim Ableiten von Strom nach GND insgesamt
**höchstens 100 mA** aufnehmen; weitere Pins derselben Gruppe zählen mit.
Bei direkter Ansteuerung der Common-Anode-Anzeige würden die Arduino-Pins
den Segmentstrom nach GND ableiten. Fünf Ausgänge mit je 20 mA würden
die Gruppengrenze bereits ausschöpfen.

Außerdem teilen sich die beiden Zehnersegmente b+c einen Kathodenanschluss:
Der zugehörige Ausgang müsste den Strom beider Segmente zusammen tragen.
Der ULN2803A übernimmt deshalb die Segmentströme; die Arduino-Ausgänge
liefern nur die kleinen Steuerströme für seine Eingänge. Die Vorwiderstände
R1–R8 bleiben zur Begrenzung der LED-Ströme erforderlich.

Quelle: [ATmega328P-Datenblatt, Abschnitt 28.2, S. 258–259](https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf).

Mit dem ULN2803A gilt an den Arduino-Segmentausgängen:

- Segment an = HIGH
- Segment aus = LOW

Der Sketch setzt alle acht ULN-Eingänge und vier LED-Ausgänge bereits vor `pinMode(OUTPUT)`
auf LOW. Zwischen UNO und ULN2803A sind keine externen
Eingangsvorwiderstände nötig (interne 2,7-kΩ-Widerstände).

## Projektdatei

Die Arduino-Implementierung liegt in:

- `uno_1_5_digit_display.ino`

## PlatformIO auf dem Mac

In VS Code den übergeordneten Ordner `2_plus_7-Segmentanzeige` öffnen.
Dort liegt `platformio.ini` mit der Umgebung `uno` (Arduino UNO R3,
Arduino-Framework, Atmel-AVR-Plattform 5.3.0). Der vorhandene Sketch wird
direkt aus diesem Unterordner kompiliert; eine zweite Kopie ist nicht nötig.

In der PlatformIO-Seitenleiste unter **Project Tasks → uno → General**:

- **Build** kompiliert den Sketch.
- **Upload** kompiliert und überträgt ihn auf den angeschlossenen UNO.

Alternativ im PlatformIO-Terminal im übergeordneten Projektordner:

```sh
pio run
pio run --target upload
```

Für ein normales macOS-Terminal, falls `pio` nicht im Suchpfad liegt:

```sh
~/.platformio/penv/bin/pio run
~/.platformio/penv/bin/pio run --target upload
```

Der angeschlossene UNO wurde am Port `/dev/cu.usbmodem2101` erkannt.
Falls sich der Port nach einem USB-Wechsel ändert, `upload_port` in
`platformio.ini` anpassen oder die Zeile für automatische Erkennung entfernen.
Der Sketch gibt keine Daten über die serielle Schnittstelle aus.

Am 11.10.2026 erfolgreich mit PlatformIO Core 6.2.0 kompiliert und auf
den angeschlossenen UNO übertragen; Flash-Inhalt durch avrdude verifiziert.
Speicherbedarf: 1.288 Byte Flash, 36 Byte RAM. Die tatsächliche Anzeige
und Verdrahtung sind damit noch nicht am Aufbau geprüft.


## Bestückungsentwurf

Der Plan verwendet das **Keyestudio-UNO-Protoboard** aus
`../images/Uno und Protoboard.png`. Der UNO sitzt unter der Platine;
die seitlichen POWER-, ANALOG- und DIGITAL-Leisten sind eingezeichnet.
Die Darstellung mit Koordinaten, Umrissen und Anschlusslöchern orientiert
sich an `01-probebestueckung`, verwendet aber dessen 31×26-Platine nicht.

- `protoboard_bestueckung.png` / `.jpg`: Ansicht
- `protoboard_bestueckung.svg`: skalierbare Darstellung
- `generate_protoboard_layout.py`: reproduzierbarer Generator (Pillow)

J1 besteht aus vier separaten 3-poligen Headern für die vier aktiven
HIGH-Eingänge (UNO D10–D13, RN1-Pulldowns). Es gibt keinen eigenen
GND-Pin an J1. Der Eingangsblock ist um 90° gedreht: J1.1–J1.4 liegen nebeneinander
in Spalten 8, 10, 12 und 14, mit je drei Kontakten in Reihen 3–5.
Dazwischen bleibt jeweils eine Lochspalte frei.
Die Kontakte 1–3 sind je Header miteinander verbunden und führen
dasselbe Eingangssignal. Zwischen unterschiedlichen Headern gibt es
keine Brücke. R1–R8 liegen hinter der senkrechten Anzeige an J2.
Die Segmentausgänge vom UNO D2–D8 werden über U1 (ULN2803A)
und R2–R8 geführt; die vorher
vorgesehenen separaten UNO-Verbindungsklemmen entfallen.

Das Lochbild mit 20 Spalten und 25 Reihen ist aus dem Foto abgeleitet.
Die seitlichen UNO-Leisten sind schematisch mit ihren Versätzen dargestellt.
Die Display-Pinfolge 1–10 von links nach rechts ist bestätigt.
Die Anschlusszeichnung reserviert 12 × 6 Lochplätze: Spalten 4–15,
Reihen 20–25; Pins in Reihe 20, Spalten 5–14. Das Gehäuse liegt
zwischen Reihen 23 und 24. Die Kreise am Gehäuse zeigen die Clips
schematisch, ohne festgelegten Bohrdurchmesser.
Beide Display-Anoden (Pins 1 und 2) liegen direkt an +5 V des UNO.
Q1/Q2 und ihre Platzreserve entfallen. Anschlussplätze werden auf Rastergrenzen und
Doppelbelegung geprüft. Es gibt noch keine geprüfte Verdrahtung.
Anodentreiber und Multiplexing sind für diese Schaltung nicht erforderlich.

### J2: bestätigte Displaybelegung

Quelle: `../images/ein_ein-Halb_7-Segmentanzeige_common_Anode.jpg`.
Platzbedarf: `../images/Anschluss_7-Segmentanzeige.jpg`.

| Pin | Funktion | Zuordnung |
| --- | --- | --- |
| 1 | Gemeinsame Anode Einer | Direkt +5 V |
| 2 | Anode Zehner | Direkt +5 V |
| 3 | Gemeinsame Kathode Zehner b+c | R1, U1 (Steuerung D9) |
| 4 | Einer f | R2, U1 (Steuerung D8) |
| 5 | Einer b | R3, U1 (Steuerung D7) |
| 6 | Einer g | R4, U1 (Steuerung D6) |
| 7 | Einer e | R5, U1 (Steuerung D5) |
| 8 | Einer d | R6, U1 (Steuerung D4) |
| 9 | Einer c | R7, U1 (Steuerung D3) |
| 10 | Einer a | R8, U1 (Steuerung D2) |

R1–R8: 220 Ω laut Anzeigenangabe bei 5 V. R1 ergänzt den separaten
Kathodenanschluss der Zehneranzeige. Der Sketch steuert diesen über D9
und zeigt gleichzeitig die Einerziffer über D2–D8 an.

### RN1 neben dem Eingangsblock

RN1 ist als neunpoliges Widerstandsnetzwerk mit acht Widerständen
zu je 10 kΩ und gemeinsamem GND-Anschluss waagerecht mittig in Lochreihe 2 platziert:
Spalten 6–14. Die Darstellung zeigt den gemeinsamen Anschluss
links; die tatsächliche Pinfolge ist vor der Verdrahtung abzugleichen.
RN1-Zweige 2/4/6/8 liegen an J1/J2/J3/J4.
Zweige 1/3/5/7 bleiben frei. Pro Eingang ist ein 10-kΩ-Pulldown vorgesehen; der Sketch verwendet
`INPUT` ohne interne Pull-ups.

### U1: ULN2803A

U1 liegt waagerecht in der Boardmitte, parallel zu RN1 und der
Widerstandsreihe: Spalten 6–14, Pinreihen 14 und 17. Kerbe rechts,
Pin 1 oben rechts; obere Reihe 9–1, untere Reihe 10–18. Die acht
Ausgänge (Pins 11–18) liegen unten direkt bei R1–R8.
DIP-18-Referenz: [ST-Datenblatt](https://www.st.com/resource/en/datasheet/uln2803a.pdf).

Es bleiben acht Anzeigen-Vorwiderstände: sieben für Einer a–g und einer
für die gemeinsame Zehner-Kathode b+c (Displaypin 3). Damit sind acht
ULN-Kanäle vorgesehen: Kanäle 1–7 für a, c, d, e, g, b, f; Kanal 8 für Zehner b+c.
Alle acht Arduino-Steuersignale sind aktiv HIGH, ohne Multiplexing.

| Funktion | UNO | ULN-Eingang | ULN-Ausgang | Widerstand | Displaypin |
| --- | --- | --- | --- | --- | --- |
| Zehner b+c | D9 | 8 | 11 | R1 | 3 |
| f | D8 | 7 | 12 | R2 | 4 |
| b | D7 | 6 | 13 | R3 | 5 |
| g | D6 | 5 | 14 | R4 | 6 |
| e | D5 | 4 | 15 | R5 | 7 |
| d | D4 | 3 | 16 | R6 | 8 |
| c | D3 | 2 | 17 | R7 | 9 |
| a | D2 | 1 | 18 | R8 | 10 |

ULN-Pin 9 liegt an gemeinsamem GND. Beide Display-Anoden liegen an +5 V.

### LED1–LED4: Eingangsanzeige und RN2

L1–L4 zeigen die Werte 8/4/2/1 und liegen direkt unter J1–J4.
Die vier LEDs für Bit 0–3 liegen mit senkrechter Anschlussachse in
Spalten 8, 10, 12 und 14, jeweils Reihen 8/9. Zwischen den LEDs bleibt
jeweils eine freie Lochspalte. Im Entwurf ist die Anode
oben und die Kathode unten dargestellt; die Gehäuse sind schematisch.

RN2 liegt waagerecht darunter: Spalten 7–14, Reihe 10. RN2.1 liegt damit in Spalte 8 direkt unter L1. Es ist als
achtpoliges Netzwerk mit sieben Widerständen zu je 220 Ω und einem
gemeinsamen GND-Anschluss eingezeichnet. Der gemeinsame Anschluss
liegt im Entwurf links; die reale Pinfolge ist abzugleichen.
L1/L2/L3/L4 verwenden RN2-Zweige 1/3/5/7.

Ein Netzwerk mit gemeinsamem GND ersetzt keine einzelnen
Serienwiderstände zwischen ULN-Ausgängen und Segmentkathoden.
R1–R8 bleiben deshalb für die Ziffernanzeige vorgesehen. Die LED-Kathoden verwenden RN2-Zweige 1/3/5/7; 2/4/6 bleiben frei.

### Stromfluss der Eingangsanzeige

Eingang und LED sind elektrisch getrennt:

- J1–J4 → Arduino D10–D13; je ein RN1-Widerstand (10 kΩ) nach GND.
- Arduino A0–A3 → LED-Anode → LED-Kathode → RN2 (220 Ω) → GND.

Der Arduino liest aktive HIGH-Signale und schaltet die passenden LEDs
selbst. Die Anode bleibt oben, die Kathode unten bei RN2. Vier der sieben
RN2-Widerstände werden für die LEDs benötigt: Zweige 1/3/5/7. RN1 und RN2 sind passive
Widerstandsnetzwerke mit gemeinsamem GND, ohne Anode.

Eingangsheader von links nach rechts: J1 = 8 (D10), J2 = 4 (D11),
J3 = 2 (D12), J4 = 1 (D13). L1–L4 folgen dieser Reihenfolge an A0–A3.

## Verdrahtungsplan

Fünf Ansichten mit identischen Bauteilpositionen, jeweils als PNG und SVG:

1. [Eingänge / RN1](verdrahtung_1_eingaenge.png)
2. [Status-LEDs / RN2](verdrahtung_2_leds.png)
3. [Arduino / ULN-Eingänge](verdrahtung_3_uln.png)
4. [ULN-Ausgänge / R1–R8 / Anzeige / +5 V](verdrahtung_4_anzeige.png)
5. [Codierschalter SW1 / J1–J4](verdrahtung_5_codierschalter.png)

Generator: `generate_wiring_layout.py`. Drahtliste: `verdrahtung_verbindungen.txt`.
Die fünf Ansichten sind zusammen zu verwenden. Sie zeigen die Bauteilseite,
keine gespiegelte Lötseite. Linien stehen für isolierte Drähte; an Kreuzungen
besteht keine Verbindung. RN1-G und RN2-G bezeichnen den gemeinsamen
Netzwerkanschluss; Zweignummern sind keine absoluten Gehäusepinnummern.
Die reale RN-Pinfolge ist anhand der Markierung/Datenblätter abzugleichen.

UNO-GND verbindet RN1-G, RN2-G, U1-Pin 9 und den GND der Signalquelle.
Die Signalquelle liefert 0/5 V. Beide Display-Anoden liegen an UNO-5V.
ULN-Pin 10 (COM, Schutzdiodenanschluss) bleibt bei diesen LED-Lasten frei.
Die eingezeichneten Wege sind Verbindungsvorschläge für isolierte Drähte;
Lochbild und rückseitige Kupferverbindungen der realen Platine sind vor
dem Löten abzugleichen.

### Kurze Verbindungen der Ziffernanzeige

R1–R8 liegen in Spalten 7–14, Reihen 18/19. ULN-Ausgänge 11–18
liegen in denselben Spalten in Reihe 17; Display-Pins 3–10 in Reihe 20.
So laufen die Lötbrücken gerade und ohne Kreuzungen: U1.11 → R1 →
Display.3 bis U1.18 → R8 → Display.10. Die UNO-Pins für die logischen
Segmente sind D2/D7/D3/D4/D5/D8/D6; deren Verbindungen zu U1 ändern sich gemäß Tabelle.

RN1 liegt in Reihe 2: GND in Spalte 6, Zweige 2/4/6/8 für J1–J4
in Spalten 8/10/12/14. Zweige 1/3/5/7 sind frei.
J1–J4 liegen in Spalten 8/10/12/14, Reihen 3–5.

**J7 (blau)** liegt in Reihe 2, Spalten 3/4. Beide Kontakte sind miteinander
und mit UNO-GND verbunden. Hier den GND des externen 0/+5-V-Signalgebers
anschließen. J1 (8) ist schwarz, J2 (4) grün, J3 (2) gelb und J4 (1) weiß.
Verdrahtung 1 zeigt die gemeinsame GND-Verbindung von J7, RN1 und UNO.

### KiCad-Schaltplan

Das Projekt [UNO_Anzeige_Zaehler.kicad_pro](kicad/UNO_Anzeige_Zaehler.kicad_pro)
enthält den bearbeitbaren [Schaltplan](kicad/UNO_Anzeige_Zaehler.kicad_sch).
Eine hochauflösende Ansicht liegt als [JPG](kicad/UNO_Anzeige_Zaehler.jpg) vor.
Die verwendeten Symbole sind im Schaltplan eingebettet und zusätzlich in
`kicad/UNO_Project.kicad_sym` mit projektlokaler `sym-lib-table` enthalten.

Geprüft mit KiCad 10.0.6: ERC ohne Fehler oder Warnungen; alle 99 verbundenen
Anschlüsse der exportierten Netzliste entsprechen dem Verdrahtungsplan.
Der Sketch wurde mit simulierten Arduino-Ein-/Ausgängen für alle 16 Werte
geprüft: Start/Reset, Einersegmente, Zehner, LEDs und unveränderte Eingänge.
Die Kompilierung mit der Arduino-UNO-Toolchain und die USB-Übertragung sind
erfolgreich abgeschlossen (siehe PlatformIO-Abschnitt). Ein Funktionstest
der Anzeige am verdrahteten Aufbau steht noch aus.
Der UNO ist als Anschlussblock dargestellt. Die RN1/RN2-Anschlussnummern
bezeichnen Widerstandszweige und G den gemeinsamen Anschluss; die physische
Gehäuse-Pinfolge muss am tatsächlich verwendeten Widerstandsnetzwerk geprüft
werden. Der Schaltplan legt keine PCB-Footprints fest.

### SW1: OTAX KMR162, Codierschalter 0–F

SW1 ist im Bestückungsplan mit sechs Anschlüssen in **Spalten 17 und 20,
Reihen 1–3** ergänzt. Er verwendet Hexadezimal-Realcode (0–F), also vier
Ausgangsbits mit den Werten 1/2/4/8. Die Bezeichnung BCD gilt für 0–9.

| Reihe | Spalte 17 | Spalte 20 |
| --- | --- | --- |
| 1 | Bit 1 | Bit 8 |
| 2 | C (gemeinsamer Kontakt) | C (gemeinsamer Kontakt) |
| 3 | Bit 4 | Bit 2 |

Die Darstellung zeigt die Bauteilseite; die Unterseitenbelegung des
[Datenblatts](https://cdn-reichelt.de/documents/datenblatt/C200/KMR~ELE.pdf)
ist dafür gespiegelt. Das Raster beträgt 7,62 mm zwischen den Pinreihen
und 2,54 mm innerhalb der Reihen; das Gehäuse ist 10 × 10 mm groß.
Beide Common-Kontakte C sind mit UNO-+5V verbunden. Bit 1 führt an J4/D13,
Bit 2 an J3/D12, Bit 4 an J2/D11 und Bit 8 an J1/D10. RN1 hält offene
Kontakte auf LOW: Stellung 0 ergibt 0000, Stellung F ergibt 1111.
Die funktionalen SW1-Pinbezeichnungen im KiCad-Symbol sind 1/2/4/8/C1/C2.

Der Sketch zeigt den Schalterwert als Dezimalzahl 0–15 an.
J1–J4 sind jetzt direkt mit dem Codierschalter verbunden. Dort keine
externen Ausgänge anschließen, die gleichzeitig HIGH/LOW treiben können.
