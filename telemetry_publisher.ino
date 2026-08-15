#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <ArduinoJson.h>


#define DHTPIN 4
#define DHTTYPE DHT22

#define LDR_PIN 5

#define TRIG_PIN 12
#define ECHO_PIN 14

DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "Galaxy A16 0CF6";
const char* password = "77-Genius";

const char* mqtt_server = "broker.hivemq.com";
const int mqtt_port = 1883;
const char* mqtt_topic = "lab4/sensor";

WiFiClient espClient;
PubSubClient client(espClient);


void setup_wifi() {

  delay(100);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");

    attempts++;

    if (attempts >= 20) {

      Serial.println();
      Serial.println("WiFi connection failed.");

      return;
    }
  }

  Serial.println();
  Serial.println("WiFi Connected!");

  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {

  while (!client.connected()) {

    Serial.print("Connecting to MQTT...");

    String clientId = "ESP32-Lab4-";
    clientId += String(random(0xffff), HEX);

    if (client.connect(clientId.c_str())) {

      Serial.println("Connected!");

    } else {

      Serial.print("Failed, rc=");
      Serial.print(client.state());

      Serial.println(" - retrying in 2 seconds");

      delay(2000);
    }
  }
}



float readDistanceCM() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);

  if (duration == 0) {
    return -1;
  }

  return duration * 0.0343 / 2;
}


void setup() {

  Serial.begin(9600);

  dht.begin();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LDR_PIN, INPUT);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
}



void loop() {

  if (!client.connected()) {
    reconnect();
  }

  client.loop();



  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  int light = digitalRead(LDR_PIN);

  float distance = readDistanceCM();


  if (isnan(temperature) || isnan(humidity)) {

    Serial.println("DHT22 read failed.");

    delay(5000);

    return;
  }



  StaticJsonDocument<200> doc;

  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["light"] = light;
  doc["distance"] = distance;


  char buffer[256];

  serializeJson(doc, buffer);



  bool success = client.publish(mqtt_topic, buffer);


  if (success) {

    Serial.println("Published:");
    Serial.println(buffer);

  } else {

    Serial.println("MQTT publish failed.");

  }


  delay(5000);
}
