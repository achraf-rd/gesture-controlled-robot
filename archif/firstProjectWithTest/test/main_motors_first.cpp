//****************************************************************************
/*
 keyestudio 4wd BT Car (Adapted for ESP32)
 Motor driver shield
*/
#include <Arduino.h>

// Define the direction control and PWM pins
#define ML_Ctrl 2 // Direction control pin for group B motor
#define ML_PWM 5  // PWM control pin for group B motor
#define MR_Ctrl 4 // Direction control pin for group A motor
#define MR_PWM 16 // PWM control pin for group A motor (changed from 6 to 16)

// Define PWM properties
#define PWM_FREQ 5000    // Frequency in Hz
#define PWM_RESOLUTION 8 // Resolution in bits (0-255 for 8-bit)
#define PWM_CHANNEL_ML 0 // Channel for group B motor
#define PWM_CHANNEL_MR 1 // Channel for group A motor

void setup() {
  // Set direction control pins as output
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);

  // Attach PWM to channels and pins
  ledcSetup(PWM_CHANNEL_ML, PWM_FREQ,
            PWM_RESOLUTION);             // Set up PWM for group B motor
  ledcAttachPin(ML_PWM, PWM_CHANNEL_ML); // Attach PWM channel to pin

  ledcSetup(PWM_CHANNEL_MR, PWM_FREQ,
            PWM_RESOLUTION);             // Set up PWM for group A motor
  ledcAttachPin(MR_PWM, PWM_CHANNEL_MR); // Attach PWM channel to pin
}

void loop() {
  // Move forward
  digitalWrite(ML_Ctrl, HIGH);
  ledcWrite(PWM_CHANNEL_ML, 55); // Set speed for group B motor
  digitalWrite(MR_Ctrl, HIGH);
  ledcWrite(PWM_CHANNEL_MR, 55); // Set speed for group A motor
  delay(2000);

  // Move backward
  digitalWrite(ML_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_ML, 200);
  digitalWrite(MR_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_MR, 200);
  delay(2000);

  // Turn left
  digitalWrite(ML_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_ML, 200);
  digitalWrite(MR_Ctrl, HIGH);
  ledcWrite(PWM_CHANNEL_MR, 55);
  delay(2000);

  // Turn right
  digitalWrite(ML_Ctrl, HIGH);
  ledcWrite(PWM_CHANNEL_ML, 55);
  digitalWrite(MR_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_MR, 200);
  delay(2000);

  // Stop
  digitalWrite(ML_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_ML, 0);
  digitalWrite(MR_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_MR, 0);
  delay(2000);
}
//****************************************************************************
