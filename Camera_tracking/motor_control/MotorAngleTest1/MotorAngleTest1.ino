
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
}

void loop() {

    lower1.write(60);
    lower2.write(100);
    lower3.write(90);
    upper4.write(30);
    upper5.write(90);



}
