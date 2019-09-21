#include <Wire.h>
#define PIN 53


//Initialize Variables
long accX, accY, accZ;
float gyX, gyY, gyZ;

int MPU1_add = 0x68;
int MPU2_add = 0x69;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  setupMPU1();
  setupMPU2();
  digitalWrite(PIN, HIGH);
}


void loop() {
  process_acc(MPU1_add);
  process_gyro(MPU1_add);
  Serial.print("MPU1 : ");
  printResults();
  
  process_acc(MPU2_add);
  process_gyro(MPU2_add);
  Serial.print("MPU2 : ");
  printResults();
  
  Serial.println();
  delay(100);
}

void setupMPU1(){
  Wire.beginTransmission(MPU1_add); 
  Wire.write(0x6B); 
  Wire.write(0x00); //Setting SLEEP register to 0. 
  Wire.endTransmission();  

  //Accessing the register 0x1B which contains the Gyro Config
  Wire.beginTransmission(MPU1_add);
  Wire.write(0x1B); 

  //Set gyro to full scale +/-250deg./s
  Wire.write(0x00); 
  Wire.endTransmission(); 

  //Accessing the register 0x1C which contains the Acc Config
  Wire.beginTransmission(MPU1_add);
  Wire.write(0x1C);

  //Set acc to +/- 2g
  Wire.write(0x00);
  Wire.endTransmission(); 
}

void setupMPU2(){
  Wire.beginTransmission(MPU2_add); 
  Wire.write(0x6B); 
  Wire.write(0x00); //Setting SLEEP register to 0
  Wire.endTransmission();  

  //Accessing the register 0x1B which contains the Gyro Config
  Wire.beginTransmission(MPU2_add);
  Wire.write(0x1B); 

  //Set gyro to full scale +/-250deg./s
  Wire.write(0x00); 
  Wire.endTransmission(); 

  //Accessing the register 0x1C which contains the Acc Config
  Wire.beginTransmission(MPU2_add);
  Wire.write(0x1C);

  //Set acc to +/- 2g
  Wire.write(0x00);
  Wire.endTransmission(); 
}

void process_acc(int address) {
  Wire.beginTransmission(address); //I2C address of the MPU
  Wire.write(0x3B); //Starting register for Accel Readings
  Wire.endTransmission();
  Wire.requestFrom(address,6); //Request Accel Registers (3B - 40)
  while(Wire.available() < 6);
  accX = (Wire.read()<<8|Wire.read()) / 16384.0 * 9.81; //Store first two bytes into accelX and process it 
  accY = (Wire.read()<<8|Wire.read()) / 16384.0 * 9.81; //Store middle two bytes into accelY and process it
  accZ = (Wire.read()<<8|Wire.read()) / 16384.0 * 9.81; //Store last two bytes into accelZ and process it
}

void process_gyro(int address) {
  Wire.beginTransmission(address); //I2C address of the MPU
  Wire.write(0x43); //Starting register for Gyro Readings
  Wire.endTransmission();
  Wire.requestFrom(address,6); //Request Gyro Registers (43 - 48)
  while(Wire.available() < 6);
  gyX = (Wire.read()<<8|Wire.read()) / 131.0; //Store first two bytes into gyroX and process it
  gyY = (Wire.read()<<8|Wire.read()) / 131.0; //Store middle two bytes into gyroY and process it
  gyZ = (Wire.read()<<8|Wire.read()) / 131.0; //Store last two bytes into gyroZ and process it
}

void printResults() {

  Serial.print(" Acc ");
  Serial.print(" X=");
  Serial.print(accX);
  Serial.print(" Y=");
  Serial.print(accY);
  Serial.print(" Z=");
  Serial.print(accZ);
  Serial.print("Gyro ");
  Serial.print(" X=");
  Serial.print(gyX);
  Serial.print(" Y=");
  Serial.print(gyY);
  Serial.print(" Z=");
  Serial.print(gyZ);
}
