
#include "MPU6050.h"
#include <I2Cdev.h>
#include <Wire.h>
#include <stdlib.h>

//Initialize Function Headers
void setupSensors();
void processData(int16_t,int16_t,int16_t,int16_t,int16_t,int16_t,int16_t,int16_t,int16_t,int16_t,int16_t,int16_t);

//Initialize Sensor Variables
MPU6050 accelgyro; // class default I2C address is 0x68
MPU6050 accelgyro2(0x69);
int16_t accX1, accY1, accZ1;
int16_t gyX1, gyY1, gyZ1;
int16_t accX2, accY2, accZ2;
int16_t gyX2, gyY2, gyZ2;

/* Variables for processed data */

float gForceX1, gForceY1, gForceZ1; //Accelerometer processed variables
float rotX1, rotY1, rotZ1;          //Gyroscope processed variables

float gForceX2, gForceY2, gForceZ2; //Accelerometer processed variables
float rotX2, rotY2, rotZ2;          //Gyroscope processed variables


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Wire.begin();
  setupSensors();
}

//Initialize sensors
void setupSensors() {
    accelgyro.initialize();
    accelgyro2.initialize();
}


void processData(int16_t accX1,int16_t accY1,int16_t accZ1,int16_t gyX1,int16_t gyY1,int16_t gyZ1,int16_t accX2,int16_t accY2,int16_t accZ2,int16_t gyX2,int16_t gyY2,int16_t gyZ2) {

    gForceX1 = accX1 / 16384.0 * 9.81;
    gForceY1 = accY1 / 16384.0 * 9.81; 
    gForceZ1 = accZ1 / 16384.0 * 9.81;
    rotX1 = gyX1 / 131.0;
    rotY1 = gyY1 / 131.0; 
    rotZ1 = gyZ1 / 131.0;

    gForceX2 = accX2 / 16384.0 * 9.81;
    gForceY2 = accY2 / 16384.0 * 9.81; 
    gForceZ2 = accZ2 / 16384.0 * 9.81;
    rotX2 = gyX2 / 131.0;
    rotY2 = gyY2 / 131.0; 
    rotZ2 = gyZ2 / 131.0;

}

void loop() {
  // put your main code here, to run repeatedly:
  //read sensors, integration with hardware
    accelgyro.getMotion6(&accX1, &accY1, &accZ1, &gyX1, &gyY1, &gyZ1);
    accelgyro2.getMotion6(&accX2, &accY2, &accZ2, &gyX2, &gyY2, &gyZ2);

    //process data, give accelerometer readings in g, gyrometer readings in deg
    processData(accX1, accY1, accZ1, gyX1, gyY1, gyZ1, accX2, accY2, accZ2, gyX2, gyY2, gyZ2);

        Serial.print("Sensor 1: a/g:\t");
        Serial.print(gForceX1); Serial.print("\t");
        Serial.print(gForceY1); Serial.print("\t");
        Serial.print(gForceZ1); Serial.print("\t");
        Serial.print(rotX1); Serial.print("\t");
        Serial.print(rotY1); Serial.print("\t");
        Serial.println(rotZ1);

        Serial.print("Sensor 2 a/g:\t");
        Serial.print(gForceX2); Serial.print("\t");
        Serial.print(gForceY2); Serial.print("\t");
        Serial.print(gForceZ2); Serial.print("\t");
        Serial.print(rotX2); Serial.print("\t");
        Serial.print(rotY2); Serial.print("\t");
        Serial.println(rotZ2);
      
}
