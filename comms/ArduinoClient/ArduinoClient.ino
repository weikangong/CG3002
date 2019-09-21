#include <Wire.h>
#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include <stdlib.h>
#include <avr/power.h>

// Packet definitons
const int MAX_DATA_POINTS = 12;         // 4 sensors of 3 data points each
const int MAX_POWER_POINTS = 4;         // 4 different power parameters
const int MAX_PACKET_SIZE = 120; // Packet ID
const int MAX_PACKET = 30;

int ackID = 0;
int sendID = 0;
int slotID = 0;
char packetBuffer[MAX_PACKET_SIZE * MAX_PACKET];
char tempStr[MAX_PACKET_SIZE];

// Sensors and Power definitions
const int CURR_PIN = A0;
const int VOLT_PIN = A1;
const float RS = 0.1;                   // Shunt resistor value (in ohms)
const int RL = 10000;                   // RL of the INA169 (in ohms)
const int R1 = 425;                     // R1 of voltage divider circuit, between power source and VOLT_PIN, in kohms
const int R2 = 385;                     // R2 of voltage divider circuit, between VOLT_PIN and ground, in kohms

float voltage_divide = ((float) R1 + R2) / (float) R2;  // Measured voltage is R2/(R1+R2) times actual V
float current = 0.0;                    // Calculated current value
float voltage = 0.0;                    // Calculated voltage
float power = 0.0;                      // Calculated power (P = IV)
float cumpower = 0.0;                   // Calculated energy (E = Pt)
unsigned long timeLastTaken = 0;        // The last time readings were calculated (in number of ms elapsed since startup)
unsigned long tempTime = 0;             // To use as "current time" in two lines

const int MPU = 0x68;
float AcX, AcY, AcZ, Temp, GyX, GyY, GyZ;
float sensorData[MAX_DATA_POINTS];      // Acc1, Acc2, Acc3, gyro1
float powerData[MAX_POWER_POINTS];      // Voltage, current, power, cumpower

/////////////////////////////////
/////      HARDWARE        //////
/////////////////////////////////
void setup() {
  // Digital pins for sensors and power
  pinMode(13, OUTPUT);
  pinMode(12, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(CURR_PIN, INPUT);
  pinMode(VOLT_PIN, INPUT);

  // Force unused digital pins to 0V to conserve power
  for (int i = 0; i <= 53; i++) {
    if (i == 10 || i == 12 || i == 13 || i == 17 || i == 18 || i ==  19 || i == 20 || i == 21)
      continue;
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }

  // Force unused analog pins to 0V to converse power
  pinMode(A2, OUTPUT);
  pinMode(A3, OUTPUT);
  pinMode(A4, OUTPUT);
  pinMode(A5, OUTPUT);
  pinMode(A6, OUTPUT);
  pinMode(A7, OUTPUT);
  pinMode(A8, OUTPUT);
  pinMode(A9, OUTPUT);
  pinMode(A10, OUTPUT);
  pinMode(A11, OUTPUT);
  pinMode(A12, OUTPUT);
  pinMode(A13, OUTPUT);
  pinMode(A14, OUTPUT);
  pinMode(A15, OUTPUT);
  digitalWrite(A2, LOW);
  digitalWrite(A3, LOW);
  digitalWrite(A4, LOW);
  digitalWrite(A5, LOW);
  digitalWrite(A6, LOW);
  digitalWrite(A7, LOW);
  digitalWrite(A8, LOW);
  digitalWrite(A9, LOW);
  digitalWrite(A10, LOW);
  digitalWrite(A11, LOW);
  digitalWrite(A12, LOW);
  digitalWrite(A13, LOW);
  digitalWrite(A14, LOW);
  digitalWrite(A15, LOW);

  // Disable unused devices
  // power_adc_disable(); // probably required, we'll see
  power_spi_disable();
  //power_usart0_disable();
  power_usart2_disable();
  power_timer1_disable();
  power_timer2_disable();
  power_timer3_disable();
  power_timer4_disable();
  power_timer5_disable();

  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  Serial.begin(115200);
  Serial1.begin(115200); //Serial1: P19 RX, P18 TX
  Serial.println("Arduino Online!");
  
  handshake();
  xTaskCreate(startWork, "working", 200, NULL, 1, NULL);
  vTaskStartScheduler();
}

void getSensorsValues() {
  Serial.println("Reading Sensors");
  for (int i = 0; i < 3; i++) {
    if (i == 0) { // Acc1
      digitalWrite(13, LOW);
      digitalWrite(12, HIGH);
      digitalWrite(10, HIGH);
    } else if (i == 1) { // Acc2
      digitalWrite(13, HIGH);
      digitalWrite(12, LOW);
      digitalWrite(10, HIGH);
    } else { // Acc3
      digitalWrite(13, HIGH);
      digitalWrite(12, HIGH);
      digitalWrite(10, LOW);
    }

    Wire.beginTransmission(MPU);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU, 14, true);
    AcX = Wire.read() << 8 | Wire.read();
    AcY = Wire.read() << 8 | Wire.read();
    AcZ = Wire.read() << 8 | Wire.read();
    Temp = Wire.read() << 8 | Wire.read();
    GyX = Wire.read() << 8 | Wire.read();
    GyY = Wire.read() << 8 | Wire.read();
    GyZ = Wire.read() << 8 | Wire.read();

    sensorData[i * 3] = AcX / 16384;
    sensorData[i * 3 + 1] = AcY / 16384;
    sensorData[i * 3 + 2] = AcZ / 16384;

    if (i == 1) {
      sensorData[9] = GyX / 131;
      sensorData[10] = GyY / 131;
      sensorData[11] = GyZ / 131;
    }
  }
}

