#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include <DHT.h>

#include <TinyGPS++.h>
#include <HardwareSerial.h>

#include <WiFi.h>
#include <WebServer.h>

#include <ESP32Servo.h>


// ============================================================
// WIFI
// ============================================================

const char* ssid = "phone1";
const char* password = "12345678";
volatile bool wifiDisconnected = false;
unsigned long wifiReconnectTime = 0;
WebServer server(80);


// ============================================================
// OLED
// ============================================================

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

Adafruit_SSD1306 display(
  SCREEN_WIDTH,
  SCREEN_HEIGHT,
  &Wire,
  -1
);


// ============================================================
// MOTORS
// ============================================================

#define IN1 26
#define IN2 27

#define IN3 14
#define IN4 12


// ============================================================
// DHT11
// ============================================================

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(
  DHTPIN,
  DHTTYPE
);


// ============================================================
// SOIL & LDR
// ============================================================

#define SOIL_PIN 34
#define LDR_PIN 35

const int SOIL_THRESHOLD = 3000;


// ============================================================
// PUMP
// ============================================================

#define RELAY_PIN 33

bool pumpOn = false;
bool relayActiveLow = true;


// ============================================================
// ULTRASONIC
// ============================================================

#define TRIG -1
#define ECHO -1

float distance = 0;

const float OBSTACLE_DISTANCE = 20.0;

bool obstacleDetected = false;


// ============================================================
// LINE SENSORS
// ============================================================

#define LS 18
#define CS 19
#define RS 5


// ============================================================
// GPS
// ============================================================

TinyGPSPlus gps;

HardwareSerial gpsSerial(2);

#define GPS_RX 16
#define GPS_TX 17

#define GPS_BAUD 9600


// ============================================================
// PAN TILT
// ============================================================

#define PAN_PIN 13
#define TILT_PIN 25

Servo panServo;
Servo tiltServo;


const int PAN_MIN = 30;
const int PAN_MAX = 150;

const int TILT_MIN = 20;
const int TILT_MAX = 160;


const int SERVO_STEP = 5;


int panAngle = 90;
int tiltAngle = 90;


int targetPan = 90;
int targetTilt = 90;


unsigned long lastServoMove = 0;

const unsigned long SERVO_INTERVAL = 20;


// ============================================================
// CAMERA SCAN
// ============================================================

bool scanMode = false;

int scanDirection = 1;


unsigned long lastScanMove = 0;

const unsigned long SCAN_INTERVAL = 60;

const int SCAN_STEP = 2;


// ============================================================
// DRIVE MODE
// ============================================================

bool manualMode = true;


// ============================================================
// SENSOR CACHE
// ============================================================

unsigned long lastSensorUpdate = 0;

const unsigned long SENSOR_INTERVAL = 100;


float cachedTemperature = 0.0;

float cachedHumidity = 0.0;

int cachedSoil = 0;


unsigned long lastDHTRead = 0;

const unsigned long DHT_INTERVAL = 2000;


// ============================================================
// OLED UPDATE
// ============================================================

unsigned long lastOLEDUpdate = 0;

const unsigned long OLED_INTERVAL = 1000;


// ============================================================
// MOTORS
// ============================================================

unsigned long lastDriveTime = 0;
bool isDriving = false;
const unsigned long DRIVE_WATCHDOG_MS = 600; // Auto-stop failsafe if no keepalive within 600ms

