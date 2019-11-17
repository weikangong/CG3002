#include "MPU6050.h"
#include <I2Cdev.h>
#include <Wire.h>
#include <Arduino_FreeRTOS.h>
#include <semphr.h>
#include <stdlib.h>
#include <avr/power.h>

// Sensors and Power definitions
const int CURR_PIN = A0;
const int VOLT_PIN = A1;
const float RS = 0.1;                   // Shunt resistor value (in ohms)
const int RL = 10000;                   // RL of the INA169 (in ohms)
const int R1 = 22;                     // R1 of voltage divider circuit, between power source and VOLT_PIN, in kohms
const int R2 = 22;                     // R2 of voltage divider circuit, between VOLT_PIN and ground, in kohms

float voltage_divide = ((float) R1 + R2) / (float) R2;  // Measured voltage is R2/(R1+R2) times actual V
float current = 0.0;                    // Calculated current value
float voltage = 0.0;                    // Calculated voltage
float power = 0.0;                      // Calculated power (P = IV)
float totalPower = 0.0;                   // Calculated energy (E = Pt)
unsigned long timeLastTaken = 0;        // The last time readings were calculated (in number of ms elapsed since startup)
unsigned long tempTime = 0;             // To use as "current time" in two lines

void setup() {
  // Digital pins for power
  pinMode(CURR_PIN, INPUT);
  pinMode(VOLT_PIN, INPUT);
    
   // Force unused DIGITAL pins to 0V for power saving
  for (int i = 0; i <= 53; i++) {
    if (i == 4 || i == 10 || i == 12 || i == 13 || i == 17 || i == 18 || i ==  19 || i == 20 || i == 21)
      continue;
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }

  // Force unused ANALOG pins to 0V for power saving
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

  // Disable SPI, unused USART
  power_spi_disable();
  power_usart2_disable();
  
  // Disable unused system timers
  power_timer1_disable();
  power_timer2_disable();
  power_timer3_disable();
  power_timer4_disable();
  power_timer5_disable();
}
  
  void getPowerValues() {
  voltage = ((float) analogRead(VOLT_PIN) * 5.0) * voltage_divide / 1023.0;
  
  float Vout = (float) analogRead(CURR_PIN) * 5.0 / 1023.0;
  
  current = (Vout * 1000) / (RL * RS);
  
  power = voltage * current;
  
  tempTime = millis();
  totalPower += (tempTime - timeLastTaken) * power / 1000.0;
  timeLastTaken = tempTime;

  powerData[0] = voltage;
  powerData[1] = current;
  powerData[2] = power;
  powerData[3] = totalPower;
}