void getPowerValues() {
  Serial.println("Reading Power");
  voltage = ((float) analogRead(VOLT_PIN) * 5.0) * voltage_divide / 1023.0;
  // IS = (Vout * 1kohm) / (RL * RS)
  float vout = (float) analogRead(CURR_PIN) * 5.0 / 1023.0;
  current = (vout * 1000) / (RL * RS);
  power = voltage * current;
  tempTime = millis();
  cumpower += (tempTime - timeLastTaken) * power / 1000.0;
  timeLastTaken = tempTime;

  powerData[0] = voltage;
  powerData[1] = current;
  powerData[2] = power;
  powerData[3] = cumpower;
}

/////////////////////////////////
/////        COMMS         //////
/////////////////////////////////
void handshake() {
  while (1) { // Break only if rpi initiate handshake
    if (Serial1.available() && Serial1.read() == 'S') {
      Serial1.write('A');
      Serial.println("Ack Handshake"); 
      break;
    } else if (Serial.available() && Serial.read() == 'S') { // Test
      Serial.println("Ack Handshake");
      break;
    }
  }

  while (1) { // Break only if Ack received
    if (Serial1.available() && Serial1.read() == 'A') {
      Serial.println("Handshake complete");
      delay(500);
      break;
    } else if (Serial.available() && Serial.read() == 'A') { // Test
      Serial.println("Handshake complete");
      break;
    }
  }
}

// 1. Sensors and power
// 2. Format and send data
static void startWork(void * pvParameters) {
  TickType_t xLastWakeTime = xTaskGetTickCount();
  const TickType_t xFrequency = 100;
  
  while (1) {
    TickType_t xCurrWakeTime = xTaskGetTickCount();

    getSensorsValues();
    getPowerValues();
    formatMessage();
    pushMessage();
    getResponse();

    Serial.println();
    // 30 ms interval, ~30 samples/s
    vTaskDelayUntil(&xCurrWakeTime, 30/portTICK_PERIOD_MS);
  }
}

void formatMessage() {
  if (ackID == (slotID + 1) % MAX_PACKET) return; // No more empty slots
  
  Serial.print("Formatting Message, slotID: ");
  Serial.println(slotID);

  char slotIDChar[1];
  itoa(slotID, slotIDChar, 10);
  strcat(tempStr, slotIDChar);  // Converts slotID int to str and cat to tempStr as the packetId

  for (int i = 0; i < MAX_DATA_POINTS + MAX_POWER_POINTS; i++) {
    strcat(tempStr, ","); // Delimiter
    char floatChar[6];
    if (i < MAX_DATA_POINTS) dtostrf(sensorData[i], 0, 2, floatChar); // Converts floats to str, inputs: val, min char, char after dp, dest
    else dtostrf(powerData[i-MAX_DATA_POINTS], 0, 2, floatChar);

    strcat(tempStr, floatChar);
  }

  char checksum = 0;
  int len = strlen(tempStr);
  for (int i = 0; i < len; i++) checksum ^= tempStr[i];

  char checksumChar[6]; // TODO: find max value to allocate
  itoa((int) checksum, checksumChar, 10);

  strcat(tempStr, ",");
  strcat(tempStr, checksumChar);
  strcat(tempStr, "\n");

  int startIndex = slotID * MAX_PACKET_SIZE;
  for (int i = startIndex; i < startIndex + MAX_PACKET_SIZE; i++) packetBuffer[i] = tempStr[i-startIndex];

  slotID = (slotID + 1) % MAX_PACKET;
  Serial.print("Message formatted, len: ");
  Serial.println(strlen(tempStr));
  strcpy(tempStr, "");
}

void pushMessage() {
  if (sendID != slotID) {
    Serial.println("Pushing message");
    int startIndex = sendID * MAX_PACKET_SIZE;
    for (int i = startIndex; i < startIndex + MAX_PACKET_SIZE; i++) Serial1.write(packetBuffer[i]);
    sendID = (sendID + 1) % MAX_PACKET;
    Serial.println("Pushed message");
  } 
}

void getResponse() {
  if (Serial.available() && Serial1.read() == 'A') {
    int packetID = Serial1.read();
    ackID = packetID;
  } else if (Serial.available() && Serial1.read() == 'N') {
    int packetID = Serial1.read();
    ackID = packetID;
    sendID = packetID; // Resend previous frame 
  }
}

void loop() { }
