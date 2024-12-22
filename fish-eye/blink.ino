
#include <Servo.h>


Servo hor;
Servo ver;
Servo rightup;
Servo leftup;
Servo rightdown;
Servo leftdown;


int pos = 0;

void setup() {
  hor.attach(1);
  ver.attach(2);
  rightup.attach(3);
  leftup.attach(4);
  rightdown.attach(5);
  leftdown.attach(6);
}

void loop() {
 //open
 
  rightup.write(10);
  rightdown.write(180);
  leftup.write(170);
  leftdown.write(60);

  delay(500);

//close

  rightup.write(80);
  rightdown.write(110);
  leftup.write(100);
  leftdown.write(120);

  delay(3000);



}
