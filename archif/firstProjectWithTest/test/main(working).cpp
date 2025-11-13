#include <WiFi.h>
#include <WiFiUdp.h>

// Wi-Fi credentials
const char *ssid = "think";            // Replace with your WiFi SSID
const char *password = "achraf123490"; // Replace with your WiFi password

// Motor control pin definitions
#define ML_Ctrl 2 // Direction control pin for left motor
#define ML_PWM 5  // PWM control pin for left motor
#define MR_Ctrl 4 // Direction control pin for right motor
#define MR_PWM 16 // PWM control pin for right motor

// PWM properties
#define PWM_FREQ 5000
#define PWM_RESOLUTION 8
#define PWM_CHANNEL_ML 0
#define PWM_CHANNEL_MR 1

unsigned long lastCommandTime =
    0; // Variable to store the time of the last received command
unsigned long commandTimeout =
    500; // Timeout in milliseconds (500 ms = 0.5 second)

// UDP Server
WiFiUDP udp;
unsigned int localUdpPort = 4210; // Port for UDP communication

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Initialize motor control pins
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);
  pinMode(ML_PWM, OUTPUT);
  pinMode(MR_PWM, OUTPUT);

  // Set PWM properties for the motors
  ledcSetup(PWM_CHANNEL_ML, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL_MR, PWM_FREQ, PWM_RESOLUTION);

  ledcAttachPin(ML_PWM, PWM_CHANNEL_ML);
  ledcAttachPin(MR_PWM, PWM_CHANNEL_MR);

  // Start UDP
  if (udp.begin(localUdpPort)) {
    Serial.print("UDP server started on port ");
    Serial.println(localUdpPort);
  } else {
    Serial.println("Failed to start UDP server!");
  }
}

void controlMotors(String command) {
  int speed = 200;     // Default speed for forward and backward
  int turnSpeed = 55; // Reduced speed for turning left and right

  if (command == "FORWARD") {
    Serial.println("Moving Forward");
    digitalWrite(ML_Ctrl, HIGH);
    ledcWrite(PWM_CHANNEL_ML, turnSpeed); // Set speed for left motor
    digitalWrite(MR_Ctrl, HIGH);
    ledcWrite(PWM_CHANNEL_MR, turnSpeed); // Set speed for right motor
  } else if (command == "BACKWARD") {
    Serial.println("Moving Backward");
    digitalWrite(ML_Ctrl, LOW);
    digitalWrite(MR_Ctrl, LOW);
    ledcWrite(PWM_CHANNEL_ML, speed);
    ledcWrite(PWM_CHANNEL_MR, speed);
  } else if (command == "LEFT") {
    Serial.println("Turning Left");
    digitalWrite(ML_Ctrl, LOW);           // Reverse left motor
    digitalWrite(MR_Ctrl, HIGH);          // Forward right motor
    ledcWrite(PWM_CHANNEL_ML, 100);     // Reduced speed for left turn
    ledcWrite(PWM_CHANNEL_MR, 100); // Reduced speed for right motor
  } else if (command == "RIGHT") {
    Serial.println("Turning Right");
    digitalWrite(ML_Ctrl, HIGH);          // Forward left motor
    digitalWrite(MR_Ctrl, LOW);           // Reverse right motor
    ledcWrite(PWM_CHANNEL_ML, 100); // Reduced speed for left motor
    ledcWrite(PWM_CHANNEL_MR, 100);     // Reduced speed for right turn
  } else if (command == "STOP") {
    Serial.println("Stopping");
    digitalWrite(ML_Ctrl, LOW);
    ledcWrite(PWM_CHANNEL_ML, 0);
    digitalWrite(MR_Ctrl, LOW);
    ledcWrite(PWM_CHANNEL_MR, 0);
  }
}

void loop() {
  char incomingPacket[255];
  int packetSize = udp.parsePacket();

  if (packetSize) {
    int len = udp.read(incomingPacket, 255);
    if (len > 0) {
      incomingPacket[len] = '\0'; // Null-terminate the packet
    }
    String command = String(incomingPacket);
    Serial.print("Received Command: ");
    Serial.println(command);
    controlMotors(command); // Control motors based on the command
    lastCommandTime =
        millis(); // Update the time when the last command was received
  } else {
    // If no command is received for the specified timeout, stop the motors
    if (millis() - lastCommandTime > commandTimeout) {
      Serial.println("No command received, stopping motors.");
      controlMotors("STOP"); // Stop the motors if timeout is reached
    }
  }
}