
const bool DEBUG = false;

const byte START_BYTE = '0';
const byte END_BYTE = '\n';

const byte OK = '1';
const byte ERROR_WRONG_START_BYTE = '2';
const byte ERROR_UNKNOWN_OPTION = '3';
const byte ERROR_WRONG_END_BYTE = '4';
const byte ERROR_TOO_EARLY = '5';
const byte ERROR_ALREADY_RUNNING = '6';
const byte ERROR_ALREADY_STOPPED = '7';

const byte OPTION_GET_TEMP = 'a';
const byte OPTION_GET_HUMID = 'b';
const byte OPTION_GET_PRESSURE = 'c';
const byte OPTION_PRESS_START_STOP = 'd';
const byte OPTION_PRESS_SPEED_UP = 'e';
const byte OPTION_PRESS_SPEED_DOWN = 'f';
const byte OPTION_READ_VOLT = 'g';
const byte OPTION_READ_CURRENT = 'h';
const byte OPTION_GET_SPEED = 'i';
const byte OPTION_PRESS_START = 'j';
const byte OPTION_PRESS_STOP = 'k';

const byte PIN_START_STOP = 3;
const byte PIN_SPEED_UP = 4;
const byte PIN_SPEED_DOWN = 5;

const byte PIN_VOLTAGE = A0;
const byte PIN_CURRENT = A1;
const byte PIN_SPEED_SENSOR = 2;

unsigned long speed_readings[4];
unsigned long last_time_start_stop_pressed = 0;

void setup() {
    Serial.setTimeout(1000);
    // set the baud rate 
    Serial.begin(9600);
    // time to get serial running
    while(!Serial);
    
    if(DEBUG){
      Serial.println("Serial started");
    }

    pinMode(PIN_START_STOP, OUTPUT);
    pinMode(PIN_SPEED_UP, OUTPUT);
    pinMode(PIN_SPEED_DOWN, OUTPUT);
    pinMode(PIN_SPEED_SENSOR, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_SPEED_SENSOR), speed_sensor_raising, RISING);

}

void loop() {

  if(Serial.available() > 2){
    
      byte startByte = Serial.read();
      if(startByte == START_BYTE){
        
          byte option = Serial.read();
          executeOption(option);
          
          byte endByte = Serial.read();
          if(endByte != END_BYTE){
             writeError(ERROR_WRONG_END_BYTE);
          }
      }
      else{
          writeError(ERROR_WRONG_START_BYTE);
      }
     
  }
  delay(10); // wait a little bit
}

void executeOption(byte option){

    if(option == OPTION_PRESS_START){
      pressStart();
    }
    else if(option == OPTION_PRESS_STOP){
      pressStop();
    }
    else if(option == OPTION_PRESS_START_STOP){
      pressButton(PIN_START_STOP,300);
      writeOptionResponse(OPTION_PRESS_START_STOP, OK);
    }
    else if(option == OPTION_PRESS_SPEED_UP){
      pressButton(PIN_SPEED_UP,2000);
      writeOptionResponse(OPTION_PRESS_SPEED_UP, OK);
    }
    else if(option == OPTION_PRESS_SPEED_DOWN){
      pressButton(PIN_SPEED_DOWN,2000);
      writeOptionResponse(OPTION_PRESS_SPEED_DOWN, OK);
    }
    else if(option == OPTION_GET_SPEED){
      float rpm = getSpeed();
      writeOptionResponseFloat(OPTION_GET_SPEED, rpm);
    }
    else if(option == OPTION_READ_VOLT){
      float voltage = readVoltage();
      writeOptionResponseFloat(OPTION_READ_VOLT, voltage);
    }
    else if(option == OPTION_READ_CURRENT){
      float current = readCurrent();
      writeOptionResponseFloat(OPTION_READ_CURRENT, current);
    }
    else{
      writeError(ERROR_UNKNOWN_OPTION);
    }
}

void pressStart(){
  unsigned long lastPressDiff = millis() - last_time_start_stop_pressed;

  // check last press time > 3 sek
  if(lastPressDiff < 3000){
    writeOptionResponse(OPTION_PRESS_START, ERROR_TOO_EARLY);
    return;
  }

  if(getSpeed() > 100){
    writeOptionResponse(OPTION_PRESS_START, ERROR_ALREADY_RUNNING);
    return;
  }

  last_time_start_stop_pressed = millis();
  pressButton(PIN_START_STOP,300);
  writeOptionResponse(OPTION_PRESS_START, OK);
  
}

void pressStop(){
  unsigned long lastPressDiff = millis() - last_time_start_stop_pressed;

  // check last press time > 3 sek
  if(lastPressDiff < 3000){
    writeOptionResponse(OPTION_PRESS_STOP, ERROR_TOO_EARLY);
    return;
  }

  if(getSpeed() < 100){
    writeOptionResponse(OPTION_PRESS_STOP, ERROR_ALREADY_STOPPED);
    return;
  }

  // always stop at same time on rotation
  unsigned long diff = millis() - speed_readings[0];
  if(diff < 500){
    delay(500 - diff);
  }

  last_time_start_stop_pressed = millis();
  pressButton(PIN_START_STOP,300);
  writeOptionResponse(OPTION_PRESS_STOP, OK);
  
}

void pressButton(byte pin, unsigned long time){
  if(DEBUG){
    Serial.print("press");
  }
  digitalWrite(pin,HIGH);
  delay(time);
  digitalWrite(pin,LOW);
  if(DEBUG){
    Serial.print("pressed");
  }
}

float readCurrent(){
  int amp_read = analogRead(PIN_CURRENT);
  float current = (amp_read * (5.0 / 1024.0))*1000;
  return current;
}

float readVoltage(){
  int volt_read = analogRead(PIN_VOLTAGE);
  float voltage = volt_read * (5.0 / 1024.0) * 5.0;
  Serial.print(volt_read);
  return voltage;
}

/* 
 *  return current shaker speed
 *  calculates time between last two readings from speed sensor
 */
float getSpeed(){
   //Don't process interrupts during calculations
   detachInterrupt(0);

   unsigned long diff = speed_readings[0] - speed_readings[1];
   unsigned long time_since_last_reading = millis() - speed_readings[0];
   float rpm = 0;
   if(time_since_last_reading > 2000 || diff == 0 || diff > 2000){
     rpm = 0;
   }
   else{
     rpm = (float) 60000/diff;
   }

   //Restart the interrupt processing
   attachInterrupt(0, speed_sensor_raising, RISING);

   return rpm;
}

void speed_sensor_raising(){
   unsigned long timestamp = millis();
   // Shift older sensor timestamps
   speed_readings[3] = speed_readings[2];
   speed_readings[2] = speed_readings[1];
   speed_readings[1] = speed_readings[0];
   // Add this readings timestamp;
   speed_readings[0] = timestamp;
}

void writeOptionResponseFloat(byte option, float value){
        Serial.write(START_BYTE);
        Serial.write(option);
        writeFloat(value);
        Serial.write(END_BYTE);
}

void writeOptionResponse(byte option, byte value){
        Serial.write(START_BYTE);
        Serial.write(option);
        Serial.write(value);
        Serial.write(END_BYTE);
}

void writeFloat(float arg) {
  // get float as a byte-array:
  byte * data = (byte *) &arg;
  Serial.write(data, 4);
  if(DEBUG){
    Serial.print(arg);
  }
}

void writeError(byte errorCode){
  Serial.write(START_BYTE);
  Serial.write(errorCode);
  Serial.write(END_BYTE);
}
