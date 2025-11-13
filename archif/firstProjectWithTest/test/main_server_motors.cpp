#include "esp_wpa2.h" // WPA2 Enterprise support
#include <SPI.h>
#include <WiFi.h>


#define WIFI_SSID ""
#define WIFI_USER ""
#define WIFI_PASS ""

WiFiServer wifiServer(80);

// SPI pins for ESP32
#define SS_PIN 5 // Slave Select (Arduino)
#define SCK_PIN 18
#define MISO_PIN 19
#define MOSI_PIN 23

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Configure Wi-Fi
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);
  Serial.println("Connecting to WPA2 Enterprise Wi-Fi...");

  esp_wifi_sta_wpa2_ent_set_identity((uint8_t *)WIFI_USER, strlen(WIFI_USER));
  esp_wifi_sta_wpa2_ent_set_username((uint8_t *)WIFI_USER, strlen(WIFI_USER));
  esp_wifi_sta_wpa2_ent_set_password((uint8_t *)WIFI_PASS, strlen(WIFI_PASS));
  esp_wifi_sta_wpa2_ent_enable();
  WiFi.begin(WIFI_SSID);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  wifiServer.begin();
  Serial.println("WiFi Server started.");

  // Initialize SPI
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);
  pinMode(SS_PIN, OUTPUT);
  digitalWrite(SS_PIN, HIGH); // Ensure SS is HIGH before communication
}

void sendToArduino(char command) {
  digitalWrite(SS_PIN, LOW);
  SPI.transfer(command);
  digitalWrite(SS_PIN, HIGH);
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

        if (c == '\n') { // End of command
          Serial.print("Received: ");
          Serial.println(command);

          // Convert Wi-Fi commands to SPI commands
          if (command.startsWith("FORWARD")) {
            Serial.println("Sending: F");
            sendToArduino('F');
          } else if (command.startsWith("BACKWARD")) {
            Serial.println("Sending: B");
            sendToArduino('B');
          } else if (command.startsWith("LEFT")) {
            Serial.println("Sending: L");
            sendToArduino('L');
          } else if (command.startsWith("RIGHT")) {
            Serial.println("Sending: R");
            sendToArduino('R');
          } else if (command.startsWith("STOP")) {
            Serial.println("Sending: S");
            sendToArduino('S');
          }

          command = ""; // Clear the buffer
        }
      }
    }
    client.stop();
    Serial.println("Client disconnected.");
  }
}