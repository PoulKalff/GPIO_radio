#!/usr/bin/python3

import sys
import json
import time
import curses
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------

ports = [3,5,7,11,12,13,15,16,18,19,21,22,23,24,26,29,31,32,33,35,36,37,38,40]
input_ports = []
stringA = ''
stringB = ''
stringC = ''
stringD = ''
stringE = ''

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

input_ports = [11, 16, 15, 31, 37]	# overwrite to test only pins for current projects

screen = curses.initscr()
screen.border(0)
screen.keypad(1)
screen.scrollok(0)
curses.noecho()
curses.curs_set(0)
curses.start_color()
curses.use_default_colors()
running = True
screen.addstr(1, 1, 'PIN11    PIN16              PIN15    PIN31    PIN37')
screen.addstr(2, 1, '-----------------------------------------------------')

while running:
	status = '  ' + str(GPIO.input(11)) + '        ' + str(GPIO.input(16)) + '                  ' + str(GPIO.input(15)) + '        ' + str(GPIO.input(31)) + '        ' + str(GPIO.input(37))
	screen.addstr(3, 1, status, 0)


	stringA += str(GPIO.input(11))
	stringB += str(GPIO.input(16))
	stringC += str(GPIO.input(15))
	stringD += str(GPIO.input(31))
	stringE += str(GPIO.input(37))
	screen.addstr(5, 1, 'Pin 11:  ' + stringA[:40], 0)
	screen.addstr(6, 1, 'Pin 16:  ' + stringB[:40], 0)
	screen.addstr(7, 1, 'Pin 15:  ' + stringC[:40], 0)
	screen.addstr(8, 1, 'Pin 31:  ' + stringD[:40], 0)
	screen.addstr(9, 1, 'Pin 37:  ' + stringE[:40], 0)


	screen.refresh()
#	keyPressed = screen.getch()
#	if keyPressed == 32:
#		stringA += 's'


#	if keyPressed == 27 or keyPressed == 113:
#		running = False
screen.keypad(0)
curses.echo()
curses.nocbreak()
curses.endwin()
GPIO.cleanup()
sys.exit('\n Program terminated by user\n' + str(len(stringA)))

# --- Variables -----------------------------------------------------------------------

# GPIO.setmode(GPIO.BOARD)
# GPIO_volUp      = 11; GPIO.setup(GPIO_volUp,    GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_volDown    = 16; GPIO.setup(GPIO_volDown,  GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_mute       = 15; GPIO.setup(GPIO_mute,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_butA       = 37; GPIO.setup(GPIO_butA,     GPIO.IN, pull_up_down = GPIO.PUD_UP)
# GPIO_butB       = 31; GPIO.setup(GPIO_butB,     GPIO.IN, pull_up_down = GPIO.PUD_UP)