void forward() {
  if (obstacleDetected) {
    stopMotor();
    return;
  }
  lastDriveTime = millis();
  isDriving = true;
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void left() {
  if (obstacleDetected) {
    stopMotor();
    return;
  }
  lastDriveTime = millis();
  isDriving = true;
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void right() {
  if (obstacleDetected) {
    stopMotor();
    return;
  }
  lastDriveTime = millis();
  isDriving = true;
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void stopMotor() {
  isDriving = false;
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void backward() {
  if (obstacleDetected) {
    stopMotor();
    return;
  }
  lastDriveTime = millis();
  isDriving = true;
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}


// ============================================================
// PUMP
// ============================================================

void pumpON() {

  digitalWrite(
    RELAY_PIN,
    relayActiveLow ? LOW : HIGH
  );

  pumpOn = true;

}


void pumpOFF() {

  digitalWrite(
    RELAY_PIN,
    relayActiveLow ? HIGH : LOW
  );

  pumpOn = false;

}
// ============================================================
// PUMP WEB CONTROL
// ============================================================

void handlePumpOn() {

  pumpON();

  server.send(
    200,
    "text/plain",
    "PUMP ON"
  );

}


void handlePumpOff() {

  pumpOFF();

  server.send(
    200,
    "text/plain",
    "PUMP OFF"
  );

}

void handlePumpInvert() {
  relayActiveLow = !relayActiveLow;
  pumpOFF();
  server.send(
    200,
    "text/plain",
    relayActiveLow ? "RELAY: ACTIVE LOW" : "RELAY: ACTIVE HIGH"
  );
}


// ============================================================
// ULTRASONIC
// ============================================================

void updateDistance() {

  if (TRIG < 0 || ECHO < 0) {
    distance = 0;
    obstacleDetected = false;
    return;
  }

  digitalWrite(
    TRIG,
    LOW
  );

  delayMicroseconds(2);


  digitalWrite(
    TRIG,
    HIGH
  );

  delayMicroseconds(10);


  digitalWrite(
    TRIG,
    LOW
  );


  long duration = pulseIn(
    ECHO,
    HIGH,
    10000
  );


  if (duration == 0) {

    distance = 0;

    obstacleDetected = false;

  }

  else {

    distance =
      duration * 0.0343 / 2.0;


    if (
      distance > 0 &&
      distance < OBSTACLE_DISTANCE
    ) {

      obstacleDetected = true;

      stopMotor();

    }

    else {

      obstacleDetected = false;

    }

  }

}


// ============================================================
// SENSOR CACHE
// ============================================================

void updateSensorCache() {

  unsigned long now =
    millis();


  if (
    now - lastDHTRead >=
    DHT_INTERVAL
  ) {

    lastDHTRead = now;


    float temp =
      dht.readTemperature();


    float hum =
      dht.readHumidity();


    if (!isnan(temp)) {

      cachedTemperature =
        temp;

    }


    if (!isnan(hum)) {

      cachedHumidity =
        hum;

    }

  }


  cachedSoil =
    analogRead(
      SOIL_PIN
    );


  updateDistance();

}


// ============================================================
// SERVO
// ============================================================

void updateServos() {

  unsigned long now =
    millis();


  // ----------------------------------------------------------
  // SCAN
  // ----------------------------------------------------------

  if (
    scanMode &&
    now - lastScanMove >=
    SCAN_INTERVAL
  ) {

    lastScanMove = now;


    targetPan +=
      scanDirection *
      SCAN_STEP;


    if (
      targetPan >=
      PAN_MAX
    ) {

      targetPan =
        PAN_MAX;

      scanDirection =
        -1;

    }


    if (
      targetPan <=
      PAN_MIN
    ) {

      targetPan =
        PAN_MIN;

      scanDirection =
        1;

    }

  }


  // ----------------------------------------------------------
  // SMOOTH MOVEMENT
  // ----------------------------------------------------------

  if (
    now - lastServoMove <
    SERVO_INTERVAL
  ) {

    return;

  }


  lastServoMove =
    now;


  if (
    panAngle <
    targetPan
  ) {

    panAngle++;

  }

  else if (
    panAngle >
    targetPan
  ) {

    panAngle--;

  }


  if (
    tiltAngle <
    targetTilt
  ) {

    tiltAngle++;

  }

  else if (
    tiltAngle >
    targetTilt
  ) {

    tiltAngle--;

  }


  panServo.write(
    panAngle
  );

  tiltServo.write(
    tiltAngle
  );

}


// ============================================================
// GPS
// ============================================================

void updateGPS() {

  int count = 0;
  while (
    gpsSerial.available() && count++ < 100
  ) {

    gps.encode(
      gpsSerial.read()
    );

  }

}


// ============================================================
// AUTONOMOUS NAVIGATION
// ============================================================

void autonomousNavigation() {

  if (obstacleDetected) {

    stopMotor();

    return;

  }


  int L =
    digitalRead(LS);


  int C =
    digitalRead(CS);


  int R =
    digitalRead(RS);


  // Center

  if (
    L == 0 &&
    C == 1 &&
    R == 0
  ) {

    forward();

  }


  // Left

  else if (
    L == 1 &&
    C == 0
  ) {

    left();

  }


  // Right

  else if (
    R == 1 &&
    C == 0
  ) {

    right();

  }


  else {

    stopMotor();

  }

}


// ============================================================
// OLED
// ============================================================

void updateOLED() {

  unsigned long now =
    millis();


  if (
    now - lastOLEDUpdate <
    OLED_INTERVAL
  ) {

    return;

  }


  lastOLEDUpdate =
    now;


  display.clearDisplay();


  display.setTextColor(
    WHITE
  );


  display.setTextSize(1);


  display.setCursor(
    0,
    0
  );

  display.print(
    "AGRI-VISE"
  );


  display.setCursor(
    75,
    0
  );


  if (
    WiFi.status() ==
    WL_CONNECTED
  ) {

    display.print(
      "WiFi"
    );

  }

  else {

    display.print(
      "OFF"
    );

  }


  // Temperature

  display.setCursor(
    0,
    14
  );

  display.print(
    "T:"
  );

  display.print(
    cachedTemperature,
    1
  );

  display.print(
    "C"
  );


  // Humidity

  display.setCursor(
    65,
    14
  );

  display.print(
    "H:"
  );

  display.print(
    cachedHumidity,
    0
  );

  display.print(
    "%"
  );


  // Soil

  display.setCursor(
    0,
    28
  );

  display.print(
    "Soil:"
  );

  display.print(
    cachedSoil
  );


  // Distance

  display.setCursor(
    65,
    28
  );

  display.print(
    "D:"
  );

  display.print(
    distance,
    0
  );

  display.print(
    "cm"
  );


  // Mode

  display.setCursor(
    0,
    42
  );

  display.print(
    "Mode:"
  );


  if (manualMode) {

    display.print(
      "MANUAL"
    );

  }

  else {

    display.print(
      "AUTO"
    );

  }


  // GPS

  display.setCursor(
    70,
    42
  );


  if (
    gps.location.isValid()
  ) {

    display.print(
      "GPS OK"
    );

  }

  else {

    display.print(
      "GPS --"
    );

  }


  // Pump

  display.setCursor(
    0,
    56
  );

  display.print(
    "Pump:"
  );


  if (pumpOn) {

    display.print(
      "ON"
    );

  }

  else {

    display.print(
      "OFF"
    );

  }


  display.display();

}


// ============================================================
// DATA
// ============================================================

void handleData() {


  String modeState;


  if (manualMode) {

    modeState =
      "MANUAL";

  }

  else {

    modeState =
      "AUTO";

  }


  String pumpState;


  if (pumpOn) {

    pumpState =
      "ON";

  }

  else {

    pumpState =
      "OFF";

  }


  String json = "{";


  json +=
    "\"temperature\":";

  json +=
    String(
      cachedTemperature,
      1
    );

  json += ",";


  json +=
    "\"humidity\":";

  json +=
    String(
      cachedHumidity,
      1
    );

  json += ",";


  json +=
    "\"soil\":";

  json +=
    String(
      cachedSoil
    );

  json += ",";


  json +=
    "\"distance\":";

  json +=
    String(
      distance,
      1
    );

  json += ",";


  json +=
    "\"pump\":\"";

  json +=
    pumpState;

  json += "\",";


  json +=
    "\"mode\":\"";

  json +=
    modeState;

  json += "\",";


  json +=
    "\"pan\":";

  json +=
    String(
      panAngle
    );

  json += ",";


  json +=
    "\"tilt\":";

  json +=
    String(
      tiltAngle
    );

  json +=
    ",\"probeAngle\":";

  json +=
    String(
      tiltAngle
    );


  // GPS

  if (
    gps.location.isValid()
  ) {

    json +=
      ",\"lat\":";

    json +=
      String(
        gps.location.lat(),
        6
      );


    json +=
      ",\"lon\":";

    json +=
      String(
        gps.location.lng(),
        6
      );

  }


  json += "}";


  server.send(
    200,
    "application/json",
    json
  );

}


// ============================================================
// ROOT
// ============================================================

void handleRoot() {

  server.send(
    200,
    "text/plain",
    "AGRI-VISE ESP32 Web Server Working"
  );

}


// ============================================================
// FORWARD
// ============================================================

void handleForward() {

  manualMode = true;


  if (obstacleDetected) {

    stopMotor();


    server.send(
      200,
      "text/plain",
      "BLOCKED - OBSTACLE"
    );


    return;

  }


  forward();


  server.send(
    200,
    "text/plain",
    "FORWARD"
  );

}


// ============================================================
// LEFT
// ============================================================

void handleLeft() {

  manualMode = true;


  if (obstacleDetected) {

    stopMotor();


    server.send(
      200,
      "text/plain",
      "BLOCKED - OBSTACLE"
    );


    return;

  }


  left();


  server.send(
    200,
    "text/plain",
    "LEFT"
  );

}


// ============================================================
// RIGHT
// ============================================================

void handleRight() {

  manualMode = true;


  if (obstacleDetected) {

    stopMotor();


    server.send(
      200,
      "text/plain",
      "BLOCKED - OBSTACLE"
    );


    return;

  }


  right();


  server.send(
    200,
    "text/plain",
    "RIGHT"
  );

}


void handleBackward() {
  manualMode = true;
  backward();
  server.send(200, "text/plain", "BACKWARD");
}


// ============================================================
// STOP
// ============================================================

void handleStop() {

  stopMotor();


  server.send(
    200,
    "text/plain",
    "STOP"
  );

}


// ============================================================
// AUTO
// ============================================================

void handleAuto() {

  manualMode = false;

  stopMotor();


  server.send(
    200,
    "text/plain",
    "AUTO MODE"
  );

}


// ============================================================
// MANUAL
// ============================================================

void handleManual() {

  manualMode = true;

  stopMotor();


  server.send(
    200,
    "text/plain",
    "MANUAL MODE"
  );

}


// ============================================================
// PAN LEFT
// ============================================================

void handlePanLeft() {

  scanMode = false;


  targetPan =
    constrain(
      targetPan - SERVO_STEP,
      PAN_MIN,
      PAN_MAX
    );


  server.send(
    200,
    "text/plain",
    "PAN LEFT"
  );

}


// ============================================================
// PAN RIGHT
// ============================================================

void handlePanRight() {

  scanMode = false;


  targetPan =
    constrain(
      targetPan + SERVO_STEP,
      PAN_MIN,
      PAN_MAX
    );


  server.send(
    200,
    "text/plain",
    "PAN RIGHT"
  );

}


// ============================================================
// TILT UP
// ============================================================

void handleTiltUp() {

  scanMode = false;


  targetTilt =
    constrain(
      targetTilt + SERVO_STEP,
      TILT_MIN,
      TILT_MAX
    );


  server.send(
    200,
    "text/plain",
    "TILT UP"
  );

}


// ============================================================
// TILT DOWN
// ============================================================

void handleTiltDown() {

  scanMode = false;


  targetTilt =
    constrain(
      targetTilt - SERVO_STEP,
      TILT_MIN,
      TILT_MAX
    );


  server.send(
    200,
    "text/plain",
    "TILT DOWN"
  );

}


// ============================================================
// CENTER
// ============================================================

void handleCenter() {

  scanMode = false;


  targetPan = 90;

  targetTilt = 90;


  server.send(
    200,
    "text/plain",
    "CENTER"
  );

}


// ============================================================
// SOIL PROBE SERVO HANDLERS (GPIO 25)
// ============================================================

void handleProbeRetract() {
  scanMode = false;
  targetTilt = 55;
  server.send(200, "text/plain", "PROBE RETRACTED (55 deg)");
}

void handleProbeDeploy() {
  scanMode = false;
  targetTilt = 135;
  server.send(200, "text/plain", "PROBE DEPLOYED (135 deg)");
}

void handleProbeAngle() {
  scanMode = false;
  if (server.hasArg("val")) {
    int val = server.arg("val").toInt();
    targetTilt = constrain(val, TILT_MIN, TILT_MAX);
    server.send(200, "text/plain", String("PROBE ANGLE SET TO ") + targetTilt);
    return;
  }
  server.send(400, "text/plain", "Missing val param");
}

void handleServoUp() {
  handleTiltUp();
}

void handleServoDown() {
  handleTiltDown();
}



// ============================================================
// SCAN
// ============================================================

void handleScan() {

  scanMode =
    !scanMode;


  if (scanMode) {

    scanDirection = 1;

    lastScanMove =
      millis();


    server.send(
      200,
      "text/plain",
      "SCAN ON"
    );

  }

  else {

    server.send(
      200,
      "text/plain",
      "SCAN OFF"
    );

  }

}


// ============================================================
// WIFI
// ============================================================

void connectWiFi() {

  Serial.println();

  Serial.println(
    "Connecting to WiFi..."
  );


  WiFi.mode(
    WIFI_STA
  );

  WiFi.setAutoReconnect(true);
  WiFi.begin(
    ssid,
    password
  );


  unsigned long startTime =
    millis();


  while (

    WiFi.status() !=
    WL_CONNECTED

    &&

    millis() - startTime <
    20000

  ) {

    delay(500);

    Serial.print(
      "."
    );

  }


  Serial.println();


  if (
    WiFi.status() ==
    WL_CONNECTED
  ) {

    Serial.println(
      "WiFi connected"
    );


    Serial.print(
      "ESP32 IP: "
    );


    Serial.println(
      WiFi.localIP()
    );

  }

  else {

    Serial.println(
      "WiFi connection failed to 'phone1'. Starting AP hotspot 'AGRO-ROVER'..."
    );
    WiFi.disconnect(true);
    delay(100);
    WiFi.mode(WIFI_AP);
    IPAddress apIP(192, 168, 4, 1);
    IPAddress netMsk(255, 255, 255, 0);
    WiFi.softAPConfig(apIP, apIP, netMsk);
    WiFi.softAP("AGRO-ROVER", "12345678", 1, 0, 4);
    Serial.print("Access Point started! AP IP: ");
    Serial.println(WiFi.softAPIP());

  }

}

void WiFiEvent(WiFiEvent_t event, WiFiEventInfo_t info) {

  if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED) {

    Serial.print("WiFi disconnected. Reason: ");
    Serial.println(info.wifi_sta_disconnected.reason);

    wifiDisconnected = true;
    wifiReconnectTime = millis() + 20000;
  }

  else if (event == ARDUINO_EVENT_WIFI_STA_GOT_IP) {

    Serial.println("WiFi reconnected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    wifiDisconnected = false;
  }
}
// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(
    115200
  );


  delay(500);


  // ----------------------------------------------------------
  // MOTORS
  // ----------------------------------------------------------

  pinMode(
    IN1,
    OUTPUT
  );

  pinMode(
    IN2,
    OUTPUT
  );

  pinMode(
    IN3,
    OUTPUT
  );

  pinMode(
    IN4,
    OUTPUT
  );


  stopMotor();


  // ----------------------------------------------------------
  // LINE SENSORS
  // ----------------------------------------------------------

  pinMode(
    LS,
    INPUT
  );

  pinMode(
    CS,
    INPUT
  );

  pinMode(
    RS,
    INPUT
  );


  // ----------------------------------------------------------
  // ULTRASONIC
  // ----------------------------------------------------------

  if (TRIG >= 0 && ECHO >= 0) {
    pinMode(
      TRIG,
      OUTPUT
    );

    pinMode(
      ECHO,
      INPUT
    );

    digitalWrite(
      TRIG,
      LOW
    );
  }


  // ----------------------------------------------------------
  // SOIL
  // ----------------------------------------------------------

  pinMode(
    SOIL_PIN,
    INPUT
  );

  pinMode(
    LDR_PIN,
    INPUT
  );


  // ----------------------------------------------------------
  // RELAY
  // ----------------------------------------------------------

  pinMode(
    RELAY_PIN,
    OUTPUT
  );


  pumpOFF();


  // ----------------------------------------------------------
  // DHT
  // ----------------------------------------------------------

  pinMode(DHTPIN, INPUT_PULLUP);
  dht.begin();


  // ----------------------------------------------------------
  // OLED I2C
  // ----------------------------------------------------------

  Wire.begin(
    21,
    22
  );


  if (
    !display.begin(
      SSD1306_SWITCHCAPVCC,
      0x3C
    )
  ) {

    Serial.println(
      "OLED initialization failed"
    );

  }

  else {

    display.clearDisplay();

    display.setTextColor(
      WHITE
    );

    display.setTextSize(2);

    display.setCursor(
      10,
      20
    );

    display.println(
      "ROVER"
    );

    display.display();

    delay(1000);

  }


  // ----------------------------------------------------------
  // GPS
  // ----------------------------------------------------------

  gpsSerial.begin(

    GPS_BAUD,

    SERIAL_8N1,

    GPS_RX,

    GPS_TX

  );


  Serial.println(
    "GPS serial started"
  );


  // ----------------------------------------------------------
  // SERVOS
  // ----------------------------------------------------------

  panServo.setPeriodHertz(
    50
  );


  tiltServo.setPeriodHertz(
    50
  );


  panServo.attach(
    PAN_PIN,
    500,
    2400
  );


  tiltServo.attach(
    TILT_PIN,
    500,
    2400
  );


  panServo.write(
    panAngle
  );


  tiltServo.write(
    tiltAngle
  );


  // ----------------------------------------------------------
  // WIFI
  // ----------------------------------------------------------
  WiFi.onEvent(WiFiEvent);

  WiFi.setAutoReconnect(false);
  connectWiFi();
  // ============================================================


  // ----------------------------------------------------------
  // ROUTES
  // ----------------------------------------------------------

  server.on(
    "/",
    handleRoot
  );


  server.on(
    "/data",
    handleData
  );


  server.on(
    "/forward",
    handleForward
  );


  server.on(
    "/left",
    handleLeft
  );


  server.on(
    "/right",
    handleRight
  );


  server.on(
    "/stop",
    handleStop
  );

  server.on(
    "/backward",
    handleBackward
  );




  server.on(
    "/auto",
    handleAuto
  );


  server.on(
    "/manual",
    handleManual
  );


  server.on(
    "/panLeft",
    handlePanLeft
  );


  server.on(
    "/panRight",
    handlePanRight
  );


  server.on(
    "/tiltUp",
    handleTiltUp
  );


  server.on(
    "/tiltDown",
    handleTiltDown
  );

  server.on(
    "/probe/retract",
    handleProbeRetract
  );

  server.on(
    "/probe/deploy",
    handleProbeDeploy
  );

  server.on(
    "/probe/angle",
    handleProbeAngle
  );

  server.on(
    "/probe/up",
    handleTiltUp
  );

  server.on(
    "/probe/down",
    handleTiltDown
  );

  server.on(
    "/servoUp",
    handleServoUp
  );

  server.on(
    "/servoDown",
    handleServoDown
  );


  server.on(
    "/center",
    handleCenter
  );


  server.on(
    "/scan",
    handleScan
  );
  server.on(
    "/pumpOn",
    handlePumpOn
  );

  server.on(
    "/pump/on",
    handlePumpOn
  );

  server.on(
    "/pumpOff",
    handlePumpOff
  );

  server.on(
    "/pump/off",
    handlePumpOff
  );

  server.on(
    "/pumpInvert",
    handlePumpInvert
  );

  // ----------------------------------------------------------
  // START SERVER
  // ----------------------------------------------------------

  server.begin();


  Serial.println(
    "HTTP server started"
  );


  if (
    WiFi.status() ==
    WL_CONNECTED
  ) {

    Serial.print(
      "Open: http://"
    );


    Serial.print(
      WiFi.localIP()
    );


    Serial.println(
      "/"
    );

  }


  // ----------------------------------------------------------
  // INITIAL SENSORS
  // ----------------------------------------------------------

  cachedSoil =
    analogRead(
      SOIL_PIN
    );


  updateDistance();


  float initialTemp =
    dht.readTemperature();


  float initialHum =
    dht.readHumidity();


  if (
    !isnan(initialTemp)
  ) {

    cachedTemperature =
      initialTemp;

  }


  if (
    !isnan(initialHum)
  ) {

    cachedHumidity =
      initialHum;

  }


  lastDHTRead =
    millis();


  updateOLED();

}

// ============================================================
// WIFI AUTO RECONNECT
// ============================================================

// void maintainWiFi() {

//   static unsigned long lastAttempt = 0;

//   if (WiFi.status() == WL_CONNECTED) {
//     return;
//   }

//   if (millis() - lastAttempt < 15000) {
//     return;
//   }

//   lastAttempt = millis();

//   Serial.println("WiFi disconnected. Restarting connection...");

//   WiFi.disconnect(true);
//   delay(100);

//   WiFi.mode(WIFI_STA);
//   WiFi.begin(ssid, password);
// }
// ============================================================
// DIAGNOSTICS & SERIAL COMMANDS
// ============================================================

void runDiagnostics() {
  Serial.println("\n========================================");
  Serial.println(">>> AGRO-VATORS HARDWARE DIAGNOSTICS <<<");
  Serial.println("========================================");

  // 1. Line Sensors
  int l = digitalRead(LS);
  int c = digitalRead(CS);
  int r = digitalRead(RS);
  Serial.printf("[1/5] Line Sensors: Left=%d | Center=%d | Right=%d\n", l, c, r);

  // 2. Ultrasonic Sensor
  updateDistance();
  Serial.printf("[2/5] Ultrasonic Distance: %.1f cm (Obstacle=%s)\n", distance, obstacleDetected ? "YES" : "NO");

  // 3. Soil Moisture
  int soilVal = analogRead(SOIL_PIN);
  Serial.printf("[3/5] Soil Moisture: %d (Status: %s)\n", soilVal, soilVal < SOIL_THRESHOLD ? "WET" : "DRY");

  // 4. DHT11
  float t = dht.readTemperature();
  float h = dht.readHumidity();
  if (isnan(t) || isnan(h)) {
    Serial.println("[4/5] DHT11: Sensor reading failed / unplugged");
  } else {
    Serial.printf("[4/5] DHT11: Temperature=%.1f C | Humidity=%.1f %%\n", t, h);
  }

  // 5. Servos
  Serial.println("[5/5] Servos: Centered at 90 deg");

  // 6. LDR Sunlight Sensor
  int d_ldr = digitalRead(LDR_PIN);
  int a_ldr = analogRead(LDR_PIN);
  Serial.printf("[6/6] LDR Sunlight: Digital=%d (%s) | Analog=%d\n", d_ldr, (d_ldr == 0 ? "BRIGHT / DAYLIGHT" : "DARK / SHADE"), a_ldr);

  Serial.println("========================================");
  Serial.println(">>> DIAGNOSTICS COMPLETE <<<");
  Serial.println("========================================\n");
}

void runMotorTest() {
  Serial.println("\n>>> RUNNING MOTOR TEST (0.4s pulses) <<<");
  Serial.println("1. Forward (0.4s)...");
  forward();
  delay(400);
  stopMotor();
  delay(300);

  Serial.println("2. Backward (0.4s)...");
  backward();
  delay(400);
  stopMotor();
  delay(300);

  Serial.println("3. Turn Left (0.4s)...");
  left();
  delay(400);
  stopMotor();
  delay(300);

  Serial.println("4. Turn Right (0.4s)...");
  right();
  delay(400);
  stopMotor();
  delay(300);

  Serial.println("5. Testing Pump Relay (0.5s)...");
  pumpON();
  delay(500);
  pumpOFF();
  Serial.println(">>> MOTOR & PUMP TEST FINISHED - ALL OFF <<<\n");
}

void handleSerialCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd.length() == 0) return;

    if (cmd == "TEST" || cmd == "TEST_ALL") {
      runDiagnostics();
      runMotorTest();
    } else if (cmd == "TEST_SENSORS") {
      runDiagnostics();
    } else if (cmd == "TEST_MOTORS") {
      runMotorTest();
    } else if (cmd == "F" || cmd == "FORWARD") {
      forward(); Serial.println("OK: FORWARD");
    } else if (cmd == "B" || cmd == "BACKWARD") {
      backward(); Serial.println("OK: BACKWARD");
    } else if (cmd == "L" || cmd == "LEFT") {
      left(); Serial.println("OK: LEFT");
    } else if (cmd == "R" || cmd == "RIGHT") {
      right(); Serial.println("OK: RIGHT");
    } else if (cmd == "S" || cmd == "STOP") {
      stopMotor(); Serial.println("OK: STOP");
    } else if (cmd == "PUMP_ON") {
      pumpON(); Serial.println("OK: PUMP_ON");
    } else if (cmd == "PUMP_OFF") {
      pumpOFF(); Serial.println("OK: PUMP_OFF");
    } else if (cmd == "PUMP_INVERT") {
      relayActiveLow = !relayActiveLow;
      pumpOFF();
      Serial.printf("OK: RELAY ACTIVE %s\n", relayActiveLow ? "LOW" : "HIGH");
    } else if (cmd.startsWith("SERVO13:")) {
      int ang = cmd.substring(8).toInt();
      targetPan = ang;
      panAngle = ang;
      panServo.write(ang);
      Serial.printf("Servo (GPIO 13) moved to %d deg\n", ang);
    } else if (cmd.startsWith("SERVO25:")) {
      int ang = cmd.substring(8).toInt();
      targetTilt = ang;
      tiltAngle = ang;
      tiltServo.write(ang);
      Serial.printf("Servo (GPIO 25) moved to %d deg\n", ang);
    } else if (cmd == "DEPLOY") {
      targetTilt = 135;
      tiltAngle = 135;
      tiltServo.write(135);
      Serial.println("OK: PROBE DEPLOYED (135 deg)");
    } else if (cmd == "RETRACT") {
      targetTilt = 55;
      tiltAngle = 55;
      tiltServo.write(55);
      Serial.println("OK: PROBE RETRACTED (55 deg)");
    } else if (cmd == "SWEEP_SERVOS") {
      Serial.println("Sweeping GPIO 13 and GPIO 25 servos back and forth...");
      for (int a = 50; a <= 130; a += 10) {
        targetPan = a; panAngle = a; panServo.write(a);
        targetTilt = a; tiltAngle = a; tiltServo.write(a);
        delay(80);
      }
      for (int a = 130; a >= 50; a -= 10) {
        targetPan = a; panAngle = a; panServo.write(a);
        targetTilt = a; tiltAngle = a; tiltServo.write(a);
        delay(80);
      }
      targetPan = 90; panAngle = 90; panServo.write(90);
      targetTilt = 90; tiltAngle = 90; tiltServo.write(90);
      Serial.println("Servo sweep completed! Reset to 90 deg.");
    } else if (cmd == "TEST_LDR") {
      int d_ldr = digitalRead(LDR_PIN);
      int a_ldr = analogRead(LDR_PIN);
      Serial.printf("LDR: Digital=%d (%s) | Analog=%d\n", d_ldr, (d_ldr == 0 ? "BRIGHT (Light Detected)" : "DARK (Low Light)"), a_ldr);
    } else if (cmd == "STATUS") {
      updateDistance();
      int d_ldr = digitalRead(LDR_PIN);
      Serial.printf("STATUS: Temp=%.1f, Hum=%.1f, Soil=%d, Dist=%.1f, LDR=%d, L=%d, C=%d, R=%d\n",
        cachedTemperature, cachedHumidity, cachedSoil, distance, d_ldr,
        digitalRead(LS), digitalRead(CS), digitalRead(RS));
    } else {
      Serial.println("Unknown Serial Command: " + cmd);
    }
  }
}

// ============================================================
// LOOP
// ============================================================

void loop() {
  handleSerialCommands();

  // RC Failsafe Watchdog: Auto-stop if no command received within 600ms
  if (isDriving && (millis() - lastDriveTime > DRIVE_WATCHDOG_MS)) {
    stopMotor();
  }

  if (WiFi.getMode() == WIFI_STA &&
      wifiDisconnected &&
      millis() >= wifiReconnectTime &&
      WiFi.status() != WL_CONNECTED) {

    Serial.println("Attempting WiFi reconnect...");

    WiFi.begin();

    wifiReconnectTime = millis() + 20000;
  }
  // maintainWiFi();
  server.handleClient();


  updateGPS();


  unsigned long now =
    millis();


  if (
    now - lastSensorUpdate >=
    SENSOR_INTERVAL
  ) {

    lastSensorUpdate =
      now;


    updateSensorCache();

  }


  updateServos();


  if (!manualMode) {

    autonomousNavigation();

  }


  updateOLED();


  delay(10);
  yield();

}