//Sketch based on work done by Robin2 on the arduino forum
//more info here
//https://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764


#include <Servo.h>

//Servo panServo;
//Servo tiltServo;
Servo servo_x;
Servo servo_y;
//Servo lower3;
//Servo lower4;
//Servo lower5;
//
Servo rightup;
Servo leftup;
Servo rightdown;
Servo leftdown;
//byte redledPin = 2;
//byte yellowledPin = 3;
//byte greenledPin = 4;
//
//
byte redledPin = 8;
byte yellowledPin = 10;
byte greenledPin = 12;


const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

//float panServoAngle = 90.0;
//float tiltServoAngle = 90.0;


int servo1_good_angle = 90;
int servo2_good_angle = 90;

int servo3_good_angle = 30;
int servo4_good_angle = 145;
int servo5_good_angle = 30;


float servo1_angle = servo1_good_angle;
float servo2_angle = servo2_good_angle;
float servo3_angle = servo3_good_angle;
float servo4_angle = servo4_good_angle;
float servo5_angle = servo5_good_angle;

float rightup_angle = 10;
float leftup_angle = 170;
float rightdown_angle = 180;
float leftdown_angle = 60;

int LED_state = 2;

unsigned long lastBlinkTime = 0;
unsigned long blinkInterval = 5000; // 5 seconds interval for blinking
boolean isEyesClosed = false;



//8=============D

void setup() {
  while (!Serial);
  Serial.begin(9600);
  //   while (!Serial)
  //   {;}
  //  panServo.attach(8);
  //  tiltServo.attach(9);
  servo_x.attach(2);
  servo_y.attach(3);
  //lower3.attach(3);
  //lower4.attach(4);
  //lower5.attach(5);
  rightup.attach(4);
  leftup.attach(5);
  rightdown.attach(6);
  leftdown.attach(7);

  pinMode(redledPin, OUTPUT);
  pinMode(yellowledPin, OUTPUT);
  pinMode(greenledPin, OUTPUT);
  //
  moveServo();
  start_sequence();

  delay(5000);

  Serial.println("<Hasta la vista baby>"); // send message to computer
}

//8=============D

void loop() {
  getDataFromPC();
  moveServo();
  // blinkEyes();
  replyToPC();

    setLED();
}

//8=============D

void getDataFromPC() {

  // receive data from PC and save it into inputBuffer

  if (Serial.available() > 0) {

    char x = Serial.read();              //read char from serial

    if (x == endMarker) {                //look for end marker
      readInProgress = false;            //if found, set read in progress true (will stop adding new byte to buffer)
      newDataFromPC = true;              //let arduino know that new data is available
      inputBuffer[bytesRecvd] = 0;       //clear input buffer
      processData();                      // process data in buffer
    }

    if (readInProgress) {
      inputBuffer[bytesRecvd] = x;      //populate input buffer with bytes
      bytesRecvd ++;                    //increment index
      if (bytesRecvd == buffSize) {     //when buffer is full
        bytesRecvd = buffSize - 1;      //keep space for end marker
      }
    }

    if (x == startMarker) {              // look for start maker
      bytesRecvd = 0;                    // if found, set byte received to 0
      readInProgress = true;             // set read in progress true
    }
  }
}

//8=============D

void processData() // for data type "<float, float, int>"
{
  char * strtokIndx; // this is used by strtok() as an index

  strtokIndx = strtok(inputBuffer, ",");     // get the first part
  servo1_angle = atof(strtokIndx);         // convert this part to a float

  strtokIndx = strtok(NULL, ",");         // get the second part(this continues where the previous call left off)
  servo2_angle = atof(strtokIndx);     // convert this part to a float

  strtokIndx = strtok(NULL, ",");          // get the third part
  rightup_angle = atof(strtokIndx);     // convert this part to a float

  strtokIndx = strtok(NULL, ",");          // get the fourth part
  leftup_angle = atof(strtokIndx);     // convert this part to a float

  strtokIndx = strtok(NULL, ",");          // get the fifth part
  rightdown_angle = atof(strtokIndx);     // convert this part to a float

  strtokIndx = strtok(NULL, ",");          // get the sixth part
  leftdown_angle = atof(strtokIndx);     // convert this part to a float

  //strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
  //servo3_angle = atof(strtokIndx);     // convert this part to a float

  //strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
  //servo4_angle = atof(strtokIndx);     // convert this part to a float

  //strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
  //servo5_angle = atof(strtokIndx);     // convert this part to a float

  strtokIndx = strtok(NULL, ",");      // get the last part
  LED_state = atoi(strtokIndx);          // convert this part to an integer (string to int)
}

