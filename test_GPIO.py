#!/usr/bin/python3

import sys
import json
import time
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------

ports = [3,5,7,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]
input_ports = []

port_use = 	{	0:  "OUT",
			1:  "IN",
			40: "SERIAL",
			41: "SPI",
			42: "I2C",
			43: "HARD_PWM", 
			-1: "UNKNOWN"
		}

# --- Main ----------------------------------------------------------------------------

# Show all GPIO ports
GPIO.setmode(GPIO.BOARD)

# Set up all GPIO pins defined as GPIO.IN, so that we cant watch them
for port in ports:
	usage = GPIO.gpio_function(port)
	if port_use[usage] == 'IN':
		input_ports.append(port)
		GPIO.setup(port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	print("%d status: %s" % (port, port_use[usage]))

input_ports = [11, 12, 15, 31, 37]	# overwrite to test only pins for current projects

print('Found ' + str(len(input_ports)) + ' ports set up for input:')
print('11  16               15   31   37')

# enter hardware testing loop
counter = 0
while True:
	print(' ' + str(GPIO.input(11)), ' ', GPIO.input(16), '              ', GPIO.input(15), '  ', GPIO.input(31), '  ', GPIO.input(37), end='')
	print(' --- COUNT: ' + str(counter))
	sleep(0.1)
	counter += 1 
GPIO.cleanup()


# --- Variables -----------------------------------------------------------------------

# GPIO.setmode(GPIO.BOARD)
# GPIO_volUp      = 11; GPIO.setup(GPIO_volUp,    GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_volDown    = 12; GPIO.setup(GPIO_volDown,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_mute       = 15; GPIO.setup(GPIO_mute,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_butA       = 37; GPIO.setup(GPIO_butA,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_butB       = 31; GPIO.setup(GPIO_butB,     GPIO.IN, pull_up_down = GPIO.PUD_UP)


