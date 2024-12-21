// Works on Leonardo. Does not seem to work for Due. See https://github.com/arduino/Arduino/pull/3343

uint32_t brkStart = 0;
uint16_t brkLength = 0;
uint32_t baud = 9600;

uint8_t DTR_PIN = A0;
uint8_t RTS_PIN = A1;

#if defined(ARDUINO_ARCH_AVR)
// Leo
#define SerialUSB Serial
#define SerialHW  Serial1
#else
// Due
#define SerialHW  Serial
#endif

void setup() {
  // Baudrate is ignored
  SerialUSB.begin(0);
  // Initialize using an arbitrary default baudrate
  SerialHW.begin(baud);
}

#if defined(ARDUINO_ARCH_AVR)
// Leonardo
void setBreak(bool enable) {
  if (enable) {
    // If a break was requested, force the TX pin low and then disable the
    // UART TX side so the digitalWrite actually takes effect
    pinMode(1, OUTPUT);
    digitalWrite(1, LOW);
    UCSR1B &= ~(1 << TXEN1);
  } else {
    UCSR1B |= (1 << TXEN1);
  }
}

bool inBreak() {
  return (UCSR1B & (1 << TXEN1)) == 0;
}
#else
// Due
static bool breakIsSet = false;
void setBreak(bool enable) {
  if (enable) {
    PIO_SetOutput(g_APinDescription[1].pPort,
                  g_APinDescription[1].ulPin,
                  LOW, 0, 0);
    breakIsSet = true;
  } else {
    // Reset the default pin configuration for the TX pin (assigned to
    // the UART)
    PIO_Configure(g_APinDescription[1].pPort,
                  g_APinDescription[1].ulPinType,
                  g_APinDescription[1].ulPin,
                  g_APinDescription[1].ulPinConfiguration);
    breakIsSet = false;
  }
}

bool inBreak() {
  return breakIsSet;
}
#endif

void loop() {
  // Forward the DTR and RTS signals. Use OUTPUT LOW to pull low and
  // INPUT to leave the pin floating. This needs a pullup on the other
  // side, but also works when the other device is 3.3V
  // TODO: On SAM, setting OUTPUT also sets the pin high, so this code
  // doesn't work there.
  pinMode(DTR_PIN, SerialUSB.dtr() ? OUTPUT : INPUT);
  pinMode(RTS_PIN, SerialUSB.rts() ? OUTPUT : INPUT);

  // Process break requests
  int32_t brk = SerialUSB.readBreak();
  if (brk > 0) {
    Serial.flush();
    setBreak(true);

    // If the break has a defined length, keep track of it so it can be
    // disabled at the right time
    if (brk != 0xffff) {
      brkLength = brk;
      brkStart = micros();
    }
  } else if (brk == 0 || (brkLength > 0 && (micros() - brkStart) >= 1000L * brkLength)) {
    // If a timed break was running and its time expires, or if the
    // break is explicitly canceled through a request with time = 0,
    // end the break
    setBreak(false);
    brkLength = 0;
  }

  // If the requested baudrate changed on SerialUSB, update it on Serial
  // too (but not while a break condition is ongoing, since calling
  // SerialHW.begin() will end the break condition
  if (!inBreak() && SerialUSB.baud() != baud) {
    baud = SerialUSB.baud();

#if defined(ARDUINO_ARCH_AVR)
    // Set up the TX pin as OUTPUT HIGH, so that when the UART is
    // disabled, the pin remains high
    // On SAM, using pinMode/digitalWrite permanently takes away the pin
    // from the UART, so something more complex might be needed there.
    pinMode(1, OUTPUT);
    digitalWrite(1, HIGH);
#endif

    SerialHW.end();
    SerialHW.begin(baud);
  }

  // Forward data between SerialUSB and Serial
  if (!inBreak()) {
    // Only write to Serial when TX is enabled, to prevent lockup
    if (SerialUSB.available())
      SerialHW.write(SerialUSB.read());
  }
  if (SerialHW.available())
    SerialUSB.write(SerialHW.read());
}