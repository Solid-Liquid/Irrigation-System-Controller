/*******************************************************************************
 COMMUNICATION STUFF ***********************************************************
*******************************************************************************/
#include <Wire.h>
#include <MIDI.h>
byte x = 0;
byte stat = 0;
const byte adrOffset = 40; // 40 because reasons
const byte adrPin[] = {4,5,6,7};
byte address = 0;
boolean valveState[] = {false,false,false,false,false,false,false,false,false,false,false,false,false,false,false,false};

void comSetup() {
  address = getAddress(); //need this to print to led display
  Wire.begin(address);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  //Serial.begin(115200);// moved to MIDI setup
  //Serial.println(address);
}

//read 4bit address jumpers to create byte address (software limit to 16 sauce boards per pi)
byte getAddress(){
  byte address = 0;
  boolean bits[] = {false,false,false,false};
  for(byte i = 0; i < 4; i++){
    if(digitalRead(adrPin[i])){
      bits[i] = true;
    }
  }
  for(byte i=0; i<4; i++){
    address |= bits[i] << i;
  }
  return address+adrOffset; //offset address by some arbitrary value greater than the I2C LCD
}

void receiveEvent(int howMany) {
  //while (1 < Wire.available()) { // loop through all but the last
  //  char c = Wire.read(); // receive byte as a character
  //}
  //SWITCH will be better here but i'm lazy so yeahhhhhh
  x = Wire.read();    // receive byte as an integer
  if(x<16){
    valveState[x] = true;
  }
  else if(x>15){
    valveState[x-16] = false;
  }
}

void requestEvent() {
  //Serial.print("Sent: ");
  Serial.println(stat);
  Wire.write(stat);
}

/*******************************************************************************
 REALTIME DEBUG ****************************************************************
*******************************************************************************/
// 2 seven segment LED displays on the board
// active low
#include "SevSeg.h"
SevSeg disp;

void dispSetup(){
  byte digitPins[] = {21,20};
  byte segmentPins[] = {29,48,49,51,50,47,46,28}; //Segments: A,B,C,D,E,F,G,Period
  disp.begin(COMMON_ANODE, 2, digitPins, segmentPins, false, false, true);
  disp.setBrightness(10);
  //disp.setChars("go");
  //disp.refreshDisplay();
}

/*******************************************************************************
 VALVE STUFF *******************************************************************
*******************************************************************************/
// current measurement not implemented yet
#define DCshunt PA7 //11
#define ACshunt PA6 //12
#define killRelay 8
const byte numValves = 16;
const byte valvePins[] = {32,33,34,35,36,37,38,39,40,41,42,43,44,3,2,45};
byte numValvesOn = 0;
const int MAperChannel = 150;

void valveSetup(){
  Serial.println("starting valveSetup");
  pinMode(killRelay, OUTPUT);
  pinMode(DCshunt, INPUT);
  pinMode(ACshunt, INPUT);
  for(byte i = 0; i < numValves; i++){
    pinMode(valvePins[i], OUTPUT);
  }
  digitalWrite(killRelay,HIGH);
  Serial.println("finished valveSetup");

  for(byte i = 0; i < numValves; i++){
    digitalWrite(valvePins[i],HIGH);
    delay(100);
    digitalWrite(valvePins[i],LOW);
  }
  digitalWrite(killRelay,LOW);
  delay(250);
  digitalWrite(killRelay,HIGH);
  Serial.println("finished POST");
}

void valveUpdate(){
  numValvesOn = 0;
  int mAmps = 0;
  for(byte i = 0; i < numValves; i++){
    if(valveState[i]){
      digitalWrite(valvePins[i],HIGH);
      numValvesOn++;
      disp.setNumber(i,0);
    }
    else{
      digitalWrite(valvePins[i],LOW);
    }
  }
  if(numValvesOn*MAperChannel >= MAperChannel*numValves){
    digitalWrite(killRelay,LOW);
    Serial.println("ERROR: over current triggered");
  }
}

/*******************************************************************************
 FLOW SENSOR *******************************************************************
*******************************************************************************/
// only gonna use 1 flow sensor to start

#define FLOW0 PC10 //9 //PC10
//#define FLOW1 10 //PA15
int flow0Counter = 0;
//int flow1Counter = 0;
unsigned long prevMillis = 0;
const unsigned long period = 1000;
float GPM0;
//extern float GPM1;
//Offset and K based off datasheet. using model 228PV30xx-xxxx
const float flowOffset = 0.227;
const float flowK = 8.309;


void flow0ISR(){
  flow0Counter++;
}

//void flow1ISR(){
//  flow1Counter++;
//}

