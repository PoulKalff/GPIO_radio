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
strings = ['', '', '', '', '']

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
screen = curses.initscr()
screen.border(0)
screen.keypad(1)
screen.scrollok(0)
curses.noecho()
curses.curs_set(0)
curses.start_color()
screen.nodelay(True)
curses.use_default_colors()
running = True
height, width = screen.getmaxyx()
width -= 11
screen.addstr(1, 1, 'PIN11    PIN16              PIN15    PIN31    PIN37')
screen.addstr(2, 1, '-----------------------------------------------------')
screen.addstr(18, 1, 'PIN:       STATUS:')
screen.addstr(19, 1, '------------------------')
# get status of all ports
for nr, port in enumerate(ports):
	usage = GPIO.gpio_function(port)
	if port_use[usage] == 'IN':
		input_ports.append(port)
		GPIO.setup(port, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	screen.addstr(20 + nr, 1, "%d          %s" % (port, port_use[usage]), 1)


while running:
	status = '  ' + str(GPIO.input(11)) + '        ' + str(GPIO.input(16)) + '                  ' + str(GPIO.input(15)) + '        ' + str(GPIO.input(31)) + '        ' + str(GPIO.input(37))
	screen.addstr(3, 1, status, 0)

	strings[0] = str(GPIO.input(11)) + strings[0]
	strings[1] = str(GPIO.input(16)) + strings[1]
	strings[2] = str(GPIO.input(15)) + strings[2]
	strings[3] = str(GPIO.input(31)) + strings[3]
	strings[4] = str(GPIO.input(37)) + strings[4]


	if len(strings[0]) >= width: strings[0] = strings[0][:width]
	if len(strings[1]) >= width: strings[1] = strings[1][:width]
	if len(strings[2]) >= width: strings[2] = strings[2][:width]
	if len(strings[3]) >= width: strings[3] = strings[3][:width]
	if len(strings[4]) >= width: strings[4] = strings[4][:width]



	screen.addstr(5, 1, 'Pin 11: ' + strings[0], 0)
	screen.addstr(6, 1, 'Pin 16: ' + strings[1], 0)
	screen.addstr(7, 1, 'Pin 15: ' + strings[2], 0)
	screen.addstr(8, 1, 'Pin 31: ' + strings[3], 0)
	screen.addstr(9, 1, 'Pin 37: ' + strings[4], 0)

#	screen.addstr(19, 1, str(len(strings[0])), 0)
#	screen.addstr(20, 1, str(len(strings[1])), 0)
#	screen.addstr(21, 1, str(len(strings[2])), 0)
#	screen.addstr(22, 1, str(len(strings[3])), 0)
#	screen.addstr(23, 1, str(len(strings[4])), 0)


	screen.refresh()
	keyPressed = screen.getch()
	if keyPressed == 32:
		strings[4] = str('1') + strings[4]
	if keyPressed == 27 or keyPressed == 113:
		running = False
	sleep(0.1)
screen.keypad(0)
curses.echo()
curses.nocbreak()
curses.endwin()
GPIO.cleanup()
print('\n Program terminated by user\n')

