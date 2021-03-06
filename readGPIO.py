#!/usr/bin/python3
import json
import time
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------

GPIO.setmode(GPIO.BOARD)
# UNUSED	GPIO_volA  = 11; GPIO.setup(GPIO_volA,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
# UNUSED	GPIO_volB  = 18; GPIO.setup(GPIO_volB,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_mute	= 15; GPIO.setup(GPIO_mute,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_volUp	= 37; GPIO.setup(GPIO_volUp,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_volDown	= 31; GPIO.setup(GPIO_volDown,	GPIO.IN, pull_up_down = GPIO.PUD_UP)

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
    print('IN SETVOLUME: FIRST LINE')
    result = subprocess.getoutput('/usr/bin/curl -s 0 "http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=%s"' % str(value))
    print('IN SETVOLUME: result=', str(result))
    if not result: return False
    print('IN SETVOLUME: still here....')
    jsonResult = json.loads(result)
    print('IN SETVOLUME: returning jsonresult=', str(jsonResult))
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

# enter hardware loop
try:
    while True:
        if GPIO.input(GPIO_volUp) == GPIO.LOW:
            volume = get_status('volume')
            if volume < 40:
                volume += 2
                set_volume(volume)
                print('volume set to', str(volume))
        elif GPIO.input(GPIO_volDown) == GPIO.LOW:
            volume = get_status('volume')
            if volume >= 2:
                volume -= 2
                set_volume(volume)
                print('volume set to', str(volume))
        if GPIO.input(GPIO_mute) == GPIO.LOW:
            play_control('toggle')
            print('Toggled mute/play')
except:
   GPIO.cleanup()


# --- Notes ---------------------------------------------------------------------------

# [GPIO Pins]
#
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# | 02 | 04 | 06 | 08 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# | 01 | 03 | 05 | 07 | 09 | 11 | 13 | 15 | 17 | 19 | 21 | 23 | 25 | 27 | 29 | 31 | 33 | 35 | 37 | 39 |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
#


