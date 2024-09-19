
#include <Servo.h>

Servo servo_1;
Servo servo_2;
Servo servo_3;
Servo servo_4;
Servo servo_5;


int pos = 0;

void setup() {
  servo_1.attach(7);
  servo_2.attach(8);
  servo_3.attach(9);
  servo_4.attach(10);
  servo_5.attach(11);
}

void loop() {

// Vertical
  for (pos = 0; pos <= 90; pos += 1) {
    // in steps of 1 degree
    servo_3.write(pos);
    delay(100);
  }
  for (pos = 90; pos >= 0; pos -= 1) {
    servo_3.write(pos);
    delay(100);
  }




}
