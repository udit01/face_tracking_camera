
#include <Servo.h>

// lower1 y+
// lower2 x+
// lower3 x-
// upper4 Y-
// upper5 X / +-
Servo lower1;
Servo lower2;
Servo lower3;
Servo upper4;
Servo upper5;

Servo lower1_1;
Servo lower2_1;
Servo lower3_1;
Servo upper4_1;
Servo upper5_1;

int start = 0;
int pos = 0;

void setup() {
  //  servo_1.attach(7);
  //  servo_2.attach(8);
  //  servo_3.attach(9);
  //  servo_4.attach(10);
  //  servo_5.attach(11);
  lower1.attach(7);
  lower2.attach(8);
  lower3.attach(9);
  upper4.attach(10);
  upper5.attach(11);
  lower1_1.attach(2);
  lower2_1.attach(3);
  lower3_1.attach(4);
  upper4_1.attach(5);
  upper5_1.attach(6);
}

void loop() {


  for (pos = 30; pos <= 150; pos += 1) {
    // in steps of 1 degree
    lower1.write(pos);
    lower2.write(pos);
    lower3.write(pos);
    upper4.write(pos);
    upper5.write(pos);
    lower1_1.write(pos);
    lower2_1.write(pos);
    lower3_1.write(pos);
    upper4_1.write(pos);
    upper5_1.write(pos);
    delay(20);
  }
  for (pos = 150; pos >= 30; pos -= 1) {
    lower1.write(pos);
    lower2.write(pos);
    lower3.write(pos);
    upper4.write(pos);
    upper5.write(pos);
    lower1_1.write(pos);
    lower2_1.write(pos);
    lower3_1.write(pos);
    upper4_1.write(pos);
    upper5_1.write(pos);

    delay(20);
  }

}
