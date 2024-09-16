
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

  start = 1;
}
void fixUpperServos(){
    for (pos = 90; pos <=  180; pos += 1) {
      printf("upper 4: %d", pos);
    upper4.write(pos);
   delay(100);
    }
//  for (pos = 90; pos <=  180; pos += 1) {
//    printf("upper 5: %d", pos);
//    upper5.write(pos);
//  delay(100);
//  }

}
void loop() {
  if (start > 0){
    fixUpperServos();
    start = 1;
  }
// Vertical
//  for (pos = 0; pos <= 90; pos += 1) {
//    // in steps of 1 degree
//    lower1.write(pos);
//    delay(100);
//  }
//  for (pos = 90; pos >= 0; pos -= 1) {
//    lower1.write(pos);
//    delay(100);
//  }


}
