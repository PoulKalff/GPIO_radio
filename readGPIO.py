#!/usr/bin/python3
import json
import time
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------

GPIO.setmode(GPIO.BOARD)
GPIO_next     = 31; GPIO.setup(GPIO_next,	GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO_previous = 37; GPIO.setup(GPIO_previous,	GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO_mute     = 11; GPIO.setup(GPIO_mute,	GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO_volUp    = 15; GPIO.setup(GPIO_volUp,	GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO_volDown  = 18; GPIO.setup(GPIO_volDown,	GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# --- Def -----------------------------------------------------------------------------

def is_port_in_use(port):
    """ Check if port is up """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        status = s.connect_ex(('localhost', port)) == 0
        return status


def play_control(value):	# play, toggle, pause, next, prev, stop, clearQueue
    """ Start playing, by writing to API """
    result = subprocess.getoutput('/usr/bin/curl -s 0 http://127.0.0.1:3000/api/v1/commands/?cmd=%s' % value)
    if not result: return False
    jsonResult = json.loads(result)
    return True if jsonResult['response'] == value + ' Success' else False


def set_volume(value):		# 0 - 100
    """ Set volume, by writing to API """
    result = subprocess.getoutput('/usr/bin/curl -s 0 "http://127.0.0.1:3000/api/v1/commands/?cmd=volume&volume=%s"' % value)
    print(str(result))
    if not result: return False
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
print( set_volume(28) )
play_control('play')

# enter hardware testing loop
try:
    while not True:												## <--------------- REMOVE "NOT" !
        if GPIO_next:
            play_control('next')
        elif GPIO_previous:
            play_control('prev')
        elif GPIO_mute:
            play_control('toggle')
        elif GPIO_volUp:
            volume = int(get_status('volume'))
            if volume < 50:
                set_volume( volume + 1 )
        elif GPIO_voldown:
            volume = int(get_status('volume'))
            if volume > 0:
                set_volume( volume - 1 )
except:
   GPIO.cleanup()



# --- Notes ---------------------------------------------------------------------------

# [GPIO Pins]
#                                                                                  Grnd
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# | 02 | 04 | 06 | 08 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# | 01 | 03 | 05 | 07 | 09 | 11 | 13 | 15 | 17 | 19 | 21 | 23 | 25 | 27 | 29 | 31 | 33 | 35 | 37 | 39 |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
#                                                                             Next           Prev


