#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>
#include <Servo.h>
Servo myservo;  // create servo object to control a servo

SoftwareSerial SIM900A(10, 8); //tx, rx.... if no TEXT, then switch
static const int RXPin = 4, TXPin = 3;
static const uint32_t GPSBaud = 9600;

// The TinyGPSPlus object
TinyGPSPlus gps;

// The serial connection to the GPS device
SoftwareSerial ss(RXPin, TXPin);

int pushButton = 5;
String messagegps = "";
String emerg_message = "Emergency SOS ";
String emerg_message_unauth = "CAR IS TURNED ON, RUNNING UNSAFE.";

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

int servoPin = 3;
int pos = 0;    // variable to store the servo position
int last_pos;

void sendSMS(String message)
{
  Serial.println ("Sending Message");
  SIM900A.println("AT+CMGF=1");    //Sets the GSM Module in Text Mode
  delay(1000);
  SIM900A.println("AT+CMGS=\"09458390240\"\r"); //+country code with mobile phone number to send message
  delay(1000);
  Serial.println ("Set SMS Content");
  SIM900A.println(message);// Messsage content
  delay(100);
  Serial.println ("Finish");
  SIM900A.println((char)26);// ASCII code of CTRL+Z
  delay(1000);
  Serial.println ("Message has been sent");
}

static void smartDelay(unsigned long ms)
{
  unsigned long start = millis();
  do
  {
    while (ss.available())
      gps.encode(ss.read());
  } while (millis() - start < ms);
}

void setup() {
  // put your setup code here, to run once:
  SIM900A.begin(9600);   // Setting the baud rate of GSM Module
  Serial.begin(19200);    // Setting the baud rate of Serial Monitor (Arduino)
  ss.begin(GPSBaud);
  pinMode(pushButton, INPUT_PULLUP);
  //myservo.attach(servoPin);  // attaches the servo on pin 9 to the servo object
  myservo.write(180); // initial servo position upon startup.
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    stringComplete = true;
    
  }
}

void loop() {
  int buttonState = digitalRead(pushButton);
  
  int Alcohol_gas_Value = analogRead(A0);
  Serial.println(Alcohol_gas_Value);
  delay(300); //250
  smartDelay(0);
  
  if ( buttonState == LOW ) {
    messagegps = emerg_message_unauth;
    messagegps += String(gps.location.lat(), 6); // gps.location.lat() outputs a Floating Point value that has to be converted to STRING and display to the 6th decimal place.
    messagegps += ",";
    messagegps += String(gps.location.lng(), 6);
    Serial.println (messagegps);
    sendSMS(messagegps);
  }

  //Serial.println("Received event: " + inputString);
  if (stringComplete) {
    Serial.println("Completed String: " + inputString);
    if (inputString == "5") {
      Serial.println("Sending message...");
      messagegps = emerg_message;
      messagegps += String(gps.location.lat(), 6); // gps.location.lat() outputs a Floating Point value that has to be converted to STRING and display to the 6th decimal place.
      messagegps += ",";
      messagegps += String(gps.location.lng(), 6);
      Serial.println (messagegps);
      sendSMS(messagegps);
      Serial.println("SMS SENT");
    }
    if (inputString == "B") {
      Serial.println("Closing servo...");
      ss.end(); // Temporary disable the gps serial port
      myservo.attach(servoPin);  // attaches the servo on pin 9 to the servo object
      for (pos = last_pos; pos >= 0; pos -= 1) { // goes from 0 degrees to 180 degrees
        // in steps of 1 degree
        myservo.write(pos);              // tell servo to go to position in variable 'pos'
        delay(15);                       // waits 15 ms for the servo to reach the position
      }
      last_pos = pos;
      Serial.println("Servo Open");
      ss.begin(GPSBaud);
      myservo.detach();
    }
    if (inputString == "A") {
      Serial.println("Opening servo...");
      myservo.attach(servoPin);  // attaches the servo on pin 9 to the servo object
      ss.end(); // Temporary disable the gps serial port

      for (pos = last_pos; pos <= 180; pos += 1) { // goes from 180 degrees to 0 degrees
        myservo.write(pos);              // tell servo to go to position in variable 'pos'
        delay(15);                       // waits 15 ms for the servo to reach the position
      }
      Serial.println("Servo Closed");
    // clear the string:
 
      last_pos = pos;
      ss.begin(GPSBaud);
      myservo.detach();
    }
     inputString = "";
     stringComplete = false;
  }

}