//8=============D

void replyToPC() {

  if (newDataFromPC) {
    newDataFromPC = false;
    Serial.print("<");
    Serial.print(servo_x.read());
    Serial.print(",");
    Serial.print(servo_y.read());

    Serial.print(",");
    Serial.print(rightup.read());
    Serial.print(",");
    Serial.print(leftup.read());
    Serial.print(",");
    Serial.print(rightdown.read());
    Serial.print(",");
    Serial.print(leftdown.read());
    Serial.println(">");

    
    //Serial.print(",");
    //Serial.print(lower3.read());
    //Serial.print(",");
    //Serial.print(lower4.read());
    //Serial.print(",");
    //Serial.print(lower5.read());
    Serial.println(">");
  }
}

//8=============D

void moveServo()
{
  //  panServo.write(panServoAngle);
  //  tiltServo.write(tiltServoAngle);
  servo_x.write(servo1_angle);
  //servo_x.write(140);
  servo_y.write(servo2_angle);

  rightup.write(80);
  leftup.write(100);
  rightdown.write(110);
  leftdown.write(120);
  
  //lower3.write(servo3_angle);
  //lower4.write(servo4_angle);
  //lower5.write(servo5_angle);
  //delay(100);
  //rightup.write(10);
  //rightdown.write(180);
  //leftup.write(100);
  //leftdown.write(100);
}
//

void blinkEyes() {
  unsigned long currentTime = millis();
  if (currentTime - lastBlinkTime >= blinkInterval) {
    if (isEyesClosed) {
      // Open eyes
      rightup_angle = 10;
      leftup_angle = 170;
      rightdown_angle = 180;
      leftdown_angle = 60;
      isEyesClosed = false;
    } else {
      // Close eyes
      rightup_angle = 80;
      leftup_angle = 100;
      rightdown_angle = 110;
      leftdown_angle = 120;
      isEyesClosed = true;
    }
    moveServo();
    lastBlinkTime = currentTime;
  }
}
void setLED()
{
  if (LED_state == 2) {
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, HIGH);
    digitalWrite(greenledPin, LOW);
  }
  else if (LED_state == 1) {
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, HIGH);
  }
  else if (LED_state == 0) {
    digitalWrite(redledPin, HIGH);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, LOW);
  }
  else if (LED_state == 3) {
    digitalWrite(redledPin, HIGH);
    digitalWrite(yellowledPin, HIGH);
    digitalWrite(greenledPin, HIGH);
  }
  else {
    digitalWrite(redledPin, LOW);
    digitalWrite(yellowledPin, LOW);
    digitalWrite(greenledPin, LOW);
  }

}
//
////8=============D

void start_sequence()
{
  servo_x.write(servo1_good_angle);
  servo_y.write(servo2_good_angle);
      rightup.write(rightup_angle);
    leftup.write(leftup_angle);
    rightdown.write(rightdown_angle);
    leftdown.write(leftdown_angle);
  //lower3.write(servo3_good_angle);
  //lower4.write(servo4_good_angle);
  //lower5.write(servo5_good_angle);
  //lower3.write(servo3_good_angle);    //lower3.write(servo3_good_angle);


  delay(3000);

  //
  //    digitalWrite(redledPin, HIGH);
  //    delay(100);
  //    digitalWrite(redledPin, LOW);
  //    digitalWrite(yellowledPin, HIGH);
  //    delay(100);
  //    digitalWrite(yellowledPin, LOW);
  //    digitalWrite(greenledPin, HIGH);
  //    delay(100);
  //
  //    digitalWrite(redledPin, LOW);
  //    digitalWrite(yellowledPin, LOW);
  //    digitalWrite(greenledPin, LOW);
  //    delay(100);
  //    digitalWrite(redledPin, HIGH);
  //    digitalWrite(yellowledPin, HIGH);
  //    digitalWrite(greenledPin, HIGH);
  //    delay(100);
  //    digitalWrite(redledPin, LOW);
  //    digitalWrite(yellowledPin, LOW);
  //    digitalWrite(greenledPin, LOW);
}
