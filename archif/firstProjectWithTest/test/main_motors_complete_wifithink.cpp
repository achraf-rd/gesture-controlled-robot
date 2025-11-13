#include <WiFi.h>

// Wi-Fi credentials
#define WIFI_SSID "think"
#define WIFI_PASS "achraf123490"

// Motor control pin definitions
#define ML_Ctrl 2 // Direction control pin for group B motor
#define ML_PWM 5  // PWM control pin for group B motor
#define MR_Ctrl 4 // Direction control pin for group A motor
#define MR_PWM 16 // PWM control pin for group A motor

// PWM properties
#define PWM_FREQ 5000    // Frequency in Hz
#define PWM_RESOLUTION 8 // Resolution in bits (0-255)
#define PWM_CHANNEL_ML 0 // PWM channel for left motor
#define PWM_CHANNEL_MR 1 // PWM channel for right motor

WiFiServer wifiServer(80); // Wi-Fi server on port 80

unsigned long lastCommandTime = 0; // Stores the time of the last command
const unsigned long commandTimeout =
    3000; // Timeout period (in milliseconds) to stop motors

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Configure Wi-Fi
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);
  Serial.println("Connecting to WPA/WPA2 Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  wifiServer.begin();
  Serial.println("WiFi Server started.");

  // Motor control setup
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);

  ledcSetup(PWM_CHANNEL_ML, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(ML_PWM, PWM_CHANNEL_ML);

  ledcSetup(PWM_CHANNEL_MR, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(MR_PWM, PWM_CHANNEL_MR);
}

// Function to control the motors based on the command and speed
void controlMotors(String command, int speed) {
  // Clamp speed between 0 and 255
  speed = constrain(speed, 0, 255);

  if (command == "FORWARD") {
    Serial.println("Moving Forward");
    digitalWrite(ML_Ctrl, HIGH);
    digitalWrite(MR_Ctrl, HIGH);
    ledcWrite(PWM_CHANNEL_ML, speed);
    ledcWrite(PWM_CHANNEL_MR, speed);
  } else if (command == "BACKWARD") {
    Serial.println("Moving Backward");
    digitalWrite(ML_Ctrl, LOW);
    digitalWrite(MR_Ctrl, LOW);
    ledcWrite(PWM_CHANNEL_ML, speed);
    ledcWrite(PWM_CHANNEL_MR, speed);
  } else if (command == "LEFT") {
    Serial.println("Turning Left");
    digitalWrite(ML_Ctrl, LOW);  // Reverse left motor
    digitalWrite(MR_Ctrl, HIGH); // Forward right motor
    ledcWrite(PWM_CHANNEL_ML, speed);
    ledcWrite(PWM_CHANNEL_MR, speed);
  } else if (command == "RIGHT") {
    Serial.println("Turning Right");
    digitalWrite(ML_Ctrl, HIGH); // Forward left motor
    digitalWrite(MR_Ctrl, LOW);  // Reverse right motor
    ledcWrite(PWM_CHANNEL_ML, speed);
    ledcWrite(PWM_CHANNEL_MR, speed);
  } else if (command == "STOP") {
    Serial.println("Stopping");
    ledcWrite(PWM_CHANNEL_ML, 0); // Stop left motor
    ledcWrite(PWM_CHANNEL_MR, 0); // Stop right motor
  }
}

// Function to stop the motors
void stopMotors() {
  Serial.println("Timeout: Stopping motors due to no command received.");
  digitalWrite(ML_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_ML, 0);
  digitalWrite(MR_Ctrl, LOW);
  ledcWrite(PWM_CHANNEL_MR, 0);
}

void loop() {
  WiFiClient client = wifiServer.available();
  if (client) {
    Serial.println("Client connected!");

    String command = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        command += c;

        if (c == '\n') {  // End of command
          command.trim(); // Remove any extra whitespace
          Serial.print("Received Command: ");
          Serial.println(command);

          // Split command and speed
          int speed = 200; // Default speed if not specified
          int spaceIndex = command.indexOf(' ');
          String action = command;
          if (spaceIndex > 0) {
            action = command.substring(
                0, spaceIndex); // Extract action (e.g., FORWARD)
            String speedStr =
                command.substring(spaceIndex + 1); // Extract speed
            speed = speedStr.toInt();              // Convert speed to integer
            if (speed == 0 && speedStr != "0") {
              // If conversion fails, use default speed
              speed = 200;
            }
          }

          // Control motors based on the received command and speed
          controlMotors(action, speed);

          // Update the last command time
          lastCommandTime = millis();

          // Acknowledge the command
          client.print("Command executed: ");
          client.print(action);
          client.print(" with speed ");
          client.println(speed);

          command = ""; // Clear the buffer for the next command
        }
      }
    }
    client.stop();
    Serial.println("Client disconnected.");
  }

  // Check for timeout and stop motors if no command received within the timeout
  // period
  if (millis() - lastCommandTime > commandTimeout) {
    stopMotors();
  }
}
