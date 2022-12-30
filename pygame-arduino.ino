#define RECEIVER_PIN 13
#define PROTOCOL NEC

#include <IRremote.hpp>
#include <IRProtocol.h>

int RECV_PIN = 13;

const char parseCommand(uint16_t command) {
  char ret = 'e';
  switch (command) {
    case 69:
      ret = '1';
      break;
    case 70:
      ret = '2';
      break;
    case 71:
      ret = '3';
      break;
    case 68:
      ret = '4';
      break;
    case 64:
      ret = '5';
      break;
    case 67:
      ret = '6';
      break;
    case 7:
      ret = '7';
      break;
    case 21:
      ret = '8';
      break;
    case 9:
      ret = '9';
      break;
    case 22:
      ret = '*';
      break;
    case 25:
      ret = '0';
      break;
    case 13:
      ret = '#';
      break;
    case 24:
      ret = 'u';
      break;
    case 8:
      ret = 'l';
      break;
    case 28:
      ret = 'o';
      break;
    case 90:
      ret = 'r';
      break;
    case 82:
      ret = 'd';
      break;
    default:
      break;
  }
  return ret;
}

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(RECEIVER_PIN, ENABLE_LED_FEEDBACK);
}

void loop() {
  if (IrReceiver.decode()) {
    if (IrReceiver.decodedIRData.protocol == PROTOCOL) {
      Serial.print(parseCommand(IrReceiver.decodedIRData.command));
    }
    IrReceiver.resume();
  }
}
