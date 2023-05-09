/*
   3drobot firmware.

*/

//#define F_CPU 12000000
#define pi 3.1415926535897932384626433832795

#include <AccelStepper.h>
#include <ArduinoJson.h>

#define X_STEP_PIN         A0
#define X_DIR_PIN          A1
#define X_ENABLE_PIN       38

#define Y_STEP_PIN         A6
#define Y_DIR_PIN          A7
#define Y_ENABLE_PIN       A2

#define Z_STEP_PIN         46
#define Z_DIR_PIN          48
#define Z_ENABLE_PIN       A8

#define E_STEP_PIN         26
#define E_DIR_PIN          28
#define E_ENABLE_PIN       24

//#define E2_STEP_PIN        36
//#define E2_DIR_PIN         34
//#define E2_ENABLE_PIN      30
//#define E2_ENDSTOP         18 




// Define stepper motors connection pins (Type:driver, STEP, DIR).
AccelStepper LeftFrontWheel(1, E_STEP_PIN, E_DIR_PIN);  // Stepper1
AccelStepper LeftBackWheel(1, Z_STEP_PIN, Z_DIR_PIN);   // Stepper2
AccelStepper RightBackWheel(1, Y_STEP_PIN, Y_DIR_PIN);  // Stepper3
AccelStepper RightFrontWheel(1, X_STEP_PIN, X_DIR_PIN); // Stepper4

// Global variables.
int wheelSpeed = 0, contseg = 0, cont = 1, load = 0;
int r = 42;                                                                 // Wheel radius.r

float vX = 0, vY = 0, lt = 0, startTime = 0, vX_1, vY_1;                                    // Linear speed [m/s].
float vA = 0;                                                               // Angular speed [rad/s].
float cmdExtTemp = 0, extTemp = 0;                                          // Command extruder temperature and actual value [°C].

float a1 = pi / 4, a2 = 3 * pi / 4, a3 = 5 * pi / 4, a4 = 7 * pi / 4, w = pi, R = 181.07; // Kinematics parameters.
float v1 = 0, v2 = 0, v3 = 0, v4 = 0;                                       //Wheel angular speed [rad/s].
float vs1 = 0, vs2 = 0, vs3 = 0, vs4 = 0;                                   //Wheel angular speed [step/s].

unsigned long timeNow = 0;

//------
float stepDelay = 5;                                                     // Stepper motor step delay [seconds].
int period = stepDelay * 1000;
int microstep = 32;

DynamicJsonDocument doc(300);
String text;
String json; 


void setup() {

  Serial.begin(250000);

  pinMode(X_STEP_PIN  , OUTPUT);
  pinMode(X_DIR_PIN    , OUTPUT);
  pinMode(X_ENABLE_PIN    , OUTPUT);

  pinMode(Y_STEP_PIN  , OUTPUT);
  pinMode(Y_DIR_PIN    , OUTPUT);
  pinMode(Y_ENABLE_PIN    , OUTPUT);

  pinMode(Z_STEP_PIN  , OUTPUT);
  pinMode(Z_DIR_PIN    , OUTPUT);
  pinMode(Z_ENABLE_PIN    , OUTPUT);

  pinMode(E_STEP_PIN  , OUTPUT);
  pinMode(E_DIR_PIN    , OUTPUT);
  pinMode(E_ENABLE_PIN    , OUTPUT);


  digitalWrite(X_ENABLE_PIN    , LOW);
  digitalWrite(Y_ENABLE_PIN    , LOW);
  digitalWrite(Z_ENABLE_PIN    , LOW);
  digitalWrite(E_ENABLE_PIN    , LOW);


  // Set maximum speeds per motor.
  LeftFrontWheel.setMaxSpeed(15000);
  LeftBackWheel.setMaxSpeed(15000);
  RightBackWheel.setMaxSpeed(15000);
  RightFrontWheel.setMaxSpeed(15000);

}

void loop() {

}
void serialEvent() {
  while (Serial.available()) {
    json = Serial.readStringUntil('\n');//Se envía en el serial así:
    //{"vX":333,"vY":333,"lt":333}
    DeserializationError error = deserializeJson(doc, json);
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.print(error.f_str());
      Serial.println(json);
      return;
    }
    vX = doc["vX"];
    vY = doc["vY"];
    lt = doc["lt"];
    // Serial.print("vX: ");
    // Serial.print(vX);
    // Serial.print(" vY: ");
    // Serial.print(vY);
    // Serial.print(" lt: ");
    // Serial.println(lt);
    calculateSpeeds();

    setExSpeeds();
    startTime = millis();
    while(millis()-startTime < lt){
      setExSpeeds();
    }
    Serial.print("ok\n");
  }
}


void calculateSpeeds() {

  //float a1 = pi/4, a2 = 3*pi/4, a3 = 5*pi/4, a4 = 7*pi/4, w = pi, R = 181.07, r=42;

  // Calculate angular speed per wheel in rad/s.
  v1 = (-sin(w + a1) * vX + cos(w + a1) * vY + R * vA) / r;
  v2 = (-sin(w + a2) * vX + cos(w + a2) * vY + R * vA) / r;
  v3 = (-sin(w + a3) * vX + cos(w + a3) * vY + R * vA) / r;
  v4 = (-sin(w + a4) * vX + cos(w + a4) * vY + R * vA) / r;

  // Obtain angular speed in step/s.
  vs1 = v1 * 31.83098862 * microstep;
  vs2 = v2 * 31.83098862 * microstep;
  vs3 = v3 * 31.83098862 * microstep;
  vs4 = v4 * 31.83098862 * microstep;

  if (abs(vs1) > 15000 | abs(vs2) > 15000 | abs(vs3) > 15000 | abs(vs4) > 15000) {
    vs1 = 0;
    vs2 = 0;
    vs3 = 0;
    vs4 = 0;
  }
  vX_1 = vX;
  vY_1 = vY;
}

void setExSpeeds() {

  LeftFrontWheel.setSpeed(vs1);
  LeftFrontWheel.runSpeed();
  LeftBackWheel.setSpeed(vs2);
  LeftBackWheel.runSpeed();
  RightBackWheel.setSpeed(vs3);
  RightBackWheel.runSpeed();
  RightFrontWheel.setSpeed(vs4);
  RightFrontWheel.runSpeed();

}
