# Michael Inouye, Michael Bullock
# Dr. Ditzler
# ECE 529
# 10 December 2020
# Term Project


import sys
import RPi.GPIO as GPIO
import time

# true notes, for reference
notes = [(' ', 1), ('C',262), ('D', 294), ('E', 329), ('F', 349), ('G',392), ('A', 440), ('B', 494)]

# off-tune notes to be corrected
notes = [(' ', 1), ('C', 258), ('D',296), ('E', 326), ('F', 351), ('G',388), ('A', 435), ('B', 502)] 

# mary had a little lamb score
score = "EDCDEEE DDD EGG EDCDEEEEDDEDC"

# twinkle twinkle little star
score = "CCGGAAG  FFEEDDC  GGFFEED  GGFFEED  CCGGAAG  FFEEDDC"


score = "  " + score + "   "

# translate notes into frequency to play
playlist = []
for note in score :
	for lookup in notes :
		if lookup[0] == note :
			playlist.append(lookup[1])
			break


# Set buzzer pin
triggerPIN = 12

# Set pin to output
GPIO.setmode(GPIO.BCM)
GPIO.setup(triggerPIN,GPIO.OUT)

buzzer = GPIO.PWM(triggerPIN, 1)
buzzer.start(50)

# cycle PWM frequencies
for freq in playlist :
	print(freq) # print freq for reference
	buzzer.ChangeFrequency(freq)
	buzzer.start(50) # 50 % duty cycle
	time.sleep(.3) #play note for .3 secs
	buzzer.stop()
	time.sleep(.1)

# shut down pwm
time.sleep(1)
GPIO.cleanup()
sys.exit()
