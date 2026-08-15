## Group 52 IoT Monitoring System

Real-time IoT sensor monitoring project based on the EE 288 Lab 5 and Lab 6 work.

## What it does

The ESP32 collects temperature, humidity, light intensity and ultrasonic distance data. It serializes the readings as JSON and publishes them over MQTT. The Python Dash application subscribes to the MQTT topic and displays four live Plotly graphs plus a recent telemetry table.

## Structure

```text
Bit-By-Bit-IoT-Monitoring/
├── README.md
├── .gitignore
├── esp32/
│   └── telemetry_publisher/
│       └── telemetry_publisher.ino
└── dashboard/
    ├── app.py
    └── requirements.txt
```

## Hardware

- ESP32
- DHT11
- LDR
- HC-SR04

GPIO assignments from the report:

- DHT11: GPIO 4
- LDR: GPIO 34
- HC-SR04 Trigger: GPIO 5
- HC-SR04 Echo: GPIO 18

## MQTT

The project uses:

```text
esp32/group52/data
```

Set the same MQTT broker address in both the ESP32 firmware and `dashboard/app.py`.

**Never commit real Wi-Fi passwords or other secrets to GitHub.**

## ESP32

Open:

```text
esp32/telemetry_publisher/telemetry_publisher.ino
```

Install the Arduino libraries used by the report:

- PubSubClient
- ArduinoJson
- DHT sensor library

Set your own:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "YOUR_MQTT_BROKER_IP";
```

Upload the sketch and open Serial Monitor at 115200 baud.

## Python dashboard

From the `dashboard` folder:

```bash
python -m pip install -r requirements.txt
python app.py
```



The dashboard refreshes every 2 seconds and retains the most recent 15 records.