void flowUpdate(){
  unsigned long currentMillis = millis();
  if (currentMillis - prevMillis >= period){
    //GPM0 = (flow0Counter+flowOffset)*flowK-1.89; //this function is from the datasheet
    //GPM1 = (flow1Counter+flowOffset)*flowK;
    GPM0 = (flow0Counter / 7.5); //for chinese flow sensor
    //Serial.print("LitrePM: ");
    //Serial.println(GPM0);
    flow0Counter = 0;
    //flow1Counter = 0;
    prevMillis = currentMillis;
  }
}

void flowSetup(){
  pinMode(FLOW0, INPUT);
  //pinMode(FLOW1, INPUT);
  attachInterrupt(digitalPinToInterrupt(FLOW0), flow0ISR, FALLING); //FALLING (pull-up). RISING (pull-down)
  //attachInterrupt(digitalPinToInterrupt(FLOW1), flow1ISR, FALLING);
}

/*******************************************************************************
 SUPER SECRET SAUCE ssshhhh ****************************************************
*******************************************************************************/
void HandleNoteOn(byte channel, byte pitch, byte velocity) {
  if(velocity != 0){
    //A
    if (pitch == 106 || pitch == 105 || pitch == 94 || pitch == 93 || pitch == 82 || pitch == 81 || pitch == 70 || pitch == 69 || pitch == 58 || pitch == 57 || pitch == 46 || pitch == 45 || pitch == 34 || pitch == 33 || pitch == 22 || pitch == 21){
      valveState[0] = true;
    }
    //B
    else if (pitch == 107 || pitch == 95 || pitch == 83 || pitch == 71 || pitch == 59 || pitch == 45 || pitch == 35 || pitch == 23){
      valveState[1] = true;
    }
    //C
    else if (pitch == 108 || pitch == 97 || pitch == 96 || pitch == 85 || pitch == 84 || pitch == 73 || pitch == 72 || pitch == 61 || pitch == 60 || pitch == 47 || pitch == 46 || pitch == 37 || pitch == 36 || pitch == 25 || pitch == 24){
      valveState[2] = true;
    }
    //D
    else if (pitch == 98 || pitch == 86 || pitch == 74 || pitch == 63 || pitch == 62 || pitch == 48 || pitch == 38 || pitch == 26){
      valveState[3] = true;
    }
    //E
    else if (pitch == 100 || pitch == 99 || pitch == 88 || pitch == 87 || pitch == 76 || pitch == 75 || pitch == 64 || pitch == 64 || pitch == 50 || pitch == 49 || pitch == 40 || pitch == 39 || pitch == 28 || pitch == 27){
      valveState[4] = true;
    }
    //F
    else if (pitch == 102 || pitch == 101 || pitch == 90 || pitch == 89 || pitch == 78 || pitch == 77 || pitch == 66 || pitch == 65 || pitch == 52 || pitch == 51 || pitch == 42 || pitch == 41 || pitch == 30 || pitch == 29){
      valveState[5] = true;
    }
    //G
    else if (pitch == 104 || pitch == 103 || pitch == 92 || pitch == 91 || pitch == 80 || pitch == 79 || pitch == 68 || pitch == 67 || pitch == 56 || pitch == 55 || pitch == 54 || pitch == 53 || pitch == 44 || pitch == 43 || pitch == 32 || pitch == 31){
      valveState[6] = true;
    }
  }
  else{
    //A
    if (pitch == 106 || pitch == 105 || pitch == 94 || pitch == 93 || pitch == 82 || pitch == 81 || pitch == 70 || pitch == 69 || pitch == 58 || pitch == 57 || pitch == 46 || pitch == 45 || pitch == 34 || pitch == 33 || pitch == 22 || pitch == 21){
      valveState[0] = false;
    }
    //B
    else if (pitch == 107 || pitch == 95 || pitch == 83 || pitch == 71 || pitch == 59 || pitch == 45 || pitch == 35 || pitch == 23){
      valveState[1] = false;
    }
    //C
    else if (pitch == 108 || pitch == 97 || pitch == 96 || pitch == 85 || pitch == 84 || pitch == 73 || pitch == 72 || pitch == 61 || pitch == 60 || pitch == 47 || pitch == 46 || pitch == 37 || pitch == 36 || pitch == 25 || pitch == 24){
      valveState[2] = false;
    }
    //D
    else if (pitch == 98 || pitch == 86 || pitch == 74 || pitch == 63 || pitch == 62 || pitch == 48 || pitch == 38 || pitch == 26){
      valveState[3] = false;
    }
    //E
    else if (pitch == 100 || pitch == 99 || pitch == 88 || pitch == 87 || pitch == 76 || pitch == 75 || pitch == 64 || pitch == 64 || pitch == 50 || pitch == 49 || pitch == 40 || pitch == 39 || pitch == 28 || pitch == 27){
      valveState[4] = false;
    }
    //F
    else if (pitch == 102 || pitch == 101 || pitch == 90 || pitch == 89 || pitch == 78 || pitch == 77 || pitch == 66 || pitch == 65 || pitch == 52 || pitch == 51 || pitch == 42 || pitch == 41 || pitch == 30 || pitch == 29){
      valveState[5] = false;
    }
    //G
    else if (pitch == 104 || pitch == 103 || pitch == 92 || pitch == 91 || pitch == 80 || pitch == 79 || pitch == 68 || pitch == 67 || pitch == 56 || pitch == 55 || pitch == 54 || pitch == 53 || pitch == 44 || pitch == 43 || pitch == 32 || pitch == 31){
      valveState[6] = false;
    }
  }
  // Try to keep your callbacks short (no delays ect) as the contrary would slow down the loop()
  // and have a bad impact on real-time performance.
}

