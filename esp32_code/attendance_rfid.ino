#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <Arduino_JSON.h>

#define SS_PIN 5
#define RST_PIN 0

int bluePin = 2;
int redPin = 22;
int buzzerPin = 15;
int yellowPin = 13;

MFRC522 mfrc522(SS_PIN, RST_PIN);

String ssid;;
String password;
// const char* ssid = "Montes_family_EXT";
// const char* password = "0123456789";
// const char* serverName = "http://192.168.1.104:8000/api/";
String serverName;
String deviceName;


void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  Serial.begin(115200);
  SPI.begin();
  mfrc522.PCD_Init();

  Serial.println("Enter DeviceName:");
  while(Serial.available()==0){

  }

  
  deviceName = Serial.readString();
  deviceName.trim();

  Serial.println("Enter SSID:");
  while(Serial.available()==0){

  }

  
  ssid = Serial.readString();
  ssid.trim();

  Serial.println("Enter Password:");
  while(Serial.available()==0){

  }

  
  password = Serial.readString();
  password.trim();

  Serial.println("Enter url:");
  while(Serial.available()==0){

  }

  
  serverName = Serial.readString();
  serverName.trim();

  Serial.println("SSID:"+ssid);
  Serial.println("Password:"+password);
  Serial.println("Url:"+serverName);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(800);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
  digitalWrite(bluePin,HIGH);
  tone(buzzerPin,1000);
  delay(50);
  noTone(buzzerPin);
  tone(buzzerPin,1000);
  delay(50);
  noTone(buzzerPin);
  tone(buzzerPin,1000);
  delay(50);
  noTone(buzzerPin);
  delay(200);
  digitalWrite(bluePin,LOW);
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
    // getINFO();
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{\"card_uid\":\"" + cardUID + "\",\"device\":\""+deviceName+"\"}";
    Serial.println("JsonPayload:"+jsonPayload);
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
      Serial.println("Server may be down.");
      digitalWrite(yellowPin, HIGH);
      tone(buzzerPin,800);
      delay(300);
      noTone(buzzerPin);
      tone(buzzerPin,800);
      delay(300);
      noTone(buzzerPin);
      digitalWrite(yellowPin, LOW);
    }
    http.end();
    
  }
}
