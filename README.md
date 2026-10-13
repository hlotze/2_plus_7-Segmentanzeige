# 2_plus_7-Segmentanzeige

Arduino-UNO-Projekt für eine 1½-stellige Common-Anode-7-Segmentanzeige
mit ULN2803A. Vier Binäreingänge liefern Werte von 0 bis 15; vier LEDs
zeigen den Binärwert an.

- Standard: Dezimalanzeige **0–15** mit Zehneranzeige.
- Drahtbrücke **GND–A4**: Hexadezimalanzeige **0–F**, Zehner aus.

## Dokumentation und Schaltung

Die [ausführliche Projektdokumentation](uno_1_5_digit_display/README.md)
enthält Pinbelegung, Software-Logik, Bestückung und Verdrahtung.
Sketch, Zeichnungsgeneratoren, Schaltungsansichten und das bearbeitbare
KiCad-Projekt liegen unter `uno_1_5_digit_display/`; Referenzbilder unter `images/`.

## Build und Upload

Dieses Verzeichnis in VS Code mit PlatformIO öffnen. Die Umgebung `uno`
ist in `platformio.ini` konfiguriert.

```sh
pio run
pio run --target upload
```

Den USB-Port in `platformio.ini` bei Bedarf anpassen. Build und Upload
wurden erfolgreich geprüft; ein Funktionstest am verdrahteten Aufbau steht aus.

Build-Dateien, virtuelle Python-Umgebungen und lokale KiCad-Einstellungen
werden durch `.gitignore` ausgeschlossen. Die erzeugten Schaltungs- und
Verdrahtungsansichten bleiben zur direkten Ansicht im Repository enthalten.
