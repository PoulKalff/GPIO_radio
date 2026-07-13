#!/usr/bin/python3
import sys
import json
import time
import socket
import logging
import subprocess
#import urllib.request
import http.client
from time import sleep
import RPi.GPIO as GPIO
from rotary_class import RotaryEncoder

# PREREQUISITES: '/var/log/readGPIO.log' must exist and be writeable
# 	Provide '--screen' as argument to get output to screen

# --- Variables -----------------------------------------------------------------------

counter = 0
lastTitle = ""
currentVolume = 35
currentTrack = "None"
currentlyPlaying = True
#radioStation = 'http://streamer.radio.co/s6a349b3a2/listen'
#radioStation = "https://play.rockantenne.de/heavy-metal.m3u"
eventsList = []

GPIO.setmode(GPIO.BCM)	# not necessary, already set in rotaryEncoder
GPIO_clk =  17  # Pin 11
GPIO_dt =   23  # Pin 16
GPIO_play = 22  # Pin 15
GPIO_butA = 6;	GPIO.setup(GPIO_butA, GPIO.IN, pull_up_down = GPIO.PUD_UP) 	# Pin 37
GPIO_butB = 26;	GPIO.setup(GPIO_butB, GPIO.IN, pull_up_down = GPIO.PUD_UP)	# Pin 31

# --- Class / Def ---------------------------------------------------------------------

class ToScreen():

    def __init__(self, activate):
        self.showOutput = activate

    def output(self, msg):
        cleanString = msg.encode('ascii', errors='replace').decode('ascii')
        if self.showOutput:
            print(cleanString)


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
    if type(result) != str:
        return False
    jsonResult = json.loads(result)
    if value in jsonResult:
        singleResult = jsonResult[value]
        return singleResult if singleResult else False
    else:
        return result


def switch_event(event):
    """ Triggered for each events. Counts seconds from first to last event, calls function when 1 second has changed from first to last event """
    global eventsList, currentVolume, currentlyPlaying
    if event == RotaryEncoder.CLOCKWISE:
        eventsList.append([0, time.time()])
    elif event == RotaryEncoder.ANTICLOCKWISE:
        eventsList.append([1, time.time()])
    elif event == RotaryEncoder.BUTTONDOWN:
        play_control('toggle')
        logging.info('Toggled stop/play')
        OutputToScreen.output("Toggled STOP/START")
        sleep(1)
        currentlyPlaying = True if get_status("status") == "play" else False
    return


def showTitle():
    global lastTitle
    try:
        # Opret forbindelse til API'et
        conn = http.client.HTTPSConnection("public.radio.co")
        conn.request("GET", "/api/v2/s6a349b3a2/track/current")
        response = conn.getresponse()

        if response.status == 200:
            data = response.read().decode('utf-8')
            info = json.loads(data)
            jsonData = info["data"]
            currentTitle = jsonData['title']
            # Opdater kun skærmen, hvis sangen er skiftet
            if currentTitle != lastTitle or lastTitle == "":
                OutputToScreen.output("Now playing:     " + str(currentTitle))
                lastTitle = currentTitle
        else:
            print("Could not get data. HTTP Status:", response.status)
        conn.close()

    except Exception as e:
        # Håndterer netværksfejl uden at stoppe programmet
        print("Unknown Exception:", e)


def restart_computer():
    """Restart the computer immediately on Windows"""
    try:
        subprocess.call(["reboot", "0"])
        print("Computer restart initiated...")
    except Exception as e:
        print("Error: {e}")


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


# Display track at init
showTitle()


# Listen continually
while True:
    counter += 1
    if counter == 250000:
        counter = 0
        if currentlyPlaying:
            showTitle()
    if GPIO.input(GPIO_butA) == GPIO.LOW:
        logging.info('Button A was pressed')
        OutputToScreen.output("Selecting previous track in playlist")
        play_control('prev')
        sleep(3)
        track = get_status("artist")
        OutputToScreen.output("Now playing:" + str(track))
        showTitle()
    if GPIO.input(GPIO_butB) == GPIO.LOW:
        logging.info('Button B was pressed')
        OutputToScreen.output("Selecting next track in playlist")
        play_control('next')
        sleep(3)
        track = get_status("artist")
        OutputToScreen.output("Now playing:" + str(track))
        showTitle()
    if len(eventsList) > 0:	# if rotary encoder event has added anything to the event list
        if time.time() - eventsList[0][1] >= 0.2:	# if the first event is more than 0.2 seconds old (check to avoid repeated calls to API)
            currentVolume = set_volume(len(eventsList), eventsList[0][0])	# call API
            OutputToScreen.output("[" + "*" * int((currentVolume / 2)) + " " * (50 - int(currentVolume / 2)) + "] " + str(currentVolume) + "%")
            eventsList = []	# reset list


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
