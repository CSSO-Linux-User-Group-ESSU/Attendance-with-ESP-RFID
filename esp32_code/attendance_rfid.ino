#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <EEPROM.h>

WebServer server(80);

#define SS_PIN 5
#define RST_PIN 0

int bluePin = 2;
int redPin = 22;
int buzzerPin = 15;
int yellowPin = 13;

MFRC522 mfrc522(SS_PIN, RST_PIN);

String ssid;
String password;
String serverName;  // Your Django server endpoint
String deviceName;
String token1 = "fhdhjdkdsjcncjdhchdjdjdsjdw3@@!!#^^4682eqryoxuewrozcbvmalajurpd";


#define SSID_ADDR 0
#define PASSWORD_ADDR (SSID_ADDR + 64)
#define SERVERNAME_ADDR (PASSWORD_ADDR + 64)
#define DEVICENAME_ADDR (SERVERNAME_ADDR + 64)
#define EEPROM_SIZE 512

//sending ping
void handlePing() {
  server.send(200, "text/plain", "pong");
}

//for configuring the esp32
void handleConfig() {
  if (server.method() == HTTP_POST) {
    // Allocate a JSON document to store the incoming data
    DynamicJsonDocument doc(1024);

    // Parse the JSON body
    DeserializationError error = deserializeJson(doc, server.arg("plain"));

    if (error) {
      Serial.println("Failed to parse JSON");
      server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
      return;
    }



    // Extract the ssid and password from the parsed JSON
    String ssid = doc["ssid"];
    String password = doc["password"];
    serverName = doc["apiEndpointUrl"].as<String>();
    deviceName = doc["device_name"].as<String>();

    writeEEPROM(SSID_ADDR, ssid);
    writeEEPROM(PASSWORD_ADDR, password);
    writeEEPROM(SERVERNAME_ADDR, serverName);
    writeEEPROM(DEVICENAME_ADDR, deviceName);

    if (ssid.length() > 0 && password.length() > 0) {


      String ipAddress = WiFi.localIP().toString();
      String response = "{\"ip_address\":\"" + ipAddress + "\"}";
      server.send(200, "application/json", response);

      WiFi.begin(ssid.c_str(), password.c_str());


      Serial.print("Connecting to new WiFi credentials...");
      while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
      }

      // Successfully connected to new WiFi, send IP address back to Django
      Serial.println("\nNew WiFi connection established, IP Address: " + ipAddress);
      digitalWrite(bluePin, HIGH);
      tone(buzzerPin, 1000);
      delay(50);
      noTone(buzzerPin);
      tone(buzzerPin, 1000);
      delay(50);
      noTone(buzzerPin);
      tone(buzzerPin, 1000);
      delay(50);
      noTone(buzzerPin);
      tone(buzzerPin, 1000);
      delay(50);
      noTone(buzzerPin);
      delay(200);
      digitalWrite(bluePin, LOW);
      return;
    } else {
      server.send(400, "application/json", "{\"error\":\"Missing ssid or password\"}");
    }
  }
}

// Function to write String data to EEPROM
void writeEEPROM(int startAddr, String data) {
  int len = data.length();
  for (int i = 0; i < len; i++) {
    EEPROM.write(startAddr + i, data[i]);
  }
  EEPROM.write(startAddr + len, '\0');  // Null-terminate the string
  EEPROM.commit();  // Save changes to EEPROM
}

// Function to read String data from EEPROM
String readEEPROM(int startAddr) {
  String data = "";
  char c = EEPROM.read(startAddr);
  int i = 0;
  while (c != '\0' && i < 64) {  // Read until null-terminator or buffer size limit
    data += c;
    i++;
    c = EEPROM.read(startAddr + i);
  }
  return data;
}


void setup() {
  token1.trim();
  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  

  EEPROM.begin(EEPROM_SIZE);

  // Load saved WiFi credentials from EEPROM
  ssid = readEEPROM(SSID_ADDR);
  password = readEEPROM(PASSWORD_ADDR);
  serverName = readEEPROM(SERVERNAME_ADDR);
  deviceName = readEEPROM(DEVICENAME_ADDR);

  if (ssid.length() > 0 && password.length() > 0) {
    WiFi.begin(ssid.c_str(), password.c_str());
    int maxAttempts = 0;
    while (WiFi.status() != WL_CONNECTED && maxAttempts <= 15) {
      delay(500);
      Serial.println("Connecting to WiFi...");
      maxAttempts += 1;
    }
    if (WiFi.status() == WL_CONNECTED){
      Serial.println("Connected to WiFi, IP Address: " + WiFi.localIP().toString());
    }else{
      Serial.println("No saved WiFi credentials found. Enter them manually.");
      //Enter manually
      // initial WiFi credentials
      Serial.println("Enter SSID:");
      while (Serial.available() == 0) { }
      ssid = Serial.readString();
      ssid.trim();

      Serial.println("Enter Password:");
      while (Serial.available() == 0) { }
      password = Serial.readString();
      password.trim();
    }
    
  } else {
    Serial.println("No saved WiFi credentials found. Enter them manually.");
    //Enter manually
    // initial WiFi credentials
    Serial.println("Enter SSID:");
    while (Serial.available() == 0) { }
    ssid = Serial.readString();
    ssid.trim();

    Serial.println("Enter Password:");
    while (Serial.available() == 0) { }
    password = Serial.readString();
    password.trim();
  }

  // WiFi.begin(ssid.c_str(), password.c_str());

  // while (WiFi.status() != WL_CONNECTED) {
  //   delay(500);
  //   Serial.println("Connecting to WiFi...");
  // }

  Serial.println("Connected to WiFi, IP Address: " + WiFi.localIP().toString());
  digitalWrite(bluePin, HIGH);
  tone(buzzerPin, 1000);
  delay(50);
  noTone(buzzerPin);
  tone(buzzerPin, 1000);
  delay(50);
  noTone(buzzerPin);
  tone(buzzerPin, 1000);
  delay(50);
  noTone(buzzerPin);
  delay(200);
  digitalWrite(bluePin, LOW);

  server.on("/ping", HTTP_GET, handlePing);
  server.on("/config", HTTP_POST, handleConfig);
  server.begin();
}

void loop() {
  server.handleClient();  // Handle incoming client requests
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) return;

  // Reading the RFID card UID
  String cardUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    cardUID.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    cardUID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  cardUID.toUpperCase();
  Serial.println("Card UID: " + cardUID);

  if (WiFi.status() == WL_CONNECTED) {
    // Send the card UID to the Django server
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"card_uid\":\"" + cardUID + "\",\"device\":\"" + deviceName + "\",\"token\":\"" + token1 + "\"}";
    Serial.println("Sending JSON Payload: " + jsonPayload);
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Server Response Code: " + String(httpResponseCode));
      Serial.println("Server Response: " + response);
      
      if (httpResponseCode == 201) {
        digitalWrite(bluePin, HIGH);
        tone(buzzerPin, 1000);
        delay(100);
        noTone(buzzerPin);
        digitalWrite(bluePin, LOW);
      } else {
        digitalWrite(redPin, HIGH);
        tone(buzzerPin, 1000);
        delay(500);
        noTone(buzzerPin);
        digitalWrite(redPin, LOW);
      }
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
      digitalWrite(yellowPin, HIGH);
      tone(buzzerPin, 800);
      delay(300);
      noTone(buzzerPin);
      digitalWrite(yellowPin, LOW);
    }
    http.end();
  }
}
