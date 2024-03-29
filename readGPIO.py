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

currentVolume = 35
eventsList = []

GPIO.setmode(GPIO.BCM)	# not necessary, already set in rotaryEncoder
GPIO_clk =  17  # Pin 11
GPIO_dt =   23  # Pin 16
GPIO_play = 22  # Pin 15
GPIO_butA = 26; GPIO.setup(GPIO_butA, GPIO.IN, pull_up_down = GPIO.PUD_UP) 	# Pin 37
GPIO_butB = 6;  GPIO.setup(GPIO_butB, GPIO.IN, pull_up_down = GPIO.PUD_UP)	# Pin 31

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


def set_volume(value, counterClockwise):
    """ Checks value, formats, sets volume of volumio by writing to API """
#    print('triggerVolumeChange called with "%s" and "%s"' % (counterClockwise, value))
#    logging.info('triggerVolumeChange called with "%s" and "%s"' % (counterClockwise, value))
    newVolume = currentVolume - value if counterClockwise else currentVolume + value
    if newVolume < 0:
        newVolume = 0
    if newVolume > 100:
        newVolume = 100
    result = subprocess.getoutput('/usr/bin/curl -s 0 "http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=%s"' % str(newVolume))
    if counterClockwise:
        print("  -" + str(value))
        logging.info("  -" + str(value))
    else:
        print("  +" + str(value))
        logging.info("  +" + str(value))
    print("Volume set to " + str(newVolume))
    logging.info("Volume set to " + str(newVolume))
    return newVolume
#    if not result:
#        return False
#    jsonResult = json.loads(result)
 #   return True if jsonResult['response'] == 'volume Success' else False



# status, position, albumart, uri, trackType, seek, samplerate, bitdepth, channels, random, 
#	repeat, repeatSingle, consume, volume, disableVolumeControl, mute, stream, updatedb, volatile, service
def get_status(value):
    """ Get status category, by writing to API, sort and return """
    result = subprocess.getoutput('/usr/bin/curl -s 0 http://127.0.0.1:3000/api/v1/getstate')
    if not result:
        return False
    jsonResult = json.loads(result)
    singleResult =  jsonResult[value]
    return singleResult if singleResult else False


def switch_event(event):
    """ Triggered for each events. Counts seconds from first to last event, calls function when 1 second has changed from first to last event """
    global eventsList, currentVolume
    if event == RotaryEncoder.CLOCKWISE:
        eventsList.append(time.time())
        if eventsList[-1] - eventsList[0] >= 1:
            currentVolume = set_volume(len(eventsList), False)
            eventsList = []
    #        print(currentVolume)
#        logging.info("Clockwise")
#        print("Clockwise")
    elif event == RotaryEncoder.ANTICLOCKWISE:
        eventsList.append(time.time())
        if eventsList[-1] - eventsList[0] >= 0.3:
            currentVolume = set_volume(len(eventsList), True)
            eventsList = []
    #        print(currentVolume)
#        logging.info("Anticlockwise")
#        print("Anticlockwise")
    elif event == RotaryEncoder.BUTTONDOWN:
        play_control('toggle')
        logging.info('Toggled stop/play')
        print("Start/Stop Button pressed")
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
set_volume(0, True)
logging.info('Volume was set to ' + str(currentVolume))
subprocess.Popen("amixer -c 2 cset numid=1 100", stdout=subprocess.PIPE, shell=True).stdout.read()
play_control('play')

# Define rotary switch
rswitch = RotaryEncoder(GPIO_clk, GPIO_dt, GPIO_play, switch_event)
logging.info("Started " + str(rswitch))

# Listen continually
while True:
    if GPIO.input(GPIO_butA) == GPIO.LOW:
        logging.info('Button A was pressed!')
        print('Button A was pressed!')
    if GPIO.input(GPIO_butB) == GPIO.LOW:
        logging.info('Button B was pressed!')
        print('Button B was pressed!')
    time.sleep(0.5)









# --- Notes ---------------------------------------------------------------------------

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