void HandleNoteOff(byte channel, byte pitch, byte velocity) { 
  //A
  if (pitch == 106 || pitch == 105 || pitch == 94 || pitch == 93 || pitch == 82 || pitch == 81 || pitch == 70 || pitch == 69 || pitch == 58 || pitch == 57 || pitch == 46 || pitch == 45 || pitch == 34 || pitch == 33 || pitch == 22 || pitch == 21){
    valveState[0] = false;
  }
  //B
  else if (pitch == 107 || pitch == 95 || pitch == 83 || pitch == 71 || pitch == 59 || pitch == 45 || pitch == 35 || pitch == 23){
    valveState[1] = false;
  }
  //C
  else if (pitch == 108 || pitch == 97 || pitch == 96 || pitch == 85 || pitch == 84 || pitch == 73 || pitch == 72 || pitch == 61 || pitch == 60 || pitch == 47 || pitch == 46 || pitch == 37 || pitch == 36 || pitch == 25 || pitch == 24){
    valveState[2] = false;
  }
  //D
  else if (pitch == 98 || pitch == 86 || pitch == 74 || pitch == 63 || pitch == 62 || pitch == 48 || pitch == 38 || pitch == 26){
    valveState[3] = false;
  }
  //E
  else if (pitch == 100 || pitch == 99 || pitch == 88 || pitch == 87 || pitch == 76 || pitch == 75 || pitch == 64 || pitch == 64 || pitch == 50 || pitch == 49 || pitch == 40 || pitch == 39 || pitch == 28 || pitch == 27){
    valveState[4] = false;
  }
  //F
  else if (pitch == 102 || pitch == 101 || pitch == 90 || pitch == 89 || pitch == 78 || pitch == 77 || pitch == 66 || pitch == 65 || pitch == 52 || pitch == 51 || pitch == 42 || pitch == 41 || pitch == 30 || pitch == 29){
    valveState[5] = false;
  }
  //G
  else if (pitch == 104 || pitch == 103 || pitch == 92 || pitch == 91 || pitch == 80 || pitch == 79 || pitch == 68 || pitch == 67 || pitch == 56 || pitch == 55 || pitch == 54 || pitch == 53 || pitch == 44 || pitch == 43 || pitch == 32 || pitch == 31){
    valveState[6] = false;
  }
}

void eggSetup(){
  MIDI.begin(MIDI_CHANNEL_OMNI);
  Serial.begin(115200);
  MIDI.setHandleNoteOn(HandleNoteOn);  // Put only the name of the function
  MIDI.setHandleNoteOff(HandleNoteOff);
}

/*******************************************************************************
 NORMAL LOOP *******************************************************************
*******************************************************************************/
void setup(){
  dispSetup();
  comSetup();
  eggSetup();
  valveSetup();
  flowSetup();
  disp.setNumber(address,0);
  randomSeed(123); // for user test button
}

long randNumber;
//long prevMillis2 = 0;
boolean good = true;

void loop() {//no delays allowed anywhere EVER in this loop, including the method calls EVERRRRRRR
  valveUpdate(); //
  flowUpdate(); //update the sensor
  disp.refreshDisplay(); //update LED display segment
  MIDI.read();
  if(!digitalRead(23)){ //tester thing
    //Serial.print("LitrePM: ");
    //Serial.println(GPM0);
    randNumber = random(0,15);
    valveState[randNumber] = !valveState[randNumber];
    if(good){
      stat = 1;
    }
    else{
      stat = 0;
    }
    delay(100);
  }
}
