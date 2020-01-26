#!/usr/bin/python3
import json
import time
import socket
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------

GPIO.setmode(GPIO.BOARD)
GPIO_volA  = 11; GPIO.setup(GPIO_volA,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_mute  = 15; GPIO.setup(GPIO_mute,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_volB  = 18; GPIO.setup(GPIO_volB,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_next  = 31; GPIO.setup(GPIO_next,	GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO_prev  = 37; GPIO.setup(GPIO_prev,	GPIO.IN, pull_up_down = GPIO.PUD_UP)

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
set_volume(28)
play_control('play')

# enter hardware testing loop
try:
    while True:
        if GPIO.input(GPIO_next) == GPIO.LOW:
            play_control('next')
        elif GPIO.input(GPIO_prev) == GPIO.LOW:
            play_control('prev')
        elif GPIO.input(GPIO_mute) == GPIO.LOW:
            play_control('toggle')
            print('MUTE pressed, reading stopped')
            import sys
            sys.exit('Goodbye')



        elif GPIO.input(GPIO_volA) == GPIO.LOW:
            pass
#            print('VOLUME CONTROL A was pressed!')
#            volume = int(get_status('volume'))
#            if volume < 50:
#                set_volume( volume + 1 )
        elif GPIO.input(GPIO_volB) == GPIO.LOW:
            pass
#            print('VOLUME CONTROL B was pressed!')
#            volume = int(get_status('volume'))
#            if volume > 0:
#                set_volume( volume - 1 )
#        print(GPIO.input(GPIO_volA), GPIO.input(GPIO_volB))
except:
   GPIO.cleanup()

#print('next', GPIO.input(GPIO_next) == GPIO.LOW, GPIO.input(GPIO_next))
#print('prev', GPIO.input(GPIO_prev) == GPIO.LOW, GPIO.input(GPIO_prev))
#print('mute', GPIO.input(GPIO_mute) == GPIO.LOW, GPIO.input(GPIO_mute))
#print('up',   GPIO.input(GPIO_volUp) == GPIO.LOW, GPIO.input(GPIO_volUp))
#print('down', GPIO.input(GPIO_volDown) == GPIO.LOW, GPIO.input(GPIO_volDown))



# --- Notes ---------------------------------------------------------------------------

# [GPIO Pins]
#            Grnd                          VolB                               Grnd
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# | 02 | 04 | 06 | 08 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
# | 01 | 03 | 05 | 07 | 09 | 11 | 13 | 15 | 17 | 19 | 21 | 23 | 25 | 27 | 29 | 31 | 33 | 35 | 37 | 39 |
# +----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+----+
#                           volA     Mute                                    Next           Prev


