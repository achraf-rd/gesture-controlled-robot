#include "esp_wpa2.h" // Include WPA2 Enterprise support
#include <WiFi.h>

#define WIFI_SSID ""           // Replace with your network SSID
#define WIFI_USER "" // Replace with your username
#define WIFI_PASS ""       // Replace with your password
#define AP_SSID "think"                   // Access Point SSID
#define AP_PASSWORD "esp222888"           // Access Point Password

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
                                     strlen(WIFI_USER)); // Set username
  esp_wifi_sta_wpa2_ent_set_username(
      (uint8_t *)WIFI_USER,
      strlen(WIFI_USER)); // Set username (again for compatibility)
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

  // Once connected, print the IP address
  Serial.println("\nConnected to WPA2 Enterprise Wi-Fi!");
  Serial.print("Connected IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Print connection status
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("ESP32 is still connected to Wi-Fi.");

    // Get and print the signal strength (RSSI)
    int32_t rssi = WiFi.RSSI(); // Get the signal strength
    Serial.print("Signal Strength (RSSI): ");
    Serial.print(rssi);
    Serial.println(" dBm");
  } else {
    Serial.println("ESP32 disconnected!");
  }

  delay(5000); // Wait for 5 seconds before checking again
}
