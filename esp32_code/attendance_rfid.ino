#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <EEPROM.h>
#include <Wire.h>
#include <LiquidCrystal_PCF8574.h>

LiquidCrystal_PCF8574 lcd(0x3F);

#define SDA_CUSTOM 17
#define SCL_CUSTOM 16
#define SS_PIN 5
#define RST_PIN 0
#define SSID_ADDR 0
#define PASSWORD_ADDR (SSID_ADDR + 64)
#define SERVERNAME_ADDR (PASSWORD_ADDR + 64)
#define DEVICENAME_ADDR (SERVERNAME_ADDR + 64)
#define EEPROM_SIZE 512

int bluePin = 2;
int redPin = 22;
int buzzerPin = 15;
int yellowPin = 13;

String cardUID;
String ssid;
String password;
String serverName; // Your Django server endpoint
String deviceName;
String token1 = "fhdhjdkdsjcncjdhchdjdjdsjdw3@@!!#^^4682eqryoxuewrozcbvmalajurpd";

// HTML form for WiFi configuration
const char *htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
<head><title>WiFi Configuration</title></head>
<body>
  <h2>WiFi Configuration</h2>
  <form action="/save_config" method="POST">
    <label for="ssid">SSID:</label><br>
    <input type="text" id="ssid" name="ssid" required><br><br>
    <label for="password">Password:</label><br>
    <input type="password" id="password" name="password" required><br><br>
    <input type="submit" value="Save">
  </form>
</body>
</html>
)rawliteral";

MFRC522 mfrc522(SS_PIN, RST_PIN);
WebServer server(80);

// sending ping
// the django app periodically sends ping messages to
// know if the esp32 is still active
void handlePing()
{
  if (server.method() == HTTP_POST)
  {

    DynamicJsonDocument doc(1024);

    // Parse the JSON body
    DeserializationError error = deserializeJson(doc, server.arg("plain"));

    if (error)
    {
      Serial.println("Failed to parse JSON");
      server.send(400, "application/json", "{\"error\":\"Invalid JSON\"}");
      return;
    }
    String deviceName2 = doc["device_name"].as<String>();

    if (deviceName2 == deviceName)
      server.send(200, "text/plain", "pong");
      displayPing();
      delay(700);
      displayDevice();
  }
}

// when the django app wants to know the ip address
void sendIP()
{
  if (server.method() == HTTP_POST)
  {
    String ipAddress = WiFi.localIP().toString();
    String response = "{\"ip_address\":\"" + ipAddress + "\"}";
    server.send(200, "application/json", response);
  }
}


void displayDevice(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(deviceName);
  lcd.setCursor(0,1);
  lcd.print("Ready...");
}

void displayConnected(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Connected");
  lcd.setCursor(0,1);
  lcd.print("IP:"+ WiFi.localIP().toString());
}

void displayPing(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Ping");
  lcd.setCursor(0,1);
  lcd.print("Pong");
}

