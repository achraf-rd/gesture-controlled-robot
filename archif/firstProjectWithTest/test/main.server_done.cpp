#include "esp_wpa2.h" // Include WPA2 Enterprise support
#include <WiFi.h>

#define WIFI_SSID ""           // Replace with your network SSID
#define WIFI_USER "" // Replace with your username
#define WIFI_PASS ""       // Replace with your password

WiFiServer wifiServer(80); // Create a WiFi server on port 80

void setup() {
  // Initialize Serial Monitor
  Serial.begin(115200);
  delay(1000);

  // Disconnect from any previously connected Wi-Fi
  WiFi.disconnect(true);

  // Set Wi-Fi mode to station mode
  WiFi.mode(WIFI_STA);
  Serial.println("Starting connection to WPA2 Enterprise Wi-Fi...");

  // WPA2 Enterprise configuration: Set username and password
  esp_wifi_sta_wpa2_ent_set_identity((uint8_t *)WIFI_USER,
                                     strlen(WIFI_USER)); // Set identity
  esp_wifi_sta_wpa2_ent_set_username((uint8_t *)WIFI_USER,
                                     strlen(WIFI_USER)); // Set username
  esp_wifi_sta_wpa2_ent_set_password((uint8_t *)WIFI_PASS,
                                     strlen(WIFI_PASS)); // Set password

  // Enable WPA2 Enterprise
  esp_wifi_sta_wpa2_ent_enable();

  // Connect to Wi-Fi network
  WiFi.begin(WIFI_SSID);

  // Wait for Wi-Fi connection
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  // Print connection success and IP address
  Serial.println("\nConnected to WPA2 Enterprise Wi-Fi!");
  Serial.print("Connected IP Address: ");
  Serial.println(WiFi.localIP());

  // Start the Wi-Fi server
  wifiServer.begin();
  Serial.println("WiFi Server started.");
}

void loop() {
  // Check for client connections
  WiFiClient client = wifiServer.available();
  if (client) {
    Serial.println("Client connected!");

    // Variable to store the received command
    String command = "";

    // Read data from the client
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        command += c;

        // Check for end of command (newline character)
        if (c == '\n') {
          Serial.print("Received Command: ");
          Serial.println(command);

          // Handle commands
          if (command.startsWith("FORWARD")) {
            Serial.println("Moving forward...");
            
          } else if (command.startsWith("BACKWARD")) {
            Serial.println("Moving backward...");
          } else if (command.startsWith("LEFT")) {
            Serial.println("Turning left...");
          } else if (command.startsWith("RIGHT")) {
            Serial.println("Turning right...");
          }

          // Clear the command buffer
          command = "";
        }
      }
    }

    // Disconnect the client after processing the command
    client.stop();
    Serial.println("Client disconnected.");
  }
}
