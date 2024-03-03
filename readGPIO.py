#!/usr/bin/python3
import sys
import json
import time
import socket
import logging
import subprocess
from time import sleep
import RPi.GPIO as GPIO
from rotary_class import RotaryEncoder

# --- Variables -----------------------------------------------------------------------


#GPIO.setmode(GPIO.BOARD)
#GPIO_clk        = 11; GPIO.setup(GPIO_clk,      GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
#GPIO_dt         = 16; GPIO.setup(GPIO_dt,       GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
#GPIO_mute	= 15; GPIO.setup(GPIO_mute,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
##GPIO_butA	= 37; GPIO.setup(GPIO_butA,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
#GPIO_butB	= 31; GPIO.setup(GPIO_butB,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
#clkLastState = GPIO.input(GPIO_clk)

# Define GPIO inputs
PIN_A = 17      # Pin 11
PIN_B = 23      # Pin 16
BUTTON = 22     # Pin 15


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
    """ Set volume of software, by writing to API """
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


def switch_event(event):
    if event == RotaryEncoder.CLOCKWISE:
        print("Clockwise")
        logging.info("Clockwise")
    elif event == RotaryEncoder.ANTICLOCKWISE:
        print("Anticlockwise")
        logging.info("Anticlockwise")
    elif event == RotaryEncoder.BUTTONDOWN:
        play_control('toggle')
        logging.info('Toggled mute/play')
        print("Toggle Button Down")
        sleep(1)
    return


# --- Main ----------------------------------------------------------------------------

# setup logging
logging.basicConfig(filename='/var/log/readGPIO.log', encoding='utf-8', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('init')

# wait for port 3000 to respond
while not is_port_in_use(3000):
    time.sleep(1)

# contact API to start up radio, set amixer to 100
set_volume(20)
subprocess.Popen("amixer -c 2 cset numid=1 100", stdout=subprocess.PIPE, shell=True).stdout.read()
play_control('play')

# Define rotary switch
rswitch = RotaryEncoder(PIN_A, PIN_B, BUTTON, switch_event)
logging.info("Started "  + str(rswitch))

# Listen continually
while True:
        time.sleep(0.5)





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