// for configuring the esp32
// saves the credentials to eeprom
void handleConfig()
{
  if (server.method() == HTTP_POST)
  {
    // Allocate a JSON document to store the incoming data
    DynamicJsonDocument doc(1024);

    // Parse the JSON body
    DeserializationError error = deserializeJson(doc, server.arg("plain"));

    if (error)
    {
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

    if (ssid.length() > 0 && password.length() > 0)
    {

      WiFi.begin(ssid.c_str(), password.c_str());

      Serial.print("Connecting to new WiFi credentials...");
      while (WiFi.status() != WL_CONNECTED)
      {
        delay(500);
        Serial.print(".");
      }

      String ipAddress = WiFi.localIP().toString();
      String response = "{\"ip_address\":\"" + ipAddress + "\"}";
      server.send(200, "application/json", response);

      // Successfully connected to new WiFi, send IP address back to Django
      Serial.println("\nNew WiFi connection established, IP Address: " + ipAddress);
      
      displayDevice();

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
    }
    else
    {
      server.send(400, "application/json", "{\"error\":\"Missing ssid or password\"}");
    }
  }
}

void get_card_uid()
{
  cardUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++)
  {
    cardUID.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    cardUID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  cardUID.toUpperCase();
  server.send(200, "text/plain", cardUID);
}

void writeEEPROM(int startAddr, String data)
{
  int len = data.length();
  for (int i = 0; i < len; i++)
  {
    EEPROM.write(startAddr + i, data[i]);
  }
  EEPROM.write(startAddr + len, '\0');
  EEPROM.commit();
}

String readEEPROM(int startAddr)
{
  String data = "";
  char c = EEPROM.read(startAddr);
  int i = 0;
  while (c != '\0' && i < 64)
  {
    data += c;
    i++;
    c = EEPROM.read(startAddr + i);
  }
  return data;
}

void setupAccessPoint()
{
  Serial.println("No Saved Credentials, Starting Access Point");
  WiFi.softAP("ESP32_Config", "12345678");

  IPAddress IP = WiFi.softAPIP();
  Serial.println("SSID:ESP32_Config");
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.on("/", handleRoot);
  server.on("/save_config", HTTP_POST, saveWiFiConfig);
  server.begin();
}

void handleRoot()
{
  server.send(200, "text/html", htmlPage);
}

void saveWiFiConfig()
{
  if (server.method() == HTTP_POST)
  {
    if (server.hasArg("ssid") && server.hasArg("password"))
    {
      ssid = server.arg("ssid");
      password = server.arg("password");

      writeEEPROM(SSID_ADDR, ssid);
      writeEEPROM(PASSWORD_ADDR, password);
      writeEEPROM(DEVICENAME_ADDR,"");

      server.send(200, "text/html", "<h2>Configuration Saved. Rebooting...</h2>");
      digitalWrite(yellowPin,LOW);
      delay(1000);
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Rebooting...");
      delay(900);
      lcd.clear();
      ESP.restart();
    }
    else
    {
      server.send(400, "text/html", "<h2>Error: Missing SSID or Password</h2>");
    }
  }
}

void setup()
{
  Wire.begin(SDA_CUSTOM,SCL_CUSTOM);
  lcd.begin(16, 2);
  lcd.setBacklight(255);
  token1.trim();
  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  EEPROM.begin(EEPROM_SIZE);

  lcd.setCursor(0, 0);
  lcd.print("Starting device");
  delay(1000);
  lcd.clear();

  // Load saved WiFi credentials from EEPROM
  ssid = readEEPROM(SSID_ADDR);
  password = readEEPROM(PASSWORD_ADDR);
  serverName = readEEPROM(SERVERNAME_ADDR);
  deviceName = readEEPROM(DEVICENAME_ADDR);

  WiFi.begin(ssid.c_str(), password.c_str());
  int maxAttempts = 0;
  while (WiFi.status() != WL_CONNECTED && maxAttempts <= 15)
  {
    delay(500);
    Serial.println("Connecting to WiFi...");
    lcd.setCursor(0, 0);
    lcd.print("Connecting...");
    maxAttempts += 1;
  }
  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("Connected to WiFi, IP Address: " + WiFi.localIP().toString());
    displayConnected();
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

    server.on("/ping", HTTP_POST, handlePing);
    server.on("/config", HTTP_POST, handleConfig);
    server.on("/send_ip", HTTP_POST, sendIP);
    server.on("/get_card_uid", HTTP_GET, get_card_uid);
    server.begin();

    delay(1000);
    if(deviceName.c_str()!=""){ displayDevice();}
   
  }
  else
  {
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("AP Mode");
    lcd.setCursor(0,1);
    lcd.print("IP:192.168.4.1");
    setupAccessPoint();
    digitalWrite(yellowPin, HIGH);
  }
}

void loop()
{
  server.handleClient(); // Handle incoming client requests

  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial())
  {
    return;
  }

  // Reading the RFID card UID
  cardUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++)
  {
    cardUID.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    cardUID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  cardUID.toUpperCase();
  Serial.println("Card UID: " + cardUID);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Scanned");
  lcd.setCursor(0,1);
  lcd.print(cardUID);
  delay(500);
  displayDevice();

  if (WiFi.status() == WL_CONNECTED)
  {
    // Send the card UID to the Django server
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"card_uid\":\"" + cardUID + "\",\"device\":\"" + deviceName + "\",\"token\":\"" + token1 + "\"}";
    Serial.println("Sending JSON Payload: " + jsonPayload);
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0)
    {
      String response = http.getString();
      Serial.println("Server Response Code: " + String(httpResponseCode));
      Serial.println("Server Response: " + response);

      if (httpResponseCode == 201)
      {
        digitalWrite(bluePin, HIGH);
        tone(buzzerPin, 1000);
        delay(100);
        noTone(buzzerPin);
        digitalWrite(bluePin, LOW);
      }
      else
      {
        digitalWrite(redPin, HIGH);
        tone(buzzerPin, 1000);
        delay(500);
        noTone(buzzerPin);
        digitalWrite(redPin, LOW);
      }
    }
    else
    {
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
