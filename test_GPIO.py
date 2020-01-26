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
		GPIO.setup(port, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
	print("%d status: %s" % (port, port_use[usage]))

print('Found ' + str(len(input_ports)) + ' ports set up for input:')
print('              ', input_ports)

# enter hardware testing loop
counter = 0
while True:
	print('COUNT' + str(counter) + '-------> ', end = ' ')
	for port in input_ports:
		print(GPIO.input(port), '  ', end = '')
	print()
	sleep(1)
	counter += 1 
GPIO.cleanup()



