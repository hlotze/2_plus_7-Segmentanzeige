// 1½-stellige Common-Anode-Anzeige: Binäreingänge 0–15 am UNO R3.
// Eingänge D10–D13: aktiv HIGH, externe 10-kΩ-Pulldowns über RN1.
// ULN2803A: HIGH = Segment an. Display-Anoden (Pins 1/2) fest an +5 V.
// L1–L4: A0–A3 → LED-Anode → LED-Kathode → RN2 (220 Ω) → GND.
// A4: INPUT_PULLUP; offen = Dezimal, mit GND verbunden = Hexadezimal.

const byte INPUT_PINS[] = {10, 11, 12, 13};  // J1–J4: Werte 8, 4, 2, 1
byte displayedValue = 0;  // aktuell angezeigter Eingangswert
const byte MODE_PIN = A4;
bool displayedHexMode = false;

const byte INPUT_LED_PINS[] = {A0, A1, A2, A3};
// ULN-Eingänge für a–g: Pins 1, 6, 2, 3, 4, 7, 5.
// R1 = Zehner; R2–R8 = f, b, g, e, d, c, a.
const byte SEGMENT_PINS[] = {2, 7, 3, 4, 5, 8, 6};  // a, b, c, d, e, f, g
const byte TENS_PIN = 9;  // ULN-Kanal 8 → R1 → Displaypin 3 (Zehner b+c)

// Bits 0–6 entsprechen a–g. HIGH schaltet den jeweiligen ULN-Kanal ein.
const byte DIGIT_MASKS[] = {
  0x3F,  // 0: a b c d e f
  0x06,  // 1: b c
  0x5B,  // 2: a b d e g
  0x4F,  // 3: a b c d g
  0x66,  // 4: b c f g
  0x6D,  // 5: a c d f g
  0x7D,  // 6: a c d e f g
  0x07,  // 7: a b c
  0x7F,  // 8: a b c d e f g
  0x6F,  // 9: a b c d f g
  0x77,  // A: a b c e f g
  0x7C,  // b: c d e f g
  0x39,  // C: a d e f
  0x5E,  // d: b c d e g
  0x79,  // E: a d e f g
  0x71   // F: a e f g
};

void initOutputOff(byte pin) {
  // Ausgangslatch vor OUTPUT auf LOW setzen, damit kein Einschaltimpuls entsteht.
  digitalWrite(pin, LOW);
  pinMode(pin, OUTPUT);
}

byte readInputValue() {
  byte value = 0;
  for (byte bit = 0; bit < 4; ++bit) {
    if (digitalRead(INPUT_PINS[bit]) == HIGH) {
      value |= (1 << (3 - bit));
    }
  }
  return value;
}

void showValue(byte value, bool hexMode) {
  const byte mask = DIGIT_MASKS[hexMode ? value : value % 10];
  // Im Hexmodus bleibt die Zehneranzeige immer aus.
  digitalWrite(TENS_PIN, !hexMode && value >= 10 ? HIGH : LOW);
  for (byte segment = 0; segment < 7; ++segment) {
    digitalWrite(SEGMENT_PINS[segment], (mask & (1 << segment)) ? HIGH : LOW);
  }
  // Zehner und Einer leuchten gleichzeitig; kein Multiplexing nötig.
  for (byte bit = 0; bit < 4; ++bit) {
    digitalWrite(INPUT_LED_PINS[bit], (value & (1 << (3 - bit))) ? HIGH : LOW);
  }
}

void setup() {
  pinMode(MODE_PIN, INPUT_PULLUP);
  for (byte bit = 0; bit < 4; ++bit) {
    // Keine internen Pull-ups: RN1 hält unbeschaltete Eingänge auf LOW.
    digitalWrite(INPUT_PINS[bit], LOW);
    pinMode(INPUT_PINS[bit], INPUT);
    initOutputOff(INPUT_LED_PINS[bit]);
  }
  for (byte segment = 0; segment < 7; ++segment) {
    initOutputOff(SEGMENT_PINS[segment]);
  }
  initOutputOff(TENS_PIN);
  displayedValue = 0;
  displayedHexMode = digitalRead(MODE_PIN) == LOW;
  showValue(0, displayedHexMode);  // loop übernimmt anschließend den Eingangswert.
}

void loop() {
  const byte value = readInputValue();
  const bool hexMode = digitalRead(MODE_PIN) == LOW;
  if (value != displayedValue || hexMode != displayedHexMode) {
    displayedValue = value;
    displayedHexMode = hexMode;
    showValue(value, hexMode);  // Auch bei reinem Moduswechsel aktualisieren.
  }
}
