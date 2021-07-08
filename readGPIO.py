#!/usr/bin/python3
import json
import time
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------

GPIO.setmode(GPIO.BOARD)
GPIO_clk        = 11; GPIO.setup(GPIO_clk,      GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO_dt         = 16; GPIO.setup(GPIO_dt,       GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO_mute	= 15; GPIO.setup(GPIO_mute,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_butA	= 37; GPIO.setup(GPIO_butA,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_butB	= 31; GPIO.setup(GPIO_butB,	GPIO.IN, pull_up_down = GPIO.PUD_UP)

# --- Class / Def ---------------------------------------------------------------------


def is_port_in_use(port):
    """ Check if port is up """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        status = s.connect_ex(('localhost', port)) == 0
        return status


def play_control(value):	# play, toggle, pause, next, prev, stop, clearQueue
    """ Start playing, by writing to API """
    result = subprocess.getoutput('/usr/bin/curl -s 0 http://127.0.0.1:3000/api/v1/commands/?cmd=%s' % str(value))
    if not result: return False
    jsonResult = json.loads(result)
    return True if jsonResult['response'] == value + ' Success' else False


def set_volume(value):		# 0 - 100
    """ Set volume, by writing to API """
    result = subprocess.getoutput('/usr/bin/curl -s 0 "http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=%s"' % str(value))
    if not result:
        return False
    jsonResult = json.loads(result)
    return True if jsonResult['response'] == 'volume Success' else False


def get_status(value):		# status, position, albumart, uri, trackType, seek, samplerate, bitdepth, channels, random, repeat, repeatSingle, consume, volume, disableVolumeControl, mute, stream, updatedb, volatile, service
    """ Get status category, by writing to API, sort and return """
    result = subprocess.getoutput('/usr/bin/curl -s 0 http://127.0.0.1:3000/api/v1/getstate')
    if not result:
        return False
    jsonResult = json.loads(result)
    singleResult =  jsonResult[value]
    return singleResult if singleResult else False


# --- Main ----------------------------------------------------------------------------

# wait for port 3000 to respond
while not is_port_in_use(3000):
    time.sleep(1)

# contact API to start up radio
set_volume(28)
play_control('play')
masterVolume = get_status('volume')  # get volume once, and  only sync it back to radio when it changes

# enter hardware loop
try:
    while True:
        clkState = GPIO.input(GPIO_clk)
        dtState = GPIO.input(GPIO_dt)
        if clkState != clkLastState:
            if dtState != clkState:
                if masterVolume < 40:
                    masterVolume += 2
                    set_volume(masterVolume)
            else:
                if masterVolume >= 2:
                    masterVolume -= 2
                    set_volume(masterVolume)
        if GPIO.input(GPIO_mute) == GPIO.LOW:
            play_control('toggle')
            print('Toggled mute/play')
        if GPIO.input(GPIO_butA) == GPIO.LOW:
            print('Button A was pressed!' + str( GPIO.input(GPIO_butA) ) )
        if GPIO.input(GPIO_butB) == GPIO.LOW:
            print('Button B was pressed!')
        clkLastState = clkState
        sleep(0.01)
except:
   GPIO.cleanup()


# [GPIO Pins]
#
#              +-----------------------------------------------------------------------------------------------+
#              |                                                                                               |
#              |     	                +-------------------------------------------------------------------+  |
#              |                        |                                                                   |  |
#              |                        |                                            +-------------------+  |  |
#              |                        |                                            |                   |  |  |
#            Grnd                      DT                                          Grnd                  |  |  |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+  |  |  |
# | 02 | 04 | 06 | 08 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 |  |  |  |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+  |  |  |
# | 01 | 03 | 05 | 07 | 09 | 11 | 13 | 15 | 17 | 19 | 21 | 23 | 25 | 27 | 29 | 31 | 33 | 35 | 37 | 39 |  |  |  |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+  |  |  |
#  3.3V                      CLK       SW                                     ButA           ButB        |  |  |
#   |                         |         |                                       |              |         |  |  |
#   |                         |  +--------------------------------------------------------------------------+  |
#   |                         |  |      |                                       |              |         |     |
#   |                         |  |  +---+                                       |              |         |     |
#   |                         |  |  |                                           |              |         |     |
#   +----------------------------------+                                        |  +--------------+------+     |
#                             |  |  |  |                                        |  |           |  |            |
#                             |  |  |  |  +--------------------------------------------------------------------+
#                             |  |  |  |  |                                     |  |           |  |
#                             |  |  |  |  |                                     |  |           |  |
#                             C  D  S  3  G                                     B  G           B  G
#                             L  T  W  .  r                                     u  r           u  r
#                             K  |  |  3  n                                     t  n           t  n
#                             |  |  |  V  d                                     A  d           B  d
#                             |  |  |  |  |                                     |  |           |  |
#                           +-+--+--+--+--+-+                                +--+--+--+     +--+--+--+
#                           |               |                                |        |     |        |
#                           |               |                                | Button |     | Button |
#                           |               |                                |    A   |     |    B   |
#                           |               |                                |        |     |        |
#                           |   Rotary      |                                +--------+     +--------+
#                           |     Encoder   |
#                           |               |
#                           |               |
#                           |               |
#                           |               |
#                           +---------------+
#
