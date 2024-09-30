#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 5
#define RST_PIN 0

int bluePin = 2;
int redPin = 22;
int buzzerPin = 15;

MFRC522 mfrc522(SS_PIN, RST_PIN);

// const char* ssid = "ITLAB-CSSO-Officers-Network";
// const char* password = "1234567890";
const char* ssid = "Montes_family_EXT";
const char* password = "0123456789";
const char* serverName = "http://192.168.1.104:8000/api/";

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(800);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial())
    return;

  String cardUID = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    cardUID.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? "0" : ""));
    cardUID.concat(String(mfrc522.uid.uidByte[i], HEX));
  }

  cardUID.toUpperCase();
  Serial.println("Card UID: " + cardUID);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"card_uid\":\"" + cardUID + "\"}";
    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(httpResponseCode);
      Serial.println(response);
      if(httpResponseCode==201){
        digitalWrite(bluePin, HIGH);
        tone(buzzerPin,1000);
        delay(100);
        tone(buzzerPin,1000);
        noTone(buzzerPin);
        delay(500);
        digitalWrite(bluePin, LOW);
        
      }else{
        digitalWrite(redPin, HIGH);
        tone(buzzerPin,1000);
        delay(500);
        noTone(buzzerPin);
        digitalWrite(redPin, LOW);
      }
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  }

  delay(3000);  // Delay to avoid multiple scans for the same card
}
