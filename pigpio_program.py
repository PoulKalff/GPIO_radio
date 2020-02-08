#!/usr/bin/python3
import pigpio
from time import sleep

# --- Variables -----------------------------------------------------------------------

#GPIO_volA  = 11; GPIO.setup(GPIO_volA,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO_mute  = 15; GPIO.setup(GPIO_mute,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO_volB  = 18; GPIO.setup(GPIO_volB,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO_next  = 31; GPIO.setup(GPIO_next,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO_prev  = 37; GPIO.setup(GPIO_prev,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
#tupCW  = [ (1,1), (1,0), (0,0), (0,1) ]
#tupACW = [ (1,1), (0,1), (0,0), (1,0) ]

# --- Class / Def ---------------------------------------------------------------------

pi = pigpio.pi()
pi.set_mode(17, pigpio.INPUT)
pi.set_mode(24, pigpio.INPUT)
pi.set_pull_up_down(17, pigpio.PUD_UP)
pi.set_pull_up_down(24, pigpio.PUD_UP)
lastReading = (0, 0)


while True:
	currentReading = ( pi.read(17), pi.read(24) )
	if currentReading != lastReading:
		lastReading = currentReading
		print(currentReading)


"""
while True:
	volA = pi.read(11)
	volB = pi.read(18)


      if gpio == self.gpioA:
         self.levA = level
      else:
         self.levB = level;

      if gpio != self.lastGpio: # debounce
         self.lastGpio = gpio

         if   gpio == self.gpioA and level == 1:
            if self.levB == 1:
               self.callback(1)
         elif gpio == self.gpioB and level == 1:
            if self.levA == 1:
               self.callback(-1)
"""
