#!/usr/bin/python3
import json
import time
import socket
import logging
import subprocess
import RPi.GPIO as GPIO
from time import sleep

# --- Variables -----------------------------------------------------------------------


# --- Class / Def ---------------------------------------------------------------------
masterVolume = 30


subprocess.Popen("amixer -c 2 cset numid=1 %s" % (masterVolume), stdout=subprocess.PIPE, shell=True).stdout.read()

reply = subprocess.Popen("amixer -c 2 cset numid=1", stdout=subprocess.PIPE, shell=True).stdout.read()
strReply = reply.decode('ascii')
r = strReply.split('\n')
curVolume = int(r[2].split(',')[1])


print(curVolume)


