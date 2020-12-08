/* Michael Inouye, Michael Bullock
 * Dr. Ditzler
 * ECE 529
 * 10 December 2020
 * Term Project
 * 
 * Description: This file loads onto a MEGA 2560 microcontroller. It listens for a tune and samples on its detectPin at 40kHz.
 * Once it detects the tune has stopped, it plays back the corrected frequencies and clean the signals of noise
 */

#include "arduinoFFT.h"
#define SAVE_AND_PLAY 1
#define ON_THE_FLY 0

const int operationMode = SAVE_AND_PLAY;
const int NUM_SAMPLES = 512; // total samples to collect per note
const int numNotes = 8; // number of notes to round to, inclding no notes
const int buzzerPin = 12; // GPIO for buzzer
const int detectPin = 2; // GPIO for incoming buzzer signal
const int noteDuration = 300; // 300ms note playback
const long int notes[numNotes] = {0, 262, 294, 329, 349, 392, 440, 494}; // note frequencies in major key
const char names[numNotes] = {'X', 'C', 'D', 'E', 'F', 'G', 'A', 'B'}; // note names

double vReal[NUM_SAMPLES]; // note samples stored here
double vImag[NUM_SAMPLES]; // note samples stored here

int autotunedNoteIndex = 0; // Note ID to save
int noteNum = 0; // counts total notes played so far
char corrected[50]; // list of notes to play back once finished listening

// some variables to keep track of the end of the song
char notem1 = ' ';
char notem2 = ' ';

arduinoFFT FFT = arduinoFFT();

void setup() {
  pinMode(detectPin, INPUT); // sets the incoming sound wave pin as an input
  Serial.begin(9600);
}

void loop() {
  // song finished
  if (operationMode == SAVE_AND_PLAY) {
    if (noteNum != 0 && (notem1 == names[0]) && (notem2 == names[0])) {
      delay(2000);
      for (int i = 0; i < noteNum; i++) {
            playbackSamples(notes[corrected[i]]);
            delay(400);
      }
      noteNum = 0;
      notem1 = ' ';
      notem2 = ' ';
      Serial.println("Waiting for next song!");
    }
  }
  
  //Serial.println("Awaiting next note...");
  awaitNextNote();
  //Serial.println("Note detected, now reading...");
  readSamples();
  //autotunedNoteIndex = autoTuneSamples();
  autotunedNoteIndex = autoTuneSamplesFFT();
  //Serial.println(names[autotunedNoteIndex]);
  //delay(300); // Is an extra delay needed before playing?
  
  if (operationMode == ON_THE_FLY) {
    playbackSamples(notes[autotunedNoteIndex]); // Live auto tune
  }
  else {
    corrected[noteNum] = autotunedNoteIndex; 
    noteNum++;
    notem2 = notem1;
    notem1 = names[autotunedNoteIndex];
  }
}

// Sample PWM output. Add delay to get around 20kHz sampling frequency
void readSamples() {
  int PWM = 0;
  /*unsigned long StartTime = micros();
  unsigned long CurrenTime;
  unsigned long ElaspsedTime;*/
  
  for (int i = 0; i < NUM_SAMPLES; i ++) {
    //StartTime = micros();
    PWM = digitalRead(detectPin);
    vReal[i] = PWM;
    vImag[i] = 0;
    delayMicroseconds(40);
    //while(micros() < (StartTime + 50));      // pause to get total sample at around 50us period (20kHz)
  }
  /*CurrenTime = micros();
  ElaspsedTime = CurrenTime - StartTime;
  Serial.println(ElaspsedTime);*/
  
  return;
}

// Take FFT of sample sequence to determine the contained frequency, then round to nearest note
int autoTuneSamplesFFT() {

 //FFT
  FFT.Windowing(vReal, NUM_SAMPLES, FFT_WIN_TYP_HAMMING, FFT_FORWARD);
  FFT.Compute(vReal, vImag, NUM_SAMPLES, FFT_FORWARD);
  FFT.ComplexToMagnitude(vReal, vImag, NUM_SAMPLES);
  int rounded_freq = FFT.MajorPeak(vReal, NUM_SAMPLES, 20000); //20kHz sample frequency

  //Serial.print(rounded_freq);
  
  if ((rounded_freq > 550) || (rounded_freq < 200)) {
    return 0;
  }

  
  int closest = 1000;
  int arg_min = -1;
  for (int i = 0; i < numNotes; i++) {
    if (notes[i] > rounded_freq) {
      if ((notes[i] - rounded_freq) < closest) {
        closest = notes[i] - rounded_freq;
        arg_min = i;
      }
    }
    else {
      if ((rounded_freq - notes[i]) < closest) {
        closest = rounded_freq - notes[i];
        arg_min = i;
      }
    }
  }
  return arg_min;
}

// Playback the new corrected note at the specified frequency!
void playbackSamples(int frequency) {

  tone(buzzerPin, frequency, noteDuration);
  
}

// Want to wait for a 50ms (50000us) period of ones before attempting to sample again
void awaitNextNote() {

  long int zeroCount = 0;
  

  //unsigned long StartTime = millis();
  while (zeroCount < 100) {
    if (digitalRead(detectPin) == LOW) {
      zeroCount++;
    }
    else {
      zeroCount = 0;
    }
    delayMicroseconds(500);
  }
  /*unsigned long CurrenTime = millis();
  unsigned long ElaspsedTime = CurrenTime - StartTime;
  Serial.println("Wow! that zero await took (ms)");
  Serial.println(ElaspsedTime);*/
  
  // wait until the next note starts (goes LOW)
  while (digitalRead(detectPin) == LOW);
  return;
}