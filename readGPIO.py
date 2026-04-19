#!/usr/bin/python3
import sys
import json
import time
import socket
import logging
import subprocess
import urllib.request
from time import sleep
import RPi.GPIO as GPIO
from rotary_class import RotaryEncoder

# PREREQUISITES: '/var/log/readGPIO.log' must exist and be writeable
# 	Provide '--screen' as argument to get output to screen

# --- Variables -----------------------------------------------------------------------

counter = 0
currentVolume = 35
currentTrack = "None"
eventsList = []

GPIO.setmode(GPIO.BCM)	# not necessary, already set in rotaryEncoder
GPIO_clk =  17  # Pin 11
GPIO_dt =   23  # Pin 16
GPIO_play = 22  # Pin 15
GPIO_butA = 26; GPIO.setup(GPIO_butA, GPIO.IN, pull_up_down = GPIO.PUD_UP) 	# Pin 37
GPIO_butB = 6;  GPIO.setup(GPIO_butB, GPIO.IN, pull_up_down = GPIO.PUD_UP)	# Pin 31

# --- Class / Def ---------------------------------------------------------------------

class ToScreen():

    def __init__(self, activate):
        self.showOutput = activate

    def output(self, msg):
        if self.showOutput:
            print(msg)


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
    newVolume = currentVolume - value if counterClockwise else currentVolume + value
    if newVolume < 0:
        newVolume = 0
    if newVolume > 100:
        newVolume = 100
    result = subprocess.getoutput('/usr/bin/curl -s 0 "http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=%s"' % str(newVolume))
    logging.info('set_volume() called with "%s%s". Volume is now "%s"' % ("-" if counterClockwise else "+", value, str(newVolume)))
    return newVolume


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
        eventsList.append([0, time.time()])
    elif event == RotaryEncoder.ANTICLOCKWISE:
        eventsList.append([1, time.time()])
    elif event == RotaryEncoder.BUTTONDOWN:
        play_control('toggle')
        logging.info('Toggled stop/play')
        OutputToScreen.output("Toggled STOP/START")
        sleep(1)
    return


def getTitle():
    request = urllib.request.Request('http://streamer.radio.co/s6a349b3a2/listen', headers={'Icy-MetaData' : 1})
    response = urllib.request.urlopen(request)
    icy_metaint_header = response.headers.get('icy-metaint')
    if icy_metaint_header is not None:
        metaint = int(icy_metaint_header)
        read_buffer = metaint+255
        content = response.read(read_buffer)
        content_str = ""
        for _byte in content:
            content_str += chr(int(_byte))
        stream_title_pos = content_str.find("StreamTitle=")
        post_title_content = content_str[stream_title_pos+13:]
        semicolon_pos = post_title_content.find(';')
        title = post_title_content[:semicolon_pos-1]
    return title


# --- Main ----------------------------------------------------------------------------

# very simple check if user want output to screen
activateScreen = True if len(sys.argv) > 1 and sys.argv[1] == "--screen" else False
OutputToScreen = ToScreen(activateScreen)


# setup logging
logging.basicConfig(filename='/var/log/readGPIO.log', encoding='utf-8', format='%(asctime)s %(message)s', level=logging.DEBUG)
OutputToScreen.output("Program starting up...")
logging.info('init')


# wait for port 3000 to respond
while not is_port_in_use(3000):
    time.sleep(1)


# contact API to start up radio, set amixer to 100
set_volume(0, True)
subprocess.Popen("amixer -c 2 cset numid=1 100", stdout=subprocess.PIPE, shell=True).stdout.read()
play_control('play')
OutputToScreen.output("Control set to PLAY")


# Define rotary switch
rswitch = RotaryEncoder(GPIO_clk, GPIO_dt, GPIO_play, switch_event)
logging.info("Started " + str(rswitch))


# read initalt metadata
title = getTitle()
OutputToScreen.output(title)


# Listen continually
while True:
    counter += 1
    if GPIO.input(GPIO_butA) == GPIO.LOW:
        logging.info('Button A was pressed!')
        OutputToScreen.output("Button A pressed")
        sleep(1)
    if GPIO.input(GPIO_butB) == GPIO.LOW:
        logging.info('Button B was pressed!')
        OutputToScreen.output("Button B pressed")
        sleep(1)
    if len(eventsList) > 0:	# if rotary encoder event has added anything to the event list
        if time.time() - eventsList[0][1] >= 0.2:	# if the first event is more than 0.2 seconds old (check to avoid repeated calls to API)
            currentVolume = set_volume(len(eventsList), eventsList[0][0])	# call API
#            OutputToScreen.output("Volume DOWN" if eventsList[0][0] else "Volume UP" + " by " + str(len(eventsList)) + ". Volume is now " + str(currentVolume))
            OutputToScreen.output("[" + "*" * int((currentVolume / 2)) + " " * (50 - int(currentVolume / 2)) + "] " + str(currentVolume) + "%")
            eventsList = []	# reset list
    # TESTING ------------------------------------------------------------
    if counter == 500000:		# read metadate regulary, but not continuously
        title = getTitle()
        if title != currentTrack:
            OutputToScreen.output("Now playing : " + title)
            currentTrack = title
        counter = 0
    # TESTING ------------------------------------------------------------




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
