#!/usr/bin/python3

import RPi.GPIO as GPIO
import time
import collections
from flask import Flask, json

# Define GPIO pins
START_STOP = 20
SPEED_UP = 21
SPEED_DOWN = 16
SPEED_SENSOR = 4

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(START_STOP, GPIO.OUT)
GPIO.setup(SPEED_UP, GPIO.OUT)
GPIO.setup(SPEED_DOWN, GPIO.OUT)
GPIO.setup(SPEED_SENSOR, GPIO.IN,  pull_up_down = GPIO.PUD_DOWN)

# Set outputs down to start with
GPIO.output(START_STOP, 0)
GPIO.output(SPEED_UP, 0)
GPIO.output(SPEED_DOWN, 0)

# Storage for the latest timestamps from the speed sensor
stack = collections.deque(maxlen=5)

# callback method used when speed sensor pin rises
def speed_sensor_rising(channel):
  stack.appendleft(time.time())

# simulate button press by putting current through pin for x seconds
def press(pin_no):
  # print("press: " + str(pin_no))
  PRESS_TIME = 1
  GPIO.output(pin_no, 1)
  time.sleep(PRESS_TIME)
  GPIO.output(pin_no, 0)

# return current shaker speed
# calculates time between last two readings from speed sensor
def get_speed():
  current = time.time()

  # if less than 2 edges or oldest edge is more than 2 sec old
  # ten return zero speed 
  if len(stack) < 2 or stack[1] + 2 < current:
    rpm = 0
  else:
    diff = stack[0] - stack[1]
    rpm = 60.0 / diff

  return rpm

# define callback when a HIGH signal is detected
GPIO.add_event_detect(SPEED_SENSOR, GPIO.RISING, callback=speed_sensor_rising)

# define restserver and api
api = Flask(__name__)

@api.route('/speed', methods=['GET'])
def speed():
  result = [{"speed": get_speed()}]
  return json.dumps(result)

@api.route('/press_on_off', methods=['GET'])
def press_on_off():
  press(START_STOP)
  result = [{"press": "OK"}]
  return json.dumps(result)

if __name__ == '__main__':
    api.run()