
#include <Servo.h>

// lower1 y+
// lower2 x+
// lower3 x-
// upper4 Y-
// upper5 X / +-

Servo upper1;
Servo upper2;
Servo lower3;
Servo lower4;
Servo lower5;

int start = 0;
int pos = 0;

void setup() {
  //  servo_1.attach(7);
  //  servo_2.attach(8);
  //  servo_3.attach(9);
  //  servo_4.attach(10);
  //  servo_5.attach(11);
  upper1.attach(1);
  upper2.attach(2);
  lower3.attach(3);
  lower4.attach(4);
  lower5.attach(5);
}

void loop() {
          upper1.write(30);

    upper2.write(30);
        lower3.write(30);
                lower4.write(90);
                        lower5.write(30);
    delay(10);

}
