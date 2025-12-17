// ToF Sensors
#include <VL53L1X.h>
#define b16_tof 2   // Right ToF
#define b17_tof 4   // Middle ToF
#define b18_tof 7   // Left ToF

const uint8_t sensorCount = 3;
const uint8_t xshutPins[sensorCount] = { b18_tof, b17_tof, b16_tof };
VL53L1X sensors[sensorCount];

// RGBW
#define p2_red 3
#define p2_green 5
#define p2_blue 6
#define p2_white 9

// IR Receiver
#define b13_ir_in 13

int pwmRed = 0;
int pwmGreen = 0;
int pwmBlue = 0;
int pwmWhite = 0;

bool irSignal = 0;
int16_t distanceLeft = 0;
int16_t distanceMiddle = 0;
int16_t distanceRight = 0;

unsigned long previousMillis = 0;
unsigned long currentMillis = millis();
const long interval = 250;

String myString;
long myStringInt = 0;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(10);
  while (!Serial) delay(10);

  Wire.begin();
   for (uint8_t i = 0; i < sensorCount; i++)
  {
    pinMode(xshutPins[i], OUTPUT);
    digitalWrite(xshutPins[i], LOW);
  }

  // Enable, initialize, and start each sensor, one by one.
  for (uint8_t i = 0; i < sensorCount; i++)
  {
    pinMode(xshutPins[i], INPUT);
    delay(10);

    sensors[i].setTimeout(500);
    if (!sensors[i].init())
    {
      Serial.print("Failed to detect and initialize sensor ");
      Serial.println(i);
      while (1);
    }

    // Each sensor address is changed from default 0x29 to a unique one
    sensors[i].setAddress(0x2A + i);

    sensors[i].startContinuous(50);
  }

  pinMode(p2_red, OUTPUT);
  pinMode(p2_green, OUTPUT);
  pinMode(p2_blue, OUTPUT);
  pinMode(p2_white, OUTPUT);
  pinMode(b13_ir_in, INPUT);

  for (int i = 0; i <= 252; i++) {
    analogWrite(p2_red, (i * 0.266));
    analogWrite(p2_green, i);
    analogWrite(p2_blue, (i * 0.869));
    delay(15);
  }
  pwmRed = 67;
  pwmGreen = 252;
  pwmBlue = 219;
}

void loop() {
  myString = getSerial();
  if (myString.startsWith("#")) {
    myString.remove(0, 1);
    myStringInt = myString.toInt();
    setSelectedRGBW(myStringInt); // send the long integer value to the function which activates the RGBW pins
  }
  
  currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    distanceLeft = sensors[0].read();
    distanceMiddle = sensors[1].read();
    distanceRight = sensors[2].read();
    Serial.print(digitalRead(b13_ir_in));
    Serial.print(",");
    Serial.print(distanceLeft);
    Serial.print(",");
    Serial.print(distanceMiddle);
    Serial.print(",");
    Serial.print(distanceRight);
    Serial.println();
  }

  if ((pwmRed == 255) && (pwmGreen == 255) && (pwmBlue == 255)) {
    pwmWhite = 255;
  } else {
    pwmWhite = 0;
  }

  analogWrite(p2_red, pwmRed);
  analogWrite(p2_green, pwmGreen);
  analogWrite(p2_blue, pwmBlue);
  analogWrite(p2_white, pwmWhite);
}

String getSerial() {
  String a;
  while (Serial.available()) {
    a = Serial.readString();
  }
  return (a);
}

void setSelectedRGBW(long colorValue) {
  pwmRed = (colorValue >> 16);
  pwmGreen = ((colorValue & 0xFF00) >> 8);
  pwmBlue = (colorValue & 0xFF);
}