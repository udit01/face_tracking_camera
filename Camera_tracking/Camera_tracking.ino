//Sketch based on work done by Robin2 on the arduino forum
//more info here
//https://forum.arduino.cc/index.php?topic=225329.msg1810764#msg1810764


#include <Servo.h>

//Servo panServo;
//Servo tiltServo; 
Servo upper1;
Servo upper2;
Servo lower3;
Servo lower4;
Servo lower5;
//
//byte redledPin = 2;
//byte yellowledPin = 3;
//byte greenledPin = 4;
//
//
//byte redledPin = 6;
//byte yellowledPin = 7;
//byte greenledPin = 8;


const byte buffSize = 40;
char inputBuffer[buffSize];
const char startMarker = '<';
const char endMarker = '>';
byte bytesRecvd = 0;
boolean readInProgress = false;
boolean newDataFromPC = false;

//float panServoAngle = 90.0;
//float tiltServoAngle = 90.0;


int servo1_good_angle = 145;
int servo2_good_angle = 110;
int servo3_good_angle = 30;
int servo4_good_angle = 145;
int servo5_good_angle = 30;


float servo1_angle = servo1_good_angle;
float servo2_angle = servo2_good_angle;
float servo3_angle = servo3_good_angle;
float servo4_angle = servo4_good_angle;
float servo5_angle = servo5_good_angle;



int LED_state = 0;



//8=============D

void setup() {
  while (!Serial);
  Serial.begin(9600);
//   while (!Serial)
//   {;}
//  panServo.attach(8);
//  tiltServo.attach(9);
    upper1.attach(1);
    upper2.attach(2);
    lower3.attach(3);
    lower4.attach(4);
    lower5.attach(5);
    
//  pinMode(redledPin, OUTPUT);
//  pinMode(yellowledPin, OUTPUT);
//  pinMode(greenledPin, OUTPUT);
//  
  //moveServo();
  start_sequence();

  delay(5000);
  
  Serial.println("<Hasta la vista baby>"); // send message to computer
}

//8=============D

void loop() {
  getDataFromPC();
  replyToPC();
  moveServo();
//  setLED();
}

//8=============D

void getDataFromPC() {

    // receive data from PC and save it into inputBuffer
    
  if(Serial.available() > 0) {

    char x = Serial.read();              //read char from serial
      
    if (x == endMarker) {                //look for end marker
      readInProgress = false;            //if found, set read in progress true (will stop adding new byte to buffer)
      newDataFromPC = true;              //let arduino know that new data is available
      inputBuffer[bytesRecvd] = 0;       //clear input buffer
      processData();                      // process data in buffer
    }
    
    if(readInProgress) {
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

   strtokIndx = strtok(inputBuffer,",");      // get the first part
   servo1_angle = atof(strtokIndx);         // convert this part to a float

   strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
   servo2_angle = atof(strtokIndx);     // convert this part to a float

   strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
   servo3_angle = atof(strtokIndx);     // convert this part to a float
   
   strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
   servo4_angle = atof(strtokIndx);     // convert this part to a float
   
   strtokIndx = strtok(NULL,",");          // get the second part(this continues where the previous call left off)
   servo5_angle = atof(strtokIndx);     // convert this part to a float

   strtokIndx = strtok(NULL, ",");      // get the last part
   LED_state = atoi(strtokIndx);          // convert this part to an integer (string to int)
}

//8=============D

void replyToPC() {

  if (newDataFromPC) {
    newDataFromPC = false;
    Serial.print("<");
    Serial.print(upper1.read());
    Serial.print(",");
    Serial.print(upper2.read());
    Serial.print(",");
    Serial.print(lower3.read());
    Serial.print(",");
    Serial.print(lower4.read());
    Serial.print(",");
    Serial.print(lower5.read());
    Serial.println(">");
  }
}

//8=============D

void moveServo() 
{
//  panServo.write(panServoAngle);
//  tiltServo.write(tiltServoAngle);
  upper1.write(servo1_angle);
  upper2.write(servo2_angle);
  lower3.write(servo3_angle);
  lower4.write(servo4_angle);
  lower5.write(servo5_angle);
}
//
//void setLED()
//{
//  if(LED_state == 2){
//    digitalWrite(redledPin, LOW);
//    digitalWrite(yellowledPin, HIGH);
//    digitalWrite(greenledPin, LOW);
//    }
//  else if(LED_state == 1){
//    digitalWrite(redledPin, LOW);
//    digitalWrite(yellowledPin, LOW);
//    digitalWrite(greenledPin, HIGH);    
//    }
//  else if(LED_state == 0){
//    digitalWrite(redledPin, HIGH);
//    digitalWrite(yellowledPin, LOW);
//    digitalWrite(greenledPin, LOW);  
//    }  
//  else if(LED_state == 3){
//    digitalWrite(redledPin, HIGH);
//    digitalWrite(yellowledPin, HIGH);
//    digitalWrite(greenledPin, HIGH);  
//    }  
//  else{
//    digitalWrite(redledPin, LOW);
//    digitalWrite(yellowledPin, LOW);
//    digitalWrite(greenledPin, LOW);    
//    }
//  
//  }
//
////8=============D

  void start_sequence()
  {
    upper1.write(servo1_good_angle);
    upper2.write(servo2_good_angle);
    lower3.write(servo3_good_angle);
    lower4.write(servo4_good_angle);
    lower5.write(servo5_good_angle);
    
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
