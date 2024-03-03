#!/usr/bin/python3
import json
import time
import socket
import logging
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
clkLastState = GPIO.input(GPIO_clk)

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


# --- Main ----------------------------------------------------------------------------

# setup logging
logging.basicConfig(filename='/var/log/readGPIO.log', encoding='utf-8', format='%(asctime)s %(message)s', level=logging.DEBUG)
logging.info('init')

# wait for port 3000 to respond
while not is_port_in_use(3000):
    time.sleep(1)

# contact API to start up radio
set_volume(60)
subprocess.Popen("amixer -c 2 cset numid=1 100", stdout=subprocess.PIPE, shell=True).stdout.read()
masterVolume = 100
play_control('play')

while True:
    clkState = GPIO.input(GPIO_clk)
    dtState = GPIO.input(GPIO_dt)
    if clkState != clkLastState:
        logging.info('Click detected!')
        if dtState != clkState:
            # turn up
            logging.info('   UP')
            if masterVolume < 170:
                masterVolume += 5
                subprocess.Popen("amixer -c 2 cset numid=1 %s" % (masterVolume), stdout=subprocess.PIPE, shell=True).stdout.read()
                logging.info('Volume up to ' + str(masterVolume))
        else:
            # turn down
            logging.info('   DOWN')
            if masterVolume >= 100:
                masterVolume -= 5
                subprocess.Popen("amixer -c 2 cset numid=1 %s" % (masterVolume), stdout=subprocess.PIPE, shell=True).stdout.read()
                logging.info('Volume down to ' + str(masterVolume))
        clkLastState = clkState
    if GPIO.input(GPIO_mute) == GPIO.LOW:
        play_control('toggle')
        logging.info('Toggled mute/play')
        sleep(1)
    if GPIO.input(GPIO_butA) == GPIO.LOW:
        logging.info('Button A was pressed!')
    if GPIO.input(GPIO_butB) == GPIO.LOW:
        logging.info('Button B was pressed!')
logging.info('Program terminated')
GPIO.cleanup()

 	 	
